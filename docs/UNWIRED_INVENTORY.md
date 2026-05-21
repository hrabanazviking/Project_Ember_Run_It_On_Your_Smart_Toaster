# Unwired Inventory

**As of 2026-05-21 (HEAD `02ded16`).** A canonical list of everything in
this repo that is **defined but not currently wired into Ember-the-project**,
plus the recommended action for each.

The audit was performed by the Mythic-Engineering Auditor (Sólrún) using
the Explore subagent + manual grep verification. Re-running it should
produce the same list — update this file when something here gets wired,
removed, or new orphans appear.

---

## 1. Orphan fields inside `src/ember/` — TWO ACTIONABLE ITEMS

These are real schema fields the operator can write into `ember.yaml`
**but the code never reads them**. Operator setting these gets nothing.

### 1.1 `StrengrConfig.health_check_timeout_s`

- **Declared:** `src/ember/schemas/config.py:116`
- **Default:** `5.0`
- **Documented in:** `src/ember/thread/strengr/README.md:76`
- **Read by production code:** **zero callers**
- **Read by tests:** `tests/unit/test_strengr_tether.py:82` (only sets it
  as a config value; the test never asserts that the timeout actually
  fired)

**Status:** declared as if it controls Strengr's health-check timeout,
but `tether.health()` doesn't reference the field. Operator-misleading.

**Recommended action:** **wire it.** In `tether.health()`, wrap the
`brunnr.count()` probe in a timeout that uses `config.health_check_timeout_s`.
The signature already exists; the plumbing is one `signal.alarm` or
`concurrent.futures.ThreadPoolExecutor.result(timeout=...)` call.

Alternatively: **delete the field** + update the strengr README. Less
work, but operators who saw the README will lose a documented capability.

**Estimated effort:** 30 min to wire + a regression test that simulates
a slow probe. Or 5 min to delete.

### 1.2 `JournalConfig.stale_heartbeat_s`

- **Declared:** `src/ember/schemas/config.py:191`
- **Default:** `600` (10 minutes)
- **Documented in:** nowhere — not even in the journal README
- **Read by production code:** **zero callers**
- **Read by tests:** **zero callers**

**Status:** ghost field. The most-orphan field in the schema.
Presumably intended for "if a journal's last_heartbeat is older than N
seconds, treat the journal as crashed and recover." But there's no
crash-recovery code path that uses it.

**Recommended action:** **wire it.** Two options:

- (a) In `Journal._find_existing()`, when resuming, check if the
  journal's `last_heartbeat` is older than `stale_heartbeat_s`. If so,
  log a warning and refuse to resume (start fresh) — protects against
  a crashed-ingest journal from yesterday that's no longer truthful.
- (b) Add a CLI command `ember well clean-stale` that walks
  journals and removes ones older than the threshold.

Or: **delete the field**. Lowest effort.

**Estimated effort:** 1-2 hours for option (a) with tests. 5 min to
delete.

---

## 2. Test seams (intentional, NOT orphans)

`src/ember/tools/fetch_url.py` exposes three module-level setters:

- `_set_url_opener(fn)` — overrides `urllib.request.urlopen` shape
- `_set_address_resolver(fn)` — overrides the DNS resolver
- `_set_robots_fetcher(fn)` — overrides the robots.txt parser

No production caller. **This is correct by design.** They're test seams
with safe default fallbacks. When unset (default), the real
implementations run.

Same pattern applies to:
- `search_well.bind_brunnr()` and `search_well.bind_embedder()` —
  WIRED (chat.py's `_maybe_init_tools` calls them).
- `fetch_url.bind_allow_private_default()` — WIRED in Batch J.

**No action needed.** Leave the underscore-prefixed setters as test
infrastructure.

---

## 3. Sibling projects in the monorepo — 9 SEPARATE PYTHON PACKAGES

This repository has grown into a *monorepo* with Ember-the-agent at
the center (`src/ember/`) and **9 sibling Python projects** added as
top-level directories. Each has its own `pyproject.toml`. None imports
from `src/ember/`; `src/ember/` doesn't import from any of them.

### Status table

| Project | What it is | Mentions Ember? | Integration path |
|---|---|---|---|
| **bifrost** | Composite memory provider (Mímir + Huginn + Muninn bridge) | not in its README | ✅ **Yes — ADR-0012 placeholder reserves "Bifröst" as the slice-3 HTTP gateway surface.** This sibling project is plausibly the implementation. Awaits slice-3 wiring. |
| **mimir-well** | AI memory database | no | Related to bifrost (Mímir leg). Wait for slice-3. |
| **seidr_engine** | Old Norse poetry generator (Eddic meter, rule-based) | no | None planned. Standalone Norse-themed sibling. |
| **kista** | Encrypted credential vault (Fernet, 8 entry types) | no | None planned. Could *plausibly* feed `EMBER_WELL_PASSWORD` via a `pgvector` secret resolver in V2, but not designed. |
| **mempalace** | (README is scam-warning only — content unclear) | no | None planned. Likely abandoned or archival. |
| **CloakBrowser** | Playwright stealth wrapper for browser automation | no | None planned. Could complement `fetch_url` in slice-3+ if Ember ever needs a real browser. |
| **astrology-engine** | Lunar phase + planetary aspects library | "Hermes Agent" mentioned (not Ember) | None planned. |
| **Hamr** | (README is image-only — content unclear) | no | None planned. |
| **Verdandi** | (Image + "Integration Guide" link; framework-agnostic) | no | None planned. |

### Non-Python siblings

- **`cleasby-vigfusson-old-norse-dict`** — Next.js, Old Norse
  dictionary corpus. Archival / reference. Could fuel `seidr_engine`
  or a future Norse-tooling chain.
- **`Open-VTT`** — Godot, virtual tabletop. Unrelated to Ember;
  bachelor's thesis basis per memory.

### Recommended action

- **No code wiring needed.** All siblings are properly isolated
  monorepo neighbors.
- **Make the relationship explicit.** This document IS the
  explanation; link to it from the top-level `README.md` so visitors
  know the repo is a monorepo and the other directories aren't part
  of Ember.
- **When bifrost gets wired (slice-3):** that's the moment to revise
  this file's bifrost row to "INTEGRATED, see ADR-0016" or similar.

---

## 4. The Stofa TUI design tree — 74 docs, ZERO CODE

`docs/tui/` contains a 74-file design tree shipped on 2026-05-21
(commit `8e9e9b3`). Every file is a `.md`; there is no Python
implementation yet.

**Status:** intentionally pre-implementation. Phase 1 ("The Hearth")
is documented in
[`docs/tui/roadmap/99_ROADMAP_PHASE_1_HEARTH.md`](tui/roadmap/99_ROADMAP_PHASE_1_HEARTH.md);
~25 files / ~2,500 LOC. Awaits ADR-0015 ratification.

**Recommended action:** draft ADR-0015 when the operator (Volmarr) is
ready to begin implementation. The design tree is the input; the ADR
is the commitment.

---

## 5. Other notes (not orphans, but worth recording)

### 5.1 No CLI flag orphans

`ember --allow-tools`, `--no-tools`, `--config-root` all handled.
`ember mcp list/tools/ping/serve --transport` all handled.

### 5.2 No service-class orphans

Every `Service` class is constructed in the right place. Every
`Message` class is both posted and subscribed.

### 5.3 No audit-log field orphans

Every field written to the audit log is documented in
`docs/decisions/0011-tool-use-framework.md` and read by either tests
or operator-facing CLI flows.

### 5.4 ADR placeholders that haven't ratified

- **ADR-0012** (Auga / Rödd / Bifröst) — placeholder slice-3 ADR.
  Not ratified. Bifröst is now plausibly bifrost-the-sibling-project;
  Auga + Rödd remain conceptual.
- **ADR-0015** (Stofa TUI) — not drafted yet. Will draft when
  implementation begins.
- **ADR-0016+** — reserved for future slice work.

---

## How to use this file

When you (or a future Mythic-Engineering sweep) notices something
that *should* exist but doesn't, OR something that *exists* but
isn't connected, add a section here. When something gets wired,
move it to "Historical" at the bottom (delete-not-yet-needed
material) or remove it.

This is the **load-bearing inventory** of what's unfinished in the
repo at any given commit.

---

## Historical (resolved orphans, kept for context)

Orphans we previously found and wired up — DO NOT re-add unless
they re-orphan:

- `LoggingConfig.level/format/destinations` — wired in Batch J via
  `src/ember/logging.py`.
- `ToolDescriptor.timeout_s` — enforced in Batch J via chat.py's
  `_execute_with_timeout`.
- `ToolsConfig.allow_private_addresses` — wired in Batch J via
  `fetch_url.bind_allow_private_default`.
- MCP doctor's Funi probe — wired in Batch J (was previously stubbed
  to None).
- `tests/unit/test_hardening_batch_a.py` `/tmp/` literals — replaced
  with `tmp_path` fixture in Batch H.

---

## Audit metadata

- **Last audited:** 2026-05-21 at HEAD `02ded16`.
- **Auditor:** Mythic-Engineering Sólrún + Explore subagent.
- **Method:** grep for declarations vs grep for callers across `src/`
  + manual verification of suspect findings.
- **Re-audit when:** new code lands in `src/ember/`, new sibling
  project added, new ADR drafted, or quarterly otherwise.
