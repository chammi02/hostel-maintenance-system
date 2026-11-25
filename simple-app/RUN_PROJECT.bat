@echo off
title Hostel Maintenance Management System
echo ====================================================================
echo Starting Hostel Maintenance Request Management System
echo ====================================================================
echo.
echo Database: Connecting to XAMPP MySQL (hostel_db)
echo (Note: If MySQL is not running, it automatically uses local SQLite)
echo.
cd /d "%~dp0"

IF EXIST "C:\Program Files\QGIS 3.44.11\apps\Python312\python.exe" (
    "C:\Program Files\QGIS 3.44.11\apps\Python312\python.exe" app.py
) ELSE (
    python app.py
)

pause
