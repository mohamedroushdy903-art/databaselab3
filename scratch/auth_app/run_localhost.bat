@echo off
title AuthGuard Localhost Server - Keep This Window Open!
echo ===================================================================
echo  Alexandria National University (ANU) - Database Systems Portal
echo  Starting Flask Server on http://127.0.0.1:5000 ...
echo ===================================================================
echo.
cd /d "%~dp0"

:: Open the browser after 2 seconds to give Flask enough time to start
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

echo [1/2] Attempting to launch with 'py' launcher...
py app.py
if errorlevel 1 (
    echo.
    echo [2/2] 'py' encountered an issue. Attempting with 'python'...
    python app.py
)

echo.
echo ===================================================================
echo  Server stopped. Keep this window open while using the app!
echo ===================================================================
pause
