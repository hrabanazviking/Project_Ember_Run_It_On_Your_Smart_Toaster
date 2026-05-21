# FUNI_LOCAL_MODEL_OPTIONS — Local Models for the Spark

**Voice:** Forge Worker (Eldra Járnsdóttir)
**Status:** Proposed — for ratification. Bootstrap-stage reference.
**Last touched:** 2026-05-21
**Reads with:** `docs/architecture/ARCHITECTURE.md` §3.1, `docs/architecture/DOMAIN_MAP.md` §5, `docs/AI_OS_Research/AI_OS_RESEARCH_2026.md` (inherited).

---

## 1. The Forge Worker's selection rule

Funi is the only model running inside the Spark. The selection rule is:

> **Pick the smallest model that can do the operator's actual work, on the operator's actual hardware, with the operator's actual offline tolerance.**

Anything larger is the Vow of Smallness being broken. Anything that requires more cooperation from the cloud than the operator already gives is the Vow of Tethered Grounding being broken (the *Well* grounds Funi; an OpenAI call does not).

---

## 2. The default ladder

The recommendation, ordered by host class, for the first slice's bundled defaults:

| Host class | Recommended Funi | Runtime | Resident RAM (approx Q4) | Notes |
|---|---|---|---|---|
| Pi 4 (4 GB) — barely capable | `qwen2.5:0.5b-instruct` | Ollama | ~600 MB | The "actually fits on the toaster" choice. Limited reasoning. Honest replies stay short. |
| Pi 5 (4 GB) | `qwen2.5:1.5b-instruct` *or* `llama3.2:1b` | Ollama | ~1.3 GB | Good middle ground. |
| Pi 5 (8 GB) — **default target** | `phi3:mini` (3.8B) *or* `qwen2.5:3b-instruct` | Ollama | ~2.2–2.5 GB | The first-slice default. Strong small-model reasoning. |
| Pi 5 (16 GB) | `qwen2.5:7b-instruct` *or* `llama3.1:8b` | Ollama / llama.cpp | ~5–6 GB | Comfortable; leaves room for embedding model alongside. |
| Old laptop, fanless x86 box, NUC | Above + `mistral-small`, `gemma2:9b`, etc. | Ollama / llama.cpp / LM Studio | 6–12 GB | Operator preference. |
| Windows Copilot+ PC | **Phi Silica** via Windows AI APIs | `phi_silica/` adapter | OS-managed | NPU-resident; minimal RAM impact. Adapter ships when Windows AI Foundry is stable. |
| Apple silicon (M1+) | **Apple Foundation Models** (~3B on-device) | `apple_foundation/` adapter | OS-managed | Reachable via the Foundation Models framework; adapter ships when the bridge is wired. |

The first slice supports **Ollama only** (one Funi adapter). The above ladder lets Hjarta pick a sensible default for the detected host RAM without committing to other adapters before they exist.

---

## 3. Hjarta's auto-recommendation heuristic

Pseudocode is forbidden by `RULES.AI.md`. Here is the recommendation as a data table that Hjarta will read at runtime:

```yaml
# config/hjarta_funi_ladder.yaml (planned)
ladder:
  - host_ram_gb_min: 14
    recommend: qwen2.5:7b-instruct
    fallback: llama3.1:8b
    note: "Comfortable host. Leaves room for the embedding model."
  - host_ram_gb_min: 6
    recommend: phi3:mini
    fallback: qwen2.5:3b-instruct
    note: "Default toaster-class target. Strong small-model reasoning."
  - host_ram_gb_min: 3
    recommend: qwen2.5:1.5b-instruct
    fallback: llama3.2:1b
    note: "Light host. Replies are short and direct."
  - host_ram_gb_min: 0
    recommend: qwen2.5:0.5b-instruct
    fallback: null
    note: "Barely-capable host. Honest is better than impressive here."
```

Hjarta reads the YAML, asks Ollama which of those models are already pulled, and offers the smallest still-recommendable model that is present (or asks before pulling).

---

## 4. The Funi adapter interface in concrete

(Detailed in `docs/architecture/DOMAIN_MAP.md` §5.1.)

A Funi adapter implements four functions:

- `open(config)` → handle or `Unavailable`. Validates the model is loaded; for Ollama, sends a HEAD-ish probe.
- `complete(prompt, context, tools=None)` → `FuniReply`. **No streaming in the first slice.**
- `embed(texts)` *(optional)* → list of embedding vectors. If absent, Smiðja uses its own embedding endpoint.
- `health()` → `FuniHealth(model_id, ram_use, last_ok)`. For `ember doctor`.

The Ollama-specific adapter's `complete` wraps `POST /api/generate` (or `/api/chat` if the system prompt benefits from it). Temperature, top-p, and max tokens are operator-configurable in `config/ember.yaml`. The default `max_tokens` is **127000** per RULES.AI.md, with the caveat that any tiny model will OOM before reaching that — the model's *own* context limit applies first.

---

## 5. Why Phi Silica and Apple Foundation Models are second-slice (not first)

The first slice ships one adapter to *prove the shape works*. Adding Phi Silica or Apple Foundation Models first would mean:

- shipping platform-specific code paths before the Brunnr/Smiðja/Strengr triad is proven on Linux,
- coupling the first-slice acceptance to a Windows or macOS host,
- spending design budget on the bridge instead of the spine.

Both ship in **Phase 8** (parallel to Gungnir's pgvector Brunnr), each as its own subpackage under `src/ember/spark/funi/`. They become first-class peers of the Ollama adapter once they land.

For the Cartographer's notes on the AI-OS landscape that drives this, see the inherited `docs/AI_OS_Research/AI_OS_RESEARCH_2026.md`.

---

## 6. Models considered and not on the ladder (and why)

| Model | Why not on the default ladder |
|---|---|
| `tinyllama:1.1b` | Reasoning quality at Q4 has not held up vs `qwen2.5:1.5b` in late-2025 testing. Operator may still pick it; not the default. |
| `gemma2:2b` | Strong but Google-license caveats and weaker tool-call format than Qwen2.5. Available via Ollama; not the recommended default. |
| `mistral:7b-instruct` (v0.2/v0.3) | Older. `qwen2.5:7b-instruct` matches or beats it at the same size. |
| `llama3.2:3b` | Good; basically interchangeable with `qwen2.5:3b-instruct`. Operator-preference; not the default to keep the ladder short. |
| `gpt-oss-*` (any size) | Cloud-call defeats the Vow of Tethered Grounding. Never on the ladder. |
| Any > 14B at Q4 | RAM-incompatible with the toaster story. Operators with workstation-class hosts run Runa, not Ember. |

---

## 7. The embedding model question

Funi may or may not embed (per `INTERFACE.md` §5.1's `embed(texts)` optional). The decoupling matters because the embedding model and the reasoning model have different size sweet spots:

| Embedding model | Dim | Recommended host class |
|---|---|---|
| `nomic-embed-text` (Ollama) | 768 | Anything Pi 5 8GB or larger. Gungnir uses this. |
| `bge-small-en-v1.5` | 384 | Lighter hosts. Half the storage; comparable quality on English. |
| `bge-base-en-v1.5` | 768 | Same class as nomic-embed-text. |
| `mxbai-embed-large` | 1024 | Heavier; not recommended for Pi-class Wells (storage cost). |

**Recommendation:** Match Gungnir. Use `nomic-embed-text` (768) by default. If the operator's Well will be shared with Gungnir, the dim must match exactly — pgvector indexes are dim-specific. See `GUNGNIR_WELL_REFERENCE.md` §3 for the consequence.

---

## 8. The Forge Worker's closing word

> *Pick the small one. You can always replace it. You cannot always afford the big one.*

— Eldra Járnsdóttir
