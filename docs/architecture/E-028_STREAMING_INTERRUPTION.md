# E-028 — Streaming + interruption: talked over, state stays coherent

Roadmap slice E-028 (Part II): *"Streaming + interruption: the
companion can be talked over; state stays coherent."*

## 1. Where the companion could be talked over — before E-028

Phase 11 (ADR 0009 part 2) built exactly one interrupt path:
`KeyboardInterrupt` raised while iterating a streaming reply was
caught in `_run_streaming_turn`, the partial reply was tagged
`[interrupted by operator]`, persisted as the Episode, and the REPL
continued. Every *other* place the companion waits had no guard —
Ctrl-C there propagated out of `chat.run()`, killing the session
and losing the turn entirely:

| Waiting point | Before E-028 |
|---|---|
| Mid-stream iteration | ✅ partial tagged, persisted, session lives (Phase 11) |
| At the REPL prompt (`stdin.readline()`) | ❌ session died |
| During retrieval (embed / Well search) | ❌ session died |
| Creating the stream (adapter work before the iterator exists) | ❌ session died |
| At a tool-approval prompt | ❌ session died, turn lost |
| During tool execution | ❌ session died, turn lost |
| Inside non-streaming `complete()` | ❌ session died, turn lost |

A companion for normal folks on tiny hardware gets talked over
constantly — a slow local model is exactly when a person reaches
for Ctrl-C. Losing the whole session (and the conversation's last
turn) for that one keypress is the opposite of the project's shape.

## 2. The E-028 interruption contract

One rule, applied at every waiting point:

> **Ctrl-C ends the current thing, never the session, and never
> silently.** What was already said or done stands; what was in
> flight is named as interrupted; the session continues at the
> next prompt.

Point by point, as implemented in `src/ember/spark/munnr/chat.py`:

- **At the prompt** — `readline()`'s `KeyboardInterrupt` re-prompts.
  Leaving is `/exit` or EOF, never an accidental interrupt.
- **During retrieval** — the turn is *abandoned*: no reply ever
  existed, so nothing is persisted (a tag-only Episode for a turn
  the operator stopped before the companion spoke would pollute
  the persona's history with turns that never happened). The tag
  is shown on stdout and the session continues.
- **Mid-stream** — unchanged Phase 11 shape: partial text +
  `[interrupted by operator]`, persisted, session continues.
  E-028 additionally moves *stream creation* inside the guard, so
  an adapter that blocks or raises before returning its iterator
  produces the same interrupted turn (tag-only partial).
- **At a tool-approval prompt** — `KeyboardInterrupt` is
  deliberately NOT folded into `_safe_prompt`'s degrade-to-"n"
  handling: Ctrl-C there talks over the *whole turn*, not one
  call. It propagates to the turn driver, which ends the turn:
  no call executes, no follow-up generation runs, the already
  streamed text is persisted with the tag.
- **During tool execution** — same driver handling. Calls in the
  round that already completed stand (each was emitted and
  audited as it completed); the interrupted call and every later
  call in the round never run; the partial is persisted tagged.
- **Inside non-streaming `complete()`** — the new non-streaming
  driver (below) returns the last reply (or None) marked
  interrupted; the caller persists its text with the tag (tag-only
  when nothing had returned) and the session continues.

State coherence, stated plainly: an Episode is persisted for every
turn in which a reply was in flight, always with the tag when the
operator stopped it; session-standing approvals granted *before*
the interrupt stand (they were completed operator acts); no tool
executes after the interrupt; the Well/Funi handles stay open and
are closed only by the normal session end.

## 3. Docket 83 CLOSED — non-streaming tool calls are executed

E-019 found it and assigned it to E-026/E-028: the non-streaming
branch passed tool descriptors to `complete()` and then silently
dropped any returned `tool_calls`, while its own comment claimed
they were "honoured". The same drop existed in
`wrap_complete_as_stream`, which built its single final chunk
without the reply's `tool_calls` — disarming the tool loop for
every WRAPPED backend (E-022's contract shape).

E-028 fixes both ends:

- `wrap_complete_as_stream` (`src/ember/spark/funi/handle.py`) now
  carries `reply.tool_calls` into the final chunk.
- The non-streaming chat branch now drives
  `_drive_complete_turn_with_tools`: a reply carrying tool calls
  runs the same propose → approve → execute → feedback round as
  the streaming driver (`_run_tool_round`, unchanged), tool
  replies return as context, the follow-up `complete("")` produces
  the summarising reply, and the loop is bounded by the same
  `_MAX_TOOL_TURNS` (8) with the same on-screen cap note. A
  non-final reply carrying both text and calls is rendered before
  its round runs — mirroring what a streaming operator already
  saw live. The persisted Episode is the final reply's text, as
  on the streaming path.

The non-streaming mode's purpose is unchanged — one blob per turn
for piped callers; it just no longer amputates tool use.

## 4. What was NOT changed

- The Phase 11 mid-stream shape, tag text, and render helpers are
  untouched; their tests stand unmodified.
- `_safe_prompt`'s IO-error degradation (closed stdin → "n") is
  unchanged; only `KeyboardInterrupt` is excepted, by design.
- Tool execution timeouts, approval gating (E-026), and the plain
  approval wording (E-027) are untouched.
- No new dependencies; stdlib only. Budget: the slice adds no
  runtime cost to an uninterrupted turn beyond one extra function
  call per non-streaming turn.

## 5. Tests

New: `tests/unit/test_streaming_interruption_e028.py` — **9 passed**
(prompt re-prompt; retrieval abandonment with nothing persisted;
approval-prompt interrupt — nothing executed, partial tagged;
execution interrupt — first call attempted, second never runs,
partial tagged; non-streaming tool loop end-to-end with the tool
reply in the follow-up context; non-streaming interrupt inside
`complete()` — tag-only episode, next turn normal; plain
non-streaming reply unchanged; wrapped-stream tool-call carriage;
stream-creation interrupt).

Existing Phase 11 streaming and Phase 16 tool-loop suites re-run
unmodified and green.

Slice gate (E-017 method): Run B (default env, pgvector file
excluded) **755 passed, 6 failed, 13 skipped, 1 warning** — the
746 E-027 baseline + the 9 new tests; Run D (whole suite, extras
supplied) **796 passed, 0 failed, 19 skipped, 1 warning**, exit 0.
The 6 Run B failures are the proven environment failures of the
E-017 freeze (FTS5 sanitisers ×3, pgvector text search ×2,
sqlite_vec cross-thread ×1 — all `sqlite_vec` absence), unchanged.

## 6. Honest limits

- A tool executor running in its worker thread cannot be killed
  mid-flight (the pre-existing `_execute_with_timeout` truth):
  Ctrl-C ends the *turn* coherently, but a runaway tool's thread
  may finish in the background, exactly as a timed-out tool's may.
  Its result is discarded — never audited as a completed call,
  never fed to the model.
- Interruption during the brief prompt-assembly/windowing step
  (pure local computation, no waiting) is not separately guarded;
  there is no wait there to talk over.
- `ember ask` rides `chat.run`, so a Ctrl-C during its single turn
  ends the turn interrupted and the process then reaches EOF and
  exits 0 with the tagged Episode persisted — the same coherence,
  one-shot shaped.
