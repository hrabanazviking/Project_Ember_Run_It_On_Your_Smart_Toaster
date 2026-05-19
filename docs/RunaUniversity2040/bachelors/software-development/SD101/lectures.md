# SD101: Computational Thinking & Logic
## Bachelor of Science in Software Development — University of Yggdrasil, 2040

**Credits:** 4
**Semester:** Year 1, Semester 1
**Prerequisites:** None
**Instructor:** Dr. Eira Lundström, Faculty of Computational Arts

> *"The computer was never about the machine. It was always about teaching the mind to see its own patterns, to trace the braided threads of logic back to their source. Computational thinking is the seiðr of the 21st century — not magic, but method."* — Eira Lundström, *Weaving Thought: A Heathen Programmer's Manifesto* (2038)

---

## Course Description

Computational Thinking & Logic introduces the fundamental mental frameworks that underpin all software development. This is not a programming course — it is a *thinking* course. Students learn to decompose complex problems, recognize patterns across disparate domains, abstract essential structures from incidental detail, and design algorithmic solutions with formal rigor. By 2040, the software industry has moved decisively beyond the "learn a framework, get a job" model toward deep computational literacy: the ability to reason about computation itself, regardless of language, platform, or paradigm. This course provides that literacy.

The course draws on three intellectual traditions: classical logic (from Aristotle through Boole to Gödel), algorithmic thinking (from al-Khwarizmi through Dijkstra to modern complexity theory), and the 2040-era synthesis of AI-augmented reasoning — where human intuition and machine inference collaborate rather than compete. Students will emerge able to think clearly about problems that have no obvious computational solution, and to design solutions whose correctness can be demonstrated rather than merely hoped for.

---

## Lectures

### ᚠ Lecture 1: What Computation Is — And What It Isn't

**Date:** Week 1, Session 1

#### Overview

This lecture establishes the foundational question of the course: What distinguishes computational thinking from other modes of reasoning? We examine the historical origins of computation as a *formal* activity — something that can be defined, analyzed, and guaranteed — and contrast it with heuristic reasoning, intuition, and trial-and-error. By the end, students should be able to articulate what makes a problem "computational" and recognize when computational thinking is the right tool for a given challenge.

#### Lecture Notes

The story of computation does not begin with the electronic computer. It begins, properly speaking, with the realization that *thought itself* can be formalized. When Aristotle laid out the syllogism in the *Organon* — "All men are mortal; Socrates is a man; therefore Socrates is mortal" — he was not merely doing philosophy. He was defining a primitive computational operation: given premises of a certain form, a conclusion follows with necessity. No interpretation required. No intuition. Just structure.

This thread runs through the Islamic Golden Age, where al-Khwarizmi's *Kitab al-Jabr wal-Muqabala* (c. 820 CE) gave us not only algebra but the very concept of an *algorithm* — a step-by-step procedure for solving a class of problems, guaranteed to terminate. It runs through Leibniz, who dreamed of a *calculus ratiocinator* that would settle all disputes by computation. And it runs through the 19th-century crisis in mathematics, when Cantor's set theory and Frege's logicism collided with Russell's paradox, forcing a reckoning with the limits of formal systems — a reckoning that culminated in Gödel's incompleteness theorems (1931), Turing's halting problem (1936), and Church's lambda calculus (1936).

What unifies these moments is a single insight: **computation is the systematic manipulation of symbols according to formal rules**. The symbols may be numbers, propositions, or strings in an alphabet. The rules may be axioms of arithmetic, inference rules of logic, or transition functions of a Turing machine. But the essential character is the same: given a well-defined input, the computation produces a well-defined output, and anyone who follows the same rules on the same input will get the same result.

In 2040, we have computational systems of staggering complexity — AI agents that compose poetry, architectural models that simulate entire cities, memory systems like Mímir's Well that store and retrieve knowledge across decades. But the foundational question remains the same: *What can computation do, and what can it not do?* This course begins with that question because everything else — every framework, every architecture, every deployment pipeline — depends on the answer.

**The Three Pillars of Computational Thinking.** We will organize the course around three conceptual pillars, each corresponding to a distinct mode of computational reasoning:

1. **Decomposition:** Breaking a problem into subproblems that can be solved independently and composed back together. This is not merely "divide and conquer" — it is the art of finding the *right* decomposition, one where the subproblems are genuinely independent and their solutions compose cleanly. Bad decomposition is worse than no decomposition at all.

2. **Pattern Recognition:** Identifying structural similarities between problems — even when they appear in different domains, at different scales, or in different languages. The programmer who sees that a scheduling problem and a graph-coloring problem are isomorphic has a power that no memorization of APIs can provide.

3. **Abstraction:** Stripping away incidental detail to reveal essential structure. Abstraction is the most difficult of the three pillars because it requires judgment: which details are essential, and which can be safely ignored? Get it wrong, and you abstract away the very thing you needed to solve.

Throughout the course, we will return to these pillars, using formal logic as our language of precision and algorithmic analysis as our measure of quality.

#### Required Reading

- Wing, J.M. (2006). "Computational Thinking." *Communications of the ACM*, 49(3), 33-35. [Seminal paper; we read it in 2040 as a historical document — what did Wing get right, and what did she miss?]
- Turing, A.M. (1936). "On Computable Numbers, with an Application to the Entscheidungsproblem." *Proceedings of the London Mathematical Society*, 42(1), 230-265. §§1-3. [Read the original — not a summary. Watch Turing invent the computer.]
- Lundström, E. (2038). *Weaving Thought: A Heathen Programmer's Manifesto*. University of Yggdrasil Press. Chapter 1: "The Loom and the Algorithm."

#### Discussion Questions

1. Wing argued in 2006 that computational thinking is "a fundamental skill for everyone, not just computer scientists." In 2040, with AI agents handling most routine programming tasks, is this claim stronger or weaker? Why?
2. Consider a non-computational domain (e.g., poetry, cooking, or parenting). Are there aspects of these activities that resist formalization? What does the boundary between computable and non-computable look like in practice?
3. Lundström draws a parallel between weaving on a warp-weighted loom and algorithmic decomposition. Is this metaphor illuminating, or does it risk romanticizing what is essentially a mechanical process? Defend your position.

---

### ᚢ Lecture 2: Propositional Logic — The Skeleton of Reason

**Date:** Week 1, Session 2

#### Overview

We begin our study of formal logic with propositional calculus: the simplest logical system capable of expressing non-trivial reasoning. Students learn the syntax and semantics of propositional logic, the truth-table method for evaluating logical expressions, and the concept of logical equivalence. This lecture provides the formal vocabulary that will underlie everything else in the course.

#### Lecture Notes

If computation is the manipulation of symbols according to rules, then logic is the study of *which rules preserve truth*. This is not merely an academic distinction — it is the difference between a program that works and one that merely appears to work under testing.

**Syntax.** Propositional logic has a stark, almost runic simplicity. The alphabet consists of:
- **Atomic propositions:** *p, q, r, …* — statements that are either true or false, with no internal logical structure.
- **Connectives:** ¬ (not), ∧ (and), ∨ (or), → (implies), ↔ (iff). Each connective has a precise, unambiguous meaning defined by its truth table.
- **Parentheses:** Used to disambiguate complex expressions.

From these primitives, we build **well-formed formulas** (WFFs) by recursive construction: every atomic proposition is a WFF; if φ and ψ are WFFs, then ¬φ, (φ ∧ ψ), (φ ∨ ψ), (φ → ψ), and (φ ↔ ψ) are WFFs; nothing else is.

The key insight here is *compositionality*: the meaning of a complex expression is determined entirely by the meanings of its parts and the way they are combined. This is the same principle that underlies modular software design — a module's behavior should be determined by its components and their connections, with no hidden dependencies.

**Semantics.** The meaning of a propositional formula is given by a **valuation** — an assignment of truth values (T or F) to each atomic proposition. The truth value of a complex formula under a given valuation is computed recursively using truth tables:

| φ | ψ | φ ∧ ψ | φ ∨ ψ | φ → ψ | φ ↔ ψ |
|---|---|---|------|------|------|------|
| T | T |  T   |  T   |  T   |  T   |
| T | F |  F   |  T   |  F   |  F   |
| F | T |  F   |  T   |  T   |  F   |
| F | F |  F   |  F   |  T   |  T   |

And for negation: ¬T = F, ¬F = T.

Notice the material conditional (→) — it is the most misunderstood connective. "If p then q" is false *only* when p is true and q is false. In all other cases, it is true. This captures the idea of a promise: "If it rains, I will bring an umbrella." If it doesn't rain, the promise is not broken regardless of whether you bring an umbrella. In programming terms, → corresponds to the contract of a function: given valid input, it must produce valid output; given invalid input, all bets are off.

**Tautologies, Contradictions, and Contingencies.** A formula that is true under *every* valuation is a **tautology** (e.g., p ∨ ¬p — the law of excluded middle). One that is false under every valuation is a **contradiction** (e.g., p ∧ ¬p). Everything else is a **contingency** — its truth depends on the world.

Identifying tautologies is computationally significant. A tautology represents a truth that holds regardless of the state of the world — a "free theorem" in programming terminology. When you can prove that a condition in your code is a tautology, you can eliminate the check entirely. This is the logical foundation of compiler optimization and dead-code elimination.

**Logical Equivalence.** Two formulas are logically equivalent (φ ≡ ψ) if φ ↔ ψ is a tautology — that is, they have the same truth value under every possible valuation. Logical equivalence is the gold standard of program transformation: if you can prove that two code fragments are logically equivalent, you can replace one with the other with zero risk of changing behavior. This is what enables refactoring, optimization, and the entire field of formal verification.

#### Required Reading

- Huth, M. & Ryan, M. (2035). *Logic in Computer Science: Modelling and Reasoning about Systems* (4th ed.). Cambridge University Press. Chapter 1, §§1.1-1.3.
- Hofstadter, D.R. (1979). *Gödel, Escher, Bach: An Eternal Golden Braid*. Basic Books. Chapter VII: "The Propositional Calculus." [A classic; read it for the pleasure of watching Hofstadter think.]

#### Discussion Questions

1. The material conditional (→) often confuses students because it doesn't match the colloquial "if…then…" of everyday speech. Is this a flaw in the formalization, or a flaw in everyday speech? Should we fix the logic or fix the language?
2. Prove using truth tables that (p → q) ≡ (¬p ∨ q). What does this equivalence tell us about the nature of implication — that it reduces to simpler connectives?
3. In 2040, we increasingly write programs by *specifying* desired behavior to AI agents rather than *coding* explicit logic. Does propositional logic still matter in this paradigm? If so, how?

---

### ᚦ Lecture 3: Predicate Logic — The Flesh on the Skeleton

**Date:** Week 2, Session 1

#### Overview

Propositional logic is powerful but coarse-grained — it treats atomic propositions as indivisible units. Predicate logic (first-order logic) adds quantifiers, predicates, and variables, allowing us to express statements about *all* or *some* members of a domain. This lecture introduces the syntax and semantics of first-order logic and demonstrates its expressive power over propositional logic.

#### Lecture Notes

Propositional logic can say "it is raining" (p) and "I will bring an umbrella" (q), and even compose them into "if it is raining, then I will bring an umbrella" (p → q). But it cannot say "every person who goes outside in the rain brings an umbrella" — for that, we need to quantify over persons, to speak of properties (being a person, going outside in the rain) that may or may not hold of individuals.

**The Expressive Leap.** The essential addition of predicate logic is the **quantifier**. Where propositional logic talks about *this* fact and *that* fact, predicate logic talks about *all* facts of a certain kind. Consider:

- ∀x (Person(x) ∧ RainingOn(x) → HasUmbrella(x))  
  "For every x, if x is a person and it is raining on x, then x has an umbrella."

This single statement captures an infinite family of propositional statements — one for each possible person. The universal quantifier ∀ ("for all") and the existential quantifier ∃ ("there exists") are the logical analogues of loops in programming: they compress potentially infinite computation into finite specification.

**Syntax Extended.** To propositional logic we add:

- **Variables:** x, y, z, … — placeholders for individuals in the domain of discourse.
- **Predicates:** P(x), Q(x, y), … — functions from individuals to truth values. "x is a person," "x is taller than y."
- **Functions:** f(x), g(x, y), … — functions from individuals to individuals. "the mother of x," "the sum of x and y."
- **Quantifiers:** ∀x φ ("for all x, φ holds") and ∃x φ ("there exists an x such that φ holds").

A **term** is either a variable, a constant, or a function applied to terms. An **atomic formula** is a predicate applied to terms. The rest of the WFF definition extends propositional logic by adding: if φ is a WFF and x is a variable, then ∀x φ and ∃x φ are WFFs.

**The Domain Problem.** The semantics of predicate logic require a **domain of discourse** — a set of individuals that the quantifiers range over. This is both the power and the peril of predicate logic. "∀x Mortal(x)" means something completely different if the domain is {all humans} versus {all mammals} versus {all living things}. The choice of domain is a modeling decision, and getting it wrong is one of the most common sources of logical error in specification and verification.

In software terms, the domain is the *type system*. When you write `for item in collection:`, the quantifier ranges over the elements of that collection. Type-checking ensures that the predicates you apply actually make sense for those elements. This is why strong type systems matter — they prevent quantifier-domain mismatches that would otherwise manifest as runtime errors.

**Free and Bound Variables.** A variable occurrence is **bound** if it falls within the scope of a quantifier for that variable; otherwise it is **free**. A formula with no free variables is a **sentence** — it makes a definite claim whose truth depends only on the domain and the interpretation of predicates/functions. Sentences are the units of specification: when you write a program's contract, you write sentences, not formulas with free variables that would be ambiguous.

This distinction maps directly to programming: a bound variable is like a local variable declared within a loop or function — its scope is limited to that context. A free variable is like a global variable or an uninitialized reference — its meaning depends on context that is not specified within the formula itself.

#### Required Reading

- Huth & Ryan, Chapter 2, §§2.1-2.3.
- Smullyan, R.M. (2014). *A Beginner's Guide to Mathematical Logic*. Dover Publications. Chapters 4-5. [Smullyan is a master of making hard things clear; read him slowly.]

#### Discussion Questions

1. In natural language, "everyone loves someone" is ambiguous between ∀x ∃y Loves(x, y) (each person has someone they love) and ∃y ∀x Loves(x, y) (there is a single person whom everyone loves). How many such ambiguities exist in typical program specifications, and how do we guard against them?
2. Why do we need a domain of discourse? Couldn't we just quantify over "everything that exists"? (Hint: Russell's paradox.)
3. Modern AI agents (circa 2040) often use natural language specifications rather than formal logic. What is gained and lost in this transition?

---

### ᚨ Lecture 4: Proof Systems — Building Certainty from Uncertainty

**Date:** Week 2, Session 2

#### Overview

Truth tables work for propositional logic but explode combinatorially for predicate logic. To establish logical truths in richer systems, we need *proof systems* — formal rules for deriving conclusions from premises. This lecture introduces natural deduction for propositional logic, covering the introduction and elimination rules for each connective.

#### Lecture Notes

A truth table for a formula with *n* atomic propositions has 2^n rows. That's manageable for n = 10 (1,024 rows) but impossible for n = 100 (1.27 × 10^30 rows — more than the number of atoms in the observable universe). Predicate logic makes matters worse: a universal quantifier over an infinite domain produces an infinite truth table. We need a different approach.

**The Idea of Proof.** A proof is a finite sequence of formulas, each of which is either a premise (something we assume) or follows from earlier formulas by one of a small set of inference rules. The final formula in the sequence is the conclusion. If such a sequence exists from premises Γ to conclusion φ, we write Γ ⊢ φ ("Γ proves φ").

The crucial property of a proof system is **soundness**: if Γ ⊢ φ, then Γ ⊨ φ (if there's a proof, the conclusion logically follows from the premises — no proof can establish a false conclusion from true premises). The converse is **completeness**: if Γ ⊨ φ, then Γ ⊢ φ (if a conclusion logically follows, there exists a proof). For propositional logic, natural deduction is both sound and complete.

**Natural Deduction Rules.** Natural deduction, developed by Gerhard Gentzen in the 1930s, mirrors how mathematicians actually reason. Each connective has **introduction rules** (how to *prove* a formula with that connective) and **elimination rules** (how to *use* a formula with that connective):

*Conjunction (∧):*
- ∧-Introduction: From φ and ψ, infer φ ∧ ψ.
- ∧-Elimination: From φ ∧ ψ, infer φ (left) or ψ (right).

*Implication (→):*
- →-Introduction: If, by assuming φ, you can prove ψ, then you may infer φ → ψ (discharging the assumption φ).
- →-Elimination (Modus Ponens): From φ → ψ and φ, infer ψ.

*Negation (¬):*
- ¬-Introduction: If, by assuming φ, you can derive a contradiction (⊥), then infer ¬φ.
- ¬-Elimination: From φ and ¬φ, infer ⊥ (contradiction).

The →-Introduction rule is the most conceptually important. It captures the idea of **hypothetical reasoning**: "Suppose φ were true. Then… [reasoning]… therefore ψ. So, if φ then ψ." This is the logical analogue of writing a function: you assume the parameter has the right type (the hypothesis), you compute the result (the reasoning), and you conclude the function's type is input → output.

**The Curry-Howard Correspondence.** One of the deepest discoveries of 20th-century logic is the Curry-Howard correspondence: proofs in natural deduction correspond EXACTLY to programs in a typed lambda calculus. An assumption corresponds to a variable declaration. →-Introduction corresponds to lambda abstraction (function definition). →-Elimination corresponds to function application. A proposition corresponds to a type, and a proof corresponds to a program of that type.

In 2040, this correspondence has become the intellectual foundation of verified software. When you write a proof in a system like Coq, Agda, or the University of Yggdrasil's own Yggdrasil-Verify (2042), you are simultaneously writing a program — and the type-checker guarantees that the program meets its specification. This is not a metaphor; it is a mathematical identity.

**Example Proof.** Let's prove a simple theorem: (A → B) → ((B → C) → (A → C)). This is the transitivity of implication — if A implies B and B implies C, then A implies C.

```
1. A → B          [Assumption]
2. B → C          [Assumption]
3.   A            [Assumption for →I]
4.   B            [→E from 1, 3]
5.   C            [→E from 2, 4]
6. A → C          [→I from 3-5, discharging 3]
7. (B → C) → (A → C)  [→I from 2-6, discharging 2]
8. (A → B) → ((B → C) → (A → C))  [→I from 1-7, discharging 1]
```

Each step is justified by a rule. The proof is mechanical — a program could check it — yet it captures genuine reasoning. This is the magic of formal proof: it makes reasoning *auditable*.

#### Required Reading

- Huth & Ryan, Chapter 1, §§1.4-1.5.
- Wadler, P. (2015). "Propositions as Types." *Communications of the ACM*, 58(12), 75-84. [A beautiful, accessible exploration of Curry-Howard.]

#### Discussion Questions

1. The Curry-Howard correspondence tells us that proofs and programs are the same thing. Does this mean that every program is a proof? What would it mean for a program to be a "proof" — proof of what?
2. Natural deduction's →-Introduction rule requires *discharging* an assumption. In programming terms, this corresponds to closing over a variable. Trace the parallels and differences.
3. If AI agents can generate proofs automatically (as they can in 2040 for many classes of problems), does the human skill of constructing proofs still matter? Why or why not?

---

### ᚱ Lecture 5: Algorithms and Complexity — The Cost of Certainty

**Date:** Week 3, Session 1

#### Overview

Knowing that a solution exists is not enough — we need to know whether it is practically achievable. This lecture introduces algorithmic complexity analysis through the lens of asymptotic notation (Big-O, Ω, Θ) and the complexity hierarchy. We examine why some problems admit efficient solutions while others resist them, and what this means for the practicing software developer in 2040.

#### Lecture Notes

A proof tells us that a theorem is true. It does not tell us how hard it was to find. Similarly, an algorithm tells us that a problem can be solved; complexity analysis tells us whether it can be solved before the heat death of the universe. These are different questions, and confusing them is one of the most expensive mistakes in software engineering.

**The Asymptotic Lens.** When we analyze an algorithm, we ask how its resource consumption (time, memory, energy) grows as the input size grows. The key insight — due to Knuth, though the notation comes from Bachmann and Landau — is that constant factors matter less than growth rates for large inputs. An algorithm that takes 100n steps beats one that takes n² steps, not just eventually, but *dramatically*: for n = 1,000,000, the former takes 10^8 steps while the latter takes 10^12 — four orders of magnitude slower.

We formalize this with asymptotic notation:

- **O(f(n)):** Upper bound. The algorithm takes *at most* proportional to f(n) steps for sufficiently large n. "This sorting algorithm is O(n log n)."
- **Ω(f(n)):** Lower bound. The algorithm takes *at least* proportional to f(n) steps. "Any comparison-based sorting algorithm is Ω(n log n)."
- **Θ(f(n)):** Tight bound. Both O and Ω — the growth rate is exactly proportional to f(n).

**The Complexity Zoo.** Problems cluster into complexity classes based on the most efficient algorithms known for them:

- **P (Polynomial time):** Problems solvable in time O(n^k) for some constant k. Sorting, shortest paths, linear programming. These are the problems we consider *efficiently solvable*. In 2040, with quantum-accelerated classical hardware, the practical boundary of P has expanded considerably — problems with k = 6 or 7 are now tractable at scale.

- **NP (Nondeterministic Polynomial time):** Problems whose solutions can be *verified* in polynomial time, though finding them may require exponential search. Boolean satisfiability, the traveling salesman problem, graph coloring. The P vs. NP question — whether every problem whose solution can be verified quickly can also be *found* quickly — remains open in 2040, though the consensus has shifted: most complexity theorists now believe P ≠ NP, but the proof remains elusive.

- **Undecidable:** Problems for which no algorithm can exist at all. The halting problem (will an arbitrary program terminate?), Hilbert's tenth problem (does a Diophantine equation have integer solutions?), the equivalence problem for context-free grammars. These are not merely hard — they are *impossible*, and this impossibility is proven, not conjectured.

**Why Complexity Matters in the Age of AI.** In 2040, much routine programming is handled by AI agents — Hermes-class systems that can generate, test, and deploy code from natural language specifications. But AI agents are themselves computational processes. They consume resources. They can be asked to solve problems that are NP-hard or undecidable. Knowing complexity theory is what prevents you from asking your AI assistant to "find the optimal route for these 10,000 delivery drones in real time" — that's TSP, it's NP-hard, and no amount of AI magic will make it polynomial.

Complexity theory is the *engineering discipline* that backs computational thinking: it tells you not just *whether* you can solve a problem, but *at what cost*, and whether that cost is worth paying.

#### Required Reading

- Cormen, T.H., Leiserson, C.E., Rivest, R.L., & Stein, C. (2032). *Introduction to Algorithms* (5th ed.). MIT Press. Chapters 1-3.
- Aaronson, S. (2041). "P vs. NP: The State of the Question in 2040." *Annual Review of Computer Science*, 15, 1-28.

#### Discussion Questions

1. Quantum computing (now mainstream in 2040) solves some problems in BQP that are believed to be outside P, like integer factorization. Does this challenge the practical relevance of the P/NP distinction? Why or why not?
2. If AI agents can reliably solve many NP-hard problems *approximately* (within 1% of optimal), does the theoretical intractability of exact solutions matter in practice? Give examples where approximation is sufficient and where it is not.
3. Consider the problem: "Write a program that determines whether an arbitrary Python program contains an infinite loop." Is this decidable? What does your answer imply about the limits of automated code review?

---

### ᚲ Lecture 6: Decomposition — The Art of Dividing to Conquer

**Date:** Week 3, Session 2

#### Overview

Having established the logical and algorithmic foundations, we now turn to the first pillar of computational thinking: decomposition. This lecture examines strategies for breaking complex problems into manageable subproblems, with emphasis on recursion, dynamic programming, and the conditions under which decomposition succeeds or fails.

#### Lecture Notes

Decomposition is the most practical of the three pillars because it is the one you use every day, often without thinking. Every time you write a function, you are decomposing a larger task into a named sub-task. Every time you design a class, you are decomposing a system into components with defined responsibilities. The question is not whether you decompose, but whether you decompose *well*.

**The Golden Rule of Decomposition.** A decomposition is good if and only if the subproblems are *genuinely independent* — that is, solving one subproblem does not require information about how another subproblem is solved, except through explicitly defined interfaces. When subproblems are independent, you can:
- Solve them in parallel
- Test them in isolation
- Modify one without breaking another
- Assign them to different team members (or different AI agents)
- Replace one implementation with another without cascading changes

This is the principle behind modular design, microservices, and the Unix philosophy. It is also the principle behind recursion: solve the problem for a smaller instance, then combine.

**Recursive Decomposition.** The cleanest form of decomposition is recursion: define the solution to a problem of size *n* in terms of solutions to problems of size < *n*, with a base case for the smallest instances. Classic examples:

- **Merge Sort:** To sort a list of *n* elements, split it into two lists of size n/2, sort each recursively, then merge the sorted halves. The decomposition is clean because "sort the left half" and "sort the right half" are independent — they operate on disjoint data. Time: O(n log n).

- **Binary Search:** To find an element in a sorted array of size *n*, compare the target to the middle element. If it matches, done. If it's smaller, recursively search the left half; if larger, the right half. Each step halves the search space. Time: O(log n) — exponentially faster than linear search.

- **Tree Traversal:** To process a tree, process the root, then recursively process each subtree. The independence of subtrees makes this naturally parallelizable — each branch can be handled by a separate thread or agent.

**When Decomposition Fails.** Not every problem decomposes cleanly. Consider:

- **The Traveling Salesman Problem:** The optimal tour through *n* cities cannot be decomposed into "optimal tour through the first n/2 cities" plus "optimal tour through the rest" — the subproblems are interdependent because the path through the first half constrains where you enter the second half. Decomposition fails, and we pay the exponential price.

- **Concurrent Systems with Shared State:** If two threads access the same memory, their subproblems are not independent — the behavior of one depends on the timing of the other. This is why concurrent programming is hard, and why functional programming (which eliminates shared mutable state) is appealing.

- **Tightly Coupled Requirements:** When product requirements are contradictory — "the system must be both extremely secure and extremely easy to use" — neither "security" nor "usability" can be solved independently of the other. The decomposition fails at the requirements level, and no amount of clever architecture can fix it.

**Dynamic Programming.** Sometimes subproblems *overlap* but are not fully interdependent. Dynamic programming handles this case by solving each subproblem once and caching the result. The classic example is Fibonacci: F(n) = F(n-1) + F(n-2). A naive recursive implementation computes F(n-2) twice — once from F(n-1) and once from F(n-1)'s own recursive call. Dynamic programming stores F(k) after computing it, reducing the time from exponential to linear. The art of dynamic programming is recognizing when subproblems overlap and organizing the computation to exploit that overlap rather than suffer from it.

In 2040, AI-augmented IDEs can often suggest the right decomposition automatically. But they cannot *choose* the decomposition for you — because the choice of decomposition is a design decision that encodes your understanding of the problem. The AI can show you options; you must exercise judgment.

#### Required Reading

- Cormen et al., Chapters 4 (Divide-and-Conquer) and 15 (Dynamic Programming).
- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley. "Strategy" and "Composite" patterns. [These are decomposition patterns, nothing more and nothing less.]

#### Discussion Questions

1. Microservices architecture claims to solve the decomposition problem at the system level. What are the costs of decomposing too finely — of making subproblems *too* independent?
2. In pair programming with an AI agent (standard practice in 2040), who should decide the decomposition: the human, the AI, or both? Justify your answer with reference to the concept of *design intent*.
3. Consider a problem you have solved recently. Could you decompose it differently? What would change — performance, readability, maintainability?

---

### ᚷ Lecture 7: Pattern Recognition — Seeing the Isomorphism

**Date:** Week 4, Session 1

#### Overview

The second pillar of computational thinking is pattern recognition: the ability to see that two apparently different problems share a common structure. This lecture develops the skill of recognizing computational patterns — graph problems, optimization problems, constraint satisfaction problems — and mapping novel challenges onto known solution strategies.

#### Lecture Notes

An expert programmer does not have a larger mental library of algorithms than a novice. What the expert has is a richer set of *problem patterns* — abstract structures that cut across domains, languages, and scales. When presented with a new problem, the expert thinks: "This looks like a graph reachability problem" or "This is essentially a scheduling problem with resource constraints." Once the pattern is recognized, the solution strategy follows.

**The Pattern Language of Computation.** Just as Christopher Alexander documented the pattern language of architecture — "a courtyard that is too small feels like a shaft" — the software field has developed a pattern language of computational structures. Some of the most fundamental:

- **Linear scan:** Visit each element exactly once, in order. Use when the problem requires examining all elements and the order of examination doesn't matter for correctness (though it may matter for cache performance). Time: O(n). Examples: finding the maximum element, counting occurrences, validating a sequence.

- **Graph search (BFS/DFS):** Traverse a graph, visiting nodes reachable from a starting point. BFS (breadth-first search) finds shortest paths in unweighted graphs; DFS (depth-first search) is memory-efficient and natural for recursion. Use when the problem involves relationships, connections, or pathways.

- **Divide and conquer:** Split the problem, solve parts independently, combine. Use when subproblems are genuinely independent. Time: usually O(n log n) with log n levels of recursion.

- **Greedy:** At each step, make the locally optimal choice, hoping it leads to a globally optimal solution. Use when the problem has the *greedy-choice property* (a global optimum can be reached by local choices) and *optimal substructure* (optimal solutions contain optimal solutions to subproblems). Examples: Huffman coding, Dijkstra's shortest path (for non-negative weights).

- **Backtracking:** Systematically enumerate all possibilities, pruning branches that cannot lead to a solution. Use when the search space is too large for brute force but constraints can eliminate most candidates. Examples: constraint satisfaction, puzzle solving, scheduling with hard constraints.

**The Isomorphism Insight.** The deepest level of pattern recognition is recognizing that a problem *is* another problem — that it can be reduced to a known problem by a transformation. Examples:

- A *course scheduling problem* with prerequisites (some courses can't be taken until others are completed) is isomorphic to **topological sorting** of a directed acyclic graph.
- A *network routing problem* where you want to minimize total cable length connecting all nodes is isomorphic to the **minimum spanning tree** problem.
- A *resource allocation problem* where each resource can be assigned to one task and each task requires one resource is isomorphic to the **assignment problem** (a special case of min-cost max-flow).

Recognizing an isomorphism is a creative act — it requires seeing past surface features to underlying structure. It is also the skill that most distinguishes great programmers from merely competent ones, because it enables the great programmer to solve a new problem by applying a solution they already understand deeply.

**Pattern Recognition and AI.** In 2040, AI agents are excellent at pattern recognition *within* a known domain — they can spot a graph problem in a codebase faster than any human. But they struggle with *cross-domain* isomorphism — recognizing that a biological neural circuit, a social network phenomenon, and a compiler optimization share the same abstract structure. This is where human cognition, with its capacity for metaphor and analogy, remains indispensable. The best 2040 developers are those who can work *with* AI agents: let the AI handle within-domain pattern recognition, while the human focuses on the creative leaps that connect disparate domains.

#### Required Reading

- Gamma et al., *Design Patterns*. Read the introduction and the "Visitor" pattern as an example of encoding a traversal pattern.
- Alexander, C. (1977). *A Pattern Language*. Oxford University Press. [Skim — the patterns are about buildings, but the *idea* of a pattern language is universal.]
- Lakoff, G. & Johnson, M. (1980). *Metaphors We Live By*. University of Chicago Press. Chapter 1-3. [Metaphor is pattern recognition across conceptual domains — the cognitive basis of everything we're discussing.]

#### Discussion Questions

1. Describe a problem you have encountered outside computing that, on reflection, has the structure of a graph search or dynamic programming problem. What would it mean to "solve" that problem computationally?
2. AI agents in 2040 can translate natural language descriptions into code. Does this make pattern recognition skill *more* or *less* important for human developers? Defend your position.
3. The "Three Wells Isomorphism" (Lundström, 2038) identifies a pattern — immutable log, queryable memory, raw event stream — that recurs across mythology, cognitive architecture, and system design. Is this a genuine isomorphism or a forced analogy? How would you tell the difference?

---

### ᚹ Lecture 8: Abstraction — The Art of Knowing What to Ignore

**Date:** Week 4, Session 2

#### Overview

The third pillar is abstraction: the disciplined practice of ignoring detail that is irrelevant to the current level of analysis. This lecture examines the hierarchy of abstractions in computing — from transistors through logic gates, machine code, programming languages, and architectural patterns — and develops criteria for evaluating whether an abstraction is "good" or "leaky."

#### Lecture Notes

Of the three pillars, abstraction is simultaneously the most powerful and the most dangerous. Powerful, because it enables us to build systems of staggering complexity — no human can hold an entire operating system in their head at the transistor level. Dangerous, because every abstraction *lies*: it hides details that, under certain circumstances, become critically relevant.

**The Abstraction Stack.** A modern computing system circa 2040 rests on a hierarchy of abstractions, each building on the one below:

1. **Physics → Transistors:** The quantum behavior of semiconductors is abstracted into a binary switch.
2. **Transistors → Logic Gates:** Switches are composed into AND, OR, NOT gates.
3. **Logic Gates → Machine Code:** Gates are arranged into an instruction set architecture (ISA) — the boundary between hardware and software.
4. **Machine Code → Programming Language:** ISAs are abstracted by compilers into high-level languages with variables, functions, types.
5. **Language → Framework/Library:** Common patterns are packaged into reusable components with APIs.
6. **Framework → Agent-Level Specification:** In 2040, the highest level of abstraction is often a natural language specification interpreted by an AI coding agent.

Each layer provides a **contract**: "if you use me correctly, I guarantee certain behavior, and you don't need to know how I work internally." The quality of an abstraction is measured by how well it keeps this contract.

**Good Abstractions.** A good abstraction:

- **Hides what it promises to hide.** The `sort()` function hides the sorting algorithm. As long as the result is correct and the performance is documented, you don't need to know whether it uses quicksort, mergesort, or timsort.
- **Exposes what matters.** The `sort()` function exposes parameters for the comparison function and, in some languages, the sorting strategy. It does not expose pivot selection or memory allocation details because those don't affect correctness.
- **Has a clear failure model.** If the abstraction can fail, it documents how and when. `malloc()` can return NULL; `sort()` can throw an exception on non-comparable elements.
- **Leaks predictably.** No abstraction is perfect. A good abstraction leaks in documented, manageable ways. The Java garbage collector abstracts memory management, but it "leaks" when it causes unpredictable pause times — and this leak is documented and measurable.

**The Leaky Abstraction Problem.** Joel Spolsky's Law of Leaky Abstractions (2002) states: "All non-trivial abstractions, to some degree, are leaky." The TCP protocol abstracts away packet loss — but when the network is congested, the abstraction leaks, and your "reliable" connection becomes slow or drops entirely. SQL abstracts away disk I/O — but when your query produces a full table scan, the abstraction leaks, and performance plummets.

The lesson is not to avoid abstraction — that way lies assembly language, and no one writes operating systems in assembly anymore. The lesson is to **know the abstraction's failure modes** and to be prepared to descend one level when necessary. The best developers in 2040 can operate comfortably at *any* level of the stack, choosing the right level for the problem at hand.

**Abstraction in the Age of AI Agents.** When you delegate coding to an AI agent, you are using the ultimate abstraction: "here is a specification; produce working code." This abstraction leaks in specific ways:
- The agent may misinterpret ambiguous specifications.
- The agent may produce code that works for common cases but fails on edge cases.
- The agent may use libraries or patterns that you don't understand, creating maintenance debt.
- The agent's output reflects the biases and limitations of its training data.

Knowing these failure modes is what distinguishes the effective AI-assisted developer from the helpless one. The abstraction of AI-assisted coding is powerful, but it is not magic — and treating it as magic is how you build systems that fail in production.

#### Required Reading

- Spolsky, J. (2002). "The Law of Leaky Abstractions." *Joel on Software*. [Short, essential blog post.]
- Dijkstra, E.W. (1972). "The Humble Programmer." *Communications of the ACM*, 15(10), 859-866. [Dijkstra's Turing Award lecture — a meditation on abstraction, humility, and intellectual manageability.]
- Lundström, E. (2040). "Abstraction as Forgetting: A Heathen Critique of the Stack." *Journal of Computational Philosophy*, 3(1), 45-67.

#### Discussion Questions

1. Is "AI agent that writes code" a good abstraction by the criteria above? Analyze its contract, its hiding/exposing choices, and its failure modes.
2. Spolsky wrote about leaky abstractions in 2002, when the dominant abstraction was the OS/hardware boundary. How has the landscape of leaky abstractions changed in 2040?
3. The "physical anchor pattern" (Lundström, 2040) suggests that some abstractions are *embodied* — they require a physical or digital instantiation to function. Is this a leak in the abstraction concept, or an extension of it?

---

### ᚺ Lecture 9: Induction and Recursion — The Mirror of Self-Reference

**Date:** Week 5, Session 1

#### Overview

Mathematical induction and computational recursion are two sides of the same coin — the former proves properties about the latter. This lecture deepens the treatment of recursion from Lectures 6 and 8 by examining structural induction, well-founded recursion, and the relationship between recursive data structures and recursive algorithms.

#### Lecture Notes

The word "recursion" appears in the dictionary as: "see recursion." The joke is old, but the insight is profound: recursion is the computational manifestation of self-reference, and self-reference is one of the most powerful — and dangerous — concepts in all of thought.

**Mathematical Induction: Proving Recursive Claims.** To prove that a property P(n) holds for all natural numbers n:

1. **Base case:** Prove P(0).
2. **Inductive step:** Assume P(k) — the *induction hypothesis* — and prove P(k+1).

If both hold, then P(n) holds for all n. The reasoning: P(0) is true (base); if P(0) then P(1) (inductive step with k=0); if P(1) then P(2); and so on, domino-fashion, to infinity.

Induction is the proof technique for recursion because a recursive function typically:
- Handles a base case directly (corresponding to the proof's base case)
- Makes recursive calls only on "smaller" instances (corresponding to the proof's inductive step, where the induction hypothesis covers those smaller instances)

**Example.** Prove that Merge Sort correctly sorts any list.

- **Base case:** A list of 0 or 1 elements is trivially sorted. Merge Sort returns it unchanged. ✓
- **Inductive step:** Assume Merge Sort correctly sorts any list of length < n (induction hypothesis). For a list of length n, Merge Sort splits it into two lists each of length < n, recursively sorts them (correctly, by the induction hypothesis), and merges them. The merge step is correct because it always selects the smaller of the two front elements, preserving sortedness. Therefore Merge Sort correctly sorts lists of length n.

The proof mirrors the code exactly. This is not coincidence — it is the Curry-Howard correspondence in action: the proof *is* the program, analyzed at the type level.

**Structural Induction.** Natural number induction (base case 0, step from k to k+1) is a special case. The general principle, **structural induction**, proves properties of recursively defined structures (trees, lists, expressions) by:

1. Proving the property for all "atomic" (non-recursive) cases.
2. For each recursive constructor, assuming the property holds for the substructures and proving it holds for the constructed structure.

This is how we prove type safety for programming languages, correctness for compilers, and invariants for distributed systems.

**Dangers of Recursion.** Recursion without a well-founded measure leads to infinite descent — and in practice, to stack overflow. Every recursive call must make progress toward a base case, and this progress must be demonstrable. In functional languages like Haskell (and in 2040's increasingly popular verified-functional paradigm), the compiler can often prove termination automatically — but the programmer must still *design* for termination.

The deeper danger is conceptual: self-reference can produce paradox. "This statement is false." Russell's paradox. The halting problem. These are not flaws in logic — they are boundary markers. They tell us that some forms of self-reference are fundamentally ill-posed, and learning to recognize them is part of computational maturity.

#### Required Reading

- Huth & Ryan, Chapter 1, §1.6 (Mathematical Induction).
- Peirce, B.C. (2042). *Software Foundations, Vol. 1: Logical Foundations* (4th ed.). Electronic textbook. Chapters on Induction. [This is the standard 2040s introduction to verified programming in Yggdrasil-Verify.]

#### Discussion Questions

1. In 2040, many recursion-heavy algorithms (tree traversal, graph search) are handled by libraries or AI-generated code. Does the practicing developer still need to understand induction? Why?
2. The halting problem proves that no algorithm can determine whether an arbitrary program terminates. Yet in practice, we can prove termination for most programs we write. What is the gap between theory and practice here?
3. Self-reference appears in language ("this sentence"), in mathematics (Gödel), and in computation (recursion, quines). Is self-reference a bug or a feature of formal systems?

---

### ᚾ Lecture 10: Concurrency and Distribution — Thinking in Parallel

**Date:** Week 5, Session 2

#### Overview

For most of computing history, programs were written for a single sequential processor. By 2040, parallelism is the default — multi-core CPUs, distributed cloud services, and AI agent swarms all require thinking about computation that happens *simultaneously*. This lecture introduces the fundamental challenges of concurrency: race conditions, deadlocks, consistency models, and the emerging agent-oriented concurrency paradigm.

#### Lecture Notes

Sequential computation is like a single thread of yarn — one stitch follows another, and you can always see where you are. Concurrent computation is like a loom with multiple shuttles — threads cross, intertwine, and must be coordinated to prevent tangling. The loom metaphor is apt: weaving is inherently parallel, and the warp-weighted loom (used by Norse women for millennia) represents an early triumph of concurrent engineering.

**The Problem of Shared Mutable State.** When two threads access the same memory location, and at least one writes to it, the result depends on timing — and timing is unpredictable. Consider:

```
Thread A: x = x + 1
Thread B: x = x + 1
```

If both threads read `x` before either writes, they both see the same value, both increment it, and the result is `x+1` instead of `x+2`. One increment is lost. This is a **race condition**.

The traditional solution is **mutual exclusion** — locks, semaphores, monitors — which serializes access to shared state. But locks introduce their own problems:
- **Deadlock:** Thread A holds lock 1 and waits for lock 2; Thread B holds lock 2 and waits for lock 1. Neither can proceed.
- **Priority inversion:** A low-priority thread holds a lock needed by a high-priority thread.
- **Lock contention:** Too many threads competing for the same lock reduces parallelism to serial.

**The Functional Alternative.** Functional programming avoids the problem entirely by eliminating shared mutable state. In a pure functional language, data is immutable — you don't modify values, you produce new values. There is no "x = x + 1" because `x` cannot change. Instead, you compute `let y = x + 1` and use `y` going forward.

In 2040, the dominant programming paradigm for concurrent systems is **functional core, imperative shell** — the business logic is pure and functional (easily parallelized, easily tested), while the outer layer that interacts with the world (databases, network, UI) uses careful, localized imperative code with explicit concurrency control. This is the architecture behind most agentic AI systems, including the Hermes home assistant framework.

**Agent-Oriented Concurrency.** The 2040 innovation is treating concurrent components as *agents* — independent entities with their own internal state, communicating through message passing rather than shared memory. This is the Actor Model (Hewitt, 1973; popularized by Erlang) taken to its logical conclusion: each agent has a mailbox, processes messages sequentially, and can create new agents. Since agents don't share state, race conditions are impossible. Since messages are asynchronous, deadlocks are rare (though livelocks — agents waiting for messages that never arrive — remain a concern).

This model maps naturally to distributed systems: agents can run on different machines, communicating over the network. In 2040, with the maturation of the decentralized web (Web4), agent-oriented concurrency is the standard pattern for building scalable, resilient systems.

**Consistency Models.** In distributed systems, the CAP theorem (Brewer, 2000; proved by Gilbert and Lynch, 2002) tells us that a distributed data store can provide at most two of: Consistency (all nodes see the same data at the same time), Availability (every request receives a response), and Partition tolerance (the system continues to function despite network partitions). Since partitions are inevitable in real networks, the choice is between CP (consistent but may be unavailable during partitions) and AP (available but may return inconsistent data).

Understanding this tradeoff is essential for system design. A banking system must be CP — you cannot allow two branches to withdraw the same money. A social media feed can be AP — seeing a slightly stale version of a friend's post is acceptable. Knowing which to choose is a design decision, not a technical one.

#### Required Reading

- Herlihy, M. & Shavit, N. (2041). *The Art of Multiprocessor Programming* (3rd ed.). Morgan Kaufmann. Chapters 1-3.
- Hewitt, C. (1973). "A Universal Modular ACTOR Formalism for Artificial Intelligence." *IJCAI*. [The original actor model paper — short and visionary.]
- Brewer, E. (2022). "CAP Twelve Years Later: How the 'Rules' Have Changed." *IEEE Computer*, 45(2), 23-29. [A retrospective by the theorem's originator.]

#### Discussion Questions

1. Agent-oriented concurrency avoids shared-state problems but introduces *coordination* overhead — agents must agree on protocols for message formats, error handling, and timeouts. Is this a genuine improvement over shared-state concurrency, or just moving the complexity to a different layer?
2. The CAP theorem is often cited as a fundamental limit. Are there practical workarounds — systems that achieve "essentially" all three properties by relaxing the definitions? Discuss CRDTs (Conflict-free Replicated Data Types) as one approach.
3. In 2040, we routinely run swarms of AI agents that coordinate autonomously. What new concurrency challenges does this introduce beyond traditional distributed systems?

---

### ᛁ Lecture 11: Verification and Testing — Trust, but Verify

**Date:** Week 6, Session 1

#### Overview

How do we know a program is correct? This lecture surveys the landscape of software assurance, from unit testing through property-based testing, model checking, and formal verification. We examine the cost-benefit tradeoffs of each approach and the 2040 paradigm shift toward AI-augmented verification.

#### Lecture Notes

"Testing shows the presence, not the absence, of bugs." Dijkstra's aphorism is as true in 2040 as it was in 1970. But the *meaning* of testing has changed dramatically. In 2040, we live in a world where:
- AI agents generate most code, making traditional unit testing insufficient (the human didn't write the code, so they don't know what edge cases the AI might have missed).
- Formal verification tools have become practical for production systems (Yggdrasil-Verify, Coq 10.0, Lean 6).
- Property-based testing (QuickCheck and its descendants) can automatically generate thousands of test cases from specifications.

**The Testing Pyramid.** The classic testing pyramid (unit → integration → end-to-end) has been augmented in 2040:

- **Unit tests:** Still essential, mostly AI-generated from code analysis. The human's role is to review the test cases for *coverage gaps* — what is NOT being tested.
- **Property-based tests:** The human specifies invariant properties ("sorting a list should produce a list with the same elements in non-decreasing order") and the testing framework generates random inputs, searching for counterexamples. This catches edge cases that human-written unit tests miss.
- **Integration tests:** Increasingly handled by AI agents that simulate user behavior at the API level.
- **Formal verification:** For critical components (cryptographic protocols, financial transactions, medical device software), the specification is written in a formal logic, and a proof assistant verifies that the implementation satisfies the specification. In 2040, this is no longer exotic — it is routine for safety-critical systems.

**Model Checking.** An intermediate approach between testing and full verification: the system is modeled as a finite state machine, and a model checker exhaustively explores all reachable states, checking that specified properties hold. Model checking works for finite-state systems (or systems that can be abstracted to finite state) and is particularly valuable for concurrent systems, where race conditions are hard to reproduce through testing. In 2040, model checking is a standard part of the CI/CD pipeline for distributed systems.

**The Economics of Correctness.** Verification is not free. A 2044 study by the Software Assurance Institute found that formal verification adds approximately 40% to development time but reduces post-deployment defects by 98% for the verified components. The economic calculation depends on the cost of failure:
- A bug in a social media app causes mild inconvenience → unit testing suffices.
- A bug in a payment system costs money → property-based testing + integration testing.
- A bug in an autonomous vehicle's collision avoidance code kills people → formal verification is mandatory.

Part of computational maturity is making this judgment correctly — knowing what level of assurance is appropriate for a given system, and not letting either perfectionism or laziness drive the decision.

**Trusting AI-Generated Code.** In 2040, the question "should I trust this code?" most often refers to code generated by an AI agent. The answer depends on the verification regime:
- If the AI also generated the tests, and the tests pass, you have *some* confidence — but the AI may have made correlated errors in both code and tests.
- If a *different* AI agent (or a human) wrote the tests, confidence is higher.
- If the code is formally verified against a specification written by a human, you can trust it to the extent you trust the specification.
- Ultimately, **accountability rests with the human who approved the code for deployment**, not with the AI that generated it.

#### Required Reading

- O'Hearn, P.W. (2023). "Incorrectness Logic." *Communications of the ACM*, 66(1), 86-95. [A revolutionary paper: instead of proving what programs *do*, prove what they *don't* do.]
- Hughes, J. (2022). "Why Functional Programming Matters, Revisited." *Journal of Functional Programming*, 32, e1. [Hughes revisits his 1984 classic, updated for the verification era.]
- University of Yggdrasil Software Assurance Group. (2043). *Yggdrasil-Verify User Manual*. Chapters 1-3.

#### Discussion Questions

1. If AI agents can generate both code and tests, what role remains for the human in quality assurance? Is there a point where the human becomes the weakest link in the verification chain?
2. Formal verification proves that code matches specification — but the specification itself may be wrong. How do we verify specifications? Is there an infinite regress here?
3. Dijkstra said testing shows the presence, not the absence, of bugs. Does AI-generated testing change this calculus, or merely accelerate the same process?

---

### ᛃ Lecture 12: Synthesis — The Thinking Developer in 2040

**Date:** Week 6, Session 2

#### Overview

The final lecture synthesizes the three pillars — decomposition, pattern recognition, abstraction — into a unified portrait of the computational thinker. We reflect on what has changed since Wing's 2006 call for universal computational literacy and what has remained constant. The lecture concludes with a vision of the software developer in 2040: not a coder, but a *designer of computational thought*.

#### Lecture Notes

We began this course with a question: What distinguishes computational thinking from other modes of reasoning? After twelve weeks, the answer has deepened. Computational thinking is not merely "thinking like a computer" — it is thinking with *precision about process*, with *awareness of limits*, and with *commitment to verifiability*.

**What Has Changed Since 2006.** When Jeannette Wing published her manifesto, the world was different. The iPhone did not exist. Deep learning was a niche research area. The phrase "AI agent" would have meant nothing to most software developers. Wing argued that computational thinking should be a universal skill, like reading and writing.

In 2040, Wing's vision has been realized, but not as she imagined. Computational thinking IS universal — but it has been absorbed into tools. A child who asks a household AI to plan the week's meals is engaging in computational thinking without knowing it: decomposition (meals by day), pattern recognition (dietary preferences), abstraction (ignoring irrelevant details like brand names). The question is no longer whether people *use* computational thinking, but whether they understand it well enough to *direct* it.

**What Has Not Changed.** The fundamentals are immutable. Logic is logic, whether you reason in 400 BCE Athens or 2040 CE Yggdrasil. An undecidable problem cannot be solved, no matter how many GPU clusters you throw at it. An NP-hard problem remains exponential unless P=NP — and in 2040, we still don't know. The halting problem still applies: no system can reliably predict the behavior of all possible programs, including its own.

These limits are not obstacles to be overcome. They are *features* of the computational universe — constraints that make the craft of software development meaningful. If every problem were efficiently solvable, there would be no need for judgment, creativity, or wisdom. The developer would be a mere transcriber of requirements. The limits are what make the work human.

**The Developer of 2040.** The software developer in 2040 is not primarily a writer of code. AI agents handle most coding tasks — not perfectly, but well enough that the bottleneck is no longer implementation speed. The developer's role is:

1. **Specification:** Defining what should be built, with enough precision that an AI agent can implement it and enough wisdom to know when the specification itself is wrong.
2. **Architecture:** Making the high-level design decisions that determine system qualities — security, scalability, maintainability, evolvability. These decisions cannot be delegated because they require value judgments.
3. **Verification:** Designing the assurance strategy — what level of testing, what formal properties to prove, what monitoring to deploy. The developer is the guarantor of correctness, not the AI.
4. **Ethics:** Recognizing when a system, even if technically correct, will cause harm — through bias, through surveillance, through environmental cost. Computational thinking includes thinking about the *consequences* of computation.
5. **Teaching:** As AI agents become more capable, the developer's role increasingly resembles that of a mentor or editor — guiding the AI, catching its mistakes, and ensuring the output reflects genuine understanding rather than statistical pattern-matching.

This is a more demanding role than "coder," but also a more rewarding one. It requires the skills this course has developed: logical precision, algorithmic intuition, pattern literacy, and abstract reasoning. It requires, above all, the habit of thinking clearly about problems that have no obvious answer — because those are the only problems worth solving.

**Final Reflection.** The Norse metaphor of the Norns — the three fate-weavers at the roots of Yggdrasil — offers a closing image. Urðr (that which has become) is the code that has been written. Verðandi (that which is becoming) is the code being written now. Skuld (that which shall become) is the code yet to be written — the debt, the obligation, the future. Computational thinking is the skill of the Norns: the ability to hold past, present, and future in relation, to weave the threads without tangling them, to see the pattern while working on a single stitch.

You are not here to learn a framework that will be obsolete in five years. You are here to learn to think — and thinking, unlike frameworks, does not deprecate.

#### Required Reading

- Wing, J.M. (2022). "Computational Thinking, Revisited." *Communications of the ACM*, 65(3), 24-26. [Wing reflects on 16 years of impact.]
- Lundström, E. (2038). *Weaving Thought*. Chapter 12: "The Norns as System Architects."
- Your own course notes. Re-read them. What has changed in your thinking since Lecture 1?

#### Discussion Questions

1. In 2040, what does *not* count as computational thinking? What modes of reasoning lie outside its scope, and should we value them equally?
2. If AI agents can design architectures, write specifications, and verify correctness — all the roles listed above — what uniquely human contribution remains? Is there one?
3. The Norn metaphor frames computational thinking as *weaving*. Is this a productive metaphor, or does it romanticize what should be understood as an engineering discipline? What does the choice of metaphor reveal about the values of the person who chooses it?

---

## Final Examination Preparation

The final examination for SD101 consists of two components:

### Part I: Written Examination (60%)

Choose **four** of the following **eight** essay questions. Each essay should be approximately 800-1200 words and should demonstrate both mastery of the technical material and the ability to synthesize concepts across lectures.

1. **Formal Logic in Specification.** A client asks you to build a system that "never loses data and is always fast." Using propositional and predicate logic, formalize what this requirement might mean. Identify ambiguities in the natural language requirement and show how formalization exposes them. What would it mean for these requirements to be contradictory, and how would you prove that contradiction?

2. **Decomposition in Practice.** Choose a complex software system (real or hypothetical). Analyze how it decomposes into components. Is the decomposition "good" by the criteria of Lecture 6 — are the subproblems genuinely independent? Identify at least one place where the decomposition fails and discuss the consequences.

3. **Recursion and Induction.** Explain the relationship between recursive algorithms and inductive proofs. Provide an example of a recursive function, state a correctness property, and prove it by induction. Then provide an example where the naive recursive solution is exponentially inefficient, explain why, and show how dynamic programming resolves the issue.

4. **Pattern Recognition and Isomorphism.** Identify a problem from a non-computing domain that is structurally isomorphic to a known computational problem. Describe the isomorphism in detail, including the mapping between domain concepts and formal structures. Discuss whether the isomorphism is useful — does the computational solution actually help with the original problem?

5. **The Leaky Abstraction.** Select a well-known abstraction in computing (e.g., TCP, SQL, virtual memory, garbage collection, or the 2040-era AI coding agent). Describe the abstraction's contract, identify at least two ways it leaks, and discuss whether these leaks are acceptable given the abstraction's benefits. Propose a design change that would reduce one leak and analyze its costs.

6. **Concurrency Models.** Compare and contrast two concurrency models: shared-memory with locks and message-passing with actors. For each model, describe a scenario where it is clearly superior and a scenario where it is clearly inferior. Which model do you believe will dominate by 2050, and why?

7. **Verification Economics.** A startup is building a healthcare scheduling system. The CEO wants to move fast and skip formal verification. As the technical lead, make the case for a specific verification strategy, referencing the cost-benefit analysis from Lecture 11. What would you verify formally, what would you test with properties, and what would you leave to unit tests?

8. **The Future of the Developer.** Reflect on the portrait of the 2040 developer presented in Lecture 12. Do you agree that coding skill is becoming secondary to specification, architecture, and ethics? Or is this vision elitist — does it assume a level of abstraction that most working developers cannot afford? Ground your argument in specific trends you observe in the industry.

### Part II: Design Project (40%)

Design a computational solution for a problem of your choice. The problem may be drawn from any domain — personal, professional, academic, or civic. Your submission must include:

1. **Problem Statement** (500 words): What problem are you solving, and for whom? Why is it computationally interesting?
2. **Logical Formalization** (500 words): Express the core requirements in propositional or predicate logic. Identify any ambiguities and how you resolved them.
3. **Decomposition Strategy** (500 words): How have you decomposed the problem into subproblems? Justify your decomposition against the criteria of Lecture 6.
4. **Algorithmic Sketch** (500 words): Describe the key algorithm(s) in prose and pseudocode. Analyze time and space complexity.
5. **Abstraction Analysis** (500 words): What abstractions have you introduced? Are they good abstractions by the criteria of Lecture 8? Where do they leak?
6. **Verification Plan** (500 words): How would you verify that your solution is correct? Specify at least three properties you would verify and the method (testing, property-based, model checking, formal) you would use for each.

---

**ᛗ í ᛗ í ᚱ — From the Well, all wisdom flows.**

*SD101: Computational Thinking & Logic — University of Yggdrasil, 2040*
*Instructor: Dr. Eira Lundström*
*Course version: 1.0 — 2040 Academic Year*