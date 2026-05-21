"""Ember Agent — a small, tethered, runs-anywhere AI companion.

The compact statement of intent lives at ``docs/SYSTEM_VISION.md``.
The compact statement of method lives at ``MYTHIC_ENGINEERING.md``.
The map of every subpackage lives at ``docs/architecture/DOMAIN_MAP.md``.
The plan of the first slice lives at ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md``.

Phases 1-5 of the first slice are complete: typed schemas under
:mod:`ember.schemas`; the Well realm via
:mod:`ember.well.brunnr.sqlite_vec` and :mod:`ember.well.smidja`; the
Thread realm via :mod:`ember.thread.strengr`; and Funi via
:mod:`ember.spark.funi.ollama` with a runtime-neutral prompt assembler
in :mod:`ember.spark.funi.prompt`. :mod:`ember.spark.hjarta`,
:mod:`ember.spark.munnr`, and :mod:`ember.cli` remain scaffolds;
``python -m ember`` still raises ``NotImplementedError``.
"""

__version__ = "0.0.0"
