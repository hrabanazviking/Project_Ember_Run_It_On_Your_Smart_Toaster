# INTERFACE — `runa.apps`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**True Names:** **Auga** (GUI), **Rödd** (voice), **Bifröst** (gateway).
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §7.

## Purpose

The user-experience layer for each surface. Where Runa is seen, heard, typed against. Each app pairs with a service in `runa.services/`.

## Public surface

Each app exposes:

| Symbol | Purpose |
|---|---|
| `<app_name>.App` | The app class. Service shells instantiate one per process. |
| `<app_name>.App.run(kernel_handle, config) -> None` | Block running the app against the given kernel. |

Planned apps:

| App | Module | Surface |
|---|---|---|
| `gateway_app` | `runa.apps.gateway` | HTTP/WS server (FastAPI or Starlette). Underlies all chat-bridge adapters. |
| `gui_app` | `runa.apps.gui` | Window — **Auga**. Pi-and-laptop deployments may host this only on the laptop. |
| `voice_app` | `runa.apps.voice` | **Rödd** — wake-word, capture, TTS playback. |
| `cli_app` | `runa.apps.cli` | The interactive **Munnr** shell (distinct from `runa.cli`, which parses commands). |

## Invariants

- **Apps read from `runa.core` only through the kernel handle.** They never reach into `core/memory/` or `core/tasks/` directly.
- **Each app fails alone.** A crash in `voice_app` does not bring down `gateway_app` or `cli_app`.
- **No app holds persistent state.** All persistence is in the stores managed by `runa.core`.
- **Each app respects identity.** Runa's name, voice, and persona come from `runa.core.identity`; an app may not hard-code them.

## Allowed callers

`runa.services` (the only legitimate way to construct and run an app).

## Allowed callees

`runa.schemas`, `runa.core` (through declared interfaces).

## Failure semantics

App-level failures degrade only their own surface. Logged via `core/logging`, surfaced via `runa doctor`. The kernel keeps running with the remaining surfaces.
