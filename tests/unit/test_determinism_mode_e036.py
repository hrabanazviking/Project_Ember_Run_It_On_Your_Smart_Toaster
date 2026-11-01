"""E-036 — determinism mode for tests/benchmarks (seeded).

Pins the E-036 contract:

- The mode is OFF by default: effective generation options are
  the operator's configured ones, unchanged, and NO seed key is
  added — a normal request keeps its pre-E-036 shape exactly.
- ON, every implemented backend's request carries the same
  fixed seed and temperature 0.0 (greedy): Ollama as the
  ``seed`` generation option, Aesir as the native route's
  ``seed`` field (its API support matrix v1 names that field).
  The operator's configured temperature is never mutated; it
  returns when the mode is switched off.
- A negative or non-integer seed in an ENABLED mode is refused
  at open time as typed CONFIG_INVALID, before any request —
  never clamped, dropped, or crashed on. A disabled mode's
  seed is inert.
- Surfaces: config file (``funi.determinism``, TOML-pinned) and
  the one-run CLI flags ``--deterministic`` / ``--seed``
  (``--seed`` implies the mode; neither is ever saved).
- Retrieval ranking is deterministic by construction: hybrid
  RRF ties break on chunk_id, not on which search happened to
  return a chunk first (extras shape — the sqlite_vec adapter
  imports its optional extra at module level).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ember.cli.main import _apply_determinism_override, _build_parser
from ember.config import load_ember_config
from ember.schemas.config import (
    DeterminismConfig,
    EmberConfig,
    FuniAesirConfig,
    FuniConfig,
    FuniRuntime,
)
from ember.schemas.funi import FinishReason, Unavailable, UnavailableReason
from ember.spark.funi.determinism import (
    DETERMINISTIC_TEMPERATURE,
    determinism_error,
    effective_options,
    is_deterministic,
)
from ember.spark.funi.aesir import open as aesir_open
from ember.spark.funi.ollama import open as ollama_open

# --------------------------------------------------------------------- #
# Transport fakes (E-022/E-023 shapes)                                   #
# --------------------------------------------------------------------- #


class _Resp:
    def __init__(self, payload: dict[str, Any] | bytes) -> None:
        self._body = (
            payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        )

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _Resp:
        return self

    def __exit__(self, *_: object) -> None:
        return None


class _StreamResp:
    def __init__(self, lines: list[dict[str, Any]]) -> None:
        self._lines = [json.dumps(x).encode() + b"\n" for x in lines]

    def __iter__(self):
        return iter(self._lines)

    def close(self) -> None:
        return None


class _Capture:
    """urlopen fake: records requests + parsed bodies, routes by suffix."""

    def __init__(self, routes: dict[str, Any]) -> None:
        self.routes = routes
        self.requests: list[Any] = []
        self.bodies: list[dict[str, Any]] = []

    def __call__(self, request, *, timeout: float = 0.0):
        self.requests.append(request)
        if request.data:
            self.bodies.append(json.loads(request.data))
        for suffix, response in self.routes.items():
            if request.full_url.endswith(suffix):
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(f"unexpected URL: {request.full_url}")


def _funi(runtime: FuniRuntime, det: DeterminismConfig, **kw: Any) -> FuniConfig:
    return FuniConfig(runtime=runtime, determinism=det, **kw)


# --------------------------------------------------------------------- #
# The pure contract                                                      #
# --------------------------------------------------------------------- #


def test_mode_is_off_by_default_with_seed_42() -> None:
    cfg = FuniConfig()
    assert cfg.determinism == DeterminismConfig(enabled=False, seed=42)
    assert is_deterministic(cfg) is False
    assert determinism_error(cfg) is None


def test_disabled_mode_options_are_unchanged_and_seedless() -> None:
    base = {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024}
    out = effective_options(base, FuniConfig())
    assert out == base
    assert "seed" not in out
    assert out is not base  # a copy — the caller's dict is never mutated


def test_enabled_mode_forces_greedy_and_seed_preserving_the_rest() -> None:
    base = {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024}
    cfg = _funi(FuniRuntime.OLLAMA, DeterminismConfig(enabled=True, seed=7))
    out = effective_options(base, cfg)
    assert out == {
        "temperature": DETERMINISTIC_TEMPERATURE,
        "top_p": 0.9,
        "num_predict": 1024,
        "seed": 7,
    }
    assert DETERMINISTIC_TEMPERATURE == 0.0
    # The configured temperature itself is untouched.
    assert base == {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024}
    assert cfg.ollama.temperature == 0.7


def test_repeat_calls_give_identical_options() -> None:
    cfg = _funi(FuniRuntime.OLLAMA, DeterminismConfig(enabled=True, seed=123))
    base = {"temperature": 0.3, "top_p": 0.5}
    assert effective_options(base, cfg) == effective_options(base, cfg)


@pytest.mark.parametrize("bad_seed", [-1, -999])
def test_negative_seed_is_an_error_only_when_enabled(bad_seed: int) -> None:
    on = _funi(FuniRuntime.OLLAMA, DeterminismConfig(enabled=True, seed=bad_seed))
    assert determinism_error(on) is not None
    assert str(bad_seed) in (determinism_error(on) or "")
    off = _funi(FuniRuntime.OLLAMA, DeterminismConfig(enabled=False, seed=bad_seed))
    assert determinism_error(off) is None  # inert while the mode is off


def test_bool_seed_is_not_a_seed() -> None:
    cfg = _funi(
        FuniRuntime.OLLAMA, DeterminismConfig(enabled=True, seed=True)  # type: ignore[arg-type]
    )
    assert determinism_error(cfg) is not None


# --------------------------------------------------------------------- #
# Config file + CLI surfaces                                             #
# --------------------------------------------------------------------- #


def test_determinism_loads_through_the_toml_loader(tmp_path: Path) -> None:
    toml = tmp_path / "ember.toml"
    toml.write_text(
        "[funi.determinism]\nenabled = true\nseed = 7\n", encoding="utf-8"
    )
    cfg = load_ember_config(file_override=toml, skip_env=True)
    assert cfg.funi.determinism == DeterminismConfig(enabled=True, seed=7)


def test_cli_override_no_flags_returns_the_same_config() -> None:
    cfg = EmberConfig()
    args = argparse.Namespace(deterministic=False, seed=None)
    assert _apply_determinism_override(cfg, args) is cfg


def test_cli_deterministic_flag_uses_the_configured_seed() -> None:
    cfg = EmberConfig()
    args = argparse.Namespace(deterministic=True, seed=None)
    out = _apply_determinism_override(cfg, args)
    assert out.funi.determinism == DeterminismConfig(enabled=True, seed=42)
    assert cfg.funi.determinism.enabled is False  # original untouched


def test_cli_seed_flag_implies_the_mode_and_wins() -> None:
    cfg = EmberConfig()
    args = argparse.Namespace(deterministic=False, seed=99)
    out = _apply_determinism_override(cfg, args)
    assert out.funi.determinism == DeterminismConfig(enabled=True, seed=99)


def test_cli_parser_accepts_the_flags_before_the_subcommand() -> None:
    args = _build_parser().parse_args(["--seed", "5", "doctor"])
    assert args.seed == 5
    assert args.deterministic is False
    args = _build_parser().parse_args(["--deterministic", "doctor"])
    assert args.deterministic is True
    assert args.seed is None


# --------------------------------------------------------------------- #
# Ollama on the wire                                                     #
# --------------------------------------------------------------------- #

_CHAT_OK = {
    "model": "phi3:mini",
    "message": {"role": "assistant", "content": "hello"},
    "done_reason": "stop",
    "prompt_eval_count": 3,
    "eval_count": 1,
}


def _ollama_capture() -> _Capture:
    return _Capture(
        {"/api/version": _Resp({"version": "0.1.32"}), "/api/chat": _Resp(_CHAT_OK)}
    )


def test_ollama_request_is_seedless_and_configured_by_default() -> None:
    capture = _ollama_capture()
    with patch("urllib.request.urlopen", side_effect=capture):
        handle = ollama_open(FuniConfig(runtime=FuniRuntime.OLLAMA))
        assert not isinstance(handle, Unavailable)
        reply = handle.complete("hi", [])
    assert reply.finish_reason is FinishReason.STOP
    options = capture.bodies[-1]["options"]
    assert options == {"temperature": 0.7, "top_p": 0.9, "num_predict": 1024}


def test_ollama_request_carries_seed_and_greedy_temperature_when_on() -> None:
    capture = _ollama_capture()
    cfg = _funi(FuniRuntime.OLLAMA, DeterminismConfig(enabled=True, seed=7))
    with patch("urllib.request.urlopen", side_effect=capture):
        handle = ollama_open(cfg)
        assert not isinstance(handle, Unavailable)
        reply = handle.complete("hi", [])
    assert reply.finish_reason is FinishReason.STOP
    options = capture.bodies[-1]["options"]
    assert options == {
        "temperature": 0.0,
        "top_p": 0.9,
        "num_predict": 1024,
        "seed": 7,
    }


def test_ollama_negative_seed_is_refused_before_any_request() -> None:
    capture = _ollama_capture()
    cfg = _funi(FuniRuntime.OLLAMA, DeterminismConfig(enabled=True, seed=-1))
    with patch("urllib.request.urlopen", side_effect=capture):
        result = ollama_open(cfg)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
    assert capture.requests == []  # not even the version probe was sent


# --------------------------------------------------------------------- #
# Aesir on the wire                                                      #
# --------------------------------------------------------------------- #

_KEY = "testkey-" + "a" * 32
_READY = {
    "schema_version": 1,
    "status": "ready",
    "ready": True,
    "backend": "cuda",
    "model": "gemma4-e2b:latest",
    "context": 512,
}
_GENERATE_OK = {
    "text": "Four.",
    "finish_reason": "eos",
    "prompt_tokens": 9,
    "generated_tokens": 2,
    "model": "gemma4-e2b:latest",
}


def _aesir_config(tmp_path: Path, det: DeterminismConfig) -> FuniConfig:
    key_file = tmp_path / "service.key"
    key_file.write_text(_KEY + "\n", encoding="utf-8")
    key_file.chmod(0o600)  # E-093 custody law: credential files are 0600
    return FuniConfig(
        runtime=FuniRuntime.AESIR,
        determinism=det,
        aesir=FuniAesirConfig(api_key_file=key_file),
    )


def _aesir_capture() -> _Capture:
    return _Capture(
        {"/health/ready": _Resp(_READY), "/v1/generate": _Resp(_GENERATE_OK)}
    )


def test_aesir_request_has_no_seed_by_default(tmp_path: Path) -> None:
    capture = _aesir_capture()
    with patch("urllib.request.urlopen", side_effect=capture):
        handle = aesir_open(_aesir_config(tmp_path, DeterminismConfig()))
        assert not isinstance(handle, Unavailable)
        reply = handle.complete("2+2?", [])
    assert reply.finish_reason is FinishReason.STOP
    body = capture.bodies[-1]
    assert "seed" not in body
    assert body["temperature"] == 0.7


def test_aesir_request_carries_native_seed_when_on(tmp_path: Path) -> None:
    capture = _aesir_capture()
    cfg = _aesir_config(tmp_path, DeterminismConfig(enabled=True, seed=7))
    with patch("urllib.request.urlopen", side_effect=capture):
        handle = aesir_open(cfg)
        assert not isinstance(handle, Unavailable)
        reply = handle.complete("2+2?", [])
    assert reply.finish_reason is FinishReason.STOP
    body = capture.bodies[-1]
    assert body["seed"] == 7
    assert body["temperature"] == 0.0
    assert body["top_p"] == 0.9  # the rest rides as configured


def test_aesir_streaming_request_carries_seed_when_on(tmp_path: Path) -> None:
    lines = [
        {"text": "Four.", "done": False},
        {
            "text": "",
            "done": True,
            "finish_reason": "eos",
            "prompt_tokens": 9,
            "generated_tokens": 2,
            "model": "gemma4-e2b:latest",
        },
    ]
    capture = _Capture(
        {"/health/ready": _Resp(_READY), "/v1/generate": _StreamResp(lines)}
    )
    cfg = _aesir_config(tmp_path, DeterminismConfig(enabled=True, seed=7))
    with patch("urllib.request.urlopen", side_effect=capture):
        handle = aesir_open(cfg)
        assert not isinstance(handle, Unavailable)
        chunks = list(handle.complete_streaming("2+2?", []))
    assert chunks[-1].finish_reason is FinishReason.STOP
    assert capture.bodies[-1]["seed"] == 7
    assert capture.bodies[-1]["stream"] is True


def test_aesir_negative_seed_is_refused_before_the_key_is_read(
    tmp_path: Path,
) -> None:
    # The key file does not even exist: determinism is judged first,
    # so the refusal names the seed, not the missing file.
    cfg = FuniConfig(
        runtime=FuniRuntime.AESIR,
        determinism=DeterminismConfig(enabled=True, seed=-3),
        aesir=FuniAesirConfig(api_key_file=tmp_path / "nope.key"),
    )
    result = aesir_open(cfg)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
    assert "seed" in (result.detail or "")


# --------------------------------------------------------------------- #
# Retrieval ranking: RRF ties break on chunk_id (extras shape)           #
# --------------------------------------------------------------------- #


def test_rrf_ties_break_on_chunk_id_not_arrival_order() -> None:
    pytest.importorskip("sqlite_vec")
    from ember.schemas.chunks import RetrievalHit
    from ember.well.brunnr.sqlite_vec.adapter import SqliteVecBrunnr

    def hit(cid: int) -> RetrievalHit:
        return RetrievalHit(
            chunk_id=cid,
            document_id=1,
            document_title="t",
            text=f"chunk {cid}",
            score=0.0,
            char_start=0,
            char_end=1,
        )

    class _Fake(SqliteVecBrunnr):
        def __init__(self, vec: list[int], fts: list[int]) -> None:
            self._vec = vec
            self._fts = fts

        def vector_search(self, qvec, k, filter=None):  # noqa: A002
            return [hit(c) for c in self._vec]

        def text_search(self, query, k, filter=None):  # noqa: A002
            return [hit(c) for c in self._fts]

    # Chunks 9 and 3 swap ranks between the two searches, so their
    # RRF scores are exactly equal. Whichever search returned a
    # chunk first, the fused order must be the same: id order.
    for vec_order, fts_order in (((9, 3), (3, 9)), ((3, 9), (9, 3))):
        fake = _Fake(list(vec_order), list(fts_order))
        hits = fake.hybrid_search((0.0,), "q", k=2)
        assert [h.chunk_id for h in hits] == [3, 9]
        assert hits[0].score == hits[1].score  # the tie itself is real


def test_vector_search_ties_break_on_chunk_id(tmp_path: Path) -> None:
    # Regression pin for the vec0 lesson: a second ORDER BY key
    # in the KNN query itself raises OperationalError, so the
    # tie-break lives in Python. Two chunks with the SAME
    # embedding have exactly equal distance; their order must
    # be chunk_id order on every run.
    pytest.importorskip("sqlite_vec")
    from ember.schemas.chunks import Chunk, Document
    from ember.schemas.config import BrunnrConfig, SqliteVecConfig
    from ember.well.brunnr.sqlite_vec import SqliteVecBrunnr
    from ember.well.brunnr.sqlite_vec import open as sv_open

    cfg = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    )
    handle = sv_open(cfg)
    assert isinstance(handle, SqliteVecBrunnr)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    handle.add_chunks(
        [
            Chunk(
                document_id=doc_id, chunk_index=i, text=f"c{i}",
                embedding=(1.0, 0.0, 0.0, 0.0),
            )
            for i in range(3)
        ]
    )
    hits = handle.vector_search((1.0, 0.0, 0.0, 0.0), k=3)
    assert [h.chunk_id for h in hits] == sorted(h.chunk_id for h in hits)
    assert len({h.score for h in hits}) == 1  # the tie itself is real
    handle.close()
