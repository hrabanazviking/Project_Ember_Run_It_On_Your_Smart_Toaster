"""Allow ``python -m ember`` to dispatch into the CLI.

The actual ``ember`` console script is declared in ``pyproject.toml`` under
``[project.scripts]`` and also resolves to :func:`ember.cli.main.main`.

Phase 1 of the first slice (this commit) ships the realm scaffolding only.
``ember.cli.main`` is created but contains no commands yet, so invoking
this entry point during Phase 1 raises a friendly ``NotImplementedError``
pointing at the first-slice plan.
"""


def main() -> int:
    raise NotImplementedError(
        "Ember's first slice has not landed yet. See "
        "docs/architecture/EMBER_FIRST_SLICE_PLAN.md for the seven-phase "
        "plan. Phase 1 (this commit) builds the structural skeleton only."
    )


if __name__ == "__main__":
    raise SystemExit(main())
