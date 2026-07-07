@echo off
REM Operations Co-Founder Brain — Dashboard Launcher
REM Run this to start the dashboard

echo.
echo ============================================================
echo   Operations Co-Founder Brain
echo   Starting dashboard...
echo ============================================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please run INSTALL.bat first to set up the application.
    echo.
    pause
    exit /b 1
)

REM Check if ANTHROPIC_API_KEY is set
for /f "tokens=2 delims==" %%a in ('findstr /I "ANTHROPIC_API_KEY" .env') do set API_KEY=%%a

if "%API_KEY%"=="" (
    echo ERROR: ANTHROPIC_API_KEY not configured in .env
    echo.
    echo Please edit .env and add your API key.
    echo Get it from: https://console.anthropic.com/
    echo.
    pause
    exit /b 1
)

echo Launching Streamlit dashboard...
echo.
echo The app will open in your browser at: http://localhost:8501
echo.
echo To stop the app, press CTRL+C in this window
echo.

REM Start the dashboard
streamlit run dashboard.py

pause
