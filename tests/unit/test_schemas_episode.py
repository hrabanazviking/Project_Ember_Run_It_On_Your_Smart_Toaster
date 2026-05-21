"""Shape contracts for ``ember.schemas.episode``."""

from __future__ import annotations

import dataclasses

import pytest

from ember.schemas.episode import Episode


def test_episode_minimal_construction() -> None:
    ep = Episode(operator_input="hi", ember_reply="hello")
    assert ep.cited_chunk_ids == ()
    assert ep.well_disconnected is False
    assert ep.id is None


def test_episode_is_frozen() -> None:
    ep = Episode(operator_input="hi", ember_reply="hello")
    with pytest.raises(dataclasses.FrozenInstanceError):
        ep.ember_reply = "tampered"  # type: ignore[misc]


def test_episode_records_disconnect_flag() -> None:
    # Per docs/architecture/DATA_FLOW.md §2.2: when the Well is
    # unreachable, the Episode records that fact, and Munnr writes it
    # to a local pending-episodes journal.
    ep = Episode(
        operator_input="hi",
        ember_reply="I don't have grounding right now.",
        well_disconnected=True,
    )
    assert ep.well_disconnected is True


def test_episode_cited_chunk_ids_is_tuple() -> None:
    ep = Episode(
        operator_input="who is Odin?",
        ember_reply="Odin is …",
        cited_chunk_ids=(1, 2, 3),
    )
    assert isinstance(ep.cited_chunk_ids, tuple)
