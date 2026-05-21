"""T8-1e: Verify get_memory() respects user_id isolation.

- get_memory() without user_id returns any memory (backwards compatible)
- get_memory() with user_id filters by ownership
- get_memory() with wrong user_id returns None
- supersede() now uses get_memory with user_id for ownership check
"""
import sys, tempfile, os
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import RunaMemory


def test_get_memory_without_user_id_returns_any():
    """get_memory(id) without user_id should return any memory."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory("Volmarr's secret", category="personal", importance=8, user_id="volmarr")

        # No user_id filter — should return it regardless
        row = mem.get_memory(mid)
        assert row is not None, "get_memory without user_id should return any memory"
        assert row["content"] == "Volmarr's secret"

    finally:
        os.unlink(db_path)


def test_get_memory_with_matching_user_id():
    """get_memory(id, user_id='volmarr') should return volmarr's memory."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory("Volmarr's secret", category="personal", importance=8, user_id="volmarr")

        row = mem.get_memory(mid, user_id="volmarr")
        assert row is not None, "get_memory with matching user_id should return the memory"
        assert row["user_id"] == "volmarr"

    finally:
        os.unlink(db_path)


def test_get_memory_with_wrong_user_id_returns_none():
    """get_memory(id, user_id='runa') should NOT return volmarr's memory."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory("Volmarr's secret", category="personal", importance=8, user_id="volmarr")

        # Try to read as runa — should get None
        row = mem.get_memory(mid, user_id="runa")
        assert row is None, "get_memory with wrong user_id should return None"

    finally:
        os.unlink(db_path)


def test_get_memory_nonexistent_id_returns_none():
    """get_memory with a nonexistent ID returns None regardless of user_id."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        assert mem.get_memory(99999) is None
        assert mem.get_memory(99999, user_id="runa") is None

    finally:
        os.unlink(db_path)


def test_supersede_uses_user_id_for_get_memory():
    """supersede should use get_memory with user_id — cross-user supersede returns None."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        volmarr_id = mem.add_memory("Volmarr's old preference", category="preference", importance=7, user_id="volmarr")

        # Try to supersede volmarr's memory as runa
        result = mem.supersede(volmarr_id, "Runa trying to supersede", user_id="runa")

        # Should return None because get_memory filters by user_id
        assert result is None, f"Cross-user supersede should return None, got {result}"

    finally:
        os.unlink(db_path)


def test_supersede_with_matching_user_id_still_works():
    """supersede with matching user_id should still work after get_memory change."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        old_id = mem.add_memory("Old preference", category="preference", importance=7, user_id="runa")
        new_id = mem.supersede(old_id, "New preference", user_id="runa")

        assert new_id > 0, "Matching supersede should succeed"
        old = mem.get_memory(old_id)
        assert old["is_current"] == 0, "Old should be superseded"

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_get_memory_without_user_id_returns_any()
    print("✅ test_get_memory_without_user_id_returns_any")
    test_get_memory_with_matching_user_id()
    print("✅ test_get_memory_with_matching_user_id")
    test_get_memory_with_wrong_user_id_returns_none()
    print("✅ test_get_memory_with_wrong_user_id_returns_none")
    test_get_memory_nonexistent_id_returns_none()
    print("✅ test_get_memory_nonexistent_id_returns_none")
    test_supersede_uses_user_id_for_get_memory()
    print("✅ test_supersede_uses_user_id_for_get_memory")
    test_supersede_with_matching_user_id_still_works()
    print("✅ test_supersede_with_matching_user_id_still_works")
    print("\nAll T8-1e tests PASSED! 💜")