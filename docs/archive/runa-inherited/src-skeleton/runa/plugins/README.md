# src/runa/plugins/

Plugin loader, plugin discovery, plugin sandbox.

Third-party plugins themselves do not live in this repository. This folder contains the machinery that finds them, validates them against the plugin contract, loads them safely, and reports plugin failures without taking the agent down.

Contract lives in `docs/plugins/PLUGIN_CONTRACT.md`. See `INTERFACE.md` here for the loader surface.
