"""
Verðandi Skuld Check — The Norn of the Future.

Skuld sees what is becoming. Using historical pulse data, she predicts
what WILL happen: health degradation, disk exhaustion, memory trends,
and anomaly patterns. She is the prophetic voice in the system.

Prediction methods:
  1. Linear Regression — fit a line to health scores over time
  2. Anomaly Detection — flag values >2σ from rolling mean
  3. Capacity Planning — predict when disk/memory will be exhausted
  4. Trend Classification — categorize trends as improving/stable/degrading/erratic

All predictions include confidence intervals and are stored in Mímir
for longitudinal analysis. When Skuld speaks, the system listens.

Norse metaphor: Skuld is the third Norn, the one who sees what must come.
She doesn't predict the future — she reads the threads that are already
being woven and makes visible the inevitable.
"""

import math
import sqlite3
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity
from heartbeat.paths import get_db_path

logger = logging.getLogger("verdandi.checks.skuld")


# ─────────────────────────────────────────────────────
# Prediction Engine — Statistical Models
# ─────────────────────────────────────────────────────

class LinearRegression:
    """Simple linear regression without numpy — pure Python for Pi.

    Fits y = mx + b to a series of (x, y) data points.
    Returns slope, intercept, R², and confidence.
    """

    @staticmethod
    def fit(xs: list[float], ys: list[float]) -> dict:
        """Fit a linear model and return slope, intercept, r_squared."""
        n = len(xs)
        if n < 2:
            return {"slope": 0.0, "intercept": ys[0] if ys else 0.0,
                    "r_squared": 0.0, "n": n, "confidence": "insufficient"}

        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_xx = sum(x * x for x in xs)
        sum_xy = sum(x * y for x, y in zip(xs, ys))
        sum_yy = sum(y * y for y in ys)

        denom = n * sum_xx - sum_x * sum_x
        if abs(denom) < 1e-10:
            return {"slope": 0.0, "intercept": sum_y / n,
                    "r_squared": 0.0, "n": n, "confidence": "constant"}

        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n

        # R² calculation
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in ys)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Confidence based on R² and sample size
        if r_squared > 0.8 and n >= 10:
            confidence = "high"
        elif r_squared > 0.5 and n >= 5:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "slope": round(slope, 6),
            "intercept": round(intercept, 4),
            "r_squared": round(r_squared, 4),
            "n": n,
            "confidence": confidence,
        }

    @staticmethod
    def predict(model: dict, x: float) -> float:
        """Predict y value from a fitted model."""
        return model["slope"] * x + model["intercept"]

    @staticmethod
    def predict_future(model: dict, current_x: float, target_y: float) -> Optional[float]:
        """Predict how many x-steps until y reaches target_y.

        Returns None if the slope is too flat or goes away from target.
        """
        slope = model["slope"]
        if abs(slope) < 1e-10:
            return None  # No trend, can't predict

        steps = (target_y - model["intercept"]) / slope - current_x
        if steps < 0:
            return None  # Already past target or moving away
        return round(steps, 1)


class AnomalyDetector:
    """Statistical anomaly detection using z-score on rolling windows.

    A value is anomalous if it's >2 standard deviations from the
    rolling mean. Uses pure Python — no numpy needed.
    """

    def __init__(self, window: int = 50, threshold: float = 2.0):
        self.window = window
        self.threshold = threshold

    def detect(self, values: list[float]) -> list[dict]:
        """Return list of anomaly entries with index, value, z_score."""
        anomalies = []
        if len(values) < 3:
            return anomalies

        for i in range(self.window, len(values)):
            window_vals = values[i - self.window:i]
            mean = sum(window_vals) / len(window_vals)
            variance = sum((v - mean) ** 2 for v in window_vals) / len(window_vals)
            std = math.sqrt(variance) if variance > 0 else 0.0

            if std < 1e-10:
                continue

            z_score = (values[i] - mean) / std
            if abs(z_score) > self.threshold:
                anomalies.append({
                    "index": i,
                    "value": values[i],
                    "z_score": round(z_score, 2),
                    "window_mean": round(mean, 2),
                    "window_std": round(std, 2),
                })

        return anomalies


class CapacityPredictor:
    """Predict when a resource will be exhausted based on growth rate.

    Uses linear regression on historical usage percentages to predict
    when a resource (disk, memory) will reach 100%.
    """

    @staticmethod
    def predict_exhaustion(usage_history: list[dict], threshold_percent: float = 95.0) -> dict:
        """Predict days until resource exhaustion.

        Args:
            usage_history: List of {"timestamp": float, "percent": float}.
            threshold_percent: When to alert (default 95%).

        Returns:
            Dict with prediction data, or insufficient data message.
        """
        if len(usage_history) < 5:
            return {
                "prediction": "insufficient_data",
                "data_points": len(usage_history),
                "minimum_required": 5,
            }

        xs = [i for i in range(len(usage_history))]
        ys = [h["percent"] for h in usage_history]

        model = LinearRegression.fit(xs, ys)

        if model["confidence"] == "insufficient":
            return {
                "prediction": "no_trend",
                "model": model,
                "data_points": len(usage_history),
            }

        # If slope is negative (usage decreasing), no exhaustion risk
        if model["slope"] <= 0:
            return {
                "prediction": "decreasing_or_stable",
                "current_percent": ys[-1],
                "slope": model["slope"],
                "model": model,
            }

        # How many more pulses until threshold
        steps_to_threshold = LinearRegression.predict_future(
            model, float(len(usage_history)), threshold_percent
        )

        if steps_to_threshold is None:
            return {
                "prediction": "no_exhaustion_risk",
                "current_percent": ys[-1],
                "model": model,
            }

        # Convert pulses to days (assuming ~1 pulse per minute)
        # This is a rough estimate — the caller should adjust
        days_estimate = round(steps_to_threshold / 1440, 1)  # 1440 min/day

        result = {
            "prediction": "exhaustion_predicted",
            "current_percent": ys[-1],
            "slope_per_pulse": model["slope"],
            "days_to_threshold": days_estimate,
            "threshold_percent": threshold_percent,
            "model_confidence": model["confidence"],
            "r_squared": model["r_squared"],
        }

        # Alert if exhaustion is within 7 days
        if days_estimate <= 7:
            result["urgency"] = "critical"
        elif days_estimate <= 30:
            result["urgency"] = "warning"
        else:
            result["urgency"] = "info"

        return result


# ─────────────────────────────────────────────────────
# Trend Classifier — Emotional Architecture Mapping
# ─────────────────────────────────────────────────────

class TrendClassifier:
    """Classify a health trend into an emotional state.

    Maps quantitative trends to qualitative states inspired by the
    Norse emotional architecture. This gives the system a "feeling"
    about its own health, not just a number.

    | Trend         | Emotion     | Response                |
    |---------------|-------------|-------------------------|
    | High + stable | Contentment | Maintain, no action     |
    | High + degrading | Concern  | Monitor closely         |
    | Low + stable  | Acceptance  | Sustain healing         |
    | Low + degrading | Urgency   | Escalate immediately    |
    | Erratic       | Anxiety     | Increase check freq     |
    | Improving fast | Hope      | Verify recovery         |
    """

    EMOTIONAL_STATES = {
        "contentment": {"min_health": 80, "max_std": 5, "trend": "stable"},
        "concern": {"min_health": 80, "max_std": float("inf"), "trend": "degrading"},
        "acceptance": {"max_health": 50, "max_std": 5, "trend": "stable"},
        "urgency": {"max_health": 50, "max_std": float("inf"), "trend": "degrading"},
        "anxiety": {"min_std": 15, "trend": "any"},
        "hope": {"min_slope": 1.0, "trend": "improving"},
    }

    @staticmethod
    def classify(health_scores: list[float], trend: str, stability: float) -> dict:
        """Classify current health into an emotional state.

        Args:
            health_scores: Recent health scores (0-100).
            trend: Current trend ('improving', 'stable', 'degrading').
            stability: Standard deviation of recent scores.

        Returns:
            Dict with emotion, description, and recommended response.
        """
        if not health_scores:
            return {"emotion": "unknown", "description": "No data", "response": "collect_data"}

        current = health_scores[-1]
        avg = sum(health_scores) / len(health_scores)

        # Erratic = high variability
        if stability > 15:
            return {
                "emotion": "anxiety",
                "description": "Health scores are erratic — significant variability detected",
                "response": "increase_frequency",
                "current_health": round(current, 1),
                "stability": stability,
                "trend": trend,
            }

        # Improving fast = hope
        if trend == "improving" and len(health_scores) >= 5:
            recent_slope = health_scores[-1] - health_scores[-5]
            if recent_slope > 5:
                return {
                    "emotion": "hope",
                    "description": "Health is recovering quickly — verify the improvement is real",
                    "response": "verify_recovery",
                    "current_health": round(current, 1),
                    "stability": stability,
                    "trend": trend,
                }

        # High + stable = contentment
        if avg >= 80 and stability <= 5 and trend == "stable":
            return {
                "emotion": "contentment",
                "description": "System is healthy and stable",
                "response": "maintain",
                "current_health": round(current, 1),
                "stability": stability,
                "trend": trend,
            }

        # High + degrading = concern
        if avg >= 80 and trend == "degrading":
            return {
                "emotion": "concern",
                "description": "Health is high but declining — monitor closely",
                "response": "monitor_closely",
                "current_health": round(current, 1),
                "stability": stability,
                "trend": trend,
            }

        # Low + stable = acceptance
        if avg <= 50 and stability <= 5 and trend == "stable":
            return {
                "emotion": "acceptance",
                "description": "Health is low but stable — sustain healing efforts",
                "response": "sustain_healing",
                "current_health": round(current, 1),
                "stability": stability,
                "trend": trend,
            }

        # Low + degrading = urgency
        if avg <= 50 and trend == "degrading":
            return {
                "emotion": "urgency",
                "description": "Health is low and declining — escalate immediately",
                "response": "escalate",
                "current_health": round(current, 1),
                "stability": stability,
                "trend": trend,
            }

        # Default: moderate
        return {
            "emotion": "moderate",
            "description": "System health is moderate — no clear pattern",
            "response": "observe",
            "current_health": round(current, 1),
            "stability": stability,
            "trend": trend,
        }


# ─────────────────────────────────────────────────────
# Skuld Check — The Fifth Sense
# ─────────────────────────────────────────────────────

class SkuldCheck(BaseCheck):
    """Predictive health analysis — the Norn of the Future.

    Uses historical pulse data from Mímir's database to:
      1. Predict health trend and days-to-critical
      2. Detect anomalous health scores
      3. Predict resource exhaustion (disk, memory)
      4. Classify system emotion (contentment, concern, urgency, etc.)

    This is the prophetic voice. When Skuld speaks, the system listens.
    """

    name = "prediction"
    description = "Predictive health analysis — the Norn of the Future"

    def _perform_check(self) -> CheckResult:
        """Run all predictive analyses and return combined result."""
        issues = []
        details = {}

        # 1. Health trend prediction
        trend_result = self._predict_health_trend()
        details["health_trend"] = trend_result

        if trend_result.get("prediction") == "degrading":
            days = trend_result.get("days_to_critical", "unknown")
            issues.append(("warning", f"Health degrading — ~{days} days to critical"))

        # 2. Anomaly detection
        anomaly_result = self._detect_anomalies()
        details["anomalies"] = anomaly_result

        if anomaly_result.get("anomaly_count", 0) > 3:
            issues.append(("warning", f"{anomaly_result['anomaly_count']} anomalous readings detected"))

        # 3. Capacity prediction
        capacity_result = self._predict_capacity()
        details["capacity"] = capacity_result

        # Only iterate if we got per-resource predictions (not a status dict)
        if capacity_result.get("status") != "insufficient_data":
            for resource, pred in capacity_result.items():
                if not isinstance(pred, dict):
                    continue
                if pred.get("prediction") == "exhaustion_predicted":
                    urgency = pred.get("urgency", "info")
                    days = pred.get("days_to_threshold", "?")
                    if urgency == "critical":
                        issues.append(("critical", f"{resource} exhaustion in ~{days} days"))
                    elif urgency == "warning":
                        issues.append(("warning", f"{resource} exhaustion in ~{days} days"))

        # 4. Emotional classification
        emotion_result = self._classify_emotion()
        details["emotion"] = emotion_result

        # Determine overall severity
        severity = self.worst_severity([
            CheckResult(name="skuld_sub", severity=CheckSeverity(l[0]), message=l[1])
            for l in issues
        ]) if issues else CheckSeverity.OK

        message = self.detail_message(issues) if issues else "Future looks stable — no degradation predicted"

        return CheckResult(
            name=self.name,
            severity=severity,
            message=message,
            details=details,
            sub_results=[
                CheckResult(name=f"skuld_{k}", severity=CheckSeverity.OK,
                           message=str(v)[:200])
                for k, v in details.items()
            ],
        )

    def _get_pulse_history(self, hours: int = 168) -> list[dict]:
        """Read pulse history from the state database.

        Args:
            hours: How many hours of history to fetch (default: 168 = 7 days).

        Returns:
            List of dicts with timestamp, state, health data.
        """
        db_path = self.config.get("heartbeat.db_path") or str(get_db_path())
        if not Path(db_path).exists():
            return []

        try:
            with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row
                cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
                rows = conn.execute(
                    "SELECT * FROM pulse_history WHERE timestamp > ? ORDER BY timestamp",
                    (cutoff,),
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Skuld: Could not read pulse history: {e}")
            return []

    def _predict_health_trend(self) -> dict:
        """Predict future health based on historical trends."""
        history = self._get_pulse_history(hours=168)

        if len(history) < 5:
            return {
                "prediction": "insufficient_data",
                "data_points": len(history),
                "minimum_required": 5,
            }

        # Extract health-like scores from check results
        # We approximate from the state: running=100, degraded=60, critical=20
        state_scores = {
            "running": 100, "recovering": 75, "degraded": 50,
            "critical": 20, "initializing": 50, "shutting_down": 10,
        }

        xs = list(range(len(history)))
        ys = [state_scores.get(h.get("state", "unknown"), 50) for h in history]

        model = LinearRegression.fit([float(x) for x in xs], [float(y) for y in ys])

        # Predict days to critical (score <= 30)
        days_to_critical = LinearRegression.predict_future(model, float(len(history)), 30.0)

        return {
            "prediction": "degrading" if model["slope"] < -0.05 else
                         ("improving" if model["slope"] > 0.05 else "stable"),
            "slope": model["slope"],
            "r_squared": model["r_squared"],
            "confidence": model["confidence"],
            "days_to_critical": days_to_critical,
            "data_points": len(history),
        }

    def _detect_anomalies(self) -> dict:
        """Detect anomalous health readings."""
        history = self._get_pulse_history(hours=72)

        if len(history) < 10:
            return {"anomaly_count": 0, "anomalies": [], "data_points": len(history)}

        state_scores = {
            "running": 100, "recovering": 75, "degraded": 50,
            "critical": 20, "initializing": 50,
        }
        values = [float(state_scores.get(h.get("state", "unknown"), 50)) for h in history]

        detector = AnomalyDetector(window=min(50, len(values) // 2))
        anomalies = detector.detect(values)

        return {
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:10],  # Limit to 10 most recent
            "data_points": len(history),
        }

    def _predict_capacity(self) -> dict:
        """Predict resource exhaustion for disk and memory.

        Uses the latest Eir health check data if available, otherwise
        reads from pulse history.
        """
        predictions = {}

        # Try to get recent Eir check data from pulse_history
        history = self._get_pulse_history(hours=168)
        if len(history) < 10:
            return {"status": "insufficient_data", "minimum_required": 10}

        # Parse disk/memory percentages from check JSON
        disk_history = []
        memory_history = []

        for h in history:
            checks_json = h.get("checks_json", "")
            if not checks_json:
                continue

            try:
                import json
                checks = json.loads(checks_json) if isinstance(checks_json, str) else checks_json
                health = checks.get("health", {})

                if "disk_used_percent" in str(health):
                    disk_pct = health.get("disk_used_percent")
                    if isinstance(disk_pct, (int, float)):
                        disk_history.append({"timestamp": 0, "percent": float(disk_pct)})

                if "memory_used_percent" in str(health):
                    mem_pct = health.get("memory_used_percent")
                    if isinstance(mem_pct, (int, float)):
                        memory_history.append({"timestamp": 0, "percent": float(mem_pct)})
            except (json.JSONDecodeError, TypeError):
                continue

        # Re-index timestamps
        for i, entry in enumerate(disk_history):
            entry["timestamp"] = float(i)
        for i, entry in enumerate(memory_history):
            entry["timestamp"] = float(i)

        if len(disk_history) >= 5:
            predictions["disk"] = CapacityPredictor.predict_exhaustion(disk_history)

        if len(memory_history) >= 5:
            predictions["memory"] = CapacityPredictor.predict_exhaustion(memory_history)

        if not predictions:
            predictions["status"] = "no_resource_data"

        return predictions

    def _classify_emotion(self) -> dict:
        """Classify the current system state into an emotional category."""
        history = self._get_pulse_history(hours=24)

        if len(history) < 3:
            return {"emotion": "unknown", "description": "Insufficient data for emotional classification"}

        state_scores = {
            "running": 100, "recovering": 75, "degraded": 50,
            "critical": 20, "initializing": 50,
        }

        scores = [float(state_scores.get(h.get("state", "unknown"), 50)) for h in history]

        # Determine trend
        if len(scores) >= 5:
            recent = scores[-5:]
            older = scores[-10:-5] if len(scores) >= 10 else scores[:5]
            diff = (sum(recent) / len(recent)) - (sum(older) / len(older))
            trend = "improving" if diff > 5 else ("degrading" if diff < -5 else "stable")
        else:
            trend = "stable"

        # Calculate stability
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        stability = round(variance ** 0.5, 1)

        return TrendClassifier.classify(scores, trend, stability)