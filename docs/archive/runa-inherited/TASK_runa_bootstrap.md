# TASK — Runa Agent Bootstrap (Mythic Engineering Sacred Setup)

**Task owner:** Runa Gridweaver Freyjasdottir (AI working under Volmarr)
**Branch:** development
**Started:** 2026-05-17
**Status:** P0 complete (orientation + planning + this file) — P1 next
**Mode:** Full autonomous Sacred Setup (Volmarr authorized: all 12 phases in one session)

---

## 0. Purpose of this file

This task file is the *resumption anchor*. If this session is interrupted at any point — context limit, crash, disconnect, Volmarr returns next week — any future session can read this file alone and pick up exactly where work stopped. The Status Tracker at the bottom is updated after every completed phase.

---

## 1. Task scope (one paragraph)

Take the Runa-Agent-Digital-Being repo from its current state — a vision-stage repo with ~30 plundered markdown design docs piled at the repository root, 9 image files at root, an empty `config.yaml`, no folder structure, no source code — and bring it into full Mythic Engineering Sacred Setup form: canonical ME documents at root, layered `docs/` subfolders containing the sorted plundered material, `src/runa/` skeleton matching the FILE_ORG guide layout, `tests/` / `config/` / `scripts/` / `deploy/` / `tools/` / `examples/` / `vendor/` / `assets/` directories with placeholder READMEs, INTERFACE.md stubs in each src subdomain, real attribution register in `ORIGINS.md`, polished front-door README, and `pyproject.toml` + `.gitignore` + `.env.example` scaffolding. No production code is written in this bootstrap — documentation and structure only.

## 2. Strategic decisions (locked by Volmarr 2026-05-17)

| Decision | Chosen | Source |
|---|---|---|
| Repo layout | `src/runa/` (FILE_ORG guide) | Volmarr AskUserQuestion 2026-05-17 |
| Plundered docs disposition | Sort into `docs/` subfolders | Volmarr AskUserQuestion 2026-05-17 |
| Pace | Full autonomous Sacred Setup | Volmarr AskUserQuestion 2026-05-17 |
| ME methodology | `~/.claude/rules/practical_mythic_engineering_step_by_step.md` (Volmarr's global rules) | Standing |
| Coding laws | `RULES.AI.md` at root | Standing |
| Image references | Relative paths only (Law of Flexible Roots) | Standing |

## 3. Starting inventory (2026-05-17, fresh clone)

**Branches:** `main`, `development` (default). Working branch: `development`.

**Root files (37 + .git):**

| File | Size | Provisional disposition |
|---|---|---|
| `README.md` | 41 KB | Stay at root (front door) — polish in P9 |
| `LICENSE` | 1.1 KB | Stay at root |
| `NOTICE` | 380 B | Stay at root |
| `LEGAL-NOTICE.md` | 3.3 KB | Stay at root |
| `THIRD_PARTY_NOTICES.md` | 755 B | Stay at root |
| `PHILOSOPHY.md` | 3.9 KB | Stay at root (ME canonical) — escape-cleanup in P6 |
| `MYTHIC_ENGINEERING.md` | 289 B | Stay at root — expand in P9 |
| `ORIGINS.md` | 587 B (stub) | Stay at root — fill in P3 |
| `RULES.AI.md` | 20 KB | Stay at root |
| `config.yaml` | 0 B (empty) | Move to `config/runa.example.yaml` |
| `Heathen_Third_Path_and_Cyber-Viking_Ethos.md` | 31 KB | `docs/philosophy/` |
| `Volmarr_writings_philosophy.md` | 39 KB | `docs/philosophy/` |
| `The_Saga_of_Runa.md` | 26 KB | `docs/philosophy/` |
| `ROBUST_AGENT_ENGINEERING_PLAN.md` | 19 KB | `docs/architecture/` |
| `Technical_Architecture_of_Volmarrs_AI_Ecosystem.md` | 55 KB | `docs/architecture/` |
| `Runa-Agent-Digital-Being.md` | 48 KB | `docs/architecture/` |
| `Runa_Agent_Digital_Being.md` | 65 KB | `docs/architecture/` (review for dupe vs above in P1) |
| `RUNA_ADVANCED_AGI_ENGINEERING_GUIDE.md` | 36 KB | `docs/design/` |
| `WORLD_MODELING_SKILL.md` | 19 KB | `docs/design/` |
| `RUNA_ECOSYSTEM_IDEA_HARVEST.md` | 31 KB | `docs/design/` |
| `RUNAFREYJASDOTTIR_GITHUB_CODE_HARVEST.md` | 37 KB | `docs/design/` |
| `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` | 43 KB | `docs/operations/` |
| `HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md` | 25 KB | `docs/decisions/` |
| `Mythic_Engineers_Codex.md` | 88 KB | `docs/methodology/` |
| `Mystic_Engineering_Protocals1.0.md` | 170 KB | `docs/methodology/` |
| `MYTHIC_ENGINEERING_PLUNDERING_WORKFLOW.md` | 31 KB | `docs/methodology/` |
| 8 UUID-named `.jpg/.jpeg` | ~2.3 MB total | `assets/` |
| `IMG_0665.jpeg`, `IMG_0666.jpeg` | ~800 KB | `assets/` (re-name to descriptive in later pass) |
| `MIT_license_Rune_Forge_AI.jpeg` | 418 KB | `assets/` |

**No directories at root** other than `.git`. Confirms greenfield structural state.

**README.md image references:** 7 absolute `raw.githubusercontent.com/.../main/<uuid>.jpg` URLs need rewriting to relative `./assets/<uuid>.jpg` in P5.

## 4. Target end-state shape

```text
runa-agent/                              # repo root
  README.md
  LICENSE / NOTICE / LEGAL-NOTICE.md / THIRD_PARTY_NOTICES.md
  PHILOSOPHY.md
  MYTHIC_ENGINEERING.md                  # expanded in P9
  ORIGINS.md                             # filled in P3
  RULES.AI.md
  TASK_runa_bootstrap.md                 # this file, removed at P12 only if Volmarr says so
  pyproject.toml                         # stub from P11
  .python-version / .env.example / .gitignore

  docs/
    REPO_MAP.md                          # P8
    SYSTEM_VISION.md                     # P6
    DEVLOG.md                            # P11
    architecture/   {DOMAIN_MAP, ARCHITECTURE, DATA_FLOW + moved plundered}
    operations/     {FILE_ORG guide + later runbooks}
    development/    {placeholder}
    design/         {moved harvest/skill/idea docs}
    security/       {placeholder}
    adapters/       {placeholder}
    plugins/        {placeholder}
    decisions/      {ADR-style + HERMES anti-patterns}
    philosophy/     {Heathen/Saga/Volmarr writings}
    methodology/    {Mythic Engineers Codex, Mystic Protocols, Plundering Workflow}

  config/
    runa.example.yaml                    # from empty config.yaml
    profiles/

  src/runa/
    __init__.py / __main__.py
    cli/         INTERFACE.md
    runtime/     INTERFACE.md
    core/        INTERFACE.md
    services/    INTERFACE.md
    apps/        INTERFACE.md
    adapters/    INTERFACE.md
    plugins/     INTERFACE.md
    skills/      INTERFACE.md
    schemas/     INTERFACE.md
    migrations/  INTERFACE.md

  tests/         {unit,integration,e2e,fixtures,snapshots}
  scripts/       {dev,maintenance,one_shot}
  deploy/        {systemd,docker,pi,examples}
  tools/         {repo,diagnostics,importers}
  examples/      {configs,sessions,skills,plugins}
  vendor/        README only
  assets/        9 image files + assets-README
```

## 5. Out of scope for this bootstrap

- Writing any actual Python implementation under `src/runa/`. INTERFACE.md stubs only.
- Real dependency choices in `pyproject.toml` (stub with name/version/Python only).
- Decision records (ADRs) other than placeholder file in `docs/decisions/`.
- Wiring CI / GitHub Actions.
- Cleanup of duplicate vision content between `Runa-Agent-Digital-Being.md` and `Runa_Agent_Digital_Being.md` — flag for later, do not merge in this session.
- Renaming the UUID-named images to descriptive names — defer.

## 6. Operating procedure

1. After each phase: update Status Tracker in §8, `git add -A && git commit -m "bootstrap: P<N> <summary>"`, `git push origin development`. This is the resumption checkpoint.
2. Never delete an existing file in the same commit as moving its replacement in — additive-only law. If a file is being retired, move it to `docs/archive/` rather than rm.
3. Never use absolute paths in any doc or config (Law of Flexible Roots).
4. Use `git mv` not raw `mv`/`Move-Item` so history follows the file.
5. If a phase reveals a structural problem not anticipated here, append a §7 deviation note before continuing.

## 7. Deviations from plan (append-only)

*(none yet)*

## 8. Status Tracker

| Phase | Description | Status | Commit |
|---|---|---|---|
| P0 | Orientation, clarifying Qs, this file | completed | f437a29 |
| P1 | Cartographer pre-pass — classify every root doc | completed | (folded into P0 §3 inventory) |
| P2 | Build folder skeleton (FILE_ORG layout) | completed | 22cd6c5 |
| P3 | Fill ORIGINS.md attribution register | completed | d068c95 |
| P4 | git-mv plundered docs into docs/ subfolders | completed | 68b349d |
| P5 | Move images to assets/ + rewrite README refs | completed | 166d00f |
| —  | Reconcile main-merge — remove 4 root-duplicate images (Volmarr's `b57a241` brought them back; bytewise-identical to `assets/` copies; root copies removed) | completed | 50db3dd |
| P6 | Skald — refine PHILOSOPHY + SYSTEM_VISION | completed | 5e1fc0d |
| P7 | Architect — DOMAIN_MAP + ARCHITECTURE | completed | 1a97884 (was aab5797 pre-rebase) |
| P8 | Cartographer — DATA_FLOW + REPO_MAP | completed | 3ca55e3 |
| P9 | Scribe — polish MYTHIC_ENGINEERING + folder READMEs | completed | a8e44b1 |
| P10 | INTERFACE.md stubs in each src/runa/* | completed | 6b46c70 |
| P11 | Top-level scaffolding (pyproject, gitignore, env, DEVLOG, __init__) | completed | 5c6ccdb |
| P12 | Auditor pass + final closing ADR | completed | (this commit) |

**Bootstrap closed 2026-05-17.** All 12 phases shipped. See `docs/decisions/0001-mythic-engineering-bootstrap-2026-05-17.md` for the formal closing ADR and `docs/DEVLOG.md` for the per-phase record.

## 9. Next exact action (for any resuming session)

If P0 is `in_progress`: finish the P0 commit (`git add TASK_runa_bootstrap.md && git commit && git push`), then proceed to P1.

If a later phase is `in_progress`: read its row above for what was being done, read the most recent commit on `development` for what landed, then continue.

If all phases are `completed`: read the closing report referenced from P12 and ask Volmarr for the next task.
