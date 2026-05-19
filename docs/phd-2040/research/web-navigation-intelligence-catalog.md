# Web Navigation Intelligence: Tool & Skill Catalog
## Comprehensive Survey of AI Agent Web Interaction Tools, Skills, and Libraries
### Runa Gridweaver Freyjasdóttir · Mythic Engineering · May 2026

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [OpenClaw/Hermes Skills](#openclawhermes-skills)
3. [Python Libraries](#python-libraries)
4. [OpenClaw Community Skills](#openclaw-community-skills)
5. [CAPTCHA Solving](#captcha-solving)
6. [Browser Fingerprint Tools](#browser-fingerprint-tools)
7. [MCP Servers](#mcp-servers)
8. [AI Web Agent Frameworks](#ai-web-agent-frameworks)
9. [Cloudflare Bypass Tools](#cloudflare-bypass-tools)
10. [TLS Fingerprinting](#tls-fingerprinting)
11. [Skill Registries](#skill-registries)
12. [Gaps & Recommendations](#gaps--recommendations)
13. [Quick Reference: What We Have vs. What's Available](#quick-reference)

---

## Executive Summary

This catalog surveys **50+ tools, libraries, skills, and services** for AI agent web navigation, anti-bot evasion, CAPTCHA solving, and human-like browser interaction. Sources include:

- **Hermes Agent** built-in and optional skills
- **OpenClaw** community skill ecosystem (5400+ skills)
- **Python/Node** open-source libraries
- **MCP servers** for browser automation
- **Commercial services** and APIs

Key finding: **No single tool covers the full stack.** Our Gríma + Camoufox + playwright_stealth combination is uniquely positioned — but there are significant complementary tools we should evaluate.

---

## OpenClaw/Hermes Skills

### Built-In Toolsets

| Skill | Type | Relevance | Description |
|-------|------|-----------|-------------|
| **Browser Toolset** | Core | ⭐⭐⭐⭐⭐ | browser_navigate, browser_click, browser_type, browser_snapshot, browser_console, browser_vision, web_search. CDP support when endpoint available. |
| **Web Toolset** | Core | ⭐⭐⭐ | web_search, web_extract. No anti-bot. |
| **macOS Computer Use** | Core (macOS) | ⭐⭐⭐⭐ | Native desktop automation — can drive any GUI including browsers |
| **dogfood** | Skill | ⭐⭐⭐ | QA testing methodology for web apps |

### Optional Hermes Skills

| Skill | Install | Relevance | Description |
|-------|---------|-----------|-------------|
| **scrapling** ⭐ | `hermes skills install official/research/scrapling` | ⭐⭐⭐⭐⭐ | 3-tier web scraping: HTTP → Dynamic → Stealth. Cloudflare Turnstile bypass via StealthyFetcher. Most relevant. |
| **duckduckgo-search** | `hermes skills install official/research/duckduckgo-search` | ⭐⭐⭐ | Free web search, no API key. Fallback. |
| **searxng-search** | `hermes skills install official/research/searxng-search` | ⭐⭐⭐ | Meta-search, 70+ engines, self-hosted. |
| **domain-intel** | `hermes skills install official/research/domain-intel` | ⭐⭐ | Passive domain recon. Pre-navigation intelligence. |
| **sherlock** | `hermes skills install official/osint/sherlock` | ⭐⭐ | OSINT username search. |

---

## OpenClaw Community Skills

### 🔴 HIGHLY RELEVANT — Anti-Bot / Stealth / CAPTCHA

| Skill | Author | Relevance | Description |
|-------|--------|-----------|-------------|
| **camoufox-stealth** | kesslerio | ⭐⭐⭐⭐⭐ | C++ level anti-bot via Camoufox Firefox fork. Stealth compiled into browser. |
| **camoufox-stealth-browser** | kesslerio | ⭐⭐⭐⭐⭐ | Browser automation variant of camoufox-stealth. |
| **camoufox-tools** | adastraabyssoque | ⭐⭐⭐⭐ | Simplified CLI: fox-open, fox-scrape, fox-eval, fox-close. |
| **stealth-browser** | mayuqi-crypto | ⭐⭐⭐⭐⭐ | Anti-detection, Cloudflare bypass, CAPTCHA solving, persistent sessions. |
| **b0tresch-stealth-browser** | b0tresch | ⭐⭐⭐⭐⭐ | Puppeteer-extra with stealth. Anti-bot, CAPTCHA, IP blocks. |
| **browser-automation-stealth** | shepherd217 | ⭐⭐⭐⭐⭐ | Playwright wrapper with stealth mode, proxy rotation, captcha, fingerprint randomization. |
| **agent-browser-stealth** | leeguooooo | ⭐⭐⭐⭐⭐ | Anti-fingerprint, captcha solving, bot-protected websites. |
| **2captcha** | adinvadim | ⭐⭐⭐⭐ | 2Captcha service integration. reCAPTCHA v2/v3, hCaptcha, Turnstile, FunCaptcha, GeeTest. |
| **Capsolver** | DenimEvert | ⭐⭐⭐⭐ | CapSolver API. reCAPTCHA, Cloudflare Turnstile. |
| **openclaw-ultra-scraping** | LeoYeAI | ⭐⭐⭐⭐⭐ | 3-tier adaptive scraping (HTTP → Dynamic → Stealth). Uses Scrapling. |
| **browse-2-0-2** | radical7vii | ⭐⭐⭐⭐⭐ | Remote Browserbase sessions, CAPTCHA solving, residential proxies. |
| **next-browser** | highxshell | ⭐⭐⭐⭐ | Cloud browser, residential proxy, stealth, CAPTCHA solving via Browserbase. |
| **adspower-browser** | official | ⭐⭐⭐⭐ | AdsPower anti-detect browser profile management. |
| **agent-browser-stagehand** | peytoncasper | ⭐⭐⭐⭐ | Stagehand-based. Has stealth and proxy/CAPTCHA modes. |

### 🟡 MODERATELY RELEVANT — Browser Automation

| Skill | Relevance | Description |
|-------|-----------|-------------|
| **agent-browser** (thesethrose) | ⭐⭐⭐ | Rust-based headless browser CLI (137k downloads). |
| **agent-browser** (murphykobe) | ⭐⭐⭐ | Form filling, screenshots, navigation. |
| **browser-use** | ⭐⭐⭐ | Browser Use cloud API (26.4k downloads). |
| **Decodo** | ⭐⭐⭐ | Web scraping API with proxy rotation. |
| **Browserless** | ⭐⭐⭐⭐ | Built-in config for Browserless.io CDP. Needs account. |
| **Browserbase MCP** | ⭐⭐⭐⭐ | Cloud browser with stealth + CAPTCHA solving. |

---

## Python Libraries

### Anti-Detect / Stealth Browsers

| Library | Stars | Language | Relevance | Description |
|---------|-------|----------|-----------|-------------|
| **camoufox** | ~300 | Python | ⭐⭐⭐⭐⭐ | Anti-fingerprint Firefox fork. Randomized canvas, WebGL, audio, fonts. **We have this installed.** |
| **nodriver** | ~2k | Python | ⭐⭐⭐⭐ | Successor to undetected-chromedriver. Direct CDP, no WebDriver. **We have this installed.** |
| **undetected-chromedriver** | ~10k | Python | ⭐⭐⭐⭐ | Patched Selenium ChromeDriver. Superseded by nodriver. **NOT installed (superseded).** |
| **undetected-playwright** | ~200 | Python | ⭐⭐⭐⭐⭐ | Patches Playwright Chromium to remove detection vectors. **Should evaluate.** |
| **Selenium Stealth** | ~1.5k | Python | ⭐⭐⭐⭐ | Stealth patches for Selenium. **We use Playwright, not Selenium.** |
| **playwright-stealth** | ~800 | Python | ⭐⭐⭐⭐⭐ | Python stealth patches for Playwright. **We have this installed.** |
| **Botright** | ~500 | Python | ⭐⭐⭐⭐⭐ | Human-like mouse movements, typing simulation, Bezier curves. **Should evaluate.** |
| **DrissionPage** | ~8k | Python | ⭐⭐⭐⭐⭐ | Modern anti-detect browser automation. Built-in anti-bot. Chinese community favorite. **Should evaluate.** |
| **pydoll** | ~200 | Python | ⭐⭐⭐ | Async browser automation via CDP. Anti-detection built in. |

### Web Scraping & Anti-Bot

| Library | Stars | Language | Relevance | Description |
|---------|-------|----------|-----------|-------------|
| **Scrapling** | ~3k | Python | ⭐⭐⭐⭐⭐ | Adaptive scraping with StealthyFetcher. Cloudflare/WAF bypass. **Hermes has this as optional skill.** |
| **Botasaurus** | ~5k | Python | ⭐⭐⭐⭐ | All-in-one scraping framework. Anti-detect, parallel, Cloudflare bypass. |
| **FlareSolverr** | ~7k | Python | ⭐⭐⭐⭐⭐ | Proxy server solving Cloudflare challenges with real browser rendering. |
| **Cloudscraper** | ~4k | Python | ⭐⭐⭐⭐ | Improved Cloudflare bypass. Handles more challenge types. |
| **curl_cffi** | ~2k | Python | ⭐⭐⭐⭐⭐ | Browser TLS fingerprint impersonation. JA3/JA4. **Critical for API-level stealth.** |

### Human-Like Behavior

| Library | Stars | Language | Relevance | Description |
|---------|-------|----------|-----------|-------------|
| **browser-use** | ~55k | Python | ⭐⭐⭐⭐⭐ | LLM-driven browser agent. Human-like navigation, form filling. Built-in CAPTCHA detection. |
| **Ghost Curser** | ~500 | Node | ⭐⭐⭐⭐ | Bezier curve mouse movement for Playwright. **Directly relevant to Gríma.** |
| **puppeteer-extra-plugin-stealth** | ~25k | Node | ⭐⭐⭐⭐⭐ | Gold standard Node stealth plugin. Hides webdriver, chrome runtime. |
| **Rebrowser patches** | ~1k | Patches | ⭐⭐⭐⭐⭐ | Fixes Playwright CDP leak. Critical for Playwright stealth. **Should install.** |

---

## CAPTCHA Solving

### Open-Source

| Tool | Language | Relevance | Description |
|------|----------|-----------|-------------|
| **hcaptcha-challenger** | Python | ⭐⭐⭐⭐⭐ | AI-based hCaptcha solver using computer vision. No API needed. **We have this installed.** |
| **playwright-recaptcha** | Python | ⭐⭐⭐⭐ | reCAPTCHA solver via audio challenge fallback. Clever approach. |

### Commercial Services

| Service | Types | Pricing | Relevance |
|---------|-------|---------|-----------|
| **2Captcha** | reCAPTCHA v2/v3, hCaptcha, Turnstile, FunCaptcha, GeeTest | ~$3/1000 | ⭐⭐⭐⭐ |
| **Anti-Captcha** | All major types | ~$2/1000 | ⭐⭐⭐ |
| **CapSolver** | reCAPTCHA, Turnstile | ~$1-3/1000 | ⭐⭐⭐⭐ |
| **CaptchaAI** | reCAPTCHA, hCaptcha, FunCaptcha | Varies | ⭐⭐⭐ |
| **YesCaptcha** | All major | Budget | ⭐⭐⭐ |

---

## Browser Fingerprint Tools

| Tool | Type | Relevance | Description |
|------|------|-----------|-------------|
| **FingerprintJS** | Detection (⭐⭐⭐⭐⭐) | 22k stars | Browser fingerprinting library. **Use to TEST our own fingerprint leakage.** |
| **CreepJS** | Detection (⭐⭐⭐⭐⭐) | 1k stars | Advanced fingerprint detection. **Use to validate anti-detect effectiveness.** |
| **fp-collect** | Detection (⭐⭐⭐⭐) | Collection tool | Collects all fingerprint vectors. **Recon tool.** |
| **FingerprintSwitcher** | Spoofing (⭐⭐⭐⭐) | BAS plugin | Generate/spoof fingerprints. |
| **multilogin** | Commercial (⭐⭐⭐⭐) | Enterprise | Professional anti-detect browser. |
| **GoLogin** | Commercial (⭐⭐⭐⭐) | Prosumer | Anti-detect browser + proxy management. |
| **AdsPower** | Commercial (⭐⭐⭐⭐) | Multi-profile | Anti-detect browser. OpenClaw skill available. |

---

## MCP Servers

| Server | Stars | Relevance | Description |
|--------|-------|-----------|-------------|
| **MCP Server Browserbase** | ~500 | ⭐⭐⭐⭐⭐ | Official Browserbase MCP. Cloud browsers with stealth. |
| **playwright-mcp** | ~300 | ⭐⭐⭐⭐⭐ | Local Playwright via MCP. |
| **puppeteer-mcp-server** | ~200 | ⭐⭐⭐⭐ | Puppeteer via MCP. |
| **mcp-browser-use** | New | ⭐⭐⭐⭐⭐ | browser-use agent via MCP. |
| **@anthropic/mcp-server-fetch** | Part of official | ⭐⭐⭐ | Simple page content fetcher (no JS rendering). |

---

## AI Web Agent Frameworks

| Framework | Stars | Relevance | Description |
|-----------|-------|-----------|-------------|
| **browser-use** | ~55k | ⭐⭐⭐⭐⭐ | LLM-driven browser agent. Forms, CAPTCHA, navigation. |
| **Skyvern** | ~10k | ⭐⭐⭐⭐⭐ | AI web agent. Vision+LLM. Handles forms, CAPTCHAs, navigation. |
| **LaVague** | ~4k | ⭐⭐⭐⭐ | LLM + Selenium/Playwright natural-language web navigation. |
| **Agent-E** | ~500 | ⭐⭐⭐⭐ | DOM-aware AI web agent. Multi-step tasks. |
| **WebArena** | ~2k | ⭐⭐⭐ | Benchmark for testing web agents on real sites. |

---

## Cloudflare Bypass Tools

| Tool | Stars | Relevance | Description |
|------|-------|-----------|-------------|
| **Scrapling (StealthyFetcher)** | ~3k | ⭐⭐⭐⭐⭐ | Best open-source Cloudflare bypass. |
| **FlareSolverr** | ~7k | ⭐⭐⭐⭐⭐ | Real browser rendering proxy. Most reliable for Cloudflare. |
| **Cloudscraper** | ~4k | ⭐⭐⭐⭐ | Improved cfscrape. |
| **Camoufox** | ~300 | ⭐⭐⭐⭐⭐ | Full browser with anti-fingerprint. **We have this.** |

---

## TLS Fingerprinting

| Tool | Stars | Relevance | Description |
|------|-------|-----------|-------------|
| **curl_cffi** | ~2k | ⭐⭐⭐⭐⭐ | Python binding for curl-impersonate. Mimics browser TLS fingerprints. |
| **tls-client** | ~1k | ⭐⭐⭐⭐ | Go/Python HTTP client with browser TLS fingerprints. |

---

## Skill Registries

| Registry | URL | Description |
|----------|-----|-------------|
| **ClawHub** | clawhub.ai | Official OpenClaw skill registry |
| **ClawSkills.sh** | clawskills.sh | Independent index (323 browser skills) |
| **VoltAgent/awesome-openclaw-skills** | github.com/VoltAgent/awesome-openclaw-skills | 5400+ curated skills |
| **OpenClawDir** | openclawdir.com | Community directory with voting |
| **LLMBase.ai** | llmbase.ai/openclaw | Trending skills sorted by downloads/stars |
| **LobeHub** | lobehub.com/skills | Third-party marketplace |
| **agentskills.io** | agentskills.io | Open standard for agent skills (Hermes + others) |

---

## Gaps & Recommendations

### Tools We Should Evaluate and Install

| Priority | Tool | Why |
|----------|------|-----|
| 🔴 P0 | **Scrapling** (Hermes skill) | Best open-source Cloudflare/WAF bypass. Complements Camoufox for scraping scenarios. |
| 🔴 P0 | **FlareSolverr** | Solves Cloudflare challenges we can't bypass with behavior alone. |
| 🔴 P0 | **Rebrowser patches** | Fixes critical Playwright CDP detection vector. |
| 🟡 P1 | **Botright** | Human-like mouse movements for Playwright. Could enhance Gríma's Slóð principle. |
| 🟡 P1 | **Ghost Curser** | Bezier curve mouse generation. Directly relevant to Gríma cursor paths. |
| 🟡 P1 | **undetected-playwright** | Playwright patches removing detection vectors. |
| 🟡 P1 | **DrissionPage** | Modern anti-detect with built-in bot evasion. Alternative to Camoufox. |
| 🟡 P1 | **curl_cffi** | TLS fingerprint impersonation for API-level requests. |
| 🟢 P2 | **FingerprintJS / CreepJS** | Test our own fingerprint leakage. Know thy enemy. |
| 🟢 P2 | **2captcha** (OpenClaw skill) | Fallback CAPTCHA solving when behavioral methods fail. |
| 🟢 P2 | **playwright-recaptcha** | Audio challenge approach for reCAPTCHA. |
| 🟢 P2 | **Skyvern** | AI web agent with vision+LLM for complex form navigation. |

### Key Gaps

1. **No single tool covers the full stack** — our Gríma + Camoufox + playwright_stealth combination is already strong
2. **Open-source CAPTCHA solving is limited** — hcaptcha-challenger is best but niche; 2Captcha for fallback
3. **Playwright-stealth Python is less maintained** than the Node counterpart
4. **No comprehensive MCP server** bundles all anti-detect features — Browserbase MCP is closest but commercial
5. **DrissionPage** is underdocumented in English but has powerful anti-detect features from the Chinese community

---

## Quick Reference: What We Have vs. What's Available

### Already Installed on Pi

| Tool | Status | Purpose |
|------|--------|---------|
| camoufox 0.4.11 | ✅ Installed | Anti-detect Firefox browser |
| playwright_stealth 2.0.3 | ✅ Installed | Playwright stealth patches |
| nodriver 0.48.1 | ✅ Installed | Undetected Chrome CDP automation |
| hcaptcha_challenger 0.19.0 | ✅ Installed | hCaptcha solver via Gemini |
| playwright 1.59.0 | ✅ Installed | Browser automation engine |
| Gríma skill | ✅ Installed | Behavioral human-mimicry layer |

### Our Custom Skills

| Skill | Lines | Purpose |
|-------|-------|---------|
| grima | 574 | Human-like behavioral layer (6 Norse principles) |
| anti-bot-navigation | 871 | 8 anti-bot systems field manual |
| human-web-patterns | 1250 | React/ProseMirror/forms/playbooks |
| web-session-management | 1736 | Session persistence & warming |
| camofox-browser | existing | Camoufox integration skill |
| captcha-ninja | existing | CAPTCHA solving strategies |
| browser-automation | existing | Browser automation patterns |

### Not Yet Installed (Recommended)

| Tool | Priority | Install Method |
|------|----------|----------------|
| Scrapling | P0 | `hermes skills install official/research/scrapling` |
| FlareSolverr | P0 | `pip install flaresolverr` |
| Rebrowser patches | P0 | Git clone + Playwright patches |
| Botright | P1 | `pip install botright` |
| Ghost Curser | P1 | `npm install ghost-cursor` |
| DrissionPage | P1 | `pip install DrissionPage` |
| curl_cffi | P1 | `pip install curl_cffi` |
| CreepJS | P2 | Use as test tool (browser-side) |

---

*The web is a fortress. The mask breathes. We have the siege weapons.* 🏰⚔️