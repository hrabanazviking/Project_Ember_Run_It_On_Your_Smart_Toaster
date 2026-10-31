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

E-032 (day-one friction, docket 88): the YAML preference had a trap —
the *loader* also needs PyYAML, so on an install carrying only the
documented ``[sqlite_vec]`` extra, Hjarta wrote an ``ember.yaml`` the
very next launch (and the first launch's own post-setup reload) could
not read back: every later ``ember`` invocation died with "PyYAML is
not installed". The writer now chooses by what the machine can read:
PyYAML importable → ``ember.yaml`` exactly as before; otherwise →
``ember.toml``, which the loader reads with the stdlib alone. The
operator's choices survive either way; the file format is the only
difference. (If an ``ember.yaml`` from an earlier, PyYAML-carrying
install is already present, the loader's YAML-wins rule still applies
to that file — the TOML fallback is written only when no YAML reader
exists on this machine, in which case a stale YAML file would already
have been unreadable.)
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


def _yaml_available() -> bool:
    """True when PyYAML can be imported on this machine (E-032 seam)."""
    try:
        import yaml  # noqa: PLC0415 — availability probe, not a use site

        del yaml
    except ImportError:
        return False
    return True


def write_ember_config(
    config_root: Path,
    identity: IdentityConfig,
    *,
    extras: Mapping[str, Mapping[str, object]] | None = None,
) -> Path:
    """Atomically write Hjarta's initial operator config.

    Writes ``ember.yaml`` when PyYAML is importable, else ``ember.toml``
    (stdlib-readable) — see the module docstring (E-032, docket 88).

    ``identity`` always appears. ``extras`` is a mapping of
    ``section_name -> {key: value}`` for any other top-level sections
    Hjarta needs to record from the wizard (e.g. an alternative Brunnr
    path). Values must be str / int / float / bool / None, or a nested
    mapping of the same one level deep (e.g. ``brunnr.sqlite_vec.path``).
    In the TOML fallback, ``None`` has no literal and is refused.

    Returns the written path.
    """
    yaml_ok = _yaml_available()
    target = ember_config_path(config_root)
    if not yaml_ok:
        target = target.with_suffix(".toml")
    target.parent.mkdir(parents=True, exist_ok=True)

    sections: list[tuple[str, Mapping[str, object]]] = [
        ("identity", {"name": identity.name, "role": identity.role})
    ]
    if extras:
        sections.extend(extras.items())
    if yaml_ok:
        body = _HEADER + "\n" + "".join(
            ("\n" if i else "") + _format_section(name, fields)
            for i, (name, fields) in enumerate(sections)
        )
    else:
        body = _HEADER + "\n" + _format_toml(sections)

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

    # Tighten mode to 0o600 BEFORE the atomic replace — the
    # NamedTemporaryFile default honours umask, which on many systems
    # is 0o022 (i.e. world-readable group + others). The operator's
    # ember.yaml never contains secrets, but it does carry the
    # identity name + tool config, which is operator-private. The
    # chmod is best-effort: on Windows the bits don't carry the same
    # meaning, and unusual filesystems may refuse chmod entirely.
    if os.name != "nt":
        import contextlib  # noqa: PLC0415 — narrowly scoped
        with contextlib.suppress(OSError):
            os.chmod(tmp_path, 0o600)

    try:
        os.replace(tmp_path, target)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise ConfigError(
            f"could not write {target}: {exc}"
        ) from exc
    return target


def ember_config_exists(config_root: Path) -> bool:
    yaml_path = ember_config_path(config_root)
    return yaml_path.is_file() or yaml_path.with_suffix(".toml").is_file()


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
        if isinstance(value, Mapping):
            lines.append(f"  {key}:")
            for sub_key, sub_value in value.items():
                lines.append(f"    {sub_key}: {_format_scalar(sub_value)}")
        else:
            lines.append(f"  {key}: {_format_scalar(value)}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- #
# TOML fallback emission (E-032 — stdlib-readable first-run config)     #
# --------------------------------------------------------------------- #


def _format_toml(sections: list[tuple[str, Mapping[str, object]]]) -> str:
    blocks: list[str] = []
    for name, fields in sections:
        lines = [f"[{name}]"]
        nested: list[tuple[str, Mapping[str, object]]] = []
        for key, value in fields.items():
            if isinstance(value, Mapping):
                nested.append((key, value))
            else:
                lines.append(f"{key} = {_format_toml_scalar(value)}")
        blocks.append("\n".join(lines) + "\n")
        for key, sub_fields in nested:
            sub = [f"[{name}.{key}]"]
            for sub_key, sub_value in sub_fields.items():
                sub.append(f"{sub_key} = {_format_toml_scalar(sub_value)}")
            blocks.append("\n".join(sub) + "\n")
    return "\n".join(blocks)


def _format_toml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return _quote_toml_string(value)
    if isinstance(value, Path):
        return _quote_toml_string(str(value))
    raise ConfigError(
        f"writer cannot emit value of type {type(value).__name__} "
        f"in the TOML fallback: {value!r}"
    )


def _quote_toml_string(value: str) -> str:
    """TOML basic-string emission: escape backslash, quote, controls."""
    out: list[str] = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append(f"\\u{ord(ch):04X}")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


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
