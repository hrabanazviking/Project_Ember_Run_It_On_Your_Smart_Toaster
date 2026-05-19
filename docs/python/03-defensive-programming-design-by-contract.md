# 03 — Defensive Programming and Design by Contract

**Category:** Robustness Fundamentals
**Runa relevance:** every subpackage boundary, every public function, the policy engine
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Defensive programming** is the discipline of writing code that protects itself from incorrect input, unexpected state, and the world being weirder than you imagined. **Design by Contract (DbC)** — Bertrand Meyer's framework from Eiffel in 1986 — formalises this into three pillars: *preconditions* (what must be true before a function runs), *postconditions* (what must be true after), and *invariants* (what is always true about an object's state). The combination is the engineering practice that distinguishes "this code works on the happy path" from "this code remains correct as it's used in ways the author didn't anticipate."

For Runa, defensive programming and contracts are how subpackage boundaries stay honest. A function that promises certain inputs and certain outputs has a *clear contract*; violations are detected at the boundary, not buried deep in stack traces. Standing-trust doctrine (the agent acts without per-action approval) makes contract-checking even more important — there's no human catching obvious bugs at action time.

## 2. Technique / mechanism

**The four levels of defense, from cheap to thorough:**

**Level 1 — Type hints + static checking (cheapest):**

```python
def get_episode(episode_id: UUID) -> Episode | None:
    """Returns the episode if found, None if not."""
    ...
```

The contract is in the signature. mypy or pyright catches callers passing wrong types. Zero runtime cost.

**Level 2 — Runtime validation at boundaries (Pydantic / assertions):**

```python
from pydantic import BaseModel, Field, field_validator

class EpisodeWrite(BaseModel):
    episode_id: UUID
    text: str = Field(min_length=1, max_length=100_000)
    timestamp: datetime
    speaker: str
    
    @field_validator("speaker")
    def speaker_is_known(cls, v: str) -> str:
        if v not in {"user", "runa", "tool"} and not v.startswith("agent:"):
            raise ValueError(f"unknown speaker: {v!r}")
        return v
```

Catches malformed inputs at the *boundary* (typically the kernel <-> service interface). Pydantic does this fluently.

**Level 3 — Explicit assertions inside functions:**

```python
def consolidate_episodes(episodes: list[Episode]) -> Summary:
    assert episodes, "consolidate called with empty list"
    assert all(e.conversation_id == episodes[0].conversation_id 
               for e in episodes), "mixed conversations"
    ...
    summary = ...
    assert len(summary.text) > 0, "consolidation produced empty summary"
    return summary
```

Assertions inside functions catch invariant violations *near* the bug, before they propagate. **Warning:** `assert` is removed under `python -O`. Use only for "this should never happen if the code is correct" — internal sanity, not validation of external input.

**Level 4 — Contracts via decorators or libraries:**

```python
from icontract import require, ensure, invariant

@require(lambda episodes: len(episodes) > 0, "must have episodes")
@require(lambda episodes: all(e.conversation_id == episodes[0].conversation_id 
                              for e in episodes), "same conversation")
@ensure(lambda result: len(result.text) > 0, "non-empty summary")
def consolidate_episodes(episodes: list[Episode]) -> Summary:
    ...
```

Library `icontract` brings Meyer-style DbC to Python with decorators. Pre and post conditions run automatically. Failures raise `ViolationError`.

Class invariants:

```python
@invariant(lambda self: self.balance >= 0, "balance never negative")
class Account:
    def deposit(self, amount: Decimal) -> None: ...
    def withdraw(self, amount: Decimal) -> None: ...
```

Invariants checked after every method call.

**Defensive programming idioms in Python:**

- **Validate at the boundary, trust within.** External input (config, API request, file read) validates once; internal callers can trust.
- **Use immutable types for shared state** (`frozen=True` dataclasses, `tuple` over `list` where appropriate, `NamedTuple`).
- **Prefer explicit failure over silent success.** Raise / return-error rather than mask.
- **No magic defaults.** A function that silently substitutes `0` or `""` for missing args hides bugs.
- **Avoid mutable default arguments** — the perennial Python gotcha:

```python
# Wrong:
def add_item(item, items=[]):  # default list shared across all calls!
    items.append(item)
    return items

# Right:
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

- **Fail-fast on invariant violation.** Don't try to "limp on" with corrupted state — restart cleanly ([[11-crash-only-software]]).

**The defensive-vs-trust trade-off:**

Too little defense → bugs propagate, debugging is hard. Too much defense → code becomes a checklist of assertions, performance suffers, readability collapses. The right balance:

- **High defense** at trust boundaries (external input, subpackage interfaces, IPC).
- **Low defense** inside well-tested internal code where callers are trusted.
- **Type hints everywhere** (zero runtime cost).

## 3. Key works / libraries

- **Meyer, B. *Object-Oriented Software Construction*, 2nd ed.** Prentice Hall, 1997. The Design by Contract foundation.
- **Eiffel programming language.** Where DbC originated.
- **icontract** — github.com/Parquery/icontract. Decorator-based DbC for Python.
- **deal** — github.com/life4/deal. Alternative DbC library with broader feature set.
- **Pydantic** — pydantic.dev. Runtime validation; the go-to for boundary validation.
- **`assert` in PEP 8 / PEP 20** — Python's built-in.
- **Bertrand Meyer's papers and talks.** Still the clearest articulation.
- **Hillel Wayne's "Beyond Smart Contracts: Design by Contract."** Hillel's writing on the formal-methods spectrum.

## 4. Pitfalls and gotchas

- **`assert` removed in `-O` mode.** Production deployments sometimes run with `-O` for speed; `assert` disappears. Don't validate external input with assert. Use `if not condition: raise ValueError(...)`.
- **Side effects in assertions** are deleted in `-O`. `assert log.write("..."), "log failed"` loses the log line in optimised mode.
- **Over-validation in hot paths** slows everything. Profile; pull validation to colder layers.
- **Validating after construction** rather than during. Pydantic validates on `__init__`, which is the right time. Validating later misses inputs that were already used.
- **Catching `AssertionError`** is almost always wrong — it means "the code's invariants are violated." Crash; don't recover.
- **Contract decorators run in production.** If you have `@require` with expensive checks, that cost compounds. Either keep contracts cheap or use icontract's modes (check-only-in-dev).
- **Pydantic v1 vs v2 differences** are large. Use v2 (pydantic 2.x) for new code; the migration is non-trivial.

## 5. Applicability to Runa

For **subpackage boundaries**:

- Every public function that crosses a subpackage boundary has type hints. mypy strict mode enforced ([[26-mypy-strict-mode]]).
- Inputs from outside Runa (config files, adapter payloads, plugin calls) validate via Pydantic. Inside Runa, trust the types.

For **`runa.schemas`**:

- All boundary types are Pydantic `BaseModel`s with `field_validator`s where invariants apply.
- Frozen dataclasses for value objects that don't need full validation.
- Use `Annotated[int, Field(ge=0)]` for "non-negative int" rather than runtime checks downstream.

For **`runa.core.policy`**:

- The policy engine is *all* about contracts: "can this action proceed given this state?" Express as predicates on `(action, state)`. Make the policy declarative.

For **`runa.core.memory` (Muninn)**:

- `MuninnWriter.write_episode(episode)` requires `episode` to satisfy the `Episode` Pydantic schema. Pydantic raises clear errors on shape violations.
- Internal Muninn invariants (the embedding column is always populated; the index is consistent) checked by Eir's periodic health check rather than per-write assertions.

For **plugins (loaded code)**:

- Plugin calls into the host API are validated. Plugin internal logic is the plugin's concern.

What to avoid:

- Don't validate the same thing at every layer. Validate once at the boundary; trust below.
- Don't make contracts so heavy they become the bug. A failing contract test is informative; a failing contract that masks a real bug is noise.
- Don't conflate "user-facing validation" (Pydantic) with "internal sanity assertions" (`assert`). Different tools for different jobs.
- Don't use docstrings as the only contract documentation. Type hints + Pydantic field constraints are machine-checkable; docstrings rot.

## 6. Open questions

- **Formal contracts at Python scale.** Tools like Hypothesis ([[31-hypothesis-property-based-testing]]) test properties; full formal verification (Crystal, deal's checking modes) is rare in Python.
- **Performance impact of `@require` chains.** For low-throughput code, negligible. For tight loops, measure.
- **Combining DbC with effect systems.** Effects (IO, state mutation) are tracked in some languages; Python has none. Open territory.

## 7. References (curated)

- Meyer (1997) — *Object-Oriented Software Construction*, 2nd ed.
- github.com/Parquery/icontract — icontract library.
- pydantic.dev — Pydantic v2.
- hillelwayne.com — Hillel Wayne's writing on formal methods, contracts.
- realpython.com/python-assert-statement/ — pragmatic intro to asserts.
- PEP 484 onward — Python typing.
- Companion docs: [[01-exception-design]], [[04-preconditions-postconditions-invariants]], [[26-mypy-strict-mode]], [[27-pydantic-runtime-validation]].
