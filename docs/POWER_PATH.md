# POWER_PATH.md — 50 W Power Path: Inductors & Design Decisions

*Working trade study for Sprint S3. Nick decides; agreed decisions move to the
DESIGN.md decision log and this file keeps the evidence.*
*Last updated: 2026-10-05 · Owner/gate: **Nick***

> **Deferred to a later 50 W revision (Nick, 2026-10-05; DESIGN D12).** This
> first board keeps the Sofar mote's power path unchanged: SRF1260-101M L1/L2
> and every other part as vetted, rated ~20 W absolute max (890 mA per port
> inductor at 24 V); Nick already powers his cameras from it. Everything below
> is the 50 W trade study, kept intact for the future spin that adds a motor
> load, when it gets scoped against that load. Nothing here applies to this board.

## Sources

| Tag | Source | Notes |
|---|---|---|
| [G] | [Sofar — 50W & 100W Mote Component Selection & Circuit Design Guide](https://manual.sofarocean.com/50W-100W-Bristlemouth-Mote-Component-Selection-Circuit-Design-Guide-f78b6124579340ba88ac8631a784dd88) | From Evan. Says itself it gives recommendations, **not qualified at 50 W**. |
| [E] | [Sofar — Bristlemouth Evolution: More Power Delivery](https://manual.sofarocean.com/bristlemouth-evolution-more-power-delivery) | From Evan. Jetpack (100 W tested) and Dev Kit context. |
| [J] | Jetpack design archive (linked from [E] and [G]) | Not downloaded yet. Discrete inductors, not coupled. |
| [DS] | Manufacturer datasheets | Required before any value is final. Add each one here as it's used. |
| [DS-SRF] | [Bourns SRF1260 datasheet](https://www.bourns.com/docs/Product-Datasheets/SRF1260.pdf) | Read 2026-10-04 |

## 1. Rating definition — decided 2026-10-04 (P1, DESIGN D8)

Defined the way Sofar rates the mote [E]: an **absolute maximum current**
through each port's PoDL inductor, quoted as watts at 24 V.

| Parameter | Value | Notes |
|---|---|---|
| Rating | **~50 W absolute max at 24 V = 2.083 A** per port inductor | Covers pass-through and the mote's own load, like Sofar's 20 W |
| Below 24 V | Current limit holds; power falls | At 16 V, 2.083 A is ~33 W |
| Environment | **Potted** | Datasheet thermal ratings don't apply as-is [G]; potting rules in SPEC.md constraint 8 |
| Margin | Choose magnetics rated above 2.083 A *after* a potting derating | Nick: use the larger recommended inductors to get margin |

### How the mote's 20 W is defined (for comparison)

SRF1260-101M in series mode (one winding in each leg) [DS-SRF]: 400 µH,
**Irms 0.892 A** (40 °C temperature rise), Isat 1.1 A (30 % inductance drop),
DCR 0.656 Ω max. 0.892 A × 24 V = 21.4 W, which Sofar states as 20 W absolute
max [E]. It's a thermal limit, below saturation. At that current each port
drops ~0.58 V and each inductor dissipates ~0.52 W.

## 2. Rules for comparing coupled inductors [G]

- Two-winding part: one winding in the + leg and one in the return leg,
  **series-aiding**, so the data pair sees L_diff ≈ 4L. The wrong polarity
  leaves only leakage inductance and wrecks the link.
- Coilcraft's Isat is the *sum* of both winding currents, so compare it against
  2 × branch current. Use the "both windings energized" Irms as the thermal
  limit, never the one-winding figure.
- More current rating from less inductance makes droop worse. The 10BASE-T1L
  limit is < 25 % droop (IEEE 802.3dd, as cited in [G]).
- DC loss: 4 windings × DCR in the pass-through path.
- **Normalise across vendors before comparing.** Bourns quotes series-mode
  DCR (both windings), Irms and Isat at a **30 %** inductance drop [DS-SRF].
  Coilcraft quotes DCR per winding and Isat at a **10 %** drop [G]. Convert
  everything to the same basis in S3.

## 3. Candidates

Coilcraft figures are as quoted in [G]; each needs datasheet confirmation [DS].
Bourns rows are from [DS-SRF] series mode: DCR covers both windings and Isat is
the series-mode figure (30 % drop), so they're not directly comparable with the
Coilcraft sum-current column yet.

| Part | L/winding | L_diff | DCR max | Isat (sum) → branch | Irms (both) | Size (mm) | 50 W @ 24 V |
|---|---|---|---|---|---|---|---|
| SRF1260-101M (fitted now) | 100 µH | 400 µH | 0.656 Ω series | 1.1 A series (30 %) | 0.892 A | 12.5×12.5×6 | ✗ ~20 W |
| SRF1260-470M (2026 mote rev) | 47 µH | 188 µH | 0.34 Ω series | 1.62 A series (30 %) | 1.35 A | 12.5×12.5×6 | ✗ ~32 W |
| **MSD1514-473MED** ([G] preferred) | 47 µH | ~188 µH | 75 mΩ | 6.2 A → 3.1 A | 2.6 A | 15.5×15.5×14.2 | ✓ candidate |
| MSD1514-683MED | 68 µH | ~272 µH | 90 mΩ | 5.1 A → 2.55 A | 2.2 A | 15.5×15.5×14.2 | thin margin |
| MSD1278H-473MED | 47 µH | ~188 µH | 130 mΩ | 3.6 A → 1.8 A | 2.10 A | 12.3×12.3×8.05 | ✗ margin too thin |
| MSD1514-104KED | 100 µH | ~400 µH | 130 mΩ | 4.2 A → 2.1 A | 2.0 A | 15.5×15.5×14.2 | ✗ margin too thin |

With MSD1514-473: 0.30 Ω through-path → ~0.63 V drop and ~1.3 W of heat at 2.083 A [G].
Size fit on the board: Nick to confirm in SolidWorks (2026-10-05).

## 4. Impacted parts (everything in the path must meet §1 and the potting rules)

| Ref | Part (now) | Concern | Status |
|---|---|---|---|
| L1, L2 | SRF1260-101M | ~20 W rated; replace (§3). The replacement is newly sourced, so potting rules apply: check vendor guidance for ferrite under potting | open |
| D1 | SMA6F33A | Clamp voltage at real current vs the lowest absolute maximum on the node [G] | open |
| U5 (+ S4 copy) | LMR51430YDDCR | [G] quotes ~36 V operating / 38 V absolute maximum; confirm in [DS] | open |
| D2, D3 | RB058LAM-60TFTR | Current rating at 2.083 A + margin | open |
| U9, R34, R11 | FPF2700MX, 374 kΩ, 0 Ω | Payload switch current-limit range; is R11 fitted? Datasheet needed (onsemi link dead 2026-10-04). SOFAR_QUESTIONS Q2, Q3 | open |
| R8 | UR73D1JTTD10L0F | Shunt I²R dissipation and INA232 range at 50 W | open |
| C22/C23, R15/R16 | EEEFT1H470AP 47 µF/50 V + 7.5 Ω (Sofar-vetted) | **Kept as-is** (Nick, 2026-10-04). Only open point: does the damping need new values for the new magnetics [G]? SOFAR_QUESTIONS Q5 | open |
| Bulk caps | none | [G] provisions ~470 µF effective in a soft-started payload branch. Newly sourced, so potting rules apply (no electrolytics) | open |
| Through-path protection | **none** (no fuse or e-fuse in the schematic; Sofar: the mote has no through-current protection [E]) | Need one that works in both directions and is safe to pot (no PPTC [G]). U9 only protects the payload branch. SOFAR_QUESTIONS Q1 | open |
| Payload connector, copper | — | Current rating (Nick: copper widths) | open |

## 5. Pending decisions → DESIGN.md once Nick approves (all deferred with this file, D12)

- ~~P1 — Rating definition (§1)~~ → decided, DESIGN D8
- P2 — PoDL magnetics part and count per port (leaning MSD1514-473MED, pending fit)
- P3 — Damping (keep C22/C23/R15/R16, retune only if needed) and new bulk capacitance (no electrolytics)
- P4 — Protection: through-path e-fuse, clamp, reverse polarity, payload switch, inrush
