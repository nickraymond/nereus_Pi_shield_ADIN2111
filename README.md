# nereus_Pi_shield_ADIN2111

A Raspberry Pi Zero 2W shield built from a copy of the Sofar Bristlemouth mote:
ADIN2111 two-port 10BASE-T1L with PoDL, powered from the bus, 5 V for the Pi,
a 24 V payload port, and a ~50 W power path (absolute max at 24 V). Potted.

Claude Code does the schematic capture, up to a design-review package. Nick
reviews, lays out, routes and brings up the board.

## Folders

```
nereus_Pi_shield_ADIN2111/   live KiCad 9 project — open the .kicad_pro
docs/                        spec, tracker, design log, power-path study
docs/design-review/          ERC, netlist, PDF and the review package
KiCAD_reference_designs/     BM mote 000639-AB, UrchinCam (read-only)
Archive/                     earlier iterations, junction fix (read-only)
pi-shield-checklist.html     visual walkthrough (reference; progress lives in docs/TRACKER.md)
```

## Working on it

- Agents: start with `CLAUDE.md`, then `/agent-entry`.
- People: `docs/TRACKER.md` shows where things stand; `docs/SPEC.md` says what
  we're building and why.
- Close KiCad before an agent edits the project.
