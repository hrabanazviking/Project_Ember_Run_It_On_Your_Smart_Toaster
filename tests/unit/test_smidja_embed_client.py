"""Shape and behaviour tests for the Ollama embed client.

All tests mock urllib.request.urlopen — no network. Real-Ollama tests
are deferred to integration with the ``requires_ollama`` marker.
"""

from __future__ import annotations

import json
import urllib.error
from typing import Any
from unittest.mock import patch

from ember.schemas.config import EmbeddingConfig
from ember.well.smidja.embed_client import OllamaEmbedClient


class _MockResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _MockResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _capture_request(payload: dict[str, Any]):
    """Returns (mock_factory, captured) for use with patch."""
    captured: dict[str, Any] = {}

    def factory(req, *, timeout: float = 0.0):
        captured["url"] = req.full_url
        captured["data"] = req.data
        captured["headers"] = dict(req.headers)
        captured["timeout"] = timeout
        return _MockResponse(payload)

    return factory, captured


def test_empty_input_returns_empty_list() -> None:
    client = OllamaEmbedClient()
    assert client.embed([]) == []


def test_single_batch_calls_endpoint_with_correct_shape() -> None:
    factory, captured = _capture_request(
        {"embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]}
    )
    cfg = EmbeddingConfig(model="nomic-embed-text", batch_size=4)
    client = OllamaEmbedClient(config=cfg, max_attempts=1)

    with patch("urllib.request.urlopen", side_effect=factory):
        vectors = client.embed(["one", "two"])

    assert vectors == [(0.1, 0.2, 0.3), (0.4, 0.5, 0.6)]
    sent = json.loads(captured["data"])
    assert sent == {"model": "nomic-embed-text", "input": ["one", "two"]}
    assert captured["url"] == cfg.endpoint
    assert captured["headers"]["Content-type"] == "application/json"


def test_multiple_batches_are_concatenated_in_order() -> None:
    cfg = EmbeddingConfig(batch_size=2)
    client = OllamaEmbedClient(config=cfg, max_attempts=1)

    call_count = {"n": 0}

    def factory(req, *, timeout: float = 0.0):
        call_count["n"] += 1
        payload = json.loads(req.data)
        return _MockResponse(
            {
                "embeddings": [
                    [float(call_count["n"]), float(i)]
                    for i, _ in enumerate(payload["input"])
                ]
            }
        )

    with patch("urllib.request.urlopen", side_effect=factory):
        vectors = client.embed(["a", "b", "c", "d", "e"])

    assert call_count["n"] == 3  # 2 + 2 + 1
    assert len(vectors) == 5
    # First batch: model_call=1, indices 0..1
    assert vectors[0] == (1.0, 0.0)
    assert vectors[1] == (1.0, 1.0)
    # Third batch: model_call=3, one entry
    assert vectors[4] == (3.0, 0.0)


def test_url_error_after_max_attempts_returns_none_vectors() -> None:
    def always_fail(req, *, timeout: float = 0.0):
        raise urllib.error.URLError("connection refused")

    cfg = EmbeddingConfig(batch_size=4)
    client = OllamaEmbedClient(
        config=cfg, max_attempts=2, backoff_base_s=0.0, backoff_max_s=0.0
    )

    with patch("urllib.request.urlopen", side_effect=always_fail):
        vectors = client.embed(["one", "two"])

    assert vectors == [None, None]


def test_mismatched_response_size_returns_none_vectors() -> None:
    factory, _ = _capture_request({"embeddings": [[0.1, 0.2]]})  # only 1 for 2 inputs
    client = OllamaEmbedClient(max_attempts=1)

    with patch("urllib.request.urlopen", side_effect=factory):
        vectors = client.embed(["one", "two"])

    assert vectors == [None, None]


def test_invalid_json_response_returns_none_vectors() -> None:
    class _BadResponse:
        def read(self) -> bytes:
            return b"not json at all"

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

    client = OllamaEmbedClient(max_attempts=1)

    with patch("urllib.request.urlopen", return_value=_BadResponse()):
        vectors = client.embed(["one"])

    assert vectors == [None]
