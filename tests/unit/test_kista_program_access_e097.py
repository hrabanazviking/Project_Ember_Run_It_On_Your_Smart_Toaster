"""E-097 — Per-program access for the toaster-Kista.

Pins ``docs/architecture/E-097_PER_PROGRAM_ACCESS.md``:

* every entry carries the name of the program it
  belongs to (``program``; empty = the vault owner's
  own entry, and entries written before this slice
  read exactly that way);
* a caller that names itself with ``KISTA_PROGRAM``
  can add, read, list, search, check, change, and
  remove ONLY its own entries — another program's
  entry and a missing entry answer identically, so a
  program learns nothing about the rest of the vault;
* whole-vault and vault-life operations (export,
  backup, config, set-passphrase, and kin) are the
  owner's acts and are refused to a program caller;
* only the owner can change who an entry belongs to
  (``update --program`` / ``--unassign-program``);
* the honesty line stands in the doc and in the code:
  a program name is an identifier, not a credential —
  this is discipline for well-behaved programs, not a
  wall against malicious same-account code (E-095 A2).

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
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-097_PER_PROGRAM_ACCESS.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

OWNER_VAL = "synthetic-owner-one"
PROG_VAL = "synthetic-prog-one"
OTHER_VAL = "synthetic-other-one"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


# ── The slice record, on file ───────────────────────────


def test_doc_records_per_program_access():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "kista_program",
                   "only its own entries", "identifier",
                   "not a credential", "same-account",
                   "e-100", "--program", "--unassign-program"):
        assert needle in text, needle


# ── The shape is the code's shape ───────────────────────


def test_program_shape_in_code():
    src = _source()
    assert "KISTA_PROGRAM" in src
    assert '"program": owner_program' in src
    assert "def _program_sees" in src
    assert "def _visible_entries" in src
    assert "def _refuse_program_whole_vault" in src
    # The caller's name is read from the environment,
    # never from a command-line value (a name is an
    # identifier; a value on a command line is the
    # docket-128 exposure shape, and no secret of any
    # kind is taken there either).
    assert 'os.environ.get("KISTA_PROGRAM")' in src


# ── Probes against a scratch vault ──────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str,
         program: str | None = None,
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
    _run(tmp_path, vault, "init")
    _run(tmp_path, vault, "add", "ownersite", "--username",
         "owner", "--password-file",
         _pw_file(tmp_path, "pw1.txt", OWNER_VAL))
    _run(tmp_path, vault, "add", "progsite", "--username",
         "prog", "--password-file",
         _pw_file(tmp_path, "pw2.txt", PROG_VAL),
         "--program", "ember-core")
    return vault


def test_probe_owner_still_sees_everything(tmp_path):
    vault = _scratch_vault(tmp_path)
    assert OWNER_VAL in _run(
        tmp_path, vault, "get", "ownersite").stdout
    assert PROG_VAL in _run(
        tmp_path, vault, "get", "progsite").stdout
    listing = _run(tmp_path, vault, "list").stdout
    assert "ownersite" in listing and "progsite" in listing


def test_probe_program_sees_only_its_own(tmp_path):
    vault = _scratch_vault(tmp_path)
    got = _run(tmp_path, vault, "get", "progsite",
               program="ember-core")
    assert PROG_VAL in got.stdout
    assert '"program": "ember-core"' in got.stdout
    # Another program's entry: refused, no value, and
    # no available-services list (which would name
    # other programs' entries).
    refused = _run(tmp_path, vault, "get", "ownersite",
                   program="ember-core", check=False)
    assert refused.returncode == 1
    assert OWNER_VAL not in refused.stdout
    assert "Available:" not in refused.stdout
    # A missing entry answers identically — a program
    # cannot tell "not yours" from "not there".
    missing = _run(tmp_path, vault, "get", "nosuchsite",
                   program="ember-core", check=False)
    assert missing.returncode == 1
    assert "can only see its own entries" in missing.stdout
    assert "can only see its own entries" in refused.stdout
    # A third program sees neither of them.
    third = _run(tmp_path, vault, "get", "progsite",
                 program="other-app", check=False)
    assert third.returncode == 1
    assert PROG_VAL not in third.stdout


def test_probe_list_search_check_status_are_scoped(tmp_path):
    vault = _scratch_vault(tmp_path)
    listing = _run(tmp_path, vault, "list",
                   program="ember-core").stdout
    assert "progsite" in listing
    assert "ownersite" not in listing
    search = _run(tmp_path, vault, "search", "ownersite",
                  program="ember-core").stdout
    assert "No matches" in search
    check = _run(tmp_path, vault, "check", "ownersite",
                 program="ember-core").stdout
    assert "No entry found" in check
    status = _run(tmp_path, vault, "status",
                  program="ember-core").stdout
    assert "Entries: 1" in status
    assert "ownersite" not in status


def test_probe_program_add_stamps_only_itself(tmp_path):
    vault = _scratch_vault(tmp_path)
    added = _run(tmp_path, vault, "add", "coresite",
                 "--username", "c", "--password-file",
                 _pw_file(tmp_path, "pw3.txt", OTHER_VAL),
                 program="ember-core")
    assert "Belongs to program: ember-core" in added.stdout
    got = _run(tmp_path, vault, "get", "coresite",
               program="ember-core")
    assert OTHER_VAL in got.stdout
    # Stamping another program's name is refused...
    refused = _run(tmp_path, vault, "add", "sneakysite",
                   "--username", "s", "--password-file",
                   _pw_file(tmp_path, "pw4.txt", OTHER_VAL),
                   "--program", "other-app",
                   program="ember-core", check=False)
    assert refused.returncode == 1
    # ...and nothing was added for anyone.
    owner_view = _run(tmp_path, vault, "list").stdout
    assert "sneakysite" not in owner_view


def test_probe_program_cannot_touch_others_entries(tmp_path):
    vault = _scratch_vault(tmp_path)
    upd = _run(tmp_path, vault, "update", "ownersite",
               "--username", "hijacked",
               program="ember-core", check=False)
    assert upd.returncode == 1
    rm = _run(tmp_path, vault, "remove", "ownersite",
              program="ember-core", check=False)
    assert rm.returncode == 1
    # The owner's entry is whole and unchanged.
    got = _run(tmp_path, vault, "get", "ownersite")
    assert OWNER_VAL in got.stdout
    assert "hijacked" not in got.stdout
    # Even --force cannot overwrite another's entry.
    force = _run(tmp_path, vault, "add", "progsite",
                 "--username", "x", "--password-file",
                 _pw_file(tmp_path, "pw5.txt", OTHER_VAL),
                 "--force", program="other-app", check=False)
    assert force.returncode == 1
    got = _run(tmp_path, vault, "get", "progsite")
    assert PROG_VAL in got.stdout


def test_probe_program_updates_and_removes_its_own(tmp_path):
    vault = _scratch_vault(tmp_path)
    _run(tmp_path, vault, "update", "progsite",
         "--username", "prog-two", program="ember-core")
    got = _run(tmp_path, vault, "get", "progsite",
               program="ember-core")
    assert "prog-two" in got.stdout
    _run(tmp_path, vault, "remove", "progsite",
         program="ember-core")
    gone = _run(tmp_path, vault, "get", "progsite",
                check=False)
    assert gone.returncode == 1


def test_probe_whole_vault_operations_are_owners_acts(tmp_path):
    vault = _scratch_vault(tmp_path)
    for argv in (("export",), ("backup",), ("config", "list"),
                 ("set-passphrase",), ("repair",)):
        refused = _run(tmp_path, vault, *argv,
                       program="ember-core", check=False)
        assert refused.returncode == 1, argv
        assert "belongs to the vault owner" in refused.stderr, argv


def test_probe_only_owner_reassigns_ownership(tmp_path):
    vault = _scratch_vault(tmp_path)
    # A program cannot give its own entry away.
    refused = _run(tmp_path, vault, "update", "progsite",
                   "--program", "other-app",
                   program="ember-core", check=False)
    assert refused.returncode == 1
    got = _run(tmp_path, vault, "get", "progsite")
    assert '"program": "ember-core"' in got.stdout
    # The owner can: the entry moves, access follows it.
    _run(tmp_path, vault, "update", "progsite",
         "--program", "other-app")
    assert _run(tmp_path, vault, "get", "progsite",
                program="ember-core",
                check=False).returncode == 1
    moved = _run(tmp_path, vault, "get", "progsite",
                 program="other-app")
    assert PROG_VAL in moved.stdout
    # And the owner can take it back to their own.
    _run(tmp_path, vault, "update", "progsite",
         "--unassign-program")
    assert _run(tmp_path, vault, "get", "progsite",
                program="other-app",
                check=False).returncode == 1
    assert PROG_VAL in _run(
        tmp_path, vault, "get", "progsite").stdout


def test_probe_bad_program_names_refused(tmp_path):
    vault = _scratch_vault(tmp_path)
    refused = _run(tmp_path, vault, "list",
                   program="Bad Name!", check=False)
    assert refused.returncode == 1
    assert "not a usable program name" in refused.stderr
    refused = _run(tmp_path, vault, "add", "xsite",
                   "--username", "x", "--password-file",
                   _pw_file(tmp_path, "pw6.txt", OTHER_VAL),
                   "--program", "Bad Name!", check=False)
    assert refused.returncode == 1


def test_probe_legacy_entry_is_the_owners(tmp_path):
    # An entry written before E-097 has no program
    # field: strip it in-process and re-save, then it
    # must read as the owner's own — visible to the
    # owner, invisible to every program.
    vault = _scratch_vault(tmp_path)
    home = tmp_path / "home"
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    snippet = (
        "import scripts.credstore as cs\n"
        "key = cs._get_key()\n"
        "vault = cs._load_vault(key)\n"
        "del vault['entries']['progsite']['program']\n"
        "cs._save_vault(vault, key)\n"
    )
    subprocess.run([sys.executable, "-c", snippet],
                   capture_output=True, text=True, env=env,
                   check=True, stdin=subprocess.DEVNULL)
    assert PROG_VAL in _run(
        tmp_path, vault, "get", "progsite").stdout
    refused = _run(tmp_path, vault, "get", "progsite",
                   program="ember-core", check=False)
    assert refused.returncode == 1
    assert PROG_VAL not in refused.stdout


def test_probe_unlock_and_program_access_compose(tmp_path):
    # E-096's lock and E-097's scoping are two different
    # doors and both hold at once: with a passphrase
    # set, a program caller still needs the passphrase
    # AND still sees only its own entries.
    vault = _scratch_vault(tmp_path)
    phrase = "correct horse battery staple"
    _run(tmp_path, vault, "set-passphrase", passphrase=phrase)
    locked = _run(tmp_path, vault, "get", "progsite",
                  program="ember-core", check=False)
    assert locked.returncode == 1
    assert PROG_VAL not in locked.stdout
    opened = _run(tmp_path, vault, "get", "progsite",
                  program="ember-core", passphrase=phrase)
    assert PROG_VAL in opened.stdout
    still_scoped = _run(tmp_path, vault, "get", "ownersite",
                        program="ember-core",
                        passphrase=phrase, check=False)
    assert still_scoped.returncode == 1
    assert OWNER_VAL not in still_scoped.stdout
