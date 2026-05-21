# ADR 0009 — Streaming Funi replies

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr** (under the slice-2 scope ratification — "go for slice 2 — bundle 1, 2, 3"; ADR-level ratification implicit in `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 10-11).
**Author:** Mythic-Engineering session — Architect (Rúnhild Svartdóttir) + Forge Worker (Eldra Járnsdóttir).
**Supersedes:** None
**Superseded by:** —

---

## 1. Context

Slice 1's Funi `complete()` returns the whole reply at once. On a Pi 5
with `phi3:mini` and a typical 200-token answer, that means the
operator waits 5-10 seconds in silence and then sees the full reply
appear. The wait is the model generating tokens — the model can
*produce* tokens incrementally; we just don't surface them.

Streaming surfaces them. Operator sees the reply unfold token-by-
token. Same model, same latency, totally different felt experience.

This ADR settles the protocol shape, chunk schema, failure folding,
and default-wrapper semantics so the Phase-10 implementation (Funi
side) and Phase-11 integration (Munnr render + Ctrl-C) have a clear
contract.

## 2. Decision

### 2.1 New Protocol method, not a separate Protocol

**Decision:** `FuniHandle` gains a `complete_streaming` method
alongside `complete`. Both methods are part of the same
`@runtime_checkable Protocol`; every adapter implements both.

**Why one Protocol:** Spark code shouldn't have to branch on "is this
a streaming-capable runtime?" The streaming path is the common case
once Phase 11 lands (default `funi.streaming=True`). The
non-streaming path is the fallback for `funi.streaming=False` or for
runtimes that can't stream natively.

**Why not retire `complete()`:** some callers (e.g. tests, `ember ask`
when piped) genuinely want the whole-reply-as-one-value semantics.
Keeping both methods avoids forcing every caller to consume an
iterator.

### 2.2 Default wrapper for adapters that can't stream natively

**Decision:** `ember.spark.funi.handle` exports a
`wrap_complete_as_stream(handle, prompt, context, tools) -> Iterator[FuniStreamChunk]`
helper that calls `handle.complete()` and yields a single
`FuniStreamChunk(done=True, ...)` carrying the full reply.

**Why a helper rather than a Protocol default body:** Python's
`Protocol` doesn't have method implementations — the `@runtime_checkable`
isinstance check only verifies attribute presence. A separate helper
keeps the Protocol clean and lets adapter authors choose:

- *"I can stream natively"* → implement `complete_streaming` directly
  (Ollama in Phase 10).
- *"I can't stream"* → `def complete_streaming(self, ...): yield from
  wrap_complete_as_stream(self, ...)`.

Either way, the adapter satisfies the Protocol; the test doubles in
slice 1's test suite take the second form and become a one-line
addition.

### 2.3 FuniStreamChunk schema

**Decision:** A frozen, slots-True dataclass at
`src/ember/schemas/stream.py`:

```python
@dataclass(frozen=True, slots=True)
class FuniStreamChunk:
    text_delta: str
    done: bool
    finish_reason: FinishReason | None = None
    model_id: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
```

- `text_delta` carries only the *new* tokens since the last chunk —
  not the cumulative text. Munnr's render layer appends; the model's
  total reply is `"".join(c.text_delta for c in chunks)`.
- `done=False` for every non-final chunk; `done=True` for exactly one
  final chunk per stream.
- `finish_reason`, `prompt_tokens`, `completion_tokens` are populated
  on the final chunk only; `None` otherwise. (Ollama's stream protocol
  only reports totals on the final response.)
- `model_id` may appear on any chunk; Ollama sends it on every chunk
  for free, but operators only need it once.

### 2.4 Failure folding — same shape as non-streaming `complete()`

**Decision:** A mid-stream error (URL error, server died, non-JSON
line, malformed final chunk) yields a single final chunk with
`done=True`, `finish_reason=FinishReason.ERROR`, and an
operator-readable error message in `text_delta`. The stream then
terminates.

**Why:** matches the slice-1 pattern from `Funi.complete()` (ADR 0007
§2.2 — typed-value-over-exception). Munnr's render layer treats
streaming errors identically to non-streaming errors: render the
error text, tag with `[ember reported an error]`. The Vow of
Graceful Offline holds at the streaming boundary the same way it
holds at every other realm boundary.

### 2.5 Tool refusal is immediate

**Decision:** Calling `complete_streaming(prompt, context, tools=[...])`
where `tools` is non-empty yields a single final chunk with
`finish_reason=FinishReason.ERROR` and empty `text_delta` — the same
shape `complete()` uses in slice 1.

**Why:** tool use is ADR 0011's territory; until that ships, the
slot is reserved. Streaming behaviour must mirror non-streaming
behaviour for tool-call requests.

### 2.6 `FuniConfig.streaming` opt-out

**Decision:** `FuniConfig` gains a `streaming: bool = True` field.
Operators who want to revert to the slice-1 batched behaviour can set
`funi.streaming: false` in their `ember.yaml`. Munnr's Phase-11
render code branches on this flag.

**Why default true:** streaming is the better UX in almost every case.
Operators who hit specific issues (terminal rendering bugs, piped
output, log capture systems that don't handle byte streams well) can
opt out per ADR 0008's overlay rules.

### 2.7 NDJSON line-buffered reading for Ollama

**Decision:** OllamaFuni's `complete_streaming` reads Ollama's
`POST /api/chat` response with `"stream": true` line-by-line and
parses each line as JSON. Empty lines are skipped. Malformed JSON
lines yield an ERROR chunk and terminate the stream.

**Why line-buffered:** Ollama sends one JSON object per line
(newline-delimited JSON, NDJSON). `urllib.request.urlopen` returns a
file-like response; iterating it yields bytes-per-newline-chunk.
Stdlib only, no SSE parser required.

### 2.8 Where streaming code lives

| New | Why |
|---|---|
| `src/ember/schemas/stream.py` | `FuniStreamChunk` is a cross-subpackage type. |
| `src/ember/spark/funi/handle.py` (touched) | Protocol slot + `wrap_complete_as_stream` helper. |
| `src/ember/spark/funi/ollama/adapter.py` (touched) | Native `complete_streaming` implementation. |
| `src/ember/schemas/config.py` (touched) | `FuniConfig.streaming` opt-out. |

Munnr's render integration is Phase 11, not this ADR's
implementation phase.

## 3. Consequences

### 3.1 What becomes true after Phase 10 (this ADR's part 1)

- `FuniHandle` Protocol declares `complete_streaming`. Every existing
  adapter (`OllamaFuni`, test doubles) implements it.
- `OllamaFuni.complete_streaming` produces incremental chunks against
  the real Ollama `/api/chat?stream=true` endpoint.
- `FuniConfig.streaming` exists and defaults to `True`.
- No caller actually consumes the streaming path yet — Munnr still
  uses `complete()`. Phase 11 wires the consumer.

### 3.2 What becomes true after Phase 11 (Munnr integration)

- `ember chat` renders incrementally when `funi.streaming=True`.
- Operator Ctrl-C aborts mid-stream cleanly — partial text becomes the
  Episode's `ember_reply` with a `[interrupted by operator]` tag.
- Suggested release at 0.1.7 (streaming live).

### 3.3 Risks

- **Adapter authors forget to implement `complete_streaming`** for new
  runtimes. Mitigation: the Protocol declares it as required (not
  optional); `wrap_complete_as_stream` makes the fallback a one-liner.
- **NDJSON parsing edge cases** — Ollama sends one object per line,
  but partial lines split across `urlopen` reads are possible if the
  underlying read buffer fills mid-line. Mitigation: use the
  response's iterator (yields per-line), not raw bytes.
- **Token-count accuracy** — only the final chunk has totals; if the
  stream terminates abnormally (URL error mid-stream), totals stay
  `None`. Munnr's `add_episode` handles this gracefully.
- **`FuniConfig.streaming` defaults true changes operator behaviour**
  for upgrades from 0.1.5 → 0.1.7. Documented in DEVLOG and INSTALL.md
  Phase-11 sidebar; operators with custom terminal-render-sensitive
  setups opt out via config.

## 4. Alternatives considered

| Alternative | Why not |
|---|---|
| Separate `StreamingFuniHandle` Protocol that extends `FuniHandle` | Forces Spark code to branch on capability; complicates the registry. Single Protocol with both methods is simpler. |
| Default Protocol method body via a stub mixin class | Mixins don't compose well with Protocol checks; adapter authors would need to inherit specifically. Helper function is cleaner. |
| Server-Sent Events (SSE) instead of NDJSON | Ollama uses NDJSON; we'd be parsing SSE on top of it for no benefit. |
| Return full reply + a `chunks` field on `FuniReply` | Loses the actual incremental UX — operator still waits for the whole reply before any render. The point of streaming is the unfolding. |
| Make `complete()` the optional method (deprecate it) | Breaks every existing test + caller. `complete()` is the simpler API for non-interactive use. |
| `async def` iterators instead of sync | Ember has no async runtime; adding one for one feature breaks the Vow of Smallness. Stdlib-sync iterators work fine on a single REPL loop. |

## 5. Open follow-ups

- **Streaming for the embed endpoint** is not in scope — embeddings
  are batched by design.
- **Backpressure / cancellation** beyond Ctrl-C (e.g. operator types
  another prompt while the previous stream is in flight) — out of
  scope for slice 2; Munnr's REPL is single-line at a time.
- **Streaming to non-terminal surfaces** (the future Bifröst HTTP
  gateway in ADR 0012+) will need its own transport wrapping; the
  Protocol shape stays the same.

## 6. Provenance

This ADR was authored at the start of Phase 10 of
`EMBER_SECOND_SLICE_PLAN.md`. The Phase-10 implementation lands in the
same commit as this document. Phase 11 (Munnr render + Ctrl-C) lands
in the next commit.

— Eirwyn Rúnblóm (Scribe), with Rúnhild (Architect) and Eldra (Forge Worker)
