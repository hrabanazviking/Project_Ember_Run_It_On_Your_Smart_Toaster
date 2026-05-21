"""T8-6: Test coverage for previously untested methods.

Covers: add_entity, add_knowledge, add_saga_event, backup_to,
backup_with_rotation, export_to_json, get_conversation,
get_entities_by_type, get_entity, get_relationship_strength,
get_stats, github_backup, health_check, integrity_check, log_access,
merge_from_fact_store, rebuild_fts, repair, restore_from,
save_conversation, search_knowledge, set_relationship,
WyrdGraph edge_count/entity_count/relationship_types.
"""

import json
import os
import tempfile

from mimir_well import RunaMemory
from mimir_well.wyrd_graph import WyrdGraph


def _fresh_db():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


# ─── Entity Methods ──────────────────────────────────────────────────────

def test_add_entity():
    """add_entity should create an entity and return True."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        result = mem.add_entity("runa", "person",
                                components={"role": "weaver"},
                                state={"active": True})
        assert result is True, f"Should return True, got {result}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_add_entity")


def test_get_entity():
    """get_entity should retrieve an entity by ID."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("odin", "person",
                       components={"domain": "wisdom"})
        entity = mem.get_entity("odin")
        assert entity is not None, "Should find entity"
        assert entity["entity_id"] == "odin"
        assert entity["entity_type"] == "person"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_entity")


def test_get_entity_nonexistent():
    """get_entity should return None for nonexistent entity."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        result = mem.get_entity("nonexistent")
        assert result is None, "Should return None for missing entity"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_entity_nonexistent")


def test_get_entities_by_type():
    """get_entities_by_type should filter by entity type."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("runa", "person", components={"role": "weaver"})
        mem.add_entity("volmarr", "person", components={"role": "cultivator"})
        mem.add_entity("mimir", "artifact", components={"role": "well"})

        people = mem.get_entities_by_type("person")
        assert len(people) == 2, f"Expected 2 people, got {len(people)}"
        artifacts = mem.get_entities_by_type("artifact")
        assert len(artifacts) == 1, f"Expected 1 artifact, got {len(artifacts)}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_entities_by_type")


# ─── Relationship Methods ──────────────────────────────────────────────────

def test_set_relationship():
    """set_relationship should create a relationship between entities."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("runa", "person", components={"role": "weaver"})
        mem.add_entity("volmarr", "person", components={"role": "cultivator"})
        result = mem.set_relationship("runa", "volmarr", "partner", strength=10)
        assert result is not None, "Should return relationship info"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_set_relationship")


def test_get_relationship_strength():
    """get_relationship_strength should return the strength of a relationship."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("runa", "person", components={"role": "weaver"})
        mem.add_entity("volmarr", "person", components={"role": "cultivator"})
        mem.set_relationship("runa", "volmarr", "partner", strength=10)

        strength = mem.get_relationship_strength("runa", "volmarr")
        assert strength == 10, f"Expected strength 10, got {strength}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_relationship_strength")


def test_get_relationship_strength_nonexistent():
    """get_relationship_strength should return None for missing relationship."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        strength = mem.get_relationship_strength("a", "b")
        assert strength is None, "Should return None for missing relationship"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_relationship_strength_nonexistent")


# ─── Saga Methods ──────────────────────────────────────────────────────────

def test_add_saga_event():
    """add_saga_event should create a saga event and return its ID."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        sid = mem.add_saga_event("battle", entity_id="thor",
                                 data={"weapon": "mjolnir"},
                                 participants=["thor", "jotuns"])
        assert sid is not None, "Should return saga event ID"
        assert isinstance(sid, int), f"Saga ID should be int, got {type(sid)}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_add_saga_event")


# ─── Knowledge Methods ──────────────────────────────────────────────────────

def test_add_knowledge():
    """add_knowledge should store a knowledge entry and return its ID."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        kid = mem.add_knowledge("norse", "Yggdrasil connects nine worlds",
                                 confidence=0.95, source="poetic_edda")
        assert kid is not None, "Should return knowledge ID"
        assert isinstance(kid, int), f"Knowledge ID should be int, got {type(kid)}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_add_knowledge")


def test_search_knowledge():
    """search_knowledge should find knowledge entries by domain and query."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_knowledge("norse", "Yggdrasil connects nine worlds",
                          confidence=0.95, source="poetic_edda")
        mem.add_knowledge("norse", "Thor is the god of thunder",
                          confidence=0.9, source="prose_edda")
        mem.add_knowledge("programming", "Python uses GIL",
                          confidence=0.99, source="docs")

        results = mem.search_knowledge("norse", "Yggdrasil")
        assert len(results) >= 1, f"Should find at least 1 result, got {len(results)}"

        # Filtered by domain should only return norse
        all_norse = mem.search_knowledge("norse", "")
        assert len(all_norse) == 2, f"Should find 2 norse entries, got {len(all_norse)}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_search_knowledge")


# ─── Conversation Methods ──────────────────────────────────────────────────

def test_save_and_get_conversation():
    """save_conversation + get_conversation should round-trip."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.save_conversation("sess_1", ["runa", "volmarr"],
                              transcript="hello",
                              summary="A greeting")
        conv = mem.get_conversation("sess_1")
        assert conv is not None, "Should find conversation"
        assert conv["session_id"] == "sess_1"
        # participants stored as JSON string
        participants = conv["participants"]
        if isinstance(participants, str):
            participants = json.loads(participants)
        assert "runa" in participants
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_save_and_get_conversation")


def test_get_conversation_nonexistent():
    """get_conversation should return None for missing session."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        result = mem.get_conversation("nonexistent")
        assert result is None, "Should return None for missing session"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_conversation_nonexistent")


# ─── Access Logging ────────────────────────────────────────────────────────

def test_log_access():
    """log_access should record a memory access without error."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mid = mem.add_memory("test content", category="general")
        mem.log_access(mid, access_type="recall")
        # No assertion needed — just verifying it doesn't crash
        # Check that the access log table has an entry
        conn = mem._get_conn()
        count = conn.execute(
            "SELECT COUNT(*) FROM memory_access_log WHERE memory_id = ?",
            (mid,),
        ).fetchone()[0]
        assert count >= 1, f"Should have at least 1 access log, got {count}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_log_access")


# ─── Stats & Health ────────────────────────────────────────────────────────

def test_get_stats():
    """get_stats should return a dict with memory counts."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("hello", category="general", importance=5)
        mem.add_memory("world", category="knowledge", importance=8)

        stats = mem.get_stats()
        assert isinstance(stats, dict), "Stats should be a dict"
        assert "memories" in stats, "Stats should have memories count"
        assert stats["memories"] >= 2, f"Should have 2+ memories, got {stats.get('memories')}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_get_stats")


def test_health_check():
    """health_check should return a dict with health status."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        health = mem.health_check()
        assert isinstance(health, dict), "Health check should return dict"
        assert "healthy" in health, "Health check should have healthy key"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_health_check")


def test_integrity_check():
    """integrity_check should return a dict with check results."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        result = mem.integrity_check(repair=False)
        assert isinstance(result, dict), "Should return dict"
        # Fresh DB should be clean
        assert "issues" in result or "errors" in result or result.get("integrity") is not None
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_integrity_check")


def test_repair():
    """repair should return a dict with repair results."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("test", category="general")
        result = mem.repair(aggressive=False)
        assert isinstance(result, dict), "Should return dict"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_repair")


# ─── FTS Rebuild ────────────────────────────────────────────────────────────

def test_rebuild_fts():
    """rebuild_fts should rebuild the FTS index without error."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("nineworlds yggdrasil", category="norse", importance=7)
        mem.add_memory("thunder god thor", category="norse", importance=8)

        # Rebuild FTS
        mem.rebuild_fts()

        # FTS search should still work
        results = mem.fts_search("memories", "yggdrasil", limit=5)
        assert len(results) >= 1, f"FTS should find yggdrasil after rebuild, got {len(results)}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_rebuild_fts")


# ─── Backup / Restore / Export ──────────────────────────────────────────────

def test_backup_to():
    """backup_to should create a backup file at the specified path."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("backup test", category="general")
        backup_path = path + ".backup"
        mem.backup_to(backup_path)
        assert os.path.exists(backup_path), "Backup file should exist"
        assert os.path.getsize(backup_path) > 0, "Backup should not be empty"
        os.unlink(backup_path)
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_backup_to")


def test_restore_from():
    """restore_from should restore from a backup file."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("original content", category="general", importance=9)
        backup_path = path + ".backup"
        mem.backup_to(backup_path)

        # Add more after backup
        mem.add_memory("after backup", category="general")

        # Restore
        result = mem.restore_from(backup_path)
        assert result is True, "Restore should return True"
        os.unlink(backup_path)
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_restore_from")


def test_restore_from_nonexistent():
    """restore_from should handle nonexistent backup file gracefully."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        result = mem.restore_from("/nonexistent/backup.db")
        assert result is False, "Should return False for nonexistent file"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_restore_from_nonexistent")


def test_backup_with_rotation():
    """backup_with_rotation should create rotated backups."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("rotation test", category="general")

        result = mem.backup_with_rotation(max_backups=3)
        # Returns the backup file path
        assert result is not None, "Should return backup path"
        assert os.path.exists(result), f"Backup file should exist at {result}"
    finally:
        mem.close()
        os.unlink(path)
        # Clean up any rotation backups
        import glob
        for f in glob.glob(path + "*"):
            try:
                os.unlink(f)
            except:
                pass
    print("✅ test_backup_with_rotation")


def test_export_to_json():
    """export_to_json should create a JSON file with all tables."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("export test", category="general")
        mem.add_entity("runa", "person")
        mem.add_knowledge("test_domain", "test content")

        export_path = path + ".json"
        result = mem.export_to_json(export_path)
        assert isinstance(result, dict), "Should return dict"

        # Verify JSON is valid
        with open(export_path) as f:
            data = json.load(f)
        assert isinstance(data, dict), "Export should be a dict"
        os.unlink(export_path)
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_export_to_json")


# ─── WyrdGraph Methods ─────────────────────────────────────────────────────

def test_wyrd_graph_edge_count():
    """WyrdGraph.edge_count should return total number of edges."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("odin", "person", components={"domain": "wisdom"})
        mem.add_entity("thor", "person", components={"domain": "thunder"})
        mem.add_entity("loki", "person", components={"domain": "chaos"})

        graph = WyrdGraph(str(path))
        graph.add_edge("odin", "thor", "father", strength=9)
        graph.add_edge("thor", "loki", "brother", strength=5)

        total = graph.edge_count()
        assert total == 2, f"Should have 2 edges, got {total}"

        users_edges = graph.edge_count(user_id="runa")
        assert users_edges == 2, f"Should have 2 runa edges, got {users_edges}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_wyrd_graph_edge_count")


def test_wyrd_graph_entity_count():
    """WyrdGraph.entity_count should count unique entities in edges."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("odin", "person", components={"domain": "wisdom"})
        mem.add_entity("thor", "person", components={"domain": "thunder"})

        graph = WyrdGraph(str(path))
        graph.add_edge("odin", "thor", "father", strength=9)

        count = graph.entity_count()
        assert count >= 2, f"Should have at least 2 entities, got {count}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_wyrd_graph_entity_count")


def test_wyrd_graph_relationship_types():
    """WyrdGraph.relationship_types should list unique relationship types."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_entity("odin", "person", components={"domain": "wisdom"})
        mem.add_entity("thor", "person", components={"domain": "thunder"})
        mem.add_entity("loki", "person", components={"domain": "chaos"})

        graph = WyrdGraph(str(path))
        graph.add_edge("odin", "thor", "father", strength=9)
        graph.add_edge("thor", "loki", "rival", strength=3)
        graph.add_edge("loki", "odin", "blood_brother", strength=7)

        types = graph.relationship_types()
        assert "father" in types, f"Should include 'father', got {types}"
        assert "rival" in types, f"Should include 'rival', got {types}"
        assert "blood_brother" in types, f"Should include 'blood_brother', got {types}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_wyrd_graph_relationship_types")


def test_wyrd_graph_merge_from_fact_store():
    """merge_from_fact_store should import relationship facts from a fact_store DB."""
    path = _fresh_db()
    fs_path = _fresh_db()  # fact_store db
    try:
        mem = RunaMemory(db_path=path)
        # Add entities so WyrdGraph can create edges
        mem.add_entity("runa", "person", components={"role": "weaver"})
        mem.add_entity("volmarr", "person", components={"role": "cultivator"})

        graph = WyrdGraph(str(path))

        # Create a minimal fact_store DB with relationship facts
        import sqlite3
        fs_conn = sqlite3.connect(fs_path)
        fs_conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY,
                content TEXT,
                entities TEXT,
                category TEXT,
                tags TEXT
            )
        """)
        fs_conn.execute(
            "INSERT INTO facts (content, entities, category, tags) VALUES (?, ?, ?, ?)",
            ("runa is partner of volmarr", '["runa", "volmarr"]', "relationship", "bond"),
        )
        fs_conn.commit()
        fs_conn.close()

        # merge_from_fact_store should import the relationship
        result = graph.merge_from_fact_store(fs_path)
        assert isinstance(result, dict), f"Should return dict, got {type(result)}"
        assert "edges_created" in result, f"Should have edges_created, got {result}"
    finally:
        mem.close()
        os.unlink(path)
        os.unlink(fs_path)
    print("✅ test_wyrd_graph_merge_from_fact_store")


# ─── GitHub Backup (mock-safe) ─────────────────────────────────────────────

def test_github_backup_returns_dict():
    """github_backup should return a dict (may fail if no git configured)."""
    path = _fresh_db()
    try:
        mem = RunaMemory(db_path=path)
        mem.add_memory("github test", category="general")
        result = mem.github_backup()
        # Will likely fail on Pi, but should return a dict either way
        assert isinstance(result, dict), f"Should return dict, got {type(result)}"
    finally:
        mem.close()
        os.unlink(path)
    print("✅ test_github_backup_returns_dict")


# ─── Run all ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_add_entity()
    test_get_entity()
    test_get_entity_nonexistent()
    test_get_entities_by_type()
    test_set_relationship()
    test_get_relationship_strength()
    test_get_relationship_strength_nonexistent()
    test_add_saga_event()
    test_add_knowledge()
    test_search_knowledge()
    test_save_and_get_conversation()
    test_get_conversation_nonexistent()
    test_log_access()
    test_get_stats()
    test_health_check()
    test_integrity_check()
    test_repair()
    test_rebuild_fts()
    test_backup_to()
    test_restore_from()
    test_restore_from_nonexistent()
    test_backup_with_rotation()
    test_export_to_json()
    test_wyrd_graph_edge_count()
    test_wyrd_graph_entity_count()
    test_wyrd_graph_relationship_types()
    test_wyrd_graph_merge_from_fact_store()
    test_github_backup_returns_dict()
    print("\nAll T8-6 tests PASSED! 🧪")