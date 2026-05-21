# `ember.schemas/`

**Frozen dataclasses, StrEnums, and shared type definitions** used in
two or more other subpackages. The gravitational floor of the Ember
package: every other module under `ember.*` imports *down* into here,
never the reverse. No subpackage under `ember.schemas/` ever imports
back into a realm.

**Shipped:** Phase 2, slice 1 (version 0.1.0, 2026-05-21). Extended
in Phase 8 (config), Phase 10 (stream), Phase 14 (tool).
**Reads with:** `INTERFACE.md` for the public surface; `docs/architecture/DOMAIN_MAP.md` §1 for the design rationale; `docs/decisions/0007-first-slice-ratification-2026-05-21.md` §2.5 for the "no pydantic by default" rule.

---

## What this subpackage owns

Every datatype that crosses a realm boundary:

| Module | What's in it | Used by |
|---|---|---|
| `chunks.py` | `Document`, `Chunk`, `RetrievalHit`, `BrunnrStats` | Smiðja produces, Brunnr stores, Spark consumes via retrieval. |
| `config.py` | `EmberConfig` (top-level) + per-realm subconfigs: `IdentityConfig`, `FuniConfig`, `FuniOllamaConfig`, `StrengrConfig`, `BrunnrConfig`, `SqliteVecConfig`, `PgVectorConfig`, `SmidjaConfig`, `ChunkerConfig`, `EmbeddingConfig`, `JournalConfig`, `ToolsConfig`, `LoggingConfig`, `LoggingDestination`. Plus StrEnums for backends, runtimes, log levels, boundary preferences. | `ember.config` loads; every realm reads. |
| `episode.py` | `Episode` — one persisted conversation turn. | Munnr produces; Brunnr stores; future analysis tools read. |
| `errors.py` | The cross-boundary exception hierarchy (`EmberError` → `BrunnrError` / `IngestError` / `StrengrError` / `FuniError` / `HjartaError` / `MunnrError`); the typed-value-over-exception values (`Disconnected` + `DisconnectReason`). | Every realm raises into these names. |
| `funi.py` | `ContextItem` + `ContextKind` (SYSTEM / EPISODE / CHUNK / TOOL_REPLY); `FuniReply` + `FinishReason`; `FuniHealth`; `Unavailable` + `UnavailableReason`. Re-exports `ToolCall` from `ember.schemas.tool` for backwards-compat. | Spark assembles `ContextItem` lists; Funi adapters produce `FuniReply`. |
| `ingest.py` | `IngestSummary` — the row Smiðja returns when an `ember well ingest <dir>` run completes. | Munnr renders. |
| `stream.py` | `FuniStreamChunk` — one streamed token batch from Funi. Final chunk may carry `tool_calls`. | Funi `complete_streaming` produces; Munnr's chat loop consumes. |
| `thread.py` | `StrengrHealth` — what `ember doctor` reads from Strengr. | Strengr produces; doctor renders. |
| `tool.py` | `ToolDescriptor`, `ToolCall`, `ToolReply`, `ToolParameter`, `ToolParameterKind`, `ApprovalPolicy`, `ApprovalOutcome`, `ToolError`. | Tool framework + first-party tools. |

## What this subpackage does NOT own

- **Validation logic.** The dataclasses are *shape only*. Anything
  beyond "this field is of type X" lives in the consumer
  (`ember.config.validate.coerce_to_dataclass` does config-side
  type coercion; `ember.spark.funi.tools.registry.validate_arguments`
  does tool-arg validation).
- **Defaults that depend on runtime state.** No `field(default_factory=lambda: something_at_import_time())`. Defaults are either literals or `field(default_factory=...)` with a static factory.
- **Pydantic.** Per ADR 0007 §2.5: stdlib `dataclasses` + `StrEnum`
  is the slice-1+slice-2 standard. Pydantic is a deferred opt-in
  extra (`[validation]`).
- **Behaviour.** No methods that do work — just `@classmethod`
  alternate constructors at most. The dataclasses are immutable
  data carriers.

## Conventions

All Ember dataclasses follow:

```python
@dataclass(frozen=True, slots=True)
class FuniReply:
    text: str
    finish_reason: FinishReason
    tool_calls: tuple[ToolCall, ...] = ()      # tuple, never list
    model_id: str = ""
    ...
```

- **`frozen=True`** — immutable after construction.
- **`slots=True`** — no dict overhead, fast attribute access.
- **`StrEnum` for enums** — string-valued, naturally JSON-serialisable,
  no `int → enum` surprise.
- **`tuple[X, ...]` for collections in defaults** — `frozen=True`
  forbids mutable defaults; `field(default_factory=dict)` or
  `field(default_factory=tuple)` for the rare empty defaults.

## File map

```
src/ember/schemas/
├── __init__.py
├── INTERFACE.md         # public surface
├── README.md            # this file
├── chunks.py            # Document / Chunk / RetrievalHit / BrunnrStats
├── config.py            # EmberConfig + every subconfig + StrEnums
├── episode.py           # Episode
├── errors.py            # Exception hierarchy + Disconnected + DisconnectReason
├── funi.py              # ContextItem / ContextKind / FuniReply / FinishReason / FuniHealth / Unavailable
├── ingest.py            # IngestSummary
├── stream.py            # FuniStreamChunk
├── thread.py            # StrengrHealth
└── tool.py              # ToolDescriptor / ToolCall / ToolReply / ApprovalPolicy / ApprovalOutcome
```

## How this subpackage grew through slice 2

| Phase | What changed |
|---|---|
| 2 (slice 1) | Initial population — `chunks`, `config`, `episode`, `errors`, `funi`, `ingest`, `thread`. 66 shape tests. |
| 8 (slice 2) | `config.py` gained the slice-2 subconfigs (overlay paths, secret fields, etc.). |
| 10 (slice 2) | New `stream.py` with `FuniStreamChunk`. |
| 14 (slice 2) | New `tool.py` with the full tool framework's data carriers. `ToolCall` promoted from a placeholder in `funi.py` and re-exported there for backwards-compat. |
| 16 (slice 2) | `FuniStreamChunk.tool_calls` field added; `ContextKind.TOOL_REPLY` added; `ToolsConfig` added to `config.py`. |

## Tests

- `tests/unit/test_schemas_*.py` (8 files) — shape contracts only;
  no behaviour tests live here.
- Cross-realm tests in `tests/integration/test_phase{6,9,11,16,17}_*.py`
  exercise these types in their actual production roles.

## Related

- `INTERFACE.md` — the public surface every other realm imports.
- `docs/architecture/DOMAIN_MAP.md` §1 — the design rationale.
- `docs/decisions/0007-first-slice-ratification-2026-05-21.md` §2.5
  — the stdlib-only rule.
- `docs/decisions/0011-tool-use-framework.md` §2.1-2.2 — the design
  of `tool.py` in particular.
