# 🔮 Skuld — The Third Norn (Roadmap)

## ✅ v0.3.0 — Skuld (RELEASED 2026-05-11)

All Skuld features have been implemented! See README changelog for details.

- ✅ **SkuldCheck** — Predictive health analysis (linear regression, anomaly detection, capacity prediction, emotional classification)
- ✅ **Vör Action** — Pre-emptive healing that acts on Skuld's predictions
- ✅ **Emotional Architecture** — 7 emotional states mapped from health + trend + stability
- ✅ **Maintenance Windows** — Scheduled maintenance suppresses non-critical actions
- ✅ **Prometheus Metrics** — 8 metrics exposed via `/metrics` HTTP endpoint
- ✅ **pulse_metrics table** — Per-pulse health scores, trends, emotional states

### Original Planned Features (v0.3.0 — "Skuld")

### 1. Predictive Health Scoring

Using the pulse history stored in SQLite, Skuld will perform linear regression to predict health trends:

```python
class SkuldCheck(BaseCheck):
    """Predict future system health based on historical trends."""
    
    name = "skuld"
    description = "Predictive health analysis"
    
    def check(self) -> CheckResult:
        history = self._get_health_history(days=7)
        slope = self._linear_regression(history)
        
        # If health is degrading at 2 points/day, predict CRITICAL in N days
        if slope < -0.5:
            days_to_critical = self._predict_days_to_critical(history)
            return CheckResult(
                name="predictive:health_trend",
                severity=CheckSeverity.WARNING,
                message=f"Health trending DOWN. Estimated {days_to_critical} days to critical.",
                details={"slope": slope, "days_to_critical": days_to_critical}
            )
```

### 2. Anomaly Detection

Statistical anomaly detection on check results:

```python
def detect_anomaly(self, values: list[float], window: int = 50) -> bool:
    """Detect if latest value is anomalous (>2σ from mean)."""
    if len(values) < window:
        return False
    recent = values[-window:]
    mean = sum(recent) / len(recent)
    std = (sum((x - mean) ** 2 for x in recent) / len(recent)) ** 0.5
    latest = values[-1]
    return abs(latest - mean) > 2 * std
```

### 3. Capacity Planning

Disk and memory usage prediction:

```python
def predict_disk_full(self, disk_history: list) -> dict:
    """Predict when disk will be full based on growth rate."""
    # Linear regression on disk usage
    # Return: estimated days until 100% full
```

### 4. Pre-emptive Healing

Instead of waiting for CRITICAL, act on WARNING + negative trend:

```yaml
reactor:
  rules:
    - trigger: "predictive:health_trend"
      severity: warning
      action: pre_emptive_restart
      cooldown_seconds: 86400  # Once per day
```

### 5. Scheduled Maintenance Windows

Integrate with Urðr to plan maintenance during low-impact windows.

## Planned Features (v0.4.0 — "Valhalla")

### Distributed Heartbeat

Multiple Verðandi instances sharing a nerve hub:

```
Node A (Pi) ──► nerve hub ──┐
                            ├──► Aggregated Pulse
Node B (Laptop) ──► nerve hub ──┤
                            │
Node C (Server) ──► nerve hub ──┘
```

### REST API

HTTP API for remote monitoring (with authentication):

```python
@app.get("/api/v1/health")
async def get_health():
    return {"health_score": 87.5, "state": "running", "checks": {...}}

@app.get("/api/v1/health/history")
async def get_health_history(hours: int = 24):
    return {"history": [...], "trend": "stable"}
```

### Prometheus Metrics Exporter

```python
# Standard Prometheus metrics
verdandi_health_score 87.5
verdandi_pulse_total 42
verdandi_check_severity{check="eir"} 0  # OK
verdandi_circuit_breaker_state{check="eir"} 0  # CLOSED
```

### Emotional Architecture

Mapping health trends to emotional states:

| Health Trend | Emotion | Response |
|-------------|---------|----------|
| High + stable | Contentment | Maintain, no action |
| High + degrading | Concern | Monitor closely |
| Low + stable | Acceptance | Sustain healing |
| Low + degrading | Urgency | Escalate immediately |
| Erratic | Anxiety | Increase check frequency |
| Improving fast | Hope | Verify recovery |

## Version Naming Convention

Following the Norse theme:

| Version | Name | Norse Meaning | Focus |
|---------|------|--------------|-------|
| v0.1.0 | Bein | Skeleton | Project structure |
| v0.2.0 | Andi | Spirit | Self-awareness |
| v0.3.0 | Skuld | The Future | Prediction |
| v0.4.0 | Valhöll | Valhalla | Distributed |
| v1.0.0 | Yggdrasil | World Tree | Production-ready |