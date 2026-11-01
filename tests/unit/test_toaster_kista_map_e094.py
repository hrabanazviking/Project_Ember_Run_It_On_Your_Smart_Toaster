"""E-094 — Toaster-Kista mapped, docket 46 built.

Pins ``docs/architecture/E-094_TOASTER_KISTA_MAPPED.md``:

* the program in ``kista/`` is the one mapped — one file,
  Fernet whole-vault encryption, a separate key file,
  the storage names, 14 entry types and 32 subcommands,
  every surface fact derived from the code itself;
* docket 46 stands built: with the override variable
  unset the vault home resolves under the owner's own
  Ember home, and with it set the override wins —
  proven by sandboxed probes that create nothing in
  the probed home;
* docket 5 stands closed: the member suite resolves
  the in-tree script beside its tests, its stale
  version expectation is corrected to the program's
  true version, and the map records the suite's
  before/after counts.

The probes never touch a real vault home: each runs
with a scratch home and the member directory on its
path, the custody discipline the campaign works under.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import re
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-094_TOASTER_KISTA_MAPPED.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"
MEMBER_TESTS = KISTA / "tests" / "test_credstore.py"

ENTRY_TYPES = {
    "credential", "apikey", "sshkey", "certificate",
    "note", "totp", "license", "identity", "url",
    "astrology", "character-sheet", "rune-reading",
    "tarot-reading", "markdown",
}

CORE_COMMANDS = {
    "init", "repair", "add", "get", "list", "update",
    "remove", "check", "search", "generate-password",
    "status", "export", "import", "backup", "restore",
    "github-backup", "add-soul", "add-cron-backup",
    "config",
}
SHORTCUT_COMMANDS = {
    "add-apikey", "add-sshkey", "add-certificate",
    "add-note", "add-totp", "add-license",
    "add-identity", "add-astrology",
    "add-character-sheet", "add-rune-reading",
    "add-tarot-reading", "add-markdown", "add-person",
}


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


# ── The map, on record ──────────────────────────────────


def test_doc_records_the_map():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("in plain words", "~/.ember/kista/",
                   "docket 46", "CLOSED", "Fernet",
                   "149 passed, 0 failed",
                   "146 passed, 3 failed", "docket 5",
                   "docket 14", "docket 130", "E-095",
                   "E-096", "E-098", "E-100", "E-104",
                   "no vault passphrase",
                   "32 subcommands", "14 entry types"):
        assert needle in text, needle


# ── The surface, derived from the code ──────────────────


def test_entry_types_are_the_mapped_fourteen():
    tree = ast.parse(_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(
                node.targets[0], "id", "") == "ENTRY_TYPE_SCHEMAS":
            assert {k.value for k in node.value.keys} == ENTRY_TYPES
            return
    raise AssertionError("ENTRY_TYPE_SCHEMAS not found")


def test_subcommands_are_the_mapped_thirty_two():
    src = _source()
    named = set(re.findall(r'add_parser\("([^"]+)"', src))
    named.discard("set")  # only a config child, never top level
    shortcuts = {"add-" + t for t in (
        "apikey", "sshkey", "certificate", "note", "totp",
        "license", "identity", "astrology",
        "character-sheet", "rune-reading", "tarot-reading",
        "markdown")} | {"add-person"}
    assert shortcuts == SHORTCUT_COMMANDS
    assert CORE_COMMANDS | SHORTCUT_COMMANDS == (
        named | SHORTCUT_COMMANDS)
    assert len(CORE_COMMANDS | SHORTCUT_COMMANDS) == 32


def test_crypto_and_storage_shape():
    src = _source()
    assert "from cryptography.fernet import Fernet" in src
    assert '".vault_key"' in src or '".vault_key"' in src.replace("'", '"')
    for name in ('"vault.json.enc"', '"vault_meta.json"',
                 '"config.json"', '"backups"'):
        assert name in src, name
    assert '__version__ = "2.0.0"' in src
    assert "scripts.credstore:main" in (
        KISTA / "pyproject.toml").read_text(encoding="utf-8")


# ── Docket 46, proven by probe ──────────────────────────


def _probe(tmp_path: Path, extra_env: dict) -> str:
    if importlib.util.find_spec("cryptography") is None:
        import pytest
        pytest.skip("cryptography absent in this environment")
    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ)
    env["HOME"] = str(home)
    env.pop("KISTA_DIR", None)
    env.update(extra_env)
    path_parts = [str(KISTA), site.getusersitepackages(),
                  env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in path_parts if p)
    out = subprocess.run(
        [sys.executable, "-c",
         "import scripts.credstore as cs; print(cs.VAULT_DIR)"],
        capture_output=True, text=True, env=env, check=True)
    # Importing the module creates nothing in the probed home.
    assert list(home.iterdir()) == []
    return out.stdout.strip()


def test_default_home_is_embers_own(tmp_path):
    got = _probe(tmp_path, {})
    assert got == str(tmp_path / "home" / ".ember" / "kista")


def test_override_still_wins(tmp_path):
    target = str(tmp_path / "elsewhere")
    got = _probe(tmp_path, {"KISTA_DIR": target})
    assert got == target


def test_source_default_names_no_other_home():
    for line in _source().splitlines():
        if line.startswith("VAULT_DIR ="):
            assert '".ember"' in line and '"kista"' in line
            assert '".hermes"' not in line
            return
    raise AssertionError("VAULT_DIR assignment not found")


# ── Docket 5, closed in the member harness ──────────────


def test_member_suite_resolves_the_in_tree_script():
    text = MEMBER_TESTS.read_text(encoding="utf-8")
    assert 'Path(__file__).resolve().parents[1]' in text
    assert "runa-credentials" not in text
    assert '"2.0.0" in result.stdout' in text
    assert '"1.3.0" in result.stdout' not in text
    # The fixture patches every vault path, config included.
    assert '"VAULT_CONFIG"' in text and '"BACKUP_DIR"' in text
