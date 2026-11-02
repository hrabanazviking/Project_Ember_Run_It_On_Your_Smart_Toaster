# E-100 — Ember Core Binding: the Companion Fetches Its Credentials from the Toaster-Kista

*Project Ember campaign, Part VI (Kista of the Toaster),
eighth slice. Roadmap line: "Ember core binding: the
companion fetches its model/API credentials from
toaster-Kista under E-097". Built and measured
2026-11-01 on branch `yrsa/ember-road-build` in the
campaign's own clone, building on E-097's per-program
access and E-096's unlock. Method: a new core module
(`src/ember/kista_binding.py`), two consumers wired to
it (the Aesir backend and the Well secret resolver),
the vault program's write lock (docket 134), and
probes against scratch vaults holding synthetic
entries only (raw logs in
`~/workspace/.verify-tmp/ember-e100/`). The ai-folder
Kista was not accessed, run, or read — this binding
calls the toaster-Kista on the companion's own
machine, exactly the shape E-099 §6 left untouched.*

## Headline — read this first, in plain words

**The companion now keeps its keys in the vault, the
way the custody law always said it should.** In plain
words:

- **The companion has a name at the vault, and only
  its own keys answer to it.** The core calls the
  toaster-Kista as the program `ember-core`
  (`KISTA_PROGRAM=ember-core`, E-097). The owner gives
  the companion its entries at the Kista's own command
  line (`add … --program ember-core`); from then on
  the companion can fetch exactly those entries and
  no others. The owner's own entries, another
  program's entries, and entries that do not exist
  all refuse in the same words, and no fetch ever
  learns a name, a count, or a value that is not its
  own.
- **Only model/API credentials cross.** The binding
  fetches the toaster set's two secret-bearing kinds
  (E-098): a `credential` entry gives its password, an
  `apikey` entry gives its key. Any other kind — a
  note, a URL, an identity — is refused by the binding
  itself, in words: it is not a model/API credential,
  and this road does not carry it.
- **A locked vault stays locked.** When the owner has
  set a passphrase (E-096), the fetch carries it
  through the `KISTA_PASSPHRASE` environment variable
  — the variable's *name* is what config holds, never
  a value — and without it the vault refuses and the
  binding reports that refusal. The binding never
  prompts: a programmatic fetch that cannot open the
  vault fails with a reason, it does not stop a
  conversation to ask a question nobody scripted.
- **The binding is fetch-only.** The core never adds,
  changes, or removes a vault entry — it issues
  exactly one vault verb, `get`. Custody stays the
  owner's act, at the Kista's own command line, as
  E-097 built it. A fetched value lives in memory
  only: never logged, never written to a config,
  never named — in whole or in part — in any reason
  the binding or its consumers return.
- **Two consumers are wired.** The Aesir backend: set
  `funi.aesir.api_key_entry` to the name of the
  companion's vault entry and `AesirFuni.open` fetches
  the service key through the binding and never reads
  the key file at all. The Well: set
  `brunnr.pgvector.kista_entry` and the secret
  resolver takes the vault as its first and only
  source for that password. Naming an entry in either
  place is the act that turns the binding on for that
  credential; with no entry named, both consumers
  behave exactly as they did before this slice, and
  the core's `kista.enabled` switch (default off)
  records the same posture for the binding as a whole.
- **The interim chain is retired where a vault entry
  is named.** E-093 §3's env → keyring → mode-600-file
  order was the bridge to this binding. It still
  serves any secret no vault entry has been named
  for — removing it there would strand existing
  installs, and this slice does not pretend
  otherwise — but for a named entry the interim
  sources are not tried at all, not even as a
  fall-back when the vault refuses. A credential the
  owner has put in custody does not quietly come
  from somewhere plainer because the vault said no.

## 1. How it works

- **The face.** `ember.kista_binding.fetch_credential
  (entry_name, *, config, env, runner)` returns a
  `KistaResolution` — a secret, or a reason, never
  both, never an exception for a vault-side failure —
  in the Well resolver's manner. It runs the
  toaster-Kista program (`kista/scripts/credstore.py`)
  as a subprocess with `KISTA_DIR` set from config
  (default `~/.ember/kista/`, the E-094 home),
  `KISTA_PROGRAM` set to the configured program name
  (`ember-core`), and the member directory + user
  site-packages on the child's path, exactly as the
  campaign's probes run it — so the member's one
  dependency resolves the same way it does for the
  owner's own runs, and its absence is the program's
  own plain refusal, reported as the reason. A fetch
  that has not answered in 30 seconds is reported as
  timed out, never waited on forever.
- **Config is references only** (E-093 rule 2):
  `KistaConfig` holds the program name, the vault
  directory, an optional path to the Kista program
  (empty = the in-tree member), and the *name* of the
  passphrase environment variable. Consumers hold an
  entry *name* each (`api_key_entry`, `kista_entry`).
  No config anywhere holds a value.
- **The consumers.** `AesirFuni.open` gains the vault
  road beside the file road: with `api_key_entry`
  set, the fetched key passes through the same
  grammar check and readiness probe as a file-read
  key (the checking tail is one shared
  `_open_with_key`, so the two roads can never drift
  apart in what they accept), and a vault refusal is
  `Unavailable(CONFIG_INVALID)` carrying the binding's
  reason. The Well resolver gains step 0: with
  `kista_entry` set, the vault is tried before the
  env and is the only source; with it unset, the
  ADR 0010 order stands byte-for-byte as before,
  which its elder battery proves unchanged.
- **Honesty, inherited and restated.** A program name
  is an identifier, not a credential (E-097): this
  binding is discipline for the companion and its
  fellow well-behaved programs, not a wall against
  malicious same-account code — E-095's A2 verdict
  stands unchanged, and the passphrase is the door
  that guards a copied vault folder, not this name.

## 2. Docket 134 — the write lock, built here

E-095 §3.9 recorded that the vault program had **no
inter-process lock**: two writers at once shared one
predictable temp-file name, and a load/modify/save
from each could interleave and silently drop one
writer's change. E-095 assigned the lock's shape to
this slice ("the binding slice makes the second
writer real"), with the drills at E-102. The shape
built here, in `kista/scripts/credstore.py`:

- **One lock per vault.** Every command that can
  change the vault, its key, its config, or its
  backups (init, add, update, remove, import,
  restore, repair, the passphrase commands,
  github-backup, add-soul, add-cron-backup, config)
  takes an `flock` on `.vault.lock` inside the vault
  directory at dispatch and holds it for the whole
  run. A second writer waits; it does not fail, and
  it does not interleave. A crashed holder releases
  the lock when its process dies, so the lock can
  never go stale. Read commands never lock: vault
  writes land by atomic replace, so a reader — this
  binding included — always sees one whole state or
  the other.
- **Per-process temp names.** The atomic write's
  temp file now carries the writer's pid
  (`<name>.<pid>.tmp`), never the one shared
  predictable name — so even where the lock cannot
  reach, two writers cannot write into each other's
  temp file.
- **The platform limit, stated.** The lock is POSIX
  `flock`, standard library only, no new dependency
  and no daemon. On a platform without it, the lock
  is a no-op and the vault keeps its pre-E-100
  behaviour there; no claim is made for that
  platform, and E-187's platform audit (docket 136's
  home) inherits the line.
- **A record defect found on the way in, recorded
  not repaired:** E-095's own docket-134 paragraph
  is truncated on disk — its last sentence ends
  mid-thought ("…so the lock is") and the following
  line is a literal truncation marker baked into the
  file at that slice's banking. The lost words are
  not recoverable from the tree and are not invented
  here; this section is the shape the docket asked
  for, filed in the slice that owns it. The E-095
  file itself is elder record and stands as written,
  this note beside it.

## 3. What was proven (probes, synthetic entries only)

Against a scratch vault holding an `ember-core`
apikey entry (a synthetic Aesir-shaped key), an
`ember-core` credential entry, and an owner's entry:

- The binding fetches both of the companion's
  entries, whole — the apikey's key and the
  credential's password, each from its own field.
- The owner's entry refuses through the binding, and
  its value appears nowhere in the reason; a missing
  entry refuses the same way.
- With a passphrase set on the vault: a fetch with
  no passphrase is refused and names nothing; with
  `KISTA_PASSPHRASE` in the caller's environment the
  same fetch opens and returns the key; with a wrong
  passphrase it refuses again — the lock and the
  scoping compose through the binding exactly as
  E-097 proved them at the program's own door.
- Two writer processes adding different entries at
  the same moment both land whole — both names
  listed, both values reading back — and the
  `.vault.lock` file stands in the vault directory
  as the lock's visible trace. (The harder drills —
  kill-mid-write, tamper, wrong-passphrase batteries
  against this lock — are E-102's charter.)
- The Aesir consumer: opened against the scratch
  vault with `api_key_entry` set and the key file
  path pointing at a file that does not exist, the
  adapter opens — and its generate call carries
  `Authorization: Bearer <the vault's key>` to the
  (faked) service. The file road was never touched:
  the named file does not exist, so any read of it
  would have failed the open. With the entry naming
  the *owner's* entry instead, the open is
  `CONFIG_INVALID` and the owner's value appears
  nowhere in the detail.
- The Well consumer: with `kista_entry` set and the
  environment carrying a *different* value under the
  configured env name, the resolution is the vault's
  value — the interim chain is not consulted; with
  the vault refusing, the resolution is a typed
  failure naming the vault as the only source tried,
  and the env value is not used.

## 4. Standing findings handed on

- **E-101** inherits the boundary of this binding:
  backup & restore are whole-vault, owner-only acts
  (E-097) and stay outside the binding — the core
  fetches single entries under its program name, and
  nothing here is a backup road. Dockets 135 and 138
  stand as E-098/E-099 left them.
- **E-102** inherits the drills for §2's lock:
  concurrent writers under load, a writer killed
  mid-save, and the wrong-passphrase / tampered-vault
  batteries re-run against the locked shape.
  Docket 133 (rollback/freshness) stands beside them
  as its own question.
- **E-103** inherits the binding's price row: one
  subprocess run of the vault program per fetch (plus
  one scrypt derivation when the vault is locked) —
  a per-open cost, never a per-turn one, since
  consumers fetch at open and hold the value in
  memory. Nothing here claims a figure; E-103
  measures the vault whole.
- **E-104** inherits the user words: "your companion
  keeps its keys in your Kista, under its own name;
  you give it a key by adding an entry for
  ember-core; it can never read your own entries,
  and it never writes anything." The docs there are
  written against the toaster set's four kinds
  (E-098), of which this binding fetches two.
- **E-106** (Part VI gate) inherits the claim this
  slice proves: core binding live — the companion
  fetches its model/API credentials from the
  toaster-Kista under E-097, with the drills of
  E-102 still to land before the gate can pass.
- **E-187** inherits the honesty lines: the program
  name is not a credential (A2 stands), the lock is
  POSIX-only and stated so, and a fetched value's
  custody is memory-only — an audit that finds a
  fetched value in a log, a config, or a reason
  string has found a defect in this slice's code.

## Slice gate

Focal battery `tests/unit/test_kista_core_binding_
e100.py` pins this record: the doc, the binding's
shape in code (one verb, the program name, the
kind→field map), the lock's shape in the vault
program, unit fetches through an injected runner,
the scratch-vault probes of §3 (scoping, the
passphrase composition, the two-writer landing),
and both consumers end to end. Three elder batteries
were re-pinned consciously at this slice, each with
its attribution written beside the pin: E-095's
no-lock pin (that absence was its docket-134
requirement to this slice, and the lock is now
present in its built shape — the same act E-096
performed on E-095's no-derivation pin), E-093's
credential-assignment census (this slice's battery
adds one classified fixture: its synthetic
Aesir-shaped vault key, scratch vaults only), and
E-033's config-template completeness (the template
now documents the six new keys in plain words — the
`kista:` section and the two entry-name keys).
Member suite and root gates are recorded in the
campaign state file at banking; the E-057 member
table is re-measured there (the binding grows
`src/`, the lock grows `kista/` — both rows and the
twelve-member total re-pinned in both published
copies, with attribution).

*Filed by the E-100 slice, 2026-11-01. Next: E-101 —
backup & restore of a tiny vault (user-carried file,
encrypted; restore proven), carrying dockets 135
and 138.*
