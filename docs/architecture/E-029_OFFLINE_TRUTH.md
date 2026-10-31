# E-029 — Offline truth: the local life works, the rest is named

Roadmap slice E-029 (Part II): *"Offline truth: with the network
cut, the core's full local life works — proven, with the degraded
set listed honestly."*

## 1. What "the network cut" means here

Ember is *tethered* (E-020): its reasoner and embedder live on the
same machine by default (Ollama on loopback), its Well is a local
file by default, its person lives in one local config root. So
"offline" for this companion means precisely:

> **No traffic leaves the machine. Loopback still works.**

That is the cut these tests make — and it is made mechanically,
not by unplugging anything and hoping: a guard patches socket
resolution and connection so that any non-loopback DNS lookup or
connect raises immediately and is *recorded*. A test that passed
while secretly reaching out cannot hide: the recorded-attempts
list is asserted empty after every local-life proof, and a sanity
test proves the guard itself bites (an external connect and an
external DNS lookup both fail under it).

## 2. The full local life — proven under the cut

All of it against the **real** adapters — no fake Funi, no fake
embedder (`tests/unit/test_offline_truth_e029.py`):

| Local life | Evidence |
|---|---|
| A complete chat turn: session opens, the real Ollama adapter probes + streams from a loopback server, the real embed client embeds over loopback, retrieval runs, the reply renders, the Episode is persisted | `test_chat_turn_end_to_end_over_loopback_offline` — reply `local answer` persisted; **zero** external attempts recorded |
| Identity / persona / config | The same turn loads identity from the local config root (Hjarta file) before opening anything; E-020/E-025 pinned the filesystem shapes |
| Local file tool | `test_read_local_file_works_offline` — `read_local_file` returns the file's contents; zero attempts |
| Well search tool | `search_well` reads the same local Well handle the chat turn uses (E-026 inventory: `private_read`); no network surface of its own |
| The local Well itself | `test_sqlite_well_round_trip_offline` — an Episode written, the handle closed, reopened, and read back, entirely on disk (extras shape; skips honestly in the stdlib-only env, as E-021's reader proofs do) |
| Ingest of local files | Smiðja's local-files source reads the filesystem; its only network-shaped step is embedding, which degrades per §3 (journal marks the failure, the job continues) |
| Seiðr / astrology / dictionary members | Pure local computation by construction (E-006: seidr composes in the bare default env); their service binding is Part VII's road, not a network need |

## 3. The degraded set — what the cut actually takes, named

Each item was exercised under the guard; each fails as **typed,
plainly-worded data**, never as a crash and never as fabricated
output:

| Capability | Offline truth | Evidence |
|---|---|---|
| `fetch_url` tool (the core's one deliberately-network tool) | Returns a `ToolReply` error: `fetch_url: refused: DNS lookup failed for 'example.com': …`. Nothing is fetched, nothing is invented. | `test_fetch_url_external_is_an_honest_error_offline` |
| Embedding via a *remote* embed endpoint | The embed client returns `None` vectors (its documented failure shape); retrieval degrades to text search — the Vow of Graceful Offline in action. A *loopback* embedder is unaffected (§2). | `test_embed_client_external_endpoint_degrades_to_none` |
| A Funi backend configured at a *remote* address | `open()` returns typed `Unavailable (endpoint_unreachable)`; chat refuses with the reason named instead of starting half-alive. The default loopback Ollama is unaffected (§2). | `test_external_funi_backend_opens_unavailable_offline` |
| The pgvector Well backend | A remote database by definition: under the cut Strengr returns `Disconnected` and the session continues **ungrounded** with the banner shown (E-019/E-020's shape) — conversation works, memory does not pretend to. The default sqlite_vec Well is a local file and is unaffected. | Shape pinned by E-020's tethering tests; classified here, not re-proven |
| MCP bridges to remote servers | Off by default (E-020); a configured remote MCP server is unreachable offline, and its tools are simply absent — Ember's own local MCP *server* (explicit `ember mcp serve`) is a local surface. | E-026 inventory; classified here |
| Model downloads / updates / anything fetched | Not part of a running session at all: pulling a model or an update needs the network *at that moment*, by definition. Nothing in the core fetches silently (the telemetry refusal is E-184's proof to make). | Stated, not measured |

## 4. What was NOT changed

No production code was changed by this slice: the offline shapes
above already existed (typed `Unavailable`, `Disconnected`,
`None`-vector degradation, `ToolReply` errors). E-029's work is
the *proof* — the guard, the real-adapter turn, and this list —
plus one correction to the operator playbook (below).

One defect found and fixed in the slice's own test code, stated
for the record: the first guard draft patched
`socket.socket.connect` with a bound method, which dropped the
socket argument and failed the chat-turn test with a `TypeError`
inside `socket.create_connection`. Fixed by patching with a plain
function; the guard then passed its own sanity test and the turn
test. No product code was involved.

## 5. Playbook correction (in scope)

Recipe 7 ("Run Ember offline") claimed `ember doctor` "shows both
realms ok" as the verification — doctor in the *default*
(stdlib-only) env crashes on the missing `sqlite_vec` extra
(docket 13, E-006), so that sentence promised a check a bare
install cannot run. The recipe now verifies with the chat turn
itself and names the extras condition for doctor.

## 6. Tests and gate

New: `tests/unit/test_offline_truth_e029.py` — **6 passed,
1 skipped** in the default env (the skip is the sqlite_vec Well
round-trip, extras-gated as in E-021); **7 passed** with extras
supplied (Run D shape).

Slice gate (E-017 method): Run B (default env, pgvector file
excluded) **761 passed, 6 failed, 14 skipped, 1 warning** — the
755 E-028 baseline + 6 new passes + 1 new honest skip; the 6
failures are the proven environment failures of the E-017 freeze.
Run D (whole suite, extras supplied) **803 passed, 0 failed,
19 skipped, 1 warning**, exit 0.

## 7. Honest limits

- The cut is *simulated in-process* (socket guard), not a physical
  unplug or a network namespace: a code path that reached the
  network without Python sockets (a subprocess, a vendored binary)
  would not be seen by the guard. The core spawns no such path in
  a chat session — MCP servers are operator-configured
  subprocesses, off by default, and are the named exception.
- No live Ollama daemon was used: the loopback server speaks
  Ollama's wire shape (`/api/version`, `/api/chat` NDJSON,
  `/api/embed`) and the **real** adapter code ran against it, but
  a real model's behaviour on real hardware is Part III's proof
  road (E-047–E-049), not claimed here.
- ThoughtForge (E-024, candidate) is a local in-process layer; it
  adds no network surface, and it is still not wired into chat.
