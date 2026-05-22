# 37 — The Mobile Question

OpenClaw ships native iOS + Android apps. Ember has none. What
does mobile mean for Ember? When and how should we approach it?

---

## What mobile gives operators

When Ember is on the operator's phone:

### 1. Always-with-them

Phone is the universally-carried device. Ember available
wherever the operator is.

### 2. Spontaneous interactions

Quick question while walking; voice during driving; photo capture
while shopping. These aren't possible on a laptop.

### 3. Notification surface

Ember can *initiate* (with operator permission): "Your weekly
summary is ready" / "I noticed something interesting."

### 4. Device capabilities as tools

Camera, location, accelerometer, calendar, contacts, etc. The
phone has rich sensors the agent can leverage.

### 5. Companion-app polish

Native apps have:
- App-store discoverability.
- Push notifications.
- Background processing.
- Native UI feel.

For *some* operators: this is essential to the AI assistant
being part of their daily life.

---

## What mobile costs us

### 1. Engineering

Native iOS app (Swift / SwiftUI): months of work + ongoing.
Native Android (Kotlin / Compose): months of work + ongoing.

Total: substantial multi-quarter investment.

### 2. App-store mediation

Apple's App Store has:
- Review process (weeks for first submission).
- Annual developer fee ($99).
- Removal risk if Apple decides our app violates guidelines.
- Forced compliance with their UI/UX patterns.

Google Play is slightly looser but has its own constraints.

### 3. Platform-specific maintenance

iOS updates break things. Android fragmentation. We'd need
testing across many devices, OS versions.

### 4. Sovereignty tension

Apple/Google control app distribution. If we build native apps,
we're partially dependent on their goodwill.

### 5. Footprint

Mobile apps add significant *project* surface. Documentation,
build infrastructure, contributors with mobile skills.

---

## The web companion alternative

A **Progressive Web App** sidesteps many costs:

- No native app development; HTML/CSS/JS in the browser.
- No app-store mediation; install from a URL.
- Cross-platform free (any modern mobile browser).
- Faster iteration.

What PWA gives:
- Chat surface on mobile browser.
- WebSocket to home Ember Gateway.
- Add to home screen (looks like an app).
- Limited push notifications (Apple restricts; Android allows).
- No native API access (camera with limits; location with
  limits; etc.).

What PWA doesn't give:
- Always-on background process.
- Robust native push notifications (esp. iOS).
- Tight OS integration (widgets, Siri shortcuts).

For Ember V4-V5: **web companion is the right path**.

---

## Why not native (for now)

Per [`../patterns/17_COMPANION_APP_PAIRING.md`](../patterns/17_COMPANION_APP_PAIRING.md):

🔴 **Reject native mobile for V1-V4.**

Reasons:
- Engineering cost is too high.
- We have no mobile developer.
- App-store mediation conflicts with sovereignty.
- Web companion gets 80% of value at 20% of cost.

If/when Ember scales (V5+) and has mobile contributors: revisit.

---

## What the web companion needs

For V5 web companion shape:

### Backend (Ember daemon)

- WebSocket server on tailnet.
- HTTP API for non-real-time operations.
- Pairing flow (QR code + token).
- Session sync.

### Frontend (mobile browser)

- Chat UI (HTML/CSS).
- WebSocket client.
- Local storage for chat draft (offline).
- Service worker for offline-installability.
- A2A-like UI elements (if Live Canvas lands).

### Connectivity

- Tailscale on phone → reach home Ember.
- Or local-network access if on same wifi.
- No public exposure of Ember.

---

## Use case: kitchen Pi

A Pi in the kitchen running Ember. Operator's phone (on tailnet)
opens web companion in browser. Operator asks Ember while
cooking; Ember replies via:
- Text on phone screen.
- Voice on Pi speaker (if Rödd enabled).

This is **a powerful, sovereign, modest-tech kitchen AI**.

Cost: a Pi 5 + a phone with browser + Tailscale. Operator
already has both.

This is the *promise of Ember* + Klóinn-informed companion.

---

## Use case: travel

Operator traveling. Laptop is in hotel; phone is on train.
Operator wants to ask Ember a question.

Without mobile companion: operator must wait until laptop.

With web companion: open mobile browser → tailnet → talk to
Ember on hotel laptop. Synced session.

This is *substantial operator value*.

---

## Use case: roommate / family

Multiple humans in one household, one Ember running. Each pairs
their phone with their persona:
- Phone A → "personal" persona for human A.
- Phone B → "personal" persona for human B.

Multi-persona shape (per
[`../patterns/11_MULTI_AGENT_WORKSPACES.md`](../patterns/11_MULTI_AGENT_WORKSPACES.md))
combined with web companion enables shared household AI.

V5+ scenario. Genuinely valuable.

---

## What about deeper iOS/Android features

Some features are mobile-native-only:
- Background voice wake.
- Lock-screen integration.
- Siri shortcuts (iOS).
- Tasker integration (Android).
- Widget on home screen.

Web companion can't deliver these. Native could.

For V5: skip these.
For V6+: maybe.

In the meantime: **operators who want native-only features can
build native frontends themselves** (Tasker scripts, Shortcuts,
etc.) that interface with Ember's HTTP API.

This *empowers operators* without us shipping native apps.

---

## Privacy on mobile

Mobile = location data + camera access + microphone access +
contacts. Each is sensitive.

Ember's web companion has *minimal* native API access:
- Browser asks permission per-feature (camera, microphone).
- No always-on listening (browser doesn't allow that).
- No location tracking unless operator initiates.

This is *better than native apps* for privacy-conservative
operators. Browsers are sandboxed in ways native apps aren't.

---

## The mobile-LLM question

Should the LLM run *on* the phone?

Modern phones (iPhone 15, Pixel 8) can run 3B-parameter models
on-device. Apple's Foundation Models, Google's Gemini Nano,
etc.

Pros: zero network latency; full sovereignty (LLM on phone too).
Cons: battery drain; thermal throttling; smaller model than
home.

For Ember: **don't ship phone-native LLM** in V5. Phone is a
*surface*; LLM stays on home device.

When phone hardware reaches Pi 5-class capability with good
battery (V6+), revisit.

---

## What about Ember as a phone background process

iOS/Android allow background apps with restrictions:
- Background fetch (limited duration).
- Push notifications (server-initiated).
- Audio playback (foreground-only effectively).

For Ember-on-phone: would consume battery; would face
restrictions; wouldn't deliver primary value (full LLM).

Skip.

---

## Configuration shape (web companion)

```yaml
ember:
  companion:
    enabled: false  # opt-in V5
    
    web:
      bind_address: 0.0.0.0     # tailnet interface
      port: 8888
      tls: false                # tailnet encrypted
      session_token_ttl_minutes: 60
      pairing_token_ttl_minutes: 5
      
    auth:
      kind: token                # or "tailscale_identity" if available
      
    ui:
      theme: dark
      voice_buttons: true        # if Rödd enabled
      a2ui_rendering: false      # V5+ if Live Canvas
```

---

## What we tell operators

Honest messaging:

> *Ember has no native mobile app and isn't planning one in
> V1-V4. We will ship a web companion in V5 — a browser-based
> interface accessible from your phone over Tailscale. This
> gives you most of the mobile benefit without app-store
> mediation.*
>
> *Operators who specifically need native iOS/Android features
> (lock screen widgets, push notifications, OS shortcuts) might
> prefer projects with mobile-first design — OpenClaw is one.
> Ember serves the operator who wants sovereign + Pi-class +
> Norse-coded + browser-mobile-OK.*

This is honest constraint setting.

---

## What about *operator-built* mobile apps

If an operator wants native mobile, they can:
- Use Ember's HTTP API.
- Build their own native app.
- Open-source it as community contribution.

We accept community-contributed native frontends. We don't
maintain them in core.

This is the Modular Authorship pattern applied to mobile.

---

## Closing

The Mobile Question is **a strategic deferral**. OpenClaw ships
native mobile; Ember will ship web companion in V5. Both serve
operators; different shapes.

Ember's mobile strategy:
- 🔴 Reject native mobile for V1-V4.
- 🟢 Web companion in V5 (Progressive Web App).
- 🟢 Tailnet-only access (no public exposure).
- 🟢 Open HTTP API for operator-built native apps.
- 🔴 No phone-native LLM (V5+); LLM on home device.

The Klóinn lesson: **mobile is valuable but not at any cost**.
Web companion gets us 80% of the value for 20% of the
engineering. Operators wanting more can build it; we don't
have to.

In the meantime: the *home device* is the operator's Ember
center of gravity. Mobile is *additive*, not primary.
