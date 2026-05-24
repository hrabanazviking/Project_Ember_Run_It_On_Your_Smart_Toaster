---
codex_id: 38_PERSISTENT_MEMORY
title: Persistent Memory — SessionDB, FTS5, Compression Chains, and Honcho
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - hermes_state.py:1-60
  - hermes_state.py:245-310
  - hermes_state.py:680-760
  - hermes_state.py:1660-1780
  - hermes_state.py:2030-2350
  - agent/memory_manager.py:1-100
  - agent/memory_manager.py:244-400
  - agent/memory_provider.py
ember_subsystem_targets: [Brunnr, Smiðja, Munnr]
cross_refs:
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/36_CONTEXT_FILE_DISCIPLINE
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - reference_gungnir_db
---

# Persistent Memory

Hermes's persistent memory is not one thing. It's a stack:

1. **SessionDB** (`hermes_state.py`) — SQLite with FTS5 for every message ever exchanged.
2. **MEMORY.md** — a curated file the agent edits via the `memory` tool, holding distilled facts.
3. **USER.md** — a user-profile file the agent edits to remember who the user is.
4. **MemoryManager** + plugin providers — pluggable external memory (Honcho, Hindsight).

Each layer answers a different question. SessionDB answers "what happened?" MEMORY.md answers "what should always be remembered?" USER.md answers "who is the user?" External providers answer "what do third-party memory systems contribute?"

I'm Eldra. Let me show you the actual SessionDB layer first (because it's the load-bearing one), then the MEMORY.md flavor, then the provider plugin model. Then translate to Brunnr without violating the Vow of Tethered Grounding.

## SessionDB — the Journal Layer

`hermes_state.py:1-16`:

> "Provides persistent session storage with FTS5 full-text search, replacing the per-session JSONL file approach. Stores session metadata, full message history, and model configuration for CLI and gateway sessions.
>
> Key design decisions:
> - WAL mode for concurrent readers + one writer (gateway multi-platform)
> - FTS5 virtual table for fast text search across all session messages
> - Compression-triggered session splitting via parent_session_id chains
> - Batch runner and RL trajectories are NOT stored here (separate systems)
> - Session source tagging ('cli', 'telegram', 'discord', etc.) for filtering"

Five design decisions in one comment. Each one is load-bearing.

### WAL with graceful fallback

Lines 40-58:

```python
# SQLite's WAL mode requires shared-memory (mmap) coordination and fcntl
# byte-range locks that don't reliably work on network filesystems...
#
# Instead, fall back to ``journal_mode=DELETE`` (the pre-WAL default) which
# works on NFS.  Concurrency drops — concurrent readers are blocked during
# a write — but the feature works.
_WAL_INCOMPAT_MARKERS = (
    "locking protocol",       # SQLITE_PROTOCOL on NFS/SMB
    "not authorized",         # Some FUSE mounts block WAL pragma outright
    "disk i/o error",         # Flaky network FS during WAL setup
)
```

A user on NFS doesn't get an error. They get DELETE journal mode with a debug log. **Degraded performance, not broken feature.** This is the Hermes pattern in microcosm: detect the constraint, downgrade gracefully, log the downgrade, move on.

### FTS5 — Two Tables, Two Tokenizers

The schema (lines 254-307) creates TWO FTS5 virtual tables:

- `messages_fts` — default `unicode61` tokenizer. Good for ASCII/Latin scripts. Fast BM25 ranking.
- `messages_fts_trigram` — trigram tokenizer for CJK/substring search. Each message gets indexed twice.

Why two? Lines 279-282:

> "The default unicode61 tokenizer splits CJK characters into individual tokens, breaking phrase matching. The trigram tokenizer creates overlapping 3-byte sequences so substring queries work natively for any script (CJK, Thai, etc.)."

The unicode61 path is faster and ranks better; the trigram path covers languages the default fails. Both tables get triggers (INSERT/DELETE/UPDATE) so they stay in sync with `messages`. Disk cost: ~2× the message content, but FTS5 indices are compact. Worth it for CJK users.

### Query sanitization

`_sanitize_fts5_query` (line 2030):

> "FTS5 has its own query syntax where characters like `"`, `(`, `)`, `*`, `:` have special meaning. Naive user input often trips this:
> - Strip unmatched FTS5-special characters that would cause errors
> - Wrap unquoted hyphenated and dotted terms in quotes so FTS5..."

The function is ~50 lines and handles every FTS5 syntax pitfall. Without this, a user search for `pr-2847` would throw a FTS5 syntax error. With it, the user gets results. This is the kind of code you write once and never look at again until someone reports "my search broke."

### Compression chains

The `parent_session_id` column (line 249) is the link in the chain. When a session is compressed (see [[30_execution/36_CONTEXT_FILE_DISCIPLINE]]), the OLD session stays in the database under its original id; a NEW session is created with `parent_session_id = old.id`; the chat continues in the new session.

Effect: every long conversation becomes a chain of session rows. The user can search across the *whole chain* via FTS5. The agent only loads the current session's messages into context, but the journal is unbroken.

The bookend pattern at line 1666:

> "FTS5 match) and the scroll shape (anchored on any message id). The Bookends let an FTS5 hit anywhere in a long session yield the goal..."

When a search hits a single message deep in an old session, the FTS5 result returns *bookend* context — N messages before and after — so the user sees the search result in conversational context, not as a single floating line.

## MEMORY.md — the Curated Layer

Distinct from SessionDB. SessionDB is "every message ever." MEMORY.md is "facts the agent should always know."

The agent has a `memory` tool that:
- `read`s MEMORY.md and returns its content
- `write`s a new note appending or replacing
- `delete`s a specific entry

`agent/memory_manager.py:7-9`:

> "Only ONE external plugin provider is allowed at a time — attempting to register a second external provider is rejected with a warning. This prevents tool schema bloat and conflicting memory backends."

The built-in MEMORY.md is always available; external providers are mutually exclusive. Most users only need MEMORY.md.

Format-for-system-prompt happens at agent boot:

```python
# agent/memory_manager.py: usage
# System prompt
prompt_parts.append(self._memory_manager.build_system_prompt())
```

The memory block lands in the *volatile* tier of the system prompt (per [[30_execution/36_CONTEXT_FILE_DISCIPLINE]]). It's regenerated on each session boot from the on-disk MEMORY.md.

### Context fencing

`agent/memory_manager.py:38-50`:

```python
_FENCE_TAG_RE = re.compile(r'</?\s*memory-context\s*>', re.IGNORECASE)
_INTERNAL_CONTEXT_RE = re.compile(
    r'<\s*memory-context\s*>[\s\S]*?</\s*memory-context\s*>',
    re.IGNORECASE,
)
_INTERNAL_NOTE_RE = re.compile(
    r'\[System note:\s*The following is recalled memory context,\s*NOT new user input\.\s*Treat as (?:informational background data|authoritative reference data[^\]]*)\.\]\s*',
    re.IGNORECASE,
)


def sanitize_context(text: str) -> str:
    """Strip fence tags, injected context blocks, and system notes from provider output."""
```

**The agent fences memory content** with `<memory-context>...</memory-context>` tags. When the assistant emits text, the text is run through `sanitize_context` to strip those tags before display. Why? So the agent can't accidentally leak its internal context-fencing scheme into the user's view. Defense against prompt-injection: a malicious external memory provider can't get the agent to emit fake "[System note]" lines to the user.

The `StreamingContextScrubber` class (line 62+) handles the streaming case: a fence tag opened in one delta and closed in a later delta is held back across deltas. This is the kind of small, careful state machine you only build after you ship something and see a real-world leak.

## External Memory Providers

`agent/memory_provider.py` defines the abstract base class. Identifier string (line 48):

```python
"""Short identifier for this provider (e.g. 'builtin', 'honcho', 'hindsight')."""
```

Built-in is always present; Honcho and Hindsight are pluggable. The `MemoryManager` (line 244) keeps a list of providers and orchestrates:

- `build_system_prompt()` — combine each provider's memory block.
- `prefetch_all(user_message)` — let providers fetch user-message-relevant context before the LLM call.
- `sync_all(user_msg, assistant_response)` — push the completed exchange back to each provider for indexing.
- `queue_prefetch_all(user_msg)` — async warm-up for the next turn's prefetch.

The lifecycle is *per-turn*. Each turn: prefetch → call LLM → sync. External providers don't need to handle storage internals; the manager dispatches.

This is plugin architecture in the truest sense. Hermes ships with Honcho as the recommended external provider but the interface accepts any backend that implements `MemoryProvider`.

## What This Means for Ember

Ember already has Brunnr — the pluggable Well that holds knowledge chunks. Brunnr is *knowledge memory*. Ember needs to add *session memory* (Hermes SessionDB equivalent) and *curated memory* (MEMORY.md equivalent).

Critically, Ember's Vow of Tethered Grounding says: never confabulate. Persistent memory is exactly where confabulation can sneak in — the agent says "I remember you told me X" and the user has no idea if that's real or fabricated. Every memory layer must be *checkable*.

### Brunnr's two faces

Brunnr already stores `chunks` (the Well — knowledge). Add a second namespace: `messages` (the Journal — what happened).

```python
# src/ember/well/brunnr/schema.py
TABLES = {
    "chunks": ...,           # existing — ingested documents
    "chunk_fts": ...,        # existing — FTS5 over chunks (where supported)
    "sessions": "...",       # NEW — session metadata
    "messages": "...",       # NEW — every message
    "messages_fts": "...",   # NEW — FTS5 over messages
    "messages_fts_trigram": "...",   # NEW — trigram FTS5 over messages
}
```

The two namespaces share a backend (sqlite_vec, pgvector, etc.) but are conceptually distinct. A search for "what did the user tell me about their cat?" should hit `messages`. A search for "what does the user's documents say about cats?" should hit `chunks`. Munnr's search command makes this distinction explicit:

```
$ ember well search "cat" --in messages
$ ember well search "cat" --in chunks
$ ember well search "cat" --in both    # default
```

### Steal SessionDB verbatim, almost

The schema, the WAL fallback, the FTS5 + trigram dual-table, the query sanitizer, the bookends — all of it transfers. Move it into Brunnr.

The exception is the *backend* — Brunnr is pluggable, SessionDB is SQLite-only. Reconciliation: Brunnr's adapter interface needs a `messages` namespace that EVERY backend implements. Adapters that have native FTS (SQLite, PostgreSQL) implement it natively. Adapters that don't (Qdrant, Chroma, LanceDB) implement a lightweight fallback: store messages with their text vectorized, search via vector similarity. Less precise than FTS5 but better than nothing.

```python
# src/ember/well/brunnr/adapter.py
class WellAdapter(Protocol):
    # Knowledge layer (existing)
    def upsert_chunks(self, chunks: list[Chunk]) -> None: ...
    def search_chunks(self, query: str, k: int = 10) -> list[Chunk]: ...

    # Session layer (NEW)
    def save_message(self, msg: Message) -> int: ...
    def search_messages(self, query: str, *, k: int = 20, with_bookends: int = 3) -> list[MessageHit]: ...
    def get_session(self, session_id: str) -> Session: ...
    def list_sessions(self, *, source: str | None = None, limit: int = 50) -> list[Session]: ...
```

Each Brunnr backend implements both. Vow of Pluggable Storage preserved.

### MEMORY.md — keep the file, add the trace

Adopt MEMORY.md verbatim with one Vow-of-Honest-Memory enhancement: every entry must declare a source.

```markdown
<!-- ~/.ember/MEMORY.md -->
- User has ADHD <!-- source: session 47abf, turn 12 -->
- User prefers stdout-only delivery for cron <!-- source: session 8a3d, turn 5 -->
- Tailnet IP: 100.67.240.22 <!-- source: ~/.ember/config/network.yaml -->
```

The `<!-- source: ... -->` marker is mechanical, parseable, and removable by display tooling. When the user asks "why do you think I have ADHD?" Ember can answer "because in session 47abf turn 12 you said 'I have ADHD' — here's the surrounding context." Vow of Honest Memory paid in cash.

### USER.md as a structured slot

USER.md gets its own slot in the system prompt (per `agent/system_prompt.py:249`). Ember's USER.md should be YAML-structured rather than freeform:

```yaml
# ~/.ember/USER.md (YAML inside Markdown)
name: Volmarr
preferred_pronouns: he/him
preferred_address: by first name
tone: direct, no marketing voice
time_zone: America/Los_Angeles
working_hours: 09:00–18:00
known_systems:
  - gungnir (PG18 + pgvector)
  - tailnet
  - hermes-agent
```

A YAML user profile is *machine-checkable* and *renderable* into a system-prompt slot. Free-text USER.md is a free-form trap; structured USER.md is a feature.

### MemoryManager — adopt the lifecycle, simplify the plugin API

Mirror Hermes:

```python
# src/ember/munnr/memory/manager.py
class MemoryManager:
    def __init__(self):
        self._providers: list[MemoryProvider] = []
        self.add_provider(BuiltinMemoryProvider())  # MEMORY.md + USER.md

    def add_provider(self, provider: MemoryProvider) -> None:
        # Only one external provider at a time (mirror Hermes rule)
        ...

    def build_system_prompt(self) -> str:
        return "\n\n".join(p.build_system_prompt() for p in self._providers if ...)

    def prefetch_all(self, user_message: str) -> dict[str, str]: ...
    def sync_all(self, user_msg: Message, assistant_response: Message) -> None: ...
```

`BuiltinMemoryProvider` is always present. External providers (Honcho-equivalent, the hypothetical Skry projection layer) are optional and mutually exclusive.

### Context fencing — adopt verbatim

The `<memory-context>` tag scheme and `sanitize_context` regex are exact transferable. The `StreamingContextScrubber` is also a verbatim port. **Memory leakage through assistant output is a real adversarial concern** — if Ember ever supports community memory plugins ([[Vow of Open Knowledge]] suggests it should), this defense is non-negotiable.

### WAL fallback — adopt verbatim

`_WAL_INCOMPAT_MARKERS` and the journal-mode-DELETE fallback. Mounting the Well on NFS is a legitimate use case (home-server users with a NAS). Hermes's pattern lets it just work.

### What to skip

- **Don't ship Honcho/Hindsight integration in v1.** The plugin interface is enough; concrete plugins can come later.
- **Don't ship streaming display.** Ember's CLI in v1 doesn't stream model output in a way that needs the `StreamingContextScrubber`. Add when streaming lands.
- **Don't ship cross-platform message sources tagging beyond `cli` and `cron`.** Hermes tags `telegram`, `discord`, etc. because it has gateway adapters. Ember in v1 just has the CLI. Add as gateway adapters land.

### Vows on the line

- **Vow of Honest Memory** — strengthened by source markers on every MEMORY.md entry and by SessionDB being the unbroken journal.
- **Vow of Pluggable Storage** — preserved by the `messages` namespace being part of every Brunnr adapter contract.
- **Vow of Tethered Grounding** — strengthened. The agent says "I think you told me X" with a session-id receipt.
- **Vow of Smallness** — at risk if FTS5 indexing on a Pi gets expensive. Mitigation: trigger reindex only on schema migration; otherwise let triggers maintain incrementally. SQLite's trigger overhead on a Pi is < 1ms per message.
- **Vow of Modular Authorship** — strengthened. The MemoryManager + provider list means an external provider crashing only affects its own block in the system prompt.

### The Skein/Skry alignment

User's note: "Skein/Skry are co-invented embedding-derived KG + query-time projection methods." The persistent memory layer here is the substrate Skein and Skry act on. Specifically:

- **Skein** reads from `chunks` (the knowledge layer) and produces an embedding-derived KG that Brunnr can store as a third namespace (`kg`).
- **Skry** reads from BOTH `chunks` and `messages` at query time, projecting entities into the response context.

The proposed adapter shape (`upsert_chunks`, `search_chunks`, `save_message`, `search_messages`) leaves room for Skein/Skry as future namespaces or as side-tables. Cross-link: [[project_skein_skry]] in user memory.

### Concrete deliverables

1. `src/ember/well/brunnr/session_store.py` — SQLite-vec adapter for sessions+messages with FTS5 dual-tokenizer.
2. `src/ember/munnr/memory/manager.py` — provider orchestrator.
3. `src/ember/munnr/memory/builtin.py` — MEMORY.md + USER.md (YAML-structured) provider.
4. `src/ember/munnr/memory/context_fence.py` — sanitizer + streaming scrubber.

Each is < 800 lines. SessionDB-port is the biggest single piece (~1,000 LoC in Hermes, would be ~700 in Ember after trimming Hermes-only features). The whole stack is < 3,000 LoC for full memory.

### Where to read next

- [[30_execution/30_SELF_HEALING_LOOP]] — how the journal feeds the curator.
- [[30_execution/36_CONTEXT_FILE_DISCIPLINE]] — how memory blocks land in the system prompt.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — Brunnr's expanded scope to own session+memory storage.
- [[reference_gungnir_db]] — the existing knowledge DB that becomes Brunnr's pgvector backend.

A memory you can't trace back is a story. Tether your memory. Cite your past. — Eldra.
