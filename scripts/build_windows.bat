@echo off
REM VoiceTextMaker Windows 打包脚本
REM 使用方法: 在 Windows 上运行此脚本

echo ========================================
echo   VoiceTextMaker Windows 打包脚本
echo ========================================

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

REM 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 PyInstaller...
    pip install pyinstaller
)

REM 安装项目依赖
echo [INFO] 安装项目依赖...
pip install -r requirements.txt

REM 创建 spec 文件
echo [INFO] 生成 PyInstaller 配置...
python scripts\create_spec.py

REM 执行打包
echo [INFO] 开始打包...
pyinstaller --clean dist\VoiceTextMaker.spec

if errorlevel 1 (
    echo [ERROR] 打包失败！
    pause
    exit /b 1
)

echo ========================================
echo   打包完成！
echo   输出目录: dist\VoiceTextMaker\
echo ========================================
echo.
echo 注意事项:
echo   1. 模型文件需要单独下载，不包含在 exe 中
echo   2. 首次运行需要配置模型路径
echo   3. 需要 NVIDIA GPU + CUDA 驱动才能使用 GPU 加速
echo.
pause
