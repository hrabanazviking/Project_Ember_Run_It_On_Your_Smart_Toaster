# `ember.spark.munnr/` — Munnr

**The command-line surface — where Ember is summoned.** Munnr is the
operator's entry point: it routes arguments, drives the chat REPL,
renders every terminal output line, and orchestrates the slice-2 tool
loop. Behaviour lives in the other realms; Munnr is the conductor.

**Shipped:** Phase 6, slice 1 (version 0.1.0). Extended Phase 11
(streaming consumer + Ctrl-C tagging) and Phase 16 (tool loop +
approval-prompt integration).
**Reads with:** `INTERFACE.md` for the public surface; `docs/architecture/DATA_FLOW.md` §2-3 for the turn + ingest flows; `docs/architecture/DOMAIN_MAP.md` §7 for ownership.

---

## What this subpackage owns

The thin router + the orchestrator + the render layer:

| Module | What's in it |
|---|---|
| `chat.py` | The `ember chat` REPL loop. Streaming consumer (Phase 11). Tool loop (Phase 16) — propose→approve→execute→audit→feedback, bounded by `_MAX_TOOL_TURNS=8`. |
| `ask.py` | `ember ask "..."` — one-shot ask. Mostly a chat.run wrapper with `StringIO` stdin. |
| `ingest.py` | `ember well ingest <path>` — Smiðja wrapper. |
| `status.py` | `ember well status` — counts + health. |
| `doctor.py` | `ember doctor` — diagnostics across all realms. |
| `setup.py` | `ember setup --reset` — re-run Hjarta. |
| `render.py` | **All** terminal output formatting. `render_reply`, `render_stream_chunk`, `stream_finish_tag`, `render_citations`, `render_well_disconnected_banner`, `render_well_status`, `render_doctor`, `render_ingest_summary`, plus Phase-16 `render_tool_call_proposal` + `render_tool_reply` + `INTERRUPTED_TAG`. |

## What this subpackage does NOT own

- **CLI argument parsing.** `ember.cli.main` builds the argparse tree;
  Munnr's modules expose `run(...)` callables that the dispatcher
  invokes.
- **Behaviour.** Every line of operator-facing work happens in one of
  the other realms (Funi for reasoning, Brunnr for storage, Smiðja for
  ingest, Hjarta for first-run). Munnr orchestrates, never implements.
- **Approval prompting policy.** That's `ember.spark.funi.tools.approval.resolve(...)`.
  Munnr just calls into it and consumes the `ApprovalDecision`.
- **Tool execution.** Tool executors live in `ember.tools/`. Munnr
  binds `search_well` to the live Brunnr at chat-loop startup, then
  the registry's `lookup()` returns the executor.

## The conversation REPL — slice 2 shape

`chat.run` is the most load-bearing function in the realm. Its shape:

```
setup
   funi = funi_handle.open(config.funi)         # Unavailable → exit 1
   brunnr | disconnect = strengr.open(...)      # Disconnected → ungrounded mode
   tool_ctx = _maybe_init_tools(config, ...)    # None when tools disabled

loop on operator input
   hits = _retrieve(text, brunnr, embedder)     # empty when disconnected
   context = funi_prompt.assemble(...)          # SYSTEM + EPISODE + CHUNK items

   if streaming:
      final_text = _drive_turn_with_tools(...)  # outer loop, bounded by _MAX_TOOL_TURNS
         for iteration in range(_MAX_TOOL_TURNS):
            turn = _run_streaming_turn(funi, ..., tools=tool_descriptors)
            # writes deltas live, captures final chunk's tool_calls
            if not turn.tool_calls: break
            tool_round = _run_tool_round(turn.tool_calls, tool_ctx, stdout)
               # for each call: validate → resolve approval → maybe prompt →
               #                 execute → audit → render reply
            context.extend(tool_round.context_extension)  # TOOL_REPLY items
            tool_ctx.session_standing |= tool_round.session_added
            current_input = ""    # follow-up turns carry no operator input
   else:
      reply = funi.complete(text, context, tools=...)
      stdout.write(render.render_reply(reply, ...) + "\n")

   episode = Episode(text, final_text, hits, model_id, ...)
   episodes.append(episode); brunnr.add_episode(episode) suppressing BrunnrError
```

The tool loop is **per operator turn**, bounded at 8 iterations. A
model that loops on tool_calls forever still terminates with
`[tool-loop max iterations reached]` on stdout.

## How Munnr renders

Per `DATA_FLOW.md` §2.2 + the Vow of Graceful Offline:

- **Always show the disconnect banner on ungrounded replies.**
  `render_well_disconnected_banner(disconnect)` prepends every reply
  that landed without a live Brunnr.
- **Citations footer** when there are hits AND the Well was reachable
  for *this* turn.
- **Tool proposal + reply blocks** when the model emitted tool_calls
  (Phase 16). Redaction-on-display honored per
  `descriptor.redacted_arg_names`.
- **No `print()` anywhere.** Everything routes through `render.py`
  helpers or `stdout.write(...)` in the chat hot loop.

## Slice-2 extensions

| Phase | What landed |
|---|---|
| 11 | `chat.py` rewritten to consume `complete_streaming`. New `_run_streaming_turn` writes deltas live; new `_tag_interrupted` handles Ctrl-C. New `render_stream_chunk` + `stream_finish_tag` + `render_citations` helpers. `INTERRUPTED_TAG` constant. |
| 16 | `chat.py` extended with `_drive_turn_with_tools` (the outer loop) and `_run_tool_round` (the per-call orchestrator). New `_ToolContext` and `_StreamedTurn.tool_calls`. New `render_tool_call_proposal` + `render_tool_reply` helpers. |

## Layout

```
src/ember/spark/munnr/
├── README.md
├── INTERFACE.md
├── __init__.py
├── chat.py            # the REPL — streaming + tool loop
├── ask.py             # one-shot ask
├── ingest.py          # ember well ingest
├── status.py          # ember well status
├── doctor.py          # ember doctor
├── setup.py           # ember setup --reset
└── render.py          # all terminal output formatting
```

## Test seams

Every `run(...)` in this subpackage accepts:

- `stdin` / `stdout: TextIO` — defaults to `sys.stdin` / `sys.stdout`;
  tests inject `io.StringIO`.
- `funi_opener: Callable` — overrides `funi_handle.open` for test
  doubles.
- `strengr_opener: Callable` — overrides `strengr.open` for forced
  disconnect / fake Brunnr.
- (chat only) `approval_prompter: ApprovalPrompter` — Phase-16
  addition; tests inject scripted `y`/`n`/`always` answers.

Production code never passes these — defaults kick in.

## Related

- `INTERFACE.md` — public surface.
- `docs/architecture/DATA_FLOW.md` §2 (turn) + §3 (ingest).
- `docs/architecture/DOMAIN_MAP.md` §7 — ownership.
- `docs/decisions/0009-streaming-funi-replies.md` — the streaming
  contract Munnr consumes.
- `docs/decisions/0011-tool-use-framework.md` — the tool framework
  Munnr drives.
- `tests/integration/test_phase{6,11,16,17}_*.py` — end-to-end
  Munnr-driven flows.
- `tests/unit/test_munnr_render*.py` — render helper contracts.
