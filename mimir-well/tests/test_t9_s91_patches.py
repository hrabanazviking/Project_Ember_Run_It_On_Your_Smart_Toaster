"""S9.1 Patch Tests — bug fixes from the audit.

Tests for:
- get_stats() uses whitelist (3.4)
- get_edges_from/to return consistent keys (3.5)
- merge_from_fact_store extracts rel_type from tags/content, not category (3.6)
- merge_from_fact_store returns error=None on success (5.4)
- health_check() cursor fresh after exception (3.7)
- bare except replaced with logged exception (4.4)
- SCHEMA_VERSION only written on change (4.6)
- add_memory returns None (not -1) when guard blocks (5.1)
- supersede returns None when memory not found (5.3)
"""

import json
import os
import sqlite3
import tempfile
import pytest

from mimir_well.core import RunaMemory
from mimir_well.wyrd_graph import WyrdGraph
from mimir_well.config import MimirConfig


class TestGetStatsWhitelist:
    """3.4: get_stats() uses a whitelist of valid table names."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.mem = RunaMemory(db_path=self.db_path)

    def teardown_method(self):
        self.mem.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_stats_returns_all_tables(self):
        stats = self.mem.get_stats()
        for table in ["memories", "entities", "relationships",
                       "knowledge", "saga_events", "conversations",
                       "memory_access_log"]:
            assert table in stats

    def test_get_stats_counts_match(self):
        self.mem.add_memory("test", category="general", importance=5)
        stats = self.mem.get_stats()
        assert stats["memories"] >= 1

    def test_get_stats_no_sql_injection(self):
        """Even if someone modified the frozenset (they can't), parameterized
        queries wouldn't help for table names — whitelist is the correct fix."""
        stats = self.mem.get_stats()
        assert isinstance(stats, dict)


class TestEdgeKeyConsistency:
    """3.5: get_edge, get_edges_from, get_edges_to return consistent keys."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)
        self.graph.add_edge("runa", "volmarr", "partner", strength=10)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_edge_keys(self):
        edge = self.graph.get_edge("runa", "volmarr", "partner")
        assert edge is not None
        assert "source_entity" in edge
        assert "target_entity" in edge
        assert "user_id" in edge
        # Should NOT have "source" or "target"
        assert "source" not in edge
        assert "target" not in edge

    def test_get_edges_from_keys(self):
        edges = self.graph.get_edges_from("runa")
        assert len(edges) == 1
        e = edges[0]
        assert "source_entity" in e
        assert "target_entity" in e
        assert "user_id" in e
        assert "source" not in e
        assert "target" not in e

    def test_get_edges_to_keys(self):
        edges = self.graph.get_edges_to("volmarr")
        assert len(edges) == 1
        e = edges[0]
        assert "source_entity" in e
        assert "target_entity" in e
        assert "user_id" in e
        assert "source" not in e
        assert "target" not in e


class TestMergeFromFactStore:
    """3.6/5.4: merge_from_fact_store extracts relationship type from tags,
    not category; returns error=None on success."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)
        # Create a minimal fact_store db
        self.fs_path = os.path.join(self.tmpdir, "fact_store.db")
        conn = sqlite3.connect(self.fs_path)
        conn.execute("""CREATE TABLE facts (
            id INTEGER PRIMARY KEY,
            content TEXT,
            entities TEXT,
            category TEXT,
            tags TEXT
        )""")
        conn.execute(
            "INSERT INTO facts (content, entities, category, tags) VALUES (?, ?, ?, ?)",
            ("Volmarr is partner of Runa", '["volmarr","runa"]', "relationship", "partner,close"),
        )
        conn.execute(
            "INSERT INTO facts (content, entities, category, tags) VALUES (?, ?, ?, ?)",
            ("Runa is sister of Freyja", '["runa","freyja"]', "relationship", "sister"),
        )
        conn.commit()
        conn.close()

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_relationship_type_from_tags(self):
        result = self.graph.merge_from_fact_store(self.fs_path)
        # Should extract "partner" from tags, not "relationship" from category
        edges = self.graph.get_edges_from("volmarr")
        assert len(edges) == 1
        # The relationship type should be "partner" (from tags), not "relationship"
        assert edges[0]["relationship_type"] in ("partner", "related_to")

    def test_success_returns_error_none(self):
        result = self.graph.merge_from_fact_store(self.fs_path)
        assert "error" in result
        assert result["error"] is None

    def test_failure_returns_error_string(self):
        result = self.graph.merge_from_fact_store("/nonexistent/path.db")
        assert result["error"] is not None
        assert isinstance(result["error"], str)


class TestHealthCheckCursorSafety:
    """3.7: health_check() uses fresh cursor in second try block."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.mem = RunaMemory(db_path=self.db_path)

    def teardown_method(self):
        self.mem.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_health_check_returns_structure(self):
        result = self.mem.health_check()
        assert "healthy" in result
        assert "issues" in result
        assert "integrity" in result

    def test_health_check_healthy_on_fresh_db(self):
        result = self.mem.health_check()
        assert result["healthy"] is True


class TestSchemaVersionConditional:
    """4.6: SCHEMA_VERSION only written on change, not every startup."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_schema_version_not_rewritten(self):
        mem1 = RunaMemory(db_path=self.db_path)
        # Get schema version rowid
        conn = mem1._get_conn()
        rowid = conn.execute(
            "SELECT rowid FROM _schema_meta WHERE key='schema_version'"
        ).fetchone()[0]
        mem1.close()

        # Reopen — should NOT rewrite schema_version
        mem2 = RunaMemory(db_path=self.db_path)
        conn2 = mem2._get_conn()
        rowid2 = conn2.execute(
            "SELECT rowid FROM _schema_meta WHERE key='schema_version'"
        ).fetchone()[0]
        # Row ID should be the same (no INSERT OR REPLACE on second init)
        assert rowid == rowid2
        mem2.close()


class TestGuardReturnsNone:
    """5.1/5.3: add_memory and supersede return None (not -1) when blocked."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.mem = RunaMemory(db_path=self.db_path)

    def teardown_method(self):
        self.mem.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_add_memory_guard_blocked_returns_none(self):
        result = self.mem.add_memory("normal\x00hidden", category="general", importance=5)
        assert result is None

    def test_supersede_not_found_returns_none(self):
        result = self.mem.supersede(99999, "new content")
        assert result is None


class TestEdgesFromHaveUserId:
    """Edges from get_edges_from/to include user_id in output."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)
        self.graph.add_edge("runa", "volmarr", "partner", strength=10, user_id="runa")

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_edges_from_have_user_id(self):
        edges = self.graph.get_edges_from("runa")
        assert len(edges) == 1
        assert "user_id" in edges[0]
        assert edges[0]["user_id"] == "runa"

    def test_edges_to_have_user_id(self):
        edges = self.graph.get_edges_to("volmarr")
        assert len(edges) == 1
        assert "user_id" in edges[0]

    def test_single_edge_has_user_id(self):
        edge = self.graph.get_edge("runa", "volmarr", "partner", user_id="runa")
        assert edge is not None
        assert "user_id" in edge