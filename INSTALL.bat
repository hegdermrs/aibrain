@echo off
REM Operations Co-Founder Brain — One-Click Installer
REM Run this once to set up everything

echo.
echo ============================================================
echo   Operations Co-Founder Brain — Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python found. Installing dependencies...
echo.

REM Install requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Dependencies installed successfully!
echo.

REM Check if .env exists
if not exist .env (
    echo [3/4] Creating .env file...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY
    echo.
    echo   1. Open .env in Notepad
    echo   2. Replace sk-ant-xxxxx with your actual API key
    echo   3. Save the file
    echo.
    echo Get your API key from: https://console.anthropic.com/
    echo.
    pause
) else (
    echo [3/4] .env file already exists (skipping creation)
)

echo.
echo [4/4] Setup complete!
echo.
echo ============================================================
echo   Ready to run!
echo.
echo   Next step: Run "START_DASHBOARD.bat" to launch the app
echo.
echo   The dashboard will open in your browser at:
echo   http://localhost:8501
echo.
echo ============================================================
echo.
pause
