"""E-106 — Part VI gate.

Pins ``docs/architecture/E-106_PART_VI_GATE.md``:

* the gate record itself: Part VI closed, its
  criteria each checked, the slice-by-slice
  dispositions on file;
* the two rulings this gate owned — docket 140
  RULED (the vault's stated install floor is
  laptop-class; the measured carrying-in price
  named; toaster install NOT PROVEN) and
  docket 133 carried in the verdict in its own
  words (rollback OPEN, NOT DEFENDED, the
  external-anchor candidate and its E-204 owner);
* the carried items and their owners (dockets
  129 + 136 → E-187, hazard H2 → E-204, docket
  130's README half → E-195);
* every Part VI slice document E-093–E-106
  present under ``docs/architecture/``;
* one live probe of the gate's headline: through
  the core binding itself, a scratch vault hands
  ``ember-core`` its own apikey whole, refuses the
  owner's untagged entry, and answers a missing
  entry in the same shape — the binding live at
  the gate tree, re-proven not recalled.
"""

from __future__ import annotations

import importlib.util
import os
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-106_PART_VI_GATE.md"
ARCH = REPO / "docs" / "architecture"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

PART_VI_DOCS = (
    "E-093_CUSTODY_LAW.md",
    "E-094_TOASTER_KISTA_MAPPED.md",
    "E-095_TOASTER_KISTA_THREAT_MODEL.md",
    "E-096_UNLOCK_EXPERIENCE.md",
    "E-097_PER_PROGRAM_ACCESS.md",
    "E-098_ENTRY_KINDS.md",
    "E-099_INTEROP_TRUTH.md",
    "E-100_CORE_BINDING.md",
    "E-101_CARRIED_BACKUP.md",
    "E-102_AUDIT_DRILLS.md",
    "E-103_BUDGET_PROOF.md",
    "E-104_KISTA_FOR_USERS.md",
    "E-105_NAMING_KINDNESS.md",
    "E-106_PART_VI_GATE.md",
)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_all_part_vi_slice_docs_present():
    for name in PART_VI_DOCS:
        assert (ARCH / name).is_file(), name


def test_doc_records_the_gate_verdict():
    text = _flat(DOC)
    for needle in ("Part VI is done",
                   "Part VI gate: PASS",
                   "core binding live",
                   "drills green",
                   "no entry ever crosses",
                   "Next: E-107"):
        assert needle in text, needle


def test_doc_rules_docket_140():
    text = _flat(DOC)
    for needle in ("Docket 140 — RULED",
                   "laptop-class",
                   "15,723,450",
                   "149,853",
                   "15,573,597",
                   "toaster-sized at rest and in use",
                   "NOT PROVEN",
                   "may call the vault toaster-installable"):
        assert needle in text, needle


def test_doc_carries_docket_133_not_defended():
    text = _flat(DOC)
    for needle in ("Docket 133 — rollback stands OPEN and NOT DEFENDED",
                   "rotated-away password is served again",
                   "anchor outside the folder",
                   "E-204's presentation",
                   "never** be described as defending against rollback"):
        assert needle in text, needle


def test_doc_names_the_carried_items_and_owners():
    text = _flat(DOC)
    for needle in ("Docket 129", "Docket 136", "E-187",
                   "Hazard H2", "E-204's presentation",
                   "Docket 130's README half", "E-195"):
        assert needle in text, needle


# ── Live probe: the binding, at the gate tree ───────────

sys.path.insert(0, str(REPO / "src"))

from ember.kista_binding import fetch_credential  # noqa: E402
from ember.schemas.config import KistaConfig  # noqa: E402

GATE_KEY = "gate-probe-key-0001"
OWNER_PW = "gate-probe-owner-pw"


def _run_cli(tmp_path: Path, vault: Path, *argv: str) -> subprocess.CompletedProcess:
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
    result = subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env,
        stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        raise AssertionError(
            f"{argv} -> {result.returncode}: "
            f"{result.stdout}{result.stderr}")
    return result


def test_probe_binding_live_at_the_gate(tmp_path):
    vault = tmp_path / "vault"
    _run_cli(tmp_path, vault, "init")
    _run_cli(tmp_path, vault, "add", "gateapi", "--type", "apikey",
             "--key", GATE_KEY, "--program", "ember-core")
    pw_file = tmp_path / "pw.txt"
    pw_file.write_text(OWNER_PW)
    _run_cli(tmp_path, vault, "add", "ownersite", "--username",
             "owner", "--password-file", str(pw_file))
    cfg = KistaConfig(enabled=True, vault_dir=vault,
                      credstore_path=CREDSTORE)
    got = fetch_credential("gateapi", config=cfg, env={})
    assert got.secret == GATE_KEY
    refused = fetch_credential("ownersite", config=cfg, env={})
    assert refused.secret is None
    assert OWNER_PW not in (refused.reason or "")
    missing = fetch_credential("nosuch", config=cfg, env={})
    assert missing.secret is None
