#!/usr/bin/env python3
"""FissionCAD Icon CMS — browse, edit, manage, and deploy CAD tool icons.

Integrates with the FissionCAD project at ~/Projects/fission-cad/.
Reads tool definitions from source files, maps icons to tools,
and lets you edit/generate/export SVG icons for every tool.
"""

import sys, os, math, json, re, subprocess, shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QScrollArea,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox,
    QFrame, QSplitter, QTextEdit, QTabWidget, QGroupBox, QListWidget,
    QListWidgetItem, QComboBox, QLineEdit, QFormLayout, QCheckBox,
    QSpinBox, QColorDialog, QSlider, QSizePolicy, QToolTip,
    QTextBrowser
)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import (
    QPixmap, QPainter, QColor, QPen, QFont, QPainterPath,
    QPolygonF, QBrush, QTransform, QImage, QIcon, QFontDatabase,
    QPalette, QCursor
)

# ── Paths ────────────────────────────────────────────────────────

FC_DIR = os.path.expanduser("~/Projects/fission-cad")
ICON_DIR = os.path.join(FC_DIR, "resources", "icons")
SRC_DIR = os.path.join(FC_DIR, "src")

CANVAS = 64
ICON_GRID_SIZE = 72
PREVIEW_SIZE = 160

# ── Parsed tool definitions from FC source ───────────────────────

def parse_tool_defs():
    """Parse tool definitions from SketchStage.cpp, ModelStage.cpp, PrintStage.cpp
    plus a synthetic Constraints stage (since constraints share a single S_Constraint tool
    in FissionCAD but are tracked individually in the spec)."""
    stages = {}
    for stage_name, src_file in [
        ("Sketch", os.path.join(SRC_DIR, "SketchStage.cpp")),
        ("Model",  os.path.join(SRC_DIR, "ModelStage.cpp")),
        ("Make",  os.path.join(SRC_DIR, "PrintStage.cpp")),
    ]:
        if not os.path.exists(src_file):
            continue
        tools = []
        with open(src_file) as f:
            text = f.read()
        # Find tool def blocks: { ID, Name, iconPath, Shortcut }
        pattern = r'\{\s*(\S+),\s*"([^"]+)",\s*"([^"]+\.svg)",\s*"([^"]*)"\s*\}'
        for match in re.finditer(pattern, text):
            tool_id = match.group(1)
            tool_name = match.group(2)
            icon_path = match.group(3)
            shortcut = match.group(4) if match.group(4) else ""
            # Extract just the filename from the icon path
            icon_file = os.path.basename(icon_path)
            tools.append({
                "id": tool_id,
                "name": tool_name,
                "icon": icon_file,
                "shortcut": shortcut,
            })
        stages[stage_name] = tools

    # ── Synthetic Constraints stage ──
    # Constraints are individual in the spec but map to the generic S_Constraint
    # tool in FissionCAD. Track them here so they appear in Browse/Stage Mapping.
    constraint_tools = [
        ("Coincident",  "coincident.svg"),
        ("Horizontal",  "horizontal.svg"),
        ("Vertical",    "vertical.svg"),
        ("Parallel",    "parallel.svg"),
        ("Perpendicular","perpendicular.svg"),
        ("Tangent",     "tangent.svg"),
        ("Equal",       "equal.svg"),
        ("Concentric",  "concentric.svg"),
        ("Collinear",   "collinear.svg"),
        ("Fix",         "fix.svg"),
        ("Midpoint",    "midpoint.svg"),
        ("Symmetric",   "symmetric.svg"),
        ("Curvature",   "curvature.svg"),
    ]
    stages["Constraints"] = [
        {"id": "-1", "name": name, "icon": icon, "shortcut": ""}
        for name, icon in constraint_tools
    ]

    return stages


# ── SVG generation (reusable from generate_svgs.py) ──────────────

SVG_TEMPLATE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#c1c3c8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n{}\n</svg>'

SVG_TEMPLATE_LIGHT = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\n{}\n</svg>'


def render_svg_to_pixmap(svg_content, size=64, dark=True):
    """Render an SVG string to a QPixmap at the given size."""
    from PyQt5.QtSvg import QSvgRenderer
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    if dark:
        svg_content = svg_content.replace('#c1c3c8', '#e0e0e0').replace('stroke="#888"', 'stroke="#aaa"')
        svg_content = svg_content.replace('#4a9eff', '#4fc3f7').replace('#4efc7e', '#66ff99')
    p = QPainter(pix)
    renderer = QSvgRenderer(bytes(svg_content, 'utf-8'))
    renderer.render(p)
    p.end()
    return pix


# ── CONTENT MANAGEMENT SYSTEM ────────────────────────────────────

class IconCMS(QWidget):

    # ── Theme stylesheets ──────────────────────────────────────────
    DARK_QSS = """
        QWidget { background-color: #1e1e2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 12px; }
        QTabWidget::pane { background: #1a1b1e; border: 1px solid #2a2b30; }
        QTabBar::tab { background: #25262b; border: 1px solid #2a2b30; padding: 8px 16px; margin-right: 2px; }
        QTabBar::tab:selected { background: #1a1b1e; border-bottom: 1px solid #4a9eff; }
        QListWidget { background: #25262b; border: 1px solid #2a2b30; border-radius: 4px; color: #e0e0e0; }
        QListWidget::item { padding: 4px; color: #e0e0e0; }
        QListWidget::item:selected { background: #2a3a55; color: #ffffff; }
        QListWidget::item:alternate { background: #22232e; }
        QTextEdit { background: #1e1e2e; color: #c1c3c8; border: 1px solid #2a2b30; font-family: monospace; font-size: 11px; }
        QGroupBox { border: 1px solid #2a2b30; border-radius: 4px; margin-top: 8px; padding-top: 16px; }
        QGroupBox::title { color: #4a9eff; font-weight: bold; }
        QPushButton { background: #2d2d44; border: 1px solid #444; border-radius: 4px; padding: 6px 14px; color: #e0e0e0; }
        QPushButton:hover { background: #3a3a55; border-color: #4a9eff; }
        QPushButton#primary { background: #005aa0; border-color: #4a9eff; font-weight: bold; }
        QPushButton#primary:hover { background: #006ec0; }
        QComboBox { background: #25262b; border: 1px solid #2a2b30; border-radius: 3px; padding: 3px 8px; color: #e0e0e0; }
        QSpinBox { background: #25262b; border: 1px solid #2a2b30; border-radius: 3px; padding: 2px 6px; color: #e0e0e0; }
        QLineEdit { background: #25262b; border: 1px solid #2a2b30; border-radius: 3px; padding: 3px 8px; color: #e0e0e0; }
        QCheckBox { color: #e0e0e0; }
        QSlider::groove:horizontal { background: #2a2b30; height: 4px; border-radius: 2px; }
        QSlider::handle:horizontal { background: #4a9eff; width: 12px; border-radius: 6px; margin: -4px 0; }
    """

    LIGHT_QSS = """
        QWidget { background-color: #f0f0f0; color: #222; font-family: 'Segoe UI', sans-serif; font-size: 12px; }
        QTabWidget::pane { background: #ffffff; border: 1px solid #ccc; }
        QTabBar::tab { background: #e0e0e0; border: 1px solid #ccc; padding: 8px 16px; margin-right: 2px; }
        QTabBar::tab:selected { background: #ffffff; border-bottom: 1px solid #4a9eff; }
        QListWidget { background: #ffffff; border: 1px solid #ccc; border-radius: 4px; color: #222; }
        QListWidget::item { padding: 4px; color: #222; }
        QListWidget::item:selected { background: #d0e4ff; color: #000; }
        QListWidget::item:alternate { background: #f7f7f7; }
        QTextEdit { background: #ffffff; color: #333; border: 1px solid #ccc; font-family: monospace; font-size: 11px; }
        QGroupBox { border: 1px solid #ccc; border-radius: 4px; margin-top: 8px; padding-top: 16px; }
        QGroupBox::title { color: #005aa0; font-weight: bold; }
        QPushButton { background: #e0e0e0; border: 1px solid #aaa; border-radius: 4px; padding: 6px 14px; color: #222; }
        QPushButton:hover { background: #d0d0d0; border-color: #4a9eff; }
        QPushButton#primary { background: #4a9eff; border-color: #4a9eff; font-weight: bold; color: white; }
        QPushButton#primary:hover { background: #3a8eee; }
        QComboBox { background: #ffffff; border: 1px solid #ccc; border-radius: 3px; padding: 3px 8px; color: #222; }
        QSpinBox { background: #ffffff; border: 1px solid #ccc; border-radius: 3px; padding: 2px 6px; color: #222; }
        QLineEdit { background: #ffffff; border: 1px solid #ccc; border-radius: 3px; padding: 3px 8px; color: #222; }
        QCheckBox { color: #222; }
        QSlider::groove:horizontal { background: #ccc; height: 4px; border-radius: 2px; }
        QSlider::handle:horizontal { background: #4a9eff; width: 12px; border-radius: 6px; margin: -4px 0; }
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FissionCAD Icon CMS")
        self.setMinimumSize(1200, 800)
        self._is_dark = True
        self.setStyleSheet(self.DARK_QSS)

        # Parse tool definitions from FC source
        self.stages = parse_tool_defs()

        # Load all SVG icons from the FC resources
        self.icons = {}  # name -> svg content
        self._load_icons()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(4)

        # ─── Header ───
        hdr = QHBoxLayout()
        title = QLabel("FissionCAD Icon CMS")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4a9eff;")
        hdr.addWidget(title)

        self.status_label = QLabel("42 icons loaded")
        self.status_label.setStyleSheet("color: #6b6e78;")
        hdr.addWidget(self.status_label)
        hdr.addStretch()

        self.dark_btn = QPushButton("Dark" if self._is_dark else "Light")
        self.dark_btn.clicked.connect(self._toggle_theme)
        self.dark_btn.setFixedWidth(60)
        hdr.addWidget(self.dark_btn)

        save_btn = QPushButton("Save All to FC")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save_all)
        hdr.addWidget(save_btn)

        deploy_btn = QPushButton("▶ Deploy to FC")
        deploy_btn.setStyleSheet(
            "QPushButton { background: #2e7d32; color: white; padding: 4px 12px;"
            " border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background: #388e3c; }"
        )
        deploy_btn.clicked.connect(self._deploy_to_fc)
        hdr.addWidget(deploy_btn)

        main_layout.addLayout(hdr)

        # ─── Main content: tabs ───
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)

        # ─── Footer ───
        footer = QHBoxLayout()
        footer.setContentsMargins(4, 0, 4, 2)
        ver_label = QLabel("\u00a9 GnomeWorx 2026  Version 0.1.0")
        ver_label.setStyleSheet("color: #4a4d57; font-size: 11px;")
        footer.addWidget(ver_label)
        footer.addStretch()
        main_layout.addLayout(footer)

        # Tab 1: Browse all icons with stage mapping
        self._build_browse_tab()

        # Tab 2: Stage tool mapping
        self._build_stage_tab()

        # Tab 3: SVG editor
        self._build_editor_tab()

        # Tab 4: Icon generator
        self._build_generator_tab()

        # Tabs 5-7: Spec reference tabs — all three specs as QTextBrowser HTML pages
        self._build_sketch_spec_tab()
        self._build_model_spec_tab()
        self._build_make_spec_tab()

        self._refresh_all()

        # Default to Sketch Spec tab so user sees tools reference first
        self.tabs.setCurrentIndex(4)

    def _load_icons(self):
        """Load all .svg files from FC icon dir"""
        self.icons = {}
        if not os.path.exists(ICON_DIR):
            return
        for f in sorted(os.listdir(ICON_DIR)):
            if f.endswith('.svg') and not f.startswith('.'):
                path = os.path.join(ICON_DIR, f)
                with open(path) as fp:
                    self.icons[f] = fp.read()

    def _get_tool_usage(self):
        """Return dict: icon_file -> [list of (stage, tool_name)]"""
        usage = {}
        for stage_name, tools in self.stages.items():
            for t in tools:
                icon_name = t["icon"]
                usage.setdefault(icon_name, []).append((stage_name, t["name"]))
        return usage

    def _build_browse_tab(self):
        """Tab 1: Browse all icons with usage info"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        # Filter bar
        filt_row = QHBoxLayout()
        filt_row.addWidget(QLabel("Filter:"))
        self.browse_filter = QLineEdit()
        self.browse_filter.setPlaceholderText("Type to filter icons...")
        self.browse_filter.textChanged.connect(self._refresh_browse)
        filt_row.addWidget(self.browse_filter, 1)

        filt_row.addWidget(QLabel("  Stage:"))
        self.browse_stage_filter = QComboBox()
        self.browse_stage_filter.addItems(
            ["All", "Unused"] + sorted(self.stages.keys())
        )
        self.browse_stage_filter.currentTextChanged.connect(self._refresh_browse)
        filt_row.addWidget(self.browse_stage_filter)

        layout.addLayout(filt_row)

        # Icon grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.browse_container = QWidget()
        self.browse_grid = QGridLayout(self.browse_container)
        self.browse_grid.setSpacing(6)
        scroll.setWidget(self.browse_container)
        layout.addWidget(scroll, 1)

        self.tabs.addTab(tab, "Browse")

    def _build_stage_tab(self):
        """Tab 2: Stage-by-stage tool-icon mapping — Scandi minimal"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ── Stage header ──
        hdr = QHBoxLayout()
        hdr.setSpacing(8)

        stage_lbl = QLabel("Stage")
        stage_lbl.setStyleSheet("font-size: 10px; color: #8a9; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;")
        hdr.addWidget(stage_lbl)

        self.stage_combo = QComboBox()
        self.stage_combo.addItems(list(self.stages.keys()))
        self.stage_combo.currentTextChanged.connect(self._refresh_stage)
        self.stage_combo.setFixedWidth(180)
        hdr.addWidget(self.stage_combo)

        hdr.addSpacing(12)

        self.stage_desc = QLabel("")
        self.stage_desc.setStyleSheet("font-size: 11px; color: #556;")
        hdr.addWidget(self.stage_desc)

        hdr.addStretch()
        layout.addLayout(hdr)

        # ── Divider ──
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background: #2e2e4a; max-height: 1px;")
        layout.addWidget(div)

        # ── Toolbar mockup (icon strip) ──
        tb_lbl = QLabel("Toolbar preview")
        tb_lbl.setStyleSheet("font-size: 10px; color: #556; font-weight: 600; letter-spacing: 0.5px;")
        layout.addWidget(tb_lbl)

        self.toolbar_mock = QWidget()
        self.toolbar_mock.setFixedHeight(44)
        self.toolbar_mock.setStyleSheet("background: #1a1a2e; border: 1px solid #2e2e4a; border-radius: 4px;")
        self.toolbar_layout = QHBoxLayout(self.toolbar_mock)
        self.toolbar_layout.setContentsMargins(8, 0, 8, 0)
        self.toolbar_layout.setSpacing(2)
        layout.addWidget(self.toolbar_mock)

        # ── Tool list with custom rows ──
        tool_scroll = QScrollArea()
        tool_scroll.setWidgetResizable(True)
        tool_scroll.setFrameShape(QFrame.NoFrame)
        tool_scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self.tool_container = QWidget()
        self.tool_container.setStyleSheet("background: transparent;")
        self.tool_list_layout = QVBoxLayout(self.tool_container)
        self.tool_list_layout.setContentsMargins(0, 4, 0, 4)
        self.tool_list_layout.setSpacing(2)
        tool_scroll.setWidget(self.tool_container)
        layout.addWidget(tool_scroll, 1)

        # ── Icon assign bar ──
        assign_bar = QFrame()
        assign_bar.setStyleSheet("QFrame { background: #24243d; border: 1px solid #2e2e4a; border-radius: 4px; }")
        assign_layout = QHBoxLayout(assign_bar)
        assign_layout.setContentsMargins(10, 6, 10, 6)
        assign_layout.setSpacing(8)

        assign_lbl = QLabel("Assign icon")
        assign_lbl.setStyleSheet("font-size: 10px; color: #8a9; font-weight: 600; letter-spacing: 0.5px;")
        assign_layout.addWidget(assign_lbl)

        self.icon_picker = QComboBox()
        self.icon_picker.setMinimumWidth(200)
        self.icon_picker.addItems(sorted(self.icons.keys()))
        self.icon_picker.currentTextChanged.connect(self._on_icon_picked)
        assign_layout.addWidget(self.icon_picker, 1)

        self.assign_btn = QPushButton("Save")
        self.assign_btn.setFixedHeight(24)
        self.assign_btn.setStyleSheet(
            "QPushButton { background: #3a9bea; border: none; border-radius: 3px; "
            "padding: 0 14px; color: white; font-size: 10px; font-weight: 600; }"
            "QPushButton:hover { background: #4aabfa; }"
        )
        self.assign_btn.clicked.connect(self._assign_icon)
        assign_layout.addWidget(self.assign_btn)

        layout.addWidget(assign_bar)

        self.tabs.addTab(tab, "Stage Mapping")

    def _build_editor_tab(self):
        """Tab 3: SVG source editor"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Horizontal)

        # Left: icon browser
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel("Select icon:"))
        self.editor_icon_list = QListWidget()
        self.editor_icon_list.itemClicked.connect(self._on_editor_icon_selected)
        left_layout.addWidget(self.editor_icon_list)

        splitter.addWidget(left_panel)

        # Centre: editing area
        centre_panel = QWidget()
        centre_layout = QVBoxLayout(centre_panel)
        centre_layout.setContentsMargins(0, 0, 0, 0)

        # Preview
        preview_row = QHBoxLayout()
        self.editor_preview_64 = QLabel()
        self.editor_preview_64.setFixedSize(80, 80)
        self.editor_preview_64.setAlignment(Qt.AlignCenter)
        self.editor_preview_64.setStyleSheet("background: #141517; border: 1px solid #2a2b30; border-radius: 4px;")
        preview_row.addWidget(self.editor_preview_64)

        self.editor_preview_24 = QLabel()
        self.editor_preview_24.setFixedSize(40, 40)
        self.editor_preview_24.setAlignment(Qt.AlignCenter)
        self.editor_preview_24.setStyleSheet("background: #141517; border: 1px solid #2a2b30; border-radius: 4px;")
        preview_row.addWidget(self.editor_preview_24)

        preview_row.addWidget(QLabel("Toolbar size (20×20):"))
        self.editor_preview_toolbar = QLabel()
        self.editor_preview_toolbar.setFixedSize(32, 32)
        self.editor_preview_toolbar.setAlignment(Qt.AlignCenter)
        self.editor_preview_toolbar.setStyleSheet("background: #141517; border: 1px solid #2a2b30; border-radius: 2px;")
        preview_row.addWidget(self.editor_preview_toolbar)

        self.editor_info = QLabel("")
        self.editor_info.setStyleSheet("color: #888;")
        preview_row.addWidget(self.editor_info)
        preview_row.addStretch()
        centre_layout.addLayout(preview_row)

        # SVG source editor
        centre_layout.addWidget(QLabel("SVG source:"))
        self.svg_editor = QTextEdit()
        self.svg_editor.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.svg_editor.textChanged.connect(self._on_svg_edited)
        centre_layout.addWidget(self.svg_editor, 1)

        edit_btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("Refresh Preview")
        self.preview_btn.clicked.connect(self._on_svg_edited)
        edit_btn_row.addWidget(self.preview_btn)

        self.revert_btn = QPushButton("Revert to Original")
        self.revert_btn.clicked.connect(self._revert_icon)
        edit_btn_row.addWidget(self.revert_btn)

        self.save_btn = QPushButton("Save to FC")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self._save_current_icon)
        edit_btn_row.addWidget(self.save_btn)

        centre_layout.addLayout(edit_btn_row)
        splitter.addWidget(centre_panel)
        splitter.setSizes([200, 600])

        layout.addWidget(splitter, 1)
        self.tabs.addTab(tab, "Editor")

    def _build_generator_tab(self):
        """Tab 4: Generate new icons from templates"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        # Template grid
        layout.addWidget(QLabel("Quick-generate from template:"))
        templates_grid = QGridLayout()
        templates_grid.setSpacing(10)

        templates = [
            ("Line",    "line", "Diagonal line with endpoint dots"),
            ("Rect",    "rect", "Rectangle with corner dots"),
            ("Circle",  "circle", "Circle outline"),
            ("Arc",     "arc", "Arc with endpoint dots"),
            ("Arrow",   "arrow", "Single arrow, any direction"),
            ("Cross",   "cross", "Crosshair + centre dot"),
            ("Gear",    "gear", "Simple gear shape"),
            ("Box 3D",  "box3d", "Isometric 3D box"),
            ("Plus",    "plus", "Plus sign"),
            ("Minus",   "minus", "Minus sign"),
        ]

        for i, (name, template, desc) in enumerate(templates):
            btn = QPushButton(f"{name}\n{desc}")
            btn.setFixedSize(120, 60)
            btn.setStyleSheet("text-align: center; font-size: 10px; padding: 4px;")
            btn.clicked.connect(lambda checked, t=template: self._generate_template(t))
            templates_grid.addWidget(btn, i // 3, i % 3)

        layout.addLayout(templates_grid)

        # Manual SVG construction area
        layout.addWidget(QLabel("Or write SVG manually:"))
        self.gen_svg_input = QTextEdit()
        self.gen_svg_input.setPlaceholderText("Paste or type SVG content for the 24×24 canvas...")
        self.gen_svg_input.setMaximumHeight(120)
        self.gen_svg_input.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        layout.addWidget(self.gen_svg_input)

        # Preview + save
        gen_row = QHBoxLayout()
        self.gen_preview = QLabel()
        self.gen_preview.setFixedSize(80, 80)
        self.gen_preview.setAlignment(Qt.AlignCenter)
        self.gen_preview.setStyleSheet("background: #141517; border: 1px solid #2a2b30; border-radius: 4px;")
        gen_row.addWidget(self.gen_preview)

        gen_row.addWidget(QLabel("Name:"))
        self.gen_name = QLineEdit()
        self.gen_name.setPlaceholderText("icon_name (no .svg)")
        gen_row.addWidget(self.gen_name)

        self.gen_save_btn = QPushButton("Save to FC")
        self.gen_save_btn.setObjectName("primary")
        self.gen_save_btn.clicked.connect(self._save_generated)
        gen_row.addWidget(self.gen_save_btn)
        gen_row.addStretch()
        layout.addLayout(gen_row)

        # Hook up the manual SVG preview timer
        self.gen_svg_input.textChanged.connect(self._preview_generated)

        layout.addStretch()
        self.tabs.addTab(tab, "Generator")

    # ─── Sketch spec tab — data from sketch_tools.txt ───────────────

    SPEC_CATEGORIES = [
        {
            "name": "Sketch Creation & Environment",
            "section": 2,
            "tools": [
                ("Create Sketch", "Creates a new 2D sketch on a selected plane or face", ""),
                ("Finish Sketch", "Exits sketch environment and saves changes", ""),
            ]
        },
        {
            "name": "Create — Basic Geometry",
            "section": 3,
            "tools": [
                ("Line",    "Straight line segments (L)", "line"),
                ("Circle",  "Center-diameter or 2-point (C)", "circle"),
                ("Arc",     "3-point, center-point, or tangent arc (A)", "arc"),
                ("Rectangle", "2-point, 3-point, center, or centered (R)", "rectangle"),
                ("Polygon", "Regular polygon, 3-64 sides", "polygon"),
                ("Ellipse", "Oval shape, major/minor radii", "ellipse"),
                ("Slot",    "Rounded rectangle / oblong hole", "slot"),
                ("Spline",  "Smooth curve through control points", "spline"),
                ("Point",   "Construction reference point", "point"),
            ]
        },
        {
            "name": "Text Tool",
            "section": 3,
            "tools": [
                ("Text", "Text for engraving/embossing — height, font, bold/italic", "text"),
            ]
        },
        {
            "name": "Modify Tools",
            "section": 4,
            "tools": [
                ("Trim",    "Removes lines up to intersection boundaries (T)", "trim"),
                ("Extend",  "Extends line to nearest boundary", "extend"),
                ("Offset",  "Parallel copy at specified distance", "offset"),
                ("Move/Copy", "Translate or rotate geometry (M)", "move"),
                ("Rotate",  "Rotates geometry about a point", "rotate"),
                ("Scale",   "Resizes about a reference point", "scale"),
                ("Fillet",  "Rounds corners with specified radius (F)", "fillet"),
                ("Chamfer", "Bevels corners with specified distances", "chamfer"),
                ("Break",   "Splits geometry into segments at selected points", ""),
            ]
        },
        {
            "name": "Pattern Tools",
            "section": 5,
            "tools": [
                ("Rectangular Pattern", "Array of copies in grid formation (X×Y)", "pattern"),
                ("Circular Pattern",    "Array of copies around a center point", "pattern"),
                ("Mirror",  "Mirrored copy across symmetry line", "mirror"),
            ]
        },
        {
            "name": "Constraints",
            "section": 6,
            "tools": [
                ("Coincident",  "Forces two points to share the same location", "coincident"),
                ("Horizontal",  "Forces line to be exactly horizontal", "horizontal"),
                ("Vertical",    "Forces line to be exactly vertical", "vertical"),
                ("Parallel",    "Forces two lines to run in the same direction", "parallel"),
                ("Perpendicular","Forces two lines to meet at 90°", "perpendicular"),
                ("Tangent",     "Forces curve to touch another smoothly", "tangent"),
                ("Equal",       "Forces lengths or radii to be identical", "equal"),
                ("Concentric",  "Forces circles/arcs to share center", "concentric"),
                ("Collinear",   "Forces lines to lie on the same infinite line", "collinear"),
                ("Fix/Coincident", "Locks entity position", "fix"),
                ("Midpoint",    "Forces point to midpoint of line", "midpoint"),
                ("Symmetric",   "Forces symmetry across centerline", "symmetric"),
                ("Curvature",   "Maintains curvature continuity (G2) between splines", "curvature"),
            ]
        },
        {
            "name": "Dimension Tools",
            "section": 7,
            "tools": [
                ("Distance",  "Linear distance between two points or line length (D)", "dimension"),
                ("Radius",    "Radius of arc or fillet", "dimension"),
                ("Diameter",  "Diameter of circle", "dimension"),
                ("Angle",     "Angle between two lines", "dimension"),
            ]
        },
        {
            "name": "Construction & Reference",
            "section": 8,
            "tools": [
                ("Construction Geometry", "Reference geometry — dashed lines, not a profile (X)", ""),
                ("Centerline", "Axis geometry that participates in profiles", ""),
                ("Project",   "Projects 3D edges/faces onto sketch plane (P)", ""),
                ("Project Cut Edges", "Projects intersection of plane with bodies", ""),
            ]
        },
        {
            "name": "Inspection & Display",
            "section": 9,
            "tools": [
                ("Measure",       "Measures distances between entities", "measure"),
                ("Sketch Palette","Grids, snaps, profile/point display options", ""),
                ("Profile Display","Shows closed profiles with blue highlighting", ""),
                ("Points Display", "Shows all sketch points to identify gaps", ""),
            ]
        },
    ]


    # Map spec tool name → FissionCAD tool ID (from SketchTool enum)
    SPEC_TOOL_TO_ID = {
        "Line":     1, "Rectangle": 2, "Circle": 3,
        "Dimension":4, "Arc": 6, "Fillet": 7,
        "Trim":     8, "Polygon": 13, "Slot": 14,
        "Point":    15, "Text": 16, "Offset": 17,
        "Mirror":   18, "Extend": 21, "Move/Copy": 22,
        "Rotate":   23, "Scale": 24, "Measure": 25,
        "Spline":   11, "Ellipse": 12, "Chamfer": 20,
        "Pattern":  19,
    }.get  # use .get for safe lookup with default None

    # Simple name → tool ID map
    SPEC_NAME_TO_ID = {
        "Line": 1, "Rectangle": 2, "Circle": 3,
        "Arc": 6, "Fillet": 7, "Trim": 8,
        "Polygon": 13, "Slot": 14, "Point": 15,
        "Text": 16, "Offset": 17, "Mirror": 18,
        "Extend": 21, "Move/Copy": 22,
        "Rotate": 23, "Scale": 24, "Measure": 25,
        "Spline": 11, "Ellipse": 12, "Chamfer": 20,
        "Rectangular Pattern": 19, "Circular Pattern": 19,
    }

    def _build_sketch_spec_tab(self):
        """Tab 5: Sketch tools spec as HTML reference with unique ref IDs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        hdr = QHBoxLayout()
        title = QLabel("<b>Sketch Tools Spec</b>  "
                       "<span style='color:#4a4d57;font-size:11px'>sketch_tools.txt</span>")
        title.setStyleSheet("font-size: 16px; color: #c1c3c8;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        viewer = QTextBrowser()
        viewer.setOpenExternalLinks(True)
        viewer.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
            }
        """)
        html_path = os.path.join(os.path.dirname(__file__), "refs", "sketch_spec.html")
        if os.path.exists(html_path):
            with open(html_path) as f:
                viewer.setHtml(f.read())
        else:
            viewer.setPlainText("sketch_spec.html not found in refs/")
        layout.addWidget(viewer, 1)

        self.tabs.addTab(tab, "Sketch Spec")

    def _build_model_spec_tab(self):
        """Tab 6: Model (Plastic) spec as HTML reference"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        hdr = QHBoxLayout()
        title = QLabel("<b>Plastic Model Spec</b>  "
                       "<span style='color:#4a4d57;font-size:11px'>model_tools.txt</span>")
        title.setStyleSheet("font-size: 16px; color: #c1c3c8;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        viewer = QTextBrowser()
        viewer.setOpenExternalLinks(True)
        viewer.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
            }
        """)
        html_path = os.path.join(os.path.dirname(__file__), "refs", "model_spec.html")
        if os.path.exists(html_path):
            with open(html_path) as f:
                viewer.setHtml(f.read())
        else:
            viewer.setPlainText("model_spec.html not found in refs/")
        layout.addWidget(viewer, 1)

        self.tabs.addTab(tab, "Model Spec")

    def _build_make_spec_tab(self):
        """Tab 7: Make (3D Printing) spec as HTML reference"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        hdr = QHBoxLayout()
        title = QLabel("<b>3D Print Make Spec</b>  "
                       "<span style='color:#4a4d57;font-size:11px'>make_tools.txt</span>")
        title.setStyleSheet("font-size: 16px; color: #c1c3c8;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        viewer = QTextBrowser()
        viewer.setOpenExternalLinks(True)
        viewer.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
            }
        """)
        html_path = os.path.join(os.path.dirname(__file__), "refs", "make_spec.html")
        if os.path.exists(html_path):
            with open(html_path) as f:
                viewer.setHtml(f.read())
        else:
            viewer.setPlainText("make_spec.html not found in refs/")
        layout.addWidget(viewer, 1)

        self.tabs.addTab(tab, "Make Spec")

    def _refresh_spec(self):
        """Rebuild the spec tab content with filter applied"""
        # Clear
        while self.spec_container_layout.count():
            item = self.spec_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filter_text = self.spec_filter.text().lower()
        total_tools = 0
        shown_tools = 0

        # Build shortcuts legend from spec shortcuts
        import re
        spec_text = open(os.path.join(FC_DIR, "sketch_tools.txt")).read()
        # Extract from the shortcut key table in the spec
        sc_match = re.search(r'## 11\. Common Shortcut Keys.*?(?=\n##|\Z)', spec_text, re.DOTALL)
        shortcuts = []
        if sc_match:
            for m in re.finditer(r'\|\s*`([^`]+)`\s*\|\s*(\S[\w/ ]+?)\s*\|', sc_match.group()):
                shortcuts.append(f"<b>{m.group(1)}</b>={m.group(2)}")
        sc_text = "  ".join(shortcuts[:6])
        if sc_text:
            self.spec_legend_shortcuts.setText(f"<span style='color:#4a4d57'>Shortcuts:</span> {sc_text}")

        for cat in self.SPEC_CATEGORIES:
            # Filter
            cat_tools = []
            for name, desc, icon_name in cat["tools"]:
                total_tools += 1
                if filter_text and filter_text not in name.lower() and filter_text not in icon_name.lower():
                    continue
                cat_tools.append((name, desc, icon_name))
            if not cat_tools and filter_text:
                continue

            section = self._build_spec_category(cat["name"], cat_tools)
            self.spec_container_layout.addWidget(section)
            shown_tools += len(cat_tools)

        self.spec_container_layout.addStretch()
        self.spec_count.setText(f"{shown_tools}/{total_tools} tools")

    def _build_spec_category(self, cat_name, tools):
        """Build a card for one spec category showing its tools"""
        w = QWidget()
        w.setStyleSheet("background: #1e1f2a; border: 1px solid #2a2b30; border-radius: 6px;")

        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        hdr = QLabel(f"<b>{cat_name}</b>")
        hdr.setStyleSheet("color: #4fc3f7; font-size: 13px; padding: 2px 0;")
        layout.addWidget(hdr)

        grid = QGridLayout()
        grid.setSpacing(4)
        col = 0
        row = 0

        for name, desc, icon_name in tools:
            cell = self._build_spec_tool_cell(name, desc, icon_name)
            grid.addWidget(cell, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

        layout.addLayout(grid)
        return w

    def _build_spec_tool_cell(self, name, desc, icon_name):
        """Build a single tool cell with icon preview, name, FC status"""
        cell = QFrame()
        cell.setFixedHeight(72)
        cell.setStyleSheet("""
            QFrame { background: #25263a; border: 1px solid transparent; border-radius: 4px; }
            QFrame:hover { border-color: #4a9eff66; }
        """)

        layout = QHBoxLayout(cell)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        icon_preview = QLabel()
        icon_preview.setFixedSize(40, 40)
        icon_preview.setAlignment(Qt.AlignCenter)

        fc_icon_file = f"{icon_name}.svg" if icon_name else ""
        svg = self.icons.get(fc_icon_file, "")
        fc_icon_exists = bool(svg)

        if svg:
            pix = render_svg_to_pixmap(svg, 36, self._is_dark)
            icon_preview.setPixmap(pix)
        else:
            icon_preview.setStyleSheet("background: #1a1b1e; border: 1px dashed #3a3b4e; border-radius: 4px;")

        layout.addWidget(icon_preview)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)

        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        tool_id = self.SPEC_NAME_TO_ID.get(name)
        has_fc_impl = tool_id is not None and tool_id >= 0
        has_icon = fc_icon_exists and icon_name

        if has_fc_impl and has_icon:
            status_color = "#2e7d32"
            status_text = "✓"
        elif has_fc_impl:
            status_color = "#4a4d57"
            status_text = "no icon"
        else:
            status_color = "#6b6e78"
            status_text = "⚡"

        badge = QLabel(f'<span style="color:{status_color};font-weight:bold;font-size:10px">{status_text}</span>')
        name_row.addWidget(badge)

        ttl = QLabel(f"<b style='color:#c1c3c8;font-size:11px'>{name}</b>")
        name_row.addWidget(ttl)

        if tool_id is not None:
            id_lbl = QLabel(f'<span style="color:#4a4d57;font-size:9px">ID {tool_id}</span>')
            name_row.addWidget(id_lbl)

        name_row.addStretch()
        text_col.addLayout(name_row)

        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #6b6e78; font-size: 10px;")
        text_col.addWidget(desc_lbl)

        layout.addLayout(text_col, 1)
        cell.setToolTip(f"{name}: {desc}\nIcon: {icon_name or '(none)'}\nFC Tool ID: {tool_id or 'Not mapped'}")

        return cell

    def _apply_theme(self):
        """Swap the entire UI stylesheet between dark and light."""
        self.setStyleSheet(self.DARK_QSS if self._is_dark else self.LIGHT_QSS)
        self.dark_btn.setText("Dark" if self._is_dark else "Light")

    def _refresh_all(self):
        self._refresh_browse()
        self._refresh_stage()
        self._populate_editor_list()

    def _refresh_browse(self):
        """Rebuild the browse tab icon grid with filtering"""
        # Clear grid
        while self.browse_grid.count():
            item = self.browse_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filter_text = self.browse_filter.text().lower()
        stage_filter = self.browse_stage_filter.currentText()
        usage = self._get_tool_usage()

        cols = 8
        row = col = 0
        count = 0

        for name, svg_content in sorted(self.icons.items()):
            if filter_text and filter_text not in name.lower():
                continue

            icon_usage = usage.get(name, [])
            # Stage filter
            if stage_filter == "Unused" and icon_usage:
                continue
            if stage_filter not in ("All", "Unused") and \
               not any(s == stage_filter for s, _ in icon_usage):
                continue

            w = BrowserIcon(name, svg_content, icon_usage, self._is_dark)
            w.clicked.connect(self._browse_icon_clicked)
            self.browse_grid.addWidget(w, row, col)
            count += 1
            col += 1
            if col >= cols:
                col = 0
                row += 1

        self.status_label.setText(f"{count} icons shown ({len(self.icons)} total)")

    def _browse_icon_clicked(self, name):
        """When an icon is clicked in browse tab, highlight and show info"""
        # Switch to editor tab
        self.tabs.setCurrentIndex(2)
        # Find and select in editor list
        items = self.editor_icon_list.findItems(name, Qt.MatchExactly)
        if items:
            self.editor_icon_list.setCurrentItem(items[0])
            self._on_editor_icon_selected(items[0])

    def _build_tool_row(self, tool, index):
        """Build a Scandi tool row: icon + name + filename + shortcut"""
        row = QFrame()
        row.setObjectName(f"tool_row_{index}")
        row.setFixedHeight(32)
        row.setStyleSheet(
            "QFrame { background: transparent; border: none; border-radius: 3px; }"
            "QFrame:hover { background: #2e2e4a; }"
        )

        rl = QHBoxLayout(row)
        rl.setContentsMargins(8, 0, 8, 0)
        rl.setSpacing(8)

        # Click indicator / selection dot
        self._tool_dots[index] = QLabel("○")
        self._tool_dots[index].setFixedWidth(14)
        self._tool_dots[index].setStyleSheet("color: #556; font-size: 10px;")
        rl.addWidget(self._tool_dots[index])

        # Icon preview
        icon_preview = QLabel()
        icon_preview.setFixedSize(22, 22)
        svg_content = self.icons.get(tool["icon"], "")
        if svg_content:
            pix = render_svg_to_pixmap(svg_content, 20, self._is_dark)
            icon_preview.setPixmap(pix)
        else:
            icon_preview.setStyleSheet("background: #1a1a2e; border: 1px dashed #2e2e4a; border-radius: 2px;")
        rl.addWidget(icon_preview)

        # Tool name
        name_lbl = QLabel(tool["name"])
        name_lbl.setStyleSheet("color: #e0e0e0; font-size: 12px; font-weight: 500;")
        rl.addWidget(name_lbl)

        rl.addSpacing(12)

        # Icon filename (muted)
        icon_lbl = QLabel(tool["icon"])
        icon_lbl.setStyleSheet("color: #556; font-size: 10px;")
        rl.addWidget(icon_lbl)

        rl.addStretch()

        # Shortcut (muted, monospace)
        sc = tool.get("shortcut", "")
        sc_text = f"[{sc}]" if sc else ""
        sc_lbl = QLabel(sc_text)
        sc_lbl.setStyleSheet("color: #445; font-family: monospace; font-size: 10px;")
        sc_lbl.setFixedWidth(60)
        sc_lbl.setAlignment(Qt.AlignRight)
        rl.addWidget(sc_lbl)

        # Arrow indicator
        arrow = QLabel("→")
        arrow.setStyleSheet("color: #2e2e4a; font-size: 10px;")
        arrow.setFixedWidth(16)
        arrow.setAlignment(Qt.AlignCenter)
        rl.addWidget(arrow)

        # Make row clickable
        row.mousePressEvent = lambda e, idx=index: self._on_tool_row_clicked(idx)

        return row

    def _refresh_stage(self):
        """Refresh the stage mapping tab — Scandi tool rows"""
        stage = self.stage_combo.currentText()
        tools = self.stages.get(stage, [])

        self.stage_desc.setText(f"{len(tools)} tools")

        # Clear toolbar mockup
        while self.toolbar_layout.count():
            item = self.toolbar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear tool rows
        while self.tool_list_layout.count():
            item = self.tool_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._tool_row_frames = []
        self._tool_dots = {}
        self._selected_row = -1

        for i, t in enumerate(tools):
            icon_name = t["icon"]
            svg_content = self.icons.get(icon_name, "")

            # Toolbar button mockup
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setToolTip(f"{t['name']} ({t['shortcut']})")
            btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-radius: 2px; }"
                "QPushButton:hover { background: #2e2e4a; }"
            )
            if svg_content:
                pix = render_svg_to_pixmap(svg_content, 18, self._is_dark)
                btn.setIcon(QIcon(pix))
                btn.setIconSize(QSize(16, 16))
            self.toolbar_layout.addWidget(btn)

            # Custom tool row
            row = self._build_tool_row(t, i)
            self._tool_row_frames.append(row)
            self.tool_list_layout.addWidget(row)

        self.toolbar_layout.addStretch()

        # Select first tool by default
        if self._tool_row_frames:
            self._on_tool_row_clicked(0)

    def _on_tool_row_clicked(self, index):
        """Handle a Scandi tool row click"""
        if index < 0 or index >= len(self._tool_row_frames):
            return

        # Deselect old
        if self._selected_row >= 0 and self._selected_row < len(self._tool_row_frames):
            old_row = self._tool_row_frames[self._selected_row]
            old_row.setStyleSheet(
                "QFrame { background: transparent; border: none; border-radius: 3px; }"
                "QFrame:hover { background: #2e2e4a; }"
            )
            if self._selected_row in self._tool_dots:
                self._tool_dots[self._selected_row].setStyleSheet("color: #556; font-size: 10px;")

        # Select new
        self._selected_row = index
        row = self._tool_row_frames[index]
        row.setStyleSheet(
            "QFrame { background: #24243d; border: 1px solid #3a9bea; border-radius: 3px; }"
            "QFrame:hover { background: #2a2a4f; }"
        )
        if index in self._tool_dots:
            self._tool_dots[index].setStyleSheet("color: #3a9bea; font-size: 10px;")

        # Update icon picker
        stage = self.stage_combo.currentText()
        tools = self.stages.get(stage, [])
        if index < len(tools):
            current_icon = tools[index]["icon"]
            idx = self.icon_picker.findText(current_icon)
            if idx >= 0:
                self.icon_picker.setCurrentIndex(idx)

    def _on_icon_picked(self, name):
        pass

    def _assign_icon(self):
        """Assign a new icon to a tool and save to source file"""
        if self._selected_row < 0:
            QMessageBox.warning(self, "No tool", "Select a tool first")
            return

        stage = self.stage_combo.currentText()
        tools = self.stages[stage]
        if self._selected_row >= len(tools):
            return

        row = self._selected_row
        tool = tools[row]
        old_icon = tool["icon"]
        new_icon = self.icon_picker.currentText()

        if old_icon == new_icon:
            QMessageBox.information(self, "Same icon", "That's already the assigned icon.")
            return

        # Update the C++ source file
        src_file = os.path.join(SRC_DIR, f"{stage}Stage.cpp")
        if not os.path.exists(src_file):
            QMessageBox.warning(self, "Error", f"Source file not found: {src_file}")
            return

        qrc_path = f":/icons/{old_icon}" if not old_icon.startswith(":/") else old_icon
        new_qrc_path = f":/icons/{new_icon}" if not new_icon.startswith(":/") else new_icon

        with open(src_file) as f:
            content = f.read()

        old_line = f'":/icons/{old_icon}"'
        new_line = f'":/icons/{new_icon}"'
        content = content.replace(old_line, new_line)

        with open(src_file, "w") as f:
            f.write(content)

        # Update our data
        tool["icon"] = new_icon
        self._refresh_stage()

        QMessageBox.information(self, "Saved",
            f"Updated {stage}Stage.cpp:\n{tool['name']}: {old_icon} → {new_icon}")

    def _populate_editor_list(self):
        self.editor_icon_list.clear()
        for name in sorted(self.icons.keys()):
            item = QListWidgetItem(name)
            self.editor_icon_list.addItem(item)

    def _on_editor_icon_selected(self, item):
        name = item.text()
        svg_content = self.icons.get(name, "")
        if not svg_content:
            return

        self.svg_editor.blockSignals(True)
        self.svg_editor.setPlainText(svg_content)
        self.svg_editor.blockSignals(False)
        self._current_editing = name
        self._original_svg = svg_content

        # Update previews
        self._update_editor_previews(svg_content)
        self.editor_info.setText(f"Editing: {name}  ({len(svg_content)} chars)")

    def _update_editor_previews(self, svg_content):
        pix64 = render_svg_to_pixmap(svg_content, 64, self._is_dark)
        pix24 = render_svg_to_pixmap(svg_content, 24, self._is_dark)
        pix20 = render_svg_to_pixmap(svg_content, 20, self._is_dark)

        self.editor_preview_64.setPixmap(pix64)
        self.editor_preview_24.setPixmap(pix24)
        self.editor_preview_toolbar.setPixmap(pix20)

    def _on_svg_edited(self):
        name = getattr(self, '_current_editing', None)
        if not name:
            return
        svg_content = self.svg_editor.toPlainText()
        self._update_editor_previews(svg_content)

    def _revert_icon(self):
        if hasattr(self, '_original_svg'):
            self.svg_editor.blockSignals(True)
            self.svg_editor.setPlainText(self._original_svg)
            self.svg_editor.blockSignals(False)
            self._on_svg_edited()

    def _save_current_icon(self):
        name = getattr(self, '_current_editing', None)
        if not name:
            QMessageBox.warning(self, "No icon", "Select an icon first.")
            return

        svg_content = self.svg_editor.toPlainText()
        path = os.path.join(ICON_DIR, name)

        with open(path, "w") as f:
            f.write(svg_content)

        self.icons[name] = svg_content
        QMessageBox.information(self, "Saved", f"Icon saved to:\n{path}")

        # Refresh all views
        self._refresh_all()

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self._apply_theme()
        # Rebuild all icon previews for the new theme
        self._refresh_all()
        # Force rebuild the stage mapping list
        if hasattr(self, 'stage_combo'):
            self._refresh_stage()

    def _generate_template(self, template):
        """Generate icon from template and switch to generator tab"""
        svg_content = ""
        if template == "line":
            svg_content = SVG_TEMPLATE.format(
                '  <line x1="4" y1="20" x2="20" y2="4"/>\n'
                '  <circle cx="4" cy="20" r="1.5" fill="#c1c3c8"/>\n'
                '  <circle cx="20" cy="4" r="1.5" fill="#c1c3c8"/>'
            )
        elif template == "rect":
            svg_content = SVG_TEMPLATE.format(
                '  <rect x="3" y="4" width="18" height="16" rx="1"/>\n'
                '  <circle cx="3" cy="4" r="1.5" fill="#c1c3c8"/>\n'
                '  <circle cx="21" cy="20" r="1.5" fill="#c1c3c8"/>'
            )
        elif template == "circle":
            svg_content = SVG_TEMPLATE.format(
                '  <circle cx="12" cy="12" r="9"/>'
            )
        elif template == "arc":
            svg_content = SVG_TEMPLATE.format(
                '  <path d="M6,18 A9,9 0 0,1 18,6"/>\n'
                '  <circle cx="6" cy="18" r="1.5" fill="#c1c3c8"/>\n'
                '  <circle cx="18" cy="6" r="1.5" fill="#c1c3c8"/>'
            )
        elif template == "arrow":
            svg_content = SVG_TEMPLATE.format(
                '  <line x1="4" y1="12" x2="20" y2="12"/>\n'
                '  <polyline points="16,8 20,12 16,16" fill="none" stroke="#c1c3c8" stroke-width="1.5" stroke-linejoin="round"/>'
            )
        elif template == "cross":
            svg_content = SVG_TEMPLATE.format(
                '  <line x1="5" y1="12" x2="19" y2="12"/>\n'
                '  <line x1="12" y1="5" x2="12" y2="19"/>\n'
                '  <circle cx="12" cy="12" r="1.5" fill="#c1c3c8"/>'
            )
        elif template == "gear":
            svg_content = SVG_TEMPLATE.format(
                '  <path d="M12,3 L13.5,6.5 L14,6.6 L16.5,4.5 L17.5,7.5 L18,7.7 L20,5.5 L20.5,8.5 L20.3,9 L22,"\n'
                '        stroke="#c1c3c8" fill="none"/>\n'
                '  <circle cx="12" cy="12" r="4" stroke="#c1c3c8" fill="none"/>'
            )
        elif template == "box3d":
            svg_content = SVG_TEMPLATE.format(
                '  <rect x="4" y="7" width="14" height="12" rx="1"/>\n'
                '  <line x1="4" y1="7" x2="7" y2="4"/>\n'
                '  <line x1="18" y1="7" x2="21" y2="4"/>\n'
                '  <rect x="7" y="4" width="14" height="12" rx="1" stroke-dasharray="2,2"/>'
            )
        elif template == "plus":
            svg_content = SVG_TEMPLATE.format(
                '  <line x1="12" y1="5" x2="12" y2="19"/>\n'
                '  <line x1="5" y1="12" x2="19" y2="12"/>'
            )
        elif template == "minus":
            svg_content = SVG_TEMPLATE.format(
                '  <line x1="5" y1="12" x2="19" y2="12"/>'
            )

        self.tabs.setCurrentIndex(3)
        self._current_editing_template = template
        self.gen_svg_input.blockSignals(True)
        self.gen_svg_input.setPlainText(svg_content)
        self.gen_svg_input.blockSignals(False)

        # Auto-suggest name
        self.gen_name.setText(template)
        self._preview_generated()

    def _preview_generated(self):
        svg_text = self.gen_svg_input.toPlainText().strip()
        if not svg_text:
            return
        # Wrap in SVG boilerplate if needed
        if not svg_text.startswith('<svg'):
            svg_text = SVG_TEMPLATE.format(svg_text)
        pix64 = render_svg_to_pixmap(svg_text, 64, self._is_dark)
        self.gen_preview.setPixmap(pix64)

    def _save_generated(self):
        name = self.gen_name.text().strip()
        if not name:
            QMessageBox.warning(self, "No name", "Enter an icon name first.")
            return
        if not name.endswith('.svg'):
            name += '.svg'

        svg_text = self.gen_svg_input.toPlainText().strip()
        if not svg_text:
            return
        if not svg_text.startswith('<svg'):
            svg_text = SVG_TEMPLATE.format(svg_text)

        path = os.path.join(ICON_DIR, name)
        with open(path, "w") as f:
            f.write(svg_text)

        self.icons[name] = svg_text
        QMessageBox.information(self, "Saved", f"Icon saved to FC:\n{path}")
        self._refresh_all()

    def _save_all(self):
        """Save all in-memory icons back to disk"""
        count = 0
        for name, content in self.icons.items():
            path = os.path.join(ICON_DIR, name)
            with open(path, "w") as f:
                f.write(content)
            count += 1
        QMessageBox.information(self, "Saved",
            f"All {count} icons saved to:\n{ICON_DIR}")

    def _deploy_to_fc(self):
        """Save icons, rebuild FC, kill old process, launch new one"""
        # 1. Save all icons
        count = 0
        for name, content in self.icons.items():
            path = os.path.join(ICON_DIR, name)
            with open(path, "w") as f:
                f.write(content)
            count += 1

        # 2. Rebuild FC
        build_dir = os.path.join(FC_DIR, "build")
        if not os.path.exists(build_dir):
            QMessageBox.critical(self, "Error",
                f"Build dir not found:\n{build_dir}")
            return

        self.status_label.setText("🔄 Building FissionCAD...")
        QApplication.processEvents()

        import subprocess, shlex
        ret = os.system(f"cd {shlex.quote(build_dir)} && cmake .. > /tmp/fc_build.log 2>&1")
        if ret != 0:
            QMessageBox.critical(self, "CMake Failed",
                f"cmake returned {ret}. See /tmp/fc_build.log")
            self.status_label.setText("❌ Build failed")
            return

        ret = os.system(f"cd {shlex.quote(build_dir)} && make -j$(nproc) >> /tmp/fc_build.log 2>&1")
        if ret != 0:
            QMessageBox.critical(self, "Build Failed",
                f"make returned {ret}. See /tmp/fc_build.log")
            self.status_label.setText("❌ Build failed")
            return

        # 3. Kill old process
        os.system("pkill -x fission-cad 2>/dev/null")

        # 4. Launch new binary
        binary = os.path.join(build_dir, "fission-cad")
        if os.path.exists(binary):
            import subprocess
            subprocess.Popen([binary])
            self.status_label.setText("✅ FC rebuilt & relaunched")
            QMessageBox.information(self, "Deployed",
                "FissionCAD rebuilt and launched.")
        else:
            self.status_label.setText("❌ Binary not found")
            QMessageBox.critical(self, "Error",
                f"Binary not found:\n{binary}")


# ── Browser icon widget ──────────────────────────────────────────

class BrowserIcon(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, name, svg_content, usage, dark):
        super().__init__()
        self.name = name
        self.svg_content = svg_content
        self.usage = usage
        self.dark = dark
        self.setFixedSize(ICON_GRID_SIZE + 4, ICON_GRID_SIZE + 28)
        self.setToolTip(self._tooltip_text())
        self.setStyleSheet("""
            BrowserIcon { background: #25253a; border: 1px solid transparent; border-radius: 4px; }
            BrowserIcon:hover { border-color: #4a9eff66; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        self.pixmap_label = QLabel()
        self.pixmap_label.setFixedSize(ICON_GRID_SIZE, ICON_GRID_SIZE)
        self.pixmap_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pixmap_label, 0, Qt.AlignCenter)

        # Name + usage badge
        info = QHBoxLayout()
        info.setContentsMargins(2, 0, 2, 0)
        nlabel = QLabel(name.replace('.svg', ''))
        nlabel.setStyleSheet("font-size: 8px; color: #aaa; background: transparent;")
        info.addWidget(nlabel)
        if usage:
            badge = QLabel(str(len(usage)))
            badge.setFixedSize(14, 12)
            badge.setAlignment(Qt.AlignCenter)
            c = "#4a9eff" if len(usage) > 0 else "#aaa"
            badge.setStyleSheet(
                f"font-size: 7px; color: white; background: {c}; border-radius: 6px;")
            info.addWidget(badge)
        info.addStretch()
        layout.addLayout(info)

        self._render()

    def _tooltip_text(self):
        lines = [f"Icon: {self.name}"]
        if self.usage:
            for stage, tool in self.usage:
                lines.append(f"  Used by: {stage} Stage → {tool}")
        else:
            lines.append("  Unused — available for assignment")
        return "\n".join(lines)

    def _render(self):
        if self.svg_content:
            pix = render_svg_to_pixmap(self.svg_content, ICON_GRID_SIZE - 8, self.dark)
            self.pixmap_label.setPixmap(pix)

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)
        super().mousePressEvent(event)


# ── Main ─────────────────────────────────────────────────────────

def main():
    # We need QtSvg module
    app = QApplication(sys.argv)

    # Check if PyQt5.QtSvg is available
    try:
        from PyQt5 import QtSvg
    except ImportError:
        QMessageBox.critical(None, "Missing dependency",
            "PyQt5.QtSvg is required.\nInstall with: uv add pyqt5-svg")
        return 1

    w = IconCMS()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
