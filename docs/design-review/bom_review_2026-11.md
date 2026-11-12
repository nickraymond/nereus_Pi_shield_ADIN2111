# BOM review for the JLC order (2026-11-11)

*Board: `experiments/nick_raw_routing/`, layout frozen at tag `s9-layout-freeze` (board of step 24). Build: 20 boards,
JLC PCBA. Stock read Wed 2026-11-11, 4:24 to 4:31 PM Pacific, from JLC's parts search (not signed in). Stock changes
daily: read it again on the order screen.*

**The BOM:** [`bom_nick_raw_routing.csv`](bom_nick_raw_routing.csv) and [`bom_nick_raw_routing.pdf`](bom_nick_raw_routing.pdf),
53 lines, 108 fitted parts per board plus R11 (not fitted). They are exported from this board's own schematic, not
from the live project. `bom.csv` and `bom.pdf` in this folder belong to the live project and are older.

**Rule (Nick, 2026-11-11):** per line, Sofar's specified part or an alternate from Sofar's own list if JLC has it in
stock; then the parts already bought into JLC; only then a generic part JLC stocks. No global sourcing.

**Result:** 46 lines are ready to order: 35 from JLC stock as specified by Sofar or by us, 4 from JLC stock with a
generic part, 7 from the parts bought on 2026-10-18. One line is not fitted. Six lines are open, below.

## Open lines: questions for Nick

| # | Line | Question | Recommendation |
|---|---|---|---|
| 1 | **C22, C23** EEEFT1H470AP (Panasonic, 47 µF 50 V) | JLC's public stock is 0 and Sofar's file gives no alternate. Your review sheet of 10/23 says "Already ordered qty 60". Are they in My Parts Lib, ready for assembly? | If yes, nothing to do. If no, this line stops the order: there is no stocked like-for-like part, and a new electrolytic is barred by SPEC constraint 8. |
| 2 | **R15, R16** CRCW08057R50FKEAHP (Vishay, 7.5 Ω pulse-rated) | Same: public stock 0, no alternate in Sofar's file, the 10/23 sheet says 50 ordered. In My Parts Lib? | If no: YAGEO SR0805FR-477R5L (C873769, stock 5,492) fits the pads and the value, but states no pulse rating. That swap is yours and Sofar's to decide. |
| 3 | **R8** UR73D1JTTD10L0F (KOA, 10 mΩ shunt) | Public stock 0; the 10/23 sheet says 25 ordered, which is exactly 20 plus JLC's attrition of 5. In My Parts Lib? | If no, or if you want margin: **Sofar's own alternate 7, Stackpole CSRF0603FT10L0 (C346485), is in JLC stock: 9,822.** It is in the fields as ALT1. Its datasheet land pattern is not checked against R8's pads here; Sofar lists it for the same footprint. |
| 4 | **F1** BSMD1206-150-16V (BHFUSE, C883133) | It is a PPTC resettable fuse. SPEC constraint 8 bars PPTCs on newly sourced parts, because potting changes how they trip. In stock: 42,233. Keep it for this build? | Keep it: these 20 are development units without potting (DESIGN D32) and the layout is frozen. Record the exception; replace it before a potted build. |
| 5 | **J1** Pi socket, 2 × 20 | Still "TBD": the socket height is not chosen. In JLC stock today: ZHOURI 2.54-2*20 (C2977589, 37,698) and Megastar ZX-PM2.54-2-20PY (C7499354, 6,641), both 8.5 mm by JLC's text. Which one, or hand-solder a socket of your own? | Yours: it sets the board-to-Pi spacing. |
| 6 | **L1, L2** SRF1260-101M (Bourns) | Not blocking: JLC stock is 92 for a need of 40. The 10/23 sheet says 42 were also bought. Use yours or JLC's? | Use the 42 in My Parts Lib if they are there; else JLC stock covers it. |

Also for you to check on the order screen, not blocking:

- **My Parts Lib must show the seven lines bought on 2026-10-18** (order DOB202610190524705, JLC's estimate "ready
  2026-11-05"): U1 22, U2 / U3 42, L3 / L6 42, Y1 22, D1 27, D2 / D3 45, MP1 to MP4 84. I can't sign in to JLC, so their
  arrival is not verified. JLC's public stock would not cover them: 0, 33, 0, 0, 0, 10, 0.
- **U1 has two JLC listings**, C3226964 and C56341494. The fields carry C3226964; use the number My Parts Lib shows.
- **C16, C18, C24, C25:** JLC's page for C597304 names no maker ("--") for 08051C474KAT2A. The part number is KYOCERA
  AVX's, exactly as Sofar specifies. If you would rather have a named maker, ALT1 (YAGEO CC0805KKX7R0BB474, C596323,
  stock 240,022) is the earlier plan.
- **D4, D5:** pick the BOURNS listing C911382. JLC has two other makers' parts with the same name.
- **JLC's attrition** in the table is the figure on each public listing. JLC sets the final figure at the order.

## Lines changed in the schematic fields, and why

Only fields changed: PLANNED MPN / MFR / LCSC / NOTE, SOURCING, ALT. No value, footprint, wire or flag. The full list of
288 field changes is `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/field_changes.json`.

| Line | Before | Now | Why |
|---|---|---|---|
| C16, C18, C24, C25 | planned YAGEO CC0805KKX7R0BB474 (C596323) | **Sofar's 08051C474KAT2A** (C597304) | Sofar's part is in JLC stock now: 8,865, need 82. On 10/6 it had no listing |
| C19, C27 | planned KEMET C0805C102KDRACTU (C2167549) | **Sofar's C0805C102MDRACTU** (C2181610) | In JLC stock now: 188, need 40 |
| C21 | planned Taiyo Yuden UMK325AB7106KM-T (C386167) | **Sofar's CL32B106KBJNNNE** (C138687) | In JLC stock now: 77,751, need 20 |
| R21, R35, R36, R37, R43 | planned UNI-ROYAL 0402WGF1003TCE (C25741) | **Sofar's RMCF0402FT100K** (C7055151) | In JLC stock now: 1,058, need 110. The UNI-ROYAL part is JLC Basic and stays as ALT1 |
| R34 | planned YAGEO AC0402FR-079K09L (C227284) | **as specified, RC0402FR-079K09L** (C274897) | In JLC stock now: 4,378, need 30 |
| R47 | planned RC0402FR-071K5L with C11702 | **RC0402FR-071KL** (C106235) | 1 kΩ is Nick's decision of 2026-11-11. The old pair did not even agree with itself: C11702 is a UNI-ROYAL 1 kΩ part |
| C59 | planned MPN CL05A104KA5NNNC (100 nF) with C47129 | **CL05A224KA5NNNC** (C47129) | The value, the description (220 nF, U11 dVdT) and C47129 all say 220 nF; only the planned MPN was wrong |
| J3 | fields named "Planned MPN / MFR / LCSC" | same values in "PLANNED MPN / MFR / LCSC", plus note and sourcing | One spelling for every part, so the BOM export has one column. JST SM04B-SRSS-TB(LF)(SN), C160404, stock 75,275 |
| R8 | PLANNED LCSC "wait for JLC update"; no backups | C2482319; **ALT1 Stackpole CSRF0603FT10L0, ALT2 EATON MFL0603R0100FA** | Sofar's own alternates 7 and 1 from the mote file. Open line 3 |
| R15, R16 | PLANNED LCSC "wait for JLC update"; fields differed between the two | C313962; ALT1 YAGEO SR0805FR-477R5L on both | Open line 2 |
| C22, C23 | fields differed between the two | same on both | Open line 1 |
| U1, L3 / L6, Y1, D1, D3, MP2 to MP4 | PLANNED LCSC empty or "none shown yet" | JLC's part number: C3226964, C17230195, C6851222, C7083040, C3757753, C17256375 | JLC lists all of them now. Stock comes from the parts bought |
| every line | "in LCSC stock (checked 2026-10-06)", "JLC global sourcing ..." | "in JLC stock (read 2026-11-11)", or the 2026-10-18 order with its quantity | Notes brought up to the day; no global sourcing any more |

Four lines keep a generic part, because Sofar's part has no stock and Sofar's file gives no alternate:

| Line | Sofar's part (JLC stock) | Part to order | What matches |
|---|---|---|---|
| C17, C26 | C2012X7S2A105K125AB (0) | TDK C2012X7S2A105KT000N, C342785 (7,130) | Same maker and series, 1 µF ±10 % 100 V X7S 0805. Thickness not confirmed (Sofar's is 1.25 mm) |
| C31 | C1608X5R0J226M080AC (1) | Samsung CL10A226MQ8NRNC, C59461 (6,741,783; JLC Basic) | 22 µF ±20 % 6.3 V X5R 0603 |
| R14, R18 | RR0510P-101-D (0) | YAGEO RT0402BRD07100RL, C705627 (345,748) | 100 Ω thin film 0402, ±25 ppm; ±0.1 % against Sofar's ±0.5 % |
| R20, R39 | CRCW04021M82FKED (0) | RALEC RTT021824FTH, C166520 (7,566) | 1.82 MΩ ±1 % 62.5 mW 50 V ±100 ppm 0402 |

These four were already the planned parts in the review sheet of 10/23 (`experiments/nick_raw_routing/
pi_adin_shield_bom_for_review.xlsx`). Whether Sofar agreed to them is not recorded in the repo.

## Alternates in Sofar's mote file

Read from `KiCAD_reference_designs/20250409_BM_Mote_000639-AB/`: all 8 sheets, 170 parts, every field. Only three
parts carry an alternate, and one of them (Y2) is not on the shield.

| Part | Alternate in Sofar's file | JLC part | JLC stock 2026-11-11 |
|---|---|---|---|
| R8 (specified UR73D1JTTD10L0F: stock 0) | 1 MFL0603R0100FA | C6090593 (EATON) | 16, short of 20 |
| | 2 MFSA0603R0100FSM | C5441428 (EATON) | 0 |
| | 3 RL0816T-R010-F | C2073594 (SUSUMU) | 0 |
| | 4 D1MPC0603DR010FF-T5 | C9900113258 (no maker shown) | 0 |
| | 5 D1WEL0603MR010F-T5 | no listing | |
| | 6 ERJ-3LWFR010V | no listing | |
| | **7 CSRF0603FT10L0** | **C346485 (Stackpole)** | **9,822** |
| D1 (specified ST SMA6F33A: stock 2, obsolete) | **1 Vishay SMA6F33A-M3/H** | C7083040 | 0 public; **27 bought 2026-10-18** |
| | 2 ST SMA6F33AY | C3703808 | 0 |
| Y2 (Processor sheet, not on the shield) | Abracon ABS07L-32.768KHZ-T | not read | |

R15 / R16, D6 and D7 have a "MANUFACTURER PART NUMBER 1" field that repeats the specified part: not an alternate.
No other part has one. Detail: `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/mote_alternates.md`.

## How this BOM differs from the live project's `bom.csv`

`bom.csv` has 51 lines and 106 parts; this board has 53 lines and 109 parts.

- **Not on this board:** J5 as a part (it is two wire pads here, not in the BOM) and the 0 Ω jumpers R12, R13, R17,
  R19 (removed in Nick's commit `1c75bd3`, 2026-10-26).
- **Only on this board:** C59 (220 nF, U11 dVdT), F1 (fuse at J4), J3 (Qwiic), R9, R10, R24, R36, R47.
- **Different value:** R38 is 0402WGF1332TCE, 13.3 kΩ for 5.11 V (Nick's commit `629d4e8`, 2026-10-23); `bom.csv` and
  DESIGN D16 still say 13.7 kΩ.
- **In the schematic but not in either BOM:** J2 and J6 (headers, marked not fitted), J4 and J5 (wire pads),
  JP1 to JP4, H1 to H4, test points, fiducials.
- **Planned part differs:** the five lines that went back to Sofar's part, above.

## Stock table, read 2026-11-11 (4:24 to 4:31 PM Pacific)

Need = 20 boards × quantity + JLC's attrition for that listing. Source of every figure: JLC parts search, part page
`jlcpcb.com/partdetail/<number>`. Raw table and a second reading a few minutes later (one figure moved):
`~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/jlc_stock_2026-11-11.tsv`, `jlc_stock_recheck_2026-11-11.txt`.

| Refs | Per board | Part to order | JLC part | JLC stock | Attrition | Need | From |
|---|---|---|---|---|---|---|---|
| C1,C3,C9-C15,C28,C53 | 11 | CL05A104KA5NNNC | [C100072](https://jlcpcb.com/partdetail/C100072) | 1,198,302 | 14 | 234 | JLC stock |
| C2,C4 | 2 | CL05A105KP5NNNC | [C14445](https://jlcpcb.com/partdetail/C14445) | 9,916,974 | 10 | 50 | JLC stock |
| C5,C6 | 2 | CC0402KRX5R6BB684 | [C113784](https://jlcpcb.com/partdetail/C113784) | 133,600 | 10 | 50 | JLC stock |
| C7,C8 | 2 | CC0402JRNPO9BN150 | [C106997](https://jlcpcb.com/partdetail/C106997) | 2,001,264 | 10 | 50 | JLC stock |
| C16,C18,C24,C25 | 4 | 08051C474KAT2A | [C597304](https://jlcpcb.com/partdetail/C597304) | 8,865 | 2 | 82 | JLC stock |
| C17,C26 | 2 | C2012X7S2A105KT000N (Sofar: C2012X7S2A105K125AB) | [C342785](https://jlcpcb.com/partdetail/C342785) | 7,130 | 2 | 42 | JLC stock |
| C19,C27 | 2 | C0805C102MDRACTU | [C2181610](https://jlcpcb.com/partdetail/C2181610) | 188 | 0 | 40 | JLC stock |
| C20,C29,C49,C50,C54 | 5 | GRM188R72A104KA35D | [C77058](https://jlcpcb.com/partdetail/C77058) | 84,882 | 8 | 108 | JLC stock |
| C21 | 1 | CL32B106KBJNNNE | [C138687](https://jlcpcb.com/partdetail/C138687) | 77,751 | 0 | 20 | JLC stock |
| C22,C23 | 2 | EEEFT1H470AP | [C92059](https://jlcpcb.com/partdetail/C92059) | 0 | 0 | 40 | **open**: 60 ordered per the 10/23 sheet |
| C30,C55 | 2 | UMK107BBJ225KA-T | [C268016](https://jlcpcb.com/partdetail/C268016) | 109,767 | 8 | 48 | JLC stock |
| C31 | 1 | CL10A226MQ8NRNC (Sofar: C1608X5R0J226M080AC) | [C59461](https://jlcpcb.com/partdetail/C59461) | 6,741,783 | 10 | 30 | JLC stock |
| C32 | 1 | GRJ155R60J106ME11D | [C469527](https://jlcpcb.com/partdetail/C469527) | 16,593 | 4 | 24 | JLC stock |
| C33 | 1 | GRM155R60J475ME87D | [C76996](https://jlcpcb.com/partdetail/C76996) | 234,828 | 10 | 30 | JLC stock |
| C56,C57 | 2 | GRM21BR61C226ME44L | [C86817](https://jlcpcb.com/partdetail/C86817) | 694 | 4 | 44 | JLC stock |
| C58 | 1 | GRM155R61A475MEAAD | [C335105](https://jlcpcb.com/partdetail/C335105) | 173,888 | 10 | 30 | JLC stock |
| C59 | 1 | CL05A224KA5NNNC | [C47129](https://jlcpcb.com/partdetail/C47129) | 64,376 | 10 | 30 | JLC stock |
| D1 | 1 | SMA6F33A-M3/H (Sofar: SMA6F33A) | [C7083040](https://jlcpcb.com/partdetail/C7083040) | 0 | 0 | 20 | bought 2026-10-18, qty 27 |
| D2,D3 | 2 | RB058LAM-60TFTR | [C3757753](https://jlcpcb.com/partdetail/C3757753) | 10 | 0 | 40 | bought 2026-10-18, qty 45 |
| D4,D5 | 2 | CDSOD323-T36SC | [C911382](https://jlcpcb.com/partdetail/C911382) | 1,123 | 0 | 40 | JLC stock |
| D8 | 1 | KT-0603R | [C2286](https://jlcpcb.com/partdetail/C2286) | 6,090,401 | 10 | 30 | JLC stock |
| D9,D10 | 2 | KT-0603YG | [C2289](https://jlcpcb.com/partdetail/C2289) | 34,769 | 14 | 54 | JLC stock |
| F1 | 1 | BSMD1206-150-16V | [C883133](https://jlcpcb.com/partdetail/C883133) | 42,233 | 4 | 24 | JLC stock; **open**: PPTC |
| J1 | 1 | TBD | — | - | - | 20 | **open**: part not chosen |
| J3 | 1 | SM04B-SRSS-TB(LF)(SN) | [C160404](https://jlcpcb.com/partdetail/C160404) | 75,275 | 0 | 20 | JLC stock |
| L1,L2 | 2 | SRF1260-101M | [C6496096](https://jlcpcb.com/partdetail/C6496096) | 92 | 0 | 40 | JLC stock |
| L3,L6 | 2 | PA5432.822NLT | [C17230195](https://jlcpcb.com/partdetail/C17230195) | 0 | 0 | 40 | bought 2026-10-18, qty 42 |
| L4 | 1 | DFE201612E-2R2M=P2 | [C337893](https://jlcpcb.com/partdetail/C337893) | 33,715 | 2 | 22 | JLC stock |
| MP1-MP4 | 4 | 78614015360 | [C17256375](https://jlcpcb.com/partdetail/C17256375) | 0 | 1 | 81 | bought 2026-10-18, qty 84 |
| R1,R44-R46 | 4 | RC0402FR-071K5L | [C114759](https://jlcpcb.com/partdetail/C114759) | 3,172,355 | 10 | 90 | JLC stock |
| R2-R6,R9,R26,R27 | 8 | ERJ-2RKF4701X | [C400631](https://jlcpcb.com/partdetail/C400631) | 947,116 | 10 | 170 | JLC stock |
| R7,R10,R24 | 3 | RC0402JR-0710KL | [C60489](https://jlcpcb.com/partdetail/C60489) | 21,834,079 | 10 | 70 | JLC stock |
| R8 | 1 | UR73D1JTTD10L0F | [C2482319](https://jlcpcb.com/partdetail/C2482319) | 0 | 5 | 25 | **open**: 25 ordered per the 10/23 sheet |
| R11 | 1 | CRCW12100000Z0EA | [C844880](https://jlcpcb.com/partdetail/C844880) | 69,679 | 4 | 0 | DNP, not ordered |
| R14,R18 | 2 | RT0402BRD07100RL (Sofar: RR0510P-101-D) | [C705627](https://jlcpcb.com/partdetail/C705627) | 345,748 | 8 | 48 | JLC stock |
| R15,R16 | 2 | CRCW08057R50FKEAHP | [C313962](https://jlcpcb.com/partdetail/C313962) | 0 | 6 | 46 | **open**: 50 ordered per the 10/23 sheet |
| R20,R39 | 2 | RTT021824FTH (Sofar: CRCW04021M82FKED) | [C166520](https://jlcpcb.com/partdetail/C166520) | 7,566 | 10 | 50 | JLC stock |
| R21,R35-R37,R43 | 5 | RMCF0402FT100K | [C7055151](https://jlcpcb.com/partdetail/C7055151) | 1,058 | 10 | 110 | JLC stock |
| R22,R40 | 2 | RC0402FR-07200KL | [C114763](https://jlcpcb.com/partdetail/C114763) | 2,965,101 | 10 | 50 | JLC stock |
| R23 | 1 | RC0402FR-0722K1L | [C163478](https://jlcpcb.com/partdetail/C163478) | 1,693,215 | 10 | 30 | JLC stock |
| R34 | 1 | RC0402FR-079K09L | [C274897](https://jlcpcb.com/partdetail/C274897) | 4,378 | 10 | 30 | JLC stock |
| R38 | 1 | 0402WGF1332TCE | [C122547](https://jlcpcb.com/partdetail/C122547) | 97,859 | 10 | 30 | JLC stock |
| R41 | 1 | RC0402FR-071ML | [C138033](https://jlcpcb.com/partdetail/C138033) | 2,836,790 | 15 | 35 | JLC stock |
| R42 | 1 | RMCF0402FT10K0 | [C6111655](https://jlcpcb.com/partdetail/C6111655) | 3,199 | 10 | 30 | JLC stock |
| R47 | 1 | RC0402FR-071KL | [C106235](https://jlcpcb.com/partdetail/C106235) | 1,686,245 | 12 | 32 | JLC stock |
| T1,T2 | 2 | 74930000 | [C4354923](https://jlcpcb.com/partdetail/C4354923) | 1,752 | 0 | 40 | JLC stock |
| U1 | 1 | ADIN2111BCPZ | [C3226964](https://jlcpcb.com/partdetail/C3226964) | 0 | 0 | 20 | bought 2026-10-18, qty 22 |
| U2,U3 | 2 | AP22913CN4-7 | [C2150198](https://jlcpcb.com/partdetail/C2150198) | 33 | 0 | 40 | bought 2026-10-18, qty 42 |
| U4 | 1 | INA232AIDDFR | [C5447660](https://jlcpcb.com/partdetail/C5447660) | 3,077 | 0 | 20 | JLC stock |
| U5,U10 | 2 | LMR51430YDDCR | [C5210749](https://jlcpcb.com/partdetail/C5210749) | 5,287 | 0 | 40 | JLC stock |
| U6 | 1 | TPS62840YBGR | [C2071139](https://jlcpcb.com/partdetail/C2071139) | 3,039 | 0 | 20 | JLC stock |
| U11 | 1 | TPS26621DRCR | [C1848341](https://jlcpcb.com/partdetail/C1848341) | 4,808 | 0 | 20 | JLC stock |
| Y1 | 1 | ABM11W-25.0000MHZ-6-K1Z-T3 | [C6851222](https://jlcpcb.com/partdetail/C6851222) | 0 | 0 | 20 | bought 2026-10-18, qty 22 |

## Checks after the edits

- ERC: 39 items, the same types and counts as `erc_24.json`.
- DRC with schematic parity: counts identical to `drc_24.json` (3 skew errors, 16 excluded), 0 unconnected, parity 0.
- Netlist: nets identical before and after; reference, value and footprint identical on all 143 components.
- Board file: parity compares symbol fields with footprint fields, so the same field values went into the board's
  hidden footprint fields (285 changes, 70 of them new hidden fields on the Fab layers). With those fields taken out,
  the board is byte for byte the board of tag `s9-layout-freeze`
  (`scripts/bom_fields_board_sync_2026_11.py --verify`). No copper, part, outline or silkscreen changed.
- Reports: `~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/` (`erc_after.json`, `drc_after.json`,
  `net_before.net`, `net_after.net`).

Regenerate: `python3 experiments/nick_raw_routing/scripts/bom_fields_2026_11.py` (dry run; `--write` edits), then
`bom_fields_board_sync_2026_11.py`; the CSV with the `kicad-cli sch export bom` line in DEV_LOG's entry of 2026-11-11;
the PDF with `python3 tools/bompdf.py docs/design-review/bom_nick_raw_routing.csv docs/design-review/bom_nick_raw_routing.pdf "<board>" "<note>"`.

## Not done here

- No datasheet was read for this review. Ratings in the notes are JLC's listing text or carried over from
  `bom_alternates.md` (2026-10-06).
- The placement file (which footprints JLC should place) is the design session's task.
- DESIGN D16 (R38), D26 / D27 (sourcing policy) and the Sofar brief still describe the earlier plan; they are the
  design session's documents.
- `bom_lifecycle.md`, `bom_alternates.md` and `jlc_parts_buy_2026-10.md` are left as the record of October.
