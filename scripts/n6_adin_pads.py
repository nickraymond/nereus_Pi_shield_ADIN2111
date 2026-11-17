"""Read-only: where the ADIN2111's host-side pads sit on the starting board (block frame: x from the L2 end,
y from the block's north copper edge). Usage: python n6_adin_pads.py start.kicad_pcb"""
import sys, pcbnew
mm = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
X0, Y0 = 124.85, 95.88
for f in b.GetFootprints():
    if f.GetReference() == "U1":
        c = f.GetPosition()
        for p in f.Pads():
            n = p.GetNetname().split("/")[-1]
            if any(k in n for k in ("SCK", "MOSI", "MISO", "CS}", "INT", "RST", "TIMER", "LED", "CFG")):
                dx, dy = mm(p.GetPosition().x - c.x), mm(p.GetPosition().y - c.y)
                side = "N" if dy < -3 else "S" if dy > 3 else "W" if dx < -3 else "E"
                print(p.GetNumber(), n, "block (%.1f, %.1f)" % (mm(p.GetPosition().x) - X0, mm(p.GetPosition().y) - Y0), "U1 side", side)
for f in b.GetFootprints():
    if f.GetReference() in ("U2", "U3", "R43", "U4", "R1", "TP8"):
        print(f.GetReference(), "block (%.1f, %.1f)" % (mm(f.GetPosition().x) - X0, mm(f.GetPosition().y) - Y0))
