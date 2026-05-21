# 🔄 State Machine Deep Dive

## The Six States

Verðandi's daemon operates as a finite state machine with six states representing different levels of system consciousness:

```
    INITIALIZING
         │
         ▼
      RUNNING ◄──────┐
      │    │          │
      │    │          │ RECOVERING
      │    ▼          │     ▲
      │  DEGRADED ────┤     │
      │    │           │     │
      │    ▼           │     │
      │  CRITICAL ─────┘     │
      │    │                 │
      │    └─────improving───┘
      │
      ▼
   SHUTTING_DOWN
```

## Transition Rules

| From | To | Condition |
|------|----|-----------|
| INITIALIZING | RUNNING | First pulse completes successfully |
| RUNNING | DEGRADED | Any check returns WARNING |
| RUNNING | CRITICAL | Any check returns CRITICAL |
| DEGRADED | CRITICAL | Any check returns CRITICAL |
| DEGRADED | RECOVERING | All checks return OK |
| CRITICAL | RECOVERING | All checks return OK |
| RECOVERING | RUNNING | Second consecutive pulse with all OK |
| Any | SHUTTING_DOWN | SIGTERM received |

## UNKNOWN Severity Handling

When a check returns UNKNOWN severity (circuit breaker open, check error):
- Does NOT cause state transition to DEGRADED or CRITICAL
- Preserves the current state
- If currently INITIALIZING, transitions to RUNNING (first pulse completed)

This prevents a failing check from dragging the entire system into CRITICAL state. The circuit breaker handles the failed check independently.

## Hysteresis (Recovery Buffer)

The system doesn't immediately transition from RECOVERING to RUNNING. It requires **two consecutive OK pulses**. This prevents flapping between states when a system is on the boundary.

Example timeline:
```
Pulse 1: All OK → RUNNING
Pulse 2: CPU high → DEGRADED
Pulse 3: All OK → RECOVERING
Pulse 4: All OK → RUNNING (confirmed recovery)
```

Without hysteresis, Pulse 3 would immediately go back to RUNNING, potentially masking an intermittent issue.

## State Persistence

The current state is persisted to the SQLite database (`heartbeat_state` table) on every pulse. On daemon restart, the state is initialized to INITIALIZING regardless of the persisted state — the first pulse will determine the actual state.

However, the `pulse_count` and `last_healthy_pulse` timestamps ARE restored from the database, providing continuity across restarts.

## Nerve Impulses on State Change

When the daemon state changes, a `heartbeat_state_change` impulse is fired:

```json
{
  "event_type": "heartbeat_state_change",
  "old_state": "running",
  "new_state": "degraded",
  "pulse_count": 42
}
```

This allows external systems to react to state changes in real time.