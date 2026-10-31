"""E-026 — tools discipline: permission shapes + the approval gate.

Pins, from the runner:

- the first-party inventory: every registered first-party tool
  states its access class, approval policy, guarded arguments;
- the gate: dangerous or unspecified access classes are never
  auto-approved (descriptor STANDING, session "always", and
  standing_trust all fail to wave them through);
- the regression: a config ``forbidden`` override beats
  ``standing_trust`` (before E-026 the trust knob was resolved
  first and silently overrode the operator's specific refusal);
- guarded arguments: a truthy model-supplied escape hatch always
  prompts, even for an otherwise auto-approvable tool;
- MCP-bridged tools state EXTERNAL access.
"""

from __future__ import annotations

import importlib

import pytest

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolAccess,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
)
from ember.spark.funi.tools.approval import resolve
from ember.spark.funi.tools.permissions import (
    guarded_argument_in_use,
    may_auto_approve,
    permission_shape,
    tool_inventory,
)
from ember.spark.funi.tools.registry import clear


@pytest.fixture(autouse=True)
def _isolate_registry():
    clear()
    yield
    clear()


def _first_party_inventory():
    """Register the three first-party tools fresh and inventory them."""
    import ember.tools.fetch_url as fetch_url  # noqa: PLC0415
    import ember.tools.read_local_file as read_local_file  # noqa: PLC0415
    import ember.tools.search_well as search_well  # noqa: PLC0415

    # Importing ember.tools runs its package __init__, which
    # registers all three; clear before the reloads so each
    # module's own register() lands on an empty registry.
    clear()
    for module in (fetch_url, read_local_file, search_well):
        importlib.reload(module)
    return tool_inventory()


def _descriptor(
    name: str = "some_tool",
    *,
    access: ToolAccess = ToolAccess.UNSPECIFIED,
    required_approval: ApprovalPolicy = ApprovalPolicy.PER_CALL,
    guarded_arguments: tuple[str, ...] = (),
) -> ToolDescriptor:
    return ToolDescriptor(
        name=name,
        description="t",
        required_approval=required_approval,
        access=access,
        guarded_arguments=guarded_arguments,
    )


# --------------------------------------------------------------------- #
# The first-party inventory                                             #
# --------------------------------------------------------------------- #


def test_first_party_inventory_is_complete_and_stated() -> None:
    shapes = {s.name: s for s in _first_party_inventory()}
    assert sorted(shapes) == ["fetch_url", "read_local_file", "search_well"]

    fetch = shapes["fetch_url"]
    assert fetch.access is ToolAccess.NETWORK
    assert fetch.approval == "per_call"
    assert fetch.auto_approvable is False
    assert fetch.guarded_arguments == ("allow_private_addresses",)
    assert fetch.timeout_s == pytest.approx(15.0)

    read = shapes["read_local_file"]
    assert read.access is ToolAccess.PRIVATE_READ
    assert read.approval == "per_call"
    assert read.auto_approvable is True  # class may auto; policy still asks
    assert read.guarded_arguments == ()
    assert read.timeout_s == pytest.approx(5.0)

    search = shapes["search_well"]
    assert search.access is ToolAccess.PRIVATE_READ
    assert search.approval == "standing"
    assert search.auto_approvable is True
    assert search.guarded_arguments == ()
    assert search.timeout_s == pytest.approx(15.0)


def test_no_first_party_tool_is_unspecified_or_write_capable() -> None:
    for shape in _first_party_inventory():
        assert shape.access is not ToolAccess.UNSPECIFIED, shape.name
        assert shape.access not in (
            ToolAccess.WRITE, ToolAccess.EXECUTE, ToolAccess.EXTERNAL,
        ), shape.name


def test_fetch_url_guarded_argument_defaults_falsy() -> None:
    """A guarded argument that defaulted truthy would widen by default."""
    import ember.tools.fetch_url as fetch_url  # noqa: PLC0415

    clear()
    importlib.reload(fetch_url)
    entry_param = fetch_url._DESCRIPTOR.parameters_schema["allow_private_addresses"]
    assert entry_param.default is False
    assert fetch_url._DESCRIPTOR.guarded_arguments == ("allow_private_addresses",)


def test_descriptor_defaults_are_unspecified_and_unguarded() -> None:
    d = ToolDescriptor(name="x", description="y")
    assert d.access is ToolAccess.UNSPECIFIED
    assert d.guarded_arguments == ()


def test_access_enum_values() -> None:
    assert {a.value for a in ToolAccess} == {
        "read_only", "private_read", "network", "write",
        "execute", "external", "unspecified",
    }


def test_inventory_from_mapping_is_sorted() -> None:
    b = _descriptor("b_tool")
    a = _descriptor("a_tool")
    shapes = tool_inventory({"b_tool": b, "a_tool": a})
    assert [s.name for s in shapes] == ["a_tool", "b_tool"]


# --------------------------------------------------------------------- #
# The gate — dangerous / unspecified never auto-approves                #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "access",
    [
        ToolAccess.NETWORK, ToolAccess.WRITE, ToolAccess.EXECUTE,
        ToolAccess.EXTERNAL, ToolAccess.UNSPECIFIED,
    ],
)
def test_dangerous_or_unspecified_standing_descriptor_prompts(access) -> None:
    """An author declaring STANDING on a dangerous tool gets per-call."""
    d = _descriptor(access=access, required_approval=ApprovalPolicy.STANDING)
    decision = resolve(d)
    assert decision.needs_prompt is True
    assert may_auto_approve(d) is False


@pytest.mark.parametrize(
    "access",
    [
        ToolAccess.NETWORK, ToolAccess.WRITE, ToolAccess.EXECUTE,
        ToolAccess.EXTERNAL, ToolAccess.UNSPECIFIED,
    ],
)
def test_dangerous_or_unspecified_ignores_standing_trust(access) -> None:
    d = _descriptor(access=access)
    decision = resolve(d, standing_trust_all=True)
    assert decision.needs_prompt is True


@pytest.mark.parametrize(
    "access",
    [ToolAccess.NETWORK, ToolAccess.EXTERNAL, ToolAccess.UNSPECIFIED],
)
def test_dangerous_or_unspecified_ignores_session_always(access) -> None:
    d = _descriptor(access=access)
    decision = resolve(d, session_standing=frozenset({"some_tool"}))
    assert decision.needs_prompt is True


@pytest.mark.parametrize("access", [ToolAccess.READ_ONLY, ToolAccess.PRIVATE_READ])
def test_safe_classes_may_auto_approve(access) -> None:
    standing = _descriptor(access=access, required_approval=ApprovalPolicy.STANDING)
    assert resolve(standing).outcome is ApprovalOutcome.AUTO_APPROVED
    per_call = _descriptor(access=access)
    assert resolve(per_call, standing_trust_all=True).outcome is (
        ApprovalOutcome.AUTO_APPROVED
    )
    assert resolve(per_call, session_standing=frozenset({"some_tool"})).outcome is (
        ApprovalOutcome.AUTO_APPROVED
    )
    assert may_auto_approve(per_call) is True


def test_permission_shape_reports_declared_vs_honoured() -> None:
    d = _descriptor(
        access=ToolAccess.NETWORK, required_approval=ApprovalPolicy.STANDING,
    )
    shape = permission_shape(d)
    assert shape.approval == "standing"       # what the author declared
    assert shape.auto_approvable is False     # what the gate honours


# --------------------------------------------------------------------- #
# The regression — a specific refusal beats blanket trust               #
# --------------------------------------------------------------------- #


def test_config_forbidden_beats_standing_trust() -> None:
    """E-026 regression: before the fix, resolve() checked the trust
    knob before config overrides, so standing_trust silently
    overrode an operator's per-tool ``forbidden``."""
    d = _descriptor(access=ToolAccess.PRIVATE_READ)
    decision = resolve(
        d,
        config_overrides={"some_tool": ApprovalPolicy.FORBIDDEN},
        standing_trust_all=True,
    )
    assert decision.outcome is ApprovalOutcome.FORBIDDEN_BY_REGISTRY
    assert decision.needs_prompt is False


def test_config_forbidden_beats_session_and_descriptor_standing() -> None:
    d = _descriptor(
        access=ToolAccess.PRIVATE_READ,
        required_approval=ApprovalPolicy.STANDING,
    )
    decision = resolve(
        d,
        config_overrides={"some_tool": ApprovalPolicy.FORBIDDEN},
        session_standing=frozenset({"some_tool"}),
        standing_trust_all=True,
    )
    assert decision.outcome is ApprovalOutcome.FORBIDDEN_BY_REGISTRY


def test_descriptor_forbidden_beats_everything() -> None:
    d = _descriptor(
        access=ToolAccess.READ_ONLY,
        required_approval=ApprovalPolicy.FORBIDDEN,
    )
    decision = resolve(d, standing_trust_all=True)
    assert decision.outcome is ApprovalOutcome.FORBIDDEN_BY_REGISTRY


def test_config_cannot_upgrade_within_gate() -> None:
    """Config STANDING still cannot lift a PER_CALL safe tool."""
    d = _descriptor(access=ToolAccess.PRIVATE_READ)
    decision = resolve(
        d, config_overrides={"some_tool": ApprovalPolicy.STANDING},
    )
    assert decision.needs_prompt is True


# --------------------------------------------------------------------- #
# Guarded arguments — the model may not widen its own reach             #
# --------------------------------------------------------------------- #


def _guarded_descriptor() -> ToolDescriptor:
    return ToolDescriptor(
        name="fetch_like",
        description="t",
        parameters_schema={
            "url": ToolParameter(kind=ToolParameterKind.URL, description="u"),
            "allow_private_addresses": ToolParameter(
                kind=ToolParameterKind.BOOLEAN,
                description="widen",
                required=False,
                default=False,
            ),
        },
        required_approval=ApprovalPolicy.STANDING,
        access=ToolAccess.PRIVATE_READ,  # safe class on purpose: isolate the arg gate
        guarded_arguments=("allow_private_addresses",),
    )


def test_guarded_argument_truthy_always_prompts() -> None:
    d = _guarded_descriptor()
    decision = resolve(
        d,
        standing_trust_all=True,
        session_standing=frozenset({"fetch_like"}),
        arguments={"url": "https://example.com", "allow_private_addresses": True},
    )
    assert decision.needs_prompt is True


def test_guarded_argument_falsy_or_absent_auto_approves() -> None:
    d = _guarded_descriptor()
    for args in (
        {"url": "https://example.com", "allow_private_addresses": False},
        {"url": "https://example.com"},
        {},
        None,
    ):
        decision = resolve(d, arguments=args)
        assert decision.outcome is ApprovalOutcome.AUTO_APPROVED, args


def test_guarded_argument_in_use_helper() -> None:
    d = _guarded_descriptor()
    assert guarded_argument_in_use(d, {"allow_private_addresses": True}) == (
        "allow_private_addresses"
    )
    assert guarded_argument_in_use(d, {"allow_private_addresses": False}) is None
    assert guarded_argument_in_use(d, {}) is None
    assert guarded_argument_in_use(d, None) is None


def test_real_fetch_url_call_with_private_flag_prompts_under_trust() -> None:
    """End-to-end at the resolver: the real fetch_url descriptor +
    a model-supplied allow_private_addresses=true can never be
    waved through by standing_trust or a session 'always'."""
    import ember.tools.fetch_url as fetch_url  # noqa: PLC0415

    clear()
    importlib.reload(fetch_url)
    descriptor = fetch_url._DESCRIPTOR
    call = ToolCall(
        call_id="c-1",
        name="fetch_url",
        arguments={
            "url": "http://127.0.0.1:8080/admin",
            "allow_private_addresses": True,
        },
    )
    decision = resolve(
        descriptor,
        standing_trust_all=True,
        session_standing=frozenset({"fetch_url"}),
        arguments=call.arguments,
    )
    assert decision.needs_prompt is True
    # And without the flag it still prompts — NETWORK is per-call-only.
    decision = resolve(
        descriptor,
        standing_trust_all=True,
        arguments={"url": "https://example.com"},
    )
    assert decision.needs_prompt is True


# --------------------------------------------------------------------- #
# MCP-bridged tools state EXTERNAL                                      #
# --------------------------------------------------------------------- #


def test_mcp_bridge_descriptor_states_external_access() -> None:
    from ember.mcp.bridge import _build_descriptor  # noqa: PLC0415

    class _FakeTool:
        name = "ping"
        description = "Ping"
        inputSchema = {}  # noqa: N815 — MCP's own field name

    desc = _build_descriptor(
        full_name="mcp__demo__ping", mcp_tool=_FakeTool(), standing=True,
    )
    assert desc.access is ToolAccess.EXTERNAL
    # The descriptor keeps the operator's auto_approve lift…
    assert desc.required_approval is ApprovalPolicy.STANDING
    # …but the gate will not honour auto-approval for EXTERNAL.
    assert resolve(desc).needs_prompt is True
