"""Regression tests for the post-cc32dcd Batch G hardening sweep.

Sweep #4 of 2026-05-21. Three fresh-angle Auditors (adapter parity /
Vow enforcement / resource lifecycle) returned three actionable
findings; this file pins their fixes.

If a test fails, the corresponding hardening was reverted.
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

# --------------------------------------------------------------------- #
# Batch G — pgvector text_search Unicode sanitisation                   #
# (adapter parity with sqlite_vec)                                      #
# --------------------------------------------------------------------- #


def test_pgvector_text_search_strips_bidi_override_from_query() -> None:
    """The sqlite_vec adapter strips Cc + Cf bytes from FTS5 queries
    (Batch C). The pgvector adapter must do the same so the audit log
    and operator diagnostics are symmetric across backends.

    We patch the connection so the cursor never executes; we only care
    that the cleaned query passed to plainto_tsquery has the bidi byte
    removed. If sanitisation is reverted, the test sees the raw byte
    on the way to ``cur.execute()``.
    """
    from ember.well.brunnr.pgvector.adapter import PgVectorBrunnr  # noqa: PLC0415

    captured: list[str] = []

    class _StubCursor:
        def __enter__(self): return self
        def __exit__(self, *exc): return False
        def execute(self, sql, params):
            captured.append(params[0])
        def fetchall(self): return []

    class _StubConn:
        def cursor(self): return _StubCursor()

    inst = PgVectorBrunnr.__new__(PgVectorBrunnr)
    inst._conn = _StubConn()
    inst._schema = "public"
    inst._read_only = False
    inst.embedding_dim = 3
    bidi = chr(0x202E)
    inst.text_search(f"hello{bidi}world", k=5)
    assert captured, "execute() was never called"
    assert bidi not in captured[0]
    assert "hello" in captured[0] and "world" in captured[0]


def test_pgvector_text_search_returns_empty_on_whitespace_query() -> None:
    """Parity check: both adapters return [] on a query that becomes
    empty after sanitisation. pgvector previously did this only via
    ``strip()``; now does it after _strip_unsafe_chars too."""
    from ember.well.brunnr.pgvector.adapter import PgVectorBrunnr  # noqa: PLC0415

    inst = PgVectorBrunnr.__new__(PgVectorBrunnr)
    inst._conn = object()  # never reached
    inst._schema = "public"
    inst._read_only = False
    inst.embedding_dim = 3
    # All-Cf characters; sanitiser strips them; strip() leaves "".
    only_bidi = chr(0x202E) + chr(0x200E) + chr(0x202D)
    out = inst.text_search(only_bidi, k=5)
    assert out == []


# --------------------------------------------------------------------- #
# Batch G — pgvector close() logs warnings instead of silent suppress   #
# (adapter parity with sqlite_vec)                                      #
# --------------------------------------------------------------------- #


def test_pgvector_close_logs_warning_on_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """sqlite_vec.close() logs close-time failures via logger.warning
    (Batch D). The pgvector adapter previously used
    ``contextlib.suppress(Exception)`` which silently ate every error.
    Now mirrors sqlite_vec so operators can see *why* close failed."""
    from ember.well.brunnr.pgvector.adapter import PgVectorBrunnr  # noqa: PLC0415

    class _BadConn:
        def close(self):
            raise RuntimeError("backend already gone")

    inst = PgVectorBrunnr.__new__(PgVectorBrunnr)
    inst._conn = _BadConn()
    inst._schema = "public"
    inst._read_only = False
    inst.embedding_dim = 3

    caplog.set_level(logging.WARNING, logger="ember.well.brunnr.pgvector.adapter")
    inst.close()  # must NOT raise

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("pgvector close failed" in r.message for r in warnings), (
        "close-time failure was not logged"
    )


def test_pgvector_close_does_not_raise_on_failure() -> None:
    """The Protocol says close() never raises. Verify with a connection
    that raises arbitrarily."""
    from ember.well.brunnr.pgvector.adapter import PgVectorBrunnr  # noqa: PLC0415

    class _RaisingConn:
        def close(self):
            raise RuntimeError("anything at all")

    inst = PgVectorBrunnr.__new__(PgVectorBrunnr)
    inst._conn = _RaisingConn()
    inst._schema = "public"
    inst._read_only = False
    inst.embedding_dim = 3
    # If close() leaks the exception, the test fails here.
    inst.close()


# --------------------------------------------------------------------- #
# Batch G — journal tempfile cleanup on os.replace failure              #
# (resource lifecycle)                                                  #
# --------------------------------------------------------------------- #


def test_journal_write_state_unlinks_tempfile_on_replace_failure(
    tmp_path: Path,
) -> None:
    """If os.replace() fails (cross-filesystem, EACCES, ENOSPC), the
    tempfile must not orphan in the journal directory. Without
    cleanup, repeated ingest failures on a disk-pressured Pi would
    accumulate orphan files until the disk fills."""
    from ember.schemas.ingest import IngestSourceKind  # noqa: PLC0415
    from ember.well.smidja.journal import Journal, JournalState, _now_iso  # noqa: PLC0415

    state = JournalState(
        job_id="testjob",
        source_kind=IngestSourceKind.LOCAL_FILES,
        source_root=str(tmp_path),
        started_at=_now_iso(),
        last_heartbeat=_now_iso(),
        entries={},
    )
    target = tmp_path / "journal.json"

    def _failing_replace(src, dst):
        raise OSError("simulated EACCES on replace")

    files_before = set(tmp_path.iterdir())
    with (
        patch("ember.well.smidja.journal.os.replace", side_effect=_failing_replace),
        pytest.raises(OSError, match="simulated"),
    ):
        Journal._write_state(target, state)
    files_after = set(tmp_path.iterdir())

    # The .tmp file must have been unlinked; only files present before
    # the failed write should remain.
    new_files = files_after - files_before
    leftover_tmps = [f for f in new_files if f.suffix == ".tmp" or ".tmp." in f.name]
    assert not leftover_tmps, (
        f"orphaned tempfile(s) after failed os.replace: {leftover_tmps!r}"
    )


def test_journal_write_state_happy_path_still_works(tmp_path: Path) -> None:
    """Verify the rewrite didn't break the happy path — the journal
    file should be present and contain the serialised state."""
    import json  # noqa: PLC0415

    from ember.schemas.config import JournalConfig  # noqa: PLC0415, F401
    from ember.schemas.ingest import IngestSourceKind  # noqa: PLC0415
    from ember.well.smidja.journal import (  # noqa: PLC0415
        Journal,
        JournalState,
        _now_iso,
    )

    state = JournalState(
        job_id="testjob",
        source_kind=IngestSourceKind.LOCAL_FILES,
        source_root=str(tmp_path),
        started_at=_now_iso(),
        last_heartbeat=_now_iso(),
        entries={"a": {"status": "done"}},
    )
    target = tmp_path / "journal.json"
    Journal._write_state(target, state)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["job_id"] == "testjob"
    assert loaded["entries"]["a"]["status"] == "done"
    # No tempfile leftover.
    tmps = [f for f in tmp_path.iterdir() if f.suffix == ".tmp" or ".tmp." in f.name]
    assert not tmps
