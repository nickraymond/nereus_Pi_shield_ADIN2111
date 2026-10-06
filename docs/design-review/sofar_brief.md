# Design-review brief for Sofar — nereus Pi shield vs Bristlemouth mote 000639-AB

*Shipped with the board files. Lists every deliberate change from your mote design
and why. Anything not listed is your circuit, copied as-is. Decision IDs (Dn) refer
to `docs/DESIGN.md`.* *Updated 2026-10-05 (S5.c).*

**Baseline:** Sofar Bristlemouth mote 000639-AB (KiCad copy of the Altium design).
The ADIN2111 / PoDL front end, 3.3 V and 1.8 V regulation and the ~20 W power path
(L1/L2 SRF1260-101M, D1–D3, R8, C22/C23/R15/R16) are **unchanged** (D12).

| # | Area | Mote 000639-AB | This shield | Why |
|---|---|---|---|---|
| 1 | Host processor | STM32 + DF17 mezzanine (P1) | Removed. Raspberry Pi Zero 2 W on a 2×20 socket header (J1); the Pi drives the ADIN2111 over SPI | The Pi runs the application (cameras) |
| 2 | I²C pull-ups | R26/R27 4.7 kΩ on the STM32 sheet | Re-added on the shield: same refs, part (ERJ-2RKF4701X) and footprint, to the shield's 3V3 (D11, D20). With the Pi's own 1.8 kΩ the bus sees ≈ 1.3 kΩ | Removed with the STM32; the Pi needs them, and they keep the bus usable with a bench MCU |
| 3 | 5 V rail | None | U10 LMR51430YDDCR, a copy of your U5 block: R38 13.7 kΩ (4.98 V), output caps 2 × 22 µF 16 V + 4.7 µF 10 V, same 8.2 µH inductor (D13, D16) | Powers the Pi from the bus |
| 4 | 5 V to the Pi | — | JP1: bridged copper link on 1210 pads (connected as built; cut for a battery/USB-powered Pi; refit a 0 Ω) (D14) | Shield is normally the Pi's only supply |
| 5 | Payload load switch | U9 FPF2700MX with R11 (0 Ω) **fitted across it** in the files we received, so the switch was bypassed (Q2 asks about production) | **R11 DNP.** U9 replaced by **TI TPS26621DRCR** (U11): R34 374 kΩ → **9.09 kΩ** (≈ 0.73 A limit), new R41 1 MΩ (UVLO tie), dVdT open, OVP to GND. Enable pull-up R32 → **10 kΩ pull-down R42** (TPS26621 SHDN is active low; payload off by default). PGOOD dropped (R33/TP34 removed); FLT kept. RTN = GND (reverse-input protection not used). R_ON 478 mΩ vs 88 mΩ: ≈ 0.35 V drop at 0.73 A (D17, D18) | FPF2700MX is no longer manufactured (Digi-Key, 2026-10); we want the payload switched by the Pi and current-limited. TPS26621 is active at TI and stocked by JLC (C1848341) |
| 6 | ADIN power enable (ADIN_PWR → U2/U3 ON) | Driven by the STM32, no pull resistor | Driven by Pi GPIO23 with a new **R43 100 kΩ pull-down** (your R21 part). The AP22913 ON pin has no internal pull-down | Keeps the ADIN off while the Pi boots, is absent or is off, so the straps are only read on a deliberate power-up and INT can't feed an unpowered Pi. CS/RST back-power is handled by a boot order in Pi software (D21) |
| 7 | Load-switch control links | R10 0 Ω (STM32 pin 19 → SW_ON) and R9 0 Ω (mezzanine → same net), TP19 | R9 and R10 removed; TP19 kept, tied to SW_EN; Pi GPIO16 is the only controller (D22) | One controller; fewer parts to place |
| 8 | Payload power out | VBUS_OUT through mezzanine P1 pins 14/16/18 | **J5 JST GH 2-pin** (SM02B-GHS-TB): pin 1 VBUS_OUT, pin 2 GND; 1.0 A per contact, 50 V (D23) | The mezzanine is gone; the payload needs its own connector |
| 9 | ADIN status LEDs | None | **D8 red** (ADIN powered), **D9 / D10 yellow-green** (port 1 / port 2 link/activity on ADIN pins 21 / 48, active low; your R3 / R5 stay as their pull-ups, so the 1.0 V p-p straps are unchanged), each via 1.5 kΩ from ADIN_VDDIO through **JP2**, a bridged link that is cut to disable them (D25) | Bench visibility of PHY power and per-port link; a few mW, off with the ADIN |

**Notes for your review**

- Rating, budget and thermal analysis: `docs/design-review/power_budget.md`. The Pi
  is limited to ≤ 1 A continuous by U10's temperature (D15).
- Open questions for you: `docs/SOFAR_QUESTIONS.md` (Q2 R11 on production motes,
  Q4 mezzanine-side load-switch control).
- Import housekeeping, not design changes: Altium-import connectivity repairs (21
  mid-wire pins split and joined), new reference numbers start above the mote
  board's highest (U10+, C53+, R37+).
