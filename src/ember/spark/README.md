# `ember.spark/` — the Spark realm

**Where Ember thinks on the device.** The only realm that **must run
with no network at all**: Funi reasons locally, Hjarta walks the
operator through first-run on first launch, Munnr renders the CLI.
If the Well is unreachable, Spark continues — ungrounded, but it
continues. That's the Vow of Graceful Offline made mechanical.

**Shipped:** Slice 1 Phases 5-6 (version 0.1.0); extended through
slice 2 Phases 10, 11, 14, 16 (streaming, tool framework, tool loop,
Hjarta advanced branch).
**Reads with:** `docs/architecture/ARCHITECTURE.md` §3.1; `docs/architecture/DOMAIN_MAP.md` §5-7; `docs/architecture/DATA_FLOW.md` §2 + §4.

---

## What this realm owns

Three subpackages, each with its own True Name:

| Subpackage | True Name | Role |
|---|---|---|
| `funi/` | **Funi** ("flame, fire") | Local LLM runtime. One adapter per supported runtime; first-slice default is `ollama/`. Owns the prompt assembler, the streaming protocol, the tool-call wire format, and the tools subpackage (registry / approval / audit). |
| `hjarta/` | **Hjarta** ("heart") | The first-run setup state machine. A finite, named FSM (Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell → TestRetrieval → NameEmber → **AdvancedTools** → WriteIdentity → Done). Atomic identity write at the end; no half-configured state. |
| `munnr/` | **Munnr** ("mouth") | The command-line surface. Argument parsers, subcommand routing, REPL loop, render layer, the chat-side tool loop. Where Ember is summoned. |

## What this realm does NOT own

- **The Well.** Brunnr (`ember.well.brunnr/`) and Smiðja
  (`ember.well.smidja/`) live in their own realm.
- **The tether.** Strengr (`ember.thread.strengr/`) is the boundary
  between Spark and the Well; Spark imports it but doesn't host it.
- **Persistence.** Spark hands `Episode` objects to Brunnr for
  storage; it never writes to disk directly (except through Hjarta's
  identity writer + `ember.config`'s yaml writer, both of which use
  atomic-write helpers).

## How the three Spark subpackages fit together

The conversation turn (per `DATA_FLOW.md` §2):

```
Operator types at `ember chat`
   ↓
[Munnr] parses the line
   ↓
[Strengr] open(well_config) → BrunnrHandle | Disconnected
   ↓
[Smiðja embed client] embed(text) → qvec
   ↓
[Brunnr] hybrid_search(qvec, text, k=5) → list[RetrievalHit]
   ↓
[Munnr → funi.prompt] assembles ContextItem list (system + episodes + chunks)
   ↓
[Funi] complete_streaming(prompt, context, tools=...) → Iterator[FuniStreamChunk]
   ↓
[Munnr] renders deltas live; on final chunk with tool_calls, runs tool loop
   ↓                                              ↓
   ↓                       [Funi.tools] registry → executor → ToolReply
   ↓                                              ↓
   ↓                       [Munnr] feeds ToolReply back as TOOL_REPLY context
   ↓                                              ↓
   ↓                       [Funi] complete_streaming again (no operator input)
   ↓                                              ↓
[Munnr] renders summary reply
   ↓
[Brunnr] add_episode(ep)   (via Strengr handle; failure non-fatal)
```

The first-run rite (per `DATA_FLOW.md` §4) is Hjarta's; it ends with
the atomic `WriteIdentity` step that lays down both `identity.json`
and `ember.yaml`.

## Slice-2 changes

| Phase | Subpackage | What changed |
|---|---|---|
| 10 | `funi/` | `complete_streaming` Protocol slot + Ollama NDJSON streaming. |
| 11 | `munnr/` | `chat.py` streaming consumer + Ctrl-C-tags-partial. |
| 14 | `funi/tools/` | Tool framework subpackage (registry, approval, audit). |
| 15 | (outside spark — `ember.tools/`) | First three first-party tools; bind into spark at chat-loop startup. |
| 16 | `funi/ollama/`, `munnr/chat.py`, `hjarta/machine.py`, `munnr/render.py` | Ollama tool-call wire format; chat-side tool loop; Hjarta ADVANCED_TOOLS branch; render helpers. |

## Layout

```
src/ember/spark/
├── README.md          # this file
├── __init__.py
├── funi/
│   ├── README.md
│   ├── INTERFACE.md
│   ├── handle.py      # FuniHandle Protocol + open() registry + wrap_complete_as_stream
│   ├── prompt.py      # context assembler (system + episodes + chunks → ContextItem list)
│   ├── ollama/        # the slice-1 default runtime
│   └── tools/         # the slice-2 tool framework (registry / approval / audit)
├── hjarta/
│   ├── README.md
│   ├── INTERFACE.md
│   ├── __init__.py
│   ├── machine.py     # the FSM
│   ├── identity.py    # atomic identity write + load
│   └── prompts/wizard.toml  # prompt strings per state
└── munnr/
    ├── README.md
    ├── INTERFACE.md
    ├── chat.py        # the conversation REPL (with tool loop)
    ├── ask.py         # one-shot ask
    ├── ingest.py      # ember well ingest wrapper
    ├── status.py      # ember well status wrapper
    ├── doctor.py      # ember doctor wrapper
    ├── setup.py       # ember setup --reset wrapper
    └── render.py      # all terminal rendering helpers
```

## Constraints (per ADR 0007 §2 + ADR 0013 §2.1)

- **Spark must be offline-capable.** Importing anything in `ember.spark/`
  must not require network access. The Funi runtime adapter may *call*
  out to a local Ollama at runtime, but the adapter's import is offline-
  safe.
- **No direct Brunnr import.** Spark imports `BrunnrHandle` from
  `ember.well.brunnr.handle` (the Protocol), but it doesn't import the
  concrete adapters. Backend selection happens in `cli/main.py` via the
  registry.
- **Typed-value-over-exception at every boundary.** `Funi.open()`
  returns `Unavailable`; `complete()` folds errors into
  `FuniReply(finish_reason=ERROR)`; the tool framework folds executor
  exceptions into `ToolReply.error`.

## Related

- `docs/architecture/ARCHITECTURE.md` §3.1 — Spark realm definition.
- `docs/architecture/DOMAIN_MAP.md` §5-7 — per-subpackage ownership.
- `docs/architecture/DATA_FLOW.md` §2 (turn) + §4 (first-run).
- `docs/architecture/EMBER_TRUE_NAMES.md` — what each name owns and
  does not own.
