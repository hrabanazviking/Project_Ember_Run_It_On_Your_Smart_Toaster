"""Secret resolver for the pgvector Brunnr.

Per ADR 0010 §2.5 — resolves the Well password in this order:

1. **Env var** (``PgVectorConfig.secret_env``, default
   ``EMBER_WELL_PASSWORD``). Empty / missing → continue.
2. **Keyring** (``keyring.get_password(keyring_service, username)``)
   when ``use_keyring=True`` and the ``keyring`` package is importable.
   Missing → continue.
3. **Mode-600 file** at ``PgVectorConfig.secret_ref``. The file *must*
   be 0o600 (operator-only); a more permissive mode is refused with a
   typed reason so the operator gets a pointer at the permission bits
   rather than a silent leak.
4. **Final** → ``None``. The caller folds this into
   :class:`Disconnected(AUTH_FAILED)`.

The secret is **never** logged or echoed back through any return value —
even on error. Reasons describe *why* a path was skipped or refused;
they never name the resolved value.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from ember.schemas.config import PgVectorConfig

# Default keyring service name (also lives in PgVectorConfig.keyring_service
# as the operator-overridable knob). Kept at module level so tests can
# refer to it without constructing a PgVectorConfig.
DEFAULT_KEYRING_SERVICE: Final[str] = "ember-well"
DEFAULT_SECRET_ENV: Final[str] = "EMBER_WELL_PASSWORD"

REQUIRED_FILE_MODE: Final[int] = 0o600


@dataclass(frozen=True, slots=True)
class SecretResolution:
    """The outcome of a resolve() attempt.

    Either ``secret`` is set (success) or ``reason`` is set (failure).
    The two are never both populated. ``reason`` is *operator-facing*:
    it explains which sources were tried and why each was skipped, so
    the operator can fix the right thing.
    """

    secret: str | None
    reason: str | None

    @classmethod
    def found(cls, secret: str) -> SecretResolution:
        return cls(secret=secret, reason=None)

    @classmethod
    def missing(cls, reason: str) -> SecretResolution:
        return cls(secret=None, reason=reason)


def resolve(  # noqa: PLR0912 — secret resolution is naturally branchy; each branch is one source
    config: PgVectorConfig,
    *,
    env: dict[str, str] | None = None,
    keyring_module: object | None = None,
) -> SecretResolution:
    """Resolve the Well secret per ADR 0010 §2.5.

    ``env`` defaults to ``os.environ``; tests pass a dict to avoid
    polluting the real environment. ``keyring_module`` defaults to the
    real ``keyring`` package (or None if it's not importable); tests
    inject a fake.
    """
    notes: list[str] = []
    env_map = os.environ if env is None else env

    # --- 1. Env var ---------------------------------------------------- #
    env_name = config.secret_env or DEFAULT_SECRET_ENV
    env_value = env_map.get(env_name, "")
    if env_value:
        return SecretResolution.found(env_value)
    notes.append(f"env ${env_name} not set")

    # --- 2. Keyring (optional) ----------------------------------------- #
    if config.use_keyring:
        kr = keyring_module if keyring_module is not None else _try_import_keyring()
        if kr is None:
            notes.append("keyring package not installed")
        else:
            username = _resolve_username(config)
            if username is None:
                notes.append("keyring skipped: no username in URL or config")
            else:
                service = config.keyring_service or DEFAULT_KEYRING_SERVICE
                try:
                    value = kr.get_password(service, username)  # type: ignore[attr-defined]
                except Exception as exc:
                    # The keyring's "is locked" state (operator hasn't
                    # unlocked their GPG/libsecret session) is a
                    # transient + actionable failure; surface it as a
                    # distinct note so the operator's error message
                    # points at "unlock the keyring" instead of "no
                    # entry exists". Other exceptions remain
                    # type-named.
                    exc_name = type(exc).__name__
                    if "Locked" in exc_name:
                        notes.append(
                            f"keyring is locked ({exc_name}); "
                            f"unlock it or use the env / file source"
                        )
                    else:
                        notes.append(
                            f"keyring lookup raised: {exc_name}",
                        )
                    value = None
                if value:
                    return SecretResolution.found(value)
                notes.append(
                    f"keyring entry for ({service!r}, {username!r}) not found"
                )
    else:
        notes.append("keyring disabled in config")

    # --- 3. Mode-600 file ---------------------------------------------- #
    secret_path = Path(config.secret_ref).expanduser()
    if not secret_path.exists():
        notes.append(f"secret file {secret_path} not found")
    else:
        mode_check = _check_secret_file_mode(secret_path)
        if mode_check is not None:
            notes.append(mode_check)
        else:
            try:
                contents = secret_path.read_text(encoding="utf-8").rstrip("\n")
            except OSError as exc:
                notes.append(f"secret file unreadable: {type(exc).__name__}")
                contents = ""
            if contents:
                return SecretResolution.found(contents)
            notes.append(f"secret file {secret_path} is empty")

    # --- 4. Final ------------------------------------------------------ #
    return SecretResolution.missing("; ".join(notes))


def _try_import_keyring() -> object | None:
    """Return the imported ``keyring`` module, or None if unavailable.

    Lazy import so the rest of Ember can run without ``keyring`` on the
    host. Per ADR 0010 §2.5 keyring is *optional*.
    """
    try:
        import keyring  # noqa: PLC0415 — lazy by design
    except ImportError:
        return None
    return keyring


def _resolve_username(config: PgVectorConfig) -> str | None:
    """Determine the username for keyring lookup.

    Order: ``PgVectorConfig.username`` → parse from URL.
    """
    if config.username:
        return config.username
    return _parse_username_from_url(config.url)


def _parse_username_from_url(url: str) -> str | None:
    """Pull the user out of ``postgresql://user@host/db`` or ``user:pw@``.

    Returns None if the URL doesn't carry one. Uses urllib.parse for
    portability — same shape psycopg's URL parser would see.
    """
    from urllib.parse import urlsplit  # noqa: PLC0415 — only needed here

    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    return parts.username or None


def _check_secret_file_mode(path: Path) -> str | None:
    """Return None if the file's permission bits are exactly 0o600,
    else an operator-facing reason string.

    Windows: ``st_mode`` doesn't carry Unix permission bits in a
    meaningful way; we skip the check there and trust the OS-level
    ACL. Linux / macOS get the strict 0o600 check.
    """
    if os.name == "nt":  # Windows — skip the Unix-bits check.
        return None
    try:
        st = path.stat()
    except OSError as exc:
        return f"secret file {path} stat() failed: {type(exc).__name__}"
    actual = stat.S_IMODE(st.st_mode)
    if actual != REQUIRED_FILE_MODE:
        return (
            f"secret file {path} has mode 0o{actual:03o}, "
            f"want 0o{REQUIRED_FILE_MODE:03o} (operator-readable only)"
        )
    return None


__all__ = [
    "DEFAULT_KEYRING_SERVICE",
    "DEFAULT_SECRET_ENV",
    "REQUIRED_FILE_MODE",
    "SecretResolution",
    "resolve",
]
