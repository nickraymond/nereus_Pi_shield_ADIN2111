# Routing scripts for Nereus_Pi_Shield_Adin2111 (until 2026-11-12: nick_raw_routing)

Scripted board edits, one file per step of the routing plan (2026-11-10). Each script loads
`../Nereus_Pi_Shield_Adin2111.kicad_pcb` with KiCad's own Python (`pcbnew`), makes its edits, checks what it
did, and saves. KiCad must be closed while a script runs.

```bash
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
$PY Nereus_Pi_Shield_Adin2111/scripts/step0_fixes.py
```

- `boardio.py` loads and saves. A save is followed by one more load and save, because KiCad's
  writer only settles (no further diff) on the second pass.
- `normalize.py` is a load and save with no edit. Run once on the zip board so later diffs show
  only real changes.
- `step0_fixes.py` holds the fixes made before any routing. It refuses to run twice.
- `rename_project_2026_11.py` renamed the project and its sheets on 2026-11-12 (run once; names only).
- `verify_against_freeze.py` proves the board still is the frozen layout (tag `s9-layout-freeze`), apart from
  the hidden BOM fields and the sheet file names. Run it after any change to the board file.

After every step: `kicad-cli pcb drc --refill-zones --schematic-parity --severity-all`.
Check outputs and renders go to `~/NereusData/nereus_Pi_shield_ADIN2111/`, not into git.
