"""E-065 — The reflex layer: fast, dumb, safe reactions
below cognition (never speaks for the companion).

Pins Verdandi/reflexes.py against the tree it governs: the
register covers exactly the heartbeat actions that exist,
each spec matches its action class and its Reactor rule,
the safety shape holds (WARNING floor, positive cooldown,
BaseAction wrapper, ActionResult-only output), Vör — the
broken reflex, docket 31 — is repaired and covered by its
first tests, and the conversation reactor's focus
(docket 95) actually filters.
"""

import ast
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-065_REFLEX_LAYER.md"

sys.path.insert(0, str(VERDANDI))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reflexes = _load("ember_reflexes", VERDANDI / "reflexes.py")
conv_reactor = _load("ember_conv_reactor_e065", VERDANDI / "reactor.py")

from heartbeat.actions.base import (  # noqa: E402
    ACTION_REGISTRY, ActionContext, ActionSeverity, BaseAction,
)
import heartbeat.actions  # noqa: E402,F401  (populates the registry)
from heartbeat.actions.vor_action import VörAction  # noqa: E402
from heartbeat.checks.base import CheckResult, CheckSeverity  # noqa: E402
from heartbeat.reactor import Reactor  # noqa: E402


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ctx(details, severity=CheckSeverity.WARNING, dry_run=False):
    result = CheckResult(name="prediction", severity=severity,
                         message="prediction", details=details)
    return ActionContext(trigger_check="prediction",
                         trigger_result=result,
                         all_results={"prediction": result},
                         dry_run=dry_run)


# ── The register is well-formed and complete ────────────────


def test_version_and_registry_sound():
    assert reflexes.REFLEX_VERSION == 1
    assert reflexes.validate_registry() == []
    assert reflexes.spec_for("bogus") is None
    assert reflexes.spec_for(None) is None


def test_module_is_stdlib_only_and_self_contained():
    tree = ast.parse(_source(VERDANDI / "reflexes.py"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names)


def test_registry_covers_exactly_the_trees_actions():
    assert set(ACTION_REGISTRY) == {s.name for s in reflexes.REFLEX_SPECS}
    for spec in reflexes.REFLEX_SPECS:
        cls = ACTION_REGISTRY[spec.name]
        assert cls.name == spec.name
        assert tuple(cls.trigger_checks) == spec.trigger_checks, spec.name
        assert cls.trigger_severity.value == spec.min_severity, spec.name
        assert cls.cooldown_seconds == spec.cooldown_seconds, spec.name
        assert spec.speaks_for_companion is False


def test_reactor_rules_match_the_register():
    rules = {(r.check_name, r.action_name, r.min_severity.value)
             for r in Reactor().rules}
    assert rules == {
        ("projects", "auto_push", "warning"),
        ("schedule", "auto_restart", "warning"),
        ("memory", "auto_cleanup", "warning"),
        ("health", "auto_cleanup", "critical"),
        ("memory", "auto_heal", "critical"),
        ("prediction", "preemptive_heal", "warning"),
    }
    for check, action, severity in rules:
        assert reflexes.spec_for(action) is not None
        assert check in reflexes.spec_for(action).trigger_checks


def test_every_reflex_runs_under_the_base_wrapper():
    for name, cls in ACTION_REGISTRY.items():
        assert "_execute" in cls.__dict__, name
        # No reflex may override execute() and bypass the
        # wrapper (dry-run, duration, cooldown, crash fold).
        assert "execute" not in cls.__dict__, name
        assert cls.execute is BaseAction.execute, name


# ── Fast, dumb, safe: the rule match ────────────────────────


def test_rule_match_fires_only_at_warning_or_above():
    names = lambda rs: {s.name for s in rs}  # noqa: E731
    assert names(reflexes.reflexes_for_trigger("projects", "warning")) == {"auto_push"}
    assert names(reflexes.reflexes_for_trigger("memory", "warning")) == {"auto_cleanup"}
    assert names(reflexes.reflexes_for_trigger("memory", "critical")) == {
        "auto_cleanup", "auto_heal"}
    assert names(reflexes.reflexes_for_trigger("prediction", "warning")) == {
        "preemptive_heal"}
    for quiet in ("ok", "unknown"):
        assert reflexes.reflexes_for_trigger("memory", quiet) == ()
        assert reflexes.reflexes_for_trigger("prediction", quiet) == ()
    assert reflexes.reflexes_for_trigger("bogus", "critical") == ()
    assert reflexes.reflexes_for_trigger("memory", "bogus") == ()


def test_reflex_result_shape_never_speaks():
    good = {
        "action_name": "auto_heal", "severity": "success",
        "message": "Healed 1 targets, 0 failed", "details": {},
        "timestamp": "2026-10-31T00:00:00+00:00",
        "targets_affected": [], "targets_failed": [], "duration_ms": 1.0,
    }
    assert reflexes.validate_reflex_result(good) == []
    for bad in (
        {**good, "reply": "Don't worry, I fixed it"},
        {**good, "utterance": "I am healing the database"},
        {**good, "action_name": "not_a_reflex"},
        {**good, "severity": "info"},
        {k: v for k, v in good.items() if k != "details"},
        "not a dict",
    ):
        assert reflexes.validate_reflex_result(bad), bad


# ── Vör repaired (docket 31) — its first tests ──────────────

STRING_CAPACITY = {"capacity": {"status": "no_resource_data"}}
URGENCY_CAPACITY = {"capacity": {
    "disk": {"prediction": "exhaustion_predicted", "urgency": "warning"}}}


def test_vor_should_trigger_survives_skuld_string_capacity():
    vor = VörAction()
    # Skuld's own shapes: a string status value, and the
    # insufficient-data shape — neither may crash, neither
    # triggers.
    assert vor.should_trigger(_ctx(STRING_CAPACITY)) is False
    assert vor.should_trigger(_ctx({"capacity": {"status": "insufficient_data"}})) is False
    assert vor.should_trigger(_ctx({"capacity": "no_resource_data"})) is False
    assert vor.should_trigger(_ctx({})) is False


def test_vor_should_trigger_on_real_urgency():
    vor = VörAction()
    assert vor.should_trigger(_ctx(URGENCY_CAPACITY)) is True
    assert vor.should_trigger(_ctx(URGENCY_CAPACITY,
                                   severity=CheckSeverity.OK)) is False


def test_vor_capacity_helpers_drop_string_shapes():
    vor = VörAction()
    assert vor._get_capacity_prediction(_ctx(STRING_CAPACITY)) == {}
    assert vor._get_capacity_summary(_ctx(STRING_CAPACITY)) == {}
    assert vor._get_capacity_prediction(_ctx(URGENCY_CAPACITY)) == URGENCY_CAPACITY["capacity"]
    assert vor._get_capacity_summary(_ctx(URGENCY_CAPACITY)) == {
        "disk": "exhaustion_predicted"}


def test_vor_no_action_result_is_a_real_record():
    vor = VörAction()
    result = vor.execute(_ctx(STRING_CAPACITY))
    assert result.action_name == "preemptive_heal"
    assert result.severity == ActionSeverity.SKIPPED
    assert result.message == "No pre-emptive actions needed at this time"
    assert reflexes.validate_reflex_result(result.to_dict()) == []


def test_vor_runs_under_the_wrapper_dry_run():
    vor = VörAction()
    result = vor.execute(_ctx(URGENCY_CAPACITY, dry_run=True))
    # The wrapper's dry-run answer, not Vör's own code —
    # proof the reflex runs under BaseAction.execute.
    assert result.severity == ActionSeverity.DRY_RUN
    assert result.action_name == "preemptive_heal"


def test_vor_preemptive_disk_path():
    vor = VörAction()
    result = vor._execute(_ctx(URGENCY_CAPACITY, dry_run=True))
    assert result.severity == ActionSeverity.SUCCESS
    assert result.details["actions_taken"] == [
        "disk_cleanup:would_clean_logs_and_temp_files"]
    assert reflexes.validate_reflex_result(result.to_dict()) == []


def test_vor_source_has_no_broken_constructions_left():
    src = _source(VERDANDI / "heartbeat" / "actions" / "vor_action.py")
    assert "def _execute" in src
    assert "ActionSeverity.INFO" not in src
    assert "ActionResult(\n                name=" not in src
    assert "action_name=self.name" in src


# ── Conversation reactor focus (docket 95) ──────────────────


def _seed_reactor(tmp_path, monkeypatch):
    state = tmp_path / "state"
    state.mkdir(parents=True)
    log = state / "conversation_log.jsonl"
    current = state / "current.json"
    monkeypatch.setattr(conv_reactor, "STATE_DIR", state)
    monkeypatch.setattr(conv_reactor, "CONV_LOG", log)
    monkeypatch.setattr(conv_reactor, "CURRENT_FILE", current)
    now = datetime.now(timezone.utc).isoformat()
    entries = [
        {"entry_type": "start", "session_id": "s1", "timestamp": now},
        {"entry_type": "event", "session_id": "s1", "timestamp": now,
         "event_type": "blocker", "content": "Stuck thing"},
        {"entry_type": "event", "session_id": "s1", "timestamp": now,
         "event_type": "learned", "content": "A lesson"},
        {"entry_type": "event", "session_id": "s1", "timestamp": now,
         "event_type": "file_changed", "content": "a.py"},
        {"entry_type": "end", "session_id": "s1", "timestamp": now},
    ]
    log.write_text("".join(json.dumps(e) + "\n" for e in entries),
                   encoding="utf-8")
    current.write_text(json.dumps(
        {"session_id": "s1", "next_actions": ["Do the next thing"]}),
        encoding="utf-8")


def test_focus_all_is_the_default_and_complete(tmp_path, monkeypatch):
    _seed_reactor(tmp_path, monkeypatch)
    full = conv_reactor.react()
    assert full == conv_reactor.react(focus="all")
    assert len(full["blockers_needing_reaction"]) == 1
    assert len(full["recent_learnings_to_store"]) == 1
    assert len(full["files_changed_needing_push"]) == 1
    assert len(full["next_actions_to_pick_up"]) == 1
    assert len(full["reactions"]) >= 4


def test_focus_keeps_only_its_category_and_directive(tmp_path, monkeypatch):
    _seed_reactor(tmp_path, monkeypatch)
    cases = {
        "blockers": ("blockers_needing_reaction", "resolve_blockers"),
        "learnings": ("recent_learnings_to_store", "store_learnings"),
        "files": ("files_changed_needing_push", "verify_pushed"),
        "next": ("next_actions_to_pick_up", "continue_work"),
    }
    for focus, (category, action) in cases.items():
        out = conv_reactor.react(focus=focus)
        assert len(out[category]) == 1, focus
        assert [r["action"] for r in out["reactions"]] == [action], focus
        for key, value in out.items():
            if key not in (category, "reactions"):
                assert value == [], (focus, key)


def test_focus_unknown_is_refused_not_ignored(tmp_path, monkeypatch):
    _seed_reactor(tmp_path, monkeypatch)
    try:
        conv_reactor.react(focus="bogus")
    except ValueError as e:
        assert "bogus" in str(e)
    else:
        raise AssertionError("unknown focus silently accepted")
    src = _source(VERDANDI / "reactor.py")
    assert "FOCUS_MAP" in src and "FOCUS_CHOICES" in src
    assert 'choices=["all", "blockers", "learnings", "files", "next"]' in src


def test_doc_names_every_reflex_and_the_never_speaks_rule():
    doc = _source(DOC)
    for spec in reflexes.REFLEX_SPECS:
        assert spec.name in doc, spec.name
    for needle in ("never speaks", "Docket 31", "Docket 95",
                   "BaseAction", "WARNING", "E-066", "E-067", "E-070"):
        assert needle in doc, needle
