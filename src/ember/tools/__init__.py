"""First-party tools (ADR 0011 part 2 — Phase 15).

Each submodule registers itself at import time via
:func:`ember.spark.funi.tools.registry.register`. Importing this
package imports every first-party tool, which is the canonical way the
host (Munnr) wires the registry::

    import ember.tools  # noqa: F401 — side-effect import for tool registration

Tools live one level out from ``ember.spark.funi.tools`` (the
*framework*) because a tool author shouldn't have to navigate Funi
internals to add one. See ``README.md`` in this directory for the
first-party-tool conventions.
"""

from __future__ import annotations

# Side-effect imports — each module's top-level register() call hooks
# the tool into the process-global registry.
from ember.tools import fetch_url, read_local_file, search_well  # noqa: F401

__all__: list[str] = []
