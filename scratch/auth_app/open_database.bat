@echo off
title SQLite Database Viewer
cd /d "%~dp0"
echo Reading users.db and opening in your browser...
py open_database.py
if errorlevel 1 (
    python open_database.py
)
pause
