"""T8-5: Architecture improvements — AuditTrail thread-local, type hints, docstrings.

- AuditTrail uses thread-local connection reuse (no open/close per call)
- AuditTrail.close() properly shuts down connection
- RunaMemory.close() also closes audit trail connection
- stats() supports user_id filter
- All methods have proper type hints
"""

import os
import tempfile
import threading

from mimir_well import RunaMemory
from mimir_well.audit import AuditTrail, AuditAction, AuditEntry


def _fresh_db():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


def test_audit_trail_thread_local_reuse():
    """AuditTrail should reuse the same connection per thread, not open/close each call."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)
        audit = mem.audit

        # Log an entry — should use thread-local connection
        aid = audit.log(
            memory_id=1,
            action=AuditAction.STORE,
            source="test",
            content_hash="abc123",
        )
        assert aid > 0, f"Should return audit ID, got {aid}"

        # Log another entry — should reuse same connection
        aid2 = audit.log(
            memory_id=1,
            action=AuditAction.UPDATE,
            source="test",
            content_hash="def456",
        )
        assert aid2 > aid, "Second ID should be greater"

        # Query — should reuse same connection
        entries = audit.query(memory_id=1)
        assert len(entries) == 2, f"Should find 2 entries, got {len(entries)}"

        # Verify connection is thread-local (not closed between calls)
        conn = audit._get_conn()
        assert conn is not None, "Should have a connection"
        # Verify it's still alive (not closed)
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1, "Connection should be alive"
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_audit_trail_thread_local_reuse")


def test_audit_trail_close():
    """AuditTrail.close() should properly close the thread-local connection."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)
        audit = mem.audit

        # Use it first
        audit.log(memory_id=1, action=AuditAction.STORE, source="test", content_hash="abc")

        # Close the audit trail
        audit.close()

        # Verify connection is gone
        conn = getattr(audit._local, 'conn', None)
        assert conn is None, "Connection should be None after close"

        # Creating a new audit and using it should work (new connection)
        audit2 = AuditTrail(db_path)
        audit2.log(memory_id=1, action=AuditAction.STORE, source="test2", content_hash="def")
        audit2.close()
    finally:
        os.unlink(db_path)
    print("✅ test_audit_trail_close")


def test_runamemory_close_closes_audit():
    """RunaMemory.close() should also close the AuditTrail connection."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)

        # Use audit through RunaMemory
        mem.audit.log(memory_id=1, action=AuditAction.STORE, source="test", content_hash="abc")

        # Close RunaMemory (should also close audit)
        mem.close()

        # Audit connection should be cleaned up
        audit_conn = getattr(mem.audit._local, 'conn', None)
        assert audit_conn is None, "Audit connection should be None after RunaMemory.close()"
    finally:
        os.unlink(db_path)
    print("✅ test_runamemory_close_closes_audit")


def test_audit_stats_user_id():
    """AuditTrail.stats() should support user_id filtering."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)

        mem.audit.log(memory_id=1, action=AuditAction.STORE, source="test",
                      content_hash="abc", user_id="runa")
        mem.audit.log(memory_id=2, action=AuditAction.STORE, source="test",
                      content_hash="def", user_id="volmarr")
        mem.audit.log(memory_id=3, action=AuditAction.STORE, source="test",
                      content_hash="ghi", user_id="runa")

        # Stats for all users
        all_stats = mem.audit.stats()
        assert all_stats["total_entries"] == 3, f"Expected 3 total, got {all_stats['total_entries']}"

        # Stats for runa only
        runa_stats = mem.audit.stats(user_id="runa")
        assert runa_stats["total_entries"] == 2, f"Expected 2 runa entries, got {runa_stats['total_entries']}"

        # Stats for volmarr only
        volmarr_stats = mem.audit.stats(user_id="volmarr")
        assert volmarr_stats["total_entries"] == 1, f"Expected 1 volmarr entry, got {volmarr_stats['total_entries']}"
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_audit_stats_user_id")


def test_audit_entry_to_dict():
    """AuditEntry.to_dict() should return all fields including user_id."""
    entry = AuditEntry(
        id=1,
        memory_id=42,
        action="store",
        source="hermes",
        content_hash="abc123",
        timestamp="2026-05-14T12:00:00",
        metadata={"category": "knowledge"},
        user_id="runa",
    )
    d = entry.to_dict()
    assert d["user_id"] == "runa", f"user_id should be 'runa', got {d.get('user_id')}"
    assert d["action"] == "store"
    assert d["metadata"] == {"category": "knowledge"}
    print("✅ test_audit_entry_to_dict")


def test_audit_trail_multithreaded():
    """AuditTrail should handle concurrent access from multiple threads."""
    db_path = _fresh_db()
    try:
        mem = RunaMemory(db_path=db_path)
        results = {"success": 0, "errors": 0}
        lock = threading.Lock()

        def write_audit(thread_id):
            try:
                mem.audit.log(
                    memory_id=thread_id,
                    action=AuditAction.STORE,
                    source=f"thread-{thread_id}",
                    content_hash=f"hash-{thread_id}",
                )
                with lock:
                    results["success"] += 1
            except Exception as e:
                with lock:
                    results["errors"] += 1

        threads = [threading.Thread(target=write_audit, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert results["errors"] == 0, f"Got {results['errors']} errors from threads"
        assert results["success"] == 10, f"Expected 10 successes, got {results['success']}"

        # Verify all entries were written
        all_entries = mem.audit.query(limit=20)
        assert len(all_entries) == 10, f"Expected 10 entries, got {len(all_entries)}"
    finally:
        mem.close()
        os.unlink(db_path)
    print("✅ test_audit_trail_multithreaded")


def test_type_hints_present():
    """Verify key type hints are present on AuditTrail methods."""
    import inspect

    # Check log() signature
    log_sig = inspect.signature(AuditTrail.log)
    assert "memory_id" in log_sig.parameters
    assert log_sig.parameters["memory_id"].annotation == int
    assert log_sig.parameters["user_id"].annotation == str

    # Check query() return type
    query_sig = inspect.signature(AuditTrail.query)
    assert "user_id" in query_sig.parameters
    assert query_sig.parameters["limit"].annotation == int

    # Check stats() return type
    stats_sig = inspect.signature(AuditTrail.stats)
    assert "user_id" in stats_sig.parameters

    print("✅ test_type_hints_present")


if __name__ == "__main__":
    test_audit_trail_thread_local_reuse()
    test_audit_trail_close()
    test_runamemory_close_closes_audit()
    test_audit_stats_user_id()
    test_audit_entry_to_dict()
    test_audit_trail_multithreaded()
    test_type_hints_present()
    print("\nAll T8-5 tests PASSED! ⚙️")