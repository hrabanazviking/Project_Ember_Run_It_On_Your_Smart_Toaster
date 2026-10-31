"""E-024 — ThoughtForge binding (candidate).

MindSpark ThoughtForge as Ember's cognition layer, bound against
the contract ThoughtForge froze at its TF-034 (cognition API
v1.0.0). These tests pin, with a fake ThoughtForge package shaped
from that freeze (TF-161's pattern — the real neighbour needn't be
present, and in the default env is not installed):

- registry truth: thoughtforge implemented against API major 1,
  afforded on phone/pi/laptop, NOT on the toaster;
- refusal order in open_cognition: disabled → profile cannot
  afford → unknown provider → provider not installed, each a typed
  CognitionUnavailable, never a raise;
- profile caps: toaster None, phone 1, pi 1, laptop 2; an explicit
  num_drafts wins; a cap below 1 is refused as CONFIG_INVALID;
- version refusal: a live package on API major 2, an unversioned
  package, and a package whose verify_api_surface() reports drift
  each get VERSION_MISMATCH — never silent adaptation;
- construction custody: the core is built with Ember's memory_dir /
  db_path expanded, tf_config passed through as a plain dict,
  model_path None unless the operator set one;
- think(): episodes become a ThoughtForge ChatHistory built with
  ThoughtForge's own classes (user/assistant per episode, in
  order); the frozen think signature is called with num_drafts +
  history; the FinalResponseRecord maps straight onto
  CognitionReply; a core exception folds into an ERROR-shaped
  reply, never a raise;
- config plumbing: defaults (disabled, inside ~/.ember) + TOML
  loader coercion for the ``cognition`` section;
- no core dependency: importing Ember's cognition modules does not
  import thoughtforge.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any

from ember.config import load_ember_config
from ember.schemas.cognition import (
    CognitionHealth,
    CognitionReply,
    CognitionUnavailable,
    CognitionUnavailableReason,
)
from ember.schemas.config import (
    CognitionConfig,
    ConversationProfile,
    EmberConfig,
)
from ember.schemas.episode import Episode
from ember.spark.cognition.handle import (
    CognitionHandle,
    cognition_registry,
    open_cognition,
)
from ember.spark.cognition.thoughtforge.adapter import ThoughtForgeCognition

# --------------------------------------------------------------------- #
# Fake ThoughtForge package — shaped from the TF-034 freeze            #
# --------------------------------------------------------------------- #


class FakeChatMessage:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class FakeChatHistory:
    """Mirrors TF's ChatHistory.add_user / add_assistant shape."""

    def __init__(self) -> None:
        self.messages: list[FakeChatMessage] = []

    def add_user(self, text: str) -> str:
        self.messages.append(FakeChatMessage("user", text))
        return "turn-id"

    def add_assistant(self, text: str, turn_id: str = "") -> None:
        self.messages.append(FakeChatMessage("assistant", text))


@dataclass
class FakeFinalResponseRecord:
    """Mirrors TF's FinalResponseRecord fields the binding reads."""

    text: str = "a forged answer"
    turn_id: str = "turn-1"
    mode: str = "knowledge_only"
    enforcement_passed: bool = True
    citations: list[str] = field(default_factory=lambda: ["doc-a"])
    token_count: int = 7


class FakeCore:
    """Records exactly how Ember's adapter constructs + calls it."""

    instances: list[FakeCore] = []
    raise_on_think: Exception | None = None

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        model_path: Any = None,
        memory_dir: Any = None,
        db_path: Any = None,
        backend: Any = None,
    ) -> None:
        self.ctor = {
            "config": config,
            "model_path": model_path,
            "memory_dir": memory_dir,
            "db_path": db_path,
            "backend": backend,
        }
        self.think_calls: list[dict[str, Any]] = []
        self.unloaded = False
        FakeCore.instances.append(self)

    def think(
        self,
        user_text: str,
        retrieval_path: Any = None,
        num_drafts: Any = None,
        history: Any = None,
        interrupt: Any = None,
    ) -> FakeFinalResponseRecord:
        self.think_calls.append(
            {
                "user_text": user_text,
                "retrieval_path": retrieval_path,
                "num_drafts": num_drafts,
                "history": history,
                "interrupt": interrupt,
            }
        )
        if FakeCore.raise_on_think is not None:
            raise FakeCore.raise_on_think
        return FakeFinalResponseRecord()

    def unload_model(self) -> None:
        self.unloaded = True


def _fake_module(
    *,
    api_version: str | None = "1.0.0",
    drift: list[str] | None = None,
    with_core: bool = True,
) -> ModuleType:
    module = ModuleType("thoughtforge.cognition")
    if api_version is not None:
        module.API_VERSION = api_version  # type: ignore[attr-defined]
    module.verify_api_surface = lambda: list(drift or [])  # type: ignore[attr-defined]
    module.ChatHistory = FakeChatHistory  # type: ignore[attr-defined]
    if with_core:
        module.ThoughtForgeCore = FakeCore  # type: ignore[attr-defined]
    FakeCore.instances = []
    FakeCore.raise_on_think = None
    return module


def _enabled(**overrides: Any) -> CognitionConfig:
    return CognitionConfig(enabled=True, **overrides)


def _open_with_fake(config: CognitionConfig, module: ModuleType):
    return ThoughtForgeCognition.open(config, module=module)


# --------------------------------------------------------------------- #
# Registry + profile gate                                              #
# --------------------------------------------------------------------- #


def test_registry_truth() -> None:
    registry = cognition_registry()
    assert len(registry) == 1
    entry = registry[0]
    assert entry.provider == "thoughtforge"
    assert entry.implemented is True
    assert entry.api_major == 1
    assert entry.afforded_profiles == (
        ConversationProfile.PHONE,
        ConversationProfile.PI,
        ConversationProfile.LAPTOP,
    )


def test_profile_affordance_and_caps() -> None:
    expected = {
        ConversationProfile.TOASTER: None,
        ConversationProfile.PHONE: 1,
        ConversationProfile.PI: 1,
        ConversationProfile.LAPTOP: 2,
    }
    for profile, cap in expected.items():
        config = CognitionConfig(profile=profile)
        assert config.resolved_num_drafts == cap
        assert config.affords() is (cap is not None)


def test_explicit_num_drafts_wins_over_profile() -> None:
    config = CognitionConfig(profile=ConversationProfile.PI, num_drafts=2)
    assert config.resolved_num_drafts == 2


# --------------------------------------------------------------------- #
# open_cognition refusal order (default env: TF not installed)         #
# --------------------------------------------------------------------- #


def test_open_cognition_disabled_by_default() -> None:
    result = open_cognition(CognitionConfig())
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.DISABLED


def test_open_cognition_toaster_cannot_afford() -> None:
    result = open_cognition(_enabled(profile=ConversationProfile.TOASTER))
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.PROFILE_CANNOT_AFFORD


def test_open_cognition_unknown_provider() -> None:
    result = open_cognition(_enabled(provider="someone-else"))
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.RUNTIME_NOT_INSTALLED


def test_open_cognition_not_installed_in_default_env() -> None:
    # The default env has no thoughtforge package: the refusal must
    # name that, and must not raise.
    assert "thoughtforge.cognition" not in sys.modules
    result = open_cognition(_enabled())
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.RUNTIME_NOT_INSTALLED


# --------------------------------------------------------------------- #
# Adapter open: version, drift, custody                                #
# --------------------------------------------------------------------- #


def test_open_success_builds_core_with_ember_custody() -> None:
    module = _fake_module()
    config = _enabled(
        memory_dir=Path("~/ember-tf/memory"),
        db_path=Path("~/ember-tf/knowledge.db"),
        tf_config={"conversation": {"depth": "deep"}},
    )
    handle = _open_with_fake(config, module)
    assert isinstance(handle, ThoughtForgeCognition)
    assert isinstance(handle, CognitionHandle)
    assert handle.api_version == "1.0.0"
    core = FakeCore.instances[0]
    assert core.ctor["memory_dir"] == Path("~/ember-tf/memory").expanduser()
    assert core.ctor["db_path"] == Path("~/ember-tf/knowledge.db").expanduser()
    assert core.ctor["config"] == {"conversation": {"depth": "deep"}}
    assert isinstance(core.ctor["config"], dict)
    # No model configured → knowledge-only shape, model_path untouched.
    assert core.ctor["model_path"] is None
    assert core.ctor["backend"] is None


def test_open_passes_model_path_only_when_set(tmp_path: Path) -> None:
    module = _fake_module()
    model = tmp_path / "model.gguf"
    handle = _open_with_fake(_enabled(model_path=model), module)
    assert isinstance(handle, ThoughtForgeCognition)
    assert FakeCore.instances[0].ctor["model_path"] == model


def test_open_refuses_wrong_api_major() -> None:
    result = _open_with_fake(_enabled(), _fake_module(api_version="2.0.0"))
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.VERSION_MISMATCH


def test_open_refuses_unversioned_package() -> None:
    result = _open_with_fake(_enabled(), _fake_module(api_version=None))
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.VERSION_MISMATCH


def test_open_refuses_drifted_surface() -> None:
    module = _fake_module(drift=["core method think: parameters differ"])
    result = _open_with_fake(_enabled(), module)
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.VERSION_MISMATCH
    assert result.detail is not None and "1 place" in result.detail


def test_open_refuses_missing_core_class() -> None:
    result = _open_with_fake(_enabled(), _fake_module(with_core=False))
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.RUNTIME_NOT_INSTALLED


def test_open_refuses_num_drafts_below_one() -> None:
    result = _open_with_fake(_enabled(num_drafts=0), _fake_module())
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.CONFIG_INVALID
    assert FakeCore.instances == []


def test_open_refuses_core_construction_failure() -> None:
    class BadCore:
        def __init__(self, **kwargs: Any) -> None:
            raise ValueError("unknown profile id 'bogus'")

    module = _fake_module()
    module.ThoughtForgeCore = BadCore  # type: ignore[attr-defined]
    result = _open_with_fake(_enabled(), module)
    assert isinstance(result, CognitionUnavailable)
    assert result.reason is CognitionUnavailableReason.CONFIG_INVALID


# --------------------------------------------------------------------- #
# think(): history, draft cap, reply mapping                           #
# --------------------------------------------------------------------- #


def _handle(module: ModuleType | None = None, **overrides: Any):
    handle = _open_with_fake(_enabled(**overrides), module or _fake_module())
    assert isinstance(handle, ThoughtForgeCognition)
    return handle


def test_think_maps_final_record() -> None:
    handle = _handle()
    reply = handle.think("What is the Yggdrasil?")
    assert isinstance(reply, CognitionReply)
    assert reply.text == "a forged answer"
    assert reply.provider == "thoughtforge"
    assert reply.api_version == "1.0.0"
    assert reply.turn_id == "turn-1"
    assert reply.mode == "knowledge_only"
    assert reply.enforcement_passed is True
    assert reply.citations == ("doc-a",)
    assert reply.token_count == 7
    core = FakeCore.instances[0]
    call = core.think_calls[0]
    assert call["user_text"] == "What is the Yggdrasil?"
    # PI profile default: draft cap 1 rides the frozen parameter.
    assert call["num_drafts"] == 1
    # No episodes → history stays the frozen default (None).
    assert call["history"] is None


def test_think_laptop_cap_is_two() -> None:
    handle = _handle(profile=ConversationProfile.LAPTOP)
    handle.think("hello")
    assert FakeCore.instances[0].think_calls[0]["num_drafts"] == 2


def test_think_builds_thoughtforge_history_from_episodes() -> None:
    handle = _handle()
    episodes = (
        Episode(operator_input="first question", ember_reply="first answer"),
        Episode(operator_input="second question", ember_reply="second answer"),
    )
    handle.think("third question", episodes)
    history = FakeCore.instances[0].think_calls[0]["history"]
    assert isinstance(history, FakeChatHistory)
    assert [(m.role, m.content) for m in history.messages] == [
        ("user", "first question"),
        ("assistant", "first answer"),
        ("user", "second question"),
        ("assistant", "second answer"),
    ]


def test_think_core_exception_folds_into_error_reply() -> None:
    handle = _handle()
    FakeCore.raise_on_think = RuntimeError("backend exploded")
    reply = handle.think("hello")
    assert reply.mode == "error"
    assert "backend exploded" in reply.text
    assert reply.provider == "thoughtforge"


def test_health_and_close() -> None:
    handle = _handle()
    health = handle.health()
    assert isinstance(health, CognitionHealth)
    assert health.provider == "thoughtforge"
    assert health.api_version == "1.0.0"
    assert health.last_ok is not None
    handle.close()
    assert FakeCore.instances[0].unloaded is True


# --------------------------------------------------------------------- #
# Config plumbing                                                      #
# --------------------------------------------------------------------- #


def test_config_defaults_disabled_and_tethered() -> None:
    config = EmberConfig().cognition
    assert config.enabled is False
    assert config.provider == "thoughtforge"
    assert config.expected_api_major == 1
    assert config.model_path is None
    assert config.memory_dir == Path("~/.ember/thoughtforge/memory")
    assert config.db_path == Path("~/.ember/thoughtforge/knowledge.db")


def test_toml_loader_coerces_cognition_section(tmp_path: Path) -> None:
    toml = tmp_path / "ember.toml"
    toml.write_text(
        "[cognition]\n"
        "enabled = true\n"
        'profile = "laptop"\n'
        "num_drafts = 2\n",
        encoding="utf-8",
    )
    config = load_ember_config(file_override=toml, skip_env=True)
    assert config.cognition.enabled is True
    assert config.cognition.profile is ConversationProfile.LAPTOP
    assert config.cognition.resolved_num_drafts == 2


# --------------------------------------------------------------------- #
# No core dependency                                                   #
# --------------------------------------------------------------------- #


def test_binding_imports_do_not_import_thoughtforge() -> None:
    # Importing Ember's cognition surface (done at this module's
    # top) must not pull the neighbour in: it is optional, lazy,
    # and absent from the default env where this suite runs.
    assert "thoughtforge.cognition" not in sys.modules
    assert "thoughtforge" not in sys.modules
