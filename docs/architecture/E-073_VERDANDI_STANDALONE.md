# E-073 — Verdandi standalone: the hub usable without the full companion

*Roadmap slice E-073 (Part IV — Verdandi: the Nerve Hub).
The law is stated in code at `Verdandi/standalone.py` and
carried inline by its two consumers of the hub's home:
`Verdandi/nervous_system.py` (the hub) and
`src/ember/nerve.py` (the core's nerve bridge). Pinned by
`tests/unit/test_standalone_e073.py`.*

## 1. The claim

The nerve hub is usable **without the full companion**:
no Ember process needs to be running, installed, or even
importable for the hub to serve, publish, and answer.
Its own consumers exist in the constellation — in-tree:
the hub's own CLI, the heartbeat's reward producers and
the conversation logger (both via the hub module's
`publish_event_sync`), and the Ember core's nerve bridge
when the companion *is* present; external: Hermes-shaped
publishers (E-068). The companion is one consumer among
several, never a prerequisite.

## 2. What standalone takes

- **One file.** `Verdandi/nervous_system.py` is a
  stdlib-only Python module (the hub has been file-loaded
  by its consumers since E-059). Run it by path, or use
  the installed `verdandi` console script; there is
  nothing else to install and no network to reach — the
  transport is a Unix-domain socket.
- **The eight commands** are the whole surface:
  `serve`, `publish`, `stimulus`, `recent`, `subscribe`,
  `status`, `healthcheck`, `stop`.
- **The wire is the E-061 contract**, not the companion:
  events over the socket (`runa.sock`), or the feed file
  (`nerve_feed.jsonl`) in the fallback shape. Anything
  that can open a Unix socket or write a JSON line is a
  hub client (E-074 documents this for member-builders).

## 3. The home law (the slice's one repair)

Before this slice the hub's state dir was hard-coded to
`~/.hermes/state`: standalone use still silently required
a Hermes-shaped home, and a machine with no Hermes at all
would have the hub writing into a directory tree named
for another system. The law now:

- `VERDANDI_HOME`, when set and non-empty, **is** the
  hub's state dir (socket, feed, PID and log all live
  directly in it);
- otherwise the state dir is `~/.hermes/state` — the
  default every existing consumer already expects,
  byte-for-byte unchanged behaviour for every current
  deployment.

The resolution is stated once in
`Verdandi/standalone.py` (`resolve_state_dir`) and carried
inline by the hub module (whose deployed form is a lone
file in the state dir itself) and by the core bridge
(under its no-member-imports discipline, E-067); the
conformance tests pin all three resolutions equal,
including by importing the real hub module in a
subprocess under both shapes of environment.

## 4. Live proof (this slice, this machine)

The hub was booted by file path alone with
`HOME=/tmp/e73home` (empty), `VERDANDI_HOME=/tmp/e73state`,
no `PYTHONPATH`, cwd `/tmp` — no Ember anywhere:

- the socket appeared at `/tmp/e73state/runa.sock`;
- `healthcheck` exited 0: ALL CHECKS PASSED (socket
  responsive, feed healthy, PID valid);
- `publish standalone_probe` was acked as event #1;
  `recent` showed it; `status` reported the relocated
  socket/feed paths; the feed held exactly that event;
- the isolated HOME stayed **completely empty** — no
  `.hermes`, no `.ember`: the hub lived entirely in its
  relocated home.

One wart the proof exposed, recorded not hidden:
`stop` reported "Process could not be killed" after
sending SIGTERM — yet the serve process had in fact
exited by that SIGTERM (exit −15). The cause is in
`cmd_stop`: its `os.kill(pid, 0)` liveness probe succeeds
for a zombie child the parent has not reaped, so an
unreaped-but-dead hub reads as unkillable. Real shell use
reaps promptly; the false report is still wrong. New
**docket 106** (cmd_stop's zombie-blind liveness probe),
owned by the E-076 gate review. Log:
`~/workspace/.verify-tmp/ember-e073/live_proof.log`.

## 5. Honest limits

- The **heartbeat** is a separate daemon with its own
  path law (`Verdandi/heartbeat/paths.py`): its
  `VERDANDI_HOME` is its own home, with a different
  socket layout (`run/verdandi.sock` under it). The name
  is shared; the homes are distinct, and this slice did
  not unify them — conflating them silently would have
  broken the live Hermes deployment's heartbeat.
- The shipped **systemd units still hard-code one
  machine**: `Verdandi/systemd/verdandi.service` starts
  a copy of the hub from `/home/pi/.hermes/state`, and
  the heartbeat unit likewise names `%h/.hermes/state`
  and `%h/Verdandi`. They describe the Pi deployment
  they were written for, not a standalone install. New
  **docket 105** (machine-hard-coded systemd units),
  owned by E-076.
- Install-from-package (`pip install` of the Verdandi
  member and its console scripts) was not proven in
  this slice; standalone is proven at the file level,
  which is how every in-tree consumer already loads it.

## 6. Slice gate

Recorded in `CAMPAIGN_STATE.md` (the E-070 pattern):
the new conformance suite, the combined Part IV
conformance run, the Verdandi focal sets, and the root
Run B / Run D gates, all by the E-017 method. The E-072
re-verification duty was discharged by this same tick:
Run D re-verified green (1330 passed, 0 failed, its log
agrees), and the canonical heartbeat focal set
(heartbeat + actions + checks + skuld, 374 tests) was
re-run green at this slice's gate. The broader
test_heartbeat*.py glob set (388 tests, including the
integration file) scores 383 passed / 5 failed, the 5
being the pre-existing machine-coupled CLI tests of
docket item 6's family (their subprocesses cd to
~/Verdandi, absent on this VM) — recorded in the
campaign state with a correction to this tick's first
re-verification entry, whose heartbeat counts came from
a mismatched run report rather than the run's log.

*Filed by the E-073 slice, 2026-10-31. Next: E-074 —
Docs: the nerve model for member-builders.*
