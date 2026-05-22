# 30 — The Nine Realms Architecture

The technical shape of Yggdrasil. How Ember (Asgard) talks to
each realm; what the gateway looks like; what guarantees hold
across realms.

---

## The high-level architecture

```
                              ┌───────────────────┐
                              │      ASGARD       │
                              │   src/ember/      │
                              │  (the agent)      │
                              └─────────┬─────────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  │ all cross-realm calls flow through        │
                  │ the Yggdrasil layer at                    │
                  │ src/ember/yggdrasil/                      │
                  └─────────────────────┬─────────────────────┘
                                        │
        ┌───────────────────────────────┼─────────────────────────────────┐
        │                               │                                 │
   ┌────▼────┐                     ┌────▼────┐                       ┌────▼────┐
   │ BIFRǪST │                     │ NIFLHEIM│                       │ MUSPELL │
   │ Gateway │                     │  Kista  │                       │Astrology│
   │(memory) │                     │(secrets)│                       │ (time)  │
   └────┬────┘                     └─────────┘                       └─────────┘
        │
   ┌────┼─────┬──────────┐
   ▼    ▼     ▼          ▼
 Mímir Huginn Muninn  MemPalace
                                
                                
   ┌────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌─────────────┐
   │URÐAR   │  │VANAHEIM  │  │ÚTGARÐR     │  │ALFHEIM   │  │HELHEIM      │
   │Verðandi│  │ Seiðr    │  │CloakBrowser│  │ Hamr     │  │MemPalace    │
   │(events)│  │(verse)   │  │(web)       │  │(avatars) │  │(verbatim)   │
   └────────┘  └──────────┘  └────────────┘  └──────────┘  └─────────────┘
```

Each realm is an independent sibling project (or a Brunnr
sub-backend). Ember reaches each through the Yggdrasil
adapter layer.

---

## The Yggdrasil layer

`src/ember/yggdrasil/` is the *thin adapter package* that:

- Imports each sibling lazily.
- Wraps its API behind an Ember-side Protocol.
- Bridges sibling-specific exceptions to typed values.
- Coordinates cross-realm calls.
- Centralizes Kista-mediated secret resolution.
- Bridges Ember's internal Message bus to Verdandi.

It is **not a service**. It's a Python package of adapters.

### Layout

```
src/ember/yggdrasil/
├── __init__.py
├── runner.py                  # async/sync bridge (reusable, like MCPRunner)
├── kista/
│   └── client.py              # KistaClient + secret resolver bridge
├── bifrost/
│   └── adapter.py             # BifrostBrunnr (BrunnrHandle Protocol)
├── mimir/
│   └── adapter.py             # MimirBrunnr (BrunnrHandle Protocol)
├── mempalace/
│   └── adapter.py             # MemPalaceBrunnr (BrunnrHandle Protocol)
├── verdandi/
│   ├── client.py              # VerdandiClient (pub/sub over UDS)
│   ├── events.py              # event schemas
│   ├── awareness.py           # self-awareness layer
│   └── bridge.py              # internal Message ↔ external event
├── rhythm/                    # Astrology Engine wrapper
│   ├── client.py
│   └── rhythm.py              # current-rhythm state
├── seidr/                     # Seiðr wrapper
│   ├── client.py
│   └── mood_channel.py
├── hamr/                      # Hamr wrapper (Phase 4)
│   └── client.py
└── norse_dict/
    └── ingest.py              # one-shot dictionary ingest helper
```

Roughly 30 new Python files in total across all phases.

---

## The realm protocols

Each realm implements (or wraps) an Ember-side Protocol so
Ember's main code paths don't care whether a realm is
present:

| Realm | Protocol implemented |
|---|---|
| Bifrǫst / Mímir / MemPalace | `BrunnrHandle` (existing, ADR-0010) |
| Kista | `SecretResolver` (new — generalizes pgvector's chain) |
| Verðandi | `EventBus` (new) + `AwarenessSource` (new) |
| Seiðr | `MoodChannel` (new) — invokable for register-shaping |
| Astrology / Rhythm | `RhythmSource` (new) — emits temporal context |
| CloakBrowser | `ToolExecutor` (existing tool framework, ADR-0011) |
| Hamr | `AvatarSource` (new, Phase 4) |
| norse-dict | `IngestSource` (new — generalizes Smiðja's pattern) |

**New protocols are added; existing ones are reused.** This
preserves the architecture's clarity.

---

## How a chat turn flows through Yggdrasil

Compare a chat turn before/after Yggdrasil.

### Before (today)

```
operator input
  → BrunnrHandle.search() (one backend)
  → prompt assembly
  → FuniHandle.stream()
  → tool loop (if any)
  → episode persistence
```

### After (Yggdrasil Phase 3)

```
operator input
  → RhythmSource.current_rhythm() (lightweight cached)
  → AwarenessSource.recent_state() (Verdandi-fed)
  → MoodChannel.detect(input, recent_state) → register
  → BrunnrHandle.search() ← composed via Bifrǫst → Mímir + Huginn + Muninn
  → prompt assembly (includes register + recent-state hint)
  → FuniHandle.stream() (with tone-aware system prompt)
  → tool loop (incl. CloakBrowser escalation if needed; all secrets via Kista)
  → MoodChannel.maybe_seed_seidr(register) (optional verse seed)
  → episode persistence (writes via Bifrǫst to all sub-backends)
  → EventBus.publish("ember.chat.turn_finished", ...) (Verdandi)
```

The flow gains **5 new touchpoints** (rhythm, awareness,
mood, optional seidr, event publish), but each is *fast*
(milliseconds) and *operator-toggleable*. A Pi-class operator
who disables Rhythm + Awareness + Mood gets the original
flow with the upgraded Bifrǫst memory.

---

## Cross-realm contracts

Three contracts hold across every realm:

### 1. Typed-value over exception

Per ADR-0007 §2.2 (existing Ember invariant), no realm raises
across the Yggdrasil boundary. Failures return typed values:

- `Disconnected(realm, reason, detail)` for unreachable realms.
- `Unavailable(realm, reason)` for missing optional realms.
- `RealmError(message)` for in-flight failures.

The chat loop continues; the affected capability degrades to
"realm offline."

### 2. Lazy import, opt-in via pip extras

Every realm import is lazy. Ember without the realm's pip
extra installed sees:

```
yggdrasil.kista not installed: pip install ember-agent[kista]
```

Friendly message, not ImportError traceback.

### 3. Kista mediation for ALL secrets

After Phase 2, no realm uses plaintext credentials. Every
realm requests secrets through Kista. The Yggdrasil-secrets
resolver chain handles fallback for non-Kista operators (env
vars, keyring, file).

---

## How Verdandi observes everything

The event bus is the *cross-cutting observability layer*:

```
       ┌──────────────┐
       │   Verðandi   │
       │  (event bus) │
       └──────▲───────┘
              │
   ┌──────────┼──────────┬──────────┬─────────┐
   │          │          │          │         │
Ember      Bifrǫst     Mímir    Kista    Astrology
publishes  publishes   publishes publishes publishes
chat       memory      decay    secret-   rhythm-
events     events      events   access    change
                                events    events
```

Every realm that emits events publishes to Verdandi.
Subscribers (including Ember herself for self-awareness)
listen.

This is *passive observability* — nothing requires another
realm to read its events. But it makes the system *legible*
to any observer (the Stofa StatusBar, a future Auga, a
sysadmin's separate observability tool).

---

## How realms can fail independently

Per the Vow of the Unbroken Whole:

- **Mímir down**: chat continues with Brunnr-disconnected
  banner.
- **Huginn (Qdrant) down**: Bifrǫst skips vector search;
  Mímir-only retrieval; banner.
- **Kista down**: if Ember booted with secrets cached, she
  continues; if not, she enters limited-functionality mode
  (skip realms requiring secrets).
- **Verdandi daemon down**: self-awareness layer reports
  "unavailable"; chat continues with no "I notice…" remarks.
- **Astrology down**: rhythm-aware behaviors revert to
  defaults.
- **Seiðr down**: mood-channel skips verse-seeding.
- **CloakBrowser missing**: escalation tool simply isn't
  proposed; fetch_url remains the only web tool.
- **MemPalace down** (if used): same as any Brunnr backend
  going down — banner + skip.

**No realm's failure cascades to others.** This is the
Brunnr disconnect pattern, generalized.

---

## How the operator interacts with the architecture

The operator never sees `src/ember/yggdrasil/` directly.
They interact with:

- `ember.yaml` (`yggdrasil:` section for opt-ins).
- The Stofa Settings screen (visual config).
- The Stofa MCP screen (for any MCP-bridged realm tools).
- The Doctor screen (which now shows the state of every
  Yggdrasil-enabled realm).
- Chat (which becomes *better* without the operator having
  to think about why).

The architecture is **invisible by intent**. Operators feel
the *effect* (better memory, mood-aware tone, self-aware
remarks) without needing to know which realm produced what.

---

## Closing

The Nine Realms Architecture is a *thin adapter layer* that
respects each sibling's sovereignty while making them
collaborate. Same Vows as Ember itself: pluggable, opt-in,
typed-value-over-exception, sovereign-by-default.

Yggdrasil's depth is in the *integration*, not in new
abstractions. The architecture's elegance is that it didn't
require Ember to change its bones — it just gave the bones
more friends.
