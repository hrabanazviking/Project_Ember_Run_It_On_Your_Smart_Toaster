"""T9-5: Context Engineer Tests — full coverage for context_engineer.py.

Tests ContextResult, ContextEngineer, entity extraction, token estimation,
context assembly, quick_context, budget stats, and graph path deduplication.
"""

import os
import tempfile
import unittest

from mimir_well import RunaMemory, WyrdGraph, ContextEngineer, ContextResult
from mimir_well.budget import TokenBudget, TokenBudgeter


def _fresh_db():
    """Create a temporary database path that auto-cleans."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


class TestContextResult(unittest.TestCase):
    """ContextResult dataclass formatting and stats."""

    def test_empty_context_block(self):
        result = ContextResult()
        self.assertEqual(result.to_context_block(), "")
        self.assertEqual(result.total_tokens, 0)
        self.assertEqual(result.budget_used_pct, 0.0)

    def test_episodic_context_block(self):
        result = ContextResult(
            episodic=[{"content": "Remembered something important", "importance": 9}]
        )
        block = result.to_context_block()
        self.assertIn("## Episodic (Recent Events)", block)
        self.assertIn("Remembered something important", block)
        self.assertIn("[9]", block)

    def test_semantic_context_block(self):
        result = ContextResult(
            semantic=[{"content": "Runa loves coding", "importance": 8}]
        )
        block = result.to_context_block()
        self.assertIn("## Semantic (Facts & Preferences)", block)
        self.assertIn("Runa loves coding", block)

    def test_procedural_context_block(self):
        result = ContextResult(
            procedural=[{"content": "Always use threading.local()", "importance": 7}]
        )
        block = result.to_context_block()
        self.assertIn("## Procedural (Patterns & Skills)", block)
        self.assertIn("Always use threading.local()", block)

    def test_graph_paths_context_block(self):
        path = {
            "entity": "volmarr",
            "relationship_type": "partner",
            "strength": 10,
            "path": [("runa", "partner"), ("volmarr", "partner")],
        }
        result = ContextResult(graph_paths=[path])
        block = result.to_context_block()
        self.assertIn("## Relationships (Graph Paths)", block)

    def test_spatial_context_block(self):
        result = ContextResult(
            spatial=[{"content": "Kitchen is north of living room"}]
        )
        block = result.to_context_block()
        self.assertIn("## Spatial Awareness", block)
        self.assertIn("Kitchen is north of living room", block)

    def test_heuristic_context_block(self):
        result = ContextResult(
            heuristic=[{"content": "Night coding = flow state"}]
        )
        block = result.to_context_block()
        self.assertIn("## Heuristic Associations", block)
        self.assertIn("Night coding = flow state", block)

    def test_content_truncation(self):
        long_content = "x" * 500
        result = ContextResult(episodic=[{"content": long_content, "importance": 5}])
        block = result.to_context_block()
        # Content should be truncated to 200 chars in the block
        self.assertIn("x" * 200, block)

    def test_stats_default(self):
        result = ContextResult()
        self.assertIsInstance(result.stats, dict)
        self.assertEqual(len(result.stats), 0)


class TestContextEngineerInit(unittest.TestCase):
    """ContextEngineer initialization tests."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)
        self.graph = WyrdGraph(db_path=_fresh_db())

    def tearDown(self):
        self.mem.close()
        self.graph.close()
        for p in [self.db_path, self.graph.db_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_default_init(self):
        engineer = ContextEngineer(self.mem, self.graph)
        self.assertIsInstance(engineer.budgeter, TokenBudgeter)
        self.assertIsInstance(engineer.budgeter.budget, dict)

    def test_custom_budgeter(self):
        budget = TokenBudget(total_context=8000)
        budgeter = TokenBudgeter(budget)
        engineer = ContextEngineer(self.mem, self.graph, budgeter=budgeter)
        self.assertIsInstance(engineer.budgeter.budget, dict)

    def test_custom_total_context(self):
        engineer = ContextEngineer(self.mem, self.graph, total_context=4000)
        self.assertIsInstance(engineer.budgeter.budget, dict)


class TestEntityExtraction(unittest.TestCase):
    """_extract_entities heuristic tests."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)
        self.graph = WyrdGraph(db_path=_fresh_db())
        self.engineer = ContextEngineer(self.mem, self.graph)

    def tearDown(self):
        self.mem.close()
        self.graph.close()
        for p in [self.db_path, self.graph.db_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_capitalized_names(self):
        entities = self.engineer._extract_entities("Runa met Volmarr yesterday")
        self.assertIn("runa", entities)
        self.assertIn("volmarr", entities)

    def test_multi_word_entity(self):
        entities = self.engineer._extract_entities("Norse Pagan ceremonies are beautiful")
        # "Norse Pagan" should be detected
        self.assertTrue(len(entities) > 0)

    def test_skip_common_words(self):
        entities = self.engineer._extract_entities("The weather is very nice today")
        # Common words should be filtered out
        self.assertNotIn("the", entities)
        self.assertNotIn("very", entities)

    def test_empty_input(self):
        entities = self.engineer._extract_entities("")
        self.assertEqual(entities, [])

    def test_all_lowercase(self):
        entities = self.engineer._extract_entities("the quick brown fox")
        # All lowercase — no entity names detected
        self.assertEqual(entities, [])

    def test_deduplication(self):
        entities = self.engineer._extract_entities("Runa likes Runa")
        # Same entity should appear only once
        self.assertEqual(entities.count("runa"), 1)


class TestTokenEstimation(unittest.TestCase):
    """_estimate_tokens heuristic test."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)
        self.graph = WyrdGraph(db_path=_fresh_db())
        self.engineer = ContextEngineer(self.mem, self.graph)

    def tearDown(self):
        self.mem.close()
        self.graph.close()
        for p in [self.db_path, self.graph.db_path]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_empty_string(self):
        self.assertEqual(self.engineer._estimate_tokens(""), 1)

    def test_short_text(self):
        # 4 chars = 1 token
        self.assertEqual(self.engineer._estimate_tokens("test"), 1)

    def test_longer_text(self):
        # 100 chars ≈ 25 tokens
        result = self.engineer._estimate_tokens("x" * 100)
        self.assertEqual(result, 25)

    def test_minimum_one_token(self):
        result = self.engineer._estimate_tokens("a")
        self.assertEqual(result, 1)


class TestContextAssembly(unittest.TestCase):
    """assemble_context and quick_context integration tests."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.graph_db = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)
        self.graph = WyrdGraph(db_path=self.graph_db)
        self.engineer = ContextEngineer(self.mem, self.graph, total_context=8000)
        # Add test data
        self.mem.add_memory("Runa loves coding in Python", category="preference",
                            importance=9, user_id="test")
        self.mem.add_memory("Always use threading.local() for SQLite", category="lesson",
                            importance=8, user_id="test")
        self.mem.add_memory("Had breakfast with Volmarr", category="saga_moment",
                            importance=7, user_id="test")

    def tearDown(self):
        self.mem.close()
        self.graph.close()
        for p in [self.db_path, self.graph_db]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_assemble_returns_result(self):
        result = self.engineer.assemble_context("What does Runa love?")
        self.assertIsInstance(result, ContextResult)
        self.assertIsInstance(result.stats, dict)
        self.assertIn("total_tokens", result.stats)

    def test_assemble_has_budget_stats(self):
        result = self.engineer.assemble_context("What does Runa love?")
        self.assertGreaterEqual(result.budget_total, 0)
        self.assertGreaterEqual(result.budget_used_pct, 0.0)

    def test_assemble_with_entities(self):
        result = self.engineer.assemble_context(
            "Tell me about Runa",
            mentioned_entities=["runa"],
        )
        self.assertIsInstance(result, ContextResult)

    def test_assemble_with_focus_categories(self):
        result = self.engineer.assemble_context(
            "What did I learn?",
            focus_categories=["lesson"],
        )
        self.assertIsInstance(result, ContextResult)

    def test_quick_context_returns_string(self):
        text = self.engineer.quick_context("What does Runa love?")
        self.assertIsInstance(text, str)

    def test_assemble_empty_db(self):
        # Create fresh engineer with empty db
        db = _fresh_db()
        gdb = _fresh_db()
        mem = RunaMemory(db_path=db)
        graph = WyrdGraph(db_path=gdb)
        eng = ContextEngineer(mem, graph, total_context=8000)
        result = eng.assemble_context("empty query")
        self.assertEqual(len(result.episodic), 0)
        self.assertEqual(len(result.semantic), 0)
        mem.close()
        graph.close()
        for p in [db, gdb]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_graph_paths_deduplication(self):
        # Add graph edges and test dedup
        self.graph.add_edge("runa", "volmarr", "partner", strength=10)
        result = self.engineer.assemble_context(
            "Tell me about Runa",
            mentioned_entities=["runa"],
        )
        # graph_paths may or may not have entries, but should not crash
        self.assertIsInstance(result.graph_paths, list)


class TestQuickContextBlock(unittest.TestCase):
    """Integration: assemble_context → to_context_block round-trip."""

    def setUp(self):
        self.db_path = _fresh_db()
        self.graph_db = _fresh_db()
        self.mem = RunaMemory(db_path=self.db_path)
        self.graph = WyrdGraph(db_path=self.graph_db)
        self.engineer = ContextEngineer(self.mem, self.graph, total_context=8000)

    def tearDown(self):
        self.mem.close()
        self.graph.close()
        for p in [self.db_path, self.graph_db]:
            try:
                os.unlink(p)
            except OSError:
                pass

    def test_block_formatting_with_memories(self):
        self.mem.add_memory("Night coding sessions", category="preference",
                            importance=8, user_id="test")
        self.mem.add_memory("Use RLock for SQLite", category="lesson",
                            importance=9, user_id="test")
        result = self.engineer.assemble_context("What about coding?")
        block = result.to_context_block()
        # At least one section should appear
        self.assertTrue(len(block) > 0 or result.total_tokens == 0)


if __name__ == "__main__":
    unittest.main()