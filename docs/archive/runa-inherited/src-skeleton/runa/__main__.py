"""Allow ``python -m runa`` to dispatch into the CLI.

The actual ``runa`` console script is declared in ``pyproject.toml`` under
``[project.scripts]`` and also resolves to :func:`runa.cli.main.main`.
"""

from runa.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
