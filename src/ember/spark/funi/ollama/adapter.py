"""OllamaFuni — Funi runtime adapter for Ollama.

Calls ``POST {base_url}/api/chat`` for completions and ``GET
{base_url}/api/version`` as the open-time probe. Stdlib ``urllib`` only
— no ``httpx`` dependency, honouring the Vow of Smallness (same shape
as Smiðja's :class:`OllamaEmbedClient`).

Failure semantics:

- ``open()`` returns :class:`Unavailable` rather than raising on probe
  failure (endpoint unreachable, version response malformed, etc.).
- ``complete()`` always returns a :class:`FuniReply`. Runtime failure
  mid-call (timeout, OOM, malformed response) yields a reply with
  ``finish_reason=FinishReason.ERROR`` and an explanatory ``text``,
  rather than raising. Munnr's turn renderer surfaces this honestly.
- ``health()`` never raises; the same shape Strengr uses for the Well.
"""

from __future__ import annotations

import contextlib
import json
import logging
import urllib.error
import urllib.request
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime

from ember.schemas.config import FuniConfig, FuniRuntime
from ember.schemas.funi import (
    ContextItem,
    ContextKind,
    FinishReason,
    FuniHealth,
    FuniReply,
    Unavailable,
    UnavailableReason,
)
from ember.schemas.stream import FuniStreamChunk

logger = logging.getLogger(__name__)


_DEFAULT_TIMEOUT_S = 60.0


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


_OLLAMA_DONE_REASON_TO_FINISH: dict[str, FinishReason] = {
    "stop": FinishReason.STOP,
    "length": FinishReason.LENGTH,
    "load": FinishReason.ERROR,
    "tool_calls": FinishReason.TOOL_CALL,
}


class OllamaFuni:
    """Ollama-backed Funi adapter. Implements :class:`FuniHandle`."""

    runtime_kind: str = "ollama"

    def __init__(
        self,
        *,
        base_url: str,
        model_id: str,
        options: dict[str, object],
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.model_id = model_id
        self._base_url = base_url.rstrip("/")
        self._options = options
        self._timeout_s = timeout_s
        self._last_ok: datetime | None = None

    # ------------------------------------------------------------- open

    @classmethod
    def open(cls, config: FuniConfig) -> OllamaFuni | Unavailable:
        if config.runtime is not FuniRuntime.OLLAMA:
            return Unavailable(
                reason=UnavailableReason.CONFIG_INVALID,
                detail=f"funi config is for {config.runtime.value}, not ollama",
            )
        ollama_cfg = config.ollama
        options = {
            "temperature": ollama_cfg.temperature,
            "top_p": ollama_cfg.top_p,
            "num_predict": ollama_cfg.num_predict,
        }
        adapter = cls(
            base_url=ollama_cfg.base_url,
            model_id=ollama_cfg.model,
            options=options,
        )
        probe = adapter._probe_version()
        if isinstance(probe, Unavailable):
            return probe
        adapter._last_ok = _now_utc()
        return adapter

    # ------------------------------------------------------------- complete

    def complete(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[str] | None = None,
    ) -> FuniReply:
        """Send one turn through ``/api/chat`` and return the reply.

        Errors are folded into ``FuniReply(finish_reason=ERROR)`` rather
        than raised — see module docstring.
        """
        if tools:
            # Tool use is reserved for a later slice; refuse cleanly.
            return FuniReply(
                text="",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        messages = _messages_from_context(context, prompt)
        payload = json.dumps(
            {
                "model": self.model_id,
                "messages": messages,
                "stream": False,
                "options": self._options,
            }
        ).encode("utf-8")

        url = f"{self._base_url}/api/chat"
        try:
            request = urllib.request.Request(
                url=url,
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(
                request, timeout=self._timeout_s
            ) as response:
                body = response.read()
        except urllib.error.URLError as exc:
            logger.debug("ollama complete: URL error %s", exc)
            return FuniReply(
                text=f"[ollama unreachable: {exc}]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            return FuniReply(
                text=f"[ollama returned non-JSON body: {exc}]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        if isinstance(parsed, dict) and parsed.get("error"):
            return FuniReply(
                text=f"[ollama error: {parsed['error']}]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        message = (parsed or {}).get("message") or {}
        text = message.get("content") if isinstance(message, dict) else None
        if not isinstance(text, str):
            return FuniReply(
                text="[ollama returned no message content]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        finish = _OLLAMA_DONE_REASON_TO_FINISH.get(
            str(parsed.get("done_reason") or "stop"), FinishReason.STOP
        )
        self._last_ok = _now_utc()
        return FuniReply(
            text=text,
            finish_reason=finish,
            model_id=str(parsed.get("model") or self.model_id),
            prompt_tokens=_safe_int(parsed.get("prompt_eval_count")),
            completion_tokens=_safe_int(parsed.get("eval_count")),
        )

    # --------------------------------------------------- complete_streaming

    def complete_streaming(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[str] | None = None,
    ) -> Iterator[FuniStreamChunk]:
        """Stream a turn via ``/api/chat`` with ``stream=True``.

        Yields one :class:`FuniStreamChunk` per Ollama NDJSON line.
        Mid-stream errors fold into a final ERROR chunk per ADR 0009
        §2.4. Tool requests refuse immediately per §2.5.
        """
        if tools:
            yield FuniStreamChunk(
                text_delta="",
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return

        messages = _messages_from_context(context, prompt)
        payload = json.dumps(
            {
                "model": self.model_id,
                "messages": messages,
                "stream": True,
                "options": self._options,
            }
        ).encode("utf-8")
        url = f"{self._base_url}/api/chat"

        try:
            request = urllib.request.Request(
                url=url,
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            response = urllib.request.urlopen(
                request, timeout=self._timeout_s
            )
        except urllib.error.URLError as exc:
            logger.debug("ollama complete_streaming: URL error %s", exc)
            yield FuniStreamChunk(
                text_delta=f"[ollama unreachable: {exc}]",
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
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError as exc:
                    yield FuniStreamChunk(
                        text_delta=f"[ollama returned non-JSON line: {exc}]",
                        done=True,
                        finish_reason=FinishReason.ERROR,
                        model_id=self.model_id,
                    )
                    return

                if isinstance(parsed, dict) and parsed.get("error"):
                    yield FuniStreamChunk(
                        text_delta=f"[ollama error: {parsed['error']}]",
                        done=True,
                        finish_reason=FinishReason.ERROR,
                        model_id=self.model_id,
                    )
                    return

                message = (parsed or {}).get("message") or {}
                text_delta = (
                    message.get("content") if isinstance(message, dict) else ""
                ) or ""
                done = bool(parsed.get("done"))
                if done:
                    seen_done = True
                    finish = _OLLAMA_DONE_REASON_TO_FINISH.get(
                        str(parsed.get("done_reason") or "stop"),
                        FinishReason.STOP,
                    )
                    self._last_ok = _now_utc()
                    yield FuniStreamChunk(
                        text_delta=text_delta,
                        done=True,
                        finish_reason=finish,
                        model_id=str(parsed.get("model") or self.model_id),
                        prompt_tokens=_safe_int(parsed.get("prompt_eval_count")),
                        completion_tokens=_safe_int(parsed.get("eval_count")),
                    )
                    return
                yield FuniStreamChunk(
                    text_delta=text_delta,
                    done=False,
                    model_id=str(parsed.get("model") or self.model_id),
                )
        except urllib.error.URLError as exc:
            yield FuniStreamChunk(
                text_delta=f"[ollama stream died: {exc}]",
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )
            return

        if not seen_done:
            yield FuniStreamChunk(
                text_delta="[ollama stream ended without done=true]",
                done=True,
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

    # ------------------------------------------------------------- health

    def health(self) -> FuniHealth:
        probe = self._probe_version()
        if isinstance(probe, Unavailable):
            return FuniHealth(
                model_id=self.model_id,
                ram_use_bytes=None,
                last_ok=self._last_ok,
            )
        return FuniHealth(
            model_id=self.model_id,
            ram_use_bytes=None,
            last_ok=_now_utc(),
        )

    def close(self) -> None:
        # No persistent connection to release; intentional no-op.
        return None

    # ------------------------------------------------------------- internals

    def _probe_version(self) -> Unavailable | dict[str, object]:
        url = f"{self._base_url}/api/version"
        try:
            request = urllib.request.Request(url=url, method="GET")
            with urllib.request.urlopen(
                request, timeout=self._timeout_s
            ) as response:
                body = response.read()
        except urllib.error.URLError as exc:
            return Unavailable(
                reason=UnavailableReason.ENDPOINT_UNREACHABLE,
                detail=str(exc),
            )

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            return Unavailable(
                reason=UnavailableReason.UNKNOWN,
                detail=f"version endpoint returned non-JSON: {exc}",
            )
        if not isinstance(payload, dict):
            return Unavailable(
                reason=UnavailableReason.UNKNOWN,
                detail=f"version endpoint returned {type(payload).__name__}",
            )
        return payload


# --------------------------------------------------------------------- #
# Module-level open() for the registry                                  #
# --------------------------------------------------------------------- #


def open(config: FuniConfig) -> OllamaFuni | Unavailable:
    return OllamaFuni.open(config)


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _messages_from_context(
    context: Sequence[ContextItem], operator_input: str
) -> list[dict[str, str]]:
    """Translate the runtime-neutral context items into Ollama messages.

    Strategy: keep system items as ``role="system"`` (Ollama supports
    multiple); episodes become alternating ``user``/``assistant`` pairs
    when they parse cleanly from our ``_episode_text`` shape; chunk
    hits become ``role="system"`` messages so they ground the model
    rather than appearing as conversation history. Finally, the
    operator's current input is a ``role="user"`` message.
    """
    messages: list[dict[str, str]] = []
    for item in context:
        if item.kind is ContextKind.SYSTEM or item.kind is ContextKind.CHUNK:
            messages.append({"role": "system", "content": item.text})
        elif item.kind is ContextKind.EPISODE:
            op, em = _split_episode(item.text)
            if op:
                messages.append({"role": "user", "content": op})
            if em:
                messages.append({"role": "assistant", "content": em})
    messages.append({"role": "user", "content": operator_input})
    return messages


_OPERATOR_LABEL = "Operator: "
_EMBER_LABEL = "Ember: "


def _split_episode(text: str) -> tuple[str, str]:
    """Split the canonical episode text shape into (operator, ember).

    The shape comes from ``prompt._episode_text``; this is a *graceful*
    parser — if the shape doesn't match (because the caller built the
    ContextItem themselves), we return ``("", "")`` so the whole item
    is dropped rather than corrupting the conversation history.
    """
    lines = text.splitlines()
    op_line = next((ln for ln in lines if ln.startswith(_OPERATOR_LABEL)), "")
    em_line = next((ln for ln in lines if ln.startswith(_EMBER_LABEL)), "")
    return (
        op_line[len(_OPERATOR_LABEL) :].strip(),
        em_line[len(_EMBER_LABEL) :].strip(),
    )


def _safe_int(value: object) -> int | None:
    if value is None:
        return None
    with contextlib.suppress(TypeError, ValueError):
        return int(value)  # type: ignore[arg-type]
    return None


__all__ = ["OllamaFuni", "open"]
