@echo off
chcp 65001 >nul
echo 正在安装文字转语音程序...
echo.
echo 步骤1: 检查Python安装
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到Python，正在下载并安装Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe' -OutFile 'python_installer.exe'"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
) else (
    echo 已检测到Python安装
)

echo.
echo 步骤2: 安装依赖项
pip install -r requirements.txt

echo.
echo 步骤3: 创建桌面快捷方式
set SCRIPT_PATH=%~dp0run_tts_universal.bat
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\文字转语音.lnk');$s.TargetPath='%SCRIPT_PATH%';$s.WorkingDirectory='%~dp0';$s.Save()"

echo.
echo 安装完成！桌面已创建快捷方式。
pause