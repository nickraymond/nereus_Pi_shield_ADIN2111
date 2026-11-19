#!/bin/sh
# Step 0c: rebuild the board from the committed starting board and the committed schematic, with the gate checks.
# Everything runs on copies outside git (pcbnew.SaveBoard rewrites the .kicad_pro beside the board); only the
# .kicad_pcb is copied back into the worktree. Nothing is committed. Written new (the Pi Zero work's run.sh did the
# same copy-in / compare-project-files round trip).
set -e
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
OUT=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0/0c
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
P=N6_Shield_ADIN2111; N=Nereus_Pi_Shield_Adin2111
REFB=KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb
if pgrep -lf KiCad | grep -v kicad-cli | grep -q .; then echo "KiCad is running: close it first"; exit 1; fi
mkdir -p "$OUT/ref"; rm -rf "$OUT/work" "$OUT/start"; mkdir -p "$OUT/work" "$OUT/start"
git -C ../.. show "origin/development:$REFB" > "$OUT/ref/BM_Mote_000639-AB.kicad_pcb"
git -C ../.. archive HEAD $P | tar -x -C "$OUT/work" --strip-components=1      # the committed project: schematic, rules, libraries, starting board
git -C ../.. archive HEAD $P | tar -x -C "$OUT/start" --strip-components=1
( cd "$OUT/work" && $K sch export netlist -o "$OUT/netlist_0c.net" $N.kicad_sch >/dev/null )
test -s "$OUT/netlist_0c.net"
$PY step0c_board.py "$OUT/work/$N.kicad_pcb" "$OUT/ref/BM_Mote_000639-AB.kicad_pcb" "$OUT/netlist_0c.net" "$OUT/work" 2>"$OUT/step0c.err" | grep -v "swig/python detected" | tee "$OUT/step0c.log" | grep -v -E "^  (PAD|PART|SPOT) "
# the project file as committed, in case SaveBoard touched it, before any check runs
for f in $N.kicad_pro $N.kicad_dru; do git -C ../.. show "HEAD:$P/$f" > "$OUT/work/$f"; done
$PY lockcheck_0c.py "$OUT/start/$N.kicad_pcb" "$OUT/work/$N.kicad_pcb" "$OUT/ref/BM_Mote_000639-AB.kicad_pcb" 2>/dev/null | tee "$OUT/lock_0c.txt"
( cd "$OUT/start" && $K pcb drc --schematic-parity --severity-all --format json -o "$OUT/drc_start.json" $N.kicad_pcb >/dev/null 2>&1 || true )
( cd "$OUT/work" && $K pcb drc --schematic-parity --severity-all --format json -o "$OUT/drc_0c.json" $N.kicad_pcb >/dev/null 2>&1 \
  && $K pcb drc --schematic-parity --severity-all --format report -o "$OUT/drc_0c.rpt" $N.kicad_pcb >/dev/null 2>&1 )
python3 -B drcsum.py "$OUT/drc_0c.json" "$OUT/drc_start.json" | tee "$OUT/drcsum_0c.txt"
cp "$OUT/work/$N.kicad_pcb" "../../$P/$N.kicad_pcb"
echo "files that differ from HEAD in $P (must be the board only):"; git -C ../.. status --short -- $P
# zone refill with KiCad's own filler, on a copy
rm -rf "$OUT/refill"; cp -R "$OUT/work" "$OUT/refill"
( cd "$OUT/refill" && $K pcb drc --refill-zones --save-board --schematic-parity --severity-all --format json -o "$OUT/drc_0c_refilled.json" $N.kicad_pcb >/dev/null 2>&1 || true )
# Decision of the first-pass session after its own check (2026-11-17): the board kept in git is the REFILLED one.
# Sofar's fills as turned are stale (they pass the new east edge and run through the header pads: 53 DRC errors);
# fills are derived data, so KiCad's own refill replaces them and the lock check then compares outlines only.
for f in $N.kicad_pro $N.kicad_dru; do cmp -s "$OUT/refill/$f" "$OUT/work/$f" || { echo "kicad-cli changed $f"; exit 1; }; done
$PY lockcheck_0c.py "$OUT/start/$N.kicad_pcb" "$OUT/refill/$N.kicad_pcb" "$OUT/ref/BM_Mote_000639-AB.kicad_pcb" --outlines-only 2>/dev/null | tee "$OUT/lock_0c_refilled.txt" | tail -3
cp "$OUT/refill/$N.kicad_pcb" "../../$P/$N.kicad_pcb"
echo "DRC with zones refilled (scratch copy only):"; python3 -B drcsum.py "$OUT/drc_0c_refilled.json" "$OUT/drc_0c.json" | grep -E "^(violations|unconnected|schematic)|error" | tee "$OUT/drcsum_0c_refilled.txt"
# renders and STEP for Nick
S0=$HOME/NereusData/nereus_Pi_shield_ADIN2111/n6_shield/stage0
( cd "$OUT/work" && $K pcb render --side top --quality basic --width 1500 --height 2100 -o "$S0/N6_shield_stage0c_top.png" $N.kicad_pcb >/dev/null 2>&1
  $K pcb render --side bottom --quality basic --width 1500 --height 2100 -o "$S0/N6_shield_stage0c_bottom.png" $N.kicad_pcb >/dev/null 2>&1
  $K pcb export step --drill-origin --subst-models --include-silkscreen --force -o "$S0/N6_shield_stage0c.step" $N.kicad_pcb >"$OUT/step_export.log" 2>&1 || true )
ls -la "$S0"/N6_shield_stage0c*
# proof that nothing but the board differs from the commit
git -C ../.. diff --quiet HEAD -- $P/$N.kicad_pro $P/$N.kicad_dru $P/*.kicad_sch $P/*.kicad_sym $P/fp-lib-table $P/sym-lib-table $P/mote.pretty $P/nereus.pretty $P/urchin.pretty \
  && echo "project file, rule file, all sheets, symbol and footprint libraries: byte-identical to $(git -C ../.. rev-parse --short HEAD)"
