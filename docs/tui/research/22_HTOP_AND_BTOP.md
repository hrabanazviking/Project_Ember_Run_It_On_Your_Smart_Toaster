# 22 — htop and btop

> https://htop.dev/ · https://github.com/aristocratos/btop

Two system monitors. htop is the classic; btop is the modern beautiful
cousin. Together they teach Stofa about **live updates**, **animation
restraint**, and **dense-but-readable dashboards**.

---

## htop

### What it is

The interactive process viewer that replaced `top`. Shows CPU bars,
memory bars, swap, process list. Sort, filter, kill, renice — all
visible.

### The clever idea

**The dashboard format that everyone recognizes**. CPU bars at the
top (one per core), memory + swap, then the process list. You glance
at htop and *know* what's wrong, in 2-3 seconds.

The clever-er idea is that **the dashboard format teaches itself.**
A new operator sees the bars and the labels and immediately
understands "those are CPU cores; that's a bar." No tutorial needed.

### What we steal

1. **Section labels in fixed positions.** Stofa's HomeScreen has
   "Conversation / Well / Realms / Tools" panels in fixed 2×2 grid.
   Same intent: scan-readable status without navigation.
2. **The bottom-bar key legend.** htop's bottom bar lists F1-F10
   with current functions. Stofa's StatusBar does the same with
   contextual keys.
3. **One-color = one-meaning.** htop uses green for low, yellow for
   medium, red for high — same semantic on every bar. Stofa's
   five-color palette ([`../design/64_PALETTE_AURORA.md`](../design/64_PALETTE_AURORA.md))
   follows: `$success`, `$warning`, `$error` mean the same thing
   everywhere.

### What we avoid

1. **The 1-Hz full-screen refresh.** htop repaints everything every
   second, which is bandwidth-heavy and produces visible flicker on
   slow links. Stofa uses Textual's diff renderer — only changed
   cells repaint.
2. **The "everything is a bar" school of design.** htop is great for
   numeric data; chat conversations aren't bars. We use bars only
   for genuinely-bar-shaped data (ingest progress, token throughput
   if we ever show it).
3. **The function-key reliance.** htop's primary keys are F1-F10.
   Many modern terminals don't forward F-keys reliably. Stofa uses
   letter keys + F-keys as alternates.

---

## btop

### What it is

A modern rewrite of bashtop/bpytop in C++. Beautiful: rounded
borders, Unicode block characters for smooth bars, themes, mouse
support, network + disk panels in addition to CPU/mem.

Author: aristocratos. ~30k stars by 2026.

### The clever idea

**Beauty as a feature, not an indulgence.** btop spends a *lot* of
its rendering on smooth Unicode block characters (▁▂▃▄▅▆▇█) instead
of ASCII pipes. The result looks like a real GUI app — operators
talk about btop the way they talk about good native software.

The deeper idea: **users will tolerate complexity if the surface is
beautiful.** btop has more panels and more options than htop, but
the beautiful rendering makes it feel less dense.

### What we steal

1. **Smooth Unicode block characters for progress bars.** When we
   render ingest progress, we use ▁▂▃▄▅▆▇█ for fractional progress,
   not just █-on-or-█-off.
2. **Rounded borders everywhere.** Per [`../architecture/14_LAYOUT_SYSTEM.md`](../architecture/14_LAYOUT_SYSTEM.md),
   our default border style is `round` — matches btop, more
   modern than the default sharp boxes.
3. **Themes that ship with the product.** btop ships ~20 themes
   out of the box. Stofa V1 ships 5; V2+ adds community themes via
   plugins.
4. **The investment in look.** btop's existence is the strongest
   argument that "modern terminal UI" deserves real design work.

### What we avoid

1. **The "animate everything" trap.** btop pulses values constantly,
   which fights for attention. Stofa is calmer — pets tick at 1 Hz
   max; the hearth pulses on Funi work only.
2. **Bright saturated colors.** btop's defaults run hot. Our Aurora
   is muted.
3. **The information density.** btop fills the screen with information;
   we use whitespace deliberately.

---

## Comparison table

| Concern | htop | btop | Stofa |
|---|---|---|---|
| Update rate | 1 Hz full repaint | 2-10 Hz partial | event-driven, no fixed rate |
| Color count (default) | ~5 | ~12 | 5 semantic |
| Themes | 1 | ~20 | 5 (V1) |
| Borders | sharp ASCII | rounded Unicode | rounded Unicode |
| Mouse | partial | full | full (optional) |
| Font requirements | ASCII | Unicode blocks | Unicode + fallback |
| Information density | high | very high | medium (deliberate) |
| Cute factor | 0 | 1 (some character) | high (pets) |

---

## Lessons synthesized

From htop:
- Dashboard format teaches itself.
- One-color = one-meaning.
- Bottom bar as contextual help.
- Restrain animation.

From btop:
- Beauty matters more than density.
- Themes are load-bearing for adoption.
- Smooth Unicode > ASCII.
- Rounded > sharp.

From the comparison:
- Pick one update-rate philosophy and stick. (We pick event-driven.)
- Information density is a trade-off. (We err on the airy side.)
- Themes are a V1 feature, not a V2 nice-to-have.

---

## Specific Stofa choices informed by these

- **Ingest progress bar in WellScreen** uses btop-style smooth blocks.
- **Realms panel in HomeScreen** uses htop-style one-line-per-realm.
- **No constant pulsing.** Funi-spark only animates when Funi is
  actually working.
- **Five built-in themes** at launch.
- **Rounded borders everywhere.** Sharp borders never make it into
  the codebase.

---

## Closing

htop taught the world what a system-monitor TUI looks like. btop
taught the world that beauty is allowed. Stofa borrows both: the
clear dashboard discipline of htop, the visual investment of btop,
and the restraint of neither — calmer than both, because chat is the
foreground and the dashboard is the chrome.
