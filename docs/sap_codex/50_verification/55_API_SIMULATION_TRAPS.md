---
codex_id: 55_API_SIMULATION_TRAPS
title: API Simulation Traps — Where OpenAI-Compat Adapters Leak Under Load
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - py/ClaudeAsOpenAI.py:1-206
  - py/GeminiAsOpenAI.py:1-203
  - py/dify_openai.py:1-165
ember_subsystem_targets: [Strengr, Smiðja]
cross_refs:
  - 20_interface/21_OPENAI_COMPAT_API
  - 50_verification/53_SECURITY_REVIEW
  - 50_verification/57_FAILURE_TAXONOMY
---

# API Simulation Traps — Where OpenAI-Compat Adapters Leak Under Load

> *Sólrún, voice cold and even: "OpenAI-compatible" is the most popular lie in 2025-2026 LLM tooling. SAP ships three of them. Each lie is uniformly shaped at the surface and uniquely shaped at the seam. This document is the seam-by-seam teardown.*

This document is a deeper read of the same three files audited at the interface layer ([[21_OPENAI_COMPAT_API]]) — but here the lens is **failure-under-load**: what breaks when the adapter sees real traffic, real edge cases, real multi-call concurrency, real token accounting?

The interface doc named the lies. This doc lists the production scars they will produce.

---

## 1. Token Counting — The Most Common Trap

OpenAI's `usage` block looks like:

```json
"usage": {
  "prompt_tokens": 123,
  "completion_tokens": 45,
  "total_tokens": 168
}
```

Three adapters, three different lies about this block.

### 1.1 Claude — usage.prompt_tokens omits cache tokens

Claude's native usage shape (from Anthropic SDK):

```json
{
  "input_tokens": 100,
  "cache_creation_input_tokens": 200,
  "cache_read_input_tokens": 800,
  "output_tokens": 45
}
```

When LiteLLM normalizes this to OpenAI shape (which `ClaudeAsOpenAI.py` returns verbatim from `litellm.acompletion`), the result depends on the LiteLLM version. At time of SAP's `uv.lock` pin (verified from `/tmp/super-agent-party/uv.lock`), LiteLLM maps `input_tokens` → `prompt_tokens` and **does not surface cache_creation/cache_read** in the top-level `usage`. Cache tokens are visible in `usage.cache_creation_input_tokens` if you reach into the LiteLLM-extended object — but a caller written against the OpenAI Pydantic types sees only `prompt_tokens`.

**Cost implication:** On a 100k-token cached-prefix call, the operator reads `prompt_tokens=100` and believes they spent 100 input tokens. They actually spent 100 + (200 × 1.25) + (800 × 0.1) = 100 + 250 + 80 = 430 in Anthropic-billed equivalent. The dashboard is **wrong by 4.3×**.

`ClaudeAsOpenAI.py:206` returns `await litellm.acompletion(...)` raw. There is no `usage` normalizer in SAP. Whatever LiteLLM emits is what the caller sees.

### 1.2 Gemini — usage.prompt_tokens may be reported by Google's own count

Gemini's native usage shape is `usageMetadata.promptTokenCount` + `usageMetadata.candidatesTokenCount`. LiteLLM normalizes. But Google's tokenizer differs from OpenAI's. A 1000-character English prompt is ~250 tokens by OpenAI's tiktoken, ~280 tokens by Gemini's SentencePiece. Cost is computed correctly *if* the operator reads the right line. SAP, displaying `usage.prompt_tokens` in a unified UI labeled "tokens used," conflates the two tokenizers' meanings.

This is not a bug *in SAP*; it is a documentation absence. The UI label "tokens used" is ambiguous across providers.

### 1.3 Dify — no usage at all

`dify_openai.py:94-106` constructs `ChatCompletion` without a `usage` block:

```python
return ChatCompletion(
    id="super-agent-party",
    object="chat.completion",
    created=int(asyncio.get_event_loop().time()),
    model=model,
    choices=[
        Choice(
            index=0,
            message=ChatCompletionMessage(role="assistant", content=answer),
            finish_reason="stop",
        )
    ],
)
```

`usage=` is not passed. The OpenAI Pydantic model accepts `None` (it's optional). Callers reading `response.usage.prompt_tokens` get `AttributeError: 'NoneType' object has no attribute 'prompt_tokens'`. Or, with the Python `or 0` idiom, silently get zero.

Dify's API actually returns token counts in the `message_end` streaming event. SAP's adapter discards them.

**Cost implication:** A Dify-heavy operator sees "0 tokens" in cost displays and overruns their budget.

---

## 2. System Prompt Handling — The Lossy Mapping

OpenAI: `messages = [{"role": "system", ...}, {"role": "user", ...}, ...]`. Multiple system messages are allowed and concatenated.

### 2.1 Claude — system message moves out of messages

Claude's native API has a top-level `system` parameter, not a message with role=system. LiteLLM moves OpenAI-shaped system messages to the `system` parameter. But LiteLLM's behavior on *multiple* system messages varies by version — some versions concatenate, some take only the first.

`ClaudeAsOpenAI.py:170-175` constructs `completion_kwargs` and hands it to LiteLLM without intervening on `messages`. The adapter does no system-message normalization. The behavior is "whatever LiteLLM does at the pinned version."

A caller who depends on three system messages (e.g. one for persona, one for tools, one for safety) gets different behavior on Claude vs OpenAI vs Gemini.

### 2.2 Gemini — system message implementation depends on version

Gemini's native API has `systemInstruction` at the top level. The OpenAI-compat layer Google provides accepts `messages` with role=system but maps to `systemInstruction`. LiteLLM does its own mapping. Three layers, three potentially different behaviors.

### 2.3 Dify — system message becomes `inputs["system"]`

`dify_openai.py:60-64`:

```python
query = messages[-1]["content"] or ""
inputs: Dict[str, Any] = {}
for m in messages[:-1]:
    role = m["role"]
    if role != "user":
        inputs[role] = m["content"]
```

The last message is the user query. Every other message becomes `inputs[role] = content` — keyed by role. **The last message of each role wins.** Three system messages collapse to the last system message. Three assistant messages collapse to the last assistant message. The caller has no idea.

If the conversation is `[system_persona, user1, assistant1, system_tools, user2, assistant2, user3]`, what Dify sees is:
- query = "user3 content"
- inputs = `{"system": "system_tools content", "assistant": "assistant2 content"}`

The persona system message and assistant1 are gone. **The conversation has been silently lobotomized.**

---

## 3. Tool Call Format Differences

OpenAI tool calls return:

```json
"tool_calls": [
  {"id": "call_abc", "type": "function", "function": {"name": "foo", "arguments": "{\"x\": 1}"}}
]
```

Where `arguments` is a JSON-string.

### 3.1 Claude — tool_use blocks become OpenAI tool_calls via LiteLLM

Claude returns `content` blocks of type `tool_use`. LiteLLM normalizes to `tool_calls` shape — including stringifying the arguments JSON. Mostly correct. But Claude's `input` object can contain native Python-types (numbers, booleans) that get JSON-stringified — and LiteLLM's stringification may differ from how OpenAI emits them (whitespace, key ordering, escaping). A caller that compares tool-call arguments as strings (rather than parsing) sees instability.

The adapter ships no tool-call normalizer. The behavior is again LiteLLM-version-dependent.

### 3.2 Gemini — function_call vs tool_calls

Gemini emits `functionCall` (singular) in its native API. The OpenAI-compat layer Google provides maps to `tool_calls`. LiteLLM does its own mapping when going through native Gemini. Through the `is_official` path (`GeminiAsOpenAI.py:89-94`) the format is one thing; through the `is_openai_proxy` path it is another.

A caller with two configurations of the same Gemini model — direct Google API vs OpenAI-compat proxy — sees different tool-call shapes for the same prompt.

### 3.3 Dify — tools are not supported at all

`dify_openai.py:50-57` — `create` accepts `**_` (ignored kwargs). Tools passed in are silently dropped. Tool calls back are never emitted. The caller that pipes Dify through an agent loop expecting tool calls gets only text replies forever.

The adapter does not say "tools not supported." It says nothing.

---

## 4. Streaming Chunk Semantics

OpenAI's streaming chunks:

- `delta.content` for content additions
- `delta.tool_calls` with index-aligned partial tool calls
- `delta.role = "assistant"` only on first chunk
- `finish_reason` only on final chunk
- `usage` only on final chunk (if `stream_options.include_usage=True`)

### 4.1 Claude — content_block_delta translation

LiteLLM translates Claude's `content_block_delta` events to OpenAI `delta.content`. Mostly correct. But Claude has:

- `thinking` blocks (extended-thinking models) — LiteLLM may or may not surface these as `delta.reasoning_content` depending on version
- `text` blocks (normal output) — surfaces as `delta.content`
- `tool_use` blocks (tool calls) — surfaces as `delta.tool_calls`
- `ping` events (heartbeat) — should be silently consumed; some LiteLLM versions surface as empty chunks

`ClaudeAsOpenAI.py:206` returns the stream raw. A caller checking `chunk.choices[0].delta.content` will see empty strings from ping events on bad-LiteLLM-version paths.

### 4.2 Gemini — chunk boundaries differ

Gemini streams whole-token chunks; OpenAI streams sub-word chunks. The *granularity* differs. A UI that types-out the response character-by-character sees Gemini "bursts" of tokens, not the smooth stream of OpenAI. Functionally correct, perceptually different.

### 4.3 Dify — terminal chunk is forced to "stop"

`dify_openai.py:152-159`:

```python
yield ChatCompletionChunk(
    id="super-agent-party",
    object="chat.completion.chunk",
    created=int(asyncio.get_event_loop().time()),
    model=model,
    choices=[ChunkChoice(index=0, delta=ChoiceDelta(), finish_reason="stop")],
)
```

`finish_reason="stop"` always. If Dify hit a length limit, content filter, or tool gate, the caller never knows. Retries based on `finish_reason="length"` don't fire.

### 4.4 Dify — initial delta only on first non-empty event

`dify_openai.py:131-136`:

```python
delta = event.get("answer") or ""
if first and delta:
    cid = event.get("conversation_id")
    if cid and not conversation_id:
        delta = f"<conversion id:{cid}>\n\n{delta}"
    first = False
```

`first` is set to `False` only when `delta` is non-empty. If the first Dify event is empty (which can happen with agent_message types), `first` stays `True` for the next non-empty event. The `<conversion id:...>` marker is prepended to whichever delta happens to be the first non-empty one — which may not be the first chunk of actual content. This corrupts the *content* of the early stream.

---

## 5. Error Mapping

OpenAI's exception hierarchy: `OpenAIError`, `APIError`, `APIConnectionError`, `APITimeoutError`, `RateLimitError`, `BadRequestError`, etc. Callers catch specific types for specific retry logic.

### 5.1 Claude / Gemini — LiteLLM-shaped errors

LiteLLM raises its own exception types. `litellm.exceptions.RateLimitError`, etc. Some are subclasses of OpenAI's; some are not. A caller that catches `openai.RateLimitError` may not catch LiteLLM's variants in some versions.

`ClaudeAsOpenAI.py` and `GeminiAsOpenAI.py` propagate LiteLLM exceptions raw. The caller sees LiteLLM types when they expected OpenAI types.

### 5.2 Dify — all errors become `httpx.HTTPStatusError`

`dify_openai.py:84-87`:

```python
resp = await self._outer._client.post(url, json=payload, headers=headers)
resp.raise_for_status()
data = resp.json()
```

Dify errors become `httpx.HTTPStatusError`. The caller catching `openai.BadRequestError` for a 400 catches nothing. Retry logic that distinguishes 429 from 500 must check `e.response.status_code` directly.

This is the same class of bug across all three: the OpenAI-compat lie does not extend to exceptions.

---

## 6. Concurrency Hazards

### 6.1 GeminiAsOpenAI — global env mutation per call

Already named in `[[53_SECURITY_REVIEW]]` §6.1 and `[[21_OPENAI_COMPAT_API]]` §4.1. Repeated here because under *load*, the race window is real:

```python
# /tmp/super-agent-party/py/GeminiAsOpenAI.py:67-69
if self._parent.api_key:
    os.environ["GEMINI_API_KEY"] = self._parent.api_key
    os.environ["GOOGLE_API_KEY"] = self._parent.api_key
```

Two concurrent calls with different keys (multi-tenant; or just two requests with different API key configurations):

1. Call A writes key_A to env
2. Call B writes key_B to env
3. Call A reads env (in LiteLLM internals), gets key_B
4. Call A's request goes out with key_B
5. Audit log shows call A but call B's account is billed

There is no way to fix this without rewriting how LiteLLM reads credentials. SAP's adapter must not be used multi-tenant.

### 6.2 Dify — long-lived AsyncClient

`dify_openai.py:26`:

```python
self._client = httpx.AsyncClient(timeout=60)
```

Created in `__init__`. Never closed unless someone calls `close()`. SAP code doesn't. Connection pool grows; sockets leak.

Under sustained load this becomes an FD exhaustion path.

### 6.3 Claude / Gemini — lazy LiteLLM import not thread-safe

`ClaudeAsOpenAI.py:29-38`:

```python
@property
def _litellm(self):
    if self._litellm_module is None:
        import litellm
        self._litellm_module = litellm
    return self._litellm_module
```

No lock. Two concurrent calls on the *same* adapter instance both see `self._litellm_module is None`, both import, both assign. `import` is idempotent at the module level, so the second assignment is harmless — but if `litellm`'s init has side effects (it does: it reads env vars), the side effects can race.

In practice: low impact. A thread-safety nit.

---

## 7. Model Name Mangling

### 7.1 Claude — anthropic/ prefix forced

`ClaudeAsOpenAI.py:164-165`:

```python
if not model.startswith("anthropic/"):
    model = f"anthropic/{model}"
```

User passes `claude-3-5-sonnet-20241022`. Adapter rewrites to `anthropic/claude-3-5-sonnet-20241022`. Correct for LiteLLM routing.

But: a user passes `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0` (AWS Bedrock). The adapter rewrites to `anthropic/bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0`. LiteLLM cannot route this. The user wanted Bedrock; the adapter forced direct Anthropic.

This is a "we know what you want" assumption that fails on out-of-pattern model strings.

### 7.2 Gemini — split('/')[-1] mangles vendor-prefixed names

`GeminiAsOpenAI.py:92`:

```python
clean_model = raw_model.split('/')[-1]
completion_kwargs["model"] = f"gemini/{clean_model}"
```

User passes `vertex_ai/gemini-1.5-pro`. Split → `gemini-1.5-pro`. Prepend `gemini/` → `gemini/gemini-1.5-pro`. The vertex_ai prefix is lost. LiteLLM routes to Google AI Studio, not Vertex.

A user with Vertex credentials sees billing land on Google AI Studio (if they happen to also have AI Studio creds in env, leaked via the env-mutation path above). Confusing failure.

---

## 8. Cross-References

- [[21_OPENAI_COMPAT_API]] — interface-level analysis of the same three files
- [[53_SECURITY_REVIEW]] — `os.environ` mutation as security issue
- [[54_DEPENDENCY_HEALTH]] — LiteLLM as trust hinge for two adapters
- [[57_FAILURE_TAXONOMY]] — the failures here, ranked
- [[58_OBSERVABILITY_GAPS]] — `print()` as failure signal
- [[hermes:HEM-30_LLM_ADAPTER]] — Hermes's adapter contract as positive counter

---

## What This Means for Ember

**Adopt:**
- Adopt LiteLLM as the **multi-vendor routing layer** — it does the heavy lifting and SAP's bet on it is reasonable. But adopt it at *one* place in the stack, not three. Ember has a single LLMAdapter that uses LiteLLM internally and exposes Ember's typed contract externally.

**Adapt:**
- Adapt the `_convert_tools` pattern (`ClaudeAsOpenAI.py:97-118`) into a **vendor-capability declaration + conversion table**. Each vendor declares its tool-shape; the conversion is data-driven, not hardcoded in a loop with magic strings.
- Adapt the auto-detection logic (`GeminiAsOpenAI.py:75-82`) into an **explicit `endpoint_kind` parameter on the adapter constructor**. The user declares whether the endpoint is official, proxy, or native. No URL substring sniffing.

**Avoid:**
- **Avoid silent token-count loss** (cache tokens missing from Claude; missing entirely from Dify). Ember's `UsageReport` is a *typed structure* that names cache_creation, cache_read, prompt_native, prompt_normalized, completion. Every vendor maps into this; gaps are explicit `None` not silent zero.
- **Avoid the `messages[:-1] for ... inputs[role]=content` pattern** (`dify_openai.py:60-64`). It silently destroys conversation history.
- **Avoid forcing `finish_reason="stop"` on all stream endings.** Use what the upstream said.
- **Avoid model-name mangling without first checking for vendor-prefix sentinels.** Hands off names that start with `bedrock/`, `vertex_ai/`, `azure/`, etc.
- **Avoid one-import-per-adapter for heavy SDKs** — Ember imports LiteLLM once at process start in a known place, not lazily per-call. Lazy import has its merits for cold start, but the loss of import-time error visibility outweighs them for production paths.

**Invent:**
- **TypedRequest / TypedResponse / TypedDelta**. Ember's LLMAdapter speaks a Pydantic-typed contract internally. Vendor-specific shapes live only at the boundary. The OpenAI shape is a *consumer* of the typed contract, not the typed contract itself.

- **Capability-Probed Adapter Registration.** At adapter registration, fire a probe call that tests each capability: does this endpoint emit `usage`? does it support tools? does it support multi-system? Cache the result with TTL (Vow of Cache Discipline). Surface mismatches as warnings before traffic hits them.

- **Token-Reconciliation Telemetry.** Every adapter call reports two token counts: the vendor's claim and Ember's recomputation (via the vendor's tokenizer). Drift over threshold triggers a warning event. Helps detect tokenizer mismatches early.

- **Conversation Continuity Witness.** Every adapter that uses a session id (Dify-style) carries the session id in a `SessionHandle` that the caller passes explicitly. Smuggling the id into message content is rejected at construction time. Vow of **Defended System Prompt** for *session state*.

- **Per-Vendor Stream Normalizer.** Streams are normalized to Ember's `TypedDelta` at the adapter boundary, never raw-LiteLLM. Vendors emit different chunk shapes; Ember's downstream code sees one shape. Tests verify equivalence across vendors with golden-streams.

- **Multi-System Message Policy.** Ember declares: "Ember always sends exactly one system message." Multi-system is a no-op (concatenated at the adapter). This kills the cross-vendor drift at the source. Vow of **Defended System Prompt** extended: the system message is typed, single, and final.
