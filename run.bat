:: Operations Co-Founder Dashboard
:: Double-click this file to start (or run from terminal)
@echo off
cd /d "%~dp0"
echo.
echo   Brain Dashboard starting...
echo   Open http://localhost:8501 in your browser
echo.
call streamlit run dashboard.py
pause
