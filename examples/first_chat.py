"""Example 1 — a first chat with Ember, end to end.

Run it (from the repo root, no optional extras needed):

    PYTHONPATH=src python3 examples/first_chat.py

What this shows: the real conversation loop (`ember chat`'s own
`run()`) taking one typed line, streaming a reply, and remembering
the turn — exactly the turn `docs/architecture/DATA_FLOW.md` §2
draws. Two stand-ins keep the example runnable on any machine,
and both are labelled, never hidden:

- the *model* is a small fake that always answers with the same
  sentence. A real chat talks to a local model program (Ollama
  by default); the loop around it is the real one.
- the *memory store* (the Well) is a small in-memory stand-in
  with no files inside. A real chat uses the sqlite Well on disk;
  the handle shape it answers to is the real one.

Everything the session writes for real — its plain-words diary —
lands in a temporary folder that is removed when the example
ends, so running this never touches your own Ember folder.
"""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

# Allow running straight from a source checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ember.schemas.config import EmberConfig  # noqa: E402
from ember.schemas.episode import Episode  # noqa: E402
from ember.schemas.stream import FuniStreamChunk  # noqa: E402
from ember.schemas.funi import FinishReason  # noqa: E402
from ember.spark.munnr import chat  # noqa: E402

REPLY = "Hello! I am Ember, your small local companion."


class ExampleFuni:
    """A fake model: streams one fixed reply, in two pieces."""

    runtime_kind = "fake"
    model_id = "fake:tiny"

    def complete_streaming(self, prompt, context, tools=None):
        yield FuniStreamChunk(text_delta=REPLY[:20], done=False)
        yield FuniStreamChunk(
            text_delta=REPLY[20:],
            done=True,
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
        )

    def close(self) -> None:
        return None


class ExampleWell:
    """An in-memory memory store with the Well handle's shape."""

    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self) -> None:
        self._episodes: list[Episode] = []

    def recent_episodes(self, limit: int) -> list[Episode]:
        return list(self._episodes[-limit:] if limit > 0 else [])

    def add_episode(self, episode: Episode) -> int:
        self._episodes.append(episode)
        return len(self._episodes)

    def text_search(self, query: str, k: int, filter=None):  # noqa: A002
        return []

    def hybrid_search(self, qvec, query: str, k: int):
        return []

    def close(self) -> None:
        return None


class _NullEmbed:
    """No embedding model in the example: retrieval stays text-only."""

    def embed(self, texts):
        return [None for _ in texts]


def main() -> int:
    well = ExampleWell()
    with tempfile.TemporaryDirectory(prefix="ember-example-") as tmp:
        out = io.StringIO()
        rc = chat.run(
            config=EmberConfig(),
            config_root=Path(tmp),
            stdin=io.StringIO("hello ember\n/exit\n"),
            stdout=out,
            embed_client=_NullEmbed(),
            funi_opener=lambda _cfg: ExampleFuni(),
            strengr_opener=lambda *_a: well,
        )
        transcript = out.getvalue()

    print("--- what the operator saw ---")
    print(transcript, end="")
    print("--- what Ember remembers ---")
    remembered = well.recent_episodes(5)
    for ep in remembered:
        print(f"you: {ep.operator_input}")
        print(f"ember: {ep.ember_reply}")
    print(f"first_chat: exit {rc}, {len(remembered)} turn(s) remembered")
    return 0 if rc == 0 and len(remembered) == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
