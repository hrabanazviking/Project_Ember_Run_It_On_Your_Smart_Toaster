"""E-079 — The verdict paper: unify / bound / retire.

Pins docs/architecture/E-079_MEMORY_VERDICT_PAPER.md:

* the doc exists and delivers the BOUND verdict: one
  face, Brunnr bounded to documents/chunks/episodes,
  mimir-well bounded to living facts + lifecycle;
* the evidence numbers it argues from are the E-078
  canonical ones (20/20 verbatim, paraphrase 9/9 vs 0/9,
  exact living rows, budget figures);
* all three single-system crowns are argued and refused;
* the mempalace retirement is a PROPOSAL for Volmarr's
  word only — the member is still present in the tree,
  unretired, and the bounded fallback is stated;
* the inheritor assignments name E-080, E-081, E-091,
  E-092 and E-196, and E-080 is stated not blocked by
  the retirement question.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-079_MEMORY_VERDICT_PAPER.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_doc_exists_and_delivers_bound_verdict():
    text = _text(DOC)
    for needle in ("Bound", "one face", "Brunnr",
                   "mimir-well", "mempalace",
                   "documents, chunks", "living facts"):
        assert needle in text, needle


def test_evidence_numbers_are_e078_canonical():
    text = _text(DOC)
    for needle in ("20/20", "9/9", "0/9", "402.8 MiB",
                   "614,283 B", "745 B", "585 B/episode",
                   "185 MB", "88 MB"):
        assert needle in text, needle


def test_three_crowns_refused():
    text = _text(DOC)
    assert text.count("Refused") >= 3
    for needle in ("Unify on mempalace", "Unify on mimir-well",
                   "Unify on Brunnr"):
        assert needle in text, needle


def test_retirement_is_proposal_only_member_untouched():
    text = _text(DOC)
    for needle in ("Volmarr's word", "Proposed",
                   "Until he rules", "stays exactly where it is"):
        assert needle in text, needle
    # The proposal decided nothing in the tree: the member
    # is still here, with its packaging intact.
    assert (REPO / "mempalace" / "pyproject.toml").exists()
    assert (REPO / "mimir-well" / "pyproject.toml").exists()


def test_fallback_and_inheritors_named():
    text = _text(DOC)
    for needle in ("fallback", "never-bundled", "E-080",
                   "E-081", "E-091", "E-092", "E-196",
                   "not blocked"):
        assert needle in text, needle
    # Docket obligations the verdict lays on E-080/gate.
    for needle in ("docket 51", "docket 109", "docket 110",
                   "docket 108", "docket 72"):
        assert needle in text, needle
