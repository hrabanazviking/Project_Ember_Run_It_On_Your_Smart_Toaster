"""
Verðandi Config — YAML Configuration with Environment Overrides.

Loads configuration from heartbeat.yaml, with environment variable overrides.
Config can be reloaded at runtime via SIGHUP.

Design principles:
  - Every setting has a sensible default
  - Environment variables override YAML: VERDANDI_<SECTION>_<KEY>
  - Config reload is safe (atomic swap)
  - Works without a config file at all (defaults only)
"""

import os
from pathlib import Path
from typing import Any, Optional
import copy

# Try to import yaml, fall back to a minimal parser
try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

from heartbeat.paths import get_config_path, ensure_dirs


# ─────────────────────────────────────────────────────
# Default Configuration — The Skeleton's DNA
# ─────────────────────────────────────────────────────

DEFAULTS: dict[str, Any] = {
    # Core heartbeat settings
    "heartbeat": {
        "interval_seconds": 60,           # How often to pulse (seconds)
        "jitter_seconds": 5,              # Add random jitter to prevent thundering herd
        "startup_delay_seconds": 10,      # Delay before first pulse after daemon start
        "max_pulse_time_seconds": 300,    # Timeout for a single pulse cycle
        "dedup_window_seconds": 300,       # Don't re-alert on same issue within this window
        "health_score_window": 100,       # EMA window for health score trending
    },

    # v0.3.0: Skuld — Prediction settings
    "prediction": {
        "enabled": True,                  # Enable Skuld predictive check
        "history_hours": 168,            # 7 days of history for predictions
        "anomaly_window": 50,             # Rolling window for anomaly detection
        "anomaly_threshold": 2.0,         # Z-score threshold for anomaly detection
        "capacity_warning_days": 30,      # Alert N days before resource exhaustion
        "capacity_critical_days": 7,       # Critical alert N days before exhaustion
    },

    # v0.3.0: Scheduled maintenance windows
    "maintenance": {
        "windows": [],                    # List of {"day": "sunday", "start": "02:00", "end": "06:00"}
        "suppress_actions": True,          # During window, suppress non-critical actions
        "suppress_checks": [],            # List of check names to skip during window
    },

    # v0.3.0: Prometheus metrics exporter
    "prometheus": {
        "enabled": False,                 # Set to True to enable /metrics endpoint
        "port": 9101,                     # Prometheus scrape port
        "host": "0.0.0.0",               # Bind address
    },
    
    # State machine thresholds
    "thresholds": {
        # Health check thresholds
        "cpu_temp_warning": 70,            # °C — degraded state
        "cpu_temp_critical": 80,           # °C — critical state
        "ram_warning_percent": 85,         # % — degraded state
        "ram_critical_percent": 95,        # % — critical state
        "disk_warning_percent": 80,        # % — degraded state
        "disk_critical_percent": 90,       # % — critical state
        
        # Service thresholds
        "service_restart_attempts": 3,     # How many times to try restarting a service
        "service_cooldown_minutes": 5,     # Wait between restart attempts
        
        # Project thresholds
        "unpushed_commits_warning": 5,    # Commits behind remote
        "unpushed_commits_critical": 20,   # Very far behind
        "stale_branch_days": 30,           # Days before branch is "stale"
    },
    
    # Which checks to enable
    "checks": {
        "health": True,                    # CPU temp, RAM, disk
        "projects": True,                   # Git repo scanning
        "memory": True,                     # Mímir DB health
        "schedule": True,                   # Cron job monitoring
        "conversation_log": True,           # Conversation log growth
    },
    
    # Project directories to watch
    "projects": {
        "auto_discover": True,              # Scan ~/ for git repos
        "watch_paths": [],                  # Explicit paths to watch
        "ignore_paths": [],                 # Paths to skip
    },
    
    # Recovery actions — what to do when problems are found
    "recovery": {
        "auto_push": True,                  # Auto-push unpushed commits
        "auto_restart_services": False,     # Auto-restart failed services (conservative)
        "auto_cleanup_logs": True,          # Trim oversized log files
        "auto_vacuum_db": True,             # Vacuum SQLite databases periodically
        "max_log_size_mb": 50,              # Trim logs above this size
    },
    
    # Nerve system integration
    "nerve": {
        "publish_pulses": True,             # Send every pulse to nerve hub
        "publish_alerts": True,             # Send alerts to nerve hub
        "socket_path": "",                  # Empty = use default from paths
        "fallback_to_file": True,           # If socket unavailable, write to file
    },
    
    # Reactor integration
    "reactor": {
        "run_on_degraded": True,            # Run reactor when state degrades
        "run_on_critical": True,             # Run reactor in critical state
        "reactor_path": "",                 # Empty = use default from paths
    },
    
    # Logging
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "file_max_bytes": 10 * 1024 * 1024,  # 10MB
        "file_backup_count": 5,
        "also_log_to_stderr": True,         # For systemd/journal
    },
    
    # Pi-specific optimizations
    "pi": {
        "reduce_io_on_low_memory": True,     # Skip disk-heavy checks if RAM is low
        "thermal_throttle_interval": 30,     # Check CPU temp every 30s instead of every pulse
        "sd_card_friendly": True,            # Minimize writes to SD card
    },
}


class HeartbeatConfig:
    """Configuration loader with env overrides and hot reload.
    
    Usage:
        config = HeartbeatConfig()          # Load from default locations
        config = HeartbeatConfig(path)      # Load from specific path
        config.reload()                      # Reload from disk (for SIGHUP)
        config.get("heartbeat.interval_seconds")  # Dot-notation access
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path or get_config_path()
        self._raw: dict[str, Any] = {}
        self._config: dict[str, Any] = {}
        self._env_overrides: dict[str, Any] = {}
        self._loaded = False
        self.load()
    
    def load(self) -> None:
        """Load configuration from file and apply overrides."""
        # Start with defaults (deep copy)
        self._config = copy.deepcopy(DEFAULTS)
        
        # Load YAML if available
        if self._config_path and self._config_path.exists():
            self._load_yaml()
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        self._loaded = True
    
    def _load_yaml(self) -> None:
        """Load and merge YAML config file."""
        if not _HAS_YAML:
            # Minimal YAML-like parsing for key sections
            self._load_yaml_minimal()
            return
        
        try:
            with open(self._config_path) as f:
                file_config = yaml.safe_load(f) or {}
            self._raw = file_config
            self._deep_merge(self._config, file_config)
        except Exception as e:
            # Config file errors are non-fatal — use defaults
            import logging
            logging.getLogger("verdandi.config").warning(f"Config load error: {e}, using defaults")
    
    def _load_yaml_minimal(self) -> None:
        """Minimal YAML-like config parser for systems without PyYAML."""
        try:
            with open(self._config_path) as f:
                # Very simple key: value parser for flat sections
                current_section = None
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.endswith(":") and not line.startswith("-"):
                        current_section = line.rstrip(":").strip()
                        continue
                    if ":" in line and current_section:
                        key, _, value = line.partition(":")
                        key = key.strip()
                        value = value.strip()
                        # Type conversion
                        if value.lower() in ("true", "yes"):
                            value = True
                        elif value.lower() in ("false", "no"):
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        elif "." in value:
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                        if current_section in self._config and key in self._config[current_section]:
                            self._config[current_section][key] = value
        except Exception:
            pass  # Non-fatal
    
    def _apply_env_overrides(self) -> None:
        """Apply VERDANDI_<SECTION>_<KEY> environment variable overrides.
        
        Example: VERDANDI_HEARTBEAT_INTERVAL_SECONDS=30 overrides
                 heartbeat.interval_seconds in config.
        """
        prefix = "VERDANDI_"
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            
            # Convert VERDANDI_HEARTBEAT_INTERVAL_SECONDS -> heartbeat.interval_seconds
            config_key = key[len(prefix):].lower()
            parts = config_key.split("_")
            
            # Try to match: first part is section, rest is key
            if len(parts) >= 2:
                section = parts[0]
                subkey = "_".join(parts[1:])
                
                if section in self._config:
                    if subkey in self._config[section]:
                        # Convert string value to appropriate type
                        current = self._config[section][subkey]
                        if isinstance(current, bool):
                            self._config[section][subkey] = value.lower() in ("true", "yes", "1")
                        elif isinstance(current, int):
                            try:
                                self._config[section][subkey] = int(value)
                            except ValueError:
                                pass
                        elif isinstance(current, float):
                            try:
                                self._config[section][subkey] = float(value)
                            except ValueError:
                                pass
                        else:
                            self._config[section][subkey] = value
                        self._env_overrides[key] = value
    
    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge override into base (in-place)."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                HeartbeatConfig._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def reload(self) -> None:
        """Reload configuration from disk. Safe to call from signal handler."""
        self._env_overrides.clear()
        self.load()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation.
        
        Example: config.get("heartbeat.interval_seconds") -> 60
        """
        parts = key.split(".")
        current = self._config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def set(self, key: str, value: Any) -> None:
        """Set a config value using dot notation (runtime only, not persisted)."""
        parts = key.split(".")
        current = self._config
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    
    @property
    def all(self) -> dict:
        """Return the full configuration dictionary."""
        return copy.deepcopy(self._config)
    
    @property
    def config_path(self) -> Path:
        """Return the path to the config file."""
        return self._config_path
    
    def __repr__(self) -> str:
        source = "env_override" if self._env_overrides else ("file" if self._raw else "defaults")
        return f"HeartbeatConfig(source={source}, path={self._config_path})"