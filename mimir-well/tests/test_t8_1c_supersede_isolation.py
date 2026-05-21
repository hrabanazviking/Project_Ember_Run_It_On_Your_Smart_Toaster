"""T8-1c: Verify supersede() respects user_id isolation.

- User A cannot supersede user B's memory (UPDATE WHERE user_id mismatch)
- User A CAN supersede their own memory
- New memory from supersede inherits the specified user_id
- Default user_id='runa' still works
"""
import sys, tempfile, os
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import RunaMemory


def test_supersede_with_matching_user_id():
    """supersede with matching user_id should mark old as superseded."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        old_id = mem.add_memory("I love cats", category="preference", importance=7, user_id="runa")
        new_id = mem.supersede(old_id, "I love dogs now", user_id="runa")

        assert new_id > 0, f"supersede should return valid ID, got {new_id}"

        # Old memory should be non-current
        old = mem.get_memory(old_id)
        assert old["is_current"] == 0, "Old memory should be superseded (is_current=0)"
        assert old["superseded_by"] == new_id, "Old memory should reference new ID"

        # New memory should be current and owned by runa
        new = mem.get_memory(new_id)
        assert new["is_current"] == 1, "New memory should be current"
        assert new["content"] == "I love dogs now"
        assert new["user_id"] == "runa"

    finally:
        os.unlink(db_path)


def test_supersede_cross_user_blocked():
    """Volmarr cannot supersede runa's memory — old memory stays current."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        old_id = mem.add_memory("Runa's preference", category="preference", importance=7, user_id="runa")
        new_id = mem.supersede(old_id, "Volmarr trying to supersede", user_id="volmarr")

        # Cross-user supersede fails — get_memory filters by user_id
        # so volmarr can't see runa's memory, supersede returns None
        assert new_id is None, (
            f"Cross-user supersede should return None, got {new_id}"
        )

        # The original memory should remain untouched
        old = mem.get_memory(old_id)
        assert old["is_current"] == 1, (
            f"Old memory should remain current, got is_current={old['is_current']}"
        )
        assert old.get("superseded_by") is None, (
            f"Old memory should not have superseded_by set, got {old.get('superseded_by')}"
        )

    finally:
        os.unlink(db_path)


def test_supersede_default_user_id():
    """supersede without explicit user_id defaults to 'runa'."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        old_id = mem.add_memory("Old preference", category="preference", importance=5)
        new_id = mem.supersede(old_id, "New preference")

        assert new_id > 0
        old = mem.get_memory(old_id)
        assert old["is_current"] == 0, "Default supersede should mark old as non-current"

        new = mem.get_memory(new_id)
        assert new["user_id"] == "runa", "New memory should default to runa"

    finally:
        os.unlink(db_path)


def test_supersede_inherits_category_and_importance():
    """supersede inherits category and importance from old memory."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        old_id = mem.add_memory("Old fact", category="knowledge", importance=9, user_id="runa")
        new_id = mem.supersede(old_id, "Updated fact", user_id="runa")

        new = mem.get_memory(new_id)
        assert new["category"] == "knowledge", f"Should inherit category, got {new['category']}"
        assert new["importance"] == 9, f"Should inherit importance, got {new['importance']}"

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_supersede_with_matching_user_id()
    print("✅ test_supersede_with_matching_user_id")
    test_supersede_cross_user_blocked()
    print("✅ test_supersede_cross_user_blocked")
    test_supersede_default_user_id()
    print("✅ test_supersede_default_user_id")
    test_supersede_inherits_category_and_importance()
    print("✅ test_supersede_inherits_category_and_importance")
    print("\nAll T8-1c tests PASSED! 💜")