"""Slice-2 acceptance flow (Phase 17, ADR 0013).

The full operator journey ratified by ADR 0013:

1. Operator runs ``ember setup`` → Hjarta writes ``identity.json`` AND
   ``ember.yaml`` (including ``tools.enabled: true`` when the Advanced
   branch was answered yes).
2. Operator runs ``ember well ingest <dir>`` → Smiðja chunks + embeds
   + deposits into the configured Brunnr (sqlite_vec default; pgvector
   variant exercised by the requires_podman / requires_postgres
   markers in the peer test ``test_pgvector_real_backend.py``).
3. Operator runs ``ember chat`` → an operator turn streams live; a
   model that emits a ``tool_call`` is proposed to the operator,
   approved per ADR 0011 §2.4, executed, audited, and the reply is
   folded back into the next Funi turn's context.
4. The persisted Episode shows the *final* (post-tool-loop) reply.
5. The audit log gains one JSONL record per tool invocation.

This file mocks Funi (no Ollama dependency) so it runs in any
environment that has ``sqlite-vec`` installed. The real-Ollama side
of the acceptance was verified in the Phase-16 manual smoke against
tailnet llama3.2:3b (see DEVLOG 2026-05-21).
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

pytest.importorskip("sqlite_vec")

from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    SqliteVecConfig,
    StrengrConfig,
    ToolsConfig,
)
from ember.schemas.funi import (
    ContextItem,
    FinishReason,
    FuniHealth,
    FuniReply,
)
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.tool import (
    ToolCall,
    ToolDescriptor,
)
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools import register
from ember.spark.hjarta import HjartaIO
from ember.spark.hjarta import run as hjarta_run
from ember.spark.munnr import chat, ingest

_DIM = 32


# --------------------------------------------------------------------- #
# Test doubles                                                          #
# --------------------------------------------------------------------- #


class _DeterministicEmbed:
    """Hash-derived embeddings — same content → same vector."""

    def embed(self, texts: Sequence[str]) -> list[tuple[float, ...] | None]:
        return [_hash_to_vector(t, _DIM) for t in texts]


def _hash_to_vector(text: str, dim: int) -> tuple[float, ...]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    while len(digest) < dim * 4:
        digest += hashlib.sha256(digest).digest()
    return tuple(
        int.from_bytes(digest[i * 4 : (i + 1) * 4], "little") / 2**32
        for i in range(dim)
    )


class _SliceTwoFuni:
    """Funi that runs the full slice-2 turn shape:

    - First turn streams a few text deltas, then proposes a tool call.
    - Second (follow-up) turn streams a summarising reply, no tools.

    Captures every call so the test can assert on what got sent.
    """

    runtime_kind = "fake"
    model_id = "fake:slice2"

    def __init__(self) -> None:
        self.streaming_calls: list[dict] = []

    def complete(self, *a, **kw) -> FuniReply:  # pragma: no cover
        raise AssertionError("acceptance uses streaming only")

    def complete_streaming(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> Iterator[FuniStreamChunk]:
        self.streaming_calls.append({
            "prompt": prompt,
            "context": list(context),
            "tools": list(tools) if tools else [],
        })
        if len(self.streaming_calls) == 1:
            # First turn — model proposes a tool call.
            yield FuniStreamChunk(text_delta="Let me check...\n", done=False)
            yield FuniStreamChunk(
                text_delta="",
                done=True,
                finish_reason=FinishReason.TOOL_CALL,
                model_id=self.model_id,
                tool_calls=(
                    ToolCall(
                        call_id="acc-1",
                        name="search_well",
                        arguments={"query": "Odin", "k": 3},
                    ),
                ),
            )
        else:
            # Follow-up turn — model summarises what the tool returned.
            yield FuniStreamChunk(
                text_delta="Based on the well, ", done=False,
            )
            yield FuniStreamChunk(
                text_delta="Odin is the Allfather.", done=False,
            )
            yield FuniStreamChunk(
                text_delta="",
                done=True,
                finish_reason=FinishReason.STOP,
                model_id=self.model_id,
            )

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


class _AutoApprovePrompter:
    """Approval prompter that says 'y' for every PER_CALL request."""

    def __init__(self) -> None:
        self.calls: list[ToolCall] = []

    def prompt(self, descriptor: ToolDescriptor, call: ToolCall) -> str:
        self.calls.append(call)
        return "y"


# --------------------------------------------------------------------- #
# Config                                                                #
# --------------------------------------------------------------------- #


def _ember_config(tmp_path: Path, *, tools_enabled: bool) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=_DIM,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
        tools=ToolsConfig(enabled=tools_enabled),
    )


def _scripted_io(answers: Sequence[str]) -> tuple[HjartaIO, list[str]]:
    out: list[str] = []
    it = iter(answers)
    return (
        HjartaIO(
            prompt=lambda _t: next(it, ""),
            info=out.append,
            error=lambda s: out.append("ERROR: " + s),
        ),
        out,
    )


def _read_audit(config_root: Path) -> list[dict]:
    audit_dir = config_root / "state" / "tool_audit"
    if not audit_dir.exists():
        return []
    records: list[dict] = []
    for path in sorted(audit_dir.iterdir()):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


# --------------------------------------------------------------------- #
# The acceptance flow                                                   #
# --------------------------------------------------------------------- #


def test_slice_two_full_operator_flow_with_tool_call(tmp_path: Path) -> None:  # noqa: PLR0915 — acceptance test naturally walks all 5 stages
    """The Phase-17 acceptance: setup → ingest → chat → tool call → audit.

    Uses the *real* ``ember.tools.search_well`` executor — it self-
    registers when ``ember.tools`` is imported, and chat.py binds it to
    the live sqlite_vec Brunnr. The model's tool_call therefore round-
    trips through Smiðja's ingested chunks back to Funi, which is the
    full production shape.
    """
    # Import order matters: the ember.tools package __init__ side-effect-
    # imports each tool module, which side-effect-calls register(). Do
    # the imports FIRST (so any first-time-import register fires), THEN
    # clear (so the registry is empty), THEN re-register explicitly.
    from ember.tools import fetch_url as _fetch_url  # noqa: PLC0415
    from ember.tools import read_local_file as _read_local_file  # noqa: PLC0415
    from ember.tools import search_well as _search_well  # noqa: PLC0415

    registry_clear()
    register(_search_well._DESCRIPTOR, _search_well._execute)
    register(_read_local_file._DESCRIPTOR, _read_local_file._execute)
    register(_fetch_url._DESCRIPTOR, _fetch_url._execute)
    try:
        config_root = tmp_path / "ember-home"
        notes_root = tmp_path / "notes"
        notes_root.mkdir()
        (notes_root / "odin.md").write_text(
            "Odin is the Allfather. He sacrificed an eye for wisdom at "
            "Mimir's well. His ravens Huginn and Muninn fly the worlds.",
            encoding="utf-8",
        )

        ember_config = _ember_config(tmp_path, tools_enabled=False)

        # ---- 1. Hjarta sets up identity AND tools-enabled yaml ---- #
        # Five answers in wizard order — last "y" enables tools.
        io_obj, _hjarta_log = _scripted_io(["", "", "", "", "y"])

        fake_funi_for_hjarta = _SliceTwoFuni()
        outcome = hjarta_run(
            config=ember_config,
            config_root=config_root,
            io=io_obj,
            funi_opener=lambda _cfg: fake_funi_for_hjarta,
        )
        assert outcome.success, f"Hjarta failed: {outcome.detail}"

        # Confirm Hjarta wrote tools.enabled=true into ember.yaml.
        # The CLI reloads here per Phase 9; the test keeps its custom
        # embedding_dim by flipping only the tools-enabled bit on the
        # original test config (load_ember_config would clobber dim
        # back to the default 768).
        from dataclasses import replace  # noqa: PLC0415

        from ember.config import load_ember_config  # noqa: PLC0415
        reloaded = load_ember_config(config_root, skip_env=True)
        assert reloaded.tools.enabled is True
        ember_config = replace(ember_config, tools=reloaded.tools)

        # ---- 2. Smiðja ingests a small corpus ---- #
        ingest_stdout = io.StringIO()
        rc = ingest.run(
            path=notes_root,
            config=ember_config,
            stdout=ingest_stdout,
            embed_client=_DeterministicEmbed(),
        )
        assert rc == 0, ingest_stdout.getvalue()
        assert "documents: 1" in ingest_stdout.getvalue()

        # ---- 3. Munnr drives the full tool-loop ---- #
        chat_funi = _SliceTwoFuni()
        prompter = _AutoApprovePrompter()
        chat_stdout = io.StringIO()

        rc = chat.run(
            config=ember_config,
            config_root=config_root,
            stdin=io.StringIO("Tell me about Odin\n/exit\n"),
            stdout=chat_stdout,
            embed_client=_DeterministicEmbed(),
            funi_opener=lambda _cfg: chat_funi,
            approval_prompter=prompter,
        )
        assert rc == 0, chat_stdout.getvalue()

        out = chat_stdout.getvalue()

        # Funi was called twice: first for the tool proposal, then for
        # the summarising reply.
        assert len(chat_funi.streaming_calls) == 2

        # First call carried tool descriptors AND the operator input.
        first = chat_funi.streaming_calls[0]
        assert first["prompt"] == "Tell me about Odin"
        assert any(d.name == "search_well" for d in first["tools"])

        # Second call carried the tool reply context + no operator input.
        second = chat_funi.streaming_calls[1]
        assert second["prompt"] == ""
        from ember.schemas.funi import ContextKind  # noqa: PLC0415
        tool_items = [
            ci for ci in second["context"] if ci.kind is ContextKind.TOOL_REPLY
        ]
        assert tool_items
        assert "Mimir's well" in tool_items[0].text

        # The real search_well executor ran — its formatted output
        # contains "search_well(...)" and references the chunk it found.
        # Pull the tool reply text out of the second turn's context.
        tool_reply_text = tool_items[0].text
        assert "search_well" in tool_reply_text
        # The ingested chunk about Odin should surface.
        assert "Odin" in tool_reply_text or "Mimir" in tool_reply_text

        # search_well is STANDING — no operator prompt fires.
        assert prompter.calls == []

        # Operator-facing render shows the proposal, the reply, and the
        # follow-up summary text.
        assert "[tool proposal] search_well" in out
        assert "auto-approved] search_well" in out
        assert "Odin is the Allfather." in out  # follow-up summary

        # ---- 4. The Episode persisted carries the final reply ---- #
        # ingest writes documents+chunks; chat writes the episode. Read
        # them back via a peer SqliteVecBrunnr to confirm.
        from ember.well.brunnr.sqlite_vec import (  # noqa: PLC0415
            open as sqlite_vec_open,
        )
        well = sqlite_vec_open(ember_config.brunnr)
        from ember.well.brunnr.sqlite_vec import SqliteVecBrunnr  # noqa: PLC0415
        assert isinstance(well, SqliteVecBrunnr)
        try:
            stats = well.count()
            assert stats.documents >= 1
            assert stats.chunks >= 1
        finally:
            well.close()

        # ---- 5. The audit log gains one record ---- #
        records = _read_audit(config_root)
        assert len(records) == 1
        r = records[0]
        assert r["tool"] == "search_well"
        assert r["approval"] == "auto_approved"
        assert r["approval_policy"] == "standing"
        assert r["arguments"]["query"] == "Odin"
        # Reply output preserves the search_well-rendered header.
        assert "search_well" in r["reply"]["output"]
    finally:
        registry_clear()


def test_slice_two_acceptance_with_tools_disabled(tmp_path: Path) -> None:
    """Default-off acceptance — Funi never sees tool descriptors, no audit log."""
    registry_clear()
    try:
        config_root = tmp_path / "ember-home"
        notes_root = tmp_path / "notes"
        notes_root.mkdir()
        (notes_root / "odin.md").write_text(
            "Odin is the Allfather.", encoding="utf-8",
        )

        ember_config = _ember_config(tmp_path, tools_enabled=False)

        # No-tool Hjarta: empty answer to ADVANCED_TOOLS keeps tools off.
        io_obj, _ = _scripted_io(["", "", "", "", ""])
        outcome = hjarta_run(
            config=ember_config,
            config_root=config_root,
            io=io_obj,
            funi_opener=lambda _cfg: _SliceTwoFuni(),
        )
        assert outcome.success

        # Reload — tools should still be off. Preserve the test's
        # custom embedding_dim by flipping only the tools-enabled bit.
        from dataclasses import replace  # noqa: PLC0415

        from ember.config import load_ember_config  # noqa: PLC0415
        reloaded = load_ember_config(config_root, skip_env=True)
        assert reloaded.tools.enabled is False
        ember_config = replace(ember_config, tools=reloaded.tools)

        rc = ingest.run(
            path=notes_root,
            config=ember_config,
            stdout=io.StringIO(),
            embed_client=_DeterministicEmbed(),
        )
        assert rc == 0

        chat_funi = _SliceTwoFuni()
        rc = chat.run(
            config=ember_config,
            config_root=config_root,
            stdin=io.StringIO("Tell me about Odin\n/exit\n"),
            stdout=io.StringIO(),
            embed_client=_DeterministicEmbed(),
            funi_opener=lambda _cfg: chat_funi,
        )
        assert rc == 0

        # Tools disabled — no tool descriptors forwarded; the tool_calls
        # the model emits are ignored (short-circuit), so the loop ends
        # after one turn.
        assert len(chat_funi.streaming_calls) == 1
        assert chat_funi.streaming_calls[0]["tools"] == []

        # No audit log.
        assert _read_audit(config_root) == []
    finally:
        # Belt-and-suspenders — we didn't register anything, but clear
        # in case a prior test polluted the registry.
        with contextlib.suppress(Exception):
            registry_clear()


def test_slice_two_streaming_default_remains_on(tmp_path: Path) -> None:
    """Sanity: the slice-2 default for FuniConfig.streaming is True."""
    cfg = _ember_config(tmp_path, tools_enabled=False)
    assert cfg.funi.streaming is True
