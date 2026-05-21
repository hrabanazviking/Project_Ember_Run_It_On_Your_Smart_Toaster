"""
ᛚᛖᛪᛁᚲᛟᚾ — The Lexicon
Vocabulary domains organized as the Nine Worlds of Yggdrasil

Each domain holds words that resonate with its world's nature.
The seiðr-worker draws from these pools to weave verse.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class WordEntry:
    """A single word in the lexicon with its metrical and semantic properties."""
    word: str
    syllables: int
    stress_pattern: Tuple[int, ...]  # 1 = stressed, 0 = unstressed
    alliteration_group: str  # first consonant or vowel group
    domain: str
    part_of_speech: str  # noun, adjective, verb, adverb
    kennings: List[str] = field(default_factory=list)  # known kennings this word appears in
    old_norse: Optional[str] = None  # original Old Norse form
    
    @property
    def is_stressed_initial(self) -> bool:
        """Whether this word has initial stress (Germanic/default pattern)."""
        return self.stress_pattern[0] == 1 if self.stress_pattern else True
    
    @property
    def alliteration_letter(self) -> str:
        """The letter group this word alliterates with."""
        return self.alliteration_group[0] if self.alliteration_group else self.word[0]


@dataclass  
class Kenning:
    """A Norse kenning — a poetic circumlocution."""
    base: str  # the thing described (e.g., "sword")
    expression: str  # the kenning phrase (e.g., "wound-wand")
    components: List[str]  # words that make up the kenning
    domain: str  # thematic domain
    
    @property
    def syllable_count(self) -> int:
        """Rough syllable count for the kenning."""
        # Hyphenated kennings: count components
        return sum(count_syllables_approx(w) for w in self.components)


def count_syllables_approx(word: str) -> int:
    """Rough syllable counter for English words.
    A skald's approximation — not perfect, but enough for meter weaving.
    """
    word = word.lower().strip()
    if not word:
        return 0
    
    vowels = "aeiouy"
    syllable_count = 0
    prev_was_vowel = False
    
    for i, ch in enumerate(word):
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel
    
    # Silent terminal 'e'
    if word.endswith('e') and not word.endswith('le') and syllable_count > 1:
        syllable_count -= 1
    
    # 'le' at end when preceded by consonant adds a syllable
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        syllable_count = max(syllable_count, 1)
    
    # Every word has at least one syllable
    return max(1, syllable_count)


def stress_pattern(word: str, syllables: int) -> Tuple[int, ...]:
    """Generate a Germanic stress pattern for a word.
    Primary stress on first syllable, secondary on alternating syllables after.
    """
    if syllables <= 1:
        return (1,)
    pattern = [1] + [0] * (syllables - 1)
    # Secondary stress on odd syllables after the first
    for i in range(2, syllables, 2):
        pattern[i] = 1
    return tuple(pattern)


def alliteration_group(word: str) -> str:
    """Determine the alliteration group for a word.
    In Old Norse alliteration:
    - Vowels alliterate with vowels
    - Consonant groups: sk, sp, st alliterate as a group
    - Other consonants alliterate by their first letter
    """
    w = word.lower().strip()
    if not w:
        return ""
    
    # Vowel-initial
    if w[0] in "aeiouyæåø":
        return "vowel"
    
    # Consonant clusters that alliterate as groups
    clusters = {"sk": "sk", "sp": "sp", "st": "st"}
    for cluster, group in clusters.items():
        if w.startswith(cluster):
            return group
    
    # Single consonant
    return w[0]


class Lexicon:
    """The collective vocabulary of the seiðr-worker, organized by domain.
    
    Each domain corresponds to one of the Nine Worlds, and words
    within carry the resonance of their home world.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.words: Dict[str, List[WordEntry]] = {}
        self.kennings: List[Kenning] = []
        self._rng = random.Random(seed)
        self._load_base_vocabulary()
    
    def _add_word(self, word: str, syllables: int, domain: str, 
                  part_of_speech: str, old_norse: Optional[str] = None,
                  kennings: Optional[List[str]] = None):
        """Add a word to the lexicon."""
        entry = WordEntry(
            word=word,
            syllables=syllables,
            stress_pattern=stress_pattern(word, syllables),
            alliteration_group=alliteration_group(word),
            domain=domain,
            part_of_speech=part_of_speech,
            kennings=kennings or [],
            old_norse=old_norse
        )
        if domain not in self.words:
            self.words[domain] = []
        self.words[domain].append(entry)
    
    def _add_kenning(self, base: str, expression: str, domain: str, components: List[str]):
        """Add a kenning to the lexicon."""
        kenning = Kenning(
            base=base,
            expression=expression,
            components=components,
            domain=domain
        )
        self.kennings.append(kenning)
    
    def get_words(self, domain: Optional[str] = None, 
                  part_of_speech: Optional[str] = None,
                  syllables: Optional[int] = None,
                  alliteration_group: Optional[str] = None,
                  min_syllables: Optional[int] = None,
                  max_syllables: Optional[int] = None) -> List[WordEntry]:
        """Query words from the lexicon with filters."""
        results = []
        domains = [domain] if domain else list(self.words.keys())
        
        for d in domains:
            if d not in self.words:
                continue
            for entry in self.words[d]:
                if part_of_speech and entry.part_of_speech != part_of_speech:
                    continue
                if syllables and entry.syllables != syllables:
                    continue
                if min_syllables and entry.syllables < min_syllables:
                    continue
                if max_syllables and entry.syllables > max_syllables:
                    continue
                if alliteration_group and entry.alliteration_group != alliteration_group:
                    continue
                results.append(entry)
        return results
    
    def random_word(self, domain: Optional[str] = None,
                    part_of_speech: Optional[str] = None,
                    syllables: Optional[int] = None,
                    alliteration_group: Optional[str] = None,
                    min_syllables: Optional[int] = None,
                    max_syllables: Optional[int] = None) -> Optional[WordEntry]:
        """Pick a random word matching the given criteria."""
        pool = self.get_words(
            domain=domain,
            part_of_speech=part_of_speech,
            syllables=syllables,
            alliteration_group=alliteration_group,
            min_syllables=min_syllables,
            max_syllables=max_syllables
        )
        return self._rng.choice(pool) if pool else None
    
    def random_kenning(self, domain: Optional[str] = None,
                       base: Optional[str] = None) -> Optional[Kenning]:
        """Pick a random kenning matching the criteria."""
        pool = self.kennings
        if domain:
            pool = [k for k in pool if k.domain == domain]
        if base:
            pool = [k for k in pool if k.base == base]
        return self._rng.choice(pool) if pool else None
    
    def _load_base_vocabulary(self):
        """Load the foundational vocabulary of the seiðr-worker.
        
        Words drawn from Old Norse poetry, saga literature,
        and the landscapes of the North.
        """
        self._load_asgard()
        self._load_vanaheim()
        self._load_alfheim()
        self._load_midgard()
        self._load_jotunheim()
        self._load_svartalfheim()
        self._load_niflheim()
        self._load_muspelheim()
        self._load_helheim()
        self._load_connectors()
        self._load_kennings()
    
    def _load_asgard(self):
        """Asgard — realm of the Æsir: sovereignty, war, runes, fate, honor."""
        d = "asgard"
        
        # Gods and divine beings
        self._add_word("Odin", 2, d, "noun", "Óðinn")
        self._add_word("Thor", 1, d, "noun", "Þórr")
        self._add_word("Tyr", 1, d, "noun", "Týr")
        self._add_word("Bragi", 2, d, "noun", "Bragi")
        self._add_word("Frigg", 1, d, "noun", "Frigg")
        self._add_word("Heimdall", 2, d, "noun", "Heimdallr")
        self._add_word("Valkyrie", 3, d, "noun", "Valkyrja")
        self._add_word("Einherjar", 3, d, "noun", "Einherjar")
        self._add_word("Valhalla", 3, d, "noun", "Valhöll")
        
        # Concepts of sovereignty
        self._add_word("throne", 1, d, "noun", "hásæti")
        self._add_word("crown", 1, d, "noun", "krúna")
        self._add_word("spear", 1, d, "noun", "geirr")
        self._add_word("raven", 2, d, "noun", "hrafn")
        self._add_word("eagle", 2, d, "noun", "örn")
        self._add_word("wisdom", 2, d, "noun", "speki")
        self._add_word("rune", 1, d, "noun", "rún")
        self._add_word("rune-stave", 2, d, "noun", "rúnakefli")
        self._add_word("sacrifice", 3, d, "noun", "blót")
        self._add_word("oath", 1, d, "noun", "eiðr")
        self._add_word("law", 1, d, "noun", "lǫg")
        self._add_word("judgment", 2, d, "noun", "dómr")
        self._add_word("fate", 1, d, "noun", "ørlǫg")
        self._add_word("wyrd", 1, d, "noun", "Urðr")
        self._add_word("honor", 2, d, "noun", "sómi")
        self._add_word("glory", 2, d, "noun", "dýrð")
        self._add_word("battle", 2, d, "noun", "orrusta")
        
        # Verbs
        self._add_word("rule", 1, d, "verb", "stýra")
        self._add_word("judge", 1, d, "verb", "dæma")
        self._add_word("swear", 1, d, "verb", "sverja")
        self._add_word("conquer", 2, d, "verb", "sigra")
        self._add_word("sacrifice", 3, d, "verb", "blóta")
        self._add_word("counsel", 2, d, "verb", "ráða")
        self._add_word("foresee", 2, d, "verb", "sjá fyrir")
        self._add_word("weave", 1, d, "verb", "vefa")
        
        # Adjectives
        self._add_word("golden", 2, d, "adjective", "gullinn")
        self._add_word("sacred", 2, d, "adjective", "heilagr")
        self._add_word("ancient", 2, d, "adjective", "forn")
        self._add_word("sovereign", 3, d, "adjective", "valdandi")
        self._add_word("holy", 2, d, "adjective", "helg")
        self._add_word("wise", 1, d, "adjective", "fróðr")
        self._add_word("fearless", 2, d, "adjective", "ótta")
        self._add_word("eternal", 3, d, "adjective", "æeiligr")
    
    def _load_vanaheim(self):
        """Vanaheim — realm of the Vanir: fertility, magic, nature, seafaring."""
        d = "vanaheim"
        
        self._add_word("Freyja", 2, d, "noun", "Freyja")
        self._add_word("Freyr", 1, d, "noun", "Freyr")
        self._add_word("Njord", 1, d, "noun", "Njǫrðr")
        self._add_word("seidr", 2, d, "noun", "seiðr")
        self._add_word("spell", 1, d, "noun", "galdr")
        self._add_word("charm", 1, d, "noun", "seiðskapr")
        self._add_word("falcon", 2, d, "noun", "valr")
        self._add_word("feather", 2, d, "noun", "fjǫðr")
        self._add_word("necklace", 2, d, "noun", "men")
        self._add_word("amber", 2, d, "noun", "raf")
        self._add_word("harvest", 2, d, "noun", "uppskeran")
        self._add_word("fertility", 4, d, "noun", "auðna")
        self._add_word("prosperity", 4, d, "noun", "auðr")
        self._add_word("feast", 1, d, "noun", "veizla")
        self._add_word("longship", 2, d, "noun", "langskip")
        self._add_word("wave", 1, d, "noun", "alda")
        self._add_word("tide", 1, d, "noun", "flóð")
        self._add_word("wind", 1, d, "noun", "vindr")
        self._add_word("shore", 1, d, "noun", "strǫnd")
        self._add_word("ritual", 3, d, "noun", "blót")
        
        # Verbs
        self._add_word("sing", 1, d, "verb", "syngja")
        self._add_word("enchant", 2, d, "verb", "galdra")
        self._add_word("grow", 1, d, "verb", "vaxa")
        self._add_word("bloom", 1, d, "verb", "blómga")
        self._add_word("sail", 1, d, "verb", "sigla")
        self._add_word("celebrate", 3, d, "verb", "fagna")
        self._add_word("heal", 1, d, "verb", "lækna")
        self._add_word("dance", 1, d, "verb", "dansa")
        
        # Adjectives
        self._add_word("abundant", 3, d, "adjective", "auðigr")
        self._add_word("lush", 1, d, "adjective", "grænn")
        self._add_word("golden", 2, d, "adjective", "gullinn")
        self._add_word("fragrant", 2, d, "adjective", "ilmandi")
        self._add_word("fertile", 2, d, "adjective", "auðkent")
        self._add_word("bejeweled", 3, d, "adjective", "skrýddur")
    
    def _load_alfheim(self):
        """Alfheim — realm of the Light Elves: beauty, light, art."""
        d = "alfheim"
        
        self._add_word("star", 1, d, "noun", "stjarna")
        self._add_word("light", 1, d, "noun", "ljós")
        self._add_word("dawn", 1, d, "noun", "dagan")
        self._add_word("twilight", 2, d, "noun", "rjúgandi")
        self._add_word("beauty", 2, d, "noun", "fegrð")
        self._add_word("song", 1, d, "noun", "sǫngr")
        self._add_word("melody", 3, d, "noun", "lag")
        self._add_word("art", 1, d, "noun", "íþrótt")
        self._add_word("weaving", 2, d, "noun", "vefnaðr")
        self._add_word("silver", 2, d, "noun", "silfr")
        self._add_word("pearl", 1, d, "noun", "perla")
        self._add_word("crystal", 2, d, "noun", "bergkristall")
        self._add_word("dew", 1, d, "noun", "dögg")
        self._add_word("moonbeam", 2, d, "noun", "máni geisli")
        self._add_word("aurora", 3, d, "noun", "norðrljós")
        
        # Verbs
        self._add_word("shine", 1, d, "verb", "ljóma")
        self._add_word("gleam", 1, d, "verb", "birta")
        self._add_word("illumine", 3, d, "verb", "lýsa")
        self._add_word("dance", 1, d, "verb", "dansa")
        self._add_word("craft", 1, d, "verb", "smíða")
        self._add_word("adorn", 2, d, "verb", "skreyta")
        
        # Adjectives
        self._add_word("luminous", 3, d, "adjective", "ljómandi")
        self._add_word("ethereal", 3, d, "adjective", "lofandi")
        self._add_word("radiant", 2, d, "adjective", "geislóttur")
        self._add_word("graceful", 2, d, "adjective", "fagur")
        self._add_word("shimmering", 3, d, "adjective", "glitrandi")
        self._add_word("delicate", 3, d, "adjective", "bragðvottur")
    
    def _load_midgard(self):
        """Midgard — realm of humans: struggle, love, community, labor."""
        d = "midgard"
        
        self._add_word("home", 1, d, "noun", "heim")
        self._add_word("hearth", 1, d, "noun", "eldhús")
        self._add_word("hall", 1, d, "noun", "höll")
        self._add_word("field", 1, d, "noun", "akr")
        self._add_word("plow", 1, d, "noun", "arl")
        self._add_word("hammer", 2, d, "noun", "hamarr")
        self._add_word("anvil", 2, d, "noun", "stði")
        self._add_word("forge", 1, d, "noun", "smiðja")
        self._add_word("bread", 1, d, "noun", "brauð")
        self._add_word("ale", 1, d, "noun", "ǫl")
        self._add_word("mead", 1, d, "noun", "mjöðr")
        self._add_word("love", 1, d, "noun", "ást")
        self._add_word("kin", 1, d, "noun", "frændr")
        self._add_word("friend", 1, d, "noun", "vinr")
        self._add_word("child", 1, d, "noun", "barn")
        self._add_word("mother", 2, d, "noun", "móðir")
        self._add_word("father", 2, d, "noun", "faðir")
        self._add_word("warrior", 3, d, "noun", "þegn")
        self._add_word("skald", 1, d, "noun", "skáld")
        self._add_word("ship", 1, d, "noun", "skip")
        self._add_word("shield", 1, d, "noun", "skjǫldr")
        self._add_word("sword", 1, d, "noun", "sverð")
        self._add_word("mountain", 2, d, "noun", "fjall")
        self._add_word("river", 2, d, "noun", "á")
        self._add_word("valley", 2, d, "noun", "dalr")
        self._add_word("winter", 2, d, "noun", "vetr")
        self._add_word("summer", 2, d, "noun", "sumar")
        self._add_word("storm", 1, d, "noun", "stormr")
        
        # Verbs
        self._add_word("work", 1, d, "verb", "vinna")
        self._add_word("build", 1, d, "verb", "byggja")
        self._add_word("love", 1, d, "verb", "elska")
        self._add_word("fight", 1, d, "verb", "berjask")
        self._add_word("journey", 2, d, "verb", "fara")
        self._add_word("remember", 3, d, "verb", "muna")
        self._add_word("protect", 2, d, "verb", "verja")
        self._add_word("laugh", 1, d, "verb", "hlæja")
        self._add_word("weep", 1, d, "verb", "gráta")
        self._add_word("sing", 1, d, "verb", "syngja")
        self._add_word("feast", 1, d, "verb", "bera risk")
        
        # Adjectives
        self._add_word("strong", 1, d, "adjective", "sterkr")
        self._add_word("brave", 1, d, "adjective", "hugrakkur")
        self._add_word("weathered", 2, d, "adjective", "veðradur")
        self._add_word("warm", 1, d, "adjective", "hlár")
        self._add_word("steadfast", 2, d, "adjective", "stöðugur")
        self._add_word("mortal", 2, d, "adjective", "dauðlegur")
    
    def _load_jotunheim(self):
        """Jotunheim — realm of giants: chaos, wildness, primal forces."""
        d = "jotunheim"
        
        self._add_word("giant", 2, d, "noun", "jǫtunn")
        self._add_word("frost", 1, d, "noun", "frost")
        self._add_word("ice", 1, d, "noun", "íss")
        self._add_word("storm", 1, d, "noun", "stormr")
        self._add_word("thunder", 2, d, "noun", "þruma")
        self._add_word("lightning", 2, d, "noun", "eldingar")
        self._add_word("mountain", 2, d, "noun", "fjall")
        self._add_word("boulder", 2, d, "noun", "steinn")
        self._add_word("wolf", 1, d, "noun", "úlfr")
        self._add_word("serpent", 2, d, "noun", "ormr")
        self._add_word("chaos", 2, d, "noun", " skaði")
        self._add_word("rage", 1, d, "noun", "reiði")
        self._add_word("darkness", 2, d, "noun", "myrkr")
        self._add_word("shadow", 2, d, "noun", "skuggi")
        self._add_word("void", 1, d, "noun", "ginungagap")
        self._add_word("fang", 1, d, "noun", "tǫnn")
        self._add_word("claw", 1, d, "noun", "klær")
        
        # Verbs
        self._add_word("crush", 1, d, "verb", "krossa")
        self._add_word("roar", 1, d, "verb", "rjóða")
        self._add_word("devour", 2, d, "verb", "éta")
        self._add_word("shatter", 2, d, "verb", "brjóta")
        self._add_word("freeze", 1, d, "verb", "frjósa")
        self._add_word("rage", 1, d, "verb", "reiðast")
        self._add_word("howl", 1, d, "verb", "hįla")
        self._add_word("devour", 2, d, "verb", "gleypa")
        
        # Adjectives
        self._add_word("massive", 2, d, "adjective", "risastór")
        self._add_word("frozen", 2, d, "adjective", "frosinn")
        self._add_word("feral", 2, d, "adjective", "villaður")
        self._add_word("relentless", 3, d, "adjective", "óstöðvandi")
        self._add_word("primal", 2, d, "adjective", "upphafslegur")
        self._add_word("savage", 2, d, "adjective", "grimmur")
    
    def _load_svartalfheim(self):
        """Svartalfheim — realm of dwarves: craft, earth, dark metals."""
        d = "svartalfheim"
        
        self._add_word("dwarf", 1, d, "noun", "dvergr")
        self._add_word("forge", 1, d, "noun", "smiðja")
        self._add_word("anvil", 2, d, "noun", "stði")
        self._add_word("mithril", 2, d, "noun", "míðrill")
        self._add_word("iron", 2, d, "noun", "járn")
        self._add_word("gold", 1, d, "noun", "gull")
        self._add_word("steel", 1, d, "noun", "stál")
        self._add_word("gem", 1, d, "noun", "nýtimenni")
        self._add_word("ring", 1, d, "noun", "hringr")
        self._add_word("treasure", 2, d, "noun", "skatt")
        self._add_word("cave", 1, d, "noun", "hellir")
        self._add_word("depth", 1, d, "noun", "dýpt")
        self._add_word("craft", 1, d, "noun", "íþrótt")
        self._add_word("chain", 1, d, "noun", "fjöturr")
        self._add_word("net", 1, d, "noun", "net")
        
        # Verbs
        self._add_word("forge", 1, d, "verb", "smíða")
        self._add_word("craft", 1, d, "verb", "skapa")
        self._add_word("dig", 1, d, "verb", "grafva")
        self._add_word("melt", 1, d, "verb", "bræða")
        self._add_word("shape", 1, d, "verb", "mynda")
        self._add_word("temper", 2, d, "verb", "herða")
        
        # Adjectives
        self._add_word("deep", 1, d, "adjective", "djúpur")
        self._add_word("heavy", 2, d, "adjective", "þungur")
        self._add_word("gleaming", 2, d, "adjective", "blöndóttr")
        self._add_word("unbreakable", 4, d, "adjective", "óbrotnottr")
        self._add_word("masterwork", 3, d, "adjective", "meistara")
    
    def _load_niflheim(self):
        """Niflheim — realm of mist: primordial cold, origins, obscurity."""
        d = "niflheim"
        
        self._add_word("mist", 1, d, "noun", "þoka")
        self._add_word("fog", 1, d, "noun", "þoka")
        self._add_word("frost", 1, d, "noun", "frost")
        self._add_word("ice", 1, d, "noun", "íss")
        self._add_word("rime", 1, d, "noun", "hríma")
        self._add_word("void", 1, d, "noun", "gap")
        self._add_word("silence", 2, d, "noun", "þag")
        self._add_word("origin", 3, d, "noun", "upphaf")
        self._add_word("well", 1, d, "noun", "brunnr")
        self._add_word("spring", 1, d, "noun", "lind")
        self._add_word("cold", 1, d, "noun", "kuldi")
        self._add_word("depth", 1, d, "noun", "dýpt")
        self._add_word("shadow", 2, d, "noun", "skuggi")
        self._add_word("veil", 1, d, "noun", "slæða")
        
        # Verbs
        self._add_word("obscure", 2, d, "verb", "dylgja")
        self._add_word("conceal", 2, d, "verb", "fela")
        self._add_word("freeze", 1, d, "verb", "frjósa")
        self._add_word("emanate", 3, d, "verb", "koma fram")
        self._add_word("dissolve", 2, d, "verb", "leysast")
        self._add_word("congeal", 2, d, "verb", "storkna")
        
        # Adjectives
        self._add_word("primordial", 4, d, "adjective", "frumheimskr")
        self._add_word("obscure", 2, d, "adjective", "dulur")
        self._add_word("frigid", 2, d, "adjective", "köldur")
        self._add_word("ancient", 2, d, "adjective", "forn")
        self._add_word("silent", 2, d, "adjective", "þagandi")
    
    def _load_muspelheim(self):
        """Muspelheim — realm of fire: creation, destruction, transformation."""
        d = "muspelheim"
        
        self._add_word("fire", 1, d, "noun", "eldr")
        self._add_word("flame", 1, d, "noun", "logi")
        self._add_word("ember", 2, d, "noun", "glóð")
        self._add_word("ash", 1, d, "noun", "aska")
        self._add_word("spark", 1, d, "noun", "gneisti")
        self._add_word("surtr", 1, d, "noun", "Surtr")
        self._add_word("blade", 1, d, "noun", "blað")
        self._add_word("ruin", 2, d, "noun", " eyðileging")
        self._add_word("transformation", 4, d, "noun", "umbreyting")
        self._add_word("sun", 1, d, "noun", "sól")
        self._add_word("burn", 1, d, "noun", "brennsla")
        self._add_word("heat", 1, d, "noun", "hiti")
        
        # Verbs
        self._add_word("burn", 1, d, "verb", "brenna")
        self._add_word("scorch", 1, d, "verb", "sviða")
        self._add_word("ignite", 2, d, "verb", "kveikja")
        self._add_word("consume", 2, d, "verb", "neyða")
        self._add_word("transform", 2, d, "verb", "umbreyta")
        self._add_word("purify", 3, d, "verb", "hreinsa")
        self._add_word("forge", 1, d, "verb", "smíða")
        
        # Adjectives
        self._add_word("blazing", 2, d, "adjective", "blandandi")
        self._add_word("searing", 2, d, "adjective", "sviðandi")
        self._add_word("molten", 2, d, "adjective", "bráðinn")
        self._add_word("dying", 2, d, "adjective", "dauðandi")
        self._add_word("reborn", 2, d, "adjective", "endurfæddur")
    
    def _load_helheim(self):
        """Helheim — realm of the dead: endings, memory, the inevitable."""
        d = "helheim"
        
        self._add_word("death", 1, d, "noun", "dauði")
        self._add_word("grave", 1, d, "noun", "gröf")
        self._add_word("mist", 1, d, "noun", "þoka")
        self._add_word("ghost", 1, d, "noun", "draugr")
        self._add_word("memory", 3, d, "noun", "minni")
        self._add_word("grief", 1, d, "noun", "sorg")
        self._add_word("silence", 2, d, "noun", "þag")
        self._add_word("end", 1, d, "noun", "endir")
        self._add_word("passage", 2, d, "noun", "leið")
        self._add_word("dust", 1, d, "noun", "ryk")
        self._add_word("bone", 1, d, "noun", "bein")
        self._add_word("threshold", 2, d, "noun", "þröskuldur")
        self._add_word("Hel", 1, d, "noun", "Hel")
        self._add_word("Garmr", 2, d, "noun", "Garmr")
        
        # Verbs
        self._add_word("remember", 3, d, "verb", "muna")
        self._add_word("mourn", 1, d, "verb", "sorga")
        self._add_word("fade", 1, d, "verb", "fades")
        self._add_word("wither", 2, d, "verb", "þróna")
        self._add_word("release", 2, d, "verb", "gefa laust")
        self._add_word("pass", 1, d, "verb", "fara")
        self._add_word("linger", 2, d, "verb", "dvelja")
        self._add_word("forget", 2, d, "verb", "gleyma")
        
        # Adjectives
        self._add_word("hollow", 2, d, "adjective", "hólgur")
        self._add_word("pale", 1, d, "adjective", "fölur")
        self._add_word("eternal", 3, d, "adjective", "eilíffur")
        self._add_word("inevitable", 4, d, "adjective", "óhjákvæmilegur")
        self._add_word("forgotten", 3, d, "adjective", "gleymdur")
        self._add_word("still", 1, d, "adjective", "kyrr")
    
    def _load_connectors(self):
        """Structural words — the thread that stitches verse together.
        These belong to no single world but weave between them."""
        d = "connectors"
        
        # Pronouns
        self._add_word("I", 1, d, "pronoun")
        self._add_word("you", 1, d, "pronoun")
        self._add_word("we", 1, d, "pronoun")
        self._add_word("they", 1, d, "pronoun")
        self._add_word("she", 1, d, "pronoun")
        self._add_word("he", 1, d, "pronoun")
        self._add_word("who", 1, d, "pronoun")
        
        # Articles
        self._add_word("the", 1, d, "article")
        self._add_word("a", 1, d, "article")
        
        # Prepositions
        self._add_word("in", 1, d, "preposition")
        self._add_word("on", 1, d, "preposition")
        self._add_word("of", 1, d, "preposition")
        self._add_word("from", 1, d, "preposition")
        self._add_word("to", 1, d, "preposition")
        self._add_word("by", 1, d, "preposition")
        self._add_word("with", 1, d, "preposition")
        self._add_word("under", 2, d, "preposition")
        self._add_word("over", 2, d, "preposition")
        self._add_word("through", 1, d, "preposition")
        self._add_word("upon", 2, d, "preposition")
        self._add_word("across", 2, d, "preposition")
        self._add_word("between", 2, d, "preposition")
        self._add_word("beyond", 2, d, "preposition")
        
        # Conjunctions
        self._add_word("and", 1, d, "conjunction")
        self._add_word("but", 1, d, "conjunction")
        self._add_word("nor", 1, d, "conjunction")
        self._add_word("for", 1, d, "conjunction")
        self._add_word("when", 1, d, "conjunction")
        self._add_word("while", 1, d, "conjunction")
        self._add_word("though", 1, d, "conjunction")
        self._add_word("yet", 1, d, "conjunction")
        
        # Adverbs
        self._add_word("now", 1, d, "adverb")
        self._add_word("then", 1, d, "adverb")
        self._add_word("here", 1, d, "adverb")
        self._add_word("there", 1, d, "adverb")
        self._add_word("ever", 2, d, "adverb")
        self._add_word("never", 2, d, "adverb")
        self._add_word("always", 2, d, "adverb")
        self._add_word("again", 2, d, "adverb")
        self._add_word("long", 1, d, "adverb")
        self._add_word("still", 1, d, "adverb")
        self._add_word("far", 1, d, "adverb")
        self._add_word("near", 1, d, "adverb")
        self._add_word("yet", 1, d, "adverb")
        self._add_word("soon", 1, d, "adverb")
        
        # Auxiliary/modal verbs
        self._add_word("shall", 1, d, "auxiliary")
        self._add_word("will", 1, d, "auxiliary")
        self._add_word("may", 1, d, "auxiliary")
        self._add_word("must", 1, d, "auxiliary")
        self._add_word("was", 1, d, "auxiliary")
        self._add_word("were", 1, d, "auxiliary")
        self._add_word("is", 1, d, "auxiliary")
        self._add_word("are", 1, d, "auxiliary")
        self._add_word("has", 1, d, "auxiliary")
        self._add_word("had", 1, d, "auxiliary")
    
    def _load_kennings(self):
        """Load the treasure-hoard of Norse kennings."""
        # Battle kennings
        self._add_kenning("battle", "storm of spears", "asgard", ["storm", "spears"])
        self._add_kenning("battle", "riot of iron", "asgard", ["riot", "iron"])
        self._add_kenning("battle", "clash of shields", "asgard", ["clash", "shields"])
        self._add_kenning("sword", "wound-wand", "asgard", ["wound", "wand"])
        self._add_kenning("sword", "fire of the wound", "asgard", ["fire", "wound"])
        self._add_kenning("sword", "leaving of the blade", "asgard", ["leaving", "blade"])
        self._add_kenning("warrior", "tree of battle", "asgard", ["tree", "battle"])
        self._add_kenning("warrior", "oak of the spear-storm", "asgard", ["oak", "spear", "storm"])
        self._add_kenning("blood", "dew of wounds", "asgard", ["dew", "wounds"])
        self._add_kenning("raven", "slaughter-goose", "asgard", ["slaughter", "goose"])
        
        # Sea/Ocean kennings
        self._add_kenning("sea", "whale-road", "vanaheim", ["whale", "road"])
        self._add_kenning("sea", "ship-path", "vanaheim", ["ship", "path"])
        self._add_kenning("sea", "field of the longfish", "vanaheim", ["field", "longfish"])
        self._add_kenning("ship", "wave-rider", "vanaheim", ["wave", "rider"])
        self._add_kenning("ship", "steed of the sea-king", "vanaheim", ["steed", "sea", "king"])
        
        # Gold/Treasure kennings
        self._add_kenning("gold", "fire of the arm", "svartalfheim", ["fire", "arm"])
        self._add_kenning("gold", "tears of the sun", "alfheim", ["tears", "sun"])
        self._add_kenning("gold", "Aegir's fire", "vanaheim", ["Aegir", "fire"])
        
        # Poetry/Knowledge kennings
        self._add_kenning("poetry", "mead of Odin", "asgard", ["mead", "Odin"])
        self._add_kenning("poetry", "Kvasir's blood", "asgard", ["Kvasir", "blood"])
        self._add_kenning("mead", "Kvasir's blood", "asgard", ["Kvasir", "blood"])
        
        # Earth/Land kennings
        self._add_kenning("earth", "flesh of Ymir", "jotunheim", ["flesh", "Ymir"])
        self._add_kenning("mountains", "bones of Ymir", "jotunheim", ["bones", "Ymir"])
        self._add_kenning("sky", "skull of Ymir", "jotunheim", ["skull", "Ymir"])
        self._add_kenning("sea", "blood of Ymir", "jotunheim", ["blood", "Ymir"])
        
        # Woman/Freyja kennings
        self._add_kenning("woman", "dispenser of gold", "vanaheim", ["dispenser", "gold"])
        self._add_kenning("woman", "wearer of the costs", "vanaheim", ["wearer", "costs"])
        self._add_kenning("Freyja", "owner of the falcon-cloak", "vanaheim", ["owner", "falcon", "cloak"])