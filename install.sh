#!/bin/bash
# AI Therapy Chatbot Installation Script (Unix/Linux/macOS)

echo "Installing AI Therapy Chatbot..."

# Check Python version
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" || {
    echo "Error: Python 3.11 or higher required"
    exit 1
}

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pip
fi

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Setup environment
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your Gemini API key."
fi

echo "Installation complete!"
echo "Next steps:"
echo "1. Edit .env file with your Gemini API key"
echo "2. Run: python3 run_app.py"
