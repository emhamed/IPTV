#!/usr/bin/env python3
"""
IPTV Server - A comprehensive IPTV streaming server
Supports 2000+ TV channels and 20,000+ movies/shows
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
import uvicorn
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IPTV Server",
    description="A comprehensive IPTV streaming server with 2000+ channels and 20,000+ movies/shows",
    version="1.0.0"
)

# Create necessary directories
BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media"
CHANNELS_DIR = MEDIA_DIR / "channels"
MOVIES_DIR = MEDIA_DIR / "movies"
SHOWS_DIR = MEDIA_DIR / "shows"
PLAYLISTS_DIR = BASE_DIR / "playlists"
EPG_DIR = BASE_DIR / "epg"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

for directory in [MEDIA_DIR, CHANNELS_DIR, MOVIES_DIR, SHOWS_DIR, PLAYLISTS_DIR, EPG_DIR, STATIC_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Global variables for content management
channels_db = []
movies_db = []
shows_db = []
playlists_db = []

class Channel:
    def __init__(self, name: str, url: str, logo: str = "", category: str = "General", 
                 language: str = "en", country: str = "US", tvg_id: str = "", 
                 tvg_name: str = "", group_title: str = ""):
        self.name = name
        self.url = url
        self.logo = logo
        self.category = category
        self.language = language
        self.country = country
        self.tvg_id = tvg_id or name.replace(" ", "_").lower()
        self.tvg_name = tvg_name or name
        self.group_title = group_title or category
        self.id = len(channels_db) + 1

class Movie:
    def __init__(self, title: str, file_path: str, year: int = None, genre: str = "", 
                 description: str = "", poster: str = "", duration: int = 0):
        self.title = title
        self.file_path = file_path
        self.year = year
        self.genre = genre
        self.description = description
        self.poster = poster
        self.duration = duration
        self.id = len(movies_db) + 1

class Show:
    def __init__(self, title: str, seasons: Dict, year: int = None, genre: str = "", 
                 description: str = "", poster: str = ""):
        self.title = title
        self.seasons = seasons  # {season_num: [episode_files]}
        self.year = year
        self.genre = genre
        self.description = description
        self.poster = poster
        self.id = len(shows_db) + 1

@app.get("/channels", response_class=HTMLResponse)
async def channels_page(request: Request):
    """Channels page showing all channels"""
    from content_manager import ContentManager
    manager = ContentManager()
    
    # Get all channels
    channels = manager.get_channels()
    
    return templates.TemplateResponse("channels.html", {
        "request": request,
        "channels": channels
    })

@app.get("/player", response_class=HTMLResponse)
async def web_player(request: Request):
    """Web-based IPTV player"""
    with open("web_player.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/embed", response_class=HTMLResponse)
async def embed_player(request: Request):
    """Embeddable IPTV player"""
    with open("embed_player.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/embed-code")
async def get_embed_code():
    """Get iframe embed code for websites"""
    embed_code = '''
    <!-- IPTV Player Embed Code -->
    <iframe 
        src="http://localhost:8000/embed" 
        width="800" 
        height="600" 
        frameborder="0" 
        allowfullscreen
        style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
    </iframe>
    
    <!-- Responsive version -->
    <div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%;">
        <iframe 
            src="http://localhost:8000/embed" 
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 10px;"
            frameborder="0" 
            allowfullscreen>
        </iframe>
    </div>
    '''
    
    return {"embed_code": embed_code, "iframe_url": "http://localhost:8000/embed"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    from content_manager import ContentManager
    manager = ContentManager()
    
    # Get statistics from database
    stats = manager.get_statistics()
    
    # Get recent content
    channels = manager.get_channels()[:20]  # Show more channels on dashboard
    movies = manager.get_movies()[:10]
    shows = manager.get_shows()[:10]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "channels": channels,
        "movies": movies,
        "shows": shows
    })

@app.get("/api/channels")
async def get_channels():
    """Get all channels"""
    from content_manager import ContentManager
    manager = ContentManager()
    channels = manager.get_channels()
    return {"channels": channels}

@app.get("/api/movies")
async def get_movies():
    """Get all movies"""
    from content_manager import ContentManager
    manager = ContentManager()
    movies = manager.get_movies()
    return {"movies": movies}

@app.get("/api/shows")
async def get_shows():
    """Get all shows"""
    from content_manager import ContentManager
    manager = ContentManager()
    shows = manager.get_shows()
    return {"shows": shows}

@app.post("/api/channels")
async def add_channel(channel_data: dict):
    """Add a new channel"""
    try:
        from content_manager import ContentManager
        manager = ContentManager()
        channel_id = manager.add_channel(channel_data)
        return {"message": "Channel added successfully", "channel_id": channel_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/movies")
async def add_movie(movie_data: dict):
    """Add a new movie"""
    try:
        from content_manager import ContentManager
        manager = ContentManager()
        movie_id = manager.add_movie(movie_data)
        return {"message": "Movie added successfully", "movie_id": movie_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/playlist.m3u")
async def get_playlist():
    """Generate M3U playlist for all channels"""
    from content_manager import ContentManager
    manager = ContentManager()
    channels = manager.get_channels()
    
    m3u_content = "#EXTM3U\n"
    
    for channel in channels:
        m3u_content += f'#EXTINF:-1 tvg-id="{channel["tvg_id"]}" tvg-name="{channel["tvg_name"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group_title"]}",{channel["name"]}\n'
        m3u_content += f"{channel['url']}\n"
    
    return StreamingResponse(
        iter([m3u_content]),
        media_type="application/vnd.apple.mpegurl",
        headers={"Content-Disposition": "attachment; filename=playlist.m3u"}
    )

@app.get("/epg.xml")
async def get_epg():
    """Generate EPG (Electronic Program Guide)"""
    from content_manager import ContentManager
    manager = ContentManager()
    channels = manager.get_channels()
    
    epg_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    epg_content += '<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
    epg_content += '<tv>\n'
    
    for channel in channels:
        epg_content += f'  <channel id="{channel["tvg_id"]}">\n'
        epg_content += f'    <display-name>{channel["name"]}</display-name>\n'
        epg_content += f'    <icon src="{channel["logo"]}"/>\n'
        epg_content += f'  </channel>\n'
    
    # Add sample programs (you can expand this with real EPG data)
    for channel in channels:
        epg_content += f'  <programme channel="{channel["tvg_id"]}" start="20240101000000 +0000" stop="20240101010000 +0000">\n'
        epg_content += f'    <title>Sample Program</title>\n'
        epg_content += f'    <desc>Sample program description</desc>\n'
        epg_content += f'  </programme>\n'
    
    epg_content += '</tv>\n'
    
    return StreamingResponse(
        iter([epg_content]),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=epg.xml"}
    )

@app.get("/stream/{content_type}/{content_id}")
async def stream_content(content_type: str, content_id: int):
    """Stream content (channels, movies, shows)"""
    if content_type == "channel":
        if content_id <= len(channels_db):
            channel = channels_db[content_id - 1]
            # For now, redirect to the channel URL
            # In a real implementation, you'd proxy the stream
            return {"redirect": channel.url}
    
    elif content_type == "movie":
        if content_id <= len(movies_db):
            movie = movies_db[content_id - 1]
            if os.path.exists(movie.file_path):
                return FileResponse(movie.file_path)
    
    elif content_type == "show":
        # This would need episode selection logic
        pass
    
    raise HTTPException(status_code=404, detail="Content not found")

@app.post("/api/import/playlist")
async def import_playlist(file_path: str, background_tasks: BackgroundTasks):
    """Import channels from an existing M3U playlist"""
    background_tasks.add_task(parse_m3u_playlist, file_path)
    return {"message": "Playlist import started"}

async def parse_m3u_playlist(file_path: str):
    """Parse M3U playlist and add channels to database"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        current_channel = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # Parse channel info
                info = line[8:]  # Remove '#EXTINF:'
                parts = info.split(',', 1)
                if len(parts) == 2:
                    attrs = parts[0]
                    name = parts[1]
                    
                    # Parse attributes
                    tvg_id = ""
                    tvg_name = ""
                    tvg_logo = ""
                    group_title = ""
                    
                    if 'tvg-id=' in attrs:
                        tvg_id = attrs.split('tvg-id="')[1].split('"')[0]
                    if 'tvg-name=' in attrs:
                        tvg_name = attrs.split('tvg-name="')[1].split('"')[0]
                    if 'tvg-logo=' in attrs:
                        tvg_logo = attrs.split('tvg-logo="')[1].split('"')[0]
                    if 'group-title=' in attrs:
                        group_title = attrs.split('group-title="')[1].split('"')[0]
                    
                    current_channel = {
                        "name": name,
                        "tvg_id": tvg_id,
                        "tvg_name": tvg_name,
                        "logo": tvg_logo,
                        "group_title": group_title
                    }
            
            elif line and not line.startswith('#') and current_channel:
                # This is the URL
                current_channel["url"] = line
                channel = Channel(**current_channel)
                channels_db.append(channel)
                current_channel = None
        
        logger.info(f"Imported {len([c for c in channels_db if c.url])} channels from playlist")
        
    except Exception as e:
        logger.error(f"Error parsing playlist: {e}")

@app.get("/api/stats")
async def get_stats():
    """Get server statistics"""
    from content_manager import ContentManager
    manager = ContentManager()
    stats = manager.get_statistics()
    stats.update({
        "server_uptime": "Running",
        "last_updated": datetime.now().isoformat()
    })
    return stats

if __name__ == "__main__":
    # Add some sample data for demonstration
    sample_channels = [
        {"name": "CNN", "url": "http://example.com/cnn.m3u8", "category": "News", "country": "US"},
        {"name": "BBC One", "url": "http://example.com/bbc1.m3u8", "category": "Entertainment", "country": "UK"},
        {"name": "Discovery", "url": "http://example.com/discovery.m3u8", "category": "Documentary", "country": "US"},
    ]
    
    for channel_data in sample_channels:
        channel = Channel(**channel_data)
        channels_db.append(channel)
    
    # Add sample movies
    sample_movies = [
        {"title": "The Matrix", "file_path": "/path/to/matrix.mp4", "year": 1999, "genre": "Action"},
        {"title": "Inception", "file_path": "/path/to/inception.mp4", "year": 2010, "genre": "Sci-Fi"},
    ]
    
    for movie_data in sample_movies:
        movie = Movie(**movie_data)
        movies_db.append(movie)
    
    print("Starting IPTV Server...")
    print(f"Dashboard: http://localhost:8000")
    print(f"Playlist: http://localhost:8000/playlist.m3u")
    print(f"EPG: http://localhost:8000/epg.xml")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
