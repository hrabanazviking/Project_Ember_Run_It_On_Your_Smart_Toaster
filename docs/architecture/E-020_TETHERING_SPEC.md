# E-020 — Tethering Made Explicit: the Specification

*Part II, slice E-020. Method: every clause below is drawn from
the code in `src/ember/` at the slice's starting HEAD, with the
file and symbol named. The clauses are pinned by automated tests
in `tests/unit/test_tethering_e020.py` (13 tests, all passing in
the default environment); the plain-language statement for
operators stands in `docs/OPERATOR_PLAYBOOK.md` ("What Ember is
tied to — and what it is not"). Where the code falls short of
what "tethered" promises, the shortfall is stated here, not
smoothed over.*

## 1. Plain-language summary

"Tethered" is Ember's defining word — the roadmap calls Ember
*a small, tethered, runs-anywhere AI companion*, and the Vision's
second Vow is Tethered Grounding. Until this slice the word did
three jobs at once without ever being unpacked. Unpacked, Ember
is tethered in exactly three ways:

1. **To its person** — everything that makes this Ember *yours*
   lives in one place on your machine: a single config root
   holding Ember's name and role for you, your settings, and your
   secrets. Ember has no account, no cloud profile, and no idea
   who you are beyond what that folder says.
2. **To its machine** — by default Ember thinks with a model
   running on the same machine (Ollama on localhost) and reads
   with an embedder on the same machine. Nothing in the shipped
   defaults reaches off the box. The tether can be *lengthened*
   by configuration — a model or a Well on another machine in
   your house — but it is never lengthened silently.
3. **To its memory** — Ember's knowledge and conversation record
   live outside the chatting process, in the Well, and the only
   road there is Strengr: a connection layer that retries what
   can recover, refuses fast what cannot, reports its own health
   honestly, and — when the Well is unreachable — says so and
   carries on ungrounded rather than pretending.

One asymmetry is load-bearing and is specified, not accidental:
the **machine tether is hard** (no model → Ember does not start)
while the **memory tether is soft** (no Well → Ember starts,
banners the fact, and answers ungrounded). And one honest limit
stands at the centre of the memory tether today: conversation
Episodes are *written* to the Well but never *read back*
(docket 81/82), so the memory tether currently grounds Ember in
its ingested documents across restarts, but not in its own past
conversations. E-021/E-031 own closing that gap; this slice
specifies the tether as it is.

## 2. Tether to its person

**T-P1 — One config root.** All per-person state lives under a
single root: the CLI default `~/.ember/`
(`cli/main.py`: `--config-root`, expanded at use), overridable
per invocation with `--config-root`. The root holds:

| Path under root | What it is | Written by |
|---|---|---|
| `identity/identity.json` | Ember's name + role for this person | Hjarta, atomically, at the end of setup |
| `config/ember.yaml` / `ember.toml` | the operator's config file (YAML wins if both) | Hjarta + the operator's editor |
| `secrets/well.password` | a remote Well's password (mode-600 file; one of three secret sources, §4) | the operator |
| `well/store.db` | the default local Well (path is config, see T-W1) | Brunnr sqlite_vec adapter |
| `state/tool_audit/` | the tool-use audit log | the tool framework |
| `state/smidja_progress/` | ingest journals | Smiðja |

**T-P2 — Identity is name and role, only.** `identity.json`
carries exactly two fields (`spark/hjarta/identity.py`;
`schemas/config.py: IdentityConfig`, defaults name "Ember",
role "your small local AI companion"). Hjarta writes it
atomically (temp file + `os.replace`) as the *last* step of
setup, so an interrupted setup leaves no half-made person-tether
behind. A missing file is not an error: the loader falls back to
the schema defaults (E-019 §4 step 1).

**T-P3 — Ember does not identify its person.** There is no user
account, no login, no person record anywhere in the core. The
tether runs the other way: the *companion* is bound to the
person's folder and choices, not the person to the companion.
Whoever holds the config root holds the tether — custody of the
folder is custody of the companion (the Kista custody law,
E-093, governs the credentials inside it).

**T-P4 — Roots do not bleed.** Each config root is complete and
separate: two roots hold two identities, two configs, two Wells,
with no shared state (pinned by test). This is also the seam
E-025's per-persona memory separation and E-035's
multi-conversation isolation will build on.

**T-P5 — The environment surface is two keys.** Beyond files,
the core reads exactly `OLLAMA_HOST` (redirects the model +
embedder endpoints, `config/overlay.py`) and
`EMBER_WELL_PASSWORD` (first secret source, §4) from the
environment — the E-013 census's finding, restated here as
specification.

## 3. Tether to its machine

**T-M1 — The model is local by default.** `FuniConfig` defaults:
runtime `ollama`, `base_url http://localhost:11434`, model
`phi3:mini` (`schemas/config.py`). The embedder defaults to the
same host (`SmidjaConfig.embedding`: `http://localhost:11434/
api/embed`, model `nomic-embed-text`). A default Ember makes no
network call off its own machine.

**T-M2 — Only one runtime exists today, and absence is typed.**
`funi/handle.open()` implements Ollama only; `llamacpp`,
`lmstudio`, `phi_silica`, and `apple_foundation` each return a
typed `Unavailable(RUNTIME_NOT_INSTALLED)` — never an exception,
never a silent fallback to a different (e.g. cloud) runtime.
E-022 owns widening this contract.

**T-M3 — The machine tether is hard at startup.** In
`munnr/chat.py` (E-019 §4) Funi opens *first*: an `Unavailable`
result prints its reason and the session exits 1 before the Well
is opened. A companion that cannot think does not pretend to be
one. (Contrast T-W3: the Well opens second and its failure is
tolerated.)

**T-M4 — Flexible roots: no frozen paths.** Schema paths keep
`~` unexpanded (`schemas/config.py` header: the consumer expands
when the path is used — sqlite adapter, journal, secret
resolver, identity, config loader all call `expanduser()` at
the point of use). A clone or a config root in any location, on
any supported platform, works identically (Vision: Vow of
Flexible Roots).

**T-M5 — The tether lengthens only by the person's word.**
Config (or `OLLAMA_HOST`) may point Funi at another machine's
Ollama (Playbook Recipe 1) — that is the person choosing a
longer machine tether, in plain sight, in their own config
file. Nothing in the core discovers, negotiates, or migrates
the model on its own.

**T-M6 — Sovereignty defaults.** Tools default off
(`ToolsConfig.enabled = False`), MCP client and server default
off (`MCPConfig`). The machine tether carries conversation and
the Well — reaching beyond the machine's own surfaces is always
opt-in (E-026/E-027 own the approval shapes).

## 4. Tether to its memory

**T-W1 — Memory lives outside the process, in the Well.**
`BrunnrConfig` defaults: backend `sqlite_vec` at
`~/.ember/well/store.db`, `embedding_dim 768`. Two backends are
implemented behind the one `BrunnrHandle` protocol —
`sqlite_vec` (local file) and `pgvector` (possibly another
machine: the household's shared Well). Switching is a config
edit; no code changes, ordering commensurate (Vision §11).

**T-W2 — Strengr is the only road.** Callers never open a
Brunnr directly in session code: `thread/strengr.open(
StrengrConfig, BrunnrConfig)` wraps the registry call with the
tether's policy — defaults 3 attempts, backoff 1s doubling
capped at 30s (`StrengrConfig`: `retry_attempts 3`,
`retry_backoff_max_s 30.0`, `health_check_timeout_s 5.0`).

**T-W3 — A cut tether is a value, not a crash, and never a
lie.** Non-recoverable reasons (`CONFIG_INVALID`, `AUTH_FAILED`,
`DNS_FAILURE`) fast-fail on the first attempt; recoverable ones
retry to the configured count; exhaustion returns a typed
`Disconnected`. Startup tolerates it: banner rendered, prompt
carries the do-not-invent instruction, retrieval is skipped,
turns continue ungrounded (E-019 §8). `strengr.health()` never
raises — a failed probe returns `last_ok=None` with a detail, so
`ember doctor` can show the cut honestly.

**T-W4 — A remote Well's secret is a reference, never a
value.** `PgVectorConfig` carries `secret_env` (default
`EMBER_WELL_PASSWORD`), `keyring_service` ("ember-well"), and
`secret_ref` (default `~/.ember/secrets/well.password`) — the
resolver (`well/brunnr/pgvector/secrets.py`) tries env →
keyring → mode-600 file (a wider mode is refused with a typed
reason) and never logs the value. This is E-093's custody
model, already shipped for this one secret.

**T-W5 — What crosses the tether today.** *Reads:* document
chunks — per turn, hybrid (vector+text) search when the query
vector matches `embedding_dim`, else text search, k=5, feeding
the prompt's grounding excerpts and the reply's citations
(E-019 §5.1). *Writes:* ingested documents/chunks (Smiðja) and
one Episode per completed turn (`add_episode`).

**T-W6 — The honest gap: Episodes are write-only.** No episode
reader exists on `BrunnrHandle` or in any caller, and the
pending-episodes journal promised in `schemas/episode.py` for
disconnected sessions was never built — so the memory tether
today is *grounding across restarts* (documents) but *not
continuity across restarts* (conversations). A new session
starts with an empty history window even though its Episodes
are stored in the Well. This is docket 81 + 82, owned by
E-021/E-031; the specification records the tether's present
shape so no later slice has to rediscover it.

## 5. The binding moment: Hjarta

The three tethers are tied in one ceremony. `spark/hjarta/
machine.py` runs a fixed state machine — Greet → ChooseFuni →
DiscoverFuni (machine tether proven by opening Funi) →
ChooseWell → ConfigureWell (memory tether proven by opening
the Well through Strengr) → TestRetrieval (a probe document is
written and searched back: the tether must *carry*, not just
connect) → NameEmber (person tether named) → AdvancedTools
(sovereignty opt-in, default no) → WriteIdentity (identity +
operator config written atomically) → Done. Any earlier failure
aborts with nothing written: an untied tether leaves no trace.

## 6. What tethering is not

- **Not a cloud account.** No vendor, no sign-in, no telemetry
  is specified anywhere in the three tethers. (Proving the
  absence of phone-home behaviour at packet level is E-184's
  job, not claimed here.)
- **Not single-device lock-in.** The whole tether is one folder
  plus a Well file: moving `~/.ember/` moves the companion
  (Playbook Recipe 10, corrected in this slice — see §7).
- **Not the other members.** No Verdandi nerve, no mempalace,
  no mimir-well participates in any tether today (E-019 §1:
  zero references in `src/ember/`). Parts IV/V may add nerves
  and a memory face; they will extend this specification, not
  silently replace it.

## 7. Defect found and fixed in this slice

**OPERATOR_PLAYBOOK Recipe 10 overclaimed the memory
tether.** Its verification step promised that after moving to a
new machine "your conversation history is intact (visible by
`ember chat` then asking Ember to recall something from
before)" — false under T-W6: Episodes move with the Well but
chat never reads them back, so past conversations cannot be
recalled in chat today. Fixed in this slice: the recipe now
states what provably carries over (identity, config, secrets,
and the Well's ingested documents, which Ember *can* search and
cite) and names the episode limit plainly. No code defect was
found in the tether paths themselves; the two structural gaps
are the already-docketed 81/82, restated as T-W6.

## 8. What this specification gives the rest of Part II

- E-021 (conversation hardening) builds the episode reader and
  the token budget *inside* T-W5/T-W6's stated shape.
- E-022 (backend contract) widens T-M2 from one runtime to the
  contract's full truth table.
- E-025 (persona core) layers personae onto T-P4's root
  separation; E-031 (session persistence) closes T-W6.
- E-029 (offline truth) proves T-M1/T-W3's degraded set end to
  end; E-033 (config for humans) documents T-P1/T-P5's surface
  in plain words; E-037 (API freeze) freezes the handles this
  spec names.
