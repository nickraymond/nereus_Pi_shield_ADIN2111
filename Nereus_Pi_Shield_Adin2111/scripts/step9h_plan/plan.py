"""Step 9h planner: where every silkscreen text, box line and reference designator goes.

Plain python 3, no pcbnew. Run in this folder:
  <KiCad python> dump.py ../../Nereus_Pi_Shield_Adin2111.kicad_pcb base.json     (the board BEFORE step 9h)
  python3 plan.py 0.8 0.75                                              (designator height, width in mm)
It prints every collision it could not avoid and writes plan.json; the reviewed result is committed as
../step9h_silk_style.json, which step9h_silk_style.py applies.
"""
import sys, json, math
from eng import *
RH, RW = float(sys.argv[1]), float(sys.argv[2])
ADV, CAP = 0.843, 1.02                      # Menlo in KiCad: advance per char = 0.843 x width, cap height = 1.02 x height (measured on a render)
e = Eng("base.json"); d = e.d
for f in d["fps"]:
    for k in f["silk"]:
        if k["cls"] == "PCB_TEXT" and f["ref"] not in ("J4", "J5"): e.add(k["side"], k["bb"], "fptext " + f["ref"])   # J4 / J5's own + and GND are replaced
    if f["ref"].startswith("FID"):          # keep text out of the fiducial's mask opening
        e.add(f["side"], (f["x"] - 1.2, f["y"] - 1.2, f["x"] + 1.2, f["y"] + 1.2), "fidring " + f["ref"])
# the logo and the old name leave the north-east corner (the logo moves to the east strip in step9h_silk_style.py)
e.hard["T"] = [o for o in e.hard["T"] if not (o[4] == "silk" and o[0] > 176 and o[3] < 96)]
texts, lines, problems, manual = [], [], [], {}
def tb(s, x, y, h, w, just="C", ang=0):
    W = len(s) * ADV * w; H = CAP * h
    if ang == 90: return (x - H / 2, y - W / 2, x + H / 2, y + W / 2)
    x0 = x - W / 2 if just == "C" else (x - W if just == "R" else x)
    return (x0, y - H / 2, x0 + W, y + H / 2)
def chk(side, s, bb, gap=0.12):
    hh = e.hits(side, bb, gap)
    if hh: problems.append((side, s, [round(v, 2) for v in bb], sorted(set(o[4] for o in hh))))
def T(side, s, x, y, h=1.0, w=0.8, just="C", ang=0, ok=()):
    bb = tb(s, x, y, h, w, just, ang)
    hh = [o for o in e.hits(side, bb, 0.12) if o[4] not in ok]
    if hh: problems.append((side, s, [round(v, 2) for v in bb], sorted(set(o[4] for o in hh))))
    e.add(side, (bb[0] - 0.35, bb[1] - 0.1, bb[2] + 0.35, bb[3] + 0.1), "label " + s); texts.append({"side": side, "t": s, "x": x, "y": y, "h": h, "w": w, "just": just, "ang": ang})
def REF(ref, x, y):                         # a designator set by hand: small, under its function name
    side = e.body[ref][0]; bb = tb(ref, x, y, RH, RW); chk(side, "ref " + ref, bb); e.add(side, bb, "ref " + ref); manual[ref] = (x, y, side)
def L(side, pts, width=0.2, ok=()):
    for a, b in zip(pts, pts[1:]):
        bb = (min(a[0], b[0]) - width / 2, min(a[1], b[1]) - width / 2, max(a[0], b[0]) + width / 2, max(a[1], b[1]) + width / 2)
        hh = [o for o in e.hits(side, bb, 0.1) if o[4] not in ("edge", "line") + tuple(ok)]
        if hh: problems.append((side, "line", [round(v, 2) for v in bb], sorted(set(o[4] for o in hh))))
        e.add(side, bb, "line"); lines.append({"side": side, "a": a, "b": b, "w": width})
J2X = lambda n: 150.32 + 2.54 * ((n - 1) // 2)
north = {2: "ALR", 4: "GND", 6: "CE1", 8: "SC3", 10: "GND", 12: "GND", 14: "GND", 16: "SC0", 18: "GND", 20: "IN2", 22: "TM", 24: "MO"}
south = {1: "TX", 3: "RX", 5: "CE0", 7: "SD3", 9: "3V3", 11: "3V3", 13: "3V3", 15: "SD0", 17: "SLP", 19: "IN1", 21: "MI", 23: "CK"}
sx = {9: 160.30, 11: 163.22}                # step 9f: the 3V3 names step aside for the FAULT via
for side, yn, ys in (("T", 82.50, 90.35), ("B", 83.40, 89.45)):
    for n, s in north.items(): T(side, s, J2X(n), yn, 1.0, 0.78 if len(s) == 3 else 0.85, ok=("body H2",))
    for n, s in south.items(): T(side, s, sx.get(n, J2X(n)) if side == "T" else J2X(n), ys, 1.0, 0.78 if len(s) == 3 else 0.85)
# ---- top: function name large, designator small and centred under it
T("T", "5V", 145.20, 85.10, 1.0, 0.8); T("T", "GND", 145.60, 87.64, 1.0, 0.75)
T("T", "PI 5V", 139.86, 90.40, 1.4, 1.0);  REF("J6", 139.86, 91.95)
T("T", "5V SEL", 121.45, 82.90, 1.3, 0.85, ok=("body H1",)); REF("JP1", 121.45, 84.35)
T("T", "I2C3", 120.40, 106.65, 1.4, 1.0);  REF("J3", 120.40, 108.20)
T("T", "CFG0", 154.60, 92.45, 1.5, 1.0);   REF("JP4", 154.60, 94.20)
T("T", "0", 151.30, 96.40, 1.2, 1.0); T("T", "1", 157.60, 96.40, 1.2, 1.0)
T("T", "CFG1", 168.60, 92.45, 1.5, 1.0);   REF("JP3", 168.60, 94.20)
T("T", "0", 165.70, 96.40, 1.2, 1.0); T("T", "1", 171.60, 96.40, 1.2, 1.0)
T("T", "LED", 144.90, 124.00, 1.3, 1.0);   REF("JP2", 144.90, 125.40)
T("T", "P1", 145.80, 131.00, 1.0, 0.8); T("T", "PWR", 148.80, 131.00, 1.0, 0.8); T("T", "P2", 151.80, 131.00, 1.0, 0.8)
# board name in the east strip, turned 90 degrees, logo at the north end (apply.py moves the logo)
e.add("T", (175.0, 99.2, 179.5, 103.0), "logo")
T("T", "Pi Shield", 176.09, 112.30, 2.6, 2.2, ang=90); T("T", "ADIN2111 Rev0", 178.73, 112.30, 1.6, 1.5, ang=90)
T("B", "Pi Shield", 131.60, 110.15, 1.3, 1.0); T("B", "ADIN2111 Rev0", 131.60, 111.75, 0.95, 0.7)
T("T", "BM1", 164.10, 124.00, 1.8, 1.3); T("T", "BM2", 133.50, 124.00, 1.8, 1.3)
MPS = ("body MP1", "body MP2", "body MP3", "body MP4", "pad MP1", "pad MP2", "pad MP3", "pad MP4")   # square boxes of round inserts
T("B", "BM1", 164.10, 124.00, 1.5, 1.1, ok=MPS); T("B", "BM2", 133.50, 124.00, 1.5, 1.1, ok=MPS)
for side in "TB":
    # J4: boxed, +5V / AUX OUT / GND; the box's top line lies on L6's outline, its west side is the board edge
    T(side, "+5V", 123.00, 92.10, 1.2, 0.9); T(side, "AUX OUT", 124.45, 94.00, 1.5, 0.95); T(side, "GND", 123.00, 95.91, 1.2, 0.9)
    L(side, [(116.60, 90.40), (127.60, 90.40), (127.60, 97.55), (116.60, 97.55)], ok=("body F1", "body L6", "body J4", "body J3", "body C55"))
    # J5: boxed, VBUS OUT above, + / GND beside the pads
    T(side, "VBUS OUT", 120.50, 117.50, 1.5, 1.0); T(side, "+", 122.40, 120.20, 1.2, 1.2); T(side, "GND", 122.85, 124.01, 1.2, 0.9)
    L(side, [(116.60, 116.35), (124.55, 116.35), (124.55, 125.80), (116.60, 125.80)], ok=("body J5",))
REF("J4", 125.90, 92.10); REF("J5", 122.85, 122.10); REF("J1", 128.00, 83.50)
# ---- bottom: ratings in two columns under J2 (reader's left is board east), notes in the east strip
def col(left_x, y0, rows, w=0.74, h=1.0, pitch=1.6):
    for i, s in enumerate(rows):
        if s: T("B", s, left_x - len(s) * ADV * w / 2, y0 + pitch * i, h, w)
col(177.70, 96.20, ["BUS  24V (16-32V)", "PORT 0.89A 20W", "5V OUT  1A CONT"])
col(165.30, 96.20, ["VBUS OUT 0.73A MAX"[:14] + "", "VBUS ON=GPIO26 HI", "JP1 5V TO PI/AUX"])
col(179.40, 107.80, ["INSERTS  M3", "MOUNT    M2.5", "", "NO USB POWER ON", "THE PI WHILE", "JP1 FEEDS IT"], pitch=1.7)
print("label problems:"); [print("  ", p) for p in problems]
# ---- reference designators: one size, horizontal, nearest free spot; turned 90 degrees only where nothing else fits
skip = lambda r: r.startswith(("FID", "H", "MP"))
def dist(bb, o):
    return math.hypot(max(o[0] - bb[2], bb[0] - o[2], 0), max(o[1] - bb[3], bb[1] - o[3], 0))
def free(f, ang):
    side, b = e.body[f["ref"]]; W = len(f["ref"]) * ADV * RW; H = CAP * RH
    if ang: W, H = H, W
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; ok = []
    for g in (0.2, 0.45, 0.8, 1.2, 1.7, 2.3):
        for s in (0, 0.4, -0.4, 0.8, -0.8, 1.3, -1.3, 2.0, -2.0):
            for (x, y) in ((cx + s, b[1] - g - H / 2), (cx + s, b[3] + g + H / 2), (b[0] - g - W / 2, cy + s), (b[2] + g + W / 2, cy + s)):
                bb = (x - W / 2, y - H / 2, x + W / 2, y + H / 2)
                if e.hits(side, bb, 0.12): continue
                own = dist(bb, b); amb = any(dist(bb, ob) < own - 0.05 for r, (s2, ob) in e.body.items() if s2 == side and r != f["ref"])
                ok.append((2 * own + 0.2 * math.hypot(x - cx, y - cy) + 0.25 * e.nvias(bb) + (2.5 if amb else 0) + (1.0 if ang else 0), x, y, bb))
    return side, sorted(ok)
todo = [f for f in d["fps"] if f["ref"] in e.body and not skip(f["ref"]) and f["ref"] not in manual and (f["ref_vis"] or f["ref"] in ("D8", "D9", "D10"))]
refs, lost = [], []
for f in sorted(todo, key=lambda f: len(free(f, 0)[1])):
    side, ok = free(f, 0); ang = 0
    if not ok or ok[0][0] > 3.4:
        s2, ok2 = free(f, 90)
        if ok2 and (not ok or ok2[0][0] < ok[0][0] - 0.5): ok, ang = ok2, 90
    if not ok: lost.append(f["ref"]); continue
    c, x, y, bb = ok[0]; e.add(side, (bb[0] - 0.1, bb[1] - 0.05, bb[2] + 0.1, bb[3] + 0.05), "ref " + f["ref"]); refs.append({"ref": f["ref"], "x": round(x, 3), "y": round(y, 3), "cost": round(c, 2), "side": side, "ang": ang})
for r, (x, y, side) in manual.items(): refs.append({"ref": r, "x": x, "y": y, "cost": 0, "side": side, "ang": 0})
print("refs: %d placed (%d by hand), %d turned 90: %s; not placed: %s" % (len(refs), len(manual), sum(1 for r in refs if r["ang"]), sorted(r["ref"] for r in refs if r["ang"]), sorted(lost)))
print("far or ambiguous (cost > 3):", sorted((r["ref"], r["cost"]) for r in refs if r["cost"] > 3))
hide = [f["ref"] for f in d["fps"] if f["ref_vis"] and (skip(f["ref"]) or f["ref"] in lost)]
json.dump({"texts": texts, "lines": lines, "refs": refs, "hide": hide, "rh": RH, "rw": RW}, open("plan.json", "w"))
