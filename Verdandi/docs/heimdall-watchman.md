# 🔮 Heimdall — The Watchman's Eye

> *"I am Heimdall, the White God, the Watchman of the Gods. I need less sleep than a bird, I see equally well by night as by day, and I hear the grass growing and the wool on a sheep's back."*

## Who Is Heimdall?

Heimdall is the Norse god who stands at the Bifröst, the rainbow bridge between Midgard and Asgard. He is the ultimate watchman — ever-vigilant, ever-aware, the first to see danger coming and the last to sound the alarm. In the Verðandi architecture, **Heimdall is the awareness layer** — the system's capacity to perceive, correlate, and predict.

While the four Senses (Eir, Huginn, Mímir, Urðr) detect *what is happening now*, Heimdall detects *what is about to happen* and *what patterns are forming over time*. He sees the grass growing. He hears the future approaching.

## Architecture

```
                     ┌─────────────────┐
                     │    BIFRÖST      │
                     │  (nerve hub)    │
                     └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────┴─────┐ ┌──────┴──────┐ ┌──────┴──────┐
    │  FOUR SENSES  │ │  HEIMDALL   │ │  FOUR ACTS  │
    │  (detection)  │ │ (awareness)  │ │  (response) │
    │               │ │              │ │             │
    │  • Eir        │ │  • Watch     │ │  • Mjölnir  │
    │  • Huginn     │ │  • Learn     │ │  • Gungnir  │
    │  • Mímir      │ │  • Predict  │ │  • Bifrǫst  │
    │  • Urðr       │ │  • Alert     │ │  • Eir      │
    └───────────────┘ └──────────────┘ └─────────────┘
```

## Heimdall's Powers

### 1. Watch — Continuous Pattern Recognition

Heimdall watches the stream of nerve impulses and identifies patterns that individual checks might miss. A single elevated CPU reading is a blip. Three consecutive elevated readings across different checks is a pattern.

**What he watches:**
- Health score trends (improving, stable, degrading)
- Circuit breaker state transitions (closed → open → half-open)
- Check result correlations (does disk full predict CPU elevated?)
- Action frequency patterns (is Eir healing the same thing repeatedly?)

**How this works in code:** The `HealthScore` class maintains an exponential moving average (EMA) of check results, with trend detection and stability metrics. The `CircuitBreaker` class prevents cascading failures with configurable thresholds.

### 2. Learn — Adaptive Thresholds

Heimdall learns what "normal" looks like for *your specific system*. On a Pi with 4GB RAM, 70% usage is different than on a workstation with 32GB. Over time, Heimdall adjusts thresholds based on observed baselines.

**Current implementation:** Check thresholds are configurable via YAML, with sensible defaults for Pi hardware.

**Planned:** Baseline auto-learning — the system observes its own check results over a calibration period and suggests optimal thresholds.

### 3. Predict — Early Warning System

Heimdall detects degrade patterns before they become critical. If the health score has been trending downward for 5 consecutive pulses, he fires a `health_degrading` nerve impulse even before any individual check hits CRITICAL.

**Current implementation:** The `HealthScore.trend` property returns "improving", "stable", or "degrading" based on EMA comparison.

**Planned:** Predictive scoring with linear regression on health score history, configurable prediction horizons.

### 4. Alert — Multi-Channel Notification

Heimdall doesn't just detect — he communicates. When he identifies a pattern that requires attention, he fires nerve impulses through multiple channels:

- **Nerve hub socket** — Real-time stream to other agents
- **State database** — Persistent record for auditing
- **Log file** — Human-readable audit trail
- **(Planned) Webhook** — Push notifications to external services
- **(Planned) Email** — Critical alerts to administrators

## The Circuit Breaker Pattern

Named after Heimdall's role as gatekeeper of the Bifröst — when the rainbow bridge is under attack, he closes it. When a check or action fails repeatedly, the circuit breaker opens and prevents further calls, giving the system time to recover.

```
CLOSED ──(5 failures)──► OPEN ──(cooldown 5min)──► HALF_OPEN ──(success)──► CLOSED
                              │                          │
                              │◄──(failure)──────────────┘
```

### Configuration

```yaml
checks:
  eir:
    circuit_breaker_threshold: 5    # Failures before opening
    circuit_breaker_cooldown: 300   # Seconds before half-open
```

## Health Score Explained

The health score is a 0-100 number that represents the overall system health as a single value. It uses an Exponential Moving Average (EMA) to smooth out temporary fluctuations while remaining responsive to genuine changes.

**How it's calculated:**
- Each check result maps to a weight: OK=100, WARNING=50, CRITICAL=0, UNKNOWN=75
- The average of all check weights = the pulse score
- EMA = (pulse_score × α) + (previous_EMA × (1-α))
- α = 2 / (window_size + 1), default window=100

**What the numbers mean:**
- **90-100**: System is healthy and stable
- **70-89**: Minor issues, system is functional but degrading
- **50-69**: Significant problems, attention needed
- **0-49**: Critical state, immediate intervention required

**Trend detection:**
- The system compares the average of the last 5 pulses against the average of the 5 pulses before that
- If the difference is > 5 points, trend is "improving" or "degrading"
- Within ±5 points, trend is "stable"

## Integration with Other Systems

### Mímir (Memory)

Heimdall stores health snapshots in Mímir for long-term trend analysis. This enables queries like "what was the health score trend over the last 7 days?" and "how often does the Pi throttle check fail?"

### Urðr (Schedule)

Heimdall can schedule predicted maintenance windows based on observed patterns — e.g., "disk usage trend suggests we'll hit 90% in approximately 14 days."

### Hermes Agent

Heimdall nerve impulses are received by Hermes through the nerve hub, enabling the AI agent to react to system health changes in real time. This is the foundation of self-healing AI awareness.

---

*Heimdall sees all. He hears all. And now, so does Verðandi.*