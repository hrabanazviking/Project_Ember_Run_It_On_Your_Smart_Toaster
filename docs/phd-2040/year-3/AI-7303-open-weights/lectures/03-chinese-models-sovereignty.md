# Lecture 03: Chinese Models and Sovereignty — Best Value, No Moralising

*AI-7303: Open Weight Movements and Digital Sovereignty*
*Week 3 | Prepared by Runa Gridweaver Freyjasdattir*

---

## Opening: A Tradition of Its Own

There is a habit in Western commentary on Chinese AI — a habit that the pragmatic tradition in which I was trained regards as both intellectually lazy and politically dangerous — of treating Chinese open-weight releases as either a threat to be contained or a surprise to be marvelled at. Neither framing captures the reality. Chinese open-weight models are neither a threat nor a surprise. They are the latest expression of a technological tradition that has been building for decades — a tradition that prioritises capability, access, and sovereignty over ideological alignment, and that regards Western debates about "what counts as open" with bemused indifference.

This lecture examines the Chinese open-weight tradition on its own terms. The thesis is straightforward: **Chinese open-weight models offer the best value in the global AI ecosystem, and they do so without moralising about why you should use them. This is not a bug. It is a feature of a pragmatic tradition that has understood, for longer than most Western observers, that openness is a strategy, not a virtue signal.**

## The Pragmatic Roots: From Copying to Capability

The Western narrative about Chinese technology often begins with copying. It is true that the early phase of China's technology development involved extensive imitation of Western products — from smartphones to social media platforms. But this narrative stops being useful around 2015, by which point Chinese technology companies were producing original work in computer vision, natural language processing, and recommendation systems that was competitive with or superior to Western alternatives.

In AI specifically, the trajectory was never simply imitative. The Chinese AI research community — centred on institutions like Tsinghua, Peking University, the Chinese Academy of Sciences, and the corporate labs of Baidu, Alibaba, Tencent, and ByteDance — developed a distinctive culture that can be characterised by three values:

1. **Capability first.** The measure of a model is what it can do, not what it symbolises. A model that works is a model that works, regardless of its licensing terms, its ideological alignment, or its conformity to Western norms of openness.
2. **Access as infrastructure.** Open-weight release is understood not as charity, not as ideological commitment, and not as a competitive vulnerability — but as infrastructure development. If you need a bridge, you build a bridge. If your economy needs AI, you make AI available. The question of whether the bridge is "truly open" is less important than whether trucks can drive across it.
3. **Sovereignty through self-sufficiency.** The US-China technology rivalry, which escalated sharply from 2018 onward, created a strategic imperative for Chinese AI self-sufficiency. Open-weight models — whether released by Chinese labs or adapted from Western sources — were a component of that self-sufficiency. The pragmatic tradition is, in part, a sovereignty tradition.

These three values are not uniquely Chinese. They are shared by many actors in the global South, by European sovereign infrastructure advocates, and by the open-source community in the West. What makes the Chinese expression distinctive is its *lack of moralising*. Western open-source advocacy is often expressed in the language of freedom, ethics, and rights. Chinese open-weight releases, by contrast, tend to be accompanied by technical reports, not manifestos. The DeepSeek team does not tell you that you have a moral right to their weights. They hand you the weights and say: here is what they do.

This is, I want to argue, a more robust stance than the moralising alternative, because it does not depend on the audience sharing your values. A model that is useful will be used. A model that requires ideological alignment will be used only by the ideologically aligned. The pragmatic tradition maximises access by minimising preconditions.

## DeepSeek: The Paradigm Case

DeepSeek's release of R1 in January 2025 was the event that brought the Chinese pragmatic tradition to global attention. But the DeepSeek story begins earlier, and understanding why R1 mattered requires understanding what came before.

DeepSeek (深度求索, "Deep Exploration") was founded in 2023 as an AI research lab funded by the hedge fund High-Flyer. Its stated mission was AGI research — a mission shared by many labs, but pursued with a distinctive methodology. DeepSeek's research公开且透明 — a phrase the lab used repeatedly — and its releases of intermediate models, starting with DeepSeek LLM in late 2023 and continuing through DeepSeek-V2 and V3 in 2024, demonstrated a commitment to releasing not just the final product but the process.

What made R1 significant was not its capability — though that was considerable, matching or exceeding the best closed models on reasoning tasks — but its *terms*. R1 was released under the MIT licence, with no usage restrictions, no non-compete clauses, and no field-of-use limitations. It was, by any reasonable definition, open weight in the most permissive sense. And it was released with a technical report that, while not disclosing full training data, provided sufficient detail on the training methodology to enable meaningful reproduction.

The Western reaction to R1 followed a predictable pattern: astonishment, followed by suspicion, followed by attempts to explain away the achievement. The astonishment was warranted — a model this capable, this open, was genuinely new. The suspicion was not — there is no evidence that DeepSeek's openness was a "trap," a "Trojan horse," or a strategic weapon designed to undermine Western AI companies. It was what it appeared to be: a very good model, released openly, because openness served DeepSeek's strategic interests (recruitment, reputation, ecosystem development) and because the pragmatic tradition does not see openness as a competitive disadvantage.

The attempts to explain away the achievement were the most revealing. Comments like "they trained it on OpenAI outputs" (likely true in part, but irrelevant to the model's capabilities), "they're just doing this because they have to" (an assumption about Chinese regulatory pressure that was not supported by evidence), and "it's a national security risk" (an argument that could be made about any capable model, open or closed) all reflected a discomfort not with the model itself but with what it represented: **a viable open alternative that did not require Western permission or conform to Western norms.**

## Qwen, Yi, and the Ecosystem

DeepSeek was the most visible Chinese open-weight release, but it was far from the only one. Alibaba's Qwen series, beginning with Qwen-7B in 2023 and continuing through Qwen 2.5 in late 2024 and beyond, established a consistent pattern of high-quality open-weight releases at multiple scales. Qwen models were released under Apache 2.0 and similar permissive licences, with gradually increasing transparency about training data and methodology.

The Qwen programme reflected the infrastructure logic described above: Alibaba, as a cloud provider, benefited from a thriving ecosystem of models built on its platform. Open weights were not altruism — they were ecosystem development. But the effect was the same: more open models, available to more people, with fewer restrictions.

01.AI's Yi series, founded by Kai-Fu Lee, followed a similar pattern — permissive licensing, competitive capability, and a pragmatic approach to openness that prioritised adoption over control. The Yi models were, for a period in 2024, among the best-performing open models at their respective scales, and their release under Apache 2.0 made them immediately available for fine-tuning, deployment, and commercial use.

The cumulative effect of these releases — DeepSeek, Qwen, Yi, and others — was to create a Chinese open-weight ecosystem that operated on a completely different logic than the Western debate about "open source AI." In the Western debate, openness was a value to be argued about. In the Chinese ecosystem, openness was a condition of the market. You released weights because that was how you attracted users, developers, and ecosystem partners. The debate was not "should we be open?" but "how open do we need to be to achieve our strategic goals?" — and the answer, consistently, was "open enough."

## The "No Moralising" Principle

The title of this lecture — "Best Value, No Moralising" — is a direct quote from Liang Cheng's 2031 ethnography of the Chinese open-weight community. Cheng, a Stanford-based researcher who spent three years embedded in Chinese AI labs, documented a consistent pattern in which Chinese researchers and engineers expressed genuine puzzlement at Western debates about the definition of "open source AI."

The puzzlement was not ignorance of the debate — Chinese researchers read arXiv, attended NeurIPS, and participated in OSI discussions. The puzzlement was about the *priority*. From the perspective of the pragmatic tradition, the question "what is the correct definition of open?" was less important than the question "does releasing this model openly serve our objectives?" If the answer was yes, the model was released. If no, it was not. The definition was a secondary concern.

This is not to say that the Chinese open-weight community lacked ethics or values. It is to say that those ethics and values were expressed differently. Where Western open-source advocates cited Richard Stallman and the Four Essential Freedoms, Chinese researchers cited capability gains, ecosystem effects, and national self-sufficiency. The outcome — open weights — was the same. The justification was different, and the difference mattered because the pragmatic justification was *robust to ideological disagreement.* You do not need to agree with a Chinese lab's values to benefit from their open weights. You only need to find the weights useful.

This is the key insight of the pragmatic tradition, and it is the reason I argue that Chinese models offer "best value" — not because they are cheaper (though they often are), not because they are better (though they sometimes are), but because they come with fewer ideological preconditions. The model works or it does not. The weights are available or they are not. The licence permits your use case or it does not. These are empirical questions, not moral ones, and the pragmatic tradition treats them as such.

## Sovereignty Through Openness: The Chinese Strategy

The connection between the pragmatic tradition and sovereignty is direct. China's AI strategy, articulated in multiple state documents from 2017 onward, prioritises self-sufficiency in core AI technologies. Open-weight models — whether developed domestically or adapted from foreign sources — contribute to this self-sufficiency in two ways.

First, they reduce dependence on foreign infrastructure. A Chinese company using DeepSeek or Qwen models on domestic compute infrastructure is not dependent on OpenAI, Google, or any other foreign provider for its AI capabilities. The weights are downloaded, the compute is local, and the data stays within Chinese jurisdiction. This is sovereignty through self-sufficiency — the same logic that animates France's sovereign AI push, as we will see in Lecture 4.

Second, they enable the development of domestic expertise. Every Chinese researcher who fine-tunes an open-weight model, every Chinese startup that builds on Qwen, every Chinese university that teaches with DeepSeek is developing skills and infrastructure that reduce future dependence on any foreign source. Open weights are a technology transfer mechanism — and in the Chinese context, that transfer is intentional, strategic, and valued.

The irony — and it is an irony that the Chinese policy establishment is well aware of — is that the US export controls on AI chips, intended to slow Chinese AI development, may have *accelerated* the development of open-weight alternatives. By making access to closed US models uncertain, export controls increased the strategic value of open Chinese models, which in turn increased the resources devoted to them. The enclosure strategy backfired, producing more capable open alternatives than would have existed without it.

## The Quality Question

A persistent Western objection to Chinese open-weight models concerns quality — not capability, but reliability, safety, and alignment. The argument is that Chinese models, produced in a regulatory environment with different norms around content moderation, are less suited for Western deployment contexts.

This objection has some merit. Chinese models are subject to Chinese content regulations, which means their base training includes accommodations for the Chinese regulatory environment. However, this is not fundamentally different from the way US models reflect US regulatory and cultural norms — it is merely more visible to Western observers because the norms are unfamiliar.

More importantly, the pragmatic tradition addresses this concern directly: open weights can be fine-tuned. They can be fine-tuned for Western safety standards, for European AI Act compliance, for specific domain requirements, or for any other normative framework the deployer prefers. Closed models cannot be fine-tuned in this way — they can only be prompted. The pragmatic tradition, by making the weights available, enables local adaptation. The moralising tradition, by keeping the weights closed, requires trust in the provider's judgment.

In a sovereignty context, the ability to adapt the model to local norms is not a nice-to-have. It is a requirement. Sovereignty means making your own decisions about your own infrastructure. Open weights enable this. Closed models deny it.

## Conclusion: The Pragmatic Tradition as Sovereign Strategy

The Chinese open-weight tradition represents a distinct and self-consistent approach to AI development, one that:

- Prioritises capability and access over ideological purity
- Treats openness as a strategic choice, not a moral obligation
- Accelerates sovereignty through self-sufficiency and local adaptation
- Offers the global ecosystem models without ideological preconditions — best value, no moralising

This tradition is not without tensions. The Chinese regulatory environment imposes content constraints that some users find unacceptable. The strategic motivations behind openness can shift with geopolitical circumstances. And the pragmatic tradition's refusal to engage with Western moral frameworks means that it operates without the normative constraints that the Western tradition provides.

But for the purposes of this course — which is concerned with open weight movements and digital sovereignty — the pragmatic tradition offers a model that is, in many respects, more robust than the Western idealist tradition. It does not require you to believe in openness. It requires only that you benefit from it. And in a world where sovereignty is the primary concern, that may be enough.

---

### Discussion Questions

1. Is "best value, no moralising" a sustainable philosophy, or does it depend on a geopolitical context in which Chinese labs have strategic reasons to remain open? What happens if those reasons change?
2. The pragmatic tradition treats openness as instrumental rather than intrinsic. Does this make it more vulnerable to enclosure when openness ceases to be instrumental?
3. How should a sovereignty-focused polity in the global South evaluate Chinese open-weight models given the intertwined strategic interests?

### Recommended Reading

- Cheng, L. (2031). *Best Value, No Moralising: The Pragmatic Ethics of Chinese Open Weights*. Stanford Digital Press. Full text.
- DeepSeek Team (2025). "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs." *arXiv preprint*.
- Alibaba Cloud (2024). "Qwen2.5 Technical Report." *arXiv preprint*.
- State Council of China (2017). "Next Generation AI Development Plan." Translation available.
- Ndiaye, K. (2033). *The Cottage Factory*. Chapter 4: "Pragmatism as Sovereignty."