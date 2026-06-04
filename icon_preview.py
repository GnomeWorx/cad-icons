#!/usr/bin/env python3
"""CAD Icon Browser — generate and preview tool icons for a CAD program."""

import sys, json, os, math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QScrollArea,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QPen, QFont, QPainterPath,
    QPolygonF, QBrush, QTransform, QImage
)

CANVAS = 64
HALF = CANVAS // 2
ICON_SIZE = 72


# ── Drawing helpers ──────────────────────────────────────────────

def _setup(p: QPainter, bg: QColor = QColor("#1e1e2e")):
    p.setRenderHint(QPainter.Antialiasing)
    p.fillRect(0, 0, CANVAS, CANVAS, bg)


def _pen(color="#e0e0e0", width=2.0, cap=Qt.RoundCap):
    return QPen(QColor(color), width, cap=cap)


def _fill(c):
    return QBrush(QColor(c))


def _center(size=1.0):
    return 32 - (size * 8), 32 + (size * 8)


# ── Icon definitions ─────────────────────────────────────────────

ICONS = []

def icon(name, fn):
    ICONS.append({"name": name, "draw": fn})


# ── SELECT & TRANSFORM ───────────────────────────────────────────

def draw_pointer(p):
    """Select arrow cursor"""
    path = QPainterPath()
    path.moveTo(16, 12); path.lineTo(16, 56); path.lineTo(28, 44)
    path.lineTo(36, 56); path.lineTo(42, 52); path.lineTo(34, 40)
    path.lineTo(48, 40); path.closeSubpath()
    p.fillPath(path, _fill("#4a9eff"))
    p.setPen(_pen("#4a9eff", 1.5))
    p.drawPath(path)


def draw_move(p):
    """4-direction move arrows"""
    cx, cy = HALF, HALF
    d = 16
    p.setPen(_pen("#e0e0e0", 2))
    # Arrow lines from centre
    for dx, dy in [(0, -d), (d, 0), (0, d), (-d, 0)]:
        p.drawLine(cx, cy, cx + dx, cy + dy)
        # Arrowheads
        angle = math.atan2(dy, dx)
        for sign in (-1, 1):
            ax = cx + dx + sign * 6 * math.cos(angle + 2.5)
            ay = cy + dy + sign * 6 * math.sin(angle + 2.5)
            p.drawLine(cx + dx, cy + dy, int(ax), int(ay))
    # Centre dot
    p.setBrush(_fill("#4a9eff"))
    p.drawEllipse(cx - 3, cy - 3, 6, 6)


def draw_rotate(p):
    """Rotate — circular arrow"""
    cx, cy = HALF, HALF
    r = 20
    path = QPainterPath()
    path.arcMoveTo(cx - r, cy - r, r * 2, r * 2, 90)
    path.arcTo(cx - r, cy - r, r * 2, r * 2, 90, -300)
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawPath(path)
    # Arrowhead at end
    angle = -210 * math.pi / 180
    ex = cx + r * math.cos(angle)
    ey = cy + r * math.sin(angle)
    for sign in (-1, 1):
        a = angle + sign * 2.6
        p.drawLine(int(ex), int(ey), int(ex + 8 * math.cos(a)), int(ey + 8 * math.sin(a)))


def draw_scale(p):
    """Scale — diagonal double-headed arrow"""
    p.setPen(_pen("#e0e0e0", 2.5))
    # Diagonal line
    p.drawLine(14, 50, 50, 14)
    # Arrowheads both ends
    for sx, sy in [(1, -1), (-1, 1)]:
        ox, oy = (50 if sx > 0 else 14), (14 if sy < 0 else 50)
        for sign in (-1, 1):
            px = ox + sign * 7 * sx
            py = oy + sign * 7 * sy
            p.drawLine(ox, oy, px + 4 * sy, py + 4 * sx)
    # Small box at centre
    p.setBrush(_fill("#4a9eff"))
    p.drawRect(HALF - 4, HALF - 4, 8, 8)


def draw_pan(p):
    """Pan — hand tool"""
    _setup(p)
    p.setPen(_pen("#e0e0e0", 2))
    # Palm shape
    path = QPainterPath()
    path.moveTo(28, 50)
    path.cubicTo(20, 50, 16, 42, 16, 34)
    path.lineTo(16, 26); path.lineTo(22, 26); path.lineTo(22, 38)
    path.lineTo(22, 20); path.lineTo(28, 20); path.lineTo(28, 36)
    path.lineTo(28, 14); path.lineTo(34, 14); path.lineTo(34, 34)
    path.lineTo(34, 18); path.lineTo(40, 18); path.lineTo(40, 34)
    path.cubicTo(42, 36, 44, 38, 44, 42)
    path.cubicTo(44, 48, 38, 50, 28, 50)
    p.drawPath(path)


icon("Select", draw_pointer)
icon("Move", draw_move)
icon("Rotate", draw_rotate)
icon("Scale", draw_scale)
icon("Pan", draw_pan)

# ── SKETCH TOOLS ─────────────────────────────────────────────────

def draw_line(p):
    p.setPen(_pen("#4a9eff", 3))
    p.drawLine(12, 52, 52, 12)


def draw_rectangle(p):
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawRect(12, 16, 40, 32)


def draw_circle(p):
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawEllipse(12, 12, 40, 40)


def draw_arc(p):
    path = QPainterPath()
    path.arcMoveTo(10, 10, 44, 44, 180)
    path.arcTo(10, 10, 44, 44, 180, -220)
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawPath(path)
    # Endpoint dots
    p.setBrush(_fill("#4a9eff"))
    for angle in [180, -40]:
        a = angle * math.pi / 180
        x = 32 + 22 * math.cos(a)
        y = 32 + 22 * math.sin(a)
        p.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)


def draw_polyline(p):
    pts = [(14, 48), (28, 40), (20, 22), (36, 14), (50, 26)]
    p.setPen(_pen("#4a9eff", 2.5))
    for i in range(len(pts) - 1):
        p.drawLine(*pts[i], *pts[i + 1])
    # Vertex dots
    p.setBrush(_fill("#4a9eff"))
    for x, y in pts:
        p.drawEllipse(x - 2, y - 2, 4, 4)


def draw_spline(p):
    path = QPainterPath()
    path.moveTo(10, 48)
    path.cubicTo(20, 52, 24, 12, 34, 14)
    path.cubicTo(44, 16, 48, 44, 54, 40)
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawPath(path)
    p.setBrush(_fill("#4a9eff"))
    for pt in [(10, 48), (34, 14), (54, 40)]:
        p.drawEllipse(pt[0] - 2, pt[1] - 2, 4, 4)


def draw_point(p):
    """Point / vertex"""
    p.setPen(_pen("#4a9eff", 2))
    # Crosshair
    p.drawLine(HALF - 14, HALF, HALF + 14, HALF)
    p.drawLine(HALF, HALF - 14, HALF, HALF + 14)
    # Centre dot
    p.setBrush(_fill("#4a9eff"))
    p.drawEllipse(HALF - 3, HALF - 3, 6, 6)


def draw_slot(p):
    """Slot — rounded rectangle (pill)"""
    r = 10
    x, y, w, h = 14, 22, 36, 20
    path = QPainterPath()
    path.moveTo(x + r, y)
    path.lineTo(x + w - r, y)
    path.arcTo(x + w - r * 2, y, r * 2, r * 2, 90, -180)
    path.lineTo(x + r, y + h)
    path.arcTo(x, y, r * 2, r * 2, 270, -180)
    path.closeSubpath()
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawPath(path)


def draw_polygon(p):
    """Regular hexagon"""
    cx, cy = HALF, HALF
    r = 24
    path = QPainterPath()
    for i in range(6):
        a = i * math.pi / 3 - math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        path.lineTo(x, y) if i else path.moveTo(x, y)
    path.closeSubpath()
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawPath(path)


def draw_ellipse(p):
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawEllipse(12, 18, 40, 28)


icon("Line", draw_line)
icon("Rectangle", draw_rectangle)
icon("Circle", draw_circle)
icon("Arc", draw_arc)
icon("Polyline", draw_polyline)
icon("Spline", draw_spline)
icon("Point", draw_point)
icon("Slot", draw_slot)
icon("Polygon", draw_polygon)
icon("Ellipse", draw_ellipse)

# ── MODIFY ───────────────────────────────────────────────────────

def draw_trim(p):
    """Trim — line being cut by scissors-like action"""
    p.setPen(_pen("#e0e0e0", 2))
    p.drawLine(10, 20, 46, 20)  # horizontal line
    p.drawLine(30, 10, 30, 30)  # vertical cut
    p.setPen(_pen("#ff6b6b", 2.5))
    # Scissor X
    p.drawLine(26, 36, 40, 50)
    p.drawLine(40, 36, 26, 50)
    # Dashed portion (removed)
    pen = _pen("#ff6b6b", 1.5, Qt.RoundCap)
    pen.setStyle(Qt.DashLine)
    p.setPen(pen)
    p.drawLine(30, 20, 46, 20)


def draw_extend(p):
    """Extend — adding to a line"""
    p.setPen(_pen("#e0e0e0", 2))
    p.drawLine(10, 40, 30, 40)  # existing line
    p.setPen(_pen("#4a9eff", 3))
    p.drawLine(30, 40, 54, 40)  # extended part
    # Splice dot
    p.setBrush(_fill("#4a9eff"))
    p.drawEllipse(30 - 2, 40 - 2, 4, 4)


def draw_fillet(p):
    """Fillet (rounded corner)"""
    p.setPen(_pen("#e0e0e0", 2))
    p.drawLine(12, 12, 12, 52)  # vertical
    p.drawLine(12, 52, 52, 52)  # horizontal
    # Fillet arc
    pen = _pen("#4a9eff", 3)
    p.setPen(pen)
    r = 20
    path = QPainterPath()
    path.arcMoveTo(12, 32, r * 2, r * 2, 180)
    path.arcTo(12, 32, r * 2, r * 2, 180, -90)
    p.drawPath(path)


def draw_chamfer(p):
    """Chamfer (angled corner)"""
    p.setPen(_pen("#e0e0e0", 2))
    p.drawLine(8, 12, 8, 52)
    p.drawLine(8, 52, 52, 52)
    p.setPen(_pen("#4a9eff", 3))
    p.drawLine(8, 34, 30, 52)


def draw_mirror(p):
    """Mirror — dashed axis line with reflected shape"""
    p.setPen(QPen(QColor("#888888"), 1.5, Qt.DashLine))
    p.drawLine(HALF, 6, HALF, 58)
    # Original (left side)
    p.setPen(_pen("#4a9eff", 2))
    path = QPainterPath()
    path.moveTo(10, 48); path.lineTo(10, 20); path.lineTo(28, 20)
    path.lineTo(28, 48); path.closeSubpath()
    p.drawPath(path)
    # Mirrored (right side)
    p.setPen(_pen("#4efc7e", 2))
    path = QPainterPath()
    path.moveTo(54, 48); path.lineTo(54, 20); path.lineTo(36, 20)
    path.lineTo(36, 48); path.closeSubpath()
    p.drawPath(path)


def draw_offset(p):
    """Offset — parallel curves"""
    path = QPainterPath()
    path.moveTo(10, 48)
    path.cubicTo(20, 48, 30, 14, 40, 14)
    p.setPen(_pen("#e0e0e0", 2))
    p.drawPath(path)
    # Offset curve
    path2 = QPainterPath()
    path2.moveTo(14, 54)
    path2.cubicTo(24, 54, 34, 20, 44, 20)
    p.setPen(_pen("#4a9eff", 2))
    p.drawPath(path2)
    # Offset dimension line
    p.setPen(QPen(QColor("#888888"), 1, Qt.DashLine))
    p.drawLine(20, 14, 24, 20)

def draw_pattern(p):
    """Array / pattern — grid of small circles"""
    for row in range(3):
        for col in range(3):
            x = 14 + col * 16
            y = 12 + row * 16
            p.setPen(_pen("#4a9eff" if row + col == 1 else "#e0e0e0", 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(x, y, 10, 10)


icon("Trim", draw_trim)
icon("Extend", draw_extend)
icon("Fillet", draw_fillet)
icon("Chamfer", draw_chamfer)
icon("Mirror", draw_mirror)
icon("Offset", draw_offset)
icon("Pattern", draw_pattern)

# ── 3D OPERATIONS ────────────────────────────────────────────────

def draw_extrude(p):
    """Extrude — 2D square to 3D box"""
    # Front face
    p.setPen(_pen("#4a9eff", 2))
    p.drawRect(14, 20, 28, 22)
    # Extrusion edges (isometric)
    dx, dy = 8, -8
    for x, y in [(14, 20), (42, 20), (42, 42), (14, 42)]:
        p.drawLine(x, y, x + dx, y + dy)
    # Back face
    p.setPen(QPen(QColor("#4a9eff"), 1.5, Qt.DashLine))
    p.drawRect(14 + dx, 20 + dy, 28, 22)


def draw_revolve(p):
    """Revolve — rectangle spinning to donut"""
    # Axis line
    p.setPen(QPen(QColor("#888888"), 1.5, Qt.DashLine))
    p.drawLine(12, 8, 12, 56)
    # Profile rectangle
    p.setPen(_pen("#4a9eff", 2))
    p.drawRect(16, 20, 14, 18)
    # Revolved outline (half donut)
    p.setPen(_pen("#4efc7e", 2))
    path = QPainterPath()
    path.arcMoveTo(16, 16, 28, 28, -90)
    path.arcTo(16, 16, 28, 28, -90, 180)
    p.drawPath(path)


def draw_loft(p):
    """Loft — two circles → cone shape"""
    p.setPen(_pen("#4a9eff", 2))
    p.drawEllipse(16, 8, 32, 10)  # top ellipse
    p.drawEllipse(20, 40, 24, 8)  # bottom ellipse
    # Loft lines
    for x in [16, 48]:
        p.drawLine(x, 13, x + 4, 40)
    # Tangent lines
    p.setPen(_pen("#4efc7e", 1.5))
    p.drawLine(16, 13, 20, 40)
    p.drawLine(48, 13, 44, 40)


def draw_sweep(p):
    """Sweep — circle along curved path"""
    # Path
    path = QPainterPath()
    path.moveTo(10, 50)
    path.cubicTo(30, 50, 30, 14, 50, 14)
    p.setPen(_pen("#4a9eff", 2))
    p.drawPath(path)
    # Sweep profile (circle at start)
    p.drawEllipse(6, 44, 10, 10)
    # Sweep profile (circle at end)
    p.setPen(_pen("#4efc7e", 2))
    p.drawEllipse(46, 8, 10, 10)


def draw_shell(p):
    """Shell — hollow box with cutout"""
    # Outer box
    p.setPen(_pen("#4a9eff", 2))
    p.drawRect(10, 14, 44, 36)
    # Inner cutout
    pen = _pen("#4efc7e", 2)
    pen.setStyle(Qt.DashLine)
    p.setPen(pen)
    p.drawRect(18, 22, 28, 20)
    # Opening indication
    p.setPen(_pen("#4a9eff", 2))
    p.drawLine(10, 14, 18, 22)
    p.drawLine(54, 14, 46, 22)


def draw_bool_union(p):
    """Boolean Union"""
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawEllipse(12, 14, 28, 28)
    p.drawEllipse(24, 22, 28, 28)
    # Joined fill
    p.setBrush(QColor(74, 158, 255, 40))
    path = QPainterPath()
    path.addEllipse(12, 14, 28, 28)
    path2 = QPainterPath()
    path2.addEllipse(24, 22, 28, 28)
    path = path.united(path2)
    p.drawPath(path)


def draw_bool_subtract(p):
    """Boolean Subtract"""
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawRect(10, 14, 30, 36)   # main body
    # Cut cylinder
    pen = _pen("#ff6b6b", 2.5)
    p.setPen(pen)
    p.drawEllipse(28, 18, 20, 20)
    # Fill to show hole
    p.setBrush(QColor("#1e1e2e"))
    p.setPen(Qt.NoPen)
    path = QPainterPath()
    path.addRect(10, 14, 30, 36)
    cut = QPainterPath()
    cut.addEllipse(28, 18, 20, 20)
    diff = path.subtracted(cut)
    p.drawPath(diff)
    # Redraw outlines
    p.setBrush(Qt.NoBrush)
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawRect(10, 14, 30, 36)
    p.setPen(pen)
    p.drawEllipse(28, 18, 20, 20)


def draw_bool_intersect(p):
    """Boolean Intersection"""
    p.setPen(_pen("#4efc7e", 2.5))
    p.drawEllipse(10, 14, 28, 28)
    p.drawEllipse(26, 22, 28, 28)
    # Fill overlap
    p.setBrush(QColor(78, 252, 126, 60))
    p.setPen(Qt.NoPen)
    path = QPainterPath()
    path.addEllipse(10, 14, 28, 28)
    path2 = QPainterPath()
    path2.addEllipse(26, 22, 28, 28)
    inter = path.intersected(path2)
    p.drawPath(inter)


icon("Extrude", draw_extrude)
icon("Revolve", draw_revolve)
icon("Loft", draw_loft)
icon("Sweep", draw_sweep)
icon("Shell", draw_shell)
icon("Union", draw_bool_union)
icon("Subtract", draw_bool_subtract)
icon("Intersect", draw_bool_intersect)

# ── DRAFTING ─────────────────────────────────────────────────────

def draw_dimension(p):
    """Dimension line"""
    p.setPen(_pen("#e0e0e0", 2))
    p.drawLine(18, 14, 18, 50)  # vertical guide
    p.drawLine(46, 14, 46, 50)
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawLine(18, 42, 46, 42)  # dimension line
    # Arrowheads
    for x in [18, 46]:
        for sign, dy in [(-1, 2), (-1, -2)]:
            p.drawLine(x, 42, x + sign * 6, 42 + dy)
    # Dimension text
    p.setPen(_pen("#4a9eff", 1.5))
    p.setFont(QFont("sans-serif", 8))
    p.drawText(26, 36, "42")


def draw_text_tool(p):
    """Text annotation"""
    p.setPen(_pen("#4a9eff", 2.5))
    p.setFont(QFont("sans-serif", 24, QFont.Bold))
    p.drawText(12, 50, "T")


def draw_constraint(p):
    """Constraint — parallel lines symbol"""
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawLine(14, 18, 50, 26)
    p.drawLine(14, 40, 50, 48)
    # Constraint marker (small =)
    p.drawLine(12, 28, 16, 28)
    p.drawLine(12, 32, 16, 32)


def draw_grid_snap(p):
    """Grid / snap"""
    for x in range(1, 6):
        for y in range(1, 5):
            px = 6 + x * 10
            py = 8 + y * 10
            p.setPen(_pen("#4a9eff" if (x == 3 and y == 2) else "#555", 1))
            p.drawPoint(px, py)
    # Highlight active snap point
    p.setPen(_pen("#4a9eff", 2))
    p.setBrush(QColor(74, 158, 255, 30))
    p.drawEllipse(36, 28, 14, 14)
    # Crosshair
    p.setPen(_pen("#4a9eff", 2))
    p.drawLine(36, 24, 36, 20)
    p.drawLine(36, 38, 36, 42)
    p.drawLine(32, 34, 28, 34)
    p.drawLine(40, 34, 44, 34)


def draw_section(p):
    """Section view / cut plane"""
    # Cutting line
    p.setPen(_pen("#e0e0e0", 2.5))
    p.drawLine(8, 28, 56, 28)
    # Arrowheads
    for x in [8, 56]:
        for sign in [-1, 1]:
            p.drawLine(x, 28, x + sign * 5, 28 - 5)
            p.drawLine(x, 28, x + sign * 5, 28 + 5)
    # Section label A-A
    p.setPen(_pen("#4a9eff", 2))
    p.setFont(QFont("sans-serif", 10, QFont.Bold))
    p.drawText(2, 22, "A")
    p.drawText(48, 22, "A")


def draw_zoom(p):
    """Zoom / fit"""
    p.setPen(_pen("#4a9eff", 2.5))
    p.drawEllipse(14, 14, 24, 24)  # magnifier glass
    # Handle
    pen = QPen(QColor("#4a9eff"), 4, cap=Qt.RoundCap)
    p.setPen(pen)
    p.drawLine(34, 34, 50, 50)
    # Crosshair in glass
    p.setPen(_pen("#e0e0e0", 1, Qt.RoundCap))
    cx, cy = 26, 26
    p.drawLine(cx - 8, cy, cx + 8, cy)
    p.drawLine(cx, cy - 8, cx, cy + 8)


icon("Dimension", draw_dimension)
icon("Text", draw_text_tool)
icon("Constrain", draw_constraint)
icon("Snap/Grid", draw_grid_snap)
icon("Section", draw_section)
icon("Zoom/Fit", draw_zoom)


# ── GUI Application ──────────────────────────────────────────────

class IconGrid(QWidget):
    selected = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAD Icon Browser")
        self.setMinimumSize(900, 700)

        # Dark theme
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #e0e0e0; font-family: sans-serif; }
            QPushButton {
                background: #2d2d44; border: 1px solid #444; border-radius: 6px;
                padding: 8px 20px; color: #e0e0e0; font-size: 13px;
            }
            QPushButton:hover { background: #3a3a55; border-color: #4a9eff; }
            QPushButton#export { background: #005aa0; border-color: #4a9eff; font-weight: bold; }
            QPushButton#export:hover { background: #006ec0; }
            QLabel#info { color: #888; font-size: 12px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("CAD Icon Browser")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4a9eff;")
        hdr.addWidget(title)
        hdr.addStretch()

        self.info = QLabel("Click an icon to select it")
        self.info.setObjectName("info")
        hdr.addWidget(self.info)

        self.export_btn = QPushButton("Export Selected")
        self.export_btn.setObjectName("export")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export)
        hdr.addWidget(self.export_btn)

        layout.addLayout(hdr)

        # Scrollable grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(6)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll, 1)

        # Build icon grid
        cols = 8
        self.icon_widgets = []
        self.selection_index = -1

        for i, ic in enumerate(ICONS):
            w = IconWidget(ic["name"], ic["draw"], i)
            w.clicked.connect(self._on_click)
            self.icon_widgets.append(w)
            self.grid.addWidget(w, i // cols, i % cols)

        # Category labels
        cats = [
            (0, 5, "Select & Transform"),
            (5, 10, "Sketch"),
            (10, 7, "Modify"),
            (17, 8, "3D Operations"),
            (25, 6, "Drafting"),
        ]
        # We can't easily add spanning labels in a grid, skip for now

    def _on_click(self, idx):
        for i, w in enumerate(self.icon_widgets):
            w.set_selected(i == idx)
        self.selection_index = idx
        self.info.setText(f"Selected: {ICONS[idx]['name']}")
        self.export_btn.setEnabled(True)

    def _export(self):
        if self.selection_index < 0:
            return
        ic = ICONS[self.selection_index]
        name = ic["name"].replace("/", "-").replace(" ", "_")
        default = os.path.expanduser(f"~/Desktop/{name}.png")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Icon", default, "PNG (*.png)"
        )
        if not path:
            return
        img = QImage(64, 64, QImage.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        p = QPainter(img)
        _setup(p)
        ic["draw"](p)
        p.end()
        img.save(path)
        QMessageBox.information(self, "Saved", f"Icon saved to:\n{path}")


class IconWidget(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, name, draw_fn, idx):
        super().__init__()
        self.idx = idx
        self.draw_fn = draw_fn
        self.name = name
        self._selected = False

        self.setFixedSize(ICON_SIZE + 4, ICON_SIZE + 24)
        self.setStyleSheet("""
            IconWidget {
                background: #25253a; border: 2px solid transparent; border-radius: 6px;
            }
            IconWidget:hover {
                border-color: #4a9eff66;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        self.pixmap_label = QLabel()
        self.pixmap_label.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.pixmap_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pixmap_label, 0, Qt.AlignCenter)

        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 9px; color: #aaa; background: transparent;")
        layout.addWidget(self.name_label, 0, Qt.AlignCenter)

        self._render()

    def _render(self):
        pix = QPixmap(ICON_SIZE, ICON_SIZE)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate((ICON_SIZE - CANVAS) / 2, (ICON_SIZE - CANVAS) / 2)
        self.draw_fn(p)
        p.end()
        self.pixmap_label.setPixmap(pix)

    def set_selected(self, sel):
        self._selected = sel
        border = "2px solid #4a9eff" if sel else "2px solid transparent"
        self.setStyleSheet(f"""
            IconWidget {{
                background: #25253a; border: {border}; border-radius: 6px;
            }}
            IconWidget:hover {{
                border-color: #4a9eff66;
            }}
        """)
        hl = "#4a9eff" if sel else "#aaa"
        self.name_label.setStyleSheet(f"font-size: 9px; color: {hl}; background: transparent;")

    def mousePressEvent(self, event):
        self.clicked.emit(self.idx)
        super().mousePressEvent(event)


# ── Main ─────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    w = IconGrid()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
