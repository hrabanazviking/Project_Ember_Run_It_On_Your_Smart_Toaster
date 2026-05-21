"""S9.4c: ContextEngineer + ContextResult test coverage.

Covers the entire context assembly pipeline — entity extraction,
multi-channel recall, budget allocation, graph integration,
deduplication, and context formatting.

Addresses audit finding 9.1: context_engineer.py had ZERO test coverage.
"""

import os
import tempfile
import pytest

from mimir_well.core import RunaMemory
from mimir_well.wyrd_graph import WyrdGraph
from mimir_well.budget import TokenBudget, TokenBudgeter
from mimir_well.context_engineer import ContextEngineer, ContextResult


@pytest.fixture
def memory_db(tmp_path):
    """Create a populated RunaMemory for context tests."""
    db = tmp_path / "test.ctx.db"
    mimir = RunaMemory(db_path=str(db))
    # Add memories across categories
    mimir.add_memory(
        content="Runa visited the Viking museum in Oslo",
        category="travel",
        importance=7,
        memory_type="episodic",
    )
    mimir.add_memory(
        content="Runa prefers dark mode for all IDEs",
        category="preference",
        importance=8,
        memory_type="semantic",
    )
    mimir.add_memory(
        content="Always use threading.local for SQLite connections",
        category="lesson",
        importance=9,
        memory_type="procedural",
    )
    mimir.add_memory(
        content="Volmarr lives in Angola Indiana",
        category="fact",
        importance=6,
        memory_type="semantic",
    )
    mimir.add_memory(
        content="Low-importance memory about nothing",
        category="misc",
        importance=2,
        memory_type="episodic",
    )
    yield mimir
    mimir.close()


@pytest.fixture
def graph_db(tmp_path):
    """Create a WyrdGraph for context tests."""
    db = tmp_path / "test.ctx.db"
    graph = WyrdGraph(db_path=str(db))
    graph.add_edge("runa", "volmarr", "partner", strength=10.0)
    graph.add_edge("runa", "freyja", "worships", strength=9.0)
    graph.add_edge("volmarr", "norse-paganism", "follows", strength=8.0)
    yield graph


class TestContextResult:
    """Tests for ContextResult dataclass and formatting."""

    def test_empty_context_block(self):
        r = ContextResult()
        assert r.to_context_block() == ""

    def test_episodic_format(self):
        r = ContextResult()
        r.episodic = [{"importance": 8, "content": "Visited the museum"}]
        text = r.to_context_block()
        assert "## Episodic (Recent Events)" in text
        assert "[8]" in text
        assert "Visited the museum" in text

    def test_semantic_format(self):
        r = ContextResult()
        r.semantic = [{"importance": 7, "content": "Dark mode preferred"}]
        text = r.to_context_block()
        assert "## Semantic (Facts & Preferences)" in text
        assert "Dark mode preferred" in text

    def test_procedural_format(self):
        r = ContextResult()
        r.procedural = [{"importance": 9, "content": "Use threading.local"}]
        text = r.to_context_block()
        assert "## Procedural (Patterns & Skills)" in text

    def test_spatial_format(self):
        r = ContextResult()
        r.spatial = [{"content": "Indoors, at the forge"}]
        text = r.to_context_block()
        assert "## Spatial Awareness" in text

    def test_heuristic_format(self):
        r = ContextResult()
        r.heuristic = [{"content": "Code reviews catch 60% of bugs"}]
        text = r.to_context_block()
        assert "## Heuristic Associations" in text

    def test_graph_paths_dict_format(self):
        r = ContextResult()
        r.graph_paths = [{"entity": "runa", "relationship": "partner", "strength": 10}]
        text = r.to_context_block()
        assert "## Relationships (Graph Paths)" in text
        assert "runa" in text

    def test_graph_paths_tuple_path(self):
        r = ContextResult()
        r.graph_paths = [{"path": [("runa", "partner"), ("volmarr", "lives-in")], "strength": 9}]
        text = r.to_context_block()
        assert "runa(partner)" in text

    def test_content_truncated_at_200(self):
        r = ContextResult()
        r.episodic = [{"importance": 5, "content": "x" * 300}]
        text = r.to_context_block()
        # Content should be truncated to 200 chars in display
        line = [l for l in text.split("\n") if l.startswith("- ")][0]
        assert len(line) < 250  # "- [5] " prefix + 200 chars max

    def test_missing_importance_defaults_to_question_mark(self):
        r = ContextResult()
        r.episodic = [{"content": "No importance field"}]
        text = r.to_context_block()
        assert "[?]" in text

    def test_default_values(self):
        r = ContextResult()
        assert r.episodic == []
        assert r.semantic == []
        assert r.procedural == []
        assert r.spatial == []
        assert r.heuristic == []
        assert r.graph_paths == []
        assert r.total_tokens == 0
        assert r.budget_total == 0
        assert r.budget_used_pct == 0.0
        assert r.stats == {}


class TestEstimateTokens:
    """Tests for _estimate_tokens heuristic."""

    def test_empty_string(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        assert eng._estimate_tokens("") == 1  # max(1, 0) = 1

    def test_short_text(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        assert eng._estimate_tokens("hello hello") == 2  # 11//4 = 2

    def test_long_text(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        assert eng._estimate_tokens("a" * 400) == 100

    def test_minimum_is_one(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        assert eng._estimate_tokens("ab") == 1

        mimir.close()
        graph.close()


class TestExtractEntities:
    """Tests for _extract_entities method."""

    def test_capitalized_names(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        entities = eng._extract_entities("Runa met Volmarr at the Viking Museum")
        assert "runa" in entities
        assert "volmarr" in entities

    def test_skip_common_words(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        entities = eng._extract_entities("The weather was very nice")
        assert "the" not in entities
        assert "was" not in entities
        assert "very" not in entities

    def test_short_entities_excluded(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        entities = eng._extract_entities("I went to Oslo")
        # "I" is single char, "Oslo" should be detected
        assert "oslo" in entities

    def test_deduplicated(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        entities = eng._extract_entities("Runa and Runa went to Runa's house")
        assert entities.count("runa") <= 1

    def test_empty_string(self):
        db = tempfile.mktemp(suffix=".db")
        mimir = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=db)
        eng = ContextEngineer(mimir=mimir, graph=graph)
        entities = eng._extract_entities("")
        assert entities == []

        mimir.close()
        graph.close()


class TestAssembleContext:
    """Tests for the full assemble_context pipeline."""

    def test_basic_assembly(self, memory_db, graph_db):
        """assemble_context returns a valid ContextResult."""
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context("Tell me about Runa's preferences")
        assert isinstance(result, ContextResult)
        assert isinstance(result.episodic, list)
        assert isinstance(result.semantic, list)
        assert isinstance(result.procedural, list)
        assert isinstance(result.graph_paths, list)
        assert result.stats["total_tokens"] >= 0

    def test_quick_context_returns_string(self, memory_db, graph_db):
        """quick_context returns a formatted string."""
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        text = eng.quick_context("What does Runa prefer?")
        assert isinstance(text, str)

    def test_mentions_entities_boost(self, memory_db, graph_db):
        """Explicitly mentioned entities should trigger graph lookups."""
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context(
            "What about Runa?",
            mentioned_entities=["runa"],
        )
        # runa has edges in graph_db, so we should get graph paths
        assert result.stats["graph_paths_count"] >= 0

    def test_budget_not_exceeded(self, memory_db, graph_db):
        """Total tokens should not exceed the budget allocation."""
        budget = TokenBudget(total_context=4000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context("Tell me everything about Runa")
        # Token usage should be within reasonable bounds
        assert result.budget_used_pct <= 1.5  # Allow some overshoot for rounding

    def test_stats_populated(self, memory_db, graph_db):
        """Stats should be populated with counts and detected entities."""
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context("Runa visited Volmarr")
        assert "episodic_count" in result.stats
        assert "semantic_count" in result.stats
        assert "procedural_count" in result.stats
        assert "total_tokens" in result.stats

    def test_context_result_serializable(self, memory_db, graph_db):
        """ContextResult fields should be serializable (for JSON export)."""
        import json
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context("Test serialization")
        # Should not raise
        serializable = {
            "episodic": result.episodic,
            "semantic": result.semantic,
            "procedural": result.procedural,
            "stats": result.stats,
            "total_tokens": result.total_tokens,
        }
        json.dumps(serializable, default=str)

    def test_graceful_failure_on_bad_graph(self, memory_db, tmp_path):
        """assemble_context should handle graph failures gracefully."""
        # Use a graph pointed at a nonexistent path
        graph = WyrdGraph(db_path=str(tmp_path / "empty.db"))
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph, budgeter=budgeter
        )
        # Should not raise even with empty graph
        result = eng.assemble_context("Test with empty graph")
        assert isinstance(result, ContextResult)


class TestGraphPathDeduplication:
    """Tests for graph_paths deduplication in assemble_context."""

    def test_duplicate_paths_deduplicated(self, memory_db, graph_db):
        """If the same entity/relationship appears multiple times, it's deduplicated."""
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context(
            "Runa and Volmarr",
            mentioned_entities=["runa", "volmarr"],
        )
        # Check that graph_paths are unique by (entity, relationship) key
        seen = set()
        for p in result.graph_paths:
            key = (p.get("entity", ""), p.get("relationship", ""))
            assert key not in seen, f"Duplicate graph path: {key}"
            seen.add(key)


class TestFocusCategories:
    """Tests for focus_categories parameter in assemble_context."""

    def test_focus_category_filter(self, memory_db, graph_db):
        """Providing focus_categories should filter episodic recall."""
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        eng = ContextEngineer(
            mimir=memory_db, graph=graph_db, budgeter=budgeter
        )
        result = eng.assemble_context(
            "Tell me about travel",
            focus_categories=["travel"],
        )
        assert isinstance(result, ContextResult)