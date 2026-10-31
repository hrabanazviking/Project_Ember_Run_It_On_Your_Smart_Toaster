"""The Persona type — who the companion *is* (E-025).

Before E-025 the companion's whole identity was
:class:`ember.schemas.config.IdentityConfig` — a name and a role,
one per config root, loaded with no validation at all (see the
E-025 doc). A *persona* is the richer, named, loadable unit:

- ``id`` — the persona's stable slug. It is also its memory
  namespace: episodes are tagged with it (``Episode.persona_id``)
  and only a persona's own episodes may ride in its prompts.
- ``name`` / ``role`` — the display identity, the same two fields
  Hjarta's identity carries; :meth:`Persona.identity` projects a
  persona back onto that older shape so existing consumers keep
  working unchanged.
- ``description`` — plain words about who this persona is, for
  operator-facing surfaces (pickers, docs); it never enters the
  system prompt by itself.
- ``instructions`` — operator-authored lines that DO ride in the
  system prompt, after the name/role line and the honesty
  instruction (see ``ember.spark.funi.prompt``).

Validation lives here, in the schema layer, so every road in
(loader, config, tests) judges a persona by the same rules.
The rules are shaped by the adversarial fixtures in the E-025
tests: a persona file is data an operator (or a tool acting for
one) writes, and its fields land in the *system* prompt — so no
field may carry a line break or a control character into that
prompt, no field may be unbounded, and the ``id`` may never be
a path (a persona id is used to build a filename and a memory
namespace; ``../`` in it would be a traversal, not a name).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ember.schemas.config import IdentityConfig
from ember.schemas.errors import SchemaError

#: The persona every un-tagged episode and every pre-E-025
#: install belongs to. Episodes written before personas existed
#: carry this id, so the default persona's history is continuous
#: with the single-companion past instead of orphaned by E-025.
DEFAULT_PERSONA_ID = "default"

#: Field ceilings — tiny-hardware discipline applied to identity:
#: a persona is a paragraph, not a novel. The system prompt rides
#: in every turn's token budget (E-021), so persona text is capped
#: where it is defined, not discovered in the bill later.
MAX_NAME_CHARS = 80
MAX_ROLE_CHARS = 200
MAX_DESCRIPTION_CHARS = 500
MAX_INSTRUCTIONS_CHARS = 2000
MAX_PERSONA_ID_CHARS = 64

_PERSONA_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class Persona:
    """One companion persona, validated at construction.

    Construction raises :class:`SchemaError` naming every broken
    rule at once — a persona that cannot be stated plainly is
    refused, never silently repaired (a loader that quietly
    truncated a name would leave the operator talking to someone
    slightly different from who they wrote, with no signal).
    """

    id: str
    name: str
    role: str
    description: str = ""
    instructions: str = ""

    def __post_init__(self) -> None:
        issues = persona_issues(self)
        if issues:
            raise SchemaError(
                "invalid persona: " + "; ".join(issues)
            )

    @property
    def identity(self) -> IdentityConfig:
        """This persona in the pre-E-025 identity shape."""
        return IdentityConfig(name=self.name, role=self.role)

    @property
    def memory_namespace(self) -> str:
        """The memory namespace this persona's episodes live in."""
        return f"persona:{self.id}"


def persona_issues(persona: Persona) -> tuple[str, ...]:
    """Every validation rule ``persona`` breaks (empty = valid).

    Kept separate from :meth:`Persona.__post_init__` so loaders
    can report issues for a *candidate* mapping without first
    constructing the object the constructor would refuse.
    Values are read defensively (``getattr``) so a hand-built
    stand-in with non-string fields reports issues instead of
    raising a type error of its own.
    """
    issues: list[str] = []

    pid = getattr(persona, "id", None)
    if not isinstance(pid, str) or not pid:
        issues.append("id is required")
    elif len(pid) > MAX_PERSONA_ID_CHARS:
        issues.append(f"id exceeds {MAX_PERSONA_ID_CHARS} characters")
    elif not _PERSONA_ID_RE.match(pid):
        issues.append(
            "id must be a slug: lowercase letters, digits, '-' or "
            "'_', starting with a letter or digit (no path "
            "separators, no dots, no spaces)"
        )

    _check_text(issues, "name", getattr(persona, "name", None),
                MAX_NAME_CHARS, required=True)
    _check_text(issues, "role", getattr(persona, "role", None),
                MAX_ROLE_CHARS, required=True)
    _check_text(issues, "description",
                getattr(persona, "description", None),
                MAX_DESCRIPTION_CHARS, required=False)
    _check_text(issues, "instructions",
                getattr(persona, "instructions", None),
                MAX_INSTRUCTIONS_CHARS, required=False)
    return tuple(issues)


def _check_text(
    issues: list[str],
    field_name: str,
    value: object,
    max_chars: int,
    *,
    required: bool,
) -> None:
    if not isinstance(value, str):
        issues.append(f"{field_name} must be text")
        return
    if required and not value.strip():
        issues.append(f"{field_name} is required")
        return
    if len(value) > max_chars:
        issues.append(f"{field_name} exceeds {max_chars} characters")
    # A line break or control character in a field that lands in
    # the system prompt is a prompt-injection seam: it would let
    # persona *data* pose as a new prompt line with the system's
    # authority. Instructions are the one multi-line field, and
    # even they may not carry control characters other than the
    # line breaks their author wrote.
    if field_name == "instructions":
        bad = [c for c in value if ord(c) < 0x20 and c not in "\n\t"]
    else:
        bad = [c for c in value if ord(c) < 0x20 or ord(c) == 0x7F]
        if "\n" in value or "\r" in value:
            bad.append("\n")
    if bad:
        issues.append(
            f"{field_name} contains control characters or line "
            "breaks, which may not enter the system prompt"
        )


def is_valid_persona_id(value: object) -> bool:
    """True when ``value`` is a persona id the rules allow."""
    return (
        isinstance(value, str)
        and 0 < len(value) <= MAX_PERSONA_ID_CHARS
        and bool(_PERSONA_ID_RE.match(value))
    )


def default_persona(identity: IdentityConfig | None = None) -> Persona:
    """The default persona, projected from an identity.

    The single identity every pre-E-025 install carries becomes
    the ``default`` persona unchanged — same name, same role — so
    upgrading the shape never renames the companion.
    """
    base = identity if identity is not None else IdentityConfig()
    return Persona(id=DEFAULT_PERSONA_ID, name=base.name, role=base.role)


__all__ = [
    "DEFAULT_PERSONA_ID",
    "MAX_DESCRIPTION_CHARS",
    "MAX_INSTRUCTIONS_CHARS",
    "MAX_NAME_CHARS",
    "MAX_PERSONA_ID_CHARS",
    "MAX_ROLE_CHARS",
    "Persona",
    "default_persona",
    "is_valid_persona_id",
    "persona_issues",
]
