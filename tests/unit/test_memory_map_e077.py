"""E-077 — Both memory systems mapped, in depth.

Pins docs/architecture/E-077_BOTH_MEMORY_SYSTEMS_MAPPED.md
against the tree it describes:

* the map doc exists and names all three systems, the
  roadmap slices that inherit from it (E-078/E-079/E-080/
  E-085), and the new docket items 108-110;
* tracked sizes of both member directories are exactly
  the E-057 figures re-pinned at E-076 (257 files /
  59,049,715 B mempalace; 58 files / 607,675 B
  mimir-well) — neither member has changed since import;
* the storage shapes the doc states are real: mimir-well's
  schema tables + FTS5 virtuals, Brunnr's two schema.sql
  shapes (vec0 + FTS5; pgvector HNSW + tsvector), and
  mempalace's palace/KG/searcher modules;
* the retrieval surfaces the doc states are real:
  RunaMemory's named methods, BrunnrHandle's 12 protocol
  methods, mempalace's hybrid weights (0.6/0.4) and its
  exactly-30 MCP tool functions;
* the consumer facts: the core imports neither member
  system, and bifrost carries two independent mimir
  consumers (bridge + core) beside Verdandi's check.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-077_BOTH_MEMORY_SYSTEMS_MAPPED.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _top_level_methods(path: Path, class_name: str) -> set[str]:
    tree = ast.parse(_text(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {n.name for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    raise AssertionError(f"class {class_name} not found in {path}")


def test_doc_exists_and_names_the_three_systems_and_inheritors():
    text = _text(DOC)
    for needle in ("mempalace", "mimir-well", "Brunnr",
                   "E-078", "E-079", "E-080", "E-085",
                   "docket 51", "docket 54"):
        assert needle in text, needle
    for item in (108, 109, 110):
        assert f"({item})" in text, f"docket {item} not in the map doc"


def _tracked_size(rel: str) -> tuple[int, int]:
    out = subprocess.run(
        ["git", "ls-files", rel], cwd=REPO, capture_output=True,
        text=True, check=True).stdout.splitlines()
    total = sum((REPO / name).stat().st_size for name in out)
    return len(out), total


def test_member_tracked_sizes_match_e057_repinned_at_e076():
    assert _tracked_size("mempalace") == (257, 59_049_715)
    assert _tracked_size("mimir-well") == (58, 607_675)


def test_mimir_schema_shape_is_as_mapped():
    schema = _text(REPO / "mimir-well/src/mimir_well/schema.py")
    for table in ("memories", "saga_events", "entities",
                  "relationships", "conversations", "knowledge",
                  "memory_access_log", "wyrd_edges", "memory_audit"):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in schema, table
    for virt in ("memories_fts", "knowledge_fts", "saga_events_fts"):
        assert f"CREATE VIRTUAL TABLE IF NOT EXISTS {virt}" in schema, virt
    assert "SCHEMA_VERSION = 9" in schema
    # The living columns of the memories row.
    for col in ("importance", "emotional_valence", "valid_from",
                "valid_until", "superseded_by", "is_current",
                "memory_type", "user_id"):
        assert col in schema, col


def test_brunnr_schema_shapes_are_as_mapped():
    sqlite_sql = _text(
        REPO / "src/ember/well/brunnr/sqlite_vec/schema.sql")
    for needle in ("documents", "chunks", "chunk_vectors",
                   "USING vec0", "chunk_fts", "USING fts5",
                   "episodes"):
        assert needle in sqlite_sql, needle
    pg_sql = _text(REPO / "src/ember/well/brunnr/pgvector/schema.sql")
    for needle in ("documents", "chunks", "hnsw",
                   "vector_cosine_ops", "tsvector", "episodes"):
        assert needle in pg_sql, needle


def test_runa_memory_surface_is_as_mapped():
    methods = _top_level_methods(
        REPO / "mimir-well/src/mimir_well/core.py", "RunaMemory")
    for name in ("add_memory", "get_memory", "search_memories",
                 "fts_search", "recall_by_importance", "recall_recent",
                 "recall_by_mood", "store_with_validity", "supersede",
                 "recall_current", "decay", "consolidate",
                 "promote_to_knowledge", "detect_contradictions",
                 "integrity_check", "export_to_json", "health_check"):
        assert name in methods, name


def test_brunnr_handle_protocol_has_12_methods():
    methods = _top_level_methods(
        REPO / "src/ember/well/brunnr/handle.py", "BrunnrHandle")
    assert methods == {
        "add_document", "add_chunks", "add_episode", "recent_episodes",
        "vector_search", "text_search", "hybrid_search", "get_document",
        "get_chunk", "has_document", "count", "close",
    }, sorted(methods)


def test_mempalace_retrieval_shape_is_as_mapped():
    searcher = _text(REPO / "mempalace/mempalace/searcher.py")
    assert "vector_weight: float = 0.6" in searcher
    assert "bm25_weight: float = 0.4" in searcher
    assert "_bm25_only_via_sqlite" in searcher
    mcp = _text(REPO / "mempalace/mempalace/mcp_server.py")
    tools = [n.name for n in ast.parse(mcp).body
             if isinstance(n, ast.FunctionDef)
             and n.name.startswith("tool_")]
    assert len(tools) == 30, tools
    kg = _text(REPO / "mempalace/mempalace/knowledge_graph.py")
    assert "CREATE TABLE IF NOT EXISTS entities" in kg
    assert "CREATE TABLE IF NOT EXISTS triples" in kg
    emb = _text(REPO / "mempalace/mempalace/embedding.py")
    assert "all-MiniLM-L6-v2" in emb and "384-dim" in emb


def test_consumer_facts_are_as_mapped():
    core_hits = []
    for path in (REPO / "src/ember").rglob("*.py"):
        src = _text(path)
        if "mempalace" in src or "mimir_well" in src \
                or "RunaMemory" in src:
            core_hits.append(str(path.relative_to(REPO)))
    assert core_hits == [], core_hits
    bridge = _text(REPO / "bifrost/src/bifrost/bridges/memory_bridge.py")
    core = _text(REPO / "bifrost/src/bifrost/core.py")
    bifrost_config = _text(REPO / "bifrost/src/bifrost/config.py")
    assert "runa_memory.db" in bridge
    assert "_ensure_mimir" in core and "mimir_db_path" in core
    assert "runa_memory.db" in bifrost_config
    check = _text(REPO / "Verdandi/heartbeat/checks/mimir.py")
    assert ".mimir_well" in check and "mimir_well.db" in check
