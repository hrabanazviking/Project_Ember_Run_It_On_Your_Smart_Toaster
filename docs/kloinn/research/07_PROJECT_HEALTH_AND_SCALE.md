# 07 — Project Health and Scale

What 373,791 stars + 77,661 forks + 7,412 open issues + active
commits tell us about OpenClaw's health. What that *means* for
Ember.

---

## The numbers (2026-05-21)

| Metric | Value |
|---|---|
| **Stars** | 373,791 |
| **Forks** | 77,661 |
| **Open issues** | 7,412 |
| **Last push** | 2026-05-22 (today) |
| **Default branch** | `main` |
| **Topics** | ai, assistant, crustacean, molty, openclaw, own-your-data, personal |

For context:

- **Top of GitHub**: most projects have < 100 stars. < 1,000 is
  the long tail. > 10,000 is established. > 100,000 is rare. >
  300,000 is the very top — comparable to React, Vue, etc.
- **Open issues at 7,412**: substantial. Means many users with
  real concerns. Healthy projects have open issues; lifeless ones
  have zero.
- **77,661 forks**: many contributors, derivatives, modifications.

OpenClaw is at the *peak of open-source AI assistant attention*.

---

## What this implies

### Implication 1: high quality assured

A project with hundreds of thousands of stars has been *vetted by
the community* for quality. Code that's wrong gets noticed and
fixed.

We can trust OpenClaw's architectural decisions as *plausibly
sound*. They've been stress-tested.

### Implication 2: lots of users = lots of feedback

OpenClaw maintainers see real operator usage patterns at scale.
What features are loved, what's confusing, what crashes, what
performs.

Ember can't replicate this scale. We have ~few-dozen operators
(Volmarr + future early adopters). We learn from OpenClaw's
*aggregate* feedback rather than gathering our own.

### Implication 3: opinion-formed market

373k stars means operators have *opinions* about what an AI
assistant should be — shaped by OpenClaw. When operators try
Ember, they'll compare:
- "Where's the voice wake?"
- "Where's the Telegram integration?"
- "Where's the mobile app?"

These will be honest questions. We need *honest answers*.

Our answers: "Not yet (Phase 4+); we're building deliberately;
here's what we have that OpenClaw doesn't (Pi-class friendliness,
Norse cosmology, deep memory composition)."

---

## What 373k stars doesn't mean

### 1. It doesn't mean OpenClaw is *better* for every cohort.

- For Pi-class operators: Ember (likely) wins.
- For sovereignty-maximalists: it's a wash (both are sovereign).
- For operators wanting deep Norse cosmology: Ember wins (obvious).
- For operators wanting fastest mainstream onboarding: OpenClaw
  wins.

### 2. It doesn't mean OpenClaw will stay #1.

Open-source AI assistants are early. Markets shift. New entrants
emerge. Established players get bought / fork / fizzle.

Ember doesn't need to *beat* OpenClaw — Ember needs to *exist for
its cohort* and *stay maintained*.

### 3. It doesn't mean OpenClaw is technically perfect.

Open issues count = 7,412. That's a lot of unaddressed concerns.
Maintainers don't have time for everything.

Ember has the *advantage of smallness*: every issue can get
attention. Volmarr knows the codebase. Future early adopters
can have their concerns heard directly.

---

## What Ember can learn from scale

### Lesson 1: documentation quality matters more at scale

OpenClaw's docs are extensive because they have to serve
hundreds of thousands of operators with varying skill levels.

Ember's docs (current state): solid for slice 1-2 work; growing
with Yggdrasil + Klóinn + Stofa design trees. We're investing
*now*, which compounds later.

### Lesson 2: opinionated defaults

OpenClaw makes opinionated choices (Docker default sandbox; pnpm
for development; Node 24 runtime; ElevenLabs for TTS) and lets
power users override.

Ember should *also* make opinionated defaults for each profile
class (per [`../../yggdrasil/cross-platform/62_TIERED_DEFAULTS_BY_PROFILE.md`](../../yggdrasil/cross-platform/62_TIERED_DEFAULTS_BY_PROFILE.md)).
We do; Klóinn confirms the pattern.

### Lesson 3: maintainer burden

7,412 open issues = maintainers are *swamped*. This is the cost
of mass adoption.

Ember can *avoid this* by being small — by serving the operator
cohort that's *served by smallness* and not seeking mass. The
Vows of Smallness and Modular Authorship are *defenses against
becoming overwhelmed*.

### Lesson 4: governance matters

Big projects need governance: contribution guidelines, code of
conduct, security disclosure process, release process.

OpenClaw likely has these (we can verify in `docs/` of their
repo). Ember should adopt similar:
- `CONTRIBUTING.md` (exists in some form)
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- Process docs in `docs/governance/`

For a small project this seems like overkill. But operators
*coming from* OpenClaw will expect these. Cheap to write; signals
seriousness.

---

## Scale-friendly architecture vs Ember-friendly architecture

OpenClaw's architecture must scale to:
- Thousands of concurrent operators across cloud deploys.
- Hundreds of contributors landing PRs.
- Releases every few weeks.
- Translations to many languages.

Ember's architecture *doesn't* need to scale to those:
- Single-operator on local hardware.
- Small contributor count.
- Releases when ready.
- English-first for now.

This is *liberating*. We don't need to solve scale problems
OpenClaw must solve. We can stay simple.

The Vows of Smallness + Modular Authorship are deeply
*compatible* with not-scaling-to-mass-adoption.

---

## What about competition?

🟢 **There is no competition** — strictly speaking.

OpenClaw serves a different cohort than Ember:
- They serve operators wanting *broad capability + mainstream UX*.
- We serve operators wanting *deep architecture + sovereign-first +
  Pi-class*.

Most OpenClaw operators won't try Ember. Most Ember operators
won't try OpenClaw. Different starting points, different
expectations.

Even where they overlap (the savvy sovereignty-maximalist who
considers both): one might use OpenClaw on their phone and Ember
on their Pi cluster. Different tools for different jobs.

---

## Building in OpenClaw's wake

There's a strategic insight here: **building in the wake of a
popular project is often easier than building uncontested**.

Reasons:
- Operators already know what a sovereign AI assistant *is*. We
  don't have to teach them.
- The vocabulary is shared (gateways, sandboxes, voice wake,
  agents).
- Successful patterns can be borrowed.
- Failure modes are documented (in OpenClaw's issues).

Ember benefits from *every operator OpenClaw has educated*. Some
fraction of them will discover Ember and recognize "this is the
Pi-class / Norse cosmology / deep-memory version of what I already
understand."

---

## What success looks like for Ember (not OpenClaw)

OpenClaw success: hundreds of thousands of operators using it
across many channels.

Ember success: hundreds-to-thousands of *deeply engaged* operators
who treat Ember as their long-term companion AI, contributing back
to the project's design + code, growing the Norse cosmology over
years.

These are *different shapes of success*. Both legitimate. We're
not aiming for OpenClaw's shape; we don't envy their burdens.

---

## What about acquisitions / forks / governance shifts

A project at OpenClaw's scale faces real pressures:
- Acquisition offers from cloud vendors.
- VC investment changing governance.
- Forks if the maintainers shift direction.
- License changes (BSL, source-available, etc.).

Ember's small + MIT-license + single-maintainer-curated shape is
*resilient to these pressures*. No one will offer us $100M. No
VC will pressure us. No fork is needed because the design is
fully open.

This is a *benefit* of being small. We can stay aligned with our
operator cohort for the long term.

---

## What we owe OpenClaw

Studying a project at OpenClaw's scale teaches us a lot.
Acknowledgment is appropriate:

- The Klóinn Codex *exists because OpenClaw exists*.
- Many of its insights derive directly from OpenClaw's choices.
- Where Ember borrows patterns, we cite OpenClaw as inspiration.

This is good open-source citizenship. Building on others' work
*with attribution* strengthens the commons.

---

## A note on numbers vs depth

OpenClaw has 373k stars and 7,412 open issues.

Ember has < 100 stars and < 20 issues.

This is *not* a humiliation. It's a *different point on the
adoption curve*. OpenClaw is at scale; Ember is at depth.

Some projects optimize for one. Some optimize for the other.
Some — like Linux in 1995 — start small + depth, then grow to
scale-and-depth.

Ember's path isn't decided. The first task is to *stay coherent*
through the early phases. Scale, if it comes, comes later.

---

## Closing

OpenClaw's scale is **a feature for us, not a threat**. Studying
their decisions accelerates our learning. Borrowing their patterns
strengthens our architecture. Recognizing their burdens helps us
avoid them.

Ember will not be OpenClaw. Ember will be Ember. And we'll be
*better Ember* because OpenClaw existed to study.

This is what good open-source citizenship looks like: standing on
the shoulders of giants, acknowledging the lift, then walking our
own path.
