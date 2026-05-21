"""`ember well ingest <path>` — Smiðja into the configured Brunnr."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import TextIO

from ember.schemas.config import EmberConfig
from ember.schemas.errors import Disconnected, IngestError
from ember.spark.munnr import render
from ember.thread import strengr
from ember.well.smidja.embed_client import OllamaEmbedClient
from ember.well.smidja.local_files import run as local_files_run


def run(
    *,
    path: Path,
    config: EmberConfig,
    stdout: TextIO | None = None,
    embed_client: OllamaEmbedClient | None = None,
    strengr_opener: Callable | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    open_well = strengr_opener or strengr.open

    well = open_well(config.strengr, config.brunnr)
    if isinstance(well, Disconnected):
        stdout.write(render.render_well_disconnected_banner(well) + "\n")
        stdout.write("Ingest cannot proceed without a writable Well.\n")
        return 1

    try:
        summary = local_files_run(
            well,
            root=path,
            smidja_config=config.smidja,
            embed_client=embed_client,
        )
    except IngestError as exc:
        stdout.write(f"Ingest failed: {exc}\n")
        return 1
    finally:
        well.close()

    stdout.write(render.render_ingest_summary(summary) + "\n")
    return 0


__all__ = ["run"]
