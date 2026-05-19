# Lecture 05: The Open Knowledge Commons Act — The 2034 OKCA: Full Text Analysis

*AI-7303: Open Weight Movements and Digital Sovereignty*
*Week 5 | Prepared by Runa Gridweaver Freyjasdattir*

---

## Introduction: Legislation as Irreversibility

The Open Knowledge Commons Act, passed by the European Parliament on 14 March 2034 and entered into force on 1 January 2035, is the most significant piece of AI legislation since the EU AI Act of 2024. It is also the most significant vindication of the open-weight movement. Where the AI Act regulated AI *systems*, the OKCA regulates AI *infrastructure* — and it regulates it in the direction of openness.

This lecture provides a close reading of the OKCA, analysing its structure, its key provisions, its legislative history, and its likely impact. The overarching argument is that the OKCA does not create openness ex nihilo; it codifies an irreversibility that was already emerging from the material conditions of AI production — the conditions we have traced in Lectures 1 through 4. The OKCA makes open weights a matter of law not because law is the primary driver, but because law is the mechanism by which an existing trend is made durable.

## Legislative History: From Finnish Paper to European Law

The OKCA's legislative history began, as we noted in Lecture 1, with the Finnish Presidency working paper of March 2027, "Open Weights as Sovereign Infrastructure." This paper made three arguments that would become the intellectual core of the OKCA:

1. **Dependency is a security risk.** EU member states that depend on closed AI providers for critical infrastructure are exposed to supply risk, pricing risk, and regulatory risk — the provider can withdraw the service, increase the price, or change the terms at any time.
2. **Open weights are the only sovereign option.** Only open-weight models — models whose weights are available for local deployment, modification, and audit — can provide the level of control that sovereignty demands.
3. **The market alone will not provide this.** The economic incentives of dominant AI providers favour closed models and API-based access. Public intervention is necessary to ensure that open alternatives exist and are viable.

The Finnish paper was not legislation — it was a policy analysis. But it was taken up by the European Parliament's Committee on Industry, Research, and Energy (ITRE), which commissioned a formal impact assessment in late 2027. The impact assessment, published in June 2028, confirmed the Finnish paper's analysis and added two further arguments:

4. **Open weights promote competition.** A market dominated by a small number of closed providers is less competitive, less innovative, and more prone to rent-seeking than a market in which open alternatives exist.
5. **Open weights enable regulation.** Closed models cannot be effectively audited, red-teamed, or modified to comply with local regulations. Only open models can be adapted to the regulatory requirements of the jurisdictions in which they are deployed.

The European Commission's draft proposal, published in September 2031, was substantially shaped by these five arguments. The proposal went through the ordinary legislative procedure — Commission proposal, Parliament position, Council negotiation — and was adopted in March 2034 with broad support from all major political groups. The main opposition came from the European People's Party, which argued (in line with US-based lobbying) that the Act would reduce European competitiveness, and from the Greens, who argued (somewhat paradoxically) that the Act did not go far enough in mandating training data disclosure.

The final text represents a compromise — but a compromise that tilts decisively toward openness.

## Structure of the OKCA

The OKCA consists of 94 articles organised into seven titles:

- **Title I: General Provisions** (Articles 1–8) — Scope, definitions, and general principles
- **Title II: Open Weight Requirements** (Articles 9–28) — Requirements for open-weight availability
- **Title III: Public AI Infrastructure** (Articles 29–45) — EU and member state obligations
- **Title IV: Data Commons** (Articles 46–60) — Training data disclosure and commons provisions
- **Title V: Regulatory Provisions** (Articles 61–72) — Enforcement, penalties, and remedies
- **Title VI: International Cooperation** (Articles 73–85) — Relations with third countries
- **Title VII: Final Provisions** (Articles 86–94) — Implementation, review, and sunset clauses

We will analyse the most significant provisions in each title.

## Title I: General Provisions — The Definitions That Matter

Article 2 contains the OKCA's definition of "open weight model," which drew heavily on the OSI's OSD-AI (discussed in Lecture 1) but made several crucial modifications:

> **"Open weight model" means an AI model whose model weights, inference code, and sufficient documentation to enable modification and reconstruction are made available under terms that permit:**
> **(a) use for any purpose, including commercial purposes, without restriction;**
> **(b) study of the model's functioning, including the right to inspect and analyse the model's behaviour, architecture, and training methodology;**
> **(c) modification and adaptation of the model, including the right to create derivative models, without approval from the original creator;**
> **(d) redistribution of the model and its derivatives, under terms that maintain these freedoms.**

Note what is *not* required: full training data disclosure. The OKCA, like the OSD-AI, requires "sufficient documentation to enable modification and reconstruction" — but not the training data itself. This was the most debated provision, and the compromise reflects the practical reality that training data disclosure remains legally problematic for most models.

However, Article 2 also introduces a concept not present in the OSD-AI: the concept of a "Qualified Open Weight Model" (QOWM):

> **"Qualified Open Weight Model" means an Open Weight Model that additionally discloses:**
> **(a) the composition, provenance, and processing methodology of its training data to the extent necessary for a skilled person to evaluate the model's biases, limitations, and potential harms;**
> **(b) the model's evaluation results on standard benchmarks, including benchmarks relevant to the languages and cultural contexts of the EU;**
> **(c) a description of known limitations and failure modes.**

The QOWM concept creates a two-tier system within the OKCA: open-weight models (which meet the basic requirements) and qualified open-weight models (which meet enhanced transparency requirements). This structure incentivises transparency without making it a precondition for openness — a pragmatic compromise that reflects the Chinese pragmatic tradition's influence on European thinking.

## Title II: Open Weight Requirements — The Core Mandate

Articles 9–28 contain the OKCA's core mandate: **public sector bodies in the EU must, whenever practicable, prefer open-weight models over closed models for AI deployment.**

Article 12 specifies the preference hierarchy:

> **1. When procuring or deploying AI systems, public sector bodies shall give preference to Qualified Open Weight Models.**
> **2. Where no Qualified Open Weight Model is available that meets the functional requirements of the deployment, public sector bodies shall give preference to Open Weight Models.**
> **3. Where no Open Weight Model is available that meets the functional requirements of the deployment, public sector bodies may procure or deploy closed-weight models, provided that:**
> **(a) a review is conducted at least annually to determine whether an open-weight alternative has become available;**
> **(b) the closed-weight model is subject to source code escrow provisions that enable public sector access in the event of provider failure or withdrawal;**
> **(c) the deployment does not create a dependency that would compromise the public sector body's ability to perform its functions independently.**

This hierarchy is the OKCA's most significant provision. It does not ban closed models — that would be both impractical and, given the state of technology in 2034, premature. But it creates a structural preference for open models that is backed by public procurement power. Given that the EU public sector is one of the largest AI consumers in the world, this preference has significant market effects.

Article 17 contains a provision that was hotly contested during negotiation: the "escrow and access" requirement for closed models deployed in the public sector. This provision requires closed-model providers to place their model weights in escrow with the European AI Agency, to be released to the deploying public sector body only in specified circumstances (provider bankruptcy, withdrawal from the EU market, or national emergency). This was the provision that drew the strongest opposition from US-based AI companies, who argued that it constituted a forced transfer of intellectual property. The EU responded that it was a necessary safeguard for public sector continuity — and that the comparison to IP seizure was inapt because the weights would be released only in exigent circumstances, not as a matter of course.

## Title III: Public AI Infrastructure — The Sovereign Stack

Title III is where the OKCA moves from preference to investment. Articles 29–45 require the EU and member states to develop and maintain public AI infrastructure, including:

- **Public compute clusters** — accessible to EU researchers, companies, and public bodies at below-market rates, with priority for open-weight projects
- **Data commons** — curated, legally clean datasets available for AI training, incorporating the multilingual data that the RDS had begun collecting
- **Model repositories** — the expansion of the EAA's model repository into a full public library of evaluated, approved open-weight models
- **Talent pipelines** — funding for AI education, repatriation programmes for EU researchers abroad, and retention programmes for domestic talent

Article 33 is particularly significant: it mandates that EU member states must, within five years of the Act's entry into force, ensure that public compute capacity is sufficient to train and fine-tune open-weight models at a scale competitive with the global frontier. This is, in effect, a mandate for sovereign compute infrastructure — and it was directly informed by the French experience with the Jean Zay and Turing clusters.

Title III also creates the "Open Knowledge Commons" — the institution from which the Act takes its name. The Open Knowledge Commons (OKC) is an EU body tasked with maintaining and developing the public AI infrastructure described above. It is governed by a board with representatives from each member state, from the European Commission, and from the open-weight community (including representatives from Mistral, DeepSeek's European subsidiary, and academic institutions).

## Title IV: Data Commons — The Unfinished Business

Title IV addresses the question that the OSD-AI had punted on: training data. Articles 46–60 establish the European AI Data Commons, a public dataset for AI training that is:

- Curated for legal clarity (all data licenced or in the public domain)
- Multilingual (covering all 24 official EU languages plus regional and minority languages)
- Diverse (including text, code, images, audio, and structured data)
- Continuously updated (with a rolling update cycle and community contributions)

The Data Commons is not a requirement for open-weight models — that is, models are not required to train on it. But models that do train on the Data Commons and meet the transparency requirements of Article 2 are automatically designated as Qualified Open Weight Models, creating an incentive for alignment between the Data Commons and model development.

Title IV also addresses the copyright question that had haunted the open-weight movement since 2024. Article 52 establishes a limited fair-use-style exception for AI training on publicly available data, provided that:

- The training does not substitute for the original work in its market
- The trained model does not reproduce substantial portions of training data in its outputs
- The training data is documented and disclosed to the extent required for Qualified Open Weight Model status

This provision was the most controversial in the entire Act. Rights holders argued that it eviscerated copyright; AI developers argued that it didn't go far enough. The final text was a compromise that satisfied neither side completely — which is usually a sign that it's approximately right.

## Title V: Regulatory Provisions — Enforcement

Title V contains the OKCA's enforcement mechanisms. The most significant is Article 68, which gives the European AI Agency the power to conduct "sovereignty audits" of public sector AI deployments. These audits assess whether the deployment meets the preference hierarchy of Article 12, whether closed-model deployments have appropriate escrow arrangements, and whether the deployment creates unacceptable dependencies on foreign providers.

Article 70 creates a private right of action for EU citizens who are harmed by public sector AI deployments that violate the OKCA's preference hierarchy. This is a novel provision — it turns the preference for open models from a policy guideline into an enforceable right — and its consequences remain to be seen.

## Title VI: International Cooperation

Title VI addresses the OKCA's relationship with third countries. Article 75 establishes a "reciprocity" principle: the OKCA's preference hierarchy applies only to models from countries that offer reciprocal market access to EU open-weight models. In practice, this means that EU public sector preference for open models applies equally to EU models, US models (which meet the reciprocity requirement), and Chinese models (which also meet the reciprocity requirement, as Chinese open-weight models are available without restriction to EU entities).

Article 78 contains a provision that was controversial at the time but has since proven prescient: it authorises the European Commission to negotiate mutual recognition agreements with third countries, under which the parties agree to recognise each other's open-weight designations and to coordinate on training data standards. As of 2039, mutual recognition agreements have been signed with Canada, Japan, South Korea, Brazil, and India. Negotiations with China are ongoing but have stalled over the issue of data provenance verification.

## Critical Analysis: Strengths and Weaknesses

The OKCA is, by any measure, a landmark piece of legislation. It is the first law in the world to codify a preference for open-weight models in public sector AI deployment, to mandate sovereign compute infrastructure, and to establish a public data commons for AI training. But it has weaknesses:

1. **The training data question remains unresolved.** The "sufficient documentation" standard of Article 2 is vague, and the Data Commons, while useful, is not a substitute for full training data transparency. Models trained on the Data Commons will be well-documented, but models trained on other data may not be.

2. **The enforcement mechanisms are untested.** The sovereignty audit and private right of action are novel, and it is unclear whether they will be effective in practice. The EAA has limited resources, and the private right of action depends on citizens being aware of and willing to litigate OKCA violations.

3. **The relationship with the AI Act creates regulatory complexity.** The OKCA and the AI Act impose overlapping but not identical obligations on AI deployers. Navigating both regulatory frameworks is a compliance burden, particularly for smaller organisations.

4. **The two-tier system creates incentives for gamesmanship.** The distinction between "open weight" and "qualified open weight" models invites providers to seek the designation that most benefits them, rather than the designation that most benefits the public. The QOWM's enhanced transparency requirements may become a barrier for smaller providers who cannot afford the documentation burden.

5. **The escrow provision may deter innovation.** Requiring closed-model providers to place weights in escrow may discourage some providers from entering the EU market, reducing competition and potentially slowing the development of the frontier models that drive progress.

These weaknesses are real, and they will need to be addressed in the OKCA's first scheduled review in 2039. But they do not diminish the Act's fundamental achievement: the codification of open weights as a matter of public policy, rather than private charity or market accident.

## Conclusion: From Trend to Law

The OKCA represents the moment at which the open-weight movement transitioned from a trend to a legal commitment. The trend — the growing availability and capability of open models, the increasing recognition of sovereignty concerns, the failure of corporate enclosure — was already irreversible. The OKCA made it *institutionally* irreversible, by creating legal obligations, public investments, and enforcement mechanisms that would persist even if the market conditions changed.

This is the significance of the OKCA, and it is why this course devotes an entire lecture to it. The open-weight movement did not need the OKCA to exist — Chinese and European models would have continued to be released openly regardless. But the OKCA ensured that the institutional infrastructure of openness — compute, data, talent, and legal preference — would exist even if market incentives shifted. It made openness not just the path of least resistance, but the path prescribed by law.

That is what irreversibility looks like in practice: not the absence of opposition, but the presence of structures that make opposition futile.

---

### Discussion Questions

1. The OKCA's two-tier system (open weight vs. qualified open weight) has been criticised by the FSF as creating a "good enough" category that lets providers avoid full transparency. Is this a valid concern, or is the QOWM a pragmatic improvement on the status quo?
2. Article 70's private right of action is unprecedented in AI regulation. What are the likely consequences — both positive and negative — of allowing citizens to sue over OKCA violations?
3. The OKCA's reciprocity principle treats Chinese open-weight models equally with EU models. Does this create a sovereignty risk, or does it strengthen the open ecosystem?

### Recommended Reading

- European Commission (2034). *Open Knowledge Commons Act: Legislative Text*. EU Publications Office. Full text — required.
- European Parliament, ITRE Committee (2028). *Impact Assessment on Open Weights and Sovereign AI Infrastructure*. EU Publications Office.
- Laurent, M. & Zhao, W. (2028). *Weight Liberation*. Chapter 8: "From Policy to Law."
- Ndiaye, K. (2033). *The Cottage Factory*. Chapter 6: "The Law as Infrastructure."
- Finnish EU Presidency Working Paper (2027). "Open Weights as Sovereign Infrastructure."