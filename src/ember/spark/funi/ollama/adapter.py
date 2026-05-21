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
import uuid
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
from ember.schemas.tool import (
    ToolCall,
    ToolDescriptor,
    ToolParameterKind,
)

logger = logging.getLogger(__name__)


_DEFAULT_TIMEOUT_S = 60.0

# Sanity bound on a single NDJSON frame from Ollama's streaming
# endpoint. Legitimate frames carry one token batch plus a small JSON
# envelope (a few KiB at most, even with parsed tool_calls). A frame
# larger than this is a runaway server or a memory-exhaustion attack
# disguised as a streaming response. The streaming loop aborts with a
# typed ERROR chunk if it sees one.
_MAX_NDJSON_FRAME_BYTES = 1 * 1024 * 1024  # 1 MiB


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
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> FuniReply:
        """Send one turn through ``/api/chat`` and return the reply.

        Errors are folded into ``FuniReply(finish_reason=ERROR)`` rather
        than raised — see module docstring. ``tools`` (Phase 16 / ADR
        0011) become Ollama tool descriptors; ``message.tool_calls``
        in the response surfaces as :attr:`FuniReply.tool_calls`.
        """
        messages = _messages_from_context(context, prompt)
        request_body: dict[str, object] = {
            "model": self.model_id,
            "messages": messages,
            "stream": False,
            "options": self._options,
        }
        if tools:
            request_body["tools"] = [_descriptor_to_ollama_tool(d) for d in tools]
        payload = json.dumps(request_body).encode("utf-8")

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
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # OSError catches socket.timeout (which doesn't always surface
            # as URLError) and other low-level network exceptions that
            # bypass urllib's wrapping. TimeoutError is the modern
            # equivalent of socket.timeout in Python 3.10+.
            logger.debug("ollama complete: network error %s", exc)
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
        if not isinstance(message, dict):
            message = {}
        text = message.get("content")
        # Tool calls may arrive even when text is empty (model emits only a call).
        tool_calls = _parse_tool_calls(message.get("tool_calls"))
        if not isinstance(text, str):
            text = ""
        if not text and not tool_calls:
            return FuniReply(
                text="[ollama returned no message content]",
                finish_reason=FinishReason.ERROR,
                model_id=self.model_id,
            )

        # If Ollama yields tool_calls, force the finish reason — some
        # local models forget to set ``done_reason="tool_calls"`` even
        # when they emit a call.
        if tool_calls:
            finish = FinishReason.TOOL_CALL
        else:
            finish = _OLLAMA_DONE_REASON_TO_FINISH.get(
                str(parsed.get("done_reason") or "stop"), FinishReason.STOP
            )
        self._last_ok = _now_utc()
        return FuniReply(
            text=text,
            finish_reason=finish,
            tool_calls=tool_calls,
            model_id=str(parsed.get("model") or self.model_id),
            prompt_tokens=_safe_int(parsed.get("prompt_eval_count")),
            completion_tokens=_safe_int(parsed.get("eval_count")),
        )

    # --------------------------------------------------- complete_streaming

    def complete_streaming(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> Iterator[FuniStreamChunk]:
        """Stream a turn via ``/api/chat`` with ``stream=True``.

        Yields one :class:`FuniStreamChunk` per Ollama NDJSON line.
        Mid-stream errors fold into a final ERROR chunk per ADR 0009
        §2.4. ``tools`` (Phase 16 / ADR 0011) become Ollama tool
        descriptors; any ``message.tool_calls`` on the final chunk
        surface as :attr:`FuniStreamChunk.tool_calls`.
        """
        messages = _messages_from_context(context, prompt)
        request_body: dict[str, object] = {
            "model": self.model_id,
            "messages": messages,
            "stream": True,
            "options": self._options,
        }
        if tools:
            request_body["tools"] = [_descriptor_to_ollama_tool(d) for d in tools]
        payload = json.dumps(request_body).encode("utf-8")
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
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # OSError catches socket.timeout and other low-level network
            # exceptions that bypass urllib's URLError wrapping. The
            # streaming contract (ADR 0009 §2.4) requires a single final
            # ERROR chunk on open-time failure.
            logger.debug("ollama complete_streaming: network error %s", exc)
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
        # Ollama emits ``message.tool_calls`` on a non-``done`` line (the
        # frame before the final ``done:true`` summary). We accumulate
        # them across the stream so the consumer sees them all attached
        # to the final chunk — that's the contract documented in
        # ``schemas/stream.py`` and consumed by Munnr's tool loop.
        accumulated_tool_calls: list[ToolCall] = []
        seen_done = False
        try:
            for raw_line in response:
                # Defensive: cap individual NDJSON frame size so a
                # runaway server can't push us into a MemoryError mid-
                # stream. Anything beyond _MAX_NDJSON_FRAME_BYTES is
                # treated as an error chunk; the stream ends cleanly.
                if len(raw_line) > _MAX_NDJSON_FRAME_BYTES:
                    yield FuniStreamChunk(
                        text_delta=(
                            f"[ollama frame exceeded "
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

                raw_message = (parsed or {}).get("message")
                message = raw_message if isinstance(raw_message, dict) else {}
                text_delta = message.get("content") or ""
                this_chunks_tool_calls = _parse_tool_calls(message.get("tool_calls"))
                if this_chunks_tool_calls:
                    accumulated_tool_calls.extend(this_chunks_tool_calls)
                done = bool(parsed.get("done"))
                if done:
                    seen_done = True
                    final_calls = tuple(accumulated_tool_calls)
                    if final_calls:
                        finish = FinishReason.TOOL_CALL
                    else:
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
                        tool_calls=final_calls,
                    )
                    return
                yield FuniStreamChunk(
                    text_delta=text_delta,
                    done=False,
                    model_id=str(parsed.get("model") or self.model_id),
                )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
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
) -> list[dict[str, object]]:
    """Translate the runtime-neutral context items into Ollama messages.

    Strategy: keep system items as ``role="system"`` (Ollama supports
    multiple); episodes become alternating ``user``/``assistant`` pairs
    when they parse cleanly from our ``_episode_text`` shape; chunk
    hits become ``role="system"`` messages so they ground the model
    rather than appearing as conversation history.

    Phase 16 (ADR 0011) — ``ContextKind.TOOL_REPLY`` items are emitted
    as ``role="tool"`` messages with the originating tool's name in
    ``metadata["tool_name"]`` so the model can correlate the reply
    with the call it just made. If the operator added a turn after
    the tool reply (a follow-up loop), the operator_input is appended
    last as the standard ``role="user"``. Empty operator_input is
    omitted so the follow-up turn after a tool call is just
    ``tool`` → next reply.
    """
    messages: list[dict[str, object]] = []
    for item in context:
        if item.kind is ContextKind.SYSTEM or item.kind is ContextKind.CHUNK:
            messages.append({"role": "system", "content": item.text})
        elif item.kind is ContextKind.EPISODE:
            op, em = _split_episode(item.text)
            if op:
                messages.append({"role": "user", "content": op})
            if em:
                messages.append({"role": "assistant", "content": em})
        elif item.kind is ContextKind.TOOL_REPLY:
            messages.append(
                {
                    "role": "tool",
                    "content": item.text,
                    "name": str(item.metadata.get("tool_name", "tool")),
                }
            )
    if operator_input:
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


# --------------------------------------------------------------------- #
# Tool-use ↔ Ollama format (ADR 0011 Phase 16)                          #
# --------------------------------------------------------------------- #


_PARAM_KIND_TO_JSON_TYPE: dict[ToolParameterKind, str] = {
    ToolParameterKind.STRING: "string",
    ToolParameterKind.INTEGER: "integer",
    ToolParameterKind.FLOAT: "number",
    ToolParameterKind.BOOLEAN: "boolean",
    # PATH and URL are strings on the wire; the framework's
    # validate_arguments enforces the extra constraints when the call
    # comes back.
    ToolParameterKind.PATH: "string",
    ToolParameterKind.URL: "string",
}


def _descriptor_to_ollama_tool(descriptor: ToolDescriptor) -> dict[str, object]:
    """Convert an Ember :class:`ToolDescriptor` to Ollama's tool shape.

    Ollama's ``/api/chat`` ``tools`` field follows the OpenAI-style
    function-tool spec: ``{"type": "function", "function": {"name",
    "description", "parameters": {"type": "object", "properties":
    {...}, "required": [...]}}}``. Optional parameters with defaults
    are emitted as non-required.
    """
    properties: dict[str, object] = {}
    required: list[str] = []
    for name, param in descriptor.parameters_schema.items():
        prop: dict[str, object] = {
            "type": _PARAM_KIND_TO_JSON_TYPE.get(param.kind, "string"),
            "description": param.description,
        }
        if param.enum is not None:
            prop["enum"] = list(param.enum)
        properties[name] = prop
        if param.required and param.default is None:
            required.append(name)
    function_def: dict[str, object] = {
        "name": descriptor.name,
        "description": descriptor.description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }
    return {"type": "function", "function": function_def}


def _parse_tool_calls(raw: object) -> tuple[ToolCall, ...]:
    """Parse the ``message.tool_calls`` array out of an Ollama reply.

    The expected shape is a list of objects::

        {"function": {"name": "search_well", "arguments": {...}}}

    Ollama doesn't supply a call_id, so the adapter generates a UUID4
    per call. Malformed entries are skipped rather than raised — a
    tool that produced no parseable calls reads as ``finish_reason
    != TOOL_CALL`` to the consumer.
    """
    if not isinstance(raw, list):
        return ()
    out: list[ToolCall] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        function = entry.get("function") or entry
        if not isinstance(function, dict):
            continue
        name = function.get("name")
        if not isinstance(name, str) or not name:
            continue
        arguments = function.get("arguments")
        if isinstance(arguments, str):
            # Some Ollama builds emit the arg blob as a JSON string.
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}
        if not isinstance(arguments, dict):
            arguments = {}
        out.append(
            ToolCall(
                call_id=str(entry.get("id") or uuid.uuid4()),
                name=name,
                arguments=arguments,
            )
        )
    return tuple(out)


__all__ = ["OllamaFuni", "open"]
