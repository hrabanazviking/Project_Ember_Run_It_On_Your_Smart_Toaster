"""Core API freeze v1 — the library shape members bind to (E-037).

Before E-037 the core's public surface was real but scattered:
a curated ``__all__`` in some subpackages, empty ``__init__``
files in others, and no version a member could check before
binding. Parts IV–X of the roadmap bind members (Verdandi,
memory, Kista, the engines, the bridges) to this core, so the
shape they bind to is now frozen, in one place, as **API v1**:

- ``API_VERSION`` is ``"1.0.0"``. It is deliberately separate
  from the package version (``ember.__version__``, still
  ``0.2.0``): the package may gain operator features without
  moving the library contract, and the contract may only move
  by the rules below.
- :data:`API_V1` lists every frozen name. A name is frozen at
  the dotted path listed here — that module path plus that
  attribute. Within major version 1 a frozen name is never
  removed, renamed, or given an incompatible signature;
  additions land as a minor bump, fixes as a patch bump, and
  only a major bump may break a frozen name.
- The ``ember.schemas.*`` modules are frozen as module
  surfaces: every name in each module's ``__all__`` is part of
  v1 at its module path (:data:`SCHEMA_MODULES`). The schemas
  package ``__init__`` deliberately re-exports nothing (its
  pre-freeze shape); members import schemas from their modules.
- Everything not listed is **not frozen**: the CLI and its
  text, the concrete backend adapters (``OllamaFuni``,
  ``AesirFuni``, ``SqliteVecBrunnr``, ``PgVectorBrunnr`` —
  reached through the frozen ``open()`` registries, never
  imported by members), and the ``cli`` / ``mcp`` / ``munnr`` /
  ``hjarta`` / ``smidja`` internals. Those may change in any
  release; a member that imports them binds at its own risk.
- Members keep their own config files (docket 56, member
  half): the one-config-surface law (E-033) binds the core's
  operator config. A member binds by loading an
  :class:`~ember.schemas.config.EmberConfig` through the
  frozen config loader and opening handles from its
  sub-configs — never by reading ``ember.yaml`` itself and
  never by sharing the core's config shape with its own.

This module imports only the standard library at module level.
:func:`verify_api_surface` imports the frozen modules lazily,
so importing ``ember.api`` can never pull an optional extra
(or a member) into a process that only wants the version.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass

#: The frozen core library API version (E-037). Semver: the
#: major number is the compatibility promise — see the module
#: docstring. Distinct from ``ember.__version__`` (the package).
API_VERSION = "1.0.0"

#: The major component of :data:`API_VERSION`, for members that
#: only need the integer (the ThoughtForge binding's shape).
API_MAJOR = 1


@dataclass(frozen=True, slots=True)
class ApiEntry:
    """One frozen name in API v1.

    ``module`` is the dotted module the name lives in and
    ``attribute`` the name itself; the frozen path a member
    binds to is ``f"{module}.{attribute}"``. ``kind`` is one of
    ``"function"``, ``"class"``, ``"protocol"``, ``"data"`` —
    a plain label for readers, not a promise the type system
    checks.
    """

    module: str
    attribute: str
    kind: str

    @property
    def path(self) -> str:
        """The full dotted path of the frozen name."""
        return f"{self.module}.{self.attribute}"


def _entries(module: str, kind: str, *attributes: str) -> tuple[ApiEntry, ...]:
    return tuple(ApiEntry(module=module, attribute=name, kind=kind) for name in attributes)


#: Schema modules frozen as whole surfaces (E-037): every name
#: in each module's ``__all__`` is API v1 at its module path.
SCHEMA_MODULES: tuple[str, ...] = (
    "ember.schemas.chunks",
    "ember.schemas.cognition",
    "ember.schemas.config",
    "ember.schemas.conversation",
    "ember.schemas.episode",
    "ember.schemas.errors",
    "ember.schemas.funi",
    "ember.schemas.ingest",
    "ember.schemas.persona",
    "ember.schemas.stream",
    "ember.schemas.thread",
    "ember.schemas.tool",
)

#: Every individually frozen name in API v1, grouped by the
#: surface a member binds through. The schema modules above are
#: frozen wholesale and are not repeated name by name here.
API_V1: tuple[ApiEntry, ...] = (
    # The version itself — a member checks before it binds.
    *_entries("ember", "data", "__version__", "API_VERSION"),
    *_entries("ember.api", "data", "API_MAJOR", "API_VERSION"),
    *_entries("ember.api", "class", "ApiEntry"),
    *_entries("ember.api", "function", "api_manifest", "is_api_compatible", "verify_api_surface"),
    # Config: the one surface (E-033), loaded — never parsed —
    # by members.
    *_entries(
        "ember.config",
        "function",
        "ember_config_exists",
        "ember_config_path",
        "load_ember_config",
        "write_ember_config",
    ),
    *_entries("ember.config", "class", "ConfigError"),
    # Funi: the model handle + its backend contract (E-022).
    *_entries("ember.spark.funi", "protocol", "FuniHandle"),
    *_entries("ember.spark.funi", "function", "open"),
    *_entries(
        "ember.spark.funi.handle",
        "function",
        "backend_registry",
        "capabilities_for",
        "wrap_complete_as_stream",
    ),
    *_entries("ember.spark.funi.handle", "class", "BackendRegistration"),
    *_entries("ember.spark.funi.handle", "protocol", "FuniHandle"),
    # Determinism judgement (E-036) — benchmarks bind here.
    *_entries(
        "ember.spark.funi.determinism",
        "function",
        "determinism_error",
        "effective_options",
        "is_deterministic",
    ),
    *_entries("ember.spark.funi.determinism", "data", "DETERMINISTIC_TEMPERATURE"),
    # Conversation windowing + the summariser hook (E-021).
    *_entries(
        "ember.spark.funi.windowing",
        "function",
        "episode_cost",
        "estimate_tokens",
        "window_history",
    ),
    *_entries(
        "ember.spark.funi.windowing",
        "class",
        "ExtractiveSummariser",
        "WindowedHistory",
    ),
    *_entries("ember.spark.funi.windowing", "protocol", "Summariser"),
    # The tool framework's whole curated surface (E-026/E-027):
    # frozen at the package path, names in its ``__all__``.
    *_entries("ember.spark.funi.tools", "module", "__all__"),
    # Cognition: the candidate layer above Funi (E-024).
    *_entries("ember.spark.cognition", "protocol", "CognitionHandle"),
    *_entries("ember.spark.cognition", "function", "open_cognition"),
    *_entries(
        "ember.spark.cognition.handle",
        "function",
        "cognition_registry",
    ),
    *_entries("ember.spark.cognition.handle", "class", "CognitionRegistration"),
    *_entries("ember.spark.cognition.handle", "protocol", "CognitionHandle"),
    # Personae (E-025) and conversations (E-035): loading,
    # resolution, and the memory-separation wall.
    *_entries(
        "ember.spark.persona",
        "function",
        "episodes_for_persona",
        "list_persona_ids",
        "load_persona",
        "persona_dir",
        "persona_path",
        "resolve_persona",
        "save_persona_atomic",
        "tag_episode",
    ),
    *_entries(
        "ember.spark.conversation",
        "function",
        "episodes_for_conversation",
        "resolve_conversation_id",
        "tag_episode",
    ),
    *_entries("ember.spark.conversation", "class", "ConversationError"),
    # Brunnr: the Well handle (E-021's reader included in the
    # protocol), reached through Strengr in production wiring.
    *_entries("ember.well.brunnr", "protocol", "BrunnrHandle"),
    *_entries("ember.well.brunnr", "function", "open"),
    *_entries("ember.well.brunnr.handle", "protocol", "BrunnrHandle"),
    *_entries("ember.well.brunnr.handle", "function", "open"),
    # Strengr: the tether members open the Well through (E-020).
    *_entries("ember.thread.strengr", "function", "health", "open"),
    *_entries("ember.thread.strengr", "class", "Opener"),
    # The pending-episodes journal (E-031) and the diary (E-034):
    # the two on-disk records a member may legitimately touch.
    *_entries(
        "ember.well.pending_journal",
        "class",
        "CorruptEntry",
        "DrainResult",
        "PendingJournal",
    ),
    *_entries(
        "ember.well.pending_journal",
        "function",
        "episode_from_payload",
        "episode_to_payload",
        "pending_root",
    ),
    *_entries("ember.diary", "class", "Diary"),
    *_entries("ember.diary", "function", "diary_root"),
)


def api_manifest() -> tuple[ApiEntry, ...]:
    """The frozen API v1 surface, as data.

    The individual entries of :data:`API_V1` plus one entry per
    name in each :data:`SCHEMA_MODULES` module's ``__all__``
    (kind ``"schema"``), sorted by dotted path. This is the
    list a member's conformance check diffs against; it is
    computed from the live modules so it cannot drift from
    the code it describes.
    """
    entries: list[ApiEntry] = list(API_V1)
    for module_name in SCHEMA_MODULES:
        module = importlib.import_module(module_name)
        for name in module.__all__:
            entries.append(ApiEntry(module=module_name, attribute=name, kind="schema"))
    entries.sort(key=lambda entry: entry.path)
    return tuple(entries)


def _parse_version(text: str) -> tuple[int, int, int] | None:
    parts = text.strip().split(".")
    if not 1 <= len(parts) <= 3:
        return None
    numbers: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        numbers.append(int(part))
    while len(numbers) < 3:
        numbers.append(0)
    return (numbers[0], numbers[1], numbers[2])


def is_api_compatible(want: str) -> bool:
    """True when this build's API satisfies a member's ``want``.

    ``want`` is a version a member was written against
    (``"1"``, ``"1.0"`` and ``"1.0.0"`` all name the freeze).
    Compatible means: the same major, and this build's
    minor/patch is at least the wanted one — a member written
    against 1.1 binds only to a build that has 1.1's additions.
    An unparseable ``want`` is incompatible, never an error:
    a member that cannot state its version does not bind.
    """
    wanted = _parse_version(want)
    if wanted is None:
        return False
    have = _parse_version(API_VERSION)
    if have is None:  # pragma: no cover - API_VERSION is a literal above
        return False
    return wanted[0] == have[0] and wanted <= have


def verify_api_surface() -> tuple[str, ...]:
    """Check every frozen name still resolves in this build.

    Returns a tuple of problems (empty when the surface is
    intact): one line per frozen entry whose module cannot be
    imported or whose attribute is missing, and per schema
    module whose ``__all__`` names a missing attribute. The
    E-037 tests pin this to empty; a future slice that renames
    a frozen name fails there before a member fails in the
    field.
    """
    problems: list[str] = []
    for entry in API_V1:
        if entry.kind == "module":
            # A module-surface entry (the tools framework): the
            # promise is the module's own curated ``__all__``,
            # each name resolving on the module.
            try:
                module = importlib.import_module(entry.module)
            except ImportError as exc:
                problems.append(f"{entry.module}: import failed ({exc})")
                continue
            for name in module.__all__:
                if not hasattr(module, name):
                    problems.append(f"{entry.module}.{name}: missing")
            continue
        try:
            module = importlib.import_module(entry.module)
        except ImportError as exc:
            problems.append(f"{entry.path}: import failed ({exc})")
            continue
        if not hasattr(module, entry.attribute):
            problems.append(f"{entry.path}: missing")
    for module_name in SCHEMA_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            problems.append(f"{module_name}: import failed ({exc})")
            continue
        for name in module.__all__:
            if not hasattr(module, name):
                problems.append(f"{module_name}.{name}: missing")
    return tuple(problems)


__all__ = [
    "API_MAJOR",
    "API_V1",
    "API_VERSION",
    "SCHEMA_MODULES",
    "ApiEntry",
    "api_manifest",
    "is_api_compatible",
    "verify_api_surface",
]
