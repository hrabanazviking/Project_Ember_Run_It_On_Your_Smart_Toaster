"""E-037 — core API freeze v1 (library shape).

Pins the freeze:

- ``ember.API_VERSION`` is ``"1.0.0"`` — a library contract
  version, deliberately separate from the package version
  (``ember.__version__`` stays ``"0.2.0"``).
- Every frozen name in ``ember.api.API_V1`` plus every name in
  each frozen schema module's ``__all__`` resolves in the
  default (stdlib-only) environment — the freeze needs no
  optional extra to check.
- The curated ``__all__`` of every frozen subpackage is a
  subset of the manifest: a future slice that adds a public
  name to a frozen package without freezing it (or removes
  one) fails here.
- ``is_api_compatible`` judges semver the way members need:
  same major, provider at least the wanted minor/patch, and
  an unparseable want never binds.
- What is NOT frozen stays out of the manifest: the CLI, the
  MCP / Munnr / Hjarta / Smiðja internals, and the concrete
  backend adapters (reached through the frozen ``open()``
  registries only).
- ``ember.api`` imports only the standard library at module
  level, and importing it in a fresh process pulls in no
  member package, no optional extra, and no adapter — the
  laziness the tiny profiles depend on.
- A fake member binding through ONLY the frozen surface can
  check the version, build a default config, and open the
  handles' typed refusal shapes without any extra installed
  (docket 56's member half: members bind through the API,
  never through the core's config file).
"""

from __future__ import annotations

import ast
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

import ember
import ember.api
from ember.api import (
    API_MAJOR,
    API_V1,
    API_VERSION,
    SCHEMA_MODULES,
    api_manifest,
    is_api_compatible,
    verify_api_surface,
)
from ember.schemas.cognition import CognitionUnavailable, CognitionUnavailableReason
from ember.schemas.config import (
    CognitionConfig,
    EmberConfig,
    FuniConfig,
    FuniRuntime,
)
from ember.schemas.episode import Episode
from ember.schemas.funi import Unavailable, UnavailableReason

REPO_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------- #
# The version itself                                                     #
# --------------------------------------------------------------------- #


def test_api_version_is_1_0_0_and_separate_from_package_version() -> None:
    assert API_VERSION == "1.0.0"
    assert ember.API_VERSION == "1.0.0"
    assert ember.api.API_VERSION is API_VERSION or ember.api.API_VERSION == API_VERSION
    assert API_MAJOR == 1
    # The package version is an operator-facing release label;
    # the freeze does not move it.
    assert ember.__version__ == "0.2.0"


@pytest.mark.parametrize(
    ("want", "expected"),
    [
        ("1", True),
        ("1.0", True),
        ("1.0.0", True),
        (" 1.0.0 ", True),
        ("1.0.1", False),  # wants a patch this build does not have
        ("1.1", False),  # wants additions this build does not have
        ("1.1.0", False),
        ("0.9", False),  # an older major never binds to v1
        ("0.9.9", False),
        ("2", False),  # a future major is a different contract
        ("2.0.0", False),
        ("", False),  # unparseable never binds, never raises
        ("v1", False),
        ("1.x", False),
        ("1.0.0.1", False),
        ("-1", False),
    ],
)
def test_is_api_compatible_matrix(want: str, expected: bool) -> None:
    assert is_api_compatible(want) is expected


# --------------------------------------------------------------------- #
# The frozen surface resolves                                            #
# --------------------------------------------------------------------- #


def test_verify_api_surface_is_clean_in_default_env() -> None:
    assert verify_api_surface() == ()


def test_manifest_is_sorted_unique_and_complete() -> None:
    manifest = api_manifest()
    paths = [entry.path for entry in manifest]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths)), "duplicate frozen paths"
    schema_names = sum(len(importlib.import_module(name).__all__) for name in SCHEMA_MODULES)
    assert len(manifest) == len(API_V1) + schema_names
    for entry in manifest:
        assert entry.module == "ember" or entry.module.startswith("ember."), entry.path


def test_every_schema_module_all_is_frozen() -> None:
    manifest_paths = {entry.path for entry in api_manifest()}
    for module_name in SCHEMA_MODULES:
        module = importlib.import_module(module_name)
        assert module.__all__, f"{module_name} has an empty __all__"
        for name in module.__all__:
            assert f"{module_name}.{name}" in manifest_paths


@pytest.mark.parametrize(
    "package_name",
    [
        "ember.config",
        "ember.spark.funi",
        "ember.spark.cognition",
        "ember.spark.persona",
        "ember.spark.conversation",
        "ember.thread.strengr",
        "ember.well.brunnr",
    ],
)
def test_frozen_subpackage_all_is_subset_of_manifest(package_name: str) -> None:
    package = importlib.import_module(package_name)
    manifest_paths = {entry.path for entry in api_manifest()}
    for name in package.__all__:
        assert f"{package_name}.{name}" in manifest_paths, (
            f"{package_name}.{name} is public but not frozen — "
            "freeze it in ember.api.API_V1 or unpublish it"
        )


def test_tools_module_surface_entry_covers_its_all() -> None:
    module_entries = [entry for entry in API_V1 if entry.kind == "module"]
    assert [entry.module for entry in module_entries] == ["ember.spark.funi.tools"]
    tools = importlib.import_module("ember.spark.funi.tools")
    for name in tools.__all__:
        assert hasattr(tools, name)


# --------------------------------------------------------------------- #
# What is NOT frozen stays out                                           #
# --------------------------------------------------------------------- #

_FORBIDDEN_PREFIXES = (
    "ember.cli",
    "ember.mcp",
    "ember.spark.munnr",
    "ember.spark.hjarta",
    "ember.well.smidja",
    "ember.spark.funi.ollama",
    "ember.spark.funi.aesir",
    "ember.well.brunnr.sqlite_vec",
    "ember.well.brunnr.pgvector",
)

_FORBIDDEN_NAMES = ("OllamaFuni", "AesirFuni", "SqliteVecBrunnr", "PgVectorBrunnr")


def test_manifest_freezes_no_internals_or_concrete_adapters() -> None:
    for entry in api_manifest():
        for prefix in _FORBIDDEN_PREFIXES:
            assert not entry.module.startswith(prefix), entry.path
        assert entry.attribute not in _FORBIDDEN_NAMES, entry.path


def test_api_module_imports_only_stdlib_at_module_level() -> None:
    tree = ast.parse((REPO_ROOT / "src" / "ember" / "api.py").read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__"}
    assert "ember" not in roots


def test_importing_api_pulls_no_members_extras_or_adapters() -> None:
    code = (
        "import sys\n"
        "import ember.api\n"
        "bad = [m for m in sys.modules if m.split('.')[0] in "
        "{'Verdandi', 'kista', 'mempalace', 'sqlite_vec', 'psycopg', 'yaml'} "
        "or m.startswith('ember.cli') or m.startswith('ember.mcp') "
        "or '.ollama' in m or '.aesir' in m or 'sqlite_vec.' in m]\n"
        "assert not bad, bad\n"
        "print('clean')\n"
    )
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "clean" in result.stdout


# --------------------------------------------------------------------- #
# A member binds through the frozen surface only                         #
# --------------------------------------------------------------------- #


def test_fake_member_binds_through_frozen_surface_only() -> None:
    # The version gate a member runs before binding.
    assert is_api_compatible("1.0")

    # Config is built from the frozen schema surface and the
    # frozen defaults — never by parsing ember.yaml.
    config = EmberConfig()
    assert config.funi.runtime is FuniRuntime.OLLAMA

    # Opening an unimplemented runtime through the frozen
    # registry returns the typed refusal, with no extra and
    # no network involved.
    from ember.spark.funi import open as funi_open

    refused = funi_open(FuniConfig(runtime=FuniRuntime.LLAMACPP))
    assert isinstance(refused, Unavailable)
    assert refused.reason is UnavailableReason.RUNTIME_NOT_INSTALLED

    # The cognition layer's frozen open refuses plainly while
    # disabled (its default).
    from ember.spark.cognition import open_cognition

    cognition = open_cognition(CognitionConfig())
    assert isinstance(cognition, CognitionUnavailable)
    assert cognition.reason is CognitionUnavailableReason.DISABLED

    # Persona/conversation tagging rides the frozen helpers.
    from ember.spark.conversation import tag_episode as tag_conversation
    from ember.spark.persona import tag_episode as tag_persona

    episode = Episode(operator_input="hi", ember_reply="hello")
    assert tag_persona(episode, "default") == episode
    assert tag_persona(episode, "default").persona_id == "default"
    assert tag_conversation(episode, "default") == episode
    assert tag_conversation(episode, "default").conversation_id == "default"


def test_frozen_handles_are_protocols_with_the_frozen_methods() -> None:
    from ember.spark.cognition import CognitionHandle
    from ember.spark.funi import FuniHandle
    from ember.well.brunnr import BrunnrHandle

    for method in ("complete", "complete_streaming", "health", "close"):
        assert hasattr(FuniHandle, method), method
    for method in ("add_episode", "recent_episodes", "hybrid_search", "count", "close"):
        assert hasattr(BrunnrHandle, method), method
    for method in ("think", "health", "close"):
        assert hasattr(CognitionHandle, method), method
