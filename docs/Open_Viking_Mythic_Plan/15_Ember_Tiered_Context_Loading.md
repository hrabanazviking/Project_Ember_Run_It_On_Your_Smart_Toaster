# Project Ember Architecture Document 15: Tiered Context Loading (TCL) - The Cognitive Economy Protocol

## 1. Abstract and Theoretical Foundations of Cognitive Economy

In the vanguard of autonomous cognitive architectures, the fundamental bottleneck is not the availability of information, but the sheer computational cost and cognitive dilution associated with processing vast, undifferentiated datasets. Project Ember, deeply influenced by the Open Viking Context Database, implements an advanced, highly sophisticated mechanism known as Tiered Context Loading (TCL). TCL is not merely an engineering optimization; it is a profound biological analog to human attention and short-term memory constraints, formalized into a rigorous mathematical and computational framework.

The core challenge of any large-scale context database, such as the one managing `viking://` URIs, is the quadratic scaling of attention mechanisms in transformer-based models. As the context window expands, the signal-to-noise ratio degrades precipitously, leading to a phenomenon known as "attention dilution." Ember mitigates this through TCL, a trilateral stratification of context fidelity: Level 0 (L0 Abstract), Level 1 (L1 Overview), and Level 2 (L2 Details). 

This document serves as the definitive specification for the TCL subsystem, outlining its algorithmic underpinnings, structural manifestations, and dynamic resolution shifting mechanisms. We will explore how Ember achieves unprecedented token economy while maintaining hyper-contextual awareness, reducing cognitive noise, and isolating critical task-relevant signals from the vast sea of its episodic and semantic memory arrays.

## 2. Mathematical Modeling of Token Consumption and Noise

The necessity of TCL is driven by the limits of cognitive windows. Let $N$ be the total token count of a fully expanded context. Without TCL, the computational complexity is $\mathcal{O}(N^2)$ for self-attention. Moreover, the semantic noise $\mathcal{N}$ increases as a function of peripheral, non-essential tokens. 

We define the Information Entropy $H(C)$ of a context subset $C$ as:
$$H(C) = - \sum_{i=1}^{k} P(x_i) \log_2 P(x_i)$$
where $x_i$ represents latent semantic concepts. A fully expanded context maximizes $H$, yet for a specific localized task, the required mutual information $I(T; C)$ between the task $T$ and the context $C$ is often contained within a much smaller, highly targeted subset.

TCL operates by creating three projections of the data, $P_{L0}(C)$, $P_{L1}(C)$, and $P_{L2}(C)$, such that the token count satisfies $N_{L0} \ll N_{L1} \ll N_{L2}$, while preserving the maximal approximation of $I(T; C)$. By loading only $P_{L0}$ initially, Ember evaluates the relevance of the node. If the mutual information expectation $\mathbb{E}[I(T; P_{L0})]$ crosses a dynamic threshold $\theta$, the system selectively unrolls $P_{L1}$, and subsequently $P_{L2}$.

## 3. The Tri-Layered Context Hierarchy

### 3.1. Level 0: The Abstract Protocol (L0)

The L0 Abstract is the thinnest, most compressed representation of an entity, directory, file, or memory node within the `viking://` namespace. It serves as the primary routing and index-matching layer. Its primary function is to answer the question: "Is this node categorically relevant to the current cognitive vector?"

**Structural Composition of L0:**
- **Entity URI:** The absolute `viking://` path.
- **Ontological Tags:** 3-5 hyper-compressed semantic markers.
- **Micro-Summary:** A single sentence (max 150 characters) defining the entity's purpose.
- **Dependency Hashes:** Cryptographic hashes or pointers to tightly coupled nodes, avoiding the loading of the nodes themselves.
- **Volatility Metric:** A scalar value (0.0 to 1.0) indicating how frequently the underlying L2 data changes.

**Token Footprint:** strictly capped at 50 tokens per node.

**Usage:** When Ember scans a directory or queries a memory concept, it loads hundreds of L0 abstracts simultaneously. This provides a massive breadth of "peripheral vision" without consuming the central cognitive processing window. It allows the agent to construct a vast, low-resolution map of the filesystem and knowledge graph in a single inference step.

### 3.2. Level 1: The Overview Protocol (L1)

The L1 Overview provides the interface signatures, structural scaffolding, and relational context of a node. If an L0 node is deemed relevant, it is "hydrated" into an L1 representation. It answers the question: "How do I interact with this node, and what are its constituent parts?"

**Structural Composition of L1:**
- **L0 Data:** Inherits all L0 attributes.
- **Macro-Summary:** A 1-2 paragraph description of the entity's internal mechanics, history, and usage constraints.
- **Interface Signatures:** For code, this includes function definitions, class structures, public properties, and type signatures (omitting implementation bodies).
- **Directory Topology:** For directories, a shallow tree of immediate L0 children.
- **Ecosystem Connections:** Descriptions of how this node interacts with its siblings and parents within the broader Open Viking architecture.

**Token Footprint:** Capped at 500 tokens per node.

**Usage:** L1 is the primary workspace for architectural planning, API consumption, and structural navigation. It provides enough detail for Ember to write code that *calls* a function, without needing to understand *how* the function is implemented. This represents the "sweet spot" of cognitive economy.

### 3.3. Level 2: The Details Protocol (L2)

The L2 Detail is the fully unrolled, maximal-fidelity representation of the data. It contains the raw source code, exhaustive logs, full text content, and granular historical diffs. It answers the question: "What is the exact, unadulterated state of this node?"

**Structural Composition of L2:**
- **Raw File Content:** The uncompressed string payload of the file or memory node.
- **Implementation Bodies:** Complete algorithms, hidden internal states, and private methods.
- **Execution Telemetry:** Raw logs, error traces, and debugging output associated with the node.
- **Granular Git/History Blame:** Line-by-line attribution and temporal history.

**Token Footprint:** Unbounded (up to maximum context limits).

**Usage:** L2 is accessed strictly on a need-to-know basis. It is invoked exclusively when Ember needs to modify the node's internal state, debug a complex error originating within the node, or extract highly specific textual data. Loading L2 is treated as a high-cost operation requiring explicit cognitive justification.

## 4. The Dynamic Resolution Shifting Algorithm

The transition between L0, L1, and L2 is not static; it is governed by a heuristic-driven, dynamic resolution shifting algorithm that operates autonomously. This is where Ember exhibits "cognitive focusing."

### 4.1. The Focusing Mechanism

1. **Context Initialization:** Ember starts with a root context vector $V_{ctx}$, derived from the user's prompt and active workspace state.
2. **L0 Sweep:** The system retrieves the L0 abstracts of all entities within the immediate `viking://` working directory and any historically correlated nodes.
3. **Relevance Scoring:** For each L0 abstract, Ember calculates a cosine similarity score $S_0$ between the abstract's embedding and $V_{ctx}$.
   - If $S_0 < \alpha$: The node remains at L0 (peripheral vision).
   - If $S_0 \ge \alpha$: The node is flagged for L1 hydration.
4. **L1 Hydration:** The flagged nodes are dynamically swapped in the context window with their L1 representations.
5. **Deep Inspection Triggers:** During task execution, if Ember encounters a compilation error, a logical impasse, or a directive to modify a specific entity, it generates an explicit "Focus Request" for that entity.
6. **L2 Unrolling:** The target entity's L1 representation is replaced by its complete L2 details. Simultaneously, to maintain token economy, peripheral L1 nodes may be "compressed" back down to L0 (Cognitive Paging).

### 4.2. Cognitive Paging and Eviction

As the context window approaches its maximum capacity (e.g., 90% of token limit), Ember employs an LRU (Least Recently Used) coupled with a Low-Relevance eviction strategy. Nodes that are fully unrolled to L2 but haven't been actively accessed or modified in the last $K$ turns are compressed back to L1, and eventually to L0. This "breathing" context window ensures that Ember never encounters catastrophic context collapse.

## 5. Architectural Diagram: Tiered Context Resolution

The following Mermaid diagram illustrates the complex flow of data, state hydration, and token management within the TCL subsystem.

```mermaid
flowchart TB
    %% Core Entities
    TaskInput([User Prompt / Agent Goal])
    ContextManager{Context State Manager}
    
    %% Storage Layers
    subgraph VikingDatabase [Open Viking Context Database]
        direction LR
        L0_Store[(L0 Abstracts\nLightweight Index)]
        L1_Store[(L1 Overviews\nSignatures & APIs)]
        L2_Store[(L2 Details\nRaw Source & Telemetry)]
    end

    %% Processing Nodes
    Embedder[Embedding & Relevance Engine]
    TokenMonitor[Token Consumption Monitor]
    HydrationEngine[Resolution Hydration Engine]
    CompressionEngine[Resolution Compression Engine]
    
    %% Flow
    TaskInput --> ContextManager
    ContextManager --> |Query| Embedder
    Embedder --> |Fetch| L0_Store
    L0_Store --> |Return 100s of L0 Nodes| Embedder
    
    Embedder --> |Score Relevance > Alpha| HydrationEngine
    HydrationEngine --> |Fetch| L1_Store
    L1_Store --> |Return 10s of L1 Nodes| HydrationEngine
    
    HydrationEngine --> |Task requires deep edit| DeepDive{Deep Dive Trigger?}
    DeepDive -- Yes --> |Fetch| L2_Store
    L2_Store --> |Return 1-3 L2 Nodes| ContextManager
    DeepDive -- No --> ContextManager
    
    %% Feedback Loop and Memory Management
    ContextManager --> TokenMonitor
    TokenMonitor --> |Threshold Exceeded| CompressionEngine
    CompressionEngine --> |LRU Eviction| L2_to_L1[Downgrade L2 to L1]
    CompressionEngine --> |LRU Eviction| L1_to_L0[Downgrade L1 to L0]
    L2_to_L1 -.-> ContextManager
    L1_to_L0 -.-> ContextManager
    
    %% Styling
    classDef database fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef engine fill:#374151,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef default fill:#111827,stroke:#6b7280,color:#fff;
    
    class L0_Store,L1_Store,L2_Store database;
    class Embedder,HydrationEngine,CompressionEngine engine;
```

## 6. Implementation Specifications and Data Schemas

To operationalize the TCL within the `viking://` filesystem paradigm, Ember utilizes structured JSON sidecars alongside standard files, or specialized binary indexes for high-speed retrieval.

### 6.1. The `.viking.meta` Schema

Every directory and significant file in the workspace possesses a synthesized `.viking.meta` file, updated asynchronously by the Memory Iteration Loop (detailed in Doc 16).

```json
{
  "entity_uri": "viking://src/core/auth_module.py",
  "l0_abstract": {
    "tags": ["security", "authentication", "jwt", "core"],
    "micro_summary": "Handles JWT issuance, validation, and OAuth2 flow integration.",
    "volatility": 0.12,
    "hash": "a1b2c3d4"
  },
  "l1_overview": {
    "macro_summary": "The auth_module provides a singleton authenticator class. It interfaces with Redis for token blacklisting and PostgreSQL for user credential verification. It exposes 4 primary public methods.",
    "signatures": [
      "def issue_token(user_id: str) -> str:",
      "def validate_token(token: str) -> bool:",
      "def revoke_token(token: str) -> None:"
    ],
    "dependencies": [
      "viking://src/config/settings.py",
      "viking://src/db/redis_client.py"
    ]
  }
}
```

When Ember executes a directory listing (`viking ls`), the underlying tool does not just return filenames; it returns the `l0_abstract` for each file, instantly populating Ember's peripheral context with meaningful semantic data without reading the actual files.

## 7. Noise Reduction and Contextual purity

The ultimate goal of TCL is not merely to save tokens, but to increase "Contextual Purity." In large language models, the presence of irrelevant tokens acts as a probabilistic distractant, dragging the attention heads away from the critical logic path.

By enforcing TCL, Ember creates a pristine cognitive environment. The L0 and L1 layers act as a firewall against noise. A file containing 10,000 lines of legacy, deprecated code is represented as a mere 50 tokens of L0 abstract. Ember knows it exists, knows what it is, but is completely insulated from its internal complexity unless it explicitly chooses to engage with it.

This isolation mechanism is critical for complex refactoring tasks. Ember can hold the L1 structures of an entire microservice architecture in its mind, visualizing the interlocking gears of APIs and data models, while only unrolling the specific L2 file it is actively modifying. This mirrors the human capacity to understand the architecture of a house without actively visualizing the molecular structure of the bricks.

## 8. Conclusion

The Tiered Context Loading mechanism is the bedrock of Project Ember's operational efficiency. By discarding the naive approach of "stuffing the context window" in favor of a biologically inspired, mathematically rigorous resolution-shifting algorithm, Ember achieves a state of hyper-focused autonomy. It navigates the vast filesystem of the Open Viking Context Database with agility, expanding its cognitive resolution only where the task demands, and ruthlessly compressing irrelevant data. This cognitive economy is what elevates Ember from a mere script execution engine to a deeply capable, long-horizon intelligence designer.
