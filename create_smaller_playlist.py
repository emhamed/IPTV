#!/usr/bin/env python3
"""
Create a smaller playlist for Plex compatibility
"""
import requests
import re

def create_smaller_playlist():
    """Create a smaller playlist with top channels for Plex"""
    print("🎬 Creating smaller playlist for Plex compatibility...")
    
    # Read the full playlist from local file
    try:
        with open('playlist.m3u', 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        
        # Filter for top channels (limit to 1000)
        filtered_lines = []
        channel_count = 0
        max_channels = 1000
        
        i = 0
        while i < len(lines) and channel_count < max_channels:
            line = lines[i].strip()
            if line.startswith("#EXTINF:"):
                # Check if this is a good channel
                if is_good_channel(line):
                    filtered_lines.append(line)
                    if i + 1 < len(lines):
                        filtered_lines.append(lines[i + 1])
                        channel_count += 1
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        
        # Write smaller playlist
        with open('smaller_playlist.m3u', 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write('# Smaller playlist for Plex compatibility\n')
            f.write(f'# Total Channels: {channel_count}\n\n')
            for line in filtered_lines:
                f.write(line + '\n')
        
        print(f"✅ Created smaller_playlist.m3u with {channel_count} channels")
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def is_good_channel(extinf_line):
    """Check if this is a good channel to include"""
    # Look for popular content keywords
    good_keywords = [
        'netflix', 'hbo', 'disney', 'apple', 'prime', 'bbc', 'cnn', 'espn',
        'fox', 'abc', 'cbs', 'nbc', 'hulu', 'paramount', 'showtime',
        'starz', 'amc', 'fx', 'tnt', 'tbs', 'comedy', 'national geographic',
        'discovery', 'history', 'a&e', 'lifetime', 'hallmark', 'syfy',
        'bravo', 'e!', 'mtv', 'vh1', 'bet', 'nickelodeon', 'cartoon',
        'adult swim', 'cn', 'disney channel', 'disney xd', 'freeform'
    ]
    
    line_lower = extinf_line.lower()
    
    # Check for good keywords
    for keyword in good_keywords:
        if keyword in line_lower:
            return True
    
    # Check for movie/series indicators
    if any(word in line_lower for word in ['movie', 'film', 'series', 'show', 'tv']):
        return True
    
    # Check for HD quality
    if 'hd' in line_lower or '1080' in line_lower or '720' in line_lower:
        return True
    
    return False

if __name__ == "__main__":
    create_smaller_playlist()
