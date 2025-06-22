#!/bin/bash

# Quick run script for Istanbul Municipality Traffic Prediction System

echo "🚀 Starting Istanbul Municipality Traffic Prediction System"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed. Please run ./setup.sh first"
    exit 1
fi

echo "✅ Environment ready"
echo ""

# Option to run tests first
read -p "Run system tests first? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Running system tests..."
    python test_system.py
    echo ""
fi

# Start the application
echo "🚀 Starting the application..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python main.py
