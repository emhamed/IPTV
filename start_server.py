#!/usr/bin/env python3
"""
IPTV Server Startup Script
Run this to start your IPTV server locally
"""

import os
import sys
import subprocess

def main():
    print("🎬 Starting IPTV Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("src/core/main.py"):
        print("❌ Error: Please run this from the project root directory")
        print("   Make sure you're in the directory with src/ folder")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        sys.exit(1)
    
    print("✅ Python version:", sys.version.split()[0])
    
    # Install requirements if needed
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies found")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    print("\n🚀 Starting server...")
    print("📺 Dashboard: http://localhost:8000")
    print("📋 Playlist: http://localhost:8000/playlist.m3u")
    print("🎮 Web Player: http://localhost:8000/web_player.html")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Change to src/core directory and run main.py
    os.chdir("src/core")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()
