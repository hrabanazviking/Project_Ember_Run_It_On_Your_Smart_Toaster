"""Regression tests for Batch K — the two final orphan-field wirings.

Sweep #8 of 2026-05-21. The unwired-inventory audit
(`docs/UNWIRED_INVENTORY.md`) named two schema fields declared but
never read:

  1. StrengrConfig.health_check_timeout_s — now enforced via
     ThreadPoolExecutor in `strengr.health(..., timeout_s=...)`.
  2. JournalConfig.stale_heartbeat_s — now enforced in
     `Journal.open()` via the new `_heartbeat_is_stale` helper.

These tests pin the wirings so future PRs can't re-orphan them.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from ember.schemas.config import JournalConfig
from ember.schemas.ingest import IngestSourceKind

# --------------------------------------------------------------------- #
# Batch K — StrengrConfig.health_check_timeout_s actually enforced      #
# --------------------------------------------------------------------- #


def test_strengr_health_no_timeout_runs_unchanged() -> None:
    """Backward-compat: existing callers that don't pass timeout_s
    get the previous behavior (synchronous probe, no thread pool)."""
    from ember.schemas.chunks import BrunnrStats  # noqa: PLC0415
    from ember.thread.strengr.tether import health  # noqa: PLC0415

    class _FastHandle:
        backend_kind = "test"
        def count(self) -> BrunnrStats:
            return BrunnrStats(
                documents=3, chunks=10, embedded_chunks=10, size_bytes=1024,
            )

    result = health(_FastHandle())
    assert result.last_ok is not None
    assert result.documents == 3


def test_strengr_health_with_timeout_returns_typed_on_overrun() -> None:
    """A handle whose count() takes longer than timeout_s must produce
    a typed StrengrHealth (last_ok=None, detail mentions timeout)
    without blocking the caller. This is the wiring that was missing
    before Batch K — health_check_timeout_s was declared in the schema
    but never enforced."""
    from ember.thread.strengr.tether import health  # noqa: PLC0415

    class _SlowHandle:
        backend_kind = "test"
        def count(self):
            time.sleep(2.0)

    t0 = time.monotonic()
    result = health(_SlowHandle(), timeout_s=0.15)
    elapsed = time.monotonic() - t0
    assert elapsed < 1.0, f"timeout did not fire, took {elapsed}s"
    assert result.last_ok is None
    assert result.detail and "timeout" in result.detail.lower()


def test_strengr_health_timeout_doesnt_crash_on_handle_exception() -> None:
    """If the handle raises before the timeout fires, we still get a
    typed StrengrHealth (last_ok=None, detail names the exception)."""
    from ember.thread.strengr.tether import health  # noqa: PLC0415

    class _RaisingHandle:
        backend_kind = "test"
        def count(self):
            raise RuntimeError("crafted in test")

    result = health(_RaisingHandle(), timeout_s=5.0)
    assert result.last_ok is None
    assert result.detail and "crafted in test" in result.detail


# --------------------------------------------------------------------- #
# Batch K — JournalConfig.stale_heartbeat_s actually enforced           #
# --------------------------------------------------------------------- #


def test_heartbeat_is_stale_true_for_old_timestamp() -> None:
    """A timestamp 1 hour ago is stale at a 60s threshold."""
    from ember.well.smidja.journal import _heartbeat_is_stale  # noqa: PLC0415

    one_hour_ago = (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat()
    assert _heartbeat_is_stale(one_hour_ago, threshold_s=60) is True


def test_heartbeat_is_stale_false_for_fresh_timestamp() -> None:
    """A timestamp 1 second ago is NOT stale at a 60s threshold."""
    from ember.well.smidja.journal import _heartbeat_is_stale  # noqa: PLC0415

    one_sec_ago = (datetime.now(tz=UTC) - timedelta(seconds=1)).isoformat()
    assert _heartbeat_is_stale(one_sec_ago, threshold_s=60) is False


def test_heartbeat_is_stale_false_for_malformed_timestamp() -> None:
    """Defensive: a malformed timestamp is treated as fresh — we'd
    rather attempt resume than wrongly discard work."""
    from ember.well.smidja.journal import _heartbeat_is_stale  # noqa: PLC0415

    assert _heartbeat_is_stale("not-a-date", threshold_s=60) is False
    assert _heartbeat_is_stale("", threshold_s=60) is False


def test_journal_open_resumes_fresh_existing_journal(tmp_path: Path) -> None:
    """The happy path: an existing journal with a recent heartbeat
    gets resumed (not archived)."""
    from ember.well.smidja.journal import Journal  # noqa: PLC0415

    cfg = JournalConfig(root=tmp_path, stale_heartbeat_s=3600)

    j1 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root=str(tmp_path))
    j1.mark_in_progress("/notes/x.md", content_hash="abc")
    job_id_first = j1.job_id

    j2 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root=str(tmp_path))
    # Same journal — resumed, not fresh.
    assert j2.job_id == job_id_first


def test_journal_open_archives_stale_journal_and_starts_fresh(
    tmp_path: Path,
) -> None:
    """A journal whose last_heartbeat is older than stale_heartbeat_s
    must be archived (renamed with .stale-<ts> suffix) and a new
    journal opened. This is the Batch K wiring of stale_heartbeat_s."""
    import json  # noqa: PLC0415

    from ember.well.smidja.journal import Journal  # noqa: PLC0415

    cfg = JournalConfig(root=tmp_path, stale_heartbeat_s=60)

    j1 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root=str(tmp_path))
    j1.mark_in_progress("/old/notes.md", content_hash="hOld")
    old_id = j1.job_id

    # Manually mutate the on-disk last_heartbeat to be 2 days ago.
    journal_path = tmp_path / f"{old_id}.json"
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    old_time = (datetime.now(tz=UTC) - timedelta(days=2)).isoformat()
    payload["last_heartbeat"] = old_time
    journal_path.write_text(json.dumps(payload), encoding="utf-8")

    # Now re-open — should detect stale, archive, start fresh.
    j2 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root=str(tmp_path))
    assert j2.job_id != old_id  # fresh journal
    assert not journal_path.exists()  # original moved aside
    stale_files = list(tmp_path.glob(f"{old_id}.json.stale-*"))
    assert len(stale_files) == 1, (
        f"expected one stale-archived file, found {stale_files}"
    )


def test_journal_open_huge_threshold_disables_check(tmp_path: Path) -> None:
    """A very large stale_heartbeat_s lets the operator opt out of the
    staleness check entirely — even ancient journals get resumed."""
    from ember.well.smidja.journal import Journal  # noqa: PLC0415

    cfg = JournalConfig(root=tmp_path, stale_heartbeat_s=10_000_000)

    j1 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root=str(tmp_path))
    job_id_first = j1.job_id
    j2 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root=str(tmp_path))
    assert j2.job_id == job_id_first
