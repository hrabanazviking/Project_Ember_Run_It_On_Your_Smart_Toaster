"""`ember doctor` — diagnostics across all realms.

Calls :func:`strengr.open` + :meth:`BrunnrHandle.count` + ``Strengr.health``
for the Well, :func:`funi.open` + :meth:`FuniHandle.health` for Funi, and
renders a combined report. Never raises — every realm's failure is
folded into the rendered output so the operator sees the whole picture.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TextIO

from ember.schemas.config import EmberConfig
from ember.schemas.errors import Disconnected
from ember.schemas.funi import Unavailable
from ember.spark.funi import handle as funi_handle
from ember.spark.munnr import render
from ember.thread import strengr


def run(
    *,
    config: EmberConfig,
    stdout: TextIO | None = None,
    funi_opener: Callable | None = None,
    strengr_opener: Callable | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    open_funi = funi_opener or funi_handle.open
    open_well = strengr_opener or strengr.open

    funi_health = None
    funi_unavailable_detail = None
    well_health = None
    well_stats = None
    well_disconnected_detail = None

    funi_result = open_funi(config.funi)
    if isinstance(funi_result, Unavailable):
        funi_unavailable_detail = f"{funi_result.reason.value} — {funi_result.detail or ''}"
    else:
        try:
            funi_health = funi_result.health()
        finally:
            funi_result.close()

    well_result = open_well(config.strengr, config.brunnr)
    if isinstance(well_result, Disconnected):
        well_disconnected_detail = (
            f"{well_result.reason.value} — {well_result.detail or ''}"
        )
    else:
        try:
            well_stats = well_result.count()
            well_health = strengr.health(
                well_result, timeout_s=config.strengr.health_check_timeout_s,
            )
        finally:
            well_result.close()

    report = render.render_doctor(
        funi_health=funi_health,
        strengr_health=well_health,
        brunnr_stats=well_stats,
        funi_unavailable=funi_unavailable_detail,
        well_disconnected=well_disconnected_detail,
    )
    stdout.write(report + "\n")

    if funi_unavailable_detail or well_disconnected_detail:
        return 1
    return 0


__all__ = ["run"]
