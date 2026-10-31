"""E-020 — Tethering made explicit: spec-pinning tests.

The tethering spec lives at ``docs/architecture/E-020_TETHERING_SPEC.md``.
Ember is tethered in exactly three ways, and each test below pins one
clause of that spec to the code that honours it:

- **To its person** — one config root (default ``~/.ember/``, or
  ``--config-root``) holding the identity file, the operator config,
  and the secrets; nothing about the person lives anywhere else.
- **To its machine** — the model (Funi) and the embedder default to
  services on the same machine (Ollama on localhost); schema paths
  keep ``~`` unexpanded until use, so a clone anywhere works.
- **To its memory** — the Well is reached only through Strengr:
  retry-with-backoff, fast-fail on non-recoverable reasons, a health
  probe that never raises, and a typed ``Disconnected`` — never an
  exception, never a pretence of connection.

These tests are stdlib-only and run in the default environment shape
(the campaign's Run B gate shape).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ember.config import load_ember_config
from ember.schemas.config import (
    BrunnrBackend,
    EmberConfig,
    FuniRuntime,
    IdentityConfig,
    PgVectorConfig,
    StrengrConfig,
)
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import Unavailable, UnavailableReason
from ember.spark import funi
from ember.spark.hjarta import identity as hjarta_identity
from ember.thread import strengr

# --------------------------------------------------------------------- #
# To its person — the config root and the identity file                 #
# --------------------------------------------------------------------- #


def test_person_tether_identity_defaults() -> None:
    cfg = EmberConfig()
    assert cfg.identity.name == "Ember"
    assert cfg.identity.role == "your small local AI companion"


def test_person_tether_identity_file_location_and_round_trip(
    tmp_path: Path,
) -> None:
    root = tmp_path / "person-a"
    assert hjarta_identity.has_identity(root) is False
    # A missing identity file is not an error: the schema defaults
    # ARE the untethered-yet state (E-019 §4 step 1).
    assert hjarta_identity.load_identity(root) == IdentityConfig()

    saved = hjarta_identity.save_identity_atomic(
        root, IdentityConfig(name="Spark", role="a small test companion")
    )
    assert saved == root / "identity" / "identity.json"
    assert hjarta_identity.has_identity(root) is True
    loaded = hjarta_identity.load_identity(root)
    assert loaded.name == "Spark"
    assert loaded.role == "a small test companion"


def test_person_tether_identity_file_holds_name_and_role_only(
    tmp_path: Path,
) -> None:
    root = tmp_path / "person-a"
    hjarta_identity.save_identity_atomic(root, IdentityConfig(name="Spark"))
    payload = json.loads(
        (root / "identity" / "identity.json").read_text(encoding="utf-8")
    )
    # The person tether stores who Ember is for this person — and
    # nothing else. No credentials, no history, no machine data.
    assert set(payload) == {"name", "role"}


def test_person_tether_two_roots_do_not_bleed(tmp_path: Path) -> None:
    root_a = tmp_path / "person-a"
    root_b = tmp_path / "person-b"
    hjarta_identity.save_identity_atomic(
        root_a, IdentityConfig(name="Spark", role="for person A")
    )
    # Person B's root is untouched by person A's setup.
    assert hjarta_identity.has_identity(root_b) is False
    assert hjarta_identity.load_identity(root_b) == IdentityConfig()

    hjarta_identity.reset_identity(root_a)
    assert hjarta_identity.has_identity(root_a) is False
    # Reset is idempotent and root-scoped.
    hjarta_identity.reset_identity(root_a)


def test_person_tether_config_is_read_from_the_config_root(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "ember.toml").write_text(
        "[identity]\nname = 'Spark'\n", encoding="utf-8"
    )
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"
    # An empty root yields the pure defaults — the tether's floor.
    empty = tmp_path / "empty"
    empty.mkdir()
    assert load_ember_config(empty, skip_env=True) == EmberConfig()


# --------------------------------------------------------------------- #
# To its machine — local model, local embedder, flexible roots         #
# --------------------------------------------------------------------- #


def test_machine_tether_model_and_embedder_default_to_localhost() -> None:
    cfg = EmberConfig()
    assert cfg.funi.runtime is FuniRuntime.OLLAMA
    assert cfg.funi.ollama.base_url == "http://localhost:11434"
    assert cfg.funi.ollama.model == "phi3:mini"
    assert cfg.smidja.embedding.endpoint == "http://localhost:11434/api/embed"
    assert cfg.smidja.embedding.model == "nomic-embed-text"


def test_machine_tether_unimplemented_runtime_is_typed_unavailable() -> None:
    cfg = EmberConfig()
    from dataclasses import replace

    for runtime in (
        FuniRuntime.LLAMACPP,
        FuniRuntime.LMSTUDIO,
        FuniRuntime.PHI_SILICA,
        FuniRuntime.APPLE_FOUNDATION,
    ):
        result = funi.handle.open(replace(cfg.funi, runtime=runtime))
        assert isinstance(result, Unavailable)
        assert result.reason is UnavailableReason.RUNTIME_NOT_INSTALLED


def test_machine_tether_schema_paths_keep_tilde_unexpanded() -> None:
    cfg = EmberConfig()
    # Flexible Roots: the schema never freezes $HOME at import time;
    # consumers expand when the path is actually used.
    assert cfg.brunnr.sqlite_vec is not None
    assert cfg.brunnr.sqlite_vec.path == Path("~/.ember/well/store.db")
    assert cfg.smidja.journal.root == Path("~/.ember/state/smidja_progress/")
    pg = PgVectorConfig(url="postgresql://ember@localhost/well")
    assert pg.secret_ref == Path("~/.ember/secrets/well.password")


def test_machine_tether_sovereignty_defaults_are_off() -> None:
    cfg = EmberConfig()
    # The machine tether does not reach out on its own: tools and MCP
    # are opt-in, and a remote Well's read_only hardening exists.
    assert cfg.tools.enabled is False
    assert cfg.mcp.enabled is False
    assert cfg.mcp.expose_self is False


# --------------------------------------------------------------------- #
# To its memory — Strengr is the only road to the Well                  #
# --------------------------------------------------------------------- #


def test_memory_tether_default_backend_is_the_local_well() -> None:
    cfg = EmberConfig()
    assert cfg.brunnr.backend is BrunnrBackend.SQLITE_VEC
    assert cfg.brunnr.embedding_dim == 768


def test_memory_tether_strengr_policy_defaults() -> None:
    cfg = StrengrConfig()
    assert cfg.retry_attempts == 3
    assert cfg.retry_backoff_max_s == 30.0
    assert cfg.health_check_timeout_s == 5.0


def _disconnected(reason: DisconnectReason) -> Disconnected:
    return Disconnected(
        reason=reason, since=datetime.now(tz=UTC), detail=reason.value
    )


def test_memory_tether_disconnect_is_a_typed_value_never_raised() -> None:
    calls: list[int] = []

    def opener(_config):
        calls.append(1)
        return _disconnected(DisconnectReason.CONN_REFUSED)

    result = strengr.open(
        StrengrConfig(retry_attempts=3, retry_backoff_max_s=0.0),
        EmberConfig().brunnr,
        opener=opener,
        sleeper=lambda _s: None,
    )
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONN_REFUSED
    # Recoverable reasons are retried exactly the configured number
    # of times before the tether reports itself cut.
    assert len(calls) == 3


def test_memory_tether_remote_well_secret_is_a_reference_not_a_value() -> None:
    pg = PgVectorConfig(url="postgresql://ember@localhost/well")
    # The config carries WHERE the secret lives (env name, keyring
    # service, mode-600 file path) — never the secret itself.
    assert pg.secret_env == "EMBER_WELL_PASSWORD"
    assert pg.use_keyring is True
    assert pg.keyring_service == "ember-well"
    assert not hasattr(pg, "password")
