@echo off
echo ========================================
echo    Telegram Music Bot - Installation
echo ========================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    python --version
    echo Python is installed ✓
)
echo.

REM Create virtual environment (optional but recommended)
echo [2/5] Setting up virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created ✓
) else (
    echo Virtual environment already exists ✓
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated ✓
echo.

REM Install requirements
echo [4/5] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies!
    pause
    exit /b 1
) else (
    echo Dependencies installed successfully ✓
)
echo.

REM Setup environment file
echo [5/5] Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo Configuration file created ✓
    echo.
    echo IMPORTANT: Please edit .env file and add your BOT_TOKEN!
    echo You can get a bot token from @BotFather on Telegram.
) else (
    echo Configuration file already exists ✓
)
echo.

REM Create directories
if not exist temp mkdir temp
if not exist output mkdir output
echo Directories created ✓
echo.

echo ========================================
echo    Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your BOT_TOKEN
echo 2. Run the bot using: run.bat
echo.
echo For FFmpeg installation (required for format conversion):
echo - Download from: https://ffmpeg.org/download.html
echo - Add to system PATH
echo.

pause