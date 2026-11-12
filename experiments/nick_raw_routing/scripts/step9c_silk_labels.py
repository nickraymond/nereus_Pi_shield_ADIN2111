"""Step 9c: silkscreen names for the straps, the wire pads, the headers and the LEDs (Nick, 2026-11-10:
"add names to the straps, the thru-hole connections, and places I need to add wires, so I know what each
strap does"). No copper changes.

Every name is the net or function read from this board's netlist:
- JP1 "5V-PI": the bridge joins the 5 V converter's output (5V_PI) to the Pi's 5 V pins (PI_5V).
- JP2 "LED": ADIN_VDDIO to the three LED resistors.
- JP3 "CFG1", JP4 "CFG0": the ADIN's SPI_CFG1 / SPI_CFG0 straps; "1" marks the ADIN_VDDIO end, "0" the GND end.
- J4 "5V IN" (through F1), J5 "PAYLOAD" (VBUS_OUT), J6 "PI 5V" with its 5V and GND rows, J3 "I2C3".
- J2: one short name per pin, north row above the header, south row below it.
- Inserts: "BM2" / "BM1" replace the bare "2" / "1" (both sides); LEDs: P1, PWR, P2.
Reference texts that sat on other parts are moved; those of F1, the LEDs, the mounting holes H1-H4 and the inserts MP1-MP4 are hidden.
Two texts outside the board outline (Sofar's part number and name, y < 65) are removed.
"""
import sys
import pcbnew
import boardio
from boardio import mm

F = pcbnew.FromMM
b = boardio.load()
fp = boardio.footprints(b)
TOP, BOT = b.GetLayerID("Top Overlay"), b.GetLayerID("Bottom Overlay")
texts = [d for d in b.GetDrawings() if d.Type() in (pcbnew.PCB_TEXT_T, pcbnew.PCB_TEXTBOX_T) and d.GetLayer() in (TOP, BOT)]
if any(d.GetText() == "CFG1" for d in texts):
    sys.exit("step 9c already applied (text CFG1 exists); nothing done")
n_new = 0


def text(s, x, y, w=0.8, h=1.0, th=0.15, layer=TOP, angle=0):
    global n_new
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(F(w), F(h))); t.SetTextThickness(F(th))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetTextAngleDegrees(angle); t.SetMirrored(layer == BOT)
    t.SetPosition(pcbnew.VECTOR2I(F(x), F(y)))
    b.Add(t); n_new += 1


def ref(name, x, y, angle=0, w=None):
    r = fp[name].Reference()
    r.SetTextAngleDegrees(angle)
    r.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); r.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    if w:
        r.SetTextSize(pcbnew.VECTOR2I(F(w), r.GetTextHeight()))
    r.SetPosition(pcbnew.VECTOR2I(F(x), F(y)))


# ---- straps
ref("JP1", 121.00, 82.90, w=0.8);  text("5V-PI", 121.00, 84.20, w=0.7)
ref("JP2", 144.90, 124.00);        text("LED", 144.90, 125.30)
ref("R47", 152.90, 126.00); ref("R2", 156.40, 124.60)
text("1", 151.50, 122.40); text("0", 157.60, 122.40); ref("JP3", 160.00, 122.40); text("CFG1", 163.20, 122.40, w=0.7)
text("0", 151.30, 96.40);  text("1", 157.60, 96.40);  ref("JP4", 153.40, 94.40);  text("CFG0", 156.40, 94.40, w=0.7)

# ---- wire pads and headers
ref("J4", 122.50, 94.00, w=0.8);   text("5V IN", 125.30, 94.00, w=0.6)
ref("C54", 129.52, 94.45)
text("PAYLOAD", 124.60, 122.10, w=0.7)
ref("J6", 137.35, 91.70, w=0.8);   text("PI 5V", 140.30, 91.70, w=0.7)
text("5V", 145.20, 85.10, w=0.7);  text("GND", 145.60, 87.64, w=0.6)
ref("C56", 130.90, 82.50, w=0.6);  ref("C57", 133.20, 82.50, w=0.6);  ref("C58", 135.60, 82.50, w=0.6)
ref("J3", 118.30, 106.40, w=0.8);  text("I2C3", 121.40, 106.40, w=0.7)

# ---- J2 pin names: even pins (north row) above the header, odd pins (south row) below
north = {2: "ALR", 4: "GND", 6: "CE1", 8: "SC3", 10: "GND", 12: "GND", 14: "GND", 16: "SC0", 18: "GND", 20: "IN2", 22: "TM", 24: "MO"}
south = {1: "TX", 3: "RX", 5: "CE0", 7: "SD3", 15: "SD0", 17: "SLP", 19: "IN1", 21: "MI", 23: "CK"}
expect = {"ALR": "~{ADC_ALERT}", "GND": "GND", "CE1": "~{SPI1_CE1}", "SC3": "I2C3_SCL", "SC0": "I2C0_SCL", "IN2": "MOTOR_IN2",
          "TM": "ADIN_TIMER", "MO": "SPI1_MOSI", "TX": "UART_TX", "RX": "UART_RX", "CE0": "~{SPI1_CE0}", "SD3": "I2C3_SDA",
          "SD0": "I2C0_SDA", "SLP": "MOTOR_nSLEEP", "IN1": "MOTOR_IN1", "MI": "SPI1_MISO", "CK": "SPI1_SCLK"}
pads = {p.GetNumber(): p for p in fp["J2"].Pads()}
for row, y in ((north, 82.50), (south, 90.35)):
    for n, s in row.items():
        p = pads[str(n)]
        assert p.GetNetname().split("/")[-1] == expect[s], (n, s, p.GetNetname())
        x = mm(p.GetPosition().x) + (0.40 if n == 15 else 0.0)        # pin 15: clear of R27
        text(s, x, y, w=0.6 if len(s) == 3 else 0.8)
for n in (9, 11, 13):
    assert pads[str(n)].GetNetname().split("/")[-1] == "PI_3V3"
x9, x11, x13 = (mm(pads[n].GetPosition().x) for n in ("9", "11", "13"))
text("3V3", x9 - 0.18, 90.35, w=0.6)                                 # pin 9, clear of the via at (161.75, 89.75)
text("3V3", 163.50, 90.35, w=0.6)                                    # one name for pins 11 and 13 under a bracket (R26 sits below pin 13)
for a, c in (((x11 - 0.67, 89.75), (x13 + 0.4, 89.75)), ((x11 - 0.67, 89.75), (x11 - 0.67, 89.55)), ((x13 + 0.4, 89.75), (x13 + 0.4, 89.55))):
    s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(F(a[0]), F(a[1]))); s.SetEnd(pcbnew.VECTOR2I(F(c[0]), F(c[1])))
    s.SetWidth(F(0.15)); s.SetLayer(TOP); b.Add(s)
ref("R26", 164.30, 91.40); ref("R27", 167.20, 91.40)

# ---- inserts and LEDs
moved = 0
for d in texts:
    s, x, y = d.GetText(), mm(d.GetPosition().x), mm(d.GetPosition().y)
    if s in ("1", "2") and d.Type() == pcbnew.PCB_TEXT_T:
        d.SetText("BM" + s)
        d.SetTextSize(pcbnew.VECTOR2I(F(1.0), F(1.3))); d.SetTextThickness(F(0.2))
        d.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); d.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        d.SetPosition(pcbnew.VECTOR2I(F(133.50 if s == "2" else 164.10), F(124.00)))
        moved += 1
    elif s == "-" and d.GetLayer() == TOP and abs(x - 152.63) < 0.1:
        d.Move(pcbnew.VECTOR2I(F(0.6), F(0.5)))                        # off D10 and its anode via
        moved += 1
    elif y < 70:
        b.Remove(d)                                                   # outside the board outline
        moved += 1
assert moved == 4 + 1 + 2, moved
for led, name in (("D9", "P1"), ("D8", "PWR"), ("D10", "P2")):
    fp[led].Reference().SetVisible(False)
    text(name, boardio.pos(fp[led])[0], 131.00)
fp["F1"].Reference().SetVisible(False)
for h in ("H1", "H2", "H3", "H4"):
    fp[h].Reference().SetVisible(False)                               # two were clipped by the board edge, one sat on J5's pad
for m in ("MP1", "MP2", "MP3", "MP4"):
    fp[m].Reference().SetVisible(False)                               # bottom side: BM1 / BM2 and + / - name the inserts

boardio.save(b)
print("  %d texts added, %d board texts changed or removed" % (n_new, moved))
