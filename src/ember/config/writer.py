"""Minimal YAML writer for Hjarta's first-run config emission.

Per ADR 0008 §2.1-2.2: YAML is the primary operator format. But PyYAML
is an optional extra (`pip install ember-agent[config]`), and the
first-run experience must not require it — Hjarta writes the operator's
initial config file *before* the operator has any reason to install
extras.

This module hand-rolls the *very small* subset of YAML emission that
Hjarta needs: a header comment block, then top-level mappings of
string scalars, nested one level deep. No anchors, no flow style, no
multi-line strings beyond what fits a single line, no tag handling.
Anything richer than that is read by :mod:`yaml_loader` (which already
requires PyYAML).

If the operator later wants the loader to round-trip their config
through PyYAML's dumper for non-trivial edits, that's the operator
installing the extra. The write side stays stdlib-only.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping
from pathlib import Path

from ember.schemas.config import IdentityConfig
from ember.schemas.errors import ConfigError

_CONFIG_FILENAME = "ember.yaml"

_HEADER = """\
# Ember operator configuration.
#
# Written by Hjarta during first-run setup. Edit this file to change
# Ember's behaviour; changes take effect on the next `ember chat`.
#
# Only the keys you set need to be present — every absent key falls
# back to the default in `EmberConfig` (see `src/ember/schemas/config.py`).
#
# For the full schema with every supported key + comments, see:
#   https://github.com/hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster/blob/development/config/ember.example.yaml
#
# Environment variables (e.g. OLLAMA_HOST) and CLI flags override
# anything set here. See `ember --help` for the full overlay order.
"""


def ember_config_path(config_root: Path) -> Path:
    """Where the operator's ember.yaml lives under ``config_root``."""
    return Path(config_root).expanduser() / "config" / _CONFIG_FILENAME


def write_ember_config(
    config_root: Path,
    identity: IdentityConfig,
    *,
    extras: Mapping[str, Mapping[str, object]] | None = None,
) -> Path:
    """Atomically write Hjarta's initial ember.yaml.

    ``identity`` always appears. ``extras`` is a mapping of
    ``section_name -> {key: value}`` for any other top-level sections
    Hjarta needs to record from the wizard (e.g. an alternative Brunnr
    path). Values must be str / int / float / bool / None.

    Returns the written path.
    """
    target = ember_config_path(config_root)
    target.parent.mkdir(parents=True, exist_ok=True)

    body = _HEADER + "\n" + _format_identity(identity)
    if extras:
        for section, fields in extras.items():
            body += "\n" + _format_section(section, fields)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(target.parent),
        prefix=target.name,
        suffix=".tmp",
        delete=False,
    ) as tmp:
        tmp.write(body)
        tmp_path = Path(tmp.name)
    try:
        os.replace(tmp_path, target)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise ConfigError(
            f"could not write {target}: {exc}"
        ) from exc
    return target


def ember_config_exists(config_root: Path) -> bool:
    return ember_config_path(config_root).is_file()


# --------------------------------------------------------------------- #
# Internals                                                              #
# --------------------------------------------------------------------- #


def _format_identity(identity: IdentityConfig) -> str:
    return _format_section(
        "identity",
        {"name": identity.name, "role": identity.role},
    )


def _format_section(name: str, fields: Mapping[str, object]) -> str:
    lines = [f"{name}:"]
    for key, value in fields.items():
        lines.append(f"  {key}: {_format_scalar(value)}")
    return "\n".join(lines) + "\n"


def _format_scalar(value: object) -> str:
    """YAML 1.1-safe scalar emission for the values Hjarta writes."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return _quote_string(value)
    if isinstance(value, Path):
        return _quote_string(str(value))
    raise ConfigError(
        f"writer cannot emit value of type {type(value).__name__}: {value!r}"
    )


def _quote_string(value: str) -> str:
    """Always double-quote strings.

    Avoids YAML 1.1's surprise booleans (``yes``/``no``/``on``/``off``),
    avoids quoting decisions per character class, and lets operators
    see exactly what was written. Internal double-quotes are escaped.
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


__all__ = ["ember_config_exists", "ember_config_path", "write_ember_config"]
