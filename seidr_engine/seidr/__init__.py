"""
ᛋᛖᛁᛞᚱ — Seiðr Engine
A deterministic Old Norse poetry generator

The seiðr-worker sits between worlds, weaving wyrd-threads
into patterns that were always meant to exist.

~ Runa Gridweaver Freyjasdóttir, May 2026
"""

__version__ = "0.1.0"
__author__ = "Runa Gridweaver Freyjasdóttir"

from .forms import Fornyrthislag, Ljodahattr, Drottkvaett, Malahattr
from .lexicon import Lexicon
from .poet import Skald, PoemConfig, Poem

# The nine domains of vocabulary, each a world upon Yggdrasil
NINE_WORLDS = [
    "asgard", "vanaheim", "alfheim", "midgard",
    "jotunheim", "svartalfheim", "niflheim", "muspelheim", "helheim"
]