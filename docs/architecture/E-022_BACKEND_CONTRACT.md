# E-022 — Model backends: the backend contract + conformance

*Slice E-022 of the Project Ember roadmap (Part II). What changed,
what it proves, and what remains open — all claims drawn from the
code and the test runner of this slice.*

## The problem, as E-019/E-020 left it

- The "contract" was four methods on the `FuniHandle` protocol
  (`complete`, `complete_streaming`, `health`, `close`) and one
  implemented adapter — Ollama. E-019 §5.3 mapped it; E-022 owns it.
- Nothing declared **capabilities**. A consumer could not ask a
  backend whether it streams natively or through the ADR 0009
  wrapper, whether it speaks the tool protocol, whether its replies
  carry token counts, or whether its health reports RAM. Chat
  simply assumed the richest backend's shape for every handle.
- Capability claims lived in prose, and had already drifted:
  `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` §4 described a
  `POST /api/generate` call, an optional Funi `embed()` method,
  and a 127000 max-token default — none of which the shipped code
  has ever done (`/api/chat`, no `embed` on the protocol,
  `num_predict` default 1024).
- The config enum names five runtimes; four (`llamacpp`,
  `lmstudio`, `phi_silica`, `apple_foundation`) return a typed
  `Unavailable` from `open()` — truthful, but nowhere published as
  a table a reader (or E-023) could bind against.

## What this slice builds

### 1. Declared capabilities (`ember.schemas.funi`)

- `StreamingMode` — `NATIVE` (the backend streams incrementally),
  `WRAPPED` (complete-only; streaming is the one-final-chunk
  `wrap_complete_as_stream` helper, ADR 0009 §2.2), `NONE`.
- `BackendCapabilities` — a frozen dataclass every implemented
  backend carries as its `capabilities` attribute, now part of
  the `FuniHandle` protocol: `runtime_kind`, `streaming`,
  `tool_calls`, `tool_calls_model_dependent` (the adapter speaks
  the tool protocol but whether a model *emits* calls is the
  model's part — `phi3:mini` does not, per the options ladder),
  `token_counts`, `reports_ram_use`, `requires_endpoint`, and
  `context_kinds` (which `ContextKind` values have a defined
  translation).

### 2. The registry (`ember.spark.funi.handle`)

`backend_registry()` publishes one `BackendRegistration` per
`FuniRuntime` — runtime, `implemented`, and its capabilities
(`None` exactly when unimplemented). `capabilities_for(runtime)`
is the single-runtime lookup. The conformance tests fail if a
runtime is ever added to the enum without a registry entry, so
the table cannot silently fall behind the config again.

### 3. Capability truth per backend

| Runtime | Implemented | Streaming | Tool calls | Token counts | RAM in health | Endpoint | Context kinds |
|---|---|---|---|---|---|---|---|
| ollama | **yes** | native NDJSON | yes — model-dependent emission | yes (eval counters) | **no** (always None) | yes (localhost by config default) | all five |
| llamacpp | no | — | — | — | — | — | — |
| lmstudio | no | — | — | — | — | — | — |
| phi_silica | no | — | — | — | — | — | — |
| apple_foundation | no | — | — | — | — | — | — |

Ollama's row is `OLLAMA_CAPABILITIES` in its adapter module,
read from the code it describes: native streaming in
`complete_streaming`; tool descriptors sent and `tool_calls`
parsed in both paths; `prompt_eval_count` / `eval_count` mapped
to the reply's token fields; `health()` leaves `ram_use_bytes`
None; `_messages_from_context` translates SYSTEM, SUMMARY and
CHUNK to system messages, EPISODE to a user/assistant pair, and
TOOL_REPLY to a tool message. The unimplemented four are not
"planned capabilities" — they have none, and `open()` keeps
returning `Unavailable(RUNTIME_NOT_INSTALLED)` for each.

### 4. Conformance, proven by tests

`tests/unit/test_backend_contract_e022.py` (16 tests) pins:
registry coverage of every runtime exactly once; exactly one
implemented backend; every unimplemented runtime both
Unavailable at `open()` and capability-free in the registry;
Ollama's capabilities identical across the adapter class, a live
handle, and the registry; the capability pins above (including
immutability); Ollama's mocked-transport contract run (complete
carrying token counts, native streaming terminating in a `done`
chunk, health never raising and reporting no RAM, idempotent
close); and a minimal complete-only fake backend conforming via
`StreamingMode.WRAPPED` — the shape any future backend (E-023's
Aesir binding first) is judged against.

### 5. In-scope drift fixed

`FUNI_LOCAL_MODEL_OPTIONS.md` §4 now states the real contract
(the four methods + `close()` + the E-022 capabilities
attribute), names Smiðja's own embed client as the embedding
owner, and corrects the endpoint to `POST /api/chat` with the
`num_predict` default of 1024 — with the correction itself noted
in the doc. No other prose was touched; no README was touched.

## Honest limits

- Tool-call *emission* stays model-dependent under Ollama; the
  contract declares that dependence rather than resolving it.
  Which models emit calls is the options ladder's business.
- `runtime_checkable` isinstance checks verify methods only;
  attribute presence (`runtime_kind`, `model_id`, `capabilities`)
  is pinned by the conformance tests, not the type system.
- Chat does not yet *branch* on capabilities (e.g. it does not
  refuse streamed tool loops on a WRAPPED backend) — docket 83's
  non-streaming tool-call drop keeps its E-026/E-028 home; this
  slice gives those slices the declared truth to branch on.
- E-023 binds Project Aesir under this contract next; nothing
  about Aesir is claimed here.
