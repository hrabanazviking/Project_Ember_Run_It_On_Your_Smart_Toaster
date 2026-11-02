"""E-101 — Backup & restore of a tiny vault: the
user-carried file.

Pins ``docs/architecture/E-101_CARRIED_BACKUP.md``:

* the carried file — ``backup --carry`` writes the
  whole vault encrypted under a backup passphrase the
  user chooses (scrypt, the E-096 derivation; never
  the vault key), and ``restore`` opens it into a
  vault holding a *different* key, on the passphrase
  alone — the road E-095/E-099 proved missing;
* a copied carried file without its passphrase opens
  nothing: wrong passphrase and no passphrase are both
  plain refusals, and the destination holds nothing
  afterwards;
* docket 138 — the plain backup road is no longer a
  silent, unauthenticated whole-vault crossing
  between different-key vaults: a plain restore is
  refused without ``--allow-plaintext``, and with it
  the warning prints before anything is restored
  (the E-099 battery's plain-road probe is re-pinned
  consciously at this slice to the new shape);
* docket 135 — ``github-backup`` names its harvest
  shape at the moment of use (history keeps every
  pushed blob; every blob opens under the one vault
  key; the program cannot check the repo is private)
  and its staging file is owner-only.

Probes run scratch vaults with synthetic entries
only, exactly as at E-099; no real vault is touched.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import site
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-101_CARRIED_BACKUP.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

CARRY_PW = "synthetic-carry-passphrase"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


def _section(src: str, start: str, end: str) -> str:
    return src[src.index(start):src.index(end)]


# ── The slice record, on file ───────────────────────────


def test_doc_records_the_carried_road_and_both_dockets():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "user-carried",
                   "backup passphrase", "different key",
                   "opens nothing", "docket 138",
                   "docket 135", "history",
                   "--allow-plaintext", "e-102", "e-104"):
        assert needle in text, needle


# ── The built shape, in code ────────────────────────────


def test_carry_file_is_passphrase_encrypted_never_vault_key():
    src = _source()
    assert 'CARRY_MARKER = "kista_carry_backup"' in src
    assert "_derive_wrapping_key" in _section(
        src, "def _make_carry_file", "def _carry_doc")
    backup = _section(src, "def cmd_backup", "def cmd_restore")
    assert 'getattr(args, "carry", False)' in backup
    assert "_make_carry_file(export_data, passphrase)" in backup
    assert "_chmod_600(carry_path)" in backup


def test_backup_passphrase_never_comes_from_an_argument():
    src = _source()
    assert "KISTA_BACKUP_PASSPHRASE" in src
    # No parser anywhere takes a backup-passphrase value:
    # the passphrase arrives by environment or hidden
    # prompt only, never as a command-line argument.
    assert "backup-passphrase" not in src


def test_plain_restore_is_gated_in_code():
    restore = _section(_source(), "def cmd_restore",
                       "def cmd_github_backup")
    assert "allow_plaintext" in restore
    assert "plain, unencrypted text" in restore


def test_github_backup_names_the_harvest_shape_in_code():
    gh = _section(_source(), "def cmd_github_backup",
                  "def cmd_add_soul")
    assert "stays in that repository's" in gh
    assert "cannot check whether that repository" in gh
    assert "_chmod_600(backup_file)" in gh


def test_surface_stays_thirty_five():
    # --carry and --allow-plaintext are flags on existing
    # commands, not new subcommands (E-098's count stands;
    # the exact surface count is E-098's battery's pin).
    src = _source()
    assert '"backup": cmd_backup' in src
    assert '"restore": cmd_restore' in src


# ── Probes against scratch vaults ───────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str,
         check: bool = True, carry_pw: str | None = None,
         ) -> subprocess.CompletedProcess:
    if importlib.util.find_spec("cryptography") is None:
        import pytest
        pytest.skip("cryptography absent in this environment")
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_PASSPHRASE", None)
    if carry_pw is None:
        env.pop("KISTA_BACKUP_PASSPHRASE", None)
    else:
        env["KISTA_BACKUP_PASSPHRASE"] = carry_pw
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=check,
        stdin=subprocess.DEVNULL)


def _source_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vaultA"
    _run(tmp_path, vault, "init")
    pw = tmp_path / "pw.txt"
    pw.write_text("synthetic-pw-A")
    _run(tmp_path, vault, "add", "site", "--username", "u",
         "--password-file", str(pw))
    _run(tmp_path, vault, "add", "key", "--type", "apikey",
         "--key", "synthetic-token-A")
    _run(tmp_path, vault, "add", "memo", "--type", "note",
         "--content", "synthetic note A")
    return vault


def _carry(tmp_path: Path, vault: Path) -> Path:
    out = tmp_path / "carried.enc"
    _run(tmp_path, vault, "backup", "--carry",
         "--output", str(out), carry_pw=CARRY_PW)
    return out


def _names(tmp_path: Path, vault: Path) -> str:
    return _run(tmp_path, vault, "list").stdout


def test_probe_carry_file_holds_no_plaintext_and_no_key(tmp_path):
    a = _source_vault(tmp_path)
    carried = _carry(tmp_path, a)
    raw = carried.read_bytes()
    assert b"synthetic-pw-A" not in raw
    assert b"synthetic-token-A" not in raw
    assert (a / ".vault_key").read_bytes().strip() not in raw
    doc = json.loads(raw)
    assert doc["kista_carry_backup"] == 1
    assert stat.S_IMODE(carried.stat().st_mode) == 0o600


def test_probe_carry_restores_into_a_different_key_vault(tmp_path):
    a = _source_vault(tmp_path)
    carried = _carry(tmp_path, a)
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    assert (b / ".vault_key").read_bytes() != \
        (a / ".vault_key").read_bytes()
    out = _run(tmp_path, b, "restore", str(carried),
               carry_pw=CARRY_PW).stdout
    assert "Restored 3 new" in out
    assert "synthetic-pw-A" in _run(tmp_path, b, "get", "site").stdout
    assert "synthetic-token-A" in _run(tmp_path, b, "get", "key").stdout


def test_probe_wrong_passphrase_restores_nothing(tmp_path):
    a = _source_vault(tmp_path)
    carried = _carry(tmp_path, a)
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    refused = _run(tmp_path, b, "restore", str(carried),
                   check=False, carry_pw="wrong-passphrase-1")
    assert refused.returncode == 1
    assert "did not open this file" in refused.stderr
    assert "site" not in _names(tmp_path, b)


def test_probe_no_passphrase_restores_nothing(tmp_path):
    a = _source_vault(tmp_path)
    carried = _carry(tmp_path, a)
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    refused = _run(tmp_path, b, "restore", str(carried),
                   check=False)
    assert refused.returncode == 1
    assert "No backup passphrase was given" in refused.stderr
    assert "site" not in _names(tmp_path, b)


def test_probe_plain_restore_refused_without_the_word(tmp_path):
    # Docket 138: the E-099 crossing no longer happens
    # silently — synthetic entries only, as there.
    a = _source_vault(tmp_path)
    bk = tmp_path / "plain.json"
    _run(tmp_path, a, "backup", "--output", str(bk))
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    refused = _run(tmp_path, b, "restore", str(bk), check=False)
    assert refused.returncode == 1
    assert "plain, unencrypted text" in refused.stderr
    assert "--allow-plaintext" in refused.stderr
    assert "site" not in _names(tmp_path, b)


def test_probe_plain_restore_with_the_word_warns_and_restores(tmp_path):
    a = _source_vault(tmp_path)
    bk = tmp_path / "plain.json"
    _run(tmp_path, a, "backup", "--output", str(bk))
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    out = _run(tmp_path, b, "restore", str(bk),
               "--allow-plaintext")
    assert "PLAIN backup" in out.stdout
    assert "Restored 3 new" in out.stdout
    assert "synthetic-pw-A" in _run(tmp_path, b, "get", "site").stdout


def test_probe_github_backup_warns_before_it_writes(tmp_path):
    a = _source_vault(tmp_path)
    out = _run(tmp_path, a, "github-backup",
               "--repo", "https://example.com/x/y.git")
    assert "stays in that repository's" in out.stdout
    assert "cannot check whether that repository" in out.stdout
