# Power budget — shield + Pi + payload (S4.c)

*Part of the S6 design-review package. Every figure carries its source; anything
assumed is labelled as an assumption. Reproduce the arithmetic from the tables below.*
*Written 2026-10-05 (S4.c; revised after QE round 1). Owner/gate: **Nick***

## Sources

| Tag | Source |
|---|---|
| [RPi-docs] | [Raspberry Pi documentation, "Power supply"](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply), read 2026-10-05 |
| [RPi-brief] | Raspberry Pi Zero 2 W product brief, "Published April 2024" (datasheets.raspberrypi.com) |
| [RPi-sch] | Raspberry Pi Zero 2 W reduced schematic, RPI-ZERO2W_R1, 2021-10-15 |
| [TI] | TI LMR51430 datasheet SLUSEF4A (Nov 2022): §7.3, §7.4 thermal, §7.5, Figure 7-2 (5 V efficiency, 1.1 MHz) |
| [P890] | Pulse P890.B (01/22), PA5432.822NLT |
| [FPF] | Fairchild FPF2700/2701/2702 datasheet, Rev. 1.0.3 (Dec 2013), via Rochester Electronics; supplied by Nick 2026-10-05 |
| [ADI] | [ADIN2111 product page](https://www.analog.com/en/products/adin2111.html), read 2026-10-05 |
| [E] | Sofar, *Bristlemouth Evolution: More Power Delivery* (SPEC confirmed facts) |
| [SRF] | Bourns SRF1260 datasheet (SPEC confirmed facts): SRF1260-101M series mode, DCR 0.656 Ω max |
| [IPC] | IPC-2221 external-conductor current formula: I = 0.048 · ΔT^0.44 · A^0.725 (A in mil²) |
| [USB2] | USB 2.0 specification, Table 7-7: VBUS at a high-power port 4.75–5.25 V |

## 1. Limits and loads

**Two limits apply, and they're different (QE S4.c F1):**

| Limit | Value | What it is |
|---|---|---|
| **Bristlemouth v1 per-module draw** | **≤ 12 W** from a nominal 24 V bus [E] | What the bus and host are specified to supply to one module: this shield + Pi + payload |
| **Port-inductor rating (D12)** | **890 mA** absolute max per port inductor [E]: 21.4 W at 24 V, 14.2 W at 16 V | Hardware ceiling for everything through L1/L2: own load **and** current passing through to other modules |

The bus runs from 16 V to 32 V [E]. VBUS on the shield sits behind L1 (DCR 0.656 Ω [SRF]),
so VBUS = bus − I · 0.656 Ω (QE S4.c F2). The tables below solve that.

**Loads:**

- **Pi Zero 2 W** [RPi-docs]: recommended PSU **2 A**, typical bare-board active **350 mA**.
  Camera Module **250 mA**, HDMI 50 mA, GPIO 50 mA total, USB devices 100–1000 mA each.
  [RPi-brief]: input power **5 V DC 2.5 A**, operating temperature **−20 °C to +70 °C**.
  USB peripherals the Pi powers draw from the same rail, so from U10 when JP1 is bridged.
  **Target (D15, Nick): ≤ 1 A continuous** (Pi + its USB devices). Typical + camera +
  GPIO is ≈ 650 mA, which leaves 350 mA for USB devices.
- **Shield 3.3 V domain** (ADIN2111, INA232, pull-ups, via U5): ADIN2111 is **77 mW
  typical** (dual supply, 1.0 V p-p) [ADI]. The 2.4 V p-p figure and the other ICs
  aren't sourced, so the budget uses an **allowance of 0.30 W at U5's input** (≈ 4× the
  ADIN figure). *Assumption, to be replaced by datasheet numbers.*
- **U10 efficiency** (5 V, 1.1 MHz, PFM, VIN 24 V), read from [TI] Figure 7-2:
  ≈ 88 % at 0.35 A, ≈ 89 % at 0.65 A, ≈ 90 % at 1 A, ≈ 89 % at 2 A, ≈ 88 % at 2.5 A
  (±2 points, read from a graph; slightly conservative per QE). *Note: the figure's
  legend repeats "PFM, VIN=24V" (and 12 V), but above 0.35 A all 24 V curves agree
  within ~2 points.* The same values are used at 16 V.
- **Payload port (U9 FPF2700, R34 = 374 kΩ)**: [FPF] Eq. 1, R_SET (kΩ) = 277.5 / I_LIM(TYP) (A)
  → **I_LIM ≈ 0.74 A typical, 0.59–0.89 A** (±20 % at 25 °C [FPF] electrical table);
  short-circuit limit 0.75 × I_LIM (VOUT < 2 V); off after 0.5 ms blanking and retries
  every 127.5 ms (FPF2700); 88 mΩ typical; 2.8–36 V; thermal shutdown 140 °C. **R11
  (0 Ω across U9) bypasses all of this if fitted** (SOFAR_QUESTIONS Q2). **FPF2700MX
  is obsolete** (Digi-Key, 2026-10-05). Nick: find a replacement JLC can source (S5);
  its current limit should match ≈ 0.74 A typical.

## 2. Budget against both limits

Shield input = U10 input + 0.30 W. Bus current solves I · (bus − 0.656 · I) = shield input.

| Pi load | Shield input | 12 W limit: left for payload | 24 V bus: I / VBUS / left of 890 mA | 16 V bus: I / VBUS / left of 890 mA |
|---|---|---|---|---|
| 0.35 A (typical [RPi-docs]) | 2.28 W | 9.7 W (≈ 405 mA) | 95 mA / 23.94 V / 795 mA | 143 mA / 15.91 V / 747 mA |
| 0.65 A (typical + camera + GPIO) | 3.94 W | 8.1 W (≈ 336 mA) | 165 mA / 23.89 V / 725 mA | 249 mA / 15.84 V / 641 mA |
| **1.0 A (D15 target)** | **5.83 W** | **6.2 W (≈ 257 mA)** | 245 mA / 23.84 V / 645 mA | 370 mA / 15.76 V / 520 mA |
| 2.0 A (recommended PSU) | 11.49 W | 0.5 W | 485 mA / 23.68 V / 405 mA | 741 mA / 15.51 V / 149 mA |
| 2.5 A (input rating) | 14.45 W | **−2.5 W (over)** | 612 mA / 23.60 V / 278 mA | 939 mA / 15.38 V / **−49 mA (over)** |

(mA under "12 W" are at 24 V.)

**Reading:**

- **The 12 W per-module limit is the tighter one.** At the D15 target the payload gets
  ≈ 6.2 W. The 890 mA rating leaves 645 mA at 24 V for payload **plus** pass-through.
- **U9 doesn't enforce the budget.** Its limit (≈ 0.74 A typical, ≈ 17.8 W at 24 V) is
  well above 6.2 W. A 1 A Pi plus a payload at U9's limit is ≈ 0.99 A, over 890 mA as
  well. So the payload budget has to come from the payload's own design, or from
  software watching the shield's INA232 (U4 on the R8 shunt, which measures this
  module's bus current).
- **Shield heat from L1:** at the shield's own 245 mA, L1 dissipates 39 mW. At a full
  890 mA through the port it's 0.52 W with a 0.58 V drop. That's the same order as
  U10's loss, and it's heat inside the potting (§3).

→ **Decided (D17, Nick):** the payload port stays as Sofar designed it (U9 with
R34 → ≈ 0.74 A limit). Payloads are small devices (e.g. another sensor that needs
switching on); none runs near the limit, so there's no extra budget enforcement.
The 12 W figure above is for information. U9 itself is obsolete and gets a
JLC-sourceable replacement in S5 (§1).

## 3. Shield heat: U10, L6, L1

Loss = Pout · (1/η − 1); L6 share = I² · 26.4 mΩ (DCR max [P890]); the rest is in U10.
ΔTj = U10 loss × RθJA, with 107.8 °C/W (JEDEC) or 80 °C/W (TI's 2-layer example) [TI] §7.4.

| Pi load | Total loss | L6 | U10 | ΔTj @ 107.8 °C/W | ΔTj @ 80 °C/W |
|---|---|---|---|---|---|
| 0.35 A | 0.24 W | 3 mW | 0.23 W | 25 °C | 19 °C |
| 0.65 A | 0.40 W | 11 mW | 0.39 W | 42 °C | 31 °C |
| 1.0 A | 0.55 W | 26 mW | 0.53 W | 57 °C | 42 °C |
| 2.0 A | 1.23 W | 106 mW | 1.13 W | 121 °C | 90 °C |
| 2.5 A | 1.70 W | 165 mW | 1.53 W | 165 °C | 123 °C |

**These ΔTj numbers are indicative, not a design guarantee (QE S4.c F3):**
- TI says its RθJA "is only valid for comparison … and cannot be used for design
  purposes" [TI] §7.4. It points to a "Maximum Output Current Versus Ambient
  Temperature" section that doesn't appear in SLUSEF4A.
- Figure 7-2 is at TA = 25 °C. RDS(on) rises when hot, so losses at high Tj are
  somewhat higher than shown.
- Potting changes everything here (SPEC constraint 8).

**Reading:** U10's temperature limits the Pi's load. At the **D15 target (≤ 1 A)** the
rise is moderate. At 2 A and above the junction gets near 150 °C, beyond which TI
derates lifetime ([TI] §7.3 note 5); thermal shutdown is at 163 °C typical [TI] §7.5.
The Pi itself is rated to +70 °C ambient [RPi-brief], which matters inside a sealed,
potted housing next to U10 and L1. L6 is comfortable (Iheat 8 A [P890]).

**Bring-up check (quantitative):** measure U10's top-of-case temperature T_top under the
real load. Then Tj ≈ T_top + ψJT · P_U10, with ψJT = 9.3 °C/W [TI] §7.4, which is
≈ +5 °C at 0.53 W.

## 4. JP1 bridge (1.0 mm copper, D14)

[IPC], external layer, 1 oz (35 µm, *assumed*; Nick's stack-up decides): A = 54.3 mil²
→ **2.4 A at ΔT 10 °C, 3.2 A at ΔT 20 °C.** Resistance of the 1.7 mm bridge
≈ 0.84 mΩ, so 2 mV drop at 2.5 A. **Adequate** for the D15 target and even for the
2.5 A worst case at ~20 °C rise.

## 5. Pi supply voltage (decided: D16, keep R38 = 13.7 kΩ)

- [RPi-docs]: "All models require a 5.1V supply". The low-voltage detector (4.63 V
  ±5 %) exists on all models since the B+ "**except the Zero range**". **The Zero 2 W
  has no undervoltage detector.**
- On the Zero 2 W, header pins 2/4 sit directly on the 5 V rail [RPi-sch], with no fuse
  or cable drop on this path. The Pi's USB peripherals see the same rail.

| R38 | Nominal | Worst case (VREF ±1.5 %, 1 % R) | Against USB 4.75–5.25 V [USB2] |
|---|---|---|---|
| **13.7 kΩ (D13; kept, D16)** | 4.98 V | 4.82–5.14 V | inside; low corner 70 mV above 4.75 V |
| 13.5 kΩ (E192; QE option) | 5.04 V | 4.88–5.21 V | centred: 130 mV / 40 mV margins |
| 13.3 kΩ | 5.11 V | 4.95–5.28 V | top corner 30 mV over 5.25 V |

Nick chose to keep 13.7 kΩ (D16). Caveat from QE: at the low corner, load regulation
(≈ −15 mV to 1 A, Figure 7-4 at 500 kHz) plus header contact drop leave ~30–50 mV above
the 4.75 V bench threshold. **Bench check:** 5V_PI at J1 stays ≥ 4.75 V under the real
load. If it doesn't, 13.5 kΩ is the drop-in fix.

## 6. Still open (carried to SPEC §Open questions)

- Is R11 fitted on production motes (Sofar Q2)? If it is, the payload has no current limit.
- ADIN2111 at 2.4 V p-p and the other 3.3 V loads: replace the 0.30 W allowance.
- C56/C57 effective capacitance at 5 V (Murata SimSurfing; licence acceptance is Nick's).
- Pi Zero 2 W data-port VBUS wiring (the D14 bench rule covers it either way).
