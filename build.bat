@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Local Game Library - Build

echo ============================================
echo   Local Game Library - Build EXE
echo ============================================
echo.

:: Prefer Python launcher if available
set "PY=python"
where py >nul 2>&1 && set "PY=py -3"

echo [1/4] Checking Python...
%PY% --version
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found. Install Python 3 and try again.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/4] Installing / updating build dependencies...
%PY% -m pip install --upgrade pip
%PY% -m pip install --upgrade pyinstaller pillow pystray
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

if not exist "LocalGameLibrary.py" (
    echo.
    echo ERROR: LocalGameLibrary.py not found in:
    echo   %cd%
    echo Put build.bat next to LocalGameLibrary.py and run again.
    pause
    exit /b 1
)

if not exist "app.ico" (
    echo.
    echo WARNING: app.ico not found. Building without a custom icon.
    set "ICON_ARGS="
) else (
    set "ICON_ARGS=--icon app.ico --add-data app.ico;."
)

echo.
echo [3/4] Cleaning previous build folders...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Local Game Library.spec" del /q "Local Game Library.spec"
if exist LocalGameLibrary.spec del /q LocalGameLibrary.spec

echo.
echo [4/4] Building standalone EXE (this may take a minute)...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name "Local Game Library" %ICON_ARGS% LocalGameLibrary.py
if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build finished
echo ============================================
echo.
echo EXE location:
echo   %cd%\dist\Local Game Library.exe
echo.
echo Game data is stored in:
echo   %%APPDATA%%\LocalGameLibrary\
echo.

if exist "dist\Local Game Library.exe" (
    explorer /select,"dist\Local Game Library.exe"
)

echo Done.
pause
endlocal
