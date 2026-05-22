# 64 — Offline Mode Guarantees

What works without network. The Vow of Graceful Offline,
made concrete across every realm.

---

## The principle

Per the Vow of Graceful Offline + sovereign-by-default:
**Ember must work without network access**. Period.

Tested: pull the ethernet cable; turn off wifi; what
breaks?

Answer (in Yggdrasil): almost nothing.

---

## What's offline-capable by default

| Feature | Offline? | Notes |
|---|---|---|
| Chat with Funi | yes | local LLM via Ollama |
| Memory retrieval (Brunnr + Mímir + Huginn + Muninn) | yes | all local |
| Memory storage | yes | all local |
| Stofa TUI | yes | local |
| Episode persistence | yes | local SQLite |
| Self-awareness | yes | local Verdandi |
| Emotional intelligence | yes | local rule-based |
| Dreamstate | yes | local |
| Audit | yes | local |
| Snapshots (Norns) | yes | local disk |
| Seiðr verse generation | yes | local |
| Astrology rhythm | yes | Swiss Ephemeris is local |
| Kista secret resolution | yes | local vault |

Default: 100% offline-capable for the *core agent*.

---

## What requires network (and degrades gracefully when offline)

| Feature | Network need | Offline behavior |
|---|---|---|
| Tool calls to web | yes | tool returns Disconnected; chat continues |
| CloakBrowser fetches | yes | returns Disconnected |
| MCP servers (network-bound) | depends on server | typed Disconnected; chat says "I can't reach X right now" |
| Curiosity-driven ingest | yes | suggestion still shown; "fetch" deferred |
| Federation (Phase 4) | yes | local-only mode; reconciles when network returns |

Each of these:
1. Detects the network failure.
2. Returns typed Unavailable / Disconnected.
3. Surfaces to operator gracefully.
4. Continues local-only operation.

---

## How offline mode is tested

CI runs:
- Disable network in the test container.
- Run full chat test suite.
- Verify all "local-only" tests pass.
- Verify "network" tests return appropriate typed-error.

Tests:
- `tests/integration/test_yggdrasil_offline_full.py`
- `tests/integration/test_yggdrasil_offline_network_tools_fail.py`

---

## What operators experience offline

### Day-to-day

Operator opens Stofa on a plane:
- Chat works.
- Memory works.
- Awareness works.
- No "you're offline" annoying banner.

### When operator tries a web tool

```
> volmarr: fetch https://example.com/article and summarize

ember: I can't reach the web right now (network appears
to be offline). Want me to queue this fetch for when you're
back online?

> volmarr: yes

[ember queues the request via Verdandi]
[when network returns, the reconciliation worker
notices, surfaces: "I have a queued fetch from earlier
— shall I run it now?"]
```

Offline doesn't mean *abandon the operator*; it means
*adapt*.

### When MCP server is unreachable

```
[operator asked about something a remote MCP tool would handle]

ember: I noticed my MCP connection to <server> is down.
I can still help based on my local memory; let me know if
you want me to retry the connection.
```

Operator gets clarity; system continues.

---

## The "fully sovereign" stance

Yggdrasil's default deployment:
- **No telemetry** sent anywhere.
- **No license checks** phoning home.
- **No "cloud features"** that secretly require a server.
- **No fonts / icons / assets** fetched from CDNs.

Everything operator-facing ships with Ember (or sibling
packages). When operator is offline, *nothing fails
because of missing remote resources*.

The few things that ship as separate downloads (LLM model
weights, Astronomy ephemeris files) are operator-installed
once + cached forever; subsequent offline use works.

---

## Configuration shape (offline assertions)

```yaml
yggdrasil:
  offline:
    assert_no_remote_calls_at_boot: true
    log_any_remote_attempts: true   # surface accidental dependencies
    block_remote_calls: false       # too aggressive for normal use
```

CI test: with `assert_no_remote_calls_at_boot: true`,
Yggdrasil's boot sequence makes ZERO network requests.
Verifiable + enforceable.

---

## What happens when network *partially* fails

Common case: DNS works; HTTPS broken (corporate proxy
interception, expired certs). Or vice versa.

Yggdrasil treats partial network as offline:
- Tools tried; tools fail; tools return Disconnected.
- Local features continue.
- Doctor screen distinguishes "network: detected; remote
  endpoints: unreachable."

No subtle "well, DNS works so maybe…" hopeful retries.
If a specific endpoint fails, *fail typed*, continue.

---

## Offline as a default state

Yggdrasil does not assume the operator is online unless
told. There is no:
- "Welcome to Ember! Connecting…" loading state.
- "Sync with cloud" toggle.
- "Logging in to your account" first-run flow.

There is no account. There is no cloud. There is just
the operator's machine + Ember.

If the operator wants remote features (federation, MCP,
web tools), they configure them. Until then: offline by
default.

---

## What this enables

### Air-gapped operation

Some operators (researchers, those handling sensitive
data, those in restricted environments) need Ember to run
on a completely network-isolated machine.

Yggdrasil supports this *by default*. No special "air-
gapped mode" flag.

### Privacy-preserving operation

Operator's chats stay on their machine. Operator's notes
stay in their Well. Operator's identity stays in
identity.json on disk. Nothing leaks because nothing tries
to leave.

### Resilient operation

Network outages don't destroy the work session. Operator
keeps thinking, keeps chatting, keeps building.

### Travel operation

Plane, train, off-grid cabin — Ember works.

---

## What's harder when offline

Some operations are *naturally* network-bound:
- Looking up current events.
- Fetching new web content.
- Connecting to remote MCP servers.
- Federating with off-network nodes.

Yggdrasil doesn't pretend these work offline. They fail
*clearly* with operator-actionable next steps.

What we *don't* do:
- Cache stale web content and pretend it's current.
- Lie about being online.
- Hide the network state from the operator.

---

## How offline interacts with federation

Phase 4 federation (multiple Ember nodes coordinating):
- Each node operates *locally* by default.
- When network is up, nodes gossip + sync.
- When network is down, each node continues *independently*.
- When network returns, divergent state reconciles per
  the receipts pattern.

Federation is *additive* to offline operation, not
replacing it. A federated Ember that loses network is
just a *non-federated* Ember temporarily.

---

## Configuration shape (full)

```yaml
yggdrasil:
  offline:
    # Assertions for the paranoid
    assert_no_remote_calls_at_boot: true
    
    # Logging
    log_remote_attempts: true        # all outbound attempts go to audit
    
    # Behavior
    queue_failed_web_calls: true     # offer to retry later
    
    # UI
    show_offline_banner: minimal     # subtle indicator vs alarming banner
    
    # Time-since-last-online
    track: true                      # operator can see "online 3 hours ago"
```

---

## Closing

Offline Mode Guarantees make Yggdrasil **trustworthy in
any network condition**. Operators on planes, in
basements, off-grid, in privacy-sensitive contexts — all
get a full-featured Ember.

The Vow of Graceful Offline isn't aspirational. It's
*tested in CI*, *honored by every realm*, *the default
mode*.

This is what sovereignty actually requires.
