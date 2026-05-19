# INTERFACE — `runa.schemas`

**Status:** Stub — no code yet. Surface will be filled in as first slice lands.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §1.

## Purpose

Pydantic models, dataclasses, and shared type definitions used in two or more other subpackages.

## Public surface (declared at slice-time)

When code lands, this section will list every type that another subpackage may import. Until then, the floor rule applies: anything not declared here is private to `runa.schemas`.

Planned top-level modules:

| Module | Holds |
|---|---|
| `runa.schemas.events` | Event types on **VERÐANDI** — `Heard`, `Replied`, `SkillInvoke`, …  |
| `runa.schemas.config` | Config root model + per-subpackage config slices. |
| `runa.schemas.errors` | Exception classes raised across subpackage boundaries. |
| `runa.schemas.memory` | Episode, semantic record, retrieval-result types. |
| `runa.schemas.tasks` | Task, task-state, transition types. |
| `runa.schemas.identity` | Identity record + persona snapshot types. |
| `runa.schemas.world` | WYRD-bridge slice types. |

## Invariants

- **No behaviour.** A schema may define a type and validation; it must not define a method that does work.
- **No `runa.*` imports.** Only standard library + `pydantic` / `typing_extensions` / `enum`.
- **Forward-compatible.** New fields are added with sensible defaults; removed fields go through deprecation, then a migration in `runa.migrations`.

## Allowed callers

Everything under `runa.*`.

## Allowed callees

Standard library, `pydantic`, `typing_extensions`. Nothing in `runa.*`.

## Failure semantics

A failure in `runa.schemas` means the package fails to import. There is no graceful degradation. CI guarantees the import is clean.
