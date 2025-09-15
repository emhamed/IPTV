#!/usr/bin/env python3
"""
Embedded IPTV Tuner for Render - No external dependencies
This version has the playlist embedded directly in the code
"""
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re
import os

# Embedded playlist data (first 100 channels for testing)
EMBEDDED_PLAYLIST = """#EXTM3U
# Embedded IPTV Playlist for Plex
# Total Channels: 100

#EXTINF:-1 tvg-id="1" tvg-name="Movie 1" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200584.mp4
#EXTINF:-1 tvg-id="2" tvg-name="Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/202205.mkv
#EXTINF:-1 tvg-id="3" tvg-name="Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/204951.mp4
#EXTINF:-1 tvg-id="4" tvg-name="All My Friends Are Dead (2024)" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/220726.mp4
#EXTINF:-1 tvg-id="5" tvg-name="Series 1" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181776.mkv
#EXTINF:-1 tvg-id="6" tvg-name="Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181777.mkv
#EXTINF:-1 tvg-id="7" tvg-name="Action Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200585.mp4
#EXTINF:-1 tvg-id="8" tvg-name="Comedy Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181778.mkv
#EXTINF:-1 tvg-id="9" tvg-name="Drama Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200586.mp4
#EXTINF:-1 tvg-id="10" tvg-name="Thriller Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181779.mkv
#EXTINF:-1 tvg-id="11" tvg-name="Horror Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200587.mp4
#EXTINF:-1 tvg-id="12" tvg-name="Sci-Fi Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181780.mkv
#EXTINF:-1 tvg-id="13" tvg-name="Romance Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200588.mp4
#EXTINF:-1 tvg-id="14" tvg-name="Fantasy Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181781.mkv
#EXTINF:-1 tvg-id="15" tvg-name="Adventure Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200589.mp4
#EXTINF:-1 tvg-id="16" tvg-name="Crime Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181782.mkv
#EXTINF:-1 tvg-id="17" tvg-name="Mystery Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200590.mp4
#EXTINF:-1 tvg-id="18" tvg-name="Documentary Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181783.mkv
#EXTINF:-1 tvg-id="19" tvg-name="Family Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200591.mp4
#EXTINF:-1 tvg-id="20" tvg-name="Kids Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181784.mkv
#EXTINF:-1 tvg-id="21" tvg-name="Action Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181785.mkv
#EXTINF:-1 tvg-id="22" tvg-name="Comedy Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200592.mp4
#EXTINF:-1 tvg-id="23" tvg-name="Drama Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181786.mkv
#EXTINF:-1 tvg-id="24" tvg-name="Thriller Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200593.mp4
#EXTINF:-1 tvg-id="25" tvg-name="Horror Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181787.mkv
#EXTINF:-1 tvg-id="26" tvg-name="Sci-Fi Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200594.mp4
#EXTINF:-1 tvg-id="27" tvg-name="Romance Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181788.mkv
#EXTINF:-1 tvg-id="28" tvg-name="Fantasy Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200595.mp4
#EXTINF:-1 tvg-id="29" tvg-name="Adventure Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181789.mkv
#EXTINF:-1 tvg-id="30" tvg-name="Crime Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200596.mp4
#EXTINF:-1 tvg-id="31" tvg-name="Mystery Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181790.mkv
#EXTINF:-1 tvg-id="32" tvg-name="Documentary Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200597.mp4
#EXTINF:-1 tvg-id="33" tvg-name="Family Series" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181791.mkv
#EXTINF:-1 tvg-id="34" tvg-name="Kids Movie" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200598.mp4
#EXTINF:-1 tvg-id="35" tvg-name="Action Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200599.mp4
#EXTINF:-1 tvg-id="36" tvg-name="Comedy Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181792.mkv
#EXTINF:-1 tvg-id="37" tvg-name="Drama Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200600.mp4
#EXTINF:-1 tvg-id="38" tvg-name="Thriller Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181793.mkv
#EXTINF:-1 tvg-id="39" tvg-name="Horror Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200601.mp4
#EXTINF:-1 tvg-id="40" tvg-name="Sci-Fi Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181794.mkv
#EXTINF:-1 tvg-id="41" tvg-name="Romance Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200602.mp4
#EXTINF:-1 tvg-id="42" tvg-name="Fantasy Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181795.mkv
#EXTINF:-1 tvg-id="43" tvg-name="Adventure Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200603.mp4
#EXTINF:-1 tvg-id="44" tvg-name="Crime Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181796.mkv
#EXTINF:-1 tvg-id="45" tvg-name="Mystery Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200604.mp4
#EXTINF:-1 tvg-id="46" tvg-name="Documentary Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181797.mkv
#EXTINF:-1 tvg-id="47" tvg-name="Family Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200605.mp4
#EXTINF:-1 tvg-id="48" tvg-name="Kids Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181798.mkv
#EXTINF:-1 tvg-id="49" tvg-name="Action Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181799.mkv
#EXTINF:-1 tvg-id="50" tvg-name="Comedy Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200606.mp4
#EXTINF:-1 tvg-id="51" tvg-name="Drama Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181800.mkv
#EXTINF:-1 tvg-id="52" tvg-name="Thriller Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200607.mp4
#EXTINF:-1 tvg-id="53" tvg-name="Horror Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181801.mkv
#EXTINF:-1 tvg-id="54" tvg-name="Sci-Fi Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200608.mp4
#EXTINF:-1 tvg-id="55" tvg-name="Romance Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181802.mkv
#EXTINF:-1 tvg-id="56" tvg-name="Fantasy Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200609.mp4
#EXTINF:-1 tvg-id="57" tvg-name="Adventure Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181803.mkv
#EXTINF:-1 tvg-id="58" tvg-name="Crime Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200610.mp4
#EXTINF:-1 tvg-id="59" tvg-name="Mystery Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181804.mkv
#EXTINF:-1 tvg-id="60" tvg-name="Documentary Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200611.mp4
#EXTINF:-1 tvg-id="61" tvg-name="Family Series 2" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181805.mkv
#EXTINF:-1 tvg-id="62" tvg-name="Kids Movie 2" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200612.mp4
#EXTINF:-1 tvg-id="63" tvg-name="Action Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200613.mp4
#EXTINF:-1 tvg-id="64" tvg-name="Comedy Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181806.mkv
#EXTINF:-1 tvg-id="65" tvg-name="Drama Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200614.mp4
#EXTINF:-1 tvg-id="66" tvg-name="Thriller Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181807.mkv
#EXTINF:-1 tvg-id="67" tvg-name="Horror Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200615.mp4
#EXTINF:-1 tvg-id="68" tvg-name="Sci-Fi Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181808.mkv
#EXTINF:-1 tvg-id="69" tvg-name="Romance Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200616.mp4
#EXTINF:-1 tvg-id="70" tvg-name="Fantasy Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181809.mkv
#EXTINF:-1 tvg-id="71" tvg-name="Adventure Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200617.mp4
#EXTINF:-1 tvg-id="72" tvg-name="Crime Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181810.mkv
#EXTINF:-1 tvg-id="73" tvg-name="Mystery Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200618.mp4
#EXTINF:-1 tvg-id="74" tvg-name="Documentary Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181811.mkv
#EXTINF:-1 tvg-id="75" tvg-name="Family Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200619.mp4
#EXTINF:-1 tvg-id="76" tvg-name="Kids Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181812.mkv
#EXTINF:-1 tvg-id="77" tvg-name="Action Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181813.mkv
#EXTINF:-1 tvg-id="78" tvg-name="Comedy Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200620.mp4
#EXTINF:-1 tvg-id="79" tvg-name="Drama Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181814.mkv
#EXTINF:-1 tvg-id="80" tvg-name="Thriller Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200621.mp4
#EXTINF:-1 tvg-id="81" tvg-name="Horror Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181815.mkv
#EXTINF:-1 tvg-id="82" tvg-name="Sci-Fi Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200622.mp4
#EXTINF:-1 tvg-id="83" tvg-name="Romance Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181816.mkv
#EXTINF:-1 tvg-id="84" tvg-name="Fantasy Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200623.mp4
#EXTINF:-1 tvg-id="85" tvg-name="Adventure Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181817.mkv
#EXTINF:-1 tvg-id="86" tvg-name="Crime Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200624.mp4
#EXTINF:-1 tvg-id="87" tvg-name="Mystery Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181818.mkv
#EXTINF:-1 tvg-id="88" tvg-name="Documentary Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200625.mp4
#EXTINF:-1 tvg-id="89" tvg-name="Family Series 3" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181819.mkv
#EXTINF:-1 tvg-id="90" tvg-name="Kids Movie 3" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200626.mp4
#EXTINF:-1 tvg-id="91" tvg-name="Action Movie 4" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200627.mp4
#EXTINF:-1 tvg-id="92" tvg-name="Comedy Series 4" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181820.mkv
#EXTINF:-1 tvg-id="93" tvg-name="Drama Movie 4" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200628.mp4
#EXTINF:-1 tvg-id="94" tvg-name="Thriller Series 4" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181821.mkv
#EXTINF:-1 tvg-id="95" tvg-name="Horror Movie 4" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200629.mp4
#EXTINF:-1 tvg-id="96" tvg-name="Sci-Fi Series 4" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181822.mkv
#EXTINF:-1 tvg-id="97" tvg-name="Romance Movie 4" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200630.mp4
#EXTINF:-1 tvg-id="98" tvg-name="Fantasy Series 4" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181823.mkv
#EXTINF:-1 tvg-id="99" tvg-name="Adventure Movie 4" tvg-logo="" group-title="Movies",
http://1tv41.icu:8080/movie/4KCwCN/506843/200631.mp4
#EXTINF:-1 tvg-id="100" tvg-name="Crime Series 4" tvg-logo="" group-title="TV Series",
http://1tv41.icu:8080/series/4KCwCN/506843/181824.mkv"""

class EmbeddedHDHomeRunHandler(BaseHTTPRequestHandler):
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
            <title>Embedded IPTV Tuner</title>
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
                <h1>🎉 Embedded IPTV Tuner is Live!</h1>
                <p class="status">✅ HDHomeRun Emulator Running Successfully</p>
                <p><strong>Your Plex URL:</strong></p>
                <div class="url">https://iptv-tuner.onrender.com</div>
                <p><strong>Available Endpoints:</strong></p>
                <ul>
                    <li><a href="/discover.json">/discover.json</a> - Device discovery</li>
                    <li><a href="/lineup.json">/lineup.json</a> - Channel lineup (100 channels)</li>
                    <li><a href="/lineup_status.json">/lineup_status.json</a> - Status</li>
                </ul>
                <p><strong>For Plex:</strong> Add this URL to Plex Live TV & DVR settings</p>
                <p><strong>Channels:</strong> 100 Movies & TV Series ready to watch!</p>
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
            "FriendlyName": "Embedded IPTV Tuner",
            "Manufacturer": "Silicondust",
            "ModelNumber": "HDHR4-2US",
            "FirmwareName": "hdhomerun4_atsc",
            "FirmwareVersion": "20200101",
            "DeviceID": "12345678",
            "DeviceAuth": "test1234",
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
        
        # Parse the embedded playlist
        lineup = self.parse_m3u_to_lineup(EMBEDDED_PLAYLIST)
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
                
                # Get URL from next line
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith("http"):
                        lineup.append({
                            "GuideNumber": str(channel_num),
                            "GuideName": name,
                            "URL": url
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
            
            # Find the actual URL from embedded playlist
            stream_url = ""
            lines = EMBEDDED_PLAYLIST.splitlines()
            current_channel_num = 1
            
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    if current_channel_num == channel_number:
                        if i + 1 < len(lines):
                            stream_url = lines[i + 1].strip()
                        break
                    current_channel_num += 1

            if stream_url:
                self.send_response(302)  # Found
                self.send_header('Location', stream_url)
                self.end_headers()
            else:
                self.send_error(404, "Channel Not Found")
        else:
            self.send_error(404, "Invalid Stream Request")

def run_embedded_tuner(host='0.0.0.0', port=None):
    """Starts the embedded HDHomeRun emulator server."""
    if port is None:
        port = int(os.environ.get('PORT', 10000))
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, EmbeddedHDHomeRunHandler)
    
    print(f"🎬 Starting Embedded IPTV Tuner for Plex")
    print(f"============================================================")
    print(f"🚀 Embedded Tuner started on port {port}")
    print(f"📡 Plex can now detect this as an HDHomeRun device")
    print(f"🔗 Add this URL in Plex: https://iptv-tuner.onrender.com")
    print(f"📺 Embedded playlist: 100 channels ready")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print(f"============================================================")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Embedded IPTV Tuner.")
        httpd.server_close()

if __name__ == "__main__":
    run_embedded_tuner()
