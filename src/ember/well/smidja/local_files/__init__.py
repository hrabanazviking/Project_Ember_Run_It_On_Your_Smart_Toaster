"""local_files Smiðja source — the first-slice ingest source."""

from ember.well.smidja.local_files.source import (
    DEFAULT_EXCLUDE,
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_INCLUDE,
    DEFAULT_INCLUDE_SUFFIXES,
    run,
    walk,
)

__all__ = [
    "DEFAULT_EXCLUDE",
    "DEFAULT_EXCLUDE_DIRS",
    "DEFAULT_INCLUDE",
    "DEFAULT_INCLUDE_SUFFIXES",
    "run",
    "walk",
]
