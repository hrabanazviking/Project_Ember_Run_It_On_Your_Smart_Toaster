"""E-021 — Conversation engine hardening: history, windowing,
summarisation hooks under a token budget (profile-aware).

Pins, in the default (stdlib-only) environment shape:

- the profile-aware budget table + explicit overrides, loadable from
  an operator config file like every other section;
- the token estimator and the windowing rules (episode cap, token
  budget, newest episode always kept, dropped turns reported);
- the summarisation hook contract (default extractive hook invents
  nothing; a custom hook slots in; disabling works);
- prompt assembly placing the summary between system and episodes,
  and the Ollama adapter carrying it as a system message;
- the chat loop loading persisted history at startup (docket 81's
  reader half) and windowing it per turn.

The Well-backed reader itself is proven against the real sqlite_vec
adapter in ``test_episode_reader_e021.py`` (extras shape).
"""

from __future__ import annotations

import io
from dataclasses import replace
from pathlib import Path

from ember.config import load_ember_config
from ember.schemas.config import (
    ConversationConfig,
    ConversationProfile,
    EmberConfig,
)
from ember.schemas.episode import Episode
from ember.schemas.funi import ContextKind, FinishReason
from ember.schemas.stream import FuniStreamChunk
from ember.spark.funi import prompt as funi_prompt
from ember.spark.funi.ollama.adapter import _messages_from_context
from ember.spark.funi.windowing import (
    ExtractiveSummariser,
    episode_cost,
    estimate_tokens,
    window_history,
)
from ember.spark.munnr import chat


def _ep(op: str, em: str) -> Episode:
    return Episode(operator_input=op, ember_reply=em)


# --------------------------------------------------------------------- #
# Profile-aware budgets                                                  #
# --------------------------------------------------------------------- #


def test_profile_budget_table_is_monotonic_and_tiny_first() -> None:
    budgets = [
        ConversationConfig(profile=p).resolved_token_budget
        for p in ConversationProfile
    ]
    caps = [
        ConversationConfig(profile=p).resolved_max_episodes
        for p in ConversationProfile
    ]
    # The toaster is the smallest; budgets never shrink as the
    # machine class grows.
    assert budgets == sorted(budgets)
    assert caps == sorted(caps)
    assert ConversationConfig(
        profile=ConversationProfile.TOASTER
    ).resolved_token_budget == 512
    assert ConversationConfig().profile is ConversationProfile.PI


def test_explicit_overrides_beat_profile_defaults() -> None:
    cfg = ConversationConfig(
        profile=ConversationProfile.TOASTER, token_budget=99, max_episodes=2
    )
    assert cfg.resolved_token_budget == 99
    assert cfg.resolved_max_episodes == 2


def test_conversation_section_loads_from_operator_config(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "ember.toml").write_text(
        "[conversation]\nprofile = 'toaster'\ntoken_budget = 700\n",
        encoding="utf-8",
    )
    cfg = load_ember_config(tmp_path, skip_env=True)
    assert cfg.conversation.profile is ConversationProfile.TOASTER
    assert cfg.conversation.resolved_token_budget == 700
    # An empty root yields the pure defaults.
    empty = tmp_path / "empty"
    empty.mkdir()
    assert load_ember_config(empty, skip_env=True).conversation == (
        ConversationConfig()
    )


# --------------------------------------------------------------------- #
# Estimator + windowing                                                  #
# --------------------------------------------------------------------- #


def test_estimate_tokens_is_a_cheap_deterministic_guardrail() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcde") == 2
    assert episode_cost(_ep("aaaa", "bbbb")) == 2


def test_window_keeps_everything_when_it_fits() -> None:
    eps = [_ep("one", "1"), _ep("two", "2")]
    result = window_history(eps, ConversationConfig())
    assert result.episodes == tuple(eps)
    assert result.dropped == ()
    assert result.summary is None
    assert result.estimated_tokens == sum(episode_cost(e) for e in eps)


def test_window_episode_cap_drops_oldest_and_summarises() -> None:
    eps = [_ep(f"question {i}", f"answer {i}") for i in range(6)]
    cfg = ConversationConfig(token_budget=100_000, max_episodes=3)
    result = window_history(eps, cfg)
    assert result.episodes == tuple(eps[-3:])
    assert result.dropped == tuple(eps[:3])
    assert result.summary is not None
    assert "3 earlier turn(s)" in result.summary
    assert "question 0" in result.summary


def test_window_token_budget_drops_oldest_first() -> None:
    small = _ep("aa", "bb")  # cost 2
    big = _ep("x" * 40, "y" * 40)  # cost 20
    cfg = ConversationConfig(token_budget=22, max_episodes=50)
    result = window_history([big, small, small], cfg)
    # Newest two fit (2 + 2 <= 22 after keeping newest-first: the two
    # small ones cost 4; adding big would reach 24 > 22).
    assert result.episodes == (small, small)
    assert result.dropped == (big,)


def test_window_always_keeps_the_newest_episode() -> None:
    huge = _ep("x" * 400, "y" * 400)  # cost 200, over any tiny budget
    cfg = ConversationConfig(
        profile=ConversationProfile.TOASTER, token_budget=10
    )
    result = window_history([huge], cfg)
    assert result.episodes == (huge,)
    assert result.dropped == ()
    assert result.estimated_tokens == 200


def test_window_summarisation_can_be_disabled() -> None:
    eps = [_ep(f"q{i}", f"a{i}") for i in range(4)]
    cfg = ConversationConfig(
        token_budget=100_000, max_episodes=1, summarise_dropped=False
    )
    result = window_history(eps, cfg)
    assert len(result.dropped) == 3
    assert result.summary is None


def test_window_custom_summariser_hook_slots_in() -> None:
    class FixedHook:
        def summarise(self, episodes) -> str:
            return f"hook saw {len(episodes)}"

    eps = [_ep(f"q{i}", f"a{i}") for i in range(3)]
    cfg = ConversationConfig(token_budget=100_000, max_episodes=1)
    result = window_history(eps, cfg, summariser=FixedHook())
    assert result.summary == "hook saw 2"


def test_extractive_summariser_invents_nothing() -> None:
    eps = [_ep("what is odin", "a god"), _ep("and thor", "his son")]
    text = ExtractiveSummariser().summarise(eps)
    assert "2 earlier turn(s)" in text
    assert "what is odin" in text
    assert "his son" in text
    assert ExtractiveSummariser().summarise(()) == ""


# --------------------------------------------------------------------- #
# Prompt assembly + adapter carriage                                     #
# --------------------------------------------------------------------- #


def test_prompt_places_summary_between_system_and_episodes() -> None:
    from ember.schemas.config import IdentityConfig

    items = funi_prompt.assemble(
        identity=IdentityConfig(),
        episodes=[_ep("q", "a")],
        summary="Summary of 2 earlier turn(s)",
    )
    kinds = [item.kind for item in items]
    assert kinds == [ContextKind.SYSTEM, ContextKind.SUMMARY, ContextKind.EPISODE]
    # No summary -> no summary item (the pre-E-021 shape).
    items = funi_prompt.assemble(identity=IdentityConfig(), episodes=[_ep("q", "a")])
    assert [item.kind for item in items] == [ContextKind.SYSTEM, ContextKind.EPISODE]


def test_ollama_adapter_carries_summary_as_system_message() -> None:
    from ember.schemas.config import IdentityConfig

    items = funi_prompt.assemble(
        identity=IdentityConfig(), summary="earlier: stuff happened"
    )
    messages = _messages_from_context(items, "now?")
    assert {"role": "system", "content": "earlier: stuff happened"} in messages


# --------------------------------------------------------------------- #
# Chat loop: history survives a restart, windowed per turn               #
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


def _run_chat(tmp_path: Path, brunnr: _FakeBrunnr, funi: _FakeFuni,
              config: EmberConfig) -> int:
    return chat.run(
        config=config,
        config_root=tmp_path,
        stdin=io.StringIO("hello again\n/exit\n"),
        stdout=io.StringIO(),
        embed_client=_NullEmbed(),
        funi_opener=lambda _cfg: funi,
        strengr_opener=lambda *_a: brunnr,
    )


def test_chat_loads_persisted_history_at_startup(tmp_path: Path) -> None:
    stored = [_ep("first question", "first answer"),
              _ep("second question", "second answer")]
    brunnr = _FakeBrunnr(stored)
    funi = _FakeFuni()
    rc = _run_chat(tmp_path, brunnr, funi, EmberConfig())
    assert rc == 0
    kinds = [item.kind for item in funi.contexts[0]]
    assert kinds.count(ContextKind.EPISODE) == 2
    episode_texts = [
        item.text for item in funi.contexts[0]
        if item.kind is ContextKind.EPISODE
    ]
    assert any("first question" in t for t in episode_texts)
    # The new turn was persisted through the same handle.
    assert len(brunnr.added) == 1
    assert brunnr.added[0].operator_input == "hello again"


def test_chat_windows_loaded_history_under_tiny_budget(
    tmp_path: Path,
) -> None:
    stored = [_ep("old " + "x" * 200, "old reply " + "y" * 200)
              for _ in range(4)]
    brunnr = _FakeBrunnr(stored)
    funi = _FakeFuni()
    config = replace(
        EmberConfig(),
        conversation=ConversationConfig(
            profile=ConversationProfile.TOASTER, token_budget=60,
            max_episodes=50,
        ),
    )
    rc = _run_chat(tmp_path, brunnr, funi, config)
    assert rc == 0
    kinds = [item.kind for item in funi.contexts[0]]
    # Some history dropped -> a summary rides; at least the newest
    # episode is still verbatim.
    assert ContextKind.SUMMARY in kinds
    assert ContextKind.EPISODE in kinds
