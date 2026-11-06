import base64
import html
import json
import math
import os
import re
import tkinter as tk
from collections import Counter
from io import BytesIO
from tkinter import font as tkfont
from tkinter import colorchooser, filedialog, messagebox, simpledialog

try:
    from PIL import Image, ImageChops, ImageGrab, ImageMath
except ImportError:
    Image = None
    ImageChops = None
    ImageGrab = None
    ImageMath = None

try:
    from psd_tools import PSDImage
except ImportError:
    PSDImage = None

PSD_CSS_BLEND_MODES = frozenset({
    "normal",
    "multiply",
    "screen",
    "overlay",
    "darken",
    "lighten",
    "color-dodge",
    "color-burn",
    "hard-light",
    "soft-light",
    "difference",
    "exclusion",
    "hue",
    "saturation",
    "color",
    "luminosity",
    "plus-lighter",
})

BG = "#0f172a"
PANEL_BG = "#1e293b"
BORDER = "#334155"
HOVER_BG = "#334155"
ACTIVE_BG = "#2563eb"
DANGER_BG = "#7f1d1d"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
SUBTLE = "#fca5a5"
ACCENT = "#3b82f6"
ICON = "#dbe3ee"
BRUSH_COLOR = "#2563eb"
DOC_BG = "#ffffff"
PAGE_BACKGROUNDS = ("white", "none")
TRANSPARENT_BG = "#cbd5e1"
DROP_BG = "#1d4ed8"

WINDOWED_SIZE = (1100, 700)
MIN_SIZE = (760, 460)
CONTENT_SIZE = (960, 540)
IMAGE_FILE_PATTERN = "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.psd"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".psd")
RULER_SIZE = 22
RULER_BG = "#0b1220"
RULER_TICK = "#475569"
GUIDE_COLOR = "#38bdf8"
SIDEBAR_WIDTH = 56
LAYER_PANEL_WIDTH = 240
TOOL_SIZE = 40
ZOOM_STEPS = (0.25, 0.33, 0.5, 0.67, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0)
RULER_STEPS = (10, 20, 50, 100, 200, 500, 1000)


def draw_move(c, col):
    c.create_line(20, 7, 20, 33, fill=col, width=2, capstyle="round")
    c.create_line(7, 20, 33, 20, fill=col, width=2, capstyle="round")
    c.create_polygon(20, 5, 16, 11, 24, 11, fill=col, outline="")
    c.create_polygon(20, 35, 16, 29, 24, 29, fill=col, outline="")
    c.create_polygon(5, 20, 11, 16, 11, 24, fill=col, outline="")
    c.create_polygon(35, 20, 29, 16, 29, 24, fill=col, outline="")


def draw_marquee(c, col):
    c.create_rectangle(8, 8, 32, 32, outline=col, width=2, dash=(3, 2))


def draw_lasso(c, col):
    c.create_oval(8, 6, 29, 25, outline=col, width=2)
    c.create_line(19, 25, 16, 31, 19, 33, fill=col, width=2, smooth=True)


def draw_wand(c, col):
    c.create_line(9, 33, 25, 17, fill=col, width=2, capstyle="round")
    c.create_line(28, 4, 28, 14, fill=col, width=2)
    c.create_line(23, 9, 33, 9, fill=col, width=2)
    c.create_line(25, 6, 31, 12, fill=col, width=2)


def draw_crop(c, col):
    c.create_line(14, 6, 14, 27, 34, 27, fill=col, width=2)
    c.create_line(6, 14, 27, 14, 27, 34, fill=col, width=2)


def draw_slice(c, col):
    c.create_rectangle(7, 7, 31, 31, outline=col, width=2, dash=(3, 2))
    c.create_line(20, 20, 33, 33, fill=col, width=2)
    c.create_polygon(34, 34, 27, 32, 32, 27, fill=col, outline="")


def draw_eyedropper(c, col):
    c.create_line(6, 36, 24, 18, fill=col, width=2, capstyle="round")
    c.create_line(25, 17, 29, 13, fill=col, width=7, capstyle="round")


def draw_healing(c, col):
    c.create_rectangle(9, 13, 31, 31, outline=col, width=2)
    c.create_line(15, 13, 15, 9, 25, 9, 25, 13, fill=col, width=2)
    c.create_line(16, 22, 24, 22, fill=col, width=2)
    c.create_line(20, 18, 20, 26, fill=col, width=2)


def draw_brush(c, col):
    c.create_line(10, 33, 22, 21, fill=col, width=2, capstyle="round")
    c.create_polygon(19, 18, 27, 7, 33, 13, 24, 22, fill=col, outline="")


def draw_stamp(c, col):
    c.create_rectangle(15, 6, 25, 13, outline=col, width=2)
    c.create_line(20, 13, 20, 17, fill=col, width=2)
    c.create_polygon(10, 24, 30, 24, 34, 32, 6, 32, outline=col, width=2)


def draw_eraser(c, col):
    c.create_polygon(10, 24, 22, 10, 32, 20, 20, 34, outline=col, width=2)
    c.create_line(27, 15, 15, 29, fill=col, width=2)


def draw_gradient(c, col):
    top = (241, 245, 249)
    bottom = (51, 65, 85)
    for i in range(21):
        t = i / 20
        rgb = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        c.create_line(10, 10 + i, 30, 10 + i, fill="#%02x%02x%02x" % rgb)
    c.create_rectangle(10, 10, 30, 30, outline=MUTED)


def draw_bucket(c, col):
    c.create_arc(10, 5, 30, 25, start=0, extent=180, style="arc",
                 outline=col, width=2)
    c.create_polygon(10, 17, 30, 17, 27, 33, 13, 33, outline=col, width=2)
    c.create_polygon(31, 4, 35, 10, 31, 13, 27, 10, fill=col,
                     outline="", smooth=True)


def draw_blur(c, col):
    c.create_polygon(20, 7, 27, 18, 25, 27, 20, 32, 15, 27, 13, 18,
                     outline=col, width=2, smooth=True)


def draw_sharpen(c, col):
    c.create_oval(8, 8, 26, 26, outline=col, width=2)
    c.create_oval(18, 15, 22, 19, fill=col, outline="")
    c.create_line(24, 24, 33, 33, fill=col, width=3, capstyle="round")


def draw_pen(c, col):
    c.create_polygon(20, 6, 27, 17, 23, 29, 17, 29, 13, 17,
                     outline=col, width=2)
    c.create_line(20, 13, 20, 24, fill=col, width=1)
    c.create_oval(18.5, 10.5, 21.5, 13.5, fill=col, outline="")


def draw_text(c, col):
    c.create_line(10, 8, 30, 8, fill=col, width=2)
    c.create_line(20, 8, 20, 32, fill=col, width=2)
    c.create_line(14, 32, 26, 32, fill=col, width=2)


def draw_path(c, col):
    c.create_polygon(12, 7, 12, 29, 17, 24, 21, 33, 25, 31, 21, 23, 28, 22,
                     fill=col, outline="")


def draw_rect(c, col):
    c.create_rectangle(8, 10, 32, 30, outline=col, width=2)


def draw_ellipse(c, col):
    c.create_oval(8, 10, 32, 30, outline=col, width=2)


def draw_hand(c, col):
    c.create_oval(10, 19, 29, 34, outline=col, width=2)
    for x, top in ((13, 12), (17, 9), (21, 9), (25, 13)):
        c.create_line(x, 22, x, top, fill=col, width=2, capstyle="round")
    c.create_line(12, 26, 6, 19, fill=col, width=2, capstyle="round")


def draw_zoom(c, col):
    c.create_oval(7, 7, 25, 25, outline=col, width=2)
    c.create_line(23, 23, 33, 33, fill=col, width=3, capstyle="round")
    c.create_line(12, 16, 20, 16, fill=col, width=2)
    c.create_line(16, 12, 16, 20, fill=col, width=2)


TOOLS = [
    ("move", "Di chuyển", draw_move),
    ("marquee", "Chọn vùng", draw_marquee),
    ("lasso", "Chọn tự do", draw_lasso),
    ("wand", "Đũa thần", draw_wand),
    ("crop", "Cắt ảnh", draw_crop),
    ("slice", "Chia lát", draw_slice),
    ("eyedropper", "Ống hút màu", draw_eyedropper),
    ("healing", "Chữa ảnh", draw_healing),
    ("brush", "Cọ vẽ", draw_brush),
    ("stamp", "Con dấu nhân bản", draw_stamp),
    ("eraser", "Cục tẩy", draw_eraser),
    ("gradient", "Chuyển sắc", draw_gradient),
    ("bucket", "Xô màu", draw_bucket),
    ("blur", "Làm mờ", draw_blur),
    ("sharpen", "Làm sắc nét", draw_sharpen),
    ("pen", "Bút vẽ", draw_pen),
    ("text", "Văn bản", draw_text),
    ("path", "Chọn đường dẫn", draw_path),
    ("rect", "Hình chữ nhật", draw_rect),
    ("hand", "Bàn tay", draw_hand),
    ("zoom", "Thu phóng", draw_zoom),
]

CURSORS = {
    "brush": "pencil",
    "eraser": "dotbox",
    "rect": "crosshair",
    "marquee": "crosshair",
    "text": "xterm",
}

TEXT_TAGS = ("p", "h1", "h2", "h3", "h4", "h5", "h6")

TEXT_FORMATS = ("text", "span", "strong")

GROUP_FORMATS = ("text", "h1", "h2", "h3", "h4", "h5", "h6")

GROUP_DISPLAYS = ("block", "flex", "grid","inline")

GROUP_ALIGNS = ("left", "center", "right")

GROUP_JUSTIFIES = ("left", "center", "right", "between")

PSEUDO_KEYS = ("before", "after")

PSEUDO_DISPLAYS = ("", "block", "inline-block", "inline", "none", "flex")

PSEUDO_POSITIONS = ("absolute", "relative", "fixed", "sticky", "static")

PSEUDO_DEFAULTS = {
    "enabled": False,
    "content": "",
    "position": "absolute",
    "top": "",
    "left": "",
    "bottom": "",
    "right": "",
    "transform": "",
    "color": "",
    "background": "",
    "width": "",
    "height": "",
    "margin": "",
    "padding": "",
    "font_size": "",
    "font_weight": "",
    "display": "",
    "extra": "",
}

SHORTCUTS = [
    ("F1", "Mở/đóng tab hướng dẫn phím tắt"),
    ("Ctrl + N", "Tạo project mới"),
    ("Ctrl + O", "Mở tài liệu"),
    ("Ctrl + S", "Lưu tài liệu"),
    ("Ctrl + Shift + S", "Lưu tài liệu sang tệp khác"),
    ("Ctrl + E", "Mở cửa sổ Export"),
    ("Ctrl + Q", "Thoát ứng dụng"),
    ("Ctrl + Z", "Hoàn tác"),
    ("Ctrl + J", "Nhân bản lớp"),
    ("Ctrl + G", "Nhóm các lớp đang chọn"),
    ("Ctrl + ;", "Ẩn/hiện đường gióng"),
    ("Ctrl + lăn chuột", "Thu phóng khung nội dung"),
    ("F11", "Bật/tắt toàn màn hình"),
    ("Esc", "Thoát toàn màn hình"),
]


class Layer:
    def __init__(self, name):
        self.name = name
        self.visible = True
        self.items = []
        self.children = []
        self.parent = None
        self.expanded = True
        self.background_image = None
        self.display = "block"
        self.align = "left"
        self.justify = "left"
        self.gap = 0
        self.blend_mode = "normal"
        self.text_format = ""
        self.group_tag = ""
        self.pseudo = {}


class _DocEvent:
    """Mouse event with canvas coordinates converted to document units."""

    def __init__(self, event, zoom):
        self.widget = event.widget
        self.state = event.state
        self.num = getattr(event, "num", 0)
        self.delta = getattr(event, "delta", 0)
        self.x_root = event.x_root
        self.y_root = event.y_root
        self.x = event.x / zoom
        self.y = event.y / zoom


class Tooltip:
    def __init__(self, widget, text, delay=250):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.after_id = None
        self.tip = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self.after_id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self.after_id is not None:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def _show(self):
        self.after_id = None
        if self.tip is not None:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + (self.widget.winfo_height() - 26) // 2
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.attributes("-topmost", True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            bg=BORDER,
            fg=TEXT,
            font=("Segoe UI", 9),
            padx=10,
            pady=4,
        ).pack()

    def _hide(self, _event=None):
        self._cancel()
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Giao diện toàn màn hình")
        self.configure(bg=BG)
        self.minsize(*MIN_SIZE)
        self.is_fullscreen = False
        self.tool_items = {}
        self.tool_tips = {}
        self.tool_names = {tool_id: name for tool_id, name, _draw in TOOLS}
        self.rect_tool_shape = "rect"
        self.active_tool_id = None
        self.layers = []
        self.layer_counter = 0
        self.active_layer = None
        self.selected_layers = []
        self._selection_anchor = None
        self._stroke = None
        self._last_point = None
        self._temp_ids = []
        self._rect_start = None
        self._rect_preview = None
        self.marquee_region = None
        self._marquee_start = None
        self.history = []
        self.doc_name = "Chưa có tên-1"
        self._new_doc_counter = 1
        self.doc_path = None
        self.content_width, self.content_height = CONTENT_SIZE
        self.content_full = False
        self.content_background = "white"
        self.body_font_family = "none"
        self.zoom = 1.0
        self._content_size_window = None
        self.guides = []
        self.guides_visible = True
        self._guide_drag = None
        self._moving_guide = None
        self._guide_move_start = 0
        self.saved_signature = ""
        self.dirty = False
        self._updating_info = False
        self.info_collapsed = False
        self.info_pinned = False
        self._drag_layer = None
        self._drag_origin = (0, 0)
        self._drag_moved = False
        self._drag_blocked = False
        self._drag_in_panel = False
        self._drop_row = None
        self._drop_mode = None
        self._drop_indicator = None
        self._rename_entry = None
        self._rename_layer = None
        self._move_last = None
        self._move_moved = False
        self._export_window = None
        self._layer_options_window = None
        self._image_refs = {}
        self._image_scaled = {}
        self._text_areas = []
        self._record_offsets = {}
        self._font_cache = {}
        self._font_suggest_entry = None
        self._text_editor = None
        self._text_editor_record = None

        self._build_fonts()
        self._build_ui()
        self._bind_keys()

        self._add_layer(record=False)
        self.saved_signature = self._document_signature()
        self._refresh_doc_tab()
        self.select_tool("brush")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.withdraw()
        self.after(50, self.start_maximized)

    def _build_fonts(self):
        self.font_brand = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_menu = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.font_status = tkfont.Font(family="Consolas", size=10)
        self.font_panel = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.font_layer = tkfont.Font(family="Segoe UI", size=10)
        self.font_marquee = tkfont.Font(
            family="Segoe UI", size=9, weight="bold"
        )

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, minsize=LAYER_PANEL_WIDTH)

        self._build_header()
        self._build_sidebar()
        self._build_workspace()
        self._build_layer_panel()

        self.status = tk.Label(
            self,
            text="",
            font=self.font_status,
            fg=MUTED,
            bg=BG,
            anchor="w",
            padx=16,
            pady=6,
        )
        self.status.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.bind("<Configure>", lambda _e: self._update_status())

    def _build_header(self):
        header = tk.Frame(self, bg=PANEL_BG)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        brand = tk.Frame(header, bg=PANEL_BG)
        brand.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=10)

        tk.Label(
            brand,
            text="T",
            font=self.font_menu,
            fg=TEXT,
            bg=ACCENT,
            width=3,
            pady=4,
        ).pack(side="left")

        tk.Label(
            brand,
            text="Thiết Kế HTML",
            font=self.font_brand,
            fg=TEXT,
            bg=PANEL_BG,
            padx=10,
        ).pack(side="left")

        nav = tk.Frame(header, bg=PANEL_BG)
        nav.grid(row=0, column=1, sticky="e", padx=(0, 12))

        self.btn_fullscreen = self._make_menu_item(
            nav, "Toàn màn hình", self.toggle_fullscreen
        )
        self.btn_fullscreen.pack(side="left", padx=1)

        self._make_menu_item(nav, "Thu nhỏ", self.minimize_window).pack(
            side="left", padx=1
        )
        self._make_menu_item(
            nav, "Cỡ nhỏ", lambda: self.set_window_size(800, 520)
        ).pack(side="left", padx=1)
        self._make_menu_item(
            nav, "Cỡ lớn", lambda: self.set_window_size(1300, 860)
        ).pack(side="left", padx=1)
        self._make_menu_item(nav, "Mới", self._new_document).pack(
            side="left", padx=1
        )
        self._make_menu_item(nav, "Chèn hình", self._insert_image).pack(
            side="left", padx=1
        )
        self._make_menu_item(nav, "Mở", self._open_document).pack(
            side="left", padx=1
        )
        self.save_menu = tk.Menu(
            self,
            tearoff=0,
            bg="#0b1220",
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=BG,
            font=("Segoe UI", 9),
        )
        self.save_menu.add_command(
            label="Lưu",
            accelerator="Ctrl+S",
            command=self._save_document,
        )
        self.save_menu.add_command(
            label="Lưu khác…",
            accelerator="Ctrl+Shift+S",
            command=self._save_document_as,
        )
        save_item = self._make_menu_item(nav, "Lưu ▾", lambda: None)
        save_item.bind("<Button-1>", self._open_save_menu)
        save_item.pack(side="left", padx=1)
        self._make_menu_item(nav, "Export", self._open_export_window).pack(
            side="left", padx=1
        )
        self._make_menu_item(nav, "Thoát", self._on_close, danger=True).pack(
            side="left", padx=1
        )

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=PANEL_BG)
        sidebar.grid(row=1, column=0, sticky="ns")

        border = tk.Frame(sidebar, bg=BORDER, width=1)
        border.pack(side="right", fill="y")

        self.sidebar_canvas = tk.Canvas(
            sidebar, bg=PANEL_BG, highlightthickness=0, width=SIDEBAR_WIDTH
        )
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)

        self.tools_frame = tk.Frame(self.sidebar_canvas, bg=PANEL_BG)
        window = self.sidebar_canvas.create_window(
            (0, 0), window=self.tools_frame, anchor="nw"
        )
        self.sidebar_canvas.itemconfigure(window, width=SIDEBAR_WIDTH)

        self.tools_frame.bind("<Configure>", self._sync_scrollregion)
        self.sidebar_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.tools_frame.bind("<MouseWheel>", self._on_mousewheel)
        sidebar.bind("<MouseWheel>", self._on_mousewheel)

        for tool_id, name, draw in TOOLS:
            self._build_tool(tool_id, name, draw)

    def _build_tool(self, tool_id, name, draw):
        item = tk.Canvas(
            self.tools_frame,
            width=TOOL_SIZE,
            height=TOOL_SIZE,
            bg=PANEL_BG,
            highlightthickness=0,
            cursor="hand2",
        )
        item.pack(pady=1)

        backdrop = item.create_rectangle(
            2, 2, TOOL_SIZE - 2, TOOL_SIZE - 2, fill=PANEL_BG, outline=""
        )
        draw(item, ICON)

        item.bind("<Enter>", lambda _e, tid=tool_id: self._tool_enter(tid))
        item.bind("<Leave>", lambda _e, tid=tool_id: self._tool_leave(tid))
        item.bind("<Button-1>", lambda _e, tid=tool_id: self.select_tool(tid))
        item.bind("<MouseWheel>", self._on_mousewheel)
        if tool_id == "rect":
            item.bind("<Button-3>", self._open_rect_shape_menu)

        self.tool_tips[tool_id] = Tooltip(item, name)
        self.tool_items[tool_id] = (item, backdrop)

    def _build_workspace(self):
        workspace = tk.Frame(self, bg=BG)
        workspace.grid(row=1, column=1, sticky="nsew")
        workspace.grid_rowconfigure(1, weight=1)
        workspace.grid_columnconfigure(0, weight=1)

        tabbar = tk.Frame(workspace, bg=BG)
        tabbar.grid(row=0, column=0, sticky="ew")
        tab = tk.Frame(tabbar, bg=PANEL_BG)
        tab.pack(side="left", padx=(28, 0), pady=(12, 0))
        self.doc_tab_label = tk.Label(
            tab,
            text=self.doc_name,
            font=self.font_layer,
            fg=TEXT,
            bg=PANEL_BG,
            padx=14,
            pady=6,
        )
        self.doc_tab_label.pack()
        self.doc_tab_label.configure(cursor="hand2")
        self.doc_tab_label.bind("<Button-1>", self._hide_help_tab)

        self.help_tab_label = tk.Label(
            tabbar,
            text="Hướng dẫn phím tắt",
            font=self.font_layer,
            fg=MUTED,
            bg=PANEL_BG,
            padx=14,
            pady=6,
            cursor="hand2",
        )
        self.help_tab_label.pack(side="left", padx=(2, 0), pady=(12, 0))
        self.help_tab_label.bind("<Button-1>", self._toggle_help_tab)
        self.help_visible = False

        self.content_size_button = tk.Label(
            tabbar,
            text="",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=BG,
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.content_size_button.pack(side="right", padx=(0, 32), pady=(12, 0))
        self.content_size_button.bind(
            "<Button-1>", lambda _e: self._open_content_size_dialog()
        )
        self.content_size_button.bind(
            "<Enter>", lambda _e: self.content_size_button.configure(fg=TEXT)
        )
        self.content_size_button.bind(
            "<Leave>", lambda _e: self.content_size_button.configure(fg=MUTED)
        )
        Tooltip(
            self.content_size_button,
            "Kích thước khung nội dung, nhấp để thay đổi",
        )
        self._update_content_size_label()

        wrap = tk.Frame(workspace, bg=BG)
        wrap.grid(row=1, column=0, sticky="nsew", padx=32, pady=(10, 26))
        self.workspace_wrap = wrap
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(1, weight=1)

        self.ruler_corner = tk.Canvas(
            wrap,
            width=RULER_SIZE,
            height=RULER_SIZE,
            bg=RULER_BG,
            highlightthickness=0,
            bd=0,
        )
        self.ruler_corner.grid(row=0, column=0, sticky="nsew")
        self.ruler_corner.create_line(
            RULER_SIZE - 7,
            RULER_SIZE - 1,
            RULER_SIZE - 1,
            RULER_SIZE - 7,
            fill=RULER_TICK,
        )
        self.hruler = tk.Canvas(
            wrap, height=RULER_SIZE, bg=RULER_BG, highlightthickness=0, bd=0
        )
        self.hruler.grid(row=0, column=1, sticky="ew")
        self.vruler = tk.Canvas(
            wrap, width=RULER_SIZE, bg=RULER_BG, highlightthickness=0, bd=0
        )
        self.vruler.grid(row=1, column=0, sticky="ns")

        self.view_canvas = tk.Canvas(
            wrap, bg=BG, highlightthickness=0, bd=0
        )
        self.view_canvas.grid(row=1, column=1, sticky="nsew")
        self.vbar = tk.Scrollbar(
            wrap,
            orient="vertical",
            command=self.view_canvas.yview,
            bg=BORDER,
            troughcolor=BG,
            activebackground=HOVER_BG,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.vbar.grid(row=1, column=2, sticky="ns")
        self.hbar = tk.Scrollbar(
            wrap,
            orient="horizontal",
            command=self.view_canvas.xview,
            bg=BORDER,
            troughcolor=BG,
            activebackground=HOVER_BG,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.hbar.grid(row=2, column=1, sticky="ew")
        self.vbar.grid_remove()
        self.hbar.grid_remove()

        self.doc_canvas = tk.Canvas(
            self.view_canvas,
            width=self.content_width,
            height=self.content_height,
            bg=DOC_BG,
            highlightthickness=1,
            highlightbackground="#475569",
            cursor="pencil",
        )
        self._doc_window = self.view_canvas.create_window(
            0, 0, window=self.doc_canvas, anchor="nw"
        )
        self.view_canvas.configure(
            yscrollcommand=self._on_view_yscroll,
            xscrollcommand=self._on_view_xscroll,
        )

        self.view_canvas.bind("<Configure>", self._layout_content_viewport)
        for ruler, orient in ((self.hruler, "h"), (self.vruler, "v")):
            ruler.bind(
                "<ButtonPress-1>",
                lambda event, o=orient: self._start_guide_drag(o, event),
            )
            ruler.bind("<B1-Motion>", self._drag_guide)
            ruler.bind("<ButtonRelease-1>", self._finish_guide_drag)
        for widget in (self.view_canvas, self.doc_canvas):
            widget.bind("<MouseWheel>", self._on_doc_mousewheel)
            widget.bind("<Shift-MouseWheel>", self._on_doc_mousewheel)

        self.doc_canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.doc_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.doc_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.doc_canvas.bind("<Motion>", self._on_canvas_motion)
        self.doc_canvas.bind("<Leave>", self._on_canvas_leave)
        self.doc_canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.after_idle(self._layout_content_viewport)

        self.help_panel = tk.Frame(workspace, bg=BG)
        self.help_panel.grid(
            row=1, column=0, sticky="nsew", padx=32, pady=(10, 26)
        )
        self.help_panel.grid_columnconfigure(0, weight=1)
        self.help_panel.grid_rowconfigure(0, weight=1)

        card = tk.Frame(self.help_panel, bg=PANEL_BG, padx=28, pady=22)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        tk.Label(
            card,
            text="Hướng dẫn phím tắt",
            font=self.font_brand,
            fg=TEXT,
            bg=PANEL_BG,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            card,
            text="Nhấn F1 để mở hoặc đóng tab này.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(4, 18))

        table = tk.Frame(card, bg=PANEL_BG)
        table.grid(row=2, column=0, sticky="nw")
        for row, (keys, description) in enumerate(SHORTCUTS):
            tk.Label(
                table,
                text=keys,
                font=("Consolas", 10, "bold"),
                fg=TEXT,
                bg="#0b1220",
                anchor="w",
                width=18,
                padx=10,
                pady=3,
            ).grid(row=row, column=0, sticky="w", pady=3)
            tk.Label(
                table,
                text=description,
                font=self.font_layer,
                fg=MUTED,
                bg=PANEL_BG,
                anchor="w",
            ).grid(row=row, column=1, sticky="w", padx=(16, 0), pady=3)
        self.help_panel.grid_remove()

    def _show_help_tab(self, _event=None):
        if self.help_visible:
            return
        self._commit_text_editor()
        self.help_visible = True
        self.workspace_wrap.grid_remove()
        self.help_panel.grid()
        self.help_tab_label.configure(fg=TEXT, bg=HOVER_BG)
        self.doc_tab_label.configure(fg=MUTED)
        self.update_idletasks()
        self._layout_content_viewport()

    def _hide_help_tab(self, _event=None):
        if not self.help_visible:
            return
        self.help_visible = False
        self.help_panel.grid_remove()
        self.workspace_wrap.grid()
        self.help_tab_label.configure(fg=MUTED, bg=PANEL_BG)
        self.doc_tab_label.configure(fg=TEXT)
        self.update_idletasks()
        self._layout_content_viewport()

    def _toggle_help_tab(self, _event=None):
        if self.help_visible:
            self._hide_help_tab()
        else:
            self._show_help_tab()

    def _page_pixel_size(self):
        return (
            max(round(self.content_width * self.zoom), 1),
            max(round(self.content_height * self.zoom), 1),
        )

    def _page_background(self):
        value = getattr(self, "content_background", "white")
        return value if value in PAGE_BACKGROUNDS else "white"

    def _layout_content_viewport(self, _event=None):
        if not (
            self.view_canvas.winfo_exists()
            and self.hruler.winfo_exists()
            and self.vruler.winfo_exists()
        ):
            return
        view_w = max(self.view_canvas.winfo_width(), 1)
        view_h = max(self.view_canvas.winfo_height(), 1)
        page_w, page_h = self._page_pixel_size()
        pad = 16
        bar = 16
        need_h = page_w > view_w
        need_v = page_h > view_h
        if need_h and page_h > view_h - bar:
            need_v = True
        if need_v and page_w > view_w - bar:
            need_h = True

        if need_v:
            self.vbar.grid()
        else:
            self.vbar.grid_remove()
        if need_h:
            self.hbar.grid()
        else:
            self.hbar.grid_remove()

        avail_w = max(view_w - (bar if need_v else 0), 1)
        avail_h = max(view_h - (bar if need_h else 0), 1)
        x = pad if page_w > avail_w else (avail_w - page_w) // 2
        y = pad if page_h > avail_h else (avail_h - page_h) // 2
        self.view_canvas.coords(self._doc_window, max(x, 0), max(y, 0))
        self.view_canvas.configure(
            scrollregion=(
                0,
                0,
                page_w + pad * 2 if page_w > avail_w else avail_w,
                page_h + pad * 2 if page_h > avail_h else avail_h,
            )
        )
        self._draw_rulers()

    def _on_view_xscroll(self, first, last):
        self.hbar.set(first, last)
        self._draw_hruler()

    def _on_view_yscroll(self, first, last):
        self.vbar.set(first, last)
        self._draw_vruler()

    def _draw_rulers(self):
        if self._doc_window is None:
            return
        doc_x, doc_y = self.view_canvas.coords(self._doc_window)
        self._draw_hruler(doc_x + 1 - self.view_canvas.canvasx(0))
        self._draw_vruler(doc_y + 1 - self.view_canvas.canvasy(0))

    def _ruler_minor_step(self):
        for step in RULER_STEPS:
            if step * self.zoom >= 6:
                return step
        return RULER_STEPS[-1]

    def _draw_hruler(self, origin=None):
        ruler = self.hruler
        ruler.delete("all")
        width = ruler.winfo_width()
        if width <= 1:
            return
        if origin is None:
            doc_x = self.view_canvas.coords(self._doc_window)[0]
            origin = doc_x + 1 - self.view_canvas.canvasx(0)
        height = RULER_SIZE
        zoom = self.zoom
        step = self._ruler_minor_step()
        major = step * 10
        page_end = origin + self.content_width * zoom
        if page_end > 0 and origin < width:
            ruler.create_rectangle(
                max(origin, 0),
                height - 3,
                min(page_end, width),
                height,
                fill=ACCENT,
                outline="",
            )
        start = int((0 - origin) // (step * zoom)) * step
        end = int((width - origin) // (step * zoom)) * step
        for value in range(
            max(start, 0), min(end, self.content_width) + 1, step
        ):
            x = origin + value * zoom
            if value % major == 0:
                length = 10
                ruler.create_text(
                    x + 3,
                    2,
                    text=str(value),
                    anchor="nw",
                    fill=MUTED,
                    font=("Segoe UI", 7),
                )
            elif value % (major // 2) == 0:
                length = 7
            else:
                length = 4
            ruler.create_line(
                x, height - length, x, height, fill=RULER_TICK
            )

    def _draw_vruler(self, origin=None):
        ruler = self.vruler
        ruler.delete("all")
        height = ruler.winfo_height()
        if height <= 1:
            return
        if origin is None:
            doc_y = self.view_canvas.coords(self._doc_window)[1]
            origin = doc_y + 1 - self.view_canvas.canvasy(0)
        width = RULER_SIZE
        zoom = self.zoom
        step = self._ruler_minor_step()
        major = step * 10
        page_end = origin + self.content_height * zoom
        if page_end > 0 and origin < height:
            ruler.create_rectangle(
                width - 3,
                max(origin, 0),
                width,
                min(page_end, height),
                fill=ACCENT,
                outline="",
            )
        start = int((0 - origin) // (step * zoom)) * step
        end = int((height - origin) // (step * zoom)) * step
        for value in range(
            max(start, 0), min(end, self.content_height) + 1, step
        ):
            y = origin + value * zoom
            if value % major == 0:
                length = 10
                ruler.create_text(
                    width // 2 - 3,
                    y,
                    text=str(value),
                    angle=90,
                    anchor="center",
                    fill=MUTED,
                    font=("Segoe UI", 7),
                )
            elif value % (major // 2) == 0:
                length = 7
            else:
                length = 4
            ruler.create_line(
                width - length, y, width, y, fill=RULER_TICK
            )

    def _start_guide_drag(self, orient, event):
        self._commit_text_editor()
        self._guide_drag = orient
        if not self.guides_visible:
            self.guides_visible = True
            self._draw_guides()
        self._update_guide_preview(event)

    def _drag_guide(self, event):
        self._update_guide_preview(event)

    def _finish_guide_drag(self, event):
        self.doc_canvas.delete("guide_preview")
        orient = self._guide_drag
        self._guide_drag = None
        if orient is None:
            return
        pos = self._guide_pos_from_event(orient, event)
        if pos is None:
            return
        self.guides.append({"orient": orient, "pos": pos})
        self._draw_guides()
        self._refresh_doc_tab()

    def _guide_pos_from_event(self, orient, event):
        if orient == "h":
            view_x = event.x
            view_y = event.y - RULER_SIZE
        else:
            view_x = event.x - RULER_SIZE
            view_y = event.y
        doc_x, doc_y = self.view_canvas.coords(self._doc_window)
        x = (self.view_canvas.canvasx(view_x) - (doc_x + 1)) / self.zoom
        y = (self.view_canvas.canvasy(view_y) - (doc_y + 1)) / self.zoom
        pos, limit = (
            (y, self.content_height)
            if orient == "h"
            else (x, self.content_width)
        )
        if 0 <= pos <= limit:
            return round(pos)
        return None

    def _update_guide_preview(self, event):
        if self._guide_drag is None:
            return
        self.doc_canvas.delete("guide_preview")
        pos = self._guide_pos_from_event(self._guide_drag, event)
        if pos is None:
            return
        self._create_guide_line(self._guide_drag, pos, "guide_preview")
        self.doc_canvas.tag_raise("guide_preview")

    def _create_guide_line(self, orient, pos, tag):
        options = {
            "fill": GUIDE_COLOR,
            "width": 1,
            "tags": tag,
        }
        if tag == "guide_preview":
            options["dash"] = (4, 3)
        zoom = self.zoom
        page_w, page_h = self._page_pixel_size()
        if orient == "h":
            self.doc_canvas.create_line(
                0, pos * zoom, page_w, pos * zoom, **options
            )
        else:
            self.doc_canvas.create_line(
                pos * zoom, 0, pos * zoom, page_h, **options
            )

    def _draw_guides(self):
        self.doc_canvas.delete("guide")
        if not self.guides_visible:
            return
        for guide in self.guides:
            self._create_guide_line(
                guide["orient"], guide["pos"], "guide"
            )

    def _toggle_guides(self, _event=None):
        self.guides_visible = not self.guides_visible
        self._draw_guides()
        if not self.guides_visible:
            self.doc_canvas.configure(cursor="pencil")
        return "break"

    def _guide_at(self, x, y, tolerance=4):
        if not self.guides_visible:
            return None
        found = None
        best = tolerance + 1
        for guide in self.guides:
            distance = abs(
                (y if guide["orient"] == "h" else x) - guide["pos"]
            )
            if distance <= tolerance and distance < best:
                found = guide
                best = distance
        return found

    def _guide_cursor(self, guide):
        if guide is None:
            return "pencil"
        return (
            "sb_v_double_arrow"
            if guide["orient"] == "h"
            else "sb_h_double_arrow"
        )

    def _on_canvas_motion(self, event):
        event = _DocEvent(event, self.zoom)
        guide = (
            self._guide_at(event.x, event.y)
            if self.active_tool_id == "move"
            else None
        )
        cursor = self._guide_cursor(guide)
        if self.doc_canvas.cget("cursor") != cursor:
            self.doc_canvas.configure(cursor=cursor)

    def _on_canvas_leave(self, _event=None):
        if self._moving_guide is not None:
            return
        self.doc_canvas.configure(cursor="pencil")

    def _move_guide_to(self, pos):
        guide = self._moving_guide
        limit = (
            self.content_height
            if guide["orient"] == "h"
            else self.content_width
        )
        guide["pos"] = round(max(0, min(pos, limit)))
        self._draw_guides()

    def _on_doc_mousewheel(self, event):
        if event.state & 0x0004:
            if event.delta:
                self._zoom_by(1 if event.delta > 0 else -1, event)
            return "break"
        step = -1 if event.delta > 0 else 1
        if event.state & 0x0001:
            self.view_canvas.xview_scroll(step, "units")
        else:
            self.view_canvas.yview_scroll(step, "units")
        return "break"

    def _zoom_anchor(self):
        view = self.view_canvas
        vx = view.winfo_pointerx() - view.winfo_rootx()
        vy = view.winfo_pointery() - view.winfo_rooty()
        if not (0 <= vx < view.winfo_width() and 0 <= vy < view.winfo_height()):
            return None
        doc_x, doc_y = view.coords(self._doc_window)
        return (
            vx,
            vy,
            (view.canvasx(vx) - (doc_x + 1)) / self.zoom,
            (view.canvasy(vy) - (doc_y + 1)) / self.zoom,
        )

    def _restore_zoom_anchor(self, anchor):
        if anchor is None:
            return
        vx, vy, doc_x_units, doc_y_units = anchor
        view = self.view_canvas
        view.update_idletasks()
        page_w, page_h = self._page_pixel_size()
        doc_x, doc_y = view.coords(self._doc_window)
        if page_w > view.winfo_width():
            target = doc_x + 1 + doc_x_units * self.zoom - vx
            span = max(page_w + 32 - view.winfo_width(), 1)
            view.xview_moveto(max(0.0, min(1.0, target / span)))
        if page_h > view.winfo_height():
            target = doc_y + 1 + doc_y_units * self.zoom - vy
            span = max(page_h + 32 - view.winfo_height(), 1)
            view.yview_moveto(max(0.0, min(1.0, target / span)))

    def _zoom_by(self, direction, event=None):
        try:
            index = ZOOM_STEPS.index(self.zoom)
        except ValueError:
            index = min(
                range(len(ZOOM_STEPS)),
                key=lambda i: abs(ZOOM_STEPS[i] - self.zoom),
            )
        index = max(0, min(len(ZOOM_STEPS) - 1, index + direction))
        zoom = ZOOM_STEPS[index]
        if zoom == self.zoom:
            return "break"
        if self._text_editor is not None:
            self._commit_text_editor()
        anchor = self._zoom_anchor()
        self.zoom = zoom
        self.doc_canvas.configure(
            width=self._page_pixel_size()[0],
            height=self._page_pixel_size()[1],
        )
        self._render_document()
        self._layout_content_viewport()
        self._restore_zoom_anchor(anchor)
        self._update_status()
        return "break"

    def _update_content_size_label(self):
        label = (
            f"Kích thước nội dung: "
            f"{self.content_width} × {self.content_height}"
        )
        if self.content_full:
            label += " (Full)"
        self.content_size_button.configure(text=label)

    def _set_content_size(self, width, height):
        self.content_width = width
        self.content_height = height
        self.guides = [
            guide
            for guide in self.guides
            if 0
            <= guide["pos"]
            <= (
                self.content_height
                if guide["orient"] == "h"
                else self.content_width
            )
        ]
        self.doc_canvas.configure(
            width=self._page_pixel_size()[0],
            height=self._page_pixel_size()[1],
        )
        self._draw_guides()
        self._layout_content_viewport()
        self._update_content_size_label()
        self._refresh_doc_tab()

    def _open_content_size_dialog(self):
        self._commit_text_editor()
        window = self._content_size_window
        if window is not None and window.winfo_exists():
            window.lift()
            window.focus_force()
            return

        window = tk.Toplevel(self)
        self._content_size_window = window
        window.title("Kích thước nội dung")
        window.configure(bg=PANEL_BG)
        window.resizable(False, False)
        window.transient(self)
        window.protocol(
            "WM_DELETE_WINDOW",
            lambda: self._close_content_size_dialog(window),
        )
        window.bind(
            "<Escape>", lambda _e: self._close_content_size_dialog(window)
        )

        body = tk.Frame(window, bg=PANEL_BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Kích thước nội dung",
            font=self.font_brand,
            fg=TEXT,
            bg=PANEL_BG,
        ).pack(anchor="w")
        tk.Label(
            body,
            text="Kích thước khung thiết kế, tính bằng pixel.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
        ).pack(anchor="w", pady=(4, 14))

        form = tk.Frame(body, bg=PANEL_BG)
        form.pack(fill="x")
        form.grid_columnconfigure(1, weight=1)

        entries = {}
        full_var = tk.BooleanVar(window, value=self.content_full)
        background_var = tk.StringVar(window, value=self._page_background())
        for row, (key, title, value) in enumerate(
            (
                ("width", "Chiều rộng", self.content_width),
                ("height", "Chiều cao", self.content_height),
            )
        ):
            tk.Label(
                form,
                text=title,
                font=("Segoe UI", 10),
                fg=TEXT,
                bg=PANEL_BG,
                anchor="w",
            ).grid(row=row, column=0, sticky="w", pady=4)
            entry = self._make_info_entry(form, width=8)
            entry.configure(justify="center", font=self.font_layer)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, sticky="e", pady=4)
            tk.Label(
                form,
                text="px",
                font=("Segoe UI", 9),
                fg=MUTED,
                bg=PANEL_BG,
            ).grid(row=row, column=2, sticky="w", padx=(6, 0))
            entry.bind(
                "<Return>",
                lambda _e: self._apply_content_size(
                    window,
                    entries["width"],
                    entries["height"],
                    full_var,
                    background_var,
                ),
            )
            entries[key] = entry

        tk.Label(
            form,
            text="Nền trang",
            font=("Segoe UI", 10),
            fg=TEXT,
            bg=PANEL_BG,
            anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=(12, 0))
        background_row = tk.Frame(form, bg=PANEL_BG)
        background_row.grid(
            row=2, column=1, columnspan=2, sticky="e", pady=(12, 0)
        )
        for value, title in (("white", "Trắng"), ("none", "Không nền")):
            tk.Radiobutton(
                background_row,
                text=title,
                value=value,
                variable=background_var,
                font=("Segoe UI", 10),
                fg=TEXT,
                bg=PANEL_BG,
                activebackground=PANEL_BG,
                activeforeground=TEXT,
                selectcolor="#0b1220",
                highlightthickness=0,
                bd=0,
                anchor="w",
                cursor="hand2",
            ).pack(side="left", padx=(10, 0))

        tk.Checkbutton(
            form,
            text="Full",
            variable=full_var,
            font=("Segoe UI", 10),
            fg=TEXT,
            bg=PANEL_BG,
            activebackground=PANEL_BG,
            activeforeground=TEXT,
            selectcolor="#0b1220",
            highlightthickness=0,
            bd=0,
            anchor="w",
            cursor="hand2",
        ).grid(row=3, column=0, sticky="w", pady=(10, 0))
        tk.Label(
            form,
            text="Body full — không đặt width/height khi xuất HTML.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="w",
        ).grid(
            row=3, column=1, columnspan=2, sticky="w", pady=(10, 0)
        )

        actions = tk.Frame(body, bg=PANEL_BG)
        actions.pack(fill="x", pady=(16, 0))

        tk.Button(
            actions,
            text="Hủy",
            command=lambda: self._close_content_size_dialog(window),
            font=self.font_menu,
            fg=TEXT,
            bg=BORDER,
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="right")

        tk.Button(
            actions,
            text="Áp dụng",
            command=lambda: self._apply_content_size(
                window,
                entries["width"],
                entries["height"],
                full_var,
                background_var,
            ),
            font=self.font_menu,
            fg=BG,
            bg=ACCENT,
            activebackground="#60a5fa",
            activeforeground=BG,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="right", padx=(0, 8))

        window.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width() - width) // 2
        y = self.winfo_rooty() + (self.winfo_height() - height) // 3
        window.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        entries["width"].focus_set()
        entries["width"].select_range(0, "end")

    def _apply_content_size(
        self, window, width_entry, height_entry, full_var, background_var
    ):
        try:
            width = int(width_entry.get().strip())
            height = int(height_entry.get().strip())
        except ValueError:
            messagebox.showwarning(
                "Kích thước nội dung",
                "Vui lòng nhập số nguyên cho chiều rộng và chiều cao.",
                parent=window,
            )
            return
        if not (
            100 <= width <= 6000
            and 100 <= height <= 6000
        ):
            messagebox.showwarning(
                "Kích thước nội dung",
                "Chiều rộng và chiều cao phải trong khoảng 100–6000 px.",
                parent=window,
            )
            return
        self._close_content_size_dialog(window)
        self.content_full = bool(full_var.get())
        background = background_var.get()
        self.content_background = (
            background if background in PAGE_BACKGROUNDS else "white"
        )
        self._set_content_size(width, height)
        self._render_document()

    def _close_content_size_dialog(self, window):
        if window is not None and window.winfo_exists():
            window.destroy()
        if self._content_size_window is window:
            self._content_size_window = None

    def _build_layer_panel(self):
        panel = tk.Frame(self, bg=PANEL_BG, width=LAYER_PANEL_WIDTH)
        panel.grid(row=1, column=2, sticky="ns")
        panel.grid_propagate(False)
        panel.pack_propagate(False)

        border = tk.Frame(panel, bg=BORDER, width=1)
        border.pack(side="left", fill="y")

        inner = tk.Frame(panel, bg=PANEL_BG)
        inner.pack(side="left", fill="both", expand=True)

        self._build_page_section(inner)
        self._build_info_section(inner)

        header = tk.Frame(inner, bg=PANEL_BG)
        header.pack(fill="x", padx=14, pady=(12, 8))

        tk.Label(
            header,
            text="LỚP",
            font=self.font_panel,
            fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left")

        self._make_panel_button(header, "−", self._delete_layer).pack(
            side="right", padx=(2, 0)
        )
        self._make_panel_button(header, "+", self._add_layer).pack(side="right")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=12)

        self.layer_list_canvas = tk.Canvas(
            inner,
            bg=PANEL_BG,
            highlightthickness=0,
            bd=0,
            yscrollincrement=20,
        )
        self.layer_list_canvas.pack(
            fill="both", expand=True, padx=6, pady=6
        )
        self.layer_list = tk.Frame(self.layer_list_canvas, bg=PANEL_BG)
        self._layer_list_window = self.layer_list_canvas.create_window(
            (0, 0), window=self.layer_list, anchor="nw"
        )
        for widget in (
            self.layer_list_canvas,
            self.layer_list,
        ):
            widget.bind("<MouseWheel>", self._on_layer_mousewheel)
            widget.bind(
                "<Configure>", lambda _e: self._sync_layer_list_scroll()
            )
        self.after_idle(self._sync_layer_list_scroll)

        self.layer_count_label = tk.Label(
            inner,
            text="",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="w",
            padx=16,
            pady=8,
        )
        self.layer_count_label.pack(fill="x", side="bottom")

    def _sync_layer_list_scroll(self):
        canvas = self.layer_list_canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        content_height = max(self.layer_list.winfo_reqheight(), height)
        canvas.itemconfigure(
            self._layer_list_window, width=width, height=content_height
        )
        canvas.configure(scrollregion=(0, 0, width, content_height))

    def _on_layer_mousewheel(self, event):
        delta = int(event.delta / 120)
        if delta:
            self.layer_list_canvas.yview_scroll(-delta * 2, "units")
        return "break"

    def _build_page_section(self, parent):
        header = tk.Frame(parent, bg=PANEL_BG)
        header.pack(fill="x", padx=14, pady=(14, 8))
        tk.Label(
            header,
            text="TRANG",
            font=self.font_panel,
            fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left")
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=12)

        body = tk.Frame(parent, bg=PANEL_BG)
        body.pack(fill="x", padx=14, pady=(8, 10))
        body.grid_columnconfigure(1, weight=1)

        self._info_label(body, 0, "Font chữ body")
        holder = tk.Frame(body, bg=PANEL_BG)
        holder.grid(row=0, column=1, sticky="ew", pady=2)
        self.body_font_family_var = tk.StringVar(value=self.body_font_family)
        self.body_font_family_entry = self._make_info_entry(holder, width=1)
        self.body_font_family_entry.configure(
            textvariable=self.body_font_family_var,
            justify="left",
        )
        self.body_font_family_entry.pack(side="left", fill="x", expand=True)
        self.body_font_family_arrow = tk.Label(
            holder,
            text="▾",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg="#0b1220",
            padx=5,
            cursor="hand2",
        )
        self.body_font_family_arrow.pack(side="left", fill="y")
        self.body_font_family_entry.bind(
            "<FocusIn>",
            lambda _e: self._set_font_entry_active(
                self.body_font_family_entry
            ),
        )
        self.body_font_family_entry.bind(
            "<KeyRelease>",
            lambda event: self._update_font_suggestions(
                event, self.body_font_family_entry
            ),
        )
        self.body_font_family_entry.bind(
            "<Return>",
            lambda event: self._apply_font_field(
                event, self.body_font_family_entry
            ),
        )
        self.body_font_family_entry.bind("<Down>", self._font_suggest_down)
        self.body_font_family_entry.bind("<Up>", self._font_suggest_up)
        self.body_font_family_entry.bind(
            "<Escape>", self._hide_font_suggestions
        )
        self.body_font_family_entry.bind(
            "<FocusOut>", self._on_font_focus_out
        )
        self.body_font_family_arrow.bind(
            "<ButtonPress-1>",
            lambda _e: self._toggle_font_suggestions(
                entry=self.body_font_family_entry
            ),
        )

    def _build_info_section(self, parent):
        header = tk.Frame(parent, bg=PANEL_BG)
        header.pack(fill="x", padx=14, pady=(14, 8))
        self.info_header = header
        self.info_chevron = tk.Label(
            header,
            text="▾",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            padx=4,
            cursor="hand2",
        )
        self.info_chevron.pack(side="left")
        self.info_title = tk.Label(
            header,
            text="THÔNG TIN HÌNH",
            font=self.font_panel,
            fg=MUTED,
            bg=PANEL_BG,
            cursor="hand2",
        )
        self.info_title.pack(side="left")
        self.info_pin = tk.Canvas(
            header,
            width=18,
            height=18,
            bg=PANEL_BG,
            highlightthickness=0,
            cursor="hand2",
        )
        self.info_pin.pack(side="right")
        self._draw_info_pin()
        for widget in (self.info_chevron, self.info_title):
            widget.bind("<Button-1>", self._toggle_info_section)
        self.info_pin.bind("<Button-1>", self._toggle_info_pin)
        Tooltip(self.info_pin, "Ghim: luôn mở phần thông tin")

        self.info_content = tk.Frame(parent, bg=PANEL_BG)
        self.info_content.pack(fill="x")
        tk.Frame(self.info_content, bg=BORDER, height=1).pack(
            fill="x", padx=12
        )

        position = tk.Frame(self.info_content, bg=PANEL_BG)
        position.pack(fill="x", padx=14, pady=(8, 0))
        position.grid_columnconfigure(1, weight=1)
        self.info_position_label = self._info_label(position, 0, "Tọa độ")
        position_holder = tk.Frame(position, bg=PANEL_BG)
        position_holder.grid(row=0, column=1, sticky="e", pady=2)
        self.info_position_rows = (self.info_position_label, position_holder)
        tk.Label(
            position_holder, text="X", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left")
        self.info_position_x = self._make_info_entry(position_holder, width=5)
        self.info_position_x.pack(side="left", padx=(4, 8))
        tk.Label(
            position_holder, text="Y", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left")
        self.info_position_y = self._make_info_entry(position_holder, width=5)
        self.info_position_y.pack(side="left", padx=(4, 0))
        tk.Label(
            position_holder, text="px", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))
        for entry in (self.info_position_x, self.info_position_y):
            entry.bind("<Return>", self._apply_layer_position)
            entry.bind("<FocusOut>", self._apply_layer_position)
        self.info_position_tip = Tooltip(
            self.info_position_label,
            "Nhập X/Y để di chuyển layer — mốc: canvas",
        )

        body = tk.Frame(self.info_content, bg=PANEL_BG)
        body.pack(fill="x", padx=14, pady=(6, 10))
        body.grid_columnconfigure(1, weight=1)

        self.info_shape_rows = []
        self.info_text_rows = []

        label = self._info_label(body, 0, "Kích thước")
        size_holder = tk.Frame(body, bg=PANEL_BG)
        size_holder.grid(row=0, column=1, sticky="e", pady=2)
        self.info_shape_rows.extend((label, size_holder))
        self.info_width_entry = self._make_info_entry(size_holder)
        self.info_width_entry.pack(side="left")
        tk.Label(
            size_holder, text="×", font=("Segoe UI", 9), fg=MUTED, bg=PANEL_BG,
            padx=4,
        ).pack(side="left")
        self.info_height_entry = self._make_info_entry(size_holder)
        self.info_height_entry.pack(side="left")
        tk.Label(
            size_holder, text="px", font=("Segoe UI", 9), fg=MUTED, bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))

        label = self._info_label(body, 1, "Độ dày viền")
        border_holder = tk.Frame(body, bg=PANEL_BG)
        border_holder.grid(row=1, column=1, sticky="e", pady=2)
        self.info_shape_rows.extend((label, border_holder))
        self.info_border_entry = self._make_info_entry(border_holder)
        self.info_border_entry.pack(side="left")
        tk.Label(
            border_holder, text="px", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))

        label = self._info_label(body, 2, "Màu viền")
        border_color_holder = tk.Frame(body, bg=PANEL_BG)
        border_color_holder.grid(row=2, column=1, sticky="e", pady=2)
        self.info_shape_rows.extend((label, border_color_holder))
        self.info_border_swatch = tk.Canvas(
            border_color_holder, width=14, height=14, bg=PANEL_BG,
            highlightthickness=0, cursor="hand2",
        )
        self.info_border_swatch.pack(side="left")
        self.info_border_color_entry = self._make_info_entry(
            border_color_holder, width=8
        )
        self.info_border_color_entry.pack(side="left", padx=(6, 0))
        self.info_border_swatch.bind("<Button-1>", self._choose_border_color)
        self.info_border_color_entry.bind(
            "<Return>", self._apply_border_color_text
        )
        self.info_border_color_entry.bind(
            "<FocusOut>", self._apply_border_color_text
        )

        label = self._info_label(body, 3, "Nền")
        bg_holder = tk.Frame(body, bg=PANEL_BG)
        bg_holder.grid(row=3, column=1, sticky="e", pady=2)
        self.info_shape_rows.extend((label, bg_holder))
        self.info_bg_swatch = tk.Canvas(
            bg_holder, width=14, height=14, bg=PANEL_BG,
            highlightthickness=0, cursor="hand2",
        )
        self.info_bg_swatch.pack(side="left")
        self.info_bg_entry = self._make_info_entry(bg_holder, width=8)
        self.info_bg_entry.pack(side="left", padx=(6, 0))
        self.info_bg_clear = tk.Label(
            bg_holder, text="×", font=("Segoe UI", 9, "bold"), fg=MUTED,
            bg=PANEL_BG, cursor="hand2", padx=4,
        )
        self.info_bg_clear.pack(side="left")
        self.info_bg_swatch.bind("<Button-1>", self._choose_background_color)
        self.info_bg_entry.bind("<Return>", self._apply_background_text)
        self.info_bg_entry.bind("<FocusOut>", self._apply_background_text)
        self.info_bg_clear.bind("<Button-1>", self._clear_background)
        self.info_bg_clear.bind(
            "<Enter>", lambda _e: self.info_bg_clear.configure(fg=TEXT)
        )
        self.info_bg_clear.bind(
            "<Leave>",
            lambda _e: self.info_bg_clear.configure(
                fg=TEXT if self._active_rect() and self._active_rect().get("background")
                else MUTED
            ),
        )

        label = self._info_label(body, 4, "Ảnh nền")
        bg_image_holder = tk.Frame(body, bg=PANEL_BG)
        bg_image_holder.grid(row=4, column=1, sticky="e", pady=2)
        self.info_shape_rows.extend((label, bg_image_holder))
        self.info_bg_image_rows = (label, bg_image_holder)
        self.info_bg_image_name = tk.Label(
            bg_image_holder,
            text="Chọn ảnh",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg="#0b1220",
            anchor="w",
            padx=6,
            pady=2,
            width=14,
            cursor="hand2",
        )
        self.info_bg_image_name.pack(side="left")
        self.info_bg_image_clear = tk.Label(
            bg_image_holder, text="×", font=("Segoe UI", 9, "bold"),
            fg=MUTED, bg=PANEL_BG, cursor="hand2", padx=4,
        )
        self.info_bg_image_clear.pack(side="left")
        self.info_bg_image_name.bind(
            "<Button-1>", self._choose_layer_background_image
        )
        self.info_bg_image_clear.bind(
            "<Button-1>", self._clear_layer_background_image
        )
        for button in (self.info_bg_image_name, self.info_bg_image_clear):
            button.bind(
                "<Enter>", lambda _e, w=button: w.configure(fg=TEXT)
            )
            button.bind(
                "<Leave>",
                lambda _e: self._refresh_bg_image_row(self.active_layer),
            )

        self.info_bg_option_rows = []
        self.info_bg_size_var = tk.StringVar(value="cover")
        self.info_bg_position_var = tk.StringVar(value="center")
        self.info_bg_repeat_var = tk.StringVar(value="no-repeat")
        for row, title, key, variable, values in (
            (5, "Cỡ nền", "size", self.info_bg_size_var,
             ("cover", "contain")),
            (6, "Vị trí", "position", self.info_bg_position_var,
             ("center", "top", "left", "right")),
            (7, "Lặp nền", "repeat", self.info_bg_repeat_var,
             ("repeat", "no-repeat")),
        ):
            label = self._info_label(body, row, title)
            holder = tk.Frame(body, bg=PANEL_BG)
            holder.grid(row=row, column=1, sticky="e", pady=2)
            menu = self._make_info_menu(
                holder,
                variable,
                values,
                lambda value, key=key: self._apply_layer_background_option(
                    key, value
                ),
            )
            menu.pack(side="left")
            label.grid_remove()
            holder.grid_remove()
            self.info_bg_option_rows.extend((label, holder))

        label = self._info_label(body, 8, "Display")
        display_holder = tk.Frame(body, bg=PANEL_BG)
        display_holder.grid(row=8, column=1, sticky="e", pady=2)
        self.info_group_rows = (label, display_holder)
        self.info_group_display_var = tk.StringVar(value="block")
        self.info_group_display_menu = self._make_info_menu(
            display_holder,
            self.info_group_display_var,
            GROUP_DISPLAYS,
            self._apply_layer_display,
        )
        self.info_group_display_menu.pack(side="left")
        label.grid_remove()
        display_holder.grid_remove()

        label = self._info_label(body, 9, "Canh lề")
        align_holder = tk.Frame(body, bg=PANEL_BG)
        align_holder.grid(row=9, column=1, sticky="e", pady=2)
        self.info_group_align_rows = (label, align_holder)
        self.info_group_align_var = tk.StringVar(value="left")
        for value, text in (
            ("left", "Trái"),
            ("center", "Giữa"),
            ("right", "Phải"),
        ):
            button = tk.Radiobutton(
                align_holder,
                text=text,
                value=value,
                variable=self.info_group_align_var,
                command=lambda value=value: self._apply_group_align(value),
                indicatoron=False,
                font=("Segoe UI", 9),
                fg=TEXT,
                bg="#0b1220",
                activebackground=HOVER_BG,
                activeforeground=TEXT,
                selectcolor=ACCENT,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=BORDER,
                padx=4,
                pady=2,
                width=4,
                cursor="hand2",
            )
            button.pack(side="left", padx=(0, 2))
        label.grid_remove()
        align_holder.grid_remove()

        label = self._info_label(body, 10, "Justify")
        justify_holder = tk.Frame(body, bg=PANEL_BG)
        justify_holder.grid(row=10, column=1, sticky="e", pady=2)
        self.info_group_justify_rows = (label, justify_holder)
        self.info_group_justify_var = tk.StringVar(value="left")
        self.info_group_justify_menu = self._make_info_menu(
            justify_holder,
            self.info_group_justify_var,
            GROUP_JUSTIFIES,
            self._apply_group_justify,
        )
        self.info_group_justify_menu.pack(side="left")
        label.grid_remove()
        justify_holder.grid_remove()

        label = self._info_label(body, 11, "Gap")
        gap_holder = tk.Frame(body, bg=PANEL_BG)
        gap_holder.grid(row=11, column=1, sticky="e", pady=2)
        self.info_group_gap_rows = (label, gap_holder)
        self.info_group_gap_entry = self._make_info_entry(gap_holder)
        self.info_group_gap_entry.pack(side="left")
        tk.Label(
            gap_holder, text="px", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))
        self.info_group_gap_entry.bind("<Return>", self._apply_group_gap)
        self.info_group_gap_entry.bind("<FocusOut>", self._apply_group_gap)
        label.grid_remove()
        gap_holder.grid_remove()

        for entry in (self.info_width_entry, self.info_height_entry):
            entry.bind("<Return>", self._apply_rect_size)
            entry.bind("<FocusOut>", self._apply_rect_size)
        self.info_border_entry.bind("<Return>", self._apply_border_width)
        self.info_border_entry.bind("<FocusOut>", self._apply_border_width)

        label = self._info_label(body, 0, "Font chữ")
        family_holder = tk.Frame(body, bg=PANEL_BG)
        family_holder.grid(row=0, column=1, sticky="ew", pady=2)
        self.info_text_rows.extend((label, family_holder))
        self.info_font_family_var = tk.StringVar(value="none")
        self.info_font_family_entry = self._make_info_entry(
            family_holder, width=1
        )
        self.info_font_family_entry.configure(
            textvariable=self.info_font_family_var,
            justify="left",
        )
        self.info_font_family_entry.pack(
            side="left", fill="x", expand=True
        )
        self.info_font_family_arrow = tk.Label(
            family_holder,
            text="▾",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg="#0b1220",
            padx=5,
            cursor="hand2",
        )
        self.info_font_family_arrow.pack(side="left", fill="y")
        self._font_families = ["none"] + sorted(
            {
                name
                for name in tkfont.families(self)
                if not name.startswith("@")
            },
            key=str.lower,
        )
        self._font_suggest = None
        self._font_suggest_list = None
        self._font_focus_after = None
        self.info_font_family_entry.bind(
            "<FocusIn>",
            lambda _e: self._set_font_entry_active(
                self.info_font_family_entry
            ),
        )
        self.info_font_family_entry.bind(
            "<KeyRelease>", self._update_font_suggestions
        )
        self.info_font_family_entry.bind("<Return>", self._apply_font_field)
        self.info_font_family_entry.bind("<Down>", self._font_suggest_down)
        self.info_font_family_entry.bind("<Up>", self._font_suggest_up)
        self.info_font_family_entry.bind(
            "<Escape>", self._hide_font_suggestions
        )
        self.info_font_family_entry.bind(
            "<FocusOut>", self._on_font_focus_out
        )
        self.info_font_family_arrow.bind(
            "<ButtonPress-1>", self._toggle_font_suggestions
        )

        label = self._info_label(body, 1, "Cỡ chữ")
        font_holder = tk.Frame(body, bg=PANEL_BG)
        font_holder.grid(row=1, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, font_holder))
        self.info_font_size_entry = self._make_info_entry(font_holder)
        self.info_font_size_entry.pack(side="left")
        tk.Label(
            font_holder, text="px", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))

        label = self._info_label(body, 2, "Màu chữ")
        text_color_holder = tk.Frame(body, bg=PANEL_BG)
        text_color_holder.grid(row=2, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, text_color_holder))
        self.info_text_swatch = tk.Canvas(
            text_color_holder, width=14, height=14, bg=PANEL_BG,
            highlightthickness=0, cursor="hand2",
        )
        self.info_text_swatch.pack(side="left")
        self.info_text_color_entry = self._make_info_entry(
            text_color_holder, width=8
        )
        self.info_text_color_entry.pack(side="left", padx=(6, 0))
        self.info_text_swatch.bind("<Button-1>", self._choose_text_color)
        self.info_text_color_entry.bind(
            "<Return>", self._apply_text_color_text
        )
        self.info_text_color_entry.bind(
            "<FocusOut>", self._apply_text_color_text
        )

        label = self._info_label(body, 3, "Độ đậm")
        weight_holder = tk.Frame(body, bg=PANEL_BG)
        weight_holder.grid(row=3, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, weight_holder))
        self.info_weight_var = tk.StringVar(value="400")
        self.info_weight_menu = tk.OptionMenu(
            weight_holder,
            self.info_weight_var,
            *[str(value) for value in range(100, 1000, 100)],
            command=lambda _value: self._apply_text_style(),
        )
        self.info_weight_menu.configure(
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            relief="flat",
            bd=0,
            width=6,
            anchor="center",
            cursor="hand2",
        )
        self.info_weight_menu["menu"].configure(
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            activebackground=ACCENT,
            activeforeground=BG,
            tearoff=0,
        )
        self.info_weight_menu.pack(side="left")

        label = self._info_label(body, 4, "Giãn dòng")
        line_holder = tk.Frame(body, bg=PANEL_BG)
        line_holder.grid(row=4, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, line_holder))
        self.info_line_height_entry = self._make_info_entry(line_holder)
        self.info_line_height_entry.pack(side="left")

        label = self._info_label(body, 5, "Giãn chữ")
        spacing_holder = tk.Frame(body, bg=PANEL_BG)
        spacing_holder.grid(row=5, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, spacing_holder))
        self.info_letter_spacing_entry = self._make_info_entry(spacing_holder)
        self.info_letter_spacing_entry.pack(side="left")
        tk.Label(
            spacing_holder, text="px", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))

        label = self._info_label(body, 6, "Chữ hoa")
        transform_holder = tk.Frame(body, bg=PANEL_BG)
        transform_holder.grid(row=6, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, transform_holder))
        self.info_transform_var = tk.StringVar(value="none")
        self.info_transform_menu = tk.OptionMenu(
            transform_holder,
            self.info_transform_var,
            *("none", "uppercase"),
            command=lambda _value: self._apply_text_style(),
        )
        self.info_transform_menu.configure(
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            relief="flat",
            bd=0,
            width=10,
            anchor="center",
            cursor="hand2",
        )
        self.info_transform_menu["menu"].configure(
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            activebackground=ACCENT,
            activeforeground=BG,
            tearoff=0,
        )
        self.info_transform_menu.pack(side="left")

        label = self._info_label(body, 7, "Canh lề")
        align_holder = tk.Frame(body, bg=PANEL_BG)
        align_holder.grid(row=7, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, align_holder))
        self.info_align_var = tk.StringVar(value="left")
        for value, text in (
            ("left", "Trái"),
            ("center", "Giữa"),
            ("right", "Phải"),
        ):
            button = tk.Radiobutton(
                align_holder,
                text=text,
                value=value,
                variable=self.info_align_var,
                indicatoron=False,
                font=("Segoe UI", 9),
                fg=TEXT,
                bg="#0b1220",
                activebackground=HOVER_BG,
                activeforeground=TEXT,
                selectcolor=ACCENT,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=BORDER,
                padx=4,
                pady=2,
                width=4,
                cursor="hand2",
            )
            button.bind(
                "<Button-1>",
                lambda _event, value=value: self._on_align_click(value),
            )
            button.bind("<ButtonRelease-1>", lambda _event: "break")
            button.pack(side="left", padx=(0, 2))

        label = self._info_label(body, 9, "Thẻ")
        tag_holder = tk.Frame(body, bg=PANEL_BG)
        tag_holder.grid(row=9, column=1, sticky="e", pady=2)
        self.info_text_rows.extend((label, tag_holder))
        self.info_tag_var = tk.StringVar(value="p")
        self.info_tag_menu = self._make_info_menu(
            tag_holder,
            self.info_tag_var,
            TEXT_TAGS,
            lambda _value: self._apply_text_style(),
            width=6,
        )
        self.info_tag_menu.pack(side="left")

        for entry in (self.info_font_size_entry,
                      self.info_line_height_entry,
                      self.info_letter_spacing_entry):
            entry.bind("<Return>", self._apply_text_style)
            entry.bind("<FocusOut>", self._apply_text_style)

        for widget in self.info_text_rows:
            widget.grid_remove()

        tk.Frame(self.info_content, bg=BORDER, height=1).pack(
            fill="x", padx=12
        )

    def _draw_info_pin(self):
        canvas = self.info_pin
        canvas.delete("all")
        color = ACCENT if self.info_pinned else MUTED
        canvas.create_oval(
            5, 1, 13, 9,
            outline=color,
            width=1.5,
            fill=ACCENT if self.info_pinned else "",
        )
        canvas.create_polygon(7, 9, 11, 9, 9, 16, fill=color, outline="")

    def _toggle_info_section(self, _event=None):
        if self.info_pinned:
            return "break"
        self.info_collapsed = not self.info_collapsed
        self._apply_info_collapsed()
        return "break"

    def _toggle_info_pin(self, _event=None):
        self.info_pinned = not self.info_pinned
        if self.info_pinned:
            self.info_collapsed = False
        self._apply_info_collapsed()
        return "break"

    def _apply_info_collapsed(self):
        if self.info_collapsed:
            self.info_content.pack_forget()
        else:
            self.info_content.pack(fill="x", after=self.info_header)
        self.info_chevron.configure(
            text="▸" if self.info_collapsed else "▾"
        )
        self._draw_info_pin()

    def _info_label(self, parent, row, title):
        label = tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="w",
        )
        label.grid(row=row, column=0, sticky="w", pady=2)
        return label

    def _make_info_entry(self, parent, width=4):
        return tk.Entry(
            parent,
            width=width,
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            disabledbackground="#0b1220",
            insertbackground=TEXT,
            disabledforeground=MUTED,
            justify="right",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )

    def _make_info_menu(self, parent, variable, values, command, width=9):
        menu = tk.OptionMenu(parent, variable, *values, command=command)
        menu.configure(
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            relief="flat",
            bd=0,
            width=width,
            anchor="center",
            cursor="hand2",
        )
        menu["menu"].configure(
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            activebackground=ACCENT,
            activeforeground=BG,
            tearoff=0,
        )
        return menu

    def _active_rect(self):
        if self.active_layer is None:
            return None
        rects = [
            record
            for record in self.active_layer.items
            if record.get("type") in ("rect", "ellipse")
        ]
        return rects[-1] if rects else None

    def _active_image(self):
        if self.active_layer is None:
            return None
        images = [r for r in self.active_layer.items if r.get("type") == "image"]
        return images[-1] if images else None

    def _active_shape(self):
        return self._active_rect() or self._active_image()

    def _active_text(self):
        if self.active_layer is None:
            return None
        texts = [r for r in self.active_layer.items if r.get("type") == "text"]
        return texts[-1] if texts else None

    def _can_have_layer_background(self, layer):
        if layer is None:
            return False
        if layer.children:
            return True
        return not (
            self._is_text_layer(layer)
            or self._is_image_layer(layer)
            or self._is_shape_layer(layer)
        )

    def _refresh_bg_image_row(self, layer):
        image = layer.background_image if layer is not None else None
        name = str(image.get("name") or "") if image else ""
        label = name if name else "Chọn ảnh"
        if len(label) > 14:
            label = label[:13] + "…"
        self.info_bg_image_name.configure(
            text=label, fg=TEXT if image else MUTED
        )
        self.info_bg_image_clear.configure(fg=TEXT if image else MUTED)

    def _background_setting(self, image, key):
        allowed = {
            "size": ("cover", "contain"),
            "position": ("center", "top", "left", "right"),
            "repeat": ("repeat", "no-repeat"),
        }
        defaults = {"size": "cover", "position": "center",
                    "repeat": "no-repeat"}
        value = image.get(key) if isinstance(image, dict) else None
        return value if value in allowed[key] else defaults[key]

    def _refresh_bg_option_rows(self, image):
        visible = image is not None
        for widget in self.info_bg_option_rows:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()
        if not visible:
            return
        self.info_bg_size_var.set(self._background_setting(image, "size"))
        self.info_bg_position_var.set(
            self._background_setting(image, "position")
        )
        self.info_bg_repeat_var.set(
            self._background_setting(image, "repeat")
        )

    def _apply_layer_background_option(self, key, value):
        layer = self.active_layer
        if layer is None or not layer.background_image:
            return
        if self._background_setting(layer.background_image, key) == value:
            return
        self._push_history()
        layer.background_image[key] = value
        self._render_document()
        self._refresh_doc_tab()

    def _choose_layer_background_image(self, _event=None):
        layer = self.active_layer
        if not self._can_have_layer_background(layer):
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Chọn ảnh nền",
            filetypes=[
                ("Hình ảnh", IMAGE_FILE_PATTERN),
                ("Tất cả tệp", "*.*"),
            ],
        )
        if not path:
            return
        try:
            with open(path, "rb") as handle:
                raw = handle.read()
            data, mime, width, height = self._prepare_image(raw, path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Lỗi ảnh nền", str(error), parent=self)
            return
        self._push_history()
        layer.background_image = {
            "data": data,
            "mime": mime,
            "width": width,
            "height": height,
            "name": os.path.basename(path),
            "size": "cover",
            "position": "center",
            "repeat": "no-repeat",
        }
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _clear_layer_background_image(self, _event=None):
        layer = self.active_layer
        if layer is None or layer.background_image is None:
            return
        self._push_history()
        layer.background_image = None
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _layer_display(self, layer):
        value = getattr(layer, "display", "block")
        return value if value in GROUP_DISPLAYS else "block"

    def _apply_layer_display(self, value):
        layer = self.active_layer
        if layer is None:
            return
        if not (layer.children or self._is_text_layer(layer)):
            return
        if value not in GROUP_DISPLAYS or self._layer_display(layer) == value:
            return
        self._push_history()
        layer.display = value
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _layer_align(self, layer):
        value = getattr(layer, "align", "left")
        return value if value in GROUP_ALIGNS else "left"

    def _apply_group_align(self, value):
        layer = self.active_layer
        if layer is None or not layer.children:
            return
        if value not in GROUP_ALIGNS or self._layer_align(layer) == value:
            return
        self._push_history()
        layer.align = value
        self._refresh_doc_tab()

    def _layer_justify(self, layer):
        value = getattr(layer, "justify", "left")
        return value if value in GROUP_JUSTIFIES else "left"

    def _layer_gap(self, layer):
        value = getattr(layer, "gap", 0)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return 0
        return max(value, 0)

    def _normalize_pseudo(self, data):
        result = {}
        if not isinstance(data, dict):
            return result
        for key in PSEUDO_KEYS:
            value = data.get(key)
            if not isinstance(value, dict):
                continue
            normalized = dict(PSEUDO_DEFAULTS)
            normalized["enabled"] = bool(value.get("enabled"))
            for name in PSEUDO_DEFAULTS:
                if name == "enabled":
                    continue
                if isinstance(value.get(name), str):
                    normalized[name] = value[name]
            if normalized["position"] not in PSEUDO_POSITIONS:
                normalized["position"] = "absolute"
            result[key] = normalized
        return result

    def _layer_pseudo(self, layer, key):
        if layer is None:
            return dict(PSEUDO_DEFAULTS)
        data = self._normalize_pseudo(getattr(layer, "pseudo", None))
        return data.get(key, dict(PSEUDO_DEFAULTS))

    def _layer_has_pseudo(self, layer):
        return any(
            self._layer_pseudo(layer, key)["enabled"] for key in PSEUDO_KEYS
        )

    def _apply_group_justify(self, value):
        layer = self.active_layer
        if layer is None or not layer.children:
            return
        if value not in GROUP_JUSTIFIES or self._layer_justify(layer) == value:
            return
        self._push_history()
        layer.justify = value
        self._render_document()
        self._refresh_doc_tab()

    def _apply_group_gap(self, _event=None):
        if self._updating_info:
            return
        layer = self.active_layer
        if (
            layer is None
            or not layer.children
            or self._layer_display(layer) not in ("flex", "grid")
        ):
            return
        try:
            value = max(0, int(self.info_group_gap_entry.get().strip()))
        except ValueError:
            self._refresh_info()
            return
        if value == self._layer_gap(layer):
            return
        self._push_history()
        layer.gap = value
        self._render_document()
        self._refresh_doc_tab()

    def _layer_box_defaults(self):
        bounds = self._record_bounds(self.active_layer.items)
        if bounds is None:
            return 0, 0, 200, 120
        x1, y1, x2, y2 = (round(value) for value in bounds)
        if x2 <= x1:
            x2 = x1 + 200
        if y2 <= y1:
            y2 = y1 + 120
        return x1, y1, x2, y2

    def _ensure_layer_shape(self):
        x1, y1, x2, y2 = self._layer_box_defaults()
        rect = {
            "type": "rect",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": BRUSH_COLOR,
            "border_color": BRUSH_COLOR,
            "border_width": 2,
            "background": "",
        }
        self.active_layer.items.insert(0, rect)
        return rect

    def _refresh_info(self):
        self._hide_font_suggestions()
        rect = self._active_rect()
        image = self._active_image() if rect is None else None
        text = self._active_text() if rect is None and image is None else None
        shape = rect if rect is not None else image
        self._updating_info = True
        try:
            self._refresh_layer_position()
            self._show_info_rows(text is not None)
            bg_editable = text is None and self._can_have_layer_background(
                self.active_layer
            )
            for widget in self.info_bg_image_rows:
                if bg_editable:
                    widget.grid()
                else:
                    widget.grid_remove()
            self._refresh_bg_image_row(
                self.active_layer if bg_editable else None
            )
            self._refresh_bg_option_rows(
                self.active_layer.background_image
                if bg_editable else None
            )
            group = (
                self.active_layer is not None
                and bool(self.active_layer.children)
            )
            show_display = group or text is not None
            for widget in self.info_group_rows:
                if show_display:
                    widget.grid()
                else:
                    widget.grid_remove()
            for widget in self.info_group_align_rows:
                if group:
                    widget.grid()
                else:
                    widget.grid_remove()
            flex_group = (
                group
                and self._layer_display(self.active_layer) == "flex"
            )
            gap_group = (
                group
                and self._layer_display(self.active_layer) in ("flex", "grid")
            )
            for widget in self.info_group_justify_rows:
                if flex_group:
                    widget.grid()
                else:
                    widget.grid_remove()
            for widget in self.info_group_gap_rows:
                if gap_group:
                    widget.grid()
                else:
                    widget.grid_remove()
            if show_display:
                self.info_group_display_var.set(
                    self._layer_display(self.active_layer)
                )
            if group:
                self.info_group_align_var.set(
                    self._layer_align(self.active_layer)
                )
                self.info_group_justify_var.set(
                    self._layer_justify(self.active_layer)
                )
                self._set_info_entry(
                    self.info_group_gap_entry,
                    self._layer_gap(self.active_layer),
                )
            if text is not None:
                self._refresh_text_info(text)
                return
            if shape is None:
                if self.active_layer is None:
                    for entry in (
                        self.info_width_entry,
                        self.info_height_entry,
                        self.info_border_entry,
                        self.info_border_color_entry,
                        self.info_bg_entry,
                    ):
                        entry.configure(state="normal")
                        entry.delete(0, "end")
                        entry.configure(state="disabled")
                    self._paint_swatch(self.info_border_swatch, None)
                    self._paint_swatch(self.info_bg_swatch, None)
                    self.info_bg_clear.configure(fg=MUTED)
                    return
                x1, y1, x2, y2 = self._layer_box_defaults()
                self._set_info_entry(self.info_width_entry, x2 - x1)
                self._set_info_entry(self.info_height_entry, y2 - y1)
                self._set_info_entry(self.info_border_entry, 2)
                self._set_info_entry(self.info_border_color_entry, BRUSH_COLOR)
                self._paint_swatch(self.info_border_swatch, BRUSH_COLOR)
                self.info_bg_entry.configure(state="normal")
                self.info_bg_entry.delete(0, "end")
                self._paint_swatch(self.info_bg_swatch, None)
                self.info_bg_clear.configure(fg=MUTED)
                return

            if rect is not None:
                width = round(abs(rect["x2"] - rect["x1"]))
                height = round(abs(rect["y2"] - rect["y1"]))
                border_width = rect.get("border_width", 2)
                border_color = rect.get("border_color")
                if border_color is None:
                    border_color = rect.get("color") or BRUSH_COLOR
                background = rect.get("background") or ""
            else:
                width = round(image.get("width", 1))
                height = round(image.get("height", 1))
                border_width = image.get("border_width", 0)
                border_color = image.get("border_color")
                if border_color is None:
                    border_color = BRUSH_COLOR
                background = ""

            self._set_info_entry(self.info_width_entry, width)
            self._set_info_entry(self.info_height_entry, height)
            self._set_info_entry(
                self.info_border_entry, border_width if border_width else ""
            )
            self._set_info_entry(
                self.info_border_color_entry, border_color or ""
            )
            self._paint_swatch(
                self.info_border_swatch, border_color or None
            )
            if rect is not None:
                self._set_info_entry(self.info_bg_entry, background)
                self._paint_swatch(self.info_bg_swatch, background or None)
                self.info_bg_clear.configure(fg=TEXT if background else MUTED)
            else:
                self.info_bg_entry.configure(state="normal")
                self.info_bg_entry.delete(0, "end")
                self.info_bg_entry.configure(state="disabled")
                self._paint_swatch(self.info_bg_swatch, None)
                self.info_bg_clear.configure(fg=MUTED)
        finally:
            self._updating_info = False

    def _show_info_rows(self, show_text):
        self.info_title.configure(
            text="THÔNG TIN VĂN BẢN" if show_text else "THÔNG TIN HÌNH"
        )
        for widget in self.info_shape_rows:
            if show_text:
                widget.grid_remove()
            else:
                widget.grid()
        for widget in self.info_text_rows:
            if show_text:
                widget.grid()
            else:
                widget.grid_remove()

    def _refresh_text_info(self, text):
        color = text.get("color") or TEXT
        self.info_font_family_var.set(self._text_family(text))
        self._set_info_entry(
            self.info_font_size_entry, text.get("font_size", 14)
        )
        self._set_info_entry(self.info_text_color_entry, color)
        self._paint_swatch(self.info_text_swatch, color)
        self.info_weight_var.set(str(self._text_weight_value(text)))
        self._set_info_entry(
            self.info_line_height_entry, text.get("line_height", 1.4)
        )
        self._set_info_entry(
            self.info_letter_spacing_entry, text.get("letter_spacing", 0)
        )
        self.info_transform_var.set(self._text_transform(text))
        align = self._text_align_state(text)
        self.info_align_var.set("" if align == "none" else align)
        self.info_tag_var.set(self._text_tag(text))

    def _refresh_layer_position(self):
        layer = self.active_layer
        if layer is None:
            for widget in self.info_position_rows:
                widget.grid_remove()
            return
        for widget in self.info_position_rows:
            widget.grid()
        position = self._layer_position(layer)
        values = (
            ("—", "—")
            if position is None
            else (str(position[0]), str(position[1]))
        )
        for entry, value in zip(
            (self.info_position_x, self.info_position_y), values
        ):
            entry.delete(0, "end")
            entry.insert(0, value)
        parent = layer.parent
        target = "canvas" if parent is None else f"nhóm '{parent.name}'"
        self.info_position_tip.text = (
            f"Nhập X/Y để di chuyển layer — mốc: {target}"
        )

    def _apply_layer_position(self, _event=None):
        if self._updating_info:
            return
        layer = self.active_layer
        if layer is None:
            return
        current = self._layer_position(layer)
        if current is None:
            self._refresh_info()
            return
        try:
            x = int(self.info_position_x.get())
            y = int(self.info_position_y.get())
        except ValueError:
            self._refresh_info()
            return
        dx = x - current[0]
        dy = y - current[1]
        if dx == 0 and dy == 0:
            return
        self._push_history()
        self._translate_layer(layer, dx, dy)
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _layer_position(self, layer):
        box = self._export_visual_box(layer)
        if box is None and layer.children:
            group_box = self._group_css_box(layer)
            box = (
                group_box["x"],
                group_box["y"],
                group_box["width"],
                group_box["height"],
            )
        if box is None:
            return None
        offsets = self._layer_layout_offsets()
        dx, dy = offsets.get(id(layer), (0.0, 0.0))
        x = box[0] + dx
        y = box[1] + dy
        parent = layer.parent
        if parent is not None:
            parent_box = self._export_visual_box(parent)
            if parent_box is None and parent.children:
                group_box = self._group_css_box(parent)
                parent_box = (
                    group_box["x"],
                    group_box["y"],
                    group_box["width"],
                    group_box["height"],
                )
            if parent_box is not None:
                pdx, pdy = offsets.get(id(parent), (0.0, 0.0))
                x -= parent_box[0] + pdx
                y -= parent_box[1] + pdy
        return int(round(x)), int(round(y))

    def _layer_layout_offsets(self):
        offsets = {}

        def walk(
            layers, dx=0.0, dy=0.0,
            children_dx=None, children_dy=None,
        ):
            base_dx = dx if children_dx is None else children_dx
            base_dy = dy if children_dy is None else children_dy
            for item_layer in layers:
                offsets[id(item_layer)] = (dx, dy)
                if not item_layer.visible:
                    continue
                child_offsets = {}
                display = self._layer_display(item_layer)
                if item_layer.children and display == "flex":
                    child_offsets = self._flex_child_offsets(item_layer)
                elif item_layer.children and display == "grid":
                    child_offsets = self._grid_child_offsets(item_layer)
                for child in item_layer.children:
                    if not child.visible:
                        continue
                    child_dx, child_dy, _stretch = child_offsets.get(
                        id(child), (0.0, 0.0, None)
                    )
                    keep_design = (
                        display == "flex"
                        and child.children
                        and self._is_flex_fill_layer(child)
                    )
                    walk(
                        [child],
                        base_dx + child_dx,
                        base_dy + child_dy,
                        children_dx=base_dx if keep_design else None,
                        children_dy=base_dy if keep_design else None,
                    )

        walk(self.layers)
        return offsets

    def _font_matches(self, text):
        query = text.strip().lower()
        if not query:
            return list(self._font_families)
        matches = [
            name for name in self._font_families if query in name.lower()
        ]
        matches.sort(
            key=lambda name: (
                not name.lower().startswith(query),
                name.lower(),
            )
        )
        return matches

    def _font_suggest_widgets(self):
        top = self._font_suggest
        if top is not None and top.winfo_exists():
            return top, self._font_suggest_list
        top = tk.Toplevel(self)
        top.wm_overrideredirect(True)
        top.attributes("-topmost", True)
        top.withdraw()
        listbox = tk.Listbox(
            top,
            font=("Segoe UI", 9),
            bg="#0b1220",
            fg=TEXT,
            selectbackground=ACCENT,
            selectforeground=BG,
            highlightthickness=1,
            highlightbackground=BORDER,
            relief="flat",
            bd=0,
            activestyle="none",
            exportselection=False,
        )
        listbox.pack(fill="both", expand=True)
        listbox.bind("<ButtonRelease-1>", self._pick_font_suggestion)
        self._font_suggest = top
        self._font_suggest_list = listbox
        return top, listbox

    def _font_entry_spec(self, entry=None):
        entry = entry or self.info_font_family_entry
        if entry is getattr(self, "body_font_family_entry", None):
            return (
                entry,
                self.body_font_family_var,
                self.body_font_family_arrow,
                self._apply_body_font,
            )
        return (
            entry,
            self.info_font_family_var,
            self.info_font_family_arrow,
            self._apply_text_style,
        )

    def _set_font_entry_active(self, entry):
        self._font_suggest_entry = entry

    def _show_font_suggestions(self, entry=None):
        entry, var, arrow, _apply = self._font_entry_spec(entry)
        if not entry.winfo_ismapped():
            return
        matches = self._font_matches(var.get())
        if not matches:
            self._hide_font_suggestions()
            return
        top, listbox = self._font_suggest_widgets()
        visible = matches[:12]
        listbox.configure(height=len(visible))
        listbox.delete(0, "end")
        for name in visible:
            listbox.insert("end", name)
        listbox.selection_clear(0, "end")
        top.update_idletasks()
        width = max(
            entry.winfo_width() + arrow.winfo_width(),
            170,
        )
        height = min(max(listbox.winfo_reqheight(), 20), 220)
        x = max(entry.winfo_rootx(), 0)
        y = entry.winfo_rooty() + entry.winfo_height() + 2
        if y + height > self.winfo_screenheight() - 4:
            y = max(entry.winfo_rooty() - height - 2, 4)
        self._font_suggest_entry = entry
        top.wm_geometry(f"{width}x{height}+{x}+{y}")
        top.deiconify()
        top.lift()

    def _hide_font_suggestions(self, _event=None):
        top = getattr(self, "_font_suggest", None)
        if top is not None and top.winfo_exists():
            top.withdraw()
        if _event is not None:
            return "break"

    def _update_font_suggestions(self, event=None, entry=None):
        if event is not None and event.keysym in (
            "Up", "Down", "Return", "Escape", "Tab", "ISO_Left_Tab",
            "Left", "Right", "Home", "End",
            "Shift_L", "Shift_R", "Control_L", "Control_R",
            "Alt_L", "Alt_R",
        ):
            return
        self._show_font_suggestions(entry)

    def _move_font_suggestion(self, direction):
        top = self._font_suggest
        listbox = self._font_suggest_list
        if top is None or not top.winfo_exists() or not top.winfo_ismapped():
            self._show_font_suggestions()
            return
        if listbox is None or not listbox.size():
            return
        current = listbox.curselection()
        index = (current[0] + direction) if current else 0
        index = max(0, min(index, listbox.size() - 1))
        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        listbox.activate(index)
        listbox.see(index)

    def _font_suggest_down(self, _event=None):
        self._move_font_suggestion(1)
        return "break"

    def _font_suggest_up(self, _event=None):
        self._move_font_suggestion(-1)
        return "break"

    def _apply_font_field(self, _event=None, entry=None):
        entry = entry or self._font_suggest_entry or self.info_font_family_entry
        _entry, var, _arrow, apply = self._font_entry_spec(entry)
        top = self._font_suggest
        listbox = self._font_suggest_list
        if (
            top is not None and top.winfo_exists() and top.winfo_ismapped()
            and listbox is not None and listbox.size()
        ):
            current = listbox.curselection()
            if current:
                var.set(listbox.get(current[0]))
        self._hide_font_suggestions()
        apply()
        return "break"

    def _pick_font_suggestion(self, event):
        listbox = self._font_suggest_list
        if listbox is None:
            return
        index = listbox.nearest(event.y)
        if index < 0 or index >= listbox.size():
            return
        entry = self._font_suggest_entry or self.info_font_family_entry
        _entry, var, _arrow, apply = self._font_entry_spec(entry)
        var.set(listbox.get(index))
        self._hide_font_suggestions()
        apply()
        entry.focus_set()

    def _toggle_font_suggestions(self, _event=None, entry=None):
        entry = entry or self.info_font_family_entry
        entry.focus_set()
        top = self._font_suggest
        if top is not None and top.winfo_exists() and top.winfo_ismapped():
            self._hide_font_suggestions()
        else:
            self._show_font_suggestions(entry)
        return "break"

    def _on_font_focus_out(self, _event=None):
        if self._font_focus_after is not None:
            self.after_cancel(self._font_focus_after)
        self._font_focus_after = self.after(
            150, self._finish_font_focus_out
        )

    def _finish_font_focus_out(self):
        self._font_focus_after = None
        focus = self.focus_get()
        if focus in (
            self.info_font_family_entry,
            getattr(self, "body_font_family_entry", None),
        ):
            return
        if focus is self._font_suggest_list:
            return
        entry = self._font_suggest_entry or self.info_font_family_entry
        _entry, _var, _arrow, apply = self._font_entry_spec(entry)
        self._hide_font_suggestions()
        apply()

    def _set_info_entry(self, entry, value):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(value))

    def _apply_rect_size(self, _event=None):
        if self._updating_info:
            return
        rect = self._active_rect()
        image = self._active_image() if rect is None else None
        if rect is None and image is None and (
            self.active_layer is None or self._active_text() is not None
        ):
            return
        try:
            width = max(1, int(self.info_width_entry.get()))
            height = max(1, int(self.info_height_entry.get()))
        except ValueError:
            self._refresh_info()
            return
        if rect is not None:
            new_x2 = rect["x1"] + width
            new_y2 = rect["y1"] + height
            if new_x2 == rect["x2"] and new_y2 == rect["y2"]:
                return
            self._push_history()
            rect["x2"], rect["y2"] = new_x2, new_y2
        elif image is not None:
            width = min(width, 6000)
            height = min(height, 6000)
            if width == image.get("width") and height == image.get("height"):
                return
            self._push_history()
            image["width"], image["height"] = width, height
        else:
            width = min(width, 6000)
            height = min(height, 6000)
            x1, y1, x2, y2 = self._layer_box_defaults()
            if width == x2 - x1 and height == y2 - y1:
                self._refresh_info()
                return
            self._push_history()
            rect = self._ensure_layer_shape()
            rect["x2"] = rect["x1"] + width
            rect["y2"] = rect["y1"] + height
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _apply_border_width(self, _event=None):
        if self._updating_info:
            return
        shape = self._active_shape()
        if shape is None and (
            self.active_layer is None or self._active_text() is not None
        ):
            return
        raw = self.info_border_entry.get().strip()
        if not raw:
            border_width = 0
        else:
            try:
                border_width = max(0, min(50, int(raw)))
            except ValueError:
                self._refresh_info()
                return
        if shape is not None:
            default = 2 if shape.get("type") in ("rect", "ellipse") else 0
            if border_width == shape.get("border_width", default):
                self._refresh_info()
                return
        else:
            if border_width == 2:
                self._refresh_info()
                return
            self._push_history()
            shape = self._ensure_layer_shape()
        shape["border_width"] = border_width
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _parse_hex_color(self, value):
        value = value.strip()
        if value.startswith("#"):
            value = value[1:]
        if len(value) == 3:
            value = "".join(ch * 2 for ch in value)
        if len(value) != 6:
            return None
        if any(ch not in "0123456789abcdefABCDEF" for ch in value):
            return None
        return "#" + value.lower()

    def _apply_border_color_text(self, _event=None):
        if self._updating_info:
            return
        shape = self._active_shape()
        if shape is None and (
            self.active_layer is None or self._active_text() is not None
        ):
            return
        text = self.info_border_color_entry.get().strip()
        if not text:
            if shape is not None:
                self._set_border_color(shape, "")
            else:
                self._refresh_info()
            return
        color = self._parse_hex_color(text)
        if color is None:
            self._refresh_info()
            return
        if shape is None:
            if color == BRUSH_COLOR:
                self._refresh_info()
                return
            self._push_history()
            shape = self._ensure_layer_shape()
            shape["border_color"] = color
            self._render_document()
            self._refresh_info()
            self._refresh_doc_tab()
            return
        self._set_border_color(shape, color)

    def _apply_background_text(self, _event=None):
        if self._updating_info:
            return
        rect = self._active_rect()
        if rect is None and (
            self.active_layer is None
            or self._active_image() is not None
            or self._active_text() is not None
        ):
            return
        text = self.info_bg_entry.get().strip()
        if not text:
            if rect is not None:
                self._set_background_color(rect, "")
            return
        color = self._parse_hex_color(text)
        if color is None:
            self._refresh_info()
            return
        if rect is None:
            self._push_history()
            rect = self._ensure_layer_shape()
            rect["background"] = color
            self._render_document()
            self._refresh_info()
            self._refresh_doc_tab()
            return
        self._set_background_color(rect, color)

    def _set_border_color(self, shape, color):
        current = shape.get("border_color")
        if current is None:
            current = shape.get("color") or BRUSH_COLOR
        if color != current:
            self._push_history()
            shape["border_color"] = color
            self._render_document()
            self._refresh_doc_tab()
        self._refresh_info()

    def _set_background_color(self, rect, color):
        if color != (rect.get("background") or ""):
            self._push_history()
            rect["background"] = color
            self._render_document()
            self._refresh_doc_tab()
        self._refresh_info()

    def _choose_border_color(self, _event=None):
        shape = self._active_shape()
        if shape is None and (
            self.active_layer is None or self._active_text() is not None
        ):
            return
        current = (
            shape.get("border_color") or shape.get("color") or BRUSH_COLOR
        ) if shape is not None else BRUSH_COLOR
        _rgb, color = colorchooser.askcolor(
            color=current, title="Chọn màu viền", parent=self
        )
        if color:
            if shape is None:
                self._push_history()
                shape = self._ensure_layer_shape()
                shape["border_color"] = color
                self._render_document()
                self._refresh_info()
                self._refresh_doc_tab()
            else:
                self._set_border_color(shape, color)

    def _choose_background_color(self, _event=None):
        rect = self._active_rect()
        if rect is None and (
            self.active_layer is None
            or self._active_image() is not None
            or self._active_text() is not None
        ):
            return
        current = (rect.get("background") or "#ffffff") if rect else "#ffffff"
        _rgb, color = colorchooser.askcolor(
            color=current, title="Chọn màu nền", parent=self
        )
        if color:
            if rect is None:
                self._push_history()
                rect = self._ensure_layer_shape()
                rect["background"] = color
                self._render_document()
                self._refresh_info()
                self._refresh_doc_tab()
            else:
                self._set_background_color(rect, color)

    def _clear_background(self, _event=None):
        rect = self._active_rect()
        if rect is None or not rect.get("background"):
            return
        self._set_background_color(rect, "")

    def _apply_body_font(self, _event=None):
        family = self.body_font_family_var.get().strip()[:60] or "none"
        if family.lower() == "none":
            family = "none"
        self.body_font_family_var.set(family)
        if family == self.body_font_family:
            return
        self._push_history()
        self.body_font_family = family
        self._render_document()
        self._refresh_doc_tab()

    def _on_align_click(self, value):
        text = self._active_text()
        if text is None:
            return "break"
        current = self._text_align_state(text)
        self.info_align_var.set("" if current == value else value)
        self._apply_text_style()
        return "break"

    def _apply_text_style(self, _event=None):
        if self._updating_info:
            return
        text = self._active_text()
        if text is None:
            return
        try:
            font_family = (
                self.info_font_family_var.get().strip()[:60] or "none"
            )
            if font_family.lower() == "none":
                font_family = "none"
            font_size = max(1, min(300, int(self.info_font_size_entry.get())))
            line_height = max(
                0.5,
                min(5.0, float(
                    self.info_line_height_entry.get().replace(",", ".")
                )),
            )
            letter_spacing = max(
                -20, min(100, int(self.info_letter_spacing_entry.get()))
            )
            weight_text = self.info_weight_var.get().strip()
            try:
                font_weight = max(100, min(900, int(weight_text)))
            except ValueError:
                font_weight = 400
            font_weight = round(font_weight / 100) * 100
        except ValueError:
            self._refresh_info()
            return
        align = self.info_align_var.get().strip().lower()
        if align not in ("left", "center", "right"):
            align = "none"
        tag = self.info_tag_var.get().strip().lower()
        if tag not in TEXT_TAGS:
            tag = "p"
        updated = {
            "font_family": font_family,
            "font_size": font_size,
            "font_weight": font_weight,
            "line_height": round(line_height, 2),
            "letter_spacing": letter_spacing,
            "text_transform": self.info_transform_var.get(),
            "text_align": align,
            "text_tag": tag,
        }
        if align == "none":
            updated["text_frame"] = None
        elif self.marquee_region is not None:
            updated["text_frame"] = list(self.marquee_region)
        if all(text.get(key) == value for key, value in updated.items()):
            self._refresh_info()
            return
        tag_changed = self._text_tag(text) != tag
        self._push_history()
        text.update(updated)
        self._render_document()
        if tag_changed:
            self._refresh_layers()
        else:
            self._refresh_info()
        self._refresh_doc_tab()

    def _set_text_color(self, text, color):
        if color != (text.get("color") or ""):
            self._push_history()
            text["color"] = color
            self._render_document()
            self._refresh_doc_tab()
        self._refresh_info()

    def _apply_text_color_text(self, _event=None):
        if self._updating_info:
            return
        text = self._active_text()
        if text is None:
            return
        color = self._parse_hex_color(self.info_text_color_entry.get())
        if color is None:
            self._refresh_info()
            return
        self._set_text_color(text, color)

    def _choose_text_color(self, _event=None):
        text = self._active_text()
        if text is None:
            return
        _rgb, color = colorchooser.askcolor(
            color=text.get("color") or TEXT, title="Chọn màu chữ", parent=self
        )
        if color:
            self._set_text_color(text, color)

    def _paint_swatch(self, canvas, color):
        canvas.delete("all")
        if color:
            canvas.create_rectangle(1, 1, 13, 13, fill=color, outline=BORDER)
        else:
            canvas.create_rectangle(1, 1, 13, 13, fill="#f8fafc", outline=BORDER)
            canvas.create_line(2, 12, 12, 2, fill=MUTED)

    def _make_panel_button(self, parent, text, command):
        button = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            fg=MUTED,
            bg=PANEL_BG,
            width=2,
            cursor="hand2",
        )
        button.bind("<Button-1>", lambda _e: command())
        button.bind("<Enter>", lambda _e: button.configure(bg=BORDER, fg=TEXT))
        button.bind("<Leave>", lambda _e: button.configure(bg=PANEL_BG, fg=MUTED))
        return button

    def _open_save_menu(self, event=None):
        widget = event.widget if event is not None else None
        if widget is not None and widget.winfo_exists():
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height()
        else:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
        try:
            self.save_menu.tk_popup(x, y)
        finally:
            self.save_menu.grab_release()

    def _make_menu_item(self, parent, text, command, danger=False):
        fg = SUBTLE if danger else TEXT
        hover_bg = DANGER_BG if danger else HOVER_BG

        item = tk.Label(
            parent,
            text=text,
            font=self.font_menu,
            fg=fg,
            bg=PANEL_BG,
            padx=6,
            pady=8,
            cursor="hand2",
        )
        item.bind("<Button-1>", lambda _e: command())
        item.bind("<Enter>", lambda _e: item.configure(bg=hover_bg))
        item.bind("<Leave>", lambda _e: item.configure(bg=PANEL_BG))
        return item

    def _sync_scrollregion(self, _event=None):
        self.sidebar_canvas.configure(
            scrollregion=(0, 0, SIDEBAR_WIDTH, self.tools_frame.winfo_reqheight())
        )

    def _on_mousewheel(self, event):
        self.sidebar_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _tool_enter(self, tool_id):
        item, backdrop = self.tool_items[tool_id]
        if tool_id != self.active_tool_id:
            item.itemconfigure(backdrop, fill=HOVER_BG)

    def _tool_leave(self, tool_id):
        item, backdrop = self.tool_items[tool_id]
        fill = ACTIVE_BG if tool_id == self.active_tool_id else PANEL_BG
        item.itemconfigure(backdrop, fill=fill)

    def select_tool(self, tool_id):
        self.active_tool_id = tool_id
        for tid, (item, backdrop) in self.tool_items.items():
            fill = ACTIVE_BG if tid == tool_id else PANEL_BG
            item.itemconfigure(backdrop, fill=fill)
        self.doc_canvas.configure(cursor=CURSORS.get(tool_id, "arrow"))
        self._update_status()

    def _open_rect_shape_menu(self, event):
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=PANEL_BG,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=TEXT,
            selectcolor=ACCENT,
            bd=0,
        )
        mode = tk.StringVar(value=self.rect_tool_shape)
        for shape, label in (
            ("rect", "Hình chữ nhật"),
            ("ellipse", "Hình elip"),
        ):
            menu.add_radiobutton(
                label=label,
                variable=mode,
                value=shape,
                command=lambda value=shape: self._set_rect_shape_mode(value),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    def _set_rect_shape_mode(self, shape):
        self.rect_tool_shape = shape
        self.tool_names["rect"] = (
            "Hình elip" if shape == "ellipse" else "Hình chữ nhật"
        )
        self._refresh_rect_tool_icon()
        tip = self.tool_tips.get("rect")
        if tip is not None:
            tip.text = self.tool_names["rect"]
        if self.active_tool_id != "rect":
            self.select_tool("rect")
        else:
            self._update_status()

    def _refresh_rect_tool_icon(self):
        item, _backdrop = self.tool_items["rect"]
        item.delete("all")
        backdrop = item.create_rectangle(
            2, 2, TOOL_SIZE - 2, TOOL_SIZE - 2, fill=PANEL_BG, outline=""
        )
        draw = (
            draw_ellipse
            if self.rect_tool_shape == "ellipse"
            else draw_rect
        )
        draw(item, ICON)
        self.tool_items["rect"] = (item, backdrop)
        if self.active_tool_id == "rect":
            item.itemconfigure(backdrop, fill=ACTIVE_BG)

    def _add_layer(self, record=True):
        self._commit_text_editor()
        if record:
            self._push_history()
        self._create_layer()
        self._refresh_layers()
        self._refresh_doc_tab()

    def _next_layer_name(self, prefix):
        used = set()
        marker = f"{prefix} "
        for layer in self._iter_layers():
            name = layer.name.strip()
            if name.startswith(marker):
                suffix = name[len(marker):]
                if suffix.isdigit():
                    used.add(int(suffix))
        number = 1
        while number in used:
            number += 1
        return f"{prefix} {number}"

    def _create_layer(self, name=None):
        self.layer_counter += 1
        layer = Layer(name or self._next_layer_name("Lớp"))
        active = self.active_layer
        if active is not None and active.parent is not None:
            siblings = active.parent.children
            siblings.insert(siblings.index(active) + 1, layer)
            layer.parent = active.parent
            active.parent.expanded = True
        else:
            self.layers.append(layer)
        self.active_layer = layer
        return layer

    def _is_text_layer(self, layer):
        return any(record.get("type") == "text" for record in layer.items)

    def _set_text_format(self, layer, value):
        if value not in TEXT_FORMATS:
            return
        new_value = "" if layer.text_format == value else value
        if new_value == layer.text_format:
            return
        self._push_history()
        layer.text_format = new_value
        self._refresh_layers()
        self._refresh_doc_tab()

    def _set_group_format(self, layer, value):
        if value not in GROUP_FORMATS:
            return
        new_value = "" if layer.group_tag == value else value
        if new_value == layer.group_tag:
            return
        self._push_history()
        layer.group_tag = new_value
        self._refresh_layers()
        self._refresh_doc_tab()

    def _is_image_layer(self, layer):
        return any(record.get("type") == "image" for record in layer.items)

    def _shape_layer_kind(self, layer):
        for record in layer.items:
            if record.get("type") in ("rect", "ellipse"):
                return record["type"]
        return None

    def _is_shape_layer(self, layer):
        return self._shape_layer_kind(layer) is not None

    def _can_draw_on(self, layer):
        return (
            layer is not None
            and not layer.children
            and not self._is_text_layer(layer)
            and not self._is_image_layer(layer)
            and not self._is_shape_layer(layer)
        )

    def _clone_layer(self, layer):
        clone = Layer(layer.name)
        clone.visible = layer.visible
        clone.expanded = layer.expanded
        clone.items = [dict(item) for item in layer.items]
        clone.display = self._layer_display(layer)
        clone.align = self._layer_align(layer)
        clone.justify = self._layer_justify(layer)
        clone.gap = self._layer_gap(layer)
        clone.blend_mode = layer.blend_mode
        clone.text_format = layer.text_format
        clone.group_tag = layer.group_tag
        clone.pseudo = self._normalize_pseudo(layer.pseudo)
        clone.background_image = (
            dict(layer.background_image) if layer.background_image else None
        )
        clone.children = [self._clone_layer(child) for child in layer.children]
        for child in clone.children:
            child.parent = clone
        return clone

    def _duplicate_layer(self, _event=None):
        entry = self._rename_entry
        if entry is not None and entry.winfo_exists():
            return "break"
        self._commit_text_editor()
        layer = self.active_layer
        if layer is None:
            return "break"
        self._push_history()
        clone = self._clone_layer(layer)
        clone.name = f"{layer.name} copy"
        clone.parent = layer.parent
        siblings = layer.parent.children if layer.parent else self.layers
        siblings.insert(siblings.index(layer) + 1, clone)
        if layer.parent is not None:
            layer.parent.expanded = True
        self.active_layer = clone
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()
        return "break"

    def _iter_layers(self, layers=None):
        for layer in self.layers if layers is None else layers:
            yield layer
            yield from self._iter_layers(layer.children)

    def _count_layers(self):
        return sum(1 for _ in self._iter_layers())

    def _layer_path(self, layer):
        path = []
        node = layer
        while node is not None:
            siblings = node.parent.children if node.parent else self.layers
            path.append(siblings.index(node))
            node = node.parent
        return list(reversed(path))

    def _layer_at(self, path):
        siblings = self.layers
        node = None
        for index in path:
            node = siblings[index]
            siblings = node.children
        return node

    def _is_descendant(self, node, ancestor):
        parent = node.parent
        while parent is not None:
            if parent is ancestor:
                return True
            parent = parent.parent
        return False

    def _delete_layer(self):
        self._commit_text_editor()
        layer = self.active_layer
        if layer is None or self._count_layers() <= 1:
            return
        subtree = list(self._iter_layers([layer]))
        if self._count_layers() - len(subtree) < 1:
            return
        self._push_history()
        siblings = layer.parent.children if layer.parent else self.layers
        index = siblings.index(layer)
        siblings.pop(index)
        if layer.parent is not None:
            next_active = layer.parent
        elif siblings:
            next_active = siblings[min(index, len(siblings) - 1)]
        else:
            next_active = list(self._iter_layers())[-1]
        self.active_layer = next_active
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()

    def _select_layer(self, layer):
        self._commit_text_editor()
        self.selected_layers = [layer]
        self._selection_anchor = layer
        self.active_layer = layer
        self._refresh_layer_selection()
        self._refresh_info()
        self._update_status()

    def _select_layer_range(self, layer):
        self._commit_text_editor()
        order = list(self._panel_layers())
        anchor = self._selection_anchor
        if anchor not in order or layer not in order:
            self._select_layer(layer)
            return
        start, end = order.index(anchor), order.index(layer)
        if start > end:
            start, end = end, start
        self.selected_layers = order[start:end + 1]
        self.active_layer = layer
        self._refresh_layer_selection()
        self._refresh_info()
        self._update_status()

    def _toggle_layer_selection(self, layer):
        self._commit_text_editor()
        if layer in self.selected_layers:
            if len(self.selected_layers) == 1:
                return
            self.selected_layers.remove(layer)
            if self.active_layer is layer:
                self.active_layer = self.selected_layers[-1]
        else:
            self.selected_layers.append(layer)
            self.active_layer = layer
        self._selection_anchor = layer
        self._refresh_layer_selection()
        self._refresh_info()
        self._update_status()

    def _panel_layers(self, layers=None):
        for layer in reversed(self.layers if layers is None else layers):
            yield layer
            if layer.children and layer.expanded:
                yield from self._panel_layers(layer.children)

    def _group_selected_layers(self, _event=None):
        entry = self._rename_entry
        if entry is not None and entry.winfo_exists():
            return "break"
        self._commit_text_editor()
        order = [
            layer
            for layer in self._panel_layers()
            if layer in self.selected_layers
        ]
        if not order:
            return "break"
        layers = [
            layer
            for layer in order
            if not any(
                self._is_descendant(layer, other)
                for other in order
                if other is not layer
            )
        ]
        top = layers[0]
        group_parent = top.parent
        siblings = group_parent.children if group_parent else self.layers
        selected_ids = {id(layer) for layer in layers}
        top_index = siblings.index(top)
        removed_below = sum(
            1
            for node in siblings[:top_index]
            if id(node) in selected_ids
        )
        insert_at = top_index - removed_below

        self._push_history()
        for layer in layers:
            current = layer.parent.children if layer.parent else self.layers
            current.remove(layer)

        group = Layer(self._next_layer_name("Nhóm"))
        group.parent = group_parent
        group.children = list(reversed(layers))
        for child in group.children:
            child.parent = group
        siblings.insert(max(0, min(insert_at, len(siblings))), group)

        self.active_layer = group
        self.selected_layers = [group]
        self._selection_anchor = group
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()
        return "break"

    def _refresh_layer_selection(self):
        for row in self.layer_list.winfo_children():
            layer = getattr(row, "_layer", None)
            if layer is None:
                continue
            bg = (
                ACTIVE_BG
                if layer in self.selected_layers
                else PANEL_BG
            )
            row._layer_base_bg = bg
            for widget in row._layer_bg_widgets:
                widget.configure(bg=bg)
            self._draw_eye(row._layer_eye, layer.visible, bg)
            if row._layer_expander is not None:
                self._draw_expander(row._layer_expander, layer.expanded)

    def _toggle_layer(self, layer):
        self._push_history()
        layer.visible = not layer.visible
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()

    def _layer_state(self, layer):
        return {
            "name": layer.name,
            "visible": layer.visible,
            "expanded": layer.expanded,
            "display": self._layer_display(layer),
            "align": self._layer_align(layer),
            "justify": self._layer_justify(layer),
            "gap": self._layer_gap(layer),
            "blend_mode": layer.blend_mode,
            "text_format": layer.text_format,
            "group_tag": layer.group_tag,
            "pseudo": self._normalize_pseudo(getattr(layer, "pseudo", None)),
            "items": [dict(item) for item in layer.items],
            "background_image": (
                dict(layer.background_image)
                if layer.background_image
                else None
            ),
            "children": [self._layer_state(child) for child in layer.children],
        }

    def _restore_layers(self, data, parent=None):
        layers = []
        for item in data:
            layer = Layer(item["name"])
            layer.visible = item["visible"]
            layer.expanded = item.get("expanded", True)
            display = item.get("display", "block")
            layer.display = display if display in GROUP_DISPLAYS else "block"
            align = item.get("align", "left")
            layer.align = align if align in GROUP_ALIGNS else "left"
            justify = item.get("justify", "left")
            layer.justify = (
                justify if justify in GROUP_JUSTIFIES else "left"
            )
            gap = item.get("gap", 0)
            layer.gap = (
                gap
                if isinstance(gap, (int, float))
                and not isinstance(gap, bool)
                and gap >= 0
                else 0
            )
            blend_mode = item.get("blend_mode", "normal")
            layer.blend_mode = (
                blend_mode
                if blend_mode in PSD_CSS_BLEND_MODES
                else "normal"
            )
            text_format = item.get("text_format", "")
            if text_format not in TEXT_FORMATS:
                text_format = "span" if item.get("inline_text") else ""
            layer.text_format = text_format
            group_tag = item.get("group_tag", "")
            layer.group_tag = (
                group_tag if group_tag in GROUP_FORMATS else ""
            )
            layer.pseudo = self._normalize_pseudo(item.get("pseudo"))
            layer.items = [dict(record) for record in item["items"]]
            background = item.get("background_image")
            if (
                isinstance(background, dict)
                and isinstance(background.get("data"), str)
                and background["data"]
            ):
                layer.background_image = dict(background)
            layer.parent = parent
            layer.children = self._restore_layers(item.get("children", []), layer)
            layers.append(layer)
        return layers

    def _push_history(self):
        self.history.append({
            "layers": [self._layer_state(layer) for layer in self.layers],
            "active": self._layer_path(self.active_layer),
            "counter": self.layer_counter,
            "body_font": self.body_font_family,
        })
        if len(self.history) > 50:
            self.history.pop(0)

    def _undo(self, _event=None):
        self._commit_text_editor()
        if not self.history:
            return "break"
        state = self.history.pop()
        self.layer_counter = state["counter"]
        self.body_font_family = state.get("body_font", "none")
        self.body_font_family_var.set(self.body_font_family)
        self.layers = self._restore_layers(state["layers"])
        try:
            self.active_layer = self._layer_at(state["active"])
        except (IndexError, TypeError):
            self.active_layer = list(self._iter_layers())[-1]
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()
        return "break"

    def _layer_signature(self, layer):
        return {
            "name": layer.name,
            "visible": layer.visible,
            "display": self._layer_display(layer),
            "align": self._layer_align(layer),
            "justify": self._layer_justify(layer),
            "gap": self._layer_gap(layer),
            "blend_mode": layer.blend_mode,
            "text_format": layer.text_format,
            "group_tag": layer.group_tag,
            "pseudo": self._normalize_pseudo(getattr(layer, "pseudo", None)),
            "items": layer.items,
            "background_image": layer.background_image,
            "children": [self._layer_signature(child) for child in layer.children],
        }

    def _document_signature(self):
        return json.dumps(
            {
                "content": [
                    self.content_width,
                    self.content_height,
                    self.content_full,
                    self._page_background(),
                ],
                "guides": self.guides,
                "body_font": self.body_font_family,
                "layers": [
                    self._layer_signature(layer) for layer in self.layers
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    def _refresh_doc_tab(self):
        self.dirty = self._document_signature() != self.saved_signature
        name = (
            os.path.basename(self.doc_path)
            if self.doc_path
            else self.doc_name
        )
        self.doc_tab_label.configure(text=f"{name}*" if self.dirty else name)
        self._update_status()

    def _refresh_layers(self):
        self._rename_entry = None
        self._rename_layer = None
        existing = list(self._iter_layers())
        self.selected_layers = [
            layer for layer in self.selected_layers if layer in existing
        ]
        if (
            self.active_layer is not None
            and self.active_layer not in self.selected_layers
        ):
            self.selected_layers = [self.active_layer]
            self._selection_anchor = self.active_layer
        for child in self.layer_list.winfo_children():
            child.destroy()
        self._drop_row = None
        self._drop_mode = None
        self._drop_indicator = tk.Frame(self.layer_list, bg=ACCENT, height=2)
        self._build_layer_rows(self.layers, 0)
        self.layer_count_label.configure(text=f"{self._count_layers()} lớp")
        self.after_idle(self._sync_layer_list_scroll)
        self._refresh_info()

    def _build_layer_rows(self, layers, depth):
        for layer in reversed(layers):
            self._build_layer_row(layer, depth)
            if layer.children and layer.expanded:
                self._build_layer_rows(layer.children, depth + 1)

    def _build_layer_row(self, layer, depth=0):
        selected = layer in self.selected_layers
        row_bg = ACTIVE_BG if selected else PANEL_BG

        row = tk.Frame(self.layer_list, bg=row_bg, cursor="hand2")
        row.pack(fill="x", pady=1)
        row._layer = layer
        row._layer_base_bg = row_bg
        bg_widgets = [row]

        expander = tk.Canvas(
            row, width=12, height=20, bg=row_bg, highlightthickness=0,
            cursor="hand2" if layer.children else "",
        )
        expander.pack(side="left", padx=(6 + depth * 14, 0), pady=8)
        if layer.children:
            self._draw_expander(expander, layer.expanded)
            expander.bind(
                "<Button-1>", lambda _e, l=layer: self._toggle_expanded(l)
            )
        bg_widgets.append(expander)

        eye = tk.Canvas(
            row, width=20, height=20, bg=row_bg,
            highlightthickness=0, cursor="hand2",
        )
        eye.pack(side="left", padx=(4, 4), pady=8)
        self._draw_eye(eye, layer.visible, row_bg)
        eye.bind("<Button-1>", lambda _e, l=layer: self._toggle_layer(l))
        bg_widgets.append(eye)

        thumb = tk.Canvas(
            row, width=30, height=30, bg="#f8fafc",
            highlightthickness=1, highlightbackground=BORDER,
        )
        thumb.pack(side="left", padx=(0, 8), pady=6)
        if layer.children:
            thumb.create_polygon(
                5, 10, 13, 10, 15, 13, 25, 13, 25, 23, 5, 23,
                fill=ACCENT, outline="",
            )
            thumb.create_line(5, 14, 25, 14, fill="#1d4ed8")
        elif self._is_image_layer(layer):
            thumb.create_rectangle(6, 8, 24, 22, outline=ACCENT, width=1.5)
            thumb.create_oval(16.5, 10, 19.5, 13, fill=ACCENT, outline="")
            thumb.create_polygon(
                7, 21, 12, 14, 16, 18, 19, 15, 23, 21,
                fill=ACCENT, outline="",
            )
        elif self._shape_layer_kind(layer) == "ellipse":
            thumb.create_oval(
                7, 9, 23, 21, outline=ACCENT, width=1.8
            )
        elif self._is_shape_layer(layer):
            thumb.create_rectangle(
                7, 9, 23, 21, outline=ACCENT, width=1.8
            )
        elif any(item.get("type") == "text" for item in layer.items):
            text_record = [
                item for item in layer.items if item.get("type") == "text"
            ][-1]
            thumb.create_text(
                15, 15, text=self._text_tag(text_record), fill=ACCENT,
                font=("Segoe UI", 13, "bold"),
            )

        name = tk.Label(
            row,
            text=layer.name,
            font=self.font_layer,
            fg=TEXT,
            bg=row_bg,
            anchor="w",
        )
        name.pack(side="left", fill="x", expand=True, padx=(0, 10))
        bg_widgets.append(name)

        badge_text = (
            layer.group_tag if layer.children else layer.text_format
        )
        if badge_text:
            badge = tk.Label(
                row,
                text=badge_text,
                font=("Segoe UI", 8, "bold"),
                fg=ACCENT,
                bg=row_bg,
            )
            badge.pack(side="right", padx=(0, 6))
            bg_widgets.append(badge)

        for widget in (row, thumb, name):
            widget.bind(
                "<Button-1>", lambda event, l=layer: self._on_layer_press(event, l)
            )
        for widget in bg_widgets + [thumb]:
            widget.bind(
                "<Button-3>",
                lambda event, l=layer: self._on_layer_context(event, l),
            )
        name.bind(
            "<Double-Button-1>",
            lambda _e, l=layer, w=name: self._begin_rename(l, w),
        )
        Tooltip(name, "Nhấp đúp để đổi tên lớp")

        row._layer_bg_widgets = bg_widgets
        row._layer_eye = eye
        row._layer_expander = expander if layer.children else None

        for widget in row.winfo_children():
            widget.bind("<MouseWheel>", self._on_layer_mousewheel)
        row.bind("<MouseWheel>", self._on_layer_mousewheel)

    def _toggle_expanded(self, layer):
        layer.expanded = not layer.expanded
        self._refresh_layers()

    def _on_layer_press(self, event, layer):
        if event.state & 0x0004:
            self._toggle_layer_selection(layer)
            self._drag_layer = None
            return "break"
        if event.state & 0x0001:
            self._select_layer_range(layer)
            self._drag_layer = None
            return "break"
        self._select_layer(layer)
        self._drag_layer = layer
        self._drag_origin = (event.x_root, event.y_root)
        self._drag_moved = False
        self._drag_blocked = False
        self._drag_in_panel = True

    def _add_format_menu(self, parent, layer, options, current, setter):
        format_menu = tk.Menu(
            parent,
            tearoff=0,
            bg=PANEL_BG,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=TEXT,
            selectcolor=ACCENT,
            bd=0,
        )
        variables = []
        for value, label in options:
            variable = tk.BooleanVar(value=current == value)
            variables.append(variable)
            format_menu.add_checkbutton(
                label=label,
                variable=variable,
                onvalue=True,
                offvalue=False,
                command=lambda v=value, target=layer: setter(target, v),
            )
        format_menu._check_vars = variables
        parent.add_cascade(label="Định dạng", menu=format_menu)
        return format_menu

    def _on_layer_context(self, event, layer):
        if layer not in self.selected_layers:
            self._select_layer(layer)
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=PANEL_BG,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=TEXT,
            selectcolor=ACCENT,
            bd=0,
        )
        export_menu = tk.Menu(
            menu,
            tearoff=0,
            bg=PANEL_BG,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=TEXT,
            bd=0,
        )
        for kind, label in (
            ("png", "PNG (.png)"),
            ("jpg", "JPG (.jpg)"),
            ("webp", "WebP (.webp)"),
            ("svg", "SVG (.svg)"),
        ):
            export_menu.add_command(
                label=label,
                command=lambda value=kind, target=layer: self._export_layer(
                    target, value
                ),
            )
        menu.add_cascade(label="Xuất layer", menu=export_menu)
        menu.add_command(
            label="Tùy chọn CSS (::before / ::after)…",
            command=lambda target=layer: self._open_layer_options(target),
        )
        if layer.children:
            menu.add_separator()
            self._add_format_menu(
                menu,
                layer,
                (
                    ("text", "Text"),
                    ("h1", "H1"),
                    ("h2", "H2"),
                    ("h3", "H3"),
                    ("h4", "H4"),
                    ("h5", "H5"),
                    ("h6", "H6"),
                ),
                layer.group_tag,
                self._set_group_format,
            )
        elif self._layer_text_style(layer) is not None:
            menu.add_separator()
            self._add_format_menu(
                menu,
                layer,
                (
                    ("text", "Text"),
                    ("span", "Span"),
                    ("strong", "Strong"),
                ),
                layer.text_format,
                self._set_text_format,
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    def _open_layer_options(self, layer):
        self._commit_text_editor()
        window = self._layer_options_window
        if window is not None and window.winfo_exists():
            window.lift()
            window.focus_force()
            return

        window = tk.Toplevel(self)
        self._layer_options_window = window
        window.title(f"Tùy chọn CSS — {layer.name}")
        window.configure(bg=PANEL_BG)
        window.resizable(False, False)
        window.transient(self)
        window.protocol(
            "WM_DELETE_WINDOW",
            lambda: self._close_layer_options(window),
        )
        window.bind(
            "<Escape>", lambda _e: self._close_layer_options(window)
        )

        body = tk.Frame(window, bg=PANEL_BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Tùy chọn CSS",
            font=self.font_brand,
            fg=TEXT,
            bg=PANEL_BG,
        ).pack(anchor="w")
        tk.Label(
            body,
            text="Thiết lập ::before và ::after cho layer. Các khai báo "
            "được thêm vào style.css khi export HTML. Position mặc định "
            "là absolute; Top/Left/Bottom/Right nhận px hoặc %. Chọn "
            "Display: inline-block nếu muốn width/height có hiệu lực.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            justify="left",
        ).pack(anchor="w", pady=(4, 14))

        sections = tk.Frame(body, bg=PANEL_BG)
        sections.pack(fill="both", expand=True)
        forms = {}
        for column, pseudo in enumerate(PSEUDO_KEYS):
            sections.grid_columnconfigure(column, weight=1)
            forms[pseudo] = self._build_pseudo_form(
                sections, layer, pseudo, column
            )

        actions = tk.Frame(body, bg=PANEL_BG)
        actions.pack(fill="x", pady=(16, 0))
        tk.Button(
            actions,
            text="Hủy",
            command=lambda: self._close_layer_options(window),
            font=self.font_menu,
            fg=TEXT,
            bg=BORDER,
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="right")
        tk.Button(
            actions,
            text="Lưu",
            command=lambda: self._save_layer_options(layer, forms, window),
            font=self.font_menu,
            fg=BG,
            bg=ACCENT,
            activebackground="#60a5fa",
            activeforeground=BG,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="right", padx=(0, 8))

        window.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        x = self.winfo_rootx() + (self.winfo_width() - width) // 2
        y = self.winfo_rooty() + (self.winfo_height() - height) // 3
        window.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _build_pseudo_form(self, parent, layer, pseudo, column):
        data = self._layer_pseudo(layer, pseudo)
        frame = tk.LabelFrame(
            parent,
            text=f"::{pseudo}",
            font=self.font_panel,
            fg=MUTED,
            bg=PANEL_BG,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=12,
            pady=10,
        )
        frame.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0, 8) if column == 0 else (8, 0),
        )
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        enabled = tk.BooleanVar(value=data["enabled"])
        tk.Checkbutton(
            frame,
            text="Bật",
            variable=enabled,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT,
            bg=PANEL_BG,
            activebackground=PANEL_BG,
            activeforeground=TEXT,
            selectcolor=BG,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        variables = {}

        def add_field(row, column_index, key, title, width=12):
            tk.Label(
                frame,
                text=title,
                font=("Segoe UI", 9),
                fg=MUTED,
                bg=PANEL_BG,
                anchor="w",
            ).grid(row=row, column=column_index, sticky="w", pady=3)
            variable = tk.StringVar(value=data[key])
            entry = tk.Entry(
                frame,
                textvariable=variable,
                width=width,
                font=("Segoe UI", 9),
                fg=TEXT,
                bg="#0b1220",
                insertbackground=TEXT,
                relief="flat",
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=ACCENT,
            )
            entry.grid(
                row=row,
                column=column_index + 1,
                sticky="ew",
                padx=(4, 12),
                pady=3,
            )
            variables[key] = variable
            return entry

        tk.Label(
            frame,
            text="Content",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=3)
        content_var = tk.StringVar(value=data["content"])
        variables["content"] = content_var
        tk.Entry(
            frame,
            textvariable=content_var,
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        ).grid(row=1, column=1, columnspan=3, sticky="ew", pady=3)

        add_field(2, 0, "color", "Màu chữ")
        add_field(2, 2, "background", "Nền")
        add_field(3, 0, "width", "Width (px)")
        add_field(3, 2, "height", "Height (px)")
        add_field(4, 0, "margin", "Margin")
        add_field(4, 2, "padding", "Padding")
        add_field(5, 0, "font_size", "Font-size (px)")
        add_field(5, 2, "font_weight", "Font-weight")

        def add_menu(row, column_index, key, title, options):
            tk.Label(
                frame,
                text=title,
                font=("Segoe UI", 9),
                fg=MUTED,
                bg=PANEL_BG,
                anchor="w",
            ).grid(row=row, column=column_index, sticky="w", pady=3)
            labels = {value: label for label, value in options}
            reverse = {label: value for value, label in labels.items()}
            current = data[key] if data[key] in labels else options[0][1]
            variable = tk.StringVar(value=labels[current])
            menu = tk.OptionMenu(frame, variable, *labels.values())
            menu.configure(
                font=("Segoe UI", 9),
                fg=TEXT,
                bg="#0b1220",
                activebackground=HOVER_BG,
                activeforeground=TEXT,
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=ACCENT,
                relief="flat",
                bd=0,
                width=12,
                anchor="center",
                cursor="hand2",
            )
            menu["menu"].configure(
                font=("Segoe UI", 9),
                fg=TEXT,
                bg=PANEL_BG,
                activebackground=ACCENT,
                activeforeground=TEXT,
            )
            menu.grid(
                row=row,
                column=column_index + 1,
                sticky="ew",
                padx=(4, 12),
                pady=3,
            )
            return variable, reverse

        display_var, display_reverse = add_menu(
            6,
            0,
            "display",
            "Display",
            (
                ("Mặc định", ""),
                ("block", "block"),
                ("inline-block", "inline-block"),
                ("inline", "inline"),
                ("none", "none"),
                ("flex", "flex"),
            ),
        )
        position_var, position_reverse = add_menu(
            6,
            2,
            "position",
            "Position",
            tuple((name, name) for name in PSEUDO_POSITIONS),
        )

        add_field(7, 0, "top", "Top (px/%)")
        add_field(7, 2, "left", "Left (px/%)")
        add_field(8, 0, "bottom", "Bottom (px/%)")
        add_field(8, 2, "right", "Right (px/%)")
        transform_entry = add_field(9, 0, "transform", "Transform")
        transform_entry.grid_configure(columnspan=3)

        tk.Label(
            frame,
            text="CSS bổ sung",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="nw",
        ).grid(row=10, column=0, sticky="nw", pady=(6, 3))
        extra = tk.Text(
            frame,
            width=28,
            height=4,
            wrap="word",
            font=("Segoe UI", 9),
            fg=TEXT,
            bg="#0b1220",
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        extra.insert("1.0", data["extra"])
        extra.grid(
            row=10,
            column=1,
            columnspan=3,
            sticky="ew",
            pady=(6, 3),
        )

        return {
            "enabled": enabled,
            "fields": variables,
            "display": (display_var, display_reverse),
            "position": (position_var, position_reverse),
            "extra": extra,
        }

    def _save_layer_options(self, layer, forms, window):
        pseudo = {}
        for key in PSEUDO_KEYS:
            form = forms[key]
            data = {
                name: variable.get().strip()
                for name, variable in form["fields"].items()
            }
            data["enabled"] = bool(form["enabled"].get())
            display_var, display_reverse = form["display"]
            data["display"] = display_reverse.get(
                display_var.get(), ""
            )
            position_var, position_reverse = form["position"]
            data["position"] = position_reverse.get(
                position_var.get(), "absolute"
            )
            data["extra"] = form["extra"].get("1.0", "end").strip()
            pseudo[key] = data
        normalized = self._normalize_pseudo(pseudo)
        if normalized == self._normalize_pseudo(layer.pseudo):
            self._close_layer_options(window)
            return
        self._push_history()
        layer.pseudo = normalized
        self._close_layer_options(window)
        self._render_document()
        self._refresh_doc_tab()
        self._flash_status(
            f"Đã lưu tùy chọn CSS cho layer '{layer.name}'."
        )

    def _close_layer_options(self, window):
        if window is not None and window.winfo_exists():
            window.destroy()
        if self._layer_options_window is window:
            self._layer_options_window = None

    def _begin_rename(self, layer, label):
        entry = self._rename_entry
        if entry is not None and entry.winfo_exists():
            entry.focus_set()
            entry.select_range(0, "end")
            return "break"
        row = label.master
        info = label.pack_info()
        entry = tk.Entry(
            row,
            font=self.font_layer,
            fg=TEXT,
            bg=label.cget("bg"),
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT,
            highlightcolor=ACCENT,
            insertbackground=TEXT,
        )
        entry.insert(0, layer.name)
        entry.pack(
            side=info["side"],
            fill=info["fill"],
            expand=info["expand"],
            padx=info["padx"],
            pady=info["pady"],
        )
        bg_widgets = getattr(row, "_layer_bg_widgets", None)
        if bg_widgets is not None and label in bg_widgets:
            bg_widgets[bg_widgets.index(label)] = entry
        label.destroy()
        self._rename_entry = entry
        self._rename_layer = layer
        self._drag_layer = None
        self._drag_moved = False
        entry.bind(
            "<Return>", lambda _e, l=layer, w=entry: self._commit_rename(l, w)
        )
        entry.bind(
            "<KP_Enter>", lambda _e, l=layer, w=entry: self._commit_rename(l, w)
        )
        entry.bind("<Escape>", lambda _e, w=entry: self._cancel_rename(w))
        entry.bind(
            "<FocusOut>", lambda _e, l=layer, w=entry: self._commit_rename(l, w)
        )
        entry.focus_set()
        entry.select_range(0, "end")
        entry.icursor("end")
        return "break"

    def _commit_rename(self, layer, entry):
        if self._rename_entry is not entry or not entry.winfo_exists():
            return "break"
        self._rename_entry = None
        self._rename_layer = None
        name = entry.get().strip()
        entry.destroy()
        if name and name != layer.name:
            self._push_history()
            layer.name = name
            self._refresh_doc_tab()
        self._refresh_layers()
        return "break"

    def _cancel_rename(self, entry):
        if self._rename_entry is not entry or not entry.winfo_exists():
            return "break"
        self._rename_entry = None
        self._rename_layer = None
        entry.destroy()
        self._refresh_layers()
        return "break"

    def _commit_rename_if_outside(self, event):
        entry = self._rename_entry
        if entry is None or not entry.winfo_exists():
            return
        widget = event.widget
        if widget is None or not widget.winfo_exists():
            return
        while widget is not None:
            if widget is entry:
                return
            widget = getattr(widget, "master", None)
        self._commit_rename(self._rename_layer, entry)

    def _find_layer_row(self, x_root, y_root):
        widget = self.winfo_containing(x_root, y_root)
        while widget is not None:
            if hasattr(widget, "_layer_base_bg"):
                return widget
            widget = widget.master
        return None

    def _is_in_layer_panel(self, x_root, y_root):
        widget = self.winfo_containing(x_root, y_root)
        while widget is not None:
            if (
                widget is self.layer_list
                or widget is self.layer_list_canvas
                or widget is self.layer_count_label
            ):
                return True
            if widget is self:
                return False
            widget = widget.master
        return False

    def _on_layer_drag(self, event):
        if self._drag_layer is None:
            return
        dx = event.x_root - self._drag_origin[0]
        dy = event.y_root - self._drag_origin[1]
        if not self._drag_moved:
            if abs(dx) < 4 and abs(dy) < 4:
                return
            self._drag_moved = True
            self.configure(cursor="fleur")

        self._drag_in_panel = self._is_in_layer_panel(event.x_root, event.y_root)
        row = self._find_layer_row(event.x_root, event.y_root)
        self._drag_blocked = False
        mode = None
        if row is not None:
            target = row._layer
            if target is self._drag_layer or self._is_descendant(
                target, self._drag_layer
            ):
                row = None
                self._drag_blocked = True
            else:
                ratio = (event.y_root - row.winfo_rooty()) / max(
                    row.winfo_height(), 1
                )
                if ratio < 0.3:
                    mode = "above"
                elif ratio > 0.7:
                    mode = "below"
                else:
                    mode = "into"
        self._set_drop_target(row, mode)

    def _on_layer_release(self, event):
        if self._drag_layer is None:
            return
        layer = self._drag_layer
        moved = self._drag_moved
        row = self._drop_row
        mode = self._drop_mode
        blocked = self._drag_blocked
        in_panel = self._drag_in_panel

        self._clear_drop_highlight()
        if moved:
            self.configure(cursor="")
        self._drag_layer = None
        self._drag_moved = False
        self._drag_blocked = False
        self._drag_in_panel = False

        if not moved or blocked:
            return
        if row is not None and mode is not None:
            self._apply_layer_drop(layer, row, mode)
        elif in_panel:
            self._move_layer_to_root(layer)

    def _apply_layer_drop(self, layer, row, mode):
        target = row._layer
        if mode == "into":
            self._move_layer_into(layer, target)
            return
        if mode == "below" and target.children and target.expanded:
            index = len(target.children) - (
                1 if layer.parent is target else 0
            )
            self._move_layer_to(layer, target, index)
            return
        parent = target.parent
        siblings = parent.children if parent else self.layers
        index = 0
        for node in siblings:
            if node is layer:
                continue
            if node is target:
                break
            index += 1
        if mode == "above":
            index += 1
        self._move_layer_to(layer, parent, index)

    def _set_drop_target(self, row, mode):
        if row is self._drop_row and mode == self._drop_mode:
            return
        self._clear_drop_highlight()
        if row is None or mode is None:
            return
        self._drop_row = row
        self._drop_mode = mode
        if mode == "into":
            for widget in row._layer_bg_widgets:
                widget.configure(bg=DROP_BG)
            self._draw_eye(row._layer_eye, row._layer.visible, DROP_BG)
            if row._layer_expander is not None:
                self._draw_expander(row._layer_expander, row._layer.expanded)
            return
        y = row.winfo_y()
        if mode == "below":
            y += row.winfo_height() - 2
        self._drop_indicator.place(x=0, y=y, relwidth=1, height=2)
        self._drop_indicator.lift()

    def _clear_drop_highlight(self):
        if self._drop_indicator is not None:
            self._drop_indicator.place_forget()
        row = self._drop_row
        self._drop_row = None
        self._drop_mode = None
        if row is None:
            return
        bg = row._layer_base_bg
        for widget in row._layer_bg_widgets:
            widget.configure(bg=bg)
        self._draw_eye(row._layer_eye, row._layer.visible, bg)
        if row._layer_expander is not None:
            self._draw_expander(row._layer_expander, row._layer.expanded)

    def _move_layer_to(self, layer, parent, index):
        old_parent = layer.parent
        old_siblings = old_parent.children if old_parent else self.layers
        old_index = old_siblings.index(layer)
        if parent is old_parent and index == old_index:
            return
        self._push_history()
        old_siblings.remove(layer)
        layer.parent = parent
        if parent is not None:
            parent.children.insert(index, layer)
            parent.expanded = True
        else:
            self.layers.insert(index, layer)
        self.active_layer = layer
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()

    def _move_layer_into(self, layer, target):
        index = len(target.children) - (1 if layer.parent is target else 0)
        self._move_layer_to(layer, target, index)

    def _move_layer_to_root(self, layer):
        index = len(self.layers) - (1 if layer.parent is None else 0)
        self._move_layer_to(layer, None, index)

    def _draw_expander(self, canvas, expanded):
        canvas.delete("all")
        if expanded:
            canvas.create_polygon(3, 8, 9, 8, 6, 12, fill=TEXT, outline="")
        else:
            canvas.create_polygon(4, 6, 4, 14, 9, 10, fill=TEXT, outline="")

    def _draw_eye(self, canvas, visible, bg):
        canvas.delete("all")
        color = TEXT if visible else MUTED
        canvas.create_oval(2, 5, 18, 15, outline=color, width=1.5)
        if visible:
            canvas.create_oval(7.5, 8, 12.5, 12, fill=color, outline="")
        else:
            canvas.create_line(3, 3, 17, 17, fill=color, width=1.5)

    def _text_record_at(self, x, y):
        if self.active_layer is None:
            return None
        for record, x1, y1, x2, y2 in reversed(self._text_areas):
            if not (x1 - 2 <= x <= x2 + 2 and y1 - 2 <= y <= y2 + 2):
                continue
            if any(record is entry for entry in self.active_layer.items):
                return record
        return None

    def _on_canvas_double_click(self, event):
        event = _DocEvent(event, self.zoom)
        if self._guide_at(event.x, event.y) is not None:
            return
        record = self._text_record_at(event.x, event.y)
        if record is None:
            return
        self._open_text_editor(record)

    def _open_text_editor(self, record):
        self._commit_text_editor()
        font = self._text_font(record, self.zoom)
        color = record.get("color") or TEXT
        line_gap = max(
            0,
            round(font.metrics("linespace") * (self._text_line_height(record) - 1)),
        )
        editor = tk.Text(
            self.doc_canvas,
            font=font,
            fg=color,
            bg=DOC_BG,
            insertbackground=color,
            selectbackground=ACCENT,
            selectforeground=BG,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=ACCENT,
            highlightcolor=ACCENT,
            wrap="none",
            spacing3=line_gap,
            padx=2,
            pady=1,
            undo=False,
        )
        editor.insert("1.0", record.get("text", ""))
        editor.tag_configure("align", justify=self._text_align(record))
        editor.tag_add("align", "1.0", "end")
        editor._editor_font = font
        self._text_editor = editor
        self._text_editor_record = record
        self._place_text_editor()
        editor.mark_set("insert", "end-1c")
        editor.bind("<KeyRelease>", lambda _e: self._place_text_editor())
        editor.bind("<FocusOut>", lambda _e: self._commit_text_editor())
        editor.bind("<Escape>", lambda _e: self._cancel_text_editor())
        editor.bind("<Control-z>", lambda _e: "break")
        editor.bind("<Control-Z>", lambda _e: "break")
        editor.focus_set()

    def _place_text_editor(self):
        editor = self._text_editor
        record = self._text_editor_record
        if editor is None or record is None:
            return
        font = editor._editor_font
        content = editor.get("1.0", "end-1c")
        if self._text_transform(record) == "uppercase":
            content = content.upper()
        lines = content.split("\n")
        line_gap = int(editor.cget("spacing3"))
        letter_spacing = self._text_letter_spacing(record) * self.zoom
        width = max((font.measure(line) for line in lines), default=0) + 14
        longest = max((len(line) for line in lines), default=0)
        if letter_spacing and longest > 1:
            width += int(letter_spacing * (longest - 1))
        height = (
            len(lines) * font.metrics("linespace")
            + len(lines) * line_gap
            + 10
        )
        frame = self._text_frame(record)
        dx, dy = self._record_offsets.get(id(record), (0.0, 0.0))
        if frame is not None:
            editor_x = (frame[0] + dx) * self.zoom
            width = max((frame[2] - frame[0]) * self.zoom + 6, 48)
        else:
            editor_x = (record["x"] + dx) * self.zoom
            width = max(width, 48)
        editor.tag_configure("align", justify=self._text_align(record))
        editor.tag_add("align", "1.0", "end")
        editor.place(
            x=editor_x - 3,
            y=(record["y"] + dy) * self.zoom - 3,
            width=width,
            height=max(height, font.metrics("linespace") + 10),
        )
        editor.lift()

    def _commit_text_editor(self):
        editor = self._text_editor
        record = self._text_editor_record
        if editor is None or record is None:
            return False
        self._text_editor = None
        self._text_editor_record = None
        try:
            content = editor.get("1.0", "end-1c")
        except tk.TclError:
            content = record.get("text", "")
        editor.destroy()
        if content == record.get("text", ""):
            return False
        self._push_history()
        record["text"] = content
        self._render_document()
        self._refresh_doc_tab()
        return True

    def _cancel_text_editor(self):
        editor = self._text_editor
        if editor is None:
            return "break"
        self._text_editor = None
        self._text_editor_record = None
        editor.destroy()
        return "break"

    def _marquee_span(self, x1, y1, x2, y2):
        x1, x2 = sorted((
            max(0, min(x1, self.content_width)),
            max(0, min(x2, self.content_width)),
        ))
        y1, y2 = sorted((
            max(0, min(y1, self.content_height)),
            max(0, min(y2, self.content_height)),
        ))
        return (x1, y1, x2, y2)

    def _finish_marquee(self, event):
        x1, y1 = self._marquee_start
        self._marquee_start = None
        self.doc_canvas.delete("marquee_preview")
        region = self._marquee_span(x1, y1, event.x, event.y)
        width = region[2] - region[0]
        height = region[3] - region[1]
        if width < 3 or height < 3:
            self.marquee_region = None
            self.doc_canvas.delete("marquee")
            self._flash_status("Đã bỏ vùng chọn.")
            return
        self.marquee_region = region
        self._draw_marquee_overlay()
        self._flash_status(
            f"Vùng chọn: {round(width)} × {round(height)} px"
            " — canh văn bản theo vùng này."
        )

    def _draw_marquee_overlay(self, region=None, tag="marquee"):
        self.doc_canvas.delete(tag)
        region = self.marquee_region if region is None else region
        if region is None:
            return
        zoom = self.zoom
        x1, y1, x2, y2 = [value * zoom for value in region]
        self.doc_canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=ACCENT, width=1, dash=(4, 3), tags=tag,
        )
        label = (
            f"{round(region[2] - region[0])} × "
            f"{round(region[3] - region[1])} px"
        )
        pad = 5
        chip_h = 18
        chip_w = self.font_marquee.measure(label) + pad * 2
        chip_x = x1
        chip_y = y1 - chip_h - 2
        if chip_y < 1:
            chip_y = max(min(y1 + 2, y2 - chip_h), 1)
        self.doc_canvas.create_rectangle(
            chip_x, chip_y, chip_x + chip_w, chip_y + chip_h,
            fill="#0b1220", outline=ACCENT, tags=tag,
        )
        self.doc_canvas.create_text(
            chip_x + pad, chip_y + chip_h / 2, text=label,
            fill="#e2e8f0", font=self.font_marquee, anchor="w", tags=tag,
        )

    def _on_canvas_press(self, event):
        event = _DocEvent(event, self.zoom)
        if self._text_editor is not None:
            self._commit_text_editor()
            return
        guide = self._guide_at(event.x, event.y)
        if guide is not None and self.active_tool_id == "move":
            self._moving_guide = guide
            self._guide_move_start = guide["pos"]
            return
        tool = self.active_tool_id
        zoom = self.zoom
        if tool == "marquee":
            self._marquee_start = (event.x, event.y)
            self.doc_canvas.delete("marquee_preview")
            return
        if tool in ("brush", "eraser") and not self._can_draw_on(
            self.active_layer
        ):
            self._flash_status(
                "Không thể vẽ vào nhóm, lớp văn bản, lớp hình hoặc"
                " lớp hình khối — chọn lớp thường để vẽ."
            )
            return
        if tool in ("brush", "eraser"):
            color = DOC_BG if tool == "eraser" else BRUSH_COLOR
            width = 18 if tool == "eraser" else 4
            self._stroke = {
                "coords": [event.x, event.y],
                "color": color,
                "width": width,
            }
            self._last_point = (event.x, event.y)
            radius = width / 2 * zoom
            dot = self.doc_canvas.create_oval(
                event.x * zoom - radius, event.y * zoom - radius,
                event.x * zoom + radius, event.y * zoom + radius,
                fill=color, outline="", tags="temp",
            )
            self._temp_ids = [dot]
        elif tool == "rect":
            self._rect_start = (event.x, event.y)
            preview = (
                self.doc_canvas.create_oval
                if self.rect_tool_shape == "ellipse"
                else self.doc_canvas.create_rectangle
            )
            self._rect_preview = preview(
                event.x * zoom, event.y * zoom,
                event.x * zoom, event.y * zoom,
                outline=BRUSH_COLOR, width=2, dash=(4, 2), tags="temp",
            )
        elif tool == "text":
            if self._text_record_at(event.x, event.y) is not None:
                return
            content = simpledialog.askstring("Văn bản", "Nhập nội dung:", parent=self)
            if content:
                self._push_history()
                record = {
                    "type": "text",
                    "x": event.x,
                    "y": event.y,
                    "text": content,
                    "color": "#0f172a",
                    "font_family": "none",
                    "font_size": 14,
                    "font_weight": 400,
                    "line_height": 1.4,
                    "letter_spacing": 0,
                    "text_transform": "none",
                    "text_align": "left",
                    "text_tag": "p",
                }
                self._create_layer(self._next_layer_name("Văn bản"))
                self.active_layer.items.append(record)
                self._refresh_layers()
                self._draw_record(record)
                self._refresh_doc_tab()
        elif tool == "move":
            if self.active_layer is not None and self._has_drawable_items(
                self.active_layer
            ):
                self._move_last = (event.x, event.y)
                self._move_moved = False

    def _on_canvas_drag(self, event):
        event = _DocEvent(event, self.zoom)
        if self._moving_guide is not None:
            self._move_guide_to(
                event.y
                if self._moving_guide["orient"] == "h"
                else event.x
            )
            return
        tool = self.active_tool_id
        zoom = self.zoom
        if tool == "marquee" and self._marquee_start is not None:
            x1, y1 = self._marquee_start
            region = self._marquee_span(x1, y1, event.x, event.y)
            self._draw_marquee_overlay(region, tag="marquee_preview")
        elif tool in ("brush", "eraser") and self._stroke is not None:
            last_x, last_y = self._last_point
            if (event.x, event.y) == (last_x, last_y):
                return
            segment = self.doc_canvas.create_line(
                last_x * zoom, last_y * zoom, event.x * zoom,
                event.y * zoom,
                fill=self._stroke["color"],
                width=max(1, round(self._stroke["width"] * zoom)),
                capstyle="round", tags="temp",
            )
            self._temp_ids.append(segment)
            self._stroke["coords"].extend([event.x, event.y])
            self._last_point = (event.x, event.y)
        elif tool == "rect" and self._rect_preview is not None:
            x1, y1 = self._rect_start
            self.doc_canvas.coords(
                self._rect_preview,
                x1 * zoom, y1 * zoom, event.x * zoom, event.y * zoom,
            )
        elif tool == "move" and self._move_last is not None:
            dx = event.x - self._move_last[0]
            dy = event.y - self._move_last[1]
            if dx == 0 and dy == 0:
                return
            if not self._move_moved:
                self._push_history()
                self._move_moved = True
            self._move_last = (event.x, event.y)
            self._translate_layer(self.active_layer, dx, dy)
            self._render_document()
            self._refresh_layer_position()

    def _on_canvas_release(self, event):
        native_event = event
        event = _DocEvent(event, self.zoom)
        if self._moving_guide is not None:
            guide = self._moving_guide
            self._moving_guide = None
            if guide["pos"] != self._guide_move_start:
                self._refresh_doc_tab()
            self._on_canvas_motion(native_event)
            return
        tool = self.active_tool_id
        if tool == "marquee" and self._marquee_start is not None:
            self._finish_marquee(event)
            return
        if self._stroke is not None:
            for item_id in self._temp_ids:
                self.doc_canvas.delete(item_id)
            self._temp_ids = []
            coords = self._stroke["coords"]
            if len(coords) >= 4:
                record = {
                    "type": "line",
                    "coords": coords,
                    "color": self._stroke["color"],
                    "width": self._stroke["width"],
                }
            else:
                record = {
                    "type": "dot",
                    "x": coords[0],
                    "y": coords[1],
                    "r": self._stroke["width"] / 2,
                    "color": self._stroke["color"],
                }
            self._stroke = None
            self._push_history()
            self.active_layer.items.append(record)
            self._draw_record(record)
            self._refresh_doc_tab()
            self._refresh_layer_position()
        elif tool == "rect" and self._rect_preview is not None:
            x1, y1 = self._rect_start
            self.doc_canvas.delete(self._rect_preview)
            self._rect_preview = None
            x2, y2 = event.x, event.y
            if abs(x2 - x1) >= 3 and abs(y2 - y1) >= 3:
                kind = (
                    "ellipse"
                    if self.rect_tool_shape == "ellipse"
                    else "rect"
                )
                record = {
                    "type": kind,
                    "x1": min(x1, x2),
                    "y1": min(y1, y2),
                    "x2": max(x1, x2),
                    "y2": max(y1, y2),
                    "border_color": BRUSH_COLOR,
                    "border_width": 2,
                    "background": "",
                }
                self._push_history()
                layer = self._create_layer(
                    self._next_layer_name(
                        "Hình elip" if kind == "ellipse" else "Hình chữ nhật"
                    )
                )
                layer.items.append(record)
                self._refresh_layers()
                self._draw_record(record)
                self._refresh_doc_tab()
        elif tool == "move" and self._move_last is not None:
            moved = self._move_moved
            self._move_last = None
            self._move_moved = False
            if moved:
                self._refresh_info()
                self._refresh_doc_tab()

    def _insert_image(self, _event=None):
        self._commit_text_editor()
        path = filedialog.askopenfilename(
            parent=self,
            title="Chèn hình",
            filetypes=[
                ("Hình ảnh", IMAGE_FILE_PATTERN),
                ("Tất cả tệp", "*.*"),
            ],
        )
        if not path:
            return
        try:
            with open(path, "rb") as handle:
                raw = handle.read()
            data, mime, width, height = self._prepare_image(raw, path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Lỗi chèn hình", str(error), parent=self)
            return

        canvas_width = max(
            round(self.doc_canvas.winfo_width() / self.zoom), 1
        )
        canvas_height = max(
            round(self.doc_canvas.winfo_height() / self.zoom), 1
        )
        x = max((canvas_width - width) // 2, 10)
        y = max((canvas_height - height) // 2, 10)
        record = {
            "type": "image",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "data": data,
            "mime": mime,
            "border_color": BRUSH_COLOR,
            "border_width": 0,
        }
        self._push_history()
        self._create_layer(self._next_layer_name("Hình ảnh"))
        self.active_layer.items.append(record)
        self._refresh_layers()
        self._draw_record(record)
        self._refresh_doc_tab()

    def _prepare_image(self, raw, path):
        if Image is not None:
            try:
                with Image.open(BytesIO(raw)) as image:
                    image.load()
                    width, height = image.size
                    buffer = BytesIO()
                    image.convert("RGBA").save(buffer, format="PNG")
            except Exception as error:
                raise ValueError("Không đọc được tệp hình ảnh.") from error
            data = base64.b64encode(buffer.getvalue()).decode("ascii")
            return data, "image/png", width, height

        extension = os.path.splitext(path)[1].lower()
        if extension not in (".png", ".gif"):
            raise ValueError(
                "Cần cài Pillow để chèn định dạng hình này."
            )
        data = base64.b64encode(raw).decode("ascii")
        try:
            photo = tk.PhotoImage(data=data)
        except tk.TclError as error:
            raise ValueError("Không đọc được tệp hình ảnh.") from error
        mime = "image/png" if extension == ".png" else "image/gif"
        return data, mime, photo.width(), photo.height()

    def _make_photo(self, record):
        data = record.get("data")
        if not data:
            return None
        try:
            return tk.PhotoImage(data=data)
        except tk.TclError:
            if Image is None:
                return None
        try:
            raw = base64.b64decode(data)
            with Image.open(BytesIO(raw)) as image:
                buffer = BytesIO()
                image.convert("RGBA").save(buffer, format="PNG")
            return tk.PhotoImage(
                data=base64.b64encode(buffer.getvalue()).decode("ascii")
            )
        except Exception:
            return None

    def _scale_photo(self, record, photo, width, height):
        if photo.width() == width and photo.height() == height:
            return photo
        if Image is None:
            return photo
        key = (id(record), width, height)
        scaled = self._image_scaled.get(key)
        if scaled is not None:
            return scaled
        data = record.get("data")
        if not data:
            return photo
        try:
            raw = base64.b64decode(data)
            with Image.open(BytesIO(raw)) as image:
                resized = image.convert("RGBA").resize((width, height))
                buffer = BytesIO()
                resized.save(buffer, format="PNG")
            scaled = tk.PhotoImage(
                data=base64.b64encode(buffer.getvalue()).decode("ascii")
            )
        except Exception:
            return photo
        self._image_scaled[key] = scaled
        return scaled

    def _background_photo(self, record, width, height):
        size = self._background_setting(record, "size")
        position = self._background_setting(record, "position")
        repeat = self._background_setting(record, "repeat")
        key = (id(record), width, height, size, position, repeat)
        cached = self._image_scaled.get(key)
        if cached is not None:
            return cached
        data = record.get("data")
        if not data:
            return None
        if Image is not None:
            photo = self._compose_background(
                data, width, height, size, position, repeat
            )
            if photo is not None:
                self._image_scaled[key] = photo
                return photo
        photo = self._make_photo(record)
        if photo is None:
            return None
        photo = self._scale_photo(record, photo, width, height)
        self._image_scaled[key] = photo
        return photo

    def _compose_background(self, data, width, height, size, position,
                            repeat):
        try:
            raw = base64.b64decode(data)
            with Image.open(BytesIO(raw)) as source:
                image = source.convert("RGBA")
        except Exception:
            return None
        source_width, source_height = image.size
        if source_width < 1 or source_height < 1:
            return None
        if size == "contain":
            scale = min(width / source_width, height / source_height)
        else:
            scale = max(width / source_width, height / source_height)
        tile_width = max(round(source_width * scale), 1)
        tile_height = max(round(source_height * scale), 1)
        resample = getattr(Image, "Resampling", Image).LANCZOS
        tile = image.resize((tile_width, tile_height), resample)
        composed = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        if position == "left":
            offset_x = 0
        elif position == "right":
            offset_x = width - tile_width
        else:
            offset_x = (width - tile_width) // 2
        offset_y = 0 if position == "top" else (height - tile_height) // 2
        if repeat == "repeat":
            start_x = offset_x % tile_width
            start_y = offset_y % tile_height
            y = start_y - tile_height
            while y < height:
                x = start_x - tile_width
                while x < width:
                    composed.paste(tile, (x, y), tile)
                    x += tile_width
                y += tile_height
        else:
            composed.paste(tile, (offset_x, offset_y), tile)
        buffer = BytesIO()
        composed.save(buffer, format="PNG")
        return tk.PhotoImage(
            data=base64.b64encode(buffer.getvalue()).decode("ascii")
        )

    def _has_drawable_items(self, layer):
        if layer.items:
            return True
        return any(self._has_drawable_items(child) for child in layer.children)

    def _translate_layer(self, layer, dx, dy):
        for record in layer.items:
            self._translate_record(record, dx, dy)
        for child in layer.children:
            self._translate_layer(child, dx, dy)

    def _translate_record(self, record, dx, dy):
        kind = record.get("type")
        if kind == "line":
            record["coords"] = [
                value + (dx if index % 2 == 0 else dy)
                for index, value in enumerate(record["coords"])
            ]
        elif kind in ("dot", "text", "image"):
            record["x"] += dx
            record["y"] += dy
            if kind == "text":
                frame = self._text_frame(record)
                if frame is not None:
                    record["text_frame"] = [
                        frame[0] + dx, frame[1] + dy,
                        frame[2] + dx, frame[3] + dy,
                    ]
        elif kind in ("rect", "ellipse"):
            record["x1"] += dx
            record["y1"] += dy
            record["x2"] += dx
            record["y2"] += dy

    def _text_weight_value(self, record):
        weight = record.get("font_weight", 400)
        if isinstance(weight, str):
            lowered = weight.strip().lower()
            if lowered == "normal":
                return 400
            if lowered == "bold":
                return 700
            try:
                weight = int(lowered)
            except ValueError:
                return 400
        try:
            return max(100, min(900, int(weight)))
        except (TypeError, ValueError):
            return 400

    def _text_family(self, record):
        return str(record.get("font_family", "none")).strip() or "none"

    def _text_font(self, record, zoom=1.0):
        weight = "bold" if self._text_weight_value(record) >= 600 else "normal"
        family = self._text_family(record)
        if family == "none":
            family = (
                self.body_font_family
                if self.body_font_family != "none"
                else "Segoe UI"
            )
        size = max(int(round(int(record.get("font_size", 14)) * zoom)), 1)
        if record.get("font_px"):
            size = -size
        key = (family, size, weight)
        font = self._font_cache.get(key)
        if font is None:
            font = tkfont.Font(family=family, size=size, weight=weight)
            self._font_cache[key] = font
        return font

    def _text_line_height(self, record):
        try:
            return max(float(record.get("line_height", 1.4)), 0.5)
        except (TypeError, ValueError):
            return 1.4

    def _text_transform(self, record):
        return (
            "uppercase"
            if str(record.get("text_transform", "none")).lower() == "uppercase"
            else "none"
        )

    def _text_align_state(self, record):
        align = str(record.get("text_align", "left")).lower()
        return align if align in ("left", "center", "right") else "none"

    def _text_align(self, record):
        align = self._text_align_state(record)
        return "left" if align == "none" else align

    def _text_tag(self, record):
        tag = str(record.get("text_tag", "p")).lower()
        return tag if tag in TEXT_TAGS else "p"

    def _text_frame(self, record):
        frame = record.get("text_frame")
        if not isinstance(frame, (list, tuple)) or len(frame) != 4:
            return None
        try:
            x1, y1, x2, y2 = (float(value) for value in frame)
        except (TypeError, ValueError):
            return None
        if x2 <= x1 or y2 <= y1:
            return None
        return (x1, y1, x2, y2)

    def _text_block_start(self, record, block_width, layer=None):
        frame = self._text_frame(record)
        if frame is None:
            if self._text_align_state(record) == "none":
                return record["x"]
            if self._text_align(record) == "left":
                return record["x"]
            frame = self._text_group_frame(layer)
        if frame is None:
            return record["x"]
        x1, _y1, x2, _y2 = frame
        frame_width = x2 - x1
        align = self._text_align(record)
        if align == "center":
            return x1 + (frame_width - block_width) / 2
        if align == "right":
            return x1 + frame_width - block_width
        return x1

    def _text_group_frame(self, layer):
        group = layer.parent if layer is not None else None
        if group is None:
            return None
        shapes = []

        def collect(item_layer):
            for record in item_layer.items:
                if record.get("type") in ("rect", "ellipse"):
                    shapes.append(record)
            for child in item_layer.children:
                if child.visible:
                    collect(child)

        collect(group)
        if shapes:
            shape = max(
                shapes, key=lambda record: record["x2"] - record["x1"]
            )
            return (shape["x1"], shape["y1"], shape["x2"], shape["y2"])
        bounds = self._layer_content_bounds(group)
        if bounds is None:
            if not group.background_image:
                return None
            bounds = self._layer_background_bounds(group)
        return bounds

    def _text_display_text(self, record):
        text = str(record.get("text", ""))
        return text.upper() if self._text_transform(record) == "uppercase" else text

    def _text_letter_spacing(self, record):
        try:
            return float(record.get("letter_spacing", 0))
        except (TypeError, ValueError):
            return 0.0

    def _text_metrics(self, record):
        font = self._text_font(record)
        line_height = self._text_line_height(record)
        letter_spacing = self._text_letter_spacing(record)
        advance = max(
            int(round(font.metrics("linespace") * line_height)), 1
        )
        lines = self._text_display_text(record).split("\n")
        widths = []
        for line in lines:
            if letter_spacing:
                width = (
                    sum(font.measure(ch) + letter_spacing for ch in line)
                    - letter_spacing
                )
                widths.append(max(width, 0))
            else:
                widths.append(font.measure(line))
        height = advance * (len(lines) - 1) + font.metrics("linespace")
        return font, lines, widths, advance, letter_spacing, height

    def _draw_text_record(self, record, dx=0.0, dy=0.0, layer=None):
        font, lines, widths, advance, letter_spacing, height = (
            self._text_metrics(record)
        )
        y = record["y"] + dy
        block_width = max(widths, default=0)
        block_start = (
            self._text_block_start(record, block_width, layer) + dx
        )
        self._text_areas.append(
            (record, block_start, y, block_start + block_width, y + height)
        )
        color = record.get("color") or TEXT
        align = self._text_align(record)
        zoom = self.zoom
        draw_font = font if zoom == 1 else self._text_font(record, zoom)
        x = block_start * zoom
        y *= zoom
        advance *= zoom
        letter_spacing *= zoom
        for index, line in enumerate(lines):
            line_x = x
            if align == "center":
                line_x += (block_width - widths[index]) / 2 * zoom
            elif align == "right":
                line_x += (block_width - widths[index]) * zoom
            line_y = y + index * advance
            if letter_spacing:
                cursor = line_x
                for char in line:
                    self.doc_canvas.create_text(
                        cursor, line_y, text=char, fill=color,
                        font=draw_font, anchor="nw",
                    )
                    cursor += draw_font.measure(char) + letter_spacing
            else:
                self.doc_canvas.create_text(
                    line_x, line_y, text=line, fill=color, font=draw_font,
                    anchor="nw",
                )

    def _draw_record(
        self, record, dx=0.0, dy=0.0, stretch_width=None, layer=None
    ):
        kind = record["type"]
        zoom = self.zoom
        self._record_offsets[id(record)] = (dx, dy)
        if kind == "line":
            coords = list(record["coords"])
            for index in range(0, len(coords), 2):
                coords[index] += dx
                coords[index + 1] += dy
            self.doc_canvas.create_line(
                *[value * zoom for value in coords],
                fill=record["color"],
                width=max(1, round(record["width"] * zoom)),
                capstyle="round", joinstyle="round",
            )
        elif kind == "dot":
            x = (record["x"] + dx) * zoom
            y = (record["y"] + dy) * zoom
            radius = record["r"] * zoom
            self.doc_canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=record["color"], outline="",
            )
        elif kind == "rect":
            x2 = (
                record["x1"] + stretch_width
                if stretch_width is not None
                else record["x2"]
            )
            border_width, border_color = self._record_border(record, 2)
            self.doc_canvas.create_rectangle(
                (record["x1"] + dx) * zoom, (record["y1"] + dy) * zoom,
                (x2 + dx) * zoom, (record["y2"] + dy) * zoom,
                outline=border_color,
                width=max(1, round(border_width * zoom)),
                fill=record.get("background") or "",
            )
        elif kind == "ellipse":
            x2 = (
                record["x1"] + stretch_width
                if stretch_width is not None
                else record["x2"]
            )
            border_width, border_color = self._record_border(record, 2)
            self.doc_canvas.create_oval(
                (record["x1"] + dx) * zoom, (record["y1"] + dy) * zoom,
                (x2 + dx) * zoom, (record["y2"] + dy) * zoom,
                outline=border_color,
                width=max(1, round(border_width * zoom)),
                fill=record.get("background") or "",
            )
        elif kind == "text":
            self._draw_text_record(record, dx, dy, layer)
        elif kind == "image":
            photo = self._image_refs.get(id(record))
            if photo is None:
                photo = self._make_photo(record)
                if photo is None:
                    return
                self._image_refs[id(record)] = photo
            image_width = (
                stretch_width
                if stretch_width is not None
                else int(record.get("width", photo.width()))
            )
            width = max(round(image_width * zoom), 1)
            height = max(
                round(int(record.get("height", photo.height())) * zoom), 1
            )
            photo = self._scale_photo(record, photo, width, height)
            x = (record["x"] + dx) * zoom
            y = (record["y"] + dy) * zoom
            self.doc_canvas.create_image(x, y, image=photo, anchor="nw")
            border_width, border_color = self._record_border(record)
            if border_width > 0:
                self.doc_canvas.create_rectangle(
                    x, y, x + width, y + height,
                    outline=border_color,
                    width=max(1, round(border_width * zoom)),
                )

    def _render_document(self):
        self.doc_canvas.delete("all")
        self._image_refs.clear()
        self._image_scaled.clear()
        self._text_areas.clear()
        self._record_offsets.clear()
        self._draw_page_background()
        self._draw_layers(self.layers)
        self._draw_guides()
        self._draw_marquee_overlay()

    def _draw_page_background(self):
        if self._page_background() != "none":
            return
        width, height = self._page_pixel_size()
        self.doc_canvas.create_rectangle(
            -1, -1, width + 1, height + 1,
            fill=TRANSPARENT_BG, outline="", stipple="gray50",
            tags=("page-background",),
        )

    def _draw_layers(
        self, layers, dx=0.0, dy=0.0, stretch_width=None,
        children_dx=None, children_dy=None,
    ):
        base_dx = dx if children_dx is None else children_dx
        base_dy = dy if children_dy is None else children_dy
        for layer in layers:
            if not layer.visible:
                continue
            self._draw_layer_background(layer, dx, dy, stretch_width)
            self._draw_layer_pseudo(layer, "before", dx, dy)
            for record in layer.items:
                self._draw_record(record, dx, dy, stretch_width, layer)
            offsets = {}
            display = self._layer_display(layer)
            if layer.children and display == "flex":
                offsets = self._flex_child_offsets(layer)
            elif layer.children and display == "grid":
                offsets = self._grid_child_offsets(layer)
            for child in layer.children:
                if not child.visible:
                    continue
                child_dx, child_dy, child_stretch = offsets.get(
                    id(child), (0.0, 0.0, None)
                )
                keep_design = (
                    display == "flex"
                    and child.children
                    and self._is_flex_fill_layer(child)
                )
                self._draw_layers(
                    [child],
                    base_dx + child_dx,
                    base_dy + child_dy,
                    child_stretch,
                    children_dx=base_dx if keep_design else None,
                    children_dy=base_dy if keep_design else None,
                )
            self._draw_layer_pseudo(layer, "after", dx, dy)

    def _is_flex_fill_layer(self, layer):
        if (
            self._is_text_layer(layer)
            or not any(
                record.get("type") in ("rect", "ellipse", "image")
                for record in layer.items
            )
        ):
            return False
        bounds = self._record_bounds(layer.items)
        if bounds is None:
            return False
        return bounds[2] - bounds[0] <= 1

    def _flex_child_bounds(self, child):
        box = self._layer_css_box(child)
        if box is None:
            box = self._group_css_box(child)
        if box is None:
            return None
        return (
            box["x"], box["y"],
            box["x"] + box["width"], box["y"] + box["height"],
        )

    def _flex_child_offsets(self, layer):
        box = self._layer_css_box(layer)
        if box is None:
            box = self._group_css_box(layer)
        children = [child for child in layer.children if child.visible]
        if not children:
            return {}
        bounds = [self._flex_child_bounds(child) for child in children]
        widths = [
            max(bound[2] - bound[0], 0) if bound else 0
            for bound in bounds
        ]
        justify = self._layer_justify(layer)
        gap = self._layer_gap(layer)
        fills = [self._is_flex_fill_layer(child) for child in children]
        count = len(children)
        if any(fills):
            margins = []
            for index, bound in enumerate(bounds):
                if justify != "left" or index == 1 or bound is None:
                    margins.append(0.0)
                else:
                    margins.append(bound[0] - box["x"])
            fixed = sum(
                width for width, fill in zip(widths, fills) if not fill
            )
            used = fixed + sum(margins) + gap * (count - 1)
            share = max(box["width"] - used, 0) / sum(fills)
            offsets = {}
            cursor = box["x"]
            for child, bound, width, fill, margin in zip(
                children, bounds, widths, fills, margins
            ):
                draw_width = share if fill else width
                start = cursor + margin
                if bound is not None:
                    offsets[id(child)] = (
                        start - bound[0],
                        0.0,
                        share if fill else None,
                    )
                cursor = start + draw_width + gap
            return offsets
        offsets = {}
        if justify == "left":
            cursor = box["x"]
            for index, (child, bound, width) in enumerate(
                zip(children, bounds, widths)
            ):
                left = 0.0
                if index != 1 and bound is not None:
                    left = bound[0] - box["x"]
                start = cursor + left
                if bound is not None:
                    offsets[id(child)] = (start - bound[0], 0.0, None)
                cursor = start + width + gap
            return offsets
        total = sum(widths) + gap * (count - 1)
        free = box["width"] - total
        if justify == "between" and count > 1:
            step = gap + free / (count - 1)
        else:
            step = gap
        if justify == "center":
            cursor = box["x"] + free / 2
        elif justify == "right":
            cursor = box["x"] + free
        else:
            cursor = box["x"]
        for child, bound, width in zip(children, bounds, widths):
            if bound is not None:
                offsets[id(child)] = (cursor - bound[0], 0.0, None)
            cursor += width + step
        return offsets

    def _grid_child_offsets(self, layer):
        gap = self._layer_gap(layer)
        if not gap:
            return {}
        offsets = {}
        row = 0
        for child in layer.children:
            if not child.visible:
                continue
            offsets[id(child)] = (0.0, gap * row, None)
            row += 1
        return offsets

    def _draw_layer_background(
        self, layer, dx=0.0, dy=0.0, stretch_width=None
    ):
        image = layer.background_image
        if not image or not image.get("data"):
            return
        x1, y1, x2, y2 = self._layer_background_bounds(layer)
        if stretch_width is not None:
            x2 = x1 + stretch_width
        x1 += dx
        y1 += dy
        zoom = self.zoom
        width = max(round((x2 - x1) * zoom), 1)
        height = max(round((y2 - y1) * zoom), 1)
        photo = self._background_photo(image, width, height)
        if photo is None:
            return
        self.doc_canvas.create_image(
            x1 * zoom, y1 * zoom, image=photo, anchor="nw"
        )

    def _pseudo_token(self, token):
        token = str(token).strip()
        if not token:
            return None, ""
        for unit in ("px", "%", "deg"):
            if token.endswith(unit):
                try:
                    return float(token[: -len(unit)]), unit
                except ValueError:
                    return None, ""
        try:
            return float(token), ""
        except ValueError:
            return None, ""

    def _pseudo_length_px(self, raw, base=0.0):
        value, unit = self._pseudo_token(raw)
        if value is None or unit == "deg":
            return None
        if unit == "%":
            return value / 100.0 * base
        return value

    def _pseudo_sides(self, raw, base):
        tokens = str(raw).split()
        if not tokens:
            return (0.0, 0.0, 0.0, 0.0)
        values = []
        for token in tokens[:4]:
            value = self._pseudo_length_px(token, base)
            values.append(value if value is not None else 0.0)
        if len(values) == 1:
            return (values[0],) * 4
        if len(values) == 2:
            return (values[0], values[1], values[0], values[1])
        if len(values) == 3:
            return (values[0], values[1], values[2], values[1])
        return tuple(values)

    def _pseudo_content(self, data):
        content = str(data.get("content", "")).strip()
        if (
            len(content) >= 2
            and content[0] == content[-1]
            and content[0] in "\"'"
        ):
            content = content[1:-1]
        return content.replace("\\A", "\n")

    def _pseudo_extra_rules(self, data):
        rules = {}
        for line in str(data.get("extra", "")).splitlines():
            line = line.strip().rstrip(";")
            if ":" not in line:
                continue
            name, value = line.split(":", 1)
            rules[name.strip().lower()] = value.strip()
        return rules

    def _pseudo_base_style(self, layer):
        style = self._layer_text_style(layer)
        if style is not None:
            return style
        donor = self._group_text_donor(layer) if layer.children else None
        if donor is not None:
            return self._layer_text_style(donor)
        return None

    def _pseudo_font(self, data, style, scale):
        family = style["font_family"] if style else "none"
        if family == "none":
            family = (
                self.body_font_family
                if self.body_font_family != "none"
                else "Segoe UI"
            )
        size = self._pseudo_length_px(data.get("font_size", ""))
        if size is None:
            size = style["font_size"] if style else 14
        raw_weight = str(data.get("font_weight", "")).strip().lower()
        if raw_weight:
            try:
                bold = int(raw_weight) >= 600
            except ValueError:
                bold = raw_weight in ("bold", "bolder")
        else:
            bold = bool(style and style["font_weight"] >= 600)
        pixel = max(int(round(size * scale)), 1)
        weight = "bold" if bold else "normal"
        key = (family, -pixel, weight)
        font = self._font_cache.get(key)
        if font is None:
            font = tkfont.Font(family=family, size=-pixel, weight=weight)
            self._font_cache[key] = font
        return font

    def _pseudo_translate(self, tokens, index, base):
        if index >= len(tokens):
            return 0.0
        value, unit = self._pseudo_token(tokens[index])
        if value is None:
            return 0.0
        return value / 100.0 * base if unit == "%" else value

    def _pseudo_transform(self, raw, width, height):
        tx = ty = angle = 0.0
        scale = 1.0
        for name, args in re.findall(
            r"([A-Za-z]+)\s*\(([^)]*)\)", str(raw)
        ):
            name = name.lower()
            tokens = [part.strip() for part in args.split(",")]
            if name in ("translate", "translate3d"):
                tx += self._pseudo_translate(tokens, 0, width)
                ty += self._pseudo_translate(tokens, 1, height)
            elif name == "translatex":
                tx += self._pseudo_translate(tokens, 0, width)
            elif name == "translatey":
                ty += self._pseudo_translate(tokens, 0, height)
            elif name == "rotate":
                value, unit = self._pseudo_token(
                    tokens[0] if tokens else ""
                )
                if value is not None:
                    angle += value if unit == "deg" else math.degrees(value)
            elif name == "scale":
                value, _unit = self._pseudo_token(
                    tokens[0] if tokens else ""
                )
                if value is not None:
                    scale *= value
        return tx, ty, angle, scale

    def _canvas_color(self, value):
        value = str(value).strip()
        if not value:
            return ""
        try:
            self.winfo_rgb(value)
        except tk.TclError:
            return ""
        return value

    def _text_block_box(self, layer, box):
        style = self._layer_text_style(layer)
        if style is None or style["text_frame"] is not None:
            return box
        if self._layer_display(layer) != "block":
            return box
        if layer.text_format in ("span", "strong"):
            return box
        parent = layer.parent
        if parent is None:
            origin = 0.0
            width = float(self.content_width)
        else:
            if self._layer_display(parent) in ("flex", "grid"):
                return box
            parent_box = self._layer_css_box(parent)
            if parent_box is None:
                parent_box = self._group_css_box(parent)
            origin = float(parent_box["x"])
            width = float(parent_box["width"])
        if style["text_align"] != "left":
            return (origin, box[1], width, box[3])
        offset = box[0] - origin
        if abs(offset) < 0.001:
            return (origin, box[1], width, box[3])
        return (
            origin + offset,
            box[1],
            max(width - offset, 1.0),
            box[3],
        )

    def _draw_layer_pseudo(self, layer, key, dx=0.0, dy=0.0):
        data = self._layer_pseudo(layer, key)
        if not data["enabled"]:
            return
        if str(data.get("display", "")).strip() == "none":
            return
        box = self._export_visual_box(layer)
        if box is None and layer.children:
            css_box = self._group_css_box(layer)
            box = (
                css_box["x"],
                css_box["y"],
                css_box["width"],
                css_box["height"],
            )
        if box is None:
            return
        box = self._text_block_box(layer, box)
        bx = box[0] + dx
        by = box[1] + dy
        bw, bh = box[2], box[3]
        zoom = self.zoom
        style = self._pseudo_base_style(layer)
        rules = self._pseudo_extra_rules(data)
        font = self._pseudo_font(data, style, zoom)
        content = self._pseudo_content(data)
        lines = content.split("\n") if content else []
        letter_spacing = self._pseudo_length_px(
            rules.get("letter-spacing", ""), bw
        )
        letter_spacing = (letter_spacing or 0.0) * zoom
        line_height = style["line_height"] if style else 1.2
        raw_line_height = rules.get("line-height", "").strip()
        if raw_line_height:
            value, unit = self._pseudo_token(raw_line_height)
            if value is not None:
                if unit == "px":
                    line_height = value / max(
                        font.metrics("linespace"), 1
                    )
                elif unit == "%":
                    line_height = value / 100.0
                else:
                    line_height = value
        advance = max(
            int(round(font.metrics("linespace") * line_height)), 1
        )
        widths = []
        for line in lines:
            if letter_spacing:
                total = sum(
                    font.measure(char) + letter_spacing for char in line
                )
                widths.append(max(int(round(total - letter_spacing)), 0))
            else:
                widths.append(font.measure(line))
        content_width = max(widths, default=0) / zoom
        content_height = (
            (advance * (len(lines) - 1) + font.metrics("linespace")) / zoom
            if lines
            else 0.0
        )
        pad_top, pad_right, pad_bottom, pad_left = self._pseudo_sides(
            data.get("padding", ""), bw
        )
        mar_top, _mar_right, _mar_bottom, mar_left = self._pseudo_sides(
            data.get("margin", ""), bw
        )
        explicit_width = self._pseudo_length_px(data.get("width", ""), bw)
        explicit_height = self._pseudo_length_px(data.get("height", ""), bh)
        inner_width = (
            explicit_width if explicit_width is not None else content_width
        )
        inner_height = (
            explicit_height if explicit_height is not None else content_height
        )
        border_width = 0.0
        border_color = ""
        border_raw = rules.get("border", "").strip()
        if border_raw:
            parts = border_raw.split()
            value, _unit = self._pseudo_token(parts[0])
            if value is not None:
                border_width = value
            for part in reversed(parts[1:]):
                if part not in (
                    "solid",
                    "dashed",
                    "dotted",
                    "double",
                    "groove",
                    "ridge",
                    "inset",
                    "outset",
                ):
                    border_color = part
                    break
        radius_raw = rules.get("border-radius", "").replace(" ", "")
        oval = radius_raw in ("50%", "9999px", "100%")
        align = rules.get("text-align", "").strip().lower()
        if align not in ("left", "center", "right"):
            align = style["text_align"] if style else "left"
        box_width = inner_width + pad_left + pad_right
        box_height = inner_height + pad_top + pad_bottom
        left = self._pseudo_length_px(data.get("left", ""), bw)
        right = self._pseudo_length_px(data.get("right", ""), bw)
        top = self._pseudo_length_px(data.get("top", ""), bh)
        bottom = self._pseudo_length_px(data.get("bottom", ""), bh)
        x1 = bx
        if left is not None:
            x1 = bx + left
        elif right is not None:
            x1 = bx + bw - right - box_width
        x1 += mar_left
        y1 = by
        if top is not None:
            y1 = by + top
        elif bottom is not None:
            y1 = by + bh - bottom - box_height
        y1 += mar_top
        tx, ty, angle, scale = self._pseudo_transform(
            data.get("transform", ""), box_width, box_height
        )
        center_x = x1 + box_width / 2
        center_y = y1 + box_height / 2

        def point(px, py):
            px = center_x + (px - center_x) * scale
            py = center_y + (py - center_y) * scale
            if angle:
                radians = math.radians(angle)
                cos_value = math.cos(radians)
                sin_value = math.sin(radians)
                offset_x = px - center_x
                offset_y = py - center_y
                px = center_x + offset_x * cos_value - offset_y * sin_value
                py = center_y + offset_x * sin_value + offset_y * cos_value
            return (px + tx) * zoom, (py + ty) * zoom

        fill = self._canvas_color(data.get("background", ""))
        corners = None
        if box_width > 0 and box_height > 0 and (fill or border_color):
            corners = [
                point(x1, y1),
                point(x1 + box_width, y1),
                point(x1 + box_width, y1 + box_height),
                point(x1, y1 + box_height),
            ]
        if corners is not None and fill:
            if oval and not angle and scale == 1:
                self.doc_canvas.create_oval(
                    corners[0][0],
                    corners[0][1],
                    corners[2][0],
                    corners[2][1],
                    fill=fill,
                    outline="",
                )
            else:
                self.doc_canvas.create_polygon(
                    [value for corner in corners for value in corner],
                    fill=fill,
                    outline="",
                )
        border_color = self._canvas_color(border_color)
        if corners is not None and border_width > 0 and border_color:
            if oval and not angle and scale == 1:
                self.doc_canvas.create_oval(
                    corners[0][0],
                    corners[0][1],
                    corners[2][0],
                    corners[2][1],
                    fill="",
                    outline=border_color,
                    width=max(1, round(border_width * zoom * scale)),
                )
            else:
                self.doc_canvas.create_polygon(
                    [value for corner in corners for value in corner],
                    fill="",
                    outline=border_color,
                    width=max(1, round(border_width * zoom * scale)),
                )
        if not lines:
            return
        color = self._canvas_color(data.get("color", ""))
        if not color:
            color = style["color"] if style else TEXT
        draw_font = font if scale == 1 else self._pseudo_font(
            data, style, zoom * scale
        )
        origin_x = x1 + pad_left
        origin_y = y1 + pad_top
        line_advance = advance / zoom
        for index, line in enumerate(lines):
            line_width = widths[index] / zoom
            offset = 0.0
            if align == "center":
                offset = (inner_width - line_width) / 2
            elif align == "right":
                offset = inner_width - line_width
            base_x = origin_x + offset
            base_y = origin_y + index * line_advance
            if angle:
                screen_x, screen_y = point(base_x, base_y)
            else:
                screen_x = (
                    center_x + (base_x - center_x) * scale + tx
                ) * zoom
                screen_y = (
                    center_y + (base_y - center_y) * scale + ty
                ) * zoom
            if letter_spacing and not angle:
                cursor = screen_x
                for char in line:
                    self.doc_canvas.create_text(
                        cursor,
                        screen_y,
                        text=char,
                        fill=color,
                        font=draw_font,
                        anchor="nw",
                    )
                    cursor += draw_font.measure(char) + letter_spacing * scale
            else:
                options = {
                    "text": line,
                    "fill": color,
                    "font": draw_font,
                    "anchor": "nw",
                }
                if angle:
                    options["angle"] = -angle
                self.doc_canvas.create_text(screen_x, screen_y, **options)

    def _layer_content_bounds(self, layer):
        records = list(layer.items)

        def collect(item_layer):
            for child in item_layer.children:
                if not child.visible:
                    continue
                records.extend(child.items)
                collect(child)

        collect(layer)
        return self._record_bounds(records)

    def _layer_background_bounds(self, layer):
        records = list(layer.items)

        def collect(item_layer):
            for child in item_layer.children:
                if not child.visible:
                    continue
                records.extend(child.items)
                collect(child)

        collect(layer)
        bounds = self._record_bounds(records)
        if bounds is None:
            return (0, 0, self.content_width, self.content_height)
        x1, y1, x2, y2 = bounds
        if x2 - x1 < 1 or y2 - y1 < 1:
            return (0, 0, self.content_width, self.content_height)
        return bounds

    def _reset_document_state(self):
        self.layers = []
        self.layer_counter = 0
        self.active_layer = None
        self.selected_layers = []
        self._selection_anchor = None
        self.history = []
        self._stroke = None
        self._last_point = None
        self._temp_ids = []
        self._rect_start = None
        self._rect_preview = None
        self.marquee_region = None
        self._marquee_start = None
        self._moving_guide = None
        self._guide_move_start = 0
        self._drag_layer = None
        self.guides = []
        self.guides_visible = True
        self.zoom = 1.0
        self.content_full = False
        self.content_background = "white"
        self.body_font_family = "none"
        self.body_font_family_var.set("none")
        self.doc_path = None

    def _new_document(self, _event=None):
        self._commit_text_editor()
        if not self._confirm_save_changes():
            return
        self._hide_help_tab()
        self._new_doc_counter += 1
        self._reset_document_state()
        self.doc_name = f"Chưa có tên-{self._new_doc_counter}"
        self._set_content_size(*CONTENT_SIZE)
        self._add_layer(record=False)
        self.saved_signature = self._document_signature()
        self._render_document()
        self._layout_content_viewport()
        self._refresh_doc_tab()

    def _open_document(self, _event=None):
        self._commit_text_editor()
        if not self._confirm_save_changes():
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Mở tài liệu",
            filetypes=[
                (
                    "Tài liệu & hình ảnh",
                    f"*.dbw {IMAGE_FILE_PATTERN}",
                ),
                ("DBW Document", "*.dbw"),
                ("Hình ảnh PNG", "*.png"),
                ("Hình ảnh WebP", "*.webp"),
                ("Hình ảnh khác", "*.jpg *.jpeg *.gif *.bmp *.psd"),
                ("Tất cả tệp", "*.*"),
            ],
        )
        if not path:
            return

        extension = os.path.splitext(path)[1].lower()
        if extension in IMAGE_EXTENSIONS:
            return self._open_image_document(path)

        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict) or data.get("format") != "dbw":
                raise ValueError("Tệp không đúng định dạng .dbw.")
            layers_data = data["layers"]
            if not isinstance(layers_data, list) or not layers_data:
                raise ValueError("Tệp không chứa lớp nào.")
            layers = self._restore_layers(layers_data)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            messagebox.showerror("Lỗi mở tệp", str(error), parent=self)
            return

        self.layers = layers
        active = None
        active_path = data.get("active_layer_path")
        if isinstance(active_path, list) and active_path and all(
            isinstance(index, int) for index in active_path
        ):
            try:
                active = self._layer_at(active_path)
            except (IndexError, TypeError):
                active = None
        if active is None:
            active_index = data.get("active_layer", 0)
            flat = list(self._iter_layers())
            if not isinstance(active_index, int) or not 0 <= active_index < len(flat):
                active_index = len(flat) - 1
            active = flat[active_index]
        self.active_layer = active
        counter = data.get("layer_counter")
        self.layer_counter = (
            counter if isinstance(counter, int) and counter >= self._count_layers()
            else self._count_layers()
        )
        self.history = []
        self._stroke = None
        self._rect_preview = None
        self._temp_ids = []
        self.doc_path = path
        self.doc_name = os.path.splitext(os.path.basename(path))[0]
        content_width = data.get("content_width")
        content_height = data.get("content_height")
        if not (
            isinstance(content_width, int)
            and 100 <= content_width <= 6000
            and isinstance(content_height, int)
            and 100 <= content_height <= 6000
        ):
            content_width, content_height = CONTENT_SIZE
        content_full = data.get("content_full", False)
        self.content_full = content_full if isinstance(content_full, bool) else False
        content_background = data.get("content_background", "white")
        self.content_background = (
            content_background
            if content_background in PAGE_BACKGROUNDS
            else "white"
        )
        self._set_content_size(content_width, content_height)
        loaded_guides = []
        for guide in data.get("guides", []):
            if not isinstance(guide, dict):
                continue
            orient = guide.get("orient")
            pos = guide.get("pos")
            limit = content_height if orient == "h" else content_width
            if (
                orient in ("h", "v")
                and isinstance(pos, int)
                and 0 <= pos <= limit
            ):
                loaded_guides.append({"orient": orient, "pos": pos})
        self.guides = loaded_guides
        body_font = data.get("body_font_family", "none")
        if not isinstance(body_font, str):
            body_font = "none"
        body_font = body_font.strip()[:60]
        if not body_font or body_font.lower() == "none":
            body_font = "none"
        self.body_font_family = body_font
        self.body_font_family_var.set(body_font)
        self.marquee_region = None
        self._marquee_start = None
        self.saved_signature = self._document_signature()
        self._hide_help_tab()
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()

    def _open_image_document(self, path):
        if os.path.splitext(path)[1].lower() == ".psd":
            if PSDImage is not None:
                return self._open_psd_document(path)
            messagebox.showwarning(
                "PSD",
                "Cần cài psd-tools để giữ layer PSD. "
                "Tệp sẽ được mở dưới dạng ảnh gộp.",
                parent=self,
            )
        try:
            with open(path, "rb") as handle:
                raw = handle.read()
            data, mime, width, height = self._prepare_image(raw, path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Lỗi mở tệp", str(error), parent=self)
            return

        page_width = max(100, min(width, 6000))
        page_height = max(100, min(height, 6000))
        record_width, record_height = width, height
        if width > page_width or height > page_height:
            scale = min(page_width / width, page_height / height)
            record_width = max(int(round(width * scale)), 1)
            record_height = max(int(round(height * scale)), 1)

        self._hide_help_tab()
        self._new_doc_counter += 1
        self._reset_document_state()
        self.doc_name = os.path.splitext(os.path.basename(path))[0]
        self._set_content_size(page_width, page_height)
        record = {
            "type": "image",
            "x": (page_width - record_width) // 2,
            "y": (page_height - record_height) // 2,
            "width": record_width,
            "height": record_height,
            "data": data,
            "mime": mime,
            "border_color": BRUSH_COLOR,
            "border_width": 0,
        }
        self._create_layer(self._next_layer_name("Hình ảnh"))
        self.active_layer.items.append(record)
        self._refresh_layers()
        self.saved_signature = self._document_signature()
        self._render_document()
        self._layout_content_viewport()
        self._refresh_doc_tab()

    @staticmethod
    def _psd_blend_mode(blend_mode):
        name = getattr(blend_mode, "name", "") or ""
        css = name.lower().replace("_", "-")
        return css if css in PSD_CSS_BLEND_MODES else "normal"

    @staticmethod
    def _psd_font_key(name):
        return "".join(ch for ch in str(name).lower() if ch.isalnum())

    def _psd_installed_fonts(self):
        fonts = getattr(self, "_psd_font_map", None)
        if fonts is None:
            fonts = {}
            try:
                for name in tkfont.families(self):
                    fonts.setdefault(self._psd_font_key(name), name)
            except tk.TclError:
                pass
            self._psd_font_map = fonts
        return fonts

    @staticmethod
    def _psd_font_base(postscript):
        base = str(postscript or "").split("-", 1)[0]
        for suffix in ("PSMT", "MT", "PS"):
            if len(base) > len(suffix) and base.endswith(suffix):
                return base[: -len(suffix)]
        return base

    @staticmethod
    def _psd_font_trim_style(base):
        style_words = (
            "extrabold", "ultrabold", "semibold", "demibold",
            "extralight", "ultralight", "regular", "italic", "oblique",
            "bold", "black", "heavy", "medium", "light", "thin",
        )
        trimmed = base
        changed = True
        while changed:
            changed = False
            lowered = trimmed.lower()
            for word in style_words:
                if len(trimmed) > len(word) and lowered.endswith(word):
                    trimmed = trimmed[: -len(word)]
                    changed = True
                    break
        return trimmed

    def _psd_font_family(self, style):
        font = getattr(style, "font", None)
        family = str(getattr(font, "family", "") or "").strip()
        postscript = str(
            getattr(style, "font_name", "")
            or getattr(font, "postscript_name", "")
            or ""
        ).strip()
        base = self._psd_font_base(postscript)
        installed = self._psd_installed_fonts()
        for candidate in (family, postscript, base, self._psd_font_trim_style(base)):
            actual = installed.get(self._psd_font_key(candidate))
            if actual:
                return actual
        return family or base or "none"

    def _psd_font_weight(self, style):
        if getattr(style, "faux_bold", False):
            return 700
        font = getattr(style, "font", None)
        label = " ".join(
            str(value or "")
            for value in (
                getattr(font, "style", ""),
                getattr(font, "postscript_name", ""),
                getattr(style, "font_name", ""),
            )
        ).lower()
        if any(word in label for word in ("black", "heavy")):
            return 900
        if any(word in label for word in ("extrabold", "ultrabold")):
            return 800
        if any(word in label for word in ("semibold", "demibold")):
            return 600
        if "bold" in label:
            return 700
        if "medium" in label:
            return 500
        if any(word in label for word in ("extralight", "ultralight", "thin")):
            return 200
        if "light" in label:
            return 300
        return 400

    @staticmethod
    def _psd_argb_color(values):
        try:
            parts = [float(value) for value in values]
        except (TypeError, ValueError):
            return ""
        if len(parts) >= 4:
            red, green, blue = parts[1:4]
        elif len(parts) == 3:
            red, green, blue = parts
        else:
            return ""
        factor = 255.0 if max(red, green, blue) <= 1.0 else 1.0
        channels = [
            max(0, min(255, int(round(value * factor))))
            for value in (red, green, blue)
        ]
        return "#%02x%02x%02x" % tuple(channels)

    def _psd_text_color(self, style):
        color = ""
        try:
            if getattr(style, "fill_flag", True):
                color = self._psd_argb_color(style.fill_color)
            if not color:
                color = self._psd_argb_color(style.stroke_color)
        except Exception:
            color = ""
        return color or "#0f172a"

    def _psd_text_frame(self, psd_layer, context):
        try:
            if psd_layer.text_type != 1:
                return None
        except Exception:
            return None
        try:
            shapes = psd_layer.engine_dict.get("Rendered", {}).get("Shapes")
            children = shapes.get("Children") if shapes is not None else None
            cookie = children[0].get("Cookie") if children else None
            photoshop = cookie.get("Photoshop") if cookie is not None else None
            bounds = photoshop.get("BoxBounds") if photoshop is not None else None
            x1, y1, x2, y2 = (float(value) for value in bounds)
            xx, xy, yx, yy, tx, ty = (
                float(value) for value in psd_layer.transform[:6]
            )
        except Exception:
            return None
        corners = [(x, y) for x in (x1, x2) for y in (y1, y2)]
        xs = [xx * x + yx * y + tx for x, y in corners]
        ys = [xy * x + yy * y + ty for x, y in corners]
        x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
        if x2 - x1 < 1 or y2 - y1 < 1:
            return None
        scale = context["scale"]
        offset_x = context["offset_x"]
        offset_y = context["offset_y"]
        return [
            int(round(x1 * scale + offset_x)),
            int(round(y1 * scale + offset_y)),
            int(round(x2 * scale + offset_x)),
            int(round(y2 * scale + offset_y)),
        ]

    def _psd_text_record(self, psd_layer, context):
        if getattr(psd_layer, "kind", None) != "type":
            return None
        try:
            text = str(psd_layer.text or "")
        except Exception:
            return None
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\x03", "\n").strip("\x00").rstrip()
        if not text.strip():
            return None

        try:
            typesetting = psd_layer.typesetting
            run = next(iter(typesetting.runs), None)
            style = run.style if run is not None else typesetting.default_style
            paragraph = next(iter(typesetting.paragraphs), None)
            paragraph_style = (
                paragraph.style
                if paragraph is not None
                else typesetting.default_paragraph_style
            )
        except Exception:
            return None

        try:
            engine_size = float(getattr(style, "font_size", 12.0) or 12.0)
        except (TypeError, ValueError):
            engine_size = 12.0
        scale = context["scale"]
        transform = getattr(psd_layer, "transform", None)
        transform_scale = 1.0
        try:
            xx, xy, yx, yy = (float(value) for value in transform[:4])
            determinant = abs(xx * yy - xy * yx)
            if determinant > 0:
                transform_scale = max(0.05, min(20.0, determinant ** 0.5))
        except (TypeError, ValueError):
            transform_scale = 1.0
        pixel_size = engine_size * scale * transform_scale
        font_size = max(1, min(300, int(round(pixel_size))))

        line_height = 1.2
        try:
            if getattr(style, "auto_leading", True):
                line_height = float(getattr(paragraph_style, "auto_leading", 1.2))
            else:
                leading = float(getattr(style, "leading", 0) or 0)
                if leading > 0 and engine_size > 0:
                    line_height = leading / engine_size
            line_height = round(min(3.0, max(0.5, line_height)), 2)
        except (TypeError, ValueError):
            line_height = 1.2

        try:
            tracking = int(getattr(style, "tracking", 0) or 0)
        except (TypeError, ValueError):
            tracking = 0
        letter_spacing = int(round(tracking / 1000.0 * font_size))
        letter_spacing = max(-20, min(100, letter_spacing))

        align = "left"
        justification = getattr(paragraph_style, "justification", None)
        justify_name = getattr(justification, "name", "")
        if justify_name == "RIGHT":
            align = "right"
        elif justify_name == "CENTER":
            align = "center"

        uppercase = getattr(getattr(style, "font_caps", None), "name", "") == "ALL_CAPS"

        frame = self._psd_text_frame(psd_layer, context)
        if frame is not None:
            x, y = frame[0], frame[1]
        else:
            left, top = getattr(psd_layer, "offset", (0, 0))
            x = int(round(left * scale + context["offset_x"]))
            y = int(round(top * scale + context["offset_y"]))

        record = {
            "type": "text",
            "x": x,
            "y": y,
            "text": text,
            "color": self._psd_text_color(style),
            "font_family": self._psd_font_family(style),
            "font_size": font_size,
            "font_weight": self._psd_font_weight(style),
            "line_height": line_height,
            "letter_spacing": letter_spacing,
            "text_transform": "uppercase" if uppercase else "none",
            "text_align": align,
            "text_tag": "p",
            "font_px": True,
        }
        if frame is not None:
            record["text_frame"] = frame
        return record

    def _open_psd_document(self, path):
        try:
            psd = PSDImage.open(path)
            psd_width = int(psd.width)
            psd_height = int(psd.height)
        except Exception as error:
            messagebox.showerror("Lỗi mở tệp PSD", str(error), parent=self)
            return
        if psd_width < 1 or psd_height < 1:
            messagebox.showerror(
                "Lỗi mở tệp PSD",
                "Tệp PSD không có kích thước hợp lệ.",
                parent=self,
            )
            return

        scale = min(1.0, 6000 / psd_width, 6000 / psd_height)
        page_width = max(100, min(int(round(psd_width * scale)), 6000))
        page_height = max(100, min(int(round(psd_height * scale)), 6000))
        context = {
            "scale": scale,
            "offset_x": (page_width - psd_width * scale) / 2.0,
            "offset_y": (page_height - psd_height * scale) / 2.0,
        }

        try:
            layers = [
                self._psd_layer_to_app(layer, [], 1.0, context)
                for layer in psd
            ]
            if not layers:
                flat = Layer(
                    os.path.splitext(os.path.basename(path))[0]
                    or "Hình ảnh"
                )
                record = self._psd_image_record(
                    psd.composite(),
                    context["offset_x"],
                    context["offset_y"],
                    scale,
                )
                if record is not None:
                    flat.items.append(record)
                layers = [flat]
        except Exception as error:
            messagebox.showerror("Lỗi mở tệp PSD", str(error), parent=self)
            return

        self._hide_help_tab()
        self._new_doc_counter += 1
        self._reset_document_state()
        self.doc_name = os.path.splitext(os.path.basename(path))[0]
        self.layers = layers
        for layer in self.layers:
            layer.parent = None
        self.layer_counter = self._count_layers()
        self.active_layer = self.layers[-1] if self.layers else None
        self._set_content_size(page_width, page_height)
        self._refresh_layers()
        self.saved_signature = self._document_signature()
        self._render_document()
        self._layout_content_viewport()
        self._refresh_doc_tab()

    def _psd_layer_to_app(self, psd_layer, ancestors, opacity_scale, context):
        name = str(getattr(psd_layer, "name", "") or "").strip() or "Lớp"
        layer = Layer(name)
        layer.visible = bool(getattr(psd_layer, "visible", True))
        layer.blend_mode = self._psd_blend_mode(
            getattr(psd_layer, "blend_mode", None)
        )
        opacity = getattr(psd_layer, "opacity", 255)
        try:
            opacity = max(0, min(255, int(opacity)))
        except (TypeError, ValueError):
            opacity = 255

        is_group = getattr(psd_layer, "is_group", None)
        if callable(is_group) and is_group():
            layer.expanded = bool(getattr(psd_layer, "open_folder", True))
            child_scale = opacity_scale * (opacity / 255.0)
            for child in psd_layer:
                child_layer = self._psd_layer_to_app(
                    child,
                    ancestors + [psd_layer],
                    child_scale,
                    context,
                )
                child_layer.parent = layer
                layer.children.append(child_layer)
            return layer

        text = self._psd_text_record(psd_layer, context)
        if text is not None:
            layer.items.append(text)
            return layer

        image = self._psd_layer_image(psd_layer, ancestors)
        if image is not None:
            image = image.convert("RGBA")
            if opacity_scale >= 0.999:
                rect = self._psd_shape_rect(psd_layer, image, context)
                if rect is not None:
                    layer.items.append(rect)
                    return layer
            if opacity_scale < 0.999:
                alpha = image.getchannel("A").point(
                    lambda value: int(round(value * opacity_scale))
                )
                image.putalpha(alpha)
            left, top = getattr(psd_layer, "offset", (0, 0))
            scale = context["scale"]
            record = self._psd_image_record(
                image,
                int(round(left * scale + context["offset_x"])),
                int(round(top * scale + context["offset_y"])),
                scale,
            )
            if record is not None:
                layer.items.append(record)
        return layer

    def _psd_layer_image(self, psd_layer, ancestors):
        hidden = [node for node in ancestors if not node.visible]
        if not getattr(psd_layer, "visible", True):
            hidden.append(psd_layer)
        for node in hidden:
            node.visible = True
        try:
            image = psd_layer.composite()
        except Exception:
            image = None
        finally:
            for node in hidden:
                node.visible = False
        if image is None:
            try:
                image = psd_layer.topil()
            except Exception:
                image = None
        return image

    def _psd_shape_rect(self, psd_layer, image, context):
        if image is None or image.mode != "RGBA":
            return None
        shape = None
        for origin in getattr(psd_layer, "origination", None) or []:
            if type(origin).__name__ == "Rectangle":
                shape = origin
                break
        if shape is None:
            return None
        for check in ("has_mask", "has_effects", "has_clip_layers"):
            probe = getattr(psd_layer, check, None)
            if not callable(probe):
                continue
            try:
                if probe():
                    return None
            except Exception:
                return None
        if getattr(psd_layer, "clipping", False):
            return None
        try:
            if int(getattr(psd_layer, "opacity", 255)) < 255:
                return None
            fill_opacity = getattr(psd_layer, "fill_opacity", 255)
            if isinstance(fill_opacity, (int, float)) and fill_opacity < 255:
                return None
        except (TypeError, ValueError):
            return None

        bbox = getattr(shape, "bbox", None)
        if bbox is None:
            return None
        try:
            x1, y1, x2, y2 = (float(value) for value in bbox)
        except (TypeError, ValueError):
            return None
        if x2 - x1 < 1 or y2 - y1 < 1:
            return None

        scale = context["scale"]
        offset_x = context["offset_x"]
        offset_y = context["offset_y"]
        left, top = getattr(psd_layer, "offset", (0, 0))
        local = (x1 - left, y1 - top, x2 - left, y2 - top)

        stroke = getattr(psd_layer, "stroke", None)
        stroke_on = bool(stroke is not None and getattr(stroke, "enabled", False))
        border_width = 0
        border_color = ""
        if stroke_on:
            try:
                line_width = float(getattr(stroke, "line_width", 0) or 0)
            except (TypeError, ValueError):
                line_width = 0
            if line_width > 0:
                border_color = self._psd_stroke_color(stroke)
                if not border_color:
                    return None
                border_width = max(int(round(line_width * scale)), 1)

        background = ""
        fill_on = stroke is None or bool(getattr(stroke, "fill_enabled", True))
        if fill_on:
            inset = border_width + 2
            background = self._psd_sample_color(
                image,
                (
                    local[0] + inset,
                    local[1] + inset,
                    local[2] - inset,
                    local[3] - inset,
                ),
            )
            if not background:
                return None
        if not background and not (border_color and border_width > 0):
            return None
        if border_width <= 0:
            border_color = background

        return {
            "type": "rect",
            "x1": int(round(x1 * scale + offset_x)),
            "y1": int(round(y1 * scale + offset_y)),
            "x2": int(round(x2 * scale + offset_x)),
            "y2": int(round(y2 * scale + offset_y)),
            "color": border_color or background or BRUSH_COLOR,
            "border_color": border_color or background or BRUSH_COLOR,
            "border_width": border_width,
            "background": background,
        }

    def _psd_stroke_color(self, stroke):
        content = getattr(stroke, "content", None)
        if content is None:
            return ""
        color = content.get(b"Clr ")
        if color is None or not hasattr(color, "get"):
            return ""
        try:
            values = [
                max(0, min(255, int(round(float(color.get(key))))))
                for key in (b"Rd  ", b"Grn ", b"Bl  ")
            ]
        except (KeyError, TypeError, ValueError):
            return ""
        return "#%02x%02x%02x" % tuple(values)

    def _psd_sample_color(self, image, box):
        left, top, right, bottom = (int(round(value)) for value in box)
        width, height = image.size
        left = max(left, 0)
        top = max(top, 0)
        right = min(right, width - 1)
        bottom = min(bottom, height - 1)
        if right < left or bottom < top:
            return ""
        step_x = max((right - left + 1) // 32, 1)
        step_y = max((bottom - top + 1) // 32, 1)
        pixels = []
        for y in range(top, bottom + 1, step_y):
            for x in range(left, right + 1, step_x):
                red, green, blue, alpha = image.getpixel((x, y))
                if alpha >= 200:
                    pixels.append((red, green, blue))
        if not pixels:
            return ""
        color, count = Counter(pixels).most_common(1)[0]
        if count < len(pixels) * 0.9:
            return ""
        return "#%02x%02x%02x" % color

    def _psd_image_record(self, image, x, y, scale):
        if image is None or image.width < 1 or image.height < 1:
            return None
        width = max(int(round(image.width * scale)), 1)
        height = max(int(round(image.height * scale)), 1)
        image = image.convert("RGBA")
        if image.size != (width, height):
            resample = getattr(Image, "Resampling", Image).LANCZOS
            image = image.resize((width, height), resample)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        data = base64.b64encode(buffer.getvalue()).decode("ascii")
        return {
            "type": "image",
            "x": int(round(x)),
            "y": int(round(y)),
            "width": width,
            "height": height,
            "data": data,
            "mime": "image/png",
            "border_color": BRUSH_COLOR,
            "border_width": 0,
        }

    def _save_document(self, _event=None):
        self._commit_text_editor()
        path = self.doc_path
        if not path:
            path = filedialog.asksaveasfilename(
                parent=self,
                title="Lưu tài liệu",
                defaultextension=".dbw",
                initialfile=f"{self.doc_name}.dbw",
                filetypes=[("DBW Document", "*.dbw"), ("Tất cả tệp", "*.*")],
            )
            if not path:
                return False
        return self._write_document_file(path)

    def _save_document_as(self, _event=None):
        self._commit_text_editor()
        initial = (
            os.path.basename(self.doc_path)
            if self.doc_path
            else f"{self.doc_name}.dbw"
        )
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Lưu tài liệu khác",
            defaultextension=".dbw",
            initialfile=initial,
            filetypes=[
                ("DBW Document", "*.dbw"),
                ("Hình ảnh PNG", "*.png"),
                ("Hình ảnh WebP", "*.webp"),
                ("Hình ảnh JPG", "*.jpg *.jpeg"),
                ("Tất cả tệp", "*.*"),
            ],
        )
        if not path:
            return False
        extension = os.path.splitext(path)[1].lower()
        if extension in (".png", ".jpg", ".jpeg", ".webp"):
            return self._save_page_image(path)
        return self._write_document_file(path)

    def _save_page_image(self, path):
        extension = os.path.splitext(path)[1].lower()
        image_format = {
            ".png": "PNG",
            ".webp": "WEBP",
        }.get(extension, "JPEG")
        if Image is None or ImageGrab is None:
            messagebox.showerror(
                "Lỗi lưu ảnh",
                "Cần cài Pillow để lưu trang thiết kế thành ảnh JPG/WebP/PNG.",
                parent=self,
            )
            return False
        self._commit_text_editor()
        self._hide_help_tab()
        self.update_idletasks()
        if not self.winfo_viewable():
            messagebox.showerror(
                "Lỗi lưu ảnh",
                "Cần mở cửa sổ ứng dụng để chụp trang thiết kế.",
                parent=self,
            )
            return False
        try:
            if image_format == "PNG" and self._page_background() == "none":
                image = self._transparent_page_image()
                image.save(path, format="PNG")
            else:
                image = self._render_page_image()
                if image_format == "PNG":
                    image.convert("RGB").save(path, format="PNG")
                else:
                    image.convert("RGB").save(
                        path, format=image_format, quality=95
                    )
        except Exception as error:
            messagebox.showerror("Lỗi lưu ảnh", str(error), parent=self)
            return False
        self._flash_status(
            f"Đã lưu ảnh {os.path.basename(path)}"
        )
        return True

    @staticmethod
    def _snapshot_offsets(total, view):
        if total <= view:
            return [0]
        offsets = [0]
        while offsets[-1] + view < total:
            offsets.append(offsets[-1] + view)
        if offsets[-1] + view > total:
            offsets[-1] = total - view
        return offsets

    def _render_page_image(self, background=DOC_BG):
        """Render the whole page at 1:1 by capturing tiles of a scratch window."""
        page_w = max(int(round(self.content_width)), 1)
        page_h = max(int(round(self.content_height)), 1)
        screen_w = max(int(self.winfo_screenwidth()), 1)
        screen_h = max(int(self.winfo_screenheight()), 1)
        view_w = min(page_w, 1200, max(screen_w - 120, 240))
        view_h = min(page_h, 900, max(screen_h - 180, 180))
        snapshot = tk.Toplevel(self)
        snapshot.overrideredirect(True)
        snapshot.geometry(f"{view_w}x{view_h}+20+20")
        try:
            snapshot.attributes("-topmost", True)
        except tk.TclError:
            pass
        canvas = tk.Canvas(
            snapshot,
            width=view_w,
            height=view_h,
            bg=background,
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)
        canvas.configure(scrollregion=(0, 0, page_w, page_h))
        previous_canvas = self.doc_canvas
        previous_zoom = self.zoom
        self.doc_canvas = canvas
        self.zoom = 1.0
        try:
            self._draw_layers(self.layers)
            snapshot.update_idletasks()
            snapshot.update()
            image = Image.new("RGB", (page_w, page_h), background)
            hwnd = snapshot.winfo_id()
            for offset_y in self._snapshot_offsets(page_h, view_h):
                for offset_x in self._snapshot_offsets(page_w, view_w):
                    canvas.xview_moveto(offset_x / page_w)
                    canvas.yview_moveto(offset_y / page_h)
                    snapshot.update_idletasks()
                    snapshot.update()
                    origin_x = max(int(round(canvas.canvasx(0))), 0)
                    origin_y = max(int(round(canvas.canvasy(0))), 0)
                    width = min(view_w, page_w - origin_x)
                    height = min(view_h, page_h - origin_y)
                    if width <= 0 or height <= 0:
                        continue
                    shot = ImageGrab.grab(window=hwnd)
                    image.paste(
                        shot.crop((0, 0, width, height)),
                        (origin_x, origin_y),
                    )
            return image
        finally:
            self.doc_canvas = previous_canvas
            self.zoom = previous_zoom
            snapshot.destroy()
            self._render_document()
            self._layout_content_viewport()

    def _transparent_page_image(self):
        over_white = self._render_page_image(DOC_BG).convert("RGB")
        over_black = self._render_page_image("#000000").convert("RGB")
        alpha = ImageChops.invert(
            ImageChops.subtract(over_white, over_black)
        ).convert("L")
        safe_alpha = ImageChops.add(
            alpha, alpha.point(lambda value: 255 if value == 0 else 0)
        )
        evaluate = getattr(ImageMath, "unsafe_eval", None) or ImageMath.eval
        bands = [
            evaluate("convert(b * 255 / a, 'L')", b=band, a=safe_alpha)
            for band in over_black.split()
        ]
        return Image.merge("RGBA", (*bands, alpha))

    def _export_layer(self, layer, kind):
        self._commit_text_editor()
        if not layer.visible:
            messagebox.showinfo(
                "Xuất layer",
                "Lớp đang bị ẩn. Hãy bật hiển thị lớp trước khi xuất.",
                parent=self,
            )
            return
        if kind != "svg" and (Image is None or ImageGrab is None):
            messagebox.showerror(
                "Lỗi xuất layer",
                "Cần cài Pillow để xuất layer thành ảnh JPG/PNG/WebP.",
                parent=self,
            )
            return
        bounds = self._layer_export_bounds(layer)
        if bounds is None:
            messagebox.showinfo(
                "Xuất layer", "Lớp này không có nội dung để xuất.", parent=self
            )
            return
        labels = {"png": "PNG", "jpg": "JPG", "webp": "WebP", "svg": "SVG"}
        label = labels[kind]
        path = filedialog.asksaveasfilename(
            parent=self,
            title=f"Xuất layer '{layer.name}'",
            defaultextension=f".{kind}",
            initialfile=f"{self._layer_file_stem(layer)}.{kind}",
            filetypes=[
                (f"{label} (*.{kind})", f"*.{kind}"),
                ("Tất cả tệp", "*.*"),
            ],
        )
        if not path:
            return
        if not self.winfo_viewable():
            messagebox.showerror(
                "Lỗi xuất layer",
                "Cần mở cửa sổ ứng dụng để xuất layer.",
                parent=self,
            )
            return
        self._hide_help_tab()
        self.update_idletasks()
        try:
            if kind == "svg":
                self._save_layer_svg(layer, path, bounds)
            else:
                self._save_layer_image(layer, path, kind, bounds)
        except Exception as error:
            messagebox.showerror("Lỗi xuất layer", str(error), parent=self)
            return
        self._flash_status(f"Đã xuất layer {os.path.basename(path)}")

    @staticmethod
    def _layer_file_stem(layer):
        raw = str(layer.name or "")
        cleaned = "".join(
            char for char in raw
            if char not in '<>:"/\\|?*' and ord(char) >= 32
        ).strip().strip(".")
        return cleaned or "layer"

    def _save_layer_image(self, layer, path, kind, bounds):
        if kind == "jpg":
            image = self._render_layer_image(layer, bounds).convert("RGB")
            image.save(path, format="JPEG", quality=95)
            return
        image = self._transparent_layer_image(layer, bounds)
        if kind == "png":
            image.save(path, format="PNG")
        else:
            image.save(path, format="WEBP", quality=95)

    def _layer_export_bounds(self, layer):
        bounds = self._layer_visual_bounds(layer)
        if bounds is None:
            return None
        x1, y1, x2, y2 = bounds
        pad = 2
        left = math.floor(x1) - pad
        top = math.floor(y1) - pad
        right = max(math.ceil(x2) + pad, left + 1)
        bottom = max(math.ceil(y2) + pad, top + 1)
        return (float(left), float(top), float(right), float(bottom))

    def _layer_visual_bounds(self, layer):
        xs = []
        ys = []

        def add_record(record, dx, dy, stretch_width, layer=None):
            kind = record.get("type")
            if kind in ("rect", "ellipse"):
                x2 = (
                    record["x1"] + stretch_width
                    if stretch_width is not None
                    else record["x2"]
                )
                edge = max(1, record.get("border_width", 2)) / 2
                xs.extend(
                    (record["x1"] - edge + dx, x2 + edge + dx)
                )
                ys.extend(
                    (record["y1"] - edge + dy, record["y2"] + edge + dy)
                )
            elif kind == "line":
                edge = max(1, record.get("width", 1)) / 2
                coords = record.get("coords") or []
                for index in range(0, len(coords) - 1, 2):
                    xs.extend(
                        (
                            coords[index] - edge + dx,
                            coords[index] + edge + dx,
                        )
                    )
                    ys.extend(
                        (
                            coords[index + 1] - edge + dy,
                            coords[index + 1] + edge + dy,
                        )
                    )
            elif kind == "dot":
                radius = record.get("r", 0)
                xs.extend(
                    (record["x"] - radius + dx, record["x"] + radius + dx)
                )
                ys.extend(
                    (record["y"] - radius + dy, record["y"] + radius + dy)
                )
            elif kind == "text":
                _font, _lines, widths, _advance, _spacing, height = (
                    self._text_metrics(record)
                )
                block_width = max(widths, default=0)
                start = self._text_block_start(
                    record, block_width, layer
                )
                xs.extend((start + dx, start + block_width + dx))
                ys.extend((record["y"] + dy, record["y"] + height + dy))
            elif kind == "image":
                width = (
                    stretch_width
                    if stretch_width is not None
                    else record.get("width", 0)
                )
                edge = record.get("border_width", 0) / 2
                xs.extend(
                    (
                        record["x"] - edge + dx,
                        record["x"] + dx + width + edge,
                    )
                )
                ys.extend(
                    (
                        record["y"] - edge + dy,
                        record["y"] + dy
                        + record.get("height", 0) + edge,
                    )
                )

        def collect(
            layers, dx=0.0, dy=0.0, stretch_width=None,
            children_dx=None, children_dy=None,
        ):
            base_dx = dx if children_dx is None else children_dx
            base_dy = dy if children_dy is None else children_dy
            for item_layer in layers:
                if not item_layer.visible:
                    continue
                image = item_layer.background_image
                if image and image.get("data"):
                    bx1, by1, bx2, by2 = self._layer_background_bounds(
                        item_layer
                    )
                    if stretch_width is not None:
                        bx2 = bx1 + stretch_width
                    xs.extend((bx1 + dx, bx2 + dx))
                    ys.extend((by1 + dy, by2 + dy))
                for record in item_layer.items:
                    add_record(record, dx, dy, stretch_width, item_layer)
                offsets = {}
                display = self._layer_display(item_layer)
                if item_layer.children and display == "flex":
                    offsets = self._flex_child_offsets(item_layer)
                elif item_layer.children and display == "grid":
                    offsets = self._grid_child_offsets(item_layer)
                for child in item_layer.children:
                    if not child.visible:
                        continue
                    child_dx, child_dy, child_stretch = offsets.get(
                        id(child), (0.0, 0.0, None)
                    )
                    keep_design = (
                        display == "flex"
                        and child.children
                        and self._is_flex_fill_layer(child)
                    )
                    collect(
                        [child],
                        base_dx + child_dx,
                        base_dy + child_dy,
                        child_stretch,
                        children_dx=base_dx if keep_design else None,
                        children_dy=base_dy if keep_design else None,
                    )

        collect([layer])
        if not xs or not ys:
            return None
        return min(xs), min(ys), max(xs), max(ys)

    def _render_layer_image(self, layer, bounds, background=DOC_BG):
        x1, y1, x2, y2 = bounds
        page_w = max(int(round(x2 - x1)), 1)
        page_h = max(int(round(y2 - y1)), 1)
        screen_w = max(int(self.winfo_screenwidth()), 1)
        screen_h = max(int(self.winfo_screenheight()), 1)
        view_w = min(page_w, 1200, max(screen_w - 120, 240))
        view_h = min(page_h, 900, max(screen_h - 180, 180))
        snapshot = tk.Toplevel(self)
        snapshot.overrideredirect(True)
        snapshot.geometry(f"{view_w}x{view_h}+20+20")
        try:
            snapshot.attributes("-topmost", True)
        except tk.TclError:
            pass
        canvas = tk.Canvas(
            snapshot,
            width=view_w,
            height=view_h,
            bg=background,
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)
        canvas.configure(scrollregion=(0, 0, page_w, page_h))
        previous_canvas = self.doc_canvas
        previous_zoom = self.zoom
        self.doc_canvas = canvas
        self.zoom = 1.0
        try:
            self._draw_layers([layer], -x1, -y1)
            snapshot.update_idletasks()
            snapshot.update()
            image = Image.new("RGB", (page_w, page_h), background)
            hwnd = snapshot.winfo_id()
            for offset_y in self._snapshot_offsets(page_h, view_h):
                for offset_x in self._snapshot_offsets(page_w, view_w):
                    canvas.xview_moveto(offset_x / page_w)
                    canvas.yview_moveto(offset_y / page_h)
                    snapshot.update_idletasks()
                    snapshot.update()
                    origin_x = max(int(round(canvas.canvasx(0))), 0)
                    origin_y = max(int(round(canvas.canvasy(0))), 0)
                    width = min(view_w, page_w - origin_x)
                    height = min(view_h, page_h - origin_y)
                    if width <= 0 or height <= 0:
                        continue
                    shot = ImageGrab.grab(window=hwnd)
                    image.paste(
                        shot.crop((0, 0, width, height)),
                        (origin_x, origin_y),
                    )
            return image
        finally:
            self.doc_canvas = previous_canvas
            self.zoom = previous_zoom
            snapshot.destroy()
            self._render_document()
            self._layout_content_viewport()

    def _transparent_layer_image(self, layer, bounds):
        over_white = self._render_layer_image(
            layer, bounds, DOC_BG
        ).convert("RGB")
        over_black = self._render_layer_image(
            layer, bounds, "#000000"
        ).convert("RGB")
        alpha = ImageChops.invert(
            ImageChops.subtract(over_white, over_black)
        ).convert("L")
        safe_alpha = ImageChops.add(
            alpha, alpha.point(lambda value: 255 if value == 0 else 0)
        )
        evaluate = getattr(ImageMath, "unsafe_eval", None) or ImageMath.eval
        bands = [
            evaluate("convert(b * 255 / a, 'L')", b=band, a=safe_alpha)
            for band in over_black.split()
        ]
        return Image.merge("RGBA", (*bands, alpha))

    def _save_layer_svg(self, layer, path, bounds):
        x1, y1, x2, y2 = bounds
        width = max(int(round(x2 - x1)), 1)
        height = max(int(round(y2 - y1)), 1)
        parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="{self._css_num(x1)} {self._css_num(y1)} '
            f'{width} {height}">'
        ]
        self._svg_layers([layer], 0.0, 0.0, parts)
        parts.append("</svg>")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(parts))

    def _svg_layers(
        self, layers, dx, dy, parts, stretch_width=None,
        children_dx=None, children_dy=None,
    ):
        base_dx = dx if children_dx is None else children_dx
        base_dy = dy if children_dy is None else children_dy
        for layer in layers:
            if not layer.visible:
                continue
            self._svg_layer_background(
                layer, dx, dy, stretch_width, parts
            )
            for record in layer.items:
                markup = self._svg_record(
                    record, dx, dy, stretch_width, layer
                )
                if markup:
                    parts.append(markup)
            offsets = {}
            display = self._layer_display(layer)
            if layer.children and display == "flex":
                offsets = self._flex_child_offsets(layer)
            elif layer.children and display == "grid":
                offsets = self._grid_child_offsets(layer)
            for child in layer.children:
                if not child.visible:
                    continue
                child_dx, child_dy, child_stretch = offsets.get(
                    id(child), (0.0, 0.0, None)
                )
                keep_design = (
                    display == "flex"
                    and child.children
                    and self._is_flex_fill_layer(child)
                )
                self._svg_layers(
                    [child],
                    base_dx + child_dx,
                    base_dy + child_dy,
                    parts,
                    child_stretch,
                    children_dx=base_dx if keep_design else None,
                    children_dy=base_dy if keep_design else None,
                )

    def _svg_layer_background(
        self, layer, dx, dy, stretch_width, parts
    ):
        image = layer.background_image
        if not image or not image.get("data"):
            return
        x1, y1, x2, y2 = self._layer_background_bounds(layer)
        if stretch_width is not None:
            x2 = x1 + stretch_width
        width = max(x2 - x1, 1)
        height = max(y2 - y1, 1)
        fit = (
            "xMidYMid slice"
            if self._background_setting(image, "size") == "cover"
            else "xMidYMid meet"
        )
        href = (
            f"data:{image.get('mime') or 'image/png'};base64,"
            f"{image['data']}"
        )
        parts.append(
            f'  <image x="{self._css_num(x1 + dx)}" '
            f'y="{self._css_num(y1 + dy)}" '
            f'width="{self._css_num(width)}" '
            f'height="{self._css_num(height)}" '
            f'href="{href}" preserveAspectRatio="{fit}"/>'
        )

    def _svg_record(
        self, record, dx=0.0, dy=0.0, stretch_width=None, layer=None
    ):
        kind = record.get("type")
        if kind in ("rect", "ellipse"):
            x1 = float(record["x1"]) + dx
            y1 = float(record["y1"]) + dy
            x2 = (
                float(record["x1"]) + stretch_width
                if stretch_width is not None
                else float(record["x2"])
            ) + dx
            y2 = float(record["y2"]) + dy
            fill = html.escape(
                str(record.get("background") or "none"), quote=True
            )
            border_width, border_color = self._record_border(record, 2)
            stroke = html.escape(border_color or "none", quote=True)
            stroke_width = max(1, round(border_width))
            if kind == "rect":
                return (
                    f'  <rect x="{self._css_num(x1)}" '
                    f'y="{self._css_num(y1)}" '
                    f'width="{self._css_num(max(x2 - x1, 0))}" '
                    f'height="{self._css_num(max(y2 - y1, 0))}" '
                    f'fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="{stroke_width}"/>'
                )
            return (
                f'  <ellipse cx="{self._css_num((x1 + x2) / 2)}" '
                f'cy="{self._css_num((y1 + y2) / 2)}" '
                f'rx="{self._css_num(max((x2 - x1) / 2, 0))}" '
                f'ry="{self._css_num(max((y2 - y1) / 2, 0))}" '
                f'fill="{fill}" stroke="{stroke}" '
                f'stroke-width="{stroke_width}"/>'
            )
        if kind == "line":
            coords = list(record.get("coords") or [])
            points = []
            for index in range(0, len(coords) - 1, 2):
                points.append(
                    f"{self._css_num(coords[index] + dx)},"
                    f"{self._css_num(coords[index + 1] + dy)}"
                )
            if len(points) < 2:
                return ""
            color = html.escape(
                str(record.get("color") or BRUSH_COLOR), quote=True
            )
            width = max(1, round(record.get("width", 1)))
            return (
                f'  <polyline points="{" ".join(points)}" fill="none" '
                f'stroke="{color}" stroke-width="{width}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )
        if kind == "dot":
            radius = max(float(record.get("r", 0)), 0)
            color = html.escape(
                str(record.get("color") or BRUSH_COLOR), quote=True
            )
            return (
                f'  <circle cx="{self._css_num(record["x"] + dx)}" '
                f'cy="{self._css_num(record["y"] + dy)}" '
                f'r="{self._css_num(radius)}" fill="{color}"/>'
            )
        if kind == "text":
            return self._svg_text(record, dx, dy, layer)
        if kind == "image":
            return self._svg_image(record, dx, dy, stretch_width)
        return ""

    def _svg_text(self, record, dx=0.0, dy=0.0, layer=None):
        font, lines, widths, advance, letter_spacing, _height = (
            self._text_metrics(record)
        )
        family = self._text_family(record)
        if family == "none":
            family = (
                self.body_font_family
                if self.body_font_family != "none"
                else "Segoe UI"
            )
        color = html.escape(
            str(record.get("color") or TEXT), quote=True
        )
        size = max(int(record.get("font_size", 14)), 1)
        weight = self._text_weight_value(record)
        align = self._text_align(record)
        block_width = max(widths, default=0)
        start = self._text_block_start(record, block_width, layer)
        ascent = font.metrics("ascent")
        attributes = (
            f'font-family="{html.escape(str(family), quote=True)}" '
            f'font-size="{size}" font-weight="{weight}"'
        )
        if letter_spacing:
            attributes += (
                f' letter-spacing="{self._css_num(letter_spacing)}"'
            )
        parts = []
        for index, line in enumerate(lines):
            if not line:
                continue
            line_x = start + dx
            if align == "center":
                line_x += (block_width - widths[index]) / 2
            elif align == "right":
                line_x += block_width - widths[index]
            line_y = record["y"] + dy + index * advance + ascent
            parts.append(
                f'  <text x="{self._css_num(line_x)}" '
                f'y="{self._css_num(line_y)}" fill="{color}" '
                f'{attributes} xml:space="preserve">'
                f'{html.escape(line)}</text>'
            )
        return "\n".join(parts)

    def _svg_image(self, record, dx=0.0, dy=0.0, stretch_width=None):
        data = record.get("data")
        if not data:
            return ""
        width = (
            float(stretch_width)
            if stretch_width is not None
            else float(record.get("width", 0))
        )
        height = float(record.get("height", 0))
        if width <= 0 or height <= 0:
            return ""
        mime = record.get("mime") or "image/png"
        parts = [
            f'  <image x="{self._css_num(record["x"] + dx)}" '
            f'y="{self._css_num(record["y"] + dy)}" '
            f'width="{self._css_num(width)}" '
            f'height="{self._css_num(height)}" '
            f'href="data:{mime};base64,{data}" '
            f'preserveAspectRatio="none"/>'
        ]
        border_width, border_color = self._record_border(record)
        if border_width > 0:
            stroke = html.escape(border_color, quote=True)
            parts.append(
                f'  <rect x="{self._css_num(record["x"] + dx)}" '
                f'y="{self._css_num(record["y"] + dy)}" '
                f'width="{self._css_num(width)}" '
                f'height="{self._css_num(height)}" fill="none" '
                f'stroke="{stroke}" '
                f'stroke-width="{max(1, round(border_width))}"/>'
            )
        return "\n".join(parts)

    def _write_document_file(self, path):
        data = {
            "format": "dbw",
            "version": 2,
            "content_width": self.content_width,
            "content_height": self.content_height,
            "content_full": self.content_full,
            "content_background": self._page_background(),
            "body_font_family": self.body_font_family,
            "guides": [dict(guide) for guide in self.guides],
            "layers": [self._layer_state(layer) for layer in self.layers],
            "active_layer_path": self._layer_path(self.active_layer),
            "layer_counter": self.layer_counter,
        }
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
        except OSError as error:
            messagebox.showerror("Lỗi lưu tệp", str(error), parent=self)
            return False

        self.doc_path = path
        self.doc_name = os.path.splitext(os.path.basename(path))[0]
        self.saved_signature = self._document_signature()
        self._refresh_doc_tab()
        return True

    def _open_export_window(self):
        self._commit_text_editor()
        window = self._export_window
        if window is not None and window.winfo_exists():
            window.lift()
            window.focus_force()
            return

        window = tk.Toplevel(self)
        self._export_window = window
        window.title("Export")
        window.configure(bg=PANEL_BG)
        window.resizable(True, True)
        window.minsize(640, 420)
        window.transient(self)
        window.protocol(
            "WM_DELETE_WINDOW", lambda: self._close_export_window(window)
        )
        window.bind("<Escape>", lambda _e: self._close_export_window(window))

        body = tk.Frame(window, bg=PANEL_BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Export HTML",
            font=self.font_brand,
            fg=TEXT,
            bg=PANEL_BG,
        ).pack(anchor="w")
        tk.Label(
            body,
            text="Xem trước HTML và CSS, xuất tệp HTML kèm tệp"
            " style.css liên kết.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
        ).pack(anchor="w", pady=(4, 16))

        tk.Label(
            body,
            text="TỆP HTML",
            font=self.font_panel,
            fg=MUTED,
            bg=PANEL_BG,
        ).pack(anchor="w")

        path_row = tk.Frame(body, bg=PANEL_BG)
        path_row.pack(fill="x", pady=(6, 18))

        path_var = tk.StringVar(value=self._suggest_export_path())
        entry = tk.Entry(
            path_row,
            textvariable=path_var,
            font=self.font_layer,
            fg=TEXT,
            bg=BG,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        entry.bind(
            "<Return>",
            lambda _e: self._export_html_from_dialog(window, path_var),
        )

        tk.Button(
            path_row,
            text="Chọn…",
            command=lambda: self._choose_export_path(path_var),
            font=self.font_menu,
            fg=TEXT,
            bg=HOVER_BG,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="left", padx=(8, 0))

        html_preview, css_preview = self._build_export_content()

        preview = tk.Frame(body, bg=PANEL_BG)
        preview.pack(fill="both", expand=True, pady=(0, 16))
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_columnconfigure(1, weight=1)
        preview.grid_rowconfigure(1, weight=1)

        for column, (title, content) in enumerate(
            (("HTML", html_preview), ("CSS", css_preview))
        ):
            tk.Label(
                preview,
                text=title,
                font=self.font_panel,
                fg=MUTED,
                bg=PANEL_BG,
            ).grid(
                row=0,
                column=column,
                sticky="w",
                padx=(0, 6) if column == 0 else (6, 0),
            )
            pane = tk.Frame(preview, bg=BG)
            pane.grid(
                row=1,
                column=column,
                sticky="nsew",
                padx=(0, 6) if column == 0 else (6, 0),
                pady=(6, 0),
            )
            text = tk.Text(
                pane,
                bg=BG,
                fg=ICON,
                insertbackground=ICON,
                relief="flat",
                font=("Consolas", 9),
                wrap="none",
                highlightthickness=1,
                highlightbackground=BORDER,
                padx=10,
                pady=8,
            )
            scroll = tk.Scrollbar(pane, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            scroll.pack(side="right", fill="y")
            text.pack(side="left", fill="both", expand=True)
            text.insert("1.0", content)
            text.configure(state="disabled")

        actions = tk.Frame(body, bg=PANEL_BG)
        actions.pack(fill="x")

        tk.Button(
            actions,
            text="Hủy",
            command=lambda: self._close_export_window(window),
            font=self.font_menu,
            fg=TEXT,
            bg=BORDER,
            activebackground=HOVER_BG,
            activeforeground=TEXT,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="right")

        tk.Button(
            actions,
            text="Xuất",
            command=lambda: self._export_html_from_dialog(window, path_var),
            font=self.font_menu,
            fg=BG,
            bg=ACCENT,
            activebackground="#60a5fa",
            activeforeground=BG,
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            highlightthickness=0,
        ).pack(side="right", padx=(0, 8))

        width, height = 900, 600
        window.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - width) // 2
        y = self.winfo_rooty() + (self.winfo_height() - height) // 3
        window.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")
        window.grab_set()
        entry.focus_set()
        entry.select_range(0, "end")

    def _close_export_window(self, window):
        if window is not None and window.winfo_exists():
            window.grab_release()
            window.destroy()
        if self._export_window is window:
            self._export_window = None

    def _suggest_export_path(self):
        base = os.path.splitext(os.path.basename(self.doc_name))[0] or "export"
        folder = os.path.dirname(self.doc_path) if self.doc_path else os.getcwd()
        return os.path.join(folder, f"{base}.html")

    def _choose_export_path(self, path_var):
        current = path_var.get().strip()
        initial_dir = os.path.dirname(current)
        if not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()
        initial_file = os.path.basename(current) or f"{self.doc_name}.html"
        path = filedialog.asksaveasfilename(
            parent=self._export_window or self,
            title="Xuất HTML",
            defaultextension=".html",
            initialdir=initial_dir,
            initialfile=initial_file,
            filetypes=[("HTML", "*.html"), ("Tất cả tệp", "*.*")],
        )
        if path:
            path_var.set(path)

    def _export_html_from_dialog(self, window, path_var):
        path = path_var.get().strip()
        if not path:
            messagebox.showwarning(
                "Export", "Vui lòng chọn nơi lưu tệp HTML.", parent=window
            )
            return
        if not os.path.splitext(path)[1]:
            path += ".html"
            path_var.set(path)
        try:
            self._write_html(path)
        except OSError as error:
            messagebox.showerror("Lỗi xuất tệp", str(error), parent=window)
            return
        self._close_export_window(window)
        messagebox.showinfo(
            "Export",
            f"Đã xuất tệp HTML:\n{path}\nCSS:\n"
            f"{os.path.join(os.path.dirname(os.path.abspath(path)), 'style.css')}",
            parent=self,
        )

    def _build_export_content(self):
        html_lines = []
        self._collect_html_layers(self.layers, html_lines, 1)
        flow, body_padding = self._export_flow()
        bare_props = {}
        self._collect_css_rules(self.layers, [], flow, bare_props=bare_props)
        css_lines = []
        self._collect_css_rules(
            self.layers, css_lines, flow, bare_props=bare_props
        )
        page_lines = [
            "body {",
            "  margin: 0;",
        ]
        if self._page_background() == "white":
            page_lines.append("  background: #ffffff;")
        if body_padding:
            page_lines.append(
                f"  padding-top: {self._css_num(body_padding)}px;"
            )
            page_lines.append("  box-sizing: border-box;")
        if not self.content_full:
            page_lines.append(
                f"  width: {self._css_num(self.content_width)}px;"
            )
            page_lines.append(
                f"  height: {self._css_num(self.content_height)}px;"
            )
        if self.body_font_family != "none":
            page_lines.append(
                "  font-family: "
                f"{self._css_font_family(self.body_font_family)};"
            )
        page_lines.append("}")
        page_css = "\n".join(page_lines)
        css = "\n".join(css_lines)
        parts = [page_css]
        if self._has_visible_text(self.layers):
            parts.append(
                "p, h1, h2, h3, h4, h5, h6 {\n  margin: 0;\n}"
            )
        if css:
            parts.append(css)
        css = "\n\n".join(parts)
        return "\n".join(html_lines), css

    @staticmethod
    def _has_visible_text(layers):
        for layer in layers:
            if not layer.visible:
                continue
            if any(
                record.get("type") == "text" for record in layer.items
            ):
                return True
            if App._has_visible_text(layer.children):
                return True
        return False

    def _write_html(self, path):
        html_body, css = self._build_export_content()
        title = html.escape(self.doc_name)
        document = "\n".join(
            [
                "<!DOCTYPE html>",
                '<html lang="vi">',
                "<head>",
                '<meta charset="utf-8">',
                f"<title>{title}</title>",
                '<link rel="stylesheet" href="style.css">',
                "</head>",
                "<body>",
                html_body,
                "</body>",
                "</html>",
                "",
            ]
        )
        folder = os.path.dirname(os.path.abspath(path))
        self._export_images(folder)
        with open(
            os.path.join(folder, "style.css"), "w", encoding="utf-8"
        ) as handle:
            handle.write(css + "\n")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(document)

    def _visible_image_layers(self, layers):
        for layer in layers:
            if not layer.visible:
                continue
            if self._is_image_layer(layer):
                yield layer
            yield from self._visible_image_layers(layer.children)

    def _image_export_filename(self, layer):
        name = self._layer_class_name(layer.name)
        cleaned = "".join(
            "-" if char in '\\/:*?"<>|' else char for char in name
        ).strip(" .")
        return f"{cleaned or 'image'}.jpg"

    def _background_export_filename(self, layer):
        name = self._layer_class_name(layer.name)
        cleaned = "".join(
            "-" if char in '\\/:*?"<>|' else char for char in name
        ).strip(" .")
        return f"{cleaned or 'layer'}-bg.jpg"

    def _visible_layers(self, layers):
        for layer in layers:
            if not layer.visible:
                continue
            yield layer
            yield from self._visible_layers(layer.children)

    def _export_images(self, folder):
        entries = []
        for layer in self._visible_image_layers(self.layers):
            images = [
                record
                for record in layer.items
                if record.get("type") == "image"
            ]
            data = images[-1].get("data") if images else ""
            if data:
                entries.append((self._image_export_filename(layer), data))
        for layer in self._visible_layers(self.layers):
            background = layer.background_image
            if background and background.get("data"):
                entries.append((
                    self._background_export_filename(layer),
                    background["data"],
                ))
        if not entries:
            return
        if Image is None:
            raise OSError("Cần cài Pillow để xuất hình ảnh sang JPG.")
        for file_name, data in entries:
            self._write_jpeg(os.path.join(folder, file_name), data)

    def _write_jpeg(self, target, data):
        raw = base64.b64decode(data)
        with Image.open(BytesIO(raw)) as image:
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGBA")
                background = Image.new("RGB", image.size, "white")
                background.paste(image, mask=image.getchannel("A"))
                output = background
            else:
                output = image.convert("RGB")
            output.save(target, format="JPEG", quality=90)

    def _group_direct_text_layers(self, layer):
        result = []
        for child in layer.children:
            if not child.visible:
                continue
            if child.children or self._layer_text_style(child) is None:
                return []
            result.append(child)
        return result

    def _group_inline_mode(self, layer):
        if not layer.group_tag:
            return False
        return bool(self._group_direct_text_layers(layer))

    def _group_inline_tag(self, layer):
        if layer.group_tag == "text":
            return "p"
        if layer.group_tag in TEXT_TAGS:
            return layer.group_tag
        return "div"

    def _group_inline_content(self, layer):
        parts = []
        for child in self._group_direct_text_layers(layer):
            record = [
                item for item in child.items if item.get("type") == "text"
            ][-1]
            content = html.escape(
                str(record.get("text", ""))
            ).replace("\n", "<br>")
            if child.text_format in ("span", "strong"):
                class_name = html.escape(
                    self._layer_class_name(child.name), quote=True
                )
                tag = child.text_format
                parts.append(
                    f'<{tag} class="{class_name}">{content}</{tag}>'
                )
            else:
                parts.append(content)
        return "".join(parts)

    def _collect_html_layers(self, layers, lines, depth):
        indent = "  " * depth
        for layer in layers:
            if not layer.visible:
                continue
            class_name = html.escape(
                self._layer_class_name(layer.name), quote=True
            )
            if layer.children:
                if self._group_inline_mode(layer):
                    tag = self._group_inline_tag(layer)
                    content = self._group_inline_content(layer)
                    lines.append(
                        f'{indent}<{tag} class="{class_name}">'
                        f"{content}</{tag}>"
                    )
                else:
                    lines.append(f'{indent}<div class="{class_name}">')
                    self._collect_html_layers(layer.children, lines, depth + 1)
                    lines.append(f"{indent}</div>")
            elif self._layer_text_style(layer) is not None:
                for record in layer.items:
                    if record.get("type") != "text":
                        continue
                    content = html.escape(
                        str(record.get("text", ""))
                    ).replace("\n", "<br>")
                    text_format = layer.text_format
                    if text_format == "text":
                        lines.append(f"{indent}{content}")
                        continue
                    tag = (
                        text_format
                        if text_format in ("span", "strong")
                        else self._text_tag(record)
                    )
                    if (
                        class_name == tag
                        and not text_format
                        and not self._layer_has_pseudo(layer)
                    ):
                        lines.append(f"{indent}<{tag}>{content}</{tag}>")
                    else:
                        lines.append(
                            f'{indent}<{tag} class="{class_name}">'
                            f"{content}</{tag}>"
                        )
            elif self._is_image_layer(layer):
                image = [
                    record
                    for record in layer.items
                    if record.get("type") == "image"
                ][-1]
                if image.get("data"):
                    file_name = html.escape(
                        self._image_export_filename(layer), quote=True
                    )
                    alt = html.escape(
                        self._layer_class_name(layer.name), quote=True
                    )
                    lines.append(
                        f'{indent}<img class="{class_name}" '
                        f'src="{file_name}" alt="{alt}">'
                    )
            else:
                lines.append(f'{indent}<div class="{class_name}"></div>')

    def _layer_text_style(self, layer):
        if any(r.get("type") in ("rect", "ellipse", "image") for r in layer.items):
            return None
        texts = [r for r in layer.items if r.get("type") == "text"]
        if not texts:
            return None
        record = texts[-1]
        _font, _lines, widths, _advance, _spacing, height = (
            self._text_metrics(record)
        )
        frame = self._text_frame(record)
        if frame is not None:
            left = frame[0]
            width = frame[2] - frame[0]
        else:
            left = record["x"]
            width = max(widths, default=0)
        return {
            "x": left,
            "y": record["y"],
            "width": width,
            "height": height,
            "font_family": self._text_family(record),
            "color": record.get("color") or TEXT,
            "font_size": int(record.get("font_size", 14)),
            "font_weight": self._text_weight_value(record),
            "line_height": round(self._text_line_height(record), 2),
            "letter_spacing": self._text_letter_spacing(record),
            "text_transform": self._text_transform(record),
            "text_align": self._text_align(record),
            "text_frame": frame,
            "tag": self._text_tag(record),
        }

    def _export_visual_box(self, layer):
        images = [
            record for record in layer.items if record.get("type") == "image"
        ]
        if images:
            record = images[-1]
            return (
                record["x"],
                record["y"],
                max(float(record.get("width", 0)), 1),
                max(float(record.get("height", 0)), 1),
            )
        text_style = self._layer_text_style(layer)
        if text_style is not None:
            return (
                text_style["x"],
                text_style["y"],
                text_style["width"],
                text_style["height"],
            )
        box = self._layer_css_box(layer)
        if box is not None:
            return (box["x"], box["y"], box["width"], box["height"])
        if layer.background_image:
            box = self._background_css_box(layer)
            return (box["x"], box["y"], box["width"], box["height"])
        return None

    def _export_flow(self):
        """Compute flow margins from the design positions of sibling items."""
        flow = {}

        def walk(layers, origin_x, origin_y, parent=None):
            items = []
            child_offsets = {}
            if parent is not None and self._layer_display(parent) == "flex":
                child_offsets = self._flex_child_offsets(parent)

            def collect(seq_layers):
                for layer in seq_layers:
                    if not layer.visible:
                        continue
                    if layer.children:
                        shapes = [
                            record
                            for record in layer.items
                            if record.get("type") in ("rect", "ellipse")
                        ]
                        bounds = self._layer_content_bounds(layer)
                        if shapes:
                            shape = shapes[-1]
                            bounds = (
                                shape["x1"],
                                shape["y1"],
                                shape["x2"],
                                shape["y2"],
                            )
                        if bounds is None:
                            if not layer.background_image:
                                continue
                            bounds = (
                                0.0,
                                0.0,
                                self.content_width,
                                self.content_height,
                            )
                        x1, y1, x2, y2 = bounds
                        items.append({
                            "layer": layer,
                            "x": x1,
                            "y": y1,
                            "width": max(x2 - x1, 1),
                            "height": max(y2 - y1, 1),
                        })
                        child_x = x1
                        offset = child_offsets.get(id(layer))
                        if offset and self._is_flex_fill_layer(layer):
                            child_x = x1 + offset[0]
                        child_flow, child_padding = walk(
                            layer.children, child_x, y1, layer
                        )
                        flow[id(layer)] = {
                            "padding_top": child_padding,
                        }
                        flow.update(child_flow)
                        continue
                    box = self._export_visual_box(layer)
                    if box is None:
                        continue
                    items.append({
                        "layer": layer,
                        "x": box[0],
                        "y": box[1],
                        "width": box[2],
                        "height": box[3],
                    })

            collect(layers)
            padding = 0
            if items:
                first = items[0]["layer"]
                position = self._layer_position(first)
                padding = (
                    max(position[1], 0)
                    if position is not None
                    else max(items[0]["y"] - origin_y, 0)
                )
            for index, item in enumerate(items):
                entry = flow.setdefault(id(item["layer"]), {})
                entry["left"] = item["x"] - origin_x
                gap = 0
                if index + 1 < len(items):
                    following = items[index + 1]
                    gap = following["y"] - (item["y"] + item["height"])
                entry["gap"] = gap
            return flow, padding

        return walk(self.layers, 0.0, 0.0)

    def _group_text_donor(self, layer):
        texts = self._group_direct_text_layers(layer)
        if not texts:
            return None
        if self._group_inline_mode(layer):
            return texts[-1]
        for child in reversed(texts):
            if child.text_format == "text":
                return child
        return None

    def _group_inline_text_style(self, layer):
        if not layer.children:
            return None
        donor = self._group_text_donor(layer)
        if donor is None:
            return None
        return self._layer_text_style(donor)

    def _append_group_inline_typography(self, lines, layer):
        style = self._group_inline_text_style(layer)
        if style is None:
            return
        lines.append(f"  color: {style['color']};")
        if style["font_family"] != "none":
            lines.append(
                "  font-family: "
                f"{self._css_font_family(style['font_family'])};"
            )
        lines.append(f"  font-size: {self._css_num(style['font_size'])}px;")
        lines.append(f"  font-weight: {style['font_weight']};")
        lines.append(
            "  line-height: " f"{self._css_num(style['line_height'])};"
        )
        lines.append(
            "  letter-spacing: "
            f"{self._css_num(style['letter_spacing'])}px;"
        )
        if style["text_transform"] != "none":
            lines.append(f"  text-transform: {style['text_transform']};")
        if style["text_align"] != "left":
            lines.append(f"  text-align: {style['text_align']};")

    def _collect_css_rules(
        self,
        layers,
        lines,
        flow,
        parent_display=None,
        parent_justify="left",
        bare_props=None,
        inline_parent=False,
    ):
        visible_index = 0
        for layer in layers:
            if not layer.visible:
                continue
            if inline_parent and layer.text_format not in ("span", "strong"):
                continue
            flex_child = parent_display == "flex"
            flex_justify = flex_child and parent_justify != "left"
            skip_bottom = flex_child and visible_index == 0
            skip_left = flex_child and (visible_index == 1 or flex_justify)
            fill_child = flex_child and self._is_flex_fill_layer(layer)
            visible_index += 1
            entry = flow.get(id(layer), {})
            left = entry.get("left", 0.0)
            gap = entry.get("gap", 0.0)
            class_name = self._layer_class_name(layer.name)
            if self._is_image_layer(layer):
                images = [
                    record
                    for record in layer.items
                    if record.get("type") == "image"
                ]
                if images:
                    self._append_image_css(
                        lines,
                        class_name,
                        images[-1],
                        left,
                        gap,
                        skip_left=skip_left,
                        skip_bottom=skip_bottom,
                        fill=fill_child,
                        blend_mode=layer.blend_mode,
                    )
                self._collect_css_rules(
                    layer.children,
                    lines,
                    flow,
                    bare_props=bare_props,
                )
                continue
            text_style = self._layer_text_style(layer)
            is_group = bool(layer.children)
            box = None if text_style is not None else self._layer_css_box(layer)
            if (
                box is None
                and text_style is None
                and is_group
                and id(layer) in flow
            ):
                box = self._group_css_box(layer)
            elif box is None and text_style is None and layer.background_image:
                box = self._background_css_box(layer)
            if text_style is not None:
                if layer.text_format == "text":
                    continue
                if lines:
                    lines.append("")
                frame = text_style["text_frame"]
                tag = text_style["tag"]
                inline = layer.text_format in ("span", "strong")
                has_pseudo = self._layer_has_pseudo(layer)
                bare = class_name == tag and not inline and not has_pseudo
                selector = tag if bare else f".{class_name}"
                lines.append(f"{selector} {{")
                bottom = (
                    gap
                    if (
                        not inline
                        and not skip_bottom
                        and self._css_nonzero(gap)
                    )
                    else None
                )
                horizontal = (
                    left
                    if (
                        not inline
                        and text_style["text_align"] == "left"
                        and not skip_left
                        and self._css_nonzero(left)
                    )
                    else None
                )
                if bare:
                    if bottom is not None:
                        lines.append(
                            f"  margin-bottom: {self._css_num(bottom)}px;"
                        )
                        if bare_props is not None:
                            bare_props.setdefault(tag, set()).add(
                                "margin-bottom"
                            )
                    if horizontal is not None:
                        lines.append(
                            "  margin-left: "
                            f"{self._css_num(horizontal)}px;"
                        )
                        if bare_props is not None:
                            bare_props.setdefault(tag, set()).add(
                                "margin-left"
                            )
                else:
                    resets = (
                        bare_props.get(tag, ())
                        if bare_props is not None
                        else ()
                    )
                    if inline:
                        resets = ()
                    self._append_text_margin(
                        lines,
                        "margin-bottom",
                        bottom,
                        "margin-bottom" in resets,
                    )
                    self._append_text_margin(
                        lines,
                        "margin-left",
                        horizontal,
                        "margin-left" in resets,
                    )
                display = self._layer_display(layer)
                if frame is not None and not inline:
                    lines.append(
                        "  width: "
                        f"{self._css_num(frame[2] - frame[0])}px;"
                    )
                elif (
                    display == "block"
                    and not inline
                    and (
                        layer.parent is None
                        or self._layer_display(layer.parent)
                        not in ("flex", "grid")
                    )
                ):
                    if horizontal is None:
                        lines.append("  width: 100%;")
                    elif horizontal > 0:
                        lines.append(
                            "  width: calc(100% - "
                            f"{self._css_num(horizontal)}px);"
                        )
                    else:
                        lines.append(
                            "  width: calc(100% + "
                            f"{self._css_num(-horizontal)}px);"
                        )
                lines.append(f"  color: {text_style['color']};")
                if text_style["font_family"] != "none":
                    lines.append(
                        "  font-family: "
                        f"{self._css_font_family(text_style['font_family'])};"
                    )
                lines.append(
                    f"  font-size: {self._css_num(text_style['font_size'])}px;"
                )
                weight = text_style["font_weight"]
                if layer.text_format == "strong":
                    weight = max(weight, 700)
                lines.append(f"  font-weight: {weight};")
                lines.append(
                    "  line-height: "
                    f"{self._css_num(text_style['line_height'])};"
                )
                lines.append(
                    "  letter-spacing: "
                    f"{self._css_num(text_style['letter_spacing'])}px;"
                )
                if text_style["text_transform"] != "none":
                    lines.append(
                        "  text-transform: "
                        f"{text_style['text_transform']};"
                    )
                if text_style["text_align"] != "left" or frame is not None:
                    lines.append(
                        "  text-align: "
                        f"{text_style['text_align']};"
                    )
                if display != "block" and not inline:
                    lines.append(f"  display: {display};")
                if has_pseudo:
                    lines.append("  position: relative;")
                if layer.blend_mode != "normal":
                    lines.append(
                        f"  mix-blend-mode: {layer.blend_mode};"
                    )
                lines.append("}")
            elif box is not None:
                if lines:
                    lines.append("")
                lines.append(f".{class_name} {{")
                if layer.children and self._layer_align(layer) != "left":
                    if not skip_bottom and self._css_nonzero(gap):
                        lines.append(
                            f"  margin-bottom: {self._css_num(gap)}px;"
                        )
                else:
                    self._append_flow_margins(
                        lines, left, gap,
                        skip_left=skip_left,
                        skip_bottom=skip_bottom,
                    )
                if fill_child:
                    lines.append("  flex: 1;")
                padding_top = entry.get("padding_top", 0)
                if padding_top:
                    lines.append(
                        f"  padding-top: {self._css_num(padding_top)}px;"
                    )
                if not fill_child:
                    lines.append(
                        f"  width: {self._css_num(box['width'])}px;"
                    )
                lines.append(
                    f"  height: {self._css_num(box['height'])}px;"
                )
                if box["background"]:
                    lines.append(f"  background: {box['background']};")
                if box["border_width"] > 0 and box["border_color"]:
                    lines.append(
                        f"  border: {self._css_num(box['border_width'])}px "
                        f"solid {box['border_color']};"
                    )
                if box.get("border_radius"):
                    lines.append(
                        f"  border-radius: {box['border_radius']};"
                    )
                if layer.background_image:
                    image = layer.background_image
                    lines.append(
                        '  background-image: url("'
                        f'{self._background_export_filename(layer)}");'
                    )
                    lines.append(
                        "  background-size: "
                        f"{self._background_setting(image, 'size')};"
                    )
                    lines.append(
                        "  background-position: "
                        f"{self._background_setting(image, 'position')};"
                    )
                    lines.append(
                        "  background-repeat: "
                        f"{self._background_setting(image, 'repeat')};"
                    )
                if layer.children:
                    lines.append(
                        f"  display: {self._layer_display(layer)};"
                    )
                    self._append_group_gap(lines, layer)
                    self._append_group_justify(lines, layer)
                    self._append_group_align(lines, layer)
                self._append_group_inline_typography(lines, layer)
                if layer.blend_mode != "normal":
                    lines.append(
                        f"  mix-blend-mode: {layer.blend_mode};"
                    )
                lines.append("}")
            elif layer.children:
                display = self._layer_display(layer)
                align = self._layer_align(layer)
                justify = self._layer_justify(layer)
                gap = self._layer_gap(layer)
                inline_style = self._group_inline_text_style(layer)
                if (
                    display != "block"
                    or align != "left"
                    or (display == "flex" and justify != "left")
                    or (display in ("flex", "grid") and gap > 0)
                    or inline_style is not None
                ):
                    if lines:
                        lines.append("")
                    lines.append(f".{class_name} {{")
                    if display != "block":
                        lines.append(f"  display: {display};")
                    self._append_group_gap(lines, layer)
                    self._append_group_justify(lines, layer)
                    self._append_group_align(lines, layer)
                    self._append_group_inline_typography(lines, layer)
                    lines.append("}")
            self._append_pseudo_css(lines, layer, class_name)
            self._collect_css_rules(
                layer.children,
                lines,
                flow,
                self._layer_display(layer) if layer.children else None,
                self._layer_justify(layer) if layer.children else "left",
                bare_props,
                self._group_inline_mode(layer) if layer.children else False,
            )

    def _append_text_margin(self, lines, prop, value, reset):
        if value is not None:
            lines.append(f"  {prop}: {self._css_num(value)}px;")
        elif reset:
            lines.append(f"  {prop}: 0;")

    def _append_pseudo_css(self, lines, layer, class_name):
        for pseudo in PSEUDO_KEYS:
            data = self._layer_pseudo(layer, pseudo)
            if not data["enabled"]:
                continue
            declarations = self._pseudo_declarations(data)
            if lines:
                lines.append("")
            lines.append(f".{class_name}::{pseudo} {{")
            for declaration in declarations:
                lines.append(f"  {declaration}")
            lines.append("}")

    def _pseudo_declarations(self, data):
        declarations = []
        content = str(data.get("content", "")).strip()
        if (
            len(content) >= 2
            and content[0] == content[-1]
            and content[0] in "\"'"
        ):
            content = content[1:-1]
        content = (
            content.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\r\n", "\\A ")
            .replace("\n", "\\A ")
            .replace("\r", "\\A ")
        )
        declarations.append(f'content: "{content}";')
        position = str(data.get("position", "absolute")).strip()
        if position not in PSEUDO_POSITIONS:
            position = "absolute"
        declarations.append(f"position: {position};")
        for prop in ("top", "left", "bottom", "right"):
            value = self._pseudo_length(data.get(prop, ""))
            if value:
                declarations.append(f"{prop}: {value};")
        transform = str(data.get("transform", "")).strip().rstrip(";")
        if transform:
            declarations.append(f"transform: {transform};")
        display = str(data.get("display", "")).strip()
        if display in PSEUDO_DISPLAYS and display:
            declarations.append(f"display: {display};")
        for prop, key in (
            ("width", "width"),
            ("height", "height"),
            ("margin", "margin"),
            ("padding", "padding"),
            ("font-size", "font_size"),
        ):
            value = self._pseudo_length(data.get(key, ""))
            if value:
                declarations.append(f"{prop}: {value};")
        color = str(data.get("color", "")).strip()
        if color:
            declarations.append(f"color: {color};")
        background = str(data.get("background", "")).strip()
        if background:
            declarations.append(f"background: {background};")
        weight = str(data.get("font_weight", "")).strip()
        if weight:
            declarations.append(f"font-weight: {weight};")
        for line in str(data.get("extra", "")).splitlines():
            line = line.strip().rstrip(";")
            if line and "{" not in line and "}" not in line:
                declarations.append(f"{line};")
        return declarations

    def _pseudo_length(self, raw):
        value = str(raw).strip()
        if not value:
            return ""
        parts = []
        for token in value.split():
            try:
                number = float(token)
            except ValueError:
                parts.append(token)
            else:
                parts.append(f"{self._css_num(number)}px")
        return " ".join(parts)

    def _append_group_gap(self, lines, layer):
        if self._layer_display(layer) not in ("flex", "grid"):
            return
        gap = self._layer_gap(layer)
        if self._css_nonzero(gap):
            lines.append(f"  gap: {self._css_num(gap)}px;")

    def _append_group_justify(self, lines, layer):
        if self._layer_display(layer) != "flex":
            return
        value = {
            "left": "flex-start",
            "center": "center",
            "right": "flex-end",
            "between": "space-between",
        }.get(self._layer_justify(layer), "flex-start")
        lines.append(f"  justify-content: {value};")

    def _append_group_align(self, lines, layer):
        align = self._layer_align(layer)
        if align == "center":
            lines.append("  margin-left: auto;")
            lines.append("  margin-right: auto;")
        elif align == "right":
            lines.append("  margin-left: auto;")

    def _append_flow_margins(
        self, lines, left, gap, skip_left=False, skip_bottom=False
    ):
        if not skip_bottom and self._css_nonzero(gap):
            lines.append(f"  margin-bottom: {self._css_num(gap)}px;")
        if not skip_left and self._css_nonzero(left):
            lines.append(f"  margin-left: {self._css_num(left)}px;")

    def _append_image_css(
        self, lines, class_name, record, left, gap,
        skip_left=False, skip_bottom=False, fill=False, blend_mode="normal",
    ):
        if lines:
            lines.append("")
        lines.append(f".{class_name} {{")
        self._append_flow_margins(
            lines, left, gap,
            skip_left=skip_left,
            skip_bottom=skip_bottom,
        )
        if fill:
            lines.append("  flex: 1;")
        lines.append("  display: block;")
        if not fill:
            lines.append(
                "  width: "
                f"{self._css_num(record.get('width', 0))}px;"
            )
        lines.append(
            "  height: "
            f"{self._css_num(record.get('height', 0))}px;"
        )
        border_width, border_color = self._record_border(record)
        if border_width > 0:
            lines.append(
                f"  border: {self._css_num(border_width)}px solid "
                f"{border_color};"
            )
        if blend_mode != "normal":
            lines.append(f"  mix-blend-mode: {blend_mode};")
        lines.append("}")

    def _layer_css_box(self, layer):
        shapes = [
            r for r in layer.items if r.get("type") in ("rect", "ellipse")
        ]
        if shapes:
            shape = shapes[-1]
            border_width, border_color = self._record_border(shape, 2)
            box = {
                "x": shape["x1"],
                "y": shape["y1"],
                "width": max(shape["x2"] - shape["x1"], 1),
                "height": max(shape["y2"] - shape["y1"], 1),
                "background": shape.get("background") or "",
                "border_color": border_color,
                "border_width": border_width,
            }
            if shape.get("type") == "ellipse":
                box["border_radius"] = "50%"
            return box
        bounds = self._record_bounds(layer.items)
        if bounds is None:
            return None
        x1, y1, x2, y2 = bounds
        return {
            "x": x1,
            "y": y1,
            "width": max(x2 - x1, 1),
            "height": max(y2 - y1, 1),
            "background": "",
            "border_color": "",
            "border_width": 0,
        }

    def _record_border(self, record, default_width=0):
        width = record.get("border_width", default_width)
        color = record.get("border_color")
        if color is None:
            color = record.get("color") or BRUSH_COLOR
        try:
            width = float(width)
        except (TypeError, ValueError):
            width = 0
        if width <= 0 or not color:
            return 0, ""
        return width, color

    def _background_css_box(self, layer):
        x1, y1, x2, y2 = self._layer_background_bounds(layer)
        return {
            "x": x1,
            "y": y1,
            "width": max(x2 - x1, 1),
            "height": max(y2 - y1, 1),
            "background": "",
            "border_color": "",
            "border_width": 0,
        }

    def _group_css_box(self, layer):
        bounds = self._layer_content_bounds(layer)
        if bounds is None:
            bounds = (0.0, 0.0, self.content_width, self.content_height)
        x1, y1, x2, y2 = bounds
        return {
            "x": x1,
            "y": y1,
            "width": max(x2 - x1, 1),
            "height": max(y2 - y1, 1),
            "background": "",
            "border_color": "",
            "border_width": 0,
        }

    def _record_bounds(self, records):
        xs = []
        ys = []
        for record in records:
            kind = record.get("type")
            if kind in ("rect", "ellipse"):
                xs.extend((record["x1"], record["x2"]))
                ys.extend((record["y1"], record["y2"]))
            elif kind == "line":
                coords = record.get("coords") or []
                xs.extend(coords[0::2])
                ys.extend(coords[1::2])
            elif kind == "dot":
                radius = record.get("r", 0)
                xs.extend((record["x"] - radius, record["x"] + radius))
                ys.extend((record["y"] - radius, record["y"] + radius))
            elif kind == "text":
                _font, _lines, widths, _advance, _spacing, height = (
                    self._text_metrics(record)
                )
                xs.extend((record["x"], record["x"] + max(widths, default=0)))
                ys.extend((record["y"], record["y"] + height))
            elif kind == "image":
                xs.extend(
                    (record["x"], record["x"] + record.get("width", 0))
                )
                ys.extend(
                    (record["y"], record["y"] + record.get("height", 0))
                )
        if not xs or not ys:
            return None
        return min(xs), min(ys), max(xs), max(ys)

    def _layer_class_name(self, name):
        tokens = name.strip().split()
        return "-".join(tokens) if tokens else "layer"

    def _css_num(self, value):
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")

    def _css_nonzero(self, value):
        return self._css_num(value) not in ("0", "-0")

    def _css_font_family(self, family):
        raw = str(family).strip()
        name = "".join(
            char for char in raw if char not in '";{}\\\n\r'
        ) or "Segoe UI"
        if name.lower() in (
            "serif", "sans-serif", "monospace", "cursive", "fantasy",
            "system-ui",
        ):
            return name.lower()
        return f'"{name}"'

    def _confirm_save_changes(self):
        if not self.dirty:
            return True
        name = (
            os.path.basename(self.doc_path)
            if self.doc_path
            else self.doc_name
        )
        answer = messagebox.askyesnocancel(
            "Chưa lưu thay đổi",
            f"Tài liệu '{name}' có thay đổi chưa lưu.\n"
            "Bạn có muốn lưu trước khi tiếp tục không?",
            parent=self,
        )
        if answer is None:
            return False
        if answer:
            return bool(self._save_document())
        return True

    def _on_close(self):
        self._commit_text_editor()
        if not self._confirm_save_changes():
            return
        self.destroy()

    def _bind_keys(self):
        self.bind("<F11>", lambda _e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda _e: self.exit_fullscreen())
        self.bind("<Control-z>", self._undo)
        self.bind("<Control-Z>", self._undo)
        self.bind("<Control-j>", self._duplicate_layer)
        self.bind("<Control-J>", self._duplicate_layer)
        self.bind("<Control-g>", self._group_selected_layers)
        self.bind("<Control-G>", self._group_selected_layers)
        self.bind("<Control-s>", self._save_document)
        self.bind("<Control-S>", self._save_document)
        self.bind("<Control-Shift-s>", self._save_document_as)
        self.bind("<Control-Shift-S>", self._save_document_as)
        self.bind("<Control-o>", self._open_document)
        self.bind("<Control-O>", self._open_document)
        self.bind("<Control-n>", self._new_document)
        self.bind("<Control-N>", self._new_document)
        self.bind("<Control-e>", lambda _e: self._open_export_window())
        self.bind("<Control-E>", lambda _e: self._open_export_window())
        self.bind("<Control-q>", lambda _e: self._on_close())
        self.bind("<Control-Q>", lambda _e: self._on_close())
        self.bind("<F1>", self._toggle_help_tab)
        self.bind("<Control-semicolon>", self._toggle_guides)
        self.bind("<B1-Motion>", self._on_layer_drag, add="+")
        self.bind("<ButtonRelease-1>", self._on_layer_release, add="+")
        self.bind("<Button-1>", self._commit_rename_if_outside, add="+")

    def start_maximized(self):
        self.state("zoomed")
        self.deiconify()
        self.is_fullscreen = False
        self.btn_fullscreen.configure(text="Toàn màn hình")
        self.lift()
        self.focus_force()
        self.after(100, self._update_status)

    def enter_fullscreen(self):
        self.attributes("-fullscreen", True)
        self.deiconify()
        self.is_fullscreen = True
        self.btn_fullscreen.configure(text="Cửa sổ")
        self._update_status()
        self.lift()
        self.focus_force()
        self.after(200, self._verify_fullscreen)

    def _verify_fullscreen(self):
        if not self.is_fullscreen:
            return
        self.update_idletasks()
        if (
            self.winfo_width() >= self.winfo_screenwidth()
            and self.winfo_height() >= self.winfo_screenheight()
        ):
            return
        self.attributes("-fullscreen", False)
        self.after(50, self._reapply_fullscreen)

    def _reapply_fullscreen(self):
        if not self.is_fullscreen:
            return
        self.attributes("-fullscreen", True)
        self.lift()

    def exit_fullscreen(self):
        if not self.is_fullscreen:
            return
        self.attributes("-fullscreen", False)
        self.is_fullscreen = False
        self.resizable(True, True)
        self.state("zoomed")
        self.btn_fullscreen.configure(text="Toàn màn hình")
        self._update_status()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def minimize_window(self):
        if self.is_fullscreen:
            self.exit_fullscreen()
        self.iconify()

    def set_window_size(self, width, height):
        if self.is_fullscreen:
            self.attributes("-fullscreen", False)
            self.is_fullscreen = False
            self.resizable(True, True)
            self.btn_fullscreen.configure(text="Toàn màn hình")
        self._center_window(width, height)
        self._update_status()

    def _center_window(self, width, height):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(width, screen_w)
        height = min(height, screen_h)
        x = max((screen_w - width) // 2, 0)
        y = max((screen_h - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _flash_status(self, message):
        self.status.configure(text=message)
        self.after(2500, self._update_status)

    def _update_status(self):
        mode = "Toàn màn hình" if self.is_fullscreen else "Cửa sổ"
        size = f"{self.winfo_width()}x{self.winfo_height()}"
        tool = self.tool_names.get(self.active_tool_id, "—")
        layer = self.active_layer.name if self.active_layer else "—"
        doc = f"{self.doc_name}*" if self.dirty else self.doc_name
        self.status.configure(
            text=f"Công cụ: {tool}    |    Lớp: {layer}"
                 f"    |    Tài liệu: {doc}    |    {mode} {size}"
                 f"    |    Zoom: {round(self.zoom * 100)}%"
                 f"    |    F1 · F11 · Esc · Ctrl+N/O/S/E/Q · Ctrl+Shift+S"
                 f" · Ctrl+J/G/Z · Ctrl+; · Ctrl+lăn chuột (zoom)"
        )


if __name__ == "__main__":
    App().mainloop()
