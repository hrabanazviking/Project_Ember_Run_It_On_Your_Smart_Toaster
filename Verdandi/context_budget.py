#!/usr/bin/env python3
"""
Verdandi Context Injection Budget — the discipline for what may
be injected into a cron/companion prompt, when, and how much.

Filed by Project Ember slice E-062 (docs/architecture/
E-062_CONTEXT_INJECTION_DISCIPLINE.md). This module IS the
budget in code, in the same shape as event_contract.py (E-061):
stdlib only, no imports from any other Verdandi module, because
the deployed copies of the conversation layer load modules
file-by-file from ~/.hermes/state and this discipline must stand
alone exactly like nervous_system.py does.

WHAT MAY BE INJECTED (the only sources)

The context block built by conversation_logger.get_context_for_cron
may draw on exactly four sources, all inside the one state dir
(STATE_DIR, default ~/.hermes/state):

1. ``current.json`` — the active session's state snapshot
   (session id, status, last updated, summary, decisions,
   next actions, blockers, projects touched).
2. ``conversation_log.jsonl`` — recent session summaries only:
   one line per session (timestamp, session id, summary). Full
   log entry bodies, event contents beyond the summary line,
   and older sessions are NOT injected.
3. ``nerve_feed.jsonl`` — the tail of the nerve feed (E-061
   contract events), rendered as one short line per event.
4. Reaction directives — reactor.react() output derived from
   the same log (priority, action, detail, capped items).

Nothing else may be injected: no environment variables, no
config files, no credential-shaped material (E-093's custody
law starts here — a secret that is never in the log can never
be injected, and log writers must never log one), no file
contents from outside the state dir, and no live hub query —
the feed is read from its file, so injection works with the
hub down and can never block on it.

WHEN

Injection happens once, at the start of a cron/companion job,
via context_injector (default / ``context`` command) or the
logger's own ``context`` command. It is a starting brief, not
a per-turn feed: nothing in this discipline authorises
re-injecting mid-session or injecting into a human's ordinary
chat unasked.

THE BUDGET (characters, not tokens — the block is plain text
and characters are what a reader can verify without a tokenizer)

- The whole block never exceeds TOTAL_MAX_CHARS, header and
  end marker included.
- Each layer has its own ceiling; the layer ceilings sum to
  the total, so no layer can starve the others by construction.
- Per-item caps apply inside each layer (counts AND lengths):
  an item list is capped in both dimensions, so one huge
  blocker or decision cannot fill a layer by itself.
- Shedding order when a layer or the total overflows, lowest
  value first: reaction directives shed first, then the nerve
  feed tail, then recent sessions; the current-state layer is
  shed last and its blockers are the last thing inside it to
  go. A shed or truncated layer says so in the block itself
  (the truncation marker) — injection never silently pretends
  a shortened block was the whole story.
- Supplementary layers (nerve feed, reactions) remain
  failure-silent, exactly as before: a missing or broken
  supplementary source yields no layer, never an error and
  never a fabricated one. The primary layers (current state,
  recent sessions) are read from the log's own state dir —
  the same STATE_DIR the logger writes to, not a second
  hardcoded home path (fixed in E-062).

The numeric literals live in conversation_logger.py as plain
literals (not imports of this module) for the same deployed-
standalone reason event_contract's version literal lives in
nervous_system.py; the E-062 conformance tests pin the two
copies equal, so they cannot drift.
"""

CONTEXT_BUDGET_VERSION = 1

# Total ceiling for the whole rendered block, in characters.
TOTAL_MAX_CHARS = 4000

# Per-layer ceilings (sum == TOTAL_MAX_CHARS).
CURRENT_MAX_CHARS = 1200
RECENT_MAX_CHARS = 700
NERVE_MAX_CHARS = 1000
REACTIONS_MAX_CHARS = 1100

# Layer shedding priority: higher number sheds first.
LAYER_SHED_ORDER = {
    "reactions": 3,
    "nerve": 2,
    "recent": 1,
    "current": 0,
}

# Retention order inside the current-state layer: fields render
# in the order identity/summary, blockers, decisions, next
# actions, projects — so when the layer must shed whole lines,
# projects shed first and blockers shed last.

# Per-item caps: (max items, max chars per item) per field.
SUMMARY_MAX_CHARS = 120
RECENT_SUMMARY_MAX_CHARS = 100
DECISIONS_MAX_ITEMS = 5
NEXT_ACTIONS_MAX_ITEMS = 5
BLOCKERS_MAX_ITEMS = 10
PROJECTS_MAX_ITEMS = 10
LIST_ITEM_MAX_CHARS = 120
PROJECT_ITEM_MAX_CHARS = 60

# Joined-field caps: a whole rendered list line is also capped,
# so the highest-retention field (blockers, 600) plus the
# scalar lines always fits inside the current layer's ceiling
# on its own — line shedding can then never be forced to drop
# blockers merely because every item used its full allowance.
BLOCKERS_JOIN_MAX_CHARS = 600
DECISIONS_JOIN_MAX_CHARS = 300
NEXT_ACTIONS_JOIN_MAX_CHARS = 300
PROJECTS_JOIN_MAX_CHARS = 300

# Recent sessions: the caller's max_sessions is a request, not
# an entitlement — it is clamped to this ceiling.
RECENT_MAX_SESSIONS = 5

# Nerve feed tail.
NERVE_MAX_EVENTS = 10
NERVE_DATA_MAX_CHARS = 100
NERVE_SOURCE_MAX_CHARS = 60
NERVE_TYPE_MAX_CHARS = 60

# Reaction directives.
REACTIONS_MAX_DIRECTIVES = 6
REACTIONS_ITEMS_PER_DIRECTIVE = 3
REACTION_ITEM_MAX_CHARS = 120
REACTION_DETAIL_MAX_CHARS = 120

TRUNCATION_MARKER = "[... truncated by context budget E-062]"

# The only state-dir files injection may read.
ALLOWED_SOURCE_FILES = (
    "current.json",
    "conversation_log.jsonl",
    "nerve_feed.jsonl",
)


def truncate_text(text: str, limit: int) -> str:
    """Truncate ``text`` to at most ``limit`` chars, marking the cut."""
    text = str(text)
    if len(text) <= limit:
        return text
    if limit <= len(TRUNCATION_MARKER):
        return text[:limit]
    return text[: limit - len(TRUNCATION_MARKER)] + TRUNCATION_MARKER


def cap_items(items, max_items: int, max_chars: int) -> list:
    """Cap a list in both dimensions: count and per-item length."""
    return [truncate_text(item, max_chars) for item in list(items)[:max_items]]
