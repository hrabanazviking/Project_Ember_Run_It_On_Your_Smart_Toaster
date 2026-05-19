# docs/security/

Threat model, trust boundaries, secrets handling, and sandbox policy for a system that holds standing autonomous trust on its host machine.

## Why this folder is load-bearing

Runa's core doctrine is **standing owner trust** — she acts without per-action permission prompts on her own machine. That doctrine is only safe if the trust boundary is clearly drawn and enforced. This folder is where that drawing lives.

## Planned canonical documents

- `THREAT_MODEL.md` — what Runa is allowed to do, what she is not, who can ask what of her over which surface.
- `TRUST_BOUNDARIES.md` — the host machine, the operator (Volmarr), other humans on the same Tailnet, the public internet, third-party models — each tier's permissions.
- `SECRETS.md` — where secrets live (never in this repo), how rotation works, what the agent does on detected leak.
- `SANDBOX_POLICY.md` — what tools are permitted by default, what require explicit configuration, what are never permitted.
- `INCIDENT_RESPONSE.md` — the kill-switch, the recovery path, the post-incident audit.

Currently empty. To be drafted before `src/runa/core/` and `src/runa/services/` ship anything that touches the outside world.
