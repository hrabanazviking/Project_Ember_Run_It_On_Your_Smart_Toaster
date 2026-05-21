# 🛡️ Circuit Breaker Pattern in Verðandi

## Overview

The Circuit Breaker pattern prevents cascading failures in distributed and self-monitoring systems. Named after Heimdall's role as gatekeeper of the Bifröst — when the bridge is under attack, he closes it. When a check or action fails repeatedly, the circuit breaker opens and prevents further calls, giving the system time to recover.

## Why Circuit Breakers?

Without circuit breakers, a single failing component can consume excessive resources:
- **Repeated health checks** on a database that's already known to be down waste I/O and add latency
- **Repeated action attempts** on an unresolvable issue create log spam and delay real responses
- **Resource exhaustion** — every check costs CPU, memory, and I/O cycles
- **Cascade failures** — one slow check can delay all subsequent checks

## How It Works

```
CLOSED ──(5 consecutive failures)──► OPEN ──(300s cooldown)──► HALF_OPEN ──(success)──► CLOSED
                                       │                            │
                                       │◄──(failure)───────────────┘
```

### States

| State | Behavior |
|-------|----------|
| **CLOSED** | Normal operation. All calls pass through. Failure counter starts at 0. |
| **OPEN** | Circuit is tripped. All calls are rejected fast. No actual check/action is executed. The last known result is used instead, or UNKNOWN if no previous result exists. |
| **HALF_OPEN** | Cooldown has elapsed. One probe call is allowed. If it succeeds, the circuit closes. If it fails, the circuit opens again for another cooldown period. |

### Configuration

Each check and action can have its own circuit breaker settings:

```yaml
checks:
  eir:
    enabled: true
    circuit_breaker_threshold: 5    # Failures before opening (default: 5)
    circuit_breaker_cooldown: 300    # Seconds before half-open probe (default: 300)

  mimir:
    enabled: true
    circuit_breaker_threshold: 3     # More sensitive for memory checks
    circuit_breaker_cooldown: 600    # Longer cooldown for DB operations

reactor:
  circuit_breaker_threshold: 10     # Actions are more tolerant
  circuit_breaker_cooldown: 180     # But recover faster
```

### Statistics

Each circuit breaker tracks:
- `failure_count`: Current consecutive failures (resets on success)
- `success_count`: Total successes since last reset
- `total_calls`: Total calls attempted (including rejected ones)
- `total_failures`: Total failures ever recorded
- `state`: Current state (closed, open, half_open)

These stats are included in nerve impulses and state dumps for monitoring.

## Implementation

The CircuitBreaker class is defined in `heartbeat/core.py`:

```python
from heartbeat.core import CircuitBreaker

# Create a breaker with custom settings
breaker = CircuitBreaker(
    failure_threshold=5,    # Trip after 5 failures
    cooldown_seconds=300,   # 5 minute cooldown
    name="check_eir"
)

# Before executing a check
if not breaker.allow():
    # Circuit is open — skip the check, use cached result
    return cached_result

# After the check completes
if result.severity == CheckSeverity.UNKNOWN:
    breaker.record_failure()
else:
    breaker.record_success()

# Check stats
print(breaker.stats)
# {'name': 'check_eir', 'state': 'closed', 'failure_count': 0, ...}
```

## Best Practices

1. **Set appropriate thresholds**: Checks that hit external resources (network, DB) should have lower thresholds (3) because they're more likely to fail. CPU/disk checks can have higher thresholds (5-7) because they're more reliable.

2. **Set appropriate cooldowns**: External resource checks should have longer cooldowns (300-600s) because the underlying issue takes time to resolve. Local checks can have shorter cooldowns (60-120s).

3. **Monitor breaker state**: Include circuit breaker stats in your monitoring dashboards. A breaker that's frequently opening suggests a systemic issue.

4. **Don't disable breakers**: If a check is constantly tripping its breaker, fix the underlying issue rather than disabling the breaker. The breaker is telling you something important.

5. **Test half-open behavior**: In integration tests, verify that a breaker transitions correctly through all three states: closed → open → half_open → closed.