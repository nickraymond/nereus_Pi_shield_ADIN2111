# BOM lifecycle and stock check (S5.e)

*Checked 2026-10-06 against main `e62d974` (all parts on the schematic). Stock figures change daily: recheck before
ordering. Part of the S6 design-review package.*

**Scope:** 50 unique parts, 105 placements, from the exported netlist. Excluded: test points, fiducials, mounting holes,
R11 (DNP), JP1/JP2 (copper links, not in the BOM).

**Build size:** 20 boards (Nick). A part is flagged when LCSC stock is below 20 × its per-board quantity, when it has no
LCSC listing, when it has no real part number, or when it is not Active.

**Sources:**
- **Lifecycle:** Digi-Key "Product Status" unless marked. The TI parts are from ti.com. Most other manufacturer sites
  refused automated access (403, time-outs, JavaScript-only pages).
- **Stock:** lcsc.com product pages read on 2026-10-06.
- **JLC Basic/Extended:** the label on jlcpcb.com part pages. Almost everything is Extended, so expect a per-part-type
  setup fee.
- **Caveat:** "None found" means no LCSC listing turned up in web searches restricted to lcsc.com/jlcpcb.com. LCSC's own
  search can't be queried automatically, so it isn't proof the part is absent; confirm in a browser before deciding.
- **Method:** the research was split across four read-only research agents. The design agent spot-checked their
  results: the SMA6F33A obsolete status on Digi-Key, LMR51430YDDCR stock on LCSC, and D1/R8's second-source fields in
  the netlist.

## Summary

| Result | Parts |
|---|---|
| OK (Active, LCSC stock ≥ 20 boards) | 29 (the KENTO LEDs' lifecycle is unverified: no manufacturer page) |
| **Obsolete** | 1: D1 SMA6F33A (ST). Sofar's own fields name second sources |
| **No real part number** | 1: J1 (open decision: socket height) |
| **Low stock** | 1: U2/U3 AP22913CN4-7 (30 < 40) |
| **Out of stock at LCSC** | 6: J5, R21/R35/R37/R43, C17/C26, C21, C22/C23, C31 |
| **No LCSC listing found** | 12: U1, MP1–MP4, L3/L6, Y1, D2/D3, R34, C16/C18/C24/C25, C19/C27, R14/R18, R15/R16, R8, R20/R39 |

**Every flagged part except J1 is Active and in stock at Digi-Key or Mouser.** The issue is JLC/LCSC availability, not
lifecycle (apart from D1).

**Constraints (SPEC hard constraints 7 and 8):** every Sofar part stays exactly as specified. Buying the exact part
(JLC global sourcing or consigned) keeps both constraints. Substituting any Sofar part would need Nick to amend
constraint 8, and constraint 7 as well for power-path parts (D1–D3, R8, R15/R16, C22/C23, L1/L2 …). Only these may
change without an amendment:
- Sofar's own listed alternates (D1, R8).
- The parts we sourced ourselves (J1, J5, R34, the LEDs, …).

**Sourcing policy (Nick, 2026-10-06; DESIGN D26):**
- **Critical parts:** buy the exact part through **JLC global sourcing**. This covers U1, U2/U3, L3/L6, Y1, D1–D3,
  MP1–MP4 and J5.
- **Passives:** the specified part stays on the schematic. Pin-compatible, generic, LCSC-stocked alternates are recorded
  as hidden `ALT…` fields next to it (S5.h), as **proposals for Sofar's design review**.
- Adopting any alternate for a Sofar part is a later decision, made with Sofar, that needs a constraint amendment. The
  bespoke PoDL/power-path parts (R8, R15/R16, C22/C23) are flagged "Sofar review".
- **First build:** every flagged passive is also bought exact through JLC global sourcing (or consigned) until an
  alternate is approved, so the 20-board order can be placed.
- **Done in S5.h:** the alternates are now hidden symbol fields (`ALT1 MPN/MFR/LCSC`, `ALT2 MPN/MFR/LCSC`, `ALT NOTE`)
  on the 24 flagged passives, and `SOURCING` is set on those and on every critical part. `tools/check.sh` exports them
  to the tracked `docs/design-review/bom.csv`: Sofar's specified part stays in the `Value (MPN)` column, alternates sit
  beside it. Values and their LCSC check: `docs/design-review/bom_alternates.md`. In KiCad: Tools → Edit Symbol Fields.

## Decisions needed (proposed, not applied; rows marked † need a constraint amendment)

| Part (refs) | Problem | Suggested route | Why |
|---|---|---|---|
| J1 Pi socket | no part number | choose height later (Nick); candidates ZHOURI C2977589 / Megastar C7499354, both 8.5 mm | open until the board-to-board spacing is known |
| D1 SMA6F33A (bus TVS) | ST part obsolete | Sofar's second source **Vishay SMA6F33A-M3/H** (same DO-221AC, 600 W, 33 V; Vishay datasheet 89458) via global sourcing | already Sofar-approved in the part fields |
| U1 ADIN2111BCPZ | no LCSC listing | global sourcing or consign (DK 120) | no equivalent part |
| MP1–MP4 Würth 78614015360 | no LCSC listing | JLC global sourcing (DK 7,835) | the LCSC insert found needs a footprint change; JLC lists taller Würth M3 inserts (3.0 / 4.0 mm) if a taller insert were acceptable |
| L3/L6 PA5432.822NLT | no LCSC listing | global sourcing or consign | vetted power-path inductor; XAL6060 is not a confirmed drop-in |
| Y1 ABM11W 25 MHz | no LCSC listing | JLC global sourcing (DK 87) | LCSC same-family crystals aren't drop-ins (one −20…+70 °C vs −40…+125 °C, one 8 pF load); others need an ADIN2111 crystal-spec check |
| C22/C23 EEEFT1H470AP | out of stock | global sourcing (DK 78,606) | a newly sourced replacement must be potting-safe, so not another electrolytic |
| U2/U3 AP22913CN4-7 | 30 in stock, need 40 | JLC global sourcing for all 40 (simplest), or LCSC 30 + DK balance | no drop-in |
| J5 SM02B-GHS-TB | out of stock | global sourcing (DK 10,839) | GH lookalikes' land patterns unchecked |
| R15/R16 CRCW08057R50FKEAHP | no LCSC listing | global sourcing (Sofar review) | pulse-proof PoDL damping part; Yageo SR0805 alternate† has unverified pulse rating and ±200 vs ±100 ppm/°C |
| D2/D3 RB058LAM-60TFTR | no LCSC listing | **JLC global sourcing** (policy). Alternate for review†: RB088LAM-60TFTR (same family/package, higher current) | constraint 7 (power path) |
| R8 UR73D1JTTD10L0F | no LCSC listing | one of Sofar's 7 listed alternates (no amendment needed; none found at LCSC) or global sourcing; ROHM/Vishay 10 mΩ 0603 for review† (Sofar review) | Sofar-approved list exists |
| Commodity R/C: R34, R20/R39, R14/R18, R21/R35/R37/R43, C16/C18/C24/C25, C19/C27, C17/C26, C21, C31 | no listing / out of stock | specified parts stay; LCSC alternates recorded as `ALT…` fields (S5.h) for Sofar review† (R34 is ours: no amendment) | value-for-value; R21 group's UNI-ROYAL part is JLC Basic |

**Watch items (no action now):**
- L1/L2 SRF1260-101M: LCSC 137 (thin margin). Bourns PCN IC25029 changes assembly only, not EOL.
- T1/T2 Würth 74930000: LCSC 295; Digi-Key has 0, with a 37-week lead time.
- C30/C55 UMK107BBJ225KA-T has been renamed MSASU168BB5225KTNA01 by Taiyo Yuden.
- KYOCERA AVX is renumbering its MLCCs (distributor notice).
- L4's footprint is named DFE201612C, but the part is the E series; the land patterns haven't been compared.
- D4/D5: LCSC also lists a same-named ElecSuper part. Order the Bourns one.
- The KENTO LEDs have no published lifecycle.

## Full table

| MPN | Mfr | Refs | Qty / 20 boards | Lifecycle | LCSC | LCSC stock | JLC | Status | Notes / alternates |
|---|---|---|---|---|---|---|---|---|---|
| Raspberry_Pi_2_3 | — | J1 | 1 / 20 | — | — | — | — | NO MPN | Generic 2×20 female socket footprint only; part to choose (height open). Candidates: ZHOURI 2.54-2*20 C2977589 (32,515; 8.5 mm insulator; Ext), Megastar ZX-PM2.54-2-20PY C7499354 (10,148; 8.5 mm, gold; Ext). UrchinCam's Amphenol 95157-440LF is a male SMD header: not usable |
| SM02B-GHS-TB | JST | J5 | 1 / 20 | Active (DK) | C189893 | 0 (out of stock) | Ext | OUT OF STOCK | DK 10,839. LCSC GH-type lookalikes (land pattern unchecked): HCTL HC-GH-2PWT C2845397 (1,400), JUSHUO GH125-S02DCA-00 C2886765 (10,670) |
| 78614015360 | Würth Elektronik | MP1, MP2, MP3, MP4 | 4 / 80 | Active (DK) | none found | — | — | NO LCSC LISTING | DK 7,835 (M3, 1.5 mm, OD 6.0). Würth 9774015360R has the same dimensions (no LCSC). LCSC Sinhoo SMTSO3015CTJ C2915632 is Ø5.56 mm: needs a footprint change |
| ERJ-2RKF4701X | Panasonic | R2, R3, R4, R5, R6, R26, R27 | 7 / 140 | Active (DK) | C400631 | 184,700 | Ext | OK |  |
| RMCF0402FT100K | Stackpole | R21, R35, R37, R43 | 4 / 80 | Active (DK; AEC-Q200) | C7055151 | 0 (out of stock) | — | OUT OF STOCK | UNI-ROYAL 0402WGF1003TCE C25741 (2,432,700; **JLC Basic**); Yageo RC0402FR-07100KL C60491 (8,367,900). Same value/tol/power/TCR; AEC-Q200 not stated |
| CL05A104KA5NNNC | Samsung | C1, C3, C9, C10, C11, C12, C13, C14, C15, C28, C53 | 11 / 220 | Active (DK) | C100072 | 2,632,100 | Ext | OK |  |
| CL05A105KP5NNNC | Samsung | C2, C4 | 2 / 40 | Active (DK) | C14445 | 924,800 | Ext | OK |  |
| CC0402KRX5R6BB684 | Yageo | C5, C6 | 2 / 40 | Active (DK) | C113784 | 142,800 | Ext (probable) | OK |  |
| CC0402JRNPO9BN150 | Yageo | C7, C8 | 2 / 40 | Active (DK) | C106997 | 2,229,300 | Ext | OK |  |
| KT-0603R | Hubei KENTO | D8 | 1 / 20 | unverified (no mfr page) | C2286 | 2,601,000 | Basic | OK (lifecycle unverified) |  |
| KT-0603YG | Hubei KENTO | D9, D10 | 2 / 40 | unverified (no mfr page) | C2289 | 24,100 | Ext (probable) | OK (lifecycle unverified) |  |
| RC0402FR-071K5L | Yageo | R1, R44, R45, R46 | 4 / 80 | Active (DK) | C114759 | 1,002,200 | Ext | OK |  |
| ADIN2111BCPZ | Analog Devices | U1 | 1 / 20 | Active (DK) | none found | — | — | NO LCSC LISTING | DK 120 (tray; -R7 reel also listed). No equivalent: buy/consign or JLC global sourcing |
| AP22913CN4-7 | Diodes Inc. | U2, U3 | 2 / 40 | Active (DK) | C2150198 | 30 | Ext | LOW STOCK (30 < 40) | DK 52,413. No LCSC drop-in. LCSC 30 + DK balance, consigned |
| ABM11W-25.0000MHZ-6-K1Z-T3 | Abracon | Y1 | 1 / 20 | Active (DK) | none found | — | — | NO LCSC LISTING | DK 87. LCSC 25 MHz 6 pF 2016 alternates, need an ADIN2111 crystal-spec check: TKD SX20Y025000B61T002 C20623595 (11,920; −30…+85 °C), Murata XRCGB25M000F3A00R0 C467842 (6,140; ±35/±35 ppm) |
| GRM188R72A104KA35D | Murata | C20, C29, C49, C50, C54 | 5 / 100 | Active (DK) | C77058 | 49,730 | Ext | OK |  |
| RB058LAM-60TFTR | ROHM | D2, D3 | 2 / 40 | Active (DK) | none found | — | — | NO LCSC LISTING | ROHM RB088LAM-60TFTR C5336606 (5,135; same SOD-128, 60 V, 5 A); RB058LAM100TR C962680 (115; higher V_F) |
| RC0402FR-079K09L | Yageo | R34 | 1 / 20 | Active (DK) | none found | — | — | NO LCSC LISTING | Yageo AC0402FR-079K09L C227284 (7,700; same series, automotive); UNI-ROYAL 0402WGF9091TCE C11549 (4,100) |
| RC0402FR-071ML | Yageo | R41 | 1 / 20 | Active (DK) | C138033 | 1,826,500 | Ext | OK |  |
| RMCF0402FT10K0 | Stackpole | R42 | 1 / 20 | Active (DK) | C6111655 | 3,900 | Ext | OK |  |
| TPS26621DRCR | Texas Instruments | U11 | 1 / 20 | ACTIVE (TI, family page) | C1848341 | 8,038 | Ext | OK |  |
| 08051C474KAT2A | KYOCERA AVX | C16, C18, C24, C25 | 4 / 80 | Active (DK) | none found | — | — | NO LCSC LISTING | Yageo CC0805KKX7R0BB474 C596323 (250,730); AVX 08051C474K4Z2A C597303 (750). AVX MLCC part-number migration (distributor notice, Oct 2026) |
| C2012X7S2A105K125AB | TDK | C17, C26 | 2 / 40 | Active (DK) | C2182292 | 0 (out of stock) | Ext | OUT OF STOCK | TDK C2012X7S2A105KT000N C342785 (10,140); Murata GCM21BC72A105KE36L C126585 (23,540) |
| C0805C102MDRACTU | KEMET | C19, C27 | 2 / 40 | Active (DK) | none found | — | — | NO LCSC LISTING | KEMET C0805C102KDRACTU C2167549 (3,715; ±10%); Walsin 0805B102K102CT C303890 (182,650) |
| CL32B106KBJNNNE | Samsung | C21 | 1 / 20 | Active (DK; DK 0, 61 wk) | C138687 | 0 (out of stock) | Ext | OUT OF STOCK | FH 1210B106K500NT C116808 (17,642); Taiyo Yuden UMK325AB7106KM-T C386167 (5,670) |
| EEEFT1H470AP | Panasonic | C22, C23 | 2 / 40 | Active (DK; DK 78,606) | C92059 | 0 (out of stock) | Ext | OUT OF STOCK | Aluminium electrolytic (bus input). A newly sourced replacement must be potting-safe (SPEC constraint): keep this part via global sourcing, or redesign. Substitutes not assessed |
| SMA6F33A | STMicroelectronics | D1 | 1 / 20 | **Obsolete** (DK: "Obsolete and no longer manufactured") | none found | — | — | OBSOLETE | Sofar's fields already list second sources: Vishay **SMA6F33A-M3/H** (MPN1) and ST SMA6F33AY (MPN2; RS "intend to remove"). No LCSC listing found for either. DK subs: ST SMA6J33A-TR (SMA pkg), Littelfuse SMA6L33A |
| CDSOD323-T36SC | Bourns | D4, D5 | 2 / 40 | Active (DK) | C911382 | 2,674 | Ext | OK | LCSC C22363665 is an ElecSuper part with the same name: not Bourns |
| SRF1260-101M | Bourns | L1, L2 | 2 / 40 | Active (DK) | C6496096 | 137 | Ext | OK (thin margin) | Bourns PCN IC25029 (assembly/glue change from DC 2540; not EOL) |
| CRCW12100000Z0EA | Vishay Dale | R12, R13, R17, R19 | 4 / 80 | Active (DK) | C844880 | 6,990 | Ext | OK |  |
| RR0510P-101-D | Susumu | R14, R18 | 2 / 40 | Active (DK) | none found | — | — | NO LCSC LISTING | Yageo RT0402BRD07100RL C705627 (326,300; 0.1 %, 25 ppm thin film); Panasonic ERA2AEB101X C445575 (3,280; AEC-Q200) |
| CRCW08057R50FKEAHP | Vishay Dale | R15, R16 | 2 / 40 | Active (DK) | none found | — | — | NO LCSC LISTING | Pulse-proof 0.5 W 0805 (PoDL damping). Yageo SR0805FR-477R5L C873769 (8,360; 0.5 W; pulse rating/AEC not verified) |
| 74930000 | Würth Elektronik | T1, T2 | 2 / 40 | Active (DK) | C4354923 | 295 | Ext | OK | DK 0, 37-week lead time |
| RC0402JR-0710KL | Yageo | R7 | 1 / 20 | Active (DK) | C60489 | 12,252,700 | Ext | OK |  |
| UR73D1JTTD10L0F | KOA Speer | R8 | 1 / 20 | Active (DK) | none found | — | — | NO LCSC LISTING | Sofar's fields list 7 approved 10 mΩ 0603 alternates (e.g. Murata MFL0603R0100FA, Panasonic ERJ-3LWFR010V, Stackpole CSRF0603FT10L0); LCSC options found: ROHM PMR03EZPFU10L0 C308571 (1,390), Vishay WSLP0603R0100FEA C5334451 (4,990); land patterns to check |
| INA232AIDDFR | Texas Instruments | U4 | 1 / 20 | ACTIVE (TI) | C5447660 | 14,958 | Ext | OK |  |
| UMK107BBJ225KA-T | Taiyo Yuden | C30, C55 | 2 / 40 | Renamed: MSASU168BB5225KTNA01 "Mass Production (Preferred)" (Taiyo Yuden) | C268016 | 122,670 | Ext | OK | Record the new part number |
| C1608X5R0J226M080AC | TDK | C31 | 1 / 20 | Active (DK; DK 0 until 2027-01) | C2167532 | 0 (out of stock) | Ext | OUT OF STOCK | Samsung CL10A226MQ8NRNC C59461 (5.27 M; Basic per mirror only); Murata GRM188R60J226MEA0D C77042 (77,150). Thickness vs 1.0 mm footprint not checked |
| GRJ155R60J106ME11D | Murata | C32 | 1 / 20 | Active (DK) | C469527 | 28,390 | Ext | OK |  |
| GRM155R60J475ME87D | Murata | C33 | 1 / 20 | Active (DK) | C76996 | 128,840 | Ext | OK |  |
| GRM21BR61C226ME44L | Murata | C56, C57 | 2 / 40 | Active (DK) | C86817 | 5,305 | Ext | OK |  |
| GRM155R61A475MEAAD | Murata | C58 | 1 / 20 | Active (DK) | C335105 | 179,780 | Ext | OK |  |
| PA5432.822NLT | Pulse (YAGEO group) | L3, L6 | 2 / 40 | Active (DK) | none found | — | — | NO LCSC LISTING | Twin PM5432.822NLT C17666871 out of stock. Coilcraft XAL6060-822MEC C19191627 (655; Isat 8.4 A; footprint and rated current to check). Bourns SRP6060FA-8R2M C2045598 (17: not enough) |
| DFE201612E-2R2M=P2 | Murata | L4 | 1 / 20 | Active (DK) | C337893 | 13,455 | Ext | OK | Footprint named DFE201612C; land pattern vs the E series not compared |
| CRCW04021M82FKED | Vishay Dale | R20, R39 | 2 / 40 | Active (DK) | none found | — | — | NO LCSC LISTING | RALEC RTT021824FTH C166520 (7,500; same 1.82 MΩ 1 % 100 ppm 62.5 mW 50 V 0402) |
| RC0402FR-07200KL | Yageo | R22, R40 | 2 / 40 | Active (DK) | C114763 | 3,014,900 | Ext | OK |  |
| RC0402FR-0722K1L | Yageo | R23 | 1 / 20 | Active (DK) | C163478 | 1,779,100 | Ext | OK |  |
| RC0402FR-0713K7L | Yageo | R38 | 1 / 20 | Active (DK) | C274888 | 290,500 | Ext | OK |  |
| LMR51430YDDCR | Texas Instruments | U5, U10 | 2 / 40 | ACTIVE (TI) | C5210749 | 7,155 | Ext | OK |  |
| TPS62840YBGR | Texas Instruments | U6 | 1 / 20 | ACTIVE (TI) | C2071139 | 3,630 | Ext | OK |  |
