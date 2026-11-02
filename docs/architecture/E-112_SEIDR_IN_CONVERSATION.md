# E-112 — Seiðr in Conversation: What the Engine Offers a Chat

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — sixth slice. Filed
2026-11-02 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), on
top of E-111 banked (812ec87) + its push record
(2d2ce06) + this slice's IN PROGRESS marker (cde53fb).
Every count below was measured this slice at this
tree (probes in `~/workspace/.verify-tmp/ember-e112/`).
No README was touched.*

## The verdict, in plain words — read this first

**A chat can now be offered seiðr, honestly: a verse
and a draw, both as data, in one new core module,
`src/ember/seidr_conversation.py`.** The verse offer
composes through the E-110 service, untouched, and
carries the facts the service served — form, the
world actually used, the lines, the seed — plus, on
request, the Old Norse forms of the verse's own
words, looked up in the member's lexicon as data.
The draw takes a seeded handful of words from one
world of the lexicon, with that world's kenning
where the world holds one, each item the lexicon's
own entry, stated as data.

**The honesty rule governs every shape this slice
builds: the engine computes; meaning is the
companion's voice, labelled as its own.** The engine
has no fate model and no interpretation of its own
(E-107 §2), so no offer here claims one: a draw is a
drawing of *words*, stated as exactly that, and a
reading enters only as text the companion itself
supplied, carried verbatim in a separate field under
its own label, never merged into the computed data.
The context block a chat consumes says so in its own
text — which part the engine computed, and that any
meaning present is the companion's, spoken in its
own voice, or that none has been spoken.

**This slice also rules docket 144, the two dead
config fields E-107 found and E-110 kept out of the
service contract.** `include_old_norse` is removed
from the member — it promised a rendering nothing
ever produced, in the config and in the renderer's
own signature alike — and the true road for Old
Norse in conversation is data: the forms the lexicon
itself carries, served on draws and on verse glosses
here. `topic` stands, corrected in the member to
what it always was: a label carried on the stanza,
never the "thematic hint" its comment claimed; a
conversation's theme rides on an offer the same way,
as a label only, shaping nothing.

## 1. The verse offer

`offer_verse(...)` composes through the E-110
service and carries its answer: form, world (the
world actually used, as the service reports it),
lines in reading order, the member's own rendering,
stanza count, seed. A service refusal — an unknown
form, an unknown world, a missing member — is
returned verbatim and no offer is built; the battery
pins the offered lines equal to the service's own
for the same seeded request, so this layer is a
carrying, never a second composer.

The elder design corpus (the Yggdrasil sibling
sheet for this member) asked for verse as a
*register seed* for chat: tonal material the
companion speaks from, never a reply pasted in its
place, and epigraphs only as an operator's opt-in.
The offer is that seed, in data: what a chat does
with it — speak from it, quote it under the labels
§4 keeps, or let it season a turn silently — is the
chat's own act, and §5 names what this slice did not
wire.

With `with_old_norse=True` the offer also carries
`glosses`: the Old Norse form of each of the verse's
own distinct words that the lexicon carries one for,
looked up in the member's lexicon (the verse's own
world first), in first-appearance order — plus the
coverage counted as `glossed` of `words_seen`
distinct words, so a partial gloss is stated as
partial. Probed at this tree: the seeded Asgard
verse (seed 7) glosses 10 of its 13 distinct words;
the rest are words the lexicon holds no form for —
the connectors above all (E-107 §3: exactly the
non-connector entries carry forms).

## 2. The draw

`draw_words(seed=..., world=..., count=...)` draws
`count` distinct words (default 3, at most 9) from
one world of the lexicon through the member's own
seeded lexicon, and the world's kenning under the
same seed where the world holds one. Each drawn word
is the lexicon's own entry as data: word, world,
part of speech, syllables, and its Old Norse form or
an honest `None`. Probed at this tree: seed 42 in
Asgard draws *fearless*, *Einherjar*, *Thor* and the
kenning *Kvasir's blood* (for poetry) — the same
draw the raw lexicon probe at this slice's opening
produced, and byte-equal across re-draws.

Three honesty shapes, each pinned:

- **A seed is required.** A conversation draw must
  be re-drawable to be checkable; an unseeded
  request is refused in words naming that reason,
  never silently made irreproducible. (E-113 owns
  the campaign-wide determinism ruling; this is the
  conversation layer's own discipline within it.)
- **An unchosen world is picked by the seed and
  reported.** The draw names the world actually
  drawn from — seed 42 unchosen draws from Vanaheim
  at this tree — and every word in it is that
  world's.
- **A world with no kenning states the absence.**
  Five of the nine worlds hold no kennings at all
  (E-107 §3); a draw from Helheim (seed 42:
  *linger*, *ghost*, *death*) carries `kenning =
  None`, and its context block says the world holds
  none — the gap is never filled from another
  world's hoard.

What a draw is *not*: the engine models no lots, no
wyrd, no fate state (E-107 §2), and this module
invents none. A draw offered to a chat is a drawing
of words with provenance — seed, world, source —
and nothing in its shape whispers that the words
were *meant*.

## 3. Docket 144 — RULED and executed in the member

E-107 probed both fields dead or misdescribed;
E-110 executed the contract note (neither is carried
by the service); this slice, the docket's owner,
rules their fate in the member itself:

- **`include_old_norse` — removed.** The config
  field was copied config-to-config and never
  consulted by composition (probed again at this
  tree's opening: seeded poems with the flag true
  and false are byte-identical), and
  `Poem.format()`'s parameter of the same name was
  accepted and silently ignored — a poem holds line
  text, not word entries, so the renderer never had
  the forms to show. Both dead shapes are removed
  from `seidr_engine/seidr/poet.py` in this slice:
  the field, its copy in `compose_poem`, and the
  format parameter, each removal commented at the
  site with the reason. No in-tree caller passed
  either (the CLI and the service construct configs
  without it; the member's suite never names it —
  all checked, not assumed), and the member's suite
  stands at 38 passed, unchanged. The *intent*
  behind the field is honoured where it can be
  true: Old Norse as data, from the lexicon that
  actually holds the forms (§1's glosses, §2's
  per-word forms).
- **`topic` — kept, and corrected to the truth.**
  The field stays: a stanza carrying the label of
  what it was composed under is a real, if small,
  thing. Its comment in `PoemConfig` no longer
  calls it a "thematic topic hint"; it states that
  composition never reads it. Probed at this tree's
  opening: two seeded poems differing only in topic
  are byte-identical and carry their different
  labels — a label, behaving as a label. The
  conversation layer's `theme` is the same shape
  under the same rule (§1, and the battery pins a
  themed and unthemed offer at one seed as the same
  verse).

Docket 144 is therefore CLOSED in scope: no config
surface in the member or the service any longer
promises an effect it does not have.

## 4. Readings, and the context block

Interpretation is data only in this labelled sense:
`attach_reading(computed, reading)` pairs a verse
offer or a draw with text the *caller* — the
companion — supplied, and the pair keeps the halves
apart forever: `computed` under the source label
`engine`, `reading` verbatim under `companion`. An
empty reading is refused loudly (a caller error,
raised in words): an empty label would dress
silence up as speech. This module contains no
function that turns computed data into a claim
about what it means — that absence is the slice's
central discipline, and the battery pins the labels,
the verbatim carry, and the unmerged halves.

`context_text(...)` shapes what a chat consumes:
one block whose header names the computed part as
the engine's data, the data itself (verse lines, or
the draw's words with their forms and its kenning
or stated absence, and any theme under the words
"Asked under the label"), then the honesty line —
*the engine computes; meaning is the companion's
voice, labelled as its own* — and finally either
the companion's reading under its own label, after
the honesty line, or the plain statement that no
reading has been spoken and the engine offers none.
A reader of the block — human or model — meets the
labels before any meaning, in the block itself.

## 5. What this slice did not build

- **No persona gate.** Whether a given persona may
  draw on the engines at all is E-117's slice (off
  by default for personae that shouldn't, there);
  this layer offers to any caller that asks, and
  claims no persona discipline.
- **No wiring into the live prompt assembly.** The
  context block's shape is defined and pinned here;
  Ember's per-turn prompt assembler does not consume
  it yet, and no chat path offers verse or draws
  unasked. Adopting the block in a live turn is a
  deliberate later act, not a side effect of this
  slice.
- **No epigraph machinery and no mood detection.**
  The sibling sheet's session-start vignettes and
  mood-chosen forms are designs, not commissions in
  this roadmap's Part VII lines; the caller chooses
  form, world, and seed, and this layer reports what
  was actually used.
- NOT PROVEN at this slice: any live conversation
  consuming an offer, any real-hardware figure
  beyond E-057's standing rows (Part VII's budget
  rows are E-114), and the Old Norse forms as
  scholarship (carried as the lexicon's data, as at
  E-107 — no slice in Part VII is charged with
  verifying them).

## 6. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in
`~/workspace/.verify-tmp/ember-e112/`.

- **Pre-doc standing batteries** (E-057's table,
  E-043's install weight, E-089's canon guard):
  the first 20 of the focal set below.
- **Focal battery** (this slice's own, 16 tests):
  **16 passed** in the default shape — the
  conversation layer needs no ephemeris, so there
  is no live shape and nothing skips.
- **Focal set** (the standing 20 + E-107's 11 +
  E-108's 11 + E-109's 19 + E-110's 18 + E-064's
  16 + E-111's 10 + this slice's 16 = 121):
  **111 passed, 10 skipped** in the default shape
  — the ten skips exactly the E-110/E-111
  batteries' live-ephemeris fixtures. Two pins
  were re-pinned consciously with attribution
  inside it: the E-107 battery's no-consumer pin
  (now guards exactly two core files naming the
  member — the service, and this slice's module
  as its first conversation consumer) and its
  member-size pin (§6's last bullet), and the
  E-109 battery's book-total pin.
- **Member suite** (seiðr, its own shape): **38
  passed, 0 failed** — unchanged across the
  docket-144 removals in `poet.py`.
- **E-057 re-pinned consciously with attribution:**
  src 135 files / 992,245 B (the new conversation
  module, plus the anchor comment's growth in
  `budgets.py` below), seidr_engine 11 / 104,387 B
  (the docket-144 removals in `poet.py`, net
  +431 B with their ruling comments), total
  131,676,841 B, miss unchanged 256,944 B — both
  published copies.
- **Run A:** **1 error, 20 skipped**, exit 2
  (docket 1, identical).
- **Run B:** **1570 passed, 6 failed, 44 skipped**
  — the 6 proven environment failures ONLY,
  name-for-name the standing set (Batch CDE ×3,
  G ×2, J ×1 — the sqlite_vec-missing family;
  = E-111's 1554 + 16 new, exact).
- **Run D:** **1778 passed, 0 failed, 17 skipped**
  CLEAN in one run (= E-111's clean 1762 + 16 new,
  exact).
- **GATE FINDING, fixed in scope — the install
  anchor was outgrown.** This slice's first full
  runs stood at Run B 1569 passed / 7 failed and
  Run D 1776 passed / 2 failed: the seventh and
  first failures were E-042's
  `test_install_size_rederived_fits_the_toaster` —
  the package alone now weighs 991,046 B, over
  E-041's measured all-in anchor of 978,843 B
  (package 729,802 B + dist-info + the sqlite-vec
  extra, measured when the package was smaller).
  The gate test's own instruction governs: the
  anchor must be re-measured, not quietly
  outgrown. It was, by E-041's own method — a
  fresh venv install of this tree on the VM,
  caches excluded: package 991,046 B (byte-
  identical installed and in source, the method's
  identity holding), dist-info 84,617 B,
  `sqlite-vec` 0.1.9 at 199,548 B with its
  dist-info — **1,275,211 B in all (1.22 MiB)**.
  `MEASURED_INSTALL_BYTES` in `ember.budgets`
  now carries the re-measured figure with the
  founding measurement recorded as superseded in
  its comment; the budget book's founding line
  and anchor appendix carry it likewise, and the
  E-041 battery's two pins were re-pinned
  consciously with attribution — including the
  honest one: the core no longer installs in
  under a MiB, and still fits the toaster's
  2 MiB ceiling with room. The growth itself —
  the package up 261,244 B across Parts II–VII,
  the extra up with its releases — is **docket
  159**, owned by E-114 (Part VII's budget rows
  weigh this part's contribution) and E-197 (the
  claims audit): no document may repeat the
  under-a-MiB install claim from here.
- The first Run D also carried one E-087
  kill-mid-write failure (`[2]`), and that file
  failed once more in isolation under load
  (`[1]`) before passing whole twice in a row —
  the timing family, on a file this slice does
  not touch; the final Run D above is clean with
  it. The gate's second Run B attempt died at
  ~9% when the recurring home-quota EDQUOT flap
  killed its own log flush (`OSError: [Errno
  122]`, an INTERNALERROR with 183 passed and no
  failure in the completed portion); the banked
  Run B above ran with its log on `/dev/shm`,
  the campaign's standing flap pattern. Nothing
  was deleted by this campaign.

## Carried forward

- Part VII continues. Next: E-113 (determinism +
  offline: both engines fully local, reproducible —
  seeded and date-pinned fixtures; carrying docket
  146, the one-seed-semantics ruling, and docket
  153's offline ruling).
- Docket 144 CLOSED in scope here. Dockets 143 and
  148 stand with E-120 (their contract notes
  executed at E-110); docket 146 stands with E-113;
  docket 153's declaration stands carried at E-110
  with its offline ruling at E-113. Docket 159 NEW
  (§6's gate finding — the core's install growth,
  978,843 B → 1,275,211 B all-in as re-measured)
  stands with E-114 and E-197.
- NOT PROVEN at this slice: a live chat consuming
  an offer, a persona gate (E-117), any scheduled
  or unasked offering, any real-hardware figure
  beyond E-057's rows.

*Filed by the E-112 slice, 2026-11-02. Next:
E-113 — determinism + offline.*
