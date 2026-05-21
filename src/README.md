# src/

All Python implementation lives under `src/ember/`. The outer `src/`
folder is a [PEP 517 src-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
marker — it prevents accidental imports during testing and forces the
package to be installed (or path-injected) the same way operators get
it.

The src-layout means `import ember` only succeeds after either:

- `pip install -e .` (editable install for development), or
- `pip install ember-agent` (operator install), or
- `PYTHONPATH=src python ...` (path injection — used by some manual
  smoke scripts).

`pytest` discovers the package via the same mechanism through
`pyproject.toml`'s `[tool.pytest.ini_options]` configuration.

See `src/ember/README.md` for the realm-by-realm package map.
