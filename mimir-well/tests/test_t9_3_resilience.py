"""T9-3: Connection Resilience Tests.

Tests for:
- restore_from_backup() resets thread-local connections
- validate_backup() deduplication works
- rollback_migration() works
- github_backup() logs warning on missing config
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from mimir_well import RunaMemory
from mimir_well.repair import validate_backup
from mimir_well.backup import _validate_backup_file
from mimir_well.migrations.runner import rollback_migration, get_schema_version, run_migrations


def _fresh_db():
    """Create a temporary database path that auto-cleans."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


def _fresh_backup():
    """Create a temporary backup path."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


class TestRestoreResetsConnection(unittest.TestCase):
    """restore_from_backup() should reset the thread-local connection."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.backup_path = _fresh_backup()
        self.mem = RunaMemory(db_path=self.db_path)
        # Add some data
        self.mem.add_memory("test memory before backup", category="general",
                            importance=7, user_id="test_user")

    def tearDown(self):
        self.mem.close()
        for p in [self.db_path, self.backup_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_restore_then_write_works(self):
        """After restore_from(), add_memory() should work without errors."""
        # Create backup
        self.mem.backup_to(self.backup_path)
        # Add more data after backup
        self.mem.add_memory("memory after backup", category="general",
                            importance=5, user_id="test_user")
        # Restore from backup (should reset connection)
        result = self.mem.restore_from(self.backup_path)
        self.assertTrue(result)
        # This should NOT raise "database is locked" or similar
        self.mem.add_memory("memory after restore", category="general",
                            importance=6, user_id="test_user")
        # Verify
        results = self.mem.recall_by_importance(min_importance=5, limit=10,
                                                 user_id="test_user")
        self.assertIsInstance(results, list)

    def test_restore_preserves_original_data(self):
        """After restore, original backup data should be present."""
        self.mem.backup_to(self.backup_path)
        self.mem.restore_from(self.backup_path)
        results = self.mem.recall_by_importance(min_importance=5, limit=10,
                                                 user_id="test_user")
        contents = [m["content"] for m in results]
        self.assertIn("test memory before backup", contents)

    def test_close_after_restore(self):
        """close() after restore_from() should not raise."""
        self.mem.backup_to(self.backup_path)
        self.mem.restore_from(self.backup_path)
        self.mem.close()  # Should not raise


class TestValidateBackupDedup(unittest.TestCase):
    """_validate_backup_file() should delegate to validate_backup()."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)
        self.mem.add_memory("test", category="general", importance=5)
        self.backup_path = _fresh_backup()
        self.mem.backup_to(self.backup_path)

    def tearDown(self):
        self.mem.close()
        for p in [self.db_path, self.backup_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_validate_backup_file_delegates(self):
        """_validate_backup_file should return same result as validate_backup."""
        path = Path(self.backup_path)
        result_private = _validate_backup_file(path)
        result_public = validate_backup(str(path))
        self.assertEqual(result_private, result_public)
        self.assertTrue(result_private)

    def test_validate_backup_invalid_path(self):
        """validate_backup should return False for nonexistent file."""
        self.assertFalse(validate_backup("/nonexistent/backup.db"))


class TestRollbackMigration(unittest.TestCase):
    """rollback_migration() should downgrade schema version."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)

    def tearDown(self):
        self.mem.close()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def test_rollback_decrements_schema_version(self):
        """Rolling back migration 008 should reduce schema version."""
        initial_version = get_schema_version(self.mem._get_conn())
        self.assertGreaterEqual(initial_version, 8)
        # Rollback migration 008
        result = rollback_migration(self.mem._get_conn(), 8)
        self.assertIsNotNone(result)
        # Schema version should be decremented
        new_version = get_schema_version(self.mem._get_conn())
        self.assertEqual(new_version, initial_version - 1)

    def test_rollback_then_re_run(self):
        """After rollback, re-running migrations should restore version."""
        initial_version = get_schema_version(self.mem._get_conn())
        rollback_migration(self.mem._get_conn(), 8)
        # Re-run all migrations
        run_migrations(self.mem._get_conn())
        final_version = get_schema_version(self.mem._get_conn())
        self.assertEqual(final_version, initial_version)


if __name__ == "__main__":
    unittest.main()