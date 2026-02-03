# -*- coding: utf-8 -*-
"""
全屏离开提示工具 - 统一入口
- 直接运行：打开配置界面
- 带 --fullscreen 参数：直接运行全屏提示
"""

import sys

if __name__ == "__main__":
    if "--fullscreen" in sys.argv:
        from fullscreen_prompt_tool import FullScreenPromptApp
        app = FullScreenPromptApp()
        app.run()
    else:
        from config_ui import ConfigUI
        app = ConfigUI()
        app.run()
