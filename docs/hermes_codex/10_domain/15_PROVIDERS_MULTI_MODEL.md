---
codex_id: 15_PROVIDERS_MULTI_MODEL
title: Providers — Two Hundred Models Behind One Profile
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - providers/base.py:1-200
  - providers/__init__.py:1-100
  - plugins/model-providers/anthropic/__init__.py
  - plugins/model-providers/anthropic/plugin.yaml
  - plugins/model-providers/openrouter/
  - plugins/model-providers/gemini/
  - plugins/model-providers/bedrock/
  - plugins/model-providers/copilot/
  - plugins/model-providers/nous/
  - plugins/model-providers/deepseek/
  - plugins/model-providers/kimi-coding/
  - plugins/model-providers/qwen-oauth/
  - plugins/model-providers/xai/
  - plugins/model-providers/nvidia/
  - plugins/model-providers/gmi/
  - plugins/model-providers/openai-codex/
  - plugins/model-providers/zai/
  - plugins/model-providers/alibaba/
  - plugins/model-providers/azure-foundry/
  - plugins/model-providers/huggingface/
  - plugins/model-providers/minimax/
  - plugins/model-providers/moonshot/
  - plugins/model-providers/stepfun/
  - plugins/model-providers/xiaomi/
  - plugins/model-providers/arcee/
  - plugins/model-providers/ai-gateway/
  - plugins/model-providers/custom/
  - plugins/model-providers/kilocode/
  - plugins/model-providers/novita/
  - plugins/model-providers/ollama-cloud/
  - plugins/model-providers/opencode-zen/
  - plugins/model-providers/copilot-acp/
  - plugins/model-providers/alibaba-coding-plan/
  - agent/credential_pool.py:1-80
  - agent/credential_pool.py:60-78
  - agent/error_classifier.py:1-100
  - agent/error_classifier.py:24-61
  - agent/anthropic_adapter.py
  - agent/gemini_native_adapter.py
  - agent/gemini_cloudcode_adapter.py
  - agent/codex_responses_adapter.py
  - agent/codex_runtime.py
  - agent/bedrock_adapter.py
  - agent/copilot_acp_client.py
  - agent/lmstudio_reasoning.py
  - agent/moonshot_schema.py
  - agent/google_code_assist.py
  - agent/google_oauth.py
  - agent/nous_rate_guard.py
  - agent/transports/__init__.py
  - agent/model_metadata.py
  - agent/usage_pricing.py
  - agent/prompt_caching.py
  - AGENTS.md:311-330
  - AGENTS.md:549-572
ember_subsystem_targets: [Funi, Strengr, Vegfarendr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/17_PLUGINS_EXTENSIBILITY
  - 20_interface/23_PROVIDER_INTERFACE
  - 30_execution/41_MULTI_PROVIDER_FAILOVER
---

# Providers — Two Hundred Models Behind One Profile

*— Rúnhild Svartdóttir, Architect*

> *A provider is not a model. A provider is a road to a model. The architect's job is to draw the roads on the map so every traveler can find the same destination, even when the roads change names overnight.*

Hermes supports roughly 200 models across roughly 30 providers. The README claims this number; the implementation enforces it through one declarative dataclass (`ProviderProfile`) and one credential pool. This doc maps the provider domain — how the dataclass is shaped, how profiles are discovered, what each profile owns, what stays on the agent core.

The mental model: **declarative profiles describe each provider; lazy discovery loads them on first use; user plugins can override bundled profiles by last-writer-wins; the credential pool is the single chooser of *which key to use*; the error classifier is the single decider of *what to do when a call fails*.**

---

## 1. The `ProviderProfile` Dataclass

`providers/base.py:38-100` defines the dataclass that holds everything declarative about a provider:

```python
@dataclass
class ProviderProfile:
    # ── Identity ─────────────────────────────────────────────
    name: str
    api_mode: str = "chat_completions"   # also: "anthropic_messages", "codex_responses", "gemini_native", "bedrock_invoke"
    aliases: tuple = ()

    # ── Human-readable metadata ───────────────────────────────
    display_name: str = ""
    description: str = ""
    signup_url: str = ""

    # ── Auth & endpoints ─────────────────────────────────────
    env_vars: tuple = ()                  # API key env-var names (first match wins)
    base_url: str = ""
    models_url: str = ""                  # explicit models endpoint
    auth_type: str = "api_key"            # api_key | oauth_device_code | oauth_external | copilot | aws_sdk
    supports_health_check: bool = True

    # ── Model catalog ─────────────────────────────────────────
    fallback_models: tuple = ()           # curated list when live fetch fails
    hostname: str = ""                    # base hostname for URL→provider reverse-mapping

    # ── Client-level quirks ──────────────────────────────────
    default_headers: dict[str, str] = field(default_factory=dict)

    # ── Request-level quirks ─────────────────────────────────
    fixed_temperature: Any = None         # None = caller default; OMIT_TEMPERATURE = don't send
    default_max_tokens: int | None = None
    default_aux_model: str = ""           # cheap model for auxiliary tasks
```

Behavioral hooks (overridable in subclasses):

- `get_hostname()` — derive hostname from `base_url` if not explicitly set
- `prepare_messages(messages)` — provider-specific message preprocessing (called *after* codex sanitization, *before* developer-role swap)
- `build_extra_body(session_id, **ctx)` — extra-body fields merged into API kwargs
- `build_api_kwargs_extras(reasoning_config, **ctx)` — returns `(extra_body_additions, top_level_kwargs)` — the split exists because OpenRouter wants `extra_body.reasoning` while Kimi wants top-level `reasoning_effort`
- `fetch_models(api_key, timeout)` — live model-list fetch with the default OpenAI-compat `GET /models` shape

The default `fetch_models` (`providers/base.py:132-184`) is robust: explicit `models_url` overrides; otherwise `base_url + "/models"`. Sends Bearer auth when `api_key` is given; sets a `hermes-cli/<version>` User-Agent so providers behind a WAF (OpenCode Zen) don't 403 the catalog probe. Falls back gracefully to `None` so callers know to use the static fallback list.

### 1.1 The Anthropic Profile (Example)

`plugins/model-providers/anthropic/__init__.py` shows the full profile shape:

```python
anthropic = AnthropicProfile(
    name="anthropic",
    aliases=("claude", "claude-oauth", "claude-code"),
    api_mode="anthropic_messages",
    env_vars=("ANTHROPIC_API_KEY", "ANTHROPIC_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN"),
    base_url="https://api.anthropic.com",
    auth_type="api_key",
    default_aux_model="claude-haiku-4-5-20251001",
)
```

The `AnthropicProfile` subclass *only* overrides `fetch_models` (because Anthropic uses `x-api-key` + `anthropic-version: 2023-06-01` headers rather than Bearer). Everything else is declarative.

This is the *cleanest* provider abstraction I have seen in any agent framework. One file. One dataclass. One subclass when a quirk is too specific. The transport reads the profile.

---

## 2. The Discovery System

`providers/__init__.py:1-100` describes a *three-source lazy* discovery:

1. **Bundled plugins** at `plugins/model-providers/<name>/`
2. **User plugins** at `$HERMES_HOME/plugins/model-providers/<name>/`
3. **Legacy** at `providers/<name>.py` (single-file profiles for back-compat)

Each plugin directory contains:
- `__init__.py` — calls `register_provider(profile)` at import
- `plugin.yaml` — manifest (`name`, `kind: model-provider`, `version`, `description`)

The discovery (`providers/__init__.py:65-89`):

```python
def get_provider_profile(name: str) -> ProviderProfile | None:
    if not _discovered:
        _discover_providers()
    canonical = _ALIASES.get(name, name)
    return _REGISTRY.get(canonical)
```

`register_provider()` is **last-writer-wins** (`providers/__init__.py:53-63`):

```python
def register_provider(profile: ProviderProfile) -> None:
    """Later registrations with the same name replace earlier ones..."""
    _REGISTRY[profile.name] = profile
    for alias in profile.aliases:
        _ALIASES[alias] = profile.name
```

Since user plugins load *after* bundled, the user can monkey-patch any bundled profile by writing their own with the same name. **No core code edit required.** This is `AGENTS.md:549-572`'s key claim, and it is implemented exactly as advertised.

The general `PluginManager` (`hermes_cli/plugins.py`) records `kind: model-provider` manifests but does *not* import them — that would double-instantiate the `ProviderProfile`. Plugins without an explicit `kind:` get auto-coerced by a source-text heuristic (`register_provider` + `ProviderProfile` in `__init__.py`).

This is a *third* plugin-discovery system in Hermes (the other two: general plugins in `hermes_cli/plugins.py`, memory providers in `plugins/memory/__init__.py`). Documented in `[[10_domain/19_BOUNDARY_LAW]]` as a leak.

---

## 3. The Thirty Bundled Profiles

The full bundled profile list (from `plugins/model-providers/`):

| Profile | Provider | Notable quirks |
|---|---|---|
| `ai-gateway` | Cloudflare AI Gateway | proxy in front of other providers |
| `alibaba` (+ `alibaba-coding-plan`) | Alibaba Cloud | DashScope endpoints |
| `anthropic` | Anthropic native | x-api-key + anthropic-version headers; cache_control breakpoints |
| `arcee` | Arcee.ai | OSS-finetune cloud |
| `azure-foundry` | Azure AI Foundry | Microsoft enterprise endpoint |
| `bedrock` | AWS Bedrock | aws_sdk auth; boto3 dependency |
| `copilot` (+ `copilot-acp`) | GitHub Copilot | copilot auth_type; ACP variant for IDE integration |
| `custom` | OpenAI-compatible | shared by every endpoint that "looks like OpenAI" |
| `deepseek` | DeepSeek | own pricing tier |
| `gemini` | Google Gemini | gemini_native api_mode |
| `gmi` | GMI Cloud | multi-model direct API |
| `huggingface` | HuggingFace Inference | Inference Endpoints + Serverless |
| `kilocode` | Kilo Code | OSS coding agents |
| `kimi-coding` | Moonshot Kimi | server-managed temperature (`OMIT_TEMPERATURE`) |
| `minimax` | MiniMax | own STT/TTS bundled |
| `nous` | Nous Research | the Hermes-house provider; subscription + rate-guard |
| `novita` | Novita.ai | low-cost OpenAI-compat |
| `nvidia` | NVIDIA NIM | self-hosted-ish enterprise NIMs |
| `ollama-cloud` | Ollama Cloud | newer hosted Ollama |
| `openai-codex` | OpenAI Codex Responses | codex_responses api_mode; deterministic call IDs |
| `opencode-zen` | OpenCode Zen | behind WAF; needs custom UA |
| `openrouter` | OpenRouter | aggregator; reasoning in extra_body.reasoning |
| `qwen-oauth` | Alibaba Qwen | oauth_device_code; QR sign-in |
| `stepfun` | StepFun | Chinese OSS-compat |
| `xai` | xAI | grok models; native x_search tool |
| `xiaomi` | Xiaomi | enterprise endpoint |
| `zai` | Z.ai | OSS finetune cloud |

**Add `lmstudio`, `ollama` (local), and `ollama-cloud` for self-hosted inference and Hermes can cover ~200 models without any new code beyond a profile.**

---

## 4. The Five `api_mode` Values

The api_mode determines which adapter shapes the request:

1. **`chat_completions`** (default) — OpenAI-compatible `POST /v1/chat/completions` with `messages`, `tools`, `tool_choice`. Used by most providers.

2. **`anthropic_messages`** — Anthropic's native `POST /v1/messages` with system blocks, content blocks (text, tool_use, tool_result, image, thinking), and `cache_control` markers. Adapter: `agent/anthropic_adapter.py` + `agent/transports/anthropic.py`. Caching layout: `system_and_3` (`agent/prompt_caching.py:49-100`).

3. **`codex_responses`** — OpenAI Codex Responses API with the Responses object shape. Tool-call IDs are *derived* on the client side because the server doesn't always send them. Adapter: `agent/codex_responses_adapter.py` + `agent/codex_runtime.py` + `agent/transports/codex.py`. The deterministic call-ID derivation lives at `_deterministic_call_id`.

4. **`gemini_native`** — Google Gemini's `generateContent` endpoint with their own schema dialect. Adapter: `agent/gemini_native_adapter.py` + `agent/gemini_schema.py`. There is *also* `agent/gemini_cloudcode_adapter.py` for Google's Cloud Code OAuth-only path, plus `agent/google_code_assist.py` for their newer Code Assist surface.

5. **`bedrock_invoke`** — AWS Bedrock's `InvokeModel` / `Converse` API with boto3 SDK. Adapter: `agent/bedrock_adapter.py` + `agent/transports/bedrock.py`. Auth via AWS SDK chain.

A sixth adapter exists outside the api_mode dispatch:
- **`copilot_acp`** — `agent/copilot_acp_client.py` for GitHub Copilot's ACP protocol. ACP is Agent Communication Protocol, not a model API per se; the adapter speaks ACP to Copilot's IDE-facing endpoint.

The `agent/lmstudio_reasoning.py` and `agent/moonshot_schema.py` are *helpers*, not full adapters — they handle the model-side quirks (`<think>` block extraction for LMStudio; Moonshot's tool-schema variants) but pass through `chat_completions` for the actual call.

---

## 5. The Credential Pool

`agent/credential_pool.py` (1955 lines) is the *single decider* of which credential to use. The pool has four selection strategies (`agent/credential_pool.py:60-69`):

- `STRATEGY_FILL_FIRST` — use the first credential until it exhausts
- `STRATEGY_ROUND_ROBIN` — rotate through all credentials per call
- `STRATEGY_RANDOM` — pick randomly
- `STRATEGY_LEAST_USED` — pick whichever was used least recently

Exhaustion TTLs (`agent/credential_pool.py:71-78`):

```python
EXHAUSTED_TTL_401_SECONDS = 5 * 60          # 5 minutes for transient 401
EXHAUSTED_TTL_429_SECONDS = 60 * 60         # 1 hour for rate-limit
EXHAUSTED_TTL_DEFAULT_SECONDS = 60 * 60     # 1 hour default
```

Provider-supplied `reset_at` timestamps override these. The pool persists state to disk so a process restart doesn't reset cooldowns and walk back into the same exhausted credential.

Auth types (`agent/credential_pool.py:55-58`):

- `oauth` — refresh tokens with skew (`CODEX_ACCESS_TOKEN_REFRESH_SKEW_SECONDS`)
- `api_key` — straightforward Bearer or x-api-key

A credential's `pool_key` is the canonical identifier — for custom OpenAI-compat endpoints, all share `provider='custom'` but are keyed by the endpoint URL hash (`agent/credential_pool.py:79+`).

The integration with the error classifier (next section): when `ClassifiedError.should_rotate_credential` is true, the loop calls `credential_pool.mark_exhausted(current_credential, classified.reason)` and asks for the next viable credential. The pool decides.

---

## 6. The Error Classifier

`agent/error_classifier.py` (1087 lines) classifies API errors into typed `FailoverReason` values (`agent/error_classifier.py:24-61`):

| Reason | Status / Cause | Recovery action |
|---|---|---|
| `auth` | 401/403 transient | Refresh/rotate credential |
| `auth_permanent` | Auth still failing after refresh | Abort |
| `billing` | 402 or "insufficient credits" body | Rotate immediately |
| `rate_limit` | 429 or quota throttling | Backoff then rotate |
| `overloaded` | 503/529 | Backoff |
| `server_error` | 500/502 | Retry |
| `timeout` | Connection/read timeout | Rebuild client + retry |
| `context_overflow` | Context too large | Compress, not failover |
| `payload_too_large` | 413 | Compress |
| `image_too_large` | Native image part exceeds per-image limit | Shrink and retry |
| `model_not_found` | 404 or invalid model | Fallback to different model |
| `provider_policy_blocked` | Aggregator blocked the only endpoint | Failover provider |
| `format_error` | 400 bad request | Abort or strip + retry |
| `thinking_signature` | Anthropic thinking-block signature invalid | Strip and retry |
| `long_context_tier` | Anthropic "extra usage" tier gate | Provider-specific |
| `oauth_long_context_beta_forbidden` | Anthropic OAuth subscription rejects 1M beta | Disable beta and retry |
| `llama_cpp_grammar_pattern` | llama.cpp grammar rejects regex pattern | Strip from tools and retry |
| `unknown` | Unclassifiable | Retry with backoff |

The classifier's classification result (`agent/error_classifier.py:67-86`) carries four recovery hints:

```python
@dataclass
class ClassifiedError:
    reason: FailoverReason
    status_code: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    message: str = ""
    error_context: Dict[str, Any] = field(default_factory=dict)

    # Recovery action hints
    retryable: bool = True
    should_compress: bool = False
    should_rotate_credential: bool = False
    should_fallback: bool = False
```

The loop reads the hints; the loop doesn't re-classify. This is excellent boundary discipline. *Classify once; act on the typed value.*

---

## 7. Rate-Limit Tracking & Provider-Specific Guards

`agent/rate_limit_tracker.py` records per-provider, per-key, per-endpoint rate-limit state. The `agent/nous_rate_guard.py` is a *provider-specific* guard for Nous Research subscriptions — they have particular rate behavior that benefits from active tracking ("is this a genuine rate limit or just slow rollout?").

The pattern: most provider-specific behavior is in the *profile* (declarative). A few rate-limit nuances live in dedicated guard modules. Both are accessed only by the conversation loop and the credential pool — never by adapters directly.

---

## 8. Model Metadata & Usage Pricing

`agent/model_metadata.py` answers questions about a model:

- `fetch_model_metadata(model_id)` — context length, pricing, capability flags
- `estimate_tokens_rough(text)`, `estimate_messages_tokens_rough`, `estimate_request_tokens_rough` — pre-call token estimation
- `get_next_probe_tier(model_id)` — for adaptive context-length detection
- `parse_context_limit_from_error(err)` — recover from "context too long" errors with the *actual* limit
- `is_local_endpoint(base_url)` — local backends (Ollama, LMStudio) are treated differently for cost tracking
- `query_ollama_num_ctx(base_url, model)` — Ollama-specific context length probe

`agent/usage_pricing.py` does cost estimation per response. It is the answer to "how much did that turn cost?" — combining the usage object's input/output token counts with the model's pricing rate from `models.dev` (queried in `agent/models_dev.py`).

---

## 9. The Codex Specifics

Codex Responses deserves its own paragraph because the protocol is unusual. `agent/codex_responses_adapter.py` + `agent/codex_runtime.py` + `agent/transports/codex.py` + `agent/transports/codex_app_server.py` + `agent/transports/codex_app_server_session.py` + `agent/transports/codex_event_projector.py` form a small subsystem.

Why so many files? Because Codex Responses is a *stateful* API — it has a server-side session that can be resumed. The Codex App Server is OpenAI's recommended embedding-side daemon that mediates between Hermes and the Codex backend. Hermes can run as a Codex App Server client (subscriber model) or talk directly to the Responses endpoint (BYO-key model). The `_event_projector.py` maps Codex's event stream into Hermes's tool-call shape.

For Ember, Codex is out of scope. But the pattern — a complex provider gets its own subsystem rather than bloating the chat_completions branch — is worth noting.

---

## 10. The OAuth Providers

Several providers use OAuth rather than static API keys:

- **`anthropic`** (when `CLAUDE_CODE_OAUTH_TOKEN` is set) — Claude Code subscription
- **`copilot`** — GitHub Copilot's device-code flow
- **`gemini-cloudcode`** — Google's Cloud Code OAuth flow
- **`qwen-oauth`** — Alibaba's Qwen Coder device-code flow
- **`openai-codex`** (sometimes) — ChatGPT Pro subscription path
- **`google_code_assist`** — Google's newer Code Assist surface

OAuth means refresh tokens, token storage, refresh-skew handling, and "did this token expire mid-call?" recovery. `hermes_cli/auth.py` is the central OAuth store. `hermes_cli/copilot_auth.py`, `hermes_cli/dingtalk_auth.py`, `hermes_cli/vercel_auth.py` are provider-specific flows.

For Ember (slice 1-2 is API-key-only), OAuth is future work. The boundary discipline (auth lives in its own file, never inline in the adapter) is portable.

---

## What This Means for Ember

**Proposed new True Name: Vegfarendr** (Old Norse: "wayfarer, traveler"). Vegfarendr is the *provider-and-route* layer — the part of Strengr that knows which road leads to which destination. Lives in Strengr's submodule space (`src/ember/thread/vegfarendr/`).

Why not call it "Provider"? Because the True Name is the *role* in the system. Vegfarendr is the one who knows the roads. The provider profiles are her maps.

### Concrete proposals

1. **Adopt the `ProviderProfile` dataclass exactly.** Same fields, same hooks, same lazy discovery. The dataclass shape is portable; the lazy discovery is portable; the override-by-last-write is the right pluggability. Cite `providers/base.py:38-100`.

2. **Adopt the `FailoverReason` enum as Ember's typed-disconnect taxonomy.** Ember already has a typed `Disconnected` value at the Strengr boundary; the Hermes enum is the larger sibling. Add the dozen-plus reasons (auth, billing, rate_limit, overloaded, server_error, timeout, context_overflow, payload_too_large, image_too_large, model_not_found, format_error, unknown). When Strengr disconnects, it returns one of these values. When Funi is asked to plan recovery, it reads the reason and chooses. Cite `agent/error_classifier.py:24-61`.

3. **Adopt the four selection strategies (fill_first, round_robin, random, least_used) for credential rotation.** Ember currently has one Funi; when she acquires multiple credentials (a household with multiple operators sharing one Strengr key + a fallback), the rotation strategy matters. Default to `fill_first` (simplest); expose `round_robin` for keys with strict per-key rate limits. Cite `agent/credential_pool.py:60-69`.

4. **Adopt the persistent exhaustion-TTL pattern.** A credential marked exhausted persists across process restart. The `EXHAUSTED_TTL_401_SECONDS = 5 * 60` and `EXHAUSTED_TTL_429_SECONDS = 60 * 60` defaults are good starting values. Cite `agent/credential_pool.py:71-78`.

5. **Adopt the lazy-discovery + last-writer-wins override.** Plugin-style provider profiles in `~/.ember/plugins/providers/<name>/` override bundled ones. The user can monkey-patch any provider without editing Ember source. Cite `providers/__init__.py:53-89`.

6. **Adopt the five api_mode values when they become relevant.** Slice 1-2 uses chat_completions only (Ollama). When Ember gains Anthropic native, codex_responses, gemini_native, bedrock — each becomes a *new mode* of one adapter, not a new adapter class. Cite the api_mode pattern.

7. **Defer the Codex / OAuth / aggregator complexity.** Slice 1-2 ships Funi-against-Ollama. Codex Responses, OAuth providers, OpenRouter / GMI / aggregators are slice-N decisions. The pattern is captured here for later.

8. **Adopt model_metadata.py's pre-call token estimation.** `estimate_request_tokens_rough` lets the agent decide whether a request will fit *before* sending. This is a small but valuable Funi-side discipline. Cite `agent/model_metadata.py`.

9. **Refuse to put 1955 lines in one file.** The Hermes credential pool is impressive engineering and architectural debt at once. Ember's credential management should live in 3-5 smaller files: `store.py` (persistence), `selector.py` (strategy), `exhaustion.py` (TTLs), `oauth.py` (when OAuth arrives), `pool.py` (the orchestrator).

**Affected True Names:** **Vegfarendr** (new — provider profiles + credential pool), **Strengr** (uses Vegfarendr to select credentials), **Funi** (reads classified failures and acts).

**Vows reinforced:**
- **Vow of Modular Authorship** — every provider is a plugin; user plugins override bundled ones.
- **Vow of Graceful Offline** — the typed `FailoverReason` enum makes every kind of disconnect a named, typed value.
- **Vow of Pluggable Storage** — *and* pluggable providers. The same lazy-discovery pattern works for Brunnr backends and provider profiles.

**Vows at risk if ported wrong:**
- **Vow of Smallness** — 1955-line credential pool is a foot-gun. Split early.
- **Vow of Modular Authorship** — Hermes has three plugin discoveries; Ember should have *one*. The provider discovery is the third; consolidate before this becomes a tradition.

The roads to the models are many. The discipline of the map is what keeps the traveler from getting lost. Ember inherits the map shape — and travels lighter.
