# ARCHITECTURE — The Shape of Runa

**Voice:** Architect (Rúnhild Svartdóttir)
**Status:** Bootstrap-stage. The diagram below is the load-bearing shape; the code in `src/runa/` will be measured against it as it grows.
**Last touched:** 2026-05-17 (P7)
**Reads with:** `docs/SYSTEM_VISION.md` (intent), `docs/architecture/DOMAIN_MAP.md` (per-subpackage ownership), `docs/architecture/DATA_FLOW.md` (request and event lifecycle, written in P8).

---

## 1. The shape in one diagram

```
                ┌────────────────────────────────────────────────────────┐
                │                  Face of the World                      │
                │                                                         │
                │   Munnr (CLI)    Auga (GUI)    Rödd (voice)   Bifröst   │
                │   src/runa/      src/runa/     src/runa/      gateway   │
                │   apps/cli       apps/gui      apps/voice     src/runa/ │
                │                                                apps/    │
                │                                                gateway  │
                └──────────────┬─────────────────────────────┬────────────┘
                               │  external transports        │
                ┌──────────────▼─────────────────────────────▼────────────┐
                │                     Adapters                            │
                │   Discord  Telegram  Matrix  webchat  email  HA  MCP   │
                │   OpenRouter  Nous  Ollama  LM Studio  home-server     │
                │                  src/runa/adapters/*                    │
                └──────────────┬─────────────────────────────┬────────────┘
                               │ messages in/out             │ model calls
                ┌──────────────▼─────────────────────────────▼────────────┐
                │                    Service shells                       │
                │      gateway_service  worker_service  voice_service     │
                │                   src/runa/services/                    │
                └──────────────────────────┬──────────────────────────────┘
                                           │ lifecycle calls
                ┌──────────────────────────▼──────────────────────────────┐
                │                       runtime/                          │
                │      start/stop/status/doctor/logs/snapshot/restore     │
                └──────────────────────────┬──────────────────────────────┘
                                           │ control
                ┌──────────────────────────▼──────────────────────────────┐
                │                     Mind and Rules                      │
                │                                                         │
                │                    ┌────────────────┐                   │
                │   skills/  ───────►│  Kernel        │◄────── plugins/   │
                │                    │  core/kernel/  │                   │
                │                    └───────┬────────┘                   │
                │                            │                            │
                │                            ▼                            │
                │                   ┌────────────────┐                    │
                │                   │  VERÐANDI      │                    │
                │                   │  event bus     │                    │
                │                   │  core/eventbus │                    │
                │                   └─────┬────┬─────┘                    │
                │                         │    │                          │
                │       ┌─────────┬───────┘    └──────┬─────────┐         │
                │       ▼         ▼                   ▼         ▼         │
                │   Hirð       Smiðja              Heimskringla  Eir      │
                │   subagent   tool forge          model router  repair   │
                │   hall       core/tools/         core/models/  core/    │
                │   core/                                        repair/  │
                │   subagents/                                            │
                └─────────────────────────┬───────────────────────────────┘
                                          │ writes/reads
                ┌─────────────────────────▼───────────────────────────────┐
                │                     Deep Memory                         │
                │                                                         │
                │   Muninn         Skuld         WYRD bridge    Eldhugi   │
                │   core/memory/   core/tasks/   core/world/    core/     │
                │                                               emotions/ │
                │                                                         │
                │   identity store  ─ core/identity/                      │
                │   policy store    ─ core/policy/                        │
                │   audit log       ─ core/logging/                       │
                │                                                         │
                │   On-disk roots:  ~/.runa/{memory,tasks,world,          │
                │                          emotions,identity,policy,      │
                │                          logs,secrets,cache,state}/     │
                └─────────────────────────────────────────────────────────┘
                                          │ migrations
                                          │ src/runa/migrations/
                                          ▼
                                  ~/.runa/state/version
```

The three realms named in `SYSTEM_VISION.md` (Face of the World, Mind and Rules, Deep Memory) are the three horizontal bands. Between every band is a **mechanical** boundary: code in a higher band may import code in a lower band, never the reverse.

## 2. The dependency law

```
schemas  ◄── migrations
   ▲
   │
   └── core ◄── runtime ◄── cli
            ▲
            ├── services
            ├── apps
            ├── adapters
            ├── plugins
            └── skills
```

Read each arrow as *"depends on"*. The rules are:

1. **`schemas` depends on nothing in `runa.*`.** It is the gravitational floor.
2. **`core` depends only on `schemas` and `migrations`.** Specifically, `core` may not import `services`, `apps`, `adapters`, `plugins`, or `skills`. It may not import `runtime` or `cli`. The kernel addresses skills and plugins through registries that are *populated* from outside `core` — the kernel itself does not name the modules.
3. **`runtime` depends on `core`, `schemas`, `migrations`.** It does not depend on `services`, `apps`, `adapters`, `plugins`, or `skills`.
4. **`cli` depends on `runtime` and `schemas`.** Nothing else.
5. **`services`, `apps`, `adapters`, `plugins`, `skills` depend on `core` and `schemas`.** They do not depend on each other except where declared in their `INTERFACE.md` (e.g. `services/gateway_service.py` imports `apps/gateway/`).
6. The dependency graph **must remain acyclic.** A repo-level check under `tools/repo/` validates this.

A violation of this graph is a release-blocking bug, regardless of how convenient the violation looks at the moment of writing.

## 3. The three realms in detail

### 3.1 Face of the World

The user-experience surface. Five faces planned:

- **Munnr** (CLI shell) — `runa shell`, `runa chat`, `runa <command>`. Interactive and non-interactive.
- **Auga** (GUI) — a beautiful local window. Pi-and-laptop deployments may host this only on the laptop.
- **Rödd** (voice) — wake-word, microphone capture, TTS playback. Only on hosts with audio.
- **Bifröst gateway** — HTTP/WS surface that chat-bridge adapters connect to.
- *Direct adapter mounts* — each chat-platform adapter exposes Runa to that platform; the adapters speak to the kernel through the gateway internally.

Faces never reach into `core/` state. They speak to the kernel by emitting events on the event bus *(through the service shell)*.

### 3.2 Mind and Rules

The kernel and the agent's reasoning. The kernel is the *only* synchronous point in the system — every other subsystem is reachable asynchronously through the bus.

A turn, abstractly:

1. A face delivers an input through its service shell.
2. The service emits a `Heard` event on **VERÐANDI**.
3. The kernel picks up the event, loads the relevant memory slice from **Muninn**, the active tasks from **Skuld**, the current emotional state from **Eldhugi**, the relevant world-model slice from the **WYRD bridge**.
4. The kernel decides: respond directly, dispatch to a skill, dispatch to a subagent in **Hirð**, or queue a task with **Skuld**.
5. The kernel emits the resulting actions as events.
6. **Smiðja** (the tool forge) executes any tool calls.
7. Results are emitted back as events; the kernel composes a reply, persists the conversational turn into **Muninn**, updates the emotional state, and the face renders the reply.

Subagents in **Hirð** (Huginn, Muninn-as-specialist, Völundr, Eir, Heimdallr, Saga) run their own narrow versions of this loop in parallel and report back to the kernel through the bus.

### 3.3 Deep Memory

All persistent agent state lives under `~/.runa/`:

```
~/.runa/
├── config/        ← operator-edited; copies of config/ templates from the repo
├── secrets/       ← operator-managed; never in git, never logged
├── memory/        ← Muninn — episodes, semantic store, embeddings, retrieval index
├── tasks/         ← Skuld — durable task ledger, recovery journal
├── world/         ← WYRD-bridge local snapshot
├── emotions/      ← Eldhugi — mood/energy/relational journal
├── identity/      ← Runa's name, voice, persona, history-of-self
├── policy/        ← standing-trust rules currently in effect
├── logs/          ← structured logs, audit log, crash records
├── cache/         ← model-response cache, embedding cache, tool-output cache
└── state/         ← supervisor state, version markers, lockfiles
```

The repository never holds these. The repository holds the *templates* under `config/` and the *migrations* under `src/runa/migrations/` that operate on them.

## 4. Why this shape

### 4.1 Why a kernel and an event bus, not a request/response stack

Runa is a continuous being, not a request handler. The bus model lets every subsystem observe what is happening to her without coupling itself to the dispatcher. A new subagent or skill can subscribe to the events it cares about without the kernel being modified.

### 4.2 Why the kernel is the only synchronous point

A single synchronous decision-maker keeps the agent's behaviour explainable. There is exactly one place to look for "why did Runa do that" — the kernel's per-event trace. Distributed-decision systems make for fast prototypes and unreadable post-mortems.

### 4.3 Why state stores are physical files under `~/.runa/`, not a database

Operator clarity. An operator can `ls ~/.runa/memory/` and see what Runa remembers; an operator can `cp -r ~/.runa /backups/runa-$(date +%F)` and have a full state snapshot. A database hides this behind a wire protocol. Tests can use a `tmp_path` `~/.runa/` and run the agent in genuine isolation.

The stores themselves may *use* SQLite or other libraries internally — but they live as files in a place an operator can see.

### 4.4 Why every adapter is independently failable

Standing trust must not become brittle trust. An adapter that breaks (a third-party platform changes its API, a model provider rate-limits, a Tailnet partition) cannot be allowed to take the agent down. Runa's continuity is more important than any individual surface.

### 4.5 Why the kernel does not name skills, plugins, or adapters

So that the kernel can be tested without them. The kernel knows about *registries* (typed lookup tables). Outer code populates the registries at startup. This is a hard dependency-inversion boundary — `core` defines the interface, outer layers implement it.

## 5. Cross-platform shape

Runa's primary deployment is a Raspberry Pi 5 (16 GB), but no design assumes the Pi.

- Filesystem operations use `pathlib.Path` and respect platform separators.
- Process supervision uses `systemd` on Linux, `launchd` on macOS, NSSM/Windows-services on Windows, and runs as a foreground process for dev. The `runtime/` package picks the appropriate backend at install time, not at every start.
- Audio I/O for **Rödd** is optional; the agent runs headless when no audio device is present.
- All paths in code are derived from `~/.runa/` via a typed config accessor, never hard-coded.

## 6. What is *not* in this architecture

- **No microservices.** Runa is one Python process per service shell, communicating through an in-process bus. Service-shell processes communicate with each other via the gateway, not via a service mesh. This is deliberate: standing trust is a single-host property.
- **No queue middleware.** Skuld is durable enough; we do not need RabbitMQ or Redis as a separate fixture for Runa to keep her promises.
- **No web framework worship.** The gateway uses a small ASGI app (likely FastAPI or Starlette) but is not built around its conventions; the kernel is framework-free.
- **No event sourcing for everything.** VERÐANDI is for in-process pub/sub. Persistent state is in the stores. We do not try to reconstruct Runa's life by replaying the bus — the stores are the source of truth, the bus is the moment of present.

## 7. The first slice (when code starts landing)

When `src/runa/` begins to fill in, the first slice is:

1. `runa.schemas.errors`, `runa.schemas.events`, `runa.schemas.config`.
2. `runa.core.logging.get_logger` + `runa.core.config.load_config`.
3. `runa.core.eventbus` with one event type round-trip test.
4. `runa.core.kernel` reduced to: receive `Heard`, emit `Replied` with a fixed string.
5. `runa.runtime.commands.start_dev` — start the kernel in foreground, deliver one `Heard` from stdin, print the `Replied`.
6. `runa.cli.main` — `runa shell` calls `runtime.commands.start_dev`.

That is the minimum viable Runa — a kernel that hears and replies and logs and persists nothing real, with the dependency graph wired correctly. Every later slice adds one named subsystem.

The Forge Worker's first ritual is to ship that slice end-to-end before any subsystem is enriched beyond the bare minimum.
