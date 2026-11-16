"""Gate 3: every new part's footprint loads from its library (pcbnew), pad numbers cover the symbol's pins, and its
value / MPN fields are listed. Run with KiCad's Python."""
import os
import re
import sys
import pcbnew
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netparse  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.abspath(os.path.join(HERE, "..", "board"))
STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
local = dict(re.findall(r'\(name "([^"]+)"\)\(type "KiCad"\)\(uri "\$\{KIPRJMOD\}/([^"]+)"\)', open(os.path.join(BOARD, "fp-lib-table")).read()))
bp, _ = netparse.load(os.path.join(HERE, "..", "netlist_baseline.net"))
sp, sn = netparse.load(os.path.join(HERE, "..", "netlist_stage2.net"))
plug = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
pins = {}
for net, nodes in sn.items():
    for n in nodes:
        r, p = n.split(".", 1)
        pins.setdefault(r, set()).add(p)
bad = 0
print("| Ref | Value | MPN (PLANNED MPN) | Footprint | Library | Pads | Symbol pins |")
print("|---|---|---|---|---|---|---|")
for ref in sorted(set(sp) - set(bp), key=lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r)))):
    part = sp[ref]
    nick, name = part["footprint"].split(":", 1)
    path = os.path.join(BOARD, local[nick]) if nick in local else os.path.join(STOCK, nick + ".pretty")
    fp = plug.FootprintLoad(path, name) if os.path.isfile(os.path.join(path, name + ".kicad_mod")) else None
    pads = sorted({p.GetNumber() for p in fp.Pads()}) if fp else []
    ok = fp is not None and pins[ref] <= set(pads) and part["value"]
    bad += not ok
    print("| %s | %s | %s | %s | %s | %s | %s |%s" % (ref, part["value"], part["fields"].get("PLANNED MPN") or "to choose", part["footprint"],
          "project " + local[nick] if nick in local else "KiCad stock", " ".join(pads), " ".join(sorted(pins[ref], key=lambda s: int(s))), "" if ok else "  <-- PROBLEM"))
print("\n%d new parts, %d problems" % (len(set(sp) - set(bp)), bad))
sys.exit(1 if bad else 0)
