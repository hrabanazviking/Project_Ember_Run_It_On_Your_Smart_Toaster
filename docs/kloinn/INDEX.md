# Klóinn Codex — INDEX

> *Klóinn (KLOH-in) — Old Norse for "the Clawed One." The lobster
> mascot Molty has claws; the Norse word holds the form. This codex is
> what Ember learns by studying the Clawed One.*

---

## Overview

The **Klóinn Codex** is a research + design tree analyzing
[**OpenClaw**](https://github.com/openclaw/openclaw) — the
373k-star personal AI assistant project ("Your own personal AI
assistant. Any OS. Any Platform. The lobster way.") — and extracting
what Ember should learn, borrow, adapt, and deliberately *not* do.

OpenClaw is Ember's most direct peer in the sovereign-AI-assistant
space. They reached mass adoption (373k stars) while Ember is
deliberately small. They picked TypeScript/Node; we picked Python.
They built for 23+ messaging channels; we built for the terminal.
They ship companion mobile apps; we ship Pi-class hardware support.

There is enormous to learn from a project that succeeded at the
problem we are solving — *without* abandoning the Vows that make
Ember worth building.

This codex is **57 documents** in eight sections.

---

## Why this codex exists

When two projects share a goal and pick different paths, the right
move isn't to ignore the other — it's to *study* it. Specifically:

- **What did OpenClaw get right** that Ember should borrow?
- **What did OpenClaw choose differently** that doesn't fit our Vows?
- **What did OpenClaw invent** that the field will copy?
- **What can we cross-pollinate** to make Ember stronger?

This codex answers those four questions in deep detail. It's grounded
in the actual OpenClaw repo (README, architecture, design docs) as
of 2026-05-21.

---

## Codex structure

| Section | Purpose | Docs |
|---|---|---|
| **research/** | What OpenClaw actually is, factually | 8 |
| **patterns/** | Architectural patterns extracted | 12 |
| **lessons/** | Where Ember should agree, disagree, depart | 8 |
| **applications/** | How each pattern applies to a specific Ember subsystem | 12 |
| **invented-methods/** | New methods born of the cross-pollination | 8 |
| **integrations/** | Concrete things to add to Ember | 4 |
| **roadmap/** | Phased adoption plan | 4 |
| **INDEX** | This file | 1 |

Total: **57 documents**.

---

## The grand thesis

> *OpenClaw shows that a sovereign AI assistant CAN reach mass
> adoption. They did it by abundance: 23+ messaging channels, voice
> wake, mobile companions, mainstream-friendly UX. Ember chooses the
> opposite path: scarcity-by-design, sovereignty-by-default, the
> terminal as primary surface. But there are technical patterns
> OpenClaw uses that we should borrow — and **disagreements with our
> own design** that the comparison sharpens.*

The codex's thesis in one breath:

> *Borrow the Gateway architecture. Borrow the Sandbox abstraction.
> Borrow Voice Wake. Borrow the Workspace prompt-injection files.
> Reject the cloud-deployment surfaces. Reject the centralized
> registry. Reject the proliferation of channels. Keep the Vows.
> Make Ember a better version of itself — informed by OpenClaw,
> not imitating it.*

---

## How to use this codex

**As a contributor**: read [`research/`](research/) first; then jump
to whichever section serves your current work. Each doc is
self-contained.

**As an operator**: skim [`research/00_WHAT_IS_OPENCLAW.md`](research/00_WHAT_IS_OPENCLAW.md) for context;
then read [`applications/`](applications/) for the changes you might
see in Ember V2-V5.

**As Volmarr**: this codex is a *ratification document*. Each
proposal is marked with a recommendation; you decide which to apply.

---

## Sections

### research/ — what OpenClaw actually is

- [`00_WHAT_IS_OPENCLAW.md`](research/00_WHAT_IS_OPENCLAW.md) — the project at a glance
- [`01_MOLTY_THE_LOBSTER.md`](research/01_MOLTY_THE_LOBSTER.md) — the mascot, the mythology
- [`02_THE_GATEWAY_ARCHITECTURE.md`](research/02_THE_GATEWAY_ARCHITECTURE.md) — the local-first gateway
- [`03_MULTI_AGENT_ROUTING.md`](research/03_MULTI_AGENT_ROUTING.md) — workspaces per agent
- [`04_TECHNOLOGY_STACK.md`](research/04_TECHNOLOGY_STACK.md) — TypeScript, pnpm, Node
- [`05_TOOL_ECOSYSTEM.md`](research/05_TOOL_ECOSYSTEM.md) — browser, canvas, nodes, cron
- [`06_DEPLOYMENT_AND_DEVELOPMENT.md`](research/06_DEPLOYMENT_AND_DEVELOPMENT.md) — Fly.io, Docker, channels
- [`07_PROJECT_HEALTH_AND_SCALE.md`](research/07_PROJECT_HEALTH_AND_SCALE.md) — 373k stars, what it means

### patterns/ — what to extract

- [`10_LOCAL_FIRST_GATEWAY.md`](patterns/10_LOCAL_FIRST_GATEWAY.md)
- [`11_MULTI_AGENT_WORKSPACES.md`](patterns/11_MULTI_AGENT_WORKSPACES.md)
- [`12_PROMPT_INJECTION_FILES.md`](patterns/12_PROMPT_INJECTION_FILES.md)
- [`13_SANDBOX_BACKEND_ABSTRACTION.md`](patterns/13_SANDBOX_BACKEND_ABSTRACTION.md)
- [`14_VOICE_WAKE_AND_TALK_MODE.md`](patterns/14_VOICE_WAKE_AND_TALK_MODE.md)
- [`15_LIVE_CANVAS_A2UI.md`](patterns/15_LIVE_CANVAS_A2UI.md)
- [`16_MULTI_CHANNEL_MESSAGING.md`](patterns/16_MULTI_CHANNEL_MESSAGING.md)
- [`17_COMPANION_APP_PAIRING.md`](patterns/17_COMPANION_APP_PAIRING.md)
- [`18_SKILL_REGISTRY_AND_BUNDLES.md`](patterns/18_SKILL_REGISTRY_AND_BUNDLES.md)
- [`19_ONBOARDING_DRIVEN_SETUP.md`](patterns/19_ONBOARDING_DRIVEN_SETUP.md)
- [`20_DEVELOPMENT_CHANNELS.md`](patterns/20_DEVELOPMENT_CHANNELS.md)
- [`21_PER_AGENT_SESSION_HISTORY.md`](patterns/21_PER_AGENT_SESSION_HISTORY.md)

### lessons/ — where to depart

- [`30_THE_DIVERGENCE_OF_PHILOSOPHIES.md`](lessons/30_THE_DIVERGENCE_OF_PHILOSOPHIES.md)
- [`31_WHEN_TO_DEPART_FROM_OPENCLAW.md`](lessons/31_WHEN_TO_DEPART_FROM_OPENCLAW.md)
- [`32_THE_PRICE_OF_POPULARITY.md`](lessons/32_THE_PRICE_OF_POPULARITY.md)
- [`33_TYPESCRIPT_VS_PYTHON_TRADEOFFS.md`](lessons/33_TYPESCRIPT_VS_PYTHON_TRADEOFFS.md)
- [`34_THE_SANDBOX_QUESTION.md`](lessons/34_THE_SANDBOX_QUESTION.md)
- [`35_THE_VOICE_QUESTION.md`](lessons/35_THE_VOICE_QUESTION.md)
- [`36_THE_CHANNEL_PROLIFERATION_QUESTION.md`](lessons/36_THE_CHANNEL_PROLIFERATION_QUESTION.md)
- [`37_THE_MOBILE_QUESTION.md`](lessons/37_THE_MOBILE_QUESTION.md)

### applications/ — concrete Ember uses

- [`40_BRIDGES_TO_MESSAGING_CHANNELS.md`](applications/40_BRIDGES_TO_MESSAGING_CHANNELS.md)
- [`41_VOICE_WAKE_FOR_RODD.md`](applications/41_VOICE_WAKE_FOR_RODD.md)
- [`42_LIVE_CANVAS_FOR_AUGA.md`](applications/42_LIVE_CANVAS_FOR_AUGA.md)
- [`43_SANDBOXING_LAYER_FOR_TOOLS.md`](applications/43_SANDBOXING_LAYER_FOR_TOOLS.md)
- [`44_MULTI_AGENT_FOR_EMBER_PERSONAS.md`](applications/44_MULTI_AGENT_FOR_EMBER_PERSONAS.md)
- [`45_WORKSPACE_PROMPT_FILES.md`](applications/45_WORKSPACE_PROMPT_FILES.md)
- [`46_SKILL_BUNDLES_FOR_OPERATORS.md`](applications/46_SKILL_BUNDLES_FOR_OPERATORS.md)
- [`47_ONBOARDING_FLOW_REFINEMENT.md`](applications/47_ONBOARDING_FLOW_REFINEMENT.md)
- [`48_DEVELOPMENT_CHANNELS_FOR_EMBER.md`](applications/48_DEVELOPMENT_CHANNELS_FOR_EMBER.md)
- [`49_COMPANION_APP_PAIRING_DESIGN.md`](applications/49_COMPANION_APP_PAIRING_DESIGN.md)
- [`50_DOCKER_DEFAULT_SANDBOX_FOR_LARGE_PROFILES.md`](applications/50_DOCKER_DEFAULT_SANDBOX_FOR_LARGE_PROFILES.md)
- [`51_MENU_BAR_PRESENCE.md`](applications/51_MENU_BAR_PRESENCE.md)

### invented-methods/ — new methods born of comparison

- [`60_THE_HUMARR_GATEWAY.md`](invented-methods/60_THE_HUMARR_GATEWAY.md)
- [`61_THE_SHED_PROTOCOL.md`](invented-methods/61_THE_SHED_PROTOCOL.md)
- [`62_THE_PINCER_LOOP.md`](invented-methods/62_THE_PINCER_LOOP.md)
- [`63_THE_TIDE_ROUTING.md`](invented-methods/63_THE_TIDE_ROUTING.md)
- [`64_THE_MOULT_CYCLE.md`](invented-methods/64_THE_MOULT_CYCLE.md)
- [`65_THE_CLAW_NEGOTIATION.md`](invented-methods/65_THE_CLAW_NEGOTIATION.md)
- [`66_THE_DEEP_WATER_FEDERATION.md`](invented-methods/66_THE_DEEP_WATER_FEDERATION.md)
- [`67_THE_CARAPACE_DEFENSE.md`](invented-methods/67_THE_CARAPACE_DEFENSE.md)

### integrations/ — what to add to Ember

- [`70_ADDING_VOICE_WAKE.md`](integrations/70_ADDING_VOICE_WAKE.md)
- [`71_ADDING_TELEGRAM_BRIDGE.md`](integrations/71_ADDING_TELEGRAM_BRIDGE.md)
- [`72_ADDING_SANDBOX_BACKEND.md`](integrations/72_ADDING_SANDBOX_BACKEND.md)
- [`73_ADDING_LIVE_CANVAS.md`](integrations/73_ADDING_LIVE_CANVAS.md)

### roadmap/ — phases

- [`80_PHASE_OVERVIEW.md`](roadmap/80_PHASE_OVERVIEW.md)
- [`81_PHASE_1_OBSERVE_AND_BORROW.md`](roadmap/81_PHASE_1_OBSERVE_AND_BORROW.md)
- [`82_PHASE_2_BRIDGES_AND_VOICE.md`](roadmap/82_PHASE_2_BRIDGES_AND_VOICE.md)
- [`83_PHASE_3_CANVAS_AND_CHANNELS.md`](roadmap/83_PHASE_3_CANVAS_AND_CHANNELS.md)

---

## Status

**Design-only.** No source code changes. All 57 documents are
research + proposal. Each proposal labeled with a recommendation:

- 🔵 **Borrow as-is** — pattern translates directly.
- 🟢 **Adapt to Ember Vows** — pattern works with modifications.
- 🟡 **Defer** — interesting but not yet.
- 🔴 **Reject** — incompatible with Vows / cost > value.

The codex must pass operator-ratification before any of its
proposals become source-code work. Same ratification gate as
Yggdrasil.

---

## Related design trees

- **Yggdrasil** ([`../yggdrasil/`](../yggdrasil/)) — the integration
  plan for all sibling projects.
- **Stofa** ([`../tui/`](../tui/)) — the TUI surface design.
- **Klóinn** (this tree) — what we learn from OpenClaw.

Together: 197 design documents across three trees. Ember is a
*deeply considered* project.

---

## A closing word

OpenClaw is a *legitimate, well-built, popular* peer in our space.
Studying it is not betrayal of our path — it's stewardship of our
craft.

The lobster has claws; we have hands of our own. We learn from his
grip; we use ours differently.

— *the Skald, in her quiet authority*
