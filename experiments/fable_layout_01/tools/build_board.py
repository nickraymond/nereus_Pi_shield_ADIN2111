#!/usr/bin/env python3
"""M0: build a fresh board from the schematic's netlist (KiCad 9 pcbnew; KiCad itself stays closed).

  $PY tools/build_board.py out/m0/netlist.net board/nereus_Pi_shield_ADIN2111.kicad_pcb

For every component in the netlist: load its footprint from the project (Vault, nereus) or the stock KiCad 9
libraries, set reference / value / library id / schematic path / DNP / exclude-from-BOM, assign every pad its net.
Adds the four Pi standoff holes H1-H4 as board-only footprints (BRIEF §3). Parts are parked on a grid east of the
board frame (x >= 60 mm); M1/M2 place them. Layers: 6 copper, the mote's names and roles (BRIEF §2).
"""
import os
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import netlist  # noqa: E402

STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
# the mote's copper layer names and roles, in stack order (BRIEF §2)
LAYERS = [(pcbnew.F_Cu, "Top Layer", pcbnew.LT_SIGNAL), (pcbnew.In1_Cu, "Internal 1", pcbnew.LT_SIGNAL),
          (pcbnew.In2_Cu, "GND Plane", pcbnew.LT_POWER), (pcbnew.In3_Cu, "Internal 2", pcbnew.LT_SIGNAL),
          (pcbnew.In4_Cu, "PWR Plane", pcbnew.LT_POWER), (pcbnew.B_Cu, "6 Bottom Layer", pcbnew.LT_SIGNAL)]
HOLES = {"H1": (3.5, 3.5), "H2": (26.5, 3.5), "H3": (3.5, 61.5), "H4": (26.5, 61.5)}   # BRIEF §3, frame mm
MM = pcbnew.FromMM


def lib_dir(board_dir, nickname):
    return {"Vault": board_dir / "mote.pretty", "nereus": board_dir / "nereus.pretty"}.get(
        nickname, Path(STOCK) / f"{nickname}.pretty")


def load_footprint(board_dir, fpid):
    nick, name = fpid.split(":", 1)
    d = lib_dir(board_dir, nick)
    if not (d / f"{name}.kicad_mod").is_file():
        raise SystemExit(f"footprint not found: {fpid} (looked in {d}); fix the library table or the field")
    fp = pcbnew.FootprintLoad(str(d), name)
    if fp is None:
        raise SystemExit(f"pcbnew could not load {fpid} from {d}")
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    return fp


def main(net_path, pcb_path):
    pcb_path = Path(pcb_path)
    board_dir = pcb_path.parent
    comps, nets = netlist.read(net_path)

    board = pcbnew.BOARD()
    board.SetFileName(str(pcb_path))
    board.SetCopperLayerCount(6)
    for lid, name, kind in LAYERS:
        board.SetLayerName(lid, name)
        board.SetLayerType(lid, kind)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(MM(1.6))

    # nets first, so pads can be assigned
    net_items = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        net_items[name] = ni
    pad_net = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pad_net[(ref, pin)] = name

    col, row = 0, 0
    missing_pads = []
    for c in sorted(comps, key=lambda c: c.ref):
        fp = load_footprint(board_dir, c.footprint)
        fp.SetReference(c.ref)
        fp.SetValue(c.value)
        fp.SetPath(pcbnew.KIID_PATH(c.path))
        attrs = fp.GetAttributes()
        if c.dnp:
            attrs |= pcbnew.FP_DNP
        if c.exclude_from_bom:
            attrs |= pcbnew.FP_EXCLUDE_FROM_BOM
        fp.SetAttributes(attrs)
        if c.datasheet:
            fp.SetField("Datasheet", c.datasheet)
        if c.description:
            fp.SetField("Description", c.description)
        # park on a grid east of the frame: 10 mm pitch, 12 per row
        fp.SetPosition(pcbnew.VECTOR2I(MM(70 + 10 * col), MM(10 * row)))
        col += 1
        if col == 12:
            col, row = 0, row + 1
        board.Add(fp)
        for pad in fp.Pads():
            num = pad.GetNumber()
            if not num:
                continue                       # mechanical / unnumbered pads keep no net
            key = (c.ref, num)
            if key in pad_net:
                pad.SetNet(net_items[pad_net[key]])
            else:
                missing_pads.append(f"{c.ref}.{num}")
    # Pi standoff holes, board-only (not in the schematic)
    for ref, (x, y) in HOLES.items():
        fp = load_footprint(board_dir, "MountingHole:MountingHole_2.7mm_M2.5")
        fp.SetReference(ref)
        fp.SetValue("M2.5 Pi standoff")
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM
                         | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        board.Add(fp)

    pcbnew.SaveBoard(str(pcb_path), board, True)   # skip project settings: the .kicad_pro is edited by hand
    print(f"wrote {pcb_path}: {len(list(board.GetFootprints()))} footprints, {len(nets)} nets")
    # pads with a number but no schematic pin: expected only for pins the schematic leaves unconnected
    print("numbered pads without a schematic node:", len(missing_pads), " ".join(missing_pads[:40]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
