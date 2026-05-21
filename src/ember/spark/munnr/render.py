"""Terminal rendering helpers for Munnr.

All output formatting lives here so chat/ask/ingest/doctor/status can
stay router-thin per ``docs/architecture/DOMAIN_MAP.md`` §7.

The most load-bearing helper is :func:`render_well_disconnected_banner`
— the Vow of Graceful Offline says every ungrounded reply *must* be
visibly tagged, and this is where that tag is built.

Phase 11 (ADR 0009 part 2) added the streaming-render helpers
(:func:`render_stream_chunk`, :func:`stream_finish_tag`,
:func:`render_citations`) so chat.py can drive a live token loop while
keeping all formatting inside this module.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence

from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.errors import Disconnected
from ember.schemas.funi import FinishReason, FuniHealth, FuniReply
from ember.schemas.ingest import IngestSummary
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.thread import StrengrHealth
from ember.schemas.tool import (
    ApprovalOutcome,
    ToolCall,
    ToolDescriptor,
    ToolReply,
)

INTERRUPTED_TAG = "[interrupted by operator]"
TOOL_OUTPUT_PREVIEW_BYTES = 2 * 1024  # 2 KiB shown on stdout; full text persisted in audit

# ANSI / CSI / OSC escape-sequence pattern. Tools return strings that
# may include attacker-controllable bytes (HTTP response bodies, file
# contents, model output that quoted a malicious source). Without
# scrubbing, a reply.error or reply.output containing ``\x1b[2J`` could
# clear the operator's terminal; ``\x1b]0;evil\x07`` could rewrite the
# window title; raw CR could overwrite previously-printed lines.
# Stripping the whole ESC-introduced sequence is safer than per-byte
# filtering because the SAFE rendering target is plain text — we do
# not emit ANSI colors ourselves.
_ANSI_ESCAPE_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"      # CSI (cursor / color)
    r"|\x1b\][^\x07]*\x07"          # OSC (title) terminated by BEL
    r"|\x1b\][^\x1b]*\x1b\\"        # OSC terminated by ST
    r"|\x1b[@-_]",                  # other ESC-then-byte sequences
)


def _strip_terminal_controls(text: str) -> str:
    """Strip ANSI escape sequences and stray Cc characters from ``text``.

    Tools and exceptions can carry attacker-controlled bytes; rendering
    them raw would let a hostile URL response or filename rewrite the
    operator's terminal. We replace the dangerous bytes with their
    Unicode replacement character so the operator sees that something
    was scrubbed rather than getting silent disappearance.

    Newlines and tabs are kept (they're handled by the line-by-line
    rendering above); everything else in Unicode category ``Cc`` is
    replaced. Bidi-override format chars (Cf) are also stripped — they
    can flip the visual reading order of a line.
    """
    if not text:
        return text
    text = _ANSI_ESCAPE_RE.sub("�", text)
    out_chars = []
    for ch in text:
        if ch in ("\n", "\t"):
            out_chars.append(ch)
            continue
        cat = unicodedata.category(ch)
        if cat in ("Cc", "Cf"):
            out_chars.append("�")
        else:
            out_chars.append(ch)
    return "".join(out_chars)

# --------------------------------------------------------------------- #
# Conversation                                                          #
# --------------------------------------------------------------------- #


def render_reply(
    reply: FuniReply,
    hits: Sequence[RetrievalHit] = (),
    *,
    well_disconnected: bool = False,
) -> str:
    """Format a reply for the operator.

    Includes citations when hits are non-empty; prepends a disconnect
    banner when grounding was unavailable; tags error finish-reasons.
    """
    parts: list[str] = []

    if well_disconnected:
        parts.append(render_well_disconnected_banner())

    body = reply.text.strip() or "(no reply text)"
    if reply.finish_reason is FinishReason.ERROR:
        parts.append(f"[ember reported an error]\n{body}")
    elif reply.finish_reason is FinishReason.LENGTH:
        parts.append(body)
        parts.append("[reply truncated — context limit reached]")
    elif reply.finish_reason is FinishReason.REFUSED:
        parts.append(body)
        parts.append("[ember declined to answer]")
    else:
        parts.append(body)

    if hits and not well_disconnected:
        parts.append(render_citations(hits))

    return "\n\n".join(parts)


def render_well_disconnected_banner(
    disconnect: Disconnected | None = None,
) -> str:
    """The one-line banner shown on ungrounded replies.

    When ``disconnect`` is given, the reason and since-time are included;
    when None, a generic banner is used.
    """
    if disconnect is None:
        return "[well: disconnected — reply is ungrounded]"
    since = disconnect.since.isoformat(timespec="seconds")
    return (
        f"[well: disconnected ({disconnect.reason.value}, since {since}) — "
        f"reply is ungrounded; run `ember doctor` for diagnosis]"
    )


def render_citations(hits: Sequence[RetrievalHit]) -> str:
    """Public citations block (was ``_render_citations`` pre-Phase-11).

    Promoted so chat.py's streaming path can render the footer *after*
    the live token loop ends, without duplicating the format.
    """
    lines = ["citations:"]
    for hit in hits:
        title = hit.document_title or "(untitled)"
        lines.append(f"  - {title} (chunk {hit.chunk_id}, score {hit.score:.3f})")
    return "\n".join(lines)


# --------------------------------------------------------------------- #
# Streaming (Phase 11, ADR 0009 part 2)                                 #
# --------------------------------------------------------------------- #


def render_stream_chunk(chunk: FuniStreamChunk) -> str:
    """The bare text payload to write to stdout for a single stream chunk.

    Chat.py's hot loop calls ``stdout.write(render_stream_chunk(c))``
    once per chunk. Returning the delta unmodified is deliberate — the
    chunker (Funi adapter) preserves whitespace, so we must too.

    The final ``done=True`` chunk often carries an *empty* ``text_delta``
    (Ollama's final ``done:true`` frame has no new content); callers may
    short-circuit on empty deltas, but this helper does not — that
    decision belongs to the consumer.
    """
    return chunk.text_delta


def stream_finish_tag(
    finish_reason: FinishReason | None,
    *,
    interrupted: bool = False,
) -> str | None:
    """The tag appended *after* a streamed reply ends.

    Returns ``None`` when no tag is required (normal STOP completion).
    The interrupted-by-operator tag wins over any finish-reason tag —
    Ctrl-C is a stronger signal than ``length`` or ``error`` because
    the operator chose to stop the stream.
    """
    if interrupted:
        return INTERRUPTED_TAG
    if finish_reason is FinishReason.LENGTH:
        return "[reply truncated — context limit reached]"
    if finish_reason is FinishReason.REFUSED:
        return "[ember declined to answer]"
    if finish_reason is FinishReason.ERROR:
        return "[ember reported an error]"
    return None


# --------------------------------------------------------------------- #
# Tool use (Phase 16, ADR 0011)                                         #
# --------------------------------------------------------------------- #


def render_tool_call_proposal(
    descriptor: ToolDescriptor | None,
    call: ToolCall,
) -> str:
    """Format Funi's proposed tool call for the operator to see.

    Renders the tool name, a one-line description (when a descriptor
    is known), and the argument map. Arguments named in
    ``descriptor.redacted_arg_names`` print as ``<redacted>`` so
    secrets don't appear on stdout.
    """
    lines = [
        f"[tool proposal] {call.name}  (call {call.call_id[:8]})",
    ]
    if descriptor is not None:
        lines.append(f"  description: {descriptor.description}")
    if call.arguments:
        lines.append("  arguments:")
        redacted = (
            set(descriptor.redacted_arg_names) if descriptor is not None else set()
        )
        for name, value in call.arguments.items():
            shown = "<redacted>" if name in redacted else _short_repr(value)
            lines.append(f"    {name}: {shown}")
    else:
        lines.append("  arguments: (none)")
    return "\n".join(lines)


def render_tool_reply(
    reply: ToolReply,
    descriptor: ToolDescriptor | None,
    *,
    outcome: ApprovalOutcome | None = None,
) -> str:
    """Format the executed (or refused) tool reply for the operator.

    Lead line names the tool + the resolution (auto-approved / approved
    / denied / refused / errored). Body shows the bounded output or the
    error string. The full output goes to the audit log; the rendered
    line is truncated so a 4 KB tool output doesn't dominate the chat.
    """
    name = descriptor.name if descriptor is not None else "(unknown tool)"
    head = _outcome_headline(name, reply, outcome)
    # Tool output and error text can carry ANSI escapes or other
    # terminal-rewriting control bytes — sanitise before printing. The
    # audit log gets the raw text (via _serialise_reply); the operator's
    # terminal gets the scrubbed view.
    safe_error = _strip_terminal_controls(reply.error) if reply.error else None
    safe_output = _strip_terminal_controls(reply.output or "")
    if safe_error and not safe_output:
        return f"{head}\n  error: {safe_error}"
    body = safe_output
    if len(body.encode("utf-8")) > TOOL_OUTPUT_PREVIEW_BYTES:
        body = body.encode("utf-8")[:TOOL_OUTPUT_PREVIEW_BYTES].decode(
            "utf-8", errors="ignore",
        ) + "..."
    body_block = "\n".join(f"  {line}" for line in body.splitlines()) or "  (no output)"
    parts = [head, body_block]
    if safe_error:
        parts.append(f"  (with error: {safe_error})")
    return "\n".join(parts)


def _outcome_headline(  # noqa: PLR0911 — one early-return per outcome is the readable shape
    name: str, reply: ToolReply, outcome: ApprovalOutcome | None,
) -> str:
    """One-line summary of the call's resolution."""
    elapsed = f" ({reply.elapsed_s * 1000:.0f} ms)" if reply.elapsed_s else ""
    if outcome is None:
        return f"[tool reply] {name}{elapsed}"
    if outcome is ApprovalOutcome.AUTO_APPROVED:
        return f"[tool reply: auto-approved] {name}{elapsed}"
    if outcome is ApprovalOutcome.APPROVED_THIS_CALL:
        return f"[tool reply: approved] {name}{elapsed}"
    if outcome is ApprovalOutcome.APPROVED_FOR_SESSION:
        return f"[tool reply: approved-for-session] {name}{elapsed}"
    if outcome is ApprovalOutcome.DENIED:
        return f"[tool refused: operator denied] {name}"
    if outcome is ApprovalOutcome.INVALID_ARGUMENTS:
        return f"[tool refused: invalid arguments] {name}"
    if outcome is ApprovalOutcome.FORBIDDEN_BY_REGISTRY:
        return f"[tool refused: forbidden by registry] {name}"
    if outcome is ApprovalOutcome.NO_SUCH_TOOL:
        return f"[tool refused: no such tool] {name}"
    return f"[tool reply: {outcome.value}] {name}{elapsed}"


def _short_repr(value: object) -> str:
    """Compact repr for arg display — keeps the proposal one screen."""
    text = repr(value)
    if len(text) > 200:
        return text[:200] + "..."
    return text


# --------------------------------------------------------------------- #
# Status / doctor / ingest                                              #
# --------------------------------------------------------------------- #


def render_well_status(
    stats: BrunnrStats,
    strengr_health: StrengrHealth,
) -> str:
    last_ok = (
        strengr_health.last_ok.isoformat(timespec="seconds")
        if strengr_health.last_ok
        else "(never)"
    )
    return (
        f"Well ({strengr_health.backend_kind}):\n"
        f"  documents:        {stats.documents}\n"
        f"  chunks:           {stats.chunks}\n"
        f"  embedded chunks:  {stats.embedded_chunks}\n"
        f"  size on disk:     {_human_bytes(stats.size_bytes)}\n"
        f"  last successful probe: {last_ok}"
    )


def render_doctor(
    funi_health: FuniHealth | None,
    strengr_health: StrengrHealth | None,
    brunnr_stats: BrunnrStats | None,
    *,
    funi_unavailable: str | None = None,
    well_disconnected: str | None = None,
) -> str:
    lines = ["Ember health:"]
    # Funi
    if funi_unavailable:
        lines.append(f"  Funi:    UNAVAILABLE — {funi_unavailable}")
    elif funi_health is not None:
        last_ok = (
            funi_health.last_ok.isoformat(timespec="seconds")
            if funi_health.last_ok
            else "(never)"
        )
        lines.append(f"  Funi:    ok — model {funi_health.model_id}, last_ok {last_ok}")
    else:
        lines.append("  Funi:    (not probed)")

    # Strengr / Well
    if well_disconnected:
        lines.append(f"  Well:    DISCONNECTED — {well_disconnected}")
    elif strengr_health is not None and brunnr_stats is not None:
        last_ok = (
            strengr_health.last_ok.isoformat(timespec="seconds")
            if strengr_health.last_ok
            else "(never)"
        )
        lines.append(
            f"  Well:    ok — backend {strengr_health.backend_kind}, "
            f"{brunnr_stats.documents} docs / {brunnr_stats.chunks} chunks, "
            f"last_ok {last_ok}"
        )
    else:
        lines.append("  Well:    (not probed)")

    return "\n".join(lines)


def render_ingest_summary(summary: IngestSummary) -> str:
    return (
        f"Ingest complete (job {summary.job_id[:8]}):\n"
        f"  documents: {summary.n_documents}\n"
        f"  chunks:    {summary.n_chunks}\n"
        f"  failed:    {summary.n_failed}\n"
        f"  elapsed:   {summary.elapsed_s:.2f}s"
    )


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _human_bytes(n: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    size = float(n)
    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


__all__ = [
    "INTERRUPTED_TAG",
    "TOOL_OUTPUT_PREVIEW_BYTES",
    "render_citations",
    "render_doctor",
    "render_ingest_summary",
    "render_reply",
    "render_stream_chunk",
    "render_tool_call_proposal",
    "render_tool_reply",
    "render_well_disconnected_banner",
    "render_well_status",
    "stream_finish_tag",
]
