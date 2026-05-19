# 45 — Configuration Management: Pydantic Settings, dynaconf, env-driven

**Category:** Architecture Patterns
**Runa relevance:** `config/runa.example.yaml`, `~/.runa/config/runa.yaml`, `.env.example`
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Configuration management answers: "where does each setting come from?" Hard-coded constants? Environment variables? Config files (YAML/TOML/JSON)? Command-line flags? Secrets stores? In production systems, all of these contribute, in a specific precedence order, and the *config layer* is what assembles them into a single typed object the application reads.

For Runa, config is layered: defaults compiled in → `config/runa.example.yaml` template → `~/.runa/config/runa.yaml` user file → environment variables (`RUNA_*`) → command-line flags. Typed via Pydantic Settings ([[27-pydantic-runtime-validation]]). Secrets pulled separately from `~/.runa/secrets/`. Validated at startup; the agent refuses to start if config is malformed.

## 2. Technique / mechanism

**Pydantic Settings — typed config from many sources:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel
from pathlib import Path

class HeimskringlaConfig(BaseModel):
    default_provider: str = "ollama"
    timeout_seconds: float = 30.0

class MuninnConfig(BaseModel):
    embedding_model: str = "bge-small-en-v1.5"
    retrieval_top_k: int = 12

class RunaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RUNA_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        # Precedence: env > .env > defaults
    )
    
    home: Path = Path("~/.runa").expanduser()
    log_level: str = "INFO"
    heimskringla: HeimskringlaConfig = HeimskringlaConfig()
    muninn: MuninnConfig = MuninnConfig()

settings = RunaSettings()
# Reads RUNA_HOME, RUNA_LOG_LEVEL, RUNA_HEIMSKRINGLA__DEFAULT_PROVIDER, etc.
```

Nested config via `__` delimiter: `RUNA_MUNINN__EMBEDDING_MODEL` sets `settings.muninn.embedding_model`.

**Loading from YAML file:**

```python
import yaml

class RunaSettings(BaseSettings):
    @classmethod
    def from_yaml(cls, path: Path) -> "RunaSettings":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

# Usage:
settings = RunaSettings.from_yaml(Path("~/.runa/config/runa.yaml").expanduser())
```

Or use `pydantic-settings-yaml` for built-in YAML support.

**Layered loading:**

```python
def load_settings() -> RunaSettings:
    """Load config with layered precedence:
    1. Compiled defaults (in the Pydantic model defaults)
    2. config/runa.yaml template (in the repo, shipped)
    3. ~/.runa/config/runa.yaml (operator-edited)
    4. RUNA_* env vars
    5. CLI flags (handled separately in runa.cli)
    """
    template = yaml.safe_load((Path("config") / "runa.example.yaml").read_text())
    user_path = Path("~/.runa/config/runa.yaml").expanduser()
    if user_path.exists():
        user_config = yaml.safe_load(user_path.read_text())
        merged = deep_merge(template, user_config)
    else:
        merged = template
    
    return RunaSettings(**merged)  # env vars override via Pydantic Settings
```

**Secret management:**

Secrets *do not* go in config files. They live in:
- `~/.runa/secrets/runa.env` (env file the operator creates) — for development.
- OS keyring (`keyring` library) — for proper systems.
- External secret stores (AWS Secrets Manager, HashiCorp Vault) — for production.

```python
from pydantic_settings import BaseSettings

class Secrets(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path("~/.runa/secrets/runa.env").expanduser(),
        env_file_encoding="utf-8",
        env_prefix="",  # different from main config
    )
    
    openrouter_api_key: str | None = None
    anthropic_api_key: str | None = None
    discord_bot_token: str | None = None
```

Secrets are separate; loaded from a different file with stricter perms (0600).

**Validation at startup:**

```python
def startup_validate(settings: RunaSettings, secrets: Secrets) -> list[str]:
    """Return a list of validation errors; empty means OK."""
    errors = []
    if not settings.home.exists():
        errors.append(f"home directory {settings.home} doesn't exist")
    if settings.heimskringla.default_provider == "openrouter" and not secrets.openrouter_api_key:
        errors.append("openrouter provider requires OPENROUTER_API_KEY")
    return errors

# In startup:
errors = startup_validate(settings, secrets)
if errors:
    for e in errors:
        logger.error(e)
    sys.exit(2)
```

The agent refuses to start if config is invalid.

**Config validation via Pydantic:**

```python
class MuninnConfig(BaseModel):
    embedding_model: str = "bge-small-en-v1.5"
    retrieval_top_k: int = Field(ge=1, le=100, default=12)
    
    @field_validator("embedding_model")
    @classmethod
    def known_model(cls, v: str) -> str:
        if v not in KNOWN_EMBEDDING_MODELS:
            raise ValueError(f"unknown embedding model: {v}")
        return v
```

Validation happens at load time; bad values raise clear errors.

**Other config libraries:**

- **`dynaconf`** — github.com/rochacbruno/dynaconf. Multi-source config with envrionments (dev/prod/test).
- **`configparser`** (stdlib) — INI files. Older.
- **`tomllib`** (stdlib 3.11+) — TOML parser. Read-only.
- **`OmegaConf`** — github.com/omry/omegaconf. Hierarchical YAML; powerful interpolation. Heavy.
- **`hydra`** — github.com/facebookresearch/hydra. Built on OmegaConf; great for ML config.

For Runa-scale, Pydantic Settings is the sweet spot.

**Watching for changes (hot reload):**

```python
from watchfiles import awatch

async def watch_config(path: Path):
    async for changes in awatch(path):
        logger.info("config changed; reloading")
        new_settings = RunaSettings.from_yaml(path)
        # Apply new settings — needs careful handling
```

Hot config reload is hard to get right; usually requires a restart instead. Reload sparingly.

## 3. Key works / libraries

- **Pydantic Settings** — docs.pydantic.dev/latest/concepts/pydantic_settings/.
- **`dynaconf`** — dynaconf.com.
- **`OmegaConf`** / **`hydra`** — facebookresearch.
- **`tomllib`** (3.11+) — stdlib.
- **The Twelve-Factor App** — 12factor.net. Config principles.

## 4. Pitfalls and gotchas

- **Secrets in config files** — visible in git, logs, `runa doctor` output. Separate.
- **Defaults that depend on environment.** `home: Path = Path.home() / ".runa"` works at definition time, not run time. Use `Field(default_factory=...)` or compute in a validator.
- **Mutable default values.** Pydantic handles this correctly; raw dataclasses don't.
- **Nested env vars.** `RUNA_MUNINN__EMBEDDING_MODEL` requires `env_nested_delimiter`.
- **Type coercion surprises.** `True` from env var is the string `"true"` — Pydantic coerces; some types it can't.
- **YAML traps.** `yes` parses as `True`; `1.0e10` parses as float; numbers starting with `0` parse as octal sometimes. Use safe_load.
- **Config drift.** Production config diverges from `config/runa.example.yaml`. Periodic sync.
- **Hot reload races.** Don't reload mid-request unless very careful.

## 5. Applicability to Runa

For **`config/runa.example.yaml`**:

- Shipped in the repo. Cautious defaults. Template the operator copies.

For **`~/.runa/config/runa.yaml`**:

- Operator's machine. Edits here override the template.

For **environment variables**:

- `RUNA_*` prefix.
- Useful for deployment-specific overrides without editing config file (e.g., `RUNA_LOG_LEVEL=DEBUG` in a debugging session).

For **`~/.runa/secrets/runa.env`**:

- Separate file. Mode 0600.
- Holds API keys, tokens.
- Never logged unredacted.

For **`runa config validate`**:

- CLI command that loads + validates config; reports errors without starting the agent.

For **`runa config init`**:

- CLI command that creates `~/.runa/config/runa.yaml` from the template.

For **CLI flag overrides**:

- `runa start --log-level=DEBUG` overrides config setting for one run.

What to avoid:

- Don't put secrets in config files.
- Don't hard-code paths inside source code.
- Don't read env vars deep in business logic — load at startup, pass as dependency.
- Don't hot-reload config without testing the cutover carefully.

## 6. Open questions

- **Multi-environment config** (dev / staging / prod). Single-user Runa is mostly one environment; longhall might be multi.
- **Versioning of config schema.** Old configs may need migration when new versions add required fields.
- **Config UI.** Eventually, a GUI for editing config rather than YAML. Long-term.

## 7. References (curated)

- docs.pydantic.dev/latest/concepts/pydantic_settings/.
- 12factor.net/config.
- dynaconf.com.
- docs.python.org/3/library/tomllib.html.
- Companion docs: [[27-pydantic-runtime-validation]], [[41-dependency-injection]], [[49-graceful-shutdown]] (signal-driven reload).
