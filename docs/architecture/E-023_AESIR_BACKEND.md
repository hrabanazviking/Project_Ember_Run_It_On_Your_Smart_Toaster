# E-023 — Aesir backend for Ember: Project Aesir under the contract

*Slice E-023 of the Project Ember roadmap (Part II). What changed,
what it proves, and what remains open — all claims drawn from the
code and the test runner of this slice, and from Project Aesir's
own API support matrix v1 + native-service doc, which are the
authorities for what Aesir's service accepts.*

## The plain truth first

Ember can now run on Project Aesir — Volmarr's own engine — as its
second implemented model backend. Point `funi.runtime` at `aesir`,
start Aesir's native service with a model loaded, and Ember talks
to it over its loopback port, using the service key from the key
file you made with Aesir's own key tool. Nothing leaves the
machine, no new software needs installing (the adapter uses only
Python's standard library, like the Ollama one), and no tool calls
are possible on this backend — Aesir's native route does not take
tools, so Ember says so up front instead of pretending.

## Why the native mode, not the Ollama-compatible mode

Aesir's service offers two faces: its **native mode**
(`POST /v1/generate` on `127.0.0.1:18434`, bearer-authenticated) and
an **Ollama-compatible mode** (`/api/chat` on :11434, no auth, built
so Ollama clients can connect). This binding uses the native mode
only. Routing Ember through the Ollama face would work, but it
would hide which engine is answering and would make Aesir look like
"just Ollama" in Ember's registry — the opposite of what E-022's
contract exists to state. The native mode is Aesir's own contract,
so the binding speaks it and is judged against it.

## What the native contract actually is (from Aesir's matrix)

- `POST /v1/generate` accepts exactly `prompt`, `system`,
  `max_tokens`, `timeout_ms`, `temperature`, `top_k`, `top_p`,
  `min_p`, `repeat_penalty`, `seed`, `stream`. **No `model` field**
  (one resident model per service), **no `messages`**, **no
  `tools`**, no sessions: each admitted generation resets logical
  history, so the client sends the conversation itself every turn.
- `GET /health/ready` (schema v1) reports `ready` plus the resident
  model identity/profile/context; 200 when ready, 503 otherwise.
- `stream: true` sends incremental NDJSON text records followed by
  one counted terminal record. EOF without the terminal record is
  incomplete — never a success.
- Requests are bounded server-side (128 KiB body, 64 KiB decoded
  text fields); a request may lower but never raise the service's
  reply ceiling (default 256 tokens).
- The service is loopback-only, one resident model, one generation
  at a time with a bounded waiting queue — a tiny-hardware shape
  that matches Ember's own budgets: this adapter adds **zero
  dependencies** (stdlib `urllib`) and holds no connection open.

## What this slice builds

### 1. The runtime + config (`ember.schemas.config`)

`FuniRuntime.AESIR = "aesir"` and `FuniAesirConfig`:
`base_url` (default `http://127.0.0.1:18434`), `model` (the
*expected* resident model; empty = accept what readiness reports),
`api_key_file` (default `~/.config/aesir/service.key`),
`temperature` / `top_p`, `max_tokens` (default **256** — the
service's own default ceiling, so Ember never promises more than
the service grants), and optional `timeout_ms` (omitted when unset;
the service's limit then applies). The TOML/YAML loader coerces the
`funi.aesir` section with no loader changes (proven by test).

### 2. Key custody — reference, never value

Following the Well-secret shape E-013/E-020 named the tree's best:
config carries the key file's **path**, never the key. `open()`
reads the file, accepts exactly Aesir's key grammar (32–256 of
`[A-Za-z0-9_-]`, one optional trailing newline), and keeps the value
in memory only. Missing/unreadable file → `Unavailable
(CONFIG_INVALID)` naming the path; malformed content →
`CONFIG_INVALID` **without echoing any of what was read**; the
adapter has no `__repr__`, logs no key, and puts the key in exactly
one place on the wire: the `Authorization: Bearer …` header.

### 3. The adapter (`ember.spark.funi.aesir`)

`AesirFuni` implements the `FuniHandle` protocol:

- **open probe** — `GET /health/ready` with the bearer header.
  Unreachable → `ENDPOINT_UNREACHABLE`; 401/403 → `CONFIG_INVALID`
  (key rejected); 503 or `ready` not true → `NOT_LOADED`; a
  configured expected model that differs from the resident model →
  `NOT_LOADED` naming both (model identities are not secrets). On
  success the handle's `model_id` is the **resident model the probe
  reported**, not the config's hope.
- **complete** — context is flattened into the two fields the route
  accepts: SYSTEM + SUMMARY → `system`; EPISODE, CHUNK and
  TOOL_REPLY (as labelled `Tool result (<name>):` text — content
  preserved, no tool protocol pretended) plus the operator's line →
  `prompt`. Reply mapping: `prompt_tokens` ← `prompt_tokens`,
  `completion_tokens` ← `generated_tokens`; finish reasons `eos` /
  `stop` → STOP, `length` → LENGTH, `timeout` → LENGTH (Aesir's
  deadline may return a partial answer — a truncated reply),
  `tool_calls` → TOOL_CALL (unreachable today, mapped for honesty),
  `refused` → REFUSED, `error` → ERROR. HTTP errors (400/422/500…)
  and native error bodies fold into ERROR replies carrying the
  server's code/message (Aesir states its errors echo no request
  data and no key).
- **tools are refused, not dropped** — a turn carrying tool
  descriptors returns an ERROR reply naming the limit, and nothing
  is sent. Silently generating without the tools the caller asked
  for would be a fabricated capability.
- **complete_streaming** — NDJSON pieces pass through; the terminal
  record carries counts and the mapped finish reason; an error
  line, a mid-stream death, or EOF without a terminal record each
  end in exactly one ERROR chunk.
- **health** — readiness probed per call; never raises; reports no
  RAM (the capability declaration says so, and health agrees).

### 4. Declared capabilities (`AESIR_CAPABILITIES`)

Native streaming; `tool_calls=False` (not model-dependent — the
route rejects the field); token counts yes; RAM never reported;
endpoint required; every `ContextKind` translated (TOOL_REPLY as
prompt text, per §3). The registry in `ember.spark.funi.handle`
now publishes **two** implemented backends; `open()` dispatches
`aesir` beside `ollama`. E-022's conformance tests were updated
with attribution to pin the implemented set as exactly
`[OLLAMA, AESIR]` — a future backend extends that list in its own
slice, as E-021 did for `ContextKind`.

## The ledger, respected — what is NOT claimed

- **No accelerator claim.** The generate response carries the
  server's own `backend` field (e.g. `cuda`); this adapter passes
  no verdict on it and Ember claims none. Aesir's capability ledger
  — not this binding — is the authority on what its CPU/GPU/Hailo
  paths have proven, including its own rule that native-source
  Hailo text generation is a separate, harder claim from the
  verified HailoRT route. Ember binding a text client proves only
  the client.
- **No live-service proof in this slice.** Every Aesir behaviour
  above is tested over a **mocked transport** shaped from Aesir's
  published matrix and fixtures. No Aesir binary was run, no real
  model answered — a live end-to-end turn against a running Aesir
  service is **NOT PROVEN** here and awaits a machine where the
  service is up (the natural home is the laptop/Pi proof work in
  Part III, with the device named when it happens).
- **No model claim.** The adapter works with whatever single model
  the service holds resident; which models Aesir can load is
  Aesir's ledger's business, and a configured expectation is
  verified — never substituted silently.
- **One generation at a time** is the service's shape; Ember's
  concurrency story (E-038) must respect it rather than paper over
  it. E-038 inherits this note.

## Tests

`tests/unit/test_aesir_backend_e023.py` — **26 passed** in the
default env (registry/capabilities, config defaults + TOML loader,
key custody ×4, open outcomes ×5, complete mapping/flattening/
refusals ×7, streaming ×4, health ×2). E-022's file re-run with its
updated pins: **16 passed**. Slice gates are recorded in
`CAMPAIGN_STATE.md`.
