@echo on
chcp 65001 >nul
echo 正在启动Web模式...
echo.
python "%~dp0app.py"
pause