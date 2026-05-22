# 33 — The Kista Secret Plane

How encrypted credentials flow through Yggdrasil. The
gatekeeper pattern applied to the whole constellation.

---

## The principle

Every secret in Yggdrasil flows through Kista. Operators
manage credentials in *one* encrypted vault; realms request
them on demand.

No plaintext credentials in:
- `ember.yaml`
- Process environment (except as a *fallback* resolver)
- Realm config files
- Audit log
- Stofa logs

---

## The architecture

```
                    ┌──────────────────────┐
                    │   Operator's actions │
                    │  (CLI / Stofa / etc.)│
                    └──────────┬───────────┘
                               │
                  ┌────────────▼─────────────┐
                  │  Kista vault              │
                  │  ~/.ember/kista.vault     │
                  │  Fernet-encrypted          │
                  └────────────┬─────────────┘
                               │
                               │ (resolves via)
                               ▼
                  ┌────────────────────────────┐
                  │   SecretResolver chain     │
                  │   ────────────────────     │
                  │   1. Env var (legacy)      │
                  │   2. Kista (primary)       │
                  │   3. Keyring (legacy)      │
                  │   4. File (legacy)         │
                  └────────────┬───────────────┘
                               │
              ┌────────────────┼────────────────┬──────────┐
              │                │                │          │
         ┌────▼────┐      ┌────▼────┐      ┌────▼────┐ ┌──▼──────┐
         │ Brunnr  │      │  MCP    │      │ Cloak-  │ │Bifrǫst  │
         │ pgvector│      │ Servers │      │ Browser │ │ Qdrant  │
         │ password│      │  tokens │      │ creds   │ │ password│
         └─────────┘      └─────────┘      └─────────┘ └─────────┘
```

Each realm requests its secret by *key*; the chain resolves;
Kista wins by default.

---

## Per-realm secret namespaces

Kista's namespace structure for Yggdrasil:

```
ember/
  brunnr/
    pgvector_password          # Postgres for pgvector
    mempalace_master_key       # if MemPalace requires
  bifrost/
    qdrant_password
  funi/
    ollama_remote_token        # if Ollama is auth-protected
  mcp/
    github_token
    aws_session_token
    custom_server_X_key
  cloakbrowser/
    proxy_username
    proxy_password
    site_X_session_cookie      # per-site if needed
  yggdrasil/
    verdandi_socket_token      # if Verdandi has auth
    kista_self_unlock_hint     # operator-supplied
```

Operators can `kista list ember/*` to see what secrets Ember
references. They can `kista rotate ember/brunnr/pgvector_password`
to change the underlying value without editing `ember.yaml`.

---

## How secret references work in `ember.yaml`

The reference syntax is opaque:

```yaml
brunnr:
  pgvector:
    url: postgres://postgres@gungnir:5432/knowledge
    password_ref: "kista://ember/brunnr/pgvector_password"

mcp:
  servers:
    - name: github
      command: docker
      args: ["run", "..."]
      env:
        GITHUB_TOKEN: "kista://ember/mcp/github_token"
```

The `kista://` URI scheme tells the config loader to defer
resolution to the SecretResolver chain (with Kista preferred).
At runtime, the actual secret is fetched once and held in
process memory only (never written to disk unencrypted).

---

## The unlock flow

Kista's vault is encrypted with the operator's master key.
Three flows for unlocking:

### 1. Interactive (operator at the terminal)

First chat-launch of the day:

```
$ ember tui
Stofa is opening...
Kista needs to unlock for this session.
Master key: [hidden prompt]
✓ Unlocked. Vault stays open until Stofa quits.
```

The operator types their key once; it stays in process
memory for the session.

### 2. SSH-friendly (operator on a Pi via SSH)

Same as #1, with the prompt routed through SSH.

### 3. Cached / persistent (operator-configured)

For headless operations (cron jobs, daemons):

- Master key stored in OS keyring (macOS Keychain, Linux
  secret-service).
- OR master key in a hardware security key (TPM, Secure
  Enclave) — if Kista supports.
- OR ephemeral access token (Kista provides; expires).

Operator picks per their threat model.

---

## What happens when a secret isn't in Kista

The resolver chain falls through:

```python
# Resolver chain:
# 1. Env var EMBER_WELL_PASSWORD
# 2. Kista lookup
# 3. Keyring lookup
# 4. ~/.ember/secrets/well.password file
# 5. None — caller handles as Disconnected(AUTH_FAILED)
```

So operators who *haven't* migrated to Kista see no change
— their existing env-var / keyring / file setup still works.
Kista is *the new preferred resolver*, not the only one.

---

## What Kista replaces

Yggdrasil Phase 2 ships:

### `pgvector/secrets.py` resolver chain → generalized

The current pgvector-specific chain becomes the
Yggdrasil-wide `SecretResolver` chain. All realms that
needed credentials migrate to use it.

### Plaintext env-vars → Kista keys

Operators who currently have `EMBER_WELL_PASSWORD=hunter2`
in their `.bashrc` get a migration helper:

```bash
ember yggdrasil kista bootstrap
# Reads env vars matching Ember-known names
# Stores in Kista under appropriate namespaces
# Suggests removing them from .bashrc
```

### MCP server env vars → Kista refs

Current:
```yaml
mcp:
  servers:
    - env:
        GITHUB_TOKEN: "${GITHUB_TOKEN}"   # operator manages
```

After Phase 2:
```yaml
mcp:
  servers:
    - env:
        GITHUB_TOKEN: "kista://ember/mcp/github_token"
```

---

## Security properties

What Kista mediation gives us:

- **Vault is encrypted at rest.** Fernet (AES-128-CBC +
  HMAC-SHA256).
- **Master key never persists in plaintext.** Held in
  operator memory or hardware token.
- **`ember.yaml` is shareable.** No secrets in it.
- **Audit log records *which* secret was accessed, never
  the value.**
- **Failed Kista unlock = no realms requiring secrets.**
  Ember boots in limited-functionality mode (chat works with
  any secrets-free Funi runtime; Brunnr disconnected if it
  needed a password).

What Kista mediation does NOT give us:

- **Protection against an attacker with operator-process
  access.** Once the master key is in process memory, an
  attacker who can read process memory can extract secrets.
  Same as any in-memory key system.
- **Protection against a malicious sibling project.**
  Sibling projects that go rogue can read the secrets they're
  given. (Standard threat model: install trusted siblings
  only.)

---

## How Kista interacts with the Vow of Sovereignty

Kista *strengthens* sovereignty:

- **Before**: secrets in env vars / .bashrc / scattered
  config files — operator has to manually audit "what does
  Ember have access to."
- **After**: `kista list ember/*` shows everything. Single
  source of truth.

The Vow says operators own their AI. Kista makes "what your
AI knows / can do" visible and controllable.

---

## Open questions for Phase 2

1. **Master key rotation.** Kista supports key rotation —
   how does Yggdrasil surface the right flow?
2. **Backup encryption.** Kista vault on operator's main
   disk is one copy; backup is the second. Should backups
   be encrypted with the same key or a separate "recovery"
   key?
3. **Cross-device vault sync** (Phase 4 multi-device).
   Each device has its own Kista vault; sync via
   operator-controlled mechanism (tailnet rsync,
   manual copy, etc.). No central key server.

---

## Operator-facing example

Phase-2 onboarding for an operator with existing setup:

```bash
$ ember yggdrasil kista bootstrap
Found 3 secrets in your environment:
  EMBER_WELL_PASSWORD (used by: brunnr.pgvector)
  GITHUB_TOKEN (used by: mcp.servers.github)
  OLLAMA_API_KEY (used by: funi.ollama)

Move these to Kista? [Y/n] y

✓ Stored as: ember/brunnr/pgvector_password
✓ Stored as: ember/mcp/github_token
✓ Stored as: ember/funi/ollama_api_key

Updated ember.yaml to reference Kista keys.

Remove the env vars from your shell startup? [Y/n] y
(modified ~/.bashrc — backup at ~/.bashrc.ember-backup)
```

A clean migration in three prompts. After this, operator's
`ember.yaml` is shareable, their secrets are in one place,
and their `.bashrc` is cleaner.

---

## Closing

The Kista secret plane is **the gatekeeper of the
constellation**. Every credential flows through it. Operators
get visibility, encryption, and rotation in one place.
Realms get clean secret-resolution without having to
implement their own credential management.

This is sovereignty as infrastructure.
