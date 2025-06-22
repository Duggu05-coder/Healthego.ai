#!/usr/bin/env python3
"""
AI Therapy Chatbot Setup Script
Automated setup for the AI therapy chatbot application
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.11 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"✗ Python 3.11 or higher required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✓ Python version {version.major}.{version.minor} is compatible")
    return True

def install_requirements():
    """Install Python requirements"""
    if Path("requirements.txt").exists():
        return run_command("pip install -r requirements.txt", "Installing Python dependencies")
    else:
        print("✗ requirements.txt not found")
        return False

def setup_environment():
    """Create .env file template"""
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# AI Therapy Chatbot Environment Variables
# Get your Gemini API key from: https://ai.google.dev
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: PostgreSQL database connection
# DATABASE_URL=postgresql://username:password@localhost:5432/database_name
# PGHOST=localhost
# PGPORT=5432
# PGUSER=your_username
# PGPASSWORD=your_password
# PGDATABASE=therapy_chatbot
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✓ Created .env file template")
        print("  Please edit .env file and add your Gemini API key")
        return True
    else:
        print("✓ .env file already exists")
        return True

def check_streamlit_config():
    """Ensure Streamlit configuration exists"""
    config_dir = Path(".streamlit")
    config_file = config_dir / "config.toml"
    
    if not config_dir.exists():
        config_dir.mkdir()
    
    if not config_file.exists():
        config_content = """[server]
headless = true
address = "0.0.0.0"
port = 8501

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
        with open(config_file, 'w') as f:
            f.write(config_content)
        print("✓ Created Streamlit configuration")
    else:
        print("✓ Streamlit configuration exists")
    return True

def main():
    """Main setup function"""
    print("🤖 AI Therapy Chatbot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  Warning: Some dependencies failed to install")
        print("   You may need to install system dependencies manually")
        print("   See README.md for platform-specific instructions")
    
    # Setup environment
    setup_environment()
    
    # Check Streamlit config
    check_streamlit_config()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. (Optional) Set up PostgreSQL database")
    print("3. Run: streamlit run app.py")
    print("4. Open http://localhost:8501 in your browser")
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main()