# docs/plugins/

How third-party plugins are written, packaged, registered, sandboxed, and removed.

Plugins are user-facing extensions. Adapters (`docs/adapters/`) are first-party connections to specific external systems. Skills (`src/runa/skills/`) are agent-facing capabilities. Plugins are the third lane: a path for users to add new behavior without touching the core repository.

## Planned canonical documents

- `PLUGIN_CONTRACT.md` — the API a plugin must implement, lifecycle hooks, allowed imports.
- `AUTHOR_GUIDE.md` — how to write, test, and publish a plugin.
- `SANDBOXING.md` — what plugins can and cannot do on the host machine, how the trust boundary is enforced.
- `REGISTRY.md` — discovery and installation of community plugins.

Currently empty. To be drafted before the first third-party plugin lands.
