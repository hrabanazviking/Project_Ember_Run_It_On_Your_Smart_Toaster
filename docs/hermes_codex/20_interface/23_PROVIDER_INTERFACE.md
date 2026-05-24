---
codex_id: 23_PROVIDER_INTERFACE
title: Provider Interface — The Contract Funi Needs
role: Cartographer
layer: Interface
status: draft
hermes_source_refs:
  - providers/base.py:1-185
  - providers/README.md
  - agent/transports/base.py:1-90
  - agent/transports/types.py:1-160
  - agent/transports/anthropic.py:1-180
  - agent/transports/chat_completions.py:1-300
  - plugins/model-providers/README.md
  - plugins/model-providers/anthropic/__init__.py
  - plugins/model-providers/openrouter/__init__.py
  - agent/credential_pool.py:1-450
  - agent/credential_sources.py:1-450
ember_subsystem_targets: [Funi, Strengr, Munnr]
cross_refs:
  - 20_interface/20_MCP_INTEGRATION
  - 20_interface/21_RPC_INTERFACE
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/63_INTEGRATION_PATHS
  - 30_execution/41_MULTI_PROVIDER_FAILOVER
  - 30_execution/33_HOT_COLD_TIERS
---

# 23 — Provider Interface: The Contract Funi Needs

> *A profile is a portrait, not a soul. Each one names what the provider answers to when called.*
> — Védis Eikleið, holding two profiles side by side

## 1. Two layers, one outcome

A "provider" in Hermes is the answer to *"where does the model live and how does it speak?"* — Anthropic at api.anthropic.com via Messages API, OpenRouter at openrouter.ai/api/v1 via OpenAI-compatible, Ollama at localhost:11434, Bedrock via the AWS SDK, and so on for 30+ entries (`plugins/model-providers/` lists them).

Hermes splits this question across two carefully separated layers:

1. **`ProviderProfile`** (`providers/base.py:38-185`) — *declarative* metadata about a provider: name, endpoints, env vars, default models, header quirks. This is "what kind of beast."
2. **`ProviderTransport`** (`agent/transports/base.py:1-90`) — *behavioural* code for one **api_mode**: convert messages outbound, normalize response inbound. This is "how to talk to that beast."

The wiring is: each `ProviderProfile` declares an `api_mode` string (default `"chat_completions"`); the `api_mode` resolves to a registered `ProviderTransport`. There are currently **four api_modes** that show up in the source:

- `"chat_completions"` — the default OpenAI-compatible mode used by ~16 providers (OpenRouter, Nous, NVIDIA, Qwen, Ollama, DeepSeek, xAI, Kimi, etc.).
- `"anthropic_messages"` — Anthropic's native Messages API.
- `"bedrock"` — AWS Bedrock through the boto3 SDK.
- `"codex"` — OpenAI's Codex Responses API.

The split means **adding a new provider that uses an existing api_mode is a 30-line plugin file**. Adding a provider with a genuinely new api_mode is a full transport implementation (~200 lines, comparable to `agent/transports/anthropic.py`). This is excellent separation of concerns and the heart of what Funi should learn.

## 2. ProviderProfile — the declarative surface

`providers/base.py:38-93` declares the dataclass. Reading it slowly:

```python
@dataclass
class ProviderProfile:
    # ── Identity ─────────────────────────────────────────────
    name: str
    api_mode: str = "chat_completions"
    aliases: tuple = ()

    # ── Human-readable metadata ───────────────────────────────
    display_name: str = ""
    description: str = ""
    signup_url: str = ""

    # ── Auth & endpoints ─────────────────────────────────────
    env_vars: tuple = ()
    base_url: str = ""
    models_url: str = ""
    auth_type: str = "api_key"
    supports_health_check: bool = True

    # ── Model catalog ─────────────────────────────────────────
    fallback_models: tuple = ()
    hostname: str = ""

    # ── Client-level quirks (set once at client construction) ─
    default_headers: dict[str, str] = field(default_factory=dict)

    # ── Request-level quirks ─────────────────────────────────
    fixed_temperature: Any = None
    default_max_tokens: int | None = None
    default_aux_model: str = ""
```

Every field is either a static string or a default value with a clear meaning. The dataclass is the **single source of truth** for everything downstream needs to know about the provider. `providers/README.md:30-53` lists every consumer:

- `hermes_cli/auth.py` extends `PROVIDER_REGISTRY` with every api-key profile it sees.
- `hermes_cli/models.py` calls `profile.fetch_models()` inside `provider_model_ids()`.
- `hermes_cli/doctor.py` adds a `/models` health check for each `auth_type="api_key"` profile.
- `hermes_cli/config.py` injects every `env_var` into `OPTIONAL_ENV_VARS` so the setup wizard knows about it.
- `hermes_cli/runtime_provider.py` reads `profile.api_mode` as a fallback when URL detection finds nothing.
- `agent/model_metadata.py` maps hostname → provider via `profile.get_hostname()`.
- `agent/auxiliary_client.py` reads `profile.default_aux_model` first.
- `agent/transports/chat_completions.py::_build_kwargs_from_profile()` invokes `profile.prepare_messages()`, `profile.build_extra_body()`, and `profile.build_api_kwargs_extras()` on every call.

**Eight downstream consumers, all reading from one declaration.** This is the value of the declarative pattern. When a new provider arrives — say, a new Chinese model API — adding the profile is the single change that wires it into auth, models listing, doctor health check, config wizard, hostname detection, aux-model selection, and transport kwargs. No parallel registration in seven files.

## 3. The four override hooks

`providers/base.py:95-184` defines the hooks a non-trivial profile can override:

```python
def get_hostname(self) -> str: ...
def prepare_messages(self, messages) -> list: ...
def build_extra_body(self, *, session_id=None, **context) -> dict: ...
def build_api_kwargs_extras(self, *, reasoning_config=None, **context) -> tuple[dict, dict]: ...
def fetch_models(self, *, api_key=None, timeout=8.0) -> list[str] | None: ...
```

Each hook has a sensible default. `fetch_models()` defaults to a Bearer-auth GET on `{base_url}/models` and parses the OpenAI-shape response. `build_extra_body()` defaults to empty dict. `prepare_messages()` is identity. Only the providers that need to be different override.

Real examples from the plugin dir:

**`plugins/model-providers/anthropic/__init__.py`** subclasses `ProviderProfile` only to override `fetch_models` — because Anthropic uses `x-api-key` instead of Bearer:

```python
class AnthropicProfile(ProviderProfile):
    def fetch_models(self, *, api_key=None, timeout=8.0):
        if not api_key:
            return None
        req = urllib.request.Request("https://api.anthropic.com/v1/models")
        req.add_header("x-api-key", api_key)
        req.add_header("anthropic-version", "2023-06-01")
        ...
```

Forty-six lines total for the profile file. The downstream layers do the rest.

**`plugins/model-providers/openrouter/__init__.py`** overrides three hooks because OpenRouter has more quirks: model catalog is public (no auth), reasoning config goes in `extra_body.reasoning`, and Grok models routed through OpenRouter need an `x-grok-conv-id` header for prompt-cache stickiness. Each override is a few lines; the whole file is ~100 lines.

This is **the right granularity**. Cookie-cutter providers are plugins of ~30 lines. Quirky providers are plugins of ~100. Genuinely new APIs are full transports of ~200-600. Nothing scales worse than that.

## 4. ProviderTransport — the behavioural surface

`agent/transports/base.py:16-89` defines the ABC:

```python
class ProviderTransport(ABC):
    @property
    @abstractmethod
    def api_mode(self) -> str: ...

    @abstractmethod
    def convert_messages(self, messages, **kwargs) -> Any: ...

    @abstractmethod
    def convert_tools(self, tools) -> Any: ...

    @abstractmethod
    def build_kwargs(self, model, messages, tools=None, **params) -> Dict[str, Any]: ...

    @abstractmethod
    def normalize_response(self, response, **kwargs) -> NormalizedResponse: ...

    # Optional with defaults:
    def validate_response(self, response) -> bool: return True
    def extract_cache_stats(self, response) -> Optional[Dict[str, int]]: return None
    def map_finish_reason(self, raw_reason) -> str: return raw_reason
```

Five abstract methods, three optional. The shape is unusually clean:

1. **`api_mode`** — the string this transport handles.
2. **`convert_messages`** — outbound: OpenAI shape → provider-native shape.
3. **`convert_tools`** — outbound: OpenAI tool schema → provider-native schema.
4. **`build_kwargs`** — outbound assembly: model + converted messages + converted tools + params → kwargs dict ready for the provider SDK.
5. **`normalize_response`** — inbound: provider-native response → `NormalizedResponse`.

The optional three:
- **`validate_response`** — does the raw response have a valid structure? (See `agent/transports/anthropic.py:133-148` for why this matters: an empty content list with `stop_reason == "end_turn"` is legitimate after a tool turn; treating it as invalid causes false retries.)
- **`extract_cache_stats`** — provider-specific prompt-cache hit metrics.
- **`map_finish_reason`** — translate provider-specific stop reasons to OpenAI vocabulary.

What the transport explicitly does **not** own (per the docstring at `agent/transports/base.py:1-8`):
- Client construction (lives on `AIAgent`).
- Streaming (lives on `AIAgent`).
- Credential refresh (lives on `agent/credential_pool.py`).
- Prompt caching (lives on `agent/prompt_caching.py`).
- Interrupt handling (lives on `AIAgent`).
- Retry logic (lives on `agent/retry_utils.py`).

This is the discipline that keeps each layer testable. The transport is a pure function pair: convert and normalize. Everything stateful lives elsewhere.

## 5. The NormalizedResponse type

`agent/transports/types.py:89-160` (partly read above) defines the canonical response shape:

```python
@dataclass
class NormalizedResponse:
    content: str | None
    tool_calls: list[ToolCall] | None
    finish_reason: str
    reasoning: str | None        # extended-thinking blocks
    usage: Usage | None
    provider_data: dict[str, Any] | None
```

The principle: **shared fields are truly cross-provider.** Every downstream consumer can read them without branching on `api_mode`. Protocol-specific state (Anthropic's `reasoning_details`, Codex's `codex_reasoning_items`, Gemini's `thought_signature`) lives in the `provider_data` dict, accessed only by code paths that know which provider produced the response.

`ToolCall` is `agent/transports/types.py:18-77` — and there is a beautiful detail. It exposes a `function` property that returns *self*:

```python
@property
def function(self) -> ToolCall:
    """Return self so tc.function.name / tc.function.arguments work."""
    return self
```

This is **backward compatibility done right**. The 45+ existing sites that read `tc.function.name` continue to work, even though the canonical fields (`tc.name`, `tc.arguments`) are now flat. The refactor — moving from a `Function` sub-object to flat fields — did not require touching the call sites. A two-line property is the bridge.

## 6. The credential pool — a separate layer entirely

Hermes treats credential management as **its own subsystem**, not as part of the provider profile. `agent/credential_pool.py` is 1,955 lines. It owns:

- Loading credentials from many sources (`env`, `claude_code`, `hermes_pkce`, `device_code`, `qwen-cli`, `gh_cli`, `config`, `manual` — per `agent/credential_sources.py:5-13`).
- Maintaining a **pool of credentials per provider** with rotation strategies (`fill_first`, `round_robin`, `random`, `least_used` — `agent/credential_pool.py:60-69`).
- Tracking exhaustion state with **per-error TTLs**:
  ```python
  EXHAUSTED_TTL_401_SECONDS = 5 * 60           # 5 minutes
  EXHAUSTED_TTL_429_SECONDS = 60 * 60          # 1 hour
  EXHAUSTED_TTL_DEFAULT_SECONDS = 60 * 60      # 1 hour
  ```
  (`agent/credential_pool.py:75-77`)
- **Parsing provider-supplied reset timestamps** (`_parse_absolute_timestamp` at `agent/credential_pool.py:208-235`) — accepts epoch seconds, epoch milliseconds, and ISO-8601 strings. Returns seconds since epoch. When the provider tells you when the rate limit resets, you respect it.
- **Extracting retry-after from error messages** (`_extract_retry_delay_seconds` at `agent/credential_pool.py:238-248`) — the message text "retry after 12 seconds" becomes `12.0`.
- **Unified removal contract** (`agent/credential_sources.py:1-449`) — every credential source has a `RemovalStep` so that `hermes auth remove <provider> <N>` makes the entry stay gone (this was a long-standing bug before the unification; see the file's docstring for the history).

The discipline here is **the same typed-not-thrown pattern** Ember already uses for realm boundaries (per [[20_interface/21_RPC_INTERFACE]] §6). A credential failure does not throw a generic exception; it sets `last_status = "exhausted"`, classifies the cause, computes a cooldown, and the pool finds another. For Ember, this is the second-tier expansion: Strengr today owns the network tether; tomorrow Strengr will own a credential pool for tethers-to-many-models.

## 7. Adding a provider — what it actually takes

`plugins/model-providers/README.md:33-65` gives the recipe:

```python
# plugins/model-providers/<your_provider>/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

my_provider = ProviderProfile(
    name="your-provider",
    aliases=("alias1", "alias2"),
    display_name="Your Provider",
    description="One-line description shown in the setup picker",
    signup_url="https://your-provider.example.com/keys",
    env_vars=("YOUR_PROVIDER_API_KEY", "YOUR_PROVIDER_BASE_URL"),
    base_url="https://api.your-provider.example.com/v1",
    default_aux_model="your-cheap-model",
)

register_provider(my_provider)
```

```yaml
# plugins/model-providers/<your_provider>/plugin.yaml
name: your-provider-profile
kind: model-provider
version: 1.0.0
description: Short sentence about the provider
author: Your Name
```

That is it. For an OpenAI-compatible provider, this is the complete change set. No edits to `auth.py`, `models.py`, `doctor.py`, `runtime_provider.py`, `model_metadata.py`, `runtime.py`, the transport, or the chat loop. The downstream layers all auto-wire from the registry.

The discovery mechanism is `providers/__init__.py::_discover_providers()` — scans `plugins/model-providers/` and `$HERMES_HOME/plugins/model-providers/` on first access. User plugins override bundled plugins of the same name (last-writer-wins). The same "filesystem-as-registry" pattern as skills (see [[20_interface/22_SKILL_INTERFACE]]).

## 8. The streaming contract

The base ABC does not declare streaming methods. Streaming lives on `AIAgent` (per the docstring caveat) and uses transport-specific streaming SDKs. The pattern: `transport.build_kwargs(...)` produces a kwargs dict; `AIAgent.run_streaming(...)` calls the provider SDK's streaming method with those kwargs and handles the chunk-by-chunk delivery.

For Ember, this is an important separation. Funi's `complete_streaming()` Protocol slot exists in slice 2 (ADR 0009); it returns an iterator of `FuniStreamChunk`. The transport layer (when Ember adopts it) would handle conversion at the request-build step; the streaming itself stays with Funi. **The split mirrors Hermes exactly.**

## 9. The retry / failover scaffolding

`agent/retry_utils.py` (referenced from the credential pool docstring) is the cousin of the credential pool. The pool decides *which credential to use next*; the retry layer decides *whether to try again at all*. Together they implement:

1. Try with credential A.
2. Get a 429 with a `Retry-After` header.
3. Pool marks A as exhausted with `last_error_reset_at = now + 60`.
4. Pool selects credential B from the same provider.
5. Retry succeeds with B.
6. After 60s, credential A becomes eligible again.

The same logic survives across providers via the `_NEXT_PROVIDER_ON_EXHAUSTION` table — when an entire provider's pool is exhausted, Hermes optionally fails over to a *different provider* (e.g., Anthropic via Claude Code → Anthropic via API key → Bedrock Claude). This is provider-failover, not just credential-failover. The execution-layer doc [[30_execution/41_MULTI_PROVIDER_FAILOVER]] is where this gets unpacked at depth.

## 10. The honest limits

- **Only one provider profile per name.** Re-registering with the same name silently replaces the prior one (last-writer-wins). This is a feature (user plugin overrides bundled plugin) but it's also a source of subtle bugs when two plugins ship the same name unknowingly.
- **`fetch_models` is a synchronous urllib call with timeout.** No retry, no caching beyond per-process. A flaky provider catalog endpoint makes the doctor command slow.
- **No streaming-shape sanity check.** A transport that returns a malformed chunk produces a chat that hangs or crashes mid-stream. There is no top-level guard.
- **No per-provider quota tracking persisted across sessions.** The exhaustion TTL is in-memory in the pool; restarting Hermes re-attempts credentials that were known exhausted moments earlier.

Each limit is acceptable for Hermes's threat model. For Ember, the `fetch_models` synchronous design is fine (Pi-scale, infrequent operation). The exhaustion-not-persisted question deserves an ADR — for a Pi user with one cheap key, re-trying after restart is fine; for a household with three operators sharing a pool of OpenRouter keys via shared Gungnir, persisting exhaustion would be friendlier.

## What This Means for Ember

**True Names affected:**

- **Funi (flame).** The two-layer split (`ProviderProfile` + `ProviderTransport`) is exactly the next-step refactor Funi needs. Today Funi has one Protocol (`FuniHandle`) with `complete()` and `complete_streaming()`, and one concrete adapter (Ollama). Tomorrow she will want LM Studio, llama.cpp HTTP, Anthropic-compatible (via Claude Code OAuth), OpenAI-compatible (via OpenRouter or local proxy), and possibly Bedrock. The Hermes shape — declarative profile + behavioural transport — scales to all of these without code-duplication. Proposed Ember layout:
  ```
  src/ember/spark/funi/
  ├── profile.py            # FuniProfile dataclass (Ember's ProviderProfile)
  ├── transports/
  │   ├── base.py           # FuniTransport ABC
  │   ├── ollama.py         # current adapter, refactored as a transport
  │   ├── openai_compat.py  # for OpenRouter, LM Studio, llama.cpp HTTP
  │   ├── anthropic.py      # future
  │   └── types.py          # NormalizedFuniResponse + ToolCall + Usage
  └── plugins/              # one __init__.py per provider, like Hermes's plugins/model-providers/
  ```
- **Strengr (cord).** The credential pool is Strengr-shaped, not Funi-shaped. Strengr already owns the tether's health; expanding her to own *multi-credential* tethers is the natural growth path. Today Strengr has one configured target (the Well); tomorrow she will have multi-target failover (multiple OpenRouter keys, primary-and-secondary local Ollama, OAuth-and-API-key Anthropic). The pool's exhaustion-with-typed-reasons pattern (`401 → 5min`, `429 → 1hr`, `default → 1hr`) is directly portable.
- **Munnr (mouth).** The CLI surfaces (`ember auth list`, `ember auth add`, `ember auth remove`, `ember doctor`) all consume the profile registry. Hermes already has equivalent surfaces; the Munnr versions can be much smaller because Ember will start with 2-3 providers, not 30.

**Vows touched:**

- *Reinforced:* Vow of Pluggable Storage (provider profile is itself the plugin shape — same lesson at the model layer); Vow of Modular Authorship (a broken provider plugin doesn't crash Funi — it just doesn't register); Vow of Smallness (declarative profiles are tiny; the behavioural transport is shared across many providers); Vow of Public-Friendliness (the `display_name` / `description` / `signup_url` fields are operator-facing strings).
- *Strain test:* Vow of Smallness — the `agent/credential_pool.py` file is 1,955 lines. Ember's equivalent must not grow that large at v1. The right scope: **single-credential per provider** for slice 3; the pool comes later. Defer multi-credential rotation.
- *At risk:* Vow of Honest Memory — provider failover can confuse the audit log. When credential A times out and B succeeds, the operator's mental model is "this turn succeeded against provider X." If the audit log doesn't record *which credential within X* served the response, debugging gets murky. Mitigation: every audit entry includes `(provider, credential_id_short)` — the latter being the 6-hex of the credential's id, not the credential itself.

**Specific code-level adoption proposals:**

1. `src/ember/spark/funi/profile.py` — `FuniProfile` dataclass mirroring `ProviderProfile` minus the things Ember doesn't need (display_name suffices; description is optional; the hostname-detection bits are for URL-based detection which Ember doesn't do until she has many providers).
2. `src/ember/spark/funi/transports/base.py` — `FuniTransport` ABC with the five required methods + three optional, mirroring `agent/transports/base.py:1-90` verbatim.
3. `src/ember/spark/funi/transports/types.py` — `NormalizedFuniResponse`, `ToolCall`, `Usage`. The `tc.function` backward-compat property included.
4. `src/ember/spark/funi/transports/ollama.py` — port today's adapter into the transport shape. Phase work, not a rewrite.
5. `src/ember/spark/funi/plugins/` — discovery mechanism. Phase 1: hardcoded import of bundled providers. Phase 2: filesystem walk. Phase 3 (post-Vows-stress-test): user plugins at `~/.ember/plugins/funi-providers/`.
6. `src/ember/thread/strengr/credentials.py` — single-credential pool first (one `Credential` per provider, with exhaustion-with-typed-reasons). Multi-credential rotation deferred to slice 4 or later.
7. `src/ember/thread/strengr/retry.py` — typed retry policy with exponential backoff and provider-supplied retry-after parsing.

**Cross-platform check:** All of the above is pure stdlib + Ollama-protocol Python (already shipped). The credential pool's `urllib.request` pattern works on every Ember target. JWT decoding (used in `label_from_token` at `agent/credential_pool.py:181-187`) is base64 + JSON — stdlib.

**Concrete deferrals:**

- **OAuth flows.** Hermes supports `device_code`, `oauth_external`, `copilot`, `aws_sdk` auth types. Ember v1 should support **`api_key` only**. OAuth is large surface area; defer until there's a concrete operator need (e.g., Claude Code OAuth pass-through).
- **Per-provider failover.** Single-provider-with-pool first; cross-provider failover later.
- **Persisted exhaustion state.** In-memory only at v1; persist if the household-sharing scenario shows up.
- **Bedrock / Codex transports.** These are AWS-shaped and OpenAI-Responses-shaped respectively. Ember doesn't need them in slice 3 or 4. Maybe ever.

**Cross-references:**
- The model abstraction layer (10_domain/15_PROVIDERS_MULTI_MODEL) is the Architect's deeper dive on the same surface.
- The execution patterns for failover live in [[30_execution/41_MULTI_PROVIDER_FAILOVER]].
- The hot-cold tier strategy (different models for different hardware classes) lives in [[30_execution/33_HOT_COLD_TIERS]] and consumes the same profile registry.
- The Hermes-vs-Ember crosswalk and dependency-flow docs use the provider/transport split as their model: [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]], [[60_synthesis/62_DEPENDENCY_FLOW]].
