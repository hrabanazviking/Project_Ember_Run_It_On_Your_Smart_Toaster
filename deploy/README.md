# deploy/

Deployment manifests, install scripts, and container definitions.
Nothing here is imported by Ember code; this is operator-facing
infrastructure.

**Last touched:** 2026-05-21 (slice 2 ratified).

---

## Subfolders

| Folder | Holds | Slice-2 state |
|---|---|---|
| `pi/` | Raspberry Pi 5 install guide + first-boot scripts. The operator-facing source of truth for getting Ember running. | **Live.** `pi/INSTALL.md` is the primary install document — 11 sections covering Ollama setup, ember install, Hjarta first-run, ingest, chat, doctor, editing `ember.yaml`, streaming, switching to `pgvector`, enabling tools, troubleshooting. |
| `examples/` | Reference deployment recipes (single-host Pi, Pi + laptop split, multi-machine longhall). | Scaffold; sample recipes land as operators contribute them. |
| `systemd/` | User-level systemd unit files for supervising Ember as a service (`ember-chat.service`, `ember-ingest.timer`, etc.). | **Scaffold only** in slice 2; first slice and slice 2 ship as CLI-driven, not daemonised. Daemon-mode is a future-slice consideration tied to the Bifröst HTTP-gateway ADR (ADR 0012, deferred). |
| `docker/` | `Dockerfile`(s) and `docker-compose.yaml` for containerized deployment. | **Scaffold only.** The slice-1 + slice-2 install path is `pip install ember-agent` directly into a venv on the target machine; containerisation is for operators who want it but not the recommended path. |

---

## Rules (per ADR 0007 §2 + ADR 0013 §2.2)

- **No secrets in any deploy file.** Use environment variables,
  `EnvironmentFile=`, or operator-side secret stores (`~/.ember/secrets/`
  with mode-`0o600` files per ADR 0010 §2.5).
- **Every service unit declares `Restart=on-failure`** with sane
  backoff, when those files land.
- **Pi-targeted material avoids x86-only assumptions** — no SSE2, no
  Intel-specific kernels.
- **Operator config stays in `~/.ember/config/ember.yaml`**, not in
  deploy files. Per ADR 0008 §2.1 + ADR 0013 §2.2.

---

## What's here right now (slice 2 — version 0.2.0)

The Pi install guide at `pi/INSTALL.md` is the load-bearing
operator-facing document. It covers:

| Section | What it teaches |
|---|---|
| §1-2 | Install Ollama, install `ember-agent` from PyPI. |
| §3 | Hjarta's first-run wizard (now with optional `Enable tools?` branch). |
| §4-5 | Smiðja ingest + Munnr chat. |
| §6 | `ember doctor` health check. |
| §7 | Editing `~/.ember/config/ember.yaml` (slice-2 config loader). |
| §8 | Streaming on / off (slice-2 streaming Funi). |
| §9 | Switching to a shared Well via `pgvector` (slice-2 Brunnr backend). |
| §10 | Enabling tools + approval policy (slice-2 tool framework). |
| §11 | Update / reset. |
| Advanced | Non-default Ollama endpoint (`OLLAMA_HOST`); smaller Funi models. |
| Troubleshooting | Twelve common failure modes with fixes. |

---

## What's NOT here yet

- **Systemd units.** Slice-2 ships as CLI; daemon-mode waits for slice 3.
- **Docker images.** Slice-2 is `pip`-install-first; container path is
  future operator-driven.
- **Multi-host orchestration recipes.** Single-operator, single-host
  is the slice-2 deployment shape per ADR 0013 §2.4 (the
  multi-operator deferral).
