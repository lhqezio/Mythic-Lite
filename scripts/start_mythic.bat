@echo off
title Mythic-Lite AI Chatbot Interactive Launcher
color 0A

:MAIN_MENU
cls
echo.
echo ================================================
echo    MYTHIC-LITE AI CHATBOT INTERACTIVE LAUNCHER
echo ================================================
echo.
echo Choose an option:
echo.
echo [1] Voice Mode (ASR + TTS)
echo [2] Text Chat Mode
echo [3] Initialize System Only
echo [4] Show System Status
echo [5] Test TTS System
echo [6] Debug Mode (Verbose Output)
echo [7] Help & Commands
echo [8] Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto VOICE_MODE
if "%choice%"=="2" goto TEXT_MODE
if "%choice%"=="3" goto INIT_ONLY
if "%choice%"=="4" goto SHOW_STATUS
if "%choice%"=="5" goto TEST_TTS
if "%choice%"=="6" goto DEBUG_MODE
if "%choice%"=="7" goto SHOW_HELP
if "%choice%"=="8" goto EXIT
goto INVALID_CHOICE

:VOICE_MODE
cls
echo.
echo ================================================
echo           LAUNCHING VOICE MODE
echo ================================================
echo.
echo Starting Mythic-Lite in voice conversation mode...
echo This will enable both speech recognition and text-to-speech.
echo.
echo Press Ctrl+C to stop when ready.
echo.
goto SETUP_AND_LAUNCH

:TEXT_MODE
cls
echo.
echo ================================================
echo           LAUNCHING TEXT MODE
echo ================================================
echo.
echo Starting Mythic-Lite in text chat mode...
echo This will run without voice features for better compatibility.
echo.
echo Type 'quit' to exit when ready.
echo.
goto SETUP_AND_LAUNCH

:INIT_ONLY
cls
echo.
echo ================================================
echo           SYSTEM INITIALIZATION
echo ================================================
echo.
echo Initializing Mythic system components...
echo This will load models and prepare the system.
echo.
goto SETUP_AND_LAUNCH

:SHOW_STATUS
cls
echo.
echo ================================================
echo           SYSTEM STATUS
echo ================================================
echo.
echo Checking system status...
echo.
goto SETUP_AND_LAUNCH

:TEST_TTS
cls
echo.
echo ================================================
echo           TTS SYSTEM TEST
echo ================================================
echo.
echo Testing text-to-speech system...
echo This will verify audio output is working.
echo.
goto SETUP_AND_LAUNCH

:DEBUG_MODE
cls
echo.
echo ================================================
echo           DEBUG MODE
echo ================================================
echo.
echo Starting Mythic-Lite in debug mode...
echo This will show detailed logging and system information.
echo.
goto SETUP_AND_LAUNCH

:SHOW_HELP
cls
echo.
echo ================================================
echo           HELP & COMMANDS
echo ================================================
echo.
echo Available Commands:
echo.
echo Voice Mode Commands:
echo - Just start speaking to interact
echo - Press Ctrl+C to stop
echo - Say 'debug' for troubleshooting menu
echo - Say 'status' for system information
echo.
echo Text Mode Commands:
echo - Type your messages and press Enter
echo - Type 'quit' or 'exit' to exit
echo - Type 'debug' for troubleshooting menu
echo - Type 'status' for system information
echo - Type 'help' for this help
echo.
echo Debug Menu Options:
echo - Test TTS system
echo - Test ASR system
echo - Show system status
echo - Show configuration
echo - Performance metrics
echo.
echo Press any key to return to main menu...
pause >nul
goto MAIN_MENU

:INVALID_CHOICE
echo.
echo Invalid choice. Please enter a number between 1 and 8.
echo.
pause
goto MAIN_MENU

:SETUP_AND_LAUNCH
echo Setting up environment...
echo.

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Navigate to the project root (one level up from scripts)
cd ..

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+
    pause
    goto MAIN_MENU
)

echo Python found
python --version

REM Create venv if needed
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create venv
        pause
        goto MAIN_MENU
    )
    echo Virtual environment created
) else (
    echo Virtual environment found
)

REM Activate venv
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate venv
    pause
    goto MAIN_MENU
)
echo Virtual environment activated

REM Install requirements
echo.
echo Checking dependencies...
python -c "import llama_cpp, piper_tts, rich, click" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        goto MAIN_MENU
    )
    echo Dependencies installed
) else (
    echo Dependencies found
)

REM Install windows-curses
echo.
echo Installing Windows dependencies...
pip install windows-curses
echo Windows dependencies installed

echo.
echo Environment setup complete!
echo.

REM Launch based on choice
if "%choice%"=="1" (
    echo Launching Mythic-Lite in voice mode...
    echo.
    python -m mythic_lite.utils.cli voice
    if errorlevel 1 (
        echo Package import failed, trying alternative method...
        python run_mythic.py voice
    )
) else if "%choice%"=="2" (
    echo Launching Mythic-Lite in text mode...
    echo.
    python -m mythic_lite.utils.cli chat
    if errorlevel 1 (
        echo Package import failed, trying alternative method...
        python run_mythic.py chat
    )
) else if "%choice%"=="3" (
    echo Initializing Mythic system...
    echo.
    python -m mythic_lite.utils.cli init
    if errorlevel 1 (
        echo Package import failed, trying alternative method...
        python run_mythic.py init
    )
) else if "%choice%"=="4" (
    echo Checking system status...
    echo.
    python -m mythic_lite.utils.cli status
    if errorlevel 1 (
        echo Package import failed, trying alternative method...
        python run_mythic.py status
    )
) else if "%choice%"=="5" (
    echo Testing TTS system...
    echo.
    python -m mythic_lite.utils.cli test-tts
    if errorlevel 1 (
        echo Package import failed, trying alternative method...
        python run_mythic.py test-tts
    )
        ) else if "%choice%"=="6" (
            echo Launching Mythic-Lite in debug mode...
            echo.
            python -m mythic_lite.utils.cli --debug
            if errorlevel 1 (
                echo Package import failed, trying alternative method...
                echo.
                echo Trying alternative debug launch methods...
                echo.
                echo Method 1: Direct debug launch...
                python -c "from mythic_lite.utils.cli import cli; cli(['--debug'])"
                if errorlevel 1 (
                    echo Method 1 failed, trying Method 2...
                    python run_mythic.py --debug
                )
            )
        )

echo.
echo Mythic-Lite has exited.
echo.
echo Press any key to return to main menu...
pause >nul
goto MAIN_MENU

:EXIT
cls
echo.
echo ================================================
echo           GOODBYE!
echo ================================================
echo.
echo Thank you for using Mythic-Lite!
echo.
echo Press any key to exit...
pause >nul
exit /b 0
