# 42 — Logical Reasoning Audit

How Ember verifies her own reasoning before delivering it.
Catching LLM-hallucinated logic before the operator sees it.

---

## The problem

LLMs are confidently wrong. They produce reasoning that
sounds right but isn't. A chat reply like "since A implies
B, and B implies C, we have C" might have plausible-sounding
content but the implications might be invalid or the
premises wrong.

Yggdrasil's tetheredness defense (cite the Well, don't
invent) reduces *factual* hallucination. The logical-
reasoning audit reduces *inferential* hallucination.

---

## What the audit checks

Three types of verification, run on the LLM's draft response
before it streams to the operator:

### 1. Citation reality check

If the response says "according to your notes on X…", verify
that:
- A Well chunk actually matching "your notes on X" exists.
- The content of the citation is approximately what the
  response claims it says.

If verification fails: replace the citation with "I don't
have direct support for that in your notes" and re-draft.

### 2. Internal consistency check

If the response makes claims of the form "A implies B" or
"B because of C", check that:
- The implication isn't immediately contradicted elsewhere
  in the response.
- Numerical claims (counts, percentages) are consistent
  across the response.
- Temporal claims (X happened before Y) don't conflict.

If contradiction detected: flag for re-draft with explicit
guidance to resolve.

### 3. Capability honesty check

If the response says "I'll do X for you" or "I can do Y",
verify that:
- X corresponds to a real tool Ember has.
- Y is within Ember's actual capability set.

If false claim detected: replace with honest scope
statement ("I can search your Well for X, but I can't
do Y").

---

## How the audit runs

Each verification has two modes:

### Light mode (V1 default)

Runs before streaming begins. Fast (sub-100ms). Catches
the obvious cases.

- Citation reality: regex match on cited document titles +
  presence check in Well.
- Internal consistency: extract numerical/temporal claims
  via regex; flag conflicts.
- Capability honesty: extract "I'll/I can" claims; match
  against the tool registry.

### Deep mode (V2 opt-in)

Runs Funi a second time as a *verifier*. Asks: "Audit this
draft response for unsupported claims, contradictions, or
false capability claims."

Costs ~2× the latency. Opt-in via config.

---

## Where the audit happens in the chat flow

```
operator input
   ↓
retrieval (Bifrǫst)
   ↓
prompt assembly (with register from emotional intelligence)
   ↓
Funi streams response   ← stream pauses ~100ms here
   ↓
[draft buffered locally; not yet streaming to operator]
   ↓
Logical-reasoning audit (V1 light mode)
   ├── passes → response streams to operator
   └── fails → re-draft prompt + run again
                  ↓
                  passes → stream to operator
                  fails again → surface with "I'm uncertain
                                about this; reviewing…"
```

The audit adds ~100ms to first-token latency. Acceptable
for the safety it provides.

---

## What "passes" vs "fails" looks like

### Passes

Most chat turns. The LLM's output is grounded in retrieved
context; reasoning is consistent; capability claims are
honest. Audit completes silently; response streams as usual.

### Fails gracefully

Citation reality fail:
- Draft: "Your notes mention Odin's three ravens..."
- Audit: Well has citations about Odin's *two* ravens (Hugin
  + Munin), not three.
- Re-draft: "Your notes mention Odin's two ravens..."

Internal consistency fail:
- Draft: "There are 12 documents in your Well; let me
  count them... actually, looks like 14."
- Audit: 12 vs 14 conflict.
- Re-draft asks Funi to reconcile.

Capability honesty fail:
- Draft: "I'll email you a summary."
- Audit: Ember has no email tool.
- Re-draft: "I can't email; want me to write a summary you
  can copy?"

---

## Why this matters for trust

Operators learn (over time) that Ember's confidence is
calibrated:

- When she says "according to your notes," the notes exist
  and say what she says they say.
- When she says "I'll do X," X is within her actual
  capability.
- When she draws conclusions, the conclusions follow.

Without the audit, operators can't trust any single response
fully; they have to verify. With the audit, operators can
trust *most* responses and only verify the unusual ones.

Trust-calibration is a *huge* operator value. The audit is
how we build it.

---

## What the audit does NOT do

- **Replace operator judgment.** Ember might still produce
  a wrong conclusion if the underlying retrieval is wrong.
  Audit catches *internal* errors, not *external* errors.
- **Verify external facts.** "Norway is in Europe" doesn't
  need audit (no Well claim); but if Ember says "according
  to your notes, Norway is in Europe" without that being in
  the Well, the citation check catches it.
- **Stop the operator from getting wrong info.** Some wrong
  info will get through. Audit reduces it, doesn't eliminate.
- **Make Ember always slower.** Light mode adds ~100ms.
  Deep mode adds ~2× latency.

---

## How audit interacts with Verdandi

Audit events flow through Verdandi:

- `audit.citation_check.passed` / `.failed`
- `audit.consistency_check.passed` / `.failed`
- `audit.capability_check.passed` / `.failed`
- `audit.redraft_triggered` (with reason)

Stofa's debug overlay shows audit results live (off by
default; debug-only).

If audits fail frequently for a specific kind of response,
Verdandi-fed awareness can surface: "I've noticed my recent
citation checks are failing — your Well may need updating
or my retrieval may need tuning."

---

## Configuration shape

```yaml
yggdrasil:
  reasoning_audit:
    enabled: true                  # default on
    mode: light                     # or "deep" (V2)
    citation_check: true
    consistency_check: true
    capability_check: true
    max_redraft_attempts: 2
    on_persistent_failure:
      surface_to_operator: true    # "I'm uncertain..."
      log_via_verdandi: true
```

Disable any axis if operator finds false-positives. The
goal is *calibration*, not *paranoia*.

---

## Performance characteristics

Light mode adds:
- Citation check: ~50ms (Brunnr lookup per cited doc)
- Consistency check: ~10ms (regex + comparison)
- Capability check: ~5ms (registry lookup)
- Total: ~70-100ms per response

Negligible for chat (response starts streaming after this);
inacceptable for high-volume API use (out of scope).

---

## Risk / known issues

- **False positives.** Audit might re-draft when the
  original was fine. Operators report the case; we tune.
- **Latency.** ~100ms extra per turn. Operators with
  patience-poor use cases can disable.
- **Adversarial LLMs.** A truly mendacious LLM could try
  to evade the audit. Mitigation: audit catches simple
  hallucinations; LLM adversarial behavior is beyond scope.

---

## Open questions for Phase 3

1. **Citation check strictness.** Exact-string match vs
   semantic match? Default to semantic (more forgiving)
   with exact-string as opt-in tightening.
2. **Capability check scope.** Just tools? Or also memory
   operations, MCP servers, etc.?
3. **How visible should re-drafts be?** Default invisible
   (operator sees only the final response); debug mode
   shows them.

---

## Test strategy

Phase 3 ships:

- **Unit tests** for each check (citation, consistency,
  capability) with synthetic drafts.
- **Integration test** with real Funi + real Bifrǫst:
  inject a hallucinated citation, verify the audit
  catches it.
- **Latency regression** — verify audit adds < 150ms
  to first-token time on Pi 5.

---

## Closing

The Logical Reasoning Audit is **the trust calibration
layer**. It makes Ember's confident statements *actually
deserving of confidence*. Without it, operators have to
verify every claim. With it, they trust by default and
verify rarely.

This is what makes Yggdrasil-Ember a *reliable* companion
— not just a capable one.
