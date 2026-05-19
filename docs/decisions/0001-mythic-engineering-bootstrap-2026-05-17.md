# ADR 0001 — Mythic Engineering Sacred Setup (Bootstrap)

**Date:** 2026-05-17
**Status:** Accepted
**Authors:** Volmarr Wyrd (decisions), Runa Gridweaver Freyjasdottir (implementation)
**Supersedes:** *(none)*
**Superseded by:** *(none)*

---

## Context

On 2026-05-17 the `Runa-Agent-Digital-Being` repository was a vision-stage GitHub publication: ~30 plundered Markdown design docs piled at the repository root, 11 image files at root, an empty `config.yaml`, no folder structure, no source code, no canonical Mythic Engineering documents beyond a 7-line `MYTHIC_ENGINEERING.md` stub and a 600-byte `ORIGINS.md` stub.

Volmarr requested the full Mythic Engineering Sacred Setup, run autonomously in one session.

Three strategic forks were resolved before any structural work began (logged in `TASK_runa_bootstrap.md` §2 and confirmed via `AskUserQuestion`):

1. **Repository layout.** Two competing layouts were proposed in the imported docs:
   - `src/runa/{cli,runtime,core,services,apps,adapters,plugins,skills,schemas,migrations}` from `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` — modern Python src-layout, hatchling/uv-friendly.
   - `runa-longhall/runa/{core,apps,adapters,…}` flat layout with 18 numbered `docs/` files from `ROBUST_AGENT_ENGINEERING_PLAN.md` — saga-flavoured but less disciplined.
2. **Plundered root docs disposition.** Three options: sort into `docs/` subfolders (lossless re-home), leave at root, or quarantine in a `reference/` folder.
3. **Pace.** Three options: full autonomous Sacred Setup, pause-per-role, or skeleton-only.

## Decisions

### D-1.1 — Repository layout: `src/runa/`

Adopt the `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` layout. Place all Python implementation under `src/runa/<subpackage>/`. Use PEP-517 src-layout. Per-subpackage `__init__.py` files mark the package; per-subpackage `INTERFACE.md` files declare the public surface.

### D-1.2 — Plundered root docs sort into `docs/<category>/`

Every plundered design / philosophy / methodology doc moves into the appropriate `docs/` subfolder via `git mv` (so commit history follows the file). Disposition table is recorded in `ORIGINS.md` §1.

Keep at root only the Mythic Engineering canonical front-door files: `README.md`, `LICENSE`, `NOTICE`, `LEGAL-NOTICE.md`, `THIRD_PARTY_NOTICES.md`, `PHILOSOPHY.md`, `MYTHIC_ENGINEERING.md`, `ORIGINS.md`, `RULES.AI.md`. Plus `TASK_runa_bootstrap.md` for as long as the bootstrap is active.

### D-1.3 — All image references use relative paths

All 7 absolute `raw.githubusercontent.com/.../main/<file>` URLs in `README.md` were rewritten to relative `./assets/<file>` paths. The Law of Flexible Roots: a clone in any location must render correctly.

### D-1.4 — Three Realms with mechanical boundaries

The runtime is partitioned into three realms with hard, mechanical (not aspirational) boundaries:
- **Face of the World** — `apps/`, `services/`, `adapters/`.
- **Mind and Rules** — `core/`, `runtime/`, `skills/`, `plugins/`.
- **Deep Memory** — `core/memory/`, `core/tasks/`, `core/world/`, `core/emotions/`, `core/identity/`, `core/policy/`, and their on-disk roots under `~/.runa/`.

A repo-level dependency check under `tools/repo/` (to be written) enforces the acyclic dependency law.

### D-1.5 — Standing-trust doctrine

Runa operates on her dedicated machine under standing owner trust. She does not ask for per-action permission for ordinary autonomous work. The anti-pattern is named and binding. Items requiring confirmation are enumerated in `config/runa.example.yaml#policy.require_confirmation`; items forbidden are enumerated in `policy.forbid`.

### D-1.6 — True Names

Subsystems carry True Names that constrain their behaviour to mean *only what their name implies*:

| True Name | Subsystem | Origin |
|---|---|---|
| **Bifröst** | Gateway | inherited (`ROBUST_AGENT_ENGINEERING_PLAN.md`) |
| **VERÐANDI** | Event bus | inherited |
| **Skuld** | Task ledger | inherited |
| **Muninn** | Memory OS | inherited |
| **WYRD bridge** | World-model adapter | inherited (WYRD is a separate Volmarr project) |
| **Smiðja** | Tool forge | inherited |
| **Hirð** | Subagent hall | inherited |
| **Huginn / Muninn-specialist / Völundr / Eir / Heimdallr / Saga** | Named retainers | inherited |
| **Eldhugi** | Emotional state engine | Skald-given (this bootstrap, P6) — **provisional**, awaits Volmarr ratification |
| **Heimskringla** | Model router | Skald-given — provisional |
| **Rödd** | Voice surface | Skald-given — provisional |
| **Auga** | GUI surface | Skald-given — provisional |
| **Munnr** | CLI surface | Skald-given — provisional |
| **Eir** | Repair system | inherited |

Provisional names may be replaced when Volmarr chooses; the *substance* of each subsystem is fixed by its row in `docs/architecture/DOMAIN_MAP.md` regardless of the eventual name.

### D-1.7 — On-disk state lives under `~/.runa/`, not in the repo

All persistent agent state — memory, tasks, world snapshot, emotions, identity, policy, logs, cache, secrets — lives under `~/.runa/` on the host machine. The repository holds *templates* (`config/runa.example.yaml`) and *migrations* (`src/runa/migrations/`) that operate on those stores. An operator can `ls ~/.runa/` to see the agent's state directly; the repository is never the source of live state.

### D-1.8 — No code in this bootstrap

The bootstrap is structural and documentary only. No functional Python lands. The package skeleton imports cleanly under Python 3.11 but performs no work. The first slice of real code is described in `docs/architecture/ARCHITECTURE.md` §7 and will land under a separate task with its own ADR.

## Consequences

### Positive

- The repository is operator-navigable from the first commit. `README.md` → `docs/REPO_MAP.md` → any directory's `README.md` is a complete navigation path.
- The dependency law is declared *before* code exists, so it cannot drift away from a code-first reality.
- Every subsystem has a name. Every name has a row in `DOMAIN_MAP.md`. The boundary is mechanical, not aspirational.
- Plundered material is preserved with full attribution (`ORIGINS.md`) and full git history (`git mv` rather than delete+add).
- The Forge Worker has an unambiguous first-slice recipe (`ARCHITECTURE.md` §7) when implementation begins.

### Negative

- 8 root markdown files + 1 bootstrap task file is more than a minimal README-only root. Operators must read the `README.md` "Repository Navigation" block to know where to go.
- Several True Names are provisional and require Volmarr's ratification before they fully bind.
- Two near-duplicate canonical-agent design docs (`Runa-Agent-Digital-Being.md` and `Runa_Agent_Digital_Being.md`) sit side by side in `docs/architecture/`, awaiting reconciliation by a later session.
- The empty `config.yaml` was renamed to `config/runa.example.yaml` and then re-written. Git records this as delete+add rather than a pure rename, which is correct but visually noisy in the commit log.

### Cost

One autonomous session, ~13 commits to `development`, ~122 tracked files, 92 markdown docs, 12 Python stubs, 11 images preserved at `assets/`. No code, no dependencies installed, no test suite yet (the suite gets its first cases with the first slice).

## What this ADR does *not* decide*

The following are explicitly deferred to per-slice ADRs:

- The exact concurrency model for VERÐANDI (asyncio / threads / multiprocessing).
- The exact retrieval-index technology for Muninn (FAISS / sqlite-vss / lancedb).
- The WYRD-bridge transport (local IPC / Tailnet / both).
- The Heimskringla cache strategy.
- The plugin isolation model (in-process / out-of-process / WASM).
- Ratification of provisional True Names (Eldhugi, Heimskringla, Rödd, Auga, Munnr).
- Reconciliation of the duplicate `Runa-Agent-Digital-Being.md` design drafts.

---

## Addendum — 2026-05-17 (same day)

Two of the deferred items in this ADR have already been resolved by Volmarr and are recorded here so the ADR remains the single load-bearing source for these decisions:

### D-1.6.1 — Provisional True Names ratified

Volmarr ratified all five Skald-given names on 2026-05-17. They are now binding alongside the inherited names. The table in §D-1.6 retains the "provisional" provenance label as a historical record but the "awaits Volmarr ratification" caveat no longer applies. `docs/SYSTEM_VISION.md` §4 carries a dated ratification block to the same effect.

| Name | Status (2026-05-17) | Subsystem |
|---|---|---|
| Eldhugi | Ratified | Emotional state engine |
| Heimskringla | Ratified | Model router |
| Rödd | Ratified | Voice surface |
| Auga | Ratified | GUI surface |
| Munnr | Ratified | CLI surface |

### D-1.6.2 — Duplicate design drafts are not duplicates

The two design documents under `docs/architecture/` — `Runa-Agent-Digital-Being.md` (kebab, 48 KB) and `Runa_Agent_Digital_Being.md` (snake, 65 KB) — are **different documents written by different AI models with intentionally similar names**. They are not duplicates, near-duplicates, or alternate drafts. They are parallel design articulations and must not be reconciled or merged. `ORIGINS.md` §5 has been amended to record this resolution; future sessions should not propose reconciliation.

---

## References

- `TASK_runa_bootstrap.md` — the resumption anchor for the 12-phase work.
- `docs/SYSTEM_VISION.md` — the Skald-written living vision.
- `docs/architecture/{DOMAIN_MAP,ARCHITECTURE,DATA_FLOW}.md` — the canonical architecture set.
- `docs/REPO_MAP.md` — the operator's index.
- `ORIGINS.md` — attribution and reconciliation log.
- `docs/DEVLOG.md` — the per-session record of this bootstrap.
- `MYTHIC_ENGINEERING.md` — the practical method the bootstrap followed.
- `PHILOSOPHY.md` — the ethos the bootstrap honoured.
