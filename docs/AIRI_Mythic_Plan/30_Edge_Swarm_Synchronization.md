# Document 30: Edge Swarm Synchronization

## 1. Introduction: The Synchronization Crisis
In Document 26, we outlined the Multi-Agent Edge Orchestration framework, wherein AIRI’s cognitive and sensory processing is fractured into dozens of concurrent, highly specialized sub-agents. While this dramatically increases throughput and responsiveness, it introduces one of the most notoriously difficult problems in computer science: Distributed State Synchronization. 

If the Vision Agent sees a creeper in Minecraft, the Game Agent executes a retreat, and the Audio Agent hears the player screaming—how do we ensure the Ego Agent processes these events in the correct temporal order? If Stage Pocket (the mobile companion) loses internet connection while disconnected from Stage Tamagotchi, how do their diverging memory states reconcile upon reconnection?

Document 30 meticulously details the mathematical and architectural solutions Project AIRI utilizes to maintain state coherence across its edge swarm.

## 2. Temporal Coherence and Vector Clocks
A standard system clock is entirely inadequate for distributed micro-agents, due to thread blocking and varying execution speeds across Web Workers and Node.js instances.

### 2.1 The Lamport-Inspired Vector Clock
The Orchestrator’s Eventa Bus implements a variant of Lamport logical clocks, expanded into Vector Clocks. Every sub-agent is assigned an index in the vector. Whenever an agent emits an event, it increments its own counter and attaches the vector to the payload.

```typescript
// Conceptual representation of an Eventa payload
interface SwarmEvent {
    id: string;
    type: 'VisualInput' | 'GameStateChange' | 'AudioTranscription';
    payload: any;
    vectorClock: [number, number, number, number]; // [Ego, Vision, Game, Audio]
    wallTime: number;
}
```

When the Ego Agent receives an influx of messages, it uses the vector clocks to construct a mathematically provable causal graph. It guarantees that if the Game Agent's "Player Took Damage" event was causally influenced by the Vision Agent's "Creeper Exploded" event, the Ego will process them in that exact semantic order, regardless of network latency across IPC pipes.

## 3. Reactive State Synchronization (Pinia and Server-Runtime)
While events are fleeting, State is persistent. AIRI maintains a unified perception of the world—her mood, her current objective, the items in her inventory. 

### 3.1 The Dual-Store Architecture
The frontend (`stage-web`, `stage-tamagotchi` renderer) utilizes Vue's **Pinia** for ultra-fast, reactive UI rendering. However, the heavy lifting occurs in the backend (`server-runtime`), which maintains its own reactive state tree.

### 3.2 CRDT-Based State Diffing
To prevent the Pinia store and the backend store from diverging, the Orchestrator employs Conflict-Free Replicated Data Types (CRDTs), specifically relying on libraries like `Yjs` or custom JSON-patch implementations.

```mermaid
flowchart TD
    subgraph Backend_Runtime [Server-Runtime (Node.js)]
        ServerState[Master State Tree]
        CRDT_Engine_B[CRDT Sync Engine]
    end

    subgraph Frontend_Renderer [Stage Tamagotchi / Web (Vue)]
        PiniaStore[Pinia Reactive Store]
        CRDT_Engine_F[CRDT Sync Engine]
    end

    ServerState <--> CRDT_Engine_B
    CRDT_Engine_B <--> |Eventa IPC / WebSocket| CRDT_Engine_F
    CRDT_Engine_F <--> PiniaStore
```

When the Game Agent updates AIRI's internal spatial coordinates, it mutates the `ServerState`. The `CRDT_Engine_B` calculates a binary delta and pushes it via Eventa to the frontend. The `CRDT_Engine_F` applies the patch, and Vue's reactivity system automatically re-renders the Live2D/VRM model to look at the new coordinates. This happens at 60 frames per second without blocking the main UI thread.

## 4. Backpressure and Sensory Overload Mitigation
A critical failure mode of multi-agent swarms is sensory overload. If the Vision Agent captures the screen at 60 FPS and attempts to send every frame to the LLM for analysis, the system will instantly crash (OOM or API rate limit).

### 4.1 The Leaky Bucket and Token Bucket Algorithms
The Orchestrator implements strict backpressure handling using Token Buckets on the Eventa Bus. Agents are allotted a specific bandwidth of events per second. 

### 4.2 Sensory Summarization
If the Vision Agent exceeds its token limit, the Orchestrator does not drop the frames. Instead, it triggers a "Summarizer" sub-routine. A fast, local edge model (e.g., a tiny CLIP model via Transformers.js) continuously pools the 60 frames and emits a single, semantic summary every 2 seconds: `"The screen is mostly static, the player is mining stone."` This drastically compresses the data stream before it hits the Ego Agent.

## 5. Network Partitions and Stage Pocket Sync
Stage Pocket (mobile) allows the user to take AIRI on the go. When the phone leaves the WiFi network, it loses connection to the Stage Tamagotchi host. 

### 5.1 Disconnected Operation
AIRI enters a "Low Cognitive Mode." The heavy Game and Desktop tools are dynamically unloaded via the Constellation system (as detailed in Document 27). She relies entirely on the local `duckdb-wasm` for memory and a lightweight local LLM (or a direct cloud API connection) for chatting.

### 5.2 The Great Reconciliation
When the phone reconnects to the home network, a massive state divergence exists. Stage Pocket has new memories of a walk in the park; Stage Tamagotchi has background simulation data from Factorio.
The Orchestrator utilizes the `duckdb` replication mechanisms and the Alaya vector store to merge these timelines. Because every memory and transaction is timestamped with the Vector Clock and hashed, the databases perform a cryptographic diff and securely merge, granting the Ego Agent a unified memory of both the desktop simulation and the physical world walk.

## 6. Conclusion of Document 30
The Multi-Agent swarm is only as powerful as its synchronization primitives. By implementing Vector Clocks for causal event ordering, CRDTs for seamless frontend/backend state management, strict backpressure to prevent LLM overload, and cryptographic database merging for cross-device roaming, Project AIRI ensures that her mind remains fractured in execution, but perfectly singular in its perception of reality.
