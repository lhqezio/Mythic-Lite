#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Mythic-Lite AI Chatbot Interactive Launcher
.DESCRIPTION
    Interactive launcher for Mythic-Lite with menu options for different modes
    and features including debug mode, voice/text mode, and system management.
#>

# Set console title and colors
$Host.UI.RawUI.WindowTitle = "Mythic-Lite AI Chatbot Interactive Launcher"
$Host.UI.RawUI.ForegroundColor = "Green"

function Show-MainMenu {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "    MYTHIC-LITE AI CHATBOT INTERACTIVE LAUNCHER" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Choose an option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[1] Voice Mode (ASR + TTS)" -ForegroundColor White
    Write-Host "[2] Text Chat Mode" -ForegroundColor White
    Write-Host "[3] Initialize System Only" -ForegroundColor White
    Write-Host "[4] Show System Status" -ForegroundColor White
    Write-Host "[5] Test TTS System" -ForegroundColor White
    Write-Host "[6] Debug Mode (Verbose Output)" -ForegroundColor White
    Write-Host "[7] Help & Commands" -ForegroundColor White
    Write-Host "[8] Exit" -ForegroundColor White
    Write-Host ""
}

function Show-VoiceMode {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           LAUNCHING VOICE MODE" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Starting Mythic-Lite in voice conversation mode..." -ForegroundColor Yellow
    Write-Host "This will enable both speech recognition and text-to-speech." -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop when ready." -ForegroundColor Yellow
    Write-Host ""
}

function Show-TextMode {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           LAUNCHING TEXT MODE" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Starting Mythic-Lite in text chat mode..." -ForegroundColor Yellow
    Write-Host "This will run without voice features for better compatibility." -ForegroundColor White
    Write-Host ""
    Write-Host "Type 'quit' to exit when ready." -ForegroundColor Yellow
    Write-Host ""
}

function Show-InitOnly {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           SYSTEM INITIALIZATION" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Initializing Mythic system components..." -ForegroundColor Yellow
    Write-Host "This will load models and prepare the system." -ForegroundColor White
    Write-Host ""
}

function Show-Status {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           SYSTEM STATUS" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Checking system status..." -ForegroundColor Yellow
    Write-Host ""
}

function Show-TestTTS {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           TTS SYSTEM TEST" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Testing text-to-speech system..." -ForegroundColor Yellow
    Write-Host "This will verify audio output is working." -ForegroundColor White
    Write-Host ""
}

function Show-DebugMode {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           DEBUG MODE" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Starting Mythic-Lite in debug mode..." -ForegroundColor Yellow
    Write-Host "This will show detailed logging and system information." -ForegroundColor White
    Write-Host ""
}

function Show-Help {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           HELP & COMMANDS" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available Commands:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Voice Mode Commands:" -ForegroundColor White
    Write-Host "- Just start speaking to interact" -ForegroundColor Gray
    Write-Host "- Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host "- Say 'debug' for troubleshooting menu" -ForegroundColor Gray
    Write-Host "- Say 'status' for system information" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Text Mode Commands:" -ForegroundColor White
    Write-Host "- Type your messages and press Enter" -ForegroundColor Gray
    Write-Host "- Type 'quit' or 'exit' to exit" -ForegroundColor Gray
    Write-Host "- Type 'debug' for troubleshooting menu" -ForegroundColor Gray
    Write-Host "- Type 'status' for system information" -ForegroundColor Gray
    Write-Host "- Type 'help' for this help" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Debug Menu Options:" -ForegroundColor White
    Write-Host "- Test TTS system" -ForegroundColor Gray
    Write-Host "- Test ASR system" -ForegroundColor Gray
    Write-Host "- Show system status" -ForegroundColor Gray
    Write-Host "- Show configuration" -ForegroundColor Gray
    Write-Host "- Performance metrics" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press any key to return to main menu..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Show-Goodbye {
    Clear-Host
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "           GOODBYE!" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Thank you for using Mythic-Lite!" -ForegroundColor Yellow
    Write-Host ""
}

function Setup-Environment {
    Write-Host "Setting up environment..." -ForegroundColor Yellow
    Write-Host ""

    # Get the directory where this script is located
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir

    # Navigate to the project root (one level up from scripts)
    Set-Location ..

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python found" -ForegroundColor Green
            Write-Host $pythonVersion -ForegroundColor White
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "Python not found. Please install Python 3.8+" -ForegroundColor Red
        Read-Host "Press Enter to return to main menu"
        return $false
    }

    # Create venv if needed
    if (-not (Test-Path "venv")) {
        Write-Host ""
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to create venv" -ForegroundColor Red
            Read-Host "Press Enter to return to main menu"
            return $false
        }
        Write-Host "Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "Virtual environment found" -ForegroundColor Green
    }

    # Activate venv
    Write-Host ""
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to activate venv" -ForegroundColor Red
        Read-Host "Press Enter to return to main menu"
        return $false
    }
    Write-Host "Virtual environment activated" -ForegroundColor Green

    # Install requirements
    Write-Host ""
    Write-Host "Checking dependencies..." -ForegroundColor Yellow
    try {
        python -c "import llama_cpp, piper_tts, rich, click" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Dependencies not found"
        }
        Write-Host "Dependencies found" -ForegroundColor Green
    } catch {
        Write-Host ""
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to install dependencies" -ForegroundColor Red
            Read-Host "Press Enter to return to main menu"
            return $false
        }
        Write-Host "Dependencies installed" -ForegroundColor Green
    }

    # Install windows-curses
    Write-Host ""
    Write-Host "Installing Windows dependencies..." -ForegroundColor Yellow
    pip install windows-curses
    Write-Host "Windows dependencies installed" -ForegroundColor Green

    Write-Host ""
    Write-Host "Environment setup complete!" -ForegroundColor Green
    Write-Host ""
    return $true
}

function Launch-Mythic {
    param(
        [string]$Mode,
        [string]$Command
    )

    Write-Host "Launching Mythic-Lite in $Mode..." -ForegroundColor Yellow
    Write-Host ""

    # Try the new package structure first, fallback to simple script
    try {
        if ($Command -eq "debug") {
            python -m mythic_lite.utils.cli --debug
        } else {
            python -m mythic_lite.utils.cli $Command
        }
    } catch {
        Write-Host "Package import failed, trying alternative method..." -ForegroundColor Yellow
        Write-Host ""
        try {
            if ($Command -eq "debug") {
                python run_mythic.py --debug
            } else {
                python run_mythic.py $Command
            }
        } catch {
            Write-Host "Failed to launch Mythic-Lite" -ForegroundColor Red
            Write-Host ""
            Write-Host "Troubleshooting:" -ForegroundColor Yellow
            Write-Host "1. Make sure Python is installed and in PATH" -ForegroundColor White
            Write-Host "2. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
            Write-Host "3. Check that all files are present" -ForegroundColor White
            Write-Host ""
        }
    }
}

# Main loop
do {
    Show-MainMenu
    $choice = Read-Host "Enter your choice (1-8)"

    switch ($choice) {
        "1" {
            Show-VoiceMode
            if (Setup-Environment) {
                Launch-Mythic "voice mode" "voice"
            }
        }
        "2" {
            Show-TextMode
            if (Setup-Environment) {
                Launch-Mythic "text mode" "chat"
            }
        }
        "3" {
            Show-InitOnly
            if (Setup-Environment) {
                Launch-Mythic "initialization mode" "init"
            }
        }
        "4" {
            Show-Status
            if (Setup-Environment) {
                Launch-Mythic "status mode" "status"
            }
        }
        "5" {
            Show-TestTTS
            if (Setup-Environment) {
                Launch-Mythic "TTS test mode" "test-tts"
            }
        }
                 "6" {
             Show-DebugMode
             if (Setup-Environment) {
                 Launch-Mythic "debug mode" "debug"
                 if ($LASTEXITCODE -ne 0) {
                     Write-Host ""
                     Write-Host "Trying alternative debug launch methods..." -ForegroundColor Yellow
                     Write-Host ""
                     Write-Host "Method 1: Direct debug launch..." -ForegroundColor Cyan
                     try {
                         python -c "from mythic_lite.utils.cli import cli; cli(['--debug'])"
                     } catch {
                         Write-Host "Method 1 failed, trying Method 2..." -ForegroundColor Yellow
                         python run_mythic.py --debug
                     }
                 }
             }
         }
        "7" {
            Show-Help
            continue
        }
        "8" {
            Show-Goodbye
            break
        }
        default {
            Write-Host ""
            Write-Host "Invalid choice. Please enter a number between 1 and 8." -ForegroundColor Red
            Write-Host ""
            Read-Host "Press Enter to continue"
            continue
        }
    }

    Write-Host ""
    Write-Host "Mythic-Lite has exited." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to return to main menu..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

} while ($true)

Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
