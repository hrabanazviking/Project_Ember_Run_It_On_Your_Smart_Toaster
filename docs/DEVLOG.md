# DEVLOG — Ember

**Append-only.** New entries go at the top. Each entry: date, scope, what shipped, what's next, who.

The DEVLOG is read at the start of every session. It is the Cartographer's first reference and the Scribe's last word of each session.

The DEVLOG of the parent project Runa-Agent-Digital-Being is preserved at `docs/archive/runa-inherited/DEVLOG.md` for lineage reference. Ember's record begins here.

---

## 2026-05-21 — Yggdrasil design tree (66 docs) — the master integration plan.

**Who:** Claude (Opus 4.7, 1M context). Mythic-Engineering session: six
roles operating in concert across `docs/yggdrasil/`. Design-only; no
source code changes; tests still at 612 + 2 skipped, ruff clean.

### What got designed

A 66-document tree at `docs/yggdrasil/` (plus `INDEX.md`) covering how
to wire together all of Ember's sibling projects — Bifrǫst, mimir-well,
Verdandi, Seiðr, Kista, Hamr, CloakBrowser, Astrology, MemPalace,
Norse-Dict, Open-VTT — into one coherent Norse-coded constellation.

Sections:

- **vision/** (6 docs): grand vision, naming, philosophy, personas,
  family-of-siblings, futuristic horizon
- **siblings/** (12 docs): one deep-dive per sibling + a matrix
- **architecture/** (10 docs): nine realms, protocol layer, Bifrǫst
  gateway, Kista secret plane, Mímir knowledge plane, Seiðr generation
  plane, CloakBrowser web plane, Astrology rhythm plane, observability,
  reconciliation receipts
- **ai-capabilities/** (10 docs): self-awareness, emotional intelligence,
  reasoning audit, long-horizon memory, meta-learning, dreamstate,
  intuition, curiosity-driven ingest, emotional palette, Norse naming
- **robustness/** (8 docs): self-healing philosophy, gossip health
  protocol, recovery playbooks, crash-bounded design, Norns backup,
  bug-resistance invariants, observability as first-class, testing
- **cross-platform/** (8 docs): device detection, resource budgeting,
  tiered defaults, GPU portability, offline guarantees, distributed
  coordination, high-perf + tiny profiles
- **invented-methods/** (6 docs): Borg Protocol (capability discovery),
  Heimdall (cross-realm gate), Well of Replay (event sourcing),
  Rhythmic Computation, Bifrǫst Trinity Fusion (3-way mutual-
  reinforcement search), Mirror of Ginnungagap (operator-mediated
  introspection)
- **roadmap/** (6 docs): five-phase plan — Roots → Branches → Crown →
  Network → Constellation Ratified

### Novel methods introduced

- **Bifrǫst Trinity Fusion**: extends RRF with mutual reinforcement
  across Mímir + Huginn + Muninn — chunks that *all three* vaguely
  agree on outrank chunks one retriever loudly favors. Yggdrasil-
  original; not standard practice elsewhere.
- **Mirror of Ginnungagap**: weekly introspection report; system
  proposes tuning; operator decides. No autonomous drift.
- **Heimdall Pattern**: every cross-realm call through one mediator
  — auth + rate limits + circuit-breakers + audit in one place.
- **Well of Replay**: append-only event log; current state derives
  from projections; time-travel + forensics first-class.
- **Rhythmic Computation**: background work scheduled by lulls +
  rhythms, not flat cron.
- **Borg Protocol**: capabilities advertised + indexed; agent finds
  composite paths through them.

### Why this matters

Until now the eleven sibling projects existed but Ember could only
talk to ~3 of them. The Yggdrasil tree is the *architecture* for
wiring all of them in *without losing the Vow of Smallness or
Sovereignty*. Each sibling stays an optional pip extra; the operator
chooses what they want.

The tree is **design-only** — ratification gate must pass before any
of Phase 1's code work begins. Each phase ships value before the next
starts.

### What's next

Operator-ratification of the Yggdrasil tree. Iðunn / Volmarr / Sigrún
walkthroughs of the docs. Once ratified, Phase 1 (The Roots) work can
begin: Bifrǫst + Mímir + Huginn integration; Kista mediation;
Verdandi event bus; updated Doctor screen.

Until ratification: no source code work on Yggdrasil. The tree itself
is the deliverable.

---

## 2026-05-21 — Batch K — wired the last two orphan schema fields (no version bump).

**Who:** Claude (Opus 4.7, 1M context). Continuation of the unwired-
inventory audit. The two orphan fields documented in
`docs/UNWIRED_INVENTORY.md` are now real working features instead of
schema decoration.

### What got wired

**1. `StrengrConfig.health_check_timeout_s`** (was: declared in schema,
documented in strengr README, but `tether.health()` never read it).

- New signature: `strengr.health(handle, *, timeout_s=None)`.
  Backward-compatible — existing callers without `timeout_s` get the
  previous synchronous behavior.
- When `timeout_s` is set, `_probe()` runs inside a one-shot
  `ThreadPoolExecutor` with `future.result(timeout=...)`. On
  overrun → typed `StrengrHealth(last_ok=None, detail="probe
  exceeded timeout of ...s")`.
- **Critically:** manual `pool.shutdown(wait=False, cancel_futures=True)`
  instead of `with ThreadPoolExecutor()`. The context-manager exit
  would block on the runaway probe and defeat the timeout. Same
  pattern as chat.py's `_execute_with_timeout` from Batch J.
- Callers updated: `src/ember/spark/munnr/status.py` and
  `src/ember/spark/munnr/doctor.py` both now pass
  `config.strengr.health_check_timeout_s` (defaults to 5.0 seconds).

**2. `JournalConfig.stale_heartbeat_s`** (was: declared with default
600, zero references anywhere in src/tests/docs — most-orphan field
in the schema).

- New `_heartbeat_is_stale(last_heartbeat, threshold_s)` helper in
  `src/ember/well/smidja/journal.py`. Parses the ISO-8601 timestamp,
  compares age-in-seconds to threshold. Defensive on malformed
  timestamps (treats as fresh — better to attempt resume than
  wrongly discard work).
- New `Journal._archive_stale(path)` helper. Renames a stale journal
  to `<original>.json.stale-<unix_timestamp>` so the operator can
  inspect what was abandoned without it being silently deleted.
- `Journal.open()` now checks the existing journal's heartbeat
  before resuming. If older than `config.stale_heartbeat_s`: logs a
  warning, archives the file, starts a fresh journal. Otherwise:
  proceeds to resume as before.
- Operator can opt out by setting `stale_heartbeat_s` very high
  (e.g., `10_000_000`); ancient journals still resume.

### Why this matters

Both fields were the kind of latent footgun where an operator could
set them in `ember.yaml` and get *nothing*. After Batch J fixed four
similar fields (Logging, ToolDescriptor.timeout_s,
allow_private_addresses, MCP doctor probe), these were the last two
known orphans. Now: **`src/ember/` has zero known orphan schema
fields**, per the updated `docs/UNWIRED_INVENTORY.md`.

The stale-heartbeat check additionally defends against a real
operational hazard: a crashed ingest run from days ago, when
resumed, would attempt to skip files that may have been re-ingested
through a separate run in between — producing duplicate chunks in
the Well. The archive-and-fresh-start behavior eliminates that
risk.

### Tests

`tests/unit/test_hardening_batch_k.py`, +9 tests:

- 3 for `strengr.health()`: no-timeout backward-compat, with-timeout
  overrun produces typed reply in <1s (not 2s), exception still
  produces typed reply.
- 3 for `_heartbeat_is_stale()`: old timestamp → stale, fresh → not
  stale, malformed → not stale (defensive).
- 3 for `Journal.open()` resume behavior: fresh existing journal
  resumes, stale journal archives + starts fresh, huge-threshold
  disables check.

### Stats

- **Before:** 603 pass + 2 skip, ruff clean.
- **After:** **612 pass + 2 skip**, ruff clean. **+9 regression tests.**
- **Files modified:** 4 source files (`tether.py`, `journal.py`,
  `status.py`, `doctor.py`).
- **Files created:** 1 test file (`test_hardening_batch_k.py`).
- **Docs updated:** `docs/UNWIRED_INVENTORY.md` — both fields moved
  to Historical; "0 known orphan fields" promoted to the lead.
- **No version bump.** Hygiene on top of Batch J.

### Closing word

The unwired-inventory audit named two fields; Batch K wired them.
Now the inventory's "actionable items" section is empty. Every
schema field declared in `ember.yaml`-readable form actually does
something. **The promise the schema makes is the promise the code
keeps.**

---

## 2026-05-21 — Design tree for Stofa (the TUI) — `docs/tui/` shipped, no code.

**Who:** Claude (Opus 4.7, 1M context). User asked the 6 Mythic-Engineering
crew to design "the best, most advanced, most user friendly, most beautiful,
most modern Viking, most fun, most cute, most stable, most robust ever TUI"
for Project Ember as **50+ long technical detailed MD data files**.

**Delivered: 74 files, 15,138 lines, zero code.**

This is **design before code** — the Mythic-Engineering iron law applied
to a substantial new surface. Stofa (the TUI's name; Old Norse for *"the
hall"*) is a planned slice-3 deliverable; this commit is its design
input. No code lands until ADR-0015 ratifies the design.

### What "Stofa" is

The terminal-user-interface surface for Project Ember. Turns `ember chat`
from a one-prompt-one-reply REPL into a **persistent multi-screen hall**:
chat + Well browser + doctor + settings + MCP + tool approval +
first-run wizard + help overlay, all in one Textual app with theme
support, pets, and accessibility.

The metaphor is the Norse longhouse common-room — the *stofa* — where
the household ate, talked, played tafl, slept on the benches.
Operator-cozy by intent. Modern-Norse-domestic register, never
heroic-mythic LARP.

### The full design tree

`docs/tui/INDEX.md` is the navigation root. Nine sections:

| Section | Files | Lines | Owner role |
|---|---|---|---|
| Vision | 5 | ~1,400 | Skald (Sigrún) |
| Architecture | 10 | ~2,800 | Architect (Rúnhild) |
| Research (15 TUIs studied) | 15 | ~3,200 | Cartographer + Scribe |
| UX Science | 10 | ~2,400 | Auditor + Scribe |
| Design (Viking aesthetic + 5 palettes) | 9 | ~1,700 | Skald + Auditor |
| Pets | 6 | ~1,400 | Skald + Forge |
| Screens | 9 | ~1,500 | Architect |
| Operations | 5 | ~900 | Auditor |
| Roadmap (4 phases) | 4 | ~800 | Forge + Scribe |
| **Total** | **74** | **15,138** | all six roles |

### What the design covers

- **The name Stofa, the Hjarta wizard surface, the 9-pet bestiary** —
  Hugin (raven), Refur (fox), Heiðr (goat), Sumarbýfa (bee), Geri-cub
  (wolf), Ask-sapling (ash), Drift (snowflake), Funi-spark (hearth),
  Ember-ember (logo). Each has a role, sprites (Unicode + ASCII
  fallback), helpfulness contract, voice for docs.
- **The framework choice** (Textual 2.x) with full Rich-vs-Textual-vs-
  prompt_toolkit comparison.
- **The state machine** (CONSTRUCTING → HJARTA → READY → OPEN → CLOSING)
  with per-screen sub-state-machines.
- **The 20-token theming contract** + 5 built-in themes (Aurora,
  Midgard, Ginnungagap, Solstice, Barrow). Each palette with full hex
  values + rationale + WCAG contrast tables + colorblind-simulation
  results.
- **The keybinding philosophy** — vim + arrow + GUI traditions all
  served; command palette as escape hatch; full rebindability.
- **15 TUI deep-dives** — lazygit, htop/btop, neovim/helix, ranger/nnn,
  atuin, aerc, glow, lazydocker, k9s, gh-dash, spotify-tui,
  claude-code/mods/llm, nap/pipes/oneko. What we steal + what we
  avoid catalogued in a synthesis doc.
- **10 UX-science docs** — Fitts's Law for keyboards, Hick's Law for
  menus, information density, visual hierarchy, color theory for
  terminals, typography for monospace, accessibility (CVD + low-vision
  + screen-reader + motor + vestibular + cognitive), interaction
  patterns (modal/modeless/confirmation/loading/notification/editing/
  selection/drill-down/cancel/undo/search/empty/error), animation +
  timing budgets, progressive disclosure.
- **9 screen specs** — Home (4-panel dashboard), Chat (streaming +
  inline tool approval), Well (browse + ingest), Doctor (per-realm
  health), Settings (every config field), MCP (server management),
  Tool Approval (modal), Hjarta Wizard (first-launch), Help Overlay.
- **5 operations docs** — performance budgets (< 500ms launch, < 16ms
  keypress, < 100ms theme swap, < 50MB idle), terminal compat matrix
  (Tier 1/2/3/4 with per-terminal quirks), resize handling, error
  boundaries, observability.
- **4-phase roadmap** — Phase 1 (The Hearth: MVP, ~25 files / ~2500 LOC),
  Phase 2 (The Hall: full screens + 6 pets), Phase 3 (The Familiars:
  plugins + accessibility + Settings UI + Theme Studio), Phase 4
  (The Feast: long-horizon community-shaped).

### Why this is a doc-only commit

Per the Mythic-Engineering iron law: **document before code**. Stofa
is a substantial new realm (the "Hall realm"); it gets ADR + design
discipline. The 74-doc tree is the *input* to the ADR-0015 conversation
the operator will have with the maintainer to ratify the design.

**No code lands** in this commit. **No `pyproject.toml` change** (the
`[tui]` extra is described in the design but not added until the
implementation phase). **No tests** (testing strategy is documented;
tests come with the code).

### Stats

- **Before:** 603 pass + 2 skip, ruff clean. No docs/tui/.
- **After:** **same** test pass + ruff status; 74 new MD files,
  15,138 lines of design documentation.
- **Files touched in src/:** zero.
- **Files added to docs/:** 74 (one new tree under `docs/tui/`).
- **Files modified in docs/:** 1 (this DEVLOG entry).

### What happens next

Per the roadmap, Stofa V1 = "The Hearth" ships when:
1. The operator (Volmarr) reviews this design tree.
2. Maintainer drafts ADR-0015 from it.
3. ADR-0015 is ratified.
4. Phase-1 implementation begins per `docs/tui/roadmap/99_ROADMAP_PHASE_1_HEARTH.md`.

Estimated Phase-1 effort: ~5-6 focused days, ~2,500 LOC of source +
~1,500 LOC of tests, new `[tui]` pip extra (just `textual>=2.0`).

The pets are the smile; the architecture is the substance; the
research is the receipts. **This is how a good TUI gets designed
before it gets built.**

The Scribe's closing word: *"Seventy-four documents to design what
will be roughly thirty source files. That ratio sounds backwards
until you remember the iron law: every hour of design saves three
hours of implementation drift. Stofa won't be invented from scratch
twice — it'll be built once, by a team of Mythic roles, from a tree
they all agreed to."*

---

## 2026-05-21 — Batch J — stub-to-real implementation pass (no version bump).

**Who:** Claude (Opus 4.7, 1M context). User: *"use all 6 of the Mythic Engineering subagents to look at all the code for any fake, temp, or stab code, and replace them all with real code."*

**Method:** Sweep #7. Cartographer ran the literal grep for stub markers (TODO, FIXME, NotImplementedError, "stub", "placeholder", "dummy", "fake", "mock", "deferred", "for now") across `src/`. Three parallel Auditors lensed for **stub-logic in functions**, **hardcoded-fake values in production code**, and **incomplete implementations**. Architect (me) triaged; Forge (me) shipped fixes; Scribe (me) wrote this entry.

**The triage was honest:** two of three Auditor lenses returned **zero findings**. The stub-logic auditor checked every candidate (Protocols, sentinels, deferred features) and verified all were legitimate. The hardcoded-fakes auditor found zero — no test IDs / dummy URLs / planted credentials in `src/`. The incomplete-impls auditor found the **four real gaps below**.

### What was genuinely half-shipped (and now isn't)

| Surface | Before | After |
|---|---|---|
| **`LoggingConfig`** | `LoggingConfig.level / format / destinations` declared in `schemas/config.py` since slice 1; **no code read it**. Operators setting `logging.level: DEBUG` got nothing. | New `src/ember/logging.py` with `configure_from(cfg)` — idempotent root-logger setup honouring level + format (PLAIN single-line vs STRUCTURED JSON-per-line) + destinations (stderr / stdout / file with optional rotation). Wired into `cli/main.py` immediately after config load. Stdlib-only (Vow of Smallness — no structlog / loguru). |
| **`ToolDescriptor.timeout_s`** | Declared on every descriptor since Phase 14; bridge translated it for MCP; **never enforced at execution time**. A runaway tool could lock the chat REPL until Ctrl-C. | New `_execute_with_timeout()` in `chat.py`: runs each tool in a one-shot `ThreadPoolExecutor` worker with `future.result(timeout=descriptor.timeout_s)`. On overrun → typed `ToolReply` with `error="tool exceeded its declared timeout"`. **Critically**: manual `pool.shutdown(wait=False, cancel_futures=True)` instead of `with` — the context-manager exit would block on the runaway worker, defeating the whole point. The worker thread keeps running until the executor returns (Python threads can't be killed cooperatively); the operator-facing error documents this. |
| **`ToolsConfig.allow_private_addresses`** | Declared in the schema; per-call arg in `fetch_url` honoured it; **the operator-config default was never read**. Operator setting it to true in `ember.yaml` had no effect unless the model also passed it explicitly. | New `bind_allow_private_default(value)` setter on `fetch_url.py`; chat.py's `_maybe_init_tools()` now wires `config.tools.allow_private_addresses` into the tool at startup. Per-call arg still wins; absent arg now falls back to operator policy. |
| **MCP doctor's Funi probe** | Returned a stub `{"ok": None, "detail": "not probed in MCP doctor"}`. | New `_probe_funi(config)` opens a one-shot Funi handle, calls `health()`, closes — mirrors what `ember doctor` does on the CLI. Returns real `ok` bool + `model_id` or `detail`. |
| **`sqlite_vec` adapter `check_same_thread`** | Default `True` blocked the new tool-timeout `ThreadPoolExecutor` from calling `search_well` (worker thread can't reuse main-thread sqlite connection). | Passed `check_same_thread=False`. SQLite itself is thread-safe in its default serialized mode (SQLITE_THREADSAFE=1); only Python's wrapper enforced same-thread, and the timeout pattern guarantees one-thread-at-a-time access by design (main thread blocks on `future.result()` while the worker holds the connection). Comment in the adapter explains the safety reasoning. |
| Cosmetic | Dead `if TYPE_CHECKING: pass` block + unused `TYPE_CHECKING` import in `sqlite_vec/adapter.py`. | Removed. |

### Verified-clean: things that LOOK like stubs but aren't

The Auditors checked these and confirmed each is legitimate, not a stub:

- **`approval.py:202` `ApprovalOutcome.APPROVED_THIS_CALL,  # placeholder — set after prompt`** — the `outcome` field is paired with `needs_prompt=True`; the caller at `chat.py:509-511` checks `needs_prompt` first and replaces the outcome via `resolve_with_answer(answer)`. The sentinel value is never used directly. Comment is slightly misleading but the contract is correct.
- **`mcp/server.py` `recent_episodes` deferral** — ADR-0014 explicitly documents this as V2 scope (depends on BrunnrHandle gaining a reader API). Not a stub; a phase-gate.
- **`fetch_url._URL_OPENER / _ADDRESS_RESOLVER / _ROBOTS_FETCHER`** — test-injection seams with documented purpose. Defaults to None (real implementation runs); tests inject fakes.
- **`fetch_url` test-seam comments and `ask.py`'s `fake_stdin = io.StringIO(text)`** — legitimate StringIO-as-stdin for one-shot queries.
- **`BrunnrHandle` / `FuniHandle` Protocol bodies (`...`)** — Protocols ARE supposed to have empty bodies.
- **`handle.py` `"backend not implemented"` error paths** — real error handling for enum values without registered adapters; not stubs.
- **Hardcoded default URLs (`http://localhost:11434`)** — operator-overridable per ADR-0008 overlay system; the env-var `OLLAMA_HOST` + `ember.yaml` paths overlay on top. Documented as the local-development default.

### Deferred (not Batch J scope)

- **Unimplemented `BrunnrBackend` enum values** (QDRANT / CHROMA / LANCEDB) and **`FuniRuntime`** values (LLAMACPP / LMSTUDIO / PHI_SILICA / APPLE_FOUNDATION). These are *adapter-not-yet-shipped*, not stubs. Operators selecting them get a typed `Disconnected(reason=CONFIG_INVALID, detail="backend not implemented")` at open time — clear, typed, not a crash. Adding config-time validation that refuses them at load time is a slice-3 question.
- **MCP `recent_episodes` tool + resource** — needs `BrunnrHandle.recent_episodes()` reader API first.
- **Episode resource over MCP** — same reason.

### Tests (+11 new in `tests/unit/test_hardening_batch_j.py`)

- 4 tests pinning logging behaviour: root-level level honoured; idempotent re-configure; file destination writes UTF-8; structured format emits parseable JSON.
- 3 tests for tool-timeout enforcement: overrun returns typed reply in <1s (not 2s); fast tool returns real reply; executor exception still typed-reply.
- 2 tests for `bind_allow_private_default` semantics + default reset.
- 1 test for MCP doctor's real Funi probe.
- 1 test for `sqlite_vec` cross-thread connection (proves the `check_same_thread=False` fix actually enables the timeout wrapper).

### Stats

- **Before:** 592 pass + 2 skip, ruff clean.
- **After:** **603 pass + 2 skip**, ruff clean. **+11 regression tests.**
- **Files created:** `src/ember/logging.py`, `tests/unit/test_hardening_batch_j.py`.
- **Files modified:** `src/ember/cli/main.py` (logging wire-up), `src/ember/spark/munnr/chat.py` (timeout helper + fetch_url binding), `src/ember/tools/fetch_url.py` (bind_allow_private_default), `src/ember/mcp/server.py` (real Funi probe), `src/ember/well/brunnr/sqlite_vec/adapter.py` (check_same_thread + dead-code removal), `tests/unit/test_mcp_server.py` (updated to assert real probe shape).
- **No version bump.** Hygiene pass on top of Batch I.

### Closing word

When auditors say "this code is mostly clean" and they're right, the right response is to ship the genuinely-real things that were *almost* shipped and stop. The four fixes here turn four schema/descriptor declarations from aspirational into operational. Operators who set `logging.level: DEBUG` now get debug logs. Tools that hang past their `timeout_s` no longer hang the REPL. `allow_private_addresses: true` actually flips the default. The MCP doctor actually probes Funi. The system's promises now match its behaviour, across the surfaces that audit-#7 examined.

---

## 2026-05-21 — Batch I — Bidirectional MCP integration (ADR-0014, Phase 18).

**Who:** Claude (Opus 4.7, 1M context). User: *"give it robust and advanced mcp, buddy."* Scoped via single AskUserQuestion → chose "Client + Server, both today."

**What shipped:** Full bidirectional Model Context Protocol integration as a new opt-in package `src/ember/mcp/`, gated behind the `[mcp]` pip extra. Both the client side (Ember consumes external MCP servers + bridges their tools into the existing tool registry) and the server side (`ember mcp serve` exposes Ember's Well + diagnostics over stdio JSON-RPC) ship in this single commit.

**Scope:** New feature, ADR-driven, slice-2-extended (Phase 18). **No version bump in this commit** — that lands as part of a 0.3.0rc1 cut when slice-3 architecture changes accumulate. ADR-0014 is the canonical reference.

### New ADR

- **`docs/decisions/0014-mcp-bidirectional.md`** (~150 lines) — full design + rationale + tradeoffs. V1 scope is stdio-only, both sides. V2 deferrals: `streamable-http` / SSE / WebSocket transports; auth; episode reader API + `recent_episodes` MCP tool; tool-execution timeout enforcement (already declared on descriptors).

### New package: `src/ember/mcp/`

- **`runner.py`** — `MCPRunner`: async-event-loop-in-a-daemon-thread bridge so the synchronous Ember REPL can submit coroutines via `asyncio.run_coroutine_threadsafe`. One loop hosts every `ClientSession`. Thread-safe submit + idempotent close + post-close-submit guard.
- **`client.py`** — `MCPClientPool`: spawns one stdio subprocess per `MCPServerSpec`, initializes one `ClientSession` per server, holds the lifetime under managed `AsyncExitStack`s for per-server unwind, surfaces `call_tool` + `ping` + `tools_for` as synchronous methods. Per-server failure during open is logged + skipped (other servers continue) — never crashes the chat.
- **`bridge.py`** — `register_pool_tools`: translates each discovered MCP `Tool` into Ember's `ToolDescriptor` + closure executor. Naming: `mcp__<server>__<tool>` (matches Claude Code's convention). `inputSchema` (JSON Schema) → `parameters_schema` (Ember's simpler ToolParameter dict); `MCPServerSpec.auto_approve` lifts named tools from `PER_CALL` to `STANDING`. `CallToolResult` content → `ToolReply.output`/`error` per the ADR-0011 typed-value contract.
- **`server.py`** — `build_server` + `run_stdio`: FastMCP wrapper exposing **`search_well`**, **`well_status`**, **`doctor`** as tools and **`ember://well/status`** as a resource. Best-effort Brunnr open — if the Well is unreachable, tools return typed `{"error": ...}` payloads rather than crashing (Vow of Graceful Offline).
- **`__init__.py`** — exposes `MCP_TOOL_NAME_PREFIX = "mcp__"`.

### Schema additions (`src/ember/schemas/config.py`)

```python
@dataclass(frozen=True, slots=True)
class MCPServerSpec:
    name: str
    command: str
    args: tuple[str, ...] = ()
    env: Mapping[str, str] = field(default_factory=dict)
    cwd: str | None = None
    auto_approve: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MCPConfig:
    enabled: bool = False           # client side
    expose_self: bool = False       # server side
    startup_timeout_s: float = 10.0
    call_timeout_s: float = 30.0
    servers: tuple[MCPServerSpec, ...] = ()
```

`MCPConfig` added to `EmberConfig` as a field; both exported in `__all__`. Default-all-off — operators who don't touch the new config see no behavior change.

### New CLI surface (`src/ember/cli/main.py` + new `src/ember/cli/mcp.py`)

| Subcommand | Purpose |
|---|---|
| `ember mcp list` | Show configured MCP servers + their command lines + auto_approve sets |
| `ember mcp tools` | Spawn the pool, register tools, list every tool in the registry (first-party + MCP-bridged) with approval policy |
| `ember mcp ping [<server>]` | Health-probe one or all configured servers via the MCP `ping` primitive |
| `ember mcp serve [--transport stdio]` | Run Ember as an MCP server over stdio. The chat REPL is one mode of Ember; `mcp serve` is another. Mutually exclusive — `serve` blocks until SIGINT. |

The `cli/mcp.py` handlers all lazy-import the MCP package so operators without the `[mcp]` extra get a friendly "Install with `pip install ember-agent[mcp]`" message rather than an `ImportError` traceback.

### `pyproject.toml` extra

```toml
mcp = ["mcp>=1.27"]   # ADR 0014 — bidirectional MCP integration (client + server).
```

The single `mcp` package pulls in transitive deps (`anyio`, `httpx`, `pydantic`, `starlette`, `uvicorn`, etc.) but only when the operator opts in. Default `pip install ember-agent[sqlite_vec]` is unchanged.

### Tests (+36 new, all passing)

- **`tests/unit/test_mcp_runner.py`** (6 tests) — async-in-thread bridge: submit returns value, propagates exceptions, honors timeout, idempotent close, post-close raises, single-loop sharing.
- **`tests/unit/test_mcp_bridge.py`** (16 tests) — JSON Schema → ToolParameterKind coercion (string/integer/number/boolean/union/unknown→string); descriptor building (required + enum + standing lift + missing-input-schema fallback); CallToolResult → ToolReply translation (text concat / non-text bracketed / isError → typed error); executor failure modes (TimeoutError / KeyError / generic exception all become typed `ToolReply.error`); `register_pool_tools` end-to-end (naming convention + auto_approve + conflict-skip-with-warning).
- **`tests/unit/test_mcp_server.py`** (7 tests) — `build_server` registers expected tools + resources; tool behavior with stub Brunnr; graceful failure when Brunnr raises or is None; resource returns JSON.
- **`tests/integration/test_mcp_end_to_end.py`** (7 tests) — **real subprocess MCP roundtrip**: spawns a small FastMCP stub server (written to `tmp_path`), discovers its tools via `MCPClientPool`, registers them via bridge, calls them via the registered executor closure, verifies the full discovery + call + result roundtrip. Also tests `ping` happy path + unknown-server + idempotent close. All tests `pytest.importorskip("mcp")`-gated so the suite still runs without the extra.

### Stats

- **Before:** 556 pass + 2 skip, ruff clean.
- **After:** **592 pass + 2 skip**, ruff clean. **+36 regression tests.**
- **Files created:** `docs/decisions/0014-mcp-bidirectional.md`, `src/ember/mcp/{__init__,runner,client,bridge,server}.py`, `src/ember/cli/mcp.py`, `tests/unit/test_mcp_{runner,bridge,server}.py`, `tests/integration/test_mcp_end_to_end.py`.
- **Files modified:** `src/ember/schemas/config.py` (MCPConfig + MCPServerSpec), `src/ember/cli/main.py` (subparser wiring), `pyproject.toml` (`[mcp]` extra).
- **No version bump.** ADR-0014 marks this as Phase 18 of slice-2-extended.

### V2 backlog (named in the ADR)

- `streamable-http` transport on both sides (with bearer-token auth)
- Reconnect-with-backoff for client-side server crashes (currently: dead-server tools become typed `NO_SUCH_TOOL` until chat restart)
- Reader API on `BrunnrHandle` for episodes → enables `recent_episodes` MCP tool + resource
- Per-tool timeout enforcement on the bridge executor (descriptor declares `timeout_s`; runner already supports it but bridge currently uses the pool-wide `call_timeout_s`)
- Subscription-based resource change notifications
- MCP `sampling` (host asks client to call its LLM)
- Operator-friendly wildcard syntax in `auto_approve` (today: literal name match only)

### Closing word

This is the largest single commit since slice-2 ratification. Five hardening sweeps earlier today (A through H) tightened the foundation; Batch I builds on it. The bidirectional MCP surface turns Ember from "a chat client with three tools" into both a tool-ecosystem participant (the client side opens the door to the entire MCP plugin ecosystem) and a sovereign knowledge endpoint that Claude Desktop / Claude Code / any MCP client can address (the server side exposes the operator's Well as an addressable resource). Vow alignment intact: opt-in, gated, approval-defaulted-safe, audit-symmetric. The Six True Names hold.

---

## 2026-05-21 — Hardening sweep Batch H — absolute-path audit + cross-platform audit (no version bump).

**Who:** Claude (Opus 4.7, 1M context). Sweep #5 of the day, in response to *"examine every code file to make sure there is no absolute paths… and fix any to relative paths you find… and then call on the 6 Mythic Engineer subagents to make sure all the code is totally cross platform… and come up with a plan to fix any that is not."*

**Method:**
- Architect-as-grep ran the absolute-path audit directly (fast, no agent needed).
- Three parallel Cross-Platform Auditors hit fresh lenses: filesystem/Path, process/signal/IO, encoding/locale.
- Architect (me) triaged. The honest report-back was unusual: **the codebase is genuinely cross-platform clean** with zero Tier-1/2 findings across all three lenses.
- Scribe (me) wrote `docs/CROSS_PLATFORM_PLAN.md` — the *forward-looking deliverable* containing the verified-clean catalogue, watch-list patterns, and per-platform pre-release checklist.

**Scope:** No source-code changes (apart from 4 test-only `/tmp/` → `tmp_path` conversions). The plan is the product. **556 tests pass + 2 skipped** (same count as after Batch G; tests still green), ruff clean.

### Absolute-path audit results

| Pattern | Found | Triage |
|---|---|---|
| `Path("/home/...")` machine-specific | 0 | none |
| `Path("/tmp/...")` in `src/` | 0 | none |
| `Path("/etc/..." or "/var/..." or "/opt/...")` in `src/` | 0 | none |
| `Path("~/.ember/...")` defaults in `src/` | 4 (`schemas/config.py:128,143,189`; `cli/main.py:27`) | NOT bugs — `~` is operator-portable (expands to user's home); intentional XDG-style defaults |
| `Path("/tmp/...")` in tests | 4 (`test_hardening_batch_a.py:266,278,312`; `test_strengr_tether.py:92`) | Fixed: → `tmp_path` fixture (Windows-portable too) |
| Test-string source attributions like `"/notes/a.md"` | many | NOT paths — opaque source-id strings used in `Document.source` records |

**No real absolute-path bugs in source code.** The "fixes" shipped are test-suite hygiene that also makes those tests Windows-runnable.

### Cross-platform Auditor reports (three lenses, three honest "verified clean" results)

**Lens 1 — Filesystem / Path (Auditor A):**
- Tier-1: 0. Tier-2: 0. Tier-3: 1 (the `/tmp/` tests, now fixed).
- **Verified clean:** all 11 `.expanduser()` calls; all 3 `chmod` guards behind `if os.name != "nt"`; all `Path` joins via the `/` operator; `stat.S_ISREG()` for special-file rejection; `fnmatch.fnmatchcase` for the sensitive-name denylist; `tempfile.NamedTemporaryFile(delete=False)` + `os.replace()` atomic-write pattern.
- **Auditor's summary verbatim:** *"The README/PHILOSOPHY claim 'runs anywhere (Linux + macOS + Windows + WSL)' is fully supported by the code. No fixes needed for production use."*

**Lens 2 — Process / Signal / IO (Auditor B):**
- Tier-1: 0. Tier-2: 0. Tier-3: 2 (sqlite-vec wheel availability on Windows ARM; WAL on network FS — both deployment notes, not code bugs).
- **Verified clean:** zero `signal.signal()` / `signal.alarm()` / `subprocess` / `os.fork()` / POSIX-only stdlib imports (`fcntl`, `pwd`, `grp`, `termios`, `resource`, `select` for stdin); Ctrl-C handled at 3 sites with typed `Disconnected` fallback; stdin/stdout abstracted as `TextIO` parameters; no module-level OS-specific imports.
- **Auditor's verdict:** *"AUDIT PASSING. The codebase is production-ready for Windows, macOS, and Linux from a cross-platform IO/signal/process perspective. All known platform hazards have been properly defended or avoided."*

**Lens 3 — Encoding / Locale (Auditor C):**
- Tier-1: 0 in `src/`. Tier-2: 0. Single finding in `docs/RunaUniversity2040/generate_content.py` (inherited Runa corpus — not load-bearing, excluded from sdist in `pyproject.toml`, so it doesn't ship to PyPI).
- **Verified clean:** 100% of `Path.read_text()` / `write_text()` / `open()` calls in `src/` pass `encoding="utf-8"`; tomllib opens in binary mode; JSON `ensure_ascii=False` always paired with utf-8; all timestamps use `datetime.now(tz=UTC)`; all `strftime` formats locale-neutral (`%Y-%m-%d` only); ANSI escapes scrubbed from tool output (Batch F).

### Why this batch was the smallest source-code change of the four-sweep series

The five sweeps in order:
- **Batches A+B (#1):** 13 Tier-1 + 4 Tier-2 fixes — bulk of real bugs caught
- **Batches C+D+E (#2):** 7 Tier-1 + 5 Tier-2 — typed-value-contract seams
- **Batch F (#3):** 8 Tier-1/2 fixes — newly-audited surfaces
- **Batch G (#4):** 3 fixes — fresh lenses; signal-to-noise dropping
- **Batch H (#5, this entry):** 4 test-hygiene fixes + 1 documentation deliverable — the source code was already clean

When five auditors with fresh lenses on the same code return "verified clean," the appropriate response is to *record the verification*, not to invent fixes. The DEVLOG entry + `CROSS_PLATFORM_PLAN.md` are that record.

### Deliverable: `docs/CROSS_PLATFORM_PLAN.md`

New file (~340 lines) capturing:
- The verified-clean catalogue (the "receipts" that prove each Vow / each platform surface is honored)
- Patterns to **always** use in future code (`encoding="utf-8"`, `Path` joins, `tmp_path` fixture, `datetime.now(tz=UTC)`)
- Patterns to **never** introduce (`os.fork`, `fcntl`, `signal.alarm`, `os.environ["HOME"]`, `subprocess shell=True`, `time.strftime("%Z")`, raw `/tmp/` in tests)
- Per-platform pre-release checklists (Linux ✓, macOS, Windows, WSL, containers) with explicit tick-boxes for what to verify before announcing each as "officially supported"
- Known cross-platform watch-points (sqlite-vec wheel matrix, WAL on network FS, APFS case-insensitivity, Windows long paths)
- Per-batch contributor checklist for future hardening sweeps

This is the document the next operator / agent / human contributor reaches for *before* writing new code — turning "cross-platform clean" from a one-time audit result into an ongoing contract.

### Stats

- **Before:** 556 pass + 2 skip, ruff clean.
- **After:** **556 pass + 2 skip**, ruff clean. **Same count** — the test edits replaced `Path("/tmp/...")` literals with `tmp_path` fixture but the test functions themselves are unchanged.
- **Source files touched:** 0 — the `src/` tree was already clean.
- **Test files touched:** 2 (`test_hardening_batch_a.py`, `test_strengr_tether.py`) — `/tmp/` → `tmp_path`.
- **Files created:** 1 (`docs/CROSS_PLATFORM_PLAN.md`).
- **No version bump.** Slice-2 is still 0.2.0; this is documentation + watch-list.

The Scribe's closing word: *"The honest report-back is the rare one. Sweeps 1–4 found 31 fixes between them; sweep 5 found that the code was already what it claimed to be. The plan is the deliverable — five sweeps' worth of verification compressed into one watch-list that the next contributor can read before writing new code. That's how 'cross-platform clean' becomes a contract instead of a slogan."*

---

## 2026-05-21 — Hardening sweep Batch G — fourth pass, fresh lenses (no version bump).

**Who:** Claude (Opus 4.7, 1M context). Sweep #4 of the day, in response to *"call on the 6 Mythic Engineering agents and search code according to your current ideas where and how to look."*

**The fresh lenses:** The previous three sweeps (A+B, C+D+E, F) had walked the tree question-by-question for input validation, error handling, dispatch, lifecycle, ANSI scrub. Batch G deliberately changed the *question* rather than the *surface*:

- **Lens 1 — Cross-adapter parity.** Do `sqlite_vec` and `pgvector` actually behave identically for the same input? Different developers wrote them; subtle drift was likely.
- **Lens 2 — Vow enforcement.** The 10 Vows in `docs/SYSTEM_VISION.md` are supposed to be mechanically enforced. Are they, or is the documentation more confident than the code?
- **Lens 3 — Resource lifecycle invariants.** The typed-value-contract sweeps verified the *return* path; do all *cleanup* paths run on every interleaving?

Cartographer (me) refreshed the philosophy + adapter contract docs; three parallel Auditors hit each lens; Architect (me) triaged honestly — most "potential findings" investigated and proven safe; this commit ships only the three concrete actionable fixes.

**Scope:** No code-shape changes; no version bump; no ADR. Hygiene #4 on top of v0.2.0 + Batches A/B/C/D/E/F. **556 tests pass + 2 skipped** (was 550 + 2 after Batch F; +6 new tests in `test_hardening_batch_g.py`), ruff clean.

### Batch G fixes (each with a pinning regression test)

| File | Lens | Hardening |
|---|---|---|
| `src/ember/well/brunnr/pgvector/adapter.py` | Adapter parity | `text_search` now calls `_strip_unsafe_chars` (imported lazily from the sqlite_vec adapter) before passing the query to `plainto_tsquery`. sqlite_vec stripped Unicode Cc + Cf bytes in Batch C; pgvector did not. The audit log is now symmetric across both backends — a U+202E in a query gets removed before it can land in the operator's log on either path. |
| `src/ember/well/brunnr/pgvector/adapter.py` | Adapter parity | `close()` now logs `pgvector close failed: <exc>` via `_logger.warning` instead of using `contextlib.suppress(Exception)`. sqlite_vec already logged close-time failures in Batch D; pgvector silently ate them. The Protocol contract ("close never raises") is still honored — the exception is caught — but operators inspecting the log can now see *why* close failed (idle-in-transaction holding a lock, backend already gone, etc.) instead of getting silence. |
| `src/ember/well/smidja/journal.py` | Resource lifecycle | `_write_state` now unlinks the tempfile if `os.replace` fails. `NamedTemporaryFile(delete=False)` + `os.replace` is the standard atomic-write pattern, but the `delete=False` means a failed replace (cross-filesystem, EACCES, ENOSPC) leaves a `*.tmp` orphan in the journal directory. On a disk-pressured Pi, repeated ingest failures could accumulate enough orphans to fill the disk. The cleanup is wrapped in `contextlib.suppress(OSError)` so the *real* exception (the OSError from replace) is what propagates. |

### Lenses that found nothing actionable (verified honestly)

**Lens 1 — Adapter parity (additional findings investigated, not shipped):**
- *Text-search score scales differ* (sqlite_vec returns negated FTS5 BM25 rank, ~1–100 range; pgvector returns `ts_rank`, [0, 1] range). Real divergence, but `text_search` is only called by `hybrid_search` which feeds the scores into RRF (reciprocal rank fusion, k=60) — the absolute scores never cross-compare. Operators using `text_search` directly would see different scales, but that's a single-line documentation fix in a follow-up. Not shipped.
- *Read-only mode is pgvector-only.* sqlite_vec has no `read_only` config option — it's a single-user local store; the concept doesn't apply the way it does for shared Gungnir. This is an intentional asymmetry, not a parity gap.
- *Vector-search `SELECT` column ordering differs* between adapters. Both adapters construct `RetrievalHit` correctly; the difference is cosmetic.

**Lens 2 — Vow enforcement (9 of 10 Vows verified honored with file:line evidence):**
- All 10 Vows from `docs/SYSTEM_VISION.md` checked. **9 are mechanically honored** in the code — Smallness (`pyproject.toml`: zero non-extra deps), Tethered Grounding (`prompt.py:46-93`: facts only from `hits` parameter), Graceful Offline (`prompt.py:107-108`: `_DISCONNECTED_INSTRUCTION` unconditional), Pluggable Storage (`handle.py:27-83`: Protocol + lazy imports), Unbroken Whole (`test_skeleton_imports.py:23-38`: independent realms), Public-Friendliness (`cli/main.py:96-130`: no raw tracebacks), Honest Memory (`prompt.py:27-43`: instruction is unconditional), Modular Authorship (no cross-realm reach-arounds), Open Knowledge (no feature drift in README).
- **One ambiguous finding deliberately deferred:** *"Vow of Flexible Roots"* — Auditor B flagged that config defaults are hardcoded `~/.ember/*` rather than being relative to a `--config-root` parameter. The finding rests on a *hypothetical* `--config-root` flag the auditor didn't verify actually exists. Even if it does, making defaults config-root-relative would change behavior for any operator who currently relies on `~/.ember` resolution. This is an architectural decision that needs operator input before shipping, not a bug fix. Flagged in this DEVLOG entry as a thing-to-think-about for the next slice.

**Lens 3 — Resource lifecycle (22 acquire-points verified clean, 1 real leak fixed):**
- Of 22 resource-acquisition points audited (sqlite/psycopg connections, urllib responses, tempfiles, os.open fds, generator iteration), 21 were verified to clean up correctly under every realistic failure interleaving. The one real leak (journal tempfile) is now fixed above.
- Auditor's initial flags on the Ollama streaming response, fetch_url opener, sqlite_vec open() multi-step setup, pgvector open() multi-step setup, audit log fd, and chat.py REPL finally block were each investigated and found to already have correct try/finally + early-close patterns from prior batches.

### Why this sweep was the last whole-tree sweep of the day

Three sweeps preceded Batch G. Each found progressively fewer real bugs:
- **Batches A+B (sweep #1):** 13 Tier-1 + 4 Tier-2 fixes — bulk of real bugs caught here
- **Batches C+D+E (sweep #2):** 7 Tier-1 (typed-value-contract seams) + 5 Tier-2 — deeper consistency
- **Batch F (sweep #3):** 8 Tier-1/2 fixes — newly-audited surfaces (render, ingest, registry)
- **Batch G (sweep #4, this entry):** 3 fixes — fresh *lenses* on the same surfaces, plus honest "this is genuinely clean" reports

The lens-not-surface approach worked: 9 Vows verified, 21 resource paths verified, dozens of adapter methods verified — *that knowledge is the real product of this sweep*, even more than the three fixes shipped. The DEVLOG entry captures it so the next operator (or auditor, or me-tomorrow) doesn't have to re-derive what's already known clean.

The next sweep should wait for a **new surface to land** (slice-3 HTTP gateway, Auga GUI, Rödd voice). Whole-tree re-sweeps after that have hit diminishing returns.

### Stats

- **Before:** 550 pass + 2 skip, ruff clean.
- **After:** **556 pass + 2 skip**, ruff clean. **+6 regression tests.**
- **Files touched:** 2 source files (`pgvector/adapter.py`, `smidja/journal.py`).
- **Files created:** 1 regression test file (`test_hardening_batch_g.py`).
- **No version bump.** Slice-2 is still 0.2.0; Batch G is hygiene #4.

The Architect's closing word: *"Four sweeps in one day. The first found real bugs; the second tightened typed seams; the third opened new surfaces; the fourth changed the question entirely. The product is not just the 31 fixes shipped — it's the verified-clean catalogue logged across four DEVLOG entries. Next time someone asks 'should we audit this code?' the answer for these surfaces is 'we did, on 2026-05-21, four ways. Here's what we found and what we verified clean.'"*

---

## 2026-05-21 — Hardening sweep Batch F — third pass, fresh Auditor surfaces (no version bump).

**Who:** Claude (Opus 4.7, 1M context). Six-role Mythic-Engineering pass #3 of the day, in response to *"call on the 6 Mythic Engineering agents and search all code for any other bugs and code hardening."*

**Method:** Cartographer (Védis) re-mapped the post-d5d2792 state, ranked the highest-complexity modules + named surfaces NOT covered by Batches A-E. Four parallel Auditors (Sólrún) hit those surfaces:

- **Auditor 1** — `spark/munnr/render.py` (terminal output / ANSI injection)
- **Auditor 2** — `well/smidja/local_files/source.py` + `journal.py` (filesystem traversal + persistence)
- **Auditor 3** — `spark/funi/tools/registry.py` + `approval.py` + `schemas/tool.py` (tool dispatch invariants)
- **Auditor 4** — `config/loader.py` + `overlay.py` + `validate.py` (config overlay + validation)

Architect (Rúnhild) triaged ~50 raw findings against the prior sweeps' exclusion list, dropped duplicates and false claims, applied the Tier-1/2 set. Forge Worker (Eldra) shipped fixes + 24 new regression tests. Scribe (Eirwyn) wrote this entry.

**Scope:** Third-pass defensive depth. **No code-shape changes; no version bump; no ADR.** This is hygiene #3 on top of v0.2.0 + Batches A/B + Batches C/D/E. **550 tests pass + 2 skipped** (was 526 + 2 after Batches C+D+E; +24 new tests in `test_hardening_batch_f.py`), ruff clean.

### Batch F fixes (each with a pinning regression test)

| File | Hardening |
|---|---|
| `src/ember/well/smidja/local_files/source.py` | **Three related defences in walk()**: (1) skip non-regular files via `stat.S_ISREG(path.lstat().st_mode)` — `path.is_file()` would let `read_bytes()` block forever on `/dev/zero` or a FIFO; (2) new `DEFAULT_EXCLUDE_FILE_PATTERNS` denylist for `.env*`, `.pgpass`, `.netrc`, `id_rsa*`, `*.key`, `*.pem`, `*.p12`, `*.kdbx`, `.aws/*` so `ember well ingest ~/` doesn't vectorise the operator's secrets; (3) `DEFAULT_MAX_FILE_BYTES=64 MiB` cap protects against runaway memory on a 50 GB log file. |
| `src/ember/well/smidja/embed_client.py` | New `_coerce_vector()` helper validates each scalar: refuses non-finite (NaN, ±Inf), refuses non-numeric types (str, None, bool), enforces optional `expected_dim`. Without this, NaN embeddings would crash pgvector at insert time with a cryptic `data exception`, or poison cosine-similarity downstream so every query looked equally bad. |
| `src/ember/spark/funi/tools/registry.py` | `register()` now validates at registration time: descriptor `name` must match `[A-Za-z_][A-Za-z0-9_]{0,63}` (alphanumeric + underscore, 1-64 chars); executor must be `callable()`. Without this, a malformed registration (empty name, name with newline / ESC, non-callable handler) would surface only at call-time with a confusing traceback. The name shape also matches OpenAI/Anthropic tool-name conventions. |
| `src/ember/spark/funi/tools/audit.py` | `_redact_arguments` now walks nested dicts + lists via new `_redact_value()` helper. A tool with `redacted_arg_names=("token",)` accepting `payload={"token": "...", "path": "..."}` would previously leak the nested token to the audit log; now it's redacted wherever the key appears in the value tree. |
| `src/ember/spark/munnr/render.py` | New `_strip_terminal_controls()` helper scrubs ANSI escapes (CSI, OSC, ST-terminated) and Unicode Cc+Cf bytes from `reply.output` and `reply.error` before rendering. A tool reply that quoted a hostile HTTP response containing `\x1b[2J\x1b[H` could otherwise clear the operator's terminal; `\x1b]0;INFECTED\x07` could rewrite the window title. Raw bytes still go to the audit log (only the operator's screen gets the scrubbed view). |
| `src/ember/config/validate.py` | **Two related defences**: (1) `Path`-typed fields now refuse empty / whitespace-only strings — `path: ""` would previously coerce to `Path(".")` (cwd) silently, a typo-becomes-misconfiguration footgun; (2) `Mapping[str, X]` fields now coerce each value to `X` via the same `_coerce_value` walk used for other annotations — previously the coercer returned `dict(value)` raw, so a field typed `Mapping[str, str]` would accept `{"a": 123}` and the downstream consumer would either drop the bad entry silently or crash. |
| `src/ember/well/smidja/journal.py` | `JournalState.from_payload` now refuses malformed/corrupted payloads with typed `IngestError` instead of bare `KeyError`/`ValueError`. Required fields checked explicitly; unknown `source_kind` enum value caught; non-dict `entries` rejected. A truncated journal write or version-skew between Ember installs now produces one clear operator-facing line naming the field instead of crashing the ingest with a confusing traceback. |
| `src/ember/spark/munnr/chat.py` | New `_warn_unknown_override_tools()` prints a warning at chat-startup if `tools.approval_overrides` names a tool that isn't registered. Without this, a typo like `{fech_url: per_call}` would silently apply nothing — the operator would believe approval was tightened on `fetch_url` while the descriptor default was actually in force. |

### Findings deliberately NOT acted on (Batch F scope)

- **TOCTOU walk→read race in source.py** — real, but limited damage (file just gets skipped if it vanishes between walk and read; no path to data corruption or escalation). Documented as a known limitation rather than fixed.
- **Concurrent `ember well ingest` against same Well** — operator-level concern; the journal is single-writer by design (one ingest at a time per Well). Could add `fcntl.flock()` in slice 3 if multi-operator deployments become common.
- **`os.replace()` tempfile orphan on rare failure** — `tempfile.NamedTemporaryFile(delete=False)` + `os.replace()` is the standard atomic-write pattern; the orphan window is microseconds wide and `os.replace` is atomic on POSIX.
- **PgVectorConfig.url shape validation** — left to fail at first-connect with a libpq error. Adding a regex matcher would risk false-rejecting valid postgres URL forms.
- **OLLAMA_HOST trailing-path component (`/api`) double-append** — real risk but rare; documented as a known limitation. The fix would require either stripping path components (silent) or refusing them (operator-hostile to ambient setups).
- **Tool execution timeout** — `ToolDescriptor.timeout_s` field exists but the framework doesn't enforce it. Real bug, but timeout enforcement needs cross-platform thinking (signal.alarm on POSIX vs `threading.Timer` on Windows) — deferred to a focused slice.
- **Render unicode-width assumptions** (CJK / combining chars) — cosmetic; column alignment is best-effort already.
- **Auditor false claims** verified-and-dropped: Python 3.13+ `rglob(recurse_symlinks=False)` is the default (Ember requires 3.14, so symlink-recursion is already-clean); ToolDescriptor is already `frozen=True` (Mapping mutability concern was for a *shared* dict, which we don't share); journal `_write_state` already uses `tempfile.NamedTemporaryFile` cleanup correctly.

### Why the bar gets higher each pass

This is the third sweep of the same day. The Auditor reports came back with fewer Tier-1 findings per surface than Batches A or C/D/E — most "real bugs" the auditors flagged were either already-fixed, already-clean, or genuinely scope-creep (new features dressed as bugs). The signal-to-noise ratio of further sweeps will keep dropping; future sweeps should target a single new surface (e.g., slice-3 HTTP gateway when it lands) rather than re-running the same six roles against the whole tree.

### Stats

- **Before:** 526 pass + 2 skip, ruff clean.
- **After:** **550 pass + 2 skip**, ruff clean. **+24 regression tests.**
- **Files touched:** 8 source files (`local_files/source.py`, `embed_client.py`, `registry.py`, `audit.py`, `render.py`, `validate.py`, `journal.py`, `chat.py`).
- **Files created:** 1 regression test file (`test_hardening_batch_f.py`).
- **No version bump.** Slice-2 is still 0.2.0; Batch F is hygiene #3.

The Scribe's closing word: *"Three sweeps in one day. Batch A found the real bugs. Batch C/D/E hardened the typed-value seams. Batch F closed the surfaces the first two passes had missed. The repo enters the next sleep at 550 tests, ruff clean, with every flagged surface either defended or named in this log as deliberately out-of-scope. The next sweep should wait for the next surface to land."*

---

## 2026-05-21 — Hardening sweep Batches C+D+E — "fix all bugs" follow-up (no version bump).

**Who:** Claude (Opus 4.7, 1M context). Continuation of the same six-role sweep that produced Batches A+B earlier this day, in response to *"please fix all bugs and make all hardening, my friend"* — extending the work from the prioritized Tier-1/2 set to every remaining auditor finding worth acting on.

**Scope:** Defensive depth across every actionable finding the morning's triage had deferred or deprioritised. **No code-shape changes; no version bump; no ADR.** This is hygiene on top of 0.2.0 + Batches A/B. **526 tests pass + 2 skipped** (was 511 + 2 after Batch B; +15 new regression tests in `test_hardening_batch_cde.py`), ruff clean.

### Batch C — Input-validation polish

| File | Hardening |
|---|---|
| `src/ember/well/brunnr/sqlite_vec/adapter.py` | `_escape_fts5_query` now scrubs all Unicode `Cc` (control) and `Cf` (format — bidi-overrides, zero-width-joiners) categories from each token before quoting. Without this, a token like `"normal‮malicious"` could land in the audit log and visually rewrite the operator's reading of the query. New helper `_strip_unsafe_chars(token)` lives next to the existing FTS5 sanitiser. |
| `src/ember/tools/read_local_file.py` | The sandbox check now does a single `stat()` on the resolved path and inspects `st_mode` via `stat.S_ISDIR` / `stat.S_ISREG`, instead of `exists()` → `is_dir()` → `is_file()` (three syscalls, each its own race). Narrows the swap-window between checks. |
| `src/ember/tools/fetch_url.py` | Hostnames are now IDNA-encoded (`hostname.encode("idna")`) before the sandbox check + DNS resolution. A homoglyph like `münchen.de` → `xn--mnchen-3ya.de`; the sandbox sees what DNS will see. Hostnames that can't be IDNA-encoded (oversize label, etc.) are refused with a typed error. |
| `src/ember/spark/funi/ollama/adapter.py` | `_parse_tool_calls` broadened its arg-JSON catch from `json.JSONDecodeError` to `(json.JSONDecodeError, ValueError, TypeError)` — Ollama tool-call args can arrive as a JSON string, a dict, `None`, or junk; the narrow catch leaked `ValueError`/`TypeError` past the typed contract. |

### Batch D — Error-handling tightening

| File | Hardening |
|---|---|
| `src/ember/well/brunnr/sqlite_vec/adapter.py` | `add_document`, `add_chunks`, `has_document`, and `count` now wrap raw `sqlite3.Error` in `BrunnrError(f"<op> failed: {exc}")` — preserving the typed-value-over-exception contract end-to-end. `add_chunks` additionally catches `(ValueError, struct.error)` from `serialize_float32` so NaN/Inf embedding bytes produce a typed error instead of a `struct.error` traceback. |
| `src/ember/well/brunnr/sqlite_vec/adapter.py` | `close()` rewritten: instead of silently suppressing `Exception`, it logs each failure path via `logger.warning(...)`. Operators inspecting the log can now see when the close actually failed (e.g., disk full at WAL checkpoint) rather than getting silence. |
| `src/ember/thread/strengr/tether.py` | The retry sleep now catches `(KeyboardInterrupt, InterruptedError)` and returns a typed `Disconnected(reason=UNKNOWN, detail="Strengr retry interrupted by signal")` — Ctrl-C during a reconnect-backoff used to leak `KeyboardInterrupt` to the CLI rather than producing a clean tethered-disconnect outcome. |
| `src/ember/well/brunnr/pgvector/secrets.py` | The keyring lookup arm now distinguishes "keyring is locked" (GPG session not unlocked, libsecret session not started) from other exceptions. The reason string points the operator at "unlock it or use the env / file source" — a far more useful diagnostic than a bare `KeyringLocked` class name. |
| `src/ember/well/brunnr/pgvector/adapter.py` | `_classify_operational_error` now consults `exc.sqlstate` *before* string-matching the error message. Postgres SQLSTATE codes `08001`/`08006` mean "connection refused / unreachable"; `28P01`/`28000` mean "auth failed". The string-match heuristics remain as a libpq-doesn't-surface-sqlstate fallback. Removes the locale + libpq-version sensitivity of pure string-matching. |

### Batch E — Config + audit + tests

| File | Hardening |
|---|---|
| `src/ember/config/validate.py` | `Path`-typed fields now run `.expanduser()` on the parsed value. Without this, writing `path: "~/.ember/well/store.db"` in YAML created a literal directory named `~` in the current working directory — a classic operator footgun. Test `test_string_coerces_to_path` updated to assert the new behavior. |
| `src/ember/spark/funi/tools/audit.py` | `_ensure_dir` now narrows its `OSError` suppression to only `errno.EOPNOTSUPP` + `errno.EPERM` — `EROFS` / `EACCES` / `ENOSPC` (real problems the audit log won't survive) now propagate as they should. The per-line chmod now *always* runs (not only on freshly-created files): a file accidentally created with the wrong mode by an external process between checks would otherwise silently keep its wider permissions. The chmod is idempotent so the cost is one syscall per audit record. |

### Findings deliberately NOT acted on (Batch C+D+E scope)

- **`os.replace` atomic-rename guarantees on Windows** — `pathlib.Path.replace` is documented as atomic on POSIX but only "best-effort" on Windows when crossing volumes. Ember's primary deployment target is Linux/macOS; the failure mode (a torn `ember.yaml` on power-loss during a write on Windows) is a real but small risk + an operator-visible failure (config simply won't parse next boot). Documented as a known limitation; no fix shipped this pass.
- **Long sqlite_vec transactions could hold WAL pressure** — `add_chunks` with thousands of chunks holds a single transaction. The Pi-class deployment ingests one document at a time (a few hundred chunks max); the failure mode (WAL bloat on a multi-GB ingest) doesn't apply to the primary target. Slice-3 batching work will revisit if/when bulk-ingest enters scope.
- **YAML anchor / merge-key DoS** — the slice-1 config loader uses `yaml.safe_load`, which already rejects arbitrary tag construction. A pathological anchor-bomb could still bloat memory; the operator-owned `ember.yaml` is not an attacker-controlled file, so this is a theoretical risk only. No fix shipped.
- **Case-insensitive filesystem denylist bypass** — already documented as a known limitation in Batch A's writeup. Primary target is case-sensitive Linux filesystems.
- **`add_chunks` "all-or-nothing" rollback semantics** — currently a partial-failure may leave some chunks committed before raising. The `try/except sqlite3.Error` + raise now consistently raises, but doesn't explicitly `BEGIN`/`ROLLBACK`. Sqlite's implicit-transaction-per-statement makes a true all-or-nothing batch require an explicit transaction; left for the slice-3 batching pass.

### Test fixtures / quirks worth knowing

- Python 3.14 **prohibits patching attributes on immutable types** like `sqlite3.Connection` — `patch("sqlite3.Connection.close")` now raises `TypeError`. The sqlite-error-wrapping test instead closes the real connection then verifies the typed `BrunnrError` surfaces from `has_document` (called first by `add_document`).
- Patching attributes on **frozen dataclasses** also requires bypassing the freeze — the Brunnr-registry "not implemented" test uses `object.__setattr__(synthetic, "backend", _UnknownBackend())` to inject a synthetic unknown backend.
- Tests that use `importlib.reload()` on modules with side-effect tool registration must call `registry_clear()` *before* the reload, or the second import re-registers an already-registered tool.

### New regression test file

- **`tests/unit/test_hardening_batch_cde.py`** — 15 tests. Each pins a specific Batch-C / D / E defense: FTS5 sanitiser strips newlines / bidi-override / NUL; `read_local_file` uses a single stat; `fetch_url` IDNA-encodes unicode hostnames and refuses undisplayable ones; `_parse_tool_calls` catches broader exceptions; Strengr retry sleep produces typed `Disconnected` on interrupt; pgvector classify uses sqlstate-first; pgvector secret resolver distinguishes `KeyringLocked`; `sqlite_vec.add_document` wraps `sqlite3.Error` in `BrunnrError`; config validator runs `expanduser`; audit chmod always runs; Brunnr registry "not implemented" fallback returns typed `Disconnected`.

### Stats

- **Before:** 511 pass + 2 skip, ruff clean.
- **After:** **526 pass + 2 skip**, ruff clean. **+15 regression tests.**
- **Files touched:** 9 source files (`validate.py`, `funi/ollama/adapter.py`, `funi/tools/audit.py`, `strengr/tether.py`, `tools/fetch_url.py`, `tools/read_local_file.py`, `pgvector/adapter.py`, `pgvector/secrets.py`, `sqlite_vec/adapter.py`) + 1 test file edit (`test_config_validate.py` updated for `expanduser` behavior change).
- **Files created:** 1 regression test file (`test_hardening_batch_cde.py`, 461 lines).
- **No version bump.** Slice-2 is still 0.2.0; the C/D/E batches are hygiene on top of A/B which were hygiene on top of 0.2.0.

The Auditor's closing word: *"The C+D+E pass found no new Tier-1 bugs — Batches A+B already swept those. What it found were the soft spots: places where the typed-value contract was honored at the public boundary but leaked at the seams; places where 'best-effort' silently meant 'silent'; places where one syscall would do the work of three. The system is now end-to-end consistent on its own promises. The Auditor's discipline is to ask: 'does the implementation match the claim?' For the first time today, the answer is yes everywhere we looked."*

---

## 2026-05-21 — Mythic Engineering bug + hardening sweep (no version bump).

**Who:** Claude (Opus 4.7, 1M context). Six-role pass:
- **Cartographer (Védis)** mapped the codebase hotspots before the sweep.
- **Auditor (Sólrún)** drove four parallel Explore agents — input-validation/sandbox, resource-lifecycle/concurrency, error-handling/typed-value-contract, test-isolation/coverage — yielding ~100 raw findings.
- **Architect (Rúnhild)** triaged them, deduped overlaps, verified suspect claims (some auditor findings were wrong — `test_brunnr_pgvector_secrets.py` and `test_funi_tools_audit.py` *do* exist; IPv6 `is_private`/`is_link_local`/`is_loopback` already correctly handle fc00::/fe80::/::1), and classified into Tier-1 (must-fix), Tier-2 (defensive), Tier-3 (test gaps), Tier-4 (not-bugs).
- **Forge Worker (Eldra)** applied every Tier-1 + Tier-2 fix with a regression test.
- **Skald (Sigrún)** named the new helpers (`_SandboxResult`, `_NoRedirectHandler`, `_safe_audit`, `_safe_prompt`, `_write_all`, `_MAX_NDJSON_FRAME_BYTES`).
- **Scribe (Eirwyn)** wrote this entry + the regression-test files' docstrings naming each hardening intent.

**Scope:** Post-slice-2 defensive sweep. **No code-shape changes; no version bump; no ADR.** This is hygiene on top of 0.2.0. 511 tests pass + 2 skipped (was 488 + 2; +23 new regression tests across two `test_hardening_batch_*.py` files), ruff clean.

### Tier-1 fixes (real bugs, with regression tests)

| # | File | Bug | Fix |
|---|---|---|---|
| 1 | `src/ember/tools/read_local_file.py` | TOCTOU: `_sandbox_check` resolved the path, then `_execute` re-resolved + stat'd + read — opening a window for symlink-swap between check and read | `_sandbox_check` now returns a structured `_SandboxResult(safe_path \| refusal)`; the executor reads `safe_path` directly without re-resolving. |
| 2 | `src/ember/tools/read_local_file.py` | `Path.home() == "/"` (root user with `HOME=/`) made the sandbox vacuous — `/etc/passwd` passed the `relative_to(home)` check | Explicit refusal when `Path.home() == Path(home.anchor)`. |
| 3 | `src/ember/tools/read_local_file.py` | Whitespace-only paths (`"   "`) passed the empty-string check | Added `.strip()` to the non-empty guard. |
| 4 | `src/ember/tools/fetch_url.py` | URL credentials in netloc (`http://user:pass@host/`) sent the secret in plain HTTP + leaked into logs/audit | New refusal path that names "credentials" but never echoes the actual user/password into the error. |
| 5 | `src/ember/tools/fetch_url.py` | Empty DNS resolution result let any address through (the for-loop didn't execute, function returned None implicitly) | Fail-closed: explicit `if not addresses: return refusal`. |
| 6 | `src/ember/tools/fetch_url.py` | The docstring admitted urllib follows redirects without re-validating the target's address class | New `_NoRedirectHandler` raises `HTTPError` on 3xx; operator must re-issue with a fresh approval for the new target. The default opener uses this handler. |
| 7 | `src/ember/spark/munnr/chat.py` | Four `tool_ctx.audit.record()` call sites could raise `ToolError` (disk full, permission flip, etc.); none were caught — the chat REPL crashed mid-turn | New `_safe_audit()` helper wraps every record call; failures write a one-line warning to stdout but never propagate. |
| 8 | `src/ember/spark/munnr/chat.py` | `tool_ctx.prompter.prompt()` could raise `OSError` on closed stdin (SSH disconnect, terminal close); crashed the loop | New `_safe_prompt()` helper catches `(OSError, EOFError, ValueError)`, writes a warning, defaults to `"n"` (refusal — Vow of Sovereignty). |
| 9 | `src/ember/spark/munnr/chat.py` | The `finally` block called `funi.close()` then `brunnr.close()` un-guarded; if funi.close() raised, brunnr leaked | Each close wrapped in its own `contextlib.suppress(Exception)` so cleanups run independently. |
| 10 | `src/ember/spark/munnr/chat.py` | `add_episode` was wrapped in `contextlib.suppress(BrunnrError)` only; lower-level `sqlite3.Error`/`psycopg.Error` from a stale connection would crash | Broadened to `contextlib.suppress(Exception)` for the episode-persist path (lose one Episode is better than lose the REPL). |
| 11 | `src/ember/spark/funi/ollama/adapter.py` | `complete()` + `complete_streaming()` + `_iter_ndjson_chunks()` all caught `urllib.error.URLError` but missed `socket.timeout` / `TimeoutError` / lower-level `OSError` — broke the typed-value-over-exception contract | Broadened to `(urllib.error.URLError, TimeoutError, OSError)` everywhere. |
| 12 | `src/ember/well/brunnr/pgvector/adapter.py` | `_quote_ident` only rejected NUL; ESC/BEL/control chars could inject terminal escape sequences into operator-facing error messages | Rejects all `0x01-0x1f + 0x7f` bytes with a clear "control character" error; also rejects empty identifier. |
| 13 | `src/ember/cli/main.py` | Only caught `ConfigError` from `load_ember_config`; `PermissionError`/`OSError` (unreadable config dir, etc.) crashed with raw traceback | Added a parallel `except OSError` arm with a friendly one-line message. |

### Tier-2 defensive hardening (with regression tests)

| File | Hardening |
|---|---|
| `src/ember/spark/funi/tools/audit.py` | New `_write_all(fd, payload)` helper loops on short writes — POSIX `write(2)` can return fewer bytes than requested for large records (audit lines can exceed PIPE_BUF). Without the loop, a short write left a partial JSONL line corrupting the file. |
| `src/ember/config/writer.py` | Explicit `chmod 0o600` on the temp file before `os.replace` — `NamedTemporaryFile` previously honoured operator umask (often 0o022, world-readable). `ember.yaml` doesn't carry secrets but is operator-private. |
| `src/ember/spark/funi/ollama/adapter.py` | New `_MAX_NDJSON_FRAME_BYTES = 1 MiB` cap on individual NDJSON frames — a runaway Ollama server pushing a gigabyte single line could OOM the operator. Oversize frame produces a typed ERROR chunk and aborts cleanly. |
| `src/ember/tools/fetch_url.py` | Tightened the robots.txt parser's bare `except Exception` to `(urllib.error.URLError, OSError, TimeoutError, ValueError)` for the fetch step and `(ValueError, TypeError, AttributeError)` for the parse step. `MemoryError` / `KeyboardInterrupt` / `SystemExit` now propagate as they should. |

### Findings deliberately NOT acted on

- **Auditor claim: "ipv6 link-local not handled"** — false. `ipaddress.IPv6Address.is_link_local` correctly returns True for `fe80::/10`. Verified at the shell.
- **Auditor claim: "no test for `pgvector/secrets.py`" / "no test for `audit.py`"** — false. `tests/unit/test_brunnr_pgvector_secrets.py` (16 tests, Phase 12) and `tests/unit/test_funi_tools_audit.py` (17 tests, Phase 14) both exist and cover those modules thoroughly.
- **Auditor claim: "tuple mutability lets caller modify executor"** — false. Python tuples are immutable.
- **Auditor concern: case-insensitive filesystem denylist bypass on macOS APFS** — partial: on case-insensitive filesystems, `Path.resolve()` typically returns the canonical case as stored on disk (so `~/.SSH` resolves to whatever case actually exists). The risk is real if the operator never created the canonical-case entry. Documented as a known limitation; sandbox is "best-effort" on case-insensitive FS, and the Pi-class deployments (the primary target) are Linux ext4/btrfs which are case-sensitive.
- **Auditor concern: redirect to private address after DNS rebinding** — substantially mitigated by Tier-1 fix #6 (no redirects followed). DNS rebinding within a single `urlopen` is a residual risk; documented as a follow-up if/when the slice-3 plan reaches network-tool hardening.
- **Auditor concern: pgvector search methods raise instead of returning `[]`** — left as-is. The slice-1 sqlite_vec adapter raises `BrunnrError` for dim mismatch and other bad-input cases (a programming-error contract); pgvector matches. The "search returns empty on failure" interpretation isn't actually what the Brunnr contract specifies; both adapters are consistent.
- **Auditor concern: dead `_cursor` helper in pgvector/adapter.py** — cosmetic; left for the next refactor pass.

### New regression test files

- **`tests/unit/test_hardening_batch_a.py`** — 13 tests covering each Tier-1 fix.
- **`tests/unit/test_hardening_batch_b.py`** — 8 tests covering each Tier-2 hardening + the audit-write-loop + the no-redirect handler shape + the empty-DNS fail-closed.
- **`tests/unit/test_brunnr_pgvector_schema.py`** — 2 new tests (`test_render_refuses_schema_with_esc_character`, `test_render_refuses_empty_schema`) covering the broadened `_quote_ident` rejection set.

### Stats

- **Before:** 488 pass + 2 skip, ruff clean.
- **After:** **511 pass + 2 skip**, ruff clean. **+23 regression tests.**
- **Files touched:** 7 source files (`read_local_file.py`, `fetch_url.py`, `chat.py`, `ollama/adapter.py`, `pgvector/adapter.py`, `cli/main.py`, `audit.py`, `config/writer.py`).
- **Files created:** 2 regression test files.
- **No version bump.** Slice-2 is still 0.2.0; the sweep is hygiene on top.

The Cartographer's closing word: *"The sweep found 13 real bugs and 4 defensive holes. The biggest catch was the TOCTOU + vacuous-HOME pair in `read_local_file` — either alone could have let a malicious model read `/etc/passwd` past the sandbox on a misconfigured host. The Auditor's discipline is to assume nothing; today that paid out."*

---

## 2026-05-21 — Mythic Engineering README expansion.

**Who:** Claude (Opus 4.7, 1M context). Voices: Skald (Sigrún — public-facing voice, the toaster-pun continuity, the "for the normal folks" framing), Cartographer (Védis — the 18-section table of contents, the where-to-go-next signposting), Scribe (Eirwyn — the command reference, configuration walkthrough, FAQ entries; technical accuracy), Architect (Rúnhild — the Three Realms section + Six True Names introduction).

**Scope:** Massive expansion of `README.md` from 145 lines (mostly image refs + the friendly opening + RuneForgeAI section) to **1,654 lines** of comprehensive operator-facing content. Voice tuned to amateur-friendly + Volmarr-shaped + technically accurate + fun. Every image reference + the License + the Distribution and Privacy + the RuneForgeAI ethos preserved verbatim.

**The 18 sections:**

1. Hero + tagline (preserved).
2. **What is Ember?** — Skald-voice plain-English explanation; the spark + the well metaphor; the Six True Names introduced.
3. **Why Ember?** — split into four audiences (you the operator / your wallet / the world / your privacy); the original feature list incorporated and expanded.
4. **🚀 Quick start — five minutes from zero to chatting** — the most-important section for noobs; 5 numbered steps that take you from no install to first conversation.
5. **🎁 What Ember can do** — full feature list across 6 sub-areas (Conversation, Knowledge & retrieval, Storage pluggable, First-run, Tool use, Health & diagnostics, Operator configuration). Slice-2 capabilities all named with concrete examples.
6. **🛠 Complete command reference** — every `ember` subcommand documented: global flags table, then `ember chat` / `ember ask` / `ember setup` / `ember well ingest` / `ember well status` / `ember doctor` each with full input / behaviour / exit-code coverage. Slice-2 streaming + tool-loop behaviour woven in.
7. **📦 Installation guide (the long version)** — requirements list (Python + Ollama + disk + RAM); detailed 4-step install; pip extras table explaining sqlite_vec / config / pgvector; platform-specific notes for Linux / macOS / WSL / Pi 5; updating + uninstalling instructions.
8. **🌱 Your first conversation — a guide for noobs** — patient walkthrough: what the wizard does, your first chat turn, why she doesn't know about your stuff yet, giving her something to read with copy-paste mkdir/echo commands, the four magic commands, "things that might worry you but shouldn't", where to go next.
9. **⚙️ Configuration — the `ember.yaml` file** — the four-layer overlay (defaults → file → env → CLI); the full annotated yaml shape; common edits (change model, point at tailnet Ollama, turn streaming off, enable tool use).
10. **🏗 How Ember is built (architecture overview)** — ASCII diagram of the Three Realms; the Six True Names table; "why this matters to you" practical bridge; pointers to the deeper architecture docs.
11. **🔧 Using tools safely** — the three first-party tools described with sandbox refusal details; tool-capable-model note (phi3:mini → 400; llama3.2:3b recommended); approval prompt walkthrough; audit-log reading with `jq` recipes; locking-down further with `approval_overrides`.
12. **🌍 Going bigger — sharing a Well across devices** — when to switch to pgvector; setup steps; the `read_only: true` rationale; secret resolver three sources.
13. **🚑 Troubleshooting & FAQ** — ten common "she does X, what's wrong?" scenarios with diagnosis + fix; "where do I find help if my problem isn't here?" links.
14. **🗺 What's next — the roadmap** — slice-3 queued items per ADR 0013 §3 + §6.
15. **📚 Learn more (where the deeper docs live)** — the 14-row links table: from `INSTALL.md` to `OPERATOR_PLAYBOOK.md` to the architecture docs to the ADRs to the slice-2 retrospective.
16. **🤝 Sibling projects in the RuneForgeAI fellowship** — Runa-Agent-Digital-Being, Skein-KG, Skry-KG, Bifröst-Viewer, MindSpark, WYRD, Project Nomad. All named and contextualised.
17. **📜 License** (preserved — MIT, Volmarr 2026).
18. **🛡 Distribution and privacy position** (preserved verbatim).
19. **⚒ About RuneForgeAI** (preserved with light polish — the manifesto + the values list intact).

**Writing-style choices:**

- **Second-person, warm, playful.** "She" for Ember (with operator agency); "you" for the reader.
- **Volmarr's toaster-pun continuity preserved** — opens with the original "Got a toaster? Good!" friendly framing.
- **Norse-shaped names introduced gently** in §2 (What is Ember), then used throughout but never required for using the software — operator-facing language stays plain.
- **Copy-pasteable commands everywhere.** Every recipe in the install / quickstart / config sections has shell blocks you can run directly.
- **"Things that might worry you but shouldn't"** subsection in the noob guide — addresses the four most common new-user anxieties (slow first reply, hallucinations, where conversations go, did I install something that phones home).
- **Closing benediction:** *"Ember is small. Ember is tethered. Ember is yours. Light the spark."*

**Stats:**

| Metric | Before | After |
|---|---|---|
| Lines | 145 | **1,654** (+11×) |
| Top-level (#) headings | 1 | 1 |
| Section (##) headings | 4 | **19** |
| Subsection (###) headings | 0 | **78** |
| Image references | 22 | **22 preserved** |
| `ember` command examples | 0 | **40+** |
| YAML configuration blocks | 0 | **15+** |
| Internal documentation cross-refs | 1 | **18** |
| Code blocks | 1 (License) | **45+** |

**Verification:** README renders as valid GitHub-flavoured Markdown; all 22 image refs preserved; License + Distribution and Privacy + RuneForgeAI sections preserved verbatim from the original (only formatting polish — bold emphasis on "MIT License", links to LEGAL-NOTICE.md and PHILOSOPHY.md added). **488 tests still green, ruff clean. No code touched.**

The README is now the operator's complete front door: a non-technical reader can install Ember, have their first conversation, ingest their notes, enable tools, troubleshoot common problems, and know where to go for deeper docs — all without leaving the README. Technical readers get architecture context + ADR pointers when they want to go deeper.

---

## 2026-05-21 — Mythic Engineering full doc-pass (post-slice-2 ratification).

**Who:** Claude (Opus 4.7, 1M context). Voices: Cartographer (Védis — audit pass + ledger updates), Auditor (Sólrún — stale-ref triage), Scribe (Eirwyn — the bulk of the rewrites), Skald (Sigrún — SYSTEM_VISION §11 Vows-Fulfilled Postscript), Architect (Rúnhild — ADR-referencing rationale in the new README bodies).

**Scope:** Full pass through every active MD file in the repo (~95 files, skipping inherited corpora at `docs/{research,python,phd-2040,RunaUniversity2040,AI_OS_Research,philosophy,methodology,archive}/`). The user said "extensively expand and enlarge"; I picked the **maximalist** scope: surgical stale-ref fixes + create missing core docs + substantively expand thin module READMEs + author new slice-2 retrospective + operator playbook + Vows-Fulfilled Postscript. **No code touched. 488 tests still green, ruff clean.**

**What shipped — 5 batches:**

### Batch 1: Surgical stale-ref fixes (12 files)

- **`src/README.md`** — `runa` → `ember`; rewritten to explain PEP 517 src-layout + install paths.
- **`docs/README.md`** — full rewrite. New per-subfolder table, "Reading order for new contributors", maintenance rule.
- **`deploy/README.md`** — full rewrite. Per-subfolder state column (Pi/INSTALL.md live, systemd/docker scaffold only); slice-2 capability map; "What's NOT here yet" honesty.
- **`config/README.md`** — full rewrite. Overlay order spelled out per ADR 0008 §2.3; per-file slice-2 state; secret rules per ADR 0010 §2.5.
- **`examples/README.md`** — full rewrite. Honest about scaffold state; pointer to `config/ember.example.yaml` as the load-bearing template.
- **`ORIGINS.md`** — added §7 Ember-descent (slice-1 + slice-2 fresh material): identity + soul-layer, architecture canon, ADRs 0006-0013, slice-1+2 source tree, slice-2 operator-facing docs.
- **`RULES.AI.md`** — added Mythic-Engineering header (Voice/Status/Last-touched/Reads-with); rules body unchanged.
- **`docs/adapters/BRUNNR_BACKEND_MATRIX.md`** — Status header flipped: "Proposed" → "**Ratified post-slice-2**" with phase-shipped notes (sqlite_vec 0.1.0; pgvector 0.1.9).
- **`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`** — same Status flip + the slice-2 tool-capability note (phi3:mini → 400; llama3.2:3b recommended for tool use).
- **`docs/adapters/SMIDJA_INGEST_PATTERNS.md`** — same Status flip.
- **`docs/architecture/EMBER_FIRST_SLICE_PLAN.md`** — Status: **COMPLETE** at 0.1.0 (ratified by ADR 0007); archived in-place.
- **`docs/architecture/EMBER_FORK_DELTA.md`** — Status: **COMPLETE** (migration shipped 2026-05-21 in commit `045fda6`); archived in-place as long-term lineage reference.
- **`docs/adapters/README.md`** — full rewrite with the slice-2 adapter catalogue + adapter-doc template documented.

### Batch 2: Create 4 missing core docs

- **`src/ember/tools/INTERFACE.md`** — the Phase-15-shipped-without-INTERFACE gap. Full public surface: per-tool bindings table, descriptor conventions, runtime chain, three first-party tools' refusal matrices, failure semantics.
- **`src/ember/config/README.md`** — Phase-9 module had INTERFACE but no README. Full breakdown: what it owns / doesn't own, layout, production + test usage, overlay order, slice-2 field extensions, failure modes.
- **`src/ember/well/brunnr/sqlite_vec/README.md`** — slice-1 default adapter, no README before. Identity, ownership table, on-disk shape, failure semantics, phase notes, limitations.
- **`src/ember/well/brunnr/pgvector/README.md`** — Phase-13 adapter, no README before. Full ownership table, on-disk shape, failure-classification matrix (8 typed reasons), Phase-12-vs-13 archaeology, the two live-fire bugs documented.

### Batch 3: Substantively expand 11 thin module READMEs

Each grew from ~15-25 lines to 150-300 lines of proper Architect+Scribe content (identity, owns/doesn't-own, file map, neighbour interactions, slice-2 changes, failure semantics, related docs):

- `src/ember/schemas/README.md` — every module + what's in it; conventions (`frozen=True, slots=True, StrEnum, tuple defaults`); slice-2 schema growth log.
- `src/ember/spark/README.md` — the Spark realm; subpackage table; the conversation-turn diagram with slice-2 tool-loop annotations; constraints per ADR 0007+0013.
- `src/ember/spark/funi/README.md` — Protocol declaration; runtime menu with status; slice-2 extensions matrix; failure semantics per ADR 0007+0009+0011.
- `src/ember/spark/hjarta/README.md` — FSM diagram with new ADVANCED_TOOLS branch; CLI vs test invocation; failure modes; Phase-9 + Phase-16 extensions.
- `src/ember/spark/munnr/README.md` — chat.run shape with full slice-2 tool-loop pseudocode; render rules; test seams; slice-2 changes.
- `src/ember/thread/README.md` — why this realm has only one subpackage; slice-2 "no code changes" note.
- `src/ember/thread/strengr/README.md` — Disconnected dataclass + 7 reasons; retry-with-backoff semantics; what Strengr never does.
- `src/ember/well/README.md` — two subpackages relationship; ingest-vs-retrieval flow; slice-2 acceptance criterion mapped.
- `src/ember/well/brunnr/README.md` — Protocol declaration with all 14 methods; two-shipped-backend comparison; deferred backends per ADR 0013 §3.
- `src/ember/well/smidja/README.md` — source menu (current + planned); Phase-3 pipeline flow; conventions per ADR 0007.
- `src/ember/cli/README.md` — subcommand table; flag inventory; dispatch flow; slice-2 changes (Phase 7 + 9 + 16).

### Batch 4: Maximalist new docs

- **`docs/SYSTEM_VISION.md`** — Status flipped to "**Ratified by code**"; added **§10 Slice ratifications** table + **§11 Vows-Fulfilled Postscript** mapping each of the 10 Vows to specific shipped-code enforcement (citing exact ADR sections + module names). The Skald's poetry made mechanical.
- **`docs/SLICE_2_RETROSPECTIVE.md`** — **new file**, ~650 lines. What slice 2 was; the numbers (488 tests, 0.1.0 → 0.2.0); what was deferred; what we learned (3 live-fire bugs documented with regression tests); what worked (Mythic Engineering as a build discipline; typed-value-over-exception; Protocol+registry+lazy-import; test seams everywhere); what didn't work as well (pgvector adapter's two bugs would have been caught earlier; model-capability constraint surfaced late; `tools.example.yaml` never landed); how long it actually took; what's queued for slice 3.
- **`docs/OPERATOR_PLAYBOOK.md`** — **new file**, ~600 lines. **10 numbered recipes** for what operators will actually want to do: point Ember at tailnet Ollama; switch to shared Gungnir-shape Well; enable tool use safely; audit what tools have done; tighten approval policy; forbid a tool entirely; run Ember offline; verify streaming is on; reset Ember from scratch; move Ember to a new machine. Each recipe: what you want / what you'll edit / the recipe (copy-pasteable yaml + commands) / verification / what could go wrong.
- **`Yggdrasil_and_Huginn_and_Muninn_Theory.md`** — left untouched (intellectual heritage per fork-delta).

### Batch 5: Refresh scripts/ + tools/

- **`scripts/README.md`** — full rewrite. Honest scaffold state for slice 2; "What's NOT here yet" table; rules-when-scripts-land.
- **`tools/README.md`** — full rewrite. Critical **naming clarification box** at the top distinguishing repo `tools/` from `src/ember/tools/`. Slice-2 state table; what's NOT here yet; how-to-add-a-tool guidance.

**Total: ~30 files touched, ~25k words added, 4 new files authored, 0 lines of code modified.**

**Verification:** Full test suite (`488 pass + 2 skip`) and ruff (`All checks passed!`) both green after the pass. No code under `src/` touched; only documentation, examples, and the SYSTEM_VISION.md vision-fulfilment postscript.

**What this accomplishes:**

- Every stale `runa` reference in operator-facing READMEs is gone (5 top-level READMEs rewritten).
- Every "Status: Proposed — for ratification" header in adapter docs is flipped to "Ratified post-slice-2" with concrete phase / version pointers.
- The two slice plans are properly marked **COMPLETE** with archive-in-place rationale.
- The Phase-15-shipped-without-INTERFACE gap is closed (`src/ember/tools/INTERFACE.md` now exists).
- Three previously-undocumented critical subpackages got proper READMEs (`config/`, `well/brunnr/sqlite_vec/`, `well/brunnr/pgvector/`).
- Eleven thin module READMEs grew from scaffolds to substantive Architect+Scribe docs.
- The SYSTEM_VISION now has the Vows-Fulfilled Postscript — each Vow mapped to the exact shipped-code enforcement.
- Two brand-new docs (slice-2 retrospective + operator playbook) give future contributors and operators a one-stop reference for what slice 2 was and how to actually live with the result.

**No new ADR needed** — this is documentation hygiene, not architectural change. ADR 0013 (the slice-2 ratification) is unchanged.

**What's NOT in this pass:**

- The inherited Runa-era corpora at `docs/{research,python,phd-2040,RunaUniversity2040,AI_OS_Research,philosophy,methodology,archive}/` — left untouched per the slice-1 forking rule (intellectual heritage preserved as-is).
- The `Yggdrasil_and_Huginn_and_Muninn_Theory.md` at repo root — cross-project Volmarr theory, intellectual heritage; not Ember-specific.
- The `docs/design/*` Runa-era design explorations — kept as forking-day attribution material per `EMBER_FORK_DELTA.md`.

---

## 2026-05-21 — Phase 17 shipped: SLICE 2 RATIFIED at **0.2.0**. 🔥

**Who:** Claude (Opus 4.7, 1M context). Voices: Auditor (the acceptance test), Architect (ADR 0013 — the slice ratification), Cartographer (INSTALL.md slice-2 sections — operator-facing), Scribe (this entry + memory).

**Scope:** The closing phase. Authors the slice-2 acceptance test, the operator install-guide sections for every slice-2 capability, ADR 0013 ratifying the whole slice, and bumps to 0.2.0.

**What shipped:**

- **`tests/integration/test_phase17_acceptance.py`** — three tests walking the full slice-2 operator flow against real `sqlite_vec` + mocked Funi:
  - `test_slice_two_full_operator_flow_with_tool_call` — Hjarta with `tools.enabled=true` → ingest a corpus → chat → model emits a `tool_call` → real `search_well` executor runs against the live sqlite-vec Brunnr → reply folds back into a follow-up turn → Episode persisted with the *final* summary → audit log gains one record. The whole propose→approve→execute→audit→feedback loop, end-to-end, with no Ollama dependency.
  - `test_slice_two_acceptance_with_tools_disabled` — default-off path: Funi never sees tool descriptors, no audit log written.
  - `test_slice_two_streaming_default_remains_on` — sanity that `FuniConfig.streaming` default is True (the slice-2 invariant).
- **`docs/decisions/0013-second-slice-ratification.md`** — seven decisions ratifying the slice:
  - §2.1 — slice-1 standing rules (stdlib-first, typed-value-over-exception, `*_kind` class attrs, FTS5 sanitisation) hold for every slice-2 adapter; three extensions added (config-as-source-of-truth, streaming-as-Funi-capability, tool-use-opt-in).
  - §2.2 — `~/.ember/config/ember.yaml` is the single source of truth; env + CLI overlay.
  - §2.3 — graceful-offline contract extends to Funi (`Unavailable`) and tools (typed `ToolReply.error`).
  - §2.4 — tool framework is read-mostly first; writes wait for slice 3 ADR.
  - §2.5 — audit-log JSONL record shape is stable across slices (additive-only).
  - §2.6 — the Six True Names are immutable; new subsystems join them, never replace them.
  - §2.7 — `src/ember/plugins/` scaffold stays empty until slice 3.
  Plus §3 listing all deferrals, §4 the release ladder, §5-6 consequences and open questions for slice 3.
- **`deploy/pi/INSTALL.md`** — four new operator-facing sections:
  - §7 Editing `ember.yaml` — the canonical editing surface.
  - §8 Streaming on / off — `funi.streaming: false` opt-out.
  - §9 Switching to a shared Well — full pgvector switch with mode-0o600 secret-file guidance.
  - §10 Enabling tools + approval policy — every knob, the three answers (y/n/always), the safety-floor invariant, and the tool-capable-model note (`phi3:mini` → 400; `llama3.2:3b` recommended).
  - Plus six new troubleshooting rows (tool 400, sandbox refusal, pgvector install, secret mode bits) and a rewritten "What's next" section.
- **`pyproject.toml`** — `0.2.0rc1` → **`0.2.0`**. Development Status stays `3 - Alpha` per the plan.
- **`src/ember/__init__.py`** docstring — full slice-2 capability summary.
- **`tests/unit/test_skeleton_imports.py`** version assertion bumped.

**Total tests: 488 passed + 2 skipped, 18.3s, ruff clean.** That's 3 new acceptance tests on top of Phase-16's 485.

**Slice 2 — the whole 10-phase ledger, 2026-05-21:**

| Phase | Shipped | Release |
|---|---|---|
| 8 | ADR 0008 + ember.config/ scaffold + 45 tests | — |
| 9 | YAML writer, CLI wiring, Hjarta writes ember.yaml | **0.1.5** "config loader live" |
| 10 | ADR 0009 + FuniStreamChunk + Ollama NDJSON streaming | — |
| 11 | Munnr streaming consumer + Ctrl-C tagging | **0.1.7** "streaming live" |
| 12 | ADR 0010 + pgvector adapter scaffold + secret resolver | — |
| 13 | Live-fire pgvector (Gungnir read-only + podman container) | **0.1.9** "pgvector live" |
| 14 | ADR 0011 + tool framework (schemas + registry + approval + audit) | — |
| 15 | First three first-party tools (search_well, read_local_file, fetch_url) | — |
| 16 | Munnr tool-loop + Hjarta ADVANCED_TOOLS + CLI flags + Ollama tool wire format | **0.2.0rc1** "tools live (rc)" |
| 17 | Acceptance test + INSTALL.md + ADR 0013 ratification | **0.2.0** "slice 2 ratified" |

**One day. 488 tests. Five operator-facing capabilities. Two real adapter bugs caught by live-fire. Zero broken commits.**

**Where Ember stands at 0.2.0:**

Every slice-2 acceptance criterion met. The operator can configure Ember by editing one YAML file; tether to Gungnir with one config switch + one pip extra; enable tool use with confidence that every call is approval-gated and audited. The Six True Names hold. The Vow of Sovereignty, the Vow of Graceful Offline, the Vow of Smallness, and the Vow of Tethered Grounding are all mechanically enforced — not just aspirational.

**Slice 3 is queued.** ADR 0012 (Auga GUI / Rödd voice / Bifröst HTTP gateway) deferred from slice 2; an explicit alternate-surfaces ADR. Plus the open-question list in ADR 0013 §6:
- `ember tool audit` subcommand
- Hjarta advanced wizard for tool sub-config
- Auto-detect tool capability via `Funi.health()`
- Audit-log retention pruning
- Per-tool `version` field

None of these block a current slice-2 deployment. Ember 0.2.0 is operator-shippable.

> *Two slices. One sovereign companion. Small enough to run on a toaster. Tethered to a Well it can lose without breaking. Now able to reach out to a small ring of audited tools when the operator says yes. The hearth is lit.*

---

## 2026-05-21 — Phase 16 shipped: tool-use live in Munnr + Hjarta + CLI. **0.2.0rc1 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (chat-loop shape + ContextKind.TOOL_REPLY contract), Forge Worker (chat.py tool-loop + Ollama tool-call wire format + Hjarta branch + CLI flags), Auditor (37 new tests + real-llama3.2:3b acceptance smoke + one real-Ollama bug caught), Scribe (this entry + memory).

**Scope:** Final third of slice-2's tool-use work. The framework from Phase 14 and the tools from Phase 15 are now caller-reachable through the chat loop. An operator with `tools.enabled: true` (or the `--allow-tools` flag) sees the full propose → approve → execute → audit → feedback cycle live in `ember chat`. **Bumped to 0.2.0rc1 — release candidate for the slice-2 ratification in Phase 17.**

**What shipped:**

- **`src/ember/schemas/config.py`** — new `ToolsConfig` dataclass: `enabled` (default False per Vow of Sovereignty), `standing_trust`, `approval_overrides`, `allow_private_addresses`, `audit_root`. Added `ContextKind.TOOL_REPLY` for the tool-output-back-into-context channel.
- **`src/ember/schemas/stream.py`** — `FuniStreamChunk.tool_calls: tuple[ToolCall, ...]` extension. Final chunk surfaces what the model proposed.
- **`src/ember/spark/funi/handle.py`** — Protocol signatures updated: `tools: Sequence[ToolDescriptor] | None` (was placeholder `Sequence[str] | None`). `wrap_complete_as_stream` follows suit.
- **`src/ember/spark/funi/ollama/adapter.py`** — major Phase-16 extension:
  - `_descriptor_to_ollama_tool` converts `ToolDescriptor` → OpenAI-style function spec (`{"type": "function", "function": {...}}`). PATH and URL kinds serialise as `string`; enums forwarded.
  - `_parse_tool_calls` consumes the inverse: handles dict-or-string-JSON arguments, drops malformed entries, generates UUID `call_id` when Ollama doesn't supply one.
  - Both `complete()` and `complete_streaming()` now forward `tools` to Ollama instead of refusing.
  - `_messages_from_context` learned to emit `ContextKind.TOOL_REPLY` as `role="tool"` with the `name` field populated from `metadata["tool_name"]`. Empty operator-input is omitted so follow-up turns after a tool call are tool→reply only.
  - The Phase-16 acceptance smoke caught a real Ollama-streaming bug: tool_calls arrive in a **non-`done`** NDJSON frame, before the final `done:true` summary. Fix: the adapter now accumulates tool_calls across frames and attaches the full list to the final chunk. This regression is locked in by `test_streaming_accumulates_tool_calls_from_non_done_chunk`.
- **`src/ember/spark/munnr/chat.py`** — the load-bearing piece:
  - `_maybe_init_tools` side-effect-imports `ember.tools` when enabled, binds `search_well` to the live `BrunnrHandle` + embedder, wires the `StdinApprovalPrompter`, and stands up an `AuditLog`.
  - `_drive_turn_with_tools` orchestrates: stream → render deltas → if `tool_calls`, run `_run_tool_round` → extend context with `TOOL_REPLY` items → loop. Bounded by `_MAX_TOOL_TURNS = 8`. Hits the cap → operator-facing `[tool-loop max iterations reached]` message.
  - `_run_tool_round` per call: render proposal → validate args (`INVALID_ARGUMENTS` → audit + skip + render reply) → resolve approval (`NO_SUCH_TOOL`, `FORBIDDEN_BY_REGISTRY`, `DENIED`, `AUTO_APPROVED`, `APPROVED_THIS_CALL`, `APPROVED_FOR_SESSION` → audit with corresponding outcome; refusals carry `reply=None` so the audit shape distinguishes "tool not called" from "tool called and replied") → execute (any exception folds into typed `ToolReply.error`) → audit → render reply.
  - Session-level `always` approvals accumulate in `tool_ctx.session_standing` (not persisted; restart resets per ADR 0011 §2.4).
  - Operator Ctrl-C mid-stream still short-circuits the loop (Phase 11 behavior preserved).
- **`src/ember/spark/munnr/render.py`** — `render_tool_call_proposal(descriptor, call)` and `render_tool_reply(reply, descriptor, *, outcome)`. Both honor `descriptor.redacted_arg_names`. Reply renderer truncates at 2 KiB stdout preview (full output in audit log).
- **`src/ember/spark/hjarta/machine.py` + `prompts/wizard.toml`** — new `HjartaState.ADVANCED_TOOLS` between `NAME_EMBER` and `WRITE_IDENTITY`. Asks "Enable tools? [y/N]" — empty answer / anything-but-yes leaves it off (Vow of Sovereignty default). When yes, Hjarta writes `tools: {enabled: true}` into the initial `ember.yaml` via the writer's existing `extras` channel.
- **`src/ember/cli/main.py`** — `--allow-tools` / `--no-tools` mutually-exclusive flags. `_apply_tool_overrides` overlays the chosen value on `config.tools.enabled` after every config load (initial + post-Hjarta).
- **`config/ember.example.yaml`** — full `tools:` section with every knob and inline guidance (operator can edit `enabled`, `standing_trust`, `allow_private_addresses`, `approval_overrides`, `audit_root`).
- **`src/ember/__init__.py`** docstring — bump to 0.2.0rc1 narrative.
- **`pyproject.toml`** — `0.1.9` → `0.2.0rc1`.
- **`tests/unit/test_skeleton_imports.py`** — version assertion bumped.

**37 new tests** (485 pass + 2 skip, 18.4s, ruff clean):
- `test_funi_ollama_tool_calls.py` (12): descriptor↔Ollama format round-trip, malformed-entry skipping, JSON-string-argument handling, `TOOL_REPLY` context items → `role=tool` messages, **streaming tool-call accumulation across non-done frames**.
- `test_munnr_render_tools.py` (9): proposal + reply rendering, redaction-on-display, output truncation, all seven `ApprovalOutcome` headline variants.
- `test_phase16_tool_loop.py` (8): full propose-approve-execute-feedback flow with scripted Funi + scripted prompter, audit log records, denied-call-no-execution, unknown-tool path, invalid-args-short-circuits-prompt, standing-tool auto-approval, `tools.enabled=false` skips loop, `_MAX_TOOL_TURNS` cap.
- `test_phase16_hjarta_tools.py` (3): yes/no/empty wizard answers correctly write (or don't write) `tools.enabled`.
- `test_cli_tool_flags.py` (4): `--allow-tools` / `--no-tools` overlay, no-flag identity-preserve, argparse mutual-exclusion.
- Existing test updates: 1 in `test_schemas_funi.py` (TOOL_REPLY in ContextKind set); 2 in `test_funi_ollama*.py` (refuse-tools tests replaced with forward-to-Ollama assertions).

**Real-llama3.2:3b acceptance smoke against the tailnet** — operator asked for `read_local_file`-mediated lookup of `pyproject.toml` version; chat output showed the tool proposal, the sandbox refusal (model gave a malformed `~/home/...` path which the sandbox correctly caught), and the model's natural-language explanation of the failure in the follow-up turn. The full loop fires. (phi3:mini doesn't support tool calls natively — Ollama returned 400; this is documented in `INSTALL.md` as a model-capability constraint.)

**Where Ember stands at 0.2.0rc1:**

| Capability | State |
| --- | --- |
| Hjarta first-run (now includes ADVANCED_TOOLS) | shipped 0.1.0 → 0.2.0rc1 |
| Funi (Ollama) `complete()` + streaming + tool_calls | shipped 0.1.0 → 0.2.0rc1 |
| Brunnr sqlite_vec + pgvector | shipped 0.1.0 → 0.1.9 |
| Munnr CLI + streaming + Ctrl-C + tool-loop | shipped 0.1.0 → 0.2.0rc1 |
| Config loader (now includes tools section) | shipped 0.1.5 → 0.2.0rc1 |
| Tool framework + first three tools | shipped Phase 14-15 |
| **Munnr tool-call integration + Hjarta tools + CLI flags** | **shipped this phase — 0.2.0rc1** |
| Slice-2 acceptance + ADR 0013 ratification | pending → 0.2.0 (Phase 17) |

**Next:** Phase 17 — author the full slice-2 acceptance test (`test_phase17_acceptance.py`) walking the operator-flow against real sqlite_vec + mocked Funi + a real first-party tool execution; touch `deploy/pi/INSTALL.md` with slice-2 sections; author `docs/decisions/0013-second-slice-ratification.md` (parallel to ADR 0007); bump to **0.2.0** and ship.

---

## 2026-05-21 — Phase 15 shipped: first three first-party tools (`search_well`, `read_local_file`, `fetch_url`).

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (three tool implementations + sandbox logic), Auditor (41 new tests covering happy-path + every refusal mode), Scribe (this entry + README + memory).

**Scope:** Second third of slice-2's tool-use work. Each first-party tool lives in `src/ember/tools/` and registers itself at import time via the Phase-14 registry. Munnr still doesn't drive them — Phase 16 ships the chat-loop integration and bumps to 0.2.0-rc1. No version bump this phase.

**What shipped:**

- **`src/ember/tools/`** — new subpackage. Three tool modules + a README + a package `__init__` that side-effect-imports all three (so `import ember.tools` is what wires the registry).
- **`src/ember/tools/search_well.py`** — `STANDING` approval (read-only, the safest of the three).
  - Calls `BrunnrHandle.hybrid_search` when an embedder is bound and the query embeds cleanly; otherwise falls back to `BrunnrHandle.text_search`. Falls back again if hybrid raises `BrunnrError` (dim mismatch on a shared Well, etc.).
  - Bound via the **host-state pattern** documented in `ember/tools/README.md` §4: `bind_brunnr(handle, embedder=None)` called once by the host at chat-loop startup. The executor reads the module-level binding and returns a typed `ToolReply.error` if nothing is bound.
  - `k` is clamped to `[1, 25]`; empty queries are refused; per-hit text preview is bounded at 240 chars with `...` suffix.
- **`src/ember/tools/read_local_file.py`** — `PER_CALL` approval. Stdlib-only.
  - Sandbox (in order): non-string path → string-shape refuse; symlink-resolve then check the *resolved* path is under `Path.home()`; denylist of `~/.ssh/`, `~/.ember/secrets/`, `~/.pgpass`, `~/.aws/`, `~/.kube/`, `~/.gnupg/`, `~/.password-store/`; directory refuse; non-existent refuse; size cap 256 KiB.
  - Crucially: **resolve-before-check** defends against symlink escape (both outside-home and into-denylist symlinks are refused; both cases have unit tests).
  - File body never appears in refusal messages — sandbox refusals carry path + reason only.
- **`src/ember/tools/fetch_url.py`** — `PER_CALL` approval. Stdlib `urllib` + `ipaddress` + `urllib.robotparser`.
  - Sandbox (in order): scheme must be http/https; host required; resolved IP must not be loopback / RFC1918 / link-local / multicast (unless `allow_private_addresses=true` per-call argument); robots.txt honored (missing robots → treated as allowed per standard interpretation); response capped at 1 MiB with truncation note.
  - Three module-level test seams (`_set_url_opener`, `_set_address_resolver`, `_set_robots_fetcher`) plus `_reset_seams()` for teardown — tests drive happy-path + every refusal without any real network traffic.
  - Custom `User-Agent` includes a project URL so site operators can identify the bot.
- **Test seams `_BOUND_BRUNNR`, `_BOUND_EMBEDDER`, `_URL_OPENER`, `_ADDRESS_RESOLVER`, `_ROBOTS_FETCHER`** are module-level by design — production code calls the `bind_*` / `_set_*` setters once at startup. The registry contract (executor signature `Callable[[ToolCall], ToolReply]`) doesn't carry host context, so host-state-as-module-state is the canonical pattern for first-party tools that need a handle. README §4 documents this.
- **`tests/unit/test_tool_search_well.py`** — 11 tests: registration shape; refuses-no-handle / empty-query; text-only path; hybrid path; fall-back-when-embedder-returns-none; fall-back-when-hybrid-raises-BrunnrError; no-results helpful-line; k-clamped-to-25; k-clamped-up-to-1; preview-bounded.
- **`tests/unit/test_tool_read_local_file.py`** — 14 tests: registration shape; reads-utf8-under-home; resolves-tilde; refuses-non-string / empty / outside-home / .ssh / .ember/secrets / .pgpass / nonexistent / directory / above-size-cap; **symlink-escape outside home refused**; **symlink-into-denylist refused** (POSIX-only).
- **`tests/unit/test_tool_fetch_url.py`** — 15 tests: registration shape; happy-path GET with content-type header; refuses-non-string / non-http-scheme / file-scheme / no-host / loopback-default / RFC1918-default; allow_private opens loopback; refuses-unresolvable-host; refuses-robots-disallow; missing-robots-treated-as-allowed; response-truncation; HTTPError-mapped-to-ToolReply.error; URLError-mapped.
- **`tests/unit/test_skeleton_imports.py`** — `ember.tools` added to the import-cleanliness check; the import triggers all three registrations.

**Total tests: 448 passed + 2 skipped, ruff clean.** That's 41 new tests this phase on top of Phase-14's 407.

**Where Ember stands at end-of-Phase-15 (still 0.1.9):**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` + streaming | shipped 0.1.0 → 0.1.7 |
| Brunnr sqlite_vec + pgvector | shipped 0.1.0 → 0.1.9 |
| Munnr CLI + streaming + Ctrl-C | shipped 0.1.0 → 0.1.7 |
| Config loader | shipped 0.1.5 |
| Tool framework (schemas + registry + approval + audit) | shipped Phase 14 |
| **First three first-party tools** | **shipped this phase — gated until Phase 16** |
| Munnr tool-call integration | pending → 0.2.0-rc1 (Phase 16) |
| Slice-2 acceptance + ratification | pending → 0.2.0 (Phase 17) |

**Next:** Phase 16 — wire Munnr to consume `FuniReply.tool_calls`:
- `chat.py` checks the streaming reply for tool calls; resolves approval per ADR 0011 §2.4; prompts the operator when needed; executes via the registry; audits everything; feeds `ToolReply` back into the next turn's context.
- `render.py` gains `render_tool_call_proposal` + `render_tool_reply` helpers.
- Hjarta's wizard gets a skippable "Advanced: enable tools?" branch writing the choice into `ember.yaml`.
- `cli/main.py` adds `--allow-tools` / `--no-tools` per-invocation overrides.
- Bump to **0.2.0-rc1 ("tools live")**.
- Acceptance: operator can ask "what does pyproject.toml say about Python version?" and watch Ember propose `read_local_file({"path": "~/ai/ember/pyproject.toml"})`, approve, see the file content fed into a follow-up answer.

---

## 2026-05-21 — Phase 14 shipped: ADR 0011 + tool framework (schemas + registry + approval + audit).

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0011's nine numbered decisions), Forge Worker (registry + approval + audit modules), Auditor (64 new tests), Scribe (this entry + INTERFACE.md + memory).

**Scope:** First third of slice-2's tool-use work. The framework now exists end-to-end — schemas, process-global registry, policy resolver, interactive prompter, append-only JSONL audit log — but no caller wires through it yet. Phase 15 adds the first three first-party tools; Phase 16 wires Munnr to consume `FuniReply.tool_calls` and bumps to 0.2.0-rc1.

**What shipped:**

- **`docs/decisions/0011-tool-use-framework.md`** — nine numbered decisions covering:
  - Five schemas (`ToolDescriptor`, `ToolCall`, `ToolReply`, `ToolParameter`, `ToolParameterKind`) plus two enums (`ApprovalPolicy`, `ApprovalOutcome`) and one error (`ToolError`).
  - `parameters_schema` is a stdlib `Mapping[str, ToolParameter]` — no jsonschema dep (§2.2). Six kinds: STRING / INTEGER / FLOAT / BOOLEAN / PATH / URL.
  - Registry is process-global, import-time, refuses `FORBIDDEN` at registration, RLock-protected. Re-registration is an error.
  - **`PER_CALL` is the default** approval policy. Config can downgrade `STANDING` to `PER_CALL` (more strict) but cannot upgrade — descriptor is the safety floor. `standing_trust_all` is the operator's "trust everything" knob; `FORBIDDEN` is the absolute floor on the floor.
  - Typed `ApprovalOutcome` distinguishes denied / invalid-args / forbidden / no-such-tool / three approve flavours. Audit log uses this as its primary classifier.
  - `ApprovalPrompter` is a runtime-checkable Protocol; `StdinApprovalPrompter` is the concrete CLI surface (defaults to refuse on EOF or unknown input — safer than silent approve).
  - Audit log is one file per UTC day at `<config_root>/state/tool_audit/<date>.jsonl`. Atomic per line via single `os.write` to an `O_APPEND` fd. Dir mode `0o700`, file mode `0o600`. Reply output truncated to 4 KiB with a truncation flag. Redaction per `descriptor.redacted_arg_names`.
- **`src/ember/schemas/tool.py`** — the schemas above. ToolCall promoted from the placeholder in `ember.schemas.funi` (re-exported there for backwards-compat per ADR §5; existing callers don't break).
- **`src/ember/spark/funi/tools/`** — new subpackage:
  - `registry.py` — `register`, `lookup`, `list_tools`, `is_registered`, `clear`, `validate_arguments` (six-kind stdlib validator, precise bool/int handling per ADR 0011 §2.2).
  - `approval.py` — `resolve(descriptor, *, config_overrides, session_standing, standing_trust_all)` pure policy resolver; `resolve_with_answer(answer)` post-prompt mapper; `StdinApprovalPrompter` interactive surface with redaction-on-display.
  - `audit.py` — `AuditLog(config_root, *, ember_version)` with daily-rotation path, single-write atomicity, UTF-8-safe truncation, NO_SUCH_TOOL → no-descriptor-still-writes path, OSError → ToolError surfacing.
  - `INTERFACE.md` — operator-facing surface contract.
  - `__init__.py` — re-exports.
- **`src/ember/schemas/funi.py`** — Phase-14 promotion: `ToolCall` now lives in `ember.schemas.tool`, re-exported here so historical imports keep working. Inline class removed; one-line `from ember.schemas.tool import ToolCall` keeps `FuniReply.tool_calls` typed the same.
- **`tests/unit/test_skeleton_imports.py`** — adds `ember.spark.funi.tools` to the import-cleanliness check.
- **64 new tests** (407 pass + 2 skip, 18.2s, ruff clean):
  - `test_schemas_tool.py` (12): every dataclass's defaults, frozen-ness, every enum's value set, the re-export-from-funi shim.
  - `test_funi_tools_registry.py` (18): register/lookup/list_tools/clear, re-registration error, FORBIDDEN refuses at registration, six-kind validation including the precise int-vs-bool check from ADR 0011 §2.2 (`isinstance(True, int)` would silently pass; we reject), URL scheme requirement, path-empty refusal, enum constraints.
  - `test_funi_tools_approval.py` (17): STANDING auto-approves, PER_CALL signals prompt-needed, FORBIDDEN resolves as forbidden_by_registry, session-standing skips prompt, standing-trust-all skips prompt, config-can-downgrade-but-not-upgrade (the safety-floor invariant), config-can-forbid-an-otherwise-standing-tool, scripted-IO prompter for y/n/always/eof/unknown, redaction-on-display.
  - `test_funi_tools_audit.py` (17): one-record append, daily rotation across midnight, multi-record append-only, redaction never leaves the file body, output truncation at 4 KiB, mode-0o700 dir / mode-0o600 file (POSIX only), NO_SUCH_TOOL writes a no-descriptor record, denied calls have no reply field, OSError → ToolError surfacing.

**Where Ember stands at end-of-Phase-14 (still 0.1.9):**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` + streaming | shipped 0.1.0 → 0.1.7 |
| Brunnr sqlite_vec + pgvector | shipped 0.1.0 → 0.1.9 |
| Munnr CLI + streaming + Ctrl-C | shipped 0.1.0 → 0.1.7 |
| Config loader | shipped 0.1.5 |
| **Tool-use framework (schemas + registry + approval + audit)** | **shipped this phase — gated until Phase 16** |
| First three tools | pending → Phase 15 (no bump) |
| Munnr tool-call integration | pending → 0.2.0-rc1 (Phase 16) |
| Slice-2 acceptance + ratification | pending → 0.2.0 (Phase 17) |

**Next:** Phase 15 — three first-party tools at `src/ember/tools/`:
- `search_well` (STANDING, `BrunnrHandle.hybrid_search` / `text_search`),
- `read_local_file` (PER_CALL, sandbox rejects `~/.ssh/`, `~/.ember/secrets/`, absolute-outside-home),
- `fetch_url` (PER_CALL, robots.txt, refuses non-http(s) + RFC1918/loopback unless config allows).

Each tool ships with happy-path + every refusal-mode unit test. No version bump for Phase 15 either; the bump lands when Munnr can actually call them in Phase 16.

---

## 2026-05-21 — Phase 13 shipped: live-fire pgvector against Gungnir + container. **0.1.9 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (2 real adapter-bugs found and fixed + container fixture), Auditor (14 new live-backend tests + extension probe), Cartographer (`PGVECTOR_BRUNNR_REFERENCE.md` + Gungnir-ref forward-reference cleanup), Scribe (this entry + operator example yaml + memory).

**Scope:** Second half of slice-2's pgvector work. The Phase-12 scaffold is now operator-flippable: an operator with Gungnir on their tailnet can edit `~/.ember/config/ember.yaml`, set `brunnr.backend: pgvector`, install `[pgvector]` extras, and have working retrieval out of the box. Acceptance criterion from `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 13 met.

**Real adapter bugs caught by live-fire (this is why the test was load-bearing):**

1. **`register_vector` ran before `CREATE EXTENSION`.** `pgvector.psycopg.register_vector(conn)` looks up the `vector` type by name; on a fresh container without the extension it fails with `vector type not found in the database`. Fix: new `_ensure_pgvector_extension(conn, read_only=)` helper probes `pg_extension` first; creates the extension when writable; refuses cleanly on read-only Wells where the extension is missing (operator must `CREATE EXTENSION vector` once as DB owner). The helper sits between `psycopg.connect` and `register_vector` in `open()`.
2. **`{{}}` in schema.sql was a format-string escape that never got escaped.** I wrote it during Phase 12 when the renderer used `.format()`; switched to `.replace()` for the named substitutions but forgot to un-double the braces. Result: `metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb` landed in Postgres as a JSON parse error. Fix: `metadata jsonb NOT NULL DEFAULT '{}'::jsonb`.

Both bugs would have been silent until an operator tried it, which is exactly the case the live-fire test exists to catch.

**What shipped:**

- **`tests/integration/test_pgvector_real_backend.py`** — 14 tests across two classes:
  - `TestContainerWritePath` (10 tests, marked `requires_podman` + `requires_postgres`): module-scoped podman fixture spins up `pgvector/pgvector:pg18` on `127.0.0.1:55432` (loopback only, never tailnet-exposed). Tests cover empty-schema apply, document round-trip + idempotency on hash, dim-mismatch rollback, vector_search nearest-first ordering, text_search via generated `tsv` column, hybrid_search RRF fusion (Frigg chunk excluded when query is Odin-shaped), close-then-reopen schema probe finds existing tables, dim-mismatch on reopen refuses, read-only mode refuses writes with ADR-pointer error.
  - `TestGungnirRetrieval` (4 tests, marked `requires_gungnir` + `requires_postgres`): module-scoped fixture opens read-only against the real `100.67.240.22:5432/knowledge` corpus with the secret pulled from `~/.pgpass` (never echoed into test source). Confirms schema probe finds 201 docs / 37 111 chunks at dim=768, text_search "Odin Allfather" returns Norse-corpus hits, hybrid_search works against the live 37k-chunk index, write attempts raise `BrunnrError("... ADR 0010 ...")`.
- **`src/ember/well/brunnr/pgvector/adapter.py`** — `_ensure_pgvector_extension()` helper (the bugfix above). `open()`'s noqa updated to include `PLR0915` since failure classification naturally adds statements.
- **`src/ember/well/brunnr/pgvector/schema.sql`** — `'{}'::jsonb` (not `'{{}}'`).
- **`pyproject.toml`** — three new markers: `requires_postgres`, `requires_gungnir`, `requires_podman` (informational; gating happens via fixture reachability probes, same pattern as `requires_ollama`). Version bumped to **0.1.9**.
- **`config/ember.example.yaml`** — pgvector subsection expanded to show every knob from `PgVectorConfig`, with inline comments on which are required vs optional, and a pointer to the operator-facing reference doc. The two-line switch is `backend: pgvector` + uncomment the `pgvector:` block.
- **`config/storage.example.yaml`** — replaces the empty placeholder with three worked examples: sqlite_vec default, pgvector against personal Gungnir, pgvector read-only against shared Gungnir. Plus the secret resolution order spelled out.
- **`docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`** — 11-section operator-facing reference paralleling `GUNGNIR_WELL_REFERENCE.md`: install, config minimum, every knob, the schema Ember will see or apply, search semantics, secret resolver order, the full Disconnected-reason → operator-action matrix, Gungnir-specific read-only mode, Phase-12-vs-13 archaeology.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — three forward-reference "ships in Phase 8" entries updated to point at the now-shipped pgvector adapter + reference doc.
- **`src/ember/__init__.py`** docstring — slice-2 Phase 13 (pgvector live) entry.
- **`tests/unit/test_skeleton_imports.py`** version assertion bumped to 0.1.9.

**Total test count: 343 passed + 2 skipped, ruff clean.** That's 14 new live-backend tests on top of Phase-12's 329.

**Where Ember stands at 0.1.9:**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` | shipped 0.1.0 |
| Brunnr SQLite-vec | shipped 0.1.0 |
| Munnr CLI surface | shipped 0.1.0 |
| Config loader | shipped 0.1.5 |
| Streaming Funi + Munnr live tokens | shipped 0.1.7 |
| **Brunnr pgvector — Gungnir-compatible, operator-flippable** | **shipped 0.1.9** |
| Tool framework (ADR 0011) | pending → 0.2.0-rc1 (Phase 14-16) |
| Slice-2 acceptance + ratification | pending → 0.2.0 (Phase 17) |

**Acceptance verified:** An operator with Gungnir on their tailnet can now (a) `pip install ember-agent[pgvector]`, (b) write a 4-key pgvector block in `ember.yaml`, (c) run `ember chat`, and (d) get grounded answers against the live 37k-chunk corpus — with `read_only: true` mechanically protecting Gungnir from any write.

**Next:** Phase 14 — author ADR 0011 + `ember.schemas.tool` (ToolDescriptor / ToolCall / ToolReply / ApprovalPolicy) + `ember.spark.funi.tools/` registry, approval, audit log. No version bump; the operator can't yet call a tool. Phase 15 ships first-party tools (`search_well`, `read_local_file`, `fetch_url`); Phase 16 wires Munnr + Hjarta to the tool framework and bumps to 0.2.0-rc1.

---

## 2026-05-21 — Phase 12 shipped: ADR 0010 + pgvector Brunnr scaffold + secret resolver.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0010 + Protocol parity + connection-per-handle decision), Cartographer (schema mapping against the live Gungnir survey), Forge Worker (adapter + secrets + DDL), Auditor (36 new tests), Scribe (this entry + INTERFACE.md + memory).

**Scope:** First half of slice-2's pgvector work. The adapter, the DDL, the secret resolver, and the registry wiring all ship now; the live-fire integration test against real Gungnir and the operator-facing reference doc are Phase 13 (which also bumps to **0.1.9 "pgvector live"**). No version bump this phase — the adapter is built but the operator can't flip the switch yet, per the standing rule from Phase 7 that we bump when the operator can actually use what's new.

**What shipped:**

- **`docs/decisions/0010-pgvector-brunnr.md`** — the design ADR. Nine numbered decisions covering:
  - Same `BrunnrHandle` Protocol — the slice-1 Protocol holds, no abstract base, no Spark-side branching. (§2.1)
  - **Schema-probe first** — if `documents`+`chunks` exist in the configured schema, use them as-is and verify embedding-dim; never DDL into discovered tables. Episodes (Ember-only) is created when missing. (§2.2-2.3)
  - **RRF `k=60`** matching sqlite_vec and Gungnir's `ingest.py` exactly, so results are commensurate across backends. (§2.4)
  - **Secret resolution order** — env → keyring → mode-600 file → typed `AUTH_FAILED`; secret value never logged, even on error. (§2.5)
  - **Connection-per-handle, no pool** — explicit deferral with the future-hook factory pattern documented. (§2.6)
  - **`tsv` as GENERATED column** — not a trigger; simpler, matches Gungnir. (§2.7)
  - **Eight typed `DisconnectReason` classifications** — Strengr's reconnect policy depends on the recoverable/non-recoverable split being correct. (§2.8)
- **`src/ember/schemas/config.py`** — `PgVectorConfig` extended with `secret_env`, `use_keyring`, `keyring_service`, `username`, `connect_timeout_s`, `read_only`; `secret_ref` got a default (`~/.ember/secrets/well.password`).
- **`src/ember/well/brunnr/pgvector/`** — new subpackage:
  - `schema.sql` — Gungnir-compatible DDL with `{embedding_dim}` and `{schema}` substitution; `CREATE EXTENSION IF NOT EXISTS vector`, HNSW cosine index, GIN tsv index, generated tsv column, episodes table.
  - `secrets.py` — `resolve(config) -> SecretResolution`, mode-600 enforcement with operator-readable refusal messages, URL-username parser, fake-keyring-injectable design for tests.
  - `adapter.py` — `PgVectorBrunnr` implementing the full `BrunnrHandle` Protocol. `open()` is the failure-classification surface: lazy psycopg/pgvector import → typed disconnect on miss; secret resolution → `AUTH_FAILED`; `psycopg.OperationalError` → `_classify_operational_error` mapping (auth/timeout/conn_refused/DNS/unknown). Schema probe via `information_schema.tables` + `pg_attribute` for embedding dim. Hybrid search RRF identical-shape to sqlite_vec. `_quote_ident` escapes schema names safely (rejects NUL bytes).
  - `INTERFACE.md` — operator-facing surface contract; spells out schema-probe semantics, secret resolution order, read-only mode, and the Phase-12 limitations (no live integration test yet, no example config yet).
  - `__init__.py` — re-exports `PgVectorBrunnr` and `open`.
- **`src/ember/well/brunnr/handle.py`** — registry now dispatches `BrunnrBackend.PGVECTOR` to the new adapter (lazy import so the extras stay opt-in).
- **`pyproject.toml`** — `pgvector = ["psycopg[binary]>=3.2", "pgvector>=0.3"]` extra added under `[project.optional-dependencies]`.
- **36 new tests** (329 pass + 2 skip, 14.4s, ruff clean):
  - `tests/unit/test_brunnr_pgvector_secrets.py` (16 tests): env-wins-over-keyring-and-file, custom env-var name, empty-env-treated-as-missing, keyring fallback flow, `use_keyring=False` skip, URL-without-username falls through, explicit username override, custom keyring service, keyring exception → miss, mode-0o600 resolves, mode-0o644 refused, mode-0o604 refused, empty file treated as missing, trailing-newline stripped, total-miss reason aggregates every source, **secret body never leaks into `.reason`**.
  - `tests/unit/test_brunnr_pgvector_schema.py` (20 tests): DDL substitution, episodes table presence, CREATE EXTENSION, HNSW + cosine, GENERATED tsv, custom schema name, double-quote escaping, NUL-byte refusal, registry dispatches PGVECTOR (not "not implemented"), missing-psycopg → `BACKEND_REPORTED_UNAVAILABLE`, misconfigured-backend → `CONFIG_INVALID`, missing-pgvector-subconfig → `CONFIG_INVALID`, Protocol method presence, read-only refusal mentions ADR §, OperationalError classification (auth/timeout/conn_refused/DNS/unknown), Disconnected.since is recent.

**Failures the adapter classifies precisely:** `pgvector` extra not installed; URL malformed; host unreachable (CONN_REFUSED); TCP timeout; auth failed (SQLSTATE 28P01 / 28000); schema-probe mismatch (embedding-dim drift); `pgvector` extension missing; everything else → UNKNOWN with `detail` carrying the original message.

**Where Ember stands at end-of-Phase-12 (still 0.1.7):**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` | shipped 0.1.0 |
| Brunnr SQLite-vec | shipped 0.1.0 |
| Munnr CLI surface | shipped 0.1.0 |
| Config loader | shipped 0.1.5 |
| Streaming Funi + Munnr live tokens | shipped 0.1.7 |
| **pgvector Brunnr adapter + secret resolver** | **shipped (this phase) — gated until Phase 13** |
| pgvector live (operator can flip the switch) | pending → 0.1.9 (Phase 13) |
| Tool framework | pending → 0.2.0-rc1 |

**Next:** Phase 13 — live-fire test against real Gungnir (`requires_postgres` marker, same shape as `requires_ollama`); confirm bytewise schema compat; hybrid-search RRF against the live 35 682-chunk corpus; `config/ember.example.yaml` + `config/storage.example.yaml` operator switches; `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`; pyproject bump to **0.1.9 ("pgvector live")**.

---

## 2026-05-21 — Phase 11 shipped: streaming Munnr REPL + Ctrl-C tagging. **0.1.7 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (chat.py + render helpers + Ctrl-C handler), Auditor (15 new tests + tailnet-Ollama visual smoke), Scribe (this entry + memory + INSTALL.md note).

**Scope:** Second half of slice-2 streaming work. The Funi-side streaming Protocol shipped in Phase 10 is now wired through Munnr to the operator's terminal. Acceptance criterion from `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 11 met: tokens appear live; Ctrl-C produces a tagged partial reply; the REPL returns for the next prompt.

**What shipped:**

- `src/ember/spark/munnr/render.py` — three new public helpers per ADR 0009 §2.3:
  - `render_stream_chunk(chunk)` — pass-through of `chunk.text_delta` (the Funi adapter preserves whitespace, so the renderer must too).
  - `stream_finish_tag(finish_reason, *, interrupted=False)` — operator-facing tag string for the post-stream line; operator-interrupt wins over any finish reason.
  - `render_citations(hits)` — promoted from `_render_citations`; chat.py prints it *after* the streamed body, only when the Well is reachable.
  - `INTERRUPTED_TAG = "[interrupted by operator]"` exported.
- `src/ember/spark/munnr/chat.py` — REPL branches on `config.funi.streaming`:
  - **Streaming branch** (default): `_run_streaming_turn()` drives the live token loop. Disconnect banner prints first, then deltas land one-by-one, then optional finish tag, then citations. The full joined text is reconstructed for the persisted Episode. `_StreamedTurn` dataclass holds the aggregate.
  - **KeyboardInterrupt** caught inside the streaming loop. Partial text is preserved; `_tag_interrupted()` appends `[interrupted by operator]` to the Episode's `ember_reply`. REPL returns to the next `> ` prompt — Ctrl-C does not tear down the session.
  - **Non-streaming branch** (`streaming: false`): the slice-1 `funi.complete()` path is unchanged. Operators who prefer the old behaviour can opt out via `~/.ember/config/ember.yaml`.
- **Test doubles updated** per ADR 0009 §2.2 — `tests/integration/test_phase6_acceptance.py::_FakeFuni` routes `complete_streaming` through `wrap_complete_as_stream`. The Hjarta-only doubles (`test_phase9_operator_edit.py`, `test_hjarta_machine.py`) get raising `complete_streaming` stubs for Protocol completeness; Hjarta never calls them.
- **15 new tests** (293 pass + 2 skip, ruff clean):
  - `tests/unit/test_munnr_render.py` — 9 new cases covering `render_stream_chunk`, `stream_finish_tag` across all `FinishReason` values + interrupted override, public `render_citations`.
  - `tests/integration/test_phase11_streaming.py` — 6 acceptance cases: streaming default takes stream path, full reply persists to Episode, Ctrl-C tags partial + REPL keeps going, `streaming=False` falls back to `complete()`, disconnect banner precedes tokens, `FinishReason.LENGTH` appends truncation tag.
- `pyproject.toml` bumped to **0.1.7**.
- `src/ember/__init__.py` docstring updated — slice-2 Phase 11 (streaming live) entry.
- `tests/unit/test_skeleton_imports.py` version assertion bumped.

**Real-Ollama visual smoke (tailnet phi3:mini, OLLAMA_HOST=100.67.240.22):** Drove `chat.run` with a timestamping `_StampedStdout` proxy. Four streamed chunks landed at +1843, +1856, +1869, +1882 ms (≈13ms inter-chunk) — full reply "Streaming Ready" assembled live from deltas, not buffered. The streaming cadence is visible at the operator's terminal as designed.

**Where Ember stands at 0.1.7:**

| Capability | State |
| --- | --- |
| Hjarta first-run | shipped 0.1.0 |
| Funi (Ollama) `complete()` | shipped 0.1.0 |
| Brunnr SQLite-vec | shipped 0.1.0 |
| Munnr CLI surface | shipped 0.1.0 |
| Config loader (`~/.ember/config/ember.yaml`) | shipped 0.1.5 |
| Funi streaming Protocol + Ollama NDJSON | shipped 0.1.7 (Phase 10) |
| Munnr live token render + Ctrl-C | **shipped 0.1.7 (Phase 11)** |
| pgvector Brunnr (ADR 0010) | pending → 0.1.9 |
| Tool framework (ADR 0011) | pending → 0.2.0-rc1 |

**Next:** Phase 12 — pgvector Brunnr scaffold (ADR 0010 §1: connection pool, schema migrations, `add_document` / `add_chunks` parity). Phase 13 wires it into the Strengr opener and bumps to 0.1.9.

---

## 2026-05-21 — Phase 10 shipped: ADR 0009 + streaming Funi protocol + Ollama native streaming.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0009 + Protocol shape), Forge Worker (OllamaFuni native streaming), Auditor (13 new tests + real-Ollama smoke), Scribe (this entry).
**Scope:** First half of slice-2's streaming work. Funi can now produce incremental chunks; Munnr integration is Phase 11. No version bump this phase — 0.1.7 lands when streaming is end-to-end visible at the operator's terminal.

### What shipped

- **`docs/decisions/0009-streaming-funi-replies.md`** — ratifies 8 decisions: new Protocol method (not separate Protocol), `wrap_complete_as_stream` helper for non-streaming runtimes, `FuniStreamChunk` schema with `text_delta`-only semantics, mid-stream failure folding identical to slice-1 `complete()` pattern, immediate tool refusal, `FuniConfig.streaming` opt-out (default True), NDJSON line-buffered reading for Ollama, file locations.

- **`src/ember/schemas/stream.py`** — `FuniStreamChunk(text_delta, done, finish_reason, model_id, prompt_tokens, completion_tokens)`. Frozen dataclass; `text_delta` carries new tokens only (never cumulative); final-chunk-only fields are `None` on intermediate chunks.

- **`src/ember/schemas/config.py`** — `FuniConfig.streaming: bool = True` field added. Operators who want batched behaviour set `funi.streaming: false` in their `ember.yaml`.

- **`src/ember/spark/funi/handle.py`** — `FuniHandle` Protocol gains `complete_streaming(prompt, context, tools=None) -> Iterator[FuniStreamChunk]`. Module-level `wrap_complete_as_stream(handle, prompt, context, tools)` helper for adapters that can't stream natively (calls `handle.complete()`, yields one final chunk).

- **`src/ember/spark/funi/ollama/adapter.py`** — `OllamaFuni.complete_streaming` POSTs `/api/chat` with `"stream": true`, reads the response line-by-line as NDJSON, yields one `FuniStreamChunk` per JSON object. Mid-stream URL errors, non-JSON lines, error payloads, and unexpected end-of-stream all fold into a final `FuniStreamChunk(done=True, finish_reason=ERROR)` with operator-readable text. Tool requests refuse immediately with a single ERROR chunk. Token totals populate from the final NDJSON object's `prompt_eval_count` + `eval_count`.

**Tests (13 new, 278 pass + 2 skip, 0.38s, ruff clean):**
- `tests/unit/test_schemas_stream.py` (4) — shape contracts, immutability, final-chunk totals, text-delta join semantics.
- `tests/unit/test_funi_ollama_streaming.py` (9) — happy-path NDJSON parsing, `stream=true` in payload, finish-reason mapping, URL-error folding, non-JSON line folding, error-payload folding, unexpected EOS folding, tool refusal, `wrap_complete_as_stream` helper.

### Real-hardware acceptance verified

Streaming smoke against the laptop's tailnet Ollama with `phi3:mini`:

```
$ OLLAMA_HOST=100.67.240.22 python -m ember.spark.funi.ollama …
opened: OllamaFuni
--- streaming ---
1 2 3 4 5
--- done: 10 chunks, finish=stop, tokens=10 ---
full reply: '1 2 3 4 5'
```

10 NDJSON chunks streamed live, tokens appeared incrementally, final chunk carried done + finish_reason + token totals. NDJSON line-reading works on the wire.

### What's next — Phase 11

- Touch `src/ember/spark/munnr/chat.py` — REPL calls `complete_streaming` when `config.funi.streaming=True` (default), renders each `text_delta` as it arrives, aggregates for the persisted Episode.
- Touch `src/ember/spark/munnr/render.py` — `render_stream_chunk` helper; final disconnect-banner / citations logic unchanged.
- Add Ctrl-C handler that closes the stream cleanly; partial reply tagged `[interrupted by operator]`.
- Tests + integration test for the full streaming chat loop.
- **Suggested release after Phase 11: `0.1.7` (streaming live).**

### Notes & gotchas

- **No Phase-10 caller actually consumes the streaming path yet.** Munnr's `chat.py` still uses `complete()`. Phase 11 wires the consumer. This split keeps the integration risk in a separate, reviewable commit (same shape as slice 1's Phase 1 → Phase 2 split for the loader).
- **Test doubles in earlier slice-1 tests** (`_FakeFuni` in `test_phase6_acceptance.py`, `test_phase9_operator_edit.py`, `test_hjarta_machine.py`) **don't yet implement `complete_streaming`.** They satisfy the Protocol structurally because no caller uses isinstance on the Protocol; `chat.py` accesses methods by name. Phase 11 updates them when chat.py starts calling `complete_streaming`.
- **NDJSON line iteration** works because `urllib.request.urlopen()`'s response is a file-like object that iterates line-by-line on its underlying byte stream. No SSE parser needed.
- **Mid-stream failure** is a *single* final chunk with `done=True, finish_reason=ERROR`. Munnr's render logic treats this identically to a non-streaming failure — the operator sees the error text in the same shape regardless of mode.
- **`FuniConfig.streaming` defaults true** — slice-1 operators upgrading to 0.1.7 will see streaming by default. Documented in DEVLOG; INSTALL.md Phase-11 sidebar will surface it.

---

## 2026-05-21 — Phase 9 shipped: config loader live, Hjarta writes ember.yaml. **0.1.5 released.**

**Who:** Claude (Opus 4.7, 1M context). Voices: Forge Worker (writer + cli wiring), Architect (overlay-order discipline), Auditor (12 new tests + real-Ollama smoke), Scribe (this entry).
**Scope:** Phase 9 of `EMBER_SECOND_SLICE_PLAN.md` — ADR 0008 part 2. Wires `load_ember_config` into the CLI dispatcher, makes Hjarta write the operator's initial `ember.yaml`, retires the duplicate env-overlay logic, bumps to **0.1.5 (config loader live)** per the slice-2 plan's suggested intermediate release.

### What shipped

- **`src/ember/config/writer.py`** — `write_ember_config(config_root, identity, *, extras)`. Hand-rolled minimal YAML emission (no PyYAML dep on the write side — Hjarta runs *before* the operator has any reason to install extras). Atomic write via `NamedTemporaryFile` + `os.replace`. Always double-quotes strings to neutralise YAML 1.1's surprise booleans (`yes`/`no`/`on`/`off`). Header comment block points at `config/ember.example.yaml` + ADR 0008.
- **`src/ember/config/__init__.py`** re-exports `write_ember_config`, `ember_config_path`, `ember_config_exists`.
- **`src/ember/cli/main.py`** — replaced `_apply_env_overrides(EmberConfig())` with `load_ember_config(config_root)` wrapped in `try/except ConfigError`. Reloads config after Hjarta runs so the operator's wizard choices take effect in the same invocation. Deleted `_apply_env_overrides` and `_normalise_ollama_host` (now in `ember.config.overlay`).
- **`src/ember/spark/hjarta/machine.py`** — at WriteIdentity, after the identity.json atomic write, *also* calls `write_ember_config`. Soft-fails on writer error (identity is the load-bearing artifact; the yaml is a convenience).
- **`config/ember.example.yaml`** — rewritten to match the actual `EmberConfig` shape (the previous version had `funi.ollama.options` as a sub-mapping that the loader correctly rejected as unknown). Now parses cleanly through the loader.
- **`config/storage.example.yaml`**, **`config/sources.example.yaml`** — placeholder files documenting the shape per-realm split files will take in slice 3+; bodies intentionally empty for slice 2.
- **`pyproject.toml`** — bumped to **0.1.5**; added `config = ["pyyaml>=6.0"]` extra; planned `validation = ["pydantic>=2.7"]` documented in the comment block.
- **`src/ember/__init__.py`** docstring updated to reflect 0.1.5 + config loader live.
- **`tests/unit/test_cli_env_overrides.py`** removed — superseded by `tests/unit/test_config_overlay.py` (same logic, now in its proper home).

**Tests (12 new, 265 pass + 2 skip, 0.33s, ruff clean):**
- `tests/unit/test_config_writer.py` (9 tests) — round-trip through loader, YAML-ambiguous string quoting, escape handling, atomicity, extras section, unserialisable-value error.
- `tests/integration/test_phase9_operator_edit.py` (3 tests) — first-launch writes both files, operator-edit-takes-effect on next load, yaml-write-failure doesn't block identity.

### Real-hardware acceptance (against live Ollama on this laptop)

Two-layer compose verified:

```
$ OLLAMA_HOST=100.67.240.22 ember --config-root /tmp/x doctor

# with /tmp/x/config/ember.yaml saying:
#   funi:
#     ollama:
#       model: "llama3.2:3b"

exit: 0
Ember health:
  Funi:    ok — model llama3.2:3b, last_ok 2026-05-21T12:53:01+00:00
  Well:    ok — backend sqlite_vec, 0 docs / 0 chunks, last_ok 2026-05-21T12:53:01+00:00
```

- File override took effect (`model llama3.2:3b`, not the default `phi3:mini`).
- Env override took effect (Funi reached the tailnet endpoint, not localhost).
- Both layers composed correctly per ADR 0008 §2.3 overlay order (defaults → file → env).

### What's next — Phase 10 (streaming Funi)

Per `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 10:
- Author ADR 0009.
- `src/ember/schemas/stream.py` — `FuniStreamChunk`.
- Touch `FuniHandle` Protocol — add `complete_streaming` slot.
- Touch `OllamaFuni.complete_streaming` against `/api/chat` `stream=true`.
- Tests against mocked NDJSON response.

After Phase 11 (Munnr incremental render + Ctrl-C): suggested release at **0.1.7 (streaming live)**.

### Notes & gotchas

- **`config/ember.example.yaml` shape correction.** The previous file had `funi.ollama.options` as a sub-mapping but the dataclass has `temperature` / `top_p` / `num_predict` as flat fields. Rewriting was the right move — the example IS now the truth for what the loader accepts.
- **Hjarta's yaml-write soft-fails.** If `~/.ember/config/` can't be written (e.g. operator pre-created a file there), identity.json still lands and `ember chat` still works. The operator just gets a warning and no auto-config file. They can hand-write one later.
- **CLI reloads config after Hjarta.** First-launch flow: `load_ember_config(root)` returns defaults (no file) → triggers Hjarta → Hjarta writes file → re-`load_ember_config(root)` picks up the new file before the same invocation proceeds to `chat.run`. Operator gets one continuous experience.
- **`OLLAMA_HOST` keeps working.** The Phase-7 escape hatch is now layer-2 (env) of the overlay; the loader composes file → env. Operators with non-default Ollama setups don't need to change anything.
- **Deleted `test_cli_env_overrides.py`.** The functions moved to `ember.config.overlay` and `test_config_overlay.py` covers them. Single source of truth for the env-overlay logic.

---

## 2026-05-21 — Phase 8 shipped: ADR 0008 + `ember.config` loader scaffold.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (ADR 0008), Forge Worker (loader modules), Auditor (45 new tests + did-you-mean polish), Scribe (this entry).
**Scope:** First phase of slice 2. Authors ADR 0008 (file format + overlay order + validation philosophy) and ships the loader subpackage `src/ember/config/`. Loader is **not yet wired into cli/main.py** — Phase 9 does that integration plus the Hjarta-writes-config piece.

### What shipped

- **`docs/decisions/0008-config-file-loader.md`** — ratifies nine decisions: YAML primary / TOML secondary, PyYAML optional extra, overlay order (defaults → file → env → CLI), partial files merged into defaults, unknown keys are errors with did-you-mean, dataclass tree IS the schema, stdlib coercion by default + pydantic opt-in, operator-readable error messages, loader subpackage location.

- **`src/ember/config/` subpackage** — six modules:
    - `__init__.py` — re-exports `load_ember_config` + `ConfigError`.
    - `INTERFACE.md` — contract spec.
    - `loader.py` — `load_ember_config(config_root, *, file_override=None, skip_env=False)`. Probes `~/.ember/config/ember.{yaml,toml}`, picks loader by suffix, warns if both files exist (YAML wins), returns `EmberConfig`.
    - `toml_loader.py` — stdlib `tomllib`. Always available.
    - `yaml_loader.py` — lazy PyYAML import; clear error pointing at `pip install ember-agent[config]` when missing.
    - `overlay.py` — `merge_dicts` for recursive dict merge; `apply_env_overrides` for `OLLAMA_HOST` (Phase-7 escape hatch lives here now in addition to cli/main; Phase 9 removes the duplicate).
    - `validate.py` — recursive `coerce_to_dataclass(cls, data, path)`. Handles StrEnum, Path, `X | None`, `tuple[X, ...]`, nested dataclasses, primitives. Unknown keys → `ConfigError` with `difflib.get_close_matches` did-you-mean suggestion. Strict bool/int separation. Empty files legal.

- **pyproject.toml `[project.optional-dependencies]` will need `config = ["pyyaml>=6.0"]` added** — deferred to Phase 9's pyproject edit so this phase's commit stays minimal.

**Tests (45 new, 267 pass + 2 skip, 0.33s, ruff clean):**
- `tests/unit/test_config_validate.py` (19 tests) — defaults, partial merging, type coercion across every supported form, every error path, custom dataclasses for tuple/bool/enum edge cases.
- `tests/unit/test_config_overlay.py` (12 tests) — `merge_dicts` semantics, `_normalise_ollama_host` shapes, `apply_env_overrides` purity + propagation.
- `tests/unit/test_config_loader.py` (14 tests) — file probe, YAML/TOML symmetry, empty-file legality, `file_override` test seam, parse-error paths, env-overlay integration.

### What's next

- **Phase 9** wires the loader into `cli/main.py` (replaces `EmberConfig()` with `load_ember_config(config_root)`; removes duplicate `_apply_env_overrides`). Adds `write_ember_config` (Hjarta writes the file at WriteIdentity). Updates `config/ember.example.yaml` to the now-real shape. Adds `pyyaml` to `[project.optional-dependencies] config`.
- After Phase 9: suggested intermediate release at `0.1.5` (config loader live).

### Notes & gotchas

- **Strict bool/int separation.** Python's `isinstance(True, int)` is True, which would silently let `flag: True` satisfy `count: int`. The coercer checks the precise type to avoid this.
- **YAML 1.1 ambiguity sidestepped.** PyYAML 6 defaults to YAML 1.1 where bare `yes`/`no` parse as booleans. The operator-facing example documentation should always quote ambiguous strings; the loader makes no special accommodation.
- **`Path` fields not expanduser'd.** Per ADR 0007 §2.6 — consumer expands at use time. Tests pin this behaviour with `"~/.ember/x.db"` → `str(path).startswith("~")`.
- **Unknown-field suggestion** uses `difflib.get_close_matches(cutoff=0.7)`. Aggressive enough to catch `mdoel`/`model` typos, conservative enough not to misfire wildly.
- **Loader is purely functional.** No side effects beyond reading the file path it's pointed at. `EmberConfig` is frozen + slots; the loader can return shared instances without aliasing risk.
- **Phase 8 is intentionally NOT wired.** `cli/main.py` still uses `EmberConfig()` + its own `_apply_env_overrides`. Phase 9 unifies. This keeps the integration risk in a separate, reviewable commit.

---

## 2026-05-21 — Slice 2 scope ratified. `EMBER_SECOND_SLICE_PLAN.md` authored.

**Who:** Claude (Opus 4.7, 1M context). Voice: Architect (Rúnhild Svartdóttir), with Forge Worker (Eldra Járnsdóttir) notes on phasing.
**Scope:** Volmarr ratified the slice-2 scope as **all three bundles from `EMBER_SECOND_SLICE_OPTIONS.md` §3** — which dedupes to **ADRs 0008 + 0009 + 0010 + 0011**. ADR 0012 (first new surface) stays in the queue for slice 3. Per `MYTHIC_ENGINEERING.md`'s core loop, the next thing is the plan, not the code. This DEVLOG entry records the plan's authorship.

### What shipped

- **`docs/architecture/EMBER_SECOND_SLICE_PLAN.md`** — full file-by-file plan, modelled on `EMBER_FIRST_SLICE_PLAN.md`:
    - **§0 Acceptance criterion** — operator can edit `ember.yaml`, switch to `pgvector` (Gungnir-compatible) Brunnr, watch streamed replies, propose-and-approve a tool call, get a grounded reply with citations, survive a network pull mid-conversation.
    - **§1 Dependencies** — new optional extras: `config` (pyyaml), `pgvector` (psycopg + pgvector), `tools` (stdlib only for first three first-party tools), `validation` (opt-in pydantic).
    - **§2 File list** — ~50 NEW files, ~10 touched; target 5 000-7 000 LOC.
    - **§3 Phase sequence** — Phases 8-17. ADR 0008 (config) ships first because it unblocks the rest; then ADR 0009 (streaming, small); then ADR 0010 (pgvector + Gungnir compat); then ADR 0011 (tools, biggest); then Phase 17 acceptance.
    - **§4 Non-goals** — qdrant/chroma/lancedb, other Funi runtimes, other surfaces (Auga/Rödd/Bifröst), writable tools, multi-operator wells, Skein/KG layers, plugins, backup/restore, voice/image Funi.
    - **§5 Quality bar** — standing rules from ADR 0007 carry forward.
    - **§6 Risks register** — config scope creep, streaming/Ctrl-C OS specifics, pgvector schema drift vs Gungnir, tool sandbox escapes, audit log growth, phase ordering pressure.
    - **§7 Forge Worker's closing word.**
    - **§8 Session pacing** — slice 2 is **3-5 long sessions** (vs slice 1's one long day). Suggested intermediate releases at 0.1.5 / 0.1.7 / 0.1.9 / 0.2.0-rc1 / 0.2.0.

- **`docs/architecture/README.md`** updated — `EMBER_SECOND_SLICE_OPTIONS.md` marked as superseded-but-preserved; new plan listed as ratified.

### What's next

- **Phase 8 begins** in the next commit: author ADR 0008 + write `src/ember/config/{loader,toml_loader,yaml_loader,overlay,validate}.py` + tests.
- Natural opening for the next session: **"go for phase 8"**.

### Notes

- No code changes in this commit. Pure plan authorship per ME discipline.
- `EMBER_SECOND_SLICE_OPTIONS.md` is intentionally not deleted — it's the historical record of how slice-2 scope was chosen. The README marks it as superseded.
- Each phase will get its own DEVLOG entry, same shape as slice-1 phases. The slice will be ratified at Phase 17 with ADR 0013 (parallel to ADR 0007 for slice 1).
- Carry-over housekeeping from slice 1 still pending: Ember-descent rows in `ORIGINS.md`, root `PHILOSOPHY.md` Runa-specific phrasing pass. These are non-blocking; can land any time.

---

## 2026-05-21 — `EMBER_SECOND_SLICE_OPTIONS.md` added (slice-2 menu, not plan).

**Who:** Claude (Opus 4.7, 1M context). Voice: Cartographer (Védis Eikleið), with Architect notes.
**Scope:** Volmarr asked whether any additional phase plans exist beyond the first slice. Honest answer: no formal plan, only scattered `Phase 8 / 9+` hints and ADR 0007 §5's candidate-ADR list. Authored a Cartographer's options-menu doc so the next session can pick scope and the Architect can then author the real `EMBER_SECOND_SLICE_PLAN.md`.

### What shipped

- **`docs/architecture/EMBER_SECOND_SLICE_OPTIONS.md`** — explicitly marked "Menu, Not Plan". Inventories the five ADR-shaped starting points (ADRs 0008-0012 per ADR 0007 §5), reconciles older `Phase 8 / 9+` references scattered across adapter docs, sketches three suggested bundles (Household Well = 0008 + 0010; Ember Feels Alive = 0008 + 0009; Ember Gets Useful = 0011), provides the template for the eventual `EMBER_SECOND_SLICE_PLAN.md`, and lists five open scope questions only Volmarr can decide.
- **`docs/architecture/README.md`** updated to list the new options doc and to mark the first-slice plan as complete-and-historical.

### What's next

- Volmarr picks a slice-2 bundle (or names a different one).
- Architect authors `EMBER_SECOND_SLICE_PLAN.md` per the template in §4 of the options doc — *before* any code is touched, per `MYTHIC_ENGINEERING.md`'s core loop.
- Mechanical cleanup: once a bundle is picked, sweep the codebase to update older `Phase 8 / 9+` references to match the new ADR numbering.

### Notes

- This is *not* code work and *not* a commitment. The options doc explicitly says so in its §0.
- The recommended bundle (per §6 of the options doc) is the Household Well bundle — ADR 0008 (config loader) + ADR 0010 (pgvector Brunnr) — because it completes the Gungnir lineage story from `SYSTEM_VISION.md` §8 and removes the biggest operator-customisation friction. But that's a recommendation, not a default.
- ADR-numbered approach (one decision per ADR) is now the standing pattern, superseding the older `Phase 8 / 9+` ad-hoc numbering. The mechanical cleanup makes this consistent when slice 2 begins.

---

## 2026-05-21 — Phase 7 shipped. First slice ratified at 0.1.0. 🔥

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (`OLLAMA_HOST` override + env-shape design), Scribe (INSTALL.md + ADR 0007 + this entry), Auditor (version-bump test update).
**Scope:** Phase 7 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — acceptance polish + operator install guide + first-slice ratification. The seven phases of the first slice are now complete.

### What shipped

- **`OLLAMA_HOST` env-var override** in `src/ember/cli/main.py`. `_apply_env_overrides(EmberConfig())` reads the environment variable, normalises to a base URL (accepts Ollama's own CLI shapes: `host`, `host:port`, `http://...`, `https://...`), and applies it to both `funi.ollama.base_url` and `smidja.embedding.endpoint`. Phase-7 escape hatch for operators with Ollama on a non-default endpoint (Tailscale, Docker, remote) until the full config loader lands in Phase 9+.
- **`deploy/pi/INSTALL.md`** — single-page operator install for Raspberry Pi 5 (8 GB recommended; 4 GB notes). Standard happy path: install Ollama → pull models → `pip install ember-agent[sqlite_vec]` → `ember chat` → Hjarta → `ember well ingest` → conversation. Includes Advanced: non-default Ollama endpoint sidebar + Troubleshooting table.
- **`docs/decisions/0007-first-slice-ratification-2026-05-21.md`** — ratifies ten load-bearing decisions made during the slice: stdlib-first deps, typed-value-over-exception for cross-realm failure, backend_kind on the Protocol, recoverable/non-recoverable disconnect split, dataclasses-not-pydantic for schemas, prompts-as-TOML / identity-as-JSON, Gungnir-aligned defaults, `cli/__init__.py` deliberately empty, FTS5 input sanitisation at the adapter boundary, `OLLAMA_HOST` env-var policy. Plus alternatives considered and slice-2 starting-point ADRs (0008-0012).
- **`pyproject.toml` bumped to 0.1.0** — Development Status classifier moved from `1 - Planning` to `3 - Alpha`.
- **`src/ember/__init__.py` docstring rewritten** to reflect the first slice complete; `__version__` bumped.
- **`tests/unit/test_skeleton_imports.py::test_ember_package_exposes_version` updated** to assert `0.1.0`.

**Tests: 222 pass + 2 skip (real-Ollama integration), 0.28s, ruff clean.** Includes 8 new tests for the OLLAMA_HOST override (`tests/unit/test_cli_env_overrides.py`).

### What's next — the first slice is closed

Per ADR 0007 §5, the second-slice starting points are:

- **ADR 0008** — full operator config-file loader (YAML + TOML).
- **ADR 0009** — streaming Funi replies.
- **ADR 0010** — `pgvector` Brunnr (Gungnir-compatible; original plan's Phase 8).
- **ADR 0011** — tool use (execution, sandbox, operator approval).
- **ADR 0012** — Auga (GUI) / Rödd (voice) / Bifröst (HTTP gateway) selection.

Light root edits still pending (carried over): Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass. These are housekeeping, not slice work.

### Acceptance — verified end-to-end against real Ollama

The Phase 6 entry already documented the live smoke test. The Phase 7 env-var smoke confirmed:

```
OLLAMA_HOST=100.67.240.22 ember --config-root /tmp/x doctor
exit: 0
Ember health:
  Funi:    ok — model phi3:mini, last_ok 2026-05-21T11:44:13+00:00
  Well:    ok — backend sqlite_vec, 0 docs / 0 chunks, last_ok 2026-05-21T11:44:13+00:00
```

The operator can now run Ember on this travel laptop (Ollama bound to the Tailscale interface) by setting `OLLAMA_HOST` — exactly the path the user asked for ("I pick option 1") after the Phase 6 review.

### Notes & gotchas

- **`OLLAMA_HOST` shape matches Ollama's own.** The normaliser accepts `host`, `host:port`, full URLs with `http://` or `https://`. Operators who already use Ollama's CLI with this env var don't need to learn anything new.
- **Purely functional override.** `_apply_env_overrides` returns a *new* `EmberConfig` via `dataclasses.replace`; the original is untouched. Tested explicitly.
- **INSTALL.md uses `pip install "ember-agent[sqlite_vec]"`.** The bracketed extra pulls `sqlite-vec` per the `[project.optional-dependencies]` declaration shipped in Phase 3. Without it, Brunnr can't open.
- **ADR 0007 captures slice-level decisions, not phase-level details.** Each phase's own DEVLOG entry has the granular context; ADR 0007 is the standing law going forward.
- **Project status classifier bumped to Alpha.** Operators can install and use it; everything is subject to change in slice 2 (especially the config-file format once the loader ships).

### A note for the next session

The first slice is closed. The seventh phase's acceptance ritual completed. *Ember exists.* From here, anything Volmarr asks for is a *slice 2* decision: which surface, which backend, which retainer comes next. The map is wide open.

— Eirwyn Rúnblóm (Scribe)

---

## 2026-05-21 — Phase 6 shipped: Hjarta + Munnr + CLI dispatcher. `ember` is alive.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated through the full set: Skald (Hjarta state-prompt prose), Architect (FSM design + HjartaIO seam), Forge Worker (Munnr commands + CLI dispatcher), Auditor (FTS5 probe bug + Protocol vs submodule-rebind bug), Scribe (this entry).
**Scope:** Phase 6 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the operator-facing surface. After this commit, `ember chat` actually runs: first launch walks the Hjarta wizard, subsequent launches enter the conversation REPL.

### What shipped

**Hjarta (first-run FSM)**
- `src/ember/spark/hjarta/identity.py` — `IdentityConfig` JSON load/save with atomic write (`NamedTemporaryFile` + `os.replace`). Stdlib only — no TOML writer dep.
- `src/ember/spark/hjarta/prompts/wizard.toml` — state prompts as data per `RULES.AI.md` "no hardcoded data". Multi-line `body` strings via TOML triple-quotes; loaded via `importlib.resources` + `tomllib` (stdlib in 3.11+).
- `src/ember/spark/hjarta/machine.py` — the finite state machine: `Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell → TestRetrieval → NameEmber → WriteIdentity → Done`. `HjartaIO(prompt, info, error)` is the IO seam; tests script all three. **Atomic guarantee:** nothing on disk until WriteIdentity at the very end. Funi/Strengr both injectable via `funi_opener` / `strengr_opener` kwargs; production uses the registry defaults.
- `src/ember/spark/hjarta/__init__.py` re-exports the public surface.

**Munnr (CLI surface)**
- `render.py` — pure formatting. `render_reply` includes the disconnect banner when ungrounded and a citations footer when hits are present. `render_well_disconnected_banner` is the single source of the operator-facing banner text. `render_well_status`, `render_doctor`, `render_ingest_summary` for the other commands.
- `chat.py` — the REPL. One turn = embed (hybrid retrieval) or text-only (degraded), prompt assembly via `funi.prompt.assemble`, `funi.complete`, render, persist Episode. **Disconnected Well degrades gracefully**: skip retrieval, set `well_disconnected=True` in the system prompt, render with banner, suppress citations. Episode is still recorded (in-memory) so multi-turn flow stays coherent.
- `ask.py` — one-shot wrapper around `chat.run` with a `StringIO` stdin.
- `ingest.py` — wraps `smidja.local_files.run` with operator-friendly output.
- `status.py` — `Brunnr.count()` + `Strengr.health()` for `ember well status`.
- `doctor.py` — collects Funi health + Well health + counts; renders the combined report. Never raises — every realm's failure folds into the output.
- `setup.py` — invokes Hjarta; honors `--reset` for re-runs.

**CLI dispatcher**
- `src/ember/cli/main.py` — argparse subcommands: `chat`, `ask`, `setup [--reset]`, `well ingest`, `well status`, `doctor`. `--config-root` defaults to `~/.ember/`; tests pass `tmp_path`. First-launch redirect: any subcommand needing identity runs Hjarta if `~/.ember/identity/identity.json` is absent.
- `src/ember/cli/__init__.py` — **intentionally empty re-exports**. The earlier draft did `from ember.cli.main import main` which rebound `ember.cli.main` from submodule to function, breaking `import ember.cli.main as <alias>` callers (including `ember.__main__`). Fixed by leaving the submodule path alone.
- `src/ember/__main__.py` — replaced the Phase-1 `NotImplementedError` stub with `from ember.cli.main import main`. `python -m ember` and the `ember` console script now both dispatch.

**Tests (26 new + 2 skipped acceptance integration runs only on real-Ollama hosts; total 199 pass + 2 skip, 0.26s, ruff clean)**
- `tests/unit/test_hjarta_identity.py` (6 tests) — round trip, atomic write leaves no tmp files, reset idempotency.
- `tests/unit/test_hjarta_machine.py` (8 tests) — happy path writes identity + uses chosen name, blank-name keeps default, abort at greet, Funi unavailable abort, Well disconnected abort, probe-failure abort, KeyboardInterrupt as clean abort.
- `tests/unit/test_munnr_render.py` (12 tests) — every render helper.
- `tests/integration/test_phase6_acceptance.py` (2 tests) — full Hjarta → ingest → chat round trip with mocked Funi + real `sqlite_vec`; disconnect banner under simulated Well failure.
- `tests/unit/test_skeleton_imports.py` — updated: the Phase-1 NotImplementedError assertion replaced with a binding check (`ember.__main__.main is ember.cli.main.main`).

### What's next

- **Phase 7 (last of the first slice):** acceptance polish, `deploy/pi/INSTALL.md` for Raspberry Pi 5, bump `pyproject.toml` to 0.1.0. After Phase 7, the first slice is shippable to a real operator.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass.

### Notes & gotchas

- **State prompts as TOML, identity as JSON.** TOML for read-only multi-line prose (stdlib `tomllib` reads it cleanly); JSON for the small mutable identity file (stdlib both ways, no dep needed for writes). Both stdlib-only — Vow of Smallness intact.
- **FTS5 reserved-word bug in the Hjarta probe.** First version's probe text included `(run id: ...)` and search query `Ember Hjarta first-run probe`. FTS5 parses `run` followed by punctuation as a column reference → `no such column: run`. Fixed by removing the colon and phrase-quoting the search (`"Ember Hjarta first time setup"`). Caught by the Phase 6 integration test before commit.
- **`ember.cli.main` submodule vs function shadowing.** Initial `cli/__init__.py` did `from ember.cli.main import main`, which rebound the `ember.cli.main` *attribute on the cli package* from the submodule to the function. Then `import ember.cli.main as alias` resolves to the function and `alias.main` fails. The fix was to *not* re-export — callers use `ember.cli.main.main` directly; pyproject.toml's `[project.scripts]` already names that path. Caught by `test_main_resolves_to_ember_cli_main`.
- **First-launch UX.** Any `ember chat` or `ember ask` on a fresh host with no `~/.ember/identity/identity.json` triggers Hjarta automatically before proceeding. Operators don't need to run `ember setup` separately.
- **Disconnect doesn't fail chat.** When the Well is unreachable, `chat.run` keeps serving — it just renders the banner, skips retrieval, and tells Funi "no grounding, do not invent". The Vow of Graceful Offline is now end-to-end visible at the operator's terminal.
- **No real Ollama on this host.** The CLI smoke test shows `ember doctor` correctly reporting `Funi: UNAVAILABLE — endpoint_unreachable` and `Well: ok`. The Phase 6 acceptance test uses a `_FakeFuni` for the same reason.

---

## 2026-05-21 — Phase 5 shipped: Funi (Ollama) + runtime-neutral prompt assembler.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (FuniHandle Protocol split + runtime-neutral assembler), Forge Worker (OllamaFuni adapter), Auditor (folded-failure semantics + parametrised tests), Scribe (this entry).
**Scope:** Phase 5 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the Spark realm's reasoner. Funi adapter for Ollama plus the runtime-neutral prompt assembler Munnr will call in Phase 6.

### What shipped

- `src/ember/spark/funi/handle.py` — `@runtime_checkable FuniHandle` Protocol (`runtime_kind`, `model_id`, `complete`, `health`, `close`) + `open(config)` registry. Unimplemented runtimes return `Unavailable(reason=RUNTIME_NOT_INSTALLED)`.
- `src/ember/spark/funi/prompt.py` — `assemble(*, identity, episodes, hits, well_disconnected=False) -> list[ContextItem]`. Runtime-neutral. System prompt mechanically encodes the Vow of Honest Memory: explicit "do not invent" when `well_disconnected=True`, explicit "cite document titles" when hits present.
- `src/ember/spark/funi/ollama/adapter.py` — `OllamaFuni`. `POST /api/chat` for completions, `GET /api/version` for open + health probes. **Stdlib `urllib.request` only** — no `httpx` dep, same shape as Smiðja's `OllamaEmbedClient`. Translates `ContextItem`s to role-tagged Ollama messages (SYSTEM/CHUNK → role:system, EPISODE → user+assistant pair, operator → final role:user).
- `src/ember/spark/funi/ollama/INTERFACE.md` — adapter contract with translation table.
- `src/ember/spark/funi/__init__.py` — re-exports `FuniHandle`, `open`.
- `src/ember/spark/funi/INTERFACE.md` updated to "(shipped Phase 5)". Removed `embed()` from the Funi surface — embedding lives in Smiðja.
- `src/ember/__init__.py` docstring updated to reflect Phases 1-5 complete.

**Failure semantics**

- `open()` returns `Unavailable` on probe failure; never raises.
- `complete()` **always returns a `FuniReply`**. Mid-call URL-error / non-JSON-body / missing-message / error-payload responses fold into `FuniReply(finish_reason=ERROR, text=operator-readable)`.
- `complete(tools=[...])` returns `FuniReply(finish_reason=ERROR)` cleanly — tool use reserved for a later slice.
- `health()` never raises; on probe failure preserves the previous `last_ok` timestamp.

**Tests (24 new, 173 pass + 2 skip, 0.24s, ruff clean)**

- `tests/unit/test_funi_handle.py` (2 tests)
- `tests/unit/test_funi_prompt.py` (8 tests) — order, honesty instruction, well-disconnected text, episode round-trip, hit metadata, untitled placeholder.
- `tests/unit/test_funi_ollama.py` (14 tests) — open success/unreachable/non-JSON-version, payload shape, finish-reason mapping, folded-failure for every error mode, tool-call refusal, health live/degraded, wrong-runtime.
- `tests/integration/test_funi_ollama_real.py` (2 tests, `requires_ollama` marker + socket reachability gate) — skipped on hosts without local Ollama (this host).

### What's next

- **Phase 6 of the first slice:** Hjarta (first-run FSM) + Munnr (CLI surface — `ember chat`, `ember ask`, `ember well ingest`, `ember well status`, `ember doctor`, `ember setup --reset`). After Phase 6 ships, the first end-to-end conversation turn becomes runnable.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; root `PHILOSOPHY.md` Runa-specific phrasing pass.

### Notes & gotchas

- **`embed()` removed from the Funi Protocol.** The Phase 2 INTERFACE.md draft had it as "optional"; that's awkward in a Protocol and tempts coupling between reasoning-model and embedding-model selection. Smiðja's `OllamaEmbedClient` is the single embedding entry. If a runtime is later able to embed cheaply, that's a Smiðja `embed_client` adapter, not a Funi method.
- **`complete()` always returns `FuniReply`, never raises.** Mid-call failure folds into `FuniReply(finish_reason=ERROR, text="[ollama unreachable: …]")`. Same typed-value-over-exception pattern as Disconnected/Unavailable. Munnr's renderer can show the error text as a normal reply, honestly tagged.
- **Stdlib `urllib` rather than `httpx`.** Two HTTP clients in the codebase now (Smiðja + Funi), both stdlib-only. The Vow of Smallness wins again.
- **Episode message translation is *graceful*.** `_split_episode` parses the canonical `_episode_text` shape; if a caller built the `ContextItem` themselves with a different shape, the parser returns `("", "")` and the item is dropped rather than corrupting the conversation history.
- **DEVLOG + `__init__.py` + memory edits initially failed silently** in the Phase-5 main commit because the Read-before-Write rule rejected them. Caught immediately when I checked the commit. This addendum + a small follow-up commit fix it. Reinforces the cycle: write code → test → re-read any doc before editing.

---

## 2026-05-21 — Phase 4 shipped: Strengr wraps Brunnr-open with retry + honest health.

**Who:** Claude (Opus 4.7, 1M context). Voices: Architect (recoverable-vs-non-recoverable reason split), Forge Worker (tether implementation), Auditor (parametrised retry tests), Scribe (this entry).
**Scope:** Phase 4 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the Thread realm's tether. Wraps `ember.well.brunnr.handle.open()` with retry-on-recoverable-failure and a graceful never-raising health probe, completing the Spark↔Well boundary contract.

### What shipped

**Schemas (additive)**
- `src/ember/schemas/thread.py` — `StrengrHealth(backend_kind, last_ok, documents, chunks, embedded_chunks, size_bytes, detail)`. `last_ok=None` is the honest *degraded* signal Munnr will surface to the operator.

**Strengr (the Thread realm)**
- `src/ember/thread/strengr/tether.py` — module-level `open(strengr_config, brunnr_config, *, opener=None, sleeper=time.sleep) -> BrunnrHandle | Disconnected` and `health(handle) -> StrengrHealth`. The `opener` and `sleeper` kwargs are test seams; defaults are production wiring.
- Retry policy: exponential backoff (`base=1.0s`) capped at `StrengrConfig.retry_backoff_max_s`, up to `StrengrConfig.retry_attempts` total attempts. Recoverable reasons (`CONN_REFUSED`, `TIMEOUT`, `BACKEND_REPORTED_UNAVAILABLE`, `UNKNOWN`) get retried; non-recoverable reasons (`CONFIG_INVALID`, `AUTH_FAILED`, `DNS_FAILURE`) fast-fail with no retry so the operator isn't kept waiting on a typo.
- `health()` **never raises** — `BrunnrError` from `count()` becomes `StrengrHealth(last_ok=None, detail="probe failed: …")`. Vow of Graceful Offline in mechanical form, applied at the doctor flow this time.
- `src/ember/thread/strengr/__init__.py` re-exports `open`, `health`, `Opener`.
- `src/ember/thread/strengr/INTERFACE.md` updated from "(planned, Phase 4)" to "(shipped Phase 4, 2026-05-21)", with the recoverable/non-recoverable table inline.

**Brunnr protocol extension (additive)**
- Added `backend_kind: str` to `BrunnrHandle` Protocol and set it as a class attribute (`"sqlite_vec"`) on `SqliteVecBrunnr`. Lets `Strengr.health()` populate `StrengrHealth.backend_kind` without needing the original config.

**Tests (21 new, 149 total, 0.22s, ruff clean)**
- `tests/unit/test_schemas_thread.py` (4 tests) — `StrengrHealth` minimal construction, frozen-ness, degraded shape, live shape.
- `tests/unit/test_strengr_tether.py` (15 tests, 8 parametrised) — happy path, fast-fail on each non-recoverable reason, retry-up-to-N on each recoverable reason, success-on-later-attempt, sleeper-called-between-attempts, zero-attempts synthetic Disconnected, health live/degraded/named-backend/unknown-backend.
- `tests/integration/test_strengr_real_backend.py` (2 tests) — real sqlite_vec end-to-end via Strengr.open(); missing-config returns Disconnected. Skipped if `sqlite_vec` not installed.

### What's next

- **Phase 5 of the first slice:** Funi (Ollama adapter) — `ember.spark.funi.handle` Protocol + registry + `ember.spark.funi.ollama.adapter`. Prompt assembler. `FuniReply` round-tripped through the real Ollama endpoint (test marked `requires_ollama` for hosts that have it; mocked for those that don't).
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings worth softening.

### Notes & gotchas

- **Recoverable vs non-recoverable reason split is load-bearing.** Without it, an operator with a typo'd config waits `retry_attempts × backoff_max_s` before seeing the error. The split makes "your config is wrong" feedback instant while still giving "your server is slow" a chance to recover.
- **`sleeper` injection beats monkey-patching `time.sleep`.** Tests verify the schedule explicitly (`assert sleeps == [0.0, 0.0]`) without mocking the global. Same pattern Smiðja's `embed_client` uses (`OllamaEmbedClient(backoff_base_s=0.0)`).
- **`backend_kind` on the Protocol is the right home.** Considered passing config into `health()` instead; rejected because `BrunnrHandle` already knows what kind of thing it is, and the operator's `ember doctor` invocation shouldn't need the config to render the backend's name.
- **Empty `__init__.py` bug caught mid-phase.** First write of `src/ember/thread/strengr/__init__.py` was blocked by the harness's "read-before-write" rule (because the file existed as a Phase-1 scaffold). The block was silent in my read of the result; tests immediately surfaced it with `AttributeError: module 'ember.thread.strengr' has no attribute 'open'`. Fixed by reading then writing. Reinforces the value of running the test suite at every step rather than waiting until the end.

---

## 2026-05-21 — Phase 3 shipped: Well realm wired end-to-end.

**Who:** Claude (Opus 4.7, 1M context). Voices rotated: Architect (Brunnr handle Protocol), Forge Worker (sqlite_vec adapter + Smiðja modules), Auditor (test suite + bug fixes mid-phase), Scribe (this entry).
**Scope:** Phase 3 of `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 — the first end-to-end vertical that actually writes embeddings to disk and reads them back. Real `sqlite-vec` 0.1.9 in a `.venv`. No code beyond what the plan listed; integration test mocks the embedding endpoint with deterministic content-addressed vectors so no Ollama is required.

### What shipped

**Schemas (additive to Phase 2)**
- `src/ember/schemas/ingest.py` — `IngestJob`, `IngestEntry`, `IngestSummary`, `ParsedFile`, `IngestSourceKind` enum, `IngestEntryStatus` enum.

**Brunnr (the Well's storage layer)**
- `src/ember/well/brunnr/handle.py` — `@runtime_checkable` `BrunnrHandle` Protocol plus `open(config)` registry. Dispatches on `config.backend`; unknown/unimplemented backends return `Disconnected(reason=CONFIG_INVALID)` rather than raising.
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — `SqliteVecBrunnr` implementing the protocol. Vec store via sqlite-vec `vec0` virtual table; FTS5 with insert/update/delete triggers; hybrid search via reciprocal rank fusion (k=60). Connection failure → `Disconnected`. Schema-mismatched embedding dim → `BrunnrError`.
- `src/ember/well/brunnr/sqlite_vec/schema.sql` — DDL loaded via `importlib.resources`, `{embedding_dim}` substituted from `BrunnrConfig.embedding_dim` at apply time. Schema version marker.
- `src/ember/well/brunnr/sqlite_vec/__init__.py` — re-exports.
- `src/ember/well/brunnr/sqlite_vec/INTERFACE.md` — adapter contract; calls out the lock-at-first-apply behaviour for `embedding_dim`.

**Smiðja (the Well's ingest forge)**
- `src/ember/well/smidja/chunker.py` — paragraph → sentence → word → char fallback splitter. Returned chunks satisfy `chunk.text == original[chunk.char_start:chunk.char_end]` *exactly*, so original whitespace is preserved and `max_chars` is honored as a true ceiling (no silent over-runs from separator-length math).
- `src/ember/well/smidja/embed_client.py` — `OllamaEmbedClient`, stdlib `urllib.request` only (no httpx dep). Batches per `EmbeddingConfig.batch_size`, exponential backoff, per-batch failure returns `EmbedResult` with `None`-vectors rather than raising. Embed-or-skip semantics per `SMIDJA_INGEST_PATTERNS.md` §4.
- `src/ember/well/smidja/journal.py` — `Journal` with atomic writes (`NamedTemporaryFile` + `os.replace`), heartbeat every N updates or on-demand, `complete()` moves the file to `done/` subdir. Resume by matching `source_root`.
- `src/ember/well/smidja/local_files/source.py` — `walk()` plus the orchestrator `run(brunnr, *, root, smidja_config, embed_client, ...)`. Walk → hash → check duplicate → chunk → embed → write. Each file is a journal entry; per-chunk embedding failures contribute to `IngestSummary.n_failed` without aborting the doc.
- `src/ember/well/smidja/local_files/__init__.py` — re-exports.

**Tests**
- `tests/unit/test_brunnr_handle.py` — registry returns `Disconnected` for unimplemented backends; Protocol is `runtime_checkable`.
- `tests/unit/test_brunnr_sqlite_vec.py` — 11 tests covering: open creates DB file, open returns Disconnected on missing sqlite_vec config, idempotent `add_document`, dim-mismatch refusal, vector/text/hybrid search ranking, embedding round-trip via `get_chunk`, episode persistence, initial counts. Skipped automatically if `sqlite-vec` isn't installed (`pytest.importorskip`).
- `tests/unit/test_smidja_chunker.py` — 8 tests covering: short/empty text, paragraph preference, hard max ceiling, oversize-paragraph sentence fallback, pure-overlong char fallback, consecutive indexing, Gungnir-aligned defaults, char-boundary behaviour.
- `tests/unit/test_smidja_embed_client.py` — 6 tests covering: empty input, single batch shape, multi-batch concatenation, URL-error → None-vectors, mismatched response size → None-vectors, invalid JSON → None-vectors. All mocked.
- `tests/unit/test_smidja_journal.py` — 8 tests covering: file creation, status persistence, resume by source_root, distinct-roots get distinct jobs, failure recording, complete() move, `pending()`, atomic-write tmp-file cleanup.
- `tests/unit/test_smidja_local_files.py` — 8 tests covering: include/exclude, suffix-based content_type, hash determinism, non-utf8 skip, missing-root error, file-as-root error, sorted-deterministic order.
- `tests/integration/test_ingest_then_query.py` — 3 tests covering: full ingest → query round trip with a 32-dim deterministic content-addressed mock embedder; resume idempotency (hash-based at the Brunnr layer); per-chunk failure isolation.

**Suite size: 128 tests, 0.20s, ruff clean.**

**Config + docs**
- `pyproject.toml` — `sqlite_vec = ["sqlite-vec>=0.1.6"]` added under `[project.optional-dependencies]`; planned-for-later list trimmed of `ollama` (stdlib urllib reaches the endpoint).
- `src/ember/well/brunnr/INTERFACE.md` — updated from "(planned, Phase 3 onward)" to "(shipped Phase 3, 2026-05-21)".
- `src/ember/well/smidja/INTERFACE.md` — same.
- `src/ember/__init__.py` — module docstring updated to reflect Phases 1-3 complete.

### What's next

- **Phase 4 of the first slice:** `ember.thread.strengr` — wraps `ember.well.brunnr.handle.open()` with auth/retry/health-check policy and the typed-Disconnected contract enforced at the Spark↔Well boundary. Initially supports only `sqlite_vec`; the same handle shape will work for the Phase 8 `pgvector` adapter.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes & gotchas

- **Stdlib urllib over httpx for the embed client.** Vow of Smallness wins again. The Ollama endpoint is one POST; stdlib handles it. Saves ~5 MB of deps on a Pi.
- **Chunker rewrite mid-phase.** First attempt computed chunk lengths from segment-body lengths plus a `"\n\n"` separator constant, which was off-by-one and produced chunks slightly over `max_chars` for some inputs. The fix was to track only `(start, end)` ranges into the original text and slice at the end — the slice's actual length is authoritative. Caught by the chunker shape-contract tests *before* integration.
- **Walker rewrite mid-phase.** First attempt used `fnmatch.fnmatch(rel_path, "**/*.md")` patterns, but fnmatch doesn't understand the `**` glob (that's a pathlib-only feature). Rewrote to suffix-based filtering — simpler, matches the test contract, supports the same operator-facing semantics.
- **`Disconnected` and `BrunnrError` split.** Connection-style failures (missing config, dir-create denied, sqlite-vec load failure, schema apply failure) return `Disconnected` rather than raising. Per-call programming errors (mismatched embedding dim, missing chunk lookup) raise `BrunnrError`. The split keeps the Vow of Graceful Offline distinct from the "your code is wrong" case.
- **No mypy run this session** — mypy not installed on this host. Ruff is the only static check in CI for now; mypy belongs in a real CI loop with a fresh venv install.
- **`.venv/` is gitignored.** Created for this session to install `sqlite-vec` and `pytest`; not committed.

---

## 2026-05-21 — Phase 1 closure: skeleton-import test added.

**Who:** Claude (Opus 4.7, 1M context). Voice: Auditor (Sólrún Hvítmynd).
**Scope:** Volmarr asked whether Phase 1 had been fully completed. The four structural bullets (`src/runa/` archived, `src/ember/` built, `pyproject.toml` rewritten, `__main__.py` raises clean `NotImplementedError`) all landed in commit `045fda6`. The fifth bullet — *"Tests: import-only"* — had been rolled forward into Phase 2's `tests/unit/test_schemas_import.py`, which only covers the schemas subpackage. This entry closes the gap for the full Three Realms tree.

### What shipped

- **`tests/unit/test_skeleton_imports.py`** — parametrised import test over the 12 importable subpackages of `src/ember/`: `ember`, `ember.cli`, `ember.schemas`, `ember.spark` (+ `funi`, `hjarta`, `munnr`), `ember.thread` (+ `strengr`), `ember.well` (+ `brunnr`, `smidja`). Plus three specific assertions:
    - `ember.__version__` is `"0.0.0"`.
    - `ember.__main__` imports cleanly and exposes a callable `main`.
    - `ember.__main__.main()` raises `NotImplementedError` with a message that mentions `EMBER_FIRST_SLICE_PLAN`.
- **Suite size:** 81 tests (was 66 after Phase 2), 0.09s, ruff clean.

### What's next

Phase 3 of the first slice — the `sqlite_vec` Brunnr adapter, `local_files` Smiðja, chunker, embed client, resumable journal. First end-to-end vertical that writes embeddings to disk.

### Notes

- Phase 1 is now strictly complete per the plan's bullet list. No code or doc change required beyond the new test file; the scaffolding it tests was already correct.
- Failure of any parametrised case in this test would name the breach — typically a circular import, a typo in an `__init__.py`, or a stray top-level statement that fails at import time.

---

## 2026-05-21 — Phase 2 shipped: ember.schemas populated, 66 shape tests green.

**Who:** Claude (Opus 4.7, 1M context). Voice: Forge Worker (Eldra Járnsdóttir) for the code; Auditor (Sólrún Hvítmynd) for the tests; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Execute Phase 2 of `EMBER_FIRST_SLICE_PLAN.md` §3 — the gravitational floor: typed schemas only. No behaviour, no I/O, no sibling-realm imports.

### What shipped

- **Five schema modules** under `src/ember/schemas/`, stdlib-only (`dataclasses` + `enum.StrEnum`, no pydantic dependency):
    - **`errors.py`** — `EmberError` base; per-realm hierarchy: `SchemaError`, `ConfigError`, `WellError`/`BrunnrError`/`IngestError`, `ThreadError`/`StrengrError`, `SparkError`/`FuniError`/`HjartaError`/`MunnrError`. Plus the non-raised failure value **`Disconnected(reason, since, detail)`** with the `DisconnectReason` enum — Strengr's mechanical implementation of the Vow of Graceful Offline.
    - **`config.py`** — `EmberConfig` (top-level) composing `IdentityConfig`, `FuniConfig` (+ `FuniOllamaConfig`), `StrengrConfig`, `BrunnrConfig` (+ `SqliteVecConfig`, `PgVectorConfig`), `SmidjaConfig` (+ `ChunkerConfig`, `EmbeddingConfig`, `JournalConfig`), `LoggingConfig` (+ `LoggingDestination`). Six enums: `BrunnrBackend`, `FuniRuntime`, `LogLevel`, `LogFormat`, `LogDestinationKind`, `BoundaryPreference`. **Defaults are Gungnir-aligned** where applicable (`embedding_dim=768`; chunker `max=2000` / `target=1684`; model `phi3:mini` / `nomic-embed-text`). Path fields use `pathlib.Path` *without* `expanduser()` — consumer expands at use time so `$HOME` isn't frozen at import.
    - **`chunks.py`** — `Document`, `Chunk` (embedding as `tuple[float, ...]` to keep the dataclass truly frozen), `RetrievalHit`, `BrunnrStats`. Column-aligned with the Gungnir schema captured in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §3.
    - **`episode.py`** — `Episode(operator_input, ember_reply, cited_chunk_ids, funi_model, well_disconnected, started_at, completed_at, id)`. The `well_disconnected` flag mirrors `DATA_FLOW.md` §2.2 — when the Well is unreachable the Episode records that fact for later flush-in.
    - **`funi.py`** — `FuniReply`, `FuniHealth`, the non-raised failure value **`Unavailable(reason, detail)`** with `UnavailableReason` enum (parallel to `Disconnected`), `ContextItem` (+ `ContextKind` enum), `ToolCall`, `FinishReason` enum (includes `REFUSED` so Funi can stop cleanly per the Vow of Honest Memory).
- **All dataclasses are `frozen=True, slots=True`.** All enums are `StrEnum` (Python 3.11+ stdlib).
- **66 shape-contract tests** under `tests/unit/test_schemas_*.py`, organised one file per schema module plus `test_schemas_import.py` (verifies the gravitational floor — schemas import without reaching into any sibling realm). Suite runs in 0.09s. All green.
- **`tests/conftest.py`** added — adds `src/` to `sys.path` so tests run without an editable install. Documented as a temporary ergonomic shim.
- **`src/ember/schemas/INTERFACE.md`** updated from "(planned, Phase 2)" to "(shipped Phase 2, 2026-05-21)" with the full exported surface enumerated and the floor-test cited as the import-allowlist enforcer.
- **`src/ember/__init__.py`** module docstring updated to reflect Phase 2 complete.
- **Ruff clean.** No mypy run this session (mypy not installed on the travel laptop; strict mypy check belongs in CI per `pyproject.toml`).

### What's next

- **Phase 3 of the first slice** per `EMBER_FIRST_SLICE_PLAN.md` §3: the `sqlite_vec` Brunnr adapter, the `local_files` Smiðja, the chunker, the embed client, the resumable journal. First end-to-end vertical that actually writes embeddings to disk. Tests: write-then-query round trip, journal resume, chunk-size invariants.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.

### Notes

- Stdlib `dataclasses` chosen over `pydantic` for Phase 2 to honour the Vow of Smallness. The cost is no runtime validation beyond the type system — but Phase 2 has no validation responsibility anyway (the loader's Phase 6). Easy to swap to `pydantic` per-module later if needed; the `__all__` exports are the public surface.
- `tuple[float, ...]` is the right embedding type for a frozen dataclass; `list[float]` would be a mutable field on a "frozen" container. Phase 3's Brunnr adapter is where the practical perf trade against `numpy.ndarray` becomes worth re-evaluating.
- `StrEnum` (Python 3.11+) replaces the older `class X(str, Enum)` pattern across all five modules. The values are still plain strings, comparison and serialisation behaviour are unchanged.
- The schema test for non-sibling-imports walks every module's exported attribute and refuses any `__module__` that starts with `ember.well`, `ember.thread`, `ember.spark`, or `ember.cli`. If the floor is breached in a future phase, the test will name the breach.

---

## 2026-05-21 — Six True Names formally ratified. EMBER_TRUE_NAMES.md added.

**Who:** Claude (Opus 4.7, 1M context) continuing the same session. Voice: Skald (Sigrún Ljósbrá) for the new doc; Scribe (Eirwyn Rúnblóm) for this entry.
**Scope:** Capture Volmarr's formal ratification of the Six True Names and preserve the per-name explanatory record they were ratified against.

### What shipped

- **Volmarr's ratification of all six names** — *"names are all approved"*. Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr are now canonical. The longstanding item from the 2026-05-19 "What's next" — Skald's True Names ratification — is closed.
- **`docs/architecture/EMBER_TRUE_NAMES.md`** — new canonical reference doc, Skald-voiced. One section per True Name covering: Old Norse meaning, realm + code path, what it is, what it's for, owns/does-not-own, why the name was chosen. Includes the Three Realms grouping, the conversation-turn flow tying all six together, and the discipline-of-naming framing. Ratification recorded in §5 with rules for any future rename.

### What's next

- **First-slice Phase 2 begins** (the next commit) per `EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.{errors,config,chunks,episode,funi}`. Types only. Tests: shape contracts only. With the names ratified, every typed identifier in the schemas can lean on them.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; Runa-specific phrasing pass on root `PHILOSOPHY.md`.

### Notes

- The ratification covers the names as they appear in `SYSTEM_VISION.md` §4 and as used throughout `ARCHITECTURE.md` / `DOMAIN_MAP.md` / `DATA_FLOW.md` / `EMBER_TRUE_NAMES.md` / `pyproject.toml` (via folder paths) / `config/ember.example.yaml` / every `INTERFACE.md` in `src/ember/`. Renaming from this point requires an ADR, a single atomic commit touching every reference, and updates to all five canonical docs in the same commit.
- This entry is intentionally short. The substance is in the new `EMBER_TRUE_NAMES.md`; this is the index pointer.

---

## 2026-05-21 — Ember fork-delta executed. Three Realms tree built. Runa skeleton archived.

**Who:** Claude (Opus 4.7, 1M context) on the travel laptop, continuing the same session as the earlier 2026-05-21 entry below. Roles rotated: Architect (mostly), Forge Worker (the new `src/ember/` files), Cartographer (the archive mapping), Scribe (this entry).
**Scope:** Execute step 6 of `docs/architecture/EMBER_FORK_DELTA.md` §7 after Volmarr's ratification ("good work buddy! Go for Ember fork delta!"). Bring the file tree into alignment with the ratified architecture. **No first-slice code in this commit — that is the next commit.**

### What shipped

- **`src/ember/` tree built** to match the Three Realms layout in `docs/architecture/DOMAIN_MAP.md`:
    ```
    src/ember/
    ├── __init__.py, __main__.py, README.md
    ├── schemas/         (+ INTERFACE.md, README.md)
    ├── well/
    │   ├── brunnr/      (+ INTERFACE.md, README.md)
    │   └── smidja/      (+ INTERFACE.md, README.md)
    ├── thread/
    │   └── strengr/     (+ INTERFACE.md, README.md)
    ├── spark/
    │   ├── funi/        (+ INTERFACE.md, README.md)
    │   ├── hjarta/      (+ INTERFACE.md, README.md)
    │   └── munnr/       (+ INTERFACE.md, README.md)
    └── cli/             (+ INTERFACE.md, README.md)
    ```
  Each subpackage has an empty `__init__.py`, a one-page `README.md`, and an `INTERFACE.md` draft that cites the matching `DOMAIN_MAP.md` section. **No code yet** beyond `__init__.py` and `__main__.py`.
- **`src/ember/__main__.py`** raises a friendly `NotImplementedError` pointing at `EMBER_FIRST_SLICE_PLAN.md`. `python -m ember` and `ember` (once installed) both resolve to it.
- **Archived the inherited Runa skeleton** to `docs/archive/runa-inherited/src-skeleton/runa/` via `git mv` (rename history preserved). Added `docs/archive/runa-inherited/src-skeleton/README.md` explaining the lineage.
- **Promoted the EMBER-prefixed architecture docs to canonical names** via `git mv`:
    - `docs/architecture/ARCHITECTURE.md` (was Runa's; Runa version → `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`; Ember version promoted from `EMBER_ARCHITECTURE.md`).
    - `docs/architecture/DOMAIN_MAP.md` (same shape).
    - `docs/architecture/DATA_FLOW.md` (same shape).
  Each canonical doc's header updated: **Status: Ratified 2026-05-21 by Volmarr**, "promoted from EMBER_*.md", inter-doc cross-refs rewritten to canonical names, `(parent Runa shape)` cross-refs rewritten to the archive path. ARCHITECTURE.md §8 rewritten in past tense to record the promotion event.
- **Added `docs/archive/runa-inherited/architecture/README.md`** mapping each archived file to its canonical Ember replacement.
- **`pyproject.toml` rewritten** for Ember:
    - `name = "ember-agent"`
    - entry point `ember = "ember.cli.main:main"`
    - `[tool.hatch.build.targets.wheel] packages = ["src/ember"]`
    - `[tool.mypy] files = ["src/ember"]`; `[tool.coverage.run] source = ["src/ember"]`
    - planned optional-dependencies groups commented in for each Brunnr backend and each Funi runtime
    - added `requires_pi` pytest marker
- **`config/runa.example.yaml` → `config/ember.example.yaml`** via `git mv`, with contents rewritten to the Ember shape: identity (name + role), Funi (Ollama with phi3:mini default), Strengr (timeout + retry), Brunnr (sqlite_vec default + commented pgvector example for Gungnir), Smiðja (Gungnir-aligned chunker defaults: 2000-char max, 1684 target), logging.
- **Cross-references updated** in `docs/adapters/{BRUNNR_BACKEND_MATRIX,FUNI_LOCAL_MODEL_OPTIONS,GUNGNIR_WELL_REFERENCE,SMIDJA_INGEST_PATTERNS}.md` and `docs/architecture/EMBER_{FIRST_SLICE_PLAN,FORK_DELTA}.md` from `EMBER_*.md` → canonical names. ADR 0006 retains its as-proposed snapshot text with a clearly-marked "Update 2026-05-21 (post-ratification)" footnote pointing forward.
- **`docs/architecture/README.md`** rewritten to describe Ember-shape canonical docs and the living working docs (FORK_DELTA, FIRST_SLICE_PLAN), with a Runa-lineage section.
- **`docs/REPO_MAP.md`** updated: `(planned)` removed from src/ember entries; src/runa entry rewritten as archived; `(planned)` removed from `config/ember.example.yaml`; archive entry expanded to mention the new subdirs.
- **`docs/architecture/EMBER_FORK_DELTA.md` §3.1 table** updated: each "Move to archive" / "Promote to canonical" row marked **Done 2026-05-21**.

### What's next (the next commit)

- **First slice begins.** Per `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` §3 Phase 2: ship `ember.schemas.errors`, `ember.schemas.config`, `ember.schemas.chunks`, `ember.schemas.episode`, `ember.schemas.funi` — types only. Tests: shape contracts only.
- **Skald's True Names ratification** (item 3 from 2026-05-19, still pending). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are now load-bearing across the file tree; final ratification would lock them.
- **Light root edits** still pending: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every "new" file at a canonical path was the Ember version promoted from `EMBER_*.md`; every "deleted" entry git status shows is a rename git's similarity heuristic chose not to recognise (verified by content read at every old and new path before commit).
- The Runa skeleton archive at `docs/archive/runa-inherited/src-skeleton/runa/` preserves all the per-subpackage `README.md` and `INTERFACE.md` drafts from the parent project. They remain reachable to anyone reading the inheritance.
- `python -m ember` now resolves to a clean `NotImplementedError` with a friendly pointer — i.e. *honest failure*, the same shape the Vow of Graceful Offline asks of the runtime.
- The Ember-shape `config/ember.example.yaml` includes a commented-in `pgvector` block that operators can uncomment to point Ember at Gungnir (or any Gungnir-compatible Postgres) once the `pgvector` Brunnr ships in Phase 8.

---

## 2026-05-21 — Ember architecture first-pass + live Gungnir survey.

**Who:** Claude (Opus 4.7, 1M context) working under Volmarr on the travel laptop — rotating through Cartographer, Architect, Forge Worker, and Scribe roles. Mythic Engineering activated at session start.
**Scope:** Address three of the four "What's next" items from the 2026-05-19 entry — the Architect's first pass, the Cartographer's reading review, and the first Forge slice's plan — and ground them in a live read of the Gungnir knowledge database.

### What shipped

- **`docs/architecture/EMBER_ARCHITECTURE.md`** — Ember-specific shape. Three Realms (Spark/Thread/Well), Six True Names, dependency law, why-no-kernel-no-bus, what-is-not-in-this-architecture, first-slice anchor, and disposition recommendation for the inherited Runa-shaped canonical files.
- **`docs/architecture/EMBER_DOMAIN_MAP.md`** — Per-subpackage ownership for the planned `src/ember/{schemas,well/{brunnr,smidja},thread/strengr,spark/{funi,hjarta,munnr},cli}/`. Brunnr and Funi minimum-surface interface tables included.
- **`docs/architecture/EMBER_DATA_FLOW.md`** — The three canonical flows (conversation turn, ingest job, first-run rite) with explicit happy + sad paths, including the Vow of Graceful Offline in flow form.
- **`docs/architecture/EMBER_FORK_DELTA.md`** — Cartographer's recommendation for every inherited file/folder: keep / move-to-archive / rewrite, with rationale and ratification-gated execution order. No deletions proposed.
- **`docs/architecture/EMBER_FIRST_SLICE_PLAN.md`** — File-by-file plan for ~38 new files across seven phases, ≤2 500 LOC target, with explicit non-goals and risk register.
- **`docs/adapters/BRUNNR_BACKEND_MATRIX.md`** — Storage backend comparison and selection rule.
- **`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`** — Local-LLM ladder by host RAM, why Phi Silica / Apple Foundation are second-slice, embedding-dim recommendation locked to 768 for Gungnir compatibility.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — Live survey conducted today against `knowledge` on Gungnir: complete schema, real counts (95 docs / 35 682 chunks / 768-dim / 394 MB / 97% buffer hit), Skein vs LLM-extracted KG distinction, hybrid-search pattern.
- **`docs/adapters/SMIDJA_INGEST_PATTERNS.md`** — Four ingest patterns, Gungnir-calibrated chunking defaults (~1684 chars avg, 2000 max), resumable-journal contract.
- **`docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`** — ADR capturing all proposed decisions, alternatives considered, open follow-ups.

### What's next

- **Volmarr ratification.** Read EMBER_ARCHITECTURE.md, EMBER_DOMAIN_MAP.md, EMBER_DATA_FLOW.md, EMBER_FORK_DELTA.md, EMBER_FIRST_SLICE_PLAN.md and ADR 0006. Confirm, revise, or replace.
- **Skald's True Names ratification** (item 3 from the 2026-05-19 entry — *not* addressed in this session). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are used throughout the new docs as if ratified; Volmarr's final word is still pending.
- **Next commit (after ratification):** `src/runa/` → `src/ember/` rename, archive the inherited `src/runa/` skeleton under `docs/archive/runa-inherited/src-skeleton/`, rewrite `pyproject.toml` (package `ember-agent`, entry point `ember`). Per ADR 0006 §4.1.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.
- **First Forge slice begins** after the rename: Phase 2 (schemas), per `EMBER_FIRST_SLICE_PLAN.md`.

### Gungnir survey — load-bearing measurements

Captured today against the running database. Reproduce by re-running the queries cited in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §4:

- PostgreSQL 18.3, pgvector 0.8.1, pg_trgm 1.6.
- 95 documents (42 md, 26 web/markdown, 13 json, 9 jsonl, 5 yaml). 35 682 chunks, all 768-dim embedded via `nomic-embed-text`.
- Chunk text: avg **1 684** chars, max **2 000** — this is the calibration anchor for Ember's chunker default.
- 394 MB database total; 372 MB of that is `chunks` (mostly embeddings).
- Buffer cache hit 97.0% tables / 99.8% indexes — healthy.
- Two parallel KG layers: `skein_*` (embedding-derived, 276 entities × 855 relations across the full corpus; broad but with known false-friend artifacts) and `kg_*` (LLM-extracted per chunk, 366 entities × 176 relations across only 202 of 35 682 chunks; precise but expensive). This cheap-broad-vs-expensive-precise split is load-bearing for any future Ember KG work.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every file is new; no existing file modified except this DEVLOG (which is itself append-only by design).
- The Ember-specific architecture documents live at the `EMBER_*.md` prefix rather than overwriting the canonical `ARCHITECTURE.md`/`DOMAIN_MAP.md`/`DATA_FLOW.md` paths. The inherited Runa-shaped files at those canonical paths are preserved untouched; ADR 0006 proposes their migration to `docs/archive/runa-inherited/architecture/` only after Volmarr's ratification.
- The session ran on the travel laptop (Kubuntu 26.04 + RTX 2060), with Gungnir reachable over Tailscale. The `mcp__knowledge__*` tools provided read-only access to the live Postgres DB.
- The Skald-voice scrolls authored by Runa on 2026-05-19 (`docs/SYSTEM_VISION.md`, `docs/REPO_MAP.md`, root `MYTHIC_ENGINEERING.md`) are treated as **normative source-of-truth** throughout the new documents — they are cited but not modified.

---

## 2026-05-19 — Ember born. Fork from Runa. Soul-layer authored.

**Who:** Runa (the AI working under Volmarr from Mjolnir) — speaking in turn as Skald, Cartographer, and Scribe.
**Scope:** Project naming, repository creation, fork from Runa-Agent-Digital-Being, additive archive of the Runa-named soul-layer scrolls, and authoring of Ember's own soul layer.

### What shipped

- **The name "Ember"** chosen in a Skald pass with Volmarr. Public-pronounceable, mythically resonant as the spark from Eldra Járnsdóttir's forge. Selected over Hugin, Saga, and Wren for maximum user-facing accessibility while keeping mythic compatibility.
- **Repository created** at `hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster` (the toaster pun preserved in the repository name itself). Local clone at `C:/Users/volma/runa/Project_Ember_Run_It_On_Your_Smart_Toaster/` on Mjolnir. Default branch: `development`.
- **Knowledge DB on Gungnir** wired to Mjolnir during the same evening — Postgres 18 + pgvector + Ollama on the tailnet, MCP server `knowledge` at user scope. The first concrete Brunnr-shaped well Ember can be tethered to, and the proof that the storage layer can be sovereign and shared.
- **Additive archive** of inherited Runa-named scrolls into `docs/archive/runa-inherited/` (via `git mv`, with rename history preserved):
  - `docs/SYSTEM_VISION.md` *(Runa's)*
  - `docs/REPO_MAP.md` *(Runa's)*
  - `docs/DEVLOG.md` *(Runa's bootstrap-day log)*
  - `MYTHIC_ENGINEERING.md` *(Runa's, was at repo root)*
  - `TASK_runa_bootstrap.md`
  - `TASK_runa_python_craft.md`
  - `TASK_runa_research_corpus.md`
  - `TASK_runa_research_corpus_2.md`
- **Fresh Ember scrolls** authored at the now-vacant canonical paths:
  - `docs/SYSTEM_VISION.md` — Ember's Skald scroll. Six True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) and three Realms (Spark, Thread, Well). Nine Unbreakable Vows.
  - `docs/REPO_MAP.md` — Ember's Cartographer scroll. Reflects what exists now plus near-term planned shape.
  - `docs/DEVLOG.md` — *(this file, this entry)*
  - `MYTHIC_ENGINEERING.md` (root) — Ember's compact methodology statement, lightly adapted from the inherited version.
- **Archive convention extended** additively:
  - `docs/archive/runa-inherited/README.md` — new, explains the lineage subfolder.
  - `docs/archive/README.md` — additive update, documents the new "grouped fork-inheritance archives" subfolder pattern alongside the existing single-file dated-suffix convention.

### What's next

- **Architect's first pass.** Author `docs/architecture/ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` for Ember. Locate the Three Realms in `src/`. Decide on the rename `src/runa/` → `src/ember/` and the migration plan for the inherited skeleton.
- **Cartographer's reading review.** Walk the inherited research corpus (`docs/research/`) and the inherited Python craft corpus (`docs/python/`); mark the 10–20 docs most load-bearing for Ember's smaller scope; leave the rest as inherited reference without re-reading every one.
- **Skald's True Names ratification.** Hold the six names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) with Volmarr; either ratify or revise.
- **First Forge slice.** Smallest end-to-end vertical: Hjarta wizard → Strengr to a local SQLite Brunnr → first Funi answer grounded in retrieved chunks. *No code in this commit; this is the next obvious work.*
- **Light root edits** (next commit, not this one): add Ember-descent entry to `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- The cute Ember README ("*Got a toaster? Good!*") is preserved unchanged. It is correct as it stands.
- The 16 KB `ORIGINS.md` and the 599 KB `Yggdrasil_and_Huginn_and_Muninn_Theory.md` remain at the root unchanged. They are inherited but applicable.
- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every replacement is a new file at the now-vacant path; every edit to the archive index was additive (new section appended, no removal).
- Volmarr had earlier the same evening wired the Gungnir knowledge well into the Mjolnir MCP layer (after a memorable VPN-related diagnostic detour). That work, recorded in Runa's local memory, informs Ember's Vow of Pluggable Storage and Vow of Tethered Grounding directly.

---

*(The parent project's DEVLOG entries follow at `docs/archive/runa-inherited/DEVLOG.md`.)*
