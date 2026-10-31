"""Conversation identity — which talk an episode belongs to (E-035).

Before E-035 a persona had exactly one undifferentiated memory
stream: every episode it ever remembered loaded into every
session, whatever the operator was talking about. Two talks —
say, household planning in the morning and a work project in the
afternoon — bled into each other's prompts, and there was no way
to keep them apart.

A *conversation* is the named unit episodes are grouped by,
inside a persona:

- ``id`` — the conversation's stable slug. It is a memory
  namespace, exactly as ``Persona.id`` is (E-025): episodes are
  tagged with it (``Episode.conversation_id``) and only a
  conversation's own episodes may ride in its turns. The rules
  are the persona slug rules, for the same reason — the id is
  used to build namespaces and (in the pending journal) travels
  in file payloads, so it may never be a path.
- The ``default`` conversation is the namespace every
  pre-E-035 episode already belongs to, so an existing install's
  history is continuous with its single-stream past instead of
  orphaned by this slice.

Validation lives here, in the schema layer, so every road in
(resolution, filtering, tests) judges a conversation id by the
same rules.
"""

from __future__ import annotations

import re

#: The conversation every un-tagged episode and every pre-E-035
#: install belongs to.
DEFAULT_CONVERSATION_ID = "default"

#: A conversation id is a paragraph-label, not a novel — and it
#: rides in episode metadata on every turn, so it is capped
#: where it is defined (tiny-hardware discipline, as E-025).
MAX_CONVERSATION_ID_CHARS = 64

_CONVERSATION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def is_valid_conversation_id(value: object) -> bool:
    """True when ``value`` is a conversation id the rules allow."""
    return (
        isinstance(value, str)
        and 0 < len(value) <= MAX_CONVERSATION_ID_CHARS
        and bool(_CONVERSATION_ID_RE.match(value))
    )


__all__ = [
    "DEFAULT_CONVERSATION_ID",
    "MAX_CONVERSATION_ID_CHARS",
    "is_valid_conversation_id",
]
