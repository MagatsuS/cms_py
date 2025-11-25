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

    if not player_url or player_url == 'http://127.0.0.1:8000/player/PLAYER-XXXXXXXX':
        # First time setup - ask user for URL
        print("\n" + "="*70)
        print("  FIRST TIME SETUP - CMS_PY Digital Signage Player")
        print("="*70)
        print("\nPlayer URL not configured in .env file.")
        print("\nPlease enter your player URL from cms_dupe:")
        print("Example: http://127.0.0.1:8000/player/PLAYER-ABC123")
        print()

        player_url = input("Player URL: ").strip()

        if not player_url:
            logger.error("No player URL provided")
            return None

        # Validate URL format
        if not player_url.startswith('http'):
            logger.error("Invalid URL format. Must start with http:// or https://")
            return None

        # Ask if they want to save it
        print()
        save = input("Save this URL to .env file? (y/n): ").strip().lower()
        if save == 'y':
            try:
                env_file = Path('.env')
                if env_file.exists():
                    with open(env_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Replace PLAYER_URL line
                    if 'PLAYER_URL=' in content:
                        # Find and replace the line
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('PLAYER_URL='):
                                lines[i] = f'PLAYER_URL={player_url}'
                                break
                        content = '\n'.join(lines)
                    else:
                        # Add new line
                        content += f'\nPLAYER_URL={player_url}\n'

                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write(content)

                    logger.info("Player URL saved to .env file")
                    print("✓ Configuration saved!")
                else:
                    logger.warning(".env file not found")
            except Exception as e:
                logger.error(f"Failed to save player URL: {str(e)}")

        print()

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
