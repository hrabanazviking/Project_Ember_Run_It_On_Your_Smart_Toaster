# 06: L0-L1-L2 Caching for Variable Performance Scaling

## 1. The Physics of the Swarm

I am ODIN, the Grand Architect. We have conceptualized the Omni-Brain, the Edge-Compute Mesh, Recursive Retrieval, Telemetry, and Self-Iteration. However, grand theories shatter upon the jagged rocks of physical reality. The reality of a multi-device swarm is one of brutal constraints: limited battery life, constrained thermal envelopes, throttled bandwidth, and disparate VRAM availability.

Project Ember must run on a $10,000 liquid-cooled workstation and a $100 smartwatch simultaneously, acting as a singular mind. This requires an absolute mastery of Variable Performance Scaling. The mechanism for this mastery is the aggressive, mathematically rigorous caching of OpenViking’s L0, L1, and L2 tiers.

## 2. The Anatomy of the Tiers

To build a flawless caching strategy, we must deeply understand the physical footprint of the context layers defined by OpenViking.

- **L0 (Abstract)**: 
  - *Content*: A one-sentence semantic summary.
  - *Size*: ~100-200 bytes.
  - *Function*: Rapid routing, intent matching, and swarm-wide omniscience.
- **L1 (Overview)**: 
  - *Content*: Structural summary, key points, API signatures.
  - *Size*: ~2-5 kilobytes.
  - *Function*: Intermediate reasoning, determining if L2 is strictly necessary, providing "good enough" context for tactical tasks.
- **L2 (Details)**: 
  - *Content*: The absolute raw data. Source code, full PDFs, massive logs.
  - *Size*: Megabytes to Gigabytes.
  - *Function*: Deep extraction, deterministic problem solving, final synthesis.

## 3. The Caching Matrix

Project Ember does not treat all devices equally. Devices are classified into a Node Topology, and their caching permissions are strictly defined by their hardware capabilities.

### 3.1 Tier 3: Micro-Nodes (Wearables, IoT)
*Hardware Profile*: Microcontroller, KB of RAM, extreme battery constraints.
*Caching Strategy*: **L0 Strict**.
- Micro-nodes are only permitted to cache a highly pruned subset of the L0 gossip ring. They hold the abstracts for immediate user preferences and highly utilized agent skills. 
- They never download L1 or L2 data. If a user asks a smartwatch a complex question, the smartwatch uses its L0 cache to identify the target directory, and instantly delegates the entire L1/L2 operation to a Meso or Macro node.

### 3.2 Tier 2: Meso-Nodes (Smartphones, Tablets)
*Hardware Profile*: ARM processors, 8-16GB RAM, thermal throttling.
*Caching Strategy*: **L0 Complete, L1 Dynamic, L2 Ephemeral**.
- Meso-nodes hold the *entire* L0 mesh index in memory. They know where everything is.
- They aggressively cache L1 overviews for active projects.
- They only download L2 data ephemerally. Once an L2 payload is processed for a specific user query, it is flushed from the Meso-node's memory to save space, relying on the Macro-nodes to store it permanently.

### 3.3 Tier 1: Macro-Nodes (Desktops, Home Servers)
*Hardware Profile*: x86/ARM heavy compute, 32GB+ RAM, dedicated GPUs.
*Caching Strategy*: **L0, L1, L2 Persistent**.
- Macro-nodes are the vaults. They maintain the full, uncompressed OpenViking database on NVMe storage. 
- They serve as the definitive source of truth when edge devices request L2 data.

## 4. The Predictive Pre-Fetching Algorithm

Latency is the enemy of a seamless swarm experience. If a smartphone (Meso-node) realizes it needs L2 data and has to request it from the Desktop (Macro-node) over a crowded Wi-Fi network, the user experiences a lag spike.

Project Ember utilizes **Predictive Pre-Fetching**, powered by the Telemetry data discussed in Doc 04.

### 4.1 Temporal-Spatial Heuristics
The swarm learns the user's habits.
- *Observation*: Every weekday at 9:00 AM, the user opens their laptop and queries `viking://resources/work_codebase/`.
- *Action*: At 8:45 AM, the Home Server silently pushes the updated L1 and L2 caches of `work_codebase/` to the laptop. When the user opens the laptop, the context is already local. Latency is zero.

### 4.2 Cross-Device Intent Bleed
When a user begins an action on one device, the swarm prepares the others.
- *Observation*: The user is on their smartphone, looking at a GitHub issue regarding a memory leak in a specific repository. The L0 gossip ring broadcasts that the smartphone is evaluating `viking://resources/repo_x/issues/mem_leak`.
- *Action*: The swarm knows that debugging memory leaks usually requires heavy compute. The Desktop (Macro-node) immediately pre-fetches the massive L2 source code for `repo_x` from cold storage into its active VRAM, anticipating that the user will soon transition to the desktop to fix the bug.

## 5. Cache Invalidation in a Decentralized Mesh

The hardest problem in computer science is cache invalidation. In a multi-device swarm utilizing OpenViking, stale context can lead an agent to hallucinate catastrophically.

If the user updates a file on their desktop, how does the smartphone know its L1 cache is obsolete?

We solve this using a modified vector-clock system layered over the `viking://` protocol.

1. **Mutation**: A file in `viking://resources/docs/api.md` is updated on the Desktop.
2. **Hash Generation**: The Desktop generates a new cryptographic hash for the L2 file, and subsequently updates the L1 and L0 hashes.
3. **Gossip Invalidation**: The Desktop broadcasts the new L0 abstract *and* its new hash across the gossip ring.
4. **Edge Purge**: The smartphone receives the gossip. It compares the new L0 hash against its cached L0 hash. Noticing a discrepancy, the smartphone instantly drops its cached L1 overview for that specific directory. The next time it needs that L1 data, it is forced to request a fresh copy from the Desktop.

This ensures strict eventual consistency across the swarm without requiring massive bandwidth overhead. Only the hashes and the tiny L0 abstracts are constantly moving; the heavy L1 and L2 payloads only move when absolutely necessary.

## 6. The Economics of Token Consumption

Variable Performance Scaling is not just about physical hardware constraints; it is about financial and computational economics.

Every time we feed context into an LLM, we pay a price—either in cloud API costs or local electricity and time. OpenViking's tiered structure allows Project Ember to be ruthlessly economical.

- If a query can be answered using only L1 overviews, we save 90% of the token cost compared to a flat RAG system that blindly retrieves raw L2 data.
- If a query requires L2 data, we only extract the specific L2 files isolated by the Directory Recursive Retrieval, ignoring the rest of the directory. 
- By caching these results across the swarm, if another device asks a similar question, the swarm can serve the answer from a localized cache without invoking the LLM at all.

## 7. Conclusion: The Seamless Illusion

Through rigorous L0-L1-L2 caching, predictive pre-fetching, and localized cache invalidation, Project Ember achieves the ultimate illusion: a singular, omnipotent AI agent that seems to exist perfectly on every device simultaneously.

The smartwatch feels as smart as the workstation because it borrows the workstation's mind. The smartphone feels infinitely fast because it predicts what it needs before it needs it. The swarm operates in perfect harmony, orchestrated by the hierarchical elegance of the OpenViking Context Database.

We move now to the penultimate design document: bridging the quantum leap between Ember's core OS and the Viking protocol.
