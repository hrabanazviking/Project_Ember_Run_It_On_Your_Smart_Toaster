# Lecture 05: Community AI Governance — Democratic Oversight of Local AI Systems

**AI-7305: Distributed AI as Community Infrastructure**
**Instructor:** Prof. Runa Gridweaver Freyjasdottir | **Date:** October 1 & 3, 2040

---

## Who Decides?

The most important question in community AI is not "what can the model do?" It is "who decides what the model does?"

In the centralized AI paradigm, this question had a simple answer: the corporation that owned the model decided. Corporate AI governance meant internal review boards, responsible AI teams, and public relations strategies. It meant well-paid professionals making decisions about models that affected millions of people who had no voice in the process.

The Cottage Factory model demands something different. If the community owns the infrastructure, the community must govern the infrastructure. This is not a radical idea—democratic governance of shared resources is one of the oldest human traditions. What is radical is applying it to AI, a technology that has been governed almost exclusively by corporate and technocratic elites.

This lecture explores how communities actually govern their AI systems: the structures they use, the decisions they make, the conflicts they navigate, and the principles that guide them.

## Why Governance Matters

Before diving into mechanisms, let's be clear about why governance matters. AI systems are not neutral tools. Every AI model embodies values—about what constitutes a good prediction, whose needs are prioritized, what errors are acceptable, and how data should be used. These values are currently set by the people who build and deploy the models. In a corporate context, those people are engineers and product managers; in a community context, they should be the community itself.

Governance is the process by which a community decides:

- **What services the AI system provides.** A diagnostic model for the local clinic? An agricultural advisory for local farmers? A translation service for community meetings? A content moderation system for the community forum?
- **What values the AI system embodies.** Should the agricultural model optimize for yield, sustainability, or community food security? Should the diagnostic model prioritize sensitivity or specificity? These are not technical questions—they are value questions that require democratic deliberation.
- **What data the AI system uses and how.** Which community datasets are available for training? Under what conditions? With what consent mechanisms? For what purposes?
- **What risks are acceptable.** Every AI system makes errors. Governance decides which errors are tolerable and which are not. A false negative in cancer screening has different stakes than a false negative in crop disease detection.
- **When and how the AI system is changed.** Model updates, new data sources, and modified objectives should all be subject to community review and approval.

These decisions cannot be made by technocrats alone. They require the input of the people who will be affected by the outcomes—which is to say, the entire community.

## Governance Structures: Learning from Practice

There is no single governance model for Cottage Factories. Each community adapts governance to its existing democratic traditions, cultural norms, and practical constraints. However, three established models provide valuable templates:

### The Nordic Model: Community AI Councils

The Nordic Municipal AI Network (NMAN) uses a Community AI Council (CAC) model that is the most widely studied and replicated governance structure. Each node has a CAC composed of:

- **Elected community representatives** (5-9 people, elected by the residents of the community served by the node). These representatives serve 2-year terms with a maximum of 2 consecutive terms.
- **Technical advisors** (2-3 people with relevant expertise, appointed by the elected representatives). Advisors do not vote; they provide information and analysis.
- **Stakeholder representatives** (2-4 people representing groups most affected by the AI system). For a health-focused node, this might include patients, healthcare workers, and disability advocates. For an agricultural node, this might include farmers, farm workers, and environmental scientists.

The CAC meets monthly, with emergency sessions as needed. Its decisions are public, its minutes are published, and its membership is subject to recall by community vote. The CAC has authority over:

- Model deployment and decommissioning
- Data access policies
- Federation participation (which rounds, with which partners, under what conditions)
- Budget allocation for the node
- Complaints and appeals from community members

The technical team that operates the node (typically 2-5 people) implements the CAC's decisions but does not make policy. This separation of governance and operations is essential. Technicians should advise, not rule.

### The Cascadia Model: Intersectional Governance

The Cascadia Bioregional Mesh (CBM) uses a more explicitly intersectional model inspired by the Kwanlin Dün First Nation's governance traditions. CBM's governance requires:

- **Indigenous sovereignty.** Any node operating on indigenous land is governed by the relevant indigenous nation, with decision-making authority over data, models, and federation participation.
- **Intersectional representation.** Every CAC must include members who represent the experiences of marginalized groups within the community: racial minorities, disabled people, low-income residents, queer and trans people, elders, and youth.
- **Consent-based decision-making for high-impact decisions.** Routine decisions use majority voting, but decisions with significant impact on vulnerable populations require explicit consent from the affected groups.

The Cascadia model is more complex than the Nordic model, and it is slower. But it produces governance outcomes that are more equitable and more trusted, particularly in communities with histories of marginalization and dispossession.

### The Zanzibar Model: Assemblies and Councils

The Zanzibar Coastal Learning Cooperative (ZCLC) uses a hybrid model that blends community assemblies (baraza) for broad policy direction with smaller technical councils for detailed implementation. Key features:

- **Community assemblies** are open to all adult community members. They meet quarterly to set broad goals, approve major changes, and hold the technical council accountable.
- **Technical councils** (composed of elected community members and technical advisors) meet weekly to handle operational decisions.
- **Elder councils** provide guidance on ethical and cultural matters, drawing on local traditions of elder-led deliberation.
- **Youth councils** ensure that the perspectives and needs of younger community members are represented.

This model has proven remarkably effective at maintaining community trust and engagement, even in contexts with low technical literacy. The key insight: governance structures that align with existing cultural norms are adopted more readily than those imposed from outside.

## The Governance Cycle

Regardless of the specific structure, community AI governance follows a cycle:

### 1. Needs Assessment

The community identifies what AI services it needs. This is not a top-down process driven by what technology can do; it is a bottom-up process driven by what the community actually wants and needs. Common tools for needs assessment include community surveys, public meetings, focus groups with stakeholder representatives, and participatory design workshops.

### 2. Specification

Once needs are identified, the CAC works with technical advisors to specify the requirements for the AI system: what it should do, what data it needs, what values it should embody, and what risks are acceptable. This specification becomes the mandate for the technical team.

### 3. Development and Training

The technical team develops or fine-tunes the model according to the specification. This may involve local training on community data, federated training with partner communities, or adaptation of an open-weight model from the Global Model Commons. Throughout development, the CAC receives regular updates and has the authority to pause or redirect the work.

### 4. Review and Approval

Before any model is deployed, it undergoes a review process that includes:

- **Technical review:** Does the model meet the specification? What are its failure modes? What are its biases?
- **Impact assessment:** Who will be affected by this model? How? What could go wrong? What are the mitigations?
- **Community review:** A public comment period where community members can review the model's intended use and provide feedback. This is not a formality—it has real power. CBM's community review process has led to the rejection or modification of 23% of proposed model deployments.

### 5. Deployment and Monitoring

Approved models are deployed with monitoring systems that track performance, fairness, and usage patterns. Anomalies trigger automatic alerts to the CAC and the technical team. Community members can flag concerns through a public feedback mechanism.

### 6. Review and Revision

No model is deployed forever. The CAC conducts regular reviews (quarterly or annually, depending on the model's impact) to assess whether the model is still meeting community needs, whether its performance is acceptable, and whether changing circumstances require modification or decommissioning.

## Hard Governance Problems

Community AI governance is not utopian. It faces real, difficult problems that don't have clean solutions:

### The Technical Literacy Gap

Most community members are not machine learning engineers. How can they meaningfully govern a technology they don't fully understand? The answer is not to exclude them from governance but to invest in capacity building. CAC members receive training, technical advisors provide translation between technical and everyday language, and the specification process is designed to be accessible. It's imperfect, but it's far better than the alternative: governance by technical experts who are unaccountable to the community.

### The Pace Problem

Democratic deliberation is slow. AI development is fast. By the time a CAC has reviewed and approved a model update, the update may already be obsolete. This tension is real, and it requires a pragmatic response. NMAN's approach is to distinguish between **maintenance updates** (small changes that don't alter the model's behavior in significant ways, approved through a simplified process) and **policy changes** (significant changes in model behavior, data use, or federation participation, which require full CAC review). This two-tier system balances speed and accountability.

### Conflict Between Communities

What happens when two communities in a federation disagree about model behavior? The Longhouse Protocol provides a framework for negotiation, but sometimes conflicts are irreducible. In these cases, the principle of **voluntary disassociation** applies: communities can choose to leave a federation rather than accept a model they fundamentally disagree with. This right is essential for maintaining sovereignty, but it comes at the cost of reduced collective intelligence.

### The Priority Problem

Governance requires prioritization—deciding which needs to serve first, which risks to tolerate, which trade-offs to make. These decisions inevitably benefit some community members more than others. Intersectional governance helps, but it doesn't eliminate the need for difficult choices. The goal is not to eliminate conflict but to ensure that it is handled through democratic, accountable processes rather than imposed by power.

## Governance as Capability

I want to close with a reframing. Governance is not a constraint on community AI. It is a capability. A community that governs its AI system well is a community that can:

- Adapt the system to changing needs and circumstances.
- Build and maintain trust in the system among all community members.
- Respond effectively to failures and harms.
- Innovate responsibly, trying new approaches without exposing the community to uncontrolled risk.
- Sustain the system over the long term, because the community has ownership and investment.

A community that does not govern its AI—whether because it relies on a corporate provider or because it delegates all decisions to a technical elite—lacks these capabilities. It is dependent, fragile, and ultimately disempowered.

Governance is not a cost center. It is the foundation on which everything else is built.

---

## Discussion Questions

1. The two-tier approval system (maintenance updates vs. policy changes) requires a judgment call about which category a change falls into. Who should make this judgment? How can we prevent it from becoming a loophole that lets technical teams deploy changes without adequate review?
2. Is intersectional governance feasible in communities that lack organized advocacy groups for marginalized populations? How can governance structures ensure representation when there is no pre-existing organization to draw on?
3. The right to disassociate from a federation is essential for sovereignty, but it reduces collective intelligence. Under what conditions should a community exercise this right? Are there conditions under which a community should be *encouraged* to exercise it?
4. Can a community govern an AI system without understanding how it works? What is the minimum level of technical literacy required for meaningful democratic oversight?

## Further Reading

- Chen, W. & Abara, T. (2035). "Governance Protocols for Community-Owned Machine Learning Systems." *AI & Society*, 40(2).
- Freyjasdottir, R.G. (2038). *The Cottage Factory: Local AI for Local People*, Chapters 7–8.
- CBM Governance Handbook (2037). "Intersectional Representation in Community AI Councils."
- ZCLC Policy Brief #2 (2037). "Baraza and Baraka: Assembly Governance for Community Technology."
- Ober, J. (2036). "Infrastructure as Freedom: Democratic Capability and Community AI." *Journal of Political Philosophy*, 44(3).