# REPO_MAP — One Line for Every Place

**Purpose:** The operator's second stop after `README.md`. If you are lost in the repository, you read this file. Every folder gets one line; every line says what lives there and where to go for more.
**Voice:** Cartographer (Védis Eikleið)
**Last touched:** 2026-05-17 (P8)
**Reads with:** `docs/SYSTEM_VISION.md`, `docs/architecture/{ARCHITECTURE,DOMAIN_MAP,DATA_FLOW}.md`, `ORIGINS.md`.

---

## Root

| Path | One-line meaning |
|---|---|
| `README.md` | The front door. Install + start + most-important commands. |
| `LICENSE` | MIT, Volmarr Wyrd 2026. |
| `NOTICE` | Copyright + pointer to LICENSE + THIRD_PARTY_NOTICES. |
| `LEGAL-NOTICE.md` | Author's distribution stance, no-personal-info policy, third-party packaging disclaimer. |
| `THIRD_PARTY_NOTICES.md` | Attribution for any vendored third-party material. |
| `PHILOSOPHY.md` | The compact ethos statement. Long form lives at `docs/philosophy/`. |
| `MYTHIC_ENGINEERING.md` | How we build. Compact statement; long form at `docs/methodology/`. |
| `ORIGINS.md` | Attribution register: where every imported file came from. |
| `RULES.AI.md` | Standing coding laws for human and AI contributors. |
| `TASK_runa_bootstrap.md` | Resumption anchor for the 2026-05-17 ME Sacred Setup. May be archived once setup closes. |
| `config.yaml` | Empty stub remaining at root until P11 moves it to `config/runa.example.yaml`. |

## `docs/`

| Path | One-line meaning |
|---|---|
| `docs/README.md` | Map of every doc subfolder. |
| `docs/SYSTEM_VISION.md` | Skald-written living vision statement: Primary Rite, Vows, True Names, Realms. |
| `docs/REPO_MAP.md` | *(this file)* |
| `docs/DEVLOG.md` | *(created P11)* Append-only per-session record. |
| `docs/architecture/` | `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` plus the long-form architectural source docs imported from earlier projects. |
| `docs/operations/` | Operator runbooks (planned: INSTALL, STARTUP, OBSERVABILITY, BACKUP_RESTORE, INCIDENT_RUNBOOK). Source: `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md`. |
| `docs/development/` | How to contribute, dev setup, testing, style. |
| `docs/design/` | Long-form design explorations; idea harvests; deep dives that informed architecture but are not the spec. |
| `docs/security/` | Threat model, trust boundaries, secrets, sandbox policy. |
| `docs/adapters/` | One contract doc per external adapter. |
| `docs/plugins/` | Plugin author contract, sandboxing, registry. |
| `docs/decisions/` | Architecture Decision Records (`NNNN-short-name.md`). Append-only. |
| `docs/philosophy/` | Heathen + modern-Viking + Mythic worldview source documents. |
| `docs/methodology/` | Mythic Engineering canonical reference: Codex, Protocols v1.0, Plundering Workflow. |
| `docs/research/` | **100-document AI/CS research library** (added 2026-05-17). Corpus I (docs 01–50) — foundational concept syntheses; ADR-0003. Corpus II (docs 51–100) — AGI-frontier deep dive on self-awareness, cross-session memory, 3D / virtual / physical / game awareness, theory of mind, AI Operating System, world modeling, 2025–2026 frontier; ADR-0005. Architect's reading. |
| `docs/python/` | **50-document Python craft corpus** (added 2026-05-17). Implementation patterns for robust, self-healing, crash-proof Python software. Forge Worker's reading. See ADR-0004. |
| `docs/AI_OS_Research/` | Volmarr's parallel research on the 2026 AI-OS market / standards / research landscape. Companion to `docs/research/`. |
| `docs/RunaUniversity2040/` | Volmarr's lecture series / AI curriculum material. |
| `docs/archive/` | Retired docs preserved for history. Never deleted; superseded docs go here. |

## `config/`

| Path | One-line meaning |
|---|---|
| `config/README.md` | Rules for the config layer; what lives here vs what lives in `~/.runa/`. |
| `config/profiles/` | Named bundles of partial config for common deployment shapes. |
| *(planned)* `config/runa.example.yaml` | Main agent configuration template. |
| *(planned)* `config/logging.example.yaml` | Log sinks, levels, rotation. |
| *(planned)* `config/models.example.yaml` | Model-provider routing for Heimskringla. |
| *(planned)* `config/permissions.example.yaml` | Tool capability allow-lists per surface. |

## `src/`

| Path | One-line meaning |
|---|---|
| `src/README.md` | Why we use PEP-517 src-layout. |
| `src/runa/` | The Runa Python package; everything below is its internals. |
| `src/runa/cli/` | **Munnr** — the `runa` command-line entry point. Thin parser + dispatcher. |
| `src/runa/runtime/` | Process supervision and control-plane commands (start/stop/status/doctor/logs/snapshot/restore/migrate). |
| `src/runa/core/` | **The agent itself** — kernel + VERÐANDI + Skuld + Muninn + WYRD-bridge + Eldhugi + Heimskringla + Smiðja + Hirð + Eir + identity + policy. |
| `src/runa/services/` | Long-running service shells (gateway, worker, voice, gui). Lifecycle and IPC. |
| `src/runa/apps/` | User-experience layer per surface — **Auga** (GUI), **Rödd** (voice), **Bifröst** (gateway), interactive Munnr shell. |
| `src/runa/adapters/` | One subfolder per external system (Discord, Telegram, Matrix, MCP, Home Assistant, OpenRouter, Ollama, LM Studio, …). |
| `src/runa/plugins/` | Plugin loader, sandbox, discovery, lifecycle. Plugins themselves live outside the repo. |
| `src/runa/skills/` | First-party agent-facing capabilities. |
| `src/runa/schemas/` | Pydantic models and shared types. Floor of the dependency graph. |
| `src/runa/migrations/` | Versioned state-store migrations. |

## `tests/`

| Path | One-line meaning |
|---|---|
| `tests/README.md` | Tiering rules; what each tier may and may not do. |
| `tests/unit/` | Single-module tests. No real network, no real disk outside `tmp_path`. |
| `tests/integration/` | Multi-module flows. Local SQLite, stub models, no public internet. |
| `tests/e2e/` | Through the real `runa` CLI / gateway. Marker-gated; slow. |
| `tests/fixtures/` | Reusable test data: seed memory, sample conversations, mock model responses. |
| `tests/snapshots/` | Golden-file outputs. |

## `scripts/`

| Path | One-line meaning |
|---|---|
| `scripts/dev/` | Developer convenience: format, lint, regen-fixtures, rebuild-lockfile. |
| `scripts/maintenance/` | Operator maintenance: rotate-logs, vacuum-memory, prune-cache, export-state. Dry-run by default. |
| `scripts/one_shot/` | Rare dated migrations and fixups. Old ones preserved as historical record. |

## `deploy/`

| Path | One-line meaning |
|---|---|
| `deploy/systemd/` | User-level `*.service` files for runa-core / runa-gateway / runa-voice / runa-worker. |
| `deploy/docker/` | Dockerfile(s) and compose for containerised deployment (multi-arch). |
| `deploy/pi/` | Raspberry Pi 5 install + first-boot + thermal/swap tuning. |
| `deploy/examples/` | Reference deployment shapes (single-pi, pi-and-laptop, longhall). |

## `tools/`

| Path | One-line meaning |
|---|---|
| `tools/repo/` | Repo-shape checks: INTERFACE presence, README presence, link integrity, ORIGINS drift. |
| `tools/diagnostics/` | Live-Runa read-only inspectors: VERÐANDI tail, Muninn integrity, Skuld snapshot, world inspect. |
| `tools/importers/` | One-way imports from other Volmarr projects; each run documented in `docs/decisions/`. |

## `examples/`

| Path | One-line meaning |
|---|---|
| `examples/configs/` | Fully-worked example `runa.yaml` per deployment shape. |
| `examples/sessions/` | Redacted transcripts of meaningful sessions; doubles as eval fixtures. |
| `examples/skills/` | Reference skill packages a third party can fork. |
| `examples/plugins/` | Reference plugin packages a third party can fork. |

## `vendor/`

| Path | One-line meaning |
|---|---|
| `vendor/` | Third-party code that lives inside the repo. Currently empty; vendoring criteria in `vendor/README.md`. |

## `assets/`

| Path | One-line meaning |
|---|---|
| `assets/` | Images and binary media referenced from docs. UUID-named jpgs are AI-generated Runa illustrations; `IMG_NNNN.jpeg` are camera/screenshot; `MIT_license_Rune_Forge_AI.jpeg` is a licensing illustration. All references from `.md` use relative `./assets/...` paths. |

---

## Top-level shape, at a glance

```
runa-agent-digital-being/
├── README.md                 ← front door
├── PHILOSOPHY.md             ← ethos (compact)
├── MYTHIC_ENGINEERING.md     ← method (compact)
├── ORIGINS.md                ← attribution register
├── RULES.AI.md               ← coding laws
├── LICENSE / NOTICE / LEGAL-NOTICE.md / THIRD_PARTY_NOTICES.md
├── TASK_runa_bootstrap.md    ← bootstrap resumption anchor
│
├── docs/                     ← all written material
│   ├── architecture/         ← what Runa IS
│   ├── operations/           ← how to run her
│   ├── development/          ← how to contribute
│   ├── design/               ← exploratory writing
│   ├── security/             ← trust boundaries
│   ├── adapters/             ← per-adapter contracts
│   ├── plugins/              ← plugin contract
│   ├── decisions/            ← ADRs
│   ├── philosophy/           ← worldview source
│   ├── methodology/          ← Mythic Engineering source
│   └── archive/              ← retired docs
│
├── config/                   ← templates (never live)
├── src/runa/                 ← all Python implementation
├── tests/                    ← unit/integration/e2e/fixtures/snapshots
├── scripts/                  ← dev/maintenance/one_shot
├── deploy/                   ← systemd/docker/pi/examples
├── tools/                    ← repo/diagnostics/importers
├── examples/                 ← configs/sessions/skills/plugins
├── vendor/                   ← third-party code (empty)
└── assets/                   ← images and binary media
```

Every directory shown carries a `README.md`. When you do not know where something belongs, that directory's README is the first place to look.
