#!/bin/bash
set -e

echo "Setting up development environment..."

# Sync environment with uv
echo "Syncing environment with uv..."
uv sync --extra dev

# Make hooks executable
echo "Making git hooks executable..."
chmod +x scripts/pre-commit
chmod +x scripts/pre-push

# Link hooks to .git/hooks
echo "Linking git hooks..."
ln -sf "$(pwd)/scripts/pre-commit" .git/hooks/pre-commit
ln -sf "$(pwd)/scripts/pre-push" .git/hooks/pre-push

echo ""
echo "✓ Development environment setup complete!"
echo ""
echo "Git hooks installed:"
echo "  - pre-commit: Runs ruff formatting and checks for unstaged changes"
echo "  - pre-push: Runs pre-commit + diff-quality check (90% threshold)"
