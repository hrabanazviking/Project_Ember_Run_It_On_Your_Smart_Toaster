"""Verify the gravitational floor: schemas import cleanly with only the
standard library + the schemas package itself.

Per ``docs/architecture/DOMAIN_MAP.md`` §1: ``ember.schemas`` may import
from the standard library only. Optional ``pydantic`` and
``typing_extensions`` are allowed but not used in Phase 2. **No** imports
from sibling ``ember.*`` subpackages.

A failure of any of these tests means the floor has been breached.
"""

from __future__ import annotations

import importlib

import ember.schemas.chunks
import ember.schemas.config
import ember.schemas.episode
import ember.schemas.errors
import ember.schemas.funi

SCHEMA_MODULES = (
    "ember.schemas",
    "ember.schemas.errors",
    "ember.schemas.config",
    "ember.schemas.chunks",
    "ember.schemas.episode",
    "ember.schemas.funi",
)

_FORBIDDEN_SIBLING_PREFIXES = (
    "ember.well",
    "ember.thread",
    "ember.spark",
    "ember.cli",
)

_SCHEMA_MODULE_OBJECTS = (
    ember.schemas.errors,
    ember.schemas.config,
    ember.schemas.chunks,
    ember.schemas.episode,
    ember.schemas.funi,
)


def test_every_schema_module_imports_cleanly() -> None:
    for name in SCHEMA_MODULES:
        importlib.import_module(name)


def test_schemas_do_not_import_sibling_ember_subpackages() -> None:
    # Inspect each module's exported attrs for any ember.* reference
    # outside ember.schemas.*. The gravitational floor must not reach
    # sideways into sibling realms.
    for module in _SCHEMA_MODULE_OBJECTS:
        for attr_name in dir(module):
            value = getattr(module, attr_name, None)
            module_name = getattr(value, "__module__", "") or ""
            for forbidden in _FORBIDDEN_SIBLING_PREFIXES:
                assert not module_name.startswith(forbidden), (
                    f"{module.__name__}.{attr_name} reaches forbidden "
                    f"sibling subpackage: {module_name}"
                )
