---
codex_id: 52_NO_LICENSE_RISK
title: No-License Risk — What Study-Only Means When You Cannot Cite the LICENSE That Does Not Exist
role: Auditor
layer: Verification
status: draft
waifu_source_refs:
  - (root)/ — directory listing, absence of LICENSE
  - package.json:1-37
  - README.md (no license declaration)
  - src/modes/BasicMode.tsx:1-31
  - src/modes/AdvancedMode.tsx:1-188
ember_subsystem_targets: [Munnr, Brunnr, Smiðja]
cross_refs:
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 20_interface/22_ACTION_PROTOCOL
  - 10_domain/12_DEPENDENCY_STACK
  - sap:53_SECURITY_REVIEW
  - ember:PHILOSOPHY
  - ember:RULES.AI
---

# No-License Risk — What Study-Only Means When You Cannot Cite the LICENSE That Does Not Exist

> *Sólrún, voice cold and even: a repository without a LICENSE file is not a generous gift. It is the default copyright posture of every jurisdiction with a Berne Convention signature. The author has not granted permission to copy, modify, redistribute, or build derivative works. They have only granted permission to read — and read is what we will do. The rest is for our restraint, not their generosity.*

This is the load-bearing doc of the verification layer. The other two (`[[50_DEPENDENCY_HEALTH]]`, `[[51_SECURITY_AND_PRIVACY]]`) catalog technical risk. This one catalogs **legal posture** — the constraint that shapes every Adopt-list entry in every other doc.

The question: *"Now that we have read 846 LOC, what can Ember do with the knowledge, and what must Ember refuse to do?"* The answer lives between *pattern* and *expression*. I draw the line precisely, then turn it into a per-action rubric Volmarr can apply at 2am without rereading legal commentary.

---

## 1. The Empirical Finding

`find /tmp/waifu-chat-starter-kit -maxdepth 2 -iname 'license*'` — returns nothing. No `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `COPYING`, or `UNLICENSE`. The directory listing at the root contains only `README.md`, `eslint.config.js`, `index.html`, `package-lock.json`, `package.json`, `public/`, `src/`, three `tsconfig.*.json` files, and `vite.config.ts`.

`package.json:1-37` declares `"private": true`, name `"aizone-web"`, version `"0.0.0"`. **No `"license"` field.** The README has no license declaration, no SPDX identifier, no "released under" language. Seven git commits; none add a LICENSE. No `.github/`, no `CONTRIBUTING.md`, no CLA reference.

**The repository is unlicensed in the strict sense.** Not "permissively licensed." Not "MIT-by-default." **Unlicensed.**

---

## 2. What "Unlicensed" Means By Default

The mental model "if there's no LICENSE, it's free" is wrong in every Berne Convention jurisdiction — most of the planet, including the US (kit's likely origin per the absolute-path string `/Users/minhanh29/...` in the README), the EU, the UK, Vietnam (likely origin given the author name), and ~180 other countries.

The default copyright posture for original creative work — and source code qualifies — is **all rights reserved**, automatically, at the moment of fixation; held by the author for life + ~70 years; **no grant** of copying, modification, redistribution, derivative-work creation, or public performance.

Posting to GitHub does not change this. GitHub ToS §D.5 grants users the right to **view and fork via the GitHub interface** — and explicitly notes *"this license does not grant any rights for other purposes."* Clone, read, learn — that falls under "view." Anything beyond requires a license from the author. There is no license. Therefore: not permitted.

**This is the legal frame.** Now the practical one.

---

## 3. The Practical Continuum: Idea, Pattern, Expression

Copyright protects **expression**, not **ideas**. The doctrine of `Baker v. Selden` (US, 1879) and analogs in essentially every Berne jurisdiction. The distinction tells us what we can *learn from* versus what we cannot *copy from*.

| Layer | Example | Protected? | Ember's Posture |
|---|---|---|---|
| **Idea** | "Cloud-rendered anime avatar streamed via WebRTC to a browser" | No | Free to discuss, design from, implement |
| **Pattern / Architecture** | "Two parallel mode components: a 31-LOC minimal one and a 188-LOC custom one" | No (functional architecture is generally unprotectable) | Free to use the pattern, must reimplement from scratch |
| **API Shape** | "A `useAvatarSession()` hook returning `{ token, isConnected, isConnecting, micMuted, volume, timeRemaining, connect, disconnect, toggleMic, ... }`" | **Contested** — see `Oracle v. Google` (US Supreme Court, 2021) | Treat as the *interface* of a proprietary SDK; do not duplicate the shape verbatim; reinvent the shape |
| **Specific Code** | `const m = Math.floor(seconds / 60).toString().padStart(2, "0")` | Yes (literal expression) | Do not copy. Write your own formatter |
| **Distinctive Naming** | `LiveKitAvatarSession`, `LiveKitAvatarProvider`, `useAvatarSession` | These are ZeroWeight SDK exports, not the kit's | Belong to ZeroWeight's proprietary SDK, not the kit |
| **Trivial Expression** | `import React from 'react'` | No (lacks originality) | Free, but it's not theirs to give in the first place |

The `Oracle v. Google` cite (US Supreme Court, 2021) ruled Google's reimplementation of ~11,500 lines of Java API declarations was fair use **in the context of building an interoperable platform** — the *use* was transformative, not the declarations uncopyrightable in general. Conservative read for Ember: don't rely on fair use as a shield. Reimplement APIs with *different names, different shapes*. Where the SDK's surface is the only sensible surface (e.g. WebRTC primitives), cite the upstream LiveKit (MIT) and design from there.

---

## 4. The Specific Risk Profile of `aizone-web`

Several features of this particular repository compound the no-license posture:

### 4.1 The Kit Demos a Proprietary SDK

`package.json:14-15` declares `@zeroweight/react: ^0.2.38` and `@zeroweight/renderer: ^0.2.43`. `BasicMode.tsx:3` and `AdvancedMode.tsx:6` import from `@zeroweight/react`. The kit's purpose is to demonstrate ZeroWeight's commercial SDK; ZeroWeight benefits from the kit being studied.

This *reduces* one risk: the implicit social contract is "study this and become a ZeroWeight customer." But that invitation extends to *use of ZeroWeight's SDK as a service consumer*, not to vendoring of the kit's glue code into a competing or unrelated project.

### 4.2 The Kit Is Branded ("Waifu AI Chat", "Zera")

`AdvancedMode.tsx:56` — `<h1>Waifu AI Chat</h1>`. `:128` — `Talk to Zera`. These are *trademark-adjacent* elements. Distinctive naming should be stripped from any pattern Ember adapts.

### 4.3 The Kit Embeds an Author's Absolute Path

The README contains `/Users/minhanh29/Desktop/Workspace/Personal/waifu-chat-starter-kit/...` three times. **This is one person's repository**, not a corporate-managed one. No "open source program office," no licensing email. The most likely outcome of "I emailed minhanh29 to ask about licensing" is "no response." When license-clarification is unobtainable in practice, the conservative posture must hold.

### 4.4 The Kit Mixes MIT Code (LiveKit) and Proprietary Code (ZeroWeight)

LiveKit (`@livekit/components-react`, `livekit-client`, `@livekit/components-styles`) is MIT/Apache-2.0. The terms permit free use, modification, and redistribution with attribution. **Code derived from LiveKit's documentation or repositories** is fair game for Ember.

The kit's *use* of LiveKit (e.g. the `<LiveKitRoom>` JSX block at `AdvancedMode.tsx:168-182`) is the kit's own code, not LiveKit's. That arrangement is the kit's *expression* and falls under "no LICENSE" default.

The load-bearing distinction: when Ember adopts a LiveKit pattern, cite `docs.livekit.io/<page>` or `github.com/livekit/components-js:<path>:<line>`, **not** `AdvancedMode.tsx:168`. The kit showed us what was possible; LiveKit's docs are what we cite when writing Ember's version.

---

## 5. The Per-Action Rubric

Volmarr at 2am asks: *"Can I do X with what I learned?"*

**Read the kit's source code?** Yes. GitHub's "view" right covers it; there is no infringement in reading.

**Cite line numbers in Ember's documentation?** Yes. Citation is not copying. Quoting for analysis is fair use (US fair use, UK fair dealing for criticism/review, Berne 10.1 quotation right). Keep excerpts ≤25 lines per STYLE_GUIDE §7. Full quotation of a 31-line file like `BasicMode.tsx` is defensible when discussing the file as a unit.

**Describe a pattern in prose?** Yes. Prose description of "the kit ships two modes" is fact about the kit; facts are not copyrightable.

**Reimplement the pattern from scratch in Ember?** Yes, with caveats. Don't copy the kit's specific naming (`useAvatarSession`, `LiveKitAvatarSession`, `LiveKitAvatarProvider` — ZeroWeight SDK exports anyway). Where the kit chose names that aren't ZeroWeight's (e.g. `handleToogleCharacter` at `:41`, with the `Toogle` typo), invent your own. Reimplement the *shape*, not the *literal expression*. Your code, written by you.

**Copy 5 lines of code into Ember?** No. Five lines of substantive expression are protected. The Linux kernel project and FreeBSD foundation apply the same standard because the cost of being wrong is project-existential.

**Copy 1 line?** Generally yes for *trivial* expression (`import React from 'react'` — only sensible way), generally no for *substantive*. `const m = Math.floor(seconds / 60).toString().padStart(2, "0")` (`:32`) is a creative choice. Write `const m = String(Math.floor(seconds / 60)).padStart(2, '0')` — semantically identical, syntactically yours. The bar isn't "is this a lot of code." The bar is "is this a creative choice."

**Copy a file (renamed)?** No. The whole-file copy is the canonical infringement. Renaming changes nothing.

**Write a document about the kit and put it under Ember's docs/?** Yes. This document is that document. Ember's original work; the kit's authors have no claim.

**Use kit's package.json as a template?** Mixed. The dep *list* is fact (not protected); the *file's* specific text/formatting is the author's. Look at the deps, write your own.

**Publish Ember commercially if informed by reading the kit?** Yes — informed-by-reading ≠ derived-from-code. Contingent on no vendoring anywhere in source, build, tests, or docs.

---

## 6. The Open Knowledge Vow, Recontextualized

Ember's Vow of **Open Knowledge** (`ember:PHILOSOPHY` §3, `ember:RULES.AI`): *"Knowledge, technology, and culture must remain open, decentralised, and free from corporate gatekeeping."* This is Ember's *output* posture, not *input* posture.

The tension: Ember commits to releasing openly; the kit's author did not. Ember cannot honor its own Open Knowledge commitment by *taking* closed work and republishing it open — that would be openness-by-force, the opposite of the Vow's spirit.

So the Vow does not authorize vendoring no-LICENSE code. The Vow *requires* respecting that this author chose not to grant a license. Open Knowledge applies to what *Ember* produces, not to what others have failed to release. The Vow is honored more deeply by *restraint here* than by appropriation. The discipline is the point.

---

## 7. The Operational Discipline

For codex authoring:

- **Citation format:** `/tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:142` — names file and line; no code duplicated unnecessarily.
- **Excerpt size:** ≤25 lines per STYLE_GUIDE §7. Full quotation of a small file (31-line `BasicMode.tsx`) acceptable when the whole file is analyzed as a unit.
- **Adopt-list language:** must prefer LiveKit upstream (MIT — cite `docs.livekit.io` or `github.com/livekit/components-js`), Ember-invented patterns, or kit-derived entries annotated `[license-pending]`. Adopt entries that propose kit-code-adoption without `[license-pending]` are stylistic violations.
- **Adapt-list:** adapts *patterns*, not *code*. "Adapt the dual-mode architecture" is fine — pattern. "Adapt the AdvancedMode.tsx by changing JSX" is derivative work; not fine.
- **Avoid-list:** names failure modes — descriptive, not derivative, no license implications.
- **Invent-list:** Ember's original design space; license-clear because it's Ember's. The Invent list should be longest in this codex because the no-LICENSE posture forces invention rather than adaptation.

---

## 8. Where This Gets Hard

Two genuinely-fuzzy cases:

### 8.1 The Action Vocabulary

`AdvancedMode.tsx:44-49` dispatches `"embarrassed"`, `"dance"`, `"wave_hand"`. These names are documented by ZeroWeight (per README) as part of the operator's avatar configuration — ZeroWeight's API surface, not the kit's invention. Mentioning them in analysis is fine. The kit's *use of them in a dispatch table* is the kit's expression; reimplementing a dispatch table with the same three names is arguably conformance to a third-party API (ZeroWeight's), not copying from the kit. Same logic as "you can write SQL that uses someone else's table names." `[[22_ACTION_PROTOCOL]]` analyzes this surface in depth.

### 8.2 The CSS

`AdvancedMode.css` is 379 LOC. CSS is *less* clearly creative than imperative code in some legal traditions, but courts have not converged. Treat CSS the same as code: cite, don't copy.

---

## 9. The Worst-Case Scenario, Modeled

If Ember copied AdvancedMode.tsx verbatim and shipped it:

- **Detection probability:** Low-medium. GitHub search flags verbatim copies; `licensee`, `fossology`, `scancode-toolkit` detect unlicensed origins. A determined complainant could find it within hours.
- **Escalation probability:** Low. minhanh29 is an individual; the likely response is a public complaint, not a lawsuit.
- **Public-complaint cost:** **High.** Ember's reputation is partly its Vows. "Ember violated upstream copyright" damages standing with the audience Ember most wants to attract — independent, ethics-conscious developers.
- **Corporate-scale escalation (hypothetical):** US statutory damages up to $30k/work non-willful, $150k willful. Low likelihood; project-existential tail risk.

The reputational cost alone outweighs any conceivable benefit from vendoring 846 LOC. The work can be rewritten in days; reputational damage from "Ember used unlicensed code" cannot be undone in years.

---

## 10. The Future State

If a LICENSE appears later (MIT, Apache-2.0, BSD-3 — any OSI-approved permissive license), posture relaxes substantially. If a *restrictive* license appears (AGPL-3.0, copyleft), posture **tightens** — positive prohibition. If a *no-commercial* license appears (CC-BY-NC, BSL), posture stays as restrictive as today. Scribe's `meta/CROSS_AGENT_NOTES.md` should record the date of last license check and recommend re-check on Ember's next major codex revision.

---

## 11. Cross-References

- `[[50_DEPENDENCY_HEALTH]]` — LiveKit (MIT, freely adoptable) versus ZeroWeight (proprietary, cite-only)
- `[[51_SECURITY_AND_PRIVACY]]` — security surfaces independent of license; mic capture and cloud session posture
- `[[22_ACTION_PROTOCOL]]` — the action vocabulary discussion (one of the kit's two fuzzy-line cases)
- `[[10_DOMAIN_MAP]]` — the kit's macro shape (factual; not protected)
- `[[12_DEPENDENCY_STACK]]` — per-dep license disposition
- `[[30_BASIC_MODE_FLOW]]` — full-file quotation of BasicMode is acceptable per STYLE_GUIDE §7
- `[[sap:53_SECURITY_REVIEW]]` — SAP has a license (AGPLv3) and that fact shapes Ember's posture differently; this codex's no-LICENSE state is the *more restrictive* sibling case
- `[[ember:PHILOSOPHY]]` §3 — the Open Knowledge Vow as Ember's output posture
- `[[ember:RULES.AI]]` — the Vow as operational law

---

## What This Means for Ember

**Adopt:**
- Adopt the **per-document license-clearance checklist** as a Scribe-pass invariant. Every Adopt-list entry checked against: (a) LiveKit MIT? (b) Ember-invented? (c) Kit-derived and `[license-pending]`? If none, reject.

**Adapt:**
- Adapt the **citation format** the SAP codex uses (`path:line` with optional excerpt) but extend it: every kit citation in this codex implicitly carries the `[study-only — no LICENSE]` annotation. The Scribe can elide it in display but it is binding on every Adopt/Adapt evaluation. The codex's citation discipline is *adapted from* SAP and *tightened* for the no-LICENSE case.
- Adapt the **Open Knowledge Vow** language to explicitly cover the *input* posture as well as the *output* posture. Current language addresses what Ember releases; the kit study has shown a gap: what Ember consumes also matters. Recommended addition to PHILOSOPHY §3: *"The Vow of Open Knowledge applies to inputs as well as outputs. Ember does not take without permission, even where it could not be detected."* This is an *adapted* clarification of the existing Vow.

**Avoid:**
- **Avoid copying kit code into Ember.** No file copy. No function copy. No 5-line copy. No 1-line copy of substantive expression. The conservative posture is uniform.
- **Avoid replicating ZeroWeight SDK signatures in Ember.** Even where Ember wants a similar capability, do not name the hook `useAvatarSession`, do not name the component `LiveKitAvatarProvider`. Invent Ember's own naming. (For example: Ember's proposed `CloudPresenceSession`, `RealtimeAvatarBridge`. Names that signal Ember's idiom, not ZeroWeight's.)
- **Avoid vendoring `package.json`'s text.** The dep list is fact; the file is expression. Look at what they chose; write your own file.
- **Avoid implying license-clearance retroactively.** If the kit ever gets a LICENSE, the posture relaxes prospectively, not retroactively. Any docs written under the no-LICENSE posture remain valid as written; their Adopt lists remain conservative.
- **Avoid the trap of "five lines doesn't matter."** The conservative-posture line is "cite or invent, never copy." Even five lines of substantive expression is a copy. The Linux kernel discipline holds; the FreeBSD discipline holds; Ember's discipline holds.
- **Avoid emailing minhanh29 expecting a license grant.** It is the right move to try once, briefly. It is the wrong move to wait on a response, or to assume one. Plan for "no response" as the working assumption.

**Invent:**
- **The Three-Tier Citation Annotation.** Every kit citation in Ember's docs carries one of: `[mit-upstream]` (LiveKit cited via official source), `[study-only — no LICENSE]` (kit cited for analysis only), `[interface-only — proprietary SDK]` (ZeroWeight surface visible only through the kit's usage). The Scribe enforces. The reader knows what they can do with each citation without rereading the legal frame. This annotation set does not exist in SAP codex; it is invented here because the no-LICENSE posture demands it.

- **The Pre-Vendor Hash Gate.** Before any external code lands in Ember's source tree, a CI gate fires: hash the candidate file; compare against the kit's tree; if a match (or near-match, by `simhash` or similar), block. The principle is "Ember's source tree cannot contain bytes from a no-LICENSE upstream, even by accident." This invents the technical countermeasure for the *human discipline* gap.

- **The License-Surface Manifest.** Ember ships `LICENSE_SURFACE.md` listing every external project Ember has studied (kit, SAP, Hermes, Peer, Klóinn, others). Each entry: project name, project license, what Ember took (patterns / nothing), what Ember cites. Operators and reviewers can audit Ember's input posture in one document. The no-LICENSE projects are listed prominently as "study-only — no derivation."

- **The Pattern-vs-Expression Note.** Every doc's Adopt/Adapt entry that derives from a third-party project carries a one-line note distinguishing the *pattern* (unprotectable) from the *expression* (protected). The discipline becomes habit. SAP's codex doesn't do this systematically; this codex starts the habit.

- **The Re-Check Cadence.** The Scribe's final pass adds to `meta/CROSS_AGENT_NOTES.md` a "next license re-check" date — typically Ember's next major codex revision (~6 months). On that date, a re-check confirms: does the kit still lack a LICENSE? Is the project still active? Has anything changed? The cadence keeps the posture current rather than stale.

- **The Fork-and-License-Yourself Anti-Pattern Naming.** Some open-source projects, when faced with a useful no-LICENSE upstream, fork the repo, slap an MIT LICENSE on the fork, and proceed. This is **illegal** in essentially every jurisdiction — you cannot license code you don't have rights to. Ember names this anti-pattern and documents the prohibition. The naming is invented here because Volmarr-at-2am might be tempted, and the codex says "no, don't, here's why."

The line is drawn. The discipline holds. The codex's value is in the *learning*, not the *taking*. That is what study-only means in practice — and it is what the Open Knowledge Vow, read carefully, has always required.
