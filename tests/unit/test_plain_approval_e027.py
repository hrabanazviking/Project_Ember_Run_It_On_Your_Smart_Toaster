"""E-027 — approval shape for normal folks.

Pins, from the runner:

- the plain action sentence for each first-party tool (built from
  the detail that matters) + the description fallback;
- the plain reach sentence for every access class — ordinary
  words, never the class/policy names;
- the guarded-argument warning in plain words (fetch_url's
  private-address widening named as a home-network reach);
- the rememberable scopes: "always" is offered exactly when the
  E-026 gate would honour it, and its stated scope is *while
  we're chatting*, forgotten at chat end — never "forever";
- why a call is asked every time, stated plainly per class;
- the prompter: offers only valid answers, counts an unoffered
  "always" as a one-time yes *with that said on screen*, and the
  whole prompt carries no approval jargon.
"""

from __future__ import annotations

import importlib
import io

import pytest

from ember.schemas.tool import (
    ApprovalPolicy,
    ToolAccess,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
)
from ember.spark.funi.tools.approval import StdinApprovalPrompter
from ember.spark.funi.tools.plain import (
    can_remember,
    offered_choices,
    plain_action,
    plain_guarded_warning,
    plain_reach,
    render_plain_proposal,
    why_asked_every_time,
)
from ember.spark.funi.tools.registry import clear


@pytest.fixture(autouse=True)
def _isolate_registry():
    clear()
    yield
    clear()


def _descriptor(
    name: str = "some_tool",
    *,
    access: ToolAccess = ToolAccess.PRIVATE_READ,
    description: str = "Do a thing.",
    guarded_arguments: tuple[str, ...] = (),
    redacted_arg_names: tuple[str, ...] = (),
) -> ToolDescriptor:
    return ToolDescriptor(
        name=name,
        description=description,
        required_approval=ApprovalPolicy.PER_CALL,
        access=access,
        guarded_arguments=guarded_arguments,
        redacted_arg_names=redacted_arg_names,
    )


def _call(name: str = "some_tool", arguments: dict | None = None) -> ToolCall:
    return ToolCall(call_id="c-1", name=name, arguments=arguments or {})


def _real_descriptor(module_name: str) -> ToolDescriptor:
    module = importlib.import_module(f"ember.tools.{module_name}")
    clear()
    importlib.reload(module)
    return module._DESCRIPTOR


# --------------------------------------------------------------------- #
# Plain actions                                                         #
# --------------------------------------------------------------------- #


def test_plain_action_search_well_names_the_search_words() -> None:
    d = _real_descriptor("search_well")
    out = plain_action(d, _call("search_well", {"query": "odin sleep"}))
    assert "Search the things you have saved with Ember" in out
    assert '"odin sleep"' in out


def test_plain_action_read_local_file_names_the_file() -> None:
    d = _real_descriptor("read_local_file")
    out = plain_action(d, _call("read_local_file", {"path": "/home/u/notes.md"}))
    assert out == "Read one of your files: /home/u/notes.md."


def test_plain_action_fetch_url_names_the_address() -> None:
    d = _real_descriptor("fetch_url")
    out = plain_action(d, _call("fetch_url", {"url": "https://example.com/x"}))
    assert out == "Fetch a page from the internet: https://example.com/x."


def test_plain_action_falls_back_to_the_description() -> None:
    d = _descriptor(description="Water the plants.")
    assert plain_action(d, _call()) == "Water the plants."


def test_plain_action_never_shows_a_redacted_detail() -> None:
    d = _descriptor(
        name="read_local_file", redacted_arg_names=("path",),
    )
    out = plain_action(d, _call("read_local_file", {"path": "/secret/path"}))
    assert "/secret/path" not in out


# --------------------------------------------------------------------- #
# Plain reach — every class, in ordinary words                          #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("access", "needles"),
    [
        (ToolAccess.READ_ONLY, ["only look", "cannot change"]),
        (ToolAccess.PRIVATE_READ, ["your own information", "nothing is sent"]),
        (ToolAccess.NETWORK, ["to the internet", "will see"]),
        (ToolAccess.WRITE, ["can change things", "carefully"]),
        (ToolAccess.EXECUTE, ["runs a program", "carefully"]),
        (ToolAccess.EXTERNAL, ["outside Ember", "cannot fully see"]),
        (ToolAccess.UNSPECIFIED, ["no statement", "say no if you are unsure"]),
    ],
)
def test_plain_reach_per_class(access, needles) -> None:
    out = plain_reach(_descriptor(access=access))
    for needle in needles:
        assert needle in out
    # The class's machine name never leaks into the plain wording.
    assert access.value not in out


# --------------------------------------------------------------------- #
# The guarded-argument warning                                          #
# --------------------------------------------------------------------- #


def test_fetch_url_private_addresses_warning_is_plain() -> None:
    d = _real_descriptor("fetch_url")
    call = _call("fetch_url", {
        "url": "http://192.168.1.1/", "allow_private_addresses": True,
    })
    out = plain_guarded_warning(d, call)
    assert out is not None
    assert "private addresses on your own home network" in out
    assert "wider reach" in out


def test_no_warning_without_a_guarded_argument() -> None:
    d = _real_descriptor("fetch_url")
    call = _call("fetch_url", {"url": "https://example.com"})
    assert plain_guarded_warning(d, call) is None


def test_generic_guarded_warning_names_the_argument() -> None:
    d = _descriptor(guarded_arguments=("wide_mode",))
    call = _call(arguments={"wide_mode": True})
    out = plain_guarded_warning(d, call)
    assert out is not None and "wide_mode" in out and "wider reach" in out


# --------------------------------------------------------------------- #
# The rememberable scopes                                               #
# --------------------------------------------------------------------- #


def _answers(descriptor, call) -> list[str]:
    return [c.answer for c in offered_choices(descriptor, call)]


def test_safe_tool_offers_once_chat_and_no() -> None:
    d = _descriptor(access=ToolAccess.PRIVATE_READ)
    choices = offered_choices(d, _call())
    assert [c.answer for c in choices] == ["y", "always", "n"]
    always = choices[1]
    # The scope is stated truthfully: this chat only, never forever.
    assert "while we're chatting" in always.meaning
    assert "Forgotten when the chat ends" in always.meaning
    assert "never forever" in always.meaning


@pytest.mark.parametrize(
    "access",
    [
        ToolAccess.NETWORK, ToolAccess.WRITE, ToolAccess.EXECUTE,
        ToolAccess.EXTERNAL, ToolAccess.UNSPECIFIED,
    ],
)
def test_gated_classes_never_offer_always(access) -> None:
    d = _descriptor(access=access)
    assert _answers(d, _call()) == ["y", "n"]
    assert can_remember(d, _call()) is False


def test_guarded_call_on_a_safe_tool_never_offers_always() -> None:
    d = _descriptor(
        access=ToolAccess.PRIVATE_READ, guarded_arguments=("wide_mode",),
    )
    call = _call(arguments={"wide_mode": True})
    assert _answers(d, call) == ["y", "n"]
    # The same tool without the widening offers it again.
    assert "always" in _answers(d, _call())


@pytest.mark.parametrize(
    ("access", "needle"),
    [
        (ToolAccess.NETWORK, "goes out to the internet"),
        (ToolAccess.WRITE, "can change things"),
        (ToolAccess.EXECUTE, "runs something"),
        (ToolAccess.EXTERNAL, "another program outside Ember"),
        (ToolAccess.UNSPECIFIED, "no statement of what this tool can reach"),
    ],
)
def test_why_asked_every_time_is_plain(access, needle) -> None:
    out = why_asked_every_time(_descriptor(access=access), _call())
    assert out is not None
    assert needle in out
    assert "just this once" in out


def test_why_asked_every_time_guarded_reason_wins() -> None:
    d = _descriptor(
        access=ToolAccess.NETWORK, guarded_arguments=("wide_mode",),
    )
    out = why_asked_every_time(d, _call(arguments={"wide_mode": True}))
    assert out is not None and "widens what the tool can reach" in out


def test_why_asked_every_time_is_none_when_remembering_is_offered() -> None:
    assert why_asked_every_time(_descriptor(), _call()) is None


# --------------------------------------------------------------------- #
# The rendered prompt                                                   #
# --------------------------------------------------------------------- #

_JARGON = (
    "per_call", "standing", "descriptor", "ToolAccess",
    "approval policy", "FORBIDDEN_BY_REGISTRY", "guarded_argument",
)


def test_rendered_prompt_is_complete_and_jargon_free() -> None:
    d = _real_descriptor("fetch_url")
    call = _call("fetch_url", {
        "url": "http://192.168.1.1/admin", "allow_private_addresses": True,
    })
    out = render_plain_proposal(d, call)
    assert "Ember is asking your permission." in out
    assert "What Ember wants to do:" in out
    assert "Fetch a page from the internet: http://192.168.1.1/admin." in out
    assert "What this can and cannot do:" in out
    assert "home network" in out
    assert "Your choices:" in out
    assert "y — Yes — just this once." in out
    assert "n — No — don't do it." in out
    assert "always" not in [
        c.answer for c in offered_choices(d, call)
    ]
    for word in _JARGON:
        assert word not in out


def test_rendered_prompt_hides_redacted_details() -> None:
    d = _descriptor(redacted_arg_names=("token",))
    call = _call(arguments={"token": "super-secret", "path": "/tmp/x"})
    out = render_plain_proposal(d, call)
    assert "super-secret" not in out
    assert "<hidden" in out
    assert "/tmp/x" in out


def test_rendered_prompt_for_a_safe_tool_shows_the_chat_scope() -> None:
    out = render_plain_proposal(_descriptor(), _call())
    assert "always — Yes" in out
    assert "while we're chatting" in out


# --------------------------------------------------------------------- #
# The prompter itself                                                   #
# --------------------------------------------------------------------- #


def _prompt(descriptor, call, typed: str) -> tuple[str, str]:
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=io.StringIO(typed), stdout=stdout)
    return prompter.prompt(descriptor, call), stdout.getvalue()


def test_prompter_for_a_safe_tool_accepts_always() -> None:
    answer, out = _prompt(_descriptor(), _call(), "always\n")
    assert answer == "always"
    assert "Your answer (y/always/n): " in out


def test_prompter_counts_unoffered_always_as_a_one_time_yes_and_says_so() -> None:
    """The E-027 honesty pin: before this slice, "always" on a
    NETWORK tool returned APPROVED_FOR_SESSION and the name was
    added to the session set — but resolve()'s gate asked again on
    the next call anyway, so the grant was silently worthless.
    Now the answer is a one-time yes, stated on screen."""
    d = _descriptor(access=ToolAccess.NETWORK)
    answer, out = _prompt(d, _call(), "always\n")
    assert answer == "y"
    assert "can't be remembered for this kind of request" in out
    assert "yes for this once only" in out
    assert "Your answer (y/n): " in out


def test_prompter_for_fetch_url_private_call_explains_itself() -> None:
    d = _real_descriptor("fetch_url")
    call = _call("fetch_url", {
        "url": "http://192.168.1.1/", "allow_private_addresses": True,
    })
    answer, out = _prompt(d, call, "y\n")
    assert answer == "y"
    assert "home network" in out
    assert "asks about it every time" in out


def test_prompter_still_refuses_on_eof_and_unknown() -> None:
    assert _prompt(_descriptor(), _call(), "")[0] == "n"
    answer, out = _prompt(_descriptor(), _call(), "maybe\n")
    assert answer == "n"
    assert "unrecognised" in out


# --------------------------------------------------------------------- #
# Munnr's proposal renderer carries the plain lines                     #
# --------------------------------------------------------------------- #


def test_render_tool_call_proposal_includes_plain_words() -> None:
    from ember.spark.munnr import render  # noqa: PLC0415

    d = _descriptor(
        name="read_local_file", description="Read a file.",
        access=ToolAccess.PRIVATE_READ,
    )
    call = ToolCall(
        call_id="abc-12345678", name="read_local_file",
        arguments={"path": "/home/u/notes.md"},
        )
    out = render.render_tool_call_proposal(d, call)
    assert "tool proposal" in out  # the technical header stays
    assert "in plain words: Read one of your files: /home/u/notes.md." in out
    assert "what it can reach: It reads your own information" in out


def test_tool_parameter_schema_helper_is_used() -> None:
    """Guard against the schema import drifting out of this file."""
    param = ToolParameter(kind=ToolParameterKind.BOOLEAN, description="x")
    assert param.kind is ToolParameterKind.BOOLEAN
