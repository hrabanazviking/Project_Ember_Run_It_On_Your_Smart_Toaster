"""Shape + behaviour tests for the identity helper."""

from __future__ import annotations

from pathlib import Path

from ember.schemas.config import IdentityConfig
from ember.spark.hjarta import identity as identity_mod


def test_load_returns_defaults_when_no_file(tmp_path: Path) -> None:
    result = identity_mod.load_identity(tmp_path)
    assert result.name == "Ember"


def test_has_identity_is_false_when_not_yet_written(tmp_path: Path) -> None:
    assert identity_mod.has_identity(tmp_path) is False


def test_save_atomic_creates_file_and_load_round_trips(tmp_path: Path) -> None:
    identity = IdentityConfig(name="Spark", role="a small flame")
    written = identity_mod.save_identity_atomic(tmp_path, identity)
    assert written.is_file()
    assert identity_mod.has_identity(tmp_path)
    loaded = identity_mod.load_identity(tmp_path)
    assert loaded.name == "Spark"
    assert loaded.role == "a small flame"


def test_save_leaves_no_tmp_files_behind(tmp_path: Path) -> None:
    identity_mod.save_identity_atomic(tmp_path, IdentityConfig(name="X"))
    identity_dir = tmp_path / "identity"
    leftover = [p for p in identity_dir.iterdir() if p.name.endswith(".tmp")]
    assert leftover == []


def test_reset_removes_identity(tmp_path: Path) -> None:
    identity_mod.save_identity_atomic(tmp_path, IdentityConfig())
    assert identity_mod.has_identity(tmp_path)
    identity_mod.reset_identity(tmp_path)
    assert not identity_mod.has_identity(tmp_path)


def test_reset_is_idempotent_when_no_identity(tmp_path: Path) -> None:
    # No raise, no error.
    identity_mod.reset_identity(tmp_path)
    assert not identity_mod.has_identity(tmp_path)
