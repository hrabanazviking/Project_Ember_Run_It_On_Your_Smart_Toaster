# 36 — The CloakBrowser Web Plane

How Ember reaches the web beyond `fetch_url`'s capabilities.
The escalation pattern, the approval flow, the ethical
guardrails.

---

## The two-tier web access design

Ember today has one web tool: `fetch_url`. Yggdrasil adds a
second tier: `fetch_url_cloaked` (CloakBrowser-based).

The pattern: **always try the simple tool first; escalate
only when needed; the operator approves the escalation**.

```
┌─────────────────┐
│  Funi proposes  │
│  fetch_url(url) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  fetch_url tries to GET     │
└────────┬────────────────────┘
         │
    ┌────┴────┐
    │         │
   200       403/503/cloudflare-challenge
    │         │
    ▼         ▼
content    typed ToolReply.error:
returned   "anti-bot detected; consider escalation"
    │         │
    │         ▼
    │   ┌─────────────────────────┐
    │   │  Funi sees the typed     │
    │   │  hint; proposes          │
    │   │  fetch_url_cloaked(url)  │
    │   └────────┬────────────────┘
    │            │
    │            ▼
    │   ┌─────────────────────────┐
    │   │  Operator approval      │
    │   │  (modal with ⚠ marker)  │
    │   └────────┬────────────────┘
    │            │
    │            ▼
    │   ┌─────────────────────────┐
    │   │  CloakBrowser spawns    │
    │   │  Chromium; fetches;     │
    │   │  returns content        │
    │   └─────────────────────────┘
    │
    ▼
Funi continues with content
```

Two-tier means: most operators most of the time use
`fetch_url` (fast, cheap, simple). When they actually need
the heavy tool, they get it — but only with explicit
approval.

---

## Why escalation, not always-cloaked

We *could* make `fetch_url` always use CloakBrowser. Why
don't we?

1. **Resource cost.** CloakBrowser spawns Chromium
   (~200MB, ~3s). For static HTML, that's 100× more
   expensive than `urllib`.
2. **Ethical default.** Stealth Chromium bypasses
   anti-bot defenses. The right default is *not* to bypass
   unless needed.
3. **Operator visibility.** The escalation prompt *tells
   the operator* something special is happening — they
   approve consciously, not by routine.
4. **Pi-class operators.** Don't have the resources to run
   Chromium routinely. `fetch_url` works fine for most
   needs.

---

## How `fetch_url` signals "needs escalation"

Today's `fetch_url` returns typed errors. We add a hint
field:

```python
@dataclass(frozen=True, slots=True)
class ToolReply:
    call_id: str
    output: str = ""
    error: str | None = None
    elapsed_s: float = 0.0
    suggest_escalation: str | None = None    # new
```

When `fetch_url` sees a 403/503/cloudflare-challenge:

```python
return ToolReply(
    call_id=call.call_id,
    error="fetch_url refused (403); anti-bot defense detected",
    suggest_escalation="fetch_url_cloaked",
)
```

Funi sees the suggestion in the tool reply context. Its
follow-up message can naturally propose the escalation tool.

This is a *gentle architectural extension* — one new
optional field on ToolReply, used by one new tool, ignored
by all existing tools.

---

## CloakBrowser's tool descriptor

```python
DESCRIPTOR = ToolDescriptor(
    name="fetch_url_cloaked",
    description=(
        "Fetch a URL using a stealth Chromium browser. Slower + "
        "heavier than fetch_url, but bypasses common anti-bot "
        "defenses and renders JavaScript. Use when fetch_url "
        "returns suggest_escalation='fetch_url_cloaked'."
    ),
    parameters_schema={
        "url": ToolParameter(
            kind=ToolParameterKind.URL,
            description="The http(s) URL to fetch.",
        ),
        "wait_for_selector": ToolParameter(
            kind=ToolParameterKind.STRING,
            description="Optional CSS selector to wait for before reading.",
            required=False,
            default="",
        ),
    },
    required_approval=ApprovalPolicy.PER_CALL,
    timeout_s=60.0,  # Chromium is slower
)
```

Per-call approval is the default. Operators who want
"always approve" can set `tools.approval_overrides:
{fetch_url_cloaked: standing}` — but the heavier tool's
default is *more cautious*.

---

## Operator-facing approval flow

In Stofa's ToolApprovalScreen:

```
╭──── ᛟ ── Approve tool call? ──────╮
│                                     │
│   Ember wants to use:                │
│   fetch_url_cloaked                  │
│                                     │
│   ⚠ This tool spawns a stealth       │
│   Chromium browser. It bypasses      │
│   common anti-bot defenses.          │
│                                     │
│   URL:                              │
│     https://example.com/spa-page     │
│                                     │
│   Reason from Ember:                 │
│     "fetch_url returned 403 with     │
│      Cloudflare challenge"           │
│                                     │
│   y = approve once                   │
│   a = approve + remember session     │
│   n = deny                           │
│                                     │
╰─────────────────────────────────────╯
```

The ⚠ marker + the reason from Ember make the operator's
choice fully informed.

---

## Robots.txt and ethical defaults

CloakBrowser's adapter respects robots.txt by default —
same as `fetch_url`. Operators can override per call via
the arguments.

We deliberately *do not* enable user-agent rotation by
default. We deliberately *do not* enable cookie
persistence across calls by default. Both are operator
opt-ins per realm config:

```yaml
yggdrasil:
  cloakbrowser:
    enabled: true
    user_agent_rotation: false    # default off (ethical)
    cookie_persistence: false      # default off (cleaner)
    respect_robots_txt: true       # default on
    max_concurrent_fetches: 1
    timeout_s: 60.0
```

---

## Session cookies via Kista (Phase 2)

When CloakBrowser needs site-specific authentication (the
operator's session cookie for site X), it asks Kista:

```python
# CloakBrowser adapter
session_cookie = secret_resolver.resolve(
    f"kista://ember/cloakbrowser/sessions/{host}"
)
```

The operator can store per-site cookies in Kista:

```bash
kista add ember/cloakbrowser/sessions/news.example \
  --type secret_note \
  --value 'session=abc123'
```

CloakBrowser uses these without exposing them in `ember.yaml`
or process memory beyond the call duration.

---

## Caching policy

CloakBrowser fetches are *cached briefly* (default 5
minutes, operator-configurable). The same URL fetched twice
within the TTL returns the cached result.

Why: Chromium spawn cost. If Ember references the same
URL multiple times in one chat session, caching saves real
time.

Cache invalidation: by TTL only. No revalidation. Operators
who need fresh content per call set `cache_ttl_s: 0`.

---

## What CloakBrowser does NOT do

- **Web scraping at scale.** This is a per-call tool, not a
  scraping framework. Operators who need to scrape 1000 pages
  use scrapy or similar, not Ember.
- **Persistent browser sessions.** Each call spawns +
  tears down. No long-running browser.
- **Form filling / interaction.** Reads pages; doesn't act
  on them (no clicks, no typing, no checkout flows). That's
  a separate tool category (web automation; not in scope).
- **Bypassing legal access controls.** CloakBrowser's
  stealth is for *anti-bot* defenses, not authentication.
  Sites that require login: operator provides credentials
  via Kista; CloakBrowser uses them for legitimate access.

---

## Risk / known issues

- **Compute cost.** Each fetch is ~3s + ~200MB. Pi-class
  operators turn this off by default.
- **Ethical considerations.** Stealth Chromium bypasses
  anti-bot defenses; some sites consider this hostile. The
  per-call approval + the ⚠ marker push the decision to the
  operator. Operator-controlled, not Ember-automated.
- **Maintenance cost.** Anti-bot defenses evolve; CloakBrowser
  needs to keep up. We pin to a known-good version and
  upgrade when needed.

---

## Operator-facing example

```
> volmarr: read https://complex-spa.example/article/123

[Funi proposes fetch_url; modal approves; fetch_url returns 403]
[fetch_url's typed reply suggests escalation to fetch_url_cloaked]

ember: I tried fetch_url but the site has Cloudflare
protection. Want me to use the cloaked browser?

╭──── Approve tool call? ──────╮
│ fetch_url_cloaked              │
│ URL: complex-spa.example/...   │
│ ⚠ stealth Chromium             │
│ y / a / n                      │
╰────────────────────────────────╯

> volmarr: y

[3 second pause; Chromium spawns + fetches]
ember: Got it. Here's what the article says: ...
```

Clean escalation; operator-approved; visible cost; no
surprise.

---

## Closing

CloakBrowser as web plane gives Ember access to the
modern, JavaScript-heavy, anti-bot-defended web — without
making *every* fetch heavy. Two-tier design protects
operators from cost they don't need, while making the
heavy tier available when they do.

This is *escalation as architectural pattern* — and it
generalizes (V2 may add more escalation tiers for other
expensive operations).
