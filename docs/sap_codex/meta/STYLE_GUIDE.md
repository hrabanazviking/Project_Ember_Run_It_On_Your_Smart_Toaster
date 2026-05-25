---
name: sap-codex-style-guide
description: Voice, tone, length, structure, citation rules, and closer format for every SAP Codex document
metadata:
  codex: sap
  type: meta
---

# STYLE_GUIDE — Super Agent Party Codex

This guide is binding. Read it before authoring any doc.

---

## 1. Length

**Target:** 1,500–4,000 words per doc.
**Floor:** 1,500 words. Below this you are summarizing, not teaching.
**Ceiling:** 4,000 words. Above this, split (`<slug>_A.md` / `<slug>_B.md`) and update `meta/MANIFEST.md` with the new entries.

Word count is not the goal. *Insight density* is the goal. A 1,500-word doc with three load-bearing insights beats a 4,000-word doc with one.

## 2. Voice

The codex voice is **technical, entertaining, insight-rich**.

- **Technical** — name files, name modules, name line numbers, name functions, name classes. Quote real code where instructive.
- **Entertaining** — the reader is a sleep-deprived solo developer reading at 2am. Earn their attention. Use sharp sentences, occasional dry humor, the occasional metaphor that actually fits.
- **Insight-rich** — every section should make the reader smarter. If a paragraph could be deleted without losing a teaching, delete it.

Avoid:
- Corporate dead language ("leverage", "robust solution", "best-in-class", "next-generation")
- Marketing tone ("powerful", "amazing", "revolutionary")
- Filler ("In conclusion", "It is important to note that")
- Generic warnings ("Be careful here") — name the specific failure mode

Prefer:
- Concrete subject + concrete verb + concrete object
- One idea per paragraph
- Lists when the items are genuinely parallel; prose when they're not

## 3. Structure

Every content doc follows this skeleton (adapt as needed):

```markdown
# <Title>

> *<Optional epigraph — a quote or a one-line distillation>*

<2–4 sentence opening that names what this doc is about and what the reader will gain>

## <Section 1: The Subject Itself>

<What is it? Where does it live? Cite files.>

## <Section 2: How It Works>

<Mechanism. Cite specific lines.>

## <Section 3: Where It Breaks / Where It Surprises>

<The auditor-flavored section — what's brittle, what's leaky, what's clever-in-the-wrong-way>

## <Section 4: Cross-References>

<[[slug]] links to related docs in this codex; [[hermes:slug]] etc. cross-codex>

## What This Means for Ember

**Adopt:** <patterns to take wholesale, named>
**Adapt:** <patterns to take and transform, with the transformation specified>
**Avoid:** <patterns to reject, with the reason>
**Invent:** <novel patterns this analysis suggests, named>
```

The "Adopt / Adapt / Avoid / Invent" closer is **mandatory**. Each list must have at least one entry — if you can't fill one, write "(none from this lens)" and explain why in one line.

## 4. Citation

Every claim about SAP must cite real code, not the README.

**Format:**
```
`/tmp/super-agent-party/py/affection_system.py:142` — `class AffectionState` defines decay rate of 0.95 per tick
```

For multi-line ranges:
```
`server.py:2410–2438` — sub-agent spawn lifecycle
```

For files that aren't Python (config, JSON, JS):
```
`config/settings_template.json:14` — default `affection_decay_rate`
`main.js:1240` — IPC handler `register-extension`
```

If a README claim cannot be verified in code, mark it:
```
SAP claims "VRM and Live2D have feature parity" [unverified — README claim only]
```

**Never** paraphrase the README as if it were code-grounded. The README is marketing until proven otherwise.

## 5. The "What This Means for Ember" Closer

This is the load-bearing section of the entire codex. It is why this document exists.

- **Adopt** — name the SAP pattern, name the Ember module that should take it, name the True Name (if applicable).
- **Adapt** — name the SAP pattern, name what to change, name *why* (Vow violation, Ember-specific constraint, scale mismatch).
- **Avoid** — name the SAP pattern, name the failure mode it embodies, name what Ember does instead.
- **Invent** — name a pattern that didn't exist in SAP but became visible *because* of this analysis. This is the most valuable category. Aim for at least one true Invent in every doc.

Be specific. "Adopt SAP's MCP integration" is useless. "Adopt SAP's pattern of treating MCP servers as supervised child processes (`mcp_clients.py:88` `MCPClientManager.spawn`), but bind it to Ember's Smiðja instead of a global registry" is the bar.

## 6. Cross-Linking

Within this codex: `[[slug]]` (filename minus `.md`). Example: `[[1A_AFFECTION_DOMAIN]]`.

Across codexes:
- `[[hermes:HEM-23_HOTSWAP]]`
- `[[peer:LETTA-2_SLEEPER]]`
- `[[ember:CROSS_PLATFORM_PLAN]]`

Forward-link liberally — the Scribe verifies all links resolve on the final pass. A `[[slug]]` that doesn't match an existing doc yet is fine; it marks something worth writing, not an error.

## 7. Code Excerpts

When quoting SAP code, use fenced blocks with language and a citation comment on the first line:

```python
# /tmp/super-agent-party/py/affection_system.py:140–155
class AffectionState:
    def __init__(self, decay_rate: float = 0.95):
        self.decay_rate = decay_rate
        ...
```

Keep excerpts under 25 lines. If you need more, summarize the rest in prose and cite the range.

## 8. Tone Calibration — Examples

**Too dry:**
> "The affection system in SAP implements a decay-based state machine for tracking user-agent emotional state."

**Too hyped:**
> "SAP's affection system is a revolutionary breakthrough in AI emotional intelligence!"

**Right:**
> "SAP's `affection_system.py` is a decay machine wearing a heart-shaped mask. State drifts toward neutral every tick; positive events nudge it up; gacha-style milestones unlock animations. It is honest about what it is — but it is also exactly what Ember must not become."

## 9. Failure to Cite

If a doc lacks specific citations to SAP source, it fails review. The Auditor will catch this. The Scribe will return it for revision.

## 10. Continuation Notes

If you run out of budget mid-doc:

```markdown
## Continuation Notes

**Stopped at:** <section name or topic>
**Remaining scope:**
- <bullet>
- <bullet>
**Source files still to read:**
- `py/foo.py:200–400`
- `py/bar.py` (entire)
**Open questions:**
- <question>
```

The next agent picks up from here. No silent truncation.

## 11. The Hermes Codex as Voice Reference

If you're calibrating tone, read these as exemplars:

- `docs/hermes_codex/00_vision/00_OVERTURE.md` — Skald voice
- `docs/hermes_codex/10_domain/` (any) — Architect voice
- `docs/hermes_codex/50_verification/` (any) — Auditor voice
- `docs/hermes_codex/30_execution/` (any) — Forge voice
- `docs/hermes_codex/60_synthesis/` (any) — synthesis voice

The SAP Codex is a sibling of Hermes — same voice family, different subject.

## 12. The Reader

Imagine the reader is Volmarr at 2am with ADHD, a half-empty mug, and the question *"is this worth keeping for Ember?"* burning behind their eyes.

Write for that reader. Earn their attention. Hand them a teaching they can carry into the morning.
