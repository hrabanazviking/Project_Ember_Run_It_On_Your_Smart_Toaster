# E-013 — Config & Secrets Census

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit e945b51 (E-012 banked, with its corrections). Method:
the tracked tree enumerated via `git ls-files` (3,242 files;
2,754 text-shaped files scanned), 57 config-shaped files
inventoried, high-confidence secret patterns scanned over
every tracked text file, credential-shaped assignments
classified by `git grep`, and every documented env key
checked for a live consumer in `src/`. **No credential
value is reproduced anywhere in this doc** — hits are
recorded as file, line, shape, and classification only.
Raw inventories live in
`~/workspace/.verify-tmp/ember-e013/`.*

## Headline — read this first, in plain words

**No real credential was found in any plain file in this
tree.** That is the good news, and it is proven, not
assumed: every high-confidence secret-shaped string in
2,754 tracked text files was individually classified, and
every single one is a test fixture, a placeholder, a
documentation template, or a false positive (§3). The
core's one real secret path — the Well password — is
handled the best way in the whole tree: environment
variable, then keyring, then a file that must be
mode-600 or it is refused, and the value is never logged.

The defects are about *shape*, not leaks:

- **The root `.env.example` is a Runa-era fossil.** It
  tells an operator to copy it to `~/.runa/secrets/`
  and fill in a dozen provider and bridge keys — and
  **not one of those keys has a consumer in the Ember
  core**. An operator who follows it puts real secrets
  in a file nothing in this project reads. (→ docket 55.)
- **There is no one config shape.** The core, Verdandi,
  mempalace, mimir-well, bifrost, kista, and Hamr each
  configure differently — YAML+env, YAML+prefixed-env,
  JSON+env, dataclass-only, env-only, YAML-specs — and
  astrology-engine has no config shape at all. E-033's
  "config for humans" inherits the whole map. (→ docket 56.)
- **The one custody-sensitive plain file stays as
  E-011 found it:** `kista/references/known-accounts.md`
  holds account *identifiers* (addresses/identities,
  vault key names, statuses) — no credential values,
  re-verified this slice — and stays under its existing
  docket item 48, awaiting Volmarr's word. It is not
  renumbered here.

## 1. The config shapes, member by member

| Member | Shape | Live file | Env surface | Secrets handling |
|---|---|---|---|---|
| Ember core (`src/ember/`) | Typed dataclasses (`schemas/config.py`); loader composes defaults → YAML or TOML file → env overlay (ADR 0008) | `~/.ember/config/ember.yaml` (or `.toml`); templates `config/ember.example.yaml` (+ sources/storage example markers) | Only `OLLAMA_HOST` in the overlay (`config/overlay.py`) | Well password only, via the pgvector resolver (§2) — exemplary |
| Verdandi heartbeat | YAML file + in-code `DEFAULTS` (319-line `heartbeat/config.py`), SIGHUP reload | `Verdandi/config/heartbeat.yaml` (all operational values, no secrets) | Generic `VERDANDI_<SECTION>_<KEY>` override loop over `os.environ` | No secret keys in its config at all |
| Verdandi Eir | Dataclass-only (`verdandi/eir/config.py`) | None — code defaults | None | None; its DB defaults point at `~/.hermes/...` (kin to docket 51) |
| mempalace | JSON file + env, priority env > file > defaults (`mempalace/config.py`) | `~/.mempalace/config.json` | `MEMPALACE_*` / `MEMPAL_*` (palace path, languages, embedding device, …) | LLM keys env-only: `LLM_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` read from env in `llm_client.py` / `closet_llm.py` — never from its config file. Good shape |
| mimir-well | JSON file + env (`src/mimir_well/config.py`); creates a default file (O_EXCL) if absent | `~/.mimir_well/mimir-well-config.json` | `MIMIR_DB_PATH`, `MIMIR_BACKUP_REPO` — but its Eye reads `MIMIR_DB_PATH` + `FACT_DB_PATH` separately (`eye/app.py`) | No credential keys; `backup_repo` is a plain config string (a credential-bearing repo URL *could* be pasted there — no such value found; noted for E-093) |
| bifrost | Dataclass-only (`src/bifrost/config.py`), no file or env loader at all | None — code defaults, incl. `~/.hermes/memory/...` paths (docket 51) | None | No secret fields |
| kista (toaster) | The vault *is* the config for credentials; CLI-driven | Vault at `KISTA_DIR` (default `~/.hermes/credentials` — the collision of docket 46) | `KISTA_DIR`; vault passphrase via `--password-env <VAR>` indirection (the passphrase itself is never a CLI value) | Fernet-encrypted vault (E-011); passphrase-by-env-name is a sound shape |
| Hamr | YAML character *specs* (examples + presets), not program config | `Hamr/examples/*.yaml`, `build_output/` presets | None for secrets | No credential fields anywhere |
| seidr_engine | In-code `PoemConfig` dataclass only | None | None | None |
| astrology-engine | **No config shape at all** — no packaging file (E-007), no config file, no env reads in its module | None | None | None — and its "pyswisseph required" silent-exit behaviour is docket 16 |
| dictionary (cleasby-vigfusson) | Next.js env | None tracked | `REVALIDATE_SECRET` compared from `process.env` in `src/pages/api/revalidate.ts` | Correct env-only shape |
| Open-VTT | Godot `export_presets.cfg` only | `Open-VTT/Godot/export_presets.cfg` | None | No credential fields found |
| CloakBrowser (vendored) | Python/JS config modules + env (`CLOAKBROWSER_*`: cache dir, binary path, download URL…) | Its own modules | `CLOAKBROWSER_*` | Proxy credentials travel inside proxy URLs in its API, docs, and tests (§3) — vendored shape, never rewritten; Ember must not adopt it (→ docket 58) |
| deploy/ | Markdown recipes only | — | States the rule itself: "**No secrets in any deploy file.** Use environment variables, `EnvironmentFile=`, or operator-side secret stores (`~/.ember/secrets/`…)" | The house rule, written down in the right place |

Root `.gitignore` is on the right side of all of this:
`.env`, `.env.*` (with `!.env.example` the sole
exception), `secrets/`, and `*.secret*` are excluded,
and **no tracked `.env`, `.pem`, `.key`, or vault file
exists** (`git ls-files` checked by name).

## 2. The core's real secret path — the tree's best shape

`src/ember/well/brunnr/pgvector/secrets.py` is the only
place the Ember core resolves a credential, and it is
the model the rest of the tree should be judged against
(ADR 0010 §2.5):

1. Env var (`EMBER_WELL_PASSWORD`, name overridable via
   `secret_env` in config — the config holds the *name*,
   never the value);
2. OS keyring (`keyring.get_password("ember-well",
   <username>)`, lazy/optional — E-007 noted `keyring`
   is declared in no extra, docket 20's kin);
3. A file at `secret_ref` that **must be exactly
   mode 0o600** — any other mode is refused with an
   operator-readable reason;
4. Otherwise a typed failure whose reason lists which
   sources were tried — and never the value. The
   module's contract states it outright: the secret "is
   **never** logged or echoed back through any return
   value".

Its dedicated tests (`tests/unit/
test_brunnr_pgvector_secrets.py`) are part of the root
suite's green body. E-093's custody law should adopt
this resolver's order as the campaign standard.

## 3. The secrets scan — every hit, classified

High-confidence patterns were scanned over all 2,754
tracked text files (GitHub tokens `ghp_*`/`github_pat_*`,
OpenAI `sk-*`, AWS `AKIA*`, private-key blocks, JWTs,
bearer literals, and password-bearing URLs), and
credential-shaped *assignments* were separately counted
by `git grep`. Results:

- **GitHub tokens: 0. JWTs: 0. Bearer literals: 0.**
- **Private-key blocks: 7 hits, all fixtures/templates.**
  Four in `kista/tests/test_credstore.py` — synthetic
  key material stored into an *isolated test vault* to
  prove the credstore round-trips it (the tests' whole
  purpose). Two in `tests/unit/
  test_tool_read_local_file.py` — fake keys used to
  prove the file-reading tool refuses/redacts them.
  One in `kista/SKILL.md:120` — a shell heredoc
  *template* whose key body is literally `...`, inside
  instructions that say never to paste a private key
  into chat.
- **AWS-shaped keys: 2 hits, both synthetic.**
  `kista/tests/test_credstore.py` (in
  `test_add_apikey`, against the isolated vault): the
  suffix is a sequential digit/letter pattern — test
  data by construction, not a leaked key.
- **`sk-` shape: 1 hit, a false positive** — hyphenated
  English prose in a PhD-2040 paper under `docs/`
  (2 hyphens, 0 digits; no key structure).
- **Password-bearing URLs: ~150 hits, one family.**
  Overwhelmingly CloakBrowser's vendored proxy docs and
  tests, where the password segment is the literal word
  `pass` in 90 cases and short obvious test tokens in
  the rest (its own proxy-parsing fixtures). The few
  house-side hits are documented placeholders of the
  `postgresql://user:…@host` shape in the Brunnr
  references and this doc's own kin — no real password
  in any of them.
- **Assignments in code/config files** (`.py/.yaml/
  .toml`): of 173 credential-key assignment lines,
  exactly **8** carry a quoted value of 12+ characters —
  and all 8 are test fixtures (7 in kista's credstore
  tests, 1 in mempalace's LLM-client tests). Everything
  else is an env lookup, a parameter name, an empty
  default, or a placeholder.
- **Docs/codex assignments** are discussion, not
  configuration: the codices quote and analyse
  *third-party* code (a Letta password lifecycle, Super
  Agent Party managers passing a local dummy key —
  SAP's own notes flag a "super secret literal" in that
  upstream code). No Ember credential appears in any
  codex.

**Verdict for E-093:** the campaign's custody problem
is not leakage — there is none in plain files — it is
that the *documented* places to put secrets
(`.env.example`, §4) do not match the *real* places the
code reads (§2, §1). Custody law must be written from
the code's truth.

## 4. The `.env.example` fossil (the census's one real trap)

The tracked root `.env.example` is titled "Runa Agent",
instructs copying to `~/.runa/secrets/runa.env`, and
documents: `RUNA_HOME`, `RUNA_CONFIG`, `RUNA_LOG_LEVEL`,
four model-provider keys (OpenRouter, Nous, Anthropic,
OpenAI), three chat-bridge credentials (Discord,
Telegram, Matrix), a Home Assistant token, and an MCP
config path under `~/.runa/`.

Checked one by one against `src/`: **every one of those
names has zero consumers in the Ember core** (grep over
`src/**/*.py`: 0 files each). The core's actual env
surface is exactly two names — `OLLAMA_HOST` and
`EMBER_WELL_PASSWORD` (§2). The file's own hygiene
advice is good (never commit values, audit-log redaction
patterns, rotate on exposure) — but it describes the
*predecessor's* wiring, under the predecessor's home
directory, for adapters this tree does not contain.
Kin to the stale `THIRD_PARTY_NOTICES.md` (E-003/E-007):
the fork renamed the product but not this operator
document. An operator following it would (a) conclude
Ember needs cloud keys it never reads — against the
project's tiny/local soul — and (b) write real secrets
into a file whose only possible reader is a stale Runa
install. (→ docket 55, assigned to E-033, where the
one human config surface is built; the file itself is
an operator doc, not a README, so a later slice may
correct it in scope there.)

## 5. Identifiers in plain files — the known-accounts ledger

Re-verified this slice (E-011's H4, docket 48):
`kista/references/known-accounts.md` is a vault *status*
ledger — service names, vault key names, account
addresses/identities, and statuses, including an
SSH-keys section. The high-confidence scan found **no
credential value** in it (no token, key block, or
password shape), and this census reproduces none of its
identifiers. But key *names* plus account *identities*
are exactly the map an attacker would want beside a
stolen vault, so under E-013's rule ("anything
credential-shaped in plain files is a defect") it
stands confirmed as custody-sensitive material in a
plain tracked file. Its disposition remains Volmarr's
word under docket 48 / E-093 — this census changes
nothing and removes nothing.

## 6. What the later slices inherit

- **E-014** (dead/duplicate census): `.env.example`'s
  adapter sections are dead documentation for absent
  adapters (kin to E-003's unregistered-material
  findings) — classify as fossil docs, not dead code.
- **E-016** (docket): items 55–58 below.
- **E-033** (config for humans): §1's table is the
  fragmentation it must unify; §4 is its first fix;
  the core loader (defaults → file → env, ADR 0008)
  is the shape to unify *toward*.
- **E-093** (custody law): §2's resolver order is the
  proven standard; §3's verdict (no leakage, shape
  mismatch only) is its starting fact; docket 48's
  ledger is its first case.
- **E-187** (security audit): docket 57's fixture
  discipline is its concern — today's fixtures are
  proven synthetic, and keeping them obviously
  synthetic is what keeps a future scanner honest.

## Carried to the E-016 docket

(55) Root `.env.example` is a pre-fork Runa fossil: it
directs operators to place a dozen provider/bridge
secrets in `~/.runa/secrets/runa.env`, and **none** of
its documented keys (`RUNA_*`, OpenRouter/Nous/
Anthropic/OpenAI keys, Discord/Telegram/Matrix tokens,
Home Assistant token) has any consumer in `src/ember`
— the core's true env surface is `OLLAMA_HOST` +
`EMBER_WELL_PASSWORD` only. It misdescribes the
product (cloud keys for a local companion) and
misplaces secrets. Assigned to E-033 (config for
humans); correction is an operator-doc edit there,
in scope, preserving the file's genuine hygiene rules.
(56) Config fragmentation across members: at least
seven distinct shapes (§1) — core YAML/TOML+one-env
overlay; Verdandi YAML+generic prefixed env; Verdandi
Eir and bifrost dataclass-only with `~/.hermes`
defaults and no loader; mempalace JSON+env; mimir-well
JSON+env with its Eye reading a partially different
env set; kista env-only vault location; Hamr YAML
specs; astrology-engine none at all. No member can be
configured by a method learned from another. Assigned
to E-033/E-037 (the one config surface + core API
freeze), with docket 51 (the three Mímir DB paths) as
its sharpest single instance.
(57) Credential-shaped test fixtures are proven
synthetic (sequential AWS-shaped suffix, isolated-vault
private keys, fake keys in refusal tests — §3) but are
indistinguishable from leaks to any pattern scanner
that does not read context. Any future secret-scanning
gate (E-187) will false-alarm on exactly these files
unless fixtures stay obviously synthetic and the gate
carries a classified allowlist. Recorded as a
discipline item for E-187 / Part XI stewardship — not
a leak, and no fixture is to be "cleaned up" silently:
the credstore tests *need* key-shaped data.
(58) CloakBrowser's shape embeds proxy credentials in
URL strings throughout its vendored docs, API, and
tests (password segment literally `pass` in 90 cases;
the rest its own parsing fixtures). Vendored code is
never rewritten (roadmap §3), so the item is a
*boundary* rule for Part XI: Ember's own code must
never adopt URL-embedded credentials as its shape —
its proven shape is §2's resolver — and E-178's
browser-safety ladder inherits the note that any proxy
Ember configures through the wrapper takes its
credentials from custody (E-093), not from a URL in a
config file.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env; `TMPDIR` redirected to the
workspace overlay because the VM's 512 MB `/tmp` was
full at run time — the E-012/docket-54 pressure, noted
here as method, nothing deleted): **546 passed,
6 failed, 12 skipped** — identical to the opening
baseline; the 6 failures are the proven environment
failures. Doc-only slice, no code touched, no README
touched, no push (but see the state file: the push
policy recorded there is superseded for slices banked
from E-013 onward by Volmarr's 2026-10-31 standing
go-ahead — this slice's commit is pushed under it and
verified by `ls-remote`).
