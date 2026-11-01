"""E-092 — Part V gate: one memory face live; migration
proven; the verdict paper + Volmarr's word (where
required) on record.

Pins the gate's own acts:

* docket 108 CLOSED in scope — every requirement
  mimir-well declares (build-system + project
  dependencies) is bounded both ways, like the root
  package's (E-044's law): an unbounded floor resolves a
  future breaking major silently;
* docket 125 RULED in scope — the gate doc records the
  watermark semantics as the project's law for decay
  (a pass applies only the age accrued since the last
  pass/access watermark; passes never compound), with
  the implementation assigned to a named owner;
* the memory contract is frozen at v1 — the gate doc
  records the freeze, and ``MemoryFace`` still carries
  the full public surface E-090 documented;
* the verdict's record — the gate doc states the
  mempalace retirement stands proposed, not decided:
  it awaits Volmarr's word, its recorded absence is on
  record at this gate, and the E-079 fallback is in
  force; the member itself stands present and
  unmodified at its pinned measure;
* the gate doc's accounting — every Part V docket item
  is named in it, and every Part V slice doc
  E-077–E-092 is on disk.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MIMIR = REPO / "mimir-well"
DOC = REPO / "docs" / "architecture" / "E-092_PART_V_GATE.md"
ARCH = REPO / "docs" / "architecture"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tracked_size(rel: str) -> tuple[int, int]:
    out = subprocess.run(
        ["git", "ls-files", rel], cwd=REPO, capture_output=True,
        text=True, check=True).stdout.splitlines()
    total = sum((REPO / name).stat().st_size for name in out)
    return len(out), total


# ── Docket 108: bounded both ways ───────────────────────


def test_mimir_well_requirements_are_bounded_both_ways():
    data = tomllib.loads(_source(MIMIR / "pyproject.toml"))
    reqs = list(data["build-system"]["requires"])
    reqs.extend(data["project"].get("dependencies", []))
    for extra in data["project"].get(
            "optional-dependencies", {}).values():
        reqs.extend(extra)
    assert reqs, "mimir-well declares no requirements at all?"
    for req in reqs:
        assert ">=" in req and "<" in req, \
            f"unbounded requirement: {req}"
    # The flask line docket 108 named, exactly.
    assert "flask>=3.0,<4" in data["project"]["dependencies"]


# ── The contract freeze + the live face ─────────────────


def test_memory_contract_is_frozen_at_this_gate():
    text = _source(DOC)
    assert "FROZEN" in text
    assert "version bump" in text


def test_memory_face_carries_the_documented_surface():
    import sys
    sys.path.insert(0, str(REPO / "src"))
    from ember.well.memory_face import MemoryFace
    for op in ("remember_fact", "recall_facts_word",
               "recall_current", "search_facts_meaning",
               "supersede_fact", "inspect_memory",
               "correct_fact", "export_memory",
               "delete_fact", "delete_all_memory",
               "export_wyrd", "ingest_log_candidates",
               "retract_deleted_session", "run_lifecycle",
               "lifecycle_report", "add_document",
               "add_turn", "recent_turns", "state"):
        assert callable(getattr(MemoryFace, op)), op


# ── Docket 125: the semantics, ruled ────────────────────


def test_gate_doc_rules_decay_semantics():
    text = _source(DOC)
    assert "docket 125" in text
    assert "watermark" in text
    assert "never compound" in text


# ── The verdict's record ────────────────────────────────


def test_gate_doc_records_the_word_or_its_absence():
    text = _source(DOC)
    for needle in ("Volmarr's word", "no ruling is on record",
                   "fallback", "proposed, not decided",
                   "Silence is never read"):
        assert needle in text, needle


def test_mempalace_member_stands_unmodified():
    assert (REPO / "mempalace" / "pyproject.toml").exists()
    assert _tracked_size("mempalace") == (257, 59_049_715)


# ── The gate doc's accounting ───────────────────────────


def test_gate_doc_names_every_part_v_docket():
    text = _source(DOC)
    for item in (51, 52, 100, 102, 104, 108, 109, 110, 111,
                 112, 113, 119, 120, 121, 122, 123, 124, 125, 126):
        assert f"docket {item}" in text, f"docket {item} not accounted"
    for item in range(114, 119):
        assert f"docket {item}" in text, f"docket {item} not accounted"


def test_every_part_v_slice_doc_is_on_disk():
    expected = {
        "E-077_BOTH_MEMORY_SYSTEMS_MAPPED.md",
        "E-078_MEMORY_COMPARISON_HARNESS.md",
        "E-079_MEMORY_VERDICT_PAPER.md",
        "E-080_ONE_MEMORY_CONTRACT.md",
        "E-081_MIGRATION_ANSWER.md",
        "E-082_MEMORY_LIFECYCLE.md",
        "E-083_PERSONA_SEPARATION_AT_THE_FACE.md",
        "E-084_USER_MEMORY_RIGHTS.md",
        "E-085_MEMORY_VERDANDI_RECONCILIATION.md",
        "E-086_MEMORY_WYRD_EXPORT.md",
        "E-087_CORRUPTION_RECOVERY_DRILLS.md",
        "E-088_LONG_LIFE_SOAK.md",
        "E-089_CANON_SHAPED_TEST_DATA.md",
        "E-090_MEMORY_MODEL.md",
        "E-091_VERDICT_RESIDUE.md",
        "E-092_PART_V_GATE.md",
    }
    missing = {name for name in expected if not (ARCH / name).exists()}
    assert not missing, f"missing Part V docs: {sorted(missing)}"
