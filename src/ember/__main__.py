"""Allow ``python -m ember`` to dispatch into the CLI.

Both ``python -m ember`` and the ``ember`` console-script declared in
``pyproject.toml`` resolve to :func:`ember.cli.main`.
"""

from ember.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
