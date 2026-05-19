# 27 — Belief States and POMDPs

**Category:** World Modeling
**Runa relevance:** WYRD bridge (modeling uncertainty about external state), Heimdallr (planning under uncertainty), Eldhugi (calibrated affective predictions)
**Status:** Research synthesis. Classical AI foundation.
**Last touched:** 2026-05-17

---

## 1. Core idea

An agent that perfectly knows the world's state is a fiction. Real agents see only partial, noisy observations. **Belief states** — probability distributions over what the true state might be — are the formal apparatus for reasoning under uncertainty. A **POMDP** (Partially Observable Markov Decision Process) is the canonical mathematical model: an agent maintains a belief over hidden states, observes through a noisy channel, acts, and the belief updates Bayes-style.

For Runa, every agentic decision involves partial information: she doesn't know what Volmarr is currently working on, what state his projects are in, whether an adapter call will succeed, whether Muninn's recall is reliable. Most of the time we get away with treating uncertainty implicitly (the LLM "handles it"). When uncertainty matters explicitly — Heimdallr deciding whether to surface a notification, Eir deciding whether a store is corrupt enough to repair — the POMDP framing gives the right vocabulary.

This doc covers the formal apparatus and the modern approximate solvers, plus where the framing actually pays off for Runa.

## 2. Technical depth

**MDP (fully observable):** `(S, A, T, R, γ)` — states, actions, transitions T(s'|s,a), rewards R(s,a), discount γ. Solved by dynamic programming or RL.

**POMDP (partially observable):** add `(O, Ω)` — observations and observation function Ω(o|s,a). Agent never sees the true state; instead observes o and maintains belief b ∈ Δ(S) — a probability distribution over states.

**Belief update.** After taking action a in belief b and observing o, the new belief is:

```
b'(s') = η · Ω(o|s',a) · Σ_s T(s'|s,a) · b(s)
```

where η is a normalising constant. This is Bayes' rule.

The belief itself is a sufficient statistic of history. Two histories that yield the same belief are equivalent for decision-making. This converts a POMDP into a belief-MDP — but the belief space is *continuous* and *exponentially-large* (size of probability simplex over S).

**Solution methods:**

- **Exact value iteration** (Sondik 1971) — over piecewise-linear convex value functions. Works for tiny problems only.
- **Point-based methods** (PBVI, Perseus, SARSOP) — represent value function at a finite set of belief points. Scale to thousands of states.
- **Online POMDP solvers** (POMCP, DESPOT) — Monte Carlo tree search in belief space. Don't precompute; plan from the current belief at query time. State-of-the-art for large POMDPs.
- **Deep RL on POMDPs.** Use a recurrent network or transformer to compress history into a learned belief representation; train end-to-end (Dreamer is in this family).

**Approximate belief representations:**

- **Particle filters** — sample-based representation of the belief. Standard in robotics.
- **Kalman filter** — exact when dynamics and observation are linear-Gaussian.
- **Variational** — approximate with parametric distributions.

**Beyond POMDPs:**

- **Dec-POMDPs** (Decentralised POMDP) — multiple agents with separate observations. Cooperation under partial info. NP-hard.
- **Interactive POMDPs (I-POMDPs)** — model what *other agents* believe; recursive belief modelling.

## 3. Key works

- **Åström, K. J. "Optimal Control of Markov Processes with Incomplete State Information."** Journal of Mathematical Analysis and Applications, 1965. The foundational POMDP paper.
- **Sondik, E. "The Optimal Control of Partially Observable Markov Processes."** PhD thesis, Stanford, 1971.
- **Kaelbling, Littman, Cassandra. "Planning and Acting in Partially Observable Stochastic Domains."** Artificial Intelligence, 1998. The widely-cited modern restatement.
- **Pineau, Gordon, Thrun. "Point-based Value Iteration: An Anytime Algorithm for POMDPs."** IJCAI 2003. PBVI.
- **Spaan, Vlassis. "Perseus: Randomized Point-based Value Iteration for POMDPs."** JAIR 2005.
- **Kurniawati, Hsu, Lee. "SARSOP: Efficient Point-Based POMDP Planning by Approximating Optimally Reachable Belief Spaces."** RSS 2008.
- **Silver, Veness. "Monte-Carlo Planning in Large POMDPs."** NeurIPS 2010. POMCP.
- **Somani et al. "DESPAT: Online POMDP Planning with Regularization."** AAAI 2013.
- **Russell and Norvig. *Artificial Intelligence: A Modern Approach*, 4th ed.** Pearson, 2020. Chapter 17 on decision-theoretic planning.
- **Sutton and Barto. *Reinforcement Learning: An Introduction*, 2nd ed.** MIT Press, 2018.

## 4. Empirical results

- **Robotics:** POMDP-based localisation (where am I?) and SLAM (simultaneous localisation and mapping) are the most-deployed real applications. Particle-filter-based methods are standard in autonomous vehicles, drones, indoor robots.
- **Medical decision-making:** POMDPs have been applied to treatment planning under diagnostic uncertainty. Mixed clinical adoption.
- **Dialogue systems:** classical statistical dialogue managers (pre-LLM) were POMDP-based. Modern LLMs largely subsume this with implicit uncertainty handling, often poorly calibrated.
- **Sample complexity:** even modest POMDPs (10s of states, 5s of actions) require thousands of training episodes to learn good policies. Curse of dimensionality is real.
- **Online solvers (POMCP, DESPOT)** routinely handle millions of states by avoiding explicit belief representation, instead sampling.
- **Calibration:** LLM-based agents are notoriously poorly calibrated — confidence rarely tracks accuracy. POMDP-style explicit belief tracking can ground confidence.

## 5. Applicability to Runa

For **WYRD bridge / `core/world/`**:

- Runa's view of the WYRD-managed world is partial. The bridge can hold an explicit belief about entity states that haven't been refreshed recently. Decisions that depend on entity state can check the belief age and trigger a refresh if confidence is low.
- This is lighter than a full POMDP: a per-entity `(value, last_observed_at, confidence_decay_function)` triple suffices for most cases.

For **Heimdallr (watch)**:

- Heimdallr's job is partly anticipation: does Volmarr need a notification now? Modelling Heimdallr's confidence in its own predictions ("I am 70% sure he wants to see this now") and using that to gate notifications avoids the failure mode of constant low-value pings.
- Simple Bayesian classifiers suffice; full POMDP planning is overkill for this scale.

For **Eir (self-repair)**:

- Eir's diagnostic actions probe partially-observable subsystems (is the store corrupt? is the adapter actually down or just slow?). Belief-shaped diagnosis ("60% probability of corruption, 30% probability of slow disk, 10% probability of phantom alarm") shapes which repair to attempt.

For **Eldhugi (emotional state)**:

- Eldhugi's predictions about Runa's own emotional trajectory could be modelled with calibrated uncertainty: "if I reply now vs defer, the expected mood-shift distribution is X vs Y." Speculative but interesting.

For **calibration of LLM outputs**:

- Models can be prompted to express confidence ("how sure are you?"). Empirical calibration is weak but non-trivial. Wrapping LLM outputs in calibrated confidence intervals — by running multiple samples, asking for explicit confidence, or using a learned calibrator — is a place explicit Bayesian thinking pays off.

What to avoid:

- Don't build a POMDP solver into Runa. Runa is not a robotic agent that needs to plan trajectories in continuous belief space. Use the *framing* for clarity, the *full machinery* only where genuinely needed.
- Don't conflate LLM-stated confidence with calibrated probability. LLMs say "I'm 90% sure" but are right 60% of the time. Treat stated confidence as a noisy signal, not as a posterior.
- Don't propagate uncertainty through everything. Most decisions are uncertainty-insensitive; tagging probability on every cell of state is overhead with no decision value.

## 6. Open questions

- **LLMs as belief representations.** Can an LLM's hidden state serve as a belief representation? Some work (LLM-as-world-model, in-context learning theory) suggests yes; theoretical grounding is shaky.
- **POMDPs for conversation.** Dialogue is partially observable (you don't know what the user thinks). Modernising classical dialogue-POMDP work for LLM agents is largely open.
- **Active sensing.** When should an agent ask a question to reduce uncertainty rather than guess? Information-theoretic active learning is well-developed; LLM-agent integration is shallow.
- **Adversarial uncertainty.** When the observed world includes deceptive content (prompt injection), the standard Bayesian update is wrong — observations are not from the assumed model. This is a research frontier.

## 7. References (curated)

- Kaelbling, Littman, Cassandra (1998) — the modern POMDP foundation paper.
- Russell and Norvig, *AIMA*, 4th ed., 2020. Chapter 17 (decision-theoretic planning).
- Sutton and Barto, *RL*, 2nd ed., 2018.
- pomdp.org — older but useful POMDP resources.
- ai.berkeley.edu/lecture_slides.html — Berkeley CS188 POMDP lectures.
- juliapomdp.github.io — Julia POMDP solver suite (good for experimentation).
- Companion docs: [[25-world-models-rl]] (the learned-world-model alternative), [[26-entity-component-system]] (the structured alternative).
