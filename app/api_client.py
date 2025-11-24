"""
API Client for communicating with cms_dupe backend
"""
import requests
import logging
from typing import Optional, Dict, Any
import time

logger = logging.getLogger(__name__)


class CMSApiClient:
    """Client for CMS API communication"""

    def __init__(self, api_url: str, player_code: str):
        self.api_url = api_url.rstrip('/')
        self.player_code = player_code
        self.token: Optional[str] = None
        self.player_data: Optional[Dict] = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate with player code and get token"""
        try:
            logger.info(f"Authenticating player with code: {self.player_code}")

            response = self.session.post(
                f"{self.api_url}/player/authenticate",
                json={"code": self.player_code},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data['data']['token']
                    self.player_data = data['data']['player']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}',
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    })
                    logger.info(f"Authentication successful! Player: {self.player_data.get('name')}")
                    return True
                else:
                    logger.error(f"Authentication failed: {data.get('message')}")
                    return False
            else:
                logger.error(f"Authentication failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    def send_heartbeat(self, status: str = "playing", is_tv_on: bool = True) -> Dict[str, Any]:
        """Send heartbeat to server"""
        try:
            response = self.session.post(
                f"{self.api_url}/player/heartbeat",
                json={
                    "status": status,
                    "is_tv_on": is_tv_on,
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.debug("Heartbeat sent successfully")
                    return data['data']
            else:
                logger.warning(f"Heartbeat failed with status {response.status_code}")

        except Exception as e:
            logger.error(f"Heartbeat error: {str(e)}")

        return {}

    def get_playlist(self) -> Optional[Dict[str, Any]]:
        """Get current playlist and assets"""
        try:
            response = self.session.get(
                f"{self.api_url}/player/playlist",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info(f"Playlist retrieved: {data['data']['playlist']['name']}")
                    return data['data']
                else:
                    logger.warning(f"No playlist assigned: {data.get('message')}")
            elif response.status_code == 404:
                logger.warning("No playlist assigned to this player")
            else:
                logger.error(f"Failed to get playlist: {response.status_code}")

        except Exception as e:
            logger.error(f"Get playlist error: {str(e)}")

        return None

    def get_pending_deployments(self) -> list:
        """Check for pending deployments"""
        try:
            response = self.session.get(
                f"{self.api_url}/player/deployments/pending",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('data', [])

        except Exception as e:
            logger.error(f"Get pending deployments error: {str(e)}")

        return []

    def update_deployment_progress(self, deployment_id: int, progress: int, status: str, error_message: Optional[str] = None) -> bool:
        """Update deployment progress"""
        try:
            response = self.session.put(
                f"{self.api_url}/player/deployments/{deployment_id}/progress",
                json={
                    "progress": progress,
                    "status": status,
                    "error_message": error_message,
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)

        except Exception as e:
            logger.error(f"Update deployment progress error: {str(e)}")

        return False

    def report_playback(self, asset_id: int, playlist_id: int, started_at: str, duration_played: int) -> bool:
        """Report playback to server"""
        try:
            response = self.session.post(
                f"{self.api_url}/player/playback/report",
                json={
                    "asset_id": asset_id,
                    "playlist_id": playlist_id,
                    "started_at": started_at,
                    "duration_played": duration_played,
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)

        except Exception as e:
            logger.error(f"Report playback error: {str(e)}")

        return False

    def get_player_info(self) -> Optional[Dict[str, Any]]:
        """Get player information"""
        try:
            response = self.session.get(
                f"{self.api_url}/player/info",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data['data']

        except Exception as e:
            logger.error(f"Get player info error: {str(e)}")

        return None

    def download_file(self, url: str, destination: str, progress_callback=None) -> bool:
        """Download file from URL"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            progress_callback(progress)

            logger.info(f"Downloaded: {url} -> {destination}")
            return True

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return False
