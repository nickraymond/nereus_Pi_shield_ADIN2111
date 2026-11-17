# N6 shield: brief

Branch `n6-shield`, created 2026-11-17 from `pi-zero-side-entry` (commit 33ad05f, the Pi Zero shield as sent to M
for review). Owner and approval gate: Nick.

**State: nothing designed yet.** The project in `N6_Shield_ADIN2111/` is an unchanged copy of the Pi Zero
side-entry shield (file names still `Nereus_Pi_Shield_Adin2111.*`, Nick 2026-11-17: keep the names for now). It is
the starting point, not an N6 design.

## Goal

A shield that mounts on the back of the N6 board and carries Sofar's Bristlemouth mote circuit (ADIN2111, PoDL
power), a 5 V supply and the motor driver, as small as possible.

"N6" is Nick's name for the target board. The project's records mention an "OpenMV N6" as a later variant of the
full-size shield (`docs/DESIGN.md` D31 on the `development` branch). **Confirm with Nick which board and which
revision he means before sourcing its drawings**, then source every N6 fact (outline, mounting holes, header
positions and pitch, pin functions, logic levels, supply pins and their current limits, ADC, timers / PWM, SPI
buses, which pins are free) from the maker's published documents, with the URL and date. Nothing about the N6 is
recorded in this repository yet.

## Nick's request, in his words (chat of 2026-11-17)

Things to eliminate:

1. "the VBUS out control circuit, I do not need it"
2. "5V jumper switch for the PSU, do not need it, remove the fuse"

Things to make better:

- "5V circuit - more copper so more thermal [protection]"
- "Needs to map to the N6 pinouts"
- "I want to make this as small as possible, while keeping the mote circuitry [intact], [might] be challenging
  given I need to fit the N6 headers [so] lets see what a first pass looks like, I think the mote should be rotated
  90 deg to fit between the headers of the N6"
- "motor driver, give it more copper for plenty of heat sinking"
- "this shield ideally is the same size or slightly larger than the N6 board outline, it is a shield that will
  mount on the back"

Things to explore:

- "where and what style JST connectors, likely the top-entry variant but lets see how both could fit in a mock"
- "there are less I/O so we need to understand what we can and can't support"
- "the N6 has an ADC onboard, can we use it?"
- "N6 has PWM, can we use those for the motor controller?"
- "N6 and SPI need a clear and safe way to route that"
- "Adin LEDs, good for dev but not needed for deployment, can we wire this to a I/O on the N6 so their on and off
  becomes something to toggle in firmware?"

## What these map to on the starting design (read from the Pi Zero board; verify before acting)

- VBUS out control: the payload load switch U11 (TPS26621) with its support parts, the pads J5, GPIO26 enable and
  GPIO6 fault. Schematic sheet "Load Switch".
- 5 V jumper and fuse: JP1 (5 V select), polyfuse F1 and the AUX 5 V pads J4. With JP1 gone, decide with Nick how
  the 5 V rail reaches the N6 (direct to its supply pin?) and whether the AUX pads stay.
- 5 V circuit: U10 LMR51430 with L6. Design target on the Pi Zero board 1.5 A continuous, limited by U10's heat;
  the bench check is still open. An older board of Nick's ran the same circuit with about five times the
  outer-layer ground copper. Re-derive the N6's 5 V (or other) supply need from its documents.
- Motor driver: U12 MP6550 on the 5 V rail, current limit 1.24 A (R48 4.02 k), current sense to the ADC.
- ADC: U13 ADS1115 (motor current on AIN0, pot wiper on AIN1). If the N6's own ADC can do this, U13 may go:
  that is one of the questions.
- ADIN LEDs: D8 (power), D9 / D10 (port LEDs driven by the ADIN2111), their resistors and the LED jumper JP2.
- Mote block: Sofar's ADIN2111 / PoDL / 3.3 V circuit (81 footprints and his copper), kept as a locked block on
  the Pi boards. "Rotated 90 deg" means turning that whole block rigidly with its copper.
- Connectors today: JST GH side-entry J7 (motor), J9 / J10 (bus ports), J8 (pot), JST SH J3 (Qwiic). Why a
  top-entry swap failed on the Pi Zero layout, the JLC part numbers for the top-entry parts and the open question
  of their mated height: `experiments/pi_zero_fit_01/reports/TOP_ENTRY_VARIANT.md` on `development`.

## First deliverable (before any change to the board or schematic)

1. The N6 facts sheet with sources.
2. A pin map proposal: every signal the shield needs against the N6 pins that can carry it, what cannot be
   supported with fewer I/O, and answers to the explore questions (ADC, PWM, SPI routing, LEDs under firmware
   control), each with its source.
3. Size study and placement mocks: the N6 outline and headers, the mote block rotated 90 degrees between the
   headers, the 5 V converter and motor driver with their copper areas, and the connectors drawn both as top-entry
   and as side-entry. Smallest outline that holds it, against "same size or slightly larger than the N6".
4. Questions for Nick. Then stop for his review.

## How to work

- Read on the `development` branch: `START_HERE.md` (map and lessons), `CLAUDE.md` and `docs/TRACKER.md` (rules),
  `docs/SPEC.md` (hard constraints), `docs/DESIGN.md` (decisions), `docs/design-review/power_budget.md`,
  `experiments/pi_zero_fit_01/BRIEF.md` and `LOG.md` (how the Pi Zero variant was specified and built, stage by
  stage, and the scripted-KiCad traps).
- KiCad stays closed while an agent edits. No change to the board, schematic or rule files without Nick's go.
  Never push without asking. Never invent facts: every value comes from a source read in the session.
- Work only on this branch. Outputs (mocks, renders, reports, check results) go to
  `~/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/`, not into git; the brief, scripts and decisions go into git.
- Nick's standing preferences: routing that looks hand-made (straight runs, 45 degree bends, parallel buses);
  JLC 6-layer rules; reuse vetted footprints; mocks first, then build on his yes; reviews before he inspects.
