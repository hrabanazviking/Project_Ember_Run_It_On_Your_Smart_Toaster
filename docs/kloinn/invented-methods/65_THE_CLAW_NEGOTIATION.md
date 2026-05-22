# 65 — The Claw Negotiation

A new method for *operator-agent disagreement protocols* —
informed by Pincer Loop's plan-then-execute pattern and
OpenClaw's two-pincered grip. When operator and Ember
disagree, this is how they meet.

---

## What it solves

Agents sometimes recommend things operators disagree with:
- "Use this approach" — operator: "no, that's wrong."
- "Here's the answer" — operator: "I have different info."
- "I'd suggest X" — operator: "I want Y; please reconsider."

Today: operator types "no, do Y." Agent does Y. The
disagreement is *resolved by operator override*.

The **Claw Negotiation** is more structured: when Ember
*notices* a probable disagreement, it can *negotiate* — offer
alternatives, ask clarifying questions, integrate operator's
correction explicitly.

This isn't AI being argumentative; it's *AI being thoughtful
about its own confidence*.

---

## When this fires

The audit layer + emotional intelligence + meta-learning all
combine to detect:
- Operator just corrected Ember; correction is non-trivial.
- Ember's response had low audit confidence.
- Ember and Well disagree on a fact.

When detected: Claw Negotiation engages instead of just
*applying* the correction.

---

## The negotiation pattern

```
operator: "no, the date was 1066, not 1067."
ember: [detects fact-disagreement]
        [Claw Negotiation activates]

ember (negotiation mode):
  Thank you for the correction. Let me verify.
  
  Your earlier message implied 1067. The Well has:
    - notes/medieval.md chunk 4: "1066"
    - notes/timeline.md chunk 12: "1066-67"
  
  I'll trust your correction (1066). Would you like me to:
    (a) Update notes/medieval.md to be more specific?
    (b) Update notes/timeline.md to remove "67"?
    (c) Leave the Well as-is; just remember 1066 for this session?
  
  > c
  
ember:
  Noted. 1066 it is.
```

The agent *engages* the disagreement. Surface options. Let
operator decide.

---

## What this is NOT

🔴 **Reject**:

### 1. Arguing

Ember doesn't *push back* against the operator. It *acknowledges*
their correction and offers structured handling.

### 2. False humility

If Ember has high confidence + the correction seems wrong,
it can *gently* say so:

```
ember: I'd actually suggest 1066 was the correct date —
the Well has multiple sources confirming. Want me to share
them, or should I just use 1067 as you stated?
```

But Ember always *defers* to operator decision.

### 3. Endless negotiation

Maximum 1-2 negotiation rounds per correction. Then accept
the operator's stance.

---

## What this enables

### 1. Operator-AI knowledge synthesis

When operator corrects Ember, the system *learns* — either:
- "Operator knows better; update Well."
- "Operator is sometimes wrong; flag uncertainty."

This is operator-curated *and* AI-noticed.

### 2. Citation transparency

Claw Negotiation surfaces *what Ember was relying on*. Operator
sees: "Ember had source X; based decision on it; I disagree
because of Y."

This is *exact source attribution at correction time*.

### 3. Reduced misalignment

Without negotiation: operator corrects; Ember just complies. No
learning.

With negotiation: operator corrects; both *reconcile*.

---

## How this composes with meta-learning

Each negotiation outcome feeds back:
- "Operator overrode Ember on this topic 5 times" → suggests
  operator's expertise here is high.
- "Operator confirmed Ember was right after negotiation 3
  times" → suggests operator's first impulse was wrong.

Mirror of Ginnungagap surfaces patterns weekly.

---

## When this should NOT fire

For *minor* corrections:
- Typos.
- Trivial preferences ("call me X not Y").
- Clear operator-knows-better domains.

Just accept. Don't negotiate trivial.

Threshold: Claw fires when *audit signals uncertainty about
Ember's original response*.

---

## What operators see

In Stofa, negotiation gets visual treatment:

```
operator: no, the date was 1066, not 1067.

[Claw Negotiation active]

ember: 
  Source check:
    notes/medieval.md  →  "1066"  
    notes/timeline.md  →  "1066-67"
  
  Your correction matches the Well. Possible Well update:
    [a] Make notes/timeline.md more specific.
    [b] Leave both as-is.
  
> _
```

Visible, structured, brief.

---

## Configuration shape

```yaml
ember:
  claw_negotiation:
    enabled: false               # opt-in V4+
    
    fire_when:
      - operator_correction_is_non_trivial
      - audit_confidence_below: 0.7
      - well_and_ember_disagree
    
    max_rounds: 2
    
    behavior:
      defer_to_operator: true
      surface_sources: true
      offer_well_updates: true
    
    learn_from:
      override_count: true
      confirmation_count: true
```

---

## V4+ ship

🟢 **Phase 4** — when audit + meta-learning are mature.

Implementation:
- Detect disagreement signals.
- Generate negotiation message.
- Parse operator's response.
- Optionally update Well.
- Log to meta-learning.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Negotiation annoys operator | Threshold + max rounds; default off |
| AI seems argumentative | Always defers to operator |
| Wrong fires (false negotiation) | Tune thresholds; meta-learn suppression |

---

## Closing

The Claw Negotiation is **Ember's structured-disagreement
method**. Operator and AI meet at the disagreement, integrate,
move on.

Named for Molty's claw — *the grip that holds without
crushing*. Ember holds its information; defers to operator;
both grow.

V4+ feature. Opt-in. Bounded. Operator-respectful.

This is *AI epistemics done well* — confidence with humility,
defer with reasoning, learn from every correction.
