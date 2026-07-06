#!/Users/persagy/.local/bin/python3.11
"""
FrameKit — macOS 图片尺寸转换工具
DESIGN.md 驱动的 UI，干净克制的 macOS 工具风格。
使用 sips（macOS 内置）处理图片，零外部依赖。
"""

from __future__ import annotations

import subprocess
import os
import sys
import threading
import traceback
import queue
from datetime import datetime
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Listbox, Entry, Canvas,
    filedialog, messagebox, StringVar, OptionMenu,
    MULTIPLE, END, DISABLED, NORMAL, ttk,
    LEFT, RIGHT, X, Y, BOTH, W, FLAT, SUNKEN
)
from tkinter.scrolledtext import ScrolledText

# ═══════════════════════════════════════════════════════════════
#  DESIGN.md 设计令牌 → tkinter 常量
# ═══════════════════════════════════════════════════════════════
class T:
    """将 DESIGN.md 令牌映射为 tkinter 可直接使用的值"""
    # Colors
    PRIMARY      = "#2563EB"
    PRIMARY_HOV  = "#1D4ED8"
    TEXT         = "#0F172A"
    TEXT_SEC     = "#64748B"
    TEXT_MUTED   = "#94A3B8"
    BG_PAGE      = "#F8FAFC"
    BG_CARD      = "#FFFFFF"
    BG_INPUT     = "#F1F5F9"
    BORDER       = "#E2E8F0"
    BORDER_FOCUS = "#93C5FD"
    SUCCESS      = "#16A34A"
    ERROR        = "#DC2626"
    WARN         = "#D97706"
    WHITE        = "#FFFFFF"

    # Typography (tkinter font tuples)
    FONT_TITLE   = ("Helvetica Neue", 15, "bold")
    FONT_BODY    = ("Helvetica Neue", 13)
    FONT_SMALL   = ("Helvetica Neue", 11)
    FONT_LABEL   = ("Helvetica Neue", 11, "bold")
    FONT_CODE    = ("Monaco", 11)
    FONT_CODE_SM = ("Monaco", 10)
    FONT_BTN     = ("Helvetica Neue", 13, "bold")

    # Spacing (multiples of 8px base grid)
    XS  = 4
    SM  = 8
    MD  = 12
    LG  = 16
    XL  = 24
    X2L = 32


# ═══════════════════════════════════════════════════════════════
#  预设尺寸库（按分类）
# ═══════════════════════════════════════════════════════════════
PRESET_CATEGORIES: dict[str, dict[str, str]] = {
    "🍎 Apple": {
        "iPhone 14 Pro Max":       "1290×2796",
        "iPhone 14 Plus":          "1284×2778",
        "iPhone 14 / 14 Pro":      "1179×2556",
        "iPhone 13 Pro Max":       "1284×2778",
        "iPhone 13 / 13 Pro":      "1170×2532",
        "iPhone SE / 8 / 7":       "750×1334",
        "iPhone 通用投放":          "1242×2688",
        "iPad Pro 12.9\"":          "2048×2732",
        "iPad Pro 11\"":            "1668×2388",
        "iPad 通用投放":            "2064×2752",
        "iPad mini":               "1488×2266",
        "Apple Watch 49mm":        "396×484",
        "Apple Watch 45mm":        "396×484",
        "Apple Watch 41mm":        "352×430",
        "Mac 16:10":               "2880×1800",
        "Mac 14\"":                 "3024×1964",
    },
    "🤖 Google Play": {
        "手机截图 (竖屏)":          "1080×1920",
        "手机截图 (横屏)":          "1920×1080",
        "平板 7\"":                 "800×1280",
        "平板 10\"":                "1600×2560",
        "Feature Graphic":         "1024×500",
        "TV Banner":               "1280×720",
        "Wear OS (方形)":          "384×384",
        "Wear OS (圆形)":          "320×320",
        "应用图标":                 "512×512",
    },
    "🛒 第三方商店": {
        "华为 AppGallery 手机":     "1080×1920",
        "华为 AppGallery 平板":     "2048×2732",
        "三星 Galaxy Store":        "1080×1920",
        "小米 GetApps":             "1080×1920",
        "OPPO 软件商店":            "1080×1920",
        "vivo 应用商店":            "1080×1920",
        "腾讯应用宝":               "1080×1920",
        "TapTap":                  "1080×1920",
    },
    "🌐 通用 / 社交": {
        "16:9 横屏 (1920×1080)":    "1920×1080",
        "16:9 竖屏 (1080×1920)":    "1080×1920",
        "4:3 (1024×768)":          "1024×768",
        "1:1 方形 (1080×1080)":    "1080×1080",
        "3:2 (1200×800)":          "1200×800",
        "微信公众号封面":            "900×383",
        "视频号封面":               "1080×1260",
        "小红书封面":               "1080×1440",
        "Instagram 帖子":           "1080×1350",
        "Twitter/X 横图":           "1600×900",
        "LinkedIn 横图":            "1200×627",
    },
}
CUSTOM_LABEL = "✏️ 自定义尺寸"
for _cat in PRESET_CATEGORIES.values():
    _cat[CUSTOM_LABEL] = ""


# ═══════════════════════════════════════════════════════════════
#  线程安全消息
# ═══════════════════════════════════════════════════════════════
class _Msg:
    __slots__ = ('kind', 'payload')
    def __init__(self, kind: str, payload=None):
        self.kind = kind
        self.payload = payload


# ═══════════════════════════════════════════════════════════════
#  辅助：创建带颜色的按钮
# ═══════════════════════════════════════════════════════════════
def _make_btn(parent, text, command, style="secondary", font=None):
    """统一按钮工厂 — 保证 style 一致性"""
    styles = {
        "primary":   {"bg": T.PRIMARY,     "fg": T.WHITE,   "activebg": T.PRIMARY_HOV, "activefg": T.WHITE},
        "secondary": {"bg": T.BG_INPUT,    "fg": T.TEXT,    "activebg": T.BORDER,      "activefg": T.TEXT},
        "danger":    {"bg": T.ERROR,       "fg": T.WHITE,   "activebg": "#B91C1C",     "activefg": T.WHITE},
        "ghost":     {"bg": T.BG_PAGE,     "fg": T.TEXT_SEC,"activebg": T.BG_INPUT,    "activefg": T.TEXT},
    }
    s = styles.get(style, styles["secondary"])
    kwargs = dict(
        text=text, command=command,
        bg=s["bg"], fg=s["fg"], activebackground=s["activebg"], activeforeground=s["activefg"],
        font=font or T.FONT_BODY,
        relief=FLAT, borderwidth=0, highlightthickness=0,
        padx=T.MD, pady=T.XS,
        cursor="pointinghand" if os.environ.get("TERM_PROGRAM") else "",
    )
    return Button(parent, **kwargs)


# ═══════════════════════════════════════════════════════════════
#  应用主类
# ═══════════════════════════════════════════════════════════════
class ImageResizerApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("FrameKit · 图片尺寸转换")
        self.root.geometry("820x720")
        self.root.minsize(680, 560)
        self.root.configure(bg=T.BG_PAGE)

        # 去掉原生标题栏下的分割线感觉
        self.root.option_add("*Font", T.FONT_BODY)

        # 状态
        self.files: list[str] = []
        self.output_dir = StringVar(value=str(Path.home() / "Desktop"))
        self.custom_width = StringVar()
        self.custom_height = StringVar()
        self.category_var = StringVar(value="🍎 Apple")
        self.preset_var = StringVar(value="iPhone 通用投放")
        self.mode_var = StringVar(value="crop-center")
        self._cancelled = False
        self._converting = False

        # 消息队列
        self._msg_queue: queue.Queue[_Msg] = queue.Queue()

        self._build_ui()
        self._on_category_changed()
        self._on_preset_changed()
        self._poll_messages()

    # ═══════════════════════════════════════════════════════════
    #  消息轮询
    # ═══════════════════════════════════════════════════════════
    def _poll_messages(self):
        try:
            while True:
                msg = self._msg_queue.get_nowait()
                if msg.kind == "log":
                    self._write_log(*msg.payload)
                elif msg.kind == "progress":
                    self.progress["value"], text = msg.payload
                    self.status_label.config(text=text)
                elif msg.kind == "done":
                    self._on_done_ui(*msg.payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(80, self._poll_messages)

    def _emit_log(self, level: str, text: str):
        self._msg_queue.put(_Msg("log", (level, text)))

    def _emit_progress(self, val: int, text: str):
        self._msg_queue.put(_Msg("progress", (val, text)))

    def _emit_done(self, success: int, total: int, errors: list[str]):
        self._msg_queue.put(_Msg("done", (success, total, errors)))

    # ═══════════════════════════════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════════════════════════════
    def _build_ui(self):
        # ── 全局样式 ──
        style = ttk.Style()
        style.theme_use("aqua")
        style.configure("TProgressbar", troughcolor=T.BG_INPUT, background=T.PRIMARY, borderwidth=0, thickness=6)
        style.configure("TVertical.TScrollbar", background=T.BG_CARD, troughcolor=T.BG_PAGE, borderwidth=0, arrowsize=14)

        # ═══════════════════════════════════════════════════════
        #  1. 文件列表区域
        # ═══════════════════════════════════════════════════════
        section1 = self._section(self.root, "源文件（可多选）", "file")

        # 列表 + 滚动条
        list_frame = Frame(section1, bg=T.BG_CARD)
        list_frame.pack(fill=BOTH, expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", style="TVertical.TScrollbar")
        sb.pack(side=RIGHT, fill=Y)
        self.file_listbox = Listbox(
            list_frame, selectmode=MULTIPLE, yscrollcommand=sb.set,
            font=T.FONT_CODE, bg=T.BG_CARD, fg=T.TEXT,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            selectbackground=T.PRIMARY, selectforeground=T.WHITE,
            activestyle="none",
        )
        self.file_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        sb.config(command=self.file_listbox.yview)

        # 操作按钮行
        btn_row = Frame(section1, bg=T.BG_CARD)
        btn_row.pack(fill=X, pady=(T.SM, 0))
        _make_btn(btn_row, "➕ 添加图片", self._add_files, "secondary").pack(side=LEFT, padx=(0, T.XS))
        _make_btn(btn_row, "➖ 移除选中", self._remove_selected, "secondary").pack(side=LEFT, padx=(0, T.XS))
        _make_btn(btn_row, "清空列表", self._clear_files, "secondary").pack(side=LEFT)
        self._file_count_label = Label(btn_row, text="", fg=T.TEXT_MUTED, font=T.FONT_SMALL, bg=T.BG_CARD)
        self._file_count_label.pack(side=RIGHT)

        # ═══════════════════════════════════════════════════════
        #  2. 转换参数区域
        # ═══════════════════════════════════════════════════════
        section2 = self._section(self.root, "转换参数", "params")

        # 分类 + 预设 一行
        sel_row = Frame(section2, bg=T.BG_CARD)
        sel_row.pack(fill=X, pady=(0, T.SM))

        self._labeled(sel_row, "分类", 50).pack(side=LEFT, padx=(0, T.XS))
        self.category_menu = OptionMenu(
            sel_row, self.category_var, *PRESET_CATEGORIES.keys(),
            command=self._on_category_changed,
        )
        self.category_menu.config(
            bg=T.BG_INPUT, fg=T.TEXT, font=T.FONT_BODY,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            activebackground=T.BORDER, activeforeground=T.TEXT,
        )
        self.category_menu.pack(side=LEFT, padx=(0, T.LG))

        self._labeled(sel_row, "预设", 50).pack(side=LEFT, padx=(0, T.XS))
        self.preset_menu = OptionMenu(sel_row, self.preset_var, "")
        self.preset_menu.config(
            bg=T.BG_INPUT, fg=T.TEXT, font=T.FONT_BODY,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            activebackground=T.BORDER, activeforeground=T.TEXT,
        )
        self.preset_menu.pack(side=LEFT)

        # 宽 × 高 一行
        size_row = Frame(section2, bg=T.BG_CARD)
        size_row.pack(fill=X, pady=(0, T.SM))

        self._labeled(size_row, "尺寸", 50).pack(side=LEFT, padx=(0, T.XS))
        self.entry_w = Entry(
            size_row, textvariable=self.custom_width, width=7,
            font=T.FONT_CODE, bg=T.BG_INPUT, fg=T.TEXT,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            insertbackground=T.PRIMARY,
        )
        self.entry_w.pack(side=LEFT)
        Label(size_row, text=" × ", font=T.FONT_BODY, fg=T.TEXT_SEC, bg=T.BG_CARD).pack(side=LEFT)
        self.entry_h = Entry(
            size_row, textvariable=self.custom_height, width=7,
            font=T.FONT_CODE, bg=T.BG_INPUT, fg=T.TEXT,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            insertbackground=T.PRIMARY,
        )
        self.entry_h.pack(side=LEFT)
        Label(size_row, text=" px", font=T.FONT_SMALL, fg=T.TEXT_MUTED, bg=T.BG_CARD).pack(side=LEFT, padx=(T.XS, 0))

        # 裁切模式 一行
        mode_row = Frame(section2, bg=T.BG_CARD)
        mode_row.pack(fill=X, pady=(0, T.SM))
        self._labeled(mode_row, "模式", 50).pack(side=LEFT, padx=(0, T.XS))

        for text, val in [
            ("等比缩放 fit", "fit"),
            ("拉伸填充 fill", "fill"),
            ("居中裁切 crop", "crop-center"),
        ]:
            rb = ttk.Radiobutton(mode_row, text=text, variable=self.mode_var, value=val)
            rb.pack(side=LEFT, padx=(0, T.LG))

        # 输出路径 一行
        out_row = Frame(section2, bg=T.BG_CARD)
        out_row.pack(fill=X)
        self._labeled(out_row, "输出", 50).pack(side=LEFT, padx=(0, T.XS))
        Entry(
            out_row, textvariable=self.output_dir,
            font=T.FONT_SMALL, bg=T.BG_INPUT, fg=T.TEXT,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            insertbackground=T.PRIMARY,
        ).pack(side=LEFT, fill=X, expand=True, padx=(0, T.XS))
        _make_btn(out_row, "浏览...", self._browse_output, "secondary", T.FONT_SMALL).pack(side=LEFT)

        # ═══════════════════════════════════════════════════════
        #  3. 操作栏（进度 + 按钮）
        # ═══════════════════════════════════════════════════════
        action_bar = Frame(self.root, bg=T.BG_PAGE)
        action_bar.pack(fill=X, padx=T.LG, pady=(T.SM, T.XS))

        self.progress = ttk.Progressbar(action_bar, mode="determinate", style="TProgressbar")
        self.progress.pack(side=LEFT, fill=X, expand=True, padx=(0, T.MD))

        self.status_label = Label(
            action_bar, text="就绪", fg=T.TEXT_MUTED, font=T.FONT_SMALL,
            bg=T.BG_PAGE, anchor=W, width=18,
        )
        self.status_label.pack(side=LEFT)

        self.cancel_btn = _make_btn(action_bar, "取消", self._cancel, "danger")
        self.cancel_btn.pack(side=RIGHT, padx=(T.XS, 0))
        self.cancel_btn.config(state=DISABLED)

        self.convert_btn = _make_btn(action_bar, "🚀 开始转换", self._start_conversion, "primary", T.FONT_BTN)
        self.convert_btn.pack(side=RIGHT, padx=(0, T.XS))

        # ═══════════════════════════════════════════════════════
        #  4. 日志面板
        # ═══════════════════════════════════════════════════════
        section4 = self._section(self.root, "日志", "log")

        log_hdr = Frame(section4, bg=T.BG_CARD)
        log_hdr.pack(fill=X, pady=(0, T.XS))
        _make_btn(log_hdr, "清空日志", self._clear_log, "secondary", T.FONT_SMALL).pack(side=RIGHT)

        self.log_text = ScrolledText(
            section4, height=8, font=T.FONT_CODE_SM,
            bg=T.BG_INPUT, fg=T.TEXT,
            relief=FLAT, borderwidth=0, highlightthickness=0,
            state=DISABLED, wrap='word',
        )
        self.log_text.pack(fill=BOTH, expand=True)

        for tag, fg in [
            ("INFO", T.TEXT), ("OK", T.SUCCESS), ("ERROR", T.ERROR),
            ("WARN", T.WARN), ("DIM", T.TEXT_MUTED),
        ]:
            self.log_text.tag_config(tag, foreground=fg)

    # ═══════════════════════════════════════════════════════════
    #  UI 帮助方法
    # ═══════════════════════════════════════════════════════════
    def _section(self, parent: Frame, title: str, key: str) -> Frame:
        """创建带标题的卡片式区域"""
        outer = Frame(parent, bg=T.BG_PAGE)
        outer.pack(fill=BOTH, expand=("log" not in key), padx=T.LG, pady=(T.SM if key != "file" else T.LG, 0))

        # 标题
        Label(
            outer, text=title, font=T.FONT_LABEL, fg=T.TEXT_SEC, bg=T.BG_PAGE, anchor=W,
        ).pack(fill=X, pady=(0, T.XS))

        # 卡片容器
        card = Frame(outer, bg=T.BG_CARD)
        card.pack(fill=BOTH, expand=True, padx=0, pady=0)
        # 模拟轻微的 card 效果：用细线框
        for widget in [card]:
            pass

        return card

    def _labeled(self, parent: Frame, text: str, width: int = 60) -> Label:
        """创建标签（用于表单项左侧）"""
        return Label(parent, text=text, font=T.FONT_LABEL, fg=T.TEXT_SEC, bg=T.BG_CARD,
                     anchor=W, width=width // 10 if width > 10 else 5)

    # ═══════════════════════════════════════════════════════════
    #  日志
    # ═══════════════════════════════════════════════════════════
    def _write_log(self, level: str, text: str):
        self.log_text.config(state=NORMAL)
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(END, f"{ts}  ", "DIM")
        self.log_text.insert(END, f"{text}\n", level)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)

    def _clear_log(self):
        self.log_text.config(state=NORMAL)
        self.log_text.delete("1.0", END)
        self.log_text.config(state=DISABLED)

    # ═══════════════════════════════════════════════════════════
    #  分类 / 预设 联动
    # ═══════════════════════════════════════════════════════════
    def _on_category_changed(self, *_):
        cat = self.category_var.get()
        presets = PRESET_CATEGORIES.get(cat, {})
        keys = list(presets.keys())

        menu = self.preset_menu["menu"]
        menu.delete(0, END)
        for k in keys:
            menu.add_command(
                label=k,
                command=lambda v=k: (self.preset_var.set(v), self._on_preset_changed())
            )
        if keys:
            self.preset_var.set(keys[0])
            self._on_preset_changed()

    def _on_preset_changed(self, *_):
        preset = self.preset_var.get()
        cat = self.category_var.get()
        size_str = PRESET_CATEGORIES.get(cat, {}).get(preset, "")
        if "×" in size_str:
            w, h = size_str.split("×")
            self.custom_width.set(w.strip())
            self.custom_height.set(h.strip())
            self.entry_w.config(state=DISABLED, bg=T.BG_CARD, fg=T.TEXT)
            self.entry_h.config(state=DISABLED, bg=T.BG_CARD, fg=T.TEXT)
        else:
            self.entry_w.config(state=NORMAL, bg=T.BG_INPUT, fg=T.TEXT)
            self.entry_h.config(state=NORMAL, bg=T.BG_INPUT, fg=T.TEXT)

    # ═══════════════════════════════════════════════════════════
    #  事件
    # ═══════════════════════════════════════════════════════════
    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.heic *.webp *.avif"), ("所有", "*.*")],
        )
        added = 0
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.file_listbox.insert(END, p)
                added += 1
        self._update_file_count()
        if added:
            self._write_log("OK", f"添加了 {added} 个文件")

    def _remove_selected(self):
        for idx in reversed(self.file_listbox.curselection()):
            del self.files[idx]
            self.file_listbox.delete(idx)
        self._update_file_count()

    def _clear_files(self):
        self.files.clear()
        self.file_listbox.delete(0, END)
        self._update_file_count()

    def _update_file_count(self):
        n = len(self.files)
        self._file_count_label.config(text=f"{n} 个文件" if n else "")

    def _browse_output(self):
        d = filedialog.askdirectory(title="选择输出目录")
        if d:
            self.output_dir.set(d)

    def _cancel(self):
        self._cancelled = True
        self._write_log("WARN", "⏹ 用户取消，当前文件处理完后停止...")
        self.cancel_btn.config(state=DISABLED)

    # ═══════════════════════════════════════════════════════════
    #  转换逻辑
    # ═══════════════════════════════════════════════════════════
    def _get_target_size(self) -> tuple[int, int] | None:
        w_str = self.custom_width.get().strip()
        h_str = self.custom_height.get().strip()
        try:
            w, h = int(w_str), int(h_str)
            if w <= 0 or h <= 0:
                raise ValueError
            return w, h
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的正整数宽高")
            return None

    def _start_conversion(self):
        if self._converting:
            self._write_log("WARN", "转换进行中，请等待...")
            return
        if not self.files:
            messagebox.showwarning("提示", "请先添加图片文件")
            return

        target = self._get_target_size()
        if not target:
            return
        out = self.output_dir.get().strip()
        if not out or not os.path.isdir(out):
            messagebox.showerror("路径错误", "输出路径不存在")
            return

        self._cancelled = False
        self._converting = True
        self.convert_btn.config(state=DISABLED, text="转换中...", bg=T.BG_INPUT, fg=T.TEXT_SEC)
        self.cancel_btn.config(state=NORMAL)
        self.progress["maximum"] = len(self.files)
        self.progress["value"] = 0
        self.status_label.config(text="开始...", fg=T.TEXT)

        self._write_log("INFO", f"══════ 开始 {len(self.files)} 个文件 ══════")
        self._write_log("INFO", f"尺寸: {target[0]}×{target[1]}  模式: {self.mode_var.get()}")
        self._write_log("DIM", f"输出: {out}")

        mode = self.mode_var.get()
        threading.Thread(
            target=self._convert_all, args=(target, out, mode), daemon=True
        ).start()

    def _convert_all(self, target: tuple[int, int], out_dir: str, mode: str):
        tw, th = target
        total = len(self.files)
        success, errors = 0, []

        try:
            for i, src in enumerate(self.files):
                if self._cancelled:
                    self._emit_log("WARN", "转换已取消")
                    break

                sp = Path(src)
                out_name = f"{sp.stem}_{tw}x{th}{sp.suffix}"
                out_path = str(Path(out_dir) / out_name)

                self._emit_progress(i, f"{i+1}/{total}")
                self._emit_log("INFO", f"[{i+1}/{total}] {sp.name}")

                ok, err = self._resize_one(src, out_path, tw, th, mode)
                if ok:
                    success += 1
                    self._emit_log("OK", f"  ✅ {out_name}")
                else:
                    errors.append(f"{sp.name}: {err}")
                    self._emit_log("ERROR", f"  ❌ {err}")

        except Exception as e:
            self._emit_log("ERROR", f"💥 致命错误: {e}")
            self._emit_log("DIM", traceback.format_exc())
        finally:
            self._emit_done(success, total, errors)

    def _resize_one(self, src: str, dst: str, tw: int, th: int, mode: str) -> tuple[bool, str]:
        try:
            if mode in ("fit", "fill"):
                subprocess.run(
                    ["sips", "-z", str(th), str(tw), src, "--out", dst],
                    check=True, capture_output=True, timeout=60,
                )
                return True, ""
            elif mode == "crop-center":
                return self._crop_center(src, dst, tw, th)
            return False, f"未知模式: {mode}"
        except subprocess.TimeoutExpired:
            return False, "sips 超时（60s）"
        except subprocess.CalledProcessError as e:
            err = (e.stderr.decode() if e.stderr else str(e)).strip()
            return False, f"sips 失败: {err[:200]}"
        except FileNotFoundError:
            return False, "源文件不存在"
        except Exception as e:
            return False, f"异常: {e}"

    def _crop_center(self, src: str, dst: str, tw: int, th: int) -> tuple[bool, str]:
        tmp = ""
        try:
            r = subprocess.run(
                ["sips", "-g", "pixelWidth", "-g", "pixelHeight", src],
                capture_output=True, text=True, timeout=15,
            )
            if r.returncode != 0:
                return False, f"读取尺寸失败: {r.stderr.strip()[:100]}"

            ow = oh = 1
            for l in r.stdout.splitlines():
                if "pixelWidth" in l:
                    ow = int(l.split(":")[-1].strip())
                if "pixelHeight" in l:
                    oh = int(l.split(":")[-1].strip())
            if ow <= 0 or oh <= 0:
                return False, f"无法读取尺寸: {ow}×{oh}"

            scale = max(tw / ow, th / oh)
            sw, sh = max(int(ow * scale), tw), max(int(oh * scale), th)

            tmp = dst + ".tmp_resize.png"
            subprocess.run(
                ["sips", "-z", str(sh), str(sw), src, "--out", tmp],
                check=True, capture_output=True, timeout=60,
            )
            subprocess.run(
                ["sips", "-c", str(th), str(tw),
                 "--cropOffset", str(max(0, (sh - th) // 2)),
                 str(max(0, (sw - tw) // 2)),
                 tmp, "--out", dst],
                check=True, capture_output=True, timeout=60,
            )
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "crop sips 超时"
        except subprocess.CalledProcessError as e:
            err = (e.stderr.decode() if e.stderr else str(e)).strip()
            return False, f"crop 失败: {err[:200]}"
        except Exception as e:
            return False, f"crop 异常: {e}"
        finally:
            if tmp:
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    # ═══════════════════════════════════════════════════════════
    #  完成回调
    # ═══════════════════════════════════════════════════════════
    def _on_done_ui(self, success: int, total: int, errors: list[str]):
        self._converting = False
        self.convert_btn.config(
            state=NORMAL, text="🚀 开始转换",
            bg=T.PRIMARY, fg=T.WHITE,
            activebackground=T.PRIMARY_HOV, activeforeground=T.WHITE,
        )
        self.cancel_btn.config(state=DISABLED)
        self.progress["value"] = total

        cancelled = self._cancelled
        self._cancelled = False

        if cancelled:
            self.status_label.config(text=f"已取消 {success}/{total}", fg=T.WARN)
            self._write_log("WARN", f"══════ 已取消: {success}/{total} ══════")
        elif success == total:
            self.status_label.config(text="✅ 全部完成", fg=T.SUCCESS)
            self._write_log("OK", f"══════ {total}/{total} ✅ ══════")
            self.root.after(300, lambda: messagebox.showinfo(
                "完成", f"{total} 张图片全部转换完成！\n{self.output_dir.get()}"
            ))
        else:
            fail = total - success
            self.status_label.config(text=f"⚠ {success}/{total}", fg=T.ERROR)
            self._write_log("WARN", f"══════ {success}/{total} 成功, {fail} 失败 ══════")
            summary = "\n".join(f"  • {e}" for e in errors[:10])
            if len(errors) > 10:
                summary += f"\n  ... 还有 {len(errors)-10} 个"
            self.root.after(300, lambda: messagebox.showwarning(
                "完成", f"{success}/{total} 成功, {fail} 失败\n\n失败:\n{summary}"
            ))


# ═══════════════════════════════════════════════════════════════
def main():
    root = Tk()
    try:
        root.tk.call("::tk::unsupported::MacWindowStyle", "::appearance", "aqua")
    except Exception:
        pass
    ImageResizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
