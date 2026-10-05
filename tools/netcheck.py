#!/usr/bin/env python3
"""Compare schematic connectivity against the mote's copper.

Reads the mote board (read-only) and a KiCad netlist exported from our
schematic, then compares which pins are joined together. Net names are
ignored (the Altium import renamed them); only parts present in both designs
are compared.

  opens  : a copper net whose pins are split across several schematic nets
  shorts : a schematic net that joins pins from several copper nets
  missing: a pin/pad on a shared part that exists on only one side

Parts listed in the exclusion file (scheduled for deletion) are treated as
already removed from both sides.

Exit code 0 = connectivity matches, 1 = differences, 2 = bad input.
Python standard library only.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

DEFAULT_PCB = "KiCAD_reference_designs/20250409_BM_Mote_000639-AB/BM_Mote_000639-AB.kicad_pcb"
DEFAULT_NETLIST = "docs/design-review/out/netlist.net"
DEFAULT_REPORT = "docs/design-review/netcheck.md"
DEFAULT_EXCLUDE = "docs/design-review/excluded_parts.txt"


def read_exclusions(text):
    """Return {ref: reason} from 'REF  # reason' lines; blank and comment lines ignored."""
    out = {}
    for line in text.splitlines():
        ref, _, reason = line.partition("#")
        if ref.strip():
            out[ref.strip()] = reason.strip()
    return out


def blocks(text, head):
    """Yield every balanced s-expression in text that starts with '(' + head."""
    key = "(" + head
    i = 0
    while True:
        i = text.find(key, i)
        if i < 0:
            return
        depth, j = 0, i
        while True:
            c = text[j]
            if c == '"':
                j += 1
                while text[j] != '"':
                    j += 2 if text[j] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        yield text[i:j + 1]
        i = j + 1


def pcb_connectivity(text):
    """Return ({net name: {"REF.PAD"}}, {"REF.PAD"} for pads with no net)."""
    nets = collections.defaultdict(set)
    no_net = set()
    for fp in blocks(text, "footprint "):
        m = (re.search(r'\(property "Reference" "([^"]+)"', fp)
             or re.search(r'\(fp_text reference "([^"]+)"', fp))
        if not m:
            continue
        ref = m.group(1)
        for pad in blocks(fp, "pad "):
            num = re.match(r'\(pad "([^"]*)"', pad)
            if not num or not num.group(1):
                continue  # mechanical pad without a number
            net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pad)
            node = f"{ref}.{num.group(1)}"
            if net and net.group(1):
                nets[net.group(1)].add(node)
            else:
                no_net.add(node)
    return nets, no_net


def netlist_connectivity(text):
    """Return {net name: {"REF.PIN"}} from a kicadsexpr netlist."""
    nets = {}
    for net in blocks(text, "net (code"):
        name = re.search(r'\(name "([^"]*)"\)', net).group(1)
        nets[name] = {f"{r}.{p}" for r, p in
                      re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', net)}
    return nets


def ref_of(node):
    return node.rsplit(".", 1)[0]


def compare(pcb_nets, pcb_no_net, sch_nets, excluded=()):
    pcb_refs = {ref_of(n) for v in pcb_nets.values() for n in v} | {ref_of(n) for n in pcb_no_net}
    sch_refs = {ref_of(n) for v in sch_nets.values() for n in v}
    shared = (pcb_refs & sch_refs) - set(excluded)

    def restrict(nets):
        return {name: frozenset(n for n in nodes if ref_of(n) in shared)
                for name, nodes in nets.items()}

    pcb = {k: v for k, v in restrict(pcb_nets).items() if v}
    sch = {k: v for k, v in restrict(sch_nets).items() if v}
    pcb_of = {n: name for name, nodes in pcb.items() for n in nodes}
    sch_of = {n: name for name, nodes in sch.items() for n in nodes}
    pcb_no_net = {n for n in pcb_no_net if ref_of(n) in shared}

    multi = {k: v for k, v in pcb.items() if len(v) > 1}
    sch_sets = set(sch.values())
    matched = sorted(k for k, v in multi.items() if v in sch_sets)
    opens = {k: v for k, v in multi.items() if v not in sch_sets
             and len({sch_of.get(n) for n in v}) > 1}
    shorts = {k: v for k, v in sch.items()
              if len({pcb_of.get(n, "(no copper net)") for n in v
                      if n in pcb_of or n in pcb_no_net}) > 1}
    all_pcb = set(pcb_of) | pcb_no_net
    return {
        "matched": matched, "multi": multi, "opens": opens, "shorts": shorts,
        "pcb_of": pcb_of, "sch_of": sch_of,
        "pins_not_in_copper": sorted(set(sch_of) - all_pcb),
        "pads_not_in_schematic": sorted(set(pcb_of) - set(sch_of)),
        "only_pcb": sorted(pcb_refs - sch_refs), "only_sch": sorted(sch_refs - pcb_refs),
        "excluded": sorted(set(excluded) & (pcb_refs | sch_refs)),
        "excluded_missing": sorted(set(excluded) - (pcb_refs | sch_refs)),
    }


def natural(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def render(r, pcb_path, netlist_path, reasons=None):
    ok = not (r["opens"] or r["shorts"] or r["pins_not_in_copper"] or r["pads_not_in_schematic"])
    out = ["# Net check — schematic vs mote copper", "",
           f"*Copper: `{pcb_path}` · Schematic netlist: `{netlist_path}`*", "",
           "Generated by `tools/netcheck.py`; don't edit by hand.", "",
           "| Result | Count |", "|---|---|",
           f"| Copper nets (2+ pins on shared parts) | {len(r['multi'])} |",
           f"| Matched exactly | {len(r['matched'])} |",
           f"| Opens (copper net split in schematic) | {len(r['opens'])} |",
           f"| Shorts (schematic joins copper nets) | {len(r['shorts'])} |",
           f"| Schematic pins with no copper pad | {len(r['pins_not_in_copper'])} |",
           f"| Copper pads with no schematic pin | {len(r['pads_not_in_schematic'])} |",
           f"| Parts only in copper (removed) | {len(r['only_pcb'])} |",
           f"| Parts only in schematic (new) | {len(r['only_sch'])} |",
           f"| Parts excluded (scheduled for deletion) | {len(r['excluded'])} |",
           "", f"**Status: {'MATCH' if ok else 'DIFFERENCES'}**", ""]
    if r["excluded"]:
        reasons = reasons or {}
        out += ["## Excluded parts", "", "Treated as already removed (see the exclusion file).", ""]
        out += [f"- {ref} — {reasons.get(ref, '')}".rstrip(" —") for ref in sorted(r["excluded"], key=natural)]
        out.append("")
    if r["excluded_missing"]:
        out += ["## Exclusion list entries no longer in either design", "",
                "Delete these lines from the exclusion file: "
                + ", ".join(sorted(r["excluded_missing"], key=natural)), ""]
    if r["opens"]:
        out += ["## Opens", "", "Pins joined in copper but split in the schematic, "
                "grouped by the schematic net each pin landed on.", ""]
        for name in sorted(r["opens"], key=natural):
            out.append(f"### {name} ({len(r['opens'][name])} pins)")
            groups = collections.defaultdict(list)
            for n in r["opens"][name]:
                groups[r["sch_of"].get(n, "(pin missing)")].append(n)
            for sch_name in sorted(groups, key=lambda g: (-len(groups[g]), g)):
                out.append(f"- `{sch_name}`: {', '.join(sorted(groups[sch_name], key=natural))}")
            out.append("")
    if r["shorts"]:
        out += ["## Shorts", "", "Schematic nets that join pins from different copper nets.", ""]
        for name in sorted(r["shorts"], key=natural):
            groups = collections.defaultdict(list)
            for n in r["shorts"][name]:
                groups[r["pcb_of"].get(n, "(no copper net)")].append(n)
            out.append(f"### `{name}`")
            for pcb_name in sorted(groups):
                out.append(f"- copper `{pcb_name}`: {', '.join(sorted(groups[pcb_name], key=natural))}")
            out.append("")
    for title, key in (("Schematic pins with no copper pad", "pins_not_in_copper"),
                       ("Copper pads with no schematic pin", "pads_not_in_schematic"),
                       ("Parts only in copper (removed)", "only_pcb"),
                       ("Parts only in schematic (new)", "only_sch")):
        if r[key]:
            out += [f"## {title}", "", ", ".join(sorted(r[key], key=natural)), ""]
    return "\n".join(out), ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pcb", default=DEFAULT_PCB, help="mote board (read-only)")
    ap.add_argument("--netlist", default=DEFAULT_NETLIST, help="kicadsexpr netlist from our schematic")
    ap.add_argument("--report", default=DEFAULT_REPORT, help="markdown report to write")
    ap.add_argument("--exclude", default=DEFAULT_EXCLUDE,
                    help="parts scheduled for deletion ('' to disable)")
    a = ap.parse_args(argv)
    reasons = {}
    if a.exclude:
        if not Path(a.exclude).is_file():
            print(f"netcheck: exclusion file not found: {a.exclude}\n"
                  f"  hint: pass --exclude '' to run without one", file=sys.stderr)
            return 2
        reasons = read_exclusions(Path(a.exclude).read_text())
    for p in (a.pcb, a.netlist):
        if not Path(p).is_file() or Path(p).stat().st_size == 0:
            print(f"netcheck: missing or empty input: {p}\n"
                  f"  hint: run tools/check.sh to export the netlist first", file=sys.stderr)
            return 2
    pcb_nets, pcb_no_net = pcb_connectivity(Path(a.pcb).read_text())
    sch_nets = netlist_connectivity(Path(a.netlist).read_text())
    if not pcb_nets or not sch_nets:
        print(f"netcheck: parsed no nets (copper {len(pcb_nets)}, schematic {len(sch_nets)}); "
              "is the file format right?", file=sys.stderr)
        return 2
    r = compare(pcb_nets, pcb_no_net, sch_nets, reasons)
    text, ok = render(r, a.pcb, a.netlist, reasons)
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text(text + "\n")
    print(f"netcheck: {len(r['matched'])}/{len(r['multi'])} copper nets matched; "
          f"{len(r['opens'])} opens, {len(r['shorts'])} shorts, "
          f"{len(r['pins_not_in_copper'])}+{len(r['pads_not_in_schematic'])} unpaired pins; "
          f"{len(r['excluded'])} parts excluded → {a.report}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
