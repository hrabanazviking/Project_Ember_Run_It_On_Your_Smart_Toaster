"""
ᛋᛖᛁᛞᚱ — Seiðr Engine CLI

Invoke the seiðr-worker from the command line.
Weave verse by the patterns of the ancient skalds.

Usage:
    python -m seidr.cli [form] [options]

Forms:
    fornyrthislag   Old Sayings' Meter (Eddic, concise)
    ljodhattr       Song-Meter (Hávamál style, wisdom)
    drottkvaett     Court Meter (skaldic, demanding)
    malahattr       Speech-Meter (narrative, expanded)

Options:
    --domain, -d    Limit vocabulary to a Nine World
    --stanzas, -s   Number of stanzas (default: 1)
    --kennings, -k  Use kennings (default: true)
    --seed          Random seed for reproducibility
    --frame, -f     Display in runestone ASCII frame
    --list          List available forms and domains
    --verbose, -v   Show structural metadata
"""

import argparse
import sys

from .lexicon import Lexicon
from .poet import Skald, PoemConfig
from .forms import FORMS, get_form


NINE_WORLDS_BANNER = """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║          ᛋᛖᛁᛞᚱ ENGINE                  ║
    ║       Old Norse Poetry Generator          ║
    ║                                          ║
    ║   ᛬  The Níu Heimar  ᛬                  ║
    ║                                          ║
    ║   ᚨ Asgard     — Æsir, sovereignty       ║
    ║   ᚡ Vanaheim   — Vanir, fertility         ║
    ║   ᛇ Alfheim    — Light Elves, beauty      ║
    ║   ᛗ Midgard    — Humans, struggle         ║
    ║   ᛃ Jotunheim  — Giants, chaos            ║
    ║  ᛊ Svartalfheim — Dwarves, craft          ║
    ║   ᚾ Niflheim   — Mist, origin             ║
    ║   ᛋ Muspelheim  — Fire, destruction      ║
    ║   ᚺ Helheim    — Death, endings           ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
"""

FORMS_BANNER = """
    ᛬ Available Poetic Forms ᛬

    fornyrthislag (fornyrðislag)
      Old Sayings' Meter — the most ancient Eddic form.
      4 lines per stanza, alliterating pairs. Concise, proverbial.
      ᛊ Words carved in stone, brief as a sword-stroke.

    ljodhattr (ljóðaháttr)
      Song-Meter — the meter of the Hávamál.
      6 lines, with full-line morals. For wisdom and prophecy.
      ᛊ The voice of Odin at the well.

    drottkvaett (dróttkvætt)
      Court Meter — the skald's proving ground.
      8 lines, strict alliteration + rhyme. Demanding, ornate.
      ᛊ The Olympic tier of Norse verse.

    malahattr (málaháttr)
      Speech-Meter — narrative variant of dróttkvætt.
      8 lines, more syllables, room to breathe.
      ᛊ The meter of long sagas told in verse.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="seidr",
        description="ᛋᛖᛁᛞᚱ — Old Norse Poetry Generator. Weave verse from the Nine Worlds."
    )
    
    parser.add_argument(
        "form",
        nargs="?",
        default="fornyrthislag",
        choices=["fornyrthislag", "ljodhattr", "drottkvaett", "malahattr"],
        help="Poetic form to compose in (default: fornyrthislag)"
    )
    
    parser.add_argument(
        "-d", "--domain",
        default=None,
        choices=["asgard", "vanaheim", "alfheim", "midgard", "jotunheim",
                  "svartalfheim", "niflheim", "muspelheim", "helheim"],
        help="Limit vocabulary to one of the Nine Worlds"
    )
    
    parser.add_argument(
        "-s", "--stanzas",
        type=int,
        default=1,
        help="Number of stanzas to compose (default: 1)"
    )
    
    parser.add_argument(
        "--no-kennings",
        action="store_true",
        help="Disable kennings in the generated verse"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible verse"
    )
    
    parser.add_argument(
        "-f", "--frame",
        action="store_true",
        help="Display the poem in a runestone ASCII frame"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available forms and domains, then exit"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show structural metadata alongside the verse"
    )
    
    args = parser.parse_args()
    
    # List mode
    if args.list:
        print(NINE_WORLDS_BANNER)
        print(FORMS_BANNER)
        
        # Show word counts
        lexicon = Lexicon()
        print("    ᛬ Lexicon Word Counts by Domain ᛬\n")
        for domain in sorted(lexicon.words.keys()):
            count = len(lexicon.words[domain])
            rune = {
                "asgard": "ᚨ", "vanaheim": "ᚡ", "alfheim": "ᛇ", "midgard": "ᛗ",
                "jotunheim": "ᛃ", "svartalfheim": "ᛊ", "niflheim": "ᚾ",
                "muspelheim": "ᛋ", "helheim": "ᚺ", "connectors": "᛬"
            }.get(domain, "?")
            print(f"      {rune} {domain:15s} — {count:3d} words")
        
        print(f"\n      ᛬ {len(lexicon.kennings)} kennings loaded ᛬")
        
        # Show kennings
        if lexicon.kennings:
            print("\n    ᛬ Kennings ᛬\n")
            for k in lexicon.kennings:
                print(f"      {k.base:12s} → {k.expression}")
        
        return
    
    # Compose!
    print(NINE_WORLDS_BANNER)
    
    lexicon = Lexicon(seed=args.seed)
    skald = Skald(lexicon=lexicon, seed=args.seed)
    
    config = PoemConfig(
        form=args.form,
        domain=args.domain,
        num_stanzas=args.stanzas,
        use_kennings=not args.no_kennings,
        seed=args.seed
    )
    
    # Generate multiple attempts and keep the best
    best_poem = None
    best_score = -1
    
    for attempt in range(5):
        attempt_seed = (args.seed or 42) + attempt * 7919  # Different seed each attempt
        attempt_config = PoemConfig(
            form=config.form,
            domain=config.domain,
            num_stanzas=config.num_stanzas,
            use_kennings=config.use_kennings,
            seed=attempt_seed
        )
        
        try:
            poem = skald.compose_poem(attempt_config)
            score = _score_poem(poem)
            if score > best_score:
                best_score = score
                best_poem = poem
        except Exception as e:
            continue
    
    if best_poem is None:
        print("  ᛬ The seiðr-worker could not find words today. ᛬")
        print("  ᛬ Try a different domain or form. ᛬")
        sys.exit(1)
    
    # Display
    if args.frame:
        print(best_poem.format_ascii_frame())
    else:
        print(best_poem.format())
    
    # Verbose metadata
    if args.verbose and best_poem.stanzas:
        print("\n─── Structure ───")
        form_obj = get_form(args.form)
        print(f"  Form: {form_obj.name_on()} ({form_obj.name()})")
        print(f"  Domain: {best_poem.stanzas[0].domain or 'mixed'}")
        print(f"  Stanzas: {len(best_poem.stanzas)}")
        print(f"  Quality score: {best_score:.2f}/10")
        
        for i, stanza in enumerate(best_poem.stanzas):
            print(f"\n  Stanza {i+1}:")
            for j, line in enumerate(stanza.lines):
                allit = line.alliteration_group or "?"
                print(f"    Line {j+1}: {line.syllables}syl [{allit:6s}] — {line.text}")


def _score_poem(poem) -> float:
    """Score a poem on structural quality (0-10).
    
    Penalizes repetition, rewards alliteration and varied line lengths.
    """
    if not poem.stanzas:
        return 0.0
    
    score = 5.0  # baseline
    
    all_words = []
    all_texts = []
    
    for stanza in poem.stanzas:
        for line in stanza.lines:
            all_texts.append(line.text.lower())
            all_words.extend(line.text.lower().split())
    
    # Penalty for repeated lines
    unique_texts = len(set(all_texts))
    if len(all_texts) > 1:
        diversity = unique_texts / len(all_texts)
        score += diversity * 2.0  # up to +2 for no repeats
    
    # Penalty for same word appearing too many times
    if all_words:
        word_counts = {}
        for w in all_words:
            word_counts[w] = word_counts.get(w, 0) + 1
        max_repeat = max(word_counts.values())
        if max_repeat > 2:
            score -= (max_repeat - 2) * 0.5  # -0.5 per extra repeat
    
    # Bonus for alliteration
    allit_groups = set()
    for stanza in poem.stanzas:
        for line in stanza.lines:
            if line.alliteration_group:
                allit_groups.add(line.alliteration_group)
    score += min(len(allit_groups) * 0.3, 1.0)  # up to +1 for varied alliteration
    
    # Bonus for kennings (they contain hyphens)
    kenning_count = sum(1 for t in all_texts if "-" in t)
    score += min(kenning_count * 0.5, 1.0)
    
    return max(0.0, min(10.0, score))


if __name__ == "__main__":
    main()