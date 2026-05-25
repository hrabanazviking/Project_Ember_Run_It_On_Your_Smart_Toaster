---
codex_id: 21_OPENAI_COMPAT_API
title: OpenAI-Compat Simulation — Where Claude, Gemini, and Dify Pretend to Be OpenAI
role: Auditor
layer: Interface
status: draft
sap_source_refs:
  - py/ClaudeAsOpenAI.py:1-206
  - py/GeminiAsOpenAI.py:1-203
  - py/dify_openai.py:1-165
ember_subsystem_targets: [Strengr, Smiðja, Munnr]
cross_refs:
  - 50_verification/55_API_SIMULATION_TRAPS
  - 50_verification/53_SECURITY_REVIEW
  - 10_domain/12_AGENT_CORE_DOMAIN
---

# OpenAI-Compat Simulation — Where Claude, Gemini, and Dify Pretend to Be OpenAI

> *Sólrún, voice cold and even: every adapter that says "I am OpenAI" is lying. The interesting question is what shape the lie takes, and which seam tears first when the lie meets traffic.*

SAP exposes a unified `AsyncOpenAI`-shaped client surface so the rest of the codebase — agent loops, the IM bots, the livestream router, the affection extractor — can call `client.chat.completions.create(...)` without caring which vendor sits beneath. Three modules implement that lie: `py/ClaudeAsOpenAI.py` (Anthropic via LiteLLM), `py/GeminiAsOpenAI.py` (Google AI Studio / Vertex / proxy via LiteLLM), and `py/dify_openai.py` (Dify workflow service via raw `httpx`). They share an external contract. They share almost nothing internally. The contract leaks differently in each.

This document audits the simulation layer as a contract — not as three independent files. The question I keep asking: *if my agent code believes this object is `AsyncOpenAI`, what will it learn the hard way?*

---

## 1. The Subject — Three Simulators, One Pretense

`ClaudeAsOpenAI.py:5-27` defines `AsyncClaudeAsOpenAI`, a class that quacks like `openai.AsyncOpenAI` and routes to LiteLLM under the hood. The docstring is honest about the intent:

```python
# /tmp/super-agent-party/py/ClaudeAsOpenAI.py:5-9
class AsyncClaudeAsOpenAI:
    """
    完全模拟 AsyncOpenAI 客户端，底层用 litellm.acompletion（懒加载）
    """
```

Translation: "completely simulates the AsyncOpenAI client, backed by litellm.acompletion (lazy-loaded)." The word the author chose is **simulate** (`模拟`). That is the right word. It is also the load-bearing word. A simulator that becomes load-bearing in production *will* be tested in ways its author did not anticipate.

`GeminiAsOpenAI.py:5-9` repeats the pattern with even more ambition — it must autodetect three different gateway flavors at runtime:

```python
# /tmp/super-agent-party/py/GeminiAsOpenAI.py:5-9
class AsyncGeminiAsOpenAI:
    """
    完全模拟 AsyncOpenAI 客户端，底层用 litellm.acompletion
    自适应兼容：官方 Google AI Studio 直连、OpenAI 中转站、Gemini 专属网关
    """
```

`dify_openai.py:17-26` does not pretend it is a full client — it claims only to align with the `async` chat-completions call shape:

```python
# /tmp/super-agent-party/py/dify_openai.py:17-26
class DifyOpenAIAsync:
    """
    纯 httpx 封装的 Dify → OpenAI 适配器
    外部接口完全对齐 OpenAI 官方 SDK 的 async 调用方式
    """

    def __init__(self, *, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        ...
```

Three shapes of lie, one pretense.

---

## 2. The Contract The Three Adapters Claim to Honor

A caller that uses any of these three objects expects, at minimum:

- `client.chat.completions.create(model, messages, stream, ...)` returns either a `ChatCompletion` (when `stream=False`) or an async iterator of `ChatCompletionChunk` (when `stream=True`).
- `client.models.list()` returns something with `.data` whose items have `.id`.
- Exceptions follow OpenAI's family (timeout → `APITimeoutError`, etc.).
- Token usage is reported on every response.
- `tools=...` accepts the OpenAI function-tool shape; tool calls come back on `choice.message.tool_calls` or as streamed deltas.

None of the three adapters honors all five. Let me name where each one breaks.

---

## 3. ClaudeAsOpenAI — The Quiet Lies

### 3.1 Models list silently returns empty on failure

`ClaudeAsOpenAI.py:48-95` — `models.list()` tries to call `/v1/models`. On 200 it parses. On any error or non-200 it prints a Chinese error to stdout and returns an empty list:

```python
# /tmp/super-agent-party/py/ClaudeAsOpenAI.py:90-95
            except Exception as e:
                print(f"动态获取 Anthropic 模型列表失败 (可能代理/代理商不支持): {e}")

            # [静态兜底方案]：如果请求报错或代理商 API 未实现 /models 端点，返回常见的 Claude 模型
            fallback_models =[]
            return ModelList([ModelItem(m) for m in fallback_models])
```

The static-fallback comment says "common Claude models" — but the list is **empty**. The comment lies about what the code does. A caller using `client.models.list()` to populate a UI dropdown will see "no models" on any flake; it is indistinguishable from "no models registered." There is no error surface. There is no log channel. There is `print()`, going to whichever stream the host process inherited.

That is a swallowed failure mode. A caller writing `if not (await client.models.list()).data: raise ConfigError("Claude not configured")` will conflate "Anthropic is down" with "user has no Claude key."

### 3.2 Tool-type leakage

`ClaudeAsOpenAI.py:97-118` converts OpenAI tools to Claude tools. It supports `function` and a hardcoded list of two web-search tool versions (`web_search_20250305`, `web_search_20260209`). Everything else it silently drops:

```python
# /tmp/super-agent-party/py/ClaudeAsOpenAI.py:104-118
        for tool in tools:
            tool_type = tool.get("type")
            
            if tool_type == "custom":
                continue  # Claude 不支持
            elif tool_type == "function":
                ...
            elif tool_type in ["web_search_20250305", "web_search_20260209"]:
                claude_tools.append(tool)
                
        return claude_tools if claude_tools else None
```

A caller passing OpenAI's `code_interpreter`, `file_search`, or `computer_use` tools gets neither a result nor a warning. Their tool was dropped on the floor. If they had three tools and all three were unsupported, they get `None` back — and the call proceeds *without tools at all*. That is not a port; that is a censor with a polite smile.

### 3.3 The kwargs filter is a hard-coded denylist

`ClaudeAsOpenAI.py:202-204`:

```python
# /tmp/super-agent-party/py/ClaudeAsOpenAI.py:202-205
                # 过滤 OpenAI 特有参数
                safe_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ['logprobs', 'top_logprobs', 'response_format', 'n']}
                
                return await litellm.acompletion(**completion_kwargs, **safe_kwargs)
```

The denylist names four parameters Claude does not support. It is **incomplete** — OpenAI has `seed`, `logit_bias`, `parallel_tool_calls`, `service_tier`, `audio`, `modalities`, `prediction`, `web_search_options`, plus the entire response-format ecosystem (`json_schema`, `text.format`, etc.). Most of those will reach LiteLLM, which will either pass them to Claude (and 400) or silently drop them. A denylist is structurally incomplete the moment OpenAI ships a new parameter. The correct shape is allowlist-by-claude-capability, not denylist-by-author's-memory.

### 3.4 No usage normalization

The adapter returns whatever LiteLLM returns. LiteLLM does coerce many shapes, but its `usage.prompt_tokens` for Claude is computed via Anthropic's own counting (input vs output), and the *cache control* tokens (`cache_creation_input_tokens`, `cache_read_input_tokens`) are not surfaced in the OpenAI usage shape. A caller computing cost from `usage.prompt_tokens` will be wrong on any cached-prefix Claude call. See `[[55_API_SIMULATION_TRAPS]]` §3 for the table.

### 3.5 No stream-event normalization

OpenAI streams `ChatCompletionChunk` with `choice.delta.content` and `choice.delta.tool_calls`. Claude streams `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, *plus* `ping` events. LiteLLM does the translation. But LiteLLM is a moving target — at the time SAP's `uv.lock` was pinned, the translation lossed Anthropic `thinking` blocks under some configurations. SAP carries no test of stream-shape equivalence. The bug, when it appears, will show as "the model trails off mid-sentence on Claude but not OpenAI."

---

## 4. GeminiAsOpenAI — The Loud Lies

### 4.1 Global environment mutation per call

`GeminiAsOpenAI.py:66-69` is the most dangerous five lines in the file:

```python
# /tmp/super-agent-party/py/GeminiAsOpenAI.py:65-69
                # 【防御机制 1】强制注入环境变量，防止 LiteLLM 误判降级到 Vertex AI 验证流
                if self._parent.api_key:
                    os.environ["GEMINI_API_KEY"] = self._parent.api_key
                    os.environ["GOOGLE_API_KEY"] = self._parent.api_key
```

**Every chat completion writes the API key to the process-global environment.** The author calls this "Defense Mechanism 1" in a Chinese comment — to stop LiteLLM from falling through to Vertex auth flow. The fix is correct for that symptom and **wildly wrong** as a pattern:

- Two concurrent calls with different keys (e.g. a multi-tenant server) race. The last writer wins. The earlier-call's request then completes with the wrong key in the environment.
- Any subprocess spawned after this point inherits the key. A code interpreter (`code_interpreter.py:11`) launched downstream sees the live API key in `os.environ`.
- A process introspection (`/proc/self/environ`, on Linux) leaks the key to any process running as the same user.
- Multi-key rotation becomes impossible: there is no way to scope a key to a single call.

This is not a "best practice violation." This is a credential leakage path with concurrency-unsafe semantics. The `[[53_SECURITY_REVIEW]]` doc catalogs this as a confirmed STRIDE Information-Disclosure vulnerability.

### 4.2 URL-pattern routing is fragile

`GeminiAsOpenAI.py:76-82` decides between three routing modes via substring sniffing:

```python
# /tmp/super-agent-party/py/GeminiAsOpenAI.py:75-82
                # 判断是否为标准的 OpenAI 格式中转代理（如 OneAPI, NewAPI 等）
                is_openai_proxy = False
                if base_url_str:
                    cleaned_url = base_url_str.rstrip('/')
                    if cleaned_url.endswith('/v1') or "api." in cleaned_url or "proxy" in cleaned_url:
                        if "generativelanguage.googleapis.com" not in cleaned_url:
                            is_openai_proxy = True
```

The detection logic is: "URL ends with `/v1`, or contains `api.`, or contains `proxy`." Any caller hosting a Gemini proxy at `https://my-gemini.example.com/` (no `/v1`, no `api.`, no `proxy`) will be routed as `is_official=False AND is_openai_proxy=False` — i.e. **scenario C**, which sets `custom_llm_provider="gemini"` and passes the URL as `api_base`. That may or may not work depending on how the proxy actually speaks.

This is heuristic routing on a config value the user is expected to set correctly. There is no `vendor` field on the request itself. The cure: name the wire format on the request, not on a URL substring.

### 4.3 Same kwargs filter, same incompleteness

`GeminiAsOpenAI.py:125-126` repeats the four-parameter denylist verbatim. Gemini has *different* incompatibilities than Claude (e.g. `frequency_penalty` and `presence_penalty` were not supported in early Gemini OpenAI-compat endpoints; `tool_choice="required"` is supported but `"none"` is not). The denylist is identical to Claude's. The class is therefore wrong by inheritance, not by design.

### 4.4 Models list `print()` to stdout

`GeminiAsOpenAI.py:198-202` matches Claude's: error → print, return empty list, no log channel. Same swallowed failure.

---

## 5. Dify — The Honest, Smaller Lies

Dify's adapter is the most narrowly scoped and therefore the least dangerous. But it has its own seams.

### 5.1 Conversation-id stowed inside assistant message content

`dify_openai.py:34-41` extracts the Dify conversation id from a *string literal* embedded in a prior assistant message:

```python
# /tmp/super-agent-party/py/dify_openai.py:34-41
    @staticmethod
    def _extract_conv_id_from_messages(messages: List[ChatCompletionMessageParam]) -> str | None:
        for m in messages:
            if m["role"] == "assistant":
                m_content = m.get("content") or ""
                if match := re.search(r"<conversion id:(.*?)>", m_content):
                    return match.group(1).strip()
        return None
```

(The string is `<conversion id:...>` — yes, the author misspelled "conversation" as "conversion" and it is now wire-protocol.) The adapter then prepends this string to the *next* response on `dify_openai.py:91-92` so future calls can extract it again:

```python
# /tmp/super-agent-party/py/dify_openai.py:89-92
                cid = data.get("conversation_id") or ""
                answer = data.get("answer") or ""
                if not conversation_id and cid:
                    answer = f"<conversion id:{cid}>\n\n{answer}"
```

This means: every conversation that uses Dify carries a side-channel marker in the assistant message body that is **invisible to the caller's other tooling**. If the caller's memory subsystem (Brunnr equivalent) stores assistant messages verbatim and replays them, the marker survives. If the caller cleans assistant output (markdown render, redaction, summarization), the marker dies and conversation continuity breaks silently.

This is conversation state laundered through the message body. The OpenAI contract has no concept of session ids — Dify needs one — so the author smuggled it into the content. It is a clever hack and a future bug.

### 5.2 No `usage` field on Dify responses

`dify_openai.py:94-106` constructs `ChatCompletion` without a `usage` block. Callers that compute cost or rate-limit on token counts will see `None` / missing field and either crash or silently treat usage as zero. Dify's own API does return token counts in the streaming `message_end` event — the adapter ignores it.

### 5.3 Multi-turn `messages` collapsed to `inputs`

`dify_openai.py:60-64`:

```python
# /tmp/super-agent-party/py/dify_openai.py:59-65
            query = messages[-1]["content"] or ""
            inputs: Dict[str, Any] = {}
            for m in messages[:-1]:
                role = m["role"]
                if role != "user":
                    inputs[role] = m["content"]
```

Only the last message becomes the Dify `query`. All earlier messages are flattened into `inputs[role]` — keyed by role, so the *last* assistant message overwrites all prior assistant messages, and the *last* system message overwrites all prior system messages. Multi-turn context with multiple assistant turns is lost entirely except the most recent of each role. A caller using `messages=[system, user, assistant, user, assistant, user]` sends only the last `assistant` and the last `user` to Dify.

This is the OpenAI multi-turn contract reduced to a single turn dressed in OpenAI clothing. The caller never knows.

### 5.4 Streaming end-chunk has no `usage` and no `finish_reason="length"` path

`dify_openai.py:152-159` emits a terminal chunk with `finish_reason="stop"` unconditionally. There is no path for `length`, `content_filter`, or `tool_calls`. A caller that depends on `finish_reason` for retry logic will retry forever or never.

### 5.5 The connection is leaked on construction

`dify_openai.py:23-29`:

```python
# /tmp/super-agent-party/py/dify_openai.py:23-29
    def __init__(self, *, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=60)

    async def close(self):
        await self._client.aclose()
```

`httpx.AsyncClient` is created at construction time, lives for the life of the object, and is closed only by an explicit `close()` call that no caller in SAP makes. Per-request adapters created and discarded inside a loop will leak connection pools until the process is recycled. A long-running SAP host will accumulate them.

---

## 6. The Cross-Cutting Lies

Two failures span all three adapters.

### 6.1 No retry/backoff/circuit-breaker semantics

OpenAI's SDK has built-in retries (HTTP 429, 500, 503), tenacity-style backoff, and a `max_retries` parameter that callers tune. `ClaudeAsOpenAI.py:17` accepts `max_retries` and **discards it** — the value is stored at line 25, never read again. `GeminiAsOpenAI.py` has no `max_retries` parameter. `dify_openai.py` has none. The caller that wrote `client = AsyncClaudeAsOpenAI(api_key, max_retries=5)` got a placebo. The Anthropic-side retries happen only at the LiteLLM layer with LiteLLM's defaults.

### 6.2 No timeout normalization

`ClaudeAsOpenAI.py:17,197-198` accepts `timeout` and passes it to LiteLLM. `GeminiAsOpenAI.py` does not accept `timeout` at all. `dify_openai.py:26` hardcodes 60 seconds. A caller building a uniform retry-with-deadline policy across all three has nothing to lean on.

---

## 7. The Pattern Behind the Pattern

The three adapters share an authorial assumption: *if my output looks like OpenAI's, I am compatible.* That is shape-level compatibility. Real compatibility lives in the seams:

- **Error surface** — what exceptions does the caller see when the upstream is sick? Three different answers here.
- **State semantics** — does multi-turn behave the same? No (Dify collapses).
- **Resource lifecycle** — is the client safe to abandon, safe to share, safe to construct-per-call? Three different answers.
- **Telemetry** — does `.usage` report the same thing? No (Dify omits; Claude misses cache tokens; Gemini depends on LiteLLM version).
- **Tool fidelity** — do tools round-trip? No (Claude silently drops unknown types; Dify ignores tools entirely).

A code path that treats the three adapters as interchangeable will work on the happy path and fail unpredictably on the unhappy paths. The unhappy paths are the ones an agent loop encounters every day.

---

## 8. Cross-References

- [[55_API_SIMULATION_TRAPS]] — the deeper teardown of token counting, streaming chunk format, and system-prompt handling fidelity
- [[53_SECURITY_REVIEW]] — `os.environ` mutation pattern as confirmed information-disclosure
- [[54_DEPENDENCY_HEALTH]] — LiteLLM as the trust hinge for two of three adapters
- [[58_OBSERVABILITY_GAPS]] — `print()`-to-stdout as the dominant error reporting channel
- [[hermes:HEM-25_GATEWAY_INTERFACE]] — Hermes's allowlist-fail-closed posture for inbound network surfaces; informs Ember's outbound symmetry
- [[ember:RULES.AI]] — "make all data reading code very robust, error resistant" — the simulator pattern violates this when failure is silent

---

## What This Means for Ember

**Adopt:**
- Adopt the **lazy-load** pattern from `ClaudeAsOpenAI.py:29-38` for heavy SDKs (LiteLLM, transformers, etc.). Lazy import is a real win for cold-start time and Pi-floor smallness. Bind it to Smiðja's tool spawn.

**Adapt:**
- Adapt SAP's "unified `AsyncOpenAI`-shaped client" idea — but ground it in a **typed vendor enum** on the request, not URL-substring sniffing. The caller declares "this call goes to vendor=anthropic"; the adapter routes by that, not by a heuristic. This violates `GeminiAsOpenAI.py:76-82` directly and on purpose.
- Adapt the kwargs-filter idea into an **allowlist** keyed on declared capabilities — `vendor.capabilities() -> set[str]`, intersect with request kwargs, drop the difference with a logged warning per dropped key. No silent drops.

**Avoid:**
- **Never write API keys to `os.environ`** (`GeminiAsOpenAI.py:66-69`). Pass keys as request-scoped values. If the underlying SDK requires env vars, fork the process or use a sub-interpreter; do not mutate the parent. This is a hard Vow.
- **Never construct a long-lived `httpx.AsyncClient` in a class without a context-manager lifecycle** (`dify_openai.py:26`). Use `async with` or accept a shared client.
- **Never use `print()` for error reporting** (`ClaudeAsOpenAI.py:91`, `GeminiAsOpenAI.py:199`). Ember uses structured logging at all error sites — this is already a Vow under `[[ember:RULES.AI]]` and SAP violates it across three files.
- **Never smuggle conversation state through assistant message content** (`dify_openai.py:91-92`). State has a place in the protocol; the place is not the body.
- **Never claim "fallback models" and return `[]`** (`ClaudeAsOpenAI.py:93-95`). Either return real fallbacks or raise. A claim-the-comment-makes-the-code-doesn't-honor is a documentation defect that becomes a runtime defect.

**Invent:**
- **Vendor-Honest Adapter Contract** — a Pydantic-typed `LLMAdapter` interface that exposes:
  - `capabilities() -> AdapterCapabilities` (declared synchronously, used to gate features)
  - `complete(request: TypedRequest) -> TypedResponse` (request and response are typed, not OpenAI-shaped pretense)
  - `stream(request: TypedRequest) -> AsyncIterator[TypedDelta]`
  - `list_models() -> Result[list[ModelInfo], AdapterError]` — explicit failure type, not silent empty
  - `usage_normalizer(raw: VendorRaw) -> UsageReport` (typed, includes cache tokens, omits nothing)
  
  Then a thin `AsyncOpenAIShim` wraps `LLMAdapter` only at the surface where legacy code expects OpenAI shape — and that shim is deprecated from day one. Honest shape internally; legacy shape only at the boundary. This is the Vow of **Defended System Prompt** extended to the *outbound* surface: the wire is typed in, typed out, and the lie lives in exactly one place, with tests.

- **Capability Probe** — at adapter registration time, fire a probe request that tests each declared capability against the live endpoint. Cache the result with TTL (Cache Discipline Vow). Surface capability mismatches before traffic hits them, not during.

- **Credential Scope** — every adapter receives credentials via a `CredentialHandle` that the adapter cannot copy to `os.environ`, cannot serialize, cannot log. The handle revokes on context exit. SAP's globals are the negative template here.
