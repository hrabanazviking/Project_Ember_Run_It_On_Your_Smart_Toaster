"""E-066 — Nerve health: a stuck/dead nerve is detected and
reported; the hub degrades honestly.

Pins Verdandi/nerve_health.py (the classification), the
docket-96 repair (a status probe is a control ping, never
a published event), the inline classifier in
nervous_system.py agreeing with the module, get_status
reporting the classification without touching the feed,
and docket 34's closure: Skuld reads pulse_metrics'
health_score as its health-history source, falling back
to the pulse_history state approximation only when no
usable metric exists.
"""

import ast
import importlib.util
import json
import socket
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-066_NERVE_HEALTH.md"

sys.path.insert(0, str(VERDANDI))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


health = _load("ember_nerve_health", VERDANDI / "nerve_health.py")
hub = _load("ember_nervous_system_e066", VERDANDI / "nervous_system.py")
contract = _load("ember_event_contract_e066", VERDANDI / "event_contract.py")

from heartbeat.checks.skuld import SkuldCheck  # noqa: E402


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


BASE = dict(state_dir_exists=True, socket_exists=True,
            pid_file_exists=True, pid_alive=True,
            ping_responded=True, feed_exists=True,
            feed_size_bytes=100, feed_max_bytes=10 * 1024 * 1024,
            log_writable=True)


def _classify(**over):
    obs = dict(BASE)
    obs.update(over)
    return health.classify_nerve_health(obs)


# ── The classification ──────────────────────────────────────


def test_version_states_and_module_shape():
    assert health.NERVE_HEALTH_VERSION == 1
    assert set(health.STATES) == {"healthy", "degraded", "stuck",
                                  "dead", "absent"}
    assert set(health.DEGRADE_BEHAVIOUR) == set(health.STATES)
    tree = ast.parse(_source(VERDANDI / "nerve_health.py"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names)


def test_healthy_requires_a_pong():
    out = _classify()
    assert out["status"] == "healthy"
    assert out["warnings"] == []
    assert health.validate_classification(out) == []


def test_degraded_is_healthy_with_warnings_shown():
    big = _classify(feed_size_bytes=9 * 1024 * 1024)
    assert big["status"] == "degraded" and big["warnings"]
    nolog = _classify(log_writable=False)
    assert nolog["status"] == "degraded" and nolog["warnings"]
    nofeed = _classify(feed_exists=False, feed_size_bytes=None)
    assert nofeed["status"] == "degraded" and nofeed["warnings"]


def test_dead_is_papers_without_a_process():
    out = _classify(pid_alive=False)
    assert out["status"] == "dead"
    assert health.validate_classification(out) == []
    # A warning can never mask death.
    assert _classify(pid_alive=False,
                     feed_size_bytes=9 * 1024 * 1024)["status"] == "dead"


def test_stuck_is_alive_but_silent():
    assert _classify(ping_responded=False)["status"] == "stuck"
    assert _classify(socket_exists=False,
                     ping_responded=None)["status"] == "stuck"
    out = _classify(ping_responded=False)
    assert "does not answer" in " ".join(out["reasons"])
    assert health.validate_classification(out) == []


def test_absent_is_not_running_and_not_dead():
    out = health.classify_nerve_health({})
    assert out["status"] == "absent"
    assert out["behaviour"] == health.DEGRADE_BEHAVIOUR["absent"]
    assert "fallback" in out["behaviour"]


def test_unprobed_hub_is_never_called_healthy():
    out = _classify(ping_responded=None)
    assert out["status"] == "degraded"
    assert any("not probed" in w for w in out["warnings"])


def test_validate_classification_refuses_lies():
    good = _classify()
    assert health.validate_classification(
        {**good, "status": "fine"}) != []
    assert health.validate_classification(
        {**good, "behaviour": "everything is wonderful"}) != []
    stuck = _classify(ping_responded=False)
    assert health.validate_classification(
        {**stuck, "behaviour": health.DEGRADE_BEHAVIOUR["healthy"]}) != []


def test_inline_classifier_agrees_with_the_module():
    matrix = [
        {}, dict(BASE), dict(BASE, pid_alive=False),
        dict(BASE, ping_responded=False),
        dict(BASE, feed_size_bytes=9 * 1024 * 1024),
        dict(BASE, log_writable=False),
        dict(BASE, socket_exists=False, ping_responded=None),
        dict(BASE, ping_responded=None),
        dict(BASE, feed_exists=False, feed_size_bytes=None),
    ]
    for obs in matrix:
        assert hub._classify_nerve_health(obs) == \
            health.classify_nerve_health(obs)["status"], obs


# ── Docket 96: the probe is a control message ───────────────


def test_get_status_source_never_publishes_a_ping():
    src = _source(VERDANDI / "nervous_system.py")
    assert "publish_event_sync('ping'" not in src
    assert 'publish_event_sync("ping"' not in src
    assert "def ping_hub" in src
    assert "'nerve_type': 'ping'" in src
    spec = contract.spec_for("ping")
    assert spec is not None and spec.status == "legacy"
    assert "CLOSED" in spec.notes


def test_ping_hub_speaks_only_control(monkeypatch):
    # A short /tmp home: Unix socket paths cap at ~108 chars
    # and the campaign TMPDIR is far deeper than that.
    import tempfile
    short = Path(tempfile.mkdtemp(prefix="e066-", dir="/tmp"))
    sock_path = short / "runa.sock"
    received = []

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(sock_path))
    server.listen(1)

    def serve_once():
        conn, _ = server.accept()
        data = conn.recv(4096)
        received.append(json.loads(data.decode().strip()))
        conn.sendall(json.dumps({"nerve_type": "pong"}).encode() + b"\n")
        conn.close()
        server.close()

    t = threading.Thread(target=serve_once, daemon=True)
    t.start()
    monkeypatch.setattr(hub, "SOCKET_PATH", sock_path)
    assert hub.ping_hub(timeout=5.0) is True
    t.join(timeout=5)
    assert received == [{"nerve_type": "ping"}]


def test_ping_hub_false_when_nothing_listens(tmp_path, monkeypatch):
    monkeypatch.setattr(hub, "SOCKET_PATH", tmp_path / "nope.sock")
    assert hub.ping_hub(timeout=0.5) is False


def test_get_status_on_absent_hub_leaves_feed_untouched(tmp_path, monkeypatch):
    feed = tmp_path / "nerve_feed.jsonl"
    feed.write_text('{"type": "real_event"}\n', encoding="utf-8")
    monkeypatch.setattr(hub, "STATE_DIR", tmp_path)
    monkeypatch.setattr(hub, "SOCKET_PATH", tmp_path / "runa.sock")
    monkeypatch.setattr(hub, "FEED_PATH", feed)
    monkeypatch.setattr(hub, "PID_PATH", tmp_path / "hub.pid")
    monkeypatch.setattr(hub, "LOG_PATH", tmp_path / "hub.log")
    status = hub.get_status()
    assert status["hub_running"] is False
    assert status["hub_responsive"] is False
    assert status["nerve_health"] == "absent"
    # The old get_status would have appended a 'ping' event
    # here (fallback publish). The feed must be byte-identical.
    assert feed.read_text(encoding="utf-8") == '{"type": "real_event"}\n'


def test_get_status_reports_dead_hub(tmp_path, monkeypatch):
    import os
    feed = tmp_path / "nerve_feed.jsonl"
    feed.write_text("", encoding="utf-8")
    pid_file = tmp_path / "hub.pid"
    # A PID that cannot be a live process on this machine.
    pid_file.write_text("99999999", encoding="utf-8")
    monkeypatch.setattr(hub, "STATE_DIR", tmp_path)
    monkeypatch.setattr(hub, "SOCKET_PATH", tmp_path / "runa.sock")
    monkeypatch.setattr(hub, "FEED_PATH", feed)
    monkeypatch.setattr(hub, "PID_PATH", pid_file)
    monkeypatch.setattr(hub, "LOG_PATH", tmp_path / "hub.log")
    assert os.path.exists(str(pid_file))
    status = hub.get_status()
    assert status["hub_running"] is False
    assert status["nerve_health"] == "dead"


# ── Docket 34: Skuld reads pulse_metrics ────────────────────


class _Cfg:
    def __init__(self, db):
        self._db = str(db)

    def get(self, key, default=None):
        return self._db if key == "heartbeat.db_path" else default


def _make_db(path, states, metric_scores):
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(str(path)) as conn:
        conn.execute("CREATE TABLE pulse_history (id INTEGER PRIMARY "
                     "KEY AUTOINCREMENT, timestamp DATETIME, state TEXT, "
                     "checks_json TEXT, pulse_count INTEGER)")
        conn.execute("CREATE TABLE pulse_metrics (id INTEGER PRIMARY "
                     "KEY AUTOINCREMENT, timestamp DATETIME, "
                     "pulse_count INTEGER NOT NULL, health_score REAL, "
                     "health_trend TEXT, daemon_state TEXT, "
                     "check_severities_json TEXT, "
                     "circuit_breakers_json TEXT, emotional_state TEXT)")
        for i, s in enumerate(states):
            conn.execute("INSERT INTO pulse_history (timestamp, state, "
                         "checks_json, pulse_count) VALUES (?, ?, '{}', ?)",
                         (now, s, i))
        for i, sc in enumerate(metric_scores):
            conn.execute("INSERT INTO pulse_metrics (timestamp, "
                         "pulse_count, health_score) VALUES (?, ?, ?)",
                         (now, i, sc))
    return path


def test_skuld_trend_reads_pulse_metrics_not_state_names(tmp_path):
    # History says "running" throughout (state approximation
    # would be a flat 100, prediction stable); the metrics
    # tell the real story: 90 falling steadily to 40.
    db = _make_db(tmp_path / "h.db", ["running"] * 10,
                  [90 - 5 * i for i in range(10)])
    check = SkuldCheck(_Cfg(db))
    rows = check._get_pulse_metrics(hours=168)
    assert [r["health_score"] for r in rows] == [90 - 5 * i for i in range(10)]
    trend = check._predict_health_trend()
    assert trend["score_source"] == "pulse_metrics"
    assert trend["prediction"] == "degrading"
    assert trend["data_points"] == 10


def test_skuld_falls_back_to_state_scores_without_metrics(tmp_path):
    db = _make_db(tmp_path / "h.db", ["running"] * 10, [])
    check = SkuldCheck(_Cfg(db))
    scores, source = check._health_score_series(hours=168)
    assert source == "pulse_history_state"
    assert scores == [100.0] * 10
    trend = check._predict_health_trend()
    assert trend["score_source"] == "pulse_history_state"
    assert trend["prediction"] == "stable"


def test_skuld_anomalies_and_emotion_use_metrics(tmp_path):
    scores = [50.0] * 20 + [5.0] + [50.0] * 5
    db = _make_db(tmp_path / "h.db", ["running"] * 26, scores)
    check = SkuldCheck(_Cfg(db))
    anomalies = check._detect_anomalies()
    assert anomalies["score_source"] == "pulse_metrics"
    low = _make_db(tmp_path / "h2.db", ["running"] * 7,
                   [48.0, 44.0, 40.0, 32.0, 24.0, 16.0, 8.0])
    emotion = SkuldCheck(_Cfg(low))._classify_emotion()
    # Low and degrading from the real scores — state names
    # alone (all "running") could never produce urgency.
    assert emotion["emotion"] == "urgency"


def test_skuld_missing_metrics_table_is_the_fallback(tmp_path):
    db = tmp_path / "h.db"
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(str(db)) as conn:
        conn.execute("CREATE TABLE pulse_history (id INTEGER PRIMARY "
                     "KEY AUTOINCREMENT, timestamp DATETIME, state TEXT, "
                     "checks_json TEXT, pulse_count INTEGER)")
        for i in range(6):
            conn.execute("INSERT INTO pulse_history (timestamp, state, "
                         "checks_json, pulse_count) VALUES (?, 'running', "
                         "'{}', ?)", (now, i))
    check = SkuldCheck(_Cfg(db))
    assert check._get_pulse_metrics(hours=168) == []
    assert check._health_score_series(hours=168)[1] == "pulse_history_state"


def test_doc_names_the_states_and_both_dockets():
    doc = _source(DOC)
    for needle in ("healthy", "degraded", "stuck", "dead", "absent",
                   "Docket 96", "Docket 34", "pulse_metrics",
                   "E-067", "E-070", "E-076"):
        assert needle in doc, needle
