#!/usr/bin/env python3
"""
Plex-Compatible IPTV Tuner Server
This creates a proper HDHomeRun-compatible server that Plex can detect and use.
"""
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import re
import os

class PlexTunerHandler(BaseHTTPRequestHandler):
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
        """Send discover.json response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        discover_data = {
            "FriendlyName": "GitHub IPTV Tuner",
            "Manufacturer": "Silicondust",
            "ModelNumber": "HDHR4-2US",
            "FirmwareName": "hdhomerun4_atsc",
            "FirmwareVersion": "20200101",
            "DeviceID": "12345678",
            "DeviceAuth": "github1234",
            "BaseURL": f"http://{self.server.server_address[0]}:{self.server.server_address[1]}",
            "LineupURL": f"http://{self.server.server_address[0]}:{self.server.server_address[1]}/lineup.json"
        }
        self.wfile.write(json.dumps(discover_data).encode('utf-8'))

    def send_lineup(self):
        """Send lineup.json response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Read the M3U playlist and convert to lineup format
        lineup = []
        try:
            # Try to read from GitHub Pages first
            github_url = "https://emhamed.github.io/IPTV/playlist.m3u"
            response = requests.get(github_url, timeout=10)
            if response.status_code == 200:
                m3u_content = response.text
                lineup = self.parse_m3u_to_lineup(m3u_content)
            else:
                # Fallback to local file
                if os.path.exists('playlist.m3u'):
                    with open('playlist.m3u', 'r') as f:
                        m3u_content = f.read()
                    lineup = self.parse_m3u_to_lineup(m3u_content)
        except Exception as e:
            print(f"Error reading playlist: {e}")
            # Create a sample lineup if nothing works
            lineup = [
                {
                    "GuideNumber": "1",
                    "GuideName": "Sample Channel 1",
                    "URL": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
                }
            ]
        
        self.wfile.write(json.dumps(lineup).encode('utf-8'))

    def parse_m3u_to_lineup(self, m3u_content):
        """Parse M3U content and convert to lineup format"""
        lineup = []
        lines = m3u_content.splitlines()
        channel_num = 1
        
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("#EXTINF:"):
                # Extract channel name
                name_match = re.search(r',(.+)$', line)
                name = name_match.group(1).strip() if name_match else f"Channel {channel_num}"
                
                # Get the URL from the next line
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith("http"):
                        lineup.append({
                            "GuideNumber": str(channel_num),
                            "GuideName": name,
                            "URL": f"http://{self.server.server_address[0]}:{self.server.server_address[1]}/auto/v{channel_num}"
                        })
                        channel_num += 1
        
        return lineup

    def send_lineup_status(self):
        """Send lineup_status.json response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        status_data = {
            "ScanInProgress": 0,
            "ScanPossible": 1,
            "Source": "Cable",
            "SourceList": ["Cable"],
            "Tuners": 2
        }
        self.wfile.write(json.dumps(status_data).encode('utf-8'))

    def send_stream(self, path):
        """Redirect to the actual IPTV stream URL"""
        match = re.search(r'/auto/v(\d+)', path)
        if match:
            channel_number = int(match.group(1))
            
            # Find the actual URL from the M3U playlist
            stream_url = self.get_stream_url(channel_number)
            
            if stream_url:
                self.send_response(302)  # Found
                self.send_header('Location', stream_url)
                self.end_headers()
            else:
                self.send_error(404, "Channel Not Found")
        else:
            self.send_error(404, "Invalid Stream Request")

    def get_stream_url(self, channel_number):
        """Get the actual stream URL for a channel number"""
        try:
            # Try to read from GitHub Pages
            github_url = "https://emhamed.github.io/IPTV/playlist.m3u"
            response = requests.get(github_url, timeout=10)
            if response.status_code == 200:
                m3u_content = response.text
                return self.extract_channel_url(m3u_content, channel_number)
        except Exception as e:
            print(f"Error getting stream URL: {e}")
        
        return None

    def extract_channel_url(self, m3u_content, channel_number):
        """Extract the URL for a specific channel number"""
        lines = m3u_content.splitlines()
        current_channel_num = 1
        
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("#EXTINF:"):
                if current_channel_num == channel_number:
                    if i + 1 < len(lines):
                        return lines[i + 1].strip()
                current_channel_num += 1
        
        return None

def run_plex_tuner_server(host='0.0.0.0', port=6077):
    """Starts the Plex-compatible tuner server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PlexTunerHandler)
    
    print(f"🎬 Starting Plex-Compatible IPTV Tuner Server")
    print(f"============================================================")
    print(f"🚀 Server started on port {port}")
    print(f"📡 Plex can now detect this as an HDHomeRun device")
    print(f"🔗 Add this URL in Plex: http://{host}:{port}")
    print(f"📺 Reading playlist from: https://emhamed.github.io/IPTV/playlist.m3u")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print(f"============================================================")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Plex Tuner Server.")
        httpd.server_close()

if __name__ == "__main__":
    run_plex_tuner_server()
