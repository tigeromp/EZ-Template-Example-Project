# Apple Music Mood-Based Playlist Organizer

This tool automatically organizes your Apple Music library into playlists based on mood!

## 🎵 What It Does

- Scans your entire Apple Music library
- Classifies each track by mood (Happy, Sad, Energetic, Chill, Romantic, etc.)
- Creates playlists automatically in Music.app based on these classifications

## 📋 Requirements

- macOS (with Music.app)
- Python 3 (already installed on your system)
- Apple Music library with tracks

## 🚀 Quick Start

### Option 1: Advanced Script (Recommended)
```bash
python3 apple_music_advanced.py
```

### Option 2: Basic Script
```bash
python3 apple_music_mood_organizer.py
```

## 🎭 Mood Categories

The organizer uses these mood categories:

- **Happy**: Pop, dance, electronic, upbeat music
- **Sad**: Ballads, slow, melancholic, emotional tracks
- **Energetic**: Rock, metal, punk, intense, fast-paced music
- **Chill**: Ambient, lounge, relaxing, calm music
- **Romantic**: Love songs, soft, intimate tracks
- **Motivational**: Inspirational, workout, gym music
- **Nostalgic**: Classic, vintage, retro, oldies
- **Focus**: Instrumental, classical, study music

## 📝 How It Works

1. The script connects to Music.app via AppleScript
2. Reads all tracks from your library
3. Analyzes each track's genre, name, and artist
4. Classifies tracks into mood categories
5. Creates playlists in Music.app for each mood

## ⚠️ Important Notes

- **Music.app must be open** when you run the script
- The script will create new playlists - if playlists with the same names exist, they will be replaced
- Large libraries (>200 tracks per mood) will be split into multiple playlists
- Classification is based on genre/keyword matching - results may vary

## 🔧 Troubleshooting

### "Music.app is not running"
- Open Music.app manually, then run the script again
- The script will try to open it automatically

### "No tracks found"
- Make sure you have tracks in your library playlist
- Check that Music.app has permission to access your library

### Script is slow
- Large libraries (1000+ tracks) may take several minutes
- The advanced script processes in batches to be more efficient

## 🧪 Testing

Test your setup first:
```bash
./test_music_access.sh
```

This will verify:
- Music.app is accessible
- Your library has tracks
- AppleScript permissions are working

## 📊 Your Library Stats

Based on the test, you have **665 tracks** in your library!

## 🎯 Next Steps

1. Run the test script to verify access: `./test_music_access.sh`
2. Run the organizer: `python3 apple_music_advanced.py`
3. Review the classification summary
4. Confirm to create playlists
5. Check Music.app for your new mood-based playlists!

---

**Note**: This tool uses AppleScript to interact with Music.app. It requires no special API keys or authentication - it works directly with your local Music.app library.

