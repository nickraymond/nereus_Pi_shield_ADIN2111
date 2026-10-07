# Footprint types and courtyards (S6.c)

*Set 2026-10-06 by `tools/fpattrs.py` on the `Vault` library (`nereus_Pi_shield_ADIN2111/mote.pretty`, the 43 footprints
extracted read-only from Sofar's board in S4.d). Library only: the board picks these up when Nick updates footprints
from the library (pcbnew: Tools → Update Footprints from Library). Pads untouched: `fpextract.py --verify` → 0 problems.*

**Why:** the Altium import left every footprint with no type (no SMD/through-hole `attr`), so JLC's SMD-only position file
would drop parts, and no `F.CrtYd` courtyard (their outlines sit on Altium mechanical layers, imported as User.N), so
KiCad's courtyard DRC couldn't see overlaps (QE S4.d N3).

**Type** (KiCad stock-library conventions): `smd` for every placed part; fiducial `smd exclude_from_bom`; test pad and
mounting hole `exclude_from_pos_files exclude_from_bom`.

**Courtyard** (F.CrtYd rectangle, 0.05 mm lines), first match wins: (1) Sofar's courtyard rectangle (thin lines on a User
layer enclosing the pads); (2) Sofar's largest User-layer outline enclosing the pads (body/assembly outline);
(3) computed: pads ∪ silkscreen ∪ fab + 0.25 mm (IPC-7351 nominal), only where no User outline exists.

| Footprint | Used by | Type | Courtyard (mm) | Source |
|---|---|---|---|---|
| 78614015360-Footprint-2 | J1, MP2, MP3, MP4 | `smd` | 7.80x7.80 | Sofar's outer outline, User.14 |
| ADIN2111BCPZ-Footprint-1 | U1 | `smd` | 9.12x9.12 | computed: pads+silk+fab+0.25 |
| AP22913CN4-7-Footprint-1 | U2, U3 | `smd` | 1.00x1.00 | Sofar's outer outline, User.1 |
| CAPC1608X100X20ML10 | C31 | `smd` | 3.40x2.10 | Sofar's courtyard rectangle, User.13 |
| CAPC2013X145X50LL20T25 | C19, C27 | `smd` | 2.70x1.70 | Sofar's courtyard rectangle, User.14 |
| CRCW08057R50FKEAHP-Footprint-1 | R15, R16 | `smd` | 2.70x1.70 | Sofar's courtyard rectangle, User.13 |
| FIDUCIAL_075MM | FID1, FID2, FID3, FID4, FID5, FID6 | `smd exclude_from_bom` | 2.25x2.25 | Sofar's outer outline, User.13 |
| FP-0603-L_1_6_0_2-W_0_8_0-MFG | C30, C55 | `smd` | 2.30x1.20 | Sofar's outer outline, User.5 |
| FP-0805-L_2_01_0_2-W_1_25-MFG | C18, C24, C25, U11 | `smd` | 3.20x1.65 | Sofar's outer outline, User.14 |
| FP-74930000-MFG | T1, T2 | `smd` | 5.38x3.62 | Sofar's outer outline, User.5 |
| FP-ABM11W-MFG | Y1 | `smd` | 2.35x1.95 | Sofar's outer outline, User.14 |
| FP-C2012-125-0_2-MFG | C17, C26 | `smd` | 2.85x1.65 | Sofar's outer outline, User.14 |
| FP-CC0402-0_55-IPC_B | C7, C8 | `smd` | 1.77x1.00 | Sofar's outer outline, User.14 |
| FP-CC0402-MFG | C5, C6 | `smd` | 1.75x1.00 | Sofar's outer outline, User.14 |
| FP-CL278-IPC_C | C1, C3, C9, C10, C11, C12, C13, C14, C15, C28, C53 | `smd` | 1.47x0.75 | Sofar's outer outline, User.5 |
| FP-CL32-IPC_C | C21 | `smd` | 4.10x3.00 | Sofar's outer outline, User.5 |
| FP-CL511-IPC_C | C2, C4 | `smd` | 1.47x1.00 | Sofar's outer outline, User.14 |
| FP-CRCW0402-e3-MFG | R20, R39 | `smd` | 1.85x1.00 | Sofar's outer outline, User.14 |
| FP-CRCW1210-e3-IPC_B | R11, R12, R13, R17, R19 | `smd` | 4.61x3.21 | Sofar's outer outline, User.14 |
| FP-DFE201612C-MFG | L4 | `smd` | 2.60x2.00 | Sofar's outer outline, User.14 |
| FP-FTD-MFG | C22, C23 | `smd` | 8.70x7.30 | Sofar's outer outline, User.5 |
| FP-GRJ155-0_2-MFG | C32 | `smd` | 1.60x1.00 | Sofar's outer outline, User.14 |
| FP-GRM155-0_15-MFG | C33 | `smd` | 1.60x1.00 | Sofar's outer outline, User.14 |
| FP-GRM188-0_1-e0_2_0_5-IPC_B | C20, C29, C49, C50, C54 | `smd` | 2.91x1.41 | Sofar's outer outline, User.5 |
| FP-PA5432_472NLT-MFG | C56, L6 | `smd` | 7.00x6.80 | Sofar's outer outline, User.5 |
| FP-PMDTM-MFG | D2, D3 | `smd` | 6.00x2.90 | Sofar's outer outline, User.14 |
| FP-RC0402-0_4-IPC_B | R23, R38 | `smd` | 1.77x1.00 | Sofar's outer outline, User.14 |
| FP-RC0402-0_4-IPC_C | R7 | `smd` | 1.47x1.00 | Sofar's outer outline, User.14 |
| FP-RMCF0402-IPC_C | R21, R35, R37, R41, R43 | `smd` | 1.51x0.75 | Sofar's outer outline, User.5 |
| FP-RR0510-IPC_B | R14, R18 | `smd` | 1.77x1.00 | Sofar's outer outline, User.14 |
| FP-SOD-323-MFG | D4, D5 | `smd` | 3.20x1.65 | Sofar's outer outline, User.14 |
| FP-YBG0006-MFG | U6 | `smd` | 2.00x2.50 | Sofar's outer outline, User.14 |
| Hole_M3 | MTG1, MTG2, MTG3, MTG4 | `exclude_from_pos_files exclude_from_bom` | 8.50x8.50 | computed: pads+silk+fab+0.25 |
| INA232AIDDFR-Footprint-1 | U4 | `smd` | 4.16x3.72 | computed: pads+silk+fab+0.25 |
| PCB_TP_1.5mm | TP1, TP2, TP3, TP5, TP7, TP8, TP13, TP19, TP20, TP21, TP22, TP23, TP24, TP35, TP36, TP38 | `exclude_from_pos_files exclude_from_bom` | 1.80x1.80 | Sofar's outer outline, User.11 |
| RESC1005X40X25LL05T05 | R2, R3, R4, R5, R6, R26, R27 | `smd` | 1.50x0.80 | Sofar's courtyard rectangle, User.13 |
| RESC1005X40X25LL05T10 | R22, R34, R40 | `smd` | 1.50x0.80 | Sofar's courtyard rectangle, User.14 |
| RESC1005X40X25ML05T10 | D8, R44, R45, R46 | `smd` | 2.10x1.10 | Sofar's courtyard rectangle, User.13 |
| RESC1005X40X25NL05T10 | — | `smd` | 1.80x0.90 | Sofar's courtyard rectangle, User.13 |
| RESC1608X60X55ML20T10 | R8 | `smd` | 3.40x2.10 | Sofar's courtyard rectangle, User.14 |
| SMA6F33A-Footprint-1 | D1 | `smd` | 6.56x3.66 | computed: pads+silk+fab+0.25 |
| SOT-23-THIN-6_DDC_TEX | U5, U10 | `smd` | 5.03x4.32 | Sofar's outer outline, User.5 |
| SRF1260-101M-Footprint-1 | L1, L2 | `smd` | 13.00x13.51 | Sofar's outer outline, User.13 |

Sources: 8 Sofar courtyard rectangles, 31 Sofar outer outlines, 4 computed (ADIN2111, INA232, SMA6F33A, Hole_M3).
