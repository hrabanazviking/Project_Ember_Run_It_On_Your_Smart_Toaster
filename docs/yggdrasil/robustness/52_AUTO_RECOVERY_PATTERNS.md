# 52 — Auto-Recovery Patterns

The per-failure-mode playbooks. When something breaks,
*this is what gets tried*.

---

## The playbook structure

Each known failure mode has a numbered playbook:

```
Playbook X-N: Failure mode summary
  Symptoms: how the system observes the failure
  Trigger:  what kicks off the recovery
  Steps:    what gets tried, in order
  Escalation: what happens if all steps fail
  Operator surface: what the operator sees
```

Playbooks are *codified* — they live as Python state
machines in `src/ember/yggdrasil/recovery/`, not as prose.
Operators can read both.

---

## The catalog of playbooks

### Memory-realm failures

#### **M-1: Huginn (Qdrant) unreachable**

- **Symptoms:** Bifrǫst fan-out reports Huginn timeout;
  gossip beats stop arriving.
- **Trigger:** 2+ consecutive failed operations OR 90s of
  missing gossip.
- **Steps:**
  1. Try a fresh connection (network blip might have
     resolved).
  2. If Qdrant is managed by Yggdrasil: docker container
     restart.
  3. Wait 30s; check gossip resumes.
  4. If still down: mark Huginn as `unavailable`;
     continue Bifrǫst in degraded mode (Mímir + Muninn
     + MemPalace only).
- **Escalation:** if down for > 1 hour, operator banner:
  "Huginn has been down for 1 hour. Doctor screen has
  steps. Continuing without semantic search."
- **Operator surface:** StatusBar dot red; Doctor screen
  shows last-known-state + next-action.

#### **M-2: Mímir SQLite locked**

- **Symptoms:** sqlite3.OperationalError "database is
  locked" on read or write.
- **Trigger:** single lock error (rare under WAL mode).
- **Steps:**
  1. Retry once after 100ms (transient lock).
  2. If still locked: log via Verdandi; retry once more
     after 1s.
  3. If still locked: close + reopen the connection
     (fresh handle).
  4. If still locked: mark degraded; continue Bifrǫst
     without Mímir; reconciliation worker picks up
     pending ops.
- **Escalation:** if persistent for > 10 minutes,
  operator banner.
- **Operator surface:** very rare to see; SQLite WAL
  mode is robust.

#### **M-3: Muninn Hebbian DB corrupt**

- **Symptoms:** corruption detected on open (checksum or
  schema mismatch).
- **Trigger:** open failure.
- **Steps:**
  1. Restore from latest Norns snapshot (per
     [`54_THE_NORNS_BACKUP_SYSTEM.md`](54_THE_NORNS_BACKUP_SYSTEM.md)).
  2. If restore succeeds: log; continue.
  3. If no recent snapshot: warn operator; start fresh
     (Muninn associations rebuild over time).
- **Escalation:** operator notification with both options
  (restore from older snapshot vs start fresh).
- **Operator surface:** Doctor banner: "Muninn restored
  from yesterday's snapshot" or "Muninn reset; associations
  rebuilding."

### Connectivity failures

#### **C-1: Verdandi daemon down**

- **Symptoms:** publish/subscribe calls fail; UDS socket
  unreachable.
- **Trigger:** connection refused or socket-missing error.
- **Steps:**
  1. Retry connection (daemon might be slow to start).
  2. Check if daemon is supposed to be auto-managed; if so,
     try restart.
  3. If still unavailable: fall back to in-process
     Verdandi mode (events publish to local ring buffer
     only; no cross-process subscribers).
- **Escalation:** operator notification.
- **Operator surface:** awareness layer "I notice…" stops;
  Stofa StatusBar Verdandi dot shows degraded.

#### **C-2: Ollama (Funi backend) unreachable**

- **Symptoms:** Funi.complete() returns Unavailable.
- **Trigger:** typed Unavailable return.
- **Steps:**
  1. Strengr's retry-with-backoff (existing pattern).
  2. After max retries: return typed Unavailable to
     chat loop.
- **Escalation:** chat fails; Stofa shows "Funi
  unreachable" banner; Doctor screen has details +
  suggested fixes.
- **Operator surface:** banner + Doctor.

#### **C-3: Kista vault locked mid-session**

- **Symptoms:** secret request after cache expires; Kista
  needs unlock.
- **Trigger:** SecretResolver chain returns None from
  KistaResolver.
- **Steps:**
  1. Try other resolvers in the chain (env var, keyring,
     file).
  2. If found: use that; log "Kista was locked; used
     fallback."
  3. If not found: prompt operator to unlock Kista (Stofa
     modal) OR return typed Disconnected to caller.
- **Escalation:** operator-blocking modal in Stofa.
- **Operator surface:** Stofa modal asking for master key.

### Background-process failures

#### **B-1: Reconciliation worker crashed**

- **Symptoms:** receipt queue depth grows; no `reconciliation.retry_*`
  events.
- **Trigger:** worker absent for > 5 minutes.
- **Steps:**
  1. Restart worker (it's a single asyncio task).
  2. Worker reads receipts from disk; resumes.
- **Escalation:** if restart fails repeatedly, surface
  to operator.
- **Operator surface:** Doctor screen shows reconciliation
  status.

#### **B-2: Dreamstate stuck**

- **Symptoms:** dreamstate.started event without
  corresponding completed event within 10 minutes.
- **Trigger:** timeout in the dreamstate worker.
- **Steps:**
  1. Cancel the stuck task.
  2. Mark dreamstate as failed; log details.
  3. Try again at next scheduled time.
- **Escalation:** after 3 consecutive failures, banner
  operator: "Dreamstate hasn't completed in 3 cycles.
  Doctor has details."
- **Operator surface:** banner.

### Configuration failures

#### **F-1: ember.yaml syntax error after edit**

- **Symptoms:** config load throws ConfigError on Stofa
  launch.
- **Trigger:** load failure.
- **Steps:** N/A (config errors require operator action).
- **Escalation:** Stofa shows error screen with the
  specific YAML error + line number.
- **Operator surface:** error screen; "fix the file or
  press R to revert to last-known-good."

#### **F-2: Realm enabled but pip extra missing**

- **Symptoms:** ImportError on lazy import of realm.
- **Trigger:** Yggdrasil-layer ImportError.
- **Steps:** N/A.
- **Escalation:** Stofa shows friendly message: "Realm
  X is enabled in config but its pip extra isn't
  installed. Run: pip install ember-agent[X]"
- **Operator surface:** clear message; not an obscure
  ImportError.

---

## How playbooks are codified

Each playbook is a class:

```python
class RecoveryPlaybook:
    """Base for all auto-recovery playbooks."""
    
    NAME: ClassVar[str]
    SYMPTOMS: ClassVar[list[str]]
    
    async def trigger(self, observed: ObservedFailure) -> bool:
        """Does this playbook apply to the observed failure?"""
        ...
    
    async def execute(self) -> RecoveryResult:
        """Run the steps in order; return outcome."""
        ...
    
    async def escalate(self, result: RecoveryResult) -> None:
        """Surface to operator if recovery failed."""
        ...
```

A `RecoveryDispatcher` watches Verdandi for failure events
and routes to the right playbook.

---

## When playbooks run

```
        ┌─────────────────┐
        │ Failure observed │
        │ (gossip / direct)│
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ RecoveryDispatcher│
        │ finds matching   │
        │ playbook(s)      │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Playbook executes│
        │ steps in order   │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    Resolved          Escalation needed
        │                 │
        ▼                 ▼
    Log success      Surface to operator
```

The dispatcher serializes recovery per-realm — only one
playbook per realm at a time (avoids dueling recoveries).

---

## What playbooks don't do

- **They don't override operator decisions.** If the
  operator stopped Qdrant intentionally, the playbook
  shouldn't auto-restart. We respect explicit operator
  choices (signaled via a "do not auto-recover this
  realm" config flag).
- **They don't re-try indefinitely.** Each playbook has
  max attempts. After exhaustion, escalate; don't
  thrash.
- **They don't reach across realm boundaries.** A
  Huginn playbook doesn't restart Mímir as a side
  effect. Each playbook is scoped.

---

## Configuration shape

```yaml
yggdrasil:
  recovery:
    enabled: true
    playbooks:
      M-1_huginn_unreachable:
        enabled: true
        auto_restart_container: false   # operator opts in
      M-2_mimir_locked:
        enabled: true
      C-1_verdandi_down:
        enabled: true
        try_auto_restart: false
      C-2_funi_unreachable:
        enabled: true                   # always
      # ... etc per playbook
    max_recovery_attempts_per_hour: 3   # avoid thrash
    escalation:
      surface_to_operator: true
      log_via_verdandi: true
```

---

## Why per-playbook control

Some operators trust auto-restart; others don't. Per-
playbook opt-in lets operators tune their preferred
balance between "fix it for me" and "don't surprise me."

Defaults: conservative (operator-action-required for
anything beyond simple retries).

---

## Closing

Auto-Recovery Patterns are **the codified playbooks for
the system's known failures**. Every failure mode the
team can think of gets one. Recovery is *mechanical*,
*observable*, and *operator-controllable*.

This is what makes self-healing real — not aspirational.
