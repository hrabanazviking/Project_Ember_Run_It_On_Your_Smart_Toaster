"""
ᚠᛟᚱᛗᛋ — Poetic Forms
The structural bones of skaldic verse

Each form is a vessel — the shape the seiðr-worker pours meaning into.
Fornyrðislag, ljóðaháttr, dróttkvætt, málaháttr:
ancient containers for ancient fire.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod


@dataclass
class Line:
    """A single line of poetry with its structural metadata."""
    text: str
    syllables: int
    alliteration_group: Optional[str] = None
    stressed_syllables: int = 0
    domain: Optional[str] = None
    
    def __str__(self) -> str:
        return self.text


@dataclass
class HalfStanza:
    """A pair of lines forming a half-stanza (vísuorð)."""
    lines: Tuple[Line, Line]
    
    @property
    def total_syllables(self) -> int:
        return sum(l.syllables for l in self.lines)
    
    def __str__(self) -> str:
        return "\n".join(str(l) for l in self.lines)


@dataclass
class Stanza:
    """A complete stanza of Norse verse."""
    half_stanzas: List[HalfStanza]
    form: str  # which poetic form
    topic: Optional[str] = None
    domain: Optional[str] = None
    full_lines: List[Line] = field(default_factory=list)  # for ljóðaháttr's full lines
    
    @property
    def lines(self) -> List[Line]:
        result = []
        for hs in self.half_stanzas:
            result.extend(hs.lines)
        result.extend(self.full_lines)
        return result
    
    def __str__(self) -> str:
        if self.form == "ljodhattr":
            return self._format_ljodhattr()
        parts = []
        for i, hs in enumerate(self.half_stanzas):
            parts.append(str(hs))
        return "\n".join(parts)
    
    def _format_ljodhattr(self) -> str:
        """Format ljóðaháttr with proper structure:
        pair + full line, then pair + full line."""
        parts = []
        hs_idx = 0
        fl_idx = 0
        # Structure: hs0, hs1 are pairs; full_lines[0] and full_lines[1] are full lines
        # Half-stanza 1
        if hs_idx < len(self.half_stanzas):
            parts.append(str(self.half_stanzas[hs_idx]))
            hs_idx += 1
        if hs_idx < len(self.half_stanzas):
            parts.append(str(self.half_stanzas[hs_idx]))
            hs_idx += 1
        if fl_idx < len(self.full_lines):
            parts.append(f"    {self.full_lines[fl_idx].text}")
            fl_idx += 1
        parts.append("")  # blank line between half-stanzas
        # Half-stanza 2
        if hs_idx < len(self.half_stanzas):
            parts.append(str(self.half_stanzas[hs_idx]))
            hs_idx += 1
        if hs_idx < len(self.half_stanzas):
            parts.append(str(self.half_stanzas[hs_idx]))
            hs_idx += 1
        if fl_idx < len(self.full_lines):
            parts.append(f"    {self.full_lines[fl_idx].text}")
            fl_idx += 1
        return "\n".join(parts)
    

class PoeticForm(ABC):
    """Base class for Old Norse poetic forms.
    
    Each form defines the structural rules that govern
    syllable count, alliteration patterns, and stanza shape.
    """
    
    @abstractmethod
    def name(self) -> str:
        """The name of this poetic form."""
        pass
    
    @abstractmethod
    def name_on(self) -> str:
        """The Old Norse name of this form."""
        pass
    
    @abstractmethod
    def validate_stanza(self, lines: List[Line]) -> bool:
        """Check if a set of lines conforms to this form's rules."""
        pass
    
    @abstractmethod
    def syllable_range(self) -> Tuple[int, int]:
        """Acceptable syllable count per line."""
        pass
    
    @abstractmethod
    def alliteration_pattern(self, line_position: int, half_stanza: int) -> Optional[str]:
        """What alliteration group is expected for this line position?
        None = no constraint, 'any' = must alliterate with something,
        'free' = no alliteration needed.
        """
        pass


class Fornyrthislag(PoeticForm):
    """Fornyrðislag — "Old Sayings' Meter"
    
    The oldest and simplest Eddic meter. Four-line stanzas, each line
    divided into two half-lines (vísuorð) by a caesura.
    
    Structure:
    - Two half-lines per line, each with 2-3 stressed syllables
    - Each line: 4-6 syllables typical
    - Alliteration links the half-lines:
      - First stressed syllable of the second half-line (the "head-stave")
        must alliterate with at least one stressed syllable in the first half-line
    - No rhyme required
    - Concise, lapidary, proverbial feel
    
    Example (Vǫluspá):
    Þá voru miðgarðr    mærar tregar
    (Then were Midgard's    famous groves)
    """
    
    def name(self) -> str:
        return "fornyrthislag"
    
    def name_on(self) -> str:
        return "fornyrðislag"
    
    def syllable_range(self) -> Tuple[int, int]:
        return (4, 6)
    
    def alliteration_pattern(self, line_position: int, half_stanza: int) -> Optional[str]:
        # In fornyrðislag, the two half-stanzas of each line alliterate together
        if line_position == 0:
            return "any"  # first half-line can start any alliteration
        return "any"  # must alliterate with line 0
    
    def validate_stanza(self, lines: List[Line]) -> bool:
        # Must have exactly 4 lines (2 pairs of half-lines = 2 long lines)
        if len(lines) != 4:
            return False
        
        # Lines 0-1 form one alliterating pair, lines 2-3 form another
        for pair_start in [0, 2]:
            line_a, line_b = lines[pair_start], lines[pair_start + 1]
            # At least one alliterating pair must match
            if line_a.alliteration_group and line_b.alliteration_group:
                if line_a.alliteration_group != line_b.alliteration_group:
                    # Still valid if any word in line_a alliterates with any word in line_b
                    pass  # Simplified check
            # Syllable count within range
            for l in [line_a, line_b]:
                if l.syllables < self.syllable_range()[0] or l.syllables > self.syllable_range()[1]:
                    return False
        
        return True
    
    def describe(self) -> str:
        return """ᚠ Fornyrðislag — The Old Sayings' Meter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The most ancient Eddic meter. Concise, proverbial, carved-in-stone.
Four lines per stanza, each a pair of half-lines linked by alliteration.
4-6 syllables per line. No rhyme. Just the bone-structure of the words.

Form:
  Line 1a ~~//~~ Line 1b    (alliterating pair)
  Line 2a ~~//~~ Line 2b    (alliterating pair)

Example:
  Ár var alda    þar er Ymir bygði
  Vara sandr né sær    né svalarungr"""


class Ljodahattr(PoeticForm):
    """Ljóðaháttr — "Song-Meter" or "Chant-Meter"
    
    The other major Eddic meter, used for wisdom poetry, prophecies,
    and the sayings of the hávamál. More expansive than fornyrðislag.
    
    Structure:
    - Six lines per stanza (two half-stanzas of three lines each)
    - Within each half-stanza:
      - Lines 1 and 2 are linked by alliteration (like fornyrðislag)
      - Line 3 is the "full line" — longer, with internal alliteration,
        and completes the thought
    - The full line often contains the moral or punch of the verse
    
    Example (Hávamál):
    Deyr fé,        deyja frændr,
    eyðisk land auðit,
    """
    
    def name(self) -> str:
        return "ljodhattr"
    
    def name_on(self) -> str:
        return "ljóðaháttr"
    
    def syllable_range(self) -> Tuple[int, int]:
        return (4, 6)
    
    def alliteration_pattern(self, line_position: int, half_stanza: int) -> Optional[str]:
        # Lines 0,1 alliterate; line 2 is the "full line"
        if line_position == 2:
            return "free"
        return "any"
    
    def validate_stanza(self, lines: List[Line]) -> bool:
        if len(lines) != 6:
            return False
        # Check syllable ranges
        for l in lines:
            if l.syllables < self.syllable_range()[0] - 1:
                return False
            if l.syllables > self.syllable_range()[1] + 2:
                # The full line (positions 2, 5) can be longer
                return False
        return True
    
    def describe(self) -> str:
        return """ᛚ Ljóðaháttr — The Song-Meter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The meter of the Hávamál — wisdom poetry, prophetic verse, gnomic sayings.
Six lines: two half-stanzas of three lines each. The third line of each
half-stanza is the "full line" — longer, freer, carrying the moral weight.

Form:
  Line 1 ~~//~~ Line 2           (alliterating pair)
  Line 3 — full line              (completes the thought)

  Line 4 ~~//~~ Line 5           (alliterating pair)
  Line 6 — full line              (the moral lands)

Example:
  Deyr fé,        deyja frændr,
  eyðisk land auðit;
  orðd externalar    vinr vænti sás
  vin á Þrifheimi."""


class Drottkvaett(PoeticForm):
    """Dróttkvætt — "Court Meter"
    
    The most complex skaldic meter. Strict rules of alliteration AND rhyme.
    This is the form used by professional court poets — the skalds.
    
    Structure:
    - Eight-line stanzas (four couplets of two half-lines each)
    - Each half-line: 6 syllables
    - Each couplet:
      - Line 1 (odd line): 2 syllables alliterate, 2 internal rhymes (skothending)
      - Line 2 (even line): 1st syllable alliterates with odd line, 
        2 syllables rhyme with odd line's rhymes (adalhending)
    - Skothending: half-rhyme (consonants match, vowels differ)
    - Adalhending: full rhyme (vowels and consonants match)
    
    This is the Olympic-level meter. If we can generate dróttkvætt,
    we can generate anything.
    """
    
    def name(self) -> str:
        return "drottkvaett"
    
    def name_on(self) -> str:
        return "dróttkvætt"
    
    def syllable_range(self) -> Tuple[int, int]:
        return (5, 7)  # 6 ideal, allow slight wiggle
    
    def alliteration_pattern(self, line_position: int, half_stanza: int) -> Optional[str]:
        # All lines alliterate
        return "any"
    
    def validate_stanza(self, lines: List[Line]) -> bool:
        if len(lines) != 8:
            return False
        # All lines should be close to 6 syllables
        for l in lines:
            if l.syllables < 5 or l.syllables > 7:
                return False
        return True
    
    def describe(self) -> str:
        return """ᛞ Dróttkvætt — The Court Meter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The most demanding skaldic meter. Eight lines, strict syllable count,
mandatory alliteration AND internal rhyme. This is where skalds prove
their craft. 

Each couplet:
  Odd line:  6 syllables, 2 alliterating stresses + skothending (half-rhyme)
  Even line: 6 syllables, 1st stressed syllable alliterates + aðalhending (full rhyme)

ᛖᛖᛖ The Olympic tier of Norse verse. ᛖᛖᛖ"""


class Malahattr(PoeticForm):
    """Málaháttr — "Speech-Meter"
    
    A variant of dróttkvætt with an extra syllable per line (5 instead of 4
    in the original Norse, so ~7 in English). More relaxed than dróttkvætt,
    but still demanding. Used for narrative verse.
    """
    
    def name(self) -> str:
        return "malahattr"
    
    def name_on(self) -> str:
        return "málaháttr"
    
    def syllable_range(self) -> Tuple[int, int]:
        return (5, 8)
    
    def alliteration_pattern(self, line_position: int, half_stanza: int) -> Optional[str]:
        return "any"
    
    def validate_stanza(self, lines: List[Line]) -> bool:
        if len(lines) != 8:
            return False
        for l in lines:
            if l.syllables < 5 or l.syllables > 8:
                return False
        return True
    
    def describe(self) -> str:
        return """ᛗ Málaháttr — The Speech-Meter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A narrative variant of dróttkvætt with an extra syllable per line.
More room to breathe, still demands alliteration.
The meter of sagas told in verse."""


# Registry of all available forms
FORMS = {
    "fornyrthislag": Fornyrthislag(),
    "fornyrdislag": Fornyrthislag(),  # alternate spelling
    "ljodhattr": Ljodahattr(),
    "ljodahattr": Ljodahattr(),
    "drottkvaett": Drottkvaett(),
    "malahattr": Malahattr(),
}


def get_form(name: str) -> PoeticForm:
    """Retrieve a poetic form by name."""
    name_lower = name.lower().strip()
    if name_lower in FORMS:
        return FORMS[name_lower]
    raise ValueError(f"Unknown poetic form: {name}. Available: {list(FORMS.keys())}")