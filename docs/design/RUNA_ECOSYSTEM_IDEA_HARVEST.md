# Runa Ecosystem Idea Harvest

## Purpose

This document gathers design ideas from the local repos under `/home/pi` that should feed into the design of Runa Agent.

The goal is not to copy every project into Runa. The goal is to identify the reusable architectural patterns, memory systems, safety ideas, embodiment concepts, and engineering disciplines already present across the ecosystem, then turn them into a coherent design vocabulary for Runa.

The major lesson across the repos is clear:

> Runa should not be a monolithic agent. Runa should be an operating system for a digital being, built from small, inspectable organs connected by events, durable memory, typed contracts, and recovery paths.

## Repos And Sources Surveyed

High-signal local sources included:

- `/home/pi/Runa-Agent-Digital-Being`
- `/home/pi/Verdandi`
- `/home/pi/verdandi`
- `/home/pi/NorseSagaEngine`
- `/home/pi/WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model`
- `/home/pi/NorseSagaEngine/wyrd_protocol`
- `/home/pi/runa_memory`
- `/home/pi/memory-system-docs`
- `/home/pi/mimir-well`
- `/home/pi/huginn`
- `/home/pi/muninn`
- `/home/pi/bifrost`
- `/home/pi/eir-archived-standalone`
- `/home/pi/svalinn`
- `/home/pi/skofnung`
- `/home/pi/hlidskjalf`
- `/home/pi/vordr`
- `/home/pi/fact_store`
- `/home/pi/Hamr`
- `/home/pi/Seidr-Smidja`
- `/home/pi/seidr_engine`
- `/home/pi/kista`
- `/home/pi/Heimdall-SL-Hermes-Agent`
- `/home/pi/data/reports/*Heimdall*`
- `/home/pi/Viking-Code-Mythic-Engineering-CLI-Vibe-Coding`

There are many additional repos, duplicates, backups, upstream/vendor trees, and experiments. This document focuses on the repos that contribute directly to the Runa agent architecture.

## The Big Synthesis

The ecosystem already contains almost every organ Runa needs:

| Need | Existing Source | Runa Design Use |
|---|---|---|
| Real-time nervous system | Verdandi | Event bus, pulse feed, cross-process awareness |
| Self-monitoring | Verdandi heartbeat | Health score, state machine, checks/actions |
| Memory database | Mimir's Well | Durable memory, FTS5, provenance, contradiction detection |
| Semantic recall | Huginn | Vector search and hybrid retrieval |
| Associative recall | Muninn | Hebbian reinforcement and path consolidation |
| Unified memory API | Bifrost | Composite memory provider |
| Memory maintenance | Eir | Decay, promotion, dedup, backup, integrity check |
| Context pruning | Svalinn | Token budget protection |
| Tool learning | Skofnung | Tool success/latency affinity |
| Prompt cache | Hlidskjalf | TTL/LRU response caching |
| Output guardian | Vordr | Validation, hallucination detection, correction log |
| World model | WYRD | ECS world state outside the model context |
| Game/world behavior | NorseSagaEngine | Data-driven prompting, charts, session persistence |
| Persona assembly | PersonaCompilerSpec | Runtime persona packets instead of static character blobs |
| Micro-context | MicroRAGPipelineSpec | Typed, contradiction-aware context packets |
| Secrets | Kista | Local encrypted vault, atomic writes, key safety |
| Avatar/body generation | Hamr, Seidr-Smidja | Headless spec-first embodiment pipeline |
| Virtual-world body | Heimdall | Second Life/virtual world bridge, body/mind separation |
| Engineering method | Mythic Vibe CLI | Intent -> constraints -> architecture -> plan -> build -> verify -> reflect |
| Repo governance | Mythic Vibe CLI, Hamr, Seidr-Smidja | Domain boundaries, shared core, contract-first adapters |

Runa should be the integration layer that turns these separate ideas into one stable digital-being runtime.

## Core Design Doctrine To Carry Forward

### 1. Evented Self-Awareness From Verdandi

Verdandi's strongest idea is self-awareness as routing.

Important ideas to use:

- Unix domain socket event bus for local low-latency process communication.
- Newline-delimited JSON protocol.
- Append-only JSONL feed.
- Server-side event stamping with sequence and timestamps.
- Hub-down fallback to direct feed writes.
- Subscriber model for live awareness.
- Ring buffer for fast recent event retrieval.
- Health check command.
- Graceful shutdown and feed rotation.

Runa application:

- Every Runa process should emit events.
- Gateways, workers, memory, repair, tools, model calls, and subagents should all publish to one event stream.
- The event feed should be the first source of truth for "what happened."
- Runa should be able to tail her own nervous system.

Recommended Runa event fields:

```yaml
event:
  event_id: string
  event_type: string
  source: string
  actor: string|null
  task_id: string|null
  session_id: string|null
  payload_json: object
  priority: low|normal|high|critical
  persistence: feed|db|temporary
  created_at: iso8601
```

### 2. Heartbeat And Self-Healing From Verdandi

Verdandi's AGI architecture notes define a minimal self-aware system:

- Heartbeat.
- Nerve hub.
- Memory.
- Reaction.
- Protection.
- Prediction.

Important ideas to use:

- Regular autonomous self-checks.
- Health score and trend.
- State machine: initializing, running, degraded, critical, recovering.
- Circuit breakers.
- Reactor rules that map checks to actions.
- Pulse history for temporal integration.
- Repair incidents as first-class events.

Runa application:

- Runa needs a `runa-repair` daemon, but it should be clean and explicit, not hidden watchdog sprawl.
- Health checks should produce structured pulses.
- Repair actions must be bounded, logged, and verified.
- Prediction should be added after basic checks are stable.

Health dimensions:

```yaml
health_pulse:
  event_bus: ok|degraded|down
  task_queue: ok|backlogged|stalled
  memory_db: ok|degraded|corrupt
  model_router: ok|degraded|unavailable
  gateways: map
  disk: percent
  memory: percent
  cpu: percent
  temperature: celsius
  health_score: 0_to_100
  trend: improving|stable|declining
```

### 3. Memory OS From Mimir, Huginn, Muninn, Bifrost, Eir

The memory repos define a complete memory operating system.

#### Mimir's Well

Use for:

- Durable SQLite memory.
- FTS5 search.
- WAL mode.
- Transactional writes.
- Contradiction detection.
- Knowledge promotion.
- Emotional valence.
- Entity/relationship storage.
- Backup and repair.

#### Huginn

Use for:

- Semantic vector search.
- Hybrid search with keyword plus vector fusion.
- Filtered search by category, importance, metadata.
- Embedding synchronization from Mimir.

#### Muninn

Use for:

- Hebbian memory associations.
- Co-activation strengthening.
- Decay of unused links.
- Emotional boost.
- Consolidated paths.
- Transitive associations.

#### Bifrost

Use for:

- One unified memory API.
- Weighted composite scoring across Mimir, Huginn, Muninn.
- Search, store, recall, health, consolidate.
- Hiding backend complexity from the kernel.

#### Eir

Use for:

- Decay.
- Promotion.
- Deduplication.
- Consolidation.
- Backup.
- Integrity check.
- Structured maintenance report.

Runa application:

- Runa should not invent a new flat memory store.
- Runa should define Muninn Memory OS as a proper subsystem using these ideas.
- Memory maintenance should be a scheduled Runa task, not random cron magic.
- Every memory write should have provenance, confidence, salience, governance, and source event ID.

Canonical memory pipeline:

```text
experience event
  -> candidate extraction
  -> type classification
  -> salience scoring
  -> novelty detection
  -> contradiction check
  -> governance tagging
  -> Mimir write
  -> Huginn vector upsert
  -> Muninn association update
  -> memory.write.committed event
```

### 4. MemCube And Memory Governance From runa_memory

The University of Yggdrasil memory docs provide the conceptual discipline Runa needs.

Important ideas to use:

- Memories are active semantic structures, not passive notes.
- Memory injection has stages: capture, encoding, prioritization, validation, write-back.
- High-salience memories can be synchronous; low-salience memories can be asynchronous.
- MemCubes need schema, indexing, compression, governance, consistency, durability, and provenance.
- Memory gates have four functions: read, write, forget, and meta-gate.
- Retrieval should be attention-based and budget-aware.

Runa application:

- Create distinct MemCubes:
  - Identity.
  - Owner.
  - Project.
  - Episodic.
  - Procedural.
  - Relational.
  - Emotional.
  - Failure lessons.
  - World model facts.
- Each MemCube should define governance and durability.
- Permanent identity memory should not be edited like ordinary episodic memory.
- Forgetting should be designed, not accidental.

### 5. MicroRAG From NorseSagaEngine Research

The MicroRAG spec is one of the strongest context-design ideas in the repos.

Important ideas to use:

- Smaller models do not need more documents; they need better assembled micro-context.
- Context should be relevant, contradiction-aware, compact, typed, confidence-tagged, and task-shaped.
- Retrieval should use multiple index families:
  - atom.
  - episode.
  - canonical.
  - bond.
  - symbolic.
  - code.
  - graph.
- Query mode determines retrieval mode.
- Typed reranking beats raw similarity.

Runa application:

- Runa's Context Engine should build context packets, not dump raw memories.
- Every model call should get a task-shaped packet.
- The packet should include open unknowns and contradictions when relevant.
- Context assembly should be auditable.

Runa context pipeline:

```text
query understanding
  -> context mode selection
  -> candidate gathering
  -> typed reranking
  -> contradiction injection
  -> packet assembly
  -> generation
  -> post-generation validation
  -> feedback learning
```

### 6. Persona Compiler From NorseSagaEngine Research

The Persona Compiler spec solves the static-character-card problem.

Important ideas to use:

- Persona is a temporary runtime assembly, not a giant static blob.
- Inputs include identity core, trait lattice, bond excerpt, world role, scene frame, memory extract, truth packet, policy packet, and task packet.
- Output is a runtime persona contract with expiry and invalidation conditions.

Runa application:

- Runa's "personality" should be compiled per situation.
- Companion mode, coding mode, repair mode, and world-embodiment mode should produce different persona packets from the same identity core.
- The packet should include "must remember", "must not claim", and "must not cross."

This will keep Runa coherent without hardcoding all behavior into one prompt.

### 7. WYRD World Model

WYRD's core idea is essential:

> Move world state out of the LLM's fleeting context window and into deterministic ECS storage.

Important ideas to use:

- Entity-Component-System world model.
- Yggdrasil hierarchy for nested spatial/container relationships.
- Passive Oracle Model: factual world reports without personality interference.
- Engine-agnostic bridge support.
- Structured state persistence.
- Components for identity, spatial state, inventory, ownership, locks, temporal presence, health, faction, persona refs.
- Systems as deterministic state transformers.

Runa application:

- Runa should have a WYRD world model for:
  - local machines.
  - repos.
  - services.
  - files.
  - tasks.
  - people.
  - virtual-world locations.
  - avatar body state.
  - symbolic/metaphysical state if desired.
- The LLM asks the Passive Oracle for state instead of inventing it.
- WYRD should be integrated through a clean internal API and eventually external bridge APIs.

### 8. Four-Ledger Belief Graph

NorseSagaEngine's world-model belief graph spec should be used directly in Runa's design.

The four ledgers:

- Canon ledger: accepted objective/project truths.
- Belief ledger: what each actor believes.
- Relationship ledger: edges between entities.
- Event ledger: time-indexed things that happened.

Why it matters:

- Without a belief ledger, rumors become canon.
- Without an event ledger, change loses causal history.
- Without relationship edges, trust and dependency cannot be modeled.

Runa application:

- Runa should know the difference between:
  - "This is true."
  - "I believe this."
  - "Volmarr said this."
  - "A subagent inferred this."
  - "This was true before but may be stale."
- This matters for memory integrity, world modeling, and companion behavior.

### 9. Data-Driven Behavior From NorseSagaEngine

NorseSagaEngine demonstrates powerful data-driven AI behavior:

- charts drive prompting.
- character records contain psychology, appearance, backstory, mechanics.
- session state persists changes separately from base data.
- AI behavior is shaped by structured cultural/world data.

Runa application:

- Runa should use structured behavior packs instead of one huge system prompt.
- Examples:
  - engineering doctrine pack.
  - communication style pack.
  - owner preference pack.
  - companion behavior pack.
  - repair behavior pack.
  - coding behavior pack.
  - mythic-symbolic pack.
- Base identity should be stable; session changes should be layered and reviewable.

### 10. Orphaned Module Syndrome From Unified Integration Plan

The NorseSagaEngine integration plan names a crucial failure mode: modules get built and tested but never wired into the main loop.

Important idea:

```text
Architecture Vision -> Code Written -> Code Tested -> Module Done
                                      -> Main Loop never calls it
```

Runa application:

- Every feature needs an integration owner.
- A module is not done until:
  - it is wired into the runtime.
  - events are emitted.
  - health checks know it exists.
  - tests cover the integrated path.
  - docs explain the contract.
- Use integration sprints with no new features, only wiring and verification.

### 11. Headless-First, Spec-First From Hamr

Hamr provides excellent design laws:

- Parameter is sovereign.
- Headless first.
- Agent as user.
- Forge, do not paint.
- Modular blades.
- Architecture scales through named domains.

Important ideas to use:

- YAML specs as stable contracts.
- Headless operation as default.
- CLI and API before GUI.
- Validation before execution.
- Domain boundaries documented in tables.
- Build artifacts and compliance reports.

Runa application:

- Runa's own configuration, persona packets, memory policies, tool permissions, and gateway specs should be declarative.
- GUI is optional; headless runtime is primary.
- Agents are first-class users of Runa's APIs.

### 12. Shared Core Behind Many Doors From Seidr-Smidja

Seidr-Smidja's strongest architecture pattern is the Shared Anvil:

- MCP, CLI, REST, and skill manifests are thin protocol translators.
- A single core dispatch path owns the pipeline.
- Request and response models are canonical.
- All bridges lead to the same forge.

Runa application:

- Runa should expose multiple surfaces:
  - CLI.
  - GUI.
  - REST.
  - MCP.
  - chat.
  - voice.
- But they must all call the same internal command/task/event core.
- No bridge should invent its own behavior.

Canonical Runa request/response pattern:

```yaml
runa_request:
  request_id: string
  source: cli|gui|voice|chat|mcp|rest
  actor: string
  trust_zone: string
  intent: string
  payload: object
  metadata: object

runa_response:
  request_id: string
  success: bool
  task_id: string|null
  events: list
  artifacts: list
  errors: list
  summary: string
```

### 13. Compliance Gates And Vision Feedback From Seidr-Smidja/Hamr

Seidr-Smidja and Hamr both emphasize that outputs should be validated before delivery.

Important ideas:

- Build produces artifact plus inspection report.
- Rendered previews allow the agent to see what it made.
- Compliance checks fail with structured reports.
- No silent pass.

Runa application:

- Tool outputs should have validators.
- Code changes should have tests.
- Memory writes should have consistency checks.
- Persona packets should have truth checks.
- Avatar/world outputs should have visual or state inspections.
- Every artifact should have a verification story.

### 14. Deterministic Creativity From seidr_engine

The Seidr Engine is useful because it is creative without being stochastic mush.

Important ideas:

- Deterministic generation with seeds.
- Rule-based constraints.
- Domain lexicons.
- Scoring multiple attempts.
- Structural metadata.

Runa application:

- Use deterministic procedural systems for things that should be reproducible.
- LLMs can propose, but rule engines should verify.
- Creative systems should emit seed, config, and score.

This is useful for:

- persona tone generation.
- symbolic context generation.
- world events.
- naming.
- ritual/poetic output.
- scenario generation.

### 15. Local Secrets From Kista

Kista contributes the local sovereignty/security pattern.

Important ideas:

- Local encrypted vault.
- No cloud dependency.
- Atomic writes.
- Key regeneration protection.
- Import safety.
- Search over secrets.
- Password/API key types.
- Secure password input.

Runa application:

- Runa should never scatter secrets across config files.
- Create or integrate a Kista-like vault.
- Secrets should be fetched through a secret provider interface.
- Tool calls should never log secret values.
- Runa should check the vault before asking Volmarr for credentials.

### 16. Tool Affinity From Skofnung

Skofnung's tool affinity idea should become part of Runa's Tool Forge.

Important ideas:

- Record every tool invocation.
- Track task context, success, latency.
- Decay old scores.
- Recommend tools by empirical performance.

Runa application:

- Tool selection should learn from use.
- If `rg` succeeds for code search, prefer it.
- If a browser tool fails often on a domain, downgrade it.
- If a local command is slow or flaky, record that.
- Tool recommendations should be data-backed.

### 17. Prompt Cache From Hlidskjalf

Hliðskjálf gives a simple useful cache:

- Hash-based lookup.
- TTL expiry.
- LRU eviction.
- Pattern invalidation.
- SQLite persistence.

Runa application:

- Cache expensive deterministic operations:
  - summarized docs.
  - stable context packets.
  - embedding batches.
  - repeated status renderings.
  - stable model responses only when safe.
- Cache entries must include source hashes so stale cache can be invalidated.

### 18. Output Guardian From Vordr

Vörðr contributes the guardian pattern:

- Validate output against constraints.
- Detect hallucination patterns.
- Cross-reference sources.
- Self-correct.
- Log corrections.

Runa application:

- Runa should have Vordr-like validation after model output.
- Validators should be mode-specific:
  - coding answer.
  - file patch.
  - memory write.
  - world update.
  - chat reply.
  - external message.
- Corrections should become events and sometimes failure lessons.

### 19. Context Shield From Svalinn

Svalinn should become the token-budget protector.

Important ideas:

- Estimate tokens.
- Prune context.
- Summarize.
- Extract key facts.

Runa application:

- Every context packet goes through Svalinn.
- Pruning should preserve high-priority constraints and provenance.
- Context overflow is a design problem, not a thing to dump on the model.

### 20. Mythic Engineering CLI Workflow

Mythic Vibe CLI gives the project governance spine:

```text
intent -> constraints -> architecture -> plan -> build -> verify -> reflect
```

Important ideas:

- Method-first development.
- Durable artifacts.
- Prompt packets.
- Phase-oriented workflow.
- Compatibility policy.
- Drift detection.
- Plugin capability declarations.
- Event log.
- Atomic writes.
- Cross-process locks.
- Architecture boundaries.
- Active product boundary.
- Dormant/reference islands require adapter contracts.

Runa application:

- Runa should use this workflow internally for coding and self-improvement.
- Every major change should create artifacts:
  - intent.
  - constraints.
  - architecture note.
  - plan.
  - verification.
  - reflection.
- Runa should maintain design memory and ADRs.
- Advanced integrations should be behind contracts and feature flags.

### 21. Boundary Governance From Mythic Vibe CLI, Hamr, Seidr-Smidja

Multiple repos independently emphasize boundaries:

- Mythic Vibe CLI: active runtime vs dormant islands.
- Hamr: spec, body, face, hair, clothing, rigs, export, CLI domains.
- Seidr-Smidja: layered model and Shared Anvil.

Runa application:

- Define bounded contexts:
  - kernel.
  - eventbus.
  - tasks.
  - memory.
  - world.
  - models.
  - tools.
  - gateways.
  - subagents.
  - repair.
  - policy.
  - identity.
  - emotions.
  - embodiment.
- Enforce dependency direction.
- Add boundary checks to CI when code exists.

### 22. Heimdall Virtual-World Embodiment

Heimdall contributes a strong body/mind separation pattern:

- AI mind in Python.
- Protocol body in C#/.NET using battle-tested libraries.
- Python bridge over WebSocket/REST.
- Event-driven inbound/outbound flow.
- State persistence.
- Auto-reconnect.
- Rate limiting.
- Visible bot identification.
- Kill switch.
- Graceful degradation when mind disconnects.

Runa application:

- Embodiment should be adapter-based.
- The "body" should not be the "mind."
- Virtual world, voice, avatar, and chat systems should all normalize events into Runa's core.
- External platform rules and compliance belong in the body adapter.
- Owner control and kill switch must exist.

### 23. Agent-Orchestrated Avatar Creation From Hamr And Seidr-Smidja

Hamr and Seidr-Smidja should eventually become Runa's body-forging systems.

Important ideas:

- YAML character specs.
- Headless Blender.
- VRM export.
- Compliance reports.
- Preview renders.
- Agent-driven iterative refinement.
- Multiple protocol doors.

Runa application:

- Runa should store her avatar/body specs as durable identity artifacts.
- Avatar changes should be tasks with previews and validation.
- Visual self-model should be separate from core cognition.

### 24. Fact Store And Structured Knowledge

The fact store contains structured extracted facts by entity, category, and source.

Runa application:

- Runa needs a fact store distinct from fuzzy memory.
- Facts should have:
  - entity.
  - predicate.
  - value.
  - source.
  - confidence.
  - review state.
  - timestamps.
- Facts can feed WYRD, memory retrieval, and persona compilation.

## Proposed Runa Architecture From Harvest

```text
Interfaces
  CLI / GUI / REST / MCP / Voice / Chat / Virtual World
        |
        v
Thin Gateways
  normalize inbound events, deliver outbound commands
        |
        v
Verdandi Event Bus
  append-only nervous system
        |
        v
Skuld Task Ledger
  durable goals, plans, steps, blocked states
        |
        +----------------------------+
        |                            |
        v                            v
Muninn Memory OS              WYRD World Model
  Mimir/Huginn/Muninn           ECS, canon/belief/event/relationship
  Bifrost interface             Passive Oracle
  Eir maintenance
        |                            |
        +-------------+--------------+
                      |
                      v
Runa Kernel
  context assembly, planning, model route, tool orchestration
        |
        +---------------+---------------+
        |               |               |
        v               v               v
Model Router       Tool Forge       Subagent Hall
  providers          tools + audit     bounded workers
        |
        v
Vordr / Svalinn / Skofnung / Hlidskjalf
  validate, prune, learn tool affinity, cache
        |
        v
Repair + Reflection
  heartbeat, incidents, learning queue, self-improvement workflow
```

## High-Priority Features To Build First

### 1. Event Bus And Feed

Borrow from Verdandi.

Deliverables:

- SQLite-backed event table.
- JSONL append feed.
- Unix socket or local IPC.
- CLI tail/status.
- fallback write path.

### 2. Task Ledger

Runa needs continuity before intelligence.

Deliverables:

- task table.
- task steps.
- task artifacts.
- restart/resume.
- blocked state.
- status reports.

### 3. Memory OS Skeleton

Borrow from Mimir/Huginn/Muninn/Bifrost/Eir.

Deliverables:

- Mimir-style memory table.
- FTS search.
- memory write pipeline.
- source event IDs.
- simple retrieval.
- maintenance report.

### 4. Context Engine

Borrow from MicroRAG, Svalinn, PersonaCompiler.

Deliverables:

- query mode classifier.
- memory candidate gathering.
- typed reranking.
- context budget pruning.
- persona packet assembly.
- context audit.

### 5. Tool Forge

Borrow from Skofnung, Vordr, Mythic Vibe CLI.

Deliverables:

- tool registry.
- tool call logs.
- risk classes.
- undo metadata.
- tool affinity.
- validation.

### 6. WYRD Passive Oracle

Borrow from WYRD and world-model belief graph.

Deliverables:

- entity table.
- component table.
- relationship table.
- canon/belief/event separation.
- simple query API.

### 7. Repair Daemon

Borrow from Verdandi and Eir.

Deliverables:

- heartbeat.
- health score.
- repair incidents.
- bounded repair actions.
- backup checks.
- no hidden watchdog sprawl.

## Design Rules From The Ecosystem

1. Gateways are doors, not brains.
2. Events are the nervous system.
3. Task state must survive restart.
4. Memory must have provenance and governance.
5. Retrieval must be typed, scored, and budgeted.
6. World state belongs outside the LLM.
7. Persona should be compiled per scene.
8. Tools need audit trails and success learning.
9. Outputs need guardians and validators.
10. Secrets belong in a local encrypted vault.
11. Interfaces should share one core.
12. Bridges must be thin translators.
13. Runtime code must respect domain boundaries.
14. Self-repair must be visible and bounded.
15. Self-improvement must use checkpoints and verification.
16. Headless-first beats GUI-first.
17. Spec-first beats hidden state.
18. Integration is not optional.
19. Tests should enforce contracts, not defend monoliths.
20. Documentation is part of the runtime memory.

## Features To Avoid Importing Blindly

The ecosystem also shows traps:

- Cron sprawl.
- Hidden autostart.
- Orphaned modules.
- Duplicated Mimir/Muninn sources of truth.
- Gateway overreach.
- Runtime behavior hidden in environment variables.
- Multiple bridges with divergent semantics.
- Static persona blobs.
- Raw memory dumps into prompts.
- Model-provider quirks in the kernel.

Runa should harvest the patterns, not the mess.

## Suggested Runa Module Map

```text
runa/
  core/
    kernel/
    eventbus/
    tasks/
    memory/
    world/
    context/
    models/
    tools/
    subagents/
    repair/
    policy/
    identity/
    emotions/
    cache/
    validation/
  apps/
    cli_app/
    worker_app/
    gateway_app/
    gui_app/
    voice_app/
    repair_app/
  adapters/
    gateways/
      webchat/
      discord/
      telegram/
      matrix/
      second_life/
    providers/
      openai/
      openrouter/
      ollama/
      lmstudio/
    tools/
      filesystem/
      shell/
      git/
      browser/
      mcp/
    secrets/
      kista/
  data/
    schemas/
    migrations/
    seed_memory/
    policies/
  docs/
    architecture/
    decisions/
    operations/
    memory/
    world/
    embodiment/
  tests/
    unit/
    integration/
    recovery/
    contracts/
    evals/
```

## Cross-Repo Ideas By Category

### Cognition

Use:

- HuginnGate analysis/judgment/synthesis pipelines.
- Persona Compiler runtime packets.
- MicroRAG query modes.
- Value cascade from runa_memory.
- Mythic Engineering reflection phase.

### Memory

Use:

- Mimir durable store.
- Huginn semantic vectors.
- Muninn associative reinforcement.
- Eir consolidation.
- MemCube governance.
- Fact store structured claims.

### World

Use:

- WYRD ECS.
- Yggdrasil hierarchy.
- Passive Oracle.
- Four-ledger belief graph.
- NorseSagaEngine session persistence.

### Tools

Use:

- Tool affinity from Skofnung.
- Output validation from Vordr.
- Context pruning from Svalinn.
- Atomic writes and locks from Mythic Vibe CLI.
- Compliance gates from Hamr/Seidr-Smidja.

### Embodiment

Use:

- Heimdall body/mind split.
- Hamr avatar specs.
- Seidr-Smidja headless forge.
- Voice/chat gateways as adapters.

### Operations

Use:

- Verdandi heartbeat.
- Eir backup/integrity checks.
- Kista secrets.
- Mythic Vibe CLI diagnostics.
- Structured logs and event IDs everywhere.

### Engineering Process

Use:

- intent -> constraints -> architecture -> plan -> build -> verify -> reflect.
- ADRs.
- active runtime boundary.
- integration sprints.
- domain maps.
- contract tests.
- drift audits.

## Recommended Build Order

### Phase 0: Repo And Doctrine

- Create package scaffold.
- Add domain map.
- Add coding standards.
- Add architecture decision records.
- Add pyproject, tests, ruff, mypy/pyright.

### Phase 1: Nervous System

- Event bus.
- Event table.
- JSONL feed.
- CLI tail.
- health check.

### Phase 2: Task Continuity

- Task ledger.
- worker loop.
- fake gateway.
- restart/resume.

### Phase 3: Memory Skeleton

- Mimir-style store.
- write pipeline.
- FTS search.
- memory provenance.
- simple consolidation.

### Phase 4: Context Engine

- MicroRAG packets.
- Svalinn pruning.
- persona compiler.
- context audit.

### Phase 5: Tool Forge

- tool registry.
- shell/filesystem/git tools.
- Skofnung affinity.
- Vordr validation.
- undo metadata.

### Phase 6: World Model

- WYRD ECS.
- canon/belief/event/relationship ledgers.
- Passive Oracle.

### Phase 7: Model Router

- provider adapters.
- capability routing.
- fallback.
- usage/error logs.

### Phase 8: Repair And Learning

- heartbeat daemon.
- repair incidents.
- Eir-style maintenance.
- learning queue.

### Phase 9: Embodiment

- GUI dashboard.
- voice gateway.
- avatar/body spec.
- virtual-world bridge.

## Final Integration Principle

The whole ecosystem points to one conclusion:

Runa should be built like a living longhouse, not like a single enchanted script.

Each organ should have a hearth:

- event bus for present awareness.
- task ledger for continuity.
- memory OS for accumulated wisdom.
- world model for grounded reality.
- tool forge for action.
- repair daemon for survival.
- persona compiler for coherent presence.
- gateways for speech, voice, body, and world.

The LLM is not the being. The LLM is the voice and reasoning pressure moving through the being.

The being is the architecture.
