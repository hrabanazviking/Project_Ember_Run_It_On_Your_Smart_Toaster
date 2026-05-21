"""T8-1b: Verify update_memory and delete_memory respect user_id isolation.

Cross-user mutations must be blocked:
- User A cannot UPDATE user B's memory
- User A cannot DELETE user B's memory
- User A CAN update/delete their own memories
"""
import sys, tempfile, os
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import RunaMemory


def test_update_memory_respects_user_id():
    """update_memory with user_id='volmarr' must NOT update runa's memory."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        # Store a memory as runa
        mid = mem.add_memory(
            content="Runa's original thought",
            category="personal",
            importance=5,
            user_id="runa",
        )

        # Try to update it as volmarr — should fail (WHERE id=? AND user_id='volmarr' matches nothing)
        result = mem.update_memory(
            mid, user_id="volmarr", content="Volmarr trying to overwrite"
        )
        assert not result, "update_memory should return False when user_id doesn't match"

        # Verify the content is unchanged
        row = mem.get_memory(mid)
        assert row is not None, "Memory should still exist"
        assert row["content"] == "Runa's original thought", (
            f"Content should be unchanged, got: {row['content']}"
        )

    finally:
        os.unlink(db_path)


def test_update_memory_allows_owner():
    """update_memory with matching user_id should succeed."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory(
            content="Original content",
            category="general",
            importance=5,
            user_id="runa",
        )

        # Update as runa — should succeed
        result = mem.update_memory(
            mid, user_id="runa", content="Updated content"
        )
        assert result, "update_memory should succeed when user_id matches"

        row = mem.get_memory(mid)
        assert row["content"] == "Updated content", (
            f"Content should be updated, got: {row['content']}"
        )

    finally:
        os.unlink(db_path)


def test_delete_memory_respects_user_id():
    """delete_memory with user_id='volmarr' must NOT delete runa's memory."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory(
            content="Runa's persistent memory",
            category="general",
            importance=5,
            user_id="runa",
        )

        # Try to delete as volmarr — should fail (WHERE id=? AND user_id='volmarr' matches nothing)
        result = mem.delete_memory(mid, source="test", user_id="volmarr")
        assert not result, "delete_memory should return False when user_id doesn't match"

        # Verify memory still exists
        row = mem.get_memory(mid)
        assert row is not None, "Memory should still exist after failed delete"
        assert row["content"] == "Runa's persistent memory"

    finally:
        os.unlink(db_path)


def test_delete_memory_allows_owner():
    """delete_memory with matching user_id should succeed."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory(
            content="Memory to delete",
            category="general",
            importance=5,
            user_id="runa",
        )

        result = mem.delete_memory(mid, source="test", user_id="runa")
        assert result, "delete_memory should succeed when user_id matches"

        # Verify memory is gone
        row = mem.get_memory(mid)
        assert row is None, "Memory should be deleted"

    finally:
        os.unlink(db_path)


def test_default_user_id_can_delete_default_memories():
    """Deleting with default user_id='runa' should work for default-owned memories."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory(content="Default memory", category="general")

        # Delete with default user_id (runa)
        result = mem.delete_memory(mid)
        assert result, "Default user should be able to delete default memories"

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_update_memory_respects_user_id()
    print("✅ test_update_memory_respects_user_id")
    test_update_memory_allows_owner()
    print("✅ test_update_memory_allows_owner")
    test_delete_memory_respects_user_id()
    print("✅ test_delete_memory_respects_user_id")
    test_delete_memory_allows_owner()
    print("✅ test_delete_memory_allows_owner")
    test_default_user_id_can_delete_default_memories()
    print("✅ test_default_user_id_can_delete_default_memories")
    print("\nAll T8-1b tests PASSED! 💜")