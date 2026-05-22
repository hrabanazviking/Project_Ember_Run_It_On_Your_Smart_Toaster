# 55 — Bug-Resistance Invariants

The structural invariants that make whole classes of bugs
*impossible* (or trivially caught). Not "no bugs" — "the
bugs that get through are surfaced fast."

---

## The principle

Most bug-prevention strategies are *defensive coding* —
careful programmers writing careful code. That works
locally but doesn't scale.

**Bug-resistance through invariants** flips it: build the
system so that *the type system / framework / structural
contract* makes certain bugs impossible to write.

When the compiler / linter / runtime *rejects* a buggy
pattern, the bug never ships.

---

## Yggdrasil's invariants

### Invariant 1: Typed-value-over-exception

Per ADR-0007 §2.2 (existing Ember invariant). Realms
return typed values (`Disconnected`, `Unavailable`,
`RealmError`) instead of raising across boundaries.

**Bug class prevented:** unhandled exceptions crashing
adjacent components.

**Enforcement:** code review + integration tests that
deliberately fail realms and verify chat continues.

### Invariant 2: Every cross-realm operation produces a Receipt

Per [`../architecture/39_THE_RECONCILIATION_LAYER.md`](../architecture/39_THE_RECONCILIATION_LAYER.md).

**Bug class prevented:** silent partial failures (one
backend wrote, another didn't, nobody noticed).

**Enforcement:** the Bifrǫst adapter wraps every fan-out;
no path bypasses receipt generation.

### Invariant 3: Every event has a typed schema

Per [`../architecture/38_THE_CROSSCUTTING_OBSERVABILITY.md`](../architecture/38_THE_CROSSCUTTING_OBSERVABILITY.md).

**Bug class prevented:** event payloads with wrong shape
(missing fields, wrong types) breaking subscribers
silently.

**Enforcement:** event schemas in `schemas/yggdrasil_protocols.py`;
publish helpers validate before sending.

### Invariant 4: All secrets flow through SecretResolver

Per [`../architecture/33_THE_KISTA_SECRET_PLANE.md`](../architecture/33_THE_KISTA_SECRET_PLANE.md).

**Bug class prevented:** plaintext secrets accidentally
landing in `ember.yaml`, logs, or process snapshots.

**Enforcement:** code reviewers reject any code that
reads `os.environ.get("...")` or inline credentials.
Linter rule flagged for `password=` literals.

### Invariant 5: Every operator-touchable config field has a test

Per Batch K's lesson (orphan fields are real risk).

**Bug class prevented:** schema fields declared but never
read (operator-misleading).

**Enforcement:** `tests/unit/test_yggdrasil_no_orphan_fields.py`
scans `schemas/config.py` and verifies each field has at
least one non-test reader. Fails CI otherwise.

### Invariant 6: Every realm's open() returns typed disconnect on missing dep

Per the pattern established with sqlite_vec / pgvector /
mcp.

**Bug class prevented:** ImportError tracebacks at chat
launch when operator hasn't installed the pip extra.

**Enforcement:** integration test that runs Stofa without
each pip extra and verifies the friendly message appears.

### Invariant 7: Every long-running task is wrapped for safety

Per [`53_CRASH_BOUNDED_DESIGN.md`](53_CRASH_BOUNDED_DESIGN.md).

**Bug class prevented:** silent async-task crashes
leaving the system in a degraded state nobody notices.

**Enforcement:** `safe_task()` helper; code review flags
direct `asyncio.create_task` without it.

### Invariant 8: Stofa widgets render-safely

Per `../tui/operations/93_ERROR_BOUNDARIES.md`.

**Bug class prevented:** one widget's render bug killing
the whole TUI.

**Enforcement:** `SafePanel` base class wraps every
render. Lint rule for direct Widget subclasses without
inheriting safe-render mixin.

### Invariant 9: Every external file write is atomic

Per the journal + writer + identity patterns (`os.replace`
+ NamedTemporaryFile).

**Bug class prevented:** torn-write corruption during
power loss.

**Enforcement:** code reviewers reject any non-atomic
write of operator-critical files. Linter pattern check.

### Invariant 10: Cross-platform paths are pathlib

Per `docs/CROSS_PLATFORM_PLAN.md`.

**Bug class prevented:** Windows-incompatible string-
based path handling.

**Enforcement:** ruff rules; CI runs on Linux + macOS +
Windows.

### Invariant 11: Every reactive value is owned by exactly one component

State that multiple components mutate creates
inconsistency. Yggdrasil designates one owner per piece of
state; others subscribe.

**Bug class prevented:** read-modify-write races between
components.

**Enforcement:** code reviewers verify reactive ownership
in PRs.

### Invariant 12: Every operator-facing error includes a recovery hint

Per the Vow of Public-Friendliness.

**Bug class prevented:** "An error occurred" with no
actionable next step.

**Enforcement:** code review pattern: every `Disconnected`
/ `Unavailable` / error message string ends with a "Try:
…" suggestion.

---

## The CI checks

Each invariant has a corresponding CI test:

```
tests/unit/test_invariant_01_typed_values.py
tests/unit/test_invariant_02_receipts.py
tests/unit/test_invariant_03_event_schemas.py
tests/unit/test_invariant_04_no_plaintext_secrets.py
tests/unit/test_invariant_05_no_orphan_fields.py
tests/unit/test_invariant_06_friendly_import_errors.py
tests/unit/test_invariant_07_safe_tasks.py
tests/unit/test_invariant_08_safe_widgets.py
tests/unit/test_invariant_09_atomic_writes.py
tests/unit/test_invariant_10_pathlib.py
tests/unit/test_invariant_11_reactive_ownership.py
tests/unit/test_invariant_12_recovery_hints.py
```

CI fails any invariant violation. The bug doesn't ship.

---

## What invariants don't catch

Invariants catch *structural* bugs:
- Patterns the system architecture should prevent.
- Conventions that, if violated, break adjacent systems.

They don't catch:
- *Semantic* bugs (the function returns the wrong answer).
- *Logic* bugs in algorithms.
- *Specification* bugs (the feature was designed wrong).

For those: standard testing, code review, operator
feedback.

The point of invariants is to **make the *types of bugs*
that violate Yggdrasil's *contract* impossible to ship**.
Other bugs are still possible — but the architecture is
sound.

---

## Why invariants beat conventions

A *convention* is "we agreed to do it this way." Survives
until someone forgets.

An *invariant* is "the system enforces it." Survives
indefinitely.

When CI is the enforcement mechanism, the invariant
*can't* be forgotten — every PR runs the check.

---

## Adding new invariants

When a bug type recurs, we promote it to an invariant:

1. Document the bug class (in this file).
2. Write a CI test that catches it.
3. Fix all current instances.
4. Going forward, the invariant prevents recurrence.

The invariant catalog grows organically over time. Each
addition makes a class of bugs *impossible* to ship.

---

## How invariants interact with the Vows

The Vows are *philosophical commitments*. Invariants are
*structural enforcements* of those commitments:

| Vow | Invariant that enforces |
|---|---|
| Smallness | Pip extras gate every realm |
| Sovereignty | Invariant 4 (Kista mediation) |
| Graceful Offline | Invariant 1 (typed values), Invariant 6 (friendly imports) |
| Tethered Grounding | (existing tests of retrieval-grounded replies) |
| Public-Friendliness | Invariant 12 (recovery hints) |
| Honest Memory | (existing tests of prompt assembly) |
| Modular Authorship | Invariant 6 (per-realm pip extras) |
| Open Knowledge | (this design tree) |
| Pluggable Storage | Invariant 1 + Bifrǫst architecture |
| The Unbroken Whole | Invariants 1, 7, 8 (isolation) |
| Flexible Roots | Invariant 10 (pathlib) |

Vows → Invariants → CI → Shipped Code. The chain that
keeps philosophy actionable.

---

## Closing

Bug-Resistance Invariants are **the structural
guarantees**. Not "good developers writing good code" —
*the system enforces the right shape*. Vows become CI
rules; CI rules catch violations; violations don't ship.

Yggdrasil is *resistant* to whole classes of bugs by
construction. The bugs that *do* slip through are easier
to fix because the surrounding architecture is sound.
