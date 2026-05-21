"""`ember ask "..."` — one-shot ask.

Internally just feeds a single line into the chat REPL via an in-memory
StringIO so the rendering, retrieval, and persistence paths are
identical to ``ember chat``.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import TextIO

from ember.schemas.config import EmberConfig
from ember.spark.munnr import chat


def run(
    *,
    text: str,
    config: EmberConfig,
    config_root: Path,
    stdout: TextIO | None = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    fake_stdin = io.StringIO(text + "\n")
    return chat.run(
        config=config,
        config_root=config_root,
        stdin=fake_stdin,
        stdout=stdout,
    )


__all__ = ["run"]
