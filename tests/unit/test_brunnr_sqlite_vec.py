"""End-to-end shape and behaviour for the sqlite_vec Brunnr adapter.

Skipped automatically if sqlite_vec is not installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

sqlite_vec = pytest.importorskip("sqlite_vec")

# These imports must follow importorskip so the file is skipped cleanly
# on hosts without the sqlite-vec C extension.
from ember.schemas.chunks import Chunk, Document  # noqa: E402
from ember.schemas.config import BrunnrBackend, BrunnrConfig, SqliteVecConfig  # noqa: E402
from ember.schemas.episode import Episode  # noqa: E402
from ember.schemas.errors import BrunnrError, Disconnected, DisconnectReason  # noqa: E402
from ember.well.brunnr.sqlite_vec import SqliteVecBrunnr  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402


def _make_brunnr(tmp_path: Path, dim: int = 4) -> SqliteVecBrunnr:
    cfg = BrunnrConfig(
        embedding_dim=dim,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    )
    handle = sv_open(cfg)
    assert isinstance(handle, SqliteVecBrunnr)
    return handle


def test_open_creates_database_file(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    handle.close()
    assert (tmp_path / "store.db").exists()


def test_open_with_missing_sqlite_vec_config_returns_disconnected(tmp_path: Path) -> None:
    cfg = BrunnrConfig(
        backend=BrunnrBackend.SQLITE_VEC,
        sqlite_vec=None,
    )
    result = sv_open(cfg)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID


def test_add_document_is_idempotent_on_hash(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc = Document(source="/x", title="t", content_type="md", hash="h1")
    first = handle.add_document(doc)
    second = handle.add_document(doc)
    assert first == second
    handle.close()


def test_add_chunks_writes_embeddings_and_counts_match(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    chunks = [
        Chunk(
            document_id=doc_id,
            chunk_index=i,
            text=f"chunk {i}",
            embedding=(float(i), 0.0, 0.0, 0.0),
        )
        for i in range(3)
    ]
    ids = handle.add_chunks(chunks)
    assert len(ids) == 3
    stats = handle.count()
    assert stats.documents == 1
    assert stats.chunks == 3
    assert stats.embedded_chunks == 3
    handle.close()


def test_add_chunks_refuses_mismatched_embedding_dim(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path, dim=4)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    bad_chunk = Chunk(
        document_id=doc_id,
        chunk_index=0,
        text="x",
        embedding=(1.0, 2.0, 3.0),  # dim 3, not 4
    )
    with pytest.raises(BrunnrError, match="dim"):
        handle.add_chunks([bad_chunk])
    handle.close()


def test_vector_search_ranks_identical_first(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    handle.add_chunks(
        [
            Chunk(
                document_id=doc_id, chunk_index=0, text="alpha",
                embedding=(1.0, 0.0, 0.0, 0.0),
            ),
            Chunk(
                document_id=doc_id, chunk_index=1, text="beta",
                embedding=(0.0, 1.0, 0.0, 0.0),
            ),
            Chunk(
                document_id=doc_id, chunk_index=2, text="gamma",
                embedding=(0.0, 0.0, 1.0, 0.0),
            ),
        ]
    )
    hits = handle.vector_search((1.0, 0.0, 0.0, 0.0), k=3)
    assert len(hits) == 3
    assert hits[0].text == "alpha"
    handle.close()


def test_text_search_finds_matching_chunk(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    handle.add_chunks(
        [
            Chunk(
                document_id=doc_id, chunk_index=0, text="Odin is a wise god",
                embedding=(1.0, 0.0, 0.0, 0.0),
            ),
            Chunk(
                document_id=doc_id, chunk_index=1, text="Thor wields Mjolnir",
                embedding=(0.0, 1.0, 0.0, 0.0),
            ),
        ]
    )
    hits = handle.text_search("Odin", k=5)
    assert len(hits) == 1
    assert "Odin" in hits[0].text
    handle.close()


def test_hybrid_search_returns_both_modes(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    handle.add_chunks(
        [
            Chunk(
                document_id=doc_id, chunk_index=0, text="Odin is wise",
                embedding=(1.0, 0.0, 0.0, 0.0),
            ),
            Chunk(
                document_id=doc_id, chunk_index=1, text="Thor is strong",
                embedding=(0.0, 1.0, 0.0, 0.0),
            ),
        ]
    )
    hits = handle.hybrid_search((1.0, 0.0, 0.0, 0.0), "wise", k=2)
    assert len(hits) >= 1
    # The most relevant chunk by both signals should rank first.
    assert "Odin" in hits[0].text
    handle.close()


def test_get_chunk_round_trips_embedding(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="t", content_type="md", hash="h1")
    )
    [chunk_id] = handle.add_chunks(
        [Chunk(document_id=doc_id, chunk_index=0, text="x", embedding=(0.1, 0.2, 0.3, 0.4))]
    )
    fetched = handle.get_chunk(chunk_id)
    assert fetched.text == "x"
    assert fetched.embedding is not None
    assert len(fetched.embedding) == 4
    assert fetched.embedding[0] == pytest.approx(0.1)
    handle.close()


def test_add_episode_assigns_id_and_persists(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    ep_id = handle.add_episode(
        Episode(
            operator_input="who is Odin?",
            ember_reply="Odin is the Allfather.",
            cited_chunk_ids=(1, 2),
            funi_model="phi3:mini",
            well_disconnected=False,
        )
    )
    assert ep_id > 0
    handle.close()


def test_count_reports_zero_initially(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    stats = handle.count()
    assert stats.documents == 0
    assert stats.chunks == 0
    assert stats.embedded_chunks == 0
    assert stats.size_bytes > 0
    handle.close()
