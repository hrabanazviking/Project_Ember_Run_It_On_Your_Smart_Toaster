#!/usr/bin/env python3
"""
Verdandi Conversation Logger Law — what is logged, where, for
whom; how long it is kept; and the user's delete right.

Filed by Project Ember slice E-063 (docs/architecture/
E-063_CONVERSATION_LOGGER_LAW.md). This module IS the law in
code, in the same shape as event_contract.py (E-061) and
context_budget.py (E-062): stdlib only, no imports from any
other Verdandi module, because the deployed copies of the
conversation layer load modules file-by-file from
~/.hermes/state and this law must stand alone exactly like
nervous_system.py does. The logger's own delete functions
live in conversation_logger.py as plain code (the deployed-
standalone pattern); the conformance tests pin this module's
constants against the logger and against the heartbeat's
retention thresholds, so the copies cannot drift.

WHAT IS LOGGED

The logger (conversation_logger.py) writes four entry kinds
to the log, and nothing else:

- ``start``  — session id, summary, model, platform,
  start_time, timestamp. Written by ``start`` (and by
  context_injector's ``log-start``).
- ``event``  — session id, timestamp, one event type from
  EVENT_TYPES (decision, file_changed, learned, action,
  blocker, blocker_resolved, mood_shift, milestone) and the
  caller-supplied content string.
- ``update`` — session id, timestamp, and the state snapshot
  fields next_actions, blockers, projects_touched, mood.
- ``end``    — session id, timestamp, summary,
  duration_minutes, and the closing snapshot lists
  (decisions, things_learned, files_changed, next_actions,
  blockers, projects_touched).

Content is caller-supplied and is logged verbatim: the
logger applies no redaction, no summarisation and no
filtering. The custody rule therefore starts at the writer:
a credential or secret must never be passed as a summary,
content, or list item (E-093's custody law; E-062 already
applies the same rule to injection).

WHERE IT LIVES

All inside the one state dir (STATE_DIR, default
~/.hermes/state):

- ``conversation_log.jsonl`` — the log itself: one JSON
  entry per line, appended as it happens, so a crashed
  session loses at most the line being written.
- ``current.json`` — a snapshot of the LATEST session only:
  whichever session ran ``start`` most recently owns it,
  and only that session's own event/update/end commands may
  change it (an entry for another session is still logged,
  but it never rewrites another session's snapshot — the
  E-063 settlement of docket 98).
- ``conversations/`` — a directory the logger creates on
  every append and otherwise does not use. Recorded
  honestly: nothing is stored there.
- The nerve copies: every appended entry is also fired to
  the nerve hub as a ``conv_*`` event (E-061 contract), so
  a copy of each entry can live in ``nerve_feed.jsonl`` and
  in its rotated archives (``nerve_feed_*.jsonl`` /
  ``nerve_feed_*.jsonl.gz``) in the same state dir. The
  delete right below covers those copies; without that, a
  "deleted" conversation would still be readable from the
  feed, and the right would not be total.

FOR WHOM — THE READERS

The log is written for the person who owns the state dir,
and read back only through named readers: the logger's own
``show`` / ``recent`` / ``context`` commands, the public
``get_current_state`` / ``get_recent_conversations`` API,
context_injector (which is the same commands plus the cron
logging shim), the reactor (which derives reaction
directives from the log, E-062 layer 4), the heartbeat's
Mimir check (which reads the log's SIZE and entry count,
not its content, for health), and the heartbeat's Bifrost
cleanup (retention, below). The Ember core does not read
the log (E-059). Whether logged conversations may feed
long-term memory is E-072's question, not settled here.

RETENTION — HOW LONG IT IS KEPT

The logger itself keeps everything indefinitely: it has no
age limit, no entry limit and no rotation. Two system
mechanisms, both in the heartbeat and both size-based,
bound the files on disk:

- the nerve feed rotates at 10 MB into a compressed
  archive (nervous_system.py);
- Bifrost's auto_cleanup prunes ``conversation_log.jsonl``
  when it exceeds 50 MB (and the nerve feed at 20 MB),
  keeping the newest lines (at least 100) — Mimir's check
  warns at 50 MB and turns critical at 200 MB.

That pruning is machine hygiene, not a user right and not
a privacy mechanism: it is oldest-first by line, it is not
session-aware (it can cut a long session's earliest lines
while keeping its later ones — docket 100, owned by the
E-076 gate review), and it never touches current.json.
Nothing else in the tree deletes logged conversations.

THE USER'S DELETE RIGHT — TOTAL, AND PROVABLE

The owner of the state dir may delete, at any time, through
the logger's own ``delete`` command:

- one named session (``delete --session <id>``), or
- everything (``delete --all --yes``; the extra ``--yes``
  is required because "everything" cannot be named the way
  a session can).

A deletion is TOTAL across every place the logger's words
live: the session's entries leave conversation_log.jsonl,
current.json is removed if (and only if) it belongs to
that session, and the session's conv_* copies leave the
nerve feed and every rotated feed archive in the state
dir. Other sessions, non-conversation feed events, and
unattributable lines (lines that are not valid JSON
entries — the logger cannot prove whose they are) are kept;
unattributable lines are counted in the report, never
silently dropped and never silently claimed deleted.

A deletion is PROVABLE: each affected file is rewritten
atomically (a temporary file in the same directory, then a
replace — a crash mid-delete leaves either the old file or
the new one, never a torn one), and after the rewrite the
logger re-reads every affected file and counts what
remains. The delete report states, per scope, how many
entries were removed from the log, whether current.json
was removed, how many nerve copies were removed, how many
unattributable lines were kept, and whether verification
found zero attributable entries remaining. A deletion that
cannot verify does not claim success.
"""

LOGGER_LAW_VERSION = 1

# The four entry kinds the logger writes, in lifecycle order.
ENTRY_TYPES = ("start", "event", "update", "end")

# The event vocabulary of an ``event`` entry. This is the
# logger's EVENT_TYPES, restated here so the law stands
# alone; the conformance tests pin the two copies equal.
EVENT_TYPES = frozenset({
    "decision", "file_changed", "learned", "action",
    "blocker", "blocker_resolved", "mood_shift", "milestone",
})

# Fields carried by each entry kind (the logger's cmd_*
# writers are the authority; the tests re-derive these
# from live entries the logger itself writes).
ENTRY_FIELDS = {
    "start": ("entry_type", "timestamp", "session_id", "summary",
              "model", "platform", "start_time"),
    "event": ("entry_type", "timestamp", "session_id",
              "event_type", "content"),
    "update": ("entry_type", "timestamp", "session_id",
               "next_actions", "blockers", "projects_touched", "mood"),
    "end": ("entry_type", "timestamp", "session_id", "summary",
            "duration_minutes", "decisions", "things_learned",
            "files_changed", "next_actions", "blockers",
            "projects_touched"),
}

# The state-dir files the logger's words live in. The nerve
# feed and its archives hold COPIES (conv_* events), not the
# log itself; both halves are inside the delete right.
LOG_FILE = "conversation_log.jsonl"
CURRENT_FILE = "current.json"
CONVERSATIONS_DIR = "conversations"
NERVE_FEED_FILE = "nerve_feed.jsonl"
NERVE_ARCHIVE_GLOBS = ("nerve_feed_*.jsonl", "nerve_feed_*.jsonl.gz")

# Every file a total deletion must account for.
DELETE_SCOPE_FILES = (LOG_FILE, CURRENT_FILE, NERVE_FEED_FILE)

# Retention thresholds of the heartbeat's size-based
# mechanisms (NOT the logger's — the logger has none).
# Pinned by the conformance tests against their sources:
# Bifrost's DEFAULT_TARGETS, Mimir's check defaults, and
# nervous_system's rotation constant.
CONVERSATION_LOG_PRUNE_MB = 50
NERVE_FEED_PRUNE_MB = 20
LOG_SIZE_WARNING_MB = 50
LOG_SIZE_CRITICAL_MB = 200
NERVE_FEED_ROTATE_BYTES = 10 * 1024 * 1024

# The delete command's shapes: a named session needs no
# further word; deleting everything requires the explicit
# confirmation flag.
DELETE_ALL_REQUIRES_YES = True
