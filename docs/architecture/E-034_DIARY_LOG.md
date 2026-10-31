# E-034 — Logging a Friend Can Read: The Diary Beside the Technical Trace

*Part II, slice E-034.*

## The two logs, stated plainly

Ember now keeps two different records, for two different readers:

- **The technical trace** (unchanged, `src/ember/logging.py`):
  timestamps, levels, logger names, structured fields — for
  people who maintain the program and need to find a fault.
- **The diary** (new, `src/ember/diary.py`): one plain sentence
  per thing that happened — *a chat session started*, *the
  memory store was connected*, *a turn was answered*, *the turn
  was saved* — for the friend who lives with the companion and
  simply wants to know what it has been doing.

A person should never have to read a stack trace to learn that
their companion had a good day, or a bad one.

## Where it lives, and why it is shaped that way

- **Daily files**: `<config root>/diary/YYYY-MM-DD.md`, each
  opening with a plain header (`# Ember's diary — 2026-10-31`)
  and holding one `- HH:MM — sentence` line per entry. Daily
  files were chosen over one ever-growing diary file for the
  tiny-hardware reason that governs this project: an entry is
  an O(1) append that never rewrites yesterday, growth is one
  small file per day, and an old day can be removed whole,
  without parsing anything, when a person wants it gone.
- **Appends, not atomic rewrites**: an entry is a single short
  line, written in one `O_APPEND` write, flushed and fsynced.
  The pending journal's tmp-file + replace shape (E-031) exists
  because a torn Episode is lost memory; a torn diary line
  loses at most one sentence and stays visible as damage. The
  simpler shape is the honest one here.
- **Never raises**: every write returns a bool. In chat, the
  first failed write of a session warns **once** on stdout, in
  plain words ("Ember's diary could not be written… The chat
  itself is unaffected"), and the session serves on.
- **Stdlib only**, like the rest of the core.

## What it records — and what it deliberately never records

Recorded, in plain words, from `chat` (and therefore `ask`,
which is the same loop): a session started, with the
companion's name and the model it is running; a session that
could not start, and why, in plain words; the memory store
connected, or not reached; saved turns from an earlier session
drained into the store (how many; damaged files moved aside,
not deleted; a failed drain kept for next time); earlier
exchanges loaded from memory (how many), or a load that failed
(they were not deleted); each turn's outcome — answered,
answered without memory grounding, stopped before its reply
finished, ended with an error, or cut off for length; where
each turn was saved — to the memory store, saved locally for a
later session, or saved nowhere (remembered only until the
session ends); and the session ending.

**Never recorded**: what the operator wrote, what Ember
replied, any secret or key material, logger names, exception
class names, or file paths as a headline. The diary records
*that* things happened — counts, the companion's name, the
model's name, outcomes — and nothing of the conversation
itself. The tests pin this: scripted operator and reply text
marked as must-not-leak appears nowhere in the diary, including
for turns drained from the pending journal.

## Turning it off, and reading it

- `logging.diary` in the one config file (E-033's surface),
  `true` by default, documented in plain words in
  `config/ember.example.yaml`. Off stops new entries; it does
  not lock away entries already kept.
- **`ember diary`** prints the last seven days of entries,
  oldest first (`--days N` reads further back; a diary with no
  entries says so, plainly). Reading needs no identity or
  setup — it is the friend's surface, not the operator's.

## Honest limits

- **Tool rounds are not in the diary yet.** Which tool was
  used, and whether it was approved or refused, already has a
  complete home — the tool audit log — and the chat drivers do
  not currently surface per-round facts to the persistence
  step where diary entries are written. Wiring that cleanly
  (rather than scraping the audit log) is future work; this
  slice does not pretend the entries exist.
- Entries are local time with no timezone label, matching how
  a person reads a diary; the technical trace keeps exact,
  labelled timestamps for anyone who needs them.
- Nothing prunes old diary files yet: growth is bounded by
  days lived × a handful of short lines, and removal is a
  whole-file delete by hand. An automatic tidy-up belongs with
  the storage-hygiene work, not silently inside this slice.
- A diary entry is written after the fact it describes (the
  save outcome is recorded once the save is known), so a hard
  kill in the middle of a turn can leave that turn unrecorded —
  the same honesty boundary the pending journal documents.

## Tests

`tests/unit/test_diary_e034.py` — **13 passed**: plain dated
entries; an entry is always one line; recent entries read back
with dates (and a missing diary reads empty); diary off writes
nothing; a write failure never raises; chat records the
session + turn facts with no operator/reply content anywhere;
a disconnected session is recorded plainly (ungrounded answer,
turn saved locally); drained saved turns are recorded without
their content; diary off via config writes nothing and chat
still serves; a blocked diary warns exactly once and never
crashes the session; the technical trace still configures
unchanged beside the diary; `ember diary` prints entries, and
says "No diary entries yet." when there are none. The E-033
tree-walk test stays green: the new `logging.diary` key is
documented in the template.
