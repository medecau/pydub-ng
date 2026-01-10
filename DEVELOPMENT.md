# Development Guide for pydub-ng

This guide provides information for developers working on the pydub-ng project.

## Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/medecau/pydub-ng.git
cd pydub-ng

# Run the development setup script (recommended)
bash scripts/init-dev.sh

# OR install manually
pip install -e ".[dev]"

# OR install with scipy support (for testing scipy_effects)
pip install -e ".[dev,scipy]"
```

The `init-dev.sh` script will:
- Sync the environment using `uv`
- Install git hooks for automatic code quality checks

### Git Hooks

The project includes two git hooks that help maintain code quality:

**pre-commit**: Runs on every commit
- Automatically fixes code issues with `ruff check --fix-only`
- Formats code with `ruff format`
- Verifies code quality on modified lines using `diff-quality`
- Fails if there are unstaged changes after formatting (prompts you to stage them)

**pre-push**: Runs before pushing to remote
- Runs all pre-commit checks first
- Runs full test suite with coverage (`pytest --cov=pydub --cov-report=xml`)
- Verifies test coverage on modified lines using `diff-cover`
- Prevents pushing code without adequate test coverage

These hooks are automatically linked by `scripts/init-dev.sh`. To install them manually:

```bash
chmod +x scripts/pre-commit scripts/pre-push
ln -sf "$(pwd)/scripts/pre-commit" .git/hooks/pre-commit
ln -sf "$(pwd)/scripts/pre-push" .git/hooks/pre-push
```

## Running Tests

### Using tox (recommended for CI)

Tox runs tests across multiple Python versions (3.10, 3.11, 3.12, 3.13, 3.14) with scipy support enabled:

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