@echo off
:: ───────────────────────────────────────────────────────────────────────────
::  Thorlabs TDC001 – GUI launcher (NO auto-start)
:: ───────────────────────────────────────────────────────────────────────────
::  • Loads image from tdc001-gui.tar if needed
::  • Starts / restarts container  tdc001-gui
::  • Waits until noVNC is reachable, then opens browser
::  • Optionally creates a Desktop shortcut to this script
:: ───────────────────────────────────────────────────────────────────────────

setlocal EnableDelayedExpansion

:: --- edit here if you used different tags / ports -------------------------
set IMAGE_TAG=tdc001-gui:1.0
set TAR_FILE=%~dp0tdc001-gui.tar
set CONTAINER=tdc001-gui
set PORT=6080
:: optional: if backend is on another host, uncomment the next line
:: set BACKEND_URL=http://192.168.65.3:8000
:: --------------------------------------------------------------------------

echo.
echo ========================================================================
echo  T D C 0 0 1   –   G U I   L A U N C H E R
echo ========================================================================
echo.

:: 1 ── import image if missing ---------------------------------------------
docker image inspect %IMAGE_TAG% >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Image %IMAGE_TAG% not found – loading %TAR_FILE% …
    if not exist "%TAR_FILE%" (
        echo [ERROR] %TAR_FILE% missing – aborting.
        pause
        exit /b 1
    )
    docker load -i "%TAR_FILE%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to load image.
        pause
        exit /b 1
    )
)

:: 2 ── start / restart container -------------------------------------------
docker ps --filter "name=%CONTAINER%" --format "{{.Names}}" | findstr /I %CONTAINER% >nul
if %errorlevel%==0 (
    echo [INFO] Container is already running.
) else (
    docker rm %CONTAINER% >nul 2>&1
    echo [INFO] Starting container %CONTAINER% …
    docker run -d --name %CONTAINER% ^
        --restart unless-stopped ^
        -p %PORT%:6080 ^
        -e BACKEND_URL=%BACKEND_URL% ^
        %IMAGE_TAG%
    if %errorlevel% neq 0 (
        echo [ERROR] Docker failed to start the container.
        pause
        exit /b 1
    )
)

:: 3 ── wait for noVNC -------------------------------------------------------
echo [INFO] Waiting for http://localhost:%PORT% …
for /l %%i in (1,1,30) do (
    curl -fs http://localhost:%PORT% >nul 2>&1 && goto :OPEN_BROWSER
    timeout /t 1 >nul
)
echo [WARN] Timed-out waiting for noVNC, but will open the page anyway.

:OPEN_BROWSER
start "" "http://localhost:%PORT%"

:: 4 ── offer desktop shortcut ----------------------------------------------
echo.
choice /M "Do you want a Desktop shortcut for next time"
if errorlevel 2 goto :EOF  :: user chose 'N'

set DESKTOP=%USERPROFILE%\Desktop
set LINK=%DESKTOP%\TDC001-GUI.lnk

if exist "%LINK%" (
    echo [INFO] Shortcut already exists: %LINK%
    goto :EOF
)

echo [INFO] Creating shortcut …
powershell -NoLogo -NoProfile -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LINK%');" ^
  "$s.TargetPath='%~f0';$s.WorkingDirectory='%~dp0';$s.WindowStyle=1;$s.Save()"

echo [INFO] Shortcut created on Desktop.
goto :EOF
