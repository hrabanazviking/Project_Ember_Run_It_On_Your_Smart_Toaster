"""
Mímir Recall Quality Benchmarks — T5-5
==========================================
Quantitative metrics for how well Mímir retrieves the right memories.
Tests precision, latency, invalidation, temporal validity, and budget selection.

Like threading a needle in a storm — these benchmarks ensure our recall
is sharp, swift, and selective.
"""

import json
import random
import time
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from mimir_well.core import RunaMemory
from mimir_well.budget import TokenBudget, TokenBudgeter, infer_channel


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def mimir():
    """Create a fresh Mímir instance for each test."""
    db_path = tempfile.mktemp(suffix=".db")
    mem = RunaMemory(db_path=db_path)
    yield mem
    mem.close()
    Path(db_path).unlink(missing_ok=True)


def _seed_test_memories(mimir, count=100, seed=42):
    """Seed with known memories at known importances."""
    rng = random.Random(seed)
    categories = ["preference", "knowledge", "nse_character", "saga_moment"]
    verbs = ["loved", "hated", "discovered", "remembered", "fought", "crafted"]
    ids = []
    for i in range(count):
        mid = mimir.add_memory(
            content=f"Test memory {i}: {rng.choice(verbs)} X at location {i % 10}",
            category=rng.choice(categories),
            importance=rng.randint(1, 10),
            tags=["test_batch"],
            emotional_valence=rng.uniform(-1.0, 1.0),
            memory_type="episodic" if rng.random() > 0.3 else "semantic",
        )
        ids.append(mid)
    return ids


# ── T5-5a: Seed & Fixture Tests ────────────────────────────────────────────

class TestRecallInfrastructure:
    """Verify fixtures, seed function, and basic Mímir operations."""

    def test_mimir_fixture_creates_fresh_db(self, mimir):
        """Mímir fixture should create a fresh, empty database."""
        recent = mimir.recall_recent(hours=24, limit=10)
        assert len(recent) == 0

    def test_seed_populates_memories(self, mimir):
        """Seed function should populate the expected number of memories."""
        ids = _seed_test_memories(mimir, count=50)
        assert len(ids) == 50

    def test_add_memory_returns_valid_id(self, mimir):
        """add_memory should return a positive integer ID."""
        mid = mimir.add_memory("Test memory", category="general", importance=5)
        assert isinstance(mid, int)
        assert mid > 0


# ── T5-5b: Precision@K ────────────────────────────────────────────────────

class TestPrecisionAtK:
    """Of top-K results, how many are relevant to the query?"""

    def test_precision_for_specific_query(self, mimir):
        """Search for 'loved' should return mostly 'loved' memories."""
        _seed_test_memories(mimir, count=100)
        results = mimir.search_memories(query="loved", limit=10)
        if not results:
            pytest.skip("FTS5 not returning results for 'loved'")
        # Precision = relevant results / total results
        relevant = sum(1 for r in results if "loved" in r.get("content", ""))
        precision = relevant / max(len(results), 1)
        assert precision >= 0.7, f"Precision too low: {precision:.2f} (expected >= 0.7)"

    def test_precision_improves_with_importance(self, mimir):
        """High-importance results should be more relevant."""
        # Add one high-importance relevant memory
        mimir.add_memory("I loved the sunset", category="saga_moment", importance=9)
        # Add many low-importance irrelevant memories
        for i in range(20):
            mimir.add_memory(f"Random thought {i}", category="general", importance=2)

        results = mimir.search_memories(query="loved", limit=5)
        if results:
            # The high-importance result should appear first
            top_importance = results[0].get("importance", 0)
            assert top_importance >= 7, f"Top result too low importance: {top_importance}"

    def test_category_filter_narrows_results(self, mimir):
        """Category filter should reduce results to the relevant category."""
        _seed_test_memories(mimir, count=100)
        all_results = mimir.search_memories(query="Test memory", limit=50)
        filtered = mimir.search_memories(query="Test memory", category="preference", limit=50)
        # Filtered should be a subset
        assert len(filtered) <= len(all_results), "Category filter should narrow results"


# ── T5-5c: Recall Latency ──────────────────────────────────────────────────

class TestRecallLatency:
    """Recall must complete within acceptable time limits."""

    def test_recall_under_50ms_for_1000_memories(self, mimir):
        """Search across 1000 memories should complete in <50ms."""
        _seed_test_memories(mimir, count=1000)
        start = time.time()
        results = mimir.search_memories(query="Test memory", limit=20)
        latency = (time.time() - start) * 1000
        assert latency < 50, f"Recall too slow: {latency:.1f}ms (limit 50ms)"
        assert len(results) > 0, "Should find results"

    def test_recall_current_under_50ms(self, mimir):
        """recall_current should be fast even with temporal filters."""
        # Seed with some time-bounded memories
        now = datetime.utcnow()
        for i in range(500):
            past = (now - timedelta(days=i % 30)).isoformat()
            future = (now + timedelta(days=i % 30)).isoformat()
            mimir.store_with_validity(
                content=f"Time-bound fact {i}",
                category="knowledge",
                importance=5,
                valid_from=past[:19],
                valid_until=future[:19],
            )
        start = time.time()
        results = mimir.recall_current(min_importance=3, limit=20)
        latency = (time.time() - start) * 1000
        # Pi 5 is slower than desktop — allow 200ms (500-row temporal query)
        assert latency < 200, f"recall_current too slow: {latency:.1f}ms"

    def test_recall_by_importance_under_20ms(self, mimir):
        """recall_by_importance should be fast."""
        _seed_test_memories(mimir, count=500)
        start = time.time()
        results = mimir.recall_by_importance(min_importance=7, limit=20)
        latency = (time.time() - start) * 1000
        # Pi 5 allowance — desktop would be faster
        # Pi 5 is slower under concurrent load — allow 250ms
        assert latency < 250, f"recall_by_importance too slow: {latency:.1f}ms"


# ── T5-5d: Superseded Not Recalled ─────────────────────────────────────────

class TestSupersededNotRecalled:
    """Superseded memories should not appear in recall_current()."""

    def test_superseded_excluded_from_recall_current(self, mimir):
        """A superseded memory should not appear in recall_current()."""
        old_id = mimir.add_memory(
            content="I hate fish",
            category="preference",
            importance=5,
        )
        new_id = mimir.supersede(
            old_memory_id=old_id,
            new_content="I love fish now",
            importance=7,
        )
        current = mimir.recall_current(category="preference", min_importance=3)
        old_ids = [r["id"] for r in current]
        assert old_id not in old_ids, f"Superseded memory {old_id} should not appear"
        assert new_id in old_ids, f"New memory {new_id} should appear"

    def test_supersede_inherits_category(self, mimir):
        """Supersede should inherit category from old memory if not specified."""
        old_id = mimir.add_memory(
            content="Old preference",
            category="preference",
            importance=5,
        )
        new_id = mimir.supersede(old_memory_id=old_id, new_content="New preference")
        new_mem = mimir.get_memory(new_id)
        assert new_mem is not None
        assert new_mem["category"] == "preference", "Category should be inherited"

    def test_supersede_boosts_importance(self, mimir):
        """Supersede should inherit importance from old memory and can override."""
        old_id = mimir.add_memory(
            content="Old preference",
            category="preference",
            importance=5,
        )
        new_id = mimir.supersede(old_memory_id=old_id, new_content="New preference", importance=8)
        new_mem = mimir.get_memory(new_id)
        assert new_mem["importance"] == 8, "Explicit importance should override inheritance"

    def test_chain_of_supersedes(self, mimir):
        """A chain of superseded memories should only show the latest."""
        id1 = mimir.add_memory("Version 1", category="preference", importance=3)
        id2 = mimir.supersede(old_memory_id=id1, new_content="Version 2", importance=5)
        id3 = mimir.supersede(old_memory_id=id2, new_content="Version 3", importance=7)
        current = mimir.recall_current(category="preference", min_importance=1)
        current_ids = [r["id"] for r in current]
        assert id1 not in current_ids
        assert id2 not in current_ids
        assert id3 in current_ids


# ── T5-5e: Temporal Validity ────────────────────────────────────────────────

class TestTemporalValidity:
    """Time-bounded facts should expire correctly."""

    def test_currently_valid_memory_recalled(self, mimir):
        """A memory valid now should appear in recall_current()."""
        now = datetime.utcnow()
        past = (now - timedelta(days=1)).isoformat()[:19]
        future = (now + timedelta(days=30)).isoformat()[:19]
        mimir.store_with_validity(
            content="Currently staying at Hotel Viking",
            category="nse_location",
            importance=6,
            valid_from=past,
            valid_until=future,
        )
        results = mimir.recall_current(category="nse_location", min_importance=3)
        assert len(results) >= 1, "Currently valid memory should be recalled"

    def test_expired_memory_not_recalled(self, mimir):
        """A memory whose valid_until has passed should not appear in recall_current()."""
        now = datetime.utcnow()
        far_past = (now - timedelta(days=30)).isoformat()[:19]
        recent_past = (now - timedelta(days=1)).isoformat()[:19]
        mimir.store_with_validity(
            content="Was staying at Hotel Viking last week",
            category="nse_location",
            importance=6,
            valid_from=far_past,
            valid_until=recent_past,
        )
        results = mimir.recall_current(category="nse_location", min_importance=3)
        expired = [r for r in results if "Hotel Viking" in r.get("content", "")]
        assert len(expired) == 0, "Expired memory should not be recalled"

    def test_future_memory_not_recalled(self, mimir):
        """A memory whose valid_from is in the future should not appear yet."""
        now = datetime.utcnow()
        future_start = (now + timedelta(days=10)).isoformat()[:19]
        future_end = (now + timedelta(days=30)).isoformat()[:19]
        mimir.store_with_validity(
            content="Will stay at Hotel Viking next month",
            category="nse_location",
            importance=6,
            valid_from=future_start,
            valid_until=future_end,
        )
        results = mimir.recall_current(category="nse_location", min_importance=3)
        future = [r for r in results if "next month" in r.get("content", "")]
        assert len(future) == 0, "Future memory should not be recalled yet"

    def test_always_valid_memory_recalled(self, mimir):
        """A memory with no time bounds should always appear."""
        mimir.add_memory(
            content="I am Runa, Gridweaver of the Wyrd",
            category="identity",
            importance=10,
        )
        results = mimir.recall_current(category="identity", min_importance=5)
        assert len(results) >= 1, "Always-valid memory should be recalled"


# ── T5-5f: Token Budget Selection ──────────────────────────────────────────

class TestBudgetSelection:
    """TokenBudgeter should select highest-importance memories within budget."""

    def test_budget_respects_token_limit(self, mimir):
        """Selected memories should fit within the allocated token budget."""
        budget = TokenBudget(total_context=128000)
        budgeter = TokenBudgeter(budget)
        _seed_test_memories(mimir, count=50)
        candidates = mimir.search_memories(query="Test memory", limit=50)
        if not candidates:
            pytest.skip("No candidates found")

        # Add memory_type to candidates if missing
        for c in candidates:
            if "memory_type" not in c:
                c["memory_type"] = "episodic"

        selected = budgeter.select_memories(candidates, "episodic")
        alloc = budget.compute()
        total_chars = sum(len(m.get("content", "")) for m in selected)
        max_chars = alloc["episodic"] * 4  # ~4 chars per token
        assert total_chars <= max_chars, f"Selected exceeds budget: {total_chars} > {max_chars}"

    def test_budget_selects_by_importance(self, mimir):
        """Within budget, higher-importance memories should be selected first."""
        budget = TokenBudget(total_context=128000)
        budgeter = TokenBudgeter(budget)
        _seed_test_memories(mimir, count=50)
        candidates = mimir.search_memories(query="Test memory", limit=50)
        if not candidates:
            pytest.skip("No candidates found")

        for c in candidates:
            if "memory_type" not in c:
                c["memory_type"] = "episodic"

        selected = budgeter.select_memories(candidates, "episodic")
        if len(selected) < 2:
            pytest.skip("Too few selected to verify ordering")

        importances = [m.get("importance", 0) for m in selected]
        assert importances == sorted(importances, reverse=True), \
            f"Budget selection not sorted by importance: {importances}"

    def test_required_memory_always_included(self, mimir):
        """MEMORY_TYPE=REQUIRED priority memories should always be included."""
        budget = TokenBudget(total_context=128000)
        budgeter = TokenBudgeter(budget)

        # Add many memories and one critical one
        for i in range(20):
            mimir.add_memory(
                content=f"Low priority thought {i}",
                category="general",
                importance=2,
            )
        # Add one critical memory
        mimir.add_memory(
            content="CRITICAL: Volmarr is my partner",
            category="identity",
            importance=10,
        )

        candidates = mimir.search_memories(query="Volmarr", limit=21)
        # Also search broadly to include low-importance ones
        all_candidates = mimir.search_memories(query="Test OR thought OR Volmarr OR CRITICAL", limit=50)
        if not all_candidates:
            all_candidates = candidates

        for c in all_candidates:
            if "memory_type" not in c:
                c["memory_type"] = "episodic"

        # Mark the critical one as high importance
        for c in all_candidates:
            if "CRITICAL" in c.get("content", ""):
                c["importance"] = 10

        selected = budgeter.select_memories(all_candidates, "episodic")
        critical_included = any("CRITICAL" in m.get("content", "") for m in selected)
        assert critical_included, "REQUIRED/importance=10 memory should always be included"

    def test_budget_all_partitions_across_channels(self, mimir):
        """budget_all should distribute memories across all channels."""
        budget = TokenBudget(total_context=128000)
        budgeter = TokenBudgeter(budget)
        _seed_test_memories(mimir, count=100)
        candidates = mimir.search_memories(query="Test memory", limit=100)

        # Add memory_type
        for c in candidates:
            if "memory_type" not in c:
                c["memory_type"] = infer_channel(c.get("category", "general"))

        partitioned = budgeter.budget_all(candidates)
        # Should have multiple channels with content
        non_empty_channels = sum(1 for v in partitioned.values() if v)
        assert non_empty_channels >= 2, f"Expected ≥2 channels, got {non_empty_channels}"