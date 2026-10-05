# Power budget — shield + Pi + payload (S4.c)

*Part of the S6 design-review package. Every figure carries its source; anything
assumed is labelled as an assumption. Reproduce the arithmetic from the tables below.*
*Written 2026-10-05 (S4.c). Owner/gate: **Nick***

## Sources

| Tag | Source |
|---|---|
| [RPi-docs] | [Raspberry Pi documentation, "Power supply"](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply), read 2026-10-05 |
| [RPi-brief] | Raspberry Pi Zero 2 W product brief, "Published April 2024" (datasheets.raspberrypi.com) |
| [RPi-sch] | Raspberry Pi Zero 2 W reduced schematic, RPI-ZERO2W_R1, 2021-10-15 |
| [TI] | TI LMR51430 datasheet SLUSEF4A (Nov 2022): §7.4 thermal, Figure 7-2 (5 V efficiency, 1.1 MHz) |
| [P890] | Pulse P890.B (01/22), PA5432.822NLT |
| [ADI] | [ADIN2111 product page](https://www.analog.com/en/products/adin2111.html), read 2026-10-05 |
| [E] | Sofar, *Bristlemouth Evolution: More Power Delivery* (SPEC confirmed facts) |
| [IPC] | IPC-2221 external-conductor current formula: I = 0.048 · ΔT^0.44 · A^0.725 (A in mil²) |
| [USB2] | USB 2.0 specification, Table 7-7: VBUS at a high-power port 4.75–5.25 V |

## 1. Rating and loads

- **Rating (D12):** 890 mA absolute max through each port inductor [E]: 21.4 W at 24 V,
  14.2 W at 16 V (the Bristlemouth minimum bus voltage [E]). Everything on or through
  the shield shares it: the shield's own load, the payload port and current passing
  through to other modules.
- **Pi Zero 2 W** [RPi-docs]: recommended PSU **2 A**; typical bare-board active
  **350 mA**; USB peripheral current "limited by PSU, board, and connector ratings
  only". [RPi-brief]: input power **5 V DC 2.5 A**. The Pi's USB peripherals draw from
  the same 5 V rail, so from U10 when JP1 is bridged.
- **Shield 3.3 V domain** (ADIN2111, INA232, pull-ups, via U5): ADIN2111 is
  **77 mW typical** (dual supply, 1.0 V p-p) [ADI]. The 2.4 V p-p figure and the other
  ICs aren't sourced yet, so the budget uses an **allowance of 0.30 W at U5's input**
  (about 4× the ADIN figure). *Assumption, to be replaced by datasheet numbers.*
- **U10 efficiency** (5 V, 1.1 MHz, PFM, VIN 24 V), read from [TI] Figure 7-2:
  ≈ 88 % at 0.35 A, ≈ 90 % at 1 A, ≈ 89 % at 2 A, ≈ 88 % at 2.5 A (±2 points, read
  from a graph). The same values are used at 16 V input, where the curves sit slightly higher.

## 2. Bus current (shield + Pi), and what's left for payload + pass-through

Pi current at 4.98 V (D13). Bus current = (U10 input + 0.30 W) / bus voltage.

| Pi load | U10 out / in | Bus mA at 24 V | Left at 24 V | Bus mA at 16 V | Left at 16 V |
|---|---|---|---|---|---|
| 0.35 A (typical [RPi-docs]) | 1.74 / 1.98 W | 95 | 795 mA (19.1 W) | 143 | 747 mA (12.0 W) |
| 1.0 A (*assumed*: Pi + modest USB/camera) | 4.98 / 5.53 W | 243 | 647 mA (15.5 W) | 365 | 525 mA (8.4 W) |
| 2.0 A (recommended PSU [RPi-docs]) | 9.96 / 11.19 W | 479 | 411 mA (9.9 W) | 718 | 172 mA (2.7 W) |
| 2.5 A (input rating [RPi-brief]) | 12.45 / 14.15 W | 602 | 288 mA (6.9 W) | 903 | **−13 mA (over)** |

**Reading:** at realistic Pi loads the bus has plenty of headroom. Only a 2.5 A Pi on
a 16 V bus exceeds the rating on its own. "Left" covers the payload port **and**
any current passing through to downstream modules.

## 3. U10 / L6 losses and temperature rise

Loss = Pout · (1/η − 1); L6 share = I² · 26.4 mΩ (DCR max [P890]); the rest is in U10.
Junction rise is U10 loss × RθJA: 107.8 °C/W (JEDEC 4-layer, [TI] §7.4) or 80 °C/W
(TI's 2-layer example, [TI] §7.4). Free air; potting changes these (SPEC constraint 8).

| Pi load | Total loss | L6 | U10 | ΔTj @ 107.8 °C/W | ΔTj @ 80 °C/W |
|---|---|---|---|---|---|
| 0.35 A | 0.24 W | 3 mW | 0.23 W | 25 °C | 19 °C |
| 1.0 A | 0.55 W | 26 mW | 0.53 W | 57 °C | 42 °C |
| 2.0 A | 1.23 W | 106 mW | 1.13 W | 121 °C | 90 °C |
| 2.5 A | 1.70 W | 165 mW | 1.53 W | 165 °C | 123 °C |

**Reading: U10's temperature, not the bus, is the binding limit.** Up to about 1 A
continuous the rise is moderate. At 2 A and above the junction gets near the 150 °C
rating (TI derates lifetime above 150 °C [TI] §7.1 note) once ambient and potting are
added. Thermal shutdown is 163 °C typical [TI] §7.5, so the part protects itself but
the Pi would brown out. L6 is comfortable (Iheat 8 A [P890]).

→ **Proposal for Nick (P-S4c-1):** set a continuous Pi load target of **≤ 1 A**
(Pi plus anything it powers over USB), with short peaks above that. Ask layout
for generous copper on U10's GND/VIN/SW pins to lower RθJA. Measure U10's case
temperature at bring-up under the real camera load.

## 4. JP1 bridge (1.0 mm copper, D14)

[IPC], external layer, 1 oz (35 µm, *assumed*; Nick's stack-up decides): A = 54.3 mil²
→ **2.4 A at ΔT 10 °C, 3.2 A at ΔT 20 °C.** Resistance of the 1.7 mm bridge
≈ 0.84 mΩ, so 2 mV drop at 2.5 A. **Adequate** for the ≤ 1 A target and even for the
2.5 A worst case at ~20 °C rise. Potting improves heat-sinking of a short bridge.

## 5. Pi supply voltage

- [RPi-docs]: "All models require a 5.1V supply". The low-voltage detector (warning
  below 4.63 V ±5 %) exists "on all models … since the Raspberry Pi B+ (2014) **except
  the Zero range**". **The Zero 2 W has no undervoltage detector**, so there's no
  hardware threshold to design against.
- On the Zero 2 W, header pins 2/4 sit directly on the 5 V rail [RPi-sch], with no fuse or
  cable drop on this path. The Pi's USB peripherals see the same rail.
- U10 today (R38 = 13.7 kΩ, D13): 4.98 V nominal, **4.82–5.14 V** worst case. That's
  inside USB's 4.75–5.25 V [USB2] in every corner, but below the 5.1 V Raspberry Pi
  asks for.
- Alternative R38 = 13.3 kΩ: 5.11 V nominal, 4.95–5.28 V worst case. That meets
  "5.1 V" nominally, but its top corner is 30 mV above USB's 5.25 V.

→ **Proposal for Nick (P-S4c-2):** **keep 13.7 kΩ.** There's no cable or fuse drop
between U10 and the Pi's rail, no detector to trip, and every corner stays inside the
USB VBUS range for the Pi's peripherals. The bench check becomes: 5V_PI at J1 stays
≥ 4.75 V [USB2] under the real load.

## 6. Still open (carried to SPEC §Open questions)

- U9 (FPF2700) payload current limit: datasheet still unavailable (onsemi link returns
  a landing page, 2026-10-05); Sofar Q3. The payload's share of "Left" above is limited
  by it.
- ADIN2111 at 2.4 V p-p and the other 3.3 V loads: replace the 0.30 W allowance with
  datasheet figures (analog.com timed out for the full datasheet).
- C56/C57 effective capacitance at 5 V: needs Murata SimSurfing (licence acceptance is Nick's).
- Pi Zero 2 W data-port VBUS wiring (D14 bench rule covers it either way).
