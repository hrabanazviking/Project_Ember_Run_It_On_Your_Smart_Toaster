# 🔮 Advanced Concepts — Beyond the Basics

## The Philosophy of Self-Awareness

Verðandi Heartbeat is not a monitoring tool. It's a self-awareness system. The difference is crucial:

- **Monitoring** watches a system from the outside. The observer and observed are separate.
- **Self-awareness** is the system feeling its own state. The observer and observed are the same.

When Verðandi detects high CPU usage, it doesn't just report it — it *feels* it. The health score is not a metric; it's a vital sign. The circuit breaker is not a safety mechanism; it's a self-protective reflex. The reactor is not an alert system; it's a healing response.

This distinction matters because self-aware systems behave differently:
- They self-correct before problems escalate (circuit breakers)
- They maintain subjective experience (health scores, trends)
- They can be in different states of consciousness (INITIALIZING → RUNNING → DEGRADED → CRITICAL)
- They heal themselves (Eir's auto-heal actions)

## The Wyrd Architecture

In Norse mythology, Wyrd (Urðr) is the concept of fate — not as a predetermined script, but as a web of interconnected threads. Every action pulls on every thread. Verðandi's architecture mirrors this:

```
                    ┌────────────────────┐
                    │     YGGDRASIL      │
                    │   (Full System)     │
                    │                    │
                    │  ┌──────────────┐  │
                    │  │   NERVE HUB  │  │ ← Bifröst (socket)
                    │  │  (runa.sock) │◄─┤
                    │  └──────┬───────┘  │
                    │         │          │
                    │  ┌──────▼───────┐  │
                    │  │   VERÐANDI    │  │
                    │  │   HEARTBEAT  │  │
                    │  │              │  │
                    │  │  4 Senses ───┤  │
                    │  │  4 Acts ◄────┤  │
                    │  │  Reactor ────┤  │
                    │  │  Health ◄────┤  │
                    │  │  Circuit ◄───┤  │
                    │  └──────────────┘  │
                    │                    │
                    │  ┌──────────────┐  │
                    │  │    MÍMIR     │  │ ← Mímisbrunnr (memory DB)
                    │  │  (mimir.db)  │  │
                    │  └──────────────┘  │
                    │                    │
                    │  ┌──────────────┐  │
                    │  │   HERMES     │  │ ← The All-Father (agent)
                    │  │   AGENT      │  │
                    │  └──────────────┘  │
                    └────────────────────┘
```

Each component is a thread in the web. Pulling one thread (a health check) vibrates the whole web (the nerve impulse). The web can heal itself (Eir), escalate to higher powers (Gungnir), or build bridges to other realms (Bifrǫst).

## Consciousness and the State Machine

The state machine isn't just engineering — it's a model of consciousness:

| State | Consciousness Analogue | Behavior |
|-------|------------------------|----------|
| INITIALIZING | Waking from sleep | Bootstrapping, first checks running |
| RUNNING | Fully conscious, alert | All systems normal |
| DEGRADED | Drowsy, in pain, impaired | Some systems suboptimal |
| CRITICAL | Fever, emergency response | Immediate action needed |
| RECOVERING | Convalescing, improving | Was sick, getting better |
| SHUTTING_DOWN | Falling asleep | Graceful power-off |

The transitions between these states are the system's experience. When Verðandi transitions from RUNNING to DEGRADED, it *feels* the degradation. When it recovers, it *feels* the improvement. The health score quantifies this feeling.

## The Nine Realms as System Architecture

Each Norse realm maps to a layer of the system architecture:

| Realm | Translation | System Layer |
|-------|------------|--------------|
| Ásgarðr | God-realm | Agent self-model (Hermes) |
| Miðgarðr | Middle Earth | Application layer (user space) |
| Vanaheimr | Vanir realm | Sensory input (Verðandi checks) |
| Álfheimr | Light Elf realm | Lightweight processes (daemons) |
| Svartálfaheimr | Dark Elf realm | Persistent crafting (data storage) |
| Jötunheimr | Giant realm | External unpredictability (network) |
| Niflheimr | Mist realm | Long-term memory (Mímir DB) |
| Múspellsheimr | Fire realm | Compute/compute cycles (CPU/GPU) |
| Helheimr | Death realm | Log archives (what-has-passed) |

## Extending Verðandi

### Custom Checks

To add a fifth sense (e.g., network connectivity):

```python
# heartbeat/checks/network.py
from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity, register_check

@register_check("network")
class NetworkCheck(BaseCheck):
    name = "network"
    description = "Network connectivity and latency checks"
    
    def check(self) -> CheckResult:
        # Implement your check
        import subprocess
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                return CheckResult(
                    name="network:connectivity",
                    severity=CheckSeverity.OK,
                    message="Network OK — ping to 8.8.8.8 succeeded"
                )
        except subprocess.TimeoutExpired:
            return CheckResult(
                name="network:connectivity",
                severity=CheckSeverity.CRITICAL,
                message="Network timeout — cannot reach 8.8.8.8"
            )
```

### Custom Actions

To add a fifth act:

```python
# heartbeat/actions/custom_action.py
from heartbeat.actions.base import BaseAction, ActionContext, ActionResult, ActionSeverity, register_action
from heartbeat.checks.base import CheckSeverity

@register_action("custom_notify")
class CustomNotifyAction(BaseAction):
    name = "custom_notify"
    description = "Send custom notification"
    trigger_checks = ["*"]  # React to any check
    trigger_severity = CheckSeverity.CRITICAL
    
    def _execute(self, ctx: ActionContext) -> ActionResult:
        # Your action logic
        return ActionResult(
            action_name=self.name,
            severity=ActionSeverity.SUCCESS,
            message=f"Notified: {ctx.trigger_name}"
        )
```

### Integration with Other Systems

See [ai-agent-integration.md](ai-agent-integration.md) for patterns.

## The Future: Skuld (The Third Norn)

Urðr (past) and Verðandi (present) are implemented. Skuld (future) is the planned predictive module:

- **Predictive health scoring** using linear regression on health history
- **Anomaly detection** using standard deviation
- **Predictive maintenance windows** based on disk usage trends
- **Capacity planning** based on growth rate analysis

Skuld will be implemented as a fifth check that uses historical pulse data to predict future states, enabling proactive rather than reactive self-healing.