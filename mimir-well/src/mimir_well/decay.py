"""
Mímir's Well — Ebbinghaus Decay Logic
========================================
Implements the forgetting curve, reinforcement scheduling, and
knowledge promotion algorithms.
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger("mimir_well.decay")


def compute_ebbinghaus_decay(importance: float, days_since_access: float,
                              half_life_days: float = 30.0) -> float:
    """Apply Ebbinghaus forgetting curve to compute decayed importance.

    The formula follows the exponential decay model:
        R(t) = importance * (0.5)^(t / half_life)

    Args:
        importance: Current importance value (1-10)
        days_since_access: Days since the memory was last accessed
        half_life_days: Days for importance to halve (default 30)

    Returns:
        New importance value after decay
    """
    if days_since_access <= 0:
        return importance
    decay_factor = 0.5 ** (1.0 / half_life_days)
    return max(1.0, min(10.0, importance * (decay_factor ** days_since_access)))


def compute_reinforcement_boost(current_importance: float, accesses_in_window: int,
                                  boost: float = 0.5) -> float:
    """Calculate importance boost from recent accesses.

    Memories accessed frequently gain importance — the digital equivalent
    of spaced repetition strengthening recall.

    Args:
        current_importance: Current importance value
        accesses_in_window: Number of accesses in the lookback window
        boost: Importance boost per access (default 0.5)

    Returns:
        New importance value after reinforcement
    """
    new_importance = current_importance + (boost * accesses_in_window)
    return min(10.0, new_importance)


def compute_confidence_for_promotion(importance: float, valence: float = 0.0) -> float:
    """Calculate confidence score for knowledge promotion.

    When a memory is promoted to knowledge, its importance and valence
    determine the confidence level of the resulting knowledge entry.

    Args:
        importance: Memory importance (1-10)
        valence: Emotional valence of the memory (-1.0 to 1.0)

    Returns:
        Confidence score (0.0 to 1.0)
    """
    return min(0.95, importance / 10.0 + valence * 0.05)


def should_decay(days_since_access: int, importance: int, threshold_days: int = 30) -> bool:
    """Determine if a memory should be subject to Ebbinghaus decay.

    Memories with high recent access are exempt from decay.

    Args:
        days_since_access: Days since last access
        importance: Current importance (high-importance memories decay slower)
        threshold_days: Days before decay kicks in (default 30)

    Returns:
        True if the memory should be decayed
    """
    if days_since_access < threshold_days:
        return False
    if importance >= 9:
        # Core memories decay much more slowly
        return days_since_access > (threshold_days * 3)
    return True


def should_promote(importance: int, access_count: int,
                    access_window_days: int = 7, min_importance: int = 8) -> bool:
    """Determine if a memory should be promoted to knowledge.

    A memory becomes knowledge when it has sustained high importance
    and frequent access — crystallizing experience into wisdom.

    Args:
        importance: Current importance (1-10)
        access_count: Number of accesses in the window
        access_window_days: Lookback window (default 7 days)
        min_importance: Minimum importance threshold (default 8)

    Returns:
        True if the memory qualifies for promotion
    """
    if importance < min_importance:
        return False
    if access_count >= 3:
        return True
    if importance >= 9:
        return True  # Near-permanent memories auto-qualify
    return False