#!/bin/bash
# Linting script for IBB Traffic Prediction

set -e  # Exit on any error

echo "🔧 IBB Traffic Prediction - Linting & Code Quality"
echo "================================================="

# Activate virtual environment
source venv/bin/activate

echo "🎨 Step 1: Formatting code..."
python -m ruff format src/ *.py

echo "🔧 Step 2: Auto-fixing linting issues..."
python -m ruff check --fix src/ *.py

echo "🔍 Step 3: Final lint check (should be clean)..."
if python -m ruff check src/ *.py; then
    echo "✅ All linting checks passed!"
    echo "🚀 Code is ready for push!"
else
    echo "❌ Linting issues remain. Please fix manually."
    exit 1
fi

echo ""
echo "✨ Linting completed successfully!"
