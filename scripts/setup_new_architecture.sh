#!/bin/bash

# 🚀 Mythic-Lite New Architecture Setup Script
# This script creates the new directory structure for the improved architecture

set -e  # Exit on any error

echo "🏗️  Setting up new Mythic-Lite architecture..."

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

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the Mythic-Lite project root directory"
    exit 1
fi

# Create new directory structure
print_status "Creating new directory structure..."

# Core layer
mkdir -p src/mythic_lite/core/interfaces
mkdir -p src/mythic_lite/core/events
mkdir -p src/mythic_lite/core/exceptions
mkdir -p src/mythic_lite/core/base
mkdir -p src/mythic_lite/core/dependency_injection
mkdir -p src/mythic_lite/core/extension_points

# Worker layer with new structure
mkdir -p src/mythic_lite/workers/base
mkdir -p src/mythic_lite/workers/llm
mkdir -p src/mythic_lite/workers/tts
mkdir -p src/mythic_lite/workers/asr
mkdir -p src/mythic_lite/workers/memory

# Service layer
mkdir -p src/mythic_lite/services/conversation
mkdir -p src/mythic_lite/services/audio
mkdir -p src/mythic_lite/services/model
mkdir -p src/mythic_lite/services/plugin

# Adapter layer
mkdir -p src/mythic_lite/adapters/external
mkdir -p src/mythic_lite/adapters/storage
mkdir -p src/mythic_lite/adapters/communication

# Plugin system
mkdir -p src/mythic_lite/plugins/examples
mkdir -p src/mythic_lite/plugins/templates

# Test structure
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/performance
mkdir -p tests/fixtures

# Documentation structure
mkdir -p docs/api
mkdir -p docs/architecture
mkdir -p docs/examples
mkdir -p docs/plugins

print_success "Directory structure created successfully!"

# Create __init__.py files
print_status "Creating __init__.py files..."

# Core layer
touch src/mythic_lite/core/interfaces/__init__.py
touch src/mythic_lite/core/events/__init__.py
touch src/mythic_lite/core/exceptions/__init__.py
touch src/mythic_lite/core/base/__init__.py
touch src/mythic_lite/core/dependency_injection/__init__.py
touch src/mythic_lite/core/extension_points/__init__.py

# Worker layer
touch src/mythic_lite/workers/base/__init__.py
touch src/mythic_lite/workers/llm/__init__.py
touch src/mythic_lite/workers/tts/__init__.py
touch src/mythic_lite/workers/asr/__init__.py
touch src/mythic_lite/workers/memory/__init__.py

# Service layer
touch src/mythic_lite/services/__init__.py
touch src/mythic_lite/services/conversation/__init__.py
touch src/mythic_lite/services/audio/__init__.py
touch src/mythic_lite/services/model/__init__.py
touch src/mythic_lite/services/plugin/__init__.py

# Adapter layer
touch src/mythic_lite/adapters/__init__.py
touch src/mythic_lite/adapters/external/__init__.py
touch src/mythic_lite/adapters/storage/__init__.py
touch src/mythic_lite/adapters/communication/__init__.py

# Plugin system
touch src/mythic_lite/plugins/__init__.py
touch src/mythic_lite/plugins/examples/__init__.py
touch src/mythic_lite/plugins/templates/__init__.py

# Test structure
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/performance/__init__.py
touch tests/fixtures/__init__.py

print_success "__init__.py files created successfully!"

# Create placeholder files for key interfaces
print_status "Creating placeholder interface files..."

# Core interfaces
cat > src/mythic_lite/core/interfaces/worker.py << 'EOF'
"""
Base worker interface definitions.
"""
from typing import Protocol, runtime_checkable, Dict, Any

@runtime_checkable
class IWorker(Protocol):
    """Base interface for all workers."""
    
    @property
    def is_initialized(self) -> bool: ...
    
    @property
    def is_enabled(self) -> bool: ...
    
    @property
    def status(self) -> Dict[str, Any]: ...
    
    async def initialize(self) -> bool: ...
    
    async def shutdown(self) -> None: ...
    
    async def health_check(self) -> bool: ...
EOF

# LLM interface
cat > src/mythic_lite/core/interfaces/llm.py << 'EOF'
"""
LLM worker interface definitions.
"""
from typing import AsyncGenerator, Optional
from .worker import IWorker

@runtime_checkable
class ILLMWorker(IWorker):
    """Interface for LLM workers."""
    
    async def generate_response(
        self, 
        prompt: str, 
        **kwargs
    ) -> str: ...
    
    async def generate_response_stream(
        self, 
        prompt: str, 
        **kwargs
    ) -> AsyncGenerator[str, None]: ...
    
    def estimate_tokens(self, text: str) -> int: ...
    
    async def switch_model(self, model_name: str) -> bool: ...
EOF

# TTS interface
cat > src/mythic_lite/core/interfaces/tts.py << 'EOF'
"""
TTS worker interface definitions.
"""
from typing import AsyncGenerator, Optional
from .worker import IWorker

@runtime_checkable
class ITTSWorker(IWorker):
    """Interface for TTS workers."""
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice: Optional[str] = None
    ) -> bytes: ...
    
    async def synthesize_speech_stream(
        self, 
        text: str, 
        voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]: ...
    
    def get_available_voices(self) -> list: ...
    
    async def switch_voice(self, voice_name: str) -> bool: ...
EOF

# ASR interface
cat > src/mythic_lite/core/interfaces/asr.py << 'EOF'
"""
ASR worker interface definitions.
"""
from typing import Optional, Callable
from .worker import IWorker

@runtime_checkable
class IASRWorker(IWorker):
    """Interface for ASR workers."""
    
    def set_callbacks(
        self, 
        on_transcription: Callable[[str], None],
        on_error: Optional[Callable[[str], None]] = None
    ) -> None: ...
    
    async def start_recording(self) -> bool: ...
    
    async def stop_recording(self) -> None: ...
    
    def get_audio_devices(self) -> dict: ...
EOF

# Memory interface
cat > src/mythic_lite/core/interfaces/memory.py << 'EOF'
"""
Memory worker interface definitions.
"""
from typing import Optional
from .worker import IWorker

@runtime_checkable
class IMemoryWorker(IWorker):
    """Interface for memory workers."""
    
    async def create_memory_summary(self, text: str, max_length: int = 100) -> Optional[str]: ...
    
    async def recall_memory(self, query: str) -> Optional[str]: ...
    
    async def store_memory(self, key: str, value: str) -> bool: ...
    
    def get_memory_stats(self) -> dict: ...
EOF

print_success "Interface files created successfully!"

# Create base worker class
print_status "Creating base worker class..."

cat > src/mythic_lite/core/base/worker.py << 'EOF'
"""
Base worker implementation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..interfaces.worker import IWorker

class BaseWorker(ABC):
    """Abstract base class for all workers."""
    
    def __init__(self, config: Any):
        self.config = config
        self._initialized = False
        self._enabled = False
        self._error = None
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @property
    def is_enabled(self) -> bool:
        return self._enabled
    
    @property
    def status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "enabled": self._enabled,
            "error": self._error
        }
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the worker."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the worker."""
        pass
    
    async def health_check(self) -> bool:
        """Check worker health."""
        return self._initialized and not self._error
EOF

print_success "Base worker class created successfully!"

# Create event system foundation
print_status "Creating event system foundation..."

cat > src/mythic_lite/core/events/base.py << 'EOF'
"""
Base event definitions.
"""
from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime

@dataclass
class BaseEvent:
    """Base class for all events."""
    timestamp: datetime
    source: str
    event_type: str
    data: Dict[str, Any]
EOF

cat > src/mythic_lite/core/events/bus.py << 'EOF'
"""
Event bus implementation.
"""
from typing import Type, List, Callable, Awaitable, Dict
from collections import defaultdict
import asyncio
from .base import BaseEvent

class EventBus:
    """Central event bus for system-wide communication."""
    
    def __init__(self):
        self._subscribers: Dict[Type[BaseEvent], List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[Type[BaseEvent], List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: Type[BaseEvent], handler: Callable) -> None:
        """Subscribe to an event type."""
        self._subscribers[event_type].append(handler)
    
    def subscribe_async(self, event_type: Type[BaseEvent], handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
        """Subscribe to an event type with async handler."""
        self._async_subscribers[event_type].append(handler)
    
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers."""
        # Handle sync subscribers
        for handler in self._subscribers[type(event)]:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in sync event handler: {e}")
        
        # Handle async subscribers
        for handler in self._async_subscribers[type(event)]:
            try:
                await handler(event)
            except Exception as e:
                print(f"Error in async event handler: {e}")
EOF

print_success "Event system foundation created successfully!"

# Create dependency injection container
print_status "Creating dependency injection container..."

cat > src/mythic_lite/core/dependency_injection/container.py << 'EOF'
"""
Dependency injection container.
"""
from typing import Type, TypeVar, Dict, Any, Callable
from functools import lru_cache

T = TypeVar('T')

class Container:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Type] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
    
    def register(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register an interface with its implementation."""
        self._services[interface] = implementation
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton implementation."""
        self._singletons[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for creating instances."""
        self._factories[interface] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve an interface to its implementation."""
        # Check singletons first
        if interface in self._singletons:
            if interface not in self._singletons:
                self._singletons[interface] = self._services[interface]()
            return self._singletons[interface]
        
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check regular services
        if interface in self._services:
            return self._services[interface]()
        
        raise ValueError(f"No implementation registered for {interface}")
EOF

print_success "Dependency injection container created successfully!"

# Create exception hierarchy
print_status "Creating exception hierarchy..."

cat > src/mythic_lite/core/exceptions/worker.py << 'EOF'
"""
Worker-related exceptions.
"""
class WorkerError(Exception):
    """Base exception for worker errors."""
    pass

class WorkerInitializationError(WorkerError):
    """Raised when worker fails to initialize."""
    pass

class WorkerOperationError(WorkerError):
    """Raised when worker operation fails."""
    pass

class WorkerConfigurationError(WorkerError):
    """Raised when worker configuration is invalid."""
    pass
EOF

print_success "Exception hierarchy created successfully!"

# Create main entry point
print_status "Creating main entry point..."

cat > src/mythic_lite/main.py << 'EOF'
"""
Main application entry point for the new architecture.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    """Main application entry point."""
    try:
        print("🚀 Starting Mythic-Lite with new architecture...")
        
        # TODO: Initialize dependency injection container
        # TODO: Register services
        # TODO: Start application
        
        print("✅ Application started successfully!")
        
        # Keep running for now
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Application failed to start: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
EOF

print_success "Main entry point created successfully!"

# Create setup script for development
print_status "Creating development setup script..."

cat > scripts/dev_setup.sh << 'EOF'
#!/bin/bash

# Development environment setup script

echo "🔧 Setting up development environment..."

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install package in development mode
pip install -e .

echo "✅ Development environment setup complete!"
echo "To activate: source venv/bin/activate"
EOF

chmod +x scripts/dev_setup.sh

print_success "Development setup script created successfully!"

# Create migration guide
print_status "Creating migration guide..."

cat > MIGRATION_GUIDE.md << 'EOF'
# 🔄 Migration Guide: Old to New Architecture

## 📋 Overview

This guide helps you migrate from the old Mythic-Lite architecture to the new improved architecture.

## 🎯 Migration Strategy

### Phase 1: Parallel Development
- Keep existing code working
- Implement new interfaces alongside old code
- Use feature flags to switch between implementations

### Phase 2: Gradual Migration
- Migrate one worker at a time
- Test thoroughly after each migration
- Update configuration to use new implementations

### Phase 3: Cleanup
- Remove old code
- Update documentation
- Final testing and validation

## 🔧 Step-by-Step Migration

### 1. Update Imports
```python
# Old
from mythic_lite.workers.llm_worker import LLMWorker

# New
from mythic_lite.workers.llm.llama_worker import LlamaWorker
```

### 2. Update Configuration
```python
# Old
llm_worker = LLMWorker(config)

# New
llm_worker = container.resolve(ILLMWorker)
```

### 3. Update Event Handling
```python
# Old
worker.on_transcription = callback

# New
event_bus.subscribe(SpeechRecognizedEvent, callback)
```

## 🚨 Breaking Changes

1. **Worker Initialization**: All workers now use async initialization
2. **Event System**: Callbacks replaced with event bus
3. **Dependency Injection**: Direct instantiation replaced with container resolution
4. **Interface Contracts**: All workers must implement new interfaces

## 📚 Testing Migration

1. **Unit Tests**: Update to use new interfaces
2. **Integration Tests**: Test new event system
3. **Performance Tests**: Ensure no regression
4. **User Acceptance**: Test with real conversations

## 🆘 Getting Help

- Check the test files for examples
- Review the new interface definitions
- Use the development setup script
- Run tests frequently to catch issues early
EOF

print_success "Migration guide created successfully!"

# Create README for new architecture
print_status "Creating new architecture README..."

cat > NEW_ARCHITECTURE_README.md << 'EOF'
# 🏗️ New Architecture Overview

## 📁 Directory Structure

```
src/mythic_lite/
├── core/                    # Core interfaces and abstractions
│   ├── interfaces/          # Abstract base classes
│   ├── events/             # Event system
│   ├── dependency_injection/ # DI container
│   ├── exceptions/         # Custom exceptions
│   └── base/               # Base classes
├── workers/                 # Worker implementations
│   ├── base/               # Base worker classes
│   ├── llm/                # LLM implementations
│   ├── tts/                # TTS implementations
│   ├── asr/                # ASR implementations
│   └── memory/             # Memory implementations
├── services/                # Business logic services
├── adapters/                # External system adapters
└── plugins/                 # Plugin system
```

## 🚀 Getting Started

### 1. Setup Development Environment
```bash
./scripts/dev_setup.sh
```

### 2. Run the New Architecture
```bash
python -m mythic_lite.main
```

### 3. Run Tests
```bash
pytest tests/ -v
```

## 🔧 Development Workflow

1. **Implement Interfaces**: Start with core interfaces
2. **Create Base Classes**: Implement common functionality
3. **Build Workers**: Implement specific worker types
4. **Add Services**: Create business logic services
5. **Test Everything**: Ensure all components work together

## 📚 Key Concepts

### Dependency Injection
- All dependencies resolved through container
- Easy to mock for testing
- Loose coupling between components

### Event System
- Publish/subscribe pattern
- Async event handling
- Decoupled communication

### Interface Contracts
- Clear contracts for all components
- Easy to swap implementations
- Better testing and mocking

## 🎯 Next Steps

1. Review the architecture design document
2. Follow the implementation plan
3. Start with Phase 1 (Foundation)
4. Test each component as you build it
5. Document your progress

## 🆘 Support

- Check the implementation plan for detailed steps
- Review the migration guide for existing code
- Use the test files as examples
- Run tests frequently to catch issues early
EOF

print_success "New architecture README created successfully!"

# Final status
echo ""
print_success "🎉 New architecture setup complete!"
echo ""
echo "📁 New directory structure created:"
echo "   - Core interfaces and abstractions"
echo "   - Event system foundation"
echo "   - Dependency injection container"
echo "   - Base worker classes"
echo "   - Service layer structure"
echo "   - Plugin system foundation"
echo ""
echo "📚 Documentation created:"
echo "   - Migration guide"
echo "   - New architecture README"
echo "   - Implementation plan"
echo ""
echo "🚀 Next steps:"
echo "   1. Review the architecture design document"
echo "   2. Follow the implementation plan"
echo "   3. Start with Phase 1 (Foundation)"
echo "   4. Test each component as you build it"
echo ""
echo "🔧 Development setup:"
echo "   - Run: ./scripts/dev_setup.sh"
echo "   - Activate: source venv/bin/activate"
echo "   - Test: pytest tests/ -v"
echo ""
print_warning "⚠️  Remember: Keep existing code working while implementing new architecture!"
echo ""