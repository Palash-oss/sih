#!/usr/bin/env python3
"""
Healthcare Chatbot Startup Script
Simple script to start the healthcare chatbot with proper initialization.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_environment():
    """Check if environment is properly set up."""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Warning: .env file not found.")
        print("Creating .env from template...")
        
        template_file = Path('.env.template')
        if template_file.exists():
            import shutil
            shutil.copy('.env.template', '.env')
            print("✅ .env file created from template.")
            print("📝 Please edit .env file with your Twilio credentials before running.")
            return False
        else:
            print("❌ Error: .env.template file not found.")
            return False
    
    print("✅ Environment file found.")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    dirs_to_create = ['data', 'logs', 'chatbot', 'services', 'templates']
    
    for dir_name in dirs_to_create:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created directory: {dir_name}")

def check_required_files():
    """Check if required files exist."""
    required_files = [
        'app.py',
        'config.py',
        'models.py',
        'chatbot/health_bot.py',
        'data/health_knowledge_base.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present.")
    return True

def start_application():
    """Start the Flask application."""
    print("\n🚀 Starting Healthcare Chatbot...")
    print("=" * 50)
    
    # Set environment variables for better development experience
    os.environ['PYTHONPATH'] = str(Path.cwd())
    
    try:
        # Import and run the app
        from app import app
        from config import Config
        
        print(f"🌐 Server starting on http://localhost:{Config.PORT}")
        print("📱 WhatsApp and SMS webhooks ready")
        print("🏥 Healthcare chatbot is now running!")
        print("=" * 50)
        print("\nPress Ctrl+C to stop the server")
        
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Please ensure all dependencies are installed correctly.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Healthcare Chatbot...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main function to set up and start the application."""
    print("🏥 Healthcare Chatbot - Setup and Startup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create necessary directories
    create_directories()
    
    # Check if required files exist
    if not check_required_files():
        print("❌ Setup incomplete. Please ensure all project files are present.")
        sys.exit(1)
    
    # Check environment setup
    if not check_environment():
        print("\n📋 Setup Instructions:")
        print("1. Edit the .env file with your Twilio credentials")
        print("2. Sign up for Twilio at https://www.twilio.com")
        print("3. Get your Account SID and Auth Token")
        print("4. Set up WhatsApp Sandbox in Twilio Console")
        print("5. Run this script again")
        sys.exit(0)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    print("✅ Setup completed successfully!")
    time.sleep(1)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()