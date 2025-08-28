# Mythic-Lite Interactive Launcher Scripts

This directory contains interactive launcher scripts for Mythic-Lite that provide a user-friendly menu system for launching different modes and features.

## Available Scripts

### Windows
- **`start_mythic.bat`** - Windows Batch file launcher
- **`start_mythic.ps1`** - PowerShell script launcher

### Unix/Linux/macOS
- **`start_mythic.sh`** - Bash shell script launcher

## Features

All launcher scripts provide the same interactive menu with the following options:

### 🎤 [1] Voice Mode (ASR + TTS)
- Launches Mythic-Lite in full voice conversation mode
- Enables both speech recognition (ASR) and text-to-speech (TTS)
- Best for hands-free voice interactions
- Press Ctrl+C to stop

### 💬 [2] Text Chat Mode
- Launches Mythic-Lite in text-only chat mode
- Runs without voice features for better compatibility
- Type your messages and press Enter
- Type 'quit' or 'exit' to exit

### 🔧 [3] Initialize System Only
- Initializes Mythic system components without launching chat
- Loads models and prepares the system
- Useful for testing system setup

### 📊 [4] Show System Status
- Displays current system status and model information
- Shows which components are loaded and working
- Helpful for troubleshooting

### 🔊 [5] Test TTS System
- Tests the text-to-speech system
- Verifies audio output is working correctly
- Plays a test audio sample

### 🐛 [6] Debug Mode (Verbose Output)
- Launches Mythic-Lite with detailed debug logging
- Shows comprehensive system information
- Enables verbose logging and detailed error reporting
- Best for troubleshooting and development
- Can be combined with any command (e.g., `mythic voice --debug`)

### ❓ [7] Help & Commands
- Displays help information and available commands
- Shows voice and text mode commands
- Lists debug menu options

### 🚪 [8] Exit
- Exits the launcher and returns to command prompt

## Usage

### Windows Users

#### Option 1: Double-click the batch file
1. Navigate to the `scripts` folder
2. Double-click `start_mythic.bat`
3. Choose your option from the menu

#### Option 2: Run from Command Prompt
```cmd
cd scripts
start_mythic.bat
```

#### Option 3: PowerShell (Recommended)
```powershell
cd scripts
.\start_mythic.ps1
```

### Unix/Linux/macOS Users

#### Option 1: Make executable and run
```bash
cd scripts
chmod +x start_mythic.sh
./start_mythic.sh
```

#### Option 2: Run with bash directly
```bash
cd scripts
bash start_mythic.sh
```

## Environment Setup

All launcher scripts automatically:

1. **Check Python Installation** - Verifies Python 3.8+ is available
2. **Create Virtual Environment** - Sets up `venv` if it doesn't exist
3. **Activate Environment** - Activates the virtual environment
4. **Install Dependencies** - Installs required packages from `requirements.txt`
5. **Install Platform Dependencies** - Adds Windows-specific packages on Windows

## Troubleshooting

### Common Issues

#### Python Not Found
- Ensure Python 3.8+ is installed and in your system PATH
- Try running `python --version` or `python3 --version` in terminal

#### Virtual Environment Issues
- Delete the `venv` folder and let the script recreate it
- Ensure you have the `venv` module available

#### Dependency Installation Fails
- Check your internet connection
- Try running `pip install -r requirements.txt` manually
- Ensure you have sufficient disk space

#### Permission Issues (Unix/Linux)
- Make the script executable: `chmod +x start_mythic.sh`
- Run with appropriate permissions

### Getting Help

If you encounter issues:

1. **Check the Help Menu** - Option 7 provides command information
2. **Use Debug Mode** - Option 6 shows detailed system information
3. **Check System Status** - Option 4 shows component status
4. **Review Logs** - Check the `src/mythic_lite/logs` directory

## Advanced Usage

### Command Line Arguments

You can also run Mythic-Lite directly without the menu:

```bash
# Voice mode
python -m mythic_lite.utils.cli voice

# Text mode
python -m mythic_lite.utils.cli chat

# Debug mode (global)
python -m mythic_lite.utils.cli --debug

# Debug mode with specific commands
python -m mythic_lite.utils.cli voice --debug
python -m mythic_lite.utils.cli chat --debug
python -m mythic_lite.utils.cli init --debug
python -m mythic_lite.utils.cli status --debug
python -m mythic_lite.utils.cli test-tts --debug

# System status
python -m mythic_lite.utils.cli status

# Initialize only
python -m mythic_lite.utils.cli init

# Test TTS
python -m mythic_lite.utils.cli test-tts
```

### Environment Variables

Set these environment variables before running for custom configuration:

```bash
export MYTHIC_DEBUG=1          # Enable debug mode
export MYTHIC_LOG_LEVEL=DEBUG  # Set log level
export MYTHIC_CONFIG_PATH=path # Custom config file path
```

## Script Customization

The launcher scripts can be customized by editing the script files:

- **Batch file**: Edit `start_mythic.bat` to modify Windows behavior
- **PowerShell**: Edit `start_mythic.ps1` to modify PowerShell behavior  
- **Shell script**: Edit `start_mythic.sh` to modify Unix/Linux behavior

Common customizations:
- Change default Python command
- Add custom environment variables
- Modify dependency installation
- Add custom launch options

## Support

For issues with the launcher scripts:

1. Check this README for troubleshooting steps
2. Review the main project documentation
3. Check the project issues page
4. Ensure you're using the latest version

## Version History

- **v1.0.0** - Initial release with basic launcher functionality
- **v1.1.0** - Added interactive menu system
- **v1.2.0** - Added cross-platform support (Windows, Unix/Linux, macOS)
- **v1.3.0** - Enhanced error handling and user experience
