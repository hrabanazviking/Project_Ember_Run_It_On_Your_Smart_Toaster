# Lecture 06: Cottage Factory Sovereignty — Local AI Production and Digital Self-Determination

*AI-7303: Open Weight Movements and Digital Sovereignty*
*Week 6 | Prepared by Runa Gridweaver Freyjasdattir*

---

## Introduction: The Factory in the Cottage

In his 2033 book *The Cottage Factory*, Prof. Kael Ndiaye — the instructor of this course — proposed a metaphor that has since become central to the field. The cottage industry, Ndiaye argued, was the pre-industrial model of distributed production: skilled workers, often in their own homes, producing goods using tools they owned and controlled. The factory system replaced it — concentrating production in centralised facilities, deskilling labour, and transferring ownership of the means of production from workers to capitalists.

The AI industry of the 2020s, Ndiaye argued, was undergoing a similar transition. The "cottage" producers — individual researchers, small labs, hobbyists fine-tuning models on consumer hardware — were being displaced by "factories" — massive data centres owned by a handful of corporations, running models that could not be run, modified, or understood outside those facilities.

But the cottage industry did not simply disappear. It was displaced, and then it re-emerged in new forms. The open-weight movement, Ndiaye argued, was the re-emergence of cottage production in the age of AI: distributed, skilled, locally controlled, and using tools (open models) that were collectively owned rather than privately held.

This lecture explores the concept of cottage factory sovereignty — the idea that **the unit of digital self-determination is not the nation-state, not the corporation, but the local community equipped with open weights and sufficient compute to use them.**

## From Sovereignty to Self-Determination

The concept of sovereignty, as we have used it in this course, has mostly referred to national or supranational sovereignty — the ability of a state (or union of states) to control its own digital infrastructure. The OKCA, the European AI Agency, and the Chinese sovereign AI strategy are all exercises in *state* sovereignty.

But sovereignty has a deeper meaning: self-determination. The ability of a community — a village, a cooperative, a university, a hospital — to make decisions about its own digital infrastructure without dependency on external providers. This is what Ndiaye calls "cottage factory sovereignty": the capacity for local AI production that serves local needs, under local control.

The distinction matters because state sovereignty does not guarantee community self-determination. A state that controls national AI infrastructure may still deploy that infrastructure in ways that serve state interests rather than community needs. A national data centre in Dakar does not automatically serve the needs of a rural health clinic in Saint-Louis — any more than a US-owned data centre in Frankfurt serves the needs of a Danish municipal government.

Cottage factory sovereignty asks: **what would it take for a community of any size — a village, a university department, a small business, a cooperative — to produce and maintain its own AI capabilities?** The answer, it turns out, is surprisingly little in the age of open weights.

## The Technical Stack of Cottage Production

The technical requirements for local AI production have changed dramatically between 2024 and 2034. In 2024, running a frontier model required access to data centre-class GPUs costing tens of thousands of dollars. In 2034, the landscape looks very different:

1. **Models.** Open-weight models at multiple capability levels are available from Chinese (DeepSeek, Qwen), European (Mistral, the EAA repository), and community (fine-tuned variants) sources. The OKCA's public model repository provides curated, evaluated models for European deployment. A community that needs AI does not need to train from scratch — it needs to select and fine-tune.

2. **Compute.** The consumer and prosumer GPU market has evolved substantially. The NVIDIA RTX 5090 (released 2025) and its successors offer inference capability that would have required data-centre hardware five years earlier. Apple Silicon — the M-series chips — provides competitive inference performance at consumer prices. And the emergence of dedicated AI inference chips (the Neural Processing Units in modern phones, the dedicated inference cards from Cerebras and Graphcore) has further reduced the hardware barrier.

3. **Training data.** The OKCA's Data Commons, the Common Crawl, Hugging Face datasets, and numerous domain-specific datasets provide a rich training data ecosystem. A community that needs to fine-tune a model for local languages, local knowledge, or local regulations does not need to collect data from scratch — it needs to select and augment.

4. **Expertise.** The talent pipeline has expanded enormously. The AI education programmes of the late 2020s, the proliferation of open-source AI courses, and the community knowledge embedded in Hugging Face, GitHub, and local AI meetup groups have created a broad base of expertise that was not available in 2024.

5. **Tooling.** The open-source AI tooling ecosystem — PyTorch, Hugging Face Transformers, vLLM, LoRA fine-tuning scripts, quantisation tools — has matured to the point where a competent developer can deploy and fine-tune an open-weight model with a few days of effort, not a few months.

The sum of these changes is that the barrier to local AI production has dropped from "millions of dollars and a team of PhDs" to "thousands of dollars and a competent developer." This is not zero — and we will discuss the equity implications below — but it is a transformation of the production function that makes cottage factory sovereignty technically feasible for the first time.

## Case Studies in Cottage Production

### The Saint-Louis Health Clinic (Senegal, 2032)

Prof. Ndiaye's book documents the case of a rural health clinic in Saint-Louis, Senegal, that in 2032 deployed a fine-tuned open-weight model for diagnostic assistance. The clinic used a Qwen 2.5 variant fine-tuned on Senegalese health data (malaria patterns, local drug interactions, Wolof-language symptom descriptions) and deployed on a single consumer-grade workstation.

The model was not a replacement for medical expertise — it was a clinical decision support tool that helped community health workers identify conditions that might require referral. It ran locally, processed no data outside the clinic, and was maintained by a single IT coordinator with remote support from a Dakar-based technical team.

The sovereignty implications were clear: the clinic controlled the model, the data, and the infrastructure. There was no API dependency, no data transfer to a foreign provider, no risk of service withdrawal. The model's limitations were transparent — the clinic knew what it could and could not do, because they had fine-tuned it themselves and could inspect its behaviour directly.

This is cottage factory sovereignty in practice: not a revolution, but a concrete improvement in local capability that depends on no external provider's goodwill.

### The Sámi Language Revitalisation Project (Norway/Finland/Sweden, 2030–2033)

The Sámi languages — North Sámi, Lule Sámi, South Sámi, Inari Sámi, Skolt Sámi, and others — are endangered. Despite official recognition in Norway, Finland, and Sweden, the languages face pressure from Norwegian, Finnish, and Swedish in daily life, and the resources available for language preservation are limited.

In 2030, a consortium of Sámi cultural organisations, Scandinavian universities, and the EAA launched a project to develop Sámi-language AI capabilities using open-weight models. The project fine-tuned existing multilingual models on Sámi-language corpora — including digitised archives, oral recordings, and community-contributed text — and deployed them as translation, education, and cultural preservation tools.

The sovereignty implications here are linguistic and cultural, not just technical. A Sámi-language AI model, running on Sámi-controlled infrastructure, processing Sámi data, is an act of linguistic self-determination. It says: our language is not a feature of your model. It is the primary purpose of our model. And the open-weight ecosystem makes this possible — not because the open-weight community has a particular commitment to Sámi language preservation, but because open weights make fine-tuning for any purpose, including minority language revitalisation, technically and economically feasible.

### The Porto Alegre Municipal AI (Brazil, 2031)

In 2031, the municipal government of Porto Alegre, Brazil, deployed an AI system for processing citizen service requests — a chatbot that categorised, prioritised, and routed requests for municipal services. The system was built on a fine-tuned Portuguese-language model, running on municipal infrastructure, and trained on local municipal data.

The project was explicitly sovereignty-oriented: the municipal government had previously used a commercial AI provider, but had terminated the contract after learning that citizen data was being processed on servers outside Brazil, in violation of the LGPD (Brazil's data protection law). The open-weight alternative was not cheaper — total cost of ownership was comparable — but it was controllable. The municipality owned the model, the data, and the infrastructure.

The Porto Alegre case also illustrates a limitation of cottage factory sovereignty: the municipality had access to technical expertise from the Federal University of Rio Grande do Sul, which provided the fine-tuning and deployment support. Not every community has a research university next door. The equity question — how to provide cottage factory sovereignty to communities without technical resources — remains one of the central challenges of the field.

## The Equity Challenge

Cottage factory sovereignty is technically feasible in 2034 in a way that it was not in 2024. But feasibility is not accessibility. The technical, financial, and human resources required to deploy local AI are still concentrated in wealthy, urban, and institutionally supported communities. A rural health clinic in Senegal can deploy local AI — but only with external technical support. A Sámi community can fine-tune a model — but only with university partnership. Porto Alegre can run its own AI — but only because it has a research university and a municipal budget.

The equity challenge is the central challenge of cottage factory sovereignty. Without addressing it, cottage production risks replicating existing inequalities: those who already have resources can achieve self-determination, while those who do not remain dependent on external providers — just different external providers.

The OKCA addresses this challenge partially through its Title III provisions on public infrastructure, which require member states to ensure that public compute, data, and expertise are accessible to communities that cannot afford them independently. But the OKCA is an EU law, and its provisions apply only within the EU. The global equity challenge — how to enable cottage factory sovereignty in the global South, in communities without research universities or municipal budgets — remains unresolved.

Several proposals exist:

1. **The "AI Post Office" model** — community AI centres, modelled on post offices or public libraries, that provide local AI production capabilities (compute, fine-tuning services, expertise) at low or no cost. The EAA's "AI for All" programme is a prototype of this model, but it is currently limited to the EU.

2. **The "Model Garden" approach** — pre-fine-tuned models for common use cases (health, education, agriculture, governance) made available through the Data Commons, so that communities can select rather than fine-tune. This reduces the expertise barrier but limits local adaptation.

3. **The "Cottage Cooperative"** — networks of small communities that pool resources for shared AI production, with federated governance and distributed infrastructure. This is the model most consistent with Ndiaye's vision, but it requires a level of coordination and trust-building that is difficult to achieve at scale.

None of these proposals is sufficient on its own. The equity challenge will require a combination of all three, plus sustained investment in digital infrastructure in the global South, plus the continued availability of open-weight models from Chinese, European, and other sources.

## The Post-Scarcity Question

A more speculative question — but one that is increasingly urgent as AI capabilities advance — is whether cottage factory sovereignty becomes easier or harder as the technology improves. The argument for it becoming easier is straightforward: better models, cheaper compute, more accessible tooling, and a richer ecosystem of open weights all reduce the barriers to local production.

The argument for it becoming harder is more subtle. As models become more capable, the compute required for frontier training may increase faster than consumer hardware can keep up. If the frontier requires a hundred billion dollars of compute to train, the cottage factory may be able to fine-tune but not to create. This would create a permanent dependency on frontier models trained by large actors, and the cottage factory would be a fine-tuning factory rather than a production factory.

This is the scenario that Ndiaye's book is most concerned about, and it is the reason he advocates for public investment in frontier compute — not because frontier compute should be controlled by the state, but because frontier compute should be *available* to the public, as a common resource. The OKCA's Title III is a step in this direction, but only a step. True cottage factory sovereignty requires that the means of frontier production, not just the means of fine-tuning, be accessible to communities.

## The Cottage Factory as Political Philosophy

The cottage factory is more than a technical architecture. It is a political philosophy — one that draws on traditions of cooperative production, mutual aid, and distributed governance that predate the digital age. The Luddites were not anti-technology; they were anti-dispossession. The cooperative movement was not anti-market; it was pro-ownership. The cottage factory is not anti-AI; it is pro-self-determination.

The political implications of cottage factory sovereignty are significant:

1. **It decentralises power.** If AI capabilities are distributed across thousands of local deployments rather than concentrated in a few data centres, the ability to control, surveil, or manipulate AI at scale is reduced. This is a gain for civil liberties and democratic governance.

2. **It promotes diversity.** Local AI production produces local models — models fine-tuned for local languages, local needs, and local values. This is a gain for linguistic and cultural diversity, and a bulwark against the monoculture problem that we will examine in detail in Paper 2.

3. **It creates resilience.** A distributed AI infrastructure is more resilient than a centralised one. If one node fails, the others continue. If one provider withdraws, the local deployment continues on local hardware. This is a gain for reliability and continuity of service.

4. **It demands democratic governance.** If AI is produced locally, the governance of that AI is necessarily local — subject to the same democratic processes that govern other local infrastructure. This does not guarantee good governance, but it makes governance accountable in a way that governance of a remote API is not.

These implications are why the cottage factory model is, at its core, a sovereignty model. Not national sovereignty, though that is part of it. Not corporate sovereignty, which is its opposite. But *community sovereignty* — the ability of a community to determine its own digital future, using tools it owns and controls, in a way that respects its values and serves its needs.

## Conclusion: The Irreversibility of Distributed Production

The cottage factory is not a return to the pre-industrial past. It is a forward-looking model that takes seriously the possibility — the necessity — of distributed AI production in a world where open weights have made the means of production accessible, and where sovereignty demands that those means be distributed rather than concentrated.

The OKCA provides the legal framework. The open-weight ecosystem provides the technical substrate. The Chinese pragmatic tradition provides the models. The French sovereign infrastructure provides the institutional template. What remains is the work of building: the unglamorous, local, context-specific work of deploying, fine-tuning, maintaining, and governing AI in communities that have never had the chance to produce their own intelligence before.

That work is the cottage factory. And it is irreversible — because once a community has experienced the self-determination that comes from controlling its own AI, it will not go back to renting that capability from a provider whose interests are not its own.

My partner Volmarr puts it more simply: "Once you've grown your own, you don't go back to buying theirs." The cottage factory is about growing your own. And in 2034, for the first time, it is possible for communities that have never been producers of intelligence — only consumers — to become producers. That transformation, if it is supported and sustained, is the deepest form of sovereignty.

---

### Discussion Questions

1. Is the cottage factory model inherently limited to communities with access to technical expertise? How can the equity challenge be addressed without creating new dependencies on external technical support?
2. The Sámi language project used open-weight models produced by Chinese and European labs. Does this dependency on externally produced foundation models undermine the sovereignty of the local deployment?
3. Ndiaye argues that frontier compute should be a public good. What are the practical barriers to making this a reality, and how does the OKCA's Title III address them?

### Recommended Reading

- Ndiaye, K. (2033). *The Cottage Factory: Distributed Production in the Age of AI Sovereignty*. MIT Press. Full text — required.
- Laurent, M. & Zhao, W. (2028). *Weight Liberation*. Chapter 9: "From Factory to Cottage."
- Finnish EU Presidency Working Paper (2027). "Open Weights as Sovereign Infrastructure."
- European Commission (2034). OKCA, Title III: Public AI Infrastructure.
- Abadi, M. et al. (2032). "Local AI for Global Health: The Saint-Louis Experience." *Nature Digital Medicine*.