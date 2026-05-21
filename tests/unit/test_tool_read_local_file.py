"""``read_local_file`` tool — happy path + every sandbox refusal."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

from ember.schemas.tool import ApprovalPolicy, ToolCall
from ember.spark.funi.tools.registry import clear, lookup
from ember.tools import read_local_file


@pytest.fixture(autouse=True)
def _isolate_registry():
    clear()
    importlib.reload(read_local_file)
    yield
    clear()


def _call(arguments: dict) -> ToolCall:
    return ToolCall(call_id="c-1", name="read_local_file", arguments=arguments)


@pytest.fixture
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Re-root HOME under tmp_path so the sandbox checks operate inside
    a clean tree the test fully controls.

    Path.home() reads HOME on POSIX; we just rewrite the env var. We
    also seed the denylist directories so sandbox tests have something
    to point at.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".ssh").mkdir()
    (tmp_path / ".ember" / "secrets").mkdir(parents=True)
    (tmp_path / ".pgpass").write_text("dummy", encoding="utf-8")
    return tmp_path


# --------------------------------------------------------------------- #
# Registration                                                          #
# --------------------------------------------------------------------- #


def test_tool_registers_with_per_call_approval() -> None:
    entry = lookup("read_local_file")
    assert entry is not None
    descriptor, _executor = entry
    assert descriptor.required_approval is ApprovalPolicy.PER_CALL


# --------------------------------------------------------------------- #
# Happy path                                                            #
# --------------------------------------------------------------------- #


def test_reads_a_utf8_file_under_home(fake_home: Path) -> None:
    notes = fake_home / "notes" / "odin.md"
    notes.parent.mkdir(parents=True)
    notes.write_text("Odin is the Allfather.", encoding="utf-8")

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(notes)}))

    assert reply.error is None
    assert "Odin is the Allfather." in reply.output


def test_resolves_tilde_paths(fake_home: Path) -> None:
    notes = fake_home / "notes.md"
    notes.write_text("home-anchored", encoding="utf-8")

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": "~/notes.md"}))
    assert reply.error is None
    assert "home-anchored" in reply.output


# --------------------------------------------------------------------- #
# Refusals — input shape                                                #
# --------------------------------------------------------------------- #


def test_refuses_non_string_path(fake_home: Path) -> None:
    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": 42}))
    assert reply.output == ""
    assert "non-empty string" in (reply.error or "")


def test_refuses_empty_string_path(fake_home: Path) -> None:
    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": ""}))
    assert reply.output == ""
    assert "non-empty string" in (reply.error or "")


# --------------------------------------------------------------------- #
# Refusals — sandbox                                                    #
# --------------------------------------------------------------------- #


def test_refuses_path_outside_home(fake_home: Path, tmp_path_factory) -> None:
    """A file in a sibling tmp directory (resolves outside HOME) is refused."""
    other = tmp_path_factory.mktemp("not-under-home") / "x.txt"
    other.write_text("payload", encoding="utf-8")

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(other)}))
    assert reply.output == ""
    assert "outside the operator's home directory" in (reply.error or "")
    # Crucially, the body must not have been read.
    assert "payload" not in (reply.error or "")


def test_refuses_ssh_dir(fake_home: Path) -> None:
    key = fake_home / ".ssh" / "id_rsa"
    key.write_text("-----BEGIN OPENSSH PRIVATE KEY-----", encoding="utf-8")

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(key)}))
    assert reply.output == ""
    err = reply.error or ""
    assert "denylist" in err
    assert ".ssh" in err
    assert "BEGIN OPENSSH" not in err  # body must not leak


def test_refuses_ember_secrets_dir(fake_home: Path) -> None:
    secret = fake_home / ".ember" / "secrets" / "well.password"
    secret.write_text("super-secret-token", encoding="utf-8")

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(secret)}))
    assert reply.output == ""
    assert "denylist" in (reply.error or "")
    assert "super-secret-token" not in (reply.error or "")


def test_refuses_pgpass(fake_home: Path) -> None:
    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(fake_home / ".pgpass")}))
    assert reply.output == ""
    assert "denylist" in (reply.error or "")


def test_refuses_nonexistent_path(fake_home: Path) -> None:
    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(fake_home / "does-not-exist.md")}))
    assert reply.output == ""
    assert "does not exist" in (reply.error or "")


def test_refuses_directory(fake_home: Path) -> None:
    (fake_home / "subdir").mkdir()
    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(fake_home / "subdir")}))
    assert reply.output == ""
    assert "directory" in (reply.error or "")


def test_refuses_file_above_size_cap(fake_home: Path) -> None:
    big = fake_home / "huge.txt"
    # Write 257 KiB, just over the 256 KiB cap.
    big.write_bytes(b"x" * (257 * 1024))
    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(big)}))
    assert reply.output == ""
    err = reply.error or ""
    assert "sandbox limit" in err
    assert "256" in err  # the limit number is in the message


@pytest.mark.skipif(os.name == "nt", reason="symlink semantics")
def test_refuses_symlink_pointing_outside_home(
    fake_home: Path, tmp_path_factory,
) -> None:
    """Defence against symlink-escape attempts — resolve before checking."""
    outside = tmp_path_factory.mktemp("outside") / "target.txt"
    outside.write_text("secret-from-outside", encoding="utf-8")

    link = fake_home / "innocent.txt"
    link.symlink_to(outside)

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(link)}))
    assert reply.output == ""
    assert "outside" in (reply.error or "")
    assert "secret-from-outside" not in (reply.error or "")


@pytest.mark.skipif(os.name == "nt", reason="symlink semantics")
def test_refuses_symlink_pointing_into_denylist(fake_home: Path) -> None:
    """A symlink that resolves into .ssh is still on the denylist."""
    key = fake_home / ".ssh" / "id_rsa"
    key.write_text("-----BEGIN OPENSSH PRIVATE KEY-----", encoding="utf-8")
    link = fake_home / "looks_innocent.txt"
    link.symlink_to(key)

    _descriptor, execute = lookup("read_local_file")  # type: ignore[misc]
    reply = execute(_call({"path": str(link)}))
    assert reply.output == ""
    assert "denylist" in (reply.error or "")
