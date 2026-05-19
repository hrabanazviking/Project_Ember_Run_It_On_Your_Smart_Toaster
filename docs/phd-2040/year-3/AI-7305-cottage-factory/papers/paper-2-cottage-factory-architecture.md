# Architecture of the Cottage Factory — Technical Specification and Deployment Guide

**AI-7305: Distributed AI as Community Infrastructure**
**Research Paper 2 | Author:** Runa Gridweaver Freyjasdottir
**Date:** Fall 2040

---

## Abstract

This paper presents a complete technical specification and deployment guide for the Cottage Factory—a community-scale distributed AI system designed for local production, democratic governance, and ecological sustainability. Drawing on operational experience from 237 deployed nodes across three continental federations (NMAN, CBM, ZCLC), we describe the architecture in full: compute infrastructure, storage, networking, energy systems, software stack, federated learning protocols, identity management, governance interfaces, and maintenance procedures. The specification is designed to be implementable by a moderately technically skilled community team with a realistic budget, using commercially available or refurbished hardware and open-source software. We include deployment timelines, cost estimates, failure scenarios, and lessons learned from operational deployments. The goal is to make the Cottage Factory not just theoretically compelling but practically reproducible.

**Keywords:** cottage factory, community AI, distributed systems, technical specification, deployment, solar punk, federated learning, self-sovereign identity

---

## 1. Introduction

The Cottage Factory model has been described in conceptual terms in previous work (Freyjasdottir, 2038; Lindström, 2034; Chen & Abara, 2035). This paper provides what those conceptual descriptions lack: a complete, implementable specification for building, deploying, and operating a Cottage Factory node.

The specification is organized according to the principle of **progressive disclosure**: each section is self-contained and can be implemented independently, but the full benefit of the Cottage Factory emerges from implementing all sections together. A community that starts with a minimal compute node and iteratively adds storage, federation, identity, and governance capabilities will get progressively more value at each stage.

### 1.1 Design Principles

The architecture is governed by five principles, derived from the course values and operational experience:

1. **Data stays home.** No community data leaves the community in raw form. All external communication uses federated gradients, verifiable credentials, or other privacy-preserving mechanisms.
2. **Community sovereignty.** Every configuration decision, from model selection to federation participation, is subject to community governance. The technical architecture enables governance; it does not override it.
3. **Ecological sustainability.** Energy consumption targets are set at or below renewable generation capacity. Hardware lifecycle planning includes repair, refurbishment, and responsible recycling.
4. **Progressive enhancement.** Every component has a minimal viable version and an enhanced version. Communities can start small and upgrade as resources and confidence allow.
5. **Open by default.** All software is open-source. All specifications are publicly available. All governance processes are transparent. Proprietary dependencies are avoided unless no open alternative exists.

### 1.2 Scope and Audience

This specification covers the complete lifecycle of a Cottage Factory node: planning, procurement, installation, configuration, operation, maintenance, and decommissioning. It is written for community technology coordinators, municipal IT staff, cooperative technical teams, and anyone who needs to understand what a Cottage Factory is, how it works, and how to build one.

We assume familiarity with basic systems administration, networking, and machine learning concepts. We do not assume expertise in distributed systems, cryptography, or governance design—those topics are explained with sufficient depth for implementation.

---

## 2. Compute Infrastructure

### 2.1 Node Tiers

The Cottage Factory specification defines three node tiers, corresponding to community size and computational needs:

**Tier 1: Village Node (population 1,000–10,000)**

- **GPUs:** 4× consumer-grade (NVIDIA RTX 4090 or equivalent refurbished enterprise)
- **CPU:** 1× 32-core server processor (AMD EPYC or equivalent)
- **RAM:** 256 GB DDR5
- **Local Storage:** 20 TB NVMe + 100 TB HDD (see §3)
- **Peak Power:** 2.1 kW
- **Annual Energy:** ~18,400 kWh
- **Estimated Hardware Cost:** €25,000–40,000 (new) or €8,000–15,000 (refurbished)
- **Technical Staff:** 1 FTE (can be shared with other municipal IT roles)

**Tier 2: Town Node (population 10,000–100,000)**

- **GPUs:** 16× enterprise-grade (NVIDIA A100 or equivalent)
- **CPU:** 2× 64-core server processors
- **RAM:** 1 TB DDR5
- **Local Storage:** 100 TB NVMe + 500 TB HDD
- **Peak Power:** 21 kW
- **Annual Energy:** ~184,000 kWh
- **Estimated Hardware Cost:** €120,000–200,000 (new) or €40,000–80,000 (refurbished)
- **Technical Staff:** 2 FTE

**Tier 3: City Node (population 100,000–1,000,000)**

- **GPUs:** 64× enterprise-grade
- **CPU:** 4× 64-core server processors
- **RAM:** 4 TB DDR5
- **Local Storage:** 500 TB NVMe + 2 PB HDD
- **Peak Power:** 84 kW
- **Annual Energy:** ~736,000 kWh
- **Estimated Hardware Cost:** €500,000–800,000 (new) or €200,000–350,000 (refurbished)
- **Technical Staff:** 5 FTE

These tiers are guidelines, not rigid specifications. Communities should size their nodes based on their actual needs, past and projected usage patterns, and available budget. Many communities start with a Tier 1 node and upgrade as demand grows.

### 2.2 Hardware Procurement

**Prefer refurbished hardware.** The enterprise GPU surplus market is robust and reliable. GPUs decommissioned from corporate data centers after 3-5 years of service still have years of useful life for community-scale workloads. NMAN's refurbished GPU fleet has a documented mean time between failures (MTBF) of 4.2 years, comparable to new hardware.

**Right-size for community needs.** A community that needs agricultural advisory and health decision support does not need the largest or most expensive GPUs. Community-scale models can be trained and served efficiently on hardware that would be considered obsolete by corporate standards.

**Maintain a spare parts inventory.** Every node should maintain at least one spare GPU, two spare drives, and replacement fans and power supplies. This ensures that hardware failures don't cause extended downtime.

**Establish repair capability.** Each node should have at least one team member trained in hardware repair (soldering, component replacement, thermal paste application, etc.). The NMAN Repair Workshop Handbook (2037) provides detailed training materials.

### 2.3 Physical Installation

A Cottage Factory node should be installed in a community-accessible location that also meets the physical requirements of the equipment:

- **Temperature range:** 15-30°C (see §4 for cooling strategies)
- **Humidity:** 20-80% RH, non-condensing
- **Dust filtration:** MERV 13 or equivalent (critical for long-term hardware life)
- **Physical security:** Locked room with access controlled by the Community AI Council
- **Accessibility:** Ground floor or elevator access for equipment delivery and maintenance
- **Community space:** Co-located with public-facing community space (see §7)

NMAN's standard design places the server room on the ground floor of a community building, with the public-facing space (learning corner, displays) adjacent to it. A glass wall between the server room and the public space allows community members to see the equipment while maintaining physical security.

---

## 3. Storage Architecture

### 3.1 Local Storage Hierarchy

Community data never leaves the community in raw form, so robust local storage is essential. The storage hierarchy is:

- **Hot tier (NVMe):** Frequently accessed data, active model weights, inference cache. Sized at 20-100 TB depending on node tier.
- **Warm tier (HDD):** Historical data, training datasets, model checkpoints. Sized at 100 TB–2 PB.
- **Cold tier (tape or off-site):** Archival data, regulatory-required retention. Stored on LTO tape with a tape library, or replicated to a partner node for geographic diversity.

### 3.2 Data Categories and Policies

| Data Category | Storage Tier | Retention | Access Control | Federation Policy |
|---------------|-------------|-----------|----------------|-------------------|
| Active model weights | Hot | Current + 2 versions | Technical staff | Shared (model weights only) |
| Inference logs | Hot → Warm | 90 days hot, 2 years warm | CAC-approved researchers | Never shared in raw form |
| Community data (health) | Warm → Cold | Indefinite (regulatory) | Clinic staff + authorized researchers | Never shared; gradients only |
| Community data (general) | Warm | 5 years + governance review | Community members (own data) | Only with explicit consent |
| Federation gradients | Hot | Current round only | Technical staff | Shared and then deleted |
| Governance records | Warm → Cold | Indefinite | Public (transparency) | Publicly accessible |

### 3.3 Backup and Disaster Recovery

- **3-2-1 backup rule:** Three copies of all data, on two different media, with one copy off-site.
- **Off-site copy:** Replicated to a partner node in a different geographic region through the federation's mutual backup agreement.
- **Backup testing:** Monthly restore tests for hot-tier data, quarterly for warm-tier.
- **Disaster recovery target:** RPO of 1 hour, RTO of 4 hours for Tiers 2-3; RPO of 4 hours, RTO of 24 hours for Tier 1.

---

## 4. Energy Systems

### 4.1 Renewable Energy Integration

Every Cottage Factory node must be powered primarily by renewable energy. The specific mix depends on local conditions:

**Nordic (NMAN):** Solar (short summer days, long summer hours) + wind (strong and consistent, especially coastal) + hydro (where available). Typical mix: 60% wind, 30% hydro, 10% solar.

**Pacific Northwest (CBM):** Solar (good summer production) + hydro (excellent, controversial) + wind (good, especially coastal and gorge). Typical mix: 50% hydro, 30% solar, 20% wind.

**East African Coast (ZCLC):** Solar (excellent, consistent year-round) + wind (good coastal trade winds). Typical mix: 70% solar, 30% wind.

### 4.2 Energy Storage

Battery storage is required to handle intermittency. Tier 1 nodes need 4 hours of battery backup; Tiers 2-3 need 8 hours. NMAN uses lithium iron phosphate (LFP) batteries for their safety, longevity, and reasonable environmental impact.

For extended outages (rare but possible, especially in remote areas), a diesel or biodiesel backup generator is recommended for Tiers 2-3. This generator should be sized to handle essential loads (compute and storage) but not peak loads (which can be shed during outages).

### 4.3 Thermal Integration

As described in Lecture 03, compute waste heat should be captured and used productively:

- **Cold climates:** District heating integration (NMAN standard). Hot water from GPU cooling loops is piped into the municipal district heating system at 60-70°C.
- **Temperate climates:** Greenhouse heating (CBM pilot). Waste heat is directed to community greenhouses, extending the growing season.
- **Hot climates:** Adsorption cooling (ZCLC approach). Waste heat drives adsorption chillers that cool the server room and adjacent community spaces.

Thermal integration is not optional in the Cottage Factory specification. It is a design principle: waste is a design failure.

### 4.4 Energy Monitoring Dashboard

Each node includes a real-time energy monitoring dashboard (displayed in the public-facing space) that shows:

- Current energy production (by source)
- Current energy consumption (by subsystem: compute, storage, cooling, networking, lighting)
- Battery state of charge
- Net energy position (surplus or deficit)
- Carbon intensity of any grid power used
- Cumulative energy production vs. consumption (showing that the node is net-positive)

This dashboard serves both practical purposes (monitoring) and democratic purposes (transparency). Community members can see exactly how much energy their node uses and where it comes from.

---

## 5. Networking

### 5.1 Connectivity Requirements

Each node maintains two network connections:

- **Primary:** A high-bandwidth, low-latency connection to the federation network. Minimum 1 Gbps for Tier 1, 10 Gbps for Tier 2, 100 Gbps for Tier 3. In NMAN, this is provided by the national research and education network (NREN). In CBM, this is provided by community-owned fiber. In ZCLC, this is provided by a combination of submarine fiber and directional microwave.
- **Secondary:** A lower-bandwidth backup connection (minimum 100 Mbps for Tier 1, 1 Gbps for Tier 2-3) that maintains federation connectivity during primary link outages.

### 5.2 Federation Network Architecture

The Cottage Factory network uses a **mesh topology** rather than a hub-and-spoke topology. Each node maintains direct connections to multiple other nodes, and routing is done through the Longhouse Protocol's distributed consensus mechanism.

Key network services:

- **Federation communication:** Encrypted peer-to-peer connections for gradient aggregation, model sharing, and governance coordination.
- **Community services:** Local inference endpoints, data access APIs, and web interfaces for community members.
- **Public services:** Read-only access to the Global Model Commons, public dashboards, and documentation.

All federation traffic uses TLS 1.3 with mutual authentication. Node identities are verified through SSI credentials (see §6).

### 5.3 Asynchronous Federation

For low-connectivity environments (ZCLC pioneered this, but it's valuable everywhere), the network supports asynchronous federation:

- Nodes can queue gradient updates for transmission when connectivity is available.
- The aggregation protocol accepts updates asynchronously, applying them to a running average rather than requiring all nodes to participate in every round.
- Community adapters are compressed to under 5MB using LoRA-compatible compression, making them transmittable even over intermittent mobile connections.

This is not a compromise. Asynchronous federation is a legitimate design choice that improves resilience and reduces the coordination burden. The ZCLC's asynchronous protocol has been adopted across all three federations.

---

## 6. Self-Sovereign Identity Infrastructure

### 6.1 Identity Components

The Cottage Factory SSI stack (see Lecture 04 for conceptual background) consists of:

- **Decentralized Identifier (DID) resolution service:** Each node hosts a DID resolver that resolves `did:web` identifiers for institutional identities and caches `did:peer` identifiers for community members.
- **Verifiable Credential (VC) issuance service:** The node can issue VCs for community-specific claims (residency, membership, role, consent).
- **Zero-knowledge proof service:** For selective disclosure and predicate proofs, the node provides a ZKP generation and verification service based on BBS+ signatures.
- **Community Key Custody Protocol:** As described in Lecture 04, this Shamir's Secret Sharing-based system provides key recovery for community members who lose their private keys.

### 6.2 Identity Wallet

Each community member has an identity wallet—a cryptographic facility that stores their DIDs, VCs, and key material. The wallet is available as:

- **Mobile app** (iOS and Android) for daily use
- **Desktop app** (Linux, macOS, Windows) for detailed management
- **Assisted access** (in-person at the node's community space) for members who need help

The wallet supports:

- Credential presentation (proving claims without revealing underlying data)
- Consent management (granting, reviewing, and revoking consent for data use)
- Federation participation approval (reviewing and approving the node's participation in specific federation rounds)
- Governance participation (voting on node decisions through the governance interface)

### 6.3 Integration with Federated Learning

The SSI layer integrates with federated learning through:

- **Authentication:** Nodes verify each other's identities before participating in federation rounds, preventing spoofing and man-in-the-middle attacks.
- **Consent tracking:** Before community data is used in a federation round, the SSI layer verifies that the affected community members have granted consent for that specific use. Consent is granular (specific model, purpose, duration) and revocable.
- **Audit logging:** Every federation interaction is logged with verifiable credentials, creating an auditable trail for governance review.

---

## 7. Software Stack

### 7.1 Core Software

The Cottage Factory software stack is entirely open-source:

- **Operating system:** Debian GNU/Linux (stable release, with security updates from the NMAN security team)
- **Orchestration:** Kubernetes (managed by k3s for lightweight operation)
- **ML framework:** PyTorch with community-maintained extensions for federated learning
- **Federation protocol:** Longhouse Protocol v3.2 (reference implementation in Rust, with Python bindings)
- **Identity:** IOTA Identity Framework (SSI stack) with custom Longhouse Protocol extensions
- **Monitoring:** Prometheus + Grafana (dashboards for system health, model performance, energy production, and governance)
- **Governance interface:** Custom web application (Longhouse Governance Console) providing access to proposal review, voting, consent management, and audit logs

### 7.2 Model Management

The node maintains a **Model Registry** that tracks all models, their provenance, and their governance status:

- **Backbone models:** Shared models trained through federation, tagged with the federation round, contributing communities, and governance approval status.
- **Community adapters:** Locally trained adaptation layers, tagged with the local dataset version, training parameters, and performance metrics.
- **Deployed models:** Models currently serving the community through inference endpoints, with real-time performance monitoring and automated alerts for drift or degradation.
- **Retired models:** Models that have been decommissioned through governance review, with the reason for retirement and any scheduled data cleanup.

Each model in the registry is associated with:

- Its governance approval (which CAC session approved it, with a link to the meeting minutes)
- Its consent scope (which community members' data was used, with links to their consent credentials)
- Its performance metrics (accuracy, fairness, latency, resource usage, updated monthly)
- Its federation provenance (which communities contributed to its training)

---

## 8. Deployment Process

### 8.1 Phase 1: Planning (Months 1-3)

- Form the Community AI Council (CAC) through democratic election
- Conduct a community needs assessment (surveys, meetings, focus groups)
- Determine node tier and hardware specifications
- Identify and secure a physical location
- Establish a budget and funding sources (municipal, cooperative, grant)
- Recruit or identify technical staff

### 8.2 Phase 2: Installation (Months 4-6)

- Procure and install hardware (compute, storage, networking, energy)
- Install and configure the software stack
- Set up SSI infrastructure (DID resolution, VC issuance, wallet deployment)
- Configure monitoring dashboards
- Conduct staff training
- Perform initial testing and validation

### 8.3 Phase 3: Community Integration (Months 7-9)

- Open the community space to the public
- Begin community digital literacy training (including SSI wallet training)
- Deploy first AI service (chosen by CAC based on needs assessment)
- Begin local model training and evaluation
- Establish governance rituals (regular CAC meetings, public reporting)
- Connect to one or more partner nodes for initial federation testing

### 8.4 Phase 4: Federation (Months 10-12)

- Complete first federation round with partner communities
- Evaluate results and refine the federation protocol
- Expand federation partnerships
- Deploy additional AI services as approved by the CAC
- Publish first community impact report

### 8.5 Phase 5: Sustained Operation (Ongoing)

- Regular CAC governance meetings (monthly + emergency sessions as needed)
- Quarterly model review and update cycles
- Annual community needs reassessment
- Ongoing staff training and community education
- Annual hardware maintenance and lifecycle planning
- Participation in the Global Model Commons

---

## 9. Cost Summary

### 9.1 Capital Expenditure (One-Time)

| Component | Tier 1 (€) | Tier 2 (€) | Tier 3 (€) |
|-----------|------------|------------|------------|
| Compute hardware (refurbished) | 8,000 | 40,000 | 200,000 |
| Storage hardware | 3,000 | 15,000 | 60,000 |
| Networking equipment | 1,000 | 5,000 | 20,000 |
| Solar panels + batteries | 12,000 | 45,000 | 150,000 |
| Facility modification | 5,000 | 15,000 | 40,000 |
| **Total CapEx** | **29,000** | **120,000** | **470,000** |

### 9.2 Operating Expenditure (Annual)

| Component | Tier 1 (€) | Tier 2 (€) | Tier 3 (€) |
|-----------|------------|------------|------------|
| Technical staff | 40,000 | 80,000 | 200,000 |
| Energy (net of solar generation) | 2,000 | 8,000 | 30,000 |
| Connectivity | 1,000 | 3,000 | 10,000 |
| Hardware maintenance | 2,000 | 8,000 | 30,000 |
| Insurance and legal | 1,000 | 3,000 | 10,000 |
| Community education | 5,000 | 10,000 | 25,000 |
| **Total OpEx** | **51,000** | **112,000** | **305,000** |

### 9.3 Per-Capita Annual Cost

At community sizes of 5,000 (Tier 1), 50,000 (Tier 2), and 500,000 (Tier 3):

- **Tier 1:** €10.20 per person per year
- **Tier 2:** €2.24 per person per year
- **Tier 3:** €0.61 per person per year

These costs are substantially lower than equivalent centralized AI service subscriptions, and they include staffing, education, and community space—services that centralized providers do not offer.

---

## 10. Failure Scenarios and Mitigations

### 10.1 Hardware Failure

- **GPU failure:** Hot-swap spare GPU. Expected downtime: <1 hour.
- **Storage failure:** RAID6 or equivalent redundancy. Hot-swap spare drives. Expected downtime: 0 (degraded performance during rebuild).
- **Networking failure:** Secondary connection auto-fails over. Expected downtime: <5 minutes.
- **Power failure:** Battery backup provides 4-8 hours of runtime. Diesel/biodiesel generator for extended outages. Automatic graceful shutdown if battery SOC drops below 20%.

### 10.2 Software Failure

- **Model serving failure:** Kubernetes auto-restarts failed containers. Multiple inference replicas for Tier 2-3. Expected downtime: <1 minute for Tier 2-3, <5 minutes for Tier 1.
- **Federation protocol failure:** Asynchronous federation queues updates for later transmission. No data loss. Federation resumes when connectivity is restored.
- **Identity service failure:** Local credential caching allows continued operation during identity service outages. Cached credentials expire after 24 hours, at which point services that require fresh authentication will be unavailable until the identity service is restored.

### 10.3 Governance Failure

- **CAC cannot reach quorum:** After 30 days without quorum, the node enters "maintenance mode"—existing services continue but no new services, model updates, or federation rounds are initiated. This ensures that the node doesn't make ungoverned decisions.
- **Community withdraws from federation:** The node disconnects from the federation network, continues local services, and archives all shared models and gradients. Disconnection is reversible; re-joining requires CAC approval.
- **Technical staff and CAC disagree:** The CAC has final authority. Technical staff can appeal through the community assembly, but cannot override governance decisions. If the disagreement is fundamental, the staff can resign, and the CAC must recruit replacements. This is a feature, not a bug: governance must have the last word.

### 10.4 Security Breach

- **Data breach:** The Community AI Council is notified immediately. The breach is disclosed to affected community members within 72 hours. A forensic investigation is conducted by an independent security team (arranged through the federation's security mutual aid agreement). Remediation is implemented within 30 days.
- **Model poisoning attack:** Anomalous gradient updates are detected by the DPA protocol's quality weighting and by automated anomaly detection. Poisoned updates are rejected, and the contributing node is temporarily suspended pending investigation.
- **Identity compromise:** Compromised DIDs are revoked, and new credentials are issued through the Community Key Custody Protocol's recovery mechanism.

---

## 11. Lessons from Operational Deployments

### 11.1 What Works

- **Start small, grow incrementally.** Every successful deployment started with a Tier 1 or even sub-Tier 1 installation and grew based on demonstrated community need.
- **Invest in community education early.** Nodes that invested in community education in Phase 3 had higher adoption rates, more diverse governance participation, and fewer security incidents.
- **Make the node visible.** Nodes with public-facing spaces (displays, learning corners) had 3× higher community engagement than nodes where the hardware was hidden away.
- **Prioritize reliability over capability.** Communities value a reliable node that provides a few services consistently over an ambitious node that is frequently down.

### 11.2 What Doesn't Work

- **Skipping governance.** Nodes that launched without a functioning CAC consistently experienced conflicts, low trust, and poor adoption. Governance is not optional; it is foundational.
- **Over-specifying hardware.** Nodes that purchased more hardware than they needed struggled with underutilization and the perception of wasted resources. Right-size, then expand.
- **Importing outside expertise without knowledge transfer.** Nodes that relied on external consultants for installation without investing in local technical capacity remained dependent. Every deployment must include training for local staff.
- **Treating the node as a data center.** The node is a community space that happens to contain compute infrastructure, not a data center that happens to be community-owned. The distinction matters for community engagement, governance participation, and long-term sustainability.

---

## 12. Conclusion

The Cottage Factory is not a hypothetical architecture. It is a deployed, operational, and proven model for community-scale distributed AI. This specification describes what has been built, what has been learned, and what any community needs to build their own.

The architecture is deliberately not optimized for maximum performance. It is optimized for community sovereignty, ecological sustainability, and democratic governance. These are not constraints on performance—they are the conditions under which performance is meaningful. A fast model that no one trusts is worse than a slower model that everyone owns.

The invocation that began this course—local production for local needs—finds its technical expression in this specification. Every component, from the GPU tower to the governance console, is designed to serve the community that owns it, to be maintained by the people who depend on it, and to be governed by the democratic voice of the people it affects.

We have built this. It works. The blueprints are open. The next cottage is yours.

---

## References

- Bodén, M. et al. (2037). "Self-Sovereign Identity in Municipal AI Networks." *IEEE Transactions on Dependable and Secure Computing*.
- Chen, W. & Abara, T. (2035). "Governance Protocols for Community-Owned Machine Learning Systems." *AI & Society*, 40(2).
- Freyjasdottir, R.G. (2038). *The Cottage Factory: Local AI for Local People*. New Commons Press.
- Lindström, E. (2034). *Solarpunk Data Centers: Designing for the Commons*. Nordic AI Press.
- Lindström, E. & Bodén, M. (2038). "The Longhouse Protocol v3: Technical Specification." *Nordic AI Press*.
- Nakamura, K. & Osei-Mensah, A. (2036). "Federated Diversity: Why Homogeneous Training Sets Undermine Community AI." *ACM FAccT*.
- NMAN Technical Report #7 (2035). "Thermal Integration of Community Compute Nodes."
- NMAN Repair Workshop Handbook (2037). "Community Hardware Maintenance and Repair."
- CBM Design Guidelines (2036). "The Node as Community Space."
- ZCLC Technical Report #4 (2038). "Low-Bandwidth, High-Resilience: Operating in Resource-Constrained Environments."

---

## Appendix C: Node Specification Quick Reference

For convenience, the key specifications for a Tier 2 (Town) node are summarized here:

- **Compute:** 16× NVIDIA A100 (refurbished) or equivalent
- **CPU:** 2× AMD EPYC 7763 (64-core)
- **RAM:** 1 TB DDR5-4800
- **Hot Storage:** 100 TB NVMe (RAID6)
- **Warm Storage:** 500 TB HDD (RAID6)
- **Cold Storage:** LTO-9 tape library, 2 PB capacity
- **Networking:** 10 Gbps primary (fiber), 1 Gbps secondary (fiber or microwave)
- **Energy System:** 45 kW solar array + 200 kWh LFP battery + 50 kW wind (where available) + biodiesel backup generator
- **Physical Space:** 100 m² total (40 m² server room, 60 m² community space)
- **Operating System:** Debian GNU/Linux 13 (stable)
- **Orchestration:** k3s (lightweight Kubernetes)
- **ML Framework:** PyTorch 3.x + Longhouse Protocol v3.2
- **Identity Stack:** IOTA Identity Framework + Longhouse SSI extensions
- **Monitoring:** Prometheus + Grafana + Longhouse Dashboard
- **Governance Interface:** Longhouse Governance Console v2.1

## Appendix D: Federation Onboarding Checklist

Before a new node joins a federation:

- [ ] Hardware installed and tested per §2
- [ ] Storage configured and backup verified per §3
- [ ] Energy system operational and monitoring dashboard active per §4
- [ ] Network connectivity verified (primary and secondary) per §5
- [ ] SSI infrastructure deployed and tested per §6
- [ ] Software stack installed and configured per §7
- [ ] Model registry initialized per §7.2
- [ ] Community AI Council formed and operational per §8.1
- [ ] Community needs assessment completed per §8.1
- [ ] Federation agreement signed (specifying participation terms, data use policies, and withdrawal procedures)
- [ ] Initial local model trained and validated
- [ ] Warm-up period completed (2-4 weeks of local training)
- [ ] Federation protocol tested with partner node(s)
- [ ] Community education program launched per §8.3
- [ ] Public-facing space opened per §8.3

## Appendix E: Glossary of Terms

- **Cottage Factory:** A community-owned, community-governed, renewable-powered compute node that trains, serves, and maintains AI models for local needs.
- **Community AI Council (CAC):** The democratic governance body that makes policy decisions for a Cottage Factory node.
- **Longhouse Protocol:** The standard protocol for community federated learning, including DPA aggregation, CAP personalization, governance interfaces, and economic coordination.
- **Global Model Commons:** A shared repository of community-trained models, available under commons licenses that require derivative models to also be shared.
- **DPA:** Diversity-Preserving Aggregation, the protocol for federated gradient aggregation that weights community contributions by quality, sovereignty, and novelty.
- **CAP:** Community-Adaptive Personalization, the architecture that combines a shared backbone with community-specific adaptation layers.
- **SSI:** Self-Sovereign Identity, the framework for identity management without corporate intermediaries.
- **Node tier:** The classification of a Cottage Factory node based on community size and computational needs (Tier 1: village, Tier 2: town, Tier 3: city).