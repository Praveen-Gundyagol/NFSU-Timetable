@echo off
echo ========================================================
echo Starting NFSU Timetable Generator - FastAPI Backend
echo ========================================================
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
