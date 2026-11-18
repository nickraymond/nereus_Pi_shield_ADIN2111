"""The west N6 header J21 moves 0.04 mm east, to the header spacing of the N6 r3 model (Nick, this session's chat,
2026-11-18: "go, and move J21 and keep moving forward.").

KiCad's Python: stepJ21_move.py <board .kicad_pcb (a copy outside git)>
Frame: X' = KiCad x - 100, y = 100 - KiCad y (mm).
Why: the model's pin columns are at x 31.42 and 33.96 in the front view (N6_FACTS.md, source S5); seen from the back
that is X' = 35.56 - x = 4.14 and 1.60. The mock placed J21's columns at 4.10 and 1.56 (the un-mirrored values), so
the shield had 32.44 mm outer to outer against the model's 32.40 mm. J22 already matches (31.46 and 34.00).
No track ends on a J21 pad when this runs (checked below); the zones are refilled by kicad-cli afterwards.
Run with the lock check told to allow J21: ALLOW_REF=J21 sh run_C.sh stepJ21_move.py J21"""
import sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM; FM = pcbnew.FromMM
f = b.FindFootprintByReference("J21"); assert f
cols = sorted({round(mm(p.GetPosition().x) - 100, 3) for p in f.Pads()}); assert cols == [1.56, 4.1], cols
for t in b.GetTracks():
    if t.Type() != pcbnew.PCB_VIA_T: assert not any(p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd()) for p in f.Pads()), "a track ends on a J21 pad"
p0 = f.GetPosition(); f.SetPosition(pcbnew.VECTOR2I(p0.x + FM(0.04), p0.y))
cols = sorted({round(mm(p.GetPosition().x) - 100, 3) for p in f.Pads()}); assert cols == [1.6, 4.14], cols
pcbnew.SaveBoard(sys.argv[1], b)
print("J21 moved 0.04 mm east: pad columns now at X' %s (uuid %s)" % (cols, f.m_Uuid.AsString()))
