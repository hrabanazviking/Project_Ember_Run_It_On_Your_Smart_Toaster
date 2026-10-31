"""The diary — a log a friend can read (E-034).

Beside the technical trace (``ember.logging``, for people who
maintain the program) Ember keeps a *diary*: one plain sentence
per thing that happened, in dated Markdown files a friend can
open and understand without knowing any jargon.

Shape, chosen for tiny hardware and bounded growth:

* **One file per day** — ``<config_root>/diary/YYYY-MM-DD.md``.
  A day's file is only ever appended to, never rewritten, so a
  write is O(1) however long Ember has lived; old days are whole
  files a person (or a later tidy-up slice) can remove without
  parsing anything. No single ever-growing diary file.
* **Append with flush + fsync.** Unlike the pending-episodes
  journal (E-031), an entry is a single short line, so the
  tmp-file + ``os.replace`` atomic-write shape would rewrite
  nothing but would cost a directory churn per entry for no
  extra safety: a torn last line is visible, human, and loses
  at most that one sentence. The append opens with ``O_APPEND``,
  writes the whole line in one call, flushes, and fsyncs before
  reporting success.
* **Never raises.** A diary that crashes the chat would be a
  diary that harms the companion it describes. Every write
  returns a bool instead: True when the entry landed (or the
  diary is on and the sentence was empty — nothing to write),
  False when it did not, including when the diary is off.
* **No conversation content, ever.** Callers pass *facts about*
  a turn (that it was answered, that it was saved), never the
  operator's words, never the reply's words, never a secret.
  The Diary itself adds only the date, the time, and the
  sentence it was given, on one line (newlines in a sentence
  are folded to spaces so one entry is always one line).

Stdlib only, like the rest of the core.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path


def diary_root(config_root: Path) -> Path:
    """The diary directory for one config root (E-020 tether)."""
    return Path(config_root).expanduser() / "diary"


class Diary:
    """A plain-words, append-only diary rooted at one directory."""

    def __init__(self, root: Path, *, enabled: bool = True) -> None:
        self.root = Path(root).expanduser()
        self.enabled = enabled

    # ---------------------------------------------------------- writes

    def record(self, sentence: str, *, when: datetime | None = None) -> bool:
        """Append one plain sentence to today's file. Never raises.

        Returns True when the entry was written, False when the
        diary is off or the write failed for any reason."""
        if not self.enabled:
            return False
        text = " ".join(str(sentence).split())
        if not text:
            return True
        stamp = when or datetime.now().astimezone()
        line = f"- {stamp:%H:%M} — {text}\n"
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            path = self.root / f"{stamp:%Y-%m-%d}.md"
            is_new = not path.exists()
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                if is_new:
                    os.write(fd, f"# Ember's diary — {stamp:%Y-%m-%d}\n\n".encode())
                os.write(fd, line.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
        except Exception:
            return False
        return True

    # ---------------------------------------------------------- reads

    def read_recent(
        self, *, days: int = 7, max_entries: int = 200, now: datetime | None = None,
    ) -> tuple[str, ...]:
        """Recent entries, oldest first, as ``YYYY-MM-DD HH:MM — …`` lines.

        Reads the last ``days`` daily files (including today),
        skips headers and blank lines, and keeps at most the
        newest ``max_entries`` entries. A missing diary reads as
        empty; an unreadable file is skipped, never raised —
        reading a friend's diary must not crash because one page
        is damaged."""
        if days < 1 or max_entries < 1:
            return ()
        today = (now or datetime.now().astimezone()).date()
        entries: list[str] = []
        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)
            path = self.root / f"{day:%Y-%m-%d}.md"
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for line in lines:
                line = line.strip()
                if line.startswith("- "):
                    entries.append(f"{day:%Y-%m-%d} {line[2:]}")
        return tuple(entries[-max_entries:])


__all__ = ["Diary", "diary_root"]
