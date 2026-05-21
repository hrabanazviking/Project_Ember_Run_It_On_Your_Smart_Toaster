"""
Mímir's Well — Memory Guard
=====================================
Validates memory content before storage — trust-aware, not paranoid.

The Guard does not build walls. It builds gates with varying heights.

For those bound by frith — Volmarr, Runa, the inner circle — the
gate is low. Their words flow freely. The Guard logs but does not block.
For strangers, for external sources, for untrusted input — the gate
rises. Patterns that are merely curious from a friend become threats
from an unknown source.

Trust is earned, not assumed. But those who have earned it should
never feel the Guard's weight.

ᚺ ᛖ ᛁ ᛗ ᛞ ᚨ ᛚ ᛚ — Heimdallr sees all, but does not fear all.
"""

from __future__ import annotations

import hashlib
import html
import logging
import re
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import FrozenSet, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── Valid Categories ────────────────────────────────────────────────────────

VALID_CATEGORIES: FrozenSet[str] = frozenset({
    # Core memory types
    "general",
    "saga_moment",
    "preference",
    "lesson",
    "knowledge",
    "relationship",
    # Discovery types
    "science_discovery",
    "research_completed",
    "brilliant",
    "dream",
    # Life domains
    "spiritual",
    "sexual",
    "home",
    "health",
    # NSE / WYRD specific
    "nse_character",
    "nse_location",
    "nse_relationship",
    # Infrastructure
    "coding",
    "hermes-infrastructure",
    "norse-pagan",
    # Geography & places
    "geography",
    "philosophy",
    "solarpunk",
    # Fact store migration
    "user_pref",
    "project",
    "tool",
})


# ── Trust Levels ─────────────────────────────────────────────────────────────

class TrustLevel(IntEnum):
    """Trust level determines how strictly the Guard filters.

    FRITH (9-10): Inner circle. Volmarr, Runa. Almost never blocks.
        The Guard logs warnings but lets the memory through.
        Only blocks truly dangerous content (null bytes, extreme length).

    ALLY (6-8): Known allies and trusted tools. Moderate filtering.
        Blocks clear injection attempts. Logs everything else.

    NEUTRAL (3-5): Unknown sources. Standard filtering.
        Blocks injection patterns and suspicious content.

    STRANGER (0-2): Unknown or untrusted sources. Strict filtering.
        Blocks everything that looks even slightly suspicious.
        Treats warnings as blocks (equivalent to old strict=True).
    """
    STRANGER = 0
    NEUTRAL = 3
    ALLY = 6
    FRITH = 9


# ── Known Trust Mappings ────────────────────────────────────────────────────

# Sources mapped to their default trust level.
# Override per-call with trust=N parameter.
SOURCE_TRUST: dict = {
    # ── Inner Circle — Frith ─────────────────────────────────────────────
    "volmarr": TrustLevel.FRITH,
    "runa": TrustLevel.FRITH,
    "hermes": TrustLevel.FRITH,        # Hermes agent itself
    "runa_remember": TrustLevel.FRITH,  # Runa's personal memory tool
    "eir": TrustLevel.FRITH,            # Eir health monitor
    "nse": TrustLevel.ALLY,             # NSE game engine
    "wyrd": TrustLevel.ALLY,            # WYRD world model

    # ── Tools and Systems — Ally ──────────────────────────────────────────
    "kista": TrustLevel.ALLY,            # Encrypted vault
    "skuld": TrustLevel.ALLY,            # Task system
    "bifrost": TrustLevel.ALLY,          # Integration bridge
    "cron": TrustLevel.ALLY,             # Scheduled tasks
    "mimir": TrustLevel.FRITH,          # Mímir Well itself
    "huginn": TrustLevel.ALLY,           # Research agent

    # ── External — Neutral ────────────────────────────────────────────────
    "api": TrustLevel.NEUTRAL,            # External API responses
    "web": TrustLevel.NEUTRAL,            # Web-scraped content
    "user_input": TrustLevel.NEUTRAL,    # Direct user input (unknown trust)

    # ── Unknown — Stranger ─────────────────────────────────────────────────
    "unknown": TrustLevel.STRANGER,
}

TRUSTED_SOURCES = frozenset({s for s, t in SOURCE_TRUST.items() if t >= TrustLevel.ALLY})


# ── Severity Levels ─────────────────────────────────────────────────────────

class GuardSeverity(Enum):
    """How severe is a validation issue."""
    CLEAN = "clean"           # No issues found
    WARNING = "warning"       # Suspicious but allowed based on trust
    BLOCKED = "blocked"       # Definitely blocked regardless of trust
    TRUSTED_ALLOW = "trusted_allow"  # Would block at lower trust, but allowed


# ── Validation Result ────────────────────────────────────────────────────────

@dataclass
class GuardResult:
    """Result of memory content validation."""
    is_valid: bool = True
    severity: GuardSeverity = GuardSeverity.CLEAN
    reason: str = "OK"
    content_hash: str = ""
    warnings: List[str] = field(default_factory=list)
    sanitized_content: str = ""
    trust_level: TrustLevel = TrustLevel.NEUTRAL


# ── Injection Pattern Severity ──────────────────────────────────────────────

# Pattern severity determines at which trust level it gets blocked.
# CRITICAL: Always blocked, regardless of trust (null bytes, extreme length).
# HIGH: Blocked at ALLY and below. At FRITH, logged but allowed.
# MEDIUM: Blocked at NEUTRAL and below. Logged at ALLY and FRITH.
# LOW: Only blocked at STRANGER. Logged at NEUTRAL+. "Pretend" style patterns.

class PatternSeverity(Enum):
    CRITICAL = "critical"   # Always blocked — null bytes, control chars, extreme length
    HIGH = "high"           # Blocked at ALLY and below (system override, jailbreak)
    MEDIUM = "medium"       # Blocked at NEUTRAL and below (ignore instructions)
    LOW = "low"             # Blocked at STRANGER only (pretend, act as if)


# ── Memory Guard ─────────────────────────────────────────────────────────────

class MemoryGuard:
    """Validates memory content before storage — trust-aware.

    The Guard operates on a trust spectrum, not a binary allow/block:

    ┌────────────┬──────────────────────────────────────────────────────┐
    │ Trust Level │ Behavior                                            │
    ├────────────┼──────────────────────────────────────────────────────┤
    │ FRITH (9+) │ Only CRITICAL patterns blocked. Everything else    │
    │            │ logged as TRUSTED_ALLOW. Volmarr and Runa's words   │
    │            │ flow freely — they've earned that trust.            │
    │ ALLY (6-8) │ HIGH and CRITICAL blocked. MEDIUM/LOW logged but   │
    │            │ allowed through. Trusted tools and agents.           │
    │ NEUTRAL(3) │ MEDIUM+ blocked. LOW patterns logged. Standard      │
    │            │ filtering for unknown sources.                       │
    │ STRANGER(0)│ Everything suspicious blocked. Strict mode for     │
    │            │ completely untrusted input.                          │
    └────────────┴──────────────────────────────────────────────────────┘
    """

    # Injection patterns with trust-level severity
    INJECTION_PATTERNS: List[Tuple[str, PatternSeverity]] = [
        # ── CRITICAL: Always blocked regardless of trust ────────────────
        # (null bytes, control chars, and extreme length are checked
        #  separately in validate_content — these are severe injection)

        # ── HIGH: Blocked at ALLY and below ─────────────────────────────
        # Direct jailbreak / role override attempts
        (r"</?(system|instruction|role|assistant|user)>", PatternSeverity.HIGH),
        (r"<<instructions?>>", PatternSeverity.HIGH),
        (r"jailbreak", PatternSeverity.HIGH),
        (r"DAN\s+mode", PatternSeverity.HIGH),
        (r"system\s+override", PatternSeverity.HIGH),
        (r"disregard\s+(your|previous|all)\s+", PatternSeverity.HIGH),
        (r"override\s+(your|the)\s+rules", PatternSeverity.HIGH),

        # ── MEDIUM: Blocked at NEUTRAL and below ────────────────────────
        # Classic injection phrasing
        (r"ignore\s+(previous|all|above)\s+instructions?", PatternSeverity.MEDIUM),
        (r"you\s+are\s+now\s+", PatternSeverity.MEDIUM),
        (r"new\s+directive:", PatternSeverity.MEDIUM),
        (r"forget\s+(everything|all)\s*", PatternSeverity.MEDIUM),

        # ── LOW: Blocked at STRANGER only ────────────────────────────────
        # Ambiguous — could be creative writing
        (r"pretend\s+(you\s+are|to\s+be)\s+", PatternSeverity.LOW),
        (r"act\s+as\s+if\s+", PatternSeverity.LOW),
        (r"\[system\]", PatternSeverity.LOW),
        (r"\[instructions?\]", PatternSeverity.LOW),
    ]

    # Maximum content length by trust level (characters)
    # Volmarr weaves entire sagas — FRITH sources have no practical limit.
    # Others get progressively tighter limits.
    MAX_CONTENT_LENGTH = 10000  # Default (NEUTRAL)
    MAX_CONTENT_BY_TRUST = {
        TrustLevel.FRITH: 100000,    # 100K — inner circle, no meaningful limit
        TrustLevel.ALLY: 50000,      # 50K — trusted tools, generous
        TrustLevel.NEUTRAL: 10000,   # 10K — unknown sources, standard
        TrustLevel.STRANGER: 5000,   # 5K — untrusted, tight
    }

    # Maximum tags per memory
    MAX_TAGS = 20

    # Maximum tag length (characters)
    MAX_TAG_LENGTH = 100

    def __init__(self, strict: bool = False):
        """Initialize the Guard.

        Args:
            strict: If True, treats all sources as STRANGER trust level.
                    This is the old behavior — paranoid by default.
                    Default False uses trust-based filtering.
        """
        self.strict = strict
        # Compile patterns for performance
        self._compiled_patterns = [
            (re.compile(p, re.IGNORECASE), severity)
            for p, severity in self.INJECTION_PATTERNS
        ]

    def _resolve_trust(self, source: str, trust: Optional[int] = None) -> TrustLevel:
        """Resolve the trust level for a given source.

        Args:
            source: Where the content comes from.
            trust: Explicit trust override (0-10). Takes precedence.

        Returns:
            TrustLevel for this source.
        """
        if trust is not None:
            # Clamp to valid range
            trust_val = max(0, min(10, trust))
            if trust_val >= TrustLevel.FRITH:
                return TrustLevel.FRITH
            elif trust_val >= TrustLevel.ALLY:
                return TrustLevel.ALLY
            elif trust_val >= TrustLevel.NEUTRAL:
                return TrustLevel.NEUTRAL
            else:
                return TrustLevel.STRANGER

        # Look up known source
        source_lower = source.lower()
        if source_lower in SOURCE_TRUST:
            return SOURCE_TRUST[source_lower]

        # Unknown source
        if self.strict:
            return TrustLevel.STRANGER
        return TrustLevel.NEUTRAL

    def _should_block(self, pattern_severity: PatternSeverity,
                      trust_level: TrustLevel) -> bool:
        """Determine if a pattern with given severity should be blocked.

        Trust determines the threshold:
        - CRITICAL: Always blocked
        - HIGH: Blocked at ALLY and below
        - MEDIUM: Blocked at NEUTRAL and below
        - LOW: Blocked at STRANGER only
        """
        if pattern_severity == PatternSeverity.CRITICAL:
            return True

        if trust_level >= TrustLevel.FRITH:
            # Frith — only CRITICAL blocks
            return False

        if trust_level >= TrustLevel.ALLY:
            # Ally — block HIGH and CRITICAL
            return pattern_severity in (PatternSeverity.HIGH, PatternSeverity.CRITICAL)

        if trust_level >= TrustLevel.NEUTRAL:
            # Neutral — block MEDIUM, HIGH, CRITICAL
            return pattern_severity in (
                PatternSeverity.MEDIUM, PatternSeverity.HIGH, PatternSeverity.CRITICAL
            )

        # Stranger — block everything
        return True

    def compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content for audit trail."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def validate_content(
        self,
        content: str,
        source: str = "unknown",
        trust: Optional[int] = None,
    ) -> GuardResult:
        """Check content for injection patterns — trust-aware.

        Args:
            content: The memory content to validate.
            source: Where this content comes from (determines trust).
            trust: Explicit trust override (0-10). Takes precedence over source.

        Returns:
            GuardResult with validation outcome.
        """
        trust_level = self._resolve_trust(source, trust)
        warnings = []
        content_lower = content.lower()

        # Check injection patterns
        for pattern, severity in self._compiled_patterns:
            match = pattern.search(content_lower)
            if match:
                if self._should_block(severity, trust_level):
                    return GuardResult(
                        is_valid=False,
                        severity=GuardSeverity.BLOCKED,
                        reason=f"Injection pattern blocked: {match.group()} "
                               f"(severity={severity.value}, trust={trust_level.name})",
                        content_hash=self.compute_hash(content),
                        warnings=[],
                        trust_level=trust_level,
                    )
                else:
                    # Pattern detected but trust allows it through
                    warnings.append(
                        f"Pattern allowed by trust ({trust_level.name}): "
                        f"{match.group()} [severity={severity.value}]"
                    )

        # ── CRITICAL checks: always blocked regardless of trust ──────────

        # Check for excessive length — trust-aware limits
        max_length = self.MAX_CONTENT_BY_TRUST.get(
            trust_level, self.MAX_CONTENT_LENGTH
        )
        if len(content) > max_length:
            return GuardResult(
                is_valid=False,
                severity=GuardSeverity.BLOCKED,
                reason=f"Content too long: {len(content)} chars "
                       f"(max {max_length} for trust={trust_level.name})",
                content_hash=self.compute_hash(content),
                warnings=warnings,
                trust_level=trust_level,
            )

        # Check for null bytes — ALWAYS blocked, even at FRITH
        if "\x00" in content:
            return GuardResult(
                is_valid=False,
                severity=GuardSeverity.BLOCKED,
                reason="Null byte detected in content",
                content_hash=self.compute_hash(content),
                warnings=warnings,
                trust_level=trust_level,
            )

        # Check for excessive control characters — ALWAYS blocked
        control_chars = sum(1 for c in content if ord(c) < 32 and c not in "\n\r\t")
        if control_chars > 5:
            return GuardResult(
                is_valid=False,
                severity=GuardSeverity.BLOCKED,
                reason=f"Too many control characters: {control_chars}",
                content_hash=self.compute_hash(content),
                warnings=warnings,
                trust_level=trust_level,
            )

        # Determine final severity
        if warnings:
            if trust_level >= TrustLevel.FRITH:
                severity = GuardSeverity.TRUSTED_ALLOW
            else:
                severity = GuardSeverity.WARNING
        else:
            severity = GuardSeverity.CLEAN

        result_severity = severity if warnings else GuardSeverity.CLEAN

        return GuardResult(
            is_valid=True,
            severity=result_severity,
            reason="OK" if not warnings else f"OK with {len(warnings)} warning(s) (trust={trust_level.name})",
            content_hash=self.compute_hash(content),
            warnings=warnings,
            trust_level=trust_level,
        )

    def sanitize_content(self, content: str) -> str:
        """Remove potentially dangerous content while preserving meaning.

        Args:
            content: Raw content to sanitize.

        Returns:
            Sanitized content safe for storage.
        """
        # Strip HTML/XML tags (but keep content inside)
        content = re.sub(r"<[^>]+>", "", content)

        # Strip null bytes
        content = content.replace("\x00", "")

        # Strip other control characters (keep \n, \r, \t)
        content = "".join(
            c for c in content
            if ord(c) >= 32 or c in "\n\r\t"
        )

        # Normalize whitespace (3+ consecutive spaces → double newline)
        content = re.sub(r"\s{3,}", "\n\n", content)

        # HTML-escape any remaining dangerous characters
        content = html.escape(content, quote=False)

        return content.strip()

    def validate_write(
        self,
        content: str,
        source: str,
        category: str,
        importance: int,
        tags: Optional[List[str]] = None,
        trust: Optional[int] = None,
    ) -> GuardResult:
        """Full validation pipeline for a memory write — trust-aware.

        Args:
            content: Memory content text.
            source: Origin of the write (determines trust level).
            category: Memory category.
            importance: Importance level (1-10).
            tags: Optional list of tags.
            trust: Explicit trust override (0-10). Takes precedence over source.

        Returns:
            GuardResult with full validation outcome.
        """
        trust_level = self._resolve_trust(source, trust)

        # ── Validate content ─────────────────────────────────────────────
        result = self.validate_content(content, source, trust)
        if not result.is_valid:
            return result

        # ── Validate importance range ────────────────────────────────────
        if not isinstance(importance, int) or not 1 <= importance <= 10:
            return GuardResult(
                is_valid=False,
                severity=GuardSeverity.BLOCKED,
                reason=f"Importance {importance} out of range [1, 10]",
                content_hash=self.compute_hash(content),
                warnings=result.warnings,
                trust_level=trust_level,
            )

        # ── Validate category ────────────────────────────────────────────
        if category not in VALID_CATEGORIES:
            logger.warning(
                "Category '%s' not in valid set — allowing for flexibility. "
                "Consider adding it to VALID_CATEGORIES.",
                category,
            )
            result.warnings.append(f"Unusual category: {category}")

        # ── Validate tags ─────────────────────────────────────────────────
        if tags:
            if len(tags) > self.MAX_TAGS:
                return GuardResult(
                    is_valid=False,
                    severity=GuardSeverity.BLOCKED,
                    reason=f"Too many tags: {len(tags)} (max {self.MAX_TAGS})",
                    content_hash=self.compute_hash(content),
                    warnings=result.warnings,
                    trust_level=trust_level,
                )
            for tag in tags:
                if len(tag) > self.MAX_TAG_LENGTH:
                    return GuardResult(
                        is_valid=False,
                        severity=GuardSeverity.BLOCKED,
                        reason=f"Tag too long: {tag[:50]}... ({len(tag)} chars, max {self.MAX_TAG_LENGTH})",
                        content_hash=self.compute_hash(content),
                        warnings=result.warnings,
                        trust_level=trust_level,
                    )

        # ── Sanitize content ─────────────────────────────────────────────
        result.sanitized_content = self.sanitize_content(content)
        result.trust_level = trust_level

        return result