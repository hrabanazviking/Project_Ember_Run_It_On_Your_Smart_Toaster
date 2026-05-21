"""Tests for Ebbinghaus decay, reinforcement, and consolidation."""

import time
import pytest

from mimir_well.core import RunaMemory
from mimir_well.decay import (
    compute_ebbinghaus_decay,
    compute_reinforcement_boost,
    compute_confidence_for_promotion,
    should_decay,
    should_promote,
)


class TestEbbinghausDecay:
    """Test the Ebbinghaus forgetting curve math."""

    def test_no_decay_for_recently_accessed(self):
        """Memories accessed 0 days ago should not decay."""
        result = compute_ebbinghaus_decay(7.0, 0.0, half_life_days=30.0)
        assert result == 7.0

    def test_decay_with_time(self):
        """Memories should decay over time."""
        # After 30 days (1 half-life), importance should be roughly halved
        result = compute_ebbinghaus_decay(7.0, 30.0, half_life_days=30.0)
        assert result < 7.0
        assert result > 3.0  # Should be around 3.5

    def test_decay_never_goes_below_one(self):
        """Even heavily decayed memories should not go below importance 1."""
        result = compute_ebbinghaus_decay(7.0, 365.0, half_life_days=5.0)
        assert result >= 1.0

    def test_decay_never_exceeds_ten(self):
        """Decay should never push importance above 10."""
        result = compute_ebbinghaus_decay(7.0, 0.5, half_life_days=30.0)
        assert result <= 10.0

    def test_longer_half_life_slower_decay(self):
        """Longer half-life should result in slower decay."""
        short = compute_ebbinghaus_decay(7.0, 30.0, half_life_days=15.0)
        long = compute_ebbinghaus_decay(7.0, 30.0, half_life_days=60.0)
        assert long > short  # Longer half-life = less decay


class TestReinforcementBoost:
    """Test reinforcement computation."""

    def test_boost_from_accesses(self):
        """More accesses should mean more reinforcement."""
        result = compute_reinforcement_boost(5.0, 3, boost=0.5)
        assert result == 6.5  # 5.0 + 0.5 * 3

    def test_boost_capped_at_ten(self):
        """Reinforcement should not push above 10."""
        result = compute_reinforcement_boost(9.0, 5, boost=0.5)
        assert result == 10.0


class TestConfidenceForPromotion:
    """Test knowledge promotion confidence calculation."""

    def test_confidence_from_importance(self):
        """Higher importance = higher confidence."""
        low = compute_confidence_for_promotion(5, 0.0)
        high = compute_confidence_for_promotion(9, 0.0)
        assert high > low

    def test_confidence_cap(self):
        """Confidence should never exceed 0.95."""
        result = compute_confidence_for_promotion(10, 1.0)
        assert result <= 0.95


class TestShouldDecay:
    """Test decay decision logic."""

    def test_recently_accessed_not_decayed(self):
        """Memories accessed within the threshold should not decay."""
        assert should_decay(5, 5, threshold_days=30) is False

    def test_old_memories_decayed(self):
        """Memories not accessed beyond the threshold should decay."""
        assert should_decay(45, 5, threshold_days=30) is True

    def test_very_important_memories_decay_slower(self):
        """Importance 9+ memories need triple the threshold to decay."""
        assert should_decay(31, 9, threshold_days=30) is False  # Not old enough
        assert should_decay(91, 9, threshold_days=30) is True   # Triple threshold


class TestShouldPromote:
    """Test promotion decision logic."""

    def test_low_importance_not_promoted(self):
        """Low-importance memories should not be promoted."""
        assert should_promote(3, 5) is False

    def test_high_importance_frequent_access_promoted(self):
        """High importance + frequent access = promotion."""
        assert should_promote(8, 3) is True

    def test_very_high_importance_auto_promoted(self):
        """Importance 9+ auto-qualifies regardless of access."""
        assert should_promote(9, 0) is True


class TestDecayIntegration:
    """Test the decay method on the actual RunaMemory class."""

    def test_decay_applies(self, tmp_path):
        """decay() should return decay/prune/reinforce counts."""
        db_path = tmp_path / "decay_test.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Old memory", importance=6)

        result = db.decay(half_life_days=30.0)
        assert "decayed" in result
        assert "pruned" in result
        assert "reinforced" in result
        db.close()

    def test_consolidation(self, tmp_path):
        """consolidate() should return decay/promote/prune counts."""
        db_path = tmp_path / "consolidation_test.db"
        db = RunaMemory(str(db_path))
        db.add_memory("Test memory", importance=7)

        result = db.consolidate()
        assert "decayed" in result
        assert "promoted" in result
        assert "pruned" in result
        db.close()

    def test_promote_to_knowledge(self, tmp_path):
        """promote_to_knowledge() should create knowledge from memories."""
        db_path = tmp_path / "promote_test.db"
        db = RunaMemory(str(db_path))

        # Add high-importance memory
        db.add_memory("Important fact about Yggdrasil", category="norse_mythology", importance=9)

        result = db.promote_to_knowledge(min_importance=8)
        assert result["promoted"] >= 1

        # Verify knowledge was created
        knowledge = db.search_knowledge("norse_mythology", "Yggdrasil")
        assert len(knowledge) >= 1
        db.close()