# WaifuOS Document 30: Edge Compute Resource Allocation

## 1. Executive Summary & Edge Reality

Project Ember envisions a WaifuOS ecosystem that is not tethered to a massive, centralized server farm, but rather distributed across the chaotic, heterogenous landscape of edge computing. In this environment, resources are scarce, volatile, and highly asymmetrical. A user might interact with their waifu via a high-end gaming PC, a mid-range smartphone, and a low-power smart speaker simultaneously. 

The Edge Compute Resource Allocation (ECRA) module is the critical intelligence that decides *where* computation happens. It balances the conflicting demands of latency, privacy, battery life, and thermal limits to ensure the waifu remains responsive without degrading the host hardware. As THOR, the Skills Forgemaster, mastering this allocation is essential; a brilliant tool is useless if executing it melts the user's phone.

## 2. Dynamic Resource Profiling

ECRA relies on continuous, lightweight telemetry from all nodes within the user's localized mesh.

### Hardware Profiling
Upon connection, a WaifuOS edge node (e.g., the mobile app) sends a hardware manifest to the Hub:
*   CPU Architecture (e.g., ARM64, x86_64)
*   Available NPU/GPU capabilities (e.g., Apple Neural Engine, Tensor Cores)
*   Total and Free RAM

### Real-Time State Profiling
Hardware is static, but state is dynamic. Nodes continuously broadcast:
*   Battery Level and Charging Status
*   Thermal Throttling State (e.g., OS thermal level warnings)
*   Network Connectivity Quality (Bandwidth and Latency to the Hub)

## 3. Task Quantization and Partitioning

Not all tasks are monolithic. ECRA employs task partitioning to split workloads.

### The Speech Pipeline Example
Consider the WaifuOS speech pipeline: LLM Generation -> Text-to-Speech (TTS).
*   **Scenario A (High-Power Desktop):** The Hub sends the user's audio. The desktop performs local STT, runs a large local LLM, and synthesizes TTS via VOICEVOX locally. Latency is near zero; privacy is absolute.
*   **Scenario B (Low-Power Phone on Battery):** The phone streams compressed audio to the Hub. The Hub runs STT, the LLM, and Azure TTS. The Hub streams the final audio back to the phone. The phone merely acts as a dumb terminal, saving battery.
*   **Scenario C (Hybrid Edge):** The phone has a capable NPU but low battery. ECRA decides the phone will run STT locally (for privacy and low latency wake-word detection), sends the text to the Hub for LLM reasoning, and the Hub sends text back to the phone where a lightweight, quantized TTS model synthesizes the voice locally.

## 4. Network Latency vs Compute Tradeoffs

ECRA utilizes a dynamic cost function to make routing decisions. The cost $C$ of executing a task $T$ on node $N$ is calculated as:

$$ C(T, N) = w_1 \cdot L(N) + w_2 \cdot E(T, N) + w_3 \cdot P(T, N) $$

Where:
*   $L(N)$ is the estimated network latency to send inputs to and receive outputs from node $N$.
*   $E(T, N)$ is the estimated execution time of task $T$ on the specific hardware of node $N$.
*   $P(T, N)$ is the estimated power cost/thermal impact of task $T$ on node $N$.
*   $w_1, w_2, w_3$ are dynamic weights adjusted based on the current context (e.g., if the user is in a fast-paced conversation, $w_1$ (latency) is prioritized. If the device is at 10% battery, $w_3$ (power) overrides all).

## 5. Thermal and Power Management Constraints

WaifuOS respects the physical host. If a node reports a high thermal state, ECRA immediately places a "Compute Embargo" on that node.

### The Cooling Handoff
If a user is having a long, computationally heavy conversation on their phone causing it to heat up, ECRA will seamlessly shift the heavy lifting (LLM, TTS) to the centralized Hub or a nearby idle node (like a plugged-in tablet), instructing the phone to only handle network streaming and UI rendering. To the user, the waifu's response time might increase by 100ms, but their device is protected from thermal damage.

## 6. The Allocation Algorithm

ECRA operates as a continuous auction. When a task is generated, the Hub acts as the auctioneer.

### Mermaid Diagram: Resource Allocation Auction

```mermaid
graph TD
    Task[Task Generated: Synthesize Audio 'Hello User'] --> Hub[Hub: Initiates Auction]
    
    Hub -->|Broadcast Request| Node1(Node 1: High-End PC)
    Hub -->|Broadcast Request| Node2(Node 2: Smartphone)
    
    Node1 -.->|Bid: Exec=50ms, Latency=5ms, Power=Low Impact| Hub
    Node2 -.->|Bid: Exec=300ms, Latency=2ms, Power=High Impact(Battery)| Hub
    
    Hub -->|Evaluate Cost Function| Decision{Select Optimal Node}
    
    Decision -->|Winner| Node1
    Node1 -->|Execute & Return Result| Hub
```

## 7. Edge Node Lifecycle Management

Nodes in an edge environment are ephemeral. They drop off Wi-Fi, run out of battery, or go to sleep.

ECRA handles node disappearance gracefully. If a node is executing a task and stops sending heartbeats, ECRA instantly re-queues the task for the next best available node. If the task was state-mutating (e.g., writing to a database), ECRA relies on the transactional guarantees of the WaifuOS data layer to ensure the operation is either rolled back or completed idempotently by the new node, preventing data corruption.

## 8. Conclusion

The Edge Compute Resource Allocation system is the invisible conductor of the WaifuOS symphony. It transforms a disparate collection of devices into a unified, intelligent swarm. By meticulously balancing the physics of the hardware with the cognitive demands of the software, ECRA ensures that the digital companion forged in Project Ember remains a helpful, pervasive presence, rather than a resource-draining burden.
