"""T8-3: Verify WyrdGraph methods respect user_id isolation.

- remove_edge with user_id only deletes that user's edge
- get_edge with user_id only returns that user's edge
- traverse with user_id only follows that user's edges
- get_related with user_id combines both directions correctly
- edge_count/entity_count/relationship_types with user_id
"""

import os
import tempfile

from mimir_well.wyrd_graph import WyrdGraph


def _fresh_graph():
    """Create a fresh WyrdGraph with a temp database."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    graph = WyrdGraph(db_path=f.name)
    return graph, f.name


def test_remove_edge_user_isolation():
    """remove_edge with user_id should only delete edges owned by that user."""
    graph, db_path = _fresh_graph()
    try:
        # Same triple, different users
        graph.add_edge("runa", "volmarr", "partner", strength=10.0, user_id="runa")
        graph.add_edge("runa", "volmarr", "partner", strength=5.0, user_id="volmarr")

        # Runa removes their edge
        removed = graph.remove_edge("runa", "volmarr", "partner", user_id="runa")
        assert removed is True

        # Volmarr's edge should still exist
        volmarr_edge = graph.get_edge("runa", "volmarr", "partner", user_id="volmarr")
        assert volmarr_edge is not None
        assert volmarr_edge["user_id"] == "volmarr"
        assert volmarr_edge["strength"] == 5.0
    finally:
        graph.close()
        os.unlink(db_path)
    print("✅ test_remove_edge_user_isolation")


def test_get_edge_user_isolation():
    """get_edge with user_id should only return that user's edge."""
    graph, db_path = _fresh_graph()
    try:
        graph.add_edge("runa", "volmarr", "partner", strength=10.0, user_id="runa")
        graph.add_edge("runa", "volmarr", "partner", strength=3.0, user_id="volmarr")

        # Get runa's edge
        runa_edge = graph.get_edge("runa", "volmarr", "partner", user_id="runa")
        assert runa_edge is not None
        assert runa_edge["strength"] == 10.0
        assert runa_edge["user_id"] == "runa"

        # Get volmarr's edge
        volmarr_edge = graph.get_edge("runa", "volmarr", "partner", user_id="volmarr")
        assert volmarr_edge is not None
        assert volmarr_edge["strength"] == 3.0
        assert volmarr_edge["user_id"] == "volmarr"

        # Without user_id, get_edge returns first match (multi-user edge)
        any_edge = graph.get_edge("runa", "volmarr", "partner")
        assert any_edge is not None
    finally:
        graph.close()
        os.unlink(db_path)
    print("✅ test_get_edge_user_isolation")


def test_traverse_user_isolation():
    """traverse with user_id should only follow edges owned by that user."""
    graph, db_path = _fresh_graph()
    try:
        # Runa's graph: runa -> volmarr -> freyja
        graph.add_edge("runa", "volmarr", "partner", user_id="runa")
        graph.add_edge("volmarr", "freyja", "mentor", user_id="runa")

        # Volmarr's graph: runa -> volmarr -> odin (different path!)
        graph.add_edge("runa", "volmarr", "colleague", user_id="volmarr")
        graph.add_edge("volmarr", "odin", "worships", user_id="volmarr")

        # Runa's traversal should only find runa's edges
        runa_results = graph.traverse("runa", max_depth=2, user_id="runa")
        runa_targets = {r["entity"] for r in runa_results}
        assert "volmarr" in runa_targets, f"volmarr should be reachable, got {runa_targets}"
        assert "freyja" in runa_targets, f"freyja should be reachable through volmarr"
        assert "odin" not in runa_targets, f"odin belongs to volmarr, not runa"

        # Volmarr's traversal should only find volmarr's edges
        volmarr_results = graph.traverse("runa", max_depth=2, user_id="volmarr")
        volmarr_targets = {r["entity"] for r in volmarr_results}
        assert "volmarr" in volmarr_targets
        assert "odin" in volmarr_targets, f"odin should be reachable through volmarr"
        assert "freyja" not in volmarr_targets, f"freyja belongs to runa, not volmarr"
    finally:
        graph.close()
        os.unlink(db_path)
    print("✅ test_traverse_user_isolation")


def test_get_related_user_isolation():
    """get_related with user_id should combine outgoing and incoming for that user only."""
    graph, db_path = _fresh_graph()
    try:
        graph.add_edge("runa", "volmarr", "partner", strength=10.0, user_id="runa")
        graph.add_edge("freyja", "runa", "patron", strength=8.0, user_id="runa")
        graph.add_edge("runa", "odin", "worships", strength=7.0, user_id="volmarr")

        result = graph.get_related("runa", max_depth=1, user_id="runa")
        outgoing_targets = {r["entity"] for r in result["outgoing"]}
        incoming_sources = {r["entity"] for r in result["incoming"]}

        assert "volmarr" in outgoing_targets, f"volmarr should be in outgoing, got {outgoing_targets}"
        assert "freyja" in incoming_sources, f"freyja should be in incoming, got {incoming_sources}"
        assert "odin" not in outgoing_targets, f"odin belongs to volmarr"
    finally:
        graph.close()
        os.unlink(db_path)
    print("✅ test_get_related_user_isolation")


def test_stats_user_isolation():
    """edge_count, entity_count, relationship_types should filter by user_id."""
    graph, db_path = _fresh_graph()
    try:
        graph.add_edge("runa", "volmarr", "partner", strength=10.0, user_id="runa")
        graph.add_edge("runa", "freyja", "patron", strength=8.0, user_id="runa")
        graph.add_edge("volmarr", "odin", "worships", strength=7.0, user_id="volmarr")

        # Total counts
        assert graph.edge_count() == 3
        assert graph.entity_count() == 4  # runa, volmarr, freyja, odin
        assert "partner" in graph.relationship_types()
        assert "worships" in graph.relationship_types()

        # Runa's counts
        assert graph.edge_count(user_id="runa") == 2
        assert graph.entity_count(user_id="runa") == 3  # runa, volmarr, freyja
        runa_types = graph.relationship_types(user_id="runa")
        assert "partner" in runa_types
        assert "worships" not in runa_types

        # Volmarr's counts
        assert graph.edge_count(user_id="volmarr") == 1
        assert graph.entity_count(user_id="volmarr") == 2  # volmarr, odin
        volmarr_types = graph.relationship_types(user_id="volmarr")
        assert "worships" in volmarr_types
        assert "partner" not in volmarr_types
    finally:
        graph.close()
        os.unlink(db_path)
    print("✅ test_stats_user_isolation")


if __name__ == "__main__":
    test_remove_edge_user_isolation()
    test_get_edge_user_isolation()
    test_traverse_user_isolation()
    test_get_related_user_isolation()
    test_stats_user_isolation()
    print("\nAll T8-3 tests PASSED! 🗡️")