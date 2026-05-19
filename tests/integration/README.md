# tests/integration/

Multi-module flows through real `src/runa/` code paths.

Allowed: local SQLite, local filesystem (under `tmp_path`), stub model that returns fixed responses, in-process event bus.

Disallowed: public internet, real model-provider APIs, real chat platform connections.
