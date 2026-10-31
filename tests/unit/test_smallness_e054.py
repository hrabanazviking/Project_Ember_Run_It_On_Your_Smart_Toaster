"""E-054 — Graceful smallness: the shed ladder, pinned.

**At budget's edge the companion sheds features by the
stated ladder, announcing each shed.** ``ember.smallness``
reads the process's own resident memory (``/proc/self/
status`` VmRSS; unparseable reads ``None``, never a guess),
judges it against the conversation profile's turn-RAM
ceiling from the budget book (E-041) — COMFORTABLE under
75% of the ceiling, EDGE at/over 75%, STRAINED at/over
90%, OVER at/over the ceiling — and sheds a prefix of the
ladder, cheapest first: (1) history summaries, (2) semantic
memory search (the turn searches on plain words and the
embed call is skipped entirely), (3) the wide history
window (narrowed to the book's smallest allowance).
Answering, saving, the announcements themselves, and tool
safety are never shed. Every shed and every restore
carries one plain sentence, spoken on change only — the
chat wiring writes it to the person's screen and to the
diary (E-034). An unknown reading never votes: nothing
sheds on a gauge that cannot be read. The record lives in
``docs/architecture/E-054_GRACEFUL_SMALLNESS.md``.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ember.budgets import budget_for
from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrConfig,
    ConversationConfig,
    ConversationProfile,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.episode import Episode
from ember.schemas.funi import FinishReason, FuniHealth
from ember.schemas.stream import FuniStreamChunk
from ember.smallness import (
    EDGE_FRACTION,
    OVER_FRACTION,
    RESTORE_ANNOUNCEMENTS,
    SHED_ANNOUNCEMENTS,
    SHED_LADDER,
    STRAINED_FRACTION,
    ShedFeature,
    SmallnessGuard,
    assess,
    plan_for,
    read_rss_mib,
)
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat

PI = ConversationProfile.PI
CEILING = budget_for(PI).turn_ram_mib  # 192.0


def _at(fraction: float) -> float:
    return CEILING * fraction


# ---------------------------------------------------------------- #
# The policy lines                                                  #
# ---------------------------------------------------------------- #


def test_policy_lines_are_the_stated_ladder() -> None:
    # Pinned exactly: a line that quietly moves is not a line.
    assert EDGE_FRACTION == 0.75
    assert STRAINED_FRACTION == 0.90
    assert OVER_FRACTION == 1.00
    assert EDGE_FRACTION < STRAINED_FRACTION < OVER_FRACTION
    assert SHED_LADDER == (
        ShedFeature.HISTORY_SUMMARIES,
        ShedFeature.SEMANTIC_RETRIEVAL,
        ShedFeature.WIDE_HISTORY,
    )
    # Every rung has exactly one shed sentence and one restore
    # sentence — an unannounced shed is a silent shed.
    assert set(SHED_ANNOUNCEMENTS) == set(SHED_LADDER)
    assert set(RESTORE_ANNOUNCEMENTS) == set(SHED_LADDER)
    assert all(SHED_ANNOUNCEMENTS[f].strip() for f in SHED_LADDER)
    assert all(RESTORE_ANNOUNCEMENTS[f].strip() for f in SHED_LADDER)


def test_plans_shed_a_prefix_of_the_ladder() -> None:
    from ember.smallness import SmallnessLevel

    for level in SmallnessLevel:
        plan = plan_for(level)
        assert plan.sheds == SHED_LADDER[: len(plan.sheds)]
        assert plan.announcements == tuple(
            SHED_ANNOUNCEMENTS[f] for f in plan.sheds
        )
        assert plan.semantic_retrieval is (
            ShedFeature.SEMANTIC_RETRIEVAL not in plan.sheds
        )


# ---------------------------------------------------------------- #
# Reading the room                                                  #
# ---------------------------------------------------------------- #


def test_read_rss_parses_vm_rss(tmp_path: Path) -> None:
    status = tmp_path / "status"
    status.write_text(
        "Name:\tember\nVmPeak:\t  500000 kB\nVmRSS:\t   40960 kB\n",
        encoding="ascii",
    )
    assert read_rss_mib(status) == pytest.approx(40.0)


def test_read_rss_unknown_is_none_never_a_guess(tmp_path: Path) -> None:
    assert read_rss_mib(tmp_path / "missing") is None
    garbage = tmp_path / "status"
    garbage.write_text("Name:\tember\nno memory here\n", encoding="ascii")
    assert read_rss_mib(garbage) is None
    bad = tmp_path / "status2"
    bad.write_text("VmRSS:\t  plenty kB\n", encoding="ascii")
    assert read_rss_mib(bad) is None


# ---------------------------------------------------------------- #
# Judging the room                                                  #
# ---------------------------------------------------------------- #


def test_unknown_reading_never_votes() -> None:
    a = assess(PI, None)
    assert a.plan.sheds == ()
    assert a.fraction is None
    assert a.ceiling_mib == CEILING
    assert "unknown never votes" in a.reason


def test_levels_cross_in_ladder_order() -> None:
    assert assess(PI, _at(0.50)).plan.sheds == ()
    assert assess(PI, _at(0.749)).plan.sheds == ()
    edge = assess(PI, _at(EDGE_FRACTION))  # exactly at the line sheds
    assert edge.plan.sheds == SHED_LADDER[:1]
    strained = assess(PI, _at(STRAINED_FRACTION))
    assert strained.plan.sheds == SHED_LADDER[:2]
    assert strained.plan.semantic_retrieval is False
    over = assess(PI, _at(OVER_FRACTION))
    assert over.plan.sheds == SHED_LADDER
    assert assess(PI, _at(1.60)).plan.sheds == SHED_LADDER  # past the ceiling
    assert over.fraction == pytest.approx(1.0)
    assert "192 MiB turn budget" in over.reason


def test_ceiling_comes_from_the_budget_book() -> None:
    toaster = assess(ConversationProfile.TOASTER, 63.0)
    assert toaster.ceiling_mib == 64.0
    assert toaster.plan.sheds == SHED_LADDER[:2]  # 63/64 is strained
    laptop = assess(ConversationProfile.LAPTOP, 63.0)
    assert laptop.plan.sheds == ()  # the same bytes are comfortable there


# ---------------------------------------------------------------- #
# What a plan does to a turn's conversation config                  #
# ---------------------------------------------------------------- #


def test_unshed_plan_returns_the_config_unchanged() -> None:
    config = ConversationConfig(profile=ConversationProfile.LAPTOP)
    comfortable = assess(PI, 1.0).plan  # far under every ceiling
    assert comfortable.sheds == ()
    assert comfortable.conversation_config(config) is config


def test_edge_plan_sheds_only_summaries() -> None:
    config = ConversationConfig(profile=ConversationProfile.LAPTOP)
    narrowed = assess(ConversationProfile.LAPTOP, _at_laptop(0.80)).plan.conversation_config(config)
    assert narrowed.summarise_dropped is False
    assert narrowed.resolved_token_budget == config.resolved_token_budget
    assert narrowed.resolved_max_episodes == config.resolved_max_episodes


def _at_laptop(fraction: float) -> float:
    return budget_for(ConversationProfile.LAPTOP).turn_ram_mib * fraction


def test_over_plan_narrows_history_to_the_smallest_allowance() -> None:
    config = ConversationConfig(profile=ConversationProfile.LAPTOP)
    narrowed = assess(
        ConversationProfile.LAPTOP, _at_laptop(1.0)
    ).plan.conversation_config(config)
    smallest = ConversationConfig(profile=ConversationProfile.TOASTER)
    assert narrowed.resolved_token_budget == smallest.resolved_token_budget == 512
    assert narrowed.resolved_max_episodes == smallest.resolved_max_episodes == 3
    assert narrowed.summarise_dropped is False


def test_narrowing_never_widens_an_operator_override() -> None:
    # An operator's own smaller caps are a choice, not headroom:
    # shedding may narrow further, never widen back.
    config = ConversationConfig(
        profile=ConversationProfile.LAPTOP, token_budget=256, max_episodes=2
    )
    narrowed = assess(
        ConversationProfile.LAPTOP, _at_laptop(1.0)
    ).plan.conversation_config(config)
    assert narrowed.resolved_token_budget == 256
    assert narrowed.resolved_max_episodes == 2
    toaster = ConversationConfig(profile=ConversationProfile.TOASTER)
    narrowed_t = assess(ConversationProfile.TOASTER, 64.0).plan.conversation_config(toaster)
    assert narrowed_t.resolved_token_budget == 512
    assert narrowed_t.resolved_max_episodes == 3


# ---------------------------------------------------------------- #
# The guard — announcements on change, and only on change           #
# ---------------------------------------------------------------- #


def _guard(readings: list[float | None], spoken: list[str]) -> SmallnessGuard:
    queue = iter(readings)
    return SmallnessGuard(
        PI,
        assess_fn=lambda: assess(PI, next(queue)),
        announce=spoken.append,
    )


def test_guard_announces_each_shed_and_restore_once() -> None:
    spoken: list[str] = []
    guard = _guard(
        [_at(0.50), _at(0.80), _at(0.80), _at(0.95), _at(1.10), _at(0.50)],
        spoken,
    )
    guard.consult()  # comfortable: silence
    assert spoken == []
    guard.consult()  # edge: rung 1 sheds
    assert spoken == [SHED_ANNOUNCEMENTS[ShedFeature.HISTORY_SUMMARIES]]
    guard.consult()  # steady at the edge: no repetition
    assert len(spoken) == 1
    guard.consult()  # strained: rung 2 sheds
    assert spoken[-1] == SHED_ANNOUNCEMENTS[ShedFeature.SEMANTIC_RETRIEVAL]
    guard.consult()  # over: rung 3 sheds
    assert spoken[-1] == SHED_ANNOUNCEMENTS[ShedFeature.WIDE_HISTORY]
    assert guard.active_sheds == SHED_LADDER
    guard.consult()  # room returns: all three restore, ladder order
    assert spoken[-3:] == [RESTORE_ANNOUNCEMENTS[f] for f in SHED_LADDER]
    assert guard.active_sheds == ()
    assert guard.announcements == spoken


def test_guard_on_the_real_process_reads_a_real_number() -> None:
    guard = SmallnessGuard(PI)
    assessment = guard.consult()
    # The campaign VM is Linux: /proc/self/status exists and
    # this process has a resident size — a real reading, and
    # the guard's judgement is one of the four stated levels.
    assert assessment.rss_mib is not None and assessment.rss_mib > 0
    assert assessment.fraction == pytest.approx(assessment.rss_mib / CEILING)


# ---------------------------------------------------------------- #
# Chat wiring — the ladder where the turn lives                     #
# ---------------------------------------------------------------- #


class _Brunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self.episodes: list[Episode] = []
        self.searches: list[str] = []

    def recent_episodes(self, limit):
        return list(self.episodes[-limit:]) if limit > 0 else []

    def add_episode(self, episode):
        self.episodes.append(episode)
        return len(self.episodes)

    def hybrid_search(self, *a, **kw):
        self.searches.append("hybrid")
        return []

    def text_search(self, *a, **kw):
        self.searches.append("text")
        return []

    def count(self):  # pragma: no cover
        return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    def close(self) -> None:
        return None


class _StreamingFuni:
    runtime_kind = "fake"
    model_id = "fake:e054"

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        yield FuniStreamChunk(text_delta="a reply", done=False)
        yield FuniStreamChunk(
            text_delta="",
            done=True,
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
        )

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


class _Embedder:
    def __init__(self) -> None:
        self.calls = 0

    def embed(self, texts):
        self.calls += 1
        return [(0.1, 0.2, 0.3, 0.4) for _ in texts]


def _config(tmp_path: Path) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(streaming=True),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
    )


def _run_chat(tmp_path: Path, rss_mib: float, monkeypatch: pytest.MonkeyPatch):
    brunnr = _Brunnr()
    embedder = _Embedder()
    config_root = tmp_path / "ember-home"
    save_identity_atomic(config_root, IdentityConfig())

    def forced_guard(profile, announce=None):
        return SmallnessGuard(
            profile,
            assess_fn=lambda: assess(profile, rss_mib),
            announce=announce,
        )

    monkeypatch.setattr(chat, "SmallnessGuard", forced_guard)
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path),
        config_root=config_root,
        stdin=io.StringIO("hello\n/exit\n"),
        stdout=stdout,
        embed_client=embedder,
        funi_opener=lambda _cfg: _StreamingFuni(),
        strengr_opener=lambda _s, _b: brunnr,
    )
    diary_text = ""
    diary_dir = config_root / "diary"
    if diary_dir.exists():
        diary_text = "\n".join(
            p.read_text(encoding="utf-8") for p in sorted(diary_dir.glob("*.md"))
        )
    return rc, stdout.getvalue(), brunnr, embedder, diary_text


def test_chat_at_the_ceiling_sheds_announces_and_still_answers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rc, out, brunnr, embedder, diary_text = _run_chat(tmp_path, CEILING, monkeypatch)
    assert rc == 0
    # All three sheds announced, in ladder order, on screen…
    positions = [out.index(SHED_ANNOUNCEMENTS[f]) for f in SHED_LADDER]
    assert positions == sorted(positions)
    assert "[room:" in out
    # …and in the diary.
    for feature in SHED_LADDER:
        assert SHED_ANNOUNCEMENTS[feature] in diary_text
    # Semantic retrieval shed: the embed call never happened
    # and the search that ran was the text one.
    assert embedder.calls == 0
    assert brunnr.searches == ["text"]
    # Never shed: the turn was answered and saved.
    assert "a reply" in out
    assert len(brunnr.episodes) == 1
    assert brunnr.episodes[0].operator_input == "hello"


def test_chat_comfortable_sheds_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rc, out, brunnr, embedder, _diary = _run_chat(tmp_path, 10.0, monkeypatch)
    assert rc == 0
    assert "[room:" not in out
    assert embedder.calls == 1
    assert brunnr.searches == ["hybrid"]
    assert len(brunnr.episodes) == 1
