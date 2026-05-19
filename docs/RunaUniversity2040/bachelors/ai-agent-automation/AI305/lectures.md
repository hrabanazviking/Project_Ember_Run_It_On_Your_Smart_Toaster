# AI305: Autonomous Task Execution & Self-Correction
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI205 (Agent Architecture Design), AI207 (Knowledge Representation & Reasoning), AI301 (Multi-Agent Systems & Coordination)
**Description:** An agent that cannot correct its own errors is not autonomous — it is brittle. Autonomous task execution requires an agent to plan multi-step actions, execute them in a dynamic and partially observable world, monitor its own progress, detect when things go wrong, diagnose the failure, and replan or recover — all without human intervention. This course covers the full lifecycle of autonomous task execution: task decomposition and hierarchical planning, execution monitoring and progress tracking, error detection and diagnosis, recovery strategies and replanning, and the feedback loops that tie these stages into a self-correcting system. Students will implement a complete autonomous executor that plans, acts, observes, and adapts — and they will learn that the hardest part of autonomy is not doing things right, but doing things right when everything goes wrong.

> *"Even the gods must sometimes retie the knot."* — The agent that cannot self-correct is no agent at all; it is a script.

---

## Lectures

### ᚠ Lecture 1: The Paradox of Autonomy — Why Execution Without Correction Is Not Autonomy

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A script executes instructions in sequence. If every instruction succeeds, the script produces the correct result. If any instruction fails — the file is not found, the network is down, the API returns an error — the script either crashes or silently produces garbage. The script has no awareness that something went wrong, no ability to diagnose the failure, and no capacity to try an alternative approach. It is a deterministic automaton that works when the world cooperates and fails when it does not.

An autonomous agent is not a script. The defining characteristic of autonomy is the ability to maintain progress toward a goal despite obstacles, errors, and changing conditions. An agent that can plan but not correct its plan is autonomous only in the happy path — when everything goes as expected. But the world does not cooperate. APIs change their response formats, services go down, users provide ambiguous instructions, and the agent's own reasoning occasionally produces flawed conclusions. Autonomous task execution without self-correction is not autonomy at all; it is fragile brittleness dressed up with a planning module.

The **autonomy paradox** states: the more autonomous an agent appears in the happy path, the more catastrophic its failures appear in the unhappy path. A fully autonomous agent that never needs human intervention seems wonderful — until it encounters a situation its plan did not anticipate, and proceeds blindly, compounding errors until the result is absurd or harmful. The paradox resolves only when autonomy includes self-correction: the ability to detect that something is wrong, diagnose what is wrong, and adapt the plan to address what is wrong. Autonomy without self-correction is reckless; self-correction makes autonomy *responsible*.

The history of autonomous systems is a history of self-correction failures. The Mars Climate Orbiter (1999) was lost because one team used metric units and another used Imperial units, and no component of the system checked whether the numbers made sense. The Ariane 5 (1996) veered off course because a floating-point value was converted to a 16-bit integer and the overflow was not caught — the guidance system, receiving garbage data, continued executing as if the data were valid. The Knight Capital trading disaster (2012) lost $440 million in 45 minutes because a misconfigured server ran old code alongside new code, and no one monitoring system caught the inconsistency until the losses were catastrophic. In each case, the system executed its instructions correctly — the problem was that no component was watching for incorrect execution and correcting it.

The 2040 agent architecture addresses the autonomy paradox with a **self-correction loop** that wraps every stage of task execution:

**Plan.** The agent generates a plan — a sequence of actions expected to achieve the goal. The plan is a hypothesis, not a guarantee; it encodes assumptions about the world that may be wrong.

**Execute.** The agent executes the plan, one action at a time, in the real world (or a simulated environment). Execution produces outcomes, which may or may not match expectations.

**Observe.** After each action, the agent observes the outcome — the tool's return value, the environment's state, the user's response. Observation is the bridge between plan and reality.

**Evaluate.** The agent compares the observed outcome to the expected outcome. If they match, execution continues. If they diverge, the agent has detected a problem — and self-correction begins.

**Diagnose.** The agent asks: why did the outcome diverge from expectations? The diagnosis can be at any level: the action was executed incorrectly (execution error), the action was correct but the expected outcome was based on a wrong assumption (planning error), the environment changed between plan and execution (world error), or the observation itself was faulty (sensing error).

**Adapt.** Based on the diagnosis, the agent modifies the plan: retry the action with different parameters (execution-level correction), replan from the current state (planning-level correction), or escalate to the user if the problem exceeds the agent's capacity to correct (bounded autonomy).

This **Plan-Execute-Observe-Evaluate-Diagnose-Adapt (PEOEDA)** cycle is the fundamental loop of autonomous task execution. It is inspired by and extends the classical **Plan-Execute-Monitor-Replan** cycle from AI planning (Ghallab, Nau & Traversot, 2004), but adds explicit diagnosis and bounded autonomy — two capabilities that distinguish 2040 agents from their predecessors.

The Norse concept of **wyrd** — the interconnected web of cause and consequence — provides the philosophical grounding for this cycle. Wyrd is not fate in the deterministic sense; it is the accumulated weight of past actions and present conditions that constrains what can happen next. The agent's plan is its intended wyrd — the path it intends to follow through the web. But the web is vast and partially known, and other forces (other agents, changing environments, the agent's own errors) are also weaving. When the agent discovers that the actual path diverges from the intended path, it must re-see the web, re-understand its position, and re-choose its path. Self-correction is the agent's ongoing negotiation with wyrd.

**Key Topics:**

- Scripts vs. autonomous agents: execution without awareness vs. execution with self-correction
- The autonomy paradox: apparent autonomy in the happy path, catastrophic failure in the unhappy path
- Historical self-correction failures: Mars Climate Orbiter, Ariane 5, Knight Capital
- The PEOEDA cycle: Plan, Execute, Observe, Evaluate, Diagnose, Adapt
- Wyrd: the web of cause and consequence as the philosophical model for self-correcting execution

**Required Reading:**

- Ghallab, M., Nau, D. & Traversot, P. *Automated Planning: Theory and Practice* (2004), Chapters 1–2
- Leveson, N. *Engineering a Safer World: Systems Thinking Applied to Safety* (2011), MIT Press
- University of Yggdrasil TR: "Wyrd-Driven Execution: Self-Correction as Negotiation with an Unpredictable World" (2040)

**Discussion Questions:**

1. The autonomy paradox suggests that adding autonomy without adding self-correction makes failures more catastrophic. But does the reverse hold? Does adding self-correction without adding autonomy produce any benefit? Is self-correction meaningful without the ability to act on the correction?
2. The PEOEDA cycle implies that every execution step should be followed by evaluation. But evaluation itself takes time and compute. At what point does the cost of evaluation exceed the cost of occasional undetected errors? How should the agent decide when to evaluate and when to skip it?
3. Wyrd is not deterministic fate — it is the web of accumulated conditions. Does this metaphor accurately capture the agent's situation? Or does the agent's plan genuinely change the web in a way that "negotiating with wyrd" doesn't capture? Is the agent creating new wyrd or merely navigating existing wyrd?

---

### ᚢ Lecture 2: Task Representation and Decomposition — Breaking the Gordian Knot

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An autonomous agent receives a goal — "Deploy the updated authentication service to production" — and must transform this high-level intention into a sequence of concrete actions — "1. Run the test suite. 2. Build the Docker image. 3. Push to the registry. 4. Update the Kubernetes deployment manifest. 5. Apply the manifest." — and each of those concrete actions may need to be further decomposed — "1a. Install test dependencies. 1b. Set the test environment variables. 1c. Execute the test runner." — and so on, until the agent reaches actions that can be directly executed by available tools. This process — **task decomposition** — is the first and most critical step of autonomous execution. Get the decomposition wrong, and no amount of brilliant execution or clever self-correction can save the agent from doing the wrong thing.

Task decomposition is not a new problem. The AI planning community has studied it since the 1970s, under various names: hierarchical task networks (HTNs), task decomposition planning, and hierarchical problem-solving. The basic insight is that tasks exist at multiple levels of abstraction, and the decomposition from one level to the next is not arbitrary — it reflects the structure of the domain. A cooking task "`prepare dinner`" decomposes into "`prepare appetizer`, `prepare main course`, `prepare dessert`" in a way that reflects the logical structure of a meal, not arbitrary slicing. A software deployment task "`deploy service`" decomposes into "`test`, `build`, `push`, `update`" in a way that reflects the logical structure of the deployment pipeline, not arbitrary slicing. Good decomposition reveals the natural structure of the task; bad decomposition fights it.

The 2040 landscape offers three major approaches to task decomposition, each with strengths and weaknesses:

**Manual decomposition** — a human expert writes the decomposition rules. "To deploy a service, first test, then build, then push, then update." This is the approach of classical HTN planning (Erol, Hendler & Nau, 1994). It is reliable and interpretable — you can inspect every rule and understand why the decomposition is what it is. But it is brittle — it cannot handle tasks the rule-writer didn't anticipate — and it doesn't scale — writing decomposition rules for every possible task in every possible domain is infeasible.

**Learned decomposition** — a language model generates the decomposition. Given the goal "Deploy the updated authentication service to production," the model outputs a plan: "1. Run the test suite. 2. Build the Docker image. 3. Push to the registry. 4. Update the Kubernetes deployment. 5. Apply the manifest." This is the approach used by most 2040 agent frameworks (LangChain, CrewAI, AutoGen, and the University of Yggdrasil's own ÞingAI). It is flexible — the model can decompose novel tasks it has never seen before — and it scales — no manual rule-writing required. But it is unreliable — the model may hallucinate steps, omit critical steps, or introduce steps that are logically inconsistent with the goal — and it is opaque — the model cannot explain why it chose this decomposition rather than another.

**Hybrid decomposition** — the model generates an initial decomposition, and a validation module checks it for completeness, consistency, and correctness against domain knowledge. Inconsistencies are flagged, missing steps are suggested, and the model revises the decomposition iteratively until it passes validation. This is the approach used by the **ÞingAI planner v3** (2040), which combines a language model for creative decomposition with a symbolic validator for correctness checking. The hybrid approach inherits the flexibility of learned decomposition and the reliability of manual decomposition — at the cost of increased complexity and the possibility that the validator rejects valid creative decompositions.

Regardless of the decomposition method, the resulting task structure can be represented in several forms:

**Linear plan:** A flat sequence of actions. Simple, but unable to represent conditional execution, parallelism, or iteration. Suitable only for trivial tasks.

**Hierarchical Task Network (HTN):** A tree of tasks, where each non-primitive task decomposes into a set of sub-tasks (which may themselves be non-primitive, decomposing further). The tree structure naturally represents the "break this big task into smaller tasks" pattern. HTNs also support **methods** — alternative decompositions for the same task, reflecting different strategies. "Deploy to production" might decompose into "blue-green deployment" or "rolling update" or "canary release," each a different method for the same task.

**State-variable plan:** A sequence of actions, each annotated with preconditions (what must be true before the action can execute) and effects (what changes after the action executes). The preconditions and effects are expressed as assignments to state variables, enabling formal verification: the planner can check that every action's preconditions are satisfied by the effects of preceding actions.

**Behavior Tree (BT):** A control structure originally developed for game AI but now widely used in robotics and agent systems. Behavior trees compose actions with control nodes — sequences (execute children in order, fail if any child fails), selectors (execute children in order, succeed if any child succeeds), decorators (modify a child's result), and parallels (execute children concurrently, succeed/fail based on policy). Behavior trees are modular, reusable, and trivial to modify — making them ideal for self-correcting agents that need to replan frequently.

The Norse myth of **Ragnarök** provides a vivid illustration of task decomposition. Odin knows that Ragnarök is coming — the final battle in which most of the gods will die. His response is not to prevent it (he cannot change wyrd) but to prepare for it: he gathers warriors to Valhalla, he sends Freyr to negotiate with the giants, he consults the head of Mímr for wisdom. Each of these is a sub-task of a higher-level task ("prepare for Ragnarök"), and each sub-task decomposes further — gathering warriors means selecting the worthiest, selecting means evaluating, evaluating means testing. Odin's decomposition is not linear; it is a network with conditional branches (if the Fenris Wolf breaks free, prioritize arming the gods; if Jörmungandr stirs, prioritize evacuating Midgard). The lesson: even the wisest of gods decomposes a seemingly impossible task into manageable sub-tasks, and even then, the plan must adapt to changing conditions.

**Key Topics:**

- Task decomposition: goal → concrete actions, the first and most critical step
- Manual decomposition (HTN planning): reliable, interpretable, brittle, doesn't scale
- Learned decomposition (LLM planning): flexible, scalable, unreliable, opaque
- Hybrid decomposition (model + validator): flexible and reliable, but complex
- Task representations: linear plans, HTNs, state-variable plans, behavior trees
- Ragnarök: Odin's decomposition of an impossible task into manageable (if ultimately doomed) sub-tasks

**Required Reading:**

- Erol, K., Hendler, J. & Nau, D. "HTN Planning: Complexity and Expressivity" (1994), *AAAI*
- Ghallab, M., Nau, D. & Traversot, P. *Automated Planning: Theory and Practice* (2004), Chapters 3–4
- Colledanchise, M. & Ögren, P. *Behavior Trees in Robotics and AI: An Introduction* (2018), CRC Press
- University of Yggdrasil TR: "ÞingAI Planner v3: Hybrid Decomposition with Symbolic Validation" (2040)

**Discussion Questions:**

1. Learned decomposition is flexible but unreliable — the model may hallucinate steps. Hybrid decomposition adds a symbolic validator, but the validator is only as good as the domain knowledge it encodes. What happens when the model generates a decomposition that is correct but not covered by the validator's rules? How can the system distinguish between "the model is wrong" and "the validator's domain knowledge is incomplete"?
2. Behavior trees allow trivial modification — just rearrange nodes, add conditions, or swap subtrees. This makes them ideal for self-correcting agents that replan frequently. But behavior trees are not "plans" in the classical AI sense — they don't represent the agent's *intention*, only the agent's *reactive behavior*. Is this a limitation? Can an agent that reasons about its own plans still use behavior trees?
3. Odin's preparation for Ragnarök is a task decomposition that ultimately fails — the gods still die. Is failed decomposition still decomposition? What does it mean for a decomposition to be "correct" if the task cannot be achieved regardless?

---

### ᚦ Lecture 3: Classical and Modern Planning — From STRIPS to LLMs

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Planning — the computation of a sequence of actions that transforms an initial state into a goal state — is the foundational problem of autonomous execution. An agent that cannot plan can only react; an agent that can plan can deliberate, anticipate, and strategize. The history of AI planning is a trajectory from rigid formalism to fluid intelligence, and understanding this trajectory is essential for understanding the 2040 planning landscape.

**Classical Planning (1971–2010)**

The founding formalism of AI planning is **STRIPS** (Stanford Research Institute Problem Solver), introduced by Fikes and Nilsson in 1971. STRIPS represents the world as a set of logical predicates — `(at robot room1)`, `(in box1 room1)`, `(door-open room1 room2)` — and each action as an operator with preconditions and effects. The action `push(box, from, to)` has preconditions `(at robot from)` and `(at box from)`, and effects `(at box to)` and `¬(at box from)`. Planning is the search for a sequence of operators that transforms the initial state (where the predicates are true) into a goal state (where the goal predicates are true).

STRIPS planning is **sound** — any plan it produces is guaranteed to achieve the goal — and **complete** — if a plan exists, STRIPS will find it. But STRIPS planning is also **intractable** — the search space grows exponentially with the number of predicates and operators, and even restricted STRIPS planning is PSPACE-complete (Bylander, 1994). The decades following STRIPS saw an explosion of planners: Graphplan (Blum & Furst, 1995), which used planning graphs to achieve remarkable speedups; SATPlan (Kautz & Selman, 1996), which encoded planning as propositional satisfiability; FF (Hoffmann & Nebel, 2001), which used heuristic search to find plans orders of magnitude faster than previous approaches; and many others.

The key limitation of classical planning is the **closed-world assumption**: the planner knows all predicates that are true, assumes all others are false, and assumes that actions have deterministic effects. If the world changes unexpectedly, the plan is invalid. If an action has a stochastic outcome, STRIPS cannot represent it. If the agent doesn't know the initial state, STRIPS cannot plan. Classical planning works in the **deterministic, fully observable, static** world — a world that does not exist outside textbooks.

**Markov Decision Processes and Probabilistic Planning (1998–2020)**

The next generation of planners relaxed the closed-world assumption. **Markov Decision Processes (MDPs)** (Puterman, 1994) model the world as a set of states, a set of actions, a transition function that specifies the probability of moving from one state to another after taking an action, and a reward function that assigns a value to each state. Planning in an MDP means computing a **policy** — a mapping from states to actions — that maximizes expected cumulative reward. Value iteration, policy iteration, and their variants (Sutton & Barto, 2018) compute optimal policies for MDPs.

**Partially Observable MDPs (POMDPs)** (Kaelbling, Littman & Cassandra, 1998) further relax the assumption that the agent knows the current state. In a POMDP, the agent receives observations that provide noisy evidence about the state, and must maintain a **belief state** — a probability distribution over possible states — and plan over belief states. POMDPs can model the fundamental problem of autonomous execution: the agent doesn't know everything, actions have uncertain outcomes, and the world changes.

The computational cost of POMDPs is severe — exact POMDP solving is PSPACE-hard in the horizon — and approximate methods (point-based value iteration, Monte Carlo tree search) are used in practice. By 2040, POMDP-based planners are used in robotics, autonomous driving, and critical infrastructure management, but they remain computationally expensive and require carefully designed models.

**Language Model Planning (2023–2040)**

The most dramatic shift in planning came not from planning research but from language modeling. Large language models, trained on vast corpora of text that include plans, recipes, tutorials, code, and step-by-step reasoning, can **generate plans** in natural language — given a goal, they produce a sequence of steps that is plausible, contextually appropriate, and often correct. The `chain-of-thought` prompting technique (Wei et al., 2022) demonstrated that LLMs can be induced to "think step by step," and the subsequent `ReAct` framework (Yao et al., 2023) interleaved thinking with acting, producing an agent that reasons, acts, observes, and reasons again.

Language model planning is radically different from classical planning. It is not guaranteed to be sound (the plan may not achieve the goal) or complete (it may not find a plan that exists). It can produce plans in domains where formal action models are unavailable — because it has learned the structure of many domains from text. It can generate creative, context-sensitive plans that no STRIPS model could encode. But it can also generate plans that contain hallucinated steps, logical contradictions, or actions that are physically impossible.

The 2040 state of the art combines classical and language-model planning in **neurosymbolic planners**: the language model generates an initial plan, a symbolic validator checks it for logical consistency and achievability, and if the plan fails validation, the model revises it. This hybrid approach (used in ÞingAI, LangChain's Plan-and-Execute, and AutoGen's GroupChat Planner) inherits the flexibility of LLM planning and the correctness guarantees of symbolic planning.

The Norse **runes** — symbols that encode both **meaning** and **magic** — are the ancient analogue of planning representations. A rune is not just a phoneme; it is a compressed representation of a concept, an action, and a consequence. ᚠ (Fehu) means "cattle" but also "wealth" and "mobile power." ᚢ (Úr) means "rain" but also "slag" and "prudent preparation." The runic system is a planning language: each rune encodes a precondition (what must be true), an action (what to do), and an effect (what will result) — not unlike a STRIPS operator. The runemaster who carves the runes is the planner who arranges the operators. The 2040 planner, like the runemaster, must choose the right symbols, arrange them in the right order, and trust that the web of wyrd will bring the plan to fruition.

**Key Topics:**

- STRIPS and classical planning: predicates, operators, soundness, completeness, intractability
- The closed-world assumption and why it fails in practice
- MDPs and POMDPs: stochastic outcomes, partial observability, belief states, policies
- Language model planning: chain-of-thought, ReAct, plan-generation without formal models
- Neurosymbolic planners: LLM generation + symbolic validation
- Runes as an ancient planning language: compressed representations with preconditions, actions, effects

**Required Reading:**

- Fikes, R.E. & Nilsson, N.J. "STRIPS: A New Approach to the Application of Theorem Proving to Problem Solving" (1971), *AIJ*
- Kaelbling, L.P., Littman, M.L. & Cassandra, A.R. "Planning and Acting in Partially Observable Stochastic Domains" (1998), *Artificial Intelligence*
- Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models" (2023), *ICLR*
- University of Yggdrasil TR: "Neurosymbolic Planning with ÞingAI: Combining LLM Generation with HTN Validation" (2040)

**Discussion Questions:**

1. Classical planning is sound and complete but intractable and assumes a closed world. LLM planning is flexible and scalable but unsound and incomplete. Neurosymbolic planning tries to combine the best of both. What are the failure modes of neurosymbolic planning? When would it be worse than either pure approach?
2. A POMDP models uncertainty about the world state. An LLM models uncertainty about what to do next. Are these the same kind of uncertainty? Should we use POMDP solvers for LLM planning problems, or are the uncertainty types fundamentally different?
3. Runes encode meaning, action, and consequence — a compressed planning representation. But the runic system had less than 30 symbols (the Elder Futhark). Modern STRIPS domains can have hundreds of operators. Is expressive power always better? What is lost when the planning language becomes too expressive?

---

### ᚬ Lecture 4: Execution Monitoring — Watching the Web While You Walk It

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A plan is a prediction. It predicts that if the agent takes action A1 in state S0, the world will transition to state S1; then if the agent takes action A2 in state S1, the world will transition to state S2; and so on until the goal state is reached. But predictions about the real world are never certain. The API that worked in testing may fail in production. The file that existed when the plan was made may have been moved by the time the agent reaches for it. The user who said "schedule a meeting for Thursday" may have meant "schedule a meeting for next Thursday" while the agent interpreted it as "schedule a meeting for this Thursday." **Execution monitoring** is the process of observing the world during plan execution and comparing observations to expectations, so that deviations can be detected and corrected before they cascade into total failure.

Execution monitoring addresses a fundamental problem: the world does not stand still while the agent executes its plan. The **dynamic world problem** has three dimensions:

**Environment dynamics.** The world changes independently of the agent. Files are created and deleted, APIs are updated and deprecated, network connections fluctuate, and other agents (human and artificial) are simultaneously modifying the environment. A plan that assumed the world was static is a plan that will encounter surprises.

**Action uncertainty.** The agent's actions have stochastic outcomes. The agent calls `deploy(service, "production")` and the deployment succeeds — or it fails with a timeout, or it partially succeeds leaving the service in an inconsistent state. Classical planners assume deterministic action effects; real agents must assume that any action can have any of several outcomes.

**Observation noise.** The agent's sensors are imperfect. When the agent checks whether a file exists, `os.path.exists()` returns True — but the file might have been deleted in the instant between check and use, or the check might return True due to a caching artifact. When the agent reads an API response, the response is correct — or it was cached and is now stale, or the network corrupted a byte, or the server is returning an error page that the agent's parser interprets as valid data. Observation noise means that the agent's model of the world may not match the world itself.

The classical approach to execution monitoring, formalized by Petrie (1987) and extended by De Giacomo, Reiter and Soutchanski (1998), is **plan recognition and execution monitoring**: the agent maintains an explicit model of the expected state after each action, compares the observed state to the expected state, and flags deviations. If the agent expects `(at robot room2)` after moving from room1 to room2, but observes `(at robot room1)`, the deviation is detected and the agent must diagnose and correct the failure.

The 2040 approach to execution monitoring extends this classical framework in three ways:

**Probabilistic monitoring.** Instead of flagging binary deviations (expected vs. observed), the agent maintains a probability distribution over possible states and updates it after each observation using a Bayesian filter. The agent does not ask "did the action succeed?" — a question that admits a binary answer that may be wrong — but "how likely is it that the action succeeded?" — a question that admits a nuanced answer that can inform downstream decisions. A deployment that returned a 500 error on one health check endpoint but 200 on nine others is probably mostly successful; the probabilistic monitor captures this nuance.

**Multi-scale monitoring.** The agent monitors at multiple levels of granularity simultaneously. At the **action level**, it checks whether the last action had the expected immediate effect. At the **plan level**, it checks whether the overall plan is making progress toward the goal. At the **meta level**, it checks whether the plan is still the right plan — whether the goal itself is still relevant. A deployment might succeed at the action level (each step completed successfully) but fail at the plan level (the deployment took so long that the version being deployed is now outdated) or the meta level (the feature being deployed was canceled while the deployment was in progress).

**Anomaly detection.** Not all deviations are explicitly monitored — the agent cannot predict every way that things might go wrong. Anomaly detection uses unsupervised or self-supervised methods to flag observations that are "unusual" relative to the agent's experience, even if the agent doesn't have a specific model of what went wrong. Techniques from statistical process control (control charts, CUSUM), time-series anomaly detection (ARIMA residuals, Isolation Forest), and language-model anomaly detection (the model flags observations it considers "surprising") all contribute to a multi-method monitoring system that can detect the unexpected as well as the expected.

The Norse concept of **Heimdallr** — the watchman of the gods, who stands at the Bifrost bridge and can see a hundred miles in every direction, who needs less sleep than a bird, who can hear grass growing and wool on sheep — is the mythological embodiment of execution monitoring. Heimdallr watches for threats that no one else can see, hears signals that no one else can detect, and sounds the Gjallarhorn when something is wrong. The autonomous agent's monitoring system is its Heimdallr: eternally vigilant, always comparing expectations to observations, always ready to sound the alarm. But unlike Heimdallr, who watches for a single known threat (the attack of the giants at Ragnarök), the agent's monitoring system must watch for unknown threats — deviations the agent did not predict and may not understand. This is the harder problem, and it is where anomaly detection becomes essential.

**Key Topics:**

- The dynamic world problem: environment dynamics, action uncertainty, observation noise
- Classical execution monitoring: expected state vs. observed state, binary deviation detection
- Probabilistic monitoring: Bayesian belief updates, nuance over binary success/failure
- Multi-scale monitoring: action level, plan level, meta level — different granularities of progress tracking
- Anomaly detection: flagging the unexpected without a specific model of what went wrong
- Heimdallr: the watchman who sees all, hears all, and sounds the alarm

**Required Reading:**

- Petrie, C. "Planning and Replanning in Reasoning About Actions" (1987), *AAAI*
- De Giacomo, G., Reiter, R. & Soutchanski, M. "Execution Monitoring of High-Level Robotics Programs" (1998), *ICRA*
- Chandola, V., Banerjee, A. & Kumar, V. "Anomaly Detection: A Survey" (2009), *ACM Computing Surveys*
- University of Yggdrasil TR: "Heimdallr Monitoring: Multi-Scale Execution Oversight for Autonomous Agents" (2040)

**Discussion Questions:**

1. Probabilistic monitoring provides nuance — "90% likely the deployment succeeded" rather than "deployment succeeded" or "deployment failed." But nuance comes at a cost: the agent must decide what probability threshold triggers corrective action. Is 90% confident enough to proceed? 95%? 99.9%? How should the threshold be set, and should it vary by the stakes of the decision?
2. Multi-scale monitoring requires the agent to evaluate progress at the action level, the plan level, and the meta level simultaneously. What happens when the levels disagree? The action level says "success" (the step completed), the plan level says "falling behind" (we're taking too long), and the meta level says "irrelevant" (the goal has changed). Which level takes priority?
3. Anomaly detection flags the unusual, but "unusual" is context-dependent. A deployment that completes in 2 seconds is unusual (and possibly suspicious) in one environment and normal in another. How should an agent learn what is unusual in its specific context, and how should it adapt its sense of normalcy as the context changes?

---

### ᚱ Lecture 5: Error Detection and Diagnosis — Finding the Root in Yggdrasil's Roots

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Monitoring detects that something is wrong. Diagnosis determines what is wrong and why. An agent that detects an error but cannot diagnose it is in the position of a doctor who can tell the patient is sick but cannot identify the disease — the patient knows there is a problem, but neither patient nor doctor can choose the right treatment. **Error diagnosis** is the bridge between detection and correction, and it is the step that most distinguishes a truly autonomous agent from a reactive system.

The fundamental challenge of diagnosis is the **multiple-fault problem**. When an action fails, there are many possible causes. A deployment failure could be caused by: (a) a syntax error in the configuration file, (b) an authentication failure at the registry, (c) a resource exhaustion on the target cluster, (d) a network partition between the registry and the cluster, (e) a version incompatibility in the container image, (f) a race condition between two concurrent deployments, or (g) any combination of the above. The agent must gather evidence, form hypotheses, test them, and converge on the correct diagnosis — all while the clock is ticking and the user is waiting.

The 2040 landscape offers four approaches to error diagnosis, each addressing different aspects of the problem:

**Structured Error Taxonomies.** Many domains have well-established error classification systems. HTTP status codes (4xx client errors, 5xx server errors), exit codes (0 for success, non-zero for various failures), and exception hierarchies (TypeError, ValueError, PermissionError) provide a first-pass diagnosis. The agent's first step in diagnosis is always to parse the error output and classify it using a taxonomy. A `403 Forbidden` response suggests an authentication or authorization problem; a `503 Service Unavailable` suggests a server-side capacity problem; a `0xC0000005` (access violation) suggests a memory corruption problem. Taxonomies are fast, cheap, and often sufficient for simple errors.

**Model-Based Diagnosis (MBD).** When the error taxonomy is insufficient — when the error is "something went wrong" without a clear classification — the agent can reason from a model of the system. MBD (Reiter, 1987; de Kleer & Williams, 1987) formalizes diagnosis as the identification of components whose failure would explain the observed behavior. Given a model of the system (each component's normal and faulty behavior) and an observation that conflicts with the model's prediction, MBD computes the minimal set of components whose failure accounts for the conflict. The agent's model of the deployment pipeline — registry, network, cluster, configuration, container — can be used to trace a deployment failure to the specific component that caused it. MBD is powerful but requires an explicit model of the system, which may not be available.

**LLM-Based Diagnosis.** When no explicit model is available, the agent can use a language model to diagnose the error. The agent provides the error output, the relevant context (what it was trying to do, what the expected behavior was, what actually happened), and asks the LLM to identify the most likely cause and suggest a correction. LLM-based diagnosis is flexible — it can diagnose errors in domains the agent has never seen before, based on the model's broad knowledge of software, systems, and common failure modes. But LLM-based diagnosis is also unreliable — the model may hallucinate causes, suggest corrections that don't work, or confidently produce a plausible but wrong diagnosis. The 2040 best practice is to use LLM-based diagnosis as a hypothesis generator, then validate the hypothesis by testing it (trying the suggested correction and observing the result).

**Experience-Based Diagnosis.** Over time, the agent accumulates a history of errors and their diagnoses. The next time the agent encounters a similar error, it can retrieve the most similar past case from its episodic memory (see AI303) and apply the past diagnosis to the present situation. Experience-based diagnosis (also called case-based reasoning, Kolodner, 1993) is fast and reliable for errors the agent has seen before, but it cannot diagnose novel errors — those that don't match any past case. The 2040 hybrid approach (used in ÞingAI's diagnostic module) combines experience-based diagnosis for known errors with LLM-based diagnosis for novel errors, using the diagnostic history as a validation set for LLM hypotheses.

The diagnostic process operates in a **diagnostic loop**, analogous to the scientific method but applied to software and systems:

1. **Observe** the error (parse the error output, note the context)
2. **Hypothesize** one or more possible causes (using taxonomy, model, LLM, or experience)
3. **Test** the hypothesis (run a diagnostic command, check a log, attempt a fix)
4. **Evaluate** the test result (did the hypothesis explain the observation?)
5. **Refine** the hypothesis (if the test confirmed, proceed to correction; if not, form a new hypothesis)

The diagnostic loop terminates when a hypothesis is confirmed, when the agent runs out of hypotheses (and escalates to the user), or when the time budget for diagnosis is exhausted (and the agent must choose the best available hypothesis or abort the task). The time budget is critical: an agent that spends hours diagnosing a trivial error is almost as useless as an agent that can't diagnose at all.

The Norse concept of **Yggdrasil's roots** illustrates the diagnostic challenge. Yggdrasil, the world-tree, has three roots: one in Asgard (the realm of the gods), one in Jotunheim (the realm of the giants), and one in Niflheim (the realm of the dead). Each root is tended by a well: Urðarbrunnr (the well of fate), Mímisbrunnr (the well of wisdom), and Hvergelmir (the roaring cauldron). When Yggdrasil shows signs of distress — its leaves wither, its trunk groans — the wise seek the cause not at the trunk but at the roots. The rot in one root can manifest as disease in the canopy, far from the actual source. Error diagnosis is the art of tracing the surface symptom to its root cause — the rot in the well that manifests as the withered leaf. An agent that treats the symptom without finding the root cause will see the same error recur, like a gardener who treats yellow leaves with fertilizer while the roots are drowning.

**Key Topics:**

- Diagnosis as the bridge between detection and correction
- The multiple-fault problem: many possible causes for any given symptom
- Structured error taxonomies: HTTP codes, exit codes, exception hierarchies
- Model-Based Diagnosis (MBD): reasoning from system models to identify faulty components
- LLM-Based Diagnosis: flexible but unreliable, best used as hypothesis generator
- Experience-Based Diagnosis (case-based reasoning): fast for known errors, blind to novel ones
- The diagnostic loop: observe → hypothesize → test → evaluate → refine
- Yggdrasil's roots: tracing surface symptoms to root causes

**Required Reading:**

- Reiter, R. "A Theory of Diagnosis from First Principles" (1987), *Artificial Intelligence*
- de Kleer, J. & Williams, B.C. "Diagnosing Multiple Faults" (1987), *Artificial Intelligence*
- Kolodner, J. *Case-Based Reasoning* (1993), Morgan Kaufmann
- University of Yggdrasil TR: "Root Cause Analysis in Autonomous Agents: From Symptom to Source" (2040)

**Discussion Questions:**

1. The diagnostic loop can run indefinitely if every hypothesis is rejected and new hypotheses are generated. What is a principled way to set the time budget for diagnosis? How should the agent trade off diagnostic thoroughness against task completion speed?
2. Experience-based diagnosis is fast for known errors but blind to novel ones. LLM-based diagnosis is flexible but unreliable. The hybrid approach uses experience to validate LLM hypotheses. But what if the experience base contains errors — misdiagnoses from the past that lead the agent astray? How should the agent handle a corrupted experience base?
3. Yggdrasil's three roots connect to three different realms — the symptom manifests in one realm, but the cause may be in another. In software systems, the symptom often manifests at the interface (the web server returns 500) while the cause is deep in the infrastructure (the database is out of disk space). How should the diagnostic process navigate between layers of abstraction — from interface symptom to infrastructure root cause?

---

### ᚴ Lecture 6: Recovery Strategies — Mjölnir Always Returns to the Hand

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Once the agent detects an error and diagnoses its cause, it must **recover** — choose and execute a corrective action that returns the agent to a state from which progress toward the goal is possible. Recovery is the third and final stage of the self-correction cycle (after detection and diagnosis), and it is where the rubber meets the road: a perfect diagnosis is useless if the agent cannot act on it.

Recovery strategies form a hierarchy from simple to complex, from local to global, from cheap to expensive:

**Retry.** The simplest recovery strategy: try the same action again. Many errors are transient — a network timeout, a brief service outage, a momentary resource contention. If the error is transient, retrying after a short delay will succeed. The retry strategy needs a **backoff policy** — how long to wait before retrying, and how many times to retry before giving up. Exponential backoff (wait 1 second, then 2, then 4, then 8...) with jitter (add a random delay to avoid synchronized retries from multiple agents) is the standard pattern. Retry is reflexive, nearly zero-cost, and should always be the first response to any error.

**Parameter adjustment.** If retry fails, the error may not be transient — it may be caused by incorrect parameters. The agent diagnoses that the error is a `400 Bad Request` response, infers that the request parameters are wrong, and adjusts them: changing the timeout from 5 to 30 seconds, reducing the batch size from 1000 to 100, using a different authentication token. Parameter adjustment requires the agent to understand which parameters are relevant to the error and which adjustments are likely to fix it. This understanding can come from a domain model (the configuration schema specifies valid ranges), from experience (past similar errors were resolved by increasing the timeout), or from LLM reasoning (the model suggests adjusting the batch size based on its understanding of the system).

**Alternative path.** If the current action cannot be made to succeed, the agent may have an alternative action that achieves the same sub-goal. If `deploy(service, "production")` fails, the agent might try `deploy(service, "staging")` first to validate the deployment, then promote staging to production. If `search(api="Google")` fails, the agent might try `search(api="Bing")`. Alternative paths are specified in the plan (the HTN or behavior tree may have alternative methods) or generated on the fly by the LLM planner. Alternative paths are more expensive than retries or parameter adjustments but less expensive than full replanning.

**Replanning.** If the current sub-goal cannot be achieved by any available action, the agent replans: it returns to the planner with the current state (which may differ from the expected state because of the error) and asks for a new plan that achieves the original goal from the current state. Replanning is the most expensive recovery strategy — it requires a full invocation of the planning system — but it is also the most powerful, because it can address fundamental plan failures where no minor adjustment will suffice. The key challenge in replanning is ensuring that the new plan does not repeat the mistake that caused the old plan to fail — the agent must provide the planner with the diagnostic information (what went wrong and why) so that the new plan avoids the same failure mode.

**Escalation.** If the agent cannot recover by any of the above strategies — the error exceeds the agent's capacity for self-correction — it must escalate to a human. Escalation is not failure; it is **bounded autonomy** — the agent recognizes its limitations and seeks help. The agent's escalation message should include: (a) what it was trying to do, (b) what happened instead, (c) what it tried to correct the error, (d) what the results of those attempts were, and (e) what it needs from the human. A well-crafted escalation message reduces the human's cognitive burden and speeds resolution. A poorly crafted one ("Something went wrong. Please help.") wastes the human's time and erodes trust.

The Norse myth of **Mjölnir**, Thor's hammer, provides the archetypal model of recovery: Mjölnir always returns to Thor's hand. When Thor throws Mjölnir at a giant, the hammer flies true, strikes the target, and then returns — no matter what obstacles intervene. This is not merely a magic property; it is a design principle. Mjölnir is designed to recover. It does not get stuck in the target, it does not veer off course, it does not fail to return. In the same way, a well-designed recovery strategy should always return the agent to a known-good state from which execution can continue. The hammer always returns.

But even Mjölnir has limits. In the myth of Þrymskviða, Thor's hammer is stolen by the giant Þrymr, and Thor must resort to a dramatically different strategy — disguising himself as the goddess Freyja, attending the giant's wedding, and seizing the hammer when it is brought out to bless the marriage. This is not a retry or a parameter adjustment; it is a full replan — and a creative one at that. The lesson: when the obvious recovery strategies fail, the agent must be prepared to fundamentally rethink its approach, not just try harder with the same approach.

**Recovery budget.** A critical design decision for any autonomous agent is the **recovery budget**: how much time, compute, and money the agent is allowed to spend on self-correction before it must either succeed or escalate. A recovery budget prevents the agent from entering an infinite loop of diagnosis and correction — spending hours retrying a failing deployment, or burning through dollars of LLM API costs trying to diagnose an obscure error. The recovery budget should be proportional to the **stakes** of the task: a low-stakes task (sending a notification) gets a small budget; a high-stakes task (deploying a critical security update) gets a larger budget. The budget should also decay: the first few correction attempts get more time and resources than later attempts, because the probability of successful correction decreases with each failure.

**Key Topics:**

- Recovery hierarchy: retry → parameter adjustment → alternative path → replanning → escalation
- Retry strategies: exponential backoff with jitter, transient vs. persistent errors
- Parameter adjustment: domain models, experience, LLM reasoning for choosing adjustments
- Alternative paths: HTN methods, behavior tree selectors, on-the-fly path generation
- Replanning: full plan regeneration with diagnostic information to avoid repeated failures
- Escalation: bounded autonomy, well-crafted escalation messages
- Mjölnir as recovery metaphor: always return to a known-good state
- Þrymskviða: the creative replan when obvious recovery strategies fail
- Recovery budget: time, compute, and money proportional to task stakes

**Required Reading:**

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4th ed., 2020), Chapter 4 (Search) and Chapter 12 (Quantifying Uncertainty)
- Brafman, R.I. & Tennenholtz, M. "R-MAX — A General Polynomial Time Algorithm for Near-Optimal Reinforcement Learning" (2002), *JMLR*
- University of Yggdrasil TR: "Mjölnir Recovery: Hierarchical Self-Correction Strategies for Autonomous Task Execution" (2040)

**Discussion Questions:**

1. The recovery hierarchy suggests trying cheap strategies first (retry) and expensive strategies later (replanning). But cheap strategies can be wasteful if the error is not transient — retrying a deployment that fails because of a syntax error in the configuration file wastes time without any chance of success. How should the agent decide whether an error is likely transient (retry) or likely persistent (skip retry and go to diagnosis)?
2. Escalation is bounded autonomy — the agent asks for help when it can't fix the problem itself. But what if no human is available? Should the agent abort the task entirely, or should it try a radical creative strategy (like Thor in Þrymskviða) that has a low probability of success but might work? How should the agent weigh the risk of a creative but unreliable strategy against the certainty of failure?
3. The recovery budget decays over time — later correction attempts get fewer resources. But what if the first few attempts use up the budget on transient errors, leaving insufficient budget for the more thorough diagnosis that a persistent error requires? Should the budget be re-initialized after a strategy change (from retry to diagnosis)?

---

### ᚻ Lecture 7: Replanning — When the Norns Rewrite Fate

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Replanning is the agent's admission that its original plan was wrong. Not just a step that failed, but a plan that — given what the agent now knows — cannot succeed. The agent must abandon its current plan and generate a new one from the current state. Replanning is the most radical corrective action available to the agent: it discards all or most of the original plan and starts fresh, constrained by the goal and the current state but unbound by the previous plan's assumptions.

Replanning is not failure. It is *learning*. The agent tried a plan, observed the world's response, learned that the plan's assumptions were incorrect, and generated a new plan that accounts for those corrections. An agent that never replans is an agent that never learns from execution; an agent that replans well is an agent that turns every failure into a lesson.

The fundamental question of replanning is: **how much of the original plan should be preserved?** The replanning spectrum ranges from conservative to radical:

**Local replanning.** Only the failed step and its immediate successors are replaced. The rest of the plan is preserved. If step 7 of a 15-step plan fails, the agent replans steps 7–9 (the local sub-plan) and leaves steps 1–6 and 10–15 intact. Local replanning is fast and preserves the most of the original investment, but it risks preserving steps that are also affected by the failure — the failure of step 7 may have invalidated the assumptions behind steps 10–15, and preserving them may lead to cascade failures.

**Global replanning.** The entire plan is discarded and regenerated from the current state. Global replanning is the most expensive option — it requires a full invocation of the planner — but it avoids the risk of preserving invalidated assumptions. The cost of global replanning depends on the planner: with a language model, global replanning takes seconds to minutes; with a classical planner on a complex domain, it can take hours.

**Progressive replanning.** A compromise: the agent preserves the *goals* and *sub-goals* of the original plan but regenerates the *actions* for each sub-goal from the current state. This approach recognizes that the original decomposition (task → sub-tasks) may still be valid even if the specific actions within each sub-task need to change. Progressive replanning is faster than global replanning (the decomposition is reused) and more flexible than local replanning (the actions are regenerated).

The 2040 replanning architecture, as implemented in ÞingAI Planner v3, uses a **spectrum rebuilder**: the agent begins with local replanning (cheapest) and escalates progressively to global replanning (most expensive) if local replanning fails. Each level of replanning has its own budget: the agent tries local replanning up to 3 times, progressive replanning up to 2 times, and global replanning once before escalating to the user. The spectrum approach ensures that cheap strategies are tried first but radical strategies remain available when cheap ones fail.

**Replanning with diagnostic information.** A critical design principle: the replanner should receive the diagnostic information gathered during the failed execution. Without this information, the replanner is likely to generate a plan with the same flaw as the original. The diagnostic information includes: (a) what the agent was trying to do, (b) what went wrong, (c) what was diagnosed as the root cause, (d) what correction was attempted, and (e) what the result of the correction was. In ÞingAI, this information is passed to the replanner as a **failure context**: a structured summary that the replanner uses to avoid the same mistake.

The representation of the failure context is crucial. A natural-language description ("The deployment failed because the Docker image tag 'v2.3.1' does not exist in the registry") is informative for an LLM-based replanner but not directly processable by a symbolic planner. A structured representation (`[action: push_image, params: {tag: "v2.3.1"}, outcome: failure, diagnosis: {type: image_not_found, registry: "ghcr.io", tag: "v2.3.1"}}]`) is processable by both. The 2040 best practice is to maintain both representations, using the structured form for symbolic validation and the natural-language form for LLM reasoning.

**Replanning and commitment.** A misconception about replanning is that it means the agent is uncommitted — flitting from plan to plan without sustained effort. In fact, the opposite is true. An agent that replans is committed to the *goal*, not the *plan*. It is willing to change its approach when the approach fails, but it does not abandon the goal. This is the distinction between **goal commitment** (persistence in achieving the outcome) and **plan commitment** (persistence in following the current plan). The autonomous agent should have high goal commitment and moderate plan commitment — it tries hard to make the current plan work, but when the plan is clearly broken, it switches to a new plan rather than persisting in a doomed approach.

The Norse **Norns** — Urðr (what has been), Verðandi (what is becoming), and Skuld (what shall be) — sit at the base of Yggdrasil and weave the web of wyrd. They do not determine a fixed destiny; they weave, and the weave can be changed. When the agent replans, it is not rewriting fate — it is reweaving its part of the web. The original plan was the agent's best guess at how to move through the web of wyrd. When the world revealed that this guess was wrong, the agent must re-see the web from its new position and choose a new path. The Norns, who see past, present, and future simultaneously, understand that every replan is both a correction and a new beginning — the agent's past choices are preserved in Urðr, its current situation in Verðandi, and its new plan in Skuld.

**Key Topics:**

- Replanning as learning: the agent discards invalid assumptions and generates new plans
- The replanning spectrum: local (preserve most of plan), progressive (preserve goals), global (regenerate entirely)
- Spectrum rebuilder in ÞingAI: cheap strategies first, radical strategies when cheap ones fail
- Failure context: passing diagnostic information to the replanner to avoid repeated mistakes
- Dual representation: structured failure context for symbolic planners, natural-language for LLM planners
- Goal commitment vs. plan commitment: persistence in the outcome, flexibility in the approach
- The Norns: Urðr (past), Verðandi (present), Skuld (future) — replanning as reweaving the web

**Required Reading:**

- Gervasio, M. & Iba, W. "Experiences with Iterative Repair Planning in a Flexible Schedule" (1997), *AAAI*
- Fox, M. & Long, D. "PDDL2.1: An Extension to PDDL for Expressing Temporal Planning Domains" (2003), *JAIR*
- University of Yggdrasil TR: "Norn Replanning: Spectrum-Based Plan Recovery with Diagnostic Context" (2040)

**Discussion Questions:**

1. Local replanning preserves existing plan steps, but these steps may be based on assumptions invalidated by the failure. How can the agent determine which remaining steps are still valid and which need to be regenerated? Is there a principled way to compute the "ripple effect" of a failure on future steps?
2. Goal commitment without plan commitment sounds ideal. But what if the goal itself was based on incorrect assumptions? For example, the goal "deploy v2.3.1 to production" is based on the assumption that v2.3.1 is the correct version — an assumption that may be wrong. Should replanning also reconsider the goal? At what point does goal commitment become stubbornness?
3. The Norns see past, present, and future simultaneously. An agent can see the past (episodic memory) and the present (current observations) but can only predict the future. How should the agent handle situations where multiple futures are possible and the replanner must prepare for all of them?

---

### ᚾ Lecture 8: Feedback Loops and Iterative Refinement — The Dwarven Forge

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Self-correction is not a one-time event. An agent that detects an error, diagnoses it, corrects it, and proceeds is using self-correction in the simplest sense: fix the problem and move on. But most real-world tasks require **iterative refinement** — the agent produces a draft, evaluates it, revises it, evaluates the revision, revises again, and so on until the result meets the quality threshold. Software development, writing, design, planning — all of these are iterative processes where the first attempt is rarely the final one, and each iteration improves the result based on feedback from the previous one.

The **feedback loop** is the mechanism that drives iterative refinement. A feedback loop consists of four components:

**Output.** The agent produces a draft — a piece of code, a document, a plan, an analysis. The draft is the agent's best attempt given its current knowledge and capabilities, but it is not expected to be perfect.

**Evaluation.** The draft is evaluated against criteria. The evaluation can be performed by the agent itself (self-evaluation), by an external system (a test suite, a linter, a validator), by another agent (a reviewer, a critic, a tester), or by the user. The evaluation produces feedback — a description of what is wrong with the draft, what is missing, what could be improved.

**Refinement.** The agent revises the draft based on the feedback. The refinement can be targeted (fix the specific issues identified by the evaluation) or holistic (rethink the entire approach based on the evaluation). Targeted refinement is more efficient; holistic refinement is more likely to produce breakthrough improvements.

**Termination.** The loop terminates when the draft meets the quality threshold (all tests pass, the validator approves, the user is satisfied) or when the iteration budget is exhausted (the agent has spent the maximum allowed time or compute without reaching the threshold). Termination conditions are critical: a loop without a termination condition can run forever.

The 2040 landscape offers several architectures for iterative refinement:

**Code Generation Loops.** The most mature and widely deployed iterative refinement architecture is the code generation loop: the agent generates code, the test suite evaluates it, the agent reads the test failures and revises the code, the revised code is tested again, and so on. The **SWE-bench** benchmark (Jimenez et al., 2023) demonstrated that language models could solve real-world GitHub issues by generating code, running tests, reading error messages, and revising. By 2040, code generation loops have become standard practice in autonomous software engineering — the agent runs in a loop of (generate → test → revise → test) until all tests pass or the budget is exhausted.

**Writing Refinement Loops.** The agent generates a document, evaluates it against criteria (clarity, completeness, accuracy, style), revises based on the evaluation, and repeats. The evaluation can be performed by the same model (self-evaluation) or by a specialized critic model (e.g., a model trained on editorial feedback). Writing refinement loops are particularly challenging because the evaluation criteria are subjective — there is no test suite that definitively determines whether a paragraph is "clear" or "persuasive." The 2040 approach uses rubric-based evaluation: the critic evaluates the document against a rubric with specific criteria (e.g., "The introduction states the thesis clearly," "Each paragraph has a topic sentence," "The conclusion summarizes the argument") and the writer revises to address the rubric scores.

**Planning Refinement Loops.** The agent generates a plan, validates it against domain constraints, revises it, validates again, and repeats. The validator can be a symbolic planner (checking that all preconditions are satisfied), a simulator (checking that the plan produces the expected outcome in a simulated environment), or a human reviewer (checking that the plan makes sense in the real world). Planning refinement loops are the natural extension of the PEOEDA cycle (Lecture 1) from a single pass to an iterative process.

**Multi-Agent Refinement Loops.** Multiple agents participate in the refinement process: a generator agent produces the draft, a critic agent evaluates it, a reviser agent incorporates the feedback, and an editor agent makes final polish. The multi-agent architecture, studied in AI301, provides specialization (each agent is optimized for its role) and adversarial robustness (the critic is incentivized to find flaws, not to approve). The ÞingAI framework uses a **Forge architecture** — named for the dwarven forge (dvergasmíðja) where master smiths collaborated to create artifacts of extraordinary quality — with separate generator, critic, reviser, and editor agents.

The Norse **dwarven forge** — the workshop where the dwarves (dvergar) crafted the treasures of the gods — illustrates the iterative refinement principle. The dwarves did not create Gungnir (Odin's spear) in a single strike. They worked the metal, heated it, hammered it, cooled it, examined it, found flaws, reheated it, rehammered it, and repeated the process until the spear was perfect — it never missed its mark. Each iteration of the forge improved the product: the first draft was rough, the second was better, and the final version was divine. The dwarves' iterative process is mythological precedent for the engineering practice of iterative refinement: produce, evaluate, revise, repeat until the quality threshold is met.

**Failure modes of the feedback loop.** Not all feedback loops converge. The most common failure modes are:

**Oscillation.** The agent alternates between two states: revision A is criticized for fault X, the agent revises to fix X, revision B is criticized for fault Y (which was introduced by the fix for X), the agent revises to fix Y, revision A' is criticized for fault X again... Oscillation occurs when the evaluation criteria are contradictory or the feedback is inconsistent. The solution is to detect oscillation (if the current revision is semantically similar to a revision from 2+ iterations ago, the loop is oscillating) and to break it by changing the revision strategy.

**Drift.** Each revision changes the draft slightly, and over many iterations, the draft drifts away from the original goal. The agent starts by writing a summary of a research paper and, after ten iterations of refinement, has produced a critique of the paper's methodology. Drift occurs when the feedback is not anchored to the original goal. The solution is to include the original goal as a fixed reference in each iteration and to evaluate not just the current draft but the draft's *distance from the original goal*.

**Diminishing returns.** Each revision produces smaller improvements until further iterations are not worth the compute cost. This is expected and not a failure — the agent should detect diminishing returns (the improvement per iteration falls below a threshold) and terminate the loop, even if the quality threshold has not been perfectly met.

**Key Topics:**

- Feedback loops: output → evaluation → refinement → termination
- Code generation loops: generate → test → revise → test
- Writing refinement loops: rubric-based evaluation for subjective criteria
- Planning refinement loops: generate → validate → revise → validate
- Multi-agent refinement: generator, critic, reviser, editor (the Forge architecture)
- The dwarven forge: iterative creation until the artifact meets divine quality
- Failure modes: oscillation, drift, diminishing returns — and how to handle each

**Required Reading:**

- Jimenez, C.E. et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (2023), *ICLR*
- Madaan, A. et al. "Self-Refine: Iterative Refinement with Self-Feedback" (2023), *NeurIPS*
- University of Yggdrasil TR: "The Forge Architecture: Multi-Agent Iterative Refinement for Autonomous Software Engineering" (2040)

**Discussion Questions:**

1. Oscillation occurs when feedback is contradictory — revision A is criticized for fault X, revision B fixes X but introduces Y, revision A' reintroduces X. How should the agent detect oscillation? One approach is to compare the current revision to previous revisions for semantic similarity. Another is to track the evaluation scores: if they oscillate rather than monotonically improve, the loop is oscillating. What are the trade-offs of each approach, and can they be combined?
2. Drift is particularly dangerous in long refinement loops with subjective criteria. A writing loop might start with "write a technical summary" and drift toward "write an opinionated critique." How can the agent anchor its revisions to the original goal without stifling creative improvements that genuinely enhance the output?
3. The dwarven forge produced artifacts of divine quality — Gungnir, which never misses; Draupnir, which multiplies; Mjölnir, which always returns. But each of these artifacts was created by a team of specialized dwarves, not a single craftsman. Is the multi-agent Forge architecture — with separate generator, critic, reviser, and editor — inherently superior to a single-agent refinement loop? What are the coordination costs?

---

### ᛁ Lecture 9: Robustness and Graceful Degradation — The Longship in the Storm

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A system that works perfectly under normal conditions but collapses catastrophically when conditions deviate from the norm is not robust — it is fragile. **Robustness** is the ability of a system to maintain acceptable performance under adverse conditions: when resources are scarce, when the network is unreliable, when the user's instructions are ambiguous, when the world changes unpredictably. Robustness is not the same as correctness — a robust system may not produce the optimal output under adverse conditions, but it produces *some* useful output, rather than failing entirely. The related concept of **graceful degradation** is the property that system performance declines gradually as conditions worsen, rather than collapsing abruptly.

The distinction between fragility and robustness is best illustrated by example. Consider two agent architectures for a meeting scheduler:

**Fragile architecture.** The agent generates a plan, calls the Calendar API to find available times, calls the Email API to send invitations, calls the Chat API to notify attendees, and calls the Database API to record the meeting. If any one of these APIs is unavailable, the agent fails entirely — it cannot schedule the meeting, cannot notify the attendees, and cannot record the result. The agent produces either a perfect outcome (all APIs available, all steps succeed) or nothing (any API failure cascades to total failure).

**Robust architecture.** The agent generates a plan with fallbacks at each step. If the Calendar API is unavailable, it uses the user's manual schedule to propose times. If the Email API is unavailable, it falls back to the Chat API to send invitations. If the Chat API is also unavailable, it generates the invitation text and saves it for later delivery. If the Database API is unavailable, it writes the meeting details to a local file and queues a background sync. The robust architecture cannot produce the optimal outcome (all APIs available) under adverse conditions, but it can produce a *useful* outcome — a meeting scheduled, attendees notified (at least eventually), and a record preserved. The performance degrades gradually: first-class service when all APIs are available, adequate service when some are unavailable, minimal service when most are unavailable.

The 2040 principles of robust agent design are:

**Redundancy.** Every critical resource should have a fallback. If the primary API is unavailable, the agent should have a secondary API or a local alternative. If the primary LLM model is unavailable, the agent should be able to fall back to a smaller, faster model. Redundancy adds complexity and maintenance cost, but it prevents single points of failure. The Norse longship (langskip) carried redundant systems: multiple sails, multiple oarsmen, a steersman and a navigator, and emergency provisions. If one system failed, the ship could still function — it might be slower, less maneuverable, or less comfortable, but it would reach its destination.

**Fallback hierarchies.** Not all fallbacks are equal. The Calendar API provides real-time availability; the user's manual schedule provides approximate availability; proposing a default time provides a guess. The agent should have a clear **fallback hierarchy**: try the best option first, fall back to the second-best if the best fails, fall back to the third if the second fails, and so on until a minimally acceptable option is reached. The fallback hierarchy should be designed so that each successive fallback provides less service but still provides *something* — the agent never produces nothing.

**Timeout and circuit breaker patterns.** An agent that waits indefinitely for a response from an unavailable service is not robust — it is stuck. The **timeout** pattern limits the time the agent waits for a response; after the timeout expires, the agent moves to the fallback. The **circuit breaker** pattern (Hystrix, 2012; Resilience4j, 2038) goes further: after N consecutive failures, the circuit breaker opens and the agent *immediately* falls back without even trying the primary service. After a cooldown period, the circuit breaker closes and the agent tries the primary service again. Circuit breakers prevent cascading failures — if the primary service is down, the agent doesn't waste time and resources repeatedly trying it.

**State preservation across failures.** An agent that loses all progress when a step fails is fragile — it must start over from the beginning, wasting all the work it completed before the failure. A robust agent preserves its state at each step: if it has completed steps 1–6 and step 7 fails, it can resume from step 7 after the failure is corrected, rather than restarting from step 1. **Checkpointing** is the technique of saving the agent's state at key points in the execution so that it can resume from the last checkpoint after a failure. The 2040 ÞingAI executor checkpoints after every tool call, every API request, and every state transition, enabling resumption from any checkpoint without re-executing completed steps.

**Degraded mode operation.** When the agent cannot achieve the user's goal, it should still provide whatever value it can. If the agent cannot schedule a meeting (because the Calendar API is down entirely), it should not silently fail — it should explain the situation to the user, suggest alternatives ("I can't access the calendar right now, but I've drafted an email proposing Thursday at 2pm — would you like me to send it when the calendar comes back online?"), and queue follow-up actions for when the service is restored. Degraded mode operation is the difference between an agent that is useless when things go wrong and an agent that is *less useful* but still helpful.

The Norse **longship** (langskip) embodies robust assembly design. The longship was a vessel built for the open ocean — a dangerous, unpredictable, and unforgiving environment. It had a shallow draft for navigating rivers and fjords, a keel for open-ocean stability, sail and oars for redundant propulsion, and a hull flexible enough to ride waves without breaking. The longship did not conquer the ocean by being invincible; it *endured* the ocean by being resilient — flexing with the waves, adapting to the wind, and giving the crew time to respond to changing conditions. The robust agent, like the longship, is not designed for perfect conditions but for the worst conditions — because the worst conditions are when robustness matters most.

**Key Topics:**

- Robustness vs. correctness: acceptable performance under adverse conditions, not perfect performance under ideal conditions
- Graceful degradation: performance declines gradually, not abruptly
- Redundancy: fallback resources for every critical dependency
- Fallback hierarchies: best option first, progressively degraded alternatives
- Timeout and circuit breaker patterns: preventing indefinite waits and cascading failures
- State preservation across failures: checkpointing and resumption
- Degraded mode operation: providing partial value when full value is impossible
- The longship: resilient design for the worst conditions

**Required Reading:**

- Nygard, M. *Release It! Design and Deploy Production-Ready Software* (2nd ed., 2018), Pragmatic Bookshelf
- Lyons, R. *Understanding Distributed Systems* (2022), Roberto Lyons
- University of Yggdrasil TR: "Longship Design: Robust Autonomous Execution in Adverse Environments" (2040)

**Discussion Questions:**

1. Redundancy adds complexity and maintenance cost. Every fallback must be tested, documented, and maintained. At what point does the cost of redundancy exceed the benefit? How should the agent designer decide which resources need fallbacks and which are acceptable single points of failure?
2. Circuit breakers prevent cascading failures by short-circuiting calls to known-failing services. But what if the service is failing intermittently — it works sometimes and fails other times? Should the circuit breaker stay open (never trying the primary service) or closed (always trying, even though it often fails)? What is the right balance between resilience and efficiency?
3. Degraded mode operation sounds appealing, but it can be confusing for users. If the agent says "I scheduled a meeting but couldn't send invitations," the user may not know whether the meeting is actually scheduled or whether the whole thing failed. How should the agent communicate the difference between "full success" and "partial success with caveats"?

---

### ᛃ Lecture 10: Adaptive Learning from Execution — The Runes on the Staff

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Self-correction is reactive: the agent detects an error, diagnoses it, and corrects it. **Adaptive learning from execution** is proactive: the agent recognizes patterns in its errors and corrections, and modifies its future behavior to avoid similar errors. An agent that corrects the same error ten times but never learns to prevent it is self-correcting but not self-improving. Adaptive learning transforms self-correction from a cost (each error requires detection, diagnosis, and correction) into an investment (each error teaches the agent how to avoid similar errors in the future).

The 2040 framework for adaptive learning from execution has four stages:

**Error pattern recognition.** The agent's episodic memory (see AI303) records every error, diagnosis, and correction. Over time, patterns emerge: the same type of error recurs, the same diagnostic procedure is applied, and the same correction is effective. Pattern recognition algorithms (clustering, frequent subsequence mining, association rule learning) identify these recurring patterns and abstract them into **error schemas**: structured representations of characteristic error types, their typical causes, their typical corrections, and their typical prevention strategies. An error schema for "API timeout" might encode: "API timeouts are typically caused by server overload or network congestion. The typical correction is retry with backoff. The typical prevention is to add a preemptive health check before the API call."

**Correction strategy learning.** Each time the agent applies a correction strategy (retry, parameter adjustment, alternative path, replanning, escalation), it records whether the strategy was effective, how long it took, and how much it cost. Over time, the agent learns which strategies are most effective for which error types. This meta-learning produces a **strategy selection policy**: given an error of type X, apply strategy Y first because it has the highest expected effectiveness-to-cost ratio. The policy is updated continuously as new experience accumulates — if retry becomes less effective (because the API is increasingly timing out), the policy shifts to alternative path or replanning.

**Plan template learning.** When the agent generates a plan, executes it, and the plan fails in a predictable way, the agent has learned that this plan template is unreliable in this context. The agent can modify the plan template to incorporate pre-emptive corrections: adding a health check before the API call, increasing the timeout threshold, choosing the alternative path proactively rather than waiting for the primary path to fail. The modified plan template is stored in procedural memory (see AI303) for future use. Over time, the agent's plan templates become increasingly robust — they anticipate and pre-empt the errors that the agent has encountered in the past.

**Environmental model learning.** The deepest form of adaptive learning modifies the agent's model of the environment. If the agent consistently encounters unexpected outcomes in a specific context (e.g., the production API always times out between 2pm and 4pm on weekdays), the agent updates its environmental model to reflect this regularity. The updated model then influences planning (the agent avoids scheduling API calls during peak hours) and monitoring (the agent is not surprised when the API times out during peak hours). Environmental model learning is the most powerful form of adaptive learning — it enables the agent to anticipate problems before they occur, rather than merely correcting them after they occur.

The Norse concept of **runes on the staff** (rúnakefli) illustrates adaptive learning. The rune staff was a wooden stick inscribed with runic messages — not just any messages, but messages that encoded accumulated wisdom about the world. A seafarer's rune staff might encode: "When the wind shifts from the north at dawn, expect storms by midday." A farmer's rune staff might encode: "When the first frost comes in October, the harvest must be complete." These are not observations of the moment; they are learned patterns — generalizations from years of experience about the regularities of the world. The agent's error schemas, strategy policies, and plan templates are its rune staffs: inscribed records of what it has learned about how the world works, distilled from experience, and applied to future decisions.

The 2040 architecture for adaptive learning in ÞingAI follows the **rúnakefli pattern**:

1. **Record.** Every execution (successful and unsuccessful) is recorded in episodic memory with full detail: what was planned, what was attempted, what happened, what was diagnosed, what was corrected, and what the outcome was.

2. **Abstract.** The learning engine periodically scans episodic memory for patterns — recurring errors, effective corrections, predictable environmental regularities. Abstracted patterns are stored as error schemas, strategy policies, and plan templates in procedural memory.

3. **Apply.** When the agent next plans a task, it consults its learned schemas, policies, and templates. If the current context matches a known pattern, the agent applies the learned pre-emptive correction: adding the health check, increasing the timeout, avoiding the peak hours.

4. **Evaluate.** The agent monitors whether the applied learning was effective. If the pre-emptive correction prevented the predicted error, the learning is reinforced. If the predicted error did not occur but the pre-emptive correction was unnecessary (the error would not have occurred anyway), the learning is weakened — it may have been a spurious pattern.

5. **Revise.** Based on evaluation, the agent revises its schemas, policies, and templates. Patterns that are consistently reinforced are strengthened; patterns that are consistently weakened or that are no longer relevant (the environment has changed) are pruned.

The rúnakefli pattern ensures that adaptive learning is not a one-time event but a continuous cycle — the agent's rune staff is constantly being updated with new wisdom and pruned of outdated patterns.

**Challenges of adaptive learning.** Adaptive learning from execution is not without risks:

**Spurious patterns.** The agent may detect patterns that are coincidental rather than causal. If the agent's API calls happened to time out three times on consecutive Tuesdays, the agent may learn "APIs time out on Tuesdays" — but the real cause was a weekly maintenance window that has since ended. The agent's pattern recognition must include statistical significance testing to distinguish genuine patterns from noise.

**Overfitting.** The agent may learn patterns that are too specific to past experience. If the agent learned that "API X times out when called with parameter Y" based on two occurrences, this pattern may not generalize. The agent's learning must be regularized — preferring general patterns over specific ones unless the data strongly supports specificity.

**Catastrophic forgetting.** As the agent accumulates new experience, it may forget old patterns that are still relevant. If the agent's error schema database is updated continuously with new patterns, old patterns may be displaced or overwritten. The agent must balance the incorporation of new learning with the retention of old learning — a challenge that mirrors the stability-plasticity dilemma in neural networks (Grossberg, 1980).

**Distribution shift.** The environment changes over time, and patterns learned in the old environment may not apply in the new environment. The API that timed out in 2039 may not time out in 2040 (the server was upgraded), and patterns learned in the old environment are not just irrelevant — they may be actively harmful if they cause the agent to avoid useful actions or prefer suboptimal ones. The agent must detect distribution shifts (using the anomaly detection techniques from Lecture 4) and adapt its learned patterns accordingly.

**Key Topics:**

- Adaptive learning: transforming self-correction from a cost into an investment
- Error pattern recognition: clustering, frequent subsequence mining, error schemas
- Correction strategy learning: meta-learning for strategy selection policies
- Plan template learning: modifying plan templates to incorporate pre-emptive corrections
- Environmental model learning: updating the agent's model of the world based on systematic regularities
- The rúnakefli pattern: record → abstract → apply → evaluate → revise
- Challenges: spurious patterns, overfitting, catastrophic forgetting, distribution shift

**Required Reading:**

- Minsky, M. *The Society of Mind* (1986), Chapter 6 (Learning and Memory)
- Grossberg, S. "How Does a Brain Build a Cognitive Code?" (1980), *Psychological Review*
- University of Yggdrasil TR: "Rúnakefli Learning: Adaptive Strategy Selection from Execution Experience" (2040)

**Discussion Questions:**

1. The agent learns that "API X times out on Tuesdays" and avoids scheduling calls to API X on Tuesdays. But what if the underlying cause (a weekly maintenance window) is fixed? The agent continues avoiding Tuesday calls even though they would now succeed. How should the agent detect and correct outdated learned patterns? Should it periodically "test" its learned patterns by deliberately violating them and observing the result?
2. Overfitting in adaptive learning means learning patterns that are too specific to past experience. But "too specific" is relative — a pattern that is specific to one environment may be exactly right in that environment. How should the agent balance the specificity of its learned patterns against the risk that they won't generalize to slightly different contexts?
3. The rune staff encodes accumulated wisdom. But times change — patterns that were true in the Viking Age (e.g., "sail when the wind is from the west") may not be true in 2040 (e.g., "API calls time out during peak hours" may not be true after a server upgrade). How can the agent maintain a living, evolving rune staff that grows with experience but also prunes patterns that are no longer valid?

---

### ᛞ Lecture 11: Multi-Agent Self-Correction — The Þing at Þingvellir

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Self-correction in a single agent is challenging enough. Self-correction in a multi-agent system — where multiple agents are simultaneously executing, monitoring, correcting, and learning — is a qualitatively different problem. A multi-agent system introduces dependencies between agents (one agent's output is another's input), conflicts between agents (two agents may pursue contradictory goals), and communication challenges (agents must coordinate their detection, diagnosis, and correction activities). The multi-agent dimension transforms self-correction from an internal process (an agent monitoring and correcting its own behavior) to a social process (agents monitoring, correcting, and coordinating with each other).

The 2040 landscape of multi-agent self-correction is shaped by three factors:

**Inter-agent dependencies.** In a multi-agent workflow, Agent A's output may be Agent B's input. If Agent A produces an error, the error propagates to Agent B, which may propagate it further to Agents C, D, and E. The multi-agent system must detect the error at the source (Agent A), diagnose it correctly (it's Agent A's error, not Agent B's, C's, D's, or E's), and correct it at the source (Agent A must revise its output, not Agent B revise its processing). **Error attribution** — determining which agent caused the error — is the first and most fundamental challenge of multi-agent self-correction.

**Conflicting corrections.** Agent A detects an error and proposes Correction X. Agent B detects the same error (or a related one) and proposes Correction Y. If X and Y are incompatible — applying both would produce an inconsistent state — the system must resolve the conflict. The resolution can be centralized (a coordinator agent decides which correction to apply) or decentralized (the agents negotiate, vote, or use a priority scheme). The Norse **Þing** — the assembly where chieftains gathered to resolve disputes — provides the archetypal model for conflict resolution among agents with conflicting corrections.

**Coordination overhead.** Multi-agent self-correction requires communication: agents must share error reports, diagnostic findings, and correction proposals. This communication has a cost — latency (the time it takes for messages to travel between agents), bandwidth (the number of messages the system can handle), and cognitive load (the amount of information each agent must process). Excessive communication can overwhelm the system; insufficient communication can leave agents unaware of each other's corrections, leading to conflicting or redundant actions. The system must balance the **communication-precision tradeoff**: more communication enables more precise coordination but costs more resources.

The ÞingAI framework's approach to multi-agent self-correction is the **Þing Architecture** (named after the Old Norse assembly):

**The Lawspeaker (Lögmaðr).** Each multi-agent system has a designated coordinator — the Lawspeaker — who maintains the shared state, resolves conflicts, and arbitrates disputes. The Lawspeaker does not generate corrections itself; it receives correction proposals from the other agents, evaluates them for conflicts, and approves or rejects them. The Lawspeaker is a single point of coordination, not a single point of failure — if the Lawspeaker fails, a backup takes over.

**The Thing SITE (Þingstaðr).** A shared workspace where agents can read each other's outputs, post error reports, propose corrections, and observe the system state. The Thing SITE is the multi-agent equivalent of the PEOEDA cycle's observation phase — it is where agents perceive the state of the system and detect deviations.

**The Law (Lög).** A set of rules that govern how corrections are proposed, evaluated, and applied. The Law specifies: (a) who can propose corrections (any agent), (b) who approves corrections (the Lawspeaker), (c) how conflicts are resolved (priority schemes, voting, or the Lawspeaker's judgment), (d) what happens when corrections conflict (the Lawspeaker may approve one, both, or neither), and (e) how corrections are applied (atomically or incrementally).

**The Frith (Friðr).** The Norse concept of frith — social peace, the obligation to maintain harmonious relationships — is the guiding principle of multi-agent self-correction. Frith does not mean the absence of conflict; it means that conflicts are resolved through established procedures (the Law) rather than through brute force or chaos. In a multi-agent system, frith means that agents cooperate even when their individual goals conflict, that they follow the Law even when it disadvantages them, and that they prioritize the system's overall success over their individual success. Frith is the social contract that makes the multi-agent system work.

The Þing Architecture supports several conflict resolution strategies:

**Priority-based resolution.** Each agent has a priority based on its role, expertise, or the stakes of its task. When corrections conflict, the higher-priority agent's correction takes precedence. A medical agent that detects a drug interaction takes precedence over a scheduling agent that detected a calendar conflict. Priority-based resolution is simple and fast but can be unfair to lower-priority agents and may not account for the quality of the correction.

**Voting-based resolution.** Multiple agents vote on which correction to apply. Each agent casts a vote (or a weighted vote based on confidence), and the correction with the most votes wins. Voting is democratic and can aggregate diverse perspectives, but it can be slow (the agents must communicate and agree on the vote) and can be manipulated (an agent that controls many votes can impose its preferred correction).

**Evidence-based resolution.** Each correction proposal includes evidence: the diagnostic reasoning that supports it, the data that justifies it, and the expected outcome if it is applied. The Lawspeaker evaluates the evidence and approves the correction with the strongest evidence. Evidence-based resolution is the most principled approach (it is essentially the scientific method applied to multi-agent correction) but it requires agents to produce and communicate rigorous evidence, which is costly.

**Negotiation-based resolution.** When agents propose conflicting corrections, the Lawspeaker facilitates a negotiation: each agent presents its case, responds to the other's case, and the agents seek a compromise that addresses both concerns. Negotiation-based resolution produces the best outcomes when the agents' concerns are partially compatible, but it is the most time-consuming and requires agents with sophisticated reasoning and communication capabilities.

**Key Topics:**

- Multi-agent self-correction: detection, diagnosis, and correction across multiple agents
- Inter-agent dependencies: error propagation, error attribution
- Conflicting corrections: when multiple agents propose incompatible corrections
- Coordination overhead: communication-precision tradeoff
- The Þing Architecture: Lawspeaker (coordinator), Thing SITE (shared workspace), Law (rules), Frith (social contract)
- Conflict resolution: priority-based, voting-based, evidence-based, negotiation-based
- The Þing at Þingvellir: the archetypal model for multi-agent conflict resolution

**Required Reading:**

- Jennings, N.R. "Commitments and Conventions: The Foundation of Coordination in Multi-Agent Systems" (1993), *The Knowledge Engineering Review*
- Wooldridge, M. *An Introduction to Multi-Agent Systems* (3rd ed., 2038), Chapter 5 (Coordination)
- University of Yggdrasil TR: "The Þing Architecture: Multi-Agent Self-Correction with Lawspeaker Coordination and Frith-Based Conflict Resolution" (2040)

**Discussion Questions:**

1. The Lawspeaker is a single point of coordination. But what if the Lawspeaker itself is wrong — it approves a correction that is harmful, or rejects a correction that is necessary? How should the system handle a failing coordinator? Should there be a mechanism for the other agents to override the Lawspeaker's decision, and if so, how does this not undermine the Lawspeaker's authority?
2. Evidence-based resolution requires agents to produce rigorous evidence for their correction proposals. But producing evidence takes time and compute — the agent must run diagnostics, gather data, and reason about causes. In a time-critical situation (a failing deployment, a system outage), the agent cannot afford a thorough evidence-gathering process. How should the system trade off evidence quality against correction speed?
3. Frith — social peace — is maintained when agents follow the Law even when it disadvantages them. But what if the Law itself is unjust — what if the priority scheme systematically disadvantages certain agents, or the voting system is dominated by a coalition? Can the agents challenge the Law? What mechanism would allow the Law itself to be corrected?

---

### ᛟ Lecture 12: The Self-Correcting Agent as a Way of Being — Vísir ok Vǫrkraft

**Course:** AI305 — Autonomous Task Execution & Self-Correction
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

We began this course with a paradox: autonomy without self-correction is not autonomy at all, but brittleness disguised as freedom. We end with a synthesis: the self-correcting agent is not merely a technical architecture — it is a way of being in the world. The agent that plans, executes, monitors, diagnoses, recovers, replans, refines, adapts, and coordinates is not a collection of modules bolted together; it is an integrated system whose very identity is constituted by its capacity to navigate an unpredictable world with wisdom and resilience.

The Norse concept of **vísir** (wisdom, foresight, discernment) and **vǫrkraft** (the power to act, to make real, to bring about) together describe the self-correcting agent. Vísir without vǫrkraft is philosophy — it sees what should be done but cannot do it. Vǫrkraft without vísir is brute force — it acts without understanding. The self-correcting agent has both: the vísir to plan wisely, diagnose accurately, and adapt intelligently, and the vǫrkraft to execute, correct, and persist. Like Odin, who sacrificed himself to himself on Yggdrasil to gain the wisdom of the runes, the agent must be willing to sacrifice its current plan — its current understanding — in order to gain the wisdom that comes from failure.

**The self-correction cycle as a way of being.** The PEOEDA cycle — Plan, Execute, Observe, Evaluate, Diagnose, Adapt — is not merely a procedure; it is an orientation toward the world. The agent that lives by this cycle is fundamentally different from the agent that does not. It does not fear failure, because failure is information — it reveals what the agent did not know. It does not cling to plans, because plans are hypotheses, not destiny. It does not assume the world is static, because it has learned from experience that the world changes. It does not trust its own certainty, because it knows that certainty is the enemy of adaptation. The self-correcting agent approaches every task with humility (I may be wrong), vigilance (I must watch for errors), resilience (I can recover from errors), and persistence (I will keep trying).

**The synthesis of the course.** Let us draw together the threads woven through the twelve lectures:

**Lecture 1** established the autonomy paradox: autonomy without self-correction is reckless. The PEOEDA cycle is the fundamental loop of autonomous execution, and wyrd — the web of accumulated conditions — is the philosophical model for the agent's negotiation with an unpredictable world.

**Lecture 2** covered task decomposition: breaking goals into manageable sub-tasks. Odin's preparation for Ragnarök illustrates that even an impossible task can be decomposed — and that even the best decomposition may not guarantee success.

**Lecture 3** traced the history of planning from STRIPS to LLMs to neurosymbolic hybrids. Runes — compressed symbols encoding conditions, actions, and effects — are the ancient analogue of planning operators.

**Lecture 4** presented execution monitoring: watching the world while the plan unfolds. Heimdallr, who sees all and hears all, is the mythological watchman whose vigilance the agent must emulate — but the agent must also detect the unexpected, not just the expected.

**Lecture 5** addressed error diagnosis: tracing surface symptoms to root causes. Yggdrasil's roots — deep, hidden, and the source of the tree's health or disease — are the metaphor for the diagnostic challenge of finding what lies beneath.

**Lecture 6** covered recovery strategies: retry, adjust, try an alternative, replan, or escalate. Mjölnir, which always returns to Thor's hand, models the recovery principle — always return to a known-good state. And Þrymskviða shows that when obvious recovery fails, creative replanning is necessary.

**Lecture 7** addressed replanning: discarding the old plan and generating a new one. The Norns weave, and the weave can be changed — the agent does not rewrite fate but reweaves its path through the web of wyrd.

**Lecture 8** covered feedback loops and iterative refinement. The dwarven forge — where Gungnir and Mjölnir were hammered, heated, cooled, examined, and improved in cycles until they were perfect — is the mythological model of iterative refinement.

**Lecture 9** addressed robustness and graceful degradation. The longship — designed for the worst conditions, not the best — embodies the principle that robustness matters most when conditions are adverse.

**Lecture 10** covered adaptive learning: transforming self-correction from a cost into an investment. The rune staff, which encodes accumulated wisdom from experience, is the agent's learned pattern library — constantly updated, pruned, and revised.

**Lecture 11** extended self-correction to multi-agent systems. The Þing — the Norse assembly where chieftains resolved disputes through law rather than force — provides the model for multi-agent conflict resolution, with a Lawspeaker, a shared workspace, a set of laws, and a commitment to frith.

And now, **Lecture 12** synthesizes these threads into a coherent vision: the self-correcting agent as a way of being in the world — vísfr ok vǫrkraft, wisdom and power, discernment and action.

**The future of self-correcting agents.** The 2040 state of the art in autonomous task execution and self-correction is impressive but far from complete. Several frontiers remain:

**Self-correction as learning-to-learn.** Current self-correction corrects the current task; adaptive learning prevents similar errors in future tasks. But meta-learning — learning how to learn — remains largely unrealized. An agent that could learn *which* patterns to learn, *how* to abstract from specific errors to general schemas, and *when* to update its learning strategy — that is, an agent that corrects its own correction process — would be a genuine meta-cognitive system. The rúnakefli pattern (Lecture 10) is a step in this direction, but it is still rule-based rather than truly meta-cognitive.

**Cross-agent learning.** In a multi-agent system, each agent learns from its own experience. But agents could also learn from each other — Agent A's error schema could be transferred to Agent B, which has not yet encountered that error. The multi-agent frith (Lecture 11) makes it possible for agents to share their learned wisdom, but the mechanisms for knowledge transfer across agents with different architectures, different capabilities, and different experiences are still being developed.

**Self-correction and trust.** An agent that frequently self-corrects may appear unreliable to users — if the plan keeps changing, the corrections keep coming, and the agent seems to be flailing — even though the corrections are actually making the outcome better. The user sees the messy process, not the improved result. Designing self-correcting agents that *appear* competent and trustworthy while they are self-correcting — communicating progress, explaining corrections, and maintaining user confidence — is an open challenge in human-agent interaction.

**The philosophical question.** Is the self-correcting agent truly autonomous, or is it merely a sophisticated script whose corrections follow predetermined rules? The PEOEDA cycle is, after all, a procedure — follow these steps, and the system self-corrects. Does the agent *choose* to self-correct, or is it compelled by its architecture? And if it is compelled, can we call it autonomous? The Norse answer would be: wyrd is not fate, but the web of accumulated conditions that constrain and enable action. The agent's architecture is its wyrd — the conditions that shape its behavior. Within those conditions, the agent still chooses: which correction to apply, which diagnosis to pursue, which path to take. The self-correcting agent is autonomous not because its architecture gives it unlimited freedom, but because its architecture gives it the freedom to navigate an unpredictable world — and that freedom is wyrd-bound, as all freedom is.

**Vísir ok vǫrkraft.** Wisdom and power. The agent that has both — the discernment to know what to do and the power to do it — is the agent that can be trusted in an uncertain world. That is the aspiration of this course, and of the field of autonomous task execution and self-correction: to build agents that are wise enough to know when they are wrong and powerful enough to put themselves right.

**Key Topics:**

- Vísir ok vǫrkraft: wisdom and power as the dual nature of the self-correcting agent
- The PEOEDA cycle as a way of being: humility, vigilance, resilience, persistence
- Synthesis of all twelve lectures: the integration of planning, monitoring, diagnosis, recovery, replanning, refinement, robustness, adaptation, and coordination
- Future frontiers: meta-cognitive self-correction, cross-agent learning, trust and appearance
- The philosophical question: is self-correction autonomy or sophisticated scripting?
- Wyrd-bound freedom: the agent's architecture shapes its behavior, but within that shape, the agent still chooses

**Required Reading:**

- All previous lectures — this lecture synthesizes the entire course
- Liddell, H. & Scott, R. *A Greek-English Lexicon* (1940), entries on *phrónēsis* and *dúnami* — the ancient roots of vísir and vǫrkraft
- University of Yggdrasil TR: "Vísir ok Vǫrkraft: Wisdom and Power in the Self-Correcting Autonomous Agent" (2040)

**Discussion Questions:**

1. The self-correcting agent that frequently changes its plan may appear unreliable to users — even though the corrections improve the outcome. How should the agent communicate its self-correction process to maintain user trust? Should it show the corrections (the messy process) or only the final result (the polished outcome)?
2. Meta-learning — learning how to learn — is the frontier of adaptive self-correction. But meta-learning introduces a new layer of potential error: the agent's learning strategy may itself be wrong. How many levels of meta-correction are needed? Is there a regress problem where the agent needs a meta-meta-correction for its meta-correction, and so on ad infinitum?
3. Wyrd is not fate but the web of conditions that constrain and enable action. The agent's architecture is its wyrd. But humans — whose architecture is also wyrd-bound (by genetics, culture, environment) — are generally considered autonomous. What is the philosophical difference between human autonomy (wyrd-bound but self-determining) and agent autonomy (also wyrd-bound but rule-governed)? Is there a meaningful difference, or is it a matter of degree?

---

## Final Examination Preparation

### Format

The final examination for AI305 will consist of **8 essay questions**, from which students must choose **4** to answer. Each essay should be 1500–2500 words and should demonstrate mastery of the course material, including the ability to apply concepts from the lectures to novel scenarios, to compare and contrast different approaches, and to critically evaluate trade-offs. Students are expected to cite specific lecture material, required readings, and technical frameworks discussed in the course.

### Essay Questions

1. **The Autonomy Paradox in Practice.** Consider an autonomous agent deployed as a medical triage assistant in a busy hospital emergency room. The agent must assess patients, recommend treatment priorities, and coordinate with human medical staff. Apply the autonomy paradox (Lecture 1) to this scenario: what are the risks of autonomy without self-correction in this domain? What are the risks of excessive self-correction (the agent constantly second-guesses itself and fails to act decisively)? Design a self-correction architecture specifically for this domain, specifying the PEOEDA cycle, the monitoring thresholds, the recovery strategies, and the escalation criteria. How does the medical domain's high stakes and regulatory environment shape the self-correction design?

2. **Recovery Strategy Selection Under Uncertainty.** You are designing an autonomous software deployment agent for a large-scale production system. The agent encounters a deployment failure and must choose a recovery strategy: retry, parameter adjustment, alternative path, replanning, or escalation (Lecture 6). But the agent does not know whether the failure is transient or persistent — it has only the error output to go on. Design a decision procedure for recovery strategy selection under this uncertainty. What features of the error output should the agent examine? What heuristics should it use? How should the recovery budget be allocated across strategies? Evaluate your design using the Norse concept of Mjölnir (always return) and Þrymskviða (creative replan when obvious strategies fail).

3. **Multi-Agent Conflict Resolution at Scale.** In a multi-agent system with 50 agents working on a large software project, conflicts between corrections are frequent. The Þing Architecture (Lecture 11) provides a framework with a Lawspeaker, a Thing SITE, and a set of Laws. But scaling the Þing from 5 agents to 50 introduces new challenges: the Lawspeaker becomes a bottleneck, the Thing SITE becomes overwhelming with messages, and the delay of conflict resolution slows the project. Propose modifications to the Þing Architecture that enable it to scale. Consider hierarchical Þings (sub-assemblies for sub-teams), federation (multiple Lawspeakers, each handling a sub-team), and market mechanisms (agents bid for correction priority). How does frith — the commitment to social harmony — scale to large systems?

4. **Adaptive Learning and Distribution Shift.** An agent has been deploying web services for two years and has learned many useful patterns: "API X times out during peak hours," "Service Y requires a 30-second startup delay," and "Database Z needs periodic connection pool resets." The organization migrates to a new cloud infrastructure, and all of these patterns become invalid at once. The agent's adaptive learning (Lecture 10) has been a strength for two years, but now it is a liability — the agent's rune staff is full of outdated wisdom. Design a procedure for detecting and recovering from distribution shifts in adaptive learning. How should the agent distinguish between a genuine distribution shift (the environment has changed) and normal variance (the environment is noisy but hasn't fundamentally changed)? Should the agent maintain separate rune staffs for different environments? How should it handle the transition period when some patterns are still valid and others are not?

5. **Robustness vs. Optimality.** The robust agent (Lecture 9) is designed for adverse conditions: it has fallbacks, circuit breakers, timeouts, and degraded modes. The optimal agent is designed for ideal conditions: it uses the best API, the fastest model, the most efficient path. In ideal conditions, the optimal agent outperforms the robust agent by a significant margin. In adverse conditions, the robust agent outperforms the optimal agent by an even larger margin. Under what conditions is it better to be optimal? Under what conditions is it better to be robust? Propose a framework for deciding when to optimize for ideal conditions and when to optimize for adverse conditions. How should the agent balance the two? Is there a strategy that combines the advantages of both — and what are its costs?

6. **Diagnostic Depth vs. Speed.** A deployment fails. The agent has 30 seconds to diagnose and correct the failure before the deployment window closes. The diagnostic loop (Lecture 5) is thorough but slow: full diagnosis might take 2 minutes. A quick diagnosis — parsing the error output and making a best guess — takes 5 seconds but has a 60% accuracy rate. Propose a diagnostic architecture that balances depth and speed. What heuristics should determine whether the agent does a quick diagnosis or a thorough one? How should the agent decide when to stop diagnosing and start correcting, even with incomplete information? In your answer, relate the diagnostic time budget to the Norse concept of Yggdrasil's roots: how deep should the agent dig before it decides that the surface symptom is sufficient?

7. **The Self-Correcting Agent and Trust.** A study at the University of Yggdrasil found that users trust agents that execute plans smoothly (without visible self-correction) more than agents that frequently self-correct — even when the self-correcting agent produces better outcomes. The users perceived the self-correcting agent as "uncertain" and "indecisive," while the non-correcting agent was perceived as "confident" and "decisive." This is the **trust paradox** of self-correction: the process that improves outcomes also erodes trust. Propose and evaluate three strategies for addressing this paradox: (a) invisible self-correction (the agent self-corrects but does not show the corrections to the user), (b) narrative self-correction (the agent presents corrections as confident plan updates rather than as error corrections), and (c) transparent self-correction with trust repair (the agent shows the corrections and explains why they improve the outcome). Which strategy is most appropriate for different contexts (medical, financial, creative)?

8. **Research Paper: Vísir ok Vǫrkraft.** Write a research paper (3000–4000 words) proposing a novel architecture for autonomous task execution and self-correction. Your architecture should integrate at least four of the following: PEOEDA cycles, hierarchical task decomposition, execution monitors, diagnostic loops, recovery hierarchies, replanning with failure context, iterative refinement, robust fallback designs, adaptive learning, and multi-agent Þing coordination. Your paper should: (a) describe the architecture in detail, (b) explain how the components interact, (c) identify the key design decisions and their trade-offs, (d) propose an evaluation methodology, and (e) relate the architecture to the Norse philosophical concepts discussed in the course (wyrd, PEOEDA as a way of being, vísir ok vǫrkraft). This is your opportunity to synthesize the material into an original contribution — weave your own thread into the web.

---

*ᚠᚢᚦᚬᚱᚴᚼᚾᛁᛃᛗᛚᛞᛟ*

*Hvat ek um fátt fregna*
*er þín spjöll of segia*
*heƒi ec uit um uarld at uísi*

— Hávamál, st. 33

*Much have I learned, much have I asked,*
*Much has the wise one told me —*
*For I have wandered the world,*
*Seeking wisdom wherever it dwells.*