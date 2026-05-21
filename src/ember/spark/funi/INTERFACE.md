# INTERFACE — `ember.spark.funi`

## Module purpose

Local LLM runtime. One adapter per supported runtime. Funi is given
prompts and (rarely) tool slots; Funi produces replies or honest stops.

## Public entry points (shipped Phase 5, 2026-05-21)

- `ember.spark.funi.FuniHandle` — `@runtime_checkable` Protocol every
  runtime adapter satisfies. Required attributes: `runtime_kind: str`,
  `model_id: str`. Required methods: `complete`, `health`, `close`.
- `ember.spark.funi.open(config) -> FuniHandle | Unavailable` — the
  registry entry. Dispatches on `config.runtime`. Returns `Unavailable`
  for runtimes not yet implemented in this build.
- `ember.spark.funi.prompt.assemble(*, identity, episodes, hits,
  well_disconnected=False) -> list[ContextItem]` — runtime-neutral
  context assembler called by Munnr before `complete()`.
- `ember.spark.funi.ollama.OllamaFuni` — the first-slice default
  adapter; `runtime_kind = "ollama"`.

## Minimum surface — the canonical table

(Authoritative spec in `docs/architecture/DOMAIN_MAP.md` §5.1.)

| Operation | Inputs | Returns | Notes |
|---|---|---|---|
| `open(config)` | `FuniConfig` | `FuniHandle` or `Unavailable` | Probes the endpoint; never raises. |
| `complete(prompt, context, tools=None)` | `str`, `Sequence[ContextItem]`, optional `Sequence[str]` | `FuniReply` | One turn. **Always returns** — mid-call failure → `finish_reason=ERROR` with operator-readable text. **No streaming.** |
| `health()` | — | `FuniHealth` | `model_id`, `ram_use_bytes`, `last_ok` — for `ember doctor`. Never raises. |
| `close()` | — | None | Free any held resources. |

The `embed()` method is **not** part of the Funi surface — embedding
lives in :mod:`ember.well.smidja.embed_client`. Keeping Funi focused on
reasoning avoids the "Funi also embeds" temptation that would couple
runtime selection to embedding-model selection.

## Inputs

Assembled prompt + context items. No raw operator text reaches Funi
directly; Munnr is responsible for assembly.

## Outputs

`FuniReply(text, tool_calls=None, finish_reason)` or `Unavailable(reason)`.

## Side effects

Calls the runtime's endpoint (Ollama HTTP, llama.cpp in-process, etc.).
Holds the model in RAM (when applicable).

## Allowed imports

`ember.schemas` plus the runtime-specific client library only inside the
matching adapter subpackage.

## Invariants

- A Funi failure aborts the current turn cleanly; Ember stays usable for
  non-LLM commands.
- The configured `max_tokens` ceiling is 127000 per `RULES.AI.md`; the
  model's own context limit applies first.
- No hardcoded prompts; system prompt content lives under `~/.ember/identity/`
  or `config/`.

## Forbidden responsibilities

- Retrieval (Munnr assembles context before calling Funi).
- Identity persistence (lives under `~/.ember/identity/`).
- Tool execution (the call is a structured value; Munnr is the executor
  if and only if `--allow-tools` was set).
