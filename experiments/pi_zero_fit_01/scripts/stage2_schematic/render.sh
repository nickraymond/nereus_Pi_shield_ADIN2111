#!/bin/sh
# PDF of the whole schematic, a PNG of the Top-Level sheet and crops of the changed areas (macOS sips).
cd "$(dirname "$0")"
S=..
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cd $S/board
$K sch export pdf -o ../schematic_stage2.pdf Nereus_Pi_Shield_Adin2111.kicad_sch | tail -1
$K sch export pdf --pages 2 -o ../render/s2_p2.pdf Nereus_Pi_Shield_Adin2111.kicad_sch >/dev/null
sips -s format png -Z 7000 ../render/s2_p2.pdf --out ../render/s2_p2.png >/dev/null 2>&1
sips -s format png -Z 2400 ../render/s2_p2.pdf --out ../render/s2_p2_small.png >/dev/null 2>&1
python3 - <<'PY'
import subprocess
s = 7000 / 594
for name, x0, y0, x1, y1 in (("crop_motor.png", 195, 280, 405, 350), ("crop_adc.png", 405, 278, 560, 350),
                             ("crop_bus.png", 420, 75, 570, 155), ("crop_j1.png", 15, 10, 215, 195), ("crop_payload.png", 55, 205, 235, 295)):
    subprocess.run(["sips", "-c", str(int((y1 - y0) * s)), str(int((x1 - x0) * s)), "--cropOffset", str(int(y0 * s)), str(int(x0 * s)),
                    "../render/s2_p2.png", "--out", "../render/" + name], capture_output=True)
PY
