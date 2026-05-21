"""Identity load/save helper for Hjarta and Munnr.

Identity lives at ``~/.ember/identity/identity.json`` — plain JSON so
stdlib alone handles read and write, no extra dependency.

Per ``docs/architecture/EMBER_ARCHITECTURE.md`` §5: on-disk identity is
small and atomic. Hjarta writes it once at the end of the first-run
ritual; Munnr reads it at every launch.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from ember.schemas.config import IdentityConfig
from ember.schemas.errors import HjartaError

_IDENTITY_FILENAME = "identity.json"


def identity_path(config_root: Path) -> Path:
    return Path(config_root).expanduser() / "identity" / _IDENTITY_FILENAME


def has_identity(config_root: Path) -> bool:
    return identity_path(config_root).is_file()


def load_identity(config_root: Path) -> IdentityConfig:
    path = identity_path(config_root)
    if not path.is_file():
        return IdentityConfig()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HjartaError(f"could not read identity at {path}: {exc}") from exc
    return IdentityConfig(
        name=str(payload.get("name", "Ember")),
        role=str(payload.get("role", "your small local AI companion")),
    )


def save_identity_atomic(config_root: Path, identity: IdentityConfig) -> Path:
    """Write identity to disk atomically.

    On any failure between starting the write and renaming the temp
    file into place, the destination is left unchanged — Hjarta can
    safely re-run with no half-configured state.
    """
    target = identity_path(config_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {"name": identity.name, "role": identity.role},
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
        raise HjartaError(f"could not write identity at {target}: {exc}") from exc
    return target


def reset_identity(config_root: Path) -> None:
    """Remove the identity file so the next launch re-runs Hjarta.

    Idempotent — calling on a host without an identity is a no-op.
    """
    path = identity_path(config_root)
    path.unlink(missing_ok=True)


__all__ = [
    "has_identity",
    "identity_path",
    "load_identity",
    "reset_identity",
    "save_identity_atomic",
]
