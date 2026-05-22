# 63 — The Tide Routing

A new method for *adaptive routing* between Ember's surfaces
+ federated nodes — informed by OpenClaw's multi-channel
orchestration. Named after tides (the lobster's medium).

---

## What it routes

Tide Routing handles: which *surface* should respond to which
*event* given current *context*.

Events come from:
- Munnr (terminal).
- Stofa (TUI).
- Web companion (browser).
- Bridges (Matrix, Telegram).
- Voice (Rödd).
- Federation peers.

Each event needs:
- A *session* assigned.
- A *persona* applied.
- A *node* (in federation; usually local).
- A *response surface* (where reply goes).

---

## Why this is hard

OpenClaw's routing is rule-based:
- "Telegram → personal agent."
- "Slack → work agent."

Static. Easy. Sufficient for OpenClaw's scope.

Ember's complexity:
- Different profiles per node (TINY can't run LLM).
- Some events need particular hardware (voice on Pi → STT on Pi).
- Operator preferences vary over time.
- Federated nodes come and go.

Static rules become brittle. Tide Routing is *adaptive*.

---

## How Tide works

For each incoming event:

1. **Identify context**:
   - Source surface.
   - Operator location (if known).
   - Time-of-day.
   - Current device load (federation-wide).
   - Operator's recent activity pattern.

2. **Consult rules**: operator's static rules (per Klóinn).

3. **Apply heuristics**: when rules ambiguous, heuristics
   pick:
   - "Bridges sandbox by default."
   - "Voice runs locally (latency)."
   - "Heavy LLM offload to GPU node when available."

4. **Route**: dispatch event to chosen target.

5. **Observe**: log decision via Verdandi for meta-learning.

---

## Example routing decisions

### Voice input on Pi 5 with federation

```
Event: voice utterance from Rödd
Context:
  - Source: rodd_on_pi5
  - Current LLM: workstation.tailnet (24GB GPU)
  - Pi 5 STT can process locally
  - Network: tailnet reachable

Decision:
  - STT: on Pi 5 (low latency).
  - Funi: route to workstation.tailnet.
  - TTS: on Pi 5 (low latency).
  
Rationale: STT/TTS are latency-critical (local).
LLM is GPU-critical (offload). Best of both.
```

### Telegram message during high local load

```
Event: telegram message from authorized user
Context:
  - Source: bridge.telegram
  - Local Ember busy processing previous turn
  - Federation has idle node

Decision:
  - Defer to idle federated node.
  - Local node continues current turn.
  
Rationale: don't drop quality; route to available capacity.
```

### Munnr request when offline

```
Event: terminal input from munnr
Context:
  - Source: munnr_local
  - Federation unreachable (network down)
  - Local has small LLM

Decision:
  - Process locally with degraded LLM.
  - Acknowledge degraded mode to operator.
  
Rationale: graceful offline (Vow honored).
```

---

## The routing decision graph

```
Event arrives
   ↓
Identify source + persona
   ↓
Static rule match? → Yes: apply, route.
   ↓ No
Apply heuristics:
  - Latency-critical? Local.
  - GPU-heavy? Federated GPU node.
  - Channel-bridged? Sandbox + sandbox-allowed surfaces.
  - Operator-presence-known? Route to where operator is.
   ↓
Resource available at chosen target?
   ↓ No: try next-best.
   ↓ Yes
Route + log decision
```

---

## The routing config

```yaml
ember:
  tide:
    enabled: true                   # required for daemon mode
    
    static_rules:
      - source: bridge.telegram
        persona: personal
      - source: bridge.matrix
        persona: main
      - source: voice
        latency_priority: true
    
    heuristics:
      latency_critical_sources: [voice, web_companion_immediate]
      gpu_offload_when_available: true
      sandbox_bridged_channels: true
      respect_operator_presence: true
    
    federation_routing:
      prefer_gpu_for_llm: true
      prefer_idle_node: true
      fallback_to_local: true
    
    observability:
      log_every_routing_decision: true
      surface_unusual_routing: true
```

---

## Operator visibility

Doctor screen:

```
Tide Routing (last 5 min):

  Events: 8
  Routed:
    - 4 → local (Munnr, Stofa)
    - 2 → workstation.tailnet (heavy LLM)
    - 1 → laptop.tailnet (voice)
    - 1 → defaulted local (federation unreachable briefly)
  
  Most common pattern: voice → local STT/TTS + GPU LLM elsewhere.
```

Operator sees *how Tide is deciding*. Adjust if wrong.

---

## Per-event override

Operator can override Tide for specific events:

```bash
ember route voice --target=local-only         # don't offload
ember route bridges --target=federation       # always remote
```

Tide respects overrides; reports them as such.

---

## Meta-learning Tide

Tide's decisions are logged. Mirror of Ginnungagap (per
Yggdrasil) can observe patterns:

> "I've noticed your voice latency averages 5s when routed to
> workstation, but 3.2s when routed to Pi 5 (where you sit).
> Want me to prefer Pi 5 for voice processing?"

Operator-suggested adjustments to Tide rules over time.

---

## When Tide isn't needed

For ephemeral single-node Ember: no Tide. Just process locally.

Tide activates when:
- Federation is configured.
- Multiple surfaces are enabled.
- Daemon mode is on.

Below that: simple routing suffices.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Routing bug breaks chat | Fallback to local-everything |
| Routing decisions confuse operator | Doctor + audit log |
| Federation latency hurts UX | Per-event latency budget |
| Operator can't predict routing | Override commands; static rules first |

---

## Composition with other Yggdrasil methods

| Method | Tide interaction |
|---|---|
| Rhythmic Computation | Heavy ops queued during lulls |
| Humarr Gateway | Tide makes routing decisions; Humarr executes |
| Federation | Tide chooses among federated nodes |
| Heimdall | Heimdall enforces; Tide chooses where |

Tide is *the higher-level decision layer*. Heimdall is *the
gate*. Together: routed-then-mediated.

---

## V4+ ship plan

🟢 **Phase 4 of Klóinn adoption** — Tide ships with federation.

Without federation: single-node; no routing needed.
With federation: Tide is the *coordinator* between nodes.

Phase 4 builds:
- Static rule evaluation.
- Basic heuristics.
- Doctor visibility.

Phase 5+ refinements:
- More heuristics.
- Meta-learning integration.
- Operator-suggested adjustments.

---

## Closing

The Tide Routing is **Ember's adaptive routing layer** —
informed by OpenClaw's static channel routing but extended
with heuristics, federation-awareness, and operator-pattern
learning.

Named for tides — flexible, contextual, always flowing toward
the right shore.

V4+ feature. Pairs with federation. Composes cleanly with
Humarr Gateway, Heimdall, and Yggdrasil's other layers.

This is the **Klóinn-original** method — borrowing OpenClaw's
need but extending it with Ember's complexity. New invented
method for the codex.
