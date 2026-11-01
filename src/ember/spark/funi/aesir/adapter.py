"""AesirFuni — Funi runtime adapter for Project Aesir's native service.

Binds Project Aesir under the E-022 backend contract. This adapter
speaks **only Aesir's native mode** — ``POST {base_url}/v1/generate``
on loopback (default ``127.0.0.1:18434``), authenticated with the
bearer key from the operator's key file. It deliberately does **not**
use Aesir's Ollama-compatible mode (``/api/chat`` on :11434): that
mode exists so Ollama clients can connect, and routing Ember through
it would hide which engine is actually answering. The native mode is
Aesir's own contract, and the binding states it as such.

What Aesir's native contract actually accepts (per the project's
API support matrix v1, the authority this adapter is judged against):

- ``POST /v1/generate`` with exactly: ``prompt``, ``system``,
  ``max_tokens``, ``timeout_ms``, ``temperature``, ``top_k``,
  ``top_p``, ``min_p``, ``repeat_penalty``, ``seed``, ``stream``.
  **No ``model`` field** (the service holds one resident model),
  **no ``messages``**, **no ``tools``**, no session/history — each
  admitted generation resets logical history, so Ember must send
  the conversation itself in the prompt on every turn (this adapter
  flattens context into ``prompt`` + ``system``; see
  :func:`_prompt_and_system_from_context`).
- ``GET /health/ready`` (schema v1): 200 with ``ready: true`` plus
  the resident model identity when healthy, 503 / ``ready: false``
  otherwise. Used as the open-time probe.
- ``stream: true`` returns NDJSON text records plus one counted
  terminal record; a stream ending without a terminal record is
  incomplete, never a success.
- Bodies are capped at 128 KiB server-side; a rejected request folds
  into a typed ``FuniReply(finish_reason=ERROR)``, never a raise,
  matching Ollama's failure semantics.

Failure semantics (same shape as the Ollama adapter):

- ``open()`` returns :class:`Unavailable` rather than raising: a
  missing/unreadable/malformed key file is ``CONFIG_INVALID``
  (the detail names the file path, never the key value); an
  unreachable endpoint is ``ENDPOINT_UNREACHABLE``; a rejected key
  (401/403) is ``CONFIG_INVALID``; a not-ready resident model (503
  or ``ready: false``) is ``NOT_LOADED``; a configured expected model
  that does not match the resident model is ``NOT_LOADED``.
- ``complete()`` always returns a :class:`FuniReply`. Runtime failure
  yields ``finish_reason=ERROR`` with an explanatory text.
  Tool descriptors are **refused, not dropped**: the native route
  rejects a ``tools`` field, so a turn carrying tools returns an
  ERROR reply naming that, rather than silently generating without
  the tools the caller expected.
- ``health()`` never raises.
- The key value is never logged, never put in an error detail, and
  never stored in config — config carries the key file's path only
  (E-013/E-020's reference-not-value shape).

What this adapter does NOT claim (the Aesir ledger respected):

- Nothing about which accelerator executed a turn: the server's
  ``backend`` field (e.g. ``cuda``) is the server's own report,
  passed through nowhere as an Ember claim. This binding is a text
  client; it does not certify a Hailo-10H text path, a GPU model,
  or any particular model — only the resident model the readiness
  probe actually names.
- No streaming-tool or multi-turn-session semantics: Aesir's native
  route has neither, and this adapter invents none.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import re
import stat
import urllib.error
import urllib.request
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.config import FuniConfig, FuniRuntime
from ember.schemas.funi import (
    BackendCapabilities,
    ContextItem,
    ContextKind,
    FinishReason,
    FuniHealth,
    FuniReply,
    StreamingMode,
    Unavailable,
    UnavailableReason,
)
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.tool import ToolDescriptor
from ember.spark.funi.determinism import determinism_error, effective_options

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_S = 60.0

# Same defensive bound as the Ollama adapter: a single NDJSON frame
# larger than this is a runaway server, not a token batch.
_MAX_NDJSON_FRAME_BYTES = 1 * 1024 * 1024  # 1 MiB

# Aesir key grammar (NATIVE_SERVICE): 32..256 letters, digits,
# hyphens or underscores, optionally followed by one newline.
_KEY_RE = re.compile(r"^[A-Za-z0-9_-]{32,256}$")


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


_AESIR_FINISH_TO_FINISH: dict[str, FinishReason] = {
    "eos": FinishReason.STOP,
    "stop": FinishReason.STOP,
    "length": FinishReason.LENGTH,
    # A generation deadline may return a partial answer with
    # finish_reason "timeout": a truncated reply, read as LENGTH.
    "timeout": FinishReason.LENGTH,
    "tool_calls": FinishReason.TOOL_CALL,
    "refused": FinishReason.REFUSED,
    "error": FinishReason.ERROR,
}


# E-023 capability truth for this backend, from the contract above:
# native NDJSON streaming; the native route accepts no tools at all,
# so tool_calls is False (not merely model-dependent); token counts
# reported from the response's prompt/generated counters; RAM use
# never reported (the readiness payload carries no RAM figure);
# the backend is reached over an HTTP endpoint (loopback by config
# default — locality is the config's, not the adapter's); every
# ContextKind has a defined translation in
# _prompt_and_system_from_context (TOOL_REPLY rides as prompt text,
# not as a tool-protocol return — there is no tool protocol here).
AESIR_CAPABILITIES = BackendCapabilities(
    runtime_kind="aesir",
    streaming=StreamingMode.NATIVE,
    tool_calls=False,
    tool_calls_model_dependent=False,
    token_counts=True,
    reports_ram_use=False,
    requires_endpoint=True,
    context_kinds=tuple(ContextKind),
)


class AesirFuni:
    """Aesir-backed Funi adapter. Implements :class:`FuniHandle`."""

    runtime_kind: str = "aesir"
    capabilities: BackendCapabilities = AESIR_CAPABILITIES

    def __init__(
        self,
        *,
        base_url: str,
        model_id: str,
        api_key: str,
        options: dict[str, object],
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.model_id = model_id
        self._base_url = base_url.rstrip("/")
        # Held in memory only; never logged, never repr'd (no __repr__
        # is defined, and no detail string below interpolates it).
        self._api_key = api_key
        self._options = options
        self._timeout_s = timeout_s
        self._last_ok: datetime | None = None

    # ------------------------------------------------------------- open

    @classmethod
    def open(cls, config: FuniConfig) -> AesirFuni | Unavailable:
        if config.runtime is not FuniRuntime.AESIR:
            return Unavailable(
                reason=UnavailableReason.CONFIG_INVALID,
                detail=f"funi config is for {config.runtime.value}, not aesir",
            )
        aesir_cfg = config.aesir
        det_error = determinism_error(config)
        if det_error is not None:
            return Unavailable(
                reason=UnavailableReason.CONFIG_INVALID,
                detail=det_error,
            )
        key_path = Path(aesir_cfg.api_key_file).expanduser()
        # Custody law (E-093): a file that holds a credential must
        # be operator-only — exactly mode 0o600 on POSIX, the same
        # standard the Well resolver (ADR 0010 §2.5) enforces. A
        # more permissive mode is refused before the file is read,
        # with a pointer at the permission bits, never the key.
        if os.name == "posix":
            try:
                key_mode = stat.S_IMODE(key_path.stat().st_mode)
            except OSError:
                key_mode = None
            if key_mode is not None and key_mode != 0o600:
                return Unavailable(
                    reason=UnavailableReason.CONFIG_INVALID,
                    detail=(
                        f"aesir key file {key_path} has mode "
                        f"{key_mode:04o}; a credential file must be "
                        "exactly 0600 (chmod 600 it) — refused "
                        "under the E-093 custody law."
                    ),
                )
        try:
            raw_key = key_path.read_text(encoding="utf-8")
        except OSError as exc:
            return Unavailable(
                reason=UnavailableReason.CONFIG_INVALID,
                detail=(
                    f"aesir key file {key_path} cannot be read: {exc}. "
                    "Create it with Aesir's keygen (see E-023 doc)."
                ),
            )
        api_key = raw_key[:-1] if raw_key.endswith("\n") else raw_key
        if not _KEY_RE.fullmatch(api_key):
            # Malformed key material: say the file is bad, never show
            # any part of what was read.
            return Unavailable(
                reason=UnavailableReason.CONFIG_INVALID,
                detail=(
                    f"aesir key file {key_path} does not hold a valid "
                    "Aesir service key (32..256 letters, digits, "
                    "hyphens or underscores)."
                ),
            )
        options: dict[str, object] = effective_options(
            {
                "temperature": aesir_cfg.temperature,
                "top_p": aesir_cfg.top_p,
                "max_tokens": aesir_cfg.max_tokens,
            },
            config,
        )
        if aesir_cfg.timeout_ms is not None:
            options["timeout_ms"] = aesir_cfg.timeout_ms
        adapter = cls(
            base_url=aesir_cfg.base_url,
            model_id=aesir_cfg.model,
            api_key=api_key,
            options=options,
        )
        probe = adapter._probe_ready()
        if isinstance(probe, Unavailable):
            return probe
        resident_model = probe.get("model")
        if aesir_cfg.model and resident_model not in (None, aesir_cfg.model):
            return Unavailable(
                reason=UnavailableReason.NOT_LOADED,
                detail=(
                    f"aesir service reports resident model "
                    f"{resident_model!r}, not configured {aesir_cfg.model!r}"
                ),
            )
        if isinstance(resident_model, str) and resident_model:
            adapter.model_id = resident_model
        adapter._last_ok = _now_utc()
        return adapter

    # ------------------------------------------------------------- complete

    def complete(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> FuniReply:
        """Send one turn through ``POST /v1/generate`` (stream false).

        Errors fold into ``FuniReply(finish_reason=ERROR)`` rather
        than raising — see module docstring. Tool descriptors are
        refused outright: the native route rejects a ``tools``
        field, so pretending the turn ran without them would be a
        silent lie about what the caller asked for.
        """
        if tools:
            return FuniReply(
                text=(
                    "[aesir backend does not support tool calls: the "
                    "native /v1/generate route accepts no tools field]"
                ),
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
        prompt_text, system_text = _prompt_and_system_from_context(
            context, prompt
        )
        if not prompt_text:
            return FuniReply(
                text="[aesir requires a non-empty prompt]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
        request_body: dict[str, object] = {
            "prompt": prompt_text,
            "stream": False,
            "max_tokens": self._options["max_tokens"],
            "temperature": self._options["temperature"],
            "top_p": self._options["top_p"],
        }
        if system_text:
            request_body["system"] = system_text
        if "timeout_ms" in self._options:
            request_body["timeout_ms"] = self._options["timeout_ms"]
        if "seed" in self._options:
            # E-036 determinism mode: Aesir's native route accepts
            # a seed field (its API support matrix v1); present
            # only when the mode is on — never in a normal request.
            request_body["seed"] = self._options["seed"]
        payload = json.dumps(request_body).encode("utf-8")

        url = f"{self._base_url}/v1/generate"
        try:
            request = urllib.request.Request(
                url=url,
                data=payload,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
            with urllib.request.urlopen(
                request, timeout=self._timeout_s
            ) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            return _error_reply_from_http_error(exc, self.model_id)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.debug("aesir complete: network error %s", exc)
            return FuniReply(
                text=f"[aesir unreachable: {exc}]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            return FuniReply(
                text=f"[aesir returned non-JSON body: {exc}]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
        if not isinstance(parsed, dict):
            return FuniReply(
                text="[aesir returned a non-object body]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
        if parsed.get("error"):
            return FuniReply(
                text=f"[aesir error: {_error_text(parsed.get('error'))}]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
        text = parsed.get("text")
        if not isinstance(text, str) or not text:
            return FuniReply(
                text="[aesir returned no text]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
        self._last_ok = _now_utc()
        return FuniReply(
            text=text,
            finish_reason=_AESIR_FINISH_TO_FINISH.get(
                str(parsed.get("finish_reason") or "eos"), FinishReason.STOP
            ),
            model_id=str(parsed.get("model") or self.model_id),
            prompt_tokens=_safe_int(parsed.get("prompt_tokens")),
            completion_tokens=_safe_int(parsed.get("generated_tokens")),
        )

    # --------------------------------------------------- complete_streaming

    def complete_streaming(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> Iterator[FuniStreamChunk]:
        """Stream a turn via ``POST /v1/generate`` with ``stream=true``.

        Yields one :class:`FuniStreamChunk` per NDJSON text record;
        the terminal record carries the counts. Mid-stream errors
        fold into a final ERROR chunk. A stream that ends without a
        terminal record yields a final ERROR chunk — per Aesir's own
        contract, EOF without a terminal marker is incomplete, not a
        successful generation.
        """
        if tools:
            yield FuniStreamChunk(
                text_delta=(
                    "[aesir backend does not support tool calls: the "
                    "native /v1/generate route accepts no tools field]"
                ),
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return
        prompt_text, system_text = _prompt_and_system_from_context(
            context, prompt
        )
        if not prompt_text:
            yield FuniStreamChunk(
                text_delta="[aesir requires a non-empty prompt]",
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return
        request_body: dict[str, object] = {
            "prompt": prompt_text,
            "stream": True,
            "max_tokens": self._options["max_tokens"],
            "temperature": self._options["temperature"],
            "top_p": self._options["top_p"],
        }
        if system_text:
            request_body["system"] = system_text
        if "timeout_ms" in self._options:
            request_body["timeout_ms"] = self._options["timeout_ms"]
        if "seed" in self._options:
            request_body["seed"] = self._options["seed"]
        payload = json.dumps(request_body).encode("utf-8")
        url = f"{self._base_url}/v1/generate"

        try:
            request = urllib.request.Request(
                url=url,
                data=payload,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._api_key}",
                },
            )
            response = urllib.request.urlopen(
                request, timeout=self._timeout_s
            )
        except urllib.error.HTTPError as exc:
            reply = _error_reply_from_http_error(exc, self.model_id)
            yield FuniStreamChunk(
                text_delta=reply.text,
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.debug("aesir complete_streaming: network error %s", exc)
            yield FuniStreamChunk(
                text_delta=f"[aesir unreachable: {exc}]",
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return

        try:
            yield from self._iter_ndjson_chunks(response)
        finally:
            response.close()

    def _iter_ndjson_chunks(self, response) -> Iterator[FuniStreamChunk]:
        seen_done = False
        try:
            for raw_line in response:
                if len(raw_line) > _MAX_NDJSON_FRAME_BYTES:
                    yield FuniStreamChunk(
                        text_delta=(
                            f"[aesir frame exceeded "
                            f"{_MAX_NDJSON_FRAME_BYTES} bytes — aborting]"
                        ),
                        done=True,
                        finish_reason=FinishReason.ERROR,
                        model_id=self.model_id,
                    )
                    return
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError as exc:
                    yield FuniStreamChunk(
                        text_delta=f"[aesir returned non-JSON line: {exc}]",
                        done=True,
                        finish_reason=FinishReason.ERROR,
                        model_id=self.model_id,
                    )
                    return
                if not isinstance(parsed, dict):
                    yield FuniStreamChunk(
                        text_delta="[aesir returned a non-object line]",
                        done=True,
                        finish_reason=FinishReason.ERROR,
                        model_id=self.model_id,
                    )
                    return
                if parsed.get("error"):
                    yield FuniStreamChunk(
                        text_delta=(
                            f"[aesir error: {_error_text(parsed.get('error'))}]"
                        ),
                        done=True,
                        finish_reason=FinishReason.ERROR,
                        model_id=self.model_id,
                    )
                    return
                if parsed.get("done"):
                    seen_done = True
                    self._last_ok = _now_utc()
                    yield FuniStreamChunk(
                        text_delta=str(parsed.get("text") or ""),
                        done=True,
                        finish_reason=_AESIR_FINISH_TO_FINISH.get(
                            str(parsed.get("finish_reason") or "eos"),
                            FinishReason.STOP,
                        ),
                        model_id=str(parsed.get("model") or self.model_id),
                        prompt_tokens=_safe_int(parsed.get("prompt_tokens")),
                        completion_tokens=_safe_int(
                            parsed.get("generated_tokens")
                        ),
                    )
                    return
                yield FuniStreamChunk(
                    text_delta=str(parsed.get("text") or ""),
                    done=False,
                    model_id=str(parsed.get("model") or self.model_id),
                )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            yield FuniStreamChunk(
                text_delta=f"[aesir stream died: {exc}]",
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return

        if not seen_done:
            yield FuniStreamChunk(
                text_delta=(
                    "[aesir stream ended without a terminal record]"
                ),
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

    # ------------------------------------------------------------- health

    def health(self) -> FuniHealth:
        probe = self._probe_ready()
        if isinstance(probe, Unavailable):
            return FuniHealth(
                model_id=self.model_id,
                ram_use_bytes=None,
                last_ok=self._last_ok,
            )
        model = probe.get("model")
        if isinstance(model, str) and model:
            self.model_id = model
        return FuniHealth(
            model_id=self.model_id,
            ram_use_bytes=None,
            last_ok=_now_utc(),
        )

    def close(self) -> None:
        # No persistent connection to release; intentional no-op.
        return None

    # ------------------------------------------------------------- internals

    def _probe_ready(self) -> Unavailable | dict[str, object]:
        """GET /health/ready: 200+ready -> payload; else Unavailable."""
        url = f"{self._base_url}/health/ready"
        try:
            request = urllib.request.Request(
                url=url,
                method="GET",
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            with urllib.request.urlopen(
                request, timeout=self._timeout_s
            ) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                return Unavailable(
                    reason=UnavailableReason.CONFIG_INVALID,
                    detail=(
                        "aesir service rejected the bearer key "
                        f"(HTTP {exc.code}); re-run Aesir keygen and "
                        "point funi.aesir.api_key_file at the new file."
                    ),
                )
            if exc.code == 503:
                return Unavailable(
                    reason=UnavailableReason.NOT_LOADED,
                    detail="aesir service reports its model is not ready",
                )
            return Unavailable(
                reason=UnavailableReason.UNKNOWN,
                detail=f"aesir readiness probe returned HTTP {exc.code}",
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return Unavailable(
                reason=UnavailableReason.ENDPOINT_UNREACHABLE,
                detail=str(exc),
            )

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            return Unavailable(
                reason=UnavailableReason.UNKNOWN,
                detail=f"readiness endpoint returned non-JSON: {exc}",
            )
        if not isinstance(payload, dict):
            return Unavailable(
                reason=UnavailableReason.UNKNOWN,
                detail=(
                    "readiness endpoint returned "
                    f"{type(payload).__name__}, not an object"
                ),
            )
        if payload.get("ready") is not True:
            return Unavailable(
                reason=UnavailableReason.NOT_LOADED,
                detail="aesir service reports its model is not ready",
            )
        return payload


# --------------------------------------------------------------------- #
# Module-level open() for the registry                                  #
# --------------------------------------------------------------------- #


def open(config: FuniConfig) -> AesirFuni | Unavailable:
    return AesirFuni.open(config)


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _prompt_and_system_from_context(
    context: Sequence[ContextItem], operator_input: str
) -> tuple[str, str]:
    """Flatten runtime-neutral context into Aesir's two fields.

    The native route accepts exactly one ``system`` string and one
    ``prompt`` string. SYSTEM and SUMMARY items join (in order) into
    ``system``; everything else joins (in original order) into
    ``prompt`` ahead of the operator's current line. EPISODE items
    already carry their ``Past turn: / Operator: / Ember:`` shape
    from ``prompt.assemble``; CHUNK items carry their ``From <title>:``
    shape; TOOL_REPLY items are rendered as ``Tool result (<name>):``
    text — there is no tool protocol on this route, so the result's
    *content* is preserved as text and nothing pretends a tool round
    trip happened. Empty operator input is omitted; a turn whose
    prompt parts are all empty yields an empty prompt, which the
    caller reports as an ERROR reply (Aesir rejects empty prompts).
    """
    system_parts: list[str] = []
    prompt_parts: list[str] = []
    for item in context:
        if item.kind in (ContextKind.SYSTEM, ContextKind.SUMMARY):
            system_parts.append(item.text)
        elif item.kind is ContextKind.TOOL_REPLY:
            tool_name = str(item.metadata.get("tool_name", "tool"))
            prompt_parts.append(f"Tool result ({tool_name}):\n{item.text}")
        else:  # EPISODE, CHUNK, and any future text-bearing kind
            prompt_parts.append(item.text)
    if operator_input:
        prompt_parts.append(operator_input)
    return "\n\n".join(prompt_parts), "\n\n".join(system_parts)


def _error_text(error: object) -> str:
    """Render Aesir's native error shape without echoing secrets.

    Native errors are ``{"error": {"code": N, "message": "..."}}``;
    Ollama-mode errors are ``{"error": "..."}`` (this adapter never
    calls Ollama mode, but the helper tolerates both). Aesir's docs
    state error messages do not echo request data or key values.
    """
    if isinstance(error, dict):
        code = error.get("code")
        message = error.get("message")
        if message is not None:
            return f"{code}: {message}" if code is not None else str(message)
        return str(error)
    return str(error)


def _error_reply_from_http_error(
    exc: urllib.error.HTTPError, model_id: str
) -> FuniReply:
    """Map an HTTP failure on /v1/generate to an ERROR reply.

    The body, when parseable, carries Aesir's error shape; when it
    cannot be read, the status code alone is reported. The key is
    never in any of this text.
    """
    try:
        body = exc.read()
    except OSError:
        body = b""
    detail = f"HTTP {exc.code}"
    if body:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and parsed.get("error") is not None:
            detail = f"HTTP {exc.code}: {_error_text(parsed['error'])}"
    return FuniReply(
        text=f"[aesir error: {detail}]",
        finish_reason=FinishReason.ERROR,
        model_id=model_id,
    )


def _safe_int(value: object) -> int | None:
    if value is None:
        return None
    with contextlib.suppress(TypeError, ValueError):
        return int(value)  # type: ignore[arg-type]
    return None


__all__ = ["AESIR_CAPABILITIES", "AesirFuni", "open"]
