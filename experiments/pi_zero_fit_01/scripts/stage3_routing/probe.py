"""Development aid (not part of the build): where is a straight run free?  <KiCad python> probe.py <board> then python on stdin.
scan_h(layer, x0, x1, ylo, yhi, w, net) prints the y ranges where a horizontal track x0..x1 passes the pre-check; scan_v likewise."""
import sys, s3lib
r = s3lib.Router(sys.argv[1], 'probe'); g = r.geo
def _rng(vals, step):
    out = []; s = None; p = None
    for v in vals:
        if s is None: s = p = v
        elif v - p > step * 1.5: out.append((round(s, 2), round(p, 2))); s = p = v
        else: p = v
    if s is not None: out.append((round(s, 2), round(p, 2)))
    return out
def scan_h(layer, x0, x1, ylo, yhi, w, net, clr=0.15, step=0.05):
    ok = []; y = ylo
    while y <= yhi + 1e-9:
        if not g.path(layer, [(x0, y), (x1, y)], w, net, clr): ok.append(y)
        y += step
    print('H %s x %.2f..%.2f w %.2f %s: free y %s' % (layer, x0, x1, w, net, _rng(ok, step)))
def scan_v(layer, y0, y1, xlo, xhi, w, net, clr=0.15, step=0.05):
    ok = []; x = xlo
    while x <= xhi + 1e-9:
        if not g.path(layer, [(x, y0), (x, y1)], w, net, clr): ok.append(x)
        x += step
    print('V %s y %.2f..%.2f w %.2f %s: free x %s' % (layer, y0, y1, w, net, _rng(ok, step)))
def chk(layer, pts, w, net, clr=0.15):
    h = g.path(layer, pts, w, net, clr); print('chk %s %s w%.2f %s: %s' % (layer, net, w, pts, h[:6] if h else 'clear'))
def chkv(p, net, d=0.6, drill=0.3, clr=0.15):
    h = g.via(p, d, drill, net, clr); print('via %s %s: %s' % (net, p, h[:6] if h else 'clear'))
exec(sys.stdin.read())
