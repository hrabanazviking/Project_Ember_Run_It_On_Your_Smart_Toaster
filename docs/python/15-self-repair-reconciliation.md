# 15 — Self-Repair Systems and Reconciliation Loops

**Category:** Self-Healing & Supervision
**Runa relevance:** Eir (the entire subsystem), Muninn integrity, Skuld task recovery
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A **reconciliation loop** observes the *current state* of a system and compares it to the *desired state*, then takes actions to drive current toward desired. The pattern was crystallised by Kubernetes (the "controller" pattern, originating earlier in Borg and Omega) and has become the foundation of modern infrastructure-as-code, GitOps, and self-healing systems. The core insight: instead of issuing imperative "do this thing" commands and hoping they succeed, *declare what should be true* and let a loop continually drive reality toward that declaration.

For Runa, the reconciliation pattern is what gives Eir teeth. Eir doesn't just *monitor* — Eir *acts*: a corrupted index gets rebuilt; a quarantined adapter gets retried; a stuck Skuld task gets unstuck; a missing config file gets regenerated from defaults. Each action is the outcome of "I observe X is true; X should be Y; here is the action that closes the gap." Done well, the loop produces a system that *heals itself* without operator intervention for the long tail of operational nicks.

## 2. Technique / mechanism

**The reconciliation loop:**

```
       ┌─────────────────────────────────────┐
       │  Loop forever:                       │
       │                                       │
       │   1. Observe current state           │
       │   2. Compute desired state           │
       │   3. Diff current vs desired         │
       │   4. For each diff:                  │
       │       - Decide action                │
       │       - Apply (idempotently)         │
       │       - Log outcome                  │
       │   5. Wait <interval>                 │
       │                                       │
       └─────────────────────────────────────┘
```

**Properties of a good reconciliation loop:**

- **Idempotent actions** ([[05-idempotency-design]]) — re-running the loop doesn't accumulate effects.
- **Continuous (not event-driven only).** Event-driven action misses things; periodic full-reconciliation catches them.
- **Convergent.** Each iteration brings the system *closer* to desired, even if it can't fully converge in one step.
- **Self-limiting.** Actions have rate limits; bug in the loop doesn't take everything down.
- **Observable.** Every action logged; current state and desired state both queryable.

**Python skeleton:**

```python
import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)

@dataclass
class Reconciler:
    name: str
    interval_seconds: float
    observe: Callable[[], Awaitable["State"]]
    desired: Callable[[], Awaitable["State"]]
    actions: list["Action"]
    
    async def run(self):
        while True:
            try:
                await self._tick()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("%s: reconciler error: %r", self.name, exc, exc_info=exc)
            await asyncio.sleep(self.interval_seconds)
    
    async def _tick(self):
        current = await self.observe()
        wanted = await self.desired()
        for action in self.actions:
            if action.is_needed(current, wanted):
                if action.is_rate_limited():
                    logger.info("%s: action %s rate-limited; skipping", self.name, action.name)
                    continue
                logger.info("%s: applying action %s", self.name, action.name)
                try:
                    await action.apply(current, wanted)
                    action.record_success()
                except Exception as exc:
                    logger.error("%s: action %s failed: %r", self.name, action.name, exc)
                    action.record_failure()
```

**Action design:**

```python
class Action(Protocol):
    name: str
    
    def is_needed(self, current: State, wanted: State) -> bool: ...
    def is_rate_limited(self) -> bool: ...
    async def apply(self, current: State, wanted: State) -> None: ...
    def record_success(self) -> None: ...
    def record_failure(self) -> None: ...
```

Each action is small, named, single-purpose. Rate limiting prevents loop bugs from causing runaway behaviour.

**Concrete examples:**

### Action: rebuild stale vector index

```python
class RebuildStaleIndexAction:
    name = "rebuild_muninn_vector_index"
    
    def __init__(self, muninn: Muninn, max_stale_seconds: float = 86400):
        self.muninn = muninn
        self.max_stale_seconds = max_stale_seconds
        self._last_run = 0.0
    
    def is_needed(self, current, wanted) -> bool:
        return (
            self.muninn.vector_index.last_rebuilt_at < 
            time.monotonic() - self.max_stale_seconds
        )
    
    def is_rate_limited(self) -> bool:
        # At most once per day
        return time.monotonic() - self._last_run < 86400
    
    async def apply(self, current, wanted) -> None:
        await self.muninn.rebuild_vector_index()
    
    def record_success(self):
        self._last_run = time.monotonic()
```

### Action: unstick a stale Skuld task

```python
class UnstickTaskAction:
    name = "unstick_stale_task"
    stuck_threshold_seconds = 600  # 10 minutes
    
    def is_needed(self, current, wanted) -> bool:
        return any(
            task.status == "in_progress" and
            (time.monotonic() - task.started_at) > self.stuck_threshold_seconds
            for task in current.tasks
        )
    
    async def apply(self, current, wanted) -> None:
        for task in current.tasks:
            if (task.status == "in_progress" and
                (time.monotonic() - task.started_at) > self.stuck_threshold_seconds):
                await self.skuld.mark_task_interrupted(task.task_id)
                # Resumption policy decides next step
```

### Action: re-enable a quarantined adapter

```python
class TryReEnableAdapterAction:
    name = "try_re_enable_adapter"
    
    def is_needed(self, current, wanted) -> bool:
        return any(adapter.quarantined for adapter in current.adapters)
    
    async def apply(self, current, wanted) -> None:
        for adapter in current.adapters:
            if adapter.quarantined and adapter.quarantined_for_seconds > 300:
                # Try a health check
                if await adapter.health_check():
                    adapter.unquarantine()
                else:
                    adapter.extend_quarantine()
```

**The Kubernetes-style declarative model:**

Make desired state explicit and external:

```python
class DesiredState:
    """Loaded from config; could be edited at runtime."""
    enabled_adapters: set[str]
    target_quants_per_provider: dict[str, str]
    max_muninn_size_gb: float
    backup_retention_days: int

class CurrentState:
    """Observed from the system."""
    running_adapters: set[str]
    actual_quants_per_provider: dict[str, str]
    muninn_size_gb: float
    backups_present: list[Backup]
```

The reconciler diffs and acts. Config changes become declarative — edit config, the loop reconciles.

## 3. Key works / libraries

- **Burns, B. et al.** "Borg, Omega, and Kubernetes." *Communications of the ACM*, 2016. The controller pattern's intellectual lineage.
- **Hightower, K., Burns, B., Beda, J.** *Kubernetes: Up & Running*, 3rd ed., O'Reilly 2022. Practical introduction.
- **Operator Framework (CoreOS / Red Hat)** — the productionised controller pattern at scale.
- **Argo CD, Flux** — GitOps reconcilers; instructive design.
- **Terraform's resource model** — declarative + reconciliation at infrastructure level.
- **`kopf`** — github.com/nolar/kopf. Python framework for writing Kubernetes operators (a serious reconciler).
- **`watchdog`** library (Python, gorakhargosh/watchdog) — filesystem-watcher; useful for one slice of observation.
- **`apscheduler`** — github.com/agronholm/apscheduler. Periodic-task scheduler for reconciler tick scheduling.

## 4. Pitfalls and gotchas

- **Non-idempotent action.** Running the loop twice produces twice the effect. The most common reconciler bug.
- **Reconciliation amplification.** Loop sees state X; takes action A; A's side effect changes state to Y; loop sees Y; takes action B; B's side effect → X; oscillation. Mitigate with hysteresis / damping.
- **Slow observation.** Observing current state takes 30s; loop runs every 10s; backed-up loop iterations queue. Decouple observation interval from action interval.
- **Acting on stale observation.** Observe → wait → act on potentially-changed state. Use compare-and-set semantics.
- **Cascading actions.** One reconciler triggers another. Easy to get into runaway loops. Be careful about interaction.
- **No rate limiting.** Reconciler loop bug → loops fire actions at full speed → real damage. Always rate-limit.
- **Operator confusion.** A reconciler that "fixes" things the operator was investigating undermines them. Loud logging is essential.
- **Unrecoverable state.** Some states the loop *can't* fix. It should know and escalate, not loop forever.

## 5. Applicability to Runa

For **Eir (`core/repair/`)**:

- Eir is one or more reconciliation loops over Runa's state.
- Per-subsystem reconcilers: Muninn-reconciler, Skuld-reconciler, adapters-reconciler, breakers-reconciler.
- Each has its own interval and action set.

For **Muninn reconciliation actions**:

- Vector index missing or wrong-dimension → rebuild.
- Embedding model mismatch → schedule re-embedding migration.
- Database integrity check fails → restore from latest snapshot + escalate.
- Disk usage > threshold → trigger compression of cold episodes.

For **Skuld reconciliation actions**:

- Stuck `in_progress` tasks → mark interrupted; let resumption policy decide.
- Failed task with retries-exhausted → escalate to `Notified`.

For **adapter reconciliation actions**:

- Quarantined adapter quiet > 5min → try re-enable.
- Adapter authenticated but no traffic > 1hr → ping.

For **Heimskringla reconciliation actions**:

- Per-provider breaker stuck OPEN > 30min → try probe + log.
- All providers down → trigger fallback to local-only + alert.

For **systemic actions**:

- Backups older than retention threshold → prune.
- Audit log rotated and old files compressible → compress.
- `~/.runa/cache/` exceeding size limit → evict.

For **desired-state from config**:

- `config/runa.yaml#repair.targets` declares desired state.
- Operator edits config; reconciler converges.

What to avoid:

- Don't write reconcilers that take destructive actions silently. Verbose logging; operator-visible.
- Don't reconcile faster than the underlying system can respond.
- Don't make reconcilers depend on each other directly. Each observes and acts independently.
- Don't let a reconciler loop on a state it can't fix. Escalate after N failures.

## 6. Open questions

- **Reconciler priorities.** Multiple actions needed; which first? Topological ordering, dependency declarations, or simple per-action order.
- **Cross-reconciler coordination.** When two reconcilers want to act on related state, how to avoid races. Locking? Compare-and-set?
- **Reconciler testing.** Property-based tests with state-machine model are appealing; complex to set up.
- **Operator override.** When a human is actively debugging, reconcilers should sometimes pause. "Maintenance mode" is the K8s equivalent.

## 7. References (curated)

- *Communications of the ACM*, "Borg, Omega, and Kubernetes," 2016.
- kubernetes.io/docs/concepts/architecture/controller/ — official controller pattern.
- github.com/nolar/kopf — Python operator framework.
- argo-cd.readthedocs.io / fluxcd.io — GitOps reconcilers.
- terraform.io — declarative resource model.
- *Kubernetes Patterns* (Ibryam and Huss, O'Reilly 2019) — patterns book.
- Companion docs: [[05-idempotency-design]], [[14-health-checks]], [[16-state-machines-reliability]].
