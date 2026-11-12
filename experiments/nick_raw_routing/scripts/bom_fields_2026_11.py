#!/usr/bin/env python3
"""BOM review 2026-11: bring the part fields of the frozen board's schematic in line with the part to order.

Field edits only (PLANNED MPN / MFR / LCSC / NOTE, SOURCING, ALT...), on the sheets beside this folder. No Value,
Footprint, wire, label or flag is touched, so the netlist and the board stay as they are. Every figure below was
read on 2026-11-11 from JLC's parts search (table: ~/NereusData/nereus_Pi_shield_ADIN2111/bom_review_2026-11-11/
jlc_stock_2026-11-11.tsv); the reasons are in docs/design-review/bom_review_2026-11.md.

  python3 bom_fields_2026_11.py            # dry run: print every change
  python3 bom_fields_2026_11.py --write    # edit the sheets
  python3 bom_fields_2026_11.py --json f   # also save the change list as JSON

Run with KiCad closed. Running it twice changes nothing the second time.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SHEETS = sorted(HERE.glob("BM_Mote_1_*.kicad_sch")) + [HERE / "nick_raw_routing.kicad_sch"]
PROP = re.compile(r'\t\t\(property "((?:[^"\\]|\\.)*)" "((?:[^"\\]|\\.)*)"\n(?:\t\t\t[^\n]*\n)*\t\t\)\n')

RD = "2026-11-11"
STOCK = f"JLC stock (read {RD})"
SPEC = f"As specified; in JLC stock (read {RD})"
NOT_SOFAR = STOCK + "; not Sofar's part, see PLANNED NOTE"
MOTE = "Sofar's mote file gives no alternate"


def bought(qty):
    return (f"Nick's JLC parts library: global sourcing order DOB202610190524705 (2026-10-18), qty {qty}; "
            "pick it from My Parts Lib at the PCBA order")


def line(refs, mpn, mfr, lcsc, note=SPEC, sourcing=STOCK, **extra):
    fields = {"PLANNED MPN": mpn, "PLANNED MFR": mfr, "PLANNED LCSC": lcsc, "PLANNED NOTE": note,
              "SOURCING": sourcing}
    fields.update({k.replace("_", " "): v for k, v in extra.items()})
    return refs.split(","), fields


LINES = [
    line("C1,C3,C9,C10,C11,C12,C13,C14,C15,C28,C53", "CL05A104KA5NNNC", "Samsung", "C100072"),
    line("C2,C4", "CL05A105KP5NNNC", "Samsung", "C14445"),
    line("C5,C6", "CC0402KRX5R6BB684", "Yageo", "C113784"),
    line("C7,C8", "CC0402JRNPO9BN150", "Yageo", "C106997"),
    line("C16,C18,C24,C25", "08051C474KAT2A", "KYOCERA AVX", "C597304",
         f"As specified: Sofar's part is in JLC stock now (8,865 on {RD}, need 82; JLC's listing shows no maker "
         "name). Planned before: YAGEO CC0805KKX7R0BB474, now ALT1"),
    line("C17,C26", "C2012X7S2A105KT000N", "TDK", "C342785",
         f"Specified C2012X7S2A105K125AB has JLC stock 0 ({RD}) and {MOTE}. Same maker and series, 1 µF ±10 % "
         "100 V X7S 0805, JLC stock 7,130 (need 42); thickness not confirmed (K125AB is 1.25 mm, KT000N doesn't "
         "state it)", NOT_SOFAR),
    line("C19,C27", "C0805C102MDRACTU", "KEMET", "C2181610",
         f"As specified: Sofar's part is in JLC stock now (188 on {RD}, need 40). Planned before: KEMET "
         "C0805C102KDRACTU, now ALT1"),
    line("C20,C29,C49,C50,C54", "GRM188R72A104KA35D", "Murata", "C77058"),
    line("C21", "CL32B106KBJNNNE", "Samsung", "C138687",
         f"As specified: Sofar's part is in JLC stock now (77,751 on {RD}, need 20). Planned before: Taiyo Yuden "
         "UMK325AB7106KM-T, now ALT2"),
    line("C22,C23", "EEEFT1H470AP", "Panasonic", "C92059",
         f"As specified (Sofar's part, kept under SPEC constraint 8); {MOTE}. JLC public stock 0 on {RD}",
         "OPEN (Nick): the 2026-10-23 review sheet says 60 ordered; confirm they are in My Parts Lib before the "
         "PCBA order",
         ALT_NOTE="Sofar review: bus damping; a newly sourced replacement must be potting-safe (constraint 8), so "
                  "no like-for-like alternate"),
    line("C30,C55", "UMK107BBJ225KA-T", "Taiyo Yuden", "C268016",
         SPEC + "; Taiyo Yuden now lists it as MSASU168BB5225KTNA01"),
    line("C31", "CL10A226MQ8NRNC", "Samsung", "C59461",
         f"Specified C1608X5R0J226M080AC has JLC stock 1 ({RD}) and {MOTE}. Same spec, 22 µF ±20 % 6.3 V X5R "
         "0603; JLC Basic part, stock 6,741,783 (need 30)", NOT_SOFAR),
    line("C32", "GRJ155R60J106ME11D", "Murata", "C469527"),
    line("C33", "GRM155R60J475ME87D", "Murata", "C76996"),
    line("C56,C57", "GRM21BR61C226ME44L", "Murata", "C86817"),
    line("C58", "GRM155R61A475MEAAD", "Murata", "C335105"),
    line("C59", "CL05A224KA5NNNC", "Samsung", "C47129"),
    line("D1", "SMA6F33A-M3/H", "Vishay", "C7083040",
         "Sofar's own listed alternate 1 (mote file, MANUFACTURERPARTNUMBER1); the specified ST SMA6F33A is "
         f"obsolete (JLC stock 2 on {RD})", bought(27)),
    line("D2,D3", "RB058LAM-60TFTR", "ROHM", "C3757753",
         f"As specified; JLC public stock 10 on {RD} (need 40), so from the parts bought", bought(45)),
    line("D4,D5", "CDSOD323-T36SC", "Bourns", "C911382",
         SPEC + ": 1,123, need 40. Pick the BOURNS listing; JLC has two other makers' parts of the same name"),
    line("D8", "KT-0603R", "Hubei KENTO", "C2286"),
    line("D9,D10", "KT-0603YG", "Hubei KENTO", "C2289"),
    line("F1", "BSMD1206-150-16V", "BHFUSE", "C883133",
         f"1.5 A hold / 3 A trip; LiFePO4 charge bridge open (0.57 A); in JLC stock (read {RD})",
         STOCK + ". OPEN (Nick): a PPTC resettable fuse, which SPEC constraint 8 bars on newly sourced parts"),
    line("J1", "TBD", "", "",
         "Part not chosen: 2×20 2.54 mm female TH socket, height open (Nick)",
         f"OPEN (Nick): part not chosen, socket height open. In JLC stock on {RD}: ZHOURI 2.54-2*20 C2977589 "
         "(37,698), Megastar ZX-PM2.54-2-20PY C7499354 (6,641), both 8.5 mm by JLC's text"),
    line("J3", "SM04B-SRSS-TB(LF)(SN)", "JST", "C160404",
         f"Qwiic connector (I2C3); in JLC stock (read {RD})"),
    line("L1,L2", "SRF1260-101M", "Bourns", "C6496096",
         f"As specified; JLC stock 92 on {RD} (need 40)",
         STOCK + "; the 2026-10-23 review sheet says 42 were also bought: check My Parts Lib"),
    line("L3,L6", "PA5432.822NLT", "Pulse (YAGEO group)", "C17230195",
         f"As specified; JLC public stock 0 on {RD}, so from the parts bought", bought(42)),
    line("L4", "DFE201612E-2R2M=P2", "Murata", "C337893"),
    line("MP1,MP2,MP3,MP4", "78614015360", "Würth Elektronik", "C17256375",
         f"As specified; JLC public stock 0 on {RD}, so from the parts bought", bought(84)),
    line("R1,R44,R45,R46", "RC0402FR-071K5L", "Yageo", "C114759"),
    line("R2,R3,R4,R5,R6,R9,R26,R27", "ERJ-2RKF4701X", "Panasonic", "C400631"),
    line("R7,R10,R24", "RC0402JR-0710KL", "Yageo", "C60489"),
    line("R8", "UR73D1JTTD10L0F", "KOA Speer", "C2482319",
         f"As specified if the 25 bought are in My Parts Lib (JLC public stock 0 on {RD}). If they are not: "
         "Sofar's own listed alternate 7, Stackpole CSRF0603FT10L0 (ALT1), JLC stock 9,822",
         "OPEN (Nick): the 2026-10-23 review sheet says 25 ordered (need 20 + 5 attrition); confirm in My Parts "
         "Lib, else order ALT1 from JLC stock",
         ALT1_MPN="CSRF0603FT10L0", ALT1_MFR="Stackpole", ALT1_LCSC="C346485",
         ALT2_MPN="MFL0603R0100FA", ALT2_MFR="EATON", ALT2_LCSC="C6090593",
         ALT_NOTE=f"Sofar's own listed alternates 7 and 1 (mote file, MANUFACTURERPARTNUMBER7 / 1); JLC stock on "
                  f"{RD}: 9,822 and 16 (16 is short of 20). Sofar's other five: stock 0 or no listing. Not on "
                  "Sofar's list, in JLC stock: ROHM PMR03EZPFU10L0 C308571 (pads not confirmed), Vishay "
                  "WSLP0603R0100FEA C5334451"),
    line("R11", "CRCW12100000Z0EA", "Vishay Dale", "C844880", "As specified; DNP (not fitted)",
         "DNP: not ordered"),
    line("R14,R18", "RT0402BRD07100RL", "YAGEO", "C705627",
         f"Specified RR0510P-101-D has JLC stock 0 ({RD}) and {MOTE}. 100 Ω thin film 0402, ±0.1 % ±25 ppm "
         "(tighter than the specified ±0.5 %); JLC stock 345,748 (need 48)", NOT_SOFAR),
    line("R15,R16", "CRCW08057R50FKEAHP", "Vishay Dale", "C313962",
         f"As specified (pulse-rated part of the bus damper); {MOTE}. JLC public stock 0 on {RD}",
         "OPEN (Nick): the 2026-10-23 review sheet says 50 ordered; confirm they are in My Parts Lib before the "
         "PCBA order",
         ALT1_MPN="SR0805FR-477R5L", ALT1_MFR="YAGEO", ALT1_LCSC="C873769",
         ALT_NOTE="Not on Sofar's list: 7.5 Ω ±1 % 0.5 W, ±200 vs ±100 ppm/°C, pulse rating not stated; JLC stock "
                  f"5,492 on {RD}"),
    line("R20,R39", "RTT021824FTH", "RALEC", "C166520",
         f"Specified CRCW04021M82FKED has JLC stock 0 ({RD}) and {MOTE}. Same spec: 1.82 MΩ ±1 % 62.5 mW 50 V "
         "±100 ppm 0402; JLC stock 7,566 (need 50)", NOT_SOFAR),
    line("R21,R35,R36,R37,R43", "RMCF0402FT100K", "Stackpole", "C7055151",
         f"As specified: Sofar's part is in JLC stock now (1,058 on {RD}, need 110). Planned before: UNI-ROYAL "
         "0402WGF1003TCE (JLC Basic), now ALT1"),
    line("R22,R40", "RC0402FR-07200KL", "Yageo", "C114763"),
    line("R23", "RC0402FR-0722K1L", "Yageo", "C163478"),
    line("R34", "RC0402FR-079K09L", "Yageo", "C274897",
         f"As specified: in JLC stock now (4,378 on {RD}, need 30). Planned before: YAGEO AC0402FR-079K09L, now "
         "ALT1"),
    line("R38", "0402WGF1332TCE", "UNI-ROYAL", "C122547",
         f"13.3k 1% 0402 for 5V buck at 5.11 V (was 13.7k); in JLC stock (read {RD})"),
    line("R41", "RC0402FR-071ML", "Yageo", "C138033"),
    line("R42", "RMCF0402FT10K0", "Stackpole", "C6111655"),
    line("R47", "RC0402FR-071KL", "Yageo", "C106235",
         f"As specified: 1 kΩ (Nick, 2026-11-11); in JLC stock (read {RD})"),
    line("T1,T2", "74930000", "Würth Elektronik", "C4354923"),
    line("U1", "ADIN2111BCPZ", "Analog Devices", "C3226964",
         f"As specified; JLC public stock 0 on {RD}, so from the parts bought. JLC has a second listing, "
         "C56341494: use the number My Parts Lib shows", bought(22)),
    line("U2,U3", "AP22913CN4-7", "Diodes Inc.", "C2150198",
         f"As specified; JLC public stock 33 on {RD} (need 40), so from the parts bought", bought(42)),
    line("U4", "INA232AIDDFR", "Texas Instruments", "C5447660"),
    line("U5,U10", "LMR51430YDDCR", "Texas Instruments", "C5210749"),
    line("U6", "TPS62840YBGR", "Texas Instruments", "C2071139"),
    line("U11", "TPS26621DRCR", "Texas Instruments", "C1848341"),
    line("Y1", "ABM11W-25.0000MHZ-6-K1Z-T3", "Abracon", "C6851222",
         f"As specified; JLC public stock 0 on {RD}, so from the parts bought", bought(22)),
]

# J3 came with lower-case field names from KiCad's dialog; same fields, upper-case names like every other part.
RENAME = {"J3": {"Planned MPN": "PLANNED MPN", "Planned MFR": "PLANNED MFR", "Planned LCSC": "PLANNED LCSC",
                 "Planned NOTE": "PLANNED NOTE"}}


def symbol_blocks(text):
    """Yield (start, end) of every placed symbol: a top-level '\\t(symbol' block that has a lib_id."""
    for m in re.finditer(r'^\t\(symbol\n', text, re.M):
        i, depth, quoted = m.start() + 1, 0, False
        while True:
            c = text[i]
            if quoted:
                if c == "\\":
                    i += 1
                elif c == '"':
                    quoted = False
            elif c == '"':
                quoted = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        if "(lib_id " in text[m.start():m.start() + 300]:
            yield m.start(), i + 2  # through the newline


def edit_block(block, ref, fields, changes):
    for old, new in RENAME.get(ref, {}).items():
        if f'(property "{old}" ' in block and f'(property "{new}" ' not in block:
            block = block.replace(f'(property "{old}" ', f'(property "{new}" ', 1)
            changes.append((ref, new, f"(field named {old})", "(renamed)"))
    for name, value in fields.items():
        assert '"' not in value and "\\" not in value, (ref, name)
        found = [m for m in PROP.finditer(block) if m.group(1) == name]
        assert len(found) <= 1, (ref, name, "more than once")
        if found:
            m = found[0]
            if m.group(2) != value:
                new = m.group(0).replace(f'"{name}" "{m.group(2)}"', f'"{name}" "{value}"', 1)
                block = block[:m.start()] + new + block[m.end():]
                changes.append((ref, name, m.group(2), value))
        elif value:
            # a new hidden field, in the form of this symbol's own PLANNED MPN field (same place on the sheet)
            tpl = [m for m in PROP.finditer(block) if m.group(1) == "PLANNED MPN"]
            assert tpl and "(hide yes)" in tpl[0].group(0), (ref, name, "no hidden PLANNED MPN to copy")
            t = tpl[0]
            new = t.group(0).replace(f'"PLANNED MPN" "{t.group(2)}"', f'"{name}" "{value}"', 1)
            last = list(PROP.finditer(block))[-1]
            block = block[:last.end()] + new + block[last.end():]
            changes.append((ref, name, "(no field)", value))
    return block


def main():
    want = {}
    for refs, fields in LINES:
        for r in refs:
            assert r not in want, r
            want[r] = fields
    seen, missed, changes, out = set(), set(), [], {}
    for path in SHEETS:
        text = path.read_text(encoding="utf-8")
        for s, e in reversed(list(symbol_blocks(text))):
            block = text[s:e]
            ref = re.search(r'\(property "Reference" "([^"]*)"', block).group(1)
            if ref in want:
                assert "(in_bom yes)" in block, (ref, "is not a BOM part")
                seen.add(ref)
                text = text[:s] + edit_block(block, ref, want[ref], changes) + text[e:]
            elif "(in_bom yes)" in block and not ref.startswith("#"):
                missed.add(ref)
        out[path] = text
    assert seen == set(want), sorted(set(want) - seen)
    assert not missed, ("BOM parts with no line in the table", sorted(missed))
    for ref, name, old, new in sorted(changes):
        print(f"{ref:5} {name:13} {old!r} -> {new!r}")
    print(f"{len(changes)} field changes on {len({c[0] for c in changes})} parts; {len(want)} parts in the table")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(
            json.dumps(sorted(changes), indent=1, ensure_ascii=False), encoding="utf-8")
    if "--write" in sys.argv:
        for path, text in out.items():
            if text != path.read_text(encoding="utf-8"):
                path.write_text(text, encoding="utf-8")
                print("wrote", path.name)


if __name__ == "__main__":
    main()
