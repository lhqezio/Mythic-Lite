"""
Pytest configuration and fixtures for Mythic-Lite tests.

This module provides common fixtures and configuration for all tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mythic_lite.config import Config
from mythic_lite.logger import Logger


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock configuration for tests."""
    config = Config()
    config.model_dir = temp_dir / "models"
    config.cache_dir = temp_dir / "cache"
    config.log_dir = temp_dir / "logs"
    
    # Create directories
    config.model_dir.mkdir(parents=True, exist_ok=True)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    config.log_dir.mkdir(parents=True, exist_ok=True)
    
    return config


@pytest.fixture
def mock_logger():
    """Create a mock logger for tests."""
    return Mock(spec=Logger)


@pytest.fixture
def mock_model_manager():
    """Create a mock model manager for tests."""
    return Mock()


@pytest.fixture
def mock_llm_worker():
    """Create a mock LLM worker for tests."""
    return Mock()


@pytest.fixture
def mock_tts_worker():
    """Create a mock TTS worker for tests."""
    return Mock()


@pytest.fixture
def mock_asr_worker():
    """Create a mock ASR worker for tests."""
    return Mock()


@pytest.fixture
def mock_summarization_worker():
    """Create a mock summarization worker for tests."""
    return Mock()


@pytest.fixture
def mock_conversation_worker():
    """Create a mock conversation worker for tests."""
    return Mock()


@pytest.fixture
def mock_chatbot_orchestrator():
    """Create a mock chatbot orchestrator for tests."""
    return Mock()


# Mark all tests as unit tests by default
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


# Auto-mark tests based on directory structure
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        else:
            item.add_marker(pytest.mark.unit)