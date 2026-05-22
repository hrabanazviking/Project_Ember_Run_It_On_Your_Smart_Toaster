# 15 — Sibling: Kista

> *"No king, no keeper."*

Encrypted credential vault. Fernet (AES-128-CBC + HMAC-SHA256).
8 entry types. No cloud. The operator's strong-chest.

---

## What it is

A Python CLI + library for storing secrets locally. From its
own README:

- **Fernet encryption** at rest.
- **8 entry types** — credentials, API keys, SSH keys,
  certificates, secure notes, TOTP secrets, software
  licenses, personal identities.
- **No cloud, no third parties, no subscription.**
- **CLI-first** with library interface for programmatic
  access.

The Old Norse word *kista* means *chest, coffer, strongbox* —
the box where the household keeps valuables.

---

## Why this sibling matters for Yggdrasil

Kista is the **secrets plane**. Without it, secrets live in:

- `ember.yaml` (plaintext — bad).
- Environment variables (better, but operator-managed).
- `~/.pgpass` (Postgres-specific).
- Keyring (OS-specific).

With Kista, every realm that needs a secret asks *Kista*. The
operator manages secrets in one place; realms get them on
demand; nothing is plaintext on disk.

---

## How Yggdrasil integrates Kista

### Integration role

Kista becomes the **canonical secret resolver** for every
realm in Yggdrasil:

- Brunnr (pgvector): password resolution via Kista (replacing
  the current `_secrets.py` resolver chain, or as a new
  preferred entry in it).
- MCP servers: API tokens, OAuth credentials.
- CloakBrowser: session cookies, authentication credentials.
- Bifrǫst: Qdrant credentials (if Qdrant is auth-protected).
- Future realms.

### Adapter shape

A `src/ember/yggdrasil/kista/` package:

- `client.py` — `KistaClient` that calls Kista's library
  interface.
- `bridge.py` — bridges Ember's secret-resolution requests
  (which currently go through `pgvector/secrets.py`'s
  resolver chain) to Kista.
- `bootstrap.py` — helper for first-time setup: the operator
  initializes Kista, the bridge migrates known secrets from
  env vars / `~/.pgpass` into Kista.

### Resolver chain integration

Current Brunnr-pgvector secret resolver chain (per
ADR-0010 §2.5):

1. Env var
2. Keyring
3. Mode-600 file
4. Final → typed Disconnected(AUTH_FAILED)

**Yggdrasil extends the chain**:

1. Env var
2. **Kista** (new)
3. Keyring (legacy)
4. Mode-600 file (legacy)
5. Final → Disconnected

Kista comes *before* keyring because keyring is OS-specific
and varies in availability; Kista is consistent across
platforms.

Operators who don't use Kista see no behavior change.
Operators who use Kista get their secrets resolved
preferentially through it.

### Per-realm secret namespaces

Each realm gets a namespace inside Kista:

```
ember/
  brunnr/
    pgvector_password
  funi/
    ollama_remote_token       # if Ollama is auth-protected
  mcp/
    github_token
    filesystem_unused
  cloakbrowser/
    proxy_username
    proxy_password
  bifrost/
    qdrant_password
```

This is operator-readable structure; they can
`kista list ember/brunnr/*` to see what Ember has access to.

### Configuration shape

```yaml
yggdrasil:
  kista:
    enabled: true
    vault_path: ~/.ember/kista.vault    # defaults; can be elsewhere
    namespace_prefix: ember              # all of Ember's keys under this
    bootstrap:
      migrate_from_env_vars: true        # one-shot import
      migrate_from_keyring: true
```

---

## Why this is a sovereignty-defining integration

**Before Kista**: An operator's `ember.yaml` either:
- Contains a plaintext password (insecure), OR
- References an env var (operator manages secrecy outside Ember).

**After Kista**: `ember.yaml` contains *references* to Kista
keys:

```yaml
brunnr:
  pgvector:
    url: postgres://postgres@gungnir:5432/knowledge
    password_ref: "kista://ember/brunnr/pgvector_password"
```

The reference is opaque. The actual secret lives in the
Fernet-encrypted vault. Ember asks Kista at startup;
gets the secret; passes to psycopg; psycopg connects; done.

**The operator's `ember.yaml` becomes shareable** (no
secrets in it). Versioning it in git is no longer a leak
risk.

---

## Risk / known issues

- **Kista master key management.** Operator's master key
  unlocks the vault. Losing it = losing all secrets. Same
  risk as any vault; documented in operator docs.
- **First-launch friction.** Operators who don't have Kista
  configured need a clear path. The bootstrap helper +
  Stofa's HjartaWizardScreen update will guide.
- **Multi-device secret sync.** Kista's vault lives on one
  device by default. Multi-device Yggdrasil Phase 4 needs to
  decide: replicate vault, or have each device with its own
  vault + same master key?

---

## Open questions for Phase 2 ratification

1. **Hardware-backed master key.** TPM / Secure Enclave for
   the master key would be ideal for laptop/desktop. Is
   Kista hardware-backed-capable today?
2. **Touch-to-unlock UX.** For frequent operations, prompting
   for the master key on every secret read is friction.
   Cache time? Stofa-integrated unlock?
3. **Backup / recovery.** Operator should be able to back up
   the vault to encrypted external storage. Kista supports
   this; Yggdrasil documentation needs to surface the right
   workflow.

---

## Test strategy

Phase 2 ships:

- **Unit tests** for `KistaClient` with mocked vault.
- **Integration tests** with a real Kista vault on a tmp
  directory — full lifecycle: init, add secret, retrieve,
  rotate.
- **Migration test** — env vars → Kista; verify the bootstrap
  helper moves credentials correctly.
- **Resolver chain test** — verify Brunnr-pgvector tries
  Kista first, falls back gracefully when Kista isn't
  available.

Tests in `tests/unit/test_yggdrasil_kista_client.py` and
`tests/integration/test_yggdrasil_kista_resolver.py`.

---

## Operator-facing example

Setup (one-shot at install):

```bash
kista init                           # creates vault, prompts for master key
ember yggdrasil kista bootstrap      # migrates known secrets in
# Now Ember can resolve passwords via Kista
```

Day-to-day:

```bash
ember chat                # works as before; Kista resolves secrets transparently
kista list ember/         # operator sees what Ember has access to
kista rotate ember/brunnr/pgvector_password   # change Postgres password
```

The chest is locked; Ember asks; the chest opens; secrets
flow; the chest closes. The operator is the keeper.

---

## Closing

Kista is *sovereignty's chest*. Without it, secrets leak
through cracks. With it, the operator owns every credential
their AI can touch, and no plaintext lives on disk.

This is the integration that lets operators *share their
`ember.yaml`* — by removing the only thing they couldn't
share before.
