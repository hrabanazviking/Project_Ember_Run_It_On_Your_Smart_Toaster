# 71 — The Heimdall Pattern (Cross-Realm Watch + Single-Door Auth)

How Yggdrasil exposes a *single sentry* through which all
inter-realm communication flows. Named for Heimdall,
guardian of Bifrǫst.

---

## The principle

A naive system has N realms talking to each other in M
patterns — N×M code paths, each with its own auth,
logging, error handling.

**The Heimdall Pattern** centralizes the *gate*: all
cross-realm calls go through a single Heimdall mediator
that handles auth, logging, rate-limiting, and circuit-
breaking.

The result:
- One place to enforce policy.
- One place to instrument.
- One place to test the auth contract.

---

## What Heimdall does

For every cross-realm call:

1. **Authentication**: verifies the caller has permission
   to invoke the target capability.
2. **Authorization**: checks the operator's policy (e.g.,
   "this realm can read but not write").
3. **Rate-limiting**: prevents one realm from drowning
   another.
4. **Circuit-breaking**: if the target realm is failing,
   short-circuit further calls.
5. **Observability**: publishes a Verdandi event for every
   call (subject to sampling).
6. **Audit**: writes to the audit log if the call is
   operator-relevant (per ADR-0011).

All centralized; all consistent.

---

## How it differs from direct calls

Without Heimdall:

```python
# Realm A directly calls Realm B
result = await realm_b.do_thing(args)
```

With Heimdall:

```python
# Realm A goes through Heimdall
result = await heimdall.call(
    caller="realm_a",
    target="realm_b",
    capability="do_thing",
    args=args,
)
```

The wrapper is mechanical. But it gives Heimdall the
opportunity to *insert behavior* without changing the
caller or target.

---

## How auth works through Heimdall

Each realm has a *capability manifest*: what it can be
called for, and what it can call.

```yaml
# Manifest for realm: bifrost
allow_called_by:
  - chat_loop        # the agent
  - smidja           # ingest pipeline can write
deny_called_by:
  - munnr_doctor     # status panel can read but not via
                      # full chat path

allow_calls_to:
  - mimir
  - huginn
  - muninn
  - mempalace

allow_capabilities:
  - search
  - store
  - hybrid_search
```

Heimdall enforces the manifest. Cross-realm calls outside
the manifest get rejected.

This is **the principle of least privilege** applied at
the realm level.

---

## How rate-limiting works

Each realm has per-caller rate limits:

```yaml
# Heimdall rate limits
rate_limits:
  bifrost.search:
    per_caller: 100_per_minute
  cloak.fetch_url:
    per_caller: 30_per_minute   # web is expensive
  hamr.render_frame:
    per_caller: 30_per_second   # smooth animation
```

Caller exceeding limit → typed RateLimited error.

Default: generous. Tuned tighter when needed.

---

## How circuit-breaking works

If a realm has been failing recently (e.g., 5 errors in
30 seconds), Heimdall *trips the circuit*:

```python
def call(self, caller, target, capability, args):
    if self._is_circuit_open(target):
        return Unavailable(f"{target} circuit open; back off")
    
    try:
        result = await self._invoke(target, capability, args)
        self._record_success(target)
        return result
    except Exception as exc:
        self._record_failure(target)
        if self._failure_rate_exceeds(target, threshold=0.5):
            self._open_circuit(target)
        raise
```

Open circuit auto-recloses after a backoff (e.g., 30s).
Stops a failing realm from being hammered.

---

## What Heimdall does NOT do

- **Doesn't process payloads.** It's a gate, not a
  transformer.
- **Doesn't make routing decisions.** The target realm is
  named by the caller; Heimdall enforces but doesn't
  select.
- **Doesn't replace error-boundary patterns.** Errors
  still bubble up the typed-value pattern; Heimdall just
  observes them.
- **Doesn't add latency.** Per-call overhead is ~50µs
  (manifest check + event publish).

---

## Operator-facing observability

Heimdall publishes a Verdandi event for every cross-realm
call (sampled for high-frequency ops):

```python
{
    "type": "heimdall.call",
    "caller": "chat_loop",
    "target": "bifrost",
    "capability": "hybrid_search",
    "result": "ok",
    "latency_ms": 47,
}
```

Doctor screen shows aggregates:

```
Heimdall Cross-Realm Traffic (last 5 min):
  chat_loop → bifrost.hybrid_search:  142 calls (avg 51ms)
  chat_loop → funi.complete:            42 calls (avg 1.2s)
  smidja → bifrost.store:               18 calls (avg 23ms)
  awareness → verdandi.subscribe:        ongoing
  bifrost → mimir.search:              420 calls (avg 12ms)
  bifrost → huginn.search:             420 calls (avg 32ms)
  bifrost → muninn.lookup:             420 calls (avg 4ms)

Circuit states: all closed.
Rate limits: no caller throttled.
```

Operators see *everything happening between realms* — a
window onto the system's internal traffic.

---

## How Heimdall integrates with Kista

For capabilities that need secrets (web fetches with
API keys, MCP servers requiring auth):

```
caller → Heimdall → (verifies auth + manifest)
                  → (asks Kista to resolve secret if target needs one)
                  → invokes target with resolved secret
```

Kista mediates the secret; Heimdall mediates the call.
Together: secrets never appear in plaintext outside the
target's immediate operation.

---

## Configuration shape

```yaml
yggdrasil:
  heimdall:
    enabled: true                    # required in V1
    manifest_path: ~/.ember/yggdrasil/heimdall.yaml
    
    rate_limits:
      default_per_caller_per_min: 1000
      overrides:
        cloak.fetch_url: 30_per_minute
        funi.complete: 60_per_minute
    
    circuit_breaker:
      enabled: true
      failure_threshold: 0.5
      consecutive_failures_to_open: 5
      backoff_seconds: 30
    
    observability:
      sample_high_freq: 0.1
      always_audit:
        - cloak.fetch_url
        - mcp.*
```

---

## Why centralized mediation matters

A common alternative is **inline patterns** — every realm
implements its own auth + logging + rate-limiting. Works
in small systems; breaks down at 11 sibling projects:

- Logic gets duplicated, drifts.
- New cross-cutting concerns (e.g., new audit field)
  require N changes.
- Testing each realm's auth becomes its own job.

Heimdall *concentrates* the concern. One place to fix; one
place to test; one place to monitor.

---

## When Heimdall is unavailable

If Heimdall itself fails (rare; it's a tiny Python
module), cross-realm calls would fail. To prevent total
deadlock:

- Heimdall is **in-process** with every Ember instance
  (no separate daemon).
- It has **no external dependencies** beyond the realms
  themselves.
- Boot-time check verifies it's instantiated; if it can't
  start, Stofa shows a friendly error.

Worst-case: Yggdrasil refuses to boot. Operator gets the
diagnostic; fixes the root cause.

---

## What the operator gains

Operators get a system where:
- *Every* cross-realm call is observable.
- *Every* secret usage is mediated.
- *Every* capability invocation is auditable.
- *Every* failing realm is gracefully isolated.

All without writing or maintaining per-realm boilerplate.

---

## How this relates to the Borg Protocol

The Borg Protocol *discovers paths* through capabilities.
Heimdall *executes calls* along those paths. They're
complementary:

```
operator goal
   ↓
Borg Protocol finds path: A → B → C
   ↓
For each hop:
   Heimdall mediates the call (auth, limits, audit)
   ↓
Result returned to caller
```

Together: a discoverable, governed, observable inter-
realm fabric.

---

## Closing

The Heimdall Pattern is **the gate at every door of
Bifrǫst**. One sentry; consistent enforcement; full
visibility.

The cosmology fits: Heimdall guarded the bridge between
realms. In Yggdrasil-code, our Heimdall guards the bridge
between Ember's realms. The metaphor is load-bearing.

This is the **structural backbone of Yggdrasil's
trust model**.
