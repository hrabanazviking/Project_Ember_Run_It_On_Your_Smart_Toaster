# `src/ember/thread/strengr/`

**Strengr** — the tether. Makes the Well usable from Spark without
leaking the network surface into Spark code.

## What it owns

Connection lifecycle, health checks, auth (keyring on desktop, file on
Pi), retry-with-backoff, transport selection (local in-process, Unix
socket, HTTP, Tailscale endpoint), and the `Disconnected` graceful-offline
contract.

## Why it matters

Strengr is the single boundary Spark crosses to reach the Well. It is
*the* place where "the network failed" becomes *legible* instead of
catastrophic. Strengr **never raises** a connection error upward; it
returns a typed `Disconnected(reason, since)` value that Spark is
required to handle.

## Status

Scaffold only.

## Reads with

- `docs/architecture/DOMAIN_MAP.md` §4
- `docs/architecture/DATA_FLOW.md` §2.2
- `src/ember/thread/strengr/INTERFACE.md`
