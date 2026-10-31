# E-059 — Verdandi Mapped: the Injector, the Logger, and the Event Model

*Part IV, slice E-059. Method: every statement below was drawn from
the code in `Verdandi/` at the slice's starting HEAD (b275aeb),
with file and symbol named. Verdandi's own elder documents
(`VERDANDI_MAP.md`, `ARCHITECTURE.md`, `INTERFACE.md`,
`DOMAIN_MAP.md`) were read as claims, not authority — where they
and the code differ, the code wins and the difference is recorded
in §9. Nothing in `Verdandi/` was modified in this slice.*

## 1. Plain-language summary

Verdandi is not one program; it is three generations of one idea —
"the parts of the companion should be able to feel each other" —
living side by side in one directory:

1. **The conversation layer** (top level): a session logger that
   writes what happened as it happens (`conversation_logger.py`),
   a thin cron shim that assembles a context block for the next
   job and can log cron sessions (`context_injector.py`), a
   read-only reactor that turns the log into "reaction directives"
   (`reactor.py`), and the **nerve hub** (`nervous_system.py`) — a
   Unix-socket publish/subscribe bus with a persistent feed.
2. **The heartbeat daemon** (`heartbeat/`): a self-contained
   package that pulses on a timer — five checks (the senses) feed
   a state machine, a reactor maps check results to five recovery
   actions, and every pulse is supposed to fire a nerve impulse.
3. **Passengers**: the `verdandi/eir/` consolidation package and
   the three `heartbeat/runa_*_system.py` modules (reward,
   negative, mood/arousal) plus `heartbeat/push_reward.py`. These
   publish nerve events or keep their own state files, but **no
   in-tree code calls them** — in this tree they are libraries
   waiting for their (deployed, out-of-tree) callers.

The map's central finding: **there is no single event model.**
The nerve hub speaks one dialect (`{type, data, source}` stamped
with `_seq/_ts/_iso`, over `~/.hermes/state/runa.sock`); the
heartbeat fires a second dialect (`{event_type, …}` flat, over a
*different* socket, `…/run/verdandi.sock`, that nothing in the
tree listens on) and falls back to writing a third shape directly
into the same feed file. The conversation logger bridges the two
worlds by hand — and only when its files have been *deployed* into
`~/.hermes/state/`, because that is the only place it looks for
the hub. E-061 (event contract v1) inherits exactly this problem;
§8 dockets it and its siblings.

Two more honest headlines: the Ember core does not touch Verdandi
at all today (`src/ember/` mentions Verdandi once, in `api.py`'s
docstring — Part IV's wiring is E-067's work, not a fact), and the
only in-tree subscriber to the nerve hub is the hub's own CLI.

## 2. Verdandi in numbers (measured this slice)

- Python, whole member: **19,194 lines** — production **11,725**,
  tests **7,469** (11 test files under `Verdandi/tests/`).
- The conversation layer: `nervous_system.py` **847** ·
  `conversation_logger.py` **619** · `reactor.py` **345** ·
  `context_injector.py` **142** lines.
- The heartbeat package: **8,618 lines** across `core.py` (813),
  `cli.py` (457), `config.py` (319), `paths.py` (278), five checks
  (base + eir/huginn/mimir/urdr/skuld), five actions (base +
  mjölnir/gungnir/bifrǫst/eir_action/vor_action), its own
  `reactor.py` (270), `signals.py` (192), `prometheus.py` (238),
  and the four `runa_*`/`push_reward` modules (613 + 609 + 1,105
  + 221).
- The Eir package (`verdandi/eir/`): **1,154 lines** (core 492,
  router 261, layers 234, config).
- Focal test proof, this slice (runner counts, §10): the four
  focal test files (`test_context_injector`,
  `test_conversation_logger`, `test_reactor`,
  `test_nervous_system`) run **101 passed** with Verdandi's
  declared dev dependency `pytest-asyncio` supplied; in the bare
  default env **95 passed, 6 failed**, and all 6 failures are the
  missing-plugin environment class (proven, §10).

## 3. The deployment shape (read this first)

Everything at Verdandi's top level is written for a **deployed
home**, not for running out of this tree:

- `conversation_logger.py:56-59` and `nervous_system.py:53-56`
  hardcode `STATE_DIR = Path.home() / ".hermes" / "state"`. The
  logger's log, `current.json`, and the nerve feed all live there,
  whatever directory the script itself sits in.
- `context_injector.py:30` does
  `sys.path.insert(0, str(Path.home() / ".hermes" / "state"))` and
  imports `conversation_logger` — the deployed copy wins if one
  exists there; the in-tree copy is only a fallback via the
  script's own directory.
- `conversation_logger._nerve_fire` (lines 83-105) loads
  `nervous_system.py` **only** from `~/.hermes/state/` (cached,
  refreshed when the path changes; every failure swallowed —
  "nerve failure must NEVER break the logger"). Run from this
  tree on a machine without that deployed copy, the logger works
  fully and silently fires nothing.
- The heartbeat package is the exception: `heartbeat/paths.py`
  resolves its home by priority — `VERDANDI_HOME` env → an
  existing `~/.hermes/state` → XDG dirs → `./verdandi_state/` dev
  fallback — and puts its socket at `<base>/run/verdandi.sock`,
  its DB at `<base>/verdandi_heartbeat.db`.

On this VM, `~/.hermes/state/` holds heartbeat deployment
artefacts (DB, feed, config, run/) but **no** deployed
`nervous_system.py`/`conversation_logger.py` copies — so the
conversation layer's nerve bridge is dormant here by shape, not
by failure. E-006 proved the hub itself LIVE when served.

## 4. conversation_logger — the streaming session log

`conversation_logger.py` (619 lines, stdlib only). Design rule,
from its own docstring: *log as it happens, not at the end — a
crashed session loses only the last line.*

**Storage.** Append-only JSONL at
`~/.hermes/state/conversation_log.jsonl`
(`CONV_LOG = STATE_DIR / "conversation_log.jsonl"`; a
`conversations/` directory is created beside it but the log does
not live in it), one JSON
object per line, plus a `current.json` snapshot overwritten on
every operation. Reads re-parse the whole JSONL and silently skip
unparseable lines (`_read_all_entries`).

**Entry model** — four `entry_type`s, all carrying `timestamp`
(UTC ISO) and `session_id`:

| entry_type | written by | fields beyond the common two |
|---|---|---|
| `start` | `cmd_start` | `summary`, `model`, `platform`, `start_time` |
| `event` | `cmd_event` | `event_type`, `content` |
| `update` | `cmd_update` | `next_actions`, `blockers`, `projects_touched`, `mood` (snapshot of current state) |
| `end` | `cmd_end` | `summary`, `duration_minutes` (arg, or computed from `start_time`), and the session's accumulated `decisions`, `things_learned`, `files_changed`, `next_actions`, `blockers`, `projects_touched` copied out of `current.json` |

**Event vocabulary.** `EVENT_TYPES` (line 63) is exactly 8:
`decision, file_changed, learned, action, blocker,
blocker_resolved, mood_shift, milestone`. `cmd_event` validates
against it (exit 1 on anything else) and folds each event into
`current.json` by a fixed field map: decision→`decisions`,
file_changed→`files_changed`, learned→`things_learned`,
action→`next_actions` (note: an *action* event is stored as a
*next action*), milestone→`decisions`, mood_shift→`mood` string,
blocker→`blockers` append, blocker_resolved→`blockers` removal
by exact string match. Lists accumulate uniquely.

**Every append fires a nerve impulse**: `_append` writes the
line, then calls `_nerve_fire(entry)`, which publishes
`type = "conv_" + entry_type` (so `conv_start`, `conv_event`,
`conv_update`, `conv_end`), `data` = the whole entry,
`source = "conv_logger:<session_id>"` — through the deployed-hub
loading described in §3.

**Public API** (for the injector and cron): `get_context_for_cron`
(§5), `get_current_state`, `get_recent_conversations`, the
`cmd_*` functions, and the private `_get_entries_for_session` /
`_get_recent_sessions` the injector imports directly.
`_get_recent_sessions` returns one entry per session — the
*last-written* entry of any type, despite its docstring's "prefer
end entries" (the code takes whatever `reversed()` meets first).

**Dead code**: `_update_current` (lines 118-152) is defined and
never called anywhere in the tree — each `cmd_*` hand-rolls its
own `current.json` merge instead, with subtly different rules
(`cmd_event`, for instance, does not preserve `session_id` or
`status` if `current.json` is missing/corrupt). Docket 98 → E-063.

**Write safety, honestly**: the JSONL append is a single
`write()` per entry (no locking, no fsync); `current.json` is a
plain overwrite (not atomic). Two writers at once can interleave
the snapshot. The nerve feed (§6) is the layer that bothered with
`fcntl` locks and fsync; the conversation log did not. Noted for
E-063's logger law; not docketed separately here.

## 5. context_injector — the cron shim and the context block

`context_injector.py` (142 lines) is a CLI shim over the logger,
built for cron prompts. No subcommand (or `context`) prints the
context block; `log-start` / `log-event` / `log-end` adapt cron
sessions onto the logger's `cmd_start`/`cmd_event`/`cmd_end`;
`show` and `recent` are read views. One vocabulary divergence:
its `log-event --type` choices are **7 — `mood_shift` is
missing** from the logger's 8 (docket 97 → E-061).

**The context block** is assembled by the logger's
`get_context_for_cron(max_sessions=5)` in four layers, each
truncated, each supplementary layer failure-silent:

1. **Current state** from `current.json`: session, status, last
   updated, summary (≤120 chars), decisions (≤5), next actions
   (≤5), blockers (all), projects touched (all).
2. **Recent sessions**: the last `max_sessions` sessions, one
   line each (timestamp ≤16 chars, summary ≤100).
3. **Nerve feed tail**: the last 10 events of
   `~/.hermes/state/nerve_feed.jsonl`, read from the *file*
   (never the live hub), rendered as
   `[_iso] [type] from source: data≤100 chars`.
4. **Reaction directives**: `reactor.react()` (§7) rendered as
   `[priority] ACTION: detail` + ≤3 items per directive.

The injector's no-subcommand path additionally prints a
`=== CURRENT STATE ===` block of its own after the context.

There is **no size budget on the block as a whole** — each layer
is item-capped but nothing measures or caps the total. That is
E-062's subject (context injection discipline), recorded here as
the fact E-062 starts from.

## 6. nervous_system — the nerve hub and the hub dialect

`nervous_system.py` (847 lines, stdlib only, asyncio). A Unix
domain socket pub/sub bus: socket at `~/.hermes/state/runa.sock`
(mode 0600 after creation), persistent feed at
`~/.hermes/state/nerve_feed.jsonl`.

**Wire protocol** — newline-delimited JSON. Control messages
carry `nerve_type`: `subscribe` → hub replies `subscribed` and
adds the writer to the broadcast set; `ping` → `pong`;
`recent` (+`count`) → `recent_events` from the ring buffer.
**Any other message is a publish**: the hub stamps `_seq`
(monotonic, recovered from the feed at startup), `_ts`, `_iso`,
strips `nerve_type`, appends the line to the feed, stores it in
the 256-event ring buffer, broadcasts it to all subscribers, and
replies `ack` with the seq. On shutdown it sends subscribers a
`shutdown` notice before closing.

**The hub event shape** (what lands in the feed) is therefore:
`{type, data, source?, _seq, _ts, _iso}` — `type` and `data` set
by the publisher via `publish_event_sync(event_type, data,
source)`, the underscored fields by the hub. There is **no
schema, no version field, and no validation**: a publish with no
`type` is stamped and broadcast all the same.

**Offline behaviour**: `publish_event_sync` (2 s timeout) falls
back, when the hub is unreachable, to appending the event
directly to the feed under an `fcntl` lock with `_fallback:
True` — but *without* a `_seq` (the sequence has holes by design;
startup recovery takes the max). Feed rotation at 10 MB archives
to a gzipped `nerve_feed_<ts>.jsonl.gz`.

**Self-healing** (all in-code, all test-covered): stale-PID
refusal at startup, dead-subscriber removal on broadcast failure,
a 30 s pruner for subscribers idle >120 s — noting that a pure
listener that never sends anything is itself timed out by
`handle_client`'s 120 s read timeout, so long-lived subscribers
must ping to stay attached.

**In-tree producers** (via `publish_event_sync`, all importing
the *deployed* module by `sys.path` insertion of
`~/.hermes/state`): the conversation logger (`conv_*`, §4),
`heartbeat/push_reward.py` (`push_reward`),
`heartbeat/runa_reward_system.py` (`runa_reward`),
`heartbeat/runa_negative_system.py` (`runa_negative`). The
`runa_mood_arousal_system.py` publishes nothing — it keeps its
own state file (`runa_mood_arousal.json`).

**In-tree consumers**: the hub's own CLI (`subscribe`, `recent`,
`status`, `healthcheck`), `get_recent_events` (hub-first via a
`recent` control message, feed-file fallback), and the logger's
context builder reading the feed *file* (§5). No other code in
the tree subscribes. One defect: `get_status()` probes the hub by
calling `publish_event_sync('ping', …)` — a real publish, not
the `nerve_type: ping` control message — so every status check
appends a spurious `ping` event to the feed and broadcasts it
(docket 96 → E-066).

## 7. The two reactors

Two different modules share the reactor name; they are not
related by import.

**Top-level `reactor.py`** (345) — read-only analysis of the
conversation log + `current.json`, producing a reactions dict
with nine buckets (blockers, decisions, learnings, files changed,
milestones, next actions, stale sessions >1 h without an `end`,
cron events, and the derived priority directives HIGH/MEDIUM/
LOW/INFO). It recommends; it never acts (its learning directive,
for instance, is the *text* of a Mímir command). Its
`react(focus=…)` parameter — exposed as the CLI's `--focus` — is
**accepted and never used**: every focus value returns the full
analysis (docket 95 → E-065). Its stale-session scan is O(n²)
over the log (a full `any()` re-scan per `start` entry).

**`heartbeat/reactor.py`** (270) — the daemon's check→action
bridge. `ReactionRule`s match a `CheckResult` by check name
(`*` wildcard), minimum severity (OK 0 / UNKNOWN 1 / WARNING 2 /
CRITICAL 3), and optional `details` conditions. Six default
rules: projects→auto_push, schedule→auto_restart,
memory→auto_cleanup (WARNING+), health→auto_cleanup (CRITICAL,
with a `conditions={"disk_used_percent": True}` entry whose
comment says "any" — the matcher actually requires the detail to
equal `True`), memory→auto_heal (CRITICAL),
prediction→preemptive_heal (WARNING+). Extra rules load from
config `reactor.rules`. Actions come from `ACTION_REGISTRY`
(five registered: `auto_push` Mjölnir, `auto_restart` Gungnir,
`auto_cleanup` Bifrǫst, `auto_heal` Eir, `preemptive_heal` Vör —
the first four via decorator, Vör by direct registry assignment
at `vor_action.py:269`). `react()` skips OK results, builds an
`ActionContext`, honours each action's `should_trigger`
(cooldowns live in `actions/base.py`), executes through
`BaseAction.execute` (the crash-wrapping path E-009 found Vör
bypassing), and records an in-memory `action_history`.

## 8. The heartbeat pulse — and the second dialect

`heartbeat/core.py` (813): `HeartbeatDaemon.run()` loops —
signal flags → `pulse()` → `_update_daemon_state()` → jittered
sleep (interval default 60 s ± 5). One `pulse()`:

1. Runs every enabled check from `CHECK_REGISTRY` — exactly five:
   `health` (Eir), `projects` (Huginn), `memory` (Mimir),
   `schedule` (Urðr), `prediction` (Skuld) — each behind a
   per-check circuit breaker (5 failures / 300 s), maintenance
   windows may suppress named checks. Results are `CheckResult`
   dataclasses (`checks/base.py`: name, `CheckSeverity`
   OK/WARNING/CRITICAL/UNKNOWN, message, details, timestamp,
   duration_ms, sub_results; `to_dict()` exists expressly "for
   JSON/nerve impulses").
2. Records the health score (EMA over severity weights
   ok 100 / warning 50 / unknown 75 / critical 0) and classifies
   an emotional state from the trend (Skuld's `TrendClassifier`).
3. **Fires the nerve pulse** (if `nerve.publish_pulses`, default
   true) — *before* the reactor runs and *before* the state
   machine transitions, so the pulse event carries the
   pre-transition state.
4. Runs the reactor over the results (during maintenance,
   CRITICAL results only).
5. Persists: SQLite at `<base>/verdandi_heartbeat.db` —
   `heartbeat_state`, `pulse_history`, and `pulse_metrics`
   (pruned to the newest 10,000 rows; the write-only-metrics
   finding is E-009's, re-proven there).

The state machine (`DaemonState`: INITIALIZING → RUNNING ⇄
DEGRADED / CRITICAL → RECOVERING) is updated **only** in
`run()`'s loop after `pulse()` returns — a single `pulse()` call
(the CLI's `pulse` command, tests) never transitions state by
itself.

**The dialect problem.** `_fire_nerve_pulse` /
`_fire_nerve_state_change` (core.py:597-644) open a raw socket to
`config nerve.socket_path` or `paths.get_socket_path()` — i.e.
`<base>/run/verdandi.sock`, **not** the hub's `runa.sock` — and
send a flat JSON object whose kind key is `event_type`
(`heartbeat_pulse` with pulse_count/state/health_score/
health_trend/emotional_state/checks{severity,message};
`heartbeat_state_change` with old/new state). Nothing in this
tree listens on `verdandi.sock`. If the connect fails and
`nerve.fallback_to_file` (default true), the pulse is appended
to `<state_dir>/nerve_feed.jsonl` in a **third shape**:
`{timestamp, source: "verdandi-heartbeat", event_type, …}` — no
`type`/`data`, no `_seq/_ts/_iso`. The state-change fire has no
fallback at all: failure is silent. So one feed file legitimately
contains hub-dialect events, heartbeat fallback events, and
offline-publisher fallback events, and a reader written against
any one shape misreads the others (the hub's own `recent` CLI
prints heartbeat events with type `?`). This is the fact E-061's
contract must settle; docket 93.

## 9. Where the elder documents and the code differ

- `VERDANDI_MAP.md` maps `~/.hermes/state/` as if it were the
  member's own layout (its §1 line counts still match the four
  top-level files closely: 840/619/142/345 claimed vs
  847/619/142/345 in tree). It is a map of the *deployment*, and
  predates the heartbeat package's `paths.py` resolution entirely.
- The heartbeat core docstring says every pulse is "stored in
  Mímir (if available)" — the pulse path writes only its own
  SQLite DB; the Mimir *check* reads memory stores, nothing
  writes pulse data to them.
- `checks/base.py`'s severity docstring calls the order
  "OK < WARNING < CRITICAL < UNKNOWN" while its own comparator
  ranks UNKNOWN at −1 (below OK) and `worst_severity` ignores
  UNKNOWN unless alone — the comparator is the behaviour;
  E-060's concordance owns the wording verdict (docket 65's
  wording half already rides there).

## 10. Slice gate

- Focal suites re-run this slice (VM profile):
  default env **95 passed, 6 failed** — all 6 in
  `test_nervous_system.py::TestNerveHub`, all "async def functions
  are not natively supported" (pytest-asyncio absent); with the
  declared dev dependency supplied from the campaign's isolated
  target dir, the same four files run **101 passed, exit 0** —
  the 6 are ENVIRONMENT, proven, the same class as E-005's
  Verdandi family. Logs in `~/workspace/.verify-tmp/ember-e059/`.
- Root suite gate, identical to E-058's banked counts (doc-only
  slice): Run B **1054 passed, 6 failed, 25 skipped, 1 warning**
  (the 6 are the proven environment failures, same set);
  Run D **1111 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0. Logs in `~/workspace/.verify-tmp/ember-e059/gate/`.
- Doc-only slice: no code touched, no README touched. New docket
  items 93–98 (§8/§4/§5/§6/§7), each with its Part IV home.

*Filed by the E-059 slice, 2026-10-31. Next: E-060 — the VD-RM
concordance executed.*
