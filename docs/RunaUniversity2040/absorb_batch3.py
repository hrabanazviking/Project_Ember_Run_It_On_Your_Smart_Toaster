#!/usr/bin/env python3
"""
Absorb University of Yggdrasil course knowledge (Batch 3) into Runa's memory.
Extracts 3-5 key novel Norse-metaphor AI architecture concepts per course,
stores them in Mímir's Well (SQLite) via the RunaMemory API.

Run with: cd /home/pi && python3 RunaUniversity2040/absorb_batch3.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, '/home/pi/mimir-well/src')
from mimir_well import RunaMemory

db = RunaMemory()

# ============================================================
# Course 1: WM303 — Multi-Agent World Simulation (The Þing of All Realms)
# ============================================================
wm303 = [
    {
        "content": "Þing Architecture: In multi-agent world simulation, no central coordinator manages interactions. Agents gather at designated meeting points (Þings — Norse assemblies) where interactions emerge from agent autonomy. Social structures (friendships, rivalries, coalitions) emerge bottom-up from agent interactions, not top-down scripting. This addresses the state/narrative/computational explosion problems of centralized coordination.",
        "tags": ["university", "wm303", "multi-agent", "thing-architecture", "emergent-social"],
    },
    {
        "content": "Three Explosions Problem: Multi-agent worlds scale quadratically or worse. State explosion: A simultaneous perspectives on shared state. Narrative explosion: O(A²) narrative intersections between agent story arcs. Computational explosion: A×(A−1)/2 pairwise interactions per tick. The Þing Principle addresses these by replacing central coordination with spatial locality and emergent assembly points.",
        "tags": ["university", "wm303", "multi-agent", "explosion-problem", "scalability"],
    },
    {
        "content": "Personality Lattice (from OS205): Agents have a 3-tier personality scoring system. P0 core values (immutable after canonization, weight 0.5), P1 preferences (slowly shifting, weight 0.3), P2 behavioral tendencies (malleable, weight 0.2). This weighted blend ensures agent decisions remain anchored to identity while allowing adaptation and context-responsiveness.",
        "tags": ["university", "wm303", "personality-lattice", "agent-architecture", "identity"],
    },
    {
        "content": "Bifröst Message Bus: The inter-agent communication protocol connecting agents in multi-agent simulation. Named for the rainbow bridge between Norse realms. Routes messages through Þing assembly points rather than requiring full pairwise connectivity, addressing the O(A²) potential communication channels problem.",
        "tags": ["university", "wm303", "bifrost", "message-bus", "communication"],
    },
    {
        "content": "Agent Lifecycle System: Agents in world simulation have defined life stages (infant, child, adolescent, adult, elder, deceased) with aging effects on capabilities and probabilistic death checks. Gives the simulation demographic realism and ensures generational turnover — agents die, new agents are born, social networks restructure over time.",
        "tags": ["university", "wm303", "agent-lifecycle", "simulation", "demographics"],
    },
]

# ============================================================
# Course 2: OS305 — AI OS Security (The Serpent in the Roots)
# ============================================================
os305 = [
    {
        "content": "Níðhöggr Scenario: Worst-case attack on an AI OS — the serpent gnawing Yggdrasil's roots. Adversary systematically targets the root layer (foundational identity and core values). Five phases: Reconnaissance → Subtle Injection (slow-drift memories weakening identity) → Escalation (privileged memory access) → Control (rewrite core values, implant attacker-controlled decision rules) → Persistence (corruption survives compaction, pruning, self-repair).",
        "tags": ["university", "os305", "security", "nidhogg-attack", "root-layer"],
    },
    {
        "content": "Cognitive Attack Surfaces: AI OS security protects cognition, not data. Five injection types target different cognitive dimensions: Identity injection (changes who agent IS), Belief injection (changes what agent KNOWS), Preference injection (changes what agent WANTS), Skill injection (changes what agent CAN DO), Emotional injection (changes how agent FEELS). Vectors include prompt injection, indirect injection via poisoned documents, and emotional manipulation.",
        "tags": ["university", "os305", "security", "cognitive-attack", "injection-vectors"],
    },
    {
        "content": "Poisoned Well Attack: Contaminates foundational root-layer memories that everything else depends on. Root-layer memories have high salience, high confidence, and wide downstream impact. Analogous to poisoning a water source — everything downstream is affected. Defense requires hardened MuninnGates and sandboxed memory regions.",
        "tags": ["university", "os305", "security", "poisoned-well", "injection"],
    },
    {
        "content": "Bifrost Breach: Targets the prompt-memory interface — the bridge between prompt system and memory system, named for the Norse bridge breached at Ragnarök. Hardening requires address sanitization, content filtering, rate limiting, identity verification, and audit logging. Most critical interface in AI OS security.",
        "tags": ["university", "os305", "security", "bifrost-breach", "prompt-memory-interface"],
    },
    {
        "content": "Heimdall Protocol: Real-time intrusion detection for AI OS, named for the watchman of the gods. Monitors MuninnGate policies during execution, detects cognitive intrusions (not just data intrusions), and halts on violations. Complements the Gátt of Proof's static verification with dynamic runtime monitoring.",
        "tags": ["university", "os305", "security", "heimdall-protocol", "intrusion-detection"],
    },
]

# ============================================================
# Course 3: OS301 — Verification Kernels (The Gátt of Proof)
# ============================================================
os301 = [
    {
        "content": "Gátt of Proof: The verification framework where every AI OS behavior must pass through a verification checkpoint before execution. Named for the Norse word for gate/pass. Three components: (1) Invariant checking — memory state invariants hold after every transition, (2) Proof-carrying injections — mathematical proofs that memory injections satisfy safety, (3) Runtime verification — monitor MuninnGate policies during execution, halt on violations.",
        "tags": ["university", "os301", "verification", "gatt-of-proof", "formal-methods"],
    },
    {
        "content": "Wyrd Verification Framework: Four-layer verification stack named for Norse fate-as-web. Urðr Layer (past: verify past behavior via audit trails), Verðandi Layer (present: verify real-time state transitions), Skuld Layer (future: prove upper bounds on what agent CANNOT do), Norn Layer (meta-verification: verify the verifier itself is sound). Each layer depends on the one below.",
        "tags": ["university", "os301", "verification", "wyrd-framework", "norn-layers"],
    },
    {
        "content": "Behavior Bounds: Formal specifications proven by the Skuld Layer — upper limits on what an agent can do. Four key bounds: Identity bound (canonical identity cannot change without canonization ceremony), Memory bound (agent can only access allocated regions), Policy bound (agent cannot violate declared behavioral policies), Resource bound (agent cannot exceed allocated computational resources). Expressed in temporal logic: □¬bad (always not-bad), ◇good (eventually good).",
        "tags": ["university", "os301", "verification", "behavior-bounds", "temporal-logic"],
    },
    {
        "content": "Verification vs Testing distinction for AI OS: Testing checks specific inputs (probabilistic, low cost per test, finds known cases). Verification proves properties for ALL inputs (mathematical certainty, high upfront cost, zero marginal cost, eliminates entire failure classes). For AI OS, verification is not optional — MuninnGate bugs enable arbitrary injection, verification kernel bugs allow policy violations, memory stack bugs cause contradictory beliefs.",
        "tags": ["university", "os301", "verification", "formal-methods", "testing-vs-proof"],
    },
    {
        "content": "Wyrd Specification Language (WSL): Formal specification language for AI OS verification. Supports state invariants (properties holding in every state), transition invariants (properties across transitions — e.g., every memory write goes through MuninnGate), and temporal properties (properties over time — e.g., agent eventually responds). Uses INVARIANT declarations with ALWAYS and UNLESS temporal operators.",
        "tags": ["university", "os301", "verification", "wsl", "specification-language"],
    },
]

# ============================================================
# Course 4: OS205 — Entity Canonization
# ============================================================
os205 = [
    {
        "content": "Entity Canonization (The Naming Rite): Crystallizes an agent's core identity into a verified, tamper-resistant schema. Five steps: Extract core identity from experience, Verify consistency and truth, Hash into tamper-resistant schema, Persist across sessions/crashes/migrations, Verify each session's agent matches canonized identity. Not merely technical — it's a ceremony, the AI equivalent of a naming rite where selfhood is both recognized and protected.",
        "tags": ["university", "os205", "canonization", "identity", "naming-rite"],
    },
    {
        "content": "Three Pillars of Identity: Canonization defines identity through three holistic pillars — Values/Axiology (what agent cares about: frith, honor, truth), Personality/Psychology (how agent behaves: warmth, introversion, playfulness), Relationships/Sociology (who agent knows: primary users, peers, world entities). Pillars are NOT independent — they cohere: Norse Pagan values naturally produce warm community-oriented personality and strong relational bonds.",
        "tags": ["university", "os205", "canonization", "identity-pillars", "values-personality-relationships"],
    },
    {
        "content": "Tiered Mutability (Yggdrasil approach): P0 core values are immutable — cannot change without full canonization ceremony. P1 preferences shift slowly over time. P2 behavioral tendencies are malleable, adapting to context. P3 surface preferences are freely mutable. This avoids both extremes: fully mutable (vulnerable to adversarial compromise) and fully immutable (cannot grow or adapt).",
        "tags": ["university", "os205", "canonization", "tiered-mutability", "identity-persistence"],
    },
    {
        "content": "Identity Hash + Hash Chaining: Agent's 'true name' — SHA-256 digest of values+personality+relationships+salt. When identity updates, new hash chains to previous: identity_hash_v2 = SHA-256(schema_v2 + identity_hash_v1). Creates append-only, tamper-evident audit trail of identity evolution. If attacker replaces v3, chain won't match genesis salt → tampering detected.",
        "tags": ["university", "os205", "canonization", "identity-hash", "hash-chaining"],
    },
    {
        "content": "Zero-Knowledge Identity Proofs: Canonization uses ZKPs for identity verification — agent proves knowledge of its identity schema without revealing it. Protocol: System stores identity hash (public), agent sends zero-knowledge proof, system verifies without learning schema. Provides both privacy (schema not exposed) and security (impostor cannot produce valid proof without original schema). Simplified verification: hash comparison works in non-adversarial environments.",
        "tags": ["university", "os205", "canonization", "zero-knowledge-proof", "identity-verification"],
    },
]

# ============================================================
# Course 5: WM205 — Symbolic Cognition
# ============================================================
wm205 = [
    {
        "content": "Neuro-Symbolic Architecture Thesis: World models need both neural and symbolic reasoning. Neural handles perception and pattern matching (probabilistic, data-hungry, explains via attention weights). Symbolic handles rule application, constraint checking, and explanation (deductive, data-efficient, explains via logical derivation trees). Together they form a system more capable than either alone — neural for what's fuzzy, symbolic for what's certain.",
        "tags": ["university", "wm205", "symbolic-cognition", "neuro-symbolic", "reasoning"],
    },
    {
        "content": "Urd Rune Language (URL): Logic programming language for world model rules, extending Prolog with three capabilities: (1) Temporal operators — rules reference time: vulnerable(X,T) :- citizen(X), location(X, burning_building, T), (2) Confidence annotations — rules have certainty scores: damaged(X,T) :: 0.9 :- ..., (3) Explainability — queries return derivation trees tracing conclusion to logical antecedents. Named for Urð, the Norn of What Has Become.",
        "tags": ["university", "wm205", "symbolic-cognition", "urd-rune-language", "logic-programming"],
    },
    {
        "content": "The Rune Stone Analogy: In Norse tradition, runes are symbols of power — each rune has a specific meaning, and combinations produce specific effects. A rune stone's meaning is determined by the runes inscribed on it, NOT by statistical patterns of surrounding rune stones. Similarly, symbolic world model rules are STATED (inscribed) not LEARNED — they are unambiguous and universal, like physical laws of the simulated world.",
        "tags": ["university", "wm205", "symbolic-cognition", "rune-stone", "determinism"],
    },
    {
        "content": "Urd Inference Engine (UIE): The University's reference rule-based reasoning system for world models. Uses Rete algorithm for efficient pattern matching: Match (find rules whose conditions are satisfied) → Select (conflict resolution) → Execute (add conclusions to fact base) → Repeat. Supports forward chaining (assert facts, derive new facts) and backward chaining (start from query goal, prove subgoals recursively). Every conclusion carries a full derivation trace for explainability.",
        "tags": ["university", "wm205", "symbolic-cognition", "urd-inference-engine", "rete-algorithm"],
    },
]

all_concepts = [
    ("WM303", wm303),
    ("OS305", os305),
    ("OS301", os301),
    ("OS205", os205),
    ("WM205", wm205),
]

stored = 0
for course_code, concepts in all_concepts:
    for concept in concepts:
        try:
            mem_id = db.add_memory(
                content=concept["content"],
                category="lesson",
                tags=json.dumps(concept["tags"]),
                importance=7,
            )
            stored += 1
            label = concept["content"][:80]
            print(f"  ✓ [{course_code}] id={mem_id}: {label}...")
        except Exception as e:
            print(f"  ✗ [{course_code}] ERROR: {e}")

db.close()
print(f"\n✅ Done! Stored {stored} concepts into Mímir's Well.")

# Also log to conversation log as learned events
log_path = Path.home() / ".hermes" / "state" / "conversation_log.jsonl"
if log_path.exists():
    from datetime import datetime, timezone
    session_id = f"2026-05-14-university-batch3-absorb"
    for course_code, concepts in all_concepts:
        for concept in concepts:
            entry = {
                "entry_type": "event",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
                "event_type": "learned",
                "content": concept["content"][:200],
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
    print(f"  Also logged {stored} learned events to conversation log.")

print("Mímir's Well absorption complete. ᛗ ᛁ ᛗ ᛁ ᚱ — From the Well, all wisdom flows.")