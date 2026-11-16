"""Shared helpers for stage 2b (board parity with the stage-2 schematic). Run with KiCad's Python."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, netparse
mm, IU = pcbnew.ToMM, pcbnew.FromMM
DX, DY, W, H, RAD = 113.47, 89.34, 65.0, 39.5, 3.0
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, '..', 'board')
STOCK = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
LIBDIR = {'nereus': 'nereus.pretty', 'Vault': 'mote.pretty', 'urchin': 'urchin.pretty'}   # fp-lib-table of the project
V = lambda x, y: pcbnew.VECTOR2I(IU(x + DX), IU(y + DY))           # new-frame mm -> board point
N = lambda p: (round(mm(p.x) - DX, 3), round(mm(p.y) - DY, 3))     # board point -> new-frame mm
SKIP_FIELDS = {'Footprint', 'Reference', 'Value'}


def load_netlist(path):
    """comps[ref] = dict(value, fpid, path, sheetname, sheetfile, fields{name: text}, pads{num: (net, pinfunction, pintype)})"""
    root = netparse.sexpr(open(path, encoding='utf-8').read())
    f, v = netparse.find, netparse.val
    comps = {}
    for c in f(f(root, 'components')[0], 'comp'):
        fields = {}
        for fs in f(c, 'fields'):
            for x in f(fs, 'field'):
                fields[v(x, 'name')] = x[2] if len(x) > 2 else ''
        props = {v(p, 'name'): v(p, 'value') for p in f(c, 'property')}
        sp = f(c, 'sheetpath')[0]
        comps[v(c, 'ref')] = dict(value=v(c, 'value'), fpid=v(c, 'footprint'), path=v(sp, 'tstamps') + v(c, 'tstamps'),
                                  sheetname=v(sp, 'names'), sheetfile=props.get('Sheetfile', ''), fields=fields, props=props, pads={})
    for n in f(f(root, 'nets')[0], 'net'):
        for x in f(n, 'node'):
            comps[v(x, 'ref')]['pads'][v(x, 'pin')] = (v(n, 'name'), v(x, 'pinfunction'), v(x, 'pintype'))
    return comps


def fpid_str(fp):
    return fp.GetFPID().GetUniStringLibId()


def lib_footprint(fpid):
    lib, name = fpid.split(':')
    d = os.path.join(PROJ, LIBDIR[lib]) if lib in LIBDIR else STOCK + lib + '.pretty'
    f = pcbnew.FootprintLoad(d, name)
    if f is None: raise SystemExit('footprint not found: ' + fpid)
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    return f


def diff_one(fp, c):
    """List of (kind, text) differences between a board footprint and its netlist component."""
    out = []
    if fp.GetValue() != c['value']: out.append(('value', '%r -> %r' % (fp.GetValue(), c['value'])))
    if fpid_str(fp) != c['fpid']: out.append(('footprint', '%r -> %r' % (fpid_str(fp), c['fpid'])))
    if fp.GetPath().AsString() != c['path']: out.append(('path', '%r -> %r' % (fp.GetPath().AsString(), c['path'])))
    if fp.GetSheetname() != c['sheetname']: out.append(('sheetname', '%r -> %r' % (fp.GetSheetname(), c['sheetname'])))
    if fp.GetSheetfile() != c['sheetfile']: out.append(('sheetfile', '%r -> %r' % (fp.GetSheetfile(), c['sheetfile'])))
    for k, t in c['fields'].items():
        if k in SKIP_FIELDS: continue
        if not fp.HasField(k): out.append(('field', '%s: missing -> %r' % (k, t[:60])))
        elif fp.GetField(k).GetText() != t: out.append(('field', '%s: %r -> %r' % (k, fp.GetField(k).GetText()[:60], t[:60])))
    for p in fp.Pads():
        net, fn, ty = c['pads'].get(p.GetNumber(), ('', '', ''))
        if p.GetNetname() != net: out.append(('net', 'pad %s: %r -> %r' % (p.GetNumber(), p.GetNetname(), net)))
        if c['pads'].get(p.GetNumber()) and (p.GetPinFunction() != fn or p.GetPinType() != ty):
            out.append(('pin', 'pad %s: %s/%s -> %s/%s' % (p.GetNumber(), p.GetPinFunction(), p.GetPinType(), fn, ty)))
    padnums = {p.GetNumber() for p in fp.Pads()}
    for num in c['pads']:
        if num not in padnums: out.append(('nopad', 'schematic pin %s has no pad' % num))
    return out


def net(b, name):
    if not name: return b.FindNet(0)
    n = b.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); print('    new net', name)
    return n


def apply(b, fp, ref, c):
    """Set on one footprint what KiCad's "Update PCB from Schematic" sets: reference, value, library ID, symbol link,
    fields, pad nets, pin functions and pin types. Position, side and geometry are not touched."""
    fab = pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab
    fp.SetReference(ref); fp.SetValue(c['value'])
    lib, name = c['fpid'].split(':')
    if fpid_str(fp) != c['fpid']:
        if fp.GetFPID().GetUniStringLibItemName() != name: raise SystemExit('%s: board has a different footprint (%s), not relinked' % (ref, fpid_str(fp)))
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fp.SetPath(pcbnew.KIID_PATH(c['path'])); fp.SetSheetname(c['sheetname']); fp.SetSheetfile(c['sheetfile'])
    for k, t in c['fields'].items():
        if k in SKIP_FIELDS: continue
        if fp.HasField(k): fp.GetField(k).SetText(t)
        else:
            fl = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, k); fl.SetText(t); fl.SetVisible(False); fl.SetLayer(fab)
            fl.SetPosition(fp.GetPosition()); fp.Add(fl)
    for p in fp.Pads():
        nn, fn, ty = c['pads'].get(p.GetNumber(), ('', '', ''))
        if p.GetNetname() != nn: p.SetNet(net(b, nn))
        p.SetPinFunction(fn); p.SetPinType(ty)


def by_ref(b):
    return {f.GetReference(): f for f in list(b.GetFootprints())}


MOTE = '/Users/nickbuemond/Documents/GitHub/nereus_Pi_shield_ADIN2111/.claude/worktrees/adoring-mclaren-10dc39/KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb'


def locked_refs(b):
    """The mote core: footprints at the same position as on Sofar's board."""
    m = {f.GetReference(): f.GetPosition() for f in pcbnew.LoadBoard(MOTE).GetFootprints()}
    return {f.GetReference() for f in b.GetFootprints() if f.GetReference() in m and f.GetPosition() == m[f.GetReference()]}


def pad_rect(p):
    bb = p.GetBoundingBox()
    return (mm(bb.GetLeft()) - DX, mm(bb.GetTop()) - DY, mm(bb.GetRight()) - DX, mm(bb.GetBottom()) - DY)


def rect_pt(r, x, y):
    dx = max(r[0] - x, 0, x - r[2]); dy = max(r[1] - y, 0, y - r[3]); return (dx * dx + dy * dy) ** 0.5


def rect_seg(r, a, c):
    n = max(2, int(((a[0] - c[0]) ** 2 + (a[1] - c[1]) ** 2) ** 0.5 / 0.02) + 1)
    return min(rect_pt(r, a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n) for i in range(n + 1))


def rect_rect(r, q):
    dx = max(q[0] - r[2], r[0] - q[2], 0); dy = max(q[1] - r[3], r[1] - q[3], 0); return (dx * dx + dy * dy) ** 0.5
