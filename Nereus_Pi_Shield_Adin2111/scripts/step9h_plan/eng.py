"""Obstacle model for the step 9h planner: pads, part bodies and silkscreen as boxes, from dump.py's json."""
import json, math
X0, Y0, X1, Y1 = 116.30, 76.10, 181.30, 132.10
class Eng:
    def __init__(s, path):
        s.d = json.load(open(path)); s.hard = {"T": [], "B": []}; s.vias = s.d["vias"]; s.body = {}
        for f in s.d["fps"]:
            for side in "TB":
                ps = [p for p in f["pads"] if f["side"] == side or p[4]]
                for p in ps: s.hard[side].append((p[0], p[1], p[2], p[3], "pad " + f["ref"]))
            own = [p for p in f["pads"]] + [k["bb"] for k in f["silk"] if k["cls"] != "PCB_TEXT" and k["side"] == f["side"]]
            if f["cy"]: own.append(f["cy"])
            if own:
                bb = (min(p[0] for p in own), min(p[1] for p in own), max(p[2] for p in own), max(p[3] for p in own))
                s.body[f["ref"]] = (f["side"], bb)
                s.hard[f["side"]].append(bb + ("body " + f["ref"],))
        for k in s.d["silk"]:
            s.hard[k["side"]].append(tuple(k["bb"]) + ("silk",))
    def add(s, side, bb, tag): s.hard[side].append(tuple(bb) + (tag,))
    def hits(s, side, bb, gap=0.15, skip=()):
        out = []
        for o in s.hard[side]:
            if o[4] in skip: continue
            if bb[0] - gap < o[2] and bb[2] + gap > o[0] and bb[1] - gap < o[3] and bb[3] + gap > o[1]: out.append(o)
        if bb[0] < X0 + 0.5 or bb[2] > X1 - 0.5 or bb[1] < Y0 + 0.5 or bb[3] > Y1 - 0.5: out.append((0, 0, 0, 0, "edge"))
        return out
    def nvias(s, bb, gap=0.05):
        return sum(1 for v in s.vias if bb[0] - gap - v[2] / 2 < v[0] < bb[2] + gap + v[2] / 2 and bb[1] - gap - v[2] / 2 < v[1] < bb[3] + gap + v[2] / 2)
    def pad_gap(s, side, bb):
        m = 99
        for o in s.hard[side]:
            dx = max(o[0] - bb[2], bb[0] - o[2], 0); dy = max(o[1] - bb[3], bb[1] - o[3], 0); m = min(m, math.hypot(dx, dy))
        m = min(m, bb[0] - X0, X1 - bb[2], bb[1] - Y0, Y1 - bb[3]); return m
