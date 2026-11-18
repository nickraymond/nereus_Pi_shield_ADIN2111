# N6 shield: rough-layout STEP files for CAD review

Mechanical mocks only, exported from KiCad scratch boards on 2026-11-17 (`scripts/n6_rough_board.py`): no routing of
ours, no DRC, small parts of ours left out. Committed at Nick's request so they can be pulled on the CAD machine.
What each mock is and what is still open: `FIRST_PASS.md`, section 3.

| File | Mock | Outline |
|---|---|---|
| `step/N6_shield_mock_D_top_entry_rough.step` | D: N6 width, through-hole pin headers, top-entry JST | 35.56 x 60.5 mm |
| `step/N6_shield_mock_F_one_column_rough.step` | F: surface-mount pin headers, all connectors in one east column, 4 holes | 46.5 x 54.5 mm |
| `step/N6_shield_mock_G_west_wall_rough.step` | G: narrower F, connectors on the west wall 3 mm apart, 4 holes | 40.1 x 56.0 mm |
| `step/N6_shield_mock_H_n6_south_east_rough.step` | H: N6 in the shield's south-east corner, all connectors on the west wall, 2.1 mm holes | 38.56 x 60.3 mm |
| `step/N6_shield_mock_I_through_hole_rough.step` | I: both headers through-hole, BM1 / BM2 / 5 V west, MOTOR / POT / QWIIC east, 2.1 mm holes | 43.7 x 59.5 mm |
| `step/N6_shield_mock_J_bm_north_south_rough.step` | J: both headers through-hole, BM1 south, BM2 north, N6 width, 2.1 mm holes | 35.56 x 66.8 mm |
| `step/N6_shield_mock_K_wide_west_rough.step` | K: both headers through-hole, BM1 south, BM2 north, 5 V and MOTOR / POT / QWIIC on a wider west side, 2.1 mm holes | 45.56 x 63.3 mm |
| `step/N6_shield_mock_L_short_rough.step` | L: mock K with BM2 beside L2 on the west, shorter | 45.56 x 56.2 mm |
| `step/N6_shield_mock_M_narrow_west_rough.step` | M: mock L with a narrower west side (MOTOR, BM1, QWIIC south; POT turned on the west wall) | 42.36 x 56.2 mm |
| `step/N6_shield_mock_N_after_review_rough.step` | N: mock L with the review's placement changes (driver and ADC beside their connectors, BM1 turned, holes 3.0 mm in) | 46.36 x 56.6 mm |
| `step/N6_shield_mock_P_north_row_rough.step` | P: east edge flush with the N6, MOTOR / POT / BM2 / QWIIC in a north row, BM1 beside T1 with its two bus tracks drawn, south edge 1.4 mm past the N6, three 2.7 mm holes | 42.16 x 60.7 mm |

Origin of every file: the N6's board corner at the USB end on the VIN side; +X towards the P0 column, +Y towards the
camera end. The view convention (which header column is P0 to P6 seen from the back) is assumed, see `N6_FACTS.md`.
The motor driver chip U12 is missing from the models (its 3D file is not in the project). Mounting holes are 2.7 mm
placeholders on F and G, and 2.1 mm on H to N, 2.7 mm on P (Nick, 2026-11-17).
