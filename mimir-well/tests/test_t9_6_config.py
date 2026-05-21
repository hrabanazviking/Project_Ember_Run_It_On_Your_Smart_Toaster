"""T9-6: Config & Polish Tests.

Tests for MimirConfig: loading, defaults, env overrides, set/get, to_dict,
db_path, backup_dir, race-free creation.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from mimir_well.config import MimirConfig, DEFAULT_CONFIG


class TestMimirConfigDefaults(unittest.TestCase):
    """Default configuration values."""

    def test_default_config_has_db_path(self):
        self.assertIn("db_path", DEFAULT_CONFIG)

    def test_default_config_has_decay_half_life(self):
        self.assertIn("decay_half_life_days", DEFAULT_CONFIG)

    def test_default_config_has_consolidation_access_threshold(self):
        self.assertIn("consolidation_access_threshold", DEFAULT_CONFIG)


class TestMimirConfigCreation(unittest.TestCase):
    """Config creation and file handling."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "test-config.json")

    def tearDown(self):
        try:
            os.unlink(self.config_path)
        except OSError:
            pass
        try:
            os.rmdir(self.tmpdir)
        except OSError:
            pass

    def test_creates_default_config_file(self):
        config = MimirConfig(config_path=self.config_path)
        self.assertTrue(Path(self.config_path).exists())

    def test_loads_existing_config(self):
        # Write a config file first
        with open(self.config_path, "w") as f:
            json.dump({"db_path": "/custom/path.db"}, f)
        config = MimirConfig(config_path=self.config_path)
        self.assertEqual(config.get("db_path"), "/custom/path.db")

    def test_handles_invalid_json(self):
        # Write invalid JSON
        with open(self.config_path, "w") as f:
            f.write("{invalid json!!!")
        config = MimirConfig(config_path=self.config_path)
        # Should fall back to defaults
        self.assertIsNotNone(config.get("decay_half_life_days"))


class TestMimirConfigGetSet(unittest.TestCase):
    """get/set operations."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "test-config.json")

    def tearDown(self):
        try:
            os.unlink(self.config_path)
        except OSError:
            pass
        try:
            os.rmdir(self.tmpdir)
        except OSError:
            pass

    def test_get_returns_default(self):
        config = MimirConfig(config_path=self.config_path)
        self.assertEqual(config.get("nonexistent_key", "fallback"), "fallback")

    def test_set_persists_value(self):
        config = MimirConfig(config_path=self.config_path)
        config.set("decay_interval_hours", 2)
        self.assertEqual(config.get("decay_interval_hours"), 2)
        # Reload from file to verify persistence
        config2 = MimirConfig(config_path=self.config_path)
        self.assertEqual(config2.get("decay_interval_hours"), 2)

    def test_set_new_key(self):
        config = MimirConfig(config_path=self.config_path)
        config.set("custom_key", "custom_value")
        self.assertEqual(config.get("custom_key"), "custom_value")

    def test_to_dict_returns_copy(self):
        config = MimirConfig(config_path=self.config_path)
        d = config.to_dict()
        self.assertIsInstance(d, dict)
        # Modifying the dict should not affect config
        d["test"] = "modified"
        self.assertIsNone(config.get("test"))


class TestMimirConfigProperties(unittest.TestCase):
    """Property accessors: db_path, backup_dir."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "test-config.json")

    def tearDown(self):
        try:
            os.unlink(self.config_path)
        except OSError:
            pass
        try:
            os.rmdir(self.tmpdir)
        except OSError:
            pass

    def test_db_path_default(self):
        config = MimirConfig(config_path=self.config_path)
        self.assertIsInstance(config.db_path, Path)

    def test_db_path_custom(self):
        config = MimirConfig(config_path=self.config_path)
        config.set("db_path", "/tmp/custom.db")
        self.assertEqual(config.db_path, Path("/tmp/custom.db"))

    def test_db_path_expanduser(self):
        config = MimirConfig(config_path=self.config_path)
        config.set("db_path", "~/custom.db")
        self.assertNotIn("~", str(config.db_path))

    def test_backup_dir_default(self):
        config = MimirConfig(config_path=self.config_path)
        self.assertIsInstance(config.backup_dir, Path)

    def test_backup_dir_custom(self):
        config = MimirConfig(config_path=self.config_path)
        config.set("backup_dir", "/tmp/backups")
        self.assertEqual(config.backup_dir, Path("/tmp/backups"))


class TestMimirConfigEnvOverrides(unittest.TestCase):
    """Environment variable overrides."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "test-config.json")
        # Save current env
        self._saved_db = os.environ.pop("MIMIR_DB_PATH", None)
        self._saved_repo = os.environ.pop("MIMIR_BACKUP_REPO", None)

    def tearDown(self):
        # Restore env
        if self._saved_db is not None:
            os.environ["MIMIR_DB_PATH"] = self._saved_db
        elif "MIMIR_DB_PATH" in os.environ:
            del os.environ["MIMIR_DB_PATH"]
        if self._saved_repo is not None:
            os.environ["MIMIR_BACKUP_REPO"] = self._saved_repo
        elif "MIMIR_BACKUP_REPO" in os.environ:
            del os.environ["MIMIR_BACKUP_REPO"]
        try:
            os.unlink(self.config_path)
        except OSError:
            pass
        try:
            os.rmdir(self.tmpdir)
        except OSError:
            pass

    def test_env_override_db_path(self):
        os.environ["MIMIR_DB_PATH"] = "/env/override.db"
        config = MimirConfig(config_path=self.config_path)
        self.assertEqual(config.get("db_path"), "/env/override.db")

    def test_env_override_backup_repo(self):
        os.environ["MIMIR_BACKUP_REPO"] = "https://github.com/test/repo"
        config = MimirConfig(config_path=self.config_path)
        self.assertEqual(config.get("backup_repo"), "https://github.com/test/repo")


if __name__ == "__main__":
    unittest.main()