# N6 shield: rough-layout STEP files for CAD review

Mechanical mocks only, exported from KiCad scratch boards on 2026-11-17 (`scripts/n6_rough_board.py`): no routing of
ours, no DRC, small parts of ours left out. Committed at Nick's request so they can be pulled on the CAD machine.
What each mock is and what is still open: `FIRST_PASS.md`, section 3.

| File | Mock | Outline |
|---|---|---|
| `step/N6_shield_mock_D_top_entry_rough.step` | D: N6 width, through-hole pin headers, top-entry JST | 35.56 x 60.5 mm |
| `step/N6_shield_mock_F_one_column_rough.step` | F: surface-mount pin headers, all connectors in one east column, 4 holes | 46.5 x 54.5 mm |
| `step/N6_shield_mock_G_west_wall_rough.step` | G: narrower F, connectors on the west wall 3 mm apart, 4 holes | 40.1 x 56.0 mm |

Origin of every file: the N6's board corner at the USB end on the VIN side; +X towards the P0 column, +Y towards the
camera end. The view convention (which header column is P0 to P6 seen from the back) is assumed, see `N6_FACTS.md`.
The motor driver chip U12 is missing from the models (its 3D file is not in the project). Mounting holes are drawn
at 2.7 mm; the size is not decided.
