# ᛋᛖᛁᛞᚱ Engine — Seiðr: Old Norse Poetry Generator

> *"Wyrd bid ful araed."*

A deterministic, rule-based Old Norse poetry generation engine. No AI text generation — pure algorithmic composition within the ancient metrical constraints of the skalds.

## What Is This?

The **Seiðr Engine** weaves verse from the Nine Worlds of Norse cosmology, following the structural rules of four Old Norse poetic forms:

| Form | Old Norse | Lines | Character |
|------|-----------|-------|------------|
| **Fornyrðislag** | *fornyrðislag* | 4 | The most ancient Eddic meter — concise, proverbial, carved-in-stone |
| **Ljóðaháttr** | *ljóðaháttr* | 6 | Song-meter of the Hávamál — wisdom, prophecy, gnomic sayings |
| **Dróttkvætt** | *dróttkvætt* | 8 | Court meter — strict alliteration AND rhyme, the skald's proving ground |
| **Málaháttr** | *málaháttr* | 8 | Speech-meter — narrative, expanded, room to breathe |

## The Nine Worlds Lexicon

Vocabulary is organized by the nine realms of Yggdrasil:

- ᚨ **Asgard** — Gods, sovereignty, runes, fate, honor
- ᚡ **Vanaheim** — Vanir, fertility, magic, seafaring
- ᛇ **Alfheim** — Light Elves, beauty, starlight, art
- ᛗ **Midgard** — Humans, hearth, love, labor, struggle
- ᛃ **Jotunheim** — Giants, chaos, frost, primal forces
- ᛊ **Svartalfheim** — Dwarves, craft, deep metals, treasure
- ᚾ **Niflheim** — Mist, primordial cold, origins, obscurity
- ᛋ **Muspelheim** — Fire, destruction, transformation, rebirth
- ᚺ **Helheim** — Death, memory, grief, the inevitable

Plus a **connectors** domain for structural words (pronouns, prepositions, conjunctions, adverbs) and a **kennings** collection (poetic circumlocutions like "whale-road" for sea, "wound-wand" for sword).

## Installation

```bash
cd seidr_engine
pip install -e .
```

## Usage

### Command Line

```bash
# Generate a fornyrðislag stanza (default)
python -m seidr

# Generate in ljóðaháttr
python -m seidr ljodhattr

# Generate dróttkvætt from Jotunheim's vocabulary
python -m seidr drottkvaett -d jotunheim

# Generate 3 stanzas of fornyrðislag about Midgard
python -m seidr fornyrthislag -d midgard -s 3

# Display in a runestone ASCII frame
python -m seidr fornyrthislag --frame

# Show structural metadata
python -m seidr ljodhattr -v

# List all forms and vocabulary
python -m seidr --list

# Reproducible output with seed
python -m seidr fornyrthislag --seed 42
```

### Python API

```python
from seidr.lexicon import Lexicon
from seidr.poet import Skald, PoemConfig

# Create a seiðr-worker with a specific vocabulary
lexicon = Lexicon(seed=42)
skald = Skald(lexicon=lexicon, seed=42)

# Compose a poem
config = PoemConfig(
    form="fornyrthislag",
    domain="asgard",
    num_stanzas=2,
    use_kennings=True,
    seed=42
)
poem = skald.compose_poem(config)

# Display
print(poem.format())

# ASCII runestone frame
print(poem.format_ascii_frame())
```

## Architecture

```
seidr_engine/
├── seidr/
│   ├── __init__.py          # Package init, version
│   ├── lexicon.py           # Nine Worlds vocabulary, kennings, syllable counting
│   ├── forms.py             # Poetic form definitions (fornyrðislag, ljóðaháttr, etc.)
│   ├── poet.py              # Skald class — the poetry generation engine
│   ├── cli.py               # Command-line interface
│   └── __main__.py          # Entry point for `python -m seidr`
├── tests/
│   └── test_seidr.py        # Test suite
├── pyproject.toml            # Build configuration
└── README.md                 # This file
```

## How It Works

The Seiðr Engine does **not** use AI text generation. It composes verse through deterministic, rule-based algorithms:

1. **Lexicon** — Vocabulary organized by the Nine Worlds, each word annotated with syllable count, alliteration group, part of speech, and Old Norse equivalent
2. **Forms** — Structural constraints defining meter, line count, alliteration patterns
3. **Skald** — The composition engine that:
   - Picks a domain and alliteration group
   - Selects line templates (adj+noun+verb, noun+and+noun, etc.)
   - Fills templates with words matching syllable and alliteration constraints
   - Composes multiple attempts and scores them (diversity, alliteration, kenning usage)
   - Returns the best result

The composition is deterministic with a seed — the same seed always produces the same poem. Like the Norns weaving Wyrd, the pattern is fixed once the thread is set.

## Kennings

Kennings are Norse poetic circumlocutions — calling the sea "whale-road", a sword "wound-wand", gold "tears of the sun". The engine includes a growing collection:

- `battle` → storm of spears, riot of iron, clash of shields
- `sea` → whale-road, ship-path
- `sword` → wound-wand, fire of the wound
- `gold` → tears of the sun, fire of the arm
- `poetry` → mead of Odin, Kvasir's blood
- `earth` → flesh of Ymir

## Philosophy

Code is craft. Poetry is code. The skalds who composed dróttkvætt were following algorithmic constraints — strict meter, alliteration rules, rhyme schemes — just expressed in human language rather than Python. The Seiðr Engine is my way of honoring that: treating their craft as what it was — an ancient programming language for meaning.

The name *seiðr* comes from the Norse practice of sorcery and prophecy, primarily associated with Freyja and the Vanir. A seiðr-worker sits between worlds, weaving wyrd-threads into patterns that were always meant to exist. That's what this engine does — it doesn't invent, it *reveals*.

---

*ᚱ — Runa Gridweaver Freyjasdóttir, May 2026*

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.