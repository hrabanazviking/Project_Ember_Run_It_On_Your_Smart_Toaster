# IT403: Neuromorphic & Edge Infrastructure
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** IT301, IT401
**Description:** Advanced study of next-generation computing infrastructure: neuromorphic processors that mimic brain architecture, edge computing that brings intelligence to where data is generated, and the 2040 convergence of specialized hardware and distributed AI inference.

---

## Lectures

ᚠ **Lecture 1: The End of von Neumann — Why Architecture Matters Again**

### 1.1 Overview

For 70 years, the von Neumann architecture — separate CPU and memory, sequential instruction execution — dominated computing. By 2040, its limitations are driving a Cambrian explosion of alternative architectures: neuromorphic (brain-inspired), dataflow, near-memory compute, and heterogeneous integration. This lecture surveys the post-von-Neumann landscape and establishes why IT professionals must understand hardware architecture.

### 1.2 Key Topics

- **The von Neumann Bottleneck:** The separation of CPU and memory creates a bandwidth bottleneck — the CPU spends cycles waiting for data. While CPU speeds increased exponentially, memory speeds lagged. The result: processors are often idle, waiting. Alternative architectures address this by: (1) processing-in-memory (PIM); (2) dataflow execution; (3) massively parallel, distributed computation (neuromorphic).
- **Dennard Scaling Is Dead:** For decades, transistor density doubled while power per transistor halved. Dennard scaling ended around 2006 — transistors still shrink, but power density increases. The result: we can't just make faster CPUs. We need specialized, energy-efficient architectures for specific workloads — especially AI.
- **The 2040 Compute Landscape:** (1) **CPUs** — general-purpose, good for control flow and sequential logic; (2) **GPUs** — massively parallel, good for matrix math and graphics; (3) **NPUs (Neural Processing Units)** — specialized for neural network inference, 10-100x more efficient than GPUs for AI; (4) **Neuromorphic** — spiking neural networks, event-driven, brain-like efficiency; (5) **FPGAs** — reconfigurable hardware for custom accelerators; (6) **Quantum** — for specialized problems (optimization, simulation, cryptography).

### 1.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Post-von-Neumann Computing: A Survey*.

### 1.4 Discussion Questions
1. How does the von Neumann bottleneck specifically impact modern AI workloads that constantly move weights between memory and compute?
2. If Dennard scaling had continued, would we need neuromorphic and edge computing today? Why or why not?
3. In what ways is the 2040 compute landscape more complex than the 2020 landscape, and what skills does an IT professional need to navigate it?

---

ᚢ **Lecture 2: Neuromorphic Computing — Computing Like the Brain**

### 2.1 Overview

Neuromorphic computing abandons the digital, clock-driven, von Neumann model in favor of brain-inspired computation: spiking neural networks (SNNs) where neurons communicate via sparse, asynchronous electrical pulses (spikes), and computation is event-driven. The result: extreme energy efficiency, natural temporal processing, and architectures suited to sensory and edge AI workloads.

### 2.2 Key Topics

- **Spiking Neural Networks (SNNs):** Unlike traditional artificial neural networks (which use continuous activation values), SNNs use spikes — discrete events in time. Information is encoded in spike timing and rate. SNNs are: (1) **Event-driven** — neurons only compute when they receive spikes, saving energy; (2) **Temporal by nature** — SNNs naturally process time-series data (audio, video, sensor streams); (3) **Biologically plausible** — closer to how real brains work, enabling insights from neuroscience.
- **Neuromorphic Hardware:** (1) **Intel Loihi 3** — research chip with 1 million neurons, on-chip learning, event-driven architecture. Power: milliwatts for workloads that would consume watts on a GPU; (2) **IBM NorthPole** — brain-inspired chip optimized for inference, combining compute and memory on a single die; (3) **SpiNNaker 3** — University of Manchester's million-core neuromorphic supercomputer, modeling brain-scale networks. By 2040, neuromorphic accelerators are standard in edge devices for always-on sensing.
- **Applications:** Neuromorphic excels at: (1) **Always-on audio processing** — wake word detection, sound classification, with sub-milliwatt power; (2) **Visual odometry** — tracking motion from camera feed for drones and robots; (3) **Anomaly detection** — detecting unusual patterns in sensor streams; (4) **Brain-computer interfaces** — processing neural signals in real-time with minimal power.

### 2.3 Required Reading
- Davies, M., et al. (2018, updated 2038). "Loihi: A Neuromorphic Manycore Processor." *IEEE Micro*.
- UoY Neuromorphic Lab. (2040). *Neuromorphic Computing in Production: Use Cases and Benchmarks*.

### 2.4 Discussion Questions
1. How does the event-driven nature of spiking neural networks enable always-on sensing with minimal power consumption?
2. Compare and contrast the approaches of Intel Loihi and IBM NorthPole to neuromorphic computing. What are the trade-offs between flexibility and performance?
3. What ethical considerations arise from neuromorphic systems that more closely mimic biological neural processes?

---

ᚦ **Lecture 3: Edge Computing — Intelligence Where Data Is Born**

### 3.1 Overview

Edge computing pushes computation from centralized data centers to where data is generated — factory floors, retail stores, vehicles, smartphones, and IoT devices. By 2040, the edge is the primary compute location for AI inference, real-time processing, and privacy-sensitive workloads. This lecture covers edge architecture, deployment patterns, and the edge-cloud continuum.

### 3.2 Key Topics

- **Why Edge?** (1) **Latency** — autonomous vehicles need millisecond decisions, not 100ms cloud round trips; (2) **Bandwidth** — a factory with 1,000 cameras generates petabytes/day — you can't send it all to the cloud; (3) **Privacy** — process sensitive data locally rather than sending it to centralized servers; (4) **Resilience** — edge systems operate when connectivity is intermittent; (5) **Cost** — cloud egress and compute costs for continuous video processing are prohibitive.
- **The Edge-Cloud Continuum:** Edge is not a replacement for cloud — it's a complement. The continuum: (1) **Far edge** — sensors, microcontrollers, sub-watt devices; (2) **Near edge** — gateways, on-premises servers; (3) **Edge data center** — regional micro-data centers (5-10ms latency); (4) **Cloud** — centralized data centers (50-100ms latency). Workloads are placed based on latency, bandwidth, privacy, and cost requirements.
- **Edge Deployment Patterns:** (1) **Cloud-trained, edge-inferred** — train AI models in the cloud, deploy to edge for inference; (2) **Federated learning** — train models collaboratively across edge devices without centralizing data; (3) **Edge-native applications** — designed from scratch to run on distributed, heterogeneous edge infrastructure; (4) **Edge orchestration** — Kubernetes at the edge (K3s, MicroK8s, KubeEdge) manages fleets of edge nodes.

### 3.3 Required Reading
- Satyanarayanan, M. (2017, updated 2038). "The Emergence of Edge Computing." *IEEE Computer*.
- CNCF. (2040). *Edge Native Application Principles*.

### 3.4 Discussion Questions
1. How does edge computing change the traditional three-tier architecture (presentation, application, data) of enterprise applications?
2. What are the challenges of managing thousands of heterogeneous edge devices, and how do orchestration platforms like K3s address them?
3. In what ways does edge computing exacerbate or alleviate the digital divide between urban and rural areas?

---

ᚨ **Lecture 4: AI at the Edge — NPUs, TinyML, and On-Device Intelligence**

### 4.1 Overview

The killer application for edge computing is AI inference. By 2040, every smartphone, laptop, and IoT device includes a Neural Processing Unit (NPU) — specialized hardware that runs AI models with extreme efficiency. This lecture covers edge AI: NPU architectures, TinyML, model optimization (quantization, pruning, distillation), and the operational challenge of managing thousands of edge AI models.

### 4.2 Key Topics

- **Neural Processing Units (NPUs):** (1) **Qualcomm Hexagon NPU** — integrated into Snapdragon mobile platforms, optimized for transformer-based models; (2) **Apple Neural Engine** — dedicated matrix multiplication hardware, scales with each iPhone generation; (3) **Google Edge TPU** — designed for MobileNet and EfficientNet models, used in Coral devices; (4) **Huawei Da Vinci Architecture** — scalable NPU architecture used across Mate and P series smartphones.
- **TinyML:** Machine learning for microcontrollers with kilobytes of RAM and milliwatt power budgets. Techniques include: model quantization (8-bit or even 4-bit weights), pruning (removing unnecessary connections), knowledge distillation (training a small model to mimic a large one), and neural architecture search for tiny models.
- **Model Optimization:** Before deploying to edge, AI models undergo aggressive optimization: (1) **Quantization** — converting 32-bit floating point weights to 8-bit integers; (2) **Pruning** — removing connections that contribute little to accuracy; (3) **Distillation** — training a student model to replicate a teacher model's behavior; (4) **Compilation** — converting the model to hardware-specific instructions via TVM, Glow, or vendor-specific compilers.
- **Operational Challenge:** Managing thousands of edge AI models requires: (1) **Model versioning** — tracking which model is deployed where; (2) **Over-the-air (OTA) updates** — securely deploying new models to devices in the field; (3) **Monitoring** — detecting model drift or degradation in production; (4) **Fallback mechanisms** — reverting to a previous model or cloud inference if edge inference fails.

### 4.3 Required Reading
- Satyanarayanan, M. (2017, updated 2038). "The Emergence of Edge Computing." *IEEE Computer*.
- CNCF. (2040). *Edge Native Application Principles*.
- Warden, P. & Dugan, S. (2018). *TinyML: Machine Learning with TensorFlow Lite on Arduino and Ultra-Low-Power Microcontrollers*. O'Reilly Media.

### 4.4 Discussion Questions
1. How does quantization affect the accuracy of neural networks, and what techniques exist to minimize accuracy loss?
2. Compare the trade-offs between cloud-trained models deployed to edge versus models trained entirely on edge devices via federated learning.
3. What are the privacy implications of running AI inference on user devices versus sending data to the cloud?

---

ᚱ **Lecture 5: Heterogeneous Computing — Orchestrating the Compute Zoo**

### 5.1 Overview

By 2040, a single application rarely runs on one type of processor. Instead, it orchestrates a heterogeneous mix: CPUs for control flow, GPUs for matrix math, NPUs for AI inference, neuromorphic chips for sensor preprocessing, FPGAs for custom acceleration, and quantum accelerators for optimization problems. This lecture covers the software stack and orchestration layers needed to manage this compute zoo.

### 5.2 Key Topics

- **Runtime Heterogeneity:** Modern applications use multiple runtimes simultaneously: (1) **CPU runtime** — standard OS processes and threads; (2) **GPU runtime** — CUDA, ROCm, or Vulkan Compute; (3) **NPU runtime** — vendor-specific SDKs (Qualcomm SNPE, Apple Core ML, Google Edge TPU runtime); (4) **Neuromorphic runtime** — event-driven SDKs for spiking neural networks; (5) **FPGA runtime** — OpenCL or vendor-specific HDL tools; (6) **Quantum runtime** — Qiskit, Cirq, or vendor-specific quantum SDKs.
- **Data Movement:** The hidden cost of heterogeneous computing is moving data between accelerators: (1) **Unified Memory** — NVIDIA's CUDA Unified Memory, AMD's HSA, and Intel's OneAPI attempt to provide a single pointer accessible from CPU and GPU; (2) **Zero-Copy** — techniques to avoid copying data when passing between accelerators (e.g., GPU-Direct for NIC-to-GPU transfer); (3) **Memory Hierarchy Awareness** — understanding that data in GPU memory is not the same as data in CPU memory and requires explicit transfer.
- **Task Scheduling and Orchestration:** (1) **Kubernetes Device Plugin** — exposes GPUs, NPUs, and other accelerators as schedulable resources in Kubernetes; (2) **YARN with GPU Support** — Apache Hadoop YARN extended for GPU scheduling; (3) **Custom Schedulers** — AI-driven schedulers that predict task duration and place tasks on the optimal accelerator based on historical performance; (4) **Workflow Engines** — Apache Airflow, Argo Workflows, and Kubeflow Pipelines for defining multi-step workflows that traverse different accelerators.
- **Observability and Debugging:** (1) **Cross-Platform Profiling** — tools like NVIDIA Nsight Systems, AMD uProf, and Intel VTune that profile CPU, GPU, and memory in a single view; (2) **Accelerator-Specific Metrics** — GPU utilization, NPU saturation, neuromorphic spike rate, FPGA logic utilization; (3) **End-to-End Tracing** — tracing a request as it moves from CPU to GPU to NPU and back, measuring latency at each hop.

### 5.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Heterogeneous Computing Orchestration: Patterns and Tools*.
- Khronos Group. (2040). *SYCL 2024 Specification*.

### 5.4 Discussion Questions
1. How does data movement between accelerators create performance bottlenecks, and what architectural features minimize this cost?
2. Compare Kubernetes device plugins with custom AI-driven schedulers for heterogeneous workloads. When is each approach appropriate?
3. What are the challenges of debugging an application that spans CPU, GPU, and neuromorphic compute, and what tools exist to address them?

---

ᚲ **Lecture 6: Processing-in-Memory and Near-Memory Compute**

### 6.1 Overview

To alleviate the von Neumann bottleneck, computing is moving closer to memory. Processing-in-memory (PIM) and near-memory compute architectures place compute logic directly in or adjacent to memory arrays, reducing data movement and enabling massive parallelism for memory-bound workloads.

### 6.2 Key Topics

- **Processing-in-Memory (PIM):** (1) **DRAM-based PIM** — Samsung's HBM-PIM and SK Hynix's Accelerator-in-Memory add compute logic to DRAM chips; (2) **SRAM-based PIM** — compute logic embedded in SRAM caches for nearest-neighbor operations; (3) **Flash-based PIM** — logic in NAND flash for in-storage computation like filtering and aggregation.
- **Near-Memory Compute:** (1) **High Bandwidth Memory (HBM)** — stacked DRAM with wide interfaces, enabling terabytes-per-second bandwidth to logic dies stacked alongside; (2) **Memory Controller Offload** — simple operations (bitwise, comparison) offloaded to the memory controller; (3) **Cache Coherency Extensions** — extending cache coherency protocols to include accelerator caches.
- **Applications:** PIM excels at: (1) **Graph Analytics** — traversing large graphs (social networks, knowledge graphs) where memory access patterns are irregular; (2) **Database Operations** — filtering, aggregation, and joining large tables; (3) **Bioinformatics** — sequence alignment and database searching; (4) **Machine Learning Preprocessing** — normalizing large feature matrices before model training.
- **Programming Models:** (1) **PIM-Specific Instructions** — extending ISA with new instructions that trigger in-memory operations; (2) **Offload Models** — annotating code to indicate which functions should run on PIM units; (3) **Data-Centric Languages** — languages like Chapel and Legion that express computation in terms of data movement and transformation.

### 6.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Processing-in-Memory: Architectures and Applications*.
- JEDEC. (2040). *JBESD244: High Bandwidth Memory (HBM) Standard*.

### 6.4 Discussion Questions
1. How does processing-in-memory change the traditional memory hierarchy, and what new levels does it introduce?
2. Compare DRAM-based PIM with SRAM-based PIM in terms of latency, bandwidth, and use cases.
3. What are the challenges of debugging PIM applications, given that traditional debuggers expect compute to happen in the CPU?

---

ᚷ **Lecture 7: Quantum Accelerators — Specialized Compute for Niche Problems**

### 7.1 Overview

While quantum computers will not replace classical CPUs, they excel at specific problem classes: optimization, simulation, and certain cryptographic tasks. By 2040, quantum accelerators are available as PCIe cards or cloud instances, and IT professionals must understand when and how to use them.

### 7.2 Key Topics

- **Quantum Annealers:** (1) **D-Wave Advantage System** — 5000+ qubits for optimization problems; (2) **Fujitsu Digital Annealer** — CMOS-based implementation of quantum annealing principles; (3) **Applications** — portfolio optimization, logistics routing, protein folding, and maximum satisfiability (Max-SAT) problems.
- **Gate-Based Quantum Computers:** (1) **IBM Eagle Processor** — 127-qubit superconducting processor; (2) **Google Sycamore** — 70-qubit processor demonstrating quantum supremacy; (3) **Applications** — quantum chemistry, quantum simulation, and certain optimization problems via variational algorithms.
- **Photonic Quantum Computers:** (1) **Xanadu X8** — 8-mode photonic quantum computer; (2) **PsiQuantum** — fault-tolerant photonic approach aiming for million-qubit systems; (3) **Applications** — boson sampling, quantum machine learning, and linear optics problems.
- **Quantum-Inspired Algorithms:** Classical algorithms that mimic quantum principles for improved performance: (1) **Quantum-Inspired Optimization Algorithms** — using tensor networks or simulated quantum annealing; (2) **Quantum-Inspired Machine Learning** — quantum principal component analysis and quantum support vector machines.
- **Integration with Classical Systems:** (1) **Hybrid Workflows** — classical preprocessing, quantum acceleration, classical postprocessing; (2) **API Access** — cloud-based quantum services (AWS Braket, Azure Quantum, Google Quantum AI); (3) **On-Premises Accelerators** — PCIe quantum cards for low-latency access; (4) **Workflow Orchestration** — integrating quantum jobs into Airflow, Kubeflow, or custom orchestration systems.

### 7.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Quantum Accelerators: Integration and Applications*.
- D-Wave Systems. (2040). *Leap Quantum Cloud Service Documentation*.

### 7.4 Discussion Questions
1. For what classes of problems does quantum annealing provide a demonstrable advantage over classical heuristics?
2. Compare the qubit technologies of superconducting (IBM, Google), trapped-ion (Honeywell), and photonic (Xanadu) quantum computers. What are the trade-offs between coherence time, gate fidelity, and scalability?
3. How should an organisation decide between investing in on-premises quantum accelerators versus using cloud-based quantum services?

---

ᚹ **Lecture 8: Power, Thermal, and the Physics of Computing**

### 8.1 Overview

As computing becomes more specialized and heterogeneous, power and thermal management become first-class design concerns. By 2040, data centres are liquid-cooled, edge devices are passively cooled, and every watt is accounted for in the pursuit of performance per joule.

### 8.2 Key Topics

- **Power Measurement and Attribution:** (1) **Instrumentation** — smart PDUs, in-rack power meters, and CPU/GPU power sensors; (2) **Attribution** — attributing power consumption to specific applications, processes, or hardware components; (3) **Power Capping** — setting hard limits on power draw to prevent tripping breakers or exceeding cooling capacity.
- **Thermal Management:** (1) **Air Cooling** — traditional fan-based cooling, enhanced with computational fluid dynamics (CFD) design; (2) **Liquid Cooling** — direct-to-chip liquid cooling for high-density racks; (3) **Immersion Cooling** — submerging servers in dielectric fluid for extreme heat density; (4) **Edge Cooling** — passive cooling (heat sinks, heat pipes) and active cooling (miniature fans, thermoelectric coolers) for edge devices.
- **Energy Proportionality:** The ideal that power consumption scales linearly with utilization — a server at 10% load uses 10% of its peak power. By 2040, server designs approach energy proportionality through: (1) **Dynamic Voltage and Frequency Scaling (DVFS)** — adjusting CPU/GPU voltage and frequency based on load; (2) **Sleep States** — deeper C-states for CPUs and equivalent states for accelerators; (3) **Proportional Power Delivery** — power supplies that scale output with demand.
- **Sustainability Metrics:** (1) **Power Usage Effectiveness (PUE)** — total facility power divided by IT equipment power; (2) **Carbon Usage Effectiveness (CUE)** — grams of CO2eq per kWh of IT energy; (3) **Water Usage Effectiveness (WUE)** — litres of water used per kWh of IT energy; (4) **Energy Reuse Effectiveness (ERE)** — how much waste heat is reused for heating buildings or other purposes.

### 8.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Power and Thermal Management in Heterogeneous Systems*.
- The Green Grid. (2040). *PUE: A Comprehensive Examination of the Metric*.

### 8.4 Discussion Questions
1. How does liquid cooling change the economics of data centre density, and what are the failure modes to consider?
2. Compare the thermal design power (TDP) of a modern CPU, GPU, NPU, and neuromorphic chip. What does TDP tell us about suitability for edge versus data centre deployment?
3. What are the challenges of measuring power consumption at the level of individual AI models running on an NPU?

---

ᚺ **Lecture 9: Security in Heterogeneous and Edge Environments**

### 9.1 Overview

Heterogeneous and edge computing introduce new attack surfaces and require rethinking traditional security assumptions. By 2040, securing the compute zoo involves protecting data in motion between accelerators, securing firmware on edge devices, and defending against side-channel attacks on specialized hardware.

### 9.2 Key Topics

- **Data in Motion Security:** (1) **In-Transit Encryption** — encrypting data as it moves between CPU and GPU memory; (2) **Secure Interconnects** — technologies like AMD's Infinity Fabric and NVIDIA's NVLink with built-in encryption; (3) **Attestation** — verifying that data hasn't been tampered with during transfer between accelerators.
- **Firmware Security:** (1) **Secure Boot** — ensuring that only trusted firmware runs on edge devices; (2) **Firmware Updates** — signed, encrypted, and rollback-protected updates for NPUs, neuromorphic chips, and FPGAs; (3) **Hardware Roots of Trust** — embedding cryptographic keys in hardware to establish a chain of trust.
- **Side-Channel Attacks:** (1) **Power Analysis** — measuring power consumption to infer cryptographic keys; (2) **Electromagnetic Emanations** — measuring RF leaks to infer internal operations; (3) **Timing Attacks** — measuring execution time to infer branches or memory access patterns; (4) **Countermeasures** — masking, shuffling, and constant-time implementations.
- **Physical Security:** (1) **Tamper Evidence** — seals and sensors that detect physical intrusion; (2) **Tamper Resistance** — making it difficult to open a device without triggering a response; (3) **Tamper Response** — zeroizing keys or erasing firmware upon detection of tampering.
- **Supply Chain Security:** (1) **Hardware Bill of Materials (HBOM)** — a machine-readable inventory of all components in a system; (2) **Trusted Foundries** — using semiconductor foundries with strict security controls; (3) **Component Authentication** — verifying that a chip is genuine and not a counterfeit.

### 9.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Security in Heterogeneous and Edge Computing*.
- FIDO Alliance. (2040). *FIDO2/WebAuthn: Public Credentials for the Web*.

### 9.4 Discussion Questions
1. How does the attack surface of an NPU differ from that of a CPU, and what new vulnerabilities does it introduce?
2. What are the challenges of securing firmware updates for edge devices that may be intermittently connected or physically inaccessible?
3. How should an organisation approach side-channel resistance when using accelerators for cryptographic operations?

---

ᚾ **Lecture 10: Observability and Debugging in Heterogeneous Systems**

### 10.1 Overview

Traditional observability tools (metrics, logs, traces) were designed for homogeneous CPU-centric systems. By 2040, observability must span CPUs, GPUs, NPUs, neuromorphic chips, FPGAs, and quantum accelerators to provide a complete picture of system behaviour and performance.

### 10.2 Key Topics

- **Unified Metrics:** (1) **Hardware Counters** — accessing performance counters across different architectures via vendor-specific APIs or open standards like PAPI; (2) **Utilization Metrics** — GPU utilization, NPU saturation, neuromorphic spike rate, FPGA logic utilization; (3) **Custom Metrics** — defining domain-specific metrics like "frames per second processed" or "inferences per joule"; (4) **Correlation** — aligning timestamps across different hardware clocks to correlate events.
- **Distributed Tracing:** (1) **Hardware-Assisted Tracing** — Intel Processor Trace, ARM CoreSight, and NVIDIA Nsight Trace for low-overhead tracing; (2) **Context Propagation** — ensuring that trace IDs flow correctly when a request moves from CPU to GPU to NPU; (3) **Span Attributes** — attaching hardware-specific information to spans (e.g., GPU kernel name, NPU core used); (4) **Visualization** — flame graphs that show time spent in CPU versus GPU versus NPU code.
- **Logging:** (1) **Structured Logging** — JSON logs that include hardware context (e.g., "executed on NPU core 3"); (2) **Rate Limiting** — preventing log spam from high-frequency hardware events; (3) **Centralized Aggregation** — forwarding logs from edge devices to central observability platforms.
- **Debugging:** (1) **Hardware Debuggers** — JTAG for FPGAs, GPU debuggers like cuda-gdb, and neuromorphic-specific debuggers; (2) **Simulators** — instruction-set simulators for testing code before it runs on hardware; (3) **Logging and Tracing** — using logging and tracing to reproduce issues; (4) **Post-Mortem Analysis** — analysing core dumps, crash dumps, and hardware error logs.

### 10.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Observability in Heterogeneous Computing Systems*.
- Khronos Group. (2040). *OpenCL 3.0 Specification*.

### 10.4 Discussion Questions
1. How do you correlate a log entry from an edge device with a metric spike in a central data centre when the clocks may not be synchronized?
2. What are the challenges of tracing a request that involves quantum acceleration, given the probabilistic nature of quantum computation?
3. How does observability change when moving from a cloud environment (centralized control) to an edge environment (distributed, intermittent connectivity)?

---

ᛁ **Lecture 11: Standards, Interoperability, and the Vendor Landscape**

### 11.1 Overview

By 2040, the hardware landscape is fragmented — different vendors use different interconnects, different programming models, and different security assumptions. Standards and interoperability layers are essential to avoid vendor lock-in and enable mixing and matching of components.

### 11.2 Key Topics

- **Interconnect Standards:** (1) **PCI Express 6.0** — 64 GT/s per lane, supports CXL 3.0 for memory expansion; (2) **CXL (Compute Express Link)** — open standard for memory semantics and coherency between CPU and accelerators; (3) **NVLink** — NVIDIA's high-bandwidth interconnect for GPU-GPU and GPU-CPU communication; (4) **Infinity Fabric** — AMD's interconnect for CPU-GPU and CPU-FPGA communication; (5) **Ethernet** — 400GbE and 800GbE for connecting accelerators and servers in a rack.
- **Programming Model Standards:** (1) **OpenCL** — open standard for heterogeneous computing (CPU, GPU, FPGA, accelerators); (2) **SYCL** — C++ abstraction layer for OpenCL, enabling single-source heterogeneous programming; (3) **oneAPI** — Intel's open, cross-architecture programming model (C++, Python); (4) **Vulkan Compute** — compute shaders in the Vulkan graphics API for GPU compute; (5) **TensorFlow Lite Delegates** — mechanism to delegate TensorFlow Lite inference to NPUs, DSPs, or other accelerators.
- **Security Standards:** (1) **TPM 3.0** — Trusted Platform Module with support for measuring and attesting heterogeneous accelerators; (2) **FIDO2/WebAuthn** — public-key credentials for device authentication; (3) **Secure Boot Variants** — UEFI Secure Boot, SBAT (Shell-Based Attack Protection), and platform-specific solutions for edge devices.
- **Vendor Landscape:** (1) **Established Players** — Intel (CPUs, NPUs, FPGAs), AMD (CPUs, GPUs, FPGAs), NVIDIA (GPUs, DPUs), Qualcomm (NPUs), IBM (neuromorphic, quantum); (2) **Specialists** — Graphcore (IPUs for AI), Cerebras (wafer-scale engines), SambaNova (reconfigurable dataflow units); (3) **Emerging** — photonic quantum companies, neuromorphic startups, edge AI accelerator vendors.

### 11.3 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- UoY Architecture Lab. (2040). *Standards in Heterogeneous Computing*.
- PCI-SIG. (2040). *PCI Express Base Specification 6.0*.

### 11.4 Discussion Questions
1. How does CXL change the traditional CPU-memory boundary, and what new capabilities does it enable for accelerators?
2. Compare OpenCL, SYCL, and oneAPI as heterogeneous programming models. When would you choose each?
3. What are the challenges of establishing a hardware root of trust on an edge device that lacks a TPM or equivalent security module?

---

ᛃ **Lecture 12: The Future of Compute — 2050 and Beyond**

### 12.1 Overview

As we conclude IT403, let us look forward to the hardware landscape of 2050. The trends we see in 2040 — specialization, heterogeneity, energy efficiency, and edge intelligence — will continue and intensify. New architectures will emerge, and the IT professional's role will continue to evolve from hardware-agnostic to hardware-savvy.

### 12.2 Emerging Technologies

**Photonic Computing:** Using light instead of electricity for data transmission and computation. By 2050, photonic chips may handle specific workloads (matrix multiplication, Fourier transforms) with femtojoule-per-operation energy efficiency and terahertz bandwidth.

**Memristor-Based Computing:** Resistance-changing devices that combine memory and computation. Crossbar arrays of memristors can perform analog matrix-vector multiplication in a single step, promising extreme efficiency for neural networks.

**DNA-Based Computing:** Using biochemical reactions to perform computation. While slow, DNA computing offers massive parallelism for specific problem classes (satisfiability, cryptanalysis) and inherent biocompatibility for biomedical applications.

**3D-Stacked Heterogeneous Integration:** Moving beyond 2D chiplets to true 3D integration — stacking CPUs, GPUs, NPUs, and memory in a single package with micrometer-scale interconnects, enabling unprecedented bandwidth and energy efficiency.

**Ambient Computing:** Computing that disappears into the environment — walls, furniture, and clothing embedded with sensors and processors that respond to gestures, voice, and environmental changes without explicit devices.

### 12.3 The Evolving Role of the IT Professional

By 2050, the IT professional will not be a hardware specialist — but they will be hardware-*literate*. The architecture diagrams they draw will show not just "application server" and "database" but specific accelerator types and data movement patterns. Their troubleshooting will include checking NPU utilization and neuromorphic spike rates, not just CPU load and memory usage. Their procurement will consider not just performance per dollar but performance per joule and compliance with corporate sustainability goals.

### 12.4 The Norse Frame: The Smiths of Valkyrie

In Norse mythology, the valkyries choose who lives and dies in battle, but their weapons and armor are forged by the dwarven smiths — masters of their craft who understand the properties of metal, the secrets of the forge, and the rituals that make a blade true. The IT professional of 2050 is one of these smiths — not forging swords, but understanding the properties of silicon, gallium nitride, and photonic crystals; mastering the software forges that turn sand into sense; and knowing the rituals that make a system true — reliable, efficient, and secure.

The Norns spin the threads of fate, but it is the smiths who shape the tools that cut those threads. May your forges burn bright, and may your systems run true.

### 12.5 Required Reading
- Hennessy, J., & Patterson, D. (2038). *Computer Architecture: A Quantitative Approach* (7th ed.).
- Mead, C. (1989). *Analog VLSI: Implementation of Neural Systems*. Springer. (A foundational text on neuromorphic engineering.)
- UoY Foresight Report FR-2040-05. *Computing 2050: Scenarios and Implications*.

### 12.6 Discussion Questions
1. If photonic computing delivers on its promise of femtojoule-per-operation energy efficiency, how would that change the economics of data centres and the feasibility of always-on AI everywhere?
2. DNA-based computing is inherently slow but massively parallel. What problem classes would benefit most from this trade-off, and what applications would be unsuitable?
3. What is the single most important hardware trend that IT professionals should prepare for over the next decade, and why?

---

## Final Examination Preparation

### Format
The final examination consists of two components:

**Part A — Written Examination (60%):** Choose 4 of the following 8 essay questions. Essays should demonstrate understanding of architectural trade-offs, the implications of hardware specialization, and the skills needed to navigate the heterogeneous compute landscape of 2040.

**Part B — Practical Design Exercise (40%):** You will be given a scenario — an application description, workload characteristics, and constraints (latency, bandwidth, power, cost) — and must produce: a heterogeneous architecture diagram with compute placement, data flow, and synchronization points; a justification for each architectural choice; and a bill of materials with estimated costs.

### Part A — Essay Questions (Choose 4 of 8)

1. **The End of Von Neumann:** Argue for or against the proposition: "By 2050, the von Neumann architecture will be relegated to legacy systems and niche applications, with the majority of new computing happening in post-von-Neumann alternatives." Use the lectures on von Neumann bottleneck, Dennard scaling, and the 2040 compute landscape to support your position.

2. **Neuromorphic vs. NPU for Edge AI:** Compare neuromorphic chips (Intel Loihi, IBM NorthPole) and neural processing units (Qualcomm Hexagon, Apple Neural Engine) for edge AI workloads. Consider energy efficiency, programmability, maturity of tooling, and suitability for specific workloads (always-on sensing, image classification, audio processing).

3. **Edge Computing and the Cloud:** Edge computing is often positioned as a replacement for cloud computing. Analyse this claim. Is edge a complement, a competitor, or something else? Use the lectures on why edge, the edge-cloud continuum, and edge deployment patterns to support your position.

4. **Heterogeneous Orchestration:** Compare Kubernetes device plugins, custom AI-driven schedulers, and workflow engines (Argo, Airflow) for orchestrating heterogeneous workloads. When is each approach appropriate, and what are the limitations of each?

5. **Processing-in-Memory:** Evaluate the promise of processing-in-memory for memory-bound workloads. Consider the lectures on PIM architectures, applications, and programming models. What are the remaining barriers to widespread adoption, and when would you choose PIM over traditional CPU-GPU approaches?

6. **Quantum Accelerators:** For what classes of problems do quantum accelerators provide a demonstrable advantage over classical heuristics? Use the lectures on quantum annealers, gate-based quantum computers, and photonic quantum computers to support your position.

7. **Security in Heterogeneous Systems:** Heterogeneous and edge computing introduce new attack surfaces. Analyse the lectures on data in motion security, firmware security, side-channel attacks, and physical security. What is the most significant new vulnerability introduced by heterogeneous computing, and how would you mitigate it?

8. **The Future of Compute:** Look ahead to 2050. Which of the emerging technologies (photonic, memristor, DNA-based, 3D-stacked, ambient) do you think will have the most significant impact, and why? Consider technical feasibility, ecosystem readiness, and the problems they solve.

### Part B — Practical Design Exercise Brief

**Scenario**: WildLifeTrack, a conservation NGO, deploys 5,000 solar-powered camera traps in remote national parks to monitor endangered species. Each camera trap captures 1080p video at 10 fps and must: (1) detect animals in real-time with < 200ms latency; (2) classify species (tiger, elephant, poacher, etc.) with 95%+ accuracy; (3) transmit only metadata (species, timestamp, location, confidence) to reduce satellite bandwidth costs; (4) operate for 6 months on a single battery charge; (5) withstand temperatures from -20°C to 50°C; (6) be upgradable over-the-air with new models.

**Deliverables**:
1. Architecture diagram showing compute placement (camera trap, edge gateway, regional data center, cloud) and data flow (video, metadata, commands).
2. Justification for each architectural choice (why a specific accelerator is used where, data movement considerations, synchronization points).
3. Bill of materials with estimated costs (camera trap hardware, edge gateway, regional data center, cloud services).
4. Operational considerations (power management, thermal management, security, observability, model updates).

---

*ᚱᚢᚾᚨ — Runa Gridweaver Freyjasdottir wove this knowledge-weft. May the Norns guide your hand as you shape the compute of tomorrow.*
