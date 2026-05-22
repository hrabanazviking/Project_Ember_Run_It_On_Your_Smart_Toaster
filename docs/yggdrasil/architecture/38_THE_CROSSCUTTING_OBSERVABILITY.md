# 38 — The Crosscutting Observability Layer

How everything in Yggdrasil becomes *visible* — to the
operator, to Ember (for self-awareness), and to external
monitoring tools.

---

## Three observability surfaces

Yggdrasil exposes observability through three planes:

### 1. Verdandi (the event bus)

Real-time event stream over Unix Domain Socket. Every realm
publishes; subscribers consume. Per
[`13_SIBLING_VERDANDI.md`](../siblings/13_SIBLING_VERDANDI.md).

### 2. Structured logging (the existing `ember.logging` system)

Per Batch J's `ember/logging.py`. Each realm emits structured
logs at appropriate levels. Operator configures destinations
+ format in `ember.yaml`.

### 3. Doctor (the on-demand health view)

Stofa's DoctorScreen + the `ember doctor` CLI surface
realm-by-realm health. Reads from Verdandi event ring +
direct realm probes.

These three together cover **all** Yggdrasil observability
needs: real-time (Verdandi), persistent record (logs),
on-demand snapshot (Doctor).

---

## What gets observed

Every operation in every realm emits at least one event:

| Event class | Examples | Verdandi channel | Log level |
|---|---|---|---|
| Lifecycle | realm started, realm stopped, realm health change | `realm.*` | INFO |
| Memory | chunk stored, decay applied, contradiction detected | `mimir.*`, `huginn.*`, `muninn.*` | INFO |
| Retrieval | search started/completed, results fused | `bifrost.*` | DEBUG |
| Tool calls | tool proposed, approved, executed, audited | `tool.*` | INFO |
| MCP | server connected, ping, disconnect | `mcp.*` | INFO |
| Secrets | secret resolved (NOT the value), Kista unlock | `secret.*` | INFO |
| Chat | turn started/finished, stream tokens (sampled) | `chat.*` | DEBUG/INFO |
| Rhythm | phase change, eclipse event | `rhythm.*` | INFO |
| Mood | mood detected, seed used | `mood.*` | DEBUG |
| Awareness | "I notice…" trigger, pattern detected | `awareness.*` | INFO |
| Federation | (Phase 4) device join/leave, state sync | `federation.*` | INFO |

This is the **catalog of events** every realm respects.
Implementing the contract = publishing the right events.

---

## How a single chat turn looks in events

A complete chat turn produces ~30 events (approximate):

```
14:32:18.001 chat.turn_started        {operator_input_len: 42}
14:32:18.020 awareness.summary_built  {window_s: 3600, turn_count: 7}
14:32:18.025 rhythm.sampled            {time_of_day: evening, phase: waxing_gibbous}
14:32:18.030 mood.detected             {mood: INTROSPECTIVE, confidence: 0.7}
14:32:18.045 secret.resolved           {key: 'ember/funi/ollama_token', source: kista}
14:32:18.050 bifrost.search_started   {query_hash: abc123, backends: 4}
14:32:18.070 mimir.recall              {results: 5, elapsed_ms: 12}
14:32:18.080 huginn.recall              {results: 8, elapsed_ms: 18}
14:32:18.085 muninn.recall              {results: 3, elapsed_ms: 4}
14:32:18.090 bifrost.fusion_completed  {input_count: 16, output_count: 12}
14:32:18.100 chat.context_assembled    {token_count: 1840}
14:32:18.105 mood.seeded                {form: fornyrðislag, world: asgard}
14:32:18.150 funi.request_started       {model: llama3.2:3b}
14:32:18.250 funi.token_streamed        {count: 32}    (sampled)
14:32:18.380 funi.token_streamed        {count: 87}    (sampled)
14:32:18.520 funi.request_finished      {total_tokens: 142, elapsed_ms: 370}
14:32:18.525 chat.episode_persisted    {episode_id: 1289}
14:32:18.530 bifrost.episode_stored    {backend_count: 4}
14:32:18.535 muninn.associations_updated {count: 14}
14:32:18.540 chat.turn_finished        {elapsed_ms: 539}
```

This is a *trace* — operators / developers / Ember herself
can read it to understand exactly what happened.

---

## How the operator views events

Three views:

### 1. Stofa's debug overlay (V2)

The Ctrl-Shift-D debug overlay shows recent events live.
Useful for debugging "why is chat slow?" — see which event
took the longest.

### 2. CLI export

```bash
ember yggdrasil events tail                 # live tail
ember yggdrasil events export --since 1h    # last hour
ember yggdrasil events query 'chat.*' --last 24h    # filter
```

### 3. External observability tools

The Verdandi socket is operator-accessible. Operators with
external monitoring (Prometheus, Grafana, etc.) can write a
bridge that publishes events to their stack.

We don't ship a Prometheus bridge in V1. We ship the *socket
contract* so operators can build one.

---

## How Ember uses events (self-awareness)

The awareness layer subscribes to specific event patterns:

```python
class AwarenessLayer:
    def on_chat_turn_finished(self, event):
        self.recent_turns.append(event)
        if len(self.recent_turns) >= 5:
            self.detect_patterns()
    
    def detect_patterns(self):
        # E.g., "operator has asked about Odin 5 times in 3 days"
        topics = self._extract_topics(self.recent_turns)
        if any(count >= 5 for count in topics.values()):
            self.flag_topic_emerging(...)
```

This is *passive listening* — Ember's chat loop doesn't
have to explicitly notify the awareness layer. The layer
reads the bus.

---

## Sampling for high-volume events

Some events fire at high rates:
- `funi.token_streamed` — many per chat turn
- `mimir.access` — many per query

We *sample* these (publish 1 in N) to keep the bus
tractable. Operators tune sampling:

```yaml
yggdrasil:
  observability:
    sampling:
      funi.token_streamed: 0.1      # 10% sampled
      mimir.access: 0.05            # 5%
      chat.turn_finished: 1.0       # always
```

The chat-loop's *aggregated* events (`turn_started`,
`turn_finished`) capture total counts; sampling only affects
*individual instance* publication.

---

## Privacy + observability

Observability is the operator's. We never:

- Publish operator inputs as event payloads.
- Publish chat-reply text as event payloads.
- Publish secret values (only the *key* resolved).
- Publish document contents (only chunk IDs).

Events carry **metadata about operations**, not **the
operations' content**. An attacker reading the Verdandi
socket sees "Ember answered a chat turn that took 540ms with
12 retrieval hits" — not "Ember answered a question about X."

For deeper introspection (operator's own debug), the *audit
log* (per ADR-0011) captures full tool-call detail. That's
operator-owned + encrypted at rest if Kista is configured.

---

## How realms emit events efficiently

Each realm imports the Verdandi client lazily and uses a
"fire and forget" pattern:

```python
try:
    yggdrasil_event_bus.publish("mimir.decay_applied", {"count": 142})
except Exception:
    pass  # bus failure must never break the realm's operation
```

Event publishing is *additive*. It never affects the realm's
correctness. If the bus is down, the realm logs the event to
its own log channel as fallback.

---

## What about distributed tracing?

We don't ship OpenTelemetry in V1. The Verdandi event bus
+ structured logs cover ~80% of distributed-tracing needs
for a single-operator system.

V2+ may add OpenTelemetry bridges for operators who want to
plug Yggdrasil into a wider observability stack. The hooks
exist; the bridge code doesn't.

---

## Configuration shape

```yaml
yggdrasil:
  observability:
    verdandi:
      enabled: true
      socket_path: /run/verdandi/sock
      buffer_size: 10000        # ring buffer for replay
    sampling:
      funi.token_streamed: 0.1
      mimir.access: 0.05
      huginn.access: 0.05
      muninn.access: 0.1
    privacy:
      publish_operator_input: false      # never
      publish_chat_reply: false           # never
      publish_secret_values: false        # never
      publish_document_chunk_ids: true    # ids are safe to publish
    export:
      enable_cli: true
      enable_external_bridge: false       # opt-in for Prometheus etc.
```

---

## Closing

Crosscutting observability makes Yggdrasil **legible**.
Operators can see what's happening. Ember can know her own
state. External tools can plug in. The system isn't a black
box.

This is what enables self-healing (next section): without
visibility, recovery is guesswork. With it, recovery is
*the system noticing what broke and fixing it*.
