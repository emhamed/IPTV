#!/usr/bin/env python3
"""
Import IPTV channels from Xtream codes found on world-iptv.club
"""

import sqlite3
import requests
import re
from content_manager import ContentManager
import time

def clear_all_content():
    """Clear all existing channels, movies, and shows"""
    print("🗑️  Clearing all existing content...")
    
    conn = sqlite3.connect('iptv_content.db')
    cursor = conn.cursor()
    
    # Clear all tables
    cursor.execute("DELETE FROM channels")
    cursor.execute("DELETE FROM movies") 
    cursor.execute("DELETE FROM shows")
    cursor.execute("DELETE FROM episodes")
    
    conn.commit()
    conn.close()
    
    print("✅ All content cleared successfully!")

def get_xtream_codes():
    """Extract Xtream codes from the page"""
    url = "https://world-iptv.club/xtream-codes-iptv-2025-m3u-playlist-newkalaplay-xyz/"
    
    print(f"🌐 Fetching Xtream codes from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        text_content = response.text
        
        # Find Xtream code URLs (handle HTML encoding)
        xtream_pattern = r'http://newkalaplay\.xyz:8080/get\.php\?username=[^&\s]+&amp;password=[^&\s]+&amp;type=m3u_plus'
        xtream_urls = re.findall(xtream_pattern, text_content)
        
        # Decode HTML entities
        xtream_urls = [url.replace('&amp;', '&') for url in xtream_urls]
        
        # Remove duplicates
        xtream_urls = list(set(xtream_urls))
        
        print(f"📋 Found {len(xtream_urls)} Xtream codes")
        return xtream_urls
        
    except Exception as e:
        print(f"❌ Error fetching Xtream codes: {str(e)}")
        return []

def import_from_xtream_code(xtream_url, manager):
    """Import channels from a single Xtream code"""
    try:
        print(f"📥 Fetching playlist from: {xtream_url[:80]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(xtream_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # Parse M3U content
            channels_imported = parse_m3u_content(content, manager)
            print(f"   ✅ Imported {channels_imported} channels")
            return channels_imported
        else:
            print(f"   ❌ Failed to fetch playlist (Status: {response.status_code})")
            return 0
            
    except Exception as e:
        print(f"   ❌ Error importing from Xtream code: {str(e)}")
        return 0

def parse_m3u_content(content, manager):
    """Parse M3U content and add channels to database"""
    channels_imported = 0
    lines = content.strip().split('\n')
    
    current_channel = {}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('#EXTINF:'):
            # Parse channel info
            info = line[8:]  # Remove #EXTINF:
            
            # Extract attributes
            attrs = {}
            if ',' in info:
                attrs_str, name = info.rsplit(',', 1)
                attrs_str = attrs_str.strip()
                name = name.strip()
                
                # Parse attributes
                for attr in attrs_str.split(' '):
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attrs[key] = value.strip('"')
                
                current_channel = {
                    'name': name,
                    'url': '',
                    'logo': attrs.get('tvg-logo', ''),
                    'group': attrs.get('group-title', 'General'),
                    'category': attrs.get('group-title', 'General'),
                    'country': attrs.get('tvg-country', 'US'),
                    'language': attrs.get('tvg-language', 'en'),
                    'tvg_id': attrs.get('tvg-id', ''),
                    'tvg_name': attrs.get('tvg-name', name)
                }
        
        elif line and not line.startswith('#') and current_channel:
            # This is the stream URL
            current_channel['url'] = line
            
            # Add channel to database
            try:
                manager.add_channel(current_channel)
                channels_imported += 1
            except Exception as e:
                print(f"   ⚠️  Error adding channel {current_channel['name']}: {str(e)}")
            
            current_channel = {}
    
    return channels_imported

def main():
    """Main function"""
    print("🚀 Starting Xtream codes import process...")
    
    # Step 1: Clear all existing content
    clear_all_content()
    
    # Step 2: Get Xtream codes
    xtream_urls = get_xtream_codes()
    
    if not xtream_urls:
        print("❌ No Xtream codes found!")
        return
    
    # Step 3: Import from Xtream codes
    manager = ContentManager()
    total_imported = 0
    successful_imports = 0
    
    # Limit to first 10 Xtream codes to avoid overwhelming the system
    for i, xtream_url in enumerate(xtream_urls[:10]):
        print(f"\n📺 Processing Xtream code {i+1}/10")
        
        channels_imported = import_from_xtream_code(xtream_url, manager)
        total_imported += channels_imported
        
        if channels_imported > 0:
            successful_imports += 1
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
    
    print(f"\n🎉 Import completed!")
    print(f"📊 Statistics:")
    print(f"   📺 Total channels imported: {total_imported}")
    print(f"   ✅ Successful Xtream codes: {successful_imports}/10")
    
    # Show final statistics
    stats = manager.get_statistics()
    print(f"   📺 Total channels in database: {stats['total_channels']}")
    print(f"   🎬 Movies: {stats['total_movies']}")
    print(f"   📺 Shows: {stats['total_shows']}")

if __name__ == "__main__":
    main()
