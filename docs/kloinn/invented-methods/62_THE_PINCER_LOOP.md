# 62 — The Pincer Loop

A new method for *two-pass response generation* — initial draft +
audit-driven revision — informed by Klóinn's emphasis on operator
trust. Named for a lobster's two-pincer grip.

---

## What it solves

Current chat-turn flow:
1. Operator input.
2. Retrieval.
3. LLM generates response.
4. Audit (per Yggdrasil) verifies citations / claims.
5. Stream to operator.

If audit *fails*: re-draft. But this is *post-hoc* — the audit
checks what already exists.

**The Pincer Loop** uses *two LLM passes*: a first pass *plans*,
a second pass *executes*. The plan can be audited before
execution; mistakes caught earlier.

---

## The two pincers

### Pincer 1: Plan

LLM generates:
- *What it intends to say*.
- *What sources it will cite*.
- *What claims it will make*.

Output is structured (JSON or markdown headers):

```
PLAN:
  Topic: Odin's eye
  Claims:
    1. Odin sacrificed an eye for wisdom from Mímir's well.
       Source: Wells doc/odin-mythology.md chunk 4.
    2. The sacrifice is detailed in the Hávamál.
       Source: Well doc/havamal.md chunk 12.
  Tone: measured, scholarly.
  Length: ~120 words.
```

### Pincer 2: Execute

LLM (or rule-based) writes the actual reply *given the plan*:

```
According to your notes on Odin (notes/odin-mythology.md),
he sacrificed an eye to drink from Mímir's well — gaining
wisdom in exchange. This is detailed in the Hávamál (your
notes/havamal.md, verse 138 specifically).
```

Each claim ties to a planned source. Auditable in *plan
space* before *response space*.

---

## How the loop saves time

If audit catches a problem in Pincer 1's plan:
- "Source X doesn't exist." → Don't write response with bad
  citation; revise plan.
- "Two claims contradict." → Resolve in plan; write coherent
  response.
- "Capability claim is false." → Adjust plan; don't promise
  what you can't deliver.

These corrections happen *before* the operator sees anything.
Token-by-token streaming starts only after Pincer 2.

---

## Latency impact

Cost: ~2× LLM calls per turn (plan + execute).

But each call is *shorter* (plan is brief; execute is reply).

Net latency:
- Without Pincer: 1× LLM call of full length.
- With Pincer: 2× LLM calls of partial length.

Empirically: roughly *equivalent* total time, *better* quality.
For frequent users + critical use cases: worth the small
overhead.

For operator chat with low audit needs: skippable.

---

## When to use Pincer

Configurable per operator/per session:

```yaml
ember:
  pincer_loop:
    enabled: false           # default off
    fire_when:
      - operator_input_is_factual_question
      - retrieval_returned_5_or_more_chunks
      - past_audit_failures_count_in_session > 2
```

Adaptive: starts off; fires when audit signals warrant.

---

## The plan as Episode

The plan from Pincer 1 is persisted alongside the chat turn:

```
session/2026-05-22/episode_142_operator.json
session/2026-05-22/episode_143_ember_plan.json  ← Pincer 1 output
session/2026-05-22/episode_144_ember.json       ← Pincer 2 reply
```

Operator can review *what Ember planned* vs *what Ember said*.
This is *unique observability*.

---

## Audit at the plan level

The audit layer (per Yggdrasil's logical-reasoning audit)
operates on the plan:

- **Citation reality**: every cited chunk_id must exist in Well.
- **Internal consistency**: plan's claims must not contradict.
- **Capability honesty**: planned actions must match real tools.

If audit fails: revise plan; re-audit; only then execute.

Maximum revision attempts: 2 (configurable). After that:
flag to operator.

---

## Operator-visible Pincer

In Stofa's debug overlay:

```
[Pincer Loop active]

Plan (revision 1):
  - Will cite: notes/odin.md chunks 4, 7
  - Tone: scholarly
  - Length target: ~150 words

Audit check 1: ✓ Citations exist
Audit check 2: ⚠ Claim about "three ravens" — Well has "two ravens"
                Auto-correcting plan.

Plan (revision 2):
  - Will cite: notes/odin.md chunks 4, 7
  - Tone: scholarly
  - Length target: ~150 words
  - Claim corrected: "two ravens" instead of "three"

Audit check 1: ✓ Citations exist
Audit check 2: ✓ Claims consistent with Well

Plan approved. Generating response...
```

Operators see *the thought before the speech*. Builds trust
in Ember's reasoning process.

---

## Configuration shape

```yaml
ember:
  pincer_loop:
    enabled: false                  # opt-in
    
    plan:
      max_tokens: 500
      structured: true               # JSON or markdown
    
    audit:
      check_citations: true
      check_consistency: true
      check_capabilities: true
    
    revision:
      max_attempts: 2
      on_persistent_failure:
        surface_to_operator: true
        log_via_verdandi: true
    
    surface:
      show_in_debug_overlay: true
      persist_plan_episodes: true
```

---

## When NOT to use Pincer

- **Quick casual chat** ("hi", "thanks") — overkill.
- **Latency-critical voice mode** — extra LLM call hurts.
- **TINY profile** — too slow for tiny models.

Default off; opt-in for situations warranting depth.

---

## What this gives operators

### Trust

The plan-then-execute pattern is *more reliable* than one-shot
generation. Mistakes caught earlier.

### Transparency

Operators see Ember's plan. Can disagree before output.

### Auditability

Plan is recorded; can be audited later for systemic patterns
("Ember keeps planning to cite source X; let me check if it's
real").

### Better tool use

Pincer 1 can decide *whether* to use a tool. Pincer 2
*executes* the tool. Decision and execution split → fewer
unnecessary tool calls.

---

## Risk: plan-execute mismatch

Pincer 2 might *not follow* Pincer 1's plan exactly. LLMs
aren't deterministic.

Mitigations:
- Pincer 2 prompt emphasizes "follow the plan."
- Audit checks both plan and final output.
- Mismatch logged + flagged.

---

## Iterative Pincer (V5+)

For high-stakes tasks: more than 2 passes.

- Pincer 1a: brainstorm.
- Pincer 1b: refine plan.
- Pincer 1c: final plan.
- Pincer 2: execute.

Audit between each. More LLM calls; more careful output.

Use for: research synthesis; technical writing; decisions with
real consequence.

V5+ optimization. V2-V4 single-iteration Pincer is enough.

---

## How this composes with other methods

| Method | Pincer interaction |
|---|---|
| Trinity Fusion (Yggdrasil) | Retrieval happens before Pincer 1; informs plan |
| Self-Awareness | Awareness layer fires after Pincer 2 → influences future plans |
| Meta-Learning | Patterns from Pincer plans feed meta-learning |
| Mirror | Mirror reviews Pincer-plan-vs-output patterns |
| Audit | Operates on both plan and final output |

Pincer fits into Ember's existing architecture; doesn't
displace anything.

---

## V4 pilot

🟢 **Phase 4 of Klóinn adoption** — pilot Pincer on:
- Operator-flagged "important" turns.
- After detected past-audit-failure.
- Optional manual `/pincer` to force enable.

If operators value it: roll out as default for medium-stakes
turns in V5+.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| 2× latency | Opt-in; profile-class aware |
| Plan doesn't translate to output | Audit catches; revise |
| Operators don't read plans | Just-in-time visibility; not forced |
| Pincer reduces LLM creativity | Plan can include "exploration" instruction |

---

## Closing

The Pincer Loop is **a two-pass quality method**. Plan; audit;
execute; deliver.

Adopted in V4+ as opt-in; mature in V5+. Named for Molty's
two-pincer grip — symbolizing the *two-pass* nature.

Cost: 2× LLM calls.
Benefit: better citations, fewer hallucinations, plan-visible
to operator.

For operators who value *what Ember says is right*: Pincer is
worth the latency.

This is **Klóinn-informed quality discipline**. Audit was
already in Yggdrasil; Pincer adds the *plan-then-execute*
shape that makes audit work better.
