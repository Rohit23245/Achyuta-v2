@echo off
title Achyuta 2.0 Web Server
cd /d "%~dp0"
echo ====================================================
echo   Achyuta 2.0 Web Server Starting...
echo   Open in browser: http://localhost:5000
echo ====================================================
start "" http://localhost:5000
python server.py
pause
