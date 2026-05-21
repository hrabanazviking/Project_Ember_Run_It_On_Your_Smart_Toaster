# 🏗️ Verðandi Architecture

## The Norn of Becoming

Verðandi — "what is becoming" — is one of the three Norns who tend the well Urðarbrunnr beneath Yggdrasil. While Urðr (past) and Skuld (future) bookend existence, Verðandi is the present moment: always in motion, always becoming. This is the perfect name for a system that continuously *becomes* — taking its pulse, sensing its environment, reacting to change.

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    VERÐANDI HEARTBEAT                         │
│                    (Hjartsláttur Daemon)                      │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │  PULSE LOOP  │  │ STATE MACHINE│  │  CIRCUIT BREAKERS   │ │
│  │             │  │              │  │                     │ │
│  │  interval   │  │ INITIALIZING │  │  Per-check:        │ │
│  │  + jitter   │  │    ↓         │  │  CLOSED → OPEN →   │ │
│  │             │  │  RUNNING      │  │  HALF_OPEN → CLOSED│ │
│  │  ┌───────┐ │  │    ↓         │  │                     │ │
│  │  │ SENSES│ │  │ DEGRADED     │  │  Failure threshold: 5│ │
│  │  │ CHECKS│ │  │    ↓         │  │  Cooldown: 300s    │ │
│  │  └───┬───┘ │  │ CRITICAL     │  └─────────────────────┘ │
│  │      │     │  │    ↓         │                            │
│  │      │     │  │ RECOVERING   │  ┌─────────────────────┐ │
│  │      ▼     │  └──────────────┘  │   HEALTH SCORE      │ │
│  │  ┌───────┐ │                    │                     │ │
│  │  │REACTOR│ │  ┌──────────────┐  │  0-100 EMA        │ │
│  │  └───┬───┘ │  │  NERVE HUB   │  │  Trend detection   │ │
│  │      │     │  │  (runa.sock)  │  │  Stability (σ)     │ │
│  │      ▼     │  └──────┬───────┘  └─────────────────────┘ │
│  │  ┌───────┐ │         │                                  │
│  │  │ACTIONS│ │         ▼                                  │
│  │  └───────┘ │  ┌──────────────┐                          │
│  │            │  │  STATE DB    │                          │
│  └─────────────┘  │(heartbeat.db)│                         │
│                    └──────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. HeartbeatDaemon (`heartbeat/core.py`)

The main daemon class that orchestrates everything. It:
- Runs the pulse loop with configurable interval and jitter
- Manages the state machine (INITIALIZING → RUNNING → DEGRADED → CRITICAL → RECOVERING)
- Coordinates checks, health scoring, circuit breakers, and actions
- Publishes nerve impulses for external observers
- Persists state to SQLite for crash recovery

### 2. Four Senses (`heartbeat/checks/`)

Each sense is a `BaseCheck` subclass that implements a `check()` method returning a `CheckResult`:

| Sense | Module | Namespace | What |
|-------|--------|-----------|------|
| Eir | `eir.py` | `health:` | CPU, RAM, disk, thermal throttle |
| Huginn | `huginn.py` | `project:` | Git dirty, unpushed, branch divergence |
| Mímir | `mimir.py` | `memory:` | DB integrity, size, row counts |
| Urðr | `urdr.py` | `schedule:` | Upcoming events, deadlines |

### 3. Reactor (`heartbeat/reactor.py`)

The check → action bridge. When a check returns CRITICAL or WARNING, the reactor looks up matching actions and executes them (or dry-runs them).

Rule format:
```yaml
reactor:
  rules:
    - trigger: "memory:mimir_db"
      severity: critical
      action: auto_heal
      cooldown_seconds: 1800
```

### 4. Four Acts (`heartbeat/actions/`)

| Act | Module | Trigger | What |
|-----|--------|---------|------|
| Mjölnir | `mjolnir_action.py` | Health CRITICAL | Restart services, clean caches |
| Gungnir | `gungnir_action.py` | Any CRITICAL | Send escalation notifications |
| Bifrǫst | `bifrost_action.py` | State change | Forward to external services |
| Eir | `eir_action.py` | Memory CRITICAL | Heal corrupted DBs, truncate malformed logs |

### 5. Circuit Breaker (`heartbeat/core.py`)

Prevents cascading failures. Each check has its own breaker:
- CLOSED: Normal, calls pass through
- OPEN: Too many failures, calls rejected
- HALF_OPEN: Cooldown elapsed, one probe allowed

### 6. Health Score (`heartbeat/core.py`)

EMA-based 0-100 health score with trend detection:
- Score = average of check severity weights
- EMA smooths fluctuations
- Trend: improving/stable/degrading
- Stability: standard deviation of recent scores

### 7. Signal Handler (`heartbeat/signals.py`)

POSIX signal handling:
- SIGTERM/SIGINT → graceful shutdown
- SIGHUP → reload configuration
- SIGUSR1 → force pulse
- SIGUSR2 → dump state to JSON

### 8. Configuration (`heartbeat/config.py`)

YAML configuration with dot-notation access:
```python
config.get("heartbeat.interval_seconds", 60)
config.get("checks.eir.thresholds.cpu_warning_percent", 80)
```

### 9. Paths (`heartbeat/paths.py`)

File-location-agnostic path resolution:
- Respects XDG_BASE_DIR on Linux
- Falls back to `~/.hermes/state/` defaults
- All paths configurable via environment variables

### 10. State Database (`heartbeat.db`)

SQLite database with two tables:
- `heartbeat_state`: Key-value store for current state
- `pulse_history`: Rolling 1000-row history of pulse results

## Data Flow

```
1. Pulse loop fires (interval + jitter)
2. For each check:
   a. Circuit breaker allows? → Yes: run check; No: skip (use cached)
   b. Check runs → CheckResult
   c. Result stored in state
   d. Circuit breaker updated
3. Health score calculated from all results
4. State machine updated based on worst severity
5. Reactor evaluates rules → executes matching actions
6. Nerve impulse published to socket (fallback: JSONL file)
7. State persisted to SQLite
8. Sleep until next pulse
```

## Error Handling Philosophy

1. **Graceful degradation**: A check that fails returns UNKNOWN, not CRITICAL
2. **Circuit breakers**: Repeated failures silence the check temporarily
3. **Fallback paths**: If the nerve hub socket is unavailable, write to file
4. **State persistence**: All state is persisted to SQLite, enabling crash recovery
5. **Jitter**: Random sleep interval variation prevents thundering herd problems