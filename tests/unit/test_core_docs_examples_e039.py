"""E-039 — Core docs + runnable examples.

The roadmap line asks for two things, and both are pinned here:

- **Runnable examples.** `examples/` held only scaffolds whose
  own README states the law — "Examples must actually run
  against the current `src/ember/`" — while containing no
  runnable example at all. E-039 lands three standalone
  programs plus one worked config file. Each test runs an
  example as a real subprocess in a bare interpreter (stdlib +
  `src` only, a scratch working directory), and fails if it
  exits nonzero, loses its expected output, or writes anything
  into the caller's directory. The member-binding example is
  additionally AST-scanned: it may import only frozen API v1
  bind points (E-037), the discipline members are held to.
- **Core docs that match the code.** Docket 84 named
  `docs/architecture/DATA_FLOW.md` stale against the code in
  four places (retrieval k=8 for the code's k=5, a "no
  streaming / no tool use" §7 the shipped core contradicts, a
  nonexistent `AskTurn` type, and a pending journal drawn as a
  SQLite file instead of per-turn JSON). E-039 corrects those
  facts in place and pins them here; the whole-docs
  reconciliation stays E-194's. The E-039 doc itself is
  link-checked: every repo path it names must exist.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"
DATA_FLOW = REPO_ROOT / "docs" / "architecture" / "DATA_FLOW.md"
E039_DOC = REPO_ROOT / "docs" / "architecture" / "E-039_CORE_DOCS_EXAMPLES.md"
EXAMPLE_CONFIG = EXAMPLES / "configs" / "phone-class.toml"


def _run_example(name: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, str(EXAMPLES / name)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


# --------------------------------------------------------------------- #
# The examples run — really, as subprocesses, leaving nothing behind    #
# --------------------------------------------------------------------- #


def test_first_chat_example_runs_and_remembers_one_turn(tmp_path: Path) -> None:
    result = _run_example("first_chat.py", tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Hello! I am Ember, your small local companion." in result.stdout
    assert "first_chat: exit 0, 1 turn(s) remembered" in result.stdout
    # The example keeps its state in a temp dir: the caller's
    # directory stays exactly as empty as it started.
    assert list(tmp_path.iterdir()) == []


def test_member_binding_example_runs_through_the_frozen_api(tmp_path: Path) -> None:
    result = _run_example("member_binding.py", tmp_path)
    assert result.returncode == 0, result.stderr
    assert "core API version: 1.0.0" in result.stdout
    assert "surface problems: 0" in result.stdout
    assert "profile=phone, history budget=1024 tokens" in result.stdout
    assert "member_binding: OK" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_offline_turns_example_runs_and_drains(tmp_path: Path) -> None:
    result = _run_example("offline_turns.py", tmp_path)
    assert result.returncode == 0, result.stderr
    assert "reply is ungrounded" in result.stdout
    assert "turns saved in the pending journal: 1" in result.stdout
    assert "turns added to the Well: 1" in result.stdout
    assert "offline_turns: OK" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_examples_are_valid_python_and_carry_run_instructions() -> None:
    for name in ("first_chat.py", "member_binding.py", "offline_turns.py"):
        source = (EXAMPLES / name).read_text(encoding="utf-8")
        ast.parse(source)  # raises on a syntax error
        # Each example tells a normal person how to run it, in
        # its own head — the "for normal folks" law.
        assert f"python3 examples/{name}" in source


# --------------------------------------------------------------------- #
# The member example binds through frozen surface only (E-037)          #
# --------------------------------------------------------------------- #

_FROZEN_BIND_POINTS = {
    "ember",
    "ember.api",
    "ember.config",
    "ember.diary",
    "ember.spark.cognition",
    "ember.spark.conversation",
    "ember.spark.funi",
    "ember.spark.persona",
    "ember.thread.strengr",
    "ember.well.brunnr",
    "ember.well.pending_journal",
}


def _imports_of(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_member_binding_imports_only_frozen_bind_points() -> None:
    imports = _imports_of(EXAMPLES / "member_binding.py")
    ember_imports = {name for name in imports if name == "ember" or name.startswith("ember.")}
    allowed = _FROZEN_BIND_POINTS | {
        name
        for name in ember_imports
        if any(name.startswith(prefix + ".") for prefix in _FROZEN_BIND_POINTS)
        or name.startswith("ember.schemas.")
    }
    assert ember_imports <= allowed, (
        f"unfrozen imports in the member example: {sorted(ember_imports - allowed)}"
    )
    # And it really does bind: the version gate is exercised.
    assert "ember.api" in imports


# --------------------------------------------------------------------- #
# The worked config example loads exactly as written                    #
# --------------------------------------------------------------------- #


def test_phone_class_example_config_loads() -> None:
    from ember.config import load_ember_config
    from ember.schemas.config import ConversationProfile

    config = load_ember_config(file_override=EXAMPLE_CONFIG, skip_env=True)
    assert config.conversation.profile is ConversationProfile.PHONE
    assert config.conversation.resolved_token_budget == 1024
    assert config.conversation.resolved_max_episodes == 5
    assert config.identity.name == "Ember"
    assert config.logging.diary is True


# --------------------------------------------------------------------- #
# DATA_FLOW tells the truth now (docket 84, E-039 half)                 #
# --------------------------------------------------------------------- #


def test_data_flow_facts_match_the_code() -> None:
    text = DATA_FLOW.read_text(encoding="utf-8")
    # Retrieval is k=5 in both the hybrid and the text path.
    assert "k=5" in text
    assert "k=8" not in text
    # There is no AskTurn type; the operator's line travels.
    assert "AskTurn(text" not in text
    assert "no\n    `AskTurn` type" in text or "no `AskTurn` type" in text
    # The pending journal is per-turn JSON files, not a SQLite file.
    assert "tiny SQLite file" not in text
    assert "one\n    small JSON file per turn" in text or "JSON file per turn" in text
    # §7's negative space no longer denies shipped behaviour.
    assert "No streaming in the first slice" not in text
    assert "Streaming is the default" in text
    # The correction is owned, in the open, at the doc's head.
    assert "docket 84" in text
    assert "E-039" in text


# --------------------------------------------------------------------- #
# The E-039 doc names only paths that exist                             #
# --------------------------------------------------------------------- #


def test_e039_doc_paths_all_exist() -> None:
    text = E039_DOC.read_text(encoding="utf-8")
    named = set(re.findall(r"`((?:docs|examples|src|tests|config)/[^`\s]+)`", text))
    assert named, "the E-039 doc should name the docs and examples it files"
    missing = [p for p in sorted(named) if not (REPO_ROOT / p).exists()]
    assert missing == [], f"E-039 doc names paths that do not exist: {missing}"
    for name in ("first_chat.py", "member_binding.py", "offline_turns.py"):
        assert f"examples/{name}" in text
    assert "examples/configs/phone-class.toml" in text
