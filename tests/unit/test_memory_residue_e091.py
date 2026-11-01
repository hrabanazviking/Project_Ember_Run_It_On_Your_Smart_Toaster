"""E-091 — The verdict's residue: docs marked truthfully.

Pins docs/architecture/E-091_VERDICT_RESIDUE.md and the
three markings it records:

* the project's living inventory no longer carries
  docket 52's stale mempalace characterisation — the
  corrected row names the E-079 verdict, the bounded
  standing, and the successor, `MemoryFace`;
* the Yggdrasil corpus's dedicated MemPalace document
  opens with its superseded/bounded banner (successor
  named) before its pre-verdict body, and the corpus's
  two front doors carry the status note;
* the residue record itself states the standing and its
  limits: retirement proposed, not decided — it awaits
  Volmarr's word, and silence is never a ruling;
* the member itself stands present and unmodified at
  its pinned measure, and `src/` carries no mempalace
  reference — the adapter the sibling document designed
  was never built.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-091_VERDICT_RESIDUE.md"
UNWIRED = REPO / "docs" / "UNWIRED_INVENTORY.md"
SIBLING = (REPO / "docs" / "yggdrasil" / "siblings"
           / "19_SIBLING_MEMPALACE.md")
MATRIX = (REPO / "docs" / "yggdrasil" / "siblings"
          / "10_SIBLING_MATRIX_OVERVIEW.md")
INDEX = REPO / "docs" / "yggdrasil" / "INDEX.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tracked_size(rel: str) -> tuple[int, int]:
    out = subprocess.run(
        ["git", "ls-files", rel], cwd=REPO, capture_output=True,
        text=True, check=True).stdout.splitlines()
    total = sum((REPO / name).stat().st_size for name in out)
    return len(out), total


def test_residue_doc_states_the_standing_and_its_limits():
    text = _text(DOC)
    for needle in ("bounded, not retired", "MemoryFace",
                   "successor", "non-default, never-bundled",
                   "Retirement is proposed, not decided",
                   "Volmarr's word", "Silence is never read",
                   "docket 52", "65 files", "61",
                   "does NOT claim", "E-092", "docket 108"):
        assert needle in text, needle


def test_unwired_row_is_corrected_docket_52():
    text = _text(UNWIRED)
    # The stale characterisation is gone: its verdict phrase
    # was unique to the mempalace row, and the row itself no
    # longer carries either stale shape. (The Hamr row's own
    # "content unclear" is a different row's business.)
    assert "Likely abandoned or archival" not in text
    row = next(line for line in text.splitlines()
               if line.startswith("| **mempalace**"))
    assert "content unclear" not in row
    assert "abandoned" not in row
    for needle in ("v3.3.5", "BOUNDED", "E-079", "MemoryFace",
                   "E-080", "non-default, never bundled",
                   "E-091", "docket 52"):
        assert needle in row, needle
    # The correction is dated on the file's face, not silent.
    assert "corrected 2026-11-01 at E-091 (docket 52)" in text


def test_sibling_doc_banner_precedes_its_body():
    text = _text(SIBLING)
    banner = text.index("STATUS — SUPERSEDED IN PART, BOUNDED")
    body = text.index("## What it is")
    assert banner < body
    head = text[:body]
    for needle in ("never built", "E-079", "MemoryFace",
                   "E-080", "bounded", "non-default",
                   "never bundled", "proposed, not",
                   "Volmarr's word", "MIT (E-007)",
                   "E-091_VERDICT_RESIDUE"):
        assert needle in head, needle


def test_front_doors_carry_the_status_note():
    for path in (MATRIX, INDEX):
        text = _text(path)
        assert "Status note — MemPalace (E-091" in text, path
        assert "MemoryFace" in text, path
        assert "E-079" in text, path


def test_member_stands_present_and_unmodified():
    assert (REPO / "mempalace" / "pyproject.toml").exists()
    assert _tracked_size("mempalace") == (257, 59_049_715)


def test_src_carries_no_mempalace_reference():
    offenders = []
    for p in (REPO / "src").rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            if "mempalace" in p.read_text(
                    encoding="utf-8", errors="replace").lower():
                offenders.append(str(p.relative_to(REPO)))
    assert offenders == [], offenders
    # The adapter the sibling document designed was never built.
    assert not (REPO / "src" / "ember" / "well" / "brunnr"
                / "mempalace").exists()
