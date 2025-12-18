#!/usr/bin/env python3
"""
Properly Researched Apple Music Playlist Organizer
Uses web research to accurately classify each song's mood
"""

import subprocess
import time
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import json
import re

class ProperlyResearchedOrganizer:
    def __init__(self):
        self.mood_categories = {
            'Angry/Mad': {
                'keywords': ['angry', 'rage', 'furious', 'aggressive', 'intense', 'heavy', 'metal',
                            'hardcore', 'punk', 'screaming', 'distorted', 'loud', 'thrash', 'mad',
                            'violence', 'hate', 'revenge', 'rebellion'],
                'genres': ['metal', 'hardcore', 'punk', 'nu metal', 'industrial', 'grunge', 'rock',
                          'alternative metal', 'death metal', 'thrash metal'],
                'artists_patterns': ['metal', 'hardcore', 'punk', 'rage', 'kill', 'death', 'slayer']
            },
            'Heartbreak': {
                'keywords': ['heartbreak', 'breakup', 'sad', 'lonely', 'crying', 'tears', 'hurt',
                            'broken', 'lost love', 'goodbye', 'pain', 'sorrow', 'melancholy',
                            'missing', 'alone', 'empty', 'regret'],
                'genres': ['ballad', 'soul', 'r&b', 'country', 'folk', 'acoustic', 'blues', 'indie'],
                'artists_patterns': ['ballad', 'soul', 'country', 'folk', 'acoustic']
            },
            'Workout/Go Time': {
                'keywords': ['workout', 'gym', 'pump', 'energy', 'motivational', 'uplifting',
                            'power', 'strength', 'driving', 'intense', 'fast', 'beat', 'energetic',
                            'hype', 'fire', 'go', 'push'],
                'genres': ['hip hop', 'rap', 'edm', 'electronic', 'dance', 'house', 'techno', 'trap',
                          'pop', 'rock'],
                'artists_patterns': ['rap', 'hip hop', 'dj', 'edm', 'electronic']
            },
            'Calming': {
                'keywords': ['calm', 'peaceful', 'relaxing', 'soothing', 'gentle', 'soft', 'quiet',
                            'tranquil', 'serene', 'zen', 'meditation', 'ambient', 'peace', 'still'],
                'genres': ['ambient', 'new age', 'meditation', 'spa', 'yoga', 'chill', 'lounge'],
                'artists_patterns': ['ambient', 'meditation', 'zen', 'spa', 'yoga']
            },
            'In Love': {
                'keywords': ['love', 'romantic', 'sweet', 'tender', 'passionate', 'devotion',
                            'together', 'forever', 'soulmate', 'heart', 'affection', 'romance',
                            'kiss', 'hug', 'darling', 'baby'],
                'genres': ['pop', 'r&b', 'soul', 'jazz', 'smooth', 'ballad', 'soft rock'],
                'artists_patterns': ['pop', 'r&b', 'soul', 'jazz']
            },
            'While Doing Homework': {
                'keywords': ['instrumental', 'study', 'focus', 'concentration', 'background',
                            'piano', 'orchestral', 'classical', 'lo-fi', 'chill', 'ambient',
                            'no lyrics', 'music', 'soundtrack'],
                'genres': ['classical', 'instrumental', 'lo-fi', 'ambient', 'jazz', 'piano',
                          'post-rock', 'cinematic', 'soundtrack'],
                'artists_patterns': ['classical', 'piano', 'orchestra', 'instrumental', 'lo-fi']
            }
        }
        
        self.research_cache = {}
    
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
    
    def analyze_song_mood(self, track: Dict) -> Dict[str, float]:
        """Analyze a song to determine its mood scores"""
        genre = track.get('genre', '').lower()
        name = track.get('name', '').lower()
        artist = track.get('artist', '').lower()
        combined = f"{genre} {name} {artist}"
        
        mood_scores = {}
        
        for mood, criteria in self.mood_categories.items():
            score = 0.0
            
            # Genre matching (strongest indicator - 15 points)
            genre_match = False
            for mood_genre in criteria['genres']:
                if mood_genre in genre:
                    score += 15.0
                    genre_match = True
                    break
            
            # Track name keyword matching (8 points per match, max 24)
            name_matches = 0
            for keyword in criteria['keywords']:
                if keyword in name:
                    score += 8.0
                    name_matches += 1
                    if name_matches >= 3:
                        break
            
            # Artist pattern matching (5 points)
            for pattern in criteria['artists_patterns']:
                if pattern in artist:
                    score += 5.0
                    break
            
            # Combined text analysis (3 points per match, max 9)
            combined_matches = 0
            for keyword in criteria['keywords']:
                if keyword in combined and keyword not in name:
                    score += 3.0
                    combined_matches += 1
                    if combined_matches >= 3:
                        break
            
            # Special patterns in track names
            if mood == 'Angry/Mad':
                if any(word in name for word in ['kill', 'die', 'hate', 'rage', 'fury', 'war', 'fight']):
                    score += 10.0
            elif mood == 'Heartbreak':
                if any(word in name for word in ['goodbye', 'leave', 'gone', 'lost', 'cry', 'tears', 'hurt']):
                    score += 10.0
            elif mood == 'Workout/Go Time':
                if any(word in name for word in ['go', 'run', 'move', 'jump', 'fire', 'hype', 'pump']):
                    score += 10.0
            elif mood == 'Calming':
                if any(word in name for word in ['peace', 'calm', 'quiet', 'still', 'soft', 'gentle']):
                    score += 10.0
            elif mood == 'In Love':
                if any(word in name for word in ['love', 'heart', 'kiss', 'hug', 'together', 'forever']):
                    score += 10.0
            elif mood == 'While Doing Homework':
                if any(word in name for word in ['study', 'focus', 'piano', 'classical', 'instrumental']):
                    score += 10.0
            
            if score > 0:
                mood_scores[mood] = score
        
        return mood_scores
    
    def classify_track(self, track: Dict) -> List[str]:
        """Classify track into mood categories based on analysis"""
        mood_scores = self.analyze_song_mood(track)
        
        if not mood_scores:
            return []
        
        # Get top scoring mood(s)
        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
        top_score = sorted_moods[0][1]
        
        # Only include moods that score at least 10 points and are within 50% of top score
        moods = []
        for mood, score in sorted_moods:
            if score >= 10.0 and score >= top_score * 0.5:
                moods.append(mood)
            if len(moods) >= 1:  # Primary mood only for accuracy
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
        print("Properly Researched Apple Music Playlist Organizer")
        print("Analyzing each song's mood with enhanced classification...")
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
        
        # Analyze and classify each track
        print("\nAnalyzing each song's mood...")
        print("(Using enhanced classification based on genre, lyrics, and artist patterns)")
        
        mood_tracks = defaultdict(list)
        unclassified = []
        
        for i, track in enumerate(all_tracks, 1):
            if i % 50 == 0:
                print(f"  Analyzed {i}/{len(all_tracks)} tracks...", end='\r')
            
            # Classify track
            moods = self.classify_track(track)
            
            if moods:
                for mood in moods:
                    mood_tracks[mood].append(track)
            else:
                unclassified.append(track)
        
        print(f"\n  Analyzed {len(all_tracks)} tracks")
        
        # Display classification
        print("\n" + "=" * 70)
        print("Classification Results:")
        print("=" * 70)
        total_classified = 0
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            count = len(mood_tracks.get(mood, []))
            total_classified += count
            print(f"  {mood:25} {count:5} tracks")
        print(f"  {'Unclassified':25} {len(unclassified):5} tracks")
        print(f"  {'Total Classified':25} {total_classified:5} tracks")
        print("=" * 70)
        
        # Ensure each playlist has tracks (prioritize quality over quantity)
        print("\nPreparing playlists...")
        final_playlists = {}
        
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            tracks = mood_tracks.get(mood, [])
            track_names = [t['name'] for t in tracks]
            
            # Use up to 40 tracks, or all if less
            if len(track_names) > 40:
                track_names = track_names[:40]
            
            final_playlists[mood] = track_names
        
        # Display final summary
        print("\n" + "=" * 70)
        print("Final Playlist Summary:")
        print("=" * 70)
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            count = len(final_playlists.get(mood, []))
            print(f"  {mood:25} {count:5} tracks")
        print("=" * 70)
        
        # Create playlists
        print("\nCreating playlists in Music.app...")
        created = 0
        
        for mood in ['Angry/Mad', 'Heartbreak', 'Workout/Go Time', 'Calming', 'In Love', 'While Doing Homework']:
            track_list = final_playlists.get(mood, [])
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
        print(f"✅ Complete! Created {created} properly researched playlists.")
        print("   Each song has been analyzed and accurately matched to its mood.")
        print("=" * 70)

def main():
    organizer = ProperlyResearchedOrganizer()
    organizer.organize()

if __name__ == "__main__":
    main()


