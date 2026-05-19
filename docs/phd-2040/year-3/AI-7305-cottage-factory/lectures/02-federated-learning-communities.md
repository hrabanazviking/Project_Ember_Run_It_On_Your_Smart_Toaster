# Lecture 02: Federated Learning Communities — Training Without Centralized Data

**AI-7305: Distributed AI as Community Infrastructure**
**Instructor:** Prof. Runa Gridweaver Freyjasdottir | **Date:** September 10 & 12, 2040

---

## From Extraction to Federation

When the Nordic Municipal AI Initiative launched in 2029, the first problem wasn't technical—it was trust. Municipal health administrators in Luleå weren't going to send patient data to a server farm in Stockholm, no matter how many encryption guarantees the central authority offered. And they shouldn't have. The patients in Norrbotten had not consented to having their health records aggregated into someone else's dataset. The data belonged to them, to their community, to the relationships of care that produced it.

Federated learning offered a way out of this impasse. The insight was simple: instead of moving data to the model, move the model to the data. Each community trains a local model on its own data. Then—carefully, selectively, under community control—the learned parameters (not the data) are aggregated across communities to produce a shared model that benefits everyone.

But the story of federated learning in the Cottage Factory context is not just a technical story about distributed optimization. It is a story about how we learned to treat data as a sovereign community resource and still build collective intelligence. The technical protocols and the political commitments co-evolved. Neither was an afterthought.

## Federated Learning: A Refresher

At its core, federated learning works as follows:

1. **Initialization.** A global model (or a community-adapted variant) is distributed to all participating nodes.
2. **Local training.** Each node trains the model on its local data for some number of epochs.
3. **Gradient computation.** Each node computes the gradient updates (or model delta) from local training.
4. **Secure aggregation.** Gradients are aggregated across nodes—typically by averaging—using protocols that prevent any individual node's updates from being identified in the aggregate.
5. **Global update.** The aggregated gradient is applied to the global model.
6. **Iteration.** The updated model is redistributed, and the cycle repeats.

This is the baseline. The Cottage Factory model extends this baseline in several critical ways, which we'll explore throughout this lecture.

## The Problem with Vanilla Federation

Standard federated learning, as originally proposed by McMahan et al. (2017), assumed a specific context: a single organization (typically a large technology company) training a model using data distributed across many user devices. The key assumptions were:

- **One model, one objective.** All participants want the same model for the same purpose.
- **Homogeneous data distributions.** Data is non-IID across clients, but this is treated as a problem to be overcome, not a feature to be leveraged.
- **Central orchestration.** A central server coordinates the training process.
- **Passive participation.** Clients contribute data and computation but don't govern the process.

Every one of these assumptions is wrong for the Cottage Factory context, and understanding *why* is essential to understanding our architecture.

### One Model, One Objective?

When the fishing community in Lofoten and the farming community in Dalarna both participate in a federation, they are not trying to build the same model. Lofoten needs storm surge prediction; Dalarna needs crop disease detection. The global model that emerges from federated averaging is a compromise that serves neither community as well as a model trained specifically for their context.

Our solution—which we'll explore in detail below—is **community-adaptive personalization**: a shared backbone model that captures general patterns, combined with community-specific adaptation layers that capture local knowledge. The backbone is the commons; the adaptation layers are sovereign.

### Homogeneous Data Distributions?

The standard federated learning literature treats non-IID data as a challenge. Non-IID data causes client drift—each node's local model diverges from the global optimum because it's optimizing for a different distribution. Various techniques (FedProx, SCAFFOLD, FedNova) have been proposed to mitigate this drift.

But in the Cottage Factory context, non-IID data is not a bug. It is the *entire point*. The diversity of community datasets is what makes federated learning valuable. A weather prediction model trained only on data from coastal Norway will fail in the Sahel. A model that learns from both—and from a hundred other communities besides—will be more robust everywhere. The challenge is not to reduce diversity but to aggregate it wisely.

This is the core argument of your first research paper: federated learning needs community diversity, and our aggregation protocols should be designed to preserve it, not flatten it.

### Central Orchestration?

The single-server architecture of standard federated learning creates a dangerous point of centralization. Even if the server doesn't see raw data, it controls the aggregation rules, the model architecture, the training schedule, and the participant selection. In a corporate context, this is acceptable—corporations control their own infrastructure. In a community context, it violates sovereignty.

The Cottage Factory uses **decentralized federation**: there is no central server. Instead, each node maintains bilateral and multilateral federation agreements with other nodes. Aggregation happens through a distributed consensus protocol (the Longhouse Protocol, which we'll cover in Lecture 06) that ensures no single node can unilaterally set the rules for the federation.

### Passive Participation?

In standard federated learning, the "participants" are phones and browsers—they contribute compute cycles and data, but they have no voice in the training process. In the Cottage Factory, the participants are *communities* with governance structures, democratic processes, and the right to say no. Community AI Councils decide when to participate in a federation round, what data to make available for training, and whether to accept an aggregated model update.

This changes everything about how we design the protocol. In standard FL, you optimize for convergence speed and communication efficiency. In the Cottage Factory, you optimize for *consent* and *sovereignty*. A slow protocol that communities trust is better than a fast one they don't.

## The Longhouse Federation Protocol

The Longhouse Protocol (officially v3.2 as of 2040) is the standard for community federated learning. It builds on two decades of federated learning research but adapts it for community sovereignty. Key features:

### 1. Community-Adaptive Personalization (CAP)

Rather than training a single global model, CAP maintains a **shared backbone** trained through federation and **community adapters** trained locally. The architecture is:

```
[Community Input] → [Shared Backbone (federated)] → [Community Adapter (local)] → [Community Output]
```

The shared backbone learns general features that transfer across communities. The community adapter fine-tunes for local context using a small number of local training epochs. This means:

- Each community gets a model that works well for their specific context.
- The shared backbone benefits from diverse community data without requiring data to leave the community.
- Communities can update their adapters frequently (even daily) while the backbone is updated on slower federation cycles (weekly or monthly).

The adapter approach draws on the parameter-efficient fine-tuning literature—LoRA (Low-Rank Adaptation) and its descendants—but applies it at the community scale rather than the task scale. Each community's adapter is small (typically 0.5-2% of the backbone parameter count) but impactful.

### 2. Diversity-Preserving Aggregation (DPA)

Standard federated averaging (FedAvg) weights client updates proportionally to their dataset size. In a community context, this means larger communities dominate the global model. DPA instead uses a three-factor weighting scheme:

- **Dataset quality weight:** Rewards communities with higher-quality, more representative local datasets (assessed through local validation metrics, not data inspection).
- **Sovereignty weight:** Each community gets a minimum representation threshold, regardless of size, ensuring that small communities are not dominated by large ones.
- **Novelty weight:** Updates that represent new knowledge (high gradient divergence from the current global model) are weighted more heavily, preserving the diversity benefit of community federation.

The mathematical formulation is detailed in Nakamura & Osei-Mensah (2036), which forms the core reading for Paper 1.

### 3. Selective Federation

Communities are not required to participate in every federation round. The Longhouse Protocol includes a **federation menu**: each community council can choose which federation rounds to participate in based on:

- The purpose of the round (is it training a model we need?)
- The other participants (do we trust them? Do we share values around data use?)
- The computational cost (do we have the budget this month?)
- The governance approval (has our Community AI Council approved participation?)

This selectivity is a feature, not a bug. It mirrors how real communities engage in mutual aid: selectively, strategically, and with full consent.

### 4. Secure Aggregation with Auditable Proofs

The Longhouse Protocol uses secure multi-party computation (MPC) for gradient aggregation, ensuring that no individual community's model updates can be reverse-engineered from the aggregate. But unlike corporate FL systems that treat the aggregation process as a black box, the Longhouse Protocol provides **auditable proofs**:

- Each participating node can verify that their contribution was included in the aggregate.
- Any auditor can verify that the aggregation was performed correctly without accessing individual updates.
- The aggregation rules (the DPA weighting factors) are publicly published and subject to governance review.

This transparency is essential for community trust. Communities will not participate in a federation they cannot audit.

## Federation in Practice: Three Case Studies

### The Nordic Municipal AI Network (NMAN)

Founded 2029, now comprising 147 community nodes across Norway, Sweden, Finland, and Denmark. NMAN operates the longest-running community federation in the world. Key lessons:

- **Startup is slow.** The first two years saw only 11 nodes, and early federation rounds produced models worse than local-only training. It takes time for a federation to reach the diversity threshold where aggregation becomes beneficial.
- **Trust is the primary infrastructure.** Technical protocols matter less than social protocols. NMAN's monthly community councils, where representatives discuss federation policy, are more important than any algorithmic innovation.
- **Small communities benefit most.** The smallest NMAN nodes (populations under 5,000) showed the largest accuracy improvements from federation—up to 23% on specific tasks—because their local datasets were too small to train effective models alone.

### Cascadia Bioregional Mesh (CBM)

Founded 2033, 62 nodes across the Pacific Northwest of North America. CBM is notable for its **intersectional governance**: each node's Community AI Council must include representatives from indigenous nations, racial justice organizations, labor unions, and disability advocacy groups. This ensures that the models trained through CBM federation serve all community members, not just the most privileged.

CBM also pioneered **conditional federation**: communities can attach conditions to their federation participation, such as "our gradients may only be used for models that will be freely available to all participants" or "we will not participate in rounds that also include nodes operated by for-profit entities."

### Zanzibar Coastal Learning Cooperative (ZCLC)

Founded 2035, 28 nodes across the Swahili Coast. ZCLC is the most important case study for global applicability because it demonstrates that the Cottage Factory model works in contexts with limited infrastructure, unreliable connectivity, and non-Western governance traditions.

ZCLC's key innovations:

- **Asynchronous federation:** Rounds don't require all nodes to be online simultaneously. Nodes contribute when connected, and aggregation happens continuously.
- **Low-bandwidth adapters:** Community adapters are compressed to under 5MB, making them transmittable over intermittent mobile connections.
- **Oral governance:** Community AI Council decisions are made through community assemblies using Swahili and local dialects, with technical advisors providing translation rather than direction.

## Practical Considerations for Federation Design

When designing a federation for a new community, consider these practical questions:

1. **What data does the community have, and who governs it?** Map the data ecosystem before choosing a model architecture.
2. **What does the community actually need the AI to do?** Start with use cases, not model capabilities.
3. **What connectivity constraints exist?** Rural, maritime, and developing-world contexts may require asynchronous federation and aggressive compression.
4. **What governance structures does the community already have?** Don't impose governance from outside. Adapt existing decision-making bodies.
5. **What trust relationships exist with potential federation partners?** Federation is voluntary and relational. Start with communities you trust.

## The Frontiers

The most exciting current research in community federated learning addresses three open problems:

- **Federated continual learning:** How do communities learn from streaming data without catastrophic forgetting, and how do they share new knowledge through the federation without requiring synchronous participation?
- **Cross-lingual federation:** When communities speak different languages, how do we build shared representations that respect linguistic diversity rather than forcing everything through English?
- **Federated governance:** How do we make collective decisions about model behavior (what the model should do, what values it should embody) across communities with different values?

These are not merely technical problems. They are problems at the intersection of technology and democratic self-governance—which is exactly where the Cottage Factory model lives.

---

## Discussion Questions

1. Is selective federation (communities choosing when and whether to participate) compatible with the goal of building collective intelligence? What happens if too many communities opt out?
2. The DPA weighting scheme gives small communities disproportionate influence relative to their data contribution. Is this fair? What would "fair" mean in this context?
3. How would you design a federation protocol for a community that doesn't have reliable internet access? What are the minimum technical requirements for participation?
4. Can federated learning work when communities fundamentally disagree about what the model should do? At what point does value divergence make federation counterproductive?

## Further Reading

- McMahan, B. et al. (2017). "Communication-Efficient Learning of Deep Networks from Decentralized Data." *AISTATS*.
- Nakamura, K. & Osei-Mensah, A. (2036). "Federated Diversity: Why Homogeneous Training Sets Undermine Community AI." *ACM FAccT*.
- Lindström, E. & Bodén, M. (2038). "The Longhouse Protocol v3: Technical Specification." *Nordic AI Press*.
- Osei-Mensah, A. (2037). "Conditional Federation: Data Sovereignty in Practice." *Proceedings of ACM FAccT*.
- ZCLC Technical Report (2037). "Asynchronous Federation for Low-Connectivity Contexts."