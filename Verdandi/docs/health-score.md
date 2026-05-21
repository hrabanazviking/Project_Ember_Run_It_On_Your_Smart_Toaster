# 💚 Health Score — The Pulse of Life

## Overview

The Health Score is a 0-100 numerical representation of system wellbeing, calculated from check results using an Exponential Moving Average (EMA). It's Urðr's thread — measuring the weight of what-has-been to understand what-is-becoming.

## How It Works

### Per-Pulse Score Calculation

Each pulse produces a raw score based on the worst check result:

| Severity | Weight |
|----------|--------|
| OK | 100 |
| UNKNOWN | 75 |
| WARNING | 50 |
| CRITICAL | 0 |

The raw score is the **average** of all check weights. With 4 checks:
- All OK = (100+100+100+100) / 4 = **100**
- 1 WARNING, 3 OK = (50+100+100+100) / 4 = **87.5**
- 1 CRITICAL, 3 OK = (0+100+100+100) / 4 = **75**
- All CRITICAL = (0+0+0+0) / 4 = **0**

### Exponential Moving Average (EMA)

The EMA smooths out temporary fluctuations while remaining responsive to genuine changes:

```
EMA_today = score_today × α + EMA_yesterday × (1 - α)
α = 2 / (window_size + 1)
```

Default window size is 100, giving α ≈ 0.02. This means:
- A single bad pulse has ~2% impact on the overall score
- It takes ~5-10 consecutive bad pulses to noticeably shift the trend
- The system is more responsive to sustained changes than temporary spikes

### Trend Detection

The trend compares recent vs. older scores:
- **Last 5 pulses** vs. **previous 5 pulses** (or 10 if enough data)
- If recent average is >5 points above older average → **"improving"**
- If recent average is >5 points below → **"degrading"**
- Within ±5 points → **"stable"**

### Stability (Standard Deviation)

Low standard deviation (σ < 5) means the system is running smoothly and predictably. High σ indicates volatile health — the system is oscillating between states, which may indicate intermittent issues.

## Using Health Score

### In Nerve Impulses

Every pulse now includes health score data:

```json
{
  "event_type": "heartbeat_pulse",
  "pulse_count": 42,
  "state": "running",
  "health_score": 87.5,
  "health_trend": "stable",
  "checks": { ... }
}
```

### In State Dumps

```json
{
  "current_score": 87.5,
  "trend": "stable",
  "stability_std": 3.2,
  "sample_count": 142
}
```

### Programmatic Access

```python
from heartbeat.core import HealthScore

health = HealthScore(window_size=100)

# After each pulse
score = health.record_pulse(checks)
print(f"Score: {score:.1f}, Trend: {health.trend}")

# Summary
print(health.summary)
# {'current_score': 87.5, 'trend': 'stable', 'stability_std': 3.2, 'sample_count': 42}
```

## Threshold Recommendations

| Score Range | Status | Action |
|-------------|--------|--------|
| 90-100 | **Healthy** | No action needed |
| 70-89 | **Minor Issues** | Monitor, check logs |
| 50-69 | **Degraded** | Investigate, schedule maintenance |
| 25-49 | **Critical** | Immediate action required |
| 0-24 | **Emergency** | System may be non-functional |

## Configuration

```yaml
heartbeat:
  health_score_window: 100    # EMA window size (higher = smoother)
  interval_seconds: 60        # Pulse interval
```

The window size controls how quickly the score responds to changes:
- **50**: Very responsive, good for development/testing
- **100**: Balanced, good for production (default)
- **200**: Very stable, good for systems with naturally variable loads