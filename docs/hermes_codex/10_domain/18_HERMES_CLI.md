---
codex_id: 18_HERMES_CLI
title: The CLI — Six Hundred Sixty-Two Kilobytes of Mouth
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - cli.py:1-200
  - cli.py:2602-2700
  - cli.py:5617-5700
  - cli.py:7806-7900
  - cli.py:14203-14560
  - hermes_cli/commands.py:1-60
  - hermes_cli/main.py
  - hermes_cli/proxy/__init__.py
  - hermes_cli/proxy/server.py
  - hermes_cli/proxy/cli.py
  - hermes_cli/proxy/adapters/base.py
  - hermes_cli/proxy/adapters/nous_portal.py
  - hermes_cli/proxy/adapters/xai.py
  - hermes_cli/setup.py
  - hermes_cli/doctor.py
  - hermes_cli/profiles.py
  - hermes_cli/config.py
  - hermes_cli/skin_engine.py
  - hermes_cli/curses_ui.py
  - hermes_cli/tools_config.py
  - hermes_cli/auth.py
  - hermes_cli/banner.py
  - hermes_cli/web_server.py
  - hermes_cli/pty_bridge.py
  - hermes_cli/main.py
  - AGENTS.md:143-261
  - AGENTS.md:947-1000
ember_subsystem_targets: [Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/19_BOUNDARY_LAW
  - 30_execution/39_INTERRUPT_MULTILINE_TUI
  - 50_verification/53_CRASH_PROOFING_PATTERNS
---

# The CLI — Six Hundred Sixty-Two Kilobytes of Mouth

*— Rúnhild Svartdóttir, Architect*

> *Every system grows a mouth. The discipline is in how the mouth stays sized to the body, not the body sized to the mouth. When the mouth exceeds the throat, the system speaks with its weight rather than its voice.*

`cli.py` is 662,814 bytes. Eleven thousand lines. Sixty top-level functions and one class (`HermesCLI` at `cli.py:2602`) with about a hundred and twenty methods. It is — by a substantial margin — the single largest Python file in Hermes. It is the load-bearing implementation of the interactive surface; it has been growing for years; and it is the most architecturally honest thing in the system, because it shows you exactly what happens when a surface keeps absorbing responsibilities without anyone breaking it up.

The mental model: **one CLI class, one slash-command registry, ninety supporting modules in `hermes_cli/`, and a proxy subsystem for talking to other AI surfaces (Nous Portal, xAI's UI).**

This doc is the autopsy.

---

## 1. The Anatomy of cli.py

`cli.py` has two parts: a thousand-line preamble of top-level functions and helpers, and a 9,000-line `HermesCLI` class.

The preamble (rough breakdown):

| Lines | Section |
|---|---|
| 1-128 | Imports, `_strip_reasoning_tags`, basic message helpers |
| 130-272 | Config loading, prefill helpers, parsing helpers |
| 272-746 | `load_cli_config()` — merges hardcoded CLI defaults with the user YAML |
| 746-1306 | Worktree setup/cleanup, git utilities, state.db maintenance |
| 1307-1568 | Color/theme — hex→ANSI, OSC11 light-mode detection, skin-aware ANSI |
| 1569-1944 | `_SkinAwareAnsi` class, output history, `_cprint`, terminal width helpers |
| 1944-2367 | Path resolution, image attachment, prompt-toolkit keybindings, terminal-response strip |
| 2368-2436 | `ChatConsole` class — a thin wrapper for chat-style printing |
| 2437-2601 | Banner builder, slash-command detection, plugin-handler discovery |
| 2602+ | `HermesCLI` class |

Inside `HermesCLI`, the bulk:

| Method type | Examples | Approximate line range |
|---|---|---|
| Setup | `__init__` (2610-3140), `_build_*`, `_setup_*` | 2602-3500 |
| Display | `_build_context_bar`, `_build_status_bar_text`, banner / panel rendering | 3140-3450 |
| Slash command handlers | `_handle_rollback`, `_handle_stop`, `_handle_paste`, `_handle_copy`, `_handle_image`, `_handle_tools`, `_handle_profile`, `_handle_handoff`, `_handle_resume`, `_handle_sessions`, `_handle_branch`, `_handle_model_*`, `_handle_codex_runtime`, `_handle_gquota`, `_handle_personality`, `_handle_cron`, `_handle_curator`, `_handle_kanban`, `_handle_skills`, `_handle_background`, `_handle_bundles`, `_handle_browser`, `_handle_goal`, `_handle_subgoal`, `_handle_skin`, `_handle_footer`, `_handle_reasoning`, `_handle_busy`, ... | 5036-9200+ |
| The dispatch | `process_command` (7806+) | one massive switch |
| `show_help` | 5617+ | help rendering |
| `run` | 11843+ | the actual interactive loop |
| Module-level `main` | 14203 | argparse entry point |

The architecture works *because* the slash-command registry (`hermes_cli/commands.py`) is centralized. The `CommandDef` dataclass (`hermes_cli/commands.py:45-58`) holds each command's metadata; every consumer (CLI dispatch, gateway dispatch, Telegram bot menu, Slack subcommand mapping, autocomplete) reads from `COMMAND_REGISTRY`. A single source of truth for the *what*; the *how* is in `cli.py:7806+ process_command`.

But the *how* is one giant if/elif chain. The chain dispatches to one of ~50 `_handle_<command>` methods. Each handler does its work inline within `HermesCLI`. The class therefore accumulates everything: model picker dialog, profile manager, kanban CLI, cron CLI, skill manager, snapshot rollback, codex runtime switch, browser tools UI, image-attachment workflow, paste handler, copy handler, footer toggling, skin switching, busy-state customization.

**This is the smell.** Each individual handler is small and competent. The class is enormous because it's the only home they have.

---

## 2. The Slash Command Registry

`hermes_cli/commands.py:45-58` defines `CommandDef`:

```python
@dataclass(frozen=True)
class CommandDef:
    name: str                          # canonical name without slash
    description: str
    category: str                      # "Session", "Configuration", etc.
    aliases: tuple[str, ...] = ()
    args_hint: str = ""                # placeholder: "<prompt>", "[name]"
    subcommands: tuple[str, ...] = ()  # tab-completable subcommands
    cli_only: bool = False
    gateway_only: bool = False
    gateway_config_gate: str | None = None  # config dotpath
```

Every command is one entry. Adding a command (per `AGENTS.md:164-180`):

1. Add a `CommandDef` to `COMMAND_REGISTRY`
2. Add a handler branch in `HermesCLI.process_command()`
3. If gateway-available, add a handler in `gateway/run.py`
4. For persistent settings, use `save_config_value()` in `cli.py`

Adding an alias is *just step 1* — the aliases tuple is consulted everywhere.

The categories (`Session`, `Configuration`, `Tools & Skills`, `Info`, `Exit`) feed `COMMANDS_BY_CATEGORY` for the help renderer. The flat dict `COMMANDS` feeds `SlashCommandCompleter` for autocomplete.

This is **excellent boundary discipline**. Without `COMMAND_REGISTRY`, adding a command would require editing six files (CLI dispatch, gateway dispatch, Telegram menu, Slack mapping, autocomplete, help). With it, you edit one. The architectural cost — one big handler class — is real, but contained.

The `gateway_config_gate` field is a small genius: a `cli_only` command can become gateway-available when a config key is truthy. The `GATEWAY_KNOWN_COMMANDS` frozenset always includes config-gated commands so the gateway can dispatch them; help/menus only show them when the gate is open. *Selective surface exposure based on configuration.*

---

## 3. The `hermes_cli/` Subdirectory

`hermes_cli/` has **89 files**. The role split:

### 3.1 The Setup/Doctor Layer
- `setup.py` — `hermes setup` wizard (interactive provider/model picker, env-var prompts)
- `doctor.py` — `hermes doctor` (one-shot health check: providers reachable? memory configured? plugins valid?)
- `auth.py`, `auth_commands.py` — credential store + OAuth flows
- `copilot_auth.py`, `dingtalk_auth.py`, `vercel_auth.py`, `slack_cli.py`, `xai_retirement.py` — provider-specific auth flows
- `dep_ensure.py` — runtime check-and-pip-install for optional deps (`tools/lazy_deps.py` ecosystem)

### 3.2 The Profile Layer
- `profiles.py` — multi-instance support; each profile has its own `HERMES_HOME`
- `profile_describer.py`, `profile_distribution.py` — profile metadata
- `inventory.py` — what's installed in this profile
- `migrate.py` — config migrations

### 3.3 The Slash-Command Implementations
- `commands.py` — the registry (see §2)
- `callbacks.py`, `cli_output.py`, `colors.py`, `banner.py` — display helpers
- `kanban.py`, `kanban_db.py`, `kanban_decompose.py`, `kanban_diagnostics.py`, `kanban_specify.py`, `kanban_swarm.py` — kanban CLI tree
- `cron.py`, `goals.py`, `curator.py` — agent lifecycle CLIs
- `gateway.py`, `gateway_windows.py` — gateway lifecycle
- `pairing.py`, `platforms.py` — gateway platform setup
- `bundles.py`, `inventory.py` — toolset bundles
- `models.py`, `model_catalog.py`, `model_normalize.py`, `model_switch.py`, `codex_models.py`, `codex_runtime_switch.py`, `codex_runtime_plugin_migration.py` — model picker
- `providers.py`, `runtime_provider.py` — provider switching
- `nous_subscription.py`, `azure_detect.py`, `security_advisories.py` — provider-specific UI
- `skills_config.py`, `skills_hub.py`, `tools_config.py` — toolset enable/disable

### 3.4 Settings & State
- `config.py` — `DEFAULT_CONFIG`, `load_config()`, config-version migrations
- `env_loader.py` — `.env` loader
- `secrets_cli.py` — secrets CLI
- `default_soul.py` — default `SOUL.md` content
- `tips.py` — startup hints

### 3.5 The TUI / Terminal Layer
- `curses_ui.py` — preferred menu UI (replaces `simple_term_menu`)
- `pt_input_extras.py` — prompt_toolkit extras
- `pty_bridge.py` — PTY bridge for dashboard embed
- `voice.py` — voice mode
- `clipboard.py`, `paste.py` (in cli.py), `claw.py` — paste/copy/clipboard helpers
- `skin_engine.py` — data-driven theming (the "skins" in `AGENTS.md:398-484`)

### 3.6 The Web Server
- `web_server.py` — `hermes dashboard` (FastAPI + Uvicorn SPA)
- `webhook.py` — webhook receivers

### 3.7 Recovery & Diagnostics
- `backup.py` — backup CLI
- `dump.py` — config dump
- `logs.py` — log viewer
- `debug.py` — debug commands
- `relaunch.py`, `uninstall.py` — lifecycle
- `checkpoints.py`, `session_recap.py` — session recovery

### 3.8 Subprocess & IO Compat
- `_subprocess_compat.py` — Windows hide-window flags, `signal.SIGINT` portability
- `_parser.py` — argparse helpers
- `stdio.py` — stdio handling
- `timeouts.py` — config-driven timeouts (`get_provider_request_timeout`, `get_provider_stale_timeout`)

### 3.9 Misc
- `tips.py`, `hooks.py`, `oneshot.py`, `send_cmd.py`, `fallback_cmd.py`, `status.py`, `plugins.py` (plugin manager), `plugins_cmd.py`, `mcp_config.py`, `memory_setup.py`, `browser_connect.py`, `completion.py`

### 3.10 The Proxy Subsystem (`hermes_cli/proxy/`)
- `proxy/__init__.py`, `proxy/server.py`, `proxy/cli.py`
- `proxy/adapters/base.py`, `proxy/adapters/nous_portal.py`, `proxy/adapters/xai.py`

The proxy is a separate concern: `hermes proxy` lets Hermes be a local OpenAI-API-compatible proxy in front of Nous Portal or xAI's UI. Useful when a tool expects an OpenAI endpoint but the user is paying a subscription. The adapter pattern here is `BaseAdapter` → per-vendor adapter. Cleaner code than `cli.py` because it was *built clean from the start* rather than accreted.

---

## 4. The Skin Engine

`hermes_cli/skin_engine.py` is a small, self-contained subsystem worth highlighting because it's the *opposite* of what `cli.py` became.

The skin engine (per `AGENTS.md:398-484`) is **pure data**:
- `SkinConfig` dataclass — colors, spinner faces/verbs/wings, tool prefix, response box, branding text
- Built-in skins: `default`, `ares`, `mono`, `slate`
- User skins as YAML at `~/.hermes/skins/<name>.yaml`
- `init_skin_from_config()` at CLI startup reads `display.skin` from config
- `set_active_skin(name)` switches at runtime via the `/skin` command
- Missing skin values inherit from `default` automatically

A *theme engine designed correctly*. No code change required to add a skin. The pattern is portable; the Ember question is whether a theme engine belongs on a Pi at all (Vow of Smallness suggests not).

---

## 5. The Dashboard Embed

`hermes_cli/web_server.py` + `hermes_cli/pty_bridge.py` are the "embedded `hermes --tui` inside a browser" layer. Per `AGENTS.md:248-260`:

- Browser loads `web/src/pages/ChatPage.tsx`, which mounts xterm.js's `Terminal` with the WebGL renderer
- `/api/pty?token=…` upgrades to a WebSocket; auth uses ephemeral `_SESSION_TOKEN` via query param
- Server spawns `hermes --tui` through `ptyprocess` (POSIX PTY — WSL works, native Windows does not)
- Resize via `\x1b[RESIZE:<cols>;<rows>]` intercepted on the server and applied with `TIOCSWINSZ`

**Do not re-implement the primary chat experience in React** is the architecture mandate. The chat is the TUI. The dashboard surrounds it with sidebar widgets, model picker dialog, tool-call inspector — but the actual chat surface is the embedded PTY.

The discipline: *one chat surface; many decorations.* Worth keeping in mind for any Ember equivalent.

---

## 6. The Recovery Patterns

Several cli.py functions deserve a callout because they encode hard-won wisdom:

### 6.1 `_setup_worktree` (`cli.py:865-1023`)

When Hermes is invoked from a git repo and the operator says "edit this file," Hermes can optionally set up a git worktree for the session. This isolates the session's edits from the operator's main checkout. `_cleanup_worktree` tears down at session end.

### 6.2 `_run_state_db_auto_maintenance` (`cli.py:1077-1130`)

On CLI startup: prune old sessions, VACUUM the SQLite, rebuild FTS5 if corrupted. Hermes maintains *itself*.

### 6.3 `_run_checkpoint_auto_maintenance` (`cli.py:1131-1154`)

Prune old checkpoints.

### 6.4 `_prune_stale_worktrees` (`cli.py:1155-1220`)

Worktrees from crashed sessions are detected and cleaned up after `max_age_hours = 24`.

### 6.5 `_prune_orphaned_branches` (`cli.py:1221-1306`)

Branches in a worktree that have no commits beyond `main` get pruned. The agent can leave many half-finished branches; Hermes cleans up its own droppings.

### 6.6 `_query_osc11_background` (`cli.py:1362-1423`)

Detects terminal background color via OSC 11. Used for light-mode auto-detection. Cross-platform fallback when the query fails.

### 6.7 `_detect_light_mode` (`cli.py:1424-1514`) + `_maybe_remap_for_light_mode` (`cli.py:1515-1532`)

Light-mode terminals get color remaps so the kawaii gold-on-black doesn't become gold-on-white (unreadable). Automatic.

These are the kind of details that get accreted in a monolithic CLI. Each is small. Each is correct. Each lives in `cli.py` because there is no obvious other home.

---

## 7. The Two Honest Pitfalls

`AGENTS.md:947-1000` lists several CLI-specific known pitfalls. Two architectural ones:

### 7.1 `\033[K` Leaks Under `prompt_toolkit`'s `patch_stdout`

ANSI erase-to-EOL leaks as literal `?[K` text when `prompt_toolkit` is patching stdout. Solution: space-padding (`f"\r{line}{' ' * pad}"`). This is the kind of cross-library detail that only emerges in production. Worth knowing.

### 7.2 `simple_term_menu` Has Ghost-Duplication in tmux/iTerm2

The CLI menu library Hermes started with has a rendering bug in some terminals. Hermes is **migrating to curses-stdlib UI** (`hermes_cli/curses_ui.py`). Existing call sites in `main.py` remain for legacy fallback only; new interactive menus must use curses. PR-level enforcement.

These pitfalls are documented in `AGENTS.md` because they bit someone. The discipline of writing them down — *explicitly forbidding* the broken pattern in the docs — is a strong cultural signal.

---

## 8. The Dashboard's Sidebar

`hermes_cli/web_server.py` exposes a REST API that the dashboard SPA (in `web/`) consumes. The chat itself is the embedded PTY (see §5); the sidebar widgets (model picker, sessions list, kanban board, achievements, plugin status) hit the REST API.

This *split* (REST sidebar + PTY chat) is architecturally interesting. The chat surface is reused (one mouth, multiple decorations). The sidebar is *aware of* the chat session via the same session ID. Status flows through; commands flow through; the user never has two competing chat surfaces to choose from.

---

## What This Means for Ember

Ember's Munnr is small today. Slice 2 ratification shipped Ember's CLI surface; it does *not* yet have ninety supporting modules. The Hermes CLI is what Munnr could grow into. The lesson is: *don't*.

### Concrete proposals

1. **Keep `cli.py` under 2000 lines forever.** Set this as a Vow-adjacent invariant. When a slash-command handler grows past ~50 lines, extract it. When the dispatch grows past 30 commands, split by category into separate handler modules. Hermes's `cli.py:7806+ process_command` is one switch with ~50 branches; Ember's should be a thin dispatcher to per-category handler modules. Cite `cli.py:7806+` as the cautionary tale.

2. **Adopt `CommandDef` + `COMMAND_REGISTRY` immediately.** When Ember's slash-command set grows past five, centralize. Same fields, same `gateway_*` flags (even though the gateway is OOS for Ember today, the discipline is portable). Cite `hermes_cli/commands.py:45-58`.

3. **Adopt the `hermes_cli/` subdirectory pattern** with `ember_cli/` (or `src/ember/spark/munnr/cli/`). Each concern (setup, doctor, profiles, config, theme, web-server, ...) goes in its own file. Avoid the `cli.py`-becomes-everything trap.

4. **Adopt `hermes doctor` exactly.** Ember already has `ember doctor`; reinforce. Plain-English output; one-shot health check; no log-spelunking required.

5. **Adopt `hermes setup` wizard discipline.** Interactive provider/model picker, env-var prompts. Hjarta already plays this role in Ember; the Hermes pattern shows the path forward when the wizard scales beyond the slice-2 single-provider flow.

6. **Adopt the curses-stdlib menu pattern from `hermes_cli/curses_ui.py`.** `simple_term_menu` is forbidden by Hermes's own AGENTS.md. Ember should not adopt simple_term_menu under any circumstance.

7. **Adopt the auto-maintenance patterns.** State-DB VACUUM, FTS5 rebuild, prune-stale-checkpoints — all of these are *background hygiene* the system does for itself on startup. Cite `cli.py:1077-1306`. **Vow of Honest Memory** through self-cleanup.

8. **Adopt the `_detect_light_mode` + remap pattern.** Operators on light-mode terminals are a real population. Five lines of OSC 11 probing plus a small color remap function. Cite `cli.py:1362-1532`.

9. **Refuse the dashboard for slice 1-N.** A FastAPI+SPA+xterm.js dashboard violates the Vow of Smallness for a Pi. The pattern (`hermes_cli/web_server.py` + PTY embed) is portable when Ember's hardware target broadens.

10. **Refuse the skin engine for slice 1-N.** Ember's Munnr should be plain. The four built-in skins of Hermes are charming and unnecessary on a Pi.

11. **Refuse the worktree pattern for slice 1-N.** Hermes's git-worktree session isolation is impressive but heavy. Ember's slice plan does not include git integration; defer.

12. **Adopt the *proxy* pattern's clean separation** (`hermes_cli/proxy/`) — small subsystem, BaseAdapter ABC, per-vendor adapter. When Ember gains a similar capability (e.g. an Ember-as-OpenAI-API-proxy for legacy tools), this is the shape.

**Affected True Names:** **Munnr** absorbs the role of `cli.py`. The Hermes path is *not* the path; Ember's Munnr stays small. The auxiliary modules — setup, doctor, config — are Munnr-adjacent (they configure the rest of the system) and belong in their own files within the Munnr realm.

**Vows reinforced (by refusing the bulk):**
- **Vow of Smallness** — small Munnr; small CLI file; small surface area.
- **Vow of the Unbroken Whole** — modular CLI handlers, not a 9000-line class.
- **Vow of Public-Friendliness** — `ember doctor` and `ember setup`.

**Vows at risk if Munnr grows like Hermes did:**
- **Vow of Smallness** — every file approaching 1000 lines is a warning.
- **Vow of Modular Authorship** — a 9000-line class is the antithesis.
- **Vow of the Unbroken Whole** — extracting handlers from `cli.py` after it has grown is a test-rewriting exercise (see `[[10_domain/11_AGENT_CORE]]` for the `_ra()` warning).

The mouth of a system speaks the system. When the mouth weighs more than the body, the system has become its own mouthpiece. Ember's mouth stays small — six hundred sixty-two kilobytes is not a target; it is a warning chiseled in stone.
