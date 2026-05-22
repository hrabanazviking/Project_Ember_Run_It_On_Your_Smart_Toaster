# 60 — The Humarr Gateway

A new invented method: the Gateway pattern adapted to Ember's
Vows. Named **Humarr** — Old Norse-derived for "lobster" — to
acknowledge OpenClaw's inspiration.

---

## What Humarr is

A Gateway pattern adapted to Ember:

- **Local-first** — runs on operator's device.
- **Profile-aware** — TINY runs minimal Gateway; WORKSTATION
  runs full.
- **Ephemeral-or-daemon** — operator chooses.
- **Surface-pluggable** — Munnr, Stofa, Auga, web companion,
  bridges all plug in uniformly.
- **Audit-by-default** — every cross-surface event logged.

OpenClaw's Gateway *centralized* control. Humarr Gateway
*tiers* control by profile while keeping centralized
audit/observability.

---

## The Humarr architecture

```
                       ┌────────────────────────┐
                       │   Humarr Gateway        │
                       │                          │
              ┌───────►│  ┌────┐ ┌────┐ ┌────┐ │
              │        │  │Sess│ │Surf│ │Tool│ │
              │        │  └─┬──┘ └─┬──┘ └─┬──┘ │
              │        │    └──────┼──────┘    │
   surfaces ──┘        │           │           │
              │        │   ┌───────▼──────┐    │
              │        │   │ Heimdall      │    │
              │        │   │ (per Yggdrasil)│    │
              │        │   └───────┬──────┘    │
              │        │           │           │
              │        │       ┌───▼───┐       │
              │        │       │ Funi  │       │
              │        │       └───────┘       │
              │        └──────────────────────┘
   bridges ───┘                  │
                                  ▼
                         Verdandi event bus
```

Surfaces and bridges feed in. Humarr orchestrates. Heimdall
mediates cross-realm calls. Funi processes. Verdandi observes.

---

## What's new vs OpenClaw's Gateway

### 1. Profile-class awareness

```python
class HumarrGateway:
    def __init__(self, profile: DeviceProfile):
        self.profile = profile
        
        if profile.class_ == "TINY":
            self.lifecycle = "ephemeral"
            self.surfaces_enabled = ["munnr"]
            self.tools_pool_size = 0
        elif profile.class_ in ("LARGE", "WORKSTATION"):
            self.lifecycle = "daemon_or_ephemeral"  # operator chooses
            self.surfaces_enabled = ["munnr", "stofa", "web_companion"]
            self.tools_pool_size = 4
        # ...
```

Profile decides defaults. Operator overrides.

### 2. Heimdall integration

Per Yggdrasil's Heimdall Pattern: every cross-realm call goes
through Heimdall. Humarr Gateway delegates *cross-realm*
mediation to Heimdall.

Separation of concerns:
- Humarr Gateway: *application-layer* control plane.
- Heimdall: *cross-realm* gate.

They compose. Application calls Heimdall to invoke realms;
Heimdall enforces; both observe via Verdandi.

### 3. Surface as Protocol

Surfaces (Munnr / Stofa / Auga / web / bridges) all implement:

```python
class Surface(Protocol):
    NAME: ClassVar[str]
    
    async def start(self, gateway: HumarrGateway) -> None:
        """Attach to gateway."""
        ...
    
    async def stop(self) -> None:
        """Detach."""
        ...
    
    async def receive_event(self, event: GatewayEvent) -> None:
        """Receive event from gateway (e.g., 'token streamed')."""
        ...
```

Adding new surfaces: implement Protocol; register; plug in.
*No changes to Gateway core*.

### 4. Ephemeral or daemon

```bash
ember chat                    # ephemeral; Gateway starts; exits
ember daemon start            # daemon; Gateway persists
```

Daemon mode unlocks:
- Voice wake.
- Bridges.
- Companion app.
- Scheduled tasks (cron tool).

Ephemeral mode keeps:
- Lightest possible footprint.
- No always-on resource use.
- Simpler operator mental model.

---

## How Humarr handles many concurrent surfaces

In daemon mode, multiple surfaces may be active:
- Stofa terminal session.
- Web companion on phone.
- Telegram bridge.

Each represents an *operator-facing-context*. Humarr routes:

```python
async def handle_event(self, event: SurfaceEvent):
    # event has surface ID
    session = self.sessions.get_or_create(event.session_id)
    
    # Route through Heimdall for any external operations
    response = await self.process(session, event.payload)
    
    # Send back to originating surface
    await event.surface.receive_event(
        GatewayEvent(type="response", payload=response)
    )
```

Each surface gets its own session(s). Crossover happens only
when operator explicitly routes (e.g., resumes a session in a
different surface).

---

## Concurrency model

In ephemeral mode: single chat at a time. Simple.

In daemon mode: multiple concurrent chat-turns possible:
- Operator typing in Stofa.
- Telegram message arriving.
- Cron-scheduled summary firing.

Humarr serializes by *session*:
- Each session is single-threaded internally (one operation
  at a time).
- Different sessions can run in parallel.
- Funi is shared resource (one at a time across sessions).

asyncio for I/O concurrency; queue for Funi.

---

## Configuration shape

```yaml
ember:
  humarr:
    lifecycle: ephemeral           # or "daemon"
    
    surfaces:
      munnr: enabled
      stofa: enabled
      web_companion: disabled       # V5+
      bridges:
        matrix: disabled
        telegram: disabled
    
    daemon:
      pid_file: ~/.ember/state/humarr.pid
      log_file: ~/.ember/logs/humarr.log
      restart_on_crash: true
    
    concurrency:
      max_concurrent_sessions: 4
      funi_queue_size: 10
    
    observability:
      audit_all_gateway_events: true
```

---

## What Humarr gives operators

### Day-to-day (ephemeral)

```bash
ember chat                  # opens chat; Humarr starts; exits when done
```

Indistinguishable from current `ember chat`. Just *named*
internally.

### Power user (daemon)

```bash
ember daemon install         # systemd / launchd setup
ember daemon start
# Stofa, voice, bridges, web companion all available
```

Always-on Ember; multi-surface; multi-session.

### Operator visibility

```bash
ember humarr status

Humarr Gateway: daemon (running for 4h 23m)

Active surfaces:
  - stofa  (1 session active)
  - web_companion (2 sessions: phone + tablet)
  - bridge.telegram (1 session)

Recent events (last 5 min):
  14:23 - stofa session received message
  14:24 - web_companion replied with OdinUI form
  14:25 - telegram session: bot replied
  ...
```

Operator sees *what Humarr is doing* in real time.

---

## How this composes with Yggdrasil

| Yggdrasil concept | Humarr role |
|---|---|
| Realms (Mímir, Huginn, etc.) | Heimdall mediates; Humarr orchestrates above |
| Verdandi event bus | Humarr publishes; other realms subscribe |
| Bifrǫst (memory gateway) | Humarr calls via Heimdall |
| Kista (secrets) | Humarr accesses via SecretResolver |

Humarr is the **application-layer counterpart** to Bifrǫst's
memory-layer role. They compose; neither replaces the other.

---

## How this composes with Klóinn-other-patterns

| Klóinn pattern | Humarr integration |
|---|---|
| Multi-agent / personas | Humarr routes events to persona-specific sessions |
| Channel bridges | Bridges are surfaces; plug into Humarr |
| Voice (Rödd) | Rödd is a surface |
| Live Canvas | Surfaces render OdinUI; Humarr passes through |
| Sessions | Humarr's session manager owns them |

Humarr is *the integration point* for everything.

---

## What we're not doing

🔴 **Reject**:

### 1. Cluster Humarr

A single Humarr Gateway per operator install. No load
balancing. No active-active. Operator's machine is the
boundary.

For federation (per Yggdrasil): each node has its own
Humarr. They federate via Yggdrasil's federation layer, not
via Humarr clustering.

### 2. Cloud-deployed Humarr

Always local. Always sovereign.

### 3. Multi-tenant Humarr

One Humarr per operator. Multi-operator machines run
separate Humarr instances per operator.

---

## Implementation phasing

🟢 **Phase 1 of Klóinn adoption**: refactor existing chat.py
+ munnr/ into named Humarr Gateway module.

🟢 **Phase 2**: add Stofa as second surface.

🟢 **Phase 3**: surface protocol formalized; tools framework
integrates.

🟢 **Phase 4**: daemon mode + bridges + cron.

🟢 **Phase 5+**: web companion + voice + Auga.

Each phase ships *operator-visible* improvements. Humarr
gradually grows.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Single point of failure (Humarr crashes) | Auto-restart in daemon mode; ephemeral runs as needed |
| Performance bottleneck (many surfaces) | asyncio + session queuing; profile-class tiering |
| Operator confusion about lifecycle | Clear `ember humarr status` |
| Scope creep (Humarr does too much) | Heimdall/Bifrǫst handle their own layers; Humarr is *application* layer only |

---

## Closing

The Humarr Gateway is **Ember's adaptation of OpenClaw's
Gateway pattern**. Profile-aware; surface-pluggable;
ephemeral-or-daemon; composes with Yggdrasil.

The name acknowledges the lobster (Molty inspires the
pattern); the implementation honors Ember's Vows.

Phase 1 adoption: refactor existing code; rename module;
formalize Surface Protocol. Cheap. High value.

Phase 4+: daemon mode unlocks the full pattern.

This is the *most impactful single Klóinn adoption*. The
Gateway pattern is OpenClaw's structural genius; Humarr
brings it home to Ember.
