# 13 — Sibling: Verðandi

> *"VERÐANDI — The Norn of Becoming. She Who Weaves What Is
> Happening Now."*

Real-time event bus and AI nervous system. Unix Domain Socket
based. Framework-agnostic.

This is **arguably the most architecturally important sibling**
in Yggdrasil — the one that makes self-awareness possible.

---

## What it is

A standalone Python library + daemon that provides:

- **Real-time event bus** over Unix Domain Socket.
- **AI nervous system** for agent self-observation.
- **Self-awareness** primitives — agents can subscribe to
  their own published events.
- **Framework-agnostic** — works with any Python agent, not
  just Ember.

In cosmology, Verðandi is one of the three Norns: Urðr (past),
Verðandi (present), Skuld (future). She weaves the *present*
— what is becoming right now.

The library's name reflects its purpose: it captures *what is
happening now* in an agent's operation and makes it
observable + actionable.

---

## Why this sibling is the architectural keystone

Without Verðandi, Ember has *no self-awareness*. She processes
inputs, produces outputs, persists Episodes — but she has no
real-time *view of her own ongoing state*.

With Verðandi, Ember can:

- Know what she's doing right now ("I'm in a chat turn,
  about to retrieve.")
- Know what she did recently ("Last turn I cited 3 documents
  about Odin.")
- Notice patterns across turns ("This is the 5th Odin question
  this week.")
- Publish her own state for other tools to observe ("Stofa's
  status bar can subscribe and surface this.")

**Self-awareness without Verðandi** would require Ember to
build her own event log + subscription mechanism. Verðandi
already exists, is framework-agnostic, and is well-designed.
We integrate.

---

## How Yggdrasil integrates Verðandi

### Integration role

Yggdrasil Phase 3 wires **Ember as both a publisher and
subscriber** to Verðandi's event bus.

#### As publisher

Every internal Ember operation emits an event:

- `ember.chat.turn_started` (payload: operator_input,
  context_size)
- `ember.chat.retrieval_returned` (payload: hit_count,
  elapsed_ms)
- `ember.chat.tool_proposed` (payload: tool_name)
- `ember.chat.tool_approved` (payload: tool_name, approval_kind)
- `ember.chat.episode_persisted` (payload: episode_id)
- `ember.well.ingest_progress` (payload: doc_count)
- `ember.realm.health_change` (payload: realm_name,
  new_state)
- `ember.mcp.server_state` (payload: server_name, state)
- `ember.stofa.screen_change` (payload: from_screen,
  to_screen) — when Stofa lands

Roughly 20-30 event types. Each is a JSON message published
on the Verðandi socket.

#### As subscriber

Ember subscribes to her *own* events (for self-awareness)
plus events from other realms:

- Subscribes to `ember.*` to build her own short-term memory
  of operations.
- Subscribes to `mimir.*` for decay / reinforcement
  notifications.
- Subscribes to `bifrost.*` for backend-availability changes.
- (Future) subscribes to `astrology.*` for temporal-context
  changes (lunar phase, time of day).

### Adapter shape

A new `src/ember/yggdrasil/verdandi/` package:

- `client.py` — `VerdandiClient` that publishes to + subscribes
  from the Verðandi socket. Wraps async I/O.
- `events.py` — typed event schemas (TypedDict / Pydantic if
  Verðandi uses Pydantic).
- `awareness.py` — the self-awareness layer's API surface.
  See [`../ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../ai-capabilities/40_SELF_AWARENESS_LAYER.md).
- `bridge.py` — bridges Ember's internal `Message`-bus events
  (from Stofa's architecture) to Verðandi's external socket
  events.

### Configuration shape

```yaml
yggdrasil:
  verdandi:
    enabled: true
    socket_path: /run/verdandi/sock     # default
    publish_events: true                 # Ember publishes her own ops
    subscribe_to:
      - ember.*
      - mimir.*
      - bifrost.*
    awareness:
      enabled: true
      memory_window_seconds: 3600        # how far back self-awareness reaches
```

Operators can disable any axis (just publish, just subscribe,
or neither while still using Verðandi as monitoring).

---

## What self-awareness enables

Concrete operator-visible behaviors that *only* exist because
Verðandi is wired:

1. **"I notice…" remarks.** Ember can occasionally surface
   patterns: "I notice you've asked me about Odin 5 times
   this week. Want me to pin those documents?"
2. **State-aware error messages.** When something fails,
   Ember can say "I was in the middle of a tool call to
   `fetch_url` when this happened" instead of "an error
   occurred."
3. **Smarter retries.** Ember can avoid re-trying an
   approach she just tried 2 minutes ago.
4. **Stofa observability.** The status bar can show
   "Currently: retrieving from Mímir + Huginn" — sourced
   from Verðandi events, not Ember's chat-thread internals.
5. **Cross-instance gossip (Phase 4 multi-device).** Two
   Ember instances on different devices can share Verðandi
   events to know about each other.

---

## Risk / known issues

- **Verðandi daemon dependency.** Operators need a Verðandi
  daemon running for the bus to work. Yggdrasil ships a
  systemd unit + a Stofa fallback (Ember runs Verðandi in-
  process if the daemon isn't available).
- **Unix Domain Socket = no cross-machine** (without
  forwarding). For multi-device Yggdrasil Phase 4, we'll
  bridge Verðandi to a network protocol (likely WebSocket
  via the Bifröst HTTP gateway).
- **Self-awareness can be uncanny.** Operators reading "I
  notice you've been…" might feel surveilled. The behavior
  is *opt-in* and *tunable*.

---

## Open questions for Phase 3 ratification

1. **Event schema versioning.** Verðandi's schema might
   evolve; we need compatibility windows.
2. **High-frequency events (token streams).** Should each
   stream token be published, or only completion? Probably
   the latter; tokens are too noisy.
3. **What's the right granularity for "I notice…"
   surfacing?** Default off; operator opts in via Settings.

---

## Test strategy

Phase 3 ships:

- **Unit tests** for `VerdandiClient` with a mocked socket.
- **Integration tests** with a real Verðandi daemon running
  in a CI fixture.
- **Self-awareness behavior tests** — drive a sequence of
  chat turns, verify Ember's "I notice…" surfaces correctly
  at the configured threshold.

Tests in `tests/unit/test_yggdrasil_verdandi_client.py` and
`tests/integration/test_yggdrasil_verdandi_real.py`.

---

## Closing

Verðandi is the **nervous system**. Without her, Ember has
limbs but no proprioception. With her, Ember knows where her
own body is in space.

This is what makes a *companion AI* different from a *chat
endpoint*. Yggdrasil V1 ships it.
