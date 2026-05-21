"""Shape contracts for ``ember.schemas.funi``."""

from __future__ import annotations

import dataclasses

import pytest

from ember.schemas.funi import (
    ContextItem,
    ContextKind,
    FinishReason,
    FuniHealth,
    FuniReply,
    ToolCall,
    Unavailable,
    UnavailableReason,
)

# --------------------------------------------------------------------- #
# Context                                                                #
# --------------------------------------------------------------------- #


def test_context_item_minimal_construction() -> None:
    ctx = ContextItem(kind=ContextKind.SYSTEM, text="you are Ember")
    assert ctx.metadata == {}


def test_context_kinds_cover_the_documented_sources() -> None:
    # Per DATA_FLOW.md §2.1 step 6: Munnr assembles system prompt +
    # last N episodes + retrieved chunks. Phase 16 (ADR 0011) added
    # ``tool_reply`` so executed tool replies fold back into the next
    # turn's context.
    expected = {"episode", "chunk", "system", "tool_reply"}
    actual = {kind.value for kind in ContextKind}
    assert actual == expected


# --------------------------------------------------------------------- #
# FuniReply                                                              #
# --------------------------------------------------------------------- #


def test_funi_reply_minimal_construction() -> None:
    reply = FuniReply(text="hello", finish_reason=FinishReason.STOP)
    assert reply.tool_calls == ()
    assert reply.prompt_tokens is None
    assert reply.completion_tokens is None


def test_funi_reply_is_frozen() -> None:
    reply = FuniReply(text="hello", finish_reason=FinishReason.STOP)
    with pytest.raises(dataclasses.FrozenInstanceError):
        reply.text = "tampered"  # type: ignore[misc]


def test_funi_reply_finish_reasons_include_refused() -> None:
    # Vow of Honest Memory: Funi must be able to refuse cleanly when she
    # cannot answer truthfully. REFUSED is a load-bearing finish reason.
    assert "refused" in {fr.value for fr in FinishReason}


def test_tool_call_holds_call_id_name_and_arguments() -> None:
    # Phase 14 (ADR 0011 §2.1) promoted ToolCall to ember.schemas.tool
    # and added the join-key ``call_id``. The funi.py re-export still
    # works, so this test continues to use the historical import path.
    call = ToolCall(
        call_id="abc-123", name="search_well", arguments={"query": "Odin"},
    )
    assert call.call_id == "abc-123"
    assert call.name == "search_well"
    assert call.arguments["query"] == "Odin"


# --------------------------------------------------------------------- #
# FuniHealth                                                             #
# --------------------------------------------------------------------- #


def test_funi_health_minimal_construction() -> None:
    h = FuniHealth(model_id="phi3:mini")
    assert h.ram_use_bytes is None
    assert h.last_ok is None


# --------------------------------------------------------------------- #
# Unavailable — non-raised failure value                                 #
# --------------------------------------------------------------------- #


def test_unavailable_is_a_value_not_an_exception() -> None:
    assert not issubclass(Unavailable, BaseException)


def test_unavailable_is_frozen() -> None:
    u = Unavailable(reason=UnavailableReason.NOT_LOADED)
    with pytest.raises(dataclasses.FrozenInstanceError):
        u.detail = "tampered"  # type: ignore[misc]


def test_all_unavailable_reasons_are_lower_string_valued() -> None:
    for member in UnavailableReason:
        assert isinstance(member.value, str)
        assert member.value == member.value.lower()


def test_unavailable_reasons_include_oom_and_endpoint_unreachable() -> None:
    # These two are the cases Hjarta and `ember doctor` distinguish to
    # produce useful operator-facing messages.
    values = {u.value for u in UnavailableReason}
    assert "out_of_memory" in values
    assert "endpoint_unreachable" in values
