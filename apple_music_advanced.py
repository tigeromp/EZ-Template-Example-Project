#!/usr/bin/env python3
"""
Advanced Apple Music Mood Organizer
Uses improved AppleScript techniques to handle large libraries
"""

import subprocess
import json
import time
from typing import List, Dict
from collections import defaultdict

class AdvancedAppleMusicOrganizer:
    def __init__(self):
        self.mood_keywords = {
            'Happy': ['pop', 'dance', 'electronic', 'upbeat', 'happy', 'party', 'celebration', 'joy', 'fun'],
            'Sad': ['sad', 'ballad', 'slow', 'melancholic', 'emotional', 'depressing', 'blue', 'tears'],
            'Energetic': ['rock', 'metal', 'punk', 'energetic', 'intense', 'aggressive', 'fast', 'hardcore', 'thrash'],
            'Chill': ['chill', 'ambient', 'lounge', 'relaxing', 'calm', 'peaceful', 'meditation', 'zen', 'smooth'],
            'Romantic': ['romantic', 'love', 'soft', 'intimate', 'ballad', 'sweet', 'tender'],
            'Motivational': ['motivational', 'inspirational', 'uplifting', 'workout', 'gym', 'pump', 'energy'],
            'Nostalgic': ['classic', 'vintage', 'retro', 'oldies', 'nostalgic', 'throwback'],
            'Focus': ['instrumental', 'classical', 'study', 'focus', 'concentration', 'background', 'piano', 'orchestral']
        }
    
    def run_applescript(self, script: str) -> str:
        """Execute AppleScript safely"""
        try:
            proc = subprocess.Popen(
                ['osascript', '-e', script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(timeout=60)
            if stderr:
                print(f"Warning: {stderr}")
            return stdout.strip()
        except subprocess.TimeoutExpired:
            proc.kill()
            return ""
        except Exception as e:
            print(f"Error running AppleScript: {e}")
            return ""
    
    def get_track_count(self) -> int:
        """Get total number of tracks"""
        script = 'tell application "Music" to return count of tracks of library playlist 1'
        result = self.run_applescript(script)
        try:
            return int(result) if result else 0
        except:
            return 0
    
    def get_tracks_batch(self, start_idx: int, end_idx: int) -> List[Dict]:
        """Get a batch of tracks"""
        script = f'''
        tell application "Music"
            set trackList to {{}}
            set allTracks to tracks {start_idx} thru {end_idx} of library playlist 1
            repeat with aTrack in allTracks
                try
                    set trackName to name of aTrack
                    set trackArtist to artist of aTrack
                    set trackGenre to genre of aTrack
                    set trackInfo to trackName & "|||" & trackArtist & "|||" & trackGenre
                    set end of trackList to trackInfo
                end try
            end repeat
            return trackList
        end tell
        '''
        
        result = self.run_applescript(script)
        tracks = []
        
        if result:
            # Parse results - AppleScript returns comma-separated list
            lines = [line.strip() for line in result.split(',')]
            for line in lines:
                if '|||' in line:
                    parts = line.split('|||')
                    if len(parts) >= 3:
                        tracks.append({
                            'name': parts[0].strip(),
                            'artist': parts[1].strip(),
                            'genre': parts[2].strip()
                        })
        
        return tracks
    
    def classify_track(self, track: Dict) -> List[str]:
        """Classify track mood"""
        moods = []
        genre = track.get('genre', '').lower()
        name = track.get('name', '').lower()
        artist = track.get('artist', '').lower()
        combined = f"{genre} {name} {artist}"
        
        for mood, keywords in self.mood_keywords.items():
            for keyword in keywords:
                if keyword in combined:
                    if mood not in moods:
                        moods.append(mood)
                    break
        
        return moods if moods else ['Chill']
    
    def create_playlist_script(self, playlist_name: str, track_names: List[str]) -> str:
        """Generate AppleScript to create playlist"""
        # Escape special characters
        safe_name = playlist_name.replace('"', '\\"').replace("'", "\\'")
        
        # Build track matching script
        track_conditions = []
        for track_name in track_names[:200]:  # Limit to 200 tracks per playlist
            safe_track = track_name.replace('"', '\\"').replace("'", "\\'")
            track_conditions.append(f'name is "{safe_track}"')
        
        conditions = ' or '.join(track_conditions)
        
        script = f'''
        tell application "Music"
            try
                -- Delete existing playlist if it exists
                try
                    set existingPlaylist to playlist "{safe_name}"
                    delete existingPlaylist
                end try
                
                -- Create new playlist
                set newPlaylist to make new playlist with properties {{name:"{safe_name}"}}
                
                -- Find and add tracks
                set matchingTracks to (every track of library playlist 1 whose {conditions})
                duplicate matchingTracks to newPlaylist
                
                return "Success: " & (count of tracks of newPlaylist) & " tracks added"
            on error errMsg
                return "Error: " & errMsg
            end try
        end tell
        '''
        
        return script
    
    def organize(self):
        """Main organization function"""
        print("=" * 70)
        print("Advanced Apple Music Mood Organizer")
        print("=" * 70)
        
        # Ensure Music.app is running
        check_script = 'tell application "System Events" to return (name of processes) contains "Music"'
        if self.run_applescript(check_script).lower() != 'true':
            print("\nOpening Music.app...")
            subprocess.run(['open', '-a', 'Music'])
            time.sleep(5)
        
        # Get track count
        print("\nScanning your library...")
        track_count = self.get_track_count()
        
        if track_count == 0:
            print("❌ No tracks found in your library.")
            print("   Make sure you have tracks in Music.app and try again.")
            return
        
        print(f"Found {track_count} tracks")
        
        # Process tracks in batches
        print("\nProcessing tracks...")
        mood_tracks = defaultdict(list)
        batch_size = 100
        
        for i in range(1, track_count + 1, batch_size):
            end_idx = min(i + batch_size - 1, track_count)
            print(f"  Processing tracks {i}-{end_idx}...", end='\r')
            
            tracks = self.get_tracks_batch(i, end_idx)
            for track in tracks:
                moods = self.classify_track(track)
                for mood in moods:
                    mood_tracks[mood].append(track['name'])
        
        print(f"\n  Processed {track_count} tracks")
        
        # Display summary
        print("\n" + "=" * 70)
        print("Mood Classification Summary:")
        print("=" * 70)
        total_classified = 0
        for mood in sorted(mood_tracks.keys()):
            count = len(mood_tracks[mood])
            total_classified += count
            print(f"  {mood:20} {count:5} tracks")
        print(f"  {'Total':20} {total_classified:5} tracks")
        print("=" * 70)
        
        # Confirm (auto-proceed)
        print("\nThis will create playlists in your Music.app.")
        print("Auto-proceeding to create playlists...")
        # response = input("Continue? (y/n): ")
        # if response.lower() != 'y':
        #     print("Cancelled.")
        #     return
        
        # Create playlists
        print("\nCreating playlists...")
        created = 0
        for mood in sorted(mood_tracks.keys()):
            track_list = mood_tracks[mood]
            if track_list:
                print(f"  Creating '{mood}' playlist ({len(track_list)} tracks)...", end=' ')
                
                # Handle large playlists by splitting
                if len(track_list) > 200:
                    # Create main playlist with first 200
                    script = self.create_playlist_script(mood, track_list[:200])
                    result = self.run_applescript(script)
                    
                    # Create additional playlists for remaining tracks
                    for part in range(1, (len(track_list) // 200) + 1):
                        part_name = f"{mood} Part {part + 1}"
                        part_tracks = track_list[part * 200:(part + 1) * 200]
                        if part_tracks:
                            script = self.create_playlist_script(part_name, part_tracks)
                            self.run_applescript(script)
                    
                    print(f"✓ (split into multiple playlists)")
                else:
                    script = self.create_playlist_script(mood, track_list)
                    result = self.run_applescript(script)
                    if "Success" in result:
                        print("✓")
                        created += 1
                    else:
                        print(f"✗ ({result})")
        
        print("\n" + "=" * 70)
        print(f"✅ Complete! Created {created} playlists.")
        print("   Check your Music.app to see the new mood-based playlists!")
        print("=" * 70)

def main():
    organizer = AdvancedAppleMusicOrganizer()
    organizer.organize()

if __name__ == "__main__":
    main()

