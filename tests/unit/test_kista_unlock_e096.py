"""E-096 — The unlock experience for normal folks.

Pins ``docs/architecture/E-096_UNLOCK_EXPERIENCE.md``:

* the vault key can be wrapped under a passphrase
  (scrypt from the standard library; the vault key
  itself never changes, so entries and backups are
  untouched by setting, changing, or removing it);
* a copied vault folder — E-095's central, proven
  total-loss shape — now opens nothing without the
  passphrase, refuses a wrong one plainly, and opens
  with the right one;
* the recovery truth is stated before a passphrase is
  set, in the program's own words, and a forgotten
  passphrase is a stated dead end, never a traceback;
* docket 14 stands closed: no installer runs at import
  time — a missing dependency is a plain message;
* docket 128 stands closed: a value typed after
  --password draws a loud, plain warning at the moment
  of use, naming the shapes that do not expose it.

The probes never touch a real vault home: each runs
with a scratch home, the member directory on its
path, and the user site-packages that carry the
member's one dependency — the custody discipline the
campaign works under. Synthetic entries only.
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
DOC = REPO / "docs" / "architecture" / "E-096_UNLOCK_EXPERIENCE.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"
MEMBER_TESTS = KISTA / "tests" / "test_credstore.py"

PASSPHRASE = "correct horse battery staple"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


# ── The slice record, on file ───────────────────────────


def test_doc_records_the_unlock_story():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "scrypt",
                   "forgotten", "no recovery", "docket 14",
                   "closed", "docket 128", "set-passphrase",
                   "remove-passphrase", "kista_passphrase"):
        assert needle in text, needle


# ── Docket 14, closed in the code ───────────────────────


def test_no_installer_runs_at_import():
    src = _source()
    # No installer invocation of any shape survives.
    assert '"pip"' not in src
    assert "pip install" not in src
    # A missing dependency is a plain, stated message.
    assert "needs the 'cryptography' package" in src


def test_member_suite_repin_names_the_new_shape():
    text = MEMBER_TESTS.read_text(encoding="utf-8")
    assert "no installer" in text.lower()
    assert '"pip"' in text


# ── Docket 128, closed in the code ──────────────────────


def test_password_flag_warns_and_names_safer_shapes():
    src = _source()
    resolve = src.split("def _resolve_password")[1].split("def ")[0]
    assert "process list" in resolve
    assert "shell history" in resolve
    assert "--password-file" in resolve
    assert "--password-env" in resolve


# ── The wrapping shape is the code's shape ──────────────


def test_wrapping_shape_in_code():
    src = _source()
    assert "hashlib.scrypt" in src
    assert "kista_key_wrap" in src
    # The passphrase is never an argparse argument.
    main = src.split("def main()")[1]
    assert '"--vault-passphrase"' not in main
    assert '"--passphrase"' in main  # the sshkey entry field, untouched


# ── Probes against a scratch vault ──────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str,
         passphrase: str | None = None,
         check: bool = True) -> subprocess.CompletedProcess:
    if importlib.util.find_spec("cryptography") is None:
        import pytest
        pytest.skip("cryptography absent in this environment")
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env.pop("KISTA_PASSPHRASE", None)
    if passphrase is not None:
        env["KISTA_PASSPHRASE"] = passphrase
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=check,
        stdin=subprocess.DEVNULL)


def _scratch_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    _run(tmp_path, vault, "init")
    env_pw = tmp_path / "pw.txt"
    env_pw.write_text("synthetic-pass-one")
    _run(tmp_path, vault, "add", "testsite", "--username",
         "alice", "--password-file", str(env_pw))
    return vault


def test_probe_unwrapped_vault_still_opens(tmp_path):
    vault = _scratch_vault(tmp_path)
    out = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-one" in out.stdout
    status = _run(tmp_path, vault, "status")
    assert "NOT set" in status.stdout


def test_probe_folder_copy_locked_after_set_passphrase(tmp_path):
    vault = _scratch_vault(tmp_path)
    set_out = _run(tmp_path, vault, "set-passphrase",
                   passphrase=PASSPHRASE)
    # The recovery truth is stated as part of setting.
    assert "no reset" in set_out.stdout or \
        "cannot open" in set_out.stdout or \
        "forget" in set_out.stdout
    if os.name == "posix":
        mode = stat.S_IMODE((vault / ".vault_key").stat().st_mode)
        assert mode == 0o600
    import shutil
    stolen = tmp_path / "stolen"
    shutil.copytree(vault, stolen)
    # No passphrase at all: a plain refusal, no entry data.
    refused = _run(tmp_path, stolen, "get", "testsite",
                   check=False)
    assert refused.returncode == 1
    assert "synthetic-pass-one" not in refused.stdout
    assert "passphrase" in refused.stderr.lower()
    # The wrong passphrase: the same honest refusal.
    wrong = _run(tmp_path, stolen, "get", "testsite",
                 passphrase="a wrong guess entirely",
                 check=False)
    assert wrong.returncode == 1
    assert "synthetic-pass-one" not in wrong.stdout
    assert "did not unlock" in wrong.stderr
    # The right passphrase opens the copied folder.
    opened = _run(tmp_path, stolen, "get", "testsite",
                  passphrase=PASSPHRASE)
    assert "synthetic-pass-one" in opened.stdout


def test_probe_entries_survive_wrap_and_remove(tmp_path):
    vault = _scratch_vault(tmp_path)
    _run(tmp_path, vault, "set-passphrase", passphrase=PASSPHRASE)
    got = _run(tmp_path, vault, "get", "testsite",
               passphrase=PASSPHRASE)
    assert "synthetic-pass-one" in got.stdout
    removed = _run(tmp_path, vault, "remove-passphrase",
                   passphrase=PASSPHRASE)
    # The consequence is stated before/with the act.
    assert "copies" in removed.stdout or \
        "can open" in removed.stdout
    got = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-one" in got.stdout


def test_probe_short_passphrase_refused(tmp_path):
    vault = _scratch_vault(tmp_path)
    refused = _run(tmp_path, vault, "set-passphrase",
                   passphrase="short", check=False)
    assert refused.returncode == 1
    # The vault still opens unwrapped — nothing changed.
    out = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-one" in out.stdout


def test_probe_password_flag_warns(tmp_path):
    vault = _scratch_vault(tmp_path)
    out = _run(tmp_path, vault, "update", "testsite",
               "--password", "synthetic-pass-two")
    assert "process list" in out.stderr
    assert "shell history" in out.stderr
    got = _run(tmp_path, vault, "get", "testsite")
    assert "synthetic-pass-two" in got.stdout
