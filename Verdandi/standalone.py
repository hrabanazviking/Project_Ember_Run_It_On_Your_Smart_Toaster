"""Verdandi standalone law (E-073): the nerve hub usable
without the full companion.

The hub's own consumers exist in the constellation — the
heartbeat's reward producers, the conversation logger, the
Ember core's nerve bridge, and external publishers such as
Hermes (E-068) — and none of them needs the companion
running. This module states, in code, what "standalone"
means for the hub, so a builder can run it alone and know
exactly what they have:

- **One file is the hub.** ``nervous_system.py`` is a
  stdlib-only Python module: copy it (or install Verdandi)
  and it runs. No Ember core import, no other member
  import, no network, no package to install.
- **Its home is relocatable by one env var.**
  ``VERDANDI_HOME``, when set, names the hub's state dir
  directly; when unset, the hub lives at
  ``~/.hermes/state`` — the deployment every existing
  consumer already expects, unchanged. Before E-073 the
  hub's home was hard-coded to the Hermes-shaped default,
  so "standalone" quietly still meant "inside a Hermes
  home"; the env var is what makes the hub honestly
  placeable on a machine with no Hermes and no companion.
  The hub module and the core's nerve bridge each carry
  this resolution inline (the hub because its deployed
  form is a lone file, the bridge under its
  no-member-imports discipline), and the E-073 conformance
  tests pin all three resolutions equal.
- **The wire is the contract, not the companion.**
  Publishers and subscribers speak the E-061 event
  contract over the hub's Unix socket (``runa.sock`` in
  the state dir) or append/read the feed file
  (``nerve_feed.jsonl``) in the E-061 fallback shape.
  Anything that can open a Unix socket or write a JSON
  line can use the hub — that, and not Ember, is the
  integration surface. E-074 documents it for builders.

Honest limits, stated here so nobody over-reads the word
"standalone": the *heartbeat* is a separate daemon with
its own path law (``heartbeat/paths.py`` — VERDANDI_HOME
there is its own home, whose socket layout differs), and
the shipped systemd units still hard-code one machine's
paths (docket 105, owned by E-076). This law covers the
hub: its module, its home, its commands, its consumers.
"""

from __future__ import annotations

import os
from pathlib import Path

#: The one env var that relocates the hub's home.
ENV_VAR = "VERDANDI_HOME"

#: The hub module: one stdlib-only file.
HUB_MODULE = "nervous_system.py"

#: The files the hub keeps in its state dir.
SOCKET_NAME = "runa.sock"
FEED_NAME = "nerve_feed.jsonl"
PID_NAME = "nervous_system.pid"
LOG_NAME = "nervous_system.log"

#: The hub CLI's commands, in the order its usage prints.
COMMANDS = (
    "serve",
    "publish",
    "stimulus",
    "recent",
    "subscribe",
    "status",
    "healthcheck",
    "stop",
)

#: Who uses the hub without the companion, in-tree first.
CONSUMERS = (
    "hub CLI (subscribe / recent / status / healthcheck)",
    "heartbeat reward producers (publish_event_sync)",
    "conversation logger (conv_* via publish_event_sync)",
    "Ember core nerve bridge (src/ember/nerve.py)",
    "external publishers (Hermes lifecycle events, E-068)",
)


def resolve_state_dir(environ=None, home=None) -> Path:
    """The hub's state dir, by the standalone law.

    ``VERDANDI_HOME`` when set (and non-empty) wins and is
    the state dir itself — not a parent of it. Otherwise
    the hub lives at ``~/.hermes/state``, the default every
    existing consumer already expects.
    """
    env = os.environ if environ is None else environ
    override = env.get(ENV_VAR)
    if override:
        return Path(override)
    base = Path.home() if home is None else Path(home)
    return base / ".hermes" / "state"


def standalone_manifest() -> dict:
    """What a standalone hub is, as data a test can pin."""
    state_dir = resolve_state_dir()
    return {
        "hub_module": HUB_MODULE,
        "stdlib_only": True,
        "requires_companion": False,
        "requires_network": False,
        "transport": "unix-domain-socket",
        "state_dir_env": ENV_VAR,
        "state_dir": str(state_dir),
        "socket_path": str(state_dir / SOCKET_NAME),
        "feed_path": str(state_dir / FEED_NAME),
        "pid_path": str(state_dir / PID_NAME),
        "log_path": str(state_dir / LOG_NAME),
        "commands": list(COMMANDS),
        "consumers": list(CONSUMERS),
    }
