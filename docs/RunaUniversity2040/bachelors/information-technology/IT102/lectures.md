# IT102: Computer Hardware & Architecture
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4  
**Description:** Computer Hardware & Architecture

**Prerequisites:** IT101 (Introduction to Information Technology) or concurrent enrollment

**Instructor:** Prof. Magni Hreðarsón, Department of Information Technology

---

## Lectures

---

### Lecture 1: From Electrons to Computation — The Physical Foundation of IT

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Every computation, every byte stored, every packet transmitted is ultimately a manipulation of electrons, photons, or quantum states in physical matter. This lecture establishes the physical foundations of digital computing: semiconductor physics, logic gates, binary representation, and the von Neumann architecture that has defined computers for eight decades. Understanding these foundations is essential for IT professionals who must diagnose hardware failures, evaluate new technologies, and communicate with vendors and engineers.

#### Key Topics

- **Semiconductor Physics:** Silicon-based transistors operate by controlling the flow of electrons through doped semiconductor material. Moore's Law — the observation that transistor density doubles approximately every two years — held for six decades but slowed in the 2010s as physical limits approached. By 2040, transistor sizes have reached the 1–2 nanometer node, where quantum tunneling and atomic-scale variability make further scaling increasingly difficult and expensive.
- **Binary Logic and Boolean Algebra:** All digital computation is built on binary logic: AND, OR, NOT, XOR, NAND, NOR gates. Boolean algebra (devised by George Boole in 1847, applied to circuits by Claude Shannon in 1938) provides the mathematical framework for circuit design. Combinational logic (output depends only on current inputs) and sequential logic (output depends on inputs and internal state, i.e., memory) are the two fundamental categories.
- **The von Neumann Architecture:** Proposed in 1945, this architecture consists of: a central processing unit (CPU) containing an arithmetic logic unit (ALU) and control unit; memory that stores both data and instructions; input/output mechanisms; and a bus system that connects them. The "stored program" concept — instructions as data — is the defining feature. By 2040, von Neumann remains the dominant paradigm, though specialized architectures (neuromorphic, quantum, dataflow) address specific workloads.
- **Clocks and Synchronization:** Digital circuits operate on clock cycles. Clock frequency (measured in GHz) determines how many operations per second the CPU can initiate. However, higher frequencies increase power consumption and heat generation. Modern CPUs use dynamic frequency scaling (Intel Turbo Boost, AMD Precision Boost) to balance performance and energy.
- **Power and Thermal Constraints:** Power consumption (measured in Watts) and thermal design power (TDP) are critical constraints. A data center rack consuming 30 kW requires sophisticated cooling. By 2040, liquid cooling (direct-to-chip, immersion) is standard for high-density deployments, and the UoY Heimdall-1 data center uses geothermal cooling to achieve a PUE of 1.08.

#### Lecture Notes

The IT professional does not need to design transistors, but they must understand the trade-offs that transistor-level decisions impose on system-level behavior. A CPU with higher clock speed may have lower per-thread performance due to shallower pipelines. A memory technology with higher bandwidth may have higher latency. A storage technology with lower cost per gigabyte may have lower endurance. These trade-offs are the essence of systems thinking.

The UoY Hardware Laboratory maintains a collection of historical processors (Intel 4004, MOS 6502, Intel 80386, Pentium 4, Core i9-13900K, AMD Ryzen 9 9950X) that students can examine and benchmark. The lab's motto: *"To understand where we are, we must touch where we have been."*

#### Required Reading

- Hennessy, J. L., & Patterson, D. A. (2037). *Computer Organization and Design: The Hardware/Software Interface* (8th ed.). Morgan Kaufmann.
- IEEE. (2038). *International Roadmap for Devices and Systems (IRDS): Beyond CMOS*.

#### Discussion Questions

1. Moore's Law has slowed but not stopped. What technologies (3D stacking, chiplets, new materials) are extending semiconductor scaling, and what are their limitations?
2. The von Neumann architecture has persisted for 80 years despite alternatives. What makes it so resilient, and what workloads genuinely require non-von Neumann architectures?
3. A data center operator must choose between air cooling and liquid immersion cooling for a new AI training cluster. What factors determine the optimal choice?

#### Practice Problems

- Calculate the total power consumption and cooling requirements for a rack of 40 servers, each with a 350W TDP CPU, 400W GPU, 64GB RAM (5W per DIMM), and 4 NVMe SSDs (7W each).
- Research the die size, transistor count, and process node of three modern CPUs. Plot transistor density versus year and comment on the trend.
- Design a simple 4-bit ALU using logic gates. Specify the operations (ADD, SUB, AND, OR, NOT) and the control signals required.

---

### Lecture 2: CPU Architecture — The Brain of the System

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

The central processing unit is the most complex integrated circuit ever manufactured, containing billions of transistors organized into cores, caches, pipelines, and control logic. This lecture examines CPU architecture in depth: instruction set architectures (ISAs), microarchitecture, pipelining, superscalar execution, out-of-order execution, and the design trade-offs that define modern processors.

#### Key Topics

- **Instruction Set Architectures (ISAs):** The ISA defines the interface between software and hardware: the instructions the CPU can execute, the registers available, the memory model, and the calling convention. Dominant ISAs in 2040:
  - **x86-64:** The legacy ISA from Intel and AMD, dominant in servers and desktops. Complex instruction set computing (CISC) with variable-length instructions and extensive backward compatibility (decades of legacy).
  - **ARM64 (AArch64):** The reduced instruction set computing (RISC) ISA dominant in mobile devices and increasingly in servers (AWS Graviton-5, Ampere Altra-Max-2). Simpler instructions, better power efficiency, and a growing software ecosystem.
  - **RISC-V:** The open-source ISA, increasingly used in embedded systems, AI accelerators, and academic research. Custom extensions allow domain-specific optimizations.
- **Microarchitecture:** The implementation of an ISA in silicon. Key components:
  - **Pipelining:** Dividing instruction execution into stages (fetch, decode, execute, memory, writeback) so multiple instructions can be in flight simultaneously. Pipeline depth varies (5–20 stages) with trade-offs between clock speed and branch misprediction penalty.
  - **Superscalar Execution:** Issuing multiple instructions per clock cycle. Modern CPUs are 4-wide to 8-wide (4–8 instructions dispatched simultaneously).
  - **Out-of-Order Execution (OoO):** Executing instructions in an order that maximizes resource utilization, rather than program order. Requires complex reorder buffers, reservation stations, and register renaming.
  - **Branch Prediction:** Speculating which direction a conditional branch will take. Modern predictors (TAGE, perceptron-based) achieve >95% accuracy, but mispredictions still cost 10–20 cycles.
  - **Cache Hierarchy:** L1 (32–64 KB, 1–2 ns), L2 (256 KB–1 MB, 3–5 ns), L3 (8–64 MB shared, 10–20 ns). Cache misses to main memory cost 100+ cycles, making cache efficiency critical.
- **Multi-Core and Many-Core:** Modern CPUs contain 8–128 cores per socket. Multi-core scaling is limited by Amdahl's Law: serial portions of a program limit maximum speedup. Thread synchronization (locks, atomics, memory barriers) introduces overhead and complexity.

#### Lecture Notes

The IT professional's relationship with the CPU is one of performance monitoring and tuning. Tools like `perf`, `vtune`, `AMD uProf`, and hardware performance counters (cycles, instructions, cache misses, branch mispredictions) reveal how efficiently software uses the hardware. A common IT task: a database query is slow. Is it CPU-bound (high IPC, few cache misses), memory-bound (low IPC, high cache misses), or I/O-bound (low CPU utilization, high I/O wait)?

CPU selection for servers in 2040 involves balancing: per-core performance (for single-threaded workloads), core count (for parallel workloads), power efficiency (for density and cooling), ISA compatibility (for legacy software), and cost. The UoY Heimdall-1 data center uses a heterogeneous mix: x86-64 for legacy enterprise workloads, ARM64 for web services and containers, and RISC-V for research and embedded edge nodes.

#### Required Reading

- Hennessy, J. L., & Patterson, D. A. (2037). *Computer Architecture: A Quantitative Approach* (8th ed.). Morgan Kaufmann.
- Agner Fog. (2038). *The Microarchitecture of Intel, AMD and VIA CPUs: An Optimization Guide for Assembly Programmers and Compiler Makers*.

#### Discussion Questions

1. ARM64 servers are cheaper and more power-efficient than x86-64, but many enterprise applications are compiled only for x86-64. How do you evaluate the business case for migrating to ARM64?
2. Out-of-order execution improves performance but increases power consumption and vulnerability to side-channel attacks (Spectre, Meltdown). Are the performance benefits worth the security risks?
3. A database administrator notices that a query uses only 10% of CPU but takes 10 minutes. What metrics would you examine to determine whether the bottleneck is CPU, memory, disk, or network?

#### Practice Problems

- Use `perf stat` (Linux) or equivalent to benchmark a CPU-intensive program (e.g., compression, matrix multiplication). Report cycles, instructions, IPC, cache misses, and branch mispredictions.
- Compare the single-threaded and multi-threaded performance of a program on a 16-core CPU. Plot speedup versus thread count and explain deviations from ideal scaling.
- Research the microarchitecture of a recent CPU (Intel Granite Rapids, AMD Turin, or ARM Neoverse V3). Write a 1,000-word summary of its pipeline, cache hierarchy, and distinguishing features.

---

### Lecture 3: Memory Systems — The Speed of Thought

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Memory is the workspace of computation. No matter how fast the CPU, it is limited by how quickly it can access data. This lecture examines memory technologies, hierarchy, and management: DRAM organization, cache coherence, virtual memory, and emerging memory technologies that blur the boundary between memory and storage.

#### Key Topics

- **DRAM Technology:** Dynamic random-access memory stores each bit as a charge in a capacitor accessed by a transistor. DRAM requires periodic refreshing (reading and rewriting) to maintain data. Key parameters: capacity (GB per DIMM), bandwidth (GB/s per channel), latency (CAS latency, measured in nanoseconds), and channel count (modern servers have 8–12 channels). DDR5 (introduced 2021) and DDR6 (introduced 2032) have increased bandwidth but at the cost of higher latency.
- **Memory Hierarchy:** The gap between CPU speed and memory speed has widened for decades. The hierarchy mitigates this:
  - **Registers:** CPU-internal, sub-nanosecond access.
  - **L1 Cache:** Split into instruction (L1i) and data (L1d), 32–64 KB, 1–2 ns.
  - **L2 Cache:** 256 KB–1 MB per core, 3–5 ns.
  - **L3 Cache:** 8–64 MB shared across cores, 10–20 ns.
  - **DRAM:** 10–100 GB per server, 100 ns.
  - **SSD/NVMe:** 100 μs–1 ms.
  - **HDD:** 5–10 ms.
  The principle of locality (temporal: recently accessed data is likely to be accessed again; spatial: nearby data is likely to be accessed) makes caching effective.
- **Cache Coherence:** In multi-core systems, each core has private caches (L1, L2). When one core writes to a memory location, other cores' caches must be updated or invalidated to maintain consistency. Protocols: MESI (Modified, Exclusive, Shared, Invalid) and its variants (MOESI, MESIF). Cache coherence traffic consumes interconnect bandwidth and can become a bottleneck for workloads with high shared-data access.
- **Virtual Memory:** The OS abstracts physical memory into virtual address spaces, enabling: process isolation, memory overcommitment, and demand paging (loading memory pages from disk only when accessed). The translation lookaside buffer (TLB) caches virtual-to-physical mappings. TLB misses are expensive, requiring a page table walk (potentially multiple DRAM accesses).
- **Emerging Memory Technologies:**
  - **HBM (High Bandwidth Memory):** 3D-stacked DRAM integrated with the CPU/GPU package. Used in AI accelerators and high-performance computing. HBM4 (2036) provides 2 TB/s bandwidth per stack.
  - **CXL (Compute Express Link):** A cache-coherent interconnect that allows CPUs to access memory on remote nodes or accelerators as if it were local. CXL 4.0 (2038) enables petabyte-scale memory pools shared across a data center.
  - **Persistent Memory (Intel Optane, replaced by CXL-attached SCM):** Memory that retains data without power, blurring the line between DRAM and SSD. Used for large in-memory databases and fast recovery.

#### Lecture Notes

Memory is often the bottleneck in modern systems. A CPU can execute billions of instructions per second, but if it spends most of its time waiting for data from DRAM, effective performance collapses. The IT professional must understand memory topology: how many channels, how many DIMMs per channel, interleaving configuration, and NUMA (Non-Uniform Memory Access) layout. A misconfigured server — e.g., populating only half the memory channels — can lose 30% of memory bandwidth.

The UoY Hardware Laboratory teaches students to read motherboard schematics and BIOS settings to optimize memory configuration. A capstone project in IT102 requires students to benchmark a workload under different memory configurations and quantify the impact.

#### Required Reading

- Jacob, B., Ng, S., & Wang, D. (2036). *Memory Systems: Cache, DRAM, Disk* (2nd ed.). Morgan Kaufmann.
- CXL Consortium. (2038). *CXL 4.0 Specification and System Architecture*.

#### Discussion Questions

1. A server has 12 memory channels but only 6 DIMMs installed. The administrator argues that capacity is sufficient. What performance impact does this configuration have, and how do you persuade them to populate all channels?
2. CXL enables memory disaggregation — sharing memory across servers. What are the latency implications, and for what workloads is this beneficial versus prohibitive?
3. Persistent memory retains data across reboots but has higher latency than DRAM. How do you design an application that leverages persistent memory's durability without sacrificing performance for hot data?

#### Practice Problems

- Write a program that deliberately causes cache thrashing (rapidly accessing memory locations that map to the same cache set). Measure the performance degradation compared to a cache-friendly access pattern.
- Benchmark a database workload with different memory configurations: single-channel vs. dual-channel, interleaved vs. non-interleaved, and different memory speeds (DDR5-4800 vs. DDR6-6400). Report throughput and latency.
- Design a CXL-based memory pool for a cluster of 10 AI training nodes. Specify the CXL switches, memory expanders, and software configuration required.

---

### Lecture 4: Storage Technologies — From Spinning Rust to Persistent Memory

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Storage is where data persists. Unlike memory, which is volatile, storage must retain data across power cycles, system crashes, and years of operation. This lecture examines storage technologies: hard disk drives (HDDs), solid-state drives (SSDs), NVMe, and emerging technologies (DNA storage, holographic storage, and computational storage). The emphasis is on practical knowledge: how to select, configure, and manage storage for reliability, performance, and cost.

#### Key Topics

- **Hard Disk Drives (HDDs):** Magnetic storage with spinning platters and moving read/write heads. Advantages: low cost per terabyte, high capacity (24+ TB in 2040), and sequential read performance. Disadvantages: high latency (5–10 ms seek time), sensitivity to vibration, and mechanical wear. HDDs remain viable for cold storage, archival, and sequential workloads (video surveillance, backup).
- **Solid-State Drives (SSDs):** NAND flash memory with no moving parts. Advantages: low latency (10–100 μs), high random IOPS, low power, and shock resistance. Disadvantages: higher cost per TB than HDDs, finite write endurance (measured in program/erase cycles), and complex garbage collection/wear leveling. SSD form factors: 2.5" SATA, M.2 NVMe, and E1.L/E3.S enterprise drives.
- **NVMe and PCIe Storage:** NVMe (Non-Volatile Memory Express) is the protocol optimized for SSDs over PCIe, replacing the legacy AHCI/SATA protocols designed for HDDs. NVMe provides parallel queues, low latency, and high throughput. PCIe 6.0 (2032) offers 256 GB/s per x16 slot, enabling NVMe drives with 50+ GB/s sequential read speeds.
- **Storage Endurance and Reliability:** NAND flash wears out with writes. TLC (triple-level cell) stores 3 bits per cell and has lower endurance than SLC (single-level cell). Wear leveling distributes writes evenly across the drive. Over-provisioning reserves spare blocks for replacement. The IT professional must monitor SSD health via SMART metrics and plan replacement before failure.
- **RAID and Erasure Coding:** RAID (Redundant Array of Independent Disks) provides redundancy and performance:
  - **RAID 1:** Mirroring. 50% capacity overhead, high read performance.
  - **RAID 5:** Striping with distributed parity. 1/N capacity overhead, can tolerate one disk failure.
  - **RAID 6:** Striping with dual parity. 2/N capacity overhead, can tolerate two disk failures.
  - **RAID 10:** Mirrored stripes. 50% overhead, best performance and reliability.
  For large-scale storage, erasure coding (Reed-Solomon, LRC — Locally Recoverable Codes) replaces RAID, providing better space efficiency at the cost of higher rebuild complexity.
- **Emerging Storage:**
  - **Computational Storage:** Processing data within the storage device (SmartSSD, NGD Systems), reducing data movement and host CPU load. Used for analytics, compression, and encryption.
  - **DNA Data Storage:** Encoding data in synthetic DNA strands. Advantages: extreme density (1 exabyte per cubic centimeter), longevity (centuries). Disadvantages: high latency (hours to days for read/write), high cost, and specialized equipment. Used for archival in 2040.
  - **Holographic Storage:** Writing data in three-dimensional optical media. Demonstrated in labs but not yet commercially viable at scale.

#### Lecture Notes

Storage decisions are economic. The IT professional must balance: capacity requirements, performance needs (IOPS, throughput, latency), endurance expectations, power budget, physical space, and cost. The UoY Storage Team uses a tiered model:
- **Tier 1 (Hot):** NVMe SSDs for active databases, VMs, and AI training datasets. Access time: <100 μs.
- **Tier 2 (Warm):** SATA SSDs and high-density HDDs for user files, application data, and recent backups. Access time: 1–10 ms.
- **Tier 3 (Cold):** Tape (LTO-12, 120 TB per cartridge) and DNA storage for archival and compliance. Access time: minutes to hours.

Automated tiering moves data based on access patterns, but the IT professional defines the policies: what to tier, how quickly, and with what retention rules.

#### Required Reading

- Talagala, N., & Patterson, D. A. (2036). *Storage Systems: Organization and Management* (2nd ed.). Morgan Kaufmann.
- SNIA. (2039). *Computational Storage Architecture and Programming Model*.

#### Discussion Questions

1. A video streaming service needs to store 10 petabytes of content with high read throughput. Compare the TCO of an all-NVMe approach versus a tiered approach (NVMe cache + HDD bulk + CDN edge caching).
2. SSDs have finite write endurance. For a database with heavy write loads, how do you estimate SSD lifespan, and what operational practices extend it?
3. DNA data storage is currently impractical for active data but compelling for archival. What metadata and retrieval infrastructure must exist to make DNA archives usable?

#### Practice Problems

- Calculate the usable capacity and fault tolerance of a RAID 6 array with 12 × 20 TB HDDs. How does this compare to a 12-drive erasure-coded configuration with 4+2 parity?
- Monitor the SMART data of an SSD over a month of heavy use. Estimate the remaining lifespan based on wear leveling count and TBW (terabytes written) rating.
- Design a storage architecture for a scientific research facility generating 500 TB of new data per year, with requirements: 5-year retention, 99.9% availability, and budget constraints. Specify tiers, redundancy, and estimated cost.

---

### Lecture 5: GPUs and Accelerators — Beyond the General-Purpose CPU

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

The general-purpose CPU is no longer sufficient for the compute-intensive workloads that dominate modern IT: artificial intelligence, scientific simulation, graphics rendering, and real-time analytics. This lecture examines specialized accelerators: graphics processing units (GPUs), tensor processing units (TPUs), neural processing units (NPUs), and field-programmable gate arrays (FPGAs). The IT professional must understand when to deploy accelerators, how to manage them, and what trade-offs they impose.

#### Key Topics

- **GPU Architecture:** GPUs are massively parallel processors designed for graphics but repurposed for general computation (GPGPU). Key concepts:
  - **SIMT (Single Instruction, Multiple Threads):** Thousands of lightweight threads execute the same instruction on different data (SPMD model).
  - **Memory Hierarchy:** Global memory (large, high latency), shared memory (fast, on-chip, limited size), and registers (per-thread, fastest).
  - **CUDA and ROCm:** The dominant programming models for NVIDIA and AMD GPUs. CUDA (Compute Unified Device Architecture) is proprietary; ROCm is open-source.
  - **NVIDIA Hopper-3 (2038):** 144 GB HBM3e memory, 4,000 TFLOPS (FP8), and Transformer Engine for AI acceleration.
  - **AMD MI400 (2039):** 192 GB HBM3e, competitive AI performance, and open software stack (ROCm 8.0).
- **TPUs and NPUs:** Tensor Processing Units (Google TPU v6, 2040) and Neural Processing Units (integrated into SoCs, edge devices, and server cards) are optimized for matrix multiplication — the core operation in neural networks. They offer higher efficiency (TFLOPS/Watt) than GPUs for inference but less flexibility for training and non-ML workloads.
- **FPGAs and ASICs:** Field-Programmable Gate Arrays (Xilinx Versal-2, Intel Agilex-3) provide hardware-level customization. Useful for: low-latency networking, custom encryption, and specialized signal processing. ASICs (Application-Specific Integrated Circuits) offer the highest efficiency but are inflexible and expensive to design.
- **Accelerator Management in Data Centers:** Power (300–700W per GPU), cooling (direct-to-chip liquid cooling standard for AI clusters), PCIe lane requirements, and network bandwidth (InfiniBand NDR 400 Gbps for GPU clusters). The IT professional must plan rack power density, cabling, and scheduling to maximize accelerator utilization.

#### Lecture Notes

Accelerator deployment is a strategic IT decision. GPUs are general-purpose enough for most AI workloads but expensive and power-hungry. TPUs offer better efficiency for inference but lock you into Google's ecosystem. FPGAs excel at niche low-latency tasks but require specialized programming (HDL, HLS). The UoY AI Infrastructure Team maintains a heterogeneous accelerator pool: NVIDIA GPUs for research flexibility, AMD GPUs for cost-sensitive projects, and FPGAs for networking and security research.

A growing challenge is *accelerator utilization*. AI training clusters often achieve only 30–50% GPU utilization due to data loading bottlenecks, synchronization overhead, and suboptimal scheduling. The IT professional works with data scientists to optimize pipelines: prefetching, asynchronous data loading, and mixed-precision training.

#### Required Reading

- Kirk, D. B., & Hwu, W. W. (2037). *Programming Massively Parallel Processors: A Hands-on Approach* (7th ed.). Morgan Kaufmann.
- NVIDIA. (2039). *Hopper-3 Architecture and Tuning Guide*.
- AMD. (2039). *MI400 Series Data Center GPU Architecture*.

#### Discussion Questions

1. A research group wants to train a large language model. They can choose between 100 NVIDIA Hopper-3 GPUs or 150 AMD MI400 GPUs. The NVIDIA option has better software support; the AMD option is cheaper. How do you evaluate the total cost of ownership, including power, cooling, engineering time, and opportunity cost?
2. GPU clusters require InfiniBand or high-speed Ethernet for inter-GPU communication. What happens to training performance when the network topology is misconfigured (e.g., asymmetric bandwidth, congested links)?
3. Edge NPUs (in smartphones, cameras, IoT devices) enable on-device AI inference. What are the operational implications for IT when millions of edge devices run inference locally rather than sending data to the cloud?

#### Practice Problems

- Profile a GPU-accelerated program using `ncu` (NVIDIA Compute Profiler) or `rocprof`. Identify memory-bound versus compute-bound kernels and propose optimizations.
- Calculate the total power, cooling, and networking requirements for a cluster of 64 GPUs in a 4-rack configuration. Specify rack power density, cooling solution, and network topology.
- Compare the inference latency and throughput of a model running on CPU, GPU, and NPU. Document the hardware, software, and power consumption for each.

---

### Lecture 6: Embedded Systems and the Internet of Things

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Not all computing happens in data centers. Billions of embedded systems — microcontrollers, sensors, actuators, and edge devices — form the "digital nervous system" of the physical world. This lecture introduces embedded systems architecture, the Internet of Things (IoT) ecosystem, and the IT operational challenges of managing distributed, resource-constrained devices at scale.

#### Key Topics

- **Microcontroller Architecture:** Unlike general-purpose CPUs, microcontrollers (ARM Cortex-M, RISC-V RV32/64, ESP32-RISC-V) integrate CPU, memory, and I/O on a single chip. They operate at low clock speeds (MHz rather than GHz), have limited RAM (KB to MB), and prioritize power efficiency over performance. Real-time operating systems (FreeRTOS, Zephyr, RT-Thread) provide deterministic scheduling for time-critical tasks.
- **IoT Connectivity:** IoT devices communicate via: Wi-Fi (high bandwidth, high power), Bluetooth Low Energy (low power, short range), Zigbee/Z-Wave (mesh networking for smart homes), LoRaWAN (long-range, low-power, wide-area), NB-IoT/LTE-M (cellular for wide-area coverage), and satellite (for remote areas). The IT professional must select appropriate protocols based on range, bandwidth, power, and cost constraints.
- **Edge Computing:** Processing data near the source rather than in the cloud. Edge gateways aggregate sensor data, run local AI inference, and communicate condensed results upstream. Benefits: reduced latency, bandwidth savings, privacy preservation, and offline operation. The UoY Smart Campus deploys 10,000+ IoT sensors (temperature, occupancy, air quality, energy) with edge processing in each building.
- **IoT Security Challenges:** IoT devices are notoriously insecure: default passwords, unencrypted communication, lack of update mechanisms, and long lifecycles (10–20 years) that outlast vendor support. The IT professional must implement: device authentication (X.509 certificates, TPM-based attestation), encrypted communication (TLS 1.3, DTLS), over-the-air (OTA) updates, and network segmentation (isolated VLANs for IoT).
- **Device Management at Scale:** Managing thousands of distributed devices requires: fleet management platforms (AWS IoT Core, Azure IoT Hub, open-source ThingsBoard), automated provisioning, remote monitoring, and predictive maintenance. The IT professional defines update policies: staggered rollouts, canary deployments, and automatic rollback on failure.

#### Lecture Notes

The IoT is where IT meets the physical world. A failed server affects digital services; a failed IoT sensor in a medical device or industrial control system can cause physical harm. The UoY IoT Security Lab studies "digital-physical attacks": adversaries who compromise IoT devices to manipulate physical processes (HVAC, power grids, manufacturing equipment).

A critical operational challenge is *firmware lifecycle management*. Many IoT devices run firmware that is never updated. The UoY Smart Campus mandates: all IoT devices must support OTA updates, all firmware must be signed, and all devices must be enrolled in the fleet management platform before deployment. Devices that cannot meet these requirements are not permitted on the network.

#### Required Reading

- Noergaard, T. (2036). *Embedded Systems Architecture: Explore Architectural Concepts and Practical Programming* (3rd ed.). Newnes.
- Stankovic, J. A. (2037). "Research Directions for the Internet of Things." *IEEE Internet of Things Journal*, 14(2), 1–18.
- UoY IoT Security Lab. (2039). *Smart Campus Security Architecture and Best Practices*.

#### Discussion Questions

1. A manufacturer releases an IoT device with a 10-year expected lifespan but commits to only 3 years of security updates. Who bears responsibility for securing the device after vendor support ends: the manufacturer, the purchaser, or the IT department that deploys it?
2. Edge computing reduces cloud bandwidth but increases management complexity. How do you design an operational model that maintains visibility and control over thousands of edge devices without creating an unsupportable administrative burden?
3. IoT devices often lack the computational resources for strong cryptography. What lightweight cryptographic protocols are appropriate for resource-constrained devices, and what are their limitations?

#### Practice Problems

- Program a microcontroller (simulated or physical) to read a temperature sensor, apply a threshold filter, and transmit alerts via MQTT. Include power management (sleep mode between readings).
- Design a network segmentation strategy for a smart building: IoT sensors, building management systems, occupant devices, and guest Wi-Fi must be isolated. Specify VLANs, firewall rules, and access controls.
- Evaluate three IoT fleet management platforms (one cloud, one open-source, one edge-native). Compare features, scalability, security, and cost for a deployment of 5,000 devices.

---

### Lecture 7: System Interconnects and I/O Architecture

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

The components of a computer system — CPU, memory, storage, accelerators, network interfaces — must communicate efficiently. This lecture examines the buses, interconnects, and I/O architectures that enable this communication: PCIe, CXL, Infinity Fabric, NVLink, InfiniBand, and Ethernet. Understanding these technologies is essential for designing balanced systems where no component starves another for bandwidth.

#### Key Topics

- **PCIe (Peripheral Component Interconnect Express):** The dominant general-purpose interconnect for attaching peripherals to a CPU. PCIe 6.0 (256 GB/s x16 bidirectional) and PCIe 7.0 (512 GB/s x16, introduced 2038) use PAM4 signaling and FEC (Forward Error Correction) to achieve higher speeds. Lane allocation: x1, x4, x8, x16. The IT professional must understand lane budgeting: a GPU may need x16, an NVMe SSD needs x4, and a network card needs x8 — but the CPU has limited lanes.
- **CXL (Compute Express Link):** Beyond PCIe, CXL provides cache coherency and memory semantics. Three protocols: CXL.io (I/O, compatible with PCIe), CXL.cache (cache coherency for accelerators), and CXL.memory (memory expansion and pooling). CXL 4.0 enables fabric topologies where memory is disaggregated across a network of switches.
- **Vendor-Specific Interconnects:**
  - **NVIDIA NVLink:** High-bandwidth, cache-coherent interconnect between NVIDIA GPUs. NVLink 5.0 (2038) provides 900 GB/s between GPU pairs, essential for multi-GPU training.
  - **AMD Infinity Fabric:** Connects CPU chiplets, GPU dies, and memory in AMD systems. Scales from on-package (Infinity Fabric on Package, IFOP) to inter-socket (Infinity Fabric Inter-Socket, IFIS) and inter-node (Infinity Fabric over Ethernet).
  - **Intel UPI/Ultra Path Interconnect:** Replaced by CXL for memory expansion but still used for multi-socket CPU connectivity.
- **Network Interconnects:**
  - **InfiniBand:** High-performance interconnect for HPC and AI clusters. NDR 400 Gbps (2022), XDR 800 Gbps (2028), and GDR 1.6 Tbps (2036). Provides RDMA (Remote Direct Memory Access) for zero-copy communication between nodes.
  - **Ethernet:** Dominant for general-purpose networking. 400 GbE (2022), 800 GbE (2028), and 1.6 TbE (2034). RDMA over Converged Ethernet (RoCEv3) brings HPC-style networking to standard Ethernet.
- **I/O Virtualization:** SR-IOV (Single Root I/O Virtualization) allows a physical device (NIC, GPU) to be shared among multiple VMs with near-native performance. The IT professional configures SR-IOV for high-performance virtualized workloads.

#### Lecture Notes

System design is an exercise in balance. A server with the fastest CPU but insufficient memory bandwidth will underperform. A GPU cluster with fast accelerators but a slow interconnect will spend most of its time waiting for data. The IT professional must map workload requirements to system topology: how much CPU, how much memory, how much storage, what network, and what accelerators — connected by what links.

The UoY High-Performance Computing Group maintains a "Balanced System Checker" — a spreadsheet and Python tool that verifies whether a proposed system configuration matches the bandwidth and latency requirements of the target workload. Students use this tool in their IT102 capstone design project.

#### Required Reading

- PCIe SIG. (2038). *PCI Express 7.0 Base Specification*.
- CXL Consortium. (2038). *CXL 4.0 Specification*.
- InfiniBand Trade Association. (2036). *InfiniBand Architecture Specification, Release 1.7*.

#### Discussion Questions

1. A system builder proposes a 2-GPU server with both GPUs connected via PCIe x8 rather than x16, arguing that "most workloads don't saturate x16." Under what conditions is this true, and when does it become a bottleneck?
2. CXL memory pooling promises to reduce memory waste by sharing unused memory across servers. What are the latency and reliability implications, and for what workloads is this appropriate?
3. InfiniBand provides lower latency and higher bandwidth than Ethernet but at higher cost and complexity. When is the performance advantage worth the premium?

#### Practice Problems

- Design a server configuration for a specific workload: a 4-GPU AI training node with 2 TB of DRAM, 8 NVMe SSDs, and dual 400 GbE NICs. Specify the CPU, motherboard, PCIe lane allocation, and power requirements.
- Benchmark network latency and bandwidth between two servers using `ib_write_bw` (InfiniBand) and `iperf3` (Ethernet). Compare the results and discuss the implications for distributed computing.
- Research the topology of a modern supercomputer (e.g., UoY's Heimdall-HPC or a Top500 system). Diagram the interconnect topology and calculate the bisection bandwidth.

---

### Lecture 8: Reliability, Availability, and Serviceability (RAS)

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Enterprise hardware must not only perform well but also operate continuously without failure. This lecture examines the engineering practices that ensure reliability, availability, and serviceability (RAS): error detection and correction, redundancy, predictive maintenance, and fault-tolerant design. The IT professional must understand RAS features to select appropriate hardware, configure systems for resilience, and respond to hardware failures.

#### Key Topics

- **Reliability Metrics:**
  - **MTBF (Mean Time Between Failures):** Average time a component operates before failing. Enterprise HDDs: 1.5–2.5 million hours; enterprise SSDs: 2–5 million hours; CPUs: effectively infinite (failure rates <0.1% per year).
  - **MTTR (Mean Time To Repair):** Average time to restore a failed component. Hot-swappable components reduce MTTR.
  - **Failure Rate (λ):** The inverse of MTBF. Used in reliability calculations.
  - **Availability (A):** A = MTBF / (MTBF + MTTR). "Five nines" (99.999%) availability allows 5.26 minutes of downtime per year.
- **Error Detection and Correction:**
  - **ECC (Error-Correcting Code) Memory:** Detects and corrects single-bit errors, detects double-bit errors. Mandatory for enterprise servers.
  - **Chipkill / SDDC:** Advanced ECC that can correct multi-bit errors within a single DRAM chip.
  - **PCIe Lane Margining:** Proactive detection of signal degradation before it causes errors.
  - **Memory Scrubbing:** Periodic reading and rewriting of memory to detect and correct latent errors.
- **Redundancy:**
  - **Component Redundancy:** Dual power supplies, redundant fans, multipath I/O (multiple HBAs, multiple network interfaces).
  - **System Redundancy:** Clustering, failover pairs, and load-balanced pools.
  - **Data Redundancy:** RAID, erasure coding, and replication.
- **Predictive Maintenance:** Analyzing sensor data (temperature, vibration, power consumption, error rates) to predict failures before they occur. Machine learning models (anomaly detection, survival analysis) identify at-risk components. The UoY data center's predictive maintenance system replaced 200 drives proactively in 2039, preventing 15 potential outages.
- **Serviceability:** Hot-swap capabilities, tool-less chassis design, LED fault indicators, remote management (IPMI, Redfish, BMC), and automated firmware updates. The goal: minimize human intervention, minimize downtime, and minimize the risk of human error during maintenance.

#### Lecture Notes

RAS is not a feature checklist; it is a system property. A server with ECC memory but no redundant power supply is less reliable than one with both. A cluster with redundant networking but a single management switch has a single point of failure. The IT professional designs for the *weakest link* and validates assumptions through failure injection (chaos engineering for hardware).

The UoY IT Department conducts quarterly "fire drills": simulated hardware failures (pulling a drive, disconnecting a power supply, isolating a network link) to verify that redundancy works as designed. These drills are documented, analyzed, and used to improve procedures.

#### Required Reading

- Siewiorek, D. P., & Swarz, R. S. (2035). *Reliable Computer Systems: Design and Evaluation* (4th ed.). A K Peters.
- Intel. (2038). *Xeon Processor RAS Features: A Technical Guide*.

#### Discussion Questions

1. A startup argues that consumer-grade hardware is "good enough" and that enterprise RAS features are overpriced. Under what conditions is this true, and when does the cost of downtime exceed the hardware savings?
2. Predictive maintenance models can identify at-risk components but may also generate false positives (unnecessary replacements). How do you optimize the trade-off between prevention and waste?
3. A data center achieves 99.999% availability but experiences a catastrophic failure that destroys all data. Is this truly "high availability"? What does this reveal about the limitations of availability metrics?

#### Practice Problems

- Calculate the availability of a system with: two redundant power supplies (each MTBF 500,000 hours, MTTR 2 hours), RAID 6 storage (MTBF 2,000,000 hours per drive, 12 drives, MTTR 4 hours), and dual network links (MTBF 1,000,000 hours, MTTR 1 hour). Assume independent failures.
- Configure a server BIOS to enable all available RAS features: ECC, memory scrubbing, PCIe lane margining, and predictive failure analysis. Document each setting and its purpose.
- Design a chaos engineering experiment for hardware: specify the failures to inject, the expected system behavior, the rollback procedures, and the metrics to collect.

---

### Lecture 9: Performance Engineering and Benchmarking

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Performance is not an accident; it is the result of deliberate measurement, analysis, and optimization. This lecture introduces the principles of performance engineering: benchmarking methodologies, workload characterization, bottleneck identification, and optimization strategies. The IT professional must be able to measure system performance, compare configurations, and justify hardware decisions with empirical data.

#### Key Topics

- **Benchmarking Principles:** A good benchmark is representative, reproducible, and relevant. Pitfalls: synthetic benchmarks that don't match real workloads, benchmarketing (cherry-picking favorable benchmarks), and neglecting system-wide effects (caching, background processes).
- **Standard Benchmarks:**
  - **SPEC CPU:** Integer and floating-point performance for general-purpose computing.
  - **SPECpower:** Energy efficiency under varying loads.
  - **TPC-C / TPC-E:** Database transaction processing.
  - **MLPerf:** Machine learning training and inference.
  - **IO500:** High-performance storage.
  - **LINPACK / HPL:** Supercomputer floating-point performance (Top500 list).
- **Workload Characterization:** Understanding what a system actually does: CPU-bound (high utilization, high IPC), memory-bound (low IPC, high cache misses), I/O-bound (low CPU, high disk/network wait), or latency-sensitive (bursty, requires consistent response times). Tools: `perf`, `bpftrace`, `eBPF`, `sar`, `iostat`, `vmstat`, and application-specific profilers.
- **Bottleneck Identification:** The fundamental theorem of performance tuning: a system is only as fast as its slowest component. Methodologies:
  - **USE Method:** Utilization, Saturation, Errors — for each resource, check if it is fully utilized, saturated with queued work, or producing errors.
  - **RED Method:** Rate, Errors, Duration — for services, monitor request rate, error rate, and response duration.
  - **Drill-Down Analysis:** Start with system-level metrics, narrow to process-level, then function-level, then code-level.
- **Optimization Strategies:**
  - **Right-Sizing:** Matching resources to workload (avoiding over-provisioning and under-provisioning).
  - **Caching:** Reducing latency by storing frequently accessed data closer to the consumer.
  - **Parallelization:** Distributing work across multiple cores, nodes, or accelerators.
  - **Algorithmic Improvement:** Sometimes the best optimization is not hardware but software — a better algorithm can yield orders of magnitude improvement.

#### Lecture Notes

The UoY Performance Engineering Lab maintains a "Benchmark Zoo" — a collection of 200+ benchmark configurations for common workloads: web serving, databases, AI training, video encoding, scientific simulation, and more. Students learn to select appropriate benchmarks, configure them correctly, and interpret results without falling into common traps.

A critical IT skill is *performance regression detection*: identifying when a system change (firmware update, software patch, configuration change) degrades performance. Automated performance testing in CI pipelines compares benchmark results against baselines and flags regressions before deployment.

#### Required Reading

- Gregg, B. (2036). *Systems Performance: Enterprise and the Cloud* (3rd ed.). Addison-Wesley.
- SPEC. (2039). *SPEC Benchmark Methodology and Best Practices*.

#### Discussion Questions

1. A vendor publishes benchmark results showing their server is 50% faster than a competitor's. The benchmark is a synthetic workload that doesn't resemble your actual application. How do you evaluate the vendor's claim?
2. Performance optimization often involves trade-offs: caching improves read performance but complicates consistency; parallelization improves throughput but increases latency variability. How do you decide which trade-offs are acceptable?
3. A system is performing poorly, but none of the standard metrics (CPU, memory, disk, network) show saturation. What less-obvious bottlenecks might exist, and how do you diagnose them?

#### Practice Problems

- Run a standard benchmark (e.g., Sysbench, Fio, or MLPerf) on a system. Characterize the workload: is it CPU-bound, memory-bound, or I/O-bound? Justify with metrics.
- Compare the performance of a workload on two different storage configurations: RAID 1 SSDs versus single NVMe. Measure throughput, latency, and consistency. Explain the differences.
- Design a performance regression testing pipeline for a web application. Specify the benchmarks, the baseline methodology, the statistical tests for significance, and the escalation procedures.

---

### Lecture 10: Hardware Procurement and Lifecycle Management

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Selecting and managing hardware is a core IT responsibility with significant financial and operational implications. This lecture covers the hardware procurement process: requirements analysis, vendor evaluation, total cost of ownership (TCO) analysis, lifecycle planning, and decommissioning. It also addresses sustainability: energy efficiency, carbon footprint, circular economy principles, and responsible disposal.

#### Key Topics

- **Requirements Analysis:** Before procuring hardware, the IT professional must understand: workload characteristics (compute, memory, storage, network, accelerator requirements), growth projections, availability requirements, compliance constraints, and budget. The UoY IT Department uses a standardized "Hardware Requirements Document" template that forces stakeholders to quantify needs rather than request "the fastest server."
- **Vendor Evaluation:** Criteria: technical specifications, reliability history, support quality, supply chain resilience, software ecosystem, and total cost. Vendor lock-in risks: proprietary technologies that make migration difficult. The IT professional maintains relationships with multiple vendors to ensure competitive pricing and reduce dependency.
- **Total Cost of Ownership (TCO):** TCO includes: acquisition cost (hardware, software licenses), operating costs (power, cooling, datacenter space, maintenance contracts), personnel costs (administration, support), and end-of-life costs (data sanitization, recycling, resale). A server that is 20% cheaper to purchase may be 50% more expensive over 5 years due to higher power consumption and maintenance costs.
- **Lifecycle Management:** The typical enterprise hardware lifecycle is 3–5 years for servers, 5–7 years for storage, and 7–10 years for networking. Lifecycle stages: procurement, deployment, operation, maintenance, refresh planning, and decommissioning. Refresh planning begins 18 months before end-of-life to allow for testing, migration, and budget approval.
- **Sustainability and Circular Economy:**
  - **Energy Efficiency:** Selecting hardware with high performance-per-watt. The UoY requires that all new server purchases meet or exceed the ENERGY STAR for Data Center Equipment standards.
  - **Carbon Footprint:** Calculating embodied carbon (manufacturing) and operational carbon (power). The IT professional considers carbon alongside cost in procurement decisions.
  - **E-Waste Reduction:** Modular design for component reuse, certified recycling programs, and donation of functional equipment. The UoY partners with the Nordic Hardware Circular Economy Initiative to ensure responsible disposal.
  - **Right to Repair:** Supporting vendor policies that allow IT staff to repair and upgrade equipment rather than replace it.

#### Lecture Notes

Hardware procurement is not shopping; it is engineering economics. The IT professional must be fluent in financial concepts: net present value (NPV), return on investment (ROI), depreciation, and amortization. The UoY IT Finance Team reviews all hardware purchases over $50,000, requiring a TCO analysis and risk assessment.

The department maintains a "Hardware Graveyard" — a storage area where decommissioned equipment awaits secure data destruction and recycling. Students in IT102 tour this facility to understand the full lifecycle. The motto: *"Every component has a story; every story deserves an ending that honors the earth."*

#### Required Reading

- UoY IT Procurement Office. (2039). *Hardware Procurement and Lifecycle Management Guide*.
- European Commission. (2038). *Circular Economy Action Plan for Data Center Hardware*.
- Gartner. (2039). *Data Center TCO Analysis: Methodology and Best Practices*.

#### Discussion Questions

1. A CFO proposes extending server lifecycles from 4 to 7 years to reduce capital expenditure. What operational risks does this create, and how do you quantify them in financial terms?
2. Vendor A offers proprietary storage with excellent performance but no interoperability. Vendor B offers standard protocols with lower performance. How do you evaluate the lock-in risk versus performance benefit?
3. The embodied carbon of manufacturing a server is equivalent to 2–3 years of operational carbon. How does this affect the economics of early replacement with more efficient hardware?

#### Practice Problems

- Calculate the 5-year TCO for two server options: Option A (lower purchase price, higher power consumption, 3-year warranty) and Option B (higher purchase price, lower power consumption, 5-year warranty). Include acquisition, power, cooling, maintenance, and disposal costs.
- Evaluate three SSD vendors on criteria: specifications, reliability data (MTBF, field failure rates), warranty terms, support quality, and price. Produce a weighted scorecard and recommendation.
- Design a sustainable hardware lifecycle policy for a mid-size company: procurement standards, refresh criteria, reuse protocols, recycling procedures, and carbon reporting requirements.

---

### Lecture 11: Future Directions — Optical, Quantum, and Biological Computing

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

Silicon-based CMOS technology has carried computing for sixty years, but its limits are visible. This lecture surveys the post-silicon technologies that may define the next era of computing: optical computing, quantum computing hardware (from an IT infrastructure perspective), biological computing, and novel materials (graphene, 2D semiconductors, spintronics). The emphasis is on practical implications: when these technologies will be ready for IT deployment, what problems they solve, and what challenges they introduce.

#### Key Topics

- **Optical Computing:** Using photons rather than electrons for computation and communication. Advantages: no RC delay, no heat generation from signal transmission, massive parallelism. Challenges: difficulty building practical optical logic gates, size mismatch between optical and electronic components, and the need for optoelectronic interfaces. By 2040, optical interconnects (chip-to-chip, board-to-board) are commercial, but general-purpose optical processors remain research projects.
- **Quantum Computing Hardware (IT Perspective):** While CS students study quantum algorithms, IT students study the infrastructure: dilution refrigerators, cryogenic control electronics, shielding requirements, and classical-quantum hybrid scheduling. The IT professional's role in quantum computing is managing the classical infrastructure that supports the QPU: ensuring power stability, managing classical-quantum data flow, and monitoring system health.
- **Biological Computing:** Using DNA, proteins, or cells for computation and storage. DNA data storage (covered in Lecture 4) is the most mature application. Protein-based logic gates and bacterial computing are fascinating but decades from practical use. The IT professional's interest is in archival storage and the ethical implications of biological data handling.
- **Novel Materials:**
  - **Graphene and 2D Materials:** High electron mobility, potential for terahertz transistors. Challenges: manufacturing uniformity, integration with silicon processes.
  - **Spintronics:** Using electron spin rather than charge for information processing. Promises ultra-low-power logic and non-volatile memory (MRAM). MRAM is commercially available in 2040 for specific applications (spacecraft, high-radiation environments).
  - **Carbon Nanotubes:** Used in specialized interconnects and sensors. IBM and TSMC have demonstrated nanotube transistors but not yet at commercial scale.

#### Lecture Notes

The IT professional must distinguish between research potential and operational reality. A technology that works in a laboratory under ideal conditions may require a decade of engineering to become deployable. The UoY Emerging Technology Evaluation Framework requires: reproducible results from multiple independent labs, a clear path to manufacturing, and a defined problem that the technology solves better than existing alternatives.

The department's position on post-silicon technologies: monitor closely, pilot cautiously, deploy only when mature. The Smart Campus has small-scale pilots of optical interconnects (in the AI training cluster), MRAM (in edge IoT devices), and quantum-safe networking (connecting to the Nordic Quantum Network). These pilots provide real-world data for future procurement decisions.

#### Required Reading

- IEEE. (2039). *International Roadmap for Devices and Systems (IRDS): Beyond CMOS*.
- Qubitsson, E. (2038). "Quantum Infrastructure: What IT Professionals Need to Know." *UoY Quantum Engineering Review*, 2(2), 45–62.
- Adleman, L. M. (2037). "Biological Computing: Progress and Prospects." *Nature Computing*, 3(1), 12–28.

#### Discussion Questions

1. Optical computing promises speed without heat, but practical optical transistors remain elusive. If optical logic never matures, what value do optical interconnects still provide?
2. MRAM is non-volatile, radiation-hard, and fast — but expensive and low-density. For what applications is it worth the premium, and when is flash or DRAM still superior?
3. A startup claims their carbon nanotube CPU is 100x faster than silicon. What evidence would convince you to invest in their technology for your data center?

#### Practice Problems

- Compare the theoretical advantages and practical readiness of three post-silicon technologies (optical, spintronic, and biological). Create a timeline projection for when each might impact enterprise IT.
- Design a pilot program for evaluating optical interconnects in a small cluster. Specify the metrics, success criteria, risk mitigation, and budget.
- Research one "beyond CMOS" technology in depth. Write a 2,000-word report assessing its technical maturity, potential applications, and remaining engineering challenges.

---

### Lecture 12: Synthesis — The Hardware Professional's Mindset

**Course:** IT102 — Computer Hardware & Architecture  
**Degree:** Bachelor of Science in Information Technology, 2040

---

#### Overview

This final lecture synthesizes the course into a coherent professional mindset. The hardware professional is part engineer, part detective, part economist, and part environmental steward. They must understand transistors and TCO, benchmarks and business cases, performance and sustainability. This lecture reflects on the enduring principles that outlast any specific technology generation.

#### Key Topics

- **Systems Thinking:** Hardware does not exist in isolation. A CPU choice affects memory requirements, cooling design, power infrastructure, software optimization, and operational staffing. The hardware professional sees connections: how a storage decision cascades through backup windows, network bandwidth, and disaster recovery time.
- **Empirical Rigor:** Claims must be tested, not accepted. "The vendor says it's faster" is not evidence; benchmarks under your workload are. The hardware professional maintains a skeptical mindset, validated by measurement.
- **Economic Literacy:** Hardware decisions are financial decisions. The hardware professional speaks the language of TCO, ROI, NPV, depreciation, and risk. They can justify a premium purchase with projected savings and quantify the cost of downtime.
- **Environmental Responsibility:** Every watt consumed, every drive manufactured, every device discarded has environmental consequences. The hardware professional minimizes waste, maximizes efficiency, and plans for responsible end-of-life.
- **The Norse Smith as Archetype:** In Norse mythology, the dwarves Brokkr and Eitri forged the gods' greatest treasures: Mjölnir, Draupnir, and Gullinbursti. Their craft was not merely technical but sacred — creating tools that shaped the world. The hardware professional carries this tradition: building the substrate on which civilization's digital life depends.

#### Lecture Notes

The course closes with a practical capstone: students design a complete system for a specified scenario (e.g., a research lab, a smart campus building, or a small business). The design must include: requirements analysis, component selection, TCO calculation, performance projections, RAS configuration, sustainability assessment, and a procurement timeline. Designs are presented to a panel of faculty and industry practitioners.

The UoY Hardware Laboratory's closing ritual: each student receives a small silicon wafer — a physical piece of the substrate they have spent the semester studying. The inscription reads: *"From sand to thought — this is your craft."*

#### Required Reading

- UoY IT Department. (2040). *The Hardware Professional's Handbook: Principles and Practices*.
- Larrington, C. (Trans.). (2014). *The Poetic Edda*. Oxford University Press. [Hávamál, stanzas on craft and wisdom]

#### Discussion Questions

1. You have designed a system that meets all technical requirements but exceeds the budget by 30%. What negotiation strategies, design compromises, or alternative approaches do you consider?
2. A vendor offers to sponsor your department's equipment in exchange for preferential treatment in procurement decisions. What ethical issues does this raise, and how do you maintain professional integrity?
3. The Hávamál advises: "A man should never move an inch from his weapons when he crosses the open field." How does this ancient wisdom apply to modern hardware redundancy and disaster preparedness?

#### Practice Problems

- Complete the capstone system design project. Present a 15-minute defense of your choices, responding to questions from faculty and peers.
- Write a "Hardware Procurement Policy" for a hypothetical organization. Address: evaluation criteria, approval workflows, vendor management, sustainability requirements, and conflict-of-interest rules.
- Reflect on your learning in IT102. What was most surprising? Most challenging? Most valuable for your career aspirations?

---

## Final Examination Preparation

The IT102 final examination is a **comprehensive written and practical assessment** evaluating hardware knowledge and system design skills. The examination consists of three parts:

### Part A: Written Examination (60 minutes)
Answer three of five essay questions:

1. **Architecture and Performance:** Compare the RISC and CISC design philosophies using specific modern examples (ARM64 vs. x86-64). Discuss the trade-offs in power efficiency, performance, software ecosystem, and backward compatibility.

2. **Memory Hierarchy:** A database server is experiencing poor performance despite low CPU utilization. Analyze how you would determine whether the bottleneck is in the memory hierarchy (cache, DRAM, TLB) and propose diagnostic and remediation steps.

3. **Storage Design:** Design a tiered storage architecture for a video production company that generates 2 TB of raw footage per day, requires fast access to recent projects, and must retain all footage for 7 years. Specify technologies, capacities, redundancy, and estimated TCO.

4. **Accelerator Deployment:** A research group wants to purchase GPU clusters for AI training. Evaluate the infrastructure implications: power, cooling, networking, software stack, and operational model. What risks must be mitigated before deployment?

5. **Sustainability:** Calculate the carbon footprint of a 100-server data center over 5 years, considering both embodied and operational carbon. Propose strategies to reduce the footprint by 50% without compromising availability.

### Part B: Practical Examination (90 minutes)
Complete hands-on tasks in the UoY Hardware Laboratory:

- Diagnose a hardware fault in a server using diagnostic LEDs, BMC logs, and physical inspection.
- Configure BIOS/UEFI settings for optimal performance and RAS on a given workload.
- Benchmark a storage device and characterize its performance profile (sequential vs. random, read vs. write, latency distribution).
- Design a rack layout for a specified workload, considering power, cooling, cabling, and serviceability.

### Part C: System Design Defense (30 minutes, oral)
- Present your capstone system design.
- Defend your component selections against alternative options.
- Respond to questions about TCO, performance, reliability, and sustainability.

### Grading Rubric
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Technical Knowledge | 25% | Understanding of CPU, memory, storage, and interconnect architectures |
| Analytical Skills | 25% | Bottleneck identification, trade-off analysis, and systematic diagnosis |
| Design Ability | 20% | Balanced system design considering performance, cost, and constraints |
| Practical Skills | 15% | Hardware configuration, benchmarking, and troubleshooting |
| Communication | 15% | Clear written and oral presentation of technical designs |

*May your transistors switch true, your memory refresh clean, and your fans spin quiet.* ᛟ

— University of Yggdrasil, Department of Information Technology, 2040
