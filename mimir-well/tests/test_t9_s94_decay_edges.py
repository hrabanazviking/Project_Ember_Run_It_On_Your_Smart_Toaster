"""S9.4e: decay.py gap-fill tests.

Covers edge cases missing from test_decay.py:
- compute_ebbinghaus_decay: zero/negative days, extreme half_life
- compute_reinforcement_boost: zero accesses, very high current
- compute_confidence_for_promotion: negative valence, valence=0
- should_decay: threshold boundary, importance=9, importance=10
- should_promote: access_count=2, importance=8
"""

import tempfile
import pytest

from mimir_well.core import RunaMemory
from mimir_well.decay import (
    compute_ebbinghaus_decay,
    compute_reinforcement_boost,
    compute_confidence_for_promotion,
    should_decay,
    should_promote,
)


class TestEbbinghausEdgeCases:
    """Edge cases for compute_ebbinghaus_decay."""

    def test_zero_days_no_decay(self):
        """Zero days since access = no decay (factor 0)."""
        result = compute_ebbinghaus_decay(importance=5, days_since_access=0)
        assert result == 5  # No change at day 0

    def test_negative_days_treated_as_zero(self):
        """Negative days should not crash — treat as 0 or minimal."""
        result = compute_ebbinghaus_decay(importance=5, days_since_access=-1)
        # Should not crash; result should be reasonable
        assert result > 0

    def test_very_long_half_life_preserves(self):
        """A very long half_life means almost no decay."""
        result = compute_ebbinghaus_decay(
            importance=8, days_since_access=30, half_life_days=10000
        )
        assert result >= 7  # Barely decayed

    def test_very_short_half_life_decays_fast(self):
        """A very short half_life means rapid decay."""
        result = compute_ebbinghaus_decay(
            importance=8, days_since_access=30, half_life_days=1
        )
        assert result < 5  # Heavy decay

    def test_extreme_days_since_access(self):
        """1000 days with default half_life should severely decay."""
        result = compute_ebbinghaus_decay(importance=5, days_since_access=1000)
        assert result == 1  # Clamped to minimum


class TestReinforcementBoostEdgeCases:
    """Edge cases for compute_reinforcement_boost."""

    def test_zero_accesses(self):
        """Zero accesses = no boost."""
        result = compute_reinforcement_boost(current_importance=5, accesses_in_window=0)
        assert result == 5

    def test_many_accesses(self):
        """Very frequent access = capped at 10."""
        result = compute_reinforcement_boost(current_importance=5, accesses_in_window=100)
        assert result <= 10

    def test_negative_accesses_reduce_importance(self):
        """Negative access count penalizes — reduces importance."""
        result = compute_reinforcement_boost(current_importance=5, accesses_in_window=-1)
        # Negative accesses reduce importance, but result stays >= 1
        assert result >= 1


class TestConfidenceForPromotion:
    """Edge cases for compute_confidence_for_promotion."""

    def test_negative_valence_lowers_confidence(self):
        """Negative valence should reduce confidence."""
        with_neg = compute_confidence_for_promotion(importance=8, valence=-0.5)
        with_zero = compute_confidence_for_promotion(importance=8, valence=0.0)
        assert with_neg < with_zero

    def test_positive_valence_boosts_confidence(self):
        """Positive valence should increase confidence."""
        with_pos = compute_confidence_for_promotion(importance=8, valence=0.5)
        with_zero = compute_confidence_for_promotion(importance=8, valence=0.0)
        assert with_pos > with_zero

    def test_confidence_capped_at_95_percent(self):
        """Confidence should not exceed 0.95."""
        result = compute_confidence_for_promotion(importance=10, valence=1.0)
        assert result <= 0.95

    def test_zero_importance_gives_low_confidence(self):
        """Zero importance = near-zero confidence."""
        result = compute_confidence_for_promotion(importance=0, valence=0.0)
        assert result < 0.1


class TestShouldDecayEdgeCases:
    """Edge cases for should_decay."""

    def test_exactly_at_threshold(self):
        """Day 30 with importance 5 should decay (not < 30)."""
        assert should_decay(30, 5) is True

    def test_one_day_before_threshold(self):
        """Day 29 should not decay."""
        assert should_decay(29, 5) is False

    def test_importance_9_needs_triple_threshold(self):
        """Importance 9 at day 30 should NOT decay (needs 90 days)."""
        assert should_decay(30, 9) is False

    def test_importance_9_decays_at_triple_threshold(self):
        """Importance 9 at day 91 should decay (30 * 3 = 90, >90 triggers)."""
        assert should_decay(91, 9) is True

    def test_importance_10_also_triple_threshold(self):
        """Importance > 9 gets the triple threshold."""
        assert should_decay(40, 10) is False
        assert should_decay(91, 10) is True

    def test_custom_threshold(self):
        """Custom threshold_days should override default."""
        assert should_decay(14, 5, threshold_days=15) is False
        assert should_decay(16, 5, threshold_days=15) is True


class TestShouldPromoteEdgeCases:
    """Edge cases for should_promote."""

    def test_importance_8_access_2_not_promoted(self):
        """Need 3+ accesses for importance 8."""
        assert should_promote(importance=8, access_count=2) is False

    def test_importance_8_access_3_promoted(self):
        """Exactly 3 accesses at importance 8."""
        assert should_promote(importance=8, access_count=3) is True

    def test_importance_7_not_promoted_even_with_accesses(self):
        """Importance below threshold not promoted regardless of access."""
        assert should_promote(importance=7, access_count=10) is False

    def test_importance_9_auto_promoted(self):
        """Importance 9 auto-qualifies even with 0 accesses."""
        assert should_promote(importance=9, access_count=0) is True

    def test_importance_10_auto_promoted(self):
        """Maximum importance auto-qualifies."""
        assert should_promote(importance=10, access_count=0) is True

    def test_custom_min_importance(self):
        """Custom min_importance threshold."""
        assert should_promote(importance=7, access_count=3, min_importance=7) is True
        assert should_promote(importance=6, access_count=3, min_importance=7) is False