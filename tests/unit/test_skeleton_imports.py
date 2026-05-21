"""Phase 1 closure: every src/ember/ subpackage imports cleanly.

This is the "import-only" test called for by Phase 1 of
``docs/architecture/EMBER_FIRST_SLICE_PLAN.md`` §3. It rolled forward
into the Phase 2 commit's effective scope (the Phase 2 test
``test_schemas_import.py`` covers the schemas subpackage); this file
finishes the job by walking the full Three Realms tree.

Failure of any of these parameters means the Phase 1 scaffolding has
regressed — typically a circular import, a typo in an ``__init__.py``,
or a stray top-level statement that fails at import time.
"""

from __future__ import annotations

import importlib

import pytest

import ember
import ember.__main__ as _ember_main

SKELETON_MODULES = (
    "ember",
    "ember.cli",
    "ember.schemas",
    "ember.spark",
    "ember.spark.funi",
    "ember.spark.hjarta",
    "ember.spark.munnr",
    "ember.thread",
    "ember.thread.strengr",
    "ember.well",
    "ember.well.brunnr",
    "ember.well.smidja",
)


@pytest.mark.parametrize("module_name", SKELETON_MODULES)
def test_subpackage_imports_cleanly(module_name: str) -> None:
    importlib.import_module(module_name)


def test_ember_package_exposes_version() -> None:
    assert isinstance(ember.__version__, str)
    # First-slice ratification bumped from 0.0.0 to 0.1.0.
    assert ember.__version__ == "0.1.0"


def test_main_module_defines_main_function() -> None:
    # ``import ember.__main__`` succeeds and exposes ``main`` — the
    # actual dispatch is exercised by ``tests/unit/test_cli_main.py``.
    assert callable(_ember_main.main)


def test_main_resolves_to_ember_cli_main() -> None:
    # Phase 6 replaced the Phase-1 NotImplementedError stub with a
    # passthrough to ``ember.cli.main.main``. Verify the binding rather
    # than re-testing the dispatcher's behaviour (covered separately).
    import ember.cli.main as cli_main_module  # noqa: PLC0415 — late import deliberate; see comment above

    assert _ember_main.main is cli_main_module.main
