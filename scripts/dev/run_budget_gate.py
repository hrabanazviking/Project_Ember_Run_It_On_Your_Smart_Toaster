#!/usr/bin/env python3
"""The permanent budget gate — Project Ember, slice E-056.

What it does
------------
Runs every Part III budget test (slices E-041–E-055) as ONE
command, from the repository root:

    python3 scripts/dev/run_budget_gate.py

Before E-056 the budget armour was fifteen test files under
``tests/unit/``. They ran inside the campaign's whole-suite
slice gates (the E-017 method's Runs B/D), but there was no
single command a maintainer — or a future campaign, or a
release check (E-200) — could run to ask only the budget
question: *does the core still fit the profiles it promises?*

This script is that command. ``BUDGET_TEST_FILES`` below is
the gate's manifest: the fifteen files, in roadmap order.
The E-056 tests (``tests/unit/test_budget_armour_e056.py``)
hold this manifest honest from both sides:

* every file named here exists under ``tests/unit/``, so the
  whole-suite gates collect it too (the armour is in BOTH
  gates — this one-command gate and the whole suite);
* every ``tests/unit/`` test file carrying a Part III slice
  number (E-041–E-055) is named here — a budget test added
  by a future slice but never enrolled silently stops
  gating nowhere: it fails the E-056 completeness test
  until it is enrolled here, in order.

Behaviour
---------
* Read-only: the script runs pytest; it writes nothing of
  its own (pytest's own caches aside).
* Exit code is pytest's exit code, propagated unchanged —
  0 only when every budget test passes or skips honestly
  (the extras-gated shapes skip where ``sqlite_vec`` is
  absent, exactly as they do in the whole suite).
* ``--list`` prints the manifest, one path per line, and
  runs nothing. ``--collect-only`` passes through to
  pytest's collection (a fast wiring check). Any other
  arguments after ``--`` are passed to pytest unchanged.
* ``PYTHONPATH`` is set so ``src/`` leads it, matching the
  suite's own convention (``tests/conftest.py`` does the
  same in-process); an existing ``PYTHONPATH`` is kept
  behind it. All other environment (notably ``TMPDIR``)
  is inherited untouched.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The budget armour, in roadmap order (E-041–E-055). One
#: entry per Part III slice that landed gate tests; E-056's
#: own tests are the armour's keeper, not a budget test, and
#: are deliberately NOT in this list (they run in the whole
#: suite and judge this manifest).
BUDGET_TEST_FILES: tuple[str, ...] = (
    "tests/unit/test_budgets_e041.py",
    "tests/unit/test_budget_gate_e042.py",
    "tests/unit/test_install_weight_e043.py",
    "tests/unit/test_dependency_diet_e044.py",
    "tests/unit/test_idle_discipline_e045.py",
    "tests/unit/test_cold_start_e046.py",
    "tests/unit/test_pi_proof_e047.py",
    "tests/unit/test_phone_proof_e048.py",
    "tests/unit/test_toaster_proof_e049.py",
    "tests/unit/test_storage_growth_e050.py",
    "tests/unit/test_etiquette_e051.py",
    "tests/unit/test_updates_e052.py",
    "tests/unit/test_battery_e053.py",
    "tests/unit/test_smallness_e054.py",
    "tests/unit/test_budget_book_e055.py",
)


def build_command(extra_args: list[str], *, collect_only: bool = False) -> list[str]:
    """The exact pytest command the gate runs (pinned by test)."""
    command = [sys.executable, "-m", "pytest", *BUDGET_TEST_FILES, "-q"]
    if collect_only:
        command.append("--collect-only")
    command.extend(extra_args)
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Ember's permanent budget gate: every Part III "
            "budget test (E-041–E-055) as one command."
        )
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="print the gate's test files, one per line, and run nothing",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="collect the budget tests without running them (wiring check)",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="arguments after -- are passed to pytest unchanged",
    )
    args = parser.parse_args(argv)

    if args.list:
        for path in BUDGET_TEST_FILES:
            print(path)
        return 0

    extra = list(args.pytest_args)
    if extra and extra[0] == "--":
        extra = extra[1:]

    env = dict(os.environ)
    src = str(REPO_ROOT / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src if not existing else src + os.pathsep + existing

    result = subprocess.run(
        build_command(extra, collect_only=args.collect_only),
        cwd=REPO_ROOT,
        env=env,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
