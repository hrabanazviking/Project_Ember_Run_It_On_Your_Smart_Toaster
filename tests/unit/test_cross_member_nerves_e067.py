"""E-067 — Cross-member nerves: ember core ⇄ Verdandi ⇄ memory
wired under the E-061 contract.

Pins the three legs the slice wired:

1. heartbeat → hub: the daemon's pulse and state-change
   impulses are canonical v1 envelopes on the canonical hub
   socket, with a canonical feed fallback for BOTH (the state
   change's legacy shape was silently lost on failure).
2. conversation layer → hub, in-tree: the logger's nerve fire
   searches the deployed hub first and falls back to the
   sibling in-tree copy (docket 94, E-067 half).
3. ember core → hub: src/ember/nerve.py publishes ember_session
   and ember_turn under the registered shapes, chat.run crosses
   its session and turn facts (memory facts included, content
   never), and the bridge degrades honestly (ack / sent /
   fallback / error) without ever raising into the chat.

Plus the registry discipline: Verdandi/cross_member.py, the
core bridge's literals, and event_contract's registrations
must agree exactly, and the E-067 doc must name every
cross-member event.
"""

from __future__ import annotations

import ast
import importlib.util
import io
import json
import socket
import sys
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-067_CROSS_MEMBER_NERVES.md"

sys.path.insert(0, str(VERDANDI))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


contract = _load("ember_event_contract_e067", VERDANDI / "event_contract.py")
cross = _load("ember_cross_member_e067", VERDANDI / "cross_member.py")

from ember import nerve  # noqa: E402


def _short_dir() -> Path:
    """A short /tmp dir — AF_UNIX paths cap at ~108 chars, which
    deep pytest tmp paths (long test names, nested TMPDIRs)
    exceed; socket tests must bind and connect below the cap."""
    return Path(tempfile.mkdtemp(prefix="e067", dir="/tmp"))


# ── Registry coherence ─────────────────────────────────────────


def test_cross_member_version_matches_contract():
    assert cross.CROSS_MEMBER_VERSION == contract.CONTRACT_VERSION == 1
    assert cross.HUB_SOCKET_NAME == contract.CANONICAL_SOCKET_NAME == "runa.sock"
    assert cross.HUB_FEED_NAME == "nerve_feed.jsonl"
    assert "runa.sock" in _source(VERDANDI / "nervous_system.py")


def test_every_cross_member_spec_is_registered_canonical():
    for spec in cross.CROSS_MEMBER_SPECS:
        reg = contract.spec_for(spec.name, contract.DIALECT_HUB)
        assert reg is not None and reg.name == spec.name, spec.name
        assert reg.status == "canonical", spec.name
        assert reg.source == spec.source, spec.name
        assert tuple(reg.data_fields) == tuple(spec.data_fields), spec.name
        assert spec.producer.split(" ")[0] in reg.producer or reg.producer in spec.producer


def test_core_bridge_literals_match_the_registry():
    assert nerve.CONTRACT_VERSION == cross.CROSS_MEMBER_VERSION
    assert nerve.SOURCE == cross.SOURCE_EMBER_CORE
    session = cross.spec_for_cross("ember_session")
    turn = cross.spec_for_cross("ember_turn")
    assert tuple(nerve.SESSION_FIELDS) == tuple(session.data_fields)
    assert tuple(nerve.TURN_FIELDS) == tuple(turn.data_fields)
    assert tuple(nerve.SESSION_PHASES) == tuple(cross.SESSION_PHASES)
    assert tuple(nerve.PERSISTED_SHAPES) == tuple(cross.PERSISTED_SHAPES)
    assert tuple(nerve.TURN_OUTCOMES) == tuple(cross.TURN_OUTCOMES)


def test_heartbeat_literals_match_the_registry():
    core = _source(VERDANDI / "heartbeat" / "core.py")
    assert "_NERVE_CONTRACT_VERSION = 1" in core
    assert '_NERVE_SOURCE = "verdandi-heartbeat"' in core
    assert '"runa.sock"' in core
    assert cross.SOURCE_HEARTBEAT == "verdandi-heartbeat"


def test_doc_names_every_cross_member_event():
    doc = _source(DOC)
    for spec in cross.CROSS_MEMBER_SPECS:
        assert spec.name in doc, spec.name


# ── Envelope builders / validation ─────────────────────────────


def test_build_event_round_trips_validation():
    data = {"pulse_count": 3, "state": "running", "health_score": 0.9,
            "health_trend": "stable", "emotional_state": "calm", "checks": {}}
    event = cross.build_event("heartbeat_pulse", data)
    assert event["v"] == 1 and event["source"] == "verdandi-heartbeat"
    assert cross.validate_cross_event(event) == []
    assert contract.validate_publish(event) == []


def test_build_event_refuses_unregistered_and_field_drift():
    for bad in (
        lambda: cross.build_event("nope", {}),
        lambda: cross.build_event("ember_turn", {"conversation_id": "x"}),
        lambda: cross.build_event("ember_session", {
            "phase": "start", "persona_id": "p", "conversation_id": "c",
            "well_connected": True, "model": "m", "turns": 0, "extra": 1}),
    ):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("build_event accepted a bad event")


def test_validate_cross_event_catches_enum_and_type_drift():
    good = nerve.build_turn_event(
        conversation_id="c", persona_id="p", hits=1, cited=1,
        persisted="well", ungrounded=False, outcome="answered", model="m")
    assert cross.validate_cross_event(good) == []
    drifted = json.loads(json.dumps(good))
    drifted["data"]["persisted"] = "everywhere"
    assert cross.validate_cross_event(drifted) != []
    drifted = json.loads(json.dumps(good))
    drifted["data"]["hits"] = "many"
    assert cross.validate_cross_event(drifted) != []
    drifted = json.loads(json.dumps(good))
    drifted["source"] = "someone_else"
    assert cross.validate_cross_event(drifted) != []


# ── Leg 1: heartbeat → hub ─────────────────────────────────────


class _Cfg:
    def __init__(self, values):
        self._values = values

    def get(self, key, default=None):
        return self._values.get(key, default)


def _daemon(tmp_path, cfg_values):
    from heartbeat.core import DaemonState, HeartbeatDaemon

    daemon = HeartbeatDaemon.__new__(HeartbeatDaemon)
    daemon.config = _Cfg(cfg_values)
    daemon.state = SimpleNamespace(
        pulse_count=7,
        state=DaemonState.RUNNING,
        checks={},
        _emotional_state="calm",
    )
    daemon._health_score = SimpleNamespace(current=0.95, trend="stable")
    return daemon


class _SocketCapture:
    """A one-shot AF_UNIX server capturing a single line."""

    def __init__(self, path: Path):
        self.path = path
        self.lines: list[str] = []
        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(str(path))
        self._server.listen(1)
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        conn, _ = self._server.accept()
        with conn:
            self.lines.append(conn.recv(65536).decode())

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._thread.join(timeout=5)
        self._server.close()


def test_heartbeat_pulse_is_canonical_on_the_wire(tmp_path):
    sock_path = _short_dir() / "cap.sock"
    daemon = _daemon(tmp_path, {"nerve.socket_path": str(sock_path)})
    with _SocketCapture(sock_path) as cap:
        daemon._fire_nerve_pulse()
    event = json.loads(cap.lines[0])
    assert event["type"] == "heartbeat_pulse"
    assert "event_type" not in event
    assert cross.validate_cross_event(event) == []
    assert event["data"]["pulse_count"] == 7


def test_heartbeat_fallback_is_canonical_for_both_events(tmp_path, monkeypatch):
    import heartbeat.core as core_mod

    monkeypatch.setattr(core_mod, "get_state_dir", lambda: tmp_path)
    daemon = _daemon(tmp_path, {"nerve.socket_path": str(tmp_path / "absent.sock")})
    daemon._fire_nerve_pulse()
    from heartbeat.core import DaemonState

    daemon._fire_nerve_state_change(DaemonState.RUNNING, DaemonState.DEGRADED)
    lines = (tmp_path / "nerve_feed.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    for line in lines:
        event = json.loads(line)
        assert event["_fallback"] is True
        assert "event_type" not in event
        assert cross.validate_cross_event(
            {k: v for k, v in event.items() if not k.startswith("_")}) == []
    types = [json.loads(line)["type"] for line in lines]
    assert types == ["heartbeat_pulse", "heartbeat_state_change"]


def test_heartbeat_fallback_can_be_disabled(tmp_path, monkeypatch):
    import heartbeat.core as core_mod

    monkeypatch.setattr(core_mod, "get_state_dir", lambda: tmp_path)
    daemon = _daemon(tmp_path, {
        "nerve.socket_path": str(tmp_path / "absent.sock"),
        "nerve.fallback_to_file": False,
    })
    daemon._fire_nerve_pulse()
    assert not (tmp_path / "nerve_feed.jsonl").exists()


# ── Leg 2: logger → hub (in-tree fallback) ─────────────────────


def _fake_hub(path: Path, tag: str, record: Path) -> Path:
    path.write_text(
        "import json\n"
        "def publish_event_sync(event_type=None, data=None, source=None):\n"
        f"    with open({str(record)!r}, 'a') as f:\n"
        f"        f.write(json.dumps({{'hub': {tag!r}, 'type': event_type,"
        " 'source': source}) + '\\n')\n"
        "    return {'nerve_type': 'ack'}\n",
        encoding="utf-8",
    )
    return path


def test_logger_falls_back_to_sibling_hub(tmp_path, monkeypatch):
    logger_mod = _load("ember_logger_e067_a", VERDANDI / "conversation_logger.py")
    record = tmp_path / "record.jsonl"
    sibling = _fake_hub(tmp_path / "sibling_hub.py", "sibling", record)
    monkeypatch.setattr(
        logger_mod, "_nerve_candidate_paths",
        lambda: [tmp_path / "no_deployed.py", sibling],
    )
    logger_mod._nerve_module = None
    logger_mod._nerve_module_path = None
    logger_mod._nerve_fire({"entry_type": "start", "session_id": "s1"})
    rows = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()]
    assert rows == [{"hub": "sibling", "type": "conv_start", "source": "conv_logger:s1"}]


def test_logger_deployed_hub_still_wins(tmp_path, monkeypatch):
    logger_mod = _load("ember_logger_e067_b", VERDANDI / "conversation_logger.py")
    record = tmp_path / "record.jsonl"
    deployed = _fake_hub(tmp_path / "deployed_hub.py", "deployed", record)
    sibling = _fake_hub(tmp_path / "sibling_hub.py", "sibling", record)
    monkeypatch.setattr(
        logger_mod, "_nerve_candidate_paths",
        lambda: [deployed, sibling],
    )
    logger_mod._nerve_module = None
    logger_mod._nerve_module_path = None
    logger_mod._nerve_fire({"entry_type": "end", "session_id": "s2"})
    rows = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["hub"] == "deployed"


def test_logger_default_candidates_put_deployed_first_and_sibling_second():
    logger_mod = _load("ember_logger_e067_c", VERDANDI / "conversation_logger.py")
    candidates = logger_mod._nerve_candidate_paths()
    assert candidates[0] == logger_mod.STATE_DIR / "nervous_system.py"
    assert candidates[1] == VERDANDI / "nervous_system.py"
    assert candidates[1].exists()


# ── Leg 3: the core bridge ─────────────────────────────────────


def test_bridge_fallback_writes_canonical_feed_line(tmp_path):
    state = _short_dir()
    result = nerve.publish_session(
        "start", persona_id="p1", conversation_id="c1",
        well_connected=True, model="m1", state_dir=state,
    )
    assert result["nerve_type"] == "fallback"
    lines = (state / "nerve_feed.jsonl").read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[0])
    assert event["_fallback"] is True
    assert cross.validate_cross_event(
        {k: v for k, v in event.items() if not k.startswith("_")}) == []


def test_bridge_reaches_a_live_socket_and_reads_back(tmp_path):
    state = _short_dir()
    sock_path = state / "runa.sock"
    received: list[dict] = []

    def serve():
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(sock_path))
        server.listen(4)
        server.settimeout(10)
        try:
            for _ in range(2):
                conn, _ = server.accept()
                with conn:
                    msg = json.loads(conn.recv(65536).decode().strip())
                    if msg.get("nerve_type") == "recent":
                        conn.sendall(json.dumps({
                            "nerve_type": "recent_events",
                            "events": received,
                        }).encode() + b"\n")
                    else:
                        received.append(msg)
                        conn.sendall(json.dumps(
                            {"nerve_type": "ack", "seq": len(received)}
                        ).encode() + b"\n")
        finally:
            server.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    deadline = datetime.now(tz=UTC).timestamp() + 5
    while not sock_path.exists() and datetime.now(tz=UTC).timestamp() < deadline:
        pass
    result = nerve.publish_turn(
        conversation_id="c1", persona_id="p1", hits=2, cited=1,
        persisted="well", ungrounded=False, outcome="answered",
        model="m1", state_dir=state,
    )
    assert result == {"nerve_type": "ack", "seq": 1}
    assert cross.validate_cross_event(received[0]) == []
    back = nerve.read_recent(5, state_dir=state)
    assert [e["type"] for e in back] == ["ember_turn"]
    thread.join(timeout=5)


def test_bridge_read_recent_feed_shape_and_empty(tmp_path):
    state = _short_dir()
    assert nerve.read_recent(3, state_dir=state) == []
    nerve.publish_session(
        "end", persona_id="p1", conversation_id="c1",
        well_connected=False, model="m1", turns=2, state_dir=state,
    )
    back = nerve.read_recent(3, state_dir=state)
    assert len(back) == 1 and back[0]["type"] == "ember_session"
    assert back[0]["data"]["turns"] == 2


def test_bridge_builders_refuse_bad_vocabularies():
    for bad in (
        lambda: nerve.build_session_event(
            "middle", persona_id="p", conversation_id="c",
            well_connected=True, model="m", turns=0),
        lambda: nerve.build_turn_event(
            conversation_id="c", persona_id="p", hits=0, cited=0,
            persisted="cloud", ungrounded=False, outcome="answered", model="m"),
        lambda: nerve.build_turn_event(
            conversation_id="c", persona_id="p", hits=0, cited=0,
            persisted="well", ungrounded=False, outcome="shrugged", model="m"),
    ):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("bridge builder accepted a bad vocabulary")


def test_bridge_never_raises_on_unwritable_feed(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a directory", encoding="utf-8")
    result = nerve.publish_session(
        "start", persona_id="p", conversation_id="c",
        well_connected=True, model="m", state_dir=blocker / "sub",
    )
    assert result["nerve_type"] == "error"


def test_bridge_imports_stdlib_only():
    tree = ast.parse(_source(REPO / "src" / "ember" / "nerve.py"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__", "ember"}


# ── Leg 3 in chat: session + turn facts cross, content never ──


class _NullEmbedder:
    def embed(self, texts):
        return [None for _ in texts]


class _Brunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self.episodes: list = []

    def recent_episodes(self, limit):
        return []

    def add_episode(self, episode):
        self.episodes.append(episode)
        return 1

    def hybrid_search(self, *a, **kw):
        return []

    def text_search(self, *a, **kw):
        return []

    def close(self) -> None:
        return None


class _StreamingFuni:
    runtime_kind = "fake"
    model_id = "fake:e067"

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        from ember.schemas.stream import FuniStreamChunk
        from ember.schemas.funi import FinishReason

        yield FuniStreamChunk(text_delta="REPLY WORDS MUST NOT CROSS", done=False)
        yield FuniStreamChunk(
            text_delta="", done=True,
            finish_reason=FinishReason.STOP, model_id=self.model_id,
        )

    def health(self):
        from ember.schemas.funi import FuniHealth

        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def _run_chat(tmp_path, lines):
    from ember.schemas.config import (
        BrunnrConfig, EmberConfig, FuniConfig, IdentityConfig,
        LoggingConfig, SqliteVecConfig, StrengrConfig,
    )
    from ember.spark.hjarta import save_identity_atomic
    from ember.spark.munnr import chat

    config_root = tmp_path / "ember-home"
    save_identity_atomic(config_root, IdentityConfig())
    config = EmberConfig(
        funi=FuniConfig(streaming=True),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
        logging=LoggingConfig(diary=True),
    )
    stdout = io.StringIO()
    rc = chat.run(
        config=config,
        config_root=config_root,
        stdin=io.StringIO(lines),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: _StreamingFuni(),
        strengr_opener=lambda _s, _b: _Brunnr(),
    )
    return rc


def test_chat_crosses_session_and_turn_facts_without_content(tmp_path):
    rc = _run_chat(tmp_path, "OPERATOR WORDS MUST NOT CROSS\n/exit\n")
    assert rc == 0
    # The conftest fixture redirected the bridge home to a
    # short /tmp dir; no hub runs there, so every publish
    # landed in its feed as a canonical fallback line.
    feed = nerve.hub_state_dir() / "nerve_feed.jsonl"
    raw = feed.read_text(encoding="utf-8")
    assert "OPERATOR WORDS MUST NOT CROSS" not in raw
    assert "REPLY WORDS MUST NOT CROSS" not in raw
    events = [json.loads(line) for line in raw.splitlines()]
    assert [e["type"] for e in events] == ["ember_session", "ember_turn", "ember_session"]
    for event in events:
        assert cross.validate_cross_event(
            {k: v for k, v in event.items() if not k.startswith("_")}) == []
    assert events[0]["data"]["phase"] == "start"
    assert events[0]["data"]["well_connected"] is True
    assert events[1]["data"]["persisted"] == "well"
    assert events[1]["data"]["outcome"] == "answered"
    assert events[2]["data"]["phase"] == "end"
    assert events[2]["data"]["turns"] == 1
