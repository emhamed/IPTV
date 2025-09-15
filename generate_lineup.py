#!/usr/bin/env python3
"""
Generate HDHomeRun lineup.json from M3U playlist for GitHub Pages
"""

import json
import re

def parse_m3u_to_lineup(m3u_file, output_file):
    """Parse M3U file and create HDHomeRun lineup.json"""
    print(f"📺 Parsing {m3u_file}...")
    
    channels = []
    channel_id = 1
    
    try:
        with open(m3u_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXTINF:'):
                # Extract channel name
                name_match = re.search(r',(.+)$', line)
                name = name_match.group(1).strip() if name_match else f"Channel {channel_id}"
                
                # Get URL from next line
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith('http'):
                        # Clean up channel name for HDHomeRun
                        clean_name = re.sub(r'[^\w\s-]', '', name)[:50]  # Limit length and remove special chars
                        
                        channel = {
                            "GuideNumber": str(channel_id),
                            "GuideName": clean_name,
                            "URL": url,
                            "HD": 1
                        }
                        channels.append(channel)
                        channel_id += 1
                        i += 1  # Skip URL line
            i += 1
        
        print(f"✅ Found {len(channels)} channels")
        
        # Write lineup.json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(channels, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Created {output_file} with {len(channels)} channels")
        
        # Also create a summary
        print(f"\n📊 Channel Summary:")
        print(f"  • Total Channels: {len(channels)}")
        print(f"  • First 5 channels:")
        for i, channel in enumerate(channels[:5]):
            print(f"    {i+1}. {channel['GuideName']}")
        
        return len(channels)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def main():
    print("🎬 Generating HDHomeRun lineup for GitHub Pages...")
    print("=" * 50)
    
    # Parse the playlist
    channel_count = parse_m3u_to_lineup('playlists/master_playlist.m3u', 'lineup.json')
    
    if channel_count > 0:
        print(f"\n🎉 Success! Generated lineup.json with {channel_count} channels")
        print("\n🔗 For Plex, use this URL:")
        print("https://emhamed.github.io/IPTV/")
        print("\n📋 Plex will detect:")
        print("  • discover.json - Device info")
        print("  • lineup.json - Channel list")
        print("  • lineup_status.json - Status info")
    else:
        print("❌ Failed to generate lineup")

if __name__ == "__main__":
    main()
