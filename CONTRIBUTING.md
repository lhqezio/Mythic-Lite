# Contributing to Mythic-Lite

Thank you for your interest in contributing to Mythic-Lite! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating a new issue, please:

1. **Search existing issues** to see if your problem has already been reported
2. **Check the documentation** to see if there's a solution already documented
3. **Provide detailed information** when creating a new issue

When creating an issue, please include:

- **Operating system** and version
- **Python version**
- **Mythic-Lite version**
- **Detailed description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error messages** and logs
- **System information** (RAM, storage, etc.)

### Feature Requests

We welcome feature requests! When suggesting new features:

1. **Describe the feature** clearly and concisely
2. **Explain the use case** and why it would be valuable
3. **Consider alternatives** and why this approach is best
4. **Be specific** about requirements and constraints

### Pull Requests

We love pull requests! Here's how to contribute:

#### Before You Start

1. **Fork the repository** and clone it locally
2. **Create a feature branch** from the main branch
3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

#### Development Workflow

1. **Make your changes** following the coding standards below
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Run the test suite**:
   ```bash
   make test
   make lint
   ```
5. **Commit your changes** with clear, descriptive commit messages
6. **Push to your fork** and create a pull request

#### Pull Request Guidelines

- **Title**: Clear, descriptive title (e.g., "Add support for custom TTS voices")
- **Description**: Detailed description of changes and why they're needed
- **Tests**: Ensure all tests pass and add new tests for new functionality
- **Documentation**: Update relevant documentation
- **Breaking Changes**: Clearly mark any breaking changes

## 📝 Coding Standards

### Python Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting (line length: 88 characters)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pydocstyle**: Documentation style

Run these tools before committing:

```bash
make format    # Format code with black and isort
make lint      # Run all linting checks
```

### Code Organization

- **Follow the existing structure** in the `src/mythic_lite/` directory
- **Use meaningful names** for variables, functions, and classes
- **Add type hints** for all function parameters and return values
- **Write docstrings** for all public functions and classes
- **Keep functions focused** and single-purpose
- **Use async/await** for I/O operations

### Documentation

- **Update docstrings** when changing function signatures
- **Add examples** in docstrings for complex functions
- **Update README.md** for user-facing changes
- **Update API documentation** for new public APIs
- **Include usage examples** in documentation

### Testing

- **Write tests** for all new functionality
- **Use pytest** as the testing framework
- **Mock external dependencies** in unit tests
- **Test edge cases** and error conditions
- **Maintain good test coverage** (aim for 80%+)

## 🏗️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Local Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/mythic-lite.git
   cd mythic-lite
   ```

2. **Create virtual environment**:
   ```bash
   make venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies**:
   ```bash
   make install-dev
   ```

4. **Install pre-commit hooks**:
   ```bash
   make pre-commit
   ```

5. **Verify setup**:
   ```bash
   make test
   ```

### Common Development Commands

```bash
make help          # Show all available commands
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting checks
make format        # Format code
make clean         # Clean build artifacts
make build         # Build package
make start         # Start the chatbot
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mythic_lite --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run specific test files
pytest tests/test_llm_worker.py

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- **Use descriptive test names** that explain what is being tested
- **Group related tests** in test classes
- **Use fixtures** for common setup
- **Mock external dependencies** to isolate units under test
- **Test both success and failure cases**
- **Use parametrized tests** for testing multiple scenarios

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Common fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_core/
│   ├── test_workers/
│   └── test_utils/
├── integration/             # Integration tests
└── fixtures/                # Test data and fixtures
```

## 📚 Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install -r requirements-dev.txt

# Build documentation
make docs

# View documentation (open docs/_build/html/index.html in browser)
```

### Documentation Standards

- **Use clear, concise language**
- **Include practical examples**
- **Maintain consistent formatting**
- **Update when APIs change**
- **Use proper markdown syntax**
- **Include code examples** where appropriate

## 🔄 Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

Before releasing a new version:

1. **Update version** in `pyproject.toml` and `src/mythic_lite/__init__.py`
2. **Update CHANGELOG.md** with new version and changes
3. **Run full test suite** and ensure all tests pass
4. **Update documentation** if needed
5. **Create release tag**:
   ```bash
   git tag -a v1.2.3 -m "Release version 1.2.3"
   git push origin v1.2.3
   ```
6. **Build and publish** to PyPI (maintainers only)

## 🐛 Bug Reports

### Before Reporting a Bug

1. **Check if it's already reported** in existing issues
2. **Try to reproduce** the issue consistently
3. **Check your environment** (Python version, dependencies, etc.)
4. **Look at the logs** for error messages
5. **Try the latest version** from the main branch

### Bug Report Template

```markdown
**Bug Description**
Brief description of the bug

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Windows 11, Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Mythic-Lite: [e.g., 0.1.0]
- RAM: [e.g., 16GB]

**Additional Information**
Any other relevant information, logs, screenshots, etc.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Brief description of the feature

**Use Case**
Why this feature would be valuable

**Proposed Implementation**
How you think it could be implemented

**Alternatives Considered**
Other approaches you considered

**Additional Context**
Any other relevant information
```

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** and considerate of others
- **Use inclusive language**
- **Be collaborative** and constructive
- **Focus on the code** and technical issues
- **Help others** when you can

## 🙏 Thank You

Thank you for contributing to Mythic-Lite! Your contributions help make this project better for everyone. Whether you're reporting bugs, suggesting features, or contributing code, we appreciate your help.

If you have any questions about contributing, feel free to ask in GitHub Discussions or create an issue.