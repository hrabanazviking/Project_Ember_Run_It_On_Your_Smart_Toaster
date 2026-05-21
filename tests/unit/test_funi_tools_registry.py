"""Process-global tool registry (ADR 0011 §2.3) + argument validation."""

from __future__ import annotations

import pytest

from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolError,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi.tools.registry import (
    clear,
    is_registered,
    list_tools,
    lookup,
    register,
    validate_arguments,
)


@pytest.fixture(autouse=True)
def _isolated_registry() -> None:
    """Each test starts with an empty registry."""
    clear()
    yield
    clear()


def _make_descriptor(
    *,
    name: str = "search_well",
    required_approval: ApprovalPolicy = ApprovalPolicy.PER_CALL,
    redacted_arg_names: tuple[str, ...] = (),
) -> ToolDescriptor:
    return ToolDescriptor(
        name=name,
        description="test tool",
        parameters_schema={
            "query": ToolParameter(
                kind=ToolParameterKind.STRING, description="search text",
            ),
            "k": ToolParameter(
                kind=ToolParameterKind.INTEGER, description="top-k",
                required=False, default=5,
            ),
        },
        required_approval=required_approval,
        redacted_arg_names=redacted_arg_names,
    )


def _noop_executor(call: ToolCall) -> ToolReply:  # pragma: no cover — never called
    return ToolReply(call_id=call.call_id, output="ok")


# --------------------------------------------------------------------- #
# register / lookup / list_tools                                        #
# --------------------------------------------------------------------- #


def test_register_then_lookup_returns_descriptor_and_executor() -> None:
    descriptor = _make_descriptor()
    register(descriptor, _noop_executor)
    result = lookup("search_well")
    assert result is not None
    found_descriptor, found_executor = result
    assert found_descriptor is descriptor
    assert found_executor is _noop_executor


def test_lookup_returns_none_for_unknown_tool() -> None:
    assert lookup("nonexistent") is None


def test_is_registered_returns_truthy_only_when_present() -> None:
    assert is_registered("nope") is False
    register(_make_descriptor(name="alpha"), _noop_executor)
    assert is_registered("alpha") is True
    assert is_registered("beta") is False


def test_list_tools_returns_sorted_by_name() -> None:
    register(_make_descriptor(name="zebra"), _noop_executor)
    register(_make_descriptor(name="apple"), _noop_executor)
    register(_make_descriptor(name="mango"), _noop_executor)
    names = [d.name for d in list_tools()]
    assert names == ["apple", "mango", "zebra"]


def test_re_registering_same_name_raises_tool_error() -> None:
    register(_make_descriptor(), _noop_executor)
    with pytest.raises(ToolError, match="already registered"):
        register(_make_descriptor(), _noop_executor)


def test_clear_drops_every_registration() -> None:
    register(_make_descriptor(name="alpha"), _noop_executor)
    register(_make_descriptor(name="beta"), _noop_executor)
    clear()
    assert list_tools() == []


# --------------------------------------------------------------------- #
# FORBIDDEN at registration                                             #
# --------------------------------------------------------------------- #


def test_forbidden_descriptor_refuses_to_register() -> None:
    """ADR 0011 §2.4 — FORBIDDEN is mechanical 'never executable'."""
    descriptor = _make_descriptor(
        name="dangerous", required_approval=ApprovalPolicy.FORBIDDEN,
    )
    with pytest.raises(ToolError, match="FORBIDDEN at the registry level"):
        register(descriptor, _noop_executor)
    assert lookup("dangerous") is None
    assert is_registered("dangerous") is False


# --------------------------------------------------------------------- #
# validate_arguments                                                    #
# --------------------------------------------------------------------- #


def test_validate_accepts_valid_arguments() -> None:
    err = validate_arguments(_make_descriptor(), {"query": "Odin", "k": 5})
    assert err is None


def test_validate_accepts_missing_optional_with_default() -> None:
    """k has default=5 and required=False — omit is fine."""
    err = validate_arguments(_make_descriptor(), {"query": "Odin"})
    assert err is None


def test_validate_rejects_unknown_argument() -> None:
    err = validate_arguments(_make_descriptor(), {"query": "Odin", "typo": True})
    assert err is not None
    assert "typo" in err


def test_validate_rejects_missing_required_argument() -> None:
    err = validate_arguments(_make_descriptor(), {"k": 5})
    assert err is not None
    assert "query" in err
    assert "missing required" in err


def test_validate_rejects_wrong_string_type() -> None:
    err = validate_arguments(_make_descriptor(), {"query": 42})
    assert err is not None
    assert "string" in err


def test_validate_rejects_bool_as_integer() -> None:
    """Python's isinstance(True, int) is True — we check precisely."""
    err = validate_arguments(_make_descriptor(), {"query": "Odin", "k": True})
    assert err is not None
    assert "integer" in err


def test_validate_rejects_int_as_boolean() -> None:
    descriptor = ToolDescriptor(
        name="t",
        description="x",
        parameters_schema={
            "flag": ToolParameter(
                kind=ToolParameterKind.BOOLEAN, description="flag",
            ),
        },
    )
    err = validate_arguments(descriptor, {"flag": 1})
    assert err is not None
    assert "boolean" in err


def test_validate_accepts_float_with_integer_input() -> None:
    """A FLOAT kind accepts ints because Python treats 5 as 5.0 fine."""
    descriptor = ToolDescriptor(
        name="t",
        description="x",
        parameters_schema={
            "temp": ToolParameter(
                kind=ToolParameterKind.FLOAT, description="temperature",
            ),
        },
    )
    assert validate_arguments(descriptor, {"temp": 5}) is None
    assert validate_arguments(descriptor, {"temp": 5.5}) is None


def test_validate_url_requires_http_scheme() -> None:
    descriptor = ToolDescriptor(
        name="fetch",
        description="x",
        parameters_schema={
            "url": ToolParameter(kind=ToolParameterKind.URL, description="u"),
        },
    )
    assert validate_arguments(descriptor, {"url": "https://example.com"}) is None
    assert validate_arguments(descriptor, {"url": "http://example.com"}) is None
    err = validate_arguments(descriptor, {"url": "ftp://example.com"})
    assert err is not None
    assert "URL" in err


def test_validate_path_rejects_empty_string() -> None:
    descriptor = ToolDescriptor(
        name="readfile",
        description="x",
        parameters_schema={
            "path": ToolParameter(kind=ToolParameterKind.PATH, description="p"),
        },
    )
    assert validate_arguments(descriptor, {"path": "~/notes.md"}) is None
    err = validate_arguments(descriptor, {"path": ""})
    assert err is not None


def test_validate_enum_constraint() -> None:
    descriptor = ToolDescriptor(
        name="pick",
        description="x",
        parameters_schema={
            "mode": ToolParameter(
                kind=ToolParameterKind.STRING, description="m",
                enum=("read", "write"),
            ),
        },
    )
    assert validate_arguments(descriptor, {"mode": "read"}) is None
    err = validate_arguments(descriptor, {"mode": "delete"})
    assert err is not None
    assert "must be one of" in err
