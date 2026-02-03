# -*- coding: utf-8 -*-
"""
电脑桌面全屏离开提示工具
使用 Python 内置 tkinter 库，无第三方依赖
适用于 Windows 系统
"""

import os
import sys
import json
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime

# 配置文件路径：打包成 exe 时使用 exe 所在目录
_SCRIPT_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_SCRIPT_DIR, "config.json")

# =============================================================================
# 【默认配置】—— 无 config.json 时使用；可通过配置 UI 或直接编辑 config.json 覆盖
# =============================================================================

DEFAULT_CONFIG = {
    # ① 提示语内容（离开时显示的标语）
    "message_text": "请勿长时间离开座位",

    # ② 背景设置
    "background_color": "#1a1a1a",        # 背景色（无背景图时使用）
    "background_image_path": "",          # 背景图路径，留空则使用背景色；推荐 gif/ppm/pgm，部分环境支持 png

    # ③ 文字颜色
    "message_color": "#f9f9f9",           # 提示语颜色
    "message_color_alt": "#d9d9d9",       # 提示语闪烁时的交替色（柔和效果）
    "time_color": "#ffd700",              # 时间文字颜色（金色）

    # ④ 字体大小（单位：磅）
    "message_font_size": 60,              # 提示语字体大小
    "time_font_size": 40,                 # 时间字体大小

    # ⑤ 闪烁开关
    "message_blink_enabled": True,        # True=开启闪烁，False=关闭闪烁
    "blink_interval_ms": 1000,            # 闪烁间隔（毫秒），1秒=1000
}


def _load_config():
    """加载配置：优先从 config.json 读取，缺失项用默认值"""
    config = DEFAULT_CONFIG.copy()
    if os.path.isfile(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            config.update(saved)
        except Exception:
            pass
    return config


# 当前使用的配置（程序启动时加载）
CONFIG = _load_config()


# =============================================================================
# 主程序
# =============================================================================

class FullScreenPromptApp:
    """全屏离开提示主窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("离开提示")
        self.root.configure(bg=CONFIG["background_color"])

        # 存储背景图引用，防止被垃圾回收
        self._bg_photo = None
        self._scaled_bg_photo = None

        # 闪烁状态
        self._blink_state = True

        self._setup_window()
        self._create_ui()
        self._bind_events()
        self._start_updates()

    def _setup_window(self):
        """设置窗口：全屏无框、置顶"""
        # 获取屏幕尺寸（需先显示才能正确获取，此处用 winfo_screen 即可）
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        # 去除窗口边框和标题栏
        self.root.overrideredirect(True)
        # 全屏：overrideredirect 与 -fullscreen 冲突，故用 geometry 实现
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        # 窗口置顶
        self.root.attributes("-topmost", True)

    def _create_ui(self):
        """创建界面：背景图/色、提示语、时间"""
        # 使用 Canvas 作为主容器，便于叠加背景图与文字
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0,
            bg=CONFIG["background_color"],
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 1. 先创建提示语和时间（需在背景图之前，以便正确设置层级）
        msg_font = ("Microsoft YaHei UI", CONFIG["message_font_size"], "bold")
        self.message_id = self.canvas.create_text(
            self.screen_width // 2,
            int(self.screen_height * 0.40),
            text=CONFIG["message_text"],
            font=msg_font,
            fill=CONFIG["message_color"],
            anchor="center",
            justify="center",
        )
        time_font = ("Microsoft YaHei UI", CONFIG["time_font_size"], "normal")
        self.time_id = self.canvas.create_text(
            self.screen_width // 2,
            int(self.screen_height * 0.60),
            text=self._get_time_str(),
            font=time_font,
            fill=CONFIG["time_color"],
            anchor="center",
        )

        # 2. 绘制背景图（若有路径且能加载），延后绘制确保窗口已显示
        if CONFIG["background_image_path"]:
            self.root.after(100, self._draw_background_image)

        # 3. 确保文字在背景之上
        self.canvas.tag_raise(self.message_id)
        self.canvas.tag_raise(self.time_id)

    def _draw_background_image(self):
        """绘制背景图，自动适配全屏（保持比例，不变形）"""
        path = (CONFIG.get("background_image_path") or "").strip()
        if not path:
            return
        path = os.path.normpath(path)
        if not os.path.isfile(path):
            try:
                with open(os.path.join(_SCRIPT_DIR, "bg_load_error.txt"), "w", encoding="utf-8") as f:
                    f.write(f"文件不存在: {path}")
            except Exception:
                pass
            return

        use_pil = False
        img = None
        try:
            from PIL import Image, ImageTk
            # 用二进制流打开，避免中文路径/文件名编码问题（Windows 常见）
            with open(path, "rb") as f:
                img = Image.open(f).copy().convert("RGB")
            use_pil = True
        except ImportError:
            try:
                self._bg_photo = tk.PhotoImage(file=path)
            except Exception as e:
                try:
                    with open(os.path.join(_SCRIPT_DIR, "bg_load_error.txt"), "w", encoding="utf-8") as f:
                        f.write(f"PIL未安装，tk加载失败: {e}\n路径: {path}")
                except Exception:
                    pass
                return
        except Exception as e:
            try:
                with open(os.path.join(_SCRIPT_DIR, "bg_load_error.txt"), "w", encoding="utf-8") as f:
                    f.write(f"PIL加载失败: {e}\n路径: {path}")
            except Exception:
                pass
            return

        if use_pil and img is not None:
            try:
                img_w, img_h = img.size
                if img_w <= 0 or img_h <= 0:
                    return

                # 计算缩放尺寸：适配全屏，保持比例（contain 模式）
                scale_w = self.screen_width / img_w
                scale_h = self.screen_height / img_h
                scale = min(scale_w, scale_h)
                new_w = max(1, int(img_w * scale))
                new_h = max(1, int(img_h * scale))

                # 使用 PIL 缩放（支持任意比例，质量更好）
                resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                img_scaled = img.resize((new_w, new_h), resample)
                self._bg_photo = ImageTk.PhotoImage(img_scaled)
                self._scaled_bg_photo = self._bg_photo
            except Exception as e:
                try:
                    with open(os.path.join(_SCRIPT_DIR, "bg_load_error.txt"), "w", encoding="utf-8") as f:
                        f.write(f"PIL缩放/转换失败: {e}\n路径: {path}")
                except Exception:
                    pass
                return
        else:
            # 使用 tk.PhotoImage（仅 GIF 等），需 zoom/subsample
            img_w = self._bg_photo.width()
            img_h = self._bg_photo.height()
            scale_w = self.screen_width / img_w
            scale_h = self.screen_height / img_h
            scale = min(scale_w, scale_h)
            if scale < 1:
                sub = max(1, int(1 / scale))
                self._scaled_bg_photo = self._bg_photo.subsample(sub, sub)
            else:
                zoom = max(1, int(scale))
                self._scaled_bg_photo = self._bg_photo.zoom(zoom, zoom)

        x = self.screen_width // 2
        y = self.screen_height // 2

        self.canvas.create_image(x, y, image=self._scaled_bg_photo, anchor="center", tags=("bg_image",))
        self.canvas.tag_lower("bg_image")
        self.canvas.tag_raise(self.message_id)
        self.canvas.tag_raise(self.time_id)

    def _get_time_str(self):
        """获取当前时间字符串：2025-01-01 星期一 12:00:00"""
        weekdays = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
        now = datetime.now()
        wd = weekdays[now.weekday()]
        return now.strftime(f"%Y-%m-%d {wd} %H:%M:%S")

    def _update_time(self):
        """每秒刷新时间"""
        self.canvas.itemconfig(self.time_id, text=self._get_time_str())
        self.root.after(1000, self._update_time)

    def _toggle_blink(self):
        """提示语柔和闪烁（交替颜色）"""
        if not CONFIG["message_blink_enabled"]:
            self.root.after(CONFIG["blink_interval_ms"], self._toggle_blink)
            return

        self._blink_state = not self._blink_state
        color = CONFIG["message_color"] if self._blink_state else CONFIG["message_color_alt"]
        self.canvas.itemconfig(self.message_id, fill=color)
        self.root.after(CONFIG["blink_interval_ms"], self._toggle_blink)

    def _start_updates(self):
        """启动定时更新：时间刷新、闪烁"""
        self.root.after(1000, self._update_time)
        if CONFIG["message_blink_enabled"]:
            self.root.after(CONFIG["blink_interval_ms"], self._toggle_blink)

    def _bind_events(self):
        """绑定键盘事件：ESC 退出"""
        self.root.bind("<Escape>", lambda e: self._quit())
        self.root.bind("<KeyPress-Escape>", lambda e: self._quit())

    def _quit(self):
        """退出程序"""
        self.root.quit()
        self.root.destroy()

    def run(self):
        """运行主循环"""
        self.root.mainloop()


# =============================================================================
# 程序入口
# =============================================================================

if __name__ == "__main__":
    app = FullScreenPromptApp()
    app.run()
