# 41 — Hick's Law and Menus

## The classical law

**Hick's Law** (William Hick, 1952; Ray Hyman, 1953): the time to
make a decision is a logarithmic function of the number of choices.

$$T = b \cdot \log_2(n + 1)$$

The more options, the slower the operator chooses. *Doubling* options
adds a constant amount of time (not double the time), so the cost is
sub-linear — but it's positive.

For TUIs, this means:

- A menu of 5 items is much faster than a menu of 50.
- A flat list of 50 items is slower than a hierarchical menu (5 of 10).
- A menu where the first item is "what 80% of operators want" is
  fastest of all.

## Hick's Law and Stofa

### The 4-panel HomeScreen

The HomeScreen has exactly **4 panels**. Operators see:

1. Conversation
2. Well
3. Realms
4. Tools

Each clearly named, clearly bordered. The operator's eye picks the
right one in roughly the same time as picking from a menu of 4 items.

Why not 6 panels? Or 8? Hick's Law: more options → slower decision.
We pick 4 because:

- 4 fits cleanly in a 2×2 grid.
- 4 covers the core operator interests (chat, knowledge, health,
  capability).
- A 5th panel would force a 2×3 or 3×2 grid, which is uglier and
  no faster to scan.

### The keymap is also Hicks-constrained

Stofa's *visible* keybindings (per `?`) cluster at:

- Global: ~10 keys (`?`, `q`, `Esc`, `:`, `Ctrl-P`, `p`, `Ctrl-T`,
  `r`, `h`, navigation arrows).
- Screen-specific: ~5-8 keys per screen.

The operator never has more than ~15 keys to consider at once.

Compare neovim's normal-mode default: ~80 keys without plugins.
The cognitive cost of "what was the right key for this?" is high.
We pay this cost intentionally on the operator's first day; they
should not pay it forever.

### The command palette as escape from Hick's tax

For long-tail actions, the command palette is fuzzy-search instead
of menu-pick. The operator types what they want (`:thm aurora`) and
the matches narrow. This **doesn't** scale logarithmically with menu
size; it scales linearly with how-distinctive the operator's typed
characters are.

Result: 200 named actions in the palette feel as fast as 10, because
the operator never sees all 200 at once.

### Settings sections are collapsible

The SettingsScreen has ~6 sections (Identity / Funi / Brunnr / Tools
/ MCP / Stofa). Each is collapsible. Default state: all collapsed.

Why? Operator opens settings to change *one* thing, usually. Having
50 settings visible at once is Hick's-Law-bad. Collapsible sections
make the operator's choice "which section?" (6 options) then "which
field?" (a few per section). Two cheap decisions instead of one
expensive one.

## Practical consequences

### Defaults that work for 80%

If 80% of operators want a particular default, that default goes
first. The most common picks in Settings:

- **Theme:** Aurora (the cozy default).
- **Start screen:** home.
- **Pets:** enabled.

These three are the defaults. Operators who want differently change
them; operators who want defaults don't have to think.

### Recently-used / recommended ordering

In the command palette, recently-used commands rank higher in the
result list. Operators who use `:theme midgard` once see it at the
top next time they type `:theme`. This shrinks the effective
menu-size to 1-2.

### No "Are you sure?" for non-destructive actions

Hick's Law applies to confirmation dialogs too. Asking "Are you
sure?" doubles the decision cost. We only ask for *destructive*
actions:

- Delete a document.
- Force-quit a running ingest.
- Reset identity.

For non-destructive actions (theme change, screen jump, refresh),
no confirmation.

## The opposite of Hick's Law: when more options *help*

Sometimes more options are better — when the operator already knows
what they want and the options are searchable.

Example: the WellScreen sources panel. If the operator has 200
ingested documents, listing all 200 with a `/` search is *faster*
than navigating a hierarchy (because the operator can type the
document name and zero in).

The distinction:

- **Pick-from-menu** scenarios → fewer options is faster (Hick's).
- **Find-by-name** scenarios → comprehensive list + fuzzy search is
  faster.

Stofa uses both. The command palette is find-by-name. The HomeScreen
panels are pick-from-menu. Different shape, different optimization.

## Specific Stofa design choices

| Element | Choice | Hick's rationale |
|---|---|---|
| HomeScreen | 4 panels | 4 is fast to scan |
| Top-level screens | 5 (Chat/Well/Doctor/Settings/MCP) | < 7 is decision-fast |
| SettingsScreen sections | 6, collapsible | hierarchical reduces visible cost |
| Theme picker | 5 built-in (V1) | exhausts before fatigue |
| Pet types | 9, but most opt-in | configurable; defaults are 4 visible |
| Command palette | 100+ actions | search not menu; Hick's doesn't apply |
| Tool-approval choices | 3 (Approve / Always / Deny) | matches mental model |

## What we don't optimize

- **Power-user menus** — Sigrún the power-user can handle longer
  lists and we don't gate them. The plugin manager (V2) might list
  20 installed plugins; that's OK because plugin-management is rare
  and Sigrún chose to be there.

## Closing

Hick's Law tells us: when you give operators a menu, keep it small.
When you can replace the menu with a search, do. When you need a
big menu, make it hierarchical. Stofa applies all three: small
top-level menus (HomeScreen panels, navigation keys), search
(command palette, document filter), hierarchy (collapsible Settings
sections). The operator's decisions are always *as cheap as we can
make them*.
