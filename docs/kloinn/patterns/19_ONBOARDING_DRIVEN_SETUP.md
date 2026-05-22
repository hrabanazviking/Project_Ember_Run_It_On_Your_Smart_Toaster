# 19 — Onboarding-Driven Setup

OpenClaw's pattern: interactive setup that *teaches* operators
as it *configures*.

---

## The pattern

When operator first runs OpenClaw:

```bash
openclaw setup
```

…the wizard:

1. Asks about the operator's intent ("for personal use? team
   use?").
2. Helps them pick a model provider.
3. Configures basic preferences.
4. Optionally enables bundled skills.
5. Optionally pairs companion app.
6. Optionally configures bridges.

Each step *explains* what it does, why it matters, and lets
the operator skip or revisit.

After setup: `openclaw onboard` runs a guided tour of features.

---

## Why this works

### 1. Reduces "I have no idea what to do"

New operators face a complex system. Without onboarding, they
flounder, give up.

With onboarding: 5-10 minutes of guided setup; they're using
the system productively immediately.

### 2. Teaches as it configures

Each setup question is a *learning moment*. "Voice wake on?
Here's what it does. Off by default; you can enable later."

Operator finishes setup understanding what's possible, not just
what's configured.

### 3. Reduces post-setup support burden

Many "how do I…" questions are addressed during setup. Documentation
becomes a reference, not a tutorial.

### 4. Catches misconfigurations early

The wizard validates. "You picked model X but it's not
installed. Want me to fetch it?"

---

## OpenClaw's setup flow (extrapolated)

```
openclaw setup

Welcome to OpenClaw! Let's get you set up.

[1/8] What's your name?
  > Volmarr

[2/8] What kind of assistant do you want?
  ▶ personal — for daily use
    work — for professional tasks
    research — for deep exploration
    custom — define your own
  > personal

[3/8] Which model provider?
  ▶ anthropic — Claude (cloud, recommended)
    openai — GPT (cloud)
    ollama — local models on this machine
    custom
  > ollama

[4/8] Which local model? (detected: llama3.2:3b, phi3:mini)
  ▶ llama3.2:3b — small, fast, multilingual
    phi3:mini — even smaller, faster
  > llama3.2:3b

[5/8] Voice features?
  Voice wake (always listening): off / on
  Talk mode (push-to-talk): off / on
  > off / on

[6/8] Bundled skills to enable?
  ☑ search_web
  ☐ file_operations
  ☐ cron_scheduler
  ☑ code_review
  > done

[7/8] Daemon mode? (recommended for voice / async features)
  ▶ no — start fresh each time
    yes — install as system service
  > no

[8/8] Confirm and write configuration.
  Save to ~/.openclaw/openclaw.json? [Y/n]
  > Y

Setup complete!

Run `openclaw onboard` for a guided feature tour.
Or `openclaw` to start chatting.
```

8 steps. ~5 minutes. Operator ready to go.

---

## What Ember has today

Ember's setup is currently a single command:

```bash
ember setup
```

…which Hjarta (the first-run wizard) handles. It already does
some of this — asks operator name, configures backends, etc.

But: it's *less guided* than OpenClaw's wizard. Fewer
explanatory moments. Less "would you like X?" branching.

---

## What Ember should adopt

🔵 **Borrow as-is**:

### 1. Multi-step wizard with explanations

Each step:
- Stated purpose (what does this configure?).
- Default highlighted (▶).
- Options listed clearly.
- "Skip" available.

Hjarta is close to this; we can refine.

### 2. Branching by use case

OpenClaw asks "personal / work / research / custom" — the
wizard branches based on intent.

Ember could do this: ask the operator's intent (companion / data
analysis / writing assistance / Norse cosmology study) and tune
defaults accordingly.

### 3. Detection + suggestion

Wizard detects installed dependencies (Ollama, Postgres,
Tailscale) and *suggests* using them.

Hjarta already does this for Ollama. Could expand for Postgres,
sqlite_vec, etc.

### 4. Guided tour post-setup

`ember onboard` (new command) walks through:
- "Here's how to ingest your first document."
- "Here's how to ask Ember a question."
- "Here's how to use a tool."
- "Here's the Doctor screen."
- "Here's where to find help."

5-10 minutes; operator gets practical fluency.

---

## What we should NOT do

🔴 **Reject**:

### 1. Asking for cloud-API keys upfront

OpenClaw might ask for Anthropic API key during setup. Ember
should default to *local Ollama* unless operator has Ollama
unavailable — then suggest local installation rather than
cloud.

### 2. Over-asking

A 20-step wizard exhausts operators. 5-8 steps for setup; 5-10
minutes for onboard; that's the limit.

### 3. "Cloud sync your config" prompts

We don't sync; we don't phone home. The wizard never
suggests these.

---

## Branching the wizard

🟢 **Adapt to Ember Vows**:

A useful pattern: ask intent early, branch the rest.

```
[1/6] What brings you to Ember?
  ▶ A — daily AI companion (general use)
    B — Norse cosmology research
    C — data analysis (ingest + query)
    D — writing assistance
    E — Pi-class hobbyist
    F — custom path

> A

[2/6] (For daily companion)
  Which surface do you want as primary?
    munnr — terminal CLI
  ▶ stofa — TUI (Phase 2+)
    auga — GUI (Phase 5+)

> stofa
```

The wizard *adapts* to the operator's stated path.

For E (Pi-class hobbyist), the wizard would skip workstation-only
features. For B (Norse cosmology), it might pre-load relevant
prompt fragments.

---

## Onboarding-after-update

OpenClaw also has an onboarding flow *after major updates* —
"these new features landed; want to learn about them?"

Ember should do this too:
- `ember upgrade` runs pip install + post-update tour.
- Tour mentions: new tools, new config options, deprecations.

This is *invaluable* for keeping operators current as the
project evolves.

---

## Configuration shape

```yaml
ember:
  onboarding:
    enabled: true                   # part of setup flow
    intent_branch: true             # ask intent + branch
    skill_suggestions: true         # offer skills during setup
    post_setup_tour: true           # offer guided tour
    upgrade_tour: true              # tour on major upgrade
    max_steps: 10                   # don't exceed
```

---

## A note on Hjarta

Hjarta is Ember's first-run wizard (per the Six True Names).
The Klóinn lessons apply directly to Hjarta:

- Make Hjarta *more* explanatory.
- Make Hjarta *branch by intent*.
- Add a post-Hjarta `ember onboard` tour.
- Make Hjarta detect environment + suggest.
- Make Hjarta *re-runnable* if operator wants to revisit.

Hjarta is one of Ember's most important UX surfaces. The
Klóinn-informed refinement is in Phase 2.

---

## What about already-installed operators

For operators who already set up Ember in earlier versions:

- `ember onboard` should work for them too — tour newer
  features.
- Optional `ember reconfigure` re-runs the wizard with their
  existing config as starting point.

---

## Closing

Onboarding-Driven Setup is **OpenClaw's UX investment in
operator success**. The first 5-10 minutes determine whether the
operator becomes productive or abandons.

Ember should:
- 🔵 Borrow the multi-step wizard with explanations.
- 🟢 Adapt: branch by operator intent.
- 🟢 Add `ember onboard` post-setup tour.
- 🟢 Add `ember upgrade` post-upgrade tour.
- 🔴 Reject: cloud-key prompts, over-asking, telemetry.

The Klóinn lesson: **good onboarding compounds**. Every operator
who finishes setup productively is one less support burden + one
more potential long-term operator.

Invest in Hjarta. It's worth it.
