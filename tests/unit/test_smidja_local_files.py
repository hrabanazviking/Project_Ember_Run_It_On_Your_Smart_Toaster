"""Shape and behaviour tests for the local_files Smiðja source."""

from __future__ import annotations

from pathlib import Path

import pytest

from ember.schemas.errors import IngestError
from ember.well.smidja.local_files import walk


def test_walk_yields_one_parsed_file_per_match(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("hello", encoding="utf-8")
    (tmp_path / "b.txt").write_text("world", encoding="utf-8")
    (tmp_path / "c.png").write_bytes(b"\x89PNG")  # excluded by include patterns

    files = sorted(walk(tmp_path), key=lambda f: f.path.name)
    assert [f.path.name for f in files] == ["a.md", "b.txt"]


def test_walk_skips_default_excluded_dirs(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "secret.md").write_text("nope", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.txt").write_text("nope", encoding="utf-8")
    (tmp_path / "real.md").write_text("ok", encoding="utf-8")

    files = list(walk(tmp_path))
    assert len(files) == 1
    assert files[0].path.name == "real.md"


def test_walk_attaches_content_type_per_suffix(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / "b.json").write_text("{}", encoding="utf-8")
    (tmp_path / "c.yaml").write_text("k: v", encoding="utf-8")

    by_name = {f.path.name: f for f in walk(tmp_path)}
    assert by_name["a.md"].content_type == "md"
    assert by_name["b.json"].content_type == "json"
    assert by_name["c.yaml"].content_type == "yaml"


def test_walk_hashes_content_so_same_bytes_get_same_hash(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("hello", encoding="utf-8")
    (tmp_path / "b.md").write_text("hello", encoding="utf-8")
    by_name = {f.path.name: f for f in walk(tmp_path)}
    assert by_name["a.md"].hash == by_name["b.md"].hash


def test_walk_silently_skips_non_utf8(tmp_path: Path) -> None:
    (tmp_path / "binary.md").write_bytes(b"\xff\xfe\x00invalid utf8")
    (tmp_path / "good.md").write_text("hello", encoding="utf-8")
    files = list(walk(tmp_path))
    names = sorted(f.path.name for f in files)
    assert names == ["good.md"]


def test_walk_raises_on_missing_root(tmp_path: Path) -> None:
    with pytest.raises(IngestError, match="does not exist"):
        list(walk(tmp_path / "nope"))


def test_walk_raises_when_root_is_a_file(tmp_path: Path) -> None:
    f = tmp_path / "f.md"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(IngestError, match="not a directory"):
        list(walk(f))


def test_walk_is_sorted_for_deterministic_order(tmp_path: Path) -> None:
    for name in ["z.md", "a.md", "m.md"]:
        (tmp_path / name).write_text("x", encoding="utf-8")
    names = [f.path.name for f in walk(tmp_path)]
    assert names == sorted(names)
