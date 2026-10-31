"""E-038 — the real sqlite_vec Well under two concurrent chats.

Skipped automatically if sqlite_vec is not installed (the
campaign's extras shape runs it). Two handles on ONE database
file stand in for two chat processes sharing the tethered Well:
episode saves from both must all land, with no "database is
locked" failure — the adapter's ``PRAGMA busy_timeout`` (E-038)
is what makes the second writer wait for the first's commit.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

sqlite_vec = pytest.importorskip("sqlite_vec")

from ember.schemas.config import BrunnrConfig, SqliteVecConfig  # noqa: E402
from ember.schemas.episode import Episode  # noqa: E402
from ember.well.brunnr.sqlite_vec import SqliteVecBrunnr  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402


def _open(tmp_path: Path, name: str = "store.db") -> SqliteVecBrunnr:
    cfg = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=tmp_path / name),
    )
    handle = sv_open(cfg)
    assert isinstance(handle, SqliteVecBrunnr)
    return handle


def test_open_sets_busy_timeout(tmp_path: Path) -> None:
    handle = _open(tmp_path)
    try:
        value = handle._conn.execute("PRAGMA busy_timeout").fetchone()[0]
        assert value == 5000
    finally:
        handle.close()


def test_two_handles_same_file_all_saves_land(tmp_path: Path) -> None:
    first = _open(tmp_path)
    second = _open(tmp_path)
    errors: list[BaseException] = []

    def save_batch(handle: SqliteVecBrunnr, tag: str) -> None:
        try:
            for i in range(10):
                handle.add_episode(
                    Episode(
                        operator_input=f"{tag}-{i}",
                        ember_reply=f"reply {tag}-{i}",
                    )
                )
        except BaseException as exc:  # noqa: BLE001 — asserted below
            errors.append(exc)

    threads = [
        threading.Thread(target=save_batch, args=(first, "a")),
        threading.Thread(target=save_batch, args=(second, "b")),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    try:
        assert errors == []
        stored = first.recent_episodes(100)
        assert sorted(ep.operator_input for ep in stored) == sorted(
            [f"a-{i}" for i in range(10)] + [f"b-{i}" for i in range(10)]
        )
    finally:
        first.close()
        second.close()
