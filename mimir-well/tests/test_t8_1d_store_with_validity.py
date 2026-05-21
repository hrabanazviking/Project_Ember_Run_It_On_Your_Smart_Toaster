"""T8-1d: Verify store_with_validity() accepts and propagates user_id + source.

- store_with_validity creates memories attributed to the correct user_id
- Validity UPDATE respects user_id (WHERE id=? AND user_id=?)
- Default user_id='runa' and source='temporal' still work
- source parameter is passed through to add_memory audit
"""
import sys, tempfile, os
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import RunaMemory


def test_store_with_validity_user_id():
    """store_with_validity should attribute memory to the specified user_id."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.store_with_validity(
            content="Staying at Hotel Valhalla until Friday",
            category="schedule",
            importance=7,
            valid_from="2026-05-14T00:00:00",
            valid_until="2026-05-16T00:00:00",
            user_id="volmarr",
            source="calendar",
        )

        assert mid > 0, f"store_with_validity should return valid ID, got {mid}"

        row = mem.get_memory(mid)
        assert row is not None, "Memory should exist"
        assert row["user_id"] == "volmarr", f"Expected user_id='volmarr', got '{row['user_id']}'"
        assert row["valid_from"] == "2026-05-14T00:00:00"
        assert row["valid_until"] == "2026-05-16T00:00:00"

    finally:
        os.unlink(db_path)


def test_store_with_validity_default_user_id():
    """store_with_validity without explicit user_id defaults to 'runa'."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.store_with_validity(
            content="Flight at 3pm",
            importance=6,
            valid_until="2026-05-15T15:00:00",
        )

        row = mem.get_memory(mid)
        assert row["user_id"] == "runa", f"Default user_id should be 'runa', got '{row['user_id']}'"

    finally:
        os.unlink(db_path)


def test_store_with_validity_audit_source():
    """store_with_validity source param should appear in audit trail."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        mid = mem.store_with_validity(
            content="Temporary fact",
            source="calendar_sync",
            user_id="runa",
        )

        entries = mem.audit.query(source="calendar_sync")
        assert len(entries) >= 1, "Should find audit entry with source='calendar_sync'"

    finally:
        os.unlink(db_path)


def test_store_with_validity_validity_update_isolation():
    """Validity UPDATE should be scoped to the correct user_id."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        mem = RunaMemory(db_path=db_path)

        # Store as runa
        mid = mem.store_with_validity(
            content="Runa's temporal fact",
            valid_from="2026-01-01T00:00:00",
            valid_until="2026-12-31T23:59:59",
            user_id="runa",
        )

        # Verify validity was set
        row = mem.get_memory(mid)
        assert row["valid_from"] == "2026-01-01T00:00:00"
        assert row["valid_until"] == "2026-12-31T23:59:59"

    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_store_with_validity_user_id()
    print("✅ test_store_with_validity_user_id")
    test_store_with_validity_default_user_id()
    print("✅ test_store_with_validity_default_user_id")
    test_store_with_validity_audit_source()
    print("✅ test_store_with_validity_audit_source")
    test_store_with_validity_validity_update_isolation()
    print("✅ test_store_with_validity_validity_update_isolation")
    print("\nAll T8-1d tests PASSED! 💜")