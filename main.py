import html
import json
import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import colorchooser, filedialog, messagebox, simpledialog

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
DROP_BG = "#1d4ed8"

WINDOWED_SIZE = (1100, 700)
MIN_SIZE = (760, 460)
SIDEBAR_WIDTH = 56
LAYER_PANEL_WIDTH = 230
TOOL_SIZE = 40


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
    "text": "xterm",
}


class Layer:
    def __init__(self, name):
        self.name = name
        self.visible = True
        self.items = []
        self.children = []
        self.parent = None
        self.expanded = True


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
        self.tool_names = {tool_id: name for tool_id, name, _draw in TOOLS}
        self.active_tool_id = None
        self.layers = []
        self.layer_counter = 0
        self.active_layer = None
        self._stroke = None
        self._last_point = None
        self._temp_ids = []
        self._rect_start = None
        self._rect_preview = None
        self.history = []
        self.doc_name = "Chưa có tên-1"
        self.doc_path = None
        self.saved_signature = ""
        self.dirty = False
        self._updating_info = False
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

        self._build_fonts()
        self._build_ui()
        self._bind_keys()

        self._add_layer(record=False)
        self.saved_signature = self._document_signature()
        self._refresh_doc_tab()
        self.select_tool("brush")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(50, self.enter_fullscreen)

    def _build_fonts(self):
        self.font_brand = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_menu = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_status = tkfont.Font(family="Consolas", size=10)
        self.font_panel = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.font_layer = tkfont.Font(family="Segoe UI", size=10)

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

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
        self.btn_fullscreen.pack(side="left", padx=2)

        self._make_menu_item(nav, "Thu nhỏ", self.minimize_window).pack(
            side="left", padx=2
        )
        self._make_menu_item(
            nav, "Cỡ nhỏ", lambda: self.set_window_size(800, 520)
        ).pack(side="left", padx=2)
        self._make_menu_item(
            nav, "Cỡ lớn", lambda: self.set_window_size(1300, 860)
        ).pack(side="left", padx=2)
        self._make_menu_item(nav, "Mở", self._open_document).pack(
            side="left", padx=2
        )
        self._make_menu_item(nav, "Lưu", self._save_document).pack(
            side="left", padx=2
        )
        self._make_menu_item(nav, "Export", self._open_export_window).pack(
            side="left", padx=2
        )
        self._make_menu_item(nav, "Thoát", self._on_close, danger=True).pack(
            side="left", padx=2
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

        Tooltip(item, name)
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

        wrap = tk.Frame(workspace, bg=BG)
        wrap.grid(row=1, column=0, sticky="nsew", padx=32, pady=(10, 26))

        self.doc_canvas = tk.Canvas(
            wrap,
            bg=DOC_BG,
            highlightthickness=1,
            highlightbackground="#475569",
            cursor="pencil",
        )
        self.doc_canvas.pack(fill="both", expand=True)

        self.doc_canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.doc_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.doc_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

    def _build_layer_panel(self):
        panel = tk.Frame(self, bg=PANEL_BG, width=LAYER_PANEL_WIDTH)
        panel.grid(row=1, column=2, sticky="ns")
        panel.grid_propagate(False)

        border = tk.Frame(panel, bg=BORDER, width=1)
        border.pack(side="left", fill="y")

        inner = tk.Frame(panel, bg=PANEL_BG)
        inner.pack(side="left", fill="both", expand=True)

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

        self.layer_list = tk.Frame(inner, bg=PANEL_BG)
        self.layer_list.pack(fill="both", expand=True, padx=6, pady=6)

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

    def _build_info_section(self, parent):
        header = tk.Frame(parent, bg=PANEL_BG)
        header.pack(fill="x", padx=14, pady=(14, 8))
        tk.Label(
            header,
            text="THÔNG TIN HÌNH",
            font=self.font_panel,
            fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left")
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=12)

        body = tk.Frame(parent, bg=PANEL_BG)
        body.pack(fill="x", padx=14, pady=(8, 10))
        body.grid_columnconfigure(1, weight=1)

        self._info_label(body, 0, "Kích thước")
        size_holder = tk.Frame(body, bg=PANEL_BG)
        size_holder.grid(row=0, column=1, sticky="e", pady=2)
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

        self._info_label(body, 1, "Độ dày viền")
        border_holder = tk.Frame(body, bg=PANEL_BG)
        border_holder.grid(row=1, column=1, sticky="e", pady=2)
        self.info_border_entry = self._make_info_entry(border_holder)
        self.info_border_entry.pack(side="left")
        tk.Label(
            border_holder, text="px", font=("Segoe UI", 9), fg=MUTED,
            bg=PANEL_BG,
        ).pack(side="left", padx=(4, 0))

        self._info_label(body, 2, "Màu viền")
        border_color_holder = tk.Frame(body, bg=PANEL_BG)
        border_color_holder.grid(row=2, column=1, sticky="e", pady=2)
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

        self._info_label(body, 3, "Nền")
        bg_holder = tk.Frame(body, bg=PANEL_BG)
        bg_holder.grid(row=3, column=1, sticky="e", pady=2)
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

        for entry in (self.info_width_entry, self.info_height_entry):
            entry.bind("<Return>", self._apply_rect_size)
            entry.bind("<FocusOut>", self._apply_rect_size)
        self.info_border_entry.bind("<Return>", self._apply_border_width)
        self.info_border_entry.bind("<FocusOut>", self._apply_border_width)

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=12)

    def _info_label(self, parent, row, title):
        tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=PANEL_BG,
            anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=2)

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

    def _active_rect(self):
        if self.active_layer is None:
            return None
        rects = [r for r in self.active_layer.items if r.get("type") == "rect"]
        return rects[-1] if rects else None

    def _refresh_info(self):
        rect = self._active_rect()
        self._updating_info = True
        try:
            if rect is None:
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

            width = round(abs(rect["x2"] - rect["x1"]))
            height = round(abs(rect["y2"] - rect["y1"]))
            border_width = rect.get("border_width", 2)
            border_color = (
                rect.get("border_color") or rect.get("color") or BRUSH_COLOR
            )
            background = rect.get("background") or ""

            self._set_info_entry(self.info_width_entry, width)
            self._set_info_entry(self.info_height_entry, height)
            self._set_info_entry(self.info_border_entry, border_width)
            self._set_info_entry(self.info_border_color_entry, border_color)
            self._paint_swatch(self.info_border_swatch, border_color)
            self._set_info_entry(self.info_bg_entry, background)
            self._paint_swatch(self.info_bg_swatch, background or None)
            self.info_bg_clear.configure(fg=TEXT if background else MUTED)
        finally:
            self._updating_info = False

    def _set_info_entry(self, entry, value):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(value))

    def _apply_rect_size(self, _event=None):
        if self._updating_info:
            return
        rect = self._active_rect()
        if rect is None:
            return
        try:
            width = max(1, int(self.info_width_entry.get()))
            height = max(1, int(self.info_height_entry.get()))
        except ValueError:
            self._refresh_info()
            return
        new_x2 = rect["x1"] + width
        new_y2 = rect["y1"] + height
        if new_x2 == rect["x2"] and new_y2 == rect["y2"]:
            return
        self._push_history()
        rect["x2"], rect["y2"] = new_x2, new_y2
        self._render_document()
        self._refresh_info()
        self._refresh_doc_tab()

    def _apply_border_width(self, _event=None):
        if self._updating_info:
            return
        rect = self._active_rect()
        if rect is None:
            return
        try:
            border_width = max(0, min(50, int(self.info_border_entry.get())))
        except ValueError:
            self._refresh_info()
            return
        if border_width == rect.get("border_width", 2):
            self._refresh_info()
            return
        self._push_history()
        rect["border_width"] = border_width
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
        rect = self._active_rect()
        if rect is None:
            return
        color = self._parse_hex_color(self.info_border_color_entry.get())
        if color is None:
            self._refresh_info()
            return
        self._set_border_color(rect, color)

    def _apply_background_text(self, _event=None):
        if self._updating_info:
            return
        rect = self._active_rect()
        if rect is None:
            return
        text = self.info_bg_entry.get().strip()
        if not text:
            self._set_background_color(rect, "")
            return
        color = self._parse_hex_color(text)
        if color is None:
            self._refresh_info()
            return
        self._set_background_color(rect, color)

    def _set_border_color(self, rect, color):
        current = rect.get("border_color") or rect.get("color") or BRUSH_COLOR
        if color != current:
            self._push_history()
            rect["border_color"] = color
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
        rect = self._active_rect()
        if rect is None:
            return
        current = rect.get("border_color") or rect.get("color") or BRUSH_COLOR
        _rgb, color = colorchooser.askcolor(
            color=current, title="Chọn màu viền", parent=self
        )
        if color:
            self._set_border_color(rect, color)

    def _choose_background_color(self, _event=None):
        rect = self._active_rect()
        if rect is None:
            return
        current = rect.get("background") or "#ffffff"
        _rgb, color = colorchooser.askcolor(
            color=current, title="Chọn màu nền", parent=self
        )
        if color:
            self._set_background_color(rect, color)

    def _clear_background(self, _event=None):
        rect = self._active_rect()
        if rect is None or not rect.get("background"):
            return
        self._set_background_color(rect, "")

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

    def _make_menu_item(self, parent, text, command, danger=False):
        fg = SUBTLE if danger else TEXT
        hover_bg = DANGER_BG if danger else HOVER_BG

        item = tk.Label(
            parent,
            text=text,
            font=self.font_menu,
            fg=fg,
            bg=PANEL_BG,
            padx=14,
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

    def _add_layer(self, record=True):
        if record:
            self._push_history()
        self._create_layer()
        self._refresh_layers()
        self._refresh_doc_tab()

    def _create_layer(self, name=None):
        self.layer_counter += 1
        layer = Layer(name or f"Lớp {self.layer_counter}")
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

    def _clone_layer(self, layer):
        clone = Layer(layer.name)
        clone.visible = layer.visible
        clone.expanded = layer.expanded
        clone.items = [dict(item) for item in layer.items]
        clone.children = [self._clone_layer(child) for child in layer.children]
        for child in clone.children:
            child.parent = clone
        return clone

    def _duplicate_layer(self, _event=None):
        entry = self._rename_entry
        if entry is not None and entry.winfo_exists():
            return "break"
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
        self.active_layer = layer
        self._refresh_layer_selection()
        self._refresh_info()
        self._update_status()

    def _refresh_layer_selection(self):
        for row in self.layer_list.winfo_children():
            layer = getattr(row, "_layer", None)
            if layer is None:
                continue
            bg = ACTIVE_BG if layer is self.active_layer else PANEL_BG
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
            "items": [dict(item) for item in layer.items],
            "children": [self._layer_state(child) for child in layer.children],
        }

    def _restore_layers(self, data, parent=None):
        layers = []
        for item in data:
            layer = Layer(item["name"])
            layer.visible = item["visible"]
            layer.expanded = item.get("expanded", True)
            layer.items = [dict(record) for record in item["items"]]
            layer.parent = parent
            layer.children = self._restore_layers(item.get("children", []), layer)
            layers.append(layer)
        return layers

    def _push_history(self):
        self.history.append({
            "layers": [self._layer_state(layer) for layer in self.layers],
            "active": self._layer_path(self.active_layer),
            "counter": self.layer_counter,
        })
        if len(self.history) > 50:
            self.history.pop(0)

    def _undo(self, _event=None):
        if not self.history:
            return "break"
        state = self.history.pop()
        self.layer_counter = state["counter"]
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
            "items": layer.items,
            "children": [self._layer_signature(child) for child in layer.children],
        }

    def _document_signature(self):
        return json.dumps(
            [self._layer_signature(layer) for layer in self.layers],
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
        for child in self.layer_list.winfo_children():
            child.destroy()
        self._drop_row = None
        self._drop_mode = None
        self._drop_indicator = tk.Frame(self.layer_list, bg=ACCENT, height=2)
        self._build_layer_rows(self.layers, 0)
        self.layer_count_label.configure(text=f"{self._count_layers()} lớp")
        self._refresh_info()

    def _build_layer_rows(self, layers, depth):
        for layer in reversed(layers):
            self._build_layer_row(layer, depth)
            if layer.children and layer.expanded:
                self._build_layer_rows(layer.children, depth + 1)

    def _build_layer_row(self, layer, depth=0):
        active = layer is self.active_layer
        row_bg = ACTIVE_BG if active else PANEL_BG

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

        for widget in (row, thumb, name):
            widget.bind(
                "<Button-1>", lambda event, l=layer: self._on_layer_press(event, l)
            )
        name.bind(
            "<Double-Button-1>",
            lambda _e, l=layer, w=name: self._begin_rename(l, w),
        )
        Tooltip(name, "Nhấp đúp để đổi tên lớp")

        row._layer_bg_widgets = bg_widgets
        row._layer_eye = eye
        row._layer_expander = expander if layer.children else None

    def _toggle_expanded(self, layer):
        layer.expanded = not layer.expanded
        self._refresh_layers()

    def _on_layer_press(self, event, layer):
        self._select_layer(layer)
        self._drag_layer = layer
        self._drag_origin = (event.x_root, event.y_root)
        self._drag_moved = False
        self._drag_blocked = False
        self._drag_in_panel = True

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
            if widget is self.layer_list or widget is self.layer_count_label:
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

    def _on_canvas_press(self, event):
        tool = self.active_tool_id
        if tool in ("brush", "eraser"):
            color = DOC_BG if tool == "eraser" else BRUSH_COLOR
            width = 18 if tool == "eraser" else 4
            self._stroke = {
                "coords": [event.x, event.y],
                "color": color,
                "width": width,
            }
            self._last_point = (event.x, event.y)
            radius = width / 2
            dot = self.doc_canvas.create_oval(
                event.x - radius, event.y - radius,
                event.x + radius, event.y + radius,
                fill=color, outline="", tags="temp",
            )
            self._temp_ids = [dot]
        elif tool == "rect":
            self._rect_start = (event.x, event.y)
            self._rect_preview = self.doc_canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline=BRUSH_COLOR, width=2, dash=(4, 2), tags="temp",
            )
        elif tool == "text":
            content = simpledialog.askstring("Văn bản", "Nhập nội dung:", parent=self)
            if content:
                self._push_history()
                record = {
                    "type": "text",
                    "x": event.x,
                    "y": event.y,
                    "text": content,
                    "color": "#0f172a",
                }
                self.active_layer.items.append(record)
                self._draw_record(record)
                self._refresh_doc_tab()
        elif tool == "move":
            if self.active_layer is not None and self._has_drawable_items(
                self.active_layer
            ):
                self._move_last = (event.x, event.y)
                self._move_moved = False

    def _on_canvas_drag(self, event):
        tool = self.active_tool_id
        if tool in ("brush", "eraser") and self._stroke is not None:
            last_x, last_y = self._last_point
            if (event.x, event.y) == (last_x, last_y):
                return
            segment = self.doc_canvas.create_line(
                last_x, last_y, event.x, event.y,
                fill=self._stroke["color"], width=self._stroke["width"],
                capstyle="round", tags="temp",
            )
            self._temp_ids.append(segment)
            self._stroke["coords"].extend([event.x, event.y])
            self._last_point = (event.x, event.y)
        elif tool == "rect" and self._rect_preview is not None:
            x1, y1 = self._rect_start
            self.doc_canvas.coords(self._rect_preview, x1, y1, event.x, event.y)
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

    def _on_canvas_release(self, event):
        tool = self.active_tool_id
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
        elif tool == "rect" and self._rect_preview is not None:
            x1, y1 = self._rect_start
            self.doc_canvas.delete(self._rect_preview)
            self._rect_preview = None
            x2, y2 = event.x, event.y
            if abs(x2 - x1) >= 3 and abs(y2 - y1) >= 3:
                record = {
                    "type": "rect",
                    "x1": min(x1, x2),
                    "y1": min(y1, y2),
                    "x2": max(x1, x2),
                    "y2": max(y1, y2),
                    "border_color": BRUSH_COLOR,
                    "border_width": 2,
                    "background": "",
                }
                self._push_history()
                self._create_layer(f"Hình chữ nhật {self.layer_counter + 1}")
                self.active_layer.items.append(record)
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
        elif kind in ("dot", "text"):
            record["x"] += dx
            record["y"] += dy
        elif kind == "rect":
            record["x1"] += dx
            record["y1"] += dy
            record["x2"] += dx
            record["y2"] += dy

    def _draw_record(self, record):
        kind = record["type"]
        if kind == "line":
            self.doc_canvas.create_line(
                *record["coords"], fill=record["color"], width=record["width"],
                capstyle="round", joinstyle="round",
            )
        elif kind == "dot":
            x, y, radius = record["x"], record["y"], record["r"]
            self.doc_canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=record["color"], outline="",
            )
        elif kind == "rect":
            self.doc_canvas.create_rectangle(
                record["x1"], record["y1"], record["x2"], record["y2"],
                outline=record.get("border_color")
                or record.get("color") or BRUSH_COLOR,
                width=record.get("border_width", 2),
                fill=record.get("background") or "",
            )
        elif kind == "text":
            self.doc_canvas.create_text(
                record["x"], record["y"], text=record["text"],
                fill=record["color"], font=("Segoe UI", 14), anchor="nw",
            )

    def _render_document(self):
        self.doc_canvas.delete("all")
        self._draw_layers(self.layers)

    def _draw_layers(self, layers):
        for layer in layers:
            if not layer.visible:
                continue
            for record in layer.items:
                self._draw_record(record)
            self._draw_layers(layer.children)

    def _open_document(self, _event=None):
        if not self._confirm_save_changes():
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Mở tài liệu",
            filetypes=[("DBW Document", "*.dbw"), ("Tất cả tệp", "*.*")],
        )
        if not path:
            return

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
        self.saved_signature = self._document_signature()
        self._refresh_layers()
        self._render_document()
        self._refresh_doc_tab()

    def _save_document(self, _event=None):
        if self.doc_path:
            path = self.doc_path
        else:
            path = filedialog.asksaveasfilename(
                parent=self,
                title="Lưu tài liệu",
                defaultextension=".dbw",
                initialfile=f"{self.doc_name}.dbw",
                filetypes=[("DBW Document", "*.dbw"), ("Tất cả tệp", "*.*")],
            )
            if not path:
                return False

        data = {
            "format": "dbw",
            "version": 2,
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
            text="Xem trước HTML và CSS, xuất cấu trúc lớp thành tệp HTML.",
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
        messagebox.showinfo("Export", f"Đã xuất tệp HTML:\n{path}", parent=self)

    def _build_export_content(self):
        html_lines = []
        self._collect_html_layers(self.layers, html_lines, 1)
        css_lines = []
        self._collect_css_rules(self.layers, css_lines)
        return "\n".join(html_lines), "\n".join(css_lines)

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
                "<style>",
                css,
                "</style>",
                "</head>",
                "<body>",
                html_body,
                "</body>",
                "</html>",
                "",
            ]
        )
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(document)

    def _collect_html_layers(self, layers, lines, depth):
        indent = "  " * depth
        for layer in layers:
            if not layer.visible:
                continue
            class_name = html.escape(
                self._layer_class_name(layer.name), quote=True
            )
            if layer.children:
                lines.append(f'{indent}<div class="{class_name}">')
                self._collect_html_layers(layer.children, lines, depth + 1)
                lines.append(f"{indent}</div>")
            else:
                lines.append(f'{indent}<div class="{class_name}"></div>')

    def _collect_css_rules(self, layers, lines):
        for layer in layers:
            if not layer.visible:
                continue
            box = self._layer_css_box(layer)
            if box is not None:
                if lines:
                    lines.append("")
                class_name = self._layer_class_name(layer.name)
                lines.append(f".{class_name} {{")
                lines.append(f"  width: {self._css_num(box['width'])}px;")
                lines.append(f"  height: {self._css_num(box['height'])}px;")
                if box["background"]:
                    lines.append(f"  background: {box['background']};")
                if box["border_width"] > 0 and box["border_color"]:
                    lines.append(
                        f"  border: {self._css_num(box['border_width'])}px "
                        f"solid {box['border_color']};"
                    )
                lines.append("}")
            self._collect_css_rules(layer.children, lines)

    def _layer_css_box(self, layer):
        rects = [r for r in layer.items if r.get("type") == "rect"]
        if rects:
            rect = rects[-1]
            return {
                "width": max(rect["x2"] - rect["x1"], 1),
                "height": max(rect["y2"] - rect["y1"], 1),
                "background": rect.get("background") or "",
                "border_color": (
                    rect.get("border_color")
                    or rect.get("color")
                    or BRUSH_COLOR
                ),
                "border_width": rect.get("border_width", 2),
            }
        bounds = self._record_bounds(layer.items)
        if bounds is None:
            return None
        x1, y1, x2, y2 = bounds
        return {
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
            if kind == "rect":
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
                xs.append(record["x"])
                ys.append(record["y"])
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
        self.bind("<Control-s>", self._save_document)
        self.bind("<Control-o>", self._open_document)
        self.bind("<B1-Motion>", self._on_layer_drag, add="+")
        self.bind("<ButtonRelease-1>", self._on_layer_release, add="+")
        self.bind("<Button-1>", self._commit_rename_if_outside, add="+")

    def enter_fullscreen(self):
        self.attributes("-fullscreen", True)
        self.is_fullscreen = True
        self.btn_fullscreen.configure(text="Cửa sổ")
        self._update_status()
        self.focus_force()

    def exit_fullscreen(self):
        if not self.is_fullscreen:
            return
        self.attributes("-fullscreen", False)
        self.is_fullscreen = False
        self.resizable(True, True)
        self._center_window(*WINDOWED_SIZE)
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

    def _update_status(self):
        mode = "Toàn màn hình" if self.is_fullscreen else "Cửa sổ"
        size = f"{self.winfo_width()}x{self.winfo_height()}"
        tool = self.tool_names.get(self.active_tool_id, "—")
        layer = self.active_layer.name if self.active_layer else "—"
        doc = f"{self.doc_name}*" if self.dirty else self.doc_name
        self.status.configure(
            text=f"Công cụ: {tool}    |    Lớp: {layer}"
                 f"    |    Tài liệu: {doc}    |    {mode} {size}"
                 f"    |    F11 · Esc · Ctrl+J · Ctrl+Z · Ctrl+S · Ctrl+O"
        )


if __name__ == "__main__":
    App().mainloop()
