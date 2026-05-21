"""Streaming-side behaviour tests for OllamaFuni.

All HTTP is mocked. Real Ollama coverage stays in
``tests/integration/test_funi_ollama_real.py`` (already gated on
``requires_ollama``).
"""

from __future__ import annotations

import json
import urllib.error
from typing import Any
from unittest.mock import patch

from ember.schemas.config import FuniConfig, FuniOllamaConfig, FuniRuntime
from ember.schemas.funi import ContextItem, ContextKind, FinishReason
from ember.schemas.stream import FuniStreamChunk
from ember.spark.funi import handle as funi_handle
from ember.spark.funi.ollama import OllamaFuni
from ember.spark.funi.ollama import open as ollama_open

# --------------------------------------------------------------------- #
# Test doubles                                                          #
# --------------------------------------------------------------------- #


class _MockStreamingResp:
    """File-like response that iterates over preset NDJSON lines."""

    def __init__(self, lines: list[dict[str, Any]]) -> None:
        self._payload = [
            (json.dumps(line) + "\n").encode("utf-8") for line in lines
        ]

    def __iter__(self):
        return iter(self._payload)

    def read(self) -> bytes:
        return b"".join(self._payload)

    def close(self) -> None:
        return None

    def __enter__(self) -> _MockStreamingResp:
        return self

    def __exit__(self, *_: object) -> None:
        return None


class _MockJsonResp:
    """File-like response that returns one JSON blob (for /api/version probe)."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def close(self) -> None:
        return None

    def __enter__(self) -> _MockJsonResp:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _route(routes: dict[str, Any]):
    def urlopen(request, *, timeout: float = 0.0):
        url = request.full_url
        for suffix, response in routes.items():
            if url.endswith(suffix):
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(f"unexpected URL: {url}")

    return urlopen


def _funi_config() -> FuniConfig:
    return FuniConfig(
        runtime=FuniRuntime.OLLAMA,
        ollama=FuniOllamaConfig(model="phi3:mini"),
    )


def _opened(routes: dict[str, Any]) -> OllamaFuni:
    """Open an OllamaFuni against the routed responses."""
    with patch("urllib.request.urlopen", side_effect=_route(routes)):
        handle = ollama_open(_funi_config())
    assert isinstance(handle, OllamaFuni)
    return handle


# --------------------------------------------------------------------- #
# Happy path                                                            #
# --------------------------------------------------------------------- #


def test_streaming_yields_one_chunk_per_ndjson_line() -> None:
    """Three text chunks + one final done chunk."""
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})
    stream_resp = _MockStreamingResp(
        [
            {
                "model": "phi3:mini",
                "message": {"role": "assistant", "content": "Hello"},
                "done": False,
            },
            {
                "model": "phi3:mini",
                "message": {"role": "assistant", "content": " world"},
                "done": False,
            },
            {
                "model": "phi3:mini",
                "message": {"role": "assistant", "content": "!"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 12,
                "eval_count": 3,
            },
        ]
    )

    with patch("urllib.request.urlopen", return_value=stream_resp):
        chunks = list(
            handle.complete_streaming(
                "say hi",
                context=[ContextItem(kind=ContextKind.SYSTEM, text="be brief")],
            )
        )

    assert len(chunks) == 3
    assert all(isinstance(c, FuniStreamChunk) for c in chunks)
    assert "".join(c.text_delta for c in chunks) == "Hello world!"

    # Only the last chunk carries done + totals.
    assert [c.done for c in chunks] == [False, False, True]
    assert chunks[-1].finish_reason is FinishReason.STOP
    assert chunks[-1].prompt_tokens == 12
    assert chunks[-1].completion_tokens == 3


def test_streaming_payload_sets_stream_true() -> None:
    captured: dict[str, Any] = {}

    def urlopen(request, *, timeout: float = 0.0):
        if request.full_url.endswith("/api/version"):
            return _MockJsonResp({"version": "0.1.32"})
        captured["payload"] = json.loads(request.data)
        return _MockStreamingResp(
            [
                {
                    "message": {"role": "assistant", "content": "ok"},
                    "done": True,
                    "done_reason": "stop",
                }
            ]
        )

    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        list(handle.complete_streaming("hi", context=[]))

    assert captured["payload"]["stream"] is True


# --------------------------------------------------------------------- #
# Finish reasons                                                        #
# --------------------------------------------------------------------- #


def test_streaming_done_reason_length_maps_through() -> None:
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})
    stream_resp = _MockStreamingResp(
        [
            {
                "message": {"role": "assistant", "content": "..."},
                "done": True,
                "done_reason": "length",
            }
        ]
    )
    with patch("urllib.request.urlopen", return_value=stream_resp):
        chunks = list(handle.complete_streaming("hi", context=[]))
    assert chunks[-1].finish_reason is FinishReason.LENGTH


# --------------------------------------------------------------------- #
# Failure folding                                                       #
# --------------------------------------------------------------------- #


def test_streaming_url_error_at_open_yields_single_error_chunk() -> None:
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})

    def fail_urlopen(*_args, **_kw):
        raise urllib.error.URLError("connection refused mid-stream")

    with patch("urllib.request.urlopen", side_effect=fail_urlopen):
        chunks = list(handle.complete_streaming("hi", context=[]))

    assert len(chunks) == 1
    assert chunks[0].done is True
    assert chunks[0].finish_reason is FinishReason.ERROR
    assert "connection refused" in chunks[0].text_delta


def test_streaming_non_json_line_yields_error_chunk_and_terminates() -> None:
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})

    class _BadLineResp:
        def __iter__(self):
            return iter(
                [
                    json.dumps(
                        {
                            "message": {"role": "assistant", "content": "Hel"},
                            "done": False,
                        }
                    ).encode("utf-8")
                    + b"\n",
                    b"definitely not json\n",
                    json.dumps(
                        {
                            "message": {"role": "assistant", "content": "lo"},
                            "done": True,
                            "done_reason": "stop",
                        }
                    ).encode("utf-8")
                    + b"\n",
                ]
            )

        def close(self):
            return None

    with patch("urllib.request.urlopen", return_value=_BadLineResp()):
        chunks = list(handle.complete_streaming("hi", context=[]))

    # First (real) chunk + the error chunk that terminates the stream.
    assert chunks[0].text_delta == "Hel"
    assert chunks[-1].finish_reason is FinishReason.ERROR
    assert chunks[-1].done is True


def test_streaming_error_payload_yields_error_chunk() -> None:
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})
    stream_resp = _MockStreamingResp(
        [{"error": "model 'phi3:mini' not found"}]
    )
    with patch("urllib.request.urlopen", return_value=stream_resp):
        chunks = list(handle.complete_streaming("hi", context=[]))

    assert chunks[-1].finish_reason is FinishReason.ERROR
    assert "model" in chunks[-1].text_delta.lower()


def test_streaming_ends_without_done_yields_synthetic_error() -> None:
    """If Ollama hangs up before sending done=true, we emit a final ERROR."""
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})
    stream_resp = _MockStreamingResp(
        [
            {
                "message": {"role": "assistant", "content": "partial"},
                "done": False,
            }
        ]
    )
    with patch("urllib.request.urlopen", return_value=stream_resp):
        chunks = list(handle.complete_streaming("hi", context=[]))

    assert chunks[0].text_delta == "partial"
    assert chunks[-1].done is True
    assert chunks[-1].finish_reason is FinishReason.ERROR
    assert "without done" in chunks[-1].text_delta.lower()


def test_streaming_tool_request_refuses_immediately() -> None:
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})
    # Note: no urlopen patch here — we should refuse BEFORE making the call.
    chunks = list(
        handle.complete_streaming("hi", context=[], tools=["search_well"])
    )
    assert len(chunks) == 1
    assert chunks[0].done is True
    assert chunks[0].finish_reason is FinishReason.ERROR


# --------------------------------------------------------------------- #
# wrap_complete_as_stream — the default for non-streaming runtimes      #
# --------------------------------------------------------------------- #


def test_wrap_complete_as_stream_yields_one_final_chunk() -> None:
    """Adapters that can't stream natively use this helper."""
    handle = _opened({"/api/version": _MockJsonResp({"version": "0.1.32"})})
    chat_resp = _MockJsonResp(
        {
            "model": "phi3:mini",
            "message": {"role": "assistant", "content": "wrapped reply"},
            "done_reason": "stop",
            "prompt_eval_count": 5,
            "eval_count": 7,
        }
    )

    with patch("urllib.request.urlopen", return_value=chat_resp):
        chunks = list(
            funi_handle.wrap_complete_as_stream(handle, "hi", context=[])
        )

    assert len(chunks) == 1
    assert chunks[0].done is True
    assert chunks[0].text_delta == "wrapped reply"
    assert chunks[0].finish_reason is FinishReason.STOP
    assert chunks[0].prompt_tokens == 5
    assert chunks[0].completion_tokens == 7
