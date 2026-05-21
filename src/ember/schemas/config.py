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
class FuniConfig:
    runtime: FuniRuntime = FuniRuntime.OLLAMA
    streaming: bool = True
    """Whether ``ember chat`` consumes Funi via streaming
    (incremental) or batched (whole reply at once). Default True per
    ADR 0009. Operators on terminals that struggle with byte streams,
    or operators piping output to log collectors, may set ``false``
    in their ``ember.yaml``."""
    ollama: FuniOllamaConfig = field(default_factory=FuniOllamaConfig)
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
# Top-level                                                             #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class EmberConfig:
    identity: IdentityConfig = field(default_factory=IdentityConfig)
    funi: FuniConfig = field(default_factory=FuniConfig)
    strengr: StrengrConfig = field(default_factory=StrengrConfig)
    brunnr: BrunnrConfig = field(default_factory=BrunnrConfig)
    smidja: SmidjaConfig = field(default_factory=SmidjaConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


__all__ = [
    "BoundaryPreference",
    "BrunnrBackend",
    "BrunnrConfig",
    "ChunkerConfig",
    "EmbeddingConfig",
    "EmberConfig",
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
    "PgVectorConfig",
    "SmidjaConfig",
    "SqliteVecConfig",
    "StrengrConfig",
]
