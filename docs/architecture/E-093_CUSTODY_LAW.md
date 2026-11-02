# E-093 — Custody Law for the Whole Campaign

*Project Ember campaign, Part VI (Kista of the Toaster),
opening slice. Measured and written 2026-11-01 on branch
`yrsa/ember-road-build` in the campaign's own clone
(`~/workspace/ember-build`), at campaign commit 2e7dffb
(E-093 IN PROGRESS). Method: E-013's secrets census
re-run fresh over the whole tracked tree at this HEAD
(3,443 tracked files, 2,991 text-shaped files scanned;
raw output in `~/workspace/.verify-tmp/ember-e093/`),
every credential-resolution point in `src/ember/`
re-read, and the toaster-Kista's own password surface
re-read in `kista/scripts/credstore.py`. **No credential
value is reproduced anywhere in this doc** — hits are
recorded as file, line, shape, and classification only.*

## Headline — read this first, in plain words

**A credential is a key. Keys live in exactly one
place: a Kista. Never in a config file, never in code,
never in chat, never in a log, never in a test that
pretends to be real.** Everything else in this document
is that sentence made precise enough to enforce.

Which Kista depends on the machine (the E-011 boundary,
which this law adopts whole): on Volmarr's own house
machines, real credentials live in the **ai-folder
Kista** on purplelongship — this campaign never touches
it. On any machine running Ember — a stranger's toaster
included — Ember's own credentials live in the
**toaster-Kista** (`kista/` in this repo), once E-100
binds the core to it. Until that binding lands, the
interim custody shape is the one the tree already
proves: environment variable → the computer's keyring →
a mode-600 file, the Well resolver's order (E-013 §2).
Interim is not a second standard; it is the bridge to
the one standard, and E-100 closes it.

The fresh scan says the tree is clean today, in the
same way E-013 found it: **no real credential exists in
any plain file** (§4). The defects this slice found are
shape defects, and they are dealt with in §5 — one
fixed in this slice, two docketed to their owners.

## 1. The law (binding on every later slice)

1. **Keys live in a Kista.** A credential (password,
   API key, token, private key, TOTP secret, vault
   passphrase) may be *stored* only in a Kista vault —
   the ai-folder Kista for house credentials on house
   machines, the toaster-Kista for Ember's credentials
   on an Ember machine (E-011 §5 governs the boundary;
   no entry ever crosses between the two).
2. **Never in configs.** A config file may hold a
   *reference* — a vault entry name, an env-var name,
   a keyring service name, a file path — never a value.
   The tree's proven shapes stand as the examples:
   `secret_env` names the variable, `secret_ref` names
   the file, `api_key_file` names Aesir's key file
   (E-033). A config string that *could* carry a value
   inside it (a URL with a password segment, a helper's
   env map) is treated as a reference slot: the value
   comes from custody, never from the string (§5,
   docket 129; docket 58's boundary rule, now law).
3. **Never in code.** No credential value is written in
   source, in a default, in a doc example, or in a
   committed script. Examples show the *shape* with an
   obvious placeholder, as `.env.example` now does.
4. **Never in chat.** No credential value is pasted
   into any conversation surface — this campaign's
   chats included — and a credential that arrives in
   chat is exposed by definition: it is rotated, and
   the rotation is the fix, not the deletion of the
   message. (The toaster-Kista's own `SKILL.md` already
   teaches this rule; this law makes it campaign-wide.)
5. **Never in logs, diary, or context.** A resolved
   credential is held in memory, used, and dropped; it
   is never logged, never echoed in an error, never
   written to the conversation diary, and never
   injected into a model's context (E-062/E-063 already
   forbid credential-shaped material there; this law is
   the rule they cite). Errors name the *source* that
   failed and the *reason shape* — never any part of
   the value (the Well resolver's and the Aesir
   adapter's stated contracts).
6. **A credential file is mode 0600 or it is refused.**
   Where a credential must exist as a file outside a
   vault (the interim shape), the file must be exactly
   mode 0600 on POSIX; a more permissive mode is a
   refusal with a pointer at the permission bits, not a
   warning. The Well resolver has always enforced this;
   this slice extends it to the Aesir key file (§5,
   docket 127, CLOSED here).
7. **A passphrase is never a command-line value.** A
   vault passphrase travels by hidden prompt, by
   `--password-file`, or by `--password-env <NAME>`
   (the *name*, never the value) — the toaster-Kista's
   sound shapes. Its one unsound shape, a `--password`
   value on the command line (visible in process lists
   and shell history), is docketed to its owner (§5,
   docket 128 → E-096).
8. **Fixtures are synthetic and visibly so.** Test
   data that must be credential-*shaped* (the credstore
   round-trip tests need key-shaped data to prove
   anything) is built from obvious synthetic patterns
   and lives only against isolated vaults/stores. The
   classified allowlist in this slice's battery is the
   enforcement shape; a new credential-shaped string
   anywhere in the tree fails the battery until it is
   classified there, consciously (docket 57's
   discipline, now armed; E-187 inherits the gate).
9. **Identifiers are not credentials — and are still
   custody-sensitive.** A service name, a vault key
   name, an account address, an API-key *prefix*: these
   identify, they cannot authenticate. They may appear
   in plain files only where a document's job requires
   them, they are never joined with a value, and a
   *map* of them (which key opens which account) is
   treated as sensitive material (§5, the docket 48
   case). Reports name identifiers only as far as the
   work requires — the E-013 census's own practice.
10. **Discovery creates the duty.** Any worker who
    finds a real credential value in a plain file, in
    any slice, stops that slice's line, reports it
    plainly (shape and place, never the value), and the
    fix — removal plus rotation advice to the owner of
    the credential — is commissioned on the spot. A
    shape defect (a place a value *could* be put
    wrongly) is docketed to its part, as §5 does.

## 2. Which Kista, per machine

| Machine / install | Custody for… | Held where |
|---|---|---|
| purplelongship (house) | Volmarr's real credentials (the Heimdall/Second Life login is the recorded example) | The ai-folder Kista — operational, Hermes/Runa-side custody. **This campaign never reads, runs, or updates it** (E-011 §5 rule 2) |
| This campaign's VM | Nothing real. Campaign work uses synthetic fixtures and isolated vaults under the slice's own scratch only; toaster-Kista is never run unconfigured (E-011 §5 rule 3) | No real entries exist here, and none may be created |
| An Ember install (any machine, the toaster included) | Ember's own credentials: the shared-Well password, the Aesir service key, any model/API keys a binding needs | The toaster-Kista on that machine, bound at E-100. Until E-100: the interim resolver chain (§3) |
| A member program with its own store shape (mempalace's env-only LLM keys, the dictionary's env-only revalidate secret) | That member's runtime keys | Env-only, as E-013 §1 recorded — a sound shape this law adopts; the value is never in the member's config file |

## 3. The interim standard — the resolver order

Until E-100, any Ember code that needs a credential
resolves it in exactly the Well resolver's order
(`src/ember/well/brunnr/pgvector/secrets.py`, ADR 0010
§2.5), which is the campaign standard:

1. **Environment** — the variable *named in config*
   (`secret_env`, default `EMBER_WELL_PASSWORD`);
2. **Keyring** — the OS keyring under the configured
   service name, when the operator has installed the
   `secrets` extra;
3. **Mode-600 file** — the file *named in config*
   (`secret_ref`), refused at any other mode;
4. **Typed failure** — which sources were tried and why
   each was skipped, with the value never named.

The Aesir binding already follows the reference shape
(config holds `api_key_file`, a path, never the key;
the adapter holds the key in memory only and never
logs or reprs it); §5 brings its file to the same
0600 standard. No new credential path may be built in
any later slice in any other shape: a binding that
needs a credential either uses this chain or waits
for E-100's Kista binding.

## 4. The fresh scan — the tree today, classified

E-013's method at this HEAD (3,443 tracked files;
2,991 text-shaped scanned — the tree has grown by
201 tracked files since E-013's 3,242):

- **GitHub tokens: 0. JWTs: 0. Bearer literals: 0.
  OpenAI-shaped `sk-` keys: 0** (the E-013 hyphenated-
  prose false positive no longer matches the tightened
  pattern; no new hit stands in its place).
- **Private-key blocks: 7 hits, the same 7 as E-013** —
  four in `kista/tests/test_credstore.py` (synthetic
  key material round-tripped through an *isolated*
  test vault), two in `tests/unit/
  test_tool_read_local_file.py` (fake keys proving the
  file tool refuses/redacts), one in `kista/SKILL.md`
  (a heredoc *template* whose body is literally `...`,
  in instructions that forbid pasting keys into chat).
- **AWS-shaped keys: 2 hits, the same 2 as E-013** —
  sequential synthetic test data in `kista/tests/
  test_credstore.py`'s isolated-vault apikey tests.
- **Password-bearing URLs: 137 hits, one family plus
  six house hits.** The family is CloakBrowser's
  vendored proxy docs/tests (password segment the
  literal word `pass` or its own short parsing
  fixtures) — vendored, never rewritten, and Ember's
  own code is forbidden the shape by law rule 2. The
  house hits are all placeholders or refusal fixtures:
  `docs/adapters/GUNGNIR_WELL_REFERENCE.md` (the
  literal `<secret>`), the E-013 census doc itself,
  `src/ember/tools/fetch_url.py`'s docstring example,
  `tests/unit/test_hardening_batch_a.py` (incl. the
  `hunter2` fixture proving redaction), and two
  Mythic-plan/DEVLOG mentions with segment `pass`.
- **Credential-shaped assignments in code/config
  (quoted values of 12+ chars): 20 hits, all
  fixtures** — 13 in `kista/tests/test_credstore.py`
  (isolated-vault values: sequential, prefixed, and
  Unicode test passwords; two TOTP-shaped secrets,
  one the RFC-style `JBSWY3…` pattern), 2 in
  mempalace's tests (`sk-fro…` fake key; a `/priva…`
  path-shaped MCP fixture), 2 in `scripts/dev/
  compare_memory_systems.py` (named synthetic tokens
  in a dev comparison script), 3 in the root tests
  (the guarded pgvector live test's local-dev
  password, the Well-secrets battery's custom-env
  fixture, the E-044 battery's env-name fixture).
  E-013 counted 8 under a narrower key-name pattern;
  this slice's wider net (password/secret/token/
  api-key/credential) is the battery's net from here
  on, and its allowlist names exactly these 20.
- **Tracked credential-shaped filenames: exactly 1**
  — `.env.example`, the documentation-only template
  E-033 rewrote (names the two live variables, holds
  no value). No tracked `.env`, `.pem`, `.key`, or
  vault file exists.

**Verdict: the starting fact of Part VI is E-013's
verdict, re-proven at this HEAD — no leakage; the
remaining work is shape, and §5 is its list.**

## 5. E-013's defects land here — dispositions

- **Docket 55 (the `.env.example` fossil) — already
  CLOSED at E-033**, which replaced the fossil with
  the two live variables and the rule "never put a
  secret in the config file". This law cites it as
  executed precedent: a document that sends an
  operator to put keys in a file nothing reads is a
  custody defect, fixed where found.
- **Docket 56 (config fragmentation) — its custody
  half is closed by this law:** whatever shape a
  member's config takes, law rules 2–3 govern its
  credential content. The unification half stands
  where E-033/E-037 left it.
- **Docket 57 (fixture indistinguishability) — the
  discipline is now armed:** law rule 8 + this
  slice's battery allowlist (the 20 assignments, the
  7 key blocks, the 2 AWS shapes, the house URL
  files). E-187's security gate inherits the battery
  as its scanner seed.
- **Docket 58 (URL-embedded credentials) — boundary
  rule promoted to law rule 2** for all Ember code
  and config; the vendored tree is untouched; E-178
  executes the browser-side ladder.
- **Docket 46 (toaster-Kista's default home is the
  other Kista's territory) — DECIDED here, built at
  E-094.** The toaster-Kista's own default vault
  directory shall be **`~/.ember/kista/`** — inside
  Ember's own home (E-020's custody-of-the-folder
  shape), no other program's territory. `KISTA_DIR`
  remains the override. Until E-094 lands the change,
  E-011 §5 rule 3 binds every worker: never run the
  toaster program unconfigured.
- **Docket 48 (the known-accounts ledger) — this
  law's first case, ruled under rule 9.**
  `kista/references/known-accounts.md` is an
  *identifier ledger*: service names, vault key
  names, account addresses, statuses, and one API-key
  prefix (a prefix identifies; it cannot
  authenticate — re-verified this slice, no credential
  value in the file). Ruling: (a) it is **not** a
  credential leak and no emergency action stands;
  (b) no credential value may ever be added to it,
  and the campaign adds no new entries; (c) whether
  the ledger *belongs in this repo at all* remains
  **Volmarr's word** — removal is his call, unmade on
  this record, and this law does not make it;
  (d) until his word, every worker treats the file as
  custody-sensitive: its identifiers are not quoted
  in reports beyond what the work requires.
- **Docket 127 — NEW, CLOSED in this slice.** The
  Aesir key file was read with no permission check,
  below the Well resolver's standard in the same
  tree. Fixed: `AesirFuni.open` now refuses a key
  file whose POSIX mode is not exactly 0600, before
  reading it, with the mode named and the key never
  shown; the E-023 and E-036 batteries' key writers
  now chmod 0600, and this slice's battery pins the
  refusal. (The key file is Aesir's own custody on
  the service side; Ember's duty is to refuse a
  world-readable copy of it.)
- **Docket 128 — NEW, assigned to E-096.**
  Toaster-Kista's credstore resolves a vault password
  from a `--password` command-line *value* (third in
  its priority, after `--password-file` and
  `--password-env`) — a value on a command line is
  visible in process listings and shell history,
  against law rule 7. E-096 (the unlock experience)
  owns the remedy's shape; until then no campaign
  work uses that flag.
- **Docket 129 — NEW, assigned to E-187.**
  mimir-well's `backup_repo` is a plain config string
  consumed as a git remote URL (`backup.py`): a
  credential-bearing URL pasted there would persist
  in a plain config *and* in the clone's remote —
  against law rule 2. No such value exists in the
  tree (E-013). E-187's audit owns the enforcement
  shape (refuse credential-bearing backup URLs at
  use, or route the remote through a credential
  helper); this law states the rule it will enforce.

## 6. What the later slices inherit

- **E-094** builds docket 46's decided default
  (`~/.ember/kista/`) into the toaster-Kista and its
  mapping; §1's table is the surface it maps against.
- **E-096** owns docket 128 (the `--password` shape)
  inside the unlock experience for normal folks.
- **E-097/E-100** build per-program access and the
  core binding *under this law*: the binding resolves
  through the vault, and the interim chain (§3) is
  retired for the core when it lands.
- **E-178** executes law rule 2 on the browser side;
  **E-187** inherits the battery as its scanner seed
  and owns docket 129.
- **Every slice:** law rule 10. A real value found
  anywhere stops the line; a shape defect is
  docketed, never silently cleaned.

## Slice gate

Focal batteries first (this slice's own, the two
batteries whose helpers this slice touched, the
E-089 canon guard whose allowlist this slice extends
consciously by one file — the governance-needle
reason: this battery pins "Volmarr's word" standing
reserved in the custody law's docket-48 ruling), then
the campaign's combined and full shapes — counts are
recorded in CAMPAIGN_STATE.md from the runner only.
One production file changed (the Aesir adapter's
custody refusal); its +1,009 B moved the core's
E-057 size pin, re-measured and re-pinned with
attribution in both published copies (src 922,893 B;
twelve-member total 131,546,922 B; laptop miss
unchanged 256,017 B). No README touched; no vendored
file touched.

*Filed by the E-093 slice, 2026-11-01. Next: E-094 —
toaster-Kista mapped (storage, crypto shape, CLI/API
surface, test state), building docket 46's decided
default home.*
