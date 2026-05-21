"""T8-1a: Verify delete_memory passes user_id explicitly to audit.log().

This test specifically catches the bug where user_id was buried in metadata JSON
instead of being passed as the explicit `user_id` parameter to AuditTrail.log().
When passed correctly, audit.query(user_id=...) can find the entry by user_id.
When buried in metadata, the audit entry defaults to user_id='runa' regardless.
"""
import sys, tempfile, os
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import RunaMemory, AuditTrail, AuditAction


def test_delete_memory_audit_propagates_user_id():
    """delete_memory log must record the explicit user_id, not default 'runa'."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        # Store a memory as volmarr
        mid = mem.add_memory(
            content="Volmarr's secret thought",
            category="personal",
            importance=8,
            user_id="volmarr",
            source="test",
        )

        # Delete it as volmarr
        result = mem.delete_memory(mid, source="manual", user_id="volmarr")
        assert result, "delete should succeed"

        # Query audit trail by user_id — this is the critical check
        entries = mem.audit.query(user_id="volmarr")

        # Must find at least one volmarr entry
        volmarr_entries = [e for e in entries if e.user_id == "volmarr"]
        assert len(volmarr_entries) >= 1, (
            f"Expected at least 1 volmarr audit entry, got {len(volmarr_entries)}. "
            f"All entries: {[(e.id, e.action, e.user_id) for e in entries]}"
        )

        # The DELETE entry specifically must have user_id="volmarr"
        delete_entries = [e for e in volmarr_entries if e.action == "delete"]
        assert len(delete_entries) >= 1, "Expected a DELETE audit entry for volmarr"
        assert delete_entries[0].user_id == "volmarr", (
            f"DELETE audit entry user_id should be 'volmarr', "
            f"got '{delete_entries[0].user_id}'"
        )

    finally:
        os.unlink(db_path)


def test_delete_memory_audit_default_user_id():
    """delete_memory with default user_id should record 'runa' in audit."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.add_memory(
            content="Default user memory",
            category="general",
            importance=5,
        )

        mem.delete_memory(mid)

        entries = mem.audit.query(action="delete")
        assert len(entries) >= 1, "Expected at least one DELETE audit entry"

        # Default user_id should be 'runa'
        delete_entry = [e for e in entries if e.memory_id == mid][0]
        assert delete_entry.user_id == "runa", (
            f"Default user_id should be 'runa', got '{delete_entry.user_id}'"
        )

    finally:
        os.unlink(db_path)


def test_delete_memory_audit_different_users_isolated():
    """Two users deleting their own memories should have isolated audit entries."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid_runa = mem.add_memory("Runa's memory", user_id="runa")
        mid_volmarr = mem.add_memory("Volmarr's memory", user_id="volmarr")

        mem.delete_memory(mid_runa, user_id="runa")
        mem.delete_memory(mid_volmarr, user_id="volmarr")

        # Querying by volmarr should NOT include runa's delete
        volmarr_entries = mem.audit.query(user_id="volmarr")
        volmarr_deletes = [e for e in volmarr_entries if e.action == "delete"]
        assert all(e.user_id == "volmarr" for e in volmarr_deletes), (
            f"Volmarr audit should only contain volmarr entries, got: "
            f"{[e.user_id for e in volmarr_deletes]}"
        )

        # Querying by runa should NOT include volmarr's delete
        runa_entries = mem.audit.query(user_id="runa")
        runa_deletes = [e for e in runa_entries if e.action == "delete"]
        assert all(e.user_id == "runa" for e in runa_deletes), (
            f"Runa audit should only contain runa entries, got: "
            f"{[e.user_id for e in runa_deletes]}"
        )

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_delete_memory_audit_propagates_user_id()
    print("✅ test_delete_memory_audit_propagates_user_id")
    test_delete_memory_audit_default_user_id()
    print("✅ test_delete_memory_audit_default_user_id")
    test_delete_memory_audit_different_users_isolated()
    print("✅ test_delete_memory_audit_different_users_isolated")
    print("\nAll T8-1a tests PASSED! 💜")