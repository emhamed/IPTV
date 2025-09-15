#!/usr/bin/env python3
"""
IPTV Content Manager
Manages TV channels, movies, and shows for the IPTV server
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib
import mimetypes

class ContentManager:
    def __init__(self, db_path: str = "iptv_content.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for content management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Channels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                logo TEXT,
                category TEXT,
                language TEXT,
                country TEXT,
                tvg_id TEXT,
                tvg_name TEXT,
                group_title TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                year INTEGER,
                genre TEXT,
                description TEXT,
                poster TEXT,
                duration INTEGER,
                file_size INTEGER,
                file_hash TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Shows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER,
                genre TEXT,
                description TEXT,
                poster TEXT,
                total_seasons INTEGER,
                total_episodes INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Episodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                show_id INTEGER,
                season_number INTEGER,
                episode_number INTEGER,
                title TEXT,
                file_path TEXT NOT NULL,
                duration INTEGER,
                file_size INTEGER,
                file_hash TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (show_id) REFERENCES shows (id)
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('News', 'News and current affairs'),
            ('Sports', 'Sports channels and events'),
            ('Entertainment', 'Entertainment and variety shows'),
            ('Documentary', 'Documentary and educational content'),
            ('Kids', 'Children\'s programming'),
            ('Movies', 'Movie channels'),
            ('Music', 'Music channels'),
            ('General', 'General programming')
        ]
        
        for category in default_categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', category)
        
        conn.commit()
        conn.close()
    
    def add_channel(self, channel_data: Dict) -> int:
        """Add a new channel to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO channels (name, url, logo, category, language, country, tvg_id, tvg_name, group_title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            channel_data['name'],
            channel_data['url'],
            channel_data.get('logo', ''),
            channel_data.get('category', 'General'),
            channel_data.get('language', 'en'),
            channel_data.get('country', 'US'),
            channel_data.get('tvg_id', ''),
            channel_data.get('tvg_name', ''),
            channel_data.get('group_title', '')
        ))
        
        channel_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return channel_id
    
    def add_movie(self, movie_data: Dict) -> int:
        """Add a new movie to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate file hash and size if file exists
        file_hash = ""
        file_size = 0
        if os.path.exists(movie_data['file_path']):
            file_hash = self._calculate_file_hash(movie_data['file_path'])
            file_size = os.path.getsize(movie_data['file_path'])
        
        cursor.execute('''
            INSERT INTO movies (title, file_path, year, genre, description, poster, duration, file_size, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            movie_data['title'],
            movie_data['file_path'],
            movie_data.get('year'),
            movie_data.get('genre', ''),
            movie_data.get('description', ''),
            movie_data.get('poster', ''),
            movie_data.get('duration', 0),
            file_size,
            file_hash
        ))
        
        movie_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return movie_id
    
    def add_show(self, show_data: Dict) -> int:
        """Add a new TV show to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shows (title, year, genre, description, poster, total_seasons, total_episodes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            show_data['title'],
            show_data.get('year'),
            show_data.get('genre', ''),
            show_data.get('description', ''),
            show_data.get('poster', ''),
            show_data.get('total_seasons', 0),
            show_data.get('total_episodes', 0)
        ))
        
        show_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return show_id
    
    def add_episode(self, episode_data: Dict) -> int:
        """Add a new episode to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate file hash and size if file exists
        file_hash = ""
        file_size = 0
        if os.path.exists(episode_data['file_path']):
            file_hash = self._calculate_file_hash(episode_data['file_path'])
            file_size = os.path.getsize(episode_data['file_path'])
        
        cursor.execute('''
            INSERT INTO episodes (show_id, season_number, episode_number, title, file_path, duration, file_size, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            episode_data['show_id'],
            episode_data['season_number'],
            episode_data['episode_number'],
            episode_data.get('title', ''),
            episode_data['file_path'],
            episode_data.get('duration', 0),
            file_size,
            file_hash
        ))
        
        episode_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return episode_id
    
    def get_channels(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """Get channels from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM channels"
        params = []
        
        conditions = []
        if active_only:
            conditions.append("is_active = 1")
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY name"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        channels = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return channels
    
    def get_movies(self, genre: str = None, active_only: bool = True) -> List[Dict]:
        """Get movies from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM movies"
        params = []
        
        conditions = []
        if active_only:
            conditions.append("is_active = 1")
        if genre:
            conditions.append("genre = ?")
            params.append(genre)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY title"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        movies = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return movies
    
    def get_shows(self, genre: str = None, active_only: bool = True) -> List[Dict]:
        """Get TV shows from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM shows"
        params = []
        
        conditions = []
        if active_only:
            conditions.append("is_active = 1")
        if genre:
            conditions.append("genre = ?")
            params.append(genre)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY title"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        shows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return shows
    
    def get_episodes(self, show_id: int, season: int = None) -> List[Dict]:
        """Get episodes for a specific show"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM episodes WHERE show_id = ? AND is_active = 1"
        params = [show_id]
        
        if season is not None:
            query += " AND season_number = ?"
            params.append(season)
        
        query += " ORDER BY season_number, episode_number"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        episodes = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return episodes
    
    def scan_directory(self, directory: str, content_type: str = "movies") -> List[Dict]:
        """Scan directory for media files and add to database"""
        media_files = []
        supported_formats = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in supported_formats:
                    if content_type == "movies":
                        # Extract movie info from filename
                        title = os.path.splitext(file)[0]
                        year = self._extract_year_from_filename(title)
                        
                        movie_data = {
                            'title': title,
                            'file_path': file_path,
                            'year': year,
                            'genre': 'Unknown'
                        }
                        media_files.append(movie_data)
                    
                    elif content_type == "shows":
                        # Extract show info from directory structure
                        # Expected: Show Name/Season XX/Episode XX - Title.ext
                        show_name = os.path.basename(root)
                        season_match = re.search(r'season\s*(\d+)', root, re.IGNORECASE)
                        episode_match = re.search(r'episode\s*(\d+)', file, re.IGNORECASE)
                        
                        if season_match and episode_match:
                            season_num = int(season_match.group(1))
                            episode_num = int(episode_match.group(1))
                            title = os.path.splitext(file)[0]
                            
                            episode_data = {
                                'show_name': show_name,
                                'season_number': season_num,
                                'episode_number': episode_num,
                                'title': title,
                                'file_path': file_path
                            }
                            media_files.append(episode_data)
        
        return media_files
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def _extract_year_from_filename(self, filename: str) -> Optional[int]:
        """Extract year from filename (e.g., 'Movie Name (2023)' -> 2023)"""
        import re
        year_match = re.search(r'\((\d{4})\)', filename)
        if year_match:
            return int(year_match.group(1))
        return None
    
    def clear_all_content(self):
        """Clear all content from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear all tables
        cursor.execute("DELETE FROM channels")
        cursor.execute("DELETE FROM movies")
        cursor.execute("DELETE FROM shows")
        cursor.execute("DELETE FROM episodes")
        cursor.execute("DELETE FROM categories")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('channels', 'movies', 'shows', 'episodes', 'categories')")
        
        conn.commit()
        conn.close()
        print("✅ All content cleared from database")

    def get_statistics(self) -> Dict:
        """Get content statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count channels
        cursor.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
        stats['total_channels'] = cursor.fetchone()[0]
        
        # Count movies (from channels table)
        cursor.execute("SELECT COUNT(*) FROM channels WHERE url LIKE '%/movie/%' AND is_active = 1")
        stats['total_movies'] = cursor.fetchone()[0]
        
        # Count shows/series (from channels table)
        cursor.execute("SELECT COUNT(*) FROM channels WHERE url LIKE '%/series/%' AND is_active = 1")
        stats['total_shows'] = cursor.fetchone()[0]
        
        # Count episodes
        cursor.execute("SELECT COUNT(*) FROM episodes WHERE is_active = 1")
        stats['total_episodes'] = cursor.fetchone()[0]
        
        # Total storage used
        cursor.execute("SELECT SUM(file_size) FROM movies WHERE is_active = 1")
        movie_size = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(file_size) FROM episodes WHERE is_active = 1")
        episode_size = cursor.fetchone()[0] or 0
        
        stats['total_storage_gb'] = round((movie_size + episode_size) / (1024**3), 2)
        
        conn.close()
        return stats

def main():
    """Example usage"""
    manager = ContentManager()
    
    # Add sample channels
    sample_channels = [
        {
            'name': 'CNN',
            'url': 'http://example.com/cnn.m3u8',
            'category': 'News',
            'country': 'US',
            'tvg_id': 'cnn',
            'tvg_name': 'CNN'
        },
        {
            'name': 'BBC One',
            'url': 'http://example.com/bbc1.m3u8',
            'category': 'Entertainment',
            'country': 'UK',
            'tvg_id': 'bbc_one',
            'tvg_name': 'BBC One'
        }
    ]
    
    for channel in sample_channels:
        channel_id = manager.add_channel(channel)
        print(f"Added channel: {channel['name']} (ID: {channel_id})")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"\nStatistics:")
    print(f"Channels: {stats['total_channels']}")
    print(f"Movies: {stats['total_movies']}")
    print(f"Shows: {stats['total_shows']}")
    print(f"Episodes: {stats['total_episodes']}")
    print(f"Storage: {stats['total_storage_gb']} GB")

if __name__ == "__main__":
    main()
