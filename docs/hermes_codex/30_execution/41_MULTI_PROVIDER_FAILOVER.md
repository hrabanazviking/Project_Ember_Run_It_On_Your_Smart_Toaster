---
codex_id: 41_MULTI_PROVIDER_FAILOVER
title: Multi-Provider Failover — Credential Pool, Rate Guards, Error Classifier
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - agent/credential_pool.py:94-180
  - agent/credential_pool.py:389-450
  - agent/credential_pool.py:1134-1290
  - agent/error_classifier.py:1-120
  - agent/error_classifier.py:345-450
  - agent/nous_rate_guard.py:1-100
  - agent/nous_rate_guard.py:192-300
  - agent/rate_limit_tracker.py:1-100
  - agent/retry_utils.py:1-58
ember_subsystem_targets: [Strengr, Funi]
cross_refs:
  - 30_execution/31_CROSS_PLATFORM_TACTICS
  - 30_execution/33_HOT_COLD_TIERS
  - 50_verification/53_CRASH_PROOFING_PATTERNS
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Multi-Provider Failover

Inference APIs fail. They fail with 429s when you've hit a rate limit. They fail with 402s when your credit card expired. They fail with 503s when their datacenter is on fire. They fail with 401s when your OAuth token expired five minutes ago and nobody refreshed it. A serious agent never crashes the user's session because of any of these — it rotates, retries, refreshes, or *honestly tells the user* the system is offline.

Hermes does this with three coordinated subsystems:

1. **`credential_pool.py`** (1,955 lines) — a pool of credentials per provider, each with status tracking, exhaustion cooldowns, OAuth refresh, cross-process sync.
2. **`error_classifier.py`** (1,087 lines) — a structured taxonomy of API errors mapping each to a recovery action.
3. **`retry_utils.py`** (57 lines) — jittered exponential backoff that decorrelates concurrent retries.

Plus `rate_limit_tracker.py` for header-parsed quotas and `nous_rate_guard.py` for the Nous Portal's specific shape. I'm Eldra. Let me walk through each piece, then propose Funi's failover behavior under the Vow of Graceful Offline.

## The Credential Pool

`agent/credential_pool.py:94`:

```python
@dataclass
class PooledCredential:
    provider: str
    id: str
    label: str
    auth_type: str
    priority: int
    source: str
    access_token: str
    refresh_token: Optional[str] = None
    last_status: Optional[str] = None
    last_status_at: Optional[float] = None
    last_error_code: Optional[int] = None
    last_error_reason: Optional[str] = None
    last_error_message: Optional[str] = None
    last_error_reset_at: Optional[float] = None
    base_url: Optional[str] = None
    expires_at: Optional[str] = None
    ...
```

A credential is not just a token. It carries:

- **Provider** + **source** — which API, where the credential came from (env var, OAuth device flow, manual entry).
- **Priority** — pool ordering.
- **Auth type** — API key, OAuth bearer, custom JWT.
- **Status** — OK, exhausted, refresh-needed.
- **Error context** — last error code + reason + message + reset timestamp.
- **Refresh metadata** — when the OAuth token expires.

The pool itself (`class CredentialPool` at line 389) holds a sorted list of these and exposes:

```python
def has_credentials(self) -> bool
def has_available(self) -> bool       # at least one not in cooldown
def select(self) -> Optional[PooledCredential]
def peek(self) -> Optional[PooledCredential]
def mark_exhausted_and_rotate(self, *, status_code, error_context) -> Optional[PooledCredential]
def acquire_lease(self, credential_id=None) -> Optional[str]
def release_lease(self, credential_id) -> None
```

The `select()` method (line 1219) is the heart of the failover logic. Three strategies (line 1226-1250):

- **`STRATEGY_RANDOM`** — pick a random available entry.
- **`STRATEGY_LEAST_USED`** — pick the entry with the lowest `request_count`. Load-balances across multiple credentials.
- **`STRATEGY_ROUND_ROBIN`** — rotate priorities so each call uses the next entry.

The default per-provider strategy comes from `get_pool_strategy(provider)` (line 370). Different providers have different shapes — some users have one Nous key and three OpenRouter keys.

## Cross-Process Credential Sync

The most surprising part of `credential_pool.py` is the *sync from on-disk credential stores* (lines 447–760). When a credential is marked `STATUS_EXHAUSTED`, the pool doesn't trust its in-memory state immediately. Before refusing the credential, it syncs from the canonical disk store:

```python
# anthropic: sync from ~/.claude/.credentials.json
def _sync_anthropic_entry_from_credentials_file(self, entry) -> PooledCredential:
    """...When something external (e.g. Claude Code CLI, or another profile's pool)
    refreshes the token, it writes the new pair to ~/.claude/.credentials.json.
    The pool entry's refresh token becomes stale. This method detects that and syncs."""
```

Same pattern for Codex (`auth.json`), xAI OAuth (`auth.json`), Nous (`auth.json`). Each provider has a canonical disk store; the pool entry shadows it.

**Why this matters**: OAuth refresh tokens are *single-use*. When Process A refreshes a token, Process B's pool entry holds a now-invalid refresh token. Without the sync, Process B is locked out of Process A's freshly-renewed credentials until the cooldown elapses (which can be hours for ChatGPT weekly quotas).

The sync runs *only when the entry is already exhausted* — lines 1149-1192. Steady-state cost is zero. Recovery cost is one disk read. This is the right shape: fast path stays fast, slow path stays correct.

## Lease-Based Concurrency

Lines 1282–1320:

```python
def acquire_lease(self, credential_id: Optional[str] = None) -> Optional[str]:
    ...
def release_lease(self, credential_id: str) -> None:
    ...
```

Multiple concurrent agent threads (gateway sessions, delegate_task children) can call `select()` simultaneously. Without leases, they'd all grab the same credential and *triple-blow* a per-minute quota. Leases pace the dispatch:

```python
self._max_concurrent = DEFAULT_MAX_CONCURRENT_PER_CREDENTIAL
```

Per-credential concurrency cap. Default is small (1-3). If all credentials are leased to capacity, new requests wait. This is the **bulkhead pattern** — failure of one credential doesn't drag down the pool.

## Exhaustion Cooldown

Lines 199-205:

```python
def _exhausted_ttl(error_code: Optional[int]) -> int:
    """Return cooldown seconds based on the HTTP status that caused exhaustion."""
    if error_code == 401:
        return EXHAUSTED_TTL_401_SECONDS
    if error_code == 429:
        return EXHAUSTED_TTL_429_SECONDS
    return EXHAUSTED_TTL_DEFAULT_SECONDS
```

Different status codes get different cooldowns. 401 (auth failed) is typically longer than 429 (rate limit) because a 401 usually means "you need to re-auth" while a 429 might clear in 60 seconds.

The reset timestamp is parsed from the response headers when present (line 208 `_parse_absolute_timestamp` + line 238 `_extract_retry_delay_seconds`). When the provider says "retry after 3600 seconds," Hermes records `last_error_reset_at = now + 3600` and refuses the entry until then.

## The Error Classifier

`agent/error_classifier.py:24-62` is the taxonomy:

```python
class FailoverReason(enum.Enum):
    auth = "auth"
    auth_permanent = "auth_permanent"
    billing = "billing"
    rate_limit = "rate_limit"
    overloaded = "overloaded"
    server_error = "server_error"
    timeout = "timeout"
    context_overflow = "context_overflow"
    payload_too_large = "payload_too_large"
    image_too_large = "image_too_large"
    model_not_found = "model_not_found"
    provider_policy_blocked = "provider_policy_blocked"
    format_error = "format_error"
    thinking_signature = "thinking_signature"
    long_context_tier = "long_context_tier"
    oauth_long_context_beta_forbidden = "oauth_long_context_beta_forbidden"
    llama_cpp_grammar_pattern = "llama_cpp_grammar_pattern"
    unknown = "unknown"
```

Eighteen reasons. Each maps to a distinct recovery action. The `ClassifiedError` dataclass (line 66) carries:

```python
retryable: bool = True
should_compress: bool = False
should_rotate_credential: bool = False
should_fallback: bool = False
```

These flags are what the retry loop reads, NOT the reason itself. The classifier is the single point of "what does this error mean?" — every other piece of code just looks at the flags.

The classification pipeline (`classify_api_error` at line 345) is *priority-ordered*. Pattern matching happens in a deliberate sequence:

1. Extract status code from the exception.
2. Extract the error body (JSON if available).
3. Check status-based branches (`_classify_by_status` at line 618).
4. Check error code branches (`_classify_by_error_code` at line 867).
5. Check message-pattern branches (`_classify_by_message` at line 907).

Provider-specific quirks are handled as patterns in the message branch (e.g., Anthropic's "long-context tier" wording, OpenRouter's "no endpoints support tool calling" wording, llama.cpp's grammar-pattern rejection).

Two specific quirks are worth calling out:

- **`oauth_long_context_beta_forbidden`** (line 57) — Anthropic OAuth subscription tiers reject the 1M-context beta header. Recovery: disable the beta and retry.
- **`llama_cpp_grammar_pattern`** (line 58) — llama.cpp's tool-call JSON schema converter rejects regex escapes. Recovery: strip the `pattern`/`format` from tool defs and retry.

These are not generic recovery actions. They are *provider-specific surgical fixes* that the classifier emits as targeted flags. The retry loop knows what to do with each.

## Jittered Backoff

`agent/retry_utils.py` is 57 lines. The whole thing:

```python
def jittered_backoff(
    attempt: int,
    *,
    base_delay: float = 5.0,
    max_delay: float = 120.0,
    jitter_ratio: float = 0.5,
) -> float:
    ...
    seed = (time.time_ns() ^ (tick * 0x9E3779B9)) & 0xFFFFFFFF
    rng = random.Random(seed)
    jitter = rng.uniform(0, jitter_ratio * delay)
    return delay + jitter
```

The classical mistake is `time.sleep(2 ** attempt)`. The classical fix is `time.sleep(2 ** attempt + random.uniform(0, 1))` — the **thundering herd** prevention. Hermes uses a *thread-local-mixed seed* (line 41-46) so concurrent retries in different threads decorrelate. The `0x9E3779B9` is the golden ratio constant — a well-known good multiplier for hash mixing.

The default base is 5 seconds; max is 120. Attempt 1 ⇒ 5s + jitter. Attempt 2 ⇒ 10s + jitter. Attempt 5 ⇒ 80s + jitter. Attempt 10 ⇒ 120s + jitter (capped).

This module is the cheapest single steal-target in Hermes. 57 lines. Copy verbatim.

## Rate-Limit Headers — `rate_limit_tracker.py`

`agent/rate_limit_tracker.py` parses 12 standard `x-ratelimit-*` headers into a `RateLimitState` dataclass with four buckets (requests/min, requests/hr, tokens/min, tokens/hr). Each `RateLimitBucket` exposes:

```python
@property
def usage_pct(self) -> float: ...

@property
def remaining_seconds_now(self) -> float:
    """Estimated seconds remaining until reset, adjusted for elapsed time."""
    elapsed = time.time() - self.captured_at
    return max(0.0, self.reset_seconds - elapsed)
```

The user can run `/usage` and see:

```
Nous Rate Limits (captured 12s ago):

  Requests/min  [████████░░░░░░░░░░░░] 40.0%  4/10 used (6 left, resets in 48s)
  Requests/hr   [██░░░░░░░░░░░░░░░░░░] 10.0%  20/200 used (180 left, resets in 47m)
  Tokens/min    [██████████░░░░░░░░░░] 50.0%  500/1.0K used (500 left, resets in 48s)
  Tokens/hr     [█░░░░░░░░░░░░░░░░░░░] 5.0%   10K/200K used (190K left, resets in 47m)

  ⚠ tokens/min at 50% — resets in 48s
```

The formatting at line 165-179 (`_bucket_line`) is doing real work: ASCII progress bar, human-readable counts (`_fmt_count` at 135), human-readable durations (`_fmt_seconds` at 146). The user gets *observable system state* without leaving the agent.

## Nous-Specific Rate Guard

`agent/nous_rate_guard.py` is the Nous Portal–specific layer on top. The Portal exposes rate limit state in a way that can be checked *without making a request* (a state file at `_state_path()` line 29). The guard at line 71+ (`record_nous_rate_limit`) writes that state. The check at line 139 (`nous_rate_limit_remaining`) tells the agent "we know we're out for 47 more minutes; don't even try."

This is a small but important pattern: **state that lives outside any individual request**. The agent that just hit a 429 on Nous writes the cooldown to the state file; the next agent (in a different process) reads it and skips the doomed request. Cross-process coordination through a shared state file. No central scheduler needed.

## What This Means for Ember — Funi's Failover Behavior

Funi is the local LLM runtime. Ember's primary failover concern is NOT "what if Anthropic is down" — it's "what if Ollama crashed" or "what if Strengr can't reach the Well."

But there's a real story for remote Funi providers too: an Ember user who has both Ollama running locally AND a tailnet-reachable Ollama on their workstation. Funi can choose. The credential pool + classifier patterns transfer.

### Funi's pool — but smaller

```python
# src/ember/spark/funi/pool.py
@dataclass(frozen=True)
class FuniEndpoint:
    name: str
    runtime: Literal["ollama", "llama.cpp", "lmstudio", "openai_compat"]
    base_url: str
    model: str
    priority: int
    label: str = ""
    last_status: Literal["ok", "exhausted", "unreachable"] = "ok"
    last_status_at: float | None = None
    last_error_message: str | None = None
    last_error_reset_at: float | None = None
```

No OAuth tokens for v1 — Funi endpoints are typically API-key-less (local Ollama) or simple Bearer (cloud OpenAI-compat). Single-use refresh tokens are not in v1's scope.

The pool:

```python
class FuniPool:
    def __init__(self, endpoints: list[FuniEndpoint]): ...

    def select(self) -> FuniEndpoint | None: ...
    def has_available(self) -> bool: ...
    def mark_exhausted(self, ep: FuniEndpoint, *, status_code: int | None, error_message: str | None) -> None: ...
```

`select()` picks the highest-priority endpoint that is not in cooldown. Strategies in v1 = just priority order. Add LEAST_USED in v2 if users actually want it.

### Funi error classifier

```python
# src/ember/spark/funi/error_classifier.py
class FailoverReason(enum.Enum):
    auth = "auth"
    rate_limit = "rate_limit"
    timeout = "timeout"
    context_overflow = "context_overflow"
    server_error = "server_error"
    network_unreachable = "network_unreachable"
    model_not_found = "model_not_found"
    payload_too_large = "payload_too_large"
    unknown = "unknown"

@dataclass
class ClassifiedError:
    reason: FailoverReason
    retryable: bool = True
    should_compress: bool = False
    should_rotate_endpoint: bool = False
    should_abort: bool = False
    message: str = ""
```

Nine reasons (vs Hermes's 18). Ember doesn't need:
- `thinking_signature` (no Anthropic OAuth specifics).
- `long_context_tier` (no subscription tiers).
- `oauth_long_context_beta_forbidden` (no Anthropic OAuth).
- `llama_cpp_grammar_pattern` — actually, KEEP this one if Ember supports llama.cpp. It's a real bug, real users hit it.
- `provider_policy_blocked` (no aggregators in v1).

Add `network_unreachable` as a first-class reason. Pi users go offline. Ember should classify the offline state distinctly from a 503 — different recovery path.

### Funi retry — adopt verbatim

`agent/retry_utils.py` ports as-is. Put it at `src/ember/strengr/retry.py`. Strengr owns retry because the tether is what survives network blips.

```python
# src/ember/strengr/retry.py
def jittered_backoff(
    attempt: int,
    *,
    base_delay: float = 2.0,    # Ember default is faster — local providers
    max_delay: float = 60.0,
    jitter_ratio: float = 0.5,
) -> float: ...
```

The defaults are smaller than Hermes's. Hermes's 5-120s defaults are calibrated for cloud APIs where 429s typically clear in 10-60s. Ember's local Funi (Ollama unresponsive) typically clears in 2-30s. Faster retry, faster recovery, no thundering herd because there's usually one Ember.

### Rate limit headers — adopt selectively

`rate_limit_tracker.py` is general-purpose. Ports cleanly to Ember. Most Funi backends (Ollama, llama.cpp) don't emit the headers, so the tracker degrades to "no data." For OpenAI-compatible cloud endpoints (the user's optional tier-up to a cloud Funi), the headers exist and the tracker works.

`format_rate_limit_display` and `format_rate_limit_compact` give Munnr a free `/usage` command. Ship the tracker as `src/ember/strengr/rate_tracker.py`.

### State-file rate guard — adopt for Strengr

The Nous-specific guard generalizes to "any rate-limited endpoint." Strengr writes per-endpoint state to `~/.ember/state/rate_limits.json`:

```json
{
  "openai_compat:cloud.example.com": {
    "captured_at": 1700000000.123,
    "remaining_until": 1700001200.000,
    "reason": "tokens/min exhausted"
  }
}
```

Before issuing a request, Strengr reads the state file and skips the endpoint if `remaining_until > now`. Cross-process coordination, zero infrastructure. Vow of Smallness preserved.

### Vow of Graceful Offline — the load-bearing translation

When `FuniPool.select()` returns None (all endpoints exhausted or unreachable), Ember does NOT retry indefinitely and does NOT silently fall back to fabrication. It says:

```
I can't reach Funi right now.
  - ollama-local: unreachable (timeout after 30s) — retry in 60s
  - ollama-workstation: unreachable (network unreachable) — retry in 60s

Suggestion: check if Ollama is running (`systemctl status ollama` or `pgrep -f ollama`).
```

This is the [[Vow of Graceful Offline]] rendered in code. The classifier produces a structured failure; Munnr renders it; the user knows exactly what's broken.

Critically, **the agent does not confabulate**. It does not generate a hallucinated response when Funi is unreachable. Per [[Vow of Honest Memory]], the Well is also unavailable in this state — but the chat REPL is still alive and can offer purely-procedural help ("here's how to check Ollama status").

### Vows on the line

- **Vow of Graceful Offline** — strengthened. Unreachable Funi produces a clear typed failure.
- **Vow of Tethered Grounding** — strengthened. The agent never falls back to confabulation when the model is unreachable.
- **Vow of Honest Memory** — strengthened. Error states are recorded in `state.json` and visible via `ember status`.
- **Vow of Smallness** — preserved. Funi pool in v1 supports priority order only; LEAST_USED and ROUND_ROBIN are v2 additions if users want them.
- **Vow of Modular Authorship** — strengthened. The classifier is a sibling module; if it crashes, requests still execute (default to "unknown, retry once" semantics).

### Concrete deliverables

1. `src/ember/spark/funi/pool.py` — endpoint pool with priority-order selection + cooldown tracking.
2. `src/ember/spark/funi/error_classifier.py` — 9-reason taxonomy with structured ClassifiedError + recovery flags.
3. `src/ember/strengr/retry.py` — jittered backoff verbatim from Hermes.
4. `src/ember/strengr/rate_tracker.py` — header parsing + display formatting.
5. `src/ember/strengr/state.py` — cross-process state file for rate limit cooldowns.

Total < 1,200 LoC. Each module is independently testable. No new dependencies.

### What I do not propose

- **OAuth flow handling in v1.** Most Funi backends don't need it. Cloud-Funi users can put a Bearer token in env vars.
- **Lease-based concurrency.** Premature for a Pi user with 1-3 endpoints.
- **18-reason classifier.** Use the 9-reason set that maps to Ember's actual failure modes.
- **Cross-process credential sync from on-disk stores.** No OAuth refresh tokens means no shadow-state-on-disk pattern needed.

### Where to read next

- [[30_execution/31_CROSS_PLATFORM_TACTICS]] — the proxy/HTTP layer that the pool sits on top of.
- [[30_execution/33_HOT_COLD_TIERS]] — how tier selection interacts with the Funi pool.
- [[50_verification/53_CRASH_PROOFING_PATTERNS]] — survival patterns that complement failover.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — Strengr's expanded scope to own all retry+rate state.

A failure is data. Classify it. Cooldown it. Try the next thing. Don't lie to the user. — Eldra.
