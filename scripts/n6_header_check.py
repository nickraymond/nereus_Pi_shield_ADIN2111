"""Read-only: the shield's N6 header pads against OpenMV's pinout image (front view = camera side).

KiCad's Python: n6_header_check.py <board .kicad_pcb>
The table below is the pinout image as Nick posted it in the first-pass session's chat on 2026-11-18 ("this is from
the front view"; product page https://openmv.io/products/openmv-n6), read row by row from the top (camera end):
four columns, left outer, left inner, right inner, right outer, as seen from the FRONT.
The shield sits behind the N6, so seen from the back the columns are mirrored: the shield's X' (from the N6's
VIN-side edge towards the P0 column) is 35.56 - x of the front view. Rows: y from the USB-end edge, row 1 at 19.37,
2.54 mm pitch (N6_FACTS.md, from the r3 model). Column x in the front view from the same model: 1.56, 4.10, 31.42, 33.96."""
import sys, pcbnew
FRONT = [("P0", "ETH LED", "ETH DC P", "RESET"), ("P1", "ETH RXN", "ETH DC N", "P11"), ("P2", "ETH RXP", "ETH DD P", "P10"),
         ("P3", "ETH TXN", "ETH DD N", "P9"), ("P4", "ETH TXP", "P14", "P8"), ("P5", "WKUP2", "P13", "P7"),
         ("P6", "RAW", "BOOT0", "VIN"), ("3V3", "GND", "3V3", "GND")]
WANT = {"P0": "N6_MOSI", "P1": "N6_MISO", "P2": "N6_SCK", "P3": "~{N6_CS}", "P4": "I2C0_SCL", "P5": "I2C0_SDA", "P6": "~{ADIN_INT}",
        "P7": "MOTOR_IN1", "P8": "MOTOR_IN2", "P9": "~{ADIN_RST}", "P13": "ADIN_PWR", "P14": "MOTOR_nSLEEP", "VIN": "5V_PI", "3V3": "N6_3V3", "GND": "GND"}
COLX = (1.56, 4.10, 31.42, 33.96); W = 35.56
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; bad = 0; worst = 0
xs = {}
for r in ("J21", "J22"):
    for p in b.FindFootprintByReference(r).Pads():
        X, y = mm(p.GetPosition().x) - 100, 100 - mm(p.GetPosition().y)
        xf = W - X; col = min(range(4), key=lambda i: abs(COLX[i] - xf)); row = round((19.37 - y) / 2.54)
        dx, dy = xf - COLX[col], y - (19.37 - 2.54 * row); worst = max(worst, abs(dx), abs(dy)); xs.setdefault(col, set()).add(round(X, 3))
        label = FRONT[row][col]; net = p.GetNetname().split("/")[-1]; want = WANT.get(label)
        ok = (net == want) if want else net.startswith("unconnected-")
        bad += not ok
        print("%s pin %-2s  X' %6.2f y %5.2f  front view: row %d, %-11s  N6 pin %-8s shield net %-28s %s   off by (%+.2f, %+.2f) mm" % (
            r, p.GetNumber(), X, y, row + 1, ("left outer", "left inner", "right inner", "right outer")[col], label, net if want else "(none)", "ok" if ok else "WRONG", dx, dy))
print("%d of 32 pads disagree with the front-view pinout" % bad)
print("pad columns on the shield, X': " + ", ".join("%s %s" % (("P0 column", "left inner", "right inner", "VIN column")[c], sorted(xs[c])) for c in sorted(xs)))
print("outer to outer on the shield %.2f mm, on the r3 model %.2f mm; inner to inner %.2f against %.2f; largest pad offset %.2f mm" % (
    max(xs[0]) - min(xs[3]), COLX[3] - COLX[0], max(xs[1]) - min(xs[2]), COLX[2] - COLX[1], worst))
