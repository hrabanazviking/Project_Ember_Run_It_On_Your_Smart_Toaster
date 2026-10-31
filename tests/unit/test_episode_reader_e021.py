"""E-021 — the Well episode reader against the real sqlite_vec adapter.

Episodes were write-only before E-021 (docket 81): ``add_episode``
existed, no reader did, and the MCP server's own note said so. This
file proves the reader half — round-trip, order, limit, and the
restart shape (open → write → close → reopen → read back) — in the
extras shape (sqlite_vec supplied); it skips honestly without it.
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
        cited_chunk_ids=(i, i + 100),
        funi_model="fake:tiny",
        well_disconnected=(i % 2 == 0),
        started_at=datetime(2026, 10, 31, 1, i, tzinfo=UTC),
        completed_at=datetime(2026, 10, 31, 1, i, 30, tzinfo=UTC),
    )


def test_recent_episodes_round_trip_oldest_first(tmp_path: Path) -> None:
    handle = sqlite_open(_config(tmp_path))
    try:
        assert handle.recent_episodes(10) == []
        for i in range(5):
            handle.add_episode(_ep(i))
        got = handle.recent_episodes(10)
    finally:
        handle.close()
    assert [e.operator_input for e in got] == [f"question {i}" for i in range(5)]
    first = got[0]
    assert first.cited_chunk_ids == (0, 100)
    assert first.funi_model == "fake:tiny"
    assert first.well_disconnected is True
    assert first.id is not None
    assert first.started_at is not None and first.started_at.hour == 1


def test_recent_episodes_limit_keeps_the_newest(tmp_path: Path) -> None:
    handle = sqlite_open(_config(tmp_path))
    try:
        for i in range(5):
            handle.add_episode(_ep(i))
        got = handle.recent_episodes(2)
        assert handle.recent_episodes(0) == []
    finally:
        handle.close()
    assert [e.operator_input for e in got] == ["question 3", "question 4"]


def test_history_survives_a_restart(tmp_path: Path) -> None:
    config = _config(tmp_path)
    handle = sqlite_open(config)
    handle.add_episode(_ep(7))
    handle.close()

    reopened = sqlite_open(config)
    try:
        got = reopened.recent_episodes(10)
    finally:
        reopened.close()
    assert len(got) == 1
    assert got[0].operator_input == "question 7"
    assert got[0].ember_reply == "answer 7"


def test_recent_episodes_on_closed_handle_is_typed_error(
    tmp_path: Path,
) -> None:
    handle = sqlite_open(_config(tmp_path))
    handle.close()
    with pytest.raises(BrunnrError):
        handle.recent_episodes(5)
