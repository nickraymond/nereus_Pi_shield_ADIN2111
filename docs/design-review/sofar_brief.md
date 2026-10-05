# Design-review brief for Sofar — nereus Pi shield vs Bristlemouth mote 000639-AB

*Shipped with the board files. Lists every deliberate change from your mote design
and why. Anything not listed is your circuit, copied as-is. Decision IDs (Dn) refer
to `docs/DESIGN.md`.* *Updated 2026-10-05.*

**Baseline:** Sofar Bristlemouth mote 000639-AB (KiCad copy of the Altium design).
The ADIN2111 / PoDL front end, 3.3 V and 1.8 V regulation and the ~20 W power path
(L1/L2 SRF1260-101M, D1–D3, R8, C22/C23/R15/R16) are **unchanged** (D12).

| # | Area | Mote 000639-AB | This shield | Why |
|---|---|---|---|---|
| 1 | Host processor | STM32 + DF17 mezzanine (P1) | Removed. Raspberry Pi Zero 2 W on a 2×20 socket header (J1); the Pi drives the ADIN2111 over SPI | The Pi runs the application (cameras) |
| 2 | I²C pull-ups | R26/R27 4.7 kΩ on the STM32 sheet | Re-added on the shield, same part (ERJ-2RKF4701X) to 3V3 (planned, D11) | Removed with the STM32; the Pi needs them |
| 3 | 5 V rail | None | U10 LMR51430YDDCR, a copy of your U5 block: R38 13.7 kΩ (4.98 V), output caps 2 × 22 µF 16 V + 4.7 µF 10 V, same 8.2 µH inductor (D13, D16) | Powers the Pi from the bus |
| 4 | 5 V to the Pi | — | JP1: bridged copper link on 1210 pads (connected as built; cut for a battery/USB-powered Pi; refit a 0 Ω) (D14) | Shield is normally the Pi's only supply |
| 5 | Payload load switch | U9 FPF2700MX with R11 (0 Ω) **fitted across it** in the files we received, so the switch was bypassed (Q2 asks about production) | **R11 DNP.** U9 replaced by **TI TPS26621DRCR** (U11): R34 374 kΩ → **9.09 kΩ** (≈ 0.73 A limit), new R41 1 MΩ (UVLO tie), dVdT open, OVP to GND. Enable pull-up R32 → **10 kΩ pull-down R42** (TPS26621 SHDN is active low; payload off by default). PGOOD dropped (R33/TP34 removed); FLT kept. RTN = GND (reverse-input protection not used). R_ON 478 mΩ vs 88 mΩ: ≈ 0.35 V drop at 0.73 A (D17, D18) | FPF2700MX is no longer manufactured (Digi-Key, 2026-10); we want the payload switched by the Pi and current-limited. TPS26621 is active at TI and stocked by JLC (C1848341) |

**Notes for your review**

- Rating, budget and thermal analysis: `docs/design-review/power_budget.md`. The Pi
  is limited to ≤ 1 A continuous by U10's temperature (D15).
- Open questions for you: `docs/SOFAR_QUESTIONS.md` (Q2 R11 on production motes,
  Q4 mezzanine-side load-switch control).
- Import housekeeping, not design changes: Altium-import connectivity repairs (21
  mid-wire pins split and joined), new reference numbers start above the mote
  board's highest (U10+, C53+, R37+).
