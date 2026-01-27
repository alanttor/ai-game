@echo off
chcp 65001 >nul
echo ========================================
echo 智能链接摘要 Web 应用 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)
echo ✓ Python 环境检测通过
echo.

echo [2/3] 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 警告: 依赖安装可能存在问题，但尝试继续运行...
)
echo ✓ 依赖包安装完成
echo.

echo [3/3] 启动应用...
echo.
echo ========================================
echo 应用已启动！
echo 访问地址: http://localhost:6000
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python app.py

pause
