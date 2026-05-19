# 10 — Graceful Degradation Strategies

**Category:** Robustness Fundamentals
**Runa relevance:** kernel (response shaping under degraded conditions), adapters (offline modes), Heimskringla (model fallbacks)
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

When something goes wrong — a backend is down, a model is rate-limited, a tool is broken — the worst response is *complete failure*. A slightly worse response — partial functionality, an honest "I can't do that right now, but here's what I can do" — is dramatically better. **Graceful degradation** is the discipline of building systems where failures *narrow the agent's capability* rather than *kill it entirely*.

For Runa, graceful degradation is what turns "Anthropic is having an outage" from "Runa is unresponsive" into "Runa is slower because she's using the local model, and she told Volmarr that." It is the user-facing complement to circuit breakers and bulkheads ([[07-circuit-breaker]], [[08-bulkhead-pattern]]) — those handle the *technical* fail-safe; graceful degradation handles *what the user sees and experiences*.

## 2. Technique / mechanism

**The hierarchy of degradation:**

```
Full capability      ← everything works
       ↓
Slightly degraded    ← e.g., slower because cloud is down, using local
       ↓
Partial capability   ← e.g., can't search the web, but other tools work
       ↓
Honest no-op         ← "I can't do that right now; here's why"
       ↓
Silent failure       ← never acceptable
```

**Five degradation patterns:**

### Pattern 1 — Fallback to alternative

```python
async def call_with_fallback(request: Request) -> Response:
    try:
        return await primary_provider.complete(request)
    except (CircuitOpenError, ModelProviderError) as e:
        logger.warning("primary failed, falling back", exc_info=e)
        return await fallback_provider.complete(request)
```

Heimskringla model routing is fallback-heavy: cloud Claude → local Llama if Claude is unavailable.

### Pattern 2 — Cached / stale data

```python
async def get_fresh_or_stale(key: str) -> Result:
    try:
        return await fetch_fresh(key)
    except FetchError:
        cached = await cache.get_stale(key)
        if cached:
            return Response(data=cached, stale=True, fetched_at=cached.timestamp)
        raise
```

When fresh data unavailable, return stale with explicit marking. Many production systems do this.

### Pattern 3 — Reduced functionality

```python
class AgentReply:
    text: str
    tool_calls_made: list[ToolCall]
    tool_calls_skipped: list[tuple[str, Reason]]  # which tools were unavailable
    confidence: float  # lower if some tools were missing
```

Reply explicitly notes what *didn't happen*. The user sees a complete reply with caveats.

### Pattern 4 — Read-only mode

When writes are failing (database down, disk full), serve reads but reject writes with clear errors:

```python
class MuninnReader:
    def get_episode(self, id: UUID) -> Episode | None:
        # Always available (reads from cached / replica state)
        ...

class MuninnWriter:
    def write_episode(self, episode: Episode) -> None:
        if self.degraded_mode:
            raise WriteDegradedError(
                "Memory writes temporarily unavailable; episode queued for retry"
            )
        ...
        # When writes restored, queued episodes are flushed
```

The agent can keep responding (reading); writes queue for later.

### Pattern 5 — Defer the operation

```python
async def deliver_message(adapter: str, message: str) -> None:
    try:
        await adapters[adapter].send(message)
    except AdapterError as e:
        # Queue for later delivery via Skuld
        await skuld.queue_task(
            DeferredDelivery(adapter=adapter, message=message),
            retry_after=300,  # try again in 5 minutes
        )
        await notify_user(
            f"I'll deliver to {adapter} when it's back up; for now I've queued it."
        )
```

The user knows the work was accepted and will happen.

**Telling the user about degradation:**

The hardest part of graceful degradation is *honest user-facing communication*. Patterns:

- **Banner / status indicator** — "Degraded mode: some adapters unavailable." Visible per surface.
- **Inline explanation** — "I used the local model for this reply because Claude is unavailable. The reply may be less detailed than usual."
- **Deferred acknowledgement** — "I've queued that for delivery; you'll get a notification when it goes through."
- **Refusal with reason** — "I can't search the web right now (web tool unavailable). Want me to try based on what I already know?"

**What graceful degradation is NOT:**

- *Silent fallback to wrong answer.* If Claude is down and Llama produces a noticeably worse answer, the user must know.
- *Caching stale data without marking it stale.* The user thinks they're getting current info.
- *Pretending a tool ran when it didn't.* Hallucinated tool calls are corrosive.
- *Indefinitely degraded operation.* Degradation is a *temporary* state; restoration must be tracked.

**State and observability:**

```python
@dataclass
class DegradationState:
    subsystem: str
    degraded_since: datetime
    reason: str
    fallback_in_use: str | None
    capability_loss: list[str]

class DegradationMonitor:
    """Track degraded subsystems and announce to user / log."""
    states: dict[str, DegradationState] = field(default_factory=dict)
    
    def degrade(self, subsystem: str, reason: str, fallback: str | None = None):
        ...
    
    def restore(self, subsystem: str):
        ...
    
    def current_capability_loss(self) -> list[str]:
        return [cap for state in self.states.values() for cap in state.capability_loss]
```

`runa doctor` reports current degradation; restoration produces an "all clear" notification.

## 3. Key works / libraries

- **Nygard, M.** *Release It!*, 2nd ed. Covers degradation alongside circuit breakers and bulkheads.
- **Beyer, B. et al.** *Site Reliability Engineering* (the Google SRE book), O'Reilly 2016. Has good chapters on graceful degradation in production services.
- **`stamina`** (github.com/hynek/stamina) — modern retry-with-fallback.
- **Hystrix** (Netflix) — `HystrixCommand.getFallback()` was the productionised fallback pattern.
- **CDN failover patterns** — origin-down patterns from Fastly, Cloudflare, Akamai engineering blogs.
- **Honeycomb's "Observability Engineering"** — chapters on degradation-aware monitoring.

## 4. Pitfalls and gotchas

- **Fallback is sometimes worse than failure.** A fallback model that produces low-quality output that gets cached and treated as canonical can be more damaging than an honest "unavailable." Audit before deciding fallback is right.
- **Cascading degradation.** Subsystem A degrades, fallback uses subsystem B; subsystem B can't handle the extra load; it degrades too. Mitigate with bulkheads and rate limits on fallback paths.
- **Forgotten degradation.** A subsystem went degraded; never restored; operator unaware. Always emit restoration events; alert if degraded > N hours.
- **Silent stale data.** Caches without freshness markers are everyone's worst-of-both-worlds.
- **Hallucinated success.** Returning "ok" when the operation didn't actually happen. Worse than any error.
- **No degradation budget.** If degraded mode is free to use, callers don't know to expect it. Bounded use ("up to 10% of traffic to fallback before alarming") keeps the system honest.
- **Quality regressions hidden by degradation.** The fallback path is rarely tested at the same quality bar as the primary. Test both.

## 5. Applicability to Runa

For **Heimskringla**:

- Per-provider circuit breakers ([[07-circuit-breaker]]) drive routing. When a breaker opens, requests route to fallback providers.
- Fallback chain configured per request type:
  - High-stakes: Claude → GPT-4 → cancel-with-explanation. Don't degrade to local for the hardest queries.
  - Standard: Claude → Llama-local. Local handles most things adequately.
  - Background / low-stakes: Local-only.
- Every reply notes "model used"; if it wasn't the preferred model, that's visible in the audit log and (optionally) the user-facing reply.

For **adapters**:

- A failed adapter is quarantined ([[07-circuit-breaker]]). Messages queue in Skuld for delivery when restored.
- Other adapters keep working. The user can be told via any working surface that one is down.

For **Smiðja tools**:

- A failed tool returns a structured `Unavailable(tool_name, reason, alternatives)` result. The kernel can either re-plan (use a different tool) or report to user.

For **Muninn**:

- Read failures are fatal (Runa can't function without memory).
- Write failures degrade gracefully: write-ahead log buffers writes; flushed when Muninn restored.

For **WYRD bridge**:

- World-model unavailability degrades to "operating without world context." Reply might say "I'm not seeing the project graph right now; my answer is based on what I remember from our conversation."

For **Eldhugi (emotional state)**:

- Eldhugi failure degrades to "neutral baseline emotional state." Affect-modulation is disabled; kernel keeps running.

For **user-facing surfaces**:

- The Munnr CLI and Auga GUI show a degradation banner when subsystems are down.
- Rödd's voice can carry a degradation note ("My web tool is unavailable, so I can't look that up right now").

For **Volmarr-facing observability**:

- `runa doctor` shows degraded subsystems prominently.
- A degradation event lasting > 1 hour triggers `Notified` to Volmarr.

What to avoid:

- Don't degrade silently. The user (and the operator) must know.
- Don't claim success when degraded operation produced lower-quality result.
- Don't make fallbacks unbounded. They should be temporary; restoration is the goal.
- Don't hide degradation from the audit log. Every fallback should be logged.

## 6. Open questions

- **How much to tell the user.** Too much degradation chatter is annoying; too little is dishonest. Tuning per-user is open.
- **Quality regression of fallbacks.** Models / providers vary; the fallback may produce subtly worse answers in ways hard to detect.
- **Cross-subsystem coordination.** When multiple subsystems are degraded, the right combined behaviour is non-obvious. Some combinations are worse than any single failure.
- **Restoration verification.** Knowing a subsystem is "back" requires probing; probing can falsely indicate success. Conservative restoration > eager.

## 7. References (curated)

- Nygard, *Release It!*, 2nd ed.
- *Site Reliability Engineering* (Beyer et al., 2016), chapters 22-27.
- aws.amazon.com/builders-library/ — multiple relevant articles.
- engineering.fb.com — many degradation case studies (search "graceful degradation").
- Companion docs: [[06-retry-strategies]], [[07-circuit-breaker]], [[08-bulkhead-pattern]], [[14-health-checks]].
