"""E-051 — Thermal & patience etiquette, pinned.

**The companion yields.** Before this slice the core had
no load or thermal manners at all. ``ember.etiquette``
now reads the room (1-minute load per CPU; the hottest
thermal zone, ``None`` where a machine exposes none —
the campaign VM has no zones), judges it PROCEED / EASE /
YIELD with worst-signal-wins, and offers background work
a *bounded* wait: it sleeps the level's delay, re-reads,
and never waits past ``MAX_WAIT_S`` in total — after the
bound the work proceeds and the outcome says so. The one
wiring is Smiðja's bulk embedding: the local-files
ingest's default client carries the hook, and the embed
client consults it *between batches only*, so a
single-batch foreground embed never waits. Policy lines:
per-CPU load 1.0 eases / 2.0 yields; 70 °C eases / 80 °C
yields (below the point small boards throttle). The
record lives in
``docs/architecture/E-051_THERMAL_PATIENCE_ETIQUETTE.md``.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

from ember.etiquette import (
    EASE_DELAY_S,
    LOAD_EASE_PER_CPU,
    LOAD_YIELD_PER_CPU,
    MAX_WAIT_S,
    THERMAL_EASE_C,
    THERMAL_YIELD_C,
    YIELD_DELAY_S,
    PatienceAssessment,
    PatienceLevel,
    assess,
    parse_thermal_celsius,
    system_load_per_cpu,
    wait_for_room,
)
from ember.schemas.config import EmbeddingConfig
from ember.well.smidja.embed_client import OllamaEmbedClient


def _judged(level: PatienceLevel) -> PatienceAssessment:
    return PatienceAssessment(
        level=level, load_per_cpu=None, thermal_c=None, reason="test"
    )


def _sequence(levels: list[PatienceLevel]) -> Iterator[PatienceAssessment]:
    return iter(_judged(level) for level in levels)


# ---------------------------------------------------------------- #
# The policy lines                                                  #
# ---------------------------------------------------------------- #


def test_policy_lines_are_the_stated_manners() -> None:
    # Pinned exactly: a line that quietly moves is not a line.
    assert LOAD_EASE_PER_CPU == 1.0
    assert LOAD_YIELD_PER_CPU == 2.0
    assert THERMAL_EASE_C == 70.0
    assert THERMAL_YIELD_C == 80.0
    # Ease and yield sit strictly below the danger line —
    # the Aesir lesson is to back off BEFORE it.
    assert THERMAL_EASE_C < THERMAL_YIELD_C
    assert EASE_DELAY_S == 1.0
    assert YIELD_DELAY_S == 5.0
    assert MAX_WAIT_S == 30.0


def test_assess_load_ladder() -> None:
    assert assess(load_per_cpu=0.25, thermal_c=None).level is PatienceLevel.PROCEED
    assert assess(load_per_cpu=1.0, thermal_c=None).level is PatienceLevel.EASE
    assert assess(load_per_cpu=1.99, thermal_c=None).level is PatienceLevel.EASE
    assert assess(load_per_cpu=2.0, thermal_c=None).level is PatienceLevel.YIELD


def test_assess_thermal_ladder() -> None:
    assert assess(load_per_cpu=None, thermal_c=55.0).level is PatienceLevel.PROCEED
    assert assess(load_per_cpu=None, thermal_c=70.0).level is PatienceLevel.EASE
    assert assess(load_per_cpu=None, thermal_c=79.9).level is PatienceLevel.EASE
    assert assess(load_per_cpu=None, thermal_c=80.0).level is PatienceLevel.YIELD


def test_assess_worst_signal_wins_and_unknown_never_votes() -> None:
    # A clear load reading cannot talk a hot machine down.
    hot = assess(load_per_cpu=0.1, thermal_c=85.0)
    assert hot.level is PatienceLevel.YIELD
    assert "°C" in hot.reason
    # A saturated load yields even on a cool machine.
    busy = assess(load_per_cpu=3.0, thermal_c=40.0)
    assert busy.level is PatienceLevel.YIELD
    # No signals at all: nothing votes, the room is clear —
    # unknown is never dressed up as danger or as calm.
    unknown = assess(load_per_cpu=None, thermal_c=None)
    assert unknown.level is PatienceLevel.PROCEED


# ---------------------------------------------------------------- #
# Reading the room                                                  #
# ---------------------------------------------------------------- #


def test_system_load_per_cpu_divides_by_cores() -> None:
    value = system_load_per_cpu(
        loadavg=lambda: (6.0, 3.0, 1.0), cpu_count=lambda: 4
    )
    assert value == 1.5


def test_system_load_per_cpu_unknown_is_none_not_a_guess() -> None:
    def boom() -> tuple[float, float, float]:
        raise OSError("no load here")

    assert system_load_per_cpu(loadavg=boom, cpu_count=lambda: 4) is None
    assert (
        system_load_per_cpu(loadavg=lambda: (1.0, 1.0, 1.0), cpu_count=lambda: None)
        is None
    )


def test_parse_thermal_takes_the_hottest_zone(tmp_path: Path) -> None:
    zone0 = tmp_path / "thermal_zone0"
    zone1 = tmp_path / "thermal_zone1"
    zone0.mkdir()
    zone1.mkdir()
    (zone0 / "temp").write_text("45000\n", encoding="ascii")
    (zone1 / "temp").write_text("72500\n", encoding="ascii")
    assert parse_thermal_celsius(tmp_path) == 72.5


def test_parse_thermal_skips_malformed_and_absent_is_none(tmp_path: Path) -> None:
    # No zones at all (the campaign VM's shape): None.
    assert parse_thermal_celsius(tmp_path) is None
    zone = tmp_path / "thermal_zone0"
    zone.mkdir()
    (zone / "temp").write_text("not-a-number\n", encoding="ascii")
    # A malformed zone is skipped, not guessed at.
    assert parse_thermal_celsius(tmp_path) is None
    (zone / "temp").write_text("60000\n", encoding="ascii")
    assert parse_thermal_celsius(tmp_path) == 60.0


# ---------------------------------------------------------------- #
# Waiting, bounded                                                  #
# ---------------------------------------------------------------- #


def test_wait_for_room_proceeds_at_once_in_a_clear_room() -> None:
    sleeps: list[float] = []
    outcome = wait_for_room(
        assess_fn=lambda: _judged(PatienceLevel.PROCEED), sleep=sleeps.append
    )
    assert outcome.waited_s == 0.0
    assert outcome.checks == 1
    assert outcome.bound_reached is False
    assert sleeps == []


def test_wait_for_room_sleeps_the_levels_delay_then_rechecks() -> None:
    levels = _sequence(
        [PatienceLevel.YIELD, PatienceLevel.EASE, PatienceLevel.PROCEED]
    )
    sleeps: list[float] = []
    outcome = wait_for_room(
        assess_fn=lambda: next(levels), sleep=sleeps.append
    )
    assert sleeps == [YIELD_DELAY_S, EASE_DELAY_S]
    assert outcome.waited_s == YIELD_DELAY_S + EASE_DELAY_S
    assert outcome.checks == 3
    assert outcome.bound_reached is False


def test_wait_for_room_is_bounded_and_says_so() -> None:
    # A room that never clears: the wait stops at the
    # bound exactly, and the outcome records it — patience
    # never becomes a deadlock.
    sleeps: list[float] = []
    outcome = wait_for_room(
        assess_fn=lambda: _judged(PatienceLevel.YIELD),
        sleep=sleeps.append,
        max_wait_s=12.0,
    )
    assert outcome.waited_s == 12.0
    assert sum(sleeps) == 12.0
    assert outcome.bound_reached is True
    assert outcome.assessment.level is PatienceLevel.YIELD


# ---------------------------------------------------------------- #
# The wiring: bulk embedding yields between batches                 #
# ---------------------------------------------------------------- #


class _MockResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _MockResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _factory(req: Any, *, timeout: float = 0.0) -> _MockResponse:
    payload = json.loads(req.data)
    return _MockResponse(
        {"embeddings": [[1.0, 0.0] for _ in payload["input"]]}
    )


def test_embed_hook_fires_between_batches_only() -> None:
    calls: list[int] = []
    cfg = EmbeddingConfig(batch_size=2)
    client = OllamaEmbedClient(
        config=cfg, max_attempts=1, patience_hook=lambda: calls.append(1)
    )
    with patch("urllib.request.urlopen", side_effect=_factory):
        vectors = client.embed(["a", "b", "c", "d", "e"])
    assert len(vectors) == 5
    # Three batches -> the hook fires before batches 2 and
    # 3, never before the first.
    assert calls == [1, 1]


def test_single_batch_embed_never_waits() -> None:
    calls: list[int] = []
    cfg = EmbeddingConfig(batch_size=8)
    client = OllamaEmbedClient(
        config=cfg, max_attempts=1, patience_hook=lambda: calls.append(1)
    )
    with patch("urllib.request.urlopen", side_effect=_factory):
        vectors = client.embed(["only", "turn"])
    assert len(vectors) == 2
    assert calls == []


def test_etiquette_proof_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"
