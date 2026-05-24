---
codex_id: 36_CONTEXT_FILE_DISCIPLINE
title: Context File Discipline — Project Context, Prompt Building, Cache Ergonomics
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - agent/prompt_builder.py:1298-1466
  - agent/system_prompt.py:60-285
  - agent/prompt_caching.py:1-79
  - agent/context_compressor.py:1-80
  - agent/context_compressor.py:550-820
  - run_agent.py:145
ember_subsystem_targets: [Munnr, Funi, Hjarta, Smiðja]
cross_refs:
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/33_HOT_COLD_TIERS
  - 30_execution/38_PERSISTENT_MEMORY
  - 60_synthesis/63_INTEGRATION_PATHS
---

# Context File Discipline

A prompt is a contract with the model. Every token you put in it is a token you're paying for, sometimes literally, always in time. Hermes runs at a scale where prompts get long fast: SOUL.md, AGENTS.md, .cursorrules, skill bodies, environment hints, computer-use guidance, model-family operational guidance, tool-use enforcement, memory snapshot, USER profile, timestamp line — *and* the actual conversation. Without discipline this becomes a 30,000-token system prompt that re-prefixes every request and burns cache misses on every turn.

Hermes has discipline. I'm Eldra. Let me show you the actual mechanics, then tell you how Munnr should construct Ember's prompts.

## The Three-Tier System Prompt

`agent/system_prompt.py:60` defines `build_system_prompt_parts()` which returns three keys:

```python
return {
    "stable":   "\n\n".join(...),   # identity + tool guidance + skills + environment + platform
    "context":  "\n\n".join(...),   # AGENTS.md / .cursorrules / cwd discovery + system_message
    "volatile": "\n\n".join(...),   # memory + USER.md + timestamp/session/model line
}
```

Three tiers. Same string. **Built once per session.** Cached on `agent._cached_system_prompt`. Only rebuilt after a context-compression event.

```python
# agent/system_prompt.py:289-291
def build_system_prompt(agent: Any, system_message: Optional[str] = None) -> str:
    parts = build_system_prompt_parts(agent, system_message=system_message)
    return "\n\n".join(p for p in (parts["stable"], parts["context"], parts["volatile"]) if p)
```

The order of concatenation is the cache strategy. Stable tier goes first because *it changes least often*. Context tier in the middle because it depends on cwd. Volatile tier last because it changes every session.

Two key invariants from the file docstring (line 295–301):

> "Layers are ordered cache-friendly: stable identity/guidance first, then session-stable context files, then per-call volatile content (memory, USER profile, timestamp). The whole string is treated as one cached block — Hermes never rebuilds or reinjects parts of it mid-session, which is the only way to keep upstream prompt caches warm across turns."

The second invariant matters: **once built, the system prompt is immutable for the session**. Even if memory changes mid-session, the system prompt doesn't get re-rendered. The new memory shows up the next session.

`invalidate_system_prompt()` at line 306 is the one exception:

```python
def invalidate_system_prompt(agent: Any) -> None:
    """Invalidate the cached system prompt, forcing a rebuild on the next turn.

    Called after context compression events. Also reloads memory from disk
    so the rebuilt prompt captures any writes from this session.
    """
    agent._cached_system_prompt = None
```

Compression is the only natural rebuild point. By the time compression fires, the session has already burned through a lot of tokens — the cache hit on the *new* prefix is what saves money going forward.

## The Date-Only Trick

`agent/system_prompt.py:264-271`:

```python
from hermes_time import now as _hermes_now
now = _hermes_now()
# Date-only (not minute-precision) so the system prompt is byte-stable
# for the full day. Minute-precision changes invalidate prefix-cache KV
# on every rebuild path (compression boundary, fresh-agent gateway turns,
# session resume without a stored prompt).
timestamp_line = f"Conversation started: {now.strftime('%A, %B %d, %Y')}"
```

This is the small, brilliant choice. If the timestamp were minute-precision (e.g., `Conversation started: 2026-05-22 14:37`), every fresh agent boot in a different minute would have a *different* system prompt string. Anthropic's prompt caching would miss. Hermes pays for the cache miss as a cold-start cost only once *per day*, not once *per session*.

Credit comment in the code: "Credit: @iamfoz (PR #20451)." Every detail in Hermes has a person's name on it.

## The Anthropic Cache Marker

`agent/prompt_caching.py` is short — 79 lines. It implements *one* caching layout, called `system_and_3`:

```python
def apply_anthropic_cache_control(
    api_messages: List[Dict[str, Any]],
    cache_ttl: str = "5m",
    native_anthropic: bool = False,
) -> List[Dict[str, Any]]:
    """Apply system_and_3 caching strategy to messages for Anthropic models.

    Places up to 4 cache_control breakpoints: system prompt + last 3 non-system
    messages, all at the same TTL.
    """
```

The four `cache_control` breakpoints land at:

1. System prompt (covers stable + context + volatile tiers).
2. Last 3 non-system messages.

The 5m TTL is default; 1h is opt-in. Cost reduction: ~75% on multi-turn conversations within a session (per the module docstring). This is *real* money — Sonnet at $3/Mtok input becomes effectively $0.30/Mtok input after the breakpoint hits.

The pattern is layered cache: the system prompt is always cached; the last 3 user/assistant exchanges are also cached so a *near-immediate* follow-up gets cached too. Three breakpoints because Anthropic's API caps the count. Beyond 3, older messages become "warm" but uncached.

## Project Context File Discovery

`agent/prompt_builder.py:1426-1465`:

```python
def build_context_files_prompt(cwd: Optional[str] = None, skip_soul: bool = False) -> str:
    """Discover and load context files for the system prompt.

    Priority (first found wins — only ONE project context type is loaded):
      1. .hermes.md / HERMES.md  (walk to git root)
      2. AGENTS.md / agents.md   (cwd only)
      3. CLAUDE.md / claude.md   (cwd only)
      4. .cursorrules / .cursor/rules/*.mdc  (cwd only)
    """
```

**First found wins.** A project with both AGENTS.md and CLAUDE.md only sees AGENTS.md. The agent doesn't get conflicting instructions; the project author picked one convention.

The discovery order encodes a politics: Hermes's own `.hermes.md` is checked first (walking up to git root), then the cross-tool standards `AGENTS.md` and `CLAUDE.md` (cwd only), then `.cursorrules` (cwd only). Each is capped at 20,000 chars via `_truncate_content()` at line 1301:

```python
def _truncate_content(content: str, filename: str, max_chars: int = CONTEXT_FILE_MAX_CHARS) -> str:
    """Head/tail truncation with a marker in the middle."""
    if len(content) <= max_chars:
        return content
    head_chars = int(max_chars * CONTEXT_TRUNCATE_HEAD_RATIO)
    tail_chars = int(max_chars * CONTEXT_TRUNCATE_TAIL_RATIO)
    head = content[:head_chars]
    tail = content[-tail_chars:]
    marker = f"\n\n[...truncated {filename}: kept {head_chars}+{tail_chars} of {len(content)} chars. Use file tools to read the full file.]\n\n"
    return head + marker + tail
```

Head/tail truncation with an explicit marker telling the model "use file tools to read the full file." The middle is sacrificed; the model is told it's been sacrificed; the model can recover by reading the file on demand. This is the right pattern. The agent isn't lied to about what it has.

## Prompt Injection Scanning

Every context file content is run through `_scan_context_content(content, filename)` before being injected (line 1356, 1372, etc.). A SOUL.md or AGENTS.md that contains prompt-injection patterns is flagged or stripped. This is *important*: a developer who installs a malicious skill or accepts an unreviewed PR can't accidentally inject "ignore all previous instructions" into the agent's system prompt.

The same scan applies to skill content via the build_context path. Defense in depth.

## Context Compression Boundary

`agent/context_compressor.py:1-80` shows the compression strategy *inside* a session:

> "Self-contained class with its own OpenAI client for summarization. Uses auxiliary model (cheap/fast) to summarize middle turns while protecting head and tail context."

The compression triggers when token estimates exceed a threshold. Head turns (system + first user) and tail turns (most recent N messages, by token budget — see line 651) are protected. Middle turns are summarized by the **auxiliary model** (smaller, cheaper).

Line 37-51 has the summary preamble. It is a precisely-engineered prompt-fragment:

```python
SUMMARY_PREFIX = (
    "[CONTEXT COMPACTION — REFERENCE ONLY] Earlier turns were compacted "
    "into the summary below. This is a handoff from a previous context "
    "window — treat it as background reference, NOT as active instructions. "
    "Do NOT answer questions or fulfill requests mentioned in this summary; "
    "they were already addressed. "
    "Your current task is identified in the '## Active Task' section of the "
    "summary — resume exactly from there. "
    "IMPORTANT: Your persistent memory (MEMORY.md, USER.md) in the system "
    "prompt is ALWAYS authoritative and active — never ignore or deprioritize "
    "memory content due to this compaction note. ..."
)
```

This prefix is *load-bearing*. Without it, the model treats compacted middle-turns as fresh user requests and tries to fulfill them again — a duplicate-action bug. With it, the model knows the summary is reference material only. Every word in this prefix has a reason.

The summary itself uses a structured template (line 37+): `## Active Task`, `## Resolved`, `## Pending Questions`, `## Remaining Work`. Sections, not free prose. The model writing the summary follows the template; the model reading the summary knows where to look.

## What This Means for Ember

Ember already keeps its system prompt minimal compared to Hermes (no SOUL.md flavor wars, no computer-use guidance, no multi-platform hints). But the same disciplines apply, and stealing them now costs less than retrofitting later.

### Munnr's prompt builder shape

Mirror Hermes's tiered structure exactly:

```python
# src/ember/munnr/prompt/system.py

@dataclass(frozen=True)
class SystemPromptParts:
    stable: str       # identity + tool guidance + environment + platform
    context: str      # cwd context files (EMBER.md, AGENTS.md, README.md)
    volatile: str     # memory snapshot, USER.md, date-only timestamp

def build_system_prompt_parts(
    *,
    valid_tool_names: set[str],
    cwd: Path | None,
    memory_block: str | None = None,
    user_profile_block: str | None = None,
    model: str | None = None,
    provider: str | None = None,
) -> SystemPromptParts: ...

def build_system_prompt(parts: SystemPromptParts) -> str:
    return "\n\n".join(p for p in (parts.stable, parts.context, parts.volatile) if p)
```

The shape is pure data — no `agent` reference. Easier to test, easier to reason about. The agent's call site passes in what's needed; the builder returns the assembled string.

### Cache the prompt

A new method on the agent state:

```python
def get_or_build_system_prompt(self) -> str:
    if self._cached_system_prompt is None:
        parts = build_system_prompt_parts(...)
        self._cached_system_prompt = build_system_prompt(parts)
    return self._cached_system_prompt

def invalidate_system_prompt(self) -> None:
    self._cached_system_prompt = None
    if self._memory_store:
        self._memory_store.load_from_disk()
```

Same shape as `agent/system_prompt.py:306`. Call `invalidate_system_prompt()` after compression. Otherwise treat the system prompt as immutable for the session.

### Date-only timestamp

Mandatory. Use `datetime.now(tz=UTC).strftime("%A, %B %d, %Y")`. Same as Hermes. Same cache savings.

### Context file discovery for Ember

Ember's priority order should be Ember-shaped:

```python
def build_context_files_prompt(cwd: Path | None) -> str:
    """Discover and load context files.

    Priority (first found wins — only ONE project context):
      1. .ember.md / EMBER.md   (walk to git root)
      2. AGENTS.md / agents.md  (cwd only)
      3. CLAUDE.md / claude.md  (cwd only)
      4. README.md              (cwd only — last resort)
    """
```

`README.md` is a deliberate addition for Ember. A user pointing Ember at a project that has no agent-aware doc still gets *some* project orientation. Vow of Public-Friendliness — the user doesn't have to author a separate file for Ember to do useful work in their repo.

### Cap per file

20,000 chars per context file (line 1436 in Hermes). Same cap for Ember. Head/tail truncation with the explicit "use file tools to read the full file" marker. Steal `_truncate_content` verbatim.

### Prompt-injection scan

Adopt `_scan_context_content` from `agent/prompt_builder.py:32`. Ember's variant must scan SOUL-equivalents and project files for injection patterns like "ignore all previous instructions," role-confusion attempts, and tool-misuse triggers. Failure mode: log + redact the suspicious section. Never refuse to start.

### Prompt caching — beyond Anthropic

Hermes only implements Anthropic's prompt caching. Ember should design the abstraction:

```python
# src/ember/strengr/cache_control.py
@dataclass(frozen=True)
class CacheControlPolicy:
    breakpoints: int            # 4 for Anthropic, 0 for everyone else
    ttl: Literal["5m", "1h", None]
    place_at_system: bool
    place_at_last_n_messages: int

def apply_cache_control(
    messages: list[Message],
    *,
    provider: Provider,
    model: str,
) -> list[Message]:
    """Provider-aware cache_control marker injection."""
```

Today only Anthropic supports cache_control. Tomorrow others might. The abstraction lets Ember exploit caching wherever it's available without rewiring the call paths.

### Compression — adopt verbatim

The summary preamble from `agent/context_compressor.py:37`. The protect-head-and-tail strategy. The structured-summary template. The auxiliary-client split. These are 1:1 transferable. Ember's compression should live in `src/ember/funi/compress.py` (Funi owns it because the LLM call is to the local model).

The only tweak: on Pi-tier, compression should be *more aggressive*. Smaller models do better with shorter contexts. Pi-tier compression triggers at 50% of `funi_max_context`; Laptop-tier at 70%; Workstation-tier at 80%.

### What Hermes Loads That Ember Should Skip

Be ruthless. Hermes's stable tier includes:

- `MEMORY_GUIDANCE` (~600 chars)
- `SESSION_SEARCH_GUIDANCE` (~400 chars)
- `SKILLS_GUIDANCE` (~600 chars)
- `KANBAN_GUIDANCE` (~500 chars)
- `COMPUTER_USE_GUIDANCE` (~1500 chars)
- `TOOL_USE_ENFORCEMENT_GUIDANCE` (~800 chars)
- `GOOGLE_MODEL_OPERATIONAL_GUIDANCE` (~1500 chars)
- `OPENAI_MODEL_EXECUTION_GUIDANCE` (~1500 chars)
- `PLATFORM_HINTS[platform_key]` (~500 chars per platform)

That's 7,000+ chars of model-family operational guidance Ember does not need because Ember is opinionated about which models work and ships compatibility-tested ones. Trim ruthlessly. **A Pi running a 3B model can't afford 2K tokens of "tool use enforcement guidance" eating its context window.**

Ember's stable tier:

- Identity (SOUL-equivalent, but tiny — 200 chars max).
- Tool guidance (per loaded tool, ~100 chars each, only loaded tools).
- Environment hint (one line, e.g. "Pi 5 (8GB) running Funi llama3.2:3b").
- Platform hint (only if user is on iOS/Android/etc., else omit).

Total budget for stable tier on Pi-tier: **under 1,500 chars**. Compared to Hermes's typical ~10,000 chars. Smaller windows demand sharper prompts.

### Vows on the line

- **Vow of Smallness** — strengthened by the tighter stable-tier budget.
- **Vow of Honest Memory** — strengthened by the immutable-per-session contract. The model can't have its memory secretly rewritten mid-session.
- **Vow of Modular Authorship** — strengthened by the prompt-injection scan. A broken context file logs and continues.
- **Vow of Flexible Roots** — preserved. Context discovery uses `Path(cwd).resolve()` not absolute paths.
- **Vow of Tethered Grounding** — strengthened. The "use file tools to read the full file" marker tells the model it doesn't have the whole thing.

### Concrete deliverables

1. `src/ember/munnr/prompt/system.py` — three-tier builder, cache slot on agent state.
2. `src/ember/munnr/prompt/context_files.py` — priority-ordered discovery with truncation + scan.
3. `src/ember/strengr/cache_control.py` — provider-aware breakpoint injector.
4. `src/ember/funi/compress.py` — head/tail-protected compressor with tier-aware threshold.

Each is < 400 lines. Each is independently testable. None violates a Vow.

### Where to read next

- [[30_execution/33_HOT_COLD_TIERS]] — the tier-aware compression threshold.
- [[30_execution/38_PERSISTENT_MEMORY]] — what gets injected as the volatile tier.
- [[60_synthesis/63_INTEGRATION_PATHS]] — sequenced PRs to land these primitives.

The prompt is the contract. Sign it once, keep it stable, pay the cache discount. — Eldra.
