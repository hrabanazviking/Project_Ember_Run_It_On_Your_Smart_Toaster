# 51 — Health Gossip Protocol

How realms in Yggdrasil tell each other (and the operator)
their current state. The continuous-awareness layer.

---

## Why gossip

Traditional distributed-systems "health check" patterns
involve a central coordinator pinging each component on a
schedule. This:
- Has a single point of failure (the coordinator).
- Adds latency (operations wait for next probe).
- Scales poorly (every component needs probing).

**Gossip protocol** flips it: each realm *broadcasts* its
own state at regular intervals to a shared channel
(Verdandi). Everyone who cares can listen.

Properties:
- No central coordinator.
- State is continuously available.
- Each realm pays a small constant cost (one publish per
  interval).
- Late joiners catch up quickly (read recent events from
  the bus).

---

## What gets gossiped

Each realm publishes a `health` event every 30 seconds
(operator-tunable):

```python
{
    "type": "health.beat",
    "realm": "mimir",
    "timestamp": "2026-05-21T14:32:18Z",
    "status": "ok",                # ok / degraded / unavailable
    "version": "1.4.2",
    "detail": "10245 chunks, 23 docs",
    "metrics": {
        "memory_mb": 32,
        "disk_used_mb": 45,
        "last_op_ms": 12
    }
}
```

Each realm decides what `detail` and `metrics` mean for its
own state. The schema is operator-readable but realm-
specific.

---

## What "status" means

Three canonical values:

- **`ok`** — realm is responding to operations normally.
- **`degraded`** — realm is working but slower / partial.
  Example: Huginn responding but slow due to index
  rebuild.
- **`unavailable`** — realm cannot serve requests.
  Example: Qdrant container is restarting.

The status reflects the realm's own assessment. Subscribers
trust it.

---

## Who subscribes

| Subscriber | Why |
|---|---|
| `DoctorService` | aggregates for the Doctor screen |
| `StatusBar` in Stofa | shows realm dots in chrome |
| Reconciliation worker | knows when to retry failed ops |
| Awareness layer | "I notice X realm came back up" |
| External monitoring (if operator-configured) | bridges to Prometheus etc. |
| Yggdrasil Bridge (Phase 4) | coordinates across devices |

Subscription is **read-only**; nobody can *demand* a realm
report. Realms gossip on their own schedule.

---

## What if a realm stops gossiping?

If 3× the publish interval elapses without a heartbeat
from a realm (e.g., 90 seconds for a 30-second interval),
subscribers infer the realm is *probably* down. The
`DoctorService` marks it as `health.stale` and updates the
DoctorScreen.

This is *passive failure detection* — no probing needed;
absence of expected heartbeats is the signal.

---

## How realms learn each other's state

Bidirectional. Each realm can subscribe to other realms'
heartbeats. Examples:

- **Bifrǫst** subscribes to mimir / huginn / muninn beats
  so it knows which backends are healthy *before*
  attempting a fan-out.
- **Awareness layer** subscribes to all realms so it can
  surface "you've been chatting through a Mímir outage
  — some retrieval may have been incomplete."
- **Reconciliation worker** subscribes so it knows when to
  retry receipts.

The gossip pattern means each subscriber gets the
information *without polling*.

---

## Per-realm health contract

Each realm implements:

```python
class HealthSource(Protocol):
    """A realm that publishes health gossip."""
    
    REALM_NAME: ClassVar[str]
    PUBLISH_INTERVAL_S: ClassVar[float] = 30.0
    
    async def gather_health(self) -> HealthBeat:
        """Compute current state."""
        ...
    
    async def gossip_loop(self, event_bus: EventBus) -> None:
        """Run forever, publishing health beats."""
        while True:
            beat = await self.gather_health()
            event_bus.publish("health.beat", beat.to_dict())
            await asyncio.sleep(self.PUBLISH_INTERVAL_S)
```

Each realm adapter inherits this. The Yggdrasil layer
starts gossip loops for each enabled realm at boot.

---

## Configuration shape

```yaml
yggdrasil:
  gossip:
    enabled: true
    publish_interval_s: 30
    stale_multiplier: 3            # 3× interval = "stale"
    subscribers:
      doctor: true                 # aggregate for Doctor screen
      status_bar: true             # show in chrome
      external_bridge: false       # opt-in for Prometheus etc.
```

---

## How gossip enables self-healing

Consider this sequence:

1. Qdrant container crashes (Huginn unreachable).
2. Bifrǫst tries a fan-out; Huginn arm times out.
3. Bifrǫst's adapter publishes `health.beat` for huginn:
   `status: unavailable`.
4. The reconciliation worker, awareness layer, and Stofa's
   StatusBar all react:
   - Reconciliation: notes; will retry when status changes.
   - Awareness: chat banner: "Semantic memory is currently
     unavailable; using keyword + associative only."
   - StatusBar: huginn dot goes red.
5. Operator restarts Qdrant (or it auto-restarts).
6. Huginn's gossip loop publishes `health.beat` with
   `status: ok`.
7. Reconciliation worker retries pending Huginn writes.
8. Stofa's status dot goes green.
9. Awareness: optional banner: "Semantic memory restored."

Operator-experience: brief degradation, transparent
recovery, no manual intervention required for typical
failures.

---

## Why "gossip" not "broadcast"

Both terms exist in distributed systems:
- **Broadcast**: one-to-many, often pushed by sender.
- **Gossip**: peer-to-peer, each node tells a random
  subset.

We use the word "gossip" *informally* — our pattern is
closer to "publish to a shared bus." We're not doing the
classical epidemic-gossip routing. But the metaphor of
*continuous, casual updates each realm casually
emits* fits the operator's intuition better than "health
check protocol" — which sounds adversarial.

Gossip is what neighbors do in a household. That's the
Norse domestic register applied to distributed-systems
terminology.

---

## What this is NOT

- **Not a leader-election protocol.** No one is voting
  on who's healthy.
- **Not a consensus protocol.** No quorum, no Paxos, no
  Raft.
- **Not a coordinator-free distributed database.** Each
  realm's data lives in its realm; gossip is just for
  health signaling.

Simple, fit-for-purpose.

---

## Operator-facing example

Stofa StatusBar shows realm dots; they reflect gossip
state in near-real-time.

```
[ ● Funi · ● Well · ● MCP 2/2 · ◉ Huginn restarting · ● Verdandi ]
```

(`◉` = degraded; `●` green/red for ok/unavailable.)

Doctor screen aggregates with detail:

```
Realm          Status       Last beat     Detail
────────       ─────────    ──────────    ──────
Funi           ● ok         12s ago        llama3.2:3b
Strengr        ● ok         5s ago         backend: sqlite_vec
Brunnr         ● ok         5s ago         95 docs
Mímir          ● ok         8s ago         10245 chunks
Huginn         ◉ degraded   30s ago        rebuilding index
Muninn         ● ok         15s ago        140 associations
Verdandi       ● ok         20s ago        event bus active
Kista          ● ok         (passive)      vault unlocked
Astrology      ● ok         (slow cycle)   refreshed 25min ago
```

The operator sees what's healthy, what's degraded, and how
recent the information is.

---

## Closing

The Health Gossip Protocol is **continuous,
decentralized, operator-visible awareness** of every
realm's state. No coordinator. No silent failures.
Recovery (when it happens) is naturally noticed.

This is the foundation that makes everything in
[`50_SELF_HEALING_PHILOSOPHY.md`](50_SELF_HEALING_PHILOSOPHY.md)
actually work.
