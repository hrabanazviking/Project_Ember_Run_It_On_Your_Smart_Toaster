"""S9.2c: WyrdGraph method coverage tests.

Covers: remove_edge, get_edges_to, traverse, get_related,
edge_count, entity_count, relationship_types, merge_from_fact_store edge cases.
"""

import json
import os
import sqlite3
import tempfile
import pytest

from mimir_well.wyrd_graph import WyrdGraph


class TestRemoveEdge:
    """remove_edge: delete specific edges."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)
        self.graph.add_edge("a", "b", "friend", strength=5)
        self.graph.add_edge("b", "c", "friend", strength=3)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_remove_existing_edge(self):
        result = self.graph.remove_edge("a", "b", "friend")
        assert result is True
        assert self.graph.get_edge("a", "b", "friend") is None

    def test_remove_nonexistent_edge(self):
        result = self.graph.remove_edge("x", "y", "unknown")
        assert result is False

    def test_remove_preserves_other_edges(self):
        self.graph.remove_edge("a", "b", "friend")
        assert self.graph.get_edge("b", "c", "friend") is not None

    def test_remove_with_user_id(self):
        self.graph.add_edge("a", "c", "colleague", strength=2, user_id="other")
        # Remove default user's edge only
        self.graph.remove_edge("a", "b", "friend", user_id="runa")
        assert self.graph.get_edge("a", "b", "friend") is None


class TestTraverse:
    """traverse: BFS traversal from seed entity."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)
        # Build: runa -> volmarr -> freyja
        self.graph.add_edge("runa", "volmarr", "partner", strength=10)
        self.graph.add_edge("volmarr", "freyja", "patron", strength=8)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_traverse_depth_1(self):
        result = self.graph.traverse("runa", max_depth=1)
        entities = {r["entity"] for r in result}
        assert "volmarr" in entities
        assert "freyja" not in entities  # depth 1 only

    def test_traverse_depth_2(self):
        result = self.graph.traverse("runa", max_depth=2)
        entities = {r["entity"] for r in result}
        assert "volmarr" in entities
        assert "freyja" in entities

    def test_traverse_empty_seed(self):
        result = self.graph.traverse("nonexistent", max_depth=2)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_traverse_filters_by_relationship_type(self):
        self.graph.add_edge("runa", "odin", "mentor", strength=7)
        result = self.graph.traverse("runa", max_depth=1, relationship_type="partner")
        entities = {r["entity"] for r in result}
        assert "volmarr" in entities
        assert "odin" not in entities


class TestGetRelated:
    """get_related: get entities related to a seed."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_related_finds_connections(self):
        self.graph.add_edge("runa", "volmarr", "partner", strength=10)
        self.graph.add_edge("runa", "freyja", "worships", strength=9)
        related = self.graph.get_related("runa", max_depth=1)
        # get_related returns a dict with "outgoing" list
        assert isinstance(related, dict)
        outgoing_entities = {r["entity"] for r in related.get("outgoing", [])}
        assert "volmarr" in outgoing_entities
        assert "freyja" in outgoing_entities

    def test_get_related_empty(self):
        related = self.graph.get_related("nobody", max_depth=1)
        assert isinstance(related, dict)


class TestGetEdgesTo:
    """get_edges_to: incoming edges to an entity."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)
        self.graph.add_edge("runa", "volmarr", "partner", strength=10)
        self.graph.add_edge("freyja", "volmarr", "patron", strength=7)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_edges_to_returns_incoming(self):
        edges = self.graph.get_edges_to("volmarr")
        assert len(edges) == 2
        sources = {e["source_entity"] for e in edges}
        assert "runa" in sources
        assert "freyja" in sources

    def test_get_edges_to_filters_by_type(self):
        edges = self.graph.get_edges_to("volmarr", relationship_type="partner")
        assert len(edges) == 1
        assert edges[0]["source_entity"] == "runa"

    def test_get_edges_to_empty(self):
        edges = self.graph.get_edges_to("nobody")
        assert len(edges) == 0


class TestEdgeCountEntityCount:
    """edge_count and entity_count stats methods."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_edge_count_empty(self):
        assert self.graph.edge_count() == 0

    def test_edge_count_with_edges(self):
        self.graph.add_edge("a", "b", "knows")
        self.graph.add_edge("b", "c", "knows")
        assert self.graph.edge_count() == 2

    def test_edge_count_filters_by_user(self):
        self.graph.add_edge("a", "b", "knows", user_id="runa")
        self.graph.add_edge("c", "d", "knows", user_id="other")
        assert self.graph.edge_count(user_id="runa") == 1

    def test_entity_count(self):
        self.graph.add_edge("a", "b", "knows")
        # 2 unique entities: a and b
        assert self.graph.entity_count() >= 2

    def test_relationship_types_empty(self):
        types = self.graph.relationship_types()
        assert isinstance(types, list)
        assert len(types) == 0

    def test_relationship_types_with_data(self):
        self.graph.add_edge("a", "b", "friend")
        self.graph.add_edge("c", "d", "enemy")
        types = self.graph.relationship_types()
        assert "friend" in types
        assert "enemy" in types


class TestMergeFromFactStoreEdgeCases:
    """Extended coverage for merge_from_fact_store."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.graph = WyrdGraph(db_path=self.db_path)

    def teardown_method(self):
        self.graph.close()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_merge_empty_fact_store(self):
        """Empty fact store should return zeros, no error."""
        fs_path = os.path.join(self.tmpdir, "empty.db")
        conn = sqlite3.connect(fs_path)
        conn.execute("""CREATE TABLE facts (
            id INTEGER PRIMARY KEY, content TEXT, entities TEXT,
            category TEXT, tags TEXT)""")
        conn.commit()
        conn.close()
        result = self.graph.merge_from_fact_store(fs_path)
        assert result["edges_created"] == 0
        assert result["error"] is None

    def test_merge_single_entity_fact(self):
        """Facts with only one entity should be skipped."""
        fs_path = os.path.join(self.tmpdir, "single.db")
        conn = sqlite3.connect(fs_path)
        conn.execute("""CREATE TABLE facts (
            id INTEGER PRIMARY KEY, content TEXT, entities TEXT,
            category TEXT, tags TEXT)""")
        conn.execute(
            "INSERT INTO facts (content, entities, category, tags) VALUES (?,?,?,?)",
            ("Runa is wise", '["runa"]', "relationship", "wise"),
        )
        conn.commit()
        conn.close()
        result = self.graph.merge_from_fact_store(fs_path)
        assert result["edges_skipped"] >= 1

    def test_merge_nonexistent_db(self):
        """Non-existent fact store should return error."""
        result = self.graph.merge_from_fact_store("/nonexistent/path.db")
        assert result["error"] is not None
        assert result["edges_created"] == 0

    def test_merge_extract_type_from_content(self):
        """Should extract relationship type from content pattern."""
        fs_path = os.path.join(self.tmpdir, "content.db")
        conn = sqlite3.connect(fs_path)
        conn.execute("""CREATE TABLE facts (
            id INTEGER PRIMARY KEY, content TEXT, entities TEXT,
            category TEXT, tags TEXT)""")
        conn.execute(
            "INSERT INTO facts (content, entities, category, tags) VALUES (?,?,?,?)",
            ("Volmarr is partner of Runa", '["volmarr","runa"]', "relationship", ""),
        )
        conn.commit()
        conn.close()
        self.graph.merge_from_fact_store(fs_path)
        edges = self.graph.get_edges_from("volmarr")
        assert len(edges) == 1
        # Should extract "partner" from content pattern
        assert edges[0]["relationship_type"] == "partner"