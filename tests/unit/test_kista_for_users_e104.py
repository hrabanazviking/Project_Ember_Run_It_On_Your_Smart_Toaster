"""E-104 — Kista for users (plain) + the boundary doc final.

Pins ``docs/architecture/E-104_KISTA_FOR_USERS.md``:

* Part A, the plain user guide: the toaster set in its
  four plain words, the vault's home and folder, the
  daily command road, the passphrase flow with its
  recovery truth, per-program scoping with its honesty
  line, the carried backup and its two warnings, the
  failure shapes, and E-103's prices restated — every
  load-bearing claim either re-derived here or proven
  live on a scratch vault with synthetic entries only;
* docket 130, closed for the member's own documents:
  no member document states the other program's
  credentials directory as this vault's home any
  more — the whole member is scanned, so a future
  stale line fails loudly — except the member README,
  which stands under the README law, untouched here,
  its stale lines pinned as standing for their owner;
* docket 49, closed: the member skill file names this
  copy, counts the true fourteen types, and marks its
  inherited other-side working text as provenance,
  not instruction;
* docket 141, new and closed here: the architecture
  document's stale "intentionally readable" metadata
  line, corrected to the mode-600 truth E-095 built;
* Part B, the boundary's final form, and its matching
  addendum appended to the E-011 boundary document —
  appended, never rewritten: the original text and
  the E-099 addendum both still stand in that file.
"""

from __future__ import annotations

import importlib.util
import os
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-104_KISTA_FOR_USERS.md"
BOUNDARY = REPO / "docs" / "audit" / "E-011_TWO_KISTAS_BOUNDARY.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

OLD_HOME = "~/.hermes" + "/credentials"
NEW_HOME = "~/.ember/kista"
MEMBER_DOCS = (
    "ARCHITECTURE.md", "ENTRY_TYPES.md", "PHILOSOPHY.md",
    "SYSTEM_VISION.md", "SKILL.md", "DOMAIN_MAP.md",
    "BUG_REPORT.md", "CODE_REVIEW.md",
)


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_guide_and_the_boundary_final():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words",
                   "passwords, tokens, urls, and notes",
                   "~/.ember/kista/", "set-passphrase",
                   "no reset, no recovery copy, no back door",
                   "backup --carry", "--allow-plaintext",
                   "not defended", "764 bytes", "328,548",
                   "41.3", "15,723,450", "docket 140",
                   "docket 130", "docket 49", "docket 141",
                   "no entry ever crosses",
                   "e-105", "e-106", "e-195", "e-204"):
        assert needle in text, needle


def test_boundary_addendum_appended_original_stands():
    text = BOUNDARY.read_text(encoding="utf-8")
    # The original filing and the E-099 addendum stand…
    assert "There are two programs called Kista" in text
    assert "E-099 addendum" in text
    # …and the E-104 final addendum extends them.
    assert "E-104 final addendum" in text
    assert "The boundary is final" in text
    low = text.lower()
    for needle in ("h1 (the default home) — closed",
                   "h2 (verdandi's third vault shape)",
                   "still", "standing"):
        assert needle in low, needle


# ── Docket 130: the member no longer states the old home ──


def test_no_member_doc_states_the_old_default_home():
    offenders = []
    for path in sorted(KISTA.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README law reserves it (below)
        if OLD_HOME in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(REPO)))
    assert offenders == [], offenders


def test_member_readme_untouched_and_reserved_to_e195():
    # The README still states the old home: this slice
    # did not touch it, exactly as the standing README
    # law requires. When E-195 corrects it by the
    # owner's hand or word, this pin is re-pinned there
    # consciously, as earlier slices re-pinned theirs.
    text = (KISTA / "README.md").read_text(encoding="utf-8")
    assert OLD_HOME in text
    doc = DOC.read_text(encoding="utf-8")
    assert "E-195" in doc and "README law" in doc


def test_corrected_member_docs_state_the_new_home():
    for name in ("ARCHITECTURE.md", "ENTRY_TYPES.md",
                 "PHILOSOPHY.md", "SYSTEM_VISION.md",
                 "SKILL.md"):
        text = (KISTA / name).read_text(encoding="utf-8")
        assert NEW_HOME in text, name


# ── Docket 49: the skill file names this copy ───────────


def test_skill_file_names_this_copy_and_counts_fourteen():
    text = (KISTA / "SKILL.md").read_text(encoding="utf-8")
    head = text.split("---", 2)[1]
    assert "name: kista-toaster" in head
    assert "14 entry types" in head
    assert "runa-credentials" not in head
    assert "hermes:" not in head
    # The other program's repo is named as the other
    # program's home, never as this copy's.
    assert "the *other* Kista's home" in text
    # Inherited working text is marked as provenance.
    assert "kept as provenance" in text
    assert "not** instructions for a person using this program" in text


# ── The reconciliations, pinned file by file ────────────


def test_entry_types_doc_carries_the_partition():
    text = (KISTA / "ENTRY_TYPES.md").read_text(encoding="utf-8")
    assert "E-098, reconciled at E-104" in text
    for needle in ("**The toaster set", "**Kept kinds",
                   "**The other road's kinds",
                   "`credential`", "`apikey`", "`url`",
                   "`note`", "`totp`", "`astrology`",
                   "`markdown`"):
        assert needle in text, needle


def test_architecture_meta_line_corrected_docket_141():
    text = (KISTA / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "is intentionally readable" not in text
    assert "since E-095 it is also written chmod 600" in text


def test_system_vision_proposals_marked_honestly():
    text = (KISTA / "SYSTEM_VISION.md").read_text(encoding="utf-8")
    assert "Environment variable `KISTA_DIR` (preferred) — **built**" in text
    assert "CLI flag `--vault-dir` — **not built**" in text
    assert "Default: `~/.ember/kista`" in text


# ── Part A's road, proven live on a scratch vault ───────


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
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_BACKUP_PASSPHRASE", None)
    if passphrase is None:
        env.pop("KISTA_PASSPHRASE", None)
    else:
        env["KISTA_PASSPHRASE"] = passphrase
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    result = subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env,
        stdin=subprocess.DEVNULL)
    if check and result.returncode != 0:
        raise AssertionError(
            f"{argv} -> {result.returncode}: "
            f"{result.stdout}{result.stderr}")
    return result


def test_probe_the_plain_user_road_end_to_end(tmp_path):
    vault = tmp_path / "vault"
    init = _run(tmp_path, vault, "init")
    # An unlocked vault says so, in words, at creation.
    assert "NOT set" in init.stdout
    assert "no recovery" in init.stdout
    pw = tmp_path / "pw.txt"
    pw.write_text("synthetic-pass-value-1234")
    _run(tmp_path, vault, "add", "example-login",
         "--username", "synthetic-user",
         "--password-file", str(pw),
         "--url", "https://example.invalid/login")
    _run(tmp_path, vault, "add-apikey", "example-token",
         "--key", "synthetic-token-value-1234")
    _run(tmp_path, vault, "add-url", "example-link",
         "--url", "https://example.invalid/docs",
         "--title", "Example docs")
    _run(tmp_path, vault, "add-note", "example-note",
         "--content", "a synthetic note")
    got = _run(tmp_path, vault, "get", "example-login")
    assert "synthetic-pass-value-1234" in got.stdout
    listed = _run(tmp_path, vault, "list")
    for name in ("example-login", "example-token",
                 "example-link", "example-note"):
        assert name in listed.stdout, name
    assert "Entry exists" in _run(
        tmp_path, vault, "check", "example-login").stdout
    assert "Found 4 match" in _run(
        tmp_path, vault, "search", "example").stdout
    status = _run(tmp_path, vault, "status")
    assert "Passphrase: NOT set" in status.stdout
    assert "a copy of this folder opens the vault" in status.stdout


def test_probe_the_passphrase_flow_in_the_docs_words(tmp_path):
    vault = tmp_path / "vault"
    _run(tmp_path, vault, "init")
    pw = tmp_path / "pw.txt"
    pw.write_text("synthetic-pass-value-1234")
    _run(tmp_path, vault, "add", "example-login",
         "--username", "synthetic-user",
         "--password-file", str(pw))
    secret = "correct horse battery staple"
    setting = _run(tmp_path, vault, "set-passphrase",
                   passphrase=secret)
    # The recovery truth is stated before the lock is set.
    assert "if you forget this passphrase" in setting.stdout
    assert "no reset and no" in setting.stdout
    status = _run(tmp_path, vault, "status", passphrase=secret)
    assert "Passphrase: SET" in status.stdout
    # No passphrase at all: a plain refusal, no data.
    refused = _run(tmp_path, vault, "get", "example-login",
                   check=False)
    assert refused.returncode == 1
    assert "synthetic-pass-value-1234" not in refused.stdout
    # The right passphrase reads the entry whole.
    got = _run(tmp_path, vault, "get", "example-login",
               passphrase=secret)
    assert "synthetic-pass-value-1234" in got.stdout
