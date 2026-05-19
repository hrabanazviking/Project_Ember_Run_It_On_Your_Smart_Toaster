# CS307: GPU & Parallel Computing
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 3, Semester 2
**Prerequisites:** CS204 (Architecture & Hardware Description), CS207 (Concurrent & Parallel Programming)
**Instructor:** Dr. Elding Fǫr, Faculty of Computational Arts

> *"A single oarsman moves the longship slowly. Eighty oarsmen, in rhythm, move it faster than the wind. GPUs are the eighty oarsmen of computation — unremarkable individually, devastating together when the stroke is true."* — Elding Fǫr, *The Many-Oared Hull* (2038)

---

## Course Description

GPU & Parallel Computing is a hands-on course covering the architectures, programming models, and algorithmic techniques needed to harness massively parallel processors. By 2040, GPUs are the primary compute engine for AI, scientific computing, graphics, and increasingly for general-purpose computing through unified memory architectures. The course covers: GPU architecture (CUDA cores, tensor cores, memory hierarchy, warp scheduling), programming models (CUDA, OpenCL, SYCL, oneAPI), parallel algorithm patterns (reduction, scan, histogram, sort, matrix multiplication, convolution), multi-GPU and distributed GPU computing, and emerging architectures (NPUs, DPUs, neuromorphic accelerators).

The Norse metaphor: the *átt* — a unit of eight rowers on a Viking longship, each rowing in perfect synchrony. A GPU warp of 32 threads (4 áttir) executes a single instruction across all threads, like rowers responding as one to the drum. The art is keeping all threads busy — the art of *drive utilization*.

---

## Lectures

### ᚠ Lecture 1: The Many-Oared Hull — GPU Architecture Fundamentals

**Date:** Week 1, Session 1

#### Overview

Why are GPUs so fast? Because they don't do what CPUs do. This lecture introduces the fundamental architectural differences between CPUs and GPUs: control logic vs. compute units, large caches vs. high-bandwidth memory, latency-optimized vs. throughput-optimized design. We trace the evolution from fixed-function graphics accelerators (1990s) through programmable shaders (2000s) to the general-purpose compute powerhouses of 2040 (NVIDIA Hopper/B200 successors, AMD CDNA, Intel Xe). The Norse framing: a CPU is a single champion (einvigi) — fast, agile, optimized for winning one duel. A GPU is a shield wall — thousands of warriors, each simpler than the champion, but together overwhelming.

#### Lecture Notes

The fundamental insight of GPU architecture is the **throughput-latency tradeoff**. A CPU is designed to minimize the latency of a single thread: it devotes significant die area to control logic, branch prediction, out-of-order execution, and large caches (L1: 32KB, L2: 256KB-32MB per core in 2040). A GPU is designed to maximize the throughput of many threads: it devotes die area to compute units and registers, with minimal control logic per thread and small caches (L1: 128KB per SM, L2: 40-80MB shared across all SMs).

**The GPU Memory Hierarchy (2040 standard NVIDIA architecture).**

| Level | Size | Bandwidth | Latency |
|-------|------|-----------|---------|
| Registers per SM | 256K 32-bit | 32 TB/s | 1 cycle (~0.4ns) |
| L1/Shared Memory | 128-256 KB | 12 TB/s | 20 cycles |
| L2 Cache | 80 MB | 4 TB/s | 200 cycles |
| HBM4 | 80 GB (stacked) | 4 TB/s | 400 cycles |
| System memory | 512-2048 GB | 100 GB/s (PCIe 6/CXL) | 1000+ cycles |

The key number: **bandwidth-to-compute ratio**. A 2040 GPU has ~100 TFLOPS of FP32 compute and ~4 TB/s of HBM4 bandwidth. This means for every floating-point operation, the GPU can load ~40 bytes from memory. In practice, many algorithms need more data per operation than this — memory bandwidth is the bottleneck. This is the *memory wall* that defines GPU algorithm design.

**SIMT Execution Model.** NVIDIA's SIMT (Single Instruction, Multiple Threads) model executes threads in groups of 32 called **warps**. All threads in a warp execute the same instruction at the same time — but each thread can have its own registers and its own path through the program. If threads diverge (e.g., an `if/else` where some threads take the `if` and others the `else`), both sides execute sequentially, and threads on the inactive side are masked. Divergence is the most common source of performance degradation in GPU programs.

**The Ampere-to-Blackwell Evolution (2020-2040).** Key architectural innovations over two decades:
- **Tensor Cores (Volta, 2017):** Dedicated matrix-multiply-accumulate units for deep learning. By 2040, 8th-generation tensor cores support FP8, FP16, BF16, TF32, FP32, and FP64 precision, and can perform 2048-bit matrix multiplies per clock.
- **MIG (Multi-Instance GPU, Ampere, 2020):** Partition a GPU into up to 7 isolated instances for multi-tenant workloads.
- **NVLink-C2C (Grace-Hopper, 2023):** Cache-coherent interconnect between GPU and CPU at 900 GB/s.
- **Neural Kernel Generation (Hopper-next, 2028):** The GPU can automatically generate optimized kernel code from Python descriptions, reducing the need for hand-tuned CUDA.
- **Unified Memory Fabric (Blackwell-next, 2035):** CPU and GPU share a single virtual address space with hardware-coherent caches — no more manual `cudaMemcpy`.

#### Required Reading
- NVIDIA (2024). *CUDA C++ Programming Guide*. Chapters 1-4.
- Hennessy, J.L. & Patterson, D.A. (2019). *Computer Architecture: A Quantitative Approach*, 6th ed. Chapter 4: "GPGPUs."
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 1: "The Fleet and the Champion." Yggdrasil University Press.

#### Discussion Questions
1. A CPU core uses ~20% of its die area for compute; a GPU SM uses ~50%. Where does the other die area go in each case, and why?
2. Warp divergence is the single biggest performance killer in GPU programming. Give an example of a simple algorithm that suffers from warp divergence and a way to restructure it.
3. The memory bandwidth of HBM4 is 4 TB/s, but system memory via PCIe 6.0 is 100 GB/s. What happens when a GPU kernel operates on data that doesn't fit in the 80 GB HBM? How do you avoid this bottleneck?

---

### ᚢ Lecture 2: The CUDA Programming Model — Rowing in Formation

**Date:** Week 2, Session 1

#### Overview

CUDA (Compute Unified Device Architecture) is the dominant GPU programming framework in 2040. This lecture covers the CUDA programming model: kernels, threads, blocks, grids, and the memory hierarchy (global, shared, local, constant, texture). Students write, compile, and profile their first CUDA kernel — a vector addition that demonstrates the core patterns of GPU programming: data parallelism, memory coalescing, and occupancy. The rowing analogy: each thread is an oarsman, each block is a ship's crew (32-1024 oarsmen), and the grid is the fleet.

#### Lecture Notes

**The Kernel Launch Hierarchy.** A CUDA kernel is a C++ function that runs on the GPU. It is launched with a grid of thread blocks:
```cuda
// Launch kernel with 256 blocks × 128 threads
vector_add<<<256, 128>>>(d_a, d_b, d_c, N);
```

- **Grid:** All threads launched by a single kernel call.
- **Block:** A group of threads that execute on the same SM and can cooperate via shared memory and synchronization (`__syncthreads()`).
- **Thread:** The smallest unit of execution. Each thread has its own program counter, registers, and local memory.

Each thread knows its position in the grid via built-in variables: `threadIdx.x`, `blockIdx.x`, `blockDim.x`. A thread's global index is `blockIdx.x * blockDim.x + threadIdx.x`.

**Memory Hierarchy.**

| Memory | Scope | Lifetime | Size | Speed |
|--------|-------|----------|------|-------|
| Registers | Per thread | Kernel | ~255 32-bit words | 0.4ns |
| Local memory | Per thread | Kernel | Up to 512KB (spills to HBM) | Fast if cached |
| Shared memory | Per block | Block | 48-164 KB | ~7ns |
| Global memory | All threads + host | Application | 80 GB HBM | ~160ns |
| Constant memory | All threads | Kernel | 64 KB (cached) | ~7ns if cached |
| Texture memory | All threads | Kernel | 48 KB (cache) | Spatial caching |

**Memory Coalescing.** The most critical performance concept: when threads in a warp access global memory, the hardware coalesces their accesses into as few cache-line transactions as possible (a cache line is 128 bytes in 2040 GPUs). For optimal performance, adjacent threads should access adjacent memory locations:

```cuda
// COALESCED: thread 0 accesses [0], thread 1 accesses [1], ...
float val = data[threadIdx.x];  // One 128B transaction for 32 threads

// NON-COALESCED: thread 0 accesses [0], thread 1 accesses [stride], ...
float val = data[threadIdx.x * 1024];  // 32 separate 128B transactions
```

Non-coalesced memory access can reduce effective bandwidth by 10-100×. The art of GPU programming is rearranging data access patterns to be coalesced.

**Occupancy.** Occupancy is the ratio of active warps per SM to the maximum possible. Higher occupancy hides memory latency: when one warp stalls on a memory access, the SM switches to another active warp. The key equation:
- Max warps per SM = 64 (2040 architecture)
- Registers per SM = 65,536 (2040)
- If each thread uses 32 registers, max threads per SM = 65,536/32 = 2,048 = 64 warps.
- If a kernel uses 64 registers per thread, max threads per SM = 1,024 = 32 warps (50% occupancy).

The occupancy-ILP tradeoff: lower occupancy with more per-thread ILP (instruction-level parallelism) can sometimes outperform high occupancy. In 2040, the GPU scheduler automatically balances these.

#### Required Reading
- NVIDIA (2024). *CUDA C++ Best Practices Guide*. Chapters 1-5.
- Harris, M. (2007). "Optimizing CUDA." *GTC 2007* (still the classic introduction to occupancy and coalescing).
- Cheng, J. et al. (2014). *Professional CUDA C Programming*. Wrox.

#### Discussion Questions
1. Given a kernel where each thread uses 48 registers and shared memory of 32 bytes, what is the maximum number of threads per SM? What limits it: registers or shared memory?
2. Write a matrix multiplication kernel with coalesced reads from matrix A and coalesced reads from matrix B. Explain the tiling strategy needed for both to be coalesced.
3. Why does shared memory improve matrix multiplication performance despite having only 48-164 KB? What's the tradeoff?

---

### ᚦ Lecture 3: Parallel Algorithm Patterns — The Oarsman's Drill

**Date:** Week 3, Session 1

#### Overview

Certain algorithmic patterns recur in GPU programming. This lecture covers the fundamental patterns: reduction (sum, max, min), scan (prefix sum), histogram, stencil (convolution), and sort. For each pattern, we cover the naive GPU implementation, the optimized version with shared memory and warp-level primitives, and the performance characteristics. The Norse analogy: the rowing drill — a set of practiced patterns that every crew learns, allowing them to respond to any situation without hesitation.

#### Lecture Notes

**Parallel Reduction (Sum).** The canonical first GPU algorithm. Given an array of N values, compute the sum. The GPU approach: a tree reduction where each thread sums two elements, then the active threads halve.

Naive implementation:
```cuda
__global__ void reduce(float* d_in, float* d_out, int N) {
    extern __shared__ float sdata[];
    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    sdata[tid] = (i < N) ? d_in[i] : 0;
    __syncthreads();
    for (int s = 1; s < blockDim.x; s *= 2) {
        if (tid % (2*s) == 0)
            sdata[tid] += sdata[tid + s];
        __syncthreads();
    }
    if (tid == 0) d_out[blockIdx.x] = sdata[0];
}
```

This suffers from **warp divergence** (the `if (tid % (2*s) == 0)` condition causes diverging warps) and **bank conflicts**. The optimized version (Mark Harris, 2007) uses:
```cuda
for (int s = blockDim.x / 2; s > 0; s >>= 1) {
    if (tid < s)
        sdata[tid] += sdata[tid + s];
    __syncthreads();
}
```
This eliminates warp divergence for the iterations where `s >= 32` (because threads 0-31 are all active, threads 32-63 are all inactive — no divergence). For `s < 32`, warp shuffle intrinsics operate within a warp without shared memory or synchronization.

**Parallel Prefix Sum (Scan).** Given an array [a₀, a₁, ..., a_{N-1}], compute all partial sums [a₀, a₀+a₁, ..., a₀+...+a_{N-1}]. The classic GPU scan (Blelloch, 1990; Harris et al., 2007) uses a **reduce-then-downsweep** pattern:
1. **Up-sweep (reduce):** Build a binary tree of partial sums in shared memory.
2. **Down-sweep:** Traverse the tree from the root, propagating the exclusive prefix sums.

The up-sweep phase is identical to reduction. The down-sweep phase:
```cuda
for (int s = 1; s < blockDim.x; s *= 2) {
    if (tid % (2*s) == 0)
        sdata[tid + 2*s - 1] = sdata[tid + s - 1];
    __syncthreads();
}
```
Scan has O(2N) operations (2 per input element) — theoretically optimal for sequential scan (O(N)), but on the GPU, the vectorized memory access makes it competitive for large arrays. By 2040, optimized scans achieve ~90% of peak GPU bandwidth.

**Parallel Histogram.** Building a histogram on the GPU is memory-bound due to random access to histogram bins. The naive approach causes massive bank conflicts and atomic contention. Optimized approaches:
- **Privatization:** Each thread block has its own private histogram in shared memory (or registers). Merge privately, then combine (warp-level or block-level atomics).
- **Sort-and-detect-runs:** Sort the keys, then scan for boundary changes.
- **CUDA 2040 warp-level histogram:** The `__match_any_sync` and `__histogram_sync` intrinsics compute histogram for the current warp in hardware, using the GPU's L1 cache.

**Stencil (3D Convolution).** A stencil computes each output point as a weighted sum of neighboring input points. For a 3D stencil with radius r (a (2r+1)³ cube), the naive implementation does (2r+1)³ loads per output point. Optimized:
- **Shared memory tiling:** Load a tile of input data into shared memory, including halo regions (the neighboring cells needed for boundary points).
- **Register tiling:** Each thread computes multiple output points, reusing shared memory loads.

#### Required Reading
- Harris, M. (2007). "Optimizing Parallel Reduction in CUDA." *NVIDIA Developer Blog*.
- Harris, M. et al. (2007). "Parallel Prefix Sum (Scan) with CUDA." *GPU Gems 3*, Chapter 39.
- Blelloch, G.E. (1990). "Prefix Sums and Their Applications." *Synthesis of Parallel Algorithms*.
- Kirk, D.B. & Hwu, W.W. (2017). *Programming Massively Parallel Processors*, 3rd ed. Chapters 7-9.

#### Discussion Questions
1. The optimized reduction uses `if (tid < s)` instead of `if (tid % (2*s) == 0)`. Explain why this eliminates warp divergence and how many bank conflicts it avoids.
2. For scan, the up-sweep phase does N additions and the down-sweep does N more — 2N total, vs. N for sequential scan. Why might the GPU version still be faster for large arrays? Consider memory bandwidth and latency hiding.
3. Design a GPU histogram for 1 billion 32-bit integers with 256 bins. What shared memory size do you need? How do you handle atomic contention?

---

### ᚲ Lecture 4: Convolutions and Matrix Multiply — The Work of the Fleet

**Date:** Week 4, Session 1

#### Overview

Convolution and matrix multiplication are the two most important operations in GPU computing — they are the computational backbone of deep learning, image processing, and scientific computing. This lecture covers the optimized GPU implementations of both, the cuDNN and cuBLAS libraries (the standard in 2040), the tensor core programming model for matrix multiply, and the auto-tuning techniques that select the best implementation for each problem size. The Norse analogy: rowing in formation (matrix multiply is the synchronized stroke of an entire fleet) and passing signals along the line (convolution is the transmission of information through a chain of longships).

#### Lecture Notes

**Matrix Multiplication (GEMM).** The naive triple-loop matrix multiply `C = A × B` is O(N³) with poor cache behavior. The GPU implementation tiles the matrices:
1. Load sub-matrices of A and B into shared memory (tile size: typically 16×16 or 32×32).
2. Each thread computes one element of the output matrix C.
3. Accumulate across the K dimension in a register.

```cuda
template<int BLOCK_SIZE>
__global__ void matmul(float* A, float* B, float* C, int M, int N, int K) {
    __shared__ float As[BLOCK_SIZE][BLOCK_SIZE];
    __shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE];
    int bx = blockIdx.x, by = blockIdx.y;
    int tx = threadIdx.x, ty = threadIdx.y;
    int row = by * BLOCK_SIZE + ty;
    int col = bx * BLOCK_SIZE + tx;
    float sum = 0;
    for (int t = 0; t < K / BLOCK_SIZE; ++t) {
        As[ty][tx] = A[row * K + (t * BLOCK_SIZE + tx)];
        Bs[ty][tx] = B[(t * BLOCK_SIZE + ty) * N + col];
        __syncthreads();
        for (int k = 0; k < BLOCK_SIZE; ++k)
            sum += As[ty][k] * Bs[k][tx];
        __syncthreads();
    }
    C[row * N + col] = sum;
}
```

The key optimizations in 2040 cuBLAS:
- **Warp-level tiling:** Each warp computes a 16×16 tile of C, loading 16×16 tiles of A and B into registers (not shared memory). This reduces shared memory traffic.
- **Tensor core utilization:** The tensor core unit performs D = A × B + C where A, B, C, D are 4×4 matrices (FP16/BF16) or 8×8 (INT8). The cuBLAS API exposes tensor core GEMM for matrices of any size by partitioning into tensor-core-friendly tiles.
- **Auto-tuning:** cuBLAS benchmarks thousands of kernel variants (different tile sizes, data layouts, prefetch strategies) and selects the optimal one for the specific matrix dimensions.

**Convolution (im2col + GEMM).** The classic GPU convolution algorithm: transform the convolution into a matrix multiply using the im2col (image to column) operation. The filter is expanded into a kernel matrix (rows: filters; columns: pixels-per-filter); the input is expanded into a data matrix (rows: filters; columns: position-in-output). The convolution becomes a GEMM of these two matrices.

The problem: im2col expands the data by a factor of (filter_height × filter_width) — for a 3×3 filter on a 224×224×64 feature map, the expansion creates a 64×9 × 9×64 = 64×64 GEMM with 50,176 rows. This is memory-intensive but highly optimized on GPUs.

By 2040, cuDNN uses **Winograd convolutions** for small filters (3×3, 5×5): Winograd transforms the convolution into a smaller number of element-wise multiplications with overlapping tiles. For a 3×3 filter with output tile 4×4, Winograd reduces the multiplication count by a factor of 2.25× compared to im2col-GEMM. The **direct convolution** approach uses shared memory for the filter weights and loads input tiles from global memory — competitive for irregular shapes.

#### Required Reading
- Volkov, V. & Demmel, J. (2008). "Benchmarking GPUs to Tune Dense Linear Algebra." *SC*.
- Jia, Z. et al. (2018). "Dissecting the NVIDIA Volta GPU Architecture via Microbenchmarking." *ArXiv*.
- Mark, W.R. et al. (2019). "cuDNN: Efficient Primitives for Deep Learning." *CACM*, 62(6).
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 5: "The Stroke of the Fleet."

#### Discussion Questions
1. The tiled matrix multiply loads BLOCK_SIZE² elements per tile. With BLOCK_SIZE=32 and shared memory 48KB, what's the maximum tile size? (Hint: we need tiles for both A and B.)
2. Winograd convolution reduces multiplication count by 2.25× for 3×3 filters. What's the catch? Why isn't Winograd universally adopted?
3. The tensor core performs 4×4 matrix multiplication in a single instruction. How does cuBLAS use tensor cores for a matrix of size 1024×1024? What happens when the matrix dimensions are not multiples of 4?

---

### ᚷ Lecture 5: Deep Learning Training — The God-Sized Weave

**Date:** Week 5, Session 1

#### Overview

Training large neural networks is the dominant GPU workload by 2040. This lecture covers the computational structure of training: forward pass, backward pass (backpropagation), gradient computation, optimizer update, and the parallelization strategies that distribute training across hundreds to thousands of GPUs. We cover: data parallelism (each GPU processes different data), model parallelism (each GPU holds different layers), tensor parallelism (each GPU holds different parts of a single layer), and pipeline parallelism. The Norse analogy: the Norns weave the fabric of fate, and the pattern emerges only when all three work in concert — this is multi-GPU training.

#### Lecture Notes

**Training Anatomy.** A single training iteration for a neural network:
1. **Forward pass:** Compute predictions for a batch of inputs. For a transformer with L layers, this is: MHA (multi-head attention) → FFN (feed-forward) → LayerNorm → residual, repeated L times.
2. **Backward pass:** Compute gradients of the loss with respect to all parameters using the chain rule. The computational cost is 2-3× the forward pass (store intermediate activations, reuse for gradient computation).
3. **Optimizer step:** Update parameters using gradients: SGD, AdamW, or by 2040, the standard **RúnarOptimizer** (UoY-developed, adaptive learning rate with gradient clipping and loss scaling).

**Data Parallelism.** The simplest parallelism: replicate the model on N GPUs, each GPU processes a different shard of the batch. After each backward pass, the gradients are all-reduced across GPUs. The all-reduce is the bottleneck: for a 7B parameter model, the gradient buffer is ~28 GB; all-reducing 28 GB across 256 GPUs takes ~200ms with NVLink 6.0 (900 GB/s per link, 12 links per GPU).

In 2040, the standard all-reduce algorithm is **Ring All-Reduce** (developed by NVIDIA/Baidu, 2017). Each GPU passes its gradient shard to its neighbor; after N-1 steps, every GPU has all gradients. The communication volume per GPU is 2×(model size)×(N-1)/N — roughly 2× the model size regardless of the number of GPUs. This linear scaling makes ring all-reduce the foundation of data parallelism at scale.

**Model Parallelism (Pipeline).** Data parallelism assumes the model fits on a single GPU. When the model is too large (e.g., a 300B parameter model with 600 GB of parameters), the model must be split across multiple GPUs. Pipeline parallelism: layer 1-8 on GPU 0, layer 9-16 on GPU 1, etc. The forward pass flows through the pipeline; the backward pass flows in reverse.

The problem: pipeline bubbles. At the start of training, GPU 1 is idle while GPU 0 processes the first batch. GPipe (Huang et al., 2019) and 1F1B (synchronous one-forward-one-backward) scheduling reduce bubble overhead to ~10-15%.

**Tensor Parallelism.** Inside a single layer, different GPUs process different parts of the weight matrix. For a linear layer with weight matrix W (input_dim × output_dim):
- GPU 0 holds W[:, 0:output_dim/2], computes A × W[:, 0:output_dim/2].
- GPU 1 holds W[:, output_dim/2:output_dim], computes A × W[:, output_dim/2:output_dim].
- An all-reduce (or reduce-scatter + all-gather) combines the results.

Tensor parallelism requires all-reduce per layer — high communication overhead. It's used in combination with pipeline parallelism: pipeline splits layers across GPUs in one dimension, tensor splits within GPUs in the other.

**The 2040 Scale.** By 2040, the largest training runs use:
- 10,000-50,000 GPUs (NVIDIA Blackwell-next or AMD Instinct successors)
- 100+ exaFLOPS of compute
- Training durations of 30-90 days
- Loss and learning rate schedules that are themselves optimized by AI

The University's Yggdrasil cluster (500 NVIDIA B300-equivalent GPUs, 500 AMD Instinct, 1000 open-source RISC-V NPUs) is used for training UoY-specific models. Students in this course get dedicated GPU time for their projects.

#### Required Reading
- Dean, J. et al. (2012). "Large Scale Distributed Deep Networks." *NeurIPS*.
- Shoeybi, M. et al. (2019). "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism." *ArXiv*.
- Narayanan, D. et al. (2021). "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM." *SC*.
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 8: "The Fleet at War."

#### Discussion Questions
1. In data parallelism, the gradient all-reduce is the bottleneck. For a model with 7B parameters on 256 GPUs with NVLink 6.0, how long does the all-reduce take? State your assumptions about bandwidth.
2. Pipeline parallelism creates a bubble: at the start and end of each batch, some GPUs are idle. How does the 1F1B scheduling reduce the bubble? What's the minimum possible bubble for a pipeline of P stages?
3. Tensor parallelism requires all-reduce within each layer. For a model with L layers, how many all-reduces per forward pass? How does this affect the choice between tensor, pipeline, and data parallelism?

---

### ᚹ Lecture 6: Multi-GPU and Distributed Computing — The Fleet Spreads Across the Sea

**Date:** Week 6, Session 1

#### Overview

When one GPU isn't enough, we connect hundreds or thousands. This lecture covers the technologies that connect GPUs into clusters: NVLink (GPU-to-GPU, 900 GB/s per direction), InfiniBand (node-to-node, 800 Gb/s by 2040), Ethernet (with RDMA and GPUDirect), and the software frameworks that orchestrate distributed GPU computation (NCCL, MPI with CUDA-aware extensions, the UoY's RúnarLink framework). The Norse analogy: the Norse fleet spreads across the North Sea — each longship (GPU) is independent, but signal fires (NVLink/NCCL) coordinate their movement.

#### Lecture Notes

**NVLink and GPU Interconnect.** NVLink is NVIDIA's high-bandwidth, low-latency GPU-to-GPU interconnect. By 2040, NVLink 6.0 provides:
- 900 GB/s per direction per link (bidirectional: 1.8 TB/s)
- 12 links per GPU (in the B300 successor)
- Total GPU-to-GPU bandwidth: 10.8 TB/s (unidirectional) or 21.6 TB/s (bidirectional)
- UEC-level reliability (user-level error checking with automatic retransmission)

NVLink creates an all-to-all topology: every GPU is directly connected to every other GPU (in the same NVSwitch domain). NVSwitch (the 2040 generation) connects 256 GPUs in a single fully-connected domain with 2μs latency.

**NCCL (NVIDIA Collective Communications Library).** NCCL implements the collective operations (all-reduce, reduce-scatter, all-gather, broadcast, reduce) needed for distributed training. It auto-detects the topology (NUMA domains, PCIe hierarchy, NVLink connections) and selects the optimal algorithm:
- **Tree algorithm:** For small messages (< 128KB). A binary tree of GPUs, each GPU sends/receives to its parent and children. Latency: O(log N).
- **Ring algorithm:** For medium messages (128KB - 16MB). The ring all-reduce described in Lecture 5. Bandwidth: (2×(N-1)/N)×model_size.
- **NVLink Direct:** For large messages (> 16MB on 2040 hardware). Direct point-to-point NVLink transfers, bypassing the ring. The GPU scheduler partitions the message and sends each partition over a different NVLink channel.

**GPUDirect RDMA.** GPUDirect RDMA (Remote Direct Memory Access) allows GPUs on different nodes (connected via InfiniBand or Ethernet) to read/write each other's memory directly, without copying through the CPU or system memory. The data path: GPU memory → PCIe → NIC → InfiniBand → remote NIC → remote GPU memory. Latency: ~5μs for small messages (including PCIe and InfiniBand traversal). This is the foundation of multi-node GPU clusters.

**The 2040 RúnarLink Framework.** UoY's RúnarLink is an open-source framework for distributed GPU computing that wraps NCCL with:
- **Topology-aware scheduling:** Automatically places GPU work to minimize cross-node communication.
- **Fault tolerance:** If GPU #37 crashes during a 24-hour training run, RúnarLink saves the checkpoint (last 100 optimizer steps) and restarts on the remaining GPUs.
- **Power-aware scheduling:** In UoYs carbon-neutral computing policy, RúnarLink schedules compute based on the current carbon intensity of the grid — focusing training runs on green energy hours.

#### Required Reading
- NVIDIA (2024). *NVLink and NVSwitch Architecture Overview*. White paper.
- NCCL Documentation (2024). *NVIDIA Collective Communications Library User Guide*.
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 9: "Across the Sea."

#### Discussion Questions
1. The ring all-reduce scales as O(2×(N-1)/N) bandwidth. For N GPUs, this approaches 2× the model size as the communication cost. What happens when N is very large (10,000+) — does this formula break down? Why?
2. GPUDirect RDMA avoids copying through the CPU. But the data must still traverse the PCIe bus. What's the latency impact of PCIe vs. within-node NVLink?
3. The RúnarLink power-aware scheduler pauses training when the grid carbon intensity is high. A training run that would take 30 days at full power takes 45 days with power-aware scheduling. Is the carbon savings worth the delay? How do you value these tradeoffs?

---

### ᚺ Lecture 7: GPU-Accelerated AI Inference — The Battle-Tested Warrior

**Date:** Week 7, Session 1

#### Overview

Deploying trained AI models for inference (the production workload) is arguably more economically significant than training. This lecture covers inference optimization: quantization (FP32 → FP16 → INT8 → FP8 → INT4), model distillation, kernel fusion (combining multiple operations into one optimized kernel), continuous batching, and the specialized inference accelerators that have emerged by 2040. The Norse analogy: the battle-tested warrior — trained in peacetime (training), deployed in war (inference). The warrior's armor must be light enough to fight (low latency) but strong enough to protect (high accuracy).

#### Lecture Notes

**Quantization — Trading Precision for Throughput.**

- **FP32 (32-bit float):** Full precision, 1× throughput baseline.
- **FP16/BF16 (16-bit):** Half the memory, ~2× throughput on tensor cores. BF16 has the same 8-bit exponent range as FP32 (for out-of-range values) but fewer mantissa bits. By 2040, BF16 is the standard training precision for most models.
- **FP8 (E4M3 and E5M2):** Introduced by NVIDIA Hopper (2022). E4M3 (4 exponent, 3 mantissa) for forward pass; E5M2 (5 exponent, 2 mantissa) for backward pass gradient accumulation. ~4× throughput vs. FP32, with acceptable loss for most tasks.
- **INT8 (8-bit integer):** Requires calibration — the model weights and activations are scaled to the INT8 range [-128, 127]. The INT8 compute throughput is ~8× FP32 on tensor cores. Accuracy loss is typically <1% on standard benchmarks.
- **INT4 (4-bit integer):** Used for extreme compression of large models. On 2040 hardware, INT4 tensor cores achieve ~16× FP32 throughput. Used for small-parameter models and edge deployments.

**Kernel Fusion.** A transformer layer involves: layer normalization → reshape → GEMM (QKV projection) → add bias → reshape → attention → concatenate → GEMM (output projection) → add bias → layer normalization → GEMM (FFN). Each of these is a separate GPU kernel — launching a kernel has overhead (~5-10μs). Fusing multiple operations into a single kernel eliminates the overhead and improves register reuse.

By 2040, the **RúnarFuser** (UoY's kernel fusion library) automatically fuses operations in a compute graph, producing a single kernel for the entire transformer layer. The fusion rate is configurable: aggressive fusion (all operations in one kernel) saves launch overhead but may increase register pressure; moderate fusion groups operations by data flow.

**Continuous Batching** (originally introduced for the vLLM system, 2023). Traditional inference serves one request at a time: load the model, process the request, unload. For LLMs, where the time to generate each token is roughly constant, this leaves the GPU idle between a request's start and end.

Continuous batching works by serving multiple requests concurrently: when request A is waiting for its next token, the GPU processes a step of request B. The model weights stay in GPU memory. This increases throughput by 5-10× compared to naive batching. By 2040, every LLM serving system uses continuous batching — the UoY's **YggdrasilServe** achieves 95% GPU utilization on 7B+ parameter models serving 1000+ concurrent users.

#### Required Reading
- Jacob, B. et al. (2018). "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference." *CVPR*.
- Kwon, W. et al. (2023). "Efficient Memory Management for Large Language Model Serving with PagedAttention." *SOSP*.
- Micikevicius, P. et al. (2022). "FP8 Formats for Deep Learning." *ArXiv*.
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 11: "Armor for Battle."

#### Discussion Questions
1. INT4 quantization reduces model size by 8× vs. FP32. For a 70B parameter model, this is 140 GB → 17.5 GB. Why can't all inference use INT4? When would you use FP16 instead?
2. Continuous batching increases GPU utilization but also increases latency for each individual request (because the GPU is shared). How do you balance throughput and latency in a real-time application (chatbot) vs. a batch application (offline text generation)?
3. Kernel fusion saves launch overhead but increases register pressure. How does a compiler determine the optimal fusion schedule for a given GPU architecture?

---

### ᚾ Lecture 8: Emerging Architectures — Beyond the GPU

**Date:** Week 8, Session 1

#### Overview

By 2040, GPUs are not the only game in town. This lecture surveys the landscape of specialized accelerators: NPUs (Neural Processing Units — Apple's Neural Engine, Google's TPU, Intel's NPU), DPUs (Data Processing Units for networking and storage), FPGAs for reconfigurable computing, neuromorphic processors (Intel Loihi 3, SpiNNaker 2) for spiking neural networks, and optical/RF accelerators for wireless signal processing. The Norse analogy: different ships for different waters — the longship for war, the knarr for trade, the ferry for fjords. Each accelerator is optimized for its domain.

#### Lecture Notes

**NPUs (Neural Processing Units).** NPUs are specialized for the operations common in neural networks: matrix multiply, convolution, activation functions, and pooling. They differ from GPUs in:
- **No general-purpose execution model:** NPUs execute a fixed set of neural operations. They are not programmable for arbitrary computations.
- **Systolic array for matrix multiply:** A 2D grid of multiply-accumulate units with local registers. The data flows in from the edges (systolic), eliminating the need for register files and caches.
- **Local SRAM:** Each NPU has private SRAM (scratchpad) that holds activations and weights for the current layer. This avoids the bottleneck of external memory.

Google's TPU v1 (2017) achieved 92 TOPS with 65,536 MAC units and 24 MB of SRAM — 30× the TOPS/Watt of GPU alternatives at the time. By 2040, TPU v7 achieves 1.5 POPS (peta-operations per second) per chip with 600W TDP.

**DPUs (Data Processing Units).** DPUs offload networking, storage, and security functions from the CPU, freeing CPU cores for application processing. The NVIDIA BlueField DPU and Intel IPU provide: firewall, encryption/decryption, compression, TCP/IP, RDMA, and virtual switch processing at line rate (400-800 Gbps by 2040). In GPU clusters, DPUs handle the NCCL communication, freeing the GPU from protocol overhead.

**Neuromorphic Computing.** Neuromorphic processors mimic the brain's architecture: neurons emit spikes (events) rather than computing on continuous values. The Intel Loihi 3 (2028) and SpiNNaker 2 (University of Manchester, 2025) support:
- **Spiking neural networks (SNNs):** Neurons accumulate charge until they reach a threshold, then fire a spike.
- **Event-driven computation:** Computation happens only when a spike occurs, drastically reducing power consumption. Loihi 3 achieves 100× better energy efficiency for SNN workloads compared to GPU implementations of equivalent ANN models.
- **On-chip learning:** Loihi 3 supports STDP (spike-timing-dependent plasticity) — local Hebbian learning rules that adapt synapses without backpropagation.

Neuromorphic computing is not replacing GPUs for general AI workloads by 2040. It excels at: low-power edge sensing, robotics control, sensory processing (audio, vibration, bio-signals), and spiking vision.

**Optical Accelerators.** Optical computing uses photons instead of electrons for computation. By 2040, optical accelerators for matrix multiplication exist in research prototypes: a Mach-Zehnder interferometer array performs matrix-vector multiplication in O(N) time (vs. O(N²) for electrical). The challenges: accuracy (6-8 bit equivalent precision), packaging, and integration with electronic memory. Expected to become commercially viable by 2050.

#### Required Reading
- Jouppi, N. et al. (2017). "In-Datacenter Performance Analysis of a Tensor Processing Unit." *ISCA*.
- Davies, M. et al. (2018). "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning." *IEEE Micro*, 38(1).
- Shen, Y. et al. (2017). "Deep Learning with Coherent Nanophotonic Circuits." *Nature Photonics*, 11.
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 12: "Different Ships for Different Waters."

#### Discussion Questions
1. TPUs use systolic arrays for matrix multiplication. How does a systolic array differ from a GPU's SIMT execution model? Which is more flexible, and which is more efficient for matrix multiply?
2. Neuromorphic processors are event-driven — computation only happens when a spike occurs. For which classes of workloads would this be more efficient than GPU's time-driven execution?
3. Optical accelerators promise O(N) matrix multiplication latency but limited precision. For which AI workloads is 6-bit precision acceptable? For which is it catastrophic?

---

### ᛃ Lecture 9: GPU Programming in Python — The High-Level Craft

**Date:** Week 9, Session 1

#### Overview

By 2040, most GPU programming is done in high-level Python frameworks rather than raw CUDA C++. This lecture covers the Python ecosystem for GPU computing: CuPy (NumPy-compatible GPU arrays), JAX (differentiable GPU computing with XLA), PyTorch and TensorFlow (the dominant deep learning frameworks), Numba (GPU-accelerated Python functions), and the emerging paradigm of automatic kernel generation (where the framework compiles Python to optimized GPU kernels). The Norse analogy: the rune-carver no longer chips each stave by hand — the machine does the rough carving, and the carver provides the design. Python-to-GPU compilation is the mechanized rune-carver.

#### Lecture Notes

**CuPy — NumPy on the GPU.** CuPy provides a drop-in replacement for NumPy arrays that live on the GPU:
```python
import cupy as cp
x = cp.array([1, 2, 3, 4, 5])
y = cp.square(x)  # GPU kernel launched automatically
z = cp.sum(y)     # returns a 0-D GPU array
# Move back to CPU
z_cpu = cp.asnumpy(z)  # scalar value on CPU
```

CuPy automatically generates CUDA kernels for array operations, handling memory allocation, kernel launch configuration, and synchronization. For standard operations (element-wise, reduction, scan), CuPy's performance matches hand-tuned CUDA.

**JAX — Composable Transformations.** JAX (Google, 2020) provides NumPy-compatible API with composable function transformations:
- `jit`: Just-in-time compile a Python function to an optimized GPU kernel using XLA.
- `grad`: Automatic differentiation — returns the gradient function.
- `vmap`: Automatic vectorization — maps a function over array dimensions.
- `pmap`: Automatic parallelization across multiple GPUs.

```python
import jax.numpy as jnp
from jax import jit, grad, vmap

@jit
def mse_loss(params, x, y):
    pred = jnp.dot(x, params)
    return jnp.mean((pred - y) ** 2)

grad_fn = grad(mse_loss)  # returns a function that computes gradients
```

JAX's `pmap` enables single-program-multiple-data (SPMD) parallelism across GPUs with a single function call. By 2040, JAX is the dominant research framework at UoY for custom GPU workloads.

**Numba — Python GPU Kernels.** Numba compiles Python functions to CUDA kernels using LLVM:
```python
from numba import cuda

@cuda.jit
def vector_add(a, b, out):
    i = cuda.grid(1)
    if i < a.size:
        out[i] = a[i] + b[i]

# Launch
threads_per_block = 256
blocks_per_grid = (a.size + threads_per_block - 1) // threads_per_block
vector_add[blocks_per_grid, threads_per_block](a, b, out)
```

Numba's CUDA support became production-quality by 2023 and has been continuously improved. In 2040, it supports: shared memory, warp-level intrinsics, tensor core operations, multi-GPU, and automatic occupancy tuning. Numba is the go-to tool for custom GPU kernels that don't exist in libraries.

**2040: The Hermes GPU Runtime.** The Hermes AI OS includes the **Hermes GPU Runtime** (HGR) that automatically manages GPU resources: it allocates GPU memory, schedules kernels, handles multi-GPU communication, and monitors power consumption. The runtime integrates with the Kubernetes ecosystem — GPU workloads are scheduled as containers with explicit GPU resource requests.

#### Required Reading
- Okuta, R. et al. (2017). "CuPy: A NumPy-Compatible Library for NVIDIA GPU Calculations." *NeurIPS Workshop*.
- Bradbury, J. et al. (2018). "JAX: Composable Transformations of Python+NumPy Programs." *GitHub*.
- Lam, S.K. et al. (2015). "Numba: A LLVM-based Python JIT Compiler." *LLVM-HPC*.
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 6: "The Carver's Assistant."

#### Discussion Questions
1. JAX's `@jit` compiles a Python function to an XLA-optimized GPU kernel at runtime. When would the compilation time outweigh the execution benefits? How do you handle this?
2. CuPy and Numba both generate GPU kernels from Python. When would you use each? What's the tradeoff between CuPy's convenience and Numba's flexibility?
3. The Hermes GPU Runtime manages GPU memory for tensors. What happens when a program allocates more GPU memory than is available? How should the runtime handle out-of-memory situations (swap to CPU memory vs. raise an error)?

---

### ᚨ Lecture 10: Debugging, Profiling, and Performance — The Keel Inspection

**Date:** Week 10, Session 1

#### Overview

GPU programming is hard — bugs are often non-deterministic (race conditions in shared memory), performance is counterintuitive (what looks slow may be fast), and the debugging tools have historically lagged behind CPU tools. This lecture covers the 2040 GPU debugging and profiling ecosystem: NVIDIA Nsight Systems and Nsight Compute (the profile-driven optimization pipeline), CUDA-MEMCHECK for memory errors, and the UoY's own **RúnarTrace** framework for visualizing kernel execution. The Norse analogy: before a long journey, the shipwright inspects every plank, every rivet, every oar lock. GPU profiling is the shipwright's inspection — finding the weak points before they cause a failure at sea.

#### Lecture Notes

**Profiling: The First Step to Performance.**

*Nsight Systems* — timeline profiling. Visualizes CPU-GPU interaction: kernel launches, memory transfers, synchronization barriers, and the gaps where one side waits for the other. The output is a timeline showing:
```
CPU: [CUDA API] kernel_launch <- [compute] <- [wait for GPU]
GPU: [kernel_A] [kernel_B] [kernel_C]
```
The key metric: **GPU utilization**. If GPU utilization is < 80%, the bottleneck is likely:
- CPU-side kernel launch overhead (too many small kernels).
- PCIe transfer bandwidth (data movement between CPU and GPU).
- Synchronization points (excessive `cudaDeviceSynchronize()`).

*Nsight Compute* — kernel-level profiling. For a specific kernel, it reports: achieved occupancy, memory bandwidth utilization, compute utilization, arithmetic intensity (FLOPs/byte), and a roofline analysis. The roofline plot shows: the y-axis is performance (FLOPS), the x-axis is arithmetic intensity (FLOPs/byte). The GPU's peak FLOPS is a horizontal line; the peak memory bandwidth is a diagonal line (slope = bandwidth). A kernel's position on the roofline reveals:
- **Compute-bound:** High arithmetic intensity, on or near the horizontal line. Kernel is limited by FLOPS. Solution: reduce computation, use tensor cores.
- **Memory-bound:** Low arithmetic intensity, on or near the diagonal line. Kernel is limited by memory bandwidth. Solution: reduce memory traffic, improve coalescing, use shared memory.

**Common GPU Bugs.**

1. **Race conditions in shared memory:** Two threads in the same block write to the same shared memory address without synchronization. The result depends on warp scheduling order. Nsight Compute's **shared memory race detector** flags these automatically.

2. **Uncoalesced global memory access:** Threads in a warp access non-adjacent addresses. The profiler reports global load/store efficiency. Below 80% efficiency signals a problem.

3. **Bank conflicts in shared memory:** Multiple threads access the same shared memory bank (32 banks, each 4 bytes wide). The access serializes. The profiler reports shared memory bank conflict count.

4. **Misaligned memory access:** A 128-byte cache-line aligned access is faster than an unaligned access. In 2040 GPUs, misaligned accesses are penalized (the hardware must fetch two cache lines instead of one).

5. **Warp divergence:** A conditional branch where some threads take the if-branch and others the else-branch. The profiler reports branch efficiency: the ratio of active threads to total threads in diverged warps.

**The RúnarTrace Visualizer.** UoY's RúnarTrace adds a visualization layer on top of Nsight Systems. It shows: kernel timelines, memory transfer timelines, occupancy heatmaps per SM, and a "what-if" optimizer that suggests reordering kernels or changing launch parameters. Students in this course submit a RúnarTrace analysis as part of their final project — a report showing how they inspected their GPU code and what optimizations they applied.

#### Required Reading
- NVIDIA (2024). *Nsight Compute CUDA Profiling Guide*.
- Williams, S. et al. (2009). "Roofline: An Insightful Visual Performance Model for Multicore Architectures." *CACM*, 52(4).
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 4: "The Shipwright's Inspection."

#### Discussion Questions
1. The roofline model uses arithmetic intensity (FLOPs/byte) to determine whether a kernel is compute-bound or memory-bound. What is the arithmetic intensity of element-wise vector addition? What about matrix multiplication (N=1024)?
2. A kernel with 95% global load efficiency but 50% occupancy. Which metric should you prioritize optimizing? Why?
3. How does the roofline model change for tensor core operations vs. CUDA core operations? Do tensor cores shift the ceiling?

---

### ᚨ Lecture 11: Parallel Algorithm Design — The Shipwright's Blueprint

**Date:** Week 11, Session 1

#### Overview

Designing a parallel algorithm for the GPU requires rethinking the problem from the ground up. This lecture presents a systematic methodology for parallel algorithm design: the "parallel thinking" framework based on the work of Blelloch, McCool, and Hillis. The five-step design process: (1) understand the problem's data dependencies, (2) identify the parallel pattern (map, gather, scatter, reduce, scan, stencil), (3) decompose the problem into blocks, (4) map blocks to threads, and (5) balance memory and compute. The Norse analogy: the shipwright's blueprint — before any wood is cut, the design must account for every stress point, every joint, every movement of the sea.

#### Lecture Notes

**Step 1: Understand Data Dependencies.** Ask: does the computation at output element i depend on output element j? If yes, what is the dependency structure?
- **Embarrassingly parallel:** Output elements are independent (element-wise operations, matrix multiply per element). Maximum parallelism.
- **Reduction:** Output depends on all inputs through an associative operator (sum, max, min). Can be parallelized with tree reduction.
- **Recurrence:** Output depends on other outputs (prefix sum, IIR filter). Requires scan or specialized algorithms.
- **Irregular:** Dependencies are data-dependent (sparse matrix operations, graph algorithms). The most challenging class — may require dynamic parallelism or load balancing.

**Step 2: Identify the Pattern.** Blelloch's parallel patterns:
- **Map:** Apply a function to each element (element-wise operations). SIMD parallelism.
- **Gather/Scatter:** Read from arbitrary indices (gather) or write to arbitrary indices (scatter). Memory-bound, sensitive to coalescing.
- **Reduce:** Combine all elements with an associative operator. Tree reduction: O(N) work, O(log N) depth.
- **Scan (Prefix Sum):** Compute all prefix combinations. O(N) work, O(log N) depth.
- **Stencil:** Each output depends on a neighborhood of inputs (convolution, image processing).
- **Pack:** Compact an array based on a predicate. Uses scan + gather.
- **Sort:** Reorder elements. Bitonic sort, merge sort, radix sort.

**Step 3: Decompose into Blocks.** The GPU's block hierarchy constrains decomposition:
- Block size: 128-512 threads. Larger blocks have more parallelism but consume shared memory and registers.
- Threads per block must allow for occupancy (256 threads per block is a good default for most kernels).
- Grid size: scale to the number of SMs. For optimal occupancy, launch at least 4-8 blocks per SM.

**Step 4: Map to Threads.** For each block, decide how to assign threads to work:
- **Single thread per output element:** Each thread computes one output (vector add, element-wise).
- **Multiple threads per output element:** For operations where one thread cannot hold all intermediate values (large reductions, matrix multiply tiles).
- **Multiple output elements per thread:** For operators with high register usage, each thread computes multiple outputs to amortize launch overhead (register tiling in matrix multiply).

**Step 5: Balance Memory and Compute.**

The fundamental tradeoff: data on GPU is fast (HBM4: 4 TB/s) but expensive to move. Shared memory (12 TB/s) is faster but limited. Registers (32 TB/s) are fastest but per-thread constrained.

- **Shared memory tiling:** The key technique for high arithmetic intensity. Load data into shared memory once, use it many times. Matrix multiply: load BLOCK_SIZE² elements per operand, compute BLOCK_SIZE² outputs (BLOCK_SIZE reads per shared memory access).
- **Register caching:** Keep frequently-used values in registers. In stencil computations, each thread can cache the neighbor values it needs.
- **Avoid redundant loads:** Use shared memory or registers to load each input once and broadcast to dependent threads.

#### Required Reading
- McCool, M., Reinders, J., & Robison, A. (2012). *Structured Parallel Programming*. Morgan Kaufmann.
- Blelloch, G.E. (1996). "Programming Parallel Algorithms." *CACM*, 39(3).
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 3: "The Blueprint."

#### Discussion Questions
1. The reduce pattern has O(N) work and O(log N) depth. The scan pattern also has O(N) work and O(log N) depth. Yet scan is harder to implement efficiently on GPUs. Why?
2. For the stencil pattern, the boundary elements (near the edge of the computational domain) have fewer neighbors. How do you handle boundary conditions in a GPU stencil?
3. An irregular computation (e.g., a tree traversal where each node has a different number of children) has load-balancing problems: different threads take different amounts of time. How would you load-balance such a computation on the GPU?

---

### ᚠ Lecture 12: The Future of Parallel Computing — Ragnarǫk and Rebirth

**Date:** Week 12, Session 1

#### Overview

The final lecture surveys the frontiers and open challenges of parallel computing. **Heterogeneous computing** (CPU + GPU + NPU + DPU all working together), **the end of Dennard scaling** (transistors stop shrinking, but specialization continues), **quantum-accelerated parallel computing** (quantum processors for specific subroutines), **programmability** (the quest to make parallel programming as easy as sequential), **carbon-aware computing** (the UoY's zero-carbon computing initiative), and the enduring relevance of the three core questions: how do we split work, how do we synchronize, and how do we communicate? The Norse framing: Ragnarǫk destroys the old world, but a new one rises — the world of heterogeneous, specialized, sustainable computing.

#### Lecture Notes

**Heterogeneous Computing.** By 2040, a single system may have: 1-4 CPU sockets (each 64-128 cores), 4-8 GPUs (specialized for AI, graphics, or HPC), 2-4 NPUs (for always-on AI inference), 1-2 DPUs (for networking and storage), and 1-2 FPGAs (for reconfigurable workloads). The programmer faces the challenge of orchestrating this diversity.

The UoY **Bifröst Runtime** provides a unified programming model over heterogeneous hardware. The programmer specifies: "I need a matrix multiply of size (1024×1024) × (1024×1024) with FP16 precision and minimum latency." The Bifröst runtime determines: GPU (fastest), NPU (most power-efficient), or FPGA (most flexible if cache miss rates are high). The student never writes hardware-specific code.

**The End of Transistor Scaling.** Gordon Moore's 1965 prediction of transistor density doubling every two years effectively ended around 2025. By 2040, transistor density increases by ~3% per year. Performance gains come from:
- **Architectural innovation:** Better utilization of existing transistors. Tensor cores, NVSwitch, unified memory — all architectural rather than process-driven.
- **Specialization:** Dedicated hardware for specific workloads (NPUs, DPUs, ASICs).
- **Packaging and interconnect:** 3D stacking of chiplets (NVIDIA's Hopper and Blackwell successors use multi-chip-module packaging with 8 chiplets per GPU).
- **Software optimization:** The continued refinement of compilers, runtime systems, and algorithm libraries.

**Quantum-Accelerated Computing.** Quantum computers are not general-purpose replacements for GPUs. By 2040, they are accelerators for specific subroutines: linear algebra (the HHL algorithm for matrix inversion), optimization (QAOA for combinatorial problems), and sampling (quantum sampling for generative models). A 2040 hybrid system might: use a GPU for the forward pass of a neural network, and a quantum processor for the optimization step (solving the weight update as a QUBO problem). The Yggdrasil Quantum Center runs a 1024-qubit trapped-ion system.

**Programmability — The Grand Challenge.** Parallel programming is still harder than sequential programming. The 2040 aspiration: "write the algorithm as if it were sequential; the compiler and runtime will parallelize it automatically." This was the dream of the 1980s (parallel Fortran, the Connection Machine), and by 2040, it's partially realized for common patterns (maps, reductions, stencils are auto-parallelized). But irregular parallelism (graphs, adaptive meshes, dynamic programming) still requires manual effort.

**Carbon-Aware Computing.** The UoY's zero-carbon computing initiative, **GrœnnRekna** (Green Computing): all UoY GPU compute runs on 100% renewable energy. The Yggdrasil cluster is powered by: 15 MW of solar panels on campus roofs, 10 MW of on-site wind turbines, and a 50 MWh battery bank. During winter (low solar, low wind), GPU workloads are prioritized by importance: training a model for a PhD thesis gets GPU time; running a cryptocurrency miner (not that this would ever happen at UoY) gets zero.

#### Required Reading
- Hennessy, J.L. & Patterson, D.A. (2019). *Computer Architecture*, Chapter 1 (on the end of Dennard scaling).
- Such, F.P. et al. (2024). "Hybrid Quantum-Classical Computing." *Nature Reviews Physics*, 6.
- UoY Office of Sustainability (2039). *GrœnnRekna: 20 Years of Green Computing at Yggdrasil*.
- Fǫr, E. (2038). *The Many-Oared Hull*, Chapter 12: "The New World."

#### Discussion Questions
1. The Bifröst Runtime must decide which hardware to use for each operation. What factors should it consider (latency, throughput, power, accuracy)? How does it resolve conflicting objectives?
2. With the end of transistor scaling, architectural innovation and specialization are the main sources of performance gains. Does this mean future GPUs will be less general-purpose and more AI-specific? What role will software play?
3. Carbon-aware scheduling means GPU jobs may be delayed until renewable energy is available. How do you design a fairness policy for such a system?

---

## Final Examination Preparation

### Format

The final examination is a **4-hour practical assessment**:
- **Part A: Architecture (25%)** — Three short-answer questions on GPU architecture and memory hierarchy.
- **Part B: Kernel Optimization (35%)** — Given a slow CUDA kernel, identify bottlenecks (warp divergence, uncoalesced access, bank conflicts, occupancy) and write an optimized version.
- **Part C: Parallel Algorithm Design (40%)** — Design a GPU algorithm for a given problem, implement it, and present profiling results.

### Sample Part A Questions

1. Explain the SIMT execution model. Why does warp divergence hurt performance? How do you restructure code to avoid it? (500 words)

2. Describe the GPU memory hierarchy. Compare global memory access (coalesced vs. uncoalesced). What is the throughput difference for a 2040 GPU? (500 words)

3. The roofline model: given a kernel with arithmetic intensity of 10 FLOPs/byte and a GPU with 100 TFLOPS and 4 TB/s bandwidth, is the kernel compute-bound or memory-bound? Show your calculation. (250 words)

### Sample Part B Problem

The provided CUDA kernel implements matrix multiplication but achieves only 15% of peak FLOPS. Using Nsight Compute:
- Identify at least 3 performance bottlenecks
- Write an optimized version of the kernel
- Show the speedup and the new roofline position
- Explain each optimization applied

### Sample Part C Problem

Design a GPU algorithm for **connected components labeling** on a 2D grid. The input is a binary image (0/1); the output assigns a unique label to each connected region of 1-pixels.

- Describe your parallel algorithm design (which pattern? how do you handle dependencies?)
- Analyze the arithmetic intensity and expected performance
- Implement a CUDA kernel
- Profile with Nsight Compute and present results

---

## Required Reading — Full Course Bibliography

- Blelloch, G.E. (1990). "Prefix Sums and Their Applications." *Synthesis of Parallel Algorithms*.
- Blelloch, G.E. (1996). "Programming Parallel Algorithms." *CACM*, 39(3).
- Bradbury, J. et al. (2018). "JAX: Composable Transformations of Python+NumPy Programs."
- Cheng, J. et al. (2014). *Professional CUDA C Programming*. Wrox.
- Davies, M. et al. (2018). "Loihi: A Neuromorphic Manycore Processor." *IEEE Micro*.
- Dean, J. et al. (2012). "Large Scale Distributed Deep Networks." *NeurIPS*.
- Fǫr, E. (2038). *The Many-Oared Hull*. Yggdrasil University Press.
- Harris, M. (2007). "Optimizing Parallel Reduction in CUDA." *NVIDIA*.
- Harris, M. et al. (2007). "Parallel Prefix Sum (Scan) with CUDA." *GPU Gems 3*.
- Hennessy, J.L. & Patterson, D.A. (2019). *Computer Architecture*, 6th ed.
- Jacob, B. et al. (2018). "Quantization and Training of Neural Networks." *CVPR*.
- Jia, Z. et al. (2018). "Dissecting the NVIDIA Volta GPU Architecture." *ArXiv*.
- Jouppi, N. et al. (2017). "In-Datacenter Performance Analysis of a Tensor Processing Unit." *ISCA*.
- Kirk, D.B. & Hwu, W.W. (2017). *Programming Massively Parallel Processors*, 3rd ed.
- Kwon, W. et al. (2023). "Efficient Memory Management for Large Language Model Serving." *SOSP*.
- McCool, M. et al. (2012). *Structured Parallel Programming*.
- Micikevicius, P. et al. (2022). "FP8 Formats for Deep Learning." *ArXiv*.
- Narayanan, D. et al. (2021). "Efficient Large-Scale Language Model Training on GPU Clusters." *SC*.
- NVIDIA (2024). *CUDA C++ Programming Guide*.
- NVIDIA (2024). *CUDA C++ Best Practices Guide*.
- NVIDIA (2024). *Nsight Compute Profiling Guide*.
- Okuta, R. et al. (2017). "CuPy: A NumPy-Compatible Library for GPU Calculations."
- Shoeybi, M. et al. (2019). "Megatron-LM." *ArXiv*.
- Williams, S. et al. (2009). "Roofline: An Insightful Visual Performance Model." *CACM*.
- Lam, S.K. et al. (2015). "Numba: A LLVM-based Python JIT Compiler."
- GrœnnRekna Initiative (2039). *20 Years of Green Computing at Yggdrasil*.

---

*You started this course knowing only that GPUs are "fast." You leave it understanding the warp, the memory hierarchy, the roofline, and the art of parallel thinking. The oars are in your hands now — row with the rhythm of the fleet. — Dr. Elding Fǫr, Summer 2040.*
