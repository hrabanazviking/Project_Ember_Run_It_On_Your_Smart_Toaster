# 10 — Local-First Gateway

The pattern: one local process as single control plane. Extracted
from OpenClaw, examined for Ember adoption.

---

## The pattern in one sentence

**A long-running, local-only process that is the sole entry point
for all operator-facing operations**, with clean internal
boundaries between subsystems (sessions, channels, tools, events).

---

## Why it works

### Avoidance of distributed-systems problems

Without a gateway: state lives in multiple places (chat client,
notification daemon, scheduler, etc.). Each needs to talk to
others. Each can fail independently. Sync requires consensus
protocols.

With a gateway: one place holds state. One process to start, stop,
debug, instrument. Operator restarts *one thing* to apply config
changes.

### Uniform policy enforcement

Every operation passes through the gateway. Auth, sandbox, audit
all apply consistently. Operators *trust* the gateway because
it's *one auditable point*.

### Observability

The gateway publishes events for every operation. Log + audit +
metrics all derive from one stream. No correlation across
distributed sub-systems.

### Latency

Local IPC is fast (UDS / shared memory). Cross-process call =
sub-millisecond. Cross-host call = ms-to-tens-of-ms.

A local gateway has *cross-process latency only when bridging to
external services* (channel APIs, MCP servers, etc.).

---

## The pattern in detail

```
                          ┌─────────────────────────────┐
                          │      Local Gateway          │
                          │                              │
                          │  ┌────┐ ┌────┐ ┌────┐ ┌────┐│
operator input →          │  │Sess│ │Chan│ │Tool│ │Evnt││
   (any surface)          │  └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘│
                          │    │      │      │      │   │
                          │    └──────┴──────┴──────┘   │
                          │              │              │
                          │         ┌────▼────┐         │
                          │         │ Agent   │         │
                          │         │ Logic   │         │
                          │         └────┬────┘         │
                          │              │              │
                          │      LLM, Brunnr, etc.      │
                          └─────────────────────────────┘
```

The boundary between "operator surfaces" and "agent logic" is
*explicit* — agent logic doesn't know which surface invoked it.

---

## Variants

### Variant 1: ephemeral gateway

The gateway starts when the operator opens the app, exits when
they close it. State persists to disk between sessions.

Pros: no always-on process; minimal resource use; battery-friendly.
Cons: no async features (cron, notifications, voice wake).

### Variant 2: daemon gateway

The gateway runs as a system service (launchd/systemd) and stays
up. Channels can deliver events anytime. Voice wake works.

Pros: full feature set.
Cons: always-on resource use; complicates operator-control.

### Variant 3: hybrid

Daemon for channel-active sessions; ephemeral for terminal-only.
Operator chooses per-use.

OpenClaw is closer to *daemon-by-default* with ephemeral as
fallback. Ember today is *ephemeral-only*. Hybrid is a
reasonable evolution.

---

## Where the gateway pattern doesn't fit

### Pi Zero hardware

A daemon takes RAM continuously. On 512MB Pi Zero, that's a
significant fraction of budget. The pattern still applies, but
the daemon must be *very small*.

For TINY profile: lazy-start the gateway components; idle them
when not in use.

### Privacy-maximalist operators

Some operators *don't want* anything running when they're not
actively using Ember. The pattern accommodates this: gateway
can be ephemeral.

### Multi-user

If multiple humans share one machine (rare in our cohort, but
possible), each needs their own gateway instance. The pattern
scales by *running one gateway per operator*.

---

## How Ember can adopt

🟢 **Adapt to Ember Vows.**

Ember already has *most* of a gateway in `src/ember/spark/munnr/`
+ `src/ember/spark/chat.py`. They coordinate sessions, tools,
events. They route to the agent.

What's missing:
1. Named as "the Gateway."
2. Other surfaces (Stofa, future-Auga) routing through it.
3. Daemon-mode option for V4+.

Proposed name: **Hjarta as the Gateway**. The "heart" sits at
the center of Ember. All surfaces beat through it.

Or, alternatively: **Munnr as the Gateway** (Munnr is "mouth" —
the surface) — but that conflates surface with control plane.
Hjarta is better.

Or actually — **call the gateway concept by its English name in
docs, and let the *implementation* live in `src/ember/spark/`**.
Don't force a Norse-coded name for every architectural pattern;
some concepts are pan-cultural enough that English suffices.

---

## What changes in the Ember codebase

Today: chat.py + munnr/ form an implicit gateway.

Tomorrow (Phase 1 of Klóinn adoption):

1. Extract a `src/ember/spark/gateway/` module.
2. Move chat.py's central orchestration there.
3. Define the *internal boundaries*:
   - `gateway.sessions` — session lifecycle.
   - `gateway.surfaces` — Munnr, Stofa, etc. plug in here.
   - `gateway.tools` — tool registry + execution (already
     exists in tools/).
   - `gateway.events` — Verdandi publisher + subscribers.
4. Keep ephemeral as default; add daemon mode as opt-in.

This is *refactoring more than re-architecting*. The shape is
already there; we're just making it *named* and *clean*.

---

## Configuration shape

```yaml
ember:
  gateway:
    mode: ephemeral         # or "daemon" (V4+)
    daemon:
      systemd_unit: ember.service     # auto-installed
      launchd_label: com.ember.gateway
      pid_file: ~/.ember/state/gateway.pid
    surfaces:
      munnr: enabled
      stofa: enabled
      auga: planned        # V5
      bridges: false       # V4+
```

---

## Observability

Verdandi events:
- `gateway.started`, `gateway.stopped`.
- `gateway.surface_attached`, `gateway.surface_detached`.
- `gateway.session_started`, `gateway.session_finished`.

Doctor row shows current surface count + active sessions.

---

## Lesson summarized

OpenClaw shows the **Gateway pattern can scale to mainstream
adoption**. Ember has the pattern implicitly. Making it *explicit*
gives us:

1. A clear refactoring target for V2+.
2. A surface-level abstraction that Stofa, Auga, bridges all
   plug into uniformly.
3. Daemon-mode capability for V4+ federation.

Cost: a refactor. Benefit: cleaner architecture and clearer
future extensibility.

This is one of the highest-value Klóinn adoptions.
