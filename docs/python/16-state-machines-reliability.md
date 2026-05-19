# 16 — State Machines for Reliability

**Category:** Self-Healing & Supervision
**Runa relevance:** Skuld (task lifecycle), Heimskringla (circuit-breaker states), adapter connection lifecycle
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A **finite state machine** (FSM) makes the legal transitions of a stateful object explicit, enumerable, and machine-checkable. Instead of `if status == "pending" and other_flag and not yet_done: ...` scattered across the codebase, an FSM declares "from `pending` you can transition to `running` or `cancelled`; from `running` you can transition to `completed`, `failed`, or `interrupted`; nothing else." Illegal transitions raise instead of producing nonsense.

For Runa, FSMs are how Skuld's task lifecycle stays sane, how circuit breakers ([[07-circuit-breaker]]) reason about their states, how adapter connections move between disconnected → connecting → authenticated → ready → disconnected. Done well, FSMs eliminate a whole category of "object is in an impossible state" bugs.

## 2. Technique / mechanism

**Pattern: enum + transition table:**

```python
from enum import Enum, auto

class TaskState(Enum):
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    INTERRUPTED = auto()
    ABANDONED = auto()

# Transition table
ALLOWED_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.QUEUED:      {TaskState.RUNNING, TaskState.ABANDONED},
    TaskState.RUNNING:     {TaskState.COMPLETED, TaskState.FAILED, TaskState.INTERRUPTED},
    TaskState.INTERRUPTED: {TaskState.RUNNING, TaskState.ABANDONED},
    TaskState.FAILED:      {TaskState.RUNNING, TaskState.ABANDONED},  # retry
    TaskState.COMPLETED:   set(),  # terminal
    TaskState.ABANDONED:   set(),  # terminal
}

class IllegalTransitionError(Exception):
    def __init__(self, current: TaskState, target: TaskState):
        super().__init__(f"cannot transition from {current} to {target}")
        self.current = current
        self.target = target

class Task:
    def __init__(self, task_id: UUID):
        self.task_id = task_id
        self.state = TaskState.QUEUED
    
    def transition(self, target: TaskState) -> None:
        if target not in ALLOWED_TRANSITIONS[self.state]:
            raise IllegalTransitionError(self.state, target)
        self.state = target
```

**Adding side effects per transition:**

```python
class Task:
    def transition(self, target: TaskState, *, reason: str | None = None) -> None:
        if target not in ALLOWED_TRANSITIONS[self.state]:
            raise IllegalTransitionError(self.state, target)
        old, self.state = self.state, target
        self._on_transition(old, target, reason)
    
    def _on_transition(self, from_: TaskState, to: TaskState, reason: str | None) -> None:
        emit_event(TaskTransitioned(self.task_id, from_, to, reason))
        if to == TaskState.RUNNING:
            self.started_at = utcnow()
        elif to in {TaskState.COMPLETED, TaskState.FAILED, TaskState.ABANDONED}:
            self.completed_at = utcnow()
```

**Pattern: per-state-class polymorphism (state pattern):**

```python
from abc import ABC, abstractmethod

class TaskStateImpl(ABC):
    @abstractmethod
    def can_start(self) -> bool: ...
    @abstractmethod
    def on_complete(self) -> "TaskStateImpl": ...

class Queued(TaskStateImpl):
    def can_start(self) -> bool: return True
    def on_complete(self) -> TaskStateImpl: raise IllegalTransitionError(...)

class Running(TaskStateImpl):
    def can_start(self) -> bool: return False
    def on_complete(self) -> TaskStateImpl: return Completed()
...
```

Heavier syntax; type-checker enforces methods exist for each state. Useful when behaviour-per-state is non-trivial.

**Pattern: state machine libraries:**

- **`transitions`** (github.com/pytransitions/transitions). Most-used. Declarative.

```python
from transitions import Machine

class Task:
    states = ["queued", "running", "completed", "failed", "interrupted", "abandoned"]
    transitions = [
        {"trigger": "start", "source": "queued", "dest": "running"},
        {"trigger": "complete", "source": "running", "dest": "completed"},
        {"trigger": "fail", "source": "running", "dest": "failed"},
        {"trigger": "interrupt", "source": "running", "dest": "interrupted"},
        {"trigger": "resume", "source": ["interrupted", "failed"], "dest": "running"},
        {"trigger": "abandon", "source": ["queued", "interrupted", "failed"], "dest": "abandoned"},
    ]

task = Task()
machine = Machine(task, states=Task.states, transitions=Task.transitions, initial="queued")
task.start()      # → running
task.complete()   # → completed
task.start()      # IllegalTransitionError equivalent (raises MachineError)
```

- **`statemachine`** (github.com/fgmacedo/python-statemachine). Modern, type-friendly alternative.

**Hierarchical state machines:**

States can have sub-states. A connection's `authenticated` state might contain `idle / sending / receiving`. The `transitions` library supports HSMs.

**Persistence and state machines:**

The state field gets persisted (Skuld stores task.state). Restart reloads the state. The state machine logic re-applies to the loaded state — no special "after-restart" handling.

**State machines + reconciliation:**

`interrupted` is a designed-for-restart state. A task in `running` at the moment of crash is, on startup, transitioned to `interrupted` by the recovery code. The reconciliation loop ([[15-self-repair-reconciliation]]) then decides per-task: resume? abandon?

**State machines + auditing:**

Every transition emits an event into the audit log:
```python
emit_event(TaskTransitioned(
    task_id=self.task_id,
    from_state=old,
    to_state=new,
    reason=reason,
    timestamp=utcnow(),
))
```

The audit log can reconstruct the full lifecycle of any task. Great for debugging.

## 3. Key works / libraries

- **Harel, D.** "Statecharts: A Visual Formalism for Complex Systems." *Science of Computer Programming*, 1987. Hierarchical state machines.
- **GoF Design Patterns** — the State pattern (chapter 5).
- **`transitions`** — github.com/pytransitions/transitions.
- **`python-statemachine`** — github.com/fgmacedo/python-statemachine.
- **xstate** (JS, but influential) — modern HSM library.
- **TLA+ and Alloy** — formal-methods tools for state-machine verification.
- **Erlang's `gen_statem`** — production-grade state-machine behaviour.

## 4. Pitfalls and gotchas

- **Implicit states.** A boolean flag added later "for convenience" creates an implicit state the FSM doesn't know about. Refuse the flag; add a real state.
- **Side-effect-during-transition errors.** A side effect that fails mid-transition leaves the system in a half-state. Either make side effects retryable (and post-transition) or use a transaction.
- **State explosion.** N independent boolean attributes = 2^N states. Use composition: have multiple smaller FSMs rather than one giant one.
- **Transitions that depend on external state.** "Can transition from X to Y only if [external condition]." Either check at transition time or model the external condition as part of the state.
- **No terminal-state distinction.** Some states are *terminal* (no further transitions); others are not. Document.
- **State machine library + ORM.** transitions library has some funny interactions with SQLAlchemy and similar. Test the integration.
- **Mutation outside `transition()`.** If anything sets `task.state = X` directly, the FSM is bypassed. Use property setters or library enforcement.

## 5. Applicability to Runa

For **Skuld task lifecycle**:

- The transition table above is the starting point.
- Every transition emits a `TaskTransitioned` event.
- Crash recovery: `RUNNING` → `INTERRUPTED` transition triggered for all tasks at startup.
- Resumption policy uses transitions to advance.

For **circuit breakers ([[07-circuit-breaker]])**:

- Three states (CLOSED, OPEN, HALF_OPEN) with explicit transitions.
- Already implemented as a small FSM in §2.

For **adapter connection lifecycle**:

- States: `disconnected → connecting → authenticating → ready → reconnecting`.
- Allows per-state behaviour: in `connecting`, queue outbound messages; in `ready`, forward immediately.

For **Eldhugi emotional state**:

- Mood as state (calm / engaged / frustrated / weary) with transitions driven by deltas.
- Hierarchical: within `engaged`, sub-states for focused vs scattered.

For **Heimskringla provider state**:

- States: `healthy → throttled → quarantined → recovering`.
- Drives routing decisions.

For **Eir's reconciliation actions** ([[15-self-repair-reconciliation]]):

- Action states (idle → running → completed/failed) themselves form FSMs.

What to avoid:

- Don't model everything as a state machine. Some objects don't have meaningful state; FSM is overhead.
- Don't allow "default" transitions. Be explicit.
- Don't combine many independent state machines into one giant one. Compose.
- Don't add side effects to transitions without thinking about idempotency.

## 6. Open questions

- **Statecharts (hierarchical) vs flat.** When does the complexity earn its keep? Usually when many states share behaviour.
- **State machine verification.** Formal checking (TLA+, model checkers) for correctness is rare in Python projects. Worth it for high-stakes code.
- **Generated state-machine code.** XState's state-chart format can generate code for multiple languages. Python adoption thin.

## 7. References (curated)

- Harel (1987) — Statecharts paper.
- *Design Patterns* (Gamma et al., 1994) — State pattern.
- github.com/pytransitions/transitions — `transitions` library.
- github.com/fgmacedo/python-statemachine.
- xstate.js.org — XState (JS, but influential design).
- Companion docs: [[07-circuit-breaker]], [[11-crash-only-software]], [[15-self-repair-reconciliation]], [[17-saga-pattern]].
