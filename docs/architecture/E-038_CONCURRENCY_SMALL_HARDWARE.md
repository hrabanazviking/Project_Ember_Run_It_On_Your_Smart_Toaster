# E-038 — Concurrency on small hardware

*Part II, slice E-038. Roadmap line: "Concurrency on small
hardware: two chats, phone-class budgets, measured."*

## Why

Everything Part II built was exercised one chat at a time. But
the tether (E-020) is one folder on one small machine, and
normal life on that machine is not serial: a second terminal,
a scheduled ask, a partner picking up the same companion. Two
chats at once share the Well file, the pending journal, the
diary, and the tool audit log. This slice ran two chats at
once for the first time, found three real races on those
shared surfaces, fixed all three in scope, and measured what
the second chat costs on the phone profile.

## The three races, and their fixes

**1. The pending journal drained twice.** Two chats starting
together both see pending turns from an earlier disconnected
session and both drain them (chat drains before history
loads, E-031). Before E-038, `PendingJournal.drain` read the
file list, added each episode, then deleted the file — two
concurrent drains added **every episode twice**. Fix: a drain
now *claims* each file before touching it, by atomically
renaming it to `<name>.claimed-<token>` (`os.replace` is
atomic; the claimed name no longer matches the `*.json` glob,
so no other drain and no `load_all` can see it). Only the
claim's owner reads, adds, and deletes it. A Well refusal
releases the claim back under the original name, in order,
and `kept` counts what actually remains. A drain that loses
every claim reports nothing flushed and nothing kept — the
turns are being flushed by the other session, not lost.

**2. The diary wrote its header twice.** Two writers opening
a new day's file could both see it as new and each write the
`# Ember's diary` header, and one writer's header could land
between the other's header and first line. Fix
(`ember.diary`): the size check and the write now happen
under an exclusive advisory lock (`fcntl.flock` where POSIX
offers it; platforms without it keep the previous append
behaviour), and "new" is judged by the opened file's size,
not by a pre-open existence check. The diary still never
raises.

**3. The Well refused the second writer.** The sqlite_vec
adapter opened its connection with no busy timeout: two
processes saving turns to the same Well file could fail a
save with "database is locked" instead of waiting out the
other's commit. Fix: `PRAGMA busy_timeout = 5000` at open —
WAL already allows one writer at a time; now the second
writer waits (5 s is far beyond any single Episode commit
on phone-class hardware).

What did **not** race, checked and pinned as-is: journal
*appends* (one uniquely-named atomic file per episode,
E-031's shape — 2×15 concurrent appends lose nothing), and
the tool audit log (one `O_APPEND` write-all per record,
already cross-process safe by construction). Each chat's
in-session state (episode list, window, tool session grants)
lives in its own `chat.run` invocation and is never shared.

## Two chats, phone-class budgets, measured

The phone profile (E-021) gives each session a 1024-token
history budget and a 5-episode cap. The E-038 tests run two
real `chat.run` sessions concurrently (threads, one shared
Well, a synchronisation barrier inside the fake backend so
both are provably mid-turn at the same moment) and pin:

- both sessions complete (exit 0);
- isolation holds under concurrency: each session's prompt
  carries only its own conversation's episodes (E-035's wall,
  now under load), and each persisted turn carries its own
  conversation tag;
- two *disconnected* chats journal concurrently with no loss
  and both tags intact;
- each session's windowed history measures ≤ 1024 estimated
  tokens, so two concurrent sessions together stay within
  twice the phone budget (2048) — the budget is per-session
  by construction, and concurrency does not multiply it.

Wall/RSS, measured on the VM profile (fresh process per run,
fake backend with a fixed 50 ms per turn, 5 turns per chat,
histories at the phone cap): sequential two chats **1.285 s,
23.7 MiB** peak RSS; concurrent two chats **0.93 s / 0.81 s,
23.9 / 24.2 MiB**. The second concurrent session costs under
half a MiB over running the same two chats one after another
— the process figure is dominated by the interpreter and the
imported core, not by the second session. These are VM
numbers with a fake backend; no phone was used, and no live
model served either chat.

## Honest limits

- **Threads, not two OS processes.** The chat-level proof
  runs two sessions in two threads of one process. The three
  fixes are process-safe by mechanism (atomic rename, flock,
  WAL + busy_timeout) and the Well proof uses two separate
  connections to one file, but a two-*process* chat run is
  NOT PROVEN in this slice.
- **The tool registry is process-global.** `search_well`'s
  Well binding is a module-level binding: two chats in *one
  process* with tools enabled share the last-bound Well.
  Two chats as separate processes are unaffected. Named
  here, not fixed — chat is a one-session-per-process CLI
  today, and Part VIII's bridges own any in-process
  multi-session shape.
- **The model is the real shared cost.** Both chats draw on
  the same local model service; its queueing under two
  streams is the backend's behaviour, not measured here
  (no live model on the VM). Ember adds no per-session model
  state of its own beyond the window above.
- The budget book (Part III, E-041) owns turning the phone
  profile's per-session numbers into whole-machine ceilings.

## Tests

- `tests/unit/test_concurrency_e038.py` — **7 passed**
  (default env): dual-drain exactly-once, refusal releases
  the claim in order, concurrent corrupt quarantine (once),
  concurrent appends, dual-diary one-header/all-entries, the
  two-chat phone-profile run, two disconnected chats.
- `tests/unit/test_concurrency_well_e038.py` — **2 passed**
  (extras shape; skipped bare): busy_timeout pinned at
  5000 ms, two handles on one Well file land all 20 saves.
- Slice gate Run B (default env, pgvector file excluded):
  **910 passed, 6 failed, 18 skipped, 1 warning** — 903
  E-037 baseline + 7 new; the 6 are the proven environment
  failures. Run D (whole, extras): **960 passed, 0 failed,
  19 skipped, 1 warning**, exit 0 (951 baseline + 9 new).
