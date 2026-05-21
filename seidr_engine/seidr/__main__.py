"""
ᛋᛖᛁᛞᚱ — Seiðr Engine
Deterministic Old Norse poetry generator

Usage:
    python -m seidr                    # Generate a fornyrðislag stanza
    python -m seidr ljodhattr           # Generate in ljóðaháttr
    python -m seidr drottkvaett -d jotunheim  # Jotunheim-themed dróttkvætt
    python -m seidr --list              # Show available forms & vocabulary
    python -m seidr --help              # Full usage info
"""

from .cli import main

if __name__ == "__main__":
    main()