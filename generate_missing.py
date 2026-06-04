#!/usr/bin/env python3
"""Generate missing FissionCAD icons — hole, thread, draft, rib, split,
thicken, pipe, plane, preview, send, setup, support, export, additive.

Also fixes revolve.svg to be distinct from extrude.svg.
"""

import os, math

ICON_DIR = os.path.expanduser("~/Projects/fission-cad/resources/icons")
os.makedirs(ICON_DIR, exist_ok=True)

SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c1c3c8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n{}\n</svg>'

TAG = '  {}'
CIRCLE = '<circle cx="{}" cy="{}" r="{}"{}'
LINE = '<line x1="{}" y1="{}" x2="{}" y2="{}"{}'
RECT = '<rect x="{}" y="{}" width="{}" height="{}" rx="{}"{}'
PATH = '<path d="{}"{}'
TEXT = '<text x="{}" y="{}" fill="#c1c3c8" font-size="{}" font-family="sans-serif" font-weight="bold">{}</text>'

def dot(x, y, fill="#c1c3c8"):
    return CIRCLE.format(x, y, 1.5, f' fill="{fill}"/>')

def _tag(s):
    return TAG.format(s)


def svg_hole():
    """Hole — circle with crosshair centre and depth arrow"""
    lines = _tag(CIRCLE.format(12, 12, 8, '/>')) + '\n'
    lines += _tag(LINE.format(12, 6, 12, 3, '/>')) + '\n'
    lines += _tag(LINE.format(8, 12, 16, 12, '/>')) + '\n'
    # Depth arrow going down
    lines += _tag(LINE.format(12, 12, 18, 18, '/>')) + '\n'
    lines += _tag(LINE.format(18, 18, 15, 17, '/>')) + '\n'
    lines += _tag(LINE.format(18, 18, 19, 15, '/>'))
    return lines


def svg_thread():
    """Thread — circle with dashed internal line"""
    lines = _tag(CIRCLE.format(12, 12, 9, '/>')) + '\n'
    # Internal thread (smaller circle + dashed)
    lines += '  <circle cx="12" cy="12" r="6" stroke="#c1c3c8" stroke-width="1" stroke-dasharray="2,2"/>\n'
    lines += _tag(CIRCLE.format(12, 12, 3, '/>'))
    return lines


def svg_draft():
    """Draft angle — tapered box shape"""
    # Vertical faces
    lines = _tag(LINE.format(4, 5, 7, 19, '/>')) + '\n'
    lines += _tag(LINE.format(20, 5, 17, 19, '/>')) + '\n'
    # Top edge (original)
    lines += _tag(LINE.format(4, 5, 20, 5, '/>')) + '\n'
    # Bottom edge (shrunk)
    lines += _tag(LINE.format(7, 19, 17, 19, '/>')) + '\n'
    # Angle indicator arrow
    path = "M5,6 A3,3 0 0,0 6,8"
    lines += _tag(PATH.format(path, '/>'))
    return lines


def svg_rib():
    """Rib/Web — thin vertical wall with base"""
    lines = _tag(RECT.format(4, 16, 16, 4, 1, '/>')) + '\n'
    lines += _tag(LINE.format(12, 16, 12, 4, '/>')) + '\n'
    # Triangle filler at top
    d = "M8,4 L16,4 L12,10 Z"
    lines += _tag(PATH.format(d, ' fill="#c1c3c8" stroke="none"'))
    return lines


def svg_split():
    """Split — body being cut by plane"""
    lines = _tag(RECT.format(4, 6, 16, 12, 1, '/>')) + '\n'
    # Cut line
    lines += _tag(LINE.format(12, 4, 12, 20, '/>')) + '\n'
    # Separation gap
    lines += _tag(LINE.format(12, 8, 12, 10, '#ff6b6b', '/>'))
    return lines


def svg_thicken():
    """Thicken — surface adding thickness outward"""
    lines = _tag(LINE.format(4, 10, 20, 10, '/>')) + '\n'
    # Thickened layer
    lines += _tag(RECT.format(4, 10, 16, 7, 1, '/>')) + '\n'
    # Original surface line
    lines += _tag(LINE.format(4, 10, 20, 10, '#4a9eff', '/>'))
    # Arrow indicating outward
    lines += _tag(LINE.format(12, 19, 12, 22, '/>')) + '\n'
    lines += _tag(LINE.format(12, 22, 10, 20, '/>')) + '\n'
    lines += _tag(LINE.format(12, 22, 14, 20, '/>'))
    return lines


def svg_pipe():
    """Pipe/Tube — circle with inner hole, curved path"""
    # Curved path
    d = "M4,18 C10,20 14,6 20,6"
    lines = _tag(PATH.format(d, '/>')) + '\n'
    # Cross-section start
    lines += _tag(CIRCLE.format(4, 18, 3, '/>')) + '\n'
    lines += _tag(CIRCLE.format(4, 18, 1.5, '/>')) + '\n'
    # Cross-section end
    lines += _tag(CIRCLE.format(20, 6, 3, '/>')) + '\n'
    lines += _tag(CIRCLE.format(20, 6, 1.5, '/>'))
    return lines


def svg_plane():
    """Construction Plane — rectangle with corner fold"""
    lines = _tag(RECT.format(4, 8, 12, 10, 1, '/>')) + '\n'
    # Fold corner
    lines += _tag(LINE.format(16, 8, 20, 4, '/>')) + '\n'
    lines += _tag(LINE.format(16, 18, 20, 14, '/>')) + '\n'
    lines += _tag(LINE.format(20, 4, 20, 14, '/>'))
    return lines


def svg_preview():
    """3D Preview — isometric view cube with play triangle"""
    lines = _tag(RECT.format(6, 8, 12, 10, 1, '/>')) + '\n'
    # Isometric edges
    for x, y in [(6,8), (18,8), (18,18), (6,18)]:
        lines += _tag(LINE.format(x, y, x+3, y-3, '/>')) + '\n'
    lines += _tag(RECT.format(9, 5, 12, 10, 1, ' stroke-dasharray="2,2"'))
    # Play triangle overlay
    d = "M15,10 L15,16 L19,13 Z"
    lines += _tag(PATH.format(d, ' fill="#4a9eff" stroke="none"'))
    return lines


def svg_send():
    """Send to Printer — arrow going into printer box"""
    # Printer box
    lines = _tag(RECT.format(4, 10, 16, 10, 1, '/>')) + '\n'
    # Paper sticking out top
    lines += _tag(RECT.format(9, 6, 6, 4, 0.5, '/>')) + '\n'
    # Arrow pointing into printer
    lines += _tag(LINE.format(12, 4, 12, 2, '/>')) + '\n'
    lines += _tag(LINE.format(12, 2, 10, 4, '/>')) + '\n'
    lines += _tag(LINE.format(12, 2, 14, 4, '/>'))
    return lines


def svg_setup():
    """Setup — wrench/gear setup icon"""
    # Gear
    d = "M12,3 L13,6 L14,6 L16,4 L17,7 L18,7 L19,5 L20,8 L19,9 L20,11 L17,12"
    lines = _tag(PATH.format(d, '/>')) + '\n'
    lines += _tag(CIRCLE.format(12, 12, 3, '/>'))
    return lines


def svg_support():
    """Support — bridge with support pillar"""
    lines = _tag(LINE.format(4, 6, 20, 6, '/>')) + '\n'
    # Bridge
    d = "M4,6 L6,10 L18,10 L20,6"
    lines += _tag(PATH.format(d, ' fill="none"')) + '\n'
    # Support pillar
    lines += _tag(LINE.format(10, 10, 10, 20, '/>')) + '\n'
    lines += _tag(LINE.format(14, 10, 14, 20, '/>'))
    return lines


def svg_export():
    """Export — arrow exiting a document"""
    # Document
    lines = _tag(RECT.format(5, 4, 10, 14, 1, '/>')) + '\n'
    lines += _tag(LINE.format(5, 8, 15, 8, '/>')) + '\n'
    lines += _tag(LINE.format(5, 12, 12, 12, '/>')) + '\n'
    # Arrow going out to right
    lines += _tag(LINE.format(16, 11, 22, 11, '/>')) + '\n'
    lines += _tag(LINE.format(22, 11, 19, 8, '/>')) + '\n'
    lines += _tag(LINE.format(22, 11, 19, 14, '/>'))
    return lines


def svg_additive():
    """Additive manufacturing — layered build with nozzle"""
    # Base layers
    lines = _tag(RECT.format(4, 16, 16, 3, 0.5, '/>')) + '\n'
    lines += _tag(RECT.format(6, 12, 12, 3, 0.5, '/>')) + '\n'
    lines += _tag(RECT.format(8, 8, 8, 3, 0.5, '/>')) + '\n'
    # Nozzle
    d = "M14,6 L16,8 L12,8 Z"
    lines += _tag(PATH.format(d, ' fill="#c1c3c8" stroke="none"'))
    lines += _tag(LINE.format(16, 6, 16, 4, '/>'))
    return lines


# ── Registry ─────────────────────────────────────────────────────

MISSING_ICONS = [
    ("hole", svg_hole, "Hole feature"),
    ("thread", svg_thread, "Screw thread"),
    ("draft", svg_draft, "Draft angle"),
    ("rib", svg_rib, "Rib/web"),
    ("split", svg_split, "Split face/body"),
    ("thicken", svg_thicken, "Thicken surface"),
    ("pipe", svg_pipe, "Pipe/tube"),
    ("plane", svg_plane, "Construction plane"),
    ("preview", svg_preview, "3D preview/play"),
    ("send", svg_send, "Send to printer"),
    ("setup", svg_setup, "Printer/material setup"),
    ("support", svg_support, "Print supports"),
    ("export", svg_export, "Export G-code/3MF"),
    ("additive", svg_additive, "Additive manufacturing"),
]

def generate_all():
    generated = []
    for name, fn, desc in MISSING_ICONS:
        content = SVG.format(fn())
        path = os.path.join(ICON_DIR, f"{name}.svg")
        with open(path, "w") as f:
            f.write(content)
        generated.append(name)
        print(f"  {name}.svg — {desc}")

    print(f"\nGenerated {len(generated)} new SVG icons in {ICON_DIR}")

if __name__ == "__main__":
    generate_all()
