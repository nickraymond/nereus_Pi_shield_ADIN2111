"""Placement mocks for the N6 shield, to scale, as SVG. Study only: reads mote_extent.json (written by
n6_mote_extent.py) and draws; writes nothing into the KiCad project.
Usage: python3 n6_mocks.py <mote_extent.json> <out_dir>
View: from behind the camera (the shield's outer face). X' = 35.56 - x of the N6 model, y = distance from the
N6's USB-end edge; the camera end is at the top of the drawing. N6 geometry: OpenMV's 3D model "N6 r3"
(openmv-boards/models/OPENMV_N6.glb, read 2026-11-17), see N6_FACTS.md."""
import json, sys, os
ext = json.load(open(sys.argv[1])); out = sys.argv[2]
S = 11.0                                   # px per mm
N6W, N6L = 35.56, 44.45
COLX = [1.56, 4.10, 31.42, 33.96]          # N6 model x of the four pin columns
ROWY = [19.37 - 2.54 * i for i in range(8)]  # row 1 (camera end) .. row 8 (USB end)
LAB = {1.56: ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "3V3"], 4.10: ["eth", "eth", "eth", "eth", "eth", "WKUP", "RAW", "GND"],
       31.42: ["eth", "eth", "eth", "eth", "P14", "P13", "BOOT", "3V3"], 33.96: ["RST", "P11", "P10", "P9", "P8", "P7", "VIN", "GND"]}
USED = {"P0": "MOSI", "P1": "MISO", "P2": "SCK", "P3": "CS", "P4": "SCL", "P5": "SDA", "P7": "IN1", "P8": "IN2", "P9": "RST",
        "P13": "A_PWR", "P14": "SLP", "P6": "INT", "VIN": "5V", "GND": "", "3V3": ""}
BX0, BY0 = 124.85, 95.88                   # block frame origin on the starting board (L2 end, north copper edge)
G = {'XOFF': 32.13}
YOFF, XOFF = 1.0, 32.13                    # block L1 end at y = 1.0; block north edge at X' = 32.13
def blk(mx, my): return (G['XOFF'] - my, YOFF + 47.48 - mx)   # block frame -> (X', y): quarter turn, no mirror
class Svg:
    def __init__(s, x0, y0, x1, y1, title):
        s.x0, s.y1 = x0 - 6, y1 + 5; s.w = max((x1 - x0 + 12) * S, 640); s.h = (y1 - y0 + 20) * S
        s.o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial" font-size="11">' % (s.w, s.h),
               '<rect width="100%" height="100%" fill="white"/>', '<text x="12" y="22" font-size="17" font-weight="bold">%s</text>' % title]
    def p(s, X, y): return ((X - s.x0) * S, (s.y1 - y) * S)
    def rect(s, X0, y0, X1, y1, fill="none", stroke="black", sw=1, dash="", op=1.0, rx=0):
        a, b = s.p(min(X0, X1), max(y0, y1)); w, h = abs(X1 - X0) * S, abs(y1 - y0) * S
        s.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="%s" stroke-dasharray="%s" fill-opacity="%s" rx="%s"/>' % (a, b, w, h, fill, stroke, sw, dash, op, rx * S))
    def circ(s, X, y, r, fill, stroke="none"):
        a, b = s.p(X, y); s.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s"/>' % (a, b, r * S, fill, stroke))
    def text(s, X, y, t, size=11, anchor="middle", fill="black", bold=False, rot=0):
        a, b = s.p(X, y); s.o.append('<text x="%.1f" y="%.1f" font-size="%s" text-anchor="%s" fill="%s"%s%s>%s</text>' % (a, b + size * 0.35, size, anchor, fill, ' font-weight="bold"' if bold else "", ' transform="rotate(%d %.1f %.1f)"' % (rot, a, b) if rot else "", t))
    def line(s, pts, col, w, dash=""):
        s.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s" stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % s.p(*q) for q in pts), col, w * S, dash))
    def note(s, lines):
        for i, t in enumerate(lines): s.o.append('<text x="12" y="%d" font-size="12">%s</text>' % (s.h - 14 * (len(lines) - i) + 4, t))
    def save(s, name):
        open(os.path.join(out, name), "w").write("\n".join(s.o + ["</svg>"])); print(name, "%d x %d px" % (s.w, s.h))
def n6(s, smd=False):
    s.rect(0, 0, N6W, N6L, stroke="#1565c0", sw=2, dash="7 4")
    if smd:   # KiCad PinSocket_2x08_P2.54mm_Vertical_SMD land pattern: pads 3.0 x 1.0 at +-2.52 from the header centre, bottom face
        for hc in (2.83, 32.73):
            for ry in ROWY:
                for d in (-2.52, 2.52): s.rect(N6W - hc + d - 1.5, ry - 0.5, N6W - hc + d + 1.5, ry + 0.5, fill="#c5e1a5", stroke="#558b2f", sw=0.6, dash="2 1", op=0.7)
    for cx in COLX:
        for i, ry in enumerate(ROWY):
            l = LAB[cx][i]; X = N6W - cx; u = l in USED
            s.circ(X, ry, 0.45 if smd else 0.85, "#2e7d32" if u else "#bdbdbd", "black")
            outer = cx in (1.56, 33.96)
            if outer and not smd: s.text(X + (1.3 if X > 18 else -1.3), ry, l + ((" " + USED[l]) if USED.get(l) else ""), 8, "start" if X > 18 else "end", "#1b5e20" if u else "#757575")
def profile():
    """Per 1 mm slice along the block: extent across it of Sofar's copper and footprints (block frame, mm)."""
    sl = {}
    def add(x0, x1, y0, y1):
        for i in range(int(x0 - BX0), int(x1 - BX0) + 1):
            a = sl.setdefault(i, [1e9, -1e9]); a[0] = min(a[0], y0 - BY0); a[1] = max(a[1], y1 - BY0)
    for c in ext["core"]: add(c["box"][0], c["box"][2], c["box"][1], c["box"][3])
    for c in ext["copper"]:
        w = c[5] / 2; add(min(c[1], c[3]) - w, max(c[1], c[3]) + w, min(c[2], c[4]) - w, max(c[2], c[4]) + w)
    return {i: v for i, v in sl.items() if 0 <= i < 48}
def header_gap():
    """Smallest gap between the block (copper and footprints, 1 mm slices) and the inner header pads (0.85 mm radius)."""
    best = {}
    for i, (lo, hi) in profile().items():
        (Xa, ya), (Xb, yb) = blk(i, lo), blk(i + 1, hi)
        if min(ya, yb) < ROWY[0] + 0.85:      # slice reaches into the header rows
            for side, g in (("P0 side", (N6W - 4.10 - 0.85) - max(Xa, Xb)), ("VIN side", min(Xa, Xb) - (N6W - 31.42 + 0.85))):
                best[side] = min(best.get(side, 99), g)
    return best
def mote(s):
    for c in ext["core"]:
        b = c["box"]; (Xa, ya), (Xb, yb) = blk(b[0] - BX0, b[1] - BY0), blk(b[2] - BX0, b[3] - BY0)
        top = c["side"] == "T"
        s.rect(Xa, ya, Xb, yb, fill="#ffcc80" if top else "#e0e0e0", stroke="#e65100" if top else "#9e9e9e", sw=1.2 if top else 0.5, op=0.9 if top else 0.6)
        if c["ref"] in ("L1", "L2", "L3", "C22", "C23", "U1", "T1", "T2", "D1"):
            s.text((Xa + Xb) / 2, (ya + yb) / 2, c["ref"] + (" 6 mm tall" if c["ref"] in ("L1", "L2") else ""), 10, bold=True)
    for i, (lo, hi) in sorted(profile().items()):
        (Xa, ya), (Xb, yb) = blk(i, lo), blk(i + 1, hi)
        s.rect(Xa, ya, Xb, yb, fill="#ffe0b2", stroke="none", op=0.55)
def group(s, X0, y0, w, h, name, col, cu=None):
    if cu: s.rect(cu[0], cu[1], cu[2], cu[3], fill=col, stroke=col, sw=1, dash="2 2", op=0.18); s.text((cu[0] + cu[2]) / 2, max(cu[1], cu[3]) - 1.0, cu[4], 9, fill=col)
    s.rect(X0, y0, X0 + w, y0 + h, fill=col, stroke="black", op=0.55); s.text(X0 + w / 2, y0 + h / 2, name, 9.5, bold=True)
def conn(s, name, X, y, along, n, kind, entry):
    """along: 'y' = pin row runs along y at the board edge X (opening away from the board centre), 'x' = along X at edge y."""
    L = {("GH", 4): 8.25, ("GH", 3): 7.0, ("SH", 4): 6.0}[(kind, n)]
    D = (4.85 if kind == "GH" else 4.95) if entry == "side" else (4.95 if kind == "GH" else 3.6)
    over = (3.1 if kind == "GH" else 2.0) if entry == "side" else 0
    col = "#ab47bc" if entry == "side" else "#00897b"
    if along == "y":
        d = 1 if X < 18 else -1
        s.rect(X, y, X + d * D, y + L, fill=col, stroke="black", op=0.75)
        if over: s.rect(X, y + 0.8, X - d * over, y + L - 0.8, stroke=col, dash="3 2")
        s.text(X + d * D / 2, y + L / 2, name, 9, bold=True, rot=-90)
    else:
        d = 1 if y < 20 else -1
        s.rect(X, y, X + L, y + d * D, fill=col, stroke="black", op=0.75)
        if over: s.rect(X + 0.8, y, X + L - 0.8, y - d * over, stroke=col, dash="3 2")
        s.text(X + L / 2, y + d * D / 2, name, 9, bold=True)
def legend(s, entry, size, extra):
    s.note(["Shield (thick black): %s" % size,
            "View from behind the camera, camera end up. Dashed blue = N6 outline 35.56 x 44.45 mm.",
            "Dots = N6 header pins: green used by the shield, grey not connected.",
            "Orange = mote block top-side parts (tall ones named); grey = its bottom-side parts;",
            "pale orange = Sofar's copper that travels with the block (47.5 x 25.8 mm in all).",
            ("Purple = JST side entry: body 4.85 mm deep, dashed = plug about 3.1 mm past it, mated 4.35 mm high." if entry == "side" else
             "Green = JST top entry: GH 8.25 x 4.95 mm on the board, mated 7.3 mm high (L1 / L2: 6.0 mm)."), extra])
def mock_a(entry):
    s = Svg(-4, -15, N6W + 4, 49.5, "Mock A (%s-entry JST): N6 width, longer. 35.56 x 62.5 mm" % entry)
    s.rect(0, -14, N6W, 48.5, sw=3, rx=1); n6(s); mote(s)
    group(s, 1.2, -11.6, 12.6, 10.2, "5 V: U10 + L6", "#c62828", (0.3, -13.7, 15.3, -0.3, "U10 copper 200 mm2 / face"))
    group(s, 17.0, -8.3, 9.4, 6.5, "U12 motor", "#283593", (15.9, -9.0, 26.9, -0.3, "U12 96 mm2 / face"))
    if entry == "side":
        conn(s, "MOTOR", 16.5, -14, "x", 4, "GH", entry); conn(s, "BM1", 26.3, -14, "x", 4, "GH", entry)
        conn(s, "BM2", 0, 39.6, "y", 4, "GH", entry); conn(s, "POT", 0, 31.6, "y", 3, "GH", entry); conn(s, "QWIIC", 0, 24.6, "y", 4, "SH", entry)
    else:
        conn(s, "MOTOR", 27.2, -9.0, "x", 4, "GH", entry); conn(s, "BM1", 27.2, -14.0, "x", 4, "GH", entry)
        conn(s, "BM2", 0.6, 39.6, "y", 4, "GH", entry); conn(s, "POT", 0.6, 31.6, "y", 3, "GH", entry); conn(s, "QWIIC", 0.6, 24.6, "y", 4, "SH", entry)
    group(s, 32.6, 30, 2.6, 8.5, "ADC", "#6d4c41"); s.text(34.0, 44, "LEDs", 9, rot=-90)
    legend(s, entry, "35.56 x 62.5 mm = 2222 mm2 (N6: 1581 mm2). Overhang: 14 mm past the USB end, 4 mm past the camera end.", "ADC (U13) sits on the N6-facing side.")
    s.save("mock_A_long_%s_entry.svg" % entry)
def mock_b(entry):
    s = Svg(-17, -6, N6W + 4, 49.5, "Mock B (%s-entry JST): wing beside the VIN / P7 / P8 column. 48.6 x 53.5 mm" % entry)
    X0 = -13.0
    s.rect(X0, -5, N6W, 48.5, sw=3, rx=1); n6(s); mote(s)
    group(s, X0 + 1.4, 2.0, 10.2, 12.6, "5 V: U10 + L6", "#c62828", (X0 + 0.3, -1.0, -0.3, 15.0, "U10 copper 198 mm2 / face"))
    group(s, X0 + 3.2, 17.0, 6.5, 9.4, "U12 motor", "#283593", (X0 + 0.3, 16.0, -0.3, 27.2, "U12 copper 139 mm2 / face"))
    group(s, -7.0, 33.5, 5.7, 6.5, "ADC", "#6d4c41")
    if entry == "side":
        conn(s, "MOTOR", X0, 28.2, "y", 4, "GH", entry); conn(s, "POT", X0, 37.0, "y", 3, "GH", entry)
        conn(s, "BM2", -6.5, 48.5, "x", 4, "GH", entry); conn(s, "QWIIC", 2.6, 48.5, "x", 4, "SH", entry); conn(s, "BM1", 10.0, -5, "x", 4, "GH", entry)
    else:
        conn(s, "MOTOR", X0 + 0.6, 28.2, "y", 4, "GH", entry); conn(s, "POT", X0 + 0.6, 37.0, "y", 3, "GH", entry)
        conn(s, "BM2", 0.4, 39.6, "y", 4, "GH", entry); conn(s, "QWIIC", 0.4, 31.0, "y", 4, "SH", entry); conn(s, "BM1", 10.0, -5, "x", 4, "GH", entry)
    s.text(34.0, 44, "LEDs", 9, rot=-90)
    legend(s, entry, "48.6 x 53.5 mm = 2600 mm2 (N6: 1581 mm2); 48.6 x 48.5 if the BM1 trunks fit beside the block between the headers.", "ADC (U13) sits on the N6-facing side.")
    s.save("mock_B_wing_%s_entry.svg" % entry)
def mock_c(entry):
    """Nick, 2026-11-17: BM1 and MOTOR on the east edge, so the board gets wider instead of longer."""
    E = N6W + 13.0
    s = Svg(-4, -1, E + 4, 49.5, "Mock C (%s-entry JST): east wing, BM1 and MOTOR on the east edge. 48.6 x 48.5 mm" % entry)
    s.rect(0, 0, E, 48.5, sw=3, rx=1); n6(s); mote(s)
    group(s, N6W + 1.4, 2.6, 10.2, 12.6, "5 V: U10 + L6", "#c62828", (N6W + 0.3, 0.3, E - 0.3, 16.3, "U10 copper 198 mm2 / face"))
    group(s, N6W + 0.9, 18.0, 6.5, 9.4, "U12 motor", "#283593", (N6W + 0.3, 16.8, N6W + 7.9, 30.0, "U12 100 mm2 / face"))
    inset = 0 if entry == "side" else 0.6
    conn(s, "MOTOR", E - inset, 18.6, "y", 4, "GH", entry); conn(s, "BM1", E - inset, 30.5, "y", 4, "GH", entry)
    conn(s, "BM2", inset, 39.6, "y", 4, "GH", entry); conn(s, "POT", inset, 31.6, "y", 3, "GH", entry); conn(s, "QWIIC", inset, 24.6, "y", 4, "SH", entry)
    group(s, N6W + 1.5, 41.0, 8.5, 5.7, "ADC", "#6d4c41"); s.text(34.0, 44, "LEDs", 9, rot=-90)
    s.line([(24.5, 9.0), (29.57, 11.0), (29.57, 22.0), (33.0, 25.0), (33.0, 34.6), (E - 5.2 - inset, 34.6)], "#d50000", 1.4, "6 3")
    s.text(31.2, 28.5, "BM1 trunks: 2.1 mm channel", 9, fill="#d50000", rot=-90)
    s.line([(1.6, 4.13), (8.0, -0.0 + 0.5), (N6W + 2.0, 0.5)], "#c62828", 0.3, "2 2")
    legend(s, entry, "48.6 x 48.5 mm = 2357 mm2 (N6: 1581 mm2). 13 mm wider on the P0 side, 4 mm past the camera end.",
           "Dashed red = BM1 bus tracks in the 2.1 mm channel beside the block (to prove); dotted = 5 V to VIN. ADC on the N6-facing side.")
    s.save("mock_C_east_wing_%s_entry.svg" % entry)
def hole(s, X, y):
    s.circ(X, y, 2.55, "#eeeeee", "#616161"); s.circ(X, y, 1.35, "white", "black")
def mock_d(entry):
    """Nick, 2026-11-17: grow taller, not wider. 5 V on the south wall, BM1 in the south-west corner, pot + ADC + motor on the east."""
    s = Svg(-4, -13, N6W + 4, 49.5, "Mock D (%s-entry JST): taller, 35.56 x 60.5 mm" % entry)
    s.rect(0, -12, N6W, 48.5, sw=3, rx=1); n6(s); mote(s)
    i = 0 if entry == "side" else 0.6
    group(s, 9.2, -11.2, 12.6, 10.2, "5 V: U10 + L6", "#c62828", (8.9, -11.7, 23.2, -0.3, "U10 copper 163 mm2 / face"))
    group(s, 23.8, -10.6, 6.5, 9.4, "U12", "#283593", (23.5, -11.7, 35.2, -0.3, "U12 133 mm2 / face"))
    conn(s, "BM1", 0.4, -12 + i, "x", 4, "GH", entry); conn(s, "MOTOR", N6W - i, -10.4, "y", 4, "GH", entry)
    conn(s, "POT", 27.6, 48.5 - i, "x", 3, "GH", entry); conn(s, "BM2", 1.6, 48.5 - i, "x", 4, "GH", entry); conn(s, "QWIIC", i, 28.0, "y", 4, "SH", entry)
    group(s, 26.8, 36.5, 5.3, 4.6, "ADC", "#6d4c41"); s.text(3.0, 38.5, "LEDs", 9, rot=-90)
    s.line([(14.5, 2.0), (8.0, -3.0), (4.5, -6.0)], "#d50000", 2.0, "6 3"); s.text(4.6, -2.0, "BM1 8 mm", 9, fill="#d50000")
    legend(s, entry, "35.56 x 60.5 mm = 2151 mm2 (N6: 1581 mm2). 12 mm past the USB end, 4 past the camera end.",
           "Dashed red = BM1 bus tracks, about 8 mm. ADC on the N6-facing side beside the pot connector.")
    s.save("mock_D_tall_%s_entry.svg" % entry)
def mock_e():
    """Nick, 2026-11-17: top-entry connectors lying east-west in two columns, surface-mount headers on the N6-facing
    side, the 5 V converter over a header, four mounting holes."""
    G['XOFF'] = 33.03     # block 0.9 mm east: about 1.0 mm from its bottom-side copper to the header pads on both sides
    W0, E = -4.0, 41.0
    s = Svg(W0 - 2, -7, E + 2, 49.5, "Mock E: SMD headers below, top-entry JST in two columns, 4 holes. 45.0 x 54.5 mm")
    s.rect(W0, -6, E, 48.5, sw=3, rx=1); n6(s, smd=True); mote(s)
    for X, y in ((W0 + 3, -3), (E - 3, -3), (W0 + 3, 45.5), (E - 3, 45.5)): hole(s, X, y)
    c = lambda name, X, y, n=4, k="GH": conn(s, name, X, y, "x", n, k, "top")
    c("BM1", -3.4, 6.2); c("QWIIC", -2.3, 11.8, 4, "SH"); c("BM2", -3.4, 40.6)
    group(s, -3.4, 16.4, 10.2, 12.6, "5 V: U10 + L6", "#c62828", (-3.7, 15.9, 7.0, 34.0, "U10 copper 194 mm2 / face"))
    c("MOTOR", 30.3, 6.2); c("POT", 30.9, 11.8, 3)
    group(s, 34.0, 21.5, 6.5, 9.4, "U12", "#283593", (33.7, 21.0, 40.7, 34.0, "U12 91 mm2 / face"))
    group(s, 34.2, 35.0, 5.7, 6.5, "ADC", "#6d4c41")
    s.line([(14.0, 6.0), (8.0, 8.7), (5.0, 8.7)], "#d50000", 2.0, "6 3")
    s.note(["Shield (thick black): 45.0 x 54.5 mm = 2453 mm2 (N6: 1581 mm2). 9.4 mm wider, 6 mm past the USB end, 4 past the camera end.",
            "View from behind the camera, camera end up. Dashed blue = N6 outline 35.56 x 44.45 mm.",
            "Pale green = surface-mount header pads on the N6-facing side (KiCad's generic 2x8 SMD socket pattern); dots = pins.",
            "Orange = mote block top-side parts; grey = its bottom-side parts; pale orange = Sofar's copper.",
            "Green = JST top entry lying east-west: GH 8.25 x 4.95 mm, mated 7.3 mm high (L1 / L2: 6.0 mm).",
            "Grey rings = 4 mounting holes, drawn 2.7 mm with a 5.1 mm keep-out (N6 hole size not found). The lower two need the 6 mm strip.",
            "ADC on the N6-facing side. Dashed red = BM1 bus tracks, about 9 mm."])
    s.save("mock_E_smd_headers_top_entry.svg"); G['XOFF'] = 32.13
def mock_f():
    """Nick, 2026-11-17: as mock E, with all five connectors in one column on the east side."""
    G['XOFF'] = 33.03
    W0, E = -3.2, 42.4
    s = Svg(W0 - 2, -7, E + 2, 49.5, "Mock F: as E, all connectors in one east column. 45.6 x 54.5 mm")
    s.rect(W0, -6, E, 48.5, sw=3, rx=1); n6(s, smd=True); mote(s)
    for X, y in ((W0 + 3, -3), (E - 3, -3), (W0 + 3, 45.5), (E - 3, 45.5)): hole(s, X, y)
    c = lambda name, y, n=4, k="GH": conn(s, name, 33.5, y, "x", n, k, "top")
    c("BM1", 0.4); c("POT", 5.95, 3); c("QWIIC", 11.5, 4, "SH"); c("MOTOR", 15.7); c("BM2", 41.3)
    group(s, 33.7, 21.6, 6.5, 9.4, "U12", "#283593", (33.4, 21.2, 41.9, 34.0, "U12 109 mm2 / face"))
    group(s, 34.0, 32.3, 5.7, 3.6, "ADC", "#6d4c41")
    group(s, -2.8, 7.6, 10.2, 12.6, "5 V: U10 + L6", "#c62828", (-2.9, 6.0, 7.4, 26.0, "U10 copper 206 mm2 / face"))
    s.line([(26.8, 4.0), (33.4, 2.9)], "#d50000", 2.0, "6 3"); s.line([(27.3, 40.0), (33.4, 38.8)], "#d50000", 2.0, "6 3")
    s.note(["Shield (thick black): 45.6 x 54.5 mm = 2485 mm2 (N6: 1581 mm2). 10 mm wider, 6 mm past the USB end, 4 past the camera end.",
            "View from behind the camera, camera end up. Dashed blue = N6 outline 35.56 x 44.45 mm.",
            "Pale green = surface-mount header pads on the N6-facing side (KiCad's generic 2x8 SMD socket pattern); dots = pins.",
            "Orange = mote block top-side parts; grey = its bottom-side parts; pale orange = Sofar's copper.",
            "Green = JST top entry, all five in one column on the east: GH 8.25 x 4.95 mm, mated 7.3 mm high.",
            "Grey rings = 4 mounting holes, drawn 2.7 mm with a 5.1 mm keep-out (N6 hole size not found).",
            "ADC on the N6-facing side. Dashed red = BM1 and BM2 bus tracks, about 7 mm each. 5 V converter over the VIN header."])
    s.save("mock_F_one_column_top_entry.svg"); G['XOFF'] = 32.13
for e in ("side", "top"): mock_a(e); mock_b(e); mock_c(e); mock_d(e)
mock_e(); mock_f()
print("gap block to inner header pads, mm:", {k: round(v, 2) for k, v in header_gap().items()})
