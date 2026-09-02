#!/bin/bash
# Clean GitClonePro build artifacts

set -e

echo "🧹 Cleaning GitClonePro..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove build artifacts
rm -rf build/ dist/ *.egg-info .eggs/ 2>/dev/null || true

# Remove test artifacts
rm -rf .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true

# Remove temporary clones
rm -rf clones/ temp/ test_clones/ 2>/dev/null || true

echo "✅ Clean complete!"