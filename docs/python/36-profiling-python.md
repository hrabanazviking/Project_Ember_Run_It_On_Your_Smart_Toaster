# 36 — Profiling Python: cProfile, py-spy, scalene, austin

**Category:** Performance
**Runa relevance:** Pi 5 deployment (latency budgets), hot-path optimisation, perf regressions
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

"Don't optimise without profiling" is one of the oldest pieces of programming wisdom. Intuition about what's slow is wrong as often as right. Python has a rich set of profilers — each suited to different questions. **cProfile** for "where does function call time go." **py-spy** for "what is this running process doing right now, without modification." **scalene** for "CPU and memory together, line-by-line." **austin** for "low-overhead sampling, attach-anywhere."

For Runa on a Pi 5 with tight latency budgets (DATA_FLOW §2.2), profiling is how you find what to fix. Each kernel turn budget is a hypothesis — profile to verify or break it.

## 2. Technique / mechanism

**cProfile — function-level, deterministic:**

```python
import cProfile
import pstats

def main():
    ...

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(50)  # top 50
```

Or from CLI:
```bash
python -m cProfile -s cumulative -o profile.out script.py
python -m pstats profile.out
```

**Interpreting cProfile output:**

- `ncalls`: number of times function was called.
- `tottime`: total time *in this function* (excluding sub-calls).
- `cumtime`: total time *including* sub-calls.
- `percall`: per-call time.

Sort by `cumulative` for "where does the time ultimately go"; `tottime` for "what's slow in itself."

**Snakeviz — visual cProfile viewer:**

```bash
pip install snakeviz
snakeviz profile.out
```

Opens an interactive sunburst diagram in the browser. Indispensable for navigating large profiles.

**py-spy — sampling profiler, no code changes:**

```bash
py-spy top --pid 12345          # like `top`, refreshing live
py-spy record -o profile.svg --pid 12345 --duration 30  # flamegraph
py-spy dump --pid 12345          # current stack traces
```

**Key wins of py-spy:**

- *Attach to running process.* No restart needed.
- *No code changes.* No import, no decorator.
- *Low overhead.* Sampling, not instrumenting. ~5% CPU at default rate.
- *Production-friendly.* Can be attached to debug live issues.

Flamegraphs from py-spy are the most-readable way to find hotspots in async / multi-threaded / production Python.

**scalene — CPU + memory + GPU, line-by-line:**

```bash
scalene script.py
```

Output shows per-line:
- CPU time (Python vs C extension).
- Memory allocated.
- GPU usage (if applicable).
- Heat map highlighting hotspots.

Scalene's killer feature: distinguishes time spent in Python code vs time spent in C extensions. Optimising a Python line that's mostly waiting on numpy is futile.

**austin — sampling, ASCII-friendly:**

```bash
austin -i 100 python script.py | austin-tui
```

Similar to py-spy but with different ergonomics. Often combined with `austin-tui` for terminal flame views.

**Line-level profiling: line_profiler:**

```python
from line_profiler import profile

@profile
def hot_function():
    ...

# Run with: kernprof -l -v script.py
```

Per-line timing inside specific functions. Very detailed; deterministic; some overhead. Best for "I know this function is slow; help me see *which line*."

**Async-aware profiling:**

Async code's call stacks are interleaved across coroutines. cProfile's deterministic measurement loses some structure. py-spy with `--native` shows native traces and is friendlier.

**Profile a specific request, not a whole process:**

```python
from contextlib import contextmanager
import cProfile, pstats

@contextmanager
def profile_block(out_path: str):
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield
    finally:
        profiler.disable()
        pstats.Stats(profiler).dump_stats(out_path)

# Around a specific turn
with profile_block("/tmp/turn.prof"):
    await kernel.handle(heard)
```

Profile only the interesting part.

## 3. Key works / libraries

- **cProfile, profile, pstats** — stdlib.
- **`snakeviz`** — github.com/jiffyclub/snakeviz.
- **`py-spy`** — github.com/benfred/py-spy.
- **`scalene`** — github.com/plasma-umass/scalene.
- **`austin`** — github.com/P403n1x87/austin.
- **`line_profiler`** — github.com/pyutils/line_profiler.
- **`pyinstrument`** — github.com/joerick/pyinstrument. Call-stack sampler, very clean output.
- **`flameprof`** — github.com/baverman/flameprof.
- **Beazley** — many talks on profiling and performance.

## 4. Pitfalls and gotchas

- **Profiling itself slows the program.** cProfile overhead ~30%; sampling profilers (py-spy, scalene) much less.
- **Async stacks are confusing.** Coroutine traces look weird; pyinstrument handles them better than cProfile.
- **Optimising before measuring.** Common waste of effort.
- **Optimising what doesn't matter.** A function that's 5% of runtime saved entirely is a 5% gain. Find the 80%.
- **Microbenchmarks lie.** Real workloads have cache effects, GIL contention, IO timing differences not seen in isolation.
- **Reading flamegraphs takes practice.** Wide = slow. Stack depth = call depth. Hot path = thick.
- **Per-call vs per-line.** cProfile is function-level. line_profiler is line-level. Choose right tool for granularity.

## 5. Applicability to Runa

For **Pi 5 latency budgets (DATA_FLOW §2.2)**:

- Profile kernel turns periodically. Target: 95th-percentile turn < deadline.
- Use py-spy attached to running process for "what is Runa doing now" during operator investigation.

For **per-subsystem hotspots**:

- Profile Muninn writes — embedding generation dominates? SQLite contention?
- Profile retrieval — vector search vs SQL filter vs rerank?
- Profile Heimskringla cache — semantic dedup overhead vs cloud call time?

For **release readiness**:

- Before each release, run scalene on critical paths. Compare to baseline. Catch regressions.

For **production debugging**:

- py-spy can attach to a hung Runa process and dump stacks. Combined with watchdog ([[13-watchdog-timers]]).

For **release docs**:

- Document target latencies per subsystem in `docs/operations/PERFORMANCE.md`. Regression budget defined.

What to avoid:

- Don't profile without a question. Random profiling produces random optimisation.
- Don't optimise based on intuition.
- Don't ignore C-extension time. scalene helps make it visible.
- Don't profile microbenchmarks and project to production.

## 6. Open questions

- **Continuous profiling.** Always-on production profiling (Datadog Continuous Profiler, Pyroscope) is increasingly viable. For single-Pi deployment, overkill.
- **Profiling free-threaded Python.** New ground; tools adapt.
- **Profiling JIT'd Python.** PyPy and others have their own profilers.

## 7. References (curated)

- docs.python.org/3/library/profile.html.
- github.com/benfred/py-spy.
- github.com/plasma-umass/scalene.
- github.com/joerick/pyinstrument.
- benfrederickson.com — py-spy author's blog with usage examples.
- Companion docs: [[13-watchdog-timers]], [[37-memory-profiling]], [[40-c-extensions]].
