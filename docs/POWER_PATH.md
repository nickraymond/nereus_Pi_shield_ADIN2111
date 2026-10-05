# POWER_PATH.md — 50 W Power Path: Inductors & Design Decisions

*Working trade study for Sprint S3. Nick decides; agreed decisions move to the
DESIGN.md decision log and this file keeps the evidence.*
*Last updated: 2026-10-04 · Owner/gate: **Nick***

## Sources

| Tag | Source | Notes |
|---|---|---|
| [G] | [Sofar — 50W & 100W Mote Component Selection & Circuit Design Guide](https://manual.sofarocean.com/50W-100W-Bristlemouth-Mote-Component-Selection-Circuit-Design-Guide-f78b6124579340ba88ac8631a784dd88) | From Evan. Says itself it gives recommendations, **not qualified at 50 W**. |
| [E] | [Sofar — Bristlemouth Evolution: More Power Delivery](https://manual.sofarocean.com/bristlemouth-evolution-more-power-delivery) | From Evan. Jetpack (100 W tested) and Dev Kit context. |
| [J] | Jetpack design archive (linked from [E] and [G]) | Not downloaded yet. Discrete inductors, not coupled. |
| [DS] | Manufacturer datasheets | Required before any value is final. Add each one here as it's used. |

## 1. Rating definition — Nick decides first (S3 gate)

| Parameter | Value | Notes |
|---|---|---|
| What the 50 W covers | ? | Port-to-port pass-through, payload port (VBUS_OUT), or both |
| Nominal / minimum local voltage | 24 V / ? | At 16 V, 50 W is 3.125 A [G] |
| Continuous vs peak | ? | Duty cycle and peak duration |
| Ambient / potting | ? | Changes thermal ratings [G] |
| Design current incl. margin | ? | [G] suggests ~15 % input-current margin |

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

## 3. Candidates

Coilcraft figures are as quoted in [G]; each needs datasheet confirmation [DS].

| Part | L/winding | L_diff | DCR max | Isat (sum) → branch | Irms (both) | Size (mm) | 50 W @ 24 V |
|---|---|---|---|---|---|---|---|
| SRF1260-101M (fitted now) | 100 µH | ~400 µH | — | 1.1 A sat [G] | 0.892 A | 12.5×12.5×6 | ✗ ~20 W |
| SRF1260-470M (2026 mote rev) | 47 µH | ~188 µH | — | 1.62 A sat [G] | 1.35 A | 12.5×12.5×6 | ✗ ~32 W |
| **MSD1514-473MED** ([G] preferred) | 47 µH | ~188 µH | 75 mΩ | 6.2 A → 3.1 A | 2.6 A | 15.5×15.5×14.2 | ✓ candidate |
| MSD1514-683MED | 68 µH | ~272 µH | 90 mΩ | 5.1 A → 2.55 A | 2.2 A | 15.5×15.5×14.2 | thin margin |
| MSD1278H-473MED | 47 µH | ~188 µH | 130 mΩ | 3.6 A → 1.8 A | 2.10 A | 12.3×12.3×8.05 | ✗ margin too thin |
| MSD1514-104KED | 100 µH | ~400 µH | 130 mΩ | 4.2 A → 2.1 A | 2.0 A | 15.5×15.5×14.2 | ✗ margin too thin |

With MSD1514-473: 0.30 Ω through-path → ~0.63 V drop and ~1.3 W of heat at 2.083 A [G].

## 4. Impacted parts (everything in the path must meet §1)

| Ref | Part (now) | Concern | Status |
|---|---|---|---|
| L1, L2 | SRF1260-101M | ~20 W rated; replace (§3) | open |
| D1 | SMA6F33A | Clamp voltage at real current vs the lowest absolute maximum on the node [G] | open |
| U5 (+ S4 copy) | LMR51430YDDCR | [G] quotes ~36 V operating / 38 V absolute maximum; confirm in [DS] | open |
| D2, D3 | RB058LAM-60TFTR | Current rating at 2.083 A + margin | open |
| U9, R34, R11 | FPF2700MX, 374 kΩ, 0 Ω | Payload switch current limit; is R11 fitted? | open |
| R8 | UR73D1JTTD10L0F | Shunt I²R dissipation and INA232 range at 50 W | open |
| R15/R16, C22/C23 (mote v1.1 refs [G]) | 7.5 Ω + EEEFT1H470AP | Retune damping for the new magnetics; resistor pulse energy [G] | open |
| Bulk caps | none | [G] provisions ~470 µF effective in a soft-started payload branch | open |
| Payload connector, copper | — | Current rating (Nick: copper widths) | open |

## 5. Pending decisions → DESIGN.md once Nick approves

- P1 — Rating definition (§1)
- P2 — PoDL magnetics part and count per port
- P3 — Damping and bulk-capacitance provisions
- P4 — Protection: clamp, reverse polarity, payload switch, inrush
