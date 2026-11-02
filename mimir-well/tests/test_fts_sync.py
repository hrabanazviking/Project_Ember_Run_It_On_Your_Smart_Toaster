"""FTS5 sync triggers — regression tests for Ember docket 111 (E-078).

Before the fix, the external-content FTS5 indexes were only
populated by the rebuild RunaMemory runs at open time, so
anything written during a session was invisible to fts_search
until the store was reopened. schema.py even claimed SQLite
syncs external-content tables automatically; it does not —
the trigger set in FTS_TRIGGERS (executed at every open) is
the mechanism. These tests pin in-session sync for all three
FTS tables across insert, update, and delete, with NO manual
rebuild anywhere.
"""

import tempfile
from pathlib import Path

import pytest

from mimir_well.core import RunaMemory


@pytest.fixture
def mimir():
    db_path = tempfile.mktemp(suffix=".db")
    mem = RunaMemory(db_path=db_path)
    yield mem
    mem.close()
    Path(db_path).unlink(missing_ok=True)


def test_memory_insert_is_fts_visible_in_session(mimir):
    mimir.add_memory("The harbour ferry leaves at the dawn bell.",
                     category="knowledge", importance=6)
    assert len(mimir.fts_search("memories", "ferry")) == 1
    assert len(mimir.fts_search("memories", "dawn bell")) == 1


def test_memory_update_moves_the_index(mimir):
    mid = mimir.add_memory("The harbour ferry leaves at the dawn bell.",
                           category="knowledge", importance=6)
    mimir.update_memory(mid, content="The harbour ferry now leaves "
                                     "at the dusk bell.")
    assert mimir.fts_search("memories", "dawn") == []
    assert len(mimir.fts_search("memories", "dusk")) == 1


def test_memory_delete_leaves_the_index(mimir):
    mid = mimir.add_memory("A knarr carries forty barrels.",
                           category="knowledge", importance=5)
    assert len(mimir.fts_search("memories", "knarr")) == 1
    mimir.delete_memory(mid)
    assert mimir.fts_search("memories", "knarr") == []


def test_knowledge_insert_is_fts_visible_in_session(mimir):
    mimir.add_knowledge("seafaring", "A knarr carries forty barrels.",
                        source="test")
    assert len(mimir.fts_search("knowledge", "knarr")) == 1


def test_saga_event_insert_is_fts_visible_in_session(mimir):
    mimir.add_saga_event("launch", entity_id="knarr-1")
    assert len(mimir.fts_search("saga_events", "launch")) == 1


def test_triggers_exist_on_a_fresh_store(mimir):
    conn = mimir._get_conn()
    names = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger'")}
    for table in ("memories", "knowledge", "saga_events"):
        for suffix in ("ai", "ad", "au"):
            assert f"{table}_fts_{suffix}" in names
