"""S9.4d: eye/app.py (Flask dashboard) test coverage.

Covers: dashboard, tab rendering, api_stats, api_search, health,
_get_base_stats, query_db.

Uses Flask test client — no live server needed.

Addresses audit finding 9.3: eye/app.py had ZERO test coverage.
"""

import json
import os
import pytest


@pytest.fixture
def app_client(tmp_path):
    """Create a Flask test client with a temp database."""
    db_path = str(tmp_path / "test_eye.db")
    os.environ["DB_PATH"] = db_path

    from mimir_well.core import RunaMemory
    from mimir_well.wyrd_graph import WyrdGraph

    mimir = RunaMemory(db_path=db_path)
    mimir.add_memory(content="Test memory for dashboard", category="test", importance=7)
    mimir.add_memory(content="Another memory", category="preference", importance=8)

    graph = WyrdGraph(db_path=db_path)
    graph.add_edge("runa", "volmarr", "partner", strength=10)

    mimir.close()
    graph.close()

    from mimir_well.eye.app import app
    app.config["TESTING"] = True
    client = app.test_client()

    yield client

    os.environ.pop("DB_PATH", None)


class TestHealth:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, app_client):
        resp = app_client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_json(self, app_client):
        resp = app_client.get("/health")
        data = json.loads(resp.data)
        assert "status" in data

    def test_health_reports_ok(self, app_client):
        resp = app_client.get("/health")
        data = json.loads(resp.data)
        assert data["status"] == "ok"


class TestAPIStats:
    """Tests for the /api/stats endpoint."""

    def test_stats_returns_200(self, app_client):
        resp = app_client.get("/api/stats")
        assert resp.status_code == 200

    def test_stats_returns_json(self, app_client):
        resp = app_client.get("/api/stats")
        data = json.loads(resp.data)
        assert isinstance(data, dict)


class TestAPISearch:
    """Tests for the /api/search endpoint."""

    def test_search_returns_results(self, app_client):
        resp = app_client.get("/api/search?q=Test")
        assert resp.status_code == 200

    def test_search_returns_json(self, app_client):
        resp = app_client.get("/api/search?q=Test")
        data = json.loads(resp.data)
        assert isinstance(data, (list, dict))

    def test_search_with_empty_query(self, app_client):
        # Empty query returns 400 — search requires a query string
        resp = app_client.get("/api/search?q=")
        assert resp.status_code == 400

    def test_search_with_no_query_param(self, app_client):
        # Missing q param returns 400 — search requires a query
        resp = app_client.get("/api/search")
        assert resp.status_code == 400


class TestDashboard:
    """Tests for dashboard HTML routes (all tabs on /)."""

    def test_dashboard_returns_200(self, app_client):
        resp = app_client.get("/")
        assert resp.status_code == 200

    def test_dashboard_returns_html(self, app_client):
        resp = app_client.get("/")
        assert b"<" in resp.data  # Should have HTML tags

    def test_memories_tab(self, app_client):
        resp = app_client.get("/?tab=memories")
        assert resp.status_code == 200

    def test_relationships_tab(self, app_client):
        resp = app_client.get("/?tab=relationships")
        assert resp.status_code == 200

    def test_knowledge_tab(self, app_client):
        resp = app_client.get("/?tab=knowledge")
        assert resp.status_code == 200

    def test_factstore_tab(self, app_client):
        resp = app_client.get("/?tab=factstore")
        assert resp.status_code == 200


class TestGetBaseStats:
    """Tests for _get_base_stats helper."""

    def test_base_stats_returns_dict(self, app_client):
        from mimir_well.eye.app import _get_base_stats
        stats = _get_base_stats()
        assert isinstance(stats, dict)

    def test_base_stats_has_expected_keys(self, app_client):
        from mimir_well.eye.app import _get_base_stats
        stats = _get_base_stats()
        assert "stats" in stats
        assert "fact_stats" in stats
        assert "db_size" in stats

    def test_base_stats_db_size_positive(self, app_client):
        from mimir_well.eye.app import _get_base_stats
        stats = _get_base_stats()
        assert stats["db_size"] >= 0


class TestQueryDB:
    """Tests for the query_db helper with a fresh temp DB."""

    def test_query_db_one(self, tmp_path):
        db_path = str(tmp_path / "test_qdb.db")
        os.environ["DB_PATH"] = db_path

        from mimir_well.core import RunaMemory
        mimir = RunaMemory(db_path=db_path)
        mimir.add_memory(content="Query test", category="test", importance=5)
        mimir.close()

        from mimir_well.eye.app import query_db
        result = query_db("DB_PATH", "SELECT COUNT(*) as cnt FROM memories", one=True)
        assert result is not None
        # Result may be a Row or dict
        count = result["cnt"] if isinstance(result, dict) else result[0]
        assert count >= 1

        os.environ.pop("DB_PATH", None)

    def test_query_db_all(self, tmp_path):
        db_path = str(tmp_path / "test_qdb2.db")
        os.environ["DB_PATH"] = db_path

        from mimir_well.core import RunaMemory
        mimir = RunaMemory(db_path=db_path)
        mimir.add_memory(content="Query test 1", category="test", importance=5)
        mimir.add_memory(content="Query test 2", category="test", importance=5)
        mimir.close()

        from mimir_well.eye.app import query_db
        result = query_db("DB_PATH", "SELECT * FROM memories", one=False)
        assert isinstance(result, list)
        assert len(result) >= 2

        os.environ.pop("DB_PATH", None)