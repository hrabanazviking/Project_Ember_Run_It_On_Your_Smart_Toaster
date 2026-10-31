"""Persona loading, saving, and per-persona memory separation.

Personae live at ``<config_root>/personas/<id>.json`` — one plain
JSON file per persona, so stdlib alone handles them and an operator
can read (or hand-write) a persona with any text editor. The shape
mirrors Hjarta's identity discipline (E-020): small files, written
atomically, living inside the one config root that *is* the person
tether — custody of the folder is custody of every persona in it.

Loading is strict, on purpose:

- a file that is not a JSON object, names unknown fields, or
  breaks any :func:`ember.schemas.persona.persona_issues` rule
  raises :class:`PersonaError` naming the problem — never a
  silently defaulted or repaired persona (error honesty, ahead of
  its Part II home at E-030, applied here because a mis-loaded
  persona is exactly the kind of quiet substitution E-030 bans);
- the filename and the ``id`` inside it must agree: a file claiming
  another persona's id would make the on-disk listing lie about
  who is who, so it is refused, not resolved by fiat;
- ``persona_id`` arguments are validated as slugs before they ever
  touch a path — ``../identity`` is refused as an id, never joined
  into a filesystem path.

Memory separation is the other half of the core. An episode only
belongs to the persona named in its ``persona_id`` tag;
:func:`episodes_for_persona` is the filter every consumer uses,
and ``ember.spark.funi.prompt.assemble`` applies the same rule at
the prompt boundary, so a caller that forgets to filter still
cannot leak one persona's conversation into another's turn.
"""

from __future__ import annotations

import dataclasses
import json
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

from ember.schemas.episode import Episode
from ember.schemas.errors import SparkError
from ember.schemas.persona import (
    DEFAULT_PERSONA_ID,
    Persona,
    default_persona,
    is_valid_persona_id,
    persona_issues,
)
from ember.spark.hjarta.identity import load_identity

_PERSONAS_DIRNAME = "personas"
_KNOWN_FIELDS = frozenset({"id", "name", "role", "description", "instructions"})


class PersonaError(SparkError):
    """A persona could not be loaded, saved, or resolved."""


def persona_dir(config_root: Path) -> Path:
    return Path(config_root).expanduser() / _PERSONAS_DIRNAME


def persona_path(config_root: Path, persona_id: str) -> Path:
    """The file for ``persona_id`` — the id is slug-checked first.

    A non-slug id (path separators, dots, traversal) raises
    :class:`PersonaError` instead of being joined into a path, so
    no caller can be talked into reading outside the personas dir
    by an adversarial id (fixture-proven in the E-025 tests).
    """
    _require_slug(persona_id)
    return persona_dir(config_root) / f"{persona_id}.json"


def list_persona_ids(config_root: Path) -> tuple[str, ...]:
    """Every persona id with a file on disk, sorted.

    Files whose stem is not a slug are skipped (they cannot be a
    loadable persona; listing one would offer an id that
    :func:`load_persona` then refuses). A missing personas dir is
    an empty listing, not an error — most installs have none yet.
    """
    directory = persona_dir(config_root)
    if not directory.is_dir():
        return ()
    return tuple(
        sorted(
            entry.stem
            for entry in directory.iterdir()
            if entry.is_file()
            and entry.suffix == ".json"
            and is_valid_persona_id(entry.stem)
        )
    )


def load_persona(config_root: Path, persona_id: str) -> Persona:
    """Load and validate one persona by id.

    Raises :class:`PersonaError` when the file is absent, unreadable,
    malformed, or invalid — the caller decides what a missing
    persona means; this loader never invents one.
    """
    path = persona_path(config_root, persona_id)
    if not path.is_file():
        raise PersonaError(f"no persona {persona_id!r} at {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PersonaError(f"could not read persona at {path}: {exc}") from exc
    return persona_from_payload(payload, source=str(path), expected_id=persona_id)


def persona_from_payload(
    payload: object,
    *,
    source: str,
    expected_id: str | None = None,
) -> Persona:
    """Build a validated Persona from a decoded JSON payload."""
    if not isinstance(payload, dict):
        raise PersonaError(
            f"persona at {source} must be a JSON object, "
            f"got {type(payload).__name__}"
        )
    unknown = sorted(set(payload) - _KNOWN_FIELDS)
    if unknown:
        raise PersonaError(
            f"persona at {source} names unknown field(s) {unknown}; "
            f"known fields are {sorted(_KNOWN_FIELDS)}"
        )
    candidate = Persona.__new__(Persona)
    for name in ("id", "name", "role", "description", "instructions"):
        object.__setattr__(candidate, name, payload.get(name, ""))
    issues = persona_issues(candidate)
    if issues:
        raise PersonaError(
            f"persona at {source} is invalid: " + "; ".join(issues)
        )
    if expected_id is not None and candidate.id != expected_id:
        raise PersonaError(
            f"persona at {source} claims id {candidate.id!r} but was "
            f"loaded as {expected_id!r}; the filename and the id "
            "inside it must agree"
        )
    return candidate


def save_persona_atomic(config_root: Path, persona: Persona) -> Path:
    """Write ``persona`` to its file atomically (Hjarta's shape).

    Validation already ran at construction; this re-checks via
    :func:`persona_issues` because a frozen dataclass can still be
    assembled by hand around its constructor. On any failure the
    destination is left unchanged.
    """
    issues = persona_issues(persona)
    if issues:
        raise PersonaError("refusing to save invalid persona: " + "; ".join(issues))
    target = persona_path(config_root, persona.id)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        dataclasses.asdict(persona),
        ensure_ascii=False,
        indent=2,
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(target.parent),
        prefix=target.name,
        suffix=".tmp",
        delete=False,
    ) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)
    try:
        os.replace(tmp_path, target)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise PersonaError(f"could not write persona at {target}: {exc}") from exc
    return target


def resolve_persona(
    config_root: Path,
    persona_id: str | None = None,
) -> Persona:
    """Resolve the persona a session should run as.

    Order: an explicit ``persona_id`` wins and must load (a named
    persona that cannot load is an error, never a silent fall-back
    to someone else); otherwise a ``default.json`` persona file,
    when one exists, is the operator's chosen default; otherwise
    the pre-E-025 identity projects onto the default persona, so
    an install with no persona files keeps exactly the companion
    it already had.
    """
    if persona_id is not None:
        return load_persona(config_root, persona_id)
    if persona_path(config_root, DEFAULT_PERSONA_ID).is_file():
        return load_persona(config_root, DEFAULT_PERSONA_ID)
    return default_persona(load_identity(config_root))


# --------------------------------------------------------------------- #
# Memory separation                                                    #
# --------------------------------------------------------------------- #


def tag_episode(episode: Episode, persona_id: str) -> Episode:
    """A copy of ``episode`` tagged as ``persona_id``'s memory."""
    _require_slug(persona_id)
    return dataclasses.replace(episode, persona_id=persona_id)


def episodes_for_persona(
    episodes: Sequence[Episode],
    persona_id: str,
) -> list[Episode]:
    """Only ``persona_id``'s episodes, in their original order.

    The separation rule in one place: an episode belongs to exactly
    the persona its tag names — no prefix matching, no shared
    "close enough" namespaces, no default-persona leakage into a
    named persona or the reverse.
    """
    _require_slug(persona_id)
    return [ep for ep in episodes if ep.persona_id == persona_id]


# --------------------------------------------------------------------- #
# Internals                                                            #
# --------------------------------------------------------------------- #


def _require_slug(persona_id: str) -> None:
    if not is_valid_persona_id(persona_id):
        raise PersonaError(
            f"persona id {persona_id!r} is not a valid slug; ids are "
            "lowercase letters, digits, '-' or '_', starting with a "
            "letter or digit — never a path"
        )


__all__ = [
    "PersonaError",
    "episodes_for_persona",
    "list_persona_ids",
    "load_persona",
    "persona_dir",
    "persona_from_payload",
    "persona_path",
    "resolve_persona",
    "save_persona_atomic",
    "tag_episode",
]
