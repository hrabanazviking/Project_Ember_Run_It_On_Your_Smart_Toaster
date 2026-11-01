# E-098 — Entry Kinds: the Toaster Set

*Project Ember campaign, Part VI (Kista of the Toaster),
sixth slice. Roadmap line: "Entry kinds: passwords,
tokens, URLs, notes — the toaster set; the ai-folder
Kista's wider ambitions (states, prompts, habits)
recorded as its road, not silently merged". Built and
measured 2026-11-01 on branch `yrsa/ember-road-build`
in the campaign's own clone, at campaign commit
6ad5680 (E-098 IN PROGRESS), building on E-097's
per-program access. Method: `kista/scripts/
credstore.py` read whole at the E-094 map and again
here; every kind's add road — the general
`add --type` road and its shortcut road — actually
run against scratch vaults holding synthetic entries
only (raw logs in `~/workspace/.verify-tmp/
ember-e098/`). The ai-folder Kista was not accessed,
run, or read — the E-011 boundary governs every word
below about that side: its ambitions are recorded
from the roadmap's own words and the in-tree
snapshot's evidence, graded RECORDED, not MEASURED.*

## Headline — read this first, in plain words

**The toaster-Kista has four kinds of its own, and
from today the program itself knows which four.**
In plain words:

- **The toaster set is passwords, tokens, URLs,
  notes** — the roadmap's own four words, standing
  in the code as the kinds `credential`, `apikey`,
  `url`, and `note`. These are what this program
  exists to hold on tiny hardware. Ember's own
  binding (E-100) is built against two of them, and
  the user docs (E-104) will be written against
  these four and no others.
- **Five more kinds stay, and are named as kept,
  not promised.** One-time-code secrets, licence
  keys, machine keys, certificates, and identity
  records are credential-family kinds the imported
  program already holds well. They stay because
  removing a kind would strand every entry of that
  kind already sitting in someone's vault, for no
  gain at all. Kept is not the same as promised:
  Ember builds nothing on them.
- **Five kinds belong to the other road, and the
  program now says so out loud.** Astrology charts,
  character sheets, rune readings, tarot readings,
  and documents are an agent's life-records — the
  ai-folder Kista's wider ambitions made visible in
  this tree's snapshot. They are recorded here as
  *its* road, not silently merged into the toaster
  set. An entry of one of these kinds already in a
  vault keeps working exactly as before — reading,
  changing, and removing one says nothing special,
  because keeping someone's entries is custody, not
  merger. But a **new** entry of one of these kinds
  is announced in words at the moment it is added:
  the add succeeds exactly as given, and the program
  prints that the kind is not one of the
  toaster-Kista's own kinds and is kept here exactly
  as given, nothing merged or changed.
- **Docket 50 is CLOSED** — the three Hermes-shaped
  commands are judged one by one in §5, not with
  one blanket: `add-soul` and `add-cron-backup`
  belong to the other road and now announce
  themselves the same way; `github-backup` is not
  an entry-kind question at all and stays E-101's.
- **Dead roads were found and fixed (docket 137,
  CLOSED in scope).** Probing every kind's add road
  proved that four kinds could not be added by the
  general road at all, documents could not be added
  by either road — their required fields were
  unreachable from the flags the program offered —
  and the `add-url` shortcut the program's own
  usage text advertises did not exist at all, for
  one of the toaster's own four kinds. A kind that
  cannot be added is not "kept working", so this
  slice fixed the roads before judging the kinds
  (§6). Every one of the 14 kinds is now proven
  addable by its general road and by its shortcut
  road, the restored `add-url` included.

## 1. The toaster set — the four kinds of its own

| Plain word | Kind | Its required field | What a normal person keeps in it |
|---|---|---|---|
| passwords | `credential` | none | a login: username, password, email, the site's address |
| tokens | `apikey` | the key itself | an API key or token a program uses to prove itself |
| URLs | `url` | the address | a link worth keeping, with a title and a line about it |
| notes | `note` | the text | a small piece of writing that must not be lost |

The set stands in the code as `TOASTER_ENTRY_TYPES`
beside the schemas it classifies, so the judgment
cannot quietly drift away from the program: the
focal battery derives the partition from the code
and proves every kind stands in exactly one of this
slice's three sets (§7).

Why these four and no more: they are the kinds a
person on the smallest machine needs to get into
their own things — into an account (passwords),
into a service their companion talks to (tokens),
back to a place (URLs), and to not forget a thing
(notes). E-100 inherits exactly this: the companion
fetches its model/API credentials as `credential`
and `apikey` entries under E-097's program name —
both toaster kinds, so the binding never reaches
outside the set this slice promises.

## 2. Kept kinds — in the program, not the promise

| Kind | Required field | Why it stays |
|---|---|---|
| `totp` | the secret | the one-time-code half of a password; people keep it beside the login it protects |
| `license` | the key | a bought licence key is a token a person pastes; the chest is its natural home |
| `sshkey` | the key file | a machine key is a credential for a machine the owner administers |
| `certificate` | the cert file | the machine key's other half; same reasoning |
| `identity` | none | a person's own identity record, kept by that person in their own chest |

The set stands in the code as `KEPT_ENTRY_TYPES`.
The reasoning is custody, stated once and plainly:
these kinds were in the imported program, they
work (the member suite has tested them since long
before this campaign), and entries of these kinds
may already sit in vaults this campaign has never
seen. Deleting a kind to make a tidier list would
strand those entries — the one outcome the custody
law (E-093) exists to prevent. So they stay, and
this record is the whole of their status: kept,
working, tested, unpromised. E-104's user docs may
name them in one line as "also in the chest"; no
Ember feature, binding, or budget row may quietly
start depending on them without a slice of its own
saying so.

## 3. The other road's kinds — recorded, not merged

| Kind | What it is | Whose road it is |
|---|---|---|
| `astrology` | a chart record: sign, positions, aspects | the other Kista's readings family; inside Ember, readings belong to Part VII's engines' world, not to the credential chest |
| `rune-reading` | a reading: spread, runes, interpretation | the same readings family |
| `tarot-reading` | a reading: spread, cards, interpretation | the same readings family |
| `character-sheet` | a game character: name, scores, spells, story | the other Kista's records family; inside Ember, character sheets belong to Part X's table world |
| `markdown` | a document: title, text, category | the documents family — the shape `add-soul` and `add-cron-backup` file their backups under |

The set stands in the code as
`OTHER_ROAD_ENTRY_TYPES`.

**The wider ambitions, recorded as that side's
road.** The roadmap names the ai-folder Kista's
ambitions in its own words: *states, prompts,
habits*. This campaign has not measured that
program (E-011: it is never accessed); what can be
seen from this tree's 2026-05-21 snapshot of the
same family is how those words take shape in
practice — soul files backed up as vault entries
(a self's *state*), a machine's crontab backed up
the same way (a household's *habits*, kept as a
record), readings and character sheets filed as
first-class entries (an agent's life, recorded).
That is a live agent's strongbox growing toward
holding the agent's whole life. It is a good road —
**for that program.** The toaster-Kista's road is
the opposite discipline: the smallest chest that
holds what a person on tiny hardware needs, and
nothing else by default. Recording the wider road
here, in its own words, is what "not silently
merged" means: the ambitions are honoured as
recorded fact about the other Kista, and not one
of them becomes a toaster requirement by being
written down.

**What the program does about it (§4's shape).**
Nothing is removed, renamed, or fenced off: all
five kinds keep their schemas, their shortcuts,
their update fields, and their entries' behaviour
— after docket 137's repair, in full (§6). The
one change is speech: a *new* entry of one of
these kinds, added by either road, prints the
notice. Reading, listing, searching, updating, or
removing an existing entry prints nothing of the
kind — the notice guards the door where a merger
would happen (a new kind quietly becoming normal
here), not the custody of what is already held.

## 4. The notice — what the program says, and when

The words, exactly as printed by `cmd_add` (and,
in their own phrasings, by `add-soul` and
`add-cron-backup`):

> Note: '<kind>' is not one of the toaster-Kista's
> own kinds (passwords, tokens, URLs, notes). It
> belongs to the other Kista's wider road and is
> kept here exactly as given — nothing was merged
> or changed.

- It fires **after** the entry is saved, so it
  never claims custody the program did not take,
  and it fires on both add roads (general `--type`
  and the kind's own shortcut), because both roads
  run through `cmd_add`.
- It never refuses, warns of danger, or asks a
  question: the entry is the owner's to keep, and
  E-095's honesty discipline is the model — say
  what a thing is, in words, at the moment it
  happens, and let the owner decide.
- It composes with E-097 untouched: a program
  caller adding an entry of an other-road kind
  under its own name gets the same line on its
  stdout, and the entry is stamped and scoped
  exactly as any other. E-100's binding uses only
  toaster kinds, so the companion's normal road
  never meets the notice at all.
- **The surface grows by exactly the one command
  docket 137 restored**: `add-url` (§6) takes the
  mapped surface 34 → 35 subcommands. No other
  command was added, and E-094's battery is
  re-pinned consciously at this slice, with
  attribution, exactly as E-096 re-pinned it for
  its own two — E-097's record of a 34-command
  surface stands as written, true of its tree.
  The whole running cost of the kinds judgment
  itself is one membership test per add — beneath
  notice on toaster hardware; E-103 prices the
  vault as a whole.

## 5. Docket 50 — CLOSED (the Hermes-shaped commands)

Docket 50 (from E-011) asked whether three
commands that ship in the toaster copy belong in
the toaster set. Judged one by one:

- **`add-soul` — the other road's.** It backs up
  *another program's own files* (that program's
  soul and identity documents, from that program's
  home) into this vault as `markdown` entries.
  Whatever else it is, it is an act *about the
  other Kista's household*, and its entries are
  the other road's kind by construction. It stays
  working — an existing soul backup's renewal road
  is custody — and from this slice a successful
  run announces itself in the same words as §4
  ("a soul backup is not one of the
  toaster-Kista's own kinds…"). Its stored name
  is also repaired at this slice (docket 137,
  §6): a soul backup is now keyed in lowercase
  like every other entry, and vaults holding a
  pre-fix mixed-case backup heal on load, so the
  backup its owner made can actually be read
  back. E-011 rule 3's
  discipline is untouched: campaign probes ran it
  only against synthetic files under a scratch
  home, never against any real soul file.
- **`add-cron-backup` — the other road's.** A
  crontab is a machine's *state* — the "states"
  ambition in its plainest shape — not a
  credential, a token, a URL, or a note. Same
  verdict, same treatment: stays working, now
  announces itself ("a crontab backup is not one
  of the toaster-Kista's own kinds…"). Proven
  end-to-end here against a synthetic `crontab`
  stand-in on the probe's own PATH (this machine
  has no crontab command at all; the handler's
  honest refusal in that case is unchanged).
- **`github-backup` — not an entry-kind
  question.** It creates no entry kind of its own;
  it moves the whole encrypted vault to a git
  repository. That is a backup road, and it
  already has an owner: E-101 judges backup and
  restore for the toaster, carrying docket 135
  (its history/privacy shape, from E-095). This
  slice changes nothing about it and claims
  nothing about it, beyond recording that the
  docket-50 question, for this command, was
  asked of the wrong list.

With those three verdicts, docket 50 is CLOSED:
nothing of the three was silently absorbed into
the toaster set, and nothing was deleted.

## 6. Docket 137 — NEW, CLOSED in scope (dead add roads)

Found by this slice's own probing, before any
judgment was written: the claim "the imported
kinds work" was only half true. The member suite
tests the nine original kinds; the five v2.0
kinds were never exercised by it, and their add
roads were dead or crippled — and one toaster
kind's shortcut was missing outright:

- **The general road could not add
  `character-sheet`, `rune-reading`, or
  `tarot-reading` at all.** The general `add`
  parser defined none of their fields, so their
  required fields (a character's name; a reading's
  spread type) were unreachable, and every such
  add died at validation. An astrology entry
  could be added by the general road, but could
  carry nothing beyond its sign.
- **No road could add `markdown` at all.** The
  general parser's `--title`/`--content` land on
  attributes the add handler never read for this
  kind, and the `add-markdown` shortcut offered
  no content flag that reached the entry
  (`--md-source` is accepted and silently unused
  for content). Both of the kind's required
  fields were therefore unsatisfiable; the only
  `markdown` entries in existence were the ones
  `add-soul` and `add-cron-backup` construct
  directly.
- The update road already knew the right shape
  (`cmd_update`'s markdown branch reads the
  general title as a fallback) — the add road
  simply never got the same care. Recorded as
  the defect's shape, not as a mystery.
- **And `add-url` did not exist.** The program's
  own usage text (the module header, line 28)
  advertises `kista add-url <service> [url
  flags...]`, and `url` is a toaster kind — yet
  no parser, no `_add_type_args` branch, and
  none of the three shortcut maps (the parser
  loop, `main`'s dispatch maps, and `cmd_add`'s
  own inference map) ever named it. Running it
  answered with an argparse error. E-094's map
  recorded the surface as the code stood and so
  recorded 13 shortcuts without it; the usage
  text's promise and the map disagreed, and the
  promise was the one in the user's hands.
- **A soul backup could not be read back.**
  `add-soul` stored its entries under a
  mixed-case key (`soul-backup-SOUL`, built from
  the file's stem untouched) while every lookup
  in the program lowercases the name it is
  given — so `get`, `update`, and `remove` could
  never reach a soul backup at all. It sat in
  `list`, visible and untouchable: a dead road
  in the reading direction, found by this
  slice's focal battery when its soul probe
  tried to read back what it had just backed up.

**The fix, in scope, here:** the general `add`
parser gains the v2.0 kinds' fields with exactly
the shortcuts' attribute names, so both roads
build the same entry; the add handler's markdown
branch reads the general road's title and content
as fallbacks, as the update branch already did;
the `add-markdown` shortcut gains a `--content`
flag that lands where the handler reads;
`add-url` is built whole — its `_add_type_args`
branch (`--url` required, `--title`,
`--description`), its parser in the shortcut
loop, and its entries in all three shortcut
maps; and `add-soul` keys its backups in
lowercase like every other add road, while
`_load_vault` — which already upgrades legacy
entries in place — normalises any mixed-case
legacy key on load (healing the entry's stored
name with it, persisted on the next save; no
add road can mint two names differing only by
case, so the normalisation cannot merge
distinct entries). No schema, field, or stored shape changed:
entries written after the fix are byte-shaped
exactly as the design (the member's own
`ENTRY_TYPES.md`) always said they should be.
Docket 137 is CLOSED in scope; §7's probe is its
proof, and the focal battery pins both roads for
the repaired kinds — and the restored shortcut —
so the roads cannot die quietly again.

## 7. What was proven (probes, synthetic entries only)

Against scratch vaults (full log
`~/workspace/.verify-tmp/ember-e098/probes.log` —
35 commands, every one exit 0; the run's first
pass caught the missing `add-url` at exit 2
before the fix, and the log on file is the
post-fix run):

- **All 14 kinds add by the general road**, each
  with its required fields supplied the way a
  user would supply them, and read back whole.
- **All 13 typed shortcuts plus `add-person`
  add** the same way — `add-url` among them,
  restored by §6; a shortcut entry and a
  general-road entry of the same kind have the
  same shape.
- **The notice fires exactly 12 times** in that
  run: the five other-road kinds on the general
  road, the same five on their shortcut roads,
  `add-soul`, and `add-cron-backup` — and nowhere
  else. The four toaster kinds and the five kept
  kinds add in silence, on both roads.
- **`add-soul` against synthetic soul files**
  under a scratch home backed up both files, the
  notice printed, and the entries read back with
  their synthetic contents whole.
- **`add-cron-backup` against a synthetic
  `crontab`** (a two-line stand-in on the probe's
  PATH) stored the backup, the notice printed,
  and the entry reads back whole.
- **Custody is silent**: `get` and `list` over a
  vault holding other-road entries print no
  notice — the entries are simply there, owned,
  exactly as E-097 left them.
- The member suite stands where E-097 left it
  (**149 passed, 0 failed**): the repair touched
  no tested behaviour, and the nine kinds it has
  always tested behave byte-identically.

## 8. Standing findings handed on

- **E-099** inherits a cleaner question: interop
  is about *entries crossing*, and §1–§3 now say
  which kinds a crossing would even concern —
  the toaster set is the only set whose crossing
  this campaign may propose; the other road's
  kinds crossing *into* the toaster set is the
  silent merger this slice exists to refuse.
- **E-100** inherits the binding set: `credential`
  + `apikey`, both toaster kinds, under E-097's
  `KISTA_PROGRAM` shape and E-096's passphrase
  road. No kept or other-road kind is in the
  binding, and none may join it without a slice
  saying so.
- **E-101** inherits `github-backup` whole
  (§5), with docket 135 standing as E-095 left
  it.
- **E-103** inherits the cost line: three
  frozensets and one membership test per add —
  no measurable weight; the vault's price is
  still the vault's own.
- **E-104** inherits the user words: "your chest
  holds passwords, tokens, URLs, and notes" is
  the sentence the plain docs are written from;
  the kept kinds earn one line ("also in the
  chest"), the other road's kinds earn the
  boundary sentence, and the member's own
  `ENTRY_TYPES.md` — which still presents all 14
  kinds as one undifferentiated design — is
  docket 130's ground, reconciled there against
  this slice's partition.
- **E-187** inherits the honesty line for the
  audit: the notice is speech, not a fence — it
  stops a silent merger, never a determined
  operator, and no Ember document may describe
  it as access control (that was E-097's line,
  and it stands unchanged).

## Slice gate

Focal battery `tests/unit/test_kista_entry_kinds_e098.py`
pins this record: the three-set partition derived
from the code itself, the notice's words in doc and
code, the 35-subcommand surface (34 + the restored
`add-url`, nothing else added), and the §7 probes —
every kind addable on both roads, the notice
firing exactly where §4 says and nowhere else. Member suite and root gates are recorded in
the campaign state file at banking; the E-057
member table is re-measured and re-pinned there
with attribution (the credstore's growth moves
kista's row and the twelve-member total; both
published copies re-pinned to the tree).
