# 电脑桌面全屏离开提示工具

使用 Python `tkinter` 开发的桌面全屏离开提醒工具，适用于 Windows 系统。离开工位时启动，全屏显示自定义提示语和实时时间，按 **ESC** 键即可退出。

## 功能特性

| 功能       | 说明                                        |
| ---------- | ------------------------------------------- |
| 全屏无框   | 无标题栏、无边框，沉浸式显示                |
| 窗口置顶   | 始终保持在最前端                            |
| ESC 退出   | 随时按 ESC 键关闭                           |
| 提示语闪烁 | 柔和 1 秒间隔闪烁，可关闭                   |
| 实时时间   | 格式 `2025-01-01 星期一 12:00:00`，每秒刷新 |
| 背景图     | 支持 JPG/PNG/GIF，自动适配全屏（保持比例）  |
| 配置界面   | 可视化修改配置，调色盘选色，一键运行        |

## 项目结构

```
Full_screen_Prompt_Tool/
├── main.py               # 统一入口（推荐）
├── config_ui.py          # 配置界面
├── fullscreen_prompt_tool.py   # 全屏主程序
├── config.json           # 配置文件（自动生成）
├── requirements.txt      # 依赖（JPG/PNG 背景需 Pillow）
├── build_exe.spec        # PyInstaller 打包配置
├── build_exe.bat         # 一键打包脚本
└── README.md
```

## 快速开始

### 1. 环境要求

- Python 3.7+
- Windows 系统

### 2. 安装依赖（使用 JPG/PNG 背景图时必装）

```bash
pip install -r requirements.txt
```

或直接安装 Pillow：

```bash
pip install Pillow
```

### 3. 运行

**推荐：通过配置界面**

```bash
python main.py
```

或

```bash
python config_ui.py
```

- 修改提示语、颜色、背景图等
- 点击「保存配置」后点击「运行全屏提示」
- 全屏显示后按 **ESC** 退出

**直接运行全屏：**

```bash
python main.py --fullscreen
```

从 `config.json` 读取配置，无配置文件时使用默认值。

> 打包为 exe：执行 `build_exe.bat` 或详见 [生成 exe 可执行文件](#生成-exe-可执行文件)。

## 配置说明

### 配置界面功能

| 功能         | 说明                                          |
| ------------ | --------------------------------------------- |
| 提示语       | 文本输入，离开时显示的标语                    |
| 背景色       | 调色盘选择，无图时使用                        |
| 背景图       | 输入路径或点击「浏览…」选择，支持 JPG/PNG/GIF |
| 调色盘       | 颜色项旁可点击打开系统颜色选择器              |
| 保存配置     | 写入 config.json                              |
| 运行全屏提示 | 保存后启动主程序                              |
| 恢复默认     | 重置为默认配置                                |

### 配置项一览

| 配置项                  | 说明             | 默认值                 |
| ----------------------- | ---------------- | ---------------------- |
| `message_text`          | 提示语内容       | `"请勿长时间离开座位"` |
| `background_color`      | 背景色           | `#1a1a1a`              |
| `background_image_path` | 背景图路径       | `""`（留空用纯色）     |
| `message_color`         | 提示语主色       | `#f9f9f9`              |
| `message_color_alt`     | 提示语闪烁交替色 | `#d9d9d9`              |
| `time_color`            | 时间文字颜色     | `#ffd700`              |
| `message_font_size`     | 提示语字号（磅） | `60`                   |
| `time_font_size`        | 时间字号（磅）   | `40`                   |
| `message_blink_enabled` | 是否开启闪烁     | `true`                 |
| `blink_interval_ms`     | 闪烁间隔（毫秒） | `1000`                 |

### 背景图说明

- **支持格式**：JPG、JPEG、PNG、GIF 等
- **JPG/PNG**：需安装 Pillow
- **中文路径**：支持中文路径和文件名
- **显示效果**：按比例缩放适配全屏，不变形不拉伸
- **示例**：`C:/Users/xxx/Desktop/star.jpg`

### 布局

- 提示语：屏幕 40% 高度，水平居中
- 时间：屏幕 60% 高度，水平居中

## 使用场景

- 离开工位时提醒他人勿动电脑
- 会议、演示时的占位提示
- 锁屏前的临时全屏提醒

## 故障排除

### 背景图不显示

1. **确认已安装 Pillow**：`pip install Pillow`
2. **检查路径**：文件是否存在，路径是否正确
3. **查看日志**：若加载失败，会在项目目录生成 `bg_load_error.txt`，记录具体错误

### 程序无法启动

- 检查 Python 版本：`python --version`
- 在项目目录下运行：`cd 项目路径` 后再执行命令

## 生成 exe 可执行文件

将程序打包为独立 exe，可免 Python 环境直接运行，且**无控制台黑框**。

### 前置条件

- Python 3.7+、Windows
- 已安装项目依赖：`pip install -r requirements.txt`（含 Pillow）
- 安装 PyInstaller：`pip install pyinstaller`

### 方式一：一键打包（推荐）

在项目目录下双击或命令行执行：

```bash
build_exe.bat
```

脚本会自动检查 PyInstaller，执行打包并提示完成。

### 方式二：手动打包

```bash
# 1. 安装打包工具与依赖
pip install pyinstaller Pillow

# 2. 进入项目目录
cd Full_screen_Prompt_Tool

# 3. 执行打包
pyinstaller --clean build_exe.spec
```

### 输出结果

| 位置                            | 说明                   |
| ------------------------------- | ---------------------- |
| `dist/FullScreenPromptTool.exe` | 可执行文件，可直接运行 |
| `build/`                        | 临时构建文件，可删除   |

### exe 使用说明

1. **双击运行**：打开配置界面
2. **配置与运行**：修改设置后点击「运行全屏提示」
3. **按 ESC 退出**：全屏时按 ESC 关闭
4. **config.json**：首次运行在 exe 同目录生成，用于保存配置

### 分发与部署

- 可将 `FullScreenPromptTool.exe` 复制到任意目录使用
- 建议将 exe 和 `config.json` 放同一文件夹
- 可创建桌面快捷方式，或固定到任务栏
- exe 为单文件，无需额外安装 Python 或依赖

### 打包故障排除

| 问题                   | 解决                                                         |
| ---------------------- | ------------------------------------------------------------ |
| 提示找不到 pyinstaller | `pip install pyinstaller`                                    |
| 打包后 exe 运行报错    | 确认已安装 Pillow，重新执行 `pyinstaller --clean build_exe.spec` |
| 仍有黑框               | 检查 `build_exe.spec` 中 `console=False` 是否生效            |
| 杀毒软件报毒           | 属 PyInstaller 打包常见误报，可加入白名单                    |

## 技术说明

- **主程序**：`tkinter` Canvas，文字与背景叠加
- **配置界面**：`tkinter` + `ttk`，配置持久化到 JSON
- **字体**：微软雅黑（提示语粗体、时间常规体）
- **时间**：24 小时制，含日期与星期

## 许可

自由使用与修改。
