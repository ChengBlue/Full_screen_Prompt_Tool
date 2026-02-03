@echo off
chcp 65001 >nul
echo 正在打包全屏离开提示工具...
echo.

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 请先安装 PyInstaller: pip install pyinstaller
    pause
    exit /b 1
)

pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 建议安装 Pillow 以支持 JPG/PNG 背景: pip install Pillow
    echo.
)

pyinstaller --clean build_exe.spec

if errorlevel 1 (
    echo 打包失败
    pause
    exit /b 1
)

echo.
echo 打包完成！可执行文件位置：dist\FullScreenPromptTool.exe
echo 可将 exe 和 config.json 复制到任意目录使用
echo.
pause
