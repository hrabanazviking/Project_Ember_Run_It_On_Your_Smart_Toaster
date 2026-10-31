"""E-029 — Offline truth: the core's full local life, network cut.

The roadmap asks: *"with the network cut, the core's full local
life works — proven, with the degraded set listed honestly."*

These tests cut the network in the only honest in-process way:
every socket resolution or connection to a non-loopback address
raises, and every such attempt is recorded. Loopback (127.0.0.1 /
::1 / localhost) stays open — that is what "the network is cut"
means for a tethered companion: the outside world is gone, the
machine itself is still there.

Under that cut, proven here against the REAL adapters (no fake
Funi, no fake embedder):

1. The guard itself bites: an external connection and an external
   DNS lookup both fail and are recorded — the cut is real, not
   assumed.
2. A full chat turn runs end to end: the real Ollama adapter opens
   against a loopback server, the real embed client embeds over
   loopback, retrieval runs, the streamed reply renders, and the
   Episode is persisted. Zero external attempts.
3. The local tools keep working: ``read_local_file`` reads under
   the cut.
4. The degraded set fails HONESTLY, never by crash or fabrication:
   ``fetch_url`` to an external site returns a typed error reply
   naming the failed DNS lookup; the embed client against an
   external endpoint returns ``None`` vectors; a Funi backend
   configured at an external address opens as typed
   ``Unavailable``, so chat would refuse with the reason named.
5. The local Well (sqlite_vec shape, extras-supplied — skips
   honestly without them, exactly as E-021) stores and re-reads an
   Episode across a reopen, entirely on disk, under the cut.

The degraded set is listed in docs/architecture/
E-029_OFFLINE_TRUTH.md.
"""

from __future__ import annotations

import io
import ipaddress
import json
import socket
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    EmbeddingConfig,
    FuniConfig,
    FuniOllamaConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
    ToolsConfig,
)
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import Unavailable, UnavailableReason
from ember.schemas.tool import ToolCall
from ember.spark.funi import handle as funi_handle
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat
from ember.tools import fetch_url, read_local_file
from ember.well.smidja.embed_client import OllamaEmbedClient

# --------------------------------------------------------------------- #
# The network cut                                                         #
# --------------------------------------------------------------------- #

_LOCAL_NAMES = {"localhost", "ip6-localhost"}
_LOCAL_HOSTNAME = socket.gethostname()


def _is_local_host(host: object) -> bool:
    if host is None or host == "":
        return True
    if not isinstance(host, str):
        return False
    if host in _LOCAL_NAMES or host == _LOCAL_HOSTNAME:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class _OfflineGuard:
    """Records and refuses every non-loopback resolution/connect."""

    def __init__(self) -> None:
        self.attempts: list[str] = []
        self._real_getaddrinfo = socket.getaddrinfo
        self._real_connect = socket.socket.connect

    def getaddrinfo(self, host, port, *args, **kwargs):
        if _is_local_host(host):
            return self._real_getaddrinfo(host, port, *args, **kwargs)
        self.attempts.append(f"dns:{host}")
        raise socket.gaierror(f"E-029 offline cut: DNS for {host!r} refused")

    def connect(self, sock, address):
        host = address[0] if isinstance(address, tuple) else None
        if host is None or _is_local_host(host):
            return self._real_connect(sock, address)
        self.attempts.append(f"connect:{host}")
        raise OSError(f"E-029 offline cut: connection to {host!r} refused")


@pytest.fixture
def offline(monkeypatch: pytest.MonkeyPatch) -> _OfflineGuard:
    guard = _OfflineGuard()

    def _connect(sock, address):  # plain function: binds as a method
        return guard.connect(sock, address)

    monkeypatch.setattr(socket, "getaddrinfo", guard.getaddrinfo)
    monkeypatch.setattr(socket.socket, "connect", _connect)
    return guard


# --------------------------------------------------------------------- #
# A real loopback Ollama-shaped server                                    #
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

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler shape
        if self.path == "/api/version":
            self._send_json({"version": "0.0-e029"})
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
                {"message": {"role": "assistant", "content": "local "},
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


@pytest.fixture
def loopback_ollama():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _LoopbackOllamaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


# --------------------------------------------------------------------- #
# 1. The cut is real                                                      #
# --------------------------------------------------------------------- #


def test_offline_guard_blocks_external_connect_and_dns(offline) -> None:
    with pytest.raises(OSError):
        socket.create_connection(("203.0.113.7", 443), timeout=2)
    with pytest.raises(OSError):
        socket.getaddrinfo("example.com", 443)
    assert any(a.startswith("dns:") for a in offline.attempts)


# --------------------------------------------------------------------- #
# 2. A full chat turn over loopback, under the cut                        #
# --------------------------------------------------------------------- #


class _CapturingBrunnr:
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

    def count(self):  # pragma: no cover
        return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    def close(self) -> None:
        return None


def _disconnected() -> Disconnected:
    return Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
    )


def test_chat_turn_end_to_end_over_loopback_offline(
    tmp_path: Path, offline, loopback_ollama: str,
) -> None:
    config_root = tmp_path / "ember-home"
    save_identity_atomic(config_root, IdentityConfig())
    config = EmberConfig(
        funi=FuniConfig(
            streaming=True,
            ollama=FuniOllamaConfig(base_url=loopback_ollama, model="fake:local"),
        ),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
        tools=ToolsConfig(enabled=False),
    )
    embedder = OllamaEmbedClient(
        config=EmbeddingConfig(endpoint=f"{loopback_ollama}/api/embed"),
        max_attempts=1,
    )
    brunnr = _CapturingBrunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=config,
        config_root=config_root,
        stdin=io.StringIO("hello\n/exit\n"),
        stdout=stdout,
        embed_client=embedder,
        # No funi_opener: the REAL Ollama adapter opens, over loopback.
        strengr_opener=lambda _s, _b: brunnr,
    )
    assert rc == 0
    assert "local answer" in stdout.getvalue()
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].ember_reply == "local answer"
    # The whole turn — open probe, embedding, retrieval, generation,
    # persistence — attempted nothing outside this machine.
    assert offline.attempts == []


# --------------------------------------------------------------------- #
# 3. Local tools keep working                                             #
# --------------------------------------------------------------------- #


def test_read_local_file_works_offline(
    tmp_path: Path, offline, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    note = tmp_path / "notes.txt"
    note.write_text("the toaster is warm\n", encoding="utf-8")
    reply = read_local_file._execute(
        ToolCall(call_id="c1", name="read_local_file",
                 arguments={"path": str(note)})
    )
    assert reply.error is None
    assert "the toaster is warm" in (reply.output or "")
    assert offline.attempts == []


# --------------------------------------------------------------------- #
# 4. The degraded set fails honestly                                      #
# --------------------------------------------------------------------- #


def test_fetch_url_external_is_an_honest_error_offline(offline) -> None:
    fetch_url._reset_seams()
    try:
        reply = fetch_url._execute(
            ToolCall(call_id="c1", name="fetch_url",
                     arguments={"url": "https://example.com/"})
        )
    finally:
        fetch_url._reset_seams()
    # A typed error reply naming the failure — never a crash, never
    # fabricated content.
    assert reply.error is not None
    assert "DNS lookup failed" in reply.error
    assert reply.output in (None, "")
    assert any("example.com" in a for a in offline.attempts)


def test_embed_client_external_endpoint_degrades_to_none(offline) -> None:
    client = OllamaEmbedClient(
        config=EmbeddingConfig(
            endpoint="http://203.0.113.9:11434/api/embed",
        ),
        max_attempts=1,
        backoff_base_s=0.0,
    )
    # Failure is data (None vectors), not an exception — the caller
    # degrades to text search, per the Vow of Graceful Offline.
    assert client.embed(["hello"]) == [None]
    assert offline.attempts != []


def test_external_funi_backend_opens_unavailable_offline(offline) -> None:
    config = FuniConfig(
        ollama=FuniOllamaConfig(
            base_url="http://203.0.113.9:11434", model="fake:remote",
        ),
    )
    result = funi_handle.open(config)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.ENDPOINT_UNREACHABLE
    assert offline.attempts != []


# --------------------------------------------------------------------- #
# 5. The local Well on disk, under the cut (extras shape)                 #
# --------------------------------------------------------------------- #


def test_sqlite_well_round_trip_offline(tmp_path: Path, offline) -> None:
    pytest.importorskip("sqlite_vec")
    from ember.schemas.episode import Episode
    from ember.well.brunnr.sqlite_vec import open as sqlite_open

    config = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    )
    handle = sqlite_open(config)
    handle.add_episode(Episode(
        operator_input="offline question",
        ember_reply="offline answer",
        funi_model="fake:local",
        started_at=datetime.now(tz=UTC),
        completed_at=datetime.now(tz=UTC),
    ))
    handle.close()

    reopened = sqlite_open(config)
    try:
        got = reopened.recent_episodes(10)
    finally:
        reopened.close()
    assert [e.ember_reply for e in got] == ["offline answer"]
    assert offline.attempts == []
