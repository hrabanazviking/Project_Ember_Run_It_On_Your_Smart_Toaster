"""`ember well status` — counts + health snapshot."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TextIO

from ember.schemas.config import EmberConfig
from ember.schemas.errors import Disconnected
from ember.spark.munnr import render
from ember.thread import strengr


def run(
    *,
    config: EmberConfig,
    stdout: TextIO | None = None,
    strengr_opener: Callable | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    open_well = strengr_opener or strengr.open

    well = open_well(config.strengr, config.brunnr)
    if isinstance(well, Disconnected):
        stdout.write(render.render_well_disconnected_banner(well) + "\n")
        return 1

    try:
        stats = well.count()
        health = strengr.health(well)
    finally:
        well.close()

    stdout.write(render.render_well_status(stats, health) + "\n")
    return 0


__all__ = ["run"]
