"""`ember setup` / `ember setup --reset` — invoke Hjarta."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

from ember.schemas.config import EmberConfig
from ember.spark.hjarta import HjartaIO, has_identity, reset_identity
from ember.spark.hjarta import run as hjarta_run


def run(
    *,
    config: EmberConfig,
    config_root: Path,
    reset: bool = False,
    stdout: TextIO | None = None,
    io: HjartaIO | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout

    if has_identity(config_root) and not reset:
        stdout.write(
            f"Ember is already set up at {config_root}. "
            f"Use `ember setup --reset` to start over.\n"
        )
        return 0

    if reset:
        reset_identity(config_root)

    outcome = hjarta_run(config=config, config_root=config_root, io=io)
    if not outcome.success:
        stdout.write(
            f"Setup did not complete ({outcome.final_state.value}): "
            f"{outcome.detail or 'no detail'}\n"
        )
        return 1

    stdout.write(
        f"Identity written to {outcome.identity_path}.\n"
    )
    return 0


__all__ = ["run"]
