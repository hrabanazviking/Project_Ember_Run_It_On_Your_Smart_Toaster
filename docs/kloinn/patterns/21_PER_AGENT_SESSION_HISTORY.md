# 21 — Per-Agent Session History

OpenClaw's session management — each agent has its own session
history, separate from other agents.

---

## The pattern

A *session* in OpenClaw is one continuous conversation thread.
Each agent maintains a list of sessions. Operators can:

- `/new` — start a new session.
- `/sessions list` — list past sessions.
- `/sessions history <id>` — read a past session.
- `/sessions send <id>` — append to a specific session.
- `/reset` — clear the current session.

History persists per-agent: the work agent's sessions are not
the personal agent's sessions.

---

## What sessions track

Each session record contains:

- Session ID.
- Timestamp range (started, last activity).
- Title (auto-generated or operator-set).
- Full message history.
- Tool calls + their results.
- Optionally: tags, notes, references.

This is *richer* than just chat-log files. Sessions are
*structured objects*.

---

## Why this is good

### 1. Conversation continuity

Operator pauses; resumes hours later; can resume the *specific*
conversation, not just "what I last said."

### 2. Multiple parallel threads

Operator's brain can hold N threads. The system can too.
"That research session is paused; I'll work on this code session
for an hour."

### 3. Auditable record

Every session is an audit-able record of operator-AI interaction.
For sensitive work, this matters.

### 4. Replay-able

Operators can revisit. "What did the AI say about X three days
ago?"

### 5. Searchable

If sessions are stored well, operators can grep / search across
all past sessions for "all the times we discussed Y."

---

## Ember's current state

Ember has **Episodes** — operator turns + agent replies
persisted to the Well. They're more granular than sessions (each
turn is its own record).

What Ember lacks:
- **Session boundaries**: when one conversation ends and another
  begins.
- **Session-level metadata**: titles, tags, summaries.
- **Session-level navigation**: `/sessions list`.

---

## What Ember should adopt

🟢 **Adapt to Ember Vows**:

### 1. Session boundaries

A *session* is bounded by:
- Explicit `/new` command from operator.
- Long idle time (e.g., > 4 hours) auto-closes.
- Explicit `/end` from operator.

Episodes belonging to a session reference its session ID.

### 2. Session-level CLI commands

```
/new                  # start new session
/sessions list        # list recent sessions
/sessions show <id>   # show a session's history
/sessions resume <id> # resume that session
/sessions rename <id> <title>  # name it
/reset                # clear current session (don't end; just forget)
/end                  # end current session (boundary)
```

Stofa can render these as a side panel (Episode Browser).

### 3. Auto-generated titles

After the first 2-3 turns of a new session, Ember auto-generates
a title from the topic. Operator can rename.

Example: a session about Norse cosmology + Odin → title "Odin's
mythology research."

### 4. Per-session summaries (longer term)

After a session ends, generate a short summary stored with the
session. Useful for recall.

---

## How sessions interact with the Well

A session is *not* the Well. The Well stores documents the
operator ingested + retrievable knowledge. The session stores
*the conversation*.

Both feed each other:
- The session can reference Well chunks (via citations).
- The Well can be augmented from sessions (operator might ask
  "save this session as a Well doc").

Sessions and Wells *complement* each other. Both persist.

---

## Storage shape

Add to `~/.ember/state/`:

```
sessions/
  2026-05-22T14-12-00_uuid/
    metadata.json
    episodes/
      00001_operator.json
      00002_ember.json
      ...
    summary.md          # generated after end
  2026-05-21T08-30-00_uuid/
    ...
```

Sessions are *directories* with metadata + messages. Greppable
from disk; restorable; backup-friendly.

---

## Session storage in Mímir

Optionally: each ended session can be *ingested into Mímir* as
documents. This makes sessions searchable as part of the Well
(via Brunnr).

Operator opts in: `sessions.ingest_on_end: true`.

When true: Ember asks "save this session for future recall? (y/n)"
on `/end`. If yes, summary + session text become Well documents.

---

## Privacy: per-session

Some operators want session granularity for privacy:

- **Default**: sessions persist locally.
- **Ephemeral session**: `/new --ephemeral` — doesn't persist.
  Useful for sensitive conversations.
- **Auto-delete**: `/sessions auto_delete_after_days: 30` —
  housekeeping.

The flexibility is operator-facing. Defaults: persist forever
locally; never share.

---

## Cross-session awareness

Per Yggdrasil's awareness layer: Ember sometimes notices
patterns *across sessions*. "You've been asking about X over
multiple sessions."

This requires sessions to be queryable. The storage shape above
supports this.

---

## Per-session sandbox / tool policy

OpenClaw allows per-session sandbox config. Ember could mirror:

```
/new --sandbox=strict
```

Starts a session where *all* tool calls require approval, with
narrowest sandbox. Useful when working with new tools or
operator-untrusted contexts.

```
/new --sandbox=trusted
```

Starts a session where tools auto-approve (STANDING). Useful
for routine work.

Defaults from `ember.yaml`.

---

## Configuration shape

```yaml
ember:
  sessions:
    enabled: true
    storage_path: ~/.ember/state/sessions/
    auto_close_idle_minutes: 240    # 4 hours
    auto_title:
      enabled: true
      after_turns: 3
      model: funi                    # use Ember's own LLM
    auto_summary:
      enabled: true
      on_end: true
    ingest_on_end:
      enabled: false                 # opt-in
      ask_operator: true
    retention:
      keep_indefinitely: true
      operator_can_delete: true
```

---

## What sessions don't replace

Sessions are *one organizational layer*. They don't replace:

- **Episodes**: individual turn records (sessions are made *of*
  episodes).
- **The Well**: knowledge base (separate concept).
- **Mímir's decay**: tracks chunk relevance (orthogonal).
- **Awareness**: real-time event analysis (orthogonal).

Sessions add *bounded conversation threads*. That's it.

---

## What if operator never uses /new?

Then everything is one giant session. No harm, but no benefit
either.

Auto-close on idle ensures eventual session boundaries even
without operator command.

For operators who *do* use `/new`: rich session management.

For operators who *don't*: graceful default behavior.

---

## Closing

Per-Agent Session History is **OpenClaw's conversation-thread
management**. Bounded sessions; per-agent isolation; replay-able
records.

Ember should:
- 🟢 Adopt session boundaries (via `/new`, `/end`, auto-idle).
- 🟢 Add session-level CLI commands.
- 🟢 Auto-generate titles + summaries.
- 🟢 Make sessions ingestable into Well (opt-in).
- 🔵 Borrow per-session sandbox config.

This is a Phase 2 Klóinn adoption — adds clear UX value, fits
existing Episode infrastructure.

The conversation has *shape*; sessions make the shape visible
+ manageable.
