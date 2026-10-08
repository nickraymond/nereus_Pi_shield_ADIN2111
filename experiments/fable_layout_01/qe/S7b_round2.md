# QE review — PR #30 (S7.b) — Round 2 — 2026-10-08

*Received from the S7 QE session; saved verbatim beside round 1.*

**Verdict:** CHANGES REQUESTED
**Reviewed:** 0903d87 (board md5 3faf7cb… confirmed), from a `git archive` copy in my scratchpad. Fresh kicad-cli DRC, my own pcbnew checks, your blockcheck/check_fixed/check_rules re-run on the copy, a full `tools/build_all.sh` rebuild on a separate copy, and one probe copy with the netclass edited (scratch only).

## Round-1 findings: verified
| # | Result | Evidence |
|---|---|---|
| F1 copper-defect warnings | ✓ fixed | Fresh DRC: hole_to_hole 0, holes_co_located 0, via_dangling 0, track_dangling 0 (r1: 14/3/23/50). Errors unchanged: 110, same items (the only non-MP/T1/T2 errors are the same 12 courtyard pairs). 258 warnings, now silk/text/padstack/lib only |
| F2 J1 plane wall | ✓ fixed | Plane clearance 0.25; GND In2 is 1 island (2,134 mm²); along the pin columns x 25.23 / 27.77 the GND and VBUS main islands are copper at 345/350 sample points, as in M4 |
| F3 totals | ✓ | REPORT §1 quotes the fresh blockcheck (byte-identical to my re-run): 242 pads, tracks 627/742, vias 152/176, 0 missing, 139 trimmed, 308 extra (sum checked) |
| F4 U3 3V3 | ✓ | DRC unconnected = 1 (J1 pins 1/17 only); §4/§7 corrected |
| F5, N1, N2, N3, N5 | ✓ declared | REPORT §5/§6/§9; rules.md re-run identical |
| F6 insert copper | ✓ | My scan: no other-net tracks, vias or pads within r 4.8 of MP1–4; only the plane edges at 4.80. check_fixed now tests copper: 0 failures |
| N4 rebuild | ✓ | Full rebuild (3 m 43 s, 17 dangling rounds): DRC identical by type and count, unconnected 1; segments 2079 vs 1936 committed, BM2_DATA_N 23.8 in the rebuild vs 23.4 committed (§8 says DRC-equivalent, not identical) |
| Scope | ✓ | Nothing outside experiments/fable_layout_01/ (`git diff --name-only a5f812c...0903d87`) |

## New findings
| # | Severity | Finding | Evidence | Suggested fix |
|---|---|---|---|---|
| R2-F1 | **MAJOR** (undeclared; present since M3, missed in my round 1) | **U4 (INA232) no longer senses R8 directly.** R8 is the 10 mΩ shunt (UR73D1JTTD10L0F, SPEC). On the mote, U4.1 (P_IN) → R8.2 and U4.2 (VBUS) → R8.1 are dedicated 0.203 mm traces, 6.6 and 7.0 mm long, with no via (pad-to-pad). They detour west out of the SENSE region (mote x < 144.4), so the M3 copy clipped them there, at x 17.85 on the shield. In round 1 the clipped halves were among the dangling stubs; round 2's dangling.py trimmed them (most of SENSE's 24 trimmed tracks are those P_IN/VBUS legs). Now each U4 sense pin reaches only a via into its plane: U4.1 → via (16.4, 14.8), U4.2 → via (17.4, 15.6). R8.1 → via (20.0, 18.9), and R8.2 → vias and L2.1/R17.2 through new copper. So vias and plane copper in the main current path sit inside the measurement, which is significant against 10 mΩ. REPORT §3 "Sofar's sense routing intact" and §9 #5 "R8/U4 … 100 %" rest on blockcheck matching items inside the region, which doesn't test pad-to-pad connectivity | My track-only path search, R8 ↔ U4 per net: mote VBUS 6.82 mm / P_IN 6.45 mm (9 items each); shield r1 and r2: NO TRACK PATH on either net. Flood from each pad listed above | Copy the whole Kelvin traces: widen SENSE's region to the mote's detour, or re-lay two dedicated 0.2 mm traces from U4.1/U4.2 to the R8 pad ends, with no via into the planes. Add a pad-to-pad track-connectivity check (U4.1↔R8.2, U4.2↔R8.1) to check_rules. Correct §3/§9 |
| R2-F2 | **MAJOR** (claim false) | **The `bus` netclass is ignored by the plane fill and by DRC.** REPORT §4 says "the fill and DRC honour (measured: 0.35 to BM vias, 0.25 to the others)". The class has no `priority` key, so Default (0.15) resolves first. Proof: with bus clearance raised to **1.0 mm**, kicad-cli DRC still gives 110 errors, unchanged. With `"priority": 0` added at 0.35, DRC reports **76 extra clearance errors**. 37 are planes (GND In2, VBUS/P_IN In4, the Q10 no-net island) at **0.2505 mm** from bus vias, e.g. BM1_N (10.16, 45.92), BM2_P (11.34, 16.53), BM2_N (17.60, 30.80). The rest are tracks, vias and pads at 0.15–0.33 mm: BM1_P via (11.95, 27.63) ↔ BM1_N via (11.80, 26.90) at 0.15; ~{ADIN_P2_LED1}/ADIN_MOSI/ADIN_PWR on Internal 2 at 0.20–0.31 from the BM2_N via (17.60, 30.80); 1V8 Internal 1 (12.40, 43.20) at 0.225 from a BM1_P via; ADIN_VDDIO via (16.90, 28.90) at 0.22 from BM2_N; GND via (7.90, 22.40) at 0.25 from the BM2_N feed. Two are T1/T2 pads 6↔7 at 0.24 (Sofar's footprint). rules.md lists 1 bus item, because it checks new tracks only, not vias or zones | `.kicad_pro` net_settings: bus has no "priority" (Default has −1); pcbnew reports BM2_N's effective class as "bus,Default". The probe DRCs were run on copies in my scratchpad only | Add `"priority": 0` to the bus class (or use a netclass pattern), refill, re-route the offenders, re-run DRC, and keep the class active in the committed .kicad_pro so DRC enforces 0.35. Extend check_rules to vias, pads and zone fills, or simply rely on DRC once the class resolves |
| R2-F3 | MINOR | §1's headline "every copied block reproduced on the mote's geometry to within 0.001 mm" now has 139 copied items deleted (115 tracks, 24 vias: ADIN 34, SENSE 24, DAMP2 19, P1L 19, P2L 12, B33/B5V 8 each, P1T 7, B18 6, P2T 2). Trimming dead stubs is reasonable, but it also deleted the evidence of R2-F1 | blockcheck.md trimmed list | Say "matched except 139 trimmed stubs", and have dangling.py report trimmed items that sat on a pad-to-pad path on the mote |
| R2-N1 | NIT | §1 typo: "blockcheck: 242/242 pads; copper pads 242/242, …; copper items 928.;" | REPORT.md §1 | Tidy |

## Could not verify
- Whether R2-F1's error matters at the bus currents of interest (it depends on the via/plane resistance inside the sense loop). Restoring Sofar's Kelvin routing is the fidelity requirement either way (BRIEF §5 SENSE, §8.5).

## Repo untouched
My worktree: git status clean before and after. Your worktree: untouched (I ran nothing there). Every run, including the netclass probe and the rebuild, used copies in my scratchpad.
