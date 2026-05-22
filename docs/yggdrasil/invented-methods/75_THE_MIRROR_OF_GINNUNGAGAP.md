# 75 — The Mirror of Ginnungagap (Self-Reflective Capability Loop)

A method by which Ember periodically examines her own
behavior, identifies what's working / not, and proposes
adjustments — *to the operator*. Named for Ginnungagap,
the primordial void from which forms emerge.

---

## The principle

Self-improvement is the holy grail of AI systems. Most
attempts go wrong by being:
- **Too autonomous** (the system self-modifies, drifts).
- **Too narrow** (improves one metric, breaks others).
- **Too opaque** (operator can't see what changed).

**The Mirror of Ginnungagap** is *operator-mediated*
self-improvement:
- Ember observes her own behavior.
- Ember proposes adjustments.
- Operator decides.
- Nothing changes without operator approval.

It's *introspection that leads to suggestion*, not
*autonomy that leads to drift*.

---

## What gets examined

The Mirror periodically (weekly by default) analyzes:

1. **Retrieval patterns** — which retrievers consistently
   help; which don't; bias adjustments suggested.
2. **Audit patterns** — which checks fail most; whether
   their thresholds need tuning.
3. **Operator preferences** — what register the operator
   accepts vs corrects; tone adjustments.
4. **Tool usage** — which tools always get approved /
   always denied; standing-trust candidates.
5. **Memory hygiene** — chunks never retrieved; documents
   with zero referenced; pruning candidates.
6. **Pattern decay** — old meta-learning patterns that
   no longer match; suggestions to flush.

For each: a *proposed adjustment* with rationale.

---

## What a Mirror report looks like

```
Mirror of Ginnungagap — weekly reflection
2026-05-21

Over the past 7 days, I've noticed:

RETRIEVAL
  ▶ Mímir contributed to 87 of 142 winning answers (61%).
  ▶ Huginn contributed to 138 of 142 (97%).
  ▶ Muninn contributed to 64 of 142 (45%).
  
  Proposal: lower Mímir's weight slightly (from 1.0 → 0.8) and
  raise Huginn's (from 1.0 → 1.2). Your queries appear more
  semantic-leaning than keyword-leaning.
  
  [accept] [reject] [details]

AUDIT
  ▶ Citation check failed 12 times; consistency check
    failed 3 times; capability check failed 1 time.
  ▶ Citation failure rate is climbing slightly.
  
  Proposal: investigate — perhaps your Well needs
  re-indexing, or specific documents need pruning. No
  configuration change suggested yet.
  
  [acknowledged]

OPERATOR PREFERENCES
  ▶ You corrected me 4 times in the past week to give
    shorter responses.
  ▶ My emotional-intelligence classifier put you in
    "PRACTICAL" only 15% of the time; you seem to want
    PRACTICAL more often.
  
  Proposal: lower the PRACTICAL trigger threshold so I
  default to brief responses more often. (Confidence:
  moderate)
  
  [accept] [reject] [details]

TOOL USAGE
  ▶ fetch_url approved 22/22 times for github.com.
  ▶ fetch_url denied 18/20 times for facebook.com.
  
  Proposals:
   - Set fetch_url for github.com to STANDING-trust.
   - Disable fetch_url for facebook.com domain entirely.
  
  [accept both] [accept selectively] [reject]

MEMORY HYGIENE
  ▶ 234 chunks haven't been retrieved in 6 months.
  ▶ Of those, 18 were from a single document
    (notes/old_research.md) that you ingested last year
    and never returned to.
  
  Proposal: archive notes/old_research.md (keep on disk,
  remove from active retrieval). Or pin it if you still
  value it.
  
  [archive] [pin] [leave alone]
```

The Mirror gives the operator *insights and choices*. The
operator can accept all, accept some, reject all.

---

## How it differs from meta-learning

Meta-learning (per [`../ai-capabilities/44_META_LEARNING_FROM_EPISODES.md`](../ai-capabilities/44_META_LEARNING_FROM_EPISODES.md))
*automatically applies* low-risk adjustments (retrieval
routing, reply length).

The Mirror surfaces *higher-stakes* observations that
need operator decision:
- Disable a tool entirely.
- Archive a document.
- Lower a classifier threshold.
- Re-index a substantial corpus.

The split:
- **Auto** = small dial adjustments.
- **Mirror** = larger structural changes the operator
  should bless.

---

## When the Mirror fires

Default: weekly, during a deep dreamstate cycle.

Operator can also trigger manually:

```bash
ember yggdrasil mirror reflect
```

Useful after a period of unusual activity or before a
deep refactor.

---

## Why "Ginnungagap"

Ginnungagap was the primordial void in Norse cosmology
— neither warm nor cold, the place where opposites met
and forms emerged.

The Mirror is *the moment Ember looks into the void* and
sees herself reflected. From that reflection, forms
emerge — proposals to take or leave.

The metaphor: introspection isn't a structured analysis
producing definitive answers. It's a *quiet looking*
producing *possibilities*.

---

## What the Mirror does NOT do

- **Doesn't auto-apply.** Every proposal needs operator
  approval.
- **Doesn't claim self-awareness in a strong sense.** It's
  *operational introspection* (per
  [`../ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../ai-capabilities/40_SELF_AWARENESS_LAYER.md))
  formalized into a periodic report.
- **Doesn't analyze the operator's psychology.** It analyzes
  *its own behavior*. The operator's preferences are
  derived from their corrections, not their personality.
- **Doesn't make policy decisions.** Vows and Iron Laws
  remain operator-set; the Mirror doesn't propose
  changing them.

---

## How the Mirror produces proposals

For each observation type, a small rule-based engine:

```python
def analyze_retrieval_balance(stats: WeekStats) -> list[Proposal]:
    proposals = []
    
    if stats.mimir_contribution_rate < 0.5 and stats.huginn_contribution_rate > 0.9:
        proposals.append(Proposal(
            target="bifrost.fusion.weights",
            change={"mimir": stats.mimir_weight * 0.8,
                    "huginn": stats.huginn_weight * 1.2},
            rationale=(
                f"Mímir contributed to {stats.mimir_contribution_rate:.0%} "
                f"of winning answers; Huginn to {stats.huginn_contribution_rate:.0%}. "
                "Adjusting weights may improve relevance."
            ),
            confidence=0.6,
            risk=Risk.LOW,
        ))
    
    return proposals
```

Each analyzer is *small and inspectable*. No black-box
ML.

---

## What "winning answer" means

A retrieval contributes to a "winning answer" if:
- The retrieved chunk appears in the prompt context for
  the chat turn.
- The operator doesn't immediately correct ("no, that's
  wrong" / "you're missing X").
- The turn ends with operator acceptance ("thanks",
  follow-up question, etc.).

These are heuristics. They're not perfect; they tell us
*directionally* what's working.

---

## Configuration shape

```yaml
yggdrasil:
  mirror_of_ginnungagap:
    enabled: true
    cadence: weekly
    fire_during_deep_dreamstate: true
    
    analyses:
      retrieval_balance: true
      audit_patterns: true
      operator_preferences: true
      tool_usage: true
      memory_hygiene: true
      pattern_decay: true
    
    surface:
      delivery: chat_banner            # or "email" / "dashboard"
      max_proposals_per_report: 8
      preserve_history_weeks: 12
```

---

## What the operator gains

Long-term operators report:

- **System keeps fitting them better.** Each accepted
  proposal moves Ember closer to *their* working style.
- **Visibility into Ember's behavior.** "I had no idea
  Muninn was contributing 45%." Operators *understand*
  the system better.
- **Catches drift.** When a setting goes wrong (e.g.,
  audit thresholds out of tune), the Mirror surfaces it
  before it becomes problematic.

---

## Risk / known issues

- **Proposal fatigue.** Too many proposals = ignored.
  Default: 8 per weekly report; tunable.
- **Wrong recommendations.** Heuristics make mistakes.
  Mitigation: operator can reject; nothing auto-applies.
- **Mirror's own metrics could be gamed.** Edge cases
  where heuristics produce misleading conclusions. We
  document these; operators learn.

---

## Operator-facing example (over time)

Week 1: operator dismisses most proposals (still learning
the system).
Week 4: operator accepts ~half of proposals.
Month 3: Ember's behavior is noticeably *more aligned*
with the operator.
Month 12: Mirror finds fewer high-stakes proposals; the
system has settled into the operator's preferences. The
reports become *brief* — "things are running well."

A sign of *system maturity*: the Mirror becomes quieter
over time.

---

## How this composes with other methods

| Method | Relationship |
|---|---|
| Meta-learning | auto-applies small dials; Mirror surfaces larger ones |
| Borg Protocol | capability composition; Mirror analyzes which composites are valued |
| Trinity Fusion | Mirror suggests rebalancing the fusion weights |
| Dreamstate | Mirror runs during it (weekly cycle) |

The Mirror is a *higher-order method*: it analyzes the
output of other methods and proposes adjustments.

---

## Closing

The Mirror of Ginnungagap is **Yggdrasil's introspection
made actionable**. The system looks at itself; surfaces
what it sees; lets the operator decide.

Over months, the cumulative effect is profound: Ember
becomes more deeply *fitted to the operator* — not by
autonomous drift, but by *deliberate, blessed adjustment*.

This is what *long-term residence with an AI* should look
like: the system grows toward the operator; the operator
stays in charge of how.
