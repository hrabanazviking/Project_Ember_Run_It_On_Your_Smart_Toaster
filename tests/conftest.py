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


import pytest


@pytest.fixture(autouse=True)
def _isolate_nerve_bridge(monkeypatch):
    """Keep the E-067 nerve bridge out of the real hub home.

    Chat sessions publish ember_session / ember_turn events to
    the Verdandi hub's state dir (~/.hermes/state) by design.
    In tests that dir is the operator's live deployment, so the
    bridge's home is redirected to a per-test tmp dir — a test
    that wants the bridge points it somewhere itself. The dir
    is a short /tmp path: AF_UNIX socket paths cap at ~108
    chars, which deep pytest tmp paths exceed.
    """
    try:
        import ember.nerve as nerve
    except Exception:
        return
    import tempfile

    short = Path(tempfile.mkdtemp(prefix="nbrv", dir="/tmp"))
    monkeypatch.setattr(nerve, "hub_state_dir", lambda: short)
