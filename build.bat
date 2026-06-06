@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo   USBIP-WSL-Manager 一键构建 & 打包脚本
echo ============================================
echo.

:: ── 0. 清理旧产物 ──
echo [0/5] 清理旧构建产物...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "installer" rmdir /s /q "installer"
if exist "nuitka_build" rmdir /s /q "nuitka_build"
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo [OK] 清理完成
echo.

:: ── 1. 生成 ICO 图标 ──
echo [1/5] 生成 ICO 图标...
python -c "import cairosvg; cairosvg.svg2png(url='icon.svg',write_to='_tmp_icon.png',output_width=256,output_height=256); from PIL import Image; Image.open('_tmp_icon.png').save('icon.ico',format='ICO',sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])" 2>nul
if exist "_tmp_icon.png" del "_tmp_icon.png"
if exist "icon.ico" (
    echo [OK] icon.ico 已生成
) else (
    echo [WARN] 未找到 cairosvg/pillow，跳过图标生成
)
echo.

:: ── 2. PyInstaller 编译 ──
echo [2/5] PyInstaller 编译...
python -m PyInstaller usbip_manager.spec --noconfirm --distpath=dist
if %errorlevel% neq 0 (
    echo [错误] 编译失败
    pause
    exit /b 1
)
echo [OK] dist\USBIP-WSL-Manager.exe 已生成
echo.

:: ── 3. 查找 Inno Setup ──
set "ISCC="
for %%p in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
) do (
    if exist %%p set "ISCC=%%~p"
)

:: ── 4. Inno Setup 打包 ──
if "%ISCC%"=="" (
    echo [3/5] 跳过 - 未找到 Inno Setup
    echo.
    echo [===== 构建完成 =====]
    echo   可执行文件: dist\USBIP-WSL-Manager.exe
    echo.
    echo 如需生成安装包，请安装 Inno Setup:
    echo   https://jrsoftware.org/isdl.php
) else (
    echo [3/5] Inno Setup 打包安装程序...
    %ISCC% setup.iss
    if %errorlevel% neq 0 (
        echo [错误] 打包失败
        pause
        exit /b 1
    )
    echo [OK] installer\USBIP-WSL-Manager-Setup.exe 已生成
    echo.
    :: ── 5. 输出信息 ──
    echo [===== 构建完成 =====]
    echo   可执行文件: dist\USBIP-WSL-Manager.exe
    echo   安装包:     installer\USBIP-WSL-Manager-Setup.exe
)

echo.
echo [提示] 下一步: git add -A ^&^& git commit -m "release"
echo.
pause
