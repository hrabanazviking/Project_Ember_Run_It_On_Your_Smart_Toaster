"""Ollama embedding client — stdlib urllib only.

No httpx dependency in the first slice, honouring the Vow of Smallness.
Posts to ``POST {endpoint}`` with ``{"model": ..., "input": [...]}``
and reads back ``{"embeddings": [[...], [...], ...]}`` per the Ollama
``/api/embed`` contract.

Batching, exponential backoff, and per-chunk failure reporting per
``docs/adapters/SMIDJA_INGEST_PATTERNS.md`` §4.
"""

from __future__ import annotations

import json
import logging
import math
import time
import urllib.error
import urllib.request
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from ember.schemas.config import EmbeddingConfig
from ember.schemas.errors import IngestError

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_S = 60.0


@dataclass(frozen=True, slots=True)
class EmbedResult:
    """One batch's embedding result. Failed entries have ``vector=None``."""

    texts: tuple[str, ...]
    vectors: tuple[tuple[float, ...] | None, ...]
    error: str | None = None


class OllamaEmbedClient:
    """Embeds text via Ollama's ``/api/embed`` endpoint.

    Designed to be called from Smiðja's orchestrator. A failed batch
    does not raise; it returns an :class:`EmbedResult` with all vectors
    set to ``None`` and ``error`` populated. Smiðja decides what to do
    with the per-chunk failure (typically: mark in the journal, skip
    the chunk, continue the job).
    """

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
        *,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
        max_attempts: int = 4,
        backoff_base_s: float = 1.0,
        backoff_max_s: float = 30.0,
    ) -> None:
        self._config = config or EmbeddingConfig()
        self._timeout_s = timeout_s
        self._max_attempts = max_attempts
        self._backoff_base_s = backoff_base_s
        self._backoff_max_s = backoff_max_s

    def embed(self, texts: Sequence[str]) -> list[tuple[float, ...] | None]:
        """Embed ``texts`` and return one vector per input.

        Failed batches contribute ``None`` for each text in the batch.
        """
        if not texts:
            return []

        out: list[tuple[float, ...] | None] = []
        for batch in self._batched(texts):
            result = self._embed_batch(list(batch))
            out.extend(result.vectors)
        return out

    def _batched(self, texts: Sequence[str]) -> Iterator[tuple[str, ...]]:
        size = self._config.batch_size
        for i in range(0, len(texts), size):
            yield tuple(texts[i : i + size])

    def _embed_batch(self, batch: list[str]) -> EmbedResult:
        payload = json.dumps(
            {"model": self._config.model, "input": batch}
        ).encode("utf-8")

        for attempt in range(1, self._max_attempts + 1):
            try:
                request = urllib.request.Request(
                    url=self._config.endpoint,
                    data=payload,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(
                    request, timeout=self._timeout_s
                ) as response:
                    body = response.read()
                parsed = json.loads(body)
            except urllib.error.URLError as exc:
                if attempt >= self._max_attempts:
                    return EmbedResult(
                        texts=tuple(batch),
                        vectors=tuple([None] * len(batch)),
                        error=f"after {attempt} attempts: {exc}",
                    )
                self._backoff(attempt)
                continue
            except json.JSONDecodeError as exc:
                return EmbedResult(
                    texts=tuple(batch),
                    vectors=tuple([None] * len(batch)),
                    error=f"invalid JSON from endpoint: {exc}",
                )

            vectors = parsed.get("embeddings")
            if not isinstance(vectors, list) or len(vectors) != len(batch):
                returned = (
                    len(vectors) if isinstance(vectors, list) else type(vectors).__name__
                )
                return EmbedResult(
                    texts=tuple(batch),
                    vectors=tuple([None] * len(batch)),
                    error=f"endpoint returned {returned} embeddings for batch of {len(batch)}",
                )

            try:
                coerced = tuple(
                    _coerce_vector(v, expected_dim=None) for v in vectors
                )
            except (ValueError, TypeError) as exc:
                # Malformed scalar inside a vector — Ollama can return
                # stringified floats, ``None`` entries, or non-finite
                # values when an upstream model misbehaves. Return the
                # batch as all-None so the journal can record the
                # failure and the orchestrator can skip these chunks
                # rather than corrupting the Well with NaN embeddings.
                return EmbedResult(
                    texts=tuple(batch),
                    vectors=tuple([None] * len(batch)),
                    error=f"endpoint returned malformed vector data: {exc}",
                )
            return EmbedResult(
                texts=tuple(batch),
                vectors=coerced,
                error=None,
            )

        # Defensive — loop above always returns or continues.
        raise IngestError("embed_batch loop exited without returning")

    def _backoff(self, attempt: int) -> None:
        delay = min(self._backoff_base_s * (2 ** (attempt - 1)), self._backoff_max_s)
        logger.debug("embed batch failed, sleeping %.1fs before attempt %d", delay, attempt + 1)
        time.sleep(delay)


def _coerce_vector(
    raw: object, *, expected_dim: int | None,
) -> tuple[float, ...]:
    """Convert one raw vector from Ollama's JSON into a tuple of floats.

    Raises :class:`ValueError` / :class:`TypeError` if any scalar is not
    convertible to float, is non-finite (NaN / Inf), or if the resulting
    dimension does not match ``expected_dim`` (when given).

    Hardening pass added this. Earlier code did ``tuple(float(x) for x in v)``
    inline; that path quietly accepted NaN and Inf — which then either
    crashed pgvector at insert time with a cryptic ``data exception`` or
    poisoned cosine similarity downstream so every query looked equally
    bad. Catching at parse time gives the journal a clean failure with a
    useful reason instead.
    """
    if not isinstance(raw, list):
        raise TypeError(f"vector must be a list, got {type(raw).__name__}")
    out: list[float] = []
    for x in raw:
        if isinstance(x, bool):  # bool subclasses int — refuse explicitly
            raise TypeError("vector scalar must not be bool")
        if not isinstance(x, (int, float)):
            raise TypeError(
                f"vector scalar must be int/float, got {type(x).__name__}"
            )
        f = float(x)
        if not math.isfinite(f):
            raise ValueError(f"vector scalar is non-finite: {f!r}")
        out.append(f)
    if expected_dim is not None and len(out) != expected_dim:
        raise ValueError(
            f"vector has {len(out)} dims, expected {expected_dim}"
        )
    return tuple(out)


__all__ = ["EmbedResult", "OllamaEmbedClient"]
