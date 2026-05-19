# SD303: Performance Engineering & Optimization
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 3, Semester 1
**Prerequisites:** SD203 (Software Architecture & Design), SD201 (Object-Oriented Design & Patterns)
**Instructor:** Dr. FáǪvér Þorgrímsson, Faculty of Computational Arts

> *"Sleipnir bears the Allfather over sea and stone, over cloud and abyss — eight hooves that never falter, eight legs that know no rest. So must our systems run: swift, tireless, and sure-footed across every terrain."* — FáǪvér Þorgrímsson, *The Eight-Legged Machine* (2038)

---

## Course Description

Performance Engineering & Optimization is both an art and a discipline — the craft of making software systems fast, efficient, and scalable without sacrificing correctness, readability, or maintainability. This course treats performance not as an afterthought or a debugging exercise, but as a first-class engineering concern that must be designed into systems from the start.

The course is structured around the metaphor of Sleipnir, Odin's eight-legged horse — the fastest mount in all the nine realms. Each of Sleipnir's legs represents a dimension of performance: latency, throughput, memory efficiency, CPU utilization, I/O efficiency, concurrency, scalability, and resilience. A system that is fast but fragile has broken legs. A system that is efficient but opaque has no eyes. We build systems that run like Sleipnir — fast, sure-footed, and visible to their riders.

Students will learn profiling methodology, algorithmic complexity analysis, memory hierarchy optimization, cache-conscious data structures, concurrent and parallel programming patterns, I/O optimization, database query tuning, network performance, frontend rendering optimization, and continuous performance monitoring. The course culminates in a capstone project where students take a real-world system from the University's RúnarNet platform and achieve a 10× performance improvement through systematic analysis and targeted optimization.

The 2040 landscape brings new challenges: AI inference latency is the new bottleneck, carbon-aware computing demands efficiency beyond speed, and heterogeneous architectures (CPU + GPU + TPU + neuromorphic) require optimization across multiple computational substrates simultaneously. This course meets those challenges head-on.

---

## Lectures

### ᚠ Lecture 1: The Speed of Sleipnir — Foundations of Performance Engineering

**Date:** Week 1, Session 1

#### Overview

Performance engineering did not begin with computers. It began with the first human who looked at a process and wondered: *can this be done faster?* This opening lecture establishes the intellectual foundations of the field — from the efficiency of Norse shipbuilding to the performance budgets of modern software — and introduces the Eight-Legged Model (ELM) that structures the entire course. We examine why performance is a design concern, not a debugging task, and why "premature optimization is the root of all evil" has been profoundly misunderstood.

#### Lecture Notes

Donald Knuth's 1974 dictum — "premature optimization is the root of all evil" — is the most quoted and most misapplied statement in software engineering. Knuth was arguing against micro-optimizations applied without measurement: replacing array indexing with pointer arithmetic, unrolling loops by hand, hand-writing assembly for code that spends 0.01% of execution time. He was *not* arguing against designing systems with performance in mind. The full quote reveals his nuance:

> "We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. Yet we should not pass up our opportunities in that critical 3%."

The critical 3% matters. A system that is architected for performance from the start — with appropriate data structures, sensible algorithmic choices, and awareness of where bottlenecks will form — is fundamentally different from a system that is "optimized later." The first kind requires targeted micro-optimizations in a few hot spots. The second kind requires rewrites.

**The Viking Ship as Performance Architecture.** The Oseberg ship (c. 820 CE) and the Gokstad ship (c. 890 CE) are masterclasses in performance engineering. These vessels were not merely fast — they were optimized for their *entire operational context*. They were shallow-drafted (to navigate fjords and rivers), flexible (to handle North Sea swells without breaking), light (to be portaged over land), and double-ended (to reverse direction without turning). Every design decision served multiple performance constraints simultaneously. A port-heavy warship would be fast in open water but useless in a fjord raid. A shallow river boat would be maneuverable but sink in the Atlantic. The longship's genius was its *balanced optimization* across a complex performance envelope.

Software performance engineering demands the same discipline. A system optimized purely for throughput may catastrophically increase latency. A system optimized for latency may waste CPU cycles. A system optimized for memory may sacrifice cache locality. The performance engineer's task, like the shipwright's, is to find the right balance for the mission.

**The Eight-Legged Model (ELM).** This course organizes performance around eight dimensions, each named for one of Sleipnir's legs:

| Leg | Dimension | Core Question |
|-----|-----------|---------------|
| 1 | **Latency** | How long does a single operation take? |
| 2 | **Throughput** | How many operations can complete per unit time? |
| 3 | **Memory Efficiency** | How much RAM does the system consume, and how well does it use the memory hierarchy? |
| 4 | **CPU Utilization** | How effectively does the system use available compute cycles? |
| 5 | **I/O Efficiency** | How well does the system manage disk, network, and device I/O? |
| 6 | **Concurrency** | How does the system handle simultaneous work? |
| 7 | **Scalability** | How does performance change as load increases? |
| 8 | **Resilience** | How does performance degrade under failure conditions? |

The first six legs are about raw performance. The seventh and eighth are about *sustained* performance — the difference between a sprint and a marathon, between a longship in calm water and a longship in a storm.

**Performance as a Feature.** In 2040, performance is no longer a "non-functional requirement" — a label that consigned it to second-class status for decades. Performance is a *feature*. Users perceive latency directly: a page that loads in 100ms feels instant; a page that loads in 1000ms feels sluggish; a page that loads in 10,000ms feels broken. Google's 2012 study showed that a 400ms delay in search results reduced search volume by 0.44%. Amazon's 2006 study showed that every 100ms of latency cost 1% of sales. In 2040, with AI inference pipelines, real-time AR overlays, and edge computing, the performance stakes are even higher.

The University of Yggdrasil's own RúnarNet platform — the infrastructure that runs all student-facing services — processes 2.3 million requests per second at peak. A 10ms latency improvement across the platform saves 23,000 seconds of user time per second of peak load. Performance at scale is human benefit at scale.

**Measurement Before Optimization.** The first law of performance engineering is: *measure*. Not guess. Not assume. Not "I think the database is slow." Measure. Every optimization begins with a profiler, a benchmark, and a hypothesis. Every optimization ends with a measurement that confirms or denies the hypothesis. Optimization without measurement is superstition.

The lecture concludes with a live demonstration: the instructor takes a deliberately slow Python web service, profiles it with the University's SleipnirProf tool (built on cProfile, py-spy, and custom AI-driven hotspot detection), identifies the top 3 bottlenecks, and applies targeted fixes — reducing response time from 1200ms to 45ms. The optimization is 96.25% faster. The code changes: 4 lines.

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine: Performance Engineering for Modern Systems*. University of Yggdrasil Press. Chapters 1-2.
- Gregg, B. (2021). *Systems Performance: Enterprise and the Cloud* (2nd ed.). Addison-Wesley. Chapters 1-2.
- Hennessy, J. L., & Patterson, D. A. (2019). *Computer Architecture: A Quantitative Approach* (6th ed.). Morgan Kaufmann. Chapter 1.
- Knuth, D. (1974). "Structured Programming with go to Statements." *ACM Computing Surveys*, 6(4), 261-301. [Read the full context of the "premature optimization" quote.]

#### Discussion Questions

1. Knuth argued that premature optimization is evil, but the Viking shipwrights optimized from the start. Is "premature optimization" still the right framing, or should we distinguish between "architectural performance design" and "micro-optimization"?
2. The ELM model lists resilience as a performance dimension. Is this a legitimate framing, or does it conflate reliability with performance? How does latency under failure differ from latency under normal load?
3. A 10ms latency improvement across RúnarNet saves 23,000 seconds of user time per second at peak. But latency improvements often require engineering time that could be spent on features. How should a team decide when performance work is worth the investment?

---

### ᚢ Lecture 2: The Measuring Eye of Mímir — Profiling & Measurement Methodology

**Date:** Week 1, Session 2

#### Overview

Mímir, the wise being who guards the well of wisdom, sacrificed an eye to drink from its waters and gain knowledge. The performance engineer makes a similar trade: sacrificing the illusion of understanding for the reality of measurement. This lecture covers the full spectrum of profiling methodology — from wall-clock timing to CPU cycle counting, from statistical profiling to deterministic tracing, from single-thread analysis to distributed tracing across microservices. We introduce the University's SleipnirProf toolkit and establish the measurement-first methodology that governs every optimization decision in this course.

#### Lecture Notes

**The Measurement Hierarchy.** Profiling tools exist on a spectrum from low-overhead/low-precision to high-overhead/high-precision:

| Method | Overhead | Precision | Best For |
|--------|----------|-----------|----------|
| Wall-clock timing (`time.time()`) | Near zero | Low (ms-level) | Quick sanity checks |
| Statistical profiling (perf, py-spy) | 1-5% | Medium (sample-based) | Production hot path |
| Instrumented profiling (cProfile, VTune) | 10-100× slowdown | High (call-level) | Development bottleneck analysis |
| Deterministic tracing (ftrace, eBPF) | 5-20% | Very high (event-level) | Kernel and syscall analysis |
| Hardware performance counters (PMU) | Near zero | Maximum (cycle-level) | Cache, branch prediction analysis |

The performance engineer must know *which tool to use when*. Using an instrumented profiler in production adds 100× latency — you'll find the profiler, not the problem. Using wall-clock timing for a cache-miss investigation tells you nothing about *why* the code is slow.

**Statistical Profiling: The Workhorse.** Statistical profilers work by sampling — periodically interrupting the program (typically 100-1000 times per second) and recording the call stack at the moment of interruption. After enough samples, the statistical distribution approximates the true distribution of execution time. The key insight: you don't need to measure every function call to find the hot paths. You need enough samples to be *confident* that the top N functions truly account for the top N% of execution time.

The University's SleipnirProf uses a Bayesian approach to statistical profiling. Instead of fixed-rate sampling, the profiler allocates samples proportionally to *estimated information gain* — sampling more densely in code regions where execution time variance is high, and sparsely in regions where execution time is stable. This approach, described in Þorgrímsson & Lindqvist (2037), achieves the same identification accuracy as fixed-rate profiling with 40% fewer samples.

**Flame Graphs: Seeing the Forest and the Trees.** Brendan Gregg's flame graph (2011) remains one of the most powerful visualization tools in performance engineering. A flame graph displays a hierarchical profile as a stack of rectangles: the x-axis represents the proportional time spent in each function, and the y-axis represents the call stack depth. The result looks like a mountain landscape — the peaks are the hot paths. Flame graphs work because the human visual system is extraordinarily good at spotting patterns in spatial representations, but terrible at spotting patterns in tables of numbers.

In 2040, SleipnirProf extends flame graphs with three innovations:

1. **Differential flame graphs** — Compare two profiles (before and after an optimization) side-by-side. Functions that got faster shrink; functions that got slower grow. The visualization tells you immediately whether your optimization worked and whether it introduced regressions elsewhere.
2. **AI-annotated flame graphs** — The profiler's AI agent identifies unusual patterns (e.g., "this function accounts for 23% of execution time but is only 8 lines of code — likely a cache miss hotspot") and annotates the graph with diagnostic suggestions.
3. **Time-series flame graphs** — Animate a flame graph over time to see how the performance profile shifts as the workload changes. Essential for understanding systems with periodic behavior (garbage collection cycles, cache warming, connection pool saturation).

**Distributed Tracing: Following a Request Across the Nine Realms.** When a user clicks "submit order" on the RúnarNet platform, the request passes through the API gateway, the authentication service, the order service, the inventory service, the payment service, and the notification service before returning a response. Each service is a separate process, possibly on a separate machine. A latency problem in the total request could originate in any one of them — or in the network between them.

Distributed tracing solves this by attaching a unique trace ID to the original request and propagating it through every service. Each service records a "span" — its contribution to the total latency — and ships the span data to a central collector. The result is a complete timeline of the request's journey through the system. OpenTelemetry, the 2040 standard for distributed tracing, provides vendor-neutral instrumentation for this purpose.

The University's RúnarNet implements distributed tracing with OpenTelemetry and stores trace data in the SleipnirProf analytics backend. Students in this course have access to anonymized production trace data for analysis exercises.

**Benchmarking: The Art of Meaningful Measurement.** Profiling tells you *where* time is spent. Benchmarking tells you *how much* time is spent. A benchmark without context is meaningless. The performance engineer must specify:

1. **The workload** — What inputs are being processed? Synthetic benchmarks use simplified workloads; production benchmarks use real traffic patterns.
2. **The environment** — What hardware, OS, runtime, and configuration? A benchmark on a developer's M4 MacBook is not comparable to a benchmark on a production ARM server.
3. **The metric** — Median? P95? P99? Maximum? The metric depends on the SLA. For user-facing requests, P95 or P99 is appropriate. For batch processing, throughput is usually the right metric.
4. **The warm-up** — JIT-compiled runtimes (JVM, V8, PyPy) need warm-up iterations before the benchmark is representative. Cache hierarchies need to be populated. Connection pools need to be established.
5. **The duration** — Short benchmarks are dominated by noise. Long benchmarks are expensive. The standard practice is to run until the confidence interval of the mean is within 5% of the estimate.

The gold standard for microbenchmarking in 2040 is the JMH (Java Microbenchmark Harness) for JVM languages, Criterion.rs for Rust, and the Python `pytest-benchmark` framework with SleipnirProf integration for Python. All three handle warm-up, iteration counting, and statistical analysis automatically.

**Avoiding Measurement Bias.** Every measurement perturbs the system being measured (the observer effect). Common sources of measurement bias in performance engineering:

- **Profiling overhead** — The profiler itself consumes CPU, memory, and I/O. In statistical profiling, the overhead is low but non-zero. In instrumented profiling, the overhead can be dramatic.
- **Cache warming** — The first run of a benchmark populates caches (CPU L1/L2/L3, disk, network). Subsequent runs benefit from these warm caches. Always discard the first iteration or use a "warm-up" phase.
- **Background noise** — Other processes on the same machine, network traffic, thermal throttling, and OS scheduling all introduce noise. Production systems are inherently noisy. Benchmarking on isolated hardware reduces noise but may not represent production behavior.
- **Branch prediction warming** — Modern CPUs use branch prediction to speculate on which path code will take. The first few iterations "train" the branch predictor, making subsequent iterations faster. This is a real performance improvement that disappears when the workload changes unpredictably.

#### Required Reading

- Gregg, B. (2021). *Systems Performance: Enterprise and the Cloud* (2nd ed.). Addison-Wesley. Chapters 2-4 (Profiling Methodology, Operating Systems, CPUs).
- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 3: "The Measuring Eye."
- Gregg, B. (2011). "Flame Graphs." *ACM Queue*. [The original flame graph paper.]
- OpenTelemetry Documentation (2040). *Tracing API Specification*. https://opentelemetry.io/docs/

#### Discussion Questions

1. The Bayesian adaptive sampler in SleipnirProf allocates samples based on estimated information gain. What are the failure modes of this approach? When might a fixed-rate sampler outperform an adaptive one?
2. You profile a production service and find that function `processRequest()` accounts for 45% of execution time. But `processRequest()` is 2,000 lines of code. What is your next step — and why is "optimize processRequest()" the wrong answer?
3. A colleague argues that distributed tracing adds too much overhead and suggests using "black-box" approaches that infer latency from log timestamps. Under what conditions is this colleague right?

---

### ᚦ Lecture 3: The Complexity of Yggdrasil — Algorithmic Complexity & Asymptotic Performance

**Date:** Week 2, Session 1

#### Overview

Yggdrasil, the world tree, connects all nine realms — its roots plunge deep, its branches reach wide, and the complexity of its structure mirrors the complexity of the algorithms we write. This lecture covers algorithmic complexity analysis as the foundation of performance engineering. Not the Big-O notation you learned in CS101 and forgot, but a practitioner's understanding of how algorithmic choices shape real-world performance in the age of cache hierarchies, branch predictors, and heterogeneous compute hardware.

#### Lecture Notes

**Beyond Big-O: The Full Complexity Picture.** Big-O notation captures the *asymptotic* behavior of an algorithm — how its runtime scales as the input size grows toward infinity. This is useful for academic analysis but incomplete for practical performance engineering because:

1. **Constants matter.** An O(n log n) algorithm with a constant of 10,000 will lose to an O(n²) algorithm with a constant of 3 for all practical input sizes. The standard library `sort()` in Python, Java, and C++ all use hybrid algorithms (Timsort, Dual-Pivot Quicksort) precisely because the constant factors matter for real data.

2. **Cache effects dominate.** An algorithm that is O(n) but makes random memory accesses will be dramatically slower than an algorithm that is O(n log n) but is cache-friendly. On modern hardware, a cache miss costs 200-400 cycles; a cache hit costs 4 cycles. That's a 50-100× difference per memory access. Big-O assumes all memory accesses are equal. They are not.

3. **Input distributions matter.** Quicksort is O(n²) worst case but O(n log n) average case. For nearly-sorted data, Timsort is O(n). The "best" algorithm depends on what you're sorting and how — a fact that Big-O alone cannot capture.

**The Cache Complexity Model.** In 1999, Alpern, Carter, and Feig introduced the *cache complexity model* (later refined by Frigo, Leiserson, Prokop, and Ramachandran as the *cache-oblivious model*). This model counts *cache misses* rather than operations, because on modern hardware a cache miss is 50-100× more expensive than a cache hit.

The cache complexity model defines:

- **Q(n)** = the number of cache misses incurred by the algorithm on an input of size n
- **The cache parameters** = (L, Z) where L is the cache line size (typically 64 bytes) and Z is the cache size (typically 32KB for L1, 256KB-1MB for L2, 8-32MB for L3)

An algorithm with Q(n) = O(n/L) is *cache-optimal* — it touches each cache line only O(1) times. An algorithm with Q(n) = O(n²/L) is *cache-hostile* — it makes O(n²) cache misses, each costing hundreds of cycles.

**Matrix Multiplication: A Case Study in Cache Complexity.** Naive matrix multiplication (ijk order) has:

- Operation count: O(n³)
- Cache misses: O(n³/L) — *every* inner loop iteration causes a cache miss because the matrix is traversed in column order (cache-hostile access pattern)

Blocked matrix multiplication (tiling the matrices into cache-sized blocks) has:

- Operation count: O(n³) (unchanged)
- Cache misses: O(n³/(L√Z)) — dramatically fewer cache misses because each block fits in cache

Same Big-O complexity, dramatically different real performance. On a 2040 server with a 32MB L3 cache, blocked matrix multiplication of two 4096×4096 matrices is roughly 10-20× faster than naive multiplication. Not 10% faster. 10-20× faster. This is the power of cache-aware algorithm design.

**Amortized Analysis: The Longship's Average Speed.** A Viking longship doesn't travel at its maximum speed for the entire voyage. It rows hard through narrows, sails with the wind in open water, and ports over land at walking pace. The *average* speed over the entire voyage is what matters — and that's the insight of amortized analysis.

Some data structure operations are individually expensive but *amortized* cheap. A dynamic array's `append()` operation is O(1) amortized even though the occasional resize is O(n), because the resize happens only every n operations. A hash table's insertion is O(1) amortized even though the occasional rehash is O(n), because the rehash happens only when the load factor crosses a threshold.

Amortized analysis is crucial for performance engineering because real systems have *bursty* behavior. A garbage collection pause that takes 50ms every second is an amortized cost of 5ms per operation — but the 50ms pause itself may violate a latency SLA. The performance engineer must understand both the amortized cost (for throughput planning) and the worst-case cost (for latency guarantees).

**Algorithm Selection in 2040.** The rise of AI-assisted development has changed how engineers select algorithms — but not how they *should* select them. An AI coding agent will typically suggest the most common algorithm for a given problem (quicksort for sorting, binary search for lookup, Dijkstra's for shortest path). This is usually fine, but the performance engineer must know when to override:

- **Nearly-sorted data** → Timsort, not quicksort
- **Integer data in a known range** → Counting sort or radix sort, not comparison sorts
- **String data with common prefixes** → Trie-based search, not hash tables
- **Graph data with negative weights** → Bellman-Ford, not Dijkstra's
- **Large datasets that don't fit in memory** → External sorting, not in-memory algorithms

The SleipnirProf system includes an AI-powered "algorithm advisor" that analyzes workload characteristics (data size, data distribution, access patterns) and recommends algorithms. Students learn to evaluate these recommendations critically — the AI's suggestion is a starting point, not a final answer. The engineer who blindly accepts the AI's algorithm choice is no different from the engineer who blindly follows Stack Overflow — both are delegating judgment rather than exercising it.

#### Required Reading

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press. Chapters 2-4 (Algorithmic Foundations), Chapter 17 (Amortized Analysis).
- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 4: "The Complexity Tree."
- Frigo, M., Leiserson, C. E., Prokop, H., & Ramachandran, S. (1999/2012). "Cache-Oblivious Algorithms." *ACM Transactions on Algorithms*, 8(1), 1-49. [The foundational paper on cache-aware algorithm design.]
- Musser, D. R. (1997). "Introspective Sorting and Selection Algorithms." *Software: Practice and Experience*, 27(8), 983-993. [The paper that introduced Timsort's predecessor — introsort — which switches algorithms based on observed depth.]

#### Discussion Questions

1. Blocked matrix multiplication has the same Big-O complexity as naive multiplication but is 10-20× faster in practice. Does this mean Big-O is useless, or does it mean we need additional models (cache complexity, constant factors) to complement it?
2. A hash table has O(1) amortized insertion but O(n) worst-case insertion during a rehash. You're building a real-time trading system where a single latency spike above 100μs costs millions. Do you use the hash table? What are your alternatives?
3. The AI algorithm advisor in SleipnirProf recommends Timsort for nearly-sorted data but quicksort for random data. How would you validate this recommendation in production? What measurements would you need?

---

### ᚨ Lecture 4: The Forge of Sindri — Memory Architecture & Cache Optimization

**Date:** Week 2, Session 2

#### Overview

Sindri's forge produced the greatest treasures of the gods — Mjǫllnir, Gungnir, Draupnir — each requiring the smith's deep understanding of materials, heat, and timing. In the same way, the performance engineer must understand the "materials" of modern computation: the memory hierarchy. This lecture dives deep into how modern processors interact with memory — from registers to L1/L2/L3 caches to RAM to disk — and teaches students to write code that respects the cache hierarchy as Sindri respected the grain of the metal he forged.

#### Lecture Notes

**The Memory Hierarchy: A Tower of Increasing Latency.** Modern processors operate on a fundamental mismatch: CPU cores can execute operations in nanoseconds, but memory accesses take hundreds of nanoseconds. To bridge this gap, processors use a hierarchy of caches, each smaller and faster than the one below it:

| Level | Size (2040 typical) | Latency | Bandwidth |
|-------|---------------------|---------|-----------|
| Register | ~1KB | 0 cycles | Unlimited |
| L1 Cache | 64KB per core | 4 cycles (~1ns) | ~2TB/s |
| L2 Cache | 256KB-1MB per core | 12 cycles (~3ns) | ~1TB/s |
| L3 Cache | 8-64MB shared | 40 cycles (~10ns) | ~500GB/s |
| DRAM | 16-256GB | 200-400 cycles (~50-100ns) | ~100GB/s |
| NVMe SSD | 1-8TB | 10,000-100,000 cycles (~5-50μs) | ~7GB/s |
| Network Storage | Effectively unlimited | 100,000+ cycles (~50μs-10ms) | Variable |

The performance implication is stark: a CPU that can execute 4-8 instructions per cycle may sit idle for 200+ cycles waiting for a DRAM access. This is the *memory wall* — the single most important performance constraint in modern computing. Every algorithm and data structure must be designed to minimize cache misses and maximize data locality.

**Cache Lines: The Fundamental Unit of Data Movement.** Data moves between cache levels not in bytes, but in *cache lines* — contiguous blocks of 64 bytes on all modern x86 and ARM processors. When the CPU reads a single byte from DRAM, it actually reads the entire 64-byte cache line containing that byte. This means:

- **Spatial locality matters.** If you access byte 0 of a cache line, bytes 1-63 are now "free" to access. A program that accesses adjacent memory locations (array traversal) exploits this automatically. A program that jumps randomly through memory (pointer chasing through a linked list) pays the full DRAM latency for each access.
- **False sharing is real.** Two threads writing to different variables on the same cache line will cause the cache line to bounce between cores — a phenomenon called *false sharing*. Each write invalidates the other core's copy, triggering cache coherence traffic. A seemingly lock-free algorithm can become a scalability bottleneck due to false sharing.
- **Data alignment matters.** A struct whose fields span two cache lines will require two cache line loads instead of one. The `__attribute__((packed))` optimization in C/C++ saves memory at the cost of misaligned (and therefore slower) accesses.

**Cache-Friendly Data Structures.** The performance difference between cache-friendly and cache-hostile data structures is enormous. Consider three ways to store a list of key-value pairs:

| Data Structure | Sequential Lookup | Random Lookup | Memory per Entry | Cache Behavior |
|---------------|-------------------|---------------|------------------|---------------|
| Sorted array of structs | O(log n) binary search | O(log n) | 16 bytes | Excellent (contiguous) |
| Hash table with open addressing | O(1) amortized | O(1) | 16 bytes | Good (mostly contiguous) |
| Linked list of node pointers | O(n) linear scan | O(n) | 24+ bytes | Terrible (pointer chasing) |

For sequential iteration, the sorted array and the hash table are both cache-friendly — the CPU prefetches cache lines ahead of the access pattern, and each 64-byte cache line delivers 4 entries. The linked list is cache-hostile — each entry requires a pointer dereference to a random location, causing a cache miss.

**Array of Structures vs. Structure of Arrays (AoS vs. SoA).** One of the most impactful design decisions in performance-critical code is how to organize data for access patterns:

```python
# Array of Structures (AoS) — natural but potentially slow
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mass: float
    charge: float

particles: list[Particle] = [...]

# Structure of Arrays (SoA) — cache-friendly for vectorized operations
class ParticleSystem:
    x: array[float]      # all x positions contiguous
    y: array[float]      # all y positions contiguous
    z: array[float]      # all z positions contiguous
    vx: array[float]     # all x velocities contiguous
    vy: array[float]
    vz: array[float]
    mass: array[float]
    charge: array[float]
```

If the hot loop computes `x[i] += vx[i] * dt`, the SoA layout loads 16 x-values and 16 vx-values per cache line (assuming 32-bit floats), achieving near-100% cache utilization. The AoS layout loads x, y, z, vx, vy, vz, mass, and charge for every particle, using only 2 out of 32 bytes per cache line — 6.25% utilization.

**Prefetching: Hiding Latency with Foresight.** Modern CPUs include hardware prefetchers that detect sequential (and some strided) access patterns and begin loading cache lines *before* the program requests them. The prefetcher is remarkably effective for predictable patterns — it can reduce L2 miss rates by 80-90% for array traversals.

Software prefetching (`__builtin_prefetch` in GCC/Clang, `_mm_prefetch` with SSE intrinsics) allows the programmer to hint the prefetcher about irregular access patterns. This is useful when:

- Walking a linked list where the next node's address is known before it's accessed
- Accessing a hash table where the bucket address can be computed one or two steps ahead
- Processing a graph where neighbor addresses are known before traversal

Software prefetching is an advanced technique that requires profiling to validate. An incorrectly placed prefetch can *reduce* performance by polluting the cache with data that won't be used.

**Memory Allocation: The Hidden Performance Tax.** Memory allocation is not free. `malloc()` in C, `new` in Java, or object allocation in Python/JavaScript all involve:

1. Finding a free block of the right size (and possibly splitting a larger block)
2. Updating the allocator's metadata
3. Possibly triggering a garbage collection (in managed languages)
4. Possibly triggering an OS page fault (for large allocations)

The worst allocation pattern for performance is "churning" — rapidly allocating and freeing small objects. This pollutes the allocator's free lists, fragments the heap, and triggers frequent garbage collections. The performance engineer has two options:

- **Object pooling.** Pre-allocate a pool of objects and reuse them instead of freeing and reallocating. Used for frequently-created objects (e.g., packet buffers, request objects, AST nodes).
- **Arena allocation.** Allocate all objects for a computation from a contiguous memory region ("arena"). When the computation is done, free the entire arena at once. Used for request handlers, game physics steps, and compiler passes.

In 2040, the University's Sleipnir runtime includes a *generational arena allocator* that combines pooling with generational segmentation — the most frequently allocated objects (generations 0-2) are served from thread-local arenas that never trigger global GC, while long-lived objects (generation 3+) are managed by a concurrent collector. This design reduces allocation latency from ~200ns (default allocator) to ~3ns (thread-local arena).

#### Required Reading

- Hennessy, J. L., & Patterson, D. A. (2019). *Computer Architecture: A Quantitative Approach* (6th ed.). Morgan Kaufmann. Chapters 2 (Memory Hierarchy) and 5 (Memory Architecture).
- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 5: "The Forge of Memory."
- Drepper, U. (2007). "What Every Programmer Should Know About Memory." *Red Hat, Inc.* [The canonical reference on memory architecture for software engineers.]
- Lemire, D. (2024). "Array layouts for comparison-based searching." *Software: Practice and Experience*, 54(2), 345-370.

#### Discussion Questions

1. A colleague argues that cache optimization is "premature optimization" and that the compiler should handle it. Under what circumstances is this colleague right? When should you manually restructure data layouts for cache performance?
2. SoA layout is faster for vectorized operations but harder to write and maintain. What is the threshold — in terms of data size and operation frequency — where the performance gain justifies the code complexity?
3. The Sleipnir runtime uses a generational arena allocator that reduces allocation latency from ~200ns to ~3ns. What are the tradeoffs? When would you prefer a standard allocator?

---

### ᚱ Lecture 5: Eight Hooves in Concert — Concurrency, Parallelism & Lock-Free Design

**Date:** Week 3, Session 1

#### Overview

Sleipnir's eight legs move in perfect coordination — never tangling, never conflicting, each leg knowing its place in the gait. Concurrent software must achieve similar coordination: multiple threads of execution sharing resources without stepping on each other. This lecture covers the fundamental models of concurrency (shared-memory, message-passing, actor-based), the pathologies of naive synchronization (deadlocks, livelocks, priority inversion), and the modern shift toward lock-free and wait-free data structures that achieve coordination without mutual exclusion.

#### Lecture Notes

**Concurrency vs. Parallelism: The Critical Distinction.** These terms are frequently conflated but describe fundamentally different concerns:

- **Concurrency** is about *dealing with* multiple things at once — managing shared resources, handling events asynchronously, and ensuring correct behavior when multiple logical threads interact. A concurrent program may run on a single core (e.g., a web server handling multiple requests with async I/O).
- **Parallelism** is about *doing* multiple things at once — utilizing multiple cores, GPUs, or machines to perform computation faster. A parallel program may have no shared resources (e.g., a MapReduce job processing independent chunks of data).

All parallel programs are concurrent (they manage multiple execution threads), but not all concurrent programs are parallel (they may time-share a single core). The distinction matters because the *bugs* are different:

| Bug Type | Concurrency Bug | Parallelism Bug |
|----------|----------------|-----------------|
| Race condition | Two threads write the same variable | Two threads compute overlapping results |
| Deadlock | Two threads wait for locks each other holds | Rare (if work is truly independent) |
| Livelock | Two threads repeatedly retry conflicting operations | Rare (if workload is partitioned) |
| Starvation | One thread never acquires a needed lock | One thread never gets CPU time |

**The Synchronization Problem: Mjǫllnir's Weight.** When Thor's hammer Mjǫllnir is placed on a table, no one can lift it except Thor. This is the essence of a mutex (mutual exclusion lock): a shared resource that only one thread can "lift" at a time. Mutexes are the simplest and most common synchronization primitive, but they have serious performance implications:

- **Lock contention.** When multiple threads compete for the same lock, they form a queue. Contended locks serialize execution, eliminating the parallelism benefit.
- **Lock convoy.** When a thread holding a lock is preempted by the OS scheduler, every other thread waiting for that lock is also blocked — even if the preempted thread is doing no useful work.
- **Deadlock.** Thread A holds Lock 1 and waits for Lock 2. Thread B holds Lock 2 and waits for Lock 1. Both threads wait forever. Deadlocks are avoided by imposing a global lock ordering, but lock ordering is difficult to maintain in large codebases.

**Lock-Free Data Structures: The Lesson of Heimdallr.** Heimdallr, the guardian of Bifrǫst, can see all things simultaneously without turning his head. Lock-free data structures achieve something similar — multiple threads can access shared data without blocking, using atomic operations that guarantee progress for at least one thread.

The key primitive is CAS (Compare-And-Swap): an atomic instruction that reads a memory location, compares it to an expected value, and writes a new value *only if* the comparison succeeds. CAS is the foundation of lock-free programming:

```python
# Lock-free counter increment using CAS
def increment(lock_free_counter):
    while True:
        old_value = lock_free_counter.value  # read
        new_value = old_value + 1            # compute
        if CAS(lock_free_counter, old_value, new_value):  # write only if unchanged
            return new_value
        # CAS failed — another thread modified the counter. Retry.
```

CAS ensures that no update is lost, even when multiple threads concurrently try to increment. If Thread A's CAS fails (because Thread B already incremented), Thread A simply retries with the new value. This is *optimistic concurrency* — assume no conflicts, detect if one occurs, and retry.

**Lock-free vs. Wait-free.** A *lock-free* algorithm guarantees that at least one thread makes progress in a bounded number of steps — but individual threads may starve if they keep losing CAS races. A *wait-free* algorithm guarantees that every thread completes its operation in a bounded number of steps, regardless of what other threads do. Wait-free is stronger but harder to achieve.

In practice, lock-free data structures (like the Michael-Scott queue, the Harris-Michael linked list, and the lock-free skip list) are widely used in 2040:

- **Java's `ConcurrentLinkedQueue`** — Lock-free queue based on Michael-Scott (1996)
- **Rust's `crossbeam` crate** — Lock-free stacks, queues, and epoch-based memory reclamation
- **Go's `sync.Map`** — Lock-free read path with sharded locks on the write path
- **C++'s `concurrent_vector`** (Intel TBB) — Lock-free growth with atomic size tracking

**Memory Ordering: The Dragon at the Base of Yggdrasil.** Modern CPUs and compilers reorder memory operations for performance. A store followed by a load may execute as load-then-store. A compiler may hoist a read out of a loop. These reorderings are invisible in single-threaded code (the program behaves "as if" executed in order) but catastrophic in concurrent code (Thread A's store to `flag = true` may be visible to Thread B only after a delay, breaking invariants).

Memory ordering guarantees are expressed through *memory fences* (barriers) and *atomic operations with specified ordering*:

| Ordering | Guarantee | Cost |
|----------|-----------|------|
| Relaxed | No ordering guarantee | Free |
| Acquire | Subsequent reads/writes cannot be reordered before this operation | Low (x86: free, ARM: ~1 cycle) |
| Release | Prior reads/writes cannot be reordered after this operation | Low (x86: free, ARM: ~1 cycle) |
| AcqRel | Both acquire and release | Moderate |
| SeqCst | Totally ordered with all other SeqCst operations | High (full fence on all architectures) |

Understanding memory ordering is critical for writing correct lock-free code. A CAS operation with `Relaxed` ordering may succeed but not be visible to other threads — a subtle bug that only manifests under high concurrency on weak-memory-model architectures (ARM, RISC-V).

**Structured Concurrency: From GOTO to GOROUTINE.** The history of concurrency models mirrors the history of control flow:

- **GOTO-based concurrency** (pthreads, raw threads) — Like GOTO in control flow, raw threads offer maximum flexibility and maximum danger. Threads can access any shared data, deadlock in any order, and leak resources in any combination.
- **Shared-memory with structured synchronization** (mutexes, condition variables, read-write locks) — Like structured programming (if/while/functions), these constrain the chaos of raw threads. Easier to reason about but still error-prone.
- **Message-passing concurrency** (Go channels, Erlang actors, CSP) — Like functional programming (no shared mutable state), these eliminate shared memory entirely. Threads communicate only through messages. Simpler to reason about but potentially higher latency.
- **Structured concurrency** (Java 21 Virtual Threads, Kotlin Coroutines, Swift Structured Concurrency) — Like structured error handling (try/catch/finally), these guarantee that concurrent tasks are always properly cleaned up. A parent task cannot complete until all child tasks complete or are cancelled.

The 2040 consensus is moving toward structured concurrency as the default model. Go's goroutines remain popular for simple cases, but the discipline of structured concurrency — where a concurrent scope is analogous to a block scope — provides better error handling, cleaner cancellation, and stronger guarantees about resource cleanup.

#### Required Reading

- Herlihy, M., & Shavit, N. (2012). *The Art of Multiprocessor Programming* (Revised 1st ed.). Morgan Kaufmann. Chapters 1-5.
- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapters 6-7: "Concurrent Hooves" and "The Lock-Free Path."
- Michael, M. M., & Scott, M. L. (1996). "Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms." *PODC '96*.
- Pressler, R. (2039). *Structured Concurrency in Practice*. Addison-Wesley. Chapters 1-3.

#### Discussion Questions

1. Lock-free data structures avoid blocking but require retry loops (CAS loops). Under high contention, a lock-free queue may require many retries before a CAS succeeds. Is lock-free always better than mutex-based? When is a simple mutex preferable?
2. Memory ordering on ARM (the dominant architecture in 2040 server infrastructure) is weaker than on x86. Code that works perfectly on x86 may fail on ARM due to memory reordering. How should the performance engineer test for these bugs?
3. Structured concurrency promises to make concurrent programming as safe as structured programming made control flow. History suggests that every "safe by default" model has escape hatches (GOTO survives in C; raw threads survive in Java). What will the escape hatches for structured concurrency look like?

---

### ᚲ Lecture 6: The River of Élivágar — I/O Optimization & Data Flow

**Date:** Week 3, Session 2

#### Overview

Élivágar, the eleven icy rivers that flow from Hvergelmir, the roaring wellspring at the root of Yggdrasil, represent the flow of data through a system. Like those rivers, data flows through multiple channels — disk, network, memory bus — and like those rivers, the flow can be blocked by ice (bottlenecks), overflow its banks (buffer bloat), or freeze solid (deadlocks). This lecture covers I/O optimization: how to move data efficiently through the system, from file I/O to network I/O to the data pipeline patterns that connect them.

#### Lecture Notes

**The I/O Bottleneck: Why Data Movement Dominates.** In modern software, I/O is almost always the bottleneck. A CPU that executes 4 billion operations per second spends most of its time waiting for data to arrive. The hierarchy of I/O latency makes this clear:

| Operation | Latency | CPU Cycles |
|-----------|---------|------------|
| L1 Cache access | ~1ns | 4 |
| L2 Cache access | ~3ns | 12 |
| L3 Cache access | ~10ns | 40 |
| DRAM access | ~100ns | 400 |
| NVMe SSD 4K read | ~5μs | 20,000 |
| NVMe SSD sequential 1MB | ~50μs | 200,000 |
| Network (same datacenter) | ~500μs | 2,000,000 |
| Network (cross-region) | ~50ms | 200,000,000 |
| Network (cross-continent) | ~150ms | 600,000,000 |

A CPU could execute 600 million instructions in the time it takes a single cross-continent network request to complete. This means the performance engineer's primary task in I/O-heavy systems is: *reduce, overlap, and pipeline*.

**The Three Strategies of I/O Optimization.**

1. **Reduce** — Eliminate unnecessary I/O. Cache frequently accessed data. Compress data before transmission. Batch multiple small operations into fewer large ones. Filter data at the source (push predicates to the database) rather than the destination (load all data then filter in application code).

2. **Overlap** — Perform computation while waiting for I/O. Asynchronous I/O (async I/O, io_uring, epoll) allows the CPU to continue executing useful work while data transfers happen in the background. This is the fundamental insight behind event-driven architectures (Node.js, Nginx) and async/await patterns (Python asyncio, Rust tokio, C# async/await).

3. **Pipeline** — Start processing data before all of it has arrived. Streaming processing (Kafka, Flink, Spark Streaming) applies computations to data as it flows through the pipeline, reducing end-to-end latency from minutes to milliseconds.

**Buffering: The Reservoir at the Source.** Every I/O system uses buffers — temporary storage that smooths out the bursty nature of data production and consumption. The key design decisions for buffering are:

- **Buffer size.** Too small → frequent system calls and context switches. Too large → memory waste and increased latency (data sits in the buffer waiting for it to fill). The optimal buffer size is typically a small multiple of the page size (4KB) for file I/O and a multiple of the network MTU (1500 bytes) for network I/O.
- **Buffer count.** Single buffering (read into one buffer, process, repeat) is simple but blocks. Double buffering (read into buffer A while processing buffer B, then swap) overlaps I/O and computation. Ring buffers (circular arrays with read/write pointers) generalize double buffering to arbitrary sizes.
- **Backpressure.** When the consumer can't keep up with the producer, the buffer fills. Without backpressure, the buffer overflows and data is lost. With backpressure, the producer is signaled to slow down. Reactive Streams (Java), asyncio (Python), and the RúnarNet pipeline all implement backpressure as a core mechanism.

**Zero-Copy I/O: The Data That Never Stops.** The most expensive I/O operation in traditional systems is not the data transfer itself — it's the copying. A traditional web server serving a file performs four copies:

1. Kernel reads data from disk into kernel buffer (DMA transfer)
2. Kernel copies data from kernel buffer to user-space buffer (CPU copy)
3. User-space processes data, then copies it back to kernel socket buffer (CPU copy)
4. Kernel sends data from socket buffer to network card (DMA transfer)

Two of those four copies are unnecessary. Zero-copy I/O eliminates them:

- `sendfile()` (Linux) — Transfers data directly from a file descriptor to a socket, without copying through user space. Used by Nginx, Kafka, and most high-performance file servers.
- `splice()` (Linux) — Moves data between two file descriptors (not necessarily a file and a socket) without copying through user space.
- `io_uring` (Linux 5.1+) — A modern async I/O interface that supports zero-copy operations and submission queue batching. The 2040 standard for high-performance I/O on Linux.
- `mmap()` — Maps a file directly into the process's address space, allowing the CPU to access file data as if it were memory. The kernel handles paging transparently. Used by databases, memory-mapped file formats, and the SleipnirProf analytics backend.

**I/O Schedulers: Prioritizing the Flow.** When multiple I/O operations are pending, the kernel must decide which to service first. The I/O scheduler (also called the I/O elevator) controls this ordering:

- **CFQ (Completely Fair Queuing)** — The traditional Linux scheduler. Assigns time slices to each process, ensuring fair I/O access. Good for multi-user systems, suboptimal for databases and latency-sensitive workloads.
- **Deadline** — Services I/O within a guaranteed deadline. Read operations get a shorter deadline than writes (because applications typically block on reads, not writes). Good for database workloads.
- **NOOP** — A simple FIFO queue with only request merging. Optimal for devices with their own scheduling intelligence (NVMe SSDs, hardware RAID controllers).
- **mq-deadline** — The 2040 Linux default for NVMe. Multiqueue variant of deadline scheduler. Handles the high queue depths of modern NVMe devices efficiently.

The performance engineer must select the right I/O scheduler for the workload. A database on a spinning HDD needs `deadline`. A web server on NVMe needs `mq-deadline` or `none`. A virtual machine with a hardware RAID needs `none` (the RAID controller handles scheduling).

**Data Serialization: The Format of the Flow.** Data that moves between processes, machines, or storage must be serialized — converted from in-memory representation to a byte stream. The serialization format affects both throughput and latency:

| Format | Schema | Speed | Size | Schema Evolution |
|--------|--------|-------|------|-----------------|
| JSON | None | Slow | Large (text) | Ad hoc |
| MessagePack | None | Moderate | Moderate | Ad hoc |
| Protocol Buffers | Required | Fast | Small (binary) | Formal |
| FlatBuffers | Required | Very fast | Small (zero-copy) | Formal |
| Cap'n Proto | Required | Very fast | Small (zero-copy) | Formal |

In 2040, Protocol Buffers remain the workhorse of serialized data (used by gRPC, Kubernetes, and most internal microservice APIs), while Cap'n Proto and FlatBuffers dominate performance-critical paths where zero-copy deserialization matters. JSON persists for human-facing APIs and configuration files, but its overhead (5-10× larger than binary formats, 10-100× slower to parse) makes it unacceptable for high-throughput data pipelines.

The performance engineer selects serialization formats based on the data access pattern:

- **Full parse, full use** → Protocol Buffers or MessagePack (compact, fast enough)
- **Full parse, partial use** → FlatBuffers or Cap'n Proto (zero-copy, access only needed fields)
- **Stream processing** → Apache Avro or Protobuf with size-delimited framing (schema-aware streaming)
- **Human-facing APIs** → JSON with optional HTTP compression (gzip/brotli)

#### Required Reading

- Gregg, B. (2021). *Systems Performance* (2nd ed.). Chapters 10-11 (File Systems, Disk I/O).
- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 8: "The River of Data."
- Kleen, A. (2019). "io_uring: Linux's New Async I/O Interface." *Linux Plumbers Conference*.
- Katz, H. (2019). *Kafka: The Definitive Guide* (2nd ed.). O'Reilly. Chapters 1-3.

#### Discussion Questions

1. Zero-copy I/O eliminates CPU overhead but bypasses the kernel's security checks (no validation of the data being transferred). Under what circumstances is this tradeoff unacceptable? What are the security implications?
2. Backpressure in a streaming pipeline prevents the consumer from being overwhelmed. But what happens to backpressure in a system with multiple consumers at different speeds? Should the pipeline slow to the slowest consumer?
3. You're designing a real-time analytics pipeline that processes 10 million events per second. The current serialization format is JSON (overhead: 5× size, 100× parse time). Switching to Protocol Buffers would reduce size by 80% and parse time by 95%. What are the migration risks, and how would you manage them?

---

### ᚷ Lecture 7: The Query Rune — Database Performance & Query Optimization

**Date:** Week 4, Session 1

#### Overview

The runic inscriptions of the Viking Age stored information in compact, efficient forms — what算是 optimal information density carved into stone. Modern databases face the same challenge: storing and retrieving information with minimal waste. This lecture covers database performance from the query planner's perspective — how databases execute queries, how to read and interpret execution plans, and how to write queries that the planner can optimize effectively.

#### Lecture Notes

**The Query Lifecycle: From SQL to Result.** When a client sends a SQL query to a database, the query passes through several stages before data is returned:

1. **Parsing** — The query text is parsed into an abstract syntax tree (AST). Syntax errors are caught here. Cost: negligible.
2. **Rewriting** — The AST is transformed by rule-based rewrites. Views are expanded, subqueries are flattened, constraint exclusions are applied. Cost: negligible.
3. **Planning** — The query planner examines the AST and generates multiple possible execution plans, estimates the cost of each (using table statistics), and selects the cheapest plan. Cost: moderate (can be significant for complex queries with many join orders).
4. **Execution** — The selected plan is executed, reading data from disk or cache, applying filters, joining tables, aggregating results, and returning them to the client. Cost: dominant (this is where the work happens).

The performance engineer can influence stages 3 and 4. Stage 3 (planning) is influenced by table statistics, configuration parameters, and query structure. Stage 4 (execution) is influenced by indexes, table partitioning, and hardware configuration.

**The Query Planner: The Norn Who Weighs All Paths.** The query planner is like the Norn Urðr, who weighs the past to determine the future. It examines statistics (the past) to estimate the cost of each execution plan (the future) and selects the cheapest one. But like any oracle, the planner's accuracy depends on the quality of its inputs.

The planner's primary inputs are *table statistics* — metadata about the content of each table:

- **Row count estimates** — How many rows the table contains (updated by `ANALYZE`)
- **Column cardinality** — How many distinct values each column contains
- **Most common values** — The most frequent values in each column (the MCV list)
- **Column correlation** — How correlated the physical row order is with the column sort order (affects index scan efficiency)
- **Histogram bounds** — The distribution of values across equal-frequency buckets

When statistics are stale (e.g., after a bulk `INSERT` that hasn't been `ANALYZE`d), the planner's cost estimates can be wildly wrong, leading to catastrophically bad plans. The classic example: a table with 10 rows where the planner thinks there are 10 million rows, leading it to choose a sequential scan when an index scan would be 1000× faster.

**Indexes: The Rune That Points the Way.** An index is a secondary data structure that allows the database to find rows without scanning the entire table. The fundamental index types are:

| Index Type | Best For | Tradeoff |
|------------|----------|----------|
| B-tree | Equality and range queries, sorted results | General-purpose; moderate write overhead |
| Hash | Equality only (no range) | Fast equality; no ordering; limited use |
| GiST | Geospatial, full-text, custom data types | Flexible; moderate performance |
| GIN | Multi-element values (arrays, full-text, JSON) | Fast lookup; expensive to build and update |
| BRIN | Very large tables with natural physical ordering | Tiny size; very approximate filtering |
| Partial | Queries that always filter on a specific condition | Smaller than full index; only helps specific queries |
| Covering | Queries that need columns not in the WHERE clause | Includes all needed columns; eliminates table lookups |

The performance engineer's index strategy should follow these principles:

1. **Index for selective queries.** An index on a column with 2 distinct values (e.g., `is_active`) helps marginally. An index on a column with 10,000 distinct values (e.g., `email`) helps enormously.
2. **Use composite indexes for multi-column queries.** A query filtering on `(user_id, created_at)` benefits from a composite index on both columns, not two separate indexes.
3. **Include columns for covering indexes.** If a query filters on `user_id` but selects `name` and `email`, a covering index on `(user_id) INCLUDE (name, email)` satisfies the entire query from the index, eliminating the table lookup.
4. **Don't over-index.** Every index slows down writes (INSERT, UPDATE, DELETE) because the index must be updated. A table with 20 indexes can have write throughput 5-10× lower than a table with 5 indexes.

**The EXPLAIN Command: Reading the Oracle's Prophecy.** `EXPLAIN ANALYZE` is the performance engineer's most important SQL tool. It shows the actual execution plan chosen by the planner, the estimated vs. actual row counts, and the time spent at each node. The key things to look for:

- **Seq Scan on large table** → Missing or ineffective index. The planner chose to scan the entire table instead of using an index. Usually a sign that the query needs a better index or the statistics are stale.
- **Nested Loop with high row estimates** → A join strategy that works well for small result sets but catastrophically badly for large ones. If the planner estimates 10 rows but the actual count is 10,000, the nested loop will be very slow.
- **Filter with high rows removed** → A condition that's being applied after the table scan instead of during it. This means the planner couldn't push the filter down into the index — usually because the index doesn't cover the filter column.
- **Sort with high row count** → The query requires sorting a large result set. Consider adding an ORDER BY-compatible index or restructuring the query to avoid sorting.

**Query Anti-Patterns: The Performance Engineer's Hit List.** The following query patterns are almost always slow and should be refactored:

1. **SELECT *** — Retrieves all columns when only a few are needed. Wastes bandwidth, memory, and prevents covering index optimization.
2. **OR in WHERE clause** — Often prevents index use. Refactor as UNION ALL or use a composite condition.
3. **Leading wildcard LIKE '%pattern'** — Prevents B-tree index use. Use full-text search (GIN index with tsvector) instead.
4. **Functions on indexed columns** — `WHERE LOWER(email) = 'x'` prevents index use on `email`. Use a functional index or store the lowered value separately.
5. **Implicit type coercion** — `WHERE varchar_column = 123` coerces the integer to varchar, preventing index use. Always use the correct type.
6. **Correlated subqueries** — A subquery that references the outer query and is executed once per outer row. Refactor as a JOIN or CTE.
7. **N+1 queries** — Fetching 1000 rows in one query, then issuing 1000 separate queries for related data. Refactor as a single JOIN or use `WHERE id IN (...)`.

**Database Architecture: OLTP vs. OLAP vs. HTAP.** The workload determines the architecture:

- **OLTP (Online Transaction Processing)** — High volume of short transactions (reads and writes). Optimized for row-based access, low latency, and ACID compliance. PostgreSQL, MySQL.
- **OLAP (Online Analytical Processing)** — Low volume of complex analytical queries over large datasets. Optimized for columnar storage, parallel scan, and aggregation. ClickHouse, Apache Druid, DuckDB.
- **HTAP (Hybrid Transactional/Analytical Processing)** — Attempts to serve both OLTP and OLAP from the same database. In 2040, SingleStore, TiDB, and PostgreSQL with columnar extensions achieve credible HTAP performance.

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 9: "The Runic Query."
- PostgreSQL Documentation (2040). *Query Planning*, Chapters 1-3. https://www.postgresql.org/docs/current/queries.html
- Taft, R., et al. (2020). "TiDB: A Raft-based HTAP Database." *Proceedings of the VLDB Endowment*, 13(12), 3072-3084.
- Dageville, B., et al. (2016). "The Snowflake Elastic Data Warehouse." *SIGMOD '16*.

#### Discussion Questions

1. The query planner uses statistics to estimate costs. What happens when the statistics are wrong? How can the performance engineer detect and fix stale statistics before they cause production incidents?
2. A covering index includes all columns needed by the query, eliminating the table lookup entirely. But covering indexes increase write overhead and storage. How do you decide when a covering index is worth the cost?
3. HTAP databases promise to serve both OLTP and OLAP from the same data store. What are the fundamental conflicts between these workloads, and how do HTAP databases resolve them?

---

### ᚹ Lecture 8: The Web of Víðarr — Network Performance & Distributed Systems

**Date:** Week 4, Session 2

#### Overview

Víðarr, the silent god whose strength surpasses all others, represents the power that holds the network together — the infrastructure that must bear immense loads without breaking. Network performance in distributed systems is the Víðarr of the software world: invisible when it works, catastrophic when it fails. This lecture covers network protocols, TCP optimization, HTTP/2 and HTTP/3, distributed systems performance, and the fundamental limits of the speed of light.

#### Lecture Notes

**The Speed of Light: The Universe's Hard Limit.** Information cannot travel faster than light — approximately 300,000 km/s in vacuum, roughly 200,000 km/s in fiber optic cable (due to the refractive index). This means:

- New York to London (~5,600 km): minimum one-way latency = 28ms
- New York to Tokyo (~10,800 km): minimum one-way latency = 54ms
- Opposite sides of Earth (~20,000 km): minimum one-way latency = 100ms

These are *physical* limits. No amount of software optimization can make a signal travel faster than light. The performance engineer's response is to minimize the number of round trips (each round trip doubles the latency) and to place computation close to the data (edge computing, CDN caching).

**TCP Optimization: Tuning the Longship's Rigging.** TCP is the dominant transport protocol for reliable data delivery. Its congestion control algorithms (Cubic, BBR) are designed to share bandwidth fairly across competing flows. But TCP's reliability guarantees come at a performance cost:

- **Three-way handshake** — Every new TCP connection requires 1.5 round trips (SYN, SYN-ACK, ACK) before data can be sent. For short-lived connections (typical HTTP requests before Keep-Alive), the handshake overhead dominates.
- **Slow start** — TCP starts with a small congestion window (10 segments in modern Linux) and doubles it each round trip. A 100KB response requires ~7 round trips to transfer on a fresh connection with slow start, even if the bandwidth could deliver it in 1 round trip.
- **Head-of-line blocking** — If a single packet is lost, TCP blocks all subsequent data until the lost packet is retransmitted. On a connection with 0.1% packet loss, this can reduce throughput by 30-50%.

Key TCP optimizations for the performance engineer:

- **Connection pooling and keep-alive** — Reuse existing TCP connections instead of creating new ones. Eliminates handshake overhead and avoids slow start.
- **TCP Fast Open (TFO)** — Allows data to be sent in the SYN packet (the first round trip), reducing connection setup to 1 round trip for resumed connections. Supported on Linux, macOS, and most modern servers.
- **Congestion control selection** — Cubic (default on Linux) is designed for fair bandwidth sharing. BBR (developed by Google) is designed for high-bandwidth, high-latency connections and can achieve 5-100× better throughput on long-distance links with packet loss.
- **Traffic classification** — Use DiffServ or ECN to mark traffic by priority. Time-sensitive traffic (VoIP, video, financial data) gets preferential queuing in network devices.

**HTTP/2 and HTTP/3: The Next Rivers.** HTTP/2 (2015) and HTTP/3 (2022) represent fundamental advances in network protocol efficiency:

**HTTP/2** introduced multiplexing — multiple streams over a single TCP connection, eliminating the need for multiple parallel connections. This reduces connection overhead but introduces HTTP/2's own head-of-line problem: TCP sees only one byte stream, so a lost packet blocks *all* HTTP/2 streams until the packet is retransmitted.

**HTTP/3** solves this by replacing TCP with QUIC — a UDP-based protocol that implements multiplexed streams with independent delivery guarantees. A lost packet on stream 3 does not block streams 1, 2, and 4. QUIC also eliminates the TCP handshake (QUIC connections are established in 1 round trip, or 0 round trips for resumed connections), reducing connection latency.

In 2040, HTTP/3 is the default for all major browsers and most server frameworks. The University's RúnarNet uses HTTP/3 exclusively for client-facing APIs, achieving 20-30% lower latency than HTTP/2 for mobile clients on lossy networks.

**Distributed Systems Performance: Fallacies and Realities.** Distributed systems add network latency to every operation. A single microservice call that takes 1ms locally takes 3-5ms over a local network, 50-100ms across regions, and 200-500ms across continents. The distributed systems engineer must minimize cross-service calls, batch remote operations, and cache aggressively.

The *Fallacies of Distributed Computing* (first articulated by Peter Deutsch in 1994, still relevant in 2040):

1. The network is reliable
2. Latency is zero
3. Bandwidth is infinite
4. The network is secure
5. Topology doesn't change
6. There is one administrator
7. Transport cost is zero
8. The network is homogeneous

Every one of these assumptions is false. A performance engineer who designs a system assuming any of them will create a system that fails in production.

**Service Mesh Performance: The Bifrǫst Between Services.** A service mesh (Istio, Linkerd, Consoul Connect) provides observability, traffic management, and security for microservice communication. But it adds latency — typically 1-5ms per hop for sidecar-based meshes (Envoy) and 0.1-0.5ms per hop for kernel-based meshes (Cilium, built on eBPF).

In 2040, the RúnarNet uses Cilium as its service mesh, achieving sub-millisecond sidecar latency through eBPF-based networking that bypasses the userspace proxy entirely. This represents a 10× latency improvement over Envoy-based meshes for inter-service communication.

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 10: "The Web of the Silent God."
- Gregg, B. (2021). *Systems Performance* (2nd ed.). Chapters 11-13 (Network, TCP, HTTP).
- Iyengar, J., & Thomson, M. (2021). "QUIC: A UDP-Based Multiplexed and Secure Transport." *RFC 9000*.
- Burnett, D., & Rizzo, J. (2039). *Service Mesh Performance: eBPF and Beyond*. O'Reilly. Chapters 2-4.

#### Discussion Questions

1. The speed of light imposes a hard minimum on latency. A financial trading firm places servers in the same building as the exchange to minimize latency. What are the equity implications of performance optimization — is it fair that firms with more resources can afford lower latency?
2. HTTP/3 eliminates TCP head-of-line blocking by using QUIC's independent streams. But QUIC runs over UDP, which some firewalls block. How should organizations manage the transition from HTTP/2 to HTTP/3?
3. The Fallacies of Distributed Computing were articulated in 1994. Are they all still relevant in 2040? Can you think of a fallacy that has been partially or fully resolved by technology advancement?

---

### ᚺ Lecture 9: The Rendering of Bifrǫst — Frontend & Web Performance

**Date:** Week 5, Session 1

#### Overview

Bifrǫst, the shimmering rainbow bridge that connects Midgard to Ásgarðr, is the user's experience of the system — the visible surface that must be fast, smooth, and delightful. No matter how optimized the backend, if the frontend is slow, the user perceives the entire system as slow. This lecture covers the full performance stack of web and application frontends: critical rendering path optimization, JavaScript bundle management, image and media optimization, layout stability, and the Core Web Vitals that define frontend performance in 2040.

#### Lecture Notes

**The Critical Rendering Path: From Bytes to Pixels.** When a browser loads a web page, it follows a fixed sequence of steps before anything appears on screen:

1. **HTML parsing** → Construct the DOM (Document Object Model)
2. **CSS parsing** → Construct the CSSOM (CSS Object Model)
3. **DOM + CSSOM** → Construct the render tree (visible nodes with styles)
4. **Layout** → Calculate the position and size of each element
5. **Paint** → Fill pixels (colors, images, borders, text)
6. **Composite** → Combine layers (transform, opacity) for final display

Each step depends on the previous step being complete. A blocked step blocks all subsequent steps. The performance engineer's goal is to unblock this path as early as possible:

- **Inline critical CSS** — The CSS needed for above-the-fold content should be inlined in the `<head>` tag, avoiding an additional network request that blocks rendering.
- **Defer non-critical CSS and JavaScript** — `<script async>` and `<script defer>` prevent JavaScript from blocking HTML parsing. Non-critical CSS can be loaded with `media="print"` and switched to `media="all"` after the page loads.
- **Reduce DOM complexity** — A simpler DOM (fewer nodes, fewer nested elements) renders faster. Virtual DOM frameworks (React, Vue) add overhead; server-side rendering (SSR) or static site generation (SSG) sends pre-rendered HTML that displays immediately.

**JavaScript Bundle Management: The Weight of the Ship's Cargo.** JavaScript is the heaviest part of most web pages. In 2040, the median web page ships 800KB of compressed JavaScript (2.5MB uncompressed), which must be downloaded, parsed, compiled, and executed before the page is interactive. The performance impact is severe:

- **Parse time** — V8's parser processes approximately 30MB/s of JavaScript on a modern device. A 2.5MB uncompressed bundle takes ~80ms just to parse.
- **Compile time** — V8's TurboFan compiler optimizes hot code after multiple executions, but the initial "baseline" compilation still takes time.
- **Execution time** — JavaScript runs on the main thread, blocking all user interaction (clicks, scrolls, keyboard events).

The performance engineer's toolkit for JavaScript optimization:

1. **Code splitting** — Load only the JavaScript needed for the current page. Dynamic imports (`import()`) and route-based splitting ensure the user downloads only what they need.
2. **Tree shaking** — Eliminate dead code from the bundle. ES modules enable static analysis that determines which exports are actually used. Webpack, Rollup, and esbuild all support tree shaking.
3. **Minification and compression** — Terser, esbuild, and SWC reduce JavaScript size by 20-30% through variable shortening, dead code elimination, and whitespace removal. Brotli compression reduces the minified output by another 60-70%.
4. **Lazy loading** — Defer loading of below-the-fold content (images, videos, non-critical JavaScript) until needed. `loading="lazy"` for images and `import()` for JavaScript modules.
5. **Web Workers** — Move expensive computation off the main thread onto a background worker. Communication via `postMessage()` adds latency (~1ms per message) but frees the main thread for user interaction.

**Core Web Vitals: The Three Pillars of User Experience.** Google's Core Web Vitals (CWV) are the primary metrics for frontend performance in 2040:

| Metric | What It Measures | Good | Needs Improvement | Poor |
|--------|-----------------|------|-------------------|------|
| LCP (Largest Contentful Paint) | Loading performance | ≤2.5s | 2.5-4.0s | >4.0s |
| INP (Interaction to Next Paint) | Interactivity | ≤200ms | 200-500ms | >500ms |
| CLS (Cumulative Layout Shift) | Visual stability | ≤0.1 | 0.1-0.25 | >0.25 |

**LCP** measures when the largest visible element (hero image, heading, video) finishes rendering. This is the moment the user perceives the page as "loaded." Key optimizations: preloaded hero images, inlined critical CSS, server-side rendering for initial content.

**INP** (replaced FID in March 2024) measures the latency between user interaction (click, key press) and the next visual update. A high INP means the page feels sluggish — the user clicks a button and nothing happens for 200ms+. Key optimizations: main thread unblocking (Web Workers, `requestIdleCallback`), debouncing event handlers, and deferring non-critical JavaScript.

**CLS** measures visual stability — whether elements on the page shift position as it loads. A high CLS means buttons move, text jumps, and the user misclicks. Key optimizations: explicit dimensions for images and videos (`width` and `height` attributes), `aspect-ratio` CSS property, font `font-display: swap` with `size-adjust` to match fallback and web fonts.

**Image and Media Optimization: The Visual Cargo.** Images and video account for 60-80% of most web pages' total bytes. Optimization strategies:

- **Format selection** — WebP (2010) and AVIF (2019) provide 25-50% better compression than JPEG at equivalent quality. In 2040, AVIF is the default for lossy images; WebP is the fallback for browsers that don't support AVIF.
- **Responsive images** — Serve different image sizes based on viewport width using `srcset` and `sizes`. A 4K desktop monitor doesn't need a 1920px image; a phone doesn't need a 4K image.
- **Progressive loading** — Low Quality Image Placeholders (LQIP) and blur-up techniques show a tiny (10×10 pixel) blurred version of the image immediately, then replace it with the full image when it loads. The user sees content instantly instead of staring at blank space.
- **Video optimization** — Use `<video autoplay muted loop playsinline>` for hero videos (short, muted, autoplaying loops). Compress with x264 for compatibility or AV1 for maximum compression. Provide poster images for fallback.

**The 2040 Frontend Stack at University of Yggdrasil.** The RúnarNet platform's frontend architecture:

- **Framework:** Remix (React-based SSR with progressive enhancement)
- **Build tool:** Vite 7 with SWC compilation
- **Styling:** Tailwind CSS 5 with Just-in-Time compilation
- **State management:** TanStack Query for server state, Zustand for client state
- **Performance budget:** 150KB JS compressed, 300KB total compressed, LCP < 1.5s, INP < 100ms, CLS < 0.05
- **Monitoring:** SleipnirProf Web Vitals dashboard with real-user monitoring

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 11: "The Rainbow Rendering Path."
- Hume, H., & Meenan, N. (2039). *Web Performance in Action* (2nd ed.). Manning. Chapters 2-5.
- Google Web Dev Team (2040). *Core Web Vitals*. https://web.dev/vitals/
- Osmani, A. (2020). "The Cost of JavaScript." *Web.dev*. [Updated 2040 edition available at web.dev/cost-of-javascript-2040.]

#### Discussion Questions

1. A typical web page in 2040 ships 2.5MB of JavaScript. Is this a fundamental consequence of rich web applications, or a failure of engineering discipline? What would a "zero JavaScript" web application look like, and could it deliver a comparable user experience?
2. INP measures the latency between user interaction and visual update. But some interactions (form validation, complex calculations) inherently take time. How should the performance engineer distinguish between "slow because the code is bloated" and "slow because the computation is genuinely complex"?
3. Progressive image loading (LQIP, blur-up) gives the user instant visual feedback, but the actual image load time is unchanged. Is this a genuine performance improvement or an illusion? Discuss the difference between objective performance metrics and subjective user experience.

---

### ᚾ Lecture 10: Continuous Vigilance — Performance Monitoring, Observability & Continuous Optimization

**Date:** Week 5, Session 2

#### Overview

The performance engineer's work does not end when the system ships. Like Heimdallr watching the Bifrǫst bridge for signs of trouble, the performance engineer must maintain continuous vigilance — monitoring the system in production, detecting regressions before users notice, and iterating on optimizations over time. This lecture covers the three pillars of observability (metrics, logs, traces), performance monitoring architecture, SLO-based alerting, and the practice of continuous performance optimization.

#### Lecture Notes

**Observability: Seeing the Unseen.** The term "observability" comes from control theory — a system is observable if its internal state can be inferred from its external outputs. In software, observability means being able to understand what the system is doing *without* modifying it, just by observing its outputs.

The three pillars of observability in 2040:

1. **Metrics** — Numeric time-series data: request rate, error rate, latency percentiles, CPU utilization, memory usage. Collected at high frequency (1-60 second intervals) and stored in time-series databases (Prometheus, VictoriaMetrics, InfluxDB). Metrics answer "what is happening right now" and "what happened over time."

2. **Logs** — Discrete events: error messages, access logs, audit trails, application events. Collected in structured format (JSON, Logfmt) and stored in log aggregation systems (Loki, Elasticsearch, CloudWatch Logs). Logs answer "what happened in this specific request" and "why did this error occur."

3. **Traces** — Distributed request journeys: the path a single request takes through the system, with timing at each hop. Collected via instrumentation (OpenTelemetry) and stored in trace backends (Jaeger, Zipkin, SleipnirProf). Traces answer "where is the time going" and "which service is slow."

The key insight: metrics tell you *that* there's a problem, logs tell you *what* the problem is, and traces tell you *where* the problem is. All three are necessary for effective performance engineering.

**Metrics: The Pulse of the System.** The RED method (Request rate, Error rate, Duration) defines the essential metrics for any service:

- **Request rate** — How many requests per second is the service handling? Sudden spikes indicate load events; sudden drops indicate outages or upstream failures.
- **Error rate** — What percentage of requests return errors? Track 4xx (client errors) and 5xx (server errors) separately. A rise in 5xx is an emergency; a rise in 4xx may be a bad deployment or a broken client.
- **Duration (latency)** — What is the distribution of request durations? Always report percentiles (P50, P90, P95, P99), never just averages. A P99 latency of 5s with a P50 of 50ms means 1% of users are experiencing catastrophic slowness — information that a 100ms average completely hides.

The USE method (Utilization, Saturation, Errors) defines the essential metrics for any resource (CPU, memory, disk, network):

- **Utilization** — What percentage of the resource is in use? 80%+ CPU utilization is a warning sign; 90%+ is an emergency.
- **Saturation** — How much work is queued waiting for the resource? A non-zero saturation means the resource is a bottleneck.
- **Errors** — How many errors is the resource producing? Disk I/O errors, packet drops, memory allocation failures.

**SLO-Based Alerting: Signal, Not Noise.** Traditional alerting thresholds (alert when CPU > 80%, alert when latency > 500ms) generate enormous noise. Most alerts fire and resolve before anyone can respond. Many alerts are irrelevant — the CPU is at 85% because it's doing useful work, not because there's a problem.

SLO-based alerting (Service Level Objectives) flips this approach. Instead of alerting on individual metric thresholds, the alerting system tracks whether the service is meeting its SLO over a time window. An SLO is expressed as a target: "99.9% of requests complete within 200ms over a rolling 30-day window."

SLO-based alerting fires when the *error budget* is in danger of being exhausted. If the SLO allows 0.1% of requests to violate the latency target, the error budget is 0.1% × total_requests. An alert fires when the remaining error budget is low (e.g., when 14.4% of the 30-day error budget has been consumed in the past 3 days), not when any individual request is slow.

This approach dramatically reduces alert noise while ensuring that genuine performance regressions are caught early. The University's RúnarNet uses SLO-based alerting exclusively — no individual threshold alerts, only error budget alerts.

**Continuous Benchmarking: CI/CD for Performance.** Just as CI/CD pipelines run tests on every commit, continuous benchmarking pipelines run performance benchmarks on every commit. The architecture:

1. **Commit hook** — Every push to the main branch triggers a benchmark run.
2. **Benchmark execution** — The CI system runs a standardized benchmark suite against the current codebase and the baseline (previous commit or tagged release).
3. **Comparison** — The benchmark framework compares the current results against the baseline. Any regression above the noise threshold (typically 3-5%) is flagged.
4. **Alert** — If a regression is detected, a notification is sent to the commit author and the performance engineering team.

The University's SleipnirProf CI integration uses this approach with one important addition: AI-driven regression analysis. When a benchmark regresses, the system analyzes the commit that caused the regression, identifies the likely culprit (using `git blame` and code diff analysis), and suggests a root cause. This reduces the average time-to-fix for performance regressions from 2-3 days to 4-6 hours.

**Capacity Planning: Knowing When the Ship Needs More Sailors.** Performance monitoring isn't just about finding problems — it's about predicting future needs. Capacity planning answers the question: "Given current growth rates, when will we need more hardware?"

The key technique is *linear extrapolation of resource utilization trends*. If CPU utilization is growing at 5% per month and the target utilization ceiling is 75%, the capacity planning system calculates the month when utilization will cross the ceiling and schedules a scaling event before that date.

More sophisticated approaches account for seasonal patterns (end-of-semester load spikes on the RúnarNet are 3-4× baseline), traffic growth rate changes (a viral product launch can 10× traffic in a week), and the nonlinear relationship between utilization and latency (an M/M/1 queue's latency = 1/(1-ρ), where ρ is utilization — latency doubles at 50% utilization and explodes at 90%+).

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 12: "Continuous Vigilance."
- Gregg, B. (2021). *Systems Performance* (2nd ed.). Chapters 17-18 (Observability, Performance Monitoring).
- Sloss, B., et al. (2023). *Site Reliability Engineering* (2nd ed.). O'Reilly. Chapters 4-5 (Service Level Objectives, Alerting on SLOs).
- Sigelman, B., et al. (2020). *Observability Engineering*. O'Reilly. Chapters 1-3.

#### Discussion Questions

1. SLO-based alerting reduces alert noise but introduces a new challenge: defining the right SLOs. How should a team determine the latency percentile (P95? P99? P99.9%) and the time window (7 days? 30 days?) for each SLO? What are the tradeoffs?
2. Continuous benchmarking in CI/CD catches performance regressions before they reach production, but benchmarks are synthetic workloads that may not represent production behavior. How can the performance engineer ensure that benchmarks are representative of real traffic patterns?
3. The error budget for an SLO of 99.9% uptime over 30 days is approximately 43 minutes. If a single incident consumes 30 minutes of that budget, the team has only 13 minutes of budget remaining for the rest of the month. Is this model too punitive? How should teams balance reliability investment against feature velocity?

---

### ᛁ Lecture 11: The Sustainability of Jǫrð — Green Computing, Energy Efficiency & Ethical Performance

**Date:** Week 6, Session 1

#### Overview

Jǫrð, the personification of the earth itself, reminds us that performance is not just about speed — it is about stewardship. The fastest code that burns the most energy is not performant; it is wasteful. In 2040, data centers consume approximately 4% of global electricity and produce 2% of global CO₂ emissions. This lecture covers the intersection of performance engineering and environmental sustainability: energy-aware computing, carbon-aware scheduling, hardware efficiency metrics, and the ethical dimensions of performance optimization that externalizes costs to the planet.

#### Lecture Notes

**The Energy Cost of Computation.** Every computation has an energy cost. A single Google search consumes approximately 0.3 watt-hours of electricity — trivial in isolation, but multiplied by 8.5 billion searches per day, that's 2.55 GWh/day, enough to power a small city. Training a single large language model in 2040 consumes 500-2,000 MWh — equivalent to the annual electricity consumption of 50-200 homes.

The components of a server's power consumption:

| Component | % of Total Power | Optimization Lever |
|-----------|------------------|-------------------|
| CPU | 40-60% | DVFS, c-states, efficient algorithms |
| DRAM | 15-25% | Memory-efficient data structures, fewer copies |
| Network | 5-15% | Efficient protocols, compression, batching |
| Storage (SSD) | 5-10% | Write coalescing, write-ahead logging |
| Cooling | 10-20% (of facility) | Hot-aisle/cold-aisle, free cooling, liquid cooling |
| Power supply | 5-10% (loss) | High-efficiency PSUs (96%+ at full load) |

The performance engineer's job is to reduce the CPU and DRAM components — and these often align with traditional performance optimization. A faster algorithm uses less CPU time per operation. A cache-friendly data structure uses less DRAM bandwidth. A compressed network payload uses less network energy. The alignment between performance and energy efficiency is strong but not perfect: some optimizations (e.g., speculative execution, prefetching) increase energy consumption without proportionally improving performance.

**MEASURING Energy: The RAPL Interface.** Intel's Running Average Power Limit (RAPL) interface (introduced with Sandy Bridge in 2011) provides per-component energy consumption estimates at the CPU, DRAM, and package level. In 2040, RAPL is available on all major x86 processors and provides the foundation for software-level energy measurement.

ARM processors provide similar functionality through the Energy Awareness Framework (EAF) and the arm64 hardware counters. The SleipnirProf energy monitoring system uses both RAPL (for x86) and EAF (for ARM) to provide real-time energy consumption data per process, per thread, and per function call.

**Carbon-Aware Computing: Time-Shifting and Region-Shifting.** Not all energy is equal. A kilowatt-hour generated by coal produces ~1 kg of CO₂. A kilowatt-hour generated by wind or solar produces ~0 kg of CO₂. The carbon intensity of electricity varies by location (Iceland: near-zero CO₂/kWh thanks to geothermal; Poland: ~700 g CO₂/kWh from coal) and by time (solar panels produce zero electricity at night; wind turbines produce less in calm weather).

Carbon-aware computing exploits this variation:

- **Time-shifting** — Delaying batch workloads (training jobs, data processing, backups) to times when renewable energy is abundant. A training job that runs at noon in Arizona uses solar energy with near-zero carbon. The same job running at midnight uses natural gas with moderate carbon. The University's RúnarNet schedules all non-time-sensitive batch jobs using a carbon-aware scheduler that queries real-time grid carbon intensity.

- **Region-shifting** — Running compute in regions with low carbon intensity. A training job run in Iceland (geothermal) has near-zero carbon; the same job run in Virginia (mixed grid) has moderate carbon. The University's Sleipnir cloud integration routes batch jobs to the lowest-carbon region automatically.

- **Carbon-aware API throttling** — Reducing the quality of service (lower video resolution, less aggressive caching, fewer AI inference tokens) when carbon intensity is high. Services like Netflix and YouTube already adjust streaming quality based on network conditions; carbon-aware throttling adjusts based on grid conditions.

**The Performance-Energy Pareto Frontier.** Many optimizations improve both performance and energy efficiency (faster algorithms, cache-friendly data structures). But some optimizations trade one for the other:

- **Speculative execution** — Improves performance by 10-30% but increases energy consumption by 5-15% because the CPU executes instructions that are later discarded. The Spectre and Meltdown vulnerabilities (2018) were a stark reminder that speculative execution has security costs as well as energy costs.
- **Prefetching** — Reduces latency by loading data before it's needed, but wastes energy if the prefetched data is never used. On modern CPUs, hardware prefetchers typically achieve ~85% accuracy, meaning ~15% of prefetched cache lines are never accessed.
- **Compression** — Reduces data size (saving I/O and network energy) but adds CPU energy for compression and decompression. The net effect depends on the compression ratio, the CPU overhead, and the relative cost of I/O vs. CPU energy.

The performance engineer must evaluate optimizations on the Pareto frontier: finding solutions that are simultaneously fast, energy-efficient, and correct. The SleipnirProf energy module visualizes this frontier: each optimization is plotted on a graph of performance vs. energy, and the Pareto-optimal solutions form a curve. Any optimization below the curve can be improved in at least one dimension without sacrificing the other.

**Ethical Dimensions: The Externalized Cost of Speed.** When a software company optimizes for speed (lower latency, higher throughput, more features) without considering energy, it externalizes the cost of that speed to the planet. A 100ms latency improvement that increases energy consumption by 10% is not an unqualified good — it depends on who pays the energy cost, who benefits from the speed improvement, and whether the speed improvement is genuinely needed.

The concept of *sufficient performance* — performance that meets the user's needs without exceeding them — is gaining traction in 2040. The University of Yggdrasil's performance engineering guidelines include a "green review" step: before deploying a performance optimization, the team evaluates whether the optimization reduces total energy consumption. If it doesn't, the team must justify the speed improvement against the energy cost.

This is not an abstract ethical concern. The University of Yggdrasil's own RúnarNet platform processes 2.3 million requests per second. A 10ms latency improvement that increases per-request energy by 1% adds approximately 23 kW of continuous power draw — the annual energy consumption of approximately 200 homes. The carbon cost of that improvement depends on the grid's carbon intensity, but at the global average of ~450 g CO₂/kWh, it adds approximately 90 tonnes of CO₂ per year.

**The E-RAII Metric: Energy per Request per Achievement.** The University's sustainability research group has proposed the E-RAII (Energy per Request per Achievement Indicator) metric, which normalizes energy consumption by the value delivered:

E-RAII = (Energy consumed by request) / (Achievements delivered by request)

An "achievement" is defined as a user-valued outcome: a completed purchase, a delivered message, a rendered page. The E-RAII metric penalizes both wasted energy (requests that consume energy without delivering achievement) and over-optimization (energy spent reducing latency below the user's threshold of perception).

In 2040, the University requires all new services to report E-RAII alongside traditional performance metrics (latency, throughput, error rate). Services with high E-RAII are flagged for optimization — not just performance optimization, but *energy* optimization.

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapter 13: "The Stewardship of Jǫrð."
- Patterson, D. A., et al. (2022). "Carbon-Aware Computing." *Communications of the ACM*, 65(4), 38-40.
- Radovanović, A., et al. (2022). "Carbon-Aware Networking and Computing." *IEEE Internet Computing*, 26(3), 54-63.
- University of Yggdrasil Sustainability Group (2040). *The E-RAII Metric: Energy per Request per Achievement Indicator*. Internal Technical Report UoY-SUST-2040-07.

#### Discussion Questions

1. Carbon-aware computing time-shifts batch jobs to periods of low carbon intensity. But this increases latency for the job. If a business-critical training job finishes 8 hours later because it was shifted to a solar-rich period, is the carbon saving worth the delay? Who should make this tradeoff — the engineer, the business, or a carbon-aware scheduling system?
2. The article argues that speculative execution increases energy consumption by 5-15% for a 10-30% performance gain. After Spectre and Meltdown, some processors allow disabling speculative execution. Should performance engineers disable speculation by default, and enable it only for proven performance-critical paths?
3. The E-RAII metric normalizes energy by "achievements." But defining an "achievement" is inherently subjective and context-dependent. How should the metric handle requests that serve multiple achievements (e.g., a search results page that delivers information AND shows advertisements)?

---

### ᛃ Lecture 12: The Longship's Wake — Synthesis & Performance Architecture

**Date:** Week 6, Session 2

#### Overview

A longship leaves a wake — a pattern in the water that reveals the ship's speed, hull design, and the river's current. The performance engineer's work leaves a similar wake: the patterns of optimization, the architectural decisions, and the monitoring infrastructure that sustain performance over the lifetime of the system. This final lecture synthesizes the Eight-Legged Model, presents a unified methodology for performance engineering, and discusses the performance engineer's role in the software development lifecycle.

#### Lecture Notes

**The Eight-Legged Model Revisited.** Over the past 11 lectures, we've explored each of Sleipnir's legs:

1. **Latency** — The user's perception of speed. Covered in Lectures 1-2 (measurement), 7 (database), 8 (network), 9 (frontend).
2. **Throughput** — The system's capacity for work. Covered in Lectures 3-4 (algorithms, memory), 5 (concurrency), 6 (I/O).
3. **Memory Efficiency** — The stewardship of the memory hierarchy. Covered in Lecture 4 (caches, allocation).
4. **CPU Utilization** — The productive use of compute cycles. Covered in Lectures 3 (algorithms), 4 (cache misses = wasted cycles), 5 (lock contention = idle cycles).
5. **I/O Efficiency** — The minimization of data movement. Covered in Lecture 6 (I/O), 7 (database I/O), 8 (network I/O).
6. **Concurrency** — The coordination of parallel work. Covered in Lecture 5 (lock-free, structured concurrency).
7. **Scalability** — The system's ability to handle increasing load. Covered in Lectures 5 (concurrency), 8 (distributed systems), 10 (monitoring).
8. **Resilience** — The system's ability to maintain performance under failure. Covered in Lectures 5 (deadlock recovery), 8 (network failure modes), 10 (monitoring and alerting).

No single leg operates in isolation. Latency and throughput are related by Little's Law: L = N / T, where L is latency, N is the number of concurrent requests, and T is throughput. Memory efficiency affects CPU utilization (cache misses stall the CPU). I/O efficiency affects latency (blocking I/O blocks the whole thread). Concurrency affects scalability (lock contention limits parallelism). The performance engineer must optimize all eight legs simultaneously, understanding the tradeoffs between them.

**The Performance Engineering Methodology: A Unified Process.** This course has presented many techniques. The methodology that unifies them is a four-step cycle:

1. **Measure.** Profile the system under realistic load. Identify the top bottlenecks using SleipnirProf or equivalent tools. Establish a baseline — what is the current performance, and what are the targets?

2. **Analyze.** For each bottleneck, determine the root cause using the Eight-Legged Model. Is this a latency issue (the operation is slow), a throughput issue (we can't handle enough operations), a memory issue (we're using too much memory), or a concurrency issue (we're wasting time on synchronization)?

3. **Optimize.** Apply the appropriate technique for the root cause. The order of optimization is:
   - **Algorithmic optimization first** — Replace O(n²) with O(n log n). No amount of cache tuning can compensate for a fundamentally wrong algorithm.
   - **Data structure optimization second** — Replace linked lists with arrays, hash tables with sorted arrays for small datasets, arbitrary data layouts with cache-friendly layouts.
   - **System-level optimization third** — Tune I/O schedulers, connection pools, batch sizes, and serialization formats.
   - **Micro-optimization last** — Only after the above three levels are addressed. Hand-optimized inner loops, SIMD intrinsics, and platform-specific tuning.

4. **Verify.** Measure again. Did the optimization achieve the target? Did it introduce regressions? Did it increase energy consumption? Record the before and after in the performance changelog.

This cycle is repeated continuously. Performance is not a one-time activity — it is a discipline, like testing, that must be practiced throughout the software development lifecycle.

**Performance at Every Stage: The Longship's Keel.** A longship's keel is laid first, before the hull, the deck, or the sail. The keel determines the ship's stability, direction, and resistance. Performance engineering is the keel of the software development lifecycle — it should be designed in from the start, not bolted on at the end.

- **Requirements** — Define performance SLOs alongside functional requirements. "The API shall respond within 200ms at P99" is a testable requirement. "The API shall be fast" is not.
- **Architecture** — Choose architectural patterns that support the SLOs. A microservices architecture that chains 5 service calls in series will never achieve a P99 < 200ms if each call adds 50ms. Batch the calls, cache aggressively, or restructure the dependency graph.
- **Design** — Select algorithms and data structures that meet the SLOs at the expected load. Profile early prototypes to validate assumptions.
- **Implementation** — Write code with performance awareness: avoid allocation in hot loops, prefer contiguous data structures, minimize I/O, use async operations for high-latency work.
- **Testing** — Include performance tests in the CI/CD pipeline. Continuous benchmarking catches regressions before they reach production.
- **Deployment** — Canary deployments with performance monitoring. Roll back if P99 latency exceeds the SLO budget.
- **Production** — Continuous monitoring, SLO-based alerting, and capacity planning. The performance engineer is never done.

**The Performance Engineer's Role.** The performance engineer is a specialist, but performance is everyone's responsibility. The performance engineer's role is to:

1. **Set the standard** — Define what "good performance" means in measurable terms (SLOs, budgets, benchmarks).
2. **Build the tooling** — Create and maintain profiling, benchmarking, and monitoring infrastructure that other engineers can use without expert knowledge.
3. **Review the architecture** — Participate in architecture reviews with a performance lens. Ask: "What are the latency budgets for each component? Where are the bottlenecks? What happens at 10× current load?"
4. **Investigate the hard problems** — When the on-call team can't diagnose a performance issue, the performance engineer takes over. This requires deep knowledge of the system, the hardware, and the tools.
5. **Teach** — Spread performance awareness throughout the team. Give lunch talks, write runbooks, pair with developers on optimization.

**The 2040 Performance Landscape: Emerging Challenges.** As this course draws to a close, consider the performance challenges that will define the next decade:

- **AI inference latency** — As AI models become larger and more complex, inference latency is becoming the dominant bottleneck in many systems. The 2040 standard for real-time AI inference is <50ms end-to-end, but achieving this for 100B+ parameter models requires model distillation, quantization, hardware accelerators (TPUs, neuromorphic chips), and careful request batching.
- **Heterogeneous computing** — CPUs, GPUs, TPUs, DPUs, and neuromorphic processors all have different performance characteristics. The performance engineer must optimize across all of them simultaneously, using frameworks like CUDA, OpenCL, and the University's Sleipnir heterogeneous runtime.
- **Edge computing** — As computation moves to the edge (CDN nodes, 5G base stations, IoT devices), the performance engineer must optimize for resource-constrained environments with limited CPU, memory, and power.
- **Quantum-classical hybrid** — While quantum computers are not yet general-purpose, quantum-classical hybrid algorithms (variational quantum eigensolver, quantum approximate optimization) are entering production for specific domains. The performance engineer must understand both classical and quantum components.
- **Carbon-aware scheduling** — As discussed in Lecture 11, performance optimization must account for energy and carbon. The future performance engineer optimizes for speed *and* sustainability.

**Capstone Project: 10× Performance Improvement.** The course project is to take a real system from the University's RúnarNet platform and achieve a 10× performance improvement (10× throughput or 10× latency reduction) through systematic application of the methodology taught in this course. Students must:

1. Profile the system and identify the top 3 bottlenecks (Lecture 2)
2. For each bottleneck, perform root cause analysis using the Eight-Legged Model (Lectures 3-9)
3. Apply optimizations in order: algorithmic → data structure → system-level → micro (Lecture 12)
4. Measure the improvement with statistical rigor (confidence intervals, multiple iterations, realistic load) (Lecture 2)
5. Calculate the E-RAII metric before and after optimization (Lecture 11)
6. Document the entire process in a performance changelog

The capstone project is worth 40% of the course grade. Students work in pairs and present their findings in a final presentation during the examination period.

#### Required Reading

- Þorgrímsson, F. (2038). *The Eight-Legged Machine*. Chapters 14-15: "The Longship's Wake" and "Performance as Discipline."
- Gregg, B. (2021). *Systems Performance* (2nd ed.). Chapters 1-2 (Methodology, Operating Systems).
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly. Chapters 1-3 (Foundations, Data Models, Storage).
- University of Yggdrasil Performance Engineering Group (2040). *SleipnirProf User Guide*. Internal Documentation.

#### Discussion Questions

1. The Eight-Legged Model identifies eight dimensions of performance. Are there dimensions that should be added? Security (a system that is fast but insecure)? Correctness (a system that is fast but wrong)? Developer productivity (a system that is fast but impossible to maintain)?
2. The performance methodology says "algorithmic optimization first." But what if the algorithmic optimization requires a major refactoring that takes 3 months, while a system-level optimization (adding a cache) takes 3 days and achieves 80% of the benefit? Should the team always do the algorithmic optimization first?
3. The capstone project requires a 10× improvement. But diminishing returns mean that the first 2× is easy, the next 2× is hard, and the last 2× is extremely hard. Is 10× a realistic target for production systems, or does it encourage over-optimization at the expense of maintainability?

---

## Final Examination Preparation

### Format

The final examination consists of **8 essay questions**. Students must **choose 4** to answer in depth. Each answer should be 800-1200 words and demonstrate mastery of course concepts, ability to apply them to novel situations, and critical engagement with the readings.

### Sample Questions

1. **The Measurement Paradox.** Profiling adds overhead to the system being profiled. At what point does profiling overhead invalidate the profiler's results? Propose a methodology for profiling production systems that minimizes perturbation while maintaining diagnostic accuracy. Reference at least three profiling techniques discussed in Lecture 2 and evaluate their overhead-accuracy tradeoffs.

2. **Cache-Aware Algorithm Selection.** You are designing a real-time search engine that must serve 10,000 queries per second over a dataset of 100 million documents. The dataset is 500GB and cannot fit in memory. Propose an architecture that minimizes cache misses, maximizes throughput, and maintains P99 latency below 50ms. Justify your choice of data structures, indexing strategy, and caching policy with reference to the memory hierarchy concepts from Lecture 4.

3. **The Concurrency Tradeoff.** Compare and contrast mutex-based and lock-free approaches to concurrent data structure design. For each approach, identify three scenarios where it is superior and three where it is inferior. Your analysis should reference specific data structures (e.g., Michael-Scott queue, concurrent hash map) and real-world workloads. What does the 2040 trend toward structured concurrency mean for the mutex vs. lock-free debate?

4. **The Carbon-Aware Performance Engineer.** Your team has optimized a service from 200ms to 50ms P99 latency, but the optimization increased per-request energy consumption by 15%. The service handles 1 million requests per second. Calculate the annual additional energy consumption and CO₂ emissions (assuming a global average grid carbon intensity of 450 g CO₂/kWh). Is this optimization justified? Present arguments for both sides and propose a framework for making such decisions.

5. **Database Performance Diagnostics.** You receive an alert that P99 latency for a critical query has increased from 20ms to 500ms. Describe your diagnostic methodology, step by step, using the tools and techniques from Lectures 2, 7, and 10. Include at least five specific checks you would perform, the tools you would use (EXPLAIN ANALYZE, flame graphs, distributed traces, etc.), and the most likely root causes for this type of regression.

6. **Frontend Performance Under Constraint.** A single-page application developed in 2038 has grown to 3.2MB of compressed JavaScript. The INP score has degraded to 450ms. Propose a systematic optimization plan that includes at least six specific techniques from Lecture 9. For each technique, estimate the expected improvement and the implementation cost (developer time, risk of regression, impact on existing features). Present a prioritized plan with a realistic timeline.

7. **The Eight-Legged Model in Practice.** Select a real-world performance failure (e.g., the 2012 Knight Capital $440M loss, the 2013 Healthcare.gov launch failure, or the 2019 Cloudflare outage) and analyze it through the lens of the Eight-Legged Model. Which legs failed? Which legs could have prevented the failure if they had been stronger? What specific monitoring, tooling, or process changes would have caught the problem earlier?

8. **Performance Architecture for Scale.** You are designing the performance architecture for a new service that must handle 100,000 requests per second with P99 latency below 100ms. The service has a hot key problem (1% of keys receive 50% of traffic), reads are 95% of the workload, and data must be consistent across three regions. Present a complete performance architecture covering caching, database selection, concurrency model, I/O optimization, and monitoring. Justify each choice with reference to the course material.

---

### Grading Criteria

Each essay is graded on a 100-point scale:

- **Technical Accuracy (30 points):** Correct application of course concepts, accurate use of terminology, sound reasoning.
- **Depth of Analysis (25 points):** Thorough exploration of the question, consideration of multiple perspectives, identification of tradeoffs.
- **Use of Evidence (25 points):** References to specific course readings, lectures, and real-world examples. Data and metrics where appropriate.
- **Clarity and Organization (20 points):** Clear thesis, logical structure, effective use of headings and examples, proper academic prose.

### Research Paper Option (Alternative to Essay Exam)

Students may choose to write a 4,000-6,000 word research paper on a performance engineering topic of their choice, subject to instructor approval. The paper must:

1. Identify a performance engineering problem in a real system (open-source or production)
2. Profile the system using SleipnirProf or equivalent tools
3. Apply the Eight-Legged Model to analyze the root causes
4. Propose and implement at least one optimization
5. Measure the improvement with statistical rigor
6. Calculate the E-RAII metric before and after optimization
7. Discuss the ethical implications (carbon cost, user impact, tradeoffs)

Paper proposals are due by Week 4. Papers are due on the last day of the examination period.

---

*Thus closes the course on Performance Engineering & Optimization — the craft of making Sleipnir run. The eight legs are measured, the forge is heated, the rivers are charted, the queries are tuned, the web is woven, the bridge is rendered, the watch is kept, the earth is honored, and the wake stretches long behind us. Go forth, and build systems that are fast, efficient, resilient, and just.*

*᛭ Hail to the All-Father who rides the eight-legged steed. Hail to the smiths who make the software swift. ᛭*