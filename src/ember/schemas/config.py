"""Typed configuration objects for every Ember subpackage.

Per ``docs/architecture/DOMAIN_MAP.md`` §1 and §11 (configuration row):
every subpackage receives its configuration as a typed object from above;
nothing in ``ember.*`` reads files directly except the loader (planned
for Phase 6 in ``ember.spark.munnr.config_loader``).

These are stdlib :func:`dataclasses.dataclass` types only. Validation
beyond the type system is intentionally deferred to the loader. Defaults
mirror the values in ``config/ember.example.yaml``.

Paths are stored as :class:`pathlib.Path` instances **without** calling
``expanduser()`` — the consumer expands when the path is actually used.
This keeps the schema pure and avoids freezing ``$HOME`` at import time.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

# --------------------------------------------------------------------- #
# Enums                                                                 #
# --------------------------------------------------------------------- #


class BrunnrBackend(StrEnum):
    SQLITE_VEC = "sqlite_vec"
    PGVECTOR = "pgvector"
    QDRANT = "qdrant"
    CHROMA = "chroma"
    LANCEDB = "lancedb"


class FuniRuntime(StrEnum):
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    LMSTUDIO = "lmstudio"
    PHI_SILICA = "phi_silica"
    APPLE_FOUNDATION = "apple_foundation"
    AESIR = "aesir"  # E-023 — Project Aesir native service


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(StrEnum):
    STRUCTURED = "structured"
    PLAIN = "plain"


class LogDestinationKind(StrEnum):
    FILE = "file"
    STDERR = "stderr"
    STDOUT = "stdout"


class BoundaryPreference(StrEnum):
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    WORD = "word"
    CHAR = "char"


class ConversationProfile(StrEnum):
    """Hardware profile shaping the conversation token budget (E-021).

    The profile names are Part III's (E-041): toaster (the smallest),
    phone, pi, laptop. E-021 consumes them only for history windowing;
    Part III owns the full budget book and may re-measure the numbers.
    """

    TOASTER = "toaster"
    PHONE = "phone"
    PI = "pi"
    LAPTOP = "laptop"


# --------------------------------------------------------------------- #
# Identity                                                              #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class IdentityConfig:
    name: str = "Ember"
    role: str = "your small local AI companion"


# --------------------------------------------------------------------- #
# Funi (Spark realm)                                                    #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class FuniOllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "phi3:mini"
    temperature: float = 0.7
    top_p: float = 0.9
    num_predict: int = 1024


@dataclass(frozen=True, slots=True)
class FuniAesirConfig:
    """Operator-facing config for the Project Aesir backend (E-023).

    Aesir's native service is loopback-only (``127.0.0.1:18434`` by
    default) and authenticated with a bearer key that lives in a
    protected key file the service reads at startup (see Aesir's
    NATIVE_SERVICE doc). Ember follows the Well-secret shape
    (E-013/E-020): the config carries the key file's *path* — a
    reference, never the key value — and the adapter reads the file
    at ``open()`` time, keeping the value in memory only.

    ``model`` is the *expected* resident model identity. The native
    ``/v1/generate`` route names no model (the service holds exactly
    one resident model), so an empty value accepts whatever model
    the service reports ready; a non-empty value is verified against
    the readiness probe at ``open()`` and a mismatch is a typed
    ``Unavailable``, never a silent substitution.

    ``max_tokens`` defaults to 256, the Aesir service's own default
    reply ceiling — a request may lower but never raise the service
    ceiling, so Ember's default must not promise more than the
    service's default grants. ``timeout_ms`` is omitted from requests
    when None (the service's own limit then applies).
    """

    base_url: str = "http://127.0.0.1:18434"
    model: str = ""
    api_key_file: Path = Path("~/.config/aesir/service.key")
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 256
    timeout_ms: int | None = None


@dataclass(frozen=True, slots=True)
class FuniConfig:
    runtime: FuniRuntime = FuniRuntime.OLLAMA
    streaming: bool = True
    """Whether ``ember chat`` consumes Funi via streaming
    (incremental) or batched (whole reply at once). Default True per
    ADR 0009. Operators on terminals that struggle with byte streams,
    or operators piping output to log collectors, may set ``false``
    in their ``ember.yaml``."""
    ollama: FuniOllamaConfig = field(default_factory=FuniOllamaConfig)
    aesir: FuniAesirConfig = field(default_factory=FuniAesirConfig)
    # Other runtime sub-configs (llamacpp, lmstudio, phi_silica,
    # apple_foundation) land alongside their adapters in Phase 5+.


# --------------------------------------------------------------------- #
# Strengr (Thread realm)                                                #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class StrengrConfig:
    health_check_timeout_s: float = 5.0
    retry_attempts: int = 3
    retry_backoff_max_s: float = 30.0


# --------------------------------------------------------------------- #
# Brunnr (Well realm — storage)                                         #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class SqliteVecConfig:
    path: Path = Path("~/.ember/well/store.db")
    wal_mode: bool = True


@dataclass(frozen=True, slots=True)
class PgVectorConfig:
    """Operator-facing config for the ``pgvector`` Brunnr (ADR 0010).

    ``url`` and ``secret_ref`` are required when this backend is selected;
    the rest carry Gungnir-aligned defaults. See ADR 0010 §2.5 for the
    secret-resolution order documented for ``secret_env`` / ``use_keyring`` /
    ``secret_ref``.
    """

    url: str
    secret_ref: Path = Path("~/.ember/secrets/well.password")
    secret_env: str = "EMBER_WELL_PASSWORD"
    use_keyring: bool = True
    keyring_service: str = "ember-well"
    username: str | None = None  # None → parsed from URL
    connect_timeout_s: float = 10.0
    vector_index: str = "hnsw"
    vector_metric: str = "cosine"
    schema: str = "public"
    read_only: bool = False  # ADR 0010 §4 open-question; opt-in hardening for shared Gungnirs.


@dataclass(frozen=True, slots=True)
class BrunnrConfig:
    backend: BrunnrBackend = BrunnrBackend.SQLITE_VEC
    embedding_dim: int = 768
    sqlite_vec: SqliteVecConfig | None = field(default_factory=SqliteVecConfig)
    pgvector: PgVectorConfig | None = None
    # qdrant / chroma / lancedb sub-configs land with their adapters.


# --------------------------------------------------------------------- #
# Smiðja (Well realm — ingest)                                          #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ChunkerConfig:
    """Gungnir-aligned defaults — see docs/adapters/SMIDJA_INGEST_PATTERNS.md §3."""

    max_chars: int = 2000
    target_chars: int = 1684
    min_chars: int = 200
    overlap_chars: int = 0
    boundary_preference: BoundaryPreference = BoundaryPreference.PARAGRAPH


@dataclass(frozen=True, slots=True)
class EmbeddingConfig:
    endpoint: str = "http://localhost:11434/api/embed"
    model: str = "nomic-embed-text"
    batch_size: int = 32


@dataclass(frozen=True, slots=True)
class JournalConfig:
    root: Path = Path("~/.ember/state/smidja_progress/")
    heartbeat_s: int = 30
    stale_heartbeat_s: int = 600


@dataclass(frozen=True, slots=True)
class SmidjaConfig:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    chunker: ChunkerConfig = field(default_factory=ChunkerConfig)
    journal: JournalConfig = field(default_factory=JournalConfig)


# --------------------------------------------------------------------- #
# Logging (cross-cutting)                                               #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class LoggingDestination:
    kind: LogDestinationKind
    path: Path | None = None
    rotate_at_mb: int | None = None
    keep: int | None = None


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.STRUCTURED
    destinations: tuple[LoggingDestination, ...] = ()


# --------------------------------------------------------------------- #
# Tools (slice-2 Phase 14-16 — ADR 0011)                                #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ToolsConfig:
    """Operator-facing tool-use config (ADR 0011).

    ``enabled`` is False by default per the Vow of Sovereignty —
    Ember does not reach beyond the chat turn unless the operator
    opts in. The ``--allow-tools`` / ``--no-tools`` CLI flags
    (Phase 16) overlay a single-invocation override on top of this.

    ``approval_overrides`` is a per-tool dict. Per ADR 0011 §2.4 the
    descriptor is the safety floor — config can downgrade STANDING to
    PER_CALL but cannot upgrade.

    ``standing_trust`` flips every PER_CALL tool to AUTO_APPROVED
    (the "trust everything" knob); still audited.

    ``audit_root`` overrides where the JSONL audit log lands.
    None → ``<config_root>/state/tool_audit/``.
    """

    enabled: bool = False
    standing_trust: bool = False
    approval_overrides: Mapping[str, str] = field(default_factory=dict)
    allow_private_addresses: bool = False
    audit_root: Path | None = None


# --------------------------------------------------------------------- #
# MCP (ADR-0014)                                                        #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class MCPServerSpec:
    """One external MCP server Ember will spawn and connect to.

    Per ADR-0014. ``name`` becomes the prefix in the registered tool
    name (``mcp__<name>__<tool>``) so multiple servers' tools never
    collide. ``auto_approve`` lists individual tool names that lift
    from PER_CALL to STANDING — every other tool requires per-call
    operator approval (Vow of Sovereignty default).
    """

    name: str
    command: str
    args: tuple[str, ...] = ()
    env: Mapping[str, str] = field(default_factory=dict)
    cwd: str | None = None
    auto_approve: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MCPConfig:
    """MCP client + server enablement and tuning.

    Per ADR-0014. ``enabled`` turns on the client side (Ember spawns +
    consumes external MCP servers). ``expose_self`` turns on the server
    side (Ember exposes Well + diagnostics as an MCP server when
    ``ember mcp serve`` is invoked).

    The timeouts apply only to the client side; the server side runs
    until the operator Ctrl-Cs it.
    """

    enabled: bool = False
    expose_self: bool = False
    startup_timeout_s: float = 10.0
    call_timeout_s: float = 30.0
    servers: tuple[MCPServerSpec, ...] = ()


# --------------------------------------------------------------------- #
# Conversation (E-021 — history windowing under a token budget)         #
# --------------------------------------------------------------------- #

# Per-profile conversation defaults: (token budget for history,
# max episodes kept verbatim). The budget covers the episode history
# only — system prompt, grounding hits, and the current operator line
# are assembled outside it (see ember.spark.funi.windowing).
_PROFILE_CONVERSATION_DEFAULTS: dict[ConversationProfile, tuple[int, int]] = {
    ConversationProfile.TOASTER: (512, 3),
    ConversationProfile.PHONE: (1024, 5),
    ConversationProfile.PI: (2048, 8),
    ConversationProfile.LAPTOP: (4096, 12),
}


@dataclass(frozen=True, slots=True)
class ConversationConfig:
    """How much conversation history rides in each turn's prompt.

    ``profile`` selects the default token budget + episode cap for the
    machine class; ``token_budget`` / ``max_episodes`` override the
    profile's numbers when set. ``summarise_dropped`` keeps a short
    deterministic summary of whatever the window drops, produced by
    the summarisation hook (E-021), so trimming never silently
    pretends the earlier conversation did not happen.
    """

    profile: ConversationProfile = ConversationProfile.PI
    token_budget: int | None = None
    max_episodes: int | None = None
    summarise_dropped: bool = True

    @property
    def resolved_token_budget(self) -> int:
        if self.token_budget is not None:
            return self.token_budget
        return _PROFILE_CONVERSATION_DEFAULTS[self.profile][0]

    @property
    def resolved_max_episodes(self) -> int:
        if self.max_episodes is not None:
            return self.max_episodes
        return _PROFILE_CONVERSATION_DEFAULTS[self.profile][1]


# --------------------------------------------------------------------- #
# Cognition (E-024 — optional ThoughtForge cognition layer)             #
# --------------------------------------------------------------------- #

# Per-profile cognition defaults: which Ember profiles may run the
# ThoughtForge cognition layer, and the candidate-draft cap handed
# to ThoughtForge's think() on that profile (TF-034 froze
# num_drafts semantics: a cap, never a raise — the local engine
# drafts at most 2 by construction, the unified backend exactly 1).
# The toaster — the smallest profile, the project's namesake floor —
# cannot afford a second full turn pipeline beside Funi: the layer
# refuses there, truthfully, instead of swapping the machine.
_PROFILE_COGNITION_DEFAULTS: dict[ConversationProfile, int | None] = {
    ConversationProfile.TOASTER: None,
    ConversationProfile.PHONE: 1,
    ConversationProfile.PI: 1,
    ConversationProfile.LAPTOP: 2,
}


@dataclass(frozen=True, slots=True)
class CognitionConfig:
    """The optional cognition layer above Funi (E-024).

    ``enabled`` is False by default: ThoughtForge is a *candidate*
    cognition layer (roadmap E-024), never a silent replacement for
    the Funi turn. Enabling it is an explicit operator act, and even
    then the profile gate applies — see
    :meth:`affords` / :meth:`resolved_num_drafts`.

    ``provider`` names the binding; ``thoughtforge`` is the only
    provider in this build. ``expected_api_major`` is the
    ThoughtForge cognition API major this binding was written
    against (TF-034 froze v1.0.0); a live provider reporting a
    different major is refused at open time, never adapted to
    silently (TF-162's rule, Ember side).

    ThoughtForge keeps its own state (its memory dir + knowledge
    DB). By default both live **inside Ember's config root**
    (``~/.ember/thoughtforge/…``) so the tether holds (E-020):
    custody of the Ember folder is custody of everything the
    companion keeps, ThoughtForge's state included. Paths are
    stored unexpanded, like every path in this module; the adapter
    expands them at open time. ``model_path`` is empty by default —
    ThoughtForge then runs knowledge-only, its own documented
    no-model shape — and names a model file only when the operator
    points at one. ``tf_config`` is passed through to the
    ThoughtForge core constructor unchanged: ThoughtForge's config
    surface (TF-032) reads its live keys from it, and Ember does
    not shadow them.
    """

    enabled: bool = False
    provider: str = "thoughtforge"
    profile: ConversationProfile = ConversationProfile.PI
    expected_api_major: int = 1
    model_path: Path | None = None
    memory_dir: Path = Path("~/.ember/thoughtforge/memory")
    db_path: Path = Path("~/.ember/thoughtforge/knowledge.db")
    num_drafts: int | None = None
    tf_config: Mapping[str, object] = field(default_factory=dict)

    def affords(self, profile: ConversationProfile | None = None) -> bool:
        """Can this (or the given) profile run the cognition layer?"""
        chosen = self.profile if profile is None else profile
        return _PROFILE_COGNITION_DEFAULTS[chosen] is not None

    @property
    def resolved_num_drafts(self) -> int | None:
        """The draft cap for the configured profile.

        An explicit ``num_drafts`` wins; otherwise the profile's
        cap applies. None when the profile cannot afford the layer
        at all. A cap below 1 is a caller error — ThoughtForge's
        frozen semantics raise on it, and the adapter refuses it
        earlier, as a typed config refusal.
        """
        if self.num_drafts is not None:
            return self.num_drafts
        return _PROFILE_COGNITION_DEFAULTS[self.profile]


# --------------------------------------------------------------------- #
# Personae (E-025 — who the companion is)                               #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class PersonasConfig:
    """Which persona the companion runs as (E-025).

    ``active`` names a persona file under
    ``<config_root>/personas/<id>.json``. It is empty by default:
    no explicit choice, so resolution falls to a ``default.json``
    persona file when one exists, else to the identity projected
    onto the default persona (see
    ``ember.spark.persona.resolve_persona``). Naming an id that
    does not load is an error at resolve time, never a silent
    substitution of a different companion.
    """

    active: str = ""


# --------------------------------------------------------------------- #
# Top-level                                                             #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class EmberConfig:
    identity: IdentityConfig = field(default_factory=IdentityConfig)
    personas: PersonasConfig = field(default_factory=PersonasConfig)
    conversation: ConversationConfig = field(default_factory=ConversationConfig)
    cognition: CognitionConfig = field(default_factory=CognitionConfig)
    funi: FuniConfig = field(default_factory=FuniConfig)
    strengr: StrengrConfig = field(default_factory=StrengrConfig)
    brunnr: BrunnrConfig = field(default_factory=BrunnrConfig)
    smidja: SmidjaConfig = field(default_factory=SmidjaConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


__all__ = [
    "BoundaryPreference",
    "BrunnrBackend",
    "BrunnrConfig",
    "ChunkerConfig",
    "CognitionConfig",
    "ConversationConfig",
    "ConversationProfile",
    "EmbeddingConfig",
    "EmberConfig",
    "FuniAesirConfig",
    "FuniConfig",
    "FuniOllamaConfig",
    "FuniRuntime",
    "IdentityConfig",
    "JournalConfig",
    "LogDestinationKind",
    "LogFormat",
    "LogLevel",
    "LoggingConfig",
    "LoggingDestination",
    "MCPConfig",
    "MCPServerSpec",
    "PersonasConfig",
    "PgVectorConfig",
    "SmidjaConfig",
    "SqliteVecConfig",
    "StrengrConfig",
    "ToolsConfig",
]
