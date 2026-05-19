# Lecture 06: The Longhouse Economy — Post-Scarcity Through Local Abundance

**AI-7305: Distributed AI as Community Infrastructure**
**Instructor:** Prof. Runa Gridweaver Freyjasdottir | **Date:** October 8 & 10, 2040

---

## From Scarcity to Abundance

The dominant economic model of the centralized AI era was built on artificial scarcity. Compute was scarce, so it was concentrated in data centers owned by a few corporations. Data was scarce, so it was extracted from billions of people without their consent. Access was scarce, so it was rationed through subscription tiers and API keys. The corporations that controlled these scarce resources extracted enormous rents, creating a small number of extremely wealthy entities and a large number of dependent users.

The Cottage Factory model is built on a fundamentally different premise: **local abundance is possible, and it changes everything.**

This is the Longhouse Economy named after the communal longhouses of Norse and Haudenosaunee traditions—spaces where resources were shared, production was collective, and abundance was created through cooperation rather than competition. The longhouse was not a space of poverty. It was a space where everyone had enough because everyone contributed and everyone received.

The question this lecture addresses is: how does distributed AI infrastructure make the Longhouse Economy possible, and what does that economy look like in practice?

## The Three Scarcities of Centralized AI

To understand the Longhouse Economy, we must first understand the scarcities that the centralized model created—and why they were artificial.

### Scarcity of Compute

In 2026, training a frontier AI model required thousands of GPUs running for months, at a cost of tens of millions of dollars. This was presented as an inevitable consequence of AI's computational requirements, but it was actually a consequence of the centralized model's obsession with scale. Industry leaders competed to build the largest, most general models possible—models that knew everything about every topic, in every language, for every user. This is like building a single factory that produces every kind of goods for the entire world. It's not efficient; it's megalomaniacal.

The Cottage Factory model recognizes that most communities don't need a model that knows everything. They need a model that knows enough about their specific context to be useful. A diagnostic model for a rural Norwegian clinic needs to know about the conditions that actually present in Norwegian primary care, not about tropical diseases. An agricultural model for a Swedish farm cooperative needs to know about Nordic soil conditions and crop varieties, not about cassava cultivation in Nigeria.

Specialization reduces computational requirements dramatically. A community-scale model can be trained on 4-16 GPUs in days, not months. The total compute across 100 Cottage Factory nodes training specialized models is a fraction of the compute required for a single frontier model—and it produces 100 models that are each better at their specific task than the frontier model would be.

This is the compute abundance thesis: **distributed, specialized computation is more efficient than centralized, general computation.** Not because of some magical algorithmic breakthrough, but because specialization is more efficient than generality, and locality eliminates the overhead of universal coverage.

### Scarcity of Data

The centralized model treated data as scarce because it needed enormous quantities of data to train universal models. It scraped the web, purchased dataset licenses, and extracted user data through surveillance capitalism—all to feed models that needed to know everything about everyone.

But data, in a community context, is not scarce. It is abundant. Every community generates vast quantities of data through its daily activities—health data, agricultural data, educational data, economic data, cultural data. The scarcity was not in the data itself but in the infrastructure to use it locally. Once a community has its own compute, its data becomes a resource it can harness directly.

More importantly, community data is **contextually appropriate.** A dataset of patient outcomes from a community clinic reflects the actual disease burden, demographic composition, and treatment patterns of that community. It is not a biased sample of a global population; it is a representative sample of the local population. This makes it more valuable for local AI than any globally scraped dataset could ever be.

The data abundance thesis: **community-bounded data is more valuable for community AI than any amount of globally aggregated data.** What matters is not the size of the dataset but its relevance to the task at hand.

### Scarcity of Access

The centralized model rationed access through pricing, gating, and platform control. Free tiers were limited, paid tiers were expensive, and API access was subject to terms of service that could change at any time. This was presented as necessary to recoup the enormous investment in compute and data, but it was also a mechanism for extracting rents and maintaining dependency.

In the Cottage Factory model, access is a function of community membership, not purchasing power. If you are a member of the community that owns the node, you have access to its services. Period. No subscription tiers, no API rate limits, no terms of service that you can't negotiate. The node exists to serve you, not to profit from you.

The access abundance thesis: **when infrastructure is communally owned, access is determined by membership, not by wealth.** This doesn't mean services are unlimited—it means they are allocated through democratic governance rather than market pricing.

## The Economic Model

So far I've described the Longhouse Economy in aspirational terms. Let me get concrete about the economics.

### Cost Structure of a Cottage Factory Node

Based on operational data from NMAN, here are the annual costs for a medium node (serving ~50,000 people):

- **Compute hardware (amortized over 5 years):** €30,000/year
- **Storage hardware (amortized over 5 years):** €5,000/year
- **Networking infrastructure:** €4,000/year
- **Energy (solar, with battery storage, amortized):** €6,000/year
- **Facilities (including community space):** €15,000/year (often donated or subsidized by the municipality)
- **Technical staff (2 FTE):** €80,000/year
- **Governance and community engagement:** €10,000/year
- **Total:** ~€150,000/year

That works out to approximately **€3 per person per year** for a community of 50,000. For comparison, the per-capita cost of centralized AI services (including the externalized costs of energy, data extraction, and platform dependency) was estimated at $50-200 per year in the 2020s—ordered by the market price of equivalent services and the societal costs of data extraction.

The Cottage Factory is not just more sovereign and more sustainable. It is dramatically cheaper.

### Revenue Model

Cottage Factory nodes are not profit-seeking enterprises. They are community infrastructure, funded through a mix of:

- **Municipal budgets** (the largest source in NMAN, where nodes are treated like libraries or fire departments—essential public services)
- **Cooperative membership fees** (in CBM, where nodes are organized as consumer cooperatives)
- **Grants and public funding** (particularly for startup costs and for nodes in underserved communities)
- **Service fees for external users** (some nodes offer inference services to non-community users for a fee, creating a revenue stream that subsidizes community access)
- **Federation participation fees** (nodes that participate in the Global Model Commons contribute a portion of their compute to shared model training, and in return receive access to the commons)

None of these revenue sources require extracting data from community members or selling access to community services to advertisers. The economic model is transparent, sustainable, and accountable.

### The Multiplier Effect

Here's the part that most surprises people who are used to thinking about AI in corporate terms: the Cottage Factory generates economic value *beyond* the direct services it provides.

When a rural community has access to local AI for agricultural advisory, the farmers in that community make better planting decisions, reduce crop losses, and increase their income. When a community clinic has diagnostic AI, health outcomes improve, reducing the societal cost of untreated illness. When a community school has personalized learning AI, students achieve better educational outcomes, increasing their future economic productivity and creativity.

These multiplier effects are hard to quantify precisely, but NMAN's longitudinal studies suggest that every €1 invested in community AI infrastructure generates €4-7 in community economic value over a 5-year period. This is not because the AI is magical; it is because the AI is *appropriate*—designed for the community's specific needs and accessible to everyone in the community.

## The Longhouse Protocol: Economic Coordination

The Longhouse Protocol (v3.2) is not just a technical specification for federated learning. It is also an **economic coordination mechanism** that governs how Cottage Factories share resources, compensate each other, and manage the commons.

### Compute Sharing

When Community A has excess compute capacity (because it's between training cycles, or because its solar panels are producing more than the node needs), it can contribute that capacity to the federation. Other communities with immediate needs (because they're in the middle of a training cycle, or because their local weather has reduced their solar output) can draw on this shared capacity. The accounting is tracked in **compute credits**—a non-monetary currency that represents contributed and consumed compute.

Compute credits cannot be hoarded or traded for money. They can only be used for federation compute. This prevents financialization and ensures that the compute commons serves community needs rather than creating a new market for speculative extraction.

### Model Sharing

When a community trains a model that might be useful to other communities, it can contribute the model (or the adapter weights) to the **Global Model Commons**—a shared repository of community-trained models. Other communities can download, adapt, and use these models freely.

The Global Model Commons operates under a **commons license** that requires derivative models to also be shared with the commons. This is the reciprocal principle at work: you benefit from the commons, and you contribute to the commons. It is not a market transaction; it is mutual aid.

### Knowledge Sharing

Beyond compute and models, the Longhouse Economy depends on knowledge sharing: documentation, training materials, governance templates, best practices, and lessons learned. NMAN, CBM, and ZCLC all maintain extensive knowledge bases that are freely available to any community starting a Cottage Factory.

This knowledge sharing is not altruism; it is investment. Every community that joins the network strengthens the commons for everyone. The ZCLC's innovations in asynchronous federation benefit NMAN's nodes just as NMAN's thermal integration designs benefit CBM's deployments. We are all building the same house, even though we each live in different rooms.

## What About the Things We Can't Produce Locally?

A common objection to the Longhouse Economy is that some things cannot be produced locally. GPUs are manufactured in a few factories. Submarine cables connect continents. The fundamental research underlying AI architectures happens in universities and research labs that are not community-owned.

This objection is real and important. The Longhouse Economy does not claim that *everything* can be produced locally. It claims that the things that *can* be produced locally should be, and that the things that can't should be governed through fair, transparent, and accountable global coordination rather than through corporate monopolies.

In practice, this means:

- **Hardware procurement** is coordinated through the Global Model Commons' hardware working group, which negotiates collective purchasing agreements with manufacturers on behalf of member communities.
- **Research funding** comes from a mix of public grants, cooperative research agreements, and contributions from Cottage Factory nodes (who have a direct interest in advancing the state of the art for community-scale AI).
- **Global infrastructure** (submarine cables, satellite networks) is governed through multilateral agreements that prioritize access equity and community sovereignty.

The Longhouse Economy is not autarky. It is **strategic self-reliance**: producing locally what can be produced locally, cooperating globally for what cannot, and never allowing dependency to become exploitation.

## Post-Scarcity: Not Utopia, But Not Impossibility

The word "post-scarcity" makes people nervous. It sounds utopian, naive, or both. Let me be clear about what I mean and what I don't.

I do not mean that the Longhouse Economy eliminates all scarcity. There will always be limits—on energy, on materials, on human time and attention. The question is not whether scarcity exists (it does) but whether it is *artificially created* to enable extraction (as in the centralized AI model) or *honestly acknowledged* and managed through democratic cooperation (as in the Longhouse Economy).

I do mean that the Cottage Factory model, combined with renewable energy, community governance, and federated cooperation, can produce **local abundance** in AI capabilities. A community with a medium-sized node and access to the Global Model Commons has more AI capability—more relevant, more accurate, more accessible, more accountable—than that same community could ever obtain through centralized services.

And I do mean that this local abundance has cascading effects. When AI capabilities are abundant and locally governed, they enable abundance in other domains: better health care, better education, better agriculture, better governance. AI becomes infrastructure—like roads, like libraries, like clean water—that amplifies community capability without extracting community wealth.

This is not a utopian claim. It is an empirical one, supported by fourteen years of operational data from communities around the world. The Longhouse Economy is not a promise. It is a practice. It is happening now, in 147 Nordic communities, 62 Cascadian communities, 28 East African communities, and more every year.

The question is not whether it's possible. The question is whether we have the courage to build it.

---

## Discussion Questions

1. Compute credits are a non-monetary currency that cannot be hoarded or traded. Is this enforceable in practice? What prevents communities from finding ways to monetize their compute credits?
2. The multiplier effect (€1 invested → €4-7 return) is impressive, but it assumes that communities can capture the value they generate. In a globalized economy, is this assumption valid? Can communities really keep the economic benefits of their AI infrastructure local?
3. "Strategic self-reliance" acknowledges that some resources must be sourced globally. How does the Longhouse Economy prevent these global supply chains from recreating the extractive dynamics it seeks to avoid?
4. Is the Longhouse Economy only possible in wealthy, well-resourced communities? How would it work in communities that lack the initial capital for a Cottage Factory node?

## Further Reading

- Freyjasdottir, R.G. (2038). *The Cottage Factory: Local AI for Local People*, Chapters 9–11.
- Lindström, E. & Chen, W. (2037). "The Longhouse Protocol: Economic Coordination in Community AI Federations." *Journal of Cooperative AI*, 12(3).
- Osei-Mensah, A. (2039). "Abundance Without Extraction: Economic Models for Community AI." *Daedalus*, 148(4).
- NMAN Annual Report (2039). "Fifteen Years of Community AI: Economic Impact Assessment."
- Bollier, D. (2036). *AI as Commons: Beyond the Market/State Duopoly*. (Updated edition with community AI case studies.)