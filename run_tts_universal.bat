@echo off
echo 正在启动文字转语音程序...

:: 尝试查找pythonw.exe的路径
for /f "tokens=*" %%i in ('where pythonw 2^>nul') do (
    set PYTHONW_PATH=%%i
    goto :found
)

:: 如果找不到pythonw，尝试从注册表获取Python安装路径
for /f "tokens=*" %%i in ('reg query HKEY_CURRENT_USER\Software\Python\PythonCore /f * /k 2^>nul ^| findstr /i PythonCore') do (
    for /f "tokens=*" %%j in ('reg query "%%i\InstallPath" /ve 2^>nul ^| findstr REG_SZ') do (
        for /f "tokens=2*" %%k in ('echo %%j') do (
            set PYTHON_DIR=%%l
            if exist "!PYTHON_DIR!\pythonw.exe" (
                set PYTHONW_PATH="!PYTHON_DIR!\pythonw.exe"
                goto :found
            )
        )
    )
)

:: 如果还是找不到，使用默认路径
if not defined PYTHONW_PATH (
    echo 警告：无法找到pythonw.exe，将尝试使用默认路径
    set PYTHONW_PATH=pythonw.exe
)

:found
echo 使用 %PYTHONW_PATH% 运行程序
start "" %PYTHONW_PATH% "%~dp0text_to_speech.py"
exit