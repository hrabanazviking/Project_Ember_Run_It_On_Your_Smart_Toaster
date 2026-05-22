# 81 — Phase 1: Observe and Borrow

The first Klóinn adoption phase. Low-cost, high-value
borrowings + foundational discipline.

---

## What Phase 1 ships

By the end of Phase 1:

- **Workspace prompt files** (AGENTS.md, SOUL.md, TOOLS.md)
  loaded into prompt assembly.
- **Sessions** as first-class concept (commands, storage,
  navigation).
- **Three release channels** (stable / beta / dev) on PyPI
  with CI automation.
- **Humarr Gateway** as named module (refactor of existing
  chat.py + munnr orchestration).
- **Onboarding refinements** (Hjarta branching by intent;
  `ember onboard` tour).
- **Shed Protocol bones** (deprecation warnings; migration
  framework; basic snapshots).
- **Pre-commit hooks** + CI improvements (multi-OS, multi-
  Python-version matrix).
- **CHANGELOG.md** maintained per release.
- **Carapace Defense** named + documented (existing layers
  formalized).

These are *cheap* changes. No new major dependencies.

---

## What Phase 1 doesn't include

Deferred:
- Bridges (Phase 2).
- Voice (Phase 2).
- Sandbox backends (Phase 2).
- Personas (Phase 3).
- Canvas (Phase 3).
- Web companion (Phase 3).

Phase 1 is *prep work + cheap wins*. The bigger features
come later.

---

## Work breakdown

### Track A: Workspace prompt files (~2 weeks)

Tasks:
1. Define workspace path; default `~/.ember/workspace/`.
2. Create default AGENTS.md, SOUL.md, TOOLS.md templates.
3. Implement prompt-assembly loader.
4. Auto-reload on file change.
5. TOOLS.md auto-generation option.
6. Workspace lint command.
7. Migration: copy existing identity.json values to
   AGENTS.md template (Shed-pattern).
8. Documentation + operator playbook.
9. Tests.

**Risk:** operators don't edit files; defaults are too
generic.  
**Mitigation:** ship reasonable defaults; document customization.

### Track B: Sessions (~3 weeks)

Tasks:
1. Define session boundaries.
2. Session storage (`~/.ember/state/sessions/`).
3. CLI commands: `/new`, `/end`, `/sessions list/show/resume`.
4. Auto-title generation.
5. Auto-summary after end (optional).
6. Stofa Episode Browser shows sessions.
7. Idle auto-close logic.
8. Tests + docs.

**Risk:** existing Episodes need migration.  
**Mitigation:** wrap existing Episodes into "legacy" session.

### Track C: Release channels (~2 weeks)

Tasks:
1. CI workflow for stable releases (on tag push).
2. CI workflow for beta/rc releases.
3. CI workflow for dev releases (on green main).
4. CHANGELOG.md template + discipline.
5. Documentation: how operators choose channel.
6. `ember update check` command.

**Risk:** dev releases clutter PyPI.  
**Mitigation:** retention policy (keep latest 5 devs).

### Track D: Humarr Gateway refactor (~3 weeks)

Tasks:
1. Define Surface Protocol.
2. Refactor `src/ember/spark/chat.py` into Gateway module.
3. Munnr + (planned) Stofa become Surface implementations.
4. Daemon mode opt-in (ephemeral remains default).
5. Tests for surface plug-in.
6. Documentation.

**Risk:** refactor breaks existing behavior.  
**Mitigation:** comprehensive integration tests; no behavior
change in observable scope.

### Track E: Onboarding refinements (~2 weeks)

Tasks:
1. Hjarta wizard branches by intent.
2. `ember onboard` post-setup tour.
3. `ember upgrade --tour` post-upgrade feature tour.
4. Improved Hjarta detection + suggestion.
5. Documentation.

**Risk:** wizard too long; operators abandon mid-setup.  
**Mitigation:** cap at 8 steps; show progress; allow skip.

### Track F: Shed Protocol bones (~2 weeks)

Tasks:
1. Define deprecation warning machinery.
2. Migration script framework + first scripts.
3. Snapshot-before-migration logic.
4. `ember shed list/migrate/restore` commands.
5. Documentation.

**Risk:** few migrations needed yet; complexity not
justified.  
**Mitigation:** ship infrastructure; populate later as needed.

### Track G: Cross-cutting (~2 weeks)

Tasks:
1. Pre-commit hooks (ruff, mypy, type-check).
2. CI matrix expansion (Linux + macOS + Windows; Python 3.12
   + 3.13 + 3.14).
3. ADR for Klóinn adoption.
4. DEVLOG entries.
5. Migration guide V0 → V1 (if Klóinn Phase 1 → V1.0
   timing).

---

## Total estimate

Roughly 16 weeks. Real-world: 3-5 months calendar.

This is *foundational work* — pays off compounding.

---

## What ship-readiness looks like

- [ ] All planned tests pass.
- [ ] Multi-OS CI green.
- [ ] Existing operators upgrade without breakage.
- [ ] Workspace prompt files default + work.
- [ ] Sessions usable end-to-end.
- [ ] Three release channels operational.
- [ ] Documentation updated.
- [ ] CHANGELOG.md has entries.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Refactor introduces regressions | High | Comprehensive integration tests |
| Operators don't adopt new features | Med | Defaults work; opt-in deeper |
| Multi-OS CI flakiness | Med | Per-OS specific tests; skip when unavoidable |
| Documentation lags code | High | Per-track doc requirement |

---

## What operators experience after Phase 1

### Old operators (V0 → V1)

```bash
$ ember upgrade

Klóinn Phase 1 brings new features. Run `ember onboard --new-features`
for a tour.

What's new in V1.0:
  - Workspace prompt files for personality control
  - Sessions: bounded conversation threads
  - Release channels: stable / beta / dev
  - Refined onboarding
```

Mostly compatible. Improvements are additive.

### New operators

```bash
$ pip install ember-agent
$ ember setup       # Hjarta with branching by intent
$ ember onboard      # 8-stop guided tour
$ ember chat         # all the V1 features available
```

Better first-impression than V0.

---

## What this enables for Phase 2

Phase 1 builds:
- **Surface Protocol** → Phase 2 plugs in voice + bridges.
- **Humarr Gateway** → daemon mode for Phase 2.
- **Sessions** → per-session settings for Phase 2 sandbox.
- **Workspace files** → bridges per-channel sandbox config.
- **Shed Protocol** → Phase 2 changes have migration paths.

Phase 1 is *load-bearing infrastructure* for everything that
follows.

---

## Phase 1 success criteria

Operator-visible:
- Hjarta wizard feels polished + branching.
- Workspace files actually shape personality.
- Sessions feel coherent.
- Release channels predictable.

Operationally:
- CI multi-OS green.
- Documentation complete + up-to-date.
- CHANGELOG maintained.
- No regression in V0 behavior.

Quantitative:
- Test count grew (new features have tests).
- Lines-of-code modest increase (~2000-3000).

---

## Closing

Phase 1: Observe and Borrow is **Klóinn's first wave**.
Foundation: workspace files, sessions, release channels,
Humarr rename, onboarding, Shed bones.

Cheap. High-value. Sets up everything.

Ships in V1.0 (or V0.3-0.4 depending on Yggdrasil timing).
Operators barely notice the refactor; deeply notice the
improvements.

This is **how Ember matures into a real engineering
project**. Each item ships value; together they
*professionalize* the system without bloating it.
