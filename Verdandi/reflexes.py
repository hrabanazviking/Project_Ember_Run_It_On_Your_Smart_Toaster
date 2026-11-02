#!/usr/bin/env python3
"""
Verdandi Reflexes — fast, dumb, safe reactions below
cognition.

Filed by Project Ember slice E-065 (docs/architecture/
E-065_REFLEX_LAYER.md). This module IS the reflex discipline
in code, in the same shape as event_contract.py (E-061),
context_budget.py (E-062), logger_law.py (E-063) and
stimuli.py (E-064): stdlib only, no imports from any other
Verdandi module, so the discipline stands alone.

WHAT A REFLEX IS

A reflex is a reaction that fires BELOW cognition: a sensor
result (a heartbeat check, E-064's sensor stimuli) crosses a
fixed severity threshold, a fixed rule matches, and a small
pre-written action runs — no model is consulted, nothing is
planned, nothing is learned in the act. The heartbeat
Reactor (heartbeat/reactor.py) is the matcher; the actions
in heartbeat/actions/ are the reflexes. This slice registers
every reflex the tree actually has, states the safety shape
each one already carries (or must carry), and repairs the
one reflex that was broken (Vör, docket 31).

THE THREE WORDS, MADE TESTABLE

- FAST: a reflex is a deterministic rule match plus one
  bounded action. It runs inside the pulse cycle, calls no
  model, performs no retrieval, and imports nothing from
  the companion core (src/ember). Its decision can be
  reproduced from the check results alone.
- DUMB: the rule is fixed at build/config time — check name,
  minimum severity, optional detail conditions, cooldown.
  A reflex does not choose its trigger, widen its own
  reach, or invent a new action. An unregistered action is
  not a reflex.
- SAFE: a reflex fires only at WARNING or above, only
  through BaseAction.execute (the wrapper that honours
  dry-run, tracks duration, registers cooldown and folds
  any exception into a FAILED result instead of crashing
  the pulse), and only as often as its cooldown allows.
  Every reflex result is an ActionResult record — what was
  done, how it ended — never a message to a person.

NEVER SPEAKS FOR THE COMPANION

This is the Heimdall doc-05 instinct applied here: a reflex
may act on the machine (clean, flush, restart, heal, push
the project's own repos under its standing rule) and it may
leave a record, but it NEVER speaks for the companion. It
produces no dialogue, no first-person utterance, no nerve
event in the companion's voice, and no message addressed to
the operator as if from the companion. Its only output
shape is the ActionResult (action_name, severity, message,
details, timestamp, targets, duration) — a technician's
record, read by operators and logs, not a voice. The
conversation reactor (reactor.py, top level) is likewise
not a voice: it emits reaction DIRECTIVES for a reader or
for cognition to consider; it executes nothing and speaks
to no one. Directives propose; reflexes act; cognition
speaks. Those three are never collapsed.

WHAT THIS DOES NOT DO

Cross-member wiring (which stimuli reach the reactor over
the canonical socket) is E-067's. Nerve health — detecting
a stuck reflex or a dead hub — is E-066's. Backpressure
(a flooded hub shedding, reflexes first-protected) is
E-070's. This slice registers, bounds and repairs; it does
not rewire transport and does not add a new reflex.
"""

from dataclasses import dataclass

REFLEX_VERSION = 1

# Severity ranks on the heartbeat scale (heartbeat/reactor's
# own SEVERITY_RESPONSE_LEVELS): a reflex may fire only at
# WARNING (2) or CRITICAL (3).
SEVERITY_RANKS = {"ok": 0, "unknown": 1, "warning": 2, "critical": 3}
MIN_REFLEX_RANK = SEVERITY_RANKS["warning"]

# The only severities an ActionResult may carry (the
# ActionSeverity enum in heartbeat/actions/base.py).
RESULT_SEVERITIES = ("success", "partial", "failed", "skipped", "dry_run")

# The exact fields of an ActionResult record (base.py's
# to_dict). A reflex result carrying any other field — a
# reply, an utterance, a message to a user — is not a
# reflex result.
RESULT_FIELDS = (
    "action_name", "severity", "message", "details",
    "timestamp", "targets_affected", "targets_failed", "duration_ms",
)

# Fields that would mean a reflex spoke for the companion.
SPEECH_FIELDS = ("reply", "utterance", "speech", "dialogue",
                 "message_to_user", "companion_says", "voice")


@dataclass(frozen=True)
class ReflexSpec:
    """One registered reflex.

    ``trigger_checks`` are the heartbeat check names the
    Reactor rule matches; ``min_severity`` is the lowest
    check severity that may fire it; ``cooldown_seconds``
    is the action's BaseAction cooldown (Vör additionally
    carries per-sub-action cooldowns, named in its notes);
    ``speaks_for_companion`` is False for every reflex —
    it is a field so a future registration must state it,
    and validation refuses True.
    """

    name: str
    action_class: str
    trigger_checks: tuple
    min_severity: str
    effect: str
    cooldown_seconds: float
    speaks_for_companion: bool = False
    notes: str = ""


REFLEX_SPECS = (
    ReflexSpec(
        name="auto_push",
        action_class="heartbeat/actions/mjölnir.MjölnirAction",
        trigger_checks=("projects",),
        min_severity="warning",
        effect="commit and push the project's own dirty/unpushed repos",
        cooldown_seconds=3600,
        notes="Reactor rule: projects -> auto_push at WARNING. "
              "Rate-limited per repo by its own cooldown logic "
              "in addition to the BaseAction cooldown.",
    ),
    ReflexSpec(
        name="auto_restart",
        action_class="heartbeat/actions/gungnir.GungnirAction",
        trigger_checks=("schedule",),
        min_severity="warning",
        effect="restart crashed or inactive systemd services",
        cooldown_seconds=600,
        notes="Reactor rule: schedule -> auto_restart at WARNING.",
    ),
    ReflexSpec(
        name="auto_cleanup",
        action_class="heartbeat/actions/bifrǫst.BifrǫstAction",
        trigger_checks=("memory", "health"),
        min_severity="warning",
        effect="prune logs and temp files, vacuum databases",
        cooldown_seconds=7200,
        notes="Two Reactor rules: memory -> auto_cleanup at "
              "WARNING, and health -> auto_cleanup at CRITICAL "
              "with a disk-usage condition. The stricter rule "
              "does not lower the registered floor.",
    ),
    ReflexSpec(
        name="auto_heal",
        action_class="heartbeat/actions/eir_action.EirAction",
        trigger_checks=("memory",),
        min_severity="critical",
        effect="repair corrupted databases, rebuild indexes, restore configs",
        cooldown_seconds=1800,
        notes="Reactor rule: memory -> auto_heal at CRITICAL — "
              "the only reflex whose floor is CRITICAL.",
    ),
    ReflexSpec(
        name="preemptive_heal",
        action_class="heartbeat/actions/vor_action.VörAction",
        trigger_checks=("prediction",),
        min_severity="warning",
        effect="pre-emptive cleanup, cache flush or service check "
               "on a degrading prediction, before CRITICAL",
        cooldown_seconds=300,
        notes="Reactor rule: prediction -> preemptive_heal at "
              "WARNING. Repaired at E-065 (docket 31): it now "
              "implements _execute under BaseAction's wrapper, "
              "guards Skuld's string capacity shapes, and "
              "returns real ActionResult records. Its own "
              "per-sub-action cooldowns stand in the action: "
              "disk_cleanup 3600, memory_cache_flush 1800, "
              "service_restart 7200, db_vacuum 86400.",
    ),
)


def spec_for(name: str) -> ReflexSpec | None:
    """The registered spec for a reflex name, or None.

    There is deliberately no open fallback: an unregistered
    action is not a reflex.
    """
    if not isinstance(name, str):
        return None
    for spec in REFLEX_SPECS:
        if spec.name == name:
            return spec
    return None


def validate_registry() -> list:
    """Errors in the reflex register itself; [] means sound."""
    errors = []
    names = [s.name for s in REFLEX_SPECS]
    if len(names) != len(set(names)):
        errors.append("reflex names are not unique")
    for spec in REFLEX_SPECS:
        if spec.speaks_for_companion:
            errors.append(f"{spec.name}: a reflex must never speak "
                          "for the companion")
        if SEVERITY_RANKS.get(spec.min_severity, -1) < MIN_REFLEX_RANK:
            errors.append(f"{spec.name}: min_severity "
                          f"{spec.min_severity!r} is below warning")
        if not spec.trigger_checks:
            errors.append(f"{spec.name}: no trigger checks")
        if spec.cooldown_seconds <= 0:
            errors.append(f"{spec.name}: cooldown must be positive")
        if not spec.action_class or not spec.effect:
            errors.append(f"{spec.name}: action class and effect required")
    return errors


def reflexes_for_trigger(check_name: str, severity: str) -> tuple:
    """The reflexes a check result may fire, by the fixed rules.

    Pure rule match: the check name must be one of the
    reflex's trigger checks and the severity rank must meet
    the reflex's floor. OK and UNKNOWN fire nothing.
    """
    rank = SEVERITY_RANKS.get(severity)
    if rank is None or rank < MIN_REFLEX_RANK:
        return ()
    return tuple(
        spec for spec in REFLEX_SPECS
        if check_name in spec.trigger_checks
        and rank >= SEVERITY_RANKS[spec.min_severity]
    )


def validate_reflex_result(result) -> list:
    """Errors in a reflex result record; [] means it is one.

    A valid result is a dict with exactly RESULT_FIELDS, a
    registered action_name, a severity in RESULT_SEVERITIES,
    and no speech field of any kind.
    """
    errors = []
    if not isinstance(result, dict):
        return ["reflex result must be a dict (the ActionResult record)"]
    for field in SPEECH_FIELDS:
        if field in result:
            errors.append(f"speech field {field!r}: a reflex never "
                          "speaks for the companion")
    extra = set(result) - set(RESULT_FIELDS)
    if extra:
        errors.append(f"unknown result fields: {sorted(extra)}")
    missing = set(RESULT_FIELDS) - set(result)
    if missing:
        errors.append(f"missing result fields: {sorted(missing)}")
    if spec_for(result.get("action_name")) is None:
        errors.append(f"action_name is not a registered reflex: "
                      f"{result.get('action_name')!r}")
    if result.get("severity") not in RESULT_SEVERITIES:
        errors.append(f"severity must be one of "
                      f"{sorted(RESULT_SEVERITIES)}, "
                      f"got {result.get('severity')!r}")
    if not isinstance(result.get("message"), str):
        errors.append("message must be a string (the record's summary)")
    return errors
