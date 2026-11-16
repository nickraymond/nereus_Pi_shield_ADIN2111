#!/usr/bin/env python3
"""Step 2 (item B): bus connectors J9 "BM2" and J10 "BM1" replace the threaded inserts.

JST GH 4-pin side entry SM04B-GHS-TB, copied from the Urchin's J3 (symbol, value, footprint
Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal). Pins 1 and 2 = the port's N net, pins 3 and 4 = its
P net (Nick, design session's chat, 2026-11-15: "2 pins ganged per polarity"; review G: N on the west pad pair on
both connectors). Connection by same-name labels to the bus wires that led to MP1 (BM1_P), MP2 (BM1_N), MP3 (BM2_P)
and MP4 (BM2_N). Mounting pins: no symbol pin and no net, as on the Urchin.
"""
from s2lib import gh4_ganged, note, read_top, refs, remove_exact, title, write_top

t = read_top()
if "J10" in refs(t):
    raise SystemExit("step 2 already applied")
t = gh4_ganged(t, "J3", "J10", 541.02, 96.52, "BM1_N", "BM1_P", "BM1", "Same part as the Urchin board's J3")
t = gh4_ganged(t, "J3", "J9", 541.02, 137.16, "BM2_N", "BM2_P", "BM2", "Same part as the Urchin board's J3")
t = note(t, "BM1", 537.21, 85.09, 2.54)
t = note(t, "BM2", 537.21, 125.73, 2.54)
t = remove_exact(t, "text_box", '\t(text_box "Bristlemouth bus:\\nM3 threaded inserts\\nMP1-MP4"')
t = note(t, "Bristlemouth bus: JST GH 4-pin, side entry,\\nJ10 = BM1, J9 = BM2.\\nPins 1-2 = N, pins 3-4 = P (two pins per polarity).", 483.87, 148.59)
write_top(t)
print("  J10 BM1 (1-2 BM1_N, 3-4 BM1_P), J9 BM2 (1-2 BM2_N, 3-4 BM2_P)")
