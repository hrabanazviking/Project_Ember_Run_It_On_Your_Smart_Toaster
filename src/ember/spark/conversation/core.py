"""Conversation selection and per-conversation memory separation.

The companion's talks live inside its persona (E-025): a persona
may hold many conversations, and a conversation is one talk —
one topic, one thread — whose episodes must never ride in
another conversation's turns. This module is the conversation
half of that discipline, shaped exactly like the persona half:

- :func:`resolve_conversation_id` picks the conversation a
  session runs in: an explicit choice (the ``ember chat
  --conversation`` flag / the ``chat.run`` argument) wins, then
  the config file's ``conversation.active``, then ``default``.
  A chosen id that is not a valid slug is an error, never a
  silent fall-back to a different conversation — falling back
  would mix the very talks the operator asked to keep apart.
- :func:`episodes_for_conversation` is the filter every consumer
  uses, and ``ember.spark.funi.prompt.assemble`` applies the
  same rule at the prompt boundary, so a caller that forgets to
  filter still cannot leak one conversation into another's turn.

What isolation does *not* cover, stated plainly: the Well's
document chunks are the companion's shared library — retrieval
grounding is deliberately common to every conversation, the
same way a person uses the same bookshelf in every talk. Only
*episodes* (remembered turns) are conversation-private.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence

from ember.schemas.conversation import (
    DEFAULT_CONVERSATION_ID,
    is_valid_conversation_id,
)
from ember.schemas.episode import Episode
from ember.schemas.errors import SparkError


class ConversationError(SparkError):
    """A conversation id could not be resolved or used."""


def resolve_conversation_id(
    explicit: str | None = None,
    configured: str = "",
) -> str:
    """Resolve the conversation a session should run in.

    Order: ``explicit`` (when not None) wins and must be a valid
    slug; otherwise a non-empty ``configured`` value must be a
    valid slug; otherwise the ``default`` conversation. An
    invalid chosen id raises :class:`ConversationError` — never
    a silent substitution of a different conversation.
    """
    if explicit is not None:
        _require_slug(explicit, source="the explicit conversation choice")
        return explicit
    if configured:
        _require_slug(configured, source="conversation.active in the config file")
        return configured
    return DEFAULT_CONVERSATION_ID


def tag_episode(episode: Episode, conversation_id: str) -> Episode:
    """A copy of ``episode`` tagged as ``conversation_id``'s memory."""
    _require_slug(conversation_id, source="the conversation tag")
    return dataclasses.replace(episode, conversation_id=conversation_id)


def episodes_for_conversation(
    episodes: Sequence[Episode],
    conversation_id: str,
) -> list[Episode]:
    """Only ``conversation_id``'s episodes, in their original order.

    The separation rule in one place: an episode belongs to
    exactly the conversation its tag names — no prefix matching,
    no shared "close enough" namespaces, no default-conversation
    leakage into a named conversation or the reverse.
    """
    _require_slug(conversation_id, source="the conversation filter")
    return [ep for ep in episodes if ep.conversation_id == conversation_id]


def _require_slug(conversation_id: str, *, source: str) -> None:
    if not is_valid_conversation_id(conversation_id):
        raise ConversationError(
            f"conversation id {conversation_id!r} from {source} is not "
            "a valid slug; ids are lowercase letters, digits, '-' or "
            "'_', starting with a letter or digit — never a path"
        )


__all__ = [
    "ConversationError",
    "episodes_for_conversation",
    "resolve_conversation_id",
    "tag_episode",
]
