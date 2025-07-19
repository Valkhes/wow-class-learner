#!/bin/bash

echo "Setting up WoW Class Learner with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "uv installed successfully!"
else
    echo "uv is already installed."
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv sync

# Create data directory
echo "Creating data directory..."
mkdir -p data

echo ""
echo "Setup completed successfully!"
echo ""
echo "To run the server:"
echo "  uv run python main.py"
echo ""
echo "To activate the environment manually:"
echo "  source .venv/bin/activate"
echo ""
echo "To install additional dependencies:"
echo "  uv add package-name"
echo "" 