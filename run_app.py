#!/usr/bin/env python3
"""
AI Therapy Chatbot Launcher
Simple launcher script for the therapy chatbot
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if environment is set up properly"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Run setup.py first or copy .env.example to .env")
        return False
    
    # Check if Gemini API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("⚠️  Gemini API key not configured")
        print("   Please edit .env file and add your Gemini API key")
        print("   Get one from: https://ai.google.dev")
        return False
    
    return True

def main():
    """Launch the therapy chatbot"""
    print("🤖 Starting AI Therapy Chatbot...")
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment not properly configured")
        print("   Run python setup.py to configure the environment")
        sys.exit(1)
    
    # Launch Streamlit app
    try:
        print("🚀 Launching Streamlit application...")
        print("   Opening in browser at: http://localhost:8501")
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start Streamlit")
        print("   Make sure all dependencies are installed")
        print("   Run: pip install -r requirements.txt")
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Therapy Chatbot")
    except FileNotFoundError:
        print("❌ Streamlit not found")
        print("   Install with: pip install streamlit")

if __name__ == "__main__":
    main()