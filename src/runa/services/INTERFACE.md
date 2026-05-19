# INTERFACE — `runa.services`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §6.

## Purpose

Long-running service shells. Each service is a thin wrapper around `runa.core` plus its own I/O surface and lifecycle.

## Public surface

Each service exposes:

| Symbol | Purpose |
|---|---|
| `<service_name>.serve(config) -> None` | Start the service in the current process. Blocks until shutdown. |
| `<service_name>.healthcheck(config) -> HealthReport` | One-shot health check usable from `runa doctor`. |

Planned services:

| Service | Module | Role |
|---|---|---|
| `gateway_service` | `runa.services.gateway_service` | HTTP/WS gateway (**Bifröst** entry-point). |
| `worker_service` | `runa.services.worker_service` | Background task executor for Skuld. |
| `voice_service` | `runa.services.voice_service` | Wake-word + microphone + TTS loop (**Rödd**). |
| `gui_service` | `runa.services.gui_service` | Window host for **Auga**. |

Each service has its own systemd unit under `deploy/systemd/`.

## Invariants

- **Each service is independently failable.** A service crash never takes another service down.
- **Each service drains gracefully on `Stopping`.** It flushes pending writes, says goodbye on its surface, then exits.
- **No service holds shared in-process state with another service** — they communicate through the gateway, the kernel, or the on-disk stores.
- **Each service's IPC is configurable** (port / socket path) and defaults to localhost-only.

## Allowed callers

`runa.cli` (to launch a service), `deploy/` unit files, tests.

## Allowed callees

`runa.schemas`, `runa.core`, `runa.runtime`, `runa.apps`.

## Failure semantics

A service exits non-zero on unrecoverable failure. The supervisor / systemd is expected to restart with backoff. Failure of one service does not affect any other.
