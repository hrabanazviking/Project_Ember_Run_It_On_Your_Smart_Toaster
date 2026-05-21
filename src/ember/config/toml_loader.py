"""TOML config-file reader.

Stdlib only — uses `tomllib` (Python 3.11+). The loader's TOML path is
zero-dependency and always available; PyYAML is opt-in.

Per ADR 0008 §2.1. TOML is the secondary operator-facing format; YAML
is primary. Both load through identical type-coercion downstream.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from ember.schemas.errors import ConfigError


def load_toml(path: Path) -> dict:
    """Parse a TOML config file into a plain dict.

    Raises :class:`ConfigError` with the file path and parse-error
    location on any tomllib failure.
    """
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except OSError as exc:
        raise ConfigError(f"{path}: cannot read file ({exc})") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path}: invalid TOML ({exc})") from exc

    if not isinstance(data, dict):
        raise ConfigError(
            f"{path}: top-level TOML value must be a table; got {type(data).__name__}"
        )
    return data


__all__ = ["load_toml"]
