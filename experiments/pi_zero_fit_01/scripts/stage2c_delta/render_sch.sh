#!/bin/sh
# PDF of the schematic and crops of the two changed areas of the Top-Level sheet (macOS sips).
S=$(cd "$(dirname "$0")/.." && pwd); K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cd "$S/board"
$K sch export pdf -o "$S/schematic_stage2c.pdf" Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1
$K sch export pdf --pages 2 -o "$S/build_2c/p2.pdf" Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null
sips -s format png -Z 7000 "$S/build_2c/p2.pdf" --out "$S/build_2c/p2.png" >/dev/null 2>&1
python3 - "$S" <<'PY'
import subprocess, sys
S = sys.argv[1]; s = 7000 / 594
for name, x0, y0, x1, y1 in (("crop_motor.png", 170, 280, 405, 350), ("crop_adc.png", 405, 278, 590, 350)):
    subprocess.run(["sips", "-c", str(int((y1 - y0) * s)), str(int((x1 - x0) * s)), "--cropOffset", str(int(y0 * s)), str(int(x0 * s)),
                    S + "/build_2c/p2.png", "--out", S + "/build_2c/" + name], capture_output=True)
PY
