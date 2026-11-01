"""E-073 — Verdandi standalone: the hub usable without the
full companion.

Pins Verdandi/standalone.py (the law) and its two inline
carriers: the hub module's own state-dir resolution
(``Verdandi/nervous_system.py`` — its deployed form is a
lone file) and the Ember core nerve bridge's
``hub_state_dir`` (``src/ember/nerve.py`` — no member
imports). All three must resolve the hub's home the same
way: ``VERDANDI_HOME`` when set, else ``~/.hermes/state``.

The live test boots the real hub by file path alone in an
isolated HOME with a relocated VERDANDI_HOME — no Ember on
the path, no companion running — and drives it through
its own CLI (healthcheck / publish / recent), then checks
the isolated HOME stayed empty: the hub created nothing
outside its relocated home.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-073_VERDANDI_STANDALONE.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


standalone = _load("ember_standalone_e073", VERDANDI / "standalone.py")

# The core bridge, loaded fresh from its file: tests/conftest.py
# monkeypatches the shared ember.nerve module's hub_state_dir to an
# isolated tmp dir for every test, so parity with the real function
# is checked against a private load (E-073).
nerve = _load("ember_nerve_fresh_e073", REPO / "src" / "ember" / "nerve.py")


# ── The module itself ──────────────────────────────────────


def test_module_is_stdlib_only_and_standalone():
    tree = ast.parse(_source(VERDANDI / "standalone.py"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= set(sys.stdlib_module_names)


def test_doc_states_the_law():
    text = _source(DOC)
    for needle in ("VERDANDI_HOME", "nervous_system.py",
                   "runa.sock", "nerve_feed.jsonl", "standalone"):
        assert needle in text


# ── The resolution law ─────────────────────────────────────


def test_env_override_wins_and_is_the_state_dir_itself():
    got = standalone.resolve_state_dir(
        environ={"VERDANDI_HOME": "/srv/nerve"}, home="/home/whoever")
    assert got == Path("/srv/nerve")


def test_empty_env_override_falls_back_to_default():
    got = standalone.resolve_state_dir(
        environ={"VERDANDI_HOME": ""}, home="/home/whoever")
    assert got == Path("/home/whoever/.hermes/state")


def test_default_is_the_hermes_shaped_home():
    got = standalone.resolve_state_dir(environ={}, home="/home/whoever")
    assert got == Path("/home/whoever/.hermes/state")


def test_manifest_shape():
    m = standalone.standalone_manifest()
    assert m["hub_module"] == "nervous_system.py"
    assert m["stdlib_only"] is True
    assert m["requires_companion"] is False
    assert m["requires_network"] is False
    assert m["state_dir_env"] == "VERDANDI_HOME"
    assert m["socket_path"].endswith("runa.sock")
    assert m["feed_path"].endswith("nerve_feed.jsonl")
    assert m["commands"] == ["serve", "publish", "stimulus", "recent",
                              "subscribe", "status", "healthcheck", "stop"]
    assert any("nerve bridge" in c for c in m["consumers"])


def test_commands_match_the_hub_cli():
    hub_src = _source(VERDANDI / "nervous_system.py")
    assert ("Commands: serve, publish, stimulus, recent, subscribe, "
            "status, healthcheck, stop") in hub_src
    assert list(standalone.COMMANDS) == [
        "serve", "publish", "stimulus", "recent",
        "subscribe", "status", "healthcheck", "stop"]


# ── The inline carriers agree ──────────────────────────────


def test_hub_module_carries_the_resolution_inline():
    hub_src = _source(VERDANDI / "nervous_system.py")
    assert '_resolve_state_dir' in hub_src
    assert 'os.environ.get("VERDANDI_HOME")' in hub_src
    assert "STATE_DIR = _resolve_state_dir()" in hub_src


def _hub_state_dir_in_subprocess(env_extra: dict) -> str:
    env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(VERDANDI)}
    env.update(env_extra)
    out = subprocess.run(
        [sys.executable, "-c",
         "import nervous_system as ns; print(ns.STATE_DIR); "
         "print(ns.SOCKET_PATH)"],
        env=env, capture_output=True, text=True, timeout=30, check=True)
    return out.stdout.strip()


def test_hub_module_follows_verdandi_home():
    got = _hub_state_dir_in_subprocess({"VERDANDI_HOME": "/tmp/e73-pin"})
    assert got.splitlines() == ["/tmp/e73-pin", "/tmp/e73-pin/runa.sock"]


def test_hub_module_default_follows_home():
    got = _hub_state_dir_in_subprocess({"HOME": "/tmp/e73-fakehome"})
    assert got.splitlines() == ["/tmp/e73-fakehome/.hermes/state",
                                "/tmp/e73-fakehome/.hermes/state/runa.sock"]


def test_core_bridge_resolution_matches(monkeypatch):
    monkeypatch.setenv("VERDANDI_HOME", "/srv/nerve")
    assert nerve.hub_state_dir() == standalone.resolve_state_dir(
        environ={"VERDANDI_HOME": "/srv/nerve"}, home="/anywhere")
    monkeypatch.delenv("VERDANDI_HOME")
    monkeypatch.setenv("HOME", "/home/whoever")
    assert nerve.hub_state_dir() == Path("/home/whoever/.hermes/state")


# ── Live: the hub alone, in an empty home ──────────────────


def test_hub_runs_standalone_in_an_empty_home():
    base = Path(tempfile.mkdtemp(prefix="e73", dir="/tmp"))
    home = base / "home"
    state = base / "state"
    home.mkdir()
    state.mkdir()
    env = {"PATH": os.environ["PATH"], "HOME": str(home),
           "VERDANDI_HOME": str(state)}
    hub = str(VERDANDI / "nervous_system.py")
    proc = subprocess.Popen(
        [sys.executable, hub, "serve"], env=env, cwd="/tmp",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        sock = state / "runa.sock"
        for _ in range(50):
            if sock.exists():
                break
            time.sleep(0.2)
        assert sock.exists(), "hub socket never appeared in VERDANDI_HOME"

        def cli(*args):
            return subprocess.run(
                [sys.executable, hub, *args], env=env, cwd="/tmp",
                capture_output=True, text=True, timeout=30)

        health = cli("healthcheck")
        assert health.returncode == 0, health.stdout + health.stderr
        assert "ALL CHECKS PASSED" in health.stdout

        pub = cli("publish", "standalone_probe",
                  '{"proof": "e073"}', "e073_tests")
        assert pub.returncode == 0, pub.stdout + pub.stderr
        assert "published" in pub.stdout

        recent = cli("recent", "5")
        assert "standalone_probe" in recent.stdout

        feed = (state / "nerve_feed.jsonl").read_text(encoding="utf-8")
        assert "standalone_probe" in feed
        # The isolated HOME stayed empty: no .hermes, no .ember,
        # nothing — the hub lived entirely in its relocated home.
        assert list(home.iterdir()) == []
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(base, ignore_errors=True)
