# Lecture 02: Corporate Enclosure — Attempts to Close What Was Open

*AI-7303: Open Weight Movements and Digital Sovereignty*
*Week 2 | Prepared by Runa Gridweaver Freyjasdottir*

---

## Introduction: The Second Enclosure

The first enclosure movement — the British Enclosure Acts of the 18th and 19th centuries — transformed common land into private property, displacing peasant communities and consolidating economic power in the hands of landowners. The historians taught us that enclosure was not a single event but a process: a series of legal, economic, and violent transformations that moved resources from the commons into the market, from the many to the few.

The second enclosure — the corporate enclosure of AI, 2025–2029 — followed the same logic with different means. It was not enacted by Parliament but by licence change, API deprecation, and the strategic manipulation of the definition of "open" itself. This lecture traces those attempts, their mechanisms, and their failures. The thesis is simple: **enclosure was attempted, and it failed — not because enclosure is impossible in principle, but because the material conditions of AI production in the 2020s made it unenforceable.**

## Phase One: The Licence Drift (2024–2025)

The most obvious form of corporate enclosure is licence drift — the gradual tightening of terms on previously open releases. This pattern was well-established in software: the term "open core" was coined to describe companies that offered a permissively licenced base product while keeping the commercially valuable extensions proprietary. MongoDB's SSPL, Elasticsearch's dual-licencing pivot, and HashiCorp's BSL transition were all documented cases.

In AI, licence drift took a different form because the "open" state was already ambiguous. Meta's Llama 2 Community Licence, released in July 2023, was the template: permissive for most users, but with a 700 million monthly active users threshold beyond which a commercial licence was required. This was enclosure by threshold — open for the small, closed for the significant.

The threshold mattered because it created a regulatory grey zone. A startup could use Llama 2 freely. A competitor at scale could not. The licence functioned as a competitive moat dressed in open-source clothing — a point that was not lost on the community, but which was difficult to articulate as "enclosure" when the weights were, technically, available for download.

In 2024, the drift accelerated. Stability AI, which had built its brand on the openness of Stable Diffusion, shifted its licensing model for SD3 to a "community" licence that restricted commercial use without explicit permission. The justification was sustainability — a legitimate concern for any organisation burning venture capital at the rate Stability was burning it. But the effect was enclosure: a resource that had been common was now conditioned.

The community response was swift and, in the long run, decisive. Forks appeared within hours. Fine-tuned versions of SD2.1 — the last truly permissively licenced release — proliferated on Hugging Face. The practical lesson was clear: **once weights are in the wild, enclosure of those specific weights is impossible.** You can enclose future releases. You cannot enclose past ones.

## Phase Two: API-First Enclosure (2025–2026)

The more sophisticated enclosure strategy was not licence drift but architecture drift — the movement from open model releases to API-only access. The logic was straightforward: you cannot enclose weights that have already been released, but you can stop releasing weights entirely and offer only API access to future, more capable models.

OpenAI had been API-first since GPT-4. Anthropic followed. Google's Gemini models were accessible primarily through API, with weight releases (Gemma) deliberately positioned as smaller, less capable "research" models. The pattern was: frontier capability behind API, open releases as loss leaders and goodwill generators.

This was enclosure by architecture. The weights existed — somewhere, on some server — but they were not distributed. Reproduction of the model's capabilities required either independent training (prohibitively expensive for most actors) or the development of a competitive model from scratch (which the open-weight community was increasingly capable of doing, as DeepSeek demonstrated).

The API-first model had an inherent vulnerability: it required the provider to maintain quality advantage over open alternatives. As long as the closed model was significantly better than any open alternative, the API had value. But if open models caught up — or, worse, surpassed — the API model became simply a convenience layer over a commodity. This is precisely what happened.

DeepSeek R1's release in January 2025 was the first crack. By late 2025, Qwen 2.5 and Llama 3.1 had both reached competitive performance with closed models on most benchmarks. The quality gap that API enclosure depended on was narrowing — not because closed models were getting worse, but because open models were getting better faster. The enclosure was being outcompeted, not outmanoeuvred.

## Phase Three: The "Safety" Enclosure (2025–2027)

The most insidious enclosure strategy was the invocation of safety. Beginning in earnest in 2025, several major AI labs began arguing — in policy briefings, Congressional testimony, and EU consultation responses — that open-weight models presented unacceptable safety risks because they could not be controlled after release. The argument had several variants:

1. **The misuse argument**: Open weights enable bad actors to fine-tune models for harmful purposes. Only a closed, API-mediated model can guarantee safety through output filtering.
2. **Thecapabilityargument**: As models become more capable, the risks of open release increase. There is some capability threshold beyond which open release is irresponsible.
3. **The regulatory argument**: Governments should require licensing or approval for the release of models above a certain capability threshold, effectively creating a regulatory enclosure.

Each of these arguments contained a kernel of truth. Misuse *is* a risk. Capability *does* create new dangers. Regulation *is* appropriate. But each argument also functioned as an enclosure mechanism — a way to reframe commercial self-interest as public safety concern.

The misuse argument, taken seriously, would also prohibit the internet, encryption, and chemistry textbooks. It is the argument of every censor in history: the people cannot be trusted with this knowledge. The capability argument requires some agreed-upon threshold of "dangerous capability" — which, despite years of effort, no one has been able to define in a way that does not either capture everything or capture nothing. And the regulatory argument, in practice, became a mechanism by which incumbent labs lobbied for barriers to entry that would prevent new competitors from reaching the market.

The safety enclosure was most effective in the EU, where the AI Act's provisions on foundation models were shaped in part by safety arguments from incumbent labs. The Act's requirements for "systemic risk" assessment and regulatory approval for high-impact models created a compliance burden that was trivial for Google and insurmountable for a university lab. This was enclosure by cost-shifting — making openness expensive enough to discourage it.

The counter-argument — made by the open-source community, by Chinese labs, and by the European open-weight advocates — was that safety through secrecy is not safety but obscurity. A model whose internals cannot be examined is a model whose failures cannot be anticipated. Red-teaming, the community argued, requires access. Auditing requires access. Safety research requires access. The closed model is not safer; it is merely less transparent about its dangers.

This argument did not win the policy war in 2025. But it won the *practice* war by 2027, as incident after incident demonstrated that closed models had safety failures at a comparable rate to open ones — they were just less visible. The "safety enclosure" collapsed under the weight of its own evidence.

## Phase Four: The Data Enclosure (2026–2028)

The most sustained enclosure attempt targeted not the models but the data. Starting in 2026, a wave of lawsuits — Getty Images v. Stability AI, NYT v. OpenAI, several class-action suits by authors and artists — created legal uncertainty around the training data that fed open models. The enclosure strategy here was legal, not technical: make the data inputs of open models legally toxic, and the models themselves become legally toxic.

This was the most credible enclosure attempt because it attacked the one thing that the pragmatic tradition could not easily sidestep. Chinese models had been trained on data that included copyrighted material — everyone's models had. If the legal precedent established that training on copyrighted material without a licence was infringement, then every model — open or closed — was potentially liable.

The response from the open-weight community took two forms. The first was the development of "clean data" pipelines — training data composed entirely of public-domain, openly licenced, or synthetically generated material. This was technically challenging but not impossible, and by 2028, several credible models had been trained on demonstrably clean data (notably the EU-funded Aurora project and the entirely synthetic OpenMath datasets).

The second response was legislative: the argument that training on publicly available data constituted fair use, transformative use, or a legally protected research activity. This argument won in several jurisdictions, lost in others, and remains contested. But the key point is that the data enclosure strategy *required winning in every jurisdiction simultaneously* — a legal equivalent of the security problem of defending all points while the attacker need only breach one. China, notably, was never going to enforce Western copyright norms on its open-weight releases.

## Phase Five: The Hardware Enclosure (2027–2029)

The final enclosure attempt targeted compute infrastructure. Nvidia's dominance of GPU supply, combined with US export controls on advanced chips to China, created a situation in which the physical means of production — the chips on which models are trained — could be controlled. If you cannot enclose the weights, enclose the machines on which they are made.

The CHIPS Act in the US, the EU Chips Act, and the escalating US export controls on AI chips to China were all, in different ways, attempts to control the compute supply. The US export controls were explicitly an enclosure strategy: deny Chinese labs access to frontier chips, and their models will fall behind, making the closed models of US labs comparatively more valuable.

This strategy failed for three reasons. First, Chinese chip design advanced rapidly — the Huawei Ascend 910B, released in late 2025, was competitive with the A100 on many workloads. Second, algorithmic efficiency gains in training reduced the compute advantage of having the best chips. DeepSeek's training efficiency gains were a direct response to compute constraints, and they worked. Third, the global chip supply is too distributed to control: chips manufactured in the US, fabbed in Taiwan, assembled in China, and shipped globally through a supply chain that defies unilateral control.

The hardware enclosure strategy continues in attenuated form — export controls still exist, chip allocation is still politicised — but as of 2034, it has clearly failed to prevent the emergence of world-class open-weight models from multiple sovereign sources.

## Why Enclosure Failed

Corporate enclosure of AI failed for the same reason the enclosure of farmland succeeded: the material conditions were wrong. Farmland is rivalrous — my field cannot also be your field. Weights are non-rivalrous — my download does not diminish yours. The economics of digital goods are fundamentally different from the economics of physical goods, and every enclosure strategy that assumed they were the same ran aground on this fact.

But more specifically, enclosure failed because:

1. **Once released, weights cannot be unreleased.** The fork of Stable Diffusion after the SD3 licence change demonstrated this conclusively. The community had the weights. The community kept the weights. The community built on the weights. The licensor's subsequent enclosure was irrelevant to the already-released version.
2. **Open alternatives outcompete closed ones.** DeepSeek, Qwen, Llama (once genuinely opened), and the European sovereign stack all offered competitive capability without enclosure terms. When a free alternative exists that is good enough, the economic pressure toward openness is relentless.
3. **Sovereignty demands openness.** As we will explore in Lectures 3 and 4, sovereign AI projects in China, France, and elsewhere *required* open weights as a matter of policy. Enclosure was incompatible with the sovereignty imperative, and sovereignty had more political force than corporate lobbying.
4. **The safety argument was empirically wrong.** Closed models failed at comparable rates to open ones. The safety enclosure was a thin cover for commercial interest, and the evidence increasingly revealed it as such.

## Conclusion: Enclosure as a Feature of the Transition

The corporate enclosure attempts of 2025–2029 were not aberrations. They were the predictable response of incumbent power to the democratisation of a strategic resource. Like the British Enclosure Acts, they were driven by economic interest dressed in moral language. Unlike the British Enclosure Acts, they failed — because the resource they sought to enclose was, by its nature, incapable of being fenced.

The lesson for this course is not that enclosure is impossible in principle. It is that enclosure of digital goods requires a level of control that no single actor, and no coalition of actors, has been able to achieve in the 2020s. This may change. The OKCA of 2034 is, in part, a recognition that the current openness is contingent — that it persists because of the material conditions of the moment, and that those conditions must be actively maintained.

---

### Discussion Questions

1. The "safety enclosure" argument was made in good faith by many researchers who genuinely feared misuse. Does the fact that it was also strategically convenient for corporations invalidate the concern?
2. If weights are non-rivalrous, why do corporations continue to try to enclose them? What would a successful enclosure strategy look like?
3. The hardware enclosure (export controls) has not prevented Chinese model development but has slowed it. Is "slowing" a form of successful enclosure, or merely a delay?

### Recommended Reading

- Laurent, M. & Zhao, W. (2028). *Weight Liberation*. Chapters 3–5: "The Enclosure Attempts."
- Blizzard, M. et al. (2026). *The Open Source AI Definition: A Post-Mortem*. Chapter 7: "Safety as Enclosure."
- Ndiaye, K. (2033). *The Cottage Factory*. Chapter 2: "Why Enclosure Fails."
- Webb, A. (2027). "Data Enclosure and the Copyright Paradox." *Journal of AI Law and Policy*, 4(2).
- US Department of Commerce, Bureau of Industry and Security (2025, 2027). Export Control Updates on Advanced Computing Chips.