# TASK — Runa Python Craft Corpus (50 robust-Python research documents)

**Task owner:** Runa Gridweaver Freyjasdottir (AI working under Volmarr)
**Branch:** development
**Started:** 2026-05-17 (same day as bootstrap + research corpus)
**Status:** P0 — TASK + folder + INDEX
**Mode:** Full autonomous run, batches of 5 docs with commit+push between

---

## 1. Task scope

Produce 50 lengthy, research-paper-length Markdown documents on how to build the most robust, well-designed, error-correcting, self-healing, crash-proof, efficient, fast, stable, and smart Python software possible. Each document is a *technique synthesis*: explains the idea, shows the reference Python implementation (code samples where useful), names the gotchas and failure modes, maps the connection back to Runa's code under `src/runa/` where applicable.

Companion to the 50-document research corpus under `docs/research/` (ADR-0003). That corpus is about *concepts in AI / CS / cognitive science*. This corpus is about *the Python craft to actually build them*. Some overlap (asyncio appears in both — once at the architectural level, once at the implementation level) is intentional.

## 2. Output target

- **Count:** 50 documents.
- **Length:** ~6–10 KB each (research-paper density without padding).
- **Location:** `docs/python/<NN>-<short-kebab-slug>.md` numbered 01–50.
- **Index:** `docs/python/INDEX.md`.
- **Folder README:** `docs/python/README.md` with template + reading guide.

## 3. Per-document template

Same seven-section template as `docs/research/`:

1. **Core idea** — 1–2 paragraphs.
2. **Technique / mechanism** — Python-specific implementation, code snippets where useful.
3. **Key works / libraries** — named papers, PEPs, libraries, authors.
4. **Pitfalls and gotchas** — failure modes, common mistakes.
5. **Applicability to Runa** — which `src/runa/*` subpackage uses this and how.
6. **Open questions** — design trade-offs, things to monitor.
7. **References (curated)** — pointers for further reading.

## 4. The 50 topics

### Robustness fundamentals (10)
01. Exception design and error hierarchies in Python
02. Result types vs exceptions: when to use which
03. Defensive programming and Design by Contract
04. Preconditions, postconditions, invariants (asserts and beyond)
05. Idempotency design and safe retries
06. Retry strategies, exponential backoff, jitter
07. Circuit breaker pattern in Python
08. Bulkhead pattern and failure isolation
09. Timeout patterns and deadline propagation
10. Graceful degradation strategies

### Self-healing & supervision (8)
11. Crash-only software design
12. Supervisor trees in Python (Erlang-inspired)
13. Watchdog timers and liveness detection
14. Health checks: liveness, readiness, startup
15. Self-repair systems and reconciliation loops
16. State machines for reliability
17. Saga pattern and compensating transactions
18. Chaos engineering and fault injection in Python

### Concurrency mastery (6)
19. asyncio advanced patterns: TaskGroup, timeout, cancellation
20. Thread safety in Python: GIL, locks, atomics
21. multiprocessing deep-dive: spawn vs fork, IPC
22. concurrent.futures patterns: pools, futures, executors
23. Async cancellation and shielded operations
24. Queue and channel patterns: asyncio.Queue, multiprocessing.Queue

### Type safety & validation (5)
25. Type hints mastery: PEP 484, 585, 604, 612, 695
26. mypy strict mode and gradual typing
27. Pydantic for runtime validation
28. Protocol classes and structural typing (PEP 544)
29. Dataclasses, NamedTuple, attrs — when to use which

### Testing (6)
30. pytest mastery: fixtures, parameterization, marks, conftest
31. Property-based testing with Hypothesis
32. Mutation testing with mutmut / cosmic-ray
33. Snapshot and golden-file testing
34. Integration and e2e testing patterns
35. Test doubles: mocks, stubs, fakes, spies

### Performance (5)
36. Profiling Python: cProfile, py-spy, scalene, austin
37. Memory profiling: tracemalloc, memray, objgraph
38. Caching strategies: functools, cachetools, diskcache
39. Lazy evaluation patterns: generators, iterators, descriptors
40. C extensions, Cython, Rust via PyO3 / maturin

### Architecture patterns (5)
41. Dependency injection without frameworks
42. Hexagonal architecture (ports & adapters) in Python
43. Event sourcing in Python — implementation
44. Plugin architecture patterns
45. Configuration management: Pydantic Settings, dynaconf, env-driven

### Observability & ops (5)
46. Structured logging in Python: structlog, loguru, stdlib
47. Distributed tracing with OpenTelemetry — Python-side
48. Metrics: Prometheus exposition, OpenTelemetry metrics
49. Graceful shutdown and signal handling (SIGTERM, SIGINT, atexit)
50. Long-running process patterns: daemons, supervisors, restarts

## 5. Batches

| Batch | Docs | Status | Commit |
|---|---|---|---|
| P0 | TASK + INDEX + folder | in_progress | (this commit) |
| B1 | 01–05 | pending | — |
| B2 | 06–10 | pending | — |
| B3 | 11–15 | pending | — |
| B4 | 16–20 | pending | — |
| B5 | 21–25 | pending | — |
| B6 | 26–30 | pending | — |
| B7 | 31–35 | pending | — |
| B8 | 36–40 | pending | — |
| B9 | 41–45 | pending | — |
| B10 | 46–50 | pending | — |
| Closing | INDEX final + ADR-0004 + memory | pending | — |

## 6. Operating rules

- One doc = one Write call. No bulk-generation. No templated paraphrase loops.
- Cite real, named libraries / PEPs / authors. Mark uncertainty honestly.
- Include real Python code where it clarifies. Code blocks should be correct as written (would compile / pass type check if a reader copy-pasted).
- Commit + push after every batch of 5.
- Closing ADR-0004 summarises the corpus.

## 7. Out of scope

- Actual implementation of any of these techniques in `src/runa/`. That's future code work.
- Per-doc adversarial peer review.
- Full coverage of every Python topic. The 50 are chosen for *robust-systems* relevance, not as an exhaustive Python textbook.

## 8. Next exact action

If P0 `in_progress`: commit P0 (TASK + INDEX + folder README), then begin B1 (docs 01–05).
