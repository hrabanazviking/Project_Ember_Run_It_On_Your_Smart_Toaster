# 05 — Tool Ecosystem

OpenClaw's first-class tools: browser, canvas, nodes, cron,
sessions, Discord/Slack-specific actions. What they are; how
they're structured; what Ember has, hasn't, shouldn't.

---

## The first-class tools

From the README + docs, OpenClaw ships these as *core* (not
plugins):

| Tool | Purpose |
|---|---|
| **browser** | Web browsing — fetch URLs, navigate, extract content |
| **canvas** | The Live Canvas — render UI elements the operator manipulates |
| **nodes** | Companion device pairing — iOS/Android nodes |
| **cron** | Scheduled tasks — "remind me daily at 8am" |
| **sessions** | Session management — list, history, switch, send |
| **discord** | Discord-specific actions |
| **slack** | Slack-specific actions |
| **bash** | Shell command execution |
| **process** | Process management |
| **read/write/edit** | File operations |

This is **a lot**. Eight categories of capability shipped in core.

---

## How they're composed

OpenClaw's chat commands surface tools:

- `/status` — agent status
- `/new` — start new session
- `/reset` — reset session
- `/think <level>` — adjust thinking level
- `/usage` — token/cost transparency

…and the agent itself can invoke any tool it has access to,
subject to sandbox policy.

---

## Tool access model

Three layers govern what an agent can do:

### 1. Sandbox mode

`agents.defaults.sandbox.mode: "non-main"` enables sandboxing for
non-main sessions. Default-deny in sandbox for: `browser`,
`canvas`, `nodes`, `cron`, channel integrations. Default-allow:
`bash`, `process`, `read`, `write`, `edit`, `sessions`.

### 2. Per-agent overrides

An agent can be configured to disable specific tools or allow
others. Per-workspace tool policies.

### 3. Per-call approval (not the default)

For high-stakes tools (channel operations, cron creation), the
operator might be asked to approve before execution.

This is *similar to but not identical to* Ember's tool model
(PER_CALL / STANDING / FORBIDDEN). OpenClaw leans more on sandbox
isolation; Ember leans more on per-call approval prompts.

---

## What this teaches

### Lesson 1: ship "enough" tools by default

Operators who install OpenClaw can *immediately* do useful work
because browser + read + write + edit + bash are all there.

Ember currently ships three tools: `search_well`, `read_local_file`,
`fetch_url`. That's *strategic minimalism*; we ship what we trust.

The right call for Ember is somewhere between:
- **Too few**: operators feel limited; "why doesn't Ember have X?"
- **Too many**: operators feel overwhelmed; tools they don't trust
  exist anyway.

Currently we're closer to "too few." The Klóinn lesson: *expand
slowly, with audit*.

Proposed Ember additions (deferred to later phases):
- `write_local_file` (PER_CALL + sandbox + size cap) — V3.
- `run_shell_command` (PER_CALL + sandbox + allowlist) — V3+.
- `cron_schedule` — V4 (needs daemon).
- `send_to_channel` — V4+ (needs bridges).

### Lesson 2: tool categories vs individual tools

OpenClaw groups by category (`browser`, `canvas`, `cron`). Each
category is a *family* of operations.

Ember's current shape is individual tools. We might benefit from
*categories* as well, especially for sandbox policy:

```yaml
tools:
  categories:
    file_ops:
      tools: [read_local_file, write_local_file]
      sandbox: per_call_default
    network:
      tools: [fetch_url, fetch_url_cloaked]
      sandbox: per_call_with_robots
```

Category-level policy is more ergonomic than per-tool.

### Lesson 3: chat commands as a surface

OpenClaw's `/status`, `/think <level>` etc. are *operator-typed
commands* — not LLM-invoked tools.

Ember's Munnr already has some commands (`/help`, slash commands
planned). The pattern is sound.

For Stofa (planned TUI): slash commands become first-class
surfaces. We can borrow OpenClaw's vocabulary patterns.

---

## What Ember has that OpenClaw doesn't

A few patterns where Ember is *ahead*:

### 1. Typed-value-over-exception tool returns

Ember's `ToolReply.error` is a *typed value*. OpenClaw (in TS)
likely throws or returns error-shape objects. Both work; Ember's
is more explicit and audit-friendly.

### 2. Audit log as cited surface

Every Ember tool call lands in audit log with full operator-
visible record. OpenClaw has audit logging but it's more
behind-the-scenes.

### 3. Robots.txt respect for `fetch_url`

Ember's `fetch_url` checks robots.txt. OpenClaw's `browser` is
broader (full headless browsing), so the respect-rules question
is more complex. Ember's narrower tool is more conservative.

These are *aesthetic choices*; OpenClaw's choices are also valid
for their cohort.

---

## What Ember should borrow

🟢 **Adapt to Ember Vows**:

### 1. Sandbox modes

Currently Ember has per-tool sandbox (`read_local_file` has
`sandbox_root`, `fetch_url` has `allow_private`, etc.). We could
add a *category-level* sandbox-mode setting (`main` / `restricted`
/ `none`).

### 2. Process tools (with sandbox)

Operators on LARGE profiles often want `run_shell_command`. We can
ship it with:
- PER_CALL approval default.
- Sandbox path restriction (only run inside operator's project
  dir).
- Allowlist of commands by default (no `rm -rf`).
- Operator can elevate to STANDING with care.

### 3. Cron tool (Phase 4+)

When the daemon mode lands, scheduled tasks become viable. "Remind
me X at Y" is a common operator request.

### 4. Sessions management as commands

`/sessions list`, `/sessions switch <id>`, etc. give operators
direct control. Stofa can render these as a panel.

---

## What Ember should NOT borrow

🔴 **Reject**:

### 1. Channel-specific tools

OpenClaw's `discord` + `slack` tools (post to channel, react,
etc.) make sense for OpenClaw's bridges-first design. Ember's
bridges don't exist (yet), so these tools aren't applicable.

When/if bridges land (Phase 4+), per-channel tools can come with
them — but only operator-opted-in.

### 2. Full headless browser

OpenClaw's `browser` tool is full headless web automation
(navigate, click, fill forms). Ember's `fetch_url` is narrower
(one-shot HTML fetch).

A full headless browser is *huge* (hundreds of MB) and has security
implications (JavaScript execution surface). Stays out of core
Ember; if needed, ships as `ember-agent[browser]` extra requiring
explicit operator opt-in.

🟡 **Defer**:

### 3. Canvas tools

Live Canvas in OpenClaw lets the agent render UI elements. Cool;
not needed for Ember V1-V3. Defer to V5+ when Auga lands.

---

## The "tools as plugins" question

OpenClaw allows third-party tool plugins (via extensions/ folder
in dev mode; ClawHub registry for prod).

Ember currently doesn't have a plugin model. Tools ship in core
or in operator-customized scripts.

**Should Ember add a plugin model?**

🟡 **Defer.** The Vow of Modular Authorship favors operator-
curated, not centralized-marketplaces. A plugin model could
either:

- **Lean into Modular Authorship**: any pip package can register
  tools. Operator-curated. No central registry.
- **Mimic ClawHub**: central registry. Discoverability. Quality
  curation by maintainers.

The first is closer to Ember's Vows. We *could* document it (any
Python package implementing the tool Protocol can be imported and
register tools), but we don't *advertise* this as a primary
extension path until we know what operators actually want.

---

## Closing

OpenClaw's tool ecosystem is **broader by default** than Ember's.
That's appropriate for their cohort (web-savvy operators wanting
turnkey capability).

Ember's tool ecosystem is **narrower by default** because the Vow
of Tethered Grounding + Vow of Public-Friendliness means each
tool must be *audit-friendly + sandbox-friendly + operator-
understandable* before shipping.

Lessons:
1. Ship categories of tool, not just individual tools.
2. Add a `process` tool family with strong sandbox.
3. Add a cron tool when daemon mode lands.
4. Keep channel-specific tools out of core.
5. Document but don't advertise plugin patterns.

OpenClaw's ecosystem is a *target* and a *cautionary tale*. We
borrow the structure; we keep the discipline.
