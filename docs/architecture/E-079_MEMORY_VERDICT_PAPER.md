# E-079 — The Verdict Paper: Unify / Bound / Retire

*Part V (Memory: Two Systems, One Verdict), third slice.
Roadmap line: "The verdict paper: unify / bound / retire —
argued from E-078's numbers + ORIGINS provenance, presented
for Volmarr's word where a retirement is proposed."
Evidence base: E-077's map (storage, retrieval, consumers,
test state for all three systems) and E-078's comparison
harness (identical synthetic workloads through all three;
canonical run 2 on the campaign VM, Python 3.12.3).
Provenance base: E-012 §1 and E-003 — ORIGINS.md itself
carries **no row for either member system** (docket 72;
E-196 owns extending the register), so provenance here is
stated from the members' own packaging and git history,
exactly as E-012/E-077 recorded it. No system is retired,
moved, or modified by this slice. No store was opened.*

## 1. Plain-language summary — the verdict

**Bound, with one retirement proposed — not three systems
competing, and not one system crowned.**

- **One face.** From E-080 the companion speaks to memory
  through **one memory contract** (the "one face" Part V's
  gate, E-092, will judge). Behind that face the two house
  systems keep the jobs the measurements say each is
  actually good at. No user, and no other part of Ember,
  ever has to know there are two stores.
- **Brunnr keeps documents, chunks, and conversation
  turns.** It is the incumbent — the only system the
  companion actually uses today — it answered verbatim
  **20/20**, paraphrase **9/9** (pure vector), it alone
  holds episodes as turns (last 5 of 12, exact, in
  order), and its episode cost is cheap (**585 B/episode**
  steady-state, E-050). Its store-open weight (33.2 MiB)
  fits.
- **mimir-well keeps living facts.** It alone answered
  the living questions exactly: importance recall
  **exact (5/5, none extra)**, mood recall **exact
  (6/6, none extra)**, and current truth after a fact
  changed (**new present, old absent**). It alone has a
  lifecycle (decay, consolidation), a write guard, and
  an audit trail. And it is the only system that fits
  **every** budget profile, the toaster included
  (614,283 B installed post-E-078; 24.2 MiB peak;
  745 B/item growth).
- **mempalace is proposed for honourable retirement
  from Ember — and that word is Volmarr's, not this
  paper's.** It remembers words and meanings perfectly
  (verbatim 20/20, paraphrase 9/9), but it fits **no**
  profile in the budget book: ~403 MiB working RAM
  against ceilings of 64 / 128 / 192 / 384 MiB, and
  roughly **185 MB of dependencies + ~88 MB of model**
  against install ceilings topping out at 16 MiB. It
  has **no consumer anywhere in this tree**, it is
  upstream open-source that lives on at its own home,
  and nothing in the companion would notice its
  absence. §6 states the proposal, what retirement
  would and would not mean, and the bounded fallback
  if Volmarr declines it. **Until he rules, mempalace
  stays exactly where it is, untouched.**
- **The paraphrase gap is closed at the face, not by
  merging stores.** mimir-well has no meaning search
  (measured: paraphrase **0/9**). The verdict does not
  ask it to grow one. Instead E-080's contract is
  charged with *index, don't merge*: living facts may
  be indexed into Brunnr's chunk store for meaning
  search, with hits resolved back through mimir-well's
  current-truth view — so a reworded question can find
  a fact, but a superseded fact is never served as
  current. This is a **proposal for E-080 to implement
  and prove**, not a result claimed here.

Why not simply unify on one system? Because every
single-system crown fails on measured evidence, not
taste — §4 takes each crown in turn.

## 2. The evidence the verdict argues from (E-078)

Recall, canonical run (identical corpus, one query set,
embedder held constant — ONNX all-MiniLM-L6-v2; a hit =
the target's marker in a top-5 result):

| Workload | mempalace | mimir-well | Brunnr |
|---|---|---|---|
| Verbatim phrase | 20/20 | 20/20 (FTS, post-fix) | 20/20 |
| Distinctive terms | 20/20 | 20/20 (FTS, post-fix) | 20/20 |
| Paraphrase (reworded) | **9/9** | **0/9** — no semantic search | **9/9** vector / 8/9 hybrid |
| Importance recall | no such face | **exact** | no such face |
| Mood recall | no such face | **exact** | no such face |
| Current truth after supersession | old + new, old first | **new only** | old + new, old first |
| Episode recall (last 5 of 12) | no such face | no such face | **exact, in order** |

Weight and speed (E-078 §5; VM-contended, comparative):

| | mempalace | mimir-well | Brunnr |
|---|---|---|---|
| Install story | ~1 MB package **+ ~185 MB deps + ~88 MB model** | 614,283 B | 831,124 B (core tree) |
| RAM judged | 402.8 MiB peak | 24.2 MiB peak | 33.2 MiB store-open |
| Growth per item | 11,737 B | **745 B** | 72,239 B embedded chunk; **585 B/episode** |
| Budget fit | **no profile** | **every profile** | laptop all; smaller profiles fail only on embedded-chunk growth |
| Word search median | ~650–800 ms (embeds first) | 0.1–0.16 ms | 0.11–0.17 ms |

Two readings of this table drive the whole verdict:

1. **No row wins every column, and every column has a
   winner.** Verbatim is a three-way tie. Meaning
   belongs to mempalace and Brunnr. Living questions
   belong to mimir-well alone. Turns belong to Brunnr
   alone. A verdict that crowns one system throws away
   measured wins of the others.
2. **The budget book is the project's soul, and only
   one column survives it whole.** mimir-well fits
   everywhere; Brunnr fits everywhere its growth is
   episode-priced rather than vector-priced; mempalace
   fits nowhere, by an order of magnitude, on both RAM
   and install. On tiny hardware that is not a
   trade-off to weigh — it is a disqualification from
   the companion's default shape.

## 3. Provenance — whose line each system is (E-012/E-077)

- **mempalace** — upstream open-source (MemPalace, by
  milla-jovovich; pyproject homepage/repository point
  at its upstream home), MIT, v3.3.5, imported whole in
  exactly one commit (f7ef473, 2026-05-21) and unchanged
  by one byte since until this campaign measured it.
  Its consumers are external by design (Claude Code
  hooks, MCP clients); in-tree consumers: **none**.
- **mimir-well** — the house's own line (Runa/Hermes
  heritage; author Eldrä Járnsdóttir), MIT, v2.10.4,
  one import commit (911eeba, 2026-05-21), stdlib-only
  at its core. In-tree consumers exist but disagree:
  Verdandi's heartbeat follows the library default
  (`~/.mimir_well/mimir_well.db`) while bifrost's two
  raw-SQL consumers and the member's own Eye default
  to `~/.hermes/memory/runa_memory.db` (docket 51,
  docket 109).
- **Brunnr** — the house core's own well
  (`src/ember/well/`), part of ember-agent 0.2.0, MIT,
  the only one of the three with real development
  history in this tree (Batch-era + E-021/E-031/
  E-035/E-036/E-037/E-038) and the only one with a live
  consumer: the companion itself (chat loop, ingest,
  doctor, MCP, Strengr's tether — E-077 §6).
- **Neither member has an ORIGINS row** (E-003;
  docket 72). That gap is a register defect, repaired
  at E-196, and it cuts both ways in this verdict: no
  system here can claim the register's protection, and
  no verdict in this paper pretends ORIGINS decided
  anything. Provenance argues from packaging + git,
  stated above, and from nothing else.

Provenance's weight in the verdict: the two systems
proposed to stay are the house's own lines, with live
or reconcilable in-tree consumers. The system proposed
for retirement is the one whose home, maintainer, and
users are elsewhere — retirement from Ember loses the
project nothing it cannot re-import from upstream, and
loses upstream nothing at all.

## 4. The three crowns, each argued and refused

### 4.1 Unify on mempalace — refused on budget alone

Its recall is perfect and its layered wake-up and
temporal knowledge graph are real (E-077 §4.1). But it
fits no profile (§2), pays an embedding on every search
(~650–800 ms even for an exact phrase), spends ~2,900
lines of its own code on its store's repair forensics,
holds no importance/mood/current-truth face at the
drawer layer where its searched memory lives, and has
no consumer in the tree. Crowning it would make the
smallest supported machine unable to run the
companion's memory at all. **Refused.**

### 4.2 Unify on mimir-well — refused on meaning

It is the toaster-shaped, living, guarded, audited
one, and this verdict keeps it — as the living-facts
engine, not as the whole memory. As sole system it
fails the way people actually ask: paraphrase **0/9**,
a measured absence of any vector code anywhere in the
member. It holds conversations as a table, not as the
turn-shaped episodes the chat loop consumes, and the
core does not use it today, so crowning it also means
replacing the incumbent's working document/episode
store and re-homing semantic document search into a
member that has never had any. **Refused as a crown;
kept, bounded, as the living-facts engine.**

### 4.3 Unify on Brunnr — refused on life

It is the incumbent, it searches by word and meaning,
and it alone holds turns. As sole system it has no
answer — no face at all — for importance, mood,
current truth, decay, guard, or audit (E-077 §4.3:
"no decay or lifecycle, no importance or valence, no
validity/supersession, no guard or audit, no knowledge
graph"). Crowning it throws away the only living
memory the house has, including the lifecycle E-082
is ordered to build on. **Refused as a crown; kept,
bounded, as the document/episode store.**

## 5. The bounded shape — what each survivor owns

The verdict is **bound**: one face, two bounded
engines, stated territories, no merged store.

| Territory | Owner | Why (evidence) |
|---|---|---|
| Documents + chunks, word + meaning search over them | Brunnr | verbatim 20/20, paraphrase 9/9 vector, incumbent |
| Conversation turns (episodes) | Brunnr | only exact episode recall; 585 B/episode |
| Living facts: importance, mood, validity, supersession, current truth | mimir-well | only exact living rows; only current-truth view |
| Lifecycle: decay, consolidation, promotion | mimir-well | the only lifecycle in the house (E-077 §4.2) |
| Write guard + audit for living facts | mimir-well | guard.py / audit.py; no other system has either |
| Meaning search over living facts | **the face** (E-080's charge) | index-don't-merge proposal, §1 — to be proven at E-080 |
| The user's rights: inspect, correct, export, delete-total | **the face** (E-084) | one face = one place a user's rights are honoured whole |

Binding conditions the verdict lays on E-080:

1. **One canonical mimir-well path.** Docket 51's
   three-path disagreement is settled by the face:
   one default, named in the contract; other paths
   only as explicit configuration, never as competing
   defaults. Docket 109's four raw-SQL readers/writers
   (bifrost bridge, bifrost core, the Eye, Verdandi's
   check) are reckoned with there, with Part VIII
   consulted — none of them is broken by this verdict,
   and none is silently re-pointed by it.
2. **Stores are not merged.** No shape migration
   between Brunnr and mimir-well is ordered. E-081's
   migration question therefore reads: existing stores
   of each surviving shape stay native behind the
   face; the only "losing shape" whose stores need a
   migration or read-compat answer is mempalace's,
   and that answer waits on Volmarr's word (§6).
3. **Persona separation is a face property** (E-083),
   including docket 110: Brunnr's episode rows carry
   no conversation/persona column at the adapter
   layer, so the face — which tags above the adapter —
   owns the separation guarantee and must state it.
4. **Budgets bind the face.** Any E-080 design whose
   combined install + RAM + growth breaks a profile
   the bounded engines individually fit (toaster
   first) fails the verdict, however elegant. The
   index-don't-merge proposal in particular must be
   priced per profile before it is built; if its
   vector growth breaks the toaster, the toaster
   profile ships word-search over living facts and
   says so plainly (E-090's docs), rather than
   breaking the budget in silence.
5. **mimir-well hygiene rides along:** docket 108
   (its flask dependency bounded below only) is fixed
   at or before the E-092 gate, per its docket owner.

## 6. The retirement proposal — for Volmarr's word

**Proposed: that mempalace be retired honourably from
Project Ember.** This paper proposes; it does not
decide. Retirement is Volmarr's word (roadmap, Part V
headnote), and nothing in this slice — or in E-080
through E-091 — removes, moves, or marks the member
before he rules. E-092's gate records his word either
way.

What retirement would mean, if he gives the word:

- The member leaves the shipped companion tree in a
  later, separately-banked slice (E-091 owns the
  residue: docs marked truthfully, successor named —
  the successor being this verdict's bounded face).
- Its stores are answered by E-081 before any removal:
  a palace on a user's machine is either migrated to
  the bounded shape or read-compatible forever — the
  verdict does not choose that sub-answer; E-081
  argues it from fixtures and Volmarr's ruling.
- Honour is kept: MIT licence and upstream attribution
  stay wherever any of its code or docs remain in
  history; the retirement note names its upstream home
  (`github.com/MemPalace/mempalace`, per its own
  pyproject — E-012 §1) so any user can go to the
  source. Nothing about upstream is disparaged by this
  verdict: its recall was perfect in every row it has
  a face for. It is simply the wrong shape for a
  toaster — three orders of magnitude too heavy for
  the smallest profile this project exists to serve.

What retirement would **not** mean: deleting the
project from the world (it is upstream's, not ours),
rewriting history (its import and this campaign's
measurements stay in git), or touching any user's
existing palace store without E-081's answer.

**The fallback if Volmarr declines retirement:**
mempalace is then **bounded**, as follows — kept in
the tree as an optional, non-default, never-bundled
external archive adapter for laptop-class machines
only, with its true budget cost (no profile fits;
~403 MiB RAM; ~185 MB deps + ~88 MB model) stated
wherever it is offered (E-090), excluded from every
profile's install and from the companion's default
memory face, and re-argued only if its upstream shape
changes enough to change §2's numbers. The bounded
shape of §5 is identical under either ruling — the
face is built over Brunnr + mimir-well in both
worlds, so **E-080 is not blocked by this question.**

**The exact question put to Volmarr (once, plainly):**
mempalace — retire it from Ember honourably, as §6
proposes, or keep it bounded as an optional
laptop-class archive adapter under the fallback?
Until he answers, the fallback's *restraints* apply
by default (non-default, never bundled, not part of
the face) and the member itself stays untouched:
silence is never read as a retirement word.

## 7. What this verdict does NOT claim

- **No device truth.** Every number is the campaign VM
  under sibling load (E-078 §6). Tiny-hardware proof
  for the bounded shape is device work in later parts.
- **No archive-scale truth.** The harness corpus was
  22 items; behaviour at 10⁴–10⁵ items is E-088's soak.
- **No production-embedder verdict for Brunnr.** Its
  paraphrase row was measured with the harness's
  held-constant ONNX embedder; the production Ollama
  path (768-dim) was unreachable from the VM (E-078).
- **The index-don't-merge bridge is unproven.** It is
  a charged proposal for E-080, with a budget condition
  (§5.4), not a measured result.
- **mempalace's closets were not harness-built**
  (E-078 §6): closet boost could only have improved
  recall rows that were already perfect. Its costs —
  the ground of the retirement proposal — are
  unaffected by that gap.

## 8. Assignments the verdict makes

- **E-080** — implement the one face over the bounded
  shape of §5, under its five binding conditions;
  settle docket 51 there; prove or honestly fail the
  index-don't-merge bridge, priced per profile.
- **E-081** — stores: survivors stay native (no
  migration ordered); the mempalace-store answer
  (migrate vs read-compat-forever) argued and, if
  Volmarr has ruled retirement, executed — if he has
  not ruled, E-081 files the argument and waits.
- **E-082** — lifecycle on mimir-well's own machinery,
  now confirmed as the surviving lifecycle (§5).
- **E-083** — persona separation at the face, docket
  110 in hand (§5.3).
- **E-085** — reconcile Verdandi's records first at
  the live relationship: Verdandi ↔ mimir-well's file
  (E-077 §6), under the face's canonical path.
- **E-091** — the residue: after Volmarr's word, mark
  the retired-or-bounded system's docs truthfully.
- **E-092** — the gate: one face live, and **the
  verdict paper + Volmarr's word (or its recorded
  absence, with the fallback in force) on record**.
- **E-196** — ORIGINS gains rows for the members this
  verdict judged (docket 72), stating provenance as
  §3 records it, whatever the retirement ruling.

## Slice gate

Conformance: `tests/unit/test_memory_verdict_e079.py`
pins this paper (the verdict, its evidence numbers,
the three refused crowns, the proposal's exact status,
the fallback, and the inheritor assignments) and pins
the paper's central honesty: the mempalace member
still present and unmodified in the tree at banking.
Root-suite gate runs recorded in CAMPAIGN_STATE at
banking. No README touched; no member code touched.

*Filed by the E-079 slice, 2026-11-01. Next: E-080 —
the chosen shape implemented: one memory contract for
the companion, over the bounded shape this paper
verdicts — which does not wait on the retirement
question (§6).*
