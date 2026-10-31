# E-011 — The Two-Kistas Boundary Doc

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit ab54b0c (E-010 banked). The toaster-Kista side of this
boundary is proven from this tree (code, tests, git, and a
fresh runner pass this slice). The ai-folder side is stated
from Volmarr's own commissioning words in the roadmap (§2)
and the campaign's recorded evidence from purplelongship
(2026-10-30/31) — this slice did not access purplelongship,
and nothing on that side was re-proven here; it is graded
RECORDED, not MEASURED, wherever it appears. No credential
value, account address, or vault content from either side
is reproduced in this doc.*

## Headline — read this first, in plain words

**There are two programs called Kista, and they are not
the same program's two homes.** They share a name (Old
Norse *kista*: a strongbox, a chest), a spirit (self-owned,
encrypted, no king, no keeper), and a family history in
Runa's credential work. They do **not** share a codebase
to be synced, a vault to be merged, a keeper, or an update
road. Volmarr's ruling, recorded 2026-10-31, is the law of
this boundary:

> The Kista to keep up to date with the current GitHub
> version is the copy in Volmarr's ai folder; the Kista
> for the Smart Toaster is another program entirely, a
> separate thing that may need work at some point but is
> not this Kista.

- **Toaster-Kista** = `kista/` in this monorepo. This
  campaign's member. Its road is Part VI (E-093–E-106).
- **Ai-folder Kista** = the operational vault on
  purplelongship, kept current with the standalone GitHub
  repo `runafreyjasdottir/kista`. Runa/Hermes-side custody.
  **This campaign never touches it** — not its code, not
  its vault, not its entries, not its update road.

Any worker who finds "Kista" in a task, a doc, or a test
and cannot tell which of the two is meant must stop and
apply §5's rules before acting. Most of the confusion
this doc exists to prevent is already inside this tree
(§4): the toaster copy's own defaults, tests, and
references point at the other Kista's home.

## 1. Toaster-Kista — proven from this tree

| Fact | Evidence |
|---|---|
| Location | `kista/` in this repo; 2,770,218 bytes, 25 files (E-002) |
| History here | Exactly ONE commit: 4f81633, 2026-05-21, "kista" — a single import, never developed in this tree since |
| Identity | `pyproject.toml`: name `kista`, version **2.0.0**, author "Runa Gridweaver", requires-python ≥3.9, sole dependency `cryptography`; console script `kista = scripts.credstore:main`; licence MIT (E-007 verified) |
| Implementation | One file: `scripts/credstore.py`, 2,382 lines (2,383 at import); its own header still calls it "Runa's Credential Store" |
| Crypto / storage | Fernet (AES-128-CBC + HMAC-SHA256). Whole vault as one encrypted JSON file `vault.json.enc`, plus a **plaintext** `vault_meta.json` index (service names + timestamps only), plus a separate key file `.vault_key` (chmod 600, 44-byte base64 Fernet key, integrity-validated) |
| Vault location | `KISTA_DIR` env override; **default `~/.hermes/credentials`** — see hazard H1, §4 |
| Entry types in code | **14** schemas in `ENTRY_TYPE_SCHEMAS`: credential, apikey, sshkey, certificate, note, totp, license, identity, url, + the v2.0 additions astrology, character-sheet, rune-reading, tarot-reading, markdown |
| Command surface | ~25 subcommands: the credential core (init, add + typed adds, add-person, get, list, update, remove, check, search with date filters, generate-password, status, config) plus backup/restore, export/import, repair — and three Hermes-shaped extras: `add-soul` (backs up `~/.hermes/SOUL.md` + `runa-identity.md`), `add-cron-backup` (backs up the crontab), `github-backup` |
| Tests | One file, `tests/test_credstore.py` (2,066 lines). **Re-run this slice: 146 passed, 3 failed** — identical to E-005. All 3 failures are the subprocess tests (version flag, no-`os.system`, chmod wrapper): they execute a hardcoded path under the *other* installation, `~/.hermes/skills/devops/runa-credentials/scripts/credstore.py`, which does not exist on this VM (`FileNotFoundError`, seen in this slice's raw output). The in-process 146 judge this tree's code; the 3 judge a machine this tree does not control |
| Boot state | E-006: BOOTS (`--help` exit 0; `status` honest — vault not initialised, key MISSING, under a sandboxed `KISTA_DIR`; under a foreign HOME it crashes at import via its pip-install fallback, docket 14) |
| Consumers in this tree | **None in code.** `grep kista src/ tests/ config/ pyproject.toml` at root: zero hits. `docs/UNWIRED_INVENTORY.md` says it plainly: wired = no, "None planned. Could *plausibly* feed `EMBER_WELL_PASSWORD` via a `pgvector` secret resolver in V2, but not designed." Every other in-tree mention is documentation or the Verdandi check in §4/H2 |
| Purpose (roadmap) | The Smart Toaster's own credential program: Part VI finishes it as a program in its own right for tiny hardware — custody law (E-093), its own mapping (E-094), threat model (E-095), unlock for normal folks (E-096), per-program access (E-097), the toaster entry set (E-098), Ember core binding (E-100), budget proof (E-103) |

Its own docs (`ARCHITECTURE.md`, `PHILOSOPHY.md`,
`SYSTEM_VISION.md`, `ENTRY_TYPES.md`, `DOMAIN_MAP.md`,
`BUG_REPORT.md`, `CODE_REVIEW.md`, `SKILL.md`) are
substantial — and they describe the program in its
Hermes home: `SKILL.md`'s frontmatter names the skill
`runa-credentials`, carries `metadata.hermes`, gives the
homepage as the standalone GitHub repo above, and its
description still says "8 entry types" while its own
table and the code carry 14. That is lineage showing
through the import, not a description of a toaster
deployment. Part VI (E-104) reconciles the toaster
docs; this slice only draws the boundary.

## 2. Ai-folder Kista — RECORDED, not measured here

Stated from the roadmap (§2, Volmarr's commissioning
words) and the campaign's recorded purplelongship
evidence of 2026-10-30/31. This campaign has no clone,
no checkout, and no access grant for this side.

| Fact | Source |
|---|---|
| What it is | "Runa's strongbox, the one Heimdall uses" — the operational, self-owned encrypted credential vault for Volmarr's Hermes/Runa line (roadmap §2) |
| Upstream | Standalone GitHub repo `runafreyjasdottir/kista`, main head recorded 2026-10-30 as `54e31f1090`, pushed 2026-06-07; built by Runa Freydisdottir, Volmarr's Hermes agent. The ai-folder copy is the one **kept up to date with that GitHub version** (Volmarr's ruling, 2026-10-31) — a full month of upstream movement after the toaster copy's 2026-05-21 import |
| Homes on purplelongship | Recorded copies at `/home/volmarr/ai/ember/kista` and in his Documents GitHub checkout of this monorepo (2026-10-30 record). Which of those is the live deployment is that side's own record, not this doc's to settle |
| Live contents | A working vault with real entries: an in-tree operational record (`docs/phd-2040/research/MASTER_TODO.md`) marks "Kista v2.0 — 149 tests, encrypted vault, 75 entries healthy". On 2026-10-30 Volmarr stored his Second Life credentials in Kista on purplelongship **and verified them** ("stored and verified"), and the Heimdall login then ran from that custody — the password itself was never recorded in campaign records |
| Keeper / update road | The Hermes/Runa side's own work, under Volmarr's word there. Never this campaign's |
| Entry ambitions | The wider set is *its* road: E-098 records the toaster set separately and does not silently merge the two. The in-tree snapshot already shows how wide the family ambition runs (states of soul, cron, readings, character sheets) — in the ai-folder program those are live features for a live agent, not a toaster specification |

## 3. What they genuinely share

- **The name and the word:** *kista*, the household
  strongbox — short, self-documenting, Norse without
  pretence (`kista/SYSTEM_VISION.md` argues the naming
  for the family as a whole).
- **The spirit, verbatim in both houses:** self-owned,
  local, encrypted at rest with Fernet, no cloud, no
  subscription, no telemetry, no phone-home —
  "No king, no keeper" (`kista/PHILOSOPHY.md`; the
  Yggdrasil sibling doc uses the same motto).
- **The lineage:** both descend from Runa's credential
  work for the Hermes line. The toaster copy is a
  2026-05-21 snapshot of that work imported into this
  monorepo; the ai-folder program is the living line
  that kept moving (GitHub head 2026-06-07). Shared
  ancestry is a fact. **Shared ancestry is not shared
  custody, and it is not a sync instruction** — the
  roadmap (§6) forbids merging the two by fiat.

## 4. The confusion hazards — all found in this tree

- **H1 — The toaster copy defaults into the other
  Kista's home.** Unconfigured, `kista/scripts/
  credstore.py` puts its vault in `~/.hermes/
  credentials` (line 76) — Hermes territory, the
  ai-folder program's world. Run the toaster program
  bare on a Hermes machine and the two vaults share a
  directory shape and filenames (`vault.json.enc`,
  `.vault_key`, `vault_meta.json`). This is the single
  most dangerous conflation in the tree, and it is in
  code, not prose. (→ docket 46; Part VI, E-093/E-094.)
- **H2 — A third vault shape exists in a consumer.**
  Verdandi's Mímir health check (`heartbeat/checks/
  mimir.py:363`, and its configuration reference) looks
  for `~/.kista/vault.db` — a **SQLite** database with
  an `entries` table. Neither Kista in this doc writes
  that shape: credstore writes an encrypted JSON file.
  Against a real credstore vault the check can only
  report not-found or error. Three "Kista vaults", three
  locations, two formats, one name. (→ docket 47.)
- **H3 — The toaster tests judge the other
  installation.** §1: 3 of the suite's tests exec
  `~/.hermes/skills/devops/runa-credentials/scripts/
  credstore.py` by absolute home path (test file
  line 32). On any machine without that Hermes skill
  installed they fail; on a machine with it, they pass
  or fail on code that is not in this repo. (E-005
  docket item 5; re-proven this slice.)
- **H4 — An operational record lives in the toaster
  tree.** `kista/references/known-accounts.md`
  (2026-05-09) is the *ai-side* vault's account-status
  ledger — service names and working/pending statuses
  for Runa's live accounts; its own header states the
  rule that credentials themselves live only in the
  encrypted vault, and none are in the file. It is a
  custody mismatch sitting in this repo: evidence
  about the other Kista, filed inside this one.
  (→ docket 48. Not removed here — removals are
  Volmarr's word.)
- **H5 — A fourth, aspirational Kista in design
  docs.** The Yggdrasil corpus (`docs/yggdrasil/
  siblings/15_SIBLING_KISTA.md`, `architecture/
  33_THE_KISTA_SECRET_PLANE.md`) designs a secret
  plane — `~/.ember/kista.vault`, `kista://` URI
  references, a `KistaClient` adapter in `src/ember/
  yggdrasil/kista/` — none of which exists in code
  (zero root `src/` hits, §1), and its "8 entry types"
  figure is stale against the code's 14. Design
  intent, not a third program; Part VIII/VI read it
  as a proposal to judge, never as a description.
- **H6 — Same version number, different programs.**
  Both sides answer to "Kista v2.0". A version string
  is not identity: the toaster copy is v2.0.0 as
  imported 2026-05-21 and frozen since; the ai-folder
  line is v2.0 as a living program whose GitHub head
  moved a month later. Cite a Kista by **which one +
  where + when**, never by version alone.

## 5. Custody rules (binding on every campaign worker)

1. **Name the Kista.** In every doc, commit, test, and
   report, write *toaster-Kista (`kista/` in this
   repo)* or *ai-folder Kista (purplelongship /
   standalone GitHub)*. Bare "Kista" is allowed only
   where the referent is already unambiguous in the
   same paragraph.
2. **This campaign works only on toaster-Kista.** The
   ai-folder Kista — its code copies, its vault, its
   entries, its GitHub repo, its update road — is out
   of scope entirely. Reading campaign records about
   it (as this doc does) is the whole of our contact.
3. **Never run toaster-Kista unconfigured.** Any
   execution sets `KISTA_DIR` to a sandbox inside the
   slice's own scratch space first (the E-006 method).
   The `~/.hermes` default must never be allowed to
   resolve on any machine, VM included.
4. **Never point a toaster test, fixture, or probe at
   the other installation's paths.** A test that needs
   the `~/.hermes` copy is a defect (H3), not a setup
   step; no worker "fixes" a red kista suite by
   installing or linking the Hermes skill.
5. **No entry ever crosses.** No export, import, copy,
   or migration of vault entries between the two
   programs, in either direction, under any slice.
   Whether the two *formats* could ever exchange
   entries is a study question for E-099 and only
   E-099; studying the format is not moving data.
6. **No sync in either direction.** The toaster copy
   is never "brought up to date" from the standalone
   GitHub repo, and the ai-folder copy is never
   updated from this tree. If a fix seems to belong on
   both sides, it is written twice, by each side's own
   keeper, under separate words from Volmarr.
7. **Real credentials live only in the ai-folder
   Kista's custody** (today's reality: e.g. the
   Heimdall/Second Life login). The toaster program
   holds no real entries anywhere this campaign knows
   of, and no slice may give it any outside Part VI's
   own custody law (E-093) and Volmarr's word.
8. **The boundary is a fact, not a merger waiting.**
   Roadmap §6: no merging of the two Kistas by fiat —
   their boundary is documented here, bridged only if
   E-099 proves a bridge wise, and never papered over.

## 6. What the later slices inherit

- **E-013** (config & secrets census): cite H1/H2 as
  the known shape collisions; `known-accounts.md`
  (H4) is a status ledger, not a credential file —
  any credential-shaped *value* found anywhere else
  in plain files is still a defect under E-013's rule.
- **E-016** (docket): items 46–50 below.
- **E-093/E-094** (Part VI opening): the toaster
  vault's default home is a decision to take and fix
  there (H1) — a toaster-profile default that is not
  another program's home directory.
- **E-097/E-098**: per-program access and the toaster
  entry set are decided from §1's measured surface;
  the Hermes-shaped commands (`add-soul`,
  `add-cron-backup`, `github-backup`) are toaster
  questions there, not assumptions.
- **E-099**: the interop study starts from §1 + §4/H2:
  one encrypted-JSON file vault, one consumer expecting
  SQLite — plus the ai-folder side's format, which
  that slice must establish from records or Volmarr's
  word, since this campaign does not inspect that side.
- **E-104/E-105**: the boundary doc's final form and
  the user-facing naming kindness build on §5 rule 1;
  `SKILL.md`'s stale "8 entry types" and Hermes-skill
  framing are toaster-doc questions there.

## Carried to the E-016 docket

(46) Toaster-Kista's default vault directory is the
other Kista's home territory: `KISTA_DIR` unset →
`~/.hermes/credentials`, with the same filenames the
Hermes deployment uses (H1). A toaster-profile default
is undecided and unbuilt; assigned to Part VI
(E-093/E-094). Until then, campaign rule §5.3 binds.
(47) Verdandi's Mímir check expects a Kista vault at
`~/.kista/vault.db` (SQLite, `entries` table) that
neither Kista writes (H2); against a real credstore
vault it reports not-found/error. One of the check,
the config reference, or the vault shape is wrong;
assigned to Part IV (Verdandi) with Part VI consulted.
(48) `kista/references/known-accounts.md` is the
ai-folder vault's operational status ledger (H4)
sitting inside the toaster tree. Whether it belongs in
this repo is Volmarr's word; recorded, not removed.
(49) The toaster tree's own Kista docs describe the
Hermes deployment as the program's home (`SKILL.md`
frontmatter: skill name `runa-credentials`, Hermes
metadata, standalone-repo homepage; description's
"8 entry types" stale against the code's 14 and its
own table). Doc-boundary reconciliation assigned to
Part VI (E-104); this slice touches no Kista doc.
(50) Three Hermes-shaped commands ship in the toaster
copy — `add-soul` (reads `~/.hermes/SOUL.md` +
`runa-identity.md`), `add-cron-backup`, `github-backup`
— features of a live agent's vault carried into the
tiny-machine program. Whether they belong in the
toaster set is undecided; assigned to Part VI (E-098).

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Kista's own suite
re-run this slice as boundary evidence: **146 passed,
3 failed**, the 3 being hazard H3 exactly. Doc-only
slice: no code touched, no README touched, no push.
The ai-folder side was not accessed; its facts are
recorded evidence, graded as such in §2.

*Filed by the E-011 slice, 2026-10-31. Next: E-012 —
the two-memories census (mempalace vs mimir-well).*
