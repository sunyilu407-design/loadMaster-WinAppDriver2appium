@echo off
chcp 65001 >nul
echo ================================================
echo    Appium 服务器启动脚本 (Windows版)
echo ================================================
echo.

REM 检查是否安装了Appium
where appium >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 未找到Appium，请先安装:
    echo    npm install -g appium@latest
    echo.
    pause
    exit /b 1
)

REM 获取配置中的端口
REM 精确匹配 appium_port（避免误匹配 appium_session_timeout 等字段导致端口带空格）
set APPIUM_HOST=127.0.0.1
set APPIUM_PORT=4723

for /f "tokens=2 delims== " %%a in ('findstr /r "^appium_port " "config\env.ini" 2^>nul') do set APPIUM_PORT=%%a

echo [INFO] Appium服务器配置:
echo    主机: %APPIUM_HOST%
echo    端口: %APPIUM_PORT%
echo.

REM 检查端口是否已被占用
netstat -ano | findstr ":%APPIUM_PORT% " >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [WARNING] 端口 %APPIUM_PORT% 已被占用，Appium可能已在运行
    echo    可访问 http://%APPIUM_HOST%:%APPIUM_PORT%/status 验证
    echo    如需重启请先关闭已有进程，按任意键继续...
    pause >nul
)

echo [INFO] 启动Appium 2.5.1 服务器...
echo    启动成功后会出现 "Appium REST http interface listener started" 字样
echo    浏览器访问 http://%APPIUM_HOST%:%APPIUM_PORT%/status 可验证是否就绪
echo.

REM 启动Appium（log-level info 让用户能看到启动结果）
appium --address %APPIUM_HOST% --port %APPIUM_PORT% --log-level info --local-timezone

echo.
echo [INFO] Appium服务器已停止
pause
