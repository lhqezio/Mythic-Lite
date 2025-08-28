.PHONY: help install install-dev test test-cov lint format clean build dist publish docs

# Default target
help:
	@echo "Mythic-Lite Development Commands"
	@echo "================================"
	@echo ""
	@echo "Installation:"
	@echo "  install      Install runtime dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Packaging:"
	@echo "  build        Build package"
	@echo "  dist         Create distribution files"
	@echo "  publish      Publish to PyPI (requires authentication)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Build documentation"
	@echo ""
	@echo "Setup:"
	@echo "  setup        Run complete development setup"
	@echo "  pre-commit   Install pre-commit hooks"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest

test-cov:
	pytest --cov=mythic_lite --cov-report=term-missing --cov-report=html

# Code quality
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/ -f json -o bandit-report.json

format:
	black src/ tests/
	isort src/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Packaging
build:
	python -m build

dist: clean build

publish: dist
	twine upload dist/*

# Documentation
docs:
	cd docs && make html

# Development setup
setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation."

pre-commit:
	pre-commit install

# Quick start
start:
	python -m mythic_lite.utils.cli

# Model management
models:
	python -m mythic_lite.scripts.initialize_models

# Environment setup
env:
	cp .env.example .env
	@echo "Environment file created. Please edit .env with your settings."

# Virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # Linux/macOS"
	@echo "  venv\\Scripts\\activate     # Windows"

# Complete setup for new developers
dev-setup: venv
	@echo "Activating virtual environment..."
	@echo "Please run: source venv/bin/activate  # Linux/macOS"
	@echo "Or: venv\\Scripts\\activate           # Windows"
	@echo "Then run: make install-dev"