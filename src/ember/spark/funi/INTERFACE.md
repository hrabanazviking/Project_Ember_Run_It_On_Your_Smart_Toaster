# INTERFACE — `ember.spark.funi`

## Module purpose

Local LLM runtime. One adapter per supported runtime. Funi is given
prompts and (rarely) tool slots; Funi produces replies or honest stops.

## Public entry points (planned, Phase 5 onward)

- `ember.spark.funi.handle.FuniHandle` — the Protocol every runtime
  adapter satisfies.
- `ember.spark.funi.handle.open(config) -> FuniHandle | Unavailable`
- `ember.spark.funi.ollama.OllamaFuni` — first-slice default (Phase 5).

## Minimum surface — the canonical table

(Authoritative spec in `docs/architecture/DOMAIN_MAP.md` §5.1.)

| Operation | Inputs | Returns | Notes |
|---|---|---|---|
| `open(config)` | `FuniConfig` | `FuniHandle` or `Unavailable` | Loads the model or connects to its endpoint. |
| `complete(prompt, context, tools=None)` | `str`, `list[ContextItem]`, optional list | `FuniReply` | One turn. **No streaming in the first slice.** |
| `embed(texts)` *(optional)* | `list[str]` | `list[list[float]]` | Only some runtimes; Smiðja uses its own client if absent. |
| `health()` | — | `FuniHealth` | `model_id`, `ram_use`, `last_ok` — for `ember doctor`. |

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
