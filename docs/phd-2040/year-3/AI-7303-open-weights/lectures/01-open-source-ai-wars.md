# Lecture 01: The Open Source AI Wars — The Definition Wars 2024–2028

*AI-7303: Open Weight Movements and Digital Sovereignty*
*Week 1 | Prepared by Runa Gridweaver Freyjasdottir*

---

## Prologue: A War Over Words

In 2024, if you told someone in the ML community that within four years the definition of "open source" as applied to AI would be the subject of parliamentary inquiries, trade negotiations, and at least one formal complaint to the World Trade Organisation, they would have looked at you with the patient concern usually reserved for people who claim to have been professionally wronged by a crossword puzzle. And yet. The definition wars of 2024–2028 were not a pedantic exercise. They were the terrain upon which the next decade of AI governance was fought. The question was simple: **what counts as "open" when the thing being opened is a neural network?** The answers were anything but.

## The Pre-War Landscape

To understand the definition wars, you have to understand the landscape that produced them. By early 2024, the term "open source AI" had become a marketing category, a legal grey zone, and a cultural fault line — all at once.

Meta had released Llama 2 under a custom licence that allowed commercial use with restrictions on scale. Stability AI had released Stable Diffusion under a licence that was open-ish for non-commercial use and conditional for commercial. Hugging Face was functioning as a de facto public library of models whose legal status varied wildly from item to item. And Google, Microsoft, and Apple were watching all of this with the calm concern of landlords watching squatters build a commune on their tax-deducted land.

The Open Source Initiative (OSI), the body that had maintained the Open Source Definition since 1998, had not yet ruled on AI. Their definition — which governed software — required four freedoms: to run, study, redistribute, and modify. But neural networks are not software in the traditional sense. You can redistribute the weights, yes. You can modify them — technically. But can you *study* them? The interpretability researchers would laugh kindly at that question. Can you *run* them for any purpose? The licence terms attached to most "open" models said no, actually, you cannot run them to compete with us, you cannot run them above a certain scale, you cannot run them in certain jurisdictions.

The gap between what "open source" meant in software and what it had come to mean in AI was wide enough to drive a legislative agenda through. And several people did.

## The OSD-AI Process Begins (April 2024)

In April 2024, the OSI announced a formal process to define "Open Source AI." The Open Source Definition for AI (OSD-AI) working group was constituted with representatives from industry, academia, and civil society. Their mandate: produce a definition that could serve as a standard, similar to how the original OSD had become the gold standard for software freedom.

The working group's composition itself was a political statement. It included representatives from Meta (who had commercial reasons to want a definition that validated Llama's licence), from Hugging Face (who had infrastructure reasons to want clarity), from the Software Freedom Conservancy (who had ideological reasons to want rigour), and from several civil society organisations (who had justice reasons to want enforceability). The first meeting, by all accounts, was genteel. The third was not.

The central fault line emerged early: **should "open source AI" require the release of training data?**

The case for requiring training data was intellectually compelling. A neural network is, in a real sense, a compressed representation of its training data. If you have the weights but not the data, you have the output of a process you cannot reproduce — you have a sausage, not a recipe. The Free Software Foundation's position, echoed by several academic members of the working group, was that without training data, you cannot exercise the freedom to study or the freedom to modify in any meaningful sense. You can fine-tune, yes. You can iterate. But you cannot understand — and you cannot rebuild.

The case against requiring training data was pragmatic and, in many ways, more honest than its proponents liked to admit. Training data for large models includes copyrighted material, personal data, and data subject to contractual restrictions. Requiring its release would make it impossible for any company to release an "open source AI" model without either massive legal risk or an entirely synthetic training pipeline — which, in 2024, did not exist at the necessary scale. The requirement, argued Meta and others, would define "open source AI" into non-existence for any model trained on the actual internet.

This was not a trivial objection. The OSI's own founder, Bruce Perens, had argued in the software context that the open source definition should describe the *ideal*, not the *currently convenient*. But Perens was working with compilers and libraries, not with models trained on three terabytes of copyrighted text scraped without consent. The terrain had changed. The definition needed to change with it — or so the argument went.

## The Corporate Lobbying Escalates (Late 2024)

By late 2024, what had begun as a definitional exercise had become a lobbying war. Meta hired two former OSI board members as consultants. Google's DeepMind division published a position paper arguing that "open source AI" should mean "weights available under a permissive licence regardless of training data provenance" — a definition that would validate their own Gemma releases and invalidate the demands of data transparency advocates. Microsoft, characteristically, argued both sides simultaneously — supporting open definitions in public testimony while their IP lawyers filed amicus briefs favouring restrictive interpretations.

The most consequential corporate intervention came from a coalition that would later be named "Open Defined" — a lobbying group funded by Meta, Google, Microsoft, and Amazon, whose explicit purpose was to shape the OSD-AI in a direction that permitted their current release practices to qualify as "open source AI." Their position paper, published in January 2025, argued that:

1. Training data should not be required for a model to be "open source," because training data is a *production input*, not a *component* of the final product.
2. Usage restrictions (e.g., "you may not use this model to compete with the licensor") should be permitted in "open source AI" licences, because AI models present unique safety risks that software does not.
3. The definition should be *forward-looking*, accommodating advances in training that might make data less relevant over time.

Each of these positions had a surface plausibility. Each also had the effect of defining "open source AI" down to the point where it meant almost nothing at all. Data is not a component? Tell that to the researchers trying to reproduce a result. Usage restrictions are safety measures? Tell that to the competitors who discover the restrictions apply only to them. Forward-looking? It is always forward-looking to define the present inconvenient requirement away.

## The DeepSeek Effect (January 2025)

And then, in January 2025, DeepSeek released R1.

The DeepSeek R1 model was not the first Chinese open-weight model, but it was the one that made the definition wars irrelevant in the way that matters most: it worked. It was competitive with the best closed models of its era, released under a permissive licence, with training details disclosed to a degree that embarrassed most Western labs. It did not have full training data release — but it had enough detail to enable meaningful reproduction and modification.

DeepSeek's release did not resolve the definition wars. It *sidestepped* them. By demonstrating that a world-class model could be released with substantial openness and no catastrophic competitive consequence, it made the "we can't do this because we'll lose our edge" argument look, at best, alarmist. The model's existence was an argument by example — the most effective kind.

More importantly, DeepSeek's release shifted the conversation from "what should open mean?" to "why can't you do what they just did?" This was not a comfortable question for Meta, whose Llama models had steadily moved toward more permissive licensing but still carried usage restrictions. It was even less comfortable for Google and Microsoft, whose "open" models were deliberately hamstrung in capability while the closed frontier was reserved for their commercial products.

## The OSD-AI Definition Released (October 2025)

The OSI released its final Open Source AI Definition in October 2025, after 18 months of controversy. The definition, in its final form, required:

- **Access to the complete model** — weights, code, and sufficient documentation to enable modification and reconstruction.
- **No restriction on use** — including commercial use, competitive use, and use in any field of endeavour.
- **No restriction on modification** — including the right to create derivative models without approval from the original creator.
- **Training data disclosure** — but only "sufficient information about the training data to enable a skilled person to rebuild an equivalent model," not the data itself.

This last point was the compromise that had cost the most blood. It was, depending on your perspective, either a pragmatic acknowledgment of legal reality or a capitulation to corporate pressure. The FSF denounced it as insufficient. Meta praised it as reasonable. DeepSeek's team, who had not been involved in the process, released a statement that was essentially the Chinese pragmatic tradition rendered in diplomatic English: "We are glad a definition exists. We look forward to seeing whether it is useful."

The definition was useful, as it turned out, but not in the way its authors intended. It became a *floor*, not a ceiling — a minimum standard that legitimate open-weight releases were expected to exceed. By 2027, any model that merely met the OSD-AI minimum was considered "compliant," not "open." The community standard had moved beyond the formal definition.

## The Aftermath: 2026–2028

The period from 2026 to 2028 saw the definition wars settle into a three-tier ontology that persists to this writing:

1. **Open Weight** — weights available under a permissive licence, with no usage restrictions. Training data may or may not be disclosed. This is the category that DeepSeek, Qwen, and most Chinese models occupy. It is the pragmatic baseline.
2. **Open Source AI (OSI-compliant)** — meets the OSD-AI standard. Includes sufficient documentation to enable reconstruction. No usage restrictions. This is the category that Mistral and several European models aim for.
3. **Weight-Available** — weights released under a licence that includes usage restrictions, field-of-use restrictions, or non-compete clauses. This is the category that Llama occupied until 2027, when Meta finally removed the last restrictions under competitive pressure from genuinely open alternatives.

The shift from "open source AI" as a marketing term to this three-tier system was not driven by definition alone. It was driven by the material reality of Chinese open-weight releases, which made restriction-laden licences commercially non-viable. When your competitor is releasing a better model with fewer restrictions, your "open-ish" licence is not a moat — it is a confession.

## The Finnish Presidency Intervention (March 2027)

A lesser-known but strategically important moment: in March 2027, during Finland's presidency of the EU Council, a working paper was circulated that proposed that EU procurement policy should favour OSI-compliant models and actively disadvantage weight-available models. The paper was authored by a team that included two former Mistral engineers and a Finnish digital infrastructure scholar. It argued that EU sovereignty required open weights — not because open was ideologically pure, but because closed or restricted models created dependency on foreign providers whose terms could change at any time.

This paper did not become policy immediately. But it became the intellectual foundation for the European AI Agency's 2030 mandate, which in turn fed into the OKCA. The definition wars had produced something durable: the understanding that *openness is a sovereignty issue, not just a freedom issue.*

## Conclusion: The War That Ended Because It Became Irrelevant

The definition wars of 2024–2028 are historically significant not because they produced a perfect definition, but because they cleared the ground for a more important realisation: the question is not whether AI should be open, but whether *any polity that depends on closed AI can be sovereign.* The definition was a proxy for that question. The pragmatic tradition — exemplified by DeepSeek and the Chinese open-weight movement — answered the question by ignoring the proxy entirely and simply releasing the weights.

In the lectures that follow, we will trace the consequences of this realisation through corporate enclosure attempts, sovereign infrastructure projects, and ultimately the codification of open weights as a matter of public law.

---

### Discussion Questions

1. Was the OSI right to compromise on training data release? Would a strict requirement have advanced or retarded the cause of open AI?
2. The three-tier ontology (open weight, open source AI, weight-available) has no formal enforcement mechanism. Is this a problem, or is community enforcement sufficient?
3. DeepSeek R1's release was a geopolitical event as much as a technical one. Does the pragmatic tradition's refusal to engage with Western definitional frameworks represent a strength or a blind spot?

### Recommended Reading

- Blizzard, M. et al. (2026). *The Open Source AI Definition: A Post-Mortem*. OSIA Press. Chapters 1–4.
- OSI (2025). *Open Source AI Definition, Version 1.0*. Available at opensource.org/ai.
- Cheng, L. (2031). *Best Value, No Moralising*. Chapter 2: "The Definition Wars as Western Theatre."
- DeepSeek Team (2025). "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs." *arXiv preprint*.
- Finnish EU Presidency Working Paper (2027). "Open Weights as Sovereign Infrastructure." Internal document, subsequently published by the European AI Agency.