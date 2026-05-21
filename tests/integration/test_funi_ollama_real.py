"""OllamaFuni against a real local Ollama — marked ``requires_ollama``.

Skipped unless an Ollama instance is reachable at the default endpoint
and the configured model is present. Run with:

    pytest -m requires_ollama tests/integration/test_funi_ollama_real.py
"""

from __future__ import annotations

import socket
from contextlib import closing

import pytest

from ember.schemas.config import FuniConfig, FuniOllamaConfig, FuniRuntime
from ember.schemas.funi import ContextItem, ContextKind, FinishReason
from ember.spark.funi.ollama import OllamaFuni
from ember.spark.funi.ollama import open as ollama_open

pytestmark = pytest.mark.requires_ollama


def _ollama_reachable(host: str = "localhost", port: int = 11434) -> bool:
    try:
        with closing(socket.create_connection((host, port), timeout=1.0)):
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def real_handle() -> OllamaFuni:
    if not _ollama_reachable():
        pytest.skip("Ollama not reachable at localhost:11434")
    cfg = FuniConfig(
        runtime=FuniRuntime.OLLAMA,
        ollama=FuniOllamaConfig(model="phi3:mini", num_predict=64),
    )
    handle = ollama_open(cfg)
    if not isinstance(handle, OllamaFuni):
        pytest.skip(f"Ollama open returned Unavailable: {handle}")
    return handle


def test_real_complete_returns_some_text(real_handle: OllamaFuni) -> None:
    reply = real_handle.complete(
        prompt="Say the single word 'ready' and nothing else.",
        context=[
            ContextItem(
                kind=ContextKind.SYSTEM,
                text="You are a terse assistant. Reply with exactly one word.",
            )
        ],
    )
    assert reply.finish_reason in {FinishReason.STOP, FinishReason.LENGTH}
    assert reply.text.strip()


def test_real_health_returns_live_snapshot(real_handle: OllamaFuni) -> None:
    health = real_handle.health()
    assert health.last_ok is not None
    assert health.model_id == "phi3:mini"
