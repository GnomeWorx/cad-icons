#!/usr/bin/env python3
"""Generate FissionCAD-compatible SVG icons from the icon browser icons.

Each icon: 24×24 viewBox, stroke="#c1c3c8" stroke-width="1.5", round caps/joins.
Output: ~/Projects/fission-cad/resources/icons/<name>.svg
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
POLY = '<polygon points="{}"{}'
ELLIPSE = '<ellipse cx="{}" cy="{}" rx="{}" ry="{}"{}'
TEXT = '<text x="{}" y="{}" fill="#c1c3c8" font-size="{}" font-family="sans-serif" font-weight="bold">{}</text>'

def dot(x, y, fill="#c1c3c8"):
    return CIRCLE.format(x, y, 1.5, f' fill="{fill}"/>')

def hollow_dot(x, y):
    return CIRCLE.format(x, y, 1.5, '/>')

def closed(points):
    return POLY.format(' '.join(f'{x},{y}' for x,y in points), '/>')


# ── SELECT & TRANSFORM ───────────────────────────────────────────

def svg_select():
    """Select — arrow pointer"""
    d = "M6,4 L6,20 L10,16 L14,20 L16,18 L12,14 L18,14 Z"
    return TAG.format(PATH.format(d, '/>'))

def svg_move():
    """Move — 4-direction arrows from centre"""
    lines = ""
    for dx, dy in [(0,-8), (8,0), (0,8), (-8,0)]:
        cx, cy = 12, 12
        ex, ey = cx+dx, cy+dy
        lines += TAG.format(LINE.format(cx, cy, ex, ey, '/>')) + '\n'
        # arrowhead
        a = math.atan2(dy, dx)
        for s in (-1, 1):
            ax = ex + s*3*math.cos(a+2.5)
            ay = ey + s*3*math.sin(a+2.5)
            lines += TAG.format(LINE.format(ex, ey, ax, ay, '/>')) + '\n'
    lines += TAG.format(dot(12, 12, "#4a9eff"))
    return lines

def svg_rotate():
    """Rotate — circular arrow"""
    d = "M19,7 A10,10 0 1,1 9,17"
    arrow = '<path d="M9,17 L6,14 L10,15 Z" fill="#c1c3c8" stroke="none"/>'
    return TAG.format(PATH.format(d, '/>')) + '\n' + TAG.format(arrow)

def svg_scale():
    """Scale — diagonal double-headed arrow"""
    lines = TAG.format(LINE.format(5, 19, 19, 5, '/>')) + '\n'
    # top-right arrow
    lines += TAG.format(LINE.format(19,5, 15,4, '/>')) + '\n'
    lines += TAG.format(LINE.format(19,5, 20,9, '/>')) + '\n'
    # bottom-left arrow
    lines += TAG.format(LINE.format(5,19, 9,20, '/>')) + '\n'
    lines += TAG.format(LINE.format(5,19, 4,15, '/>')) + '\n'
    lines += TAG.format(dot(12, 12, "#4a9eff"))
    return lines

def svg_pan():
    """Pan — hand tool"""
    d = "M10,19 C7,19 5,16 5,13 L5,9 L7,9 L7,14 L7,7 L9,7 L9,13 L9,5 L11,5 L11,12 L11,6 L13,6 L13,12 L13,7 L15,7 L15,12 C16,12 18,13 18,16 C18,19 14,19 10,19 Z"
    return TAG.format(PATH.format(d, '/>'))


# ── SKETCH TOOLS ─────────────────────────────────────────────────

def svg_line():
    return TAG.format(LINE.format(4, 20, 20, 4, '/>')) + '\n' + TAG.format(dot(4,20)) + '\n' + TAG.format(dot(20,4))

def svg_rectangle():
    lines = TAG.format(RECT.format(4, 5, 16, 14, 1, '/>')) + '\n'
    lines += TAG.format(dot(4, 5)) + '\n' + TAG.format(dot(20, 19))
    return lines

def svg_circle():
    return TAG.format(CIRCLE.format(12, 12, 9, '/>'))

def svg_arc():
    d = "M7,18 A9,9 0 0,1 17,6"
    lines = TAG.format(PATH.format(d, '/>')) + '\n'
    lines += TAG.format(dot(7, 18)) + '\n' + TAG.format(dot(17, 6))
    return lines

def svg_polyline():
    pts = [(5,18), (10,15), (7,8), (13,5), (19,10)]
    d = ' '.join(f'L{x},{y}' if i else f'M{x},{y}' for i,(x,y) in enumerate(pts))
    lines = TAG.format(PATH.format(d, '/>')) + '\n'
    for x,y in pts:
        lines += TAG.format(dot(x,y)) + '\n'
    return lines

def svg_spline():
    d = "M4,18 C8,20 9,4 13,5 C17,6 18,17 20,15"
    lines = TAG.format(PATH.format(d, '/>')) + '\n'
    for pt in [(4,18), (13,5), (20,15)]:
        lines += TAG.format(dot(*pt)) + '\n'
    return lines

def svg_point():
    lines = TAG.format(LINE.format(5,12, 19,12, '/>')) + '\n'
    lines += TAG.format(LINE.format(12,5, 12,19, '/>')) + '\n'
    lines += TAG.format(dot(12, 12, "#4a9eff"))
    return lines

def svg_slot():
    """Slot — rounded pill"""
    r = 4
    x, y, w, h = 4, 8, 16, 8
    d = f"M{x+r},{y} L{x+w-r},{y} A{r},{r} 0 0,1 {x+w},{y+r} L{x+w},{y+h-r} A{r},{r} 0 0,1 {x+w-r},{y+h} L{x+r},{y+h} A{r},{r} 0 0,1 {x},{y+h-r} L{x},{y+r} A{r},{r} 0 0,1 {x+r},{y} Z"
    return TAG.format(PATH.format(d, '/>'))

def svg_polygon():
    """Hexagon"""
    cx, cy = 12, 12
    r = 8
    pts = [(cx + r*math.cos(a*math.pi/3 - math.pi/2), cy + r*math.sin(a*math.pi/3 - math.pi/2)) for a in range(6)]
    return TAG.format(POLY.format(' '.join(f'{x:.0f},{y:.0f}' for x,y in pts), '/>'))

def svg_ellipse():
    return TAG.format(ELLIPSE.format(12, 12, 9, 6, '/>'))


# ── MODIFY TOOLS ─────────────────────────────────────────────────

def svg_trim():
    """Trim — line being cut"""
    lines = TAG.format(LINE.format(4, 9, 16, 9, '/>')) + '\n'
    lines += TAG.format(LINE.format(12, 4, 12, 12, '/>')) + '\n'
    # dashed cut portion
    lines += '  <line x1="12" y1="9" x2="20" y2="9" stroke="#ff6b6b" stroke-width="1.5" stroke-dasharray="2,2"/>'
    lines += '\n' + TAG.format(LINE.format(9, 16, 16, 19, '/>')) + '\n'
    lines += TAG.format(LINE.format(16, 16, 9, 19, '/>'))
    return lines

def svg_extend():
    """Extend — adding to a line"""
    lines = TAG.format(LINE.format(4, 15, 12, 15, '/>')) + '\n'
    lines += TAG.format('<line x1="12" y1="15" x2="20" y2="15" stroke="#4a9eff" stroke-width="1.5"/>')
    lines += '\n' + TAG.format(dot(12, 15, "#4a9eff"))
    return lines

def svg_fillet():
    """Fillet — rounded corner"""
    lines = TAG.format(LINE.format(5, 4, 5, 20, '/>')) + '\n'
    lines += TAG.format(LINE.format(5, 20, 20, 20, '/>')) + '\n'
    d = "M5,12 A8,8 0 0,1 13,20"
    lines += TAG.format('<path d="'+d+'" stroke="#4a9eff" stroke-width="1.5"/>')
    return lines

def svg_chamfer():
    """Chamfer — angled corner"""
    lines = TAG.format(LINE.format(4, 4, 4, 20, '/>')) + '\n'
    lines += TAG.format(LINE.format(4, 20, 20, 20, '/>')) + '\n'
    lines += TAG.format(LINE.format(4, 13, 11, 20, '/>'))
    return lines

def svg_mirror():
    """Mirror — with axis line"""
    lines = '  <line x1="12" y1="3" x2="12" y2="21" stroke="#888" stroke-width="1" stroke-dasharray="3,2"/>\n'
    # Original (left)
    lines += TAG.format(RECT.format(3, 7, 7, 10, 1, '/>')) + '\n'
    # Mirrored (right)
    lines += TAG.format('<rect x="14" y="7" width="7" height="10" rx="1" stroke="#4efc7e" stroke-width="1.5"/>')
    return lines

def svg_offset():
    """Offset — parallel curves"""
    lines = TAG.format(PATH.format("M4,18 C8,18 12,5 16,5", '/>')) + '\n'
    lines += TAG.format('<path d="M7,20 C11,20 15,8 19,8" stroke="#4a9eff" stroke-width="1.5"/>')
    return lines

def svg_pattern():
    """Pattern/Array — 3×3 grid of small circles"""
    lines = ""
    for row in range(3):
        for col in range(3):
            cx, cy = 5 + col*7, 5 + row*7
            color = "#4a9eff" if row+col == 1 else "#c1c3c8"
            lines += TAG.format(CIRCLE.format(cx, cy, 2.5, f' stroke="{color}" stroke-width="1.2"')) + '\n'
    return lines


# ── 3D OPERATIONS ────────────────────────────────────────────────

def svg_extrude():
    """Extrude — 2D square to 3D"""
    lines = TAG.format(RECT.format(5, 8, 11, 9, 1, '/>')) + '\n'
    # Extrusion edges
    for dx, dy in [(5,8), (16,8), (16,17), (5,17)]:
        lines += TAG.format(LINE.format(dx, dy, dx+4, dy-4, '/>')) + '\n'
    # Back face
    lines += '  <rect x="9" y="4" width="11" height="9" rx="1" stroke="#c1c3c8" stroke-width="1" stroke-dasharray="2,2"/>'
    return lines

def svg_revolve():
    """Revolve — rectangle rotated → donut"""
    lines = '  <line x1="5" y1="4" x2="5" y2="20" stroke="#888" stroke-width="1" stroke-dasharray="3,2"/>\n'
    lines += TAG.format(RECT.format(7, 7, 5, 7, 1, '/>')) + '\n'
    d = "M7,10 A6,6 0 0,1 7,18"
    lines += TAG.format('<path d="'+d+'" stroke="#4efc7e" stroke-width="1.5"/>')
    return lines

def svg_loft():
    """Loft — top and bottom ellipses"""
    lines = TAG.format(ELLIPSE.format(12, 6, 7, 3, '/>')) + '\n'
    lines += TAG.format(ELLIPSE.format(12, 18, 5, 2, '/>')) + '\n'
    # Loft lines
    for x in [5, 19]:
        lines += TAG.format(LINE.format(x, 6, x+2, 18, '/>')) + '\n'
    lines += TAG.format(LINE.format(5, 6, 7, 18, '/>')) + '\n'
    lines += TAG.format(LINE.format(19, 6, 17, 18, '/>'))
    return lines

def svg_sweep():
    """Sweep — circle along curved path"""
    lines = TAG.format(PATH.format("M4,19 C12,19 12,5 19,5", '/>')) + '\n'
    lines += TAG.format(CIRCLE.format(3, 18, 3, '/>')) + '\n'
    lines += TAG.format('<circle cx="18" cy="4" r="3" stroke="#4efc7e" stroke-width="1.5"/>')
    return lines

def svg_shell():
    """Shell — hollow box with cutout"""
    lines = TAG.format(RECT.format(4, 6, 16, 13, 1, '/>')) + '\n'
    lines += '  <rect x="8" y="10" width="10" height="7" rx="1" stroke="#c1c3c8" stroke-width="1" stroke-dasharray="2,2"/>\n'
    lines += TAG.format(LINE.format(4, 6, 8, 10, '/>')) + '\n'
    lines += TAG.format(LINE.format(20, 6, 18, 10, '/>'))
    return lines

def svg_union():
    """Boolean Union — overlapping circles"""
    lines = TAG.format(CIRCLE.format(8, 10, 7, '/>')) + '\n'
    lines += TAG.format(CIRCLE.format(16, 14, 7, '/>'))
    return lines

def svg_subtract():
    """Boolean Subtract — rect minus circle"""
    lines = TAG.format(RECT.format(4, 7, 12, 13, 1, '/>')) + '\n'
    lines += TAG.format(CIRCLE.format(14, 12, 7, '/>'))
    return lines

def svg_intersect():
    """Boolean Intersection"""
    lines = TAG.format(CIRCLE.format(8, 9, 7, '/>')) + '\n'
    lines += TAG.format(CIRCLE.format(16, 15, 7, '/>'))
    return lines


# ── DRAFTING ─────────────────────────────────────────────────────

def svg_dimension():
    """Dimension line"""
    lines = TAG.format(LINE.format(7, 5, 7, 19, '/>')) + '\n'
    lines += TAG.format(LINE.format(17, 5, 17, 19, '/>')) + '\n'
    lines += TAG.format(LINE.format(7, 16, 17, 16, '/>')) + '\n'
    # Arrowheads
    lines += TAG.format(LINE.format(7, 16, 9, 14, '/>')) + '\n'
    lines += TAG.format(LINE.format(7, 16, 9, 18, '/>')) + '\n'
    lines += TAG.format(LINE.format(17, 16, 15, 14, '/>')) + '\n'
    lines += TAG.format(LINE.format(17, 16, 15, 18, '/>'))
    return lines

def svg_text():
    return TAG.format(TEXT.format(5, 18, 16, "T"))

def svg_constrain():
    """Constraint — parallel lines with = marker"""
    lines = TAG.format(LINE.format(4, 7, 19, 10, '/>')) + '\n'
    lines += TAG.format(LINE.format(4, 16, 19, 19, '/>')) + '\n'
    lines += TAG.format(LINE.format(4, 11, 6, 11, '/>')) + '\n'
    lines += TAG.format(LINE.format(4, 13, 6, 13, '/>'))
    return lines

def svg_snap():
    """Snap/Grid"""
    lines = ""
    for x in range(5):
        for y in range(4):
            px, py = 3 + x*4, 4 + y*4
            c = "#4a9eff" if (x==2 and y==1) else "#555"
            lines += TAG.format(CIRCLE.format(px, py, 0.5, f' stroke="{c}" stroke-width="1" fill="{c}"')) + '\n'
    # Crosshair over active point
    cx, cy = 11, 8
    lines += TAG.format(LINE.format(cx, cy-3, cx, cy+3, '#4a9eff', '/>')) + '\n'
    lines += TAG.format(LINE.format(cx-3, cy, cx+3, cy, '#4a9eff', '/>'))
    return lines.replace("stroke-width=\"1.5\"", "stroke-width=\"1.2\"")

def svg_section():
    """Section line A-A"""
    lines = TAG.format(LINE.format(3, 11, 21, 11, '/>')) + '\n'
    for x in [3, 21]:
        lines += TAG.format(LINE.format(x, 11, x+2, 8, '/>')) + '\n'
        lines += TAG.format(LINE.format(x, 11, x+2, 14, '/>')) + '\n'
    lines += TAG.format(TEXT.format(6, 8, 9, "A")) + '\n'
    lines += TAG.format(TEXT.format(16, 8, 9, "A"))
    return lines

def svg_zoom():
    """Zoom/fit — magnifier"""
    lines = TAG.format(CIRCLE.format(8, 8, 6, '/>')) + '\n'
    lines += TAG.format(LINE.format(12, 12, 20, 20, '/>')) + '\n'
    # Crosshair in glass
    lines += TAG.format(LINE.format(8, 5, 8, 11, '/>')) + '\n'
    lines += TAG.format(LINE.format(5, 8, 11, 8, '/>'))
    return lines


# ── ICON REGISTRY ────────────────────────────────────────────────

ICONS = [
    # (filename, generator_function)
    # Existing — keep as-is (skipped)
    # New icons to generate:
    ("move", svg_move),
    ("rotate", svg_rotate),
    ("scale", svg_scale),
    ("pan", svg_pan),
    ("polyline", svg_polyline),
    ("spline", svg_spline),
    ("point", svg_point),
    ("slot", svg_slot),
    ("polygon", svg_polygon),
    ("ellipse", svg_ellipse),
    ("trim", svg_trim),
    ("extend", svg_extend),
    ("fillet", svg_fillet),
    ("chamfer", svg_chamfer),
    ("mirror", svg_mirror),
    ("offset", svg_offset),
    ("pattern", svg_pattern),
    ("extrude", svg_extrude),
    ("revolve", svg_revolve),
    ("loft", svg_loft),
    ("sweep", svg_sweep),
    ("shell", svg_shell),
    ("union", svg_union),
    ("subtract", svg_subtract),
    ("intersect", svg_intersect),
    ("dimension", svg_dimension),
    ("text", svg_text),
    ("constraint", svg_constrain),
    ("snap", svg_snap),
    ("section", svg_section),
    ("zoom", svg_zoom),
]

def generate_all():
    generated = []
    for name, fn in ICONS:
        content = SVG.format(fn())
        path = os.path.join(ICON_DIR, f"{name}.svg")
        with open(path, "w") as f:
            f.write(content)
        generated.append(name)

    # Also generate the existing icons that are style-matched versions
    print(f"Generated {len(generated)} SVG icons in {ICON_DIR}:")
    for name in sorted(generated):
        print(f"  {name}.svg")

if __name__ == "__main__":
    generate_all()
