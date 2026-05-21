"""Append-only audit log (ADR 0011 §2.7).

Confirms daily rotation, redaction, atomicity (in the
single-os.write-per-line sense), permission bits, and output
truncation.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolError,
    ToolReply,
)
from ember.spark.funi.tools.audit import (
    DIR_MODE,
    FILE_MODE,
    OUTPUT_TRUNCATION_BYTES,
    AuditLog,
)

# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _descriptor(
    *,
    name: str = "search_well",
    required_approval: ApprovalPolicy = ApprovalPolicy.STANDING,
    redacted_arg_names: tuple[str, ...] = (),
) -> ToolDescriptor:
    return ToolDescriptor(
        name=name,
        description="t",
        required_approval=required_approval,
        redacted_arg_names=redacted_arg_names,
    )


def _call(
    *,
    call_id: str = "abc-123",
    name: str = "search_well",
    arguments: dict | None = None,
) -> ToolCall:
    return ToolCall(
        call_id=call_id,
        name=name,
        arguments=arguments or {"query": "Odin"},
    )


def _read_lines(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


# --------------------------------------------------------------------- #
# Basic record                                                          #
# --------------------------------------------------------------------- #


def test_record_appends_a_jsonl_line(tmp_path: Path) -> None:
    log = AuditLog(tmp_path, ember_version="0.1.9")
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=ToolReply(call_id="abc-123", output="ok", elapsed_s=0.012),
        when=when,
    )
    path = log.path_for(when)
    records = _read_lines(path)
    assert len(records) == 1
    r = records[0]
    assert r["tool"] == "search_well"
    assert r["call_id"] == "abc-123"
    assert r["approval"] == "auto_approved"
    assert r["approval_policy"] == "standing"
    assert r["arguments"] == {"query": "Odin"}
    assert r["reply"]["output"] == "ok"
    assert r["reply"]["error"] is None
    assert r["reply"]["elapsed_s"] == 0.012
    assert r["ember_version"] == "0.1.9"


def test_audit_directory_lives_under_state_tool_audit(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    assert log.root_dir == tmp_path / "state" / "tool_audit"


def test_record_returns_the_path_written(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    path = log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=None,
        when=when,
    )
    assert path == log.path_for(when)
    assert path.exists()


# --------------------------------------------------------------------- #
# Append-only behaviour                                                 #
# --------------------------------------------------------------------- #


def test_multiple_records_append_to_same_file(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    for i in range(3):
        log.record(
            call=_call(call_id=f"id-{i}"),
            descriptor=_descriptor(),
            approval=ApprovalOutcome.AUTO_APPROVED,
            reply=ToolReply(call_id=f"id-{i}"),
            when=when + timedelta(seconds=i),
        )
    records = _read_lines(log.path_for(when))
    assert [r["call_id"] for r in records] == ["id-0", "id-1", "id-2"]


def test_daily_rotation_to_new_file(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    day1 = datetime(2026, 5, 21, 23, 59, 0, tzinfo=UTC)
    day2 = datetime(2026, 5, 22, 0, 0, 1, tzinfo=UTC)

    p1 = log.record(
        call=_call(call_id="a"),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=None,
        when=day1,
    )
    p2 = log.record(
        call=_call(call_id="b"),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=None,
        when=day2,
    )
    assert p1 != p2
    assert "2026-05-21" in str(p1)
    assert "2026-05-22" in str(p2)
    assert len(_read_lines(p1)) == 1
    assert len(_read_lines(p2)) == 1


# --------------------------------------------------------------------- #
# Redaction                                                             #
# --------------------------------------------------------------------- #


def test_redacted_arg_names_replace_value_with_marker(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    log.record(
        call=_call(arguments={"path": "/etc/x", "token": "super-secret"}),
        descriptor=_descriptor(redacted_arg_names=("token",)),
        approval=ApprovalOutcome.APPROVED_THIS_CALL,
        reply=ToolReply(call_id="abc-123"),
        when=when,
    )
    record = _read_lines(log.path_for(when))[0]
    assert record["arguments"]["path"] == "/etc/x"
    assert record["arguments"]["token"] == "<redacted>"
    # And the raw file body must not contain the secret either.
    raw_body = log.path_for(when).read_text(encoding="utf-8")
    assert "super-secret" not in raw_body


# --------------------------------------------------------------------- #
# Output truncation                                                     #
# --------------------------------------------------------------------- #


def test_large_output_is_truncated_with_flag(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    big_text = "a" * (OUTPUT_TRUNCATION_BYTES + 1000)
    log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=ToolReply(call_id="abc-123", output=big_text),
        when=when,
    )
    record = _read_lines(log.path_for(when))[0]
    assert record["reply"]["output_truncated"] is True
    # The stored output is shorter than the original.
    assert len(record["reply"]["output"]) < len(big_text)
    assert record["reply"]["output"].endswith("...")


def test_small_output_is_not_truncated(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=ToolReply(call_id="abc-123", output="brief"),
        when=when,
    )
    record = _read_lines(log.path_for(when))[0]
    assert record["reply"]["output"] == "brief"
    assert record["reply"]["output_truncated"] is False


# --------------------------------------------------------------------- #
# Failure cases the audit log distinguishes                             #
# --------------------------------------------------------------------- #


def test_record_with_no_descriptor_still_writes(tmp_path: Path) -> None:
    """NO_SUCH_TOOL → no descriptor available, but we still log the
    proposed call_id + arguments."""
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    log.record(
        call=_call(name="ghost_tool"),
        descriptor=None,
        approval=ApprovalOutcome.NO_SUCH_TOOL,
        reply=None,
        when=when,
    )
    record = _read_lines(log.path_for(when))[0]
    assert record["tool"] == "ghost_tool"
    assert record["approval"] == "no_such_tool"
    assert "approval_policy" not in record  # no descriptor → omitted
    assert "reply" not in record           # no reply → omitted


def test_record_denied_call_has_no_reply(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.DENIED,
        reply=None,
        when=when,
    )
    record = _read_lines(log.path_for(when))[0]
    assert record["approval"] == "denied"
    assert "reply" not in record


# --------------------------------------------------------------------- #
# Permissions (POSIX only)                                              #
# --------------------------------------------------------------------- #


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_audit_directory_is_mode_700(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=None,
        when=datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC),
    )
    actual = stat.S_IMODE(log.root_dir.stat().st_mode)
    assert actual == DIR_MODE  # 0o700


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_audit_file_is_mode_600(tmp_path: Path) -> None:
    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    path = log.record(
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=None,
        when=when,
    )
    actual = stat.S_IMODE(path.stat().st_mode)
    assert actual == FILE_MODE  # 0o600


# --------------------------------------------------------------------- #
# Error path: unwritable directory                                       #
# --------------------------------------------------------------------- #


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_record_raises_tool_error_when_directory_is_a_file(tmp_path: Path) -> None:
    """Block out the state/ path with a regular file so the mkdir
    fails — exercises the audit-write OSError branch."""
    (tmp_path / "state").write_text("not a dir", encoding="utf-8")
    log = AuditLog(tmp_path)
    with pytest.raises(ToolError, match="audit log write failed"):
        log.record(
            call=_call(),
            descriptor=_descriptor(),
            approval=ApprovalOutcome.AUTO_APPROVED,
            reply=None,
            when=datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC),
        )
