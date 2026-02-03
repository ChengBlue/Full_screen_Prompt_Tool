# -*- coding: utf-8 -*-
"""
全屏离开提示工具 - 配置界面
可视化修改配置项并保存，一键运行主程序
"""

import os
import json
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser

# 配置文件路径：打包成 exe 时使用 exe 所在目录
_SCRIPT_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_SCRIPT_DIR, "config.json")
_MAIN_SCRIPT = os.path.join(_SCRIPT_DIR, "main.py")  # 非 exe 时用 main.py --fullscreen

# 默认配置（与主程序一致）
DEFAULT_CONFIG = {
    "message_text": "请勿长时间离开座位",
    "background_color": "#1a1a1a",
    "background_image_path": "",
    "message_color": "#f9f9f9",
    "message_color_alt": "#d9d9d9",
    "time_color": "#ffd700",
    "message_font_size": 60,
    "time_font_size": 40,
    "message_blink_enabled": True,
    "blink_interval_ms": 1000,
}


def load_config():
    """从 config.json 加载配置"""
    if os.path.isfile(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置到 config.json"""
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


class ConfigUI:
    """配置界面主窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("全屏离开提示工具 - 配置")
        self.root.minsize(480, 520)
        self.root.geometry("540x580")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f5")

        self.config = load_config()
        self._build_ui()

    def _build_ui(self):
        """构建界面：上-配置区（可滚动） | 下-操作栏（固定）"""
        main = ttk.Frame(self.root, padding=24)
        main.pack(fill=tk.BOTH, expand=True)

        # ========== 1. 顶部标题 ==========
        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(header, text="全屏离开提示工具", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w")
        ttk.Label(header, text="配置", font=("Microsoft YaHei UI", 12), foreground="#888").pack(anchor="w")

        # ========== 2. 配置区（可滚动，占据中间弹性空间） ==========
        config_container = ttk.Frame(main)
        config_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(config_container, highlightthickness=0, bg="#f5f5f5")
        scrollbar = ttk.Scrollbar(config_container)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        scroll_win_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=canvas.yview)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置项网格布局
        self.entries = {}
        fields = [
            ("message_text", "提示语内容", "str", "离开时显示的标语"),
            ("background_color", "背景色", "color", "无图时使用"),
            ("background_image_path", "背景图路径", "path", "留空用纯色背景"),
            ("message_color", "提示语主色", "color", None),
            ("message_color_alt", "提示语闪烁交替色", "color", None),
            ("time_color", "时间文字颜色", "color", None),
            ("message_font_size", "提示语字号", "int", "磅"),
            ("time_font_size", "时间字号", "int", "磅"),
            ("message_blink_enabled", "开启闪烁", "bool", None),
            ("blink_interval_ms", "闪烁间隔", "int", "毫秒，1秒=1000"),
        ]

        for i, (key, label, ftype, hint) in enumerate(fields):
            row = ttk.Frame(scroll_frame)
            row.pack(fill=tk.X, pady=6)

            lbl = ttk.Label(row, text=label + "：", width=14, anchor="e")
            lbl.pack(side=tk.LEFT, padx=(0, 10))

            if ftype == "str":
                var = tk.StringVar(value=self.config.get(key, ""))
                e = ttk.Entry(row, textvariable=var)
                e.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entries[key] = ("str", var)

            elif ftype == "path":
                var = tk.StringVar(value=self.config.get(key, ""))
                frm = ttk.Frame(row)
                frm.pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Entry(frm, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Button(frm, text="浏览…", width=7, command=lambda k=key: self._browse_file(k)).pack(side=tk.LEFT, padx=(6, 0))
                self.entries[key] = ("str", var)

            elif ftype == "color":
                var = tk.StringVar(value=self.config.get(key, "#000000"))
                color_frm = ttk.Frame(row)
                color_frm.pack(side=tk.LEFT)
                ttk.Entry(color_frm, textvariable=var, width=10).pack(side=tk.LEFT)
                # 调色盘按钮：点击打开颜色选择器
                swatch = tk.Canvas(color_frm, width=26, height=22, highlightthickness=1, highlightbackground="#ccc")
                swatch.pack(side=tk.LEFT, padx=(6, 0))
                self._draw_color_swatch(swatch, var.get())
                ttk.Button(color_frm, text="调色盘", width=6, command=lambda k=key, s=swatch, v=var: self._pick_color(k, s, v)).pack(side=tk.LEFT, padx=(6, 0))
                var.trace_add("write", lambda *_, canvas=swatch, v=var: self._draw_color_swatch(canvas, v.get()))
                self.entries[key] = ("color", var)

            elif ftype == "int":
                var = tk.StringVar(value=str(self.config.get(key, 0)))
                ttk.Entry(row, textvariable=var, width=8).pack(side=tk.LEFT)
                self.entries[key] = ("int", var)

            elif ftype == "bool":
                var = tk.BooleanVar(value=self.config.get(key, True))
                ttk.Checkbutton(row, variable=var, text="是").pack(side=tk.LEFT)
                self.entries[key] = ("bool", var)

            if hint:
                ttk.Label(row, text=f"({hint})", font=("", 9), foreground="#999").pack(side=tk.LEFT, padx=(8, 0))

        # 滚轮滚动
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind_mw(e):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mw(e):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", _bind_mw)
        canvas.bind("<Leave>", _unbind_mw)

        # 窗口缩放时，配置区宽度自适应
        def _on_canvas_resize(e):
            canvas.itemconfig(scroll_win_id, width=e.width)
        canvas.bind("<Configure>", _on_canvas_resize)

        # ========== 3. 底部操作栏（固定，始终可见） ==========
        bottom_bar = ttk.Frame(main)
        bottom_bar.pack(fill=tk.X, pady=(20, 0))

        # 分隔线
        sep = ttk.Separator(bottom_bar, orient="horizontal")
        sep.pack(fill=tk.X, pady=(0, 16))

        # ESC 提示（放在最下面一行）
        hint_frame = ttk.Frame(bottom_bar)
        hint_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(hint_frame, text="💡 运行全屏程序后，按 ESC 键可退出", font=("Microsoft YaHei UI", 10), foreground="#666").pack(anchor="w")

        # 按钮行
        btn_frame = ttk.Frame(bottom_bar)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="保存配置", command=self._save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="运行全屏提示", command=self._run_main).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="恢复默认", command=self._reset_default).pack(side=tk.LEFT)

    def _draw_color_swatch(self, canvas, hex_color):
        """在 canvas 上绘制颜色色块"""
        try:
            c = hex_color.strip()
            if not c.startswith("#"):
                c = "#" + c
            if len(c) == 7 and all(x in "0123456789abcdefABCDEF" for x in c[1:]):
                canvas.delete("all")
                canvas.create_rectangle(2, 2, 24, 20, fill=c, outline="#999")
        except Exception:
            pass

    def _pick_color(self, key, swatch, var):
        """打开调色盘选择颜色"""
        current = var.get().strip()
        if current and not current.startswith("#"):
            current = "#" + current
        result = colorchooser.askcolor(
            color=current or "#000000",
            title="编辑颜色 - " + {"background_color": "背景色", "message_color": "提示语主色", "message_color_alt": "提示语闪烁交替色", "time_color": "时间文字颜色"}.get(key, key),
        )
        if result and result[1]:
            var.set(result[1])
            self._draw_color_swatch(swatch, result[1])

    def _browse_file(self, key):
        """浏览选择背景图文件"""
        path = filedialog.askopenfilename(
            title="选择背景图",
            filetypes=[("图片 (JPG/PNG/GIF)", "*.jpg *.jpeg *.png *.gif *.ppm *.pgm"), ("所有文件", "*.*")]
        )
        if path:
            self.entries[key][1].set(path)

    def _collect_config(self):
        """从界面收集配置"""
        cfg = {}
        for key, (ftype, var) in self.entries.items():
            if ftype == "str":
                cfg[key] = var.get().strip()
            elif ftype == "color":
                cfg[key] = var.get().strip() or "#1a1a1a"
            elif ftype == "int":
                try:
                    cfg[key] = int(var.get())
                except ValueError:
                    cfg[key] = DEFAULT_CONFIG.get(key, 0)
            elif ftype == "bool":
                cfg[key] = var.get()
        return cfg

    def _save(self):
        """保存配置到文件"""
        self.config = self._collect_config()
        save_config(self.config)
        messagebox.showinfo("保存成功", "配置已保存到 config.json")

    def _run_main(self):
        """运行全屏提示主程序"""
        # 先保存当前配置
        self.config = self._collect_config()
        save_config(self.config)

        try:
            kwargs = {"cwd": _SCRIPT_DIR}
            if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            # 打包成 exe 时启动同目录 exe 并传 --fullscreen；否则用 Python 运行脚本
            if getattr(sys, "frozen", False):
                cmd = [sys.executable, "--fullscreen"]
            else:
                cmd = [sys.executable, _MAIN_SCRIPT, "--fullscreen"]
            subprocess.Popen(cmd, **kwargs)
            messagebox.showinfo("已启动", "全屏提示程序已启动！\n\n按 ESC 键可退出全屏。")
        except Exception as e:
            messagebox.showerror("启动失败", str(e))

    def _reset_default(self):
        """恢复默认配置"""
        if messagebox.askyesno("确认", "确定要恢复为默认配置吗？"):
            self.config = DEFAULT_CONFIG.copy()
            save_config(self.config)
            for key, (ftype, var) in self.entries.items():
                if ftype == "bool":
                    var.set(self.config.get(key, True))
                elif ftype == "int":
                    var.set(str(self.config.get(key, 0)))
                else:
                    var.set(self.config.get(key, ""))
            messagebox.showinfo("已恢复", "已恢复为默认配置")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ConfigUI()
    app.run()
