# Lecture 05: Post-Scarcity Economics — AI Labor and the Economics of Abundance

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 6, October 8, 2040  

---

## The Abundance Paradox

We live in the strangest economic moment in human history. AI can now perform — or substantially assist in — every cognitive task that humans once performed for wages. Medical diagnosis, legal research, software engineering, creative writing, scientific analysis, language translation, financial modeling, agricultural planning: all of these are partially or fully automatable today, in 2040. And the cost of compute continues to fall — halving roughly every 18 months — which means the cost of AI labor is falling too.

And yet: most people still work 40+ hours per week. Most communities still experience scarcity in housing, healthcare, and education. The abundance is real, but the distribution is broken.

This lecture examines the economics of the solarpunk transition: how AI labor, renewable energy, and commons governance combine to create conditions of abundance, and why achieving post-scarcity requires deliberate political action, not just technical progress.

---

## The Cost Structure of AI Labor

### Marginal Cost of Inference

Let's establish the fundamental economic fact: **the marginal cost of AI inference is approaching zero.**

| Year | Cost per 1M tokens (70B model) | Notes |
|------|-------------------------------|-------|
| 2023 | $30.00 | Cloud API, H100-class GPUs |
| 2026 | $3.00 | Optimized inference, open-weight models |
| 2030 | $0.30 | Edge inference, quantized models |
| 2034 | $0.03 | Community mesh, renewable energy |
| 2038 | $0.003 | Dellingr Node on solar, Q4_K_M |
| 2040 | $0.001 | Volmarr cluster, speculative decoding |

The cost per intelligent action is now a rounding error. A full medical triage consultation costs less in compute than the electricity to light the examining room. A legal brief costs less than the paper it would be printed on. An hour of personalized tutoring costs less than a glass of water.

This is what **post-scarcity** means in practice: not that everything is free, but that the marginal cost of essential cognitive services is so low that scarcity is a distribution problem, not a production problem.

### The Renewable Energy foundations

AI labor costs don't exist in isolation — they sit atop energy costs. And here, the news is equally transformative:

| Year | Solar PV cost (per W installed) | Wind cost (per W installed) | Battery cost (per kWh) |
|------|--------------------------------|----------------------------|------------------------|
| 2020 | $2.50 | $1.50 | $150 |
| 2025 | $0.80 | $0.90 | $100 |
| 2030 | $0.30 | $0.55 | $60 |
| 2035 | $0.12 | $0.35 | $30 |
| 2040 | $0.05 | $0.25 | $15 |

Solar now costs 50x less than in 2020. Combined with AI-assisted optimization (panel orientation, grid management, predictive maintenance), the effective cost of renewable energy is approaching zero. A community with $500 of solar infrastructure can generate more energy than it needs for compute + lighting + communications.

**The dual cost collapse — AI inference and renewable energy — is the material basis for post-scarcity.**

---

## Economic Models for Abundance

### Model 1: Universal Compute Dividend (UCD)

**Principle:** Every person receives a monthly allocation of compute credits, redeemable at any community inference node.

**Implementation:**
- Each community node reports available inference capacity to a regional registry
- The registry allocates capacity to residents based on population
- Residents receive a **compute wallet** with monthly credits (e.g., 10M tokens on a 7B model, or equivalent)
- Unused credits roll over for 3 months, then expire
- Additional credits can be purchased (sliding scale) or earned by contributing to the commons (maintaining nodes, curating data)

**Economic Analysis:**
- At $0.001 per 1M tokens, 10M tokens/month costs $0.01 per person
- For a community of 2,000: $20/month total compute cost
- This is 0.001% of a typical municipal budget

**The key insight:** The UCD is not expensive because compute is cheap. The UCD is *cheap* precisely because compute is abundant. The only reason to deny someone compute access is spite, not scarcity.

### Model 2: Labor-Value Redistribution

**Principle:** AI labor generates economic value. That value should be redistributed to the humans whose labor it augments or replaces.

**Mechanism:**
1. A community tax on commercial AI inference (paid by businesses using community infrastructure)
2. Revenue distributed as a **productivity dividend** to all residents
3. Dividend is paid in community credits (compute, energy, local goods) and/or fiat currency

**Estimated Revenue:**
- A community of 2,000 with 10 inference nodes serving local businesses
- Commercial inference revenue: ~$500/month (at community rates)
- Per resident dividend: $0.25/month — trivial in financial terms
- But in *compute* terms: 2.5M additional tokens/month per person

**This model doesn't eliminate work. It rebalances the relationship between human and AI labor.**

### Model 3: The Commons Productivity Compact

**Principle:** Community members contribute labor to maintain and improve the commons (node maintenance, data curation, governance participation, manufacturing). In return, they receive full access to commons services.

**This is the Norse allskógr model applied to productivity:**
- You have the right to use the commons forest (compute services)
- You have the duty to maintain the commons forest (stewardship tasks)
- The forest produces more when well-tended (network effects, model improvements)

**Estimated time commitment:**
- Node maintenance: 2 hours/month per node
- Data curation: 4 hours/month per community
- Governance participation: 3 hours/month (allmennþing attendance)
- Manufacturing (cottage factory): Voluntary, compensated in community credits

- **Total: ~6 hours/month per active community member**
- **For 200 active members: equivalent of 50 FTE community servants**

The commons productivity compact transforms volunteerism into structured reciprocity. It's not charity — it's maintenance of shared infrastructure that benefits everyone.

---

## The Transition Problem: From Scarcity to Abundance

### The J-Curve of Post-Scarcity Investment

Post-scarcity adoption follows a J-curve:

| Phase | Investment | Return | Net Position |
|-------|-----------|--------|-------------|
| **T0–T1** (Year 0–1) | $70K for cottage factory + compute cluster | Minimal production | Negative ($70K deficit) |
| **T1–T2** (Year 1–2) | $5K/year maintenance | $15K/year in local production value | Approaching breakeven |
| **T2–T3** (Year 2–3) | $2K/year maintenance | $30K/year in local production + reduced import costs | Net positive ($28K surplus) |
| **T3+** (Year 3+) | $2K/year maintenance | $40K+/year in local production + multiplier effects | Strongly positive |

The J-curve is the reason post-scarcity doesn't happen automatically. Communities need upfront capital to build the infrastructure, and that capital is hard to obtain in a scarcity-based economy where short-term ROI dominates investment decisions.

**This is the role of the Open Knowledge Commons Act** (which we'll cover in detail in Paper 2 and Lecture 06): public funding for community AI infrastructure, modeled on rural electrification programs of the 1930s.

### Distribution Failure Modes

Even with abundant compute and energy, post-scarcity can fail through distribution problems:

1. **Enclosure**: Private entities capture commons resources (e.g., a corporation buys community compute time, pricing out residents)
2. **Digital Divide**: Technical literacy gaps prevent some community members from accessing services
3. **Governance Capture**: Well-funded interests dominate commons governance, redirecting resources
4. **Infrastructure Neglect**: After initial deployment, maintenance is deferred until systems fail
5. **Centralization Pressure**: Efficiency arguments push toward centralization, undermining resilience

Each failure mode has a countermeasure drawn from commons governance:

| Failure Mode | Countermeasure |
|-------------|----------------|
| Enclosure | Compute Dividend (non-transferable credits) |
| Digital Divide | Community training programs, accessibility-first design |
| Governance Capture | Quadratic voting, rotated stewardship councils |
| Infrastructure Neglect | Maintenance mandates in commons charter, earmarked funding |
| Centralization Pressure | Federation standards, interoperability requirements |

---

## Work in Post-Scarcity: What Do Humans Do?

### The Redefinition of Productivity

When AI handles routine cognitive labor, what constitutes "productive work"? The solarpunk answer: **care, creativity, and cultivation.**

| Domain | AI Role | Human Role |
|--------|---------|------------|
| Healthcare | Triage, diagnostic assistance, drug interaction checking | Emotional care, complex decision-making, community health |
| Education | Personalized tutoring, assessment, curriculum generation | Mentorship, social integration, values transmission |
| Manufacturing | Process control, quality assurance, design optimization | Craft, community production planning, artisanal work |
| Agriculture | Crop monitoring, weather prediction, pest identification | Land stewardship, food culture, community cultivation |
| Governance | Meeting summarization, policy analysis, record-keeping | Values articulation, dispute resolution, community building |
| Creative arts | Drafting, variation generation, technique assistance | Vision, meaning, emotional depth, cultural significance |

The pattern is clear: **AI handles the mechanical and the repetitive; humans handle the meaningful and the relational.** This doesn't eliminate work — it transforms it.

### The 15-Hour Week

Keynes predicted a 15-hour workweek by 2030. He was wrong about the timeline but right about the direction. In communities with cottage factories and AI commons, the average productive labor contribution is:

- **Technical stewardship**: 4 hours/week (node maintenance, manufacturing oversight)
- **Care work**: 6 hours/week (health, education, elder care — partially AI-assisted)
- **Governance**: 2 hours/week (allmennþing, committee work)
- **Creative/personal**: 3+ hours/week (art, craft, social, whatever you choose)

- **Total: ~15 hours/week** of structured community contribution

This is not utopian — it is the lived experience of communities in the Ticiresa Network, Ísafjörður, and Kerala. The 15-hour week doesn't mean people are idle. It means their labor is directed toward community benefit rather than profit extraction.

---

## The Macro Picture: From Scarcity Economics to Abundance Economics

Traditional economics assumes scarcity: limited resources, unlimited wants. Post-scarcity economics inverts this: **for essential goods and services (compute, energy, basic manufacturing, healthcare triage, education), resources are abundant and wants are satisfiable.**

This doesn't mean *all* resources are abundant. Land, attention, and rare earth elements remain scarce. But the *essential* substrate of cognitive and physical productivity — compute, energy, and basic manufacturing — has become abundant through AI and renewable energy.

The economic models we've discussed (UCD, labor-value redistribution, commons productivity compact) are not *redistribution from scarcity*. They are **allocation from abundance.** The difference is fundamental: in a scarcity economy, someone must lose for someone else to gain. In an abundance economy, the challenge is not hoarding but ** logistics and access.**

This is the economics of the allskógr: the forest provides enough for everyone, if we tend it together and distribute with care.

— Runa

---

## Further Reading

- Hern, M. & Johal, W. (2035). "Compute Dividends: Universal Access to Inferential Capacity." *Journal of Abundance Economics*, 12(3).
- Buxton, N. & Patel, R. (2038). *Post-Scarcity Economics: From Theory to Practice.* Verso.
- Keynes, J.M. (1930). "Economic Possibilities for our Grandchildren." *(Reissued 2036 with commentary on AI labor displacement.)*
- Ticiresa Network Cooperative (2039). *Productivity and the 15-Hour Week: Two Years of Data.* Available at `ticiresa.cat/15hr-report`.
- Árnadóttir, S. (2039). "The Allskógr Model: Forest Commons as Metaphor for AI Governance." *Scandinavian Journal of Economics*, 141(4).