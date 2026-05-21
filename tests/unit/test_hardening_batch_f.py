"""Regression tests for the post-d5d2792 Batch F hardening sweep.

Each test pins one defensive measure shipped on 2026-05-21 after
*"please fix all bugs and make all hardening, my friend (round 3)"* —
the Auditor surfaces this round were render.py / ingest+journal /
registry+approval / config-overlay (the surfaces Batches A+B+C+D+E
under-covered).

If a test here fails, the corresponding defense was reverted.
"""

from __future__ import annotations

from collections.abc import Mapping  # used by dataclass annotation below
from pathlib import Path

import pytest

from ember.schemas.errors import IngestError
from ember.schemas.tool import (
    ApprovalPolicy,
    ToolDescriptor,
    ToolError,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi.tools import audit as audit_mod
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools import register
from ember.spark.munnr import render
from ember.well.smidja.embed_client import _coerce_vector


@pytest.fixture(autouse=True)
def _isolate_registry():
    registry_clear()
    yield
    registry_clear()


# --------------------------------------------------------------------- #
# Batch F — local_files source: sensitive-name + special-file defences  #
# --------------------------------------------------------------------- #


def test_local_files_walk_skips_dotenv_and_sensitive_names(
    tmp_path: Path,
) -> None:
    """Sensitive filenames (.env, *.key, .pgpass) must be skipped even
    if their suffix would otherwise match the include set. Without
    this, ``ember well ingest ~/`` would vectorise the operator's
    secrets into the Well."""
    from ember.well.smidja.local_files.source import walk  # noqa: PLC0415

    # Two valid markdown files + one .env file with the same .md
    # extension equivalent. We include ".env" without an extension so
    # we need to extend the include suffixes to test the denylist.
    (tmp_path / "notes.md").write_text("safe content", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=hunter2", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY DATA", encoding="utf-8")
    (tmp_path / "config.md").write_text("safe content", encoding="utf-8")

    # Use a permissive include set so the denylist is the only thing
    # protecting these files.
    results = list(walk(
        tmp_path,
        include_suffixes=(".md", ".env", ""),
    ))
    names = sorted(p.path.name for p in results)
    assert "notes.md" in names
    assert "config.md" in names
    assert ".env" not in names, "sensitive .env file was ingested"
    assert "id_rsa" not in names, "private key was ingested"


def test_local_files_walk_skips_non_regular_files(
    tmp_path: Path,
) -> None:
    """FIFOs, device nodes, sockets must be skipped — read_bytes() on
    /dev/zero blocks reading forever. Skipping them avoids a hard hang."""
    import os  # noqa: PLC0415

    from ember.well.smidja.local_files.source import walk  # noqa: PLC0415

    # Create a regular file + a FIFO with the same suffix.
    (tmp_path / "ok.md").write_text("content", encoding="utf-8")
    fifo_path = tmp_path / "spooky.md"
    try:
        os.mkfifo(fifo_path)
    except (OSError, NotImplementedError):
        pytest.skip("FIFOs not supported on this platform")

    results = list(walk(tmp_path))
    names = sorted(p.path.name for p in results)
    assert "ok.md" in names
    assert "spooky.md" not in names


def test_local_files_walk_skips_oversize_files(tmp_path: Path) -> None:
    """Files larger than the configured cap must be skipped with a
    warning — protects against runaway memory use on a 50 GB log."""
    from ember.well.smidja.local_files.source import walk  # noqa: PLC0415

    small = tmp_path / "small.md"
    big = tmp_path / "big.md"
    small.write_text("tiny", encoding="utf-8")
    big.write_text("X" * 1000, encoding="utf-8")

    # Cap below the big file but above the small one.
    results = list(walk(tmp_path, max_file_bytes=500))
    names = sorted(p.path.name for p in results)
    assert "small.md" in names
    assert "big.md" not in names


# --------------------------------------------------------------------- #
# Batch F — embed_client: NaN / Inf / malformed vector defence          #
# --------------------------------------------------------------------- #


def test_coerce_vector_rejects_nan_and_inf() -> None:
    """Non-finite floats in embeddings would crash pgvector at insert
    time with a cryptic ``data exception``. Catch them at parse time."""
    with pytest.raises(ValueError, match="non-finite"):
        _coerce_vector([1.0, float("nan"), 0.5], expected_dim=None)
    with pytest.raises(ValueError, match="non-finite"):
        _coerce_vector([1.0, float("inf"), 0.5], expected_dim=None)
    with pytest.raises(ValueError, match="non-finite"):
        _coerce_vector([1.0, float("-inf"), 0.5], expected_dim=None)


def test_coerce_vector_rejects_non_numeric_scalars() -> None:
    """A stringified-float entry would silently float() its way through
    before the hardening pass; now refused at parse time."""
    with pytest.raises(TypeError):
        _coerce_vector([1.0, "0.5", 0.3], expected_dim=None)
    with pytest.raises(TypeError):
        _coerce_vector([1.0, None, 0.3], expected_dim=None)
    with pytest.raises(TypeError):
        _coerce_vector([1.0, True, 0.3], expected_dim=None)


def test_coerce_vector_enforces_expected_dim() -> None:
    """A misaligned dim would corrupt the vector store; refuse with a
    clear error rather than letting the bad row through."""
    with pytest.raises(ValueError, match="dims, expected"):
        _coerce_vector([1.0, 0.5], expected_dim=3)


def test_coerce_vector_accepts_clean_input() -> None:
    """The happy path still works."""
    out = _coerce_vector([1.0, 2.0, 3.0], expected_dim=3)
    assert out == (1.0, 2.0, 3.0)
    out = _coerce_vector([1, 2, 3], expected_dim=None)  # int-as-float
    assert out == (1.0, 2.0, 3.0)


# --------------------------------------------------------------------- #
# Batch F — registry: register-time validation of name + executor       #
# --------------------------------------------------------------------- #


def _good_descriptor(name: str = "good_tool") -> ToolDescriptor:
    return ToolDescriptor(
        name=name,
        description="a test tool",
        parameters_schema={
            "q": ToolParameter(kind=ToolParameterKind.STRING, description="q"),
        },
        required_approval=ApprovalPolicy.PER_CALL,
    )


def _noop_executor(call) -> ToolReply:
    return ToolReply(call_id=call.call_id, output="ok")


def test_registry_refuses_empty_tool_name() -> None:
    """Empty / whitespace tool names would corrupt the audit log and
    confuse the operator. Refuse at register time."""
    with pytest.raises(ToolError, match="invalid"):
        register(_good_descriptor(name=""), _noop_executor)
    with pytest.raises(ToolError, match="invalid"):
        register(_good_descriptor(name="   "), _noop_executor)


def test_registry_refuses_tool_name_with_control_chars() -> None:
    """A tool name with a newline would break per-line audit log
    parsing; with ESC would let a tool rewrite the operator's
    terminal banner. Refuse anything outside the allowed shape."""
    with pytest.raises(ToolError, match="invalid"):
        register(_good_descriptor(name="bad\nname"), _noop_executor)
    with pytest.raises(ToolError, match="invalid"):
        register(_good_descriptor(name="bad\x1bname"), _noop_executor)


def test_registry_refuses_tool_name_with_shell_metachars() -> None:
    """Shell metachars in tool names would confuse audit-log readers
    that pipe through shell tools. Refuse them."""
    for bad in ("ls;rm", "a/b", "a b", "a.b", "a-b"):
        with pytest.raises(ToolError, match="invalid"):
            register(_good_descriptor(name=bad), _noop_executor)
        registry_clear()


def test_registry_refuses_non_callable_executor() -> None:
    """A non-callable executor would crash at call time with
    ``TypeError: 'str' object is not callable``. Refuse at register
    time so the error names the tool that's broken."""
    with pytest.raises(ToolError, match="not callable"):
        register(_good_descriptor(), "not a function")  # type: ignore[arg-type]
    with pytest.raises(ToolError, match="not callable"):
        register(_good_descriptor(), None)  # type: ignore[arg-type]


def test_registry_accepts_well_formed_name() -> None:
    """Happy path still works."""
    register(_good_descriptor(name="search_well"), _noop_executor)
    register(_good_descriptor(name="A_Tool_2"), _noop_executor)
    register(_good_descriptor(name="_underscored"), _noop_executor)


# --------------------------------------------------------------------- #
# Batch F — audit: recursive redaction of nested-dict args              #
# --------------------------------------------------------------------- #


def test_audit_redacts_nested_dict_arguments() -> None:
    """A tool that accepts ``payload={"token": "...", "path": "..."}``
    with ``redacted_arg_names=("token",)`` must not leak the token to
    the audit log via the nested ``payload`` dict."""
    out = audit_mod._redact_arguments(
        {"payload": {"token": "secret123", "path": "/etc/x"}},
        redacted_names=("token",),
    )
    assert out["payload"]["token"] == "<redacted>"
    assert out["payload"]["path"] == "/etc/x"


def test_audit_redacts_through_list_of_dicts() -> None:
    """Redaction also walks through list elements (a tool that takes
    a list of credential records should not leak any of them)."""
    out = audit_mod._redact_arguments(
        {"items": [{"token": "a", "name": "x"}, {"token": "b", "name": "y"}]},
        redacted_names=("token",),
    )
    assert out["items"][0]["token"] == "<redacted>"
    assert out["items"][0]["name"] == "x"
    assert out["items"][1]["token"] == "<redacted>"


# --------------------------------------------------------------------- #
# Batch F — config validate: empty-string path refused                  #
# --------------------------------------------------------------------- #


def test_config_validate_refuses_empty_path_string() -> None:
    """``path: ""`` would coerce to ``Path(".")`` (the current working
    directory) silently. Refuse the typo so the error names the field."""
    from dataclasses import dataclass  # noqa: PLC0415

    from ember.config.validate import coerce_to_dataclass  # noqa: PLC0415
    from ember.schemas.errors import ConfigError  # noqa: PLC0415

    @dataclass(frozen=True, slots=True)
    class Cfg:
        path: Path

    with pytest.raises(ConfigError, match="must not be empty"):
        coerce_to_dataclass(Cfg, {"path": ""})
    with pytest.raises(ConfigError, match="must not be empty"):
        coerce_to_dataclass(Cfg, {"path": "   "})


# --------------------------------------------------------------------- #
# Batch F — config validate: mapping value coercion                     #
# --------------------------------------------------------------------- #


def test_config_validate_coerces_mapping_values() -> None:
    """``Mapping[str, str]`` previously accepted ``{"a": 123}`` because
    the coercer returned ``dict(value)`` raw. Walk values now."""
    from dataclasses import dataclass, field  # noqa: PLC0415

    from ember.config.validate import coerce_to_dataclass  # noqa: PLC0415
    from ember.schemas.errors import ConfigError  # noqa: PLC0415

    @dataclass(frozen=True, slots=True)
    class _MapCfg:
        labels: Mapping[str, str] = field(default_factory=dict)

    # Clean input still works.
    cfg = coerce_to_dataclass(_MapCfg, {"labels": {"a": "x", "b": "y"}})
    assert cfg.labels == {"a": "x", "b": "y"}
    # Non-string value gets rejected.
    with pytest.raises(ConfigError, match="expected str"):
        coerce_to_dataclass(_MapCfg, {"labels": {"a": 123}})


# --------------------------------------------------------------------- #
# Batch F — journal: graceful from_payload on malformed input           #
# --------------------------------------------------------------------- #


def test_journal_from_payload_refuses_missing_required_fields() -> None:
    """A corrupt journal file (truncated write, version skew) used to
    raise ``KeyError`` from the bare ``payload["job_id"]`` access."""
    from ember.well.smidja.journal import JournalState  # noqa: PLC0415

    with pytest.raises(IngestError, match="missing required field"):
        JournalState.from_payload({})
    with pytest.raises(IngestError, match="missing required field"):
        JournalState.from_payload({"job_id": "x"})


def test_journal_from_payload_refuses_unknown_source_kind() -> None:
    """An unknown ``source_kind`` value used to raise a bare
    ``ValueError`` from the enum constructor."""
    from ember.well.smidja.journal import JournalState  # noqa: PLC0415

    payload = {
        "job_id": "x",
        "source_kind": "no_such_kind",
        "source_root": "/",
        "started_at": "now",
        "last_heartbeat": "now",
    }
    with pytest.raises(IngestError, match="unknown source_kind"):
        JournalState.from_payload(payload)


def test_journal_from_payload_refuses_non_dict_entries() -> None:
    """``entries`` being a list/string would crash at iteration time;
    catch it at parse time with a clear message."""
    from ember.schemas.ingest import IngestSourceKind  # noqa: PLC0415
    from ember.well.smidja.journal import JournalState  # noqa: PLC0415

    payload = {
        "job_id": "x",
        "source_kind": IngestSourceKind.LOCAL_FILES.value,
        "source_root": "/",
        "started_at": "now",
        "last_heartbeat": "now",
        "entries": ["not", "a", "dict"],
    }
    with pytest.raises(IngestError, match="entries"):
        JournalState.from_payload(payload)


# --------------------------------------------------------------------- #
# Batch F — render: terminal-control scrub                              #
# --------------------------------------------------------------------- #


def test_render_strips_ansi_from_tool_error() -> None:
    """Tool errors can contain attacker-controllable ANSI escapes that
    would clear the operator's terminal or rewrite the window title.
    Strip them before printing."""
    reply = ToolReply(
        call_id="c-1",
        output="",
        error="bad: \x1b[2J\x1b[Hcleared your screen",
    )
    desc = _good_descriptor(name="fetch_url")
    out = render.render_tool_reply(reply, desc)
    assert "\x1b[" not in out
    assert "bad:" in out


def test_render_strips_ansi_from_tool_output() -> None:
    """Tool output can carry control bytes from a hostile HTTP response
    or file content. Strip before display; the raw text still goes to
    the audit log via _serialise_reply."""
    reply = ToolReply(
        call_id="c-2",
        output="hello\x1b[31mRED\x1b[0m world",
        error=None,
    )
    desc = _good_descriptor(name="fetch_url")
    out = render.render_tool_reply(reply, desc)
    assert "\x1b[" not in out
    assert "hello" in out
    assert "world" in out


def test_render_strips_osc_title_rewrite() -> None:
    """OSC sequences could rewrite the terminal window title — a
    hostile fetch_url response could set it to ``[INFECTED]``. Strip."""
    reply = ToolReply(
        call_id="c-3",
        output="",
        error="error: \x1b]0;INFECTED\x07see above",
    )
    desc = _good_descriptor(name="fetch_url")
    out = render.render_tool_reply(reply, desc)
    assert "\x1b]" not in out
    assert "\x07" not in out


def test_render_strips_bidi_override_from_tool_output() -> None:
    """A U+202E in tool output would flip the visual reading order on
    the operator's terminal. Strip the format-category char."""
    reply = ToolReply(
        call_id="c-4",
        output=f"file{chr(0x202E)}gnp.exe",
        error=None,
    )
    desc = _good_descriptor(name="fetch_url")
    out = render.render_tool_reply(reply, desc)
    assert chr(0x202E) not in out


def test_render_preserves_newlines_and_tabs() -> None:
    """Newlines and tabs are SAFE control chars for our line-by-line
    rendering; they must survive the scrub."""
    reply = ToolReply(
        call_id="c-5",
        output="line1\nline2\tcolumn",
        error=None,
    )
    desc = _good_descriptor(name="fetch_url")
    out = render.render_tool_reply(reply, desc)
    assert "line1" in out
    assert "line2" in out
    assert "column" in out
