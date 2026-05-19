# tools/importers/

One-way importers that pull material from other Volmarr projects into this repo:
NSE, MindSpark, WYRD, Seidr-Smidja, HERETIC, Mythic Vibe CLI, Viking Girlfriend Skill, the research-data corpus.

These tools are used carefully and rarely — never on a schedule. Every import run is reviewed before the resulting commit lands. Each import writes a manifest under `docs/decisions/` so the provenance trail in `ORIGINS.md` stays accurate.
