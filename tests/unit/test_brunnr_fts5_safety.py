"""Regression tests for the FTS5 input sanitiser.

The Hjarta probe broke on 2026-05-21 because operator-supplied text
containing FTS5-reserved syntax (e.g. ``run:`` being read as a column
reference) caused ``text_search`` to raise ``no such column``. The
fix lives in :func:`ember.well.brunnr.sqlite_vec.adapter._escape_fts5_query`;
these tests pin its behaviour and verify the adapter no longer raises.

Skipped automatically if sqlite_vec is not installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

sqlite_vec = pytest.importorskip("sqlite_vec")

from ember.schemas.chunks import Chunk, Document  # noqa: E402
from ember.schemas.config import BrunnrConfig, SqliteVecConfig  # noqa: E402
from ember.well.brunnr.sqlite_vec import SqliteVecBrunnr  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.brunnr.sqlite_vec.adapter import _escape_fts5_query  # noqa: E402

# --------------------------------------------------------------------- #
# Pure-function shape contracts                                         #
# --------------------------------------------------------------------- #


def test_escape_empty_input_returns_empty_string() -> None:
    assert _escape_fts5_query("") == ""
    assert _escape_fts5_query("   ") == ""
    assert _escape_fts5_query("\t\n") == ""


def test_escape_single_token_wraps_in_quotes() -> None:
    assert _escape_fts5_query("Odin") == '"Odin"'


def test_escape_multiple_tokens_or_joins_them() -> None:
    assert _escape_fts5_query("Odin Thor") == '"Odin" OR "Thor"'


def test_escape_neutralises_reserved_column_syntax() -> None:
    # The exact pattern that broke Hjarta on 2026-05-21.
    out = _escape_fts5_query("run: a marathon")
    # Three tokens, each wrapped in literal-phrase quotes.
    assert out == '"run:" OR "a" OR "marathon"'
    # FTS5 only parses `run:` as a column reference when it's *bare*.
    # Inside `"..."` it's a literal phrase, so the colon is harmless.
    assert '"run:"' in out


def test_escape_doubles_internal_quote_chars() -> None:
    out = _escape_fts5_query('he said "hi"')
    # Internal " is doubled per FTS5 phrase-literal escape rules.
    assert '""hi""' in out


def test_escape_neutralises_reserved_boolean_operators() -> None:
    # Bare AND/OR/NOT would otherwise be parsed as syntax.
    out = _escape_fts5_query("Odin AND Thor")
    # AND gets quoted as a literal too — won't act as an operator.
    assert '"AND"' in out


# --------------------------------------------------------------------- #
# End-to-end: the previously failing inputs no longer raise             #
# --------------------------------------------------------------------- #


def _make_brunnr(tmp_path: Path) -> SqliteVecBrunnr:
    cfg = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    )
    handle = sv_open(cfg)
    assert isinstance(handle, SqliteVecBrunnr)
    return handle


def test_text_search_with_reserved_syntax_does_not_raise(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="x", content_type="md", hash="h")
    )
    handle.add_chunks(
        [
            Chunk(
                document_id=doc_id, chunk_index=0,
                text="A long-run marathon takes hours",
                embedding=(1.0, 0.0, 0.0, 0.0),
            )
        ]
    )

    # Every one of these previously broke (column-ref, boolean op, parens, etc.)
    for query in [
        "run: a marathon",
        "Odin AND Thor",
        "what is (the) point",
        'he said "hi"',
        "NEAR star",
        "first-run probe",
        "*wildcard*",
    ]:
        hits = handle.text_search(query, k=5)
        assert isinstance(hits, list)

    handle.close()


def test_text_search_with_empty_query_returns_empty_list(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    handle.add_document(
        Document(source="/x", title="x", content_type="md", hash="h")
    )
    assert handle.text_search("", k=5) == []
    assert handle.text_search("   ", k=5) == []
    handle.close()


def test_text_search_still_finds_matches_with_natural_language(tmp_path: Path) -> None:
    handle = _make_brunnr(tmp_path)
    doc_id = handle.add_document(
        Document(source="/x", title="x", content_type="md", hash="h")
    )
    handle.add_chunks(
        [
            Chunk(
                document_id=doc_id, chunk_index=0,
                text="Odin sacrificed an eye for wisdom.",
                embedding=(1.0, 0.0, 0.0, 0.0),
            ),
            Chunk(
                document_id=doc_id, chunk_index=1,
                text="Thor wields the hammer Mjolnir against giants.",
                embedding=(0.0, 1.0, 0.0, 0.0),
            ),
        ]
    )

    # Each query should find its matching chunk by token-OR semantics.
    odin_hits = handle.text_search("Tell me about Odin", k=5)
    assert any("Odin" in h.text for h in odin_hits)

    thor_hits = handle.text_search("Mjolnir hammer", k=5)
    assert any("Mjolnir" in h.text for h in thor_hits)

    handle.close()
