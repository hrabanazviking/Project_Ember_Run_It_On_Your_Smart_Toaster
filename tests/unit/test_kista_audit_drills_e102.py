"""E-102 — Audit fixtures for the toaster-Kista: the drills.

Pins ``docs/architecture/E-102_AUDIT_DRILLS.md``:

* wrong-passphrase drills — a wrapped vault refuses a
  wrong passphrase plainly and every vault file is left
  byte-identical; a carried file (E-101) under a wrong
  passphrase restores nothing;
* tampered-vault drills — a flipped byte in the vault
  blob is caught by the Fernet HMAC and healed from the
  newest auto-backup; with no backups left, the refusal
  is plain, the damaged file is left exactly as it
  stands, and no new key is ever minted over data;
* partial-write drills — a truncated vault blob answers
  exactly like the tampered one; a crashed atomic write's
  leftover temp file is ignored and the vault serves its
  last whole state; a truncated, emptied, or torn key
  file is a plain refusal in the validator's own words,
  never a traceback (docket 139, CLOSED in this slice —
  before the fix these shapes raised a raw ValueError
  traceback at every key-loading command);
* tampered carried-envelope drills (E-101's shapes,
  proven as drills here, not inferred) — a flipped
  character in the carried token is the same "did not
  open" refusal as a wrong passphrase, a torn salt is a
  stated "damaged", a half-written carried file is a
  stated read failure, and in every case the destination
  vault holds nothing afterwards;
* the lock drill (E-100's docket-134 shape) — a second
  process holding the vault's flock blocks a writer
  until it lets go, the writer then lands whole, and
  two writers at once both land: no lost update;
* the rollback drill (docket 133) — an older valid blob
  still resurrects a rotated-away password with no
  warning. NOT defended, stated: this battery pins the
  behaviour as the standing finding E-106's gate must
  carry in the Part VI verdict, because no freshness
  shape kept inside the same folder can honestly claim
  otherwise (the doc weighs the candidate remedies).

Probes run scratch vaults with synthetic entries only,
exactly as at E-095–E-101; no real vault is touched.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import site
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-102_AUDIT_DRILLS.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

PASSPHRASE = "correct horse battery staple"
CARRY_PW = "synthetic-carry-passphrase"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


def _section(src: str, start: str, end: str) -> str:
    return src[src.index(start):src.index(end)]


# ── The slice record, on file ───────────────────────────


def test_doc_records_the_drills_and_the_verdicts():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "wrong-passphrase",
                   "tampered-vault", "partial-write",
                   "lock drill", "carried envelope",
                   "docket 139", "closed", "docket 133",
                   "not defended", "e-106",
                   "2,820,119", "131,612,827"):
        assert needle in text, needle


# ── Docket 139, closed in the code ──────────────────────


def test_key_validation_refuses_plainly_in_code():
    src = _source()
    helper = _section(src, "def _validate_key_or_exit",
                      "def _is_wrapped_key")
    assert "except ValueError" in helper
    assert "sys.exit(1)" in helper
    get_key = _section(src, "def _get_key", "def _encrypt")
    assert "return _validate_key_or_exit(raw)" in get_key


# ── Probes against scratch vaults ───────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str,
         check: bool = True, passphrase: str | None = None,
         carry_pw: str | None = None,
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
    env.pop("KISTA_BACKUP_PASSPHRASE", None)
    if passphrase is not None:
        env["KISTA_PASSPHRASE"] = passphrase
    if carry_pw is not None:
        env["KISTA_BACKUP_PASSPHRASE"] = carry_pw
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=check,
        stdin=subprocess.DEVNULL)


def _scratch_vault(tmp_path: Path, name: str = "vault") -> Path:
    vault = tmp_path / name
    _run(tmp_path, vault, "init")
    pw = tmp_path / "pw.txt"
    pw.write_text("synthetic-pass-one")
    _run(tmp_path, vault, "add", "testsite", "--username",
         "alice", "--password-file", str(pw))
    return vault


def _flip(path: Path, offset: int) -> None:
    raw = bytearray(path.read_bytes())
    raw[offset] ^= 0xFF
    path.write_bytes(bytes(raw))


# ── Wrong-passphrase drills ─────────────────────────────


def test_probe_wrong_passphrase_leaves_every_file_untouched(tmp_path):
    vault = _scratch_vault(tmp_path)
    _run(tmp_path, vault, "set-passphrase", passphrase=PASSPHRASE)
    before = {p.name: p.read_bytes()
              for p in vault.iterdir() if p.is_file()}
    refused = _run(tmp_path, vault, "get", "testsite",
                   passphrase="a wrong guess entirely",
                   check=False)
    assert refused.returncode == 1
    assert "did not unlock" in refused.stderr
    assert "synthetic-pass-one" not in refused.stdout
    after = {p.name: p.read_bytes()
             for p in vault.iterdir() if p.is_file()}
    assert before == after


# ── Tampered-vault drills ───────────────────────────────


def test_probe_tampered_vault_heals_from_the_newest_backup(tmp_path):
    vault = _scratch_vault(tmp_path)
    blob = vault / "vault.json.enc"
    _flip(blob, len(blob.read_bytes()) // 2)
    out = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-one" in out.stdout
    assert "auto-repair" in out.stderr


def test_probe_tampered_vault_without_backups_refuses_plainly(tmp_path):
    vault = _scratch_vault(tmp_path)
    shutil.rmtree(vault / "backups")
    blob = vault / "vault.json.enc"
    _flip(blob, 10)
    damaged = blob.read_bytes()
    key_before = (vault / ".vault_key").read_bytes()
    refused = _run(tmp_path, vault, "get", "testsite", check=False)
    assert refused.returncode == 1
    assert "Cannot decrypt vault" in refused.stderr
    assert "Traceback" not in refused.stderr
    # Nothing is invented and nothing is regenerated: the
    # damaged blob and the key stand exactly as they were.
    assert blob.read_bytes() == damaged
    assert (vault / ".vault_key").read_bytes() == key_before


# ── Partial-write drills ────────────────────────────────


def test_probe_truncated_vault_without_backups_refuses_plainly(tmp_path):
    vault = _scratch_vault(tmp_path)
    shutil.rmtree(vault / "backups")
    blob = vault / "vault.json.enc"
    blob.write_bytes(blob.read_bytes()[: len(blob.read_bytes()) // 2])
    refused = _run(tmp_path, vault, "get", "testsite", check=False)
    assert refused.returncode == 1
    assert "Cannot decrypt vault" in refused.stderr
    assert "Traceback" not in refused.stderr


def test_probe_crashed_atomic_write_leftover_is_ignored(tmp_path):
    vault = _scratch_vault(tmp_path)
    (vault / "vault.json.enc.99999.tmp").write_bytes(
        b"half-written garbage from a crashed save")
    out = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-one" in out.stdout
    pw = tmp_path / "pw.txt"
    _run(tmp_path, vault, "add", "second", "--password-file", str(pw))
    assert "synthetic-pass-one" in _run(
        tmp_path, vault, "get", "second").stdout


def test_probe_truncated_key_is_a_plain_refusal(tmp_path):
    # Docket 139: before this slice this shape raised a raw
    # ValueError traceback; now the validator's own words.
    vault = _scratch_vault(tmp_path)
    key = vault / ".vault_key"
    key.write_bytes(key.read_bytes()[:20])
    refused = _run(tmp_path, vault, "get", "testsite", check=False)
    assert refused.returncode == 1
    assert "Invalid vault key" in refused.stderr
    assert "do NOT regenerate the key" in refused.stderr
    assert "Traceback" not in refused.stderr
    # The damaged file is left exactly as it stands.
    assert len(key.read_bytes()) == 20


def test_probe_empty_key_is_a_plain_refusal(tmp_path):
    vault = _scratch_vault(tmp_path)
    (vault / ".vault_key").write_bytes(b"")
    refused = _run(tmp_path, vault, "get", "testsite", check=False)
    assert refused.returncode == 1
    assert "Invalid vault key" in refused.stderr
    assert "Traceback" not in refused.stderr


def test_probe_torn_wrapped_key_is_a_plain_refusal(tmp_path):
    vault = _scratch_vault(tmp_path)
    _run(tmp_path, vault, "set-passphrase", passphrase=PASSPHRASE)
    key = vault / ".vault_key"
    key.write_bytes(key.read_bytes()[: len(key.read_bytes()) // 2])
    refused = _run(tmp_path, vault, "get", "testsite",
                   passphrase=PASSPHRASE, check=False)
    assert refused.returncode == 1
    assert "Invalid vault key" in refused.stderr
    assert "Traceback" not in refused.stderr


# ── Tampered carried-envelope drills (E-101's shapes) ───


def _carried(tmp_path: Path, vault: Path) -> Path:
    out = tmp_path / "carried.enc"
    _run(tmp_path, vault, "backup", "--carry", "--output", str(out),
         carry_pw=CARRY_PW)
    return out


def _empty_destination(tmp_path: Path, name: str) -> Path:
    dest = tmp_path / name
    _run(tmp_path, dest, "init")
    return dest


def test_probe_tampered_carried_token_restores_nothing(tmp_path):
    source = _scratch_vault(tmp_path, "vaultA")
    carried = _carried(tmp_path, source)
    doc = json.loads(carried.read_text(encoding="utf-8"))
    token = doc["encrypted"]
    doc["encrypted"] = ("A" if token[0] != "A" else "B") + token[1:]
    carried.write_text(json.dumps(doc), encoding="utf-8")
    dest = _empty_destination(tmp_path, "vaultB")
    refused = _run(tmp_path, dest, "restore", str(carried),
                   carry_pw=CARRY_PW, check=False)
    assert refused.returncode == 1
    assert "did not open this file" in refused.stderr
    assert "No entries" in _run(tmp_path, dest, "list").stdout


def test_probe_torn_carried_salt_is_stated_damaged(tmp_path):
    source = _scratch_vault(tmp_path, "vaultA")
    carried = _carried(tmp_path, source)
    doc = json.loads(carried.read_text(encoding="utf-8"))
    doc["salt"] = "!!!not-base64!!!"
    carried.write_text(json.dumps(doc), encoding="utf-8")
    dest = _empty_destination(tmp_path, "vaultB")
    refused = _run(tmp_path, dest, "restore", str(carried),
                   carry_pw=CARRY_PW, check=False)
    assert refused.returncode == 1
    assert "damaged" in refused.stderr
    assert "No entries" in _run(tmp_path, dest, "list").stdout


def test_probe_half_written_carried_file_is_a_plain_refusal(tmp_path):
    source = _scratch_vault(tmp_path, "vaultA")
    carried = _carried(tmp_path, source)
    raw = carried.read_bytes()
    carried.write_bytes(raw[: len(raw) // 2])
    dest = _empty_destination(tmp_path, "vaultB")
    refused = _run(tmp_path, dest, "restore", str(carried),
                   carry_pw=CARRY_PW, check=False)
    assert refused.returncode == 1
    assert "Cannot read backup file" in refused.stderr
    assert "Traceback" not in refused.stderr
    assert "No entries" in _run(tmp_path, dest, "list").stdout


# ── The lock drill (docket 134's shape, drilled) ────────


def _env(tmp_path: Path, vault: Path) -> dict:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_PASSPHRASE", None)
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return env


def test_probe_the_write_lock_blocks_until_it_lets_go(tmp_path):
    if os.name != "posix":
        import pytest
        pytest.skip("the flock drill is the POSIX shape")
    vault = _scratch_vault(tmp_path)
    holder = subprocess.Popen(
        [sys.executable, "-c",
         "import fcntl, os, sys, time\n"
         "fd = os.open(sys.argv[1], os.O_RDWR)\n"
         "fcntl.flock(fd, fcntl.LOCK_EX)\n"
         "print('held', flush=True)\n"
         "time.sleep(5)\n",
         str(vault / ".vault.lock")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert holder.stdout.readline().strip() == "held"
        pw = tmp_path / "pw.txt"
        writer = subprocess.Popen(
            [sys.executable, str(CREDSTORE), "add", "blockedentry",
             "--password-file", str(pw)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=_env(tmp_path, vault),
            stdin=subprocess.DEVNULL)
        time.sleep(2)
        # The writer is still waiting on the lock — it has
        # not written over the holder, and it has not failed.
        assert writer.poll() is None
        assert writer.wait(timeout=30) == 0
    finally:
        holder.wait(timeout=30)
    assert "blockedentry" in _run(tmp_path, vault, "list").stdout


def test_probe_two_writers_at_once_both_land(tmp_path):
    vault = _scratch_vault(tmp_path)
    pw = tmp_path / "pw.txt"
    env = _env(tmp_path, vault)
    writers = [
        subprocess.Popen(
            [sys.executable, str(CREDSTORE), "add", name,
             "--password-file", str(pw)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=env, stdin=subprocess.DEVNULL)
        for name in ("conc-a", "conc-b")
    ]
    for writer in writers:
        assert writer.wait(timeout=60) == 0
    listed = _run(tmp_path, vault, "list").stdout
    assert "conc-a" in listed
    assert "conc-b" in listed


# ── The rollback drill (docket 133 — NOT defended) ──────


def test_probe_rollback_still_resurrects_the_rotated_password(tmp_path):
    # The standing finding, re-proven as a drill: any older
    # valid blob, served in place of the current one, brings
    # back the rotated-away password with no warning. The
    # E-095 battery proved the shape; this drill keeps it
    # measured at every gate until a remedy with an anchor
    # outside the folder exists (the doc weighs them).
    vault = _scratch_vault(tmp_path)
    snapshot = tmp_path / "older_blob.enc"
    shutil.copy2(vault / "vault.json.enc", snapshot)
    pw2 = tmp_path / "pw2.txt"
    pw2.write_text("synthetic-pass-two")
    _run(tmp_path, vault, "update", "testsite",
         "--password-file", str(pw2))
    assert "synthetic-pass-two" in _run(
        tmp_path, vault, "get", "testsite").stdout
    shutil.copy2(snapshot, vault / "vault.json.enc")
    rolled = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-one" in rolled.stdout
