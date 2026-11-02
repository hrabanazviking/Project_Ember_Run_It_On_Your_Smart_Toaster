"""E-100 — Ember core binding to the toaster-Kista.

Pins ``docs/architecture/E-100_CORE_BINDING.md``:

* the companion fetches its model/API credentials from its
  own machine's toaster-Kista under E-097: it names itself
  ``ember-core`` (``KISTA_PROGRAM``), so it receives only the
  entries the owner gave to that program — the owner's own
  entries and other programs' entries refuse, and a missing
  entry answers identically;
* only the toaster set's credential kinds are fetched
  (``credential`` -> password, ``apikey`` -> key, E-098); any
  other kind is refused by the binding itself;
* the E-096 lock composes: with a passphrase set, a fetch
  without the passphrase (named env, never a prompt, never a
  config value) is refused, and with it the entry opens —
  still scoped to ``ember-core``;
* the two consumers: ``AesirFuni.open`` with ``api_key_entry``
  set fetches through the binding and never reads the key
  file; the Well secret resolver with ``kista_entry`` set
  takes the vault as its first and only source, with no
  fall-back to the interim chain;
* a fetched value is never named in any reason the binding
  or its consumers return;
* docket 134 is closed in scope: a vault write command holds
  the inter-process write lock (``.vault.lock``, flock) for
  its whole run, and the atomic write's temp name is
  per-process — two concurrent writers both land whole,
  proven by a two-writer probe; the drills are E-102's.

Probes run against scratch vaults holding synthetic entries
only, in the E-097 shape (scratch home, scratch vault dir,
the member + user site-packages on the child's path). No real
vault is ever touched.
"""

from __future__ import annotations

import importlib.util
import json
import os
import site
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-100_CORE_BINDING.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

sys.path.insert(0, str(REPO / "src"))

from ember.kista_binding import (  # noqa: E402
    CORE_PROGRAM,
    SECRET_FIELDS,
    fetch_credential,
)
from ember.schemas.config import KistaConfig  # noqa: E402

# A synthetic Aesir-shaped key: grammar-valid, obviously fake.
AESIR_KEY = "synthetic-aesir-key-0123456789abcdef"
WELL_PW = "synthetic-well-password"
OWNER_PW = "synthetic-owner-password"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


# ── The slice record, on file ───────────────────────────


def test_doc_records_the_binding():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "ember-core", "kista_program",
                   "fetch-only", "credential", "apikey",
                   "kista_passphrase", "never",
                   "docket 134", "e-102", "e-101", "e-103",
                   "e-104", "interim"):
        assert needle in text, needle


# ── The shape is the code's shape ───────────────────────


def test_binding_shape_in_code():
    src = (REPO / "src" / "ember" / "kista_binding.py").read_text(
        encoding="utf-8")
    assert CORE_PROGRAM == "ember-core"
    assert SECRET_FIELDS == {"credential": "password",
                             "apikey": "key"}
    assert '"KISTA_PROGRAM"' in src or '["KISTA_PROGRAM"]' in src
    assert "KISTA_PASSPHRASE" in src
    # Fetch-only: the binding issues exactly one vault verb.
    assert '"get"' in src
    for verb in ('"add"', '"update"', '"remove"', '"import"',
                 '"restore"', '"export"'):
        assert verb not in src, verb


def test_lock_shape_in_credstore():
    src = _source()
    assert "_WRITE_COMMANDS" in src
    assert "def _acquire_write_lock" in src
    assert ".vault.lock" in src
    assert "LOCK_EX" in src
    # The temp name is per-process now, never the shared one.
    assert "os.getpid()" in src
    assert 'path.suffix + ".tmp"' not in src


# ── Unit shape: the runner is injectable ────────────────


class _Proc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _cfg(tmp_path: Path) -> KistaConfig:
    return KistaConfig(
        enabled=True,
        vault_dir=tmp_path / "vault",
        credstore_path=CREDSTORE,
    )


def test_fetch_extracts_credential_and_apikey(tmp_path):
    def runner(argv, env):
        assert env["KISTA_PROGRAM"] == "ember-core"
        assert argv[-2] == "get"
        entry = {
            "entry_type": "credential",
            "password": "synthetic-unit-pw",
        } if argv[-1] == "site" else {
            "entry_type": "apikey", "key": "synthetic-unit-key"}
        return _Proc(0, json.dumps(entry))

    cfg = _cfg(tmp_path)
    got = fetch_credential("site", config=cfg, env={}, runner=runner)
    assert got.secret == "synthetic-unit-pw"
    got = fetch_credential("svc", config=cfg, env={}, runner=runner)
    assert got.secret == "synthetic-unit-key"


def test_fetch_refuses_non_credential_kinds(tmp_path):
    def runner(argv, env):
        return _Proc(0, json.dumps(
            {"entry_type": "note", "content": "a note"}))

    got = fetch_credential(
        "memo", config=_cfg(tmp_path), env={}, runner=runner)
    assert got.secret is None
    assert "not a model/API credential" in (got.reason or "")


def test_fetch_refusal_never_names_a_value(tmp_path):
    def runner(argv, env):
        return _Proc(1, "", "✗ No entry for this program")

    got = fetch_credential(
        "ghost", config=_cfg(tmp_path), env={}, runner=runner)
    assert got.secret is None
    assert "refused by the vault" in (got.reason or "")


def test_fetch_missing_program_is_a_reason(tmp_path):
    cfg = KistaConfig(
        enabled=True,
        vault_dir=tmp_path / "vault",
        credstore_path=tmp_path / "no-such-credstore.py",
    )
    got = fetch_credential("site", config=cfg, env={})
    assert got.secret is None
    assert "kista program not found" in (got.reason or "")


# ── Probes against a scratch vault ──────────────────────


def _run_cli(tmp_path: Path, vault: Path, *argv: str,
             program: str | None = None,
             passphrase: str | None = None,
             check: bool = True) -> subprocess.CompletedProcess:
    if importlib.util.find_spec("cryptography") is None:
        pytest.skip("cryptography absent in this environment")
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_PASSPHRASE", None)
    if program is not None:
        env["KISTA_PROGRAM"] = program
    if passphrase is not None:
        env["KISTA_PASSPHRASE"] = passphrase
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=check,
        stdin=subprocess.DEVNULL)


def _pw_file(tmp_path: Path, name: str, value: str) -> str:
    f = tmp_path / name
    f.write_text(value)
    return str(f)


def _scratch_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    _run_cli(tmp_path, vault, "init")
    _run_cli(tmp_path, vault, "add", "aesir", "--type", "apikey",
             "--key", AESIR_KEY, "--program", "ember-core")
    _run_cli(tmp_path, vault, "add", "well", "--username", "ember",
             "--password-file", _pw_file(tmp_path, "pw.txt", WELL_PW),
             "--program", "ember-core")
    _run_cli(tmp_path, vault, "add", "ownersite", "--username",
             "owner", "--password-file",
             _pw_file(tmp_path, "pw2.txt", OWNER_PW))
    return vault


def _binding_cfg(vault: Path) -> KistaConfig:
    return KistaConfig(
        enabled=True, vault_dir=vault, credstore_path=CREDSTORE)


def test_probe_binding_fetches_only_ember_cores_entries(tmp_path):
    vault = _scratch_vault(tmp_path)
    cfg = _binding_cfg(vault)
    got = fetch_credential("aesir", config=cfg, env={})
    assert got.secret == AESIR_KEY
    got = fetch_credential("well", config=cfg, env={})
    assert got.secret == WELL_PW
    # The owner's own entry is not the companion's: refused,
    # and the value appears nowhere in the reason.
    refused = fetch_credential("ownersite", config=cfg, env={})
    assert refused.secret is None
    assert OWNER_PW not in (refused.reason or "")
    # A missing entry answers the same way (E-097's shape,
    # inherited whole by the binding).
    missing = fetch_credential("nosuch", config=cfg, env={})
    assert missing.secret is None


def test_probe_binding_and_the_passphrase_lock_compose(tmp_path):
    vault = _scratch_vault(tmp_path)
    phrase = "correct horse battery staple"
    _run_cli(tmp_path, vault, "set-passphrase", passphrase=phrase)
    cfg = _binding_cfg(vault)
    locked = fetch_credential("aesir", config=cfg, env={})
    assert locked.secret is None
    assert AESIR_KEY not in (locked.reason or "")
    opened = fetch_credential(
        "aesir", config=cfg, env={"KISTA_PASSPHRASE": phrase})
    assert opened.secret == AESIR_KEY
    wrong = fetch_credential(
        "aesir", config=cfg, env={"KISTA_PASSPHRASE": "nope phrase"})
    assert wrong.secret is None


def test_probe_two_writers_both_land_whole(tmp_path):
    # Docket 134's shape, probed: two write runs at once —
    # with the write lock they serialise, and both entries
    # land whole (the pre-E-100 shape could interleave a
    # load/modify/save and silently drop one). E-102 drills
    # this harder; this probe proves the lock's first truth.
    vault = tmp_path / "vault"
    _run_cli(tmp_path, vault, "init")
    home = tmp_path / "home"
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_PASSPHRASE", None)
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    procs = []
    for i in range(2):
        pw = tmp_path / f"cpw{i}.txt"
        pw.write_text(f"synthetic-concurrent-{i}")
        procs.append(subprocess.Popen(
            [sys.executable, str(CREDSTORE), "add", f"conc{i}",
             "--username", "c", "--password-file", str(pw)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=env, stdin=subprocess.DEVNULL))
    for p in procs:
        out, err = p.communicate(timeout=120)
        assert p.returncode == 0, err
    assert (vault / ".vault.lock").exists()
    listing = _run_cli(tmp_path, vault, "list").stdout
    assert "conc0" in listing and "conc1" in listing
    for i in range(2):
        got = _run_cli(tmp_path, vault, "get", f"conc{i}").stdout
        assert f"synthetic-concurrent-{i}" in got


# ── The consumers ───────────────────────────────────────


def _ready_response():
    payload = {
        "schema_version": 1, "status": "ready", "ready": True,
        "backend": "cuda", "model": "gemma4-e2b:latest",
        "context": 512,
    }
    body = json.dumps(payload).encode()

    class _Resp:
        def read(self):
            return body

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

    return _Resp()


def test_aesir_open_fetches_its_key_from_the_vault(tmp_path):
    from ember.schemas.config import (
        FuniAesirConfig,
        FuniConfig,
        FuniRuntime,
    )
    from ember.schemas.funi import Unavailable
    from ember.spark.funi.aesir.adapter import AesirFuni

    vault = _scratch_vault(tmp_path)
    cfg = FuniConfig(
        runtime=FuniRuntime.AESIR,
        aesir=FuniAesirConfig(
            api_key_file=tmp_path / "never-read.key",
            api_key_entry="aesir",
        ),
    )
    captured = {}

    def fake_urlopen(request, *, timeout=0.0):
        captured["auth"] = request.headers.get("Authorization")
        return _ready_response()

    # AesirFuni.open probes readiness with a bare GET (no key
    # header); capture the adapter instead via complete()'s
    # header — open's probe is unauthenticated by design, so
    # assert the opened adapter holds the vault's key by
    # driving a completion and reading its Authorization.
    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        opened = AesirFuni.open(
            cfg, kista_config=_binding_cfg(vault), env={})
    assert not isinstance(opened, Unavailable), opened
    assert opened.model_id == "gemma4-e2b:latest"

    def fake_generate(request, *, timeout=0.0):
        captured["auth"] = request.get_header("Authorization")
        body = json.dumps({
            "text": "hello", "finish_reason": "eos",
            "prompt_tokens": 3, "generated_tokens": 1,
        }).encode()

        class _Resp:
            def read(self):
                return body

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

        return _Resp()

    with patch("urllib.request.urlopen", side_effect=fake_generate):
        reply = opened.complete("hi", [])
    assert reply.text == "hello"
    assert captured["auth"] == f"Bearer {AESIR_KEY}"


def test_aesir_open_vault_refusal_is_config_invalid(tmp_path):
    from ember.schemas.config import (
        FuniAesirConfig,
        FuniConfig,
        FuniRuntime,
    )
    from ember.schemas.funi import Unavailable, UnavailableReason
    from ember.spark.funi.aesir.adapter import AesirFuni

    vault = _scratch_vault(tmp_path)
    cfg = FuniConfig(
        runtime=FuniRuntime.AESIR,
        aesir=FuniAesirConfig(
            api_key_file=tmp_path / "never-read.key",
            api_key_entry="ownersite",  # not ember-core's entry
        ),
    )
    result = AesirFuni.open(
        cfg, kista_config=_binding_cfg(vault), env={})
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
    assert OWNER_PW not in (result.detail or "")
    assert "toaster-Kista" in (result.detail or "")


def test_well_resolver_takes_the_vault_as_its_only_source(tmp_path):
    from ember.schemas.config import PgVectorConfig
    from ember.well.brunnr.pgvector import secrets as well_secrets

    def runner(argv, env):
        assert env["KISTA_PROGRAM"] == "ember-core"
        return _Proc(0, json.dumps(
            {"entry_type": "credential", "password": WELL_PW}))

    cfg = PgVectorConfig(
        url="postgresql://ember@127.0.0.1/well",
        kista_entry="well",
        secret_env="EMBER_WELL_PASSWORD",
    )
    # The env carries a different value: with a vault entry
    # named, the interim chain is retired for this secret and
    # the vault's value — not the env's — is the resolution.
    got = well_secrets.resolve(
        cfg,
        env={"EMBER_WELL_PASSWORD": "synthetic-env-value"},
        kista_runner=runner,
    )
    assert got.secret == WELL_PW

    def refusing_runner(argv, env):
        return _Proc(1, "", "✗ refused")

    refused = well_secrets.resolve(
        cfg,
        env={"EMBER_WELL_PASSWORD": "synthetic-env-value"},
        kista_runner=refusing_runner,
    )
    assert refused.secret is None
    assert "only source tried" in (refused.reason or "")
