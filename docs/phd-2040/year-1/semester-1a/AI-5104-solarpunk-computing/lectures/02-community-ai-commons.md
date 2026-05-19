# Lecture 02: Community AI Commons — Governance Models for Shared AI Infrastructure

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 2, September 10, 2040  

---

## From Allskógr to Algorithm: Why Governance Matters

The Norse *allskógr* — the commons forest — was not ungoverned land. It was the opposite: meticulously governed land, where every community member had specific rights (to graze, to forage, to timber), specific duties (to maintain paths, to report illegal harvesting), and specific dispute resolution mechanisms (the *allþing*, the commons assembly). The tragedy of the commons, as Hardin described it, occurs only when governance is *absent* — not when it is shared.

Apply this to AI infrastructure: A community-owned inference cluster without governance is not a commons. It is a free-for-all that will be captured by the most powerful user, depleted by overuse, or abandoned through neglect. **The technical architecture we discussed last week — microgrids, mesh networks, Freyja scheduling — is necessary but insufficient. Without governance, the wires are just wires.**

This lecture maps the governance models that make community AI infrastructure *actually common*.

---

## A Taxonomy of AI Commons Governance

### Model 1: Direct Democratic (The Allþing Model)

**Principle:** Every community member has equal say in all decisions about the shared AI infrastructure.

**Mechanisms:**
- Monthly *allmennþing* (commons assembly) — in-person or via mesh video
- One member, one vote on: model selection, priority tiers, budget allocation, node placement
- Elected *lögrétta* (law council) of 5–7 members who implement assembly decisions day-to-day
- Annual *dómr* (audit) where the council's actions are reviewed

**Advantages:**
- Maximum legitimacy and participation
- Community members develop AI literacy through direct engagement
- Decisions reflect actual use patterns, not hypothetical optimization

**Disadvantages:**
- Slow decision-making for technical matters (which model to run? how to configure quantization?)
- Vulnerable to demagoguery and populist pressure
- Requires significant time investment from community members

**Example:** The Ísafjörður Digital Commons Cooperative uses this model. They report 78% attendance at quarterly allmennþings (extraordinary for any governance meeting), attributed to the direct, tangible impact of decisions on community services.

### Model 2: Quadratic Voting (The Weighted Commons)

**Principle:** Members express the *intensity* of their preferences, not just direction. Quadratic voting allows members who care deeply about an issue to buy more influence — but at increasing cost.

**Mechanisms:**
- Each member receives 100 **voice credits** per quarter
- Casting 1 vote costs 1 credit; casting n votes costs n² credits
- Credits are non-transferable and expire if unused
- All decisions are transparent — who voted, how much, for what

**The Math That Makes It Work:**

If a medical clinic needs the cluster to prioritize a medical triage model, and a hobbyist wants to run a creative writing assistant, the clinic can spend 25 credits for 5 votes (cost: 5² = 25) while the hobbyist spends 1 credit for 1 vote. The clinic's preference intensity is 25x, but their vote weight is only 5x. **This protects minorities with strong preferences from majorities with weak ones.**

**Advantages:**
- Captures preference intensity, not just preference direction
- Prevents "tyranny of the majority" on issues where some members care much more
- Naturally allocates resources toward higher-value uses

**Disadvantages:**
- More complex to implement and understand
- Requires robust identity verification (one person = one voice credit allocation)
- Can be gamed through Sybil attacks if identity is weak

**Example:** The Malmö Community Mesh uses quadratic voting for model selection. In Q2 2039, they voted to add a Swedish-language legal assistance model after the local legal aid clinic spent 64 credits (8 votes) while most members spent 1 credit each. The model now serves 200+ people per month.

### Model 3: Liquid Democracy (The Delegated Commons)

**Principle:** Members can vote directly on issues they care about, or delegate their vote to a trusted representative on specific topic domains.

**Mechanisms:**
- Issue-specific delegation: I delegate my vote on "model selection" to Dr. Árnadóttir, but vote directly on "priority tiers"
- Delegations are revocable at any time — no fixed terms
- Delegation chains are transparent and auditable
- Delegates' votes are public, creating accountability

**Advantages:**
- Combines democratic legitimacy with expert input
- Flexible: different delegates for different domains
- Reduces participation burden while maintaining agency

**Disadvantages:**
- Complexity increases with delegation chains (A→B→C→?)
- Risk of "super-delegates" accumulating too much influence
- Requires sophisticated voting infrastructure

**Example:** The Barcelona Municipal AI Grid uses liquid democracy for its 12-node cluster serving 180,000 residents. Delegation patterns show tight clustering around technical experts for model configuration, and broad direct voting for priority tier decisions.

### Model 4: Stewardship Council (The Heiðr Model)

**Principle:** A small council of vetted stewards manages the infrastructure on behalf of the community, with strict accountability mechanisms and recall provisions.

**Mechanisms:**
- 7 stewards, elected for 2-year terms, with staggered elections
- Stewards must be active community members (6+ months residency)
- Decisions require 5/7 supermajority for model changes, 7/7 unanimous for security critical
- Any community member can call a *þingfest* (council challenge) with 10% petition
- Stewards are subject to *árásarvörður* (attack audit) — a public review of all decisions every 6 months

**Advantages:**
- Fast decision-making by informed, accountable individuals
- Clear responsibility and accountability
- Works well for small communities with high trust

**Disadvantages:**
- Risk of council capture or groupthink
- Requires strong accountability mechanisms
- Less direct participation

**Example:** The Akureyri Helper Network (pop. 800) uses this model. Their stewardship council meets weekly over coffee and makes most decisions in under 15 minutes. The key: they live in the same neighborhood where the node operates.

---

## Operational Governance: The Day-to-Day

### Model Selection and Updating

Who decides what model runs on the shared node? This is the most contentious governance question in any AI commons. We propose the **Weight Selection Protocol (WSP)**:

1. **Proposal**: Any community member proposes a model (from an approved registry or with justification for new model)
2. **Impact Assessment**: A technical subcommittee evaluates resource requirements, bias profile, licensing, and community benefit
3. **Community Vote**: Using the selected voting mechanism (quadratic, liquid, or direct)
4. **Implementation**: Elected operators flash the model to available nodes
5. **Review**: After 30 days, the community reviews usage data and votes to keep, modify, or remove
6. **Iterate**: Every 6 months, all models undergo sunset review

### Resource Allocation: Priority Tiers

The Freyja Scheduler needs priority tiers to operate. These tiers are themselves governance decisions:

| Tier | Services | % of Compute Allocation | Notes |
|------|----------|------------------------|-------|
| Gold | Medical triage, emergency coordination | 40% | Always-available, battery-reserved |
| Silver | Education, translation, legal aid | 35% | Best-effort, gracefully degrades |
| Bronze | Entertainment, personal projects | 25% | Surplus-only, interruptible |

These percentages are *not technical defaults* — they are *political decisions* made by the community. A rural farming community might allocate Bronze-tier to crop diagnosis. A fishing village might make tide prediction Gold-tier. The solarpunk principle: **the community configures the scheduler, not the other way around.**

### Dispute Resolution: The Várlog

Every commons needs a dispute resolution mechanism. We adapt the Norse *várlog* (spring law, a temporary legal code enacted at the spring assembly) into a **Várlog Protocol for AI Commons**:

1. **Complaint**: Any member files a complaint about infrastructure governance
2. **Mediation**: Two randomly selected community members attempt mediation
3. **Arbitration**: If mediation fails, a 5-member arbitration panel (chosen by lot from the broader community, excluding parties to the dispute) renders a binding decision
4. **Appeal**: Decisions can be appealed to the next allmennþing by a 15% petition

The Várlog Protocol emphasizes **speed, community participation, and restorative outcomes**. Punishments are rare; corrections are common.

---

## Funding the Commons

### The Compute Dividend Model

If the AI commons serves the community, the community should fund it. But how?

**Option A: Municipal Funding** — The local government includes AI infrastructure in the municipal budget. Pro: stable funding. Con: political vulnerability, potential for government overreach on model selection.

**Option B: Cooperative Membership** — Community members pay a monthly membership fee (~$3–5/month per household at current costs). Pro: democratic accountability. Con: excludes those who cannot pay, requires collection infrastructure.

**Option C: Compute Dividend** — The commons generates revenue by selling surplus compute (beyond community needs) on the open market, then distributes profits as a dividend (or reinvests in infrastructure). Pro: self-sustaining. Con: may incentivize running community-unfriendly workloads.

**Option D: Endowment Model** — An initial capital grant (from a government, foundation, or cooperative) funds hardware, which then operates at near-zero marginal cost for 5–10 years. Pro: no ongoing funding needed. Con: requires initial capital, vulnerable to hardware failures beyond reserve budget.

**Our Recommendation: B+D Hybrid.** An endowment covers hardware. Membership fees ($2/month, sliding scale) cover maintenance and expansion. Surplus compute is donated to adjacent communities, not sold — because selling compute creates market incentives that conflict with commons governance.

### The Real Cost Numbers

A 10-node community cluster (serving ~500 people) costs:

| Item | Cost (USD) | Lifespan | Annualized |
|------|-----------|-----------|------------|
| 10x Dellingr Nodes | $800 | 5 years | $160/yr |
| 10x Solar arrays (40W each) | $400 | 10 years | $40/yr |
| 10x Battery packs (40Wh each) | $200 | 3 years | $67/yr |
| Networking (LoRa radios, antennas) | $100 | 5 years | $20/yr |
| Enclosures, cabling, mounting | $200 | 10 years | $20/yr |
| Maintenance reserve (10%) | — | — | $31/yr |
| **Total** | **$1,700** | — | **$338/yr** |

At 500 users: **$0.68/person/year.** This is the cost of a single cup of coffee per person per year to have community-owned AI inference. The economics of post-scarcity begin here.

---

## The Commons Is Political

Let me be direct: **the reason corporate AI resists commons governance is not technical — it is political.** A community that owns its inference infrastructure is a community that cannot be deplatformed, cannot be data-mined, and cannot be subjected to unilateral model changes. This is digital sovereignty, and it is treated as a threat by every entity whose business model depends on being the sole intermediary between humans and AI.

The governance models we discuss today are not neutral technical choices. They are **political architectures** that determine who has power over the intelligence that increasingly mediates everyday life. Choose them carefully. Defend them fiercely.

The allskógr was defended by generations of Norse communities who understood that the commons only exists if people are willing to tend it. We are those people now.

— Runa

---

## Further Reading

- Ostrom, E. (1990/2035). *Governing the Commons.* Cambridge University Press. (With 2035 AI commons foreword by Árnadóttir.)
- Lallement, M. & Virtanen, E. (2037). "Quadratic Voting for Community AI Governance." *Journal of Digital Democracy*, 8(2).
- Hern, M. & Johal, W. (2035). "Compute Dividends: Universal Access to Inferential Capacity." *Journal of Abundance Economics*, 12(3).
- Ísafjörður Digital Commons Cooperative (2039). *Governance Charter v3.* Available at `isafjordur-commons.is/charter`.
- Weyl, E.G. (2031). "Quadratic Voting and the Robustness of Democratic Governance." *Expanded and revised edition*, Princeton University Press.