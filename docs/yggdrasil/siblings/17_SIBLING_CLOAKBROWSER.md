# 17 — Sibling: CloakBrowser

> *"Stealth Chromium that passes every bot detection test."*

Playwright + stealth-Chromium wrapper. Available on PyPI + npm
+ Docker. Already mature.

---

## What it is

A pre-existing library (the only sibling with significant
external adoption already — PyPI downloads, GitHub stars,
Docker pulls) that wraps Chromium with anti-detection
techniques:

- Passes major bot-detection tests (Cloudflare, reCAPTCHA
  v2/v3, DataDome, etc., to varying degrees).
- Playwright-shaped API.
- Headless or headful.
- Available as `pip install cloakbrowser`.

The name evokes a *cloaked walker* — a being who can pass
through hostile gates undetected.

---

## Why this sibling matters for Yggdrasil

It's the **web access plane beyond `fetch_url`**.

Ember's existing `fetch_url` tool is great for plain HTTP
GETs against cooperative sites. But the modern web is hostile
to programmatic access:

- JavaScript-heavy SPAs render content only after JS executes.
- Cloudflare and similar interpose challenges.
- Anti-bot fingerprinting blocks `urllib` immediately.

When Ember encounters a URL that `fetch_url` can't handle,
she needs an escalation path. CloakBrowser is that path.

---

## How Yggdrasil integrates CloakBrowser

### Integration role

CloakBrowser becomes a new first-party tool: `fetch_url_cloaked`
(or similar name). The chat-loop flow:

1. Funi proposes `fetch_url` for a URL.
2. `fetch_url` attempts; gets 403 / 503 / Cloudflare-challenge.
3. The tool's typed `ToolReply.error` indicates "anti-bot
   detected; consider escalation."
4. Funi (informed by the reply) proposes `fetch_url_cloaked`.
5. Operator approves (CloakBrowser is more powerful = harder
   approval; gets the same per-call approval gate).
6. CloakBrowser fetches; content is returned.

### Adapter shape

A new tool file `src/ember/tools/fetch_url_cloaked.py`
following the existing `fetch_url.py` pattern:

- Same sandbox checks (IDNA, address class, credentials
  refusal).
- Same audit-log integration.
- Same per-call approval default.
- Additionally: a "spawn cost" indicator (Chromium spawn is
  ~3 seconds and ~200MB RAM); only escalate when needed.

### Configuration shape

```yaml
yggdrasil:
  cloakbrowser:
    enabled: false             # operator opt-in
    max_concurrent_fetches: 1   # Chromium is heavy
    timeout_s: 60.0             # longer than fetch_url's 10s
    cache:
      enabled: true             # cache fetched pages briefly
      ttl_s: 300                # 5 min
    user_agent_rotation: false  # default off; ethical default
```

### Operator-facing approval flow

Stofa's ToolApprovalScreen (per the parallel design tree)
gets a slightly different presentation for CloakBrowser:

```
╭──── ᛟ ── Approve tool call? ──────╮
│                                     │
│   Ember wants to use:                │
│   fetch_url_cloaked                  │
│                                     │
│   ⚠ This tool uses CloakBrowser     │
│   to fetch URLs that resist          │
│   plain HTTP. It runs Chromium       │
│   (heavier resource cost).            │
│                                     │
│   URL:                              │
│     https://example.com/some-spa     │
│                                     │
│   y = approve once                   │
│   a = approve + remember session     │
│   n = deny                           │
│                                     │
╰─────────────────────────────────────╯
```

The ⚠ warning communicates that this is more involved than
`fetch_url`.

---

## When CloakBrowser is the right choice

- JavaScript-rendered content (SPAs).
- Sites behind Cloudflare.
- API endpoints that require cookie-based auth from a real
  browser session.
- Pages with anti-bot detection.

When `fetch_url` is still the right choice (no escalation):

- Static HTML / Markdown.
- JSON APIs.
- Sites that don't fingerprint.

The escalation pattern is **opt-in per call** — Ember doesn't
automatically jump to CloakBrowser; she tries `fetch_url`
first, learns from its typed error, and *proposes*
escalation to the operator.

---

## Risk / known issues

- **Ethical concerns.** Bypassing anti-bot defenses is a
  trade-off. The operator decides per call; Ember doesn't
  automate "always bypass." Sites that explicitly say "don't
  scrape" (robots.txt) should be respected; the existing
  fetch_url's robots.txt parser applies to CloakBrowser too.
- **Resource cost.** Chromium is ~200MB RAM + ~3s spawn.
  Pi-class operators may turn this off.
- **Dependency complexity.** CloakBrowser brings in npm + a
  Chromium binary. Heavy install.

---

## Open questions for Phase 2 ratification

1. **Robots.txt enforcement.** Mirror `fetch_url`'s policy
   exactly? Or stricter (more conservative for the more
   powerful tool)?
2. **Concurrent fetch limit.** 1 by default? Allow operator
   override?
3. **User-agent rotation.** Default off (ethical), but
   operators can enable for legitimate research?
4. **Cookie persistence between sessions.** Per-host? Or
   ephemeral per call?

---

## Test strategy

Phase 2 ships:

- **Unit tests** for the tool adapter with mocked CloakBrowser.
- **Integration test** against a Cloudflare-protected test
  endpoint (operator-provided in CI; opt-in marker).
- **Resource-cost regression** — verify a single fetch
  stays under 250MB RAM peak.

Tests in `tests/unit/test_tools_fetch_url_cloaked.py` and
`tests/integration/test_tools_cloakbrowser_real.py`.

---

## Operator-facing example

```
> volmarr: read https://complex-spa.example/article/123

ember: I'll fetch that.
[fetch_url tries; fails with 403/cloudflare]

Funi: I tried fetch_url but the site requires JavaScript or
has bot protection. Would you like me to use the cloaked
fetcher instead?

╭──── Approve tool call? ──────╮
│ fetch_url_cloaked              │
│ URL: complex-spa.example/...   │
│ y / a / n                      │
╰────────────────────────────────╯

> volmarr: y

[CloakBrowser fetches; content returned]
ember: I got it. Here's the relevant section:
```

A clear escalation; operator-approved; no surprise.

---

## Closing

CloakBrowser is the **walker that goes beyond the boundary**
when ordinary travel fails. Powerful, expensive, ethical,
opt-in. Yggdrasil V2 ships it as a per-call-approval tool —
the operator's choice every time.
