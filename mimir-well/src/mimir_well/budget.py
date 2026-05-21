"""
Mímir's Token Budget — Strategic Allocation of Context Window
================================================================

The Well must be curated. Wisdom without curation is hoarding.
TokenBudgeter selects which memories deserve the sacred resource
of context window space, ordered by importance and bounded by cost.

ᛗ í ᛗ í ᚱ — Not all memories deserve to speak at once.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────

# Approximate: 1 token ≈ 4 characters for English text.
# This is a conservative estimate; GPT-style models average ~3.6 chars/token.
CHARS_PER_TOKEN = 4

# Default context window sizes for known model families
DEFAULT_CONTEXT_WINDOWS = {
    "glm-5.1": 128000,
    "claude-sonnet-4": 200000,
    "claude-opus-4": 200000,
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000,
    "default": 128000,
}


class BudgetPriority(Enum):
    """Priority tiers for memory injection channels.

    ┌──────────┬──────────────────────────────────────────────────┐
    │ Priority │ Meaning                                         │
    ├──────────┼──────────────────────────────────────────────────┤
    │ REQUIRED │ System prompt, current user message — ALWAYS    │
    │ HIGH     │ Active entities, recent memories — almost always│
    │ MEDIUM   │ Related context, moderate-importance facts      │
    │ LOW      │ Deep history, tangential facts — only if surplus│
    └──────────┴──────────────────────────────────────────────────┘
    """
    REQUIRED = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class MemoryChannel(Enum):
    """Channels within the memory allocation.

    Each channel serves a distinct cognitive function:
    - EPISODIC: Recent conversational events — "what happened"
    - SEMANTIC: General facts, preferences, knowledge — "what is true"
    - PROCEDURAL: Learned patterns, skills — "how to do things"
    - SPATIAL: WYRD awareness, entity locations — "where things are"
    - HEURISTIC: Hebbian associations, emotional context — "what feels right"
    """
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    SPATIAL = "spatial"
    HEURISTIC = "heuristic"


# Category → memory channel mapping (derived from core.CATEGORY_TYPE_MAP)
# Single source of truth: core.py defines category→string, we map string→enum
_STRING_TO_CHANNEL = {
    "episodic": MemoryChannel.EPISODIC,
    "semantic": MemoryChannel.SEMANTIC,
    "procedural": MemoryChannel.PROCEDURAL,
    "implicit": MemoryChannel.HEURISTIC,
}


def infer_channel(category: str) -> MemoryChannel:
    """Map a Mímir category to a memory channel for budgeting.

    Uses core.CATEGORY_TYPE_MAP as the single source of truth for
    category→type mappings, then converts the string type to an enum.
    """
    from mimir_well.core import infer_memory_type
    mem_type = infer_memory_type(category)
    return _STRING_TO_CHANNEL.get(mem_type, MemoryChannel.EPISODIC)


# ── Token Budget Dataclass ────────────────────────────────────────────

@dataclass
class TokenBudget:
    """Strategic allocation of context window tokens across memory channels.

    The budget computes how many tokens each channel gets, ensuring the
    model always has room for system prompts, user messages, and response
    generation — with the remainder divided among memory sources.

    Example::

        budget = TokenBudget(total_context=128000)
        allocation = budget.compute()
        # allocation = {
        #   'episodic': 29400,
        #   'semantic': 41160,
        #   'procedural': 17640,
        #   'spatial': 11760,
        #   'heuristic': 17640,
        #   'total_memory': 117600
        # }
    """
    total_context: int = 128000
    system_prompt: int = 4000
    current_message: int = 2000
    response_reserve: int = 4000

    # Proportional splits within memory allocation
    # Must sum to 1.0
    episodic_ratio: float = 0.25
    semantic_ratio: float = 0.35
    procedural_ratio: float = 0.15
    spatial_ratio: float = 0.10
    heuristic_ratio: float = 0.15

    def compute(self) -> Dict[str, int]:
        """Compute token allocation per channel.

        Returns:
            Dict mapping channel names to token counts.
            Includes 'total_memory' for the total memory budget.
        """
        self.memory_allocation = (
            self.total_context
            - self.system_prompt
            - self.current_message
            - self.response_reserve
        )
        if self.memory_allocation < 0:
            logger.warning(
                "Token budget OVERSPENT: fixed costs (%d) exceed context (%d). "
                "Memory allocation set to 0.",
                self.system_prompt + self.current_message + self.response_reserve,
                self.total_context,
            )
            self.memory_allocation = 0

        return {
            "episodic": int(self.memory_allocation * self.episodic_ratio),
            "semantic": int(self.memory_allocation * self.semantic_ratio),
            "procedural": int(self.memory_allocation * self.procedural_ratio),
            "spatial": int(self.memory_allocation * self.spatial_ratio),
            "heuristic": int(self.memory_allocation * self.heuristic_ratio),
            "total_memory": self.memory_allocation,
        }

    @classmethod
    def for_model(cls, model_name: str) -> "TokenBudget":
        """Create a budget sized for a specific model's context window."""
        # Normalize model name for lookup
        key = model_name.lower().strip()
        total = DEFAULT_CONTEXT_WINDOWS.get("default", 128000)
        for pattern, size in DEFAULT_CONTEXT_WINDOWS.items():
            if pattern in key:
                total = size
                break
        return cls(total_context=total)


# ── Per-Type Selection Strategies (T5-3) ───────────────────────────────

def _episodic_strategy(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Episodic: prioritize recent + high emotional_valence (stories, moments)."""
    return sorted(
        candidates,
        key=lambda m: (
            m.get("importance", 5),
            abs(m.get("emotional_valence", 0.0)),
            m.get("access_count", 0),
        ),
        reverse=True,
    )


def _semantic_strategy(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Semantic: prioritize high importance + frequently accessed (facts, preferences)."""
    return sorted(
        candidates,
        key=lambda m: (
            m.get("importance", 5),
            m.get("access_count", 0),
        ),
        reverse=True,
    )


def _procedural_strategy(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Procedural: always include if relevant — sort by importance then recency."""
    return sorted(
        candidates,
        key=lambda m: (
            m.get("importance", 5),
            m.get("access_count", 0),
        ),
        reverse=True,
    )


def _implicit_strategy(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Implicit: behavioral nudges — sort by importance, inject subtly."""
    return sorted(
        candidates,
        key=lambda m: m.get("importance", 5),
        reverse=True,
    )


def _default_strategy(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fallback: sort by importance then access_count."""
    return sorted(
        candidates,
        key=lambda m: (
            m.get("importance", 5),
            m.get("access_count", 0),
        ),
        reverse=True,
    )


_TYPE_STRATEGIES = {
    "episodic": _episodic_strategy,
    "semantic": _semantic_strategy,
    "procedural": _procedural_strategy,
    "spatial": _default_strategy,
    "heuristic": _implicit_strategy,
}


# ── Token Budgeter ────────────────────────────────────────────────────

class TokenBudgeter:
    """Selects which memories to inject, bounded by token budget.

    The Budgeter sorts candidates by importance (primary) and access
    frequency (secondary), then greedily fills each channel until the
    budget is exhausted. No channel overflows — the Well respects limits.

    Usage::

        budget = TokenBudget(total_context=128000)
        budgeter = TokenBudgeter(budget)

        # From Mímir recall results
        candidates = mimir.search_memories(query="Norse", limit=50)

        # Select memories for the episodic channel
        selected = budgeter.select_memories(candidates, channel="episodic")

        # Or budget all channels at once
        allocations = budgeter.budget_all(candidates)
        # allocations = {
        #   "episodic": [...],  # top episodic memories within budget
        #   "semantic": [...],  # top semantic memories within budget
        #   ...
        # }
    """

    def __init__(self, budget: TokenBudget):
        self.budget = budget.compute()

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for a string (conservative: chars/3.5)."""
        return max(1, len(text) // 3)

    def select_memories(
        self,
        candidates: List[Dict[str, Any]],
        channel: str = "episodic",
        priority_order: Optional[List[BudgetPriority]] = None,
    ) -> List[Dict[str, Any]]:
        """Select memories to fill a channel's token budget.

        Memories are sorted by importance (desc) then access_count (desc),
        then greedily added until the channel's budget would be exceeded.

        Args:
            candidates: List of memory dicts with at least 'content',
                'importance', and optionally 'access_count' keys.
            channel: One of 'episodic', 'semantic', 'procedural',
                'spatial', 'heuristic'.
            priority_order: If given, memories with these priorities are
                included first regardless of channel budget. Defaults to
                [REQUIRED, HIGH].

        Returns:
            List of selected memory dicts that fit within budget.
        """
        budget_tokens = self.budget.get(channel, 0)
        if budget_tokens <= 0:
            logger.debug("Channel %s has 0 budget — skipping.", channel)
            return []

        max_chars = budget_tokens * CHARS_PER_TOKEN

        # Sort by importance (desc), then access_count (desc for recency)
        sorted_candidates = sorted(
            candidates,
            key=lambda m: (
                m.get("importance", 5),
                m.get("access_count", 0),
            ),
            reverse=True,
        )

        selected: List[Dict[str, Any]] = []
        total_chars = 0

        for memory in sorted_candidates:
            content = memory.get("content", "")
            if not content:
                continue

            content_len = len(content)

            # Always include REQUIRED priority memories
            mem_priority = memory.get("budget_priority")
            if mem_priority == BudgetPriority.REQUIRED:
                selected.append(memory)
                total_chars += content_len
                continue

            # Check budget overflow
            if total_chars + content_len > max_chars:
                continue  # Skip this memory — would overflow channel

            selected.append(memory)
            total_chars += content_len

            if total_chars >= max_chars:
                break  # Channel budget full

        logger.debug(
            "TokenBudgeter: selected %d/%d memories for channel %s "
            "(%d/%d chars, %.0f%% utilized)",
            len(selected), len(candidates), channel,
            total_chars, max_chars,
            (total_chars / max_chars * 100) if max_chars > 0 else 0,
        )
        return selected

    def budget_all(
        self,
        candidates: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Allocate candidates across all channels, using memory_type when available.

        Each memory is routed to its channel via:
        1. The `memory_type` field (if present) — direct routing
        2. `infer_channel(category)` — fallback from category mapping

        Then select_memories() applies per-type selection strategies:
        - **Episodic**: Recent + high emotional_valence (stories, moments)
        - **Semantic**: High importance + frequently accessed (facts, preferences)
        - **Procedural**: Always include if relevant (skills, patterns)
        - **Implicit**: Inject as behavioral nudges, not explicit content

        Args:
            candidates: List of memory dicts with 'content', 'category',
                'importance', 'memory_type' (optional), and 'access_count' keys.

        Returns:
            Dict mapping channel names to their selected memories.
        """
        # Partition candidates by channel (prefer memory_type over infer_channel)
        channels: Dict[str, List[Dict[str, Any]]] = {
            "episodic": [],
            "semantic": [],
            "procedural": [],
            "spatial": [],
            "heuristic": [],
        }

        for memory in candidates:
            # T5-3: Use memory_type field when available
            mem_type = memory.get("memory_type")
            if mem_type and mem_type in ("episodic", "semantic", "procedural", "implicit"):
                channel_name = "heuristic" if mem_type == "implicit" else mem_type
            else:
                category = memory.get("category", "general")
                channel_enum = infer_channel(category)
                channel_name = channel_enum.value
            if channel_name not in channels:
                channel_name = "episodic"  # Default fallback
            channels[channel_name].append(memory)

        # Select for each channel with type-aware strategies
        result: Dict[str, List[Dict[str, Any]]] = {}
        for channel_name, channel_candidates in channels.items():
            if channel_candidates:
                # Apply per-type selection strategy
                strategy = _TYPE_STRATEGIES.get(channel_name, _default_strategy)
                sorted_candidates = strategy(channel_candidates)
                result[channel_name] = self.select_memories(
                    sorted_candidates, channel=channel_name
                )
            else:
                result[channel_name] = []

        return result

    def format_for_injection(
        self,
        allocations: Dict[str, List[Dict[str, Any]]],
        max_total_chars: Optional[int] = None,
    ) -> str:
        """Format selected memories into a single string for prompt injection.

        Each channel is rendered with a header, and memories are presented
        as bullet points sorted by importance.

        Args:
            allocations: Output of budget_all() — channel → selected memories.
            max_total_chars: Optional hard cap on total output length.
                If None, uses the budget's total_memory allocation.

        Returns:
            Formatted string ready for prompt injection.
        """
        if max_total_chars is None:
            max_total_chars = self.budget.get("total_memory", 30000) * CHARS_PER_TOKEN

        channel_labels = {
            "episodic": "📋 Recent Events & Memories",
            "semantic": "📚 Knowledge & Facts",
            "procedural": "🔧 Patterns & Skills",
            "spatial": "🗺️ Location & Spatial Context",
            "heuristic": "💡 Associations & Intuition",
        }

        sections: List[str] = []
        total_chars = 0

        for channel_name, memories in allocations.items():
            if not memories:
                continue

            label = channel_labels.get(channel_name, channel_name.title())
            section_lines = [f"\n{label}"]

            for mem in memories:
                content = mem.get("content", "").strip()
                importance = mem.get("importance", 5)
                if content:
                    line = f"  • [{importance}] {content}"
                    if total_chars + len(line) > max_total_chars:
                        break
                    section_lines.append(line)
                    total_chars += len(line)

            if len(section_lines) > 1:  # More than just the header
                sections.append("\n".join(section_lines))

            if total_chars >= max_total_chars:
                break

        return "\n".join(sections)

    def get_budget_summary(self) -> Dict[str, Any]:
        """Return a human-readable summary of the budget allocation."""
        return {
            "total_context": self.budget.get("total_memory", 0) + 10000,
            "memory_allocation": self.budget.get("total_memory", 0),
            "channels": {
                name: f"{tokens} tokens (~{tokens * CHARS_PER_TOKEN} chars)"
                for name, tokens in self.budget.items()
                if name != "total_memory"
            },
            "chars_per_token": CHARS_PER_TOKEN,
        }