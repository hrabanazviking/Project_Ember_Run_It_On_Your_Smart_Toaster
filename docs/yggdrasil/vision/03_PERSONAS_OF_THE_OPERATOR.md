# 03 — Personas of the Operator

Yggdrasil serves operators across a wide range of needs and
capacities. This document names **six concrete personas** and
specifies how each is served. (Stofa's design tree names five
personas for the TUI surface; this one extends to the broader
integration scope.)

When a Yggdrasil design choice is hard, run it through these
six. The right answer usually becomes obvious.

---

## Persona 1 — Volmarr the Sovereign-AI Operator

> *"I run my own everything. I want a real AI that lives on my
> hardware. Nothing leaves the machine without my say-so."*

**Background:** Mid-career engineer / philosopher / craftsperson.
Linux at home. Pi cluster + tailnet + Postgres. Suspicious of
cloud AI.

**What Yggdrasil gives them:**
- Full mesh: Pi 5 ingests, desktop chats, laptop reads —
  federated identity, shared Well.
- Composite memory (Bifrǫst) — they can hold both their notes
  AND their public-knowledge corpora simultaneously, weighted
  by their interest patterns (Muninn's Hebbian layer).
- Sovereign by design — Kista holds every credential, never
  in plain `ember.yaml`.

**Volmarr's red line:** any feature that requires a sign-in or
phones home. None of Yggdrasil's components cross it.

---

## Persona 2 — Iðunn the Curious Newcomer

> *"I just installed this thing. I have no idea what's happening
> but the README made me smile."*

**Background:** Student / writer / hobbyist / retiree. May not
have used a terminal much. Friendly README hooked them.

**What Yggdrasil gives them:**
- *Nothing they have to think about by default.* `pip install
  ember-agent[sqlite_vec]` gives them Ember as it is today; no
  Yggdrasil at all.
- When they opt into `[yggdrasil]`, the experience is *richer*
  but the chrome looks the same — better memory, better tone,
  but no new menus to learn.
- The Pet layer's Hugin still perches over citations. Now
  citations might come from Mímir + Huginn + Muninn — but the
  operator just sees "Ember found these." The complexity is
  hidden.

**Iðunn's protection:** Yggdrasil is *opt-in*. They never get
forced complexity.

---

## Persona 3 — Sigrún the Ruthless Power-User

> *"I'm going to read every line. I have opinions. I'm going
> to write three plugins by next week."*

**Background:** Career engineer. Lives in neovim + tmux. Strong
opinions. Will read source.

**What Yggdrasil gives them:**
- A clean realm-Protocol architecture they can extend (each
  realm has a Protocol; new realms slot in without core
  changes).
- The Verdandi event bus — every internal operation is
  observable; they can write tools that subscribe.
- Per-realm pip extras so they can install only what they want
  (`[bifrost]`, `[kista]`, `[verdandi]`, etc.).
- A clear ADR trail (0016+) so they can argue at the design
  level, not just the code level.
- The plugin architecture from Stofa V2 generalizes to
  Yggdrasil: realm plugins, observer plugins, gateway plugins.

**Sigrún's reward:** clean abstractions + actual hackability.

---

## Persona 4 — Védis the Cozy Operator

> *"I work from home. My desk faces a window. Things should
> feel nice."*

**Background:** Cares about aesthetics. Considered choices.
Will pick the prettier option when functionality is equal.

**What Yggdrasil gives them:**
- Tone modulation (Seiðr + Astrology Engine + emotional-
  intelligence layer) means Ember *feels* different at
  different times. Evening replies are warmer; morning replies
  are crisper.
- Hamr (when integrated with Auga, the planned GUI) means
  Ember has a *visible body* — a small parametric VRM
  character. Optional. Cozy.
- Verdandi's "noticing" behavior — Ember sometimes proactively
  says something like "I noticed it's the autumn equinox; would
  you like to revisit your notes on seasonal change?" Operator-
  toggleable.

**Védis's joy:** Ember feels *alive in their home*, not just
running on their hardware.

---

## Persona 5 — Eirwyn the Pi-Class Operator

> *"My machine is a $50 single-board computer. Make it work
> here."*

**Background:** Pi 5, sometimes Pi 4. Minimum spec.

**What Yggdrasil gives them:**
- **Lazy realm loading.** They install only the realms they
  want. Each realm has a low-overhead "off" state.
- **Performance tiers.** The device-capability detection layer
  (`cross-platform/61_PERFORMANCE_TIERS.md`) picks
  Pi-appropriate behaviors at startup: smaller embeddings,
  shorter context windows, no Hamr/Auga, simpler Stofa render.
- **Multi-device federation** *helps* Pi operators: a Pi at
  home can act as the persistent Well + ingest worker; a
  laptop opens Stofa and pulls from the Pi via tailnet.

**Eirwyn's experience:** Yggdrasil isn't bigger than Pi; it
*reaches further than Pi* by federating with other devices.

---

## Persona 6 — Heiðr the Cluster Operator (NEW persona for Yggdrasil)

> *"I have a small cluster. I want Ember to use it
> intelligently."*

**Background:** Has 3-10 devices. Could be Pi cluster + NAS, or
home server + multiple workstations. Wants distributed
behavior.

**What Yggdrasil gives them:**
- **The multi-device federation layer.** A single Ember
  identity can span devices. The Well lives on the strongest
  storage; ingest runs on the device with the most CPU;
  chat opens on whichever device the operator is sitting at.
- **Gossip protocol.** Devices know about each other's state.
  If the Well-host goes down, chat continues with a "Well
  disconnected" banner and gracefully reconnects when it's
  back.
- **Per-device specialization.** A Pi can be the
  "ambient awareness" node (Astrology + Verdandi); a desktop
  can be the "compute" node (Funi); a laptop is the
  "operator surface" (Stofa).

**Heiðr's reward:** Yggdrasil is the only sovereign-AI system
that takes their cluster seriously.

---

## Cross-persona invariants

These hold for *every* persona:

1. **First-launch usability under 60 seconds.** Even with all
   realms installed, the first `ember tui` opens chat that
   works.
2. **`?` always tells you what you can do.** (Inherited from
   Stofa.)
3. **Quit always works.** From any state, on any device.
4. **Operator data never silently leaves the machine.**
5. **Every realm is opt-in via pip extras AND `ember.yaml`.**

---

## What Yggdrasil is NOT for

- **Enterprise admin teams.** Yggdrasil is single-operator (or
  single-operator-with-federated-devices). Multi-operator
  admin tooling is a separate problem.
- **AI-for-end-users-of-the-operator's-app.** Ember is the
  operator's companion, not a back-end service for their
  customers. Operators who want to *resell* Ember-powered
  service look at Bifröst-the-HTTP-gateway (slice-3, separate
  from this plan).
- **A general-purpose distributed-systems framework.** The
  multi-device federation is *narrow* — it serves Ember's
  specific use case, not arbitrary workloads.

---

## How personas interact with Yggdrasil's phases

| Phase | Volmarr | Iðunn | Sigrún | Védis | Eirwyn | Heiðr |
|---|---|---|---|---|---|---|
| 1 (Bifrǫst wiring) | ✅ direct value | invisible | ✅ extension target | invisible | ✅ enables federation | ✅ |
| 2 (Kista + Mímir) | ✅ sovereign secrets | invisible | ✅ | tone improves | ✅ small footprint | ✅ |
| 3 (Advanced AI) | tone awareness | tone awareness | ✅ plugin target | ✅ huge | acceptable | ✅ |
| 4 (Multi-device) | ✅ huge | invisible | ✅ huge | nice-to-have | ✅ huge | ✅ huge |
| 5 (Ratification) | celebrates | celebrates | celebrates | celebrates | celebrates | celebrates |

Every phase serves multiple personas. None is single-use.

---

## Closing

Six personas. Each protected. None forced into complexity. None
locked out of capability. Yggdrasil's surface is wider than
Ember's, but the *contract with the operator* is the same:
**this is your software, on your machine, serving you.**
