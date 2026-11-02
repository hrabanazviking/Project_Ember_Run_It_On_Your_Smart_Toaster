"""E-062 — Context injection discipline conformance.

Pins Verdandi/context_budget.py against the code it governs:
the budget literals conversation_logger.py carries (deployed
copies, pinned equal so they cannot drift), the allowed-source
list against the logger's actual reads, and the behavioural
rules — what may be injected, when the layers shed, and the
hard total ceiling — exercised against adversarial fixtures
(huge blockers, huge items, many sessions, a flooded nerve
feed, a flooded reactor) in an isolated state dir.
"""

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-062_CONTEXT_INJECTION_DISCIPLINE.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


budget = _load("ember_context_budget", VERDANDI / "context_budget.py")
logger = _load("ember_conversation_logger_e062", VERDANDI / "conversation_logger.py")


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _literal_assigns(path: Path, prefix: str) -> dict:
    tree = ast.parse(_source(path))
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id.startswith(prefix):
                try:
                    out[target.id] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass
    return out


# ── The budget is well-formed ───────────────────────────────────


def test_layer_ceilings_sum_to_the_total():
    layers = (budget.CURRENT_MAX_CHARS + budget.RECENT_MAX_CHARS
              + budget.NERVE_MAX_CHARS + budget.REACTIONS_MAX_CHARS)
    assert layers == budget.TOTAL_MAX_CHARS
    assert budget.TOTAL_MAX_CHARS == 4000
    assert budget.CONTEXT_BUDGET_VERSION == 1


def test_shed_order_is_reactions_nerve_recent_current():
    order = budget.LAYER_SHED_ORDER
    assert order["reactions"] > order["nerve"] > order["recent"] > order["current"]


def test_allowed_sources_are_exactly_the_three_state_files():
    assert set(budget.ALLOWED_SOURCE_FILES) == {
        "current.json", "conversation_log.jsonl", "nerve_feed.jsonl",
    }


def test_budget_module_is_stdlib_only_and_self_contained():
    tree = ast.parse(_source(VERDANDI / "context_budget.py"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names)
    assert "conversation_logger" not in imports and "reactor" not in imports


# ── The logger's deployed literals cannot drift ─────────────────


def test_logger_literals_match_the_budget_module():
    literals = _literal_assigns(VERDANDI / "conversation_logger.py", "_CONTEXT_")
    pairs = {
        "_CONTEXT_TOTAL_MAX_CHARS": budget.TOTAL_MAX_CHARS,
        "_CONTEXT_CURRENT_MAX_CHARS": budget.CURRENT_MAX_CHARS,
        "_CONTEXT_RECENT_MAX_CHARS": budget.RECENT_MAX_CHARS,
        "_CONTEXT_NERVE_MAX_CHARS": budget.NERVE_MAX_CHARS,
        "_CONTEXT_REACTIONS_MAX_CHARS": budget.REACTIONS_MAX_CHARS,
        "_CONTEXT_SUMMARY_MAX_CHARS": budget.SUMMARY_MAX_CHARS,
        "_CONTEXT_RECENT_SUMMARY_MAX_CHARS": budget.RECENT_SUMMARY_MAX_CHARS,
        "_CONTEXT_DECISIONS_MAX_ITEMS": budget.DECISIONS_MAX_ITEMS,
        "_CONTEXT_NEXT_ACTIONS_MAX_ITEMS": budget.NEXT_ACTIONS_MAX_ITEMS,
        "_CONTEXT_BLOCKERS_MAX_ITEMS": budget.BLOCKERS_MAX_ITEMS,
        "_CONTEXT_PROJECTS_MAX_ITEMS": budget.PROJECTS_MAX_ITEMS,
        "_CONTEXT_LIST_ITEM_MAX_CHARS": budget.LIST_ITEM_MAX_CHARS,
        "_CONTEXT_PROJECT_ITEM_MAX_CHARS": budget.PROJECT_ITEM_MAX_CHARS,
        "_CONTEXT_BLOCKERS_JOIN_MAX_CHARS": budget.BLOCKERS_JOIN_MAX_CHARS,
        "_CONTEXT_DECISIONS_JOIN_MAX_CHARS": budget.DECISIONS_JOIN_MAX_CHARS,
        "_CONTEXT_NEXT_ACTIONS_JOIN_MAX_CHARS": budget.NEXT_ACTIONS_JOIN_MAX_CHARS,
        "_CONTEXT_PROJECTS_JOIN_MAX_CHARS": budget.PROJECTS_JOIN_MAX_CHARS,
        "_CONTEXT_RECENT_MAX_SESSIONS": budget.RECENT_MAX_SESSIONS,
        "_CONTEXT_NERVE_MAX_EVENTS": budget.NERVE_MAX_EVENTS,
        "_CONTEXT_NERVE_DATA_MAX_CHARS": budget.NERVE_DATA_MAX_CHARS,
        "_CONTEXT_NERVE_SOURCE_MAX_CHARS": budget.NERVE_SOURCE_MAX_CHARS,
        "_CONTEXT_NERVE_TYPE_MAX_CHARS": budget.NERVE_TYPE_MAX_CHARS,
        "_CONTEXT_REACTIONS_MAX_DIRECTIVES": budget.REACTIONS_MAX_DIRECTIVES,
        "_CONTEXT_REACTIONS_ITEMS_PER_DIRECTIVE": budget.REACTIONS_ITEMS_PER_DIRECTIVE,
        "_CONTEXT_REACTION_ITEM_MAX_CHARS": budget.REACTION_ITEM_MAX_CHARS,
        "_CONTEXT_REACTION_DETAIL_MAX_CHARS": budget.REACTION_DETAIL_MAX_CHARS,
        "_CONTEXT_TRUNCATION_MARKER": budget.TRUNCATION_MARKER,
    }
    for name, expected in pairs.items():
        assert literals.get(name) == expected, f"{name}: logger has {literals.get(name)!r}, budget has {expected!r}"


def test_logger_reads_nerve_feed_from_its_own_state_dir():
    src = _source(VERDANDI / "conversation_logger.py")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "get_context_for_cron")
    fn_src = ast.get_source_segment(src, fn)
    assert 'STATE_DIR / "nerve_feed.jsonl"' in fn_src
    assert "Path.home()" not in fn_src  # no second hardcoded home path


def test_injector_echo_block_uses_the_caps():
    src = _source(VERDANDI / "context_injector.py")
    assert "_ctx_cap(state['blockers']" in src
    assert "_ctx_cap(state['next_actions']" in src
    assert "state['blockers'])}" not in src.replace("_ctx_cap(state['blockers']", "")


# ── Behaviour under adversarial fixtures ────────────────────────


@pytest.fixture()
def state(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(logger, "STATE_DIR", state_dir)
    monkeypatch.setattr(logger, "CONV_DIR", state_dir / "conversations")
    monkeypatch.setattr(logger, "CURRENT_FILE", state_dir / "current.json")
    monkeypatch.setattr(logger, "CONV_LOG", state_dir / "conversation_log.jsonl")
    # No reactor in the isolated state dir: the reactions layer
    # must stay failure-silent (absent, never fabricated).
    monkeypatch.setattr(sys, "path", [p for p in sys.path if "state" not in p])
    return state_dir


def _write_current(state_dir: Path, **fields):
    current = {"session_id": "s1", "status": "active",
               "last_updated": "2026-10-31T00:00:00+00:00", "summary": "ok"}
    current.update(fields)
    (state_dir / "current.json").write_text(json.dumps(current))


def _write_log(state_dir: Path, sessions: int, summary_len: int = 50):
    lines = []
    for i in range(sessions):
        lines.append(json.dumps({
            "entry_type": "start", "timestamp": f"2026-10-{10 + i:02d}T00:00:00+00:00",
            "session_id": f"sess-{i}", "summary": "x" * summary_len,
        }))
    (state_dir / "conversation_log.jsonl").write_text("\n".join(lines) + "\n")


def _write_nerve(state_dir: Path, events: int, data_len: int = 50):
    lines = []
    for i in range(events):
        lines.append(json.dumps({
            "type": f"ev{i}", "source": "test", "_iso": "2026-10-31T00:00:00+00:00",
            "data": {"msg": "y" * data_len},
        }))
    (state_dir / "nerve_feed.jsonl").write_text("\n".join(lines) + "\n")


def test_empty_state_block_is_small_and_honest(state):
    block = logger.get_context_for_cron()
    assert "RUNA SESSION CONTEXT" in block and "END CONTEXT" in block
    assert len(block) <= budget.TOTAL_MAX_CHARS
    assert "NERVE FEED" not in block and "REACTION DIRECTIVES" not in block


def test_blockers_are_capped_in_count_and_length(state):
    _write_current(state, blockers=["B" * 500] * 40)
    block = logger.get_context_for_cron()
    blocker_line = next(l for l in block.splitlines() if l.startswith("Blockers:"))
    items = blocker_line[len("Blockers: "):].split("; ")
    assert len(items) <= budget.BLOCKERS_MAX_ITEMS
    assert all(len(i) <= budget.LIST_ITEM_MAX_CHARS for i in items)


def test_decisions_and_next_actions_are_capped(state):
    _write_current(state, decisions=["D" * 400] * 20, next_actions=["N" * 400] * 20)
    block = logger.get_context_for_cron()
    for label, cap in (("Decisions:", budget.DECISIONS_MAX_ITEMS),
                       ("Next actions:", budget.NEXT_ACTIONS_MAX_ITEMS)):
        line = next(l for l in block.splitlines() if l.startswith(label))
        items = line[len(label) + 1:].split("; ")
        assert len(items) <= cap
        assert all(len(i) <= budget.LIST_ITEM_MAX_CHARS for i in items)


def test_projects_are_capped(state):
    _write_current(state, projects_touched=["P" * 300] * 30)
    block = logger.get_context_for_cron()
    line = next(l for l in block.splitlines() if l.startswith("Projects touched:"))
    items = line[len("Projects touched: "):].split(", ")
    assert len(items) <= budget.PROJECTS_MAX_ITEMS
    assert all(len(i) <= budget.PROJECT_ITEM_MAX_CHARS for i in items)


def test_max_sessions_request_is_clamped(state):
    _write_log(state, sessions=12)
    block = logger.get_context_for_cron(max_sessions=50)
    assert len(block) <= budget.TOTAL_MAX_CHARS
    assert block.count("sess-") <= budget.RECENT_MAX_SESSIONS + 1  # +current header none; recent lines only
    recent_section = block.split("--- Recent")[1].split("===")[0] if "--- Recent" in block else ""
    assert recent_section.count("sess-") <= budget.RECENT_MAX_SESSIONS


def test_nerve_tail_is_capped_to_last_ten(state):
    _write_nerve(state, events=25, data_len=40)
    block = logger.get_context_for_cron()
    assert "ev24" in block  # the newest survives
    assert "ev0]" not in block and "[ev1]" not in block  # the oldest are out of the tail
    nerve_lines = [l for l in block.splitlines() if " from test:" in l]
    assert len(nerve_lines) <= budget.NERVE_MAX_EVENTS


def test_total_ceiling_holds_under_full_adversarial_load(state):
    _write_current(state,
                   summary="S" * 5000,
                   blockers=["B" * 500] * 40,
                   decisions=["D" * 500] * 20,
                   next_actions=["N" * 500] * 20,
                   projects_touched=["P" * 300] * 30)
    _write_log(state, sessions=12, summary_len=500)
    _write_nerve(state, events=25, data_len=500)
    block = logger.get_context_for_cron(max_sessions=50)
    assert len(block) <= budget.TOTAL_MAX_CHARS
    assert block.startswith("=== RUNA SESSION CONTEXT")
    assert "Blockers:" in block  # the last-to-shed content survives


def test_truncation_is_marked_not_silent(state):
    _write_current(state, blockers=["B" * 500] * 40,
                   decisions=["D" * 500] * 20, next_actions=["N" * 500] * 20,
                   projects_touched=["P" * 300] * 30)
    block = logger.get_context_for_cron()
    assert budget.TRUNCATION_MARKER in block


def test_reactions_layer_is_capped_when_a_reactor_exists(state, tmp_path):
    # A reactor living in the state dir (the deployed shape)
    # that floods its directives: items and detail must cap,
    # and the total must hold.
    reactor_src = (
        "def react(focus='all'):\n"
        "    return {'reactions': [{'priority': 'HIGH', 'action': 'act',\n"
        "                             'detail': 'd' * 900,\n"
        "                             'items': ['i' * 900] * 9} for _ in range(9)]}\n"
    )
    (state / "reactor.py").write_text(reactor_src)
    _write_current(state)
    block = logger.get_context_for_cron()
    assert len(block) <= budget.TOTAL_MAX_CHARS
    if "REACTION DIRECTIVES" in block:
        items = [l for l in block.splitlines() if l.startswith("  • ")]
        assert all(len(l) <= budget.REACTION_ITEM_MAX_CHARS + 4 for l in items)


def test_helper_caps_match_the_module_semantics():
    assert budget.truncate_text("abcdef", 3) == "abc"
    assert budget.cap_items(["a" * 10] * 5, 2, 4) == ["aaaa", "aaaa"]
    assert logger._ctx_cap(["a" * 10] * 5, 2, 4) == ["aaaa", "aaaa"]


def test_doc_names_the_budget_and_sources():
    doc = _source(DOC)
    for needle in ("4000", "current.json", "conversation_log.jsonl",
                   "nerve_feed.jsonl", budget.TRUNCATION_MARKER):
        assert needle in doc, needle
