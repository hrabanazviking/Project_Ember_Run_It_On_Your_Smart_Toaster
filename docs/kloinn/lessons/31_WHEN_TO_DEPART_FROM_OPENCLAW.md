# 31 — When to Depart from OpenClaw

A decision framework for "should we adopt this OpenClaw
pattern?" Useful for any cross-project pattern borrowing.

---

## The framework

For each candidate pattern, ask:

1. **Does it solve a real problem Ember has?**
2. **Does it fit the Vows?**
3. **Does it match Ember's cohort?**
4. **Is the cost acceptable?**
5. **What does declining cost us?**

Each "yes" pushes toward adoption. Each "no" suggests departure.

---

## Question 1: Does it solve a real problem Ember has?

OpenClaw has many features. Not all map to problems Ember
operators actually have.

### Examples where YES

- **Workspace prompt files** (AGENTS.md, SOUL.md). Real problem:
  operators want to shape personality without editing code.
- **Session management** (`/new`, `/sessions list`). Real
  problem: operators want bounded conversation threads.
- **Three release channels**. Real problem: operators have
  different stability tolerance.

### Examples where NO

- **WhatsApp bridge**. Most Ember operators don't use WhatsApp;
  those who do prefer sovereign-leaning channels.
- **ElevenLabs TTS**. We don't want a cloud TTS dependency;
  local Piper is fine.
- **Discord-specific tools**. Niche; many operators don't use
  Discord.

---

## Question 2: Does it fit the Vows?

Each pattern must align with Ember's Vows:

### Vow of Smallness

The pattern must not bloat Ember unreasonably. Small is good;
large is suspicious.

Test: does this add < 10MB to install footprint?

### Vow of Sovereignty

The pattern must not introduce cloud dependencies, telemetry,
or call-home behavior.

Test: does this work fully offline?

### Vow of Graceful Offline

Pattern must degrade well when network is down.

Test: what happens when wifi is off?

### Vow of Tethered Grounding

Pattern must not lead the agent to make ungrounded claims.

Test: does this add citation pathways or undermine them?

### Vow of Modular Authorship

Pattern must not require centralized authority.

Test: can operators curate this themselves, or does it require
a registry/maintainer-curated list?

### Vow of The Unbroken Whole

Pattern must compose cleanly with other realms.

Test: does this require redesigning existing subsystems?

### Examples

- **Gateway pattern**: ✅ Aligns with Smallness (just an
  abstraction), Sovereignty (local-only), Unbroken Whole
  (compose cleanly).
- **ClawHub-style centralized registry**: ❌ Conflicts with
  Modular Authorship.
- **Voice wake**: ✅ Aligns if we use local STT/TTS; ❌ if we
  use ElevenLabs default.

---

## Question 3: Does it match Ember's cohort?

OpenClaw operators are mainstream-leaning. Ember operators are
Pi-curious, Norse-leaning, sovereignty-maximalist.

Patterns that serve one cohort may not serve the other.

### Examples

- **Companion mobile apps**: Some Ember operators *might* want
  this (Phase 5+). Many don't (CLI-only operators). Adopt as
  opt-in.
- **Live Canvas / GUI rendering**: Some Ember operators want;
  many don't. Opt-in for Auga.
- **Always-on daemon**: LARGE-profile operators benefit;
  TINY/SMALL-profile operators suffer. Tier the default.

The pattern: **opt-in features that some cohorts want, off-by-
default for others**.

---

## Question 4: Is the cost acceptable?

Cost in:

### Implementation cost

- 100 lines of Python? Easy.
- 1000 lines? Moderate.
- 10,000 lines + new dependencies? Expensive.

### Maintenance cost

- One-time addition, then stable? Cheap.
- Ongoing maintenance as upstream API changes? Costly.

### Documentation cost

- Self-evident? Free.
- Requires extensive docs? Costly.

### Operator-cognitive cost

- Operators understand it intuitively? Free.
- Operators need to learn new concepts? Costly.

### Dependency cost

- No new dependencies? Free.
- New pip extras? Cheap.
- New core dependencies? Expensive.

For each pattern: estimate. If costs > benefits, defer or
reject.

---

## Question 5: What does declining cost us?

Sometimes the right answer is "this is great; we just can't do
it now." Acknowledging this is honest.

### Examples

- **Native mobile apps**: Great pattern; we cannot build native
  apps. Acknowledged limitation.
- **23+ channel bridges**: Great breadth; we cannot maintain 23
  bridges. Acknowledged limitation.
- **Centralized skill registry**: We don't want it (different
  philosophy). Not really a "decline cost"; just a different
  path.

The first two are *real costs* — operators wanting those leave
for OpenClaw. The third is a *philosophical difference* — both
operators served, different shapes.

---

## A decision matrix

Combine all five questions:

| Pattern | Solves Problem | Fits Vows | Matches Cohort | Cost | Decline Cost | Verdict |
|---|---|---|---|---|---|---|
| Workspace prompt files | ✅ | ✅ | ✅ | Cheap | Low | 🔵 Borrow |
| Three release channels | ✅ | ✅ | ✅ | Cheap | Med | 🔵 Borrow |
| Gateway pattern | ✅ | ✅ | ✅ | Moderate | Med | 🟢 Adapt |
| Sandbox backends | ✅ | ✅ | ✅ | Mod-Expensive | High | 🟢 Adapt |
| Voice Wake | ✅ | ✅ (with subs) | ✅ (some) | Expensive | High | 🟢 Adapt (Phase 5) |
| Native mobile apps | ✅ (some) | ✅ | ✅ (some) | Very expensive | High | 🔴 Reject (V1-V4); Web companion instead |
| ClawHub registry | N/A | ❌ | ❌ | Very expensive | Low | 🔴 Reject |
| WhatsApp bridge | ❌ | ❌ (Meta-dependent) | ❌ | Expensive | Low | 🔴 Reject |
| Live Canvas | ✅ (some) | ✅ | ✅ (some) | Expensive | Med | 🟡 Defer to V5+ |
| Per-session sandbox | ✅ | ✅ | ✅ | Cheap | Low | 🟢 Adapt |

This is the *kind of decision-making* we should apply to every
OpenClaw pattern.

---

## A worked example: voice wake

### Question 1: Real problem?

Yes. Operators want hands-free interaction; voice is the natural
solution.

### Question 2: Vows?

- Smallness: voice components add ~100-300MB (Whisper, Piper). Concerning but acceptable.
- Sovereignty: local-only (no ElevenLabs); we use Piper + Whisper.
- Graceful Offline: works fully offline. ✅
- Tethered Grounding: doesn't affect retrieval. ✅
- Modular Authorship: voice is a sibling (Rödd); opt-in. ✅
- Unbroken Whole: integrates via Gateway; doesn't break anything. ✅

All aligned.

### Question 3: Cohort match?

Some operators want voice. Some don't. Opt-in.

### Question 4: Cost?

- Implementation: ~1500 lines of Python; integration with Whisper + Piper.
- Maintenance: ongoing as Whisper/Piper update.
- Documentation: ~5 pages.
- Operator-cognitive: medium (configure mic; pick voice).
- Dependencies: new pip extra (`ember-agent[voice]`).

Moderate cost.

### Question 5: Decline cost?

Significant. Operators wanting voice will leave for OpenClaw or
build their own.

### Verdict

🟢 **Adapt to Ember Vows in Phase 5.** Worth the cost. Use
local components. Make opt-in.

---

## What declining doesn't mean

Declining a pattern doesn't mean it's *bad*. Often it means:

- It's right for a different cohort.
- It's right for a different time.
- It's right with different implementation.

OpenClaw's choices are *not wrong*. They're just *not ours*.

---

## The "We Should Probably" trap

When studying a successful project, there's temptation to
adopt *everything* they do. "We should probably also have X."

This is a trap. OpenClaw has *more resources* than Ember does;
they can sustain features Ember cannot. Imitating without
capacity = half-built features.

Discipline: *only* adopt patterns where all five questions
align. Reject the rest, even if appealing.

---

## A counter-trap

The opposite trap: *reject everything* OpenClaw does because
"we're different."

Also wrong. OpenClaw's engineers are smart; their patterns
deserve consideration. Reflexive rejection costs us learnings.

Discipline: *consider* every pattern with the five questions;
adopt where aligned; reject where not.

---

## Closing

Departure from OpenClaw is **a deliberate choice, applied per-
pattern**. The five-question framework gives a structured way
to decide.

The Klóinn Codex's value: it *applies the framework* to each
of OpenClaw's patterns. The verdicts (🔵 / 🟢 / 🟡 / 🔴) in each
doc are *the framework's output*.

When future operators ask "why doesn't Ember have X?", the
answer should be findable here: "We considered X. Here are the
five questions; here's our verdict."

Transparent decisions are *good open-source citizenship*. We
publish our reasoning.
