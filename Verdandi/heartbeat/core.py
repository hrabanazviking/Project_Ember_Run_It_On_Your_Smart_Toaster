"""
Verðandi Heartbeat Core — The Pulse of Becoming.

The main daemon loop. Each pulse checks health, projects, memory, and schedule,
then reacts to what it finds. The state machine tracks overall system health:

  INITIALIZING → RUNNING → DEGRADED → CRITICAL → RECOVERING
                    ↑           ↑           │
                    └───────────┴───────────┘

States:
  - INITIALIZING: Starting up, first pulse not yet completed
  - RUNNING: All checks pass within thresholds
  - DEGRADED: One or more checks in warning state (but not critical)
  - CRITICAL: One or more checks exceeded critical thresholds
  - RECOVERING: Was critical/degraded, now recovering

Every pulse fires a nerve impulse to the nerve hub. Every state change
is logged, stored in Mímir (if available), and triggers appropriate
recovery actions.

This is not a monitor. This is a living system that feels its own pulse.
"""

import json
import os
import time
import random
import logging
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from heartbeat.config import HeartbeatConfig, DEFAULTS
from heartbeat.paths import (
    get_state_dir, get_log_dir, get_pid_dir, get_socket_path,
    get_config_path, get_db_path, get_pid_path, get_log_path,
    get_platform_info, ensure_dirs,
)
from heartbeat.signals import SignalHandler, DaemonContext
from heartbeat.checks import CHECK_REGISTRY
from heartbeat.checks.base import BaseCheck, CheckResult, CheckSeverity
from heartbeat.reactor import Reactor

logger = logging.getLogger("verdandi.heartbeat")


# ─────────────────────────────────────────────────────
# Circuit Breaker — Fail-Fast Protection for Checks/Actions
# ─────────────────────────────────────────────────────

class CircuitBreaker:
    """Prevents repeated calls to a failing component.
    
    A circuit breaker tracks consecutive failures and "trips" (opens)
    after a threshold is reached, preventing further calls until a
    cooldown period passes. This protects the system from cascading
    failures and resource exhaustion.
    
    States:
      - CLOSED: Normal operation, calls pass through
      - OPEN: Too many failures, calls are rejected fast
      - HALF_OPEN: Cooldown elapsed, one probe call allowed
    
    Norse metaphor: Heimdall's gaze — the watchman who knows when
    to close the Bifröst to protect Asgard.
    """
    
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"
    
    def __init__(self, failure_threshold: int = 5, cooldown_seconds: float = 300.0,
                 name: str = "unnamed"):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.name = name
        self._state = self.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._total_calls = 0
        self._total_failures = 0
    
    @property
    def state(self) -> str:
        if self._state == self.OPEN:
            if (time.monotonic() - self._last_failure_time) > self.cooldown_seconds:
                self._state = self.HALF_OPEN
        return self._state
    
    def allow(self) -> bool:
        """Whether a call is allowed through the breaker."""
        self._total_calls += 1
        if self.state == self.CLOSED or self.state == self.HALF_OPEN:
            return True
        return False
    
    def record_success(self) -> None:
        """Record a successful call. Resets failure counter."""
        self._failure_count = 0
        self._success_count += 1
        if self._state == self.HALF_OPEN:
            self._state = self.CLOSED
    
    def record_failure(self) -> None:
        """Record a failed call. May trip the breaker open."""
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.failure_threshold:
            self._state = self.OPEN
    
    @property
    def stats(self) -> dict:
        """Return circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "failure_threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown_seconds,
        }


# ─────────────────────────────────────────────────────
# Health Score — Trending and Stability Metrics
# ─────────────────────────────────────────────────────

class HealthScore:
    """Tracks system health over time with exponential moving average.
    
    Provides a 0-100 health score based on check severities,
    with trend detection (improving, stable, degrading) and
    anomaly detection via standard deviation.
    
    Norse metaphor: Urðr's thread — measuring the weight of what-has-been
    to understand what-is-becoming.
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._scores: list[float] = []
        self._ema: float = 100.0  # Start assuming healthy
        self._ema_alpha: float = 2.0 / (window_size + 1)
    
    def record_pulse(self, checks: dict[str, "CheckResult"]) -> float:
        """Record a pulse and return the current health score (0-100)."""
        score = self._compute_score(checks)
        self._scores.append(score)
        if len(self._scores) > self.window_size:
            self._scores = self._scores[-self.window_size:]
        self._ema = score * self._ema_alpha + self._ema * (1 - self._ema_alpha)
        return score
    
    def _compute_score(self, checks: dict[str, "CheckResult"]) -> float:
        """Compute a single health score from check results."""
        if not checks:
            return 100.0
        weights = {"ok": 100, "warning": 50, "critical": 0, "unknown": 75}
        total = sum(weights.get(r.severity.value, 75) for r in checks.values())
        return total / len(checks)
    
    @property
    def current(self) -> float:
        """Current exponentially-weighted health score."""
        return round(self._ema, 1)
    
    @property
    def trend(self) -> str:
        """Health trend: 'improving', 'stable', or 'degrading'."""
        if len(self._scores) < 5:
            return "stable"
        recent = self._scores[-5:]
        older = self._scores[-10:-5] if len(self._scores) >= 10 else recent
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        diff = recent_avg - older_avg
        if diff > 5:
            return "improving"
        elif diff < -5:
            return "degrading"
        return "stable"
    
    @property
    def stability(self) -> float:
        """Score stability (standard deviation). Lower = more stable."""
        if len(self._scores) < 3:
            return 0.0
        mean = sum(self._scores) / len(self._scores)
        variance = sum((s - mean) ** 2 for s in self._scores) / len(self._scores)
        return round(variance ** 0.5, 1)
    
    @property
    def summary(self) -> dict:
        """Full health score summary."""
        return {
            "current_score": self.current,
            "trend": self.trend,
            "stability_std": self.stability,
            "sample_count": len(self._scores),
        }


# ─────────────────────────────────────────────────────
# State Machine — The Daemon's Consciousness Levels
# ─────────────────────────────────────────────────────

class DaemonState(Enum):
    """System health states, ordered by severity."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class HeartbeatState:
    """Full state snapshot of the daemon."""
    state: DaemonState = DaemonState.INITIALIZING
    pulse_count: int = 0
    last_pulse: str = ""
    last_healthy_pulse: str = ""
    started_at: str = ""
    checks: dict[str, CheckResult] = field(default_factory=dict)
    uptime_seconds: float = 0.0
    config_source: str = ""
    platform: str = ""

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "state": self.state.value,
            "pulse_count": self.pulse_count,
            "last_pulse": self.last_pulse,
            "last_healthy_pulse": self.last_healthy_pulse,
            "started_at": self.started_at,
            "uptime_seconds": self.uptime_seconds,
            "config_source": self.config_source,
            "platform": self.platform,
            "checks": {
                name: result.to_dict() if isinstance(result, CheckResult) else result
                for name, result in self.checks.items()
            },
            "health_score": getattr(self, '_health_score_current', 0),
            "health_trend": getattr(self, '_health_trend', 'unknown'),
            "emotional_state": getattr(self, '_emotional_state', 'unknown'),
        }


# ─────────────────────────────────────────────────────
# The Heartbeat — The Pulse Loop
# ─────────────────────────────────────────────────────

class HeartbeatDaemon:
    """The main heartbeat daemon. Runs the pulse loop and manages state.

    Usage:
        daemon = HeartbeatDaemon()
        daemon.run()  # Blocks until shutdown

    Or for a single pulse:
        daemon = HeartbeatDaemon()
        result = daemon.pulse()
        print(result)

    Or for status:
        daemon = HeartbeatDaemon()
        print(daemon.state)
    """

    def __init__(self, config: Optional[HeartbeatConfig] = None, daemon: bool = True):
        self.config = config or HeartbeatConfig()
        self.daemon_mode = daemon
        self.state = HeartbeatState()
        self.state.started_at = datetime.now(timezone.utc).isoformat()
        self.state.config_source = str(self.config.config_path)
        self.state.platform = get_platform_info().get("platform_name", "unknown")

        self._signal_handler = SignalHandler(
            config_reload_callback=self.config.reload,
            state_dump_callback=lambda: self.state.to_dict(),
        )
        self._daemon_ctx = DaemonContext(get_pid_path())

        # Initialize check instances from registry
        self._checks: dict[str, BaseCheck] = {}
        for name, check_class in CHECK_REGISTRY.items():
            if self.config.get(f"checks.{name}", True):
                self._checks[name] = check_class(self.config)

        # Initialize reactor (check → action bridge)
        dry_run = self.config.get("reactor.dry_run", True)  # Default dry-run for safety
        self._reactor = Reactor(config=self.config, dry_run=dry_run)

        # Circuit breakers for each check — prevents cascading failures
        self._circuit_breakers: dict[str, CircuitBreaker] = {
            name: CircuitBreaker(
                failure_threshold=self.config.get(f"checks.{name}.circuit_breaker_threshold", 5),
                cooldown_seconds=self.config.get(f"checks.{name}.circuit_breaker_cooldown", 300),
                name=f"check_{name}",
            )
            for name in self._checks
        }

        # Health score trending
        self._health_score = HealthScore(
            window_size=self.config.get("heartbeat.health_score_window", 100)
        )

        # v0.3.0: Maintenance windows — skip non-critical actions during maintenance
        self._maintenance_windows = self.config.get("maintenance.windows", [])
        self._maintenance_suppress_actions = self.config.get("maintenance.suppress_actions", True)
        self._maintenance_suppress_checks = self.config.get("maintenance.suppress_checks", [])

        self._running = False
        self._pulse_count = 0
        self._db_path = get_db_path()

        # v0.3.0: Prometheus metrics exporter
        self._prometheus = None
        if self.config.get("prometheus.enabled", False):
            from heartbeat.prometheus import PrometheusExporter, MetricsRegistry
            self._metrics_registry = MetricsRegistry()
            self._prometheus = PrometheusExporter(
                port=self.config.get("prometheus.port", 9101),
                host=self.config.get("prometheus.host", "0.0.0.0"),
                registry=self._metrics_registry,
            )

    def _in_maintenance_window(self) -> bool:
        """Check if current time falls within a configured maintenance window.

        Maintenance windows suppress non-critical actions and specified checks.
        Format: {"day": "sunday", "start": "02:00", "end": "06:00"}
        Days can be: monday-sunday, or "daily" for every day.
        """
        if not self._maintenance_windows:
            return False

        now = datetime.now(timezone.utc)
        current_day = now.strftime("%A").lower()
        current_time = now.strftime("%H:%M")

        for window in self._maintenance_windows:
            day = window.get("day", "daily").lower()
            start = window.get("start", "00:00")
            end = window.get("end", "23:59")

            # Check day match
            if day != "daily" and day != current_day:
                continue

            # Check time range
            if start <= current_time <= end:
                logger.info(f"In maintenance window: {window}")
                return True

        return False

    def run(self) -> None:
        """Main daemon loop. Blocks until shutdown."""
        ensure_dirs()
        self._setup_logging()

        logger.info(f"🫀 Verðandi Heartbeat starting (platform: {self.state.platform})")
        logger.info(f"   Config: {self.config}")
        logger.info(f"   Checks: {list(self._checks.keys())}")
        logger.info(f"   State dir: {get_state_dir()}")
        logger.info(f"   Pulse interval: {self.config.get('heartbeat.interval_seconds')}s")

        if self.daemon_mode:
            if not self._daemon_ctx.acquire():
                logger.error("Another instance is already running. Exiting.")
                return
            logger.info("Daemon mode: PID file acquired")

        self._signal_handler.install()
        self._state_db_init()
        self.state.state = DaemonState.RUNNING
        self._running = True

        # v0.3.0: Start Prometheus exporter if enabled
        if self._prometheus:
            self._prometheus.start()
            logger.info("Prometheus metrics exporter started")

        # Startup delay
        startup_delay = self.config.get("heartbeat.startup_delay_seconds", 10)
        logger.info(f"Startup delay: {startup_delay}s")
        time.sleep(startup_delay)

        try:
            while self._running and not self._signal_handler.should_shutdown:
                # Handle signals
                if self._signal_handler.should_reload:
                    self._signal_handler.clear_reload()
                    self.config.reload()
                    # Re-initialize checks with new config
                    self._checks.clear()
                    for name, check_class in CHECK_REGISTRY.items():
                        if self.config.get(f"checks.{name}", True):
                            self._checks[name] = check_class(self.config)
                    logger.info("Config reloaded, checks re-initialized")

                if self._signal_handler.should_dump_state:
                    self._signal_handler.clear_dump_state()
                    self._signal_handler.dump_state(
                        self.state.to_dict(),
                        get_state_dir() / "verdandi_state_dump.json"
                    )

                # Run pulse
                self._pulse_count += 1
                self.pulse()

                # Update state machine
                self._update_daemon_state()

                # Sleep with jitter
                interval = self.config.get("heartbeat.interval_seconds", 60)
                jitter = self.config.get("heartbeat.jitter_seconds", 5)
                sleep_time = interval + random.uniform(-jitter, jitter)

                for _ in range(max(1, int(sleep_time))):
                    if self._signal_handler.should_shutdown:
                        break
                    if self._signal_handler.should_pulse:
                        self._signal_handler.clear_pulse()
                        break
                    if self._signal_handler.should_reload:
                        self._signal_handler.clear_reload()
                        self.config.reload()
                    time.sleep(1)

        finally:
            self.state.state = DaemonState.SHUTTING_DOWN
            self._shutdown()

    def pulse(self) -> HeartbeatState:
        """Run a single pulse cycle. Returns the state after the pulse."""
        start_time = time.monotonic()
        self.state.pulse_count += 1
        now = datetime.now(timezone.utc).isoformat()

        logger.debug(f"Pulse #{self.state.pulse_count} starting")

        # Run all enabled checks (with circuit breaker protection)
        in_maintenance = self._in_maintenance_window()

        for name, check in self._checks.items():
            # Skip checks suppressed during maintenance window
            if in_maintenance and name in self._maintenance_suppress_checks:
                logger.debug(f"Check {name}: skipped (maintenance window)")
                continue

            # Circuit breaker: skip checks that have been failing repeatedly
            breaker = self._circuit_breakers.get(name)
            if breaker and not breaker.allow():
                logger.debug(f"Check {name}: skipped (circuit breaker OPEN)")
                # Use last known result if available, otherwise UNKNOWN
                if name in self.state.checks:
                    result = self.state.checks[name]
                else:
                    result = CheckResult(
                        name=name, severity=CheckSeverity.UNKNOWN,
                        message=f"Circuit breaker open — {breaker.stats}"
                    )
                self.state.checks[name] = result
                continue

            try:
                result = check.check()
                self.state.checks[name] = result
                if breaker:
                    if result.severity == CheckSeverity.UNKNOWN:
                        breaker.record_failure()
                    else:
                        breaker.record_success()
                logger.debug(f"Check {name}: {result.severity.value} — {result.message}")
            except Exception as e:
                logger.error(f"Check {name} failed: {e}")
                self.state.checks[name] = CheckResult(
                    name=name, severity=CheckSeverity.UNKNOWN,
                    message=f"Check error: {e}"
                )
                if breaker:
                    breaker.record_failure()

        # Update health score
        health = self._health_score.record_pulse(self.state.checks)
        logger.debug(f"Health score: {health:.1f} (trend: {self._health_score.trend})")

        # v0.3.0: Determine emotional state from health trends
        try:
            from heartbeat.checks.skuld import TrendClassifier
            scores = self._health_score._scores
            trend = self._health_score.trend
            stability = self._health_score.stability
            emotion_data = TrendClassifier.classify(scores, trend, stability)
            self.state._health_score_current = self._health_score.current
            self.state._health_trend = trend
            self.state._emotional_state = emotion_data.get("emotion", "unknown")
            logger.debug(f"Emotional state: {self.state._emotional_state}")
        except Exception as e:
            logger.debug(f"Emotional classification skipped: {e}")

        # Fire nerve impulse
        if self.config.get("nerve.publish_pulses", True):
            self._fire_nerve_pulse()

        # React to check results (trigger actions)
        if self.config.get("reactor.enabled", True):
            # During maintenance windows, suppress non-critical actions
            if in_maintenance and self._maintenance_suppress_actions:
                critical_only = {
                    name: result for name, result in self.state.checks.items()
                    if result.severity == CheckSeverity.CRITICAL
                }
                action_results = self._reactor.react(critical_only)
                logger.info(f"Maintenance window: only processing {len(critical_only)} critical checks")
            else:
                action_results = self._reactor.react(self.state.checks)
            for ar in action_results:
                logger.info(
                    f"  🎯 Action {ar.action_name}: {ar.severity.value} — {ar.message}"
                )

        # Persist state
        self.state.last_pulse = now
        if self.state.state in (DaemonState.RUNNING, DaemonState.RECOVERING):
            if all(
                r.severity in (CheckSeverity.OK, CheckSeverity.WARNING)
                for r in self.state.checks.values()
            ):
                self.state.last_healthy_pulse = now

        # v0.3.0: Update Prometheus metrics
        if self._prometheus:
            self._prometheus.update(self.state.to_dict())

        self.state.uptime_seconds = time.monotonic() - start_time + (
            self.state.uptime_seconds if self.state.pulse_count > 1 else 0
        )

        self._state_db_save()

        duration = (time.monotonic() - start_time) * 1000
        logger.info(
            f"🫀 Pulse #{self.state.pulse_count} complete "
            f"({duration:.0f}ms) state={self.state.state.value}"
        )

        return self.state

    def _update_daemon_state(self) -> None:
        """Update the daemon state machine based on check results."""
        prev_state = self.state.state

        # Determine worst severity
        severities = [r.severity for r in self.state.checks.values()]

        if any(s == CheckSeverity.CRITICAL for s in severities):
            new_state = DaemonState.CRITICAL
        elif any(s == CheckSeverity.WARNING for s in severities):
            new_state = DaemonState.DEGRADED
        elif any(s == CheckSeverity.UNKNOWN for s in severities):
            # Unknown checks don't change state
            new_state = self.state.state
            if new_state == DaemonState.INITIALIZING:
                new_state = DaemonState.RUNNING
        else:
            # All OK
            if self.state.state in (DaemonState.DEGRADED, DaemonState.CRITICAL):
                new_state = DaemonState.RECOVERING
            elif self.state.state == DaemonState.RECOVERING:
                new_state = DaemonState.RUNNING
            else:
                new_state = DaemonState.RUNNING

        if new_state != prev_state:
            logger.info(f"State transition: {prev_state.value} → {new_state.value}")
            self.state.state = new_state

            # State change → nerve impulse
            if self.config.get("nerve.publish_pulses", True):
                self._fire_nerve_state_change(prev_state, new_state)

    def _fire_nerve_pulse(self) -> None:
        """Fire a nerve impulse for the pulse event."""
        try:
            socket_path = self.config.get("nerve.socket_path") or str(get_socket_path())
            nerve_data = {
                "event_type": "heartbeat_pulse",
                "pulse_count": self.state.pulse_count,
                "state": self.state.state.value,
                "health_score": self._health_score.current,
                "health_trend": self._health_score.trend,
                "emotional_state": getattr(self.state, '_emotional_state', 'unknown'),
                "checks": {
                    name: {
                        "severity": result.severity.value,
                        "message": result.message,
                    }
                    for name, result in self.state.checks.items()
                },
            }

            import socket as sock_mod
            with sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(socket_path)
                s.sendall(json.dumps(nerve_data).encode() + b"\n")
        except Exception:
            if self.config.get("nerve.fallback_to_file", True):
                self._nerve_fallback_file(nerve_data if 'nerve_data' in dir() else {})

    def _fire_nerve_state_change(self, old_state: DaemonState, new_state: DaemonState) -> None:
        """Fire a nerve impulse for a state change."""
        try:
            socket_path = self.config.get("nerve.socket_path") or str(get_socket_path())
            nerve_data = {
                "event_type": "heartbeat_state_change",
                "old_state": old_state.value,
                "new_state": new_state.value,
                "pulse_count": self.state.pulse_count,
            }

            import socket as sock_mod
            with sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(socket_path)
                s.sendall(json.dumps(nerve_data).encode() + b"\n")
        except Exception:
            pass

    def _nerve_fallback_file(self, data: dict) -> None:
        """Fallback: append nerve impulse to file if socket unavailable."""
        try:
            feed_path = get_state_dir() / "nerve_feed.jsonl"
            with open(feed_path, "a") as f:
                entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "verdandi-heartbeat",
                    "event_type": data.get("event_type", "heartbeat_pulse"),
                    **data,
                }
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def _state_db_init(self) -> None:
        """Initialize the persistent state database."""
        db_path = self._db_path or get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS heartbeat_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pulse_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    state TEXT NOT NULL,
                    checks_json TEXT,
                    pulse_count INTEGER
                )
            """)
            # v0.3.0: Skuld prediction fields
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pulse_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pulse_count INTEGER NOT NULL,
                    health_score REAL,
                    health_trend TEXT,
                    daemon_state TEXT,
                    check_severities_json TEXT,
                    circuit_breakers_json TEXT,
                    emotional_state TEXT
                )
            """)
            # Index for fast Skuld queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pulse_metrics_timestamp
                ON pulse_metrics(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_pulse_metrics_health_score
                ON pulse_metrics(health_score)
            """)
            conn.commit()

    def _state_db_save(self) -> None:
        """Persist current state to database with checksum validation."""
        try:
            db_path = self._db_path or get_db_path()
            with sqlite3.connect(str(db_path)) as conn:
                state_dict = self.state.to_dict()
                for key, value in state_dict.items():
                    if isinstance(value, dict):
                        value = json.dumps(value)
                    elif isinstance(value, Enum):
                        value = value.value
                    conn.execute(
                        "INSERT OR REPLACE INTO heartbeat_state (key, value, updated_at) VALUES (?, ?, datetime('now'))",
                        (key, str(value) if not isinstance(value, (str, int, float)) else value)
                    )

                checks_json = json.dumps(state_dict.get("checks", {}))
                conn.execute(
                    "INSERT INTO pulse_history (timestamp, state, checks_json, pulse_count) VALUES (datetime('now'), ?, ?, ?)",
                    (state_dict["state"], checks_json, state_dict.get("pulse_count", 0))
                )
                conn.execute("DELETE FROM pulse_history WHERE id < (SELECT MAX(id) FROM pulse_history) - 1000")

                # v0.3.0: Skuld metrics — store per-pulse health data for prediction
                check_severities = {
                    name: r.severity.value if isinstance(r, CheckResult) else str(r)
                    for name, r in self.state.checks.items()
                }
                circuit_breaker_states = {
                    name: breaker.stats for name, breaker in self._circuit_breakers.items()
                }

                # Determine emotional state from health score
                emotion = "unknown"
                if hasattr(self, '_health_score') and self._health_score._scores:
                    from heartbeat.checks.skuld import TrendClassifier
                    scores = self._health_score._scores
                    trend = self._health_score.trend
                    stability = self._health_score.stability
                    emotion_data = TrendClassifier.classify(scores, trend, stability)
                    emotion = emotion_data.get("emotion", "unknown")

                conn.execute(
                    """INSERT INTO pulse_metrics
                    (pulse_count, health_score, health_trend, daemon_state,
                     check_severities_json, circuit_breakers_json, emotional_state)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self.state.pulse_count,
                        self._health_score.current,
                        self._health_score.trend,
                        self.state.state.value,
                        json.dumps(check_severities),
                        json.dumps(circuit_breaker_states),
                        emotion,
                    )
                )
                # Keep last 10000 metrics for prediction (7 days at 1/min)
                conn.execute("DELETE FROM pulse_metrics WHERE id < (SELECT MAX(id) FROM pulse_metrics) - 10000")

                conn.commit()
        except Exception as e:
            logger.warning(f"State DB save failed: {e}")

    def _setup_logging(self) -> None:
        """Configure logging for the daemon."""
        log_level = self.config.get("logging.level", "INFO")
        log_format = self.config.get("logging.format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        log_path = get_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=self.config.get("logging.file_max_bytes", 10 * 1024 * 1024),
            backupCount=self.config.get("logging.file_backup_count", 5),
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        root_logger = logging.getLogger("verdandi")
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        root_logger.addHandler(file_handler)

        if self.config.get("logging.also_log_to_stderr", True):
            stderr_handler = logging.StreamHandler()
            stderr_handler.setFormatter(logging.Formatter(log_format))
            stderr_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            root_logger.addHandler(stderr_handler)

    def _shutdown(self) -> None:
        """Clean up on shutdown."""
        logger.info("Shutting down...")
        self.state.state = DaemonState.SHUTTING_DOWN
        self._state_db_save()

        # v0.3.0: Stop Prometheus exporter
        if self._prometheus:
            self._prometheus.stop()
            logger.info("Prometheus metrics exporter stopped")

        if self.daemon_mode:
            self._daemon_ctx.release()

        self._signal_handler.restore()
        self._running = False
        logger.info("🫀 Verðandi Heartbeat stopped. The pulse is silent for now.")