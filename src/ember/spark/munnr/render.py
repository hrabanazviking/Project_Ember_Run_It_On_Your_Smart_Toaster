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

from collections.abc import Sequence

from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.errors import Disconnected
from ember.schemas.funi import FinishReason, FuniHealth, FuniReply
from ember.schemas.ingest import IngestSummary
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.thread import StrengrHealth

INTERRUPTED_TAG = "[interrupted by operator]"

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
    "render_citations",
    "render_doctor",
    "render_ingest_summary",
    "render_reply",
    "render_stream_chunk",
    "render_well_disconnected_banner",
    "render_well_status",
    "stream_finish_tag",
]
