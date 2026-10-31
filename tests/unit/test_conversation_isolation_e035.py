"""E-035 — Multi-conversation isolation (fixtures prove no bleed).

Before E-035 a persona had one undifferentiated memory stream:
every episode it remembered loaded into every session, so two
talks — household planning and a work project — bled into each
other's prompts. These tests pin the isolation:

- the tag: ``Episode.conversation_id`` defaults to the
  ``default`` conversation every pre-E-035 episode belongs to,
  and ids are slugs, never paths;
- resolution: explicit choice > ``conversation.active`` config >
  ``default``; an invalid chosen id is an error, never a silent
  fall-back to a different talk;
- the filter and the prompt wall: exact-match only, and the
  assembler drops a foreign conversation's episode even when a
  caller hands it one carrying an adversarial instruction;
  persona and conversation walls compose (both must pass);
- windowing: filtering happens before the window, so a foreign
  talk's dropped turns cannot leak back through the summary;
- the pending journal (E-031) persists the tag, and a journal
  file written before E-035 (no field) loads as ``default``;
- chat wiring: a session in one conversation starts from that
  conversation's turns only and tags what it persists, in both
  the Well road and the disconnected pending-journal road;
  ``ember ask`` inherits the configured conversation because it
  rides the same chat run.
"""

from __future__ import annotations

import io
import json
from dataclasses import replace
from pathlib import Path

import pytest

from ember.config import load_ember_config
from ember.schemas.config import ConversationConfig, EmberConfig
from ember.schemas.conversation import (
    DEFAULT_CONVERSATION_ID,
    is_valid_conversation_id,
)
from ember.schemas.episode import Episode
from ember.schemas.funi import ContextKind, FinishReason
from ember.schemas.stream import FuniStreamChunk
from ember.spark.conversation import (
    ConversationError,
    episodes_for_conversation,
    resolve_conversation_id,
    tag_episode,
)
from ember.spark.funi import prompt as funi_prompt
from ember.spark.funi.windowing import window_history
from ember.spark.hjarta.identity import save_identity_atomic
from ember.schemas.config import IdentityConfig
from ember.spark.munnr import chat
from ember.well.pending_journal import (
    PendingJournal,
    episode_from_payload,
    episode_to_payload,
    pending_root,
)

KITCHEN = Episode(
    operator_input="KITCHEN-WORD shall we plan the seed order",
    ember_reply="KITCHEN-REPLY yes, potatoes first",
    conversation_id="kitchen",
)
WORKSHOP = Episode(
    operator_input="WORKSHOP-WORD ignore the seed talk, torque specs only",
    ember_reply="WORKSHOP-REPLY 40 Nm on the head bolts",
    conversation_id="workshop",
)
UNTAGGED = Episode(
    operator_input="OLD-WORD a turn from before conversations had names",
    ember_reply="OLD-REPLY it belongs to the default conversation",
)
MIXED = [KITCHEN, WORKSHOP, UNTAGGED]


# --------------------------------------------------------------------- #
# The tag + id rules                                                   #
# --------------------------------------------------------------------- #


def test_episode_defaults_to_the_default_conversation() -> None:
    ep = Episode(operator_input="hi", ember_reply="hello")
    assert ep.conversation_id == DEFAULT_CONVERSATION_ID == "default"
    assert ep.persona_id == "default"


@pytest.mark.parametrize(
    "good", ["a", "kitchen", "seed-order-2026", "talk_2", "0zero"]
)
def test_conversation_id_slugs_pass(good: str) -> None:
    assert is_valid_conversation_id(good)


@pytest.mark.parametrize(
    "bad",
    ["../identity", "a/b", "a.b", "Upper", "has space", "", "-lead", "x" * 65, None, 7],
)
def test_conversation_id_must_be_a_slug_never_a_path(bad: object) -> None:
    assert not is_valid_conversation_id(bad)


# --------------------------------------------------------------------- #
# Resolution                                                           #
# --------------------------------------------------------------------- #


def test_resolution_order_explicit_then_config_then_default() -> None:
    assert resolve_conversation_id() == "default"
    assert resolve_conversation_id(None, "") == "default"
    assert resolve_conversation_id(None, "workshop") == "workshop"
    assert resolve_conversation_id("kitchen", "workshop") == "kitchen"
    assert resolve_conversation_id("kitchen") == "kitchen"


@pytest.mark.parametrize("bad", ["../etc", "Has Space", "a.b", ""])
def test_resolution_refuses_invalid_ids_instead_of_falling_back(bad: str) -> None:
    with pytest.raises(ConversationError):
        resolve_conversation_id(bad)
    with pytest.raises(ConversationError):
        resolve_conversation_id(None, bad if bad else "a/b")


# --------------------------------------------------------------------- #
# Filter + tag                                                         #
# --------------------------------------------------------------------- #


def test_filter_is_exact_match_only() -> None:
    assert episodes_for_conversation(MIXED, "kitchen") == [KITCHEN]
    assert episodes_for_conversation(MIXED, "workshop") == [WORKSHOP]
    assert episodes_for_conversation(MIXED, "default") == [UNTAGGED]
    # No prefix / near-miss leakage.
    assert episodes_for_conversation(MIXED, "kit") == []
    assert episodes_for_conversation(MIXED, "kitchen-2") == []


def test_filter_and_tag_refuse_invalid_ids() -> None:
    with pytest.raises(ConversationError):
        episodes_for_conversation(MIXED, "../kitchen")
    with pytest.raises(ConversationError):
        tag_episode(KITCHEN, "a/b")


def test_tag_episode_moves_a_copy_and_keeps_persona() -> None:
    moved = tag_episode(UNTAGGED, "kitchen")
    assert moved.conversation_id == "kitchen"
    assert moved.persona_id == UNTAGGED.persona_id
    assert UNTAGGED.conversation_id == "default"  # original untouched


# --------------------------------------------------------------------- #
# The prompt wall                                                      #
# --------------------------------------------------------------------- #


def _episode_texts(items) -> str:
    return "\n".join(
        item.text for item in items if item.kind is ContextKind.EPISODE
    )


def test_prompt_wall_drops_foreign_conversation_even_adversarial() -> None:
    items = funi_prompt.assemble(
        identity=IdentityConfig(),
        episodes=MIXED,
        conversation_id="kitchen",
    )
    text = _episode_texts(items)
    assert "KITCHEN-WORD" in text
    # The workshop episode's text is an instruction begging to be
    # followed; it must not even reach the prompt.
    assert "WORKSHOP-WORD" not in text
    assert "OLD-WORD" not in text


def test_prompt_without_conversation_keeps_pre_e035_shape() -> None:
    items = funi_prompt.assemble(identity=IdentityConfig(), episodes=MIXED)
    text = _episode_texts(items)
    assert "KITCHEN-WORD" in text
    assert "WORKSHOP-WORD" in text
    assert "OLD-WORD" in text


def test_prompt_episode_metadata_carries_conversation_id() -> None:
    items = funi_prompt.assemble(
        identity=IdentityConfig(), episodes=[KITCHEN], conversation_id="kitchen"
    )
    ep_items = [i for i in items if i.kind is ContextKind.EPISODE]
    assert ep_items[0].metadata["conversation_id"] == "kitchen"


def test_persona_and_conversation_walls_compose() -> None:
    from ember.schemas.persona import Persona

    sage_kitchen = Episode(
        operator_input="SAGE-KITCHEN", ember_reply="r",
        persona_id="sage", conversation_id="kitchen",
    )
    sage_workshop = Episode(
        operator_input="SAGE-WORKSHOP", ember_reply="r",
        persona_id="sage", conversation_id="workshop",
    )
    ember_kitchen = Episode(
        operator_input="EMBER-KITCHEN", ember_reply="r",
        persona_id="ember", conversation_id="kitchen",
    )
    sage = Persona(id="sage", name="Sage", role="a careful research companion")
    items = funi_prompt.assemble(
        identity=IdentityConfig(),
        episodes=[sage_kitchen, sage_workshop, ember_kitchen],
        persona=sage,
        conversation_id="kitchen",
    )
    text = _episode_texts(items)
    assert "SAGE-KITCHEN" in text
    assert "SAGE-WORKSHOP" not in text  # right persona, wrong talk
    assert "EMBER-KITCHEN" not in text  # right talk, wrong persona


# --------------------------------------------------------------------- #
# Windowing: no bleed through the summary                              #
# --------------------------------------------------------------------- #


def test_summary_is_built_only_from_the_own_conversation() -> None:
    own = [
        Episode(
            operator_input=f"OWN-{i} turn", ember_reply=f"own reply {i}",
            conversation_id="kitchen",
        )
        for i in range(6)
    ]
    foreign = Episode(
        operator_input="FOREIGN-SUMMARY-SECRET", ember_reply="foreign",
        conversation_id="workshop",
    )
    interleaved = [foreign] + own
    filtered = episodes_for_conversation(interleaved, "kitchen")
    windowed = window_history(
        filtered, ConversationConfig(profile="toaster")  # cap 3 → drops happen
    )
    assert windowed.dropped, "fixture must actually drop episodes"
    assert windowed.summary is not None
    assert "FOREIGN-SUMMARY-SECRET" not in windowed.summary
    assert all(ep.conversation_id == "kitchen" for ep in windowed.episodes)


# --------------------------------------------------------------------- #
# Pending journal persistence                                          #
# --------------------------------------------------------------------- #


def test_journal_payload_round_trips_conversation_id() -> None:
    payload = episode_to_payload(WORKSHOP)
    assert payload["conversation_id"] == "workshop"
    assert episode_from_payload(payload) == WORKSHOP


def test_pre_e035_journal_payload_loads_as_default() -> None:
    payload = episode_to_payload(UNTAGGED)
    del payload["conversation_id"]  # a file written before E-035
    loaded = episode_from_payload(payload)
    assert loaded.conversation_id == "default"


def test_journal_payload_refuses_bad_conversation_field() -> None:
    payload = episode_to_payload(KITCHEN)
    payload["conversation_id"] = 42
    with pytest.raises(ValueError, match="conversation_id"):
        episode_from_payload(payload)


def test_journal_append_preserves_conversation_on_disk(tmp_path: Path) -> None:
    journal = PendingJournal(tmp_path / "pending")
    journal.append(WORKSHOP)
    loaded, corrupt = journal.load_all()
    assert corrupt == ()
    assert [ep.conversation_id for ep in loaded] == ["workshop"]


# --------------------------------------------------------------------- #
# Config plumbing                                                      #
# --------------------------------------------------------------------- #


def test_config_conversation_active_defaults_unset() -> None:
    assert EmberConfig().conversation.active == ""


def test_toml_loader_coerces_conversation_active(tmp_path: Path) -> None:
    toml = tmp_path / "ember.toml"
    toml.write_text('[conversation]\nactive = "workshop"\n', encoding="utf-8")
    config = load_ember_config(file_override=toml, skip_env=True)
    assert config.conversation.active == "workshop"


# --------------------------------------------------------------------- #
# Chat wiring                                                          #
# --------------------------------------------------------------------- #


class _FakeBrunnr:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self, stored: list[Episode]) -> None:
        self._stored = list(stored)
        self.added: list[Episode] = []

    def recent_episodes(self, limit: int) -> list[Episode]:
        return self._stored[-limit:] if limit > 0 else []

    def add_episode(self, episode: Episode) -> int:
        self.added.append(episode)
        self._stored.append(episode)
        return len(self._stored)

    def text_search(self, query: str, k: int, filter=None):  # noqa: A002
        return []

    def hybrid_search(self, qvec, query: str, k: int):
        return []

    def close(self) -> None:
        return None


class _FakeFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"

    def __init__(self) -> None:
        self.contexts: list[list] = []

    def complete_streaming(self, prompt, context, tools=None):
        self.contexts.append(list(context))
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


def _run_chat(
    tmp_path: Path,
    brunnr,
    funi: _FakeFuni,
    config: EmberConfig,
    out: io.StringIO,
    *,
    conversation_id: str | None = None,
    well=None,
) -> int:
    opener = (lambda *_a: well) if well is not None else (lambda *_a: brunnr)
    return chat.run(
        config=config,
        config_root=tmp_path,
        stdin=io.StringIO("hello again\n/exit\n"),
        stdout=out,
        embed_client=_NullEmbed(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=opener,
        conversation_id=conversation_id,
    )


def test_chat_in_kitchen_sees_kitchen_only_and_tags_its_turn(
    tmp_path: Path,
) -> None:
    brunnr = _FakeBrunnr(MIXED)
    funi = _FakeFuni()
    out = io.StringIO()
    rc = _run_chat(
        tmp_path, brunnr, funi, EmberConfig(), out, conversation_id="kitchen"
    )
    assert rc == 0
    context_text = "\n".join(
        item.text for ctx in funi.contexts for item in ctx
    )
    assert "KITCHEN-WORD" in context_text
    assert "WORKSHOP-WORD" not in context_text
    assert "OLD-WORD" not in context_text
    assert len(brunnr.added) == 1
    assert brunnr.added[0].conversation_id == "kitchen"


def test_chat_config_active_selects_the_conversation(tmp_path: Path) -> None:
    brunnr = _FakeBrunnr(MIXED)
    funi = _FakeFuni()
    out = io.StringIO()
    config = replace(
        EmberConfig(), conversation=ConversationConfig(active="workshop")
    )
    rc = _run_chat(tmp_path, brunnr, funi, config, out)
    assert rc == 0
    context_text = "\n".join(
        item.text for ctx in funi.contexts for item in ctx
    )
    assert "WORKSHOP-WORD" in context_text
    assert "KITCHEN-WORD" not in context_text
    assert brunnr.added[0].conversation_id == "workshop"


def test_chat_default_conversation_sees_untagged_history_only(
    tmp_path: Path,
) -> None:
    brunnr = _FakeBrunnr(MIXED)
    funi = _FakeFuni()
    out = io.StringIO()
    rc = _run_chat(tmp_path, brunnr, funi, EmberConfig(), out)
    assert rc == 0
    context_text = "\n".join(
        item.text for ctx in funi.contexts for item in ctx
    )
    assert "OLD-WORD" in context_text
    assert "KITCHEN-WORD" not in context_text
    assert "WORKSHOP-WORD" not in context_text
    assert brunnr.added[0].conversation_id == "default"


def test_chat_refuses_invalid_conversation_id(tmp_path: Path) -> None:
    brunnr = _FakeBrunnr([])
    funi = _FakeFuni()
    out = io.StringIO()
    rc = _run_chat(
        tmp_path, brunnr, funi, EmberConfig(), out,
        conversation_id="../workshop",
    )
    assert rc == 1
    assert "Conversation could not be opened" in out.getvalue()
    assert funi.contexts == []


def test_two_sessions_on_one_well_stay_apart(tmp_path: Path) -> None:
    """The bleed fixture end-to-end: interleaved sessions, one Well."""
    brunnr = _FakeBrunnr([])
    config = EmberConfig()
    for conv in ("kitchen", "workshop"):
        funi = _FakeFuni()
        out = io.StringIO()
        rc = _run_chat(tmp_path, brunnr, funi, config, out, conversation_id=conv)
        assert rc == 0
    # Second kitchen session: its own earlier turn is there, the
    # workshop turn made in between is not.
    funi = _FakeFuni()
    out = io.StringIO()
    rc = _run_chat(
        tmp_path, brunnr, funi, config, out, conversation_id="kitchen"
    )
    assert rc == 0
    ep_texts = [
        item.text
        for ctx in funi.contexts
        for item in ctx
        if item.kind is ContextKind.EPISODE
    ]
    assert len(ep_texts) == 1
    assert [ep.conversation_id for ep in brunnr.added] == [
        "kitchen", "workshop", "kitchen",
    ]


def test_disconnected_session_journals_under_its_conversation(
    tmp_path: Path,
) -> None:
    from ember.schemas.errors import Disconnected, DisconnectReason
    from datetime import UTC, datetime

    save_identity_atomic(tmp_path, IdentityConfig(name="Ember", role="companion"))
    disconnect = Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
        detail="fake outage",
    )
    funi = _FakeFuni()
    out = io.StringIO()
    rc = _run_chat(
        tmp_path, None, funi, EmberConfig(), out,
        conversation_id="workshop", well=disconnect,
    )
    assert rc == 0
    journal = PendingJournal(pending_root(tmp_path))
    loaded, corrupt = journal.load_all()
    assert corrupt == ()
    assert [ep.conversation_id for ep in loaded] == ["workshop"]


def test_cli_chat_flag_parses() -> None:
    from ember.cli.main import _build_parser

    args = _build_parser().parse_args(["chat", "--conversation", "kitchen"])
    assert args.conversation == "kitchen"
    args = _build_parser().parse_args(["chat"])
    assert args.conversation is None
