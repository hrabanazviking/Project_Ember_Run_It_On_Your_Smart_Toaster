# 47 — Onboarding Flow Refinement

How to refine Hjarta + add `ember onboard` — adopting OpenClaw's
onboarding patterns.

---

## What we have

Hjarta (the first-run wizard) currently:
- Asks operator name.
- Detects Ollama, suggests model.
- Optionally configures Brunnr backend.
- Writes `ember.yaml`.

Solid baseline. Klóinn refines this.

---

## What we add

🔵 **Phase 2 of Klóinn adoption**.

### 1. Branch by intent (early in wizard)

```
[1/8] What brings you to Ember?

  ▶ A — daily AI companion (general use)
    B — Norse cosmology research
    C — data analysis (ingest + query)
    D — writing assistance
    E — Pi-class hobbyist (low-power device)
    F — Yggdrasil power user (all features)
    G — custom path

> A
```

Subsequent steps tune defaults based on choice. E.g., E
suggests TINY/SMALL profile defaults; F suggests LARGE+
with all opt-ins.

### 2. Explain each setting

```
[3/8] Voice support? (Phase 5 feature; planned)

  Voice will let you talk to Ember instead of typing.
  Requires installing Rödd sibling (~150MB for Whisper +
  Piper).
  
  ▶ Off — text only (default for V1-V4)
    Plan for — set up but disable; enable later

> Off
```

Each prompt has context. Operator understands the trade-off.

### 3. Detect + suggest

```
[5/8] Detected:
  ✓ Ollama at 100.67.240.22:11434 (tailnet)
  ✓ Postgres at 100.67.240.22:5432 (Gungnir; pgvector enabled)
  ✓ Tailscale active
  ✗ Docker not installed

Configure pgvector as Brunnr backend (recommended for
your detected setup)? [y/n]: y
```

Wizard *uses* the environment intelligently.

### 4. Skill suggestions (when skills land)

```
[7/8] Skill bundles to install? (none required)

  Browse curated list at:
  https://github.com/.../community-skills

  Or skip for now; install later via:
  pip install ember-skill-<name>

> skip
```

Doesn't auto-install. Operator browses + chooses.

### 5. Verify + write

```
[8/8] Configuration summary:

  Operator: Volmarr
  Identity: ember-of-volmarr
  Funi: ollama @ tailnet llama3.2:3b
  Brunnr: pgvector (Gungnir; read_only)
  Workspace: ~/.ember/workspace/
  Sessions: enabled
  
  Save to ~/.ember/config/ember.yaml? [Y/n]: Y

Configuration written.

Run `ember onboard` for a guided feature tour.
Run `ember chat` to start chatting.
```

---

## `ember onboard` — the guided tour

After Hjarta finishes, operator can run:

```bash
ember onboard

Welcome to Ember. Let me walk you through the basics.

[1/8] Chatting

  Run `ember chat` to start a conversation. Type freely;
  press Enter to send. Ctrl-C to exit.
  
  Try it now? [y/n]: y

  (opens ember chat)
  
  ... after operator chats briefly ...

[2/8] Ingesting documents

  Add knowledge to your Well with:
  
    ember well ingest /path/to/notes/
  
  Ember will chunk + index. Future chats can reference.
  
  Try it now? [y/n]:

[3/8] Tools

  Ember has tools: search_well (always-on), read_local_file
  (per-call approval), fetch_url (per-call approval).
  
  To enable tools in chat:
  
    ember --allow-tools chat
  
  Try it? [y/n]:

[4/8] Sessions
  ...
[5/8] Personas (Phase 4+)
  ...
[6/8] Workspace files
  ...
[7/8] Doctor screen
  ...
[8/8] Help + documentation
  
  Documentation: docs/ in the repo
  CLI help: ember --help
  Operator playbook: docs/OPERATOR_PLAYBOOK.md
  
  You're set up. Enjoy.
```

8 stops; ~10 minutes; operator gets practical fluency.

---

## Re-running setup

Operators occasionally want to reconfigure. Add:

```bash
ember setup --reconfigure

This will re-run the setup wizard. Your existing config
(at ~/.ember/config/ember.yaml) will be used as the
starting point. Continue? [y/n]: y

[1/8] What brings you to Ember? (current: A)

  Press Enter to keep current; or choose new:

> [Enter]   # keeps "A"
```

Wizard remembers previous answers; operator can change or
keep each.

---

## Post-upgrade tour

After a major upgrade:

```bash
ember upgrade    # actually: pip install -U ember-agent + this

V2 → V3 upgrade complete.

New in V3:
  - Personas (multi-identity within one Ember)
  - Bridge support (Matrix, Telegram opt-in)
  - Improved memory composition (Trinity Fusion)
  
Run `ember onboard --new-features` for a tour. [Y/n]: Y

[1/3] Personas
  
  V3 adds personas — separate identities sharing one Ember.
  ...

(continues for each new feature)
```

Operators stay current as features land. No "I had no idea
that existed" moments.

---

## Migration prompts

Some changes require operator action:

```bash
ember upgrade

V3 introduces personas. Your current single-identity
config can be migrated to a "main" persona automatically.

Migrate now? (recommended)
  ▶ yes — migrate; rest works as before
    no — keep legacy single-identity; can migrate later

> yes
```

Always offers, never forces.

---

## Stofa onboarding (separate)

When Stofa launches for the first time, it has its own brief
onboarding:

```
Welcome to Stofa.

Here's the layout:
  - Left panel: Episode browser
  - Center: Chat area
  - Right: Tools / Doctor / Workspace
  - Bottom: Status bar
  - Top: Command palette (Ctrl-P)

Press Ctrl-? for keyboard shortcuts.
Press F1 for context help.

Press any key to begin.
```

Stofa onboarding focuses on UI navigation; CLI onboarding
focuses on commands. They complement.

---

## What we tell operators that have prior AI-assistant experience

Many operators come from OpenClaw, Claude, ChatGPT, etc.

Tailored explanation:

```
[1/8] You're familiar with Ember-shaped AI assistants?

  ▶ A — yes; mostly the same. Skip ahead.
    B — yes but different stack; brief differences.
    C — no; full tutorial please.

> A

Quick note: Ember differs from common AI assistants in:
  - Sovereignty-first (no cloud).
  - Norse cosmology vocabulary (Mímir, Bifrǫst, etc.).
  - Pi-class friendly defaults.
  
Otherwise: chat works similarly. Press any key.
```

---

## What we tell operators new to AI assistants

```
[1/8] You're new to AI assistants? Welcome.

  AI assistants like Ember help you with:
  - Writing (drafts, edits, summaries).
  - Reading (summarize documents, find information).
  - Thinking (organize ideas, weigh options).
  - Memory (notes that you can recall later).
  
  Ember is *sovereign* — runs on your hardware; your data
  stays here.
  
  Press any key to continue setup.
```

---

## Configuration shape

```yaml
ember:
  onboarding:
    intent_branch: true
    explain_each_step: true
    detect_environment: true
    show_summary_before_save: true
    
    post_setup_tour: true
    tour_stops: 8
    
    on_upgrade:
      run_new_features_tour: true
```

---

## Documentation for onboarding

`docs/ONBOARDING.md` covers:
- What setup does.
- What `onboard` does.
- How to re-run.
- How to recover from misconfiguration.
- How to invite a colleague (sharing setup output).

This *complements* the wizard; doesn't replace it.

---

## What about non-interactive setup

For Pi-class operators setting up via SSH script:

```bash
ember setup --non-interactive \
  --operator-name "Volmarr" \
  --intent A \
  --funi-backend ollama \
  --brunnr-backend sqlite_vec \
  --skip-tour
```

Same wizard logic; CLI args instead of prompts. Useful for
provisioning.

---

## Closing

Onboarding Flow Refinement is **early Phase 2 Klóinn adoption**.

Refinements:
- Branch Hjarta by operator intent.
- Detect + use environment.
- Explain each setting.
- Add `ember onboard` post-setup tour.
- Add new-features tour after upgrades.
- Stofa has its own brief UI onboarding.

These are *small refinements* to existing Hjarta. Big UX
impact.

Onboarding is **the first impression**. The Klóinn lesson:
invest in it. Every well-onboarded operator is one more
long-term Ember user.
