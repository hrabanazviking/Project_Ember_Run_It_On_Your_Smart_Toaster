# Python Package Security Audit Report
**Date:** 2026-05-10 | **Platform:** Raspberry Pi (ARM64) | **Python:** 3.11

---

## P0 — Priority Install

### 1. scrapling ⭐ 48,303 | v0.4.7 | BSD-3-Clause
- **GitHub:** D4Vinci/Scrapling — Active (pushed 2026-05-09)
- **CVEs:** None found
- **Suspicious code:** None. `ad_domains.py` is a static blocklist (feature, not malicious)
- **Phone-home/telemetry:** None detected
- **Install-time code:** No suspicious setup.py execution
- **License:** BSD-3-Clause ✅ Permissive
- **Pi compatible:** Requires Python ≥3.10. Depends on lxml, cssselect, orjson — ARM compatible
- **Supply chain risk:** Low. Main deps are well-known packages
- ⚠️ Note: `fetchers` extra pulls in curl_cffi, playwright, patchright, browserforge
- **Verdict: ✅ SAFE** — Install base package. Review `fetchers` extra deps separately

### 2. flaresolverr ⭐ 13,829 | v3.3.21rc4.post3 | MIT
- **GitHub:** FlareSolverr/FlareSolverr — Maintained (pushed 2026-03-26)
- **CVEs:** None direct, but deps have known CVEs (waitress ≤2.1.2: CVE-2024-49768, CVE-2024-49769)
- **CRITICAL ISSUES:**
  - 🔴 **Version is RELEASE CANDIDATE** (rc4.post3), not stable
  - 🔴 **Listens on 0.0.0.0 by default** — network exposed without auth
  - 🔴 **ALL deps pinned to exact versions**, including **YANKED** requests==2.32.0
  - 🔴 **Depends on DrissionPage BETA** (4.1.0.0b14) — another unstable package
  - 🟡 Downloads Chromium binaries during build (build_package.py with subprocess.run)
  - 🟡 Requires Xvfb (headless display) on Linux — xvfbwrapper dep
  - 🟡 waitress==2.1.2 has CVE-2024-49768/49769 (request smuggling)
- **License:** MIT ✅ Permissive
- **Pi compatibility:** Concerning — Chromium + Xvfb on ARM may be slow/problematic
- **Verdict: ⚠️ CAUTION** — Not suitable for Pi as a pip package. Use as Docker container instead. Do NOT install bare on Pi.

### 3. rebrowser-patches | Not on PyPI
- **GitHub:** rebrowser/rebrowser-patches ⭐ 1,347 | No license
- **CVEs:** None found
- **Issues:**
  - 🔴 **NOT on PyPI** — cannot `pip install`. Must install from GitHub or npm
  - 🟡 Last push 2025-05-09 (1 year stale)
  - 🟡 No license file detected
  - This is primarily a **JavaScript/Node.js patch set** for Puppeteer/Playwright
  - `rebrowser-playwright-python` (⭐99) is the Python fork — also Apache-2.0
- **Verdict: ⚠️ CAUTION** — Use `rebrowser-playwright-python` pip package instead. Limited maintenance activity.

---

## P1 — Should Evaluate

### 4. botright ⭐ 978 | v0.5.1 | GPL-3.0
- **GitHub:** Vinyzu/Botright — Maintained (pushed 2026-03-29)
- **CVEs:** None found
- **Suspicious code:** `geetest.py` is commented out (disabled). base64 reference is in commented code
- **Phone-home/telemetry:** None detected
- **Key deps:** undetected-playwright-patch (patched Playwright by kaliiiiiiiiii), chrome-fingerprints, numpy, hcaptcha-challenger, httpx, playwright
- **Concerns:**
  - 🟡 Depends on `undetected-playwright-patch` — a **forked/patched Playwright** by single dev "kaliiiiiiiiii"
  - 🟡 Depends on `chrome-fingerprints` — also by same author (Vinyzu), GPL-3.0
  - 🟡 GPL-3.0 license — copyleft, may affect your project
  - 🟡 `recognizer` dependency untested on ARM
- **License:** GPL-3.0 ⚠️ Copyleft — may require your code to also be GPL
- **Pi compatible:** numpy + Playwright will work on ARM but may be slow
- **Verdict: ⚠️ CAUTION** — GPL-3.0 is restrictive. Supply chain includes patched/forked Playwright from single maintainer

### 5. ghost-cursor | NOT ON PYPI
- **GitHub:** Original JS package (berstend/ghost-cursor) — unmaintained Python port
- **Python port:** `mcolella14/python_ghost_cursor` (⭐79, last updated 2022) — STALE
- **Issues:**
  - 🔴 **No PyPI package** for Python
  - 🔴 The Python port is 3+ years old with no updates
  - No CVE tracking, no security audits on Python port
- **Verdict: ❌ SKIP** — No viable Python package exists. Consider implementing Bezier curve mouse movement yourself or using botright which includes similar functionality.

### 6. undetected-playwright ⭐ 216 | v0.3.0 | Apache-2.0
- **GitHub:** QIN2DIM/undetected-playwright — LAST PUSH 2024-08-28 (stale 1.5+ years)
- **CVEs:** None found
- **Suspicious code:** None — just stealth injection scripts for Playwright
- **Key deps:** Only `playwright`
- **Concerns:**
  - 🔴 **Unmaintained** — last commit Aug 2024, 9 open issues
  - 🟡 Very small package (3 .py files) — stealth patches may be detectable by modern anti-bot
  - 🟡 Patch approach may break with Playwright updates
- **License:** Apache-2.0 ✅ Permissive
- **Verdict: ⚠️ CAUTION** — Unmaintained. Consider `rebrowser-playwright-python` or `patchright` as alternatives.

### 7. DrissionPage ⭐ 11,917 | v4.1.1.2 | NOASSERTION
- **GitHub:** g1879/DrissionPage — Active (pushed 2026-05-03)
- **CVEs:** None found
- **CRITICAL ISSUES:**
  - 🔴 **exec()/eval() used in browser.py** — `exec(src)` used for dynamic dict key assignment. While input comes from config files, this is a code injection vector
  - 🟡 `eval()` used in `options_manage.py` to parse config values — evaluates strings from config
  - 🟡 **No recognized open-source license** — GitHub shows "NOASSERTION", meaning terms are unclear
  - 🟡 264 open issues — large issue backlog
  - 🟡 Chinese documentation primary — may affect auditability
- **deps:** lxml, requests, cssselect, DownloadKit, websocket-client, click, tldextract, psutil
- **Pi compatible:** Should work on ARM
- **Verdict: ⚠️ CAUTION** — exec/eval usage is concerning. No clear license is a legal risk. Review before using.

### 8. curl_cffi ⭐ 5,566 | v0.15.0 | MIT
- **GitHub:** lexiforest/curl_cffi — Active (pushed 2026-05-06)
- **CVEs:** **CVE-2026-33752** (SSRF via internal IP redirect) — **Fixed in v0.15.0** (current version)
- **Suspicious code:** None detected. No phone-home, no data exfiltration
- **Binary content:** Ships prebuilt `.so` (libcurl compiled with OpenSSL patches for TLS fingerprint spoofing)
- **Key deps:** cffi≥2.0.0, certifi, rich
- **Concerns:**
  - 🟡 Ships compiled native `.so` — trust in binary provenance
  - 🟡 ARM (aarch64) build available — ✅ Pi compatible
  - ✅ CVE-2026-33752 is fixed in current version (0.15.0)
- **License:** MIT (per README) ✅ Permissive
- **Pi compatible:** aarch64 wheel available ✅
- **Verdict: ✅ SAFE** — Install v0.15.0+ only (SSRF fix). Binary provenance is a minor concern but well-audited.

---

## P2 — Nice to Have

### 9. playwright-recaptcha ⭐ 533 | v0.5.1 | MIT
- **GitHub:** Xewdy444/Playwright-reCAPTCHA — Maintained (pushed 2026-04-30)
- **CVEs:** None found
- **Key deps:** playwright≥1.33.0, pydub==0.25.1, SpeechRecognition==3.10.4, tenacity==8.3.0
- **Concerns:**
  - 🟡 **Sends audio to Google Speech Recognition API** (`recognizer.recognize_google()`) — data leaves your infrastructure
  - 🟡 **Optional CapSolver API integration** — sends captcha images + API key to capsolver.com
  - 🟡 Pinned deps: pydub==0.25.1, SpeechRecognition==3.10.4, tenacity==8.3.0
  - 🟡 SpeechRecognition requires PyAudio or similar — may have ARM build issues
- **License:** MIT ✅ Permissive
- **Pi compatible:** May have audio dependency issues on ARM
- **Verdict: ⚠️ CAUTION** — Data exfiltration risk with Google Speech API. Only use if you accept Google receiving your captcha audio data.

### 10. fake-useragent ⭐ 4,056 | v2.2.0 | Apache-2.0
- **GitHub:** fake-useragent/fake-useragent — **ARCHIVED** (last push 2026-03-29)
- **CVEs:** None found
- **Phone-home:** ✅ **None** — v2.x uses local bundled JSONL file (2.6MB), no network calls
- **Suspicious code:** None
- **deps:** Only importlib-resources (for Python <3.10)
- **Concerns:**
  - 🔴 **Repo is ARCHIVED** — no future updates, UA database will go stale
  - 🟡 Large bundled data file (2.6MB JSONL) — but static, no network calls
- **License:** Apache-2.0 ✅ Permissive
- **Pi compatible:** ✅ Pure Python, no ARM issues
- **Verdict: ✅ SAFE** — Safe to install but ARCHIVED. UA data will become stale. Consider curl_cffi's built-in impersonation instead.

---

## Summary Table

| # | Package | Verdict | Risk Level | Key Concern |
|---|---------|---------|-----------|-------------|
| 1 | scrapling | ✅ SAFE | Low | Large optional dep tree |
| 2 | flaresolverr | ⚠️ CAUTION | High | RC version, 0.0.0.0 binding, yanked deps, use Docker |
| 3 | rebrowser-patches | ⚠️ CAUTION | Medium | No PyPI, stale, use rebrowser-playwright-python |
| 4 | botright | ⚠️ CAUTION | Medium | GPL-3.0 copyleft, forked Playwright |
| 5 | ghost-cursor | ❌ SKIP | High | No Python package, 3yr stale port |
| 6 | undetected-playwright | ⚠️ CAUTION | Medium | Unmaintained 1.5yr, use alternatives |
| 7 | DrissionPage | ⚠️ CAUTION | High | exec/eval, no license, 264 open issues |
| 8 | curl_cffi | ✅ SAFE | Low | CVE fixed in current v0.15.0 |
| 9 | playwright-recaptcha | ⚠️ CAUTION | Medium | Sends audio to Google, CapSolver API |
| 10 | fake-useragent | ✅ SAFE | Low | Archived, but safe. UAs will go stale |

## Recommendations for Raspberry Pi

1. **Install first:** `scrapling`, `curl_cffi`, `fake-useragent` — all safe
2. **Install with review:** `rebrowser-playwright-python` (pip) instead of rebrowser-patches
3. **Install with caution:** `botright` (accept GPL), `playwright-recaptcha` (accept Google data flow)
4. **Do NOT install directly:** `flaresolverr` — use Docker image instead
5. **Skip entirely:** `ghost-cursor` (no Python version), `undetected-playwright` (unmaintained)
6. **Review carefully:** `DrissionPage` (exec/eval risk, unclear license)
7. **For curl_cffi:** Pin to ≥0.15.0 to avoid CVE-2026-33752 (SSRF)
