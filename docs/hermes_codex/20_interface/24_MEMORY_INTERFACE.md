---
codex_id: 24_MEMORY_INTERFACE
title: Memory Interface — Audit-Grade View of Hermes's Memory API Surface
role: Auditor
layer: Interface
status: draft
hermes_source_refs:
  - agent/memory_manager.py:1-610
  - agent/memory_provider.py:1-280
  - agent/memory_manager.py:43-59
  - agent/memory_manager.py:62-225
  - agent/memory_manager.py:244-302
  - agent/memory_manager.py:410-428
ember_subsystem_targets: [Brunnr, Smiðja, Munnr, Hjarta]
cross_refs:
  - 10_domain/11_AGENT_CORE
  - 20_interface/25_GATEWAY_INTERFACE
  - 50_verification/55_INVARIANT_LIST
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Memory Interface — Audit-Grade

*Sólrún Hvítmynd, cold-eyed: a memory interface is the place where the agent decides what it knows. If the contract is loose, the agent will lie. Read what Hermes promises. Read what it does. Then ask which of those is enforceable.*

Hermes's memory subsystem has two surfaces of interest to Ember:

1. The **manager surface** in `agent/memory_manager.py:244-610` — an in-process orchestrator that fans out lifecycle calls across an internal "builtin" provider and **at most one** external provider.
2. The **provider surface** in `agent/memory_provider.py:42-280` — an `ABC` with ~14 methods, half of them optional hooks with no-op defaults.

Both surfaces are mostly documented in prose. Few of the contracts have a machine-checkable shape. That is the substance of this audit.

## 1. What the contract documents

`MemoryProvider` (`agent/memory_provider.py:42-280`) declares:

```python
class MemoryProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def initialize(self, session_id: str, **kwargs) -> None: ...

    def system_prompt_block(self) -> str: ...
    def prefetch(self, query: str, *, session_id: str = "") -> str: ...
    def queue_prefetch(self, query: str, *, session_id: str = "") -> None: ...
    def sync_turn(self, user_content: str, assistant_content: str, *, session_id: str = "") -> None: ...

    @abstractmethod
    def get_tool_schemas(self) -> List[Dict[str, Any]]: ...

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str: ...
    def shutdown(self) -> None: ...

    # Optional lifecycle hooks (override to opt in):
    def on_turn_start(self, turn_number: int, message: str, **kwargs) -> None: ...
    def on_session_end(self, messages: List[Dict[str, Any]]) -> None: ...
    def on_session_switch(self, new_session_id: str, *, parent_session_id: str = "", reset: bool = False, **kwargs) -> None: ...
    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str: ...
    def on_delegation(self, task: str, result: str, *, child_session_id: str = "", **kwargs) -> None: ...
    def on_memory_write(self, action: str, target: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None: ...
    def get_config_schema(self) -> List[Dict[str, Any]]: ...
    def save_config(self, values: Dict[str, Any], hermes_home: str) -> None: ...
```

What is **documented but not enforced** by the ABC:

- `handle_tool_call` "must return a JSON string" (`agent/memory_provider.py:131-137`). The base class raises `NotImplementedError`; subclasses that return a dict, a `None`, or a non-string crash the consumer downstream.
- `prefetch` "should be fast — use background threads" (`agent/memory_provider.py:92-104`). Nothing measures or enforces that.
- `sync_turn` "should be non-blocking" (`agent/memory_provider.py:114-119`). Same: prose only.
- `is_available` "Should not make network calls — just check config and installed deps" (`agent/memory_provider.py:53-58`). A misbehaving provider may dial out at import time. The manager has no isolation.

What is **enforced** by the manager:

- **One-external-provider rule** (`agent/memory_manager.py:258-302`). A second non-builtin `add_provider` is rejected with a warning. Tool-name collisions across providers are kept by first registration (`agent/memory_manager.py:285-296`).
- **Failure isolation per hook**: every fan-out wraps the provider call in `try/except` (`agent/memory_manager.py:325-609`). A throwing provider does not block the manager, but the failure is *only logged* — no callback, no metric, no operator alert.
- **Tool routing by name**: the manager owns a flat `Dict[str, MemoryProvider]` (`agent/memory_manager.py:253`); duplicates are silently dropped.

## 2. The implicit contracts (the ones that bite)

These are not in the docstrings. They are load-bearing all the same.

### 2.1 The `<memory-context>` fence is a parsing contract

`agent/memory_manager.py:43-59` defines three regexes:

```python
_FENCE_TAG_RE = re.compile(r'</?\s*memory-context\s*>', re.IGNORECASE)
_INTERNAL_CONTEXT_RE = re.compile(
    r'<\s*memory-context\s*>[\s\S]*?</\s*memory-context\s*>',
    re.IGNORECASE,
)
_INTERNAL_NOTE_RE = re.compile(
    r'\[System note:\s*The following is recalled memory context,\s*NOT new user input\.\s*Treat as (?:informational background data|authoritative reference data[^\]]*)\.\]\s*',
    re.IGNORECASE,
)
```

`sanitize_context()` strips pre-wrapped fences from provider output before re-wrapping (`agent/memory_manager.py:54-59`, `:227-241`). The reason: a provider that emits its own `<memory-context>...</memory-context>` would double-wrap the fence and could smuggle a fake "system note" past the consumer.

This is a **soft trust boundary inside a string**. It is exactly the kind of in-process heuristic Hermes's own `SECURITY.md:136-145` warns against as a security boundary: *"They are useful. They are not boundaries."* The fence keeps an honest provider honest; it cannot stop an adversarial one.

### 2.2 Streaming requires its own state machine

`StreamingContextScrubber` (`agent/memory_manager.py:62-224`) exists because chunked deltas can split a fence across boundaries:

```
delta1 = "<memory-context>"
delta2 = "secret recalled fact"
delta3 = "</memory-context>"
```

A one-shot regex over each delta would emit `delta2` as if it were normal text. The scrubber holds back any tail that *might* be the start of a tag and discards everything inside an opened span. On end-of-stream, an unterminated span discards its buffer rather than emit (`agent/memory_manager.py:147-161`):

> *If we're still inside an unterminated span the remaining content is discarded (safer: leaking partial memory context is worse than a truncated answer).*

That is a real verification stance: **leak-safe, not loss-safe, when the choice is forced**. Ember's Honest Memory Vow would make the same call.

### 2.3 Metadata-mode introspection on `on_memory_write` is duck-typed

`agent/memory_manager.py:511-565` inspects every provider's `on_memory_write` signature to decide whether to pass `metadata` as keyword, positional, or omit it entirely. Three modes, no version field, no declared contract — the manager *infers* by signature. Pros: backward-compatible across plugin versions. Cons: a plugin author who reorders parameters silently flips into a different mode and gets metadata in the wrong slot.

This is a smell. An interface that needs signature inspection at the dispatch site is one that should be versioned.

## 3. The invariants Hermes relies on (often unstated)

The pure dataclasses (`agent/tool_guardrails.py:127-141`, `agent/memory_manager.py:244-302`) and the consumer code together rely on these invariants:

| # | Invariant | Documented? | Enforced? | What breaks when violated |
|---|---|---|---|---|
| M-1 | At most one external `MemoryProvider` is registered. | Yes — `add_provider` docstring, `agent/memory_manager.py:258-279`. | Yes — explicit rejection branch. | Tool-schema bloat, ambiguous routing, conflicting recalls. |
| M-2 | Tool names are globally unique across providers. | Implicitly: collisions get a warning and the first registration wins (`agent/memory_manager.py:288-296`). | Soft — duplicates are dropped, not refused. | A plugin's tool silently shadows the builtin tool; the operator never sees the conflict. |
| M-3 | `handle_tool_call` returns a JSON-encoded string. | Yes — `agent/memory_provider.py:131-137`. | No — runtime exception if a provider returns a dict. | Downstream OpenAI SDK serialization crashes; conversation loop dies. |
| M-4 | `is_available` does not perform network I/O. | Yes — `agent/memory_provider.py:53-58`. | No. | Startup latency, intermittent agent boot failures on flaky networks. |
| M-5 | `prefetch` returns quickly. | Yes — `agent/memory_provider.py:92-104`. | No timeout, no deadline. | Per-turn latency spikes, the operator notices and blames the model. |
| M-6 | Provider exceptions do not bubble to the agent loop. | Yes — `agent/memory_manager.py:325-609` wraps every call. | Yes — `try/except` everywhere. | (Not violated in shipped code, but a single missing `try` re-introduces cascading failure.) |
| M-7 | Memory context, once wrapped, is opaque to the model. | The fence is the contract (`agent/memory_manager.py:227-241`). | Soft — depends on the model not training-time-memorising the fence pattern. | Model recognises the fence, may emit it itself; provider sanitization (M-7a) is the second line. |
| M-8 | `session_id` rotation always emits `on_session_switch` before the next `sync_turn`. | Yes — `agent/memory_provider.py:163-200`. | Yes — `MemoryManager.on_session_switch` is called by every rotation path (`agent/memory_manager.py:457-490`). | A provider writes the wrong session, the operator's history fragments. |
| M-9 | The builtin provider is always first in `_providers`. | Implicit — only the builtin sets `name == "builtin"` and is never rejected. | Yes by ordering convention; nothing enforces it. | An external provider that races registration could land before the builtin, affecting `build_system_prompt` ordering. |
| M-10 | `on_memory_write` is only fired by the builtin tool. | Yes — `agent/memory_manager.py:548-565` skips the builtin provider in the loop. | Yes. | An external provider that called `on_memory_write` reentrantly would loop. |
| M-11 | Provider `shutdown` is called in reverse registration order. | Yes — `agent/memory_manager.py:581-590` uses `reversed(self._providers)`. | Yes. | Builtin shutdown before external could close storage the external still writes to. |

## 4. Where the contract is weakest

### 4.1 No deadlines

Every per-turn fan-out (`prefetch_all`, `queue_prefetch_all`, `on_turn_start`, `on_pre_compress`) iterates providers sequentially with **no per-call deadline**. A slow provider taxes every turn. The only mitigation is the prose advice "should be fast" on `prefetch`. The implicit assumption: providers self-budget.

For Ember, where the operator may be on a Pi over a tailnet to a remote Brunnr, this assumption does not hold.

### 4.2 No structured failure shape

When `prefetch` raises, the manager logs at `DEBUG` and continues. The operator sees nothing. There is no `MemoryRecallFailed` event, no banner, no degraded-mode indicator. Compare to Ember's Vow of Graceful Offline (SYSTEM_VISION §3) — when the Well is unreachable the operator must be told. Hermes does not match that vow.

### 4.3 No versioning

Neither `MemoryProvider` nor the per-method contract carries a version. The `on_memory_write` signature-introspection (`agent/memory_manager.py:511-535`) is the dispatch-time workaround. Versioning would replace it.

### 4.4 No JSON validation on `get_tool_schemas`

Schemas are accepted blindly and indexed by name (`agent/memory_manager.py:285-296`). A provider can ship a schema missing `parameters`, missing `description`, or with a `parameters` object that does not validate against the OpenAI function-calling shape, and the manager will not notice. Downstream API rejection is the first signal.

### 4.5 No reentrancy contract

If `handle_tool_call` for tool A calls back into `prefetch_all` (e.g. a memory tool that recalls before writing), the manager has no reentrancy state. Nothing prevents two-deep, three-deep, or infinite recursion via two cooperating providers. Hermes has not hit this in practice because there is only one external provider.

### 4.6 `session_id` is a string, not a typed identifier

Throughout the surface, `session_id: str` (`agent/memory_provider.py:78-79`, `:92-104`, `:114-119`). A typo, an empty string, or a colliding string from two clients all type-check. The only validation: `agent/memory_manager.py:476-477` skips `on_session_switch` for empty strings.

## 5. The `MemoryManager` orchestration surface

The manager (`agent/memory_manager.py:244-610`) is the single integration point. Worth a separate audit:

- **Registration is order-sensitive** (`agent/memory_manager.py:282-296`). A duplicate tool name from a later provider is silently ignored.
- **`build_system_prompt` concatenates** every provider's `system_prompt_block` with `"\n\n"`. The order matters for the model — and is just insertion order, no priority.
- **`get_all_tool_schemas` deduplicates by name** with a `seen` set (`agent/memory_manager.py:384-400`). The first schema for a name wins; the second is silently dropped.
- **`handle_tool_call` routes by name** (`agent/memory_manager.py:410-428`). If routing fails, the manager returns `tool_error(...)` rather than raising — the model sees a "no provider handles tool X" string and must reason about it.
- **`initialize_all` auto-injects `hermes_home`** (`agent/memory_manager.py:592-609`). A provider that forgets the key still gets the value. A provider that *expects* the key to be absent is broken.
- **`shutdown_all` walks in reverse** (`agent/memory_manager.py:581-590`). Documented; enforced; one of the few places ordering is deliberate.

## 6. Real failure modes observed in Hermes

Drawn from RELEASE notes and tests:

- **`StreamingContextScrubber` exists because earlier per-delta regex code leaked.** The streaming surface failed silently for an unknown stretch of releases before this was caught. The fix is correct; the meta-lesson is that *any* per-delta regex over LLM output is a leak waiting to be discovered.
- **`on_memory_write` metadata-mode introspection exists because old plugin signatures crashed.** The fix is correct; the meta-lesson is that backward compatibility via duck-typing accumulates technical debt.
- **External-provider rejection exists because tool schema bloat was a real complaint.** The fix is correct; the meta-lesson is that *unbounded* extensibility points become unbounded performance problems.

## 7. Comparison to Ember's current shape

Ember's slice-2 Brunnr Protocol (`src/ember/well/brunnr/`) holds 14 methods (per SLICE_2_RETROSPECTIVE.md). It is typed — the `BrunnrHandle` Protocol is named in `EMBER_FIRST_SLICE_PLAN.md`. Failure modes return typed values (`Disconnected`, eight reasons; per ADR 0007 §2.2). This is *stronger* than Hermes's `MemoryProvider` in three ways:

1. **Typed failures** (Disconnected vs silent log).
2. **Protocol, not ABC** (structural, not nominal).
3. **No optional-with-no-op default hooks** (every method is intentional).

But Ember has no equivalent of:

- Multi-provider fan-out (one Brunnr, no aggregation).
- `<memory-context>` fence semantics (no provider-injected context yet).
- Streaming scrub (Funi streams, but the Well does not).
- `on_session_switch` (Ember sessions are CLI-process-scoped at slice 2).

When Ember adds Skein/Skry as memory providers (per UNWIRED_INVENTORY §5.4 / ADR 0012), the multi-provider problem arrives. The interface needs to be designed *before* the second provider, not after.

## What This Means for Ember

**Subsystems affected:** Brunnr (storage), Smiðja (ingest), Munnr (rendering), Hjarta (first-run config).

**Vows touched:**

- **Vow of Honest Memory** — Hermes's `<memory-context>` fence + scrubber is the right mechanical shape for this Vow, but enforcement is a soft heuristic.
- **Vow of Modular Authorship** — Hermes's `try/except` fan-out matches the Vow, but silent logging violates the *operator visibility* spirit.
- **Vow of Graceful Offline** — Hermes degrades silently on provider failure. Ember must degrade *visibly*.

**Concrete proposals for the Brunnr/Smiðja interface:**

1. **Adopt the one-external-provider rule** at the Brunnr layer when memory-provider plugins arrive. Tool-schema bloat is a real Ember-scale concern on a Pi.
2. **Replace ABC with `Protocol`** (Ember already does this for `BrunnrHandle`). Apply the same pattern to any future `MemoryProviderHandle`.
3. **Version the contract.** Add `protocol_version: int` as a class attribute on every implementation; the manager refuses providers below `MIN_SUPPORTED`.
4. **Replace signature introspection with declared capabilities.** A `provider.capabilities()` set that lists `{"metadata", "delegation", "pre_compress"}` is cleaner than `inspect.signature` walking.
5. **Add per-call deadlines.** Every fan-out method takes `timeout_s: float`. A provider that exceeds it returns `Disconnected(TIMEOUT)` (matches Ember's existing eight-reason taxonomy) and the manager continues.
6. **Surface failures.** When a provider fails twice in a turn, raise a `WellDegraded` event Munnr can render to the operator. Silent retry is a Hermes habit Ember should not inherit. Cross-reference [[50_verification/52_ANTIPATTERN_CATALOG]] entry "silent-fan-out".
7. **No fence-as-trust-boundary.** If Ember ever injects recalled context, the fence is for **parsing**, never for **trust**. The model is always assumed capable of emitting the fence. This is exactly Hermes `SECURITY.md:136-145`'s position; Ember should adopt it explicitly.
8. **Treat streaming as a *separate* contract.** If a future Funi adapter streams memory tool results, the streaming scrubber pattern from `agent/memory_manager.py:62-224` is a direct reference design.
9. **Type `session_id`** as a `NewType` (`SessionId = NewType("SessionId", str)`) and validate at construction. Reject empty strings.
10. **No silent dedup of tool schemas.** Either raise on duplicate or log at WARN and refuse to register. Whichever you choose, do it loudly.

Cross-link with [[50_verification/55_INVARIANT_LIST]] for the master list and [[50_verification/52_ANTIPATTERN_CATALOG]] entry "context-fence-as-trust-boundary".

The interface that survives is the one whose contract cannot be quietly violated. Hermes has the right shape; the enforcement is still mostly prose.
