# config/

Configuration **templates** and **examples**. Nothing here is read at
runtime by a deployed Ember — the deployed agent reads from
`~/.ember/config/` on its host machine. The files here are what the
operator copies into `~/.ember/config/` during install, and what tests
load as fixtures.

**Last touched:** 2026-05-21 (slice 2 ratified — ADR 0008 + ADR 0013
made `~/.ember/config/ember.yaml` the single source of truth).

---

## Where Ember actually reads config (production)

At runtime, the operator's config lives at
`~/.ember/config/ember.yaml` (overridable via the `--config-root` CLI
flag). The loader is `ember.config.load_ember_config(config_root)`.

Overlay order per ADR 0008 §2.3 (innermost wins):

1. **Defaults** — every field on the dataclasses in
   `src/ember/schemas/config.py`.
2. **File** — `~/.ember/config/ember.yaml` (YAML) or `ember.toml`
   (TOML; stdlib-only loader, no PyYAML dep).
3. **Environment variables** — narrow set: `OLLAMA_HOST` (since
   Phase 7), `EMBER_WELL_PASSWORD` (Phase 12+).
4. **CLI flags** — single-invocation overrides like `--allow-tools` /
   `--no-tools` (Phase 16).

New env vars require an ADR per ADR 0013 §2.2.

---

## Files in this directory

| File | What it is | State |
|---|---|---|
| `ember.example.yaml` | The full operator template. Every section, every knob, with inline comments and pointers to the relevant ADRs. Copy to `~/.ember/config/ember.yaml` and edit. | **Live** as of Phase 9 (0.1.5). Updated in Phase 13 (pgvector) and Phase 16 (tools). |
| `storage.example.yaml` | Three worked examples for the Brunnr backend: sqlite_vec default, personal Gungnir via pgvector, shared-Gungnir read-only via pgvector. Plus the secret-resolution order spelled out. | **Live** as of Phase 13 (0.1.9). |
| `sources.example.yaml` | Smiðja ingest source registry — what to read, how often, from where. Today only the slice-1 `local_files` source is wired through; future `url_fetch` / `shared_well` / `nomad` sources will appear here. | Placeholder; expanded as Smiðja gains additional source kinds (deferred per ADR 0013 §3). |
| `profiles/` | Named bundles for common deployment shapes (Pi-only, Pi + laptop, dev-laptop). | Scaffold; profiles land as operators contribute them. |

---

## Rules (per ADR 0007 §2.10 + ADR 0010 §2.5 + ADR 0011 §2.7)

- **No secrets in this folder.** Ever. Secrets live in
  `~/.ember/secrets/` as mode-`0o600` files (the slice-2 pgvector
  resolver enforces this — see ADR 0010 §2.5).
- **No absolute paths.** All paths in `ember.example.yaml` are
  `~`-expanded or relative to `~/.ember/`.
- **Every key has a default.** Ember never refuses to start because
  of a missing optional key. The defaults live in the dataclasses
  in `src/ember/schemas/config.py`; this folder shows operators how
  to override.

---

## How to use the example file

```bash
mkdir -p ~/.ember/config
cp config/ember.example.yaml ~/.ember/config/ember.yaml
editor ~/.ember/config/ember.yaml
```

Then:

- `ember chat` reloads the config on every invocation. No daemon to
  restart.
- `ember doctor` shows the resolved Funi + Well state after the
  overlay order has been applied.
- A broken yaml fails loud with a clear error and Ember refuses to
  start — better than silent partial config.

---

## Reading order

1. `ember.example.yaml` — every knob with inline comments.
2. `storage.example.yaml` — three worked Brunnr setups.
3. `src/ember/config/INTERFACE.md` — the loader's public surface.
4. `docs/decisions/0008-config-file-loader.md` — the design rationale.
5. `deploy/pi/INSTALL.md` §7-10 — operator walkthroughs for the
   slice-2 capabilities the config enables (streaming, pgvector,
   tools).
