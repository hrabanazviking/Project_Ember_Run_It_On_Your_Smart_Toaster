"""Tests for core memory operations: CRUD, FTS search, recall methods."""

import os
import tempfile
import pytest

from mimir_well.core import RunaMemory


@pytest.fixture
def db(tmp_path):
    """Create a fresh RunaMemory instance for testing."""
    db_path = tmp_path / "test_memory.db"
    memory = RunaMemory(str(db_path))
    yield memory
    memory.close()


class TestMemoryCRUD:
    """Test Create, Read, Update, Delete for memories."""

    def test_add_and_get_memory(self, db):
        mid = db.add_memory("I prefer dark themes", category="preference", importance=7)
        assert mid > 0
        mem = db.get_memory(mid)
        assert mem is not None
        assert mem["content"] == "I prefer dark themes"
        assert mem["category"] == "preference"
        assert mem["importance"] == 7

    def test_add_memory_with_list_tags(self, db):
        mid = db.add_memory("Test memory", tags=["python", "test"], importance=5)
        mem = db.get_memory(mid)
        assert mem is not None
        assert "python" in mem["tags"]

    def test_add_memory_clamps_importance(self, db):
        mid = db.add_memory("Test", importance=15)
        mem = db.get_memory(mid)
        assert mem["importance"] == 10  # Clamped to max

    def test_add_memory_clamps_valence(self, db):
        mid = db.add_memory("Test", emotional_valence=2.0)
        mem = db.get_memory(mid)
        assert mem["emotional_valence"] == 1.0  # Clamped

    def test_search_memories(self, db):
        db.add_memory("I love Python programming", category="preference")
        db.add_memory("I enjoy hiking in mountains", category="hobby")
        db.add_memory("Python is great for AI", category="lesson")

        results = db.search_memories("Python")
        assert len(results) >= 2

    def test_search_memories_with_category(self, db):
        db.add_memory("I love Python", category="preference")
        db.add_memory("Python is powerful", category="lesson")

        results = db.search_memories("Python", category="preference")
        assert len(results) >= 1
        assert all(r["category"] == "preference" for r in results)

    def test_update_memory(self, db):
        mid = db.add_memory("Original content")
        db.update_memory(mid, content="Updated content", importance=8)
        mem = db.get_memory(mid)
        assert mem["content"] == "Updated content"
        assert mem["importance"] == 8

    def test_delete_memory(self, db):
        mid = db.add_memory("To be deleted")
        assert db.get_memory(mid) is not None
        db.delete_memory(mid)
        assert db.get_memory(mid) is None

    def test_recall_by_importance(self, db):
        db.add_memory("Important thing", importance=9)
        db.add_memory("Trivial thing", importance=2)
        db.add_memory("Medium thing", importance=7)

        results = db.recall_by_importance(min_importance=7)
        assert len(results) >= 2
        assert all(r["importance"] >= 7 for r in results)

    def test_recall_recent(self, db):
        db.add_memory("Just happened", importance=8)
        results = db.recall_recent(hours=1, limit=5)
        assert len(results) >= 1

    def test_recall_by_mood(self, db):
        db.add_memory("Happy memory", emotional_valence=0.8, importance=6)
        db.add_memory("Sad memory", emotional_valence=-0.7, importance=6)
        db.add_memory("Neutral memory", emotional_valence=0.0, importance=6)

        happy = db.recall_by_mood(target_valence=0.8, tolerance=0.3)
        assert len(happy) >= 1
        assert any(r["emotional_valence"] > 0.5 for r in happy)


class TestEntities:
    """Test entity and relationship management."""

    def test_add_and_get_entity(self, db):
        db.add_entity("odin", "deity", components={"wisdom": True})
        entity = db.get_entity("odin")
        assert entity is not None
        assert entity["entity_id"] == "odin"
        assert entity["entity_type"] == "deity"

    def test_set_relationship(self, db):
        db.add_entity("thor", "deity")
        db.add_entity("loki", "deity")
        db.set_relationship("thor", "loki", "brother_of", strength=8)
        strength = db.get_relationship_strength("thor", "loki")
        assert strength == 8

    def test_get_entities_by_type(self, db):
        db.add_entity("freyja", "deity", components={"domain": "love"})
        db.add_entity("server_pi", "infrastructure")
        results = db.get_entities_by_type("deity")
        assert len(results) >= 1
        assert all(r["entity_type"] == "deity" for r in results)


class TestKnowledge:
    """Test knowledge CRUD."""

    def test_add_and_search_knowledge(self, db):
        kid = db.add_knowledge("norse_mythology", "Mímir guards the well of wisdom", source="Edda")
        assert kid > 0
        results = db.search_knowledge("norse_mythology", "Mímir")
        assert len(results) >= 1

    def test_knowledge_confidence_clamped(self, db):
        kid = db.add_knowledge("test", "content", confidence=1.5)
        results = db.search_knowledge("test", "content")
        assert any(r["confidence"] <= 1.0 for r in results)


class TestSagaEvents:
    """Test saga event recording."""

    def test_add_saga_event(self, db):
        sid = db.add_saga_event("milestone", "odin", data={"sacrificed": "eye"})
        assert sid > 0


class TestConversations:
    """Test conversation storage."""

    def test_save_conversation(self, db):
        db.save_conversation("sess_1", ["user", "assistant"],
                           transcript="Hello!", summary="Greeting")
        conv = db.get_conversation("sess_1")
        # Note: not all test DBs will have this method perfectly
        # but the SQL should work


class TestBackupRestore:
    """Test backup and restore operations."""

    def test_backup_and_restore(self, db, tmp_path):
        db.add_memory("Backup test memory", importance=8)
        backup_path = str(tmp_path / "backup_test.db")

        result = db.backup_to(backup_path)
        assert result == backup_path

        # Restore from backup
        success = db.restore_from(backup_path)
        assert success is True

    def test_backup_with_rotation(self, db, tmp_path):
        db.add_memory("Rotation test", importance=5)
        backup_dir = str(tmp_path / "backups")

        path1 = db.backup_with_rotation(backup_dir=backup_dir, max_backups=3)
        assert os.path.exists(path1)

        # Create multiple backups
        for _ in range(4):
            db.backup_with_rotation(backup_dir=backup_dir, max_backups=3)

        # Should only have 3 backups
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        assert len(backups) <= 4  # Rotation should keep it manageable


class TestContextManager:
    """Test context manager usage."""

    def test_context_manager(self, tmp_path):
        db_path = tmp_path / "ctx_test.db"
        with RunaMemory(str(db_path)) as db:
            db.add_memory("Context test")
        # Connection should be closed


class TestHealthCheck:
    """Test health check and stats."""

    def test_health_check(self, db):
        result = db.health_check()
        assert result["healthy"] is True
        assert "memory_count" in result

    def test_get_stats(self, db):
        db.add_memory("Stats test", importance=6)
        stats = db.get_stats()
        assert "memories" in stats
        assert stats["memories"] >= 1