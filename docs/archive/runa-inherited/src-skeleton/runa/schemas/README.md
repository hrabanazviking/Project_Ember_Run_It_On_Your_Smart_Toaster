# src/runa/schemas/

Pydantic models, dataclasses, and shared type definitions imported across other subpackages.

This folder has no dependency on any other subpackage. Everything else depends on it; it depends on nothing inside `runa.*`.

If a type is used in exactly one subpackage, it stays there. A type only earns a home here when at least two subpackages need it.

See `INTERFACE.md`.
