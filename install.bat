@echo off
REM AI Therapy Chatbot Installation Script (Windows)

echo Installing AI Therapy Chatbot...

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" || (
    echo Error: Python 3.11 or higher required
    exit /b 1
)

REM Install Python dependencies
echo Installing Python packages...
pip install -r requirements.txt

REM Setup environment
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please edit it with your Gemini API key.
)

echo Installation complete!
echo Next steps:
echo 1. Edit .env file with your Gemini API key
echo 2. Run: python run_app.py
pause
