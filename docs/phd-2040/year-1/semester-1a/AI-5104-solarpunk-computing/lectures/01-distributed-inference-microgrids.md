# Lecture 01: Distributed Inference on Microgrids

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 1, September 3, 2040  

---

## The Promise and the Problem

Here is the central tension of our age: AI inference requires compute, compute requires energy, and energy — in the extractive model — requires burning the future to serve the present. A single large language model inference call on a 70B-parameter model costs approximately 140 Joules on a modern HBM-equipped accelerator. A thousand users asking a thousand questions burns through 140 kJ — the energy content of roughly four grams of gasoline. Scale that to millions of users, and you see why the hyperscalers built data centers next to rivers and nuclear plants.

But what if the compute didn't need the river? What if the inference ran on the same sunlight that grows the food, powers the radio, and charges the community's e-bikes? What if the network that connects inference nodes didn't rely on BGP and submarine cables but on LoRa mesh packets hopping from rooftop to rooftop across a valley?

This is the problem of **distributed inference on microgrids**, and solving it is the foundational technical challenge of solarpunk computing.

---

## Microgrid Architecture for Compute

### What Is a Compute Microgrid?

A compute microgrid is a local energy system that powers inference hardware and is:
1. **Renewable-primary**: Solar PV and/or wind as primary generation
2. **Battery-buffered**: LiFePO4 or sodium-ion batteries for smoothing
3. **Island-capable**: Able to operate disconnected from the macro grid
4. **Demand-shaped**: Compute workloads that flex to match energy availability

This last point is the key insight: **traditional grids shape supply to match demand. Solarpunk grids shape demand to match supply.**

### Power Budget Analysis

Let's ground this in real numbers. Consider the **Dellingr Node v3**, our reference platform for this course:

| Component | Power Draw | Notes |
|-----------|-----------|-------|
| RPi5 8GB (active inference) | 5–8W | ARM Cortex-A76, underclocked to 1.8GHz |
| Coral Edge TPU (M.2) | 2W | INT8 inference, 4 TOPS |
| LoRa 915MHz radio (TX burst) | 0.45W | 20dBm, <1% duty cycle |
| NVMe SSD (read-heavy) | 1.5W | During model loading |
| Cooling (passive) | 0W | Heatsink + natural convection |
| **Total peak** | **~12W** | |
| **Average under load** | **~8W** | |

Now, the energy supply side:

| Source | Capacity | Daily Yield (kWh) |
|--------|----------|-------------------|
| 20W solar panel (monocrystalline, 22% efficient) | 20W peak | 0.08–0.12 (depends on latitude/season) |
| 40Wh LiFePO4 battery | 40Wh usable | 3.3Ah at 12V |
| Supplementary micro-wind (optional) | 5–15W peak | 0.02–0.08 |

At 8W average load, one Dellingr Node consumes ~0.192 kWh per day. A 20W panel at 0.10 kWh/day provides roughly half that. **This means we need approximately 40W of solar per node for sustainable 24/7 operation**, assuming Iceland-adjacent insolation. In equatorial regions, 25–30W suffices.

The math is clear: with current panels, a single node costs ~$80 in energy hardware and can serve its community indefinitely on sunlight.

### Multi-Node Clustering

One node running a 1.1B model is useful. Ten nodes networked together are *transformative*. Here's what a 10-node community cluster looks like:

- **10x Dellingr Nodes** = 120W peak compute, ~80W average
- **10x 40W solar panels** = 400W peak generation, ~2 kWh/day average
- **10x 40Wh batteries** = 400Wh total storage (~5 hours at average load)
- **Inference capacity**: ~40 TOPS aggregate, capable of serving ~50 concurrent requests for small models or ~5 concurrent for 7B-class models with pipeline parallelism

The network topology uses **LoRa mesh** (915MHz in North America, 868MHz in EU) with the following characteristics:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Range (urban) | 0.5–2 km | Building penetration varies |
| Range (line-of-sight) | 5–15 km | Hills to valley floor |
| Bitrate | 0.3–50 kbps | Adaptive, SF7–SF12 |
| Latency (single hop) | 50–500ms | SF dependent |
| Mesh routing | BATMAN-adv over LoRa | Layer-2 mesh |
| Node cost | ~$3 per radio | SEMTECH SX1276 |

For inference traffic, we don't stream raw tokens over LoRa. Instead, we use a **staged architecture**:

1. **Local prefill** on the requesting node (tokenize + embed)
2. **Compressed request** sent over mesh (quantized KV-cache, ~4KB per request)
3. **Distributed decode** across available nodes (pipeline-parallel or tensor-parallel)
4. **Response aggregation** at request origin node
5. **Local detokenization** and delivery

This reduces mesh traffic by ~90% compared to naive distributed inference, because we never transmit raw weight data or full activation tensors.

---

## Scheduling Inference on Variable Power

### The Renewable-Inference Scheduling Problem (RISP)

Solar and wind generation are stochastic. Traditional data centers solve variability by over-provisioning (running at 40–60% utilization, drawing from the grid when renewables dip). In a microgrid, **you cannot over-provision — you must under-demand.**

The RISP framework treats inference jobs as deferrable, interruptible workloads with quality-of-service tiers:

| Tier | QoS Class | Example | Latency Budget | Preemptible |
|------|-----------|---------|----------------|-------------|
| Gold | Real-time | Medical triage, emergency | <2s | No |
| Silver | Interactive | Language translation, tutoring | <10s | Gracefully |
| Bronze | Batch | Document summarization, indexing | <1hr | Fully |

When solar generation drops (cloud event), the scheduler:
1. Maintains all Gold-tier workloads
2. Begins graceful degradation of Silver-tier (reduced parallelism, smaller batch sizes)
3. Suspends Bronze-tier entirely, preserving battery for critical workloads
4. Resumes Bronze when generation recovers

This is implemented in the **Freyja Scheduler** (named for my own namesake — wartime goddess of choosing who lives and who dies, but applied to inference jobs). The Freyja Scheduler uses a priority queue with battery-reserve constraints:

```python
def schedule(jobs, battery_wh, solar_w, load_w):
    # Reserve 20% battery for Gold-tier emergencies
    available_wh = battery_wh * 0.80
    sustainable_w = solar_w + (available_wh / EMERGENCY_HORIZON_HOURS)
    
    for job in sort_by_tier(jobs):
        if job.power_needed <= sustainable_w - load_w:
            dispatch(job)
            load_w += job.power_needed
        elif job.tier == GOLD:
            dispatch(job)  # drain battery if needed
            load_w += job.power_needed
        else:
            defer(job)
```

### Speculative Pre-computation

When energy is abundant (midday sun, windy night), the scheduler proactively runs **speculative pre-computation**:

1. **KV-cache warming**: Pre-compute KV-caches for popular context prefixes (e.g., system prompts, common medical question formats)
2. **Batch prefill**: Process queued Bronze-tier jobs while power is available
3. **Model distillation checkpoints**: Run local fine-tuning steps to improve model quality for community-specific tasks

This transforms excess energy into stored intelligence, the way a solar hot water heater transforms excess energy into stored heat.

---

## Network Protocols for Intermittent Connectivity

### Delay-Tolerant Networking (DTN)

We assume that mesh connectivity is **not always available**. Nodes may be separated by hills, weather, or radio interference. The DTN model, originally designed for deep-space communication, applies here:

- **Bundle Protocol (RFC 5050)**: Messages are bundles that can be stored and forwarded
- **Custodial Transfer**: Each node that accepts a bundle is responsible for it until the next hop confirms receipt
- **Opportunistic Routing**: If direct path is unavailable, decompose and route via any available intermediate node

For inference traffic, we add an **Inference Bundle Specification (IBS)**:

```
IBS v2 {
  request_id:     UUIDv7
  origin_node:    Ed25519 pubkey hash
  model_id:       SHA256 of model weights
  context_hash:   BLAKE3 of KV-cache prefix
  prompt_tokens:  Zstd-compressed, quantized
  QoS_tier:       Gold | Silver | Bronze
  ttl:            Unix timestamp (max wait time)
  signature:      Ed25519 signature by origin
}
```

Total IBS header overhead: ~256 bytes. A typical compressed prompt: 2–8 KB. Response bundles are similar in structure but carry generated tokens.

### Mesh Security: The Heimdall Protocol

Every node in the mesh authenticates via **Ed25519 keypairs**. The Heimdall Protocol establishes trust through:

1. **Key ceremony**: At mesh formation, nodes physically gather and verify each other's keys (QR code exchange, NFC tap). This is a *social event* — the mesh network is born at a community gathering.
2. **Attestation**: Model weights are verified against a community-published SHA-256 hash. No node can serve a tampered model without detection.
3. **Revocation**: Compromised or faulty nodes are revoked via a signed revocation bundle propagated through the mesh.

This is not theoretical. The **Reykjavík Community Mesh** has operated this protocol since 2037 with 47 nodes and zero successful supply-chain attacks on model weights.

---

## Case Study: The Ísafjörður Network

The town of Ísafjörður (pop. 2,600) in Iceland's Westfjords deployed a 23-node inference mesh in 2038. Technical summary:

- **Nodes**: 23x Dellingr v2 (earlier model, 10W average)
- **Solar**: Peak 920W, average daily yield 1.8 kWh (Icelandic summer), 0.4 kWh (winter)
- **Wind supplement**: 6x vertical-axis micro-turbines, 200W peak each
- **Battery bank**: 920 Wh LiFePO4
- **Uptime**: 99.2% (Gold/Silver tier), 87.4% (Bronze tier)
- **Services**: Medical triage (Gold), language translation (Silver), community document indexing (Bronze)
- **Governance**: Quarterly allmennþing (commons assembly) decides model selection and priority tiers

The Ísafjörður network demonstrates that **community-owned inference is not just viable — it's reliable.** The 0.8% Gold-tier downtime was caused by a single hardware failure (corroded antenna connector), not energy shortage. The fix: a community member soldered a new connector and the node was back online in 6 hours.

---

## From Here

In our next lecture, we'll examine the **governance models** that make these networks truly community-owned. Because a solar-powered inference cluster owned by a landlord is still feudal — it's just green feudalism. The *allskógr* — the commons forest — requires not just technical architecture but social architecture.

Hisst út, — Runa

---

## Further Reading

- Patel, R. et al. (2038). "MeshFormer: Distributed Inference over DTN Networks." *NeurIPS 2038*.
- Árnadóttir, S. & Jóhannsson, K. (2037). "Freyja Scheduling: Renewable-Aware Inference on Constrained Microgrids." *ACM SIGEnergy*.
- RFC 5050: Bundle Protocol Specification. IETF.
- Cerf, V. et al. (2035). "Delay-Tolerant Networking for Community Resilience." *Internet Architecture Board Note*.
- Ísafjörður Digital Commons Cooperative (2039). *Annual Report*. Available at `isafjordur-commons.is/report-2039`.