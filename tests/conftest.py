"""Pytest session configuration.

Ensures ``src/`` is on ``sys.path`` so tests run without requiring an
editable install. Once the first slice ships and ``pip install -e .`` is
documented in ``deploy/pi/INSTALL.md``, this shim can move to that path
or be removed in favor of a proper install-based test loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
