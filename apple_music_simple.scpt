-- Simple AppleScript to get track information from Music.app
tell application "Music"
	set trackCount to count of tracks of library playlist 1
	return trackCount
end tell

