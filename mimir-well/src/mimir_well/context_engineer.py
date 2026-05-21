"""
Mímir's Well — Context Engineering
=====================================
Intelligent memory injection for Hermes turns.

The ContextEngineer decides WHAT memories get injected and WHERE,
using TokenBudgeter for allocation, WyrdGraph for entity relevance,
and recall_current for temporal validity.

Like the Norns weaving threads at the Well, the engineer selects
only the threads that matter for this moment in the weave.

ᚢ ᚱ ᚦ — What was, what is becoming, what shall be.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mimir_well.budget import TokenBudget, TokenBudgeter
from mimir_well.core import RunaMemory
from mimir_well.wyrd_graph import WyrdGraph

logger = logging.getLogger(__name__)


@dataclass
class ContextResult:
    """Result of context assembly — the memory injection for a Hermes turn."""

    episodic: List[Dict[str, Any]] = field(default_factory=list)
    semantic: List[Dict[str, Any]] = field(default_factory=list)
    procedural: List[Dict[str, Any]] = field(default_factory=list)
    spatial: List[Dict[str, Any]] = field(default_factory=list)
    heuristic: List[Dict[str, Any]] = field(default_factory=list)
    graph_paths: List[Dict[str, Any]] = field(default_factory=list)
    total_tokens: int = 0
    budget_total: int = 0
    budget_used_pct: float = 0.0
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_context_block(self) -> str:
        """Format as a context block string for injection into a prompt."""
        parts = []

        if self.episodic:
            parts.append("## Episodic (Recent Events)")
            for m in self.episodic:
                parts.append(f"- [{m.get('importance', '?')}] {m['content'][:200]}")

        if self.semantic:
            parts.append("## Semantic (Facts & Preferences)")
            for m in self.semantic:
                parts.append(f"- [{m.get('importance', '?')}] {m['content'][:200]}")

        if self.procedural:
            parts.append("## Procedural (Patterns & Skills)")
            for m in self.procedural:
                parts.append(f"- [{m.get('importance', '?')}] {m['content'][:200]}")

        if self.graph_paths:
            parts.append("## Relationships (Graph Paths)")
            for p in self.graph_paths:
                # Path items can be tuples or dicts — handle both
                if isinstance(p, dict) and p.get("path"):
                    path_str = " → ".join(
                        f"{step[0]}({step[1]})" if isinstance(step, tuple) 
                        else f"{step.get('entity', '?')}({step.get('relationship', '?')})"
                        for step in p["path"]
                    )
                elif isinstance(p, dict):
                    path_str = f"{p.get('entity', '?')} via {p.get('relationship', '?')}"
                else:
                    path_str = str(p)
                strength = p.get('strength', '?') if isinstance(p, dict) else '?'
                parts.append(f"- {path_str} [strength={strength}]")

        if self.spatial:
            parts.append("## Spatial Awareness")
            for m in self.spatial:
                parts.append(f"- {m['content'][:200]}")

        if self.heuristic:
            parts.append("## Heuristic Associations")
            for m in self.heuristic:
                parts.append(f"- {m['content'][:200]}")

        return "\n".join(parts) if parts else ""


class ContextEngineer:
    """Assembles the memory context for a Hermes turn.

    Uses TokenBudgeter for allocation, WyrdGraph for entity relevance,
    and RunaMemory.recall_current for temporal validity.

    The Norns do not pour the entire Well into each cup.
    They draw only what the moment requires.
    """

    def __init__(
        self,
        mimir: RunaMemory,
        graph: WyrdGraph,
        budgeter: Optional[TokenBudgeter] = None,
        total_context: int = 128000,
    ):
        self.mimir = mimir
        self.graph = graph
        if budgeter:
            self.budgeter = budgeter
        else:
            budget = TokenBudget(total_context=total_context)
            self.budgeter = TokenBudgeter(budget)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count: ~4 chars per token."""
        return max(1, len(text) // 4)

    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entity names from user message.

        Looks for capitalized multi-word phrases and known patterns.
        """
        entities = []

        # Simple heuristic: capitalized phrases that could be entity names
        # Match 1-3 word capitalized phrases
        matches = re.findall(
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b',
            text
        )
        for match in matches:
            normalized = match.lower().replace(" ", "-")
            # Skip common non-entity words
            skip = {"the", "and", "but", "for", "not", "this", "that",
                    "was", "has", "had", "been", "will", "would", "could",
                    "should", "might", "must", "can", "are", "is", "am",
                    "have", "do", "did", "does", "what", "when", "where",
                    "how", "why", "which", "who", "there", "here", "just",
                    "like", "very", "really", "much", "more", "most"}
            if normalized not in skip and len(normalized) > 2:
                entities.append(normalized)

        return list(set(entities))

    def assemble_context(
        self,
        user_message: str,
        mentioned_entities: Optional[List[str]] = None,
        current_turn: int = 0,
        focus_categories: Optional[List[str]] = None,
    ) -> ContextResult:
        """Build the memory injection for this turn.

        Args:
            user_message: The current user message to find relevant memories.
            mentioned_entities: Explicitly mentioned entity names for graph boost.
            current_turn: Turn number (for recency weighting).
            focus_categories: Optional categories to prioritize.

        Returns:
            ContextResult with selected memories per channel.
        """
        result = ContextResult()
        total_tokens = 0

        # Extract entities from message if not provided
        entities = mentioned_entities or []
        if not entities:
            entities = self._extract_entities(user_message)

        # ── 1. Episodic: Recent High-Emotional-Valence Memories ───────────
        try:
            episodic_candidates = self.mimir.recall_current(
                query=user_message,
                category=focus_categories[0] if focus_categories else None,
                min_importance=6,
                limit=20,
            )
            # Filter to episodic type only
            episodic_candidates = [
                m for m in episodic_candidates
                if m.get("memory_type") == "episodic"
            ]
            selected = self.budgeter.select_memories(
                episodic_candidates, channel="episodic"
            )
            result.episodic = selected
            total_tokens += sum(
                self._estimate_tokens(m.get("content", ""))
                for m in selected
            )
        except Exception as e:
            logger.warning("Episodic recall failed: %s", e)

        # ── 2. Semantic: Stable Facts, Boosted by Entity Relevance ────────
        try:
            semantic_candidates = self.mimir.recall_current(
                query=user_message,
                category=focus_categories[0] if focus_categories else None,
                min_importance=5,
                limit=30,
            )
            # Filter to semantic type only
            semantic_candidates = [
                m for m in semantic_candidates
                if m.get("memory_type") in ("semantic", None)
            ]
            # Boost relevance for mentioned entities
            if entities:
                for entity in entities[:3]:  # Cap at 3 entities
                    try:
                        graph_context = self.graph.get_related(
                            entity, max_depth=2
                        )
                        # Add graph paths to heuristic channel
                        for outgoing in graph_context.get("outgoing", [])[:5]:
                            result.graph_paths.append(outgoing)
                        for incoming in graph_context.get("incoming", [])[:3]:
                            result.graph_paths.append(incoming)
                    except Exception as e:
                        logger.debug("Graph path lookup failed (best-effort): %s", e)

            selected = self.budgeter.select_memories(
                semantic_candidates, channel="semantic"
            )
            result.semantic = selected
            total_tokens += sum(
                self._estimate_tokens(m.get("content", ""))
                for m in selected
            )
        except Exception as e:
            logger.warning("Semantic recall failed: %s", e)

# ── 3. Procedural: Skills and Patterns ────────────────────────────────────
        try:
            procedural_candidates = self.mimir.recall_current(
                query=user_message,
                category="lesson",
                min_importance=5,
                limit=10,
            )
            # Filter to procedural type only
            procedural_candidates = [
                m for m in procedural_candidates
                if m.get("memory_type") == "procedural"
            ]
            # Procedural channel has smallest budget, so select carefully
            selected = self.budgeter.select_memories(
                procedural_candidates, channel="procedural"
            )
            result.procedural = selected
            total_tokens += sum(
                self._estimate_tokens(m.get("content", ""))
                for m in selected
            )
        except Exception as e:
            logger.warning("Procedural recall failed: %s", e)

        # ── 4. Spatial + Heuristic: Filled by WYRD/Hebbian bridges ───────
        # These channels remain empty until WYRD Protocol and NSE
        # provide spatial awareness and Hebbian associations respectively.
        # The architecture is ready for them.

        # Deduplicate graph_paths
        seen_paths = set()
        unique_paths = []
        for p in result.graph_paths:
            key = (p.get("entity", ""), p.get("relationship", ""))
            if key not in seen_paths:
                seen_paths.add(key)
                unique_paths.append(p)
        result.graph_paths = unique_paths[:20]  # Cap at 20 paths

# ── Compute budget stats ──────────────────────────────────────────────
        budget_alloc = self.budgeter.budget  # Already a dict from TokenBudget.compute()
        result.budget_total = budget_alloc.get("total_memory", 0)
        result.budget_used_pct = (
            total_tokens / max(result.budget_total, 1)
        )
        result.total_tokens = total_tokens

        # ── Stats ──────────────────────────────────────────────────────────
        result.stats = {
            "episodic_count": len(result.episodic),
            "semantic_count": len(result.semantic),
            "procedural_count": len(result.procedural),
            "graph_paths_count": len(result.graph_paths),
            "entities_detected": entities[:5],
            "total_tokens": total_tokens,
            "budget_pct": round(result.budget_used_pct * 100, 1),
        }

        logger.info(
            "Context assembled: %d episodic, %d semantic, %d procedural, "
            "%d graph paths — %d tokens (%.0f%% of budget)",
            result.stats["episodic_count"],
            result.stats["semantic_count"],
            result.stats["procedural_count"],
            result.stats["graph_paths_count"],
            total_tokens,
            result.budget_used_pct * 100,
        )

        return result

    def quick_context(self, user_message: str) -> str:
        """Fast context assembly that returns just the formatted string.

        Convenience method for direct injection into prompts.
        """
        result = self.assemble_context(user_message)
        return result.to_context_block()