"""E-031 — corruption fixtures against the real sqlite_vec Well.

The Well half of session persistence, in the extras shape (this
file skips honestly without ``sqlite_vec``, like E-021's reader
tests):

1. Durability pragmas: WAL mode carries ``synchronous = FULL``
   (the Samtal lesson) — a committed Episode survives a power
   cut, not just a clean close.
2. A corrupt episode row (torn cited-ids JSON; a non-integer
   cited id) is skipped by ``recent_episodes`` and the healthy
   history still loads — before E-031 the row's error escaped
   and chat started from an empty history.
3. ``add_episode`` failures are typed ``BrunnrError`` with the
   transaction rolled back (parity with ``add_document`` /
   ``add_chunks``) — before E-031 they propagated raw.
4. Restart proof with a corrupt row present: reopening the store
   still yields exactly the healthy episodes.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

pytest.importorskip("sqlite_vec")

from ember.schemas.config import BrunnrConfig, SqliteVecConfig  # noqa: E402
from ember.schemas.episode import Episode  # noqa: E402
from ember.schemas.errors import BrunnrError  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sqlite_open  # noqa: E402


def _config(tmp_path: Path) -> BrunnrConfig:
    return BrunnrConfig(
        embedding_dim=8,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    )


def _ep(i: int) -> Episode:
    return Episode(
        operator_input=f"question {i}",
        ember_reply=f"answer {i}",
        cited_chunk_ids=(i,),
        funi_model="fake:tiny",
        started_at=datetime(2026, 10, 31, 3, i, tzinfo=UTC),
        completed_at=datetime(2026, 10, 31, 3, i, 30, tzinfo=UTC),
    )


def _insert_raw(handle, cited: str) -> None:
    handle._conn.execute(
        "INSERT INTO episodes (operator_input, ember_reply, "
        "cited_chunk_ids, funi_model, well_disconnected, "
        "started_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("corrupt", "corrupt", cited, "fake:tiny", 0, None, None),
    )
    handle._conn.commit()


def test_wal_carries_synchronous_full(tmp_path: Path) -> None:
    handle = sqlite_open(_config(tmp_path))
    try:
        mode = handle._conn.execute("PRAGMA journal_mode").fetchone()[0]
        sync = handle._conn.execute("PRAGMA synchronous").fetchone()[0]
    finally:
        handle.close()
    assert str(mode).lower() == "wal"
    assert sync == 2  # FULL


def test_corrupt_rows_are_skipped_and_healthy_history_loads(
    tmp_path: Path,
) -> None:
    handle = sqlite_open(_config(tmp_path))
    try:
        handle.add_episode(_ep(1))
        _insert_raw(handle, "not json at all")
        _insert_raw(handle, '[1, "x"]')
        handle.add_episode(_ep(2))
        got = handle.recent_episodes(10)
    finally:
        handle.close()
    assert [e.operator_input for e in got] == ["question 1", "question 2"]


def test_corruption_survives_restart_as_skipped(tmp_path: Path) -> None:
    config = _config(tmp_path)
    handle = sqlite_open(config)
    handle.add_episode(_ep(1))
    _insert_raw(handle, "{torn")
    handle.close()

    reopened = sqlite_open(config)
    try:
        got = reopened.recent_episodes(10)
    finally:
        reopened.close()
    assert [e.operator_input for e in got] == ["question 1"]


def test_add_episode_on_closed_handle_is_typed_brunnr_error(
    tmp_path: Path,
) -> None:
    handle = sqlite_open(_config(tmp_path))
    handle.close()
    with pytest.raises(BrunnrError):
        handle.add_episode(_ep(1))
