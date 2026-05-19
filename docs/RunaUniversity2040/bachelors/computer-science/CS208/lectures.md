# CS208: Formal Methods & Verification
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS101 — Computational Thinking & Problem Solving; CS102 — Discrete Mathematics for CS; CS105 — Programming Languages & Paradigms
**Description:** This course is a descent into the underworld of computation — the place where programs are not merely executed but *proved*. Formal methods seek to displace testing with mathematics, to replace "it seems to work" with "it cannot fail." Students learn to specify software and hardware in precise logical languages, to verify that implementations satisfy their specifications using model checking, deductive proof, and abstract interpretation, and to wield the proof assistants — Coq, Lean, Isabelle — that have transformed formal verification from heroic feat to reproducible engineering. The course weaves together temporal logic (the language of reactive systems), Hoare logic (the calculus of imperative correctness), SAT/SMT solving (the algorithmic engine of modern verification), type theory (the constructive foundation), and the industrial tools — TLA+, CBMC, Frama-C, Z3, Alloy — that bring formal methods into real-world practice. Each lecture is grounded in a concrete verification challenge: Is this concurrent protocol deadlock-free? Does this cryptographic implementation respect constant-time execution? Can this compiler optimisation be proved semantics-preserving? By course's end, students can read a formal specification, construct a machine-checkable proof, and judge when formal methods are worth their cost — and when they are not. The course is taught in the spirit of Mímisbrunnr — Mímir's Well — where Odin sacrificed an eye for wisdom. Formal verification is a sacrifice of time and effort for the certainty that the code is correct. The question is: when is the sacrifice worth making?

---

## Lecture 1: Why Prove When You Can Test? — The Case for Formal Methods

The software industry has built empires on testing. Unit tests, integration tests, fuzz tests, regression tests, chaos engineering — the modern developer's confidence in their code rests on a mountain of test cases, each one a witness that the program behaves as expected on a particular input. And yet, testing has a fundamental limitation, captured with brutal precision by Edsger Dijkstra in 1970: "Program testing can be used to show the presence of bugs, but never to show their absence." A test suite that passes today says nothing about the input your user will provide tomorrow. A million test cases cover a vanishingly small fraction of a program's input space. For a function that takes two 64-bit integers, exhaustive testing would require 2¹²⁸ executions — more than the number of atoms in the observable universe.

Formal methods are the attempt to escape this limitation. Rather than sampling behaviour, formal verification *proves* that a program satisfies its specification for *all possible inputs*. The specification is expressed in a precise logical language — a contract that the program must honour — and the verification is a mathematical argument, checked by machine, that no execution can violate the contract. The distinction between testing and verification is the difference between checking that a bridge holds under a few test loads and proving, from the laws of mechanics and the properties of steel, that it cannot collapse under any load within its design envelope.

The modern landscape of formal methods is diverse, spanning a spectrum from lightweight to heavyweight, from automatic to interactive, from after-the-fact to correct-by-construction:

- **Model checking** (Edmund Clarke, Allen Emerson, Joseph Sifakis — Turing Award 2007) exhaustively explores the state space of a finite-state model, checking whether every possible execution satisfies a temporal-logic specification. Model checking is automatic — push a button and wait — but it suffers from the **state explosion problem**: the number of states grows exponentially with the number of components. The art of model checking lies in combating this explosion through symbolic representations (BDDs), partial-order reduction, abstraction, and compositional reasoning.

- **Deductive verification** (Floyd-Hoare logic, 1967–1969) annotates a program with logical assertions — preconditions, postconditions, loop invariants — and generates **verification conditions**: logical formulas whose validity implies the program's correctness. The verification conditions are discharged by automatic theorem provers (SMT solvers like Z3, CVC5) or interactive proof assistants. Deductive verification can handle infinite-state programs — the loop invariant is an inductive hypothesis that covers all iterations — but it requires human insight to craft the invariants.

- **Abstract interpretation** (Patrick and Radhia Cousot, 1977) approximates the behaviour of a program by executing it over an *abstract domain* — intervals instead of concrete integers, signs instead of concrete values — tracking what *might* happen rather than what *does* happen. Abstract interpretation is the foundation of static analysis tools (Astrée, Polyspace, Infer) that run automatically and scale to millions of lines of code, at the cost of false alarms: the analysis may report a potential error that cannot actually occur.

- **Type systems** (from Church's simply typed λ-calculus, 1940, to Rust's ownership types, 2015) are the most successful formal method in practice: every statically typed program carries a machine-checkable proof of a safety property (no "method not found" errors, no null-pointer dereferences in safe Rust). Dependent types (Martin-Löf type theory, Coq, Lean, Idris) blur the line between types and specifications, allowing the type system to express arbitrary correctness properties.

- **Proof assistants** (Automath, 1967; Coq, 1989; Isabelle, 1986; Lean, 2015) are interactive environments where the human guides the machine through a proof, and the machine checks every step. Proof assistants have been used to verify an operating-system microkernel (seL4, 2009), a C compiler (CompCert, 2008), and the Four-Colour Theorem (Gonthier, 2005). They are the heavy artillery of formal methods — capable of verifying anything, but demanding years of effort for large systems.

The question that haunts formal methods is the **cost-benefit calculus**. Formal verification is expensive — writing specifications, crafting invariants, and guiding proofs requires expertise and time. For a social-media app that can tolerate occasional bugs, the cost is prohibitive. For the control software of an Airbus A380, the flight-guidance system of a SpaceX Dragon, or the microkernel of a secure operating system, the cost of *not* verifying may be measured in lives. The art of the formal-methods engineer is knowing when to reach for a proof — and when a test will do.

**Required Reading:**
- Edmund M. Clarke, Orna Grumberg & Doron A. Peled, *Model Checking* (MIT Press, 1999/2041), ch. 1 — "The Need for Formal Methods"
- Edsger W. Dijkstra, "The Humble Programmer" (Turing Award Lecture, *Communications of the ACM* 15:10, 1972): 859–866
- Jean-Raymond Abrial, *Modeling in Event-B: System and Software Engineering* (Cambridge, 2010/2040), ch. 1
- Xavier Leroy, "Formal Verification of a Realistic Compiler" (*Communications of the ACM* 52:7, 2009): 107–115 — the CompCert story
- University of Yggdrasil Formal Methods Reading Room: "The Verification Spectrum" (interactive visualisation, 2040)

**Discussion Questions:**
1. Dijkstra wrote in 1970 that testing cannot show the absence of bugs. Yet the software industry remains overwhelmingly test-driven. What, specifically, has changed — and what has not — since Dijkstra's pronouncement?
2. Model checking, deductive verification, and abstract interpretation each occupy a different point on the automation-versus-expressiveness spectrum. For what kinds of systems and properties would you choose each?
3. The seL4 verification cost roughly 20 person-years for 10,000 lines of C. How do we decide whether such an investment is justified — and what would it take to reduce the cost by an order of magnitude?

---

## Lecture 2: Propositional Logic and SAT Solving — The Engine Room of Verification

At the heart of almost every modern verification tool lies a SAT solver — a program that determines whether a given propositional formula has a satisfying assignment. The propositional satisfiability problem (SAT) was the first problem proved NP-complete (Cook, 1971; Levin, 1973). For decades it was considered a theoretical curiosity — a hard problem with no practical algorithm. That changed in the late 1990s and early 2000s, when a series of algorithmic breakthroughs transformed SAT solving from a textbook impossibility into an industrial workhorse capable of handling formulas with millions of variables.

A propositional formula is built from Boolean variables (x₁, x₂, …, xₙ) using the connectives ¬ (not), ∧ (and), ∨ (or), → (implies), and ↔ (iff). Any formula can be converted to **Conjunctive Normal Form (CNF)** — a conjunction of clauses, each clause a disjunction of literals — in linear time (via the Tseitin transformation, which introduces auxiliary variables to avoid exponential blowup). CNF is the native format of SAT solvers, and the transformation from "real problem" to CNF is the first step in almost every verification workflow.

The modern SAT solver is built on the **Conflict-Driven Clause Learning (CDCL)** architecture, which synthesises two earlier paradigms: the **DPLL algorithm** (Davis–Putnam–Logemann–Loveland, 1962), a backtracking search that assigns variables and propagates their consequences, and **resolution** (Robinson, 1965), an inference rule that derives new clauses from existing ones. CDCL proceeds as follows:

1. **Decide:** Pick an unassigned variable and assign it a truth value (heuristic: VSIDS — Variable State Independent Decaying Sum — tracks which variables appear most often in recent conflicts).
2. **Propagate:** Apply **unit propagation** (also called Boolean Constraint Propagation, BCP): if all but one literal in a clause are false, the remaining literal must be true. Repeat until no further unit clauses exist or a conflict is found.
3. **Conflict Analysis:** When a clause becomes false (all literals are false), analyse the **implication graph** — the directed graph of assignments and their reasons — to find the **First Unique Implication Point (1UIP)**, the decision that is, in a precise sense, responsible for the conflict. Derive a **learned clause** — a new clause that is implied by the formula and that prevents the solver from repeating the same conflict. **Backjump** to the level where the learned clause becomes unit, undoing all assignments after that level.
4. **Restart:** Periodically abandon the current search tree and start fresh, keeping the learned clauses. Restarts prevent the solver from getting stuck in an unproductive region of the search space.

The learned clauses are the key to CDCL's power. Each learned clause is a lemma — a fact about the formula that the solver has discovered and that can be reused. Over time, the clause database grows; the solver "learns" the structure of the problem. This turns SAT solving from blind search into a form of directed reasoning, and it is why CDCL solvers can handle industrial formulas with millions of variables — the learned clauses prune vast regions of the search space.

SAT solvers are the computational engine for **bounded model checking (BMC)**, where a system is unrolled for k steps and the resulting formula is checked for satisfiability; for **planning** (STRIPS to SAT reductions); for **cryptographic analysis** (encoding differential trails as SAT); for **software verification** (CBMC unwinds loops and encodes the program as a SAT instance); and for **hardware verification** (equivalence checking of circuit designs). The annual SAT Competition drives a virtuous cycle of innovation: the best solvers — CaDiCaL, Kissat, Glucose, MapleSAT — improve by a factor of 2–10 each generation, and problems that were unsolvable in 2010 are trivial in 2040.

**SMT (Satisfiability Modulo Theories)** extends SAT with decision procedures for first-order theories — linear arithmetic, bit-vectors, arrays, uninterpreted functions. An SMT solver (Z3, CVC5, Yices, MathSAT) combines a SAT solver with theory solvers: the SAT solver handles the Boolean structure, the theory solvers check the consistency of conjunctions of theory literals, and the two communicate through the **Nelson-Oppen framework** (for disjoint theories) or **model-based theory combination**. SMT solvers are the workhorses of deductive verification: they discharge the verification conditions generated by Hoare logic, and they are the query engines behind program analysis tools that ask "is there an execution that reaches this error state?"

**Required Reading:**
- Armin Biere, Marijn Heule, Hans van Maaren & Toby Walsh (eds.), *Handbook of Satisfiability* (2nd ed., IOS Press, 2021/2039), chs. 1–6
- Niklas Eén & Niklas Sörensson, "An Extensible SAT-solver" (MiniSat, *SAT Competition*, 2004)
- João Marques-Silva & Karem Sakallah, "GRASP: A Search Algorithm for Propositional Satisfiability" (*IEEE Transactions on Computers* 48:5, 1999): 506–521 — the CDCL origin paper
- Leonardo de Moura & Nikolaj Bjørner, "Z3: An Efficient SMT Solver" (*TACAS*, 2008)
- Daniel Kroening & Ofer Strichman, *Decision Procedures: An Algorithmic Point of View* (2nd ed., Springer, 2016/2042), chs. 1–5
- UoY SAT Visualiser: Explore the implication graph of a CDCL run in real time (2040)

**Discussion Questions:**
1. CDCL learns clauses from conflicts. What, precisely, makes a learned clause useful — and when does learning too many clauses become counterproductive (the "clause database management problem")?
2. SMT solvers combine SAT solvers with theory solvers. Why is the combination non-trivial — and what goes wrong if two theories share a non-convex sort (e.g., integer + real arithmetic)?
3. Bounded model checking unwinds a system for k steps. What guarantees does this provide — and what are the limits of "bounded" correctness?

---

## Lecture 3: Temporal Logic — Specifying Behaviour Over Time

Programs do not merely transform inputs into outputs; they *interact*. A web server handles a stream of requests; a pacemaker monitors a heart and delivers pulses; a flight-control system reads sensors and commands actuators in a continuous feedback loop. The correctness of such **reactive systems** cannot be captured by preconditions and postconditions alone — we need a language for describing *sequences of events over time*. Temporal logic, invented by Arthur Prior in the 1950s for philosophical reasoning about time and adapted to computer science by Amir Pnueli (Turing Award 1996), is that language.

**Linear Temporal Logic (LTL)** describes the behaviour of a single execution path. Its temporal operators are:

- **X φ** (next): φ holds in the next state
- **F φ** (future/eventually): φ holds at some future state
- **G φ** (globally/always): φ holds in all future states (including the present)
- **φ U ψ** (until): φ holds continuously until ψ holds; ψ must eventually hold
- **φ R ψ** (release): ψ holds until and including the moment φ becomes true; φ need not ever hold, in which case ψ holds forever

With these operators, we can express properties such as:
- **G (request → F grant)** — "every request is eventually granted" (liveness, in Pnueli's terminology)
- **G (¬(crit₁ ∧ crit₂))** — "processes 1 and 2 are never simultaneously in their critical sections" (mutual exclusion, a safety property)
- **G F φ** — "infinitely often φ" (e.g., a fair scheduler grants each process infinitely often)
- **F G φ** — "eventually always φ" (e.g., the system eventually stabilises)

The distinction between **safety** and **liveness** — due to Leslie Lamport — is fundamental: a safety property asserts that "nothing bad ever happens" (it can be violated by a finite prefix of an execution), while a liveness property asserts that "something good eventually happens" (it can only be violated by an infinite execution). Every linear-time property is the conjunction of a safety property and a liveness property (the Alpern-Schneider decomposition theorem, 1985).

**Computation Tree Logic (CTL)** takes a different perspective: rather than describing individual paths, CTL describes the *tree* of all possible futures from a given state. Every temporal operator is prefixed by a **path quantifier**: **A** (for all paths) or **E** (there exists a path). Thus:
- **AG φ** — "φ holds in every reachable state" (φ is an invariant)
- **EF φ** — "there is some reachable state where φ holds" (φ is reachable)
- **AF φ** — "on every path, φ eventually holds" (unconditional liveness)
- **EG φ** — "there is a path where φ holds forever"
- **AU (φ, ψ)** — "on every path, φ holds until ψ"
- **EU (φ, ψ)** — "there exists a path where φ holds until ψ"

LTL and CTL are incomparable in expressiveness. LTL can express "G F φ" (infinitely often), which has no CTL equivalent. CTL can express "AG EF φ" (from every reachable state, it is possible to reach a state where φ holds — a "reset property"), which has no LTL equivalent. **CTL\*** (Emerson & Halpern, 1986) unifies LTL and CTL by allowing path formulas (LTL over state formulas) and state formulas (quantification over path formulas) to be combined arbitrarily. CTL\* is the most expressive branching-time logic in common use, and it is the specification language of many symbolic model checkers.

**Property Specification Language (PSL)** — standardised as IEEE 1850 — extends LTL with regular expressions for describing finite sequences, making it more convenient for hardware specification. PSL is the specification language used by industrial model-checking tools for hardware (Cadence JasperGold, Synopsys VC Formal). Its design reflects a hard-won lesson: for temporal logic to be adopted by engineers, it must be readable by engineers — not just by logicians.

**Required Reading:**
- Amir Pnueli, "The Temporal Logic of Programs" (*FOCS*, 1977): 46–57 — the paper that brought temporal logic to computer science
- Zohar Manna & Amir Pnueli, *The Temporal Logic of Reactive and Concurrent Systems: Specification* (Springer, 1992)
- Edmund M. Clarke, Orna Grumberg & Doron A. Peled, *Model Checking* (MIT Press, 1999/2041), chs. 2–3
- Leslie Lamport, "Proving the Correctness of Multiprocess Programs" (*IEEE Transactions on Software Engineering* SE-3:2, 1977): 125–143 — the safety/liveness distinction
- Cindy Eisner & Dana Fisman, *A Practical Introduction to PSL* (Springer, 2006/2040)
- UoY Temporal Logic Simulator: interactively explore LTL and CTL formulas (2040)

**Discussion Questions:**
1. "G F φ" (infinitely often φ) cannot be expressed in CTL. Why — and what does this tell us about the fundamental difference between linear-time and branching-time perspectives?
2. The Alpern-Schneider theorem says every property decomposes into safety + liveness. Is this decomposition useful in practice, or is it merely a theoretical curiosity?
3. Why would a hardware verification engineer prefer PSL over raw LTL? What does this tell us about the relationship between formal elegance and practical adoption?

---

## Lecture 4: Model Checking — Exhaustive Exploration of Finite-State Systems

Model checking is the brute-force approach to verification: build a finite-state model of the system, specify the desired property in temporal logic, and exhaustively check whether the model satisfies the specification. The algorithm explores every reachable state, every possible execution. There is no approximation, no approximation — the verdict is either "property holds" (with a proof) or "property fails" (with a counterexample — a concrete execution trace that violates the property). It is this counterexample generation that makes model checking uniquely valuable in practice: when a property fails, the tool produces a concrete scenario that the engineer can step through, debug, and fix.

The core algorithm of **explicit-state model checking** is the **nested depth-first search (NDFS)** for LTL properties. An LTL formula φ can be translated, via the **tableau construction**, into a Büchi automaton A¬φ — a finite automaton over infinite words that accepts exactly the executions that *violate* φ. The system model M is also represented as a Büchi automaton. The model-checking problem M ⊨ φ reduces to checking whether the product automaton M × A¬φ has an accepting run — a reachable cycle that visits an accepting state infinitely often. NDFS finds such cycles by performing a primary DFS to explore reachable states, and a secondary DFS from each accepting state to check whether the accepting state can reach itself (forming an accepting cycle). If an accepting cycle exists, the product has a counterexample; if not, φ holds in M.

**Symbolic model checking** (Ken McMillan, 1992) replaces explicit-state enumeration with **Ordered Binary Decision Diagrams (OBDDs)** — a canonical representation of Boolean functions that can be exponentially more compact than explicit enumeration. The state transition relation — a Boolean formula relating current-state variables to next-state variables — is represented as an OBDD, and the set of reachable states is computed by **fixed-point iteration** (image computation): from a set of states S, compute the set of successor states by existential quantification over the transition relation. OBDD-based model checking was the breakthrough that moved model checking from academic curiosity to industrial practice in the 1990s, enabling the verification of hardware designs with 10¹²⁰ reachable states — a number far beyond explicit enumeration.

**Bounded model checking (BMC)** (Biere et al., 1999) takes yet another approach: unroll the transition relation for k steps, encode the resulting formula as a SAT instance, and ask the SAT solver "is there an execution of length k that violates the property?" BMC is incomplete — it only checks for counterexamples within the bound — but it is remarkably effective in practice, and its incomplete nature can be overcome by computing the **completeness threshold**: the smallest k such that if no counterexample of length k exists, no counterexample of any length exists. For many systems, the completeness threshold is surprisingly small (the **recurrence diameter** — the longest loop-free path — is a common bound).

**Counterexample-Guided Abstraction Refinement (CEGAR)** (Clarke et al., 2000) addresses the state-explosion problem by abstraction: rather than verifying the concrete system, verify an abstract model with fewer states. If the abstract model satisfies the property, so does the concrete system (the abstraction is conservative). If the abstract model has a counterexample, check whether it is **spurious** — whether it corresponds to a real execution in the concrete system. If it is spurious, refine the abstraction to eliminate it and try again. CEGAR automates the most difficult part of abstraction — finding the right level of detail — and it is the foundation of modern software model checkers (SLAM, BLAST, CPAChecker).

**Partial-order reduction** (Valmari, 1991; Godefroid, 1996) exploits the commutativity of independent transitions: if two transitions in different threads operate on disjoint variables, executing them in either order leads to the same state. By exploring only one representative interleaving, partial-order reduction can reduce the state space by an exponential factor — making model checking tractable for concurrent programs where most interleavings are equivalent.

**Required Reading:**
- Edmund M. Clarke, Orna Grumberg & Doron A. Peled, *Model Checking* (MIT Press, 1999/2041), chs. 3–5, 9
- Kenneth L. McMillan, *Symbolic Model Checking* (Kluwer, 1993) — the OBDD breakthrough
- Armin Biere, Alessandro Cimatti, Edmund Clarke & Yunshan Zhu, "Symbolic Model Checking without BDDs" (*TACAS*, 1999): 193–207 — BMC origin paper
- Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu & Helmut Veith, "Counterexample-Guided Abstraction Refinement" (*CAV*, 2000)
- Antti Valmari, "Stubborn Sets for Reduced State Space Generation" (*Advances in Petri Nets*, 1991)
- UoY Model Checker Lab: Verify a mutual-exclusion protocol with NuSMV (2040)

**Discussion Questions:**
1. NDFS requires two passes of DFS. Why is a single DFS insufficient for detecting accepting cycles — and what is the precise role of the secondary search?
2. OBDD-based model checking can handle 10¹²⁰ states, yet it struggles with certain circuits (e.g., multipliers). What property of a circuit determines whether its OBDD representation is compact or exponential?
3. CEGAR relies on the existence of a spurious counterexample to trigger refinement. What happens if the abstraction is too coarse to prove the property but too fine to generate a spurious counterexample — a "CEGAR loop"?

---

## Lecture 5: Hoare Logic and Deductive Program Verification

Testing samples behaviour; model checking exhaustively explores finite-state behaviour; **deductive verification** *reasons* about behaviour. The foundational calculus for deductive verification is **Hoare logic** (C.A.R. Hoare, 1969), a formal system for reasoning about the correctness of imperative programs. A Hoare triple {P} C {Q} asserts that if the precondition P holds before executing command C, and C terminates, then the postcondition Q holds afterward. Hoare logic provides inference rules for each construct of the programming language:

- **Assignment:** {Q[x ↦ E]} x := E {Q} — Pushing the postcondition backwards through the assignment, substituting E for x. This *backwards* rule is counterintuitive (most people want to compute Q from P) but it is mechanically simpler: it reduces assignment to substitution.
- **Sequencing:** from {P} C₁ {R} and {R} C₂ {Q}, infer {P} C₁; C₂ {Q} — the intermediate assertion R is the glue.
- **Conditional:** from {P ∧ B} C₁ {Q} and {P ∧ ¬B} C₂ {Q}, infer {P} if B then C₁ else C₂ {Q}.
- **While loop:** from {P ∧ B} C {P}, infer {P} while B do C {P ∧ ¬B}. The assertion P is the **loop invariant** — it must hold before the loop, be preserved by the loop body, and (together with the negation of the guard) imply the desired postcondition. The loop invariant is where the human insight enters: there is no algorithm for discovering loop invariants in general (the problem is undecidable).

The **Weakest Precondition (WP) calculus** (Dijkstra, 1975) mechanises Hoare logic: wp(C, Q) is the weakest precondition that guarantees that C terminates in a state satisfying Q. The WP of a sequence is wp(C₁, wp(C₂, Q)). The WP of an assignment is substitution. The WP of a conditional is (B → wp(C₁, Q)) ∧ (¬B → wp(C₂, Q)). The WP of a loop — ah, there's the rub. wp(while B do C, Q) is an infinite disjunction that cannot be expressed in first-order logic in general. Loop invariants are the finite approximation: an invariant I that is strong enough to establish Q but weak enough to be preserved by the loop body.

In practice, deductive verification proceeds as follows. The programmer annotates the source code with preconditions, postconditions, and loop invariants (and, for functions with side effects, **frame conditions** — which parts of the heap may be modified). A verification-condition generator (VCG) — the Why3 framework, the Frama-C/WP plugin, Dafny, or VeriFast — translates the annotated program into a set of **verification conditions (VCs)**: first-order logic formulas whose validity implies the correctness of the program. The VCs are then discharged by automatic theorem provers (Z3, Alt-Ergo, CVC5) or, for the hard cases, by an interactive proof assistant (Coq, Isabelle).

The **framing problem** is the central difficulty of deductive verification for heap-manipulating programs: when a procedure modifies one field of one object, how do we know that the rest of the heap is unchanged? **Separation Logic** (Reynolds, 2002; O'Hearn, Ishtiaq) addresses this with the **separating conjunction** P ∗ Q: P and Q hold in *disjoint* portions of the heap. Separation Logic enables **local reasoning**: to verify a procedure that operates on a small data structure, we only need to reason about that data structure — the separating conjunction guarantees that the procedure does not interfere with the rest of the heap. The **frame rule** — {P} C {Q} implies {P ∗ R} C {Q ∗ R} for any R (provided C does not modify variables free in R) — is the mechanism that scales local proofs to whole programs.

**Required Reading:**
- C.A.R. Hoare, "An Axiomatic Basis for Computer Programming" (*Communications of the ACM* 12:10, 1969): 576–580
- Edsger W. Dijkstra, *A Discipline of Programming* (Prentice-Hall, 1976), chs. 1–5
- K. Rustan M. Leino, "Dafny: An Automatic Program Verifier for Functional Correctness" (*LPAR*, 2010)
- John C. Reynolds, "Separation Logic: A Logic for Shared Mutable Data Structures" (*LICS*, 2002)
- Jean-Christophe Filliâtre & Andrei Paskevich, "Why3 — Where Programs Meet Provers" (*ESOP*, 2013)
- UoY Dafny Lab: verify insertion sort, binary search, and a red-black tree (2040)

**Discussion Questions:**
1. Loop invariants are the "human insight" bottleneck in deductive verification. What would it take to automate loop-invariant discovery — and what are the most promising approaches (predicate abstraction, ICE learning, LLM-guided synthesis)?
2. Separation Logic replaced the "global reasoning" of classical Hoare logic with "local reasoning." What, precisely, makes local reasoning scale better — and what are its limits?
3. Dafny, Frama-C, and VeriFast all implement Hoare-logic verification, but with different languages (Dafny, C, C/Java). What design decisions make a language amenable or hostile to deductive verification?

---

## Lecture 6: The Curry-Howard Correspondence — Propositions as Types, Proofs as Programs

The most profound idea in the foundations of computation is the **Curry-Howard correspondence** (Curry, 1958; Howard, 1980): the observation that the types of a programming language are isomorphic to the propositions of a logic, and the programs of those types are isomorphic to the proofs of those propositions. This is not a metaphor or an analogy; it is a mathematical isomorphism. Every constructive proof corresponds to a program; every type corresponds to a theorem; and program evaluation corresponds to proof simplification (cut elimination).

The correspondence manifests in several canonical pairs:

| Logic | Programming Language Feature |
|-------|------------------------------|
| Proposition | Type |
| Proof | Program (term) |
| Implication A → B | Function type A → B |
| Conjunction A ∧ B | Product type A × B (pair) |
| Disjunction A ∨ B | Sum type A + B (tagged union) |
| Truth (⊤) | Unit type (()) |
| Falsehood (⊥) | Empty type (Void) |
| Universal quantification ∀x. P(x) | Dependent function Π(x:A). B(x) |
| Existential quantification ∃x. P(x) | Dependent pair Σ(x:A). B(x) |
| Induction | Recursion |

In **simply typed λ-calculus** (Church, 1940), the types correspond to propositions of minimal implicational logic, and the typed λ-terms correspond to proofs in natural deduction. The reduction of a λ-term (β-reduction) corresponds to the normalisation of a proof (cut elimination). A term that type-checks is a valid proof; a type error is an invalid inference.

**Dependent type theory** (Martin-Löf, 1972) extends the correspondence to full first-order (and higher-order) logic: types can *depend* on values. A dependent function type Π(x:A). B(x) is the type of functions that, given an argument x of type A, return a result of type B(x) — where B(x) is a type that may vary with x. If A is a type representing natural numbers, and B(n) is a type representing "n is a prime number" (a proposition), then a function of type Π(n:ℕ). B(n) is a proof that every natural number is prime — which is false, so no such function exists. But if B(n) represents "n is either prime or composite," the function exists and constitutes a proof of the theorem.

Dependent types enable the **specification of functional correctness entirely within the type system**. A sorting function can be given the type:

```
sort : Π(xs : List A) → Σ(ys : List A). (Sorted ys ∧ Permutation xs ys)
```

Read: "for all lists xs, there exists a list ys such that ys is sorted and ys is a permutation of xs." A program of this type is simultaneously (a) a sorting function and (b) a machine-checkable proof that the function is correct. There is no need for a separate specification language, a separate verification tool, or a separate proof — the type *is* the specification, and the program *is* the proof.

The **Calculus of Inductive Constructions (CIC)** — the foundation of Coq and Lean — combines dependent types with a rich system of inductive definitions. An inductive type (like `Nat`, `List`, or `Tree`) is defined by its **constructors**, and its elimination rule provides structural induction. The combination of dependent types + induction yields a logic that is as expressive as higher-order arithmetic — sufficient to formalise most of mathematics. The Coq proof of the Four-Colour Theorem (Gonthier, 2005) and the Lean proof of the Liquid Tensor Experiment (Scholze et al., 2022) demonstrate that dependent type theory is a practical vehicle for deep mathematics.

The **`Prop` vs `Type` universe distinction** (Coq) separates *proof-relevant* types (in `Type`) from *proof-irrelevant* propositions (in `Prop`). A function returning a value in `Prop` is erased at runtime — the proof is checked, then discarded, ensuring that verification incurs no runtime overhead. This is the mechanism that makes verified compilation (CompCert) practical: the correctness proof of the compiler is erased; only the executable code remains.

**Required Reading:**
- William A. Howard, "The Formulae-as-Types Notion of Construction" (1969, published 1980 in *To H.B. Curry: Essays on Combinatory Logic*)
- Philip Wadler, "Propositions as Types" (*Communications of the ACM* 58:12, 2015): 75–84 — a beautiful, accessible survey
- Per Martin-Löf, *Intuitionistic Type Theory* (Bibliopolis, 1984)
- Benjamin C. Pierce et al., *Software Foundations*, Volume 1: *Logical Foundations* (online, continuously updated) — the standard Coq textbook
- Georges Gonthier, "Formal Proof — The Four-Color Theorem" (*Notices of the AMS* 55:11, 2008): 1382–1393
- UoY Curry-Howard Explorer: Interactive mapping from logical formulas to types (2040)

**Discussion Questions:**
1. The Curry-Howard correspondence applies only to *constructive* logic — the Law of Excluded Middle (P ∨ ¬P) has no computational interpretation. What is lost, and what is gained, by restricting to constructive proofs?
2. Dependent types can express any functional-correctness specification. Why, then, are they not yet the dominant paradigm in software verification? What are the practical obstacles?
3. The proof-irrelevance of `Prop` ensures that proofs are erased at runtime. Is this always safe — and what happens when a proof is used computationally (e.g., to guide an algorithm)?

---

## Lecture 7: Interactive Theorem Proving with Coq — The Art of Proof by Machine

A proof assistant is a chess game between human and machine: the human proposes moves (tactics), and the machine checks that each move is legal (constructs a valid proof term). Unlike an automatic theorem prover, which either succeeds silently or fails mysteriously, a proof assistant provides a live, interactive **proof state** — the current goal, the hypotheses available, and the subgoals that remain — giving the user continuous feedback on the structure of the proof.

**Coq** (1989, INRIA) is the most mature and widely used proof assistant for program verification. Its logic, the Calculus of Inductive Constructions (CIC), is an extension of Martin-Löf type theory with an impredicative universe of propositions (Prop) and a rich system of coinductive types. Coq's **Gallina** specification language is a functional programming language with dependent types, and its **Ltac** (and, since 2018, **Ltac2**) tactic language is a meta-programming layer for constructing proofs.

A Coq proof proceeds by **tactics** — commands that transform the current proof goal:

- `intros` — move hypotheses (premises, universally quantified variables) from the goal into the context
- `apply H` — if H is an implication whose conclusion matches the goal, replace the goal with H's premises
- `destruct x` — case analysis on an inductive value x
- `induction n` — apply structural induction on n
- `rewrite H` — use an equality hypothesis H to rewrite the goal
- `auto` — try to solve the goal with a database of hints
- `omega` or `lia` — solve Presburger arithmetic (linear arithmetic over integers)

The art of Coq proving lies in **proof engineering** — structuring proofs so they are readable, maintainable, and robust to changes in definitions. A Coq proof is a program (via Curry-Howard), and like any program, it benefits from modularity, abstraction, and careful naming. The **Ssreflect** (Small-Scale Reflection) extension library, developed for the Four-Colour Theorem proof, introduced a disciplined proof style based on small, compositional lemmas and a restricted set of tactics. Ssreflect proofs are denser than traditional Coq proofs but more robust — less dependent on automation that may break when the definitions change.

**Verified programs in Coq** follow the **deep embedding** or **shallow embedding** approach:

- In a **deep embedding**, the syntax and semantics of the programming language are defined as inductive types in Coq, and programs in that language are reasoned about as Coq data structures. This is the approach of CompCert (a verified C compiler) and VST (Verified Software Toolchain).
- In a **shallow embedding**, programs are written directly in Gallina (Coq's functional language), and the semantics is inherited from Coq. This is the approach of the Fiat project (verified data structures and program synthesis) and of Bedrock (verified low-level code).

The **Verified Software Toolchain (VST)** (Appel et al., Princeton) provides a framework for verifying C programs in Coq: the C program is compiled to Clight (a simplified C), Clight is given a formal semantics in Coq, and VST's separation logic — **Verifiable C** — enables modular verification of C functions with preconditions, postconditions, and frame conditions. VST has been used to verify cryptographic libraries, concurrent data structures, and file-system components — real C code, not toy examples.

**Required Reading:**
- Benjamin C. Pierce et al., *Software Foundations*, Volumes 1–3 (online) — the definitive Coq tutorial
- Adam Chlipala, *Certified Programming with Dependent Types* (MIT Press, 2013/2040) — advanced Coq for program verification
- Xavier Leroy, "Formal Verification of a Realistic Compiler" (*Communications of the ACM* 52:7, 2009): 107–115
- Andrew W. Appel, *Program Logics for Certified Compilers* (Cambridge, 2014/2041)
- The Coq Reference Manual (coq.inria.fr, continuously updated)
- UoY Coq Lab: Prove the correctness of a simple expression evaluator and a binary search tree (2040)

**Discussion Questions:**
1. Coq proofs are programs, and like programs, they can be buggy — a "proof" of a false theorem may go undetected if the statement is not what was intended. How do we verify the verifier — and what is the role of small, independently checkable proof kernels?
2. Ssreflect proofs are more robust than traditional Coq proofs but harder to read. Is this a fundamental trade-off — and what would a "best of both worlds" proof style look like?
3. VST can verify real C programs, but the verification effort is measured in weeks per function. What would it take to reduce this to hours — and is full functional verification of C code a realistic goal for most software?

---

## Lecture 8: Lean — Dependent Type Theory for the Working Mathematician

**Lean** (Leonardo de Moura, Microsoft Research, 2015) is a relative newcomer to the proof-assistant landscape, but it has rapidly become one of the most active and influential. Lean's design philosophy differs from Coq's in several key respects:

- **Unified foundations:** Lean is based on a version of the Calculus of Inductive Constructions with **proof irrelevance**, **quotient types**, and **axiom of choice** built in — design decisions that make Lean more familiar to mathematicians, who are accustomed to classical reasoning and quotient constructions.
- **Metaprogramming in Lean itself:** Lean's tactic language is implemented as a monadic DSL *within* Lean — there is no separate tactic language (no Ltac). This means that tactics can be composed, abstracted, and reasoned about using the full power of Lean's type theory. The `simp` tactic, for instance, is a user-extensible rewriting engine powered by a database of lemmas tagged `@[simp]`.
- **`mathlib` — the mathematical library:** Lean's standard mathematical library, `mathlib`, is a community-driven effort to formalise modern mathematics in Lean. As of 2040, `mathlib` contains over 2 million lines of formalised mathematics — algebraic geometry, number theory, measure theory, category theory — and it supports a style of mathematical reasoning that feels natural to working mathematicians.
- **Interactive theorem proving for mathematics:** The **Liquid Tensor Experiment** (2022) — a collaboration between Peter Scholze (Fields Medalist) and the Lean community — formalised a key theorem in Scholze's condensed mathematics in Lean, demonstrating that proof assistants are now capable of handling cutting-edge research mathematics, not just textbook exercises.

Lean's type system is similar to Coq's, with some notable differences. Lean uses a **universe-polymorphic** hierarchy `Sort 0` (Prop), `Sort 1` (Type 0), `Sort 2` (Type 1), etc., with typical ambiguity — the universe levels are inferred automatically, sparing the user from universe bookkeeping. Lean's **typeclass** mechanism (modelled on Haskell's) is used extensively for algebraic structures: a `Group` is a typeclass, and a theorem about groups is a function polymorphic over any type that is an instance of `Group`. This is the same mechanism that allows `1 + 1` to work for natural numbers, integers, rationals, reals, and complex numbers — each has a `HasAdd` instance, and the `+` notation is overloaded via typeclass resolution.

**Program verification in Lean** is less mature than in Coq — there is no Lean equivalent of VST or CompCert (yet) — but Lean's metaprogramming facilities make it an attractive platform for building verification tools. The **F* project** (Microsoft Research, INRIA) uses a combination of dependent types and SMT automation for program verification, and F* programs can be extracted to C or WebAssembly. F* has been used to verify cryptographic implementations (the HACL* library, deployed in Firefox, WireGuard, and the Linux kernel), demonstrating that dependent-type-based verification can produce code that runs in production.

The **Lean 4** release (2023) rewrote the Lean kernel in Lean itself (self-hosting), dramatically improving performance and enabling new applications: efficient computation within proofs (via `native_decide` and `native` compilation), extensible syntax (via custom `elaborators`), and integration with external tools (via the **Lean Language Server Protocol**, LSP). Lean 4 blurred the line between proof assistant and programming language, making it practical to write verified programs that *run fast* — not just programs that *are correct*.

**Required Reading:**
- Jeremy Avigad, Leonardo de Moura & Soonho Kong, *Theorem Proving in Lean 4* (online, continuously updated) — the standard Lean textbook
- Leonardo de Moura & Sebastian Ullrich, "The Lean 4 Theorem Prover and Programming Language" (*CADE*, 2021)
- The `mathlib` Community, *Mathematics in Lean* (online tutorial, 2020/2040)
- Peter Scholze, "Liquid Tensor Experiment" (Xena Project blog, 2021–2022)
- Nikhil Swamy et al., "Dependent Types and Multi-Monadic Effects in F*" (*POPL*, 2016)
- UoY Lean Lab: Formalise basic group theory and prove Lagrange's Theorem (2040)

**Discussion Questions:**
1. Lean's designers chose to build quotient types and classical choice into the foundation, while Coq's CIC is constructive. What are the practical consequences of this choice for a mathematician trying to formalise a proof?
2. `mathlib` is a community effort with over 300 contributors. How does the social organisation of a mathematical library affect its design — and what lessons does `mathlib` offer for software engineering generally?
3. F* combines dependent types with SMT automation. Does this hybrid approach capture the best of both worlds — or does it inherit the worst?

---

## Lecture 9: TLA+ and the Specification of Concurrent and Distributed Systems

**TLA+** (Temporal Logic of Actions) is a specification language designed by Leslie Lamport (Turing Award 2013) for reasoning about concurrent and distributed algorithms. Unlike Hoare logic or dependent type theory, which are designed for sequential programs, TLA+ is designed from the ground up for the hardest class of systems: asynchronous distributed algorithms where processes may fail, messages may be lost, and the global state is only a theoretical construct.

A TLA+ specification describes a system as a **state machine**: a set of variables, an initial predicate on those variables, and a **next-state relation** that describes how the variables may change in a single step. The next-state relation is a disjunction of **actions** — each action is a formula relating the current (unprimed) variables to the next-state (primed) variables. For example, a simple counter with increment and decrement actions:

```
Init ≜ count = 0
Increment ≜ count' = count + 1
Decrement ≜ count' = count - 1
Next ≜ Increment ∨ Decrement
Spec ≜ Init ∧ □[Next]_count
```

The formula `□[Next]_count` (read: "always Next or count unchanged") is a **stuttering-invariant** next-state formula: it allows steps where nothing changes (stuttering steps), which is essential for compositional reasoning — a component's specification must not rule out the possibility that other components are making progress.

TLA+ properties are expressed as temporal formulas. **Safety** properties are invariants:
```
Inv ≜ count ≥ 0
THEOREM Spec ⇒ □Inv
```
**Liveness** properties use weak and strong fairness: `WF_v(A)` ("weak fairness of action A on variable v") asserts that if A is continuously enabled, it must eventually occur. `SF_v(A)` ("strong fairness") asserts that if A is repeatedly enabled, it must eventually occur.

The **TLC model checker** exhaustively checks finite-state instances of TLA+ specifications. Unlike symbolic model checkers, TLC is explicit-state, but it compensates with several innovations: **symmetry reduction** (if the specification is symmetric under permutation of process IDs, explore only one representative interleaving), **state compression**, and **distributed model checking** (TLC can run on a cluster, with each worker exploring a portion of the state space).

TLA+ has been used to find subtle design bugs in industrial systems: Amazon Web Services uses TLA+ to specify and verify core distributed algorithms (S3 consistency, DynamoDB replication); Microsoft uses TLA+ for the Azure Cosmos DB consistency protocol; and the TLA+ specification of the Raft consensus algorithm (Ongaro, 2014) became the reference specification against which all implementations are measured. The hallmark of a TLA+ specification is not just that it enables verification but that it *clarifies the design* — the process of writing the specification often reveals ambiguities and edge cases that the informal design document overlooked.

**PlusCal** is an alternative syntax for TLA+ that resembles a pseudo-code programming language. PlusCal is translated to TLA+ automatically, making it more accessible to engineers who find the raw mathematical notation of TLA+ intimidating. The translation is transparent — the PlusCal source and the generated TLA+ are shown side by side — and the model checking is performed on the TLA+.

Lamport's philosophy of specification — articulated in his essay "Who Builds a House Without Drawing Blueprints?" (2015) — is that specification is *design*, not verification. The primary value of writing a TLA+ specification is the clarity it imposes on the designer's thinking; the ability to model-check is a bonus. This philosophy explains why TLA+ is used at Amazon and Microsoft not by verification specialists but by ordinary engineers designing ordinary systems.

**Required Reading:**
- Leslie Lamport, *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers* (Addison-Wesley, 2002)
- Leslie Lamport, "The Temporal Logic of Actions" (*ACM Transactions on Programming Languages and Systems* 16:3, 1994): 872–923
- Chris Newcombe, Tim Rath, Fan Zhang, Bogdan Munteanu & Marc Brooker, "How Amazon Web Services Uses Formal Methods" (*Communications of the ACM* 58:4, 2015): 66–73
- Diego Ongaro, "Consensus: Bridging Theory and Practice" (PhD thesis, Stanford, 2014), chs. 5–9 — the Raft specification
- Hillel Wayne, *Practical TLA+: Planning Driven Development* (Apress, 2018/2042)
- UoY TLA+ Lab: Specify and model-check a two-phase commit protocol (2040)

**Discussion Questions:**
1. TLA+ is "stuttering-insensitive" — stuttering steps are always allowed. Why is this crucial for compositional reasoning — and what would break if stuttering were forbidden?
2. Amazon engineers report that TLA+ catches bugs that would be nearly impossible to find through testing. What properties of distributed systems make them particularly amenable to formal specification and particularly resistant to testing?
3. Lamport argues that specification is valuable even without verification. Is this true — or is an unverified specification a false sense of security?

---

## Lecture 10: Abstract Interpretation — Sound Approximation for Infinite-State Programs

Model checking works for finite-state systems. Deductive verification works for infinite-state programs — but requires loop invariants, which demand human insight. **Abstract interpretation** (Patrick and Radhia Cousot, 1977) occupies a sweet spot: it is fully automatic, it scales to millions of lines of code, and it is *sound* — if it says "no error," there truly is no error. The cost is precision: abstract interpretation may report an error that cannot actually occur (a **false alarm**).

The central idea of abstract interpretation is to replace the concrete semantics of a program — which operates over concrete values (integers, pointers, heap objects) — with an **abstract semantics** over an **abstract domain**. The abstract domain is a lattice of abstract values that approximate sets of concrete values. The abstract semantics executes the program over the abstract domain, computing, at each program point, an abstract state that over-approximates all concrete states that can reach that point.

The classic abstract domain is the **interval domain**: abstract values are intervals [ℓ, u] where ℓ ∈ {−∞} ∪ ℤ and u ∈ ℤ ∪ {+∞}. The abstract addition of two intervals: [a, b] + [c, d] = [a+c, b+d]. The abstract multiplication is trickier — it must consider all sign combinations. The interval domain can prove that an array index is within bounds if the computed interval lies within the array's bounds, but it loses precision when there are dependencies between variables: for `x = 5; y = x - 5`, the interval domain computes y ∈ [−∞, +∞], losing the fact that y = 0.

More sophisticated abstract domains recover precision:

- **The polyhedra domain** (Cousot & Halbwachs, 1978) tracks linear inequalities Ax ≤ b between variables — it can capture relationships like x ≥ 0, y = x + 1, but the convex-hull operation is exponential in the number of variables.
- **The octagon domain** (Miné, 2001) tracks constraints of the form ±x ± y ≤ c — a restriction of polyhedra that captures pairwise relationships efficiently (O(n³) for n variables).
- **The symbolic domain** tracks expressions symbolically, enabling precise reasoning about assignments and their consequences.
- **Disjunctive completion** combines multiple abstract states, enabling the analysis to track "either x < 0 or x ≥ 0" precisely through the branches of a conditional.

The **Astrée** static analyser (Cousot et al., 2005) is the landmark success of abstract interpretation. Astrée analyses C programs for runtime errors — division by zero, buffer overflows, null-pointer dereferences, integer overflow — with **zero false alarms** on the flight-control software of the Airbus A380. Achieving zero false alarms required a decade of refinement of the abstract domains — Astrée uses dozens of specialised domains, each targeting a specific class of program patterns — and it demonstrates that sound, automatic verification of real software is possible, given enough domain-specific engineering.

**Facebook Infer** (Calcagno & Distefano, 2015) brings abstract interpretation to the masses: Infer uses **separation logic** and **bi-abduction** (a form of abductive inference for separation logic) to analyse Java, C++, and Objective-C programs incrementally — analysing only the changed code on each commit. Infer is deployed in Facebook's CI pipeline, analysing every diff and reporting potential memory leaks, null-pointer dereferences, and resource leaks. Its success demonstrates that formal methods can be integrated into an agile development workflow — not as an after-the-fact verification step, but as a continuous, developer-facing analysis.

**Required Reading:**
- Patrick Cousot & Radhia Cousot, "Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints" (*POPL*, 1977): 238–252
- Patrick Cousot & Radhia Cousot, "Abstract Interpretation Frameworks" (*Journal of Logic and Computation* 2:4, 1992): 511–547
- Bruno Blanchet et al., "A Static Analyzer for Large Safety-Critical Software" (*PLDI*, 2003) — the Astrée design
- Cristiano Calcagno & Dino Distefano, "Infer: An Automatic Program Verifier for Memory Safety of C Programs" (*NASA Formal Methods*, 2011)
- Antoine Miné, "The Octagon Abstract Domain" (*Higher-Order and Symbolic Computation* 19:1, 2006): 31–100
- UoY Abstract Interpretation Lab: Build a simple interval analyser for a toy language (2040)

**Discussion Questions:**
1. Abstract interpretation is sound but incomplete — it may produce false alarms. Under what circumstances is a false alarm acceptable, and under what circumstances is it not? How do we design a development workflow around a tool that occasionally cries wolf?
2. Astrée achieves zero false alarms on Airbus flight-control software, but only after years of domain-specific tuning. Is this a scalable model for verification — or is it a proof that abstract interpretation requires heroic effort?
3. Infer uses incremental analysis — only analysing changed code. What challenges does incrementality pose for the soundness of the analysis — and how does Infer's bi-abduction engine maintain soundness across incremental updates?

---

## Lecture 11: Industrial Formal Methods — TLA+, Alloy, CBMC, Frama-C, and the Engineer's Toolkit

Formal methods have crossed the chasm from academic curiosity to industrial practice. The tools that succeeded in industry share several characteristics: they are **push-button** (or nearly so), they produce **counterexamples** (not just "yes/no" verdicts), they target **specific, well-defined properties** (not full functional correctness), and they integrate into existing development workflows. This lecture surveys the engineers' formal-methods toolkit.

**Alloy** (Daniel Jackson, MIT) is a lightweight specification language based on **relational logic** — a first-order logic with transitive closure, written in a syntax that resembles object-oriented programming. An Alloy model describes a system as a collection of **signatures** (sets of atoms, with fields that are relations) and **facts** (constraints that all instances must satisfy). The **Alloy Analyzer** translates the model into a SAT instance and uses a SAT solver to find **instances** (models of the specification, showing it is consistent) or **counterexamples** (violations of an assertion). Alloy's scope is bounded — it checks only within a user-specified finite bound — but the **small-scope hypothesis** (Andoni et al., 2003) asserts that most bugs in designs have small counterexamples, and experience confirms this. Alloy is used at MIT, NASA, and industry for modelling security protocols, network topologies, file-system designs, and electoral processes.

**CBMC** (Clarke, Kroening & Lerda, 2004) is a **bounded model checker for C programs**. CBMC translates a C program (with unwound loops, inlined functions) into a SAT formula whose models correspond to executions that violate a given assertion. CBMC is fully automatic — no annotations, no invariants, no proof scripts. It handles a large subset of C (including pointers, dynamic memory, bit operations, and floating-point arithmetic) and is used in industry for verifying embedded software, device drivers, and cryptographic implementations.

**Frama-C** (CEA List, INRIA, 2008) is a modular framework for static analysis of C code, built around a common kernel that parses C, resolves types, and constructs a control-flow graph. Frama-C's **WP** (Weakest Precondition) plugin enables deductive verification: the user annotates C functions with ACSL (ANSI/ISO C Specification Language) contracts, and WP generates verification conditions that are discharged by SMT solvers. Frama-C's **Value Analysis** plugin uses abstract interpretation to compute over-approximations of variable values, detecting runtime errors and unreachable code. Frama-C is used for the verification of safety-critical software in aerospace (Airbus, Thales), nuclear (CEA), and railway (Alstom) industries.

**Z3** (Microsoft Research, 2008) is the most widely used SMT solver, and it is embedded in countless verification tools: Dafny, F*, Boogie, VCC, Viper, and many others. Z3's API (available in Python, C, C++, Java, .NET, and OCaml) enables tools to construct formulas, assert them, check satisfiability, and retrieve models. Z3's success is due not only to its performance (it consistently wins SMT-COMP) but also to its versatility: it supports linear and nonlinear arithmetic, bit-vectors, arrays, algebraic datatypes, uninterpreted functions, quantifiers (with model-based quantifier instantiation, MBQI), and strings. Z3 is the silent partner behind much of modern program verification.

**The Rust type system** (2015) deserves mention as the most successful formal method in mainstream programming: Rust's **ownership types** and **borrow checker** enforce memory safety (no use-after-free, no double-free, no data races) *at compile time*, without garbage collection. The borrow checker is a form of substructural type system (affine types), and while it is not arbitrarily expressive (it proves a specific safety property, not arbitrary functional correctness), it demonstrates that a carefully designed type system can eliminate entire classes of bugs from production software.

**Required Reading:**
- Daniel Jackson, *Software Abstractions: Logic, Language, and Analysis* (revised ed., MIT Press, 2012/2042)
- Daniel Kroening & Michael Tautschnig, "CBMC — C Bounded Model Checker" (*TACAS*, 2014)
- Patrick Baudin et al., "ACSL: ANSI/ISO C Specification Language" (CEA List, continuously updated)
- Leonardo de Moura & Nikolaj Bjørner, "Z3: An Efficient SMT Solver" (*TACAS*, 2008)
- Ralf Jung et al., "RustBelt: Securing the Foundations of the Rust Programming Language" (*POPL*, 2018)
- UoY Formal Methods Tools Day: Hands-on with Alloy, CBMC, and Frama-C (2040)

**Discussion Questions:**
1. Alloy's bounded analysis finds counterexamples within a finite scope. The small-scope hypothesis says that most bugs have small counterexamples. Is this a theorem, an empirical observation, or wishful thinking — and what are the counterexamples to the hypothesis?
2. CBMC, Frama-C/WP, and Rust's borrow checker all target C programs — but with different guarantees and different effort levels. For a given system, how do you decide which tool (or combination) to apply?
3. Z3's dominance as an SMT solver raises a monoculture concern: if a bug in Z3 causes false proofs, every tool depending on Z3 inherits the bug. How do we mitigate this risk — and what are the alternatives to a single-solver ecosystem?

---

## Lecture 12: The Limits of Formal Methods and the Future of Verification

No lecture series on formal methods is complete without a reckoning with their limits. Formal methods can prove the absence of certain classes of bugs — but only under assumptions that must themselves be scrutinised. The specification may be wrong (a proof that the program implements the wrong specification is a proof of nothing useful). The semantics of the programming language may be unsound relative to the compiler (CompCert is a verified compiler, but most C code is compiled with GCC or Clang, whose optimisations are not formally verified). The hardware may have errata (the famous Pentium FDIV bug was a hardware flaw that no software verification could catch). And the human in the loop — the engineer who wrote the specification, the programmer who implemented the system, the verifier who guided the proof — may have made a mistake that no tool catches.

**The De Millo–Lipton–Perlis critique** (1979) argued that formal verification of software is fundamentally different from mathematical proof: a mathematical proof is a social object, validated by a community of mathematicians over years, while a formal proof is checked by a machine and may contain errors that no human ever sees. The critique was prescient — the seL4 project discovered a bug in their own specification during verification, and the bug would not have been caught by testing. But the rebuttal, from the formal-methods community, is that machine-checked proofs are *more reliable* than human-checked proofs precisely because the machine does not get tired, does not overlook cases, does not assume "the rest is obvious."

**The cost barrier** is the most persistent obstacle to adoption. The seL4 microkernel verification cost 20 person-years for 10,000 lines of C. The CompCert compiler verification cost ~4 person-years for a modest compiler. These costs are decreasing — better tools (Dafny, F*, Lean), better automation (SMT solvers, machine learning for proof synthesis), and better training (Software Foundations, mathlib) are gradually reducing the effort required — but formal verification remains an order of magnitude more expensive than testing for most applications.

**AI and formal methods** are converging in promising ways. Large Language Models (LLMs) can generate loop invariants (the hardest part of deductive verification) with surprising accuracy. Reinforcement learning can guide proof search in interactive theorem provers (as demonstrated by DeepMind's AlphaProof and OpenAI's research on neural theorem proving). The **CoqHammer** and **Tactician** tools use machine learning to predict which tactics are likely to succeed, reducing the human effort in Coq proofs. And the **Automated Mathematical Discovery** community is exploring whether AI can *discover* conjectures and proofs, not just verify them — blurring the line between proving and discovering.

**Open challenges in 2040:**

- **Verification of AI systems:** How do we specify the correctness of a neural network? What does it mean for a self-driving car's perception system to be "correct"? Formal methods for probabilistic programs, for differentiable programs, and for learned components are active research frontiers.
- **Verified infrastructure:** The Internet runs on decades-old C code (OpenSSL, BIND, Linux kernel) that has never been formally verified. Can we retrofit verification onto existing systems — or must we rewrite them in verifiable languages (as the ProseMirror/automerge folks have done with Rust)?
- **Proof engineering at scale:** The `mathlib` community has shown that large-scale collaborative formalisation is possible. Can we build a `libverified` — a library of verified software components (cryptographic primitives, data structures, protocols) that engineers can compose with confidence?
- **The economics of verification:** When is verification worth its cost? The answer depends on the cost of failure — and as software controls more of our infrastructure (power grids, water systems, medical devices), the cost of failure rises. Formal methods may become economically inevitable, not as a luxury but as a necessity.

The course ends where it began — with a question. Formal methods offer certainty in a world of uncertainty. They are a torch in the dark — but the torch is heavy, and the path is steep. The engineer who wields formal methods must know not only how to prove but when to prove, not only how to verify but when a test will suffice. This judgment — the wisdom of the formal-methods engineer — cannot be taught in any lecture. It is learned in the forge of practice, where the hammer of logic meets the anvil of reality.

**Required Reading:**
- Richard A. De Millo, Richard J. Lipton & Alan J. Perlis, "Social Processes and Proofs of Theorems and Programs" (*Communications of the ACM* 22:5, 1979): 271–280 — the classic critique
- Gerwin Klein et al., "seL4: Formal Verification of an OS Kernel" (*Communications of the ACM* 53:6, 2010): 107–115
- Cezary Kaliszyk & Josef Urban, "Learning-Assisted Automated Reasoning with Flyspeck" (*Journal of Automated Reasoning* 50:2, 2015)
- Kaiyu Yang & Jia Deng, "Learning to Prove Theorems via Interacting with Proof Assistants" (*ICML*, 2019)
- Sanjit A. Seshia, Dorsa Sadigh & S. Shankar Sastry, "Toward Verified Artificial Intelligence" (*Communications of the ACM* 65:7, 2022): 46–55
- UoY 2040 Formal Methods Summit: Keynote recordings and position papers on the next decade (2040)

**Discussion Questions:**
1. The De Millo–Lipton–Perlis critique is over 60 years old in 2040. Which of their arguments have been refuted by subsequent developments — and which remain valid concerns?
2. AI systems — neural networks, reinforcement-learned policies, large language models — resist formal specification. Is formal verification of AI fundamentally impossible, or merely difficult — and what would a "verified AI" look like?
3. If formal verification becomes 10× cheaper (through better AI, better tools, better libraries), what changes in the software industry — and what remains the same?

---

## Final Examination Preparation

The final examination for CS208 assesses your ability to (1) specify program properties in temporal logic and Hoare logic, (2) apply model checking, SAT/SMT solving, and deductive verification to small but non-trivial programs, (3) explain the theoretical foundations of the major formal-methods approaches, and (4) exercise judgment about when formal methods are appropriate and when they are not.

**Sample Essay Questions (Choose 4 of 8):**

1. **The Verification Spectrum.** Compare and contrast model checking, deductive verification, and abstract interpretation along the dimensions of automation, expressiveness, scalability, and the guarantees they provide. For each approach, give a concrete example of a property it can verify that the others cannot (or can only with disproportionate effort). Conclude with a taxonomy of the kinds of systems for which each approach is best suited.

2. **SAT and the Revolution in Automated Reasoning.** Trace the history of SAT solving from the Cook-Levin theorem (1971) to the CDCL architecture (1999) to modern SMT solvers (2040). What were the key algorithmic innovations that transformed SAT from a theoretical curiosity into an industrial workhorse — and why did they take so long to develop? Discuss the role of the annual SAT Competition in driving progress.

3. **The Curry-Howard Correspondence and Its Consequences.** Explain the Curry-Howard correspondence in detail, including the isomorphism between dependent types and first-order logic. How has this correspondence influenced programming language design (ML, Haskell, Coq, Lean, Rust)? What are the practical limitations of "propositions as types" — and what kinds of correctness properties resist encoding in a type system?

4. **Temporal Logic and the Reactive Systems Challenge.** Why do preconditions and postconditions fail to capture the correctness of reactive systems? Develop an LTL specification for a non-trivial reactive system (e.g., a traffic-light controller, an elevator scheduler, or a cache-coherence protocol) and explain how you would verify it with model checking. Discuss the expressive trade-offs between LTL, CTL, and CTL*.

5. **Separation Logic and the Framing Problem.** Why is reasoning about mutable state (the heap) so much harder than reasoning about immutable state? Explain how Separation Logic's separating conjunction and frame rule enable local reasoning, and illustrate with a small example (e.g., in-place reversal of a linked list). Compare Separation Logic with alternative approaches (ownership types in Rust, dynamic frames, implicit dynamic frames).

6. **The seL4 Verification and the Cost of Proof.** The seL4 microkernel verification is the gold standard of formal verification — a complete, machine-checked proof of functional correctness for a general-purpose OS kernel. Describe the architecture of the seL4 proof (the refinement layers, the invariants, the proof engineering challenges). Critically assess the claim that seL4 demonstrates the feasibility of full formal verification for real software — what are the strongest arguments for and against this claim?

7. **AI Meets Formal Methods.** How are AI and machine learning changing the practice of formal verification? Survey the use of AI for loop-invariant generation, proof-script synthesis, and SAT-solver heuristics. What are the risks of relying on AI-generated proofs — and how can we ensure that AI-assisted verification remains trustworthy?

8. **The Economics of Formal Methods.** Under what circumstances is formal verification worth its cost? Construct a decision framework that takes into account: the cost of failure (human lives, financial loss, reputational damage), the cost of verification (person-hours, tooling, training), the size and complexity of the system, and the availability of alternatives (testing, code review, static analysis). Apply your framework to three concrete cases: a pacemaker, a cryptocurrency exchange, and a social-media recommendation algorithm.

**Research Paper Option (for students in the Honours track):** Choose a formal-methods tool (e.g., Coq, Lean, TLA+, Alloy, CBMC, Frama-C, Z3, Infer, Dafny) and verify a non-trivial program using that tool. Your paper should include: (1) the specification of the program, (2) the verification methodology, (3) the verification script or commands (appended), (4) a discussion of challenges encountered and how they were overcome, and (5) a critical assessment of the tool — what it does well, where it falls short, and what could be improved.
