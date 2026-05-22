# 02 — The Gateway Architecture

OpenClaw's central concept: the local-first Gateway as the single
control plane for sessions, channels, tools, and events.

---

## What the Gateway is

The OpenClaw README describes the system as a **"local-first
Gateway"** serving as "the single control plane for sessions,
channels, tools, and events."

In other words: one process running locally that handles:

1. **Sessions** — conversation state with operator(s).
2. **Channels** — the 23+ messaging integrations.
3. **Tools** — execution of agent-requested operations.
4. **Events** — the cross-component signaling system.

All four converge on the Gateway. Nothing bypasses it.

---

## Why this works

A naive AI assistant architecture might:
- Run a separate process per channel (one for Telegram, one for
  Slack, one for terminal…).
- Route tools directly to the LLM with minimal mediation.
- Persist sessions in a distributed datastore.

This works but has problems:
- **State fragmentation** — each process holds partial truth.
- **Coordination overhead** — cross-process IPC for every action.
- **Inconsistent policy** — auth/sandbox enforcement diverges.

The Gateway pattern collapses all of this into **one process** with
clear internal boundaries between sessions/channels/tools/events.
*Simpler to reason about. Easier to instrument. Auditable from one
place.*

---

## How it compares to Ember's Bifrǫst

Both are local-first single-control-plane patterns. But they're at
*different layers*:

| | OpenClaw Gateway | Ember Bifrǫst |
|---|---|---|
| **Layer** | Application logic | Memory backends |
| **Routes** | sessions/channels/tools/events | search/store/recall to backends |
| **Cardinality** | 1 per operator install | 1 per agent process |
| **Pluggability** | Channel adapters; tool adapters | Brunnr backends |

OpenClaw's Gateway is *higher-level* — it's the whole application
fabric. Ember's Bifrǫst is *narrower* — it's the memory fabric.

These don't conflict. Ember could *also* adopt a Gateway-style
pattern at the application layer (it's currently more fragmented
across chat.py + Munnr + planned Stofa).

---

## The "single control plane" idea

This phrase is doing real work:

> *Single* — one process, one source of truth.
> *Control* — it's where decisions happen (routing, auth, tools).
> *Plane* — a horizontal layer that everything else attaches to.

Compared to a microservices architecture (control distributed across
N services), the Gateway pattern is **monolithic by design** — but
*monolithic-with-clean-internal-boundaries*, not
*monolithic-as-spaghetti*.

This is a *modern* monolith. The kind that distributed-systems
engineers came back to after a decade of microservices fatigue.

---

## What gateways enable

Once everything routes through one place:

### 1. Uniform observability

Every action — chat turn, tool call, channel event — passes
through the Gateway. Logging, metrics, audit all centralize.

In OpenClaw: their `/status`, `/usage`, audit log etc. all draw
from the Gateway's view.

Ember equivalent: Verdandi event bus + audit log + Doctor screen.
We have the pattern; we should keep extending it.

### 2. Consistent policy enforcement

If the Gateway is the only place tool execution happens, the
sandbox policy applies *every time*. No path around it.

In OpenClaw: `agents.defaults.sandbox.mode` applies uniformly.

Ember equivalent: the Heimdall Pattern from Yggdrasil (see
[`../../yggdrasil/invented-methods/71_HEIMDALL_PATTERN.md`](../../yggdrasil/invented-methods/71_HEIMDALL_PATTERN.md))
plays the same role at the cross-realm level.

### 3. Channel-agnostic agent logic

The agent doesn't know if input came from terminal or WhatsApp or
voice. The Gateway normalizes input format; agent logic stays
clean.

Ember equivalent: chat.py processes turns regardless of input
surface. We could formalize this more (currently Munnr is the only
real input surface).

### 4. Cross-channel session coordination

Operator chats from terminal in the morning; from phone at lunch.
The Gateway routes both to the same session (or routing rules
decide which agent each channel goes to).

Ember equivalent: Episodes persist in the Well; any surface can
resume. We have the bones; OpenClaw has the polish.

---

## The Gateway as daemon

OpenClaw can run as a daemon:

```bash
openclaw --install-daemon
```

…on launchd (macOS) or systemd (Linux). The Gateway is always-on,
listening for channel events, ready to receive operator input from
any surface.

Ember currently doesn't run as a daemon — `ember chat` is invoked
ad-hoc. This is a *deliberate choice* for sovereignty (no
always-on process), but it has costs (no async messaging support,
no wake-word voice, no notification surfaces).

Yggdrasil Phase 4's federation requires a daemon-ish pattern. We're
on the path. OpenClaw is just further along.

---

## What the Gateway doesn't do

- **Doesn't process payloads.** The Gateway routes; agents process.
- **Doesn't store data long-term.** State persists to the operator's
  files; Gateway is the orchestrator, not the database.
- **Doesn't make LLM calls.** Agents call LLM; Gateway routes
  results.
- **Doesn't replace operator choice.** Operators configure routing
  rules; the Gateway honors them.

Like Heimdall, the Gateway is a *gate*, not a *brain*.

---

## Configuration shape (OpenClaw's)

The operator's `~/.openclaw/openclaw.json` is the Gateway config.
Typical contents (from README):

```json
{
  "model": {
    "provider": "anthropic",
    "model": "claude-opus-4"
  },
  "channels": {
    "telegram": { ... },
    "slack": { ... }
  },
  "agents": {
    "defaults": {
      "sandbox": { "mode": "non-main" }
    },
    "personal": { ... },
    "work": { ... }
  }
}
```

One file; whole-system config. Operators edit + restart daemon to
apply.

Ember equivalent: `ember.yaml` (per Six True Names). Same general
shape; different format (YAML vs JSON).

---

## What Ember should borrow

🟢 **Adapt to Ember Vows** — the Gateway concept itself.

We should formalize **a single application-layer gateway in Ember**
that orchestrates:

1. Munnr / Stofa / future-Auga input.
2. Chat-loop dispatch.
3. Tool framework + Heimdall mediation.
4. Verdandi event publication.
5. Yggdrasil realm coordination.

This already partially exists (chat.py is closest to the role); but
making it *explicit and named* would be valuable.

Working name proposal: **Hjarta as the Gateway**. The "heart" sits
at the center; everything flows through it.

Alternatively: **Munnr the mouth as gateway** is the wrong frame
(Munnr is just one input surface). Hjarta as central organ fits
better.

---

## What Ember should NOT borrow

🔴 **Reject** — JSON config + always-on daemon as defaults.

OpenClaw's daemon is on-by-default for power users. Ember's design
prefers ephemeral processes (start when needed, exit cleanly).

The Pi-class hardware target also matters: a Pi running an
always-on daemon eats more battery / SD card writes / power.
Ephemeral wins there.

For LARGE / WORKSTATION profiles, an opt-in daemon mode makes
sense (per Yggdrasil Phase 4 federation). For TINY / SMALL,
keep ephemeral as default.

---

## Closing

The Gateway architecture is **OpenClaw's structural genius**: one
control plane, clean internal boundaries, channels and tools and
sessions all flowing through one auditable point.

Ember already has pieces of this (Bifrǫst at the memory layer;
chat.py at the application layer). The Klóinn lesson: **make the
gateway explicit and central**. Don't let it stay implicit.
