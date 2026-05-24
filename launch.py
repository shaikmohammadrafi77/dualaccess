#!/usr/bin/env python3
"""
Dual Access Login Test - Python Launcher
This script automatically handles virtual environment and starts the Flask app
"""

import os
import sys
import subprocess
import platform

def main():
    print("🚀 Starting Dual Access Login Test Application...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Determine the correct activation script based on OS
    if platform.system() == "Windows":
        activate_script = os.path.join("venv", "Scripts", "activate.bat")
        python_exe = os.path.join("venv", "Scripts", "python.exe")
    else:
        activate_script = os.path.join("venv", "bin", "activate")
        python_exe = os.path.join("venv", "bin", "python")
    
    # Check if virtual environment exists
    if not os.path.exists(python_exe):
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv venv")
        input("Press Enter to exit...")
        return
    
    # Check if Flask dependencies are installed
    try:
        result = subprocess.run([python_exe, "-c", "import flask_login"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("📦 Installing missing dependencies...")
            subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"⚠️  Warning: Could not check dependencies: {e}")
    
    # Start the Flask application
    print("🌐 Starting Flask application...")
    print("📍 Application will be available at: http://127.0.0.1:5000")
    print("⏹️  Press Ctrl+C to stop the application")
    print()
    
    try:
        subprocess.run([python_exe, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()












