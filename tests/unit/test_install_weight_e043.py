"""E-043 — install weight cut I: optional members are truly optional.

Before this slice the wheel was honest (305 KB, ``src/ember``
only) but the *source* distribution dragged the whole monorepo
behind it: 45 MB compressed / 127 MB unpacked, of which the
optional members were the heaviest part (mempalace 57 MB of
benchmark data, the dictionary 24 MB, Open-VTT 6.3 MB, …). Anyone
installing from source — a git URL, a tarball, a mirror — paid
that weight to obtain a core that never imports any member.

The cut lives in ``pyproject.toml``'s sdist exclude list: every
member directory, the docs heritage corpora, the design lawbook
and the campaign state file are excluded from the sdist. These
tests pin the shape so the weight cannot creep back:

* the declaration itself — every member named in the excludes,
  the wheel still core-only, core dependencies still empty;
* a re-derivation — the sdist file set is rebuilt from
  ``git ls-files`` under the declared exclude rules and weighed
  as a real tar.gz: it must stay a small download and contain
  no member path, while still containing the package, its
  tests and its architecture docs (the cut must not gut).

The exclude-rule simulation mirrors the semantics the real
build was verified against in the E-043 slice record: a plain
entry excludes that path and everything under it; a ``*.ext``
entry matches a basename at any depth. The slice record holds
the before/after builds (45 MB → 1.1 MB) made with hatchling
itself; this test is the fast per-gate regression shape.
"""

from __future__ import annotations

import fnmatch
import io
import subprocess
import tarfile
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"

#: The optional members (E-002 census; roadmap §2). Separate
#: programs that live in the monorepo and run from a checkout —
#: none is part of the ember-agent package.
OPTIONAL_MEMBERS = (
    "Verdandi",
    "kista",
    "mempalace",
    "mimir-well",
    "seidr_engine",
    "astrology-engine",
    "bifrost",
    "Hamr",
    "Open-VTT",
    "CloakBrowser",
    "cleasby-vigfusson-old-norse-dict",
)

#: The re-derived sdist must stay a small download. Measured
#: 1.1 MB after the cut (E-043 record); the bound is set under
#: the toaster profile's 2 MiB install ceiling (E-041) with
#: headroom for doc growth, and far under the 45 MB it replaces.
SDIST_MAX_BYTES = 2 * 1024 * 1024


def _pyproject() -> dict:
    with PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)


def _sdist_excludes() -> list[str]:
    data = _pyproject()
    return list(data["tool"]["hatch"]["build"]["targets"]["sdist"]["exclude"])


def _is_excluded(relpath: str, excludes: list[str]) -> bool:
    parts = relpath.split("/")
    for pattern in excludes:
        if pattern.startswith("*."):
            if fnmatch.fnmatch(parts[-1], pattern):
                return True
        elif relpath == pattern or relpath.startswith(pattern + "/"):
            return True
    return False


def _tracked_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=REPO_ROOT,
            capture_output=True,
            timeout=60,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"git ls-files unavailable in this environment: {exc}")
    # -z: plain ls-files quotes non-ASCII paths (the tree has two,
    # under Verdandi) and the quoted forms are not real paths.
    return [p for p in out.stdout.decode("utf-8").split("\0") if p]


def test_every_optional_member_is_excluded_from_the_sdist() -> None:
    excludes = _sdist_excludes()
    for member in OPTIONAL_MEMBERS:
        assert member in excludes, (
            f"optional member {member!r} is not in the sdist exclude list — "
            "a source install would download it again (E-043)"
        )
        assert (REPO_ROOT / member).is_dir(), f"member {member!r} missing from the tree"


def test_repo_furniture_is_excluded_from_the_sdist() -> None:
    excludes = _sdist_excludes()
    assert "*.pdf" in excludes  # the 11.6 MB design lawbook PDF
    assert "Volmarr_Cyber_Viking_Master_Visual_Design_Lawbook.md" in excludes
    assert "CAMPAIGN_STATE.md" in excludes


def test_wheel_is_core_only_and_core_has_no_dependencies() -> None:
    data = _pyproject()
    wheel = data["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert wheel["packages"] == ["src/ember"]
    assert data["project"]["dependencies"] == []
    # Members are not hiding in the extras either: an extra may
    # only ever name third-party packages the core itself uses.
    extras = data["project"]["optional-dependencies"]
    member_names = {m.lower().replace("-", "_") for m in OPTIONAL_MEMBERS}
    for extra, deps in extras.items():
        for dep in deps:
            name = dep.split(">")[0].split("=")[0].split("[")[0].strip().lower()
            assert name not in member_names, f"extra {extra!r} pulls member {name!r}"


def test_no_member_lives_inside_the_package() -> None:
    package = REPO_ROOT / "src" / "ember"
    for member in OPTIONAL_MEMBERS:
        assert not (package / member).exists()


def test_rederived_sdist_is_small_and_member_free() -> None:
    excludes = _sdist_excludes()
    selected = [f for f in _tracked_files() if not _is_excluded(f, excludes)]

    for relpath in selected:
        top = relpath.split("/")[0]
        assert top not in OPTIONAL_MEMBERS, f"member file selected for sdist: {relpath}"

    # The cut must not gut the package it ships.
    assert any(p.startswith("src/ember/") for p in selected)
    assert any(p.startswith("tests/") for p in selected)
    assert any(p.startswith("docs/architecture/") for p in selected)
    assert "pyproject.toml" in selected

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for relpath in selected:
            tar.add(REPO_ROOT / relpath, arcname=f"ember_agent-0.2.0/{relpath}")
    size = buffer.tell()
    assert size < SDIST_MAX_BYTES, (
        f"re-derived sdist weighs {size} bytes — over the {SDIST_MAX_BYTES}-byte "
        "bound E-043 set (measured 1.1 MB after the cut; it was 45 MB before)"
    )
