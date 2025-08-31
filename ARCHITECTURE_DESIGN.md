# 🏗️ Mythic-Lite Architecture Redesign

## 📋 Executive Summary

This document outlines a comprehensive redesign of the Mythic-Lite chatbot system architecture to address current limitations and establish a robust, scalable foundation for future development.

## 🎯 Design Goals

- **Eliminate circular dependencies** through proper interface abstraction
- **Improve maintainability** with clean separation of concerns
- **Enable extensibility** through plugin architecture
- **Enhance reliability** with proper error handling and recovery
- **Optimize performance** through async-first design
- **Simplify testing** with dependency injection and mocking

## 🏛️ Architecture Overview

### Current Architecture Issues

1. **Circular Dependencies**: Workers import from core, core imports from workers
2. **Tight Coupling**: Direct instantiation of concrete classes
3. **Limited Error Handling**: Basic try-catch without recovery strategies
4. **Synchronous Operations**: Blocking operations in main thread
5. **No Interface Contracts**: Implementation details leak between layers

### New Architecture Principles

1. **Dependency Inversion**: High-level modules depend on abstractions
2. **Interface Segregation**: Clean, focused interfaces for each capability
3. **Single Responsibility**: Each class has one reason to change
4. **Open/Closed**: Open for extension, closed for modification
5. **Async-First**: Non-blocking operations throughout the system
6. **Event-Driven**: Loose coupling through events and callbacks

## 🏗️ Component Architecture

### 1. Core Layer

```
core/
├── interfaces/          # Abstract base classes and protocols
├── events/             # Event system for loose coupling
├── dependency_injection/ # DI container and service registration
├── exceptions/         # Custom exception hierarchy
└── base/               # Base classes and utilities
```

**Key Components:**
- `IWorker`: Base interface for all workers
- `IEventBus`: Event publishing and subscription
- `IContainer`: Dependency injection container
- `BaseWorker`: Abstract base class for workers

### 2. Worker Layer

```
workers/
├── base/               # Base worker implementations
├── llm/                # Language model workers
├── tts/                # Text-to-speech workers
├── asr/                # Speech recognition workers
└── memory/             # Memory management workers
```

**Worker Categories:**
- **Stateless Workers**: LLM, TTS, ASR (can be easily replaced)
- **Stateful Workers**: Memory, Conversation (maintain state)

### 3. Service Layer

```
services/
├── conversation/        # Conversation flow management
├── audio/              # Audio pipeline coordination
├── model/              # Model lifecycle management
└── plugin/             # Plugin system management
```

**Service Responsibilities:**
- **ConversationService**: Manages conversation state and flow
- **AudioService**: Coordinates audio input/output operations
- **ModelService**: Handles model loading, caching, and updates

### 4. Adapter Layer

```
adapters/
├── external/           # External system integrations
├── storage/            # Data persistence adapters
└── communication/      # Network and IPC adapters
```

## 🔌 Interface Definitions

### IWorker Interface

```python
@runtime_checkable
class IWorker(Protocol):
    """Base interface for all workers."""
    
    @property
    def is_initialized(self) -> bool: ...
    
    @property
    def is_enabled(self) -> bool: ...
    
    @property
    def status(self) -> WorkerStatus: ...
    
    async def initialize(self) -> bool: ...
    
    async def shutdown(self) -> None: ...
    
    async def health_check(self) -> HealthStatus: ...
```

### ILLMWorker Interface

```python
@runtime_checkable
class ILLMWorker(IWorker, Protocol):
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
```

### ITTSWorker Interface

```python
@runtime_checkable
class ITTSWorker(IWorker, Protocol):
    """Interface for TTS workers."""
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice: Optional[str] = None
    ) -> AudioData: ...
    
    async def synthesize_speech_stream(
        self, 
        text: str, 
        voice: Optional[str] = None
    ) -> AsyncGenerator[AudioData, None]: ...
    
    def get_available_voices(self) -> List[VoiceInfo]: ...
    
    async def switch_voice(self, voice_name: str) -> bool: ...
```

## 📡 Event System

### Event Types

```python
@dataclass
class SpeechRecognizedEvent(BaseEvent):
    """Event fired when speech is recognized."""
    text: str
    confidence: float
    timestamp: datetime
    source: str = "asr_worker"

@dataclass
class ResponseGeneratedEvent(BaseEvent):
    """Event fired when a response is generated."""
    response: str
    tokens_used: int
    generation_time: float
    model_name: str
    timestamp: datetime
    source: str = "llm_worker"

@dataclass
class AudioPlaybackEvent(BaseEvent):
    """Event fired for audio playback status."""
    event_type: Literal["started", "completed", "error"]
    audio_length: float
    timestamp: datetime
    source: str = "tts_worker"
```

### Event Bus Implementation

```python
class EventBus:
    """Central event bus for system-wide communication."""
    
    def __init__(self):
        self._subscribers: Dict[Type[BaseEvent], List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[Type[BaseEvent], List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """Subscribe to an event type."""
        self._subscribers[event_type].append(handler)
    
    def subscribe_async(self, event_type: Type[T], handler: Callable[[T], Awaitable[None]]) -> None:
        """Subscribe to an event type with async handler."""
        self._async_subscribers[event_type].append(handler)
    
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers."""
        # Handle sync subscribers
        for handler in self._subscribers[type(event)]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in sync event handler: {e}")
        
        # Handle async subscribers
        for handler in self._async_subscribers[type(event)]:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in async event handler: {e}")
```

## 🔧 Dependency Injection

### Container Implementation

```python
class Container:
    """Dependency injection container."""
    
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
```

## 🚀 Implementation Strategy

### Phase 1: Foundation (Weeks 1-2)

1. **Create Interface Layer**
   - Define all worker interfaces
   - Create base worker classes
   - Implement event system

2. **Dependency Injection**
   - Build DI container
   - Refactor orchestrator to use DI
   - Remove circular dependencies

3. **Error Handling**
   - Create custom exception hierarchy
   - Implement proper error recovery
   - Add retry mechanisms

### Phase 2: Worker Refactoring (Weeks 3-4)

1. **LLM Worker**
   - Implement async patterns
   - Add model switching capability
   - Improve token management

2. **TTS Worker**
   - Async audio processing
   - Voice switching
   - Audio format conversion

3. **ASR Worker**
   - Async speech recognition
   - Multiple model support
   - Real-time streaming

4. **Memory Worker**
   - Async memory operations
   - Better summarization
   - Memory compression

### Phase 3: Service Layer (Weeks 5-6)

1. **Conversation Service**
   - Business logic extraction
   - State management
   - Conversation flow control

2. **Audio Service**
   - Audio pipeline management
   - Format conversion
   - Device management

3. **Model Service**
   - Model lifecycle management
   - Automatic updates
   - Performance optimization

### Phase 4: Plugin System (Weeks 7-8)

1. **Plugin Architecture**
   - Plugin discovery
   - Hot reloading
   - Configuration management

2. **Extension Points**
   - Custom workers
   - Custom events
   - Custom services

### Phase 5: Testing & Documentation (Weeks 9-10)

1. **Test Infrastructure**
   - Unit test refactoring
   - Integration tests
   - Performance tests

2. **Documentation**
   - API documentation
   - Architecture diagrams
   - Implementation guides

## 📊 Benefits of New Architecture

### 1. **Maintainability**
- Clear separation of concerns
- Easy to understand and modify
- Reduced coupling between components

### 2. **Testability**
- Easy to mock dependencies
- Isolated unit tests
- Better integration testing

### 3. **Extensibility**
- Plugin system for new features
- Easy to add new worker types
- Configurable behavior

### 4. **Performance**
- Async operations throughout
- Better resource management
- Optimized memory usage

### 5. **Reliability**
- Proper error handling
- Automatic recovery
- Health monitoring

## 🔍 Migration Strategy

### 1. **Incremental Migration**
- Implement new interfaces alongside existing code
- Gradually migrate workers one by one
- Maintain backward compatibility during transition

### 2. **Feature Flags**
- Use configuration to switch between old and new implementations
- Allow gradual rollout of new features
- Easy rollback if issues arise

### 3. **Testing Strategy**
- Comprehensive testing of new architecture
- Performance benchmarking
- User acceptance testing

## 📈 Future Considerations

### 1. **Scalability**
- Horizontal scaling of workers
- Load balancing
- Distributed processing

### 2. **Cloud Integration**
- Cloud-based model hosting
- Hybrid local/cloud processing
- Multi-region deployment

### 3. **Advanced Features**
- Multi-modal input/output
- Advanced conversation management
- Personalization and learning

---

**This architecture redesign provides a solid foundation for the future development of Mythic-Lite while maintaining the core functionality that users love.**