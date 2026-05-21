"""
Verðandi Paths — File-Location-Agnostic Path Resolution.

The Vegvísir (wayfinding) module. Finds its way on any system,
any deployment, any configuration. Never hardcoded. Always adapting.

Resolution order (highest priority first):
  1. VERDANDI_HOME environment variable
  2. XDG Base Directory specification
  3. ~/.hermes/state/ (current Hermes deployment)
  4. ./verdandi_state/ (development fallback)

Cross-platform support:
  - Linux (primary, especially Raspberry Pi)
  - macOS (~/Library/Application Support/Verdandi/)
  - Windows WSL (detected via WSL_DISTRO_NAME env var)
  - iOS (a-Shell, iSH — detected via platform)

All paths are resolved once at import time and cached.
Call reset_paths() to force re-resolution after env changes.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────
# Platform Detection
# ─────────────────────────────────────────────────────

def _is_wsl() -> bool:
    """Detect Windows Subsystem for Linux."""
    return bool(os.environ.get("WSL_DISTRO_NAME"))


def _is_macos() -> bool:
    """Detect macOS."""
    return sys.platform == "darwin"


def _is_ios() -> bool:
    """Detect iOS (iSH or a-Shell)."""
    # iSH sets this; a-Shell doesn't but runs on iPadOS
    return bool(os.environ.get("ISH_RUNTIME")) or "ish" in platform.platform().lower()


def _is_pi() -> bool:
    """Detect Raspberry Pi."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            model = f.read().lower()
        return "raspberry pi" in model
    except (FileNotFoundError, PermissionError):
        return False


def get_platform_info() -> dict:
    """Get detailed platform information."""
    info = {
        "system": sys.platform,
        "machine": platform.machine(),
        "is_wsl": _is_wsl(),
        "is_macos": _is_macos(),
        "is_ios": _is_ios(),
        "is_pi": _is_pi(),
        "is_linux": sys.platform.startswith("linux") and not _is_wsl(),
    }
    info["platform_name"] = (
        "pi" if info["is_pi"]
        else "wsl" if info["is_wsl"]
        else "macos" if info["is_macos"]
        else "ios" if info["is_ios"]
        else "linux" if info["is_linux"]
        else "unknown"
    )
    return info


# ─────────────────────────────────────────────────────
# Path Resolution — The Vegvísir
# ─────────────────────────────────────────────────────

_resolved: dict = {}


def _xdg_state_home() -> Path:
    """Get XDG state home directory."""
    xdg = os.environ.get("XDG_STATE_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".local" / "state"


def _xdg_config_home() -> Path:
    """Get XDG config home directory."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".config"


def _xdg_cache_home() -> Path:
    """Get XDG cache home directory."""
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".cache"


def _xdg_runtime_dir() -> Path:
    """Get XDG runtime directory."""
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        return Path(xdg)
    # Fallback: use /tmp for systems without XDG_RUNTIME_DIR
    return Path("/tmp") / f"verdandi-{os.getuid()}"


def resolve_paths() -> dict:
    """Resolve all paths according to priority order.
    
    Resolution order:
      1. VERDANDI_HOME env var — everything lives under this
      2. XDG Base Directory spec
      3. ~/.hermes/state/ — current Hermes deployment
      4. ./verdandi_state/ — development fallback
      
    Returns dict of resolved paths.
    """
    paths = {}
    pinfo = get_platform_info()
    
    # Priority 1: VERDANDI_HOME overrides everything
    verdandi_home = os.environ.get("VERDANDI_HOME")
    if verdandi_home:
        base = Path(verdandi_home)
        paths["state_dir"] = base
        paths["config_dir"] = base / "config"
        paths["log_dir"] = base / "logs"
        paths["pid_dir"] = base / "run"
        paths["socket_path"] = base / "run" / "verdandi.sock"
        paths["config_path"] = base / "config" / "heartbeat.yaml"
        paths["db_path"] = base / "verdandi_heartbeat.db"
        paths["pid_path"] = base / "run" / "verdandi-heartbeat.pid"
        paths["log_path"] = base / "logs" / "verdandi-heartbeat.log"
        paths["source"] = "VERDANDI_HOME"
        paths["base"] = base
        paths.update(pinfo)
        return paths
    
    # Priority 2: XDG Base Directory
    # Check if ~/.hermes/state exists (Priority 3 takes precedence over pure XDG)
    hermes_state = Path.home() / ".hermes" / "state"
    if hermes_state.exists():
        # Priority 3: existing Hermes deployment — this is the most common case
        paths["state_dir"] = hermes_state
        paths["config_dir"] = hermes_state / "config"
        paths["log_dir"] = hermes_state / "logs"
        paths["pid_dir"] = hermes_state / "run"
        paths["socket_path"] = hermes_state / "run" / "verdandi.sock"
        paths["config_path"] = hermes_state / "config" / "heartbeat.yaml"
        paths["db_path"] = hermes_state / "verdandi_heartbeat.db"
        paths["pid_path"] = hermes_state / "run" / "verdandi-heartbeat.pid"
        paths["log_path"] = hermes_state / "logs" / "verdandi-heartbeat.log"
        paths["source"] = "hermes_state"
        paths["base"] = hermes_state
        paths.update(pinfo)
        return paths
    
    # Priority 2: XDG directories (clean deployment, no Hermes)
    if pinfo["is_macos"]:
        # macOS: ~/Library/Application Support/Verdandi/
        app_support = Path.home() / "Library" / "Application Support" / "Verdandi"
        state_home = app_support / "state"
    elif pinfo["is_ios"]:
        # iOS: use app-accessible directories
        state_home = Path.home() / "Documents" / "Verdandi"
    else:
        # Linux/WSL/other: XDG
        state_home = _xdg_state_home() / "verdandi"
    
    config_home = _xdg_config_home() / "verdandi"
    runtime_dir = _xdg_runtime_dir()
    
    paths["state_dir"] = state_home
    paths["config_dir"] = config_home
    paths["log_dir"] = _xdg_cache_home() / "verdandi" / "logs"
    paths["pid_dir"] = runtime_dir
    paths["socket_path"] = runtime_dir / "verdandi.sock"
    paths["config_path"] = config_home / "heartbeat.yaml"
    paths["db_path"] = state_home / "verdandi_heartbeat.db"
    paths["pid_path"] = runtime_dir / "verdandi-heartbeat.pid"
    paths["log_path"] = _xdg_cache_home() / "verdandi" / "logs" / "verdandi-heartbeat.log"
    paths["source"] = "xdg"
    paths["base"] = state_home
    
    # Priority 4: development fallback — if XDG dirs don't exist
    dev_fallback = Path.cwd() / "verdandi_state"
    if not state_home.exists() and dev_fallback.exists():
        paths["state_dir"] = dev_fallback
        paths["config_dir"] = dev_fallback / "config"
        paths["log_dir"] = dev_fallback / "logs"
        paths["pid_dir"] = dev_fallback / "run"
        paths["socket_path"] = dev_fallback / "run" / "verdandi.sock"
        paths["config_path"] = dev_fallback / "config" / "heartbeat.yaml"
        paths["db_path"] = dev_fallback / "verdandi_heartbeat.db"
        paths["pid_path"] = dev_fallback / "run" / "verdandi-heartbeat.pid"
        paths["log_path"] = dev_fallback / "logs" / "verdandi-heartbeat.log"
        paths["source"] = "dev_fallback"
        paths["base"] = dev_fallback
    
    paths.update(pinfo)
    return paths


def reset_paths() -> None:
    """Force re-resolution of all paths. Call after env changes."""
    _resolved.clear()


def resolve_path(name: str) -> Path:
    """Resolve a single named path. Cached after first call.
    
    Valid names: state_dir, config_dir, log_dir, pid_dir,
                socket_path, config_path, db_path, pid_path, log_path, base
    """
    if not _resolved:
        _resolved.update(resolve_paths())
    if name not in _resolved:
        raise KeyError(f"Unknown path name: {name}. Valid: {list(_resolved.keys())}")
    p = _resolved[name]
    if isinstance(p, Path):
        return p
    return Path(p)


def ensure_dirs() -> None:
    """Create all directories that need to exist."""
    if not _resolved:
        _resolved.update(resolve_paths())
    for name in ("state_dir", "config_dir", "log_dir", "pid_dir"):
        path = _resolved[name] if isinstance(_resolved[name], Path) else Path(_resolved[name])
        path.mkdir(parents=True, exist_ok=True)


# Convenience functions (the main API)
def get_state_dir() -> Path:
    return resolve_path("state_dir")

def get_config_dir() -> Path:
    return resolve_path("config_dir")

def get_log_dir() -> Path:
    return resolve_path("log_dir")

def get_pid_dir() -> Path:
    return resolve_path("pid_dir")

def get_socket_path() -> Path:
    return resolve_path("socket_path")

def get_config_path() -> Path:
    return resolve_path("config_path")

def get_db_path() -> Path:
    return resolve_path("db_path")

def get_pid_path() -> Path:
    return resolve_path("pid_path")

def get_log_path() -> Path:
    return resolve_path("log_path")


# Initialize on import
_resolved.update(resolve_paths())