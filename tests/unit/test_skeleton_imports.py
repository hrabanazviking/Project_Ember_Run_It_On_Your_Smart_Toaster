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
    assert ember.__version__ == "0.0.0"


def test_main_module_defines_main_function() -> None:
    # ``python -m ember`` raises NotImplementedError, but plain
    # ``import ember.__main__`` should succeed and expose ``main``.
    assert callable(_ember_main.main)


def test_main_raises_notimplemented_with_pointer_to_the_plan() -> None:
    with pytest.raises(NotImplementedError, match="EMBER_FIRST_SLICE_PLAN"):
        _ember_main.main()
