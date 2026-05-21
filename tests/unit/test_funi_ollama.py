"""Shape and behaviour tests for the Ollama Funi adapter.

All HTTP is mocked via ``urllib.request.urlopen`` — real-endpoint
coverage lives in ``tests/integration/test_funi_ollama_real.py`` and
runs only when an Ollama instance is reachable.
"""

from __future__ import annotations

import json
import urllib.error
from typing import Any
from unittest.mock import patch

from ember.schemas.config import FuniConfig, FuniOllamaConfig, FuniRuntime
from ember.schemas.funi import (
    ContextItem,
    ContextKind,
    FinishReason,
    FuniReply,
    Unavailable,
    UnavailableReason,
)
from ember.spark.funi.ollama import OllamaFuni
from ember.spark.funi.ollama import open as ollama_open

# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


class _Resp:
    def __init__(self, payload: dict[str, Any] | bytes) -> None:
        if isinstance(payload, bytes):
            self._body = payload
        else:
            self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _Resp:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _make_routing_opener(routes: dict[str, _Resp | Exception]):
    """Return a ``urlopen`` stand-in dispatching by URL path suffix."""
    calls: list[str] = []

    def urlopen(request, *, timeout: float = 0.0):
        url = request.full_url
        calls.append(url)
        for suffix, response in routes.items():
            if url.endswith(suffix):
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(f"unexpected URL: {url}")

    return urlopen, calls


def _funi_config() -> FuniConfig:
    return FuniConfig(
        runtime=FuniRuntime.OLLAMA,
        ollama=FuniOllamaConfig(
            base_url="http://localhost:11434",
            model="phi3:mini",
        ),
    )


# --------------------------------------------------------------------- #
# open()                                                                 #
# --------------------------------------------------------------------- #


def test_open_returns_adapter_when_version_probe_succeeds() -> None:
    urlopen, calls = _make_routing_opener(
        {"/api/version": _Resp({"version": "0.1.32"})}
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        result = ollama_open(_funi_config())
    assert isinstance(result, OllamaFuni)
    assert result.runtime_kind == "ollama"
    assert result.model_id == "phi3:mini"
    assert any(c.endswith("/api/version") for c in calls)


def test_open_returns_unavailable_when_endpoint_is_unreachable() -> None:
    urlopen, _ = _make_routing_opener(
        {"/api/version": urllib.error.URLError("connection refused")}
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        result = ollama_open(_funi_config())
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.ENDPOINT_UNREACHABLE
    assert "connection refused" in (result.detail or "")


def test_open_returns_unavailable_when_version_payload_is_invalid() -> None:
    urlopen, _ = _make_routing_opener({"/api/version": _Resp(b"not json")})
    with patch("urllib.request.urlopen", side_effect=urlopen):
        result = ollama_open(_funi_config())
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.UNKNOWN


# --------------------------------------------------------------------- #
# complete() — happy path                                                #
# --------------------------------------------------------------------- #


def test_complete_returns_funi_reply_with_text_and_finish_reason() -> None:
    urlopen, calls = _make_routing_opener(
        {
            "/api/version": _Resp({"version": "0.1.32"}),
            "/api/chat": _Resp(
                {
                    "model": "phi3:mini",
                    "message": {"role": "assistant", "content": "Odin is wise."},
                    "done_reason": "stop",
                    "prompt_eval_count": 42,
                    "eval_count": 7,
                }
            ),
        }
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        reply = handle.complete(
            prompt="who is Odin?",
            context=[ContextItem(kind=ContextKind.SYSTEM, text="you are Ember")],
        )

    assert isinstance(reply, FuniReply)
    assert reply.text == "Odin is wise."
    assert reply.finish_reason is FinishReason.STOP
    assert reply.model_id == "phi3:mini"
    assert reply.prompt_tokens == 42
    assert reply.completion_tokens == 7
    assert any(c.endswith("/api/chat") for c in calls)


def test_complete_payload_includes_messages_in_canonical_shape() -> None:
    captured: dict[str, Any] = {}

    def urlopen(request, *, timeout: float = 0.0):
        if request.full_url.endswith("/api/version"):
            return _Resp({"version": "0.1.32"})
        if request.full_url.endswith("/api/chat"):
            captured["payload"] = json.loads(request.data)
            return _Resp(
                {
                    "model": "phi3:mini",
                    "message": {"role": "assistant", "content": "ok"},
                    "done_reason": "stop",
                }
            )
        raise AssertionError(request.full_url)

    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        handle.complete(
            prompt="who?",
            context=[
                ContextItem(kind=ContextKind.SYSTEM, text="be honest"),
                ContextItem(kind=ContextKind.CHUNK, text="Odin is wise"),
            ],
        )

    payload = captured["payload"]
    assert payload["model"] == "phi3:mini"
    assert payload["stream"] is False
    roles = [m["role"] for m in payload["messages"]]
    # system (honesty) + system (chunk) + user (operator).
    assert roles == ["system", "system", "user"]
    assert payload["messages"][-1]["content"] == "who?"


def test_complete_finish_reason_length_maps_through() -> None:
    urlopen, _ = _make_routing_opener(
        {
            "/api/version": _Resp({"version": "0.1.32"}),
            "/api/chat": _Resp(
                {
                    "model": "phi3:mini",
                    "message": {"role": "assistant", "content": "..."},
                    "done_reason": "length",
                }
            ),
        }
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        reply = handle.complete("hi", context=[])
    assert reply.finish_reason is FinishReason.LENGTH


# --------------------------------------------------------------------- #
# complete() — failure folding                                           #
# --------------------------------------------------------------------- #


def test_complete_returns_error_reply_when_endpoint_dies_mid_call() -> None:
    routes: dict[str, _Resp | Exception] = {
        "/api/version": _Resp({"version": "0.1.32"}),
    }
    urlopen, _ = _make_routing_opener(routes)
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)

    # Now flip the chat route to a failure for the next call.
    routes["/api/chat"] = urllib.error.URLError("conn refused mid-turn")
    urlopen2, _ = _make_routing_opener(routes)
    with patch("urllib.request.urlopen", side_effect=urlopen2):
        reply = handle.complete("hi", context=[])

    assert reply.finish_reason is FinishReason.ERROR
    assert "unreachable" in reply.text.lower() or "conn refused" in reply.text.lower()


def test_complete_returns_error_reply_when_response_lacks_message() -> None:
    urlopen, _ = _make_routing_opener(
        {
            "/api/version": _Resp({"version": "0.1.32"}),
            "/api/chat": _Resp({"model": "phi3:mini", "done_reason": "stop"}),
        }
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        reply = handle.complete("hi", context=[])
    assert reply.finish_reason is FinishReason.ERROR
    assert reply.text  # operator-readable, non-empty


def test_complete_returns_error_reply_when_body_is_not_json() -> None:
    urlopen, _ = _make_routing_opener(
        {
            "/api/version": _Resp({"version": "0.1.32"}),
            "/api/chat": _Resp(b"definitely not json"),
        }
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        reply = handle.complete("hi", context=[])
    assert reply.finish_reason is FinishReason.ERROR


def test_complete_returns_error_reply_when_ollama_reports_error_payload() -> None:
    urlopen, _ = _make_routing_opener(
        {
            "/api/version": _Resp({"version": "0.1.32"}),
            "/api/chat": _Resp({"error": "model 'phi3:mini' not found"}),
        }
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        reply = handle.complete("hi", context=[])
    assert reply.finish_reason is FinishReason.ERROR
    assert "model" in reply.text.lower()


def test_complete_refuses_tool_calls_cleanly() -> None:
    urlopen, _ = _make_routing_opener(
        {"/api/version": _Resp({"version": "0.1.32"})}
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        reply = handle.complete("hi", context=[], tools=["search_well"])
    assert reply.finish_reason is FinishReason.ERROR


# --------------------------------------------------------------------- #
# health()                                                               #
# --------------------------------------------------------------------- #


def test_health_returns_live_snapshot_after_successful_probe() -> None:
    urlopen, _ = _make_routing_opener(
        {"/api/version": _Resp({"version": "0.1.32"})}
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        health = handle.health()
    assert health.model_id == "phi3:mini"
    assert health.last_ok is not None


def test_health_falls_back_to_previous_last_ok_when_probe_fails() -> None:
    routes: dict[str, _Resp | Exception] = {
        "/api/version": _Resp({"version": "0.1.32"}),
    }
    urlopen, _ = _make_routing_opener(routes)
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        # Flip the route to a failure before the health probe.
    routes["/api/version"] = urllib.error.URLError("now broken")
    urlopen2, _ = _make_routing_opener(routes)
    with patch("urllib.request.urlopen", side_effect=urlopen2):
        health = handle.health()
    # last_ok was set at open(); a failing health probe doesn't clobber it.
    assert health.last_ok is not None


def test_open_wrong_runtime_returns_unavailable() -> None:
    cfg = FuniConfig(runtime=FuniRuntime.LMSTUDIO)
    result = ollama_open(cfg)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.CONFIG_INVALID
