"""E-078 — The comparison harness: identical workloads, three systems.

Pins docs/architecture/E-078_MEMORY_COMPARISON_HARNESS.md
against the tree and the harness it describes:

* the doc exists and names all three systems, the
  workload families, docket 111, and the inheritor slice
  E-079;
* the harness exists at scripts/dev/compare_memory_systems.py,
  carries exactly the corpus the doc states (20 items,
  9 with paraphrases, the changed-fact pair, 12 episode
  turns), and has one child runner per system;
* the docket-111 fix is real in the member: schema.py
  declares FTS_TRIGGERS for all three external-content
  FTS tables (insert/delete/update each), core.py
  executes them at open, and the schema's old "auto-sync,
  no triggers needed" claim is gone;
* the member regression tests exist beside the fix.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-078_MEMORY_COMPARISON_HARNESS.md"
HARNESS = REPO / "scripts" / "dev" / "compare_memory_systems.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_doc_exists_and_names_systems_workloads_and_inheritor():
    text = _text(DOC)
    for needle in ("mempalace", "mimir-well", "Brunnr",
                   "docket 111", "E-079",
                   "verbatim", "paraphrase",
                   "importance", "mood", "current",
                   "episode"):
        assert needle in text, needle


def _load_harness():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "compare_memory_systems", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_harness_corpus_is_the_doc_stated_one():
    module = _load_harness()
    corpus = module.CORPUS
    episodes = module.EPISODES
    assert len(corpus) == 20
    assert sum(1 for i in corpus if i["paraphrase"]) == 9
    tokens = [i["token"] for i in corpus]
    assert len(set(tokens)) == 20  # hit detection needs unique markers
    for item in corpus:
        assert item["token"] in item["text"], item["slug"]
        assert item["verbatim"] in item["text"], item["slug"]
    assert len(episodes) == 12  # the Brunnr episode row


def test_harness_has_a_child_per_system():
    text = _text(HARNESS)
    for name in ("run_mimir", "run_brunnr", "run_mempalace"):
        assert f"def {name}(" in text, name
    for needle in ("search_memories", "fts_search",
                   "text_search", "vector_search", "hybrid_search",
                   "recall_by_importance", "recall_by_mood",
                   "recall_current", "recent_episodes"):
        assert needle in text, needle


def test_docket_111_fix_is_real_in_the_member():
    schema = _text(REPO / "mimir-well/src/mimir_well/schema.py")
    assert "FTS_TRIGGERS" in schema
    for table in ("memories", "knowledge", "saga_events"):
        for suffix in ("ai", "ad", "au"):
            assert f"{table}_fts_{suffix}" in schema, (table, suffix)
    assert "auto-syncs on INSERT, UPDATE, and DELETE" not in schema
    assert "No triggers are needed" not in schema
    core = _text(REPO / "mimir-well/src/mimir_well/core.py")
    assert "FTS_TRIGGERS" in core
    regression = REPO / "mimir-well" / "tests" / "test_fts_sync.py"
    assert regression.exists()
    assert "fts_search" in _text(regression)
