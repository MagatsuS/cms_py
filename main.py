#!/usr/bin/env python3
"""
CMS_PY - Raspberry Pi Digital Signage Player
Connects to cms_dupe backend and displays content on TV screen
"""

import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('storage/logs/player.log')
    ]
)

logger = logging.getLogger(__name__)

# Import app modules
from app.api_client import CMSApiClient
from app.cache_manager import CacheManager
from app.player import DigitalSignagePlayer


def get_player_code():
    """Get player code from environment or user input"""
    player_code = os.getenv('PLAYER_CODE', '')

    if not player_code or player_code == 'PLR-XXXXXXXX':
        print("\n" + "="*60)
        print("  CMS_PY - Digital Signage Player")
        print("="*60)
        print("\nPlayer code not configured in .env file.")
        print("\nPlease enter your player code from cms_dupe:")
        print("(Format: PLR-XXXXXXXX)")
        print()

        player_code = input("Player Code: ").strip().upper()

        if not player_code:
            logger.error("No player code provided")
            return None

        if not player_code.startswith('PLR-'):
            logger.error("Invalid player code format. Must start with 'PLR-'")
            return None

        # Ask if they want to save it
        save = input("\nSave this player code to .env file? (y/n): ").strip().lower()
        if save == 'y':
            try:
                env_file = Path('.env')
                if env_file.exists():
                    with open(env_file, 'r') as f:
                        content = f.read()

                    # Replace PLAYER_CODE line
                    if 'PLAYER_CODE=' in content:
                        content = content.replace(
                            'PLAYER_CODE=PLR-XXXXXXXX',
                            f'PLAYER_CODE={player_code}'
                        )
                    else:
                        content += f'\nPLAYER_CODE={player_code}\n'

                    with open(env_file, 'w') as f:
                        f.write(content)

                    logger.info("Player code saved to .env file")
                else:
                    logger.warning(".env file not found")
            except Exception as e:
                logger.error(f"Failed to save player code: {str(e)}")

    return player_code


def main():
    """Main entry point"""
    try:
        # Create required directories
        Path('storage/cache').mkdir(parents=True, exist_ok=True)
        Path('storage/logs').mkdir(parents=True, exist_ok=True)

        logger.info("Starting CMS_PY Digital Signage Player")

        # Get configuration
        api_url = os.getenv('CMS_API_URL', 'http://localhost/cms_dupe/public/api/v1')
        player_code = get_player_code()

        if not player_code:
            logger.error("Cannot start without player code")
            return 1

        cache_dir = os.getenv('CACHE_DIR', 'storage/cache')
        max_cache_size = int(os.getenv('MAX_CACHE_SIZE_MB', '2000'))
        heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', '30'))

        # Initialize components
        logger.info(f"Connecting to CMS API: {api_url}")
        logger.info(f"Player Code: {player_code}")

        api_client = CMSApiClient(api_url, player_code)
        cache_manager = CacheManager(cache_dir, max_cache_size)

        # Authenticate
        logger.info("Authenticating with CMS...")
        if not api_client.authenticate():
            logger.error("Authentication failed! Check your player code and CMS API URL")
            return 1

        logger.info(f"Successfully authenticated! Player: {api_client.player_data.get('name')}")
        logger.info(f"Location: {api_client.player_data.get('location', 'Not set')}")

        # Create and start player
        player = DigitalSignagePlayer(
            api_client=api_client,
            cache_manager=cache_manager,
            heartbeat_interval=heartbeat_interval,
        )

        logger.info("Starting player...")
        player.start()

        return 0

    except KeyboardInterrupt:
        logger.info("Player stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
