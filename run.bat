::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAnk
::fBw5plQjdG8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCiDJHqL8EcMGAJARAuMAEqvEros5Oni++OKp38SVu4wYL3SzLWCM9wy/1HrRZosz25Tlc4+BQ1ZcgGXRwEnvW9OukWLM/WJvUHkUk3p
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal enabledelayedexpansion

:: === CONFIGURATION ===
set "SCRIPT=AutoPlaytime.py"
set "REQUIREMENTS=requirements.txt"
set "PYTHON_INSTALLER=python-3.12.1-amd64.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/%PYTHON_INSTALLER%"

:: === SCRIPT PATH ===
set "SCRIPTPATH=%~dp0"

:: === PYTHON PATHS ===
set "PYTHON_DIR1=%ProgramFiles%\Python312"
set "PYTHON_EXE1=%PYTHON_DIR1%\python.exe"
set "PYTHON_DIR2=%LocalAppData%\Programs\Python\Python312"
set "PYTHON_EXE2=%PYTHON_DIR2%\python.exe"

:: === CHECK IF PYTHON 3.12 IS INSTALLED ===
if exist "%PYTHON_EXE1%" goto found1
if exist "%PYTHON_EXE2%" goto found2

echo [*] Python 3.12 not found. Downloading installer...
curl -L -o "%SCRIPTPATH%%PYTHON_INSTALLER%" "%PYTHON_URL%"
echo [*] Running Python installer (per-user, no admin needed)...
"%SCRIPTPATH%%PYTHON_INSTALLER%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0
echo [*] Waiting for installation to finish...

:waitpython
timeout /t 2 >nul
if exist "%PYTHON_EXE2%" goto found2
if exist "%PYTHON_EXE1%" goto found1
echo [!] Python installation failed. Please install Python 3.12 manually.
pause
exit /b 1

:found1
set "PYTHON_EXE=%PYTHON_EXE1%"
set "PYTHON_DIR=%PYTHON_DIR1%"
echo [*] Python 3.12 found at %PYTHON_EXE%
goto afterpython

:found2
set "PYTHON_EXE=%PYTHON_EXE2%"
set "PYTHON_DIR=%PYTHON_DIR2%"
echo [*] Python 3.12 found at %PYTHON_EXE%
goto afterpython

:afterpython
:: === ADD PYTHON TO PATH FOR CURRENT SESSION ===
set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"
echo [*] PATH updated for this session: %PYTHON_DIR%;%PYTHON_DIR%\Scripts%

:: === INSTALL DEPENDENCIES ===
echo [*] Installing requirements...
"%PYTHON_EXE%" -m pip install --upgrade pip || pause
if exist "%SCRIPTPATH%%REQUIREMENTS%" (
    "%PYTHON_EXE%" -m pip install --quiet -r "%SCRIPTPATH%%REQUIREMENTS%" || pause
)

:: === RUN SCRIPT IN NEW CONSOLE WINDOW ===
echo Running: "%PYTHON_EXE%" "%SCRIPTPATH%%SCRIPT%"
start "" cmd /k ""%PYTHON_EXE%" "%SCRIPTPATH%%SCRIPT%" & echo. & echo Press any key to exit... & pause >nul"
