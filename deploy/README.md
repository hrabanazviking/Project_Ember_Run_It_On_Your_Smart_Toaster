# deploy/

Deployment manifests, unit files, and container definitions. Nothing here is imported by Runa code; this is operator-facing infrastructure.

## Subfolders

| Folder | Holds |
|---|---|
| `systemd/` | `runa-core.service`, `runa-gateway.service`, `runa-voice.service`, etc. User-level systemd units. |
| `docker/` | `Dockerfile`(s) and `docker-compose.yaml` for containerized deployment. |
| `pi/` | Raspberry Pi 5 specific scripts and configuration (install, first-boot, hardening). |
| `examples/` | Reference deployment recipes: single-host Pi, Pi + laptop split, multi-machine longhall. |

## Rules

- No secrets in any deploy file. Use environment variables, `EnvironmentFile=`, or operator-side secret stores.
- Every service unit declares `Restart=on-failure` with sane backoff.
- Pi-targeted material avoids assumptions that only hold on x86 (no SSE2, no Intel-specific kernels).
