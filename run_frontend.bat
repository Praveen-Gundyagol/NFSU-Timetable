@echo off
echo ========================================================
echo Starting NFSU Timetable Generator - React Frontend (Vite)
echo ========================================================
cd /d "%~dp0frontend"
set PATH=C:\Program Files\nodejs;%PATH%
npm run dev
pause
