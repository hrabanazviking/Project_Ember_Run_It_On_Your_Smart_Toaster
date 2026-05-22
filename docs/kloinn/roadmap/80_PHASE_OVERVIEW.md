# 80 — Phase Overview

The three-phase roadmap for adopting Klóinn patterns into
Ember. What lands when; what's deferred.

---

## The three phases

| Phase | Name | What ships | Timeline |
|---|---|---|---|
| **1** | Observe and Borrow | Workspace prompt files; sessions; release channels; Humarr Gateway rename; Shed Protocol bones | After Yggdrasil Phase 1 |
| **2** | Bridges and Voice | Matrix + Telegram bridges; Talk Mode; Voice Wake; basic Pincer Loop | After Yggdrasil Phase 4 |
| **3** | Canvas and Channels | OdinUI / Live Canvas; web companion; deep water federation; Mirror integration | After Yggdrasil Phase 5 |

Klóinn phases *follow Yggdrasil phases* — building on the
foundation Yggdrasil establishes.

---

## What goes in each phase

### Klóinn Phase 1 (Observe and Borrow)

Cheap, high-value adoptions that don't require new
infrastructure:

- 🔵 **Workspace prompt files** (AGENTS.md, SOUL.md, TOOLS.md)
- 🔵 **Sessions** with `/new`, `/sessions`, etc.
- 🔵 **Three release channels** (stable/beta/dev on PyPI)
- 🟢 **Humarr Gateway** (refactor; rename existing chat orchestration)
- 🟢 **Onboarding flow refinement** (Hjarta branching by intent; ember onboard tour)
- 🟢 **Shed Protocol bones** (deprecation warnings; migration framework)
- 🔵 **Pre-commit hooks** + CI discipline

These are *small* changes; *high* operator value. Ship in V0.3
or V0.4.

### Klóinn Phase 2 (Bridges and Voice)

Mid-effort adoptions building on Yggdrasil Phase 4 (federation
+ daemon mode):

- 🟢 **Matrix bridge** (sovereignty-aligned)
- 🟢 **Telegram bridge** (mainstream-but-careful)
- 🟢 **Talk Mode** (push-to-talk voice)
- 🟢 **Voice Wake** (always-listening, opt-in)
- 🟢 **Sandbox backends** (subprocess; Docker opt-in)
- 🟢 **Carapace Defense** (named + documented; tests added)
- 🟡 **Pincer Loop** (opt-in plan-then-execute)
- 🟡 **Skills as pip packages** (entry points; audit tool)

These require *infrastructure* (daemon, voice components,
sandbox abstractions). Ship in V0.5 or V1.0.

### Klóinn Phase 3 (Canvas and Channels)

High-effort adoptions building on Yggdrasil Phase 5
(constellation ratified):

- 🟢 **OdinUI / Live Canvas** (Stofa + web rendering)
- 🟢 **Web companion** (PWA paired via tailnet)
- 🟢 **Deep Water Federation** (resilient multi-device)
- 🟢 **Personas** (opt-in multi-identity)
- 🟢 **Tide Routing** (adaptive cross-node routing)
- 🟢 **Menu Bar Presence** (cross-platform)
- 🟢 **Moult Cycle** (monthly maintenance)
- 🟢 **Claw Negotiation** (operator-AI disagreement)

These are *significant features*. Ship in V1.5 or V2.0.

---

## What's NOT in the roadmap

🔴 **Permanently rejected**:

- Centralized skill registry (we don't run one).
- Cloud-deploy configs in core.
- 23+ channel bridges (we ship strategic 2-3 only).
- Native mobile apps (web companion suffices).
- Always-on daemon default (operator opt-in).
- Cloud TTS as default voice (local only by default).

These conflict with Vows or scope-bust the project.

---

## Why this order

### Phase 1 first

Workspace prompt files + sessions + release channels are
*foundational*. They benefit everything that comes after.
They're cheap.

### Phase 2 needs Phase 1

Voice + bridges need daemon mode. Daemon mode benefits from
Gateway pattern. Gateway pattern is Phase 1.

### Phase 3 needs Phase 2

Canvas needs surfaces. Surfaces are well-defined post-
Phase-2's daemon + voice work.

---

## Cumulative operator experience

### After V1.0 (Phase 1 complete)

Operator gains:
- Personality control via workspace files.
- Bounded conversation sessions.
- Predictable release channels.
- Improved onboarding.

Visible message: "Klóinn V1 — operator empowerment via
workspace prompts + sessions."

### After V2.0 (Phase 2 complete)

Operator gains:
- Talk to Ember via voice (Talk Mode).
- Chat via Matrix or Telegram.
- High-power tools (sandboxed).
- Stronger trust in audit (Pincer Loop).

Visible message: "Klóinn V2 — voice and bridges."

### After V3.0 (Phase 3 complete)

Operator gains:
- Rich UI in responses (Canvas).
- Mobile companion via browser.
- Resilient multi-device on bad networks.
- Multiple personas.

Visible message: "Klóinn V3 — Canvas and Channels;
constellation complete."

---

## Coordination with Yggdrasil

| Yggdrasil Phase | Klóinn Phase |
|---|---|
| Yggdrasil P1 (Roots — memory) | Klóinn P1 (basic adoptions) |
| Yggdrasil P2 (Branches — tone) | Klóinn P1 continues |
| Yggdrasil P3 (Crown — AI capabilities) | Klóinn P1 wraps; P2 prepares |
| Yggdrasil P4 (Network — federation) | Klóinn P2 (bridges + voice) |
| Yggdrasil P5 (Constellation) | Klóinn P3 (Canvas + companion) |

Klóinn lags Yggdrasil by ~1 phase. Each Klóinn phase builds on
the previous Yggdrasil work.

---

## What each phase doesn't promise

Phase 1: doesn't fix all UX gaps (Stofa is V2 too).

Phase 2: voice may have latency on Pi; bridges may have edge
cases.

Phase 3: Canvas may be limited (forms work; complex layouts
later); web companion is browser-only (no native mobile).

Honest scope. Manageable bites.

---

## Risk assessment per phase

### Phase 1 risks

| Risk | Severity | Mitigation |
|---|---|---|
| Operators don't use workspace files | Low | Defaults work; opt-in deeper |
| Session model confusion | Low | Clear CLI commands; docs |
| Channel release discipline burden | Low | Mostly automated |

### Phase 2 risks

| Risk | Severity | Mitigation |
|---|---|---|
| Voice latency on Pi | Med | Honest expectations + workstation offload |
| Bridge maintenance | Med | Limit to 2-3; community contributions for more |
| Sandbox complexity | Med | Layered (Carapace) defense |

### Phase 3 risks

| Risk | Severity | Mitigation |
|---|---|---|
| Canvas spec ambiguity | Med | Pydantic validation strict |
| Web companion security | High | Tailscale only; audit; per-call approval |
| Multi-persona confusion | Med | Persistent visual indicators |

---

## What we re-evaluate per phase

After each phase ships:
- **Operator feedback survey**: what's working, what's not?
- **Audit log analysis**: how are operators using new features?
- **Mirror reports** (per Yggdrasil): what's surfacing as worth
  tuning?
- **Roadmap adjustment**: defer or accelerate based on signal.

This is *adaptive roadmap*. We don't lock in years ahead.

---

## What V4+ might bring

Beyond Phase 3, potential directions:

- **Multi-modal Ember** (vision-language + Canvas integration).
- **Multi-operator federation** (small-team Ember).
- **Native mobile apps** (if operator demand justifies).
- **Voice in non-English** (community-contributed).
- **Domain-specific personas** (research, code-review, etc., as
  templates).
- **Plugin marketplace** (still operator-curated; never centralized).

These are *speculative*. Build if demand. Skip if not.

---

## Total Klóinn adoption scope

Across 3 phases:

- **57 design docs** (this codex; complete).
- **~50 source files** added/modified.
- **~5000-8000 lines of code** (excluding tests).
- **~30-50 pages of operator-facing documentation**.

Spread across V0.3 → V3.0 (roughly 18-24 months total
calendar).

This is *less* than Yggdrasil's adoption scope. Klóinn is
*complementary refinement*, not foundational rebuild.

---

## Closing

The Phase Overview is **Klóinn's adoption sequence**. Three
phases. Each adds operator-visible value. Each builds on
Yggdrasil + previous Klóinn phase.

Cumulative effect: Ember in V3.0 has:
- All of Yggdrasil's deep architecture.
- All of Klóinn's mainstream-AI-assistant ergonomics.
- Sovereignty preserved throughout.

This is the *long-term plan* — informed by OpenClaw,
disciplined by our Vows, paced by what operators justify.

Next docs unpack each phase in detail.
