# Document 39: MULTI-DEVICE COMPUTE DISTRIBUTION – The Bifrost Bridge

## 1. Introduction: The Bifrost Bridge

The **Bifrost Compute Bridge** connects isolated, resource-constrained devices into a unified, distributed AI super-organism. It allows Ember instances on a local network to pool RAM, split inference tasks, and offload operations.

---

## 2. Peer Discovery and The Cluster Mesh

Bifrost uses mDNS to find Ember instances on the network. When connected, they exchange **Hardware Profile Matrices** (CPU, RAM, thermals). 
Node A knows Node B has a fast SSD, while Node C has an NPU but is on battery.

---

## 3. Asymmetric Task Offloading

### 3.1 Embedding Offload

If Node C (a phone on battery) receives a massive PDF, it sends the raw text chunks via Bifrost to Node B (a laptop on wall power). Node B generates the embeddings and streams them back. Node C appears to process a massive document instantly without battery drain.

### 3.2 Subagent Delegation

Ember can distribute its agents:
- Research Agent runs on the Laptop.
- Coding Agent runs on the Raspberry Pi.
- Review Agent runs on the Phone.
They communicate via Diet-JSON (DSON).

---

## 4. Pipeline Parallel Inference (Split-Model)

If an 8B model doesn't fit in any single device's RAM, Bifrost shards the model file horizontally.
- Node A (Pi, 2GB RAM): Loads Layers 1 - 12.
- Node B (Laptop, 3GB RAM): Loads Layers 13 - 32.

Node A calculates the forward pass for layers 1-12, transmits the intermediate hidden state activations over Gigabit LAN to Node B, which completes the pass and returns the token. 

---

## 5. Distributed KV-Cache Pooling

If Node A runs out of RAM for the KV-cache on a long conversation, it allocates "Remote Slabs" on Node B. Surtr sends an RPC to Node B for older attention calculations, perfectly solving memory bottlenecks.

---

## 6. Invented Method: "Swarm Speculative Decoding"

When connected to a cluster, Node A runs the large accurate model (`phi3:mini`). Simultaneously, Node B and Node C run tiny draft models.
1. Nodes B & C independently generate candidate sequences.
2. They stream drafts to Node A.
3. Node A verifies them in a single batch pass.

Drafting is completely offloaded to idle devices, allowing Node A's CPU to be 100% dedicated to verification, tripling the TPS output on purely edge hardware.

*(End of Document 39)*
