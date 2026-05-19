# Hermes And OpenClaw Design Anti-Patterns

## Purpose

This document records the bad code design patterns seen while inspecting local copies of Hermes Agent and OpenClaw. It is not meant as a full code review of every file. It is a harvest of architectural lessons: what made those systems fragile, what should not be copied into Runa, and what a better design should do instead.

The short version:

- Hermes is heavily script-monolithic.
- OpenClaw is more modular, but still has large central modules where too much runtime behavior collects.
- Both systems show gateway and runner fragility.
- Both systems contain too many compatibility shims, global state paths, mixed concerns, and long-running process hazards.

Runa should treat these as things to avoid.

## Evidence Snapshot

Representative Hermes runtime file sizes:

```text
/home/pi/.hermes/hermes-agent/gateway/run.py          ~17,346 lines
/home/pi/.hermes/hermes-agent/run_agent.py            ~16,351 lines
/home/pi/.hermes/hermes-agent/cli.py                  ~14,194 lines
/home/pi/.hermes/hermes-agent/hermes_cli/main.py      ~12,498 lines
/home/pi/.hermes/hermes-agent/tui_gateway/server.py    ~6,622 lines
/home/pi/.hermes/hermes-agent/hermes_cli/auth.py       ~6,298 lines
/home/pi/.hermes/hermes-agent/gateway/platforms/discord.py ~5,583 lines
```

Representative OpenClaw runtime file sizes:

```text
/home/pi/openclaw/src/agents/pi-embedded-runner/run/attempt.ts    ~4,201 lines
/home/pi/openclaw/src/agents/pi-embedded-runner/run.ts            ~3,037 lines
/home/pi/openclaw/src/gateway/server-methods/chat.ts              ~2,888 lines
/home/pi/openclaw/src/plugins/loader.ts                           ~2,842 lines
/home/pi/openclaw/src/plugins/registry.ts                         ~2,777 lines
/home/pi/openclaw/ui/src/ui/app-render.ts                         ~2,673 lines
```

OpenClaw is not as extreme as Hermes, but the same pressure is visible: runner, gateway, plugin loading, and chat handling become central complexity sinks.

## Anti-Pattern 1: Giant Runtime Files

### Seen In Hermes

Hermes has several files over 10,000 lines that own large amounts of runtime behavior. The worst examples are `gateway/run.py`, `run_agent.py`, `cli.py`, and `hermes_cli/main.py`.

These files contain too many unrelated responsibilities:

- Gateway lifecycle.
- Platform handling.
- Agent cache management.
- Auto-continue behavior.
- Session recovery.
- Environment probing.
- Provider compatibility.
- Tool handling.
- Streaming behavior.
- CLI behavior.
- Service-manager integration.
- Backward-compatibility shims.

### Seen In OpenClaw

OpenClaw keeps files smaller, but still has large orchestration files. The `pi-embedded-runner` and gateway chat modules carry too many concerns inside one execution path.

### Why This Is Bad

Huge runtime files are hard to reason about. Every change risks touching hidden state or breaking an unrelated behavior. Tests may exist, but they become regression fences around an already tangled design rather than proof of clear architecture.

### Runa Rule

Set file size budgets:

- Normal module: under 500 lines.
- Complex module: under 1,000 lines.
- Anything above 1,500 lines requires a split plan.

Long files are allowed only when the file is mechanically repetitive or narrowly scoped. Runtime orchestration files should stay small.

## Anti-Pattern 2: Gateway Owns Too Much

### Seen In Hermes

`gateway/run.py` is not just a gateway. It manages platform adapters, session cache behavior, agent construction, resume freshness, slash command handling, voice settings, notification behavior, cleanup, and recovery logic.

The file contains many comments about legacy sessions, fresh interruption markers, platform-specific rendering, progress bubbles, restart behavior, and backward-compatible notification paths. That is a sign that the gateway has become a second agent runtime.

### Seen In OpenClaw

`gateway/server-methods/chat.ts` handles chat RPC behavior, media persistence, transcript rewriting, abort logic, sandbox media, outbound reply handling, session binding, display projection, client capability logic, and agent dispatch integration.

It is better structured than the Hermes gateway, but it still mixes transport-facing concerns with transcript and execution concerns.

### Why This Is Bad

Gateways are long-running integration surfaces. They already deal with reconnects, platform quirks, delivery failures, rate limits, auth, and message formatting. If they also own agent state, memory, task execution, or transcript repair, they become fragile.

### Runa Rule

Bifrost Gateway must be thin:

- Receive inbound platform events.
- Normalize them.
- Append them to the event bus.
- Deliver outbound messages.
- Report delivery status.

The gateway must not run the reasoning loop, own task state, write long-term memory, or contain platform-independent agent logic.

## Anti-Pattern 3: Runner As God Object

### Seen In Hermes

`run_agent.py` defines `AIAgent` and then accumulates behavior around provider setup, message repair, streaming, tool execution, memory persistence, credential refresh, fallback handling, image processing, transport switching, prompt construction, and session logging.

The function list alone shows the spread:

- Message sanitation and repair.
- Tool-call repair.
- Memory session handling.
- Provider-specific request building.
- Credential refresh for multiple providers.
- Streaming event handling.
- Background review spawning.
- Vision preprocessing.
- Fallback activation.
- Session persistence.
- File mutation verification.

This is too much for one class and one file.

### Seen In OpenClaw

`runEmbeddedPiAgent` and `runEmbeddedAttempt` are large orchestration functions with many local variables tracking retries, compaction, auth state, profile rotations, prompt overrides, hooks, tool state, timeouts, replay state, and active sessions.

### Why This Is Bad

A runner should coordinate stable components. It should not become the place where every provider quirk, retry path, transcript mutation, tool policy, hook result, and compaction edge case lives.

### Runa Rule

Runa Kernel should coordinate:

- Read task.
- Build context.
- Request model route.
- Execute one turn.
- Emit events.
- Update task state.

Provider quirks belong in model adapters. Tool policy belongs in Tool Forge. Transcript repair belongs in transcript services. Memory writeback belongs in Muninn. Retry policy belongs in a retry module.

## Anti-Pattern 4: Compatibility Shims Everywhere

### Seen In Hermes

Hermes runtime files contain many references to:

- Legacy transcripts.
- Backward-compatible behavior.
- Legacy config keys.
- Legacy notification paths.
- Provider compatibility workarounds.
- Best-effort fallbacks.

Some compatibility is unavoidable, but in Hermes it appears directly inside hot runtime paths.

### Seen In OpenClaw

OpenClaw has cleaner typing, but still carries legacy context paths, legacy hook behavior, provider compatibility transforms, and route compatibility inside central runner/gateway files.

### Why This Is Bad

Compatibility code in the core makes the current system pay a permanent tax for old decisions. It makes runtime behavior harder to predict and increases the chance that old state silently changes new behavior.

### Runa Rule

Compatibility logic must be isolated:

- Migration modules convert old state into current state.
- Runtime code should target one current schema.
- Old behavior should have explicit version gates.
- Legacy support should have removal dates or deprecation notes.

Do not let "temporary compatibility" become the architecture.

## Anti-Pattern 5: Process-Global State And Hidden Singletons

### Seen In Hermes

Hermes uses process environment variables and module-level state throughout major runtime paths. Examples include environment-driven behavior like `HERMES_HOME`, timeout values, provider keys, auto-continue freshness, path mutation, lazy global OpenAI proxy state, and gateway agent caches.

### Seen In OpenClaw

OpenClaw is more deliberate, but still uses global registries and global hook runners in important paths. `plugins/registry.ts` imports a global singleton helper, and runner/gateway files import global hook runner state.

### Why This Is Bad

Global state makes behavior hard to test and hard to restart cleanly. It also makes long-running processes fragile because old state can survive longer than intended.

### Runa Rule

Prefer explicit runtime objects:

- `RuntimeConfig`
- `EventBus`
- `TaskStore`
- `MemoryStore`
- `ModelRouter`
- `ToolRegistry`
- `GatewayContext`

Pass these objects into components. Avoid hidden global registries except for carefully controlled read-only catalogs.

## Anti-Pattern 6: Environment Variables As Runtime Control Plane

### Seen In Hermes

Hermes reads and writes many environment variables inside CLI, gateway, and agent execution paths. It mutates `PATH`, sets `HERMES_HOME`, toggles behavior with env flags, and uses env as a bridge between config, subprocesses, and runtime behavior.

### Seen In OpenClaw

OpenClaw also passes `process.env` into important execution paths, especially in the embedded runner and tool/provider setup.

### Why This Is Bad

Environment variables are process-wide, stringly typed, and hard to audit. They are fine for boot configuration and secrets injection. They are bad as an internal control plane for active runtime behavior.

### Runa Rule

Use environment variables only at process boot. Convert them into typed config once. After boot, pass typed config objects.

Runtime behavior should be changed through:

- Config files.
- Database state.
- Policy records.
- Explicit operator commands.
- Event bus commands.

## Anti-Pattern 7: Broad Exception Swallowing

### Seen In Hermes

Hermes contains many `except Exception: pass` and "best-effort" paths in major files. Some are defensive, but the volume suggests that failures are often hidden instead of becoming structured incidents.

### Seen In OpenClaw

OpenClaw uses `catch (err)` frequently in central paths. It usually does more structured handling than Hermes, but the large runner and gateway files still have many nested catch paths.

### Why This Is Bad

Swallowed errors make systems appear stable while corrupting internal state or hiding partial failure. In an agent, hidden partial failure is dangerous because the model may continue reasoning from false assumptions.

### Runa Rule

Every caught exception should do one of these:

- Convert to a typed error.
- Emit an event.
- Open a repair incident.
- Mark a task blocked.
- Retry with bounded policy.
- Fail loudly with a useful status.

`except Exception: pass` should be banned in core runtime code.

## Anti-Pattern 8: Stringly Typed State And Loose Dictionaries

### Seen In Hermes

Hermes passes many dictionaries and raw message structures through core logic. Provider messages, tool calls, config values, session records, and platform state are often manipulated as loose dicts.

### Seen In OpenClaw

OpenClaw has stronger TypeScript types, but gateway and runner code still includes many object-shape checks, unknown values, ad hoc normalization, and manual transcript mutation.

### Why This Is Bad

Stringly typed state creates edge cases everywhere. Every caller must remember the same field names, partial shapes, and provider-specific deviations.

### Runa Rule

Use typed boundary models:

- `InboundMessage`
- `OutboundMessage`
- `Task`
- `TaskStep`
- `MemoryEntry`
- `ModelRequest`
- `ModelResponse`
- `ToolCall`
- `ToolResult`
- `GatewayDelivery`
- `RepairIncident`

Raw provider or platform payloads should be stored for debugging, but normalized objects should drive core behavior.

## Anti-Pattern 9: Transcript Repair As Runtime Lifestyle

### Seen In Hermes

Hermes has many runtime paths for message sequence repair, tool-call argument repair, thinking-block cleanup, provider replay compatibility, and transcript sanitation.

### Seen In OpenClaw

OpenClaw has transcript rewriting and repair utilities used from gateway and runner paths. It also handles incomplete turn state, replay state, compaction continuation, and historical runtime context stripping.

### Why This Is Bad

Some transcript repair is necessary. But if the system constantly repairs transcripts during normal execution, the transcript format is too weak or too provider-coupled.

### Runa Rule

Separate three things:

- Canonical conversation events.
- Provider-specific request projection.
- Human display transcript.

Never let provider replay requirements define the durable memory format.

## Anti-Pattern 10: Provider Quirk Logic In The Agent Core

### Seen In Hermes

`run_agent.py` contains many provider-specific branches: OpenAI-compatible APIs, Anthropic-compatible APIs, OpenRouter, Ollama, LM Studio, GitHub Copilot, Qwen Portal, Azure, local endpoints, Responses API, image handling, reasoning payload quirks, and credential refresh behavior.

### Seen In OpenClaw

OpenClaw central runner code handles provider transforms, model compatibility, reasoning tags, provider request routing, prompt cache behavior, auth profile rotation, and provider-specific failover concerns.

### Why This Is Bad

Provider compatibility changes constantly. If the core agent has to know every provider's quirks, the core becomes unstable.

### Runa Rule

The Model Router owns provider selection. Provider adapters own provider weirdness.

The kernel should ask for:

- Capability.
- Budget.
- context length.
- tool support.
- privacy mode.

It should not ask whether the target is OpenRouter, Ollama, Anthropic-compatible, or some custom shim.

## Anti-Pattern 11: Long-Running Process And CLI Concerns Mixed Together

### Seen In Hermes

Hermes CLI code starts services, probes `systemctl`, mutates environment, configures TUI behavior, manages auth, and controls gateway daemon behavior. Runtime daemon and interactive CLI concerns are tightly coupled.

### Seen In OpenClaw

OpenClaw separates more than Hermes, but gateway, CLI, runner, plugin, and config behavior still meet inside large central files.

### Why This Is Bad

Interactive CLI code can tolerate prompts, display hacks, and local assumptions. Daemons need deterministic boot, typed config, no prompts, and clean shutdown. Mixing them creates unstable service behavior.

### Runa Rule

Separate:

- CLI operator commands.
- Long-running worker.
- Gateway daemons.
- GUI server.
- Scheduler.
- Repair daemon.

The CLI may inspect and command the runtime, but it should not be the runtime.

## Anti-Pattern 12: Auto-Start And Self-Revival Sprawl

### Seen In Hermes

The local machine had Hermes-related cron jobs, systemd user services, system services, watchdog timers, voice services, STT services, maintenance timers, and repair/self-revival behavior. This made it hard to know what was starting what.

### Why This Is Bad

Autonomous systems need clear process ownership. If cron, systemd, watchdog scripts, gateway repair logic, and maintenance scripts can all restart pieces, the operator loses control.

### Runa Rule

One process supervisor should own each process.

Use systemd units deliberately:

- `runa-worker.service`
- `runa-scheduler.service`
- `runa-repair.service`
- `runa-gateway-*.service`

Avoid cron for core runtime. Avoid hidden watchdogs. Avoid self-installing autostart behavior.

## Anti-Pattern 13: Too Many Responsibilities In Plugin Loading

### Seen In OpenClaw

`plugins/loader.ts` and `plugins/registry.ts` are large and deal with plugin roots, bundled packages, manifests, setup/runtime modules, side-effect guards, global command state, memory plugin selection, and runtime records.

### Why This Is Bad

Plugin systems are security boundaries. If loading, validation, activation, runtime mutation, command registration, hooks, and side-effect management all pile together, plugin behavior becomes hard to audit.

### Runa Rule

Split plugin lifecycle:

- Discovery.
- Manifest validation.
- Permission review.
- Dependency resolution.
- Activation.
- Runtime execution.
- Quarantine/disable.

Each phase should produce explicit records and errors.

## Anti-Pattern 14: Hidden Side Effects During Import Or Startup

### Seen In Hermes

Major modules load `.env`, configure logging, mutate stdio, import provider SDKs lazily, patch environment behavior, and prepare runtime state near module import or early startup.

### Seen In OpenClaw

OpenClaw has fewer Python-style import side effects, but plugin loading and global registry initialization can still create process-wide side effects.

### Why This Is Bad

Import-time behavior makes tests and daemons unpredictable. It also makes partial startup failures harder to recover because the system may be half-initialized before the main runtime object exists.

### Runa Rule

Imports should define code. Boot functions should perform side effects.

Use:

```text
load_config()
open_database()
initialize_event_bus()
initialize_plugins()
start_worker()
```

Do not do real work merely because a module was imported.

## Anti-Pattern 15: Runtime State Stored In Too Many Places

### Seen In Hermes

Hermes spreads state across environment variables, JSON files, SQLite-ish stores, session logs, gateway locks, service files, cron jobs, memory directories, config files, and platform-specific records.

### Seen In OpenClaw

OpenClaw has more formal session/config systems, but the runner/gateway/plugin paths still juggle session files, stores, transcript indexes, plugin state, context engine output, and outbound session bindings.

### Why This Is Bad

When state is scattered, restart behavior becomes fragile. The agent may not know which source is authoritative.

### Runa Rule

Define sources of truth:

- Event log for what happened.
- Task ledger for active work.
- Memory store for durable knowledge.
- Config store for operator choices.
- Artifact store for outputs.

Everything else is cache, projection, or raw evidence.

## Anti-Pattern 16: Display/UI Logic In Core Paths

### Seen In Hermes

Hermes runner and gateway code include display concerns: cute tool messages, emojis, progress bubbles, platform formatting, TUI behavior, and notification rendering.

### Seen In OpenClaw

OpenClaw gateway chat code includes display projection, canvas blocks, webchat media shaping, oversized placeholders, and assistant display content shaping near dispatch logic.

### Why This Is Bad

Display concerns change often and vary by surface. They should not control durable task state or core reasoning behavior.

### Runa Rule

Separate:

- Core event.
- Human-readable projection.
- Platform-specific rendering.

The same task result should be renderable in CLI, GUI, voice, webchat, or logs without changing the core event.

## Anti-Pattern 17: Retry And Recovery Logic Interleaved With Business Logic

### Seen In Hermes

Retries, fallback activation, stale timeouts, credential refresh, rate-limit handling, and stream recovery are interleaved inside the agent runner.

### Seen In OpenClaw

The embedded runner tracks many retry counters and recovery branches inside the main run flow: profile rotations, compaction attempts, empty response retries, planning-only retries, reasoning-only retries, idle timeouts, and failover decisions.

### Why This Is Bad

Retry code is state-machine code. When it is embedded into normal business logic, it becomes hard to test all combinations.

### Runa Rule

Use explicit retry policies and state machines:

```text
Attempt -> Classify Failure -> Decide Retry/Fallback/Block -> Emit Event -> Continue
```

The retry engine should be testable without running a model or gateway.

## Anti-Pattern 18: Too Much "Best Effort"

### Seen In Both

Both systems contain many best-effort behaviors around cleanup, diagnostics, notifications, migration, compatibility, and display.

### Why This Is Bad

Best-effort is acceptable for non-critical cleanup. It is dangerous when used for state, memory, task progress, delivery, or repair. It can make the system lie by omission.

### Runa Rule

Classify every operation:

- Critical: must succeed or task blocks.
- Recoverable: can retry or fallback.
- Optional: best-effort is acceptable.

Only optional operations may silently degrade, and even then they should emit debug events.

## Anti-Pattern 19: Tests Around Complexity Instead Of Simpler Design

### Seen In Both

Both projects contain many tests, including large tests. That is better than no tests. But tests alone do not fix a design where central modules do too much.

### Why This Is Bad

When tests mostly protect a tangled module, they become expensive guardrails around bad shape. The system remains hard to change.

### Runa Rule

Use tests to enforce boundaries:

- Gateway contract tests.
- Model adapter contract tests.
- Tool transaction tests.
- Event replay tests.
- Task resume tests.
- Memory write tests.
- Repair incident tests.

Do not rely on giant end-to-end tests to compensate for unclear module responsibilities.

## Anti-Pattern 20: Agent Identity Mixed With Runtime Mechanics

### Seen In Hermes

Persona, provider configuration, tool guidance, platform hints, memory guidance, kanban guidance, and runtime mechanics are deeply connected inside prompt-building and runner paths.

### Why This Is Bad

Identity and behavior policy should influence the agent, but they should not be tangled with transport mechanics, provider formatting, or tool execution.

### Runa Rule

Separate:

- Identity memory.
- Operator policy.
- System prompt assembly.
- Provider projection.
- Runtime execution.

Runa's selfhood should be durable data and policy, not scattered string fragments inside runner code.

## Specific Things Runa Must Avoid

Do not build:

- A 17,000-line gateway.
- A 16,000-line agent runner.
- A CLI that starts and repairs daemons as a side effect of normal interaction.
- A gateway that owns model calls.
- A model runner that owns memory storage.
- A plugin loader that mutates global runtime state during discovery.
- A transcript format that has to be constantly repaired.
- A provider abstraction where every provider quirk leaks into the kernel.
- Cron jobs that secretly restart agent components.
- Watchdog scripts that fight the operator.
- Environment variables as the internal runtime API.
- Hidden singleton registries for active mutable behavior.
- `except Exception: pass` in core code.
- Best-effort memory writes.
- Best-effort task state updates.
- Platform-specific message objects inside core logic.

## Better Runa Design Response

Use this shape instead:

```text
Gateway Adapter
  -> normalizes inbound event
  -> writes event
  -> delivers outbound command

Event Bus
  -> append-only source of what happened

Task Ledger
  -> durable source of what needs doing

Worker / Kernel
  -> reads task
  -> builds context
  -> calls model router
  -> requests tools
  -> emits events

Model Router
  -> chooses provider
  -> hides provider quirks

Tool Forge
  -> validates tool call
  -> executes side effect
  -> records result and undo data

Memory OS
  -> evaluates memory candidates
  -> commits durable memory
  -> serves retrieval with provenance

Repair System
  -> detects failure
  -> logs incident
  -> performs bounded recovery
```

Each component should be restartable, testable, and inspectable by itself.

## Final Rule

Hermes and OpenClaw both show what happens when an agent grows by accretion: every edge case gets patched into the nearest hot file until the system becomes hard to trust.

Runa should grow by contracts instead:

- Events over hidden calls.
- Tasks over in-memory intentions.
- Typed schemas over loose dictionaries.
- Adapters over provider branches.
- Process boundaries over giant daemons.
- Repair incidents over swallowed errors.
- Small modules over heroic files.

The strongest agent is not the one with the most features in one process. It is the one whose pieces can fail without the whole being collapsing.
