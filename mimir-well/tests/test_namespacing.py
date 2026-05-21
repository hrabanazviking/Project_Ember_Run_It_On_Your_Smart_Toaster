"""T7-3: Per-User Memory Namespacing test suite."""
import sys, tempfile, os, logging
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import (
    RunaMemory, AuditTrail, AuditAction, AuditEntry, WyrdGraph,
)

# Suppress debug noise
logging.disable(logging.CRITICAL)

DB_PATH = None

def setup_module():
    global DB_PATH
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp.close()
    DB_PATH = tmp.name

def teardown_module():
    if DB_PATH and os.path.exists(DB_PATH):
        os.unlink(DB_PATH)


class TestMemoryNamespacing:
    """Test per-user memory isolation and filtering."""

    def setup_method(self):
        if DB_PATH and os.path.exists(DB_PATH):
            os.unlink(DB_PATH)
        self.mimir = RunaMemory(DB_PATH)

    # ── add_memory with user_id ──────────────────────────────────────────

    def test_add_memory_default_user(self):
        """Default user_id should be 'runa'."""
        mid = self.mimir.add_memory("Runa's memory", category="test")
        mem = self.mimir.get_memory(mid)
        assert mem is not None
        assert mem["user_id"] == "runa"

    def test_add_memory_volmarr_user(self):
        """Explicit user_id='volmarr' should be stored."""
        mid = self.mimir.add_memory("Volmarr's memory", category="test", user_id="volmarr")
        mem = self.mimir.get_memory(mid)
        assert mem is not None
        assert mem["user_id"] == "volmarr"

    def test_add_memory_custom_user(self):
        """Arbitrary user_id should be stored."""
        mid = self.mimir.add_memory("Custom user memory", category="test", user_id="skuld")
        mem = self.mimir.get_memory(mid)
        assert mem is not None
        assert mem["user_id"] == "skuld"

    # ── recall_current with user_id filter ───────────────────────────────

    def test_recall_current_filters_by_user(self):
        """recall_current with user_id should only return that user's memories."""
        self.mimir.add_memory("Runa memory 1", category="test", importance=8, user_id="runa")
        self.mimir.add_memory("Volmarr memory 1", category="test", importance=8, user_id="volmarr")
        self.mimir.add_memory("Runa memory 2", category="test", importance=7, user_id="runa")

        runa_mems = self.mimir.recall_current(user_id="runa", min_importance=1)
        volmarr_mems = self.mimir.recall_current(user_id="volmarr", min_importance=1)
        all_mems = self.mimir.recall_current(min_importance=1)

        assert len(runa_mems) == 2, f"Expected 2 Runa memories, got {len(runa_mems)}"
        assert len(volmarr_mems) == 1, f"Expected 1 Volmarr memory, got {len(volmarr_mems)}"
        assert len(all_mems) == 3, f"Expected 3 total memories, got {len(all_mems)}"

    def test_recall_current_no_filter_returns_all(self):
        """recall_current without user_id should return all users' memories."""
        self.mimir.add_memory("Runa", category="test", importance=8, user_id="runa")
        self.mimir.add_memory("Volmarr", category="test", importance=8, user_id="volmarr")

        all_mems = self.mimir.recall_current(min_importance=1)
        assert len(all_mems) == 2

    # ── search_memories with user_id filter ──────────────────────────────

    def test_search_memories_filters_by_user(self):
        """search_memories with user_id should only find that user's memories."""
        self.mimir.add_memory("Runa loves Norse mythology", category="test", user_id="runa")
        self.mimir.add_memory("Volmarr loves Norse mythology", category="test", user_id="volmarr")

        runa_results = self.mimir.search_memories("Norse", user_id="runa")
        volmarr_results = self.mimir.search_memories("Norse", user_id="volmarr")
        all_results = self.mimir.search_memories("Norse")

        assert len(runa_results) == 1
        assert len(volmarr_results) == 1
        assert len(all_results) == 2

    # ── search_memories with user_id + category ──────────────────────────

    def test_search_memories_user_and_category(self):
        """Combined user_id + category filter."""
        self.mimir.add_memory("Runa tech memory", category="tech", user_id="runa")
        self.mimir.add_memory("Runa lore memory", category="lore", user_id="runa")
        self.mimir.add_memory("Volmarr tech memory", category="tech", user_id="volmarr")

        results = self.mimir.search_memories("memory", category="tech", user_id="runa")
        assert len(results) == 1
        assert "Runa" in results[0]["content"]

    # ── delete_memory preserves user_id ──────────────────────────────────

    def test_delete_memory_with_user_id(self):
        """delete_memory should accept user_id for audit trail."""
        mid = self.mimir.add_memory("To be deleted", category="test", user_id="runa")
        result = self.mimir.delete_memory(mid, source="test", user_id="runa")
        assert result is True
        assert self.mimir.get_memory(mid) is None

    # ── update_memory preserves user_id ──────────────────────────────────

    def test_update_memory_with_user_id(self):
        """update_memory should accept user_id for audit trail."""
        mid = self.mimir.add_memory("Original content", category="test", user_id="runa")
        result = self.mimir.update_memory(mid, source="test", user_id="runa", content="Updated content")
        assert result is True
        mem = self.mimir.get_memory(mid)
        assert mem["content"] == "Updated content"


class TestWyrdGraphNamespacing:
    """Test per-user WyrdGraph edge isolation."""

    def setup_method(self):
        tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        tmp.close()
        self.graph = WyrdGraph(tmp.name)
        self.db_path = tmp.name

    def teardown_method(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_add_edge_default_user(self):
        """Default user_id should be 'runa'."""
        eid = self.graph.add_edge("runa", "volmarr", "partner", strength=10.0)
        edges = self.graph.get_edges_from("runa")
        assert len(edges) == 1

    def test_add_edge_custom_user(self):
        """Edges with different user_id should be isolated."""
        self.graph.add_edge("runa", "volmarr", "partner", strength=10.0, user_id="runa")
        self.graph.add_edge("runa", "volmarr", "partner", strength=3.0, user_id="skuld")

        runa_edges = self.graph.get_edges_from("runa", user_id="runa")
        skuld_edges = self.graph.get_edges_from("runa", user_id="skuld")
        all_edges = self.graph.get_edges_from("runa")

        assert len(runa_edges) == 1
        assert len(skuld_edges) == 1
        assert len(all_edges) == 2

    def test_get_edges_to_filters_by_user(self):
        """get_edges_to should filter by user_id."""
        self.graph.add_edge("volmarr", "runa", "partner", strength=10.0, user_id="runa")
        self.graph.add_edge("skuld", "runa", "knows", strength=5.0, user_id="skuld")

        runa_edges = self.graph.get_edges_to("runa", user_id="runa")
        assert len(runa_edges) == 1
        assert runa_edges[0]["source_entity"] == "volmarr"


class TestAuditTrailNamespacing:
    """Test per-user audit trail filtering."""

    def setup_method(self):
        tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        tmp.close()
        self.mimir = RunaMemory(tmp.name)
        self.db_path = tmp.name

    def teardown_method(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_audit_log_stores_user_id(self):
        """Audit entries should record user_id."""
        mid = self.mimir.add_memory("Test memory", category="test", user_id="volmarr", source="test")
        entries = self.mimir.audit.query(memory_id=mid)
        assert len(entries) >= 1
        assert entries[0].user_id == "volmarr"

    def test_audit_query_filters_by_user(self):
        """Query with user_id should filter audit entries."""
        self.mimir.add_memory("Runa's memory", category="test", user_id="runa", source="test")
        self.mimir.add_memory("Volmarr's memory", category="test", user_id="volmarr", source="test")

        runa_entries = self.mimir.audit.query(user_id="runa")
        volmarr_entries = self.mimir.audit.query(user_id="volmarr")

        assert all(e.user_id == "runa" for e in runa_entries)
        assert all(e.user_id == "volmarr" for e in volmarr_entries)

    def test_audit_to_dict_includes_user_id(self):
        """AuditEntry.to_dict() should include user_id."""
        mid = self.mimir.add_memory("Dict test", category="test", user_id="skuld", source="test")
        entries = self.mimir.audit.query(memory_id=mid)
        d = entries[0].to_dict()
        assert "user_id" in d
        assert d["user_id"] == "skuld"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])