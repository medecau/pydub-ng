# Development Guide for pydub-ng

This guide provides information for developers working on the pydub-ng project.

## Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/medecau/pydub-ng.git
cd pydub-ng

# Install development dependencies
pip install -e ".[dev]"
```

## Running Tests

### Using tox (recommended for CI)

Tox runs tests across multiple Python versions (3.10, 3.11, 3.12):

```bash
# Run tests on all supported Python versions
make test

# Run tests on a specific Python version
tox -e py310

# Run specific tests on a specific Python version
tox -e py310 -- tests/test_utils.py -v
```

### Using pytest directly (faster for development)

For faster development cycles, you can use pytest directly:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_utils.py -v

# Run tests matching a specific name pattern
pytest -k "test_db"

# Generate coverage report
make coverage
```

## Code Formatting and Linting

The project uses Ruff for formatting and linting:

```bash
# Format code
make fmt

# Check formatting and linting
make lint
```

## Project Structure

- `pydub/`: Main package source code
- `tests/`: Tests using pytest framework
- `pyproject.toml`: Project metadata, dependencies, and configuration