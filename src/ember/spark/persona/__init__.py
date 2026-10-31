"""Persona core — loading, saving, and memory separation (E-025)."""

from ember.spark.persona.core import (
    episodes_for_persona,
    list_persona_ids,
    load_persona,
    persona_dir,
    persona_path,
    resolve_persona,
    save_persona_atomic,
    tag_episode,
)

__all__ = [
    "episodes_for_persona",
    "list_persona_ids",
    "load_persona",
    "persona_dir",
    "persona_path",
    "resolve_persona",
    "save_persona_atomic",
    "tag_episode",
]
