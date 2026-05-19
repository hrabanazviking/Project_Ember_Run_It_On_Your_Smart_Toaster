# DOMAIN_MAP — Subsystem Ownership

**Voice:** Architect (Rúnhild Svartdóttir)
**Status:** Bootstrap-stage — these boundaries hold until the first slice of `core/` lands. Any later code that wants to violate a boundary must amend this document and add an ADR under `docs/decisions/` *before* the violation is committed.
**Last touched:** 2026-05-17 (P7)

---

## 0. How to read this document

For every subpackage of `src/runa/`, this document gives:

- **Purpose** — one sentence. If a subpackage cannot be described in one sentence, its boundary has already failed.
- **True Name** — the named subsystem from `docs/SYSTEM_VISION.md` that lives here (when applicable).
- **Owns** — the data, behaviours, and invariants that are this subpackage's responsibility.
- **Does not own** — explicit negative space.
- **May import from** — the only subpackages whose code may appear in `import` statements here.
- **May be imported by** — the only subpackages permitted to import from here.
- **Failure semantics** — what happens to the rest of the agent when this subpackage fails.

Two iron rules sit on top of every row:

1. **Dependency direction is strict.** If `core/` may not import `services/`, then no file under `core/` may name any module under `services/` in any way — no late imports, no `importlib`, no string-built module paths. The boundary is mechanical.
2. **Every subpackage has exactly one INTERFACE.md.** Anything not on the surface declared in that INTERFACE.md is private to the subpackage.

---

## 1. `src/runa/schemas/`

- **Purpose:** Pydantic models, dataclasses, and shared type definitions used in two or more other subpackages.
- **True Name:** *(none — this is structural, not mythic)*
- **Owns:** Type definitions, validation rules, version markers for on-disk shapes.
- **Does not own:** Behaviour. A schema may define a type; it may not define a method that does work.
- **May import from:** Standard library only. Optional `pydantic`, `typing_extensions`, `enum`. No `runa.*` imports.
- **May be imported by:** Everything in `src/runa/`.
- **Failure semantics:** A failure here means the package will not load — there is no graceful degradation. Tests guarantee `runa.schemas` imports cleanly.

## 2. `src/runa/migrations/`

- **Purpose:** Versioned migrations for the on-disk state stores (Muninn memory, Skuld task ledger, WYRD-bridge snapshot, emotional journal, identity store).
- **True Name:** *(none — operational, not mythic)*
- **Owns:** Migration scripts named `NNNN_short_description.py`, the migration-runner protocol, the recorded current-version-per-store.
- **Does not own:** The stores themselves. Migrations *operate on* stores owned by `core/`.
- **May import from:** `runa.schemas` only.
- **May be imported by:** `runa.runtime` (for `runa state migrate`). Nothing else.
- **Failure semantics:** A migration failure halts startup. The runtime's `doctor` command reports the failure with the migration ID and the precise error. State is never partially-migrated — each migration is transactional.

## 3. `src/runa/core/`

- **Purpose:** The agent itself — kernel, event bus, task ledger, memory OS, world-model bridge, emotional state, model router, tool forge, identity, policy.
- **True Names:** **VERÐANDI** (event bus), **Skuld** (task ledger), **Muninn** (memory OS), **WYRD bridge** (world-model adapter, not WYRD itself), **Eldhugi** (emotional state engine, provisional), **Heimskringla** (model router), **Smiðja** (tool forge), **Hirð** (subagent hall with named retainers Huginn / Muninn-as-specialist / Völundr / Eir / Heimdallr / Saga).
- **Owns:** All agent reasoning, all persistent agent state, all internal communication between Runa's parts.
- **Does not own:** Any user-facing surface. Any external network call (those go through `adapters/`). Any process supervision (that's `runtime/`).
- **May import from:** `runa.schemas`, `runa.migrations` (the latter only via `runa.core.<store>` invoking the runner).
- **May be imported by:** `runa.runtime`, `runa.services`, `runa.apps`, `runa.adapters`, `runa.plugins`, `runa.skills`.
- **Failure semantics:** `core/` *is* the agent. A core failure is a service-down event. The runtime captures it, writes a crash record to `~/.runa/state/crashes/`, and restarts via the supervisor.

### 3.1 Subdomains within `core/`

The `core/` package is itself partitioned. The same boundary rules apply between these subdomains:

| Subdomain | True Name | One-sentence purpose |
|---|---|---|
| `core/kernel/` | — | The orchestration loop that consumes events, dispatches to skills/tools/subagents, and emits results. |
| `core/eventbus/` | **VERÐANDI** | The in-process pub/sub bus along which every agent action and observation flows. |
| `core/tasks/` | **Skuld** | The persistent task ledger — durable, recoverable, append-only. |
| `core/memory/` | **Muninn** | The memory OS — short-term, long-term, episodic, semantic, retrieval index. |
| `core/world/` | **WYRD bridge** | The adapter into the external WYRD world-model service. |
| `core/emotions/` | **Eldhugi** | The mood/energy/relational state engine. |
| `core/models/` | **Heimskringla** | The model router — provider selection, retry, fallback, budget. |
| `core/tools/` | **Smiðja** | The tool forge — filesystem, shell, git, browser, MCP, network. |
| `core/subagents/` | **Hirð** | The subagent hall with the named retainers. |
| `core/repair/` | **Eir** | The health-and-repair system — drift detection, vacuum, restart, restore. |
| `core/identity/` | — | Runa's identity and personality continuity — name, voice, history, self-description. |
| `core/policy/` | — | The standing-trust policy engine — what Runa may do without asking, what she will refuse. |
| `core/logging/` | — | Structured logging configuration and audit-log writers. |
| `core/config/` | — | Config loading, validation, hot-reload. |

Each `core/<subdomain>/` carries its own `INTERFACE.md`. Cross-subdomain communication inside `core/` goes through the event bus where possible; direct imports are allowed only where declared in the importer's `INTERFACE.md`.

## 4. `src/runa/runtime/`

- **Purpose:** Process supervision and control-plane commands — start, stop, restart, status, doctor, logs, backup, snapshot, restore, migrate.
- **True Name:** *(none — operational)*
- **Owns:** Service lifecycle, signal handling, PID files, supervisor logic, the `runa state` / `runa memory` / `runa config` / `runa doctor` / `runa logs` command implementations.
- **Does not own:** The user-facing CLI parser (that's `cli/`). Reasoning (that's `core/`).
- **May import from:** `runa.schemas`, `runa.migrations`, `runa.core`.
- **May be imported by:** `runa.cli`, `runa.services`.
- **Failure semantics:** Runtime failure is *visible* — the supervisor itself is the last fallback. If it dies, `systemd` (or equivalent) is expected to restart it.

## 5. `src/runa/cli/`

- **Purpose:** The `runa` command-line entry point — argument parsing, subcommand dispatch, output formatting.
- **True Name:** **Munnr** (the mouth — where Runa is summoned by command)
- **Owns:** Argument parsers, subcommand table, terminal output rendering.
- **Does not own:** Any actual work. The CLI is a router; behaviour lives in `runtime/` and `core/`.
- **May import from:** `runa.schemas`, `runa.runtime`.
- **May be imported by:** Nothing — `cli/` is a leaf.
- **Failure semantics:** A CLI parse failure prints help and exits non-zero. Subcommand failures bubble up exit codes from `runtime/`.

## 6. `src/runa/services/`

- **Purpose:** Long-running service wrappers — each pairs `runa.core` with a specific I/O surface and lifecycle.
- **True Names:** Each service wraps a Face-of-the-World True Name (see `apps/` row).
- **Owns:** Lifecycle of one service (start, healthcheck, graceful stop), IPC between that service and the kernel, deployment metadata referenced by `deploy/systemd/`.
- **Does not own:** The user-experience layer of any surface (that's `apps/`). Anything inside `core/`.
- **May import from:** `runa.schemas`, `runa.core`, `runa.runtime`, `runa.apps`.
- **May be imported by:** `runa.cli` (to launch a service), tests, `deploy/`.
- **Failure semantics:** Each service is independently failable. A failed service is logged and may be restarted by the supervisor; other services keep running.

## 7. `src/runa/apps/`

- **Purpose:** The user-experience layer for each surface — actual GUI window, actual voice loop, actual interactive CLI shell, actual gateway HTTP server.
- **True Names:** **Auga** (GUI), **Rödd** (voice), **Bifröst** (gateway).
- **Owns:** What the user sees, hears, or types against on each surface. UI state machines, voice barge-in handling, gateway request lifecycle.
- **Does not own:** Process lifecycle (that's `services/`). Agent reasoning (that's `core/`).
- **May import from:** `runa.schemas`, `runa.core` (read-only and through `core`'s declared interface).
- **May be imported by:** `runa.services`.
- **Failure semantics:** A failure in one app fails only that surface. The agent remains addressable through the other surfaces.

## 8. `src/runa/adapters/`

- **Purpose:** Connections to specific external systems — Discord, Telegram, Matrix, MCP servers, Home Assistant, model providers (OpenRouter, Nous, Ollama, LM Studio), email, webhooks.
- **True Names:** *(adapters are tributary streams to **Bifröst** and to **Heimskringla**)*
- **Owns:** One subfolder per adapter, each containing: the adapter's translation layer, its configuration schema, its retry/backoff policy, its degraded-operation behaviour.
- **Does not own:** Agent reasoning. The transport contract of the adapter's own external system is *external* to this repo — adapters are pure translation.
- **May import from:** `runa.schemas`, the external library for the adapter's system, `runa.core` (only the narrow message types declared in `runa.core.<surface>.INTERFACE.md`).
- **May be imported by:** `runa.services`, `runa.apps`, tests.
- **Failure semantics:** **Critical.** Every adapter is independently failable. The agent must start, run, and remain usable when any adapter fails to import, fails to authenticate, or loses its external connection at runtime. A broken adapter is logged, quarantined, and surfaced via `runa doctor`; it does not take any other adapter down.

## 9. `src/runa/plugins/`

- **Purpose:** Plugin loader, plugin sandbox, plugin discovery, plugin lifecycle.
- **True Name:** *(none — extension surface)*
- **Owns:** The plugin contract, the loader, the sandbox boundary, the registry of currently-loaded plugins, plugin-failure isolation.
- **Does not own:** The plugins themselves (those live outside this repository).
- **May import from:** `runa.schemas`, `runa.core` (a narrow declared interface).
- **May be imported by:** `runa.runtime` (for `runa plugin install/remove/list`), `runa.services`.
- **Failure semantics:** **Critical.** A misbehaving plugin must never take the agent down. The sandbox boundary is checked in tests; if it leaks, that is a release-blocking bug.

## 10. `src/runa/skills/`

- **Purpose:** First-party agent-facing capabilities — things Runa can do that are too small for a subsystem and too internal for an adapter.
- **True Name:** *(skills are the muscle of the kernel and the **Hirð**)*
- **Owns:** The skill contract, the skill registry, each first-party skill implementation.
- **Does not own:** Anything that ought to be a subagent in `core/subagents/`. Anything externally addressable (that's an adapter).
- **May import from:** `runa.schemas`, `runa.core`.
- **May be imported by:** `runa.core.kernel` (via the skill registry).
- **Failure semantics:** A skill failure surfaces to the kernel as a typed error; the kernel decides whether to retry, route to a different skill, or report degraded operation. Skills must not raise unhandled exceptions to the event bus.

---

## 11. Cross-cutting concerns

These concerns are spread across many subpackages — their ownership is declared once here to prevent drift.

| Concern | Owned by | How |
|---|---|---|
| Logging | `core/logging/` | All subpackages obtain loggers via `runa.core.logging.get_logger(__name__)`. Never `print`, never raw `logging.getLogger`. |
| Configuration | `core/config/` | All subpackages read config via the typed accessor in `core.config`. No subpackage reads files directly. |
| Errors | `runa.schemas.errors` | All exception classes raised across subpackage boundaries are defined here. Inside-subpackage errors are internal. |
| Time | `core/clock` (planned) | All time-sensitive code uses an injected clock — never `datetime.now()` direct in business logic — so tests are deterministic. |
| Identity | `core/identity/` | Runa's name, voice, persona, history. Read by `apps/` and `adapters/` for surface presentation. |
| Policy | `core/policy/` | The standing-trust rules — read by the kernel, by skills, by the tool forge before any non-trivial action. |

---

## 12. What this map does *not* yet decide

The following are deliberately left open and will be decided when their slice ships:

- Whether `core/world/` (WYRD bridge) talks to WYRD via local IPC, over Tailnet, or both — that's `docs/decisions/0NNN-wyrd-transport.md` when it lands.
- Whether `core/models/` (Heimskringla) caches model responses in a shared store or per-provider — that's a Heimskringla-slice ADR.
- The exact wire format on `core/eventbus/` (VERÐANDI) — JSON vs MessagePack vs in-process Python objects.
- Whether plugins run in-process, out-of-process, or in a WASM sandbox.

Each of these will earn an ADR before the corresponding `INTERFACE.md` is filled in.
