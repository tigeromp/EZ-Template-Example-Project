# PROS Code Setup Guide

## ✅ Step 1: Install PROS Extension (Do this now!)

1. In VS Code, click the **Extensions** icon in the left sidebar (or press `Cmd+Shift+X`)
2. Search for **"PROS"** in the search bar
3. Look for **"PROS - VEX V5 Programming"** by Purdue SIGBots
4. Click **"Install"**

## ✅ Step 2: Install PROS CLI (Automatic)

After installing the extension, VS Code will prompt you to install the PROS CLI:
- Click **"Install it now"** when prompted
- Wait for installation to complete

## ✅ Step 3: Build Your Project

Once the extension is installed:

1. Press **`Cmd+Shift+B`** (or go to Terminal → Run Build Task)
2. Select **"PROS: Build Project"** from the dropdown
3. Wait for the build to complete (check the terminal at the bottom)

## ✅ Step 4: Upload to V5 Brain

1. **Make sure your V5 Brain is:**
   - Connected via USB
   - Powered on

2. **Upload the code:**
   - Press **`Cmd+Shift+P`** (Command Palette)
   - Type **"PROS: Upload Project"**
   - Select your brain from the list
   - Wait for upload to complete

## Alternative: Use the PROS Sidebar

1. Click the **PROS icon** in the left sidebar
2. Use the buttons to:
   - Build your project
   - Upload to brain
   - Open terminal

## Troubleshooting

### Extension Not Found?
- Make sure you're searching for "PROS" (not "pros")
- The extension is published by "Purdue SIGBots"

### Build Errors?
- Make sure the PROS CLI is installed
- Check the terminal output for specific errors

### Brain Not Found?
- Check USB connection
- Make sure brain is powered on
- Try unplugging and replugging USB
- Close VEXcode if it's open

### Need Help?
- PROS Documentation: https://pros.cs.purdue.edu/v5/
- PROS Discord: https://discord.gg/purduepros

