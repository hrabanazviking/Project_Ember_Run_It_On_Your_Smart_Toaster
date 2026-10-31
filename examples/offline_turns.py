"""Example 3 — a chat while the memory store is unreachable.

Run it (from the repo root, no optional extras needed):

    PYTHONPATH=src python3 examples/offline_turns.py

What this shows: Ember's offline truth (E-029/E-031/E-034),
lived end to end with the same fake model as `first_chat.py`:

1. the Well cannot be reached, so the session says so up front
   (a banner, never silence) and answers *ungrounded*;
2. the turn is not lost: it is written to the pending-episodes
   journal on disk — one small JSON file per turn, written
   atomically — and the plain-words diary records that the
   session happened, without recording anything that was said;
3. when a later session finds the Well again, the journal
   drains into it in order — here the example drains it into a
   fresh in-memory Well and shows the turn arriving.

State lives in a temporary folder that is removed at the end.
"""

from __future__ import annotations

import io
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

# Allow running straight from a source checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ember.diary import Diary, diary_root  # noqa: E402
from ember.schemas.config import EmberConfig  # noqa: E402
from ember.schemas.episode import Episode  # noqa: E402
from ember.schemas.errors import Disconnected, DisconnectReason  # noqa: E402
from ember.schemas.funi import FinishReason  # noqa: E402
from ember.schemas.stream import FuniStreamChunk  # noqa: E402
from ember.spark.munnr import chat  # noqa: E402
from ember.well.pending_journal import PendingJournal, pending_root  # noqa: E402


class ExampleFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"

    def complete_streaming(self, prompt, context, tools=None):
        yield FuniStreamChunk(
            text_delta="I can still talk while my memory is away.",
            done=True,
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
        )

    def close(self) -> None:
        return None


class _NullEmbed:
    def embed(self, texts):
        return [None for _ in texts]


class FreshWell:
    """The Well, reachable again: an in-memory stand-in."""

    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self.added: list[Episode] = []

    def add_episode(self, episode: Episode) -> int:
        self.added.append(episode)
        return len(self.added)


def main() -> int:
    disconnect = Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
        detail="example outage",
    )
    with tempfile.TemporaryDirectory(prefix="ember-example-") as tmp:
        root = Path(tmp)
        out = io.StringIO()
        rc = chat.run(
            config=EmberConfig(),
            config_root=root,
            stdin=io.StringIO("are you there?\n/exit\n"),
            stdout=out,
            embed_client=_NullEmbed(),
            funi_opener=lambda _cfg: ExampleFuni(),
            strengr_opener=lambda *_a: disconnect,
        )
        print("--- what the operator saw ---")
        print(out.getvalue(), end="")

        journal = PendingJournal(pending_root(root))
        saved, corrupt = journal.load_all()
        print("--- while the Well was away ---")
        print(f"turns saved in the pending journal: {len(saved)}; damaged: {len(corrupt)}")
        diary_lines = Diary(diary_root(root)).read_recent(days=1)
        print(f"plain-words diary entries kept: {len(diary_lines)} (facts only, no words said)")

        well = FreshWell()
        drain = journal.drain(well)
        print("--- when the Well came back ---")
        print(f"turns added to the Well: {drain.flushed}; still saved locally: {drain.kept}")
        for ep in well.added:
            print(f"remembered: you said {ep.operator_input!r}")

    ok = rc == 0 and len(saved) == 1 and drain.flushed == 1 and drain.kept == 0
    print(f"offline_turns: {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
