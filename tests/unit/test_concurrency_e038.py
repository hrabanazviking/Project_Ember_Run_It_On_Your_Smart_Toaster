"""E-038 — Concurrency on small hardware: two chats, measured.

The roadmap line asks for two chats at once under phone-class
budgets. Before E-038 the core had never been run that way, and
three shared surfaces raced:

- the pending journal's drain: two chats starting together both
  read the same file list and both flushed every episode into
  the Well — each turn landed twice (fixed: drain claims a file
  by atomic rename before touching it, E-038);
- the diary: two writers could each write the day's header, and
  a header could land mid-entry (fixed: an exclusive advisory
  lock around the size check + write, E-038);
- the sqlite Well: two processes could fail a save with
  "database is locked" instead of waiting (fixed in the adapter:
  ``PRAGMA busy_timeout``, pinned by the companion file
  ``test_concurrency_well_e038.py`` in the extras shape).

These tests run two real ``chat.run`` sessions concurrently in
threads on the phone profile (1024 history tokens / 5 episodes
per session — E-021's numbers), against one shared Well, and
pin: both sessions complete, neither conversation's words reach
the other's prompt, what each persists carries its own tag, and
the two windowed histories together stay within twice the
phone budget. The journal and diary races are pinned directly
with deliberately slowed fakes so the overlap is forced, not
hoped for.
"""

from __future__ import annotations

import io
import threading
import time
from dataclasses import replace
from pathlib import Path

from ember.diary import Diary
from ember.schemas.config import (
    ConversationConfig,
    ConversationProfile,
    EmberConfig,
)
from ember.schemas.episode import Episode
from ember.schemas.funi import ContextKind, FinishReason
from ember.schemas.stream import FuniStreamChunk
from ember.spark.funi.windowing import window_history
from ember.spark.munnr import chat
from ember.well.pending_journal import PendingJournal

PHONE = ConversationConfig(profile=ConversationProfile.PHONE)


def _ep(text: str, conversation_id: str = "default") -> Episode:
    return Episode(
        operator_input=text, ember_reply=f"reply to {text}",
        conversation_id=conversation_id,
    )


# --------------------------------------------------------------------- #
# The pending journal under two writers / two drains                   #
# --------------------------------------------------------------------- #


class _SlowWell:
    """A recording Well whose saves are slow enough to force overlap."""

    def __init__(self, delay: float = 0.02) -> None:
        self.added: list[Episode] = []
        self._lock = threading.Lock()
        self._delay = delay

    def add_episode(self, episode: Episode) -> int:
        time.sleep(self._delay)
        with self._lock:
            self.added.append(episode)
            return len(self.added)


def _run_threads(*fns) -> list[BaseException]:
    errors: list[BaseException] = []

    def guard(fn):
        try:
            fn()
        except BaseException as exc:  # noqa: BLE001 — re-raised by assert below
            errors.append(exc)

    threads = [threading.Thread(target=guard, args=(fn,)) for fn in fns]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert all(not t.is_alive() for t in threads), "a worker thread hung"
    return errors


def test_two_drains_flush_each_episode_exactly_once(tmp_path: Path) -> None:
    journal = PendingJournal(tmp_path / "pending")
    episodes = [_ep(f"turn-{i}", "kitchen") for i in range(8)]
    for ep in episodes:
        journal.append(ep)
    well = _SlowWell()
    results: dict[str, object] = {}

    def drain(name: str) -> None:
        results[name] = journal.drain(well)

    errors = _run_threads(lambda: drain("a"), lambda: drain("b"))
    assert errors == []
    # No duplicates, no losses: the Well saw each turn exactly once.
    assert sorted(ep.operator_input for ep in well.added) == [
        f"turn-{i}" for i in range(8)
    ]
    total_flushed = results["a"].flushed + results["b"].flushed  # type: ignore[attr-defined]
    assert total_flushed == 8
    assert journal.files() == []
    assert journal.count() == 0


def test_drain_refusal_releases_the_claim_and_keeps_order(
    tmp_path: Path,
) -> None:
    journal = PendingJournal(tmp_path / "pending")
    for i in range(3):
        journal.append(_ep(f"turn-{i}"))

    class _Refusing:
        def add_episode(self, episode: Episode) -> int:
            raise RuntimeError("well said no")

    result = journal.drain(_Refusing())
    assert result.flushed == 0
    assert result.failure is not None and "well said no" in result.failure
    assert result.kept == 3
    # The claimed file came back under its original name, in order.
    loaded, corrupt = journal.load_all()
    assert corrupt == ()
    assert [ep.operator_input for ep in loaded] == ["turn-0", "turn-1", "turn-2"]


def test_concurrent_drain_quarantines_corrupt_once(tmp_path: Path) -> None:
    journal = PendingJournal(tmp_path / "pending")
    journal.append(_ep("good-turn"))
    (journal.root / "20260101T000000000000-deadbeef0000.json").write_text(
        "{not json", encoding="utf-8"
    )
    well = _SlowWell(delay=0.0)
    results: list = []

    def drain() -> None:
        results.append(journal.drain(well))

    errors = _run_threads(drain, drain)
    assert errors == []
    assert [ep.operator_input for ep in well.added] == ["good-turn"]
    assert sum(len(r.corrupt) for r in results) == 1
    quarantined = list((journal.root / "corrupt").glob("*.json"))
    assert len(quarantined) == 1
    assert journal.files() == []


def test_concurrent_appends_lose_nothing(tmp_path: Path) -> None:
    journal = PendingJournal(tmp_path / "pending")

    def append_batch(tag: str) -> None:
        for i in range(15):
            journal.append(_ep(f"{tag}-{i}"))

    errors = _run_threads(
        lambda: append_batch("a"), lambda: append_batch("b")
    )
    assert errors == []
    loaded, corrupt = journal.load_all()
    assert corrupt == ()
    assert sorted(ep.operator_input for ep in loaded) == sorted(
        [f"a-{i}" for i in range(15)] + [f"b-{i}" for i in range(15)]
    )


# --------------------------------------------------------------------- #
# The diary under two writers                                          #
# --------------------------------------------------------------------- #


def test_two_diaries_one_header_and_every_entry(tmp_path: Path) -> None:
    root = tmp_path / "diary"

    def write_batch(tag: str) -> None:
        diary = Diary(root)
        for i in range(20):
            assert diary.record(f"{tag} entry {i}")

    errors = _run_threads(
        lambda: write_batch("alpha"), lambda: write_batch("beta")
    )
    assert errors == []
    files = list(root.glob("*.md"))
    assert len(files) == 1
    lines = files[0].read_text(encoding="utf-8").splitlines()
    headers = [ln for ln in lines if ln.startswith("# ")]
    entries = [ln for ln in lines if ln.startswith("- ")]
    assert len(headers) == 1
    assert len(entries) == 40
    diary = Diary(root)
    recent = diary.read_recent(days=1)
    assert len(recent) == 40


# --------------------------------------------------------------------- #
# Two chats at once, phone profile, one shared Well                    #
# --------------------------------------------------------------------- #


class _SharedWell:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self, stored: list[Episode]) -> None:
        self._stored = list(stored)
        self.added: list[Episode] = []
        self._lock = threading.Lock()

    def recent_episodes(self, limit: int) -> list[Episode]:
        with self._lock:
            return list(self._stored[-limit:] if limit > 0 else [])

    def add_episode(self, episode: Episode) -> int:
        time.sleep(0.01)
        with self._lock:
            self.added.append(episode)
            self._stored.append(episode)
            return len(self._stored)

    def text_search(self, query: str, k: int, filter=None):  # noqa: A002
        return []

    def hybrid_search(self, qvec, query: str, k: int):
        return []

    def close(self) -> None:
        return None


class _SlowFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"

    def __init__(self, barrier: threading.Barrier) -> None:
        self.contexts: list[list] = []
        self._barrier = barrier

    def complete_streaming(self, prompt, context, tools=None):
        self.contexts.append(list(context))
        # Both sessions must be mid-turn at the same moment; if
        # the runs were secretly serialised this barrier times
        # out and the test fails loudly instead of passing soft.
        self._barrier.wait(timeout=10)
        time.sleep(0.02)
        yield FuniStreamChunk(
            text_delta="reply text",
            done=True,
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
        )

    def close(self) -> None:
        return None


class _NullEmbed:
    def embed(self, texts):
        return [None for _ in texts]


def _chat_kwargs(tmp_path: Path, well, funi, conversation_id: str):
    return dict(
        config=replace(EmberConfig(), conversation=PHONE),
        config_root=tmp_path,
        stdin=io.StringIO("hello again\n/exit\n"),
        stdout=io.StringIO(),
        embed_client=_NullEmbed(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda *_a: well,
        conversation_id=conversation_id,
    )


def test_two_chats_at_once_phone_profile_no_bleed(tmp_path: Path) -> None:
    stored = [
        _ep("KITCHEN-WORD seed order", "kitchen"),
        _ep("WORKSHOP-WORD torque specs", "workshop"),
    ]
    well = _SharedWell(stored)
    barrier = threading.Barrier(2)
    funis = {"kitchen": _SlowFuni(barrier), "workshop": _SlowFuni(barrier)}
    rcs: dict[str, int] = {}

    def run_one(conv: str) -> None:
        rcs[conv] = chat.run(**_chat_kwargs(tmp_path, well, funis[conv], conv))

    errors = _run_threads(
        lambda: run_one("kitchen"), lambda: run_one("workshop")
    )
    assert errors == []
    assert rcs == {"kitchen": 0, "workshop": 0}

    for conv, own, foreign in (
        ("kitchen", "KITCHEN-WORD", "WORKSHOP-WORD"),
        ("workshop", "WORKSHOP-WORD", "KITCHEN-WORD"),
    ):
        text = "\n".join(
            item.text
            for ctx in funis[conv].contexts
            for item in ctx
            if item.kind is ContextKind.EPISODE
        )
        assert own in text
        assert foreign not in text

    assert sorted(ep.conversation_id for ep in well.added) == [
        "kitchen", "workshop",
    ]

    # Phone-class budgets, measured on the window: each session's
    # history fits the phone budget, so two together fit twice it.
    for conv in ("kitchen", "workshop"):
        history = [
            ep for ep in well._stored if ep.conversation_id == conv
        ]
        windowed = window_history(history, PHONE)
        assert windowed.estimated_tokens <= PHONE.resolved_token_budget


def test_two_disconnected_chats_journal_without_loss(
    tmp_path: Path,
) -> None:
    from datetime import UTC, datetime

    from ember.schemas.errors import Disconnected, DisconnectReason

    disconnect = Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
        detail="fake outage",
    )
    barrier = threading.Barrier(2)
    rcs: dict[str, int] = {}

    def run_one(conv: str) -> None:
        funi = _SlowFuni(barrier)
        rcs[conv] = chat.run(
            config=replace(EmberConfig(), conversation=PHONE),
            config_root=tmp_path,
            stdin=io.StringIO("hello again\n/exit\n"),
            stdout=io.StringIO(),
            embed_client=_NullEmbed(),
            funi_opener=lambda _cfg: funi,
            strengr_opener=lambda *_a: disconnect,
            conversation_id=conv,
        )

    errors = _run_threads(
        lambda: run_one("kitchen"), lambda: run_one("workshop")
    )
    assert errors == []
    assert rcs == {"kitchen": 0, "workshop": 0}
    from ember.well.pending_journal import pending_root

    journal = PendingJournal(pending_root(tmp_path))
    loaded, corrupt = journal.load_all()
    assert corrupt == ()
    assert sorted(ep.conversation_id for ep in loaded) == [
        "kitchen", "workshop",
    ]
