#!/bin/bash

echo "🎬 Starting Plex-Compatible IPTV Tuner Server"
echo "============================================================"
echo "🚀 This will create a proper HDHomeRun-compatible server"
echo "📡 Plex will be able to detect and use this tuner"
echo "🔗 Use this URL in Plex: http://localhost:6077"
echo "📺 Reading playlist from GitHub Pages"
echo "============================================================"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    python3 plex-tuner-server.py
elif command -v python &> /dev/null; then
    python plex-tuner-server.py
else
    echo "❌ Python not found. Please install Python 3."
    exit 1
fi
