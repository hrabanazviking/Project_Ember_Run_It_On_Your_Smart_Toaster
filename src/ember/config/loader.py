"""Public loader entry point: ``load_ember_config(config_root)``.

Per ADR 0008. Composes defaults → file → env into a populated
:class:`EmberConfig`. Never raises a generic exception — every failure
becomes an operator-readable :class:`ConfigError`.

File probe order, when ``config_root/config/`` is inspected:

1. ``ember.yaml`` (PyYAML required — operator gets a clear error if
   absent).
2. ``ember.toml`` (stdlib-only).
3. Neither present → use defaults.
4. **Both present** → YAML wins, a one-line warning is emitted via
   ``warnings.warn``.

Tests bypass the probe with ``file_override=`` and the env layer with
``skip_env=True``.
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path

from ember.config.overlay import apply_env_overrides
from ember.config.toml_loader import load_toml
from ember.config.validate import coerce_to_dataclass
from ember.config.yaml_loader import load_yaml
from ember.schemas.config import EmberConfig
from ember.schemas.errors import ConfigError

logger = logging.getLogger(__name__)


def load_ember_config(
    config_root: Path | None = None,
    *,
    file_override: Path | None = None,
    skip_env: bool = False,
) -> EmberConfig:
    """Load the operator's ``EmberConfig`` from disk + environment.

    Defaults are always the floor; file and env layers compose on top.
    """
    raw_dict = _read_file_or_defaults(config_root, file_override)
    config = coerce_to_dataclass(EmberConfig, raw_dict, path="")
    if skip_env:
        return config
    return apply_env_overrides(config)


def _read_file_or_defaults(
    config_root: Path | None, file_override: Path | None
) -> dict:
    """Locate the operator config file (if any) and return its raw dict."""
    if file_override is not None:
        return _read_by_suffix(file_override)

    if config_root is None:
        return {}

    config_dir = Path(config_root).expanduser() / "config"
    yaml_path = config_dir / "ember.yaml"
    toml_path = config_dir / "ember.toml"

    yaml_exists = yaml_path.is_file()
    toml_exists = toml_path.is_file()

    if yaml_exists and toml_exists:
        warnings.warn(
            f"Both {yaml_path} and {toml_path} exist; YAML wins. "
            "Remove the unused file to silence this warning.",
            stacklevel=2,
        )
        return _read_by_suffix(yaml_path)

    if yaml_exists:
        return _read_by_suffix(yaml_path)
    if toml_exists:
        return _read_by_suffix(toml_path)

    logger.debug("no operator config file at %s; using defaults", config_dir)
    return {}


def _read_by_suffix(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return load_yaml(path)
    if suffix == ".toml":
        return load_toml(path)
    raise ConfigError(
        f"{path}: unrecognised config file extension {suffix!r}. "
        f"Use .yaml or .toml."
    )


__all__ = ["load_ember_config"]
