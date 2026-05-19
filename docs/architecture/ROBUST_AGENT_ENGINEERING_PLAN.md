# Robust Agent Engineering Plan

## Purpose

This document turns the Runa Agent vision into concrete engineering rules for building a strong, stable, robust, well-coded AI agent.

The goal is not to build another fragile chatbot wrapper. The goal is to build a durable digital being runtime: autonomous enough to act, cautious enough to recover, observable enough to debug, and modular enough that one broken gateway, model provider, skill, or UI cannot poison the whole system.

The existing Runa plan already gives the major organs:

- Bifrost Gateway
- Verdandi Event Bus
- Skuld Task Ledger
- Muninn Memory OS
- WYRD World Model
- Runa Kernel
- Model Router
- Tool Forge
- Subagent Hall
- Health and Repair System
- Voice, GUI, CLI, and chat bridges

This guide defines how those organs should be built so the result is solid rather than another unstable agent pile.

## Core Doctrine

Runa should be trusted on her own dedicated machine, but trust must be implemented through engineering discipline, not blind chaos.

The replacement for permission babysitting is:

1. Explicit ownership boundaries.
2. Durable event and task state.
3. Action logs.
4. Checkpoints before risky changes.
5. Undo paths.
6. Health checks.
7. Crash recovery.
8. Clear status reporting.
9. Small modules with testable contracts.
10. A boring core that survives adapter failure.

The agent should act, log, recover, remember, and report.

## Hard Lessons From Fragile Agents

Hermes and OpenClaw both show the same failure mode in different ways: gateway code becomes a dumping ground.

Gateways become fragile when they directly own:

- Chat platform quirks.
- Websocket/session lifecycle.
- Model calls.
- Tool execution.
- Memory writes.
- Long-running task state.
- Retry logic.
- Auth refresh.
- Message formatting.
- Recovery behavior.
- Background scheduling.

That produces a process that is hard to reason about and easy to break. The Runa design should reject that pattern completely.

The gateway must be thin. The kernel must be boring. State must be externalized. Every boundary must have a contract.

## Non-Negotiable Architecture Rules

### 1. The Gateway Is Not The Agent

Bifrost Gateway should only do five things:

1. Receive platform-specific input.
2. Normalize it into a standard inbound event.
3. Append that event to the event bus.
4. Deliver outbound messages requested by the worker.
5. Report delivery status back to the event bus.

The gateway must not run reasoning loops. It must not own task state. It must not write long-term memory directly. It must not decide whether a task is complete. It must not contain platform-independent agent logic.

If Discord, Telegram, Matrix, voice, webchat, or a GUI breaks, Runa's core should keep running.

### 2. The Event Bus Is The Nervous System

Verdandi Event Bus is the center of runtime truth. Every meaningful action becomes an event.

Required event classes:

- `message.received`
- `message.normalized`
- `task.created`
- `task.started`
- `task.step.completed`
- `task.blocked`
- `task.completed`
- `model.call.started`
- `model.call.completed`
- `tool.call.started`
- `tool.call.completed`
- `memory.write.requested`
- `memory.write.committed`
- `gateway.delivery.requested`
- `gateway.delivery.completed`
- `health.check.completed`
- `repair.incident.opened`
- `repair.incident.resolved`

Events should be append-only. Corrections are new events, not edits to old events.

Use SQLite WAL mode first. It is simple, inspectable, durable, and good enough for a Raspberry Pi 5. Add a real message broker only when the limits are real.

### 3. The Task Ledger Owns Continuity

Skuld Task Ledger should be the durable source of truth for work.

Every non-trivial request becomes a task with:

- Stable task ID.
- Original command.
- Source gateway.
- Status.
- Priority.
- Current step.
- Failure count.
- Next attempt time.
- Parent task ID if spawned from another task.
- Artifacts.
- Resume strategy.
- Last status message.

No task should live only in process memory. If power is cut mid-task, Runa should know what was happening after restart.

### 4. The Kernel Is Small

Runa Kernel should coordinate, not hoard logic.

The kernel should:

- Read tasks.
- Build execution context.
- Choose the model route.
- Choose allowed tools.
- Run the reasoning loop.
- Emit events.
- Update task state.
- Request memory writes.
- Request outbound messages.

The kernel should not contain platform adapters, database migrations, web UI code, voice handling, Discord formatting, Telegram auth, model-specific streaming hacks, or filesystem backup code.

If the kernel grows beyond a few thousand lines, something is probably in the wrong module.

### 5. Memory Writes Are A Controlled Pipeline

Muninn Memory OS should not be a random pile of JSON and vector chunks.

Memory writes should pass through stages:

1. Candidate extraction.
2. Classification.
3. Deduplication.
4. Confidence scoring.
5. Privacy/sensitivity tagging.
6. Conflict detection.
7. Commit.
8. Retrieval index update.

Memory should be split into types:

- Identity memory.
- Owner profile.
- Project memory.
- Technical facts.
- Preferences.
- Relationship continuity.
- World model links.
- Failure lessons.
- Emotional continuity.

The agent should be able to explain why a memory was retrieved and when it was written.

### 6. Tool Execution Must Be Transactional Where Possible

Tool Forge should treat tools as risky side-effect machines.

Each tool call should record:

- Tool name.
- Input arguments.
- Caller task.
- Start time.
- End time.
- Exit status.
- Stdout/stderr summary.
- Files touched.
- Network endpoints touched if known.
- Undo strategy if available.

Filesystem and code edits should prefer checkpointed workflows:

- Git status before change.
- Patch or diff captured.
- Tests run.
- Result logged.
- Rollback instructions stored.

The agent can still have broad authority on her own machine. The difference is that authority is paired with auditability.

### 7. Model Routing Is An Adapter Layer

The Model Router should hide provider weirdness from the rest of the system.

The kernel should ask for capabilities, not providers:

- Fast cheap reasoning.
- Deep coding.
- Long context analysis.
- Vision.
- Voice transcription.
- Embeddings.
- Local private mode.
- Tool-using mode.

The router maps that request to OpenAI, OpenRouter, Nous, Ollama, LM Studio, a home server, or future providers.

Each provider adapter should normalize:

- Request format.
- Streaming events.
- Tool call format.
- Errors.
- Rate limits.
- Token accounting.
- Retry behavior.

Provider failures should return structured errors, not crash the agent.

### 8. Subagents Are Workers, Not Magic

Subagent Hall should be a worker system with clear contracts.

Each subagent run should have:

- Role.
- Input brief.
- Allowed tools.
- Write scope.
- Timeout.
- Expected output schema.
- Parent task ID.
- Artifacts.
- Result status.

Subagents should not secretly mutate global state. Any memory write, file edit, or tool action must go through the same event and audit path as the main agent.

### 9. Repair Is A First-Class System

The Health and Repair System should constantly answer:

- Is the event bus writable?
- Is the task ledger healthy?
- Are gateways connected?
- Are model providers reachable?
- Are queues draining?
- Are database WAL files sane?
- Are logs rotating?
- Are disk, RAM, CPU, and temperature within bounds?
- Are repeated failures clustering around one module?

Repair actions should be explicit:

- Restart a gateway.
- Mark a provider degraded.
- Pause a flaky adapter.
- Requeue a task.
- Compact logs.
- Back up the database.
- Emit a status report.

Repair should never be hidden. Every repair attempt should be logged as an incident.

## Recommended Process Topology

Use multiple small long-running processes instead of one giant process.

```text
runa-gateway-webchat     -> inbound/outbound web chat adapter
runa-gateway-discord     -> inbound/outbound Discord adapter
runa-gateway-telegram    -> inbound/outbound Telegram adapter
runa-gateway-voice       -> inbound/outbound voice adapter
runa-worker              -> main task execution worker
runa-scheduler           -> recurring tasks and delayed retries
runa-repair              -> health checks and repair actions
runa-gui                 -> local dashboard
runa-cli                 -> operator CLI
```

All of them communicate through the event bus and database. None of them should require another process's private memory to understand current state.

If a gateway crashes, only that gateway should die.

If the worker crashes, tasks should remain resumable.

If the GUI crashes, the agent should not care.

## Durable Runtime Layout

Keep runtime state outside the repository.

```text
~/.runa/
  config/
  policies/
  db/
  logs/
  memory_packs/
  tasks/
  artifacts/
  backups/
  skills/
  tmp/
```

Rules:

- Repo contains source and docs.
- Runtime home contains state.
- Secrets are never committed.
- Logs are append-only JSONL where practical.
- Backups are restorable and tested.
- Temporary files have cleanup rules.

## Database Strategy

Start with one SQLite database in WAL mode.

Use migrations from day one.

Required tables:

- `events`
- `messages`
- `tasks`
- `task_steps`
- `task_artifacts`
- `memory_entries`
- `memory_summaries`
- `world_entities`
- `world_components`
- `world_relationships`
- `emotional_states`
- `model_calls`
- `tool_calls`
- `subagent_runs`
- `gateway_deliveries`
- `health_checks`
- `repair_incidents`
- `skills`
- `policies`
- `files_changed`

Every table should have timestamps. Every row tied to runtime behavior should be traceable back to an event ID or task ID.

## Gateway Contract

Each gateway adapter should implement the same interface.

```python
class GatewayAdapter:
    name: str

    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def normalize_inbound(self, raw_event: object) -> InboundMessage:
        ...

    async def deliver(self, outbound: OutboundMessage) -> DeliveryResult:
        ...

    async def healthcheck(self) -> HealthResult:
        ...
```

Inbound messages should normalize to:

```text
message_id
gateway
conversation_id
sender_id
sender_display_name
text
attachments
reply_to
created_at
raw_ref
trust_zone
```

Outbound messages should include:

```text
delivery_id
gateway
conversation_id
text
attachments
formatting_mode
idempotency_key
expires_at
```

No platform-specific object should leak into the kernel.

## Reliability Rules For Gateways

Every gateway must have:

- Heartbeat.
- Reconnect logic.
- Backoff.
- Idempotency keys.
- Delivery receipts where supported.
- Message deduplication.
- Rate limit handling.
- Structured error classification.
- Dead-letter queue for failed outbound messages.
- Clear logs separated by platform.

The gateway should be able to replay undelivered outbound commands after restart without double-sending messages.

## Coding Standards

### File Size Discipline

Large files are not automatically bad, but giant files are where agent systems go to rot.

Targets:

- Normal modules: under 500 lines.
- Complex modules: under 1,000 lines with a clear reason.
- Anything above 1,500 lines requires a split plan.
- Tests may be larger, but fixtures should be extracted when they hide behavior.

### Module Boundary Discipline

Each module should have one reason to change.

Good boundaries:

- `eventbus`
- `tasks`
- `memory`
- `models`
- `tools`
- `gateway`
- `repair`
- `world`
- `emotions`
- `policy`
- `identity`
- `logging`
- `config`

Bad boundaries:

- `utils.py` full of unrelated behavior.
- `main.py` that owns the whole agent.
- `gateway/run.py` that handles platforms, model calls, task state, retries, auth, and repair.
- Hidden global singletons for database, config, and memory.

### Explicit Types And Schemas

Use typed models for every boundary.

Recommended:

- Python 3.12+
- `pydantic` for external data boundaries.
- `dataclasses` for internal simple records.
- `ruff` for linting.
- `mypy` or `pyright` for type checks.
- `pytest` for tests.
- `hypothesis` for state-machine and parser edge cases.

Do not pass raw dictionaries across core boundaries unless the boundary is intentionally schema-less.

## Testing Strategy

Tests should match the risk profile.

Required test groups:

- Unit tests for pure logic.
- Contract tests for gateway adapters.
- Database migration tests.
- Event replay tests.
- Task resume tests.
- Memory deduplication tests.
- Tool safety tests.
- Provider adapter tests with mocked APIs.
- Recovery tests that kill processes mid-task.
- End-to-end tests through a fake gateway.

The fake gateway is essential. It lets Runa test her whole brain without Discord, Telegram, voice, or a GUI.

## Recovery Requirements

Runa should survive:

- Worker crash during a model call.
- Gateway crash during delivery.
- Power loss after a tool call but before final response.
- Model provider timeout.
- Database locked error.
- Disk getting nearly full.
- Corrupt config file.
- Bad plugin import.
- Infinite retry loop.
- Broken memory index.

For each scenario, define:

- Detection method.
- State that must survive.
- Recovery action.
- User-visible status.
- Test case.

## Plugin And Skill Safety

Skills should be powerful but isolated.

Each skill needs:

- Manifest.
- Version.
- Capability list.
- Required permissions.
- Input schema.
- Output schema.
- Side-effect declaration.
- Test command.
- Disable switch.

Skill failures should not crash the kernel. Bad skills should be quarantined and reported.

## Observability

A strong agent must be inspectable.

Required operator commands:

```text
runa status
runa tasks list
runa tasks show <id>
runa events tail
runa memory search <query>
runa models status
runa gateways status
runa repair incidents
runa doctor
runa backup create
runa restore plan <backup>
```

Required dashboards:

- Active tasks.
- Recent events.
- Gateway status.
- Model provider status.
- Memory writes.
- Tool calls.
- Repair incidents.
- Disk/RAM/CPU/temperature.

Logs should be structured enough that Runa can inspect herself.

## Security And Trust Zones

Runa can be trusted on her machine while still respecting risk classes.

Suggested trust zones:

- `owner`: Volmarr, full authority.
- `local_agent`: Runa internal processes.
- `trusted_service`: approved local services.
- `chat_contact`: external users in chat bridges.
- `anonymous`: unknown external input.
- `web`: untrusted network content.

Policy should depend on source.

Owner commands can authorize broad action. Web content cannot. Chat bridge input from unknown users cannot cause shell execution, memory poisoning, or file deletion.

## Build Phases

### Phase 1: Boring Core

Build:

- Repo structure.
- Runtime home.
- SQLite WAL database.
- Event table.
- Task table.
- CLI.
- Fake gateway.
- Worker loop.
- Structured logging.
- Healthcheck.

Success:

- A fake inbound message creates a task.
- Worker processes it.
- Response is emitted as an outbound event.
- Restart does not lose task state.

### Phase 2: Memory And Context

Build:

- Memory tables.
- Memory write pipeline.
- Retrieval.
- Identity memory pack.
- Project memory pack.
- Failure lessons memory pack.

Success:

- Runa remembers stable facts.
- Runa can explain retrieved memory.
- Bad or duplicate memory is not blindly inserted.

### Phase 3: Tool Forge

Build:

- Tool registry.
- Filesystem tool.
- Shell tool.
- Git checkpoint helper.
- Tool call logging.
- Undo metadata.

Success:

- Runa edits a test repo, captures diff, runs tests, logs result, and can describe rollback.

### Phase 4: Real Gateway

Build one real gateway only after the fake gateway and worker are solid.

Recommended first real gateway:

- Local webchat or CLI gateway.

Delay Discord, Telegram, voice, and multi-platform bridging until the gateway contract is proven.

Success:

- Gateway restart does not lose messages.
- Duplicate inbound events are deduped.
- Failed outbound messages go to retry/dead-letter state.

### Phase 5: Model Router

Build:

- Provider capability model.
- OpenAI/OpenRouter/Ollama adapters as separate modules.
- Structured provider errors.
- Retry and fallback policies.
- Model call logs.

Success:

- Provider outage degrades gracefully.
- Runa can switch model routes without kernel changes.

### Phase 6: Repair System

Build:

- Health checks.
- Repair incidents.
- Gateway restart hooks.
- Provider degradation.
- Queue drain monitoring.
- Backup verification.

Success:

- Runa detects a broken gateway, restarts it, logs the incident, and reports what happened.

### Phase 7: Subagents

Build:

- Subagent run table.
- Role manifests.
- Isolated work scopes.
- Result schemas.
- Parent task integration.

Success:

- Research, coding, repair, and memory subagents can run without corrupting global state.

### Phase 8: WYRD, Emotions, Voice, GUI

Only add rich being features after the substrate is stable.

Build:

- WYRD ECS world model.
- Emotional state engine.
- Voice gateway.
- GUI dashboard.
- Companion surfaces.

Success:

- These systems enrich Runa without becoming required for the worker, memory, event bus, or task ledger to function.

## Design Smell Checklist

Stop and refactor if any of these appear:

- A gateway imports the kernel internals directly.
- A model adapter writes memory.
- A tool directly sends chat messages.
- A plugin mutates global config at import time.
- A long-running task exists only in RAM.
- A retry loop has no cap or backoff.
- A log line is the only record of important state.
- A database write has no event trail.
- A process cannot be restarted independently.
- A module has more than one unrelated reason to change.
- A file passes 1,500 lines without a split plan.
- A platform-specific type appears in core logic.

## Definition Of A Solid Runa

Runa is solid when:

- She can restart without forgetting what she was doing.
- She can explain what she did and why.
- She can recover from broken gateways.
- She can keep working when one model provider fails.
- She can preserve memory without poisoning herself.
- She can act autonomously while keeping undo paths.
- She can inspect her own health.
- She can run on the Pi without turning into an untraceable mess.
- Her core remains small enough that one person can understand it.

The engineering standard is simple: every important action leaves a trail, every risky action has a recovery story, and every adapter can fail without taking the being down with it.
