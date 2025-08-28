#!/bin/bash

# Mythic-Lite Installation Script for Linux/macOS
# This script automates the installation process for Mythic-Lite

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check if version is 3.8 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_success "Found Python $PYTHON_VERSION"
    else
        print_error "Python version $PYTHON_VERSION is too old. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    check_python_version
    
    # Check available memory
    if command_exists free; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 8 ]; then
            print_warning "Available memory: ${MEMORY_GB}GB (8GB+ recommended)"
        else
            print_success "Available memory: ${MEMORY_GB}GB"
        fi
    fi
    
    # Check available disk space
    if command_exists df; then
        DISK_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
        if [ "$DISK_GB" -lt 8 ]; then
            print_warning "Available disk space: ${DISK_GB}GB (8GB+ recommended)"
        else
            print_success "Available disk space: ${DISK_GB}GB"
        fi
    fi
    
    # Check audio capabilities
    if command_exists pactl; then
        print_success "PulseAudio detected"
    elif command_exists amixer; then
        print_success "ALSA detected"
    else
        print_warning "No audio system detected. Audio features may not work."
    fi
}

# Function to create virtual environment
create_virtual_environment() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
}

# Function to activate virtual environment
activate_virtual_environment() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to setup environment configuration
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ -f ".env.example" ]; then
        if [ ! -f ".env" ]; then
            cp .env.example .env
            print_success "Environment file created from .env.example"
            print_warning "Please edit .env file with your preferred settings"
        else
            print_warning ".env file already exists, skipping"
        fi
    else
        print_warning ".env.example not found, skipping environment setup"
    fi
}

# Function to initialize models
initialize_models() {
    print_status "Initializing models..."
    
    if [ -f "src/mythic_lite/scripts/initialize_models.py" ]; then
        cd src
        $PYTHON_CMD -m mythic_lite.scripts.initialize_models
        cd ..
        print_success "Models initialized"
    else
        print_warning "Model initialization script not found, skipping"
    fi
}

# Function to create startup script
create_startup_script() {
    echo "Creating startup script..."
    
    cat > start_mythic.sh << 'EOF'
#!/bin/bash
# Mythic-Lite AI Chatbot Startup Script
# This script starts the chatbot in voice mode

echo "==============================================="
echo "    MYTHIC-LITE AI CHATBOT STARTUP"
echo "==============================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Start the chatbot using the new package structure, with fallback
echo "Starting Mythic-Lite in voice mode..."
if python -m mythic_lite.utils.cli voice; then
    echo "Chatbot started successfully using package structure"
else
    echo "Package import failed, trying alternative method..."
    if python run_mythic.py voice; then
        echo "Chatbot started successfully using alternative method"
    else
        echo "Failed to start Mythic-Lite"
        exit 1
    fi
fi
EOF

    chmod +x start_mythic.sh
    echo "Startup script created: start_mythic.sh"
    echo "Run './start_mythic.sh' to start the chatbot in voice mode"
}

# Function to display completion message
display_completion() {
    echo
    print_success "Installation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your preferred settings (optional)"
    echo "2. Run: ./start_mythic.sh"
    echo "3. Or run: source venv/bin/activate && python -m mythic_lite.utils.cli"
    echo
    echo "For more information, see the README.md file"
    echo
}

# Main installation function
main() {
    echo "🤖 Mythic-Lite Installation Script"
    echo "=================================="
    echo
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
        print_error "Please run this script from the Mythic-Lite project root directory"
        exit 1
    fi
    
    # Run installation steps
    check_system_requirements
    create_virtual_environment
    activate_virtual_environment
    install_dependencies
    setup_environment
    initialize_models
    create_startup_script
    display_completion
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --skip-models Skip model initialization"
        echo
        echo "This script will:"
        echo "  1. Check system requirements"
        echo "  2. Create a Python virtual environment"
        echo "  3. Install all dependencies"
        echo "  4. Set up environment configuration"
        echo "  5. Initialize AI models (unless --skip-models is used)"
        echo "  6. Create a startup script"
        exit 0
        ;;
    --skip-models)
        SKIP_MODELS=true
        ;;
esac

# Run main installation
main