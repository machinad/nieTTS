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
echo 步骤2: 检查并安装依赖项
echo 正在检查依赖项更新...
pip list --format=freeze > installed_packages.txt
findstr /V "^-e" requirements.txt > temp_req.txt
pip install -r requirements.txt --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
del installed_packages.txt temp_req.txt

echo.
echo 步骤3: 创建桌面快捷方式
set SCRIPT_PATH=%~dp0run_tts_universal.bat
set WEB_SCRIPT_PATH=%~dp0web模式.bat

echo 创建普通模式快捷方式...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\文字转语音（窗口）.lnk');$s.TargetPath='%SCRIPT_PATH%';$s.WorkingDirectory='%~dp0';$s.Save()"

echo 创建Web模式快捷方式...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\文字转语音(Web模式).lnk');$s.TargetPath='%WEB_SCRIPT_PATH%';$s.WorkingDirectory='%~dp0';$s.Save()"

echo.
echo 安装完成！桌面已创建快捷方式。
echo 您可以选择使用普通模式或Web模式运行程序。
pause