# 04 — Preconditions, Postconditions, Invariants

**Category:** Robustness Fundamentals
**Runa relevance:** `runa.core` invariants, Muninn/Skuld store contracts, Eir health checks
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A **precondition** is what must be true *before* a function runs. A **postcondition** is what must be true *after*. An **invariant** is what is true *always* — across the lifetime of an object, or across the lifetime of a system. Together, these three concepts are the formal language of correctness: a function with documented and checked pre/post conditions is *self-describing*; an object with documented and checked invariants is *self-maintaining*.

Most Python codebases use these informally — a docstring sentence here, an assert there. Used systematically — declared explicitly, tested with property-based testing ([[31-hypothesis-property-based-testing]]), checked at runtime where the cost is worth it — they turn vague "should be" intuitions into machine-readable, evolvable specifications.

## 2. Technique / mechanism

**Preconditions — what callers must guarantee:**

```python
def withdraw(account: Account, amount: Decimal) -> None:
    """Withdraw `amount` from `account`.
    
    Preconditions:
        - amount > 0
        - account.balance >= amount
        - account is not locked
    """
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if account.balance < amount:
        raise InsufficientFundsError(account.id, requested=amount, available=account.balance)
    if account.locked:
        raise AccountLockedError(account.id)
    account.balance -= amount
```

Preconditions are *the caller's responsibility*. Violation is an *API misuse*, typically raised as `ValueError` or a domain-specific error. The function should refuse before doing anything destructive.

**Postconditions — what callers can rely on:**

```python
def withdraw(account: Account, amount: Decimal) -> None:
    """...
    
    Postconditions:
        - account.balance is reduced by exactly `amount`
        - a transaction record is written to account.history
        - balance >= 0 (preserved invariant)
    """
    initial_balance = account.balance  # for postcondition check
    ...
    assert account.balance == initial_balance - amount, "balance not decreased correctly"
    assert account.balance >= 0, "withdrew more than balance"
    assert account.history[-1].amount == amount, "transaction not recorded"
```

Postconditions are the *function's responsibility*. Violation is an *implementation bug*. Asserts here catch the bug close to where it happened.

**Invariants — what holds always:**

For an object:
```python
class Account:
    """Invariants:
        - balance >= 0
        - len(history) == sum of all completed transactions
        - locked implies (balance >= 0 still, but no mutations allowed)
    """
    balance: Decimal
    history: list[Transaction]
    locked: bool
    
    def _check_invariants(self) -> None:
        assert self.balance >= 0, f"invariant violated: balance={self.balance}"
        assert sum(t.amount for t in self.history) == self.balance, \
            "history sum doesn't match balance"
```

For a system:
- "Every Muninn episode has an embedding."
- "Skuld task ledger is monotonically advancing in event order."
- "The audit-log hash chain is unbroken."

System invariants are typically checked by a periodic auditor (Eir).

**The `icontract` formalisation:**

```python
from icontract import require, ensure, invariant

@invariant(lambda self: self.balance >= 0)
@invariant(lambda self: sum(t.amount for t in self.completed_history) == self.balance)
class Account:
    @require(lambda amount: amount > 0, "amount positive")
    @require(lambda self, amount: self.balance >= amount, "sufficient funds")
    @require(lambda self: not self.locked, "account unlocked")
    @ensure(lambda self, amount, OLD: self.balance == OLD.self.balance - amount)
    def withdraw(self, amount: Decimal) -> None:
        self.balance -= amount
        self.history.append(Transaction(amount=amount, kind="withdraw"))
```

`OLD` references pre-execution state for postcondition comparison. The decorators check at runtime.

**The strength of the invariant approach:**

- **Local reasoning.** When reading `withdraw`, you don't need to know about the rest of the system — the invariants tell you what's true.
- **Defensive recovery.** Eir-style auditors can periodically check invariants on running state; a violation is recoverable evidence.
- **Bug isolation.** When an invariant fails, the bug is in code that *just modified* the relevant state, not in code that read it later.
- **Refactoring safety.** Changing implementation while preserving invariants is the contract.

**Property-based testing as invariant verification** ([[31-hypothesis-property-based-testing]]):

```python
from hypothesis import given, strategies as st

@given(
    initial_balance=st.decimals(min_value=0, max_value=1_000_000),
    amount=st.decimals(min_value=Decimal("0.01"), max_value=1_000_000),
)
def test_withdraw_preserves_invariants(initial_balance, amount):
    account = Account(balance=initial_balance)
    if amount <= initial_balance:
        account.withdraw(amount)
        assert account.balance == initial_balance - amount
        assert account.balance >= 0
    else:
        with pytest.raises(InsufficientFundsError):
            account.withdraw(amount)
```

Hypothesis generates many inputs to probe the contract.

## 3. Key works / libraries

- **Hoare, C.A.R.** "An Axiomatic Basis for Computer Programming." *CACM*, 1969. Hoare logic — the precondition/postcondition formalism.
- **Meyer, B.** *Object-Oriented Software Construction*. The DbC textbook ([[03-defensive-programming-design-by-contract]]).
- **Hoare's "Communicating Sequential Processes"** also relevant.
- **icontract** — github.com/Parquery/icontract.
- **deal** — github.com/life4/deal. Includes formal-style proof modes.
- **Hypothesis** — github.com/HypothesisWorks/hypothesis. Property-based testing.
- **Crystal** language for formal Python verification (academic-level).
- **Pyright's strict mode** — catches some precondition violations statically.

## 4. Pitfalls and gotchas

- **Over-specified contracts** become brittle. "x must be 42 or 17 or 23" is rarely a real invariant; usually a misunderstood requirement.
- **Mutable arguments and postconditions.** If the caller mutates the input dict during the call, postconditions on it are ambiguous. Document and prefer immutable inputs.
- **Postcondition checks that themselves can fail.** A postcondition check that depends on the same buggy code it's checking is useless. Independent checks where possible.
- **Performance.** `@invariant` runs after every method call. For hot objects, this dominates. Use sparingly or in dev-only mode.
- **Invariants spanning multiple objects** are hard. "Across all accounts, total balance is preserved" can't live on `Account`; lives at the system level, checked by an auditor.
- **`assert` removal in `-O`.** Defensive use of `assert` for preconditions is wrong; use raised exceptions. Use `assert` only for "should-never-happen" internal sanity.

## 5. Applicability to Runa

For **`runa.schemas`**:

- Field constraints (`Field(ge=0)`, `min_length=1`) are preconditions enforced at construction.
- Custom validators capture richer preconditions.

For **`runa.core.memory` (Muninn)**:

- **System invariant:** every persisted episode has an embedding whose dimension matches the configured embedding model.
- **System invariant:** the audit-log hash chain is unbroken.
- **System invariant:** Muninn's SQLite database integrity (PRAGMA integrity_check returns "ok").
- Eir's nightly maintenance pass *checks* these invariants and flags violations via `Notified`.

For **`runa.core.tasks` (Skuld)**:

- **Object invariant on Task:** state ∈ {queued, in_progress, completed, failed, abandoned}; status transitions follow a state machine ([[16-state-machines-reliability]]).
- **Object invariant on Task:** `completed_at` is set iff `state ∈ {completed, failed, abandoned}`.

For **`runa.core.policy`**:

- The policy engine is *all* preconditions: "this action is allowed iff [conditions]."

For **kernel turns**:

- **Postcondition** of every turn: an audit-log entry was written.
- **Postcondition:** Muninn was written if the turn produced an episode.
- **Postcondition:** the response timestamp is later than the request timestamp.

What to avoid:

- Don't add contracts where type hints suffice.
- Don't write contracts that are wishful thinking. If a contract claims `x is sorted` but production data sometimes isn't, fix the contract or the data.
- Don't make contracts a debug-only feature unless that's explicit. Inconsistent contract behaviour between dev and prod is confusing.
- Don't put cross-object invariants on individual objects.

## 6. Open questions

- **The right enforcement strength.** Always check? Dev-only? Sample-only in production? Per-team / per-project decision.
- **Contracts in async code.** `@require` decorators work but postcondition timing across async boundaries is subtle. Active practice.
- **Property-based-testing as contract specification** vs separate contract decorators. Some teams use only Hypothesis; others both. Trade-offs.

## 7. References (curated)

- Hoare (1969) — "An Axiomatic Basis for Computer Programming."
- Meyer's *OOSC* — DbC chapter.
- github.com/Parquery/icontract.
- github.com/life4/deal.
- hypothesis.readthedocs.io.
- hillelwayne.com — formal methods writing.
- Companion docs: [[03-defensive-programming-design-by-contract]], [[16-state-machines-reliability]], [[31-hypothesis-property-based-testing]].
