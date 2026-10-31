"""E-022 — the model-backend contract + conformance.

Before E-022 the Funi contract was four methods on a Protocol and
capability claims lived only in prose. These tests pin:

- the registry covers every FuniRuntime exactly once;
- the implemented backends are exactly the ones slices have shipped
  (Ollama at E-022; Aesir added at E-023, whose own conformance lives
  in test_aesir_backend_e023.py); the rest are honestly
  unimplemented — open() says Unavailable and the registry grants
  them no capabilities;
- Ollama's declared capabilities match its registry entry and the
  adapter's actual mocked-transport behaviour;
- a minimal complete()-only backend conforms via the WRAPPED
  streaming mode (the shape E-023's Aesir backend will be judged
  against if it cannot stream natively).
"""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from typing import Any
from unittest.mock import patch

import pytest

from ember.schemas.config import FuniConfig, FuniRuntime
from ember.schemas.funi import (
    BackendCapabilities,
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
from ember.spark.funi import handle as funi_handle
from ember.spark.funi.ollama import OllamaFuni
from ember.spark.funi.ollama import open as ollama_open
from ember.spark.funi.ollama.adapter import OLLAMA_CAPABILITIES

# --------------------------------------------------------------------- #
# Registry truth                                                         #
# --------------------------------------------------------------------- #


def test_registry_covers_every_runtime_exactly_once() -> None:
    registry = funi_handle.backend_registry()
    assert sorted(e.runtime for e in registry) == sorted(FuniRuntime)
    assert len({e.runtime for e in registry}) == len(registry)


# E-023: Aesir joined Ollama as an implemented backend. This list
# is the implemented set as of E-023; a future backend slice extends
# it here with its own attribution, as E-021 did for ContextKind.
_IMPLEMENTED = [FuniRuntime.OLLAMA, FuniRuntime.AESIR]


def test_implemented_backends_are_exactly_the_shipped_set() -> None:
    implemented = [e.runtime for e in funi_handle.backend_registry() if e.implemented]
    assert implemented == _IMPLEMENTED


def test_unimplemented_runtimes_have_no_capabilities() -> None:
    for entry in funi_handle.backend_registry():
        if entry.runtime in _IMPLEMENTED:
            assert entry.capabilities is not None
        else:
            assert entry.implemented is False
            assert entry.capabilities is None
            assert funi_handle.capabilities_for(entry.runtime) is None


@pytest.mark.parametrize(
    "runtime",
    [r for r in FuniRuntime if r not in _IMPLEMENTED],
)
def test_unimplemented_runtime_open_is_typed_unavailable(
    runtime: FuniRuntime,
) -> None:
    result = funi_handle.open(FuniConfig(runtime=runtime))
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.RUNTIME_NOT_INSTALLED
    assert runtime.value in (result.detail or "")


# --------------------------------------------------------------------- #
# Ollama capability truth                                                #
# --------------------------------------------------------------------- #


def test_ollama_capabilities_agree_everywhere() -> None:
    assert funi_handle.capabilities_for(FuniRuntime.OLLAMA) is OLLAMA_CAPABILITIES
    assert OllamaFuni.capabilities is OLLAMA_CAPABILITIES
    assert OLLAMA_CAPABILITIES.runtime_kind == OllamaFuni.runtime_kind


def test_ollama_capability_truth_pins() -> None:
    caps = OLLAMA_CAPABILITIES
    assert caps.streaming is StreamingMode.NATIVE
    assert caps.tool_calls is True
    # The adapter speaks the tool protocol; emitting calls is the
    # model's part (phi3:mini does not — FUNI_LOCAL_MODEL_OPTIONS).
    assert caps.tool_calls_model_dependent is True
    assert caps.token_counts is True
    # health() never reports RAM — the declaration must not claim it.
    assert caps.reports_ram_use is False
    assert caps.requires_endpoint is True
    # _messages_from_context translates every ContextKind.
    assert set(caps.context_kinds) == set(ContextKind)


def test_capabilities_are_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        OLLAMA_CAPABILITIES.tool_calls = False  # type: ignore[misc]


# --------------------------------------------------------------------- #
# Ollama conformance over a mocked transport                             #
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
    """Iterable NDJSON response for the streaming endpoint."""

    def __init__(self, lines: list[dict[str, Any]]) -> None:
        self._lines = [json.dumps(x).encode() + b"\n" for x in lines]

    def __iter__(self):
        return iter(self._lines)

    def close(self) -> None:
        return None


def _opener(routes: dict[str, Any]):
    def urlopen(request, *, timeout: float = 0.0):
        url = request.full_url
        for suffix, response in routes.items():
            if url.endswith(suffix):
                return response
        raise AssertionError(f"unexpected URL: {url}")

    return urlopen


def _ollama_config() -> FuniConfig:
    return FuniConfig(runtime=FuniRuntime.OLLAMA)


def test_ollama_handle_satisfies_protocol_and_contract() -> None:
    urlopen = _opener({"/api/version": _Resp({"version": "0.1.32"})})
    with patch("urllib.request.urlopen", side_effect=urlopen):
        handle = ollama_open(_ollama_config())
    assert isinstance(handle, OllamaFuni)
    assert isinstance(handle, funi_handle.FuniHandle)
    assert handle.capabilities is OLLAMA_CAPABILITIES
    handle.close()
    handle.close()  # close is idempotent (no persistent connection)


def test_ollama_complete_reports_token_counts_as_declared() -> None:
    urlopen = _opener(
        {
            "/api/chat": _Resp(
                {
                    "model": "phi3:mini",
                    "message": {"role": "assistant", "content": "hello"},
                    "done_reason": "stop",
                    "prompt_eval_count": 11,
                    "eval_count": 7,
                }
            )
        }
    )
    adapter = OllamaFuni(
        base_url="http://localhost:11434", model_id="phi3:mini", options={}
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        reply = adapter.complete("hi", [])
    assert isinstance(reply, FuniReply)
    assert reply.finish_reason is FinishReason.STOP
    # token_counts=True in the declaration — the reply must carry them.
    assert reply.prompt_tokens == 11
    assert reply.completion_tokens == 7


def test_ollama_streaming_is_native_and_terminates_done() -> None:
    urlopen = _opener(
        {
            "/api/chat": _StreamResp(
                [
                    {"message": {"content": "he"}, "done": False},
                    {
                        "message": {"content": "llo"},
                        "done": True,
                        "done_reason": "stop",
                        "prompt_eval_count": 3,
                        "eval_count": 2,
                    },
                ]
            )
        }
    )
    adapter = OllamaFuni(
        base_url="http://localhost:11434", model_id="phi3:mini", options={}
    )
    with patch("urllib.request.urlopen", side_effect=urlopen):
        chunks = list(adapter.complete_streaming("hi", []))
    # Native streaming: more than the single wrapped final chunk.
    assert len(chunks) == 2
    assert chunks[-1].done is True
    assert chunks[-1].finish_reason is FinishReason.STOP
    assert "".join(c.text_delta for c in chunks) == "hello"


def test_ollama_health_never_raises_and_reports_no_ram() -> None:
    def dead_urlopen(request, *, timeout: float = 0.0):
        import urllib.error

        raise urllib.error.URLError("connection refused")

    adapter = OllamaFuni(
        base_url="http://localhost:11434", model_id="phi3:mini", options={}
    )
    with patch("urllib.request.urlopen", side_effect=dead_urlopen):
        health = adapter.health()
    assert isinstance(health, FuniHealth)
    assert health.model_id == "phi3:mini"
    # reports_ram_use=False in the declaration — health must agree.
    assert health.ram_use_bytes is None


# --------------------------------------------------------------------- #
# The WRAPPED conformance shape (complete-only backends)                 #
# --------------------------------------------------------------------- #


class _CompleteOnlyBackend:
    """Minimum backend: no native streaming, wrapped per ADR 0009."""

    runtime_kind = "fake_complete_only"
    model_id = "fake-1"
    capabilities = BackendCapabilities(
        runtime_kind="fake_complete_only",
        streaming=StreamingMode.WRAPPED,
        tool_calls=False,
        token_counts=True,
    )

    def complete(self, prompt, context, tools=None) -> FuniReply:
        return FuniReply(
            text=f"echo:{prompt}",
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
            prompt_tokens=1,
            completion_tokens=2,
        )

    def complete_streaming(self, prompt, context, tools=None):
        yield from funi_handle.wrap_complete_as_stream(self, prompt, context, tools)

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id)

    def close(self) -> None:
        return None


def test_complete_only_backend_conforms_via_wrapped_streaming() -> None:
    backend = _CompleteOnlyBackend()
    assert isinstance(backend, funi_handle.FuniHandle)
    assert backend.capabilities.streaming is StreamingMode.WRAPPED
    chunks = list(backend.complete_streaming("hey", []))
    assert len(chunks) == 1
    only = chunks[0]
    assert isinstance(only, FuniStreamChunk)
    assert only.done is True
    assert only.text_delta == "echo:hey"
    assert only.finish_reason is FinishReason.STOP
    assert only.prompt_tokens == 1
    assert only.completion_tokens == 2


def test_context_items_shape_is_the_contracts_context() -> None:
    # The contract's context unit: a backend receives ContextItems,
    # never raw prompt strings stitched by the caller.
    item = ContextItem(kind=ContextKind.SYSTEM, text="be kind")
    backend = _CompleteOnlyBackend()
    reply = backend.complete("hi", [item])
    assert reply.text == "echo:hi"
