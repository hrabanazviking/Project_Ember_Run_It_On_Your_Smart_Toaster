"""E-074 — Docs: the nerve model for member-builders.

Pins docs/architecture/E-074_NERVE_MODEL_FOR_MEMBER_BUILDERS.md:

- every Part IV slice E-059..E-073 is represented in the doc;
- every repo path the doc names in backticks exists;
- every (file, entry point) row in the doc's builder table
  is real: the file exists and the symbol is defined at its
  top level (or, for constants, assigned there);
- the doc's three worked python examples run as written,
  from the repo root, in a bare interpreter.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-074_NERVE_MODEL_FOR_MEMBER_BUILDERS.md"

SLICES = [f"E-{n:03d}" for n in range(59, 75)]

# The builder table the doc publishes: file -> entry points.
BUILDER_TABLE = {
    "Verdandi/event_contract.py": [
        "validate_publish", "normalize_event", "spec_for",
        "classify_dialect", "CONTRACT_VERSION"],
    "Verdandi/nervous_system.py": ["publish_event_sync"],
    "Verdandi/context_budget.py": ["TOTAL_MAX_CHARS", "LAYER_SHED_ORDER"],
    "Verdandi/logger_law.py": [
        "ENTRY_TYPES", "EVENT_TYPES", "DELETE_SCOPE_FILES"],
    "Verdandi/stimuli.py": [
        "make_stimulus", "to_event", "from_event", "validate_stimulus"],
    "Verdandi/reflexes.py": [
        "reflexes_for_trigger", "validate_reflex_result", "validate_registry"],
    "Verdandi/nerve_health.py": [
        "classify_nerve_health", "NerveObservations", "validate_classification"],
    "Verdandi/cross_member.py": [
        "build_event", "validate_cross_event", "spec_for_cross"],
    "src/ember/nerve.py": [
        "publish_session", "publish_turn", "read_recent",
        "read_recent_for_persona", "filter_for_persona", "hub_state_dir"],
    "Verdandi/hermes_nerves.py": [
        "normalize_hermes_event", "validate_hermes_event",
        "is_hermes_event", "spec_for_hermes"],
    "Verdandi/replay.py": [
        "order_events", "replay_feed_lines", "replay_digest",
        "validate_replay_order"],
    "Verdandi/backpressure.py": [
        "tier_of", "apply_backpressure", "BackpressureQueue", "pressure_level"],
    "Verdandi/nerve_privacy.py": [
        "filter_events_for_persona", "redact_provenance", "event_persona"],
    "Verdandi/memory_feed.py": [
        "feed_candidates", "feed_log_entries", "validate_rule"],
    "Verdandi/standalone.py": ["resolve_state_dir", "standalone_manifest"],
}


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def _top_level_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def test_doc_exists_and_covers_every_part_iv_slice():
    text = _text()
    for slice_id in SLICES:
        assert slice_id in text, f"{slice_id} law not represented"


def test_every_backticked_repo_path_in_the_doc_exists():
    text = _text()
    checked = set()
    for token in re.findall(r"`([^`\n]+)`", text):
        if re.match(r"^(Verdandi|src|docs|tests)/\S+$", token) and (
                token.endswith((".py", ".md"))):
            checked.add(token)
            assert (REPO / token).is_file(), f"doc names missing path: {token}"
    assert len(checked) >= 25, "path check found suspiciously few paths"


def test_builder_table_is_real_and_printed():
    text = _text()
    for rel, symbols in BUILDER_TABLE.items():
        assert rel in text, f"builder table omits {rel}"
        names = _top_level_names(REPO / rel)
        for symbol in symbols:
            assert symbol in text, f"doc does not name {rel}:{symbol}"
            assert symbol in names, f"{symbol} not defined at top level of {rel}"


def test_doc_states_the_load_truth_limit():
    # E-075 owns throughput numbers; the builder doc must not invent any.
    text = _text()
    assert "E-075" in text
    assert not re.search(r"\b\d[\d,]*\s*(events|messages)/s\b", text)


def _python_blocks() -> list[str]:
    return re.findall(r"```python\n(.*?)```", _text(), flags=re.S)


def test_worked_examples_run_as_written(tmp_path):
    blocks = _python_blocks()
    assert len(blocks) == 3, f"expected 3 worked examples, found {len(blocks)}"
    for i, block in enumerate(blocks):
        script = tmp_path / f"example_{i}.py"
        script.write_text(block, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(script)], cwd=REPO,
            env={**os.environ, "PYTHONPATH": str(REPO / "src")},
            capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, (
            f"example {i} failed:\n{result.stdout}\n{result.stderr}")
        assert f"example {'ABC'[i]}:" in result.stdout
