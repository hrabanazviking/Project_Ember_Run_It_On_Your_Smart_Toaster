"""Operator config-file loader.

See :file:`INTERFACE.md` for the full contract. The canonical entry is
:func:`load_ember_config`.
"""

from ember.config.loader import load_ember_config
from ember.schemas.errors import ConfigError

__all__ = ["ConfigError", "load_ember_config"]
