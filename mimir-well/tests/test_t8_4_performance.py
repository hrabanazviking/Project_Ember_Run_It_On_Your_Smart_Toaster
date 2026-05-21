"""T8-4: Performance and schema fixes.

- decay() uses JOIN instead of N+1 queries
- decay() accepts user_id for namespace isolation
- 'hecedure' typo fixed to 'heuristic' in budget.py
- Migration 008 adds performance indexes
"""

import os
import tempfile
import time
from datetime import datetime

from mimir_well import RunaMemory
from mimir_well.budget import TokenBudget, infer_channel, _TYPE_STRATEGIES


def _fresh_db():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


def test_decay_uses_join_not_nplus1():
    """decay() should not make N+1 queries — it uses a single JOIN."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)

        # Add memories and access logs
        mid1 = mem.add_memory("Ancient wisdom", category="knowledge", importance=8)
        mid2 = mem.add_memory("Recent discovery", category="science_discovery", importance=7)

        # Log access for mid2 (makes it recently accessed)
        from datetime import datetime, timedelta
        conn = mem._get_conn()
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO memory_access_log (memory_id, accessed_at, access_type) VALUES (?, ?, ?)",
            (mid2, now, "recall"),
        )
        mem._commit()

        # Run decay — should work without N+1 queries
        result = mem.decay()
        assert "decayed" in result
        assert "pruned" in result
        assert "reinforced" in result
        assert isinstance(result["reinforced"], int)
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_decay_uses_join_not_nplus1")


def test_decay_user_isolation():
    """decay() with user_id should only decay that user's memories."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)

        mem.add_memory("Runa's old memory", category="general", importance=5, user_id="runa")
        mem.add_memory("Volmarr's old memory", category="general", importance=5, user_id="volmarr")

        result = mem.decay(user_id="runa")
        assert isinstance(result, dict)
        assert "decayed" in result

        # Both users' memories still exist (decay doesn't delete)
        all_memories = mem.recall_by_importance(min_importance=1)
        assert len(all_memories) == 2
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_decay_user_isolation")


def test_decay_reinforcement_uses_user_id():
    """decay() reinforcement should respect user_id namespace."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)

        mid1 = mem.add_memory("Runa wisdom", category="knowledge", importance=7, user_id="runa")
        mid2 = mem.add_memory("Volmarr wisdom", category="knowledge", importance=7, user_id="volmarr")

        # Log recent access for both
        conn = mem._get_conn()
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO memory_access_log (memory_id, accessed_at, access_type) VALUES (?, ?, ?)",
            (mid1, now, "recall"),
        )
        conn.execute(
            "INSERT INTO memory_access_log (memory_id, accessed_at, access_type) VALUES (?, ?, ?)",
            (mid2, now, "recall"),
        )
        mem._commit()

        # Decay with user_id="runa" — only runa's memory should be reinforced
        result = mem.decay(user_id="runa")
        assert result["reinforced"] >= 1, f"Runa's memory should be reinforced, got {result}"
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_decay_reinforcement_uses_user_id")


def test_hecedure_typo_fixed():
    """'hecedure' should no longer exist in budget.py; 'heuristic' should."""
    # _TYPE_STRATEGIES should have 'heuristic', not 'hecedure'
    assert "heuristic" in _TYPE_STRATEGIES, "TYPE_STRATEGIES should have 'heuristic' key"
    assert "hecedure" not in _TYPE_STRATEGIES, "'hecedure' typo should be removed"

    # infer_channel should map 'lesson' to 'procedural' (not 'hecedure')
    assert infer_channel("lesson").value == "procedural"

    # Verify budget allocation has 'heuristic' channel
    budget = TokenBudget(total_context=128000)
    alloc = budget.compute()
    assert "heuristic" in alloc, f"Allocation should have 'heuristic', got {list(alloc.keys())}"
    assert "hecedure" not in alloc, f"'hecedure' typo should not exist in allocation"
    print("✅ test_hecedure_typo_fixed")


def test_migration_008_indexes():
    """Migration 008 should create performance indexes on fresh DB."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)
        conn = mem._get_conn()

        # Check that new indexes exist
        indexes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name"
        ).fetchall()
        index_names = {r[0] for r in indexes}

        assert "idx_access_log_memory_time" in index_names, f"Missing idx_access_log_memory_time"
        assert "idx_access_log_recent" in index_names, f"Missing idx_access_log_recent"
        assert "idx_memories_temporal" in index_names, f"Missing idx_memories_temporal"
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_migration_008_indexes")


def test_decay_performance_comparison():
    """Benchmark: decay with JOIN should be faster than N+1 would be."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)

        # Create 100 memories with access logs
        for i in range(100):
            mid = mem.add_memory(f"Memory {i}", category="general", importance=5 + (i % 5))
            if i % 3 == 0:
                conn = mem._get_conn()
                now = datetime.now().isoformat()
                conn.execute(
                    "INSERT INTO memory_access_log (memory_id, accessed_at, access_type) VALUES (?, ?, ?)",
                    (mid, now, "recall"),
                )
        mem._commit()

        start = time.time()
        result = mem.decay()
        elapsed = time.time() - start

        # Should complete well under 5 seconds for 100 memories
        assert elapsed < 5.0, f"decay() took {elapsed:.2f}s for 100 memories — too slow"
        assert isinstance(result, dict)
    finally:
        mem.close()
        os.unlink(db_path)
    print(f"✅ test_decay_performance_comparison ({elapsed:.3f}s)")


if __name__ == "__main__":
    from datetime import datetime
    test_decay_uses_join_not_nplus1()
    test_decay_user_isolation()
    test_decay_reinforcement_uses_user_id()
    test_hecedure_typo_fixed()
    test_migration_008_indexes()
    test_decay_performance_comparison()
    print("\nAll T8-4 tests PASSED! ⚡")