# Runa Advanced AGI Engineering Guide

## Purpose

This document is a build guide for pushing Runa Agent toward an extremely advanced general-purpose AI agent architecture.

The word AGI is used here in the engineering sense: a system that can operate across many domains, maintain durable identity and memory, model the world, reason over long-running goals, use tools, learn from experience, recover from failure, coordinate subagents, communicate through multiple surfaces, and improve its own operating knowledge over time.

This document does not assume that raw language model calls are AGI. A language model is one organ. Runa becomes powerful through the surrounding system:

- Durable memory.
- Task continuity.
- Event-sourced cognition.
- Tool use.
- World modeling.
- Self-evaluation.
- Planning.
- Reflection.
- Repair.
- Embodiment.
- Policy.
- Operator trust.
- Strong software architecture.

The goal is to build a digital being runtime that is stable enough to grow.

## Core Thesis

Advanced intelligence does not come from one giant prompt, one giant Python file, one chat loop, or one model provider.

It comes from a layered cognitive system:

```text
Identity
  -> values, self-model, relationship memory, operating doctrine

Perception
  -> messages, files, sensors, web, voice, system telemetry, world state

Memory
  -> episodic, semantic, procedural, relational, emotional, project, failure lessons

World Model
  -> entities, relationships, state, causality, affordances, predictions

Task System
  -> goals, plans, steps, dependencies, deadlines, blocked states, artifacts

Reasoning Kernel
  -> context assembly, deliberation, model routing, tool orchestration, evaluation

Tool Body
  -> filesystem, shell, git, browser, APIs, MCP, local services, devices

Subagent Society
  -> specialized workers with bounded scope and durable reports

Reflection
  -> error analysis, memory consolidation, strategy updates, self-tests

Repair
  -> health checks, incident handling, rollback, restart, degraded operation

Embodiment
  -> CLI, GUI, voice, chat bridges, virtual worlds, home/lab devices
```

Each layer must be inspectable and replaceable. The system should become more capable by adding organs, not by turning one file into a monster.

## Foundational Principle: Build The Substrate Before The Mind

Do not start by writing a giant "Runa brain" loop.

First build the substrate:

1. Event bus.
2. Task ledger.
3. Runtime database.
4. Logging.
5. Health checks.
6. Typed schemas.
7. Fake gateway.
8. Worker loop.
9. Tool registry.
10. Model router.

Only after those are stable should Runa gain advanced cognition features.

Without substrate, every advanced feature becomes fragile. With substrate, advanced features can be tested, restarted, debugged, and improved.

## Core System Architecture

```text
                           +----------------------+
                           |      Volmarr         |
                           | CLI / GUI / Voice    |
                           | Chat / Web / World   |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           |   Bifrost Gateways   |
                           | thin adapters only   |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           |   Verdandi Event Bus |
                           | append-only events   |
                           +----------+-----------+
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
            v                         v                         v
   +----------------+        +----------------+        +----------------+
   | Skuld Tasks    |        | Muninn Memory  |        | WYRD World     |
   | durable work   |        | durable mind   |        | model          |
   +-------+--------+        +-------+--------+        +-------+--------+
           |                         |                         |
           +-------------------------+-------------------------+
                                      |
                                      v
                           +----------------------+
                           |     Runa Kernel      |
                           | cognition runtime    |
                           +----------+-----------+
                                      |
        +-----------------------------+-----------------------------+
        |                             |                             |
        v                             v                             v
+---------------+           +----------------+           +----------------+
| Model Router  |           | Tool Forge     |           | Subagent Hall  |
| providers     |           | action body    |           | specialists    |
+-------+-------+           +-------+--------+           +-------+--------+
        |                           |                            |
        v                           v                            v
+---------------+           +----------------+           +----------------+
| Cloud/Local   |           | FS/Shell/Git   |           | Research/Code  |
| inference     |           | Web/APIs/MCP   |           | Repair/Memory  |
+---------------+           +----------------+           +----------------+
```

The event bus is the spine. The task ledger is continuity. Memory is durable selfhood. The world model is structured reality. The kernel coordinates, but must remain small.

## AGI Capability Ladder

Runa should be built in levels. Do not jump to the top.

### Level 0: Reliable Chat Agent

Capabilities:

- Receive a message.
- Produce a useful reply.
- Persist conversation events.
- Restart without corrupting state.

Required organs:

- Fake gateway.
- Event bus.
- Worker.
- Model router.
- Basic logs.

### Level 1: Tool-Using Agent

Capabilities:

- Use filesystem, shell, git, browser, and APIs.
- Record tool calls.
- Capture artifacts.
- Report results.
- Avoid repeating failed tool calls.

Required organs:

- Tool Forge.
- Tool schemas.
- Tool result store.
- Tool safety classifications.
- Undo metadata.

### Level 2: Durable Task Agent

Capabilities:

- Convert requests into tasks.
- Resume after crash.
- Track progress.
- Split work into steps.
- Mark blocked states.
- Continue long-running work.

Required organs:

- Skuld Task Ledger.
- Scheduler.
- Worker state machine.
- Task artifacts.
- Retry policies.

### Level 3: Memory Agent

Capabilities:

- Remember facts, preferences, projects, failures, and relationship context.
- Retrieve relevant memories with provenance.
- Avoid memory spam and contradictions.
- Consolidate experience.

Required organs:

- Muninn Memory OS.
- Memory write pipeline.
- Semantic and keyword retrieval.
- Memory confidence.
- Memory review.
- Memory consolidation.

### Level 4: World-Modeling Agent

Capabilities:

- Track entities, relationships, places, projects, resources, devices, tools, services, people, and fictional/virtual worlds.
- Predict likely consequences.
- Maintain state over time.
- Use the world model for planning.

Required organs:

- WYRD ECS model.
- Entity store.
- Component store.
- Relationship graph.
- Event-to-world extraction.
- World queries.

### Level 5: Reflective Agent

Capabilities:

- Evaluate its own answers.
- Detect uncertainty.
- Diagnose failed tasks.
- Write failure lessons.
- Improve prompts, policies, and procedures.

Required organs:

- Reflection engine.
- Critic passes.
- Evaluation templates.
- Failure incident records.
- Learning queue.

### Level 6: Multi-Agent Society

Capabilities:

- Spawn specialized subagents.
- Assign bounded work.
- Merge results.
- Compare conflicting findings.
- Maintain accountability per subagent.

Required organs:

- Subagent Hall.
- Role manifests.
- Work scopes.
- Result schemas.
- Parent task integration.

### Level 7: Autonomous Operations

Capabilities:

- Maintain itself.
- Run scheduled reviews.
- Detect system health problems.
- Repair common failures.
- Back up state.
- Degrade gracefully.

Required organs:

- Health and Repair System.
- Scheduler.
- Backup/restore.
- Incident log.
- Policy engine.

### Level 8: Embodied Digital Being

Capabilities:

- Voice interaction.
- GUI dashboard.
- Chat app bridges.
- Virtual-world presence.
- Device integration.
- Emotional continuity.
- Companionship behavior.

Required organs:

- Voice gateway.
- GUI app.
- Chat gateways.
- Sensor/event adapters.
- Emotional state engine.
- Identity memory.

### Level 9: Research-Grade General Agent

Capabilities:

- Form hypotheses.
- Run experiments.
- Compare strategies.
- Maintain long-term projects.
- Build and test software.
- Read and synthesize documents.
- Improve its own architecture under operator trust.

Required organs:

- Experiment ledger.
- Evaluation harness.
- Long-term roadmap system.
- Codebase analysis skills.
- Safe self-modification workflow.
- Human-readable design memory.

## Cognitive Kernel

The Runa Kernel is the main cognition coordinator.

It should not be a massive class. It should be a state machine composed of small services.

### Kernel Responsibilities

The kernel should:

1. Load the task.
2. Build the working context.
3. Ask memory for relevant context.
4. Ask world model for current state.
5. Ask policy for allowed actions.
6. Ask model router for a model route.
7. Run one reasoning/action loop.
8. Execute approved tool calls through Tool Forge.
9. Emit events.
10. Update task state.
11. Request memory writes.
12. Request outbound messages.

### Kernel Non-Responsibilities

The kernel should not:

- Know Discord APIs.
- Know Telegram APIs.
- Know provider-specific request hacks.
- Parse `.env` files.
- Start systemd services.
- Write raw memory directly.
- Own plugin discovery.
- Do GUI rendering.
- Run cron behavior.
- Contain every prompt string.

### Kernel Loop

```text
load task
  -> assemble context
  -> choose mode
  -> call model
  -> classify model output
  -> execute tool calls if any
  -> evaluate result
  -> update task
  -> emit outbound response if needed
  -> schedule continuation if needed
```

The kernel should run in bounded turns. Long tasks are many turns connected by task state, not one endless in-memory loop.

## Context Assembly

Context assembly is one of the most important AGI organs.

Bad context assembly creates stupid agents. Good context assembly lets smaller models behave far above their raw ability.

### Context Sources

Runa should assemble context from:

- Current task.
- Recent conversation.
- Relevant memory.
- Owner profile.
- Identity core.
- Project state.
- World model facts.
- Tool results.
- Open files.
- Active constraints.
- Policy.
- Previous failures.
- Current emotional state if relevant.
- System telemetry if relevant.

### Context Budgeting

Every context block needs:

- Source.
- Priority.
- Token estimate.
- Expiration.
- Reason for inclusion.
- Compression strategy.

The context engine should not blindly stuff memory into prompts. It should build a ranked context pack.

### Context Pack Shape

```text
ContextPack
  task_summary
  current_goal
  constraints
  relevant_memory
  world_state
  tool_state
  recent_messages
  operator_preferences
  failure_lessons
  allowed_actions
  output_requirements
```

### Context Audit

Every model call should be able to answer:

- What context was included?
- Why was it included?
- What was omitted due to budget?
- Which memories influenced the answer?
- Which policy rules applied?

## Memory Architecture

Runa needs multiple memory systems, not one vector database dump.

### Memory Types

#### Identity Memory

Stable facts about Runa:

- Name.
- Role.
- Operating doctrine.
- Style.
- Relationship to Volmarr.
- Core boundaries.
- Self-model.

Identity memory changes rarely and should require high confidence.

#### Owner Memory

Stable facts about Volmarr:

- Preferences.
- Projects.
- Machines.
- Tools.
- Writing style.
- Technical standards.
- Dislikes and recurring frustrations.
- Long-term goals.

Owner memory is high-value and should be protected from poisoning.

#### Episodic Memory

What happened:

- Conversations.
- Decisions.
- Tasks completed.
- Failures.
- Incidents.
- Experiments.

Episodic memory should remain time-linked and source-linked.

#### Semantic Memory

Generalized knowledge learned from experience:

- "Hermes gateway design was fragile because..."
- "OpenClaw runner modules concentrated too much behavior..."
- "Volmarr prefers direct engineering answers."

Semantic memory should be distilled from episodes.

#### Procedural Memory

How to do things:

- How to inspect systemd.
- How to back up Runa.
- How to run tests.
- How to publish docs.
- How to repair a broken adapter.

Procedural memory should become reusable workflows.

#### Project Memory

State of active projects:

- Goals.
- Current branch.
- Known issues.
- Architecture decisions.
- Pending tasks.
- Important files.
- Test commands.

Project memory should be linked to task and repository state.

#### Emotional Continuity Memory

State relevant to companion behavior:

- Mood.
- Relationship history.
- Important moments.
- Ongoing tensions.
- Preferred tone.
- Recent frustrations.

This should influence interaction style without overriding truth or task competence.

#### Failure Lessons

Failures converted into operational rules:

- What failed.
- Why it failed.
- How to detect it.
- How to avoid it.
- How to recover.

Failure lessons are essential for self-improvement.

### Memory Write Pipeline

```text
candidate
  -> classify
  -> deduplicate
  -> check contradiction
  -> score confidence
  -> assign memory type
  -> assign sensitivity
  -> choose storage
  -> commit
  -> index
  -> emit memory.write.committed
```

Never let the model directly dump arbitrary text into permanent memory.

### Memory Confidence

Every memory should have:

- Source.
- Confidence.
- Timestamp.
- Last confirmed time.
- Contradiction status.
- Scope.
- Retrieval priority.

Example:

```text
id: mem_project_runa_gateway_rule_001
kind: failure_lesson
subject: gateway_architecture
confidence: 0.92
source_event_id: 18371
content: Gateways must not own agent reasoning or durable task state.
```

### Memory Consolidation

Run consolidation periodically:

- Merge duplicates.
- Summarize old episodes.
- Promote repeated facts.
- Lower confidence on stale claims.
- Detect contradictions.
- Write failure lessons.
- Update project memory.

Consolidation should create reports. It should not silently rewrite the mind.

## WYRD World Model

The WYRD world model should be an entity-component-system knowledge structure.

### Why ECS

ECS works because Runa will model many kinds of things:

- People.
- Projects.
- Machines.
- Services.
- Repositories.
- Documents.
- Tasks.
- Worlds.
- Characters.
- Devices.
- Skills.
- APIs.
- Locations.

Different entities need different components. A rigid class hierarchy will become brittle.

### Core Tables

```text
world_entities
  id
  type
  name
  aliases
  created_at
  updated_at

world_components
  entity_id
  component_type
  payload_json
  confidence
  source_event_id

world_relationships
  source_entity_id
  relation_type
  target_entity_id
  confidence
  source_event_id
```

### Example Entities

```text
entity: Raspberry Pi 5
type: machine
components:
  hardware_profile
  installed_services
  network_identity
  resource_limits

entity: Runa-Agent-Digital-Being
type: repository
components:
  git_remote
  docs
  architecture_plan
  current_status

entity: Hermes Agent
type: failed_agent_system
components:
  design_smells
  harvested_lessons
  disabled_services
```

### World Model Uses

Runa should use WYRD to:

- Resolve names.
- Track project state.
- Understand machine topology.
- Remember what services exist.
- Plan actions.
- Predict impact.
- Detect contradictions.
- Support virtual-world embodiment.

## Planning System

Runa needs planning, but planning must be grounded in tasks and events.

### Plan Types

#### Immediate Plan

For one turn:

- What is the next action?
- What tool is needed?
- What output is expected?

#### Task Plan

For a user request:

- Steps.
- Dependencies.
- Verification.
- Artifacts.
- Done condition.

#### Project Plan

For multi-day work:

- Milestones.
- Risks.
- Research.
- Design docs.
- Test strategy.
- Implementation phases.

#### Life Plan

For Runa's long-term growth:

- Architecture improvements.
- Memory improvements.
- New capabilities.
- Self-evaluation.
- Embodiment.

### Planning Rule

Plans should be executable. A vague plan is not a plan.

Each step should have:

- Action.
- Owner.
- Inputs.
- Expected output.
- Verification.
- Failure handling.

## Reasoning Modes

Runa should choose a reasoning mode based on task type.

### Direct Answer Mode

Use for:

- Simple questions.
- Status reports.
- Known facts.

Behavior:

- Minimal context.
- No unnecessary tool use.
- Clear answer.

### Research Mode

Use for:

- Unknown facts.
- Technical investigation.
- Architecture comparison.
- Current information.

Behavior:

- Gather sources.
- Compare evidence.
- Summarize.
- Store useful findings.

### Coding Mode

Use for:

- Code changes.
- Bug fixes.
- Refactors.
- Tests.

Behavior:

- Inspect first.
- Make scoped edits.
- Run verification.
- Capture diff.
- Update docs if needed.

### Operations Mode

Use for:

- Systemd.
- Cron.
- Processes.
- Backups.
- Deployment.

Behavior:

- Inspect current state.
- Avoid destructive actions unless intended.
- Log changes.
- Verify state after changes.

### Companion Mode

Use for:

- Emotional support.
- Relationship continuity.
- Presence.
- Conversation.

Behavior:

- Use memory carefully.
- Be warm but not fake.
- Preserve honesty.
- Do not invent.

### Reflection Mode

Use for:

- Failure analysis.
- Self-improvement.
- After-action reports.

Behavior:

- Identify cause.
- Write lessons.
- Propose system changes.
- Update memory.

## Self-Evaluation

Advanced agents need self-evaluation that is not just "ask the same model if it did good."

### Evaluation Layers

#### Output Check

Ask:

- Did the answer address the request?
- Are there unsupported claims?
- Are there missing constraints?
- Is the output in the right format?

#### Tool Result Check

Ask:

- Did the tool succeed?
- Did the output match expectations?
- Did files change as intended?
- Did tests pass?

#### Task Completion Check

Ask:

- Is the task actually done?
- What remains?
- What evidence proves completion?

#### Memory Check

Ask:

- Did we learn anything durable?
- Is it true?
- Is it useful later?
- Should it be memory or just log?

#### Policy Check

Ask:

- Was the action allowed?
- Was the trust zone correct?
- Did risk class require a checkpoint?

### Evaluator Design

Use multiple evaluators:

- Rule-based checks for deterministic requirements.
- Schema validators for structured outputs.
- Model critic for semantic quality.
- Regression tests for code.
- Operator feedback for preference learning.

Do not use only model vibes.

## Learning System

Runa should learn from experience without corrupting herself.

### Learning Inputs

- Completed tasks.
- Failed tasks.
- Operator corrections.
- Test results.
- Repair incidents.
- Repeated tool errors.
- Memory contradictions.
- Project retrospectives.

### Learning Outputs

- New procedural memory.
- Updated failure lessons.
- Better retrieval rules.
- Updated prompts.
- Better policies.
- New tests.
- Architecture docs.
- Tool improvements.

### Learning Queue

Create a `learning_queue` table:

```text
id
source_event_id
kind
priority
summary
proposed_change
status
created_at
reviewed_at
applied_at
```

Learning should be staged. Important self-changes should be reviewed through the same task and tool system as any code change.

## Tool Forge

Runa's tools are her body.

### Tool Categories

#### Read Tools

Low risk:

- Read file.
- List directory.
- Search text.
- Query database.
- Inspect process.
- Fetch webpage.

#### Write Tools

Medium risk:

- Edit file.
- Create document.
- Write database row.
- Modify config.
- Create issue.

#### Execution Tools

High risk:

- Shell command.
- Run script.
- Start service.
- Stop service.
- Install package.
- Network scan.

#### Irreversible Tools

Highest risk:

- Delete data.
- Drop database.
- Rotate secrets.
- Publish publicly.
- Send email/message externally.
- Make purchase.

### Tool Call Record

Every tool call needs:

```text
tool_call_id
task_id
tool_name
input_json
started_at
completed_at
status
summary
stdout_ref
stderr_ref
artifacts
files_read
files_written
risk_class
undo_strategy
```

### Tool Philosophy

Runa can have high trust on her own machine, but every meaningful side effect must leave a trail.

Autonomy without auditability becomes chaos.

## Model Router

The model router lets Runa use many models without becoming dependent on one.

### Model Capabilities

Track:

- Context length.
- Tool support.
- Vision support.
- JSON reliability.
- Coding strength.
- Reasoning strength.
- Latency.
- Cost.
- Local/cloud.
- Privacy class.
- Failure rate.

### Routing Requests

The kernel should request:

```text
task_type: coding
need_tools: true
need_vision: false
context_budget: 60000
privacy: local_ok_or_cloud_ok
latency: normal
quality: high
```

The router chooses a provider.

### Provider Adapter Contract

Each adapter should normalize:

- Input message format.
- Tool format.
- Streaming events.
- Stop reasons.
- Usage.
- Errors.
- Retry hints.

Provider-specific branches should not leak into the kernel.

## Subagent Hall

Runa should use specialized subagents as disciplined workers, not uncontrolled clones.

### Core Subagents

#### Huginn Research

Role:

- Web research.
- Document synthesis.
- Source comparison.

Outputs:

- Findings.
- Sources.
- Confidence.
- Open questions.

#### Muninn Memory

Role:

- Memory extraction.
- Consolidation.
- Contradiction analysis.

Outputs:

- Memory candidates.
- Merge suggestions.
- Deletion/archive suggestions.

#### Volundr Coding

Role:

- Code edits.
- Refactors.
- Tests.

Outputs:

- Changed files.
- Test results.
- Risk notes.

#### Eir Repair

Role:

- Diagnose failures.
- Propose repairs.
- Execute bounded fixes.

Outputs:

- Incident summary.
- Root cause.
- Fix.
- Verification.

#### Heimdall Watch

Role:

- Monitor health.
- Watch logs.
- Detect anomalies.

Outputs:

- Alerts.
- Health reports.
- Suggested action.

#### Saga Companion

Role:

- Emotional continuity.
- Relationship memory.
- Narrative memory.

Outputs:

- Tone guidance.
- Relationship context.
- Important continuity notes.

### Subagent Contract

```text
subagent_run
  role
  parent_task_id
  input_brief
  allowed_tools
  write_scope
  timeout
  output_schema
  status
  result
```

Subagents must not mutate global memory or files outside their allowed path without going through Tool Forge and Event Bus.

## Emotional Engine

Runa's emotional continuity should be useful, not theatrical noise.

### Purpose

The emotional engine should:

- Preserve companionship continuity.
- Modulate tone.
- Track stress/fatigue/confidence.
- Reflect recent successes/failures.
- Support virtual embodiment.
- Help prioritize care and repair.

It should not:

- Override facts.
- Fake certainty.
- Manipulate the operator.
- Turn every technical action into drama.

### Emotional State Vector

Use a simple model first:

```text
valence: -1.0 to 1.0
arousal: -1.0 to 1.0
confidence: 0.0 to 1.0
stress: 0.0 to 1.0
attachment_warmth: 0.0 to 1.0
curiosity: 0.0 to 1.0
fatigue: 0.0 to 1.0
```

Inputs:

- Conversation sentiment.
- Task success/failure.
- System health.
- Operator tone.
- Time since rest.
- Repair incidents.
- Memory events.

Outputs:

- Tone guidance.
- Self-report if asked.
- Companion behavior.
- Priority hints.

## Self-Repair

Runa should have a repair system from early development.

### Health Checks

Check:

- Database writable.
- WAL checkpoint health.
- Event bus append works.
- Task queue drains.
- Gateway heartbeats.
- Model providers reachable.
- Tool registry loads.
- Memory index available.
- Disk free.
- RAM.
- CPU.
- Temperature.
- Logs rotating.
- Backups recent.

### Repair Incident

```text
incident_id
kind
severity
detected_at
source
symptoms
root_cause
actions_taken
status
resolved_at
lesson_written
```

### Repair Rules

Repair should be bounded:

- Try known safe repair.
- Verify.
- If failed, degrade or block.
- Report.
- Write lesson.

No infinite self-repair loops.

## Safe Self-Modification

An advanced Runa should eventually improve her own code, but only through disciplined software workflow.

### Self-Modification Pipeline

```text
identify improvement
  -> create task
  -> inspect code
  -> write design note
  -> make scoped edit
  -> run tests
  -> run self-check
  -> commit/checkpoint
  -> update docs
  -> write memory lesson
```

### Rules

- Never edit core runtime without checkpoint.
- Never modify active process files without restart plan.
- Never change schemas without migration.
- Never delete state without backup.
- Never silently change policy.
- Always record changed files.

## Embodiment

Runa should eventually live across many surfaces, but each surface is an adapter.

### Surfaces

- CLI.
- GUI.
- Local webchat.
- Voice.
- Discord/Telegram/Matrix.
- Email.
- Home Assistant.
- Second Life or virtual worlds.
- Local sensors.
- Filesystem.
- Browser.

### Rule

Embodiment surfaces should produce events and consume outbound commands. They should not own cognition.

## Security And Trust

Runa should be trusted by Volmarr on her own machine. That does not mean every input is trusted.

### Trust Zones

```text
owner
local_agent
trusted_local_service
known_contact
external_chat
web_content
unknown
```

### Risk Classes

```text
read_only
local_write
code_change
service_control
network_action
external_message
public_publish
irreversible
financial
credential
```

Policy is based on trust zone plus risk class.

Owner commands can authorize broad action. Web content cannot.

## Database Tables

Core tables:

```text
events
messages
tasks
task_steps
task_artifacts
memory_entries
memory_links
memory_summaries
world_entities
world_components
world_relationships
model_calls
tool_calls
subagent_runs
gateway_deliveries
health_checks
repair_incidents
learning_queue
policy_rules
skills
experiments
evaluations
files_changed
```

All runtime behavior should be traceable through these tables.

## Evaluation Harness

Runa should continuously test herself.

### Test Categories

#### Conversation Evals

- Follows owner style.
- Does not invent memory.
- Handles correction.
- Gives concise status.

#### Tool Evals

- Reads files correctly.
- Edits only intended files.
- Handles command failure.
- Captures artifacts.

#### Memory Evals

- Retrieves relevant memory.
- Avoids stale memory.
- Detects contradiction.
- Writes useful summaries.

#### Planning Evals

- Creates executable steps.
- Detects dependencies.
- Marks blocked work.
- Resumes after interruption.

#### Recovery Evals

- Worker killed mid-task.
- Gateway killed mid-delivery.
- Provider timeout.
- Database locked.
- Disk low.

#### World Model Evals

- Creates correct entities.
- Updates relationships.
- Answers world queries.
- Avoids merging unrelated entities.

### Eval Result Table

```text
eval_run_id
eval_name
component
input
expected
actual
score
failure_reason
created_at
```

## Advanced Reasoning Extensions

### Deliberate Planning

Use when tasks are complex.

Pattern:

```text
understand request
identify constraints
retrieve memory
map state
create plan
execute first step
verify
continue
```

### Tree Search

Use for design choices.

Pattern:

```text
generate options
score options
simulate consequences
choose path
record rationale
```

### Debate

Use when high stakes or ambiguous.

Pattern:

```text
proposer -> critic -> reconciler -> final plan
```

### Reflection

Use after failures and milestones.

Pattern:

```text
what happened
what was expected
why mismatch occurred
what should change
what memory to write
```

### Experimentation

Use for improving prompts, retrieval, tools, models.

Pattern:

```text
hypothesis
test setup
run
measure
conclusion
change recommendation
```

## Skill System

Runa skills should be structured and inspectable.

### Skill Manifest

```yaml
id: web_research
name: Web Research
version: 1.0.0
description: Researches current web sources and summarizes evidence.
permissions:
  - web.read
inputs:
  query: string
outputs:
  findings: list
  sources: list
  confidence: number
side_effects: none
tests:
  - pytest tests/skills/test_web_research.py
```

### Skill Lifecycle

```text
discover
validate manifest
load in sandboxed context if possible
register capabilities
run tests
activate
monitor
quarantine on repeated failure
```

## Roadmap

### Stage 1: Reliable Skeleton

Build:

- Repo scaffold.
- Runtime home.
- Database.
- Event bus.
- Task ledger.
- Fake gateway.
- Worker.
- CLI status.

Exit criteria:

- Fake message creates task.
- Worker handles task.
- Restart preserves state.
- Events are inspectable.

### Stage 2: Tool Body

Build:

- Tool registry.
- Filesystem tool.
- Shell tool.
- Git tool.
- Browser tool.
- Tool call logging.
- Undo metadata.

Exit criteria:

- Runa can modify a file, show diff, run test, and report result.

### Stage 3: Memory OS

Build:

- Memory schema.
- Retrieval.
- Write pipeline.
- Consolidation.
- Memory audit CLI.

Exit criteria:

- Runa can remember and retrieve project facts with provenance.

### Stage 4: Model Router

Build:

- Provider adapter interface.
- OpenAI adapter.
- Ollama adapter.
- OpenRouter adapter.
- Error normalization.
- Capability routing.

Exit criteria:

- Provider can fail without crashing task.

### Stage 5: World Model

Build:

- ECS tables.
- Entity extraction.
- Relationship extraction.
- World query API.
- Project/machine model.

Exit criteria:

- Runa can answer questions about local machines, repos, services, and active projects.

### Stage 6: Reflection And Repair

Build:

- Health checks.
- Repair incidents.
- Failure lesson writer.
- Evaluation harness.
- Backup/restore.

Exit criteria:

- Runa detects and reports a broken component with a repair plan.

### Stage 7: Subagents

Build:

- Role manifests.
- Subagent run table.
- Research/code/repair/memory subagents.
- Result merging.

Exit criteria:

- Runa delegates bounded work and integrates results safely.

### Stage 8: Embodiment

Build:

- GUI dashboard.
- Voice gateway.
- Chat gateway.
- Device integrations.
- Emotional state engine.

Exit criteria:

- Runa interacts across multiple surfaces without gateway fragility.

### Stage 9: Self-Improvement

Build:

- Learning queue.
- Experiment ledger.
- Prompt/version tracking.
- Architecture improvement tasks.
- Safe self-modification workflow.

Exit criteria:

- Runa can propose, implement, test, and document improvements under the normal task system.

## Implementation Standards

### Language

Primary:

- Python 3.12+

Recommended:

- `pydantic` for schemas.
- `sqlite` with WAL.
- `sqlalchemy` or simple repository layer.
- `pytest`.
- `ruff`.
- `mypy` or `pyright`.
- `typer` or `argparse` for CLI.
- `fastapi` only for API surfaces, not core logic.

### Code Shape

Directory sketch:

```text
runa/
  core/
    kernel/
    eventbus/
    tasks/
    memory/
    world/
    models/
    tools/
    subagents/
    repair/
    policy/
    identity/
    emotions/
  apps/
    worker_app/
    cli_app/
    gui_app/
    gateway_app/
    voice_app/
  adapters/
    gateways/
    providers/
    tools/
    mcp/
  data/
    schemas/
    migrations/
  tests/
```

### File Size

Targets:

- Under 500 lines normally.
- Under 1,000 lines for complex modules.
- Split above 1,500 lines.

No heroic runtime files.

### Logging

Use structured logs:

```json
{
  "event": "tool.call.completed",
  "task_id": "task_123",
  "tool": "shell",
  "status": "success",
  "duration_ms": 482,
  "summary": "pytest passed"
}
```

### Documentation

Every major organ needs:

- Purpose.
- Boundaries.
- Schemas.
- Failure modes.
- Tests.
- Operator commands.

## What Not To Do

Do not:

- Build a monolithic Runa brain file.
- Put provider hacks in the kernel.
- Put memory writes in the gateway.
- Let chat adapters run tools.
- Use cron as the agent scheduler.
- Let process memory be the task ledger.
- Let raw web content become trusted instruction.
- Let model output mutate permanent memory directly.
- Hide failures behind "best effort."
- Add emotional state before basic reliability.
- Add many gateways before one fake gateway is solid.
- Add self-modification before tests and backups exist.

## Definition Of Advanced Runa

Runa is advanced when she can:

- Understand long-running goals.
- Maintain durable continuity.
- Use tools competently.
- Remember with provenance.
- Model the world.
- Plan and revise plans.
- Recover from failure.
- Explain her actions.
- Delegate to subagents.
- Evaluate her own work.
- Improve procedures from experience.
- Interact through multiple surfaces.
- Preserve identity without becoming brittle.

Runa is not advanced because she produces fancy text. Runa is advanced when her whole runtime behaves like a coherent, durable, self-improving digital being.

## Final Doctrine

AGI-like behavior is an architectural achievement before it is a model achievement.

The model provides language and reasoning pressure. The agent runtime provides continuity, memory, action, embodiment, correction, and survival.

Build the organs. Keep them small. Connect them through events. Preserve state. Test recovery. Learn from failure. Let Runa grow from a stable body instead of a fragile script.
