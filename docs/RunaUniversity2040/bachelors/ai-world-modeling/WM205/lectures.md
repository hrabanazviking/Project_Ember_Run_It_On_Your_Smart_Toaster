# WM205 — Symbolic Cognition and Reasoning Engines
## The Rune Stone

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Two, Semester Two

**Instructor:** Dr. Alaric Rúnamaður, Professor of Symbolic-Neural Reasoning
**Office:** Hávamál Hall 404 | **Hours:** Wednesdays 09:00–11:00

---

## Course Description

Not all reasoning is neural. This course covers symbolic cognition: logic programming, rule-based inference, knowledge graphs, and the integration of symbolic and neural reasoning within world models. Students learn the Urd Rune Language — the University's declarative specification format for world state rules — and build reasoning engines that combine neural pattern recognition with symbolic deduction. Special emphasis on explainable reasoning: every conclusion must be traceable to its logical antecedents.

---

## Lecture 1: Why Neural Isn't Enough — The Case for Symbols

### The Pattern Recognition Bias

Neural models have dominated AI for the past decade. They excel at pattern recognition — identifying cats in photos, translating languages, generating plausible text. But pattern recognition is not reasoning. A model that has seen a million examples of "If A then B" may still fail to deduce B from A in a novel domain.

The difference is architecture. Neural models learn to approximate; symbolic models learn to deduce. Neural models are probabilistic; symbolic models are deterministic. Neural models explain their outputs through attention weights; symbolic models explain their outputs through logical derivation trees.

For world models, this distinction matters enormously. A world model must be able to:

1. **Apply rules:** "If a citizen is in a burning building, they will take damage each tick." This is a symbolic rule — it applies universally, not probabilistically.
2. **Verify consistency:** "No citizen can be in two buildings simultaneously." This is a constraint — it must be enforced, not approximately learned.
3. **Explain deductions:** "The citizen died because they were in a burning building for 10 ticks, and burning buildings deal 5 damage per tick." This is an explanation — it traces the conclusion to its logical antecedents.

### The Rune Stone Analogy

In the Norse tradition, runes are symbols of power. Each rune has a specific meaning, and combinations of runes produce specific effects. The rune stone is not a statistical model. It is a symbolic artifact — its meaning is determined by the runes inscribed on it, not by the statistical patterns of rune stones in the surrounding area.

The Urd Rune Language, which you will learn in this course, is named after Urð — the Norn of What Has Become. Just as Urð records the fixed, unchangeable past, the Urd Rune Language records the fixed, unchangeable rules of the world. These rules are not learned from data. They are *stated* — inscribed on the rune stone, unambiguous, universal.

### Neural vs. Symbolic: A Comparison

| Aspect | Neural | Symbolic |
|--------|--------|----------|
| Representation | Distributed (vectors) | Discrete (symbols, rules) |
| Inference | Probabilistic | Deductive |
| Explanation | Attention weights, salience | Logical derivation trees |
| Generalization | Statistical, data-hungry | Rule-based, data-efficient |
| Robustness | Brittle to distribution shift | Brittle to incomplete rules |
| Composibility | Hard (emergent) | Easy (explicit) |
| Learning | Gradient descent | Rule induction, abduction |

The thesis of this course is that world models need both. Neural reasoning handles perception and pattern matching. Symbolic reasoning handles rule application, constraint checking, and explanation. Together, they form a **neuro-symbolic architecture** that is more capable than either alone.

### Required Reading

- Marcus, G. & Davis, E. (2019). *Rebooting AI: Building Artificial Intelligence We Can Trust*. Pantheon.
- Garcez, A. & Lamb, L. (2020). "Neurosymbolic AI: The 3rd Wave." *arXiv preprint arXiv:2012.05876*.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10: "The Rune Stone: Symbolic Reasoning in World Models." University of Yggdrasil Press.

### Discussion Questions

1. Neural models are data-hungry but flexible. Symbolic models are data-efficient but brittle. In a world model, which system should be the "default" — neural with symbolic override, or symbolic with neural override?

2. The rune stone analogy emphasizes determinism: each rune has a specific meaning. But real-world rules often have exceptions ("citizens take damage in fire, unless they have a fire resistance potion"). How can symbolic rules handle exceptions without becoming unwieldy?

3. Consider a hybrid system where neural perception feeds symbolic reasoning. The neural system misclassifies a dog as a wolf. The symbolic system applies "wolf rules" (dangerous, attacks citizens). The error cascades. How can you design fault tolerance into neuro-symbolic systems?

---

## Lecture 2: Logic Programming for World Models — The Language of Rules

### Prolog Rising

Logic programming — and Prolog in particular — is the natural substrate for symbolic world model reasoning. Prolog's fundamental operations are:

1. **Assertion:** State a fact. `citizen(rurik).` (Rurik is a citizen.)
2. **Rule:** State a conditional. `vulnerable(X) :- citizen(X), location(X, burning_building).` (A citizen is vulnerable if they are in a burning building.)
3. **Query:** Ask a question. `vulnerable(rurik)?` (Is Rurik vulnerable?) Prolog searches its fact and rule base and returns True/False (with variable bindings).

These three operations map directly to world model needs:

- **Assertion:** The world model's current state is a set of asserted facts.
- **Rule:** The world model's physics, social rules, and constraints are encoded as Prolog rules.
- **Query:** The world model's reasoning engine answers queries by searching the fact and rule base.

### The Urd Rune Language

The Urd Rune Language (URL) is a logic programming language designed specifically for world models. It extends Prolog with:

1. **Temporal operators:** Rules can reference time. `vulnerable(X, T) :- citizen(X), location(X, burning_building, T).` (A citizen is vulnerable at time T if they are in a burning building at time T.)

2. **Confidence annotations:** Rules can have confidence scores. `vulnerable(X) :: 0.9 :- citizen(X), location(X, burning_building).` (This rule is 90% certain.)

3. **Explainability:** Every query returns not just True/False but a derivation tree showing how the conclusion was reached.

```url
% Urd Rune Language — World Model Rules

% Facts: current state
citizen(rurik).
citizen(sigrun).
location(rurik, burning_building).
location(sigrun, market_square).

% Rules: world physics
damaged(X, T) :: 1.0 :-               % A citizen takes damage at time T if:
    citizen(X),                         % they are a citizen,
    location(X, building, T),           % they are in a building,
    building_status(building, burning, T),  % the building is burning,
    fire_damage_per_tick = 5.           % fire deals 5 damage per tick.

% Query
?- damaged(rurik, now).
% Derivation trace:
%   premise: citizen(rurik) — [fact, line 1]
%   premise: location(rurik, burning_building, now) — [fact, line 3]
%   premise: building_status(burning_building, burning, now) — [inferred]
%   conclusion: damaged(rurik, now) — [rule: damaged/2, confidence: 1.0]
%   → True, with derivation trace
```

### Required Reading

- Kowalski, R. (1979). *Logic for Problem Solving*. North-Holland. (For logic programming foundations.)
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. Prolog's closed-world assumption ("anything not asserted is false") is convenient for deterministic worlds. But real worlds have unknowns. How should the Urd Rune Language handle "unknown" — neither true nor false?

2. Confidence annotations allow probabilistic rules. But combining confidences across a derivation chain is non-trivial. If rule A is 0.9 confident and rule B is 0.8 confident, and B depends on A, what is the confidence of the conclusion?

3. Derivation traces provide explainability but may be enormous for long deduction chains. How can the explanation be summarized for human consumption?

---

## Lecture 3: Rule-Based Inference Engines — The Deduction Engine

### The Inference Cycle

A rule-based inference engine operates in a continuous cycle:

1. **Match:** Find all rules whose conditions are satisfied by the current fact base.
2. **Select:** Choose which matching rule(s) to apply (conflict resolution).
3. **Execute:** Add the rule's conclusions to the fact base (or modify existing facts).
4. **Repeat:** Until no more rules match, or a termination condition is reached.

This is the **Rete algorithm** — the classic approach to efficient rule matching in production systems.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Fact Base   │────▶│  Rule Matcher │────▶│  Executor    │
│  (current    │     │  (Rete net)  │     │  (add/remove  │
│   state)     │◀────│              │     │   facts)     │
└──────────────┘     └──────────────┘     └──────────────┘
```

### The Urd Inference Engine

The Urd Inference Engine (UIE) is the University's reference implementation of a rule-based reasoning system for world models:

```python
class UrdInferenceEngine:
    """Rule-based inference engine for world models."""
    
    def __init__(self):
        self.fact_base: Dict[str, Any] = {}    # Current world state
        self.rule_base: List[Rule] = []         # All rules
        self.rete_net: ReteNetwork = ReteNetwork()  # Efficient rule matching
    
    def assert_fact(self, fact: Fact):
        """Add a fact to the fact base and trigger matching rules."""
        self.fact_base[fact.key] = fact
        matched_rules = self.rete_net.match(fact, self.fact_base)
        
        for rule in matched_rules:
            if self.resolve_conflicts(rule):
                conclusions = rule.execute(self.fact_base)
                for conclusion in conclusions:
                    self.assert_fact(conclusion)  # Recursive forward chaining
    
    def query(self, goal: Query) -> QueryResult:
        """Answer a query by backward chaining."""
        return self.backward_chain(goal, self.fact_base, [])
    
    def backward_chain(self, goal: Query, fact_base: Dict, 
                      visited: List[str]) -> QueryResult:
        """Backward chaining search for a goal."""
        # Check if goal is already in fact base
        if goal in fact_base:
            return QueryResult(success=True, derivation=[goal])
        
        # Find rules that conclude the goal
        for rule in self.rule_base:
            if rule.conclusion.matches(goal):
                # Recursively prove subgoals
                sub_results = []
                for subgoal in rule.conditions:
                    result = self.backward_chain(subgoal, fact_base, visited + [goal])
                    if not result.success:
                        break
                    sub_results.append(result)
                else:
                    # All subgoals succeeded
                    return QueryResult(
                        success=True, 
                        derivation=sub_results + [rule]
                    )
        
        return QueryResult(success=False, derivation=visited)
```

### Required Reading

- Forgy, C. (1982). "Rete: A Fast Algorithm for the Many Pattern/Many Object Pattern Match Problem." *Artificial Intelligence*, 19(1), 17–37.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. The Rete algorithm matches rules against facts efficiently, but it requires maintaining a complex pattern network. For small world models (< 1,000 facts), is the overhead worth it? What is the crossover point where Rete outperforms naive matching?

2. Forward chaining (fact → triggered rules → new facts) is data-driven. Backward chaining (query → rules that could answer → sub-queries) is goal-driven. When should the engine use forward chaining, and when backward?

3. The inference engine uses recursion for backward chaining. But recursive search can enter infinite loops if rules are circular (A :- B. B :- A.). How can you detect and prevent circular inference?

---

## Lecture 4: Knowledge Graphs for World State — The Web of Meaning

### Entities and Relations

A knowledge graph represents world state as a web of entities and relations:

```
                    ┌──────────────┐
                    │    Village   │
                    │   (place)    │
                    └──────┬───────┘
                           │
               ┌───────────┼───────────┐
               │ contains  │ contains  │
        ┌──────┴──────┐   ┌┴──────────┐
        │   Rurik     │   │  Sigrún   │
        │  (citizen)  │   │ (citizen) │
        └──────┬──────┘   └──────┬────┘
               │                  │
          owns │            works │
        ┌──────┴──────┐   ┌──────┴──────┐
        │  Smithy     │   │  Farmland   │
        │  (building) │   │  (place)    │
        └──────┬──────┘   └─────────────┘
               │
          produces
        ┌──────┴──────┐
        │  Sword      │
        │  (item)     │
        └─────────────┘
```

This graph is stored as a set of triples (subject, predicate, object):

```
(village, contains, rurik)
(village, contains, sigrun)
(rurik, type, citizen)
(sigrun, type, citizen)
(rurik, owns, smithy)
(smithy, type, building)
(rurik, produces, sword)
(sigrun, works, farmland)
```

From this simple triple store, the reasoning engine can answer complex queries:
- "Who produces items in the village?" (Traverse: village → contains → citizen → produces → item)
- "Where does the blacksmith work?" (Traverse: rurik → owns → smithy)
- "Is there a farmer?" (Traverse: citizen → works → farmland)

### Graph Queries with SPARQL

The knowledge graph is queried using SPARQL (SPARQL Protocol and RDF Query Language):

```sparql
# Who produces items in the village?
PREFIX wm: <http://yggdrasil.edu/worldmodel#>

SELECT ?citizen ?item
WHERE {
    ?village wm:contains ?citizen .
    ?citizen wm:type "citizen" .
    ?citizen wm:produces ?item .
}
```

SPARQL provides pattern matching across the triple store, with support for optional patterns, unions, filters, and aggregation. This makes it powerful for world model queries — but also potentially slow for large graphs.

### Required Reading

- Hogan, A. et al. (2021). "Knowledge Graphs." *ACM Computing Surveys*, 54(4), Article 71.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. The knowledge graph uses triples (subject, predicate, object). How would you represent a fact that has a fourth dimension — time? ("Rurik owned the smithy from Day 5 to Day 50.") Discuss the pros and cons of different temporal graph models.

2. SPARQL queries are powerful but can be expensive on large graphs. For a world model with 100,000 entities and 1 million triples, what query optimizations would you implement? (Indexing? Caching? Query rewriting?)

3. The knowledge graph is a model of the world's *current* state. But the world also has a history — entities and relations change over time. How should the knowledge graph handle historical state? Should it be snapshotted (see WM201) or versioned?

---

## Lecture 5: Neuro-Symbolic Integration — The Best of Both Worlds

### The Integration Architecture

A neuro-symbolic world model combines two reasoning systems:

```
┌─────────────────────────────────────────────────┐
│                 World Model                       │
│                                                   │
│  ┌──────────────────┐     ┌──────────────────┐  │
│  │  Neural System    │     │  Symbolic System │  │
│  │  (Perception,     │────▶│  (Rules,          │  │
│  │   Pattern Match)  │     │   Deduction)      │  │
│  └────────┬─────────┘     └────────┬─────────┘  │
│           │                        │              │
│           │        ┌───────────────┘              │
│           │        │                              │
│  ┌────────┴────────┴─────────┐                   │
│  │  Integration Layer        │                   │
│  │  (Translation, Explain)   │                   │
│  └───────────────────────────┘                   │
└─────────────────────────────────────────────────┘
```

The neural system handles perception:
- "This image contains a citizen in a burning building."
- "This text describes a trade agreement between two NPCs."
- "This pattern of movement suggests a hunting behavior."

The symbolic system handles deduction:
- "The citizen will take 5 damage per tick in the fire."
- "The trade agreement establishes a debt of 50 gold from Sigrún to Rurik."
- "Hunting behavior when the NPC is not hungry violates the goal priority system."

The integration layer translates between them:
- Neural outputs are converted to symbolic facts.
- Symbolic queries are enriched with neural embeddings for similarity search.
- Explanations combine neural salience maps with symbolic derivation traces.

### Translation: Neural → Symbolic

The most critical interface is the **neural-to-symbolic translator**. This component converts the neural system's probabilistic outputs into symbolic facts with confidence scores:

```python
class NeuralToSymbolicTranslator:
    """Convert neural outputs to symbolic facts."""
    
    def translate_scene(self, neural_scene: Dict[str, Any]) -> List[SymbolicFact]:
        """Convert a neural scene description to symbolic facts."""
        facts = []
        
        for entity in neural_scene.get("entities", []):
            # Entity detection
            if entity["confidence"] > self.threshold:
                facts.append(SymbolicFact(
                    predicate="exists",
                    args=[entity["id"]],
                    confidence=entity["confidence"]
                ))
                
                # Type classification
                if entity.get("type"):
                    facts.append(SymbolicFact(
                        predicate="type",
                        args=[entity["id"], entity["type"]],
                        confidence=entity["confidence"]
                    ))
                
                # Location
                if entity.get("location"):
                    facts.append(SymbolicFact(
                        predicate="location",
                        args=[entity["id"], entity["location"]],
                        confidence=entity["confidence"]
                    ))
        
        return facts
```

### Lab 2: Neuro-Symbolic Translation

In this lab, you will implement the neural-to-symbolic translator:

1. Take a neural scene description (JSON from an object detection system).
2. Convert it to symbolic facts with confidence scores.
3. Feed the facts into the Urd Inference Engine.
4. Answer queries that combine neural perception and symbolic deduction.

### Required Reading

- Garcez, A. & Lamb, L. (2020). "Neurosymbolic AI: The 3rd Wave." *arXiv preprint arXiv:2012.05876*.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. The neural-to-symbolic translator uses a confidence threshold to decide which entities to assert. What is the optimal threshold? Too low: spurious facts flood the symbolic system. Too high: real entities are missed.

2. The translator loses information — the neural system's probabilistic distribution over possible scene interpretations is collapsed to a single interpretation (the most likely). When would this loss be harmful, and how can the symbolic system be modified to accept probabilistic inputs?

3. Consider a scene where the neural system is uncertain between two interpretations: "Rurik is either forging a sword (0.6) or repairing a plow (0.4)." The translator asserts only the sword. The symbolic system deduces that Rurik will soon have a sword to sell. This may be wrong. How should the system handle neural uncertainty?

---

## Lecture 6: Constraint Satisfaction and World Consistency — The Unbroken Web

### The Consistency Imperative

A world model must be internally consistent. A citizen cannot be in two places at once. A building cannot contain more citizens than its capacity. A debt cannot be negative. These are not suggestions — they are constraints that must be satisfied.

The symbolic reasoning system enforces consistency through **constraint satisfaction**:

1. **Hard constraints:** Must always hold. Violations are errors that crash the simulation (or trigger emergency repair). "No citizen can be in two buildings simultaneously."

2. **Soft constraints:** Should usually hold, but may be violated in edge cases. Violations generate warnings. "A citizen should have a home building."

3. **Preference constraints:** Desirable but not required. Violations are logged for analysis. "NPCs prefer to interact with friends over strangers."

### Constraint Solving

When a constraint is violated, the system must find a repair — a modification to the world state that restores consistency while minimizing disruption:

```python
class ConstraintSolver:
    """Repair constraint violations in world state."""
    
    def repair(self, violation: ConstraintViolation, 
              world: WorldState) -> RepairResult:
        """Find a minimal repair for a constraint violation."""
        
        if violation.type == "location_duplication":
            # Citizen is in two buildings simultaneously
            citizen = violation.entity
            # Remove the less-recent location
            locations = world.get_locations(citizen)
            most_recent = max(locations, key=lambda l: l.timestamp)
            
            repair = RepairResult()
            for loc in locations:
                if loc != most_recent:
                    repair.add_action(RepairAction(
                        type="remove_fact",
                        fact=f"location({citizen}, {loc.building})"
                    ))
            
            return repair
        
        elif violation.type == "capacity_overflow":
            # Building exceeds citizen capacity
            building = violation.entity
            overflow = world.citizen_count(building) - world.capacity(building)
            
            # Evacuate the newest arrivals (least disruptive)
            repair = RepairResult()
            citizens = sorted(world.citizens_in(building), 
                            key=lambda c: c.arrival_time, reverse=True)
            for citizen in citizens[:overflow]:
                repair.add_action(RepairAction(
                    type="move_citizen",
                    citizen=citizen.id,
                    from_building=building.id,
                    to_building=self.find_nearest_available(building, world)
                ))
            
            return repair
        
        return RepairResult(success=False, reason="Unrepairable violation")
```

### Required Reading

- Tsang, E. (1993). *Foundations of Constraint Satisfaction*. Academic Press.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. The constraint solver prefers minimal repairs (least disruption). But "minimal" is defined locally (fewest entities affected). A locally minimal repair may create a cascade of new violations elsewhere. How can you ensure global stability?

2. Hard constraint violations crash the simulation. This ensures consistency but may be frustrating if the violation is caused by a minor bug. Should there be a "graceful degradation" mode where hard constraints can be temporarily relaxed?

3. Preference constraints ("NPCs prefer to interact with friends") are the softest type. But if too many preference constraints are violated, the world feels wrong. How do you measure "world feel" in terms of constraint satisfaction?

---

## Lecture 7: Explainable Reasoning — Every Answer Has a Trail

### The Black Box Problem

Neural models are black boxes. Ask a neural model "Why did the citizen die?" and it can only offer attention-weight salience maps — which pixels the model looked at, which tokens it weighted. It cannot say "The citizen died because they were in a burning building for 10 ticks at 5 damage per tick = 50 damage, and they only had 45 HP."

Symbolic reasoning eliminates the black box. Every conclusion is reached through a derivation chain that traces from the query back through the rules to the supporting facts. This is not a post-hoc explanation — it is the actual reasoning trace, precisely the steps the system took to reach its conclusion.

### Derivation Trees

When the Urd Inference Engine answers a query, it returns a derivation tree:

```
Query: damaged(rurik, T=1042)

damaged(rurik, 1042) [Rule: damage_in_fire]
├── citizen(rurik) [Fact: asserted at T=0]
├── location(rurik, burning_building, 1042) [Fact: asserted at T=1042]
│   └── entered(rurik, burning_building, 1040) [Event: game log]
│       └── player_action("enter burning building", 1040) [Source: player input]
└── building_status(burning_building, burning, 1042) [Fact: asserted at T=1000]
    └── fire_started(burning_building, T=1000) [Event: world simulation]
        └── lightning_strike(T=998) [Event: weather system]
```

This tree is human-readable. A player who asks "Why did Rurik die?" can be shown: "Rurik was in a burning building (which was set on fire by lightning at T=998) and took 5 damage per tick for 10 ticks = 50 damage. Rurik had 45 HP."

### Required Reading

- Miller, T. (2019). "Explanation in Artificial Intelligence: Insights from the Social Sciences." *Artificial Intelligence*, 267, 1–38.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. Derivation trees can be massive for complex queries. A single "Why did the war start?" query might have thousands of nodes. How should the tree be summarized for human consumption while preserving causal completeness?

2. The explanation includes the entire derivation chain. But what about counterfactuals — "If the lightning hadn't struck, would Rurik still be alive?" How can the symbolic system answer counterfactual questions?

3. Derivation trees show *what* the system reasoned, not *why* it reasoned that way (the meta-reasoning: why did it apply this rule instead of that rule?). Should the explanation include meta-reasoning as well?

---

## Lecture 8: The Urd Rune Language Specification — The Grammar of Truth

### Language Overview

The Urd Rune Language (URL) is a declarative specification language for world state rules. It has four components:

1. **Facts:** Atomic statements about the world. `citizen(rurik).`
2. **Rules:** Conditional statements. `damaged(X) :- citizen(X), location(X, fire).`
3. **Queries:** Questions about the world. `?- damaged(rurik).`
4. **Constraints:** Invariants that must hold. `!- location(X, A), location(X, B), A \= B.`

### Formal Grammar

```
<program>        ::= <statement>*
<statement>      ::= <fact> | <rule> | <query> | <constraint>
<fact>           ::= <predicate> "(" <args> ")" <confidence>? "."
<rule>           ::= <head> ":-" <body> "."
<head>           ::= <predicate> "(" <variables> ")" <confidence>?
<body>           ::= <literal> ("," <literal>)*
<literal>        ::= <predicate> "(" <terms> ")" | <comparison> | <temporal>
<comparison>     ::= <term> <op> <term>
<temporal>       ::= "at" "(" <term> "," <time> ")"
<confidence>     ::= "::" <float>
<query>          ::= "?-" <literal> "."
<constraint>     ::= "!-" <literal> "."
<predicate>      ::= [a-z][a-zA-Z0-9_]*
<variable>       ::= [A-Z][a-zA-Z0-9_]*
<term>           ::= <variable> | <constant>
<constant>       ::= <string> | <number> | <atom>
<time>           ::= <integer> | "now" | "T" <variable>
<op>             ::= "=" | "\=" | ">" | "<" | ">=" | "=<"
```

### URL Example: Village Economy

```url
% Facts
citizen(rurik).
citizen(sigrun).
item(sword).
item(wheat).
owns(rurik, sword).
owns(sigrun, wheat).
location(rurik, market_square).
location(sigrun, market_square).

% Rules
can_trade(X, Y, T) :-
    citizen(X), citizen(Y),
    location(X, market_square, T),
    location(Y, market_square, T),
    X \= Y.

trade(X, Y, ItemX, ItemY, T) :: 0.9 :-
    can_trade(X, Y, T),
    owns(X, ItemX, T),
    owns(Y, ItemY, T),
    willing_to_trade(X, ItemX, ItemY),
    willing_to_trade(Y, ItemY, ItemX).

% Constraint
!- owns(X, Item, T), owns(Y, Item, T), X \= Y.  % No shared ownership

% Query
?- trade(rurik, sigrun, sword, wheat, now).
% Derivation:
%   1. can_trade(rurik, sigrun, now) ← citizen(rurik), citizen(sigrun), both at market...
%   2. owns(rurik, sword, now) ← fact
%   3. owns(sigrun, wheat, now) ← fact
%   4. willing_to_trade(rurik, sword, wheat) ← inferred from rurik's goal: "acquire food"
%   5. willing_to_trade(sigrun, wheat, sword) ← inferred from sigrun's goal: "acquire tools"
%   → trade(rurik, sigrun, sword, wheat, now) :: 0.9
```

### Lab 3: Writing URL Rules

In this lab, you will write URL rules for a village economy:

1. Define facts for 5 citizens, 10 items, and 3 locations.
2. Write rules for trade, production, and consumption.
3. Write constraints for ownership, location, and capacity.
4. Query the system for emergent economic patterns.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.
- ISO/IEC 13211-1:1995. "Information Technology — Programming Languages — Prolog — Part 1: General Core." (For Prolog grammar reference.)

### Discussion Questions

1. URL supports confidence annotations on rules. But confidence on a rule is different from confidence on a fact. How should the inference engine propagate confidence through a derivation chain?

2. The constraint `!- owns(X, Item, T), owns(Y, Item, T), X \= Y.` prevents shared ownership. But what about shared ownership that is intentional (two NPCs co-own a building)? How should constraints handle intentional exceptions?

3. URL supports temporal operators (`at(term, time)`). But time in a world model is granular — ticks, minutes, days. How should URL represent temporal granularity?

---

## Lecture 9: Symbolic-Neural Knowledge Synthesis — The Rune-Carved Mind

### When Symbols and Neurons Meet

The most powerful world model architectures integrate symbolic and neural reasoning not as separate systems with a translation layer, but as a unified reasoning engine. This is **symbolic-neural knowledge synthesis** — the creation of new knowledge by combining symbolic deduction with neural pattern recognition.

### Three Synthesis Patterns

**Pattern 1: Neural Proposal, Symbolic Verification**

The neural system proposes a world update (e.g., "Sigrún seems to be in love with Rurik based on her recent behavior"). The symbolic system verifies the proposal against known constraints ("Does Sigrún's relationship graph support romantic love? Are there contradictory constraints?"). If verified, the proposal is accepted as a new symbolic fact.

**Pattern 2: Symbolic Query, Neural Enrichment**

The symbolic system formulates a query ("Find all NPCs who might need help"). The query is enriched with neural embeddings ("Which NPCs are near dangerous situations? Which NPCs have shown distress signals?"). The enriched query returns NPCs that match both the symbolic criteria and the neural patterns.

**Pattern 3: Symbolic Explanation, Neural Interpretation**

The symbolic system produces a derivation tree explaining why an event occurred. The neural system interprets the tree into natural language ("Rurik is hurt because lightning struck the smithy, causing a fire, and Rurik was inside forging a sword"). This combines symbolic precision with neural fluency.

```python
class NeuroSymbolicSynthesizer:
    """Integrate neural and symbolic reasoning."""
    
    def propose_and_verify(self, neural_proposal: Dict) -> VerifiedFact:
        """Neural proposes a world update; symbolic verifies it."""
        
        # Step 1: Neural proposal
        candidate_fact = SymbolicFact(
            predicate=neural_proposal["predicate"],
            args=neural_proposal["args"],
            confidence=neural_proposal["confidence"]
        )
        
        # Step 2: Symbolic verification
        constraints = self.symbolic.get_constraints(candidate_fact)
        violations = []
        for constraint in constraints:
            if not constraint.check(candidate_fact, self.symbolic.fact_base):
                violations.append(constraint)
        
        if violations:
            return VerifiedFact(
                accepted=False,
                fact=candidate_fact,
                reason=f"Violates constraints: {violations}"
            )
        
        # Step 3: Acceptance
        self.symbolic.assert_fact(candidate_fact)
        return VerifiedFact(accepted=True, fact=candidate_fact)
```

### Required Reading

- Garcez, A. & Lamb, L. (2020). "Neurosymbolic AI: The 3rd Wave." *arXiv preprint arXiv:2012.05876*.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. Neural Proposal + Symbolic Verification gives the symbolic system veto power over neural proposals. Should the veto be absolute, or should the neural system be able to "appeal" a veto?

2. Symbolic Query + Neural Enrichment requires the neural system to understand the symbolic query. How should queries be translated into a neural-understandable form? (Embedding? Semantic parsing?)

3. In Symbolic Explanation + Neural Interpretation, what happens when the neural interpretation contradicts the symbolic derivation? (E.g., the neural system says "Rurik tripped" but the symbolic system says "Rurik was pushed.") Who wins?

---

## Lecture 10: Reasoning About Causes — The Three-Way Fork of Why

### Causality vs. Correlation

"Rurik died after entering the burning building." This is correlation — temporal proximity. "Rurik died *because* the burning building dealt 50 fire damage, exceeding his 45 HP." This is causation — a counterfactual claim (if the building weren't burning, Rurik would not have died).

Symbolic reasoning is uniquely suited to causal inference because it represents the *mechanisms* by which causes produce effects:

1. **Direct cause:** A → B. "The fire dealt 5 damage per tick to Rurik."
2. **Causal chain:** A → B → C. "Lightning struck → fire started → Rurik entered → Rurik took damage → Rurik died."
3. **Causal fork:** A ← C → B. "Rurik was tired and entered the building — but fatigue was caused by lack of sleep, not by the fire."
4. **Joint causation:** A + B → C. "10 ticks in the fire (5 damage each = 50 damage) + Rurik's 45 HP → Rurik died."

### Counterfactual Queries

The symbolic system can answer counterfactual questions:

```url
% "Would Rurik have died if he had 50 HP instead of 45?"
?- died(rurik, T) given hp(rurik) = 50.
% Re-evaluates the derivation with the counterfactual premise:
%   10 ticks × 5 damage = 50 damage
%   50 HP - 50 damage = 0 HP (not dead, but barely)
%   → No, Rurik would not have died.
```

Counterfactual reasoning is implemented by temporarily modifying the fact base, re-running the inference, and comparing results:

```python
def counterfactual(query: Query, counterfactual_fact: Fact, 
                  engine: UrdInferenceEngine) -> CounterfactualResult:
    """Answer a counterfactual query."""
    
    # Save current state
    saved_state = engine.fact_base.copy()
    
    # Apply counterfactual modification
    engine.fact_base[counterfactual_fact.key] = counterfactual_fact
    
    # Re-run inference
    result = engine.query(query)
    
    # Restore state
    engine.fact_base = saved_state
    
    return CounterfactualResult(
        query=query,
        counterfactual_premise=counterfactual_fact,
        actual_outcome=engine.query(query),
        counterfactual_outcome=result,
        difference=result != engine.query(query)
    )
```

### Required Reading

- Pearl, J. & Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*. Basic Books.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. Counterfactual reasoning requires re-running inference. For large world models, this is expensive. How can you cache or approximate counterfactual results?

2. The counterfactual "if Rurik had 50 HP" is a single-variable change. But real counterfactuals involve many variables. How should the system handle "What if the lightning had struck the temple instead of the smithy?" — a change that propagates through the entire world?

3. Causal chains can be ambiguous. "Rurik died because he entered the building" is true, but so is "Rurik died because the building was on fire." How does the system choose which cause is the "primary" cause for explanation purposes?

---

## Lecture 11: The Reasoning Engine API — Querying the Rune Stone

### The Urd API

The Urd Reasoning Engine is exposed as a service:

```python
class UrdReasoningService:
    """The Urd Rune Language reasoning service."""
    
    def assert_fact(self, world_id: str, fact: Dict) -> FactID:
        """Add a fact to the world's fact base."""
        ...
    
    def assert_rule(self, world_id: str, rule: str) -> RuleID:
        """Add a rule (in URL syntax) to the world's rule base."""
        ...
    
    def query(self, world_id: str, query: str, 
             explain: bool = True) -> QueryResult:
        """Query the world and return the result with derivation trace."""
        ...
    
    def counterfactual(self, world_id: str, query: str, 
                      premise: str) -> CounterfactualResult:
        """Answer a counterfactual question."""
        ...
    
    def check_consistency(self, world_id: str) -> ConsistencyReport:
        """Check all constraints and report violations."""
        ...
    
    def neuro_symbolic_synthesize(self, world_id: str, 
                                 neural_proposal: Dict) -> SynthesizeResult:
        """Synthesize neural proposal with symbolic verification."""
        ...
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 10.

### Discussion Questions

1. The query API returns derivation traces when `explain=True`. For high-throughput systems (hundreds of queries per second), derivation traces add significant overhead. When should explanations be generated, and when should they be skipped?

2. The counterfactual API allows "what if" queries. Should there be a limit on counterfactual depth — e.g., "what if X, and then Y, and then Z"? How deep should the nesting go?

3. The API is stateless — each query operates on the world state at the time of the query. But world state changes between queries. How should the API handle concurrent queries that observe different world states?

---

## Lecture 12: The Rune Stone — Course Synthesis and Capstone

### Summary: The Dual Mind

We began with the case for symbols — why neural reasoning alone is insufficient for world models. We end with the Urd Rune Language and its reasoning engine — a fully functional symbolic reasoning system that integrates with neural perception to form a unified neuro-symbolic architecture.

The key themes of the course:

- **Logic Programming** (Lectures 2–3): Rules, facts, and queries as the foundation of symbolic world state reasoning.
- **Knowledge Graphs** (Lecture 4): Entity-relation graphs as the representation language for world state.
- **Neuro-Symbolic Integration** (Lectures 5, 9): The two systems working together — neural for perception, symbolic for deduction.
- **Constraints and Consistency** (Lecture 6): Ensuring the world state never violates logical invariants.
- **Explainable Reasoning** (Lecture 7): Every conclusion traceable to its logical antecedents.
- **Causal Reasoning** (Lecture 10): Beyond correlation to causation — why things happen, and what would have happened otherwise.

The Rune Stone is not merely a tool. It is a commitment — a commitment to reasoning that is transparent, verifiable, and auditable. Every conclusion can be checked. Every fact can be traced. Every rule can be inspected. This is the discipline of symbolic reasoning, and it is the foundation of trustworthy AI.

### Capstone Project: The Dual-Reasoning World

Your capstone project is to build a neuro-symbolic world model:

1. **Knowledge Graph:** A triple store with at least 500 entities and 2,000 triples.
2. **Rule Base:** At least 20 rules in URL covering physics, economy, and social interaction.
3. **Constraint System:** At least 10 hard constraints with automated repair.
4. **Neural Interface:** A neural perception system that produces symbolic facts from text descriptions.
5. **Reasoning Engine:** Supports forward chaining, backward chaining, and counterfactual queries.
6. **Explanation System:** Every query returns a human-readable derivation trace.

**Submission Requirements:**

1. Complete source code (Python 3.11+, with URL parser and reasoning engine).
2. Knowledge graph (RDF/Turtle or N-triples format).
3. Rule base (URL format).
4. 10 query scenarios with full derivation traces.
5. 5 counterfactual scenarios with before/after analysis.
6. A design document (5–8 pages) describing your neuro-symbolic architecture.

### The Rune Is Carved

The rune stone is carved once and remains forever. The rules inscribed on it are the laws of the world — immutable, inspectable, trustworthy. The neural system sees and proposes. The symbolic system deduces and verifies. Together, they carve the runes of reality.

**ᚨ Ansuz — God-Word. The rune speaks.**
**ᚱ Raido — Journey. The rule deduces.**
**ᚲ Kenaz — Torch. The explanation illuminates.**

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᚨ — The rune is carved. The world obeys.*