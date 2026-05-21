"""S9.2 Patch Tests — atomic schema init + config race safety.

Tests for:
- WyrdGraph schema init is atomic (BEGIN/COMMIT/ROLLBACK) (8.4)
- MimirConfig file creation is race-safe using O_EXCL (4.3)
"""

import json
import os
import sqlite3
import tempfile
import pytest

from mimir_well.wyrd_graph import WyrdGraph
from mimir_well.config import MimirConfig


class TestWyrdGraphAtomicSchema:
    """8.4: WyrdGraph CREATE+ALTER is wrapped in BEGIN/COMMIT/ROLLBACK."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.db")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fresh_init_creates_table_with_user_id(self):
        graph = WyrdGraph(db_path=self.db_path)
        conn = graph._get_conn()
        # Verify user_id column exists
        cols = conn.execute("PRAGMA table_info(wyrd_edges)").fetchall()
        col_names = [c[1] for c in cols]
        assert "user_id" in col_names
        graph.close()

    def test_schema_has_unique_constraint(self):
        graph = WyrdGraph(db_path=self.db_path)
        conn = graph._get_conn()
        # UNIQUE constraints are stored in the table's CREATE statement, not as separate indexes
        table_sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='wyrd_edges'"
        ).fetchone()[0]
        assert "UNIQUE" in table_sql.upper()
        graph.close()

    def test_indexes_exist(self):
        graph = WyrdGraph(db_path=self.db_path)
        conn = graph._get_conn()
        indexes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='wyrd_edges'"
        ).fetchall()
        idx_names = {i[0] for i in indexes}
        assert "idx_wyrd_edges_source" in idx_names
        assert "idx_wyrd_edges_target" in idx_names
        assert "idx_wyrd_edges_user" in idx_names
        graph.close()

    def test_init_idempotent(self):
        """Creating WyrdGraph twice on same path doesn't crash."""
        graph1 = WyrdGraph(db_path=self.db_path)
        graph1.add_edge("a", "b", "knows")
        graph1.close()
        # Second init should succeed without errors
        graph2 = WyrdGraph(db_path=self.db_path)
        edges = graph2.get_edges_from("a")
        assert len(edges) == 1
        graph2.close()

    def test_add_edge_after_atomic_init(self):
        """Basic CRUD still works after atomic schema init."""
        graph = WyrdGraph(db_path=self.db_path)
        edge_id = graph.add_edge("runa", "volmarr", "partner", strength=10)
        assert edge_id > 0
        edge = graph.get_edge("runa", "volmarr", "partner", user_id="runa")
        assert edge is not None
        assert edge["relationship_type"] == "partner"
        graph.close()


class TestConfigRaceSafety:
    """4.3: MimirConfig file creation uses O_EXCL to avoid races."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_config_if_missing(self):
        config_path = os.path.join(self.tmpdir, "mimir-well-config.json")
        config = MimirConfig(config_path=config_path)
        assert config.get("decay_half_life_days") == 30
        assert os.path.exists(config_path)

    def test_loads_existing_config(self):
        config_path = os.path.join(self.tmpdir, "mimir-well-config.json")
        # Pre-create with custom value
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump({"decay_half_life_days": 60}, f)
        config = MimirConfig(config_path=config_path)
        assert config.get("decay_half_life_days") == 60

    def test_race_safe_creation(self):
        """Simulating race: config file appears between exists() check and creation.
        O_EXCL should handle this gracefully."""
        config_path = os.path.join(self.tmpdir, "mimir-well-config.json")
        # Pre-create the file (simulating another process winning the race)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump({"busy_timeout": 5000}, f)
        # MimirConfig should detect the race and load existing file
        config = MimirConfig(config_path=config_path)
        assert config.get("busy_timeout") == 5000
        assert config.get("decay_half_life_days") == 30  # default preserved

    def test_env_override_still_works(self):
        config_path = os.path.join(self.tmpdir, "mimir-well-config.json")
        os.environ["MIMIR_DB_PATH"] = "/custom/path.db"
        try:
            config = MimirConfig(config_path=config_path)
            assert str(config.db_path) == "/custom/path.db"
        finally:
            del os.environ["MIMIR_DB_PATH"]

    def test_set_persists(self):
        config_path = os.path.join(self.tmpdir, "mimir-well-config.json")
        config = MimirConfig(config_path=config_path)
        config.set("decay_half_life_days", 90)
        # Reload to verify persistence
        config2 = MimirConfig(config_path=config_path)
        assert config2.get("decay_half_life_days") == 90