# E-063 — The Conversation Logger's Law: What Is Logged, Where, For Whom; Retention + the User's Delete Right

*Part IV, slice E-063. Starting HEAD: 7b45729's parent 1ec6c5b
(E-062 banked + push-recorded). Method: the logger, its
readers, and the heartbeat's retention mechanisms were
re-read from code this slice — E-059's map was the starting
claim, and every statement below was re-proven against the
tree before anything was changed. The law itself lives in
code at `Verdandi/logger_law.py`; this document is its
reading copy. Conformance is pinned by
`tests/unit/test_logger_law_e063.py` (§8).*

## 1. Plain-language summary

The conversation logger is the companion's diary-keeper: it
writes down, as they happen, the sessions it is asked to
track — when a session started, what was decided, what was
learned, what is blocking, and how it ended. Until this
slice that diary had habits but no written law, and one
hole mattered most: **there was no way to delete anything.**
A person could be logged forever and could never take it
back. Now the law is written down and the missing right
exists. The law says exactly what is logged (four kinds of
entry, with named fields — nothing else), where it lives
(one folder, named files), who may read it (a short list of
named readers, all of them the owner's own programs), and
how long it is kept (the logger itself keeps everything
until the owner says otherwise; only the heartbeat's
size-based housekeeping ever trims it, and that is machine
hygiene, not privacy). And the owner now has a real delete
right: `delete --session <id>` removes one session, and
`delete --all --yes` removes everything — totally, meaning
from the log, from the current-session snapshot, *and* from
the copies the logger fires into the nerve feed and its
rotated archives — and provably, meaning the logger re-reads
every store afterwards and reports the count it found, and
a deletion that cannot verify does not claim success. One
old defect was settled on the way (docket 98): a dead helper
function was removed, and the rule for the current-session
snapshot is now uniform — it belongs to the session that
started it, and another session's entries, though still
logged, never rewrite it.

## 2. What is logged

Exactly four entry kinds, written by the logger's own
commands (and by context_injector's logging shim, which
calls the same commands). Every entry carries `entry_type`,
`timestamp` (UTC, ISO) and `session_id`.

| Kind | Fields beyond the common three | Written by |
|---|---|---|
| `start` | `summary`, `model`, `platform`, `start_time` | `start` / `log-start` |
| `event` | `event_type` (one of the eight below), `content` | `event` / `log-event` |
| `update` | `next_actions`, `blockers`, `projects_touched`, `mood` | `update` |
| `end` | `summary`, `duration_minutes`, `decisions`, `things_learned`, `files_changed`, `next_actions`, `blockers`, `projects_touched` | `end` / `log-end` |

The eight event types: `decision`, `file_changed`,
`learned`, `action`, `blocker`, `blocker_resolved`,
`mood_shift`, `milestone` (the logger's `EVENT_TYPES`,
already pinned to the E-061 contract and the injector's
choices by E-061/E-062).

**Content is caller-supplied and logged verbatim.** The
logger applies no redaction, no summarisation and no
filtering — that is stated plainly because the custody rule
depends on it: a credential or secret must never be passed
as a summary, a content string, or a list item (E-093's
custody law; E-062's injection discipline rests on the same
rule). What is *not* logged: anything the caller does not
pass. The logger records no message bodies of its own, no
environment, no machine data.

## 3. Where it lives

All inside the one state dir (`STATE_DIR`, default
`~/.hermes/state`):

- **`conversation_log.jsonl`** — the log itself. One JSON
  entry per line, appended as it happens (the file's stated
  design: a crashed session loses at most the line being
  written). Malformed lines are skipped by every reader.
- **`current.json`** — a snapshot of the *latest* session
  only (see §5 for its ownership rule). It is a view, not a
  second log: everything in it is derived from that
  session's entries.
- **`conversations/`** — a directory the logger creates on
  every append and otherwise does not use. Recorded
  honestly: nothing is stored there.
- **The nerve copies** — every appended entry is also fired
  to the nerve hub as a `conv_*` event (E-061), so a copy of
  each entry can live in **`nerve_feed.jsonl`** and in its
  rotated archives (`nerve_feed_*.jsonl`,
  `nerve_feed_*.jsonl.gz`) in the same state dir. Any honest
  account of "where the conversation lives" must include
  these — which is why the delete right (§6) covers them.

## 4. For whom — the readers

The log is written for the person who owns the state dir,
and read back only through named readers:

- the logger's own `show` / `recent` / `context` commands
  and its public `get_current_state` /
  `get_recent_conversations` API;
- **context_injector** — the same commands, plus the cron
  logging shim; its *injection* of log material into a new
  job's prompt is governed by E-062's discipline, not here;
- **the reactor** — derives reaction directives from the
  log (E-062 layer 4); its ignored `focus` parameter is
  docket 95, owned by E-065;
- **the heartbeat's Mímir check** — reads the log's *size
  and entry count* for health, not its content;
- **the heartbeat's Bifröst cleanup** — retention, §5.

The Ember core does not read the log (E-059, still true).
Whether logged conversations may feed long-term memory is
E-072's question and is *not* settled here: today, nothing
in the tree copies log entries into either memory system.

## 5. Retention — how long it is kept

**The logger itself keeps everything indefinitely.** It
has no age limit, no entry limit and no rotation of
`conversation_log.jsonl`; `current.json` lives until the
next `start` replaces it or a delete removes it.

Two system mechanisms, both in the heartbeat and both
*size-based*, bound the files on disk:

- the nerve feed rotates at **10 MB** into a compressed
  archive (`nervous_system.py`'s `MAX_FEED_BYTES`);
- **Bifröst** auto-cleanup prunes `conversation_log.jsonl`
  when it exceeds **50 MB** (and the nerve feed at
  **20 MB**), keeping the newest lines (at least 100), on a
  two-hour cooldown; Mímir's check warns at **50 MB** and
  turns critical at **200 MB**.

That pruning is machine hygiene, not a user right and not
a privacy mechanism. It is oldest-first *by line*, and it
is **not session-aware**: on a very large log it can cut a
long session's earliest lines while keeping its later
ones, and it never touches `current.json`. That gap
between pruning and the law is recorded as **docket 100**,
owned by the E-076 Part IV gate review (session-aware
pruning, or a stated verdict that line-pruning stands).
Nothing else in the tree deletes logged conversations.

**Docket 98 — settled here.** E-059 found the logger's
`_update_current` helper was dead code (defined, never
called) while the `cmd_*` commands each hand-rolled their
own `current.json` merge and diverged: an `event`, `update`
or `end` for session B would rewrite session A's snapshot —
an event would append B's decisions to A's lists, an update
would overwrite A's next actions, and an end would *close
A's snapshot* and build B's closing entry out of A's lists.
The helper is removed, and the merges are now uniform law:

> `current.json` belongs to the session that ran `start`
> most recently. Only that session's own event/update/end
> commands may change it. An entry logged for another
> session is still appended to the log — the log is the
> truth — but it leaves the snapshot alone, and a foreign
> `end` builds its entry from its own arguments alone.
> A missing or ownerless `current.json` counts as owned,
> so a first command behaves exactly as before.

## 6. The user's delete right — total, and provable

The owner of the state dir may delete, at any time, through
the logger's own commands:

```
python3 conversation_logger.py delete --session <id>
python3 conversation_logger.py delete --all --yes
```

Deleting everything requires the extra `--yes`: a session
can be named exactly, "everything" cannot, so the extra
word is the confirmation. `cmd_delete` refuses a `--all`
without it (exit 2) and deletes nothing.

**Total** means across every place the logger's words
live (§3): the session's entries leave
`conversation_log.jsonl`; `current.json` is removed if —
and only if — it belongs to that session; and the
session's `conv_*` copies leave `nerve_feed.jsonl` and
every rotated archive, plain and gzipped. For `--all`, the
log and `current.json` are removed outright and every
`conv_*` copy leaves the feed stores. What is *kept*,
deliberately: other sessions, non-conversation feed events
(heartbeats are not the logger's words), and
**unattributable lines** — lines that are not valid JSON
objects cannot be proven to belong to anyone, so they are
kept and *counted in the report*, never silently dropped
and never silently claimed deleted.

**Provable** means three things, all implemented in
`delete_session` / `delete_all_conversations`:

1. every affected JSONL store is rewritten **atomically**
   (temporary file in the same directory, then
   `os.replace` — a crash mid-delete leaves the old file
   or the new one, never a torn one), preserving kept lines
   byte-for-byte;
2. after the rewrite, the logger **re-reads every store**
   and counts attributable entries remaining for the scope;
3. the report states the numbers — log entries removed,
   whether the current snapshot was removed, nerve copies
   removed, unattributable lines kept, and whether
   verification found **zero** remaining. A deletion whose
   verification fails exits non-zero and does not claim
   success.

Because every reader (§4) reads these same files, a
verified deletion is immediately effective everywhere:
a deleted session no longer appears in `show`, `recent`,
the reactor's input, or an injected context block — the
last of these is exercised by test (§8).

## 7. What this slice did NOT do

- No reader was added or removed; E-072 (the logger as a
  memory source) and E-071 (persona privacy of nerves)
  keep their questions.
- Bifröst's pruning was not rewritten — its non-session-
  aware shape is docket 100 for the E-076 gate, not
  silently changed here.
- No redaction was added to the write path: the law states
  the verbatim fact and the writer's custody rule instead
  of pretending a filter exists.
- One bookkeeping consequence, handled in this slice:
  adding `logger_law.py` and reworking the logger changed
  Verdandi's tracked weight, so the E-057 member budget
  table was re-measured and updated in both published
  copies, as its pinning tests require — Verdandi now
  182 files / 16,871,542 B (was 181 / 16,852,579 B), the
  twelve-member total 131,265,501 B (was 131,246,538 B),
  Verdandi's miss of the laptop ceiling 94,326 B (was
  75,363 B); the re-measure is noted in the E-057 record
  itself. Verdandi's profile verdict is unchanged (none),
  and no RAM floor was re-measured.
  No README touched; no budget-book ceiling moved.

## 8. Conformance — `tests/unit/test_logger_law_e063.py`

Tests pinning, in an isolated state dir with live entries
written by the logger itself:

- the law's shape: version, `EVENT_TYPES` equal to the
  logger's, the four entry kinds, the delete scope naming
  exactly the three stores, the module stdlib-only and
  self-contained;
- the live entries the logger writes carry *exactly* the
  law's field lists, kind by kind;
- retention thresholds equal their sources (Bifröst's
  targets, Mímir's defaults, the hub's rotation constant);
- docket 98: `_update_current` is gone; a cross-session
  event/update/end leaves the owning session's
  `current.json` untouched while the entries themselves
  are still logged, and a foreign end entry carries none
  of another session's lists;
- the delete right: a session deletion removes its log
  entries, spares another session's current snapshot,
  removes its own when it owns it, purges its `conv_*`
  copies from the live feed *and* a plain archive *and* a
  gzipped archive, keeps other sessions, non-conversation
  feed events and corrupt lines (counted, unattributed),
  leaves no temporary file behind, and verifies zero
  remaining; an unknown session deletes nothing and still
  verifies; a deleted session no longer reaches context
  injection; `--all` without `--yes` exits and deletes
  nothing, and with `--yes` is total while keeping
  non-conversation feed events.

## 9. Slice gate

- New conformance suite: `tests/unit/test_logger_law_e063.py`
  — **16 passed**.
- Verdandi focal suites, re-run this slice with the declared
  dev dependency (pytest-asyncio) supplied from the isolated
  e005-extras dir and a short TMPDIR (E-062's socket-path
  discipline): the conversation-layer set (context_injector +
  conversation_logger + reactor + nervous_system) **101
  passed**, exit 0 — identical to E-059/E-061/E-062.
- Root suite gate: Run B **1110 passed, 6 failed, 25 skipped,
  1 warning** (1094 E-062 baseline + 16 new; the 6 are the
  proven environment failures, identical set); Run D
  **1167 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (1151 + 16 — reconciles exactly). Logs in
  `~/workspace/.verify-tmp/ember-e063/gate/`.

*Filed by the E-063 slice, 2026-10-31. Next: E-064 —
stimuli: external events enter as typed stimuli with
provenance.*
