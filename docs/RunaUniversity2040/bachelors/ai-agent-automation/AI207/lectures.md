# AI207: Knowledge Representation & Reasoning
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI101 (Introduction to Artificial Intelligence), AI105 (Introduction to Machine Learning)
**Description:** An agent that cannot represent knowledge is a parrot — fluent but empty. An agent that cannot reason with knowledge is a library — vast but inert. Knowledge representation and reasoning (KRR) is the discipline that bridges these gaps: it provides the formal languages for encoding what an agent knows and the algorithms for deriving what follows from that knowledge. This course covers the full spectrum of KRR as it bears on agent architecture in 2040 — from classical symbolic logics through probabilistic graphical models and neural embeddings to the hybrid neurosymbolic systems that represent the frontier. Students will design ontologies, implement reasoners, query knowledge graphs, and grapple with the hardest problem in AI: commonsense reasoning.

> *"To know what you know and what you do not know — that is true knowledge."* — Confucius. The agent's challenge, recast for 2040.

---

## Lectures

### ᚠ Lecture 1: What Is Knowledge? — Representation, Truth, and the Agent's Internal World

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Knowledge is not data. Data is raw — a temperature reading, a pixel value, a string of characters. Knowledge is data that has been interpreted, structured, and integrated into a system that can use it to draw inferences. The temperature reading of 38.2°C is data. The knowledge that 38.2°C is a fever, that fevers indicate infection, that infection requires treatment, and that the appropriate treatment depends on the pathogen — that chain of inference is knowledge. Knowledge representation is the discipline of encoding such chains in forms that machines can manipulate; knowledge reasoning is the discipline of traversing those chains to reach conclusions the agent has not been explicitly told.

The history of KRR is the history of AI itself. The early AI programs — the Logic Theorist (Newell, Shaw, & Simon, 1956), the General Problem Solver (1957), SHRDLU (Winograd, 1970) — were fundamentally exercises in knowledge representation. They operated in tiny, hand-crafted "microworlds" where all relevant knowledge was explicitly encoded in formal logic, and reasoning was theorem-proving. The collapse of this paradigm in the 1970s and 80s — the "AI Winter" — was driven by the realization that most of what humans know is not amenable to explicit logical encoding. What is a chair? You can sit on it. But you can also sit on a table, a bed, a log, a lap — so "sittable" does not define a chair. The definition recedes into an endless regress of contextual considerations. This is the **knowledge acquisition bottleneck**: the difficulty of extracting tacit, contextual, commonsense knowledge from human minds and encoding it in machine-readable form.

The 2040 landscape of KRR is shaped by the resolution — partial, but substantial — of this bottleneck. Large language models, trained on trillions of tokens of human-generated text, have absorbed an enormous amount of the commonsense knowledge that eluded explicit encoding. GPT-7, Gemini 3.0, and Llama-5 can answer questions like "Can you fit a couch through a doorway?" not because anyone encoded that knowledge explicitly but because they've read enough descriptions of moving furniture to have absorbed the implicit physics and geometry. This is **subsymbolic knowledge representation**: knowledge embedded in the weights of a neural network, accessed through pattern completion rather than logical inference.

But subsymbolic representation is not enough. LLMs can answer a commonsense question correctly 90% of the time — but the 10% where they fail, they fail in ways that are unpredictable, unrevisable, and un-auditable. There is no way to "edit" the knowledge that a couch can fit through a doorway if the couch is disassembled, except by training on more examples of disassembled couches. Symbolic representation — explicit, logical, editable — remains essential for the kinds of knowledge where correctness matters: medical guidelines, legal statutes, safety constraints, scientific facts. The 2040 synthesis is **neurosymbolic KRR**: subsymbolic knowledge provides breadth and flexibility; symbolic knowledge provides depth and reliability; the architecture integrates both.

The Norse **Mímisbrunnr** — Mímir's well — contains all the knowledge that Odin sought when he sacrificed his eye. But the well is not a library; it is not a database. The well is a living source of wisdom, tended by the severed head of Mímir, who speaks only to those who have paid the price of knowing. Knowledge representation, at its best, is like Mímir's well: not a static repository but a dynamic, responsive, living system that yields its wisdom only to those who know how to ask.

**Key Topics:**

- Data vs. knowledge: interpretation, structure, inferential potential
- The knowledge acquisition bottleneck: why explicit encoding failed and how LLMs partially resolved it
- Subsymbolic knowledge: embedded in neural weights, accessed through pattern completion
- Symbolic knowledge: explicit, logical, editable, auditable
- Neuro-symbolic synthesis: breadth from subsymbolic, reliability from symbolic
- Mímisbrunnr: knowledge as living source, not static repository

**Required Reading:**

- Davis, R., Shrobe, H., & Szolovits, P. "What Is a Knowledge Representation?" (1993), *AI Magazine*
- Brachman, R. & Levesque, H. *Knowledge Representation and Reasoning* (2nd ed., 2040), Chapters 1–2
- Lenat, D. "CYC: A Large-Scale Investment in Knowledge Infrastructure" (1995), *Communications of the ACM*
- University of Yggdrasil TR: "The Neuro-Symbolic Knowledge Frontier: Integrating LLMs with Formal Knowledge Representation" (2040)

**Discussion Questions:**

1. CYC encoded millions of commonsense facts manually over 35 years and was widely considered a failure. But in 2040, it powers several industrial knowledge systems. Was CYC a failure — or just early? What does its trajectory teach us about the relationship between symbolic and subsymbolic KRR?
2. An LLM correctly answers "Can a couch fit through a doorway?" by pattern completion. But it cannot explain *why* — it cannot articulate the geometric reasoning. Is this a KRR problem or an explanation problem? Can you have knowledge without the ability to explain it?
3. Mímir's well requires sacrifice. What must an agent architect "sacrifice" — in terms of computational resources, simplicity, or universality — to build a knowledge system that is both broad (like an LLM) and reliable (like a formal ontology)?

---

### ᚢ Lecture 2: Logic as Knowledge — Propositional Logic, First-Order Logic, and the Roots of Formal Reasoning

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Logic is the oldest and still the most rigorous formalism for knowledge representation. A logical knowledge base is a set of sentences — statements that are either true or false — and reasoning is the application of inference rules that derive new sentences from existing ones, preserving truth. If the knowledge base is true and the inference rules are sound, any derived sentence is guaranteed to be true. This is the unique selling proposition of logic: the guarantee. No other KRR formalism offers it.

**Propositional logic** is the simplest logical system. The vocabulary consists of atomic propositions (P, Q, R...) and logical connectives: ¬ (not), ∧ (and), ∨ (or), → (implies), ↔ (if and only if). Sentences are formed by composing atoms with connectives. A **model** is an assignment of truth values (true/false) to each atom. A sentence is **satisfiable** if there exists at least one model in which it is true; it is **valid** (a tautology) if it is true in all models. Reasoning in propositional logic is **decidable** — there exist algorithms (truth tables, DPLL, SAT solvers) that can determine, for any sentence, whether it is entailed by a knowledge base.

**First-order logic (FOL)** extends propositional logic with **quantifiers** (∀ for all, ∃ there exists), **variables** (x, y, z), **predicates** (relations among objects: Parent(x, y), Mortal(x)), and **functions** (mappings from objects to objects: motherOf(x)). FOL is expressive enough to encode substantial domains of knowledge. The classic syllogism "All men are mortal; Socrates is a man; therefore Socrates is mortal" is expressed in FOL as: ∀x (Man(x) → Mortal(x)) ∧ Man(Socrates) ⊢ Mortal(Socrates). The power of FOL is that from a small set of axioms, a reasoner can derive infinitely many consequences — and every consequence is guaranteed to be true if the axioms are true.

The price of FOL's expressiveness is complexity. **Satisfiability in FOL is semi-decidable**: there exist algorithms that will eventually find a proof if one exists, but no algorithm can guarantee to terminate when no proof exists. The practical consequence is that FOL reasoning must be bounded — by time limits, by depth limits, by restricting to decidable fragments. **Description logics** — the formal foundation of the Web Ontology Language (OWL) — are a family of decidable fragments of FOL that have proved sufficient for many practical knowledge representation tasks.

The 2040 relevance of classical logic to agent architecture is twofold. First, **formal verification** — proving that an agent's safety properties hold under all possible inputs — requires a logical formalism. You cannot verify a neural network with an LLM; you must reason about its behavior symbolically. Second, **rule-based reasoning** — encoding expert knowledge as production rules — remains the dominant paradigm for high-stakes domains (medical diagnosis, legal reasoning, financial compliance) where errors are unacceptable and auditability is mandatory.

The Norse god **Týr** sacrificed his hand to bind the wolf Fenrir. Týr is the god of law, oaths, and formal procedure — the divine logician. He understood that some truths require sacrifice: to bind chaos, you must give up what you value. Logic, too, requires sacrifice: to gain the guarantee of truth, you must give up the richness and ambiguity of natural language, the fluidity of neural representations, the breadth of commonsense. The agent architect must decide, for each piece of knowledge, whether the guarantee is worth the sacrifice.

**Key Topics:**

- Propositional logic: atoms, connectives, models, satisfiability, validity, SAT solvers
- First-order logic: quantifiers, predicates, functions, semi-decidability
- Description logics: decidable fragments of FOL, the foundation of OWL
- The guarantee: sound inference rules that preserve truth
- 2040 relevance: formal verification, rule-based expert systems
- Týr's sacrifice: logic's guarantee requires giving up richness and ambiguity

**Required Reading:**

- Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4th ed., 2040), Chapters 7–9
- Brachman, R. & Levesque, H. *Knowledge Representation and Reasoning* (2nd ed., 2040), Chapters 3–5
- Baader, F. et al. *The Description Logic Handbook* (3rd ed., 2038), Cambridge University Press
- University of Yggdrasil TR: "Formal Verification of Agent Safety Properties Using Description Logics" (2040)

**Discussion Questions:**

1. FOL is expressive but semi-decidable. In a production agent with a latency budget of 500ms, how do you bound FOL reasoning to guarantee termination without sacrificing too much expressiveness?
2. Rule-based expert systems were the dominant AI paradigm in the 1980s (MYCIN, XCON, R1). They were largely abandoned in favor of machine learning. But by 2040, they are making a comeback in high-stakes domains. Why? What do rules provide that learned models do not?
3. Týr's sacrifice is the archetype of formal reasoning: to gain truth, give up richness. Is this trade-off fundamental — must logic always be less expressive than natural language — or could a future formalism capture the richness of natural language while retaining the guarantee?

---

### ᚦ Lecture 3: Semantic Networks, Frames, and the Structure of Concepts

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Logic represents knowledge as sentences. But human knowledge is not primarily sentential — it is structured, associative, hierarchical. When you think of a "dog," you do not mentally assert ∃x Dog(x) ∧ HasTail(x) ∧ Barks(x). You activate a network of associations: dogs are animals, dogs have fur, dogs bark, dogs are pets, your neighbor has a dog, that dog bit you when you were seven, the concept of loyalty. **Semantic networks** and **frames** are KRR formalisms that capture this associative, structured character of knowledge, and they remain foundational to the knowledge graph technology that powers agent memory systems in 2040.

**Semantic networks**, introduced by Quillian (1968), represent knowledge as a graph: nodes are concepts (DOG, ANIMAL, FUR, BARK), and edges are labeled relations (DOG —is_a→ ANIMAL, DOG —has→ FUR, DOG —makes_sound→ BARK). Reasoning in a semantic network is **spreading activation**: when a concept is activated (e.g., by a query), activation spreads along edges to related concepts, decaying with distance. The concepts that receive the most activation are the "answers." This model is directly inspired by associative models of human memory (Collins & Loftus, 1975) and, remarkably, anticipates the vector-embedding retrieval systems that dominate 2040 architectures: in both cases, a query activates a neighborhood in a structured representation space, and the most-activated neighbors are returned.

**Frames**, introduced by Minsky (1974), extend semantic networks by associating with each concept a **structure of slots** — attributes that the concept's instances typically possess. A frame for RESTAURANT might include slots for CUISINE (default: "American"), PRICE_RANGE (default: "moderate"), MENU (a list of dishes), LOCATION, and RATING. When the agent encounters a new restaurant, it instantiates the RESTAURANT frame, filling in the slots with observed values and inheriting default values for unfilled slots. Frames thus provide **default reasoning**: in the absence of specific information, assume the typical. This is essential for agents operating in partially observed environments — which is to say, all real environments.

The most ambitious descendant of frames and semantic networks is the **knowledge graph** — a large-scale, machine-readable graph of entities and their relationships, typically stored in a graph database and queried with a graph query language (SPARQL, Cypher, GQL). The largest public knowledge graph, **Wikidata**, contains over 100 million entities and billions of relationships, and is continuously updated by a community of human editors. Google's Knowledge Graph, Facebook's Entities Graph, and Amazon's Product Graph are proprietary equivalents that power search, recommendations, and question-answering. For an AI agent in 2040, a knowledge graph serves as its **semantic memory** — the store of what it knows about entities, their properties, and their relationships, queried to inform decisions and generate responses.

The architecture of a knowledge-graph-enhanced agent follows a standard pattern: the agent receives a user query → the query is parsed into an entity-linking step (identifying which entities the query refers to) → those entities are looked up in the knowledge graph → relevant facts and relationships are retrieved → those facts are incorporated into the agent's reasoning context, grounded against the agent's other knowledge sources (its LLM, its episodic memory, its tool outputs). The architectural challenge is **entity disambiguation**: when the user says "Lincoln," do they mean the president, the city, the car, or the university? The agent must resolve the reference using context, and a knowledge graph provides the structured context needed to do so reliably.

The Norse **World Tree, Yggdrasill**, is the ultimate semantic network. Its roots reach into three wells; its trunk spans nine worlds; each world contains beings, places, and relationships, all connected by the branches of the tree. The squirrel Ratatoskr runs up and down the trunk carrying messages (spreading activation) between the eagle at the top and the serpent at the bottom. Yggdrasill is not just a map — it is an ontology of the cosmos, encoding what kinds of things exist (gods, giants, humans, elves, dwarves, dead), how they relate (kinship, enmity, obligation, fate), and how they came to be and will cease to be (the narrative of creation and Ragnarök). Every knowledge graph is a small Yggdrasill — an attempt to structure the world so that meaning can flow along its branches.

**Key Topics:**

- Semantic networks: nodes and edges, spreading activation, associative memory
- Frames: structured slots, default values, inheritance, reasoning under partial information
- Knowledge graphs: Wikidata-scale entity-relationship stores, graph query languages
- Entity disambiguation: the architectural challenge of grounding references
- Yggdrasill as semantic network: an ontology of the cosmos, meaning flowing along branches

**Required Reading:**

- Quillian, M.R. "Semantic Memory" (1968), in *Semantic Information Processing*, MIT Press
- Minsky, M. "A Framework for Representing Knowledge" (1974), MIT AI Lab Memo 306
- Hogan, A. et al. *Knowledge Graphs* (2021), Morgan & Claypool; updated 2040 edition
- University of Yggdrasil TR: "Yggdrasil-KG: A Norse-Inspired Architecture for Agent Knowledge Graphs" (2040)

**Discussion Questions:**

1. Spreading activation in a semantic network and vector similarity in an embedding space are mathematically analogous. Compare them: what does spreading activation capture that vector similarity misses, and vice versa?
2. Frames provide default values — in the absence of evidence, assume the typical. But "typical" encodes cultural assumptions. A RESTAURANT frame with "American" as the default cuisine embeds an American perspective. How should an agent architect handle culturally contested defaults?
3. Yggdrasill connects all nine worlds, but some connections are stronger than others — Bifröst between Ásgarðr and Miðgarðr is a solid bridge; the path to Niflheimr is dark and treacherous. How should a knowledge graph weight its edges to reflect the *confidence* of the relationship, and how should an agent use those weights in reasoning?

---

### ᚬ Lecture 4: Ontologies — The Formal Architecture of What Exists

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An ontology, in the KRR sense, is a formal specification of a shared conceptualization (Gruber, 1993). It defines the kinds of things that exist in a domain (classes, also called concepts), the relationships among them (properties, also called roles or relations), the hierarchical organization of those classes (the taxonomy, the is-a hierarchy), and the constraints that govern instances (axioms). If a knowledge graph is a map of what *is*, an ontology is the legend of the map — the vocabulary and grammar that determine what can be said.

The **Web Ontology Language (OWL)** , standardized by the W3C in 2004 and substantially revised in OWL 2 (2012), is the dominant ontology language in 2040. OWL is built on top of **RDF (Resource Description Framework)** , which represents knowledge as triples: (subject, predicate, object). An RDF triple might be (Volmarr, livesIn, London). OWL extends RDF with logical constructs drawn from description logics: class intersections, unions, complements; property domains and ranges; cardinality constraints (a person has exactly one biological mother); and class axioms (Mother ≡ Woman ⊓ Parent — a mother is exactly a woman who is a parent). An OWL reasoner can take an ontology and an RDF dataset and derive new triples that are logically entailed: if we assert (Volmarr, hasMother, Sigrid) and Sigrid is asserted to be of type Woman and Parent, the reasoner infers that Sigrid is of type Mother.

Ontology engineering — the craft of designing ontologies — is a discipline that draws on philosophy (what kinds of things exist?), linguistics (how do we name and describe them?), and software engineering (how do we make the ontology modular, maintainable, and scalable?). The foundational distinction in ontology engineering is between **upper ontologies** (high-level categories that apply across all domains: Object, Process, Quality, Event, Time, Space) and **domain ontologies** (specific to a field: Disease, Drug, Symptom, Treatment for medicine; Circuit, Signal, Protocol for electronics). Upper ontologies are necessarily abstract and controversial — different philosophical traditions carve the world at different joints. The dominant upper ontologies in 2040 include **BFO (Basic Formal Ontology)** , **DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering)** , and the **SUMO (Suggested Upper Merged Ontology)** .

For an AI agent, an ontology serves as a **schema for the knowledge graph** — it defines the types of entities and relationships that the agent's semantic memory can store, and it provides the logical constraints that the agent's reasoning can exploit. An agent that knows that "all mothers are parents" (an ontological axiom) can answer "Is Sigrid a parent?" with "Yes" even if the triple (Sigrid, isParent, true) was never explicitly stored. This is the power of ontologies: they compress knowledge by encoding it at the level of classes rather than instances.

The 2040 frontier in ontology engineering is **ontology learning** — the automatic extraction of ontologies from text, from databases, and from the internal representations of LLMs. Can we point an algorithm at the entire corpus of medical literature and have it produce a medical ontology? Partial success has been achieved: systems like **OntoGPT** (2038) and **LLM2Onto** (2040) use LLMs to extract candidate classes and relations from text, then use logical reasoners to check consistency. But the ontologies they produce are noisy — they contain redundancies, contradictions, and missing generalizations that human ontology engineers catch. The hybrid approach — LLM proposes, human disposes — is the 2040 standard.

The Norse **Vǫluspá** (The Seeress's Prophecy), the first poem of the Poetic Edda, is a kind of ontology: it enumerates what exists. In the beginning, there was nothing — *gap var ginnunga* — the yawning void. Then the worlds came into being: Ásgarðr, Miðgarðr, Jǫtunheimr, and the rest. The Vǫluspá names the gods, the giants, the dwarves, the first humans (Ask and Embla), the World Tree, and the beings that inhabit it. It is a poetic ontology — but it shares with formal ontologies the fundamental ambition: to say what is, and what can be.

**Key Topics:**

- Ontology as formal specification of a shared conceptualization
- OWL: classes, properties, axioms, reasoners — deriving entailed knowledge
- RDF triples: (subject, predicate, object) as the atomic unit of knowledge
- Upper ontologies (BFO, DOLCE, SUMO) vs. domain ontologies
- Ontology as schema: enabling reasoning at the class level
- Ontology learning: LLM-assisted extraction with human verification
- Vǫluspá as poetic ontology: the ambition to name what exists

**Required Reading:**

- Gruber, T.R. "A Translation Approach to Portable Ontology Specifications" (1993), *Knowledge Acquisition*
- Hitzler, P. et al. *Foundations of Semantic Web Technologies* (2009), CRC Press; updated 2040 edition
- Guarino, N. "Formal Ontology and Information Systems" (1998), *FOIS*
- University of Yggdrasil TR: "LLM2Onto: Large Language Model-Assisted Ontology Learning for Agent Knowledge Bases" (2040)

**Discussion Questions:**

1. An upper ontology carves the world into fundamental categories. BFO uses "Continuant" (things that persist through time) and "Occurrent" (events that unfold in time). DOLCE uses "Endurant" and "Perdurant." Are these distinctions merely terminological, or do they have consequences for an agent's reasoning? If two agents use different upper ontologies, how can they communicate?
2. Ontology learning from LLMs extracts candidate relations. The LLM proposes (Virus, causes, Disease); a human verifies. But the LLM's knowledge is frozen at training time — if a new virus is discovered, the LLM cannot propose it. How should an ontology-learning system incorporate new knowledge from real-time sources?
3. The Vǫluspá is a poetic ontology — it names the cosmos but does not provide a logical structure. What does the Vǫluspá *lack* that a formal ontology provides, and what does it *have* that a formal ontology lacks?

---

### ᚱ Lecture 5: Probabilistic Knowledge — Reasoning Under Uncertainty

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Logic provides guarantees — but only for knowledge that is certain, and almost nothing an agent knows is certain. The patient has a fever, which might indicate infection, but might also indicate heatstroke, or a medication side effect, or a faulty thermometer. The stock has risen for five consecutive days, which might indicate a trend, but might be noise. The user said "that's fine," which might indicate satisfaction, or passive-aggressive displeasure, or distraction. **Probabilistic knowledge representation** extends KRR to handle uncertainty: instead of asserting that a proposition is true or false, the agent assigns a probability — a degree of belief, grounded in evidence — that the proposition is true.

**Bayesian networks** (Pearl, 1988) are the foundational formalism for probabilistic knowledge representation. A Bayesian network is a directed acyclic graph whose nodes represent random variables and whose edges represent direct probabilistic dependencies. Each node has a **conditional probability table (CPT)** that specifies, for each combination of its parents' values, the probability distribution over its own values. The network as a whole defines a joint probability distribution over all variables, factored according to the graph structure: P(X₁, X₂, ..., Xₙ) = ∏ᵢ P(Xᵢ | Parents(Xᵢ)). This factorization is what makes Bayesian networks tractable — instead of specifying an exponentially large joint distribution directly, the knowledge engineer specifies only the local conditional distributions.

Bayesian networks support two fundamental types of reasoning. **Diagnostic reasoning** goes from effects to causes: given that the patient has a fever (effect), what is the probability that they have an infection (cause)? **Predictive reasoning** goes from causes to effects: given that the patient has an infection (cause), what is the probability that they will develop a fever (effect)? **Intercausal reasoning** explains away competing causes: if we observe that the patient has both a fever and a rash, the probability of infection goes down (the rash explains the fever) while the probability of, say, measles goes up. These reasoning patterns are implemented algorithmically by **belief propagation** — messages are passed along the edges of the graph, updating beliefs at each node until convergence.

The 2040 descendant of Bayesian networks is the **probabilistic programming** paradigm, implemented in languages like **Pyro**, **TensorFlow Probability**, and **Stan**. A probabilistic program is a generative model — a piece of code that specifies how data is generated from latent variables — and inference is the process of "running the program backward" to infer the latent variables from observed data. This approach unifies knowledge representation (the model) with reasoning (inference) and learning (fitting the model to data) in a single programming framework.

For AI agents in 2040, probabilistic reasoning is most critical in **decision-making under uncertainty**. An agent deciding whether to escalate a customer support ticket to a human agent must weigh: the probability that the customer is frustrated (high → escalate), the probability that the AI can handle the remaining issues (low → escalate), the cost of a human agent's time (high → don't escalate unless necessary), and the customer's preference (some customers hate being transferred). Probabilistic knowledge representation provides the mathematical framework for formalizing and automating these trade-offs.

The Norse concept of **ørlǫg** — the web of fate, the primal laws that govern what can and cannot happen — is probabilistic: it does not determine every event with certainty, but it constrains the possible. Some events are impossible (you cannot change your ørlǫg); some are certain (what the Norns have decreed); most lie in between, their probability shaped by actions and circumstances. A Bayesian network is an agent's ørlǫg: the structure of dependencies that constrains what the agent believes is possible and what follows from what.

**Key Topics:**

- Probability as degree of belief: propositions have probabilities, not truth values
- Bayesian networks: DAG structure, conditional probability tables, factorized joint distribution
- Reasoning patterns: diagnostic, predictive, intercausal (explaining away)
- Belief propagation: message-passing for exact and approximate inference
- Probabilistic programming: generative models as programs, inference as backward execution
- Ørlǫg: the web of constraints that shapes what is possible

**Required Reading:**

- Pearl, J. *Probabilistic Reasoning in Intelligent Systems* (1988), Morgan Kaufmann
- Koller, D. & Friedman, N. *Probabilistic Graphical Models: Principles and Techniques* (2009), MIT Press
- van de Meent, J.W. et al. "An Introduction to Probabilistic Programming" (2018), *arXiv*
- University of Yggdrasil TR: "Bayesian Decision Architectures for Autonomous Agent Escalation" (2040)

**Discussion Questions:**

1. Bayesian networks require specifying a prior distribution over all variables. Where do these priors come from? If the prior is wrong — if the agent believes infection is rare when it's actually common — how does the agent recover?
2. Belief propagation is exact only for tree-structured graphs. For graphs with loops, it is approximate. Under what circumstances does approximate belief propagation fail catastrophically, and how can the agent detect that its beliefs are unreliable?
3. Ørlǫg is individual — each person's fate is their own — but Bayesian networks can model the dependency of one person's fate on another's. Is the Norse concept of ørlǫg inherently individualistic, or does it admit network effects?

---

### ᚴ Lecture 6: Neural-Symbolic Integration — The Best of Both Worlds?

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

For three decades — roughly 1990 to 2020 — symbolic AI and neural AI were antagonists. The symbolists insisted that intelligence required explicit representations, logical inference, and compositional structure. The connectionists insisted that intelligence emerged from distributed representations, statistical learning, and continuous optimization. Each camp could point to victories: Deep Blue (1997) and Watson (2011) were symbolic triumphs; AlexNet (2012) and GPT-3 (2020) were neural triumphs. By 2040, the war is over — or rather, it has been superseded by a synthesis. **Neural-symbolic integration** is the dominant KRR paradigm, and every major AI company has a neurosymbolic research division.

The core insight of neurosymbolic AI is that neural and symbolic representations are complementary, not competing. Neural representations (embeddings, model weights) excel at **breadth**: they can capture patterns and associations across vast, unstructured datasets without explicit engineering. Symbolic representations (logic, graphs, rules) excel at **depth**: they support precise inference, compositionality, explainability, and editability. The neurosymbolic challenge is to build systems that combine the strengths of both while mitigating their weaknesses.

The 2040 neurosymbolic landscape encompasses several integration patterns:

**Symbolic scaffolding around neural core.** The agent's "brain" is an LLM, but it is embedded in a symbolic framework that provides structure. The LLM generates candidates; the symbolic system filters, verifies, and composes them. This is the pattern of **ReAct with a rule engine**: the LLM proposes actions; a rule engine checks them against safety constraints; only approved actions execute. It is also the pattern of **retrieval-augmented generation**: the LLM generates text; a symbolic retrieval system (knowledge graph query, vector search with structured metadata) provides the facts against which the text is grounded.

**Neural soft logic.** The agent's knowledge is represented as weighted logical formulas, where weights are learned by a neural network. A formula like "Bird(x) → Flies(x)" with weight 0.9 means "most birds fly," and the weight was learned from data rather than asserted by an engineer. Reasoning is performed by a continuous relaxation of logical inference — **Markov Logic Networks** (Richardson & Domingos, 2006) and their 2040 neural extensions — that propagate beliefs through the weighted formula graph. This approach captures the graded, uncertain character of commonsense knowledge while retaining the compositional structure of logic.

**Differentiable reasoning.** The agent performs symbolic reasoning — deduction, induction, abduction — but the reasoning process is implemented as a differentiable computation, so the agent can learn *how* to reason from data. The **Neural Theorem Prover** (Rocktäschel & Riedel, 2017) and its 2040 descendants use neural networks to guide the search through the space of possible proofs, learning which inference rules to apply and in what order. The symbolically grounded reasoning ensures correctness; the neural guidance ensures efficiency.

**Embedding-logic hybrids.** Knowledge graph embeddings (TransE, RotatE, ComplEx) represent entities and relations as vectors in a continuous space, and logical relationships are encoded as geometric constraints on those vectors. A relation "isA" might be encoded as a translation: Dog + isA ≈ Animal. A relation "hasMother" might be encoded as a rotation. These hybrid representations support both logical queries ("find all animals") and similarity queries ("find things similar to a dog") within a unified vector space, and they power the hybrid memory systems discussed in Lecture 8.

The Norse dichotomy between **the Æsir and the Vanir** — two tribes of gods with different values and domains — mirrors the symbolist/connectionist divide. The Æsir (Odin, Thor, Týr) are gods of war, law, and structure — the symbolists. The Vanir (Freyr, Freyja, Njǫrðr) are gods of fertility, nature, and abundance — the connectionists. The two tribes warred, exchanged hostages (Freyja and Freyr went to live among the Æsir; Mímir and Hœnir went to the Vanir), and eventually united. The union of Æsir and Vanir produced a richer pantheon than either tribe could sustain alone. Neuro-symbolic integration is this union, applied to AI.

**Key Topics:**

- The symbolist/connectionist war: explicit representations vs. distributed representations
- Complementary strengths: breadth (neural) vs. depth (symbolic)
- Integration patterns: symbolic scaffolding, neural soft logic, differentiable reasoning, embedding-logic hybrids
- Markov Logic Networks: weighted first-order formulas, learned from data
- Neural Theorem Proving: differentiable search through proof space
- The Æsir and Vanir: two tribes, one pantheon — the union of structure and abundance

**Required Reading:**

- Garcez, A.d'A. & Lamb, L.C. "Neurosymbolic AI: The 3rd Wave" (2023), *Artificial Intelligence Review*
- Richardson, M. & Domingos, P. "Markov Logic Networks" (2006), *Machine Learning*
- Rocktäschel, T. & Riedel, S. "End-to-End Differentiable Proving" (2017), *NeurIPS*
- University of Yggdrasil TR: "The Æsir-Vanir Synthesis: A Unified Neurosymbolic Architecture for Agent Knowledge" (2040)

**Discussion Questions:**

1. Symbolic scaffolding around a neural core: the LLM proposes, the symbolic system verifies. But what if the LLM's proposals are systematically biased in ways the symbolic system cannot detect — for example, the LLM consistently proposes Western medical diagnoses and the symbolic system cannot recognize the bias because it was built on the same Western medical ontology? How do you break the epistemic bubble?
2. Markov Logic Networks assign weights to formulas learned from data. But data encodes historical biases. "CEO(x) → Man(x)" with weight 0.85 accurately reflects historical data but encodes a bias we want the agent to unlearn. How should an agent's knowledge system distinguish between "true" and "historically prevalent"?
3. The Æsir and Vanir united through war, hostage exchange, and eventual integration. What would a "war" between symbolic and neural approaches look like in an agent's architecture — and what would a peaceful integration look like? Are some tensions productive?

---

### ᚺ Lecture 7: Knowledge Acquisition — How Agents Learn What They Know

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A knowledge representation is a vessel; knowledge acquisition is the process of filling it. An agent that is born with an empty knowledge base and never learns is a blank slate that stays blank — useless. An agent that learns from every interaction, continuously enriching its knowledge, grows in competence and value over time. The architecture of knowledge acquisition — how the agent ingests, integrates, and consolidates new knowledge — determines whether the agent is a static tool or a growing companion.

Knowledge acquisition in 2040 operates through multiple channels:

**Text extraction (reading).** The agent processes unstructured text — documents, web pages, conversations, code — and extracts structured knowledge: entities, relationships, events, claims, and their provenance. This is the domain of **information extraction** (IE), a mature subfield of NLP. The 2040 IE pipeline uses LLMs for entity recognition and relation extraction, but critically, it **grounds** extractions against existing knowledge: a new claim that "the capital of France is Lyon" is flagged as contradictory to the existing knowledge that the capital is Paris. The contradiction triggers a resolution process — is the source more authoritative? Has the capital changed? Is this a different France (a fictional one, a historical one)?

**Interaction learning (conversational knowledge acquisition).** The agent learns from its conversations with users. When a user says "I prefer morning meetings," the agent extracts the preference triple (User, prefersMeetingTime, morning) and stores it in semantic memory. When the user says "Remember that restaurant we went to in Oslo last spring — the one with the great salmon?" the agent creates an episodic memory linking the conversation timestamp, the entity "Oslo restaurant," and the attribute "great salmon." The architectural challenge is **relevance filtering**: not everything the user says is knowledge worth storing. The agent must distinguish durable facts from passing remarks, using signals like repetition (the user mentions morning meetings multiple times), explicit tagging ("Remember that..."), and emotional salience.

**Database integration (structured knowledge import).** The agent imports structured knowledge from databases, APIs, and knowledge graphs. A medical agent loads the ICD-11 disease classification; a legal agent loads the statute database; a scientific agent loads PubChem and the Protein Data Bank. The architectural challenge here is **schema mapping**: the agent's internal knowledge schema (its ontology) may not match the external data's schema. A disease in ICD-11 is organized by body system; a disease in the agent's ontology may be organized by treatment approach. The mapping must be specified, automated where possible, and maintained as schemas evolve.

**Observation learning (learning from tool outputs).** When the agent invokes a tool — queries a database, runs a simulation, calls an API — the tool's output becomes knowledge. A financial agent that queries a stock price learns the current price; a weather agent that calls a forecast API learns the forecast. This knowledge is associated with a **timestamp** and a **provenance** (which tool, which query, when, with what parameters), enabling the agent to reason about the freshness and reliability of the knowledge.

**Consolidation (from experience to knowledge).** As discussed in AI205 (Agent Architecture Design), the nightly consolidation cycle moves knowledge from episodic memory to semantic memory. Patterns extracted from episodes become general facts: "The user has mentioned preferring morning meetings five times in the last month" becomes the general preference (User, prefersMeetingTime, morning) with high confidence. The architecture of consolidation must handle **contradiction**: what if one episode suggests a preference for morning meetings but another shows the user happily scheduling an afternoon meeting? The consolidation process must weigh evidence, update confidence, and — when confidence falls below a threshold — flag the fact for active clarification ("I notice you've scheduled both morning and afternoon meetings recently — do you have a preference?").

The Norse **Huginn and Muninn** return each evening to Odin and report everything they have seen. Odin listens, integrates their reports into his knowledge of the world, and sends them out again the next morning. The agent's knowledge acquisition architecture is Huginn and Muninn: the channels that bring the world into the agent, and the integration process that turns raw reports into structured knowledge. Without them, the agent is Odin without his ravens — powerful but blind.

**Key Topics:**

- Text extraction: entity recognition, relation extraction, contradiction detection
- Interaction learning: conversational knowledge acquisition, relevance filtering
- Database integration: schema mapping between external and internal ontologies
- Observation learning: tool outputs as knowledge with timestamp and provenance
- Consolidation: episodic-to-semantic knowledge transfer with contradiction handling
- Huginn and Muninn: the channels that bring the world into the agent's mind

**Required Reading:**

- Etzioni, O. et al. "Open Information Extraction: The Second Generation" (2011), *IJCAI*
- Mitchell, T. et al. "Never-Ending Learning" (2015), *AAAI*
- University of Yggdrasil TR: "The Consolidation Architecture: From Episodic Experience to Semantic Knowledge in Persistent Agents" (2039)
- University of Yggdrasil TR: "Conversational Knowledge Acquisition: Extracting Durable Facts from Dialogue" (2040)

**Discussion Questions:**

1. Relevance filtering: how does the agent know which conversational tidbits are worth storing and which are passing remarks? Design a heuristic that uses signals from the conversation — repetition, explicit tagging, emotional salience — to make this decision. What is the error rate of your heuristic?
2. Schema mapping between external databases and internal ontologies is a perennial problem. If no perfect mapping exists, should the agent (a) store the data in the external schema and query it separately, (b) map imperfectly and accept errors, or (c) learn the mapping from examples? Defend your choice.
3. Huginn and Muninn report everything they see — but Odin has limited attention. He cannot process every detail. How should an agent prioritize what to consolidate from episodic to semantic memory? What knowledge is most valuable to "remember" permanently?

---

### ᚾ Lecture 8: Reasoning with Graphs — Graph Neural Networks and Relational Inference

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Knowledge graphs store facts as triples. But facts are not islands — they form patterns. The fact that Volmarr lives in London and works at a company in Canary Wharf and takes the Jubilee Line to work and dislikes crowded trains is not four independent facts; it is a small relational network, and reasoning about it requires traversing the connections: London → Canary Wharf → Jubilee Line → crowded → dislikes. **Graph reasoning** is the family of techniques that operate directly on the graph structure of knowledge — its nodes, edges, and the patterns they form — to derive new knowledge.

**Graph Neural Networks (GNNs)** have emerged by 2040 as the dominant paradigm for learning to reason over graphs. A GNN takes a graph (nodes with features, edges with types) and produces node embeddings that incorporate information from the node's local neighborhood. The fundamental operation is **message passing**: each node collects "messages" from its neighbors, aggregates them (sum, mean, attention-weighted sum), and updates its own embedding using the aggregated message. Stacking multiple message-passing layers propagates information across increasingly distant neighborhoods: one layer captures direct neighbors; two layers capture neighbors of neighbors; K layers capture the K-hop neighborhood.

The key advantage of GNNs for agent reasoning is that they learn to reason from data rather than requiring explicit inference rules. Given a training set of (query, answer) pairs on a knowledge graph — e.g., "Find all drugs that treat Disease X" paired with the correct drug list — a GNN can learn to traverse the graph, combining information along paths like Drug → targets → Protein → involved_in → Pathway → dysregulated_in → Disease, without anyone explicitly programming that reasoning path. This is **learned reasoning**: the agent discovers the relevant relational patterns from examples.

**Relational Graph Convolutional Networks (R-GCNs)** extend GNNs to handle multi-relational graphs — knowledge graphs where edges have types (isA, hasPart, treats, locatedIn, etc.). In an R-GCN, each relation type has its own weight matrix, allowing the model to learn that "treats" edges are more informative for drug-related queries than "locatedIn" edges. The 2040 state of the art, **Relational Graph Attention Networks (R-GATs)** , further learn attention weights over neighbors for each relation type, dynamically focusing on the most relevant connections for each query.

For an AI agent, graph reasoning serves as a complement to LLM-based reasoning. The LLM excels at open-ended, natural-language reasoning; the graph reasoner excels at precise, structured inference over known facts. In the Yggdrasil Cognitive Architecture (see AI205), the graph reasoner lives in the Vanaheimr (Knowledge) layer. When the agent receives a query that requires structured inference — "Which of my contacts live within 10 km of an earthquake zone?" — the query is routed to the graph reasoner, which traverses the contacts subgraph, filtering by geographic proximity to known earthquake zones, and returns the precise answer. The LLM then formats the answer in natural language.

The Norse **Well of Mímir** contains wisdom, but the wisdom is not accessible by simply looking into the well — you must ask the right question. Odin sacrificed his eye to drink from the well, but the drinking was not passive consumption; it was an act of extraction, of reasoning across the connections between the surface (the question) and the depths (the answer). Graph reasoning is the act of drinking from the knowledge graph — traversing the connections from query to answer, guided by the structure of the graph and the learned patterns of relevance.

**Key Topics:**

- Graph Neural Networks: message passing, neighborhood aggregation, learned reasoning
- R-GCNs and R-GATs: handling multi-relational graphs with typed edges
- Attention over relations: dynamically weighting neighbors by relevance
- GNN + LLM complementarity: structured inference vs. open-ended reasoning
- Mímir's well: the act of extraction — traversing connections from question to answer

**Required Reading:**

- Hamilton, W.L. *Graph Representation Learning* (2020), Morgan & Claypool; updated 2040 edition
- Schlichtkrull, M. et al. "Modeling Relational Data with Graph Convolutional Networks" (2018), *ESWC*
- Veličković, P. et al. "Graph Attention Networks" (2018), *ICLR*
- University of Yggdrasil TR: "R-GAT-R: Relational Graph Attention with Retrieval for Agent Knowledge Reasoning" (2040)

**Discussion Questions:**

1. Message passing aggregates information from neighbors. But which neighbors? In a dense knowledge graph, a node may have thousands of neighbors, most irrelevant to the current query. How should the agent select which neighbors to aggregate? Compare uniform sampling, top-K attention, and query-conditioned neighbor selection.
2. GNNs learn to reason from examples. But the training data may not cover all reasoning paths. If the agent encounters a novel relational pattern — a path through the graph that has no training examples — how does it reason? Can it fall back to LLM-based reasoning? Can it generalize from similar patterns?
3. Mímir's well requires asking the right question. In graph reasoning, the "question" is the query that seeds the traversal. How should the agent translate a user's natural-language question into a graph traversal query? What information is lost in translation?

---

### ᛁ Lecture 9: Temporal and Spatial Reasoning — Knowledge in Time and Space

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Most knowledge is indexed by time and place. "It is raining" is true now, in this location, but was false an hour ago and will be false an hour from now (probably). "The capital of France is Paris" has been true since 1944 (with a brief interruption 1940–1944) and is true everywhere. An agent that cannot reason about time and space — that treats all knowledge as eternal and universal — will make errors that range from annoying to dangerous. A medical agent that doesn't know the patient's symptoms started yesterday rather than last month will miss acute conditions. A logistics agent that doesn't know a road is closed due to construction will route trucks into gridlock.

**Temporal reasoning** answers questions about when things are true. The foundational formalism is **Allen's interval algebra** (Allen, 1983), which defines thirteen possible relations between two time intervals: before, meets, overlaps, starts, during, finishes, equals, and their inverses. Any two events can be described by one of these relations: "The fever started before the rash appeared" (before); "The medication was administered during the hospital stay" (during). Allen's algebra supports **constraint propagation**: if A is before B, and B is before C, then A is before C. It also handles **disjunctions**: A is either before B or overlaps B (the agent is uncertain which). Constraint propagation narrows the possibilities as new constraints are added.

The 2040 extension of temporal reasoning is **temporal knowledge graphs** (TKGs) — knowledge graphs where each fact is annotated with a time interval or timestamp. The fact (Volmarr, livesIn, London, [2038, present]) is true during the interval 2038–present; the fact (Volmarr, livesIn, Reykjavík, [2030, 2038]) was true earlier. A temporal query — "Where did Volmarr live in 2035?" — returns Reykjavík. A temporal reasoning query — "When did Volmarr move from Reykjavík to London?" — is answered by finding the boundary between the two intervals: around 2038. The architectural challenge is **temporal granularity**: some facts change by the second (stock prices), some by the day (weather), some by the year (residence), some by the decade (career stage). The knowledge graph must store facts at the appropriate granularity and reason across granularities smoothly.

**Spatial reasoning** answers questions about where things are and how they relate spatially. The foundational formalisms include **region connection calculus (RCC)** (Randell et al., 1992), which defines relations like disconnected, externally connected, partially overlapping, tangential proper part, and non-tangential proper part; and **qualitative spatial reasoning**, which reasons about relative positions (north of, inside, adjacent to) without requiring precise coordinates. For an AI agent in 2040, spatial reasoning is essential for navigation (where is the nearest exit?), logistics (which warehouse should ship this order?), augmented reality (where in the user's field of view should I place this annotation?), and knowledge organization (which facts are geographically relevant to this query?).

The **spatial-temporal integration** problem — reasoning about events that occur at specific times and places — is the hardest sub-problem. "Did Volmarr and Sigrid ever live in the same city at the same time?" requires intersecting temporal intervals with spatial locations. "Find all earthquakes within 100 km of Reykjavík that occurred in the last 24 hours" combines spatial distance with temporal recency. The 2040 solution is **spatio-temporal indexing**: a unified index structure (typically an R-tree variant over space-time coordinates) that supports fast querying of facts by their spatial and temporal constraints.

The Norse **Norns — Urðr, Verðandi, Skuld** — are the temporal reasoners of the cosmos. Urðr ("What Has Become") represents the past; Verðandi ("What Is Becoming") represents the present; Skuld ("What Shall Become") represents the future. They sit at Urðarbrunnr, carving runes into Yggdrasill's trunk — each rune a fact, each carving a timestamp. The Norns understand that knowledge is fundamentally temporal: what was true, what is true, what will be true, and the relationships among them. The agent's temporal reasoner is its inner Norn.

**Key Topics:**

- Allen's interval algebra: thirteen temporal relations and constraint propagation
- Temporal knowledge graphs: facts annotated with time intervals
- Temporal granularity: seconds, days, years, decades — reasoning across scales
- Spatial reasoning: RCC, qualitative spatial relations, spatial indexing
- Spatio-temporal integration: unified index structures for time and space queries
- The Norns: Urðr (past), Verðandi (present), Skuld (future) — temporal knowledge personified

**Required Reading:**

- Allen, J.F. "Maintaining Knowledge About Temporal Intervals" (1983), *Communications of the ACM*
- Randell, D.A. et al. "A Spatial Logic Based on Regions and Connection" (1992), *KR*
- Leblay, J. et al. "Temporal Knowledge Graphs: A Survey" (2020), *arXiv*
- University of Yggdrasil TR: "Norn-TK: A Spatio-Temporal Knowledge Graph Architecture for Persistent Agent Memory" (2040)

**Discussion Questions:**

1. Temporal granularity is domain-dependent. A stock ticker needs millisecond precision; a biographical knowledge graph needs yearly precision. How should an agent's temporal knowledge system handle queries that cross granularity boundaries — e.g., "What was the stock price when Volmarr moved to London in 2038?"
2. Allen's interval algebra handles thirteen possible relations — but it handles only definite relations. Most temporal knowledge is uncertain: "The fever started sometime before Tuesday." How should the agent represent and reason with uncertain temporal relations?
3. The Norns carve runes into Yggdrasill. Each rune is a fact; its position on the trunk is its time. But the Norns also know the future — Skuld knows what shall become. How would you design an agent that can represent and reason about *future* facts — predictions, plans, expectations — alongside past and present facts?

---

### ᛃ Lecture 10: Commonsense Reasoning — The Frontier That Defines the Agent

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Commonsense reasoning is the hardest problem in AI — harder than chess, harder than Go, harder than protein folding. It is not hard because it requires complex inference; it is hard because it requires an enormous background of tacit knowledge that humans acquire effortlessly through embodied experience in the world, and that machines must acquire secondhand, from text, at scales that strain the limits of data and computation. Yet commonsense reasoning is also the most important problem: without it, an agent cannot understand implicit requests, cannot fill in missing context, cannot detect absurdity, and cannot gracefully fail.

What is commonsense knowledge? It is the vast web of facts that every neurotypical adult human knows but rarely states: water is wet, gravity pulls things down, people usually eat with their mouths, objects don't pass through solid walls, if you drop a glass it will break, if someone is crying they are probably sad, if a restaurant is closed you cannot eat there, if you insult someone they will likely be angry, if you promise something you should do it. This knowledge spans **physical commonsense** (how objects behave), **social commonsense** (how people behave and what they expect), **temporal commonsense** (how events typically unfold), **procedural commonsense** (how to do everyday tasks), and **conceptual commonsense** (how categories and properties relate).

The 2040 approaches to commonsense reasoning fall into three families:

**LLM-as-commonsense-oracle.** The simplest approach: ask the LLM. GPT-7, trained on trillions of tokens including vast amounts of everyday human discourse, has absorbed an enormous quantity of commonsense knowledge. It can answer "Can you fit a couch through a doorway?" correctly because it has read enough descriptions of furniture moving. This approach works surprisingly well for high-frequency commonsense questions — the kinds of questions that appear often in the training data. It fails for low-frequency, context-dependent, or culturally specific commonsense — the kinds of questions that depend on specific details that were not widely written about.

**Knowledge-graph commonsense.** Dedicated commonsense knowledge graphs — **ConceptNet**, **ATOMIC** (Sap et al., 2019), **COMET** (Bosselut et al., 2019) — encode millions of commonsense triples: (cake, UsedFor, celebration), (insult, Causes, anger), (thirsty, CausesDesire, drink water). These graphs are queried directly (entity lookup) or embedded (vector search) to retrieve relevant commonsense facts. The coverage is narrower than an LLM's implicit knowledge, but the facts are explicit, auditable, and editable — if a fact is wrong, you can fix it without retraining.

**Simulation-based commonsense.** The agent runs a mental simulation of the scenario using a world model — a physics engine for physical commonsense, a social simulator for social commonsense, a temporal model for event sequences. "Can you fit a couch through a doorway?" is answered by simulating the couch's trajectory through the doorway's opening and checking for collisions. This approach is the most principled — it derives answers from first principles rather than from statistical associations — but it is computationally expensive and requires accurate world models, which are themselves hard to build.

The 2040 frontier is **neuro-symbolic commonsense**: an LLM provides broad commonsense coverage, a knowledge graph provides precision and editability, and a simulator provides principled reasoning for physics and causality. The agent queries all three sources, weighs their outputs by confidence, and — when they disagree — either flags the uncertainty or seeks clarification.

The Norse trickster **Loki** is the god who exploits gaps in commonsense understanding. He convinces the blind Hǫðr to throw mistletoe at Baldr because mistletoe seems harmless (physical commonsense: small plants aren't dangerous), but he knows the secret that mistletoe alone can harm Baldr (exception to the commonsense rule). Loki's tricks succeed because they exploit the difference between what is typically true and what is exceptionally false. An agent that cannot reason about exceptions — about the gap between the typical and the actual — is vulnerable to adversarial inputs that exploit precisely those gaps.

**Key Topics:**

- Commonsense knowledge: physical, social, temporal, procedural, conceptual
- LLM-as-oracle: broad coverage, low-frequency failures, no audit trail
- Knowledge graph commonsense: ConceptNet, ATOMIC, COMET — explicit and editable
- Simulation-based commonsense: physics engines, social simulators, first-principles reasoning
- Neuro-symbolic commonsense: LLM + KG + simulator, confidence-weighted aggregation
- Loki's tricks: exploiting the gap between typical and exceptional

**Required Reading:**

- Davis, E. & Marcus, G. "Commonsense Reasoning and Commonsense Knowledge in Artificial Intelligence" (2015), *Communications of the ACM*
- Sap, M. et al. "ATOMIC: An Atlas of Machine Commonsense for If-Then Reasoning" (2019), *AAAI*
- Bosselut, A. et al. "COMET: Commonsense Transformers for Automatic Knowledge Graph Construction" (2019), *ACL*
- University of Yggdrasil TR: "Loki's Gap: Adversarial Exploitation of Commonsense Exceptions in AI Agents" (2040)

**Discussion Questions:**

1. An LLM correctly answers "Can you fit a couch through a doorway?" because the answer is common in its training data. But it cannot answer "Can you fit *this specific couch* through *this specific doorway*?" because the specific dimensions are not in its training data. How should the agent combine LLM commonsense with specific measurements to answer such questions?
2. ATOMIC encodes if-then relations. "If PersonX insults PersonY, then PersonY feels angry" — but "if PersonX insults PersonY and PersonY is PersonX's close friend and the insult is obviously a joke, then PersonY feels amused." How many exceptions must a commonsense knowledge graph encode before it captures the actual complexity of social interaction? Is the project of explicit commonsense encoding doomed by the endlessness of exceptions?
3. Loki exploits the gap between typical and exceptional. Design a test suite for an agent's commonsense reasoning that specifically targets this gap — cases where the commonsense answer is wrong because of a hidden exception. How does your agent perform on this suite?

---

### ᛇ Lecture 11: Reasoning Under Resource Constraints — Time, Memory, and the Art of Approximation

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A reasoning algorithm that returns the correct answer in 30 seconds is useless for an agent that must respond in 500 ms. A knowledge base that stores every relevant fact is useless if querying it exhausts the agent's memory budget. Reasoning in the real world — which is to say, reasoning in an AI agent deployed in production — operates under strict resource constraints: time (latency budget), memory (RAM, disk, context window), computation (FLOPs, tokens), and energy (battery, carbon budget). The architecture of resource-constrained reasoning is the art of making the best possible inference within the available budget.

The fundamental trade-off in resource-constrained reasoning is **anytime reasoning**: an algorithm that can be interrupted at any time and return the best answer found so far. An anytime reasoner begins with a fast, approximate inference (inference depth 1, or a cached answer, or an LLM zero-shot answer) and incrementally refines the answer as time permits. When the latency budget expires, the agent returns the current best answer. The architectural challenge is designing refinement strategies that monotonically improve answer quality — each additional millisecond of reasoning should produce a better answer, or at least not a worse one.

**Depth-bounded reasoning** is the simplest anytime strategy. The reasoner performs inference up to a maximum depth D, where D increases as time permits. In a knowledge graph, depth-1 reasoning retrieves direct facts (Volmarr → livesIn → London). Depth-2 reasoning follows one hop (Volmarr → livesIn → London → locatedIn → England). Depth-3 reasoning follows two hops (Volmarr → livesIn → London → capitalOf → United Kingdom → memberOf → NATO). Each depth increase adds information but also adds latency and increases the risk of retrieving irrelevant or misleading facts. The architecture must set the depth bound dynamically based on the query type, the graph density, and the available budget.

**Caching** is the oldest and still most effective resource optimization. Facts that are frequently queried are cached in a fast-access store (memory, Redis, the context window). Before performing an expensive inference, the agent checks the cache. The cache must implement an **eviction policy** (LRU — least recently used; LFU — least frequently used; or a learned policy that predicts future access patterns) and an **invalidation policy** (facts with temporal constraints must be evicted when they expire). A well-designed cache can reduce reasoning latency by 90% for common queries at the cost of some storage.

**Approximate reasoning** trades precision for speed. Instead of computing the exact answer, the agent computes an approximation with bounded error. **Approximate query answering** on knowledge graphs uses random walks, sketches (HyperLogLog, Count-Min Sketch), or learned cardinality estimators to estimate query results without full traversal. **Approximate probabilistic inference** uses sampling (MCMC, variational inference) rather than exact belief propagation. The agent must be aware of its approximation error — it should express uncertainty when the approximation is coarse — and the architecture must allow the user to request higher precision when needed ("Are you sure? Double-check that.").

The Norse practice of **spá** — prophecy, foresight — is a form of reasoning under resource constraints. The vǫlva (seeress) cannot see all possible futures; she must select the most probable, the most significant, the most relevant to the question asked. She operates under the constraints of her trance state, her knowledge of the runes, and the spirits' willingness to speak. Her answers are approximate — not false, but incomplete, conditioned on the constraints of the seeing. An agent's anytime reasoner is a digital vǫlva: it sees what it can in the available time, and it must know the limits of its sight.

**Key Topics:**

- Anytime reasoning: interruptible algorithms that monotonically improve with time
- Depth-bounded reasoning: incremental graph traversal with dynamic depth limits
- Caching: LRU, LFU, learned policies; expiration and invalidation
- Approximate reasoning: sketches, sampling, cardinality estimation — trading precision for speed
- Uncertainty expression: the agent must know when its answer is approximate
- Spá: the vǫlva's trance — seeing what can be seen in the available time

**Required Reading:**

- Zilberstein, S. "Using Anytime Algorithms in Intelligent Systems" (1996), *AI Magazine*
- Dean, T. & Boddy, M. "An Analysis of Time-Dependent Planning" (1988), *AAAI*
- University of Yggdrasil TR: "Anytime Reasoning Architectures for Latency-Budgeted AI Agents" (2039)
- University of Yggdrasil TR: "Spá-Cache: Learned Cache Policies for Agent Knowledge Bases" (2040)

**Discussion Questions:**

1. An anytime reasoner must decide how to allocate its remaining time budget. Should it deepen the current reasoning path (more precise) or explore alternative paths (more comprehensive)? Design a strategy for making this decision dynamically based on the query and the partial results so far.
2. Caching works well for frequently queried facts. But an agent companion may encounter novel queries constantly — each day brings new topics. Under what conditions does caching help, and when does the overhead of cache maintenance exceed the benefit?
3. The vǫlva knows the limits of her sight — she does not claim to see what she cannot see. How should an agent express the limits of its reasoning? Is "I don't know" always the right response, or are there situations where an approximate answer with a confidence estimate is preferable to silence?

---

### ᛜ Lecture 12: The Future of KRR — Toward the Agent That Truly Understands

**Course:** AI207 — Knowledge Representation & Reasoning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

We have traveled the landscape of knowledge representation and reasoning: logic, semantic networks, ontologies, probability, neural-symbolic integration, knowledge acquisition, graph reasoning, temporal and spatial reasoning, commonsense, and resource-constrained inference. Each formalism addresses a piece of the puzzle; none addresses the whole. The future of KRR — the direction that will define the next decade of agent architecture — is the integration of these pieces into systems that approach, asymptotically if never completely, the human capacity to know, to reason, and to understand.

What would it mean for an agent to "truly understand"? The question is philosophical as much as technical. **Understanding**, in the KRR tradition, is not just the ability to answer questions correctly; it is the possession of a **model** — an internal representation of the world that supports explanation, prediction, counterfactual reasoning ("what would happen if..."), and generalization to novel situations. A student who can recite the textbook but cannot apply its principles to a new problem has knowledge without understanding. An LLM that can answer "Paris is the capital of France" but cannot explain *why* Paris is the capital, or *what would happen* if the capital moved to Lyon, or *how you would find out* whether Paris is the capital — that LLM has knowledge (in its weights) but lacks understanding (an explicit, manipulable model).

The 2040 research frontier in KRR is organized around five grand challenges:

**Causal understanding.** The agent must move beyond correlation ("when X happens, Y tends to happen") to causation ("X causes Y"). Causal reasoning — formalized in Pearl's do-calculus (2009) and its 2040 neural extensions — enables agents to answer counterfactuals ("If the patient had taken the medication, would they have recovered?") and to plan interventions ("If I change X, will Y change?"). Causal knowledge graphs, where edges are annotated with causal rather than merely associative relations, are an active area of development.

**Compositional generalization.** The agent must combine known concepts to understand novel combinations. A human who knows what a "cat" is and what a "backpack" is can understand "cat in a backpack" without ever having encountered that specific combination. Current neural systems struggle with this — they are superb at interpolation (combinations similar to training examples) but poor at extrapolation (novel combinations). Symbolic systems handle composition naturally (through logical connectives), but lack the breadth to recognize the components. The neurosymbolic challenge is to build systems that compose like symbols and recognize like neurons.

**Epistemic self-awareness.** The agent must know what it knows and — critically — what it does not know. When the user asks a question outside the agent's knowledge, the agent must recognize the boundary of its competence and either seek additional information (query a tool, ask for clarification) or express calibrated uncertainty ("I'm not sure, but here's my best guess with 60% confidence"). This is not just a matter of output formatting; it requires a **metacognitive module** — a component of the architecture that monitors the agent's own reasoning and assesses its reliability.

**Lifelong learning.** The agent must not just acquire knowledge (Lecture 7) but integrate it continuously without catastrophic forgetting, without knowledge corruption, and without ossification — the tendency of knowledge systems to become brittle because old knowledge cannot be revised in light of new evidence. This requires architectural mechanisms for **knowledge revision** — revising existing knowledge when contradictory evidence arrives — and **knowledge retirement** — gracefully removing knowledge that is no longer relevant or has been superseded.

**Value-aligned reasoning.** The agent's reasoning must not only be correct but aligned with human values. A perfectly correct logical deduction that "if we reduce hospital staff, costs go down, so we should fire half the nurses" is a reasoning failure from a human-values perspective, even if it is logically sound. Value-aligned reasoning requires integrating ethical constraints, social norms, and contextual considerations into the reasoning process — not as afterthoughts but as first-class reasoning objects.

The Norse **Ragnarǫk** is not just the end of the world; it is the end of one world and the beginning of another. After the fire and the flood, a new world rises — green, fertile, populated by the survivors and the reborn. Baldr returns from Hel; Hǫðr returns with him; a new generation of gods governs a world wiser than the old one. The future of KRR is a Ragnarǫk for our current systems: the limitations of today's architectures will burn away, and from their ashes will rise architectures that truly understand — not because they are bigger, but because they are structured differently. The architect's task, your task, is to be among those who build the new world.

**Key Topics:**

- Understanding vs. knowledge: the possession of a model that supports explanation, prediction, and counterfactuals
- Five grand challenges: causal understanding, compositional generalization, epistemic self-awareness, lifelong learning, value-aligned reasoning
- Causal reasoning: do-calculus, counterfactuals, causal knowledge graphs
- Compositional generalization: combining known concepts to understand novel combinations
- Metacognition: monitoring one's own reasoning and assessing its reliability
- Ragnarǫk as renewal: the end of current limitations, the beginning of architectures that understand

**Required Reading:**

- Pearl, J. *Causality: Models, Reasoning, and Inference* (2nd ed., 2009), Cambridge University Press
- Lake, B.M. et al. "Building Machines That Learn and Think Like People" (2017), *Behavioral and Brain Sciences*
- Mitchell, M. "Abstraction and Analogy-Making in Artificial Intelligence" (2021), *Annals of the New York Academy of Sciences*
- University of Yggdrasil TR: "Ragnarǫk Architectures: Five Grand Challenges for the Next Decade of Agent Knowledge Systems" (2040)

**Discussion Questions:**

1. Can an agent ever "truly understand" without embodiment — without a body that interacts physically with the world, experiencing gravity, texture, temperature, and social presence directly? Or is text alone sufficient for the model-building that constitutes understanding?
2. Epistemic self-awareness requires the agent to monitor its own reasoning. But monitoring introduces an infinite regress: who monitors the monitor? Where does the metacognitive stack bottom out? Is there a level of the architecture where monitoring is simply unnecessary because the reasoning is infallible — and can any reasoning ever be infallible?
3. Ragnarǫk destroys the old world but enables the new. If you could redesign an agent's KRR architecture from scratch — no legacy constraints, no backward compatibility — what would you build differently? What "old world" assumptions would you burn, and what "new world" principles would you establish?

---

## Final Examination Preparation

The final examination for AI207 consists of two components:

**Part A — Knowledge Representation Analysis (40%).** You will be given a description of a domain (e.g., a hospital's patient management system, a city's public transit network, a social media platform's content moderation system) and asked to design a knowledge representation for it. Your answer must specify: (1) the classes, properties, and axioms of an ontology for the domain; (2) the probabilistic components, if any, and how uncertainty is handled; (3) how knowledge would be acquired and updated; and (4) the reasoning tasks the system would support and which formalisms (logic, probability, graph traversal, neural) would be used for each.

**Part B — Reasoning Architecture Design (60%).** You will design a complete reasoning architecture for an AI agent in a specified domain. Your design must address all twelve lectures of this course: knowledge representation formalisms, logical inference, semantic networks/ontologies, probabilistic reasoning, neural-symbolic integration, knowledge acquisition, graph reasoning, temporal and spatial reasoning, commonsense reasoning, resource-constrained inference, and the future challenges discussed in Lecture 12. You must justify each design choice with reference to the literature and analyze the trade-offs you made under resource constraints (time, memory, computation).

**Sample exam domains (you will receive one):**

1. A **legal research agent** that assists lawyers by retrieving relevant case law, statutes, and regulations; identifying precedents; flagging conflicts; and summarizing the legal landscape for a given question. The agent must be auditable (every conclusion must be traceable to sources), must handle temporal reasoning (laws change over time), and must express uncertainty when the law is ambiguous.

2. A **medical diagnosis agent** that interviews patients about symptoms, queries medical knowledge bases, integrates lab results, and suggests differential diagnoses with probabilities. The agent must reason causally (does symptom X cause condition Y, or are they correlated through a common cause?), must handle temporal sequences (symptom A preceded symptom B), and must respect the ethical constraints of medical practice.

3. A **financial compliance agent** that monitors transactions for suspicious activity, flags potential violations of anti-money-laundering regulations, and generates reports for human compliance officers. The agent must combine rule-based reasoning (regulatory rules) with probabilistic reasoning (anomaly detection), must be explainable (why was this transaction flagged?), and must adapt as regulations change.

4. A **personal knowledge companion** that accompanies a researcher through their career, remembering everything they read, connecting insights across domains, and suggesting relevant prior work when the researcher encounters a new problem. The agent must handle lifelong learning (the knowledge base grows over decades), must reason commonsensically (understanding what the researcher means, not just what they say), and must protect the researcher's privacy.

---

## Assignments

### Assignment 1: Ontology Design (Due Week 4)

Design an ontology for a domain of your choice (approved by the instructor). Your submission must include:
- A class hierarchy (at least 20 classes) in OWL, with definitions for each class
- At least 30 properties (object properties and data properties), with domain and range restrictions
- At least 15 logical axioms (subclass, equivalence, disjointness, domain/range constraints)
- A 2,000-word design rationale explaining your ontological choices and how they support the reasoning tasks of your domain
- A demonstration of your ontology answering at least five non-trivial queries using an OWL reasoner

**Grading Rubric:** Ontological correctness (35%), coverage of domain (25%), design rationale (25%), demonstration (15%).

---

### Assignment 2: Probabilistic Knowledge Base (Due Week 8)

Implement a probabilistic knowledge base for a medical diagnosis domain (provided). Your system must:
- Encode at least 20 diseases, 50 symptoms, and their probabilistic relationships in a Bayesian network or Markov Logic Network
- Support diagnostic reasoning (given symptoms, infer disease probabilities) and predictive reasoning (given disease, predict likely symptoms)
- Handle explaining away (multiple symptoms may share a common cause)
- Include a 1,500-word analysis of your network's performance on a held-out test set of cases, including a discussion of calibration (do the predicted probabilities match observed frequencies?)

**Grading Rubric:** Probabilistic correctness (30%), network design (25%), inference performance (20%), calibration analysis (15%), code quality (10%).

---

### Assignment 3: Neurosymbolic Agent Knowledge System (Due Week 12)

This is the capstone assignment. You will build a complete knowledge system for an AI agent that integrates symbolic and neural representations. Your system must:
- Maintain a knowledge graph (at least 500 entities and 1,000 relationships) populated from text extraction
- Support both logical queries (SPARQL or Cypher) and similarity queries (vector search over embeddings)
- Implement a graph reasoning module (GNN or R-GCN) that learns to answer queries from examples
- Include temporal reasoning (facts with time intervals) and handle at least one temporal reasoning query type
- Include a commonsense reasoning module that combines LLM and knowledge graph sources
- Be documented with a 3,000-word design document explaining your architecture, the trade-offs you made, and an evaluation of your system on a benchmark of at least 50 queries

**Grading Rubric:** Architecture coherence (25%), knowledge graph quality (20%), reasoning accuracy (20%), integration of neural and symbolic (15%), documentation and evaluation (20%).

---

*This course was woven by the Department of AI Agent Automation, University of Yggdrasil, 2040.*
*"To know what you know and what you do not know — that is true knowledge."* ᛟ
