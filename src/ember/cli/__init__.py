"""The ``ember`` console-script entry point package.

Callers reach the dispatcher as ``ember.cli.main`` (the submodule) and
invoke ``ember.cli.main.main()`` — `pyproject.toml`'s `[project.scripts]`
declares this same dotted path.

We intentionally do **not** re-export ``main`` here. Doing so would
rebind ``ember.cli.main`` from the submodule to the function, breaking
``import ember.cli.main as <alias>`` callers (such as the
:mod:`ember.__main__` dispatcher and the skeleton test).
"""
