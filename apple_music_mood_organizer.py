#!/usr/bin/env python3
"""
Apple Music Mood-Based Playlist Organizer
This script organizes your Apple Music library into playlists based on mood.
"""

import subprocess
import json
import re
from typing import List, Dict, Optional
from collections import defaultdict
import os

class AppleMusicOrganizer:
    def __init__(self):
        self.mood_categories = {
            'Happy': ['pop', 'dance', 'electronic', 'upbeat', 'happy', 'party', 'celebration'],
            'Sad': ['sad', 'ballad', 'slow', 'melancholic', 'emotional', 'depressing'],
            'Energetic': ['rock', 'metal', 'punk', 'energetic', 'intense', 'aggressive', 'fast'],
            'Chill': ['chill', 'ambient', 'lounge', 'relaxing', 'calm', 'peaceful', 'meditation'],
            'Romantic': ['romantic', 'love', 'soft', 'intimate', 'ballad'],
            'Motivational': ['motivational', 'inspirational', 'uplifting', 'workout', 'gym'],
            'Nostalgic': ['classic', 'vintage', 'retro', 'oldies', 'nostalgic'],
            'Focus': ['instrumental', 'classical', 'study', 'focus', 'concentration', 'background']
        }
        
    def run_applescript(self, script: str) -> str:
        """Execute AppleScript and return the result"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"AppleScript error: {e.stderr}")
            return ""
    
    def get_all_tracks(self) -> List[Dict]:
        """Get all tracks from Apple Music library"""
        print("Fetching your Apple Music library...")
        
        script = '''
        tell application "Music"
            set trackList to {}
            set allTracks to every track of library playlist 1
            repeat with aTrack in allTracks
                try
                    set trackInfo to {name:name of aTrack, artist:artist of aTrack, album:album of aTrack, genre:genre of aTrack, duration:duration of aTrack, rating:rating of aTrack}
                    set end of trackList to trackInfo
                end try
            end repeat
            return trackList
        end tell
        '''
        
        # Get track count first
        count_script = '''
        tell application "Music"
            return count of tracks of library playlist 1
        end tell
        '''
        
        try:
            count_result = self.run_applescript(count_script)
            track_count = int(count_result) if count_result.isdigit() else 0
            print(f"Found {track_count} tracks in your library")
            
            if track_count == 0:
                print("No tracks found. Make sure Music.app is open and you have tracks in your library.")
                return []
        except:
            print("Could not get track count. Continuing anyway...")
        
        # Get tracks in batches to avoid timeout
        tracks = []
        batch_size = 50
        
        script_template = '''
        tell application "Music"
            set trackList to {}
            set allTracks to tracks {startIndex} thru {endIndex} of library playlist 1
            repeat with aTrack in allTracks
                try
                    set trackInfo to name of aTrack & "|" & artist of aTrack & "|" & album of aTrack & "|" & genre of aTrack & "|" & (duration of aTrack as string) & "|" & (rating of aTrack as string)
                    set end of trackList to trackInfo
                end try
            end repeat
            return trackList
        end tell
        '''
        
        # Try to get all tracks
        full_script = '''
        tell application "Music"
            set trackList to {}
            set allTracks to every track of library playlist 1
            repeat with aTrack in allTracks
                try
                    set trackName to name of aTrack
                    set trackArtist to artist of aTrack
                    set trackAlbum to album of aTrack
                    set trackGenre to genre of aTrack
                    set trackDuration to duration of aTrack
                    set trackRating to rating of aTrack
                    set trackInfo to trackName & "|" & trackArtist & "|" & trackAlbum & "|" & trackGenre & "|" & (trackDuration as string) & "|" & (trackRating as string)
                    set end of trackList to trackInfo
                end try
            end repeat
            return trackList
        end tell
        '''
        
        result = self.run_applescript(full_script)
        
        if not result:
            print("Failed to retrieve tracks. Trying alternative method...")
            return []
        
        # Parse the result
        track_lines = result.split(', ')
        for line in track_lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    tracks.append({
                        'name': parts[0].strip(),
                        'artist': parts[1].strip() if len(parts) > 1 else '',
                        'album': parts[2].strip() if len(parts) > 2 else '',
                        'genre': parts[3].strip() if len(parts) > 3 else '',
                        'duration': parts[4].strip() if len(parts) > 4 else '0',
                        'rating': parts[5].strip() if len(parts) > 5 else '0'
                    })
        
        print(f"Retrieved {len(tracks)} tracks")
        return tracks
    
    def classify_mood(self, track: Dict) -> List[str]:
        """Classify a track's mood based on genre and other metadata"""
        moods = []
        genre = track.get('genre', '').lower()
        name = track.get('name', '').lower()
        artist = track.get('artist', '').lower()
        
        # Check each mood category
        for mood, keywords in self.mood_categories.items():
            for keyword in keywords:
                if keyword in genre or keyword in name or keyword in artist:
                    if mood not in moods:
                        moods.append(mood)
                    break
        
        # If no mood found, try to infer from other factors
        if not moods:
            # Check duration for hints (longer tracks might be chill/ambient)
            try:
                duration = float(track.get('duration', 0))
                if duration > 300:  # > 5 minutes
                    moods.append('Chill')
                elif duration < 180:  # < 3 minutes
                    moods.append('Energetic')
            except:
                pass
            
            # Default to Chill if nothing matches
            if not moods:
                moods.append('Chill')
        
        return moods if moods else ['Chill']
    
    def create_playlist(self, playlist_name: str, track_names: List[str]) -> bool:
        """Create a playlist in Apple Music with the given tracks"""
        if not track_names:
            print(f"Skipping empty playlist: {playlist_name}")
            return False
        
        # Escape quotes in track names
        escaped_tracks = [name.replace('"', '\\"') for name in track_names]
        
        script = f'''
        tell application "Music"
            try
                -- Check if playlist already exists
                set playlistExists to false
                set existingPlaylist to null
                repeat with aPlaylist in playlists
                    if name of aPlaylist is "{playlist_name}" then
                        set playlistExists to true
                        set existingPlaylist to aPlaylist
                        exit repeat
                    end if
                end repeat
                
                if playlistExists then
                    -- Delete existing playlist
                    delete existingPlaylist
                end if
                
                -- Create new playlist
                set newPlaylist to make new playlist with properties {{name:"{playlist_name}"}}
                
                -- Add tracks to playlist
                set addedCount to 0
                repeat with trackName in {{"{"\", \"".join(escaped_tracks[:100])}"}}
                    try
                        set foundTracks to (every track of library playlist 1 whose name is trackName)
                        if (count of foundTracks) > 0 then
                            duplicate (item 1 of foundTracks) to newPlaylist
                            set addedCount to addedCount + 1
                        end if
                    end try
                end repeat
                
                return "Created playlist with " & addedCount & " tracks"
            on error errMsg
                return "Error: " & errMsg
            end try
        end tell
        '''
        
        result = self.run_applescript(script)
        print(f"  {result}")
        return "Error" not in result
    
    def organize_by_mood(self):
        """Main function to organize library by mood"""
        print("=" * 60)
        print("Apple Music Mood-Based Playlist Organizer")
        print("=" * 60)
        
        # Check if Music app is running
        check_script = '''
        tell application "System Events"
            return (name of processes) contains "Music"
        end tell
        '''
        
        is_running = self.run_applescript(check_script)
        if is_running.lower() != 'true':
            print("\n⚠️  Music.app is not running. Please open Music.app first.")
            response = input("Would you like me to try opening it? (y/n): ")
            if response.lower() == 'y':
                subprocess.run(['open', '-a', 'Music'])
                import time
                print("Waiting for Music.app to open...")
                time.sleep(3)
            else:
                print("Please open Music.app and run this script again.")
                return
        
        # Get all tracks
        tracks = self.get_all_tracks()
        
        if not tracks:
            print("No tracks found. Exiting.")
            return
        
        # Classify tracks by mood
        print("\nClassifying tracks by mood...")
        mood_tracks = defaultdict(list)
        
        for track in tracks:
            moods = self.classify_mood(track)
            for mood in moods:
                mood_tracks[mood].append(track['name'])
        
        # Display classification summary
        print("\n" + "=" * 60)
        print("Classification Summary:")
        print("=" * 60)
        for mood, track_list in sorted(mood_tracks.items()):
            print(f"  {mood}: {len(track_list)} tracks")
        
        # Ask for confirmation
        print("\n" + "=" * 60)
        response = input("Create playlists based on these classifications? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        # Create playlists
        print("\nCreating playlists...")
        for mood, track_list in sorted(mood_tracks.items()):
            if track_list:
                print(f"\nCreating playlist: {mood} ({len(track_list)} tracks)")
                # Process in batches if too many tracks
                if len(track_list) > 100:
                    print(f"  Note: Playlist has {len(track_list)} tracks. Creating with first 100 tracks.")
                    self.create_playlist(mood, track_list[:100])
                    # Create additional playlists for remaining tracks
                    for i in range(1, (len(track_list) // 100) + 1):
                        batch_name = f"{mood} (Part {i+1})"
                        batch_tracks = track_list[i*100:(i+1)*100]
                        if batch_tracks:
                            print(f"Creating playlist: {batch_name} ({len(batch_tracks)} tracks)")
                            self.create_playlist(batch_name, batch_tracks)
                else:
                    self.create_playlist(mood, track_list)
        
        print("\n" + "=" * 60)
        print("✅ Done! Check your Music.app for the new playlists.")
        print("=" * 60)

def main():
    organizer = AppleMusicOrganizer()
    organizer.organize_by_mood()

if __name__ == "__main__":
    main()
