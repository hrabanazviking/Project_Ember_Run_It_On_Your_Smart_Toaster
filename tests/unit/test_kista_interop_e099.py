"""E-099 — Interop truth: can the two Kistas exchange entries?

Pins ``docs/architecture/E-099_INTEROP_TRUTH.md`` and
the addendum it appends to the E-011 boundary doc:

* the verdict is NO — no one-way export/import is
  built, because every encrypted movement road in
  the toaster program requires the SAME Fernet key
  on both sides (an export is a byte-copy of the
  vault blob and carries no key), no road selects by
  kind or program (a shared-key crossing is
  whole-vault and unfiltered, so even the toaster
  set cannot cross alone), and the ai-folder
  Kista's current format is NOT MEASURED (ancestry
  from the 2026-05-21 snapshot is not compatibility);
* the one differing-key road that mechanically
  works — plaintext backup/restore — is proven to
  work and named forbidden for real entries under
  the E-093 custody law (docket 138 -> E-101);
* a future bridge's requirements stand on file
  (measured target, Volmarr's word against E-011
  rule 5, toaster-set only, its own locked box,
  verified receipt, program tags handled openly).

The probes never touch a real vault home and never
go near the ai-folder Kista: three scratch vaults
hold synthetic entries only — A (source), B (a
different key), C (sharing A's key, the "same
vault, second folder" shape).
"""

from __future__ import annotations

import importlib.util
import os
import re
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-099_INTEROP_TRUTH.md"
BOUNDARY = REPO / "docs" / "audit" / "E-011_TWO_KISTAS_BOUNDARY.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

SAME_KEY_WORDS = "shares the same encryption key"


def _source() -> str:
    return CREDSTORE.read_text(encoding="utf-8")


def _section(src: str, start: str, end: str) -> str:
    return src[src.index(start):src.index(end)]


# ── The slice record, on file ───────────────────────────


def test_doc_records_interop_verdict():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "cannot exchange entries",
                   "same encryption key", "byte-identical",
                   "not measured", "ancestry is not format",
                   "plaintext", "forbidden",
                   "docket 138", "e-101", "e-104",
                   "volmarr's word", "toaster-set only",
                   "no entry ever crosses"):
        assert needle in text, needle


def test_boundary_doc_gained_e099_addendum():
    text = BOUNDARY.read_text(encoding="utf-8")
    assert "## E-099 addendum" in text
    lower = text.lower()
    for needle in ("same key or nothing", "whole-vault roads only",
                   "format is unmeasured", "no entry ever crosses",
                   "e-099_interop_truth"):
        assert needle in lower, needle
    # The addendum extends; the original rules stand.
    assert "No entry ever crosses." in text
    assert "This campaign works only on toaster-Kista." in text


# ── The movement roads' shape, in code ──────────────────


def test_export_is_a_byte_copy_carrying_no_key():
    body = _section(_source(), "def cmd_export", "def cmd_import")
    assert "shutil.copy2(VAULT_FILE, dest)" in body
    assert "_get_key" in body  # local validity check only


def test_import_refuses_a_different_key_in_words():
    src = _source()
    assert SAME_KEY_WORDS in src
    body = _section(src, "def cmd_import", "def cmd_backup")
    assert "InvalidToken" in body


def test_movement_roads_have_no_kind_or_program_filter():
    src = _source()
    for start, end in (("def cmd_import", "def cmd_backup"),
                       ("def cmd_restore", "def cmd_github_backup")):
        body = _section(src, start, end)
        assert "TOASTER_ENTRY_TYPES" not in body, start
        assert "OTHER_ROAD_ENTRY_TYPES" not in body, start
        assert "_caller_program" not in body, start


def test_no_key_export_or_transfer_command_exists():
    src = _source()
    for banned in ("export-key", "export_key", "transfer",
                   "recipient"):
        assert banned not in src, banned


# ── Probes against scratch vaults ───────────────────────


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
    env.pop("KISTA_PROGRAM", None)
    env.pop("KISTA_PASSPHRASE", None)
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
    _run(tmp_path, vault, "add", "link", "--type", "url",
         "--url", "https://example.com")
    _run(tmp_path, vault, "add", "memo", "--type", "note",
         "--content", "synthetic note A")
    _run(tmp_path, vault, "add", "me", "--type", "identity",
         "--full-name", "Synthetic Person")
    _run(tmp_path, vault, "add", "chart", "--type", "astrology",
         "--sign", "Pisces")
    return vault


def _names(tmp_path: Path, vault: Path) -> str:
    return _run(tmp_path, vault, "list").stdout


def test_probe_export_is_the_blob_with_no_plaintext(tmp_path):
    a = _source_vault(tmp_path)
    exp = tmp_path / "a_export.enc"
    _run(tmp_path, a, "export", "--output", str(exp))
    data = exp.read_bytes()
    assert data == (a / "vault.json.enc").read_bytes()
    assert b"synthetic-pw-A" not in data
    assert (a / ".vault_key").read_bytes().strip() not in data


def test_probe_different_key_import_refuses_totally(tmp_path):
    a = _source_vault(tmp_path)
    exp = tmp_path / "a_export.enc"
    _run(tmp_path, a, "export", "--output", str(exp))
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    refused = _run(tmp_path, b, "import", str(exp), check=False)
    assert refused.returncode == 1
    assert SAME_KEY_WORDS in refused.stderr
    listing = _names(tmp_path, b)
    for name in ("site", "key", "link", "memo", "me", "chart"):
        assert not re.search(rf"^{name}\b", listing, re.M), name


def test_probe_shared_key_crossing_is_whole_and_unfiltered(tmp_path):
    a = _source_vault(tmp_path)
    exp = tmp_path / "a_export.enc"
    _run(tmp_path, a, "export", "--output", str(exp))
    c = tmp_path / "vaultC"
    c.mkdir()
    key = c / ".vault_key"
    key.write_bytes((a / ".vault_key").read_bytes())
    key.chmod(0o600)
    _run(tmp_path, c, "init")
    out = _run(tmp_path, c, "import", str(exp)).stdout
    assert "Imported 6 new" in out
    assert "synthetic-pw-A" in _run(tmp_path, c, "get", "site").stdout
    # The kept kind and the other-road kind crossed too,
    # with no notice — the road is whole-vault, not a bridge.
    assert "Synthetic Person" in _run(tmp_path, c, "get", "me").stdout
    chart = _run(tmp_path, c, "get", "chart").stdout
    assert "Pisces" in chart
    assert "not one of the toaster-Kista" not in chart


def test_probe_encrypted_backup_refuses_across_keys(tmp_path):
    a = _source_vault(tmp_path)
    bk = tmp_path / "a_backup.json"
    _run(tmp_path, a, "backup", "--output", str(bk), "--encrypt")
    enc = bk.with_suffix(".json.enc")
    assert enc.exists()
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    refused = _run(tmp_path, b, "restore", str(enc), check=False)
    assert refused.returncode == 1
    assert "site" not in _names(tmp_path, b)


def test_probe_plaintext_backup_crosses_and_is_the_forbidden_road(tmp_path):
    # The road mechanically works between different keys —
    # which is exactly why it must be named: it moves
    # secrets in clear text, forbidden for real entries
    # by the E-093 custody law. Synthetic values only here.
    a = _source_vault(tmp_path)
    bk = tmp_path / "a_backup_plain.json"
    _run(tmp_path, a, "backup", "--output", str(bk))
    assert b"synthetic-pw-A" in bk.read_bytes()
    b = tmp_path / "vaultB"
    _run(tmp_path, b, "init")
    assert (b / ".vault_key").read_bytes() != \
        (a / ".vault_key").read_bytes()
    out = _run(tmp_path, b, "restore", str(bk)).stdout
    assert "Restored 6 new" in out
    assert "synthetic-pw-A" in _run(tmp_path, b, "get", "site").stdout
