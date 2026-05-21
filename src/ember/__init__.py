"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.
The plan of the first slice lives at ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md``.

Phases 1-3 of the first slice are complete: the typed schemas under
:mod:`ember.schemas` are populated, and the Well realm is wired —
:mod:`ember.well.brunnr.sqlite_vec` is a working adapter against
sqlite-vec, and :mod:`ember.well.smidja` ships chunker, embed client,
journal, and the `local_files` orchestrator. :mod:`ember.thread`,
:mod:`ember.spark`, and :mod:`ember.cli` remain scaffolds;
``python -m ember`` still raises ``NotImplementedError``.
"""

__version__ = "0.0.0"
