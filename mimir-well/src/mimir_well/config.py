"""
Mímir's Well — Configuration Management
=========================================
Loads and validates configuration from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("mimir_well.config")

DEFAULT_CONFIG = {
    "db_path": "",
    "backup_dir": "",
    "max_backups": 7,
    "decay_half_life_days": 30,
    "consolidation_access_threshold": 3,
    "consolidation_lookback_days": 7,
    "access_log_retention_days": 90,
    "backup_repo": "",
    "backup_branch": "main",
    "strip_personal_on_backup": True,
    "wal_mode": True,
    "busy_timeout": 10000,
    "synchronous": "FULL",
}

CONFIG_FILENAME = "mimir-well-config.json"


class MimirConfig:
    """Configuration manager for Mímir's Well.

    Loads from ~/.mimir_well/mimir-well-config.json with sensible defaults.
    Environment variables override config values (MIMIR_DB_PATH, MIMIR_BACKUP_REPO).
    """

    def __init__(self, config_path: Optional[str] = None):
        self._data = dict(DEFAULT_CONFIG)
        self._config_path = Path(config_path) if config_path else self._default_config_path()
        self._load()

    @staticmethod
    def _default_config_path() -> Path:
        return Path.home() / ".mimir_well" / CONFIG_FILENAME

    def _load(self) -> None:
        """Load config from file, falling back to defaults."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r") as f:
                    user_config = json.load(f)
                self._data.update(user_config)
                logger.info("Loaded config from %s", self._config_path)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load config from %s: %s", self._config_path, e)
        else:
            # Create default config file — use O_EXCL to avoid races
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            import os
            try:
                # O_EXCL | O_CREAT = atomic create-only, fails if file exists
                fd = os.open(self._config_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                with os.fdopen(fd, "w") as f:
                    json.dump(self._data, f, indent=2)
                logger.info("Created default config at %s", self._config_path)
            except FileExistsError:
                # Another process created it first — load instead
                try:
                    with open(self._config_path, "r") as f:
                        user_config = json.load(f)
                    self._data.update(user_config)
                    logger.info("Config file appeared (race), loaded from %s", self._config_path)
                except (json.JSONDecodeError, OSError):
                    pass  # Corrupt or gone — use defaults
            except OSError as e:
                logger.warning("Could not create default config: %s", e)

        # Environment variable overrides
        import os
        if os.environ.get("MIMIR_DB_PATH"):
            self._data["db_path"] = os.environ.get("MIMIR_DB_PATH")
        if os.environ.get("MIMIR_BACKUP_REPO"):
            self._data["backup_repo"] = os.environ.get("MIMIR_BACKUP_REPO")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by key."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a config value and save to file."""
        self._data[key] = value
        self._save()

    def _save(self) -> None:
        """Persist config to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            logger.warning("Could not save config: %s", e)

    @property
    def db_path(self) -> Path:
        """Resolved database path."""
        raw = self._data.get("db_path", "")
        if raw:
            return Path(raw).expanduser()
        return Path.home() / ".mimir_well" / "mimir_well.db"

    @property
    def backup_dir(self) -> Path:
        """Resolved backup directory."""
        raw = self._data.get("backup_dir", "")
        if raw:
            return Path(raw).expanduser()
        return Path.home() / ".mimir_well" / "backups"

    def to_dict(self) -> Dict[str, Any]:
        """Return a copy of the current configuration."""
        return dict(self._data)