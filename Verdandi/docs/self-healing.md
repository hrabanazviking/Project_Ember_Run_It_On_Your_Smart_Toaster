# 🔐 Self-Healing Architecture

## Overview

Verðandi's self-healing system is modeled after the immune system: detect, diagnose, respond, and adapt. When the daemon detects a problem (through its four Senses), it can automatically respond (through its four Acts), protected by circuit breakers that prevent the cure from being worse than the disease.

## The Healing Pipeline

```
Detection → Diagnosis → Decision → Execution → Verification
   (Sense)   (Check)     (Reactor)   (Act)      (Next Pulse)
```

### 1. Detection (The Four Senses)

Each sense monitors a specific domain:
- **Eir**: Hardware health (CPU, RAM, disk, temperature)
- **Huginn**: Software health (git repos, project status)
- **Mímir**: Data health (database integrity, file validity)
- **Urðr**: Temporal health (schedules, deadlines, events)

### 2. Diagnosis (Check Severity)

Each detection produces a severity rating:
- **OK**: Everything is within normal parameters
- **WARNING**: Approaching a threshold — monitor closely
- **CRITICAL**: Threshold exceeded — action may be needed
- **UNKNOWN**: Could not determine — fallback behavior

### 3. Decision (The Reactor)

The reactor evaluates check results against configured rules:
```yaml
reactor:
  rules:
    - trigger: "memory:mimir_db"
      severity: critical
      action: auto_heal
      cooldown_seconds: 1800
```

If the rule matches, the corresponding action is triggered (unless in cooldown or dry-run mode).

### 4. Execution (The Four Acts)

| Act | Action | What It Heals |
|-----|--------|---------------|
| Eir | `auto_heal` | Corrupted DBs, malformed JSONL, missing directories |
| Mjölnir | `restart_services` | Stuck or crashed processes |
| Gungnir | `notify` | Escalation notifications |
| Bifrǫst | `forward_status` | External system integration |

### 5. Verification (Next Pulse)

The next pulse verifies whether the healing action worked:
- If check returns OK → healing succeeded, state transitions toward RUNNING
- If check still CRITICAL → healing may have failed, state stays DEGRADED/CRITICAL
- Circuit breaker prevents repeated healing attempts (e.g., don't try to heal every 60 seconds)

## Eir's Healing Capabilities

### Database Repair

When Mímir detects a database integrity failure:

1. **Backup**: Create a `.db.recover` copy of the corrupted file
2. **Preserve**: Move the original to `.db.corrupt` for forensics
3. **Recover**: Dump all recoverable data from the backup into a new database
4. **Verify**: Integrity check on the new database
5. **Report**: ActionResult with affected/failed targets

```python
# Example: Eir healing a corrupted Mímir DB
result = eir_action._heal_database(
    db_path=Path("~/.mimir/mimir.db"),
    name="mimir_well"
)
# Returns: True (healed), False (could not heal)
```

### JSONL Repair

Malformed lines in JSONL files (conversation log, nerve feed) are removed:

```python
result = eir_action._heal_jsonl(
    Path("~/.hermes/state/conversation_log.jsonl")
)
# Removes lines that fail json.loads(), keeps valid lines
```

### Directory Repair

Ensures all required directories exist:

```python
from heartbeat.paths import ensure_dirs
ensure_dirs()  # Creates ~/.hermes/state/{,run,logs}
```

## Circuit Breaker Protection

Self-healing must not make things worse. Circuit breakers prevent:

1. **Healing loops**: Don't try to heal the same DB corruption every 60 seconds
2. **Resource exhaustion**: Don't spend CPU/IO on checks that are known to be failing
3. **Cascade failures**: A failing check shouldn't delay or crash other checks

```
CLOSED ←──(success)── HALF_OPEN ←──(cooldown)── OPEN
  │                        │                      │
  └──(5 failures)─────────┘                      │
            └────────(failure)────────────────────┘
```

## State Machine Transitions

```
                    ┌──────────────┐
                    │ INITIALIZING │
                    └──────┬───────┘
                           │ (first pulse)
                    ┌──────▼───────┐
              ┌─────┤    RUNNING    ├─────┐
              │     └──────┬───────┘     │
              │            │             │
     (any WARNING)    (all OK)    (any CRITICAL)
              │            │             │
              │      ┌─────▼─────┐       │
              │      │ RECOVERING│       │
              │      └─────┬─────┘       │
              │            │             │
              │    (still OK)           │
              │            │             │
       ┌──────▼───────┐   │       ┌─────▼───────┐
       │   DEGRADED   │◄──┘       │  CRITICAL   │
       └──────┬───────┘           └─────┬───────┘
              │                         │
              └──(all OK)──►RUNNING◄─────┘
                           │
                    (any WARNING)
                           │
                    ┌──────▼───────┐
                    │   DEGRADED   │
                    └──────────────┘
```

## Best Practices

1. **Start with dry-run mode** (`reactor.dry_run: true`) — see what actions *would* fire before enabling them
2. **Set appropriate cooldowns** — don't restart a service every 60 seconds
3. **Monitor circuit breaker stats** — a frequently opening breaker indicates a systemic issue
4. **Verify after healing** — always check that the next pulse shows improvement
5. **Keep the `.db.corrupt` files** — they're forensic evidence for diagnosing root causes