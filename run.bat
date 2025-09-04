@echo off
setlocal enabledelayedexpansion

:: === AUTO PLAYTIME RUNNER WITH VIRTUAL ENVIRONMENT ===
echo.
echo ======================================================
echo    AUTO PLAYTIME - ROBLOX RIVALS LAUNCHER
echo ======================================================
echo    By: Eman
echo    Discord: https://discord.gg/W5DgDZ4Hu6
echo ======================================================
echo.

:: === CONFIGURATION ===
set "SCRIPT=AutoPlaytime.py"
set "REQUIREMENTS=requirements.txt"
set "VENV_NAME=.venv"
set "PYTHON_INSTALLER=python-3.12.1-amd64.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/%PYTHON_INSTALLER%"

:: === SCRIPT PATH ===
set "SCRIPTPATH=%~dp0"
cd /d "%SCRIPTPATH%"

:: === VIRTUAL ENVIRONMENT PATHS ===
set "VENV_DIR=%SCRIPTPATH%%VENV_NAME%"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"
set "VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat"

:: === PYTHON PATHS ===
set "PYTHON_DIR1=%ProgramFiles%\Python312"
set "PYTHON_EXE1=%PYTHON_DIR1%\python.exe"
set "PYTHON_DIR2=%LocalAppData%\Programs\Python\Python312"
set "PYTHON_EXE2=%PYTHON_DIR2%\python.exe"

:: === CHECK IF VIRTUAL ENVIRONMENT EXISTS AND IS WORKING ===
if exist "%VENV_PYTHON%" (
    echo [*] Virtual environment found. Testing...
    "%VENV_PYTHON%" --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo [+] Virtual environment is working!
        goto install_deps
    ) else (
        echo [!] Virtual environment is corrupted. Recreating...
        rmdir /s /q "%VENV_DIR%" >nul 2>&1
    )
)

:: === FIND PYTHON INSTALLATION ===
echo [*] Looking for Python 3.12 installation...
if exist "%PYTHON_EXE1%" (
    set "PYTHON_EXE=%PYTHON_EXE1%"
    set "PYTHON_DIR=%PYTHON_DIR1%"
    echo [+] Python 3.12 found at %PYTHON_EXE%
    goto create_venv
)
if exist "%PYTHON_EXE2%" (
    set "PYTHON_EXE=%PYTHON_EXE2%"
    set "PYTHON_DIR=%PYTHON_DIR2%"
    echo [+] Python 3.12 found at %PYTHON_EXE%
    goto create_venv
)

:: === INSTALL PYTHON IF NOT FOUND ===
echo [!] Python 3.12 not found. Installing automatically...
echo [*] Downloading Python installer...
curl -L --progress-bar -o "%SCRIPTPATH%%PYTHON_INSTALLER%" "%PYTHON_URL%"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to download Python installer!
    echo Please download Python 3.12 manually from: https://python.org
    pause
    exit /b 1
)

echo [*] Installing Python 3.12 (this may take a few minutes)...
"%SCRIPTPATH%%PYTHON_INSTALLER%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0 Include_doc=0

echo [*] Waiting for installation to complete...
:wait_install
timeout /t 3 >nul
if exist "%PYTHON_EXE2%" (
    set "PYTHON_EXE=%PYTHON_EXE2%"
    set "PYTHON_DIR=%PYTHON_DIR2%"
    goto install_success
)
if exist "%PYTHON_EXE1%" (
    set "PYTHON_EXE=%PYTHON_EXE1%"
    set "PYTHON_DIR=%PYTHON_DIR1%"
    goto install_success
)
echo [*] Still installing... Please wait...
goto wait_install

:install_success
echo [+] Python installation completed!
del "%SCRIPTPATH%%PYTHON_INSTALLER%" >nul 2>&1

:create_venv
:: === CREATE VIRTUAL ENVIRONMENT ===
echo [*] Creating virtual environment...
"%PYTHON_EXE%" -m venv "%VENV_DIR%"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to create virtual environment!
    echo Make sure Python venv module is available.
    pause
    exit /b 1
)
echo [+] Virtual environment created successfully!

:install_deps
:: === UPGRADE PIP IN VIRTUAL ENVIRONMENT ===
echo [*] Upgrading pip in virtual environment...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet
if !errorlevel! neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

:: === INSTALL REQUIREMENTS ===
if exist "%SCRIPTPATH%%REQUIREMENTS%" (
    echo [*] Installing dependencies from %REQUIREMENTS%...
    "%VENV_PYTHON%" -m pip install -r "%SCRIPTPATH%%REQUIREMENTS%" --quiet
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install some dependencies!
        echo Trying to continue anyway...
    ) else (
        echo [+] All dependencies installed successfully!
    )
) else (
    echo [WARNING] Requirements file not found: %REQUIREMENTS%
)

:: === INSTALL AHK PACKAGE AND AUTOHOTKEY BINARY ===
echo [*] Installing AutoHotkey (AHK) package...
"%VENV_PYTHON%" -m pip install ahk --quiet
if !errorlevel! neq 0 (
    echo [WARNING] Failed to install AHK package, but continuing...
) else (
    echo [+] AHK package installed successfully!
)

echo [*] Installing AutoHotkey binary via Chocolatey (if available)...
choco install autohotkey -y >nul 2>&1
if !errorlevel! equ 0 (
    echo [+] AutoHotkey binary installed via Chocolatey!
) else (
    echo [*] Chocolatey not found. Trying direct download...
    echo [*] Downloading AutoHotkey installer...
    curl -L --progress-bar -o "%SCRIPTPATH%AutoHotkey_1.1.37.01_setup.exe" "https://www.autohotkey.com/download/1.1/AutoHotkey_1.1.37.01_setup.exe" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [*] Installing AutoHotkey...
        "%SCRIPTPATH%AutoHotkey_1.1.37.01_setup.exe" /S
        timeout /t 5 >nul
        del "%SCRIPTPATH%AutoHotkey_1.1.37.01_setup.exe" >nul 2>&1
        echo [+] AutoHotkey binary installed!
    ) else (
        echo [WARNING] Could not install AutoHotkey binary automatically.
        echo Please install AutoHotkey manually from: https://www.autohotkey.com/
    )
)

:: === VERIFY SCRIPT EXISTS ===
if not exist "%SCRIPTPATH%%SCRIPT%" (
    echo [ERROR] Script not found: %SCRIPT%
    echo Make sure %SCRIPT% is in the same folder as this batch file.
    pause
    exit /b 1
)

:: === RUN THE SCRIPT ===
echo.
echo ======================================================
echo [*] LAUNCHING AUTO PLAYTIME SCRIPT...
echo ======================================================
echo [*] Script location: %SCRIPTPATH%%SCRIPT%
echo [*] Python executable: %VENV_PYTHON%
echo [*] Virtual environment: %VENV_DIR%
echo ======================================================
echo.

:: Run in the same window to see output and allow interaction
"%VENV_PYTHON%" "%SCRIPTPATH%%SCRIPT%"

:: === SCRIPT FINISHED ===
echo.
echo ======================================================
echo [*] SCRIPT FINISHED
echo ======================================================
set /p dummy="Press ENTER to close this window..."
