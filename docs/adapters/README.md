# docs/adapters/

**One document per external surface Ember speaks across.** Adapters are
where Ember meets the world outside its own process: model runtimes,
storage backends, ingest sources, tool surfaces. Each adapter doc
covers what the adapter does, what configuration it needs, what
permissions it requires on the host, what failure modes are tolerated
vs fatal, and how it degrades when its external dependency is
unreachable.

**Last touched:** 2026-05-21 (slice 2 ratified).

---

## Adapter docs as of slice 2 (0.2.0)

| Doc | Realm | What it covers | State |
|---|---|---|---|
| **`BRUNNR_BACKEND_MATRIX.md`** | Well — storage | The menu of supported Brunnr backends. `sqlite_vec` (shipped 0.1.0); `pgvector` (shipped 0.1.9); `qdrant`, `chroma`, `lancedb` (deferred per ADR 0013 §3). | Ratified |
| **`FUNI_LOCAL_MODEL_OPTIONS.md`** | Spark — reasoning | The menu of supported Funi runtimes. Ollama (shipped 0.1.0, with streaming 0.1.7 and tool-calls 0.2.0). Tool-capability note: `phi3:mini` cannot do tool calls; `llama3.2:3b` is the Pi-class tool-capable default. Other runtimes deferred per ADR 0013 §3. | Ratified |
| **`SMIDJA_INGEST_PATTERNS.md`** | Well — ingest | Chunking, embedding, and journal patterns for Smiðja sources. `local_files` shipped 0.1.0; other sources (`url_fetch`, `shared_well`, `nomad`) deferred per ADR 0013 §3. | Ratified |
| **`GUNGNIR_WELL_REFERENCE.md`** | Well — concrete | Live survey of the canonical operator Well: Volmarr's Gungnir Postgres on tailnet (95 docs / 35 682 chunks as of 2026-05-21). The shape pgvector Brunnr targets. | Live reference |
| **`PGVECTOR_BRUNNR_REFERENCE.md`** | Well — operator guide | Operator-side mirror of the Gungnir reference. Install, config, secret resolution, schema-probe semantics, read-only mode, the eight typed disconnect reasons, Phase-12-vs-13 archaeology. | Shipped 0.1.9 |

---

## What every adapter doc covers (the template)

The five docs above all follow the same shape, established in slice 1
and held in slice 2:

1. **Voice + Status + Last-touched header** — who wrote it, what
   shipping state it's in, when the doc was last refreshed.
2. **Reads-with** — pointers to the architecture docs + ADR(s) +
   peer adapter doc the operator needs alongside this one.
3. **Why this document exists** — what gap it fills, who it's for.
4. **Where the adapter lives** — config knobs, file paths, env vars.
5. **The on-disk / on-the-wire shape** — concrete formats; for
   storage adapters this is the SQL / DDL; for runtime adapters this
   is the HTTP request/response shape.
6. **Failure semantics** — what raises, what returns a typed
   `Disconnected` / `Unavailable` / error value.
7. **Limitations** — the deliberate gaps in the current slice, with
   the ADR that documented the deferral.

New adapter docs should follow this shape.

---

## Adapter surfaces NOT yet documented (deferred per ADR 0013 §3)

| Surface | Realm | Why deferred |
|---|---|---|
| `qdrant`, `chroma`, `lancedb` Brunnr backends | Well | No operator demand yet; each is a `BrunnrHandle` implementation that follows the pgvector / sqlite_vec template. |
| `llamacpp`, `lmstudio`, `phi_silica`, `apple_foundation` Funi runtimes | Spark | Same — the Protocol holds; each is a Phase-5-shaped commit. |
| `url_fetch`, `shared_well`, `nomad` Smiðja sources | Well | Slice-2 stayed on `local_files`. |
| Tool framework reference docs (per-tool) | Spark | The framework is documented at `docs/decisions/0011-tool-use-framework.md`; per-tool operator docs land if/when third-party tool authors emerge. The first three first-party tools are documented in `src/ember/tools/README.md`. |
| MCP-server bridge | Cross-cutting | Out of scope for slice 2; tracked as a future-slice question. |

---

## Reading order for operators

1. **`docs/SYSTEM_VISION.md`** — the four Vows; what the adapters
   serve.
2. **`docs/architecture/ARCHITECTURE.md` §3** — where adapters sit in
   the Three Realms.
3. **`BRUNNR_BACKEND_MATRIX.md`** + **`FUNI_LOCAL_MODEL_OPTIONS.md`** —
   the menus.
4. The specific adapter reference for whatever the operator is
   wiring up (Gungnir / pgvector / Ollama / etc.).
5. **`deploy/pi/INSTALL.md`** — the operator install walkthrough that
   ties them together.
