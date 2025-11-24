"""
Main Digital Signage Player Logic
"""
import time
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DigitalSignagePlayer:
    """Main player that manages playlist playback and server communication"""

    def __init__(self, api_client, cache_manager, heartbeat_interval: int = 30):
        self.api_client = api_client
        self.cache_manager = cache_manager
        self.heartbeat_interval = heartbeat_interval

        self.current_playlist: Optional[Dict] = None
        self.current_assets: List[Dict] = []
        self.cached_files: Dict[int, str] = {}
        self.current_asset_index = 0

        self.is_running = False
        self.heartbeat_thread: Optional[threading.Thread] = None

    def start(self):
        """Start the player"""
        self.is_running = True

        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

        # Load initial playlist
        logger.info("Loading playlist from server...")
        self.load_playlist()

        if not self.current_assets:
            logger.warning("No playlist assigned or empty playlist. Waiting for deployment...")
            self._wait_for_playlist()
        else:
            # Cache all assets
            logger.info(f"Caching {len(self.current_assets)} assets...")
            self.cached_files = self.cache_manager.cache_playlist_assets(
                self.current_assets,
                self.api_client
            )

            if not self.cached_files:
                logger.error("Failed to cache any assets!")
                return

            logger.info(f"Successfully cached {len(self.cached_files)} assets")

            # Start playback loop
            self._playback_loop()

    def stop(self):
        """Stop the player"""
        self.is_running = False
        logger.info("Player stopped")

    def load_playlist(self) -> bool:
        """Load playlist from server"""
        try:
            playlist_data = self.api_client.get_playlist()

            if playlist_data:
                self.current_playlist = playlist_data['playlist']
                self.current_assets = playlist_data['assets']
                self.current_asset_index = 0

                logger.info(f"Loaded playlist: {self.current_playlist['name']}")
                logger.info(f"Total assets: {len(self.current_assets)}")
                logger.info(f"Total duration: {self.current_playlist['total_duration']} seconds")

                return True
            else:
                logger.warning("No playlist available")
                return False

        except Exception as e:
            logger.error(f"Failed to load playlist: {str(e)}")
            return False

    def _wait_for_playlist(self):
        """Wait for a playlist to be assigned"""
        logger.info("Waiting for playlist assignment...")

        while self.is_running:
            time.sleep(30)  # Check every 30 seconds

            # Check for pending deployments
            deployments = self.api_client.get_pending_deployments()
            if deployments:
                logger.info(f"Found {len(deployments)} pending deployment(s)")
                # Reload playlist
                if self.load_playlist():
                    logger.info("Playlist loaded! Starting playback...")
                    # Cache assets
                    self.cached_files = self.cache_manager.cache_playlist_assets(
                        self.current_assets,
                        self.api_client
                    )
                    # Start playback
                    self._playback_loop()
                    break

    def _playback_loop(self):
        """Main playback loop"""
        logger.info("Starting playback loop...")

        while self.is_running:
            try:
                # Get current asset
                if not self.current_assets:
                    logger.warning("No assets to play")
                    time.sleep(5)
                    continue

                asset = self.current_assets[self.current_asset_index]
                asset_id = asset['id']

                # Check if asset is cached
                if asset_id not in self.cached_files:
                    logger.warning(f"Asset {asset_id} not in cache, skipping...")
                    self._next_asset()
                    continue

                cached_file = self.cached_files[asset_id]

                # Play asset
                logger.info(f"Playing: {asset['name']} ({asset['file_type']}) - Duration: {asset['duration']}s")

                started_at = datetime.now().isoformat()

                # Display the asset
                self._display_asset(asset, cached_file)

                # Report playback
                self.api_client.report_playback(
                    asset_id=asset_id,
                    playlist_id=self.current_playlist['id'],
                    started_at=started_at,
                    duration_played=asset['duration']
                )

                # Move to next asset
                self._next_asset()

            except Exception as e:
                logger.error(f"Playback error: {str(e)}", exc_info=True)
                time.sleep(5)

    def _display_asset(self, asset: Dict, file_path: str):
        """Display an asset (placeholder - implement actual display logic)"""
        file_type = asset['file_type']
        duration = asset['duration']

        logger.info(f"Displaying {file_type}: {Path(file_path).name}")

        if file_type == 'image':
            # TODO: Display image using PyQt5 or similar
            # For now, just wait for duration
            logger.debug(f"[IMAGE] {asset['name']} - {duration}s")
            time.sleep(duration)

        elif file_type == 'video':
            # TODO: Play video using VLC or similar
            # For now, just wait for duration
            logger.debug(f"[VIDEO] {asset['name']} - {duration}s")
            time.sleep(duration)

        elif file_type == 'html':
            # TODO: Display HTML using WebView
            logger.debug(f"[HTML] {asset['name']} - {duration}s")
            time.sleep(duration)

        else:
            logger.warning(f"Unknown file type: {file_type}")
            time.sleep(5)

    def _next_asset(self):
        """Move to next asset in playlist"""
        self.current_asset_index += 1
        if self.current_asset_index >= len(self.current_assets):
            self.current_asset_index = 0
            logger.debug("Playlist loop completed, starting over")

    def _heartbeat_loop(self):
        """Send periodic heartbeat to server"""
        logger.info(f"Starting heartbeat loop (interval: {self.heartbeat_interval}s)")

        while self.is_running:
            try:
                status = "playing" if self.current_assets else "idle"
                response = self.api_client.send_heartbeat(status=status, is_tv_on=True)

                # Check if playlist was updated
                if response.get('current_playlist_id') != self.current_playlist.get('id') if self.current_playlist else None:
                    logger.info("Playlist updated on server, reloading...")
                    self.load_playlist()
                    # Re-cache assets
                    self.cached_files = self.cache_manager.cache_playlist_assets(
                        self.current_assets,
                        self.api_client
                    )
                    self.current_asset_index = 0

            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")

            # Wait before next heartbeat
            time.sleep(self.heartbeat_interval)
