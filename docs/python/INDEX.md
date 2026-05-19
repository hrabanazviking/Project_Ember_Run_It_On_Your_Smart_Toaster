# Python Craft Corpus — INDEX

**50 technical documents** on building the most robust, error-correcting, self-healing, crash-proof, efficient, and stable Python software possible.

**Status:** **COMPLETE 2026-05-17** — all 50 docs landed across 10 batches. Closing ADR: `docs/decisions/0004-python-craft-corpus-2026-05-17.md`.

**Read with:** `README.md` (template + reading guide), `docs/research/` (conceptual companion corpus), `docs/architecture/{ARCHITECTURE,DOMAIN_MAP}.md`.

---

## Robustness Fundamentals

| # | Title | Commit |
|---|---|---|
| 01 | Exception design and error hierarchies in Python | f5015e9 |
| 02 | Result types vs exceptions: when to use which | f5015e9 |
| 03 | Defensive programming and Design by Contract | f5015e9 |
| 04 | Preconditions, postconditions, invariants | f5015e9 |
| 05 | Idempotency design and safe retries | f5015e9 |
| 06 | Retry strategies, exponential backoff, jitter | e2ad30b |
| 07 | Circuit breaker pattern in Python | e2ad30b |
| 08 | Bulkhead pattern and failure isolation | e2ad30b |
| 09 | Timeout patterns and deadline propagation | e2ad30b |
| 10 | Graceful degradation strategies | e2ad30b |

## Self-Healing & Supervision

| # | Title | Commit |
|---|---|---|
| 11 | Crash-only software design | db4e2dd |
| 12 | Supervisor trees in Python | db4e2dd |
| 13 | Watchdog timers and liveness detection | db4e2dd |
| 14 | Health checks: liveness, readiness, startup | db4e2dd |
| 15 | Self-repair systems and reconciliation loops | db4e2dd |
| 16 | State machines for reliability | 79669a5 |
| 17 | Saga pattern and compensating transactions | 79669a5 |
| 18 | Chaos engineering and fault injection | 79669a5 |

## Concurrency Mastery

| # | Title | Commit |
|---|---|---|
| 19 | asyncio advanced patterns: TaskGroup, timeout, cancellation | 79669a5 |
| 20 | Thread safety in Python: GIL, locks, atomics | 79669a5 |
| 21 | multiprocessing deep-dive: spawn vs fork, IPC | a258fc6 |
| 22 | concurrent.futures patterns: pools, futures, executors | a258fc6 |
| 23 | Async cancellation and shielded operations | a258fc6 |
| 24 | Queue and channel patterns | a258fc6 |

## Type Safety & Validation

| # | Title | Commit |
|---|---|---|
| 25 | Type hints mastery: PEPs and idioms | a258fc6 |
| 26 | mypy strict mode and gradual typing | 9e6440e |
| 27 | Pydantic for runtime validation | 9e6440e |
| 28 | Protocol classes and structural typing | 9e6440e |
| 29 | Dataclasses, NamedTuple, attrs — when to use which | 9e6440e |

## Testing

| # | Title | Commit |
|---|---|---|
| 30 | pytest mastery: fixtures, parameterization, marks, conftest | 9e6440e |
| 31 | Property-based testing with Hypothesis | 6a58aaa |
| 32 | Mutation testing | 6a58aaa |
| 33 | Snapshot and golden-file testing | 6a58aaa |
| 34 | Integration and e2e testing patterns | 6a58aaa |
| 35 | Test doubles: mocks, stubs, fakes, spies | 6a58aaa |

## Performance

| # | Title | Commit |
|---|---|---|
| 36 | Profiling Python: cProfile, py-spy, scalene, austin | 7f5c9ad |
| 37 | Memory profiling: tracemalloc, memray, objgraph | 7f5c9ad |
| 38 | Caching strategies and memoization | 7f5c9ad |
| 39 | Lazy evaluation patterns | 7f5c9ad |
| 40 | C extensions, Cython, Rust via PyO3 | 7f5c9ad |

## Architecture Patterns

| # | Title | Commit |
|---|---|---|
| 41 | Dependency injection without frameworks | 18b8000 |
| 42 | Hexagonal architecture (ports & adapters) | 18b8000 |
| 43 | Event sourcing in Python — implementation | 18b8000 |
| 44 | Plugin architecture patterns | 18b8000 |
| 45 | Configuration management: Pydantic Settings, dynaconf | 18b8000 |

## Observability & Operations

| # | Title | Commit |
|---|---|---|
| 46 | Structured logging in Python: structlog, loguru, stdlib | 0d9dad7 |
| 47 | Distributed tracing with OpenTelemetry (Python-side) | 0d9dad7 |
| 48 | Metrics: Prometheus exposition, OpenTelemetry metrics | 0d9dad7 |
| 49 | Graceful shutdown and signal handling | 0d9dad7 |
| 50 | Long-running process patterns: daemons, supervisors, restarts | 0d9dad7 |

---

## Batches

| Batch | Commit | Docs |
|---|---|---|
| P0 | e38e49d | TASK + INDEX + folder README |
| B1 | f5015e9 | 01–05 (Robustness Fundamentals part 1) |
| B2 | e2ad30b | 06–10 (Robustness Fundamentals part 2) |
| B3 | db4e2dd | 11–15 (Self-Healing part 1) |
| B4 | 79669a5 | 16–20 (Self-Healing part 2 + Concurrency part 1) |
| B5 | a258fc6 | 21–25 (Concurrency part 2 + Type Safety part 1) |
| B6 | 9e6440e | 26–30 (Type Safety part 2 + Testing part 1) |
| B7 | 6a58aaa | 31–35 (Testing part 2) |
| B8 | 7f5c9ad | 36–40 (Performance) |
| B9 | 18b8000 | 41–45 (Architecture Patterns) |
| B10 | 0d9dad7 | 46–50 (Observability & Operations) |
| Closing | 43dd9d5 | INDEX + ADR-0004 + REPO_MAP + DEVLOG |

Total: ~440 KB across 50 documents, ~8.8 KB average. Each doc structured per the seven-section template in `README.md`.

## Relationship to `docs/research/`

| `docs/research/` | `docs/python/` (this corpus) |
|---|---|
| Concepts from AI / CS / cognitive science | Python implementation craft |
| Why this is the right shape | How to build that shape well |
| Cites academic papers, frameworks | Cites PEPs, libraries, idioms |
| Architect's reading | Forge Worker's reading |

Some topics appear in both at different abstraction levels (asyncio, event sourcing, plugins, audit logging). Pairing intentional.
