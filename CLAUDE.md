# CLAUDE.md — nereus_Pi_shield_ADIN2111

## Start here, every session

This repo runs on the agent discipline in **docs/TRACKER.md**. Before any other
work: run **/agent-entry** (or follow the Rules for Agents at the top of
docs/TRACKER.md). Owner and approval gate: **Nick**.

Docs map — read per the ritual, don't skip it:

- `docs/SPEC.md` — goal; verified facts; hard constraints; open questions
- `docs/TRACKER.md` — rules + sprint ladder (the entry point, the only progress record)
- `docs/DESIGN.md` — sheet hierarchy, pin map, decision log, ERC/net-check results
- `docs/POWER_PATH.md` — 50 W power path: inductor trade study and pending decisions
- `docs/SOFAR_QUESTIONS.md` — open questions for Sofar and their answers
- `docs/DEV_LOG.md` — session log, newest first
- `docs/PROMPTS.md` — Nick's kickoff prompts

Layout: `nereus_Pi_shield_ADIN2111/` is the live KiCad project; `docs/design-review/`
holds check outputs; `KiCAD_reference_designs/` and `Archive/` are read-only.

## Engineering values (apply to every bite)

1. **Boring, debuggable engineering.** Small edits, explicit nets, visible
   checks, plain formats. Build for the current sprint, not an imagined future.
2. **Reuse before rewriting.** Copy proven mote blocks before designing new
   ones; document what was reused. A new design needs a measurable reason.
3. **Never invent facts.** Part values, ratings, pinouts: verify against
   datasheets or measure, else flag in SPEC.md §Open questions.
4. **Trust artifacts, not exit codes.** A schematic edit is done when kicad-cli
   loads it, ERC runs and the net diff shows only the intended change.
5. **One variable at a time.** Record the known-good baseline before changing it.
6. **Fail loudly and usefully.** Errors carry context and a recovery hint;
   partial failure never destroys good data.
7. **KiCad runtime rules.** KiCad stays closed while an agent edits; checks run
   through kicad-cli; no agent ever writes a `.kicad_pcb`.
8. **Hard constraints in SPEC.md are absolute.**

> Never trust a script just because it exits successfully. Trust the artifacts.
