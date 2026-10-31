"""The pending-episodes journal — E-031 (docket 82).

Per ``docs/architecture/DATA_FLOW.md`` §2.2 step 9' and
``ember.schemas.episode``: when the Well is unreachable, a
conversation turn is written locally to
``<config_root>/state/pending_episodes/`` and flushed into the
Well when it comes back. Before E-031 that journal existed only
in prose — a disconnected session's turns were lost at exit, and
a turn whose ``add_episode`` failed mid-session (E-030, docket
85) lived only in RAM.

Shape, chosen for tiny hardware and crash honesty:

* **One file per episode.** Appending is O(1) — no whole-journal
  rewrite on a Pi, and one damaged file cannot poison the rest.
* **Atomic writes (the Samtal lesson).** Each file is written to
  a ``.tmp`` sibling, fsynced, then ``os.replace``d into its
  final name, and the directory is fsynced. A kill mid-write can
  leave a ``.tmp`` fragment — never a torn ``.json``. Leftover
  ``.tmp`` files are ignored, not counted as episodes.
* **Corruption is quarantined, never fatal and never silent.**
  A ``.json`` file that cannot be parsed or fails validation is
  moved aside into ``corrupt/`` (never deleted) and reported in
  the drain result, so good episodes still flush and the operator
  can be told exactly what was set aside.
* **Drain is ordered and conservative.** Files sort by name
  (timestamp-prefixed, so name order is turn order). An episode
  file is removed only *after* the Well accepts it; the first
  refusal stops the drain with the rest kept, in order.

The journal persists ``persona_id`` even though the Brunnr
adapters do not yet store the tag (E-025's stated limit): a
pending episode keeps its persona while it waits, and chat uses
it when deciding whose history a drained turn belongs to.
``conversation_id`` rides the same way (E-035): a pending
episode keeps its conversation while it waits. Journal files
written before E-035 have no ``conversation_id`` field; they
load as the ``default`` conversation, which is exactly the
namespace those turns already belonged to.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.episode import Episode

_CORRUPT_SUBDIR = "corrupt"


def pending_root(config_root: Path) -> Path:
    """The journal directory for one config root (E-020 tether)."""
    return Path(config_root).expanduser() / "state" / "pending_episodes"


def episode_to_payload(episode: Episode) -> dict:
    return {
        "operator_input": episode.operator_input,
        "ember_reply": episode.ember_reply,
        "cited_chunk_ids": list(episode.cited_chunk_ids),
        "funi_model": episode.funi_model,
        "well_disconnected": episode.well_disconnected,
        "started_at": _iso(episode.started_at),
        "completed_at": _iso(episode.completed_at),
        "persona_id": episode.persona_id,
        "conversation_id": episode.conversation_id,
    }


def episode_from_payload(payload: object) -> Episode:
    """Rebuild an Episode from a journal payload. Raises ValueError
    naming the defect when the payload is not a valid episode —
    callers treat that as corruption, never as a crash."""
    if not isinstance(payload, dict):
        raise ValueError(f"payload must be a JSON object, got {type(payload).__name__}")
    for key in ("operator_input", "ember_reply"):
        if not isinstance(payload.get(key), str):
            raise ValueError(f"payload field {key!r} must be a string")
    cited_raw = payload.get("cited_chunk_ids", [])
    if not isinstance(cited_raw, list):
        raise ValueError("payload field 'cited_chunk_ids' must be a list")
    try:
        cited = tuple(int(c) for c in cited_raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"payload field 'cited_chunk_ids' holds a non-integer: {exc}") from exc
    persona = payload.get("persona_id", "default")
    if not isinstance(persona, str) or not persona:
        raise ValueError("payload field 'persona_id' must be a non-empty string")
    conversation = payload.get("conversation_id", "default")
    if not isinstance(conversation, str) or not conversation:
        raise ValueError("payload field 'conversation_id' must be a non-empty string")
    return Episode(
        operator_input=payload["operator_input"],
        ember_reply=payload["ember_reply"],
        cited_chunk_ids=cited,
        funi_model=str(payload.get("funi_model") or ""),
        well_disconnected=bool(payload.get("well_disconnected", False)),
        started_at=_parse(payload.get("started_at")),
        completed_at=_parse(payload.get("completed_at")),
        persona_id=persona,
        conversation_id=conversation,
    )


@dataclass(frozen=True, slots=True)
class CorruptEntry:
    path: Path
    detail: str


@dataclass(frozen=True, slots=True)
class DrainResult:
    flushed: int = 0
    kept: int = 0
    corrupt: tuple[CorruptEntry, ...] = ()
    failure: str | None = None


@dataclass(slots=True)
class PendingJournal:
    """A pending-episodes journal rooted at one directory."""

    root: Path

    # ---------------------------------------------------------- writes

    def append(self, episode: Episode) -> Path:
        """Atomically append one episode; returns its file path.

        Raises OSError on failure — the caller (chat) speaks the
        failure; the journal never swallows it."""
        self.root.mkdir(parents=True, exist_ok=True)
        stamp = (episode.completed_at or datetime.now(tz=UTC)).astimezone(UTC)
        name = f"{stamp.strftime('%Y%m%dT%H%M%S%f')}-{uuid.uuid4().hex[:12]}.json"
        target = self.root / name
        payload = json.dumps(episode_to_payload(episode), ensure_ascii=False, indent=2)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=str(self.root),
            prefix=name, suffix=".tmp", delete=False,
        ) as tmp:
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        try:
            os.replace(tmp_path, target)
        except OSError:
            with contextlib.suppress(OSError):
                tmp_path.unlink()
            raise
        _fsync_dir(self.root)
        return target

    # ---------------------------------------------------------- reads

    def files(self) -> list[Path]:
        if not self.root.is_dir():
            return []
        return sorted(p for p in self.root.glob("*.json") if p.is_file())

    def load_all(self) -> tuple[list[Episode], tuple[CorruptEntry, ...]]:
        """Every valid pending episode in turn order, plus every
        corrupt entry found. Corrupt files are left in place here;
        quarantine happens in drain() (the act that reports them)."""
        episodes: list[Episode] = []
        corrupt: list[CorruptEntry] = []
        for path in self.files():
            ep, bad = self._read_one(path)
            if bad is not None:
                corrupt.append(bad)
            elif ep is not None:
                episodes.append(ep)
        return episodes, tuple(corrupt)

    def count(self) -> int:
        return len(self.files())

    # ---------------------------------------------------------- drain

    def drain(self, brunnr: object) -> DrainResult:
        """Flush pending episodes into a live Well handle, in order.

        Each file is deleted only after ``add_episode`` accepts its
        episode. The first refusal stops the drain (remaining files
        kept, in order) and is reported as ``failure``. Corrupt
        files are quarantined into ``corrupt/`` and reported."""
        flushed = 0
        corrupt: list[CorruptEntry] = []
        failure: str | None = None
        kept = 0
        paths = self.files()
        for idx, path in enumerate(paths):
            ep, bad = self._read_one(path)
            if bad is not None:
                corrupt.append(bad)
                self._quarantine(path)
                continue
            assert ep is not None  # noqa: S101 — _read_one invariant
            try:
                brunnr.add_episode(ep)  # type: ignore[attr-defined]
            except Exception as exc:
                failure = f"{type(exc).__name__}: {exc}"
                kept = len(paths) - idx
                break
            with contextlib.suppress(OSError):
                path.unlink()
            flushed += 1
        else:
            kept = 0
        if flushed:
            _fsync_dir(self.root)
        return DrainResult(
            flushed=flushed, kept=kept, corrupt=tuple(corrupt), failure=failure,
        )

    # ---------------------------------------------------------- internals

    def _read_one(self, path: Path) -> tuple[Episode | None, CorruptEntry | None]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, CorruptEntry(path=path, detail=f"{type(exc).__name__}: {exc}")
        try:
            return episode_from_payload(payload), None
        except ValueError as exc:
            return None, CorruptEntry(path=path, detail=str(exc))

    def _quarantine(self, path: Path) -> Path:
        target_dir = self.root / _CORRUPT_SUBDIR
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / path.name
        with contextlib.suppress(OSError):
            os.replace(path, target)
        return target


def _iso(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _parse(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _fsync_dir(path: Path) -> None:
    with contextlib.suppress(OSError):
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


__all__ = [
    "CorruptEntry",
    "DrainResult",
    "PendingJournal",
    "episode_from_payload",
    "episode_to_payload",
    "pending_root",
]
