# E-026 — Tools discipline: inventory, permission shapes, gates

*Slice E-026 of the Project Ember roadmap (Part II): the core's
tools inventoried; each tool's permission shape stated;
dangerous-by-default tools gated.*

## The plain truth first

Ember's companion can use exactly **three built-in tools**, and
only when the operator has switched tools on at all
(`tools.enabled`, off by default). Before this slice, the only
permission fact any tool stated was *how often the operator is
asked* — and two quiet holes sat underneath that: the operator's
"trust everything" switch silently overrode their own per-tool
"forbidden" setting, and the one tool that can reach the
operator's private network took the key to that gate
(`allow_private_addresses`) from the *model's* arguments, where
blanket approval could wave it through unseen. Now **every tool
states what it can reach** (its access class), the dangerous
classes can never be auto-approved by any blanket mechanism, a
call carrying a reach-widening argument always prompts, and the
operator's specific refusal always beats their general trust.

## What stood before (the map this slice builds on)

- The framework (ADR 0011): a process-global registry, per-tool
  `ToolDescriptor` (name, description, parameter schema,
  `required_approval`, redacted args, timeout), approval
  resolution in `spark/funi/tools/approval.py`, and a JSONL audit
  log. Chat's tool loop resolves each proposed call through
  descriptor policy → config overrides → session "always" →
  interactive prompt.
- The three first-party tools (Phase 15): `search_well`
  (STANDING), `read_local_file` (PER_CALL, HOME-sandboxed with a
  secret-path denylist, 256 KiB cap), `fetch_url` (PER_CALL,
  public-web sandbox: no credentials in URLs, private/loopback
  refused unless `allow_private_addresses`, robots.txt honoured,
  no redirects, 1 MiB cap).
- Two further tool surfaces exist outside that loop, inventoried
  honestly in §4: MCP-bridged tools (registered for listing; not
  wired into chat's approval loop today) and Ember's own MCP
  *server* tools (`search_well`, `well_status`, `doctor`,
  exposed only by an explicit `ember mcp serve`).

## 1. The inventory (proven by test, from the registry)

| Tool | Access | Approval | Auto-approvable? | Guarded arguments | Timeout |
|---|---|---|---|---|---|
| `search_well` | `private_read` | standing | yes (class) | — | 15 s |
| `read_local_file` | `private_read` | per_call | yes (class); policy still asks | — | 5 s |
| `fetch_url` | `network` | per_call | **no** | `allow_private_addresses` | 15 s |

`tool_inventory()` (`ember.spark.funi.tools.permissions`) projects
every registered descriptor onto its `ToolPermissionShape`
(name, access, declared approval, auto-approvable, guarded
arguments, timeout); the E-026 tests pin the table above from the
live registry, so a future tool that registers without stating
its shape — or a first-party tool whose shape drifts — fails the
suite. No first-party tool is `write`, `execute`, `external`, or
unspecified: the companion today can read its person's Well and
home files (sandboxed) and fetch public web pages, and can
**change nothing** on the machine.

## 2. Permission shapes (`ToolAccess`, on every descriptor)

`ember.schemas.tool.ToolAccess` states what a tool can reach,
independent of how often the operator is asked:

- `read_only` — reads non-private data; no writes, no egress.
- `private_read` — reads the operator's own data; no writes, no
  egress.
- `network` — leaves the machine (egress / SSRF surface).
- `write` — mutates local state.
- `execute` — runs code or commands.
- `external` — effects delegated to an external server, unknown
  from the tool's schema (the MCP shape).
- `unspecified` — **the default.** A descriptor that states no
  shape is gated as dangerous: no stated shape, no standing
  approval. Failing closed is deliberate — the alternative
  (forgetting to declare means read-only) would reward silence.

`ToolDescriptor` gains `access` (default `unspecified`) and
`guarded_arguments` (default empty): the names of arguments that
*widen* the tool's reach beyond its stated sandbox. A guarded
argument must default falsy (pinned for `fetch_url`: its
`allow_private_addresses` parameter defaults to `False`).

## 3. The gate (one wall: approval resolution)

`approval.resolve()` now resolves in this order:

1. **Forbidden wins, specifically.** A descriptor `FORBIDDEN`,
   or a config `approval_overrides` entry of `forbidden` for
   that tool, refuses the call — checked *before* every blanket
   mechanism (see the defect in §5).
2. **The E-026 gate.** If the tool's access class is dangerous
   or unspecified (`network` / `write` / `execute` / `external`
   / `unspecified`), or the call carries a truthy guarded
   argument, the call **prompts per call** — descriptor
   `STANDING`, a session "always", and `standing_trust` are all
   powerless to wave it through. Chat passes the call's own
   arguments into `resolve()` so this check sees the actual call.
   (For a dangerous tool, an operator's "always" answer still
   approves that one call; it simply never promotes.)
3. `standing_trust` auto-approves (within the gate).
4. Descriptor `STANDING` auto-approves (config may still
   downgrade it to per-call, never the reverse — the pre-E-026
   floor rule, unchanged).
5. Session "always" auto-approves (within the gate).
6. Otherwise the call prompts.

`ToolsConfig.standing_trust`'s documentation and the example
config now state the gated truth: the knob auto-approves
read-class tools; dangerous-class tools and guarded arguments
always prompt anyway.

## 4. The other surfaces, stated honestly

- **MCP-bridged tools** (`ember.mcp.bridge`): their descriptors
  now state `access=external`. A server's `auto_approve` list
  still lifts a named tool's *descriptor* to `STANDING` (the
  operator named that tool in their config), but the gate will
  not honour auto-approval for an `external` tool — if these
  tools are ever wired into a live approval loop, each call
  prompts. Today they are registered only for `ember mcp tools`
  listing, not executed through chat (E-019's map); bridge
  pairing / permissions / kill-switch are Part VIII's E-130.
- **Ember's own MCP server** (`ember mcp serve`): exposes
  `search_well`, `well_status`, `doctor` — all read-only
  (Well search + diagnostics). It runs only when the operator
  invokes it (`mcp.expose_self` defaults off); approvals on
  that side belong to the calling MCP host, not Ember's
  framework. Stated here so the inventory is complete, not
  because this slice changes it.

## 5. Defects found and fixed in scope

1. **`standing_trust` overrode a config `forbidden`.**
   `resolve()` checked the trust knob (old step 2) before the
   config override (old step 3), so an operator who set
   `standing_trust: true` *and* `approval_overrides:
   {fetch_url: forbidden}` got fetch_url auto-approved — the
   specific refusal silently lost to the blanket trust. Fixed
   by the new order (§3 step 1); regression-pinned by
   `test_config_forbidden_beats_standing_trust`.
2. **The private-network escape hatch was model-supplied and
   blanket-waivable.** `fetch_url`'s `allow_private_addresses`
   arrives in the model's arguments; under `standing_trust` or
   a session "always" for fetch_url, a call could set it and
   reach loopback/RFC1918 addresses with no prompt at all.
   Fixed by the guarded-argument gate + fetch_url's `network`
   class (it now always prompts, flag or no flag); the executor's
   own sandbox semantics are unchanged (per-call approval is
   where the operator sees the exact URL and flag).
3. **Pinned tests updated with attribution.** Three approval
   tests and the Phase-16 loop test asserted auto-approval for
   descriptors that stated no access class; under the gate they
   now declare the safe class their tool represents
   (`private_read` / `read_only`), with E-026 comments at each
   site. Their assertions are unchanged.

## 6. What this slice does not do

- **E-027 owns the approval *shape* for normal folks** — plain
  words and rememberable scopes. This slice states and enforces
  the permission facts that shape will present; the prompt text
  itself is unchanged.
- No new tools, no write/execute tool, no change to any tool's
  sandbox or executor behaviour, no change to the audit log's
  shape. The registry still refuses `FORBIDDEN` descriptors at
  registration, unchanged.
- MCP bridge execution through chat, and bridge security
  (pairing, per-bridge permissions, kill switch), remain
  Part VIII (E-125/E-130), as roaded.

## 7. Tests and gates (counts from the runner)

- New: `tests/unit/test_tools_discipline_e026.py` — **31 passed**
  (inventory pins from the live registry, the gate matrix over
  access classes × trust/session/standing, the forbidden-beats-
  trust regression, guarded-argument truthy/falsy/absent,
  the real `fetch_url` descriptor under trust + session,
  MCP `external` shape).
- Slice gate Run B (default env, pgvector file excluded):
  **708 passed, 6 failed, 13 skipped, 1 warning** — 677 E-025
  baseline + 31 new; the 6 are the proven environment failures.
- Run D (whole suite, extras supplied): **749 passed, 0 failed,
  19 skipped, 1 warning**, exit 0.
- No README touched.
