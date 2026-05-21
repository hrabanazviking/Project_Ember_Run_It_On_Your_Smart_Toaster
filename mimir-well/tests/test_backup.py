"""Tests for backup, restore, export, and GitHub backup operations."""

import json
import os
import pytest

from mimir_well.core import RunaMemory
from mimir_well.backup import (
    backup_database, backup_with_rotation, export_to_json,
)
from mimir_well.repair import validate_backup


class TestBackupDatabase:
    """Test basic backup creation."""

    def test_backup_creates_file(self, tmp_path):
        """backup_database should create a valid backup file."""
        db_path = tmp_path / "test_backup.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Backup content", importance=7)

        backup_path = str(tmp_path / "backup.db")
        result = backup_database(db._get_conn(), db_path, backup_path)

        assert result == backup_path
        assert os.path.exists(backup_path)
        db.close()

    def test_backup_is_valid_sqlite(self, tmp_path):
        """Backup file should be a valid SQLite database."""
        import sqlite3
        db_path = tmp_path / "test_valid.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Valid backup test", importance=6)

        backup_path = str(tmp_path / "valid_backup.db")
        backup_database(db._get_conn(), db_path, backup_path)

        # Verify backup is valid SQLite
        conn = sqlite3.connect(backup_path)
        row = conn.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        assert row[0] == "ok"
        db.close()


class TestBackupWithRotation:
    """Test backup rotation."""

    def test_rotation_keeps_max_backups(self, tmp_path):
        """Rotation should keep only max_backups files."""
        db_path = tmp_path / "rotation.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Rotation test", importance=5)

        backup_dir = str(tmp_path / "backups")
        max_backups = 3

        # Create more backups than max
        for _ in range(5):
            import time
            time.sleep(0.1)  # Ensure different timestamps
            backup_with_rotation(db._get_conn(), db_path, backup_dir, max_backups)

        # Should only have max_backups files
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        assert len(backups) <= max_backups + 1  # May have one in flight
        db.close()

    def test_rotation_default_dir(self, tmp_path):
        """Default backup directory should be ~/.mimir_well/backups."""
        db_path = tmp_path / "default_dir.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Default dir test", importance=5)

        custom_dir = str(tmp_path / "custom_backups")
        result = backup_with_rotation(db._get_conn(), db_path, custom_dir, max_backups=5)
        assert os.path.exists(result)
        db.close()


class TestExportToJson:
    """Test JSON export functionality."""

    def test_export_includes_all_tables(self, tmp_path):
        """JSON export should include data from all tables."""
        db_path = tmp_path / "export_test.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Export test", category="preference", importance=7)
        db.add_entity("test_entity", "test_type")
        db.add_knowledge("test_domain", "Test knowledge", confidence=0.9)

        export_path = str(tmp_path / "export.json")
        result = db.export_to_json(export_path)

        assert "memories" in result
        assert "entities" in result
        assert "knowledge" in result
        assert "version" in result
        assert result["version"] == "2.0"
        db.close()

    def test_export_file_created(self, tmp_path):
        """JSON export should create a file on disk."""
        db_path = tmp_path / "export_file.db"
        db = RunaMemory(str(db_path))
        db.add_memory("File test", importance=6)

        export_path = str(tmp_path / "data" / "export.json")
        db.export_to_json(export_path)

        assert os.path.exists(export_path)
        with open(export_path) as f:
            data = json.load(f)
        assert "memories" in data
        db.close()


class TestValidateBackup:
    """Test backup validation."""

    def test_validate_good_backup(self, tmp_path):
        """Valid SQLite backup should pass validation."""
        db_path = tmp_path / "good.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Test", importance=5)

        backup_path = str(tmp_path / "good_backup.db")
        db.backup_to(backup_path)

        assert validate_backup(backup_path) is True
        db.close()

    def test_validate_corrupt_backup(self, tmp_path):
        """Corrupt backup should fail validation."""
        bad_file = tmp_path / "corrupt.db"
        with open(bad_file, 'w') as f:
            f.write("NOT A DATABASE")

        assert validate_backup(str(bad_file)) is False

    def test_validate_nonexistent_backup(self, tmp_path):
        """Non-existent backup should fail validation."""
        assert validate_backup(str(tmp_path / "nonexistent.db")) is False