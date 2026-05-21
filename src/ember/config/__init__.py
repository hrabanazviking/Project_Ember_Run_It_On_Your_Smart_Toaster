"""Operator config-file loader.

See :file:`INTERFACE.md` for the full contract. The canonical entry is
:func:`load_ember_config`.
"""

from ember.config.loader import load_ember_config
from ember.config.writer import (
    ember_config_exists,
    ember_config_path,
    write_ember_config,
)
from ember.schemas.errors import ConfigError

__all__ = [
    "ConfigError",
    "ember_config_exists",
    "ember_config_path",
    "load_ember_config",
    "write_ember_config",
]
