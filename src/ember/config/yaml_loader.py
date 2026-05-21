"""YAML config-file reader.

PyYAML is an optional extra (`pip install ember-agent[config]`). The
import is lazy and guarded — operators who never use YAML pay no cost,
and operators who try to use YAML without the extra installed get a
clear operator-readable error pointing at the fix.

Per ADR 0008 §2.1-2.2. YAML is the primary operator-facing format.
"""

from __future__ import annotations

from pathlib import Path

from ember.schemas.errors import ConfigError

_INSTALL_HINT = (
    "PyYAML is not installed. Either run `pip install ember-agent[config]` "
    "to enable YAML config, or rename your file to `ember.toml` "
    "(TOML is stdlib and always available)."
)


def load_yaml(path: Path) -> dict:
    """Parse a YAML config file into a plain dict.

    Raises :class:`ConfigError` on missing PyYAML, file read failure,
    YAML parse failure, or wrong top-level shape. Every error message
    names the file path.
    """
    try:
        import yaml  # noqa: PLC0415 — lazy import guards the optional dep
    except ImportError as exc:
        raise ConfigError(f"{path}: {_INSTALL_HINT}") from exc

    try:
        with path.open("rb") as fh:
            data = yaml.safe_load(fh)
    except OSError as exc:
        raise ConfigError(f"{path}: cannot read file ({exc})") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: invalid YAML ({exc})") from exc

    if data is None:
        # An empty file is legal — it means "use all defaults".
        return {}
    if not isinstance(data, dict):
        raise ConfigError(
            f"{path}: top-level YAML value must be a mapping; "
            f"got {type(data).__name__}"
        )
    return data


__all__ = ["load_yaml"]
