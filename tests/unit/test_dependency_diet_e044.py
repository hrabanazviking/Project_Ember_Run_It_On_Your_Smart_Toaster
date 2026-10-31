"""E-044 — install weight cut II: the dependency diet.

Before this slice the root package's declarations had three
proven faults (E-007 audit, docket 20 + 23):

* every requirement was an unbounded ``>=`` floor — and on
  2026-10-31 the ``mcp`` floor resolved to mcp 2.3.0, whose SDK
  renamed FastMCP away, so a fresh ``ember-agent[mcp]`` install
  could not have started `ember mcp serve` at all;
* the core's optional ``keyring`` secret source (ADR 0010 §2.5)
  was declared in no extra — undiscoverable from the packaging;
* the ``dev`` extra bundled the lint tools (mypy's compiled
  core + the ruff binary, measured 81.5 MB) into every
  test-only install (measured 89.1 MB in all).

The diet, pinned here:

* every requirement — build system, extras, dev, lint —
  carries a floor *and* an upper bound at the next major of
  the line the code was written against;
* ``keyring`` is declared as its own ``secrets`` extra and is
  *not* folded into ``pgvector`` (its Linux tree weighs
  ~16.6 MB; only keyring users pay it), and the resolver's
  missing-keyring note names that extra;
* ``dev`` is the test shape only; ``lint`` holds ruff + mypy;
* the import↔extra map is exact: every third-party package
  the core imports is declared in exactly the extra that
  names its feature, and every extra's packages are imported
  somewhere in the core (no orphans either way).

The slice record (docs/architecture/E-044_INSTALL_WEIGHT_CUT_II.md)
holds the before/after install measurements; these tests are
the fast per-gate regression shape.
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
SRC = REPO_ROOT / "src" / "ember"

#: Distribution name -> the import name the core uses.
EXTRA_IMPORTS: dict[str, dict[str, str]] = {
    "sqlite_vec": {"sqlite-vec": "sqlite_vec"},
    "config": {"pyyaml": "yaml"},
    "pgvector": {"psycopg": "psycopg", "pgvector": "pgvector"},
    "mcp": {"mcp": "mcp"},
    "secrets": {"keyring": "keyring"},
}


def _pyproject() -> dict:
    with PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)


def _all_requirements() -> list[tuple[str, str]]:
    data = _pyproject()
    reqs: list[tuple[str, str]] = [
        ("build-system", r) for r in data["build-system"]["requires"]
    ]
    for extra, deps in data["project"]["optional-dependencies"].items():
        reqs += [(extra, d) for d in deps]
    return reqs


def _dist_name(req: str) -> str:
    return re.split(r"[<>=!~;\[]", req, maxsplit=1)[0].strip().lower()


def test_core_dependencies_still_empty() -> None:
    assert _pyproject()["project"]["dependencies"] == []


def test_every_requirement_is_bounded_both_ways() -> None:
    reqs = _all_requirements()
    assert reqs, "no requirements found — pyproject shape changed?"
    for where, req in reqs:
        assert ">=" in req, f"{where}: {req!r} lost its floor"
        assert "<" in req, (
            f"{where}: {req!r} has no upper bound — an unbounded floor "
            "is how mcp 2.x broke a fresh [mcp] install (E-044, docket 23)"
        )


def test_mcp_bound_excludes_the_fastmcp_breaking_major() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]
    (mcp_req,) = [d for d in extras["mcp"] if _dist_name(d) == "mcp"]
    assert "<2" in mcp_req.replace(" ", ""), (
        "the mcp extra must stay on the 1.x line the code was written "
        "against: mcp 2.x removed mcp.server.fastmcp (measured E-044)"
    )


def test_keyring_is_its_own_extra_not_folded_into_pgvector() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]
    assert "secrets" in extras, "docket 20: keyring declared in no extra"
    assert [_dist_name(d) for d in extras["secrets"]] == ["keyring"]
    pg_names = [_dist_name(d) for d in extras["pgvector"]]
    assert "keyring" not in pg_names, (
        "keyring's tree weighs ~16.6 MB (E-044 measurement); folding it "
        "into pgvector would tax every pgvector install for a source "
        "only some operators use"
    )


def test_dev_is_test_only_and_lint_holds_the_tools() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]
    dev = {_dist_name(d) for d in extras["dev"]}
    lint = {_dist_name(d) for d in extras["lint"]}
    assert dev == {"pytest", "pytest-cov"}
    assert lint == {"ruff", "mypy"}
    assert not dev & lint


def _core_third_party_imports() -> set[str]:
    found: set[str] = set()
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return {m for m in found if m not in sys.stdlib_module_names and m != "ember"}


def test_import_map_is_exact_no_orphans_either_way() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]
    declared: dict[str, str] = {}  # import name -> extra
    for extra, dists in EXTRA_IMPORTS.items():
        assert extra in extras, f"extra {extra!r} missing from pyproject"
        assert {_dist_name(d) for d in extras[extra]} == set(dists), (
            f"extra {extra!r} no longer declares {sorted(dists)}"
        )
        for imp in dists.values():
            declared[imp] = extra
    imported = _core_third_party_imports()
    assert imported == set(declared), (
        f"import/extra drift: imported-not-declared "
        f"{sorted(imported - set(declared))}, declared-not-imported "
        f"{sorted(set(declared) - imported)}"
    )


def test_missing_keyring_note_names_the_secrets_extra(
    tmp_path: Path, monkeypatch
) -> None:
    from ember.schemas.config import PgVectorConfig
    from ember.well.brunnr.pgvector import secrets

    monkeypatch.setattr(secrets, "_try_import_keyring", lambda: None)
    config = PgVectorConfig(
        url="postgresql://volmarr@gungnir/knowledge",
        secret_ref=tmp_path / "absent-secret",
        secret_env="EMBER_WELL_PASSWORD",
        use_keyring=True,
        keyring_service="ember-well",
        username=None,
    )
    result = secrets.resolve(config, env={})
    assert result.secret is None
    assert result.reason is not None
    assert "ember-agent[secrets]" in result.reason
