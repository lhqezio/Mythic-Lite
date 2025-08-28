#!/usr/bin/env python3
"""
Environment setup script for Mythic-Lite.
Automatically creates virtual environment and installs dependencies.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python():
    """Check if Python is available."""
    print("🔍 Checking Python installation...")
    try:
        version = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Python found: {version.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Python not found or not working")
        return False


def create_venv():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔧 Creating virtual environment...")
    try:
        venv.create("venv", with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """Get the Python executable from the virtual environment."""
    if os.name == "nt":  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Unix/Linux/macOS
        return Path("venv/bin/python")


def get_venv_pip():
    """Get the pip executable from the virtual environment."""
    if os.name == "nt":  # Windows
        return Path("venv/Scripts/pip.exe")
    else:  # Unix/Linux/macOS
        return Path("venv/bin/pip")


def install_dependencies():
    """Install dependencies in the virtual environment."""
    venv_pip = get_venv_pip()
    
    if not venv_pip.exists():
        print("❌ pip not found in virtual environment")
        return False
    
    print("📦 Installing dependencies...")
    print("   This may take several minutes on first run...")
    
    # Upgrade pip first
    if not run_command(f'"{venv_pip}" install --upgrade pip', "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f'"{venv_pip}" install -r requirements.txt', "Installing requirements"):
        return False
    
    # Install Windows-specific dependencies if on Windows
    if os.name == "nt":
        print("🔧 Installing Windows-specific dependencies...")
        if not run_command(f'"{venv_pip}" install windows-curses', "Installing windows-curses"):
            print("⚠️  Warning: windows-curses installation failed, but continuing...")
    
    return True


def verify_installation():
    """Verify that all dependencies are properly installed."""
    print("🔍 Verifying installation...")
    
    venv_python = get_venv_python()
    if not venv_python.exists():
        print("❌ Python not found in virtual environment")
        return False
    
    # Test importing key packages
    test_imports = [
        "import llama_cpp",
        "import piper_tts", 
        "import rich",
        "import click"
    ]
    
    for import_stmt in test_imports:
        try:
            subprocess.run([str(venv_python), "-c", import_stmt], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"❌ Failed to import required package")
            return False
    
    print("✅ All dependencies verified successfully")
    return True


def main():
    """Main setup function."""
    print("🔥 MYTHIC-LITE Environment Setup")
    print("=" * 50)
    
    # Check Python
    if not check_python():
        print("\n❌ Setup failed: Python not available")
        print("   Please install Python 3.8+ and try again")
        sys.exit(1)
    
    # Create virtual environment
    if not create_venv():
        print("\n❌ Setup failed: Could not create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Setup failed: Installation verification failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nYou can now run Mythic-Lite using:")
    print("   python mythic.py")
    print("   python main.py")
    print("   start_mythic.bat (Windows)")
    print("   start_mythic.ps1 (PowerShell)")


if __name__ == "__main__":
    main()
