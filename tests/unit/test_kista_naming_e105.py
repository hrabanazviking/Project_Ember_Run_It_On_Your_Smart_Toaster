"""E-105 — the naming kindness.

Pins ``docs/architecture/E-105_NAMING_KINDNESS.md``:

* the two plain user-facing names — Ember's Kista
  (the user's own chest, on their machine) and the
  house Kista (the house assistants' chest, on the
  house computer) — and the one carrying sentence;
* the map between the plain names and the builders'
  names (toaster-Kista / ai-folder Kista, E-011
  rule 1), so neither layer rewrites the other;
* what was NOT renamed, read from the program file
  itself: the command's help words and header stand,
  the plain names live in the docs layer only and
  never entered the program's own speech;
* the applications: the naming addendum appended
  to the E-104 plain user guide (its banked body
  intact) and the plain names inside the member
  skill file's identity banner;
* one live probe: a scratch vault's init and
  status still speak the vault's own standing
  words — the naming layer changed no behaviour.
"""

from __future__ import annotations

import importlib.util
import os
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-105_NAMING_KINDNESS.md"
GUIDE = REPO / "docs" / "architecture" / "E-104_KISTA_FOR_USERS.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"
SKILL = KISTA / "SKILL.md"


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_two_plain_names():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("Ember's Kista", "the house Kista",
                   "your chest", "the house's chest",
                   "~/.ember/kista/", "the house computer",
                   "no entry ever crosses",
                   "support-confusion"):
        assert needle in text, needle
    low = text.lower()
    for needle in ("first mention, full form",
                   "never bare", "where both could be",
                   "kindness is the test",
                   "e-106", "e-195"):
        assert needle in low, needle


def test_doc_maps_plain_names_to_builders_names():
    text = DOC.read_text(encoding="utf-8")
    assert "Ember's Kista = toaster-Kista" in text
    assert "the house\n  Kista = ai-folder Kista" in text \
        or "house Kista = ai-folder Kista" in text
    assert "which one, where, and when" in text


# ── What was not renamed ────────────────────────────────


def test_the_vaults_own_words_stand_in_the_program():
    text = CREDSTORE.read_text(encoding="utf-8")
    # Its header and its help description stand, in
    # the words E-094/E-104 pinned.
    assert "Kista v2.0 — The Vault of Yggdrasil" in text
    assert ('description="Kista — Self-owned encrypted '
            'vault (Old Norse: strongbox/chest)"') in text
    # The naming layer never entered the program's
    # own speech: the plain names live in docs only.
    assert "Ember's Kista" not in text
    assert "house Kista" not in text
    # Its environment names stand.
    for name in ("KISTA_DIR", "KISTA_PROGRAM",
                 "KISTA_PASSPHRASE"):
        assert name in text, name


# ── The applications ────────────────────────────────────


def test_guide_gains_the_naming_addendum_appended():
    text = GUIDE.read_text(encoding="utf-8")
    # The banked guide body stands…
    assert "Part A is the whole user guide" in text
    assert "Filed by the E-104 slice, 2026-11-02" in text
    # …and the E-105 addendum extends it, after it.
    marker = "Naming addendum (E-105"
    assert marker in text
    assert text.index(marker) > text.index(
        "Filed by the E-104 slice, 2026-11-02")
    addendum = text[text.index(marker):]
    assert "Ember's Kista" in addendum
    assert "the house Kista" in addendum
    assert "no entry ever crosses" in addendum


def test_skill_banner_carries_the_plain_names():
    text = SKILL.read_text(encoding="utf-8")
    # The machine name from E-104's docket 49 stands.
    head = text.split("---", 2)[1]
    assert "name: kista-toaster" in head
    # The banner now speaks the plain names too.
    assert "Ember's Kista" in text
    assert "the house Kista" in text
    assert "E-105" in text


# ── Live probe: behaviour unchanged ─────────────────────


def _run(tmp_path: Path, vault: Path, *argv: str) -> subprocess.CompletedProcess:
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
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    result = subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env,
        stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        raise AssertionError(
            f"{argv} -> {result.returncode}: "
            f"{result.stdout}{result.stderr}")
    return result


def test_probe_the_vault_still_speaks_its_own_words(tmp_path):
    vault = tmp_path / "vault"
    init = _run(tmp_path, vault, "init")
    assert "NOT set" in init.stdout
    status = _run(tmp_path, vault, "status")
    assert "Passphrase: NOT set" in status.stdout
    assert "a copy of this folder opens the vault" in status.stdout
