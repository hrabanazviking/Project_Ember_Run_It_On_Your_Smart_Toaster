"""Conversation core — selection and memory separation (E-035)."""

from ember.spark.conversation.core import (
    ConversationError,
    episodes_for_conversation,
    resolve_conversation_id,
    tag_episode,
)

__all__ = [
    "ConversationError",
    "episodes_for_conversation",
    "resolve_conversation_id",
    "tag_episode",
]
