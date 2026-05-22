# 01 — Naming the Constellation

## The chosen name: **Yggdrasil**

**Yggdrasil** /ˈɪɡdrəsɪl/ — Old Norse compound. *Yggr* = "the
terrible one," a kenning for Odin. *Drasill* = "horse" (poetically:
"steed"). Literally: *Odin's horse* — the tree on which Odin hung
himself for nine nights and nine days to win the runes (Hávamál,
st. 138).

In the cosmology, Yggdrasil is the **world-tree** whose roots and
branches bind together the nine realms. Without it, the realms
drift. With it, they are a cosmos.

Pronounced: **IGG-druh-sil** (the *gg* hard like in *egg*).

### Why this name fits

- **It names what the thing IS.** Yggdrasil is the *structure that
  ties realms together*. The integration plan IS that tree. The
  metaphor isn't decorative; it's load-bearing.
- **It carries the project's Norse register without inventing.**
  Every Ember surface is named in Old Norse domestic-or-cosmological
  register. Yggdrasil fits the family.
- **It scales semantically.** When we say "Yggdrasil Phase 3," it
  means "the third phase of integrating the world-tree." When we
  say "an Yggdrasil release," it means a version where multiple
  realms ship together.
- **It's already in the repo.** A file titled
  `Yggdrasil_and_Huginn_and_Muninn_Theory.md` (~580 KB) sits at
  the repo root, drafted long before this plan. The metaphor was
  already alive in the operator's design vocabulary.

### Why not alternatives

| Candidate | Meaning | Why rejected |
|---|---|---|
| **The Constellation** | English; a group of related stars | Generic. Loses the Norse register. |
| **Níu Heimar** ("the nine realms") | the realms themselves | Names the parts, not the connecting structure |
| **Heimstǫð** ("home-place") | the household | Too small; this isn't just one realm |
| **Allheimr** ("all-world") | the whole world | Grandiose; less specific than Yggdrasil |
| **The Loom** | a Norn-evoking weaving metaphor | Verðandi-the-sibling already weaves; conflict |
| **The Tapestry** | similar | Same reason |
| **The Cosmos** | English / Greek | Wrong register |
| **The Web** | tech-y / Vow-violating (sovereign-by-default avoids "web" branding) | Loses the Norse |
| **Heitstrenging** ("vow-pledging") | a Norse oath ritual | Too specific to a moment |
| **Galdrabók** ("magic book") | a grimoire | Wrong register for software |

The decision rule: **does the name describe a structure that holds
disparate parts in coherent relation?** Yggdrasil passes
unambiguously.

## How operators talk about it

Idiomatic in docs and prompts:

- "Yggdrasil ships in Phase 1" → the integration design lands its
  first phase of code.
- "An Yggdrasil-ratified release" → version where multiple realms
  ship together, gated by ADR-0016.
- "The Yggdrasil tree" → this design directory + the resulting
  integration code.
- "Wiring Bifrǫst into Yggdrasil" → adding Bifrǫst as an integrated
  realm.

Not idiomatic (avoid):

- "Yggdrasil app" — it's not an app; it's the architecture.
- "Project Yggdrasil" alone (without "design tree") — it sounds
  like a separate project, but Yggdrasil IS the integration
  plan, not a sibling.

## How realms get named within Yggdrasil

The nine cosmological realms are the *metaphor*; the actual sibling
projects keep their existing names. Mapping:

| Cosmological realm | Sibling project | Why this realm |
|---|---|---|
| **Asgard** (gods, sovereignty) | Ember herself | She's the central authority |
| **Bifrǫst** (the rainbow bridge) | bifrost (sibling) | Connects realms — literal match |
| **Mímisbrunnr** (Mímir's Well at the root) | mimir-well (sibling) | Wisdom under the tree — literal match |
| **Urðarbrunnr** (Norns' well of fate) | Verdandi (sibling) | The Norn of "becoming" / present moment |
| **Vanaheim** (the Vanir, magic + cycles) | seidr_engine (sibling) | Seiðr is the Vanir's magic |
| **Niflheim** (mist + cold + secrets) | Kista (sibling) | Hidden, locked, protected |
| **Alfheim** (light elves, beauty) | Hamr (sibling) | Shape-skin / parametric avatars |
| **Útgarðr** (outer world, beyond bounds) | CloakBrowser (sibling) | Goes beyond the boundary |
| **Muspelheim** (fire + celestial cycles) | astrology-engine (sibling) | Sky-fire, time |
| **Helheim** (the realm of stored / past) | mempalace (sibling) | Verbatim recollection |
| **Yggdrasil's hoard** (lore at root) | norse-dict (sibling) | The lexicon |

When a doc says "the Niflheim realm," it means *Kista*. When it
says "the Alfheim realm," it means *Hamr*. The mapping is
*deliberate metaphor*, not arbitrary code-name. Each realm has
**cosmological resonance with its function** — that's the point.

## When NOT to use cosmological names

We use *project names* (kista, Verdandi, bifrost) when:
- Importing in code (`from kista import Vault`).
- Naming a pip extra (`[kista]`, not `[niflheim]`).
- In CLI strings the operator sees (`ember kista status`, not
  `ember niflheim status`).

We use *realm names* (Niflheim, Bifrǫst, Mímisbrunnr) when:
- Describing the architecture in prose.
- Writing about cosmology vs implementation.
- Speaking metaphorically about *roles* rather than software.

The discipline keeps the metaphor available without intruding on
the operator's command-line.

## Pronunciation guide

For operators who want it:

- **Yggdrasil** — *IGG-druh-sil*
- **Bifrǫst** — *BIV-rohst* (the "ǫ" is closer to "oh")
- **Mímir** — *MEE-meer*
- **Mímisbrunnr** — *MEE-mis-bru-ner*
- **Verðandi** — *VER-than-dee* (ð like "th" in "this")
- **Urðr** — *OOR-thur*
- **Skuld** — *SKULD*
- **Seiðr** — *SAY-thur*
- **Kista** — *KEE-stuh*
- **Hamr** — *HAH-mer*

We surface these in the README's pronunciation appendix (V3 add).

## Closing

A good name is what the thing has always wanted to be called.
Yggdrasil isn't a tree we're inventing — it's a tree the
operator's already been growing. This design tree is the formal
recognition of what's already alive.
