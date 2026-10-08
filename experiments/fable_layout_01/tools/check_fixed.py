#!/usr/bin/env python3
"""Check BRIEF §3 positions and §4 keep-outs on the board (read only). Exit 1 on any failure.

  $PY tools/check_fixed.py [--heights heights.json]

Positions ±0.05 mm; J1 pin 1 proven at (25.23, 8.37) seen from the top; nothing within r 3.0 of a Pi hole or r 3.5
of a housing hole (both sides); no part within r 4.8 of an insert; top-side parts ≥ 2.0 mm from each 50 W envelope;
bottom-side parts ≤ 3 mm tall (heights table, M2). Parts parked outside the outline (x > 40) are reported, not checked.
"""
import json
import math
import sys

import pcbnew

import geom
from geom import mm

TOL = 0.05
# recorded deviations from BRIEF §4 (REPORT.md): ref -> (accepted gap, reason)
ALLOWANCES = {"U1": (1.75, "ADIN block 0.3 mm east of the brief's pocket so Sofar's U1 west-side fan-out stays 0.5 mm from the edge; U1's body is 2.1 mm from the envelope")}


def main(heights_path=None):
    board = geom.load()
    fps = geom.fp_by_ref(board)
    fails, infos = [], []

    def expect(ref, want, what=None):
        got = geom.xy(fps[ref].GetPosition())
        d = geom.dist(got, want)
        (infos if d <= TOL else fails).append(f"{what or ref}: at ({got[0]:.3f}, {got[1]:.3f}), want {want} (d {d:.3f})")

    # J1 by pads, seen from the top
    pads = {p.GetNumber(): geom.xy(p.GetPosition()) for p in fps["J1"].Pads()}
    for num, want in (("1", (25.23, 8.37)), ("2", (27.77, 8.37)), ("39", (25.23, 56.63)), ("40", (27.77, 56.63))):
        d = geom.dist(pads[num], want)
        (infos if d <= TOL else fails).append(f"J1 pin {num}: ({pads[num][0]:.3f}, {pads[num][1]:.3f}), want {want}")
    (infos if fps["J1"].IsFlipped() else fails).append(f"J1 side: {'bottom' if fps['J1'].IsFlipped() else 'TOP'} (want bottom)")
    for ref, p in {**geom.PI_HOLES, **geom.HOUSING_HOLES, **geom.INSERTS}.items():
        expect(ref, p)
    for ref in geom.INSERTS:
        (infos if fps[ref].IsFlipped() else fails).append(f"{ref} side: {'bottom' if fps[ref].IsFlipped() else 'TOP'} (want bottom, as the mote)")
    expect("J5", geom.J5_POS)
    rot = fps["J5"].GetOrientationDegrees()
    (infos if abs(rot - geom.J5_ROT) < 0.01 else fails).append(f"J5 rotation {rot} (want {geom.J5_ROT}, face south)")
    for ref, e in geom.ENVELOPES.items():
        expect(ref, ((e[0] + e[2]) / 2, (e[1] + e[3]) / 2), f"{ref} centred in its envelope")
        (infos if not fps[ref].IsFlipped() else fails).append(f"{ref} side: {'BOTTOM' if fps[ref].IsFlipped() else 'top'}")
    # insert ring copper: arc r 3.03 w 1.2 ~290°, 7 vias 0.6/0.254 at r 3.0, on the insert's net
    for ref, p in geom.INSERTS.items():
        net = f"/Top-Level Schematic/{geom.INSERT_NET[ref]}"
        arcs = [t for t in board.GetTracks() if t.GetClass() == "PCB_ARC" and geom.dist(geom.xy(t.GetCenter()), p) < 0.01]
        vias = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and abs(geom.dist(geom.xy(t.GetPosition()), p) - 3.0) < 0.01]
        ok = (len(arcs) == 1 and abs(mm(arcs[0].GetRadius()) - 3.03) < 0.001 and abs(mm(arcs[0].GetWidth()) - 1.2) < 0.001
              and abs(arcs[0].GetAngle().AsDegrees() - 290) < 0.5 and arcs[0].GetNetname() == net
              and len(vias) == 7 and all(v.GetNetname() == net and abs(mm(v.GetWidth(pcbnew.F_Cu)) - 0.6) < 0.001
                                         and abs(mm(v.GetDrillValue()) - 0.254) < 0.001 for v in vias))
        (infos if ok else fails).append(f"{ref} ring: {len(arcs)} arc, {len(vias)} vias on {geom.INSERT_NET[ref]}" + ("" if ok else " (MISMATCH)"))

    # keep-outs over placed parts
    heights = {}
    if heights_path:
        h = json.load(open(heights_path))["by_footprint"]
        heights = {ref: h.get(str(fp.GetFPID().GetLibItemName())) for ref, fp in fps.items()}
        heights = {r: v for r, v in heights.items() if v is not None}
        heights["J1"] = 0.0          # the stacking socket itself (BRIEF §2)
    parked = []
    for ref, fp in fps.items():
        cy = geom.courtyard_bbox(fp)
        pos = geom.xy(fp.GetPosition())
        if pos[0] > 40:
            parked.append(ref)
            continue
        if cy is None:
            fails.append(f"{ref}: no courtyard (cannot check keep-outs)")
            continue
        if ref.startswith(("H", "MTG")):
            continue          # holes are not parts: the keep-outs guard components around the screws and standoffs

        def gap_to_point(c):
            dx = max(cy[0] - c[0], 0, c[0] - cy[2])
            dy = max(cy[1] - c[1], 0, c[1] - cy[3])
            return math.hypot(dx, dy)
        for h, c in geom.PI_HOLES.items():
            if ref != h and gap_to_point(c) < 3.0:
                fails.append(f"{ref} within r 3.0 of {h} (gap {gap_to_point(c):.2f})")
        for h, c in geom.HOUSING_HOLES.items():
            if ref != h and gap_to_point(c) < 3.5:
                fails.append(f"{ref} within r 3.5 of {h} (gap {gap_to_point(c):.2f})")
        for h, c in geom.INSERTS.items():
            if ref != h and ref not in geom.INSERTS and gap_to_point(c) < geom.INSERT_KEEPOUT_R:
                fails.append(f"{ref} within r {geom.INSERT_KEEPOUT_R} of insert {h} (gap {gap_to_point(c):.2f})")
        if not fp.IsFlipped():
            for l, e in geom.ENVELOPES.items():
                if ref != l and geom.rect_gap(cy, e) < geom.ENVELOPE_CLEAR - 1e-6:
                    if ref in ALLOWANCES and geom.rect_gap(cy, e) >= ALLOWANCES[ref][0] - 1e-6:
                        infos.append(f"{ref} (top) {geom.rect_gap(cy, e):.2f} mm from the {l} envelope: ALLOWED deviation ({ALLOWANCES[ref][1]})")
                    else:
                        fails.append(f"{ref} (top) only {geom.rect_gap(cy, e):.2f} mm from the {l} envelope (want ≥ {geom.ENVELOPE_CLEAR})")
        else:
            h = heights.get(ref)
            if heights and h is None:
                fails.append(f"{ref} (bottom): no height on record")
            elif h is not None and h > geom.BOTTOM_MAX_HEIGHT:
                fails.append(f"{ref} (bottom) is {h} mm tall (max {geom.BOTTOM_MAX_HEIGHT})")
    for line in infos:
        print("ok   ", line)
    for line in fails:
        print("FAIL ", line)
    print(f"check_fixed: {len(fails)} failures; {len(parked)} parts still parked off-board" + (f": {' '.join(sorted(parked))}" if parked and len(parked) < 20 else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    hp = sys.argv[sys.argv.index("--heights") + 1] if "--heights" in sys.argv else None
    sys.exit(main(hp))
