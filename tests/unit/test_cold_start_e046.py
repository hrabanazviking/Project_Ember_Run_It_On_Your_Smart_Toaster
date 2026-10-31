"""E-046 — Cold start on the smallest profile, measured + capped.

E-041 priced the core's size and memory; E-045 priced its idle
hour. Neither answers the first question a person on a small
machine actually asks: *I just started it — how long until it
says something?* This slice measures that, on the smallest
profile (toaster), and caps it in the budget book
(``ember.budgets``: ``cold_start_first_word_s``, flat across
profiles because cold start is process startup, and startup
does not grow with a profile's history allowance).

**What is timed.** A fresh ``python -m ember ask`` process —
the real CLI, a real config file on disk, a real ``sqlite_vec``
Well, the toaster conversation profile — against a loopback
Ollama *wire-shape* server (the E-029/E-032 pattern) whose
first streamed chunk is a distinctive word and which answers
instantly. The clock starts in the parent just before the
process is spawned and stops the moment that first word's
bytes arrive on the child's stdout pipe. So the number prices
Ember's own cold start — interpreter, imports, config load,
model probe, Well open, history load, retrieval, request —
and NOT a real model's thinking time: no live model exists
on the VM, and a real-model cold start is NOT PROVEN here
(E-047–E-049 own device proof; E-032's honest limit stands).

**Why the median.** Cold-start wall time is the most
contention-sensitive number the campaign measures: the slice
record's seven runs on a busy VM spread 1.28–5.38 s around a
2.87 s median, almost all of it *before* the "ready" line —
the turn itself added ~0.1 s. A single run judged against a
cap would flake with machine weather; the median of three is
the shape's centre, and the cap (5.0 s, ~1.7× the measured
median anchor) still catches a real regression — a new
import-time blowup, a retry/backoff creeping into startup —
which moves every run, not just one unlucky sample.

Where the ``sqlite_vec`` extra is absent the real-Well shape
cannot run and the measurement test skips with the reason
stated (the bookkeeping tests still run — the book and its
cap exist in every environment).
"""

from __future__ import annotations

import json
import os
import select
import statistics
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from ember.budgets import (
    MEASURED_COLD_START_FIRST_WORD_S,
    PROFILE_ORDER,
    budget_for,
    check_against,
)
from ember.schemas.config import ConversationProfile

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"

_FIRST_WORD = "coldstart"
_READY_MARK = b"is ready."
_RUNS = 3  # judged by their median — see the header


# --------------------------------------------------------------------- #
# The loopback wire-shape model (E-032's handler, first word marked)     #
# --------------------------------------------------------------------- #


class _LoopbackOllamaHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence the test server
        return None

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/api/version":
            self._send_json({"version": "0.0-e046"})
        else:
            self.send_error(404)

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        if self.path == "/api/embed":
            self._send_json({"embeddings": [[0.1, 0.2, 0.3, 0.4]]})
            return
        if self.path == "/api/chat":
            lines = [
                {"message": {"role": "assistant", "content": f"{_FIRST_WORD} "},
                 "done": False},
                {"message": {"role": "assistant", "content": "answer"},
                 "done": True, "done_reason": "stop",
                 "prompt_eval_count": 3, "eval_count": 2},
            ]
            body = "".join(json.dumps(x) + "\n" for x in lines).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)


# --------------------------------------------------------------------- #
# The cold run                                                           #
# --------------------------------------------------------------------- #


def _write_config_root(root: Path, base_url: str) -> None:
    (root / "identity").mkdir(parents=True, exist_ok=True)
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "identity" / "identity.json").write_text(
        json.dumps({"name": "Ember", "role": "your small local AI companion"}),
        encoding="utf-8",
    )
    (root / "config" / "ember.toml").write_text(
        f"""
[identity]
name = "Ember"
role = "your small local AI companion"
[conversation]
profile = "toaster"
[funi]
streaming = true
[funi.ollama]
base_url = "{base_url}"
model = "fake:local"
[strengr]
retry_backoff_max_s = 0.0
[brunnr]
embedding_dim = 4
[brunnr.sqlite_vec]
path = "{root}/well/store.db"
[smidja.embedding]
endpoint = "{base_url}/api/embed"
[tools]
enabled = false
""",
        encoding="utf-8",
    )


def _cold_run(root: Path) -> dict:
    """One fresh process, timed from spawn to the first word.

    Returns ready/first-word/total seconds (None where a mark
    never arrived) and the exit code. Output is read through a
    ``select`` loop so the first-word timestamp is when the
    bytes *arrived*, not when the process finished.
    """
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC) + (os.pathsep + existing if existing else "")
    # The loopback model must never be proxied (E-005's lesson:
    # this VM's proxy env is hostile to local clients).
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["no_proxy"] = "127.0.0.1,localhost"
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        [sys.executable, "-m", "ember", "--config-root", str(root), "ask", "hello"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(REPO_ROOT),
    )
    buf = b""
    t_ready: float | None = None
    t_first: float | None = None
    fd = proc.stdout.fileno()  # type: ignore[union-attr]
    while True:
        ready, _, _ = select.select([fd], [], [], 60)
        if not ready:
            proc.kill()
            raise AssertionError("cold-start probe produced no output for 60 s")
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        buf += chunk
        now = time.perf_counter() - t0
        if t_ready is None and _READY_MARK in buf:
            t_ready = now
        if t_first is None and _FIRST_WORD.encode() in buf:
            t_first = now
    rc = proc.wait(timeout=60)
    return {
        "ready_s": t_ready,
        "first_word_s": t_first,
        "total_s": time.perf_counter() - t0,
        "rc": rc,
        "stderr": proc.stderr.read().decode(errors="replace")[:400]
        if proc.stderr
        else "",
    }


# --------------------------------------------------------------------- #
# 1. The book: the cap and the anchor                                      #
# --------------------------------------------------------------------- #


def test_cold_start_cap_is_flat_and_holds_the_anchor_with_headroom() -> None:
    caps = [budget_for(p).cold_start_first_word_s for p in PROFILE_ORDER]
    # Flat by design (budgets.py): starting costs the same on
    # every profile; a smaller machine never waits longer by
    # allowance, and no profile is granted a slower start.
    assert len(set(caps)) == 1
    cap = caps[0]
    assert cap == 5.0
    # ~1.7× the measured median anchor: headroom for machine
    # weather, not room for a startup regression to hide in.
    assert cap >= 1.5 * MEASURED_COLD_START_FIRST_WORD_S
    assert cap <= 2.0 * MEASURED_COLD_START_FIRST_WORD_S
    assert MEASURED_COLD_START_FIRST_WORD_S == 2.87


def test_check_against_names_a_broken_cold_start_ceiling() -> None:
    problems = check_against(
        ConversationProfile.TOASTER,
        install_mib=1.0,
        idle_ram_mib=40.0,
        turn_ram_mib=40.0,
        storage_growth_mib_per_month=0.4,
        cold_start_first_word_s=99.0,
    )
    assert len(problems) == 1
    assert "cold start to first word" in problems[0]
    assert "toaster" in problems[0]
    # The measured anchor itself fits, and an unmeasured shape
    # (no cold-start argument) is not judged on one.
    assert (
        check_against(
            ConversationProfile.TOASTER,
            install_mib=1.0,
            idle_ram_mib=40.0,
            turn_ram_mib=40.0,
            storage_growth_mib_per_month=0.4,
            cold_start_first_word_s=MEASURED_COLD_START_FIRST_WORD_S,
        )
        == ()
    )


def test_cold_start_gate_is_collected_by_the_slice_gate() -> None:
    # Wiring (E-042's pattern): this file must live where the
    # campaign's slice gate — the whole root suite — collects
    # it, so every future slice re-measures the cold start.
    assert Path(__file__).resolve().parent.name == "unit"
    assert Path(__file__).resolve().parents[1].name == "tests"


# --------------------------------------------------------------------- #
# 2. The measurement: fresh processes on the toaster profile               #
# --------------------------------------------------------------------- #


def test_toaster_cold_start_median_inside_the_cap(tmp_path: Path) -> None:
    try:
        import sqlite_vec  # noqa: F401
    except ImportError:
        pytest.skip("sqlite_vec extra absent — real-Well cold start cannot run")
    server = ThreadingHTTPServer(("127.0.0.1", 0), _LoopbackOllamaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        root = tmp_path / "configroot"
        _write_config_root(root, base_url)
        # The setup run creates the Well and proves the whole
        # shape end to end; it is a first-ever start (Well
        # creation included), not one of the judged cold runs.
        setup = _cold_run(root)
        assert setup["rc"] == 0, setup["stderr"]
        assert setup["first_word_s"] is not None

        runs = [_cold_run(root) for _ in range(_RUNS)]
    finally:
        server.shutdown()
        server.server_close()
    for run in runs:
        assert run["rc"] == 0, run["stderr"]
        assert run["ready_s"] is not None
        assert run["first_word_s"] is not None
        # The reply cannot arrive before the session is ready:
        # startup is the road the first word travels.
        assert run["first_word_s"] >= run["ready_s"]
    median = statistics.median(r["first_word_s"] for r in runs)
    cap = budget_for(ConversationProfile.TOASTER).cold_start_first_word_s
    assert median <= cap, (
        f"toaster cold start to first word: median {median:.2f} s of "
        f"{[round(r['first_word_s'], 2) for r in runs]} exceeds its "
        f"ceiling of {cap:.2f} s (ember.budgets, E-046)"
    )
