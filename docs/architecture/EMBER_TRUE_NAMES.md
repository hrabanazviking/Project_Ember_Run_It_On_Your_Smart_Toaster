# EMBER_TRUE_NAMES — The Six Names Ember Is Built From

**Voice:** Skald (Sigrún Ljósbrá), with Architect notes embedded
**Status:** **Ratified 2026-05-21 by Volmarr.** ("names are all approved")
**Last touched:** 2026-05-21
**Reads with:** `docs/SYSTEM_VISION.md` §4 (the canonical Skald scroll where the names were first named), `docs/architecture/ARCHITECTURE.md` (the shape they form), `docs/architecture/DOMAIN_MAP.md` (the ownership they enforce).

---

## 0. Why True Names matter

The names are **load-bearing**, not decorative. Each is chosen so the *name itself constrains the boundary* — a subsystem named **Funi** cannot drift into doing what **Brunnr** is for, because they have different essential natures. Generic names like "model", "tether", "storage" don't enforce this; they get overloaded over time. Old Norse keeps the discipline.

This is the discipline `MYTHIC_ENGINEERING.md` calls "naming as boundary". A code review of an Ember PR is now armed with one question that has a clear answer: *"Is what this code does still what its True Name implies?"* If yes, ship. If no, the boundary failed before the code did — and the code is the symptom, not the disease.

---

## 1. The Three Realms grouping

The six names live in three realms, mechanically separated. **Higher realms may import from lower; never the reverse.**

```
SPARK realm   (local, must run offline)            →  Funi · Hjarta · Munnr
THREAD realm  (the tether)                         →  Strengr
WELL realm    (memory + knowledge, may be remote)  →  Brunnr · Smiðja
```

See `ARCHITECTURE.md` §1 for the full diagram and §2 for the dependency law.

---

## 2. The six names

### 2.1 Funi — *"flame, fire"* (Old Norse)

**Realm:** Spark. **Code:** `src/ember/spark/funi/`.

**What it is:** The local LLM runtime. The spark itself — the small model that thinks on the device.

**What it's for:** Being Ember's *reasoner and navigator*, not her *knowledge*. Funi is given a prompt + assembled context (recent episodes + retrieval hits + operator's line) and produces one of three honest outputs: a reply, a structured tool call (when explicitly permitted), or a clean "I do not know" stop. **Funi is not allowed to invent.** When grounding isn't available, the prompt assembler tells Funi so, and Funi answers without pretending otherwise.

**Owns:** One adapter per runtime — `ollama/` is the first-slice default; `llamacpp/`, `lmstudio/`, `phi_silica/` (for Windows Copilot+ PCs), `apple_foundation/` (for Apple silicon) ship in Phase 8. The prompt assembler. The tool-call slot.

**Does NOT own:** Retrieval (Munnr assembles context before calling). Identity (lives in `~/.ember/identity/`). Conversation persistence (lives in the Well via episode writes).

**Why fire as the name:** Because it's the small flame that lights the device. The spark from Eldra Járnsdóttir's forge that the SYSTEM_VISION calls out — *carried on the wind, finding a hearth in a stranger's hand and rekindling there*. That's literally what Funi is supposed to do: run on weak hardware, give an honest small intelligence to ordinary people who don't have data centres.

---

### 2.2 Strengr — *"string, cord, tether"* (Old Norse)

**Realm:** Thread (its own realm — Strengr is the *only* True Name there). **Code:** `src/ember/thread/strengr/`.

**What it is:** The tether. The invisible thread between body (Spark) and brain (Well).

**What it's for:** Making the Well usable from Spark *without leaking the network surface into Spark code*. Every Well call from Spark goes through Strengr. Strengr is the single point where "the network failed" becomes **legible** instead of **catastrophic**.

The contract is precise: Strengr **never raises** a connection error upward. Instead it returns a typed `Disconnected(reason, since)` value. Spark code is *required* to handle that value — the type system makes you. This is what the Vow of Graceful Offline looks like in mechanical form. When the Well goes away mid-conversation, Ember tells the operator plainly (`well: disconnected (conn_refused, since 03:42)`) and continues to be useful with what she has.

**Owns:** Connection lifecycle, health checks, auth (keyring on desktop, mode-600 file on Pi), retry-with-backoff, transport selection (in-process / Unix socket / HTTP / Tailscale).

**Does NOT own:** Backend-specific protocols (those live inside the Brunnr adapter). Conversation memory (Well content). Retrieval decisions (Spark's job).

**Why string as the name:** Because that's exactly what it is — a slender, fallible-but-honest cord between two places. Strings break. A good string lets you *feel* when it's broken instead of dropping the load on the floor.

---

### 2.3 Brunnr — *"well, spring"* (Old Norse)

**Realm:** Well. **Code:** `src/ember/well/brunnr/`.

**What it is:** The pluggable storage adapter layer. The Well itself.

**What it's for:** Holding Ember's persistent state — documents, chunks, embeddings, episodes — in a way that doesn't bind Ember to a single backend. **The Vow of Pluggable Storage forbids single-backend binding.** Every backend honors the same minimum surface (the `BrunnrHandle` protocol in `DOMAIN_MAP.md` §2.1): vector search, text search, hybrid (reciprocal rank fusion), `add_document/chunks/episode`, `count`.

The default is `sqlite_vec` — a single file under `~/.ember/well/store.db`, zero auxiliary processes, runs on a Pi. The Gungnir-shape `pgvector` adapter ships in Phase 8 for households where multiple devices want to share one Well (see `docs/adapters/GUNGNIR_WELL_REFERENCE.md`). Then `qdrant`, `chroma`, `lancedb` as later peers — every backend is a *first-class peer*, not a fallback.

**Owns:** Concrete adapters per backend, the backend registry, on-disk schema versioning per backend. Idempotency on content hash. Embedding-dim enforcement.

**Does NOT own:** Embedding generation (Smiðja's job). Network transport selection (Strengr's job). What questions to ask (Spark's job).

**Why well as the name:** Because in the SYSTEM_VISION's metaphor, *Ember's knowledge lives outside Ember*. You walk to the well to drink. The well is *separate from* the village. That separation is the architecture — it's what lets the same Ember run on a Pi, a phone, or a laptop while the Well stays where the operator put it. A Pi dies, a phone is reset, a laptop is replaced; the Well carries the operator's memory across hardware.

---

### 2.4 Smiðja — *"forge"* (Old Norse)

**Realm:** Well. **Code:** `src/ember/well/smidja/`.

**What it is:** The ingest forge. Takes content sources, chunks them, embeds them, deposits chunks into Brunnr.

**What it's for:** Being *the* writer of the Well. **Nothing else writes embeddings.** Brunnr only stores what Smiðja gives it; this single-writer discipline keeps the Well's integrity legible.

A Smiðja run is: walk source → parse to text → chunk (Gungnir-aligned: ~1684 char average, 2000 char max, paragraph-boundary preferred) → batch-embed via Ollama (`nomic-embed-text`, 768-dim by default — matches Gungnir bytewise) → write `Document` + `Chunks` via Brunnr. All of it journalled to `~/.ember/state/smidja_progress/<job_id>.json`. **The journal is what makes ingest bearable on a toaster** — a Pi-class operator can leave `ember well ingest ~/library/` running overnight, get killed by a power blip, run the same command the next morning, and resume from where it died. Without resumability the Vow of Smallness is broken: you cannot ingest a real library on a Pi without it.

**Owns:** Source adapters (`local_files/` first; `url_fetch/`, `shared_well/`, `nomad/` later), the chunker, the embedding HTTP client, the progress journal. See `docs/adapters/SMIDJA_INGEST_PATTERNS.md` for the canonical patterns.

**Does NOT own:** The Brunnr backend (writes through the public interface). The embedding model itself (external service). Reading from the Well (that's Brunnr).

**Why forge as the name:** Because chunking + embedding *transforms* raw content into a form that can live in the Well. You don't just dump bytes; you hammer them into chunks of the right size with the right edge-orientation. That's smithing. The Forge Worker persona (Eldra Járnsdóttir) is literally the one who built the metaphor.

---

### 2.5 Hjarta — *"heart"* (Old Norse)

**Realm:** Spark. **Code:** `src/ember/spark/hjarta/`.

**What it is:** The first-run setup ritual. The conversation that wires Funi to Strengr to Brunnr the first time someone meets Ember.

**What it's for:** Turning *"I just installed this"* into *"I have a working Ember"* — for an ordinary person, without reading a manual. The first impression. The Vow of Public-Friendliness in action.

Hjarta is a **finite, named state machine** — not a generative wizard. Its states are enumerated, its transitions are unit-testable, its prompts live as YAML data files in `config/hjarta_prompts/`. The path:

```
Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell
      → TestRetrieval → NameEmber → WriteIdentity → Done
```

`DiscoverFuni` probes the chosen runtime, lists available models, and recommends one by host RAM (a Pi5-8GB sees `phi3:mini` proposed; a Pi5-4GB sees `qwen2.5:1.5b`; see `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` for the full ladder). `TestRetrieval` writes a probe chunk, retrieves it, deletes it — proving the Spark↔Thread↔Well wiring before the operator commits. `WriteIdentity` is **atomic at the end** — if anything before it fails, the filesystem is unchanged. There is no half-configured state.

**Owns:** The FSM, the state prompts (as data, not in code per RULES.AI.md), the atomic identity write.

**Does NOT own:** Ongoing conversation (Munnr). Reconfiguration after first run (separate command: `ember setup --reset`).

**Why heart as the name:** Because it's the moment the system *becomes Ember to this person*. The other names are *what she's made of*; Hjarta is *how she meets you*. The heart isn't the brain or the lungs; it's the rhythm that says "alive". First-run is when Ember starts beating in the operator's hand.

---

### 2.6 Munnr — *"mouth"* (Old Norse)

**Realm:** Spark. **Code:** `src/ember/spark/munnr/`.

**What it is:** The command-line surface. Where Ember is summoned.

**What it's for:** Being the operator's *only* way to talk to Ember in the first slice. Commands:

- `ember chat` — interactive REPL (the conversation turn).
- `ember ask "…"` — one-shot ask.
- `ember well ingest <path>` — Smiðja into the configured Brunnr.
- `ember well status` — counts + health.
- `ember doctor` — diagnostics across all realms.
- `ember setup --reset` — re-run Hjarta.

Munnr is **only a router**. Behaviour lives in the layers below. Munnr's job is parsing arguments, dispatching subcommands, and **rendering output**. It's the rendering that matters most: the `well: disconnected` banner is *always* shown on ungrounded replies (Vow of Graceful Offline made visible), citations to retrieved chunks always appear under replies, errors always produce one-line human-readable causes.

**Owns:** Argument parsing, subcommand dispatch, REPL loop, terminal output formatting.

**Does NOT own:** Any actual work. Ember's first iron law: *Munnr is a router, not a doer.*

**Why mouth as the name:** Because it's where Ember *speaks* — and where she's *spoken to*. In the SYSTEM_VISION's words, *the command-line surface — where Ember is summoned*. The mouth doesn't think (Funi does). The mouth doesn't remember (Brunnr does). The mouth is the interface between the inner being and the outer world.

---

## 3. How they connect in one conversation turn

The canonical happy-path conversation turn (see `DATA_FLOW.md` §2 for the full version including sad paths):

```
Operator types at `ember chat`
        ▼
   [Munnr] parses the line
        ▼
   [Strengr] opens the tether → BrunnrHandle (or Disconnected)
        ▼                                          ↓
   [Funi]   embeds the question                    ↓
        ▼                                          ↓
   [Brunnr] hybrid-searches the Well        (sad path:
        ▼                                    skip retrieval,
   [Munnr]  assembles prompt: identity       set "ungrounded"
            + recent episodes + hits          flag in prompt)
            + operator line
        ▼
   [Funi]   produces FuniReply
        ▼
   [Munnr]  renders reply with citations
            (or "well: disconnected" banner if sad path)
        ▼
   [Brunnr] persists Episode (or local pending journal if Disconnected)
```

**Smiðja** is the writer-side cousin of this flow — it runs during `ember well ingest`, not during conversation. **Hjarta** runs once, the first time, then never again unless explicitly re-summoned with `--reset`.

---

## 4. The discipline these names enforce

The point of choosing **Funi** over `local_model_runtime` is that Funi *is just fire*. It cannot do anything but burn — it cannot pretend to be storage, or the tether, or the wizard, or the mouth. The name itself refuses the drift.

This is why they're called True Names: they constrain *what each subsystem can be allowed to do*. A code review of an Ember PR is now armed with a question that has a clear answer: *"Is what this code does still what its True Name implies?"* If yes, ship. If no, the boundary failed before the code did — and the code is the symptom, not the disease.

---

## 5. Ratification

The Six True Names appeared first in `docs/SYSTEM_VISION.md` §4 (2026-05-19, Skald scroll). They were used as if ratified throughout the architecture pass (2026-05-21 commit `df67f2a`) and across the fork-delta commit (2026-05-21 commit `045fda6`) — load-bearing in `pyproject.toml`, `config/ember.example.yaml`, every `INTERFACE.md`, and the on-disk Three Realms tree.

**Volmarr formally ratified all six names on 2026-05-21** with the words *"names are all approved"*. They are now canonical. Any renaming from this point forward must:

1. Be proposed in a new ADR under `docs/decisions/`.
2. Be search-and-replaced across the file tree in a single atomic commit.
3. Update this document, `SYSTEM_VISION.md` §4, `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md`, and every `INTERFACE.md` in the same commit.

This is the cost of letting them be load-bearing — and the reason ratification mattered before Phase 2 (schemas) ships.

— Sigrún Ljósbrá
