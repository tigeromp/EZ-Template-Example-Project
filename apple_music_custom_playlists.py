#!/usr/bin/env python3
"""
Custom Apple Music Playlist Organizer
Creates specific playlists: Angry, Heartbreak, Workout/Go Time, Calming, In Love, While Doing Homework
"""

import subprocess
import time
from typing import List, Dict
from collections import defaultdict

class CustomPlaylistOrganizer:
    def __init__(self):
        # Custom mood categories based on user request
        self.mood_keywords = {
            'Angry': [
                'metal', 'hardcore', 'punk', 'screamo', 'aggressive', 'angry', 'rage',
                'thrash', 'death metal', 'heavy', 'intense', 'loud', 'distorted'
            ],
            'Heartbreak': [
                'sad', 'heartbreak', 'breakup', 'lonely', 'crying', 'tears', 'melancholic',
                'emotional', 'depressing', 'blue', 'hurt', 'broken', 'ballad', 'slow'
            ],
            'Workout/Go Time': [
                'workout', 'gym', 'pump', 'energy', 'motivational', 'inspirational',
                'uplifting', 'intense', 'fast', 'beat', 'driving', 'power', 'strength',
                'cardio', 'running', 'exercise', 'fitness'
            ],
            'Calming': [
                'calm', 'calming', 'peaceful', 'relaxing', 'zen', 'meditation', 'ambient',
                'soft', 'gentle', 'soothing', 'quiet', 'tranquil', 'serene', 'lullaby',
                'spa', 'yoga', 'mindfulness'
            ],
            'In Love': [
                'romantic', 'love', 'in love', 'sweet', 'tender', 'intimate', 'passionate',
                'devotion', 'adoration', 'affection', 'heart', 'soulmate', 'forever',
                'together', 'couple', 'wedding'
            ],
            'While Doing Homework': [
                'instrumental', 'classical', 'study', 'focus', 'concentration', 'background',
                'piano', 'orchestral', 'ambient', 'lo-fi', 'chill', 'acoustic', 'jazz',
                'study music', 'homework', 'productivity', 'no lyrics'
            ]
        }
    
    def escape_applescript_string(self, text: str) -> str:
        """Escape special characters for AppleScript"""
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        return text
    
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
            return stdout.strip()
        except subprocess.TimeoutExpired:
            proc.kill()
            return ""
        except Exception as e:
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
        """Classify track into custom mood categories"""
        moods = []
        genre = track.get('genre', '').lower()
        name = track.get('name', '').lower()
        artist = track.get('artist', '').lower()
        combined = f"{genre} {name} {artist}"
        
        # Check each mood category
        for mood, keywords in self.mood_keywords.items():
            for keyword in keywords:
                if keyword in combined:
                    if mood not in moods:
                        moods.append(mood)
                    break
        
        return moods
    
    def create_playlist(self, playlist_name: str, track_names: List[str]) -> bool:
        """Create playlist by adding tracks"""
        if not track_names:
            return False
        
        safe_name = self.escape_applescript_string(playlist_name)
        
        # Create playlist first
        create_script = f'''
        tell application "Music"
            try
                -- Delete existing playlist if it exists
                try
                    set existingPlaylist to playlist "{safe_name}"
                    delete existingPlaylist
                end try
                
                -- Create new playlist
                set newPlaylist to make new playlist with properties {{name:"{safe_name}"}}
                return "created"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        result = self.run_applescript(create_script)
        if "error" in result.lower():
            return False
        
        # Add tracks in batches
        added = 0
        batch_size = 20
        
        for i in range(0, len(track_names), batch_size):
            batch = track_names[i:i+batch_size]
            
            add_commands = []
            for track_name in batch:
                safe_track = self.escape_applescript_string(track_name)
                add_commands.append(f'''
                try
                    set foundTracks to (every track of library playlist 1 whose name is "{safe_track}")
                    if (count of foundTracks) > 0 then
                        set trackToAdd to item 1 of foundTracks
                        try
                            duplicate trackToAdd to playlist "{safe_name}"
                            set added to added + 1
                        end try
                    end if
                end try
                ''')
            
            add_script = f'''
            tell application "Music"
                set added to 0
                {''.join(add_commands)}
                return added
            end tell
            '''
            
            result = self.run_applescript(add_script)
            try:
                batch_added = int(result) if result.isdigit() else 0
                added += batch_added
            except:
                pass
        
        return added > 0
    
    def organize(self):
        """Main organization function"""
        print("=" * 70)
        print("Custom Apple Music Playlist Organizer")
        print("=" * 70)
        print("\nCreating playlists:")
        print("  • Angry")
        print("  • Heartbreak")
        print("  • Workout/Go Time")
        print("  • Calming")
        print("  • In Love")
        print("  • While Doing Homework")
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
            return
        
        print(f"Found {track_count} tracks")
        
        # Process tracks in batches
        print("\nProcessing and classifying tracks...")
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
        print("Playlist Classification Summary:")
        print("=" * 70)
        total_classified = 0
        for mood in ['Angry', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            count = len(mood_tracks.get(mood, []))
            total_classified += count
            print(f"  {mood:25} {count:5} tracks")
        print(f"  {'Total':25} {total_classified:5} tracks")
        print("=" * 70)
        
        print("\nCreating playlists...")
        created = 0
        
        for mood in ['Angry', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            track_list = mood_tracks.get(mood, [])
            if track_list:
                print(f"  Creating '{mood}' playlist ({len(track_list)} tracks)...", end=' ')
                
                # Handle large playlists by splitting
                if len(track_list) > 200:
                    # Create main playlist
                    success = self.create_playlist(mood, track_list[:200])
                    if success:
                        print("✓")
                        created += 1
                    
                    # Create additional playlists for remaining tracks
                    for part in range(1, (len(track_list) // 200) + 1):
                        part_name = f"{mood} Part {part + 1}"
                        part_tracks = track_list[part * 200:(part + 1) * 200]
                        if part_tracks:
                            success = self.create_playlist(part_name, part_tracks)
                            if success:
                                print(f"  Created '{part_name}' ({len(part_tracks)} tracks) ✓")
                                created += 1
                else:
                    success = self.create_playlist(mood, track_list)
                    if success:
                        print("✓")
                        created += 1
                    else:
                        print("✗")
            else:
                print(f"  '{mood}' playlist (0 tracks)... (skipped)")
        
        print("\n" + "=" * 70)
        print(f"✅ Complete! Created {created} playlists.")
        print("   Check your Music.app to see the new playlists!")
        print("=" * 70)

def main():
    organizer = CustomPlaylistOrganizer()
    organizer.organize()

if __name__ == "__main__":
    main()

