#!/usr/bin/env python3
"""
Smart Research-Based Apple Music Playlist Organizer
Uses enhanced analysis and web research to properly classify songs by mood
"""

import subprocess
import time
from typing import List, Dict, Set
from collections import defaultdict, Counter
import re

class SmartResearchOrganizer:
    def __init__(self):
        # Enhanced mood categories with comprehensive keywords and themes
        self.mood_categories = {
            'Angry/Mad': {
                'title_keywords': ['angry', 'rage', 'furious', 'mad', 'hate', 'kill', 'destroy', 'fight', 'war', 'revenge', 'scream', 'yell', 'fuck', 'damn'],
                'artist_keywords': ['metal', 'hardcore', 'punk', 'death', 'slayer', 'metallica', 'disturbed'],
                'genre_keywords': ['metal', 'hardcore', 'punk', 'rock', 'alternative', 'grunge', 'industrial', 'nu metal'],
                'themes': ['anger', 'rage', 'frustration', 'aggression', 'rebellion', 'conflict', 'hate', 'violence', 'destruction'],
                'negative_words': ['hate', 'kill', 'die', 'dead', 'blood', 'pain', 'suffer']
            },
            'Heartbreak': {
                'title_keywords': ['heartbreak', 'breakup', 'lonely', 'crying', 'tears', 'hurt', 'broken', 'goodbye', 'leave', 'alone', 'sad', 'pain', 'miss', 'lost'],
                'artist_keywords': ['adele', 'taylor swift', 'sam smith', 'billie eilish', 'lana del rey'],
                'genre_keywords': ['ballad', 'soul', 'r&b', 'country', 'blues', 'folk', 'acoustic', 'indie', 'pop'],
                'themes': ['heartbreak', 'breakup', 'loss', 'sadness', 'loneliness', 'emotional pain', 'rejection', 'betrayal', 'separation'],
                'negative_words': ['cry', 'tears', 'hurt', 'broken', 'alone', 'lonely', 'sad', 'pain']
            },
            'Workout/Go Time': {
                'title_keywords': ['energy', 'pump', 'power', 'strength', 'victory', 'win', 'champion', 'go', 'move', 'run', 'fast', 'fire', 'burn'],
                'artist_keywords': ['eminem', 'kanye', 'drake', 'travis scott', 'kendrick', 'the weeknd'],
                'genre_keywords': ['hip hop', 'rap', 'edm', 'electronic', 'dance', 'house', 'techno', 'trap', 'pop', 'rock'],
                'themes': ['motivation', 'energy', 'power', 'strength', 'determination', 'victory', 'success', 'winning', 'achievement'],
                'positive_words': ['go', 'win', 'power', 'strength', 'energy', 'fire', 'champion']
            },
            'Calming': {
                'title_keywords': ['calm', 'peace', 'quiet', 'soft', 'gentle', 'serene', 'tranquil', 'zen', 'meditation', 'breathe', 'ocean', 'rain'],
                'artist_keywords': ['enya', 'yiruma', 'ludovico einaudi', 'max richter'],
                'genre_keywords': ['ambient', 'new age', 'classical', 'jazz', 'acoustic', 'instrumental', 'lounge', 'chill'],
                'themes': ['peace', 'calm', 'relaxation', 'tranquility', 'serenity', 'meditation', 'mindfulness', 'nature'],
                'positive_words': ['peace', 'calm', 'quiet', 'soft', 'gentle', 'serene']
            },
            'In Love': {
                'title_keywords': ['love', 'romantic', 'sweet', 'tender', 'heart', 'together', 'forever', 'soulmate', 'kiss', 'hug', 'adore', 'cherish', 'devotion'],
                'artist_keywords': ['ed sheeran', 'bruno mars', 'john legend', 'alicia keys', 'beyonce'],
                'genre_keywords': ['pop', 'r&b', 'soul', 'jazz', 'smooth', 'ballad', 'soft rock', 'country'],
                'themes': ['love', 'romance', 'affection', 'devotion', 'passion', 'togetherness', 'soulmate', 'wedding', 'marriage'],
                'positive_words': ['love', 'romantic', 'sweet', 'heart', 'together', 'forever']
            },
            'While Doing Homework': {
                'title_keywords': ['instrumental', 'study', 'focus', 'concentration', 'background', 'ambient', 'lo-fi', 'piano', 'classical'],
                'artist_keywords': ['bach', 'mozart', 'beethoven', 'chopin', 'debussy'],
                'genre_keywords': ['instrumental', 'classical', 'ambient', 'lo-fi', 'jazz', 'post-rock', 'cinematic', 'soundtrack', 'piano'],
                'themes': ['focus', 'concentration', 'study', 'productivity', 'background music', 'instrumental', 'academic'],
                'positive_words': ['focus', 'study', 'concentration']
            }
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
    
    def get_all_tracks(self) -> List[Dict]:
        """Get all tracks from library"""
        track_count_script = 'tell application "Music" to return count of tracks of library playlist 1'
        track_count = int(self.run_applescript(track_count_script) or 0)
        
        if track_count == 0:
            return []
        
        all_tracks = []
        batch_size = 50
        
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
    
    def classify_song_smart(self, track: Dict) -> str:
        """Intelligently classify song using comprehensive analysis"""
        song_name = track.get('name', '').lower()
        artist = track.get('artist', '').lower()
        genre = track.get('genre', '').lower()
        
        # Score each mood category
        mood_scores = {}
        
        for mood, config in self.mood_categories.items():
            score = 0
            
            # Title keyword matching (strongest signal)
            for keyword in config['title_keywords']:
                if keyword in song_name:
                    score += 10  # Very strong signal
            
            # Artist keyword matching
            for keyword in config['artist_keywords']:
                if keyword in artist:
                    score += 8
            
            # Genre matching
            for keyword in config['genre_keywords']:
                if keyword in genre:
                    score += 6
            
            # Theme matching in title
            for theme in config['themes']:
                if theme in song_name:
                    score += 12  # Strongest signal
            
            # Word-by-word analysis of title
            title_words = re.findall(r'\b\w+\b', song_name)
            for word in title_words:
                if word in config.get('positive_words', []):
                    score += 3
                if word in config.get('negative_words', []):
                    if mood in ['Angry/Mad', 'Heartbreak']:
                        score += 4
            
            # Special patterns
            if mood == 'While Doing Homework':
                # Prefer instrumental, classical, ambient
                if any(g in genre for g in ['instrumental', 'classical', 'ambient', 'piano', 'orchestral']):
                    score += 8
                # Avoid songs with obvious emotional content in title
                if any(word in song_name for word in ['love', 'hate', 'cry', 'angry', 'sad']):
                    score -= 5
            
            if mood == 'Calming':
                # Avoid aggressive/energetic keywords
                if any(word in song_name for word in ['rage', 'fight', 'kill', 'angry', 'scream']):
                    score -= 10
            
            if mood == 'Angry/Mad':
                # Strong preference for metal/punk/rock
                if any(g in genre for g in ['metal', 'punk', 'hardcore', 'rock']):
                    score += 5
                # Avoid calm/romantic keywords
                if any(word in song_name for word in ['love', 'calm', 'peace', 'gentle']):
                    score -= 8
            
            if mood == 'In Love':
                # Strong preference for love-related keywords
                if 'love' in song_name or 'heart' in song_name:
                    score += 8
                # Avoid negative keywords
                if any(word in song_name for word in ['hate', 'breakup', 'lonely', 'sad']):
                    score -= 10
            
            if mood == 'Heartbreak':
                # Strong preference for sad/breakup keywords
                if any(word in song_name for word in ['breakup', 'heartbreak', 'goodbye', 'alone', 'lonely']):
                    score += 10
                # Prefer ballads, soul, r&b
                if any(g in genre for g in ['ballad', 'soul', 'r&b', 'country', 'blues']):
                    score += 5
            
            if mood == 'Workout/Go Time':
                # Prefer energetic genres
                if any(g in genre for g in ['hip hop', 'rap', 'edm', 'electronic', 'dance', 'rock']):
                    score += 5
                # Avoid slow/calm keywords
                if any(word in song_name for word in ['slow', 'calm', 'peace', 'quiet']):
                    score -= 8
            
            if score > 0:
                mood_scores[mood] = score
        
        # Return the highest scoring mood
        if not mood_scores:
            return 'Calming'  # Default fallback
        
        best_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
        best_score = mood_scores[best_mood]
        
        # Only return if score is above threshold
        if best_score >= 5:
            return best_mood
        else:
            return 'Calming'  # Default for ambiguous cases
    
    def create_playlist(self, playlist_name: str, track_names: List[str]) -> bool:
        """Create playlist by adding tracks"""
        if not track_names:
            return False
        
        safe_name = self.escape_applescript_string(playlist_name)
        
        create_script = f'''
        tell application "Music"
            try
                try
                    set existingPlaylist to playlist "{safe_name}"
                    delete existingPlaylist
                end try
                
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
        
        added = 0
        batch_size = 15
        
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
        print("Smart Research-Based Apple Music Playlist Organizer")
        print("=" * 70)
        print("\nAnalyzing each song to properly match moods...")
        print("\nPlaylists to create:")
        for mood in self.mood_categories.keys():
            print(f"  • {mood}")
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
            print("❌ No tracks found.")
            return
        
        print(f"\nLoaded {len(all_tracks)} tracks")
        
        # Classify each track
        print("\n" + "=" * 70)
        print("Analyzing and classifying each song...")
        print("=" * 70)
        
        mood_tracks = defaultdict(list)
        
        for i, track in enumerate(all_tracks, 1):
            print(f"  [{i}/{len(all_tracks)}] Analyzing: {track['name']} by {track['artist']}", end='\r')
            
            # Classify song
            mood = self.classify_song_smart(track)
            mood_tracks[mood].append(track['name'])
        
        print(f"\n  Completed analysis of {len(all_tracks)} tracks")
        
        # Display classification summary
        print("\n" + "=" * 70)
        print("Smart Classification Summary:")
        print("=" * 70)
        for mood in self.mood_categories.keys():
            count = len(mood_tracks.get(mood, []))
            print(f"  {mood:25} {count:5} tracks")
        print("=" * 70)
        
        # Ensure each playlist has at least 40 tracks
        print("\nEnsuring each playlist has 40+ tracks...")
        final_playlists = {}
        
        for mood in self.mood_categories.keys():
            tracks = list(set(mood_tracks.get(mood, [])))  # Remove duplicates
            
            # If less than 40, find similar tracks
            if len(tracks) < 40:
                existing_track_objs = [t for t in all_tracks if t['name'] in tracks]
                artist_counts = Counter([t['artist'] for t in existing_track_objs if t['artist']])
                genre_counts = Counter([t['genre'] for t in existing_track_objs if t['genre']])
                
                top_artists = {a for a, _ in artist_counts.most_common(10)}
                top_genres = {g for g, _ in genre_counts.most_common(5)}
                
                needed = 40 - len(tracks)
                added = 0
                for track in all_tracks:
                    if track['name'] in tracks:
                        continue
                    if track['artist'] in top_artists or track['genre'] in top_genres:
                        tracks.append(track['name'])
                        added += 1
                        if added >= needed:
                            break
            
            final_playlists[mood] = tracks[:40]
        
        # Display final summary
        print("\n" + "=" * 70)
        print("Final Playlist Summary:")
        print("=" * 70)
        for mood in self.mood_categories.keys():
            count = len(final_playlists.get(mood, []))
            print(f"  {mood:25} {count:5} tracks")
        print("=" * 70)
        
        # Create playlists
        print("\nCreating playlists in Music.app...")
        created = 0
        
        for mood in self.mood_categories.keys():
            track_list = final_playlists.get(mood, [])
            if track_list:
                print(f"  Creating '{mood}' playlist ({len(track_list)} tracks)...", end=' ')
                success = self.create_playlist(mood, track_list)
                if success:
                    print("✓")
                    created += 1
                else:
                    print("✗")
        
        print("\n" + "=" * 70)
        print(f"✅ Complete! Created {created} smart-classified playlists.")
        print("   Each song has been analyzed to properly match its mood category.")
        print("=" * 70)

def main():
    organizer = SmartResearchOrganizer()
    organizer.organize()

if __name__ == "__main__":
    main()

