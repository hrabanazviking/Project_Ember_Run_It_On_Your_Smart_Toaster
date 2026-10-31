# E-024 — ThoughtForge binding (candidate): MindSpark ThoughtForge as the core's cognition layer

*Slice E-024 of the Project Ember roadmap (Part II). The roadmap's
own word for this slice is **candidate**, and the binding honours
it: what is built here is Ember's side of the contract — the
contract types, the profile gate, the adapter, and the refusal
shapes — proven with tests. ThoughtForge's TF-159 consumes the
same contract from its side.*

## The plain truth first

Ember can now *be given* a second mind to think with: MindSpark
ThoughtForge, the cognition engine from Volmarr's other forge,
sitting above the model backend. Where Funi answers one prompt
with one completion, ThoughtForge runs a whole turn pipeline —
routing, retrieval against its knowledge store, prompt scaffolding,
candidate drafts, salvage, enforcement — and returns a finished,
checked answer. The layer is **off by default**, it is **refused
outright on the toaster profile** (the smallest machine has no
room for a second turn pipeline beside the first), and it is
**not wired into the chat turn**: `ember chat` still thinks with
Funi. This slice binds the candidate and proves the binding; the
day an operator's Ember actually thinks through ThoughtForge in
chat is a later, deliberate act, chosen with the budgets of
Part III in hand — not a silent swap of the companion's mind.

## The contract Ember binds to (ThoughtForge's own freeze)

ThoughtForge froze its cognition API at its TF-034, v1.0.0, in
writing, precisely so consumers could bind to it:

- `ThoughtForgeCore(config, model_path, memory_dir, db_path,
  backend)` — one core = one conversation (its will ledger,
  persona expectation and turn lock are per-instance; TF-032/035).
- `think(user_text, retrieval_path, num_drafts, history,
  interrupt)` → `FinalResponseRecord` (`text`, `turn_id`,
  `mode`, `enforcement_passed`, `citations`, `token_count`, …);
  documented to never raise on content failure; `num_drafts` is a
  *cap* — the local engine drafts ≤2 by construction, the unified
  backend exactly 1, a value below 1 raises (TF-034 §5).
- The package publishes `API_VERSION`, `api_manifest()`, and
  `verify_api_surface()` — a drift check comparing the live
  surface against the frozen tables — and its versioning law says
  a consumer on an incompatible major must get a **truthful
  refusal, never silent corruption** (TF-162 owns the service-side
  enforcement; this binding is the Ember-side half).

## What this slice builds

### 1. Cognition types (`ember.schemas.cognition`)

`CognitionReply` (the provider's record mapped straight:
text / turn_id / mode / enforcement_passed / citations /
token_count — no prompt/completion split is invented, because
ThoughtForge's record carries none), `CognitionHealth`, and
`CognitionUnavailable` with its reason enum (`DISABLED`,
`PROFILE_CANNOT_AFFORD`, `RUNTIME_NOT_INSTALLED`,
`VERSION_MISMATCH`, `CONFIG_INVALID`, `UNKNOWN`) — returned,
never raised, in the Funi shape one layer up.

### 2. The profile gate (`CognitionConfig`, `ember.schemas.config`)

Off by default (`enabled: false`). Affordance is a stated table,
not a vibe: **toaster cannot afford the layer** (refused);
phone and pi afford it with a draft cap of **1**; laptop with
**2** — caps that respect TF-034's by-construction maxima. An
explicit `num_drafts` overrides the profile's cap; a resolved cap
below 1 is refused as `CONFIG_INVALID` before any core is built.
`expected_api_major` defaults to 1, the frozen major this binding
was written against.

### 3. The handle + registry (`ember.spark.cognition`)

`CognitionHandle` protocol (`think(user_text, episodes)`,
`health()`, `close()`), `open_cognition(config)` dispatch with a
deliberate refusal order — disabled → profile cannot afford →
unknown provider → the provider binding's own open — and a
`cognition_registry()` publishing the one implemented provider
with its API major and afforded profiles, so the truth can be
read without opening anything.

### 4. The adapter (`ember.spark.cognition.thoughtforge`)

- **Lazy, optional, zero new dependencies.** The
  `thoughtforge.cognition` package is imported inside `open()`
  only. Ember's core keeps its zero-dependency law: a build
  without ThoughtForge imports and runs normally, and gets a
  typed `RUNTIME_NOT_INSTALLED` refusal if the layer is switched
  on. (In this slice's test environment ThoughtForge is genuinely
  absent, and that refusal is what the default-env tests prove.)
- **Version + drift refusal.** `open()` reads the live
  `API_VERSION`: a different major (or no version) →
  `VERSION_MISMATCH`. When the package offers
  `verify_api_surface()`, open runs it; any reported drift is a
  `VERSION_MISMATCH` refusal naming the drift count and the first
  problem — the surface must prove itself against its own freeze
  before Ember thinks through it.
- **Custody.** The core is constructed with Ember's configured
  `memory_dir` / `db_path`, which default **inside the Ember
  config root** (`~/.ember/thoughtforge/…`) — the E-020 tether
  holds: custody of the Ember folder is custody of everything
  the companion keeps, ThoughtForge's state included.
  `tf_config` passes through to the core as a plain dict,
  unchanged — ThoughtForge's own config surface (TF-032) reads
  its live keys there, and Ember shadows nothing. A construction
  failure (TF-032 raises on invalid selections) becomes a typed
  `CONFIG_INVALID`. `model_path` is passed only when the operator
  set one; unset, ThoughtForge runs its documented knowledge-only
  shape. **No credential is involved in this binding at all**, so
  none is carried — TF-160's custody rule is satisfied by absence.
- **History.** Ember `Episode`s become a ThoughtForge
  `ChatHistory` built with ThoughtForge's *own* classes
  (`add_user` / `add_assistant` per episode, oldest first) and
  handed to the frozen `history` parameter, which the core
  renders via `to_prompt_context()`. No episodes → `history`
  stays None, the frozen default.
- **The turn.** `think()` maps the FinalResponseRecord straight
  onto `CognitionReply`. A core exception folds into an
  ERROR-shaped reply naming the failure as a binding/environment
  failure (ThoughtForge's `think` never raises on content, so an
  exception is never dressed as an answer). An honestly empty
  record text is returned as-is. `close()` unloads the model via
  the frozen `unload_model()` and never raises.

## What is NOT claimed

- **No live ThoughtForge turn.** Every behaviour above is proven
  over a **fake core shaped from the TF-034 freeze** (TF-161's
  pattern: consumers needn't be present to prove the shape). The
  real `thoughtforge` package is not installed in Ember's test
  environment and no real ThoughtForge turn was run in this
  slice — a live end-to-end cognition turn is **NOT PROVEN**,
  awaiting a machine/profile where ThoughtForge is installed
  (its own TF-159 + Part III's proof work are the natural homes).
- **No budgets proven.** The profile caps are contract-shaped
  (draft counts), not measured RAM/latency figures. ThoughtForge
  on phone-class hardware is TF-159's "budgets proven on
  phone_low first" burden, and Part III owns Ember's budget book;
  this slice claims neither.
- **Chat is not rewired.** `ember chat` does not consume the
  cognition layer in this slice (candidate status, above).
  Wiring it in — as an operator-chosen alternative turn path —
  belongs to a later slice with E-025's persona core and
  Part III's budgets in hand.
- **ThoughtForge's tree was not touched.** Its campaign is live
  in its own working tree (TF-036 in progress at this slice's
  start); this binding reads its freeze and nothing else.

## Tests

`tests/unit/test_thoughtforge_binding_e024.py` — **23 passed** in
the default env (registry/profile truth ×3, open_cognition
refusal order ×4, adapter open: custody/version/drift/missing
core/bad cap/construction refusal ×8, think mapping + history +
draft caps + exception folding ×5, health/close, config defaults
+ TOML coercion, and the no-import guarantee). Slice gates are
recorded in `CAMPAIGN_STATE.md`.
