"""Shape contracts for the Munnr render helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import FinishReason, FuniHealth, FuniReply
from ember.schemas.ingest import IngestSummary
from ember.schemas.thread import StrengrHealth
from ember.spark.munnr import render


def test_reply_with_no_hits_renders_just_the_body() -> None:
    reply = FuniReply(text="hello there", finish_reason=FinishReason.STOP)
    out = render.render_reply(reply)
    assert "hello there" in out
    assert "citations" not in out
    assert "well:" not in out


def test_reply_with_hits_renders_citations() -> None:
    reply = FuniReply(text="Odin is wise", finish_reason=FinishReason.STOP)
    hits = [
        RetrievalHit(
            chunk_id=42, document_id=1, document_title="The Eddas",
            text="...", score=0.91,
        )
    ]
    out = render.render_reply(reply, hits)
    assert "The Eddas" in out
    assert "chunk 42" in out


def test_reply_when_disconnected_prepends_banner_and_skips_citations() -> None:
    reply = FuniReply(text="I don't know", finish_reason=FinishReason.STOP)
    hits = [
        RetrievalHit(
            chunk_id=1, document_id=1, document_title="x", text="...", score=0.1,
        )
    ]
    out = render.render_reply(reply, hits, well_disconnected=True)
    assert out.startswith("[well: disconnected")
    assert "citations" not in out


def test_reply_with_finish_reason_error_is_tagged() -> None:
    reply = FuniReply(text="[ollama unreachable]", finish_reason=FinishReason.ERROR)
    out = render.render_reply(reply)
    assert "[ember reported an error]" in out


def test_reply_with_finish_reason_length_is_tagged() -> None:
    reply = FuniReply(text="long reply...", finish_reason=FinishReason.LENGTH)
    out = render.render_reply(reply)
    assert "[reply truncated" in out


def test_well_disconnected_banner_includes_reason_and_since() -> None:
    disconnect = Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime(2026, 5, 21, 3, 42, 0, tzinfo=UTC),
    )
    banner = render.render_well_disconnected_banner(disconnect)
    assert "conn_refused" in banner
    assert "2026-05-21T03:42:00+00:00" in banner
    assert "ember doctor" in banner


def test_well_status_renders_counts_and_last_ok() -> None:
    stats = BrunnrStats(documents=2, chunks=10, embedded_chunks=10, size_bytes=2048)
    health = StrengrHealth(
        backend_kind="sqlite_vec",
        last_ok=datetime(2026, 5, 21, 4, 0, 0, tzinfo=UTC),
        documents=2, chunks=10, embedded_chunks=10, size_bytes=2048,
    )
    out = render.render_well_status(stats, health)
    assert "sqlite_vec" in out
    assert "2" in out
    assert "10" in out
    assert "2026-05-21T04:00:00+00:00" in out


def test_doctor_renders_well_and_funi_lines() -> None:
    funi_health = FuniHealth(model_id="phi3:mini", last_ok=datetime.now(tz=UTC))
    well_health = StrengrHealth(backend_kind="sqlite_vec", last_ok=datetime.now(tz=UTC))
    well_stats = BrunnrStats(documents=1, chunks=1, embedded_chunks=1, size_bytes=10)
    out = render.render_doctor(funi_health, well_health, well_stats)
    assert "Funi:" in out
    assert "phi3:mini" in out
    assert "Well:" in out
    assert "sqlite_vec" in out


def test_doctor_renders_unavailable_funi() -> None:
    out = render.render_doctor(
        None, None, None, funi_unavailable="connection refused", well_disconnected=None,
    )
    assert "UNAVAILABLE" in out
    assert "connection refused" in out


def test_doctor_renders_disconnected_well() -> None:
    out = render.render_doctor(
        None, None, None, funi_unavailable=None, well_disconnected="conn_refused",
    )
    assert "DISCONNECTED" in out
    assert "conn_refused" in out


def test_ingest_summary_renders_counts_and_elapsed() -> None:
    summary = IngestSummary(
        job_id="0123456789abcdef",
        n_documents=3, n_chunks=15, n_failed=1, elapsed_s=1.234,
    )
    out = render.render_ingest_summary(summary)
    assert "01234567" in out  # short id
    assert "3" in out
    assert "15" in out
    assert "1.23" in out
