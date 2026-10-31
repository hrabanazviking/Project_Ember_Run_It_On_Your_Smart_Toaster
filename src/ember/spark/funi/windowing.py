"""Conversation history windowing under a token budget (E-021).

Before E-021 the chat loop carried ``episodes[-5:]`` — a fixed count,
no token budget, no account of what was dropped, and no history at all
after a restart (episodes were write-only in the Well; docket 81).
This module is the hardening:

- **History** — the caller loads past episodes (the Well reader,
  :meth:`BrunnrHandle.recent_episodes`, lands with this slice) and
  hands the whole conversation here, oldest first.
- **Windowing** — :func:`window_history` keeps the newest episodes
  that fit the profile-aware token budget from
  :class:`ember.schemas.config.ConversationConfig`, subject to the
  profile's episode cap. The newest episode is always kept, even if
  it alone exceeds the budget — an empty history when a conversation
  exists would be a lie of omission.
- **Summarisation hooks** — whatever the window drops is passed to a
  :class:`Summariser` hook. The default hook is deterministic and
  extractive (stdlib only, no model call — a toaster cannot afford a
  second inference to summarise the first); a future model-backed
  summariser implements the same protocol and slots in without the
  caller changing.

Token counting is an *estimate*: 4 characters per token, rounded up —
the standard cheap approximation for English prose. It is a budget
guardrail, not a billing meter; the model's own reported
``prompt_tokens`` remain the truth where a backend reports them.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ember.schemas.config import ConversationConfig
from ember.schemas.episode import Episode

_CHARS_PER_TOKEN = 4
# A dropped episode contributes at most this many characters of its
# operator line and of Ember's reply to the extractive summary, so the
# summary itself stays small enough for a toaster profile.
_SUMMARY_SNIPPET_CHARS = 80
_SUMMARY_MAX_CHARS = 600


def estimate_tokens(text: str) -> int:
    """Estimate the token cost of ``text`` (ceil of chars / 4)."""
    if not text:
        return 0
    return max(1, math.ceil(len(text) / _CHARS_PER_TOKEN))


def episode_cost(episode: Episode) -> int:
    """Estimated token cost of one episode in the prompt."""
    return estimate_tokens(episode.operator_input) + estimate_tokens(
        episode.ember_reply
    )


@runtime_checkable
class Summariser(Protocol):
    """Summarisation hook: dropped episodes in, summary text out.

    Returning an empty string means "no summary" — the windowing
    result then carries ``summary=None`` and the prompt honestly
    contains only what was kept.
    """

    def summarise(self, episodes: Sequence[Episode]) -> str: ...


class ExtractiveSummariser:
    """The default hook: deterministic, extractive, model-free.

    Names how many turns were summarised and quotes the head of each
    dropped operator line (and Ember's reply), oldest first, capped
    at ``_SUMMARY_MAX_CHARS``. It invents nothing — every word in the
    summary is either the count or a verbatim snippet.
    """

    def summarise(self, episodes: Sequence[Episode]) -> str:
        if not episodes:
            return ""
        parts = [
            f"Summary of {len(episodes)} earlier turn(s) that no longer "
            "fit the history window:"
        ]
        for episode in episodes:
            op = _snippet(episode.operator_input)
            em = _snippet(episode.ember_reply)
            parts.append(f"- Operator: {op} / Ember: {em}")
        text = "\n".join(parts)
        if len(text) > _SUMMARY_MAX_CHARS:
            text = text[: _SUMMARY_MAX_CHARS - 1].rstrip() + "…"
        return text


def _snippet(text: str) -> str:
    flat = " ".join(text.split())
    if len(flat) <= _SUMMARY_SNIPPET_CHARS:
        return flat
    return flat[: _SUMMARY_SNIPPET_CHARS - 1].rstrip() + "…"


@dataclass(frozen=True, slots=True)
class WindowedHistory:
    """The result of windowing one conversation's history."""

    episodes: tuple[Episode, ...]
    """Episodes kept verbatim, oldest first."""

    dropped: tuple[Episode, ...]
    """Episodes the window dropped, oldest first."""

    summary: str | None
    """Summary of ``dropped`` from the hook, or None when nothing was
    dropped, summarisation is disabled, or the hook returned empty."""

    estimated_tokens: int
    """Estimated token cost of the kept episodes."""


def window_history(
    episodes: Sequence[Episode],
    config: ConversationConfig,
    *,
    summariser: Summariser | None = None,
) -> WindowedHistory:
    """Window ``episodes`` (oldest first) under ``config``'s budget.

    Two bounds apply, in order: the episode cap keeps the newest
    ``resolved_max_episodes``; the token budget then walks newest →
    oldest keeping episodes while the cumulative estimate fits
    ``resolved_token_budget`` (the newest episode is kept regardless).
    Everything not kept is reported in ``dropped`` and, when
    ``config.summarise_dropped`` is set, summarised through the hook
    (default: :class:`ExtractiveSummariser`).
    """
    ordered = list(episodes)
    cap = max(0, config.resolved_max_episodes)
    budget = max(0, config.resolved_token_budget)

    capped = ordered[-cap:] if cap else []
    cap_dropped = ordered[: len(ordered) - len(capped)]

    kept_newest_first: list[Episode] = []
    spent = 0
    for episode in reversed(capped):
        cost = episode_cost(episode)
        if kept_newest_first and spent + cost > budget:
            break
        kept_newest_first.append(episode)
        spent += cost
    kept = list(reversed(kept_newest_first))
    budget_dropped = capped[: len(capped) - len(kept)]

    dropped = tuple(cap_dropped + budget_dropped)
    summary: str | None = None
    if dropped and config.summarise_dropped:
        hook = summariser if summariser is not None else ExtractiveSummariser()
        text = hook.summarise(dropped)
        summary = text if text else None

    return WindowedHistory(
        episodes=tuple(kept),
        dropped=dropped,
        summary=summary,
        estimated_tokens=spent,
    )


__all__ = [
    "ExtractiveSummariser",
    "Summariser",
    "WindowedHistory",
    "episode_cost",
    "estimate_tokens",
    "window_history",
]
