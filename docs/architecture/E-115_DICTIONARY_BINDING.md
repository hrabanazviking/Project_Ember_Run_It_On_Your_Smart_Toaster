# E-115 — The Dictionary Binding: Cleasby-Vigfusson as a Lookup Service

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — ninth slice.
Filed 2026-11-02 on branch `yrsa/ember-road-build`
in the campaign's own clone
(`~/workspace/ember-build`), on top of E-114 banked
(f48bbd4) + its push record + this slice's IN
PROGRESS marker. Every count below was measured
this slice at this tree; the real dictionary data
was fetched fresh from the package index into an
isolated scratch dir (the E-108 isolated-deps
discipline) and is kept for the gate at
`~/workspace/.verify-tmp/ember-e115/`. No README
was touched.*

## The verdict, in plain words — read this first

**The companion can now ask the real Cleasby &
Vigfusson dictionary what an Old Norse word means,
and be answered in the dictionary's own words —
where the dictionary carries the word. Where it
does not, the binding says so. Where the dictionary
data is not there at all, the binding refuses in
plain words and invents nothing.**

The binding is one new core module,
`src/ember/dictionary.py`: a typed lookup and a
typed search over the dictionary's 35,207 entries
(46,162 definitions), answered exactly as the data
prints them. *Maðr* returns the dictionary's own
MAÐR entry, all ten definitions. *Seiðr* returns
both of the dictionary's entries — the fish first,
then the magic — because the book carries both and
the binding does not pick winners. A word asked
for in the wrong letters (*madr*, with a plain d)
is an honest miss, stated as one: the dictionary's
alphabet is not folded into ASCII to manufacture a
hit.

**Two findings about the member itself, both
docketed to E-116.** First (docket 160): the
member as tracked cannot run its own pages — every
page and API route imports a service layer
(`lib/services/…`, `lib/utils/…`) that is **not in
the tracked tree at all** (no `src/lib/` path
exists in `git ls-files`, though 29 tracked files
under `src/` import it). Second (docket 161): the
dictionary text itself is not tracked either — it
lives only in the member's pinned npm data package
(`cleasby-vigfusson-dictionary ^1.0.16`), fetched
at install time into `node_modules/`, which this
tree has never had. The binding therefore binds
the data in the package's own shape, at the place
an installed member would keep it, and E-116
(dictionary data hygiene) inherits the provenance
and the missing layer as its opening evidence.

**The price, priced honestly (E-114's discipline).**
The book is not toaster food. The data file alone
is 10,656,938 bytes — it fits only the laptop's
install ceiling. Loaded and indexed in memory, a
lookup peaks at 59.7 MiB: inside even the toaster's
64 MiB turn ceiling, but at 93% of it, leaving a
toaster companion almost no room to be itself in
the same turn. The honest shape: **the dictionary
is a laptop-carried, phone-and-up-served member**;
on smaller profiles it is an extra a carrier
chooses with open eyes, exactly like E-114's
local-time road. Lookup itself, once the book is
loaded, is one dict read; loading takes about a
second on this contended VM and happens once per
data path.

## 1. The charter and the method

- **The roadmap's E-115 line** — "The dictionary
  binding: cleasby-vigfusson as a lookup service
  for the companion (Old Norse words in
  conversation, answered from the real
  dictionary)": Part VII's third member joins the
  two engines. E-110 bound the engines as typed
  services; E-112 gave seiðr a conversation layer.
  This slice binds the dictionary the same way —
  a typed service (`src/ember/dictionary.py`) plus
  the labelled conversation block a chat consumes
  (`answer_text`) — under the same honesty rule:
  the source speaks in its own voice, labelled;
  meaning for the conversation is the companion's.
- **Method.** The member's own consumption shape
  was read from its tracked code (entry shape
  `{word, definitions}` from its components and
  pages; the three search criteria and the
  150-result cap from its search form and search
  API route). The data package the member pins
  was fetched fresh (`npm pack
  cleasby-vigfusson-dictionary@1.0.16`, tarball
  7,586,772 B) into isolated scratch, never into
  the tree; every live figure below is measured
  from that copy. Behaviour is proven on a small
  synthetic book in the dictionary's own shape
  (default test shape) and against the real book
  (live test shape, guarded by the isolated copy's
  presence, the E-110 pattern).

## 2. The member as found

- **Shape.** A Next.js web frontend
  (cleasby-vigfusson-next, E-002) for the 1874
  Cleasby & Vigfusson dictionary: pages for words,
  letters and search; components rendering an
  entry's `word` and `definitions`. Tracked:
  170 files / 24,221,782 B (E-057's standing row,
  unchanged by this slice) — almost all of it
  test snapshots and site furniture; **no data**.
- **Docket 160 — the service layer is missing.**
  Twenty-nine tracked files under `src/` import
  `lib/services/…` or `lib/utils/…` (the word page
  alone imports three service modules and two
  utility modules); `git ls-files` carries no
  `src/lib/` path at all. As imported, the member
  cannot build or serve a single page. Whether
  the layer was never imported or was lost is not
  decidable from this tree; it is recorded, not
  repaired — rebuilding the web member's service
  layer is not this binding's road, and E-116
  owns the member's hygiene. (The member's Jest
  suite therefore remains NOT MEASURED — docket
  78, standing since E-005 — for the same reason:
  there is nothing here to run it against.)
- **Docket 161 — the data is external.** The
  dictionary text (35,207 entries) exists only as
  JSON inside the npm data package the member
  pins. ORIGINS.md does not name the dictionary
  (E-003's concordance carries what provenance
  the tree states); the package itself is MIT
  (its LICENSE matches the member's, E-007), and
  the 1874 text is public domain by the member's
  own footer. Provenance per ORIGINS is E-116's
  chartered work; this slice states what it read,
  in §3, and files the gap.

## 3. The data, as read

From `cleasby-vigfusson-dictionary@1.0.16` (the
member's pin, re-read from its `package.json` by
this slice's battery):

| What | Measured |
|---|---|
| Package tarball | 7,586,772 B |
| `json/cleasby-vigfusson.json` (markup flavour) | 11,742,655 B |
| `json/cleasby-vigfusson-no-markup.json` (plain flavour) | 10,656,938 B |
| Entries | 35,207 |
| Definitions across all entries | 46,162 |
| Headwords (lowercased) with more than one entry | 458 |
| Entry shape | `{word: str, definitions: [str, …]}`, every entry, no exceptions |

The binding reads the **no-markup** flavour: a
conversation is spoken, not rendered, and the
markup flavour's `<i>`/`<strong>` tags are the web
member's furniture. Headwords are printed in the
dictionary's own mixed casing (MAÐR in capitals,
freyja in lowercase) and are served in that casing,
verbatim.

## 4. The binding

`src/ember/dictionary.py`, standard library only:

- **`lookup_word(word)` → `LookupResult`** —
  every exact entry for a headword: matching is
  case-insensitive (one lowercase index, built
  once at load) and character-exact beyond case.
  Homographs all serve, in dictionary order
  (458 such headwords; *seiðr* the fish and
  *SEIÐR* the magic are the slice's pinned pair).
  A miss is a served empty result with a `note`
  stating the dictionary carries no such headword
  and that its letters are not folded — never a
  refusal, never a neighbour.
- **`search_dictionary(query, criteria, limit)` →
  `SearchResult`** — the member's own three
  criteria (`headword`, `definitions`, `all` =
  both), substring matching, dictionary order,
  capped at the member's own 150 by default, with
  the true `total` always counted (a headword
  search for *maðr* finds 503 and says so; a
  definitions search for *witchcraft* finds 26,
  BRAGÐ first).
- **`answer_text(result, asked)`** — the labelled
  block a conversation consumes: the source named
  (`SOURCE`: the 1874 dictionary, through the data
  package, no-markup text), the entries quoted
  verbatim, and a closing line keeping the voices
  separate — the dictionary's words are quoted;
  what they mean here is the companion's to say
  (E-112's honesty rule, applied to a book).
- **The data road.** `default_dictionary_data_path()`
  names the member's own install shape
  (`cleasby-vigfusson-old-norse-dict/node_modules/
  cleasby-vigfusson-dictionary/json/cleasby-
  vigfusson-no-markup.json`); an explicit
  `data_path` or the `EMBER_DICTIONARY_DATA`
  environment name overrides it. Data is loaded
  lazily, once per path, shape-checked record by
  record (a differently-shaped file is refused as
  not this dictionary — no guessing, no partial
  book). Absent or malformed data refuses in words
  naming the path and the package. Nothing is
  written; nothing is fetched; the network is
  never touched.
- **Prices (measured, contended VM).** Load +
  index ≈ 0.93 s once; a lookup after load is a
  dict read (the index holds 34,745 keys);
  a definitions search scans the book (26
  witchcraft hits found in one pass). Peak memory
  with the book loaded, one lookup and one
  definitions search done: **59.7 MiB** (VmHWM,
  median of three fresh processes; the bare
  interpreter in the same probe shape is
  10.0 MiB). Judged live by the battery against
  `ember.budgets`: the data file fits only the
  laptop install ceiling; the loaded peak sits
  inside every turn ceiling, the toaster's at 93%.

## 5. What is NOT built

- No correction of the dictionary's data — OCR
  errors, the 458 homograph keys' consistency,
  duplicate or garbled entries, and the provenance
  record are **E-116's** chartered road (dockets
  160 and 161 stand with it as opening evidence).
- No letter browsing, similar-words, abbreviations
  or crosslinks — the web member's shapes, whose
  service layer is the missing one (docket 160).
- No persona gate on who may ask (E-117), no
  wiring into live prompt assembly — a chat adopts
  `answer_text` deliberately, as with E-112.
- The member itself is untouched: no `node_modules`
  was created in the tree, no member file changed,
  no README touched anywhere.

## 6. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in
`~/workspace/.verify-tmp/ember-e115/`.

- **Focal battery** (this slice's own, 20 tests):
  **16 passed, 4 skipped in the default shape**
  (the four live-book fixtures skip without the
  isolated data copy) and **20 passed in the live
  shape** (the isolated real book present).
- **Focal set** (the standing gate batteries —
  E-041, E-042, E-043, E-057, E-089 — plus Part
  VII's batteries E-107…E-115, run as one list):
  **162 passed, 15 skipped** — the skips are 13
  live-ephemeris fixtures (E-110 ×5, E-111 ×5,
  E-113 ×3, each guarded on the isolated ephemeris
  dir, which this gate did not put on the path)
  and E-042's two sqlite_vec-extra guards. This
  slice's own battery ran live inside the set
  (the isolated book present) at 20 passed.
- **Member suite:** none runnable — the dictionary
  member's Jest suite remains NOT MEASURED
  (docket 78; §2 gives the reason: its service
  layer is absent from the tree). The seiðr member
  suite stands at 38 passed where Part VII's gate
  needs it (run as part of this slice's focal set).
- **E-057 re-pinned consciously with attribution:**
  src 136 files / 1,011,519 B (the new binding
  module, 17,500 B), total 131,698,183 B, miss
  unchanged 256,944 B — both published copies; the
  E-109 battery's book-total pin re-pinned
  likewise with attribution.
- **Run A:** **1 error, 20 skipped**, exit 2
  (docket 1, identical).
- **Run B:** **1619 passed, 6 failed, 47 skipped**
  — the 6 proven environment failures ONLY,
  name-for-name the standing set (Batch CDE ×3,
  G ×2, J ×1 — the sqlite_vec-missing family;
  = E-114's 1599 + 20 new, exact).
- **Run D:** **1827 passed, 0 failed, 33 skipped**
  CLEAN (= E-114's 1807 + 20 new, exact) — on the
  second attempt: the first attempt died at ~63 s
  on an INTERNALERROR whose root is this tick's
  recurring home-quota EDQUOT flap striking the
  run's own log flush (Errno 122, in the run's
  recorded traceback); the banked run wrote its
  log to /dev/shm, the campaign's standing flap
  pattern, on the identical tree.

## Carried forward

- Part VII continues. Next: E-116 (dictionary data
  hygiene: the dictionary member's data provenance
  per ORIGINS; lookup correctness fixtures) —
  dockets 160 and 161 stand with it as opening
  evidence, and docket 78 (the member's unmeasured
  Jest suite) beside them.
- NOT PROVEN at this slice: any real-hardware
  figure for the loaded book; a smaller in-memory
  shape for the book on toaster-class hardware
  (a paged or indexed-on-disk road is a future
  slice's design, not a claim here); the member
  web app running in any shape.

*Filed by the E-115 slice, 2026-11-02. Next:
E-116 — dictionary data hygiene.*
