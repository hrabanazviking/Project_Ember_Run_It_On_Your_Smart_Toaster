# 17 — Saga Pattern and Compensating Transactions

**Category:** Self-Healing & Supervision
**Runa relevance:** Skuld (multi-step task orchestration), kernel turns with multiple side effects, Smiðja tool chains
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A **saga** (Garcia-Molina and Salem, 1987) is a sequence of local transactions that together implement a larger logical operation across systems that don't share a database. Each step is a small, independently-committable transaction. If a later step fails, the saga doesn't roll back — there's nothing global to roll back to — instead it runs **compensating transactions** that undo or counterbalance the previous steps. "Charged the card; couldn't ship the item; refund the card" is a saga; the refund is the compensation.

For Runa, sagas are how multi-step actions stay correct in the face of partial failure. A kernel turn that retrieves from Muninn, asks Heimskringla, calls Smiðja, writes to memory, sends a reply — that's a saga. If the reply send fails, we don't want to silently leave the memory writes. The saga discipline says: declare what each step does, declare what undoes it (or marks it as "no longer effective"), and let the saga engine drive forward or compensate.

## 2. Technique / mechanism

**The Saga structure:**

```
   Step 1 ──► Step 2 ──► Step 3 ──► Step 4 ──► success
     │          │          │           │
     │ on       │          │           │
     │ failure  │          │           │
     ▼          ▼          ▼           ▼
   Compensate Compensate Compensate Compensate
   step 1    step 2     step 3     step 4
```

If step N fails, run compensations for steps N-1, N-2, ..., 1 in reverse order.

**Simple Python implementation:**

```python
from dataclasses import dataclass, field
from typing import Awaitable, Callable

@dataclass
class SagaStep:
    name: str
    action: Callable[[], Awaitable[None]]
    compensation: Callable[[], Awaitable[None]] | None = None

class SagaFailure(Exception):
    def __init__(self, failed_step: str, cause: Exception, compensation_errors: list[Exception]):
        super().__init__(f"saga failed at {failed_step}: {cause}")
        self.failed_step = failed_step
        self.cause = cause
        self.compensation_errors = compensation_errors

@dataclass
class Saga:
    name: str
    steps: list[SagaStep] = field(default_factory=list)
    _completed: list[SagaStep] = field(default_factory=list)
    
    def add_step(self, name: str, action, compensation=None):
        self.steps.append(SagaStep(name=name, action=action, compensation=compensation))
    
    async def run(self) -> None:
        for step in self.steps:
            try:
                await step.action()
                self._completed.append(step)
            except Exception as exc:
                logger.warning("saga %s failed at step %s: %s", self.name, step.name, exc)
                comp_errors = await self._compensate()
                raise SagaFailure(step.name, exc, comp_errors) from exc
    
    async def _compensate(self) -> list[Exception]:
        errors: list[Exception] = []
        for step in reversed(self._completed):
            if step.compensation is None:
                continue
            try:
                await step.compensation()
            except Exception as exc:
                logger.error("compensation for %s failed: %s", step.name, exc)
                errors.append(exc)
        return errors
```

**Example: a kernel turn as a saga:**

```python
async def execute_turn(heard: Heard) -> None:
    saga = Saga(name=f"turn-{heard.event_id}")
    
    episode_id = uuid4()
    saga.add_step(
        "record_input_episode",
        action=lambda: muninn.write_episode(input_episode(heard, episode_id)),
        compensation=lambda: muninn.delete_episode(episode_id),  # or mark as void
    )
    
    saga.add_step(
        "call_model",
        action=lambda: heimskringla.complete(...),
        compensation=None,  # model calls are read-only; nothing to compensate
    )
    
    reply_id = uuid4()
    saga.add_step(
        "record_reply_episode",
        action=lambda: muninn.write_episode(reply_episode(reply_id)),
        compensation=lambda: muninn.delete_episode(reply_id),
    )
    
    saga.add_step(
        "send_reply",
        action=lambda: adapter.send(reply.text),
        compensation=lambda: adapter.send_correction("(Previous reply was incomplete)"),
    )
    
    await saga.run()
```

If `send_reply` fails, both episodes are deleted (or marked void); compensation for the send step might also send an apology, depending on how far it got.

**Crucial property: compensations should be idempotent.**

If a compensation itself fails mid-execution, retry might run it twice. Idempotency ([[05-idempotency-design]]) is the substrate.

**Choreography vs orchestration:**

- **Orchestration** (the example above): a central coordinator runs the saga. Easier to reason about; central failure point.
- **Choreography:** each step listens for events and emits events. No central coordinator. More resilient; harder to debug.

For an in-process agent like Runa, orchestration is the right default. Distributed sagas use choreography.

**Saga persistence:**

For long-running sagas (Skuld tasks), the saga state itself is persistent:

```python
@dataclass
class PersistedSaga:
    saga_id: UUID
    name: str
    steps_completed: list[str]
    current_step: str | None
    status: Literal["running", "compensating", "completed", "failed"]
    ...
```

A crash mid-saga restarts and resumes from `current_step` (with idempotency-protection from re-running completed steps).

**The "Sagas Are Just State Machines" insight:**

A saga is a particular kind of state machine ([[16-state-machines-reliability]]) where the states are "completed steps 1..N" and transitions are step actions. Compensations are the transitions taken on failure. Often it's helpful to implement sagas using FSM machinery.

## 3. Key works / libraries

- **Garcia-Molina, H. and Salem, K.** "Sagas." SIGMOD 1987. The foundational paper.
- **Vasters, C., Roever, T.** "Saga." cloud-design-patterns.azure.net. Microsoft's articulation.
- **`temporal-python`** — github.com/temporalio/sdk-python. Temporal workflows include saga-like compensation.
- **Microservices.io** — Chris Richardson's saga write-up. Excellent practitioner reference.
- **`aiosaga`** — small Python saga libraries.
- **Camunda, Conductor, Cadence** — workflow engines that implement sagas.

## 4. Pitfalls and gotchas

- **Compensation does not always perfectly undo.** Sending a refund undoes a charge, but sending an apology email doesn't unsend an earlier email. Sometimes compensation is "best-effort acknowledgement that something went wrong."
- **Side effects across systems.** If step 3 sends an email and step 4 fails, the email is in the recipient's inbox forever. Compensation can send a correction, not retract.
- **Half-completed compensations.** Compensation for step N fails. Now you have neither a completed saga nor a clean state. Logging + escalation.
- **Reading partial state during saga execution.** A query mid-saga sees inconsistent state. Either tolerate this (eventual consistency) or use SAGA_ACTIVE markers.
- **Non-idempotent compensation.** Running compensation twice may double-refund. Idempotency required.
- **Forgetting to compensate completed steps.** Easy to miss when adding new steps.
- **Compensation for "internal" steps.** Some saga steps are pure-compute and need no compensation. Mark `compensation=None` explicitly; don't omit.
- **Saga timeouts.** A saga that hangs at step 2 can leave step 1's effects in place forever. Set deadlines.

## 5. Applicability to Runa

For **Skuld task orchestration**:

- Long tasks broken into steps; each step is a saga step.
- Per-task persisted saga state allows resume after crash.
- Compensation runs if task is `failed` or `abandoned`.

For **kernel turns**:

- Multi-side-effect turns use saga discipline.
- Most turns are read-heavy and don't need compensation; but turns that *do* mutate (memory writes + external messages) follow saga pattern.

For **Smiðja tool chains**:

- A skill that calls multiple tools forms a saga: tool1 → tool2 → tool3. If tool3 fails, compensations for tool1 and tool2 (if any) run.

For **Eldhugi**:

- Emotional-state updates are conceptually compensable (rare, but: "I felt warmth for X; X turned out to be bad faith; reduce the warmth").

For **adapter sends**:

- Sending a message to a chat adapter is the most-common compensation-relevant step. If a later step fails, compensation might send a correction or simply log "the agent meant to do more but couldn't."

What to avoid:

- Don't write sagas for trivial work. Overkill for single-step operations.
- Don't write compensations that perform new business logic. Compensation reverses or marks-void; it shouldn't add new effects.
- Don't ignore failed compensations. Escalate.
- Don't make compensation depend on state that may have changed since the original step. Compensation should be based on what the step *did*, not on what's now true.

## 6. Open questions

- **Saga design for natural-language outputs.** "Compensating" for an LLM-generated reply that's already in the user's chat is fundamentally messy. Apologies and corrections are the available tools.
- **Concurrent sagas.** When multiple sagas operate on overlapping state, conflicts. Locking, optimistic concurrency, or "designed for races" semantics.
- **Saga visualisation.** Long sagas with branches are hard to debug. Trace visualisation helps.

## 7. References (curated)

- Garcia-Molina and Salem (1987) — Sagas paper.
- microservices.io/patterns/data/saga.html — Chris Richardson's overview.
- learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga — Microsoft's Saga article.
- temporal.io/docs/concepts/what-is-a-workflow — Temporal's workflow as saga.
- Companion docs: [[05-idempotency-design]], [[16-state-machines-reliability]], [[22-event-sourcing-cqrs]] (research corpus).
