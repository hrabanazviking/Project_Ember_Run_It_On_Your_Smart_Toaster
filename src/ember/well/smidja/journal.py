"""Smiðja's resumable progress journal.

Per ``docs/adapters/SMIDJA_INGEST_PATTERNS.md`` §5: one JSON file per
ingest job at ``~/.ember/state/smidja_progress/<job_id>.json``,
heartbeated every ~30 s, atomically moved to a ``done/`` subdirectory on
clean completion.

The journal is what makes overnight Pi-class ingest *bearable* — kill
mid-job, rerun the same command, resume from the last committed entry.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import tempfile
import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from ember.schemas.config import JournalConfig
from ember.schemas.errors import IngestError
from ember.schemas.ingest import IngestEntry, IngestEntryStatus, IngestSourceKind

logger = logging.getLogger(__name__)

_DONE_SUBDIR = "done"


@dataclass(slots=True)
class JournalState:
    """Mutable in-memory mirror of the on-disk journal file."""

    job_id: str
    source_kind: IngestSourceKind
    source_root: str
    started_at: str
    last_heartbeat: str
    entries: dict[str, dict] = field(default_factory=dict)

    def to_payload(self) -> dict:
        return {
            "job_id": self.job_id,
            "source_kind": self.source_kind.value,
            "source_root": self.source_root,
            "started_at": self.started_at,
            "last_heartbeat": self.last_heartbeat,
            "entries": self.entries,
        }

    @classmethod
    def from_payload(cls, payload: dict) -> JournalState:
        """Reconstruct from a JSON dict. Refuses malformed payloads.

        A corrupted on-disk journal (truncated write, manual edit,
        version-skew between two Ember installs) would otherwise
        produce a bare ``KeyError`` or ``ValueError`` at resume time,
        crashing the ingest with a confusing traceback. The hardening
        pass wraps each missing-field and bad-enum case in
        :class:`IngestError` so the operator gets one clear line
        naming the field and the file.
        """
        required = ("job_id", "source_kind", "source_root", "started_at", "last_heartbeat")
        missing = [k for k in required if k not in payload]
        if missing:
            raise IngestError(
                f"journal payload missing required field(s): {missing!r}"
            )
        try:
            source_kind = IngestSourceKind(payload["source_kind"])
        except ValueError as exc:
            raise IngestError(
                f"journal payload has unknown source_kind "
                f"{payload['source_kind']!r}: {exc}"
            ) from exc
        entries_raw = payload.get("entries", {})
        if not isinstance(entries_raw, dict):
            raise IngestError(
                f"journal payload `entries` must be a dict, got "
                f"{type(entries_raw).__name__}"
            )
        return cls(
            job_id=payload["job_id"],
            source_kind=source_kind,
            source_root=payload["source_root"],
            started_at=payload["started_at"],
            last_heartbeat=payload["last_heartbeat"],
            entries=dict(entries_raw),
        )


class Journal:
    """One ingest job's journal handle.

    Pattern of use:

        journal = Journal.open(config, source_kind, source_root)
        for entry_id, parsed_file in source.walk(...):
            if journal.is_done(entry_id):
                continue
            journal.mark_in_progress(entry_id)
            ...
            journal.mark_done(entry_id, chunk_count=n)
        journal.complete()  # moves file to done/
    """

    def __init__(self, path: Path, state: JournalState, config: JournalConfig) -> None:
        self._path = path
        self._state = state
        self._config = config
        self._writes_since_heartbeat = 0
        self._heartbeat_every = 16  # flush at least every N updates

    # ------------------------------------------------------------- open

    @classmethod
    def open(
        cls,
        config: JournalConfig,
        source_kind: IngestSourceKind,
        source_root: str,
        *,
        job_id: str | None = None,
    ) -> Journal:
        """Open or resume a journal for the given source root.

        If an in-progress journal exists for the same ``source_root``,
        it is resumed unless ``job_id`` is given explicitly. Otherwise a
        new journal is created.
        """
        root_dir = Path(config.root).expanduser()
        root_dir.mkdir(parents=True, exist_ok=True)
        (root_dir / _DONE_SUBDIR).mkdir(parents=True, exist_ok=True)

        if job_id is None:
            existing = cls._find_existing(root_dir, source_root)
            if existing is not None:
                path, state = existing
                # Stale-heartbeat check (wires up
                # JournalConfig.stale_heartbeat_s which was previously
                # declared in the schema but never read). If the
                # existing journal's last heartbeat is older than the
                # configured threshold, treat it as crashed — log a
                # warning, archive the stale file, and start fresh.
                # Without this, resuming a journal from a crashed run
                # that's hours/days old can produce confusing results
                # (the previously-in-progress entries may have already
                # been re-ingested via a separate run, leading to
                # duplicate chunks).
                if _heartbeat_is_stale(
                    state.last_heartbeat, config.stale_heartbeat_s,
                ):
                    logger.warning(
                        "journal %s is stale "
                        "(last heartbeat %s, threshold %ds); "
                        "archiving and starting fresh",
                        path.name, state.last_heartbeat,
                        config.stale_heartbeat_s,
                    )
                    cls._archive_stale(path)
                else:
                    state.last_heartbeat = _now_iso()
                    cls._write_state(path, state)
                    return cls(path, state, config)
            job_id = str(uuid.uuid4())

        now = _now_iso()
        state = JournalState(
            job_id=job_id,
            source_kind=source_kind,
            source_root=source_root,
            started_at=now,
            last_heartbeat=now,
        )
        path = root_dir / f"{job_id}.json"
        cls._write_state(path, state)
        return cls(path, state, config)

    # ------------------------------------------------------------- queries

    @property
    def job_id(self) -> str:
        return self._state.job_id

    @property
    def path(self) -> Path:
        return self._path

    def is_done(self, entry_id: str) -> bool:
        entry = self._state.entries.get(entry_id)
        return entry is not None and entry.get("status") == IngestEntryStatus.DONE.value

    def get_entry(self, entry_id: str) -> IngestEntry | None:
        raw = self._state.entries.get(entry_id)
        if raw is None:
            return None
        return IngestEntry(
            path_or_id=entry_id,
            hash=raw.get("hash"),
            status=IngestEntryStatus(raw["status"]),
            chunk_count=int(raw.get("chunk_count", 0)),
            error=raw.get("error"),
            committed_through_chunk=raw.get("committed_through_chunk"),
        )

    def entries(self) -> list[IngestEntry]:
        return [
            IngestEntry(
                path_or_id=key,
                hash=raw.get("hash"),
                status=IngestEntryStatus(raw["status"]),
                chunk_count=int(raw.get("chunk_count", 0)),
                error=raw.get("error"),
                committed_through_chunk=raw.get("committed_through_chunk"),
            )
            for key, raw in self._state.entries.items()
        ]

    # ------------------------------------------------------------- writes

    def mark_in_progress(self, entry_id: str, *, content_hash: str | None = None) -> None:
        self._state.entries[entry_id] = {
            "status": IngestEntryStatus.IN_PROGRESS.value,
            "hash": content_hash,
            "chunk_count": 0,
            "error": None,
            "committed_through_chunk": None,
        }
        self._touch()

    def mark_progress(self, entry_id: str, committed_through_chunk: int) -> None:
        entry = self._state.entries.setdefault(
            entry_id,
            {
                "status": IngestEntryStatus.IN_PROGRESS.value,
                "hash": None,
                "chunk_count": 0,
                "error": None,
                "committed_through_chunk": None,
            },
        )
        entry["committed_through_chunk"] = committed_through_chunk
        self._touch()

    def mark_done(
        self, entry_id: str, *, chunk_count: int, content_hash: str | None = None
    ) -> None:
        entry = self._state.entries.setdefault(entry_id, {})
        entry.update(
            {
                "status": IngestEntryStatus.DONE.value,
                "chunk_count": chunk_count,
                "hash": content_hash if content_hash is not None else entry.get("hash"),
                "error": None,
            }
        )
        self._touch(force=True)

    def mark_failed(self, entry_id: str, error: str) -> None:
        entry = self._state.entries.setdefault(entry_id, {})
        entry.update(
            {
                "status": IngestEntryStatus.FAILED.value,
                "error": error,
            }
        )
        self._touch(force=True)

    def heartbeat(self) -> None:
        self._touch(force=True)

    def pending(self, candidate_ids: Iterable[str]) -> list[str]:
        return [eid for eid in candidate_ids if not self.is_done(eid)]

    # ------------------------------------------------------------- close

    def complete(self) -> Path:
        """Atomically move the journal to the done/ subdirectory."""
        self._touch(force=True)
        done_dir = self._path.parent / _DONE_SUBDIR
        done_dir.mkdir(parents=True, exist_ok=True)
        target = done_dir / self._path.name
        try:
            os.replace(self._path, target)
        except OSError as exc:
            raise IngestError(f"journal complete failed: {exc}") from exc
        return target

    # ------------------------------------------------------------- internals

    def _touch(self, *, force: bool = False) -> None:
        self._state.last_heartbeat = _now_iso()
        self._writes_since_heartbeat += 1
        if force or self._writes_since_heartbeat >= self._heartbeat_every:
            self._write_state(self._path, self._state)
            self._writes_since_heartbeat = 0

    @staticmethod
    def _write_state(path: Path, state: JournalState) -> None:
        # Atomic write: NamedTemporaryFile + os.replace. The tempfile is
        # created with delete=False so we own its lifetime; on a failed
        # os.replace (cross-filesystem, EACCES, ENOSPC) the temp file
        # would otherwise accumulate in the journal directory across
        # repeated ingest runs and eventually fill the disk on a Pi.
        # Hardening pass added the explicit unlink-on-failure.
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=path.name,
            suffix=".tmp",
            delete=False,
        ) as tmp:
            json.dump(state.to_payload(), tmp, ensure_ascii=False, indent=2)
            tmp_path = Path(tmp.name)
        try:
            os.replace(tmp_path, path)
        except OSError:
            with contextlib.suppress(OSError):
                tmp_path.unlink()
            raise

    @staticmethod
    def _find_existing(
        root_dir: Path, source_root: str
    ) -> tuple[Path, JournalState] | None:
        for candidate in sorted(root_dir.glob("*.json")):
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if payload.get("source_root") == source_root:
                return candidate, JournalState.from_payload(payload)
        return None

    @staticmethod
    def _archive_stale(path: Path) -> None:
        """Move a stale journal aside with a `.stale-<timestamp>` suffix.

        We don't delete it — an operator inspecting their journal
        directory should be able to see what was abandoned and when.
        """
        suffix = f".stale-{int(datetime.now(tz=UTC).timestamp())}"
        archive_path = path.with_suffix(path.suffix + suffix)
        try:
            path.rename(archive_path)
        except OSError as exc:
            logger.warning(
                "journal stale-archive failed for %s: %s; "
                "leaving file in place", path.name, exc,
            )


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def _heartbeat_is_stale(last_heartbeat: str, threshold_s: int) -> bool:
    """Return True if ``last_heartbeat`` (ISO-8601 string) is older than
    ``threshold_s`` seconds from now.

    Defensive: a malformed timestamp is treated as NOT stale (we'd rather
    attempt resume than wrongly discard work). The malformed case is
    logged at debug level.
    """
    try:
        last = datetime.fromisoformat(last_heartbeat)
    except (ValueError, TypeError) as exc:
        logger.debug(
            "journal heartbeat unparseable (%r); treating as fresh: %s",
            last_heartbeat, exc,
        )
        return False
    # ISO-8601 from _now_iso() always carries tz; if a legacy file has
    # a naive timestamp, normalize to UTC for the comparison.
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    age_s = (datetime.now(tz=UTC) - last).total_seconds()
    return age_s > threshold_s


__all__ = ["Journal", "JournalState"]
