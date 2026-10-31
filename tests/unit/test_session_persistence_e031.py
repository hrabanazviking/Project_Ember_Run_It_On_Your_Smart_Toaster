"""E-031 — Session persistence: the pending-episodes journal.

Docket 82: ``schemas/episode.py`` and DATA_FLOW §2.2 promised a
local pending-episodes journal under
``~/.ember/state/pending_episodes/``, "flushed in on Well
recovery" — in code it did not exist, so a disconnected session's
turns were lost at exit, and a turn whose Well save failed
(E-030) lived only in RAM.

These tests pin the E-031 shape, point by point:

1. Journal round-trip: appended episodes load back in turn order
   with every field (persona tag included).
2. Atomic writes: a completed append leaves no ``.tmp`` fragment;
   a leftover ``.tmp`` from a killed write is ignored — never an
   episode, never corrupt.
3. Corruption: a truncated JSON file and a structurally invalid
   payload are quarantined into ``corrupt/`` on drain (moved, not
   deleted, and reported) while healthy episodes still flush.
4. Drain discipline: a file is removed only after the Well accepts
   it; the first refusal stops the drain, keeps the rest in
   order, and reports the failure; a later drain resumes.
5. Chat, disconnected: turns are journaled; the next connected
   session drains them *before* loading history (the drained turn
   rides in that session's prompt), announces the drain, and the
   journal ends empty.
6. Chat, save failure (E-030's docket-85 site, extended): the
   turn falls back to the journal and the warning says so; only
   when the journal also fails does the operator hear the old
   "remembered only until this session ends".
7. Chat, disconnected + journal failure: spoken, same shape.

No sqlite-vec, no Ollama. Pure double-driven flow (the Well-side
corruption fixtures against the real adapter live in
``test_episode_corruption_e031.py``, extras shape).
"""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.episode import Episode
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import FinishReason, FuniHealth
from ember.schemas.stream import FuniStreamChunk
from ember.spark.hjarta import save_identity_atomic
from ember.spark.munnr import chat
from ember.well.pending_journal import PendingJournal, pending_root


def _ep(i: int, *, persona: str = "default") -> Episode:
    return Episode(
        operator_input=f"question {i}",
        ember_reply=f"answer {i}",
        cited_chunk_ids=(i, i + 100),
        funi_model="fake:tiny",
        well_disconnected=True,
        started_at=datetime(2026, 10, 31, 2, i, tzinfo=UTC),
        completed_at=datetime(2026, 10, 31, 2, i, 30, tzinfo=UTC),
        persona_id=persona,
    )


# --------------------------------------------------------------------- #
# 1 + 2. Journal round-trip and atomic-write shape                        #
# --------------------------------------------------------------------- #


def test_journal_round_trip_in_turn_order_with_persona(tmp_path: Path) -> None:
    journal = PendingJournal(tmp_path / "pending")
    for i in range(3):
        journal.append(_ep(i, persona="saga" if i == 1 else "default"))
    episodes, corrupt = journal.load_all()
    assert corrupt == ()
    assert [e.operator_input for e in episodes] == [f"question {i}" for i in range(3)]
    assert episodes[0].cited_chunk_ids == (0, 100)
    assert episodes[0].well_disconnected is True
    assert episodes[1].persona_id == "saga"
    assert episodes[0].started_at is not None and episodes[0].started_at.hour == 2


def test_append_leaves_no_tmp_and_leftover_tmp_is_ignored(tmp_path: Path) -> None:
    root = tmp_path / "pending"
    journal = PendingJournal(root)
    journal.append(_ep(0))
    assert [p.suffix for p in root.iterdir()] == [".json"]
    # A killed mid-write fragment: never an episode, never corrupt.
    (root / "20261031T020000000000-deadbeef.tmp").write_text(
        '{"operator_input": "tor', encoding="utf-8",
    )
    episodes, corrupt = journal.load_all()
    assert [e.operator_input for e in episodes] == ["question 0"]
    assert corrupt == ()
    assert journal.count() == 1


# --------------------------------------------------------------------- #
# 3 + 4. Corruption quarantine and drain discipline                       #
# --------------------------------------------------------------------- #


class _Well:
    def __init__(self, *, fail_after: int | None = None) -> None:
        self.episodes: list[Episode] = []
        self._fail_after = fail_after

    def add_episode(self, episode: Episode) -> int:
        if self._fail_after is not None and len(self.episodes) >= self._fail_after:
            raise RuntimeError("well refused")
        self.episodes.append(episode)
        return len(self.episodes)


def test_drain_quarantines_corrupt_and_flushes_healthy(tmp_path: Path) -> None:
    root = tmp_path / "pending"
    journal = PendingJournal(root)
    journal.append(_ep(0))
    journal.append(_ep(2))
    # Truncated JSON (a torn write that somehow got a .json name)
    # and a structurally invalid payload, sorting between the two.
    (root / "20261031T020115000000-aaaa.json").write_text(
        '{"operator_input": "tor', encoding="utf-8",
    )
    (root / "20261031T020145000000-bbbb.json").write_text(
        json.dumps({"operator_input": "no reply field"}), encoding="utf-8",
    )
    well = _Well()
    result = journal.drain(well)
    assert result.flushed == 2
    assert result.failure is None
    assert result.kept == 0
    assert len(result.corrupt) == 2
    assert [e.operator_input for e in well.episodes] == ["question 0", "question 2"]
    # Healthy files are gone (accepted); corrupt files are moved
    # aside under corrupt/, not deleted, and not re-counted.
    assert journal.count() == 0
    aside = sorted(p.name for p in (root / "corrupt").glob("*.json"))
    assert len(aside) == 2


def test_drain_stops_at_first_refusal_and_resumes_later(tmp_path: Path) -> None:
    journal = PendingJournal(tmp_path / "pending")
    for i in range(3):
        journal.append(_ep(i))
    refusing = _Well(fail_after=1)
    result = journal.drain(refusing)
    assert result.flushed == 1
    assert result.kept == 2
    assert result.failure is not None and "well refused" in result.failure
    assert journal.count() == 2  # the refused turn + the one after it
    healthy = _Well()
    result2 = journal.drain(healthy)
    assert result2.flushed == 2
    assert [e.operator_input for e in healthy.episodes] == ["question 1", "question 2"]
    assert journal.count() == 0


# --------------------------------------------------------------------- #
# Chat doubles (E-030 shape)                                              #
# --------------------------------------------------------------------- #


def _config(tmp_path: Path) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(streaming=True),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
    )


def _seed_identity(tmp_path: Path) -> Path:
    save_identity_atomic(tmp_path, IdentityConfig())
    return tmp_path


def _disconnected() -> Disconnected:
    return Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
    )


class _NullEmbedder:
    def embed(self, texts):
        return [None for _ in texts]


class _Brunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self, *, save_error: Exception | None = None) -> None:
        self.episodes: list[Episode] = []
        self._save_error = save_error

    def recent_episodes(self, limit):
        return list(self.episodes[-limit:]) if limit > 0 else []

    def add_episode(self, episode):
        if self._save_error is not None:
            raise self._save_error
        self.episodes.append(episode)
        return len(self.episodes)

    def hybrid_search(self, *a, **kw):
        return []

    def text_search(self, *a, **kw):
        return []

    def count(self):  # pragma: no cover
        return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    def close(self) -> None:
        return None


class _StreamingFuni:
    runtime_kind = "fake"
    model_id = "fake:e031"

    def __init__(self, text: str) -> None:
        self._text = text
        self.contexts: list[list] = []

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        self.contexts.append(list(context))
        yield FuniStreamChunk(text_delta=self._text, done=False)
        yield FuniStreamChunk(
            text_delta="", done=True,
            finish_reason=FinishReason.STOP, model_id=self.model_id,
        )

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def _run(tmp_path, *, funi, well, lines="hello\n/exit\n"):
    config_root = _seed_identity(tmp_path / "ember-home")
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path),
        config_root=config_root,
        stdin=io.StringIO(lines),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: well,
    )
    return rc, stdout.getvalue(), config_root


# --------------------------------------------------------------------- #
# 5. Disconnected turns survive; the next session drains them             #
# --------------------------------------------------------------------- #


def test_disconnected_turns_drain_into_next_session_history(
    tmp_path: Path,
) -> None:
    funi1 = _StreamingFuni("answer while offline")
    rc, _out, root = _run(tmp_path, funi=funi1, well=_disconnected())
    assert rc == 0
    journal = PendingJournal(pending_root(root))
    assert journal.count() == 1

    brunnr = _Brunnr()
    funi2 = _StreamingFuni("answer back online")
    rc, out, _root2 = _run(
        tmp_path, funi=funi2, well=brunnr, lines="again\n/exit\n",
    )
    assert rc == 0
    assert "added 1 saved turn(s)" in out
    # The drained turn reached the Well first, the new turn second.
    assert [e.operator_input for e in brunnr.episodes] == ["hello", "again"]
    assert brunnr.episodes[0].ember_reply == "answer while offline"
    assert brunnr.episodes[0].well_disconnected is True
    # And it rode in the new session's prompt as history.
    context_texts = [item.text for item in funi2.contexts[0]]
    assert any("hello" in t for t in context_texts)
    assert journal.count() == 0


# --------------------------------------------------------------------- #
# 6 + 7. Save-failure fallback and journal-failure honesty                #
# --------------------------------------------------------------------- #


def test_save_failure_falls_back_to_journal_and_says_so(tmp_path: Path) -> None:
    funi = _StreamingFuni("an answer")
    brunnr = _Brunnr(save_error=RuntimeError("disk full"))
    rc, out, root = _run(tmp_path, funi=funi, well=brunnr)
    assert rc == 0
    assert "this turn could not be saved to the Well" in out
    assert "saved locally" in out
    assert "remembered only until this session ends" not in out
    assert brunnr.episodes == []
    journal = PendingJournal(pending_root(root))
    episodes, corrupt = journal.load_all()
    assert corrupt == ()
    assert [e.operator_input for e in episodes] == ["hello"]


def test_save_and_journal_failure_is_the_old_honest_warning(
    tmp_path: Path,
) -> None:
    # Block the journal: its directory path is a plain file.
    config_root = _seed_identity(tmp_path / "ember-home")
    blocked = pending_root(config_root)
    blocked.parent.mkdir(parents=True, exist_ok=True)
    blocked.write_text("not a directory", encoding="utf-8")
    funi = _StreamingFuni("an answer")
    brunnr = _Brunnr(save_error=RuntimeError("disk full"))
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path),
        config_root=config_root,
        stdin=io.StringIO("hello\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: brunnr,
    )
    out = stdout.getvalue()
    assert rc == 0
    assert "could not be saved to the Well" in out
    assert "or to the local pending journal" in out
    assert "remembered only until this session ends" in out


def test_disconnected_journal_failure_is_spoken(tmp_path: Path) -> None:
    config_root = _seed_identity(tmp_path / "ember-home")
    blocked = pending_root(config_root)
    blocked.parent.mkdir(parents=True, exist_ok=True)
    blocked.write_text("not a directory", encoding="utf-8")
    funi = _StreamingFuni("an answer")
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path),
        config_root=config_root,
        stdin=io.StringIO("hello\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda _s, _b: _disconnected(),
    )
    out = stdout.getvalue()
    assert rc == 0
    assert "this turn could not be saved locally" in out
    assert "remembered only until this session ends" in out
