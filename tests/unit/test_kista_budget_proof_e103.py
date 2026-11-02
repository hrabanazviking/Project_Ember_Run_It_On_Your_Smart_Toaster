"""E-103 — Budget proof for the toaster-Kista: the vault's cost.

Pins ``docs/architecture/E-103_BUDGET_PROOF.md`` and the
vault's row in ``docs/BUDGET_BOOK.md`` §7:

* the storage curve is re-derived live on a scratch vault
  (synthetic entries only): an empty vault is under a
  kilobyte all-in, a typical entry grows the encrypted
  blob by a measured band around 563 bytes, the automatic
  backups cap at five, and a working vault's whole estate
  stays a small multiple of its blob — never a hidden
  second store;
* the memory and time figures are recorded measurements
  (VmHWM medians and contended-VM wall medians, the E-057
  discipline: measurements are pinned as printed, not
  re-measured by the gate, because hardware is the one
  witness a test cannot call); what is re-derived live is
  every *judgement* — the recorded peaks against the live
  ``ember.budgets`` toaster ceilings, and the scrypt
  working-set arithmetic from the program's own
  constants;
* the install verdict is re-derived from the tree and
  the environment: the program file's true size, its
  one dependency's installed size where it is installed,
  and the same laptop-only conclusion from the live
  ceilings (docket 140, handed to the E-106 gate);
* the book gained the vault's row, in both places a
  reader can find it, at this record's numbers.
"""

from __future__ import annotations

import importlib.util
import os
import site
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-103_BUDGET_PROOF.md"
BOOK = REPO / "docs" / "BUDGET_BOOK.md"
KISTA = REPO / "kista"
CREDSTORE = KISTA / "scripts" / "credstore.py"

_MIB = 1024 * 1024

# Recorded measurements at the slice (E-103 doc): the
# 100-entry estate, the wrapped peak, the installed
# total. Judgements below re-derive their verdicts
# from these pins and the live ceilings.
ESTATE_100 = 328_548
WRAPPED_PEAK_MIB = 41.3
INSTALLED_TOTAL = 15_723_450
PROGRAM_BYTES = 149_853


def _ceilings():
    import ember.budgets as budgets

    return {b.profile.value: b for b in budgets.all_budgets()}


# ── The record, on file, and the book's row ─────────────


def test_doc_records_the_proof_and_the_verdicts():
    text = DOC.read_text(encoding="utf-8").lower()
    for needle in ("in plain words", "764 bytes", "563",
                   "328,548", "617", "41.3", "27.2",
                   "zero", "149,853", "15,573,597",
                   "15,723,450", "14,434,376",
                   "docket 140", "e-106", "not proven",
                   "never call it toaster"):
        assert needle in text, needle


def test_book_gained_the_vault_row_at_the_records_numbers():
    text = BOOK.read_text(encoding="utf-8")
    assert "The vault's own costs (E-103)" in text
    for needle in ("328,548", "41.3 MiB", "15,723,450",
                   "764 B"):
        assert needle in text, needle


# ── Judgements re-derived against the live ceilings ─────


def test_recorded_estate_fits_the_toaster_storage_allowance():
    toaster = _ceilings()["toaster"]
    assert ESTATE_100 < toaster.storage_mib * _MIB
    assert ESTATE_100 < 0.17 * toaster.storage_mib * _MIB


def test_recorded_peaks_fit_the_toaster_turn_ceiling():
    toaster = _ceilings()["toaster"]
    assert WRAPPED_PEAK_MIB < toaster.turn_ram_mib
    assert WRAPPED_PEAK_MIB > 0.60 * toaster.turn_ram_mib


def test_install_total_is_laptop_only_against_live_ceilings():
    ceilings = _ceilings()
    for profile in ("toaster", "phone", "pi"):
        assert INSTALLED_TOTAL > ceilings[profile].install_mib * _MIB
    assert INSTALLED_TOTAL < ceilings["laptop"].install_mib * _MIB


def test_program_file_is_its_recorded_size():
    # The pin is deliberate: any future slice that grows
    # the program file fails here until the budget proof
    # is re-measured (the E-057 re-pin discipline).
    assert CREDSTORE.stat().st_size == PROGRAM_BYTES


def test_scrypt_working_set_arithmetic_from_the_programs_constants():
    src = CREDSTORE.read_text(encoding="utf-8")
    for needle in ("_SCRYPT_N = 16384", "_SCRYPT_R = 8",
                   "_SCRYPT_P = 1"):
        assert needle in src, needle
    # The derivation's theoretical working set: 128*N*r.
    assert 128 * 16384 * 8 == 16 * _MIB


def test_dependency_installed_size_supports_the_verdict():
    places = [Path(site.getusersitepackages())]
    places += [Path(p) for p in site.getsitepackages()]
    pkg = next((p / "cryptography" for p in places
                if (p / "cryptography").is_dir()), None)
    if pkg is None:
        import pytest

        pytest.skip("cryptography not installed in this environment")
    size = sum(f.stat().st_size for f in pkg.rglob("*") if f.is_file())
    # A band, not a pin: bytecode caches come and go with
    # imports. The verdict needs only the order of weight.
    assert 14 * _MIB < size < 17 * _MIB
    assert size + PROGRAM_BYTES > _ceilings()["pi"].install_mib * _MIB


# ── The storage curve, re-derived on a scratch vault ────


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
    return subprocess.run(
        [sys.executable, str(CREDSTORE), *argv],
        capture_output=True, text=True, env=env, check=True,
        stdin=subprocess.DEVNULL)


def _sizes(vault: Path) -> dict[str, int]:
    out = {"total": 0, "backups": 0, "backup_files": 0}
    for p in vault.rglob("*"):
        if p.is_file():
            out["total"] += p.stat().st_size
            if p.parent.name == "backups":
                out["backups"] += p.stat().st_size
                out["backup_files"] += 1
    out["blob"] = (vault / "vault.json.enc").stat().st_size
    return out


def test_probe_storage_curve_on_a_scratch_vault(tmp_path):
    vault = tmp_path / "vault"
    _run(tmp_path, vault, "init")
    empty = _sizes(vault)
    assert empty["total"] < 1000  # the whole empty estate
    assert empty["blob"] < 400
    pw = tmp_path / "pw.txt"
    pw.write_text("synthetic-pass-value-1234")
    for n in range(1, 11):
        _run(tmp_path, vault, "add", f"svc-{n:03d}",
             "--username", "synthetic-user",
             "--password-file", str(pw),
             "--url", "https://example.invalid/login",
             "--notes", "synthetic note for sizing")
    ten = _sizes(vault)
    per_entry = (ten["blob"] - empty["blob"]) / 10
    # The measured band around the recorded ~563 B/entry:
    # wide enough for timestamp-shape wobble, narrow
    # enough to catch a second store or an index growing
    # silently beside the blob.
    assert 450 < per_entry < 750
    assert ten["backup_files"] == 5  # the cap holds
    # The whole estate stays a small multiple of the blob:
    # current + five backups + key + meta, nothing else.
    assert ten["total"] < 7 * ten["blob"] + 1000
    assert ten["total"] < 40_000


def test_probe_wrapping_the_key_costs_its_recorded_shape(tmp_path):
    vault = tmp_path / "vault"
    _run(tmp_path, vault, "init")
    bare = (vault / ".vault_key").stat().st_size
    assert bare == 44
    home = tmp_path / "home"
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["KISTA_DIR"] = str(vault)
    env["KISTA_PASSPHRASE"] = "correct horse battery staple"
    parts = [str(KISTA), site.getusersitepackages(),
             env.get("PYTHONPATH", "")]
    env["PYTHONPATH"] = os.pathsep.join(p for p in parts if p)
    subprocess.run(
        [sys.executable, str(CREDSTORE), "set-passphrase"],
        capture_output=True, text=True, env=env, check=True,
        stdin=subprocess.DEVNULL)
    wrapped = (vault / ".vault_key").stat().st_size
    assert wrapped == 274  # 44 B of key in its scrypt envelope
