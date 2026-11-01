"""E-093 — Custody law for the whole campaign.

Pins ``docs/architecture/E-093_CUSTODY_LAW.md``:

* the law itself is on record — credentials live in a
  Kista (per machine), never in configs, code, or chat;
  the interim resolver chain is the campaign standard
  until E-100; docket 46's new toaster default is
  decided (``~/.ember/kista/``, built at E-094);
  docket 48's ledger is ruled an identifier ledger
  whose removal remains the owner's word; dockets
  127/128/129 are on record with their owners;
* the tree still proves the law's starting fact — a
  fresh scan of every tracked text file finds no real
  credential: the high-confidence shapes are zero or
  exactly the classified fixture families, and every
  credential-shaped assignment in code/config is one
  of the 20 classified fixtures named in the doc;
* docket 127's fix stands — the Aesir adapter refuses
  a key file that is not exactly mode 0600 before
  reading it, and the Well resolver's own 0600
  standard is unchanged;
* exactly one tracked credential-shaped filename
  exists: the documentation-only ``.env.example``.

The scanner excludes this file itself by name (its
regex literals are the shapes it hunts), stated here,
not silently — the E-089 canon guard's own practice.
"""

from __future__ import annotations

import os
import re
import subprocess
import urllib.error
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-093_CUSTODY_LAW.md"
SELF = Path(__file__).resolve()

_TEXT_SUFFIXES = {".py", ".md", ".toml", ".yaml", ".yml",
                  ".json", ".txt", ".sh", ".js", ".ts",
                  ".tsx", ".cfg", ".ini", ".html", ".xml"}
_CODE_SUFFIXES = {".py", ".yaml", ".yml", ".toml"}

_HIGH_CONF = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}"
    r"\.[A-Za-z0-9_-]{10,}"
    r"|[Bb]earer\s+[A-Za-z0-9._-]{16,}")
_ASSIGN = re.compile(
    r"""(?i)(password|passwd|secret|api[_-]?key|token"""
    r"""|credential)\w*\s*=\s*["']([^"']{12,})["']""")
_PW_URL = re.compile(r"[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s:@]{1,64}@")


def _tracked() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True,
        text=True, check=True).stdout.splitlines()
    return [name for name in out
            if (REPO / name).resolve() != SELF]


def _text(name: str) -> str:
    return (REPO / name).read_text(encoding="utf-8",
                                   errors="replace")


def _scannable(name: str) -> bool:
    p = REPO / name
    return p.is_file() and (
        p.suffix.lower() in _TEXT_SUFFIXES
        or name.endswith(".env.example"))


# ── The law, on record ──────────────────────────────────


def test_doc_records_the_custody_law():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("in plain words", "Never in a config file",
                   "never in code", "never in chat",
                   "ai-folder", "toaster-Kista", "interim",
                   "~/.ember/kista/", "E-094", "E-100",
                   "docket 46", "docket 48", "Docket 55",
                   "docket 57", "docket 58", "docket 127",
                   "docket 128", "docket 129", "0600",
                   "Volmarr's word", "identifier ledger"):
        assert needle in text, needle


# ── The fresh scan, armed ───────────────────────────────


def test_no_unclassified_high_confidence_shapes():
    counts: dict[str, int] = {}
    for name in _tracked():
        if not _scannable(name):
            continue
        for m in _HIGH_CONF.finditer(_text(name)):
            kind = ("privkey" if "PRIVATE KEY" in m.group(0)
                    else "aws" if m.group(0).startswith("AKIA")
                    else "other")
            counts[name] = counts.get(name, 0) + 1
            assert kind in ("privkey", "aws"), \
                f"unclassified shape in {name}: {kind}"
    # Exactly the classified fixture families of doc §4.
    assert counts == {
        "kista/SKILL.md": 1,
        "kista/tests/test_credstore.py": 6,
        "tests/unit/test_tool_read_local_file.py": 2,
    }, counts


def test_credential_assignments_are_the_classified_fixtures():
    counts: dict[str, int] = {}
    for name in _tracked():
        if Path(name).suffix.lower() not in _CODE_SUFFIXES:
            continue
        if not (REPO / name).is_file():
            continue
        n = len(_ASSIGN.findall(_text(name)))
        if n:
            counts[name] = n
    assert counts == {
        "kista/tests/test_credstore.py": 13,
        "mempalace/tests/test_llm_client.py": 1,
        "mempalace/tests/test_mcp_server.py": 1,
        "scripts/dev/compare_memory_systems.py": 2,
        "tests/integration/test_pgvector_real_backend.py": 1,
        "tests/unit/test_brunnr_pgvector_secrets.py": 1,
        "tests/unit/test_dependency_diet_e044.py": 1,
    }, counts


def test_password_urls_live_only_where_classified():
    house = {
        "docs/ClawLite_Mythic_Plan/26_TOOL_FORGE_ARCHITECTURE.md",
        "docs/DEVLOG.md",
        "docs/adapters/GUNGNIR_WELL_REFERENCE.md",
        "docs/audit/E-013_CONFIG_SECRETS_CENSUS.md",
        "src/ember/tools/fetch_url.py",
        "tests/unit/test_hardening_batch_a.py",
    }
    offenders = set()
    for name in _tracked():
        if name.startswith("CloakBrowser/"):
            continue  # vendored family, classified in doc §4
        if not _scannable(name):
            continue
        if _PW_URL.search(_text(name)):
            offenders.add(name)
    assert offenders <= house, offenders - house
    assert offenders, "the classified house hits vanished?"


def test_only_tracked_credential_filename_is_the_template():
    sus = [name for name in _tracked()
           if re.search(r"(^|/)\.env($|\.)|\.pem$|\.key$|vault",
                        name)]
    assert sus == [".env.example"], sus


# ── Docket 127: the Aesir refusal + the Well standard ──


def test_aesir_key_file_must_be_mode_0600(tmp_path):
    import sys
    sys.path.insert(0, str(REPO / "src"))
    from ember.schemas.config import (
        FuniAesirConfig, FuniConfig, FuniRuntime)
    from ember.schemas.funi import Unavailable
    from ember.spark.funi.aesir import open as aesir_open

    key_file = tmp_path / "service.key"
    key_file.write_text("testkey-" + "a" * 32 + "\n",
                        encoding="utf-8")
    cfg = FuniConfig(
        runtime=FuniRuntime.AESIR,
        aesir=FuniAesirConfig(api_key_file=key_file))

    key_file.chmod(0o644)
    result = aesir_open(cfg)
    assert isinstance(result, Unavailable)
    assert "0600" in result.detail
    assert "testkey" not in result.detail

    # At 0600 the mode gate passes and the open reaches
    # its probe (dead here) — no custody refusal remains.
    key_file.chmod(0o600)
    with patch("urllib.request.urlopen",
               side_effect=urllib.error.URLError("down")):
        result = aesir_open(cfg)
    assert isinstance(result, Unavailable)
    assert "0600" not in result.detail


def test_well_resolver_mode_standard_stands():
    import sys
    sys.path.insert(0, str(REPO / "src"))
    from ember.well.brunnr.pgvector.secrets import (
        REQUIRED_FILE_MODE)
    assert REQUIRED_FILE_MODE == 0o600
    assert os.name  # the refusal is POSIX-shaped, as documented
