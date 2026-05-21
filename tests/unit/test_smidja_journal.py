"""Shape and behaviour tests for Smiðja's resumable journal."""

from __future__ import annotations

import json
from pathlib import Path

from ember.schemas.config import JournalConfig
from ember.schemas.ingest import IngestEntryStatus, IngestSourceKind
from ember.well.smidja.journal import Journal


def _make_config(tmp_path: Path) -> JournalConfig:
    return JournalConfig(root=tmp_path)


def test_open_creates_state_file(tmp_path: Path) -> None:
    journal = Journal.open(
        _make_config(tmp_path),
        IngestSourceKind.LOCAL_FILES,
        source_root="/notes",
    )
    assert journal.path.exists()
    payload = json.loads(journal.path.read_text(encoding="utf-8"))
    assert payload["source_root"] == "/notes"
    assert payload["source_kind"] == "local_files"


def test_mark_done_persists_status(tmp_path: Path) -> None:
    journal = Journal.open(
        _make_config(tmp_path),
        IngestSourceKind.LOCAL_FILES,
        source_root="/notes",
    )
    journal.mark_in_progress("/notes/a.md", content_hash="hA")
    journal.mark_done("/notes/a.md", chunk_count=3)

    entry = journal.get_entry("/notes/a.md")
    assert entry is not None
    assert entry.status is IngestEntryStatus.DONE
    assert entry.chunk_count == 3
    assert entry.hash == "hA"


def test_resume_picks_up_existing_journal(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path)
    j1 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root="/notes")
    j1.mark_in_progress("/notes/a.md", content_hash="hA")
    j1.mark_done("/notes/a.md", chunk_count=2)
    job_id_1 = j1.job_id

    # Re-open over the same source_root.
    j2 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root="/notes")
    assert j2.job_id == job_id_1
    assert j2.is_done("/notes/a.md")


def test_distinct_source_roots_get_distinct_jobs(tmp_path: Path) -> None:
    cfg = _make_config(tmp_path)
    j1 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root="/notes")
    j2 = Journal.open(cfg, IngestSourceKind.LOCAL_FILES, source_root="/library")
    assert j1.job_id != j2.job_id


def test_mark_failed_records_error(tmp_path: Path) -> None:
    journal = Journal.open(
        _make_config(tmp_path),
        IngestSourceKind.LOCAL_FILES,
        source_root="/notes",
    )
    journal.mark_in_progress("/notes/a.md")
    journal.mark_failed("/notes/a.md", "out of memory")

    entry = journal.get_entry("/notes/a.md")
    assert entry is not None
    assert entry.status is IngestEntryStatus.FAILED
    assert entry.error == "out of memory"


def test_complete_moves_journal_to_done_subdir(tmp_path: Path) -> None:
    journal = Journal.open(
        _make_config(tmp_path),
        IngestSourceKind.LOCAL_FILES,
        source_root="/notes",
    )
    journal.mark_in_progress("/notes/a.md")
    journal.mark_done("/notes/a.md", chunk_count=1)
    moved = journal.complete()
    assert moved.parent.name == "done"
    assert moved.exists()
    assert not journal.path.exists()


def test_pending_returns_only_not_done(tmp_path: Path) -> None:
    journal = Journal.open(
        _make_config(tmp_path),
        IngestSourceKind.LOCAL_FILES,
        source_root="/notes",
    )
    journal.mark_in_progress("/notes/a.md")
    journal.mark_done("/notes/a.md", chunk_count=1)
    pending = journal.pending(["/notes/a.md", "/notes/b.md", "/notes/c.md"])
    assert pending == ["/notes/b.md", "/notes/c.md"]


def test_atomic_write_does_not_leave_tmp_files(tmp_path: Path) -> None:
    journal = Journal.open(
        _make_config(tmp_path),
        IngestSourceKind.LOCAL_FILES,
        source_root="/notes",
    )
    for i in range(20):
        journal.mark_in_progress(f"/notes/f{i}.md")
        journal.mark_done(f"/notes/f{i}.md", chunk_count=1)

    leftover = [p for p in tmp_path.iterdir() if p.name.endswith(".tmp") or ".json.tmp" in p.name]
    assert leftover == [], f"unexpected tmp files: {leftover}"
