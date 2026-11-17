"""Stage 17: tiny text-level helpers for KiCad 10 schematic files (standard library only).

items(text) -> list of (start, end, kind, block) for the root's direct children; the block text is kept byte for byte.
"""
import re


def _close(text, i):
    """index just past the ')' that closes the '(' at i (strings with escapes respected)."""
    depth = 0; j = i; n = len(text)
    while j < n:
        c = text[j]
        if c == '"':
            j += 1
            while text[j] != '"':
                j += 2 if text[j] == '\\' else 1
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError('unbalanced from %d' % i)


def items(text):
    out = []
    for m in re.finditer(r'\n\t\((\w+)', text):
        s = m.start() + 2
        if out and s < out[-1][1]:
            continue
        e = _close(text, s)
        out.append((s, e, m.group(1), text[s:e]))
    return out


def at(block):
    m = re.search(r'\(at ([-\d.]+) ([-\d.]+)', block)
    return (float(m.group(1)), float(m.group(2))) if m else None


def pts(block):
    return [(float(a), float(b)) for a, b in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', block)]


def ref(block):
    m = re.search(r'\(property "Reference" "([^"]*)"', block)
    return m.group(1) if m else None


def label_name(block):
    m = re.match(r'\((?:label|hierarchical_label|global_label|text|text_box) "((?:[^"\\]|\\.)*)"', block)
    return m.group(1) if m else None


def shift(block, dx, dy):
    """move every (at x y ...) and (xy x y) in the block by dx, dy (also start/end of rectangles)."""
    f = lambda v, d: ('%.4f' % (float(v) + d)).rstrip('0').rstrip('.')
    block = re.sub(r'\(at ([-\d.]+) ([-\d.]+)', lambda m: '(at %s %s' % (f(m.group(1), dx), f(m.group(2), dy)), block)
    block = re.sub(r'\(xy ([-\d.]+) ([-\d.]+)\)', lambda m: '(xy %s %s)' % (f(m.group(1), dx), f(m.group(2), dy)), block)
    block = re.sub(r'\((start|end) ([-\d.]+) ([-\d.]+)\)', lambda m: '(%s %s %s)' % (m.group(1), f(m.group(2), dx), f(m.group(3), dy)), block)
    return block
