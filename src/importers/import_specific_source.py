#!/usr/bin/env python3
"""
Import from the specific IPTV source provided
"""
from content_manager import ContentManager
import requests
import time
import re

def main():
    manager = ContentManager()
    
    print("🧹 Clearing all content...")
    manager.clear_all_content()
    
    # The specific source provided
    source_url = "http://1tv41.icu:8080/get.php?username=4KCwCN&password=506843&type=m3u"
    
    print(f"🎬 Importing from: {source_url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(source_url, timeout=30)
        response.raise_for_status()
        
        if not response.text.strip().startswith('#EXTM3U'):
            print(f"❌ Not a valid M3U playlist")
            return
        
        print(f"📺 Got M3U playlist with {len(response.text.splitlines())} lines")
        
        # Parse and import content
        lines = response.text.split('\n')
        current_channel = None
        imported_count = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # Parse channel info
                attrs = {}
                attr_pattern = r'(\w+)="([^"]*)"'
                for match in re.finditer(attr_pattern, line):
                    attrs[match.group(1)] = match.group(2)
                
                parts = line.split(',')
                if len(parts) > 1:
                    current_channel = {
                        'name': parts[-1].strip(),
                        'tvg_id': attrs.get('tvg-id', ''),
                        'tvg_name': attrs.get('tvg-name', ''),
                        'logo': attrs.get('tvg-logo', ''),
                        'group_title': attrs.get('group-title', '')
                    }
            
            elif line and not line.startswith('#') and current_channel:
                # This is the URL - add to database
                category = "IPTV Source"
                
                manager.add_channel({
                    "name": current_channel['name'],
                    "url": line,
                    "logo": current_channel.get('logo', ''),
                    "category": category,
                    "tvg_id": current_channel.get('tvg_id', ''),
                    "tvg_name": current_channel.get('tvg_name', current_channel['name']),
                    "group_title": current_channel.get('group_title', category)
                })
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"📊 Imported {imported_count} items...")
                
                current_channel = None
        
        print(f"✅ Imported {imported_count} items")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # Show statistics
    stats = manager.get_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"  • Total Channels: {stats['total_channels']}")
    print(f"  • Total Movies: {stats['total_movies']}")
    print(f"  • Total TV Shows: {stats['total_shows']}")
    
    # Create organized playlists
    print("\n📁 Creating organized playlists...")
    
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    
    # Get all channels
    cursor.execute("SELECT name, url, logo, tvg_id, tvg_name, group_title FROM channels WHERE is_active = 1")
    all_channels = cursor.fetchall()
    
    # Create master playlist
    with open('master_playlist.m3u', 'w') as f:
        f.write('#EXTM3U\n')
        f.write('# IPTV Source: 1tv41.icu\n')
        f.write('# Username: 4KCwCN\n')
        f.write('# Total Channels: {}\n'.format(len(all_channels)))
        f.write('\n')
        
        for channel in all_channels:
            name, url, logo, tvg_id, tvg_name, group_title = channel
            f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group_title}",{name}\n')
            f.write(f'{url}\n')
    
    print(f"✅ Created master_playlist.m3u with {len(all_channels)} items")
    
    # Create category-specific playlists
    cursor.execute("SELECT DISTINCT group_title FROM channels WHERE is_active = 1 AND group_title != ''")
    categories = cursor.fetchall()
    
    for (category,) in categories:
        if category:
            cursor.execute("SELECT name, url, logo, tvg_id, tvg_name, group_title FROM channels WHERE group_title = ? AND is_active = 1", (category,))
            category_channels = cursor.fetchall()
            
            playlist_name = f"{category.lower().replace(' ', '_').replace('-', '_').replace('/', '_')}.m3u"
            
            with open(playlist_name, 'w') as f:
                f.write('#EXTM3U\n')
                f.write(f'# Category: {category}\n')
                f.write(f'# Total Channels: {len(category_channels)}\n')
                f.write('\n')
                
                for channel in category_channels:
                    name, url, logo, tvg_id, tvg_name, group_title = channel
                    f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group_title}",{name}\n')
                    f.write(f'{url}\n')
            
            print(f"✅ Created {playlist_name} with {len(category_channels)} items")
    
    conn.close()
    
    print(f"\n🔗 Your IBO Player Links:")
    print(f"  • Master Playlist: http://192.168.2.181:8080/master_playlist.m3u")
    
    for (category,) in categories:
        if category:
            playlist_name = f"{category.lower().replace(' ', '_').replace('-', '_').replace('/', '_')}.m3u"
            print(f"  • {category}: http://192.168.2.181:8080/{playlist_name}")
    
    print(f"\n🎯 For IBO Player, use this main link:")
    print(f"http://192.168.2.181:8080/master_playlist.m3u")
    
    print(f"\n📺 Source Information:")
    print(f"  • Provider: 1tv41.icu")
    print(f"  • Username: 4KCwCN")
    print(f"  • Status: Active")
    print(f"  • Expires: 29/12/2025")
    print(f"  • Total Channels: {len(all_channels)}")

if __name__ == "__main__":
    main()
