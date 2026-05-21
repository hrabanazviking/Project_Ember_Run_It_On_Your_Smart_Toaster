# `ember.spark.funi/` — Funi

**The local LLM runtime — the spark itself.** The small model that
thinks on the device. Funi is treated as an *adapter*, not a built-in:
local-runtime ecosystems change too fast to hardcode, so each
supported runtime gets its own subpackage that implements the
`FuniHandle` Protocol declared in `handle.py`.

**Shipped:** Phase 5, slice 1 (Ollama runtime, version 0.1.0). Extended
Phase 10 (streaming), Phase 14-16 (tool use).
**Reads with:** `INTERFACE.md` for the public surface; `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` for the host-RAM-keyed model ladder; `docs/decisions/0009-streaming-funi-replies.md` for the streaming design; `docs/decisions/0011-tool-use-framework.md` for the tool framework that rides this subpackage.

---

## What this subpackage owns

- **The Protocol** (`handle.py`) — `FuniHandle` declares the four
  methods every adapter implements: `complete`, `complete_streaming`,
  `health`, `close`. Plus the `open(config) -> FuniHandle |
  Unavailable` registry dispatch.
- **The prompt assembler** (`prompt.py`) — turns the operator turn +
  retrieved chunks + recent episodes + identity into a runtime-neutral
  `Sequence[ContextItem]`. The Funi adapter's job is to translate
  those into messages its runtime understands.
- **The default-streaming helper** (`wrap_complete_as_stream` in
  `handle.py`) — for adapters that can't stream natively. Wraps
  `complete()` and yields one final `FuniStreamChunk(done=True, ...)`.
- **The Ollama adapter** (`ollama/`) — the slice-1 default. Sends
  to `/api/chat`, parses NDJSON streaming, serializes tool descriptors
  + parses `message.tool_calls`.
- **The tools subpackage** (`tools/`) — the slice-2 framework that
  manages the process-global tool registry, the approval-policy
  resolver, the operator prompter, and the JSONL audit log. (The
  *tools themselves* live in `ember.tools/`, one level above Spark,
  per ADR 0011 §2.9.)

## What this subpackage does NOT own

- **Tool definitions.** The framework lives here; first-party tools
  live at `ember.tools/`.
- **The chat REPL.** Munnr (`ember.spark.munnr.chat`) drives the
  REPL; Funi just answers when called.
- **Retrieval.** Brunnr's job. Munnr orchestrates retrieval before
  calling Funi.
- **Persistence.** Munnr writes Episodes to Brunnr after the turn.

## The `FuniHandle` Protocol (the contract)

```python
@runtime_checkable
class FuniHandle(Protocol):
    runtime_kind: str
    model_id: str

    def complete(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> FuniReply: ...

    def complete_streaming(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> Iterator[FuniStreamChunk]: ...

    def health(self) -> FuniHealth: ...
    def close(self) -> None: ...
```

`runtime_kind` and `model_id` are class/instance attributes so the
doctor command and audit log can identify the live runtime without
reflection.

## Subpackages — the runtime menu

| Subpackage | Status | What it talks to | Tool calls? |
|---|---|---|---|
| `ollama/` | **Shipped** (Phase 5, with streaming Phase 10, tool-calls Phase 16) | Local Ollama HTTP endpoint at `OLLAMA_HOST` (default `http://localhost:11434`). | Yes — when the model supports them. `llama3.2:3b` is the Pi-class default; `phi3:mini` does NOT support tool calls (Ollama returns 400). |
| `tools/` | **Shipped** (Phase 14) | The process; not a runtime. | N/A — this IS the tool framework. |
| `llamacpp/`, `lmstudio/`, `phi_silica/`, `apple_foundation/` | **Deferred** per ADR 0013 §3 | n/a yet | Future per-runtime decision. |

Slice 3 may add one or more of the deferred runtimes; each is a
Phase-5-shaped commit that implements the Protocol.

## How a Funi runtime is selected at runtime

1. **Config:** `FuniConfig.runtime: FuniRuntime` enum value (default
   `OLLAMA`); per-runtime sub-block (`FuniConfig.ollama` of type
   `FuniOllamaConfig`).
2. **Dispatch:** `ember.spark.funi.handle.open(config)` switches on the
   enum and calls the matching adapter's `open()`. Lazy import per
   ADR 0007 §2.1 — only the chosen runtime's library is loaded.
3. **Failure path:** `open()` returns `Unavailable(reason, detail)`
   rather than raising. CLI (`ember chat`) reports the reason and
   exits with code 1; the operator gets a clear message.

## Slice-2 extensions

| Phase | What landed |
|---|---|
| 10 | `complete_streaming` Protocol slot; `wrap_complete_as_stream` helper; Ollama NDJSON streaming via `/api/chat?stream=true`. ADR 0009. |
| 14 | `tools/` subpackage — process-global registry, approval resolver, `StdinApprovalPrompter`, atomic JSONL audit log. ADR 0011. |
| 16 | Ollama tool-call wire format: `_descriptor_to_ollama_tool` converts to OpenAI-style function spec; `_parse_tool_calls` accumulates from non-`done` streaming frames into the final chunk's `tool_calls`. Plus `ContextKind.TOOL_REPLY` → `role="tool"` message mapping. |

## Layout

```
src/ember/spark/funi/
├── README.md
├── INTERFACE.md
├── __init__.py
├── handle.py             # FuniHandle Protocol + open() registry + wrap_complete_as_stream
├── prompt.py             # context assembler
├── ollama/               # the slice-1 default runtime
│   ├── INTERFACE.md
│   ├── __init__.py       # re-exports
│   └── adapter.py        # OllamaFuni + _descriptor_to_ollama_tool + _parse_tool_calls
└── tools/                # the slice-2 tool framework
    ├── INTERFACE.md
    ├── __init__.py
    ├── registry.py       # register / lookup / list_tools / clear / validate_arguments
    ├── approval.py       # resolve / resolve_with_answer / StdinApprovalPrompter
    └── audit.py          # AuditLog — atomic JSONL writer with redaction
```

## Failure semantics (per ADR 0007 §2.2 + ADR 0009 §2.4 + ADR 0011 §2.8)

- **`open()` returns `Unavailable`, never raises.** Probe failure
  (endpoint unreachable, version response malformed, runtime not
  installed) → typed reason value.
- **`complete()` always returns a `FuniReply`.** Mid-call failure
  folds into `FuniReply(finish_reason=ERROR)` with explanatory text.
- **`complete_streaming()` always yields a final `done=True` chunk.**
  Mid-stream failure yields a final ERROR chunk per ADR 0009 §2.4.
- **`health()` never raises** — same shape Strengr uses for the Well.

## Related

- `INTERFACE.md` — public surface as Spark consumes it.
- `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` — model menu and
  host-RAM ladder.
- `docs/decisions/0009-streaming-funi-replies.md` — streaming design.
- `docs/decisions/0011-tool-use-framework.md` — tool framework design.
- `tests/unit/test_funi_*.py` — 47 unit tests across handle, prompt,
  Ollama, Ollama-streaming, Ollama-tool-calls.
- `tests/integration/test_funi_ollama_real.py` — real-Ollama smoke
  (gated on tailnet reachability).
