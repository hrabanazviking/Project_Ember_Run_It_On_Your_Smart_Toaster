"""
Verðandi Prometheus Metrics Exporter — Heimdall's Watchtower.

Exposes heartbeat metrics via a lightweight HTTP endpoint for Prometheus
scraping. This gives operators real-time visibility into daemon health.

Metrics exposed:
  - verdandi_health_score: Current health score (0-100)
  - verdandi_health_trend: Trend as gauge (improving=1, stable=0, degrading=-1)
  - verdandi_pulse_total: Total number of pulses since start
  - verdandi_daemon_state: Current daemon state (running=3, recovering=2, degraded=1, critical=0)
  - verdandi_check_severity: Per-check severity (ok=0, warning=1, critical=2, unknown=-1)
  - verdandi_circuit_breaker_state: Per-check circuit breaker state (closed=0, open=1, half_open=0.5)
  - verdandi_emotional_state: Emotional classification (contentment=5, hope=4, moderate=3, concern=2, acceptance=1, urgency=0)
  - verdandi_prediction_days_to_exhaustion: Days until resource exhaustion (disk, memory)

The exporter uses only stdlib — no dependencies beyond Python 3.11.
It runs in a daemon thread alongside the heartbeat.
"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger("verdandi.metrics")


# ─────────────────────────────────────────────────────
# Prometheus Metric Types
# ─────────────────────────────────────────────────────

class Metric:
    """Base Prometheus metric."""

    def __init__(self, name: str, help_text: str, label_names: Optional[list] = None):
        self.name = name
        self.help_text = help_text
        self.label_names = label_names or []
        self._values: dict[tuple, float] = {}

    def set(self, value: float, labels: Optional[dict] = None) -> None:
        key = tuple(labels.get(l, "") for l in self.label_names) if labels else ()
        self._values[key] = value

    def render(self) -> str:
        lines = [f"# HELP {self.name} {self.help_text}", f"# TYPE {self.name} gauge"]
        for labels, value in self._values.items():
            if labels:
                label_str = ",".join(f'{l}="{v}"' for l, v in zip(self.label_names, labels))
                lines.append(f"{self.name}{{{label_str}}} {value}")
            else:
                lines.append(f"{self.name} {value}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────
# Metrics Registry
# ─────────────────────────────────────────────────────

class MetricsRegistry:
    """Central registry for all Verðandi Prometheus metrics."""

    def __init__(self):
        self.metrics = {
            "health_score": Metric(
                "verdandi_health_score",
                "Current health score (0-100, EMA-based)",
            ),
            "health_trend": Metric(
                "verdandi_health_trend",
                "Health trend (improving=1, stable=0, degrading=-1)",
            ),
            "pulse_total": Metric(
                "verdandi_pulse_total",
                "Total number of heartbeat pulses since daemon start",
            ),
            "daemon_state": Metric(
                "verdandi_daemon_state",
                "Current daemon state (running=3, recovering=2, degraded=1, critical=0)",
            ),
            "check_severity": Metric(
                "verdandi_check_severity",
                "Per-check severity (ok=0, warning=1, critical=2, unknown=-1)",
                label_names=["check"],
            ),
            "circuit_breaker_state": Metric(
                "verdandi_circuit_breaker_state",
                "Per-check circuit breaker state (closed=0, open=1, half_open=0.5)",
                label_names=["check"],
            ),
            "emotional_state": Metric(
                "verdandi_emotional_state",
                "Emotional classification (contentment=5, hope=4, moderate=3, concern=2, acceptance=1, urgency=0)",
            ),
            "prediction_days_to_exhaustion": Metric(
                "verdandi_prediction_days_to_exhaustion",
                "Predicted days until resource exhaustion",
                label_names=["resource"],
            ),
        }

    def update_from_state(self, state_dict: dict) -> None:
        """Update all metrics from a heartbeat state dict."""
        # Health score
        health_score = state_dict.get("health_score", 0)
        self.metrics["health_score"].set(float(health_score))

        # Health trend
        trend_map = {"improving": 1, "stable": 0, "degrading": -1, "unknown": 0}
        trend = state_dict.get("health_trend", "unknown")
        self.metrics["health_trend"].set(trend_map.get(trend, 0))

        # Pulse total
        pulse_count = state_dict.get("pulse_count", 0)
        self.metrics["pulse_total"].set(float(pulse_count))

        # Daemon state
        state_map = {"running": 3, "recovering": 2, "degraded": 1, "critical": 0,
                     "initializing": 1, "shutting_down": 0}
        daemon_state = state_dict.get("state", "unknown")
        self.metrics["daemon_state"].set(float(state_map.get(daemon_state, 0)))

        # Check severities
        severity_map = {"ok": 0, "warning": 1, "critical": 2, "unknown": -1}
        checks = state_dict.get("checks", {})
        for name, result in checks.items():
            if isinstance(result, dict):
                severity = result.get("severity", "unknown")
            else:
                severity = getattr(result, "severity", CheckSeverity_safe(result))
            self.metrics["check_severity"].set(
                float(severity_map.get(severity, -1)),
                labels={"check": name},
            )

        # Emotional state
        emotion_map = {"contentment": 5, "hope": 4, "moderate": 3, "concern": 2,
                      "acceptance": 1, "urgency": 0, "anxiety": 0, "unknown": 2}
        emotion = state_dict.get("emotional_state", "unknown")
        self.metrics["emotional_state"].set(float(emotion_map.get(emotion, 2)))

    def render(self) -> str:
        """Render all metrics in Prometheus exposition format."""
        return "\n\n".join(m.render() for m in self.metrics.values()) + "\n"


# Avoid importing CheckSeverity — define a safe fallback
def CheckSeverity_safe(result):
    """Safely extract severity string from a result object."""
    if hasattr(result, "severity"):
        s = result.severity
        return s.value if hasattr(s, "value") else str(s)
    return "unknown"


# ─────────────────────────────────────────────────────
# HTTP Handler
# ─────────────────────────────────────────────────────

class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for /metrics endpoint."""

    registry: Optional[MetricsRegistry] = None

    def do_GET(self):
        if self.path == "/metrics":
            content = self.registry.render() if self.registry else ""
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.debug(f"Metrics: {format % args}")


# ─────────────────────────────────────────────────────
# Exporter Server
# ─────────────────────────────────────────────────────

class PrometheusExporter:
    """Lightweight Prometheus metrics exporter running in a daemon thread.

    Usage:
        exporter = PrometheusExporter(port=9101, registry=registry)
        exporter.start()  # Non-blocking, runs in background thread

    Configuration (in heartbeat.yaml):
        prometheus:
          enabled: true
          port: 9101
          host: "0.0.0.0"
    """

    def __init__(self, port: int = 9101, host: str = "0.0.0.0",
                 registry: Optional[MetricsRegistry] = None):
        self.port = port
        self.host = host
        self.registry = registry or MetricsRegistry()
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        MetricsHandler.registry = self.registry

    def start(self) -> None:
        """Start the metrics server in a daemon thread."""
        if self._thread and self._thread.is_alive():
            return

        def serve():
            try:
                self._server = HTTPServer((self.host, self.port), MetricsHandler)
                logger.info(f"Prometheus exporter listening on {self.host}:{self.port}")
                self._server.serve_forever()
            except Exception as e:
                logger.error(f"Prometheus exporter error: {e}")

        self._thread = threading.Thread(target=serve, daemon=True, name="verdandi-metrics")
        self._thread.start()

    def stop(self) -> None:
        """Stop the metrics server."""
        if self._server:
            self._server.shutdown()
            logger.info("Prometheus exporter stopped")

    def update(self, state_dict: dict) -> None:
        """Update metrics from a heartbeat state dict."""
        self.registry.update_from_state(state_dict)