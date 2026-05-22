# 00 — What Is OpenClaw

The factual baseline. Grounded in the OpenClaw GitHub repo
as of 2026-05-21.

---

## In one sentence

**OpenClaw** is an open-source personal AI assistant platform you
run on your own devices, exposed across 23+ messaging channels,
with voice + mobile companion apps, sandboxed tool execution, and a
local-first gateway architecture. Tagline: *"Your own personal AI
assistant. Any OS. Any Platform. The lobster way. 🦞"*

It is licensed MIT, written in TypeScript on Node.js, maintained as a
pnpm monorepo, and has **373,791 stars** on GitHub at the time of
this writing.

---

## The vital statistics

| Property | Value |
|---|---|
| **Repo** | github.com/openclaw/openclaw |
| **License** | MIT |
| **Primary language** | TypeScript |
| **Runtime** | Node.js 24 (recommended) / 22.19+ |
| **Package manager** | pnpm (workspace) |
| **Default branch** | `main` |
| **Stars** | 373,791 |
| **Forks** | 77,661 |
| **Open issues** | 7,412 |
| **Last push** | 2026-05-22 (active) |
| **Topics** | ai, assistant, crustacean, molty, openclaw, own-your-data, personal |
| **Mascot** | Molty (a space lobster) |

The stars + forks + open issues + recent commits paint a clear
picture: **OpenClaw is a major mainstream open-source AI assistant
project**.

For context: Ember (this project) has < 100 stars. We are in two very
different leagues of *adoption* and *resource availability*. The
**design quality of OpenClaw** is presumed to be high because the
community has actively curated and improved it for what is likely
years.

---

## What it does, plainly

Operator workflow:

1. `npm install -g openclaw@latest`
2. Edit `~/.openclaw/openclaw.json` with a model provider.
3. (Optional) Install daemon: `--install-daemon` (systemd / launchd).
4. (Optional) Pair with companion apps (macOS menu bar, iOS, Android).
5. (Optional) Connect messaging bridges (WhatsApp, Telegram, etc.).
6. Chat with the assistant via terminal, voice wake, mobile, or any
   of the supported channels.

The assistant has access to tools (browser, file editing, sessions
management, cron, Discord/Slack actions, etc.), can be sandboxed,
and routes to different "agents" based on channel/account/peer.

---

## The 23+ messaging channels

OpenClaw bridges to:

WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage,
IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud
Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, Zalo Personal,
WeChat, QQ, WebChat.

Plus native voice/text on macOS, iOS, Android. Plus WebSocket pairing
to iOS/Android nodes for camera/screen-capture.

This is *much wider* than Ember's surfaces (Munnr CLI, planned
Stofa TUI, planned Auga GUI, planned Rödd voice). OpenClaw treats
**meeting-the-operator-where-they-are** as load-bearing.

---

## The "Live Canvas" and A2UI

OpenClaw has a feature called **Live Canvas**, an
"agent-driven visual workspace" with their proprietary **A2UI**
system. The agent can render interactive UI elements that the
operator manipulates.

This sits closest to what we'd call **Auga** in Ember terms (the
planned graphical surface). OpenClaw shipped theirs; Ember hasn't.

---

## The Gateway architecture

OpenClaw's central concept is the **"local-first Gateway"** — a
single control plane handling sessions, channels, tools, and events.
All routes converge on the Gateway.

This is *structurally analogous* to what Bifrǫst does for Ember
(though Ember's Bifrǫst is for memory backends; OpenClaw's gateway
is for messaging channels + agents).

Both share the local-first philosophy. Both reject cloud-first
deployment models for the *primary* path (though OpenClaw also
ships deployment configs for Fly.io / Render for those who want
to self-host on a VPS).

---

## Multi-agent routing

OpenClaw supports **multiple agents** in one OpenClaw install.
Each agent has its own workspace (file directory, prompts, skills,
sessions). Channels/accounts/peers can route to different agents.

Example: operator's WhatsApp goes to "personal" agent; their Slack
goes to "work" agent. Same OpenClaw daemon; two distinct AIs with
their own contexts.

This is *more sophisticated* than Ember's current single-agent
model. We should study it carefully.

---

## Sandboxing

OpenClaw's default: tools run with **host-level access** for the
`main` session. The operator can set:

```
agents.defaults.sandbox.mode: "non-main"
```

…and then non-main sessions are sandboxed. Backends:
- **Docker** (default) — containerized isolation.
- **SSH** — remote execution.
- **OpenShell** — their own sandbox?

Typical sandbox defaults permit `bash`, `process`, `read`, `write`,
`edit`, `sessions` tools while denying `browser`, `canvas`, `nodes`,
`cron`, channel integrations.

Ember's current sandboxing for tools is per-tool (PER_CALL approval
+ path sandbox + robots.txt). OpenClaw's is process-level isolation.
Both are valid; they answer different security questions.

---

## Voice

**Voice Wake** — wake-word triggering on macOS/iOS.
**Talk Mode** — push-to-talk.

Backend: **ElevenLabs** for TTS, with **system TTS fallback**.
Android supports "continuous voice."

This is the closest equivalent to what we'd call **Rödd** in
Ember terms. OpenClaw shipped it; we haven't.

---

## Workspace structure

OpenClaw workspaces (one per agent) contain *injected prompt files*:

- `AGENTS.md` — agent definitions / personalities.
- `SOUL.md` — the agent's core identity? (their naming).
- `TOOLS.md` — tool documentation injected into context.
- `skills/` — operator-curated capability bundles.

These are *files in a directory* that the agent's prompt assembly
references. Operators edit them with standard editors. Mod-friendly.

Ember's equivalent: `identity.json` + `ember.yaml`. OpenClaw goes
further with multiple markdown files that the LLM treats as
authoritative prompt fragments.

---

## ClawHub

A **skills registry** — operators can browse and install bundles.
Centralized; community-maintained.

This is a Pattern Ember has *explicitly avoided* (the Vow of
Modular Authorship favors operator-curated, not centralized
marketplaces). We'll discuss the trade-offs in
[`../lessons/`](../lessons/).

---

## Development channels

Three release tracks:
- **stable** — tagged releases.
- **beta** — prerelease tags.
- **dev** — moving `main` branch.

Operators choose how cutting-edge they want to be. Easy install of
each.

Ember currently has no formal channel separation; this is something
to consider.

---

## What OpenClaw is NOT

- **Not cloud-only.** Local-first by default. Self-hosted on operator
  hardware. Cloud deploy is optional.
- **Not closed-source.** MIT-licensed, full source on GitHub.
- **Not Anthropic-owned.** Independent community project.
- **Not a game engine.** (Prior assumption corrected — earlier
  WebFetch results conflated this with a different project at the
  same name.)
- **Not Python.** TypeScript through and through.
- **Not Pi-class hardware-targeted.** Node.js doesn't fit the
  Pi-class profile we target.

---

## Why this matters to Ember

OpenClaw is the **mainstream version of what we are quietly
building**. They:
- Reached mass adoption (373k stars).
- Validated the sovereign-AI-assistant market.
- Solved many problems (multi-agent, sandboxing, voice wake, mobile)
  that we have only planned.

We benefit from being a *small project in their wake*: we can study
their decisions, borrow what fits our Vows, and avoid what doesn't.

---

## Closing

OpenClaw is a real, well-built, popular, sovereign AI assistant.
Maintained by serious engineers. Used by hundreds of thousands of
operators.

It is not Ember's enemy. It is Ember's *teacher* — by example.

The next 56 docs unpack what we learn.
