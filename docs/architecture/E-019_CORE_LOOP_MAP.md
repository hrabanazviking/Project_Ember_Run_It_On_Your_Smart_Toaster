# E-019 — The Ember Core Loop, Mapped From Code

*Part II, slice E-019. Method: every statement below was drawn from
the code in `src/ember/` at the slice's starting HEAD, with the
file and symbol named for each step. Where the elder canonical
`docs/architecture/DATA_FLOW.md` disagrees with the code, the code
is the authority here and the disagreement is recorded in §9 —
DATA_FLOW itself was not edited in this slice.*

## 1. Plain-language summary

One conversation turn in Ember is a single synchronous pass,
run by one function. The person types a line; Ember (1) looks the
line up in its Well of stored documents, (2) builds a prompt from
its identity, the last five turns of *this* session, and the best
five matching excerpts, (3) sends that prompt to its one model
backend — today only Ollama is implemented — streaming the reply
back word by word, (4) if the model asks for tools and tools are
switched on, runs them through a validate → approve → execute →
audit loop (at most eight rounds), and (5) saves the turn as an
Episode. There is no event bus, no background work, and no other
member (no Verdandi, no mempalace, no mimir-well) anywhere in this
loop — a tree-wide search for those names in `src/ember/` returns
nothing.

Two honest limits the map exposes, both carried to the docket in
§9: turns are *written* to the Well but never *read back* — a new
session starts with an empty history even though its Episodes are
stored — and a disconnected session's Episodes live only in
memory and are lost when it exits, despite a pending-episodes
journal being promised in the Episode schema's own docstring.

## 2. The core in numbers (measured this slice)

- `src/ember/`: **70 Python files, 11,002 lines** (excluding
  `__pycache__`; inventory in the slice's working notes).
- By area: spark 3,661 · well 2,921 · schemas 1,029 · tools 947 ·
  mcp 839 · config 726 · cli 457 · thread 205 · logging 175 ·
  package root 42.
- The turn itself lives overwhelmingly in one orchestrator:
  `src/ember/spark/munnr/chat.py` (its `run()` plus the streaming
  and tool-loop helpers in the same file). `ask` is not a second
  loop — it is the same loop fed one line (see §3).
- Runtime contract types: `FuniHandle` (`spark/funi/handle.py`),
  `BrunnrHandle` (`well/brunnr/handle.py`), both Protocols;
  adapters are chosen by config value, never by caller code.

## 3. Entry points — how a turn is reached

```
python -m ember            src/ember/__main__.py
ember (console script)     pyproject [project.scripts] → ember.cli.main:main
        │
        ▼
cli/main.py: main()  (argparse only; behaviour lives in spark/munnr)
  1. parse --config-root (default ~/.ember/), --allow-tools / --no-tools
  2. config.load_ember_config(config_root) → EmberConfig
     (ConfigError / OSError → one-line message, exit 1)
  3. apply tool overrides; configure logging from config
  4. first-run gate: for chat/ask, if hjarta.has_identity() is
     false, run the Hjarta setup wizard first, then RELOAD config
  5. dispatch: chat → munnr.chat.run · ask → munnr.ask.run ·
     setup / doctor / well ingest|status / mcp list|tools|ping|serve
```

`munnr/ask.py: run()` builds an in-memory `StringIO(text + "\n")`
and calls `chat.run()` with it — so the one-shot path shares the
REPL's retrieval, rendering, tool-loop, and persistence exactly,
and ends when the fed input reaches EOF.

## 4. Session startup (inside `chat.run()`)

In order, once per process:

1. **Identity.** `load_identity(config_root)` if an identity file
   exists, else `config.identity` (schema defaults: name "Ember",
   role "your small local AI companion").
2. **Embedder constructed.** `OllamaEmbedClient(config.smidja.
   embedding)` (default endpoint `http://localhost:11434/api/embed`,
   model `nomic-embed-text`) — constructed, not probed, here.
3. **Funi opened FIRST.** `spark/funi/handle.open(config.funi)`
   dispatches on `config.funi.runtime`: only `OLLAMA` is wired;
   every other enum value (`llamacpp`, `lmstudio`, `phi_silica`,
   `apple_foundation`) returns `Unavailable(RUNTIME_NOT_INSTALLED)`.
   The Ollama adapter probes `GET {base_url}/api/version` at open;
   failure returns `Unavailable`, and `chat.run()` then prints
   `Funi is unavailable (<reason>): <detail>` and **exits 1
   before the Well is ever opened**.
4. **Well opened SECOND, failure tolerated.** `thread/strengr.
   open(config.strengr, config.brunnr)` wraps
   `well/brunnr/handle.open` (backends: `sqlite_vec`, `pgvector`;
   anything else → `Disconnected(CONFIG_INVALID)`) with retry:
   default 3 attempts, backoff 1s·2ⁿ capped at 30s; CONFIG_INVALID /
   AUTH_FAILED / DNS_FAILURE fast-fail. A `Disconnected` result is
   **not fatal**: a banner is rendered, `brunnr = None`, and the
   session continues ungrounded (§8).
5. **Tools initialised if enabled** (`config.tools.enabled`,
   default **False**): importing `ember.tools` self-registers the
   three first-party tools (`search_well`, `read_local_file`,
   `fetch_url`); `search_well` is bound to the live Well handle;
   the audit log is rooted at `config.tools.audit_root` or
   `<config-root>/state/tool_audit/`.
6. The ready line is printed and the in-memory episode list starts
   **empty** — see §7 for what that means.

## 5. One turn — the streaming path (the default)

`config.funi.streaming` defaults to **True**, so this is the
canonical path. Per input line in the REPL loop:

```
[0] read line from stdin · EOF → exit loop · blank → skip ·
    /exit /quit /q (case-insensitive) → exit loop
[1] started = now(UTC)
[2] RETRIEVE   chat._retrieve(text, brunnr, embedder)
[3] ASSEMBLE   funi/prompt.assemble(identity, last-5 episodes,
               hits, well_disconnected?)
[4] GENERATE   _drive_turn_with_tools → _run_streaming_turn →
               funi.complete_streaming(prompt, context, tools?)
[5] (loop)     if final chunk carries tool_calls and tools are on:
               _run_tool_round per round, ≤ 8 rounds (§6)
[6] RENDER     deltas written live as they arrive; finish tag and
               citations after the body (§7)
[7] PERSIST    Episode built; appended to the in-memory list;
               brunnr.add_episode(episode) if a Well is connected
               (failures suppressed — §8)
[8] loop to [0]; on exit, funi.close() and brunnr.close() each run
    under their own exception suppression
```

### 5.1 Retrieval (`chat._retrieve`, `_DEFAULT_K = 5`)

- No Well → no hits, immediately.
- The line is embedded via the Ollama embed client. **Any**
  exception from embedding degrades to `[None]` (no vector), not
  to an error.
- If a vector comes back and its length equals
  `brunnr.embedding_dim` (default 768): `hybrid_search(qvec, text,
  k=5)`. Otherwise (no vector, wrong dimension): `text_search(
  text, k=5)`.
- A `BrunnrError` from either search degrades to **no hits**. The
  turn then assembles with `well_disconnected=False` and no hits,
  so the prompt takes the "no grounding excerpts available"
  instruction — the operator is not shown a disconnect banner for
  this mid-session retrieval failure (docket 86).

### 5.2 Prompt assembly (`spark/funi/prompt.py: assemble()`)

Runtime-neutral: it returns `list[ContextItem]`, never a
runtime payload. Canonical order, and nothing else is added:

1. One `SYSTEM` item: `You are {name}, {role}.` + the honesty
   instruction ("say so plainly rather than inventing") + exactly
   one grounding branch — disconnected instruction (do not invent,
   name the disconnected Well) / grounded instruction (cite the
   document title) / no-excerpts instruction.
2. One `EPISODE` item per past turn, oldest first, window =
   `episodes[-5:]` (`_DEFAULT_EPISODE_WINDOW = 5`), text shape
   `Past turn:\nOperator: …\nEmber: …`, metadata carries
   `episode_id` only when the Episode has one.
3. One `CHUNK` item per hit, in the search's (best-first) order,
   text shape `From {title}:\n{text}`, metadata `chunk_id`,
   `document_id`, `score`.

The operator's current line is **not** a context item — it travels
separately as the `prompt` argument. There is no token budget, no
summarisation, and no truncation anywhere in assembly: the window
is a fixed count of turns, whatever their length. (That is
E-021's subject; here it is only mapped.)

### 5.3 Generation (`spark/funi/ollama/adapter.py`)

The `FuniHandle` protocol surface is four methods: `complete`,
`complete_streaming`, `health`, `close`; `open()` returns a handle
or an `Unavailable` **value** — it never raises a connection
error. The one implemented adapter, `OllamaFuni`:

- Translates context items to Ollama messages
  (`_messages_from_context`): SYSTEM and CHUNK → `role="system"`;
  EPISODE → a `user`/`assistant` pair parsed from the §5.2 text
  shape (an item that does not parse is silently dropped);
  TOOL_REPLY → `role="tool"` with the tool name from metadata; the
  operator input, if non-empty, is appended last as `role="user"`.
- `POST {base_url}/api/chat`, stdlib `urllib` only, 60s default
  timeout, options = temperature / top_p / num_predict from config.
- Streaming reads NDJSON frames (each capped at 1 MiB — a larger
  frame aborts with a typed ERROR chunk); tool calls accumulate
  across frames and are attached to the final `done` chunk only.
  Errors never raise across the boundary: open-time failure,
  mid-stream death, non-JSON, server `error`, and a stream that
  ends without `done=true` each become one final
  `FuniStreamChunk(done=True, finish_reason=ERROR)`. The
  non-streaming `complete()` folds the same failures into a
  `FuniReply(finish_reason=ERROR)`.

## 6. The tool loop (streaming path only in effect)

Driven by `_drive_turn_with_tools`, bounded by
`_MAX_TOOL_TURNS = 8` iterations per operator input:

1. Run one streaming turn with the tool descriptors (or `None`).
2. If the turn was interrupted (Ctrl-C, §7) → tag the partial text
   and stop. If it carries no `tool_calls`, or tools are off →
   stop; that turn's text is the turn's reply.
3. Otherwise `_run_tool_round` executes **every** call in order:
   lookup (unknown → typed `no such tool` reply) → render proposal
   → validate arguments (invalid → typed reply) → resolve approval
   (descriptor policy vs config overrides vs session-standing set
   vs standing-trust; prompt when required — a prompter failure
   degrades to "n") → execute under the descriptor's own timeout
   via a one-worker `ThreadPoolExecutor` (timeout → typed reply;
   the worker thread itself cannot be killed, and the reply says
   so) → render the reply → audit (an audit-write failure warns on
   stdout but never crashes the loop) → encode the reply as a
   `TOOL_REPLY` context item.
4. Tool replies extend the context; the next iteration runs with
   `current_input = ""` and **no hits/citations** (grounding is a
   first-iteration property). An "always" approval adds the tool
   to the session-standing set for later rounds.
5. Hitting the bound prints `[tool-loop max iterations reached]`;
   the persisted reply is still the **last** turn's text.

Only the final turn's text becomes `Episode.ember_reply`; tool
outputs themselves are audit-log and context material, never
concatenated into the reply.

**Non-streaming path** (`streaming: false`): one
`funi.complete()` call, rendered whole via `render.render_reply`.
Descriptors are passed, but a returned `tool_calls` set is **not
executed and not looped** — the in-code comment says tool use here
is "honoured", the code does not honour it (docket 83).

## 7. Rendering and interruption

All formatting lives in `spark/munnr/render.py`. Streaming:
deltas are written verbatim per chunk; after the body, a finish
tag appears only for LENGTH / REFUSED / ERROR or interruption;
citations (`title (chunk N, score …)`) print after the body and
only when there are hits **and** the Well is connected. Tool
proposals/replies render through ANSI/control-character scrubbing
(`_strip_terminal_controls`); tool output previews are capped at
2 KiB on stdout (full text lives in the audit log).

Ctrl-C during streaming is caught inside `_run_streaming_turn`:
the generator is closed, the partial text is kept and tagged
`[interrupted by operator]` (the tag stands as the whole reply
when nothing was streamed), and the REPL continues with the next
prompt. There is no equivalent interrupt handling around the
non-streaming `complete()` call.

## 8. Persistence, memory, and the sad paths

**What an Episode is** (`schemas/episode.py`): operator input,
reply text, cited chunk ids, model id, `well_disconnected` flag,
start/completion timestamps, optional store id. On the happy path
it is appended to the process-local list (the §5.2 window's only
source) and written via `brunnr.add_episode` — sqlite_vec and
pgvector adapters both implement the insert.

**Sad paths, as coded — not as documented:**

| Case | Behaviour in code |
|---|---|
| Funi unavailable at open | Print reason + detail, exit 1; Well never opened |
| Well disconnected at open | Banner at startup AND before each streaming reply (and in the non-streaming render); prompt carries the do-not-invent instruction; retrieval skipped; Episodes kept in memory only |
| Embedding fails mid-session | Vector silently dropped; text search used instead |
| Search raises `BrunnrError` | Hits silently become none; **no banner** (disconnect flag stays False) |
| `add_episode` fails mid-session | Exception suppressed (`contextlib.suppress(Exception)`); the turn survives in the in-memory window; **no operator warning**; the stored record is silently absent |
| Model errors mid-turn | ERROR finish folded into the reply/chunk (adapter layer), rendered with `[ember reported an error]` |
| Tool loop exceeds 8 rounds | Note printed; last text persisted |
| Approval prompt fails (closed stdin etc.) | Treated as "n" — refusal by default |

**The two structural gaps.** (a) `BrunnrHandle` has `add_episode`
and **no episode-reading method at all** — `mcp/server.py`'s own
comment names this ("has only `add_episode` (write-only). The
reader API is deferred"). The stored Episodes are therefore never
read by any Ember code: history does not survive a restart.
(b) The pending-episodes journal promised by
`schemas/episode.py`'s docstring (`~/.ember/state/
pending_episodes/`, "flushed in on Well recovery") **does not
exist in code** — a tree search finds `pending_episodes` only in
that docstring and one test comment — so a disconnected session's
turns are lost when the process exits.

## 9. Concordance with DATA_FLOW.md + new docket items

DATA_FLOW (ratified 2026-05-21) is the elder canonical flow doc.
It remains true in shape — synchronous, three flows, no event
bus — but its conversation-turn details have drifted from the
code. The code wins; the corrections belong to E-039 / E-194's
doc work, not to silent edits here. Items below are numbered
from 81, continuing the E-016 docket (which closed at 80 and
ruled that defects found in later parts start at 81).

- **81 — Episodes are write-only; no cross-restart history.**
  No episode reader exists on `BrunnrHandle` or in any caller;
  the prompt window is a process-local list. DATA_FLOW §2.1
  step 6 ("last N episodes (read from Well)") is not what the
  code does. → Part II (E-021 / E-031).
- **82 — Pending-episodes journal promised, not implemented.**
  `schemas/episode.py` docstring + DATA_FLOW §2.2 step 9′ vs
  zero implementation; disconnected turns are memory-only and
  lost at exit. → Part II (E-031).
- **83 — Non-streaming tool calls silently dropped.**
  `chat.py`'s non-streaming branch passes descriptors but never
  executes returned `tool_calls`, contradicting its own comment.
  → Part II (E-026 / E-028).
- **84 — DATA_FLOW stale constants and negative space.**
  Retrieval is k=5 in code, k=8 in the doc; the episode window is
  5 (doc: "last N"); §7's "no streaming", "no autonomous tool
  use", and the `AskTurn` parse type in §2.1 step 2 do not match
  the shipped streaming-default, opt-in tool loop, or any type in
  the tree (`AskTurn` appears nowhere in `src/`). → E-039 /
  E-194 doc reconciliation.
- **85 — Episode-persistence failure is silent.**
  `add_episode` exceptions are suppressed with no warning,
  banner, or log line at the chat layer, so a session can believe
  it is remembering when the store is not. → Part II (E-030 /
  E-031).
- **86 — Mid-session retrieval failure is silent.**
  A `BrunnrError` in `_retrieve` yields no hits and no operator
  signal, indistinguishable in the prompt from an honestly empty
  Well (the disconnected banner is reserved for open-time
  failure). → Part II (E-030).

No defect found in this slice was fixed in this slice: E-019 is
the mapping slice; every item above has its fixing home named in
Part II itself, which is the docket rule E-016 established.

## 10. What this map gives the rest of Part II

- E-020 (tethering) starts from §4/§8: the tether today is the
  config root, the identity file, and the Well that is written
  but not read.
- E-021 (conversation hardening) owns §5.2's fixed-count window
  and docket 81.
- E-022 (backend contract) owns §5.3's four-method protocol —
  the contract exists and has exactly one implementation.
- E-025/E-031 own §8's gaps (82, 85); E-026/E-028 own 83;
  E-030 owns 85/86's honesty surface; E-032's day-one flow is
  §3+§4 exactly as drawn.
