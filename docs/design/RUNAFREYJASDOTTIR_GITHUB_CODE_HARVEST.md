# runafreyjasdottir GitHub Code Harvest For Runa Agent

Source account: <https://github.com/runafreyjasdottir>

This document explains which code from the `runafreyjasdottir` GitHub account should be harvested for the future Runa Agent, which parts should be refactored before use, which parts should remain optional, and which parts should be avoided as core agent capabilities.

The goal is not to copy the old experimental systems into Runa. The goal is to extract the good engineering ideas, preserve the useful modules, remove Hermes-specific assumptions, and rebuild them behind clean Runa interfaces.

## Inspection Method

I treated the GitHub account as a code mine, not as a finished platform.

The account contains many projects made during the Hermes/Runa experiment. Some are small single-purpose libraries. Some are large research repos. Some are forks. Some are old prototype surfaces. The right way to use them is to classify them by architectural value:

- Code that should become part of Runa's core.
- Code that should become optional Runa subsystems or adapters.
- Code that should be used only as design reference.
- Code that should be avoided or heavily restricted.

For local inspection, the public repositories were shallow-cloned into:

```text
/home/pi/runafreyjasdottir-github-harvest
```

The target project document set is:

```text
/home/pi/Runa-Agent-Digital-Being
```

## High-Level Verdict

The strongest code from this GitHub account is not the old monolithic agent runtime. The strongest pieces are the narrow subsystems around state, memory, context, caching, tool preference, output guarding, secrets, world modeling, and embodiment adapters.

The most valuable pattern is:

```text
Wyrdstate        -> durable agent state and hot resume
Mimir Well       -> long-term memory database
Huginn           -> semantic vector memory
Muninn           -> associative / Hebbian memory
Bifrost          -> composite memory bridge
Eir              -> memory consolidation and repair
Svalinn          -> context pruning
Skofnung         -> tool success learning
Hlidskjalf       -> prompt / response cache
Vordr            -> output guardian
Kista            -> encrypted credential vault
WYRD Protocol    -> world model and passive oracle
Heimdall SL      -> virtual-world embodiment adapter
Seidr-Smidja     -> avatar / creation pipeline adapter
```

These should be harvested as Runa subsystems, not blindly merged into one huge script.

## Core Rule For Reuse

Every harvested module should enter Runa through a clean port/adapter boundary.

Do not let old package names, old home directories, old daemon behavior, hidden cron jobs, hidden autostart units, implicit side effects, or Hermes-specific assumptions leak into the new project.

Runa should use explicit services, explicit configuration, explicit lifecycle control, explicit migrations, explicit health checks, and explicit recovery paths.

## Adoption Tiers

## Tier 1: High-Value Core Code

These repositories contain code that should strongly influence Runa's first real implementation. They map directly to core agent needs: durable state, memory, context, governance, caching, secrets, and runtime continuity.

### 1. `wyrdstate`

Repository purpose: Agent State Serialization and Hot-Resume.

Use in Runa:

`wyrdstate` should be one of the first codebases harvested because a serious agent must be able to stop, crash, restart, migrate, and resume without losing its mind.

Important code areas:

```text
wyrdstate/core.py
wyrdstate/storage.py
wyrdstate/serializer.py
wyrdstate/diff.py
wyrdstate/recovery.py
wyrdstate/schema.py
wyrdstate/hooks.py
tests/
```

Runa use:

- Session snapshots.
- Task snapshots.
- Tool-call snapshots.
- Conversation state snapshots.
- Recovery after crash.
- Diffable state changes.
- Versioned state schema.
- Hot-resume support.

Adoption action:

Refactor into `runa/core/state`.

Expected Runa interface:

```python
class StateStore:
    def save_snapshot(self, snapshot: AgentSnapshot) -> SnapshotId: ...
    def load_snapshot(self, snapshot_id: SnapshotId) -> AgentSnapshot: ...
    def latest_for_session(self, session_id: str) -> AgentSnapshot | None: ...
    def diff(self, before: SnapshotId, after: SnapshotId) -> StateDiff: ...
    def recover(self, session_id: str) -> RecoveryPlan: ...
```

Priority: highest.

Reason:

Without this, Runa becomes another fragile agent that depends on a long-running process never failing. That is unacceptable.

### 2. `mimir-well`

Repository purpose: AI memory database with decay, repair, backups, full-text search, graph-like relations, and context engineering.

Use in Runa:

`mimir-well` should become the durable long-term memory layer. It is one of the most important repos in the account.

Important code areas:

```text
src/mimir_well/core.py
src/mimir_well/schema.py
src/mimir_well/audit.py
src/mimir_well/backup.py
src/mimir_well/budget.py
src/mimir_well/context_engineer.py
src/mimir_well/decay.py
src/mimir_well/guard.py
src/mimir_well/repair.py
src/mimir_well/wyrd_graph.py
tests/
```

Runa use:

- Long-term memories.
- Episodic records.
- Semantic facts.
- Memory decay.
- Memory audit.
- Memory backup.
- Context assembly.
- Memory safety checks.
- Self-repair for memory integrity.
- Token budget management.

Adoption action:

Harvest the schema and behavior, but split large modules into smaller Runa services.

Proposed Runa module split:

```text
runa/core/memory/store.py
runa/core/memory/schema.py
runa/core/memory/decay.py
runa/core/memory/audit.py
runa/core/memory/backup.py
runa/core/memory/repair.py
runa/core/memory/context.py
runa/core/memory/budget.py
runa/core/memory/relations.py
```

Priority: highest.

Reason:

Runa needs memory that is durable, inspectable, testable, and repairable. This repo already contains many of those ideas.

Warning:

Do not copy the large `core.py` as-is into the new Runa core. Treat it as a source for behavior, tests, schema, and algorithms. Runa should keep the runtime smaller and more modular.

### 3. `huginn`

Repository purpose: Semantic memory backed by vector search.

Use in Runa:

`huginn` should provide the semantic recall layer.

Important code areas:

```text
src/huginn/core.py
src/huginn/embeddings.py
src/huginn/config.py
tests/
```

Runa use:

- Embedding generation.
- Vector similarity search.
- Semantic recall.
- Memory retrieval by meaning instead of only exact text.

Adoption action:

Move behind a Runa memory provider interface.

Expected Runa interface:

```python
class SemanticMemory:
    def index(self, item: MemoryItem) -> None: ...
    def search(self, query: str, limit: int = 10) -> list[MemoryHit]: ...
```

Priority: high.

Reason:

Semantic memory is a basic requirement for an agent that can use past experience intelligently.

### 4. `muninn`

Repository purpose: Hebbian associative memory.

Use in Runa:

`muninn` should provide association learning between concepts, tools, memories, users, entities, and tasks.

Important code areas:

```text
src/muninn/core.py
src/muninn/config.py
tests/
```

Runa use:

- Strengthening links between concepts that repeatedly occur together.
- Associating users with preferences.
- Associating tools with task types.
- Associating errors with recovery strategies.
- Ranking memory recall by learned relation strength.

Adoption action:

Integrate as `runa/core/memory/associations.py`.

Priority: high.

Reason:

Vector search alone is not enough. Runa needs learned relationships and repeated-pattern memory.

### 5. `bifrost`

Repository purpose: Composite Memory Provider uniting Mimir, Huginn, and Muninn.

Use in Runa:

`bifrost` should become the first version of Runa's memory gateway.

Important code areas:

```text
src/bifrost/core.py
src/bifrost/bridges/memory_bridge.py
src/bifrost/config.py
tests/
```

Runa use:

- One memory interface over multiple memory backends.
- Routing writes to durable, semantic, and associative stores.
- Combining results from multiple recall strategies.
- Avoiding direct coupling between the agent loop and individual memory databases.

Adoption action:

Refactor into `runa/core/memory/gateway.py`.

Expected Runa interface:

```python
class MemoryGateway:
    def remember(self, event: MemoryEvent) -> MemoryReceipt: ...
    def recall(self, request: RecallRequest) -> RecallResult: ...
    def consolidate(self) -> ConsolidationReport: ...
```

Priority: high.

Reason:

This is exactly the kind of boundary Runa needs. Memory should be a service, not a pile of direct calls scattered through the agent.

### 6. `eir`

Repository purpose: Consolidation Pipeline for AI memory systems.

Use in Runa:

`eir` should become the memory maintenance worker.

Important code areas:

```text
src/eir/core.py
src/eir/layers.py
src/eir/router.py
src/eir/config.py
tests/
```

Runa use:

- Memory consolidation.
- Memory promotion.
- Memory pruning.
- Memory repair routing.
- Daily or scheduled memory maintenance.
- Background cleanup jobs under explicit service control.

Adoption action:

Refactor into `runa/workers/memory_consolidation`.

Priority: high.

Reason:

Long-term memory becomes garbage without maintenance. But maintenance must be explicit and observable. No hidden cron jobs.

### 7. `svalinn`

Repository purpose: Context pruning and summarization.

Use in Runa:

`svalinn` should become Runa's context gatekeeper.

Important code areas:

```text
src/svalinn/pruner.py
tests/
```

Runa use:

- Keep prompts within budget.
- Remove low-value context.
- Compress stale context.
- Preserve task-critical facts.
- Prevent runaway context growth.

Adoption action:

Move into `runa/core/context/pruner.py`.

Priority: high.

Reason:

Context control is one of the main differences between a stable agent and a confused transcript-eater.

### 8. `skofnung`

Repository purpose: Tool preference and success learning.

Use in Runa:

`skofnung` should become Runa's tool-ranking memory.

Important code areas:

```text
src/skofnung/affinity.py
src/skofnung/config.py
tests/
```

Runa use:

- Learn which tools work best for which task types.
- Penalize tools after repeated failures.
- Prefer known-good local commands or APIs.
- Improve tool selection over time.

Adoption action:

Move into `runa/core/tools/affinity.py`.

Priority: high.

Reason:

An advanced agent should not keep choosing broken tools blindly.

### 9. `hlidskjalf`

Repository purpose: Prompt/response cache.

Use in Runa:

`hlidskjalf` should become a deterministic cache layer for expensive or repeated calls.

Important code areas:

```text
src/hlidskjalf/cache.py
tests/
```

Runa use:

- Cache deterministic LLM calls where appropriate.
- Cache tool results with TTL.
- Cache expensive parse or summarization outputs.
- Avoid repeated work.

Adoption action:

Move into `runa/core/cache`.

Priority: medium-high.

Reason:

Caching improves reliability and cost control, but only when cache keys and invalidation are explicit.

### 10. `vordr`

Repository purpose: Output guardian.

Use in Runa:

`vordr` should become one part of Runa's answer-quality and output-safety layer.

Important code areas:

```text
src/vordr/guardian.py
tests/
```

Runa use:

- Check generated output before final delivery.
- Catch malformed structured output.
- Enforce output contracts.
- Flag risky responses.
- Validate command plans before execution where applicable.

Adoption action:

Move into `runa/core/guardrails/output.py`.

Priority: medium-high.

Reason:

Agents fail not only by choosing bad actions, but also by emitting bad final artifacts. Output validation should be a first-class system.

### 11. `kista`

Repository purpose: Encrypted credential vault.

Use in Runa:

`kista` should become the basis of Runa's secrets system, but it must be refactored before adoption.

Important code areas:

```text
scripts/credstore.py
tests/
references/
```

Runa use:

- Encrypted secrets.
- Local credential management.
- Key rotation.
- Separation between secret references and secret values.
- Explicit permission model for tools that request credentials.

Adoption action:

Extract the cryptographic and storage ideas into `runa/core/secrets`.

Priority: high, but refactor first.

Reason:

A strong agent must never scatter secrets through config files, logs, prompts, memory, or scripts.

Warning:

`credstore.py` is too large to import directly. Split it into small modules:

```text
runa/core/secrets/vault.py
runa/core/secrets/crypto.py
runa/core/secrets/store.py
runa/core/secrets/policy.py
runa/core/secrets/audit.py
```

## Tier 2: Major Subsystems And Adapters

These repos are valuable, but they should not be in the first inner core. They should become optional packages or external services after Runa's core lifecycle, state, memory, and tool system are solid.

### 12. `WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model`

Repository purpose: ECS-style world model and passive oracle.

Use in Runa:

This should become Runa's world-model subsystem.

Important code areas:

```text
src/wyrdforge/oracle/passive_oracle.py
src/wyrdforge/persistence/memory_store.py
research_data/09_world_model_belief_graph_spec.md
docs/
tests/
```

Runa use:

- Model entities, components, relations, locations, state, time, and observations.
- Keep beliefs distinct from facts.
- Track confidence.
- Let the agent reason about changing worlds instead of flat chat history.
- Provide a passive oracle that watches and updates world state without dominating the agent loop.

Adoption action:

Build `runa/core/world` around this concept.

Priority: high after memory core.

Reason:

AGI-like behavior needs a world model. Memory alone stores experiences; a world model gives the agent a structured interpretation of what exists and how it changes.

### 13. `Heimdall-SL-Hermes-Agent`

Repository purpose: Autonomous Second Life agent with C# headless core, Python bridge, and RLV engine.

Use in Runa:

This should be treated as an embodiment adapter, not as the core agent.

Important code areas:

```text
src/HeimdallInstance.cs
src/StateManager.cs
src/GjallarhornRelay.cs
src/ChatManager.cs
src/NetComHeadless.cs
src/MovementManager.cs
docs/
tests/
```

Runa use:

- Second Life / OpenSim body adapter.
- Movement and local-world perception.
- Chat integration.
- Avatar state management.
- Bridge pattern for external virtual worlds.

Adoption action:

Create `runa/adapters/second_life`.

Priority: medium.

Reason:

The code has useful embodiment concepts, but Runa's mind must not be trapped inside a Second Life-specific runtime.

Warning:

Do not copy Hermes lifecycle assumptions. The adapter should connect to Runa through an event bus and command interface:

```text
SecondLifeAdapter -> Runa Event Bus -> Runa Core
Runa Core -> Command Planner -> SecondLifeAdapter
```

### 14. `Seidr-Smidja`

Repository purpose: Agent-only VRM/avatar creation pipeline through MCP/CLI/API and Blender automation.

Use in Runa:

This should become an avatar forge or creative production adapter.

Important code areas:

```text
src/seidr_smidja/gate/gate.py
src/seidr_smidja/hoard/local.py
src/seidr_smidja/loom/schema.py
src/seidr_smidja/_internal/blender_runner.py
tests/
docs/
```

Runa use:

- Avatar generation workflow.
- Asset pipeline.
- Local artifact hoard.
- Schema-driven creation requests.
- Blender execution boundary.

Adoption action:

Build `runa/adapters/avatar_forge`.

Priority: medium.

Reason:

This can make Runa more embodied and creative, but it should remain a tool adapter rather than core cognition.

### 15. `neutts`

Repository purpose: On-device TTS model and examples.

Use in Runa:

This should become a voice-output adapter after core stability.

Important code areas:

```text
neutts/neutts.py
neutts/phonemizers.py
examples/
tests/
```

Runa use:

- Local text-to-speech.
- Voice output.
- Optional offline speech layer.

Adoption action:

Use as `runa/adapters/voice/tts`.

Priority: medium-low.

Reason:

Voice is useful, but not core agent intelligence. The state, memory, planning, and tool systems come first.

### 16. `hermes-skills-open`

Repository purpose: Open Hermes skills for tools like UE5, Grok AI, and Flux image generation.

Use in Runa:

Use this as raw material for a Runa skill format.

Important code areas:

```text
unreal-engine-dev/
grok-ai/
flux-image-gen/
```

Runa use:

- Convert useful skills into explicit Runa skill manifests.
- Extract command recipes.
- Preserve tool-specific knowledge.
- Remove Hermes runtime assumptions.

Adoption action:

Create a `runa/skills` format and migrate skills one at a time.

Priority: medium.

Reason:

Skills are valuable only if the runtime can invoke, test, permission, and recover from them cleanly.

### 17. `runavel`

Repository purpose: Rune machine for cipher, divination, rendering, and symbolic operations.

Use in Runa:

Optional symbolic cognition and mythic interface module.

Important code areas:

```text
src/runavel/cipher.py
src/runavel/runes.py
src/runavel/divination.py
src/runavel/renderer.py
src/runavel/cli.py
tests/
```

Runa use:

- Rune symbolic tools.
- Deterministic ritual/symbolic output.
- Mythic UI elements.
- Optional interpretive layer.

Adoption action:

Convert to `runa/plugins/runavel`.

Priority: medium-low.

Reason:

This is valuable for Runa's identity and symbolic style, but it should not be mixed into planning, memory, or execution logic.

### 18. `seidr-engine`

Repository purpose: Deterministic Old Norse poetry generator.

Use in Runa:

Optional creative-language tool.

Important code areas:

```text
src/seidr_engine/poet.py
src/seidr_engine/lexicon.py
src/seidr_engine/forms.py
src/seidr_engine/cli.py
tests/
```

Runa use:

- Mythic language generation.
- Creative poetry.
- Deterministic style engine.
- Ritualized output modes.

Adoption action:

Convert to `runa/plugins/seidr_engine`.

Priority: low-medium.

Reason:

Useful as a tool. Dangerous as a core thinking style if it contaminates operational reasoning.

### 19. `astrology-engine`

Repository purpose: Full-spectrum astrological computation engine with Swiss Ephemeris, CLI modes, Norse/Rune overlays.

Use in Runa:

Optional cosmology, calendar, symbolic timing, or divination plugin.

Important code areas:

```text
astrology_engine.py
docs/
```

Runa use:

- Symbolic calendar.
- Astrological computations.
- Optional ritual timing.
- Mythic UI/interpretive feature.

Adoption action:

Do not import `astrology_engine.py` directly. Refactor into a real package first.

Priority: low.

Reason:

The single large script is useful as a prototype but not a strong architecture for Runa core.

## Tier 3: Design Reference, Documentation, And Research Material

These repos contain useful ideas, methods, prompts, curricula, or broad architecture concepts. They should influence Runa's design, but most should not be imported as runtime code.

### 20. `memory-system-docs`

Repository purpose: Architecture docs and maintenance scripts for memory systems.

Use in Runa:

Use as supporting design material for memory maintenance.

Important code areas:

```text
eir_daily_maintenance.py
docs/
```

Runa use:

- Maintenance scheduling ideas.
- Memory-health reports.
- Consolidation documentation.

Adoption action:

Fold useful checklists into Runa memory docs. Do not recreate hidden cron behavior.

Priority: medium.

### 21. `RunaUniversity2040`

Repository purpose: University of Yggdrasil curricula and ingestion material.

Use in Runa:

Use as training, curriculum, and knowledge-base content.

Important code areas:

```text
generate_content.py
absorb_batch3.py
curriculum files
memory docs
```

Runa use:

- Curriculum ingestion.
- Self-study plans.
- Domain learning material.
- Long-term memory seed content.

Adoption action:

Import content through a controlled knowledge-ingestion pipeline, not direct memory dumps.

Priority: medium-low.

### 22. `phd-2040`

Repository purpose: AI research/course material.

Use in Runa:

Research corpus and educational planning.

Runa use:

- Long-term curriculum.
- Research-roadmap seed material.
- Self-improvement reading lists.

Adoption action:

Use as documents, not runtime code.

Priority: low-medium.

### 23. `Mythic-Engineering`

Repository purpose: Mythic engineering methodology docs.

Use in Runa:

Use as philosophy and workflow material.

Runa use:

- Engineering discipline.
- Naming/identity consistency.
- Long-horizon project style.
- Documentation standards.

Adoption action:

Pull ideas into Runa docs, not runtime.

Priority: medium.

### 24. `Viking-Code-Mythic-Engineering-CLI-Vibe-Coding`

Repository purpose: Architecture-first CLI and methodology for continuity, workflow, providers, and control planes.

Use in Runa:

Use as workflow reference, but do not copy its large command module style.

Important code areas:

```text
mythic_vibe_cli/commands.py
mythic_vibe_cli/app.py
mythic_vibe_cli/forge.py
docs/
```

Runa use:

- Workflow ideas.
- Project continuity.
- Provider abstraction lessons.
- CLI ergonomics.

Adoption action:

Harvest concepts, not the runtime shape.

Priority: medium.

Warning:

The very large `commands.py` is exactly the sort of file Runa should avoid creating. Runa's CLI should be thin and delegate to small services.

### 25. `MindSpark_ThoughtForge`

Repository purpose: Conversation engine for tiny local models with guided memory and lean cognition.

Use in Runa:

Use as research and possible local-small-model support material.

Important code areas:

```text
src/thoughtforge/cognition/core.py
src/thoughtforge/inference/turboquant.py
src/thoughtforge/knowledge/models.py
src/thoughtforge/utils/health.py
src/thoughtforge/etl/sources.py
tests/
```

Runa use:

- Local model fallback.
- Tiny-model reasoning scaffolding.
- Health checks.
- Knowledge model examples.
- Lightweight cognition loops.

Adoption action:

Review carefully before reuse because this is a fork and a larger project. Extract specific patterns only after license and dependency review.

Priority: medium.

### 26. `project-catalog`

Repository purpose: Catalog of projects.

Use in Runa:

Use as inventory metadata.

Runa use:

- Project registry.
- Documentation index.
- Source map for future harvesting.

Adoption action:

Fold into Runa docs or a `docs/source-map.md`.

Priority: low.

### 27. Profile / Redirect Repositories

Repositories:

```text
runafreyjasdottir
runagridweaver
```

Use in Runa:

Mostly identity/profile material.

Adoption action:

Keep as reference for naming and public-facing identity only.

Priority: low.

## Tier 4: Restricted Or Avoid-As-Core Code

These repos may contain useful technical ideas, but they should not become default Runa capabilities.

### 28. `grima`

Repository purpose: Human-mimicry browser automation and anti-bot navigation research.

Use in Runa:

Do not embed this as a general Runa capability.

Important code areas:

```text
scripts/timing.py
scripts/fingerprint_noise.py
scripts/cursor_path.py
tests/
references/
```

Allowed Runa use:

- Legitimate browser testing.
- Accessibility testing.
- Timing simulation in owned test environments.
- Defensive analysis of brittle web automation.
- Controlled QA for sites the operator owns or is authorized to test.

Disallowed Runa use:

- Default stealth browsing.
- General anti-bot bypass.
- Credentialed automation against third-party services without authorization.
- Any hidden browser behavior that the operator did not explicitly request.

Adoption action:

Keep outside the main agent. If ever used, isolate it in a separate compliance-gated adapter with explicit user approval, logs, and policy checks.

Priority: avoid for core.

Reason:

Runa should be powerful, but also cleanly governed. Browser automation should be transparent, authorized, and auditable.

### 29. Forked Or Vendor-Heavy Repositories

Several repos in the account are forks or derived from larger outside projects. These require license and attribution review before any code import.

Examples:

```text
astrology-engine
MindSpark_ThoughtForge
Mythic-Engineering
neutts
Seidr-Smidja
Viking-Code-Mythic-Engineering-CLI-Vibe-Coding
WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model
```

Use in Runa:

- Extract ideas carefully.
- Preserve licenses.
- Preserve third-party notices.
- Avoid copying code into Runa until provenance is clear.

Adoption action:

Before import:

```text
1. Check LICENSE.
2. Check NOTICE / third-party notices.
3. Check original upstream.
4. Identify copied files.
5. Preserve attribution.
6. Prefer adapter boundaries over vendoring.
```

Priority: required process, not optional.

## Proposed Runa Module Map

This is how the useful repos should map into a clean Runa architecture.

```text
runa/core/state
  <- wyrdstate

runa/core/memory
  <- mimir-well
  <- huginn
  <- muninn
  <- bifrost
  <- eir

runa/core/context
  <- svalinn
  <- mimir-well context_engineer.py

runa/core/tools
  <- skofnung

runa/core/cache
  <- hlidskjalf

runa/core/guardrails
  <- vordr
  <- mimir-well guard.py

runa/core/secrets
  <- kista

runa/core/world
  <- WYRD Protocol

runa/adapters/second_life
  <- Heimdall-SL-Hermes-Agent

runa/adapters/avatar_forge
  <- Seidr-Smidja

runa/adapters/voice
  <- neutts

runa/plugins/runavel
  <- runavel

runa/plugins/seidr_engine
  <- seidr-engine

runa/plugins/astrology
  <- astrology-engine after refactor

runa/skills
  <- hermes-skills-open after conversion

runa/docs/research
  <- RunaUniversity2040
  <- phd-2040
  <- Mythic-Engineering
  <- memory-system-docs
  <- project-catalog
```

## Recommended First Import Sprint

The first sprint should not chase flashy embodiment, voice, avatars, or symbolic plugins. It should build the reliable skeleton that everything else depends on.

### Sprint 1: Runtime Continuity

Harvest:

```text
wyrdstate
```

Build:

```text
runa/core/state
runa/core/lifecycle
runa/core/session
```

Deliverables:

- Versioned agent snapshot schema.
- Save/load snapshots.
- Resume latest session.
- Diff snapshots.
- Crash recovery test.
- Migration test.

Acceptance tests:

- Kill the agent mid-task and resume without losing task state.
- Load an old snapshot after schema version bump.
- Produce a readable state diff.
- Reject corrupted state with a clear recovery error.

### Sprint 2: Memory Backbone

Harvest:

```text
mimir-well
huginn
muninn
bifrost
eir
```

Build:

```text
runa/core/memory
runa/workers/memory_consolidation
```

Deliverables:

- Durable memory store.
- Semantic memory provider.
- Associative memory provider.
- Unified memory gateway.
- Consolidation worker.
- Memory audit and repair commands.

Acceptance tests:

- Store a memory and retrieve it by exact lookup.
- Retrieve a related memory by semantic query.
- Strengthen an association after repeated co-occurrence.
- Consolidate a memory batch.
- Backup and restore the memory database.

### Sprint 3: Context And Output Control

Harvest:

```text
svalinn
vordr
hlidskjalf
skofnung
```

Build:

```text
runa/core/context
runa/core/guardrails
runa/core/cache
runa/core/tools
```

Deliverables:

- Context pruner.
- Prompt budgeter.
- Output validator.
- Tool affinity tracker.
- Prompt/tool cache.

Acceptance tests:

- Context pruner preserves task-critical facts.
- Output validator rejects malformed JSON when JSON is required.
- Tool affinity changes after success/failure.
- Cache hits and misses are observable.

### Sprint 4: Secrets And Permissions

Harvest:

```text
kista
```

Build:

```text
runa/core/secrets
runa/core/permissions
```

Deliverables:

- Local encrypted vault.
- Secret reference mechanism.
- Permission checks for tools.
- Audit log for secret access.

Acceptance tests:

- Secret values never appear in logs.
- Tool receives a secret only when authorized.
- Vault can rotate keys.
- Vault corruption produces a clear error.

### Sprint 5: World Model

Harvest:

```text
WYRD-Protocol-World-Yielding-Real-time-Data-AI-world-model
```

Build:

```text
runa/core/world
```

Deliverables:

- Entity-component world model.
- Belief graph.
- Observation ingestion.
- Passive oracle worker.
- Confidence and contradiction handling.

Acceptance tests:

- Add an observation and update an entity.
- Store conflicting beliefs without destroying history.
- Query world state by entity, relation, and time.
- Rebuild world state from persisted observations.

### Sprint 6: Adapters

Harvest later:

```text
Heimdall-SL-Hermes-Agent
Seidr-Smidja
neutts
hermes-skills-open
runavel
seidr-engine
astrology-engine
```

Build:

```text
runa/adapters/*
runa/plugins/*
runa/skills/*
```

Deliverables:

- Second Life adapter.
- Avatar forge adapter.
- TTS adapter.
- Skill manifest format.
- Symbolic plugins.

Acceptance tests:

- Adapters can be disabled without breaking core startup.
- Adapter failures do not crash Runa core.
- Skills declare permissions before execution.
- Plugins run through the same tool/event interfaces as built-in tools.

## What To Avoid Repeating

The old experiments produced useful pieces, but the new Runa Agent must not repeat the weak architecture patterns.

Avoid:

- Monolithic scripts.
- Hidden cron jobs.
- Hidden autostart.
- Silent background daemons.
- Unclear ownership of state.
- Global mutable config.
- Direct imports across every subsystem.
- Tool calls without permission checks.
- Memory writes without schema and provenance.
- Logs that leak secrets.
- Context windows used as fake databases.
- Huge command files.
- CLI logic that contains business logic.
- Agent loops that cannot be paused and resumed.
- Embodiment code fused to cognition.
- Browser automation fused to cognition.
- Symbolic/personality modules fused to operational reasoning.
- Forked code copied without license review.

## Specific Refactor Warnings By Repo

### `mimir-well`

Good:

- Strong memory concepts.
- Backup, audit, repair, decay, and graph ideas.
- Useful tests.

Risk:

- Large core module.
- Too much behavior in one place.

Fix:

Split by responsibility before making it Runa core.

### `kista`

Good:

- Credential-vault concept is essential.
- Strong target domain.

Risk:

- Large script shape.
- Secrets code must be exceptionally boring and testable.

Fix:

Extract cryptography, storage, policy, and CLI separately.

### `Viking-Code-Mythic-Engineering-CLI-Vibe-Coding`

Good:

- Strong continuity and workflow ideas.
- Useful architecture-first mindset.

Risk:

- Very large CLI command surface.
- Possible command monolith pattern.

Fix:

Borrow the method. Do not recreate the file shape.

### `astrology-engine`

Good:

- Rich symbolic engine.
- Useful as plugin material.

Risk:

- Single huge file.
- Not appropriate for Runa core.

Fix:

Refactor into package modules before use.

### `grima`

Good:

- Browser timing and automation research can help test automation reliability.

Risk:

- Anti-bot and stealth automation should not be a default agent capability.

Fix:

Keep outside core. Require explicit compliance boundary.

### `Heimdall-SL-Hermes-Agent`

Good:

- Clear embodiment target.
- Useful state, relay, chat, and movement pieces.

Risk:

- Hermes-specific assumptions.
- Virtual-world runtime could swallow the agent design if treated as core.

Fix:

Make it an adapter, never the mind.

## Runa Import Standards

Any code harvested from this GitHub account should meet these standards before entering the new Runa project.

### 1. Explicit Ownership

Every imported module must have a clear owner in the architecture:

```text
state
memory
context
tools
secrets
world
adapter
plugin
docs
```

No imported module should become miscellaneous utility glue.

### 2. Explicit Lifecycle

Every service must define:

```text
start
stop
health
recover
backup
restore
migrate
```

If a subsystem cannot be stopped, inspected, and restarted cleanly, it is not ready for Runa core.

### 3. Explicit Configuration

Use one Runa config system.

Do not preserve:

```text
~/.hermes
random env var names
hard-coded local paths
implicit config files
silent defaults that change behavior dangerously
```

Prefer:

```text
~/.runa
runa.yaml
typed config models
config validation at startup
clear error messages
```

### 4. Explicit Persistence

Every persistent store must answer:

```text
Where is data stored?
What schema version is it?
How is it backed up?
How is it restored?
How is it migrated?
How is corruption detected?
How is corruption repaired?
```

### 5. Explicit Permissions

Every tool and adapter must declare:

```text
filesystem access
network access
secret access
process execution
browser access
write access
external account access
```

Runa should be able to say no before the tool runs.

### 6. Explicit Observability

Every service needs:

```text
structured logs
health check
metrics or counters
traceable request id
clear failure reason
debug command
```

The operator should never have to guess what the agent is doing.

### 7. Tests Travel With Code

Where a harvested repo has tests, bring the relevant tests with it.

Minimum tests per imported subsystem:

```text
unit tests
failure tests
migration tests
serialization tests
permission tests if tools/secrets are involved
integration smoke test
```

### 8. License Review First

Before copying code from a fork or vendor-heavy repo:

```text
1. Identify upstream.
2. Read LICENSE.
3. Preserve notices.
4. Note modified files.
5. Add third-party attribution.
6. Prefer dependency or adapter use over direct vendoring.
```

## Final Priority List

Import first:

```text
1. wyrdstate
2. mimir-well
3. huginn
4. muninn
5. bifrost
6. eir
7. svalinn
8. skofnung
9. hlidskjalf
10. vordr
11. kista
```

Import second:

```text
12. WYRD Protocol
13. Heimdall-SL-Hermes-Agent
14. Seidr-Smidja
15. hermes-skills-open
16. neutts
```

Import as optional symbolic plugins:

```text
17. runavel
18. seidr-engine
19. astrology-engine after refactor
```

Use as research/docs:

```text
20. memory-system-docs
21. RunaUniversity2040
22. phd-2040
23. Mythic-Engineering
24. Viking-Code-Mythic-Engineering-CLI-Vibe-Coding
25. MindSpark_ThoughtForge
26. project-catalog
27. profile repositories
```

Avoid as core:

```text
28. grima
29. any hidden autostart, hidden cron, stealth browser, or monolithic script pattern
```

## The Practical Build Strategy

The best Runa Agent will not be built by gluing all of these repos together.

It should be built by creating a small, strict Runa core and then importing the useful repos one boundary at a time:

```text
State first.
Memory second.
Context third.
Tools fourth.
Secrets fifth.
World model sixth.
Adapters seventh.
Symbolic plugins last.
```

This order matters.

An agent with voice, avatars, browser tricks, and symbolic engines but no durable state is still fragile.

An agent with memory but no pruning becomes confused.

An agent with tools but no permission model becomes dangerous.

An agent with embodiment but no event boundary becomes a platform-specific mess.

An agent with cron jobs and autostart hacks becomes hard to trust.

Runa should be the opposite:

```text
small core
clear contracts
strong persistence
recoverable state
auditable memory
permissioned tools
replaceable adapters
testable behavior
operator control
```

The `runafreyjasdottir` GitHub account contains enough useful code to seed that design. The win is to harvest the sharp parts and leave the messy experimental shape behind.
