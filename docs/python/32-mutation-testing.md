# 32 — Mutation Testing

**Category:** Testing
**Runa relevance:** test-quality evaluation, pre-release confidence
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Code coverage tells you which *lines* tests touch. It does *not* tell you whether the tests would *catch a bug* in those lines. A test that exercises a function but never asserts on its behaviour has 100% coverage and zero value. **Mutation testing** is the technique that asks: "if I mutate this code (change `<` to `<=`, flip a condition, return a constant instead), do the tests still pass?" If tests still pass on a mutated version, those tests didn't actually test the mutated logic — the mutation *survived*, indicating weak tests.

For Runa, mutation testing is the deepest test-quality check available. Run periodically (not on every commit — it's slow) against critical modules to find tests that *look* thorough but aren't.

## 2. Technique / mechanism

**Tools:**

- **`mutmut`** — github.com/boxed/mutmut. Most-used.
- **`cosmic-ray`** — github.com/sixty-north/cosmic-ray. More configurable.
- **`mutpy`** — github.com/mutpy/mutpy. Older.

**`mutmut` workflow:**

```bash
# Configure
[tool.mutmut]
paths_to_mutate = "src/runa/"
tests_dir = "tests/"

# Run
mutmut run

# Inspect
mutmut results
mutmut show <mutant-id>
```

`mutmut` modifies the code (mutations include changing operators, return values, boundaries), runs the test suite, records which mutations were *killed* (caught by tests failing) vs *survived* (tests passed despite mutation).

**Output interpretation:**

```
1234 mutants killed
   12 survived
    3 timeout
    0 suspicious
```

Survived mutants are the interesting cases. Look at each:

```bash
mutmut show 17
```

Shows the diff between original and mutated code. If the mutation is *semantically equivalent* (a tautological change), it's a false positive. If the mutation *changes behaviour* but tests pass, you've found a weak test.

**Common mutation types:**

- Replace `a < b` with `a <= b`.
- Replace `+` with `-`.
- Replace `return x` with `return None`.
- Negate boolean expressions.
- Replace constants with neighbouring values (0 → 1, "x" → "").
- Remove method calls.

**Common false positives:**

- Logging statements (different log doesn't change correctness).
- Performance-only changes (caching).
- Defensive code (raising an error in unreachable code).
- Comments.

Use `# pragma: no mutate` to exclude.

**Slow execution:**

Each mutant requires re-running tests. For a 1000-test suite that takes 30s, a 100-mutation project takes ~50 minutes. Parallelise with `mutmut run --use-coverage` (only runs tests that exercise the mutated line — much faster).

## 3. Key works / libraries

- **DeMillo, R., Lipton, R., Sayward, F.** "Hints on Test Data Selection: Help for the Practicing Programmer." *IEEE Computer*, 1978. Original mutation-testing paper.
- **`mutmut`** — github.com/boxed/mutmut.
- **`cosmic-ray`** — github.com/sixty-north/cosmic-ray.
- **Mutation Testing book** — Jia and Harman, 2011.
- **PIT** (Java) — the most-mature mutation tool, instructive design.

## 4. Pitfalls and gotchas

- **Slow.** Run on critical modules only, not the whole codebase.
- **Equivalent mutants.** Some mutations produce semantically-identical code (e.g., `x + 0` → `x - 0`). Both work; tests can't distinguish. Mark.
- **False sense of perfection.** 100% killed mutants doesn't mean tests are complete — only that *these* mutations are caught.
- **Test brittleness.** Mutation testing rewards tests that assert *every detail*. Can over-couple tests to implementation.
- **Async / concurrent code.** Mutations can introduce non-determinism; results harder to interpret.
- **Coverage integration finicky.** `--use-coverage` saves time but breaks if coverage isn't accurate.

## 5. Applicability to Runa

For **critical modules**:

- Run mutmut on `runa.core.kernel`, `runa.core.memory`, `runa.core.policy`, `runa.schemas.errors`. These are the highest-stakes modules.
- Skip mutation testing on adapter code (more I/O, less logic).

For **release gating**:

- Pre-release: mutation testing run on critical modules. Surviving mutants reviewed.
- Don't gate every commit (too slow).

For **ongoing test-quality improvement**:

- Periodically (monthly?) run mutation testing on a rotating subset of modules.
- Use surviving mutants to inform new tests.

What to avoid:

- Don't run mutation testing in every PR. Too slow.
- Don't chase 100% mutation score. Diminishing returns.
- Don't write tests that pass mutation testing but lose readability.
- Don't ignore equivalent mutants — review and document.

## 6. Open questions

- **Mutation testing for Pydantic / type-annotated code.** Some mutations to type hints don't change runtime; mutation tools may or may not handle.
- **Async-aware mutation testing.** Most tools sync-focused; results on async code are best-effort.
- **Mutation testing of stub-heavy code.** Stubs don't get mutated meaningfully.

## 7. References (curated)

- github.com/boxed/mutmut.
- mutmut.readthedocs.io.
- pitest.org — PIT (Java but well-documented).
- DeMillo et al. (1978).
- Companion docs: [[30-pytest-mastery]], [[31-hypothesis-property-based-testing]], [[34-integration-e2e-testing]].
