#!/usr/bin/env python3
"""
Railway Cloud Deployment for Plex HDHomeRun Emulator
This creates a cloud-hosted HDHomeRun emulator that Plex can use without your Mac!
"""
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import re
import os

class CloudHDHomeRunHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '':
            self.send_welcome()
        elif path == '/discover.json':
            self.send_discover()
        elif path == '/lineup.json':
            self.send_lineup()
        elif path == '/lineup_status.json':
            self.send_lineup_status()
        elif path.startswith('/auto/v'):
            self.send_stream(parsed_path.path)
        else:
            self.send_error(404, "Not Found")
    
    def send_welcome(self):
        """Send welcome page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cloud IPTV Tuner</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .status { color: #28a745; font-weight: bold; }
                .url { background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Cloud IPTV Tuner is Live!</h1>
                <p class="status">✅ HDHomeRun Emulator Running Successfully</p>
                <p><strong>Your Plex URL:</strong></p>
                <div class="url">https://iptv-tuner.onrender.com</div>
                <p><strong>Available Endpoints:</strong></p>
                <ul>
                    <li><a href="/discover.json">/discover.json</a> - Device discovery</li>
                    <li><a href="/lineup.json">/lineup.json</a> - Channel lineup</li>
                    <li><a href="/lineup_status.json">/lineup_status.json</a> - Status</li>
                </ul>
                <p><strong>For Plex:</strong> Add this URL to Plex Live TV & DVR settings</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def send_discover(self):
        """Send discover.json response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Get the Render URL from environment
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://iptv-tuner.onrender.com')
        if not base_url.startswith('http'):
            base_url = f'https://{base_url}'
            
        discover_data = {
            "FriendlyName": "Cloud IPTV Tuner",
            "Manufacturer": "Silicondust",
            "ModelNumber": "HDHR4-2US",
            "FirmwareName": "hdhomerun4_atsc",
            "FirmwareVersion": "20200101",
            "DeviceID": "12345678",
            "DeviceAuth": "cloud1234",
            "BaseURL": base_url,
            "LineupURL": f"{base_url}/lineup.json"
        }
        self.wfile.write(json.dumps(discover_data).encode('utf-8'))

    def send_lineup(self):
        """Send lineup.json response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Read the M3U playlist from local file (embedded in the service)
        lineup = []
        try:
            # Try to read from local file first
            with open('smaller_playlist.m3u', 'r', encoding='utf-8') as f:
                m3u_content = f.read()
                lineup = self.parse_m3u_to_lineup(m3u_content)
        except FileNotFoundError:
            # Fallback to GitHub Pages
            try:
                github_url = "https://emhamed.github.io/IPTV/smaller_playlist.m3u"
                response = requests.get(github_url, timeout=10)
                if response.status_code == 200:
                    m3u_content = response.text
                    lineup = self.parse_m3u_to_lineup(m3u_content)
                else:
                    # Final fallback to sample
                    lineup = [
                        {
                            "GuideNumber": "1",
                            "GuideName": "Sample Channel 1",
                            "URL": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
                        }
                    ]
            except Exception as e:
                print(f"Error reading playlist: {e}")
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
        
        # Get the Render URL from environment
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://iptv-tuner.onrender.com')
        if not base_url.startswith('http'):
            base_url = f'https://{base_url}'
        
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
                            "URL": f"{base_url}/auto/v{channel_num}"
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
            # Read from GitHub Pages
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

def run_cloud_hdhomerun_server():
    """Starts the cloud HDHomeRun emulator server."""
    port = int(os.environ.get('PORT', 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CloudHDHomeRunHandler)
    
    print(f"🌐 Starting Cloud HDHomeRun Emulator for Plex")
    print(f"============================================================")
    print(f"🚀 Server started on port {port}")
    print(f"📡 Plex can now detect this as an HDHomeRun device")
    print(f"🔗 Your cloud URL will be provided by Railway")
    print(f"📺 Reading playlist from: https://emhamed.github.io/IPTV/playlist.m3u")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print(f"============================================================")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Cloud HDHomeRun Emulator.")
        httpd.server_close()

if __name__ == "__main__":
    run_cloud_hdhomerun_server()
