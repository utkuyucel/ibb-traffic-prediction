#!/bin/bash

# Istanbul Municipality Traffic Prediction System Setup Script

echo "Setting up Istanbul Municipality Traffic Prediction System..."

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Manual: python main.py"
echo "2. Docker: cd docker && docker-compose up -d"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
