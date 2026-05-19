# tools/repo/

Repo-shape integrity checks. Tools that read this repository and report on its consistency.

Planned tools:
- `check_interface_present.py` — every `src/runa/*/` subdomain has an `INTERFACE.md`.
- `check_readme_present.py` — every directory has a `README.md`.
- `check_link_targets.py` — every `[link](path)` in `.md` resolves.
- `check_origins_drift.py` — every file in repo that didn't exist at bootstrap appears in `ORIGINS.md` or was created later.
