# Development Guide for pydub-ng

This guide provides information for developers working on the pydub-ng project.

## Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/medecau/pydub-ng.git
cd pydub-ng

# Install development dependencies with uv
uv sync --extra dev
```

## Running Tests

### Using tox (recommended for CI)

Tox is used to run tests across multiple Python versions:

```bash
# Run tests on all supported Python versions
make test

# Run tests on a specific Python version
tox -e 3.12

# Run specific tests on a specific Python version
tox -e 3.12 -- tests/test_utils.py -v
```

### Using pytest directly (faster for development)

For faster development cycles, you can use pytest directly:

```bash
# Run all tests
uv run pytest

# Run specific tests
uv run pytest tests/test_utils.py -v

# Run tests matching a specific name pattern
uv run pytest -k "test_db"
```

## Code Formatting and Linting

The project uses Ruff for formatting and linting:

```bash
# Run formatting and linting
make fmt

# Check formatting without applying changes
ruff format --check .
```

## Testing with Multiple Python Versions

The project supports Python 3.11, 3.12, and 3.13. Python 3.13 requires the `audioop-lts` package.

## Migration to pytest

The project is currently transitioning from unittest to pytest. See the [Migration Plan](PYTEST_MIGRATION_PLAN.md) for details.

## Project Structure

- `pydub/`: Main package source code
- `tests/`: Tests using pytest framework
- `pyproject.toml`: Project metadata, dependencies, and configuration (tox, ruff, etc.)