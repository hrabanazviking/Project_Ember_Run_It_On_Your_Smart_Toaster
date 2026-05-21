"""``read_local_file`` — first-party tool that reads UTF-8 files under HOME.

Approval policy is :class:`ApprovalPolicy.PER_CALL` — the operator
sees the exact path being read before each invocation.

The sandbox refuses, in order:

1. Non-string ``path``.
2. Paths that resolve (symlinks followed) to anywhere outside
   ``Path.home()``.
3. Paths inside the explicit denylist:
   ``~/.ssh/``, ``~/.ember/secrets/``, ``~/.pgpass``,
   ``~/.aws/``, ``~/.kube/``, ``~/.gnupg/``.
4. Non-files (directories, symlink loops, special files).
5. Files larger than ``_MAX_FILE_BYTES`` (256 KiB).

Refusals come back as :class:`ToolReply` with ``error=...`` and an
empty ``output``. The audit log records the proposed path; the file
contents are never read on a refusal path.
"""

from __future__ import annotations

import time
from pathlib import Path

from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi.tools.registry import register

_NAME = "read_local_file"
_MAX_FILE_BYTES = 256 * 1024  # 256 KiB; Funi context windows are small

# Denylist relative to HOME — every entry is resolved into
# ``Path.home() / entry`` before comparison.
_DENYLIST_RELATIVE: tuple[str, ...] = (
    ".ssh",
    ".ember/secrets",
    ".pgpass",
    ".aws",
    ".kube",
    ".gnupg",
    ".password-store",
)


_DESCRIPTOR = ToolDescriptor(
    name=_NAME,
    description=(
        "Read a UTF-8 text file from the operator's home directory. "
        "Refuses paths outside $HOME and a small denylist of secret-bearing "
        "subdirectories. Files larger than 256 KiB are refused."
    ),
    parameters_schema={
        "path": ToolParameter(
            kind=ToolParameterKind.PATH,
            description=(
                "Absolute or ~-expanded path under $HOME. The host resolves "
                "symlinks before sandbox checks."
            ),
        ),
    },
    required_approval=ApprovalPolicy.PER_CALL,
    timeout_s=5.0,
)


def _execute(call: ToolCall) -> ToolReply:
    started = time.monotonic()
    raw_path = call.arguments.get("path")

    if not isinstance(raw_path, str) or not raw_path:
        return ToolReply(
            call_id=call.call_id,
            error="read_local_file: 'path' must be a non-empty string",
            elapsed_s=time.monotonic() - started,
        )

    refusal = _sandbox_check(raw_path)
    if refusal is not None:
        return ToolReply(
            call_id=call.call_id,
            error=refusal,
            elapsed_s=time.monotonic() - started,
        )

    # Resolve once more for the read; _sandbox_check returns the safe path.
    safe_path = Path(raw_path).expanduser().resolve()

    try:
        size = safe_path.stat().st_size
    except OSError as exc:
        return ToolReply(
            call_id=call.call_id,
            error=f"read_local_file: stat failed: {type(exc).__name__}",
            elapsed_s=time.monotonic() - started,
        )

    if size > _MAX_FILE_BYTES:
        return ToolReply(
            call_id=call.call_id,
            error=(
                f"read_local_file: file is {size} bytes; "
                f"sandbox limit is {_MAX_FILE_BYTES} bytes (256 KiB)"
            ),
            elapsed_s=time.monotonic() - started,
        )

    try:
        text = safe_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return ToolReply(
            call_id=call.call_id,
            error=f"read_local_file: read failed: {type(exc).__name__}",
            elapsed_s=time.monotonic() - started,
        )

    return ToolReply(
        call_id=call.call_id,
        output=text,
        elapsed_s=time.monotonic() - started,
    )


def _sandbox_check(raw_path: str) -> str | None:  # noqa: PLR0911 — each refusal is one named early-return
    """Return None if the path is safe; an operator-readable refusal otherwise.

    Resolves symlinks before all checks — the sandbox must not be
    fooled by a symlink that points outside HOME (or into the denylist).
    """
    try:
        candidate = Path(raw_path).expanduser()
    except (RuntimeError, ValueError) as exc:
        return f"read_local_file: refused: cannot parse path: {exc}"

    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        return f"read_local_file: refused: resolve failed: {type(exc).__name__}"

    if not resolved.exists():
        return f"read_local_file: refused: path does not exist: {resolved}"

    home = Path.home().resolve()
    try:
        resolved.relative_to(home)
    except ValueError:
        return (
            f"read_local_file: refused: path {resolved} is outside the "
            f"operator's home directory ({home})"
        )

    # Denylist check — entries are relative to HOME.
    for relative in _DENYLIST_RELATIVE:
        forbidden = (home / relative).resolve()
        # We refuse the forbidden path itself AND anything beneath it.
        if resolved == forbidden:
            return (
                f"read_local_file: refused: path {resolved} is on the "
                f"sandbox denylist"
            )
        try:
            resolved.relative_to(forbidden)
        except ValueError:
            continue  # not under this entry; check the next
        return (
            f"read_local_file: refused: path {resolved} is under the "
            f"sandbox denylist entry {forbidden}"
        )

    # Reject non-regular files (directories, special files, broken symlinks).
    if resolved.is_dir():
        return f"read_local_file: refused: {resolved} is a directory"
    if not resolved.is_file():
        return f"read_local_file: refused: {resolved} is not a regular file"

    return None


# Side-effect registration — see ember.tools README §1.
register(_DESCRIPTOR, _execute)


__all__: list[str] = []
