#!/usr/bin/env python3
"""
Browser-Based Digital Signage Player
Opens the cms_dupe web player in fullscreen kiosk mode
"""

import os
import sys
import platform
import subprocess
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_player_url():
    """Get player URL from environment or user input"""
    player_url = os.getenv('PLAYER_URL', '')

    if not player_url:
        # Construct from parts
        cms_url = os.getenv('CMS_URL', 'http://127.0.0.1:8000')
        player_code = os.getenv('PLAYER_CODE', 'PLAYER-PJHZJN')
        player_url = f"{cms_url}/player/{player_code}"

    return player_url


def open_browser_kiosk(url):
    """Open browser in kiosk/fullscreen mode"""
    system = platform.system()

    logger.info(f"Opening player in fullscreen: {url}")
    logger.info(f"Platform: {system}")

    try:
        if system == "Windows":
            # Windows - Try Chrome, then Edge, then default browser
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]

            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]

            # Try Chrome first
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    logger.info(f"Opening with Chrome in kiosk mode: {chrome_path}")
                    subprocess.Popen([
                        chrome_path,
                        "--kiosk",
                        "--disable-infobars",
                        "--noerrdialogs",
                        "--disable-session-crashed-bubble",
                        "--disable-restore-session-state",
                        "--start-fullscreen",
                        "--app=" + url
                    ])
                    logger.info("Chrome opened! Browser should be in fullscreen kiosk mode.")
                    return True

            # Try Edge
            for edge_path in edge_paths:
                if os.path.exists(edge_path):
                    logger.info(f"Opening with Edge in kiosk mode: {edge_path}")
                    subprocess.Popen([
                        edge_path,
                        "--kiosk",
                        "--disable-infobars",
                        "--start-fullscreen",
                        url
                    ])
                    logger.info("Edge opened! Browser should be in fullscreen kiosk mode.")
                    return True

            # Fallback to default browser (not fullscreen)
            logger.warning("Chrome/Edge not found, opening with default browser (NOT fullscreen)")
            logger.warning("Please press F11 to enter fullscreen mode manually")
            os.system(f'start {url}')
            return True

        elif system == "Linux":
            # Raspberry Pi / Linux - Try Chromium, then Firefox
            browsers = [
                # Chromium (most common on Raspberry Pi)
                ["chromium-browser", "--kiosk", "--noerrdialogs", "--disable-infobars",
                 "--disable-session-crashed-bubble", "--check-for-update-interval=31536000", url],
                ["chromium", "--kiosk", "--noerrdialogs", url],
                # Firefox
                ["firefox", "--kiosk", url],
                # Fallback
                ["x-www-browser", url],
            ]

            for browser_cmd in browsers:
                try:
                    logger.info(f"Trying: {browser_cmd[0]}")
                    subprocess.Popen(browser_cmd)
                    logger.info(f"Successfully opened with {browser_cmd[0]}")
                    return True
                except FileNotFoundError:
                    continue

            logger.error("No suitable browser found!")
            return False

        elif system == "Darwin":  # macOS
            # macOS - Try Chrome, then Safari
            try:
                subprocess.Popen([
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--kiosk",
                    url
                ])
                return True
            except:
                # Fallback to default browser
                os.system(f'open {url}')
                return True

        else:
            logger.error(f"Unsupported platform: {system}")
            return False

    except Exception as e:
        logger.error(f"Failed to open browser: {str(e)}")
        return False


def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("  CMS_PY - Browser-Based Digital Signage Player")
    logger.info("="*60)
    logger.info("")

    # Get player URL
    player_url = get_player_url()

    logger.info(f"Player URL: {player_url}")
    logger.info("")

    # Confirm before opening
    print(f"This will open the player in fullscreen kiosk mode:")
    print(f"  {player_url}")
    print("")
    print("Press ENTER to start, or Ctrl+C to cancel...")

    try:
        input()
    except KeyboardInterrupt:
        logger.info("Cancelled by user")
        return 0

    # Open browser
    success = open_browser_kiosk(player_url)

    if success:
        logger.info("Player started successfully!")

        # Auto-press F11 to ensure fullscreen (fallback)
        if HAS_PYAUTOGUI:
            logger.info("Waiting 3 seconds for browser to load...")
            time.sleep(3)
            logger.info("Pressing F11 to enter fullscreen...")
            pyautogui.press('f11')
            logger.info("Fullscreen activated!")
        else:
            logger.warning("pyautogui not installed - cannot auto-press F11")
            logger.warning("Please press F11 manually to enter fullscreen")

        logger.info("")
        logger.info("To exit fullscreen:")
        logger.info("  - Windows: Press F11 or Alt+F4")
        logger.info("  - Linux: Press F11 or Alt+F4")
        logger.info("  - Mac: Press Cmd+Q")
        logger.info("")
        return 0
    else:
        logger.error("Failed to start player")
        return 1


if __name__ == '__main__':
    sys.exit(main())
