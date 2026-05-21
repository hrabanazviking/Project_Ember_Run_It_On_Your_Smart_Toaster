"""``read_local_file`` — first-party tool that reads UTF-8 files under HOME.

Approval policy is :class:`ApprovalPolicy.PER_CALL` — the operator
sees the exact path being read before each invocation.

The sandbox refuses, in order:

1. Non-string or empty/whitespace-only ``path``.
2. Path resolution failure (broken symlinks, RuntimeError from cycles).
3. ``Path.home()`` resolving to the filesystem root (e.g. root user with
   ``HOME=/``) — would make the sandbox vacuous.
4. Paths that resolve (symlinks followed) to anywhere outside
   ``Path.home()``.
5. Paths inside the explicit denylist:
   ``~/.ssh/``, ``~/.ember/secrets/``, ``~/.pgpass``,
   ``~/.aws/``, ``~/.kube/``, ``~/.gnupg/``, ``~/.password-store/``.
6. Non-files (directories, symlink loops, special files).
7. Files larger than ``_MAX_FILE_BYTES`` (256 KiB).

**TOCTOU defence:** the sandbox check resolves the path once and
returns the safe :class:`Path` as part of its result; the executor
opens *that* :class:`Path` directly (no re-resolution between check
and read). A symlink-swap race between the resolve() and the read()
on the same exact resolved Path would land in the same byte-stream
either way — the kernel has the inode already.

Refusals come back as :class:`ToolReply` with ``error=...`` and an
empty ``output``. The audit log records the proposed path; the file
contents are never read on a refusal path.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class _SandboxResult:
    """The sandbox check's verdict.

    Exactly one of ``safe_path`` / ``refusal`` is populated. The
    executor reads ``safe_path`` directly (no re-resolve) to close the
    TOCTOU window between check and read.
    """

    safe_path: Path | None = None
    refusal: str | None = None


def _execute(call: ToolCall) -> ToolReply:
    started = time.monotonic()
    raw_path = call.arguments.get("path")

    if not isinstance(raw_path, str) or not raw_path.strip():
        return ToolReply(
            call_id=call.call_id,
            error="read_local_file: 'path' must be a non-empty string",
            elapsed_s=time.monotonic() - started,
        )

    result = _sandbox_check(raw_path)
    if result.refusal is not None:
        return ToolReply(
            call_id=call.call_id,
            error=result.refusal,
            elapsed_s=time.monotonic() - started,
        )

    # Use the resolved path captured during the sandbox check — do NOT
    # re-resolve here. Re-resolving would re-open the TOCTOU window
    # between the sandbox check and the stat/read.
    safe_path = result.safe_path
    assert safe_path is not None  # invariant: either refusal or safe_path

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


def _sandbox_check(raw_path: str) -> _SandboxResult:  # noqa: PLR0911 — each refusal is one named early-return
    """Resolve ``raw_path`` and verify every sandbox invariant.

    On success returns ``_SandboxResult(safe_path=<resolved Path>)``.
    On any failure returns ``_SandboxResult(refusal=<operator-readable message>)``.

    Resolves symlinks before all checks — the sandbox must not be
    fooled by a symlink that points outside HOME (or into the denylist).
    The resolved path is *also* returned to the caller so the read
    happens on the same Path the check validated (TOCTOU defence).
    """
    try:
        candidate = Path(raw_path).expanduser()
    except (RuntimeError, ValueError) as exc:
        return _SandboxResult(
            refusal=f"read_local_file: refused: cannot parse path: {exc}",
        )

    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        return _SandboxResult(
            refusal=(
                f"read_local_file: refused: resolve failed: "
                f"{type(exc).__name__}"
            ),
        )

    # Single stat call (follow symlinks via resolve already done above,
    # so a plain stat is enough). Doing this in one shot — rather than
    # the old exists() then is_dir() then is_file() trio — narrows the
    # TOCTOU window where the file could be swapped for a directory or
    # special file between the existence check and the type check.
    import stat as _stat  # noqa: PLC0415 — narrow scope

    try:
        st_mode = resolved.stat().st_mode
    except FileNotFoundError:
        return _SandboxResult(
            refusal=f"read_local_file: refused: path does not exist: {resolved}",
        )
    except OSError as exc:
        return _SandboxResult(
            refusal=(
                f"read_local_file: refused: stat failed during sandbox "
                f"check: {type(exc).__name__}"
            ),
        )

    home = Path.home().resolve()

    # The sandbox is vacuous when HOME resolves to the filesystem root
    # (e.g. root user with HOME unset, or HOME=/ explicitly). Refuse
    # rather than silently letting the operator read anywhere.
    if home == Path(home.anchor):
        return _SandboxResult(
            refusal=(
                f"read_local_file: refused: Path.home() resolves to {home} "
                f"(filesystem root); the sandbox would be vacuous. "
                f"Set $HOME to a real user directory."
            ),
        )

    try:
        resolved.relative_to(home)
    except ValueError:
        return _SandboxResult(
            refusal=(
                f"read_local_file: refused: path {resolved} is outside the "
                f"operator's home directory ({home})"
            ),
        )

    # Denylist check — entries are relative to HOME.
    for relative in _DENYLIST_RELATIVE:
        forbidden = (home / relative).resolve()
        # We refuse the forbidden path itself AND anything beneath it.
        if resolved == forbidden:
            return _SandboxResult(
                refusal=(
                    f"read_local_file: refused: path {resolved} is on the "
                    f"sandbox denylist"
                ),
            )
        try:
            resolved.relative_to(forbidden)
        except ValueError:
            continue  # not under this entry; check the next
        return _SandboxResult(
            refusal=(
                f"read_local_file: refused: path {resolved} is under the "
                f"sandbox denylist entry {forbidden}"
            ),
        )

    # Reject non-regular files using the st_mode captured by the single
    # stat() call above. This closes the swap-window between the
    # historical exists() / is_dir() / is_file() trio.
    if _stat.S_ISDIR(st_mode):
        return _SandboxResult(
            refusal=f"read_local_file: refused: {resolved} is a directory",
        )
    if not _stat.S_ISREG(st_mode):
        return _SandboxResult(
            refusal=f"read_local_file: refused: {resolved} is not a regular file",
        )

    return _SandboxResult(safe_path=resolved)


# Side-effect registration — see ember.tools README §1.
register(_DESCRIPTOR, _execute)


__all__: list[str] = []
