"""E-032 — The day-one flow: install → first model → first chat.

The roadmap asks for the day-one flow *"timed and friction-audited
(Part XII's Stranger Test consumes)"*. The audit (docs/architecture/
E-032_DAY_ONE_FLOW.md) ran the real flow in a clean venv on the VM
profile and found three frictions that broke or misled a stranger;
each is fixed in this slice and pinned here:

1. **Docket 15 — closed stdin crashed the wizard.** Hjarta caught
   Ctrl-C but not EOF, so `ember ask … < /dev/null` (or any script
   that ran out of answers) died with a raw EOFError traceback.
   EOF is now a clean abort at the current state, nothing written.
2. **Docket 88 — Hjarta wrote a config its own install could not
   read back.** The documented install is `ember-agent[sqlite_vec]`
   — no PyYAML — but Hjarta always wrote `ember.yaml`, and the
   loader needs PyYAML for YAML. The first launch's own post-setup
   reload, and every later launch, died with "PyYAML is not
   installed". The writer now falls back to `ember.toml`
   (stdlib-readable) when PyYAML is not importable.
3. **Docket 87 — a Well path typed in the wizard was forgotten.**
   Hjarta probed the chosen path, then wrote a config with no trace
   of it, so the next chat reopened the DEFAULT Well. The choice is
   now persisted in the written config and reloaded.

Also pinned: the install contract a stranger relies on (console
entry point, zero core dependencies, the documented extras), the
wizard's exact prompt count (5), and the full flow — wizard with
fake backends, then a first chat over a loopback Ollama-shaped
server (the E-029 pattern) using the identity the wizard wrote.
Real-model timing is NOT claimed here: the timings in the E-032
doc are from the clean-venv run against a wire-shape server, and
Part III owns real-hardware proof.
"""

from __future__ import annotations

import io
import json
import threading
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from ember.config import load_ember_config, write_ember_config
from ember.config import writer as config_writer
from ember.schemas.chunks import BrunnrStats, Document, RetrievalHit
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    FuniOllamaConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
    ToolsConfig,
)
from ember.schemas.errors import Disconnected
from ember.schemas.funi import FuniHealth
from ember.spark.hjarta import HjartaIO, HjartaState, has_identity
from ember.spark.hjarta import run as hjarta_run
from ember.spark.munnr import chat, setup

# --------------------------------------------------------------------- #
# Test doubles (the Hjarta machine test's shapes)                         #
# --------------------------------------------------------------------- #


class _FakeFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"
    embedding_dim = 4

    def health(self) -> FuniHealth:
        from datetime import UTC, datetime

        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


class _FakeBrunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self._docs: dict[str, int] = {}
        self._chunks: list[str] = []
        self.episodes: list = []

    def add_document(self, doc: Document) -> int:
        return self._docs.setdefault(doc.hash, len(self._docs) + 1)

    def add_chunks(self, chunks):
        self._chunks.extend(c.text for c in chunks)
        return list(range(len(self._chunks)))

    def add_episode(self, episode):
        self.episodes.append(episode)
        return 1

    def recent_episodes(self, limit):
        return []

    def text_search(self, query: str, k: int, filter=None):
        return [
            RetrievalHit(chunk_id=i + 1, document_id=1, document_title="probe",
                         text=t, score=1.0)
            for i, t in enumerate(self._chunks)
            if any(w in t.lower() for w in query.lower().split())
        ][:k]

    def hybrid_search(self, *a, **kw):
        return []

    def count(self):
        return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    def close(self) -> None:
        return None


def _counting_io(answers: list[str]):
    prompts: list[str] = []
    answer_iter = iter(answers)

    def prompt(text: str) -> str:
        prompts.append(text)
        return next(answer_iter, "")

    io_obj = HjartaIO(prompt=prompt, info=lambda _s: None, error=lambda _s: None)
    return io_obj, prompts


def _run_wizard(tmp_path: Path, answers: list[str], brunnr=None):
    io_obj, prompts = _counting_io(answers)
    outcome = hjarta_run(
        config=EmberConfig(),
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _c: _FakeFuni(),
        strengr_opener=lambda _s, _b: brunnr or _FakeBrunnr(),
    )
    return outcome, prompts


# --------------------------------------------------------------------- #
# 1. Docket 15 — EOF is a clean abort, never a traceback                   #
# --------------------------------------------------------------------- #


def test_hjarta_eof_at_greet_is_a_clean_abort(tmp_path: Path) -> None:
    def eof(_text: str) -> str:
        raise EOFError

    io_obj = HjartaIO(prompt=eof, info=lambda _s: None, error=lambda _s: None)
    outcome = hjarta_run(
        config=EmberConfig(),
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _c: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success is False
    assert outcome.final_state is HjartaState.GREET
    assert "end of input" in (outcome.detail or "")
    assert not has_identity(tmp_path)


def test_hjarta_eof_mid_wizard_is_a_clean_abort(tmp_path: Path) -> None:
    answers = iter(["", ""])

    def prompt(_text: str) -> str:
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    io_obj = HjartaIO(prompt=prompt, info=lambda _s: None, error=lambda _s: None)
    outcome = hjarta_run(
        config=EmberConfig(),
        config_root=tmp_path,
        io=io_obj,
        funi_opener=lambda _c: _FakeFuni(),
        strengr_opener=lambda _s, _b: _FakeBrunnr(),
    )
    assert outcome.success is False
    assert outcome.final_state is HjartaState.CHOOSE_WELL
    assert not has_identity(tmp_path)


def test_setup_run_reports_eof_as_failure_not_traceback(tmp_path: Path) -> None:
    def eof(_text: str) -> str:
        raise EOFError

    io_obj = HjartaIO(prompt=eof, info=lambda _s: None, error=lambda _s: None)
    stdout = io.StringIO()
    rc = setup.run(
        config=EmberConfig(), config_root=tmp_path, stdout=stdout, io=io_obj,
    )
    assert rc == 1
    assert "Setup did not complete" in stdout.getvalue()
    assert not has_identity(tmp_path)


# --------------------------------------------------------------------- #
# 2. Docket 88 — the written config is readable by the install that      #
#    wrote it (TOML fallback when PyYAML is absent)                       #
# --------------------------------------------------------------------- #


def test_writer_falls_back_to_toml_without_pyyaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(config_writer, "_yaml_available", lambda: False)
    written = write_ember_config(
        tmp_path,
        IdentityConfig(name="Spark"),
        extras={
            "tools": {"enabled": True},
            "brunnr": {"sqlite_vec": {"path": "/tmp/e032/well.db"}},
        },
    )
    assert written.name == "ember.toml"
    assert written.is_file()
    # The loader's stdlib TOML road reads back every choice.
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"
    assert cfg.tools.enabled is True
    assert cfg.brunnr.sqlite_vec is not None
    assert str(cfg.brunnr.sqlite_vec.path) == "/tmp/e032/well.db"


def test_writer_still_prefers_yaml_with_pyyaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("yaml")
    monkeypatch.setattr(config_writer, "_yaml_available", lambda: True)
    written = write_ember_config(tmp_path, IdentityConfig(name="Spark"))
    assert written.name == "ember.yaml"
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.identity.name == "Spark"


# --------------------------------------------------------------------- #
# 3. Docket 87 — the wizard's Well choice survives into the next launch   #
# --------------------------------------------------------------------- #


def test_wizard_persists_the_chosen_well_path(tmp_path: Path) -> None:
    custom = tmp_path / "elsewhere" / "my-well.db"
    outcome, _prompts = _run_wizard(
        tmp_path, ["", "", str(custom), "", ""],
    )
    assert outcome.success is True
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.brunnr.sqlite_vec is not None
    assert Path(cfg.brunnr.sqlite_vec.path) == custom


def test_wizard_default_well_writes_no_brunnr_override(tmp_path: Path) -> None:
    outcome, _prompts = _run_wizard(tmp_path, ["", "", "", "", ""])
    assert outcome.success is True
    cfg = load_ember_config(tmp_path, skip_env=True)
    # The default path is the schema default, not a wizard override.
    assert cfg.brunnr.sqlite_vec is not None
    assert Path(cfg.brunnr.sqlite_vec.path) == Path("~/.ember/well/store.db")


# --------------------------------------------------------------------- #
# 4. The install contract + the full day-one flow                         #
# --------------------------------------------------------------------- #


def test_install_contract_from_pyproject() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    data = tomllib.loads((repo_root / "pyproject.toml").read_text("utf-8"))
    project = data["project"]
    assert project["scripts"]["ember"] == "ember.cli.main:main"
    assert project["dependencies"] == []  # stdlib-only core, E-007
    extras = project["optional-dependencies"]
    # The two extras the day-one docs name must exist under those names.
    assert "sqlite_vec" in extras
    assert "config" in extras


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
            self._send_json({"version": "0.0-e032"})
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
                {"message": {"role": "assistant", "content": "day-one "},
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


def test_day_one_wizard_then_first_chat(tmp_path: Path) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _LoopbackOllamaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        # Step 1 — the wizard: exactly five questions stand between a
        # stranger and a working companion (greet, runtime, Well,
        # name, tools).
        outcome, prompts = _run_wizard(
            tmp_path, ["", "", "", "Spark", ""],
        )
        assert outcome.success is True
        assert len(prompts) == 5
        assert has_identity(tmp_path)

        # Step 2 — the first chat, in a NEW launch whose config is
        # reloaded from what the wizard wrote (name included).
        config = load_ember_config(tmp_path, skip_env=True)
        assert config.identity.name == "Spark"
        config = EmberConfig(
            identity=config.identity,
            funi=FuniConfig(
                streaming=True,
                ollama=FuniOllamaConfig(base_url=base_url, model="fake:local"),
            ),
            strengr=StrengrConfig(retry_backoff_max_s=0.0),
            brunnr=BrunnrConfig(
                embedding_dim=4,
                sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
            ),
            tools=ToolsConfig(enabled=False),
        )
        from ember.schemas.config import EmbeddingConfig
        from ember.well.smidja.embed_client import OllamaEmbedClient

        brunnr = _FakeBrunnr()
        stdout = io.StringIO()
        rc = chat.run(
            config=config,
            config_root=tmp_path,
            stdin=io.StringIO("hello\n/exit\n"),
            stdout=stdout,
            embed_client=OllamaEmbedClient(
                config=EmbeddingConfig(endpoint=f"{base_url}/api/embed"),
                max_attempts=1,
            ),
            strengr_opener=lambda _s, _b: brunnr,
        )
        assert rc == 0
        assert "day-one answer" in stdout.getvalue()
        assert len(brunnr.episodes) == 1
        assert not isinstance(brunnr, Disconnected)
    finally:
        server.shutdown()
        server.server_close()
