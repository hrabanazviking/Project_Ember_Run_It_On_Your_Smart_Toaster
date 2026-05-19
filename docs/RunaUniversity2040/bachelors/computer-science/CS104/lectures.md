# CS104: Computer Architecture & Organization
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 (Introduction to Programming), CS102 (Discrete Mathematics)
**Description:** A comprehensive journey from the von Neumann bottleneck to the heterogeneous, neuromorphic architectures of 2040. Covers digital logic, instruction set architecture (RISC-V), pipelining, memory hierarchy, SIMD/vector processing, GPU architecture, and the emerging paradigms — processing-in-memory, photonic interconnects, and neuromorphic computing — that define the post-Moore era. Laboratory work includes RISC-V assembly programming, cache simulation, and profiling on the University's Yggdrasil-9 heterogeneous compute cluster.

---

## Lectures

### Lecture 1: The Abstraction Stack — From Sand to Software and the Ghost in the Machine

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Every computation is ultimately a dance of electrons through silicon. Between the electron and the Python script lie layers of abstraction — transistors, gates, registers, instructions, assembly, compilers, runtimes — each a triumph of engineering that hides the complexity beneath. This opening lecture surveys the full abstraction stack, establishing the vocabulary and conceptual framework for the course, and makes the case that understanding the layers beneath your code is not antiquarian curiosity but a competitive advantage in an era where the end of Dennard scaling forces every programmer to think architecturally.

#### Lecture Notes

The *abstraction stack* of a modern computer is often visualized as concentric rings or a layered cake. At the bottom: *physics* — the quantum-mechanical behavior of electrons in doped silicon, governed by Schrödinger's equation and manufactured at scale by ASML's extreme ultraviolet lithography (now at 1.4nm process node in 2040, approaching the physical limits of FinFET and gate-all-around transistor designs). One layer up: *devices* — CMOS transistors operating as voltage-controlled switches, organized into logic gates. Then: *digital logic* — combinational and sequential circuits that implement Boolean functions and store state. Then: *microarchitecture* — the organization of registers, ALUs, pipelines, and caches that executes instructions. Then: *instruction set architecture* (ISA) — the contract between hardware and software, the set of instructions and their encodings. Then: *operating system* — virtual memory, process isolation, file systems. Then: *compiler and runtime* — translation from high-level languages to machine code, with garbage collection or ownership tracking. Finally: *application* — the Python script, the AI inference, the database query.

This stack is not static. In 2040, two trends are reshaping it. First, the *end of Moore's Law* (transistor density doubling every 18–24 months) and *Dennard scaling* (power density remaining constant as transistors shrink) has driven a Cambrian explosion of specialized architectures: GPUs, TPUs, FPGAs, NPUs (neural processing units), and the neuromorphic chips (like Intel's Loihi 3 and UoY's homegrown Yggdrasil-Neuro) that directly implement spiking neural networks in silicon. General-purpose CPUs are no longer the only game in town; they are one island in an archipelago of accelerators. Second, *processing-in-memory* (PIM) and *near-memory computing* are collapsing the traditional separation between compute and storage, bringing logic into the memory arrays themselves — a physical manifestation of the principle that data movement, not computation, dominates energy costs.

We introduce the concept of the *architectural state* — the minimal set of information that defines the state of a processor at any instant: program counter (PC), register file, and memory. Every instruction transforms the architectural state in a well-defined way. This model, formalized by the von Neumann architecture in 1945, remains the conceptual core of every general-purpose processor, even as the implementations have diverged radically. The tension between the von Neumann model (sequential instruction execution) and modern reality (superscalar, out-of-order, speculative execution with deep pipelines) is the central drama of computer architecture — a drama that plays out in every security vulnerability (Spectre, Meltdown, and their 2040 descendants) that exploits the gap between the programmer's model and the silicon's reality.

We close with a detailed look at the *Yggdrasil-9 cluster*, the University's heterogeneous compute platform that students will use throughout this course. The cluster contains: 64 RISC-V BOOM (Berkeley Out-of-Order Machine) cores for general-purpose computation; 8 NVIDIA H200-class GPUs for parallel workloads; 4 Yggdrasil-Neuro chips for spiking neural network simulation and neuromorphic algorithm development; a photonic interconnect fabric (based on Ayar Labs' TeraPHY technology) for chip-to-chip communication at TB/s bandwidth; and a 2TB HBM4 memory pool accessible to all compute elements through a coherent fabric. Understanding this cluster — and writing code that exploits it effectively — requires understanding every layer from gates to system topology.

#### Key Concepts
- The abstraction stack: physics → devices → gates → microarchitecture → ISA → OS → compiler → application
- Von Neumann architecture: processor, memory, control unit, ALU, I/O
- The von Neumann bottleneck: sequential instruction fetch limits performance
- Post-Moore architectural diversification: GPUs, TPUs, NPUs, neuromorphic chips
- Processing-in-memory (PIM) as a response to the memory wall
- Architectural state: PC, register file, memory
- The Yggdrasil-9 heterogeneous compute cluster

#### Required Reading
- Patterson, D.A. and Hennessy, J.L. *Computer Organization and Design: The Hardware/Software Interface*, RISC-V Edition, 4th ed. (2038), Chapter 1 (Computer Abstractions and Technology)
- Hennessy, J.L. and Patterson, D.A. *Computer Architecture: A Quantitative Approach*, 7th ed. (2039), Chapter 1 (Fundamentals of Quantitative Design and Analysis)
- Schaller, R.R. "Moore's Law: Past, Present, and Future," *IEEE Spectrum*, 2037 — a retrospective on the end of scaling

#### Discussion Questions
1. The von Neumann bottleneck refers to the limited bandwidth between processor and memory. In 2040, with HBM4 providing 1.6 TB/s bandwidth, is the bottleneck solved, or has it simply moved? If so, to where?
2. The Yggdrasil-9 cluster combines four different compute paradigms (RISC-V, GPU, neuromorphic, photonic). Under what circumstances is it better to move computation to specialized hardware rather than doing it on the general-purpose CPU? What is the cost of specialization?
3. "The architectural state is the programmer's illusion." In what ways does modern microarchitecture violate this illusion, and why did Spectre/Meltdown-class vulnerabilities arise from those violations?

#### Practice Problems
- Trace the execution of a simple Python statement `x = y + z` down the abstraction stack: what happens in the Python interpreter, in the compiled bytecode, in the OS, in the CPU pipeline, in the cache hierarchy, in the ALU, in the transistors?
- Write a one-paragraph explanation of the von Neumann architecture suitable for a non-technical audience.
- Research the specifications of the Yggdrasil-9 cluster (available on the UoY intranet) and write a brief report on which compute elements you would use for: (a) training a large language model, (b) real-time robot control, (c) simulating a spiking neural network of 10⁶ neurons.

---

### Lecture 2: Digital Logic — Gates, Boolean Algebra, and the Physics of Thought

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Before there was software, there were gates. This lecture develops digital logic from first principles — Boolean algebra, combinational circuits, sequential circuits, and finite-state machines — as the physical substrate of computation. We emphasize not just the *what* (truth tables and Karnaugh maps) but the *why* (energy, noise margins, and the physical reasons CMOS triumphed) and the *how* (designing, simulating, and synthesizing logic in Verilog, the lingua franca of hardware description that students will use in lab).

#### Lecture Notes

Boolean algebra — the mathematics of TRUE and FALSE, 1 and 0, HIGH and LOW — is the language in which hardware speaks. George Boole's 1854 insight that logic could be algebraic was, for a century, a philosophical curiosity. Claude Shannon's 1937 master's thesis showed that Boolean algebra could describe switching circuits, and the rest is history: every digital computer ever built is, at its foundation, a Boolean engine. The three fundamental operations — AND (conjunction), OR (disjunction), NOT (negation) — form a *functionally complete* set: any Boolean function, no matter how complex, can be built from these three primitives alone. NAND and NOR are each individually functionally complete, a fact that drove early semiconductor manufacturing: build one gate type well, replicate it billions of times.

A *combinational circuit* is one whose outputs depend only on the current inputs — no memory, no state. Adders, multiplexers, decoders, and ALUs are combinational. The design flow — truth table → Boolean expression → simplification (using Boolean algebra identities or Karnaugh maps) → gate-level implementation — is tedious but fundamental. In 2040, logic synthesis tools (Yosys, Synopsys Design Compiler, and UoY's open-source `gatesynth`) automate this flow, optimizing for area, delay, and power simultaneously. But understanding the manual flow is essential for debugging synthesis results — when the tool produces a circuit that works but is inexplicably large or slow, you need to understand what it's doing.

A *sequential circuit* adds memory — its outputs depend on both current inputs and past history. Flip-flops (D-type, JK, T) and latches are the atomic memory elements. Registers are banks of flip-flops that store words of data. A *finite-state machine* (FSM) — a set of states, a transition function, and an output function — is the sequential analogue of a Boolean function: it's the fundamental model for control logic in processors. The instruction decoder in a CPU is an FSM; so is the cache controller, the branch predictor, and the DMA engine. We design FSMs as state transition graphs, encode them in Verilog, and simulate them — the same workflow used by the processor architects designing the next generation of RISC-V cores.

*Verilog* (and its cousin SystemVerilog) is introduced as the practical tool for hardware description. Unlike software languages, Verilog describes *structure* (gates and wires) and *behavior* (what the circuit does) simultaneously, and the synthesis tool infers the physical implementation. A line like `assign sum = a ^ b ^ carry_in;` describes a full adder's sum output; the synthesis tool maps it to the available gate library. The lab exercises for this lecture involve designing, simulating (with Verilator or Icarus Verilog), and synthesizing a simple ALU — an experience that transforms "the CPU does arithmetic" from a vague notion to a visceral understanding.

#### Key Concepts
- Boolean algebra: axioms, identities, De Morgan's laws
- Functional completeness: NAND and NOR universality
- Combinational circuits: adders (half, full, ripple-carry, carry-lookahead), multiplexers, decoders
- Sequential circuits: flip-flops, registers, finite-state machines
- CMOS technology: why CMOS dominates, power dissipation (static vs. dynamic), noise margins
- Hardware description languages: Verilog, modules, structural vs. behavioral description
- Logic synthesis: from RTL to gate netlist

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapter 2 (Instructions: Language of the Computer) — for the bridge from logic to ISA; Appendix B (The Basics of Logic Design) for the logic foundation
- Shannon, C.E. "A Symbolic Analysis of Relay and Switching Circuits," *MIT Master's Thesis*, 1937 — the paper that launched information theory and digital logic
- Harris, D.M. and Harris, S.L. *Digital Design and Computer Architecture*, 3rd ed. (2036), Chapters 1–3

#### Discussion Questions
1. NAND and NOR are each functionally complete. Why did CMOS technology settle on NAND as the preferred primitive gate? What physical properties make NAND gates faster or smaller than NOR gates in CMOS?
2. Karnaugh maps work well for up to 4–5 variables but become unwieldy beyond that. What algorithmic methods (e.g., Quine-McCluskey, Espresso) do synthesis tools use for larger functions? Why is exact minimization NP-hard?
3. In 2040, some researchers advocate for *analog computing* as a way to bypass the energy costs of digital switching. What are the fundamental challenges that have prevented analog from displacing digital, and might neuromorphic computing overcome them?

#### Practice Problems
- Design a 4-bit ripple-carry adder in Verilog. Simulate with all possible input combinations and verify correctness. Then design a 4-bit carry-lookahead adder and compare gate counts and critical path delays.
- Simplify the Boolean function F(A,B,C,D) = Σm(0,2,5,7,8,10,13,15) using a Karnaugh map. Implement in Verilog using only NAND gates.
- Design an FSM for a traffic light controller (North-South vs. East-West, with left-turn arrows). Draw the state diagram, encode in Verilog, and simulate with a testbench.

---

### Lecture 3: The Instruction Set Architecture — RISC-V and the Contract Between Mind and Metal

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The *instruction set architecture* (ISA) is the most durable abstraction in computing. x86 has survived since 1978; ARM since 1985. In 2040, a third contender has achieved parity: RISC-V (pronounced "risk-five"), the open standard ISA developed at UC Berkeley and now the foundation of processors ranging from embedded microcontrollers to the Yggdrasil-9's general-purpose cores. This lecture covers RISC-V's design philosophy, its base integer instruction set (RV64I), and the assembly language that is the common tongue of hardware and software.

#### Lecture Notes

An ISA defines three things: (1) the *instruction set* — the operations the processor can perform, their encodings, and their semantics; (2) the *register set* — the named storage locations directly accessible to instructions; and (3) the *memory model* — how instructions access memory, including addressing modes and consistency guarantees. Everything else — pipelining, cache design, branch prediction, out-of-order execution — is microarchitecture, an implementation detail that can change without breaking ISA compatibility. This separation is what allows a program compiled for RISC-V in 2020 to run, without modification, on a RISC-V processor designed in 2040 with triple the pipeline depth and a completely different cache hierarchy.

RISC-V embodies the *RISC philosophy* (Reduced Instruction Set Computer), which emerged from the insights of Patterson (Berkeley RISC) and Hennessy (Stanford MIPS) in the 1980s: (1) simple instructions that execute in one cycle; (2) load-store architecture — only load and store instructions access memory, all others operate on registers; (3) large uniform register file (32 integer registers, 32 floating-point registers); (4) fixed-length instruction encoding (32 bits, with a compressed 16-bit extension). These design choices are not aesthetic; they are consequences of quantitative analysis. Simple, fixed-length instructions make pipelining easier. Load-store architecture simplifies the critical path. A large register file reduces memory traffic. In 2040, RISC-V's modular ISA — a small mandatory base (RV64I) plus optional standard extensions (M for multiply/divide, A for atomics, F/D for floating-point, C for compressed, V for vector) — allows implementers to choose exactly the features needed for their application domain, from a minimal embedded core (RV32E with 16 registers) to a supercomputing vector engine (RV64GCV).

We dive into RV64I, the base integer instruction set for 64-bit RISC-V. The instruction formats — R-type (register-register), I-type (immediate), S-type (store), B-type (branch), U-type (upper immediate), J-type (jump) — are designed for decoding simplicity: the opcode and register fields are always in the same bit positions, regardless of format. This regularity, which x86's variable-length encoding famously lacks, simplifies the instruction decoder to a few multiplexers and reduces the pipeline's front-end complexity. We examine each instruction class: arithmetic (`add`, `sub`, `sll`, `slt`), immediate (`addi`, `andi`, `ori`), memory (`lw`, `sw`, `ld`, `sd`), branches (`beq`, `bne`, `blt`, `bge`), and jumps (`jal`, `jalr`). The *calling convention* — which registers hold arguments (a0–a7), return values (a0–a1), and which are caller-saved vs. callee-saved — is as much a part of the ISA ecosystem as the instructions themselves.

A significant portion of the lecture is devoted to *assembly language programming* — not because students will write entire applications in assembly, but because reading assembly is essential for understanding what compilers do, for debugging performance anomalies, and for the reverse-engineering skills needed in security (CS405). We write simple RISC-V assembly: a function that computes Fibonacci numbers, a loop that sums an array, a recursive factorial. We assemble with `riscv64-unknown-elf-as`, link with `riscv64-unknown-elf-ld`, and run on the Yggdrasil-9's RISC-V cores or the Spike simulator. Seeing your code reduced to a sequence of `addi`, `jal`, and `bnez` drives home the lesson: all the abstraction of Python, all the type safety of Rust — somewhere, beneath it all, a program counter increments and an ALU adds.

#### Key Concepts
- ISA vs. microarchitecture: the architectural contract
- RISC design principles: simple instructions, load-store, large register file, fixed encoding
- RISC-V modular ISA: RV64I base + standard extensions
- RISC-V instruction formats: R, I, S, B, U, J
- RISC-V register file and calling convention
- Assembly language: labels, directives, pseudo-instructions
- The toolchain: assembler, linker, simulator (Spike), hardware (Yggdrasil-9)

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapter 2 (Instructions: Language of the Computer)
- Waterman, A. and Asanović, K. *The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA*, version 2024 (updated continuously through 2040)
- *The RISC-V Reader: An Open Architecture Atlas*, 2nd ed. (2037) by Patterson and Waterman

#### Discussion Questions
1. x86's variable-length instruction encoding (1–15 bytes) makes decoding complex but allows dense code. RISC-V's fixed-length encoding simplifies decoding but can produce larger code. In 2040, with cache sizes in the megabytes, does code density still matter? Under what circumstances?
2. The RISC-V calling convention passes the first 8 integer arguments in registers. What happens if a function has 12 arguments? How does the stack come into play, and what are the performance implications of "spilling" arguments to memory?
3. RISC-V deliberately leaves certain features (like integer division by zero behavior) undefined or implementation-specific. Why? What is the engineering rationale for leaving gaps in a standard?

#### Practice Problems
- Write a RISC-V assembly function `sum_array(base_addr, length)` that sums an array of 64-bit integers. Use the standard calling convention (a0 = base address, a1 = length, a0 = return sum). Assemble and test with Spike.
- Disassemble a simple C function compiled with `riscv64-unknown-elf-gcc -O2 -S`. Identify the correspondence between C constructs (loops, conditionals, function calls) and RISC-V instructions. Comment on the compiler's optimization choices.
- Hand-assemble (convert to machine code) the instruction `addi x5, x10, 42` using the I-type format. Show your work: opcode, funct3, rd, rs1, immediate fields.

---

### Lecture 4: Pipelining — The Assembly Line of Computation

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A single-cycle processor executes one instruction per clock cycle — but each instruction takes the full cycle, making the clock slow. Pipelining breaks instruction execution into stages, like an assembly line, so that multiple instructions overlap: while one is being decoded, another is being fetched, and yet another is writing back results. The result: a pipeline with N stages can approach N instructions per cycle throughput. This lecture develops the classic five-stage RISC pipeline, the hazards that threaten it, and the techniques — forwarding, stalling, speculation — that keep the pipeline full.

#### Lecture Notes

The *five-stage pipeline* (IF, ID, EX, MEM, WB) is the "hello world" of computer architecture — simple enough to understand in one lecture, deep enough to contain all the essential ideas. *Instruction Fetch* (IF): read the instruction at the program counter (PC) from instruction memory. *Instruction Decode* (ID): decode the instruction, read operands from the register file, compute branch targets. *Execute* (EX): perform ALU operations, compute effective addresses for memory operations. *Memory Access* (MEM): read from or write to data memory (for loads and stores). *Write Back* (WB): write results back to the register file. Each stage takes one clock cycle, and in steady state, all five stages are active simultaneously on five different instructions — achieving an ideal CPI (cycles per instruction) of 1.

Reality, of course, is messier. *Hazards* are situations where the next instruction cannot execute in the next clock cycle. We classify three types: *structural hazards* (two instructions need the same hardware resource simultaneously — e.g., a single memory port serving both instruction fetch and data access); *data hazards* (an instruction depends on the result of a previous instruction that hasn't completed yet — e.g., `add x1, x2, x3` followed by `sub x4, x1, x5`); and *control hazards* (a branch instruction changes the PC, but the next instructions have already been fetched — what to do with them?). Each hazard requires a countermeasure: structural hazards are solved by duplicating resources (separate instruction and data caches, the Harvard architecture); data hazards are solved by *forwarding* (bypassing the pipeline registers to send results directly from EX/MEM or MEM/WB to the next instruction's EX stage) and, when forwarding is insufficient, *stalling* (inserting a bubble — a no-op — into the pipeline for one cycle); control hazards are solved by *branch prediction* (guessing the branch direction and fetching from the predicted path) and *speculative execution* (executing instructions before knowing whether the branch was correctly predicted, flushing them if wrong).

The *pipeline diagram* (a grid with instructions on one axis and clock cycles on the other, showing which stage each instruction occupies at each cycle) is our primary reasoning tool. Drawing pipeline diagrams for sequences with hazards reveals exactly where stalls occur and how forwarding resolves them. Students practice with the classic hazard cases: the load-use hazard (a load followed immediately by an instruction that uses the loaded value — even forwarding can't help; one stall cycle is required) and the branch hazard (the branch outcome is known at the EX stage, meaning three instructions have been fetched behind it that might need to be flushed).

In 2040, the basic five-stage pipeline has been elaborated into *superscalar* designs that fetch, decode, execute, and retire multiple instructions per cycle (typically 4–8 on high-end cores) and *out-of-order* execution that dynamically schedules instructions to avoid stalls. But the principles are the same: identify hazards, resolve them with forwarding or stalling, predict branches, speculate. The Yggdrasil-9's RISC-V BOOM cores are 8-wide out-of-order monsters with 224-entry reorder buffers — but at their heart, they're still five-stage pipelines, just with each stage massively parallelized and each hazard detector replicated and accelerated.

#### Key Concepts
- The five-stage pipeline: IF, ID, EX, MEM, WB
- Pipeline registers: separating stages, propagating control signals
- Structural hazards and resource duplication
- Data hazards: RAW (read after write), forwarding, stalling
- Load-use hazard: the one-cycle stall that forwarding cannot eliminate
- Control hazards: branch delay, branch prediction, speculative execution
- Pipeline diagrams as the central reasoning tool

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapter 4 (The Processor)
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*, Chapter 3 (Instruction-Level Parallelism)
- Emma, P.G. and Davidson, E.S. "Characterization of Branch and Data Dependencies in Programs," *IEEE TC*, 1987 — a classic quantitative study that informed early pipeline design

#### Discussion Questions
1. The load-use hazard requires a one-cycle stall even with full forwarding. Why is this fundamentally unavoidable in a five-stage pipeline? Would a deeper pipeline make it worse?
2. Branch prediction accuracy on modern processors exceeds 97%. What happens to performance when a branch mispredicts in a deep pipeline (20+ stages)? How many instructions are flushed, and what is the performance penalty?
3. Speculative execution was the root cause of the Spectre and Meltdown vulnerabilities (2018). In 2040, what architectural features prevent speculative side-channel attacks while preserving performance?

#### Practice Problems
- Draw a pipeline diagram for the following sequence on a standard five-stage pipeline with forwarding: `lw x1, 0(x2); add x3, x1, x4; sub x5, x6, x7; and x8, x3, x5`. Identify all stalls and forwarding paths.
- Modify the single-cycle RISC-V processor from the previous lab into a pipelined version. Add pipeline registers between stages. Test with a simple program and compare CPI with the single-cycle version.
- Analyze the following code for pipeline hazards: `addi x1, x0, 10; Loop: lw x2, 0(x3); add x3, x3, x4; addi x1, x1, -1; bnez x1, Loop`. How many stalls per iteration with no forwarding? With full forwarding? How many with a branch predictor vs. always-not-taken?

---

### Lecture 5: The Memory Hierarchy — Caches, Locality, and the Art of Hiding Latency

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A modern RISC-V core can execute an instruction in ~0.3 nanoseconds. Accessing main memory (DDR5 or HBM4) takes ~80–120 nanoseconds — a 300x gap. Without caches, every load and store would stall the pipeline for hundreds of cycles, reducing performance to a crawl. The memory hierarchy — registers, L1 cache, L2 cache, L3 cache, main memory, storage — bridges this gap through the principle of *locality*: programs tend to access the same data repeatedly (temporal locality) and nearby data (spatial locality). This lecture develops the theory and practice of caching, from direct-mapped to set-associative, from write-through to write-back, from single-level to multi-level.

#### Lecture Notes

A *cache* is a small, fast memory that holds a subset of the contents of a larger, slower memory. When the processor requests an address, the cache checks whether it contains that address (a *hit*); if so, the data is returned quickly. If not (a *miss*), the cache fetches the data from the slower memory, stores it (evicting something else if necessary), and returns it. The *hit rate* — the fraction of accesses that hit — determines performance. A hit rate of 95% with a hit time of 1 cycle and a miss penalty of 100 cycles gives an average access time of 1 + 0.05 × 100 = 6 cycles — far better than 100 cycles without a cache, but still far from 1.

Cache design is governed by four interrelated choices: (1) *block size* — how many bytes are fetched on a miss (exploiting spatial locality); (2) *associativity* — how many locations a given address can map to (direct-mapped: 1; set-associative: N; fully associative: any location); (3) *replacement policy* — which block to evict on a miss (LRU, pseudo-LRU, random, RRIP); (4) *write policy* — what happens on a write hit (write-through: update cache and memory immediately; write-back: update cache only, mark dirty, write to memory on eviction) and on a write miss (write-allocate: fetch into cache then write; no-write-allocate: write directly to memory). These choices interact in complex ways. Larger blocks improve spatial locality exploitation but increase miss penalty. Higher associativity reduces conflict misses but increases hit time and energy. Write-back reduces memory traffic but complicates coherence in multicore systems.

We analyze cache performance using the *3Cs model*: *compulsory misses* (cold misses — the first access to a block, unavoidable), *capacity misses* (the working set exceeds cache size), and *conflict misses* (multiple blocks map to the same set, evicting each other — eliminated by full associativity, reduced by higher associativity). This taxonomy guides optimization: compulsory misses are reduced by prefetching (predicting future accesses and fetching early); capacity misses by larger caches or better data layout; conflict misses by higher associativity or victim caches (small fully-associative buffers that hold recently evicted blocks).

In 2040, the memory hierarchy has deepened and diversified. The Yggdrasil-9 BOOM cores have: 32KB L1 I-cache and 32KB L1 D-cache (8-way set-associative, 2-cycle latency), 512KB private L2 (16-way, 12-cycle latency), 8MB shared L3 (32-way, 40-cycle latency), and access to the 2TB HBM4 pool through a coherent crossbar (~100ns). Between L3 and HBM4 sits a *near-memory compute* layer — small processing elements embedded in the HBM4 base dies that can perform simple aggregations and filtering, reducing data movement. Understanding this hierarchy — and writing cache-conscious code — is a skill that pays dividends in every CS course that follows, from data structures (CS201) to database systems (CS405).

The lecture closes with a practical lab: a *cache simulator* written in Python or Rust that models a configurable cache hierarchy (size, associativity, block size, write policy), processes memory access traces (generated from real programs using `valgrind` or the Yggdrasil-9's hardware performance counters), and reports hit rates and miss classifications. Building the simulator internalizes the concepts more deeply than any lecture can.

#### Key Concepts
- Temporal and spatial locality
- Cache organization: direct-mapped, set-associative, fully associative
- Address decomposition: tag, index, block offset
- The 3Cs: compulsory, capacity, and conflict misses
- Write policies: write-through vs. write-back, write-allocate vs. no-write-allocate
- Replacement policies: LRU, pseudo-LRU, random, RRIP
- Multi-level caches: inclusion vs. exclusion vs. non-inclusive
- Prefetching: hardware and software techniques

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapter 5 (Large and Fast: Exploiting Memory Hierarchy)
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*, Chapter 2 (Memory Hierarchy Design)
- Drepper, U. "What Every Programmer Should Know About Memory," 2007 (updated 2035 by the UoY Systems Group) — the definitive practical guide

#### Discussion Questions
1. Why are L1 caches typically split (separate instruction and data) while L2 and L3 are unified? What would happen if L1 were unified?
2. The 3Cs model classifies misses. Is it possible to have zero compulsory misses? Zero capacity misses? Zero conflict misses? For each, either explain why not, or describe the conditions under which it is possible.
3. In a multi-core system with private L1/L2 caches and a shared L3, the cache coherence protocol (e.g., MESI, MOESI) ensures that cores see a consistent view of memory. How does the coherence protocol interact with the write policy? Why is write-back essentially required for multi-core?

#### Practice Problems
- A 32KB direct-mapped cache with 64-byte blocks. For a 64-bit address space, how many bits are tag, index, and block offset? Now make it 4-way set-associative — how do the fields change?
- Given the access sequence: 0, 4, 8, 12, 16, 4, 20, 8, 24, 4, 12, 28 — simulate a 4-entry fully-associative cache with LRU replacement. Report hit rate.
- Write a cache simulator supporting configurable size, associativity, and block size. Test with a memory trace (from a matrix multiplication or a sort — generate with `valgrind --tool=lackey` on a simple C program). Experiment with different configurations and report the 3C breakdown.
- Optimize a matrix multiplication loop for cache performance. Implement standard (i-j-k) ordering, then reorder to exploit spatial locality (i-k-j, k-i-j, blocking/tiling). Measure with hardware performance counters on the Yggdrasil-9 and report L1 miss rates.

---

### Lecture 6: Instruction-Level Parallelism — Superscalar, Out-of-Order, and the Pursuit of IPC

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A pipelined processor achieves CPI approaching 1. To go beyond — to execute *multiple* instructions per cycle — requires exploiting *instruction-level parallelism* (ILP): the property that many instructions in a sequential program are independent and could execute simultaneously. This lecture covers superscalar execution (multiple-issue), out-of-order execution (dynamic scheduling), and the microarchitectural structures — register renaming, reorder buffers, reservation stations — that make ILP practical. We use the RISC-V BOOM core and Intel's Golden Cove as running examples.

#### Lecture Notes

*Superscalar* processors issue multiple instructions per cycle — typically 4 to 8 in 2040's high-performance cores. This requires fetching multiple instructions (wide fetch), decoding them in parallel (wide decode), checking for dependences among them, issuing the independent ones to multiple functional units (wide issue), and retiring them in order (wide retire). The bottleneck is not functional units — transistors are cheap — but *dependences*: if the second instruction depends on the result of the first, they cannot issue together. The compiler can help by *scheduling* — reordering instructions to maximize the distance between producers and consumers — but dynamic (hardware) scheduling is essential because many dependences (especially through memory) are unknown at compile time.

*Out-of-order execution* (OoO) is the technique that frees the processor from strict program order. The core idea: instructions are fetched and decoded in program order, but they are issued to functional units as soon as their operands are available, regardless of original order. This means a load that misses in the cache does not stall independent instructions that follow it. The key microarchitectural structures are: the *reservation stations* (buffers that hold instructions waiting for operands — when all operands are ready, the instruction fires), the *reorder buffer* (ROB — a circular queue that holds instructions from dispatch to retirement, ensuring they retire in program order to maintain precise exceptions), and the *register alias table* (RAT — implements register renaming by mapping architectural registers to physical registers, eliminating false dependences — WAR and WAW hazards — that would otherwise limit ILP).

*Register renaming* deserves special attention. Consider the sequence: `add x1, x2, x3; sub x2, x4, x5; mul x1, x6, x7`. The `sub` writes `x2`, but no subsequent instruction reads the old `x2` — yet the `mul` writes `x1`. There's a *write-after-write* (WAW) hazard on `x1` between `add` and `mul`. Without renaming, the `mul` must wait for the `add` to complete (to avoid overwriting the architectural register in the wrong order). With renaming, the `add` writes to physical register P10, the `sub` writes to P11, and the `mul` writes to P12 — no conflict. Renaming transforms WAW and WAR (write-after-read) hazards, which are not true data dependences, into independent operations on distinct physical registers. This is perhaps the single most important microarchitectural innovation — it increases ILP by 20–40% on typical integer code.

*Speculative execution* extends OoO across branches. When the branch predictor guesses a direction, the processor begins fetching, decoding, and executing instructions from the predicted path — allocating ROB entries, renaming registers, even issuing stores (to a store buffer, not to cache — stores are held until the branch is resolved). If the prediction is correct, the speculative work becomes real work, and the processor has gained cycles. If wrong, the pipeline is *flushed* — all instructions after the branch are discarded, the RAT is restored from a checkpoint, and fetching resumes from the correct path. The performance of OoO processors is thus critically dependent on branch prediction accuracy; a mispredict in a 200-instruction speculation window can waste the equivalent of dozens of correctly executed instructions.

In 2040, the frontier of ILP is *value prediction* — predicting not just branch direction but the actual values loaded from memory or produced by long-latency operations, allowing dependent instructions to execute speculatively before the value is actually known. The Yggdrasil-9's experimental BOOM-VP core incorporates a neural value predictor (a small on-chip network trained at boot time on the running workload's value patterns) that achieves 85% accuracy on pointer-chasing codes, doubling effective ILP on some benchmarks. This blurring of the line between traditional speculation and machine learning is a hallmark of 2040 processor design.

#### Key Concepts
- Superscalar: multiple issue, multiple execute, multiple retire
- In-order vs. out-of-order execution
- Register renaming: RAT, physical register file, WAW/WAR elimination
- Reservation stations and the Tomasulo algorithm
- Reorder buffer (ROB) and precise exceptions
- Speculative execution and branch prediction
- Store buffers and memory disambiguation
- Value prediction as the 2040 ILP frontier

#### Required Reading
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*, Chapter 3 (Instruction-Level Parallelism and Its Exploitation)
- Tomasulo, R.M. "An Efficient Algorithm for Exploiting Multiple Arithmetic Units," *IBM Journal*, 1967 — the original paper on the algorithm that still bears his name
- Mutlu, O. et al. "Value Prediction for the Post-Moore Era," *ISCA 2038* — a recent survey of neural value prediction techniques

#### Discussion Questions
1. Register renaming eliminates WAW and WAR hazards. Could a compiler eliminate these hazards through static register allocation? Why is dynamic renaming still necessary?
2. The ROB enforces in-order retirement. Why is in-order retirement necessary for precise exceptions? What would happen if instructions could retire out of order?
3. Value prediction speculates on data values. What are the security implications? Could a malicious process train the neural value predictor to leak information about another process's data, similar to Spectre-style side channels?

#### Practice Problems
- Given the instruction sequence: `ld x1, 0(x2); add x3, x1, x4; sub x5, x6, x7; mul x8, x3, x5; addi x9, x8, 1`, identify all RAW, WAR, and WAW hazards. Show which are eliminated by register renaming.
- Simulate the Tomasulo algorithm by hand for the above sequence. Assume three reservation stations for the adder and two for the multiplier, each with 2-cycle latency for add and 4-cycle for multiply. Track the state of each reservation station, the RAT, and the ROB through each cycle.
- Research BOOM's open-source RTL (available on GitHub) and identify the pipeline stages, the rename unit, and the ROB. Write a short report on how BOOM's microarchitecture differs from the textbook Tomasulo design.

---

### Lecture 7: SIMD and Vector Processing — One Instruction, Many Data

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

"Multiply this array by that array" — a single operation, applied to hundreds or thousands of elements. Rather than looping element-by-element (scalar processing), SIMD (Single Instruction, Multiple Data) applies one instruction to a vector of operands simultaneously. This lecture covers SIMD from its origins in Cray vector supercomputers through Intel's SSE/AVX extensions to RISC-V's "V" vector extension, with emphasis on programming SIMD effectively in both assembly and high-level languages.

#### Lecture Notes

Flynn's taxonomy (1966) classifies computer architectures by their instruction and data streams. *SISD* (single instruction, single data) is the classic von Neumann processor. *SIMD* (single instruction, multiple data) is the subject of this lecture. *MISD* (multiple instruction, single data) is largely theoretical. *MIMD* (multiple instruction, multiple data) covers most multicore and distributed systems. SIMD's efficiency comes from *amortization*: the instruction fetch and decode energy is shared across many data operations, dramatically improving energy efficiency. This is why GPUs, which are essentially massively wide SIMD machines, dominate high-throughput computing, and why even "general-purpose" CPUs dedicate increasing die area to SIMD units.

SIMD comes in two architectural flavors. *Packed SIMD* (SSE, AVX, NEON) operates on fixed-width registers (128, 256, 512 bits) treated as vectors of smaller elements (e.g., a 512-bit register as 16 × 32-bit floats). Instructions like `vaddps` add all corresponding elements of two such registers in parallel. The limitation is the fixed vector length: code written for AVX-512 doesn't directly run on a machine with 256-bit vectors, though the AVX-512 ISA includes masking and embedded broadcasting to ease the transition. *Vector architectures* (Cray, RISC-V V extension) take a different approach: vector length is not fixed in the ISA but set at runtime by a control register (`vl`). A single `vadd.vv` instruction operates on `vl` elements, where `vl` is set to the actual vector length available. This provides *binary compatibility* across implementations with different hardware vector lengths — code written for a 256-bit vector machine runs without modification on a 4096-bit machine, simply processing more elements per instruction.

The RISC-V "V" extension (ratified 2021, widely deployed by 2040) is a modern vector architecture with several distinctive features: *vector length agnosticism* (VLEN ≥ 128 bits, software queries the actual length); *stripmining* (automated loop-over-vectors for arrays larger than VLEN); *predicated execution* (per-element masking with a vector mask register, enabling vectorized if-then-else); *gather-scatter* (indexed loads and stores for sparse data structures); and *chaining* (forwarding results from one vector instruction directly to the next without going through registers, similar to pipeline forwarding but for vectors).

Programming SIMD effectively requires *data-level parallelism*: the problem must have independent operations on multiple data elements. This is trivially true for array operations (BLAS, image processing, neural network inference) but requires restructuring for problems with irregular data access or cross-element dependences. We cover the common SIMD programming patterns: *vectorization* of loops (compiler auto-vectorization or manual intrinsics); *reduction* (sum, product, min/max across a vector — requires special shuffle and horizontal-add instructions); *gather-scatter* (irregular access patterns that SIMD historically struggled with, now handled efficiently by RISC-V V's indexed load/store); and *divergent control flow* (if-then-else within a SIMD register, handled by predication/masking).

The lab component uses the Yggdrasil-9's RISC-V cores with the V extension to vectorize common algorithms: matrix multiplication, image convolution, and a simple neural network inference pass. Students write both assembly (to understand the instruction semantics) and C with intrinsics (for productivity), measuring speedup vs. scalar code.

#### Key Concepts
- Flynn's taxonomy: SISD, SIMD, MISD, MIMD
- Packed SIMD (SSE/AVX) vs. vector architectures (Cray, RISC-V V)
- Vector length agnosticism and binary compatibility
- Stripmining, predication, gather-scatter, chaining
- Auto-vectorization in compilers
- SIMD reductions and shuffle operations
- Data-level parallelism: when SIMD works and when it doesn't

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapter 6 (Parallel Processors from Client to Cloud)
- *RISC-V V Extension Specification*, version 1.0 (ratified 2021, with 2040 amendments)
- Intel *Intrinsics Guide* (online, updated through 2040) — reference for x86 SIMD intrinsics
- Fisher, J. and Rau, B.R. "Instruction-Level Parallel Processing," *Science*, 1991 — historical perspective on VLIW and SIMD

#### Discussion Questions
1. Packed SIMD (AVX-512) and vector SIMD (RISC-V V) have different design philosophies. Under what workloads does each excel? Why hasn't the industry converged on one approach?
2. The RISC-V V extension supports "vector length agnostic" code. What are the software engineering challenges of writing code that must be performant across a 100× range of vector lengths (say, 128 bits to 131,072 bits)?
3. GPUs achieve massive SIMD throughput by hiding latency with massive multithreading (warps/wavefronts). Why don't CPUs adopt the same strategy? What is fundamentally different about CPU vs. GPU workloads?

#### Practice Problems
- Write a RISC-V V extension assembly routine that computes `C[i] = A[i] + B[i]` for vectors of length N. Use stripmining for the case where N > VLEN. Test with Spike configured for VLEN=256 and VLEN=1024 — verify the same binary works.
- Vectorize a simple image convolution (3×3 kernel) using RISC-V V intrinsics. Compare performance against a scalar implementation. How close do you get to the theoretical peak SIMD speedup?
- Using the Yggdrasil-9's perf tools, profile a scalar matrix multiplication and identify the fraction of execution time spent in loop overhead vs. actual arithmetic. Then profile the SIMD version. Where did the speedup come from?

---

### Lecture 8: GPU Architecture — The Massively Parallel Coprocessor

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

GPUs began as fixed-function graphics accelerators. By 2040, they are the dominant platform for AI training, scientific simulation, and high-performance computing — flexible, massively parallel processors that deliver orders of magnitude more throughput than CPUs on data-parallel workloads. This lecture covers GPU architecture from the programmer's perspective: the SIMT (Single Instruction, Multiple Thread) execution model, the memory hierarchy, and the programming model (CUDA and its open-source 2040 equivalents) that maps computation onto thousands of cores.

#### Lecture Notes

A GPU's architectural philosophy is the inverse of a CPU's. A CPU optimizes for *latency*: deep pipelines, branch prediction, out-of-order execution, large caches — all to minimize the time to complete a single thread. A GPU optimizes for *throughput*: thousands of lightweight threads, simple in-order cores, small caches — all to maximize total work completed per unit time, even if individual threads take longer. A CPU is a sprinter; a GPU is a marathon team. This divergence explains why GPUs achieve >50× the FLOPS/Watt of CPUs on matrix multiplication — they spend their transistor budget on ALUs, not on branch predictors and reorder buffers.

The *SIMT* (Single Instruction, Multiple Thread) model is NVIDIA's name for the GPU execution model. Threads are grouped into *warps* (NVIDIA, 32 threads) or *wavefronts* (AMD, 64 threads). All threads in a warp execute the same instruction simultaneously, but on different data — an extension of SIMD where the "D" is per-thread register state. When threads in a warp *diverge* (take different branches of an if-else), the warp executes both paths sequentially, with threads masked off on the path they didn't take — a phenomenon called *warp divergence* that serializes what looked like parallel code. Avoiding warp divergence is the first discipline of GPU programming: keep control flow uniform within warps.

The GPU memory hierarchy is distinctive. At the bottom: *global memory* (HBM, hundreds of GB, high bandwidth ~2 TB/s, high latency ~300 cycles). Above it: *L2 cache* (shared across all streaming multiprocessors, tens of MB, unified). Per-SM: *shared memory* (a programmer-managed scratchpad, ~128–256 KB per SM, ~20 cycles latency, shared among threads in a thread block — the key to GPU performance, analogous to a software-managed L1). *Registers* (the largest pool — 256 KB per SM — partitioned among threads). The programmer's challenge is to orchestrate data movement through this hierarchy: load from global to shared, synchronize, compute from shared to registers, synchronize, write back. This is a different mental model from CPU cache-oblivious programming — on a GPU, you must be *cache-conscious*, explicitly staging data through shared memory.

We introduce the *CUDA programming model* (NVIDIA's proprietary API, still dominant in 2040) and its open alternatives: *HIP* (AMD, essentially CUDA with a different name), *SYCL* (Khronos Group, C++-based, targeting multiple backends), and *WGPU* (WebGPU compute shaders, increasingly capable for portable GPU compute). The programming abstractions — *grid* (the entire computation), *block* (a group of threads that can cooperate through shared memory and synchronization), *thread* (the individual execution unit) — map directly onto the hardware hierarchy. Launching a kernel with `kernel<<<num_blocks, block_size>>>(args)` spawns the grid, and the hardware scheduler maps blocks to SMs and warps to execution units.

The Yggdrasil-9 cluster includes NVIDIA H200-class GPUs with the H100/H200's Tensor Core units — specialized matrix-multiply accelerators that deliver >1 PFLOPS of dense matrix performance (FP8 precision). Programming Tensor Cores effectively requires restructuring algorithms to expose matrix-multiply operations, even when the problem isn't naturally a matrix multiplication — a technique called *im2col* (image-to-column) for convolutions, *flash attention* for transformer models. This pattern — restructuring algorithms to match the hardware's preferred dataflow — is the essence of GPU optimization and a skill that transfers to any accelerator architecture.

#### Key Concepts
- Throughput vs. latency: the GPU architectural philosophy
- SIMT execution: warps, warp divergence, predication
- GPU memory hierarchy: global, L2, shared memory, registers
- CUDA programming model: grid, block, thread; `__global__`, `__shared__`, `__syncthreads()`
- Tensor Cores and matrix-multiply acceleration
- Occupancy: keeping enough warps active to hide memory latency
- Open alternatives: HIP, SYCL, WGPU

#### Required Reading
- Kirk, D.B. and Hwu, W.W. *Programming Massively Parallel Processors*, 5th ed. (2039), Chapters 1–6
- NVIDIA *CUDA C++ Programming Guide* (online, continuously updated)
- Jouppi, N. et al. "Ten Lessons from Three Generations of Tensor Processing Units," *ISCA 2021* — for comparison with Google's TPU architecture

#### Discussion Questions
1. A GPU hides memory latency by oversubscribing warps — when one warp stalls on a memory access, the SM switches to another warp. How does this compare to CPU hyperthreading? Why can GPUs support far more threads per core (warps per SM)?
2. Warp divergence serializes execution. What compiler and hardware techniques exist to reduce divergence? (Hint: predication, warp compaction, dynamic warp formation.)
3. CUDA is proprietary to NVIDIA. In 2040, with the rise of RISC-V-based accelerators and open GPU architectures, is there a viable open-source GPU programming ecosystem? What are the obstacles?

#### Practice Problems
- Implement vector addition in CUDA: `C[i] = A[i] + B[i]` for N = 10^8 elements. Experiment with block sizes (32, 64, 128, 256, 512, 1024) and measure throughput. Explain the performance curve.
- Implement matrix multiplication (naive) in CUDA. Then optimize: (a) use shared memory tiling, (b) use float4 vectorized loads, (c) avoid bank conflicts. Measure speedup at each stage.
- Profile a CUDA kernel using NVIDIA Nsight Compute (available on Yggdrasil-9). Identify the limiting factor: compute utilization, memory bandwidth, or latency. Propose and implement an optimization.

---

### Lecture 9: Heterogeneous Computing — CPU, GPU, NPU, FPGA, and the Orchestration Problem

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The post-Moore era is heterogeneous. A 2040 system-on-chip may contain: general-purpose RISC-V cores, a GPU-like accelerator, a neural processing unit (NPU), a DSP for signal processing, an FPGA fabric for custom logic, and specialized fixed-function blocks for cryptography, video codecs, and sensor fusion. The challenge is no longer designing any single processor but *orchestrating* computation across this diverse fabric — moving data, scheduling tasks, and maintaining coherence. This lecture introduces heterogeneous system architecture and the programming models that tame it.

#### Lecture Notes

*Heterogeneous computing* is a response to the end of Dennard scaling. When you can't make all transistors faster, you make them *different* — each specialized for a class of computations, achieving orders-of-magnitude better energy efficiency on its target workload. An NPU (neural processing unit) can perform a matrix-vector multiply at 100× the energy efficiency of a general-purpose CPU by exploiting the regularity of neural network computation: systolic arrays of multiply-accumulate units, optimized dataflows that maximize data reuse, reduced-precision arithmetic (FP8, INT4, even binary/ternary in 2040's extreme-edge NPUs). An FPGA (field-programmable gate array) can implement a custom pipeline that processes one datum per cycle at a fraction of the power of a CPU doing the same work, albeit at lower clock frequency. The tradeoff is flexibility vs. efficiency: CPU (most flexible, least efficient) → GPU (less flexible, more efficient for parallel) → FPGA (customizable hardware, efficient for streaming) → ASIC (fixed function, maximally efficient, zero flexibility post-manufacture).

The *orchestration problem* is the defining challenge of heterogeneous computing: given a computation, how do you partition it across available compute elements to minimize execution time or energy? This is a scheduling problem with heterogeneous resources, data movement costs, and complex dependences — essentially, a combinatorial optimization that is NP-hard in general. In practice, heuristic approaches dominate: *static partitioning* (the programmer or compiler decides at compile time which code runs where, using pragmas or domain-specific languages) and *dynamic scheduling* (a runtime scheduler, like the one in the Yggdrasil OS kernel, monitors device utilization and moves work opportunistically). The OS201 "Nine Realms" architecture extends this idea across an entire AI OS: realms are mapped to compute elements based on their workload characteristics, with the governance realm (OS401) dynamically rebalancing.

*Programming models* for heterogeneous systems are an active area of research and standardization in 2040. *SYCL* (C++ with heterogeneous device compilation, targeting CPUs, GPUs, FPGAs, and NPUs through a single-source model) has gained significant traction. *OpenMP 7.0* (2040) supports accelerator offloading with unified shared memory. *oneAPI* (Intel's unified programming model, now adopted by the RISC-V ecosystem) provides a common API across architectures. But the holy grail — write once, run optimally everywhere — remains elusive. The programmer must still understand the underlying hardware to achieve peak performance. The Yggdrasil curriculum addresses this head-on: CS104 exposes the hardware diversity; CS201 teaches architecture-conscious algorithm design; OS105 covers the AI OS's heterogeneous scheduling layer.

A significant portion of this lecture is devoted to *interconnect* — the physical and logical fabric that connects heterogeneous compute elements. The Yggdrasil-9 uses a *photonic interconnect* (Ayar Labs TeraPHY) for chip-to-chip links, achieving >1 TB/s bandwidth per fiber with sub-nanosecond latency. On-chip, a *network-on-chip* (NoC) — essentially a miniature internet, with routers, packets, and flow control — connects cores, caches, and accelerators. Understanding the topology (mesh, ring, crossbar, tree) and the routing algorithms (dimension-ordered, adaptive, minimal) is essential for reasoning about data movement costs. A computation that runs efficiently on a local NPU may become bottlenecked by NoC congestion if its data must traverse multiple hops.

We close with a look at the *Yggdrasil-Neuro* chip — UoY's homegrown neuromorphic processor, designed in collaboration with Intel's Loihi team. Unlike conventional processors, Yggdrasil-Neuro implements *spiking neural networks* (SNNs) in silicon: neurons are analog circuits that accumulate charge and fire spikes; synapses are programmable weights connecting neurons; and information is encoded in spike timing, not in numerical values stored in registers. This is a fundamentally different model of computation — asynchronous, event-driven, inherently temporal — and it requires a different programming paradigm (SNN training algorithms like STDP or surrogate-gradient methods). The Yggdrasil-Neuro is a harbinger: as CMOS scaling approaches physical limits, the architectures of 2050 will look less like the von Neumann machines of 1950 and more like the brain.

#### Key Concepts
- Heterogeneous SoC architecture: CPUs, GPUs, NPUs, FPGAs, fixed-function blocks
- Specialization vs. flexibility: the efficiency-flexibility spectrum
- The orchestration problem: partitioning computation across devices
- Shared virtual memory and cache coherence across accelerators
- Interconnect: NoC topology, routing, flow control; photonic links
- Programming models: SYCL, OpenMP, oneAPI; single-source vs. library-based
- Neuromorphic computing: spiking neural networks, event-driven, asynchronous

#### Required Reading
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*, Chapter 7 (Domain-Specific Architectures)
- Chung, E.S. et al. "Serving DNNs in Real Time at Datacenter Scale with Project Brainwave," *IEEE Micro*, 2018 — FPGA-accelerated DNN inference at Microsoft
- Davies, M. et al. "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning," *IEEE Micro*, 2018 — and the follow-up "Loihi 3: Scaling Neuromorphic Computing to 100 Million Neurons," *Nature Electronics*, 2036

#### Discussion Questions
1. The efficiency-flexibility spectrum suggests that ASICs are always the most efficient choice for a fixed workload. Why, then, are most AI chips (Google TPU, NVIDIA Tensor Cores, Yggdrasil-Neuro) programmable rather than pure ASICs? What is the value of programmability even in a domain-specific accelerator?
2. The orchestration problem — scheduling across heterogeneous devices — is NP-hard in general. What heuristics do real systems use? How does the OS201 governance realm make orchestration decisions?
3. Neuromorphic computing encodes information in spike timing rather than numerical values. What classes of problems are naturally suited to this representation? What classes are fundamentally unsuited?

#### Practice Problems
- Profile a workload on the Yggdrasil-9 cluster: run a matrix multiplication on the CPU, GPU, and NPU. Measure execution time and energy (using the cluster's built-in power meters). Calculate the energy efficiency (GFLOPS/Watt) for each device. Write a report on which device you would choose for: (a) real-time inference with a 1ms deadline, (b) batch training of a large model, (c) embedded deployment with a 5W power budget.
- Implement a simple data-parallel task in SYCL that runs on both CPU and GPU from the same source. Use the `sycl::queue` to dispatch to the appropriate device. Measure and report performance portability — does the same code run efficiently on both devices?
- Design a mapping of a simple AI agent's perception-action loop onto heterogeneous hardware. Which components go on the NPU? Which on the CPU? Which on the neuromorphic chip? Justify each choice with quantitative reasoning (even if using estimated numbers).

---

### Lecture 10: Input/Output — Buses, Interrupts, DMA, and the Interface to the Physical World

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A processor that cannot communicate with the outside world — with memory, storage, networks, sensors, actuators — is useless. I/O (Input/Output) systems bridge the processor's clean digital world with the messy analog reality. This lecture covers the I/O subsystem: buses and interconnects, memory-mapped I/O, interrupts, DMA (Direct Memory Access), and the emerging I/O paradigms for 2040 — CXL (Compute Express Link) for cache-coherent device attachment and NVMe 3.0 for storage that approaches memory speeds.

#### Lecture Notes

*Memory-mapped I/O* (MMIO) is the dominant paradigm for device communication: device registers are mapped into the processor's physical address space. A store to address `0x1000_0000` might write a command register on a disk controller; a load from `0x1000_0004` might read the device's status. This elegantly unifies device communication with the existing load-store architecture — no special I/O instructions needed. However, it introduces a key constraint: MMIO accesses must not be cached (the device's status changes independently of the processor's actions) and must not be reordered (the order of writes to a device's command registers is often semantically significant). Memory ordering constraints — *fence* instructions, *non-cacheable* and *strongly ordered* memory types — ensure correctness in the presence of MMIO.

*Interrupts* are the mechanism by which devices signal the processor asynchronously. When a disk completes a read, when a network packet arrives, when a timer expires — the device asserts an interrupt line, the processor acknowledges, saves its state, and vectors to an interrupt handler. This is vastly more efficient than *polling* (the processor repeatedly checking the device status), especially for infrequent or unpredictable events. In 2040, interrupt architectures have evolved to handle the extreme scale of modern systems: *message-signaled interrupts* (MSI-X) deliver interrupts as memory writes (no dedicated interrupt lines); *interrupt remapping* (Intel VT-d, ARM SMMU, RISC-V IOMMU) virtualizes interrupts for guest OSes; and *interrupt coalescing* batches multiple interrupts into a single notification to reduce overhead.

*Direct Memory Access* (DMA) is the technique that frees the processor from the drudgery of copying data between devices and memory. A DMA engine — a specialized hardware unit — is programmed with a source address, destination address, and length. It transfers the data autonomously, and interrupts the processor only when done. DMA is the unsung hero of high-performance I/O: without it, every byte read from disk or network would require a processor load and store, consuming all available cycles. With DMA, the processor initiates the transfer and goes back to useful work. In 2040, the frontier is *peer-to-peer DMA* — DMA transfers directly between devices (e.g., from a network card to a GPU's memory, without touching the CPU's memory at all), enabled by PCIe 7.0's P2P support and CXL's cache-coherent device model.

*CXL* (Compute Express Link), built on PCIe's physical layer, is the 2040 standard for attaching accelerators and memory expanders with cache coherence. A CXL-attached device can participate in the CPU's cache coherence protocol — it can cache host memory, and the CPU can cache device memory. This eliminates the expensive cache flushes that legacy PCIe device programming requires and enables fine-grained shared-memory computation between CPU and accelerator. The Yggdrasil-9's NPU and neuromorphic chip are CXL-attached, enabling the OS to treat them as coherent peers rather than dumb peripherals — a qualitative shift in the programming model.

We also cover *NVMe 3.0* (Non-Volatile Memory Express), the storage protocol that has replaced SATA and SAS for all performance-sensitive storage. NVMe leverages the parallelism of flash memory (multiple queues, 64K commands per queue) and the low latency of PCIe (now <5 µs for a 4KB random read on high-end drives) to make storage access feel more like memory access. In 2040, the line between "storage" and "memory" is blurring: *persistent memory* (Optane's successor, now based on novel phase-change materials) sits on the memory bus but retains data across power cycles, requiring a rethinking of the file-system abstraction.

#### Key Concepts
- Memory-mapped I/O: device registers as memory addresses
- Interrupts: asynchronous device signaling, interrupt handlers, MSI-X
- DMA: autonomous data transfer, scatter-gather, peer-to-peer
- PCIe: lanes, root complex, switches; PCIe 7.0
- CXL: cache-coherent device attachment, .cache/.mem/.io protocols
- NVMe: parallel queues, low-latency flash access
- Persistent memory and the storage-memory convergence

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapter 5 (storage and I/O sections)
- PCI-SIG, *PCI Express Base Specification*, revision 7.0 (2040) — the physical and link layers
- CXL Consortium, *Compute Express Link Specification*, version 3.0 (2038)
- NVMe Express, *NVM Express Base Specification*, revision 3.0 (2039)

#### Discussion Questions
1. Memory-mapped I/O uses the same address space for memory and devices. What are the security implications? How does the IOMMU (I/O Memory Management Unit) protect against malicious DMA?
2. Interrupt coalescing reduces overhead but increases latency. How would you tune the coalescing parameters for: (a) a high-frequency trading system where every nanosecond counts, (b) a batch-processing system where throughput matters more than latency?
3. CXL enables accelerators to cache host memory coherently. How does this change the programming model for heterogeneous computing compared to traditional PCIe with explicit cache management?

#### Practice Problems
- Write a simple device driver (in Rust or C) for a virtual UART device on the RISC-V VirtIO platform. Use MMIO to read/write the device registers. Implement both polling and interrupt-driven modes. Measure CPU utilization in each mode.
- Implement a ring buffer for communication between a "producer" (simulating a DMA engine filling the buffer) and a "consumer" (the processor reading from it). Ensure correct synchronization using memory barriers / fences.
- Analyze the PCIe topology of the Yggdrasil-9 using `lspci -t` and the system documentation. Draw the topology diagram showing the root complex, switches, and endpoints. Calculate the bandwidth available to each device under simultaneous load.

---

### Lecture 11: RISC-V Processor Design Lab — From RTL to Silicon

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Architecture lectures convey knowledge; building a processor conveys understanding. This lecture describes the capstone laboratory project of CS104: the design, implementation, and testing of a complete five-stage pipelined RISC-V processor (RV32I) in SystemVerilog, synthesized to an FPGA. Students work in teams of three, each responsible for a pipeline stage, collaborating through a shared Git repository and a continuous integration pipeline that runs their RTL against a suite of architecture tests.

#### Lecture Notes

The laboratory is structured as a series of milestones over 10 weeks:

**Milestone 1 (Week 1–2): Single-Cycle Processor.** Implement an unpipelined RV32I processor that executes one instruction per cycle. The datapath includes: PC register, instruction memory, register file, ALU, data memory, and control unit. The control unit decodes the instruction's opcode and funct fields to generate control signals: RegWrite, ALUSrc, MemWrite, MemRead, MemtoReg, Branch, Jump. Test with a suite of RISC-V assembly programs (the `riscv-tests` suite, provided by the instructors) running in simulation (Verilator). The single-cycle processor will be slow (long critical path through instruction memory → register file → ALU → data memory → register file), but correct.

**Milestone 2 (Week 3–5): Pipelined Processor.** Insert pipeline registers between stages to create a five-stage pipeline (IF/ID, ID/EX, EX/MEM, MEM/WB). The control signals must be propagated through the pipeline registers. Immediately, data hazards appear. Implement forwarding (from EX/MEM and MEM/WB to the EX stage) to resolve most RAW hazards, and a hazard detection unit that stalls on load-use hazards (inserting a bubble into IF/ID and setting control signals to zero for the ID/EX instruction). For control hazards, implement a simple static branch predictor (always not-taken) and flush the three instructions behind a taken branch.

**Milestone 3 (Week 6–7): Forwarding and Stalling.** Refine the hazard handling. Implement full forwarding — including forwarding from MEM/WB to the ID stage for branch comparisons (the branch might depend on a value currently in the pipeline). Add support for handling the write-after-read (WAR) hazard through proper pipeline ordering (which our design, with register reads in ID and writes in WB, naturally avoids). Test with programs specifically designed to stress hazards: tight loops with carried dependences, pointer-chasing code, deeply nested function calls.

**Milestone 4 (Week 8–9): Memory and I/O.** Replace the idealized instruction/data memories with a unified cache interface. Implement a simple direct-mapped cache (configurable size and block size) in front of a simulated DRAM (with realistic latency: 100 cycles for a miss). The processor must now handle cache misses — the pipeline stalls until the miss is resolved. Add a simple MMIO interface: map a timer (cycle counter) and a UART (for console I/O) into the address space. Now the processor can run interactive programs — a milestone that never fails to excite students.

**Milestone 5 (Week 10): FPGA Deployment.** Synthesize the design using Yosys (open-source synthesis) and place-and-route with nextpnr targeting the Lattice ECP5 FPGA on the Yggdrasil-9's FPGA mezzanine cards. Load the bitstream, connect a terminal, and watch your processor print "Hello, World!" — executing code that you compiled, on hardware that you designed. The final deliverable includes: RTL source code, testbenches, synthesis reports (area, frequency, power), and a 5-page design document explaining the architecture, design decisions, and lessons learned.

The pedagogical philosophy: *learning by building.* Computer architecture is not a spectator sport. The concepts of pipelining, forwarding, stalling, and cache coherence remain abstract until you've debugged a waveform trace showing a load-use stall at cycle 47 that you didn't anticipate. The frustration of seeing your processor execute the wrong instruction — and the exhilaration of finding the hazard-detection bug — are the experiences that forge architectural intuition. Students who complete this lab see every subsequent CS course — operating systems, compilers, parallel computing — through the lens of someone who has built the machine from gates up.

In 2040, the lab has been enhanced with AI-assisted debugging: the `veridebug` tool (developed at UoY) uses a transformer model trained on waveform traces to suggest likely bug locations when a test fails. It doesn't replace understanding — the student must still comprehend the suggestion and decide whether to apply it — but it accelerates the debugging cycle, allowing students to spend more time on design and less on tracing signals through a 2000-cycle simulation waveform.

#### Key Concepts
- Processor design flow: architecture → RTL → simulation → synthesis → FPGA
- DVFS (dynamic voltage-frequency scaling): operating point selection
- RISC-V RV32I: complete instruction set coverage
- Pipeline implementation: stage registers, control propagation
- Hazard resolution: forwarding paths, stall insertion, flush logic
- Cache interface integration
- FPGA toolchain: Yosys, nextpnr, openFPGALoader
- AI-assisted hardware debugging

#### Required Reading
- Patterson and Hennessy, *Computer Organization and Design*, Chapters 4 and 5
- Asanović, K. and Celio, C. "The Berkeley Out-of-Order Machine (BOOM): An Industry-Standard, Open-Source, RISC-V Out-of-Order Processor," *UC Berkeley Technical Report*, 2017 (updated 2040) — for inspiration on what your simple pipeline can evolve into
- Wolf, C. *Yosys Manual* (online, continuously updated) — the open-source synthesis tool documentation

#### Discussion Questions
1. The lab implements a five-stage in-order pipeline. How would the design complexity change if you added: (a) a branch predictor, (b) multiple-issue (superscalar), (c) out-of-order execution? Which of these would you tackle first, and why?
2. The AI-assisted debugging tool `veridebug` suggests fixes based on patterns in waveform traces. What are the risks of relying on AI suggestions for hardware debugging? How can the tool be designed to enhance rather than replace understanding?
3. FPGA deployment closes the gap between simulation and reality. What differences between simulation and real hardware (timing, power, signal integrity) might cause a design that passes simulation to fail on the FPGA?

#### Practice Problems
- (This entire lecture is a practice problem — the processor design lab. The following are supplementary exercises.)
- Add a new instruction to your RV32I processor: `swap rd, rs1, rs2` — atomically swap the values in registers rs1 and rs2 and store the old value of rs2 in rd. You'll need to modify the decoder, the ALU (or add a bypass), and the control logic.
- Measure the critical path of your pipelined processor. Which pipeline stage determines the maximum clock frequency? Propose and implement an optimization to balance the pipeline stages.
- Connect two instances of your processor to a shared memory through an arbiter. Implement a simple test-and-set spinlock and demonstrate mutual exclusion.

---

### Lecture 12: Architecture 2040 and Beyond — The Post-Von Neumann Horizon

**Course:** CS104 — Computer Architecture & Organization
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The von Neumann architecture has served computing for 95 years. In 2040, its limitations — the sequential instruction stream, the processor-memory bottleneck, the rigid separation of compute and memory — are increasingly apparent. This capstone lecture surveys the emerging architectural paradigms that may define the next 95 years: processing-in-memory, neuromorphic computing, quantum accelerators, photonic logic, and the radical reimagination of computation itself. The lecture is not a prediction but a provocation: the architectures of 2040 will seem as quaint to the students of 2090 as the ENIAC seems to us.

#### Lecture Notes

*Processing-in-memory* (PIM) attacks the von Neumann bottleneck at its root: instead of moving data to the processor, move the processor to the data. Modern PIM designs integrate simple processing elements — lightweight RISC-V cores or SIMD units — into the memory array itself, typically at the bank level. A PIM-enabled HBM4 stack might have 32 banks, each with a small in-order core that can perform arithmetic, comparisons, and simple aggregations on the data stored in that bank. The host processor issues *PIM commands* ("sum all values in column 5 where column 3 > threshold") that are executed in parallel across all banks, with only the result returned to the host. This can reduce data movement by orders of magnitude for memory-bound workloads like graph processing, sparse linear algebra, and database scans — exactly the workloads that dominate the AI OS's world-modeling engine (WM303). The UoY-led *Project Mímir* (named for the Norse god of wisdom who guards the well of knowledge at the root of Yggdrasil) is deploying a PIM-enhanced memory system for the Yggdrasil-9 cluster, with early results showing 12× speedup on knowledge graph traversal compared to traditional HBM+DDR.

*Neuromorphic computing* abandons the von Neumann model almost entirely. Instead of a processor reading instructions and data from memory, a neuromorphic chip consists of a network of artificial neurons connected by programmable synapses. Computation is *event-driven*: neurons fire when their accumulated input exceeds a threshold, sending spikes to downstream neurons through a fabric that physically emulates the brain's connectivity. The Loihi 3 chip (Intel, 2036) integrates 1 million neurons and 128 million synapses on a single die, consuming <1 watt. UoY's Yggdrasil-Neuro pushes this further with on-chip learning: synaptic weights adapt in real time using a variant of spike-timing-dependent plasticity (STDP), allowing the chip to learn patterns directly from sensor streams without off-chip training. The programming model is radically different — you don't write loops and branches; you configure a network of spiking neurons and let the dynamics unfold. OS403 (Stochastic Personality Composition) uses the Yggdrasil-Neuro as a substrate for personality modules that adapt to user interaction patterns in real time, a use case that conventional processors handle poorly because of the continuous, low-latency adaptation required.

*Quantum computing* in 2040 remains a specialized accelerator, not a general-purpose replacement for classical processors. Quantum processing units (QPUs) with ~1,000 logical qubits (error-corrected, not physical) are available in the cloud (IBM Quantum System Four, Google Sycamore-III, and the Yggdrasil-9's integrated RISC-V + QPU hybrid). The architecture is *heterogeneous*: a classical processor dispatches quantum circuits to the QPU, which executes them and returns measurement results. The killer applications in 2040 are: quantum chemistry simulation (modeling molecular interactions for drug discovery and battery design), optimization (quantum approximate optimization algorithm — QAOA — for logistics and finance), and cryptanalysis (Shor's algorithm, though post-quantum cryptography is now standard, rendering this less impactful than feared in the 2020s). For computer architects, the challenge is integration: tight coupling between CPU and QPU (shared memory, low-latency dispatch), cryogenic control electronics (QPU operation at 20 millikelvin requires specialized control interfaces), and the compiler stack (mapping high-level algorithms to QPU circuits with error mitigation).

*Photonic computing* uses light instead of electrons for logic and interconnects. The advantages: light doesn't generate heat from resistance (photons don't collide the way electrons do in wires), light travels at the speed of light in the medium (no RC delay), and multiple wavelengths can be multiplexed on a single waveguide (wavelength-division multiplexing, WDM). In 2040, photonic *interconnects* are mature (the Yggdrasil-9's chip-to-chip links), but photonic *logic* remains experimental. The UoY Photonics Lab has demonstrated an optical matrix multiplier — a photonic circuit that performs a 64×64 matrix-vector multiply in a single light-propagation delay (picoseconds) with femtojoule energy per multiply-accumulate. If scaled, this could revolutionize AI inference, where matrix multiplication dominates. The challenge: photonic logic is inherently analog (amplitude and phase encode values) and suffers from noise, crosstalk, and the lack of a good optical memory element.

We close with a philosophical reflection. The history of computer architecture is a history of the tension between *generality* and *efficiency*. The von Neumann machine was a brilliant compromise: one machine, programmable for any task. The post-Moore era has tilted the balance toward specialization — not because we've forgotten the value of generality, but because the physical limits of silicon demand it. The next great architecture will not be a single machine but an *ecology* of heterogeneous compute elements, woven together by a programming model that makes their diversity transparent. This is the vision of the Yggdrasil AI OS — not just software that runs on a computer, but an architecture that integrates computation at every level, from photonic logic to quantum accelerators, from neuromorphic personality modules to PIM-augmented memory. The students of CS104, having built a RISC-V processor from gates, are prepared to contribute to this vision — not as passive users of computers, but as their architects.

#### Key Concepts
- Processing-in-memory (PIM): computation at the data, Project Mímir
- Neuromorphic computing: spiking neurons, STDP, event-driven execution, Yggdrasil-Neuro
- Quantum computing: QPU as accelerator, cryogenic integration, error mitigation
- Photonic computing: optical interconnects, photonic matrix multipliers, analog challenges
- The generality-efficiency tension and the heterogeneous ecology
- The AI OS as an architectural vision: integrating computation at every level

#### Required Reading
- Mutlu, O. et al. "Processing Data Where It Makes Sense: Enabling In-Memory Computation," *Microprocessors and Microsystems*, 2039 — comprehensive PIM survey
- Davies, M. "Loihi 3 and the Neuromorphic Roadmap," *Intel Labs Technical Report*, 2036
- Preskill, J. "Quantum Computing in the NISQ Era and Beyond," *Quantum*, 2018 (updated 2038) — the seminal essay on near-term quantum computing
- UoY Photonics Lab, "Optical Matrix Multiplication at Scale: A Path to Exa-FLOP Inference," *Nature Photonics*, 2039

#### Discussion Questions
1. Processing-in-memory moves computation to the data. What software changes are required to exploit PIM? Can existing programs benefit automatically, or must they be rewritten?
2. Neuromorphic computing is asynchronous and event-driven. The von Neumann model is synchronous and instruction-driven. Is it possible to integrate both in a single system, or are they fundamentally incompatible models of computation?
3. In 2040, a 1,000-qubit QPU exists but can only run circuits with depth ~100 before errors overwhelm the computation. What classes of algorithms are viable at this scale? Does the "quantum advantage" require thousands more qubits, or are there near-term applications?

#### Practice Problems
- Research Project Mímir (materials on UoY intranet) and write a 2-page proposal for a PIM-accelerated algorithm. Choose a specific algorithm (e.g., PageRank, sparse matrix-vector multiply, k-means clustering), explain why it benefits from PIM, and sketch the dataflow.
- Using the Loihi 3 simulator (available on the Yggdrasil-9 cluster), implement a simple spiking neural network that classifies handwritten digits (MNIST). Compare the energy consumption (estimated by the simulator) with a conventional neural network on the CPU.
- Design a heterogeneous scheduling strategy for a workload that combines: (a) dense matrix operations (best on GPU/NPU), (b) sparse graph traversal (best on PIM), (c) real-time anomaly detection (best on neuromorphic). Discuss the data movement and synchronization challenges.

---

## Final Examination Preparation

The CS104 final examination consists of two components:

### Component 1: Written Examination (60%, 3 hours)

Eight essay-style questions, answer four. Questions integrate concepts from across the course and require both analytical reasoning and quantitative problem-solving.

**Sample Questions:**

1. **Pipeline Analysis.** Consider the following RISC-V code sequence. Identify all data hazards (RAW, WAR, WAW). Show how forwarding resolves them and where stalls are required. Draw a pipeline diagram for the execution.
2. **Cache Design.** Given a memory access trace, simulate a cache with specified parameters. Classify each miss as compulsory, capacity, or conflict. Propose a cache configuration change that would reduce misses and justify your proposal quantitatively.
3. **ISA Design.** Compare RISC-V's design philosophy with x86's. Discuss the tradeoffs of fixed-length vs. variable-length instruction encoding in the context of a deeply pipelined superscalar processor. What are the implications for the front-end (fetch, decode) complexity?
4. **SIMD and Vectorization.** Given a loop operating on an array, determine the loop-carried dependences. If the loop is vectorizable, write it using RISC-V V extension intrinsics. If not, explain which dependences prevent vectorization and whether loop restructuring could eliminate them.
5. **Memory Hierarchy.** A program has a working set of 64KB. Design a two-level cache hierarchy (L1 and L2) that maximizes hit rate within a total area budget. Justify your choices of size, associativity, block size, and inclusion policy for each level.
6. **Out-of-Order Execution.** Describe the roles of the reorder buffer, reservation stations, and register alias table in a Tomasulo-style out-of-order processor. Trace a given instruction sequence through these structures.
7. **Heterogeneous Computing.** Propose a mapping of the following workload components onto a heterogeneous SoC (CPU, GPU, NPU, FPGA): (a) real-time video decoding, (b) natural language inference, (c) database query processing, (d) cryptographic hashing. Justify each mapping.
8. **Architectural Futures.** Critically evaluate the claim: "Processing-in-memory will render the cache hierarchy obsolete." Under what workloads is PIM most beneficial? What are the obstacles to PIM replacing caches for general-purpose computation?

### Component 2: Processor Design Project (40%)

The laboratory project described in Lecture 11. Assessment criteria:
- Correctness (passes all provided RV32I compliance tests): 50%
- Pipeline efficiency (CPI on benchmark suite): 20%
- Design document quality (clarity of architecture description, justification of design decisions): 20%
- Team contribution (peer evaluation): 10%

---

**Course Code:** CS104
**Last Updated:** 2040-08-15
**Department:** Computer Science, University of Yggdrasil
**Instructor of Record:** Prof. Björn Þorsteinsson, Ph.D. (ETH Zürich)
**Contact:** b.thorsteinsson@uoy.edu.aks
