"""Regression tests for the post-slice-2 Batch-B defensive hardening sweep.

Each test pins a specific defensive measure introduced during the
2026-05-21 hardening pass. If a test fails, that defense was reverted.

See ``test_hardening_batch_a.py`` for the higher-severity sandbox /
lifecycle fixes.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from ember.schemas.tool import (
    ApprovalOutcome,
    ToolCall,
    ToolDescriptor,
    ToolReply,
)
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools.audit import AuditLog, _write_all


@pytest.fixture(autouse=True)
def _isolate_registry():
    """Some tests below reload tool modules — clear between cases so the
    side-effect register() doesn't trip the duplicate-registration check."""
    registry_clear()
    yield
    registry_clear()


# --------------------------------------------------------------------- #
# Audit log — write-until-complete loop                                 #
# --------------------------------------------------------------------- #


def test_write_all_loops_on_short_writes(tmp_path: Path) -> None:
    """Hardening: a short ``os.write`` no longer corrupts the JSONL line.

    Drive ``_write_all`` against a real file descriptor where the OS
    happily writes everything, then drive it against a stub fd that
    returns short. Either way, every byte lands.
    """
    payload = (b"x" * 10000) + b"\n"
    fd = os.open(
        str(tmp_path / "writeall.log"),
        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        0o600,
    )
    try:
        _write_all(fd, payload)
    finally:
        os.close(fd)
    written = (tmp_path / "writeall.log").read_bytes()
    assert written == payload


def test_write_all_raises_on_zero_byte_write() -> None:
    """Hardening: a malfunctioning fd that returns 0 surfaces as OSError
    rather than looping forever."""
    fake_fd = 999

    def _bad_write(_fd: int, _buf) -> int:
        return 0

    with patch("os.write", side_effect=_bad_write), pytest.raises(
        OSError, match="returned 0 bytes",
    ):
        _write_all(fake_fd, b"hello")


def test_audit_log_large_record_round_trips(tmp_path: Path) -> None:
    """Hardening regression: an audit record larger than POSIX PIPE_BUF
    (~4 KiB) must land as a single complete JSONL line, not a partial
    write that corrupts the file."""
    big_output = "y" * 8000  # ~8 KB output — well over PIPE_BUF
    log = AuditLog(tmp_path, ember_version="hardening-test")
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)
    log.record(
        call=ToolCall(call_id="big-1", name="x", arguments={"k": "v"}),
        descriptor=ToolDescriptor(name="x", description="x"),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=ToolReply(call_id="big-1", output=big_output),
        when=when,
    )
    contents = log.path_for(when).read_text(encoding="utf-8").splitlines()
    assert len(contents) == 1
    parsed = json.loads(contents[0])
    # Output is truncated to 4 KiB by AuditLog itself, but the *record*
    # (with metadata) is well over 4 KiB; the write_all loop is what
    # makes that safe.
    assert parsed["tool"] == "x"
    assert parsed["reply"]["output_truncated"] is True


# --------------------------------------------------------------------- #
# Config writer — explicit mode 0o600                                   #
# --------------------------------------------------------------------- #


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits only")
def test_config_writer_emits_mode_600_regardless_of_umask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hardening: the operator's umask used to leak into ember.yaml's
    permission bits via NamedTemporaryFile's defaults. Now the writer
    sets 0o600 explicitly."""
    from ember.config import write_ember_config  # noqa: PLC0415
    from ember.schemas.config import IdentityConfig  # noqa: PLC0415

    # Force a permissive umask. NamedTemporaryFile previously honoured
    # this and created the file world-readable.
    monkeypatch.setattr(os, "umask", lambda _new: 0o000)
    os.umask(0o000)

    written = write_ember_config(tmp_path, IdentityConfig())
    mode = stat.S_IMODE(written.stat().st_mode)
    assert mode == 0o600, f"expected 0o600, got {oct(mode)}"


# --------------------------------------------------------------------- #
# Ollama NDJSON frame size cap                                          #
# --------------------------------------------------------------------- #


def test_ollama_aborts_on_oversize_ndjson_frame() -> None:
    """Hardening: a runaway server pushing a 10 MB single line into the
    NDJSON stream is treated as a typed ERROR chunk rather than letting
    Python OOM."""
    from ember.spark.funi.ollama.adapter import (  # noqa: PLC0415
        _MAX_NDJSON_FRAME_BYTES,
        OllamaFuni,
    )

    huge = b"x" * (_MAX_NDJSON_FRAME_BYTES + 1) + b"\n"

    class _BigResp:
        def __iter__(self):
            return iter([huge])

        def close(self) -> None:
            return None

    adapter = OllamaFuni(
        base_url="http://nope", model_id="fake", options={},
    )
    chunks = list(adapter._iter_ndjson_chunks(_BigResp()))
    assert len(chunks) == 1
    final = chunks[0]
    assert final.done is True
    from ember.schemas.funi import FinishReason  # noqa: PLC0415
    assert final.finish_reason is FinishReason.ERROR
    assert "exceeded" in final.text_delta


def test_ollama_ndjson_cap_is_at_least_one_megabyte() -> None:
    """Sanity: the cap is high enough not to trip on legitimate frames."""
    from ember.spark.funi.ollama.adapter import _MAX_NDJSON_FRAME_BYTES  # noqa: PLC0415

    assert _MAX_NDJSON_FRAME_BYTES >= 1 * 1024 * 1024


# --------------------------------------------------------------------- #
# fetch_url robots.txt — narrow exception catches                       #
# --------------------------------------------------------------------- #


def test_robots_parser_propagates_memory_error() -> None:
    """Hardening: a MemoryError fetching robots.txt is NOT silently
    swallowed (the old code's bare ``except Exception`` would have)."""
    import importlib  # noqa: PLC0415

    from ember.tools import fetch_url  # noqa: PLC0415

    # The package import may have re-registered fetch_url via the
    # __init__'s side-effect; clear THEN reload so the reload's
    # top-level register() call lands in an empty registry.
    registry_clear()
    importlib.reload(fetch_url)

    def _oom_fetcher(_url: str):
        raise MemoryError("oom while parsing robots.txt")

    fetch_url._set_robots_fetcher(_oom_fetcher)
    try:
        with pytest.raises(MemoryError):
            fetch_url._check_robots(
                "https://example.com/page",
                # Pre-parsed URL with the bits the function needs.
                type("P", (), {
                    "scheme": "https", "netloc": "example.com",
                })(),
            )
    finally:
        fetch_url._reset_seams()


def test_robots_parser_swallows_expected_network_errors() -> None:
    """Sanity: legitimate URLError / OSError / TimeoutError from a
    robots fetch are still treated as 'no rules apply' (the standard
    interpretation), so we don't accidentally start failing on every
    fetch when robots.txt is unreachable."""
    import importlib  # noqa: PLC0415
    import urllib.error  # noqa: PLC0415

    from ember.tools import fetch_url  # noqa: PLC0415

    registry_clear()
    importlib.reload(fetch_url)

    for exc_class, exc_args in [
        (urllib.error.URLError, ("nope",)),
        (TimeoutError, ()),
        (OSError, ("network down",)),
    ]:
        def _raising_fetcher(_url: str, *, _exc_class=exc_class, _exc_args=exc_args):
            raise _exc_class(*_exc_args)
        fetch_url._set_robots_fetcher(_raising_fetcher)
        try:
            result = fetch_url._check_robots(
                "https://example.com/p",
                type("P", (), {"scheme": "https", "netloc": "example.com"})(),
            )
            assert result is None, (
                f"{exc_class.__name__} should be treated as no-rules; "
                f"got refusal: {result}"
            )
        finally:
            fetch_url._reset_seams()
