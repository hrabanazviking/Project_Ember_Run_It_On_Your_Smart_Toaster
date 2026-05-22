# 04 — The Siblings as a Family

Eleven sibling projects — most Norse-named, all converging on
the same operator's vision — already exist in the monorepo.
This document maps how they relate as a *family*, not just as
isolated repositories.

---

## The family portrait

```
                            Ember (Asgard / Spark)
                            ────────────────────
                          The agent at the world-tree's base

                                     │
                  ┌──────────────────┼──────────────────┐
                  │                  │                  │
              Bifrǫst            Verðandi             Stofa
            (Rainbow Bridge)   (Norn of Now)         (TUI)
            ────────────       ────────────        ────────────
            Memory composer    Event bus             Operator
            Mímir + Huginn +   Self-awareness        surface
            Muninn             via Unix sockets
                  │                                     │
        ┌─────────┼─────────┐                     ┌────┴────┐
        │         │         │                     │         │
    Mímir's   Huginn    Muninn                 Auga      Rödd
    Well      (Qdrant)  (Hebbian)            (GUI; later) (voice; later)
    ────────  ────────  ────────                ────────  ────────
    Structured Semantic  Associative
    + decay
        │
   (Hamr provides
    avatars for Auga)
                                                                
        Kista                Seiðr                CloakBrowser
       (Niflheim)          (Vanaheim)              (Útgarðr)
       ─────────           ──────────              ──────────
       Encrypted           Old Norse               Stealth web
       secrets             poetry +                access
                           mood-channel
                                                                
        astrology-engine               MemPalace
        (Muspelheim)                   (Helheim)
        ────────────                   ────────────
        Ephemeris +                    Local-first
        temporal awareness             verbatim memory
                                       (alt to Mímir)
                                                                
                          norse-dict
                          (Yggdrasil's hoard)
                          ──────────────────
                          Lexicon corpus
                          (data, not service)
```

Each sibling is **a real Python (or Next.js) project** with its
own life. Each has its own README, pyproject, tests. Yggdrasil
is the *thin glue* in `src/ember/yggdrasil/` that lets Ember
call into them.

---

## How they relate

### Memory family

The most tightly-knit cluster:

- **mimir-well** (mímir-well) — persistent SQLite + FTS5, with
  Ebbinghaus decay and contradiction detection.
- **bifrost** (the Bridge) — composes Mímir + Huginn (Qdrant
  vectors) + Muninn (Hebbian associations) into a unified
  memory interface.
- **MemPalace** — independent local-first verbatim memory
  system (96.6% R@5 on LongMemEval). Operator picks: use Mímir
  + Bifrǫst, OR use MemPalace, OR use both as parallel Wells
  composed by Bifrǫst.

They share a *shape* (key-value-plus-search-plus-decay) but
differ in *philosophy*:
- Mímir + Bifrǫst: composable, multi-backend, decay-curve-
  driven.
- MemPalace: verbatim-storage, single-backend, recall-quality-
  driven.

Both are first-class options. The operator picks per use case.

### Self-awareness family

- **Verdandi** (the present-Norn) — Unix Domain Socket event
  bus + real-time observation of agent state. Other agents
  subscribe; agents publish their own events.
- **Ember-as-publisher** — Yggdrasil-Phase-3 wires Ember's
  internal events (chat turn started, retrieval returned, tool
  approved, etc.) into Verdandi.
- **Ember-as-subscriber** — Ember can listen to her own
  recent events to build self-aware behaviors (see
  `ai-capabilities/40_SELF_AWARENESS_LAYER.md`).

Verdandi's design is *framework-agnostic* — it's not Ember-
specific. The integration is bidirectional but lightweight.

### Creative + temporal family

- **Seiðr Engine** — deterministic Old Norse poetry generator.
  Used in Yggdrasil as a *mood-channel*: when a chat turn
  triggers introspective register, Seiðr can be queried to
  generate a fragment of verse used in the response (when
  appropriate).
- **Astrology Engine** — Swiss Ephemeris-grade temporal
  data. Used as a *rhythm-channel*: time-of-day, lunar phase,
  season subtly shift Ember's tone.

Both are pure-functional: input → output, no side effects, no
state. They feed the emotional-intelligence layer.

### Trust + boundary family

- **Kista** — encrypted vault. Holds secrets for every other
  realm (database passwords, API tokens, SSH keys). The
  gatekeeper.
- **CloakBrowser** — stealth web access. The *outward-facing*
  boundary: when Ember needs to reach the internet, Kista
  provides the credentials, CloakBrowser executes the fetch.

Together: every cross-trust-boundary action flows through
Kista → CloakBrowser (or other web tool).

### Embodiment family (Phase-3+)

- **Hamr** — parametric VRM avatars. When Auga (the planned
  GUI surface) ships, Hamr generates the character that
  appears as Ember's body.

Hamr is *visual embodiment* — separate from Ember's *agent
identity* (which lives in `~/.ember/identity.json`). Multiple
operators could share Ember-the-agent but have different
Hamr-shaped avatars; or one operator could swap avatars over
time without losing identity.

### Corpus family

- **norse-dict** (Cleasby-Vigfusson Old Norse Dictionary) —
  the lexicon corpus. Available for ingestion into Mímir's
  Well as a knowledge base. Powers Seiðr's vocabulary. Could
  fuel a future "translate" tool.
- **Open-VTT** — *not part of Yggdrasil*. Tabletop tool with
  its own purpose; kept in the monorepo for archival reasons.

---

## How the family stays sovereign

A core design principle (per
[`02_PHILOSOPHY_OF_THE_NORSE_AI.md`](02_PHILOSOPHY_OF_THE_NORSE_AI.md)):
**realms stay sovereign within sovereignty**.

That means:

- Each sibling project keeps its own version. Yggdrasil pins to
  a range, not a single version. A sibling's bugfix release
  flows in automatically.
- Each sibling's tests pass independently. We don't fork them
  into Ember.
- Each sibling's docs live in its own README. We link, we
  don't duplicate.
- A sibling can be removed from Yggdrasil if it diverges. The
  Yggdrasil adapter degrades gracefully (the realm reports
  "unavailable").

This is the same Vow as Brunnr (pluggable storage); applied to
siblings.

---

## Tension among siblings

Honest about the friction points:

### MemPalace vs Mímir's Well

Both are local-first memory systems. They overlap in
functionality but differ in approach. Operators choose; we don't
pretend they're complementary if they're not.

**Resolution:** Bifrǫst can compose either or both. Per-Well
queries route to one; cross-Well queries fold results from
each. The operator decides which is the primary.

### Verdandi vs Audit Log

Verdandi is an event bus; the Ember audit log is a per-call
record. Some overlap in what they capture (tool calls).

**Resolution:** Audit log remains canonical for *security-
relevant* events (every tool call, no exceptions). Verdandi
captures *operational* events (state changes, retrievals,
warnings) — broader, less strict. Audit log is for forensics;
Verdandi is for awareness.

### Seiðr's poetry generator vs Funi's chat

Both produce text. Different inputs (Seiðr: structural
constraints + lexicon; Funi: LLM + prompt). Different outputs
(Seiðr: strict-meter verse; Funi: free-form).

**Resolution:** Seiðr is a *tool* Funi can call, not a
replacement for Funi. When Ember decides a poetic flourish fits
the moment, she invokes Seiðr. The choice of *when* is
Funi's; the *what* is Seiðr's.

### Hamr vs the static logo

Hamr produces 3D characters; Stofa has a static "Ember-ember"
logo glyph.

**Resolution:** They don't conflict; they're different
surfaces. Stofa is text-mode (logo glyph). Auga is GUI (Hamr
avatar). The operator might run both.

---

## What's NOT in the family

Sibling projects in the monorepo that are **not part of
Yggdrasil**:

- **Open-VTT** — tabletop tool, unrelated.
- **cleasby-vigfusson-old-norse-dict** — corpus, not service.
  We *use* its data; we don't run it.

These remain in the repo as the operator's other projects, not
as Yggdrasil components.

---

## Family rituals (engineering practices)

Things that make the family coherent over time:

- **Shared release notes.** When an Yggdrasil release ships,
  the DEVLOG mentions which sibling versions it tests against.
- **Cross-repo issue links.** When Ember bugs trace to a
  sibling, we link issues across repos.
- **Joint integration tests.** `tests/yggdrasil/` runs full
  cross-realm scenarios.
- **A shared `docs/INTEGRATION_TIMELINE.md`.** When a sibling
  was first integrated, when its protocol changed, etc.

These keep the family from drifting into incompatibility.

---

## Closing

Eleven siblings; one cosmology; one operator. The family is
already alive (the projects exist; the metaphor is alive in the
operator's mind). Yggdrasil is the formal recognition that
they belong together — and the engineering work to make that
recognition real.
