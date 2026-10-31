# E-033 — Config for Humans: One Surface, Sane Defaults, Every Key in Plain Words

*Part II, slice E-033. Docket 55 CLOSED; docket 56 closed for the
Ember core (its member half stays with E-037, where the core's API
— and with it the members' binding shape — is frozen).*

## The one surface, stated plainly

A person who runs Ember has exactly **one** config file to know
about:

- `~/.ember/config/ember.yaml` — or, on an install that has no
  PyYAML, `~/.ember/config/ember.toml` with the same keys in TOML
  shape (the E-032 shape: the first-run wizard writes whichever
  this machine can read back). If both exist, YAML wins and Ember
  says so with a warning.
- No file at all is a complete, working configuration: every key
  has a default, and the defaults are the sane ones (below).
- A key Ember does not know is **refused at startup, with the key
  named** (and a did-you-mean where one is close) — a typo can
  never quietly become a different companion. This refusal is
  what makes "one surface" a fact instead of a hope: nothing can
  fork the surface by accident. Pinned by test, including a
  fossil key (`openai_api_key`) refused by name.

On top of the file, exactly three thin layers, none of them a
second surface to learn:

1. **Environment — exactly two variables** (E-013's live keys,
   re-verified against the code this slice): `OLLAMA_HOST`
   (where Ollama lives; also moves the embedding endpoint) and
   `EMBER_WELL_PASSWORD` (only for a pgvector Well; the config
   may rename it via `brunnr.pgvector.secret_env`, the value
   itself never goes in any file). Ember does **not** load a
   `.env` file; the variables count only when set in Ember's
   real environment.
2. **Command-line flags** (e.g. `--allow-tools`) — one run only,
   never saved.
3. **Per-persona files** (`~/.ember/personas/<id>.json`, E-025)
   and **identity** (`identity.json`, written by the wizard) are
   *content*, not settings surfaces: they say who the companion
   is, not how the program behaves, and both live inside the
   same config root so custody of the folder is custody of the
   companion (E-020).

## What was wrong, and what changed

- **Docket 55 CLOSED — the `.env.example` fossil is replaced.**
  The root `.env.example` was a pre-fork Runa document: it sent
  operators to `~/.runa/secrets/runa.env` to fill in a dozen
  provider/bridge keys that **no code in this tree reads**
  (E-013 §4). It now documents exactly the two live variables,
  says plainly that Ember does not load a `.env` file, and
  points at the one config file. An operator can no longer be
  led to write real secrets into a file nothing reads, nor to
  believe Ember needs cloud keys it never asks for.
- **The template now documents every live key.** Walking the
  `EmberConfig` dataclass tree against
  `config/ember.example.yaml` found four whole areas the
  template never mentioned: the `conversation` section (E-021's
  history window — the setting a normal user is *most* likely
  to want), the `mcp` section (helper programs, both directions
  defaulted off), `funi.streaming`, and three cognition keys
  (`expected_api_major`, `num_drafts`, `tf_config`) plus
  `funi.aesir.timeout_ms`. All are now in the template, each
  with a plain-words comment and its default. A test walks the
  dataclass tree and fails if any field is ever undocumented
  again — the table below is the same list, for humans.
- **The excerpt files no longer promise a split.**
  `config/storage.example.yaml` claimed its keys lived apart
  "until per-realm split lands", and `config/sources.example.yaml`
  reserved itself for a future registry file. Both now state
  plainly that they are **not config files** — storage is a
  copy-paste excerpt of the one file's `brunnr:` section, and
  Smiðja sources are given on the command line
  (`ember well ingest <path>`), with no registry shape to learn.
- **Defaults audited, none changed.** Every default in the
  table was read from a constructed `EmberConfig()` this slice.
  They are sane for a stranger's first day: local model on
  localhost, local Well in Ember's own folder, tools/MCP/
  cognition all off, replies streaming, history window at the
  pi profile. No default needed changing — the defect was
  documentation and the fossil, not the numbers.
- One behaviour worth stating, found by the slice's own test:
  a path **read from the file** is `~`-expanded by the coercion
  layer at load (its documented design), while a **default**
  path stays unexpanded in the schema and is expanded when
  used. Both land on the same file; the difference is only
  when the `~` resolves.

## Every key, in plain words

Defaults are the value you get when the key is absent.

| Key | Default | What it does, plainly |
|---|---|---|
| `identity.name` | `"Ember"` | The name you call your companion. |
| `identity.role` | `"your small local AI companion"` | The one-line description it opens with. |
| `personas.active` | `""` (unset) | Which persona file to be. Unset → `default.json` if you have one, else your wizard identity. Naming one that does not load is an error, never a quiet swap. |
| `conversation.profile` | `pi` | Machine size for history carrying: `toaster` / `phone` / `pi` / `laptop`. |
| `conversation.token_budget` | unset → profile's (512 / 1024 / 2048 / 4096) | Rough size of past talk carried into each turn. |
| `conversation.max_episodes` | unset → profile's (3 / 5 / 8 / 12) | Most past exchanges kept word-for-word. |
| `conversation.summarise_dropped` | `true` | What falls out of the window is summarised, not silently forgotten. |
| `cognition.enabled` | `false` | Turn the optional ThoughtForge thinking layer on. Off = Ember's own turn is the mind. |
| `cognition.provider` | `"thoughtforge"` | Which cognition layer; the only one in this build. |
| `cognition.profile` | `pi` | Machine size for the layer; `toaster` refuses it outright. |
| `cognition.expected_api_major` | `1` | The ThoughtForge API generation Ember was written against; a different one is refused, not adapted to. |
| `cognition.model_path` | unset | A model file for ThoughtForge; unset = it runs knowledge-only. |
| `cognition.memory_dir` | `~/.ember/thoughtforge/memory` | Where ThoughtForge keeps its memory — inside Ember's folder on purpose. |
| `cognition.db_path` | `~/.ember/thoughtforge/knowledge.db` | ThoughtForge's knowledge file. |
| `cognition.num_drafts` | unset → profile cap (phone/pi 1, laptop 2) | Cap on draft answers per turn; a cap, never a raise. |
| `cognition.tf_config` | `{}` | Extra settings passed to ThoughtForge exactly as written. |
| `funi.runtime` | `ollama` | Which model program Ember talks to. Only `ollama` and `aesir` are built; the rest answer with a typed "not installed". |
| `funi.streaming` | `true` | Replies appear word by word; `false` = whole replies at once. |
| `funi.ollama.base_url` | `http://localhost:11434` | Where Ollama lives on this machine. `OLLAMA_HOST` overrides it. |
| `funi.ollama.model` | `phi3:mini` | The Ollama model that does the talking. |
| `funi.ollama.temperature` | `0.7` | How adventurous replies are (higher = wilder). |
| `funi.ollama.top_p` | `0.9` | A second creativity dial, kept with temperature. |
| `funi.ollama.num_predict` | `1024` | Longest reply, in tokens, per turn. |
| `funi.aesir.base_url` | `http://127.0.0.1:18434` | Where the Aesir service lives (this machine only). |
| `funi.aesir.model` | `""` | Expected Aesir model; empty accepts what the service reports, a mismatch is refused. |
| `funi.aesir.api_key_file` | `~/.config/aesir/service.key` | The FILE holding the Aesir key — a reference, never the key itself. |
| `funi.aesir.temperature` / `top_p` | `0.7` / `0.9` | As Ollama's. |
| `funi.aesir.max_tokens` | `256` | Reply ceiling; the service's own default, never raisable past it. |
| `funi.aesir.timeout_ms` | unset | Per-request limit; unset = the service's own. |
| `strengr.health_check_timeout_s` | `5.0` | How long to wait for the memory store before calling it disconnected. |
| `strengr.retry_attempts` | `3` | Tries before Ember works without the store for the session. |
| `strengr.retry_backoff_max_s` | `30.0` | Longest pause between those tries. |
| `brunnr.backend` | `sqlite_vec` | Which memory store: the local file, or `pgvector` for a shared one. |
| `brunnr.embedding_dim` | `768` | Size of the meaning-numbers; must match the embedding model. |
| `brunnr.sqlite_vec.path` | `~/.ember/well/store.db` | The local memory file itself. |
| `brunnr.sqlite_vec.wal_mode` | `true` | Safer write mode for that file; leave on. |
| `brunnr.pgvector.url` | *(required when pgvector is chosen)* | Where the shared store lives. No default — choosing it is a deliberate act. |
| `brunnr.pgvector.secret_ref` | `~/.ember/secrets/well.password` | Password FILE (must be mode 600); third in line after env and keyring. |
| `brunnr.pgvector.secret_env` | `EMBER_WELL_PASSWORD` | Name of the env variable checked first for that password. |
| `brunnr.pgvector.use_keyring` | `true` | Whether to try the computer's keyring for the password. |
| `brunnr.pgvector.keyring_service` | `"ember-well"` | The keyring entry's name. |
| `brunnr.pgvector.username` | unset → from the URL | The store's user name. |
| `brunnr.pgvector.connect_timeout_s` | `10.0` | How long connecting to the shared store may take. |
| `brunnr.pgvector.vector_index` | `hnsw` | How the shared store indexes meanings; leave unless you run the store. |
| `brunnr.pgvector.vector_metric` | `cosine` | How meanings are compared there. |
| `brunnr.pgvector.schema` | `public` | The store's schema name. |
| `brunnr.pgvector.read_only` | `false` | `true` = Ember may look but never write — for a store someone else manages. |
| `smidja.embedding.endpoint` | `http://localhost:11434/api/embed` | Where text is turned into meaning-numbers. Follows `OLLAMA_HOST`. |
| `smidja.embedding.model` | `nomic-embed-text` | The model that makes those numbers. |
| `smidja.embedding.batch_size` | `32` | How many pieces are numbered at once while learning new material. |
| `smidja.chunker.max_chars` | `2000` | Biggest single piece new material is cut into. |
| `smidja.chunker.target_chars` | `1684` | The piece size cutting aims for. |
| `smidja.chunker.min_chars` | `200` | Smallest piece kept; smaller scraps are merged. |
| `smidja.chunker.overlap_chars` | `0` | How much neighbouring pieces overlap. |
| `smidja.chunker.boundary_preference` | `paragraph` | Where cuts prefer to fall: paragraph / sentence / word / char. |
| `smidja.journal.root` | `~/.ember/state/smidja_progress/` | Where half-finished learning jobs keep their notes. |
| `smidja.journal.heartbeat_s` | `30` | How often a learning job notes "still working". |
| `smidja.journal.stale_heartbeat_s` | `600` | Silence after which a learning job counts as abandoned. |
| `tools.enabled` | `false` | Whether Ember may use tools in chat at all. Off until you opt in. |
| `tools.standing_trust` | `false` | Auto-approve read-only per-call tools (still recorded); risky tools and guarded arguments always ask anyway (E-026). |
| `tools.approval_overrides` | `{}` | Per-tool stricter settings (`per_call` / `forbidden`); can tighten, never loosen past a tool's own floor. |
| `tools.allow_private_addresses` | `false` | Whether the web-fetch tool may reach home-network addresses. |
| `tools.audit_root` | unset → `<config root>/state/tool_audit/` | Where the record of every tool call is kept. |
| `mcp.enabled` | `false` | Start the helper programs listed in `servers`. |
| `mcp.expose_self` | `false` | Let `ember mcp serve` offer Ember's store + diagnostics to other programs. |
| `mcp.startup_timeout_s` | `10.0` | How long a helper may take to start. |
| `mcp.call_timeout_s` | `30.0` | How long one helper call may take. |
| `mcp.servers[].name` | — | Helper's short name; its tools appear as `mcp__<name>__<tool>`. |
| `mcp.servers[].command` | — | The program to run. |
| `mcp.servers[].args` | `[]` | Words passed to that program. |
| `mcp.servers[].env` | `{}` | Extra environment variables for that helper only. |
| `mcp.servers[].cwd` | unset | Folder the helper starts in. |
| `mcp.servers[].auto_approve` | `[]` | This helper's tools that need no per-call asking. |
| `logging.level` | `INFO` | How much diary Ember writes: DEBUG / INFO / WARNING / ERROR. |
| `logging.format` | `structured` | Diary shape: `structured` (labelled parts) or `plain`. |
| `logging.destinations[].kind` | — (code default: none) | Where the diary goes: `file` / `stderr` / `stdout`. The template shows a file + screen setup; with no config file Ember keeps no diary file by default. |
| `logging.destinations[].path` | unset | The diary file (for `kind: file`). |
| `logging.destinations[].rotate_at_mb` | unset | Diary file size at which a fresh one starts. |
| `logging.destinations[].keep` | unset | How many old diary files are kept. |

Environment (the whole list): `OLLAMA_HOST`,
`EMBER_WELL_PASSWORD` — see `.env.example`.

## Tests

`tests/unit/test_config_for_humans_e033.py` — **6 passed**:
every `EmberConfig` field documented in the template (tree walk,
not a hand list, so a future field fails the gate until it is
documented); the template loads through the real loader and
states the defaults (logging's worked example the one deliberate
difference); `.env.example` names exactly the two live variables
with the fossil's directions gone; a no-file load equals the
defaults with the safe-off set pinned; an unknown/fossil key is
refused by name; both excerpt files carry their not-a-config-file
statement. No production code changed; no README touched
(`config/README.md`'s overlay account was already accurate and
stands).
