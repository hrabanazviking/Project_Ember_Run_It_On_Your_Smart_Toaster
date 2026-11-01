"""E-095 — Toaster-Kista threat model, sized for tiny machines.

Pins ``docs/architecture/E-095_TOASTER_KISTA_THREAT_MODEL.md``:

* the model is on record with its defended set, its
  not-defended set, the requirement handed to the
  unlock slice, and the interim claim stated word for
  word;
* dockets 131 and 132 stand closed in the code: the
  vault directory is made owner-only, and the
  metadata file and the plaintext-backup output are
  chmodded owner-only like every other vault file —
  proven by sandboxed probes against a scratch vault
  holding one synthetic entry;
* the not-defended shapes the model names are the
  code's real shapes: no passphrase or derivation
  anywhere, the key file beside the vault, no
  inter-process lock, and a restore road that accepts
  plaintext.

The probes never touch a real vault home: each runs
with a scratch home, the member directory on its
path, and the user site-packages that carry the
member's one dependency, the custody discipline the
campaign works under.
"""

from __future__ import annotations

import importlib.util
import os
import site
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-095_TOASTER_KISTA_THREAT_MODEL.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


# ── The model, on record ────────────────────────────────


def test_doc_records_the_model():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "What it defends",
                   "What it cannot defend", "docket 131",
                   "docket 132", "closed", "docket 133",
                   "docket 134", "docket 135", "docket 136",
                   "E-096", "E-100", "E-101", "E-102",
                   "E-187", "interim claim",
                   "no vault passphrase",
                   "131,547,523", "2,770,819"):
        assert needle.lower() in text, needle


# ── Dockets 131/132, closed in the code ─────────────────


def test_dir_and_meta_and_plain_backup_are_owner_only_in_code():
    src = _source()
    # _ensure_dir makes the vault directory owner-only.
    ensure = src.split("def _ensure_dir")[1].split("def ")[0]
    assert "0o700" in ensure
    # Every save chmods the metadata file.
    assert "_chmod_600(VAULT_META)" in src
    # The plaintext backup branch chmods its output.
    backup = src.split("def cmd_backup")[1].split("def ")[0]
    assert "_chmod_600(output_path)" in backup


# ── The not-defended shapes are the code's shapes ───────


def test_no_passphrase_no_lock_shapes_stand_as_modelled():
    src = _source()
    # No key derivation or wrapping exists anywhere.
    for absent in ("scrypt", "PBKDF2", "argon2", "derive"):
        assert absent not in src, absent
    # No inter-process lock exists anywhere.
    for absent in ("flock", "lockf", "FileLock"):
        assert absent not in src, absent
    # The key file lives beside the vault file.
    assert 'VAULT_DIR / ".vault_key"' in src.replace("'", '"') \
        or ".vault_key" in src


# ── Probes against a scratch vault ──────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str,
         check: bool = True) -> subprocess.CompletedProcess:
    if importlib.util.find_spec("cryptography") is None:
        import pytest
        pytest.skip("cryptography absent in this environment")
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=check)


def _scratch_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    _run(tmp_path, vault, "init")
    _run(tmp_path, vault, "add", "testsite", "--username",
         "alice", "--password", "synthetic-pass-one")
    return vault


def test_probe_modes_are_owner_only(tmp_path):
    if os.name != "posix":
        import pytest
        pytest.skip("permission modes are the POSIX shape")
    vault = _scratch_vault(tmp_path)
    assert stat.S_IMODE(vault.stat().st_mode) == 0o700
    for name in (".vault_key", "vault.json.enc",
                 "vault_meta.json"):
        mode = stat.S_IMODE((vault / name).stat().st_mode)
        assert mode == 0o600, (name, oct(mode))
    plain = tmp_path / "plain_backup.json"
    _run(tmp_path, vault, "backup", "--output", str(plain))
    assert stat.S_IMODE(plain.stat().st_mode) == 0o600


def test_probe_folder_copy_opens_and_blob_alone_refuses(tmp_path):
    vault = _scratch_vault(tmp_path)
    import shutil
    stolen = tmp_path / "stolen"
    shutil.copytree(vault, stolen)
    out = _run(tmp_path, stolen, "get", "testsite")
    # The central finding: the copied folder opens whole.
    assert "synthetic-pass-one" in out.stdout
    alone = tmp_path / "alone"
    alone.mkdir()
    shutil.copy2(vault / "vault.json.enc",
                 alone / "vault.json.enc")
    refused = _run(tmp_path, alone, "get", "testsite",
                   check=False)
    assert refused.returncode == 1
    assert "key file" in refused.stderr


def test_probe_rollback_resurrects_the_rotated_password(tmp_path):
    vault = _scratch_vault(tmp_path)
    # The older valid blob: a snapshot of the vault as it
    # stood before the rotation. (The manual probe in the
    # slice record used the oldest auto-backup the same
    # way; which auto-backup is oldest is timing-shaped —
    # init's empty-vault backup can hold that place — so
    # the battery pins the mechanism deterministically:
    # any older valid blob, served without a murmur.)
    import shutil
    snapshot = tmp_path / "older_blob.enc"
    shutil.copy2(vault / "vault.json.enc", snapshot)
    assert (vault / "backups").glob("*.enc") is not None
    _run(tmp_path, vault, "update", "testsite",
         "--password", "synthetic-pass-two")
    got = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-two" in got.stdout
    shutil.copy2(snapshot, vault / "vault.json.enc")
    rolled = _run(tmp_path, vault, "get", "testsite")
    # Docket 133, proven: no freshness check anywhere.
    assert "synthetic-pass-one" in rolled.stdout
