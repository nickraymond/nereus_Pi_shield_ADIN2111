"""Stage 21 fit: each vertical footprint at the old pin x and as far south as the edge allows (courtyard 39.5, pads 0.5 mm from
the edge), then 0.5 .. 3.0 mm further north; prints every other-net copper item closer than 0.10 mm (DRC min clearance) to a new pad,
and courtyard overlaps with other top-side parts. Items on the connector's own signal nets are not counted for the mounting pads
(they are the connector-end copper that would be re-routed). Last line: J9 at x + 0.15. Usage: <KiCad python> fit21.py <board>"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stage3_routing"))
import pcbnew, s3lib, math
from s3lib import N, sn, mm, V
LIB='/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_JST.pretty'
NEW={'J7':'JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical','J9':'JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical','J10':'JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical',
     'J8':'JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical','J3':'JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical'}
b=pcbnew.LoadBoard(sys.argv[1]); CLR=0.10
items=[]  # (desc, net, x0,y0,x1,y1, kind, data)
for t in b.GetTracks():
    n=sn(t.GetNetname())
    if t.GetClass()=='PCB_VIA':
        p=N(t.GetStart()); r=mm(t.GetWidth(pcbnew.F_Cu))/2; items.append(('via %s %s %s type %d'%(n,p,t.m_Uuid.AsString()[:8],t.GetViaType()),n,('cap',p,p,r)))
    elif t.GetLayer()==pcbnew.F_Cu:
        a,c=N(t.GetStart()),N(t.GetEnd()); items.append(('trk %s %s-%s w%.2f %s'%(n,a,c,mm(t.GetWidth()),t.m_Uuid.AsString()[:8]),n,('cap',a,c,mm(t.GetWidth())/2)))
REFS=list(NEW)
for f in b.GetFootprints():
    if f.GetReference() in NEW: continue
    for p in f.Pads():
        if not p.IsOnLayer(pcbnew.F_Cu): continue
        bb=p.GetBoundingBox(); x0,y0=N(bb.GetPosition()); x1,y1=N(bb.GetEnd()); items.append(('pad %s.%s %s'%(f.GetReference(),p.GetNumber(),sn(p.GetNetname())),sn(p.GetNetname()),('rect',x0,y0,x1,y1)))
crt=[]
for f in b.GetFootprints():
    if f.GetReference() in NEW or f.IsFlipped(): continue
    bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if bb.GetWidth()>0: x0,y0=N(bb.GetPosition()); x1,y1=N(bb.GetEnd()); crt.append((f.GetReference(),x0,y0,x1,y1))
def rect_d(r, it):
    x0,y0,x1,y1=r
    if it[0]=='rect':
        dx=max(it[1]-x1, x0-it[3], 0); dy=max(it[2]-y1, y0-it[4], 0); return math.hypot(dx,dy)
    _,a,c,rad=it; best=9
    for k in range(21):
        px=a[0]+(c[0]-a[0])*k/20; py=a[1]+(c[1]-a[1])*k/20
        dx=max(x0-px,px-x1,0); dy=max(y0-py,py-y1,0); best=min(best, math.hypot(dx,dy)-rad)
    return best
def check(ref, cx, cy, quiet=False):
    old=b.FindFootprintByReference(ref); nets={p.GetNumber():sn(p.GetNetname()) for p in old.Pads()}
    f=pcbnew.FootprintLoad(LIB,NEW[ref]); f.SetPosition(V(cx,cy))
    bad=[]
    for p in f.Pads():
        bb=p.GetBoundingBox(); x0,y0=N(bb.GetPosition()); x1,y1=N(bb.GetEnd()); pn=nets.get(p.GetNumber(),'') if p.GetNumber()!='MP' else ''
        if y1>39.5-0.5: bad.append(('edge', p.GetNumber(), y1))
        for d,n,it in items:
            if pn and n==pn: continue
            g=rect_d((x0,y0,x1,y1),it)
            if g<CLR: bad.append((p.GetNumber(),pn,round(g,3),d))
    cb=f.GetCourtyard(pcbnew.F_CrtYd).BBox(); x0,y0=N(cb.GetPosition()); x1,y1=N(cb.GetEnd())
    if y1>39.5+1e-6: bad.append(('courtyard below edge',y1))
    for r,a0,b0,a1,b1 in crt:
        if a0<x1 and x0<a1 and b0<y1 and y0<b1: bad.append(('courtyard overlaps',r))
    return bad, (x0,y0,x1,y1)
def check2(ref,cx,cy):
    old=b.FindFootprintByReference(ref); own={sn(p.GetNetname()) for p in old.Pads()}-{''}
    bad,cb=check(ref,cx,cy)
    out=[]
    for x in bad:
        if x[0]=='courtyard overlaps' or x[0]=='edge' or x[0]=='courtyard below edge': out.append(x); continue
        num,pn,g,d=x; n=d.split()[1]
        if num=='MP' and n in own and n!='GND': continue
        out.append(x)
    return out,cb
X={'J7':6.475,'J9':16.225,'J8':25.445,'J3':45.525,'J10':55.375}; YM={'J7':36.15,'J9':36.15,'J8':36.15,'J10':36.15,'J3':36.85}
for r in REFS:
    for d in (0,0.5,1.0,1.5,2.0,2.5,3.0):
        bad,cb=check2(r,X[r],YM[r]-d)
        print(r,'x %.3f y %.3f (north %.1f):'%(X[r],YM[r]-d,d),'; '.join(sorted(set(' '.join(x[3].split()[:4]) if len(x)==4 else str(x) for x in bad))) or 'CLEAN')
bad,cb=check2('J9',16.375,36.15); print('J9 x 16.375 y 36.15:', bad or 'CLEAN', 'courtyard', cb)
