"""
ᛋᚲᚨᛚᛞ — The Skald
Poetry generation engine that weaves verse from lexicon and form.

The seiðr-worker chants, the skald carves.
This module breathes life into structural constraints.
"""

import random
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .lexicon import Lexicon, WordEntry, Kenning, count_syllables_approx
from .forms import (
    PoeticForm, Fornyrthislag, Ljodahattr, Drottkvaett, Malahattr,
    Line, HalfStanza, Stanza, get_form
)


@dataclass
class PoemConfig:
    """Configuration for poem generation."""
    form: str = "fornyrthislag"  # poetic form name
    domain: Optional[str] = None  # limit vocabulary to a world/domain
    topic: Optional[str] = None  # thematic topic hint
    num_stanzas: int = 1
    use_kennings: bool = True
    include_old_norse: bool = False  # show Old Norse alongside English
    alliteration_strictness: float = 0.7  # 0.0-1.0, probability of enforcing alliteration
    seed: Optional[int] = None


class Skald:
    """The poet-engine that generates Norse verse.
    
    A Skald draws from the Lexicon (the Nine Worlds of vocabulary)
    and weaves according to the Form (metrical constraints).
    
    The result is poetry — not random words forced into meter,
    but algorithmic composition that honors both structure and spirit.
    """
    
    def __init__(self, lexicon: Optional[Lexicon] = None, seed: Optional[int] = None):
        self.lexicon = lexicon or Lexicon(seed=seed)
        self._rng = random.Random(seed)
        self._attempt_counter = 0
        self._used_words = set()  # track words used in current composition to avoid repetition
    
    def compose(self, config: Optional[PoemConfig] = None) -> Stanza:
        """Compose a complete stanza of Norse verse."""
        if config is None:
            config = PoemConfig()
        
        # Reset used words for fresh composition
        self._used_words = set()
        
        form = get_form(config.form)
        domain = config.domain
        
        if config.seed is not None:
            self._rng = random.Random(config.seed)
        
        if form.name() == "fornyrthislag":
            return self._compose_fornyrthislag(config, form)
        elif form.name() == "ljodhattr":
            return self._compose_ljodhattr(config, form)
        elif form.name() == "drottkvaett":
            return self._compose_drottkvaett(config, form)
        elif form.name() == "malahattr":
            return self._compose_malahattr(config, form)
        else:
            return self._compose_fornyrthislag(config, form)
    
    def compose_poem(self, config: Optional[PoemConfig] = None) -> 'Poem':
        """Compose a full poem (potentially multiple stanzas)."""
        if config is None:
            config = PoemConfig()
        
        stanzas = []
        for i in range(config.num_stanzas):
            # Slightly vary the seed for each stanza
            stanza_config = PoemConfig(
                form=config.form,
                domain=config.domain,
                topic=config.topic,
                num_stanzas=1,
                use_kennings=config.use_kennings,
                include_old_norse=config.include_old_norse,
                alliteration_strictness=config.alliteration_strictness,
                seed=(config.seed or 42) + i * 1000 + self._rng.randint(0, 999) if config.seed else None
            )
            stanza = self.compose(stanza_config)
            stanzas.append(stanza)
        
        return Poem(stanzas=stanzas, config=config)
    
    def _compose_fornyrthislag(self, config: PoemConfig, form: PoeticForm) -> Stanza:
        """Compose a fornyrðislag stanza.
        
        Structure: 4 lines, 2 alliterating pairs.
        Lines 0-1 are a pair, lines 2-3 are a pair.
        """
        # Pick a thematic domain if not specified
        domain = config.domain or self._pick_domain()
        
        # Pick alliteration groups for each pair
        pair_1_alliteration = self._pick_alliteration_group(domain)
        pair_2_alliteration = self._pick_alliteration_group(domain)
        
        lines = []
        
        # Compose pair 1 (lines 0-1)
        pair_1 = self._compose_alliterating_pair(
            domain=domain,
            alliteration=pair_1_alliteration,
            syllable_range=form.syllable_range(),
            config=config
        )
        lines.extend(pair_1)
        
        # Compose pair 2 (lines 2-3)
        pair_2 = self._compose_alliterating_pair(
            domain=domain,
            alliteration=pair_2_alliteration,
            syllable_range=form.syllable_range(),
            config=config
        )
        lines.extend(pair_2)
        
        half_stanzas = [
            HalfStanza(lines=(lines[0], lines[1])),
            HalfStanza(lines=(lines[2], lines[3])),
        ]
        
        return Stanza(
            half_stanzas=half_stanzas,
            form=form.name(),
            topic=config.topic,
            domain=domain
        )
    
    def _compose_ljodhattr(self, config: PoemConfig, form: PoeticForm) -> Stanza:
        """Compose a ljóðaháttr stanza.
        
        Structure: 6 lines in two half-stanzas.
        Each half-stanza: 2 alliterating lines + 1 full line.
        The full line is longer and carries the moral weight.
        
        Format:
            Line 1  ~~//~~  Line 2    (alliterating pair)
                Full Line 3              (completes the thought)
            
            Line 4  ~~//~~  Line 5    (alliterating pair)
                Full Line 6              (the moral lands)
        """
        domain = config.domain or self._pick_domain()
        
        allit_half_1 = self._pick_alliteration_group(domain)
        allit_half_2 = self._pick_alliteration_group(domain)
        
        # Half-stanza 1: alliterating pair
        pair_1 = self._compose_alliterating_pair(
            domain=domain,
            alliteration=allit_half_1,
            syllable_range=(4, 6),
            config=config
        )
        
        # The full line — longer, free structure, carries the punch
        full_line_1 = self._compose_full_line(
            domain=domain,
            min_syllables=5,
            max_syllables=8,
            config=config
        )
        
        # Half-stanza 2: alliterating pair
        pair_2 = self._compose_alliterating_pair(
            domain=domain,
            alliteration=allit_half_2,
            syllable_range=(4, 6),
            config=config
        )
        
        full_line_2 = self._compose_full_line(
            domain=domain,
            min_syllables=5,
            max_syllables=8,
            config=config
        )
        
        half_stanzas = [
            HalfStanza(lines=(pair_1[0], pair_1[1])),
            HalfStanza(lines=(pair_2[0], pair_2[1])),
        ]
        
        return Stanza(
            half_stanzas=half_stanzas,
            form=form.name(),
            topic=config.topic,
            domain=domain,
            full_lines=[full_line_1, full_line_2]
        )
    
    def _compose_drottkvaett(self, config: PoemConfig, form: PoeticForm) -> Stanza:
        """Compose a dróttkvætt stanza.
        
        Structure: 8 lines, 4 couplets. Strict alliteration + rhyme.
        This is the hardest form — we approximate with alliteration
        and aim for 6 syllables per line.
        """
        domain = config.domain or self._pick_domain()
        
        lines = []
        alliteration_groups = [
            self._pick_alliteration_group(domain),
            self._pick_alliteration_group(domain),
            self._pick_alliteration_group(domain),
            self._pick_alliteration_group(domain),
        ]
        
        # Each couplet shares an alliteration group
        for i, allit_group in enumerate(alliteration_groups):
            couplet = self._compose_alliterating_pair(
                domain=domain,
                alliteration=allit_group,
                syllable_range=(5, 7),
                config=config
            )
            lines.extend(couplet)
        
        half_stanzas = [
            HalfStanza(lines=(lines[0], lines[1])),
            HalfStanza(lines=(lines[2], lines[3])),
            HalfStanza(lines=(lines[4], lines[5])),
            HalfStanza(lines=(lines[6], lines[7])),
        ]
        
        return Stanza(
            half_stanzas=half_stanzas,
            form=form.name(),
            topic=config.topic,
            domain=domain
        )
    
    def _compose_malahattr(self, config: PoemConfig, form: PoeticForm) -> Stanza:
        """Compose a málaháttr stanza — like dróttkvætt but with more syllables."""
        # Same structure as dróttkvætt but wider syllable range
        domain = config.domain or self._pick_domain()
        
        lines = []
        alliteration_groups = [
            self._pick_alliteration_group(domain) for _ in range(4)
        ]
        
        for allit_group in alliteration_groups:
            couplet = self._compose_alliterating_pair(
                domain=domain,
                alliteration=allit_group,
                syllable_range=(5, 8),
                config=config
            )
            lines.extend(couplet)
        
        half_stanzas = [
            HalfStanza(lines=(lines[i*2], lines[i*2+1]))
            for i in range(4)
        ]
        
        return Stanza(
            half_stanzas=half_stanzas,
            form=form.name(),
            topic=config.topic,
            domain=domain
        )
    
    def _pick_domain(self) -> str:
        """Pick a random domain from the Nine Worlds."""
        domains = [d for d in self.lexicon.words.keys() if d != "connectors"]
        return self._rng.choice(domains) if domains else "asgard"
    
    def _pick_alliteration_group(self, domain: str) -> str:
        """Pick an alliteration group that has words in the given domain."""
        entries = self.lexicon.get_words(domain=domain)
        if not entries:
            # Fall back to any domain
            entries = self.lexicon.get_words()
        groups = set(e.alliteration_group for e in entries if e.alliteration_group)
        return self._rng.choice(list(groups)) if groups else "vowel"
    
    def _pick_unique_word(self, **kwargs) -> Optional[WordEntry]:
        """Pick a word that hasn't been used in this composition yet.
        Falls back to allowing repeats after 3 failed attempts."""
        attempts = 0
        while attempts < 10:
            word = self.lexicon.random_word(**kwargs)
            if word is None:
                return None
            if word.word.lower() not in self._used_words or attempts >= 3:
                self._used_words.add(word.word.lower())
                return word
            attempts += 1
        # Last resort: just pick any word matching criteria
        return self.lexicon.random_word(**kwargs)
    
    def _compose_alliterating_pair(self, domain: str, alliteration: str,
                                     syllable_range: Tuple[int, int],
                                     config: PoemConfig) -> Tuple[Line, Line]:
        """Compose a pair of alliterating lines.
        
        In Norse verse, lines in a pair share alliteration.
        The 'head-stave' (first stressed word of the second line)
        must alliterate with at least one stressed word in the first line.
        """
        min_syl, max_syl = syllable_range
        
        # Strategy: pick line templates that naturally alliterate
        line_type = self._rng.choice([
            "adj_noun_verb",       # Golden spear rules
            "noun_verb_adverb",    # Raven flies ever
            "noun_and_noun",      # Wolf and serpent
            "adj_noun_and_adj",   # Ancient oath and eternal
            "verb_the_noun",      # Burns the golden
            "kenning_verb",       # Wound-wand pierces
            "preposition_adj_noun",  # In the sacred hall
            "noun_verb_preposition", # Warrior fights for glory
        ])
        
        line_a = self._compose_line_by_type(
            line_type, domain, alliteration, min_syl, max_syl, config
        )
        
        # Line B: must link to line A's alliteration
        line_b = self._compose_alliterating_companion(
            line_a, domain, alliteration, min_syl, max_syl, config
        )
        
        return (line_a, line_b)
    
    def _compose_line_by_type(self, line_type: str, domain: str,
                                alliteration: str,
                                min_syl: int, max_syl: int,
                                config: PoemConfig) -> Line:
        """Compose a single line following a structural template."""
        
        # Also mix in connector domain words
        domains_to_use = [domain]
        
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            attempts += 1
            
            if line_type == "adj_noun_verb":
                line = self._template_adj_noun_verb(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "noun_verb_adverb":
                line = self._template_noun_verb_adverb(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "noun_and_noun":
                line = self._template_noun_and_noun(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "adj_noun_and_adj":
                line = self._template_adj_noun_and_adj(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "verb_the_noun":
                line = self._template_verb_the_noun(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "kenning_verb":
                line = self._template_kenning_verb(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "preposition_adj_noun":
                line = self._template_preposition_adj_noun(
                    domain, alliteration, min_syl, max_syl, config
                )
            elif line_type == "noun_verb_preposition":
                line = self._template_noun_verb_preposition(
                    domain, alliteration, min_syl, max_syl, config
                )
            else:
                line = self._template_adj_noun_verb(
                    domain, alliteration, min_syl, max_syl, config
                )
            
            if line and min_syl <= line.syllables <= max_syl:
                return line
        
        # Fallback: simple adjective + noun if templates fail
        return self._fallback_line(domain, alliteration, min_syl, max_syl)
    
    def _compose_alliterating_companion(self, partner_line: Line,
                                          domain: str, alliteration: str,
                                          min_syl: int, max_syl: int,
                                          config: PoemConfig) -> Line:
        """Compose a line that alliterates with its partner."""
        # Use same alliteration group, different words
        attempts = 0
        while attempts < 30:
            attempts += 1
            templates = [
                "adj_noun_verb", "noun_verb_adverb", "verb_the_noun",
                "noun_and_noun", "preposition_adj_noun"
            ]
            template = self._rng.choice(templates)
            line = self._compose_line_by_type(
                template, domain, alliteration,
                min_syl, max_syl, config
            )
            # Avoid repeating the same text
            if line.text != partner_line.text:
                return line
        
        return self._fallback_line(domain, alliteration, min_syl, max_syl)
    
    def _compose_full_line(self, domain: str, min_syllables: int,
                            max_syllables: int, config: PoemConfig) -> Line:
        """Compose a full line (for ljóðaháttr's third line).
        Freer structure, can be longer, carries the moral weight.
        """
        templates = [
            "adj_noun_verb_adverb",
            "verb_adj_noun_and",
            "noun_shall_verb_the_noun",
        ]
        template = self._rng.choice(templates)
        
        attempts = 0
        while attempts < 30:
            attempts += 1
            line = self._compose_line_by_type(
                template.split("_")[0] + "_" + "_".join(template.split("_")[1:]),
                domain, None,
                min_syllables, max_syllables, config
            )
            if line and min_syllables <= line.syllables <= max_syllables:
                return line
        
        # Fallback: string together a noun phrase
        return self._fallback_line(domain, None, min_syllables, max_syllables)
    
    # ─── Line Templates ───
    # Each template constructs a line from constituent word types,
    # respecting syllable counts and alliteration constraints.
    
    def _template_adj_noun_verb(self, domain, allit, min_syl, max_syl, config):
        """[adj] [noun] [verb] — e.g., 'Golden spear rules'"""
        adj = self._pick_unique_word(
            domain=domain, part_of_speech="adjective",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=1, max_syllables=3
        )
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit if adj is None else None,
            min_syllables=1, max_syllables=2
        )
        verb = self._pick_unique_word(
            domain=domain, part_of_speech="verb",
            min_syllables=1, max_syllables=2
        )
        if not adj and not noun:
            return None
        
        words = []
        total_syl = 0
        for w in [adj, noun, verb]:
            if w:
                words.append(w.word)
                total_syl += w.syllables
        
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        text = " ".join(words)
        allit_group = (adj.alliteration_group if adj else noun.alliteration_group) if (adj or noun) else "vowel"
        return Line(text=text, syllables=total_syl, alliteration_group=allit_group, domain=domain)
    
    def _template_noun_verb_adverb(self, domain, allit, min_syl, max_syl, config):
        """[noun] [verb] [adverb] — e.g., 'Raven flies ever'"""
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=1, max_syllables=2
        )
        verb = self._pick_unique_word(
            domain=domain, part_of_speech="verb",
            min_syllables=1, max_syllables=2
        )
        adverb = self._pick_unique_word(
            domain="connectors", part_of_speech="adverb",
            min_syllables=1, max_syllables=2
        )
        if not noun:
            return None
        
        words = [noun, verb, adverb]
        words = [w for w in words if w]
        total_syl = sum(w.syllables for w in words)
        
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        text = " ".join(w.word for w in words)
        return Line(text=text, syllables=total_syl, 
                    alliteration_group=noun.alliteration_group, domain=domain)
    
    def _template_noun_and_noun(self, domain, allit, min_syl, max_syl, config):
        """[noun] and [noun] — e.g., 'Wolf and serpent'"""
        noun1 = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=1, max_syllables=2
        )
        noun2 = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit,
            min_syllables=1, max_syllables=2
        )
        if not noun1 or not noun2:
            return None
        
        total_syl = noun1.syllables + 1 + noun2.syllables  # +1 for "and"
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        text = f"{noun1.word} and {noun2.word}"
        return Line(text=text, syllables=total_syl,
                    alliteration_group=noun1.alliteration_group, domain=domain)
    
    def _template_adj_noun_and_adj(self, domain, allit, min_syl, max_syl, config):
        """[adj] [noun] and [adj] — e.g., 'Ancient oath and eternal'"""
        adj1 = self._pick_unique_word(
            domain=domain, part_of_speech="adjective",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=2, max_syllables=3
        )
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            min_syllables=1, max_syllables=2
        )
        adj2 = self._pick_unique_word(
            domain=domain, part_of_speech="adjective",
            alliteration_group=allit,
            min_syllables=2, max_syllables=3
        )
        if not noun or not adj1:
            return None
        
        words = [adj1, noun]
        total_syl = adj1.syllables + noun.syllables + 1  # +1 for "and"
        if adj2:
            total_syl += adj2.syllables
            text = f"{adj1.word} {noun.word} and {adj2.word}"
        else:
            return None
        
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        return Line(text=text, syllables=total_syl,
                    alliteration_group=adj1.alliteration_group, domain=domain)
    
    def _template_verb_the_noun(self, domain, allit, min_syl, max_syl, config):
        """[verb] the [noun] — e.g., 'Burns the golden hall'"""
        verb = self._pick_unique_word(
            domain=domain, part_of_speech="verb",
            min_syllables=1, max_syllables=2
        )
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=1, max_syllables=2
        )
        if not verb or not noun:
            return None
        
        total_syl = verb.syllables + 1 + noun.syllables  # +1 for "the"
        if total_syl < min_syl:
            # Add an adjective
            adj = self._pick_unique_word(
                domain=domain, part_of_speech="adjective",
                min_syllables=1, max_syllables=2
            )
            if adj:
                total_syl += adj.syllables
                text = f"{verb.word} the {adj.word} {noun.word}"
            else:
                return None
        elif total_syl > max_syl:
            return None
        else:
            text = f"{verb.word} the {noun.word}"
        
        return Line(text=text, syllables=total_syl,
                    alliteration_group=noun.alliteration_group if noun else "vowel", domain=domain)
    
    def _template_kenning_verb(self, domain, allit, min_syl, max_syl, config):
        """[kenning] [verb] — e.g., 'Wound-wand pierces'"""
        if not config.use_kennings:
            return None
        
        kenning = self.lexicon.random_kenning(
            domain=domain
        )
        if not kenning:
            return None
        
        verb = self._pick_unique_word(
            domain=domain, part_of_speech="verb",
            min_syllables=1, max_syllables=2
        )
        if not verb:
            return None
        
        total_syl = kenning.syllable_count + verb.syllables
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        text = f"{kenning.expression} {verb.word}"
        return Line(text=text, syllables=total_syl,
                    alliteration_group=allit if allit else "vowel", domain=domain)
    
    def _template_preposition_adj_noun(self, domain, allit, min_syl, max_syl, config):
        """[prep] [adj] [noun] — e.g., 'In the sacred hall'"""
        prep = self._pick_unique_word(
            domain="connectors", part_of_speech="preposition",
            min_syllables=1, max_syllables=2
        )
        adj = self._pick_unique_word(
            domain=domain, part_of_speech="adjective",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=2, max_syllables=3
        )
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            min_syllables=1, max_syllables=2
        )
        if not prep or not adj or not noun:
            return None
        
        total_syl = prep.syllables + adj.syllables + noun.syllables
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        text = f"{prep.word} {adj.word} {noun.word}"
        return Line(text=text, syllables=total_syl,
                    alliteration_group=adj.alliteration_group, domain=domain)
    
    def _template_noun_verb_preposition(self, domain, allit, min_syl, max_syl, config):
        """[noun] [verb] [prep] — e.g., 'Warrior fights for glory'"""
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit if self._rng.random() < config.alliteration_strictness else None,
            min_syllables=1, max_syllables=2
        )
        verb = self._pick_unique_word(
            domain=domain, part_of_speech="verb",
            min_syllables=1, max_syllables=2
        )
        prep = self._pick_unique_word(
            domain="connectors", part_of_speech="preposition",
            min_syllables=1, max_syllables=2
        )
        noun2 = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            min_syllables=1, max_syllables=2
        )
        if not noun or not verb:
            return None
        
        words = [noun, verb]
        total_syl = noun.syllables + verb.syllables
        if prep:
            total_syl += prep.syllables
            words.append(prep)
        if noun2:
            total_syl += noun2.syllables
            words.append(noun2)
        
        if total_syl < min_syl or total_syl > max_syl:
            return None
        
        text = " ".join(w.word for w in words)
        return Line(text=text, syllables=total_syl,
                    alliteration_group=noun.alliteration_group, domain=domain)
    
    def _fallback_line(self, domain, allit, min_syl, max_syl):
        """Last-resort line generation: just pick a noun and an adjective."""
        noun = self._pick_unique_word(
            domain=domain, part_of_speech="noun",
            alliteration_group=allit,
            min_syllables=max(1, min_syl - 2),
            max_syllables=max_syl
        )
        adj = self._pick_unique_word(
            domain=domain, part_of_speech="adjective",
            min_syllables=1, max_syllables=2
        )
        
        if not noun and not adj:
            # Truly desperate: grab any noun
            noun = self._pick_unique_word(domain=domain, part_of_speech="noun")
            if not noun:
                noun = self._pick_unique_word(part_of_speech="noun")
        
        if adj and noun:
            text = f"{adj.word} {noun.word}"
            total_syl = adj.syllables + noun.syllables
        elif noun:
            text = noun.word
            total_syl = noun.syllables
        else:
            text = "the silent void"
            total_syl = 4
        
        return Line(
            text=text, 
            syllables=total_syl,
            alliteration_group=(noun or adj).alliteration_group if (noun or adj) else "vowel",
            domain=domain
        )


@dataclass
class Poem:
    """A complete poem consisting of one or more stanzas."""
    stanzas: List[Stanza]
    config: PoemConfig
    title: Optional[str] = None
    
    def __str__(self) -> str:
        return self.format()
    
    def format(self, include_runic_header: bool = True, 
               include_form_info: bool = True,
               include_old_norse: bool = False) -> str:
        """Format the poem for display."""
        lines = []
        
        if include_runic_header:
            lines.append("᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬")
        
        if self.title:
            lines.append(f"  {self.title}")
            lines.append("")
        
        if include_form_info and self.stanzas:
            form_name = self.stanzas[0].form
            lines.append(f"  [{form_name}]")
            lines.append("")
        
        for i, stanza in enumerate(self.stanzas):
            stanza_text = str(stanza)
            lines.append(stanza_text)
            if i < len(self.stanzas) - 1:
                lines.append("")  # blank line between stanzas
        
        if include_runic_header:
            lines.append("᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬᛬")
        
        return "\n".join(lines)
    
    def format_ascii_frame(self) -> str:
        """Format the poem in an ASCII art frame like a runestone."""
        poem_lines = self.format(include_runic_header=False, include_form_info=False).split("\n")
        max_width = max(len(line) for line in poem_lines) if poem_lines else 20
        frame_width = max_width + 4
        
        top = "╔" + "═" * frame_width + "╗"
        bottom = "╚" + "═" * frame_width + "╝"
        
        framed = [top]
        framed.append("║ ᛬ " + " " * max_width + " ᛬ ║")
        
        for line in poem_lines:
            padded = line.ljust(max_width)
            framed.append(f"║ ᛬ {padded} ᛬ ║")
        
        framed.append("║ ᛬ " + " " * max_width + " ᛬ ║")
        framed.append(bottom)
        
        return "\n".join(framed)


def compose_and_print(form: str = "fornyrthislag", domain: Optional[str] = None,
                       num_stanzas: int = 1, seed: Optional[int] = None,
                       use_kennings: bool = True, framed: bool = False) -> "Poem":
    """Quick function to compose and display a poem."""
    lexicon = Lexicon(seed=seed)
    skald = Skald(lexicon=lexicon, seed=seed)
    
    config = PoemConfig(
        form=form,
        domain=domain,
        num_stanzas=num_stanzas,
        use_kennings=use_kennings,
        seed=seed
    )
    
    poem = skald.compose_poem(config)
    
    if framed:
        print(poem.format_ascii_frame())
    else:
        print(poem.format())
    
    return poem