"""
Cache Manager for downloading and managing media files
"""
import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages local cache of media files"""

    def __init__(self, cache_dir: str, max_cache_size_mb: int = 2000):
        self.cache_dir = Path(cache_dir)
        self.max_cache_size = max_cache_size_mb * 1024 * 1024  # Convert to bytes
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index: Dict = {}

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cache index
        self._load_cache_index()

    def _load_cache_index(self):
        """Load cache index from file"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r') as f:
                    self.cache_index = json.load(f)
                logger.info(f"Loaded cache index with {len(self.cache_index)} entries")
            except Exception as e:
                logger.error(f"Failed to load cache index: {str(e)}")
                self.cache_index = {}
        else:
            self.cache_index = {}

    def _save_cache_index(self):
        """Save cache index to file"""
        try:
            with open(self.cache_index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {str(e)}")

    def get_cached_file(self, asset_id: int) -> Optional[str]:
        """Get cached file path if exists"""
        asset_key = str(asset_id)
        if asset_key in self.cache_index:
            file_path = Path(self.cache_index[asset_key]['file_path'])
            if file_path.exists():
                return str(file_path)
            else:
                # File doesn't exist, remove from index
                del self.cache_index[asset_key]
                self._save_cache_index()

        return None

    def cache_asset(self, asset: Dict, file_data: bytes) -> Optional[str]:
        """Cache an asset to local storage"""
        try:
            asset_id = asset['id']
            file_name = asset['name']
            file_type = asset['file_type']

            # Get file extension from name or use default
            ext = Path(file_name).suffix
            if not ext:
                ext = self._get_extension_from_type(file_type)

            # Create sanitized filename
            sanitized_name = self._sanitize_filename(file_name)
            cache_file_name = f"{asset_id}_{sanitized_name}{ext}"
            cache_file_path = self.cache_dir / cache_file_name

            # Write file
            with open(cache_file_path, 'wb') as f:
                f.write(file_data)

            # Update cache index
            self.cache_index[str(asset_id)] = {
                'file_path': str(cache_file_path),
                'file_name': file_name,
                'file_type': file_type,
                'file_size': len(file_data),
                'checksum': hashlib.md5(file_data).hexdigest(),
            }
            self._save_cache_index()

            logger.info(f"Cached asset {asset_id}: {file_name}")
            return str(cache_file_path)

        except Exception as e:
            logger.error(f"Failed to cache asset {asset.get('id')}: {str(e)}")
            return None

    def cache_file_from_url(self, asset: Dict, url: str, api_client) -> Optional[str]:
        """Download and cache file from URL"""
        try:
            # Check if already cached
            cached = self.get_cached_file(asset['id'])
            if cached:
                logger.debug(f"Asset {asset['id']} already cached")
                return cached

            # Check cache size before downloading
            if not self._check_cache_space(asset.get('file_size', 0)):
                logger.warning("Insufficient cache space, cleaning up...")
                self._cleanup_cache()

            # Download to temp location
            temp_file = self.cache_dir / f"temp_{asset['id']}"

            success = api_client.download_file(
                url,
                str(temp_file),
                progress_callback=lambda p: logger.debug(f"Downloading {asset['name']}: {p}%")
            )

            if success and temp_file.exists():
                # Read file data
                with open(temp_file, 'rb') as f:
                    file_data = f.read()

                # Cache the file
                cache_path = self.cache_asset(asset, file_data)

                # Remove temp file
                temp_file.unlink()

                return cache_path
            else:
                if temp_file.exists():
                    temp_file.unlink()
                return None

        except Exception as e:
            logger.error(f"Failed to cache file from URL: {str(e)}")
            return None

    def cache_playlist_assets(self, assets: List[Dict], api_client) -> Dict[int, str]:
        """Cache all assets from a playlist"""
        cached_files = {}

        for asset in assets:
            try:
                file_path = self.cache_file_from_url(
                    asset,
                    asset['file_url'],
                    api_client
                )
                if file_path:
                    cached_files[asset['id']] = file_path
                else:
                    logger.error(f"Failed to cache asset: {asset['name']}")
            except Exception as e:
                logger.error(f"Error caching asset {asset.get('name')}: {str(e)}")

        logger.info(f"Cached {len(cached_files)}/{len(assets)} assets")
        return cached_files

    def get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        for file_info in self.cache_index.values():
            total_size += file_info.get('file_size', 0)
        return total_size

    def _check_cache_space(self, required_size: int) -> bool:
        """Check if there's enough cache space"""
        current_size = self.get_cache_size()
        return (current_size + required_size) < self.max_cache_size

    def _cleanup_cache(self, target_free_space: int = None):
        """Clean up old cache files"""
        if target_free_space is None:
            target_free_space = int(self.max_cache_size * 0.3)  # Free up 30%

        logger.info("Starting cache cleanup...")

        # Simple cleanup: remove random entries until we have space
        # In production, you'd want to implement LRU or similar
        removed_count = 0
        for asset_id in list(self.cache_index.keys()):
            file_info = self.cache_index[asset_id]
            file_path = Path(file_info['file_path'])

            if file_path.exists():
                file_path.unlink()

            del self.cache_index[asset_id]
            removed_count += 1

            if self.get_cache_size() < (self.max_cache_size - target_free_space):
                break

        self._save_cache_index()
        logger.info(f"Cache cleanup complete. Removed {removed_count} files")

    def clear_cache(self):
        """Clear all cached files"""
        for asset_id in list(self.cache_index.keys()):
            file_info = self.cache_index[asset_id]
            file_path = Path(file_info['file_path'])
            if file_path.exists():
                file_path.unlink()

        self.cache_index = {}
        self._save_cache_index()
        logger.info("Cache cleared")

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        return filename[:100]  # Limit length

    @staticmethod
    def _get_extension_from_type(file_type: str) -> str:
        """Get file extension from file type"""
        extensions = {
            'image': '.jpg',
            'video': '.mp4',
            'html': '.html',
        }
        return extensions.get(file_type, '.bin')
