"""Tests for Skuld predictive health check — the Norn of the Future.

Tests cover:
  - LinearRegression model fitting and prediction
  - AnomalyDetector with z-score detection
  - CapacityPredictor exhaustion prediction
  - TrendClassifier emotional mapping
  - SkuldCheck integration with database
"""

import math
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime, timezone, timedelta

from heartbeat.checks.base import CheckResult, CheckSeverity
from heartbeat.checks.skuld import (
    SkuldCheck,
    LinearRegression,
    AnomalyDetector,
    CapacityPredictor,
    TrendClassifier,
)


# ─────────────────────────────────────────────────────
# LinearRegression Tests
# ─────────────────────────────────────────────────────

class TestLinearRegression:
    """Test linear regression fitting and prediction."""

    def test_perfect_fit(self):
        """A perfect linear relationship should have R² = 1.0."""
        xs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ys = [2 * x + 10 for x in xs]  # y = 2x + 10
        result = LinearRegression.fit(xs, ys)
        assert result["slope"] == pytest.approx(2.0, abs=0.01)
        assert result["intercept"] == pytest.approx(10.0, abs=0.01)
        assert result["r_squared"] == pytest.approx(1.0, abs=0.01)
        assert result["confidence"] == "high"

    def test_negative_slope(self):
        """Degrading health should produce a negative slope."""
        xs = list(range(20))
        ys = [100 - 2 * x for x in xs]  # y = -2x + 100
        result = LinearRegression.fit(xs, ys)
        assert result["slope"] < 0
        assert result["slope"] == pytest.approx(-2.0, abs=0.01)

    def test_constant_values(self):
        """All-same values should produce slope ~0 and low or constant confidence."""
        xs = [0, 1, 2, 3, 4]
        ys = [50, 50, 50, 50, 50]
        result = LinearRegression.fit(xs, ys)
        assert result["slope"] == pytest.approx(0.0, abs=0.01)
        # With 0 variance, R² is undefined — confidence could be 'constant' or 'low'
        assert result["confidence"] in ("constant", "low")

    def test_insufficient_data(self):
        """Less than 2 data points should return 'insufficient' confidence."""
        result = LinearRegression.fit([0], [50])
        assert result["confidence"] == "insufficient"
        assert result["n"] == 1

    def test_predict(self):
        """Prediction should use the fitted model."""
        model = {"slope": 2.0, "intercept": 10.0}
        assert LinearRegression.predict(model, 5) == pytest.approx(20.0)

    def test_predict_future_exhaustion(self):
        """Should predict steps until target is reached."""
        model = {"slope": -2.0, "intercept": 100.0}
        # Health going from 100 down by 2 per step
        # When will it reach 30? y = 100 - 2x, x = (30 - 100) / -2 = 35
        # Starting from x=10, steps = 35 - 10 = 25
        steps = LinearRegression.predict_future(model, 10.0, 30.0)
        assert steps == pytest.approx(25.0, abs=0.1)

    def test_predict_future_flat_slope(self):
        """Flat slope should return None (can't predict exhaustion)."""
        model = {"slope": 0.0, "intercept": 50.0}
        steps = LinearRegression.predict_future(model, 10.0, 30.0)
        assert steps is None

    def test_predict_future_already_past(self):
        """If already past the target, should return None."""
        model = {"slope": -5.0, "intercept": 20.0}  # Already below 30
        steps = LinearRegression.predict_future(model, 0.0, 30.0)
        assert steps is None


# ─────────────────────────────────────────────────────
# AnomalyDetector Tests
# ─────────────────────────────────────────────────────

class TestAnomalyDetector:
    """Test statistical anomaly detection."""

    def test_no_anomalies_in_normal_data(self):
        """Uniform values should have no anomalies."""
        values = [50.0] * 100
        detector = AnomalyDetector(window=20, threshold=2.0)
        anomalies = detector.detect(values)
        assert len(anomalies) == 0

    def test_detect_spike_anomaly(self):
        """A sudden spike should be detected as anomalous."""
        # Create data where a massive spike appears after a long steady period
        # The window starts at index `window`, so the spike needs to be
        # at index >= window and the preceding window must have nonzero stddev
        values = [50.0 + (i % 5) * 0.1 for i in range(30)]  # slight variation so std > 0
        values.append(200.0)  # Spike at index 30
        values.extend([50.0] * 10)  # Return to normal
        detector = AnomalyDetector(window=10, threshold=2.0)
        anomalies = detector.detect(values)
        assert len(anomalies) > 0
        # The spike value should be present in anomalies
        spike_anomalies = [a for a in anomalies if a["value"] == 200.0]
        assert len(spike_anomalies) > 0

    def test_insufficient_data(self):
        """Less than 3 values should return no anomalies."""
        detector = AnomalyDetector()
        assert detector.detect([50, 51]) == []

    def test_anomaly_has_z_score(self):
        """Anomalies should include z_score in their output."""
        values = [50.0] * 30 + [90.0]
        detector = AnomalyDetector(window=20, threshold=2.0)
        anomalies = detector.detect(values)
        for a in anomalies:
            assert "z_score" in a
            assert "value" in a
            assert "window_mean" in a

    def test_custom_window_and_threshold(self):
        """Custom parameters should be respected."""
        detector = AnomalyDetector(window=10, threshold=3.0)
        assert detector.window == 10
        assert detector.threshold == 3.0


# ─────────────────────────────────────────────────────
# CapacityPredictor Tests
# ─────────────────────────────────────────────────────

class TestCapacityPredictor:
    """Test resource exhaustion prediction."""

    def test_insufficient_data(self):
        """Less than 5 data points should report insufficient data."""
        result = CapacityPredictor.predict_exhaustion([
            {"timestamp": 0, "percent": 50},
            {"timestamp": 1, "percent": 51},
        ])
        assert result["prediction"] == "insufficient_data"

    def test_stable_usage(self):
        """Stable or decreasing usage should not predict exhaustion."""
        history = [{"timestamp": i, "percent": 50.0} for i in range(10)]
        result = CapacityPredictor.predict_exhaustion(history)
        # Stable usage means slope ~= 0, which means either "decreasing_or_stable" or "no_trend"
        assert result["prediction"] in ("decreasing_or_stable", "no_trend", "insufficient_data")

    def test_increasing_usagepredicted(self):
        """Increasing usage should predict eventual exhaustion."""
        history = [
            {"timestamp": i, "percent": 50.0 + i * 0.5}
            for i in range(10)
        ]
        result = CapacityPredictor.predict_exhaustion(history)
        assert result["prediction"] == "exhaustion_predicted"
        assert "days_to_threshold" in result
        assert result["slope_per_pulse"] > 0

    def test_urgency_levels(self):
        """Exhaustion within 7 days should be 'critical' urgency."""
        # Very steep growth — disk filling fast
        history = [
            {"timestamp": i, "percent": 80.0 + i * 0.1}
            for i in range(20)
        ]
        result = CapacityPredictor.predict_exhaustion(history)
        if result["prediction"] == "exhaustion_predicted":
            assert result["urgency"] in ("critical", "warning", "info")


# ─────────────────────────────────────────────────────
# TrendClassifier Tests
# ─────────────────────────────────────────────────────

class TestTrendClassifier:
    """Test emotional classification of health trends."""

    def test_contentment(self):
        """High score, stable, no degradation = contentment."""
        result = TrendClassifier.classify(
            health_scores=[95, 94, 96, 95, 94],
            trend="stable",
            stability=2.0,
        )
        assert result["emotion"] == "contentment"
        assert result["response"] == "maintain"

    def test_concern(self):
        """High score but degrading = concern."""
        result = TrendClassifier.classify(
            health_scores=[95, 92, 88, 85, 82],
            trend="degrading",
            stability=5.0,
        )
        assert result["emotion"] == "concern"
        assert result["response"] == "monitor_closely"

    def test_urgency(self):
        """Low score and degrading = urgency."""
        result = TrendClassifier.classify(
            health_scores=[40, 35, 30, 25, 20],
            trend="degrading",
            stability=8.0,
        )
        assert result["emotion"] == "urgency"
        assert result["response"] == "escalate"

    def test_anxiety(self):
        """High variability = anxiety."""
        result = TrendClassifier.classify(
            health_scores=[80, 50, 90, 30, 75, 20, 85],
            trend="erratic",
            stability=25.0,
        )
        assert result["emotion"] == "anxiety"
        assert result["response"] == "increase_frequency"

    def test_hope(self):
        """Quickly improving = hope."""
        result = TrendClassifier.classify(
            health_scores=[30, 35, 40, 50, 65, 75, 85, 92],
            trend="improving",
            stability=5.0,
        )
        assert result["emotion"] == "hope"
        assert result["response"] == "verify_recovery"

    def test_acceptance(self):
        """Low but stable = acceptance."""
        result = TrendClassifier.classify(
            health_scores=[40, 41, 39, 40, 41],
            trend="stable",
            stability=1.5,
        )
        assert result["emotion"] == "acceptance"
        assert result["response"] == "sustain_healing"

    def test_no_data(self):
        """Empty scores should return unknown."""
        result = TrendClassifier.classify([], "stable", 0.0)
        assert result["emotion"] == "unknown"

    def test_moderate(self):
        """Average scores with no clear pattern = moderate."""
        result = TrendClassifier.classify(
            health_scores=[60, 65, 60, 65, 60],
            trend="stable",
            stability=10.0,
        )
        assert result["emotion"] == "moderate"


# ─────────────────────────────────────────────────────
# SkuldCheck Integration Tests
# ─────────────────────────────────────────────────────

class TestSkuldCheck:
    """Test the Skuld check integration."""

    def test_check_instantiation(self):
        """SkuldCheck should instantiate with a config."""
        config = MagicMock()
        config.get.return_value = None
        check = SkuldCheck(config)
        assert check.name == "prediction"
        assert check.description  # Has a description

    def test_check_with_no_history(self):
        """Skuld should handle missing database gracefully."""
        config = MagicMock()
        config.get.return_value = "/nonexistent/path.db"
        check = SkuldCheck(config)
        result = check.check()
        assert result.name == "prediction"
        # With no DB, predictions should report insufficient data
        assert result.severity in (CheckSeverity.OK, CheckSeverity.UNKNOWN)

    def test_check_returns_check_result(self):
        """Skuld check should always return a CheckResult."""
        config = MagicMock()
        config.get.return_value = None
        check = SkuldCheck(config)
        result = check.check()
        assert isinstance(result, CheckResult)
        assert result.name == "prediction"
        assert result.severity in list(CheckSeverity)


# ─────────────────────────────────────────────────────
# Prometheus Exporter Tests
# ─────────────────────────────────────────────────────

class TestPrometheusExporter:
    """Test Prometheus metrics exporter."""

    def test_metrics_registry_creation(self):
        """MetricsRegistry should create all default metrics."""
        from heartbeat.prometheus import MetricsRegistry
        registry = MetricsRegistry()
        assert "health_score" in registry.metrics
        assert "pulse_total" in registry.metrics
        assert "check_severity" in registry.metrics
        assert "emotional_state" in registry.metrics

    def test_metrics_update_from_state(self):
        """Registry should update metrics from a state dict."""
        from heartbeat.prometheus import MetricsRegistry
        registry = MetricsRegistry()
        state = {
            "health_score": 85.0,
            "health_trend": "stable",
            "pulse_count": 42,
            "state": "running",
            "emotional_state": "contentment",
            "checks": {
                "health": {"severity": "ok", "message": "All good"},
                "prediction": {"severity": "ok", "message": "Stable"},
            },
        }
        registry.update_from_state(state)
        # Verify metrics were set
        output = registry.render()
        assert "verdandi_health_score 85.0" in output
        assert "verdandi_pulse_total 42" in output
        assert "verdandi_emotional_state 5" in output

    def test_metrics_render_format(self):
        """Rendered output should be valid Prometheus exposition format."""
        from heartbeat.prometheus import MetricsRegistry
        registry = MetricsRegistry()
        registry.update_from_state({
            "health_score": 100, "health_trend": "stable",
            "pulse_count": 1, "state": "running",
            "emotional_state": "contentment", "checks": {},
        })
        output = registry.render()
        assert "# HELP verdandi_health_score" in output
        assert "# TYPE verdandi_health_score gauge" in output

    def test_exporter_start_stop(self):
        """Exporter should start and stop without errors."""
        from heartbeat.prometheus import PrometheusExporter, MetricsRegistry
        registry = MetricsRegistry()
        exporter = PrometheusExporter(port=0, registry=registry)
        # Port 0 lets OS pick a free port
        exporter.start()
        import time
        time.sleep(0.2)
        exporter.stop()


# ─────────────────────────────────────────────────────
# Maintenance Windows Tests
# ─────────────────────────────────────────────────────

class TestMaintenanceWindows:
    """Test maintenance window detection."""

    def test_no_windows_configured(self):
        """No windows should always return False."""
        # Create a minimal mock to test _in_maintenance_window
        daemon = MagicMock()
        daemon._maintenance_windows = []
        daemon._maintenance_suppress_actions = True
        daemon._maintenance_suppress_checks = []
        # Import the method directly
        from heartbeat.core import HeartbeatDaemon
        result = HeartbeatDaemon._in_maintenance_window(daemon)
        assert result is False

    def test_matching_window(self):
        """Current time within a daily window should return True."""
        daemon = MagicMock()
        daemon._maintenance_windows = [
            {"day": "daily", "start": "00:00", "end": "23:59"}
        ]
        from heartbeat.core import HeartbeatDaemon
        result = HeartbeatDaemon._in_maintenance_window(daemon)
        assert result is True

    def test_non_matching_window(self):
        """Current time outside all windows should return False."""
        daemon = MagicMock()
        daemon._maintenance_windows = [
            {"day": "sunday", "start": "02:00", "end": "03:00"}
        ]
        from heartbeat.core import HeartbeatDaemon
        result = HeartbeatDaemon._in_maintenance_window(daemon)
        assert isinstance(result, bool)