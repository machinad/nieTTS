@echo off
chcp 65001 >nul
echo 正在卸载文字转语音程序...
echo.
echo 步骤1: 删除桌面快捷方式
if exist "%USERPROFILE%\Desktop\文字转语音.lnk" (
    del "%USERPROFILE%\Desktop\文字转语音.lnk"
    echo 已删除桌面快捷方式
) else (
    echo 未找到桌面快捷方式
)

echo.
echo 步骤2: 清理Python依赖项
pip uninstall -y -r requirements.txt

echo.
echo 卸载完成！
pause