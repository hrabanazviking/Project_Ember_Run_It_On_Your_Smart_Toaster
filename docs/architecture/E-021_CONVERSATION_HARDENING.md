# E-021 — Conversation engine hardening

*Slice E-021 of the Project Ember roadmap (Part II). What changed,
what it proves, and what remains open — all claims drawn from the
code and the test runner of this slice.*

## The problem, as E-019/E-020 left it

- History was `episodes[-5:]` in `chat.py`: a fixed count of the
  current process's turns, no token budget, no record of what was
  dropped.
- Episodes were **write-only** in the Well (docket 81): both adapters
  implemented `add_episode`, neither had a reader, so no conversation
  survived a restart. E-020's tethering spec named this honestly as
  its centre (T-W6).
- There was no summarisation anywhere: a long conversation simply
  fell off the back of the 5-episode window.

## What this slice builds

### 1. The episode reader (docket 81 — closed)

`BrunnrHandle` gains `recent_episodes(limit) -> list[Episode]`
(newest `limit`, oldest first), implemented in both adapters:

- sqlite_vec: `SELECT … ORDER BY id DESC LIMIT ?`, rows reversed,
  errors wrapped in `BrunnrError`, cited ids / timestamps parsed back
  into the `Episode` schema.
- pgvector: the same shape against the qualified `episodes` table,
  `cited_chunk_ids::text` parsed defensively (string or sequence).

`chat.run()` loads up to 64 stored episodes at startup when the Well
is connected; a failing reader degrades to in-session history only
(suppressed like retrieval failure — the session never crashes over
history). MCP's stale "write-only" note in `mcp/server.py` is
corrected; exposing the reader as an MCP tool/resource stays V2.

### 2. Windowing under a profile-aware token budget

New module `ember.spark.funi.windowing`:

- `estimate_tokens(text)` — ceil(chars / 4), the cheap deterministic
  guardrail (a budget, not a billing meter).
- `window_history(episodes, config, summariser=None)` — applies the
  episode cap first (newest kept), then walks newest → oldest keeping
  episodes while the cumulative estimate fits the token budget. The
  newest episode is **always** kept, even over budget. Everything
  not kept is returned in `dropped` — trimming is never silent in
  the data, even before summarisation.
- The budget is profile-aware via the new
  `ConversationConfig` (`ember.schemas.config`): profiles
  `toaster` 512 tokens / 3 episodes, `phone` 1024 / 5, `pi`
  2048 / 8 (the default), `laptop` 4096 / 12 — names per Part III's
  E-041 preview; explicit `token_budget` / `max_episodes` overrides
  win. The section loads from the operator config file through the
  generic coercion loader like every other section. The budget
  covers episode history only; system prompt, grounding hits, and
  the current line assemble outside it.

### 3. Summarisation hooks

`Summariser` is a protocol: dropped episodes in, summary text out.
The default `ExtractiveSummariser` is deterministic and model-free
(a toaster cannot afford a second inference to summarise the first):
it counts the dropped turns and quotes verbatim snippets of each,
capped at 600 chars. A model-backed summariser can implement the
same protocol later without caller changes. When summarisation is
enabled (`ConversationConfig.summarise_dropped`, default on) and
turns were dropped, the summary rides in the prompt as a new
`ContextKind.SUMMARY` item — placed by `prompt.assemble()` between
the system item and the kept episodes, and carried by the Ollama
adapter as a `role="system"` message. `test_schemas_funi`'s pinned
kind set was updated with attribution, following the Phase 16
precedent for `tool_reply`.

### 4. The chat loop

Per turn, `chat.run()` now windows the full known history (loaded +
this session's) through `window_history` with
`config.conversation`, replacing the fixed `[-5:]` slice.
`ember ask` inherits all of it through `chat.run`.

## Honest limits / what this slice does not do

- **Docket 82 stays open for E-031**: turns from a session whose
  Well was disconnected are still not journalled locally — there is
  no pending-episodes journal yet. E-021 closes cross-restart
  history for connected sessions only.
- Docket 85/86 (silent persistence / retrieval failures) keep their
  E-030 home; the startup history load follows the same
  degrade-quietly shape for now.
- Token counts are estimates by design; backends that report real
  `prompt_tokens` remain the truth for measurement (Part III).
- Session persistence proper (atomic writes, corruption fixtures)
  is E-031; multi-conversation isolation is E-035. History loaded
  here is the Well's single episode stream, as stored today.

## Proof (runner counts only)

- `tests/unit/test_conversation_e021.py` — **15 passed** in the
  default env: profile table + overrides + TOML loading, estimator,
  cap / budget / newest-always-kept / disabled / custom-hook
  windowing, extractive-hook honesty, prompt placement, Ollama
  carriage, chat startup loading + tiny-budget windowing (fake
  handle/funi seams).
- `tests/unit/test_episode_reader_e021.py` — **4 passed** with
  extras (real sqlite_vec adapter: round-trip oldest-first, limit
  keeps newest, restart reopen, closed-handle typed error); skips
  honestly in the default env.
- Slice gate (E-017 Run B shape): **574 passed, 6 failed, 13
  skipped, 1 warning** — the 559 E-020 baseline + 15 new; the 6
  failures are the proven environment failures, identical to the
  freeze. Run D (whole suite, extras supplied): **615 passed,
  0 failed, 19 skipped, 1 warning**, exit 0.
- User docs updated in scope: the Operator Playbook's two
  "conversations are not read back" statements (Recipe 10 and the
  tethering section) now state the E-021 behaviour and the remaining
  disconnected-session limit. E-020's spec is not rewritten — T-W6
  stands as the record of what was true then; this doc is its
  closing note.
