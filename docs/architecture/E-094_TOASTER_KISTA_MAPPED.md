# E-094 — Toaster-Kista Mapped

*Project Ember campaign, Part VI (Kista of the Toaster),
second slice. Roadmap line: "Toaster-Kista mapped: its
storage, crypto shape, CLI/API surface, test state —
from code", building docket 46's decided default home
(E-093 §5). Measured and written 2026-11-01 on branch
`yrsa/ember-road-build` in the campaign's own clone, at
campaign commit 401d936 (E-094 IN PROGRESS). Method:
`kista/scripts/credstore.py` (2,382 lines, 101,402 B
after this slice) read whole; its surface enumerated
from the code itself (AST + `--help` + sandboxed runs);
the member suite run fresh before and after this
slice's changes (raw logs in
`~/workspace/.verify-tmp/ember-e094/`). The ai-folder
Kista was not accessed, run, or read — the E-011
boundary governs every word below: this map is of the
toaster program in this tree, and of nothing else.*

## Headline — read this first, in plain words

**The toaster-Kista is one Python program that keeps
every entry in a single encrypted file, and as of this
slice its home is Ember's own.** Concretely:

- **One file, whole-vault encryption.** All entries
  live in one JSON document, encrypted as a single
  blob with Fernet and stored as `vault.json.enc`.
  There is no database and no per-entry file (§1–§2).
- **The key is a separate file, not a passphrase.**
  The vault is *not* unlocked by something a person
  types: a random Fernet key sits in `.vault_key`
  beside the vault, mode 0600. Whoever can read both
  files can open the vault — that is the honest shape
  E-095's threat model will judge (§2).
- **Docket 46 is built and CLOSED.** With `KISTA_DIR`
  unset, the vault now defaults to **`~/.ember/kista/`**
  — inside Ember's own home (E-020's shape), no other
  program's territory. `KISTA_DIR` remains the
  override, and it wins whenever it is set (§6).
- **Its test suite finally judges this program.** The
  suite's three long-standing failures were docket 5:
  three tests pointed at a copy of the program under
  another installation's home and never touched the
  code in this tree. They now resolve the in-tree
  script, one stale version expectation they had been
  hiding is corrected, and the suite stands at
  **149 passed, 0 failed** (§5).
- **Nothing consumes it yet.** The Ember core imports
  nothing from `kista/` (zero consumers in `src/`,
  re-verified this slice); the binding is E-100's
  work. Until then the program is a standalone keeper,
  exactly as E-011 recorded it.

## 1. Storage — what exists on disk

Everything lives under one directory, `VAULT_DIR`,
resolved once at import from the environment:
`KISTA_DIR` when set, otherwise the default home
(decided at E-093, built here): `~/.ember/kista/`.
Importing the module creates nothing; the directory
is first made by an actual vault operation
(`_ensure_dir`), proven by a sandboxed import probe
(an empty scratch home stayed empty).

| Path (under `VAULT_DIR`) | What it is | Protection |
|---|---|---|
| `.vault_key` | The Fernet key: 44 bytes, base64url, 32 bytes of entropy | Written once at first use; chmod 600 |
| `vault.json.enc` | The whole vault, one Fernet blob | chmod 600 after every save |
| `vault_meta.json` | Plaintext index: version, created/updated stamps, service *names*, entry count, program version | None — names only, never values, by design |
| `config.json` | Free-form program config (e.g. the github-backup repo reference) | chmod 600 on save |
| `backups/` | Auto-backups: the last 5 encrypted blobs, `vault_backup_<stamp>.enc` | Each chmod 600 |
| `github_tmp/` | Scratch for github-backup (created on use) | — |

Saves are atomic (write to a sibling temp file, then
`os.replace`), and every save first keeps an encrypted
auto-backup of the new blob, pruning to the last five.
A save therefore cannot leave a half-written vault,
and the last five states survive a bad one.

## 2. Crypto shape — what protects the entries

- **Cipher:** Fernet from the `cryptography` package
  — AES-128-CBC with an HMAC-SHA256 authentication
  tag, encrypting the vault JSON as one blob
  (`_encrypt` / `_decrypt` are the only two doors).
  A wrong key or a tampered blob fails as
  `InvalidToken`; nothing decrypts partially.
- **Key custody:** the key is generated once
  (`Fernet.generate_key`) and stored as a file. It is
  validated on every read: exactly 44 bytes decoding
  to 32, or a refusal that says the data is intact
  and the key must not be regenerated. If vault data
  exists but the key file is missing, the program
  exits with that stated plainly — it never silently
  mints a new key over existing data.
- **There is no vault passphrase.** No prompt unlocks
  this vault; the "password" machinery (§4) resolves
  *entry* passwords for credential entries, never a
  vault passphrase. The vault's whole defence is file
  permissions (0600) plus the operating system's own
  account boundary. E-095 sizes the threat model
  against exactly this shape, and E-096 owns whatever
  unlock experience the verdict requires.
- **Self-healing:** a vault that will not decrypt, or
  that decrypts to invalid JSON, triggers an automatic
  repair attempt from the newest valid auto-backup;
  `repair` runs the same road by hand. Corruption is
  reported, never papered over.

## 3. The vault and entry format

The decrypted vault is one JSON object:
`{version, entries, created, updated}` (version
upgrades to 2 on load; entries written before entry
types existed are read as `credential`). Each entry
is keyed by its lowercased service name and carries
`service`, `entry_type`, `created`, `updated`, the
common fields (`username`, the entry's own password
field, `email`, `url`, `notes`, `tags` — tags parsed
to a lowercased list), and its type's fields.

**14 entry types stand in `ENTRY_TYPE_SCHEMAS`**, each
with its required field named in the code:
`credential` (no required field), `apikey` (key),
`sshkey` (private key, read from a file), `certificate`
(cert, read from a file), `note` (content), `totp`
(secret), `license` (key), `identity` (no required
field), `url` (url), `astrology` (sign),
`character-sheet` (name), `rune-reading` (spread
type), `tarot-reading` (spread type), `markdown`
(title + content). Which of these belong in the
*toaster* set is E-098's question, not this map's:
the map records that all 14 stand in the code today,
including the five v2.0 reading/document types the
Hermes-shaped history brought with them (docket 50).

## 4. CLI / API surface — what a caller can do

**There is one surface: the command line.** Packaging
(`kista/pyproject.toml`, kista 2.0.0, MIT, Python
>=3.9, sole dependency `cryptography`) installs one
console script, `kista = scripts.credstore:main`.
There is no server, no socket, and no supported
library API: the module's 42 top-level functions
(20 `cmd_*` handlers + `main`, the vault helpers, and
`_add_type_args`) are the program's own internals,
imported directly only by its test suite. E-097 /
E-100 will decide what a *programmatic* face should
be; today any program — Ember's core included —
would drive it as a subprocess or not at all, and
today the core does not (§ headline).

**32 subcommands** stand in `main()`:

- *Vault life:* `init`, `repair`, `status`.
- *Entries:* `add` (any type via `--type`), `get`,
  `list` (tag filter), `update`, `remove`, `check`,
  `search` (fuzzy over services and fields, with
  optional date filters), `generate-password`.
- *Type shortcuts:* `add-apikey`, `add-sshkey`,
  `add-certificate`, `add-note`, `add-totp`,
  `add-license`, `add-identity`, `add-astrology`,
  `add-character-sheet`, `add-rune-reading`,
  `add-tarot-reading`, `add-markdown`, and
  `add-person` (the enhanced identity shape) — each
  is `add` with its type set.
- *Movement:* `export` (a copy of the encrypted blob),
  `import` (skip / `--merge` / `--overwrite`),
  `backup` (a JSON dump, optionally encrypted; the
  plaintext shape prints its own warning), `restore`.
- *Hermes-shaped, recorded not judged:* `add-soul`
  (reads the two soul files from the other program's
  home — an input path, not this vault's home),
  `add-cron-backup` (the current crontab, via
  `crontab -l`), `github-backup` (pushes an encrypted
  backup to a git repo named in config or by flag).
  Whether they belong in the toaster set is docket 50,
  owned by E-098; this slice changed none of them.
- *Config:* `config set / get / list` over
  `config.json`.
- `--version` prints the program version, 2.0.0.

**Entry-password resolution** (`_resolve_password`),
for the credential an entry stores: a file named by
flag first, then an environment variable named by
flag, then a command-line value, then — for `add`
only, on a terminal — a hidden prompt. The third
shape is docket 128 (a value on a command line is
visible in process lists), owned by E-096; no
campaign work uses it.

## 5. Test state — measured this slice

The member's suite is one file,
`kista/tests/test_credstore.py`: **149 test functions
in 43 classes**, run in the member's own shape
(`python3 -m pytest tests -q` inside `kista/`, the
E-005 method; `cryptography` 50.0.2 present in this
environment).

- **Before this slice: 146 passed, 3 failed** —
  identical to E-005 / E-011 / E-012. The 3 failures
  were `TestVersionFlag`, `TestSubprocessInstall`,
  and `TestCrossPlatformChmod`, each reading or
  running the file at docket 5's hard-coded path
  under the other installation's home, where no file
  exists on this machine (`FileNotFoundError` in the
  raw log).
- **After this slice: 149 passed, 0 failed.** The
  harness now resolves the script beside the tests
  (`Path(__file__).parents[1] / scripts / credstore.py`),
  so the suite judges this tree's program — docket 5
  CLOSED in scope. Judging the real program exposed
  what the dead path had hidden: the version test's
  expectation was stale (`1.3.0`, against the
  program's true 2.0.0 in both `__version__` and
  `pyproject.toml`); the expectation now states the
  true version. The isolated-vault fixture also
  leaked two module paths (`VAULT_CONFIG`,
  `BACKUP_DIR` still resolved to the real default
  while their siblings were patched); both are now
  patched to the test's scratch vault, so no test
  can touch a real vault home through config or
  backup paths.

## 6. Docket 46 — executed here, CLOSED

One line of code carries the whole decision
(`credstore.py`, module level): the `KISTA_DIR`
fallback default is now `~/.ember/kista/` where it
was the other Kista's home territory. Proven three
ways at this slice's tree: a sandboxed import with
the variable unset resolves every vault path under
`<home>/.ember/kista/`; with the variable set, the
override wins exactly; and an end-to-end `init` +
`status` run against a scratch `KISTA_DIR` (the
E-011 §5 rule-3 shape) initialises a healthy vault
whose key and data files land at mode 0600. With the
change landed, rule 3's reason is gone for the
default itself; the rule's discipline (always set
`KISTA_DIR` to scratch in campaign work) stands
unchanged, because this campaign never keeps real
entries (E-093 §2).

What did *not* change, stated so nobody reads the
diff as a miss: `add-soul`'s two input paths still
name the other program's home — they are that
command's *subject matter* (docket 50 → E-098), not
this vault's address.

## 7. Standing findings this map hands on

- **The import-time install (docket 14) → proposed
  owner E-096.** If
  `cryptography` is absent, importing the program
  tries to install it with pip at import time and,
  on a PEP 668 machine, dies as a raw
  `CalledProcessError` traceback. This slice
  reproduced it live (a sandboxed-home probe whose
  user site-packages fell away). A first-run program
  for normal folks must say "this is missing, here
  is the fix" in plain words instead; the remedy's
  shape belongs with E-096's first-run work. The
  member suite's `TestSubprocessInstall` currently
  *pins* the install-via-subprocess shape as a
  security fix (no `os.system`); E-096's remedy must
  re-pin it consciously, not drift past it.
- **A new item (docket 130) — NEW → E-104.** The member's own
  documents still state the old default home:
  `ARCHITECTURE.md`, `ENTRY_TYPES.md`,
  `PHILOSOPHY.md`, `SYSTEM_VISION.md`, and `SKILL.md`
  each name the other program's credentials directory
  as this vault's default (the SKILL.md half is
  docket 49's ground; this item is the set). E-104's
  reconciliation corrects them against §6. The root
  `kista/` README states it too — and stands under
  the standing README law: it changes only by the
  owner's hand or word (its turn is E-195), never by
  this campaign's editing.
- **Docket 22** (the member pyproject declares no
  licence field though its MIT LICENSE stands beside
  it) stays where E-007 put it: Part XI.
- **Budget note:** the member's tracked weight moved
  only by this slice's two file edits; E-103 proves
  the vault's running cost on the toaster profile,
  and E-057's table is re-pinned at this slice with
  the new figure attributed there.

## Slice gate

Focal battery `tests/unit/test_toaster_kista_map_e094.py`
pins this map: the 14 types and 32 subcommands derived
from the code itself, the storage names, the Fernet
shape, the decided default proven by sandboxed probe
(unset and override), docket 5's in-tree resolution,
and the true version. Member suite and root gates are
recorded in the campaign state file at banking.
