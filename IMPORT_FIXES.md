# Import Fixes and Directory Structure Changes

## 🔧 Issues Fixed

### 1. Import Path Problems

**Problem**: After restructuring the repository, the import statements in the moved files were still using relative imports that assumed the old directory structure.

**Solution**: Updated all import statements to use the correct relative paths:

#### Core Module Imports
```python
# Before (incorrect)
from .llm_worker import LLMWorker
from .logger import get_logger

# After (correct)
from ..workers.llm_worker import LLMWorker
from ..utils.logger import get_logger
```

#### Worker Module Imports
```python
# Before (incorrect)
from .config import get_config
from .model_manager import ensure_model

# After (correct)
from ..core.config import get_config
from ..core.model_manager import ensure_model
```

#### Utility Module Imports
```python
# Before (incorrect)
from .chatbot_orchestrator import ChatbotOrchestrator
from .config import get_config

# After (correct)
from ..core.chatbot_orchestrator import ChatbotOrchestrator
from ..core.config import get_config
```

#### Script Module Imports
```python
# Before (incorrect)
from src.model_manager import get_model_manager
from src.logger import get_logger

# After (correct)
from mythic_lite.core.model_manager import get_model_manager
from mythic_lite.utils.logger import get_logger
```

### 2. Batch Script Directory Issues

**Problem**: The Windows batch script was trying to run `python mythic.py` which no longer existed, and wasn't accounting for the new directory structure.

**Solution**: Updated the script to:
- Navigate to the correct project root directory
- Use the new package structure: `python -m mythic_lite.utils.cli`
- Include fallback to a simple entry point script

#### Batch Script Changes
```batch
REM Before (incorrect)
cd /d "%~dp0"
python mythic.py

REM After (correct)
cd /d "%~dp0"
cd ..
python -m mythic_lite.utils.cli
if errorlevel 1 (
    python run_mythic.py
)
```

### 3. PowerShell Script Directory Issues

**Problem**: Similar to the batch script, the PowerShell script had directory and entry point issues.

**Solution**: Updated to match the batch script fixes and include fallback options.

### 4. Linux Install Script Updates

**Problem**: The Linux install script needed to create startup scripts that worked with the new structure.

**Solution**: Updated the startup script generation to use the new package structure with fallbacks.

## 📁 New Directory Structure

```
mythic-lite/
├── src/mythic_lite/          # Main package
│   ├── core/                 # Core components
│   │   ├── __init__.py
│   │   ├── chatbot_orchestrator.py
│   │   ├── conversation_worker.py
│   │   ├── model_manager.py
│   │   └── config.py
│   ├── workers/              # AI workers
│   │   ├── __init__.py
│   │   ├── asr_worker.py
│   │   ├── llm_worker.py
│   │   ├── summarization_worker.py
│   │   └── tts_worker.py
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── logger.py
│   │   └── windows_input.py
│   └── scripts/              # Setup scripts
│       ├── __init__.py
│       ├── download_vosk_manual.py
│       ├── initialize_models.py
│       └── setup_environment.py
├── scripts/                  # Installation scripts
│   ├── start_mythic.bat     # Windows batch
│   ├── start_mythic.ps1     # Windows PowerShell
│   └── install.sh           # Linux/macOS
├── run_mythic.py            # Simple entry point
└── test_imports.py          # Import test script
```

## 🚀 How to Use

### Windows Users
1. **Double-click** `scripts/start_mythic.bat` (easiest)
2. **Or run** `scripts/start_mythic.ps1` with PowerShell

### Linux/macOS Users
1. **Run** `./scripts/install.sh` for automated setup
2. **Or manually** run `python run_mythic.py`

### Developers
1. **Test imports**: `python test_imports.py`
2. **Start directly**: `python -m mythic_lite.utils.cli`
3. **Use entry point**: `python run_mythic.py`

## ✅ Verification

To verify the fixes work:

1. **Test imports**:
   ```bash
   python test_imports.py
   ```

2. **Test package structure**:
   ```bash
   python -m mythic_lite.utils.cli --help
   ```

3. **Test simple entry point**:
   ```bash
   python run_mythic.py --help
   ```

## 🔄 Fallback Strategy

The scripts now use a two-tier approach:

1. **Primary**: Use the new package structure (`python -m mythic_lite.utils.cli`)
2. **Fallback**: Use the simple entry point script (`python run_mythic.py`)

This ensures compatibility even if there are issues with the package structure.

## 📝 Notes

- All import paths have been updated to reflect the new structure
- Scripts now navigate to the correct directories
- Fallback options are provided for robustness
- The structure maintains backward compatibility where possible
- Development tools (Makefile, pre-commit, etc.) are configured for the new structure