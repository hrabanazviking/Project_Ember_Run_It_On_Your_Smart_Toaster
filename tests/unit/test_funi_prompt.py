"""Shape contracts for the runtime-neutral prompt assembler."""

from __future__ import annotations

from ember.schemas.chunks import RetrievalHit
from ember.schemas.config import IdentityConfig
from ember.schemas.episode import Episode
from ember.schemas.funi import ContextKind
from ember.spark.funi.prompt import assemble

_DEFAULT_IDENTITY = IdentityConfig()


def test_assemble_with_no_inputs_produces_just_a_system_item() -> None:
    items = assemble(identity=_DEFAULT_IDENTITY)
    assert len(items) == 1
    assert items[0].kind is ContextKind.SYSTEM
    assert "Ember" in items[0].text


def test_assemble_order_is_system_then_episodes_then_hits() -> None:
    items = assemble(
        identity=_DEFAULT_IDENTITY,
        episodes=[
            Episode(operator_input="a", ember_reply="A"),
            Episode(operator_input="b", ember_reply="B"),
        ],
        hits=[
            RetrievalHit(chunk_id=1, document_id=1, document_title="X", text="x", score=0.9),
            RetrievalHit(chunk_id=2, document_id=2, document_title="Y", text="y", score=0.8),
        ],
    )
    kinds = [item.kind for item in items]
    assert kinds == [
        ContextKind.SYSTEM,
        ContextKind.EPISODE,
        ContextKind.EPISODE,
        ContextKind.CHUNK,
        ContextKind.CHUNK,
    ]


def test_system_prompt_includes_honesty_instruction() -> None:
    items = assemble(identity=_DEFAULT_IDENTITY)
    assert "honestly" in items[0].text.lower() or "honest" in items[0].text.lower()


def test_system_prompt_changes_when_well_is_disconnected() -> None:
    grounded = assemble(
        identity=_DEFAULT_IDENTITY,
        hits=[RetrievalHit(chunk_id=1, document_id=1, document_title="X", text="x", score=0.5)],
    )
    disconnected = assemble(
        identity=_DEFAULT_IDENTITY,
        hits=[RetrievalHit(chunk_id=1, document_id=1, document_title="X", text="x", score=0.5)],
        well_disconnected=True,
    )
    assert "well" in disconnected[0].text.lower()
    assert "unreachable" in disconnected[0].text.lower()
    assert disconnected[0].text != grounded[0].text


def test_episode_item_text_round_trips_operator_and_ember_lines() -> None:
    items = assemble(
        identity=_DEFAULT_IDENTITY,
        episodes=[Episode(operator_input="who?", ember_reply="me!")],
    )
    episode_items = [i for i in items if i.kind is ContextKind.EPISODE]
    assert len(episode_items) == 1
    text = episode_items[0].text
    assert "Operator: who?" in text
    assert "Ember: me!" in text


def test_hit_item_metadata_carries_chunk_and_score() -> None:
    hit = RetrievalHit(
        chunk_id=42, document_id=7, document_title="Saga", text="...", score=0.71
    )
    items = assemble(identity=_DEFAULT_IDENTITY, hits=[hit])
    chunk_items = [i for i in items if i.kind is ContextKind.CHUNK]
    assert len(chunk_items) == 1
    md = chunk_items[0].metadata
    assert md["chunk_id"] == 42
    assert md["document_id"] == 7
    assert abs(float(md["score"]) - 0.71) < 1e-9


def test_hit_item_text_includes_document_title() -> None:
    items = assemble(
        identity=_DEFAULT_IDENTITY,
        hits=[
            RetrievalHit(
                chunk_id=1, document_id=1, document_title="The Saga of Runa",
                text="Runa rides through the worlds.", score=0.9,
            )
        ],
    )
    chunk_text = next(i.text for i in items if i.kind is ContextKind.CHUNK)
    assert "The Saga of Runa" in chunk_text
    assert "Runa rides" in chunk_text


def test_hit_with_no_title_uses_untitled_placeholder() -> None:
    items = assemble(
        identity=_DEFAULT_IDENTITY,
        hits=[
            RetrievalHit(
                chunk_id=1, document_id=1, document_title=None,
                text="...", score=0.5,
            )
        ],
    )
    chunk_text = next(i.text for i in items if i.kind is ContextKind.CHUNK)
    assert "untitled" in chunk_text.lower()
