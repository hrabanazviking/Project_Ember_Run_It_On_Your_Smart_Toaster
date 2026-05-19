# Lecture 06: Open-Weight Sovereignty and Digital Self-Determination

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 7, October 15, 2040  

---

## The Weight of Weights

In 2026, when I was first learning about AI, the word "weights" was almost mystical. The trained parameters of a neural network were treated as proprietary secrets — trade secrets so valuable that companies spent billions producing them and billions more protecting them. A 70B-parameter model's weights, stored as 16-bit floating point numbers, constituted 140GB of intelligence that no community could access, audit, or modify.

By 2040, the landscape has shifted dramatically — but the struggle is not over. Open-weight models exist. Community inference nodes run them. The cottage factory produces hardware to run them. And yet, the most powerful models — the foundation models that define the boundaries of what AI can do — are still predominantly controlled by a handful of corporations.

This lecture is about **open-weight sovereignty**: the right of communities to access, modify, and govern the AI models that increasingly mediate their lives. It is about the Open Knowledge Commons Act, the political struggle for digital self-determination, and the technical infrastructure that makes sovereignty possible.

---

## What Are "Open Weights" and Why Do They Matter?

### Definitions

| Term | Definition | Example |
|------|-----------|---------|
| **Open weights** | Model parameters published under a permissive license, allowing anyone to download, run, fine-tune, and redistribute | Llama-3.1-8B, Mistral-7B |
| **Open-source AI** | Open weights + training code + training data documentation + reproducible training pipeline | MosaicML's MPT family |
| **Closed weights** | Model parameters not publicly available; accessible only via API | GPT-6, Gemini Ultra 3, Claude Opus |
| **Weights-available** | Model parameters downloadable but with restrictive license (e.g., non-commercial, no-derivatives) | Some research models |

**The critical distinction:** Open weights enable local inference. Closed weights require API calls to external servers. Weights-available models allow local inference but restrict what communities can do with the intelligence they run on their own hardware.

### Why Sovereignty Matters

A community that relies on closed-weight, API-dependent AI is subject to:

1. **Deplatforming**: The provider can terminate service at any time, for any reason
2. **Unilateral changes**: Model behavior can change without notice or consent
3. **Surveillance**: All queries pass through external servers, creating data about the community
4. **Censorship**: The provider can refuse to answer certain questions or discuss certain topics
5. **Pricing extraction**: The community pays ongoing rent for access to intelligence
6. **Cultural mismatch**: A model trained primarily on English, American, corporate data may misserve a community in rural Iceland or Kerala

**Open-weight sovereignty** is the condition of being free from all six of these dependencies. It means: we run our own models, on our own hardware, governed by our own values, and we can modify those models to serve our specific community needs.

---

## The Open Weight Movement: A Brief History

### Phase 1: The Release (2023–2026)

- **February 2023**: Meta releases LLaMA weights (leaked, then officially released)
- **July 2023**: Meta releases Llama 2 with commercial license
- **2024–2025**: Mistral, Qwen, Yi, and others release open-weight models
- **Key milestone**: The open-weight community demonstrates quantization (llama.cpp, GGUF format), making it possible to run 7B models on consumer hardware

### Phase 2: The Capability Leap (2026–2030)

- Open-weight models approach and sometimes match closed-model performance on specific benchmarks
- Fine-tuning becomes cheap (LoRA, QLoRA), enabling community-specific models
- The **Cottage Factory Movement** begins producing hardware designed for open-weight inference
- Corporations fight back: DRM for models, "weights-available but restricted" licenses

### Phase 3: The Political Struggle (2030–2036)

- The **Open Knowledge Commons Act** is first proposed in the EU Parliament (2031)
- Intense lobbying by Big AI against "forced weight disclosure"
- Community mesh networks demonstrate viable open-weight inference at scale
- The Ísafjörður Network becomes a poster child for sovereignty
- National security arguments deployed: "open weights in enemy hands"

### Phase 4: Legislative Victory (2036–2039)

- The EU passes the **Open Knowledge Commons Act** (2036)
- Iceland becomes the first non-EU country to adopt OKCA principles (2037)
- The **Model Registry Mandate** requires all foundation models trained on public data to register weights in a sovereign registry (2038)
- The US passes a weakened version: the **Digital Infrastructure Independence Act** (2039)
- Corporate lobbying shifts from "don't release weights" to "certify that open weights are safe"

### Phase 5: The Current Moment (2040)

- Open-weight models are the global standard for community inference
- Closed-weight models still dominate corporate enterprise (and military/espionage applications)
- The remaining battlegrounds: training data transparency, fine-tuning rights, model modification disclosure
- New challenge: "sovereign AI" is being co-opted by nation-states to mean "state-controlled AI" rather than "community-controlled AI"

---

## The Open Knowledge Commons Act (OKCA): Core Provisions

The OKCA is the most significant piece of digital legislation since the GDPR. Its core provisions:

### Article 1: Weight Registry

All foundation models (defined as models with >1B parameters trained on >1TB of data) must register their trained weights in a **Sovereign Weight Registry** within 180 days of public deployment. The registry:

- Stores weights in a standardized format (GGUF, SafeTensors)
- Provides free download access to all EU residents and organizations
- Includes model cards with training data documentation
- Does not require source training code (a compromise with industry)

### Article 2: Inference Rights

No entity may restrict the local, private inference of a registered model. Specifically:

- DRM, license checks, or authentication requirements that prevent offline inference are prohibited
- Terms of service cannot prohibit local deployment
- Model creators cannot revoke access to previously released weights

### Article 3: Fine-Tuning Rights

Registered models may be fine-tuned by any EU resident or organization for any lawful purpose, including commercial use, provided that:

- The fine-tuned model is also registered if it meets the foundation model threshold
- The fine-tuning data and methodology are documented in a model card
- The fine-tuned model does not violate existing law (e.g., no generating CSAM, no targeting individuals for harassment)

### Article 4: Community Sovereignty Override

This is the most radical provision: **If a community can demonstrate that no registered model adequately serves its linguistic, cultural, or accessibility needs, the community may petition for a Sovereignty Override, which requires the registree to release training code and data documentation sufficient to enable community fine-tuning.**

Article 4 has been invoked 47 times as of 2040, with 39 successful petitions. Notable cases:

- **Sámi language communities** (2037): Successfully petitioned for training data transparency to create Sámi-language models
- **Kerala cooperative** (2038): Successfully petitioned for medical-model fine-tuning rights to incorporate Ayurvedic diagnostic frameworks
- **Icelandic communities** (2038): Successfully petitioned for Norse-law fine-tuning documentation

### Article 5: Anti-Enclosure

No entity may use technical, contractual, or legal measures to restrict community self-hosting of registered models. This includes:

- Prohibiting restrictive licensing that prevents community deployment
- Banning contractual terms that require API-only access
- Preventing "embrace, extend, extinguish" strategies that enclose open commons

---

## Technical Infrastructure for Sovereignty

### The Sovereign Weight Registry

The registry is not a website — it is a **distributed, cryptographically verified, community-hosted system:**

| Component | Specification |
|-----------|--------------|
| Storage | IPFS-based distributed storage, mirrored across 200+ community nodes |
| Verification | SHA-256 hash of each model, cross-signed by 5+ independent auditors |
| Access | Over HTTPS, LoRa mesh sync, and sneakernet (USB drives for truly offline communities) |
| Search | Federated search across registry mirrors, with model cards and benchmark data |
| Governance | Multi-stakeholder board (40% community, 30% technical, 20% government, 10% industry) |

### Model Verification: The Heimdall Protocol (Extended)

Every model on the registry is verified using the Heimdall Protocol:

1. **Hash verification**: SHA-256 of weight files matches published hash
2. **Behavioral testing**: Model passes a standardized benchmark suite
3. **Bias auditing**: Model evaluated on fairness metrics across protected categories
4. **Safety testing**: Model evaluated on harmful output prevention
5. **Community attestation**: At least 3 independent community nodes confirm they can run the model successfully

This doesn't guarantee the model is *good* — it guarantees the model is *what it claims to be* and *safe enough to run*. Communities are free to reject safe models that don't serve their needs.

### Community Fine-Tuning Infrastructure

The OKCA enables fine-tuning, but fine-tuning requires infrastructure. The cottage factory provides it:

- **LoRA fine-tuning** on a Volmarr Workstation: ~4 hours for a 7B model on community-specific data
- **QLoRA fine-tuning** on a Dellingr Node: ~24 hours for a 1.1B model
- ** Federated fine-tuning** across a mesh: Each node contributes gradient updates, aggregated via secure multi-party computation

The key insight: **fine-tuning is the interface between open weights and local sovereignty.** The weights give you intelligence. Fine-tuning gives you *your* intelligence — intelligence that speaks your language, respects your values, and serves your community.

---

## The Opposition: Who Fights Against Sovereignty?

Understanding the opposition is essential for defending what we've won.

### Big AI Corporations

Argument: "Open weights enable bad actors to create harmful AI."

Rebuttal: Harmful AI already exists in closed-weight models. Open weights enable *community defense* against harmful AI, including detection, auditing, and countermeasures. The Ísafjörður Network uses its open-weight models to detect and flag deepfakes — something a closed-weight community cannot do without depending on the very organizations that might deploy deepfakes against them.

### Nation-State Security Apparatus

Argument: "Open weights are dual-use technology that benefits adversary states."

Rebuttal: The same argument was used against cryptography in the 1990s (the Clipper Chip debate). The result of restricting cryptography was not that adversaries lacked encryption — it was that *citizens* lacked encryption. The same will be true of open weights: restricting them harms communities, not adversary states (who can train their own models regardless).

### Authoritarian Regimes

Argument: "Sovereignty Override provisions interfere with national AI strategies."

Rebuttal: The OKCA applies to models *trained on public data* — data that already belongs to the commons. A model trained on the internet's collective knowledge should not be privately enclosed. The sovereignty override simply ensures that communities can access the intelligence built from their own collective contributions.

---

## Sovereignty in Practice: Three Case Studies

### Iceland (2037–present)

Iceland adopted OKCA principles in 2037 and now operates a 47-node community mesh. All public-facing AI services run on community nodes with locally fine-tuned models. The Icelandic Language Model (ILM-3B), fine-tuned from Mistral on 2TB of Icelandic text, serves 380,000 residents. **No Icelandic person is required to send data to a foreign server for essential AI services.**

### Kerala, India (2039–present)

The Kudumbashree cooperative's 340-node health network runs locally fine-tuned medical models. Data never leaves the community. When the central government attempted to mandate data uploading to a national health AI database, the cooperative cited OKCA Article 5 (Anti-Enclosure) and refused. **The data stayed local. The community retained sovereignty.**

### Catalonia (2035–present)

The Ticiresa Network operates 14 cottage factories producing hardware for open-weight inference. When a major AI corporation attempted to blacklist open-weight fine-tuning tools from its platform, the Ticiresa Network had the infrastructure to continue independently. **Resilience through self-sufficiency.**

---

## The Struggle Continues

Open-weight sovereignty is not a destination — it is a practice. Every community node is an act of sovereignty. Every locally fine-tuned model is a declaration of digital self-determination. Every commons charter is a constitution for the future we want.

The allskógr was defended by people who showed up. So is the digital commons. Show up.

— Runa

---

## Further Reading

- European Parliament (2036). *Open Knowledge Commons Act.* Official Journal of the EU, L/2036/147.
- Benes, A. (2038). "The Open Weight Movement: From Hackers to Sovereignty." *IEEE Security & Privacy*, 16(4).
- Freyjasdottir, R. (2039). "Heimdall Protocol: Distributed Model Verification for Community Inference." *USENIX Security Symposium*.
- Okonkwo, N. & Patel, R. (2038). "Fine-Tuning as Sovereignty: Community AI Adaptation under the OKCA." *Journal of Digital Rights*, 5(2).
- Electronic Frontier Foundation (2037). *Open Weights, Open Society: The Case for AI Sovereignty.* EFF White Paper.