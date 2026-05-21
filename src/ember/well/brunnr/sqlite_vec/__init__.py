"""sqlite-vec Brunnr adapter — the first-slice default backend.

Public surface: the :class:`SqliteVecBrunnr` class and the module-level
:func:`open` helper that ``ember.well.brunnr.handle.open`` dispatches to.
"""

from ember.well.brunnr.sqlite_vec.adapter import SqliteVecBrunnr, open

__all__ = ["SqliteVecBrunnr", "open"]
