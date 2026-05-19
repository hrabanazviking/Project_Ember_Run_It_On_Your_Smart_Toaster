# vendor/

Third-party code that lives inside the repository rather than being installed as a dependency.

## When to vendor

Vendor a dependency only when **all** of these are true:

1. The upstream is unmaintained or unreliable.
2. The dependency is small (< ~2000 lines) and self-contained.
3. The license permits redistribution (and the license is reproduced here).
4. Pinning a version via `pyproject.toml` is not sufficient (e.g. an immediate patch is needed that upstream will not accept).

For everything else, declare a normal dependency in `pyproject.toml` and let `uv` resolve it.

## Required for each vendored item

- A subfolder named after the upstream project.
- A `LICENSE` file in that subfolder, copied verbatim from upstream.
- A `VENDOR.md` in that subfolder documenting: upstream URL, exact commit/version vendored, date vendored, reason vendored, list of local modifications.
- A line in `THIRD_PARTY_NOTICES.md` at repo root.

Currently empty — no vendored code yet.
