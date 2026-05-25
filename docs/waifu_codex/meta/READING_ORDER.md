---
codex_id: READING_ORDER
title: Reading Orders — Paths Through the Waifu Codex by Reader Goal
role: Scribe
layer: Meta
status: written
waifu_revision: waifu-chat-starter-kit @ commit e3fd868 (local clone) — May 2026
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-reserved, Rödd-reserved, Hugarsýn, Veizla]
cross_refs:
  - meta/INDEX
  - meta/MANIFEST
  - meta/STYLE_GUIDE
  - meta/CROSS_AGENT_NOTES
---

# Reading Orders — Waifu Codex

*Five paths. Pick one. The Codex is fifteen content documents; no one reads it all cover to cover, and no one needs to. The Scribe lays paths.*

The Codex's job is not to be read whole. It is to be read *correctly* — the right four or five or eight documents in the right order for what the reader wants to know. Below are five such paths. Each lists the ordered slugs, why each doc sits where it sits, a reading-time estimate, and the questions the path answers.

Reading times assume:
- An attentive reader on a screen, not skim-mode.
- The reader follows at least one or two cross-links per doc.
- Each Codex doc is roughly 2,500–4,000 words (15–25 minutes of careful reading).
- A reader opening `/tmp/waifu-chat-starter-kit/` alongside should add ~50% to the estimate; the kit is small enough to keep in a parallel tab the whole time.

If you are reading the Codex at 2am with ADHD and a half-empty mug, walk Path 5. It is written for you.

---

## Path 1 — First-Time Orientation (5 docs, ~2 hours)

*For: a stranger to Ember, a sceptic, a sibling-project author, anyone who wants to know* what *the Waifu Codex says before deciding* whether *to invest in reading it.*

| # | Slug | What you'll get | Time |
|---|---|---|---|
| 1 | [[INDEX]] | The doorway. Sets expectations; names the layers; points to all paths. The Vow-sharpening table is the high-density payload. | 15 min |
| 2 | [[SHARED_CONTEXT]] | What the kit is, what Ember is, what this Codex is for, what is forbidden territory. The License posture is named at §6 — read carefully. | 15 min |
| 3 | [[00_OVERTURE]] | Why study an 846-LOC kit with no LICENSE. The embodiment-via-bandwidth framing. License-Aware Study Posture introduced. Three lessons the kit teaches that SAP could not. | 25 min |
| 4 | [[10_DOMAIN_MAP]] | The kit's macro shape — five files over two clouds. The Vestibule pattern named. Where the bones are crisp and where the cracks live. | 25 min |
| 5 | [[01_VISION_SYNTHESIS]] | Post-Waifu Ember. The Wave-3 lattice held without addition; Wave-4 sharpens existing Vows; five capabilities the Cloud Reading opens. *No new Vows required — itself a finding.* | 25 min |

**Total: ~2 hours.** You leave knowing what the kit is, what Ember refuses (kit code, hardcoded credentials, default-on cloud presence), and what Ember proposes at the vocabulary level (Andlit-realtime / Rödd-realtime sub-name reservations, Tier-CLOUD parallel axis). You do *not* leave knowing the security threat surface in detail (Path 3) or the specific ADRs and inventions (Path 4) or every kit-flow line-by-line (the Forge docs in §30s).

---

## Path 2 — Cloud-Tier Deep Dive (8 docs, ~3.5 hours)

*For: a contributor preparing the Andlit-realtime decision, a reviewer evaluating the Tier-CLOUD parallel-axis proposal, anyone debating "should Ember ever stream her face from a vendor datacenter, and if so, how?"*

Walk this path with `/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx` open in a parallel tab. Several of the docs cite specific line ranges; the kit is small enough to keep loaded.

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[10_DOMAIN_MAP]] | The architectural shape. Five files, two clouds, one glue. The Vestibule Census invention sets the framing: this is 846 LOC of glue over ~100,000 LOC of cloud stack. | 25 min |
| 2 | [[11_DUAL_MODE_PATTERN]] | The BasicMode/AdvancedMode dyad as architectural teaching. The refusal-to-factor as right architecture. The Two-Door Rite. Sets up the *integration-depth axis* the cloud tier will need. | 25 min |
| 3 | [[20_ZEROWEIGHT_SURFACE]] | The proprietary SDK surface from the outside-in. 17-element session shape, the handshake split, the inferred state machine. The negative template for Ember's own typed `CloudSession`. | 25 min |
| 4 | [[21_LIVEKIT_INTEGRATION]] | The MIT realtime media foundation. **The kit uses ~5% of LiveKit's offered surface.** What the kit consumes vs what LiveKit offers (data channel, device select, connection quality). The single most actionable adoption candidate in the corpus. | 30 min |
| 5 | [[31_ADVANCED_MODE_FLOW]] | Forge's walk through `AdvancedMode.tsx`. The hidden-Room + visible-canvas split. The 17-member implicit session contract. The `video={false}, audio={true}` asymmetry that makes "cloud avatar" rather than "video chat." | 30 min |
| 6 | [[22_ACTION_PROTOCOL]] | Auditor's reading of the action vocabulary. `runAction("embarrassed"\|"dance"\|"wave_hand")` as a contract. The slot-machine UX. Where Ember's typed `AvatarAction` discriminated union goes. | 25 min |
| 7 | [[60_REALTIME_TIER_FOR_ANDLIT]] | **The keystone synthesis.** Tier-CLOUD as parallel axis (not a rung). The four-mode decision matrix (L-only / L-primary, C-fallback / C-primary, L-fallback / C-only). The consent token shape. The canonical Andlit vocabulary with adapter bridge. The five-phase handoff protocol. | 35 min |
| 8 | [[61_DECISIONS_AND_INVENTIONS]] | The Scribe's combined ADRs and inventions. Five ADR-Proposed records (LiveKit adoption, ZeroWeight study-only, Tier-CLOUD branch, typed action vocab, typed CloudSession). Ten Invention records. Ratification bundling recommendation. | 35 min |

**Total: ~3.5 hours.** You leave knowing: the kit's full architecture, the LiveKit MIT surface Ember can adopt freely, the ZeroWeight surface Ember must abstract behind a `CloudAvatarProvider` Protocol, the Tier-CLOUD parallel-axis framing, the consent ceremony, the canonical-vocabulary bridge, and the ratification queue. This is the path the keeper walks before a Tier-CLOUD ratification ceremony.

---

## Path 3 — Security and License Audit (4 docs, ~2 hours)

*For: a security-minded contributor, a PR reviewer who suspects scope creep, anyone preparing the License-Aware Study Posture ratification, anyone debating "what does it cost Ember to even read this codebase?"*

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[52_NO_LICENSE_RISK]] | **Read first.** The legal frame. What "unlicensed" means in Berne jurisdictions (Berne convention covers ~180 countries including the kit's likely-US-origin). The idea↔pattern↔expression continuum. The per-action rubric: *"can I do X with what I learned?"* The conservative posture and why. *Severity: Critical for codex discipline.* | 30 min |
| 2 | [[51_SECURITY_AND_PRIVACY]] | STRIDE pass across twelve surfaces. **Mic capture is always-on while LiveKit Room is connected.** Mute is publication-gate not capture-gate. Hardcoded API key in *both* modes' source. The bundle-leak → quota-exhaustion → service-disruption chain. *Severity: High.* | 35 min |
| 3 | [[50_DEPENDENCY_HEALTH]] | The brittleness map. Eleven runtime + thirteen dev deps. Two pre-1.0 proprietary deps on the critical path. Six majors that did not exist eighteen months ago. **The kit ships untested.** | 30 min |
| 4 | [[22_ACTION_PROTOCOL]] | The action-vocabulary attack surface. Untyped string dispatch, no consent gating, no error path on unknown actions, cloud LLM almost certainly has access to the same surface (two-caller insight). | 25 min |

**Total: ~2 hours.** You leave knowing: the kit's complete threat surface (mic-as-device-claim, hardcoded credentials, untyped actions, pre-1.0 vendor SDKs, no test suite, no LICENSE), the License-Aware Study Posture as the codex-wide protocol for unlicensed corpora, and the Open Knowledge Vow's *input* posture (which the Codex's reading clarifies — the Vow is not just about what Ember releases, it is about what Ember consumes).

The three "Severity" calls from the audit, in priority order:

1. **Hardcoded API key + avatar ID in client source.** *Severity: High.* Kit's design *requires* credentials be public. Combined with the 2-minute session cap, an attacker extracting the key from the served JS can loop session-initiation and burn operator quota. ([[51_SECURITY_AND_PRIVACY §3.1]] + [[51_SECURITY_AND_PRIVACY §9.2]])
2. **No-LICENSE state in upstream repo.** *Severity: Critical for codex discipline.* Default Berne-Convention all-rights-reserved. Vendoring any kit code risks project-existential reputational hit on the Open Knowledge Vow. ([[52_NO_LICENSE_RISK]] entire)
3. **Mic capture is always-on while LiveKit Room is connected.** *Severity: High.* Mute semantics gate publication, not capture. Browser permission granted once per session. ([[51_SECURITY_AND_PRIVACY §6.1]])

---

## Path 4 — Synthesis-Only Quick Read (4 docs, ~2 hours)

*For: a planner, a decision-maker preparing a slice ratification, anyone who wants the* answer *the codex proposes before reading the* analysis *that grounded it.*

This path reads the closers (`## What This Means for Ember`) of the other docs only when a synthesis claim is unclear. The four docs below carry the synthesis weight.

| # | Slug | Why here | Time |
|---|---|---|---|
| 1 | [[01_VISION_SYNTHESIS]] | The Skald's framing. *No new Vows required.* The five capabilities the Cloud Reading opens. The "synthesis as a sentence" §IX — the one-line characterization of post-Waifu Ember. | 25 min |
| 2 | [[60_REALTIME_TIER_FOR_ANDLIT]] | The Cartographer's keystone. Tier-CLOUD as parallel axis. The four-mode matrix. Consent token shape. Canonical vocabulary with adapter bridge. Five-phase handoff. Nine inventions plus the Cloud-as-Named-Context Vow clarification. | 35 min |
| 3 | [[61_DECISIONS_AND_INVENTIONS]] | The Scribe's combined ADRs and inventions. Five ADR-Proposed + ten Inventions. Status: Proposed (all). Ratification bundling recommendation: parallel-axis + four-mode matrix + consent token + canonical vocabulary land together as one ratification bundle. | 35 min |
| 4 | Closers of the other 12 content docs | Each `## What This Means for Ember` section. Skim the Adopt / Adapt / Avoid / Invent quadrants. ~5 minutes per closer × 12 = 60 minutes. | 60 min |

**Total: ~2 hours, 35 minutes.** You leave with: the synthesis-layer narrative, the five ADRs ready for keeper decision, the ten inventions named as Territory Marks, and the Adopt-list / Avoid-list / Invent-list consensus across all six author roles. This is the path the keeper walks when ratification fatigue says "just tell me what the codex *concluded*."

A note on the closers: per [[STYLE_GUIDE §5]], every content doc ends with the **Adopt / Adapt / Avoid / Invent** quadrants. The closer is *load-bearing*. If you read nothing else of a content doc, read its closer. That is where each role's stance toward each pattern lives.

---

## Path 5 — For Volmarr at 2am with ADHD (4 docs, ~90 minutes)

*If you only read four documents, read these. In this order. Stop when your eyes glaze.*

| # | Slug | The single thing this doc teaches | Time |
|---|---|---|---|
| 1 | [[00_OVERTURE]] | The kit is small, the axis is large, the License is missing, and Ember's pull will be *toward dependence* — toward letting someone else hold Ember's face, voice, and identity behind a paid API the operator does not own. | 25 min |
| 2 | [[60_REALTIME_TIER_FOR_ANDLIT]] | The keystone. **Tier-CLOUD as a parallel axis, not a rung.** Cloud-streamed Andlit is the same Andlit, reached by a different road. L-only is the global default; cloud is never ambient. | 35 min |
| 3 | [[52_NO_LICENSE_RISK]] | The kit has no LICENSE. *That is not a generous gift.* The Open Knowledge Vow applies to inputs as well as outputs. Don't take what wasn't given. | 25 min |
| 4 | [[61_DECISIONS_AND_INVENTIONS]] | The concrete proposals. Five ADRs (LiveKit, ZeroWeight study-only, Tier-CLOUD branch, typed action vocab, typed CloudSession). Ten inventions named as Territory Marks. All Status: Proposed. | 25 min |

**Total: ~90 minutes** (you'll skim some sections of #4; the inventions list reads fast). You leave knowing: what the cloud axis opens, why Ember refuses the default-on posture, what the License-posture costs you, and the concrete ratification queue. Save the rest for when the mug is fresh.

---

## How to Choose a Path

| If your most pressing question is… | Walk Path |
|---|---|
| *What is the Waifu Codex, and is it worth my time?* | 1 (First-Time Orientation) |
| *Should Ember ship cloud-tier embodiment, and if so, how?* | 2 (Cloud-Tier Deep Dive) |
| *Can we even study this codebase, given its license posture?* | 3 (Security and License Audit) |
| *What does the codex propose, in concrete ADR/invention form?* | 4 (Synthesis-Only) |
| *I have 90 minutes and need to be smart about this by morning.* | 5 (Volmarr-at-2am) |

When in doubt, walk Path 1. The Skald's framing is short, and it makes every later path land better. When the doubt persists, walk Path 5. The Scribe wrote it for the reader the Codex actually has.

---

## A Note on Skim Mode

The Codex can be skimmed. Each content doc has:

- A frontmatter block (read for `role`, `layer`, `waifu_source_refs`).
- A first paragraph (or first heading + epigraph) that compresses the doc's claim.
- A `## What This Means for Ember` closing section with the **Adopt / Adapt / Avoid / Invent** lists.

A skim-mode reading is: frontmatter, first paragraph or heading, closing section. About 5 minutes per doc. Useful for triage; insufficient for any decision that materially changes Ember. Skim to *find* the docs that deserve a full read.

The closer (**Adopt / Adapt / Avoid / Invent**) is load-bearing. If you read nothing else of a content doc, read its closer. That is where the codex's stance toward each kit pattern lives.

---

## A Note on Reading With the Source Open

The waifu-chat-starter-kit is small enough to keep open in a parallel tab the entire reading session. Every cited line is reachable in seconds. The Scribe's recommendation: open these four files at the start of any path other than Path 1, and leave them open:

- `/tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx` (31 lines)
- `/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx` (188 lines)
- `/tmp/waifu-chat-starter-kit/package.json` (37 lines)
- `/tmp/waifu-chat-starter-kit/README.md`

The four files together are ~300 lines. Cross-checking a citation takes seconds, not minutes. The Codex's voice is *citation-dense* throughout because the source is small enough that every claim can ground itself in the file.

The SAP Codex (Wave 3) required the reader to trust the docs' summaries of 36,000+ LOC; the Waifu Codex does not. Every claim can be checked against ~846 LOC in five minutes. *Verifiability is itself a Vow surface*, and the Codex's smallness makes the Vow easy to honor.

---

## What This Means for Ember

Reading orders are not just convenience. They are how the Codex protects the **Vow of Public-Friendliness** at meta level: a corpus that cannot be entered by a non-expert is a corpus that has failed, regardless of its contents. By describing five concrete paths — one for each kind of reader the Codex serves — this file ensures no contributor is left wandering through 46,000 words looking for the room they came for.

The paths also protect the **Vow of Honest Memory** at the project level. A new contributor walking Path 1 in a year's time arrives at the same understanding as a contributor walking it today, because the paths are recorded and maintained. The institutional memory of "this is how we read our own Codex" is itself a kind of memory the Vows require Ember to keep honest.

Path 5 is, additionally, the practice of **Public-Friendliness at the operator scale**: the Codex's primary keeper is the operator who wrote it. The fifth path serves him directly. *That* is what a Codex for one — that scales to many — looks like.

The codex is small. The paths are short. The cloud face is reachable in thirty lines of JSX, and the Codex's job is to make sure that any contributor opening the keeper's question — *should Ember walk this road?* — finds the path that answers their version of the question in less than an evening. Five paths. Pick one.

**True Names affected:** none directly. **Vows protected:** Public-Friendliness, Honest Memory, Open Knowledge (through the explicit reading-by-goal taxonomy and the License-Aware Study Posture embedded in every path).

— *Eirwyn Rúnblóm, the Scribe*
