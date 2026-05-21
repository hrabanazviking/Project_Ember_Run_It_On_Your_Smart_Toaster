# `src/ember/spark/funi/`

**Funi** — local model runtime. One subpackage per supported runtime:

- `ollama/` — the **first-slice default** (Phase 5).
- `llamacpp/` — later.
- `lmstudio/` — later.
- `phi_silica/` — Windows Copilot+ PCs via Windows AI Foundry (Phase 8).
- `apple_foundation/` — Apple silicon via the Foundation Models framework (Phase 8).

## Status

Scaffold only. Phase 5 ships the Ollama adapter.

## Reads with

- `docs/architecture/DOMAIN_MAP.md` §5
- `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` — host-RAM-keyed ladder
- `src/ember/spark/funi/INTERFACE.md`
