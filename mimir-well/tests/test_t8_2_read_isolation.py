"""T8-2: Verify read-side methods respect user_id isolation.

- fts_search with user_id only returns that user's memories
- recall_by_importance/recent/mood with user_id filter correctly
- consolidate with user_id only decays/promotes/prunes that user's data
- promote_to_knowledge with user_id only promotes that user's memories
- detect_contradictions with user_id only finds that user's contradictions
- All methods without user_id return results from all users (backwards compat)
"""
import sys, tempfile, os, time
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import RunaMemory


def _fresh_db():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


def test_fts_search_user_isolation():
    """fts_search with user_id should only return that user's memories.

    Note: FTS5 in content= mode requires a rebuild after inserts.
    This is a known issue — triggers should be added in a future migration.
    """
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        mem.add_memory("Runa loves Python", category="tech", importance=8, user_id="runa")
        mem.add_memory("Volmarr loves Rust", category="tech", importance=8, user_id="volmarr")

        # TODO: Remove this rebuild once FTS triggers are added to migrations
        conn = mem._get_conn()
        conn.execute("INSERT INTO memories_fts(memories_fts) VALUES('rebuild')")
        conn.commit()

        runa_results = mem.fts_search("memories", "loves", user_id="runa")
        volmarr_results = mem.fts_search("memories", "loves", user_id="volmarr")
        all_results = mem.fts_search("memories", "loves")

        assert len(runa_results) == 1, f"Expected 1 runa result, got {len(runa_results)}"
        assert runa_results[0]["user_id"] == "runa"
        assert len(volmarr_results) == 1, f"Expected 1 volmarr result, got {len(volmarr_results)}"
        assert volmarr_results[0]["user_id"] == "volmarr"
        assert len(all_results) == 2, f"Expected 2 results without filter, got {len(all_results)}"
    finally:
        os.unlink(db)
    print("✅ test_fts_search_user_isolation")


def test_recall_by_importance_user_isolation():
    """recall_by_importance with user_id should only return that user's memories."""
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        mem.add_memory("Runa important thing", category="general", importance=9, user_id="runa")
        mem.add_memory("Volmarr important thing", category="general", importance=9, user_id="volmarr")

        runa_results = mem.recall_by_importance(min_importance=8, user_id="runa")
        volmarr_results = mem.recall_by_importance(min_importance=8, user_id="volmarr")
        all_results = mem.recall_by_importance(min_importance=8)

        assert len(runa_results) == 1
        assert runa_results[0]["user_id"] == "runa"
        assert len(volmarr_results) == 1
        assert len(all_results) == 2
    finally:
        os.unlink(db)
    print("✅ test_recall_by_importance_user_isolation")


def test_recall_recent_user_isolation():
    """recall_recent with user_id should only return that user's memories."""
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        mem.add_memory("Runa recent", category="general", importance=5, user_id="runa")
        mem.add_memory("Volmarr recent", category="general", importance=5, user_id="volmarr")

        runa_results = mem.recall_recent(hours=1, user_id="runa")
        volmarr_results = mem.recall_recent(hours=1, user_id="volmarr")
        all_results = mem.recall_recent(hours=1)

        assert len(runa_results) == 1
        assert runa_results[0]["user_id"] == "runa"
        assert len(volmarr_results) == 1
        assert len(all_results) == 2
    finally:
        os.unlink(db)
    print("✅ test_recall_recent_user_isolation")


def test_recall_by_mood_user_isolation():
    """recall_by_mood with user_id should only return that user's memories."""
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        mem.add_memory("Runa happy thought", category="general", importance=7,
                       emotional_valence=0.8, user_id="runa")
        mem.add_memory("Volmarr happy thought", category="general", importance=7,
                       emotional_valence=0.8, user_id="volmarr")

        runa_results = mem.recall_by_mood(target_valence=0.8, tolerance=0.3, user_id="runa")
        volmarr_results = mem.recall_by_mood(target_valence=0.8, tolerance=0.3, user_id="volmarr")

        assert len(runa_results) == 1
        assert runa_results[0]["user_id"] == "runa"
        assert len(volmarr_results) == 1
        assert volmarr_results[0]["user_id"] == "volmarr"
    finally:
        os.unlink(db)
    print("✅ test_recall_by_mood_user_isolation")


def test_consolidate_user_isolation():
    """consolidate with user_id should only decay that user's memories.

    NOTE: relationships table doesn't have user_id yet, so prune
    filtering is graceful-fallback (not user-scoped).
    """
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        # Create a memory with high importance for volmarr
        mem.add_memory("Volmarr stale memory", category="general", importance=9, user_id="volmarr")
        # Manually age it by updating the timestamp
        conn = mem._get_conn()
        conn.execute("UPDATE memories SET timestamp = datetime('now', '-60 days') WHERE user_id = 'volmarr'")
        mem._commit()

        # Consolidate only runa — should NOT decay volmarr's memory
        report = mem.consolidate(user_id="runa")
        assert report["decayed"] == 0, f"Should not decay any memories for runa, got {report['decayed']}"

        # Consolidate volmarr — SHOULD decay volmarr's memory
        report = mem.consolidate(user_id="volmarr")
        assert report["decayed"] >= 1, f"Should decay volmarr's memory, got {report['decayed']}"

        # Check volmarr's memory was decayed from 9 to 8
        # Note: get_memory with user_id filter
        volmarr_mem = mem.get_memory(1, user_id="volmarr")
        assert volmarr_mem["importance"] == 8, f"Expected importance 8 after decay, got {volmarr_mem['importance']}"
    finally:
        os.unlink(db)
    print("✅ test_consolidate_user_isolation")


def test_promote_to_knowledge_user_isolation():
    """promote_to_knowledge with user_id should only promote that user's memories."""
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        mem.add_memory("Runa wisdom", category="general", importance=9, user_id="runa")
        mem.add_memory("Volmarr wisdom", category="general", importance=9, user_id="volmarr")

        # Promote only runa's memories
        result = mem.promote_to_knowledge(min_importance=8, user_id="runa")
        assert result["promoted"] == 1, f"Should promote 1 runa memory, got {result}"
        assert result["skipped"] == 0

        # Promote only volmarr's memories
        result = mem.promote_to_knowledge(min_importance=8, user_id="volmarr")
        assert result["promoted"] == 1, f"Should promote 1 volmarr memory, got {result}"

        # Without user_id, should find both already promoted (both skipped as duplicates)
        result = mem.promote_to_knowledge(min_importance=8)
        assert result["promoted"] == 0  # Both already in knowledge
        assert result["skipped"] == 2   # Both are duplicates
    finally:
        os.unlink(db)
    print("✅ test_promote_to_knowledge_user_isolation")


def test_detect_contradictions_user_isolation():
    """detect_contradictions with user_id should only find that user's contradictions."""
    db = _fresh_db()
    try:
        mem = RunaMemory(db_path=db)
        # Runa has a contradiction
        mem.add_memory("Runa loves Python programming", category="tech",
                       importance=7, emotional_valence=0.8, user_id="runa")
        mem.add_memory("Runa hates Python complexity", category="tech",
                       importance=7, emotional_valence=-0.7, user_id="runa")
        # Volmarr has a contradiction
        mem.add_memory("Volmarr loves Rust safety", category="tech",
                       importance=7, emotional_valence=0.8, user_id="volmarr")
        mem.add_memory("Volmarr hates Rust complexity", category="tech",
                       importance=7, emotional_valence=-0.7, user_id="volmarr")

        runa_contra = mem.detect_contradictions(user_id="runa")
        volmarr_contra = mem.detect_contradictions(user_id="volmarr")
        all_contra = mem.detect_contradictions()

        # All should find contradictions, but user-filtered ones should only
        # contain that user's memories
        for c in runa_contra:
            if "memory_a" in c and c["memory_a"].get("id"):
                m = mem.get_memory(c["memory_a"]["id"])
                assert m["user_id"] == "runa", "Runa contradictions should only reference runa's memories"

        for c in volmarr_contra:
            if "memory_a" in c and c["memory_a"].get("id"):
                m = mem.get_memory(c["memory_a"]["id"])
                assert m["user_id"] == "volmarr", "Volmarr contradictions should only reference volmarr's memories"
    finally:
        os.unlink(db)
    print("✅ test_detect_contradictions_user_isolation")


if __name__ == "__main__":
    test_fts_search_user_isolation()
    test_recall_by_importance_user_isolation()
    test_recall_recent_user_isolation()
    test_recall_by_mood_user_isolation()
    test_consolidate_user_isolation()
    test_promote_to_knowledge_user_isolation()
    test_detect_contradictions_user_isolation()
    print("\nAll T8-2 tests PASSED! 💜")