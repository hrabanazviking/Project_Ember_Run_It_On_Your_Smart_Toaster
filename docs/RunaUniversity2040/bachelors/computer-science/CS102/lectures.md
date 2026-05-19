# CS102: Discrete Mathematics for Computing
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** None (co-requisite: CS101 Introduction to Programming)
**Description:** A rigorous introduction to the discrete mathematical structures that underpin all of computer science. Topics include propositional and predicate logic, proof techniques, set theory, functions and relations, combinatorics, recurrence relations, elementary number theory, graph theory, and an introduction to formal languages and automata. The course emphasizes computational thinking — the translation of mathematical abstraction into algorithmic reasoning — and prepares students for the theoretical demands of CS201 (Data Structures and Algorithms) and CS301 (Theory of Computation).

---

## Lectures

### Lecture 1: The Foundations of Mathematical Reasoning — Propositions, Truth, and the Limits of Language

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Before a computer can compute, a mind must reason. This opening lecture establishes the bedrock of formal mathematical discourse: propositional logic. We begin not with code but with the question of what it means for a statement to be true, false, or somewhere in between — a question that becomes startlingly urgent in the era of neural-symbolic AI systems that must themselves reason about propositions. The lecture traces propositional logic from Aristotle's *Organon* through Boole's *Laws of Thought* (1854) to the modern verification engines that prove correctness properties of the AI OS kernels studied in OS101.

#### Lecture Notes

Propositional logic treats declarative sentences — *propositions* — as atomic units that carry exactly one truth value: true (⊤, 1) or false (⊥, 0). This binary commitment, which Frege formalized in his 1879 *Begriffsschrift*, is the philosophical parent of every bit that ever flipped. Students must internalize that the law of excluded middle — every proposition is either true or false — is not a law of nature but a design choice. In 2040, quantum cognition research at UoY's Ginnungagap Lab challenges this very assumption: superpositional truth states have been observed in human reasoning about counterfactuals, as documented in Þorleifsdóttir and Chen's *"Fuzzy Edges of the Excluded Middle"* (UoY Press, 2039).

We introduce the five canonical logical connectives — negation (¬), conjunction (∧), disjunction (∨), implication (→), and biconditional (↔) — not merely as truth-functional operators but as the grammar of computational thought. Each connective corresponds to a fundamental programming pattern: ∧ to guard clauses, ∨ to branching, → to conditional execution, ¬ to invariant violation detection. The truth tables we construct are the first formal specifications students will ever write — specifications for the behavior of logical operators that every programming language must implement correctly.

A significant portion of this lecture is devoted to the translation of natural language into logical form, a skill that separates the competent programmer from the true computer scientist. "If the user is authenticated and the resource exists, then grant access" becomes (A ∧ R) → G. The ambiguity of English — does "or" mean inclusive or exclusive? — reveals why mathematics requires its own language. We examine the 2038 Ariane-7 satellite failure, traced to a natural-language specification that used "or" ambiguously in a thruster-control rule, causing a $2.4 billion loss. The formal specification would have prevented it.

#### Key Concepts
- The nature of propositions and the bivalence principle
- Truth-functional semantics for the five connectives
- Translating English conditionals into logical implication, with attention to contrapositive and converse
- Logical equivalence as a computational optimization — substituting cheaper expressions for expensive ones
- The material conditional paradox and its resolution in relevance logic

#### Required Reading
- Rosen, K.H. *Discrete Mathematics and Its Applications*, 9th ed. (2037), Chapter 1.1–1.3
- Þorleifsdóttir, S. and Chen, L. "Fuzzy Edges of the Excluded Middle: Quantum Cognition and the Foundations of Logic," *UoY Cognitive Systems Monographs*, 2039
- Whitehead, A.N. and Russell, B. *Principia Mathematica* (1910), selections from the Introduction — for historical perspective on what it took to ground mathematics in logic

#### Discussion Questions
1. If quantum cognition challenges the law of excluded middle for human reasoning, should AI systems built to model human cognition also abandon bivalence? What would a three-valued logic for AI look like?
2. Consider the statement "If this sentence is true, then the moon is made of cheese." Using the truth table for implication, is this statement true? What does your answer reveal about the material conditional?
3. In what ways does the translation from natural language to logic inevitably lose information, and how might a 2040 AI OS recover that lost context?

#### Practice Problems
- Construct truth tables for (p → q) ∧ (q → r) → (p → r) and verify it is a tautology
- Translate into propositional logic: "The system reboots only if a kernel panic occurs or the watchdog timer expires, but not both"
- Find a real-world software bug report (from GitHub issues, any major project) where ambiguous natural language caused a logic error, and formalize the fix

---

### Lecture 2: Predicate Logic and the Quantification of Thought

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Propositional logic cannot say "every process has a PID" or "there exists a memory address that is unallocated." For that we need *predicate logic* — the language of properties and relations, of "for all" and "there exists." This lecture introduces the syntax and semantics of first-order predicate calculus, the logical framework that underlies relational databases, type systems, formal verification, and the knowledge representation layers of every AI OS designed since 2030.

#### Lecture Notes

A predicate is a proposition with holes in it — a function from individuals to truth values. "x is prime" is a predicate P(x); it becomes a proposition only when we bind x to a specific number, or when we quantify over it. This distinction between *free* and *bound* variables is the logical analogue of the difference between a function parameter and a concrete argument — and confusing the two is among the most common errors in both mathematical proofs and program specifications.

The universal quantifier ∀ ("for all") and existential quantifier ∃ ("there exists") are the two great engines of mathematical generality. ∀x P(x) asserts that every object in the domain of discourse satisfies P; ∃x P(x) asserts that at least one does. The interplay between them, governed by De Morgan's laws for quantifiers (¬∀x P(x) ≡ ∃x ¬P(x) and ¬∃x P(x) ≡ ∀x ¬P(x)), is the logical foundation of the adversary argument in algorithm analysis — to prove a lower bound, you must show that for every algorithm, there exists an input on which it performs poorly.

We dedicate substantial time to the *domain of discourse* — the set of objects over which quantifiers range. In 2040, this concept has taken on new significance with the rise of *domain-adaptive AI OS layers* (see OS201), where the system must dynamically reconfigure its ontological commitments as it moves between, say, a medical diagnosis domain (where "everything" includes patients, symptoms, and drugs) and a network security domain (where "everything" includes packets, ports, and threat actors). The domain is not static; it is a runtime parameter.

Nested quantifiers are the crucible in which logical intuition is forged. The difference between ∀x ∃y L(x,y) ("everyone loves someone") and ∃y ∀x L(x,y) ("there is someone whom everyone loves") is the difference between a common platitude and a messianic claim. Students practice reading and writing multiply-quantified statements until the order of quantifiers feels as natural as the order of nested loops — because, fundamentally, that is what they are. A ∀x ∃y statement is a doubly-nested loop: for each x, search for a y; an ∃y ∀x statement is the much stronger claim that a single y works for all x simultaneously.

#### Key Concepts
- Predicates as parameterized propositions
- Universal and existential quantification, and their negations
- Free vs. bound variables, and the notion of scope
- Nested quantifiers and the critical role of quantification order
- Translating English sentences with "any," "every," "some," "none," "a" into quantified logical form
- The relationship between quantifiers and SQL's SELECT-FROM-WHERE semantics

#### Required Reading
- Rosen, Chapter 1.4–1.5
- Halpern, J.Y. *Reasoning About Knowledge* (2035 revised edition), Chapter 2 on the possible-worlds semantics that generalize quantification
- Date, C.J. *Database Design and Relational Theory* (2040), Chapter 6 on relational calculus as predicate logic applied to data

#### Discussion Questions
1. The statement "Nothing is better than eternal happiness. A ham sandwich is better than nothing. Therefore, a ham sandwich is better than eternal happiness" is a famous fallacy. Formalize it in predicate logic and identify the ambiguity.
2. In SQL, SELECT DISTINCT name FROM employees WHERE department = 'Engineering' implicitly uses which quantifier? What about SELECT name FROM employees WHERE EXISTS (SELECT * FROM projects WHERE projects.lead = employees.id)?
3. If an AI OS uses predicate logic for access control (∀u ∀r (has_clearance(u, r) → may_access(u, r))), what happens when the domain of discourse — the set of users and resources — changes at runtime due to hot-plugged hardware?

#### Practice Problems
- Negate: "Every CS102 student knows someone who has taken CS301 and passed with distinction."
- Write in predicate logic: "A graph is bipartite if and only if it contains no cycle of odd length."
- For the statement ∀ε > 0 ∃δ > 0 ∀x (|x - a| < δ → |f(x) - f(a)| < ε), identify the free variables and describe in English what property of f this expresses.

---

### Lecture 3: The Art of Proof — Direct, Contrapositive, and the Architecture of Certainty

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

A program is a proof of its specification, executed at runtime. This insight, known as the Curry-Howard correspondence, elevates proof from a merely academic exercise to the very fabric of software correctness. This lecture introduces the fundamental proof techniques — direct proof, proof by contrapositive, proof by contradiction, and proof by cases — treating them not as isolated tricks but as a systematic toolkit for constructing unassailable arguments about computational systems.

#### Lecture Notes

A mathematical proof is a chain of deductions, each link justified by a definition, an axiom, a previously established theorem, or a valid rule of inference. The chain must be inspectable by any rational agent — a requirement that in 2040 has been partially automated by proof assistants like Yggdrasil/Proof (the University's own verification environment, built on a dependent-type kernel inspired by Lean 5 and Coq 11), but whose fundamental principles every computer scientist must understand. When an AI OS (OS201) claims it has verified the safety of a kernel module, it is asserting the existence of a proof. Understanding what that means requires understanding proof itself.

We begin with direct proof of universal conditional statements: to prove ∀x (P(x) → Q(x)), assume an arbitrary element a satisfies P(a), then derive Q(a) through logical deduction. This universal generalization rule — "let a be arbitrary" — is the proof-theoretic counterpart of the programmer's "let x be any input of the expected type." The direct proof of "if n is odd, then n² is odd" (n = 2k + 1 ⇒ n² = 4k² + 4k + 1 = 2(2k² + 2k) + 1, which is odd) is a template for thousands of similar arguments students will encounter.

Proof by contrapositive exploits the logical equivalence (P → Q) ≡ (¬Q → ¬P). When a direct proof is obstructed — as it often is when the hypothesis P provides little structural leverage — the contrapositive may open a clear path. The classic example: "if n² is even, then n is even." Direct proof requires factoring n², which is messy. Contrapositive: "if n is odd, then n² is odd" — which we just proved directly. This strategic choice between attacking a theorem head-on or flanking it through its contrapositive mirrors the algorithmic choice between forward and backward chaining in automated reasoning systems.

Proof by contradiction — assume the negation of what you wish to prove and derive a logical absurdity — is the most philosophically contested yet practically indispensable technique. It underlies the diagonal argument (Lecture 9), the proof that √2 is irrational, and the undecidability of the halting problem. We trace its controversial history: from Euclid's proof of infinitely many primes, through Brouwer's intuitionistic rejection of excluded middle, to the 2038 discovery by Jónsson and Park that certain AI OS scheduling problems admit constructive proofs where previously only non-constructive contradiction proofs were known — a result with direct engineering implications.

#### Key Concepts
- Direct proof via universal generalization
- Proof by contrapositive as strategic redirection
- Proof by contradiction and the law of excluded middle
- Proof by cases (exhaustive enumeration of possibilities)
- The distinction between constructive and non-constructive existence proofs
- Common proof-writing errors: circular reasoning, insufficient justification, proof by example

#### Required Reading
- Rosen, Chapter 1.6–1.7
- Velleman, D.J. *How to Prove It: A Structured Approach*, 4th ed. (2038), Chapters 3–4
- Jónsson, E. and Park, S. "Constructive Scheduling Proofs for Microkernel AI OS Architectures," *Journal of Automated Reasoning*, vol. 62, 2038

#### Discussion Questions
1. Is proof by contradiction less "real" than direct proof? Consider: a contradiction proof that a number exists without constructing it tells you that number exists, but gives you no way to compute it. Does this matter for a computer scientist?
2. The Yggdrasil/Proof system refuses to accept non-constructive proofs of existence for executable specifications. Is this a feature or a limitation? When would you want to override it?
3. Consider the statement "All programs either halt or do not halt." This is true by excluded middle, but the halting problem says we cannot always determine which. What does this reveal about the gap between truth and provability?

#### Practice Problems
- Prove: if n is an integer and 3n + 2 is even, then n is even. (Try both direct and contrapositive — which is cleaner?)
- Prove by contradiction: there is no rational number whose square is 3.
- For each of the following, determine whether a constructive proof exists, and if not, prove it non-constructively: (a) there exist irrational numbers a and b such that a^b is rational; (b) every non-empty set of positive integers has a least element.

---

### Lecture 4: Mathematical Induction — The Engine of Recursive Reasoning

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Induction is the mathematical technique that justifies recursion, the algorithmic pattern that powers everything from divide-and-conquer sorting to AI tree search. This lecture treats induction not as a formula to memorize but as a principle of reasoning about infinite families of statements through finite means — a principle that, by 2040, has been extended to structural induction over recursive data types, well-founded induction over termination orderings, and coinduction over infinite data structures.

#### Lecture Notes

The principle of mathematical induction states: to prove that a property P(n) holds for all natural numbers n, it suffices to prove (1) P(0) — the base case, and (2) for arbitrary k, P(k) → P(k+1) — the inductive step. The metaphor of falling dominoes captures the intuition: if the first falls, and each knocks over the next, then all fall. But the metaphor conceals the logical force of the principle: induction is, ultimately, a consequence of the well-ordering principle (every non-empty set of natural numbers has a least element), and can be derived from it. Understanding this equivalence — induction ⇔ well-ordering ⇔ strong induction — gives students the flexibility to choose the most convenient formulation for any particular proof.

We distinguish *simple* from *strong* induction. In simple induction, the inductive hypothesis assumes P(k) to prove P(k+1). In strong induction, we assume P(0), P(1), ..., P(k) all hold to prove P(k+1). Strong induction is essential for proofs about recursively defined structures where the recursive case may depend on multiple smaller instances: the Fibonacci sequence (F(n) = F(n-1) + F(n-2)), the analysis of quicksort's partitioning, the proof that every integer greater than 1 can be factored into primes. In 2040, strong induction also underlies the *inductive bias* in neural-symbolic learning systems: when an AI OS learns a recursive concept from examples, its generalization to unseen cases is justified only if an inductive argument holds — a connection explored in our AI World Modeling curriculum (WM201).

A significant portion of this lecture is devoted to *structural induction* over recursively defined data types: natural numbers (base: 0, step: successor), lists (base: empty, step: cons), binary trees (base: leaf, step: node). This generalization, pioneered by Burstall (1969) and enshrined in proof assistants like Yggdrasil/Proof, allows us to prove properties of all programs that operate on recursive data. If we define a function `size(t)` on binary trees (size(leaf) = 0; size(node(L,R)) = 1 + size(L) + size(R)), structural induction proves that size(t) ≥ 0 for all trees t — a property that would be tedious to verify by testing alone.

The lecture closes with a warning and a wonder. The warning: induction proves *for all n*, but it does not tell you *which n* — an inductive proof of "there exists an n such that P(n)" without constructing n is a non-constructive existence proof with all the attendant philosophical baggage. The wonder: *coinduction*, the dual of induction, which proves properties of infinite data structures (streams, infinite trees, the denotational semantics of non-terminating programs) by showing that a property is preserved under *unfolding*. Coinduction is the mathematical basis for reasoning about reactive systems, lazy evaluation, and the infinite-horizon planning problems that WM303 addresses.

#### Key Concepts
- Simple induction: base case + inductive step (P(k) → P(k+1))
- Strong induction: assuming all smaller cases
- Equivalence of induction, strong induction, and well-ordering
- Structural induction over recursive datatypes
- Induction vs. coinduction: finite construction vs. infinite unfolding
- The relationship between inductive proofs and recursive program termination

#### Required Reading
- Rosen, Chapter 5.1–5.3
- Burstall, R.M. "Proving Properties of Programs by Structural Induction," *The Computer Journal*, 1969 — a classic that remains surprisingly relevant
- Sangiorgi, D. *Introduction to Bisimulation and Coinduction*, 2nd ed. (2036), Chapter 1 for coinduction motivation

#### Discussion Questions
1. "All horses are the same color." Find the error in this famous false inductive proof. (Hint: the inductive step fails for a specific small value of k.)
2. Why is induction not a valid method for proving properties of real numbers? What property of the natural numbers makes induction work?
3. Consider an AI OS that learns a sorting algorithm by observing sorted outputs. It generalizes and sorts any list correctly. Is this generalization justified by induction? If not, what is the fallacy?

#### Practice Problems
- Prove: 1 + 2 + ... + n = n(n+1)/2 for all n ≥ 1 (by simple induction)
- Prove: every amount of postage ≥ 12 cents can be formed using 4-cent and 5-cent stamps (requires strong induction)
- Define a binary tree data type. Prove by structural induction that a tree with n internal nodes has n+1 leaves.
- Find the flaw: Claim: a^n = 1 for all real a ≠ 0 and all n ∈ ℕ. "Proof": base case n=0, a^0=1. Inductive step: a^(k+1) = a^k · a^k / a^(k-1) [this step is false in general]

---

### Lecture 5: Sets, Functions, and the Cardinality of Thought

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Set theory is the unifying language of mathematics — the substrate into which every mathematical object, from numbers to graphs to probability spaces, can be encoded. For computer scientists, sets are simultaneously a theoretical foundation and a practical data structure (hash sets, bloom filters, disjoint-set unions). This lecture develops set theory from naive comprehension to the cardinality hierarchy, with special attention to the paradoxes that arise when we treat "collection" too casually — paradoxes that have direct analogues in the type-safety and Russell-style paradoxes of self-referential programs.

#### Lecture Notes

A set is a well-defined collection of distinct objects. The "well-defined" clause is doing enormous work: it rules out vague collections ("the set of all beautiful programs") and, crucially, the self-referential constructions that lead to Russell's Paradox. In 1901, Bertrand Russell asked: consider the set R of all sets that are not members of themselves. Is R ∈ R? If yes, then by definition R ∉ R. If no, then by definition R ∈ R. Contradiction. This single observation demolished Frege's life's work and drove the development of axiomatic set theory (Zermelo-Fraenkel with Choice — ZFC) that provides a rigorous, paradox-free foundation.

For computer scientists, Russell's Paradox is not a dusty historical curiosity. It is the logical cousin of the type-theoretic paradoxes that arise in programming languages with unrestricted self-reference. In 2040, with the advent of AI OS architectures that support *self-modifying code layers* (OS105), the question of how to permit useful self-reference without permitting paradox has moved from theory to engineering. UoY's contribution — the *stratified reflection* principle (Eiríksson et al., *"Safe Reflection in Layered AI OS Kernels,"* 2039) — ensures that a layer may reflect on the layers below it but never on its own consistency, a direct adaptation of Tarski's undefinability theorem.

The core set operations — union (∪), intersection (∩), difference (\), complement (with respect to a universe U), and Cartesian product (×) — must become as automatic as arithmetic. We prove their algebraic properties: commutativity, associativity, distributivity, De Morgan's laws. These proofs are exercises in the logical techniques from Lectures 1–4 and serve as a bridge to the Boolean algebra that underlies digital circuit design (CS103).

Functions are treated as special kinds of sets — sets of ordered pairs with the property that each element of the domain appears exactly once as the first component. The notions of injection (one-to-one), surjection (onto), and bijection (both) become the vocabulary for discussing data compression (injective encodings), hashing (surjective mappings from keys to buckets), and isomorphism (bijective structure-preserving maps between data types). The composition of functions, f ∘ g, is the mathematical parent of function composition in functional programming, and the inverse of a bijection is the mathematical guarantee that an encryption scheme can be decrypted.

#### Key Concepts
- Naive set theory and Russell's Paradox
- Set-builder notation and the axiom of separation
- Set operations and their algebraic laws
- Cartesian products and the set-theoretic definition of relations and functions
- Injections, surjections, bijections, and their computational significance
- Cardinality: finite, countably infinite, uncountable — a preview of Lecture 9's diagonal argument

#### Required Reading
- Rosen, Chapter 2.1–2.3
- Halmos, P.R. *Naive Set Theory* (1960, reprinted 2040), Chapters 1–8 — a classic that remains the most elegant short introduction
- Eiríksson, H., Nakamura, T., and Ólafsdóttir, K. "Safe Reflection in Layered AI OS Kernels," *UoY Technical Report TR-2039-07*

#### Discussion Questions
1. In a typed programming language, does the type of "all types that do not contain themselves" exist? Why or why not? What does this tell us about type system design?
2. If a set can be a member of itself (as permitted in some non-well-founded set theories), what would a "self-membered set" correspond to in programming — a data structure that contains itself? Can such a thing exist in a computer's finite memory?
3. Consider the function f: Programs → {halts, loops} that maps each program to whether it halts. Is this function well-defined? Is it computable? What does the distinction reveal?

#### Practice Problems
- Prove: A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C) using set-builder notation and logical equivalences
- Let A = {1, 2, 3}. List all functions f: A → A. Which are injective? Surjective? Bijective?
- Prove that if f: A → B and g: B → C are both injective, then g ∘ f is injective.
- Show that the set of all finite strings over the alphabet {0, 1} is countably infinite (i.e., has the same cardinality as ℕ).

---

### Lecture 6: Relations — The Hidden Structure Behind Every Data Model

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

If sets are the nouns of mathematics, relations are the verbs. They connect, compare, order, and partition. Every database table is a relation; every social network graph encodes a relation; every type hierarchy in an object-oriented language instantiates an ordering relation. This lecture develops the theory of relations — binary relations, their representations as matrices and digraphs, and the special properties (reflexivity, symmetry, transitivity) that define equivalence relations and partial orders — with continuous attention to their computational manifestations.

#### Lecture Notes

A binary relation R on a set A is, formally, a subset of A × A: a set of ordered pairs. Informally, it is any way of declaring that some elements are "related to" other elements. The sheer abstraction of this definition is its power: "is a parent of," "is less than," "is reachable from," "has the same hash as," "authenticates with the same token as" — all are relations, and all obey the same algebraic laws.

We identify the five fundamental properties a relation may have: *reflexive* (aRa for all a), *irreflexive* (aRa for no a), *symmetric* (aRb ⇒ bRa), *antisymmetric* (aRb ∧ bRa ⇒ a = b), and *transitive* (aRb ∧ bRc ⇒ aRc). Different combinations yield different relational "personalities." A relation that is reflexive, symmetric, and transitive is an *equivalence relation*, which partitions its domain into equivalence classes — the mathematical basis for abstract data types (two implementations are "equivalent" if they satisfy the same specification), for the quotient construction in algebra, and for the concept of observational equivalence in AI OS component verification (OS103).

A relation that is reflexive, antisymmetric, and transitive is a *partial order*, typically written ≤. Partial orders are the mathematical structure behind dependency resolution (package managers like NixOS's `nix` use topological sorting of the dependency partial order), task scheduling (Happens-Before is a partial order on distributed system events), and the type/subtype relation in programming languages. The Hasse diagram — a visual representation of a partial order with transitive edges omitted — is introduced as a practical tool for reasoning about these structures.

The *transitive closure* of a relation R, denoted R⁺, is the smallest transitive relation containing R. Computed by Warshall's algorithm (O(n³)) or by repeated matrix multiplication (O(n³ log n) with exponentiation by squaring, or O(n³) with Strassen-like techniques), transitive closure answers "is there a path?" — the fundamental question of graph reachability, authorization chain validation, and social network connection queries. In the 2040 context, AI OS trust management systems (OS203's "Gate of Remembrance") use transitive closure on the trust relation to determine whether principal A should be granted access based on a chain of delegated trust.

#### Key Concepts
- Relations as subsets of a Cartesian product
- Reflexivity, symmetry, antisymmetry, transitivity
- Equivalence relations and partitions
- Partial orders, Hasse diagrams, total orders
- Transitive closure and Warshall's algorithm
- Relational composition and its connection to database JOIN operations

#### Required Reading
- Rosen, Chapter 9.1–9.6
- Codd, E.F. "A Relational Model of Data for Large Shared Data Banks," *Communications of the ACM*, 1970 — the paper that invented relational databases, still required reading
- Schmidt, G. *Relational Mathematics* (2035), Chapters 1–3 for the modern algebraic treatment

#### Discussion Questions
1. Is "is a friend of" an equivalence relation on the set of people? Consider real social network data. What property is most likely to fail?
2. In OS203, the Gate of Remembrance uses trust delegation chains. If Alice delegates to Bob, and Bob delegates to Carol, the transitive closure grants Carol Alice's privileges. What are the security implications of a non-transitive trust relation?
3. Consider the "has the same birthday as" relation on the set of students in this class. Is it an equivalence relation? What are its equivalence classes? How many classes can there be at most?

#### Practice Problems
- Determine whether the relation R = {(a,b) | a - b is divisible by 3} on ℤ is an equivalence relation. If so, describe its equivalence classes.
- Draw the Hasse diagram for the divisibility relation on {1, 2, 3, 4, 6, 8, 12, 24}.
- Compute the transitive closure of R = {(1,2), (2,3), (3,4), (1,4)} on {1,2,3,4} using Warshall's algorithm.
- Prove: if R is symmetric and transitive, is R necessarily reflexive? (Careful: find a counterexample on a domain with isolated elements.)

---

### Lecture 7: Counting Without Counting — Combinatorics and the Mathematics of Possibility

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

How many possible passwords of length 8 exist over an alphabet of 95 printable ASCII characters? How many different binary search trees can store n distinct keys? How many ways can an AI agent traverse a 20×20 grid? These are combinatorial questions, and their answers — often astronomically large — determine the feasibility of brute-force attacks, the sample complexity of machine learning, and the state-space explosion that makes planning hard. This lecture develops the fundamental counting principles: the Rule of Products, the Rule of Sums, permutations, combinations, and the binomial theorem.

#### Lecture Notes

The *Rule of Products* (or multiplication principle) states: if a task can be decomposed into a sequence of k independent choices, where choice i has nᵢ options, then the total number of ways to perform the task is the product ∏nᵢ. This simple rule is the atomic building block of all combinatorial reasoning — and it is the source of the exponential growth that makes combinatorial spaces so vast. A password of length 8 over 95 characters yields 95⁸ ≈ 6.6 × 10¹⁵ possibilities. An AI that must search even a fraction of this space is doomed. The entire field of heuristic search (CS201) exists to cope with the consequences of the Rule of Products.

The *Rule of Sums* handles mutually exclusive alternatives: if task can be done in m ways OR in n ways, and these ways do not overlap, the total is m + n. The subtlety — and the source of most combinatorial errors — lies in ensuring the cases are genuinely disjoint. The Inclusion-Exclusion Principle, developed in Lecture 8, generalizes the Rule of Sums to overlapping cases.

*Permutations* count arrangements of distinct objects where order matters. The number of permutations of n distinct items is n! = n × (n-1) × ... × 1. The explosion of n! — 10! = 3,628,800; 20! ≈ 2.4 × 10¹⁸; 60! exceeds the estimated number of atoms in the observable universe — is the combinatorial reason that the traveling salesman problem (TSP) is hard: checking every possible tour of n cities requires (n-1)!/2 permutations. In 2040, quantum algorithms for approximate TSP (explored in CS407) reduce this to polynomial time with an approximation ratio provably close to 1, but the factorial remains the specter that haunts exact optimization.

*Combinations* count selections where order does not matter. The binomial coefficient C(n, k) = n! / (k! (n-k)!), read "n choose k," counts the number of k-element subsets of an n-element set. Its ubiquity — from Pascal's Triangle to the binomial theorem to the Catalan numbers that enumerate binary trees — makes it perhaps the most important single function in discrete mathematics. We derive the formula from first principles (choose k ordered items: P(n,k) = n!/(n-k)! ways; divide by k! to account for the k! orderings of each subset), then explore Pascal's Identity: C(n, k) = C(n-1, k-1) + C(n-1, k) — the recursive heart of Pascal's Triangle and the basis for dynamic programming algorithms that compute binomial coefficients in O(n²) time while avoiding factorial overflow.

The *binomial theorem*, (x + y)ⁿ = Σ C(n, k) xⁿ⁻ᵏ yᵏ, connects combinatorics to algebra. Its computational implications span from the fast evaluation of polynomials (CS201) to the probabilistic analysis of randomized algorithms (CS305). The combinatorial proof of the binomial theorem — each term xⁿ⁻ᵏ yᵏ comes from choosing y from exactly k of the n factors — exemplifies the power of combinatorial reasoning over algebraic manipulation.

#### Key Concepts
- Rule of Products and the exponential explosion
- Rule of Sums and the requirement of mutually exclusive cases
- Permutations (with and without repetition)
- Combinations and binomial coefficients
- Pascal's Triangle and Pascal's Identity
- The binomial theorem and combinatorial identities
- The Pigeonhole Principle: if n items are placed into m containers and n > m, at least one container has ≥ 2 items

#### Required Reading
- Rosen, Chapter 6.1–6.4
- Graham, R.L., Knuth, D.E., and Patashnik, O. *Concrete Mathematics*, 3rd ed. (2030), Chapters 1 and 5 — the definitive text on combinatorial mathematics for computer scientists
- Stanley, R.P. *Enumerative Combinatorics*, vol. 1, 3rd ed. (2035), Chapter 1 for the deeper algebraic perspective

#### Discussion Questions
1. The Pigeonhole Principle sounds trivial — but it proves that in a room of 367 people, at least two share a birthday. What is the minimum number of people needed for a > 50% probability of a shared birthday? Does the smallness of the answer (23) surprise you? Why is human intuition so poor about combinatorial explosions?
2. An AI OS must assign 10,000 processes to 64 CPU cores. How many possible assignments exist? If checking each assignment takes 1 nanosecond, how long would exhaustive search take? What does this say about the need for heuristic schedulers?
3. The Catalan number C_n = C(2n, n)/(n+1) counts binary trees with n internal nodes. Why does the number of binary search tree shapes matter for the average-case analysis of tree operations?

#### Practice Problems
- How many distinct 5-card poker hands are possible from a 52-card deck? How many are "full houses" (three of one rank, two of another)?
- How many anagrams (including nonsensical ones) of "MISSISSIPPI" exist? (Account for repeated letters.)
- Prove the identity C(n, k) = C(n, n-k) (a) algebraically from the formula, and (b) combinatorially by finding a bijection between k-subsets and (n-k)-subsets.
- Using the Pigeonhole Principle, prove that in any set of n+1 integers from {1, 2, ..., 2n}, there exist two such that one divides the other.

---

### Lecture 8: Advanced Counting — Inclusion-Exclusion, Generating Functions, and Recurrence

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

The Rule of Sums fails when cases overlap. The Inclusion-Exclusion Principle repairs it, providing a systematic method for counting elements in unions of non-disjoint sets. This lecture extends the counting toolkit with inclusion-exclusion, generating functions (the bridge from combinatorics to analysis), and the systematic solution of recurrence relations — the discrete analogue of differential equations that govern everything from algorithm running times to population models.

#### Lecture Notes

The Inclusion-Exclusion Principle generalizes |A ∪ B| = |A| + |B| - |A ∩ B|. For three sets: |A ∪ B ∪ C| = |A| + |B| + |C| - |A ∩ B| - |A ∩ C| - |B ∩ C| + |A ∩ B ∩ C|. The pattern — alternately add and subtract intersections of increasing size — extends to n sets. The general formula, |∪Aᵢ| = Σ|Aᵢ| - Σ|Aᵢ ∩ Aⱼ| + Σ|Aᵢ ∩ Aⱼ ∩ Aₖ| - ... + (-1)ⁿ⁺¹|∩Aᵢ|, is the combinatorial manifestation of the logical principle that to count objects satisfying "at least one" property, you must correct for double-counting. Applications range from counting integers in [1..n] coprime to n (Euler's totient function) to counting derangements (permutations with no fixed points, the classic "hat-check problem") to computing the probability that a random surjection from an n-element set to an m-element set covers every element.

A *generating function* is a formal power series whose coefficients encode a sequence of interest. If a₀, a₁, a₂, ... is a sequence, its ordinary generating function is A(x) = Σ aₙ xⁿ. The magic of generating functions is that combinatorial operations on sequences (addition, convolution) correspond to algebraic operations on power series (addition, multiplication) — and algebraic manipulations can extract closed forms for sequences that resist direct combinatorial attack. We demonstrate with the classic example: the Fibonacci generating function. If F₀ = 0, F₁ = 1, and Fₙ = Fₙ₋₁ + Fₙ₋₂, then F(x) = Σ Fₙ xⁿ = x/(1 - x - x²). Partial fraction decomposition yields Binet's formula: Fₙ = (φⁿ - ψⁿ)/√5, where φ = (1+√5)/2 and ψ = (1-√5)/2 — a closed form for a recursively defined sequence, obtained through purely algebraic means.

*Recurrence relations* are equations that define terms of a sequence with reference to earlier terms. They are the discrete counterpart of differential equations, and their solution techniques mirror those from continuous mathematics. A *linear homogeneous recurrence with constant coefficients*, such as aₙ = c₁aₙ₋₁ + c₂aₙ₋₂ + ... + cₖaₙ₋ₖ, is solved by assuming aₙ = rⁿ, substituting to obtain the characteristic equation rᵏ - c₁rᵏ⁻¹ - ... - cₖ = 0, and forming the general solution as a linear combination of rᵢⁿ terms (with appropriate modifications for repeated roots). This technique directly yields the asymptotic running times of divide-and-conquer algorithms: the master theorem (CS201) is a specialized application of recurrence-solving to the form T(n) = aT(n/b) + f(n).

In 2040, recurrence relations have found new life in the analysis of *self-improving AI systems*. When an AI OS (OS403) stochastically reconfigures its own decision modules, the performance trajectory over time is governed by a non-linear recurrence whose stability properties determine whether the system converges to optimality or diverges into chaos. The mathematical tools of this lecture — characteristic equations, fixed-point analysis, generating-function asymptotics — are the same tools used to analyze those recurrences.

#### Key Concepts
- Inclusion-Exclusion Principle for finite unions
- Derangements and the hat-check problem
- Ordinary generating functions and the convolution product
- Solving recurrences via characteristic equations
- Linear homogeneous recurrences with constant coefficients
- The connection between recurrences and divide-and-conquer algorithm analysis

#### Required Reading
- Rosen, Chapter 8.5–8.6 (Inclusion-Exclusion), Chapter 8.1–8.2 (Recurrence Relations)
- Wilf, H.S. *generatingfunctionology*, 3rd ed. (2034), Chapters 1–2 — freely available and beautifully written
- Sedgewick, R. and Flajolet, P. *Analysis of Algorithms*, 3rd ed. (2038), Chapter 2 on recurrence methods

#### Discussion Questions
1. The number of derangements of n items is !n = n! Σ (-1)ᵏ/k! for k=0 to n. As n → ∞, !n/n! → 1/e. Why does e appear in a purely combinatorial problem?
2. Generating functions treat infinite series as formal objects without concern for convergence. Is this mathematically legitimate? What does it mean to say a formal power series "encodes" a sequence?
3. Consider the recurrence T(n) = 2T(⌊n/2⌋) + n log n. Solve it. What algorithm has this recurrence, and what does the solution tell us about its performance relative to the standard T(n) = 2T(n/2) + n?

#### Practice Problems
- How many integers between 1 and 1000 are divisible by 2, 3, or 5? (Use inclusion-exclusion.)
- Find the generating function for the sequence aₙ = C(m, n) for fixed m, and use it to prove Σ C(m, k) = 2ᵐ.
- Solve the recurrence: aₙ = 5aₙ₋₁ - 6aₙ₋₂ with a₀ = 2, a₁ = 5.
- A robot moves on a grid: each step is either (1,0) or (0,1). Find a recurrence for the number of paths from (0,0) to (m,n) and solve it.

---

### Lecture 9: Number Theory — The Sacred Arithmetic of Cryptography

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Number theory — the study of integers and their properties — was long considered the purest of pure mathematics, "queen of mathematics" with "no practical application." The invention of public-key cryptography in the 1970s shattered that illusion. Divisibility, modular arithmetic, primality, and the Euclidean algorithm are now the foundation of every secure communication channel on Earth — and, by 2040, of the quantum-resistant lattice-based cryptosystems that protect AI OS inter-component messaging. This lecture covers the elementary number theory essential for any computer scientist.

#### Lecture Notes

The *division algorithm* is not an algorithm but a theorem: for any integers a and b > 0, there exist unique integers q (quotient) and r (remainder) such that a = bq + r and 0 ≤ r < b. This simple fact is the basis of modular arithmetic: we say a ≡ b (mod m) when m divides (a - b). The integers modulo m, written ℤₘ, form a ring — and when m is prime, a field — in which addition, subtraction, multiplication, and (under conditions) division behave like ordinary arithmetic. The computational relevance is immediate: hash tables use modulo for bucket selection; cyclic buffers use modulo for index wrapping; checksums and CRCs use modulo for error detection; and the entire edifice of RSA and elliptic-curve cryptography is built on modular exponentiation.

The *greatest common divisor* gcd(a, b) and the *Euclidean algorithm* that computes it are among the most elegant constructs in all of mathematics. The algorithm — repeatedly replace (a, b) with (b, a mod b) until b = 0 — runs in O(log min(a,b)) steps, making it exponentially faster than trial division. Its extended version, the Extended Euclidean Algorithm, finds integers s and t such that sa + tb = gcd(a, b) — Bézout's Identity. This is the computational primitive behind modular inverse computation: a⁻¹ mod m exists precisely when gcd(a, m) = 1, and the extended Euclidean algorithm computes it.

Prime numbers are the atoms of the integer universe: every integer > 1 factors uniquely into primes (the Fundamental Theorem of Arithmetic). Primality testing — determining whether a given integer is prime — was transformed in 2002 by the AKS algorithm, the first deterministic polynomial-time primality test. In 2040, quantum algorithms (Shor's algorithm, running on early fault-tolerant quantum computers) can factor integers in polynomial time, threatening RSA. The cryptographic community's response — lattice-based cryptography, which relies on the hardness of the Shortest Vector Problem rather than factorization — is the subject of CS405 (Cryptography and Security). Understanding why factorization is believed hard requires understanding the number-theoretic landscape this lecture surveys.

We close with Fermat's Little Theorem: if p is prime and a is not divisible by p, then aᵖ⁻¹ ≡ 1 (mod p). This theorem, and its generalization by Euler (a^ϕ⁽ᵐ⁾ ≡ 1 mod m when gcd(a,m)=1), is the linchpin of RSA. The proof — using the fact that the non-zero elements of ℤₚ form a multiplicative group of order p-1, and in any finite group, every element's order divides the group order — is a perfect synthesis of number theory and the group theory developed in CS301.

#### Key Concepts
- Divisibility, the division algorithm, and modular arithmetic
- gcd, lcm, and the Euclidean algorithm (standard and extended)
- Prime numbers and the Fundamental Theorem of Arithmetic
- Modular inverses and linear congruences
- Fermat's Little Theorem and Euler's Theorem
- The Chinese Remainder Theorem and its computational applications
- Introduction to the RSA cryptosystem

#### Required Reading
- Rosen, Chapter 4.1–4.6
- Hardy, G.H. and Wright, E.M. *An Introduction to the Theory of Numbers*, 7th ed. (2039), Chapters 1–6 — the classic reference
- Shor, P.W. "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer," *SIAM Journal on Computing*, 1997 — the paper that launched a thousand quantum cryptography startups

#### Discussion Questions
1. Why is factorization believed to be hard while multiplication is easy? What property of these operations makes this asymmetry possible, and is it proven that factorization is hard?
2. Fermat's Little Theorem provides a probabilistic primality test: if aⁿ⁻¹ ≢ 1 mod n for some a, then n is composite. Carmichael numbers pass this test for all a coprime to n despite being composite. What does the existence of Carmichael numbers tell us about the limitations of heuristic testing?
3. In 2040, Shor's algorithm has been demonstrated on 2048-bit integers in laboratory settings. If RSA is dead, what role does elementary number theory still play in the post-quantum cryptographic landscape?

#### Practice Problems
- Compute gcd(252, 198) using the Euclidean algorithm, showing all steps.
- Find the inverse of 7 modulo 26 using the Extended Euclidean Algorithm.
- Solve the system of congruences: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7) using the Chinese Remainder Theorem.
- Use Euler's Theorem to compute 7²⁵⁶ mod 10.

---

### Lecture 10: Graph Theory I — Vertices, Edges, and the Shape of Connection

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Graphs are the universal language of connection. Social networks, the hyperlinked structure of the web, the call graph of a program, the state space of a planning problem, the dependency tree of a build system — all are graphs. This lecture introduces the fundamental definitions, representations, and properties of undirected graphs, establishing the vocabulary that will be used throughout the CS curriculum and, increasingly, throughout the AI OS curriculum (where the "Nine Realms" architecture of OS201 is fundamentally a graph-partitioning problem).

#### Lecture Notes

A graph G = (V, E) consists of a set V of vertices (or nodes) and a set E of edges, where each edge is an unordered pair of vertices. This definition is so simple that its expressive power seems implausible — yet from it flows the entire body of graph theory, with applications spanning network routing (CN201), compiler optimization (register allocation via graph coloring), AI planning (A* search over state-space graphs), and the analysis of the neural architectures studied in WM201.

Graph representation is our first encounter with the theory-practice gap in computer science. The two canonical representations — adjacency matrices and adjacency lists — offer a time-space tradeoff that every algorithm designer must navigate. An adjacency matrix M[i][j] = 1 iff edge (i,j) exists, giving O(1) edge-existence queries at the cost of O(|V|²) space, regardless of edge count. An adjacency list stores for each vertex a list of its neighbors, giving O(degree(v)) edge queries but O(|V| + |E|) space, which is optimal for sparse graphs. The choice between them permeates graph algorithm design: BFS and DFS prefer adjacency lists; Floyd-Warshall requires an adjacency matrix. In 2040, the dominance of sparse graphs in practice (the web's average degree is < 20; social networks, despite high clustering, have average degree < 200) means adjacency-list representations are the default.

We develop the core vocabulary: degree, path, cycle, connectivity, component, bipartite. A graph is *connected* if there is a path between every pair of vertices. The *connected components* partition the vertex set into maximal connected subgraphs — a concept that finds immediate application in image segmentation algorithms, cluster analysis, and the detection of isolated modules in an AI OS component graph. A graph is *bipartite* if its vertices can be partitioned into two sets such that every edge crosses between them. The characterization — a graph is bipartite iff it contains no odd cycle — is both a theorem and an algorithm: attempt to 2-color the graph with BFS; if a conflict arises, an odd cycle has been found.

*Trees* — connected acyclic graphs — deserve special attention. A tree on n vertices has exactly n-1 edges, and any two of the properties {connected, acyclic, n-1 edges} imply the third. Trees are the optimal connected sparse structure, and they appear everywhere: the DOM is a tree; file systems are trees; the parse tree of a program is a tree; the decision tree of an AI classifier is a tree; the spanning tree of a network ensures loop-free flooding. The *spanning tree* — a subgraph that is a tree and includes all vertices — is the mathematical object behind the minimum spanning tree algorithms (Kruskal, Prim) that optimize physical network layout and cluster analysis.

#### Key Concepts
- Graph definitions: vertices, edges, directed vs. undirected
- Adjacency matrices vs. adjacency lists
- Degree, paths, cycles, connectivity, components
- Bipartite graphs: definition and odd-cycle characterization
- Trees: definitions, properties, and computational significance
- Spanning trees and their applications

#### Required Reading
- Rosen, Chapter 10.1–10.3
- Diestel, R. *Graph Theory*, 6th ed. (2037), Chapter 1 — the standard graduate reference, but Chapter 1 is accessible to undergraduates
- Easley, D. and Kleinberg, J. *Networks, Crowds, and Markets* (2035), Chapters 2–3 for the social-network perspective on graph theory

#### Discussion Questions
1. A graph's adjacency matrix raised to the k-th power has (i,j) entry equal to the number of walks of length k from i to j. Prove this. What does this tell us about the relationship between linear algebra and graph theory?
2. Every tree is bipartite. Why? Can you 2-color a tree with BFS? Does the choice of root affect the coloring?
3. The OS201 "Nine Realms" architecture partitions an AI OS into nine functional domains connected by a sparse inter-realm communication graph. Why might a tree-structured communication topology be desirable? What are its failure modes?

#### Practice Problems
- Draw all non-isomorphic graphs on 4 vertices. How many are there? Which are trees?
- For a graph G = (V,E) where |V| = n, prove that if every vertex has degree at least n/2, then G is connected. Is this bound tight?
- Prove that a tree with n ≥ 2 vertices has at least two leaves (vertices of degree 1).
- Implement BFS from a given source vertex. What data structure does BFS use, and what property of graph distances does this guarantee?

---

### Lecture 11: Graph Theory II — Traversal, Coloring, and the Algorithmic Landscape

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

Graphs become powerful not merely as static descriptions but as the substrate for algorithms. This lecture covers the two fundamental graph traversals — breadth-first search (BFS) and depth-first search (DFS) — and develops graph coloring as a gateway to the theory of NP-completeness. By the end, students will understand not only how graph algorithms work but why some graph problems are easy while others appear intractable — a distinction that echoes through every subsequent CS course.

#### Lecture Notes

*Breadth-first search* explores a graph in concentric layers from a source vertex. Using a FIFO queue, it visits all vertices at distance 1, then all at distance 2, and so on. BFS computes shortest paths in unweighted graphs — a fact that follows from the invariant that the queue always contains vertices in non-decreasing order of distance. This makes BFS the core of algorithms for web crawling (distance from seed pages), social network analysis (degrees of separation), and the unweighted shortest-path computations that underpin the "Six Degrees of Kevin Bacon" phenomenon and its serious cousin, the small-world property observed in real networks.

*Depth-first search* explores by going as deep as possible along each branch before backtracking. Using a LIFO stack (or recursion), DFS produces a classification of edges — tree edges, back edges, forward edges, cross edges — that reveals the graph's structural properties. A graph contains a cycle iff DFS discovers a back edge. Topological sorting (for directed acyclic graphs) is produced by ordering vertices by decreasing finish time. Strongly connected components are identified by two passes of DFS (Kosaraju's algorithm) or by Tarjan's single-pass algorithm. DFS is the intellectual parent of backtracking search, which underlies constraint satisfaction, SAT solving, and the planning algorithms used in autonomous AI agents (AI301).

*Graph coloring* assigns colors to vertices such that no adjacent vertices share a color. The *chromatic number* χ(G) is the minimum number of colors needed. The problem of determining χ(G) is NP-complete — a term we introduce here as the boundary between tractable and (believed) intractable computation. Even determining whether χ(G) ≤ 3 is NP-complete. Yet the *greedy coloring algorithm* — order vertices arbitrarily, assign each the smallest color not used by its neighbors — uses at most Δ(G)+1 colors (where Δ is the maximum degree), and for many graphs does much better. This gap between worst-case hardness and practical solvability is the defining tension of algorithmic computer science, and we will wrestle with it throughout CS201, CS301, and CS401.

The *four-color theorem* — every planar graph is 4-colorable — receives a brief historical treatment. Proved in 1976 by Appel and Haken using exhaustive computer case-checking (the first major proof to rely on computation), it was formally verified in Coq by Gonthier in 2005. The theorem's significance for this course is meta-mathematical: it exemplifies how computation can participate in mathematical proof, a theme that culminates in the Yggdrasil/Proof verification environment used throughout our curriculum.

#### Key Concepts
- BFS: layer-by-layer exploration, shortest paths in unweighted graphs
- DFS: edge classification, cycle detection, topological sort
- Greedy graph coloring and the Δ+1 bound
- Chromatic number and the NP-completeness barrier
- Planar graphs and the four-color theorem
- The computational role in modern mathematical proof

#### Required Reading
- Rosen, Chapter 10.4–10.8
- Cormen, T.H., Leiserson, C.E., Rivest, R.L., and Stein, C. *Introduction to Algorithms*, 5th ed. (2038), Chapters 20–22 on elementary graph algorithms
- Gonthier, G. "Formal Proof — The Four-Color Theorem," *Notices of the AMS*, 2008 — a readable account of the formal verification

#### Discussion Questions
1. BFS finds shortest paths in unweighted graphs. Why does it fail for weighted graphs? What property of BFS guarantees shortest-path optimality in the unweighted case, and which algorithm (preview of CS201) handles the weighted case?
2. DFS can be implemented recursively or iteratively with an explicit stack. In a language with limited stack depth (e.g., Python's default recursion limit of ~1000), which implementation is safer for exploring a graph with 10⁶ vertices in a long chain? Why?
3. Graph coloring is NP-complete, but register allocation in compilers — which is graph coloring on the interference graph — is done routinely for programs with thousands of variables. How is this possible? What makes real-world interference graphs easier than worst-case graphs?

#### Practice Problems
- Run BFS on a graph of your choice, showing the queue state at each step and the distance assigned to each vertex. Verify the distance invariant.
- Run DFS on the same graph, labeling each edge as tree, back, forward, or cross. Identify any cycles.
- Color the following graph greedily using the vertex order v1, v2, ..., v6: V={1..6}, E={(1,2),(1,3),(2,3),(2,4),(3,5),(4,5),(4,6),(5,6)}. How many colors did you use? Can you find a better ordering that uses fewer colors?
- Prove: if G is a bipartite graph, then χ(G) = 2. What about the converse?

---

### Lecture 12: Formal Languages and Automata — The Mathematical Soul of Computation

**Course:** CS102 — Discrete Mathematics for Computing
**Degree:** Bachelor of Science in Computer Science, 2040

---

#### Overview

What is a computation? The question admits many answers — Turing machines, lambda calculus, recursive functions — but all rest on a common foundation: the theory of formal languages and the automata that recognize them. This capstone lecture introduces finite-state machines, regular languages, and the Chomsky hierarchy, providing a preview of CS301 (Theory of Computation) while drawing together the logical, set-theoretic, and graph-theoretic threads woven throughout the course. Computation, we discover, is the systematic manipulation of discrete structures — and discrete mathematics is the language in which that manipulation is described.

#### Lecture Notes

A *formal language* over an alphabet Σ is simply a set of strings over Σ. The set of all valid Python programs, the set of all UTF-8 byte sequences, the set of all syntactically correct email addresses — each is a formal language. The central question of formal language theory is: for a given language L, what kind of computational device is needed to decide membership in L? The answer stratifies languages into the *Chomsky hierarchy*, a four-level taxonomy that is simultaneously a classification of computational power and a roadmap for parser and compiler design.

*Finite-state automata* (FSA) occupy the lowest rung: *regular languages*. A deterministic finite automaton (DFA) is a 5-tuple (Q, Σ, δ, q₀, F) — states, alphabet, transition function, start state, accepting states. Given an input string, the DFA reads one symbol at a time, transitioning according to δ, and accepts if it ends in an accepting state. DFAs are the mathematical model of circuits without memory beyond a fixed number of states, of the lexical analyzers that tokenize source code, of the regular expressions that power text search. The equivalence of DFAs, NFAs (nondeterministic FA), and regular expressions — established by Kleene's Theorem — is one of the elegant unifications of theoretical computer science.

*Context-free grammars* (CFG) occupy the next rung: *context-free languages*. A CFG is a set of recursive rewrite rules (productions) of the form A → α, where A is a single non-terminal and α is a string of terminals and non-terminals. CFGs describe the syntax of programming languages — the nested structure of parentheses, if-else blocks, and arithmetic expressions that regular expressions cannot capture. The pushdown automaton (PDA) — an FSA augmented with a stack — recognizes exactly the context-free languages. In 2040, CFGs also model the hierarchical structure of plans generated by AI planning systems (WM201), where task decomposition follows context-free production patterns.

The *Chomsky hierarchy* ascends through context-sensitive languages (recognized by linear-bounded automata) to *recursively enumerable languages* (recognized by Turing machines). The halting problem — the undecidability of whether an arbitrary Turing machine halts on a given input, proved by diagonalization (the method previewed in Lecture 5's discussion of cardinality) — establishes the fundamental limit of computation: there are well-defined problems that no algorithm can solve. This limit is not a technological shortcoming but a mathematical necessity, as inescapable as the irrationality of √2.

We close with the profound relevance of this theory to the AI OS architecture studied throughout our program. The OS401 "Þing" governance layer must decide whether a requested action is permitted by policy — a membership problem in a formal language of permissible action sequences. The OS201 "Yggdrasil" kernel must parse and validate inter-component messages against a context-free grammar of valid message formats. And the WM303 world-modeling engine must determine whether a predicted future state is reachable from the current state — a reachability problem in the graph of world configurations. In every case, the discrete mathematics of this course — logic, sets, relations, graphs, counting, and formal languages — provides the analytical framework. Mathematical maturity is not a prerequisite for computer science; it *is* computer science.

#### Key Concepts
- Formal languages as sets of strings
- Deterministic and nondeterministic finite automata
- Regular expressions and Kleene's Theorem
- Context-free grammars and pushdown automata
- The Chomsky hierarchy: Regular ⊂ Context-Free ⊂ Context-Sensitive ⊂ Recursively Enumerable
- Turing machines and the halting problem: the limit of computation
- The integration of discrete mathematics with AI OS architecture

#### Required Reading
- Rosen, Chapter 13.1–13.5
- Sipser, M. *Introduction to the Theory of Computation*, 4th ed. (2037), Chapters 1–2 (regular languages) and Chapters 3–4 (CFLs and Turing machines) — the definitive undergraduate text
- Turing, A.M. "On Computable Numbers, with an Application to the Entscheidungsproblem," *Proceedings of the London Mathematical Society*, 1937 — read the original to appreciate how modern it still feels

#### Discussion Questions
1. The language L = {aⁿbⁿ | n ≥ 0} is context-free but not regular. The language L' = {aⁿbⁿcⁿ | n ≥ 0} is not even context-free. What property of computational memory explains this progression? (Hint: think about counting.)
2. A DFA with n states can be minimized to the unique minimal DFA recognizing the same language. If an AI OS uses DFAs for policy enforcement, why might minimization matter for performance?
3. "The halting problem is undecidable" means no general algorithm can determine whether an arbitrary program halts. Yet in practice, we prove termination for specific programs using techniques like well-founded induction (Lecture 4). What is the relationship between the theoretical impossibility and the practical possibility?

#### Practice Problems
- Design a DFA that accepts binary strings divisible by 3. (Hint: states represent the remainder modulo 3.)
- Convert the regular expression (0 ∪ 1)*0 to an NFA using the construction from the proof of Kleene's Theorem, then convert to a DFA.
- Give a context-free grammar for the language of balanced parentheses, and draw the parse tree for the string (()()).
- Prove that the language {ww | w ∈ {0,1}*} is not context-free using the pumping lemma for CFLs.

---

## Final Examination Preparation

The final examination for CS102 will be a three-hour written paper. Students must answer **four (4) of eight (8)** essay-style questions, each of which requires both mathematical precision and conceptual synthesis. A scientific calculator is permitted; no programmable devices are allowed.

### Sample Examination Questions

1. **Propositional and Predicate Logic.** Formalize the following argument in predicate logic and determine whether it is valid. If valid, provide a proof; if invalid, provide a counterexample. "Every Yggdrasil OS process has a security level. Some processes are unprivileged. Therefore, there exists a security level that is assigned to at least one unprivileged process." Discuss how the domain of discourse affects the validity of your formalization.

2. **Proof Technique.** Prove that √3 is irrational using proof by contradiction. Then, explain why the same proof technique fails for √4 (which is rational). What does this reveal about the conditions under which contradiction proofs involving unique prime factorization are valid?

3. **Induction and Recurrence.** The "Tower of Yggdrasil" puzzle has n disks and 3 pegs. Let T(n) be the minimum number of moves required to solve it. Derive a recurrence relation for T(n), prove by induction that T(n) = 2ⁿ - 1, and discuss the implications of this exponential growth for problems solvable by recursive decomposition.

4. **Combinatorics and Probability.** An AI OS deploys 10 security modules across 4 servers. Each module must be assigned to exactly one server, and each server can host any number of modules. (a) How many distinct assignments exist? (b) How many assignments ensure that no server is empty? Use Inclusion-Exclusion for part (b). Discuss the relevance of these counting problems to load-balancing strategy analysis.

5. **Number Theory and Cryptography.** (a) Compute the RSA public and private keys for primes p = 61, q = 53, choosing e = 17. (b) Encrypt the message M = 42 using your public key. (c) Explain why the security of RSA depends on the computational asymmetry between multiplication and factorization. (d) In the post-quantum era of 2040, what number-theoretic problems are replacing factorization as the basis of cryptography?

6. **Graph Theory and Algorithms.** Define the adjacency matrix A of a graph. Prove that the (i,j) entry of Aᵏ equals the number of walks of length k from vertex i to vertex j. Use this result to design an algorithm that counts the number of triangles in a graph, and analyze its time complexity. How does your algorithm compare to a direct combinatorial approach?

7. **Relations and Equivalence.** Consider the relation R on the set of all finite strings over {0,1} defined by: aRb iff the number of 1's in a equals the number of 1's in b, modulo 3. Prove R is an equivalence relation, describe its equivalence classes, and explain how the Myhill-Nerode Theorem relates this partition to the minimal DFA for the language of strings where the number of 1's is a multiple of 3.

8. **Formal Languages and Computation.** (a) Construct a pushdown automaton that recognizes the language L = {aⁱbʲcᵏ | i = j or j = k, i,j,k ≥ 0}. (b) Explain why L is not deterministic context-free. (c) Discuss the significance of the Chomsky hierarchy for the design of an AI OS's message-parsing subsystem: which level of the hierarchy is needed for configuration files, for programming language syntax, and for natural language commands?

### Research Paper Option (Honors Track)

Students enrolled in the CS Honors track may substitute the final examination with a research paper (4000–6000 words) on a topic bridging discrete mathematics and AI OS design. Approved topics include: applications of graph coloring to interference analysis in neural-symbolic computing, formal verification of recursive AI self-modification using structural induction, or the role of the Chomsky hierarchy in constraining the expressiveness of AI OS policy languages. All papers must include formal mathematical proofs and reference at least five peer-reviewed sources from 2035 or later.

---

**Course Code:** CS102
**Last Updated:** 2040-08-15
**Department:** Computer Science, University of Yggdrasil
**Instructor of Record:** Dr. Jóhann V. Björnsson, D.Phil. (Oxon.)
**Contact:** j.bjornsson@uoy.edu.aks
