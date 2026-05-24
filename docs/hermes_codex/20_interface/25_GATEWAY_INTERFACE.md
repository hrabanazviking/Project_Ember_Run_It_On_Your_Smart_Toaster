---
codex_id: 25_GATEWAY_INTERFACE
title: Gateway Interface — Multi-Platform Message Contract Under Scrutiny
role: Auditor
layer: Interface
status: draft
hermes_source_refs:
  - gateway/platforms/base.py:1-200
  - gateway/platforms/base.py:1301-2000
  - gateway/platform_registry.py:38-260
  - gateway/hooks.py:1-211
  - SECURITY.md:170-220
  - gateway/platforms/base.py:114-166
  - gateway/platforms/base.py:167-200
ember_subsystem_targets: [Munnr, Strengr, Hjarta]
cross_refs:
  - 10_domain/14_GATEWAY_MULTI_PLATFORM
  - 50_verification/54_SECURITY_REVIEW
  - 50_verification/55_INVARIANT_LIST
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Gateway Interface — The Multi-Platform Message Contract

*Sólrún, with a thin smile: a gateway is the place where strangers reach the agent. Strangers are not allowed to know what the agent knows about them. Strangers are not allowed to vote on what the agent does next. The interface that crosses that boundary is the one I will inspect first.*

Hermes's gateway ([`gateway/`](../../../../tmp/hermes-agent/gateway/)) bridges 22+ messaging platforms — Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Wecom, Feishu, BlueBubbles, LINE, SimpleX, HomeAssistant, and more — to a single agent loop. Each platform speaks a different protocol; each has different identity rules, different message-length limits, different multimedia conventions, different injection vectors. The gateway tries to flatten them into one shape so the agent stays one shape.

This is hard. Let me name what is fragile.

## 1. What a message must be

The gateway's normalized event lives in `gateway/platforms/base.py` (the file is 3,812 lines — too long; that's a finding in itself). The relevant types form a contract by accretion. A `MessageEvent`, as seen by adapter code, carries:

- `source` — platform identity (chat, user, thread, message id, chat_type)
- `text` — the user-visible content
- `message_id` — adapter-supplied unique id within the platform
- `reply_to_message_id` — optional anchor
- `media_files` — list of `(path, mime, name)` tuples (`gateway/platforms/base.py` patterns referenced in `send` / `send_multiple_images`)
- platform-specific extras embedded in `source` (`thread_id`, `chat_type`, etc.)

**The shape is structurally typed by use, not by declaration.** Nowhere in the file does a `class MessageEvent: ...` declare exhaustively what fields are mandatory. The `BasePlatformAdapter` methods consume what they need and raise `AttributeError` when the field is missing — that AttributeError gets caught by the dispatcher and surfaced as a log line.

This is a known shape of bug. The audit verdict is: the contract works because Hermes has tests pinning every platform's emission shape — there are 30+ files in `tests/gateway/test_*platform*.py` — but a new platform adapter that misses a field will not crash at registration. It will crash on the first message of the wrong shape.

## 2. The `BasePlatformAdapter` surface

`gateway/platforms/base.py:1301-2000` defines the adapter contract. Sampled methods:

```python
class BasePlatformAdapter(ABC):
    def __init__(self, config: PlatformConfig, platform: Platform): ...
    def message_len_fn(self) -> Callable[[str], int]: ...
    def supports_draft_streaming(self, ...) -> bool: ...
    async def send_draft(self, ...) -> Any: ...
    def has_fatal_error(self) -> bool: ...
    def set_fatal_error_handler(self, handler: ...) -> None: ...
    @abstractmethod
    async def connect(self) -> bool: ...
    @abstractmethod
    async def disconnect(self) -> None: ...
    @abstractmethod
    async def send(self, chat_id: str, message: str, *, metadata=None, ...) -> ...
    async def create_handoff_thread(self, ...) -> ...
    async def edit_message(self, ...) -> ...
    async def delete_message(self, ...) -> ...
    async def send_slash_confirm(self, ...) -> ...
    async def send_clarify(self, ...) -> ...
    async def send_private_notice(self, ...) -> ...
    async def send_typing(self, chat_id: str, metadata=None) -> None: ...
    async def stop_typing(self, chat_id: str) -> None: ...
    async def send_multiple_images(self, ...) -> ...
    async def send_image(self, ...) -> ...
    async def send_animation(self, ...) -> ...
    # ... continues for video, audio, document, voice, sticker, reactions, buttons ...
```

That's an interface of **30+ methods, most optional with default implementations**. The contract is "implement what your platform supports; rely on `NotImplementedError` to fail at call site." This is the opposite of a typed interface. It works because the dispatcher checks support with `supports_draft_streaming(...)` and similar before calling. It would not work without those checks.

For a new platform author, the question "what is the *minimum* I must implement?" has no clear answer. The brief implies `connect`, `disconnect`, `send`. The rest is "implement if you can, fail safely if you can't."

## 3. The shape of identity is *not* uniform

`source.platform`, `source.chat_id`, `source.user_id`, `source.thread_id`, `source.chat_type` — each is a string. Each platform interprets them differently:

- **Telegram**: `chat_id` is a string-encoded negative integer for groups, positive for DMs. `thread_id` is `message_thread_id` for forums; for DM-topics Hermes invented a synthetic `direct_messages_topic_id` (`gateway/platforms/base.py:43-65`).
- **Discord**: `chat_id` is the channel snowflake (17-20 digits). `thread_id` is the thread snowflake.
- **Slack**: `chat_id` is a channel id (`Cxxx...`); `thread_id` is the thread `ts` (a timestamp string).
- **Email**: `chat_id` is the operator email; `thread_id` is the In-Reply-To header.
- **Matrix**: `chat_id` is the room id (`!xxx:server`); `thread_id` is the event id of the root reply.

**Consumers must not assume any structure** beyond "string, opaque." Hermes has tests confirming this — but the test surface is the contract surface. A consumer that splits `chat_id` on `:` is broken for Telegram but works for Matrix.

For Ember, this matters because Strengr (the tether) must carry routing keys end-to-end if Ember ever federates. The shape of identity is the shape of the routing key. **Borrow Hermes's "opaque string" stance.**

## 4. UTF-16 and the silent truncation hazard

`gateway/platforms/base.py:114-166` defines `utf16_len` and `_prefix_within_utf16_limit`:

```python
def utf16_len(s: str) -> int:
    """Count UTF-16 code units in *s*.

    Telegram's message-length limit (4 096) is measured in UTF-16 code units,
    **not** Unicode code-points.  Characters outside the Basic Multilingual
    Plane (emoji like 😀, CJK Extension B, musical symbols, …) are encoded as
    surrogate pairs and therefore consume **two** UTF-16 code units each, even
    though Python's ``len()`` counts them as one.
    """
    return len(s.encode("utf-16-le")) // 2
```

This is the kind of correctness work that distinguishes a serious gateway from a hobby project. A naive `s[:4096]` truncation:

- splits a surrogate pair (the user sees `�` at the end)
- under-truncates (the message is rejected by the platform)
- over-truncates (the message is shorter than necessary)

The binary-search prefix function (`gateway/platforms/base.py:129-146`) is correct. It is also the *only* place the truncation rule lives. A future maintainer who adds a new send path and writes `message[:limit]` reintroduces the bug.

**Audit finding**: this is a contract that lives in a function, not in the data. There is no `TruncatedMessage` type that asserts "this string is safe to send via Telegram." It is operator discipline.

## 5. The injection surface

Every inbound message is **attacker-controlled text** until proven otherwise. The brief moves through:

1. Inbound message arrives at platform adapter.
2. Adapter normalizes to `MessageEvent`.
3. Gateway dispatcher invokes `MessageHandler` (`agent/...`).
4. Handler builds a system prompt + user message.
5. LLM emits.
6. Output flows back through `send` paths.

The injection vectors:

### 5.1 At step 1: the platform-shaped attack

A Telegram message with a HTML entity, a Discord mention `<@!1234567890>`, a Slack `<@U123>`, a Matrix `<a href="...">link</a>` body — each can render differently in different consumers. Hermes redacts Discord snowflakes at log time (`agent/redact.py:153-155`) and phone numbers (`agent/redact.py:158-159`), but rendering is up to the adapter.

### 5.2 At step 3: confused-deputy on identity

`agent/redact.py:155` redacts `<@123456789012345678>` mentions in logged text. If the adapter renders an LLM response containing a *fabricated* Discord mention, it could ping a real user. The adapter, not the redactor, must escape.

Audit verdict: this is a documented stance in `SECURITY.md` (the dashboard renders agent output as inert HTML), but the gateway-side stance for "agent output as Discord/Telegram markdown" is *implicit*. The CommonMark / MarkdownV2 / Slack-mrkdwn escaping rules live inside each adapter; the contract that says "the agent must assume its output will be rendered" is prose, not type.

### 5.3 At step 5: the auto-tool path

Several Hermes platforms ship inbound webhook handlers (`gateway/platforms/webhook.py`, `msgraph_webhook.py`, `wecom_callback.py`). A webhook that fires before the allowlist is loaded, or a webhook that bypasses allowlist because of a `session_id` reuse bug, dispatches agent work for an unauthorized caller. `SECURITY.md:189-209` says this is in scope under §3.1; the test `tests/gateway/test_allowlist_startup_check.py` exists explicitly to pin this.

## 6. Hooks are not part of the interface — but they are part of the trust surface

`gateway/hooks.py:1-211` defines the event-hook system. Hooks load from `~/.hermes/hooks/<name>/handler.py` and run with full agent privileges (`SECURITY.md:155-168` — same as plugins). Events include `agent:start`, `agent:step`, `agent:end`, `session:start`, `session:end`, `command:*`. The dispatch:

```python
# gateway/hooks.py:174-181
for fn in self._resolve_handlers(event_type):
    try:
        result = fn(event_type, context)
        if asyncio.iscoroutine(result):
            await result
    except Exception as e:
        print(f"[hooks] Error in handler for '{event_type}': {e}", flush=True)
```

Two notable shapes:

1. **`exec_module` runs the handler at load time** (`gateway/hooks.py:115-122`). A malicious `handler.py` doesn't need to be invoked — importing it is the vulnerability.
2. **`emit_collect` lets a hook return a value that influences dispatch** (`gateway/hooks.py:183-210`). Decision-style hooks for `command:*` can allow/deny/rewrite. A buggy hook returning `None` is fine; a hook that *intends* to deny but raises is silently treated as "no opinion, default allow."

This is documented. It is also exactly the kind of shape Ember's Vow of Modular Authorship demands — failure is isolated. But the *trust* boundary is not the dispatch logic; it is operator review of the handler code. Hermes states this in `SECURITY.md`; Ember must.

## 7. The platform registry — a soft contract for plugins

`gateway/platform_registry.py:38-260` lets plugins register new platforms:

```python
@dataclass
class PlatformEntry:
    name: str
    label: str
    adapter_factory: Callable[[Any], Any]
    check_fn: Callable[[], bool]
    validate_config: Optional[Callable[[Any], bool]] = None
    is_connected: Optional[Callable[[Any], bool]] = None
    required_env: list = field(default_factory=list)
    install_hint: str = ""
    setup_fn: Optional[Callable[[], None]] = None
    source: str = "plugin"
    plugin_name: str = ""
    allowed_users_env: str = ""
    allow_all_env: str = ""
    max_message_length: int = 0
    pii_safe: bool = False
    emoji: str = "🔌"
    allow_update_command: bool = True
    platform_hint: str = ""
    env_enablement_fn: Optional[Callable[[], Optional[dict]]] = None
    apply_yaml_config_fn: Optional[Callable[[dict, dict], Optional[dict]]] = None
    cron_deliver_env_var: str = ""
    standalone_sender_fn: Optional[Callable[..., Awaitable[dict]]] = None
```

That's 22 fields. The first six are mandatory by convention; the rest are optional. Notable observations:

- **`PlatformRegistry.register` is last-writer-wins** (`gateway/platform_registry.py:172-187`): a plugin can shadow a built-in. Documented, intentional, terrifying for a security review.
- **`create_adapter` is a chain of validators that all fail-closed** (`gateway/platform_registry.py:208-256`): missing deps → None; bad config → None; factory exception → None. The caller must check the return value. A `None` return is the *only* failure signal.
- **No version field**. A plugin built against an old `PlatformEntry` shape that lacks a now-required field will not even be flagged at registration.

For Ember, the takeaway is structural: a registry *is* an interface. Plugin-registered platforms are not a peripheral concern; they are the same trust surface as in-tree adapters. The interface must be versioned and the registration must be explicit.

## 8. The allowlist contract

`SECURITY.md:189-209` is unusually clear:

> "An allowlist is required for every enabled network-exposed adapter. Adapters must refuse to dispatch agent work, resolve approvals, or relay output until an allowlist is set. Code paths that fail open when no allowlist is configured are code bugs in scope under §3.1."

This is a typed-failure shape that Hermes enforces with code: every network adapter has an allowlist check, and `tests/gateway/test_allowlist_startup_check.py` pins the "must fail closed at startup" assertion.

Audit verdict: this is the strongest contract on the gateway surface, and it is the one Ember should clone verbatim if she ever exposes Bifröst over HTTP. **Fail closed is not optional.**

## 9. Stance: agent output is rendered, not trusted

`SECURITY.md:240-243` introduces "stance":

> "Hermes Agent has documented a stance about how its output should be rendered by a consuming layer (dashboard, gateway adapter, file writer, shell)..."

The stance is the contract for the rendering layer. It is the only contract that lives outside Hermes itself — it constrains the *consumer*. For platform adapters, the stance is: *agent output is escaped before render*. The Discord adapter escapes Discord markdown; the Telegram adapter escapes MarkdownV2; the email adapter HTML-escapes. A stance violation (one adapter that *doesn't* escape) is in scope under §3.1.

This is rare and good. Few projects make the rendering contract explicit. Ember should adopt the same approach for Munnr's terminal rendering and any future surface.

## 10. The shape of fatal errors

The base adapter carries explicit fatal-error state:

```python
# gateway/platforms/base.py
def has_fatal_error(self) -> bool: ...
def fatal_error_message(self) -> Optional[str]: ...
def fatal_error_code(self) -> Optional[str]: ...
def fatal_error_retryable(self) -> bool: ...
def _set_fatal_error(self, code: str, message: str, *, retryable: bool) -> None: ...
def set_fatal_error_handler(self, handler: ...) -> None: ...
```

This is a typed degraded-state pattern: a platform that has lost its connection can be in three states — connected, transiently disconnected (will retry), fatal (will not retry). The handler is operator-installable.

Compare to Ember's `Disconnected` value (per ADR 0007 §2.2): same shape, applied to Brunnr instead of the gateway. Ember already has this pattern; she should extend it to Strengr per [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]].

## 11. What Ember would need to validate at the boundary

If Ember ever exposes a chat interface beyond Munnr (the CLI), the minimum validation contract:

1. **Identity**: `chat_id` and `user_id` are opaque strings. Validate as non-empty, length-bounded. Do not parse.
2. **Text**: enforce a max code-point length *and* a max UTF-16 length (per `utf16_len` rule above). Reject above limit; do not silently truncate inbound.
3. **Encoding**: reject lone surrogates inbound (`agent/message_sanitization.py:31-39` provides the canonical `_SURROGATE_RE`). Replace with U+FFFD on outbound where the model emitted them.
4. **Allowlist**: every network surface fails closed if allowlist absent.
5. **Rate**: per-`chat_id` token-bucket rate limit. (Hermes lacks a uniform layer for this; per-platform rate limits exist in `gateway/platforms/signal_rate_limit.py` and `telegram_network.py` — non-uniform.)
6. **Replay**: dedupe `message_id` over a sliding window. Webhooks can re-deliver.
7. **Authn material in metadata**: `Authorization` headers, OAuth tokens, gateway-specific signatures (Wecom CRYPTO, MS Graph subscription validation) — handle in adapter, never propagate to handler.

## What This Means for Ember

**Subsystems affected:** Munnr (rendering/surface), Strengr (tether/routing identity), Hjarta (first-run authorization wizard for future surfaces).

**Vows touched:**

- **Vow of Modular Authorship** — every gateway adapter is failable; cascade failures must be impossible.
- **Vow of Public-Friendliness** — operator must see allowlist state, fatal-error state, in plain language.
- **Vow of Honest Memory** — the gateway must never let an inbound message inject a `<memory-context>` fence the agent treats as authoritative (see [[20_interface/24_MEMORY_INTERFACE]] §2.1).

**Concrete proposals:**

1. **Define `MessageEvent` as a dataclass with typed fields** before adding any second Ember surface. Do not let the contract drift into "structural by use."
2. **Treat identity as opaque strings.** Borrow the rule. Never parse a `chat_id` substring.
3. **Adopt the `utf16_len` pattern** in Munnr's word-wrap logic and any future Bifröst HTTP surface. The contract is a function plus a type, not just a function.
4. **Adopt allowlist-fail-closed.** Verbatim. Ember's `ember --bind` (if ever introduced for Bifröst) must refuse to listen on non-loopback without an allowlist.
5. **Adopt the "stance" idea.** Document that *all* agent output is rendered as inert text by Munnr. Future surfaces (Auga, Bifröst) inherit the stance. Renderers that escape incorrectly are bugs.
6. **Implement fatal-error state in Strengr.** Three states: connected, transiently disconnected (with `Disconnected(reason)` typed value), fatal (with operator-installable handler). Half this work is already done; finish it.
7. **No 22-field PlatformEntry dataclasses.** If Ember reaches the point of supporting plugin-registered surfaces, the registry MUST be versioned, MUST be explicit-fields-only (no `extra: dict`), and MUST be operator-reviewed at install.
8. **Inbound surrogate scrub.** Apply `_sanitize_surrogates` from `agent/message_sanitization.py:31-39` at the surface boundary before any Brunnr write.
9. **Mention/mentioned-id escaping.** If Ember ever speaks a platform that has `<@id>`-style mentions, the model output must be escaped before send. The stance lives in code, not docs.
10. **Replay protection.** A `message_id` dedupe window in any surface that takes webhooks. Ember does not have this need at slice 2; flag it for slice 3+ if Bifröst lands.

Cross-link with [[50_verification/54_SECURITY_REVIEW]] §3 (multi-platform attack surfaces) and [[50_verification/55_INVARIANT_LIST]] for the consolidated invariant set.

The gateway interface is wide. Wide interfaces fail silently. Hermes has the right code for many of the right concerns, but the contracts live in tests and prose. Ember should keep her surfaces narrow, and where she must widen, the widening must be typed.
