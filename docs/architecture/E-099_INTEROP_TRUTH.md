# E-099 — Interop Truth: Can the Two Kistas Exchange Entries?

*Project Ember campaign, Part VI (Kista of the Toaster),
seventh slice. Roadmap line: "Interop truth: can the
two Kistas exchange entries? Studied; if yes, a one-way
export/import with verification; if no, the boundary
doc (E-011) gains the technical reason". Studied
2026-11-01 on branch `yrsa/ember-road-build` in the
campaign's own clone, building on E-098's entry-kind
partition. Method: the toaster program's every
movement road (`export`, `import`, `backup`, `restore`
in `kista/scripts/credstore.py`) read in code and then
actually run between scratch vaults holding synthetic
entries only (raw logs in `~/workspace/.verify-tmp/
ember-e099/`). The ai-folder Kista was not accessed,
run, or read — the E-011 boundary governs every word
below about that side: what is said of it is graded
RECORDED, not MEASURED, exactly as E-011 left it.*

## Headline — read this first, in plain words

**No. The two Kistas cannot exchange entries today —
not by any road this campaign may use, and the one
road that mechanically works is forbidden for real
entries.** The answer is the roadmap's "if no" branch:
no one-way export/import is built, and the boundary
doc (E-011) gains the technical reason as an addendum
filed with this slice. In plain words, why:

- **Every encrypted road needs the *same* key on both
  sides.** An export is a byte-for-byte copy of the
  vault's encrypted blob and carries no key with it.
  Importing it into a vault with a different key fails
  in the program's own words — "you must import into a
  vault that shares the same encryption key" — proven
  by probe (§3). Two separate Kistas have two separate
  keys by definition; that is what makes them two
  vaults and not one. Handing over the key file is not
  interop: it hands over *everything* — every entry in
  the vault, every auto-backup, and every older blob
  ever pushed by `github-backup` (E-095's harvest
  shape), forever. A key is a vault's whole life, not
  a postage stamp.
- **No selective crossing exists.** The movement roads
  are whole-vault only: there is no kind filter (kept
  and other-road entries cross right along with the
  toaster set — proven by probe, §3), no per-entry
  choice, no program-tag handling, and no re-encryption
  for a recipient. E-098 ruled that the toaster set —
  passwords, tokens, URLs, notes — is the only set
  whose crossing this campaign may even propose. A
  road that moves everything, or nothing, is a backup
  road. It is not a bridge between two programs.
- **The other side's current format is NOT MEASURED.**
  What the records establish is ancestry: the toaster
  copy is a 2026-05-21 snapshot of the same family the
  ai-folder program descends from (E-011 §3). The
  living line's GitHub head had already moved a month
  past that snapshot when E-011 recorded it, and it
  has kept its own road since. Ancestry is not format
  compatibility: claiming the two could exchange
  entries because they share grandparents would be
  inventing the very fact this slice was commissioned
  to establish. E-011 §6 saw this coming and named the
  only two honest sources for that fact — this
  campaign's records, or Volmarr's word. The records
  hold lineage only, and no word on format
  compatibility stands on record.
- **The one differing-key road that works is
  plaintext.** A plain (unencrypted) `backup` from one
  vault restores cleanly into a vault holding a
  different key — proven by probe (§3) — because
  `restore` reads plain JSON before it ever reaches
  for a key. That is not a loophole to celebrate: it
  moves secrets as clear text, which the custody law
  (E-093) forbids for credentials outright and E-095
  already judged "not defended". For real entries
  between the two Kistas it is a forbidden road, and
  for synthetic entries it proves only that the format
  *inside* one program is portable — which was never
  the question.

So the boundary stands exactly where E-011 drew it,
now with its technical reason on file (§5). What a
real bridge would require is written down as
requirements (§4) — for the day the other side's
format is measured by its own keeper or established
by Volmarr's word, and not one day before.

## 1. The movement roads, as the code stands

All four roads stand in the toaster program today
(E-094 §4 mapped them; this slice judged them as
crossings):

| Road | What actually moves | Key requirement | Selectivity |
|---|---|---|---|
| `export` → `import` | a byte-copy of `vault.json.enc`, merged into the receiving vault (skip / `--merge` / `--overwrite`) | **the same Fernet key**, or import refuses in words | none — every entry in the blob |
| `backup --encrypt` → `restore` | the whole vault as JSON, Fernet-encrypted under the vault key, inside a `{kista_version, exported_at, platform, vault}` envelope | **the same Fernet key**, or restore cannot read the file | none |
| `backup` (plain) → `restore` | the same envelope as **clear-text JSON** — values readable by anyone who can read the file | none — restore parses the JSON first | none |
| `github-backup` | an encrypted blob pushed to a git repo | the same key opens every pushed blob, past and future | none — and E-101 owns its verdict (docket 135) |

Three facts about these roads matter more than any
one row:

- **No road carries a key, wraps a key, or re-encrypts
  for a recipient.** There is no transfer passphrase
  for entries, no recipient-key shape, and no key
  export command anywhere in the surface (E-094's 32,
  grown to 35 at E-098 — none of the growth touched
  movement). E-096's passphrase wraps the vault key
  *for this vault's own unlock on this machine*; it
  is a local door, and nothing in its shape addresses
  a copy to another program.
- **No road knows about kinds or programs.** The
  import and restore merge loops copy entries as they
  stand; neither references the E-098 partition
  (`TOASTER_ENTRY_TYPES` and its kin) nor E-097's
  program tag. A shared-key crossing therefore moves
  other-road kinds *into* a vault with no notice at
  all — the silent merger E-098 exists to refuse,
  arriving by the back door. Any future bridge must
  be kind-selective by construction, not by promise.
- **A third shape already haunts the tree.** E-011's
  hazard H2 stands unrepaired in its Part IV home:
  Verdandi's Mímir check expects a Kista vault as a
  SQLite file at `~/.kista/vault.db` that neither
  Kista writes. Even *inside this one tree*, "a Kista
  vault" names at least two incompatible formats.
  Format sameness is something that must be proven
  per pair of programs, never assumed from a name —
  which is §2's whole argument in miniature.

## 2. The other side — what is known, and what is not

**RECORDED (E-011 §2, from the roadmap and the
campaign's purplelongship records of 2026-10-30/31;
not re-measured here, that side never accessed):**
the ai-folder Kista is the living line of the same
credential family, kept current with the standalone
GitHub repo `runafreyjasdottir/kista` (head recorded
2026-10-30 as `54e31f1090`, pushed 2026-06-07 — a full
month of movement after the toaster copy's single
2026-05-21 import commit). It holds real entries
under the Hermes/Runa side's custody. Both sides
answer to "v2.0" (E-011 hazard H6).

**NOT MEASURED, and therefore not claimable:**

- its current vault format — file shape, envelope,
  entry schema, and any format version it now writes;
- its current crypto shape — whether the Fernet
  whole-vault shape the snapshot shares is still its
  shape, and what key custody it now uses;
- whether any of its entry kinds have gained or lost
  fields since the snapshot — the toaster set's four
  kinds included;
- whether it has any import road of its own, and what
  that road would accept.

A one-way export/import built against the 2026-05-21
snapshot's format would be aimed at a target last
seen five months ago, on the far side of a boundary
this campaign may not cross to look. If the living
program has moved its format by even one required
field, the bridge lands as silent corruption or
silent refusal in someone else's real vault. That is
why "studied; if yes" cannot be answered yes from
this side of the boundary: the yes-condition — a
measured format on both sides — is not met, and no
amount of toaster-side proving can meet it alone.

## 3. What was proven (probes, synthetic entries only)

Three scratch vaults (full log
`~/workspace/.verify-tmp/ember-e099/probes.log`):
**A**, a source vault with its own key, holding six
synthetic entries — one `credential`, one `apikey`,
one `url`, one `note` (the toaster set), one
`identity` (kept), one `astrology` (other road);
**B**, a destination vault with a *different* key;
**C**, a destination vault *sharing A's key* (A's key
file placed before C's first init — the "same vault,
second folder" shape, not a second program).

- **Export is the blob itself.** A's `export` output
  is byte-identical to A's `vault.json.enc`; it
  contains no plaintext value and no key material.
  Whatever receives it receives exactly a locked box
  with no keyhole card.
- **Different key: the crossing refuses.** B's
  `import` of A's export exits 1 with the program's
  own words ("Failed to decrypt … You must import
  into a vault that shares the same encryption
  key."), and B's vault afterwards holds **nothing**
  from A — the refusal is total, no partial merge.
- **Shared key: everything crosses, unfiltered.**
  C's `import` of the same export exits 0, and all
  six entries read back whole in C — the four toaster
  kinds, the kept `identity`, and the other-road
  `astrology` chart alike, with no notice and no
  kind or program distinction. This proves same-key
  portability (a backup's virtue) and, in the same
  stroke, that the road is not a bridge: it cannot
  carry *only* what E-098 permits to cross.
- **Encrypted backup: same wall.** B's `restore` of
  A's `--encrypt` backup exits 1, unreadable under
  B's key, and B still holds nothing from A.
- **Plaintext backup: the forbidden road works.**
  A's plain `backup` file contains the synthetic
  password in clear text (the probe read it straight
  from the file), and B's `restore` of it exits 0 —
  afterwards B reads A's synthetic credential whole,
  under B's own different key. The crossing is real
  and wholly keyless. It is recorded here as a fact
  about `restore`, handed to E-101 as docket 138:
  the backup verdict there must reckon with the
  plain road being, mechanically, an *unauthenticated
  whole-vault transfer* to any vault that restores
  it.
- **No probe touched interop with the ai-folder
  Kista**, because there is none to probe: no shared
  key exists, no measured format exists, and E-011
  rule 5 forbids moving entries in any case. The
  probes prove the toaster side's roads; the verdict
  follows from what those roads are.

## 4. What a real bridge would require (requirements, not built)

Filed so a future slice — or the other Kista's own
keeper, from their side — can build the bridge the
day its preconditions are honestly met:

1. **A measured target.** The ai-folder program's
   current vault/entry format, established by its
   keeper's measurement or by Volmarr's word —
   versioned, so the bridge can refuse a format it
   does not recognise instead of merging into one.
2. **Volmarr's word for the crossing itself.**
   E-011 rule 5 ("no entry ever crosses") is his
   boundary law; a bridge is an exception to it, and
   exceptions to a custody law are the owner's to
   grant for a named road, in words.
3. **Toaster-set only, by construction.** The
   transfer carries `credential`, `apikey`, `url`,
   `note` entries and no others — enforced in the
   export code against `TOASTER_ENTRY_TYPES`, with
   every excluded entry counted and named by kind in
   the export's own report (never silently dropped,
   never silently carried).
4. **Its own locked box.** The transfer file is
   encrypted under a one-time transfer passphrase
   (the E-096 scrypt derivation is the in-tree shape)
   or a recipient key published for the purpose —
   never the vault key of either side, never plain
   text, and a copied transfer file without its
   passphrase opens nothing (the E-096 probe shape).
5. **Verification with a receipt.** Import proves,
   per entry, that what arrived is what was sent (a
   digest over the entry as exported, checked on
   import), and reports in plain words: how many
   entries arrived, how many were new, how many were
   skipped as already present, and any that failed —
   collisions skipped by default, as `import` already
   behaves. No silent overwrite road.
6. **Program tags handled in the open.** A crossed
   entry's E-097 program tag is either stripped (the
   entry becomes the receiving owner's own) or mapped
   by an explicit rule stated in the transfer's
   report — never trusted across the boundary as-is,
   because a program name is an identifier, not a
   credential (E-097's honesty line).

Until requirements 1 and 2 both stand, requirements
3–6 are a design on file, and Ember docs must not
describe the two Kistas as able to exchange entries
in any tense.

## 5. The boundary doc gains its reason (E-011 addendum)

Per the roadmap's "if no" branch, this slice appends
an addendum to `docs/audit/E-011_TWO_KISTAS_BOUNDARY.md`
— extending, never rewriting: §5's rules and §6's
inheritances stand exactly as filed, and the addendum
records (a) the verdict, (b) the three technical
reasons in their shortest form — same-key-or-nothing
on every encrypted road; whole-vault roads with no
kind selectivity; the other side's format unmeasured
since a snapshot five months and one upstream month
behind the living line — and (c) the pointer to §4
above as the bridge's preconditions. E-104, which
files the boundary doc's final form, inherits the
addendum as part of the doc it finalises.

## 6. Standing findings handed on

- **E-100** is untouched by this verdict: the Ember
  core binding is a program calling *its own*
  machine's toaster-Kista under E-097 — no crossing,
  no second program, no bridge required or implied.
- **E-101** inherits docket 138 (NEW): `restore`'s
  plain-JSON road is an unauthenticated whole-vault
  transfer between different-key vaults (§3) — the
  backup/restore verdict there judges that shape
  alongside docket 135 (`github-backup` history and
  privacy), which stands as E-095/E-098 left it.
- **E-104** inherits the boundary doc *with* this
  slice's addendum (§5) and the final-form duty for
  both; **E-105** inherits the naming consequence:
  user-facing words must never let "your Kista" blur
  two programs that cannot exchange so much as one
  entry.
- **E-187** inherits the honesty line for the audit:
  "the two Kistas cannot exchange entries" is the
  only true sentence about interop until §4's
  requirements 1–2 stand; any document, member doc
  included (docket 130's ground), claiming or
  implying an exchange road is a defect there.
- **E-204** inherits the re-ask: if the other side's
  format is ever measured and Volmarr ever grants
  the crossing, §4 is the slice that gets built —
  presented there as a candidate, never assumed.

## Slice gate

Focal battery `tests/unit/test_kista_interop_e099.py`
pins this record: the verdict and its reasons in this
doc, the addendum's presence in the boundary doc, the
code shape of every movement road (the same-key
refusal in the program's own words; the export's
byte-copy shape; no kind or program filter in the
import/restore merge loops), and the §3 probes —
different-key refusal total and clean, shared-key
crossing whole and unfiltered, encrypted backup
refused across keys, the plaintext road's keyless
crossing proven and named forbidden. No program code
changed in this slice: the verdict is *no*, and a
"no" builds nothing. (The one test-tree change is
governance, not program code: the E-089 canon guard's
allowlist gains this slice's battery as its sixteenth
file, consciously, with its governance-needle reason
recorded — the act that guard exists to force, as at
E-090–E-093.) Member suite and root gates are
recorded in the campaign state file at banking; the
E-057 member table is re-measured there (the kista
member itself is untouched, so its row stands as
E-098 pinned it — verified, not assumed).
