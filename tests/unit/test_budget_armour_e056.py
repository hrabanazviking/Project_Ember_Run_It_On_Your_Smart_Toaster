"""E-056 — Regression armour: budget tests join the permanent gate.

E-042 wired the first budget tests into the campaign's
whole-suite slice gate by placing them under ``tests/unit/``,
and every Part III slice after it (E-043–E-055) followed.
That made the budgets a gate *of this campaign*. E-056 makes
them a gate *of the project*: one command —
``scripts/dev/run_budget_gate.py`` — runs all fifteen budget
test files, and the script's ``BUDGET_TEST_FILES`` manifest
is the single enrolment list.

These tests are the armour's keeper, not budget tests
themselves (they re-measure nothing, so they are not in the
manifest). They hold the gate honest from both sides:

* **Enrolled means real:** every manifest entry exists,
  lives under ``tests/unit/`` (so Runs B/D of the whole
  suite still collect it — the armour stands in both
  gates), and names a file holding at least one test.
* **Real means enrolled:** every ``tests/unit/`` file
  carrying a Part III slice number (E-041–E-055, by its
  ``_eNNN`` filename suffix) is in the manifest, in
  roadmap order, with no duplicates — a future budget
  test that is never enrolled fails here instead of
  silently gating nothing.
* **The command is the manifest:** the script's pytest
  command is exactly the manifest files (plus ``-q``),
  ``--list`` prints exactly the manifest, and
  ``--collect-only`` through the real script collects
  every enrolled file (a subprocess check — collection
  is the wiring, proven, not asserted from paths alone).
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = REPO_ROOT / "scripts" / "dev" / "run_budget_gate.py"
_UNIT = REPO_ROOT / "tests" / "unit"

#: Part III's slice numbers, E-041–E-055: the slices whose
#: gate tests are the budget armour.
_PART_III = re.compile(r"_e0(4[1-9]|5[0-5])\.py$")


def _gate_module():
    spec = importlib.util.spec_from_file_location("run_budget_gate", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest() -> tuple[str, ...]:
    return _gate_module().BUDGET_TEST_FILES


def test_gate_script_exists_and_enrols_fifteen_files() -> None:
    manifest = _manifest()
    assert len(manifest) == 15  # one per slice, E-041–E-055
    assert len(set(manifest)) == 15, "no file enrolled twice"


def test_every_enrolled_file_is_real_and_holds_tests() -> None:
    for relative in _manifest():
        path = REPO_ROOT / relative
        assert path.is_file(), f"enrolled but missing: {relative}"
        # Under tests/unit/, so the whole-suite slice gate
        # (Runs B/D) collects it too — both gates, not one.
        assert path.parent == _UNIT, relative
        text = path.read_text(encoding="utf-8")
        assert "def test_" in text, f"enrolled file holds no test: {relative}"


def test_every_part_iii_budget_file_is_enrolled_in_order() -> None:
    # Discovery is by slice number (roadmap order), not by
    # filename alphabet — the manifest's order is E-041 first.
    def slice_number(path: Path) -> int:
        match = _PART_III.search(path.name)
        assert match is not None
        return int(path.name.rsplit("_e", 1)[1].removesuffix(".py"))

    discovered = [
        f"tests/unit/{path.name}"
        for path in sorted(
            (p for p in _UNIT.glob("test_*.py") if _PART_III.search(p.name)),
            key=slice_number,
        )
    ]
    assert list(_manifest()) == discovered, (
        "a Part III budget test file is not enrolled in the "
        "permanent gate (or the manifest is out of order): "
        f"manifest={list(_manifest())} discovered={discovered}"
    )


def test_gate_command_is_exactly_the_manifest() -> None:
    module = _gate_module()
    command = module.build_command([])
    assert command[:3] == [sys.executable, "-m", "pytest"]
    assert command[3:-1] == list(module.BUDGET_TEST_FILES)
    assert command[-1] == "-q"
    collected = module.build_command([], collect_only=True)
    assert "--collect-only" in collected


def test_list_mode_prints_exactly_the_manifest() -> None:
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--list"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == list(_manifest())


def test_collect_only_through_the_script_collects_every_file() -> None:
    # The wiring, proven through the real command: pytest's
    # own collection names every enrolled file. (Default
    # env: sqlite_vec-gated files still COLLECT — their
    # skips are runtime guards, not import gates.)
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--collect-only"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    for relative in _manifest():
        assert Path(relative).name in result.stdout, relative


def test_armour_keeper_is_wired_into_the_whole_suite() -> None:
    # This keeper file itself lives under tests/unit/, where
    # Runs B/D collect it on every future slice.
    assert Path(__file__).parent.name == "unit"
