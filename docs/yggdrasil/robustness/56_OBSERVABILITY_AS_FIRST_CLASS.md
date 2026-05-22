# 56 — Observability as First-Class

Why observability isn't an add-on in Yggdrasil. It's part
of the architecture from line 1.

---

## The principle

Most software treats observability as **something you bolt
on later**: structured logging gets retrofitted, metrics
get added when something breaks, distributed tracing
becomes a "we'll do it in Q4" item.

Yggdrasil's architecture *requires* observability for its
self-healing to work. So observability is *first-class* —
designed in, not retrofitted.

---

## The three pillars (re-stated)

Per [`../architecture/38_THE_CROSSCUTTING_OBSERVABILITY.md`](../architecture/38_THE_CROSSCUTTING_OBSERVABILITY.md):

1. **Verdandi event bus** — real-time event stream.
2. **Structured logs** — persistent record (Batch J's
   logging system).
3. **Doctor screen** — on-demand snapshot.

Each is *integrated*, not added.

---

## Why this matters

Without observability:
- Self-healing playbooks can't trigger (no signal).
- Reconciliation can't retry (no receipts).
- Operator can't debug (no data).
- Ember can't be self-aware (no event history).

With observability:
- All of the above work, by construction.

The system *would not function* without observability. So
it has to be first-class — there's no version of Yggdrasil
without it.

---

## What "first-class" means concretely

### 1. Every cross-realm call publishes an event

Not "if there's a problem" — *always*. The reconciliation
+ self-awareness + Doctor surfaces all depend on the event
being there.

### 2. Every realm exposes structured health

Per the gossip protocol. Each realm contributes its own
health beat; the system aggregates.

### 3. Every operator-facing surface includes observability

Stofa's StatusBar shows realm dots. The Doctor screen
shows detail. The debug overlay (Ctrl-Shift-D) shows live
events. Operators *see* the system's state without asking.

### 4. CI tests for observability coverage

A test verifies that every realm publishes its health beat
at the configured interval. Another verifies that the
event-bus catches the events Stofa expects to render.

### 5. Audit log is part of observability

The audit log (per ADR-0011) is the *security*-relevant
record. It's separate from Verdandi (which is
operational), but together they cover the full
observability surface.

---

## The minimum observability budget

Every new realm or feature MUST:

1. **Publish at least one Verdandi event** for each
   significant operation.
2. **Implement the `HealthSource` Protocol** for its gossip
   beat.
3. **Document its events** in
   `docs/yggdrasil/observability/<realm>.md`.
4. **Add a Stofa StatusBar contribution** if operator-
   relevant.
5. **Add a Doctor row** if operator-actionable.

The budget is *small per feature*; the cumulative effect
is system-wide visibility.

---

## What gets observed (the catalog)

Comprehensive list of event types in Yggdrasil V1:

### Lifecycle
- `realm.started`, `realm.stopped`, `realm.health.beat`
- `yggdrasil.boot.completed`
- `yggdrasil.shutdown.started`

### Memory
- `mimir.chunk_stored`, `mimir.decay_applied`,
  `mimir.promotion_triggered`, `mimir.contradiction_detected`
- `huginn.vector_indexed`, `huginn.recall_returned`,
  `huginn.recall_failed`
- `muninn.association_strengthened`, `muninn.pruned`
- `bifrost.fusion_completed`, `bifrost.degraded_mode`

### Chat
- `chat.turn_started`, `chat.turn_finished`,
  `chat.turn_failed`
- `chat.episode_persisted`

### Tools
- `tool.proposed`, `tool.approved`, `tool.denied`,
  `tool.executed`, `tool.audited`, `tool.timeout`

### MCP
- `mcp.server_connected`, `mcp.server_disconnected`,
  `mcp.ping_completed`

### Secrets
- `secret.resolved` (key only, never value),
  `kista.unlock_required`, `kista.unlock_succeeded`

### Rhythm + Mood
- `rhythm.phase_change`, `rhythm.eclipse_event`
- `mood.classified`, `mood.seed_used`

### Awareness
- `awareness.summary_built`, `awareness.pattern_detected`,
  `awareness.surfaced_to_chat`

### Audit
- `audit.citation_check.passed/failed`,
  `audit.consistency_check.passed/failed`,
  `audit.capability_check.passed/failed`

### Reconciliation
- `reconciliation.receipt_created`,
  `reconciliation.retry_started`,
  `reconciliation.receipt_resolved`,
  `reconciliation.receipt_failed_permanently`

### Recovery
- `recovery.playbook_triggered`, `recovery.step_completed`,
  `recovery.escalated_to_operator`

### Backup (Norns)
- `norns.snapshot_started`, `norns.snapshot_completed`,
  `norns.restore_started`, `norns.restore_completed`

### Dreamstate
- `dreamstate.started`, `dreamstate.completed`,
  `dreamstate.failed`

Roughly 50 event types. Each documented. Each consumed by
at least one subscriber.

---

## How operators consume observability

Three personas, three preferred surfaces:

### Iðunn (newcomer)

Stofa StatusBar dots. Doctor screen on demand. Errors
have actionable hints.

Doesn't need to know what "Verdandi" is.

### Volmarr (sovereign-operator)

The Doctor screen + the audit log + `ember yggdrasil
events tail` for live debugging. Can dive deep when
something's wrong.

Knows what Verdandi is; uses it.

### External monitoring (operator-configured)

The Verdandi socket can be bridged to external observability
stacks (Prometheus, Grafana, ELK). Yggdrasil doesn't ship
the bridge in V1, but the socket is operator-accessible.

For Sigrún (power-user) + cluster operators.

---

## What we don't ship in V1

- **Distributed tracing** (OpenTelemetry). V2.
- **Pretty Grafana dashboards.** Operators build their own
  if they want.
- **Anomaly detection on event patterns.** V2+.
- **Pre-built integrations with major observability
  platforms.** Operators bridge themselves.

V1 ships the *primitives*. Higher-level integration is
operator/community work.

---

## Why observability isn't optional

Some software lets you turn observability off ("for
performance"). Yggdrasil doesn't.

Reasons:
1. **Self-healing depends on it.** Turning it off breaks
   recovery.
2. **Self-awareness depends on it.** Turning it off
   breaks "I notice…".
3. **The performance cost is small.** Event publication is
   ~microseconds; gossip beats are 30-second intervals.

What CAN be turned off:
- **Sampling rate** for high-frequency events.
- **Operator-facing surfacing** (don't show patterns in
  chat).
- **External bridge** (default off).

What CAN'T:
- The internal event bus itself.

---

## Observability and privacy

Yggdrasil events are **operator-local**. They never leave
the machine (unless the operator configures an external
bridge).

Event payloads carry **operational metadata**, not
**content**:
- A chat turn fires `chat.turn_started` — not the
  operator's message text.
- A retrieval fires `bifrost.fusion_completed` — not the
  retrieved chunks' content.
- A tool call fires `tool.executed` — the tool name + the
  audit-log reference, not the full payload.

For *deep introspection*, the audit log (per ADR-0011)
holds operator-owned full detail.

The split: **observability = operational; audit =
forensic + content**.

---

## Configuration shape (reminder)

```yaml
yggdrasil:
  observability:
    verdandi:
      enabled: true                # cannot be disabled in V1
      socket_path: /run/verdandi/sock
    sampling:
      funi.token_streamed: 0.1
    privacy:
      publish_operator_input: false
      publish_chat_reply: false
    external_bridge:
      enabled: false               # opt-in
      kind: prometheus_pushgateway
      url: ""
```

---

## Closing

Observability as First-Class makes Yggdrasil **a system
you can actually operate**. Self-healing works because the
system sees its own state. Operators trust it because they
can verify what it's doing. Bugs surface because nothing's
hidden.

This isn't observability-as-a-feature. It's observability-
as-architecture. The system *is* its event stream.
