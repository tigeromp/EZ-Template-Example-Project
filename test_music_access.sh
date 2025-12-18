#!/bin/bash
# Test script to check Apple Music access

echo "Testing Apple Music access..."
echo ""

# Check if Music app is running
echo "1. Checking if Music.app is running..."
if pgrep -x "Music" > /dev/null; then
    echo "   ✅ Music.app is running"
else
    echo "   ❌ Music.app is not running"
    echo "   Opening Music.app..."
    open -a Music
    sleep 3
fi

echo ""
echo "2. Testing AppleScript access..."
osascript -e 'tell application "Music" to get count of tracks of library playlist 1'

echo ""
echo "3. Getting sample track info..."
osascript -e 'tell application "Music"
    if (count of tracks of library playlist 1) > 0 then
        set firstTrack to track 1 of library playlist 1
        return name of firstTrack & " by " & artist of firstTrack
    else
        return "No tracks found"
    end if
end tell'

echo ""
echo "Done!"

