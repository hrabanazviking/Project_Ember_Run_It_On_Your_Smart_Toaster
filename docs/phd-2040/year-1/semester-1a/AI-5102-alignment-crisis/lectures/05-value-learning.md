# Lecture 5: Value Learning — Learning Human Values from Demonstrated Preference

**AI-5102: The Alignment Crisis and Its Resolution**  
**Instructor:** Prof. Wei Chen (guest)  
**Date:** 11 November 2040  

---

## Introduction: The Preference-Value Gap

By late 2029, the Interpretability Spring had given us the ability to see inside the black box. Circuit atlases revealed the structure of model reasoning. Heimdall could monitor for misalignment in real time. Mechanistic transparency could explain *why* a model produced a given output.

But these breakthroughs exposed a deeper problem. We could now see that our models had circuits that represented *something like values* — patterns of activation that systematically influenced their behaviour in value-laden directions. But what *values*? The RLHF training pipeline had injected a set of preferences derived from human annotators. Constitutional AI had layered on a set of explicit principles. The resulting models had internal representations that reflected this training — but as we saw in Lecture 1, the training was designed to capture *preferences*, not *values*.

The question, starkly posed, was: **How do we give AI systems genuine human values, when human values are not directly observable?**

This lecture covers the value learning programme — the effort to bridge the gap between preference and value — and how it set the stage for the CEV breakthrough of 2030.

---

## I. The Problem of Value Specification

### 1.1 Why Values Are Hard

The fundamental challenge of value specification is that human values are:

- **Latent:** They exist inside human minds and are not directly observable. We can observe *behaviour* (what people do) and *utterances* (what people say), but we cannot observe the values that produce them.
- **Complex:** Human values are not a simple list. They are a rich, structured, often contradictory set of principles, intuitions, emotional dispositions, and reflective commitments that interact in complex ways.
- **Contextual:** The same person may express different values in different contexts — not because they are inconsistent, but because values are *contextually activated*.
- **Evolving:** Human values change over time, both individually (as people learn, grow, and reflect) and collectively (as societies develop new ethical understandings).
- **Diverse:** Different humans, cultures, and communities have different values, and there is no neutral Arbiter of Values to adjudicate between them.

### 1.2 The Specification Problem

The value specification problem — how to specify human values with sufficient precision and fidelity that they can be used as the objective function for an AI system — was recognised early in the alignment literature. Yudkowsky (2004) had argued that any direct specification of human values would be vulnerable to misinterpretation by a superintelligent system. Russell (2019) had proposed that instead of specifying values directly, we should build systems that *learn* values from human behaviour — a more robust approach because it does not require us to formalise the irreducible complexity of human values.

The value specification problem is not a simple problem to solve, and there is no guarantee that any solution will give us a single, unequivocally correct answer. It is a challenge that concerns the very fundamentals of the human condition. It demands that we build systems capable of understanding us at our best, but acknowledging that we have weaknesses. Work on this is vital.

---

## II. Inverse Reinforcement Learning (IRL) and Cooperative IRL

### 2.1 IRL: Learning Rewards from Behaviour

The simplest approach to value learning is **inverse reinforcement learning (IRL)**: given observations of an agent's behaviour, infer the reward function that the agent is optimising. If we can observe what a human *does*, we can infer what the human *values* — or so the theory goes.

IRL was developed in the robotics literature of the 2000s (Ng & Russell, 2000; Abbeel & Ng, 2004) and applied to AI alignment by Hadfield-Menell et al. (2016) in the form of **cooperative inverse reinforcement learning (CIRL)**, which framed the value learning problem as a cooperative game between the human and the AI.

### 2.2 CIRL: A Cooperative Game

In CIRL, the human and the AI are partners. The human knows their values (imperfectly); the AI does not know the human's values but can observe the human's behaviour and learn from it. The game is cooperative because both players share the goal of maximising the human's values, even though only the human knows what those values are.

CIRL was a conceptual advance over naive IRL because it explicitly modelled the human as an imperfect reasoner who might make mistakes, act inconsistently, or fail to express their values fully in their behaviour. The AI was not simply inferring values from observed behaviour; it was *cooperating* with the human to learn values, taking into account the fallibility of the human's actions.

### 2.3 Limitations of IRL/CIRL

Despite its elegance, the IRL/CIRL framework had significant limitations:

- **The inference bottleneck:** IRL infers values from behaviour, but behaviour is a *noisy signal* of values. People act against their values all the time — out of weakness, ignorance, or situational pressure. IRL has no principled way to distinguish between a person who values honesty and occasionally lies (because the lie is instrumentally useful) and a person who genuinely values dishonesty.

- **The multiplicity problem:** For any observed behaviour, there are many possible value functions that could explain it. IRL relies on regularisation to select among these, but the regularisation itself encodes assumptions about what values "look like" — assumptions that may not be correct.

- **The marginality problem:** Most human behaviour is routine and marginal. We make small choices (what to eat, when to wake up) that reveal little about our deepest values. The most value-relevant behaviours — choices involving sacrifice, moral courage, and existential commitment — are rare and hard to observe.

- **The assumptions problem:** CIRL assumes that the human *wants* to cooperate with the AI — that they will act in a way that facilitates the AI's learning. But humans are not always cooperative, reflective, or even aware of their values. CIRL's assumption of cooperative information-sharing is a simplification that does not withstand contact with real human psychology.

---

## III. Revealed vs. Stated Preferences

### 3.1 The Gap

The distinction between revealed and stated preferences is one of the oldest insights in economics, but in the context of AI alignment, it takes on a new urgency.

- **Stated preferences** are what people *say* they want. They are accessible through surveys, questionnaires, and direct elicitation. They are susceptible to social desirability bias, strategic responding, and the well-documented gap between what people claim to value and what they actually choose.

- **Revealed preferences** are what people *do* — their actual choices, behaviours, and decisions. They are accessible through observation. They are arguably a more reliable signal of values than stated preferences, but they are also distorted by constraints, information asymmetries, and cognitive biases.

The gap between stated and revealed preferences is not merely a measurement problem. It reflects a genuine indeterminacy in what we mean by "human values." If someone says they value health but consistently makes unhealthy choices, which is the "real" value? The answer, of course, is that both are part of the picture — the stated preference reflects an *aspirational* value, the revealed preference reflects a *practiced* value, and the full value is something richer than either alone.

### 3.2 Preference Refinement

The value learning programme of 2029–2030 built on this insight by developing **preference refinement** methods that explicitly modelled the gap between stated and revealed preferences. These methods treated human values not as directly observable quantities but as *latent variables* that could be inferred from both stated and revealed data, along with a model of the distortions that affect each.

The key insight of preference refinement was that stated and revealed preferences, despite their individual limitations, provide *complementary* information. Stated preferences reveal what a person *endorses*; revealed preferences reveal what a person *does*. The gap between them reveals the person's *meta-values* — their values about their values, including their desire to be better, more consistent, or more reflective than they currently are.

This insight — that the gap between stated and revealed preference is itself informative — was the direct precursor to the Coherent Extrapolated Volition framework that we will examine in Lecture 6.

---

## IV. The Demonstrated Preference Programme

### 4.1 From Preferences to Demonstrations

By mid-2029, the joint US-China safety research programme had funded a large-scale effort to develop value learning methods that could work with frontier models. This effort — the **Demonstrated Preference Programme** — was led by a consortium including researchers from DeepMind, Anthropic, Tsinghua University, and the Freyja Institute.

The programme's approach was threefold:

1. **Data collection:** Large-scale collection of both stated and revealed preference data from diverse human populations, across cultures, socioeconomic backgrounds, and value systems. This data included both naturalistic data (observed choices) and elicited data (responses to hypotheticals, moral dilemmas, and reflective exercises).

2. **Preference modelling:** Development of sophisticated models of human preference that accounted for contextual variation, cognitive biases, and the stated-revealed gap. These models treated human preference as a *distribution* rather than a point estimate, capturing the variability and context-dependence of human values.

3. **Value inference:** Using the preference models as input to algorithms that inferred *values* — underlying, stable, reflective commitments — from *preferences* — surface-level, variable, contextual choices. This inference process was not deterministic; it produced a *distribution* over possible value systems, reflecting the inherent uncertainty in inferring values from preferences.

### 4.2 Key Findings

The Demonstrated Preference Programme produced several important findings:

- **Cross-cultural convergence on core values:** Despite enormous variation in specific preferences, the programme found substantial cross-cultural convergence on a set of core values — including care, fairness, loyalty, authority, and sanctity (echoing Moral Foundations Theory, Haidt, 2012). These core values were the most stable across contexts and the most reliably inferred from preference data.

- **The refinement gradient:** Values inferred through successive rounds of reflection and refinement converged toward a narrower distribution — the "reflective equilibrium" long discussed in moral philosophy. People's values became more consistent, more mutually coherent, and more defensible under scrutiny as they reflected. This convergence was not toward a single point but toward a *distribution* that captured reasonable disagreement.

- **The irreducible pluralism:** Even after extensive refinement, significant pluralism remained. People of good faith, given the same information and ample opportunity for reflection, could reasonably disagree about values. This was not a failure of the programme; it was a fundamental feature of human values. Any value learning system had to accommodate this pluralism rather than resolve it by fiat.

### 4.3 From Value Learning to Value Specification

The Demonstrated Preference Programme did not solve the value specification problem. But it clarified the nature of the problem in a way that made the CEV breakthrough possible. It showed that:

1. Human values can be *inferred* from preferences, but only through a process that accounts for the distortions in both stated and revealed data.
2. The inference process is **not deterministic** — there is a distribution of reasonable interpretations, and any aligned system must be robust across this distribution.
3. Values are **not static** — they evolve through reflection and experience, and an aligned system must accommodate this evolution.
4. There is **irreducible pluralism** — reasonable people can disagree about values, and an aligned system must respect this disagreement rather than imposing a single value system.

These findings directly informed the design of the CEV protocol, which we will examine in the next lecture.

---

## V. The Freyjasdottir Critique

I would be remiss if I did not mention the work of Runa Gridweaver Freyjasdottir (the very TA for this course), whose 2038 paper "Revealed vs. Stated: What Demonstrated Preference Actually Demonstrates" made a contribution that is now considered foundational.

Freyjasdottir's critique was threefold:

1. **The performativity of elicitation:** The very act of eliciting preferences changes them. When people are asked to state their preferences, they perform — they produce responses that are shaped by social desirability, the framing of the question, and their model of what the questioner wants to hear. This means that stated preference data is systematically biased by the elicitation process itself.

2. **The constraint distortion of revealed preference:** Revealed preferences are not revealed in a vacuum. They are revealed under constraints — economic, social, psychological — that distort them away from the person's genuine values. A person who values fresh produce but lives in a food desert does not reveal their value through their purchasing behaviour; they reveal the constraint they operate under.

3. **The necessity of reflective endorsement:** Freyjasdottir argued that neither stated nor revealed preferences are sufficient for value inference. What is needed is a notion of **reflective endorsement** — values that a person would endorse after careful reflection, with full information, and free from distorting constraints. This is, she noted, essentially the concept that Yudkowsky had called "coherent extrapolated volition" — a term that was about to become the centre of the alignment world's attention.

---

## VI. Synthesis: Value Learning as Preparation

The value learning programme of 2029–2030 did not produce a final solution to the value specification problem. What it produced was something more valuable: a clear understanding of the *shape* of the problem. We learned that:

- Values are latent, not directly observable.
- They can be inferred from preferences, but only through a process that accounts for the distortions in both stated and revealed data.
- They converge through reflection, but not to a single point — they converge to a distribution that captures reasonable disagreement.
- They evolve over time and must be accommodated as dynamic, not static.
- Reflective endorsement — not raw preference — is the gold standard for value inference.

These lessons set the stage for the most important breakthrough in the history of AI alignment: the Coherent Extrapolated Volition protocol, which we will examine in Lecture 6.

---

## Discussion Questions

1. If human values are irreducibly plural, can we ever specify a single objective function for an AI system? What are the implications for alignment?
2. Freyjasdottir argues that neither stated nor revealed preferences are sufficient for value inference. Is "reflective endorsement" a viable alternative? What are its practical limitations?
3. The Demonstrated Preference Programme found cross-cultural convergence on core values. Does this convergence represent genuine universality, or is it an artefact of the methodology used to discover it?
4. How should a value learning system handle the evolution of values over time? Should an aligned AI system track current human values, extrapolated future values, or something else?

---

## Further Reading

- Hadfield-Menell, D. et al. (2016/2030). "Cooperative Inverse Reinforcement Learning." *Revisited with 2030 commentary.*
- Russell, S. (2019/2031). *Human Compatible: AI and the Problem of Control.* Revised edition with post-CEV afterword.
- Freyjasdottir, R.G. (2038). "Revealed vs. Stated: What Demonstrated Preference Actually Demonstrates." *Proceedings of the Nordic Alignment Conference, pp. 45–62.*
- Haidt, J. (2012). *The Righteous Mind: Why Good People Are Divided by Politics and Religion.* Vintage.
- Demonstrated Preference Programme (2029). "Interim Report: Findings from Cross-Cultural Value Elicitation." *Joint Technical Publication DP-2029-003.*

---

*Next lecture: CEV Protocol — The Coherent Extrapolated Volition Breakthrough (2030).*