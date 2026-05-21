"""Append-only JSONL audit log for tool invocations (ADR 0011 §2.7).

One file per UTC day at ``<config_root>/state/tool_audit/<date>.jsonl``,
created on first append. Each record is a single-line JSON object
written with a single ``write`` call to the OS — short writes truncate
cleanly, no partial-line records survive a crash.

The audit log is the operator's forensic trail. It records every tool
proposal, every approval decision, every execution outcome. Sensitive
argument values can be redacted per :class:`ToolDescriptor`'s
``redacted_arg_names`` — the framework substitutes ``"<redacted>"``
before serialising.
"""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from ember.schemas.tool import (
    ApprovalOutcome,
    ToolCall,
    ToolDescriptor,
    ToolError,
    ToolReply,
)

# Truncation cap for ``reply.output`` (ADR 0011 §2.7). Larger outputs
# get an ellipsis suffix — Episodes are the canonical source-of-truth
# for full reply text; the audit log is a forensic trail, not an
# archive.
OUTPUT_TRUNCATION_BYTES: Final[int] = 4 * 1024  # 4 KiB

DIR_MODE: Final[int] = 0o700
FILE_MODE: Final[int] = 0o600


class AuditLog:
    """Per-process audit-log writer.

    Constructed once with a ``config_root``; ``record()`` is called
    once per tool invocation. The instance keeps no file handle open
    between records — opens are short-lived, append-only, line-buffered
    so cross-process safety on POSIX is the kernel's append guarantee.
    """

    def __init__(self, config_root: Path, *, ember_version: str = "") -> None:
        self._root = Path(config_root).expanduser()
        self._ember_version = ember_version

    @property
    def root_dir(self) -> Path:
        """The directory the audit log writes into."""
        return self._root / "state" / "tool_audit"

    def path_for(self, when: datetime) -> Path:
        """The audit-log file for ``when`` (UTC date)."""
        return self.root_dir / f"{when.astimezone(UTC).strftime('%Y-%m-%d')}.jsonl"

    def record(
        self,
        *,
        call: ToolCall,
        descriptor: ToolDescriptor | None,
        approval: ApprovalOutcome,
        reply: ToolReply | None,
        when: datetime | None = None,
    ) -> Path:
        """Append a single record to today's audit file.

        Returns the path written to so callers (and tests) can verify
        the daily-rotation behaviour. Raises :class:`ToolError` when
        the audit directory cannot be created or written to — Phase 16
        callers will treat that as a hard failure (an audit miss is
        worse than an unexecuted tool).
        """
        timestamp = (when or datetime.now(tz=UTC)).astimezone(UTC)
        record = _serialise_record(
            timestamp=timestamp,
            call=call,
            descriptor=descriptor,
            approval=approval,
            reply=reply,
            ember_version=self._ember_version,
        )

        try:
            self._ensure_dir()
            path = self.path_for(timestamp)
            line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            payload = line.encode("utf-8")

            # Append the line. POSIX guarantees write(2) appends are
            # serialized when O_APPEND is set, but a single os.write()
            # may return fewer bytes than requested (especially when
            # the payload exceeds PIPE_BUF or the disk is filling up).
            # The hardening pass added a write-until-complete loop so
            # a short write is retried rather than corrupting the line.
            fd = os.open(
                str(path),
                os.O_WRONLY | os.O_CREAT | os.O_APPEND,
                FILE_MODE,
            )
            try:
                _write_all(fd, payload)
            finally:
                os.close(fd)
            # Always chmod — even on existing files. Hardening pass
            # tightened this from "only on freshly-created files",
            # because a file accidentally created with the wrong mode
            # (e.g. by an external process between our checks) would
            # silently keep its wider permissions. The chmod is
            # idempotent so the cost is one syscall per audit record.
            if os.name != "nt":
                import contextlib  # noqa: PLC0415 — narrowly scoped
                with contextlib.suppress(OSError):
                    os.chmod(path, FILE_MODE)
            return path
        except OSError as exc:
            raise ToolError(
                f"audit log write failed at {self.root_dir}: {exc}"
            ) from exc

    # --------------------------------------------------------------- #
    # Internals                                                       #
    # --------------------------------------------------------------- #

    def _ensure_dir(self) -> None:
        directory = self.root_dir
        directory.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            return  # Windows ACLs don't carry Unix mode bits meaningfully.
        # Narrow OSError suppression — chmod failing with EOPNOTSUPP
        # (unusual FS) is fine, but EROFS / EACCES / ENOSPC are real
        # problems the operator needs to see (the audit log won't
        # work). Hardening pass tightened this.
        import errno  # noqa: PLC0415 — narrowly scoped
        try:
            current = stat.S_IMODE(directory.stat().st_mode)
            if current != DIR_MODE:
                os.chmod(directory, DIR_MODE)
        except OSError as exc:
            if exc.errno not in {errno.EOPNOTSUPP, errno.EPERM}:
                raise


# --------------------------------------------------------------------- #
# Serialisation helpers                                                 #
# --------------------------------------------------------------------- #


def _serialise_record(  # noqa: PLR0913 — the audit record is naturally a fan-in of call/descriptor/approval/reply
    *,
    timestamp: datetime,
    call: ToolCall,
    descriptor: ToolDescriptor | None,
    approval: ApprovalOutcome,
    reply: ToolReply | None,
    ember_version: str,
) -> dict[str, Any]:
    """Build the dict that becomes one JSONL record."""
    redacted_names = descriptor.redacted_arg_names if descriptor else ()
    record: dict[str, Any] = {
        "ts": timestamp.isoformat(),
        "call_id": call.call_id,
        "tool": call.name,
        "arguments": _redact_arguments(call.arguments, redacted_names),
        "approval": approval.value,
    }
    if descriptor is not None:
        record["approval_policy"] = descriptor.required_approval.value
    if reply is not None:
        record["reply"] = _serialise_reply(reply)
    if ember_version:
        record["ember_version"] = ember_version
    return record


def _redact_arguments(
    arguments: Mapping[str, object],
    redacted_names: tuple[str, ...],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    redact_set = set(redacted_names)
    for name, value in arguments.items():
        if name in redact_set:
            out[name] = "<redacted>"
        else:
            out[name] = _to_jsonable(value)
    return out


def _serialise_reply(reply: ToolReply) -> dict[str, Any]:
    text = reply.output or ""
    truncated = False
    encoded = text.encode("utf-8")
    if len(encoded) > OUTPUT_TRUNCATION_BYTES:
        # Slice on a UTF-8 boundary to avoid mid-codepoint cuts. The
        # decode-then-re-encode loop is correct but pricey; we slice
        # the byte-string then strip the trailing partial codepoint by
        # decoding with ``errors="ignore"``.
        text = encoded[:OUTPUT_TRUNCATION_BYTES].decode(
            "utf-8", errors="ignore"
        ) + "..."
        truncated = True
    return {
        "output": text,
        "error": reply.error,
        "elapsed_s": float(reply.elapsed_s),
        "output_truncated": truncated,
    }


def _to_jsonable(value: object) -> Any:
    """Coerce arbitrary tool-arg values into a JSON-serialisable form.

    The strict schema in ADR 0011 §2.2 limits argument kinds to the
    JSON-native set already (string / number / boolean / path-as-str /
    url-as-str), so the default ``json.dumps`` behaviour covers
    almost everything; this is the belt-and-suspenders fallback.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    return repr(value)


def _write_all(fd: int, payload: bytes) -> None:
    """Loop on ``os.write`` until every byte is written.

    POSIX permits ``write(2)`` to return fewer bytes than requested.
    For audit records exceeding PIPE_BUF (~4 KiB on most filesystems)
    or under disk pressure, a single ``os.write`` could leave a
    partial JSONL line on disk — corrupting the file for downstream
    parsers. This helper guarantees the line is either fully written
    or surfaces an OSError that the caller turns into ``ToolError``.
    """
    view = memoryview(payload)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            # Defensive: a non-blocking write returning 0 would loop
            # forever. Treat as failure to surface the issue.
            raise OSError(
                f"audit write returned {n} bytes from a {len(payload)}-byte "
                f"payload; file may be left in an inconsistent state"
            )
        view = view[n:]


__all__ = [
    "DIR_MODE",
    "FILE_MODE",
    "OUTPUT_TRUNCATION_BYTES",
    "AuditLog",
]
