# 24 — Multiprocessing Patterns and Worker Pools for AI Workloads

**Category:** Event-Driven & Concurrency
**Runa relevance:** Smiðja (CPU-bound tools), Hirð/Völundr (heavy codegen), local inference (model loading)
**Status:** Research synthesis. The CPU-bound complement to [[23-asyncio-structured-concurrency]].
**Last touched:** 2026-05-17

---

## 1. Core idea

ADR-0002 §D-2.1 commits Runa to an asyncio kernel **plus a multiprocessing worker pool** for CPU-bound work. asyncio is excellent for I/O concurrency; it is *useless* for CPU concurrency under Python's GIL. A subagent doing heavy embedding computation, a Smiðja tool running an image transformation, or a Völundr code-analysis pass would stall the entire kernel loop if run synchronously in the same thread.

The worker-pool pattern — a `ProcessPoolExecutor` (or higher-level wrapper) that the asyncio kernel submits jobs to — is the standard answer. CPU jobs run in separate processes (true parallelism, no GIL), the kernel awaits the future, the event loop stays responsive.

The pattern is well-trodden. The pitfalls are also well-trodden. This doc covers both.

## 2. Technical depth

**The standard library's multiprocessing model:**

- `multiprocessing.Process` — a separate OS process running Python.
- `multiprocessing.Pool` — a fixed-size pool of worker processes.
- `concurrent.futures.ProcessPoolExecutor` — modern higher-level API; same underlying mechanism.

**Start methods (`multiprocessing.set_start_method`):**

- **`fork`** (Linux/macOS default historically). Child inherits parent's memory via copy-on-write. Fast startup, can share data without serialisation. **Pitfalls:** thread + fork interactions are deeply broken (fork can deadlock if the parent had non-trivial threads, especially in libraries like OpenSSL or BLAS). asyncio + fork is officially fragile.
- **`spawn`** (Windows default; macOS default since Python 3.8). Child starts fresh, re-imports the codebase, deserialises arguments. Slower startup; safer.
- **`forkserver`** (Linux only). Compromise: a dedicated forkserver process forks new workers from a known-clean state.

**Strong recommendation for Runa: use `spawn`.** Slower startup is paid once at pool creation. The robustness gain is enormous, and behaviour is consistent across Linux/macOS/Windows.

**Pickling pain.** Arguments and return values cross process boundaries via pickle. Things that don't pickle: lambdas, nested functions, file handles, sockets, asyncio loops, threading.Lock, many ML library state objects. Common workaround: pass *primitive types* (str, bytes, dict-of-primitives) and let each worker reconstruct heavier state from those.

**Bridging to asyncio:**

```python
async def run_cpu_job(arg):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(POOL, cpu_function, arg)
    return result
```

`run_in_executor` returns a future the loop awaits. While the job runs in a worker process, the loop is free to schedule other coroutines.

`asyncio.to_thread` is the *threading* version — use for short blocking calls (file I/O, simple blocking C). For CPU, use `run_in_executor` with a `ProcessPoolExecutor`.

**Sizing the pool:**

- Default: `min(4, os.cpu_count())` per ADR-0002 commentary.
- Pi 5 has 4 cores; one for kernel/asyncio, three for worker pool is the natural split.
- Workstation/server: more cores, more workers, but bear in mind memory per worker.
- Memory: each worker is a separate Python process; baseline ~30-50 MB Python + whatever heavy libraries it imports. A worker that loads a 7B GGUF model needs that model's memory *per worker*. Plan accordingly.

**Long-lived workers vs spawn-per-task:**

- ProcessPoolExecutor's workers are long-lived (re-used across tasks). Good for amortising startup cost.
- For tasks that load huge state at startup (LLM weights), long-lived workers with explicit "load on first task" are the right pattern. Pickle a thin handle; the worker loads heavy state lazily.
- For tasks that don't share state, ephemeral processes (`multiprocessing.Process` with `start()` and `join()`) avoid pool-management overhead.

**Worker initialisers.** `ProcessPoolExecutor(initializer=setup_worker, initargs=(...))` runs once per worker. Good place to load shared state (models, indices).

**Beyond standard library:**

- **`concurrent.futures.ThreadPoolExecutor`** — for blocking I/O (not CPU). GIL applies.
- **`joblib.Parallel`** — convenient for embarrassingly-parallel batch work; pickle-savvy.
- **Ray** (anyscale.com) — distributed actors and tasks across nodes. Heavy dependency; right when you need cross-machine workers.
- **Dask** — distributed data parallelism. Right for tabular / array work.
- **`loky`** — robust process pool used internally by joblib and scikit-learn.

**Process-safe state sharing:**

- **Shared memory** (`multiprocessing.shared_memory`, Python 3.8+). Useful for large numpy arrays. Avoid premature use.
- **Manager objects** (`multiprocessing.Manager`). Convenient but slow; use only for low-frequency state.
- **External stores** (Redis, SQLite, filesystem). Most robust for non-trivial shared state.

## 3. Key works

- **Beazley, D.** Various PyCon talks on concurrency — "Concurrency from the Ground Up" (2015), "Generators and the Future of Python" (2014). Educational foundation.
- **The CPython `multiprocessing` module documentation** — docs.python.org/3/library/multiprocessing.html.
- **PEP 703 — Making the Global Interpreter Lock Optional in CPython.** Adopted; experimental in 3.13. The long-term path that may eventually obviate multiprocessing for many use cases.
- **PEP 734 — Subinterpreters.** Per-interpreter GIL; a middle ground.
- **Ray paper** — Moritz et al., "Ray: A Distributed Framework for Emerging AI Applications," OSDI 2018.
- **joblib documentation** — joblib.readthedocs.io.

## 4. Empirical results

- A ProcessPoolExecutor with `spawn` on a 4-core Pi 5 reliably executes CPU-bound jobs at ~3.5× single-core throughput (small overhead for IPC).
- Startup cost per worker (`spawn`): ~200-500ms on Pi 5 depending on imports. Long-lived workers amortise this trivially.
- Pickle overhead: negligible for small arguments; can dominate for large numpy arrays (use shared memory).
- Common production failures:
  - Workers silently dying without restart (use `initializer` and monitor pool health).
  - Memory bloat over time (Python's GC + long-lived workers can leak; recycle workers periodically with `max_tasks_per_child`).
  - Deadlocks when forking from a process with threads (use `spawn`).
  - Pickled-function-not-found when refactoring (top-level functions only for `submit` targets).

## 5. Applicability to Runa

For the **Smiðja worker pool** (per ADR-0002 §D-2.1):

- Created once at kernel start, sized via config (default 3 on Pi 5).
- `spawn` start method (cross-platform safety, asyncio compatibility).
- Heavy jobs (Smiðja tools that are CPU-bound: image processing, large file analysis, embedding generation in bulk) submitted via `loop.run_in_executor`.
- Default worker initialiser loads commonly-shared state (e.g. the embedding model used by Muninn's writer) so workers are warm.

For **Hirð / Völundr** (codegen):

- Code generation that calls a local LLM in the worker pool is the natural pattern. The local LLM (via llama.cpp) is heavy to load; Völundr's worker should pin it for the lifetime of the pool.
- The kernel awaits Völundr; Völundr's process generates, validates, returns the result.

For **Eir** (background maintenance):

- Reflection passes, Muninn consolidation, embedding re-computation are batch CPU work. Submit to the worker pool; await; don't block the kernel.

For **adapter-side CPU work**:

- Most adapters are I/O bound and stay on asyncio. But e.g. a screenshot-processing adapter, an audio-codec adapter, an image-recognition adapter — these submit to the pool.

Practical guidance:

- **Job arguments should be small primitives.** Don't pickle large objects across the boundary. Pass IDs and let the worker fetch what it needs from disk / shared memory.
- **Worker initialiser** loads heavy shared state. Document what each worker loads.
- **Cap per-job memory.** A worker that needs >2 GB has implications for pool sizing on a 16 GB Pi.
- **Recycle workers** with `max_tasks_per_child=100` (or similar) to prevent long-running memory leaks.
- **Log per-job timing.** A misbehaving job dragging the pool down should be visible in audit logs.

What to avoid:

- Don't use `fork` start method. Especially with asyncio. Hard-to-debug deadlocks.
- Don't share asyncio queues / locks across processes. Use proper IPC (`multiprocessing.Queue`, `multiprocessing.Manager`, or a file/socket).
- Don't submit closures or lambdas. Top-level functions only.
- Don't open a worker pool inside another worker. The pool lives at the kernel level only.
- Don't expect workers to import all of `runa.core`. Keep worker code in a separate module (`runa.workers.*`) that imports only what it needs.

## 6. Open questions

- **PEP 703 free-threaded Python.** Once stable, parallelism without multiprocessing may be cleaner for many use cases. Wait-and-see.
- **PEP 734 subinterpreters.** Per-interpreter GIL gives parallelism with cheaper isolation than multiprocessing. Promising; needs ecosystem maturity.
- **Ray for distributed.** When Runa runs across machines, the worker-pool pattern naturally extends to Ray. Switching from `ProcessPoolExecutor` to `Ray.remote` is a localised change.
- **GPU workers.** Local CUDA / Metal / OpenCL workers add a layer of resource management (CUDA contexts don't fork). When Runa eventually serves models locally with GPU acceleration, this matters.

## 7. References (curated)

- docs.python.org/3/library/multiprocessing.html
- docs.python.org/3/library/concurrent.futures.html
- joblib.readthedocs.io
- docs.ray.io
- PEP 703 — Making the GIL Optional.
- PEP 734 — Subinterpreters.
- Beazley's PyCon talks on concurrency (search PyCon US).
- Companion docs: [[23-asyncio-structured-concurrency]] (the I/O side), [[21-actor-model-supervision]] (the conceptual frame), [[31-edge-llm-pi5]] (Pi resource budgets).
