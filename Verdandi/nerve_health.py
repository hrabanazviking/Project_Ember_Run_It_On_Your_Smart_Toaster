#!/usr/bin/env python3
"""
Verdandi Nerve Health — a stuck/dead nerve is detected and
reported; the hub degrades honestly.

Filed by Project Ember slice E-066 (docs/architecture/
E-066_NERVE_HEALTH.md). This module IS the nerve-health
discipline in code, in the same shape as event_contract.py
(E-061), context_budget.py (E-062), logger_law.py (E-063),
stimuli.py (E-064) and reflexes.py (E-065): stdlib only, no
imports from any other Verdandi module, so the discipline
stands alone. The live probes live in nervous_system.py
(which is deployed standalone); this module owns the
classification — the pure decision, from a stated set of
observations, of what state the nerve is in and what that
state honestly means for the rest of the system.

THE CAUTIONARY FIXTURE

The Hermes baseline's Verdandi-socket failures (E-059 §8,
E-066's brief): a producer fired at a socket nothing
listened on, the failure was silent for one shape and
feed-polluting for the other, and a status probe that
itself published a real event (docket 96) made the feed
lie about the traffic it carried. Nerve health exists so
none of that can happen unnoticed again: a dead or stuck
hub is NAMED, a status probe never becomes traffic, and
degradation is reported as degradation — never as success.

THE FIVE STATES

- ``healthy`` — the hub process is alive, its socket
  answers the control ping with pong, and the feed shows
  no warning condition.
- ``degraded`` — the hub answers and is alive, but a
  warning condition holds (feed at/over the warning share
  of the rotation threshold, feed missing, log not
  writable). Live pub/sub still works; the warning is
  part of the report, never hidden behind "healthy".
- ``stuck`` — the hub process is alive (or its socket
  file stands) but the socket does not answer the control
  ping: alive on paper, silent in fact. Publishers must
  not be told this is success; their sends time out or
  return no-ack, and readers fall back to the feed.
- ``dead`` — a PID file stands but the process it names
  is not running: the hub died and left its papers
  behind. That is different from never having started.
- ``absent`` — no socket, no live process, no PID file:
  the hub is simply not running. Publishers degrade to
  the feed fallback (marked ``_fallback``), subscribers
  are told the hub is not running, and recent reads come
  from the feed file. Absent is a fact, not a failure of
  the caller.

DEGRADE HONESTLY — WHAT EACH STATE MEANS, STATED

``DEGRADE_BEHAVIOUR`` states, per state, what publishers,
subscribers and readers may expect. The shapes it names
are the ones the tree already implements and E-066 pins:
publish_event_sync's feed fallback carries ``_fallback:
True`` and returns nerve_type ``fallback`` (never ``ack``);
get_status / healthcheck report the classification; the
subscribe CLI refuses plainly when the hub is not running.

WHAT THIS DOES NOT DO

It does not restart the hub (a reflex or an operator may,
on this report — detection and Restart are separate acts,
and E-065's reflexes own acting). It does not rewire the
heartbeat's legacy transport (E-067). Backpressure under
flood is E-070. The pulse_metrics half of this slice —
Skuld reading the per-pulse health scores the daemon
already writes — lives in heartbeat/checks/skuld.py, not
here; this module governs the hub (runa.sock), not the
heartbeat daemon's own store.
"""

from dataclasses import dataclass

NERVE_HEALTH_VERSION = 1

STATE_HEALTHY = "healthy"
STATE_DEGRADED = "degraded"
STATE_STUCK = "stuck"
STATE_DEAD = "dead"
STATE_ABSENT = "absent"
STATES = (STATE_HEALTHY, STATE_DEGRADED, STATE_STUCK,
          STATE_DEAD, STATE_ABSENT)

# The feed warns at 80% of its rotation threshold — the
# share nervous_system.cmd_healthcheck already warned at
# before this slice; the classification keeps that line.
FEED_WARN_FRACTION = 0.8

# What each state honestly means for the rest of the
# system. Every value is a plain sentence a report may
# quote verbatim; none of them claims a success the state
# does not support.
DEGRADE_BEHAVIOUR = {
    STATE_HEALTHY: "live pub/sub: publishes are acked, "
                   "subscribers receive events, recent reads "
                   "come from the hub",
    STATE_DEGRADED: "live pub/sub still works, but the "
                    "warning conditions in the report hold "
                    "and must be shown, not hidden",
    STATE_STUCK: "the hub does not answer: publishes time "
                 "out or return no-ack (never a success), "
                 "subscribers receive nothing new, recent "
                 "reads fall back to the feed file",
    STATE_DEAD: "the hub process is gone but its PID file "
                "stands: publishes degrade to the marked "
                "feed fallback, subscribers cannot connect, "
                "the stale PID must be reported",
    STATE_ABSENT: "the hub is not running: publishes "
                  "degrade to the marked feed fallback, "
                  "subscribers are told the hub is not "
                  "running, recent reads come from the feed "
                  "file",
}


@dataclass(frozen=True)
class NerveObservations:
    """The facts a classification is made from.

    ``pid_alive`` / ``ping_responded`` are tri-state:
    True, False, or None when the fact was not (or could
    not be) observed — a classifier must never invent a
    probe result it did not get. ``feed_size_bytes`` is
    None when the feed is missing.
    """

    state_dir_exists: bool = False
    socket_exists: bool = False
    pid_file_exists: bool = False
    pid_alive: bool | None = None
    ping_responded: bool | None = None
    feed_exists: bool = False
    feed_size_bytes: int | None = None
    feed_max_bytes: int = 10 * 1024 * 1024
    log_writable: bool | None = None


def _obs_dict(obs) -> dict:
    if isinstance(obs, NerveObservations):
        return {f: getattr(obs, f) for f in (
            "state_dir_exists", "socket_exists",
            "pid_file_exists", "pid_alive", "ping_responded",
            "feed_exists", "feed_size_bytes", "feed_max_bytes",
            "log_writable")}
    return dict(obs)


def classify_nerve_health(obs) -> dict:
    """Classify the nerve from stated observations.

    Returns {"status": one of STATES, "reasons": [...],
    "warnings": [...], "behaviour": DEGRADE_BEHAVIOUR[status]}.
    Reasons name the facts that decided the status, in
    plain words; warnings are the degraded conditions.
    The order is load-bearing: dead (papers without a
    process) and stuck (a process/socket that does not
    answer) are judged before degraded/healthy, so a
    warning condition can never mask a silent hub.
    """
    o = _obs_dict(obs)
    reasons = []
    warnings = []

    if o.get("feed_exists"):
        size = o.get("feed_size_bytes")
        maxb = o.get("feed_max_bytes") or 0
        if size is not None and maxb and size >= FEED_WARN_FRACTION * maxb:
            warnings.append(
                f"feed is {size} bytes, at or over "
                f"{int(FEED_WARN_FRACTION * 100)}% of its "
                f"{maxb}-byte rotation threshold")
    else:
        if o.get("state_dir_exists") or o.get("socket_exists"):
            warnings.append("feed file is missing")
    if o.get("log_writable") is False:
        warnings.append("hub log file is not writable")

    pid_file = bool(o.get("pid_file_exists"))
    pid_alive = o.get("pid_alive")
    socket = bool(o.get("socket_exists"))
    ping = o.get("ping_responded")

    # Dead: papers stand, process does not.
    if pid_file and pid_alive is False:
        reasons.append("PID file stands but its process is not running")
        if socket:
            reasons.append("socket file stands with no live hub behind it")
        status = STATE_DEAD
        return {"status": status, "reasons": reasons,
                "warnings": warnings,
                "behaviour": DEGRADE_BEHAVIOUR[status]}

    # Stuck: alive (or socket present) but does not answer.
    if ping is False and (socket or pid_alive is True):
        reasons.append("socket does not answer the control ping")
        if pid_alive is True:
            reasons.append("hub process is alive but silent")
        status = STATE_STUCK
        return {"status": status, "reasons": reasons,
                "warnings": warnings,
                "behaviour": DEGRADE_BEHAVIOUR[status]}
    if pid_alive is True and not socket:
        reasons.append("hub process is alive but its socket file is missing")
        status = STATE_STUCK
        return {"status": status, "reasons": reasons,
                "warnings": warnings,
                "behaviour": DEGRADE_BEHAVIOUR[status]}

    # Absent: nothing running, nothing pretending to be.
    if not socket and pid_alive is not True:
        reasons.append("no socket and no live hub process")
        status = STATE_ABSENT
        return {"status": status, "reasons": reasons,
                "warnings": warnings,
                "behaviour": DEGRADE_BEHAVIOUR[status]}

    # The hub answers — healthy, or degraded by its warnings.
    if ping is True:
        reasons.append("hub process answers the control ping with pong")
        status = STATE_DEGRADED if warnings else STATE_HEALTHY
        return {"status": status, "reasons": reasons,
                "warnings": warnings,
                "behaviour": DEGRADE_BEHAVIOUR[status]}

    # Socket stands, aliveness claimed, but no probe result:
    # the honest verdict is stuck-adjacent — report degraded
    # with the missing probe named, never healthy.
    reasons.append("socket stands but no ping result was observed")
    warnings.append("hub responsiveness was not probed")
    return {"status": STATE_DEGRADED, "reasons": reasons,
            "warnings": warnings,
            "behaviour": DEGRADE_BEHAVIOUR[STATE_DEGRADED]}


def validate_classification(result) -> list:
    """Errors in a classification record; [] means sound."""
    errors = []
    if not isinstance(result, dict):
        return ["nerve-health classification must be a dict"]
    if result.get("status") not in STATES:
        errors.append(f"status must be one of {sorted(STATES)}, "
                      f"got {result.get('status')!r}")
    else:
        if result.get("behaviour") != DEGRADE_BEHAVIOUR[result["status"]]:
            errors.append("behaviour must be the stated behaviour "
                          "for the status")
    for key in ("reasons", "warnings"):
        if not isinstance(result.get(key), list):
            errors.append(f"{key} must be a list")
    if result.get("status") in (STATE_STUCK, STATE_DEAD, STATE_ABSENT):
        # A non-healthy hub must never be reported with the
        # healthy behaviour sentence.
        if result.get("behaviour") == DEGRADE_BEHAVIOUR[STATE_HEALTHY]:
            errors.append("a non-running hub must not claim live behaviour")
    return errors
