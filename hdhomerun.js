// HDHomeRun Emulator for GitHub Pages
// This creates a simple HDHomeRun-compatible API that Plex can detect

const PLAYLIST_URL = 'https://emhamed.github.io/IPTV/playlist.m3u';

// Simple HTTP server simulation using GitHub Pages
class HDHomeRunEmulator {
    constructor() {
        this.channels = [];
        this.loadChannels();
    }

    async loadChannels() {
        try {
            const response = await fetch(PLAYLIST_URL);
            const m3uContent = await response.text();
            this.parseM3U(m3uContent);
            console.log(`Loaded ${this.channels.length} channels`);
        } catch (error) {
            console.error('Error loading playlist:', error);
        }
    }

    parseM3U(content) {
        const lines = content.split('\n');
        let currentChannel = null;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (line.startsWith('#EXTINF:')) {
                const nameMatch = line.match(/,(.+)$/);
                const name = nameMatch ? nameMatch[1] : `Channel ${this.channels.length + 1}`;
                
                currentChannel = {
                    name: name,
                    url: '',
                    id: this.channels.length + 1
                };
            } else if (line.startsWith('http') && currentChannel) {
                currentChannel.url = line;
                this.channels.push(currentChannel);
                currentChannel = null;
            }
        }
    }

    // HDHomeRun API endpoints
    getDiscover() {
        return {
            "FriendlyName": "IPTV Tuner",
            "ModelNumber": "HDTC-2US",
            "FirmwareName": "hdhomerun_cablecard",
            "FirmwareVersion": "20200101",
            "DeviceID": "12345678",
            "DeviceAuth": "test1234",
            "BaseURL": "https://emhamed.github.io/IPTV/",
            "LineupURL": "https://emhamed.github.io/IPTV/lineup.json"
        };
    }

    getLineup() {
        return this.channels.map((channel, index) => ({
            "GuideNumber": (index + 1).toString(),
            "GuideName": channel.name,
            "URL": channel.url,
            "HD": 1
        }));
    }

    getLineupStatus() {
        return {
            "ScanInProgress": 0,
            "ScanPossible": 1,
            "Source": "Antenna",
            "SourceList": ["Antenna"]
        };
    }
}

// Create global instance
const hdhomerun = new HDHomeRunEmulator();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = hdhomerun;
}
