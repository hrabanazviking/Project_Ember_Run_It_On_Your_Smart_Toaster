# 16 — Sibling: Hamr

> *"ᚺᚨᛗᚱ — The Shape-Skin Engine."*

Open-source parametric 3D anime character forge. Linux-native,
headless-first, agent-orchestrated. VRM 1.0.

---

## What it is

A Python library + CLI for generating 3D anime-style VRM
characters from parametric inputs. From its own README:

- **Parametric forge** — character attributes (face, hair,
  body, clothing) controlled by numeric parameters.
- **Linux-native** — runs on Linux without GPU requirements
  for many operations (headless mode).
- **Headless-first** — designed for CI / server / agent use,
  not just interactive Blender.
- **Agent-orchestrated** — designed to be driven by other
  agents (like Ember).
- **VRM 1.0 output** — the open avatar format for VRChat,
  VTubers, etc.
- 2,206 tests passing (per their README badge).

The Old Norse word *hamr* means *shape, skin, form* — also
the *shape-shifting skin* warriors used in saga literature.

---

## Why this sibling matters for Yggdrasil

Hamr is **Ember's body**, when she gets one.

Ember today is voiceless and bodiless — a chat REPL, a TUI
in Stofa, an MCP endpoint. Slice-3 planned three new
surfaces:

- **Auga** (GUI) — visual surface
- **Rödd** (voice) — speech surface
- **Bifröst** (HTTP gateway) — addressable surface

When Auga ships, Ember can have a *face*. Hamr generates that
face — a parametric anime-style VRM character that appears in
the GUI, animates while she talks, expresses emotion in her
posture.

This is *visual embodiment*. Optional, operator-controlled,
absent on Pi (no GUI), present on desktop (with Auga).

---

## How Yggdrasil integrates Hamr

### Integration role

Hamr is **a Phase 4 integration** — gated on Auga (which is
itself a Phase 4 slice-3 surface, not part of the current
Yggdrasil scope).

When Auga ships:

1. The operator picks (or generates) a Hamr avatar.
2. Auga renders that VRM avatar as Ember's visual presence.
3. The avatar animates in response to Ember's state (idle,
   thinking, speaking, surprised, etc.).
4. The avatar's parameters are *operator-tunable* (Hamr's
   parametric design makes this natural).

### Why Hamr (vs other avatar systems)

- **Open-source + Linux-native.** No proprietary VRoid
  Studio dependency.
- **Headless-first.** Avatars can be generated server-side
  (Pi can render avatars on-demand for delivery to a desktop
  client).
- **VRM 1.0.** Standard format; works with any VRM renderer.
- **Agent-orchestrated by design.** Ember can ask Hamr to
  produce variations without operator hand-tuning.
- **Norse-aligned naming.** Hamr fits the family.

### Adapter shape

A `src/ember/yggdrasil/hamr/` package (Phase 4):

- `client.py` — `HamrClient` wraps Hamr's library
  interface for character generation + parameter mutation.
- `auga_bridge.py` — bridges generated VRMs to the Auga
  rendering surface (when Auga ships).

### Configuration shape

```yaml
yggdrasil:
  hamr:
    enabled: false                    # off by default; needs Auga
    avatar_cache: ~/.ember/avatars/
    default_params:
      style: traditional_norse
      hair_color: pale_blonde
      eye_color: ice_blue
      # ... many more parameters
```

---

## What Hamr does NOT do

- **Animate generation.** Hamr produces the model; animation
  is the renderer's job (Auga's responsibility).
- **Image-to-avatar.** Hamr is parametric (numeric inputs);
  it doesn't take a reference image and produce a similar
  character. (That's a different category of tool.)
- **Voice-to-lip-sync.** Auga + Rödd together handle that
  when both ship.
- **Live2D / 2D animation.** Hamr is 3D-VRM-focused.

---

## Risk / known issues

- **Heaviest sibling resource-wise.** Hamr is ~200MB RAM
  during generation; Pi-class operators don't run it on the
  Pi (they run Auga on a desktop, possibly pulling avatars
  from the Pi via the federation layer).
- **Anime-style aesthetic might not match every operator's
  preference.** Hamr is what it is. Alternatives for
  non-anime style are operator-supplied.
- **Auga doesn't exist yet.** Hamr's full integration awaits
  Auga's design ratification (slice-3, separate from
  Yggdrasil).

---

## Operator-facing example (Phase 4, post-Auga)

```bash
ember auga             # launches the GUI
# First launch: Hjarta wizard now includes an avatar step
# Operator picks: "Traditional Norse, pale-haired, ice-blue eyes"
# Or: "Random — let Hamr surprise me"
# Or: "Upload my own VRM"

# Avatar saved to ~/.ember/avatars/default.vrm
# Auga renders it as Ember's face

# Later, in chat:
ember: "Hello!"
# Avatar lips move (Auga lip-sync), expression shifts to friendly

ember: "Hmm, let me think about that…"
# Avatar tilts head, thoughtful expression
```

The avatar doesn't change *what* Ember says. It changes
*how the operator experiences her* — from a chat bubble to
a presence.

---

## Why this fits the Vows

- **Smallness:** Hamr is opt-in (`pip install ember-agent[hamr]`).
  Default install doesn't bring 200MB of avatar engine.
- **Sovereignty:** Avatars live in `~/.ember/avatars/`.
  No upload, no cloud, no central registry.
- **Public-Friendliness:** Default avatar is friendly + neutral.
  Operators can replace.

---

## Test strategy

Phase 4 ships:

- **Unit tests** for `HamrClient` adapter.
- **Integration test** generating a default-parameter VRM,
  verifying the file is valid VRM 1.0.
- **Auga rendering test** (after Auga ships) verifying the
  avatar renders correctly + animates state changes.

Tests in `tests/unit/test_yggdrasil_hamr_client.py` and
`tests/integration/test_yggdrasil_hamr_auga.py`.

---

## Closing

Hamr is *the body Ember gets when she has a face to show*.
Optional, Auga-gated, sovereign, beautifully Norse-aligned.

A small Ember has no body and needs none. A desktop Ember
*can* have one — and Hamr is the forge that shapes it.
