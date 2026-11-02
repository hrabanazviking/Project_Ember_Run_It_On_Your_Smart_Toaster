"""E-023 — the Aesir backend, bound under E-022's contract.

Project Aesir's native service (loopback :18434, bearer key file,
``POST /v1/generate`` with prompt+system only, ``GET /health/ready``
as the probe) is Ember's second implemented Funi backend. These
tests pin, over a mocked transport (no real Aesir service is claimed
or required):

- registry/capability truth: Aesir implemented, native streaming,
  **no tool calls** (the native route rejects a tools field), token
  counts from prompt/generated counters, no RAM reporting, endpoint
  required, every ContextKind translated;
- key custody: the config carries the key file's *path* only; a
  missing/malformed key file is a typed Unavailable whose detail
  never contains key material; the key is sent as the Authorization
  header and nowhere else;
- open(): unreachable → ENDPOINT_UNREACHABLE, rejected key (401) →
  CONFIG_INVALID, not-ready (503 / ready:false) → NOT_LOADED,
  expected-model mismatch → NOT_LOADED, success names the resident
  model the probe reports;
- complete(): context flattened exactly as the native contract
  takes it (SYSTEM+SUMMARY → system; EPISODE/CHUNK/TOOL_REPLY →
  prompt text), tools refused as an ERROR reply (never silently
  dropped, never sent), finish reasons mapped (eos→STOP,
  timeout→LENGTH), token counters mapped, HTTP/native errors folded
  into ERROR replies;
- streaming: NDJSON pieces + counted terminal record; EOF without a
  terminal record is an ERROR chunk, never a success;
- health() never raises and reports no RAM;
- the config plumbing: defaults + TOML loader coercion for
  ``funi.aesir``.
"""

from __future__ import annotations

import io
import json
import urllib.error
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ember.config import load_ember_config
from ember.schemas.config import FuniAesirConfig, FuniConfig, FuniRuntime
from ember.schemas.funi import (
    ContextItem,
    ContextKind,
    FinishReason,
    FuniHealth,
    FuniReply,
    StreamingMode,
    Unavailable,
    UnavailableReason,
)
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.tool import ToolDescriptor, ToolParameter, ToolParameterKind
from ember.spark.funi import handle as funi_handle
from ember.spark.funi.aesir import AesirFuni
from ember.spark.funi.aesir import open as aesir_open
from ember.spark.funi.aesir.adapter import AESIR_CAPABILITIES

# A synthetic key in Aesir's grammar (32..256 of [A-Za-z0-9_-]).
_KEY = "testkey-" + "a" * 32


def _write_key(tmp_path: Path, content: str = _KEY + "\n") -> Path:
    key_file = tmp_path / "service.key"
    key_file.write_text(content, encoding="utf-8")
    # E-093 custody law: a credential file must be mode 0600 or
    # the adapter refuses it before reading.
    key_file.chmod(0o600)
    return key_file


def _aesir_config(tmp_path: Path, **overrides: Any) -> FuniConfig:
    aesir = FuniAesirConfig(api_key_file=_write_key(tmp_path), **overrides)
    return FuniConfig(runtime=FuniRuntime.AESIR, aesir=aesir)


def _adapter(model_id: str = "gemma4-e2b:latest") -> AesirFuni:
    return AesirFuni(
        base_url="http://127.0.0.1:18434",
        model_id=model_id,
        api_key=_KEY,
        options={"temperature": 0.7, "top_p": 0.9, "max_tokens": 256},
    )


# --------------------------------------------------------------------- #
# Transport fakes                                                        #
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
    """urlopen fake: records requests, routes by URL suffix."""

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


_READY = {
    "schema_version": 1,
    "status": "ready",
    "ready": True,
    "backend": "cuda",
    "model": "gemma4-e2b:latest",
    "context": 512,
}


def _http_error(code: int, body: dict[str, Any] | bytes = b"") -> urllib.error.HTTPError:
    raw = body if isinstance(body, bytes) else json.dumps(body).encode()
    return urllib.error.HTTPError(
        url="http://127.0.0.1:18434", code=code, msg="err", hdrs=None, fp=io.BytesIO(raw)
    )


# --------------------------------------------------------------------- #
# Registry + capability truth                                            #
# --------------------------------------------------------------------- #


def test_aesir_is_registered_implemented_with_capabilities() -> None:
    assert funi_handle.capabilities_for(FuniRuntime.AESIR) is AESIR_CAPABILITIES
    entry = next(
        e for e in funi_handle.backend_registry() if e.runtime is FuniRuntime.AESIR
    )
    assert entry.implemented is True
    assert entry.capabilities is AESIR_CAPABILITIES
    assert AesirFuni.capabilities is AESIR_CAPABILITIES
    assert AESIR_CAPABILITIES.runtime_kind == AesirFuni.runtime_kind


def test_aesir_capability_truth_pins() -> None:
    caps = AESIR_CAPABILITIES
    assert caps.streaming is StreamingMode.NATIVE
    # The native route accepts no tools field at all.
    assert caps.tool_calls is False
    assert caps.tool_calls_model_dependent is False
    assert caps.token_counts is True
    assert caps.reports_ram_use is False
    assert caps.requires_endpoint is True
    assert set(caps.context_kinds) == set(ContextKind)


def test_aesir_capabilities_are_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        AESIR_CAPABILITIES.tool_calls = True  # type: ignore[misc]


# --------------------------------------------------------------------- #
# Config plumbing                                                        #
# --------------------------------------------------------------------- #


def test_aesir_config_defaults_match_the_native_service() -> None:
    cfg = FuniAesirConfig()
    assert cfg.base_url == "http://127.0.0.1:18434"
    assert cfg.model == ""  # accept the resident model the probe names
    assert cfg.api_key_file == Path("~/.config/aesir/service.key")
    # The service's own default reply ceiling; Ember must not promise
    # more than the service grants by default.
    assert cfg.max_tokens == 256
    assert cfg.timeout_ms is None
    assert FuniConfig().aesir == cfg


def test_aesir_config_loads_through_the_toml_loader(tmp_path: Path) -> None:
    toml = tmp_path / "ember.toml"
    toml.write_text(
        "[funi]\nruntime = \"aesir\"\n\n[funi.aesir]\n"
        'model = "gemma4-e2b:latest"\nmax_tokens = 128\n',
        encoding="utf-8",
    )
    cfg = load_ember_config(file_override=toml, skip_env=True)
    assert cfg.funi.runtime is FuniRuntime.AESIR
    assert cfg.funi.aesir.model == "gemma4-e2b:latest"
    assert cfg.funi.aesir.max_tokens == 128
    assert cfg.funi.aesir.base_url == "http://127.0.0.1:18434"


# --------------------------------------------------------------------- #
# Key custody + open()                                                   #
# --------------------------------------------------------------------- #


def test_open_missing_key_file_is_config_invalid(tmp_path: Path) -> None:
    cfg = FuniConfig(
        runtime=FuniRuntime.AESIR,
        aesir=FuniAesirConfig(api_key_file=tmp_path / "nope.key"),
    )
    result = aesir_open(cfg)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
    assert "nope.key" in (result.detail or "")


def test_open_malformed_key_never_echoes_key_material(tmp_path: Path) -> None:
    bad = "short-secret"
    cfg = FuniConfig(
        runtime=FuniRuntime.AESIR,
        aesir=FuniAesirConfig(api_key_file=_write_key(tmp_path, bad + "\n")),
    )
    result = aesir_open(cfg)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
    assert bad not in (result.detail or "")


def test_open_unreachable_endpoint(tmp_path: Path) -> None:
    capture = _Capture({"/health/ready": urllib.error.URLError("refused")})
    with patch("urllib.request.urlopen", side_effect=capture):
        result = aesir_open(_aesir_config(tmp_path))
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.ENDPOINT_UNREACHABLE


def test_open_rejected_key_is_config_invalid(tmp_path: Path) -> None:
    capture = _Capture({"/health/ready": _http_error(401)})
    with patch("urllib.request.urlopen", side_effect=capture):
        result = aesir_open(_aesir_config(tmp_path))
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
    assert _KEY not in (result.detail or "")


def test_open_not_ready_is_not_loaded(tmp_path: Path) -> None:
    capture = _Capture({"/health/ready": _http_error(503)})
    with patch("urllib.request.urlopen", side_effect=capture):
        result = aesir_open(_aesir_config(tmp_path))
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.NOT_LOADED


def test_open_model_mismatch_is_not_loaded(tmp_path: Path) -> None:
    capture = _Capture({"/health/ready": _Resp(_READY)})
    with patch("urllib.request.urlopen", side_effect=capture):
        result = aesir_open(_aesir_config(tmp_path, model="other-model:latest"))
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.NOT_LOADED
    assert "gemma4-e2b:latest" in (result.detail or "")


def test_open_success_names_resident_model_and_sends_key_as_header(
    tmp_path: Path,
) -> None:
    capture = _Capture({"/health/ready": _Resp(_READY)})
    with patch("urllib.request.urlopen", side_effect=capture):
        result = aesir_open(_aesir_config(tmp_path))
    assert isinstance(result, AesirFuni)
    assert isinstance(result, funi_handle.FuniHandle)
    assert result.model_id == "gemma4-e2b:latest"
    assert result.capabilities is AESIR_CAPABILITIES
    # The key travelled exactly once: as the Authorization header of
    # the probe, never in a URL or body.
    probe = capture.requests[0]
    assert probe.get_header("Authorization") == f"Bearer {_KEY}"
    assert _KEY not in probe.full_url
    result.close()
    result.close()  # idempotent


def test_handle_open_dispatches_to_aesir(tmp_path: Path) -> None:
    capture = _Capture({"/health/ready": _Resp(_READY)})
    with patch("urllib.request.urlopen", side_effect=capture):
        result = funi_handle.open(_aesir_config(tmp_path))
    assert isinstance(result, AesirFuni)


# --------------------------------------------------------------------- #
# complete()                                                             #
# --------------------------------------------------------------------- #


def _generate_ok(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "text": "Four.",
        "finish_reason": "eos",
        "prompt_tokens": 9,
        "generated_tokens": 2,
        "context_used": 11,
        "backend": "cuda",
        "cpu_offload": 0,
        "model": "gemma4-e2b:latest",
    }
    payload.update(overrides)
    return payload


def test_complete_maps_reply_and_token_counts() -> None:
    capture = _Capture({"/v1/generate": _Resp(_generate_ok())})
    with patch("urllib.request.urlopen", side_effect=capture):
        reply = _adapter().complete("What is two plus two?", [])
    assert isinstance(reply, FuniReply)
    assert reply.text == "Four."
    assert reply.finish_reason is FinishReason.STOP  # eos -> STOP
    assert reply.prompt_tokens == 9
    assert reply.completion_tokens == 2  # generated_tokens mapped
    assert reply.model_id == "gemma4-e2b:latest"
    body = capture.bodies[0]
    assert body["prompt"] == "What is two plus two?"
    assert body["stream"] is False
    assert body["max_tokens"] == 256
    assert "model" not in body  # the native route names no model
    assert "tools" not in body
    assert capture.requests[0].get_header("Authorization") == f"Bearer {_KEY}"


def test_complete_flattens_context_into_system_and_prompt() -> None:
    context = [
        ContextItem(kind=ContextKind.SYSTEM, text="You are Ember."),
        ContextItem(kind=ContextKind.SUMMARY, text="Earlier: greetings."),
        ContextItem(
            kind=ContextKind.EPISODE,
            text="Past turn:\nOperator: hi\nEmber: hello",
        ),
        ContextItem(kind=ContextKind.CHUNK, text="From Notes:\nthe sky fact"),
        ContextItem(
            kind=ContextKind.TOOL_REPLY,
            text="result text",
            metadata={"tool_name": "search_well"},
        ),
    ]
    capture = _Capture({"/v1/generate": _Resp(_generate_ok())})
    with patch("urllib.request.urlopen", side_effect=capture):
        _adapter().complete("and now?", context)
    body = capture.bodies[0]
    assert body["system"] == "You are Ember.\n\nEarlier: greetings."
    prompt = body["prompt"]
    assert "Past turn:\nOperator: hi\nEmber: hello" in prompt
    assert "From Notes:\nthe sky fact" in prompt
    # A tool reply rides as labelled text — no tool protocol exists
    # on this route, and none is pretended.
    assert "Tool result (search_well):\nresult text" in prompt
    assert prompt.endswith("and now?")


def test_complete_timeout_finish_reads_as_length() -> None:
    capture = _Capture(
        {"/v1/generate": _Resp(_generate_ok(text="partial", finish_reason="timeout"))}
    )
    with patch("urllib.request.urlopen", side_effect=capture):
        reply = _adapter().complete("long answer please", [])
    assert reply.text == "partial"
    assert reply.finish_reason is FinishReason.LENGTH


def test_complete_with_tools_is_refused_not_dropped() -> None:
    tool = ToolDescriptor(
        name="search_well",
        description="Search the well",
        parameters_schema={
            "query": ToolParameter(
                kind=ToolParameterKind.STRING, description="q", required=True
            )
        },
    )
    capture = _Capture({"/v1/generate": _Resp(_generate_ok())})
    with patch("urllib.request.urlopen", side_effect=capture):
        reply = _adapter().complete("hi", [], tools=[tool])
    assert reply.finish_reason is FinishReason.ERROR
    assert "does not support tool calls" in reply.text
    assert capture.requests == []  # nothing was sent to the service


def test_complete_empty_prompt_is_an_error_without_a_call() -> None:
    capture = _Capture({"/v1/generate": _Resp(_generate_ok())})
    with patch("urllib.request.urlopen", side_effect=capture):
        reply = _adapter().complete("", [])
    assert reply.finish_reason is FinishReason.ERROR
    assert capture.requests == []


def test_complete_http_error_folds_into_error_reply() -> None:
    err = _http_error(422, {"error": {"code": 422, "message": "context too large"}})
    capture = _Capture({"/v1/generate": err})
    with patch("urllib.request.urlopen", side_effect=capture):
        reply = _adapter().complete("hi", [])
    assert reply.finish_reason is FinishReason.ERROR
    assert "422" in reply.text and "context too large" in reply.text
    assert _KEY not in reply.text


def test_complete_unreachable_folds_into_error_reply() -> None:
    capture = _Capture({"/v1/generate": urllib.error.URLError("refused")})
    with patch("urllib.request.urlopen", side_effect=capture):
        reply = _adapter().complete("hi", [])
    assert reply.finish_reason is FinishReason.ERROR
    assert "unreachable" in reply.text


# --------------------------------------------------------------------- #
# complete_streaming()                                                   #
# --------------------------------------------------------------------- #


def test_streaming_is_native_and_terminates_with_counts() -> None:
    lines = [
        {"text": "Fo", "done": False},
        {"text": "ur.", "done": False},
        {
            "text": "",
            "done": True,
            "finish_reason": "eos",
            "prompt_tokens": 9,
            "generated_tokens": 2,
            "model": "gemma4-e2b:latest",
        },
    ]
    capture = _Capture({"/v1/generate": _StreamResp(lines)})
    with patch("urllib.request.urlopen", side_effect=capture):
        chunks = list(_adapter().complete_streaming("2+2?", []))
    assert len(chunks) == 3  # native: more than the wrapped single chunk
    assert "".join(c.text_delta for c in chunks) == "Four."
    last = chunks[-1]
    assert isinstance(last, FuniStreamChunk)
    assert last.done is True
    assert last.finish_reason is FinishReason.STOP
    assert last.prompt_tokens == 9
    assert last.completion_tokens == 2
    assert capture.bodies[0]["stream"] is True


def test_streaming_without_terminal_record_is_an_error() -> None:
    lines = [{"text": "Fo", "done": False}]
    capture = _Capture({"/v1/generate": _StreamResp(lines)})
    with patch("urllib.request.urlopen", side_effect=capture):
        chunks = list(_adapter().complete_streaming("hi", []))
    assert chunks[-1].done is True
    assert chunks[-1].finish_reason is FinishReason.ERROR
    assert "terminal record" in chunks[-1].text_delta


def test_streaming_error_line_folds_into_error_chunk() -> None:
    lines = [{"error": {"code": 500, "message": "execution failed"}}]
    capture = _Capture({"/v1/generate": _StreamResp(lines)})
    with patch("urllib.request.urlopen", side_effect=capture):
        chunks = list(_adapter().complete_streaming("hi", []))
    assert len(chunks) == 1
    assert chunks[0].finish_reason is FinishReason.ERROR
    assert "execution failed" in chunks[0].text_delta


def test_streaming_with_tools_is_refused() -> None:
    tool = ToolDescriptor(
        name="search_well", description="Search", parameters_schema={}
    )
    chunks = list(_adapter().complete_streaming("hi", [], tools=[tool]))
    assert len(chunks) == 1
    assert chunks[0].finish_reason is FinishReason.ERROR
    assert "does not support tool calls" in chunks[0].text_delta


# --------------------------------------------------------------------- #
# health()                                                               #
# --------------------------------------------------------------------- #


def test_health_ready_reports_model_and_no_ram() -> None:
    capture = _Capture({"/health/ready": _Resp(_READY)})
    with patch("urllib.request.urlopen", side_effect=capture):
        health = _adapter(model_id="").health()
    assert isinstance(health, FuniHealth)
    assert health.model_id == "gemma4-e2b:latest"
    assert health.ram_use_bytes is None  # reports_ram_use=False must agree
    assert health.last_ok is not None


def test_health_dead_service_never_raises_and_reports_no_ram() -> None:
    def dead(request, *, timeout: float = 0.0):
        raise urllib.error.URLError("connection refused")

    with patch("urllib.request.urlopen", side_effect=dead):
        health = _adapter().health()
    assert health.model_id == "gemma4-e2b:latest"
    assert health.ram_use_bytes is None
    assert health.last_ok is None
