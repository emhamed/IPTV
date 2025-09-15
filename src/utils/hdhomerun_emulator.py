#!/usr/bin/env python3
"""
HDHomeRun Emulator for Plex IPTV Integration
This creates a simple HDHomeRun-compatible server that Plex can detect
"""
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import re

class HDHomeRunHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/discover.json':
            self.send_discover()
        elif path == '/lineup.json':
            self.send_lineup()
        elif path == '/lineup_status.json':
            self.send_lineup_status()
        elif path.startswith('/auto/v'):
            self.send_stream(parsed_path.path)
        else:
            self.send_error(404, "Not Found")
    
    def send_discover(self):
        """Send HDHomeRun discover response"""
        response = {
            "FriendlyName": "IPTV Tuner",
            "ModelNumber": "HDTC-2US",
            "FirmwareName": "hdhomeruntc_atsc",
            "FirmwareVersion": "20200101",
            "DeviceID": "12345678",
            "DeviceAuth": "test1234",
            "BaseURL": f"http://{self.server.server_address[0]}:{self.server.server_port}",
            "LineupURL": f"http://{self.server.server_address[0]}:{self.server.server_port}/lineup.json"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_lineup(self):
        """Send channel lineup"""
        try:
            # Get the M3U playlist
            playlist_url = "http://192.168.2.181:8080/master_playlist.m3u"
            response = requests.get(playlist_url, timeout=10)
            response.raise_for_status()
            
            channels = []
            lines = response.text.splitlines()
            i = 0
            channel_num = 1
            
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    # Extract channel name
                    name_match = re.search(r',(.+)$', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        
                        # Get the URL
                        if i + 1 < len(lines):
                            url = lines[i + 1].strip()
                            if url.startswith("http"):
                                channel = {
                                    "GuideNumber": str(channel_num),
                                    "GuideName": name,
                                    "URL": f"http://{self.server.server_address[0]}:{self.server.server_port}/auto/v{channel_num}"
                                }
                                channels.append(channel)
                                channel_num += 1
                                i += 1  # Skip URL line
                i += 1
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(channels).encode())
            
        except Exception as e:
            print(f"Error getting lineup: {e}")
            self.send_error(500, "Internal Server Error")
    
    def send_lineup_status(self):
        """Send lineup status"""
        response = {
            "ScanInProgress": 0,
            "ScanPossible": 1,
            "Source": "Cable",
            "SourceList": ["Cable"]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_stream(self, path):
        """Send stream (proxy to actual IPTV stream)"""
        try:
            # Extract channel number from path
            channel_match = re.search(r'/auto/v(\d+)', path)
            if not channel_match:
                self.send_error(404, "Channel not found")
                return
            
            channel_num = int(channel_match.group(1))
            
            # Get the actual stream URL from the playlist
            playlist_url = "http://192.168.2.181:8080/master_playlist.m3u"
            response = requests.get(playlist_url, timeout=10)
            response.raise_for_status()
            
            lines = response.text.splitlines()
            i = 0
            current_channel = 1
            
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    if i + 1 < len(lines):
                        url = lines[i + 1].strip()
                        if url.startswith("http"):
                            if current_channel == channel_num:
                                # Found the channel, redirect to the stream
                                self.send_response(302)
                                self.send_header('Location', url)
                                self.end_headers()
                                return
                            current_channel += 1
                            i += 1  # Skip URL line
                i += 1
            
            self.send_error(404, "Channel not found")
            
        except Exception as e:
            print(f"Error streaming channel: {e}")
            self.send_error(500, "Internal Server Error")
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def start_hdhomerun_emulator():
    """Start the HDHomeRun emulator server"""
    print("🎬 Starting HDHomeRun Emulator for Plex IPTV Integration")
    print("=" * 60)
    
    # Create server
    server_address = ('0.0.0.0', 6077)
    httpd = HTTPServer(server_address, HDHomeRunHandler)
    
    print(f"🚀 HDHomeRun Emulator started on port 6077")
    print(f"📡 Plex can now detect this as an HDHomeRun device")
    print(f"🔗 Add this URL in Plex: http://localhost:6077")
    print(f"📺 Your IPTV playlist: http://192.168.2.181:8080/master_playlist.m3u")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping HDHomeRun Emulator...")
        httpd.shutdown()
        print("✅ HDHomeRun Emulator stopped")

if __name__ == "__main__":
    start_hdhomerun_emulator()
