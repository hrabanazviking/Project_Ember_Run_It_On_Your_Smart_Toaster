# INTERFACE — `runa.skills`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §10.

## Purpose

First-party agent-facing capabilities. Things Runa can do that are too small to be subsystems in `core/` and too internal to be adapters.

## Public surface

| Symbol | Purpose |
|---|---|
| `runa.skills.contract.SkillContract` | Base class for first-party skills. |
| `runa.skills.registry.SkillRegistry` | The registry the kernel addresses skills through. |
| `runa.skills.registry.SkillRegistry.register(skill)` | Used at start by the loader; tests may register directly. |
| `runa.skills.registry.SkillRegistry.invoke(name, context, args) -> SkillResult` | The kernel-facing call shape. |
| Individual skill modules: `runa.skills.<name>` | Each implements `SkillContract`. |

## Invariants

- **A skill never raises an unhandled exception across its boundary.** Errors come back as `SkillResult.failed(reason, …)` types.
- **A skill's `invoke` is idempotent where possible** — re-invoking a skill with the same args yields the same effect, except for explicitly stateful skills which document the deviation.
- **A skill has a single declared purpose.** Multi-purpose skills are split.
- **A skill declares its capability requirements** (filesystem, shell, network, model-call, memory-read, memory-write). The policy engine enforces them.
- **A skill never imports from `runa.services`, `runa.apps`, `runa.adapters`, or `runa.plugins`.**

## Allowed callers

`runa.core.kernel` (via the registry).

## Allowed callees

`runa.schemas`, `runa.core` (declared narrow interfaces — tool forge, memory readers, model router).

## Failure semantics

A skill failure surfaces as a typed `SkillResult.failed`. The kernel decides whether to retry, route to a different skill, or degrade. Unhandled exceptions are caught at the registry boundary and converted to typed errors; an unhandled exception leaking out of a skill is a bug to fix in that skill.
