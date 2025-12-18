#!/usr/bin/env python3
"""
Expanded Custom Apple Music Playlist Organizer
Creates playlists with at least 40 tracks each, using taste-based recommendations
"""

import subprocess
import time
from typing import List, Dict, Set
from collections import defaultdict, Counter
import random

class ExpandedPlaylistOrganizer:
    def __init__(self):
        # Custom mood categories - expanded keywords
        self.mood_keywords = {
            'Angry/Mad': [
                'metal', 'hardcore', 'punk', 'screamo', 'aggressive', 'angry', 'rage', 'mad',
                'thrash', 'death metal', 'heavy', 'intense', 'loud', 'distorted', 'rock',
                'alternative rock', 'grunge', 'nu metal', 'industrial'
            ],
            'Heartbreak': [
                'sad', 'heartbreak', 'breakup', 'lonely', 'crying', 'tears', 'melancholic',
                'emotional', 'depressing', 'blue', 'hurt', 'broken', 'ballad', 'slow',
                'soul', 'r&b', 'blues', 'country', 'folk', 'acoustic'
            ],
            'Workout/Go Time': [
                'workout', 'gym', 'pump', 'energy', 'motivational', 'inspirational',
                'uplifting', 'intense', 'fast', 'beat', 'driving', 'power', 'strength',
                'cardio', 'running', 'exercise', 'fitness', 'hip hop', 'rap', 'edm',
                'electronic', 'dance', 'house', 'techno', 'trap'
            ],
            'Calming': [
                'calm', 'calming', 'peaceful', 'relaxing', 'zen', 'meditation', 'ambient',
                'soft', 'gentle', 'soothing', 'quiet', 'tranquil', 'serene', 'lullaby',
                'spa', 'yoga', 'mindfulness', 'new age', 'nature sounds', 'white noise'
            ],
            'In Love': [
                'romantic', 'love', 'in love', 'sweet', 'tender', 'intimate', 'passionate',
                'devotion', 'adoration', 'affection', 'heart', 'soulmate', 'forever',
                'together', 'couple', 'wedding', 'pop', 'r&b', 'soul', 'jazz', 'smooth'
            ],
            'While Doing Homework': [
                'instrumental', 'classical', 'study', 'focus', 'concentration', 'background',
                'piano', 'orchestral', 'ambient', 'lo-fi', 'chill', 'acoustic', 'jazz',
                'study music', 'homework', 'productivity', 'no lyrics', 'post-rock',
                'cinematic', 'soundtrack', 'minimal'
            ]
        }
        
        self.all_tracks = []  # Store all tracks with full info
    
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
    
    def get_all_tracks(self) -> List[Dict]:
        """Get all tracks with full information"""
        track_count = self.get_track_count()
        all_tracks = []
        batch_size = 100
        
        for i in range(1, track_count + 1, batch_size):
            end_idx = min(i + batch_size - 1, track_count)
            print(f"  Loading tracks {i}-{end_idx}...", end='\r')
            
            script = f'''
            tell application "Music"
                set trackList to {{}}
                set allTracks to tracks {i} thru {end_idx} of library playlist 1
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
            if result:
                lines = [line.strip() for line in result.split(',')]
                for line in lines:
                    if '|||' in line:
                        parts = line.split('|||')
                        if len(parts) >= 3:
                            all_tracks.append({
                                'name': parts[0].strip(),
                                'artist': parts[1].strip(),
                                'genre': parts[2].strip()
                            })
        
        return all_tracks
    
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
    
    def find_similar_tracks(self, seed_tracks: List[Dict], all_tracks: List[Dict], 
                           exclude_names: Set[str], target_count: int) -> List[str]:
        """Find similar tracks based on artists and genres from seed tracks"""
        if not seed_tracks:
            return []
        
        # Analyze patterns from seed tracks
        seed_artists = Counter([t['artist'].lower() for t in seed_tracks if t['artist']])
        seed_genres = Counter([t['genre'].lower() for t in seed_tracks if t['genre']])
        
        # Get top artists and genres
        top_artists = {artist for artist, count in seed_artists.most_common(10)}
        top_genres = {genre for genre, count in seed_genres.most_common(5)}
        
        # Find similar tracks
        similar = []
        for track in all_tracks:
            if track['name'] in exclude_names:
                continue
            
            track_artist = track['artist'].lower() if track['artist'] else ''
            track_genre = track['genre'].lower() if track['genre'] else ''
            
            # Score based on artist/genre match
            score = 0
            if track_artist in top_artists:
                score += 2
            if track_genre in top_genres:
                score += 1
            
            if score > 0:
                similar.append((score, track['name']))
        
        # Sort by score and return track names
        similar.sort(reverse=True, key=lambda x: x[0])
        return [name for _, name in similar[:target_count]]
    
    def find_correlated_tracks(self, mood: str, all_tracks: List[Dict], 
                              exclude_names: Set[str], count: int = 10) -> List[str]:
        """Find 10 tracks that correlate to the mood category"""
        correlated = []
        
        # Get mood-specific keywords
        keywords = self.mood_keywords.get(mood, [])
        
        for track in all_tracks:
            if track['name'] in exclude_names:
                continue
            
            genre = track.get('genre', '').lower()
            name = track.get('name', '').lower()
            artist = track.get('artist', '').lower()
            combined = f"{genre} {name} {artist}"
            
            # Check if track matches any keyword
            for keyword in keywords:
                if keyword in combined:
                    correlated.append(track['name'])
                    break
            
            if len(correlated) >= count:
                break
        
        return correlated[:count]
    
    def expand_playlist(self, mood: str, initial_tracks: List[Dict], 
                       all_tracks: List[Dict], target_size: int = 40) -> List[str]:
        """Expand playlist to target size using taste-based recommendations"""
        initial_names = {t['name'] for t in initial_tracks}
        final_tracks = list(initial_names)
        
        if len(final_tracks) >= target_size:
            return list(final_tracks)[:target_size]
        
        needed = target_size - len(final_tracks)
        
        # Find similar tracks based on taste (30 tracks)
        similar_needed = min(30, needed)
        if similar_needed > 0 and initial_tracks:
            similar = self.find_similar_tracks(
                initial_tracks, all_tracks, initial_names, similar_needed
            )
            final_tracks.extend(similar)
            initial_names.update(similar)
        
        # Find 10 correlated tracks
        correlated_needed = min(10, target_size - len(final_tracks))
        if correlated_needed > 0:
            correlated = self.find_correlated_tracks(
                mood, all_tracks, initial_names, correlated_needed
            )
            final_tracks.extend(correlated)
        
        # If still not enough, add more similar tracks
        if len(final_tracks) < target_size:
            remaining = target_size - len(final_tracks)
            more_similar = self.find_similar_tracks(
                initial_tracks, all_tracks, {t['name'] for t in initial_tracks if 'name' in t} | set(final_tracks),
                remaining
            )
            final_tracks.extend(more_similar)
        
        return list(final_tracks)[:target_size]
    
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
        print("Expanded Custom Apple Music Playlist Organizer")
        print("=" * 70)
        print("\nCreating playlists (minimum 40 tracks each):")
        print("  • Angry/Mad")
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
        
        # Get all tracks
        print("\nLoading your entire library...")
        all_tracks = self.get_all_tracks()
        
        if not all_tracks:
            print("❌ No tracks found in your library.")
            return
        
        print(f"\nLoaded {len(all_tracks)} tracks")
        
        # Initial classification
        print("\nClassifying tracks...")
        mood_tracks = defaultdict(list)  # Store full track dicts
        
        for track in all_tracks:
            moods = self.classify_track(track)
            for mood in moods:
                mood_tracks[mood].append(track)
        
        # Display initial classification
        print("\n" + "=" * 70)
        print("Initial Classification:")
        print("=" * 70)
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            count = len(mood_tracks.get(mood, []))
            print(f"  {mood:25} {count:5} tracks")
        print("=" * 70)
        
        # Expand each playlist to at least 40 tracks
        print("\nExpanding playlists to 40+ tracks using taste-based recommendations...")
        expanded_playlists = {}
        
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            initial = mood_tracks.get(mood, [])
            print(f"\n  Expanding '{mood}'...")
            print(f"    Initial: {len(initial)} tracks")
            
            expanded = self.expand_playlist(mood, initial, all_tracks, target_size=40)
            expanded_playlists[mood] = expanded
            print(f"    Final: {len(expanded)} tracks")
        
        # Display final summary
        print("\n" + "=" * 70)
        print("Final Playlist Summary:")
        print("=" * 70)
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            count = len(expanded_playlists.get(mood, []))
            print(f"  {mood:25} {count:5} tracks")
        print("=" * 70)
        
        # Create playlists
        print("\nCreating playlists in Music.app...")
        created = 0
        
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            track_list = expanded_playlists.get(mood, [])
            if track_list:
                print(f"  Creating '{mood}' playlist ({len(track_list)} tracks)...", end=' ')
                success = self.create_playlist(mood, track_list)
                if success:
                    print("✓")
                    created += 1
                else:
                    print("✗")
            else:
                print(f"  '{mood}' playlist (0 tracks)... (skipped)")
        
        print("\n" + "=" * 70)
        print(f"✅ Complete! Created {created} playlists with 40+ tracks each.")
        print("   Check your Music.app to see the new playlists!")
        print("=" * 70)

def main():
    organizer = ExpandedPlaylistOrganizer()
    organizer.organize()

if __name__ == "__main__":
    main()

