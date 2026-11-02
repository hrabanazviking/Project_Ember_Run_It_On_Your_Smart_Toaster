"""E-076 — Part IV gate: VD-RM's remaining road closed or
re-roaded with owners; event contract frozen; summary filed.

Pins the gate's own acts:

* docket 106 CLOSED in scope — the hub's `stop` probe
  (`_pid_alive` in ``Verdandi/nervous_system.py``) reads a
  zombie as dead, so a hub killed by its SIGTERM is reported
  stopped, not "could not be killed"; `cmd_stop` against a
  zombie pid reports a graceful stop and clears the pid file;
* the docket 6 family repair — Verdandi's CLI integration
  tests run in the member's own directory, derived from the
  test file, never in ``~/Verdandi`` (a home that exists only
  on the Pi deployment);
* docket 92's Verdandi half CLOSED in scope — every
  requirement Verdandi declares is bounded both ways, like
  the root package's (E-044's law);
* the event contract is frozen at v1 — the contract
  module's version is 1 and the gate doc records the freeze;
* the gate doc itself — every VD-RM remainder and every
  Part IV docket item (100–107) is named in it, and every
  Part IV slice doc E-059–E-076 is on disk.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-076_PART_IV_GATE.md"
ARCH = REPO / "docs" / "architecture"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── Docket 106: the stop probe is not zombie-blind ──────


@pytest.mark.skipif(not Path("/proc").exists() or not hasattr(os, "fork"),
                    reason="zombie probe needs /proc and fork")
def test_pid_alive_reads_a_zombie_as_dead():
    hub = _load("ember_hub_e076", VERDANDI / "nervous_system.py")
    assert hub._pid_alive(os.getpid()) is True
    assert hub._pid_alive(999_999_999) is False
    pid = os.fork()
    if pid == 0:  # pragma: no cover — child
        os._exit(0)
    try:
        time.sleep(0.5)
        state = Path(f"/proc/{pid}/stat").read_bytes() \
            .rsplit(b")", 1)[1].split()[0]
        assert state == b"Z"  # the child really is a zombie here
        assert hub._pid_alive(pid) is False
    finally:
        os.waitpid(pid, 0)


@pytest.mark.skipif(not Path("/proc").exists() or not hasattr(os, "fork"),
                    reason="zombie probe needs /proc and fork")
def test_cmd_stop_reports_graceful_for_a_zombie_hub(tmp_path, capsys,
                                                     monkeypatch):
    monkeypatch.setenv("VERDANDI_HOME", str(tmp_path))
    hub = _load("ember_hub_stop_e076", VERDANDI / "nervous_system.py")
    pid = os.fork()
    if pid == 0:  # pragma: no cover — child
        os._exit(0)
    try:
        time.sleep(0.3)
        hub.PID_PATH.write_text(str(pid))
        hub.cmd_stop()
        out = capsys.readouterr().out
        assert "stopped gracefully" in out
        assert "could not be killed" not in out
        assert not hub.PID_PATH.exists()
    finally:
        os.waitpid(pid, 0)


# ── Docket 6 family: CLI tests run in the member ────────


def test_cli_integration_tests_point_at_the_member():
    src = _source(VERDANDI / "tests" / "test_heartbeat_integration.py")
    assert "cwd=str(Path.home()" not in src
    assert "VERDANDI_DIR = Path(__file__).resolve().parents[1]" in src
    assert src.count("cwd=str(VERDANDI_DIR)") == 5
    # The pulse/react pair also runs against an isolated home,
    # so the CLI judges an empty world, not the host's state.
    assert "_isolated_env" in src
    assert 'env["VERDANDI_HOME"]' in src


# ── Docket 92, Verdandi half: bounded both ways ─────────


def test_verdandi_requirements_are_bounded_both_ways():
    data = tomllib.loads(_source(VERDANDI / "pyproject.toml"))
    reqs = list(data["build-system"]["requires"])
    for extra in data["project"].get("optional-dependencies", {}).values():
        reqs.extend(extra)
    assert reqs, "Verdandi declares no requirements at all?"
    for req in reqs:
        assert ">=" in req and "<" in req, f"unbounded requirement: {req}"


# ── The contract freeze ─────────────────────────────────


def test_event_contract_is_frozen_at_v1():
    contract = _load("ember_contract_e076", VERDANDI / "event_contract.py")
    assert contract.CONTRACT_VERSION == 1
    text = _source(DOC)
    assert "FROZEN" in text
    assert "version bump" in text


# ── The gate doc's accounting ───────────────────────────


def test_gate_doc_names_every_remainder_and_docket():
    text = _source(DOC)
    for needle in ("Distributed Heartbeat", "REST API", "Valhalla",
                   "Yggdrasil", "pulse_metrics"):
        assert needle in text, needle
    for item in range(100, 108):
        assert f"docket {item}" in text, f"docket {item} not accounted"


def test_every_part_iv_slice_doc_is_on_disk():
    expected = {
        "E-059_VERDANDI_MAPPED.md",
        "E-060_VDRM_CONCORDANCE_EXECUTED.md",
        "E-061_EVENT_CONTRACT_V1.md",
        "E-062_CONTEXT_INJECTION_DISCIPLINE.md",
        "E-063_CONVERSATION_LOGGER_LAW.md",
        "E-064_STIMULI.md",
        "E-065_REFLEX_LAYER.md",
        "E-066_NERVE_HEALTH.md",
        "E-067_CROSS_MEMBER_NERVES.md",
        "E-068_HERMES_SHAPED_NERVES.md",
        "E-069_ORDERING_AND_REPLAY.md",
        "E-070_BACKPRESSURE.md",
        "E-071_NERVE_PRIVACY.md",
        "E-072_LOGGER_AS_MEMORY_SOURCE.md",
        "E-073_VERDANDI_STANDALONE.md",
        "E-074_NERVE_MODEL_FOR_MEMBER_BUILDERS.md",
        "E-075_LOAD_TRUTH.md",
        "E-076_PART_IV_GATE.md",
    }
    missing = {name for name in expected if not (ARCH / name).exists()}
    assert not missing, f"missing Part IV docs: {sorted(missing)}"
