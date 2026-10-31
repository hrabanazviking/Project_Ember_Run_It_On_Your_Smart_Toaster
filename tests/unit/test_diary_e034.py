"""E-034 — the diary: a log a friend can read.

Pins the E-034 shape:

1. The Diary writes plain, dated, one-line entries to
   ``<root>/YYYY-MM-DD.md`` and reads recent entries back.
2. The diary is off when config says so, and writes nothing.
3. A diary write failure NEVER raises into a caller — and in
   chat it warns once, in plain words, and the session serves on.
4. Chat records the session's facts (started, Well reached or
   not, saved turns drained, history loaded, each turn answered
   and where it was saved, ended) — and NEVER the operator's
   words or the reply's words.
5. The diary lives beside the technical trace: configuring the
   trace (``ember.logging.configure_from``) is unchanged.
6. ``ember diary`` reads the entries back for a friend.

No sqlite-vec, no Ollama. Pure double-driven flow, in the
E-030 test shape.
"""

from __future__ import annotations

import io
import logging as py_logging
from datetime import UTC, datetime
from pathlib import Path

from ember import logging as ember_logging
from ember.cli.main import main as cli_main
from ember.diary import Diary, diary_root
from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    LogLevel,
    LoggingConfig,
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

WHEN = datetime(2026, 10, 31, 9, 5, tzinfo=UTC)

# --------------------------------------------------------------------- #
# The Diary itself                                                        #
# --------------------------------------------------------------------- #


def test_diary_writes_plain_dated_entries(tmp_path: Path) -> None:
    diary = Diary(tmp_path / "diary")
    assert diary.record("A chat session started with Ember.", when=WHEN) is True
    assert diary.record("A turn was answered.", when=WHEN) is True
    day_file = tmp_path / "diary" / "2026-10-31.md"
    text = day_file.read_text(encoding="utf-8")
    assert text.startswith("# Ember's diary — 2026-10-31")
    assert "- 09:05 — A chat session started with Ember." in text
    assert "- 09:05 — A turn was answered." in text


def test_diary_entry_is_always_one_line(tmp_path: Path) -> None:
    diary = Diary(tmp_path / "diary")
    assert diary.record("first line\nsecond line\r\nthird", when=WHEN) is True
    lines = [
        ln for ln in (tmp_path / "diary" / "2026-10-31.md")
        .read_text(encoding="utf-8").splitlines() if ln.startswith("- ")
    ]
    assert lines == ["- 09:05 — first line second line third"]


def test_diary_read_recent_flattens_with_dates(tmp_path: Path) -> None:
    diary = Diary(tmp_path / "diary")
    diary.record("Yesterday it rained.", when=datetime(2026, 10, 30, 8, 0, tzinfo=UTC))
    diary.record("A turn was answered.", when=WHEN)
    entries = diary.read_recent(days=2, now=WHEN)
    assert entries == (
        "2026-10-30 08:00 — Yesterday it rained.",
        "2026-10-31 09:05 — A turn was answered.",
    )
    # A missing diary reads as empty, not as an error.
    assert Diary(tmp_path / "absent").read_recent() == ()


def test_diary_off_writes_nothing(tmp_path: Path) -> None:
    root = tmp_path / "diary"
    diary = Diary(root, enabled=False)
    assert diary.record("A turn was answered.", when=WHEN) is False
    assert not root.exists()


def test_diary_write_failure_never_raises(tmp_path: Path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    diary = Diary(blocker / "diary")
    assert diary.record("A turn was answered.", when=WHEN) is False


# --------------------------------------------------------------------- #
# Chat integration (doubles in the E-030 shape)                           #
# --------------------------------------------------------------------- #


class _NullEmbedder:
    def embed(self, texts):
        return [None for _ in texts]


class _Brunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self.episodes: list = []

    def recent_episodes(self, limit):
        return []

    def add_episode(self, episode):
        self.episodes.append(episode)
        return 1

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
    model_id = "fake:e034"

    def __init__(self, text: str = "a reply only Ember should show") -> None:
        self._text = text

    def complete(self, prompt, context, tools=None):  # pragma: no cover
        raise AssertionError("streaming config must not call complete")

    def complete_streaming(self, prompt, context, tools=None):
        yield FuniStreamChunk(text_delta=self._text, done=False)
        yield FuniStreamChunk(
            text_delta="", done=True,
            finish_reason=FinishReason.STOP, model_id=self.model_id,
        )

    def health(self):
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self):
        return None


def _config(tmp_path: Path, *, diary: bool = True) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(streaming=True),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
        logging=LoggingConfig(diary=diary),
    )


def _run_chat(tmp_path, *, well, diary=True, lines="hello there\n/exit\n",
              funi=None):
    config_root = tmp_path / "ember-home"
    save_identity_atomic(config_root, IdentityConfig())
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path, diary=diary),
        config_root=config_root,
        stdin=io.StringIO(lines),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: funi or _StreamingFuni(),
        strengr_opener=lambda _s, _b: well,
    )
    return rc, stdout.getvalue(), config_root


def _diary_text(config_root: Path) -> str:
    root = diary_root(config_root)
    if not root.is_dir():
        return ""
    return "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(root.glob("*.md"))
    )


def test_chat_diary_records_session_and_turn_without_content(
    tmp_path: Path,
) -> None:
    brunnr = _Brunnr()
    funi = _StreamingFuni("THE REPLY WORDS MUST NOT LEAK")
    rc, _out, config_root = _run_chat(
        tmp_path, well=brunnr, funi=funi,
        lines="THE OPERATOR WORDS MUST NOT LEAK\n/exit\n",
    )
    assert rc == 0
    text = _diary_text(config_root)
    assert "A chat session started with Ember (model fake:e034)." in text
    assert "The memory store was connected." in text
    assert "No earlier exchanges were loaded from memory." in text
    assert "A turn was answered." in text
    assert "The turn was saved to the memory store." in text
    assert "The chat session ended." in text
    # The diary records THAT things happened — never what was said.
    assert "THE OPERATOR WORDS MUST NOT LEAK" not in text
    assert "THE REPLY WORDS MUST NOT LEAK" not in text


def test_chat_diary_records_disconnected_session(tmp_path: Path) -> None:
    disconnected = Disconnected(
        reason=DisconnectReason.CONN_REFUSED, since=datetime.now(tz=UTC),
    )
    rc, _out, config_root = _run_chat(tmp_path, well=disconnected)
    assert rc == 0
    text = _diary_text(config_root)
    assert "The memory store could not be reached" in text
    assert "A turn was answered without memory grounding." in text
    assert "The turn was saved locally" in text


def test_chat_diary_records_drained_saved_turns(tmp_path: Path) -> None:
    config_root = tmp_path / "ember-home"
    save_identity_atomic(config_root, IdentityConfig())
    PendingJournal(pending_root(config_root)).append(Episode(
        operator_input="OLD OPERATOR WORDS MUST NOT LEAK",
        ember_reply="OLD REPLY WORDS MUST NOT LEAK",
        started_at=datetime.now(tz=UTC), completed_at=datetime.now(tz=UTC),
    ))
    brunnr = _Brunnr()
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path),
        config_root=config_root,
        stdin=io.StringIO("hello\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: _StreamingFuni(),
        strengr_opener=lambda _s, _b: brunnr,
    )
    assert rc == 0
    assert len(brunnr.episodes) == 2  # the drained turn + this turn
    text = _diary_text(config_root)
    assert "1 saved turn(s) from an earlier session were added" in text
    assert "OLD OPERATOR WORDS MUST NOT LEAK" not in text
    assert "OLD REPLY WORDS MUST NOT LEAK" not in text


def test_chat_diary_off_via_config_writes_nothing(tmp_path: Path) -> None:
    rc, _out, config_root = _run_chat(tmp_path, well=_Brunnr(), diary=False)
    assert rc == 0
    assert not diary_root(config_root).exists()


def test_chat_diary_failure_warns_once_and_never_crashes(
    tmp_path: Path,
) -> None:
    config_root = tmp_path / "ember-home"
    save_identity_atomic(config_root, IdentityConfig())
    # A plain file where the diary folder would go: every write fails.
    (config_root / "diary").write_text("blocked", encoding="utf-8")
    stdout = io.StringIO()
    rc = chat.run(
        config=_config(tmp_path),
        config_root=config_root,
        stdin=io.StringIO("one\ntwo\n/exit\n"),
        stdout=stdout,
        embed_client=_NullEmbedder(),
        funi_opener=lambda _cfg: _StreamingFuni(),
        strengr_opener=lambda _s, _b: _Brunnr(),
    )
    out = stdout.getvalue()
    assert rc == 0
    assert out.count("Ember's diary could not be written") == 1
    assert "The chat itself is unaffected" in out


# --------------------------------------------------------------------- #
# Beside the technical trace + the reader surface                         #
# --------------------------------------------------------------------- #


def test_technical_trace_still_configures_unchanged() -> None:
    ember_logging.configure_from(LoggingConfig())
    assert py_logging.getLogger().level == py_logging.INFO
    ember_logging.configure_from(LoggingConfig(level=LogLevel.WARNING))
    assert py_logging.getLogger().level == py_logging.WARNING


def test_cli_diary_prints_recent_entries(tmp_path: Path) -> None:
    config_root = tmp_path / "ember-home"
    config_root.mkdir(parents=True)
    Diary(diary_root(config_root)).record("A turn was answered.")
    stdout = io.StringIO()
    rc = cli_main(
        ["--config-root", str(config_root), "diary"], stdout=stdout,
    )
    assert rc == 0
    assert "A turn was answered." in stdout.getvalue()


def test_cli_diary_with_no_entries_is_plain(tmp_path: Path) -> None:
    config_root = tmp_path / "ember-home"
    config_root.mkdir(parents=True)
    stdout = io.StringIO()
    rc = cli_main(
        ["--config-root", str(config_root), "diary"], stdout=stdout,
    )
    assert rc == 0
    assert stdout.getvalue() == "No diary entries yet.\n"
