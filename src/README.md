# src/

All Python implementation lives under `src/runa/`. The outer `src/` folder is a [PEP 517 src-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) marker — it prevents accidental imports during testing and forces the package to be installed (or path-injected) the same way users get it.

See `src/runa/README.md` for the package-internal map.
