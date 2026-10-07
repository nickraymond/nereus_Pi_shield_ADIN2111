#!/usr/bin/env python3
"""Render docs/design-review/bom.csv as a review PDF (A3 landscape): docs/design-review/bom.pdf.

One row per BOM line: Sofar's specified part, the planned part (what we'd build with at JLC, D27) and why, the
backups and how it's sourced. Rows where the planned part differs from Sofar's are highlighted. macOS only: the
HTML is laid out and printed to PDF by AppKit (tools/html2pdf.js via osascript). Python standard library only.

  python3 tools/bompdf.py
"""
import csv
import html
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "docs/design-review/bom.csv"
OUT = ROOT / "docs/design-review/bom.pdf"
CHANGED, SAME, HEAD = "#fff3c4", "#ffffff", "#dde4ee"


def esc(s):
    return html.escape(s or "")


def part(mpn, mfr, lcsc=""):
    bits = [f"<b>{esc(mpn)}</b>" if mpn else "—"]
    if mfr:
        bits.append(esc(mfr))
    if lcsc:
        bits.append(f"LCSC {esc(lcsc)}")
    return "<br>".join(bits)


def alt(r, n):
    mpn = r[f"Alt{n} MPN"]
    return "" if not mpn else f"{esc(mpn)} ({esc(r[f'Alt{n} Mfr'])}, {esc(r[f'Alt{n} LCSC'])})"


def build(rows):
    changed = [r for r in rows if r["Planned MPN"] and r["Planned MPN"] != r["Value (MPN)"]]
    head = (f"<h2>nereus_Pi_shield_ADIN2111 — BOM for review</h2>"
            f"<p>PCB-000001-AA rev AA · from <tt>docs/design-review/bom.csv</tt> · {date.today().isoformat()} · "
            f"{len(rows)} lines, {sum(int(r['Qty']) for r in rows if not r['DNP'])} fitted parts per board "
            f"(+ {sum(int(r['Qty']) for r in rows if r['DNP'])} DNP) · "
            f"<span style='background:{CHANGED}'>&nbsp;{len(changed)} lines where the planned part differs from "
            f"Sofar's&nbsp;</span> (for Sofar's review; nothing adopted before it, D26/D27)</p>")
    # widths in points; they add up to the printable A3-landscape width (1190 - 2 × 28 margins = 1134)
    cols = [("Refs", 80), ("Qty", 34), ("Sofar's part (specified)", 140), ("Planned part", 140),
            ("Why (planned note)", 250), ("Backups (Alt1 / Alt2)", 210), ("Sourcing", 150), ("Footprint", 130)]
    t = [f"<table border='1' cellspacing='0' cellpadding='3' width='1134' style='border-collapse:collapse'>",
         "<tr>" + "".join(f"<th style='background:{HEAD}' align='left' width='{w}'>{c}</th>" for c, w in cols) + "</tr>"]
    for r in rows:
        bg = CHANGED if r in changed else SAME
        dnp = " <i>(DNP)</i>" if r["DNP"] else ""
        alts = "<br>".join(a for a in (alt(r, 1), alt(r, 2)) if a)
        if alts and r["Alt note"]:
            alts += f"<br><i>{esc(r['Alt note'])}</i>"
        cells = [esc(r["Refs"]).replace(",", ", ") + dnp, esc(r["Qty"]),
                 part(r["Value (MPN)"], r["Mfr"]), part(r["Planned MPN"], r["Planned Mfr"], r["Planned LCSC"]),
                 esc(r["Planned note"]), alts, esc(r["Sourcing"]), esc(r["Footprint"].split(":")[-1])]
        t.append(f"<tr style='background:{bg}'>"
                 + "".join(f"<td valign='top' width='{w}'>{c}</td>" for c, (_, w) in zip(cells, cols)) + "</tr>")
    t.append("</table>")
    style = "<style>body{font-family:Helvetica;font-size:8pt} td,th{font-size:7.5pt} h2{font-size:13pt}</style>"
    return f"<html><head><meta charset='utf-8'>{style}</head><body>{head}{''.join(t)}</body></html>"


def main():
    rows = list(csv.DictReader(open(CSV, newline="")))
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "bom.html"
        page.write_text(build(rows))
        r = subprocess.run(["osascript", "-l", "JavaScript", str(ROOT / "tools/html2pdf.js"), str(page), str(OUT),
                            "landscape"], capture_output=True, text=True)
    if r.returncode != 0 or not OUT.exists() or OUT.stat().st_size == 0:
        sys.exit(f"bompdf: PDF not written ({r.stderr.strip() or r.stdout.strip()})")
    print(f"bompdf: {len(rows)} lines → {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
