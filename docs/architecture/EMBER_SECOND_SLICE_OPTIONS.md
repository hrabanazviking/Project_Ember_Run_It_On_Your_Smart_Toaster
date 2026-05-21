# EMBER_SECOND_SLICE_OPTIONS — Menu, Not Plan

**Voice:** Cartographer (Védis Eikleið), with Architect (Rúnhild Svartdóttir) notes
**Status:** **Options menu — for Volmarr to ratify scope before a real `EMBER_SECOND_SLICE_PLAN.md` is authored.** This document does *not* commit Ember to anything; it inventories the choices and what each costs.
**Last touched:** 2026-05-21 (day the first slice ratified at 0.1.0)
**Reads with:** `EMBER_FIRST_SLICE_PLAN.md` (the model this doc parallels — once scope is picked), `docs/decisions/0007-first-slice-ratification-2026-05-21.md` §5 (the seed list), `docs/SYSTEM_VISION.md` (the standard every slice is measured against).

---

## 0. Why this document exists

The first slice is closed. The seven phases of `EMBER_FIRST_SLICE_PLAN.md` are complete and ratified at 0.1.0. The Mythic Engineering method says the next thing is *not* code — it's authorship of a slice-2 plan, the same way the first slice was planned before Phase 2 began.

This file is the **input** to that authorship. It surveys what's scattered across the codebase as informal "Phase 8" / "Phase 9+" hints, reconciles them with the ADR-shaped starting points in ADR 0007 §5, and presents the resulting choices as a coherent menu for Volmarr to pick from.

Once scope is picked, the Architect authors `EMBER_SECOND_SLICE_PLAN.md` (or `EMBER_PHASE_8_PLAN.md`, or whatever naming Volmarr ratifies) with the file-by-file plan, dependencies, acceptance criterion, and phase sequence — same shape as the first-slice plan.

**This document is not a commitment. It is a map.**

---

## 1. The five ADR-shaped starting points

ADR 0007 §5 lists five candidate ADRs for the second slice. They are *independent* — any subset can ship together in slice 2; the rest become slice 3, 4, ... Below is each one expanded enough that you can pick.

### 1.1 ADR 0008 — Operator config-file loader

**What it adds:** A real loader for `~/.ember/config/ember.{yaml,toml}` (and `storage.yaml`, `sources.yaml` per `docs/REPO_MAP.md` §config/). Reads file, validates, overlays on `EmberConfig()` defaults, returns the fully-populated config to `cli/main.py`. Honors `OLLAMA_HOST` and any other env-var overrides on top of file values.

**What it unblocks:** Operators can customise Funi runtime, model, well path, chunker defaults, embedding model, logging — *without* source edits or env-var hacks. The Phase-7 `OLLAMA_HOST` escape hatch becomes one of many supported overrides instead of the only one.

**Size:** Medium. ~3-4 modules: a loader, validation helpers, env-overlay logic, and tests for each. ~500-800 LOC.

**Risks:** Validation error UX matters here — operators editing YAML hit small typos often, and the loader must say "your `embedding_dim` must be a positive integer" rather than "ValidationError at line 42". This is where `pydantic` becomes worth its weight (per ADR 0007 §2.5 the door is open for an optional dep at this layer).

**Dependencies:** None outside what's already shipped. Optional `pydantic` for validation messages.

---

### 1.2 ADR 0009 — Streaming Funi replies

**What it adds:** Funi's `complete()` gains a `stream=True` variant (or a separate `complete_streaming()` method) that yields tokens as Ollama produces them. Munnr's `chat.run` REPL renders incrementally — operator sees the reply unfold instead of waiting for the whole thing.

**What it unblocks:** UX delta is enormous. On a Pi 5 with `phi3:mini`, a 200-token reply currently waits ~5-10 seconds in silence; streaming makes it feel instant. Also lets operators interrupt long replies with Ctrl-C without losing partial output.

**Size:** Small-to-medium. The Ollama `/api/chat` endpoint supports `"stream": true` natively (newline-delimited JSON response). Funi adapter changes ~50 LOC; Munnr render changes ~50 LOC; tests ~100 LOC.

**Risks:** Error-folding semantics get fiddlier — what happens if the stream dies mid-reply? Need a `FuniReply` variant or a streaming-result type that captures partial text + error reason. Touching the Protocol means thinking about how llamacpp/lmstudio/phi_silica adapters (future) will implement streaming.

**Dependencies:** None.

---

### 1.3 ADR 0010 — `pgvector` Brunnr (Gungnir-compatible)

**What it adds:** Second Brunnr backend. `src/ember/well/brunnr/pgvector/adapter.py` implementing the same `BrunnrHandle` protocol against Postgres + pgvector. Honors Gungnir's exact schema (per `docs/adapters/GUNGNIR_WELL_REFERENCE.md`) so existing Gungnir Wells work as-is.

**What it unblocks:** Households where one operator runs Ember on multiple devices (Pi + laptop + phone) can share one Well. The Gungnir reference (95 docs, 35 682 chunks already on Volmarr's tailnet) becomes a real Brunnr Ember can talk to, not just an inspiration. Also the *lineage anchor* from `docs/SYSTEM_VISION.md` §8 ("the knowledge well on Gungnir") becomes mechanically true rather than aspirational.

**Size:** Medium. ~3-4 modules: adapter, schema-version probe (since Gungnir's schema is already there), connection management, tests against a real Postgres or a docker-compose fixture. ~600-800 LOC.

**Risks:** Auth and secret handling — Strengr was designed with this in mind (`secret_ref` field in `PgVectorConfig`), but the actual keyring/file-secret resolution code hasn't been written. Need to decide: keyring on desktop, mode-600 file on Pi, env-var on container. Per `feedback_tailnet_access.md`: bind correctly to the tailscale interface, proper auth.

**Dependencies:** `psycopg[binary]>=3.2`, `pgvector>=0.3` — both as optional extras under `[project.optional-dependencies] pgvector`.

---

### 1.4 ADR 0011 — Tool use

**What it adds:** Funi can produce structured tool calls; Munnr executes them under an operator-approval flow; results feed back into the conversation. Per `docs/architecture/EMBER_TRUE_NAMES.md` §2.6 the Funi `complete(prompt, context, tools=None)` already has the slot reserved — this fills it in.

**What it unblocks:** "Ember as agent" rather than "Ember as chatbot". Tools mentioned in scattered docs: read-file, search-well-by-query, run-shell-command, fetch-url. The Vow of Pluggable Storage says tools should be pluggable too — first slice ships maybe 3 read-only tools; later slices add writes.

**Size:** Large. Requires: tool registry, sandbox semantics (what can each tool see?), operator approval flow (per-call or standing-trust?), audit log, error handling for failed tool calls, schema for `ToolCall` reply round-trip. The `--allow-tools` CLI flag mentioned in `EMBER_DATA_FLOW.md` §7. ~1000-1500 LOC including tests.

**Risks:** This is the most security-sensitive thing in Ember. A read-file tool that doesn't sandbox can read `~/.ssh/id_rsa`. The standing-trust policy file mentioned in `~/.ember/policy/` (per `EMBER_ARCHITECTURE.md` §5) becomes real here. Get the model wrong and Ember becomes a credential exfiltration vector.

**Dependencies:** None for the framework; per-tool deps as tools land.

---

### 1.5 ADR 0012 — First new surface (Auga / Rödd / Bifröst)

**What it adds:** A second way to talk to Ember beyond `ember chat`. Three candidates:

- **Auga (GUI)** — `src/ember/spark/auga/` — a small local window. Most operator-friendly, biggest dependency footprint (Qt? Tk? Tauri? web-frontend?). Per SYSTEM_VISION §3.1 "Pi-and-laptop deployments may host this only on the laptop".
- **Rödd (voice)** — `src/ember/spark/rödd/` — wake-word + STT + TTS + barge-in. Lovely UX, requires audio hardware + non-trivial deps (Piper TTS, Whisper or vosk STT, picovoice or porcupine for wake-word). Per SYSTEM_VISION §3.1 "only on hosts with audio".
- **Bifröst (HTTP gateway)** — `src/ember/spark/bifrost/` — small ASGI app exposing the conversation API over HTTP/WS. Enables remote-Ember scenarios; chat-bridge adapters (Discord/Matrix/Telegram) plug into this. Per SYSTEM_VISION §3.1 "where chat-bridge adapters connect to".

**What it unblocks:** Each one opens an entirely different set of operator stories. Picking which surface first is a *user-research* question, not an engineering one.

**Size:** Each is medium-to-large (1000-2000 LOC + UI/protocol design). **Pick one for slice 2.** The other two stay in the queue.

**Risks:** Surface choice has long downstream consequences — once Auga ships with Qt, retiring it for Tk is a real cost. The picky thing is *which* surface deserves to ship first; the *what* is comparatively easy.

**Dependencies:** Depends on which surface. Auga: a GUI framework (PySide6? Tk? webview?). Rödd: audio + TTS + STT libraries. Bifröst: an ASGI server (uvicorn or hypercorn).

---

## 2. Reconciling the older "Phase 8 / 9+" references

The codebase still has scattered "Phase 8 = pgvector + Phi Silica + Apple Foundation" and "Phase 9+ = config loader / KG / streaming" hints from before ADR 0007 was authored. These predate the ADR-numbered approach and conflict with each other slightly.

| Older hint | Where it lives | Reconciled with |
|---|---|---|
| Phase 8 = `pgvector` Brunnr | `BRUNNR_BACKEND_MATRIX.md`, `GUNGNIR_WELL_REFERENCE.md`, `EMBER_TRUE_NAMES.md`, ADR 0006 | ADR 0010 (one decision per ADR) |
| Phase 8 = Phi Silica + Apple Foundation Funi | `FUNI_LOCAL_MODEL_OPTIONS.md`, ADR 0006 | *Not in ADR 0007 §5* — these are Funi-adapter add-ons, would belong to ADR 0013+ once a slice scopes them |
| Phase 9+ = full config loader | `GUNGNIR_WELL_REFERENCE.md`, ADR 0007 itself | ADR 0008 (the same thing, ADR-numbered) |
| Phase 9+ = Skein/KG layers | `GUNGNIR_WELL_REFERENCE.md` | *Not in ADR 0007 §5* — Skein/Skry have their own repos; an Ember-side adapter would belong to a future "ADR 001N — Skein/Skry retrieval adapter" |
| Later slice = streaming | `DATA_FLOW.md`, `EMBER_FIRST_SLICE_PLAN.md` | ADR 0009 |
| Later slice = tool use | `EMBER_FIRST_SLICE_PLAN.md`, `EMBER_TRUE_NAMES.md`, `funi/INTERFACE.md` | ADR 0011 |
| Later slice = Nomad Smiðja source | `SMIDJA_INGEST_PATTERNS.md`, `SYSTEM_VISION.md` §8 | *Not in ADR 0007 §5* — would belong to ADR 001N |
| Phase 9 = export/import | `BRUNNR_BACKEND_MATRIX.md` | *Not in ADR 0007 §5* — operational tooling, probably an ADR 0014 if/when a backend-migration scenario forces it |

**Cleanup action when slice-2 scope is picked:** sweep the codebase to update the older "Phase 8/9+" references to match whichever ADRs land in slice 2. Mechanical search-and-replace; small commit.

---

## 3. Three suggested bundlings

These are not the only ways to scope slice 2 — they're three illustrative bundles that share a theme. Pick one (or invent a different one).

### 3.1 The "Household Well" bundle (Architect's recommended)

> **ADR 0008 (config loader) + ADR 0010 (pgvector Brunnr)**

**Why bundle them:** The config loader is *the* unblocker for pgvector — operators can't sensibly use pgvector without editing a config file (you can't put a Postgres URL on the command line every time). Shipping both together means the Gungnir story works end-to-end the day slice 2 lands.

**What an operator can do after this slice:**
- Edit `~/.ember/config/ember.yaml` to set their funi model, well path, embedding model, etc. — first-class operator customisation.
- Switch from `sqlite_vec` to `pgvector` with a config edit, point at their household Postgres (or Gungnir), share one Well across Pi + laptop + phone.
- Honor `OLLAMA_HOST` plus file-based config plus eventual env-var-overlay rules.

**Estimated size:** 8-12 phases, ~2000-3000 LOC across both ADRs.

**Why it's recommended:** It completes the lineage story (`SYSTEM_VISION.md` §8 named Gungnir as the first concrete Well; until pgvector ships, that's aspirational) and removes the biggest operator friction (no customisation without source edits or hacks).

### 3.2 The "Ember Feels Alive" bundle

> **ADR 0009 (streaming) + ADR 0008 (config loader, lighter scope)**

**Why bundle them:** Streaming is the single biggest UX delta available. Adding a small config loader (read base_url + model from a file, defer full validation to a later slice) makes the streaming work configurable without source edits.

**What an operator can do after this slice:**
- Watch Ember think instead of waiting for the whole reply.
- Customise model + endpoint via a small config file.
- Interrupt long replies cleanly with Ctrl-C.

**Estimated size:** 6-8 phases, ~1500-2000 LOC.

**Why it's nice:** Smallest scope, highest "I want to keep using this" emotional payoff, doesn't commit to the heavy decisions (pgvector, tools, surface).

### 3.3 The "Ember Gets Useful" bundle

> **ADR 0011 (tool use) standalone, with as small an MVP as possible**

**Why standalone:** Tool use is the heaviest single ADR; bundling it inflates scope past one slice. Ship a minimal tool framework first (say 3 read-only tools: `search_well`, `read_local_file`, `fetch_url`), prove the operator-approval flow works, then expand in slice 3.

**What an operator can do after this slice:**
- Ask Ember "what does my config say about X?" and Ember can actually open the file.
- Ask Ember "what does this URL say?" and Ember can fetch it.
- Ask Ember "what's in my Well about X?" and Ember can do explicit search-then-summarise rather than implicit retrieval.

**Estimated size:** 7-10 phases, ~1500-2500 LOC. Largest *risk* per LOC of any bundle (security-sensitive).

**Why it's powerful:** This is the bundle that takes Ember from "chatbot with retrieval" to "small agent with bounded tools". Most operator value per slice.

---

## 4. What `EMBER_SECOND_SLICE_PLAN.md` would look like

Once a bundle is picked, the Architect authors a real plan — same shape as `EMBER_FIRST_SLICE_PLAN.md`. The template:

```
# EMBER_SECOND_SLICE_PLAN — <bundle name>

## 0. What "second slice" means here
   Acceptance criterion: <one paragraph, operator-readable>

## 1. Dependencies the slice assumes
   (Per-ADR pin tables, like §1 of the first-slice plan.)

## 2. The slice as a file list
   (Tree of NEW vs (scaffolded) files per subpackage, like §2 of the first-slice plan.)

## 3. Slice phases (ordered, each its own commit)
   Phase 8, 9, 10, ... per the ADRs in the bundle.

## 4. What the slice deliberately does NOT include
   (Explicit non-goals from the *other* ADRs.)

## 5. Forge Worker's quality bar
   (Same standing requirements as the first-slice plan §6.)

## 6. Risks the Forge Worker flags now
   (Per-bundle risk register.)
```

Each ADR's "Decision" section gets *that* ADR's own document; the slice plan is the file-by-file *execution* spec across all ADRs in the bundle.

---

## 5. Open scope questions only Volmarr can decide

These don't have right answers; they're values calls.

1. **How much slice-2 work do you want?** A two-ADR bundle is a week-of-sessions; ADR 0011 alone is a two-week-of-sessions slice. Smaller slices ship faster; bigger ones make more cohesive deltas.

2. **Which operator story matters most to you right now?** Household-Well, Ember-Feels-Alive, or Ember-Gets-Useful are the three I sketched. The right answer depends on whether you want to start using Ember yourself (Feels-Alive), share it across your devices (Household), or push the agent capability (Useful).

3. **Is `EMBER_FIRST_SLICE_PLAN.md` archived now?** It's been completed; per its own §3 Phase 7 acceptance, it could move to `docs/archive/` once you ratify the slice closed. Or it stays as historical record alongside the new slice-2 plan.

4. **How are ADRs numbered going forward?** ADR 0007 §5 named candidate ADRs 0008-0012 to specific topics. If you pick a different bundle, the ADR numbers re-shuffle. Easy to fix; just worth knowing.

5. **Do you want `EMBER_SECOND_SLICE_OPTIONS.md` (this doc) to live forever, or to be archived once a real slice-2 plan is authored?** Either works. The "options menu" pattern might be useful for slice 3 too; treating this as a long-lived design-pattern doc rather than a one-shot planning artifact would give that pattern a home.

---

## 6. Cartographer's closing word

> *The first slice was a clear walk: one plan, seven phases, one map. The second slice has five named roads and no walked path. Don't pick by feature; pick by the operator story you most want to live in next. The Architect's plan will follow from that story, not the other way around.*

— Védis Eikleið

---

## 7. How to use this doc next session

The next session begins by Volmarr picking scope. The natural opening:

> "Go for slice 2 — bundle X" (where X is one of the three above, or any combination Volmarr names).

The Architect's response is to author `EMBER_SECOND_SLICE_PLAN.md` following the template in §4, *before* any code is touched. Per `MYTHIC_ENGINEERING.md`'s core loop: **document before code.**
