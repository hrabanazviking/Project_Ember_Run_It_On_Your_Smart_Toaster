"""Example 2 — a member program binding to Ember's core.

Run it (from the repo root, no optional extras needed):

    PYTHONPATH=src python3 examples/member_binding.py

What this shows: how another program in the monorepo (a
"member" — Verdandi, a memory system, a bridge) attaches to the
Ember core through the **frozen API v1** only (E-037,
`docs/architecture/E-037_CORE_API_FREEZE.md`):

1. check the API version before binding;
2. read the frozen surface as data and verify it is intact;
3. load a config through the frozen loader — here the worked
   phone-class example in `examples/configs/` — never by
   parsing `ember.yaml` itself;
4. open handles through the frozen registries and meet their
   typed refusals (an uninstalled model runtime and the
   switched-off cognition layer both say no, plainly, as
   values — nothing raises, nothing pretends);
5. tag an Episode with its persona and conversation through
   the frozen helpers, the way a member hands a turn back.

Every import in this file is a frozen bind point. The E-039
tests AST-scan this file and fail if an unfrozen import creeps
in — that is the discipline members are held to.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running straight from a source checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ember  # noqa: E402
from ember.api import api_manifest, is_api_compatible, verify_api_surface  # noqa: E402
from ember.config import load_ember_config  # noqa: E402
from ember.schemas.cognition import CognitionUnavailable  # noqa: E402
from ember.schemas.config import CognitionConfig, FuniConfig, FuniRuntime  # noqa: E402
from ember.schemas.episode import Episode  # noqa: E402
from ember.schemas.funi import Unavailable  # noqa: E402
from ember.spark.cognition import open_cognition  # noqa: E402
from ember.spark.conversation import tag_episode as tag_conversation  # noqa: E402
from ember.spark.funi import open as funi_open  # noqa: E402
from ember.spark.persona import tag_episode as tag_persona  # noqa: E402

EXAMPLE_CONFIG = Path(__file__).resolve().parent / "configs" / "phone-class.toml"


def main() -> int:
    # 1. The version gate: bind only to a major you know.
    print(f"package version: {ember.__version__} (a release label)")
    print(f"core API version: {ember.API_VERSION} (the contract)")
    assert is_api_compatible("1.0"), "this example was written against API 1.0"
    assert not is_api_compatible("2.0"), "a future major must not bind"

    # 2. The frozen surface, as data — and proof it is intact.
    manifest = api_manifest()
    problems = verify_api_surface()
    print(f"frozen names: {len(manifest)}; surface problems: {len(problems)}")
    assert problems == ()

    # 3. Config through the frozen loader (the worked example file).
    config = load_ember_config(file_override=EXAMPLE_CONFIG, skip_env=True)
    conversation = config.conversation
    print(
        f"example config: profile={conversation.profile.value}, "
        f"history budget={conversation.resolved_token_budget} tokens, "
        f"kept word-for-word={conversation.resolved_max_episodes} turns"
    )

    # 4. Typed refusals from the frozen registries — values, not crashes.
    refused = funi_open(FuniConfig(runtime=FuniRuntime.LLAMACPP))
    assert isinstance(refused, Unavailable)
    print(f"uninstalled runtime refuses as: {refused.reason.value}")
    cognition = open_cognition(CognitionConfig())
    assert isinstance(cognition, CognitionUnavailable)
    print(f"switched-off cognition refuses as: {cognition.reason.value}")

    # 5. Tagging a turn the way a member hands one back.
    episode = Episode(operator_input="hi", ember_reply="hello")
    tagged = tag_conversation(tag_persona(episode, "default"), "kitchen")
    print(
        f"tagged episode: persona={tagged.persona_id}, "
        f"conversation={tagged.conversation_id}"
    )
    print("member_binding: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
