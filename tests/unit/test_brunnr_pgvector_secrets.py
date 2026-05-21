"""ADR 0010 §2.5 — secret resolver order, mode-600 enforcement, no leaks.

These tests do not require Postgres; they drive
``secrets.resolve(config)`` with injected env dicts, a fake keyring,
and tmp-path secret files. The live-DB exercise lands in Phase 13's
``tests/integration/test_pgvector_real_backend.py``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ember.schemas.config import PgVectorConfig
from ember.well.brunnr.pgvector import secrets

# --------------------------------------------------------------------- #
# Helpers / fakes                                                        #
# --------------------------------------------------------------------- #


class _FakeKeyring:
    def __init__(self, store: dict[tuple[str, str], str] | None = None) -> None:
        self._store = store or {}
        self.lookups: list[tuple[str, str]] = []

    def get_password(self, service: str, username: str) -> str | None:
        self.lookups.append((service, username))
        return self._store.get((service, username))


def _config(  # noqa: PLR0913 — test factory mirrors PgVectorConfig's keyword surface
    *,
    url: str = "postgresql://volmarr@gungnir/knowledge",
    secret_ref: Path,
    secret_env: str = "EMBER_WELL_PASSWORD",
    use_keyring: bool = True,
    keyring_service: str = "ember-well",
    username: str | None = None,
) -> PgVectorConfig:
    return PgVectorConfig(
        url=url,
        secret_ref=secret_ref,
        secret_env=secret_env,
        use_keyring=use_keyring,
        keyring_service=keyring_service,
        username=username,
    )


def _write_secret_file(path: Path, body: str, *, mode: int = 0o600) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(mode)
    return path


# --------------------------------------------------------------------- #
# 1. Env var wins, full stop                                            #
# --------------------------------------------------------------------- #


def test_env_var_wins_over_keyring_and_file(tmp_path: Path) -> None:
    secret_path = _write_secret_file(tmp_path / "file.pw", "file-secret")
    kr = _FakeKeyring({("ember-well", "volmarr"): "keyring-secret"})

    res = secrets.resolve(
        _config(secret_ref=secret_path),
        env={"EMBER_WELL_PASSWORD": "env-secret"},
        keyring_module=kr,
    )

    assert res.secret == "env-secret"
    assert res.reason is None
    # Env hit short-circuits — keyring is never consulted.
    assert kr.lookups == []


def test_env_var_with_custom_name_resolves(tmp_path: Path) -> None:
    res = secrets.resolve(
        _config(
            secret_ref=tmp_path / "missing.pw",
            secret_env="MY_CUSTOM_PASSWORD",
            use_keyring=False,
        ),
        env={"MY_CUSTOM_PASSWORD": "custom-env"},
        keyring_module=None,
    )
    assert res.secret == "custom-env"


def test_empty_env_var_is_treated_as_missing(tmp_path: Path) -> None:
    res = secrets.resolve(
        _config(secret_ref=tmp_path / "missing.pw", use_keyring=False),
        env={"EMBER_WELL_PASSWORD": ""},
        keyring_module=None,
    )
    assert res.secret is None
    assert "env $EMBER_WELL_PASSWORD not set" in (res.reason or "")


# --------------------------------------------------------------------- #
# 2. Keyring is consulted when env missing                              #
# --------------------------------------------------------------------- #


def test_keyring_resolves_when_env_missing(tmp_path: Path) -> None:
    kr = _FakeKeyring({("ember-well", "volmarr"): "keyring-secret"})
    res = secrets.resolve(
        _config(secret_ref=tmp_path / "missing.pw"),
        env={},
        keyring_module=kr,
    )
    assert res.secret == "keyring-secret"
    assert kr.lookups == [("ember-well", "volmarr")]


def test_keyring_skipped_when_use_keyring_false(tmp_path: Path) -> None:
    secret_path = _write_secret_file(tmp_path / "file.pw", "file-secret")
    kr = _FakeKeyring({("ember-well", "volmarr"): "would-have-won"})
    res = secrets.resolve(
        _config(secret_ref=secret_path, use_keyring=False),
        env={},
        keyring_module=kr,
    )
    # File wins because keyring is disabled in config.
    assert res.secret == "file-secret"
    assert kr.lookups == []  # never consulted


def test_keyring_username_falls_through_when_no_user_in_url(tmp_path: Path) -> None:
    """URL without a user → resolver skips keyring instead of crashing."""
    kr = _FakeKeyring()
    res = secrets.resolve(
        _config(
            url="postgresql://gungnir/knowledge",  # no user
            secret_ref=tmp_path / "missing.pw",
            username=None,
        ),
        env={},
        keyring_module=kr,
    )
    assert res.secret is None
    assert kr.lookups == []
    assert "no username" in (res.reason or "")


def test_explicit_username_overrides_url_parse(tmp_path: Path) -> None:
    kr = _FakeKeyring({("ember-well", "operator"): "op-secret"})
    res = secrets.resolve(
        _config(
            url="postgresql://different_user@host/db",
            secret_ref=tmp_path / "missing.pw",
            username="operator",
        ),
        env={},
        keyring_module=kr,
    )
    assert res.secret == "op-secret"


def test_custom_keyring_service_is_used(tmp_path: Path) -> None:
    kr = _FakeKeyring({("my-service", "volmarr"): "custom-keyring-secret"})
    res = secrets.resolve(
        _config(secret_ref=tmp_path / "missing.pw", keyring_service="my-service"),
        env={},
        keyring_module=kr,
    )
    assert res.secret == "custom-keyring-secret"


def test_keyring_lookup_exception_is_treated_as_miss(tmp_path: Path) -> None:
    class _RaisingKeyring:
        def get_password(self, service: str, username: str) -> str | None:
            raise RuntimeError("backend locked")

    res = secrets.resolve(
        _config(secret_ref=tmp_path / "missing.pw"),
        env={},
        keyring_module=_RaisingKeyring(),
    )
    assert res.secret is None
    assert "RuntimeError" in (res.reason or "")


# --------------------------------------------------------------------- #
# 3. Mode-600 file enforcement                                          #
# --------------------------------------------------------------------- #


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_mode_600_file_resolves(tmp_path: Path) -> None:
    secret_path = _write_secret_file(tmp_path / "good.pw", "from-file", mode=0o600)
    res = secrets.resolve(
        _config(secret_ref=secret_path, use_keyring=False),
        env={},
        keyring_module=None,
    )
    assert res.secret == "from-file"


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_mode_644_file_is_refused(tmp_path: Path) -> None:
    bad_path = _write_secret_file(tmp_path / "bad.pw", "would-leak", mode=0o644)
    res = secrets.resolve(
        _config(secret_ref=bad_path, use_keyring=False),
        env={},
        keyring_module=None,
    )
    assert res.secret is None
    reason = res.reason or ""
    assert "mode" in reason
    assert "0o644" in reason
    assert "0o600" in reason
    # The leak protection: the body must NEVER appear in the reason.
    assert "would-leak" not in reason


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_mode_604_file_is_refused(tmp_path: Path) -> None:
    """World-readable is refused even when group has no perms."""
    bad_path = _write_secret_file(tmp_path / "bad.pw", "anything", mode=0o604)
    res = secrets.resolve(
        _config(secret_ref=bad_path, use_keyring=False),
        env={},
        keyring_module=None,
    )
    assert res.secret is None
    assert "0o604" in (res.reason or "")


def test_empty_file_is_treated_as_missing(tmp_path: Path) -> None:
    empty_path = _write_secret_file(tmp_path / "empty.pw", "", mode=0o600)
    res = secrets.resolve(
        _config(secret_ref=empty_path, use_keyring=False),
        env={},
        keyring_module=None,
    )
    assert res.secret is None
    assert "empty" in (res.reason or "")


def test_file_with_trailing_newline_is_stripped(tmp_path: Path) -> None:
    """Operators paste with trailing newlines; the resolver trims them."""
    path = _write_secret_file(tmp_path / "good.pw", "hello\n", mode=0o600)
    res = secrets.resolve(
        _config(secret_ref=path, use_keyring=False),
        env={},
        keyring_module=None,
    )
    assert res.secret == "hello"


# --------------------------------------------------------------------- #
# 4. Final-failure reason aggregates every source tried                 #
# --------------------------------------------------------------------- #


def test_total_miss_reason_lists_every_source(tmp_path: Path) -> None:
    kr = _FakeKeyring()
    res = secrets.resolve(
        _config(secret_ref=tmp_path / "missing.pw"),
        env={},
        keyring_module=kr,
    )
    assert res.secret is None
    reason = res.reason or ""
    assert "env $EMBER_WELL_PASSWORD" in reason
    assert "keyring entry" in reason
    assert "not found" in reason


# --------------------------------------------------------------------- #
# 5. The "no secret in error messages" invariant                        #
# --------------------------------------------------------------------- #


def test_secret_value_never_appears_in_resolution_reason(tmp_path: Path) -> None:
    """No path through the resolver should put the resolved value in
    .reason — even on partial success (e.g. when env wins but file
    was unreadable). This is the security guarantee from ADR 0010 §2.5."""
    secret_path = _write_secret_file(tmp_path / "file.pw", "filebody", mode=0o644)
    res = secrets.resolve(
        _config(secret_ref=secret_path),
        env={"EMBER_WELL_PASSWORD": "envbody"},
        keyring_module=_FakeKeyring(),
    )
    # Env wins, but the file path was also walked (no — actually env
    # short-circuits, so the file isn't read; but just in case it ever
    # changes, assert the body would still not leak).
    assert res.secret == "envbody"
    assert "filebody" not in (res.reason or "")
    assert "envbody" not in (res.reason or "")
