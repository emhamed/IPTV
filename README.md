# 🎬 IPTV Server Project

A complete IPTV server solution with 49,000+ channels, movies, and TV shows. This project provides a web-based IPTV server with playlist management, content importers, and multiple player options.

## 🚀 Features

- **49,000+ IPTV Channels** - Live TV, movies, and TV shows
- **Web Dashboard** - Browse and manage your content
- **Multiple Players** - Web player, embeddable player, and Plex integration
- **Content Importers** - Import from various IPTV sources
- **GitHub Pages Hosting** - Access your playlist from anywhere
- **Plex Integration** - Works with Plex Media Server

## 📁 Project Structure

```
├── src/
│   ├── core/                 # Core server files
│   │   ├── main.py          # FastAPI server
│   │   ├── content_manager.py # Database management
│   │   └── config.json      # Configuration
│   ├── importers/           # Content import scripts
│   │   ├── import_specific_source.py
│   │   └── import_xtream_codes.py
│   ├── players/             # Web players
│   │   ├── web_player.html
│   │   ├── embed_player.html
│   │   └── templates/       # HTML templates
│   └── utils/               # Utility scripts
│       └── hdhomerun_emulator.py
├── playlists/               # M3U playlists
│   └── master_playlist.m3u  # Main playlist (49,000+ channels)
├── static/                  # Static assets
├── docs/                    # Documentation
└── index.html              # GitHub Pages homepage
```

## 🎯 Quick Start

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python src/core/main.py
```

### 2. Access Your Content
- **Web Dashboard**: http://localhost:8000
- **Playlist**: http://localhost:8000/playlist.m3u
- **Web Player**: http://localhost:8000/web_player.html

### 3. GitHub Pages (Public Access)
Your playlist is available at:
```
https://emhamed.github.io/IPTV/playlist.m3u
```

## 🎮 Using on PlayStation 5

### Method 1: IPTV Apps
1. Download **IPTV Smarters Pro** from PlayStation Store
2. Add playlist: `https://emhamed.github.io/IPTV/playlist.m3u`
3. Enjoy 49,000+ channels!

### Method 2: VLC Media Player
1. Download **VLC** from PlayStation Store
2. Open Network Stream: `https://emhamed.github.io/IPTV/playlist.m3u`
3. Browse and watch!

## 🏠 Plex Integration

### Setup with Plex
1. Install **Plex Media Server** on your computer
2. Run the HDHomeRun emulator:
   ```bash
   python src/utils/hdhomerun_emulator.py
   ```
3. In Plex, go to **Live TV & DVR**
4. Add HDHomeRun device: `http://localhost:6077`
5. Access via Plex app on PS5

## 📊 Content Statistics

- **Total Channels**: 49,258
- **Movies**: 15,000+
- **TV Shows**: 8,000+
- **Live TV**: 26,000+
- **Categories**: Movies, TV Series, Live TV, Sports, News, Music

## 🔧 Content Management

### Import New Content
```bash
# Import from Xtream Codes
python src/importers/import_xtream_codes.py

# Import specific source
python src/importers/import_specific_source.py
```

### Generate Playlists
The server automatically generates organized playlists:
- `master_playlist.m3u` - All content
- `movies.m3u` - Movies only
- `series.m3u` - TV shows only
- `live.m3u` - Live TV only

## 🌐 Web Interface

### Dashboard Features
- Browse all channels and content
- Search and filter by category
- Integrated video player
- Statistics and analytics
- Content management tools

### Player Options
- **Web Player**: Full-featured player with HLS support
- **Embed Player**: Widget for embedding in other sites
- **Mobile Responsive**: Works on all devices

## 📱 Mobile Access

Access your IPTV server from any device:
- **iPhone/Android**: Use VLC or IPTV apps
- **Smart TV**: Use built-in IPTV players
- **Computer**: Use VLC or web browser
- **Gaming Consoles**: Use IPTV apps

## 🔒 Security & Privacy

- All content is streamed directly from source
- No content is stored on our servers
- Your playlist is public but secure
- No personal data collection

## 🛠️ Technical Details

### Server Requirements
- Python 3.8+
- FastAPI
- SQLite database
- 2GB+ RAM recommended

### Supported Formats
- M3U playlists
- HLS streams (.m3u8)
- MPEG-TS streams
- Various codecs (H.264, H.265, etc.)

## 📞 Support

For issues or questions:
1. Check the documentation in `/docs`
2. Review the code in `/src`
3. Test with the provided playlists

## 🎉 Enjoy Your IPTV Server!

You now have access to 49,000+ channels, movies, and TV shows. The server works locally and is also hosted on GitHub Pages for global access.

**Happy Streaming!** 🎬📺