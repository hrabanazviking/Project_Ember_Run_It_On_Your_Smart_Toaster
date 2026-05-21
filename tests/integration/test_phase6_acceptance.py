"""Phase 6 acceptance: Hjarta + ingest + chat against real sqlite_vec.

Mocks Funi (no Ollama dependency) and the embed_client (deterministic
content-addressed vectors) so the test runs anywhere sqlite-vec is
installed. The real-Ollama integration test in
``tests/integration/test_funi_ollama_real.py`` covers the Ollama
adapter separately.

Acceptance criterion (per EMBER_FIRST_SLICE_PLAN.md §0):

    1. ``ember setup`` runs Hjarta → identity file
    2. ``ember well ingest <dir>`` → summary, chunks in Well
    3. ``ember chat`` round-trips one operator turn with a grounded reply
"""

from __future__ import annotations

import hashlib
import io
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

pytest.importorskip("sqlite_vec")

from ember.schemas.config import (
    BrunnrConfig,
    EmberConfig,
    FuniConfig,
    IdentityConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.funi import (
    FinishReason,
    FuniHealth,
    FuniReply,
)
from ember.spark.hjarta import HjartaIO, save_identity_atomic
from ember.spark.hjarta import run as hjarta_run
from ember.spark.munnr import chat, ingest

_DIM = 32


# --------------------------------------------------------------------- #
# Test doubles                                                          #
# --------------------------------------------------------------------- #


class _FakeFuni:
    runtime_kind = "fake"
    model_id = "fake:tiny"

    def __init__(self) -> None:
        self.last_prompt: str | None = None
        self.last_context_kinds: list[str] = []

    def complete(self, prompt: str, context, tools=None) -> FuniReply:
        self.last_prompt = prompt
        self.last_context_kinds = [c.kind.value for c in context]
        # Echo back the operator's prompt with a tag — easy assertions.
        return FuniReply(
            text=f"[fake-funi] you asked: {prompt}",
            finish_reason=FinishReason.STOP,
            model_id=self.model_id,
        )

    def health(self) -> FuniHealth:
        return FuniHealth(model_id=self.model_id, last_ok=datetime.now(tz=UTC))

    def close(self) -> None:
        return None


class _DeterministicEmbed:
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


def _ember_config_for(tmp_path: Path) -> EmberConfig:
    return EmberConfig(
        funi=FuniConfig(),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=_DIM,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
        ),
    )


# --------------------------------------------------------------------- #
# The acceptance flow                                                   #
# --------------------------------------------------------------------- #


def test_full_first_slice_round_trip(tmp_path: Path) -> None:
    config_root = tmp_path / "ember-home"
    notes_root = tmp_path / "notes"
    notes_root.mkdir()
    (notes_root / "odin.md").write_text(
        "Odin is the Allfather of the Norse pantheon. He sacrificed an eye "
        "for wisdom. Odin rules from Valhalla and his ravens fly the worlds.",
        encoding="utf-8",
    )

    ember_config = _ember_config_for(tmp_path)

    # ----- Hjarta -------------------------------------------------- #
    answers = iter(["", "", "", ""])  # press-Enter through all prompts
    hjarta_output: list[str] = []
    hjarta_io = HjartaIO(
        prompt=lambda _t: next(answers, ""),
        info=hjarta_output.append,
        error=lambda s: hjarta_output.append("ERROR: " + s),
    )
    fake_funi_for_hjarta = _FakeFuni()
    outcome = hjarta_run(
        config=ember_config,
        config_root=config_root,
        io=hjarta_io,
        funi_opener=lambda _cfg: fake_funi_for_hjarta,
    )
    assert outcome.success, f"Hjarta did not complete: {outcome.detail}"
    assert outcome.identity_path is not None
    assert outcome.identity_path.is_file()

    # ----- ember well ingest --------------------------------------- #
    ingest_stdout = io.StringIO()
    rc = ingest.run(
        path=notes_root,
        config=ember_config,
        stdout=ingest_stdout,
        embed_client=_DeterministicEmbed(),
    )
    assert rc == 0, ingest_stdout.getvalue()
    assert "documents: 1" in ingest_stdout.getvalue()
    assert "chunks:" in ingest_stdout.getvalue()

    # ----- ember chat (one turn) ----------------------------------- #
    chat_stdout = io.StringIO()
    chat_stdin = io.StringIO("Tell me about Odin\n/exit\n")
    fake_funi_for_chat = _FakeFuni()
    rc = chat.run(
        config=ember_config,
        config_root=config_root,
        stdin=chat_stdin,
        stdout=chat_stdout,
        embed_client=_DeterministicEmbed(),
        funi_opener=lambda _cfg: fake_funi_for_chat,
    )
    assert rc == 0, chat_stdout.getvalue()

    output = chat_stdout.getvalue()
    # Operator prompt was forwarded to Funi.
    assert fake_funi_for_chat.last_prompt == "Tell me about Odin"
    # Funi was given a system prompt + at least one chunk.
    assert "system" in fake_funi_for_chat.last_context_kinds
    assert "chunk" in fake_funi_for_chat.last_context_kinds
    # Reply rendered into stdout, with citations footer.
    assert "[fake-funi] you asked: Tell me about Odin" in output
    assert "citations:" in output
    # And no disconnect banner (the Well was reachable).
    assert "well: disconnected" not in output


def test_chat_renders_disconnect_banner_when_well_is_disconnected(tmp_path: Path) -> None:
    """The Vow of Graceful Offline in flow form."""
    config_root = tmp_path / "ember-home"
    ember_config = _ember_config_for(tmp_path)
    # Pre-write an identity so we skip Hjarta in chat's first-launch redirect.
    save_identity_atomic(config_root, IdentityConfig())

    chat_stdout = io.StringIO()
    chat_stdin = io.StringIO("hi\n/exit\n")
    fake_funi = _FakeFuni()

    rc = chat.run(
        config=ember_config,
        config_root=config_root,
        stdin=chat_stdin,
        stdout=chat_stdout,
        embed_client=_DeterministicEmbed(),
        funi_opener=lambda _cfg: fake_funi,
        strengr_opener=lambda _s, _b: Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        ),
    )
    assert rc == 0
    out = chat_stdout.getvalue()
    assert "[well: disconnected" in out
    # Funi was still called — chat degrades, doesn't fail.
    assert fake_funi.last_prompt == "hi"
    # The context handed to Funi flagged the disconnect via the system prompt.
    assert "system" in fake_funi.last_context_kinds
    # No citations under a disconnected reply.
    assert "citations:" not in out
