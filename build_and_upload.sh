#!/bin/bash

# Automated Build and Upload Script for VEX V5
# This script uses the PROS toolchain installed by the VS Code extension

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== VEX V5 Build and Upload Script ===${NC}\n"

# Find PROS toolchain
PROS_TOOLCHAIN="$HOME/Library/Application Support/Code/User/globalStorage/sigbots.pros/install/pros-toolchain-macos"

if [ ! -d "$PROS_TOOLCHAIN" ]; then
    echo -e "${RED}Error: PROS toolchain not found!${NC}"
    echo "Please install the PROS extension in VS Code first."
    exit 1
fi

echo -e "${YELLOW}Using PROS toolchain: $PROS_TOOLCHAIN${NC}\n"

# Add PROS toolchain to PATH
export PATH="$PROS_TOOLCHAIN/bin:$PATH"

# Get project directory (script location)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${GREEN}Step 1: Building project...${NC}"
if ~/Library/Python/3.13/bin/pros make; then
    echo -e "${GREEN}✓ Build successful!${NC}\n"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

# Check if brain is connected
echo -e "${GREEN}Step 2: Checking for V5 Brain...${NC}"
BRAIN_PORT=$(ls /dev/tty.usbmodem* 2>/dev/null | head -1)
CU_PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)

if [ -z "$BRAIN_PORT" ] && [ -z "$CU_PORT" ]; then
    echo -e "${RED}✗ No V5 Brain detected!${NC}"
    echo "Please connect your V5 Brain via USB and power it on."
    exit 1
fi

if [ -n "$CU_PORT" ]; then
    echo -e "${GREEN}✓ Brain found at: $CU_PORT${NC}\n"
else
    echo -e "${GREEN}✓ Brain found at: $BRAIN_PORT${NC}\n"
fi

# Upload to brain with retry
echo -e "${GREEN}Step 3: Uploading to V5 Brain...${NC}"
echo -e "${YELLOW}Note: Make sure VEXcode and other VEX programs are closed!${NC}\n"

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if ~/Library/Python/3.13/bin/pros upload --slot 1; then
        echo -e "\n${GREEN}✓✓✓ Upload successful! ✓✓✓${NC}"
        echo -e "${GREEN}Your code is now on the V5 Brain!${NC}"
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}Upload failed. Retrying in 2 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
            sleep 2
        fi
    fi
done

echo -e "${RED}✗ Upload failed after $MAX_RETRIES attempts!${NC}"
echo "Make sure:"
echo "  - Brain is powered on"
echo "  - USB cable is connected"
echo "  - Close VEXcode, VS Code PROS terminal, or any other program using the brain"
echo "  - Try unplugging and replugging the USB cable"
exit 1

